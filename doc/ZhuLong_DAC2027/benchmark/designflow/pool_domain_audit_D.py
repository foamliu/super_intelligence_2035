#!/usr/bin/env python3
"""
pool_domain_audit_D.py — shard D 可造候选池 domain 抽核 (r864)

背景：r863 发现 8n60f 跨 shard 域误分类（D ledger 标 analog_context，实为 B spice_sim）。
本脚本对 pool_reaudit_D.tsv 中所有「可造*」候选，用 scan summary 的 keyword 分布
重新判定真实域归属，标出可能误分类到他 shard 的候选，供造题前抽核。

输出：designflow/pool_domain_audit_D.tsv
列：session | user | host | mc | ledger_domain | kw_D | kw_A | kw_B | kw_C | real_domain | verdict | reason
verdict: D-confirm / lean-A / lean-B / lean-C / cross-shard-suspect / unclassifiable
"""
import csv, sys, os
from collections import defaultdict

BENCH = os.path.dirname(os.path.abspath(__file__))
POOL = os.path.join(BENCH, "pool_reaudit_D.tsv")
SUMMARY = os.path.join(BENCH, "summary_1115_081559.tsv")
OUT = os.path.join(BENCH, "pool_domain_audit_D.tsv")

# keyword -> shard signal mapping (rough; overlap acknowledged)
# D = netlist/schematic/waveform/analog
# A = digital/verification/pnr_signoff/eda_other
# B = spice_sim/characterization
# C = physical_verify/layout_virtuoso/layout_aether/pg_layout
KW_SHARD = {
    # D
    "netlist": "D", "schematic": "D", ".cdl": "D", "cdl": "D",
    "cellview": "D", "waveform": "D", "fsdb": "D", "waveview": "D",
    "analog": "D", "transistor": "D", "cmos": "D", "diffpair": "D",
    "spice": "D",  # spice netlist context is D; pure hspice sim is B (handled by hspice/finesim)
    # A
    "verilog": "A", "rtl": "A", "primetime": "A", "tempus": "A",
    "synthesis": "A", "xcelium": "A", "irun": "A", "vcs": "A",
    "ncsim": "A", "ncelab": "A", "systemverilog": "A", "sv": "A",
    "formality": "A", "conformal": "A", "lec": "A",
    # B
    "hspice": "B", "finesim": "B", "spectre": "B", "corner": "B",
    "monte": "B", "montecarlo": "B", "characterization": "B", "char": "B",
    "measure": "B", ".meas": "B", "dcop": "B", "ac": "B", "tran": "B",
    # C
    "drc": "C", "lvs": "C", "calibre": "C", "pex": "C", "gds": "C",
    "layout": "C", "virtuoso": "C", "aether": "C", "pdk": "C",
    "techfile": "C", "pcell": "C", "via": "C", "metal": "C",
    "pyaether": "C",  # aether automation -> C (layout_aether)
}

def norm_sess(s):
    if not s: return ""
    s = s.strip()
    for suf in (".messages.json", ".messages.archive", ".json"):
        if s.endswith(suf):
            s = s[:-len(suf)]
    return s

def parse_kw(kw_field):
    """parse 'aether:266;virtuoso:101;...' -> {kw: count}"""
    out = {}
    if not kw_field: return out
    for tok in kw_field.replace(",", ";").split(";"):
        tok = tok.strip()
        if not tok: continue
        if ":" in tok:
            k, v = tok.rsplit(":", 1)
            try:
                out[k.strip().lower()] = int(v)
            except ValueError:
                out[k.strip().lower()] = 1
        else:
            out[tok.lower()] = 1
    return out

def shard_scores(kw):
    sc = defaultdict(int)
    for k, v in kw.items():
        sh = KW_SHARD.get(k.lower())
        if sh:
            sc[sh] += v
    return sc

def classify(ledger_domain, sc):
    total = sum(sc.values())
    D, A, B, C = sc.get("D",0), sc.get("A",0), sc.get("B",0), sc.get("C",0)
    if total == 0:
        return "unclassifiable", "no mapped keywords"
    dfrac = D/total
    # dominant shard
    dom = max(["D","A","B","C"], key=lambda s: sc.get(s,0))
    domfrac = sc.get(dom,0)/total
    reason = f"D={D} A={A} B={B} C={C} total={total} dom={dom}({domfrac:.0%})"
    # verdict
    if dom == "D" and dfrac >= 0.4:
        return "D-confirm", reason
    if dom == "D" and dfrac >= 0.30:
        return "D-confirm(weak)", reason
    # D is not dominant
    if dom in ("A","B","C") and domfrac >= 0.45 and dfrac < 0.25:
        return f"cross-shard-suspect(lean-{dom})", reason
    if dom in ("A","B","C") and domfrac >= 0.40:
        return f"lean-{dom}", reason
    return "mixed", reason

def main():
    # load summary
    summ = {}
    with open(SUMMARY) as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            sess = norm_sess(row.get("session_file",""))
            if sess:
                summ[sess] = {
                    "user": row.get("user",""),
                    "host": row.get("host",""),
                    "ip": row.get("ip",""),
                    "mc": row.get("match_count",""),
                    "keywords": row.get("keywords",""),
                }
    print(f"loaded summary: {len(summ)} sessions", file=sys.stderr)

    # load pool, filter 可造*
    rows_out = []
    n_pool = 0
    n_matched = 0
    n_miss = 0
    verdict_counts = defaultdict(int)
    with open(POOL) as f:
        r = csv.reader(f, delimiter="\t")
        headers = next(r)
        for row in r:
            if len(row) < 8: continue
            sess, user, host, mc, dom, old, new, form = row[:8]
            if not new.startswith("可造"): continue
            n_pool += 1
            sess_n = norm_sess(sess)
            # find keywords
            kw_field = ""
            sr = summ.get(sess_n)
            if not sr:
                # try with .messages.json
                sr = summ.get(sess_n + ".messages.json")
            if sr:
                kw_field = sr["keywords"]
                user = user or sr["user"]
                host = host or sr["host"]
                mc = mc or sr["mc"]
                n_matched += 1
            else:
                n_miss += 1
            kw = parse_kw(kw_field)
            sc = shard_scores(kw)
            real_dom, reason = classify(dom, sc)
            verdict_counts[real_dom] += 1
            rows_out.append([sess, user, host, mc, dom,
                             sc.get("D",0), sc.get("A",0), sc.get("B",0), sc.get("C",0),
                             real_dom, reason])

    # write
    with open(OUT, "w") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["session","user","host","mc","ledger_domain",
                    "kw_D","kw_A","kw_B","kw_C","verdict","reason"])
        w.writerows(rows_out)
    print(f"pool 可造*: {n_pool} matched={n_matched} miss={n_miss}", file=sys.stderr)
    print("verdict counts:", file=sys.stderr)
    for k,v in sorted(verdict_counts.items(), key=lambda x:-x[1]):
        print(f"  {k}: {v}", file=sys.stderr)
    print(f"written {OUT} ({len(rows_out)} rows)", file=sys.stderr)

if __name__ == "__main__":
    main()
