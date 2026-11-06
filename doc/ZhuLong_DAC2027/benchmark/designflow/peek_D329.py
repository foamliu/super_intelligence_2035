#!/usr/bin/env python3
"""Peek user turns from cline sessions - CORRECTED for directory-based storage.
Run ON .75 (parallel ssh to target machines). Pass TARGETS list.
Shard D #329 batch: top fresh_D319_avail candidates not yet peeked.
"""
import json, subprocess, concurrent.futures, re
import sys

def sh(ip, cmd, t=60):
    try:
        out = subprocess.run(["ssh","-o","BatchMode=yes","-o","ConnectTimeout=6","-n",ip,cmd],
            capture_output=True, text=True, timeout=t)
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
        return (sid, user, ip, ["NO_TURNS"], sz.strip() or "?", mc)
    return (sid, user, ip, turns[:8], sz.strip() or "?", mc)

TARGETS = [
    # (sid, user, ip, mc)
    ("1791525231478_vbxlf", "jason17w", "10.129.32.190", 262),
    ("1792995706498_jsb4j", "yohannw", "10.129.2.12", 196),
    ("1790236401918_27c6f", "jason17w", "10.129.32.190", 166),
    ("1789913077711_ld0p8", "ziyuny", "10.129.32.190", 164),
    ("1789961467130_nibwl", "ziyuny", "10.129.32.190", 154),
    ("1785390178118_ewjnc", "e0014566", "10.129.2.10", 147),
    ("1792738287471_mrlo9", "e03179", "10.129.2.11", 144),
    ("1786710801484_wsi93", "e0014566", "10.129.2.10", 143),
    ("1792043637880_ajcab", "e0023936", "10.129.32.75", 138),
    ("1791792980970_4vv1y", "lizwen", "10.129.2.11", 138),
    ("1792142998625_n1njg", "jessegao", "10.129.2.14", 137),
    ("1786586471140_pepxy", "e0014566", "10.129.2.10", 137),
    ("1790684140804_vtl11", "haoliu", "10.129.8.106", 135),
    ("1792659994477_rw6z4", "e0045488", "10.129.2.11", 134),
    ("1786613295407_a9ta2", "e0014566", "10.129.2.10", 131),
]

if __name__ == "__main__":
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        for r in ex.map(peek_one, TARGETS):
            results.append(r)
    for sid, user, ip, turns, sz, mc in results:
        print("==== %s | %s@%s | mc=%s | size=%s | nturns=%d" % (sid, user, ip, mc, sz, len(turns)))
        for i, t in enumerate(turns):
            t1 = t.replace("\n", " ")[:280]
            print("  U#%d: %s" % (i, t1))
        print()
