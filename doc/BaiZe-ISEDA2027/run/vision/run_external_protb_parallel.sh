#!/bin/bash
# ==============================================================================
# run_external_protb_parallel.sh — Run external encoder ProtB eval in parallel
#
# Launches 5 models on GPUs 0-4 simultaneously. Each process:
#   1. Extracts IN-1k val (50k) + train (1.28M) features with native preprocessing
#   2. Caches features to external_features_cache/
#   3. Runs linear_probe_mainstream (SGD, 90ep, 3 seeds)
#   4. Saves results to external_protb_results_<model>.json
#
# Usage:
#   setsid bash run_external_protb_parallel.sh > /tmp/external_protb_parallel.log 2>&1 < /dev/null &
# ==============================================================================
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=8
export MKL_NUM_THREADS=8
export OPENBLAS_NUM_THREADS=8
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python

LOGDIR=/tmp/external_protb_logs
mkdir -p "$LOGDIR"

# Model → GPU mapping
declare -A MODEL_GPU
MODEL_GPU[clip-vitl14-336]=0
MODEL_GPU[siglip2-so400m-384]=1
MODEL_GPU[aimv2-1B-336]=2
MODEL_GPU[openvision2-vitl14-336]=3
MODEL_GPU[rice-vitl14-560]=4

PIDS=()
for model in "${!MODEL_GPU[@]}"; do
    gpu=${MODEL_GPU[$model]}
    log="$LOGDIR/${model}.log"
    echo "[$(date '+%H:%M:%S')] Launching $model on GPU $gpu -> $log"
    CUDA_VISIBLE_DEVICES=$gpu $PY external_encoder_protb.py \
        --models "$model" --gpu 0 --seeds 0 1 2 \
        > "$log" 2>&1 &
    PIDS+=($!)
done

echo "[$(date '+%H:%M:%S')] All ${#PIDS[@]} jobs launched. PIDs: ${PIDS[*]}"
echo "[$(date '+%H:%M:%S')] Waiting for all to finish..."

# Wait for all
FAIL=0
for i in "${!PIDS[@]}"; do
    pid=${PIDS[$i]}
    model=$(echo "${!MODEL_GPU[@]}" | tr ' ' '\n' | sed -n "$((i+1))p")
    if wait "$pid"; then
        echo "[$(date '+%H:%M:%S')] ✅ $model (PID $pid) completed"
    else
        echo "[$(date '+%H:%M:%S')] ❌ $model (PID $pid) FAILED (exit $?)"
        FAIL=$((FAIL+1))
    fi
done

echo "[$(date '+%H:%M:%S')] All done. Failures: $FAIL"
echo "=== Individual model logs ==="
for model in "${!MODEL_GPU[@]}"; do
    echo "--- $model ---"
    tail -5 "$LOGDIR/${model}.log" 2>/dev/null
done

# Merge results
echo "=== Merging results ==="
$PY -c "
import json, glob, os
results = []
for f in sorted(glob.glob('external_protb_results*.json')):
    if 'merged' in f: continue
    data = json.load(open(f))
    if isinstance(data, list): results.extend(data)
    else: results.append(data)
    print(f'  loaded {f}: {len(data) if isinstance(data, list) else 1} entries')
out = 'external_protb_results_merged.json'
json.dump(results, open(out, 'w'), indent=2)
print(f'Merged {len(results)} results -> {out}')
# Print summary table
print(f'\n{\"Model\":<28} {\"Res\":>5} {\"Dim\":>6} {\"ProtB\":>16} {\"Paper LP\":>30}')
print('-'*90)
for r in sorted(results, key=lambda x: -x.get('protb_mean', 0)):
    print(f'{r[\"model\"]:<28} {r[\"resolution\"]:>5} {r[\"feature_dim\"]:>6} '
          f'{r[\"protb_mean\"]*100:>8.2f}±{r[\"protb_std\"]*100:.2f} {r.get(\"paper_lp\",\"N/A\"):>30}')
" 2>&1
echo "[$(date '+%H:%M:%S')] DONE"
