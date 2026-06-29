import logging
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Abstract base class for all gc-ghost agent implementations."""

    def __init__(
        self,
        model: str,
        system_prompt: str,
        max_turns: int,
        timeout: int,
        logger: logging.LoggerAdapter,
    ):
        self.model = model
        self.system_prompt = system_prompt
        self.max_turns = max_turns
        self.timeout = timeout
        self.logger = logger

    @abstractmethod
    async def run(self, task: str, context: str, memory: str | None = None) -> tuple[str, dict]:
        """
        Run the agent with the given task, context, and optional memory.
        Returns a tuple of (summary, usage) where usage contains token counts and cost.
        """
        pass
