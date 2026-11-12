#!/usr/bin/env python3
"""Refined A-dominant filter for shard A candidates (r412).
Reads USED set from designflow/_used_4shard_r412.txt (4-shard ledger anchors).
Designed to run on .75 against the 11/09 scan summary.tsv.
"""
import re, sys, os

SUMMARY = "/home/t0002965/log/ssh_eda_search_20261109_224902/summary.tsv"
USED_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_used_4shard_r412.txt")

USED = set()
with open(USED_PATH) as f:
    for line in f:
        a = line.strip()
        if a:
            USED.add(a)

A_TOOLS = {"verdi","vcs","dc_shell","design_compiler","formality","innovus",
           "primetime","pt_shell","verilint","xrun","vivado","yosys","openroad",
           "verilog","systemverilog","rtl","sdc"}

BLOCKED_USERS = {"tongfanl","e02141"}
ANALOG_MARKERS = {"aether","virtuoso","calibre","lvs","drc","hspice","spectre",
                  "finesim","schematic","netlist","analog","skill","waveview",
                  "pyaether","layout","pex","cmos","bandgap","mosfet"}

def kw_dict(kw):
    d={}
    for tok in kw.split(';'):
        tok=tok.strip()
        if not tok: continue
        if ':' in tok:
            name,cnt = tok.rsplit(':',1)
            try: d[name.lower()]=d.get(name.lower(),0)+int(cnt)
            except: pass
    return d

cands=[]
with open(SUMMARY) as f:
    header=f.readline()
    for line in f:
        line=line.rstrip('\n')
        if not line: continue
        p=line.split('\t')
        if len(p)<6: continue
        ip,host,user,sf,mc,kw = p[0],p[1],p[2],p[3],p[4],p[5]
        try: mc=int(mc)
        except: continue
        if mc<10: continue
        anchor=re.sub(r'\.(messages\.)?json$','',sf)
        if anchor in USED: continue
        if user in BLOCKED_USERS: continue
        kd=kw_dict(kw)
        a_tot=sum(v for k,v in kd.items() if k in A_TOOLS)
        c_tot=sum(v for k,v in kd.items() if k in {"calibre","virtuoso","aether","lvs","drc","layout","pex","pexivirtuoso","ipcustom"})
        b_tot=sum(v for k,v in kd.items() if k in {"hspice","finesim","spectre","ngspice","spice","simulator","siliconsmart","custom_sim"})
        n_tot=sum(v for k,v in kd.items() if k in {"netlist","schematic","skill","waveview","analog","cosmos","spectrum","spiros"})
        if a_tot < 2*c_tot: continue
        if a_tot < 2*b_tot: continue
        if a_tot < 2*n_tot: continue
        if a_tot < 5: continue
        top=sorted(kd.items(), key=lambda x:-x[1])
        top_tool=top[0][0] if top else ""
        if top_tool not in A_TOOLS: continue
        am=sum(v for k,v in kd.items() if k in ANALOG_MARKERS)
        if am > a_tot: continue
        cands.append((mc,anchor,user,host,a_tot,c_tot,b_tot,n_tot,top_tool,kw[:160]))

cands.sort(key=lambda x:-x[0])
print("mc\tanchor\tuser\thost\ta_tot\tc_tot\tb_tot\tn_tot\ttop_tool\tkw")
for c in cands[:50]:
    print("\t".join(str(x) for x in c))
print("# total strict-A fresh candidates:", len(cands), file=sys.stderr)
