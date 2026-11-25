#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2-only WaveView runner for P2 real-test re-run (用户令 2026-11-24 08:5x).

Re-runs ONLY the V2 arm (+VQA at :30003, now serving the post-GRPOv2 adapter)
on all 182 code_gen WaveView cases, in a SEPARATE output dir so the existing
V2=17.6% (rft2_adapter_seed11) baseline in /tmp/wv_cg_full is preserved for
paired McNemar comparison. Reuses run_codegen_v0v1v2.py helpers
(setup_workdir / build_prompt / run_pi / grade / summarize / log) unchanged —
only overrides OUTD/RESULTS/LOG/CASES and restricts the arm loop to ["V2"].

Runs on 36.15 (hfeg0tedaap02) from the EDA-Eval-DesignFlow bench dir; VQA bridge
:30003 is exposed to the coding agent via vqa_ask.sh exactly as in the full run.
Resumable (submit.zip / timeout_cache) so a kill/restart never loses sessions.
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_codegen_v0v1v2 as R

BASE = R.BASE
R.OUTD = "/tmp/wv_cg_full_v2grpo2"
R.RESULTS = os.path.join(R.OUTD, "results.json")
R.LOG = os.path.join(R.OUTD, "runner.log")
ARMS = ["V2"]

cases = []
with open(os.path.join(BASE, "EDA-Eval-DesignFlow-WaveView.jsonl")) as f:
    for line in f:
        o = json.loads(line)
        if o.get("audit_category") == "code_gen" and o.get("has_check"):
            cases.append(o["task_id"])
R.CASES = cases


def main():
    import time
    os.makedirs(R.OUTD, exist_ok=True)
    open(R.LOG, "w").close()
    full = R.load_full_records()
    sub = {}
    try:
        sub = {json.loads(l)["task_id"]: json.loads(l)
               for l in open(os.path.join(BASE, "EDA-Eval-DesignFlow-WaveView.jsonl"))}
    except Exception:
        pass
    TCACHE = os.path.join(R.OUTD, "timeout_cache.json")
    tcache = {}
    try:
        tcache = json.load(open(TCACHE))
    except Exception:
        tcache = {}

    def save_tcache():
        try:
            json.dump(tcache, open(TCACHE, "w"), ensure_ascii=False, indent=2)
        except Exception:
            pass

    R.log("V2-ONLY RUNNER start | %d cases x 1 arm (V2) | OUTD=%s | tcache=%d"
          % (len(cases), R.OUTD, len(tcache)))
    rows = []
    for case in cases:
        k_sub = (sub.get(case) or {}).get("k_conditions", "?")
        for arm in ARMS:
            R.log("=== %s / %s (k=%s) ===" % (case, arm, k_sub))
            wd = os.path.join(R.OUTD, case, arm)
            submit_existing = os.path.join(wd, "outputs", "submit.zip")
            key = case + "|" + arm
            if os.path.isfile(submit_existing):
                R.log("  resume: re-grade existing submit.zip (skip pi)")
                g = R.grade(case, arm, wd)
                dt, rc = 0.0, "resume"
            elif key in tcache:
                R.log("  resume: use cached no-submit verdict (skip pi)")
                g = dict(tcache[key])
                g.setdefault("submit_path", None)
                g.setdefault("n_zip_members", 0)
                dt, rc = 0.0, "cached"
            else:
                wd = R.setup_workdir(case, arm, full.get(case, {}))
                prompt = R.build_prompt(case, arm, full.get(case, {}))
                dt, rc = R.run_pi(case, arm, wd, prompt)
                g = R.grade(case, arm, wd)
                if not os.path.isfile(os.path.join(wd, "outputs", "submit.zip")):
                    tcache[key] = {k: v for k, v in g.items() if k not in ("submit_path",)}
                    save_tcache()
            row = {"case_id": case, "arm": arm, "k_conditions": k_sub,
                   "pi_seconds": round(dt, 1), "pi_rc": rc, **g}
            rows.append(row)
            R.log("  VERDICT=%s k=%s/%s n_zip=%s | %s"
                  % (g["verdict"], g["k_pass"], g["k_total"], g["n_zip_members"], g["detail"][:80]))
            with open(R.RESULTS, "w") as fp:
                json.dump({"cases": cases, "rows": rows}, fp, ensure_ascii=False, indent=2)
    summ = R.summarize(rows)
    R.log("SUMMARY: " + json.dumps(summ, ensure_ascii=False))
    with open(R.RESULTS) as fp:
        data = json.load(fp)
    data["summary"] = summ
    with open(R.RESULTS, "w") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=2)
    R.log("V2-ONLY RUNNER done. results=%s" % R.RESULTS)


if __name__ == "__main__":
    main()
