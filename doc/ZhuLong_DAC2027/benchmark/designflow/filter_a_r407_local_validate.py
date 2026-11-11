#!/usr/bin/env python3
"""Apply refined A-dominant filter logic locally to cand_A.tsv (25 rows, top A-keyword candidates by mc).
Validates the r407 filter criteria on real data. NOT exhaustive (full summary.tsv lives on .75)."""
import re, sys

CAND = "/nasdata/app.e0031982/code/EDA-Flow-Bench/.cache/tmp_split/cand_A.tsv"
USED = set()
with open("/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/used_sessions.txt") as f:
    for line in f:
        s = line.strip()
        if s: USED.add(s)

A_TOOLS = {"verdi","vcs","dc_shell","design_compiler","formality","innovus",
           "primetime","pt_shell","verilint","xrun","vivado","yosys","openroad",
           "verilog","systemverilog","rtl","sdc"}
BLOCKED = {"tongfanl","e02141"}
ANALOG = {"aether","virtuoso","calibre","lvs","drc","hspice","spectre","finesim",
          "schematic","netlist","analog","skill","waveview","pyaether","layout","pex","cmos","bandgap","mosfet"}

def kw_dict(kw):
    d={}
    for tok in kw.split(';'):
        tok=tok.strip()
        if not tok or ':' not in tok: continue
        name,cnt = tok.rsplit(':',1)
        try: d[name.lower()]=d.get(name.lower(),0)+int(cnt)
        except: pass
    return d

cands=[]
n_in=0; n_mc=0; n_used=0; n_blocked=0; n_weak=0; n_top=0; n_analog=0
with open(CAND) as f:
    for line in f:
        line=line.rstrip('\n')
        if not line: continue
        p=line.split('\t')
        if len(p)<5: continue
        n_in+=1
        mc_str,user,host,sf,kw = p[0],p[2],p[3],p[1],p[4]
        try: mc=int(mc_str)
        except: continue
        if mc<10: n_mc+=1; continue
        anchor=re.sub(r'\.(messages\.)?json$','',sf)
        if anchor in USED: n_used+=1; continue
        if user in BLOCKED: n_blocked+=1; continue
        kd=kw_dict(kw)
        a=sum(v for k,v in kd.items() if k in A_TOOLS)
        c=sum(v for k,v in kd.items() if k in {"calibre","virtuoso","aether","lvs","drc","layout","pex","pexivirtuoso","ipcustom"})
        b=sum(v for k,v in kd.items() if k in {"hspice","finesim","spectre","ngspice","spice","simulator","siliconsmart","custom_sim"})
        n=sum(v for k,v in kd.items() if k in {"netlist","schematic","skill","waveview","analog","cosmos","spectrum","spiros"})
        if a<2*c or a<2*b or a<2*n or a<5: n_weak+=1; continue
        top=sorted(kd.items(), key=lambda x:-x[1])
        top_tool=top[0][0] if top else ""
        if top_tool not in A_TOOLS: n_top+=1; continue
        am=sum(v for k,v in kd.items() if k in ANALOG)
        if am>a: n_analog+=1; continue
        cands.append((mc,anchor,user,host,a,c,b,n,top_tool,kw[:140]))

cands.sort(key=lambda x:-x[0])
print("mc\tanchor\tuser\thost\ta\tc\tb\tn\ttop_tool\tkw")
for c2 in cands:
    print("\t".join(str(x) for x in c2))
print(f"\n# input rows: {n_in}", file=sys.stderr)
print(f"# dropped mc<10: {n_mc}", file=sys.stderr)
print(f"# dropped USED(dup): {n_used}", file=sys.stderr)
print(f"# dropped BLOCKED: {n_blocked}", file=sys.stderr)
print(f"# dropped weak(a<2c/b/n or a<5): {n_weak}", file=sys.stderr)
print(f"# dropped top_tool not A: {n_top}", file=sys.stderr)
print(f"# dropped analog> a: {n_analog}", file=sys.stderr)
print(f"# strict-A fresh candidates: {len(cands)}", file=sys.stderr)
