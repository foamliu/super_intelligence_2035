#!/usr/bin/env python3
"""Parse codex R2292 pytest-6202 result and merge into cumulative."""
import json
from pathlib import Path

HERE = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full")
REPORT_DIR = HERE / "reports"
EVAL_LOG_ROOT = HERE / "logs" / "run_evaluation"
ROUND = "R2292"
MODEL_SUFFIX = "glm-5.3-flash"

harness = "codex"
disp_h = "codex"
run_id = f"verified_full_glm53_{harness}_incr_{ROUND}"
model = f"{disp_h}-{MODEL_SUFFIX}"
iid = "pytest-dev__pytest-6202"

# Read report.json
rj = EVAL_LOG_ROOT / run_id / model / iid / "report.json"
rep = json.loads(rj.read_text())
inst = rep.get(iid, rep)
resolved = inst.get("resolved", False)

# Merge into cumulative
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

# Write per-round result
pr = {"harness": disp_h, "run_id": run_id, "round": ROUND, "n": 1,
      "resolved": [iid] if resolved else [], "failed": [] if resolved else [iid], "infra_or_quota": []}
pf = HERE / f"{disp_h}-{MODEL_SUFFIX}.verified_full_glm53_{harness}_incr_{ROUND}.json"
pr["n"] = len(pr["resolved"]) + len(pr["failed"])
# Note: this only has pytest-6202; pytest-7205 will be added when eval'd
pf.write_text(json.dumps(pr, indent=2))

print(f"codex {iid}: {'RESOLVED' if resolved else 'FAILED'}")
print(f"cumulative n={cum['n']} resolved={len(cum['resolved'])} failed={len(cum['failed'])} infra={len(cum['infra_or_quota'])}")
