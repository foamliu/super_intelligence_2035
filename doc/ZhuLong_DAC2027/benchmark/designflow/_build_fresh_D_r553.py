#!/usr/bin/env python3
"""Build fresh D-domain-dominant candidate pool for shard D, round #553."""
import json, re, sys

CAND = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/candidates_mc10.tsv"
LEDGER_D = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/trace_ledger_D.tsv"
JSONL_D = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_D.jsonl"
OUT = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/_fresh_D_r553.tsv"

D_KW = {
    "netlist":1, "schematic":1, "cmos":1, "transistor":1, "subckt":1, "spice":1, "hspice":1,
    "spectre":1, "cdl":1, ".sp":1, ".cdl":1, ".scs":1, "inst":1, "device":1, "mos":1,
    "waveform":1, "waveview":1, "fsdb":1, "vec":1, ".awf":1, "wdf":1, ".mt0":1, "vcd":1,
    "eye":1, "jitter":1, "ber":1, "prbs":1,
    "analog":1, "measure":1, ".meas":1, ".param":1, ".lib":1, ".inc":1, ".data":1, ".option":1,
    "pex":1, "rc":1, "corner":1, "pvt":1, "montecarlo":1, "mc":1, "postlayout":1,
    "model":1, "char":1, " characterization":1, "ibis":1, "itf":1,
}
A_KW = {
    "verilog":1, "rtl":1, "systemverilog":1, "sv":1, "uvm":1, "vcs":1, "verdi":1, "ncsim":1,
    "irun":1, "xrun":1, "primetime":1, "pt":1, "innovus":1, "pnr":1, "def":1, "lef":1,
    "synthesis":1, "dc":1, "compile":1, "fpga":1, "dsa":1, "sta":1, "assertion":1, "sva":1,
    "formal":1, "jasper":1,
}
C_KW = {
    "drc":1, "lvs":1, "aether":1, "virtuoso":1, "pcell":1, "layout":1, "calibre":1,
    "assura":1, "pvs":1, "pv":1, "streamout":1, "streamin":1, "gds":1, "oas":1,
    "pg":1, "powergrid":1, "em":1, "antenna":1, "via":1, "routing":1, "route":1,
}

def kw_sum(kw_str, weights):
    total = 0
    for part in kw_str.split(";"):
        part = part.strip()
        if not part: continue
        m = re.match(r"([^:]+):(\d+)", part)
        if not m: continue
        name, cnt = m.group(1).strip().lower(), int(m.group(2))
        for k,w in weights.items():
            if k in name:
                total += cnt*w
                break
    return total

ledger_sids = set()
with open(LEDGER_D) as f:
    for line in f:
        line = line.rstrip("\n")
        if not line: continue
        cols = line.split("\t")
        if len(cols) < 1: continue
        sid = cols[0].strip()
        if sid: ledger_sids.add(sid)

jsonl_sids = set()
with open(JSONL_D) as f:
    for line in f:
        line = line.strip()
        if not line: continue
        try:
            o = json.loads(line)
            ts = o.get("metadata",{}).get("trace_source",{})
            sf = ts.get("session_file","")
            m = re.search(r"(\d+_[a-z0-9]+)", sf)
            if m: jsonl_sids.add(m.group(1))
        except: pass

excluded = ledger_sids | jsonl_sids
print(f"excluded: ledger={len(ledger_sids)} jsonl={len(jsonl_sids)} union={len(excluded)}", file=sys.stderr)

rows = []
with open(CAND) as f:
    header = f.readline()
    for line in f:
        line = line.rstrip("\n")
        if not line: continue
        cols = line.split("\t")
        if len(cols) < 5: continue
        ip, user, sid, mc, kw = cols[0], cols[1], cols[2], int(cols[3]), cols[4]
        if sid in excluded: continue
        d_score = kw_sum(kw, D_KW)
        a_score = kw_sum(kw, A_KW)
        c_score = kw_sum(kw, C_KW)
        total = d_score + a_score + c_score
        if total == 0: continue
        if d_score <= a_score or d_score <= c_score: continue
        if d_score / total < 0.5: continue
        if mc < 10 or mc > 30: continue
        rows.append((mc, d_score, a_score, c_score, ip, user, sid, kw))

rows.sort(key=lambda r: (-r[0], -r[1]))
print(f"fresh D-dominant mc10-30: {len(rows)}", file=sys.stderr)

with open(OUT, "w") as f:
    f.write("mc\td\ta\tc\tip\tuser\tsid\tkeywords\n")
    for r in rows:
        f.write("\t".join(str(x) for x in r) + "\n")
print(f"wrote {OUT}", file=sys.stderr)

print("mc\td\ta\tc\tip\tuser\tsid\tkeywords")
for r in rows[:30]:
    print("\t".join(str(x) for x in r))
