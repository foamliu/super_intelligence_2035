#!/bin/bash
set -e

RUN_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
RESULTS_DIR=$RUN_DIR/longctx_eval_results
PY=/nas_train/app.e0031982/miniforge3/envs/sglang/bin/python
MODEL_PATH=/nas_train/app.e0031982/hf_cache/hub/models--Qwen--Qwen3.5-2B/snapshots/15852e8c16360a2fea060d615a32b45270f8a8fc

# Save the 64K result we already have
cp $RESULTS_DIR/qwen35_2b_longctx.json $RESULTS_DIR/results_qwen35-2b_ctx65536.json 2>/dev/null || true

for CTX in 131072 262144 524288 1048576; do
    echo "\n========== CTX=$CTX =========="
    
    # Kill previous server
    pkill -f "sglang.launch_server" 2>/dev/null || true
    sleep 5
    
    # Launch server
    LOG=$RESULTS_DIR/server_Qwen3.5-2B_ctx${CTX}.log
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
    SERVER_PID=$!
    echo "Server PID=$SERVER_PID, waiting for startup..."
    
    # Wait for server to be ready (up to 120s)
    READY=0
    for i in $(seq 1 60); do
        sleep 2
        if grep -q "Uvicorn running" "$LOG" 2>/dev/null; then
            READY=1
            echo "Server ready after ${i}x2s"
            break
        fi
        if grep -q "Traceback\|SIGQUIT\|Error\|OOM\|OutOfMemory" "$LOG" 2>/dev/null; then
            echo "Server failed during startup"
            break
        fi
    done
    
    if [ $READY -eq 0 ]; then
        echo "Server not ready, marking as OOM/error"
        echo "{\"context\": $CTX, \"status\": \"oom\", \"error\": \"Server failed to start\"}" > $RESULTS_DIR/results_qwen35-2b_ctx${CTX}.json
        pkill -f "sglang.launch_server" 2>/dev/null || true
        sleep 3
        continue
    fi
    
    # Wait extra for JIT compilation
    sleep 10
    
    # Run benchmark for this context length only
    OUTPUT=$RESULTS_DIR/results_qwen35-2b_ctx${CTX}.json
    cd $RUN_DIR
    $PY benchmark_longctx_sglang.py \
        --base-url http://127.0.0.1:30000 \
        --model-name Qwen3.5-2B \
        --model-path "$MODEL_PATH" \
        --gpu-id 0 \
        --output "$OUTPUT" \
        --start-ctx $CTX \
        --max-ctx $CTX \
        --gen-len 128 \
        --warmup 1 \
        --repeats 2 \
        2>&1 | tee $RESULTS_DIR/benchmark_qwen35_ctx${CTX}.log
    
    echo "Benchmark for CTX=$CTX done"
    
    # Check if the result indicates OOM
    if grep -q status: error|status: oom "$OUTPUT" 2>/dev/null; then
        echo "OOM or error detected at CTX=$CTX, stopping"
        pkill -f "sglang.launch_server" 2>/dev/null || true
        break
    fi
done

echo "\n========== All context lengths done =========="
pkill -f "sglang.launch_server" 2>/dev/null || true
echo "Done"
