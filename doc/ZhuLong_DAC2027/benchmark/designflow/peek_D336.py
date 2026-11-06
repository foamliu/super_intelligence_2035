#!/usr/bin/env python3
"""Peek user turns from cline sessions - directory-based storage.
Run ON .75 (parallel ssh to target machines).
"""
import json, subprocess, concurrent.futures, re
import sys

TARGETS = [('1792043637880_ajcab', 'e0023936', '10.129.32.75', '138'), ('1792142998625_n1njg', 'jessegao', '10.129.2.14', '137'), ('1786586471140_pepxy', 'e0014566', '10.129.2.10', '137'), ('1790149493569_194wf', 'ziyuny', '10.129.32.190', '128'), ('1792668123134_0oeb7', 'colinxu', '10.129.2.18', '124'), ('1791636307671_wiglh', 'jason17w', '10.129.32.190', '123'), ('1793166879135_xs1lj', 'e0017906', '10.129.2.11', '119'), ('1789634880745_4ys8e', 'ellawu', '10.129.2.14', '119')]

def sh(ip, cmd, t=60):
    try:
        out = subprocess.run(["ssh","-o","BatchMode=yes","-o","ConnectTimeout=6",ip,cmd],
            capture_output=True, text=True, timeout=t, stdin=subprocess.DEVNULL)
        return out.stdout, out.returncode
    except Exception:
        return "", 998

def extract_user_turns(raw):
    data = None
    try:
        data = json.loads(raw)
    except Exception:
        return []
    msgs = data.get("messages") if isinstance(data, dict) else data
    if not isinstance(msgs, list):
        return []
    turns = []
    for m in msgs:
        if m.get("role") != "user":
            continue
        content = m.get("content"); texts = []
        if isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and c.get("type") == "text":
                    texts.append(c.get("text", ""))
        elif isinstance(content, str):
            texts.append(content)
        for txt in texts:
            if txt.startswith("<user_input"):
                mm = re.search(r'<user_input mode="act">(.+?)</user_input>', txt, re.S)
                if mm: txt = mm.group(1)
            if txt.startswith("<skill_instructions>") or txt.startswith("<environment_details>") or txt.startswith("<attempt_completion"):
                continue
            s = txt.strip()
            if s and not s.startswith("<"):
                turns.append(s)
    return turns

def peek_one(t):
    sid, user, ip, mc = t
    ls = "ls /home/%s/.cline/data/sessions/%s/%s.messages.json 2>/dev/null" % (user, sid, sid)
    out, rc = sh(ip, ls, 20)
    files = [f for f in out.split() if f]
    if not files:
        return (sid, user, ip, ["NO_FILE"], "?", mc)
    fpath = files[0]
    sz, _ = sh(ip, "stat -c %%s %s" % fpath, 20)
    out2, _ = sh(ip, "cat %s" % fpath, 90)
    turns = extract_user_turns(out2)
    if not turns:
        for mm in re.finditer(r'<user_input mode="act">(.+?)</user_input>', out2, re.S):
            s = mm.group(1).strip()
            if s and not s.startswith("<"):
                turns.append(s)
    return (sid, user, ip, turns, sz.strip(), mc)

if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(peek_one, t): t for t in TARGETS}
        for fu in concurrent.futures.as_completed(futs):
            try:
                sid, user, ip, turns, sz, mc = fu.result()
            except Exception as e:
                t = futs[fu]; sid, user, ip, turns, sz, mc = t[0], t[1], t[2], ["EXC:"+str(e)], "?", t[3]
            print("### %s | mc=%s | %s@%s | size=%s | nturns=%d" % (sid, mc, user, ip, sz, len(turns)))
            for i, tn in enumerate(turns[:5]):
                print("  [U#%d] %s" % (i, tn[:450].replace("\n", " ")))
            print("---")
