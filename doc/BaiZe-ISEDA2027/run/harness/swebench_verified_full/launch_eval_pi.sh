#!/bin/bash
# Launch pi eval for full 500 (early start with available patches).
# R949 2026-10-30: 351 patches available, predict still running for remaining ~149.
set -uo pipefail
cd "$(dirname "$0")"

IDS=$(tr '\n' ' ' < /tmp/pi_eval_ids.txt)
echo "=== pi eval START $(date) ==="
echo "instances: $(echo $IDS | wc -w)"

sg docker -c "python3 -m swebench.harness.run_evaluation \
  --predictions_path $(pwd)/predictions/predictions_pi.json \
  --dataset_name $(pwd)/enriched_500.json \
  --split test \
  --instance_ids $IDS \
  --max_workers 8 \
  --run_id verified_full_pi \
  --timeout 1800" 2>&1 | tee logs/eval_verified_full_pi.log

echo "=== pi eval DONE $(date) rc=${PIPESTATUS[0]} ==="
