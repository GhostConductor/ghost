import yaml
from dataclasses import dataclass
from pathlib import Path


JOB_FILE = Path("/code/gc-job.yaml")


@dataclass
class Job:
    intent: str
    task: str
    context: str
    repo: str
    time_limit: int  # seconds
    job_id: str


def load_job(job_id: str) -> Job:
    if not JOB_FILE.exists():
        raise FileNotFoundError(f"Job file not found: {JOB_FILE}")

    with open(JOB_FILE) as f:
        data = yaml.safe_load(f)

    return Job(
        intent=data["intent"],
        task=data["task"],
        context=data.get("context", ""),
        repo=data["repo"],
        time_limit=_parse_time_limit(data.get("time_limit", "30m")),
        job_id=job_id,
    )


def _parse_time_limit(val: str) -> int:
    """Parse time limit string to seconds. e.g. '30m' -> 1800, '1h' -> 3600"""
    val = str(val).strip()
    if val.endswith("m"):
        return int(val[:-1]) * 60
    elif val.endswith("h"):
        return int(val[:-1]) * 3600
    elif val.endswith("s"):
        return int(val[:-1])
    return int(val)
