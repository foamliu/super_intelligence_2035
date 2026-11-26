#!/usr/bin/env python3
"""Local refined-A filter (r430). Uses candidates_mc10.tsv + 4-shard used set.
Avoids .75 awk line-length issues. 4-shard aware (P-004 fix)."""
import re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
CANDS = os.path.join(HERE, "candidates_mc10.tsv")
USED_PATH = os.path.join(HERE, "_used_4shard_current.txt")

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

def norm(sf):
    return re.sub(r'\.(messages\.)?json$','',sf)

cands=[]
with open(CANDS) as f:
    header=f.readline()
    for line in f:
        line=line.rstrip('\n')
        if not line: continue
        p=line.split('\t')
        if len(p)<5: continue
        ip,user,sf,mc,kw = p[0],p[1],p[2],p[3],p[4]
        try: mc=int(mc)
        except: continue
        if mc<10: continue
        anchor=norm(sf)
        if anchor in USED: continue
        if user in BLOCKED_USERS: continue
        kd=kw_dict(kw)
        a_tot=sum(v for k,v in kd.items() if k in A_TOOLS)
        c_tot=sum(v for k,v in kd.items() if k in {"calibre","virtuoso","aether","lvs","drc","layout","pex","pexivirtuoso","ipcustom"})
        b_tot=sum(v for k,v in kd.items() if k in {"hspice","finesim","spectre","ngspice","spice","simulator","siliconsmart","custom_sim"})
        n_tot=sum(v for k,v in kd.items() if k in {"netlist","schematic","skill","waveview","analog","cosmos","spectrum","spiros"})
        am=sum(v for k,v in kd.items() if k in ANALOG_MARKERS)
        cands.append(dict(mc=mc,anchor=anchor,user=user,ip=ip,a_tot=a_tot,
                          c_tot=c_tot,b_tot=b_tot,n_tot=n_tot,am=am,
                          top_tool=sorted(kd.items(),key=lambda x:-x[1])[0][0] if kd else "",
                          kw=kw[:160]))

# strict: top_tool in A_TOOLS + a>2c/b/n + a>=20 + am<=a
strict=[c for c in cands if c["top_tool"] in A_TOOLS and c["a_tot"]>=20
        and c["a_tot"]>2*c["c_tot"] and c["a_tot"]>2*c["b_tot"] and c["a_tot"]>2*c["n_tot"]
        and c["am"]<=c["a_tot"]]
# relaxed: top_tool in A_TOOLS + a>each + a>=20
relaxed=[c for c in cands if c["top_tool"] in A_TOOLS and c["a_tot"]>=20
         and c["a_tot"]>c["c_tot"] and c["a_tot"]>c["b_tot"] and c["a_tot"]>c["n_tot"]]
strict.sort(key=lambda x:-x["mc"])
relaxed.sort(key=lambda x:-x["mc"])
print("mc\tanchor\tuser\tip\ta_tot\tc_tot\tb_tot\tn_tot\ttop_tool\tkw")
print("# STRICT (a>2c/b/n, a>=20, top in A_TOOLS, 4-shard-fresh):", len(strict))
for c in strict[:30]:
    print("\t".join(str(x) for x in [c["mc"],c["anchor"],c["user"],c["ip"],c["a_tot"],c["c_tot"],c["b_tot"],c["n_tot"],c["top_tool"],c["kw"]]))
print("# RELAXED (a>each, a>=20):", len(relaxed))
for c in relaxed[:10]:
    print("\t".join(str(x) for x in [c["mc"],c["anchor"],c["user"],c["ip"],c["a_tot"],c["c_tot"],c["b_tot"],c["n_tot"],c["top_tool"],c["kw"]]))
