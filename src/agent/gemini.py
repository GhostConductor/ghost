import os
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from .base import BaseAgent


class GeminiAgent(BaseAgent):
    """Google ADK implementation of BaseAgent."""

    async def run(self, task: str, context: str, memory: str | None = None) -> tuple[str, dict]:
        os.environ["GOOGLE_GENAI_API_KEY"] = os.environ["AI_API_KEY"]

        prompt = self._build_prompt(task, context, memory)

        self.logger.info(
            f"Starting agent loop — model={self.model} max_turns={self.max_turns} timeout={self.timeout}s"
        )

        agent = LlmAgent(
            name="gc-ghost",
            model=self.model,
            instruction=self.system_prompt,
        )

        session_service = InMemorySessionService()
        runner = Runner(
            agent=agent,
            app_name="gc-ghost",
            session_service=session_service,
        )

        session = await session_service.create_session(
            app_name="gc-ghost",
            user_id="gc-ghost",
        )

        output_parts = []
        usage = {}
        total_input = 0
        total_output = 0

        async for event in runner.run_async(
            user_id="gc-ghost",
            session_id=session.id,
            new_message=prompt,
        ):
            if event.usage_metadata:
                total_input += event.usage_metadata.prompt_token_count or 0
                total_output += event.usage_metadata.candidates_token_count or 0
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        self.logger.info(f"agent: {part.text}")
                        output_parts.append(part.text)

        if total_input or total_output:
            usage = {
                "input_tokens": total_input,
                "output_tokens": total_output,
                "total_tokens": total_input + total_output,
            }
            self.logger.info(f"usage: input={total_input} output={total_output}")

        output = "\n".join(output_parts)
        self.logger.info(f"Agent completed — output length={len(output)}")
        return output, usage

    def _build_prompt(self, task: str, context: str, memory: str | None = None) -> str:
        parts = [f"Task: {task}"]
        if context:
            parts.append(f"Context:\n{context}")
        if memory:
            parts.append(f"Previous work on this repo:\n{memory}")
        parts.append("The repo has already been cloned into /code. Work from there.")
        return "\n\n".join(parts)
