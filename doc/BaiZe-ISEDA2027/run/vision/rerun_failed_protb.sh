#!/bin/bash
# rerun_failed_protb.sh — Monitor remaining 3 models, re-run with --skip-extract when they crash
# Models still extracting: siglip2-so400m-384 (GPU1), aimv2-1B-336 (GPU2), rice-vitl14-560 (GPU4)
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
LOGDIR=/tmp/external_protb_logs
mkdir -p "$LOGDIR"

declare -A MODEL_GPU
MODEL_GPU[siglip2-so400m-384]=1
MODEL_GPU[aimv2-1B-336]=2
MODEL_GPU[rice-vitl14-560]=4

# Original PIDs
declare -A ORIG_PID
ORIG_PID[siglip2-so400m-384]=22916
ORIG_PID[aimv2-1B-336]=22914
ORIG_PID[rice-vitl14-560]=22918

echo "[$(date '+%H:%M:%S')] Rerun monitor started" > /tmp/external_protb_rerun.log

while true; do
    ALL_DONE=true
    for m in "${!MODEL_GPU[@]}"; do
        result_file="external_protb_results_${m}.json"
        cache_file="external_features_cache/${m}_train.pt"
        orig_pid=${ORIG_PID[$m]}
        
        # Check if result already exists
        if [ -f "$result_file" ]; then
            continue
        fi
        
        ALL_DONE=false
        
        # Check if original process has died AND cache exists
        if ! ps -p "$orig_pid" > /dev/null 2>&1; then
            if [ -f "$cache_file" ]; then
                gpu=${MODEL_GPU[$m]}
                echo "[$(date '+%H:%M:%S')] $m: orig died, cache exists, re-running with --skip-extract on GPU $gpu" >> /tmp/external_protb_rerun.log
                CUDA_VISIBLE_DEVICES=$gpu $PY external_encoder_protb.py \
                    --models "$m" --gpu 0 --seeds 0 1 2 --skip-extract \
                    > "$LOGDIR/${m}_rerun.log" 2>&1 &
                # Wait for this to finish before checking next (avoid GPU conflict)
                wait $!
                echo "[$(date '+%H:%M:%S')] $m: re-run finished" >> /tmp/external_protb_rerun.log
            else
                echo "[$(date '+%H:%M:%S')] $m: orig died but NO cache, skipping" >> /tmp/external_protb_rerun.log
            fi
        else
            echo "[$(date '+%H:%M:%S')] $m: still extracting (PID $orig_pid alive)" >> /tmp/external_protb_rerun.log
        fi
    done
    
    if [ "$ALL_DONE" = true ]; then
        echo "[$(date '+%H:%M:%S')] All 3 remaining models have results!" >> /tmp/external_protb_rerun.log
        break
    fi
    sleep 60
done
