#!/usr/bin/env python3
"""R2389: eval pi sympy__sympy-20801 (single instance)."""
import json, subprocess, glob
from pathlib import Path

HERE = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full")
PRED_DIR = HERE / "predictions_glm53"
REPORT_DIR = HERE / "reports"
EVAL_LOG_ROOT = HERE / "logs" / "run_evaluation"
ENRICHED = HERE / "enriched_500.json"
ROUND = "R2389"
harness = "pi"
iid = "sympy__sympy-20801"

merged = PRED_DIR / f"predictions_{harness}_new_{ROUND}.json"
pd = json.loads((PRED_DIR / f"{harness}__{iid}.json").read_text())
if isinstance(pd, dict):
    pd = [pd]
patches = [p for p in pd if (p.get("model_patch") or "").strip()]
merged.write_text(json.dumps(patches, indent=2))
print(f"merged {len(patches)} patches")

run_id = f"verified_full_glm53_{harness}_incr_{ROUND}"
cmd = (f"python3 -m swebench.harness.run_evaluation "
       f"--predictions_path {merged} --dataset_name {ENRICHED} --split test "
       f"--instance_ids {iid} --max_workers 1 --run_id {run_id} --timeout 1800")
print(f"EVAL {iid} -> run_id={run_id}")
proc = subprocess.run(["sg", "docker", "-c", cmd], cwd=str(HERE),
                      capture_output=True, text=True, timeout=2400)
print(f"rc={proc.returncode}")
(HERE / "logs" / f"eval_{run_id}.log").write_text(proc.stdout + "\n[stderr]\n" + proc.stderr)

model = "pi-glm-5.3-flash"
rj = EVAL_LOG_ROOT / run_id / model / iid / "report.json"
if not rj.exists():
    cands = list((EVAL_LOG_ROOT / run_id).glob(f"*/{iid}/report.json"))
    rj = cands[0] if cands else None

cum = json.loads((REPORT_DIR / f"eval_glm53_{harness}.json").read_text())
cum.setdefault("resolved", [])
cum.setdefault("failed", [])
cum.setdefault("infra_or_quota", [])

if rj and rj.exists():
    rep = json.loads(rj.read_text())
    inst = rep.get(iid, rep) if isinstance(rep, dict) else {}
    resolved = inst.get("resolved", False)
    status = "RESOLVED" if resolved else "FAILED"
    print(f"{iid}: {status}")
    b = "resolved" if resolved else "failed"
    cum[b].append(iid)
else:
    print(f"{iid}: NO report.json -> infra")
    cum["infra_or_quota"].append(iid)

cum["n"] = len(cum["resolved"]) + len(cum["failed"]) + len(cum["infra_or_quota"])
cum["resolved_count"] = len(cum["resolved"])
cum["evaluated"] = cum["n"]
cum["total_predictions"] = len(glob.glob(str(PRED_DIR / f"{harness}__*.json")))
real = 0
for f in glob.glob(str(PRED_DIR / f"{harness}__*.json")):
    try:
        d = json.loads(Path(f).read_text())
        if isinstance(d, dict):
            if (d.get("model_patch") or "").strip():
                real += 1
        elif isinstance(d, list):
            if any((p.get("model_patch") or "").strip() for p in d):
                real += 1
    except:
        pass
cum["no_patch"] = cum["total_predictions"] - real
(REPORT_DIR / f"eval_glm53_{harness}.json").write_text(json.dumps(cum, indent=2))
print(f"MERGED -> n={cum['n']} resolved={len(cum['resolved'])} failed={len(cum['failed'])} infra={len(cum['infra_or_quota'])}")
