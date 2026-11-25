#!/bin/bash
# R1040 incremental eval: 2 new uneval patches (claude-code 1 + codex 1) since R1039b@11:37.
# Uses FIXED python path (miniforge py310 has swebench) per R1039b bug fix.
# uneval files already written by inline computation: /tmp/<tag>_uneval_R1040.txt
set -uo pipefail
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs/incr_eval_R1040.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R1040 START $(date) === (py=$PY)"

eval_one() {
    local h="$1"
    local tag="$(echo $h | tr '-' '_')"
    local ids_file="/tmp/${tag}_uneval_R1040.txt"
    local ids=$(tr '\n' ' ' < "$ids_file" 2>/dev/null)
    if [ -z "$ids" ]; then echo "[$(date)] $h: no unevaluated IDs, skip"; return; fi
    echo "[$(date)] === $h eval START $(echo $ids | wc -w) instances: $ids ==="
    sg docker -c "$PY -m swebench.harness.run_evaluation \
      --predictions_path $(pwd)/predictions/predictions_${h}.json \
      --dataset_name $(pwd)/enriched_500.json \
      --split test \
      --instance_ids $ids \
      --max_workers 8 \
      --run_id verified_full_${h} \
      --timeout 1800" 2>&1
    echo "[$(date)] === $h eval DONE ==="
}

eval_one "claude-code"
eval_one "codex"
eval_one "hermes"
eval_one "deepseek-harness"

echo "[$(date)] === regen summaries ==="
$PY regen_eval_summaries.py 2>&1
echo "=== incr_eval R1040 DONE $(date) ==="
