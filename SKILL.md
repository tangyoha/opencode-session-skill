---
name: opencode-session
description: Interact with OpenCode sessions via the headless serve API. Use when the user asks to inspect, debug, or analyze an opencode session, view session messages, send prompts to opencode, run analysis via opencode, check what a model returned, or references a session ID like "ses_xxx". Also triggers on "check session", "session history", "what happened in session", "send to opencode", "run in opencode", or debugging empty/broken model responses.
---

# OpenCode Session API

Inspect, create, and interact with OpenCode sessions via the headless serve API.

## Arguments

`/opencode-session <session_id>` — inspect a session
`/opencode-session send <prompt>` — create session and send prompt

## Auth & Connection

All API calls use `--noproxy "*"` (bypass proxy) and Basic Auth.

Default: `http://127.0.0.1:4999`, credentials: `opencode:changeme`

Check if serve is running:
```bash
curl --noproxy "*" -s -o /dev/null -w "%{http_code}" -u opencode:changeme http://127.0.0.1:4999/
```

If `000` (connection refused), start it:
```bash
unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy ALL_PROXY all_proxy && \
OPENCODE_SERVER_USERNAME=opencode OPENCODE_SERVER_PASSWORD=changeme \
nohup opencode serve --hostname 127.0.0.1 --port 4999 > /tmp/opencode_serve.log 2>&1 &
sleep 5
```

Proxy env vars must be unset before starting, otherwise opencode's API calls to local model servers get intercepted.

## Inspecting a session

```bash
curl --noproxy "*" -s -u opencode:changeme \
  "http://127.0.0.1:4999/session/<SESSION_ID>/message" | \
  python3 {skill_dir}/scripts/parse_session.py
```

### Analysis patterns

- `output=0` with no text parts → model failed to connect (check proxy)
- `reason=stop` but no text → model generated only tool calls
- High `reasoning` tokens, low `output` → thinking consumed the budget
- Check `modelID`/`providerID` to confirm correct model was used
- All tokens 0 → request never reached the model server

## Sending prompts

### Create session + send prompt

```bash
# 1. Create session
SID=$(curl --noproxy "*" -s -u opencode:changeme \
  -X POST "http://127.0.0.1:4999/session" \
  -H "Content-Type: application/json" -d '{}' | \
  python3 -c "import json,sys; print(json.load(sys.stdin).get('id',''))")

# 2. Send prompt (model selection is per-message, not per-session)
curl --noproxy "*" -s -u opencode:changeme \
  -X POST "http://127.0.0.1:4999/session/$SID/prompt_async" \
  -H "Content-Type: application/json" \
  -d '{
    "model": {"providerID": "<provider>", "modelID": "<model>"},
    "parts": [{"type": "text", "text": "<prompt>"}]
  }'
```

Without `model` field, uses the model currently selected in the OpenCode UI. The `POST /session` endpoint only accepts `{}` — passing modelID there has no effect.

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/session` | POST | Create session (`{}`) |
| `/session/<sid>/message` | GET | Get all messages |
| `/session/<sid>/prompt_async` | POST | Send prompt with optional model selection |
| `/session/<sid>/abort` | POST | Abort generation |
| `/session/<sid>/permissions/<pid>` | POST | Approve permission (`{"response":"once|always|reject"}`) |
| `/event` | GET | SSE event stream |
