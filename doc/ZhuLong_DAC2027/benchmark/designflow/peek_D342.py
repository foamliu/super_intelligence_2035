#!/usr/bin/env python3
"""Peek #342 candidates (fresh_D319_avail, shard D, unpeeked high netlist/analog/hspice)."""
import json, subprocess, concurrent.futures, re

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
    ("1789730312848_hpd7c", "yongk1li", "10.129.2.12"),       # netlist:364 .cdl:50 mc79
    ("1790156336826_y2xz6", "jason17w", "10.129.32.190"),     # netlist:324 mc77
    ("1788946694927_w5knw", "sagequan", "10.129.32.190"),     # analog:298 hspice:59 mc83
    ("1792378803577_hpy3y", "ruisongs", "10.129.33.207"),     # netlist:262 analog:28 mc82
    ("1792549549929_j0t84", "zhukaic", "10.129.33.26"),       # hspice:79 waveview:25 netlist:24 mc87
    ("1791941283310_41sqh", "sagequan", "10.129.32.190"),     # analog:276 netlist:87 waveview:10 mc115
    ("1792042544705_d1cg3", "t0002441", "10.129.32.75"),      # synopsys:2984 hspice:185 mc102
    ("1789634880745_4ys8e", "ellawu", "10.129.2.14"),         # .gds:2006 calibre:581 mc119 (physical? check)
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
