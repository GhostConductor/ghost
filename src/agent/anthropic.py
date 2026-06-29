import logging
from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk import AssistantMessage, ResultMessage
from .base import BaseAgent

# Phrases in ResultMessage.result that indicate a hard failure
ERROR_INDICATORS = [
    "invalid api key",
    "authentication_error",
    "invalid x-api-key",
    "permission denied",
    "rate limit",
]


class AnthropicAgent(BaseAgent):
    """Claude Agent SDK implementation of BaseAgent."""

    async def run(self, task: str, context: str, memory: str | None = None) -> tuple[str, dict]:
        prompt = self._build_prompt(task, context, memory)
        summary = []
        usage = {}

        self.logger.info(f"Starting agent loop — model={self.model} max_turns={self.max_turns} timeout={self.timeout}s")

        options = ClaudeAgentOptions(
            model=self.model,
            system_prompt=self.system_prompt,
            allowed_tools=["Read", "Edit", "Bash", "Glob"],
            permission_mode="acceptEdits",
            max_turns=self.max_turns,
            cwd="/code",
        )

        try:
            async for message in query(prompt=prompt, options=options):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if hasattr(block, "text"):
                            self.logger.info(f"agent: {block.text}")
                            summary.append(block.text)
                elif isinstance(message, ResultMessage):
                    self.logger.info(f"result: {message.result}")
                    if message.result:
                        lower = message.result.lower()
                        for indicator in ERROR_INDICATORS:
                            if indicator in lower:
                                raise RuntimeError(f"Agent API error: {message.result}")
                        summary.append(message.result)
                    if message.usage:
                        usage = {
                            "input_tokens": message.usage.get("input_tokens", 0),
                            "output_tokens": message.usage.get("output_tokens", 0),
                            "cache_creation_input_tokens": message.usage.get("cache_creation_input_tokens", 0),
                            "cache_read_input_tokens": message.usage.get("cache_read_input_tokens", 0),
                            "total_cost_usd": message.total_cost_usd if hasattr(message, "total_cost_usd") else None,
                        }
                        self.logger.info(f"usage: input={usage['input_tokens']} output={usage['output_tokens']} cost=${usage['total_cost_usd']}")
        except RuntimeError:
            raise
        except Exception as e:
            if "error result: success" in str(e):
                self.logger.warning(f"SDK threw on success result (known bug) — treating as complete: {e}")
            else:
                raise

        return "\n".join(summary), usage

    def _build_prompt(self, task: str, context: str, memory: str | None = None) -> str:
        parts = [f"Task: {task}"]
        if context:
            parts.append(f"Context:\n{context}")
        if memory:
            parts.append(f"Previous work on this repo:\n{memory}")
        parts.append("The repo has already been cloned into /code. Work from there.")
        return "\n\n".join(parts)
