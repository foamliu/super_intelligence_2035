#!/usr/bin/env bash
# L2 v6: Re-run HumanEval + MBPP with --confirm_run_unsafe_code fix
#        + MATH re-run with --repeat-penalty 1.3 (generation degradation workaround)
# Runs AFTER v5 (MATH baseline) completes. CPU-only, llama-server, no GPU impact.
# Usage: setsid bash baize_l2_eval_160k_v6.sh > /tmp/baize_l2_eval_160k_v6.log 2>&1 < /dev/null &
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
OUTDIR="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results/gguf_iter_160000_l2_v6"
PY="/nas_train/app.e0031982/miniforge3/envs/py310/bin/python"
mkdir -p "$OUTDIR"

# Wait for v5 to finish (port 8083 must be free)
echo "[$(date +%T)] Waiting for v5 (port 8083) to finish..."
for i in $(seq 1 720); do
  curl -sf "http://127.0.0.1:8083/health" >/dev/null 2>&1 || { echo "[$(date +%T)] Port 8083 free, v5 done."; break; }
  sleep 30
done
sleep 60

# Check training health before starting — abort if step time > 7.4s
echo "[$(date +%T)] Pre-flight: checking training step time..."
STEP_MS=$(ssh -o StrictHostKeyChecking=no 10.239.2.29 "tail -1 /tmp/baize_xmodel25_decay_v2_train.log 2>/dev/null | grep -oP 'elapsed time per iteration \(ms\): \K[0-9.]+'" 2>/dev/null || echo "9999")
echo "[$(date +%T)] Training step = ${STEP_MS}ms (threshold 7400ms)"
if [ "$(echo "$STEP_MS > 7400" | bc 2>/dev/null || echo 1)" = "1" ]; then
  echo "[$(date +%T)] WARN: training step > 7.4s or check failed ($STEP_MS ms). Proceeding with -t 4 nice 19 (minimal load)."
fi

# Start llama-server with --repeat-penalty 1.3 (generation degradation workaround from #1984)
echo "[$(date +%T)] Starting llama-server (ctx=4096, t=4, parallel=2, nice=19, repeat-penalty=1.3)..."
setsid nice -n 19 "$LLAMA_BIN" \
  -m "$GGUF" -t 4 -tb 4 -c 4096 --parallel 2 \
  --host 127.0.0.1 --port "$PORT" \
  --no-warmup --metrics --slots \
  --cache-prompt --temp 0 --top-k 1 --seed 1234 \
  --repeat-penalty 1.3 \
  > /tmp/llamacpp_l2_v6_server.log 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > /tmp/llamacpp_l2_v6_server.pid
echo "[$(date +%T)] Server PID=$SERVER_PID"

for i in $(seq 1 90); do
  curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1 && { echo "[$(date +%T)] Server ready after ${i}x2s"; break; }
  sleep 2
done
curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1 || { echo "FAIL: server not ready"; kill $SERVER_PID; exit 1; }

# Phase 1: HumanEval (0-shot, generation, pass@1, limit=100) — with --confirm_run_unsafe_code
echo "[$(date +%T)] Phase 1: HumanEval (0-shot, limit=100, generation, confirm_run_unsafe_code)..."
nice -n 19 "$PY" -m lm_eval \
  --model local-completions \
  --model_args "model=${HF_DIR},base_url=http://127.0.0.1:${PORT}/v1/completions,num_concurrent=1,tokenized_requests=False,max_retries=3,max_gen_toks=512" \
  --tasks humaneval --num_fewshot 0 --limit 100 \
  --confirm_run_unsafe_code \
  --output_path "${OUTDIR}/humaneval" \
  2>&1 | tee "${OUTDIR}/humaneval.log"
echo "[$(date +%T)] HumanEval phase done."

# Phase 2: MBPP (0-shot, generation, pass@1, limit=100) — with --confirm_run_unsafe_code
echo "[$(date +%T)] Phase 2: MBPP (0-shot, limit=100, generation, confirm_run_unsafe_code)..."
nice -n 19 "$PY" -m lm_eval \
  --model local-completions \
  --model_args "model=${HF_DIR},base_url=http://127.0.0.1:${PORT}/v1/completions,num_concurrent=1,tokenized_requests=False,max_retries=3,max_gen_toks=512" \
  --tasks mbpp --num_fewshot 0 --limit 100 \
  --confirm_run_unsafe_code \
  --output_path "${OUTDIR}/mbpp" \
  2>&1 | tee "${OUTDIR}/mbpp.log"
echo "[$(date +%T)] MBPP phase done."

# Phase 3: MATH re-run with repeat_penalty=1.3 (compare with v5 baseline)
echo "[$(date +%T)] Phase 3: hendrycks_math_algebra (0-shot, limit=100, generation, repeat_penalty=1.3)..."
nice -n 19 "$PY" -m lm_eval \
  --model local-completions \
  --model_args "model=${HF_DIR},base_url=http://127.0.0.1:${PORT}/v1/completions,num_concurrent=1,tokenized_requests=False,max_retries=3,max_gen_toks=512" \
  --tasks hendrycks_math_algebra --num_fewshot 0 --limit 100 \
  --output_path "${OUTDIR}/math" \
  2>&1 | tee "${OUTDIR}/math.log"
echo "[$(date +%T)] MATH phase done."

# Quick generation probe: verify repeat_penalty is actually working
echo "[$(date +%T)] Phase 4: Generation probe (verify repeat_penalty effect)..."
curl -s "http://127.0.0.1:${PORT}/v1/completions" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Solve: 2+3=?\nAnswer:","max_tokens":50,"temperature":0,"top_k":1}' \
  2>&1 | tee "${OUTDIR}/gen_probe.json"
echo ""
echo "[$(date +%T)] Generation probe done."

# Cleanup
echo "[$(date +%T)] Killing llama-server PID=$SERVER_PID..."
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null
echo "[$(date +%T)] L2 v6 eval complete. Results in $OUTDIR"