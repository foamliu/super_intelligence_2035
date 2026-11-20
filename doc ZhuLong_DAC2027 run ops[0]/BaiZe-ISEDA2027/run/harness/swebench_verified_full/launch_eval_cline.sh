#!/bin/bash
# Launch cline-patched eval for full 500 (early start with available patches).
# R947 2026-10-30: 394 patches available, predict still running for remaining ~58.
set -uo pipefail
cd "$(dirname "$0")"

IDS=$(tr '\n' ' ' < /tmp/cline_eval_ids.txt)
echo "=== cline-patched eval START $(date) ==="
echo "instances: $(echo $IDS | wc -w)"

sg docker -c "python3 -m swebench.harness.run_evaluation \
  --predictions_path $(pwd)/predictions/predictions_cline-patched.json \
  --dataset_name $(pwd)/enriched_500.json \
  --split test \
  --instance_ids $IDS \
  --max_workers 8 \
  --run_id verified_full_cline-patched \
  --timeout 1800"

echo "=== cline-patched eval DONE $(date) rc=$? ==="
