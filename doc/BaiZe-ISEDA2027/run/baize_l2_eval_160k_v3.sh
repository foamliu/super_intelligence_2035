#!/usr/bin/env bash
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
PORT=8082
HF_DIR="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/hf_iter_160000"
OUTDIR="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results/gguf_iter_160000_l2_v3"
PY="/nas_train/app.e0031982/miniforge3/envs/py310/bin/python"
GGUF_RUN_PY="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/pretrain_cpu_eval_gguf/gguf_lmeval_run.py"
mkdir -p "$OUTDIR"

# Kill old stale server on 8081
OLD_PID=$(cat /tmp/llamacpp_l2_server.pid 2>/dev/null || echo "")
if [ -n "$OLD_PID" ]; then kill "$OLD_PID" 2>/dev/null; sleep 3; fi

# Start fresh llama-server with parallel=2 for speed
echo "[$(date +%T)] Starting llama-server (ctx=4096, t=4, parallel=2, nice=19)..."
setsid nice -n 19 "$LLAMA_BIN" \
  -m "$GGUF" -t 4 -tb 4 -c 4096 --parallel 2 \
  --host 127.0.0.1 --port "$PORT" \
  --no-warmup --metrics --slots \
  --cache-prompt --temp 0 --top-k 1 --seed 1234 \
  > /tmp/llamacpp_l2_v3_server.log 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > /tmp/llamacpp_l2_v3_server.pid
echo "[$(date +%T)] Server PID=$SERVER_PID"

for i in $(seq 1 90); do
  curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1 && { echo "[$(date +%T)] Server ready after ${i}x2s"; break; }
  sleep 2
done
curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1 || { echo "FAIL: server not ready"; kill $SERVER_PID; exit 1; }

# Phase 1: GSM8K via local-completions (generation, 5-shot, limit=100)
echo "[$(date +%T)] Phase 1: GSM8K (5-shot, limit=100, generation)..."
nice -n 19 "$PY" -m lm_eval \
  --model local-completions \
  --model_args "model=${HF_DIR},base_url=http://127.0.0.1:${PORT}/v1/completions,num_concurrent=1,tokenized_requests=False,max_retries=3,max_gen_toks=256" \
  --tasks gsm8k --num_fewshot 5 --limit 100 \
  --output_path "${OUTDIR}/gsm8k" \
  2>&1 | tee "${OUTDIR}/gsm8k.log"
echo "[$(date +%T)] GSM8K phase done."

# Phase 2: MMLU via gguf_lmeval_run.py (loglikelihood, 0-shot, limit=100)
echo "[$(date +%T)] Phase 2: MMLU (0-shot, limit=100, logit_bias loglikelihood)..."
nice -n 19 "$PY" "$GGUF_RUN_PY" \
  --base-url "http://127.0.0.1:${PORT}" \
  --hf-dir "$HF_DIR" \
  --output "${OUTDIR}/mmlu" \
  --tasks mmlu --limit 100 --num-fewshot 0 \
  --parallel 2 --batch-size 32 --max-length 2048 --timeout 600 \
  --gguf "$GGUF" \
  2>&1 | tee "${OUTDIR}/mmlu.log"
echo "[$(date +%T)] MMLU phase done."

# Kill server
kill $SERVER_PID 2>/dev/null; sleep 2; kill -9 $SERVER_PID 2>/dev/null
rm -f /tmp/llamacpp_l2_v3_server.pid
echo "[$(date +%T)] L2 eval complete. Results in $OUTDIR"
