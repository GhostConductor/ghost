import os
from agents import Agent, Runner
from .base import BaseAgent


class OpenAIAgent(BaseAgent):
    """OpenAI Agents SDK implementation of BaseAgent."""

    async def run(self, task: str, context: str, memory: str | None = None) -> tuple[str, dict]:
        os.environ["OPENAI_API_KEY"] = os.environ["AI_API_KEY"]

        prompt = self._build_prompt(task, context, memory)

        self.logger.info(
            f"Starting agent loop — model={self.model} max_turns={self.max_turns} timeout={self.timeout}s"
        )

        agent = Agent(
            name="gc-ghost",
            instructions=self.system_prompt,
            model=self.model,
        )

        result = await Runner.run(
            agent,
            prompt,
            max_turns=self.max_turns,
        )

        output = result.final_output or ""
        self.logger.info(f"Agent completed — output length={len(output)}")

        usage = {}
        try:
            u = result.context_wrapper.usage
            usage = {
                "input_tokens": u.input_tokens,
                "output_tokens": u.output_tokens,
                "total_tokens": u.total_tokens,
            }
            self.logger.info(f"usage: input={usage['input_tokens']} output={usage['output_tokens']}")
        except Exception as e:
            self.logger.warning(f"Could not extract usage: {e}")

        return output, usage

    def _build_prompt(self, task: str, context: str, memory: str | None = None) -> str:
        parts = [f"Task: {task}"]
        if context:
            parts.append(f"Context:\n{context}")
        if memory:
            parts.append(f"Previous work on this repo:\n{memory}")
        parts.append("The repo has already been cloned into /code. Work from there.")
        return "\n\n".join(parts)
