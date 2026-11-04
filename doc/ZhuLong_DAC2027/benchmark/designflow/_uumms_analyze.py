#!/usr/bin/env python3
"""Analyze uumms.messages.json: print user text turns, tool_use summary,
and extract key file-contents from tool_results (read_file/get_file of .v / Cell_list)."""
import json, sys, re
from collections import Counter

d = json.load(open("uumms.messages.json"))
msgs = d["messages"] if isinstance(d, dict) and "messages" in d else d
print("TOTAL msgs:", len(msgs))

# user text turns
print("\n=== USER TEXT TURNS ===")
ui = 0
for i, m in enumerate(msgs):
    if m.get("role") != "user":
        continue
    content = m.get("content", [])
    if isinstance(content, str):
        text = content
    else:
        text = "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    if not text.strip():
        continue
    ui += 1
    print(f"\n--- U#{ui} (msg {i}) ---\n{text[:800]}")

print("\n\n=== ASSISTANT TOOL_USE SUMMARY ===")
c = Counter()
for m in msgs:
    if m.get("role") != "assistant":
        continue
    for b in m.get("content", []):
        if isinstance(b, dict) and b.get("type") == "tool_use":
            c[b.get("name", "?")] += 1
for k, v in c.most_common(30):
    print(f"  {k}: {v}")

# Extract tool_results that look like file contents (read_file / get_file / list_allowed_files)
print("\n\n=== FILE-CONTENT TOOL_RESULTS (first 2000 chars each) ===")
seen = 0
for i, m in enumerate(msgs):
    if m.get("role") != "user":
        continue
    content = m.get("content", [])
    if not isinstance(content, list):
        continue
    for b in content:
        if not isinstance(b, dict) or b.get("type") != "tool_result":
            continue
        tc = b.get("content")
        if isinstance(tc, list):
            ttxt = "\n".join(x.get("text", "") for x in tc if isinstance(x, dict))
        else:
            ttxt = str(tc)
        if not ttxt:
            continue
        # look for verilog / cell list / .v content
        low = ttxt[:200].lower()
        if any(s in low for s in ("module ", "cell_list", "cellname", "// cell", ".v ", "endmodule", "input ", "output ")):
            print(f"\n--- msg {i} tool={b.get('name','?')} ---")
            print(ttxt[:2500])
            seen += 1
            if seen >= 12:
                break
    if seen >= 12:
        break

print("\n\n=== ASSISTANT TEXT (final 3 messages) ===")
at = 0
for m in reversed(msgs):
    if m.get("role") != "assistant":
        continue
    content = m.get("content", [])
    if isinstance(content, str):
        text = content
    else:
        text = "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    if not text.strip():
        continue
    at += 1
    print(f"\n--- ASSISTANT #{at} ---\n{text[:1500]}")
    if at >= 4:
        break
