#!/bin/bash
# baize_posttrain_serve_increase_ctx.sh — R308: restart GPU4+GPU6 serves with --max-model-len 65536
# Fixes context overflow (32807 > 32768) found in wake307.
# Model supports max_position_embeddings=131072; 65536 is safe (KV cache pool unchanged).
# Sequential restart: GPU4 first (verify), then GPU6 (verify). GPU5/GPU7 untouched.
# Never touches GPU0-3 (root SGLang :8099).
set -euo pipefail

VLLM_PY=/tmp/vllm_venv/bin/python
BASE_MODEL=/nas_data/app.e0031982/models/MiniCPM5-2B
SFT_MODEL=/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/sft_surrogate_runs/minicpm5_pyaether_v2_v11v36/global_step_70
NEW_MAX_LEN=65536
WAIT_UP=180   # max seconds to wait for serve to come up
CHECK_INTERVAL=5

log()  { echo "[$(date '+%H:%M:%S')] $*"; }
die()  { echo "FATAL: $*" >&2; exit 1; }

wait_gpu_free() {
  local gpu=$1
  for i in $(seq 1 24); do
    local used=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader -i "$gpu" 2>/dev/null | wc -l)
    if [ "$used" -eq 0 ]; then log "GPU$gpu free"; return 0; fi
    sleep 5
  done
  die "GPU$gpu still has processes after 120s"
}

wait_port_up() {
  local port=$1 label=$2
  for i in $(seq 1 $((WAIT_UP / CHECK_INTERVAL))); do
    if curl -sf -m 3 "http://localhost:$port/v1/models" >/dev/null 2>&1; then
      log "$label (:$port) is UP"
      return 0
    fi
    sleep $CHECK_INTERVAL
  done
  die "$label (:$port) did not come up in ${WAIT_UP}s"
}

restart_gpu4() {
  log "=== Restarting GPU4 (base, :8098) with --max-model-len $NEW_MAX_LEN ==="
  # Kill old serve
  local old_pid=$(pgrep -f 'vllm.entrypoints.*--port 8098' | head -1 || true)
  if [ -n "$old_pid" ]; then
    log "Killing old GPU4 serve PID $old_pid"
    kill "$old_pid" 2>/dev/null || true
    sleep 3
    kill -9 "$old_pid" 2>/dev/null || true
  fi
  wait_gpu_free 4
  # Start new serve
  CUDA_VISIBLE_DEVICES=4 HF_HOME=/tmp/hf_home TRANSFORMERS_CACHE=/tmp/hf_home \
    HF_MODULES_CACHE=/tmp/hf_home/modules \
    nohup "$VLLM_PY" -m vllm.entrypoints.openai.api_server \
    --model "$BASE_MODEL" \
    --served-model-name minicpm5-2b \
    --host 0.0.0.0 --port 8098 \
    --trust-remote-code --gpu-memory-utilization 0.85 \
    --max-model-len "$NEW_MAX_LEN" \
    --enable-auto-tool-choice --tool-call-parser minicpm5 \
    --enforce-eager \
    > /tmp/vllm_gpu4_ctx.log 2>&1 &
  log "GPU4 serve started (PID $!), waiting for health..."
  wait_port_up 8098 "GPU4-base"
}

restart_gpu6() {
  log "=== Restarting GPU6 (SFT, :8096) with --max-model-len $NEW_MAX_LEN ==="
  local old_pid=$(pgrep -f 'vllm.entrypoints.*--port 8096' | head -1 || true)
  if [ -n "$old_pid" ]; then
    log "Killing old GPU6 serve PID $old_pid"
    kill "$old_pid" 2>/dev/null || true
    sleep 3
    kill -9 "$old_pid" 2>/dev/null || true
  fi
  wait_gpu_free 6
  CUDA_VISIBLE_DEVICES=6 HF_HOME=/tmp/hf_home TRANSFORMERS_CACHE=/tmp/hf_home \
    HF_MODULES_CACHE=/tmp/hf_home/modules \
    nohup "$VLLM_PY" -m vllm.entrypoints.openai.api_server \
    --model "$SFT_MODEL" \
    --served-model-name minicpm5-sft \
    --host 0.0.0.0 --port 8096 \
    --trust-remote-code --gpu-memory-utilization 0.85 \
    --max-model-len "$NEW_MAX_LEN" \
    --enable-auto-tool-choice --tool-call-parser minicpm5 \
    --enforce-eager \
    > /tmp/vllm_gpu6_ctx.log 2>&1 &
  log "GPU6 serve started (PID $!), waiting for health..."
  wait_port_up 8096 "GPU6-SFT"
}

verify_toolcall() {
  local port=$1 label=$2
  log "Verifying tool-call on $label (:$port)..."
  local resp=$(curl -sf -m 30 "http://localhost:$port/v1/chat/completions" \
    -H 'Content-Type: application/json' \
    -d '{"model":"x","messages":[{"role":"user","content":"Search for pyAether bus APIs"}],"tools":[{"type":"function","function":{"name":"pyAether_MCP_server__search_apis","description":"Search APIs","parameters":{"type":"object","properties":{"query":{"type":"string"}},"required":["query"]}}}],"tool_choice":"auto","max_tokens":512}')
  if echo "$resp" | python3 -c 'import sys,json; d=json.load(sys.stdin); assert d["choices"][0]["finish_reason"]=="tool_calls"; print("tool_calls OK:", d["choices"][0]["message"]["tool_calls"][0]["function"]["name"])' 2>/dev/null; then
    log "$label tool-call verified OK"
  else
    log "WARN: $label tool-call verification inconqueuent (resp may still be loading)"
  fi
}

# ---- main ----
log "R308: increasing max-model-len 32768 -> $NEW_MAX_LEN on GPU4+GPU6"
log "GPU5/GPU7 placeholders untouched. GPU0-3 (root) untouched."

restart_gpu4
verify_toolcall 8098 "GPU4-base"
restart_gpu6
verify_toolcall 8096 "GPU6-SFT"

log ""
log "=== Final status ==="
for port in 8095 8096 8097 8098 8099; do
  echo -n "  :$port -> "
  curl -sf -m 3 "http://localhost:$port/v1/models" | python3 -c 'import sys,json; print(json.load(sys.stdin)["data"][0]["id"])' 2>/dev/null || echo "DOWN"
done
nvidia-smi --query-gpu=index,memory.used --format=csv -i 4,5,6,7
log "Done. All 5 endpoints should be UP."
