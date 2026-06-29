import logging
import os
import sys
from pathlib import Path

LOG_DIR = Path("/log")
LOG_FILE = LOG_DIR / "gc-ghost.log"


def setup_logger(job_id: str) -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("gc-ghost")
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] job_id=%(job_id)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S"
    )

    # File handler — picked up by CloudWatch agent
    fh = logging.FileHandler(LOG_FILE)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    # Stdout handler — visible via docker logs
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    sh.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(sh)

    # Inject job_id into all log records
    logger = logging.LoggerAdapter(logger, {"job_id": job_id})

    return logger
