#!/usr/bin/env python3
"""R2390: manually parse django-15572 for claude-code + run pi eval for sympy-20916."""
import json, subprocess, glob, os
from pathlib import Path

HERE = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full")
PRED_DIR = HERE / "predictions_glm53"
REPORT_DIR = HERE / "reports"
EVAL_LOG_ROOT = HERE / "logs" / "run_evaluation"
ENRICHED = HERE / "enriched_500.json"
ROUND = "R2390"

def load_pred(iid_file):
    try:
        d = json.loads(iid_file.read_text())
    except Exception:
        return []
    if isinstance(d, dict):
        d = [d]
    return [p for p in d if (p.get("model_patch") or "").strip()]

def count_real(harness):
    return sum(1 for f in glob.glob(str(PRED_DIR / f"{harness}__*.json")) if load_pred(Path(f)))

def update_eval_json(harness, iid, run_id, resolved):
    ef = REPORT_DIR / f"eval_glm53_{harness}.json"
    cum = json.loads(ef.read_text())
    cum.setdefault("resolved", [])
    cum.setdefault("failed", [])
    cum.setdefault("infra_or_quota", [])
    if iid not in cum["resolved"] and iid not in cum["failed"] and iid not in cum["infra_or_quota"]:
        b = "resolved" if resolved else "failed"
        cum[b].append(iid)
        print(f"  Added {iid} to {b}")
    else:
        print(f"  {iid} already in eval JSON, skipping")
    cum["n"] = len(cum["resolved"]) + len(cum["failed"]) + len(cum["infra_or_quota"])
    cum["resolved_count"] = len(cum["resolved"])
    cum["evaluated"] = cum["n"]
    cum["total_predictions"] = len(glob.glob(str(PRED_DIR / f"{harness}__*.json")))
    cum["no_patch"] = cum["total_predictions"] - count_real(harness)
    ef.write_text(json.dumps(cum, indent=2))
    print(f"  {harness}: n={cum['n']} resolved={cum['resolved_count']} failed={len(cum['failed'])} infra={len(cum['infra_or_quota'])}")

# Step 1: Parse django-15572 for claude-code
print("=== Step 1: Parse claude-code django-15572 ===")
cc_run_id = "verified_full_glm53_claude-code_incr_R2390"
rj = EVAL_LOG_ROOT / cc_run_id / "claude-code-glm-5.3-flash" / "django__django-15572" / "report.json"
if rj.exists():
    rep = json.loads(rj.read_text())
    inst = rep.get("django__django-15572", rep) if isinstance(rep, dict) else {}
    resolved = inst.get("resolved", False)
    print(f"  django-15572: resolved={resolved}")
    update_eval_json("claude-code", "django__django-15572", cc_run_id, resolved)
else:
    print("  ERROR: report.json not found for django-15572")

# Step 2: Run pi eval for sympy-20916
print("\n=== Step 2: Run pi eval for sympy-20916 ===")
pi_iid = "sympy__sympy-20916"
pi_run_id = f"verified_full_glm53_pi_incr_{ROUND}"
merged = PRED_DIR / f"predictions_pi_new_{ROUND}.json"
preds = load_pred(PRED_DIR / f"pi__{pi_iid}.json")
merged.write_text(json.dumps(preds, indent=2))
print(f"  merged {len(preds)} patches")
cmd = (f"python3 -m swebench.harness.run_evaluation "
       f"--predictions_path {merged} --dataset_name {ENRICHED} --split test "
       f"--instance_ids {pi_iid} --max_workers 1 "
       f"--run_id {pi_run_id} --timeout 1800")
print(f"  EVAL {pi_iid} -> run_id={pi_run_id}")
proc = subprocess.run(["sg", "docker", "-c", cmd], cwd=str(HERE),
                      capture_output=True, text=True, timeout=2400)
print(f"  eval rc={proc.returncode}")
(HERE / "logs" / f"eval_{pi_run_id}.log").write_text(proc.stdout + "\n[stderr]\n" + proc.stderr)

# Parse pi result
rj = EVAL_LOG_ROOT / pi_run_id / "pi-glm-5.3-flash" / pi_iid / "report.json"
if not rj.exists():
    cands = list((EVAL_LOG_ROOT / pi_run_id).glob(f"*/{pi_iid}/report.json"))
    rj = cands[0] if cands else None
if rj and rj.exists():
    rep = json.loads(rj.read_text())
    inst = rep.get(pi_iid, rep) if isinstance(rep, dict) else {}
    resolved = inst.get("resolved", False)
    print(f"  {pi_iid}: resolved={resolved}")
    update_eval_json("pi", pi_iid, pi_run_id, resolved)
else:
    print(f"  ERROR: report.json not found for {pi_iid}")
    update_eval_json("pi", pi_iid, pi_run_id, False)

print("\n=== R2390 manual parse+eval done ===")
