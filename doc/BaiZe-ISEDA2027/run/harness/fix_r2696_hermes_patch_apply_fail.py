#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Correct R2696: hermes django-14631 & django-14725 are patch-apply failures
(ability), NOT infra.

Evidence (run_instance.log, verified R2693+R2694 eval runs):
  - django-14631: "Patch Apply Failed" — 2/2 hunks in formsets.py reversed
    (previously applied), 1/1 hunk in test_formsets.py reversed.
    EvaluationError raised by swebench harness → no report.json produced.
  - django-14725: 1.2MB degenerate patch touching hundreds of unrelated files
    (gis_tests, i18n, migrations, staticfiles, …) — patch apply failed.
    EvaluationError raised → no report.json produced.

Both are model ability failures (bad patch), not infra.  Move infra->failed
and recompute n.  This also prevents future rounds from wastefully re-eval'ing
them (find_new only re-evals items still in infra_or_quota)."""
import json
from pathlib import Path

REP = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/reports")
HARNESS = "hermes"
CORRECTIONS = ["django__django-14631", "django__django-14725"]

f = REP / f"eval_glm53_{HARNESS}.json"
d = json.loads(f.read_text())
moved = []
for iid in CORRECTIONS:
    if iid in d.get("infra_or_quota", []):
        d["infra_or_quota"].remove(iid)
        moved.append(iid)
    if iid not in d.get("failed", []):
        d.setdefault("failed", []).append(iid)
# dedup failed
d["failed"] = list(dict.fromkeys(d["failed"]))
d["n"] = len(d.get("resolved", [])) + len(d.get("failed", [])) + len(d.get("infra_or_quota", []))
f.write_text(json.dumps(d, indent=2))
print(f"hermes: moved {moved} infra->failed (ability: patch-apply-fail)")
print(f"  resolved={len(d['resolved'])} failed={len(d['failed'])} "
      f"infra={len(d['infra_or_quota'])} n={d['n']}")
print("correction DONE")
