#!/usr/bin/env python3
# r515: constitution-lens candidate computation for shard B (spice_sim/characterization)
# Lens (from r513/r514): sim-tool abs count >=8 + analog sig >=5 + digital noise <40%
import os, re, sys, glob

SUM = "designflow/summary_1113.tsv"
LEDGER = "designflow/trace_ledger_B.tsv"
DEEPREAD_DIR = "designflow/trace_deepreads"

SIM_TOOLS = ["hspice","spectre","finesim","ngspice","siliconsmart","simulator","spice","custom_sim"]
ANALOG_SIG = ["analog","mosfet","opamp","schematic","cascode","spice","rtl","transistor","cmos","diffpair","current_mirror"]
DIGITAL_NOISE = ["verilog","systemverilog","innovus","drc","dc_shell","synthesis","sdc","vivado","yosys","openroad","formality","prime-time","primetime","calibre","lvs"]

def parse_kw(s):
    d = {}
    if not s: return d
    for part in s.split(";"):
        part = part.strip()
        if not part: continue
        if ":" in part:
            k,v = part.rsplit(":",1)
            try: d[k.strip()] = int(v)
            except: pass
    return d

def slug(sf):
    s = sf
    for suf in [".messages.archive.json",".messages.json",".archive.json",".json"]:
        if s.endswith(suf):
            s = s[:-len(suf)]; break
    return s

# load ledger sessions (all statuses -> exclude from fresh)
ledger_sids = set()
if os.path.exists(LEDGER):
    with open(LEDGER) as f:
        for line in f:
            line=line.rstrip("\n")
            if not line: continue
            c = line.split("\t")
            if len(c) >= 1 and c[0]:
                ledger_sids.add(slug(c[0]))

# load deepread slugs
deepread_sids = set()
for p in glob.glob(DEEPREAD_DIR+"/*.md"):
    b = os.path.basename(p)[:-3]
    # filenames like "0ox36_sch2netlist_libdefs_trap.md" or "sid_1794470666600_frplj_..."
    m = re.match(r'^(?:sid_)?([0-9a-z0-9]+?)(?:[_.].*)?$', b)
    # try to extract leading slug token
    toks = b.split("_")
    # heuristic: first token that looks like a slug (alnum, len>=4)
    for t in toks:
        if len(t) >= 4 and re.match(r'^[0-9a-z]+$', t):
            deepread_sids.add(t)
            break

rows = []
with open(SUM) as f:
    header = f.readline()
    for line in f:
        line = line.rstrip("\n")
        if not line: continue
        c = line.split("\t")
        if len(c) < 7: continue
        ip,host,user,sf,mc,kw,tools = c[0],c[1],c[2],c[3],c[4],c[5],c[6]
        try: mc = int(mc)
        except: continue
        if mc < 10: continue
        s = slug(sf)
        # B keyword filter
        if not re.search(r'hspice|finesim|siliconsmart|spectre|ngspice|simulator|spice|custom_sim', kw): continue
        if s in ledger_sids: continue
        d = parse_kw(kw)
        sim_abs = sum(d.get(k,0) for k in SIM_TOOLS)
        analog_abs = sum(d.get(k,0) for k in ANALOG_SIG)
        digital_abs = sum(d.get(k,0) for k in DIGITAL_NOISE)
        total = sum(d.values()) if d else 1
        digital_ratio = digital_abs / total if total else 1
        spice_ratio = sim_abs / total if total else 0
        rows.append({
            "slug": s, "user": user, "host": host, "ip": ip, "mc": mc,
            "sim_abs": sim_abs, "analog_abs": analog_abs, "digital_ratio": digital_ratio,
            "spice_ratio": spice_ratio, "kw": kw, "deepread": s in deepread_sids,
        })

# constitution lens: sim_abs>=8, analog_abs>=5, digital_ratio<0.4
const = [r for r in rows if r["sim_abs"]>=8 and r["analog_abs"]>=5 and r["digital_ratio"]<0.4]
const.sort(key=lambda r: -r["mc"])

print(f"=== r515 constitution-lens (summary_1113.tsv, mc>=10, B-kw, NOT in ledger B) ===")
print(f"total B-kw mc>=10 not-in-ledger: {len(rows)}")
print(f"constitution hits (sim>=8 & analog>=5 & digital<0.4): {len(const)}")
print(f"  of which already deepread: {sum(1 for r in const if r['deepread'])}")
print()
print(f"=== TOP 20 constitution hits (by mc desc) ===")
print(f"{'slug':14} {'mc':>5} {'sim':>4} {'analog':>6} {'dig%':>5} {'spice%':>6} {'deepread':>9} user/host  keywords")
for r in const[:20]:
    print(f"{r['slug']:14} {r['mc']:>5} {r['sim_abs']:>4} {r['analog_abs']:>6} {r['digital_ratio']*100:>4.0f}% {r['spice_ratio']*100:>5.0f}% {'Y' if r['deepread'] else 'n':>9} {r['user']}/{r['host']}  {r['kw'][:80]}")
print()
print(f"=== constitution hits NOT deepread (candidates for this round) ===")
fresh_const = [r for r in const if not r["deepread"]]
print(f"count: {len(fresh_const)}")
for r in fresh_const[:20]:
    print(f"{r['slug']:14} {r['mc']:>5} {r['sim_abs']:>4} {r['analog_abs']:>6} {r['digital_ratio']*100:>4.0f}% {r['spice_ratio']*100:>5.0f}% {r['user']}/{r['host']}  {r['kw'][:90]}")
