import json
import os
import sys
from dataclasses import dataclass, field


@dataclass
class RepoMount:
    id: str
    name: str
    path: str
    branch: str


@dataclass
class Config:
    job_id: str
    repos: list[RepoMount]
    intent: str
    time_limit: int  # seconds
    ai_api_key: str
    model: str
    provider: str
    git_email: str = os.getenv("GC_GIT_EMAIL", "ghost@ghostconductor.dev")
    git_name: str = os.getenv("GC_GIT_NAME", "Ghost Agent")

def load_config() -> Config:
    """Load configuration from environment variables set by gc-cman."""

    def require(key: str) -> str:
        val = os.environ.get(key)
        if not val:
            print(f"ERROR: {key} env var not set", file=sys.stderr)
            sys.exit(1)
        return val

    time_limit_str = os.environ.get("GC_TIME_LIMIT", "30m")

    repos_json = require("GC_REPOS")
    try:
        repos_raw = json.loads(repos_json)
        repos = [RepoMount(**r) for r in repos_raw]
    except Exception as e:
        print(f"ERROR: failed to parse GC_REPOS: {e}", file=sys.stderr)
        sys.exit(1)

    return Config(
        job_id=require("GC_JOB_ID"),
        repos=repos,
        intent=require("GC_INTENT"),
        ai_api_key=require("AI_API_KEY"),
        model=require("GC_MODEL"),
        provider=require("GC_PROVIDER"),
        time_limit=_parse_time_limit(time_limit_str),
    )


def _parse_time_limit(val: str) -> int:
    val = str(val).strip()
    if val.endswith("m"):
        return int(val[:-1]) * 60
    elif val.endswith("h"):
        return int(val[:-1]) * 3600
    elif val.endswith("s"):
        return int(val[:-1])
    return int(val)
