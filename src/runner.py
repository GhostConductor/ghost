import logging
import os
from agent.base import BaseAgent

DEFAULT_MAX_TURNS = 100


def build_agent(
    system_prompt: str,
    timeout: int,
    logger: logging.LoggerAdapter,
) -> BaseAgent:
    provider = os.environ.get("GC_PROVIDER", "anthropic")
    model = os.environ.get("GC_MODEL")

    if not model:
        raise EnvironmentError("GC_MODEL env var not set")

    logger.info(f"Building agent — provider={provider} model={model}")

    if provider == "anthropic":
        from agent.anthropic import AnthropicAgent
        return AnthropicAgent(
            model=model,
            system_prompt=system_prompt,
            max_turns=DEFAULT_MAX_TURNS,
            timeout=timeout,
            logger=logger,
        )

    if provider == "openai":
        from agent.openai import OpenAIAgent
        return OpenAIAgent(
            model=model,
            system_prompt=system_prompt,
            max_turns=DEFAULT_MAX_TURNS,
            timeout=timeout,
            logger=logger,
        )

    if provider == "gemini":
        from agent.gemini import GeminiAgent
        return GeminiAgent(
            model=model,
            system_prompt=system_prompt,
            max_turns=DEFAULT_MAX_TURNS,
            timeout=timeout,
            logger=logger,
        )

    raise ValueError(f"Unsupported provider: {provider}")
