#!/bin/bash

RUN_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
RESULTS_DIR=$RUN_DIR/longctx_eval_results
PY=/nas_train/app.e0031982/miniforge3/envs/sglang/bin/python
MODEL_PATH=/nas_train/app.e0031982/hf_cache/hub/models--Qwen--Qwen3.5-2B/snapshots/15852e8c16360a2fea060d615a32b45270f8a8fc

# 64K result already saved from previous run
# Now run 128K, 256K, 512K, 1M with memory optimizations

for CTX in 131072 262144 524288 1048576; do
    echo "\n========== CTX=$CTX =========="
    
    # Kill previous server by PID
    OLD_PID=$(pgrep -f "sglang.launch_server" 2>/dev/null | head -1)
    if [ -n "$OLD_PID" ]; then
        kill -9 $OLD_PID 2>/dev/null
        sleep 5
    fi
    
    # Launch server with memory optimizations for large contexts
    LOG=$RESULTS_DIR/server_Qwen3.5-2B_ctx${CTX}.log
    CUDA_VISIBLE_DEVICES=0 $PY -m sglang.launch_server \
        --model-path "$MODEL_PATH" \
        --served-model-name "Qwen3.5-2B" \
        --port 30000 --host 127.0.0.1 \
        --context-length $CTX \
        --mem-fraction-static 0.90 \
        --dtype bfloat16 \
        --attention-backend flashinfer \
        --disable-radix-cache \
        --max-running-requests 4 \
        --cuda-graph-max-bs 32 \
        --log-level info \
        > "$LOG" 2>&1 &
    SERVER_PID=$!
    echo "Server PID=$SERVER_PID, waiting for startup..."
    
    # Wait for server to be ready (up to 180s)
    READY=0
    for i in $(seq 1 90); do
        sleep 2
        if grep -q "Uvicorn running" "$LOG" 2>/dev/null; then
            READY=1
            echo "Server ready after ${i}x2s"
            break
        fi
        if grep -q "SIGQUIT\|OutOfMemory\|out of memory\|Capture cuda graph failed" "$LOG" 2>/dev/null; then
            echo "Server failed during startup"
            break
        fi
    done
    
    if [ $READY -eq 0 ]; then
        echo "Server not ready, marking as OOM"
        cat > $RESULTS_DIR/results_qwen35-2b_ctx${CTX}.json << EOFJSON
{"context": $CTX, "status": "oom", "error": "Server failed to start - likely OOM", "peak_vram_gb": null}
EOFJSON
        kill -9 $SERVER_PID 2>/dev/null
        sleep 5
        continue
    fi
    
    # Wait extra for JIT compilation
    sleep 15
    
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
        > $RESULTS_DIR/benchmark_qwen35_ctx${CTX}.log 2>&1
    
    echo "Benchmark for CTX=$CTX done, checking result..."
    cat "$OUTPUT" 2>/dev/null | head -5
    
    # Check if the result indicates OOM or error
    if grep -q status: error|status: oom "$OUTPUT" 2>/dev/null; then
        echo "OOM or error at CTX=$CTX, stopping"
        kill -9 $SERVER_PID 2>/dev/null
        break
    fi
done

echo "\n========== All context lengths done =========="
FINAL_PID=$(pgrep -f "sglang.launch_server" 2>/dev/null | head -1)
if [ -n "$FINAL_PID" ]; then
    kill -9 $FINAL_PID 2>/dev/null
fi
echo "Done"
