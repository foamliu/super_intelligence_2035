#!/usr/bin/env bash
# fill_gap_docs0_1757.sh — Fill the gap: hellaswag docs 0-1757 not covered by any active chunk.
# chunk0_missing was killed at 70% (docs 0-1757 done but results lost). split1 only covers 1758-2509.
# This script waits for a free llama-server port, then starts eval for docs 0-1757.
set -uo pipefail
PY="/nas_train/app.e0031982/miniforge3/envs/py310/bin/python"
GGUF_RUN_PY="/tmp/baize_eval_v4/gguf_lmeval_run.py"
MODEL="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/hf_iter_112000"
GGUF="/nas_train/app.e0031982/models/baize2b_gguf/bz2b-112000-f16.gguf"
OUT="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results/gguf_iter_112000_full_v4"
LOGFILE="/tmp/baize_eval_v4/fill_gap_docs0_1757.log"
CHUNK="hellaswag_chunk0_missing_split0"
SAMPLES=$(python3 -c 'import json; print(json.dumps({"hellaswag": list(range(0, 1758))}))')
declare -A CLIENT_CPUS
CLIENT_CPUS[8080]="112-127"; CLIENT_CPUS[8081]="128-143"; CLIENT_CPUS[8082]="144-159"; CLIENT_CPUS[8083]="0-15"
CLIENT_CPUS[8084]="160-175"; CLIENT_CPUS[8085]="176-191"; CLIENT_CPUS[8086]="192-207"; CLIENT_CPUS[8087]="208-223"
ALL_PORTS=(8080 8081 8082 8083 8084 8085 8086 8087)
log() { echo "[$(date '+%F %T')] $*" | tee -a "$LOGFILE"; }
is_port_free() {
  local port=$1
  curl -s --max-time 3 "http://127.0.0.1:${port}/health" 2>/dev/null | grep -q "ok" || return 1
  for pid in $(pgrep -f gguf_lmeval_run 2>/dev/null); do
    cat /proc/$pid/cmdline 2>/dev/null | tr '\0' ' ' | grep -q "127.0.0.1:${port}" && return 1
  done
  return 0
}
log "=== Gap-filling script started: docs 0-1757 (1758 docs, 7032 reqs) ==="
log "Waiting for a free llama-server port..."
while true; do
  for port in "${ALL_PORTS[@]}"; do
    if is_port_free "$port"; then
      log "Found free port $port! Starting gap-filling eval..."
      cpus=${CLIENT_CPUS[$port]:-0-223}
      mkdir -p "$OUT/$CHUNK"
      setsid bash -c "export HF_DATASETS_OFFLINE=1 HF_HUB_OFFLINE=1 HF_DATASETS_CACHE=/nas_train/app.e0031982/hf_cache HF_HOME=/nas_train/app.e0031982/.cache; taskset -c $cpus $PY '$GGUF_RUN_PY' --base-url http://127.0.0.1:$port --hf-dir '$MODEL' --output '$OUT/$CHUNK' --tasks hellaswag --parallel 4 --batch-size 32 --samples '$SAMPLES' --gguf '$GGUF'" > "$OUT/$CHUNK.log" 2>&1 &
      log "Started PID=$! on port=$port cpus=$cpus chunk=$CHUNK"
      log "=== Gap-filling eval launched. Script exiting. ==="
      exit 0
    fi
  done
  sleep 30
done
