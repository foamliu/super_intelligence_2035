#!/usr/bin/env bash
# Quick test: GSM8K 0-shot with repeat_penalty=1.3 on llama-server (CPU)
# Purpose: Test if repeat_penalty fixes the SSM generation degeneration
# Based on finding #1984: repeat_penalty=1.3 broke "1" repetition loop
# Usage: setsid bash baize_l2_gsm8k_repeatpenalty_test.sh > /tmp/baize_l2_rp_test.log 2>&1 < /dev/null &
set -uo pipefail
export CUDA_VISIBLE_DEVICES=""
export OMP_NUM_THREADS=1
export HF_DATASETS_OFFLINE=1
export HF_HUB_OFFLINE=1
export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"

GGUF="/nas_train/app.e0031982/models/baize2b_gguf/bz2b-160000-f16.gguf"
LLAMA_BIN="/nas_train/app.e0031982/tools/llama.cpp/build/bin/llama-server"
PORT=8083
HF_DIR="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/hf_iter_160000"
OUTDIR="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results/gguf_iter_160000_l2_rp_test"
PY="/nas_train/app.e0031982/miniforge3/envs/py310/bin/python"
mkdir -p "$OUTDIR"

# Start llama-server WITH repeat_penalty=1.3
echo "[$(date +%T)] Starting llama-server (ctx=4096, t=4, nice=19, repeat_penalty=1.3)..."
setsid nice -n 19 "$LLAMA_BIN" \
  -m "$GGUF" -t 4 -tb 4 -c 4096 --parallel 1 \
  --host 127.0.0.1 --port "$PORT" \
  --no-warmup --temp 0 --top-k 1 --seed 1234 \
  --repeat-penalty 1.3 \
  > /tmp/llamacpp_l2_rp_server.log 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > /tmp/llamacpp_l2_rp_server.pid
echo "[$(date +%T)] Server PID=$SERVER_PID"

for i in $(seq 1 90); do
  curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1 && { echo "[$(date +%T)] Server ready after ${i}x2s"; break; }
  sleep 2
done
curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1 || { echo "FAIL: server not ready"; kill $SERVER_PID; exit 1; }

# GSM8K 0-shot with log_samples (limit=10, quick test)
echo "[$(date +%T)] GSM8K 0-shot (limit=10, repeat_penalty=1.3, log_samples)..."
nice -n 19 "$PY" -m lm_eval \
  --model local-completions \
  --model_args "model=${HF_DIR},base_url=http://127.0.0.1:${PORT}/v1/completions,num_concurrent=1,tokenized_requests=False,max_retries=3,max_gen_toks=256" \
  --tasks gsm8k --num_fewshot 0 --limit 10 --log_samples \
  --output_path "${OUTDIR}/gsm8k_0shot_rp" \
  2>&1 | tee "${OUTDIR}/gsm8k_0shot_rp.log"
echo "[$(date +%T)] GSM8K 0-shot RP test done."

# Also test with a simple curl to see raw generation
echo "[$(date +%T)] Quick curl test: '2+3=' ..."
curl -s http://127.0.0.1:${PORT}/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Question: What is 2+3?\nAnswer:","max_tokens":50,"temperature":0,"repeat_penalty":1.3}' \
  2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print('CURL_RESULT:', d.get('choices',[{}])[0].get('text','NONE')[:200])" 2>/dev/null || echo "CURL_FAILED"

echo "[$(date +%T)] Quick curl test: GSM8K sample ..."
curl -s http://127.0.0.1:${PORT}/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Question: Janet\u0027s ducks lay 16 eggs per day. She eats three for breakfast every morning and bakes muffins for her friends every day with four. She sells the remainder at the farmers\u0027 market daily for $2 per fresh duck egg. How much in dollars does she make every day at the farmers\u0027 market?\nAnswer:","max_tokens":200,"temperature":0,"repeat_penalty":1.3}' \
  2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print('CURL_GSM8K:', d.get('choices',[{}])[0].get('text','NONE')[:300])" 2>/dev/null || echo "CURL_FAILED"

# Cleanup
echo "[$(date +%T)] Killing llama-server PID=$SERVER_PID..."
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null
echo "[$(date +%T)] RP test complete. Results in $OUTDIR"
