import logging
import os
import subprocess
from pathlib import Path


def _run(cmd: list[str], logger: logging.LoggerAdapter, cwd: Path) -> str:
    logger.debug(f"git: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"git command failed: {' '.join(cmd)}\n{result.stderr}")
    return result.stdout.strip()


def create_branch(job_id: str, repos: list, logger: logging.LoggerAdapter) -> str:
    branch = f"ghost-conductor/{job_id}"
    for repo in repos:
        repo_path = Path(repo.path)
        _run(["git", "config", "--global", "--add", "safe.directory", repo.path], logger, cwd=repo_path)
        _run(["git", "fetch", "origin", repo.branch], logger, cwd=repo_path)
        _run(["git", "checkout", repo.branch], logger, cwd=repo_path)
        _run(["git", "pull", "origin", repo.branch], logger, cwd=repo_path)
        _run(["git", "checkout", "-b", branch], logger, cwd=repo_path)
        logger.info(f"Branch {branch} created in {repo.name}")
    return branch


def commit_and_push(job_id: str, repos: list, logger: logging.LoggerAdapter) -> str | None:
    """Commit and push changes across all repos. Returns last commit SHA or None."""
    branch = f"ghost-conductor/{job_id}"
    last_sha = None

    for repo in repos:
        repo_path = Path(repo.path)
        _run(["git", "add", "-A"], logger, cwd=repo_path)
        status = _run(["git", "status", "--porcelain"], logger, cwd=repo_path)
        if not status:
            logger.info(f"No changes to commit in {repo.name}")
            continue

        logger.info(f"Committing changes in {repo.name}")
        _run(["git", "commit", "-m", f"gc-ghost: job {job_id}"], logger, cwd=repo_path)
        _run(["git", "push", "-u", "origin", branch], logger, cwd=repo_path)
        last_sha = _run(["git", "rev-parse", "HEAD"], logger, cwd=repo_path)
        logger.info(f"Committed and pushed {repo.name}: {last_sha}")

    return last_sha
