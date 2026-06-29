import os
import anyio
import fcntl
import json
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from logger import setup_logger
from config import load_config
from context import load_system_prompt, load_task, load_context, load_memory
from runner import build_agent
from git import create_branch, commit_and_push
from events import job_started, job_complete, job_failed
from memory import generate_memory

USAGE_FILE = Path(os.environ.get("GC_USAGE_PATH", "/shared/usage.json"))


def write_result(job_id: str, status: str, exit_code: int, usage: dict, logger) -> None:
    result = {
        "status": status,
        "exit_code": exit_code,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "usage": usage,
    }
    Path("/data/result.json").write_text(json.dumps(result, indent=2))
    logger.info(f"result.json written: status={status} usage={usage}")


def append_usage(job_id: str, model: str, provider: str, usage: dict, logger) -> None:
    if not usage:
        logger.info("No usage data — skipping usage.json append")
        return

    entry = {
        "job_id": job_id,
        "model": model,
        "provider": provider,
        "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
        "cost_usd": usage.get("total_cost_usd"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    try:
        USAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(USAGE_FILE, "a+") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                f.seek(0)
                content = f.read().strip()
                entries = json.loads(content) if content else []
                entries.append(entry)
                f.seek(0)
                f.truncate()
                f.write(json.dumps(entries, indent=2))
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
        logger.info(f"usage.json updated: job={job_id} model={model} provider={provider} input={entry['input_tokens']} output={entry['output_tokens']} cost={entry['cost_usd']}")
    except Exception as e:
        logger.warning(f"Failed to update usage.json: {e}")


async def main():
    config = load_config()

    if config.git_email:
        subprocess.run(["git", "config", "--global", "user.email", config.git_email])
    if config.git_name:
        subprocess.run(["git", "config", "--global", "user.name", config.git_name])

    logger = setup_logger(config.job_id)
    logger.info("gc-ghost starting")
    logger.info(f"job_id={config.job_id} repos={[r.name for r in config.repos]} intent={config.intent} time_limit={config.time_limit}s")

    branch = None
    usage = {}
    try:
        logger.info("Loading task and context")
        task = load_task(logger)
        context = load_context(logger)
        logger.info(f"Task loaded: {task[:50]}...")

        logger.info(f"Loading system prompt for intent: {config.intent}")
        system_prompt = load_system_prompt(logger)

        memory = load_memory(logger)

        logger.info(f"Creating branch: ghost-conductor/{config.job_id}")
        branch = create_branch(config.job_id, config.repos, logger)

        job_started(config.job_id, logger)

        logger.info("Building agent and starting work")
        agent = build_agent(system_prompt, config.time_limit, logger)
        summary, usage = await agent.run(task, context, memory)
        logger.info(f"Agent completed: {summary}")

        logger.info("Committing and pushing changes")
        commit_sha = commit_and_push(config.job_id, config.repos, logger)

        logger.info("Generating memory summary")
        await generate_memory(config.job_id, config.model, config.provider, summary, logger)

        write_result(config.job_id, "completed", 0, usage, logger)
        append_usage(config.job_id, config.model, config.provider, usage, logger)
        job_complete(config.job_id, branch, commit_sha or "", logger)

        logger.info("gc-ghost done")

    except Exception as e:
        import traceback
        detail = traceback.format_exc()
        logger.error(f"gc-ghost failed: {e}", exc_info=True)
        write_result(config.job_id, "failed", 1, usage, logger)
        append_usage(config.job_id, config.model, config.provider, usage, logger)
        await generate_memory(config.job_id, config.model, config.provider, f"Job failed: {e}\n{detail}", logger)
        job_failed(config.job_id, str(e), detail, logger)
        sys.exit(1)


anyio.run(main)
