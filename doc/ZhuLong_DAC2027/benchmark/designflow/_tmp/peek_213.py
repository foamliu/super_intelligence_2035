#!/usr/bin/env python3
# Peek first user turns from top candidate cline sessions on .75
# Usage: python3 peek_213.py
# Reads candidates.list (rank, score, match, session, user, host, tools) lines,
# ssh to host, cat /home/<user>/.cline/data/sessions/<anchor>/<anchor>.messages.json | head -c 3MB,
# parse first 3 user turns, dump text.
import sys, re, json, subprocess, os

CANDS = """1	37	271	1791862539977_nwwkg.messages.json	taodu	hfeg0pfn012
2	37	269	1790083095684_oblxr.messages.json	e0014566	hfeg0pkn001
3	37	286	1787625078133_9ryp9.messages.json	haoyut	hfeg0pkn003
4	37	279	1792380407268_opm9y.messages.json	willashi	hfeg0plg55
5	37	274	1792827081154_d810y.messages.json	jackjia	hfeg0plg78
6	36	159	1793091608908_lzt3e.messages.json	e0023936	hfhds201
7	36	216	1792572179617_nvnc3.messages.json	e0022089	hfeg0pkn002
8	36	225	1782905118695_h80lc.messages.json	e0014566	hfeg0pkn001
9	36	217	1790501128558_cd4qp.messages.json	cwei	hfeahpc504
10	36	212	1792980238183_sh05n.messages.json	shwanlai	hfeg0pgn016
11	35	184	1792652163775_i6fn6.messages.json	jcgu	hfeg0pin003
12	35	188	1791463574990_um5we.messages.json	xuebaok	hfhds206
13	35	187	1790061417120_p2n1r.messages.json	miccao	hfeg0plg37
14	35	196	1792552457905_b4dlx.messages.json	zjqiao	hfhds206
15	35	191	1792744504374_xpor0.messages.json	e0044587	hfeg0pkn005
16	35	178	1793161602607_0i3r5.messages.json	my7li	hfeg0pkn004
17	35	165	1790078216880_4g0i9.messages.json	lizwen	hfeg0pkn002
18	35	188	1793150158938_6rvi0.messages.json	michael1l	hfeg0pkn003
19	35	168	1789119944175_j56lm.messages.json	davidwu	hfeg0pjn200
20	35	174	1789731915060_hfm2o.messages.json	davidwu	hfeg0pjn200
21	35	167	1787821853675_z72bi.messages.json	sophiaw	hfeg0plg09
24	33	177	1792137927597_f4kc0.messages.json	jackliu	hfhds209
27	33	186	1792647604577_xv1ip.messages.json	alenxu	hfeg0pkn003
30	33	195	1792201142166_8g8rx.messages.json	jessegao	hfeg0pkn005
31	33	165	1790236124444_8orer.messages.json	lvyy	hfeg0pkn002
34	33	170	1793068687829_k2y0w.messages.json	jiashengz	hfeahpc502
35	33	161	1792111736198_o3hc3.messages.json	chengk	hfeg0pgn022
36	33	172	1791420858846_g3ud6.messages.json	t0002801	hfeg0plg99
37	32	212	1792487428780_fux29.messages.json	e0029308	hfeg0pkn001
40	31	182	1791965857356_a7j5y.messages.json	haooy	hfeg0pkn004
"""

# Build IP lookup from summary.tsv: anchor -> ip
SUMMARY = "/home/t0002965/log/ssh_eda_search_20261028_174426/summary.tsv"
IP_MAP = {}
with open(SUMMARY) as f:
    f.readline()
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 7: continue
        ip, host, user, sf = parts[0], parts[1], parts[2], parts[3]
        anchor = re.sub(r"\.messages\.json$","",sf)
        IP_MAP[anchor] = ip

def extract_user_turns(raw):
    """Parse messages.json dict+messages+content-list+user_input wrapper."""
    try:
        d = json.loads(raw)
    except:
        return None
    msgs = d.get("messages") if isinstance(d, dict) else None
    if msgs is None and isinstance(d, list):
        msgs = d
    if not isinstance(msgs, list):
        return None
    turns = []
    for m in msgs:
        if not isinstance(m, dict): continue
        if m.get("role") != "user": continue
        c = m.get("content")
        text = ""
        if isinstance(c, str):
            text = c
        elif isinstance(c, list):
            for part in c:
                if isinstance(part, dict) and part.get("type") == "text":
                    text += part.get("text","")
                elif isinstance(part, str):
                    text += part
        # strip user_input wrapper
        mm = re.search(r'<user_input[^>]*>(.*?)</user_input>', text, re.S)
        if mm:
            text = mm.group(1)
        text = text.strip()
        # skip empty / context_summary / tool_result-only
        if not text: continue
        if text.startswith("<context_summary>") or text.startswith("<environment_details") or text.startswith("<tool_result"): continue
        if text.startswith("Context summary") or text.startswith("[metadata") or text.startswith("Cline") : continue
        turns.append(text[:1200])
        if len(turns) >= 3: break
    return turns

def ssh_peek(host, user, anchor):
    ip = IP_MAP.get(anchor, "10.129.32.75")
    path = f"/home/{user}/.cline/data/sessions/{anchor}/{anchor}.messages.json"
    cmd = ["ssh","-o","BatchMode=yes","-o","ConnectTimeout=8","-o","StrictHostKeyChecking=no","-q",ip,f"cat {path} </dev/null 2>/dev/null | head -c 3145728"]
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=20)
        return p.stdout.decode("utf-8","replace")
    except Exception as e:
        return ""

for line in CANDS.strip().splitlines():
    parts = line.split("\t")
    if len(parts) < 6: continue
    rank, score, mc, sf, user, host = parts
    anchor = re.sub(r"\.messages\.json$","",sf)
    print(f"\n=== rank={rank} mc={mc} user={user} host={host} anchor={anchor} ===")
    raw = ssh_peek(host, user, anchor)
    if not raw:
        print("(no data / ssh fail / file missing)")
        continue
    turns = extract_user_turns(raw)
    if not turns:
        print(f"(raw size {len(raw)} but no user turns parsed)")
        # dump first 300 chars
        print("HEAD:", raw[:300].replace("\n","\\n"))
        continue
    for i, t in enumerate(turns):
        print(f"  U#{i}: {t[:600]}")
