#!/bin/bash
export SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1

RUN_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
RESULTS_DIR=$RUN_DIR/longctx_eval_results
PY=/nas_train/app.e0031982/miniforge3/envs/sglang/bin/python
MODEL_PATH=/nas_train/app.e0031982/hf_cache/hub/models--Qwen--Qwen3.5-2B/snapshots/15852e8c16360a2fea060d615a32b45270f8a8fc

# 64K, 128K, 256K already done. Now try 512K and 1M with context override.

for CTX in 524288 1048576; do
    echo "\n========== CTX=$CTX =========="
    
    # Kill previous server
    OLD_PID=$(pgrep -f "sglang.launch_server" 2>/dev/null | head -1)
    if [ -n "$OLD_PID" ]; then
        kill -9 $OLD_PID 2>/dev/null
        sleep 5
    fi
    
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
        --max-running-requests 2 \
        --cuda-graph-max-bs 16 \
        --log-level info \
        > "$LOG" 2>&1 &
    SERVER_PID=$!
    echo "Server PID=$SERVER_PID, waiting for startup..."
    
    READY=0
    for i in $(seq 1 90); do
        sleep 2
        if grep -q "Uvicorn running" "$LOG" 2>/dev/null; then
            READY=1
            echo "Server ready after ${i}x2s"
            break
        fi
        if grep -q "SIGQUIT\|OutOfMemory\|out of memory\|Capture cuda graph failed\|ValueError\|RuntimeError" "$LOG" 2>/dev/null; then
            echo "Server failed during startup"
            break
        fi
    done
    
    if [ $READY -eq 0 ]; then
        echo "Server not ready, marking as OOM"
        cat > $RESULTS_DIR/results_qwen35-2b_ctx${CTX}.json << EOFJSON
{"context": $CTX, "status": "oom", "error": "Server failed to start", "peak_vram_gb": null}
EOFJSON
        kill -9 $SERVER_PID 2>/dev/null
        sleep 5
        continue
    fi
    
    sleep 15
    
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
    
    echo "Benchmark for CTX=$CTX done"
    cat "$OUTPUT" 2>/dev/null | head -5
    
    if grep -q status: error|status: oom "$OUTPUT" 2>/dev/null; then
        echo "OOM or error at CTX=$CTX, stopping"
        kill -9 $SERVER_PID 2>/dev/null
        break
    fi
done

echo "\n========== Extended context lengths done =========="
FINAL_PID=$(pgrep -f "sglang.launch_server" 2>/dev/null | head -1)
if [ -n "$FINAL_PID" ]; then
    kill -9 $FINAL_PID 2>/dev/null
fi
echo "Done"
