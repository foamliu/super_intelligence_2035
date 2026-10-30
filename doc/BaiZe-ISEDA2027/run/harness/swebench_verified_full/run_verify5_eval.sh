#!/bin/bash
# R986: Run docker eval on verify-5 predictions for hermes and deepseek
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full

echo "=== [$(date)] Starting hermes verify5 eval (4 instances) ==="
sg docker -c "python3 -m swebench.harness.run_evaluation \
  --predictions_path predictions/predictions_hermes.json \
  --dataset_name enriched_500.json --split test \
  --instance_ids django__django-10097 sympy__sympy-11618 sphinx-doc__sphinx-10323 scikit-learn__scikit-learn-10297 \
  --max_workers 4 --run_id verify5_hermes --timeout 1800" \
  > logs/eval_verify5_hermes.log 2>&1
echo "=== [$(date)] hermes eval done rc=$? ==="

echo "=== [$(date)] Starting deepseek verify5 eval (2 instances) ==="
sg docker -c "python3 -m swebench.harness.run_evaluation \
  --predictions_path predictions/predictions_deepseek-harness.json \
  --dataset_name enriched_500.json --split test \
  --instance_ids django__django-10097 sympy__sympy-11618 \
  --max_workers 2 --run_id verify5_deepseek --timeout 1800" \
  > logs/eval_verify5_deepseek.log 2>&1
echo "=== [$(date)] deepseek eval done rc=$? ==="
echo "=== ALL DONE ==="
