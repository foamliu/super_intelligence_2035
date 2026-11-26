#!/usr/bin/env python3
"""Peek batch for shard D #318. Run ON .75. Parallel ssh to target machines.
Extract user turns + assistant tool signal (write/create_file, produce files)
to triage A-faithful produce candidates fast.
"""
import json, subprocess, concurrent.futures, re, sys

TARGETS = [
    # (sid, user, ip, mc, domain_hint)
    ("1792995706498_hpd7c", "yongk1li", "10.129.2.12", 79, "netlist"),
    ("1791806895348_xyqtl", "taodu", "10.129.33.138", 77, "netlist/sch"),
    ("1793173193409_mx7xh", "junweix", "10.129.8.224", 77, "analog/hspice"),
    ("1789451741660_7uwtz", "e0016033", "10.129.2.10", 75, "calibre/netlist"),
    ("1788767030730_6azjv", "rongjiez", "10.129.2.11", 74, "netlist"),
    ("1789900684281_lq00u", "rongtaoy", "10.129.2.10", 74, "netlist/cdl/spi"),
    ("1792551168500_xppi3", "zongjiuh", "10.129.32.100", 71, "netlist/analog"),
    ("1791529572460_sao7s", "yanxvwei", "10.129.32.85", 71, "netlist"),
    ("1787646109879_mwyd9", "e0025730", "10.129.8.86", 71, "netlist"),
    ("1792484214005_w1dp0", "zqzhan", "10.129.32.80", 71, "netlist/waveview"),
    ("1789535827580_4fbwo", "mike", "10.129.32.80", 70, "netlist/analog"),
    ("1789630642152_8b8wk", "ghyang", "10.129.2.12", 69, "cmos/netlist/sch"),
    ("1791967421688_xdg5s", "hairuizh", "10.129.35.68", 68, "netlist/sch/pyae"),
    ("1790150666233_ob8f4", "jason17w", "10.129.32.190", 68, "netlist/hspice"),
    ("1793092596941_5j56m", "yanghao", "10.129.2.11", 65, "netlist/hspice/sch"),
    ("1791944864965_ps5ix", "e0039602", "10.129.8.136", 65, "netlist/transistor"),
    ("1792111744261_uxwb5", "e0023936", "10.129.32.75", 64, "netlist/pyae/sch"),
    ("1791940707499_psbg1", "tongni", "10.129.33.245", 64, "aether/calibre/netlist"),
    ("1783653871879_3anqw", "e0025730", "10.129.8.86", 63, "netlist/sch"),
    ("1789453406100_p28m8", "e0017484", "10.129.35.74", 63, "netlist/waveview"),
    ("1790047784806_lsc1e", "simplec", "10.129.2.11", 62, "netlist/calibre"),
    ("1792563679865_57rrw", "e0039602", "10.129.8.136", 60, "netlist"),
    ("1793150705842_rbvi8", "e03179", "10.129.2.11", 59, "netlist/analog/wv"),
    ("1790079870984_56jqu", "jason17w", "10.129.32.190", 59, "netlist"),
    ("1782803363777_e0b5q", "e0025730", "10.129.8.86", 59, "netlist/sch"),
    ("1790064843293_r98dm", "e0042337", "10.129.32.190", 57, "netlist/analog/wv"),
    ("1790057512461_vtz09", "rongtaoy", "10.129.2.10", 57, "netlist/cdl/trans"),
    ("1790216933447_e5opy", "jason17w", "10.129.32.190", 57, "netlist/hspice"),
    ("1789729630634_t5ge3", "davidwu", "10.129.40.209", 57, "sch/pyae/analog"),
    ("1789524301977_lp4xw", "clarawang", "10.129.32.80", 77, "netlist/analog"),
    ("1791612109523_qv65m", "mike", "10.129.32.80", 78, "synopsys/netlist"),
    ("1790128938715_nsf5a", "rongjiez", "10.129.2.11", 66, "waveview/hspice"),
    ("1783084592736_1kipj", "e0014566", "10.129.2.10", 65, "virtuoso/waveview"),
]

