#!/usr/bin/env python3
"""r456 local A-dominant filter. Reads intact summary_1109.tsv + 4-shard exclusion.
Avoids corrupted candidates_mc10.tsv. Cross-shard dedup via _excl_4shard_r456.txt."""
import re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
SUMMARY = os.path.join(HERE, "summary_1109.tsv")
USED_PATH = os.path.join(HERE, "_excl_4shard_r456.txt")

USED = set()
USED_BARE = set()
with open(USED_PATH) as f:
    for line in f:
        a = line.strip()
        if not a: continue
        USED.add(a)
        if '_' in a:
            USED_BARE.add(a.rsplit('_',1)[-1])
        else:
            USED_BARE.add(a)

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

def norm(sf):
    return re.sub(r'\.(messages\.)?json$','',sf)

cands=[]
seen_anchor=set()
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
        anchor=norm(sf)
        if anchor in seen_anchor: continue   # dedup across hosts
        seen_anchor.add(anchor)
        if anchor in USED: continue
        bare=anchor.rsplit('_',1)[-1]
        if bare in USED_BARE: continue
        if user in BLOCKED_USERS: continue
        kd=kw_dict(kw)
        a_tot=sum(v for k,v in kd.items() if k in A_TOOLS)
        c_tot=sum(v for k,v in kd.items() if k in {"calibre","virtuoso","aether","lvs","drc","layout","pex","pexivirtuoso","ipcustom"})
        b_tot=sum(v for k,v in kd.items() if k in {"hspice","finesim","spectre","ngspice","spice","simulator","siliconsmart","custom_sim"})
        n_tot=sum(v for k,v in kd.items() if k in {"netlist","schematic","skill","waveview","analog","cosmos","spectrum","spiros"})
        am=sum(v for k,v in kd.items() if k in ANALOG_MARKERS)
        top_tool=sorted(kd.items(),key=lambda x:-x[1])[0][0] if kd else ""
        cands.append(dict(mc=mc,anchor=anchor,user=user,host=host,a_tot=a_tot,
                          c_tot=c_tot,b_tot=b_tot,n_tot=n_tot,am=am,
                          top_tool=top_tool,kw=kw[:140]))

# strict: top_tool in A_TOOLS + a>2c/b/n + a>=15 + am<=a
strict=[c for c in cands if c["top_tool"] in A_TOOLS and c["a_tot"]>=15
        and c["a_tot"]>2*c["c_tot"] and c["a_tot"]>2*c["b_tot"] and c["a_tot"]>2*c["n_tot"]
        and c["am"]<=c["a_tot"]]
# relaxed: top_tool in A_TOOLS + a>each + a>=15
relaxed=[c for c in cands if c["top_tool"] in A_TOOLS and c["a_tot"]>=15
         and c["a_tot"]>c["c_tot"] and c["a_tot"]>c["b_tot"] and c["a_tot"]>c["n_tot"]]
strict.sort(key=lambda x:-x["mc"])
relaxed.sort(key=lambda x:-x["mc"])
print("mc\tanchor\tuser\thost\ta_tot\tc_tot\tb_tot\tn_tot\ttop_tool\tkw")
print("# STRICT (top in A_TOOLS, a>2c/b/n, a>=15, 4-shard-fresh):", len(strict))
for c in strict[:40]:
    print("\t".join(str(x) for x in [c["mc"],c["anchor"],c["user"],c["host"],c["a_tot"],c["c_tot"],c["b_tot"],c["n_tot"],c["top_tool"],c["kw"]]))
print("# RELAXED (top in A_TOOLS, a>each, a>=15):", len(relaxed))
for c in relaxed[:15]:
    print("\t".join(str(x) for x in [c["mc"],c["anchor"],c["user"],c["host"],c["a_tot"],c["c_tot"],c["b_tot"],c["n_tot"],c["top_tool"],c["kw"]]))
