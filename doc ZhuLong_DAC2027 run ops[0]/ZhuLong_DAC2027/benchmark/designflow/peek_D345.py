#!/usr/bin/env python3
"""Peek #345 candidates (fresh D-domain, not in ledger, strong netlist/schematic/analog/hspice)."""
import json, subprocess, concurrent.futures, re

def sh(ip, cmd, t=90):
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
    sid, user, ip = t
    ls = "ls /home/%s/.cline/data/sessions/%s/%s.messages.json 2>/dev/null" % (user, sid, sid)
    out, rc = sh(ip, ls, 20)
    files = [f for f in out.split() if f]
    if not files:
        return (sid, user, ip, ["NO_FILE"], "?")
    fpath = files[0]
    sz, _ = sh(ip, "stat -c %%s %s" % fpath, 20)
    out2, _ = sh(ip, "cat %s" % fpath, 90)
    turns = extract_user_turns(out2)
    if not turns:
        for mm in re.finditer(r'<user_input mode="act">(.+?)</user_input>', out2, re.S):
            s = mm.group(1).strip()
            if s and not s.startswith("<"):
                turns.append(s)
    return (sid, user, ip, turns, sz.strip())

TARGETS = [
    ("1791636307671_wiglh", "jason17w", "10.129.32.190"),     # netlist:964 mc123 ★strong netlist
    ("1790149493569_194wf", "ziyuny", "10.129.32.190"),       # schematic:210 analog:126 mc128
    ("1786586471140_pepxy", "e0014566", "10.129.2.10"),       # analog:113 calibre:57 mc137
    ("1793166879135_xs1lj", "e0017906", "10.129.2.11"),       # netlist:324 mc119
    ("1792668123134_0oeb7", "colinxu", "10.129.2.18"),        # netlist:32 analog:30 mc124
    ("1791514218543_hkyyj", "t0002962", "10.129.2.12"),       # pyaether:518 aether:156 mc112
    ("1792057192352_iz828b", "shuoran", "10.129.33.28"),      # placeholder (iz828 parked); skip if nofile
]

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
    futs = {ex.submit(peek_one, t): t for t in TARGETS}
    for fu in concurrent.futures.as_completed(futs):
        try:
            sid, user, ip, turns, sz = fu.result()
        except Exception as e:
            t = futs[fu]; sid, user, ip, turns, sz = t[0], t[1], t[2], ["EXC:"+str(e)], "?"
        print("### %s | %s@%s | size=%s | nturns=%d" % (sid, user, ip, sz, len(turns)))
        for i, tn in enumerate(turns[:6]):
            print("  [U#%d] %s" % (i, tn[:500].replace("\n", " ")))
        print("---")
