#!/bin/bash
# P-9.11 D: sglang VRAM gap-fill benchmark (H3 + 128K correction)
# Operator 2026-10-06 approved D: GPU0 · 1 card · <=2h
#
# What this fills:
#   (a) 128K: re-run with tokenizer-accurate prompt sizing (B1 proved original
#       128K failure was a prompt construction bug, NOT max_pos=4096).
#   (b) H3 VRAM: run with --mem-fraction-static 0.3 (vs original 0.85) so
#       sglang does NOT pre-allocate ~68GB, revealing TRUE VRAM at each ctx.
#
# Usage: bash p911d_launch.sh [gpu_id] [port]
set -euo pipefail

GPU_ID="${1:-0}"
PORT="${2:-30001}"

SGLANG_PY=/nas_train/app.e0031982/miniforge3/envs/sglang/bin/python
BENCH_PY=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/p911d_sglang_vram_bench.py
HYBRID_HF=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p3_hybrid/hf_iter_5000
OUT_JSON=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/p911d_hybrid_vram_results.json
SRV_LOG=/tmp/p911d_sglang_srv2.log

export SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1
export http_proxy="http://172.19.92.25:13128"
export https_proxy="http://172.19.92.25:13128"
export no_proxy="localhost,127.0.0.1,0.0.0.0"
export NO_PROXY="localhost,127.0.0.1,0.0.0.0"

echo "[$(date)] P-9.11 D: launching sglang with --mem-fraction-static 0.3 on GPU${GPU_ID}"
echo "  model=$HYBRID_HF"
echo "  port=$PORT"
echo "  log=$SRV_LOG"

# Launch sglang server with LOW mem-fraction (0.3) to reveal true VRAM
CUDA_VISIBLE_DEVICES=$GPU_ID $SGLANG_PY -m sglang.launch_server \
    --model-path "$HYBRID_HF" \
    --host 127.0.0.1 \
    --port "$PORT" \
    --context-length 131072 \
    --trust-remote-code \
    --mem-fraction-static 0.3 \
    --attention-backend flashinfer \
    --mamba-ssm-dtype float32 \
    --skip-server-warmup \
    --log-level info \
    > "$SRV_LOG" 2>&1 &
# nohup not needed — the & backgrounds it, and the script keeps running
SRV_PID=$!
echo "  sglang PID=$SRV_PID"

# Wait for server to be ready (up to 180s — model load takes >60s)
echo "[$(date)] Waiting for sglang server to be ready..."
for i in $(seq 1 90); do
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:${PORT}/v1/models" 2>/dev/null || echo "000")
    if [ "$http_code" = "200" ]; then
        echo "[$(date)] Server ready after ${i}x2s (HTTP 200)"
        break
    fi
    if ! kill -0 $SRV_PID 2>/dev/null; then
        echo "[ERROR] sglang server died. Last 10 lines of log:"
        tail -10 "$SRV_LOG"
        exit 1
    fi
    sleep 2
done

# Verify server is up
http_code=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:${PORT}/v1/models" 2>/dev/null || echo "000")
if [ "$http_code" != "200" ]; then
    echo "[ERROR] Server not responding (HTTP $http_code) after 180s"
    tail -20 "$SRV_LOG"
    kill $SRV_PID 2>/dev/null || true
    exit 1
fi

echo "[$(date)] Running VRAM benchmark..."
SGLANG_PY=/nas_train/app.e0031982/miniforge3/envs/sglang/bin/python
$SGLANG_PY "$BENCH_PY" \
    --base-url "http://127.0.0.1:${PORT}" \
    --model-name "default" \
    --model-path "$HYBRID_HF" \
    --gpu-id 0 \
    --output "$OUT_JSON" \
    --contexts 4096 16384 65536 131072 \
    --batches 1 8 \
    --gen-len 64 \
    2>&1 | tee /tmp/p911d_bench.log

echo "[$(date)] Benchmark done. Killing sglang server..."
kill $SRV_PID 2>/dev/null || true
wait $SRV_PID 2>/dev/null || true

echo "[$(date)] P-9.11 D complete. Results: $OUT_JSON"
echo "  Server log: $SRV_LOG"
echo "  Bench log: /tmp/p911d_bench.log"
