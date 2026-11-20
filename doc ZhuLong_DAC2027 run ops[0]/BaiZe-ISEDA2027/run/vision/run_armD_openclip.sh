#!/bin/bash
# ==============================================================================
# run_armD_openclip.sh — ArmD (2026-10-19): open_clip ViT-B/16 + AIMv2-style
#
# Operator instruction 2026-10-19 (user direct order, highest priority):
#   ArmD vs ArmC = FOUR variables (NOT a single-variable ablation):
#     1. data    3 sources -> 6 sources  (ArmC's 3 + WebMix-38M + wit_base + InternVL-SA1B)
#     2. epoch   4 -> 3
#     3. lr      1e-3 -> 2e-3
#     4. min_lr  1e-5 -> 2e-5
#   Everything else identical to ArmC (verified actual config):
#   - open_clip ViT-B/16 224px (86.2M visual / 149.6M total, both towers random)
#   - AIMv2-style: 1.0*InfoNCE + 1.0*masked-patch-MSE, mask_ratio=0.6
#   - GBS=8192 (MBS=512*8*accum=2); OOM fallback GBS=4096 (MBS=256*8*2, STEPS*2)
#   - warmup=2000, cosine->min_lr=2e-5, AdamW wd=0.01 betas=(0.9,0.98), bf16(AMP)
#   - grad_clip=1.0, seed=1234, fused-adamw, keep-ckpts 2
#   - Patch tokens via forward hook (single forward, no double)
#   - Independent output dir armD_20261019_* (does NOT touch/overwrite armB/armC-*)
#
# STEPS is read from env $ARMD_STEPS (set by run_armD_launch_when_ready.sh after
# snapshot pair-count). Default 63361 ~= ceil(3 * 173M / 8192).
#
# Launch:
#   setsid bash run_armD_openclip.sh > /tmp/armD_openclip_train.log 2>&1 < /dev/null &
# ==============================================================================
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export NCCL_TIMEOUT=1800
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export MASTER_ADDR=127.0.0.1
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python

SNAPSHOT_FILE="data_snapshot_20261019_armD.txt"
FAIR_DATA="${SNAPSHOT_FILE}"
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out
OUT="$OUTROOT/armD_20261019_aimv2_openclip_vitb16_224"

LOG=/tmp/armD_openclip_train.log
STEPS=${ARMD_STEPS:-63361}        # ceil(3 * total_pairs / 8192); set by launcher
STEPS_FALLBACK=$((STEPS * 2))     # half GBS -> double steps to keep 3 epochs

# ---- MBS / accumulate (try 512 first, fallback to 256 on OOM) ----
MBS=${1:-512}
ACCUM=${2:-2}
if [ "$MBS" = "512" ]; then
    ACCUM=2  # GBS=512*8*2=8192
else
    ACCUM=2  # GBS=256*8*2=4096
fi

echo "===== ArmD open_clip ViT-B/16 + AIMv2-style START $(date '+%F %T') =====" | tee "$LOG"
echo "[ArmD] model=open_clip ViT-B/16 224px (86.2M visual, 149.6M total, from scratch)" >> "$LOG"
echo "[ArmD] objective=AIMv2-style: 1.0*InfoNCE + 1.0*masked-patch-MSE (mask_ratio=0.6)" >> "$LOG"
echo "[ArmD] data=$FAIR_DATA (ArmC 3-src snapshot base + WebMix-38M + wit_base + InternVL-SA1B)" >> "$LOG"
echo "[ArmD] schedule: lr=2e-3, warmup=2000, cosine->min_lr=2e-5, steps=$STEPS (3 epochs)" >> "$LOG"
echo "[ArmD] batch=MBS=${MBS}/GPU, GBS=$((MBS*8*ACCUM)), AdamW wd=0.01 betas=(0.9,0.98), bf16(AMP) fused=True" >> "$LOG"
echo "[ArmD] VARIABLES vs ArmC: data 3src->6src, epoch 4->3, lr 1e-3->2e-3, min_lr 1e-5->2e-5 (FOUR vars, not single-var ablation)" >> "$LOG"
echo "[ArmD] output_dir=$OUT" >> "$LOG"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv >> "$LOG" 2>&1

RESUME_FLAG=""
if [ -f "$OUT/latest.pt" ]; then
    RESUME_FLAG="--resume"
    echo "[ArmD] found latest.pt -> resuming" >> "$LOG"
fi

"$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
    --master_addr=$MASTER_ADDR --master_port=$((29800 + RANDOM % 1000)) \
    armB_aimv2_openclip.py \
    --data "$FAIR_DATA" --data-source mixed --caption-type all \
    --output-dir "$OUT" --steps "$STEPS" \
    --batch-size "$MBS" --accumulate "$ACCUM" \
    --lr 2e-3 --min-lr 2e-5 --warmup 2000 \
    --wd 0.01 --beta1 0.9 --beta2 0.98 --precision bf16 --grad-clip 1.0 \
    --contrast-weight 1.0 --patch-loss-weight 1.0 --mask-ratio 0.6 \
    --save-every 10000 --log-every 20 --num-workers 12 --seed 1234 \
    --persistent-workers --prefetch-factor 4 --pin-memory \
    --cudnn-benchmark --fused-adamw --keep-ckpts 2 \
    $RESUME_FLAG >> "$LOG" 2>&1

rc=$?
if [ $rc -ne 0 ] && [ "$MBS" = "512" ] && grep -qi "out of memory\|CUDA error\|OutOfMemory" "$LOG"; then
    echo "===== OOM at MBS=512, falling back to MBS=256 GBS=4096 STEPS=$STEPS_FALLBACK $(date '+%F %T') =====" >> "$LOG"
    MBS=256
    ACCUM=2
    "$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
        --master_addr=$MASTER_ADDR --master_port=$((29800 + RANDOM % 1000)) \
        armB_aimv2_openclip.py \
        --data "$FAIR_DATA" --data-source mixed --caption-type all \
        --output-dir "$OUT" --steps "$STEPS_FALLBACK" \
        --batch-size "$MBS" --accumulate "$ACCUM" \
        --lr 2e-3 --min-lr 2e-5 --warmup 2000 \
        --wd 0.01 --beta1 0.9 --beta2 0.98 --precision bf16 --grad-clip 1.0 \
        --contrast-weight 1.0 --patch-loss-weight 1.0 --mask-ratio 0.6 \
        --save-every 10000 --log-every 20 --num-workers 12 --seed 1234 \
        --persistent-workers --prefetch-factor 4 --pin-memory \
        --cudnn-benchmark --fused-adamw --keep-ckpts 2 \
        $RESUME_FLAG >> "$LOG" 2>&1
    rc=$?
fi

echo "===== ArmD done (exit $rc) $(date '+%F %T') =====" >> "$LOG"
exit $rc
