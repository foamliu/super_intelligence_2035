#!/bin/bash
# R988: clean full-5 eval for hermes + deepseek (fresh run_id -> no skip)
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
IDS="django__django-10097 sympy__sympy-11618 sphinx-doc__sphinx-10323 scikit-learn__scikit-learn-10297 psf__requests-1142"

echo "=== [$(date)] hermes verify5b eval (5 instances) ==="
sg docker -c "python3 -m swebench.harness.run_evaluation \
  --predictions_path predictions/predictions_hermes.json \
  --dataset_name enriched_500.json --split test \
  --instance_ids $IDS \
  --max_workers 5 --run_id verify5b_hermes --timeout 1800" \
  > logs/eval_verify5b_hermes.log 2>&1
echo "=== [$(date)] hermes eval done rc=$? ==="

echo "=== [$(date)] deepseek verify5b eval (5 instances) ==="
sg docker -c "python3 -m swebench.harness.run_evaluation \
  --predictions_path predictions/predictions_deepseek-harness.json \
  --dataset_name enriched_500.json --split test \
  --instance_ids $IDS \
  --max_workers 5 --run_id verify5b_deepseek --timeout 1800" \
  > logs/eval_verify5b_deepseek.log 2>&1
echo "=== [$(date)] deepseek eval done rc=$? ==="
echo "=== ALL DONE ==="
