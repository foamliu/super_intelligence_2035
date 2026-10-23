#!/bin/bash
# Launch Qwen3.5-2B SGLang server for long-context benchmark
CTX=${1:-65536}
PY=/nas_train/app.e0031982/miniforge3/envs/sglang/bin/python
MODEL_PATH=/nas_train/app.e0031982/hf_cache/hub/models--Qwen--Qwen3.5-2B/snapshots/15852e8c16360a2fea060d615a32b45270f8a8fc
LOG=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/longctx_eval_results/server_Qwen3.5-2B_ctx${CTX}.log

pkill -f "sglang.launch_server.*30000" 2>/dev/null
sleep 2

CUDA_VISIBLE_DEVICES=0 $PY -m sglang.launch_server \
    --model-path "$MODEL_PATH" \
    --served-model-name "Qwen3.5-2B" \
    --port 30000 --host 127.0.0.1 \
    --context-length $CTX \
    --mem-fraction-static 0.88 \
    --dtype bfloat16 \
    --attention-backend flashinfer \
    --disable-radix-cache \
    --log-level info \
    > "$LOG" 2>&1 &

echo "PID=$! CTX=$CTX LOG=$LOG"
