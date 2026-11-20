#!/usr/bin/env bash
# L2 vLLM eval: GSM8K + BBH + HumanEval + MBPP + MATH @ 160k using vLLM (GPU)
# Purpose: Replace llama.cpp eval for generative tasks — vLLM has proper SSM generation.
# Prerequisite: baize_vllm_server_160k.sh must be running on port 8084.
#
# Usage (when GPU window available):
#   # 1. Start vLLM server (separate terminal)
#   export CUDA_VISIBLE_DEVICES=0
#   setsid bash baize_vllm_server_160k.sh > /tmp/baize_vllm_server.log 2>&1 < /dev/null &
#   # 2. Wait for server to be ready
#   until curl -sf http://127.0.0.1:8084/health; do sleep 5; done
#   # 3. Run eval
#   bash baize_l2_eval_160k_vllm.sh

set -uo pipefail
export HF_DATASETS_OFFLINE=1
export HF_HUB_OFFLINE=1
export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"
export HF_ALLOW_CODE_EVAL="1"

PORT=8084
HF_DIR="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/hf_iter_160000"
OUTDIR="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results/gguf_iter_160000_l2_vllm"
PY="/nas_train/app.e0031982/miniforge3/envs/vllm/bin/python"
mkdir -p "$OUTDIR"

# Wait for server
echo "[$(date +%T)] Waiting for vLLM server on port $PORT..."
for i in $(seq 1 120); do
  curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1 && { echo "[$(date +%T)] Server ready."; break; }
  sleep 5
done
curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1 || { echo "FAIL: server not ready"; exit 1; }

BASE_URL="http://127.0.0.1:${PORT}/v1/completions"

# Phase 1: GSM8K (5-shot, generation)
echo "[$(date +%T)] Phase 1: GSM8K (5-shot, limit=100, generation)..."
"$PY" -m lm_eval \
  --model local-completions \
  --model_args "model=${HF_DIR},base_url=${BASE_URL},num_concurrent=1,tokenized_requests=False,max_retries=3,max_gen_toks=512" \
  --tasks gsm8k --num_fewshot 5 --limit 100 \
  --output_path "${OUTDIR}/gsm8k" \
  2>&1 | tee "${OUTDIR}/gsm8k.log"
echo "[$(date +%T)] GSM8K done."

# Phase 2: BBH boolean_expressions (3-shot CoT, generation)
echo "[$(date +%T)] Phase 2: BBH boolean_expressions (3-shot CoT, limit=100)..."
"$PY" -m lm_eval \
  --model local-completions \
  --model_args "model=${HF_DIR},base_url=${BASE_URL},num_concurrent=1,tokenized_requests=False,max_retries=3,max_gen_toks=1024" \
  --tasks bbh_cot_fewshot_boolean_expressions --num_fewshot 3 --limit 100 \
  --output_path "${OUTDIR}/bbh" \
  2>&1 | tee "${OUTDIR}/bbh.log"
echo "[$(date +%T)] BBH done."

# Phase 3: HumanEval (0-shot, generation, pass@1)
echo "[$(date +%T)] Phase 3: HumanEval (0-shot, limit=100)..."
"$PY" -m lm_eval \
  --model local-completions \
  --model_args "model=${HF_DIR},base_url=${BASE_URL},num_concurrent=1,tokenized_requests=False,max_retries=3,max_gen_toks=512" \
  --tasks humaneval --num_fewshot 0 --limit 100 \
  --output_path "${OUTDIR}/humaneval" \
  2>&1 | tee "${OUTDIR}/humaneval.log"
echo "[$(date +%T)] HumanEval done."

# Phase 4: MBPP (0-shot, generation, pass@1)
echo "[$(date +%T)] Phase 4: MBPP (0-shot, limit=100)..."
"$PY" -m lm_eval \
  --model local-completions \
  --model_args "model=${HF_DIR},base_url=${BASE_URL},num_concurrent=1,tokenized_requests=False,max_retries=3,max_gen_toks=512" \
  --tasks mbpp --num_fewshot 0 --limit 100 \
  --output_path "${OUTDIR}/mbpp" \
  2>&1 | tee "${OUTDIR}/mbpp.log"
echo "[$(date +%T)] MBPP done."

# Phase 5: MATH algebra (0-shot, generation)
echo "[$(date +%T)] Phase 5: hendrycks_math_algebra (0-shot, limit=100)..."
"$PY" -m lm_eval \
  --model local-completions \
  --model_args "model=${HF_DIR},base_url=${BASE_URL},num_concurrent=1,tokenized_requests=False,max_retries=3,max_gen_toks=512" \
  --tasks hendrycks_math_algebra --num_fewshot 0 --limit 100 \
  --output_path "${OUTDIR}/math" \
  2>&1 | tee "${OUTDIR}/math.log"
echo "[$(date +%T)] MATH done."

echo "[$(date +%T)] L2 vLLM eval complete. Results in $OUTDIR"
echo "Compare with llama.cpp results in gguf_iter_160000_l2_v4/ and _v5/"
