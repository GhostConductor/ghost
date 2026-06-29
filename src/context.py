import logging
from pathlib import Path


TASK_FILE = Path("/data/TASK.md")
CONTEXT_FILE = Path("/data/CONTEXT.md")
INTENT_FILE = Path("/data/INTENT.md")


def load_task(logger: logging.LoggerAdapter) -> str:
    """Load task description from TASK.md."""
    if not TASK_FILE.exists():
        raise FileNotFoundError(f"Task file not found: {TASK_FILE}")

    with open(TASK_FILE, "r") as f:
        task = f.read()

    logger.info(f"Task loaded from {TASK_FILE}")
    return task


def load_context(logger: logging.LoggerAdapter) -> str:
    """Load context guidelines from CONTEXT.md."""
    if not CONTEXT_FILE.exists():
        raise FileNotFoundError(f"Context file not found: {CONTEXT_FILE}")

    with open(CONTEXT_FILE, "r") as f:
        context = f.read()

    logger.info(f"Context loaded from {CONTEXT_FILE}")
    return context


def load_system_prompt(logger: logging.LoggerAdapter) -> str:
    """Load system prompt from INTENT.md (created by gc-cman)."""
    if not INTENT_FILE.exists():
        raise FileNotFoundError(f"Intent file not found: {INTENT_FILE}")

    with open(INTENT_FILE, "r") as f:
        system_prompt = f.read()

    logger.info(f"System prompt loaded from {INTENT_FILE}")
    return system_prompt


def load_memory(logger: logging.LoggerAdapter) -> str | None:
    """Load previous memory from shared memory.md if it exists."""
    memory_file = Path("/shared/memory.md")
    if not memory_file.exists():
        logger.info("No previous memory found")
        return None

    with open(memory_file, "r") as f:
        memory = f.read()

    logger.info(f"Previous memory loaded from {memory_file}")
    return memory
