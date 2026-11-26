#!/usr/bin/env bash
# GSM8K diagnostic: Run with --log_samples to capture actual model outputs
# Only 10 samples (fast), both 5-shot (original) and 0-shot, to diagnose 0% issue
# Runs AFTER v5 completes (port 8083 must be free). CPU-only, no GPU impact.
# Usage: setsid bash baize_l2_gsm8k_diag.sh > /tmp/baize_l2_gsm8k_diag.log 2>&1 < /dev/null &
set -uo pipefail
export CUDA_VISIBLE_DEVICES=""
export OMP_NUM_THREADS=1
export HF_DATASETS_OFFLINE=1
export HF_HUB_OFFLINE=1
export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"
export PYTHONPATH="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5:${PYTHONPATH:-}"

GGUF="/nas_train/app.e0031982/models/baize2b_gguf/bz2b-160000-f16.gguf"
LLAMA_BIN="/nas_train/app.e0031982/tools/llama.cpp/build/bin/llama-server"
PORT=8083
HF_DIR="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/hf_iter_160000"
OUTDIR="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results/gguf_iter_160000_l2_gsm8k_diag"
PY="/nas_train/app.e0031982/miniforge3/envs/py310/bin/python"
mkdir -p "$OUTDIR"

# Wait for port 8083 to be free (v4/v5 must be done)
echo "[$(date +%T)] Waiting for port 8083 to be free..."
for i in $(seq 1 720); do
  curl -sf "http://127.0.0.1:8083/health" >/dev/null 2>&1 || { echo "[$(date +%T)] Port 8083 free."; break; }
  sleep 30
done
sleep 60

# Start llama-server with larger context (8192) for 5-shot GSM8K
echo "[$(date +%T)] Starting llama-server (ctx=8192, t=4, parallel=2, nice=19)..."
setsid nice -n 19 "$LLAMA_BIN" \
  -m "$GGUF" -t 4 -tb 4 -c 8192 --parallel 2 \
  --host 127.0.0.1 --port "$PORT" \
  --no-warmup --metrics --slots \
  --cache-prompt --temp 0 --top-k 1 --seed 1234 \
  > /tmp/llamacpp_l2_gsm8k_diag_server.log 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > /tmp/llamacpp_l2_gsm8k_diag_server.pid
echo "[$(date +%T)] Server PID=$SERVER_PID"

for i in $(seq 1 90); do
  curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1 && { echo "[$(date +%T)] Server ready after ${i}x2s"; break; }
  sleep 2
done
curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1 || { echo "FAIL: server not ready"; kill $SERVER_PID; exit 1; }

# Phase 1: GSM8K 5-shot with --log_samples (10 samples only)
echo "[$(date +%T)] Phase 1: GSM8K 5-shot + log_samples (limit=10)..."
nice -n 19 "$PY" -m lm_eval \
  --model local-completions \
  --model_args "model=${HF_DIR},base_url=http://127.0.0.1:${PORT}/v1/completions,num_concurrent=1,tokenized_requests=False,max_retries=3,max_gen_toks=512" \
  --tasks gsm8k --num_fewshot 5 --limit 10 \
  --log_samples \
  --output_path "${OUTDIR}/gsm8k_5shot" \
  2>&1 | tee "${OUTDIR}/gsm8k_5shot.log"
echo "[$(date +%T)] GSM8K 5-shot phase done."

# Phase 2: GSM8K 0-shot with --log_samples (10 samples only)
echo "[$(date +%T)] Phase 2: GSM8K 0-shot + log_samples (limit=10)..."
nice -n 19 "$PY" -m lm_eval \
  --model local-completions \
  --model_args "model=${HF_DIR},base_url=http://127.0.0.1:${PORT}/v1/completions,num_concurrent=1,tokenized_requests=False,max_retries=3,max_gen_toks=512" \
  --tasks gsm8k --num_fewshot 0 --limit 10 \
  --log_samples \
  --output_path "${OUTDIR}/gsm8k_0shot" \
  2>&1 | tee "${OUTDIR}/gsm8k_0shot.log"
echo "[$(date +%T)] GSM8K 0-shot phase done."

# Cleanup
echo "[$(date +%T)] Killing llama-server PID=$SERVER_PID..."
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null
echo "[$(date +%T)] GSM8K diagnostic complete. Results in $OUTDIR"
echo "[$(date +%T)] Check *_samples.json for actual model outputs."
