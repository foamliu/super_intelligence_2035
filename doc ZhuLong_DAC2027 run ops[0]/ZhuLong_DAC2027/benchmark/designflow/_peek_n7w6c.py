#!/usr/bin/env python3
"""Peek n7w6c archive: extract user turns (verbatim, masked) + assistant tool calls summary.
Run ON remote machine (pkn001) via ssh. Reads the .messages.archive.json.
Output: compact summary to stdout.
"""
import json, sys, re

PATH = sys.argv[1] if len(sys.argv) > 1 else "/home/yuyingc/.cline/data/sessions/1793623698314_n7w6c/1793623698314_n7w6c.messages.archive.json"

def mask(s):
    if not isinstance(s, str):
        s = str(s)
    # mask tokens/keys/passwords only
    s = re.sub(r'(sk-[A-Za-z0-9]{6})[A-Za-z0-9_-]+', r'\1***', s)
    s = re.sub(r'([Pp]assword|[Pp]asswd|[Tt]oken|[Aa]pi[_-]?[Kk]ey)\s*[=:]\s*\S+', r'\1=***', s)
    return s

raw = open(PATH, encoding='utf-8', errors='replace').read()
data = None
try:
    data = json.loads(raw)
except Exception as e:
    print("JSON_PARSE_ERROR", e)
    sys.exit(1)

msgs = data.get("messages") if isinstance(data, dict) else data
if not isinstance(msgs, list):
    print("NO_MESSAGES_LIST")
    sys.exit(1)

print("=== NMSG:", len(msgs))
print("=== KEYS:", list(data.keys()) if isinstance(data, dict) else "list")

def get_texts(m):
    content = m.get("content")
    texts = []
    if isinstance(content, list):
        for c in content:
            if isinstance(c, dict):
                if c.get("type") == "text":
                    texts.append(c.get("text", ""))
                elif c.get("type") == "tool_use":
                    name = c.get("name", "?")
                    inp = c.get("input", {})
                    inp_str = json.dumps(inp, ensure_ascii=False)[:300]
                    texts.append(f"[TOOL_USE {name}] {inp_str}")
                elif c.get("type") == "tool_result":
                    pass  # skip tool results for brevity
    elif isinstance(content, str):
        texts.append(content)
    return texts

# Extract user turns (with index) and assistant tool calls
user_turns = []
tool_calls = []
for i, m in enumerate(msgs):
    role = m.get("role", "?")
    texts = get_texts(m)
    for txt in texts:
        if role == "user":
            # strip <user_input ...> wrapper if present
            mm = re.search(r'<user_input mode="\w+">(.+?)</user_input>', txt, re.S)
            ut = mm.group(1) if mm else txt
            ut = ut.strip()
            if ut and not ut.startswith("[TOOL_RESULT"):
                user_turns.append((i, ut))
        elif role == "assistant":
            if txt.startswith("[TOOL_USE"):
                tool_calls.append((i, txt))

print("=== USER_TURNS:", len(user_turns))
print("=== TOOL_CALLS:", len(tool_calls))

print("\n--- USER TURNS (verbatim, masked, truncated 600 chars) ---")
for idx, (i, t) in enumerate(user_turns):
    t = mask(t)
    if len(t) > 600:
        t = t[:600] + "...[TRUNC]"
    print(f"\n[U#{idx} msg#{i}]")
    print(t)

print("\n--- TOOL CALLS (name + brief input) ---")
from collections import Counter
names = Counter()
for i, t in tool_calls:
    nm = re.match(r'\[TOOL_USE (\S+)\]', t)
    if nm:
        names[nm.group(1)] += 1
print("TOOL FREQ:", dict(names.most_common(20)))

print("\n--- FIRST 40 TOOL CALLS ---")
for i, t in tool_calls[:40]:
    print(f"[msg#{i}] {t[:250]}")
