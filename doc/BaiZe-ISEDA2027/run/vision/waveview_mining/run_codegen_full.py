#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Full code_gen WaveView V0/V1/V2 runner — all 182 code_gen cases (resumable).

Chains the SAME logic as run_codegen_v0v1v2.py over every code_gen case in
EDA-Eval-DesignFlow-WaveView.jsonl (audit_category == "code_gen" ∧ has_check).
Reuses the pilot module's functions; only overrides CASES + OUTD so grading,
prompt-building, VQA wiring, and resume semantics stay identical.

Resumable: if <OUTD>/<case>/<arm>/outputs/submit.zip already exists, it is
re-graded and pi is skipped — so the loop can re-invoke this across wakes and
make incremental progress toward the full 182-case V0/V1/V2 comparison the
2026-11-17 16:3x user order demands ("run the full ~192 queue, let V0 vs V1/V2
speak"). Results are written incrementally to <OUTD>/results.json after every
arm, so a kill/restart never loses completed sessions.

Runs on 36.15 (hfeg0tedaap02) from the EDA-Eval-DesignFlow bench dir; VQA
bridges :30001/:30003 are exposed to the coding agent via vqa_ask.sh exactly as
in the pilot (Qwen3.5-2B base / rft2). Model = deepseek-v4-pro-cloud (pi --no-mcp).
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_codegen_v0v1v2 as R

BASE = R.BASE

cases = []
with open(os.path.join(BASE, "EDA-Eval-DesignFlow-WaveView.jsonl")) as f:
    for line in f:
        o = json.loads(line)
        if o.get("audit_category") == "code_gen" and o.get("has_check"):
            cases.append(o["task_id"])

R.CASES = cases
R.OUTD = "/tmp/wv_cg_full"
R.RESULTS = os.path.join(R.OUTD, "results.json")
R.LOG = os.path.join(R.OUTD, "runner.log")

if __name__ == "__main__":
    print("FULL code_gen runner | %d cases x 3 arms | OUTD=%s" % (len(cases), R.OUTD), flush=True)
    R.main()
