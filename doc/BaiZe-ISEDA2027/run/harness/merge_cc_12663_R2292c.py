#!/usr/bin/env python3
"""Merge claude-code django-12663 (R2292c) into cumulative."""
import json
from pathlib import Path

HERE = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full")
REPORT_DIR = HERE / "reports"
EVAL_LOG_ROOT = HERE / "logs" / "run_evaluation"

harness = "claude-code"
run_id = "verified_full_glm53_claude-code_incr_R2292c"
model = "claude-code-glm-5.3-flash"
iid = "django__django-12663"

rj = EVAL_LOG_ROOT / run_id / model / iid / "report.json"
rep = json.loads(rj.read_text())
inst = rep.get(iid, rep)
resolved = inst.get("resolved", False)

ef = REPORT_DIR / f"eval_glm53_{harness}.json"
cum = json.loads(ef.read_text())
cum.setdefault("resolved", [])
cum.setdefault("failed", [])
cum.setdefault("infra_or_quota", [])

b = "resolved" if resolved else "failed"
if iid not in cum[b]:
    cum[b].append(iid)
cum["n"] = len(cum["resolved"]) + len(cum["failed"]) + len(cum["infra_or_quota"])
ef.write_text(json.dumps(cum, indent=2))

print(f"claude-code {iid}: {'RESOLVED' if resolved else 'FAILED'}")
print(f"cumulative n={cum['n']} resolved={len(cum['resolved'])} failed={len(cum['failed'])} infra={len(cum['infra_or_quota'])}")