def sh(ip, cmd, t=60):
    try:
        out = subprocess.run(["ssh","-o","BatchMode=yes","-o","ConnectTimeout=6",ip,cmd],
            capture_output=True, text=True, timeout=t, stdin=subprocess.DEVNULL)
        return out.stdout, out.returncode
    except Exception:
        return "", 998

PRODUCE_RE = re.compile(r'\.(py|tcl|skill|sv|v|sp|spi|cdl|scs|ckt|cfg|inc|f|deck|net)\b', re.I)
WRITE_TOOLS = re.compile(r'"name"\s*:\s*"(write_to_file|create_file|execute_command|run_command|replace_in_file|insert_content)"')

def analyze(raw):
    data = None
    try: data = json.loads(raw)
    except Exception: return None
    msgs = data.get("messages") if isinstance(data, dict) else data
    if not isinstance(msgs, list): return None
    user_turns = []
    asst_tools = {}
    produce_files = set()
    for m in msgs:
        role = m.get("role"); content = m.get("content")
        if role == "user":
            texts = []
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
                    user_turns.append(s)
        elif role == "assistant":
            # find tool_use blocks
            if isinstance(content, list):
                for c in content:
                    if isinstance(c, dict) and c.get("type") == "tool_use":
                        nm = c.get("name","")
                        asst_tools[nm] = asst_tools.get(nm,0)+1
                        inp = json.dumps(c.get("input",{}), ensure_ascii=False)
                        for mt in PRODUCE_RE.finditer(inp):
                            produce_files.add(mt.group(0).lower())
            # also scan raw for tool names (some formats)
    return user_turns, asst_tools, sorted(produce_files)

def peek_one(t):
    sid, user, ip, mc, hint = t
    ls = "ls /home/%s/.cline/data/sessions/%s/%s.messages.json 2>/dev/null" % (user, sid, sid)
    out, rc = sh(ip, ls, 20)
    files = [f for f in out.split() if f]
    if not files:
        return (sid, user, ip, mc, hint, "NO_FILE", [], {}, [])
    fpath = files[0]
    szo, _ = sh(ip, "stat -c %%s %s" % fpath, 20)
    out2, _ = sh(ip, "cat %s </dev/null" % fpath, 90)
    res = analyze(out2)
    if res is None:
        return (sid, user, ip, mc, hint, "PARSE_FAIL", [], {}, [])
    user_turns, asst_tools, produce_files = res
    return (sid, user, ip, mc, hint, szo.strip(), user_turns, asst_tools, produce_files)

if __name__ == "__main__":
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(peek_one, t): t for t in TARGETS}
        for fu in concurrent.futures.as_completed(futs):
            try:
                sid, user, ip, mc, hint, sz, turns, tools, pf = fu.result()
            except Exception as e:
                tt = futs[fu]; sid = tt[0]; user=tt[1]; ip=tt[2]; mc=tt[3]; hint=tt[4]; sz="EXC"; turns=[]; tools={}; pf=[]
            # produce signal: write_to_file/create_file used AND produce_files present
            writes = tools.get("write_to_file",0)+tools.get("create_file",0)
            sig = "PRODUCE" if (writes>0 and pf) else ("TOOLSONLY" if tools else "NOFILE_EMPTY")
            print("### %s | %s@%s | mc=%s %s | size=%s | nturns=%d | writes=%d | sig=%s | tools=%s | produce=%s" % (
                sid, user, ip, mc, hint, sz, len(turns), writes, sig, ",".join("%s=%d"%k for k in tools.items()) or "-", ",".join(pf) or "-"))
            for i, tn in enumerate(turns[:4]):
                print("  [U#%d] %s" % (i, tn[:380].replace("\n"," ")))
            print("---")
