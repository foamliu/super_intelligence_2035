#!/bin/bash
# R1038 incremental eval: 4 ongoing routes only (claude-code 3, codex 1, hermes 5, deepseek 2 = 11 new)
# 3 done routes (cline/opencode/pi) have 0 new -> skipped.
# swebench idempotent: only evals the listed unevaluated IDs.
set -uo pipefail
cd "$(dirname "$0")"
LOG=logs/incr_eval_4routes_R1038.log
exec >>"$LOG" 2>&1
echo "=== incr_eval_4routes R1038 START $(date) ==="

eval_one() {
    local h="$1"
    local tag="$(echo $h | tr '-' '_')"
    local ids_file="/tmp/${tag}_uneval_R1038.txt"
    local ids=$(tr '\n' ' ' < "$ids_file")
    if [ -z "$ids" ]; then echo "[$(date)] $h: no unevaluated IDs, skip"; return; fi
    echo "[$(date)] === $h eval START $(echo $ids | wc -w) instances ==="
    sg docker -c "python3 -m swebench.harness.run_evaluation \
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
python3 regen_eval_summaries.py 2>&1
echo "=== incr_eval_4routes R1038 DONE $(date) ==="
