#!/bin/bash
# R1040b incremental eval: 4 uneval patches AFTER re-merge fix.
# R1040 failed because merged predictions_<h>.json was stale (not rewritten).
# This re-merges (done inline above) and evals with FIXED python path.
# uneval files: /tmp/<tag>_uneval_R1040b.txt (claude-code 2, codex 1, hermes 1)
set -uo pipefail
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs/incr_eval_R1040b.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R1040b START $(date) === (py=$PY, re-merged predictions)"

eval_one() {
    local h="$1"
    local tag="$(echo $h | tr '-' '_')"
    local ids_file="/tmp/${tag}_uneval_R1040b.txt"
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
echo "=== incr_eval R1040b DONE $(date) ==="
