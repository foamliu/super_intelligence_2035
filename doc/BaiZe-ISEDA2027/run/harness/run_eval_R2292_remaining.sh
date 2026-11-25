#!/bin/bash
# Run remaining R2292 evals with proper Docker permissions
# Usage: setsid bash run_eval_R2292_remaining.sh < /dev/null > /dev/null 2>&1 &

HERE="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full"
LOGDIR="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/logs_glm53"

cd "$HERE"

# 1. codex pytest-7205
echo "=== codex pytest-7205 ===" 
sg docker -c "python3 -m swebench.harness.run_evaluation \
  --predictions_path predictions_glm53/codex__pytest-dev__pytest-7205.json \
  --dataset_name enriched_500.json --split test \
  --instance_ids pytest-dev__pytest-7205 --max_workers 1 \
  --run_id verified_full_glm53_codex_incr_R2292c --timeout 1800" \
  > "$LOGDIR/eval_codex_7205_R2292c.log" 2>&1
echo "codex 7205 rc=$?"

# 2. claude-code django-12663
echo "=== claude-code django-12663 ==="
sg docker -c "python3 -m swebench.harness.run_evaluation \
  --predictions_path predictions_glm53/claude-code__django__django-12663.json \
  --dataset_name enriched_500.json --split test \
  --instance_ids django__django-12663 --max_workers 1 \
  --run_id verified_full_glm53_claude-code_incr_R2292c --timeout 1800" \
  > "$LOGDIR/eval_cc_12663_R2292c.log" 2>&1
echo "cc 12663 rc=$?"

echo "=== ALL DONE ==="
