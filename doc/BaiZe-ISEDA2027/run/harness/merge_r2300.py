#!/usr/bin/env python3
"""R2300: merge cline django-11490 (report.json already exists) + run+merge cc django-13417."""
import json, subprocess, os
from pathlib import Path

HERE = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full")
PRED_DIR = HERE / "predictions_glm53"
REP = HERE / "reports"
EVAL_LOG_ROOT = HERE / "logs" / "run_evaluation"
ENRICHED = HERE / "enriched_500.json"
ROUND = "R2300"
TIMEOUT_EVAL = 1800
DISPLAY = {"cline-patched": "cline", "deepseek-harness": "deepseek"}

def disp(h): return DISPLAY.get(h, h)

def load_pred(f):
    d = json.loads(f.read_text())
    if isinstance(d, dict): d = [d]
    return [p for p in d if (p.get("model_patch") or "").strip()]

def merge_existing(harness, iid, run_id):
    """Merge from an already-existing report.json (no re-eval)."""
    model = f"{disp(harness)}-glm-5.3-flash"
    rj = EVAL_LOG_ROOT / run_id / model / iid / "report.json"
    if not rj.exists():
        cands = list((EVAL_LOG_ROOT / run_id).glob(f"*/{iid}/report.json"))
        rj = cands[0] if cands else None
    ef = REP / f"eval_glm53_{harness}.json"
    cum = json.loads(ef.read_text())
    cum.setdefault("resolved", []); cum.setdefault("failed", []); cum.setdefault("infra_or_quota", [])
    if rj is None or not rj.exists():
        cum["infra_or_quota"].append(iid)
        print(f"  {iid}: NO report.json -> infra")
    else:
        rep = json.loads(rj.read_text())
        inst = rep.get(iid, rep) if isinstance(rep, dict) else {}
        resolved = inst.get("resolved", False)
        b = "resolved" if resolved else "failed"
        if iid not in cum[b]:
            cum[b].append(iid)
        print(f"  {iid}: {'RESOLVED' if resolved else 'FAILED'}")
    cum["n"] = len(cum["resolved"]) + len(cum["failed"]) + len(cum["infra_or_quota"])
    ef.write_text(json.dumps(cum, indent=2))
    print(f"{disp(harness)}: cumulative n={cum['n']} resolved={len(cum['resolved'])} "
          f"failed={len(cum['failed'])} infra={len(cum['infra_or_quota'])}")

def run_and_merge(harness, iid):
    """Run docker eval for one instance, then merge."""
    merged = PRED_DIR / f"predictions_{harness}_new_{ROUND}.json"
    all_preds = load_pred(PRED_DIR / f"{harness}__{iid}.json")
    merged.write_text(json.dumps(all_preds, indent=2))
    run_id = f"verified_full_glm53_{harness}_incr_{ROUND}"
    cmd = (f"python3 -m swebench.harness.run_evaluation "
           f"--predictions_path {merged} --dataset_name {ENRICHED} --split test "
           f"--instance_ids {iid} --max_workers 1 "
           f"--run_id {run_id} --timeout {TIMEOUT_EVAL}")
    print(f"{disp(harness)}: EVAL {iid} -> run_id={run_id}")
    proc = subprocess.run(["sg", "docker", "-c", cmd], cwd=str(HERE),
                          capture_output=True, text=True,
                          timeout=TIMEOUT_EVAL + 600)
    (HERE / "logs" / f"eval_{run_id}.log").write_text(proc.stdout + "\n[stderr]\n" + proc.stderr)
    print(f"{disp(harness)}: eval rc={proc.returncode}")
    merge_existing(harness, iid, run_id)

# 1. Merge cline django-11490 (report.json already exists from the died incr_eval)
print("=== Step 1: merge cline django-11490 (existing report.json) ===")
merge_existing("cline-patched", "django__django-11490",
               f"verified_full_glm53_cline-patched_incr_{ROUND}")

# 2. Run + merge cc django-13417
print("\n=== Step 2: run+merge claude-code django-13417 ===")
run_and_merge("claude-code", "django__django-13417")

print("\n=== R2300 merge complete ===")
