# opencode-session

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) / [OpenCode](https://opencode.ai) skill for inspecting, creating, and interacting with OpenCode sessions via the headless serve API.

## What it does

- **Inspect sessions** — fetch and display full message history with token usage, model info, and tool calls
- **Send prompts** — create sessions and send prompts with per-message model selection
- **Debug issues** — diagnose empty responses, proxy problems, and model mismatches

## Install

### Claude Code

```bash
# Clone into your skills directory
git clone https://github.com/tangyoha/opencode-session-skill.git \
  ~/.claude/skills/opencode-session
```

### OpenCode

```bash
git clone https://github.com/tangyoha/opencode-session-skill.git \
  ~/.config/opencode/skills/opencode-session
```

## Usage

### Inspect a session

```
/opencode-session ses_abc123def456
```

Displays all messages with:
- Role, model, provider
- Token usage (input/output/reasoning/cache)
- Text content, tool calls, reasoning traces
- Step finish reasons

### Send a prompt via API

```bash
# Create session
SID=$(curl --noproxy "*" -s -u opencode:changeme \
  -X POST "http://127.0.0.1:4999/session" \
  -H "Content-Type: application/json" -d '{}' | \
  python3 -c "import json,sys; print(json.load(sys.stdin).get('id',''))")

# Send prompt with model selection
curl --noproxy "*" -s -u opencode:changeme \
  -X POST "http://127.0.0.1:4999/session/$SID/prompt_async" \
  -H "Content-Type: application/json" \
  -d '{
    "model": {"providerID": "<provider>", "modelID": "<model>"},
    "parts": [{"type": "text", "text": "your prompt"}]
  }'
```

> Model selection is per-message in `prompt_async`, not per-session. `POST /session` only accepts `{}`.

## Prerequisites

- [OpenCode](https://opencode.ai) running in headless serve mode
- Python 3.8+
- `curl` with `--noproxy` support

### Start OpenCode serve

```bash
unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy ALL_PROXY all_proxy && \
OPENCODE_SERVER_USERNAME=opencode OPENCODE_SERVER_PASSWORD=changeme \
opencode serve --hostname 127.0.0.1 --port 4999
```

## Files

```
opencode-session/
├── SKILL.md              # Skill definition (loaded by Claude Code / OpenCode)
├── scripts/
│   └── parse_session.py  # Session message parser (reads JSON from stdin)
└── README.md
```

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/session` | POST | Create session |
| `/session/<sid>/message` | GET | Get all messages |
| `/session/<sid>/prompt_async` | POST | Send prompt with optional model |
| `/session/<sid>/abort` | POST | Abort generation |
| `/session/<sid>/permissions/<pid>` | POST | Approve permission |
| `/event` | GET | SSE event stream |

## License

MIT
