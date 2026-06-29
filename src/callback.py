import logging
import os
import httpx


def _endpoint() -> str | None:
    return os.environ.get("GC_API_ENDPOINT")


def _post(payload: dict, logger: logging.LoggerAdapter) -> None:
    endpoint = _endpoint()
    if not endpoint:
        logger.warning("GC_API_ENDPOINT not set — skipping callback")
        return

    try:
        r = httpx.post(endpoint, json=payload, timeout=10)
        r.raise_for_status()
        logger.debug(f"Callback sent: {payload}")
    except Exception as e:
        logger.warning(f"Callback failed (non-fatal): {e}")


def job_started(job_id: str, logger: logging.LoggerAdapter) -> None:
    logger.info("Sending job_started callback")
    _post({"event": "job_started", "job_id": job_id}, logger)


def job_complete(job_id: str, branch: str, logger: logging.LoggerAdapter) -> None:
    logger.info("Sending job_complete callback")
    _post({"event": "job_complete", "job_id": job_id, "branch": branch}, logger)


def job_failed(job_id: str, error: str, logger: logging.LoggerAdapter) -> None:
    logger.info("Sending job_failed callback")
    _post({"event": "job_failed", "job_id": job_id, "error": error}, logger)
