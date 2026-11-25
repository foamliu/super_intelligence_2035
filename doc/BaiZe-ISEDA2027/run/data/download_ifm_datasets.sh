#!/bin/bash
# download_ifm_datasets.sh — Download IFM datasets with guardrails
# MegaMath: first batch (non-web subsets) + then web-pro if space allows
# Math-Reasoning: full
# Code-Reasoning: full
# Guardrails: nice 19, ionice 3, max-workers 2, setsid background

export PATH=/nas_train/app.e0031982/miniforge3/envs/py310/bin:$PATH
export https_proxy=http://172.19.92.25:13128
export http_proxy=http://172.19.92.25:13128

HF=/nas_train/app.e0031982/miniforge3/envs/py310/bin/hf
BASE=/nas_user/app.e0031982/datasets/IFM

# === MegaMath first batch ===
echo "=== [$(date)] MegaMath first batch (non-web subsets) ==="
mkdir -p $BASE/MegaMath
nice -n 19 ionice -c3 $HF download IFM/MegaMath --repo-type dataset \
  --include "megamath-web-pro/*" \
  --include "megamath-code/*" \
  --include "megamath-qa/*" \
  --include "megamath-text-code-block/*" \
  --include "megamath-translated-code/*" \
  --local-dir $BASE/MegaMath/ \
  --max-workers 2 2>&1 | tee /tmp/dl_megamath_batch1.log
echo "=== [$(date)] MegaMath batch1 done ==="
df -h /nas_user

# === Math-Reasoning (full, 4.46TB) ===
echo "=== [$(date)] Math-Reasoning (full) ==="
mkdir -p $BASE/Math-Reasoning
nice -n 19 ionice -c3 $HF download IFM/Math-Reasoning --repo-type dataset \
  --local-dir $BASE/Math-Reasoning/ \
  --max-workers 2 2>&1 | tee /tmp/dl_math_reasoning.log
echo "=== [$(date)] Math-Reasoning done ==="
df -h /nas_user

# === Code-Reasoning (full, 3.28TB) ===
echo "=== [$(date)] Code-Reasoning (full) ==="
mkdir -p $BASE/Code-Reasoning
nice -n 19 ionice -c3 $HF download IFM/Code-Reasoning --repo-type dataset \
  --local-dir $BASE/Code-Reasoning/ \
  --max-workers 2 2>&1 | tee /tmp/dl_code_reasoning.log
echo "=== [$(date)] Code-Reasoning done ==="
df -h /nas_user

echo "=== [$(date)] ALL IFM downloads complete ==="
