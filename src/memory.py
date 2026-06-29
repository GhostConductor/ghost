import logging
import os
from pathlib import Path
from datetime import datetime, timezone

MEMORY_ENTRY_FILE = Path("/data/memory_entry.md")
SHARED_MEMORY_FILE = Path("/shared/memory.md")
SAVE_MEMORY_PROMPT_FILE = Path("/data/UPDATE_MEMORY.md")
MAX_ENTRIES = 5


def _load_memory_prompt() -> str:
    if not SAVE_MEMORY_PROMPT_FILE.exists():
        raise FileNotFoundError(f"Memory prompt file not found: {SAVE_MEMORY_PROMPT_FILE}")
    return SAVE_MEMORY_PROMPT_FILE.read_text()


async def generate_memory(
    job_id: str,
    model: str,
    provider: str,
    agent_summary: str,
    logger: logging.LoggerAdapter,
) -> None:
    logger.info(f"Generating memory summary — provider={provider} model={model}")

    date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    memory_prompt = _load_memory_prompt()
    prompt = memory_prompt + f"\n\nHere is what the agent did:\n{agent_summary}"

    try:
        entry_text = _call_api(provider, model, prompt, logger)
        entry = f"## Job: {job_id} — {date}\n{entry_text}\n"

        # Write single entry (per-job archive)
        MEMORY_ENTRY_FILE.write_text(entry)
        logger.info(f"Memory entry written to {MEMORY_ENTRY_FILE}")

        # Read existing shared memory
        previous_entries = []
        if SHARED_MEMORY_FILE.exists():
            previous_entries = _parse_entries(SHARED_MEMORY_FILE.read_text())

        # Append new entry and trim to rolling window
        previous_entries.append(entry)
        if len(previous_entries) > MAX_ENTRIES:
            previous_entries = previous_entries[-MAX_ENTRIES:]

        SHARED_MEMORY_FILE.write_text("\n".join(previous_entries))
        logger.info(f"Shared memory updated: {len(previous_entries)} entries")

    except Exception as e:
        logger.warning(f"Memory generation failed (non-fatal): {e}")


def _call_api(provider: str, model: str, prompt: str, logger: logging.LoggerAdapter) -> str:
    api_key = os.environ["AI_API_KEY"]

    if provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    if provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    if provider == "gemini":
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(max_output_tokens=2000),
        )
        return response.text

    raise ValueError(f"Unsupported provider: {provider}")


def _parse_entries(text: str) -> list[str]:
    """Split accumulated memory into individual entries by ## Job: header."""
    entries = []
    current = []

    for line in text.split("\n"):
        if line.startswith("## Job:") and current:
            entries.append("\n".join(current) + "\n")
            current = []
        current.append(line)

    if current and any(l.strip() for l in current):
        entries.append("\n".join(current) + "\n")

    return entries
