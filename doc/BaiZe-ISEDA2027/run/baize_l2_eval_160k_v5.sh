#!/usr/bin/env bash
# L2 v5: Re-run HumanEval + MBPP (code_eval now cached) + MATH 0-shot (fix assertion) @ 160k
# Runs AFTER v4 (BBH) completes. CPU-only, llama-server, no GPU impact.
# Usage: setsid bash baize_l2_eval_160k_v5.sh > /tmp/baize_l2_eval_160k_v5.log 2>&1 < /dev/null &
set -uo pipefail
export CUDA_VISIBLE_DEVICES=""
export OMP_NUM_THREADS=1
export HF_DATASETS_OFFLINE=1
export HF_HUB_OFFLINE=1
export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"
export PYTHONPATH="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5:${PYTHONPATH:-}"
export HF_ALLOW_CODE_EVAL="1"

GGUF="/nas_train/app.e0031982/models/baize2b_gguf/bz2b-160000-f16.gguf"
LLAMA_BIN="/nas_train/app.e0031982/tools/llama.cpp/build/bin/llama-server"
PORT=8083
HF_DIR="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/hf_iter_160000"
OUTDIR="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results/gguf_iter_160000_l2_v5"
PY="/nas_train/app.e0031982/miniforge3/envs/py310/bin/python"
mkdir -p "$OUTDIR"

# Wait for v4 to finish (port 8083 must be free)
echo "[$(date +%T)] Waiting for v4 (port 8083) to finish..."
for i in $(seq 1 720); do
  curl -sf "http://127.0.0.1:8083/health" >/dev/null 2>&1 || { echo "[$(date +%T)] Port 8083 free, v4 done."; break; }
  sleep 30
done
sleep 60

# Start llama-server
echo "[$(date +%T)] Starting llama-server (ctx=4096, t=4, parallel=2, nice=19)..."
setsid nice -n 19 "$LLAMA_BIN" \
  -m "$GGUF" -t 4 -tb 4 -c 4096 --parallel 2 \
  --host 127.0.0.1 --port "$PORT" \
  --no-warmup --metrics --slots \
  --cache-prompt --temp 0 --top-k 1 --seed 1234 \
  > /tmp/llamacpp_l2_v5_server.log 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > /tmp/llamacpp_l2_v5_server.pid
echo "[$(date +%T)] Server PID=$SERVER_PID"

for i in $(seq 1 90); do
  curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1 && { echo "[$(date +%T)] Server ready after ${i}x2s"; break; }
  sleep 2
done
curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1 || { echo "FAIL: server not ready"; kill $SERVER_PID; exit 1; }

# Phase 1: HumanEval (0-shot, generation, pass@1, limit=100) — code_eval now cached
echo "[$(date +%T)] Phase 1: HumanEval (0-shot, limit=100, generation)..."
nice -n 19 "$PY" -m lm_eval \
  --model local-completions \
  --model_args "model=${HF_DIR},base_url=http://127.0.0.1:${PORT}/v1/completions,num_concurrent=1,tokenized_requests=False,max_retries=3,max_gen_toks=512" \
  --tasks humaneval --num_fewshot 0 --limit 100 \
  --output_path "${OUTDIR}/humaneval" \
  2>&1 | tee "${OUTDIR}/humaneval.log"
echo "[$(date +%T)] HumanEval phase done."

# Phase 2: MBPP (0-shot, generation, pass@1, limit=100) — code_eval now cached
echo "[$(date +%T)] Phase 2: MBPP (0-shot, limit=100, generation)..."
nice -n 19 "$PY" -m lm_eval \
  --model local-completions \
  --model_args "model=${HF_DIR},base_url=http://127.0.0.1:${PORT}/v1/completions,num_concurrent=1,tokenized_requests=False,max_retries=3,max_gen_toks=512" \
  --tasks mbpp --num_fewshot 0 --limit 100 \
  --output_path "${OUTDIR}/mbpp" \
  2>&1 | tee "${OUTDIR}/mbpp.log"
echo "[$(date +%T)] MBPP phase done."

# Phase 3: MATH (0-shot to avoid build_qa_turn assertion error)
echo "[$(date +%T)] Phase 3: hendrycks_math_algebra (0-shot, limit=100, generation)..."
nice -n 19 "$PY" -m lm_eval \
  --model local-completions \
  --model_args "model=${HF_DIR},base_url=http://127.0.0.1:${PORT}/v1/completions,num_concurrent=1,tokenized_requests=False,max_retries=3,max_gen_toks=512" \
  --tasks hendrycks_math_algebra --num_fewshot 0 --limit 100 \
  --output_path "${OUTDIR}/math" \
  2>&1 | tee "${OUTDIR}/math.log"
echo "[$(date +%T)] MATH phase done."

# Cleanup
echo "[$(date +%T)] Killing llama-server PID=$SERVER_PID..."
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null
echo "[$(date +%T)] L2 v5 eval complete. Results in $OUTDIR"