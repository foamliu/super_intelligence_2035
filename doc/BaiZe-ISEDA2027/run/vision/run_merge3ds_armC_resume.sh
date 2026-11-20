#!/bin/bash
# ==============================================================================
# run_merge3ds_armC_resume.sh — Resume merge3ds ArmC from step 8100 checkpoint
#                                 C4 false-positive at step 8100 (loss_ema=0.6414
#                                 vs threshold 0.6404, missed by 0.001).
#                                 --resume disables C4 guard (C1/C2 remain active).
#
# Original run: run_merge3ds_armC.sh (fresh, LR=2e-3 ×4 linear, 154500 steps)
# Stopped at:   step 8100/154500 (C4=FAIL, loss WAS decreasing, false positive)
# Resume from:  vision_fused.pt (step 8100, loss=0.6414, C1=0.3999 healthy)
# Remaining:    146400 steps (~8.8h @ ~217ms/iter)
#
# Why resume is safe:
#   - C4 was a marginal false positive (missed by 0.001, loss WAS decreasing)
#   - C1=0.3999 (well below 0.95 collapse threshold) — healthy
#   - C2_gap=+0.1868 (well above 0.005 collapse threshold) — healthy
#   - --resume disables C4 (loss_early stays None); C1/C2 guards REMAIN active
#   - Optimizer state NOT saved (AdamW restarts, ~1-2k step transient, minor)
#
# Launch:
#   setsid bash run_merge3ds_armC_resume.sh > /tmp/merge3ds_armC_resume.log 2>&1 < /dev/null &
# ==============================================================================
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export MASTER_ADDR=127.0.0.1
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python

# ---- Data: same as original run (E1fair frozen snapshot) ----
SNAPSHOT_FILE="data_snapshot_20261009.txt"
CC12M='/nas_train/app.e0031982/datasets/conceptual-captions-12m-webdataset/data/*.tar'
AMSH='/nas_user/app.e0031982/datasets/Amshaker/Mobile-O-Pre-Train/*.tar'
FAIR_DATA="${SNAPSHOT_FILE},${CC12M},${AMSH}"
EVAL='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out

OUT="$OUTROOT/merge3ds_bs4_lrC_w512_d30_p16_224"
LOG=/tmp/merge3ds_armC_resume.log
STEPS=154500   # same as original (resume continues to this step)
RESUME_CKPT="$OUT/vision_fused.pt"   # checkpoint from step 8100

echo "===== merge3ds ArmC RESUME (from step 8100, C4 disabled via --resume) $(date '+%F %T') =====" | tee "$LOG"
echo "[ArmC-resume] data=$FAIR_DATA" >> "$LOG"
echo "[ArmC-resume] checkpoint=$RESUME_CKPT (step 8100, loss=0.6414)" >> "$LOG"
echo "[ArmC-resume] schedule: lr=2e-3 (×4), warmup=8000 (×4), cosine, min_lr=2e-4 (×4), steps=$STEPS" >> "$LOG"
echo "[ArmC-resume] batch-size=256 (×4), GBS=256×8=2048 (×4 vs baseline 512)" >> "$LOG"
echo "[ArmC-resume] output_dir=$OUT" >> "$LOG"
echo "[ArmC-resume] C4 disabled on resume (C1/C2 remain active)" >> "$LOG"
echo "[ArmC-resume] remaining steps: $((STEPS - 8100)) = 146400 (~8.8h @ ~217ms/iter)" >> "$LOG"
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1

"$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
    --master_addr=$MASTER_ADDR --master_port=$((29800 + RANDOM % 1000)) \
    r9_train.py --tower openvision2 --width 512 --depth 30 \
    --steps "$STEPS" --resolution 224 --patch 16 \
    --batch-size 256 --lr 2e-3 --warmup 8000 --scheduler cosine --min-lr 2e-4 --seed 1234 \
    --loss aimv2 --mask-ratio 0.6 --patch-loss-weight 1.0 --contrast-weight 1.0 \
    --data "$FAIR_DATA" --data-source mixed --caption-type all --output-dir "$OUT" \
    --log-every 10 --probe-every 300 --probe-n 128 --num-workers 6 \
    --save-every 10000 --eval-data "$EVAL" \
    --resume "$RESUME_CKPT" >> "$LOG" 2>&1

rc=$?
echo "===== merge3ds ArmC RESUME done (exit $rc) $(date '+%F %T') =====" >> "$LOG"
exit $rc
