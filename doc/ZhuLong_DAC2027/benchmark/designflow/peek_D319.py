#!/usr/bin/env python3
"""Peek batch for shard D #319. Run ON .75. Parallel ssh to target machines.
Directory-based cline storage: /home/<user>/.cline/data/sessions/<sid>/<sid>.messages.json
Extract user turns + assistant tool signal (editor + produce files) to triage A-faithful produce candidates.
"""
import json, subprocess, concurrent.futures, re, sys

TARGETS = [
    ("1785403392139_acdfh", "e0014566", "10.129.2.10", 56, "netlist:215"),
    ("1790065627121_rzitp", "e0042337", "10.129.32.190", 56, "netlist:222"),
    ("1790070349314_7hpf9", "e0042337", "10.129.32.190", 56, "netlist:222"),
    ("1782390514668_65lrn", "e03179", "10.129.2.11", 56, "cellview:226"),
    ("1791537132811_pmnfz", "jason17w", "10.129.32.190", 55, "netlist:141"),
    ("1792066077921_ccxtr", "colinxu", "10.129.2.18", 55, "cellview:329"),
    ("1789803471527_ypwty", "ziyuny", "10.129.32.190", 55, "aether:247"),
    ("1792552761049_zw6mx", "xinqiaoz", "10.129.2.13", 55, "pdk:582"),
    ("1786524631640_pi18b", "e0014566", "10.129.2.10", 53, "virtuoso:117"),
    ("1790573877427_0qyc2", "alenxu", "10.129.2.12", 53, "synopsys:51"),
    ("1788871441686_fieju", "harrys", "10.129.2.11", 53, "synopsys:106"),
    ("1792475021825_nn4my", "hongyuy", "10.129.8.102", 53, "pdk:534"),
    ("1792050093175_2cmzd", "miccao", "10.129.32.47", 53, "cmos:80"),
    ("1787636335993_qe1va", "e0025730", "10.129.8.86", 52, "netlist:99"),
    ("1792388291549_ntduw", "jessegao", "10.129.2.14", 52, "aether:130"),
    ("1790151981511_hn72n", "oliverz", "10.129.40.209", 44, "aether:370"),
    ("1792738969144_h0gyt", "tongfanl", "10.129.35.69", 43, "netlist:172"),
    ("1789894067947_9lbfz", "iceyma", "10.129.2.14", 43, "netlist:252"),
    ("1788861941268_1giox", "e0014566", "10.129.2.10", 80, "cellview:143"),
    ("1792378803577_hpy3y", "ruisongs", "10.129.33.207", 82, "netlist:262"),
    ("1792131163281_6sxh5", "e0045488", "10.129.2.11", 82, ".spi:110"),
    ("1788946694927_w5knw", "sagequan", "10.129.32.190", 83, "analog:298"),
    ("1789961307805_2uipn", "ziyuny", "10.129.32.190", 83, "pyaether:169"),
    ("1791947113001_be1i0", "jie23z", "10.129.2.11", 84, "cellview:200"),
    ("1792735101347_oe94r", "jiebings", "10.129.2.10", 84, "aether:167"),
    ("1790230482027_7lp3l", "jiangbaol", "10.129.2.11", 86, "cellview:101"),
]

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

def assistant_signal(raw):
    """Count editor tool uses + extract produced file names from assistant messages."""
    data = None
    try:
        data = json.loads(raw)
    except Exception:
        return 0, []
    msgs = data.get("messages") if isinstance(data, dict) else data
    if not isinstance(msgs, list):
        return 0, []
    nedit = 0
    produced = set()
    for m in msgs:
        if m.get("role") != "assistant":
            continue
        content = m.get("content")
        if isinstance(content, list):
            for c in content:
                if not isinstance(c, dict):
                    continue
                # tool_use blocks
                if c.get("type") == "tool_use":
                    name = c.get("name","")
                    inp = c.get("input", {})
                    if name in ("write_to_file","create_file","editor","apply_diff","insert_content","search_and_replace"):
                        nedit += 1
                        fp = inp.get("path") or inp.get("file") or inp.get("filePath") or ""
                        if fp:
                            produced.add(fp)
                    elif name in ("execute_command","run_command","run_commands","bash"):
                        cmd = inp.get("command","") or inp.get("cmd","")
                        # produce via shell redirect / here-doc
                        for mm in re.finditer(r'>\s*([^\s|;&]+/\S+|[\w./-]+\.\w+)', cmd):
                            produced.add(mm.group(1))
                        for mm in re.finditer(r'\b(?:cat|tee|cp|mv)\s+(?:>?>?\s*)?([\w./-]+\.\w+)', cmd):
                            produced.add(mm.group(1))
                # some formats store text blocks with tool mentions
                elif c.get("type") == "text":
                    txt = c.get("text","")
                    for mm in re.finditer(r'(?:write_to_file|create_file|editor).*?path[":=\s]+([^\s",}]+)', txt):
                        produced.add(mm.group(1))
    return nedit, sorted(produced)

def peek_one(t):
    sid, user, ip, mc, hint = t
    ls = "ls /home/%s/.cline/data/sessions/%s/%s.messages.json 2>/dev/null" % (user, sid, sid)
    out, rc = sh(ip, ls, 20)
    files = [f for f in out.split() if f]
    if not files:
        return (sid, user, ip, mc, ["NO_FILE"], "?", 0, [])
    fpath = files[0]
    sz, _ = sh(ip, "stat -c %%s %s" % fpath, 20)
    # cap cat to avoid huge files: read first 2MB
    out2, _ = sh(ip, "head -c 2000000 %s" % fpath, 90)
    turns = extract_user_turns(out2)
    if not turns:
        for mm in re.finditer(r'<user_input mode="act">(.+?)</user_input>', out2, re.S):
            s = mm.group(1).strip()
            if s and not s.startswith("<"):
                turns.append(s)
    nedit, produced = assistant_signal(out2)
    return (sid, user, ip, mc, turns, sz.strip(), nedit, produced)

if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(peek_one, t): t for t in TARGETS}
        for fu in concurrent.futures.as_completed(futs):
            try:
                sid, user, ip, mc, turns, sz, nedit, produced = fu.result()
            except Exception as e:
                t = futs[fu]; sid, user, ip, mc, turns, sz, nedit, produced = t[0], t[1], t[2], t[3], ["EXC:"+str(e)], "?", 0, []
            print("### %s | %s@%s | mc=%s | size=%s | nturns=%d | nedit=%d | produced=%s" % (sid, user, ip, mc, sz, len(turns), nedit, produced))
            for i, tn in enumerate(turns[:6]):
                print("  [U#%d] %s" % (i, tn[:400].replace("\n", " ")))
            print("---")
