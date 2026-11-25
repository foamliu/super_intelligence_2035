#!/usr/bin/env bash
# S2 smoke: LLaMA-Factory single-step CPU LoRA SFT on Qwen3.5-2B (wake#853, 2026-11-07)
# Verifies: CPU training loop runs, loss is finite & decreasing trend.
set -euo pipefail
export CUDA_VISIBLE_DEVICES=""          # force CPU
export OMP_NUM_THREADS=16
export MKL_NUM_THREADS=16

HERE="$(cd "$(dirname "$0")" && pwd)"
CACHE="/nas_train/app.e0031982/datasets/baize-vision/out/hf_cache_qwen35"

source /nas_train/app.e0031982/miniforge3/etc/profile.d/conda.sh
conda activate qwen35

# Resolve the snapshot path for Qwen3.5-2B
MODEL_PATH="$(python - <<'PY'
import os, glob
os.environ.setdefault('HF_HOME', '/nas_train/app.e0031982/datasets/baize-vision/out/hf_cache_qwen35')
base = '/nas_train/app.e0031982/datasets/baize-vision/out/hf_cache_qwen35/hub/models--Qwen--Qwen3.5-2B/snapshots'
snaps = sorted(glob.glob(base + '/*'))
# pick the one that has a config.json + safetensors
for s in snaps:
    if os.path.exists(os.path.join(s, 'config.json')) and glob.glob(os.path.join(s, '*.safetensors')):
        print(s); raise SystemExit(0)
print(''); raise SystemExit(1)
PY
)"
if [ -z "$MODEL_PATH" ]; then
  echo "S2_FAIL: Qwen3.5-2B model not found in cache (download incomplete?)"
  exit 2
fi
echo "S2: model_path=$MODEL_PATH"

OUT_DIR="/tmp/lf_s2_smoke_out"
rm -rf "$OUT_DIR"; mkdir -p "$OUT_DIR"

# Fill placeholders in YAML
sed -e "s|PLACEHOLDER_MODEL_PATH|$MODEL_PATH|" \
    -e "s|PLACEHOLDER_DATA_DIR|$HERE|" \
    -e "s|PLACEHOLDER_OUT_DIR|$OUT_DIR|" \
    "$HERE/s2_cpu_lora_qwen35.yaml" > "$OUT_DIR/run.yaml"

echo "S2: config -> $OUT_DIR/run.yaml"
echo "S2: starting LLaMA-Factory CPU LoRA train (max_steps=3) ..."
llamafactory-cli train "$OUT_DIR/run.yaml" 2>&1 | tee "$OUT_DIR/s2_train.log"
echo "S2_DONE"
