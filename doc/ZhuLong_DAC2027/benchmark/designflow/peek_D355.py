#!/usr/bin/env python3
"""Peek aw9d7 messages.json — extract user turns (text only, skip tool_result) + assistant tool_use summary."""
import json, sys

p = sys.argv[1] if len(sys.argv) > 1 else "aw9d7.messages.json"
d = json.load(open(p))
msgs = d["messages"]
print(f"n_msgs={len(msgs)} version={d.get('version')}")

def text_of(content):
    if isinstance(content, str):
        return content
    out = []
    if isinstance(content, list):
        for blk in content:
            if not isinstance(blk, dict):
                continue
            t = blk.get("type")
            if t == "text":
                out.append(blk.get("text", ""))
            elif t == "tool_result":
                out.append("[tool_result]")
            elif t == "tool_use":
                out.append(f"[tool_use name={blk.get('name')} input_keys={list((blk.get('input') or {}).keys())}]")
    return " | ".join(out)

for i, x in enumerate(msgs):
    role = x.get("role")
    if role == "user":
        txt = text_of(x.get("content"))
        if "[tool_result]" in txt and len(txt) < 200:
            continue  # skip pure tool_result echoes
        # Only show real user text turns (not tool_result wrappers)
        if isinstance(x.get("content"), list):
            texts = [b.get("text", "") for b in x["content"] if isinstance(b, dict) and b.get("type") == "text"]
            if not texts:
                continue
            joined = " ".join(texts).strip()
            if not joined:
                continue
            print(f"\n=== USER #{i} ===")
            print(joined[:1500])
    elif role == "assistant":
        if isinstance(x.get("content"), list):
            tools = [b for b in x["content"] if isinstance(b, dict) and b.get("type") == "tool_use"]
            texts = [b.get("text", "") for b in x["content"] if isinstance(b, dict) and b.get("type") == "text"]
            tline = " ".join(t for t in texts if t.strip())[:200]
            tnames = ",".join(b.get("name", "?") for b in tools)
            if tnames or tline:
                print(f"  ASST #{i}: tools=[{tnames}] txt={tline!r}")
