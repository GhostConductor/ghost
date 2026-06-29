import json
import logging
from datetime import datetime, timezone
from pathlib import Path

EVENTS_FILE = Path("/data/events.json")


def _write(event: dict, logger: logging.LoggerAdapter) -> None:
    events = []
    if EVENTS_FILE.exists():
        try:
            events = json.loads(EVENTS_FILE.read_text())
        except Exception:
            events = []
    events.append(event)
    EVENTS_FILE.write_text(json.dumps(events, indent=2, default=str))
    logger.info(f"Event written: {event['event']}")


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def job_started(job_id: str, logger: logging.LoggerAdapter) -> None:
    _write({"event": "job_started", "job_id": job_id, "timestamp": _ts()}, logger)


def job_complete(job_id: str, branch: str, commit_sha: str, logger: logging.LoggerAdapter) -> None:
    _write({
        "event": "job_complete",
        "job_id": job_id,
        "branch": branch,
        "commit_sha": commit_sha,
        "timestamp": _ts(),
    }, logger)


def job_failed(job_id: str, error: str, detail: str, logger: logging.LoggerAdapter) -> None:
    _write({
        "event": "job_failed",
        "job_id": job_id,
        "error": error,
        "detail": detail,
        "timestamp": _ts(),
    }, logger)
