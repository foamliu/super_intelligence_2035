#!/usr/bin/env python3
"""Peek D400 candidates on reachable hosts (10.129.32.x). Run ON .75."""
import json, subprocess, concurrent.futures, re, sys

TARGETS = [
    # schematic_netlist / analog_context priority (shard D)
    ("1789713740053_1fgo2", "ynbai", "10.129.32.75"),      # mc187 netlist193
    ("1793078082560_sax5x", "miccao", "10.129.32.47"),     # mc153 pyAether204
    ("1791636307671_wiglh", "jason17w", "10.129.32.190"),  # mc141 netlist940
    ("1791785748768_pvl8c", "steveny", "10.129.32.189"),   # mc139 schematic67 cellview85
    ("1791787809781_w7un3", "ziyuny", "10.129.32.190"),    # mc113 schematic241
    ("1789889776686_se4uf", "miccao", "10.129.32.47"),     # mc106 netlist142 schematic60
    ("1789631689135_9pcjd", "miccao", "10.129.32.47"),     # mc79 schematic92
    ("1790042369946_o1yhw", "steveny", "10.129.32.189"),   # mc78 virtuoso271
    ("1790150666233_ob8f4", "jason17w", "10.129.32.190"),  # mc77 netlist166 hspice40
    ("1791617131890_5kh50", "ziyuny", "10.129.32.190"),    # mc67 pyAether102 schematic50
    ("1792111744261_uxwb5", "e0023936", "10.129.32.75"),   # mc64 pyAether122 netlist63 schematic38
    ("1790216933447_e5opy", "jason17w", "10.129.32.190"),  # mc61 netlist241
    ("1789803471527_ypwty", "ziyuny", "10.129.32.190"),    # mc55 pyAether41 schematic7
    ("1791782422113_e1ll7", "steveny", "10.129.32.189"),   # mc58 cellview125 schematic104
    ("1791782242441_8rxb1", "steveny", "10.129.32.189"),   # mc47 cellview146 schematic120
    ("1790064843293_r98dm", "e0042337", "10.129.32.204"),  # mc68 netlist185
]

def sh(ip, cmd, t=60):
    try:
        out = subprocess.run(["bash","-c","timeout %d ssh -o BatchMode=yes -o ConnectTimeout=5 %s '%s' </dev/null 2>/dev/null" % (t, ip, cmd.replace("'","'\\''"))],
            capture_output=True, text=True, timeout=t+10)
        return out.stdout, out.returncode
    except Exception as e:
        return "EXC:"+str(e), 998

def extract_user_turns(raw):
    data = None
    try: data = json.loads(raw)
    except Exception: return []
    msgs = data.get("messages") if isinstance(data, dict) else data
    if not isinstance(msgs, list): return []
    turns = []
    for m in msgs:
        if m.get("role") != "user": continue
        content = m.get("content"); texts = []
        if isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and c.get("type") == "text":
                    texts.append(c.get("text",""))
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
    # try directory-based then root
    cmds = [
        "cat /home/%s/.cline/data/sessions/%s/%s.messages.json 2>/dev/null" % (user, sid, sid),
        "cat /home/%s/.cline/data/sessions/%s.messages.json 2>/dev/null" % (user, sid),
    ]
    raw = ""
    for c in cmds:
        raw, rc = sh(ip, c, 60)
        if raw and "EXC:" not in raw and len(raw) > 50:
            break
    if not raw or len(raw) < 50:
        # try size
        sz, _ = sh(ip, "stat -c %%s /home/%s/.cline/data/sessions/%s/%s.messages.json 2>/dev/null" % (user, sid, sid), 15)
        return (sid, user, ip, ["NO_FILE or empty (sz=%s)" % sz.strip()], "?")
    turns = extract_user_turns(raw)
    if not turns:
        for mm in re.finditer(r'<user_input mode="act">(.+?)</user_input>', raw, re.S):
            s = mm.group(1).strip()
            if s and not s.startswith("<"):
                turns.append(s)
    sz = str(len(raw))
    return (sid, user, ip, turns, sz)

with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    futs = {ex.submit(peek_one, t): t for t in TARGETS}
    for fu in concurrent.futures.as_completed(futs):
        try:
            sid, user, ip, turns, sz = fu.result()
        except Exception as e:
            t = futs[fu]; sid, user, ip, turns, sz = t[0], t[1], t[2], ["EXC:"+str(e)], "?"
        print("### %s | %s@%s | size=%s | nturns=%d" % (sid, user, ip, sz, len(turns)))
        for i, tn in enumerate(turns[:6]):
            print("  [U#%d] %s" % (i, tn[:380].replace("\n"," ")))
        print("---")
        sys.stdout.flush()
