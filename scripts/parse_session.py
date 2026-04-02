#!/usr/bin/env python3
"""Parse and display opencode session messages from stdin (JSON)."""
import json, sys

data = sys.stdin.read()
if not data:
    print("No data received. Is opencode serve running?")
    sys.exit(1)

try:
    msgs = json.loads(data)
except json.JSONDecodeError as e:
    print(f"JSON parse error: {e}")
    print(f"Raw response: {data[:500]}")
    sys.exit(1)

if not msgs:
    print("No messages found for this session.")
    sys.exit(0)

sid = msgs[0].get("info", {}).get("sessionID", "unknown")
print(f"Session: {sid}")
print(f"Total messages: {len(msgs)}")
print("=" * 60)

for i, m in enumerate(msgs):
    info = m.get("info", {})
    role = info.get("role", "?")
    model = info.get("modelID", "")
    provider = info.get("providerID", "")
    tokens = info.get("tokens", {})
    cost = info.get("cost", 0)

    header = f"Message {i} [{role.upper()}]"
    if model:
        header += f"  model={model}"
    if provider:
        header += f"  provider={provider}"
    print(f"\n--- {header} ---")

    if tokens and any(v for v in tokens.values() if isinstance(v, (int, float)) and v > 0):
        print(f"  Tokens: input={tokens.get('input',0)} output={tokens.get('output',0)} reasoning={tokens.get('reasoning',0)}")
        cache = tokens.get("cache", {})
        if cache.get("read") or cache.get("write"):
            print(f"  Cache: read={cache.get('read',0)} write={cache.get('write',0)}")
    if cost:
        print(f"  Cost: ${cost:.4f}")

    parts = m.get("parts", [])
    if not parts:
        print("  (no parts)")

    for p in parts:
        t = p.get("type", "?")

        if t == "text":
            txt = p.get("text", "")
            if len(txt) > 500:
                print(f"  [{t}] ({len(txt)} chars): {txt[:500]}...")
            elif txt:
                print(f"  [{t}]: {txt}")
            else:
                print(f"  [{t}]: (empty)")

        elif t == "reasoning":
            txt = p.get("text", "")
            if len(txt) > 300:
                print(f"  [{t}] ({len(txt)} chars): {txt[:300]}...")
            elif txt:
                print(f"  [{t}]: {txt}")

        elif t == "tool-invocation":
            tool_name = p.get("toolName", "?")
            args = p.get("args", {})
            args_str = json.dumps(args, ensure_ascii=False)
            if len(args_str) > 200:
                args_str = args_str[:200] + "..."
            print(f"  [{t}] {tool_name}: {args_str}")

        elif t == "tool-result":
            result = str(p.get("result", ""))
            if len(result) > 300:
                result = result[:300] + "..."
            print(f"  [{t}]: {result}")

        elif t == "step-start":
            print(f"  [{t}]")

        elif t == "step-finish":
            reason = p.get("reason", "?")
            st = p.get("tokens", {})
            print(f"  [{t}] reason={reason} tokens={{input={st.get('input',0)}, output={st.get('output',0)}, reasoning={st.get('reasoning',0)}}}")

        else:
            raw = json.dumps(p, ensure_ascii=False)
            if len(raw) > 200:
                raw = raw[:200] + "..."
            print(f"  [{t}]: {raw}")

print("\n" + "=" * 60)
print("Done.")
