#!/usr/bin/env python3
"""Shard D fresh candidate filter for r624. mc>=10, D-keyword dominant, 4-shard ledger exclusion."""
import re, sys, os

CAND = "candidates_mc10.tsv"
OUT  = "_cand_D_r624.tsv"

# 4-shard ledger union exclusion
excl = set()
for sh in ["A","B","C","D"]:
    p = f"trace_ledger_{sh}.tsv"
    if os.path.exists(p):
        with open(p) as f:
            for line in f:
                c = line.rstrip("\n").split("\t")
                if c and c[0].strip():
                    s = c[0].strip()
                    excl.add(s)
                    for suf in (".messages.json",".json",".messages.archive"):
                        if s.endswith(suf): excl.add(s[:-len(suf)])
print(f"excl union: {len(excl)}", file=sys.stderr)

# D-core keywords (for d_ratio): analog_context + schematic_netlist + waveform domains
D_CORE = ["netlist","schematic","analog","waveview","waveform","fsdb","hspice","spectre",
          "spice",".sp",".cdl",".scs","cmos","transistor","subckt","mos",".meas",".param",
          ".lib",".inc","montecarlo","pex","corner","pvt","char","itf","vcd","eye","jitter",
          "ber","prbs","vec",".awf","wdf",".mt0","spectre","cdl","inst","device","measure"]
# D-keyword gate (must match at least one to be D-domain candidate) - mirrors awk regex
D_GATE = ["waveview","cosmos","skill","netlist","spiros","spectrum","analog","schematic"]

def kw_parse(kw_str):
    d = {}
    for part in kw_str.split(";"):
        part = part.strip()
        if not part: continue
        m = re.match(r"([^:]+):(\d+)", part)
        if m: d[m.group(1).strip().lower()] = int(m.group(2))
    return d

rows = []
with open(CAND) as f:
    header = f.readline()
    for line in f:
        line = line.rstrip("\n")
        if not line: continue
        c = line.split("\t")
        if len(c) < 5: continue
        ip, user, sid, mc, kw = c[0], c[1], c[2], int(c[3]), c[4]
        if mc < 10: continue
        s2 = sid
        for suf in (".messages.json",".json",".messages.archive"):
            if s2.endswith(suf): s2 = s2[:-len(suf)]
        if sid in excl or s2 in excl: continue
        kwlow = kw.lower()
        if not any(g in kwlow for g in D_GATE): continue
        kwd = kw_parse(kw)
        d_core = sum(v for k,v in kwd.items() if any(dc in k for dc in D_CORE))
        total = sum(kwd.values()) or 1
        d_ratio = d_core / total
        rows.append((mc, d_ratio, sid, user, ip, kw, total))

# sort by d_ratio desc (r623 approach: d_ratio surfaces low-mc high-D-density), then mc desc
rows.sort(key=lambda r: (-r[1], -r[0]))
with open(OUT, "w") as f:
    f.write("mc\td_ratio\tsid\tuser\tip\tkeywords\ttotal_kw\n")
    for mc, dr, sid, user, ip, kw, tot in rows:
        f.write(f"{mc}\t{dr:.3f}\t{sid}\t{user}\t{ip}\t{kw}\t{tot}\n")
print(f"wrote {OUT}: {len(rows)} fresh D candidates", file=sys.stderr)
# print top 20 by d_ratio, and also a low-mc band view
print("=== TOP 20 by d_ratio ===", file=sys.stderr)
for r in rows[:20]:
    print(f"mc={r[0]} dr={r[1]:.2f} tot={r[6]} {r[2]} {r[3]}@{r[4]} {r[5][:60]}", file=sys.stderr)
print("=== mc 10-50 band, top 15 by d_ratio ===", file=sys.stderr)
low = [r for r in rows if 10 <= r[0] <= 50][:15]
for r in low:
    print(f"mc={r[0]} dr={r[1]:.2f} tot={r[6]} {r[2]} {r[3]}@{r[4]} {r[5][:60]}", file=sys.stderr)
