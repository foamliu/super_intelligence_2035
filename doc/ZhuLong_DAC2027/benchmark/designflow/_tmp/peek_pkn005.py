#!/usr/bin/env python3
import json, sys, os
# Reads paths from stdin (one per line), for each extracts first 2 user-text messages
# Prints: sid\tuser\tsize\tmsgcount\tU0(first 200 chars)\tU1(first 200 chars)
sys.stdout.reconfigure(errors='replace')
for path in sys.stdin:
    path = path.strip()
    if not path: continue
    try:
        sid = os.path.basename(path).split("_",1)[1].replace(".messages.json","")
        user = path.split("/")[2]
    except Exception:
        sid = "?"; user = "?"
    try:
        with open(path, 'rb') as f:
            raw = f.read(200000)
        d = json.loads(raw.decode('utf-8', errors='replace'))
        msgs = d.get("messages", [])
        # content may be list or str
        def gettext(m):
            c = m.get("content")
            if isinstance(c, str):
                return c
            if isinstance(c, list):
                parts = []
                for it in c:
                    if isinstance(it, dict) and it.get("type")=="text":
                        parts.append(it.get("text",""))
                    elif isinstance(it, dict) and it.get("type")=="tool_result":
                        # skip tool results
                        pass
                return " ".join(parts)
            return ""
        user_msgs = []
        for m in msgs:
            if m.get("role")=="user":
                t = gettext(m)
                # skip empty / tool-result-only / environment reminders
                if t.strip() and not t.strip().startswith("<environment"):
                    user_msgs.append(t)
        u0 = (user_msgs[0][:200].replace("\n"," ").replace("\t"," ")) if len(user_msgs)>0 else ""
        u1 = (user_msgs[1][:150].replace("\n"," ").replace("\t"," ")) if len(user_msgs)>1 else ""
        print(f"{sid}\t{user}\t{len(raw)}\t{len(msgs)}\t{u0}\t{u1}")
    except Exception as e:
        print(f"{sid}\t{user}\tERR\t{type(e).__name__}: {str(e)[:80]}\t\t")
