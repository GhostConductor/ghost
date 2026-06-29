# ghost

The Ghost Conductor agent runtime. A single Docker image that runs autonomous software engineering jobs inside an isolated container.

## What it does

ghost is the agent that does the work. It reads a task, explores a codebase, writes code, commits, and pushes to a feature branch for human review.

- Supports Anthropic, OpenAI, and Google providers
- Provider and model selected at runtime — nothing baked in
- Designed to be launched by ghostconductor or server

## Pulling the image

```bash
docker pull ghcr.io/ghostconductor/ghost:latest
```

## Environment Variables

| Variable | Required | Example | Purpose |
|---|---|---|---|
| `GC_JOB_ID` | ✅ | `job-20260628-abc123` | Unique job identifier |
| `GC_PROVIDER` | ✅ | `anthropic` | AI provider (`anthropic`, `openai`, `google`) |
| `GC_MODEL` | ✅ | `claude-sonnet-4-6` | Model name |
| `GC_INTENT` | ✅ | `build_feature` | Intent type |
| `GC_TIME_LIMIT` | ✅ | `1800` | Time limit in seconds |
| `GC_API_ENDPOINT` | ✅ | `http://localhost:7777` | Callback endpoint |
| `ANTHROPIC_API_KEY` | ✅ | `sk-ant-...` | Provider API key |
| `GITHUB_TOKEN` | ✅ | `github_pat_...` | GitHub token for push |
| `GC_GIT_EMAIL` | ✅ | `you@example.com` | Git commit email |
| `GC_GIT_NAME` | ✅ | `Justin Timberlake` | Git commit name |

## Contributing

ghost is part of the GhostConductor platform. At this stage we are not accepting outside PRs. Issues and feedback welcome.

## License

MIT