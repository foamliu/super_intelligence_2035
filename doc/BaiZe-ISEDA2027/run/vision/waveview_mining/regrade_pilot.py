#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-grade the pilot /tmp/wv_cg cases with the FIXED grade() (patched module).
Re-grades every (case,arm) that has a submit.zip; carries over the old row
verbatim for arms that produced no submit.zip (pi timeout -> real fail).
Writes corrected /tmp/wv_cg/results.json and prints a summary.
"""
import json, os, sys

sys.path.insert(0, "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow")
import run_codegen_v0v1v2 as R

OUTD = "/tmp/wv_cg"
old = json.load(open(os.path.join(OUTD, "results.json")))
old_map = {(r["case_id"], r["arm"]): r for r in old["rows"]}

cases = sorted(d for d in os.listdir(OUTD)
               if d.startswith("EDA-Eval-DesignFlow-") and os.path.isdir(os.path.join(OUTD, d)))
rows = []
for case in cases:
    for arm in ["V0", "V1", "V2"]:
        wd = os.path.join(OUTD, case, arm)
        if not os.path.isdir(wd):
            continue
        submit = os.path.join(wd, "outputs", "submit.zip")
        if os.path.isfile(submit):
            g = R.grade(case, arm, wd)
            row = {"case_id": case, "arm": arm,
                   "k_conditions": old_map.get((case, arm), {}).get("k_conditions", "?"),
                   "pi_seconds": old_map.get((case, arm), {}).get("pi_seconds", 0.0),
                   "pi_rc": old_map.get((case, arm), {}).get("pi_rc", "regraded"),
                   **g}
        else:
            row = old_map.get((case, arm), {"case_id": case, "arm": arm,
                                            "verdict": False, "k_pass": 0, "k_total": 0,
                                            "detail": "no submit.zip produced (pi timeout)",
                                            "pi_rc": -99, "pi_seconds": 0.0})
        rows.append(row)

summ = R.summarize(rows)
data = {"cases": cases, "rows": rows, "summary": summ,
        "note": "regraded with fixed grade() (fresh gdir + hidden/) on existing pilot submit.zips"}
with open(os.path.join(OUTD, "results.json"), "w") as fp:
    json.dump(data, fp, ensure_ascii=False, indent=2)
print("regraded %d rows over %d cases" % (len(rows), len(cases)))
print("summary:", json.dumps(summ, ensure_ascii=False))
for r in rows:
    print("  %-42s %s verdict=%s k=%s/%s rc=%s"
          % (r["case_id"].replace("EDA-Eval-DesignFlow-", "")[:40], r["arm"],
             r.get("verdict"), r.get("k_pass", 0), r.get("k_total", 0), r.get("pi_rc")))
