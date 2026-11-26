#!/usr/bin/env bash
# L2 v4: Remaining 4 benchmarks (MATH, BBH, HumanEval, MBPP) at 160k ckpt
# Runs AFTER v3 (GSM8K+MMLU) completes. CPU-only, llama-server, no GPU impact.
# Usage: setsid bash baize_l2_eval_160k_v4.sh > /tmp/baize_l2_eval_160k_v4.log 2>&1 < /dev/null &
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
OUTDIR="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results/gguf_iter_160000_l2_v4"
PY="/nas_train/app.e0031982/miniforge3/envs/py310/bin/python"
GGUF_RUN_PY="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/pretrain_cpu_eval_gguf/gguf_lmeval_run.py"
mkdir -p "$OUTDIR"

# Wait for v3 to finish (port 8082 must be free)
echo "[$(date +%T)] Waiting for v3 (port 8082) to finish..."
for i in $(seq 1 360); do
  curl -sf "http://127.0.0.1:8082/health" >/dev/null 2>&1 || { echo "[$(date +%T)] Port 8082 free, v3 done."; break; }
  sleep 30
done
# Extra safety: wait 60s after v3 server goes down
sleep 60

# Start llama-server
echo "[$(date +%T)] Starting llama-server (ctx=4096, t=4, parallel=2, nice=19)..."
setsid nice -n 19 "$LLAMA_BIN" \
  -m "$GGUF" -t 4 -tb 4 -c 4096 --parallel 2 \
  --host 127.0.0.1 --port "$PORT" \
  --no-warmup --metrics --slots \
  --cache-prompt --temp 0 --top-k 1 --seed 1234 \
  > /tmp/llamacpp_l2_v4_server.log 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > /tmp/llamacpp_l2_v4_server.pid
echo "[$(date +%T)] Server PID=$SERVER_PID"

for i in $(seq 1 90); do
  curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1 && { echo "[$(date +%T)] Server ready after ${i}x2s"; break; }
  sleep 2
done
curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1 || { echo "FAIL: server not ready"; kill $SERVER_PID; exit 1; }

# Phase 1: HumanEval (0-shot, generation, pass@1, limit=100)
echo "[$(date +%T)] Phase 1: HumanEval (0-shot, limit=100, generation)..."
nice -n 19 "$PY" -m lm_eval \
  --model local-completions \
  --model_args "model=${HF_DIR},base_url=http://127.0.0.1:${PORT}/v1/completions,num_concurrent=1,tokenized_requests=False,max_retries=3,max_gen_toks=512" \
  --tasks humaneval --num_fewshot 0 --limit 100 \
  --output_path "${OUTDIR}/humaneval" \
  2>&1 | tee "${OUTDIR}/humaneval.log"
echo "[$(date +%T)] HumanEval phase done."

# Phase 2: MBPP (0-shot, generation, pass@1, limit=100)
echo "[$(date +%T)] Phase 2: MBPP (0-shot, limit=100, generation)..."
nice -n 19 "$PY" -m lm_eval \
  --model local-completions \
  --model_args "model=${HF_DIR},base_url=http://127.0.0.1:${PORT}/v1/completions,num_concurrent=1,tokenized_requests=False,max_retries=3,max_gen_toks=512" \
  --tasks mbpp --num_fewshot 0 --limit 100 \
  --output_path "${OUTDIR}/mbpp" \
  2>&1 | tee "${OUTDIR}/mbpp.log"
echo "[$(date +%T)] MBPP phase done."

# Phase 3: MATH algebra subset (4-shot, generation, limit=100)
echo "[$(date +%T)] Phase 3: hendrycks_math_algebra (4-shot, limit=100, generation)..."
nice -n 19 "$PY" -m lm_eval \
  --model local-completions \
  --model_args "model=${HF_DIR},base_url=http://127.0.0.1:${PORT}/v1/completions,num_concurrent=1,tokenized_requests=False,max_retries=3,max_gen_toks=512" \
  --tasks hendrycks_math_algebra --num_fewshot 4 --limit 100 \
  --output_path "${OUTDIR}/math" \
  2>&1 | tee "${OUTDIR}/math.log"
echo "[$(date +%T)] MATH phase done."

# Phase 4: BBH boolean_expressions (3-shot CoT, generation, limit=100)
echo "[$(date +%T)] Phase 4: bbh_cot_fewshot_boolean_expressions (3-shot, limit=100, generation)..."
nice -n 19 "$PY" -m lm_eval \
  --model local-completions \
  --model_args "model=${HF_DIR},base_url=http://127.0.0.1:${PORT}/v1/completions,num_concurrent=1,tokenized_requests=False,max_retries=3,max_gen_toks=512" \
  --tasks bbh_cot_fewshot_boolean_expressions --num_fewshot 3 --limit 100 \
  --output_path "${OUTDIR}/bbh" \
  2>&1 | tee "${OUTDIR}/bbh.log"
echo "[$(date +%T)] BBH phase done."

# Kill server
kill $SERVER_PID 2>/dev/null; sleep 2; kill -9 $SERVER_PID 2>/dev/null
rm -f /tmp/llamacpp_l2_v4_server.pid
echo "[$(date +%T)] L2 v4 eval complete. Results in $OUTDIR"
