#!/usr/bin/env python3
"""R1805: Launch deepseek-harness SWE-bench eval (parallel with hermes R1789).
Consolidates individual prediction files -> predictions_deepseek-harness.json,
then starts swebench.harness.run_evaluation in the background via sg docker.
"""
import json, subprocess, os, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRED = HERE / "predictions_glm53"
ENRICHED = HERE / "enriched_500.json"
RUN_ID = "verified_full_glm53_deepseek-harness_R1805"
MODEL_NAME = "deepseek-harness-glm-5.3-flash"

# 1. Merge individual deepseek predictions (real patches only)
allp = []
empty_ids = []
for f in sorted(PRED.glob("deepseek-harness__*.json")):
    if f.stat().st_size < 30:
        continue
    preds = json.loads(f.read_text())
    if isinstance(preds, dict):
        preds = [preds]
    for p in preds:
        iid = p.get("instance_id", "")
        patch = p.get("model_patch", "")
        if patch and patch.strip():
            allp.append(p)
        else:
            empty_ids.append(iid)

merged_path = PRED / "predictions_deepseek-harness.json"
merged_path.write_text(json.dumps(allp, indent=2))
print(f"Merged {len(allp)} real deepseek predictions -> {merged_path.name}")
print(f"Empty patches (skipped): {len(empty_ids)}")

if len(allp) == 0:
    print("FATAL: no real patches to eval. Exiting.")
    sys.exit(1)

# 2. Build instance_ids list
instance_ids = [p["instance_id"] for p in allp]
print(f"Instance IDs to eval: {len(instance_ids)}")
print(f"First 5: {instance_ids[:5]}")

# 3. Launch eval in background
instance_args = " ".join(instance_ids)
cmd = (
    f"python3 -m swebench.harness.run_evaluation "
    f"--predictions_path {merged_path} "
    f"--dataset_name {ENRICHED} --split test "
    f"--instance_ids {instance_args} "
    f"--max_workers 1 --run_id {RUN_ID} --timeout 1800"
)
log_file = HERE / f"eval_deepseek_R1805.log"
print(f"Launching eval (background)...")
print(f"  run_id: {RUN_ID}")
print(f"  log: {log_file}")

# Start in background with nohup
full_cmd = f"sg docker -c '{cmd}' > {log_file} 2>&1 &"
subprocess.run(["bash", "-c", full_cmd], cwd=str(HERE))
print(f"Eval launched in background. PID via: ps aux | grep {RUN_ID}")
print(f"Monitor: tail -f {log_file}")
