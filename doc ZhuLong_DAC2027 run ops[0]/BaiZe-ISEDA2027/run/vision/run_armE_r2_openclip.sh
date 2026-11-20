#!/bin/bash
# ==============================================================================
# run_armE_r2_openclip.sh — ArmE-R2 (2026-10-22): open_clip ViT-L/14 (224px) + AIMv2-style
#
# Operator instruction 2026-10-22 14:2x (user direct order, highest priority):
#   ArmE diverged (C1=0.0014≈random at step~30000) with lr=1e-3/warmup=2000.
#   Root cause: ViT-L/14(304M) is 3.5x larger than ViT-B/16(86M) but used same
#   lr=1e-3 → update magnitude too large → repeated spikes, slow C1 recovery.
#   Decision: stop ArmE, rerun as ArmE-R2 with LOWER lr + LONGER warmup.
#
#   ArmE-R2 vs ArmE = ONLY 2 variables: peak LR 1e-3->5e-4, warmup 2000->3000.
#     Tower/data/GBS/steps/loss/mask/wd/seed ALL IDENTICAL to ArmE.
#   ArmE-R2 vs ArmD-R2 = 3 variables: tower(B->L) + LR + warmup (report separately).
#
#   Tower: open_clip ViT-L/14 224px (304.0M visual / 427.6M total, from scratch).
#   Data: data_snapshot_20261019_armD.txt (6-source / 14589 shards / 173M pairs).
#   Schedule: lr=5e-4, warmup=3000, cosine->min_lr=1e-5, steps=63400 (3 epochs).
#   Batch: MBS=256/accum=4 -> GBS=8192 (preserved). OOM fallback: MBS=128/accum=8.
#   Loss: 1.0*InfoNCE + 1.0*masked-patch-MSE, mask_ratio=0.6. wd=0.01. seed=1234.
#
# Launch:
#   setsid bash run_armE_r2_openclip.sh > /tmp/armE_r2_openclip_train.log 2>&1 < /dev/null &
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
OUT="$OUTROOT/armE_r2_20261022_aimv2_openclip_vitl14_224"

LOG=/tmp/armE_r2_openclip_train.log
STEPS=${ARME_R2_STEPS:-63400}        # ceil(3 * total_pairs / 8192); GBS=8192 in ALL configs

# ---- MBS / accumulate : all configs preserve GBS=8192 ----
#   $1 = MBS (default 256).  accum chosen so MBS*8*accum == 8192.
MBS=${1:-256}
case "$MBS" in
    512) ACCUM=2 ;;   # GBS=8192 (OOM on ViT-L/14; kept for completeness)
    256) ACCUM=4 ;;   # GBS=8192 (DEFAULT; peak ~70.6GB, fits 80GB H100)
    128) ACCUM=8 ;;   # GBS=8192 (fallback; peak ~40GB, very safe)
    *)   ACCUM=$((8192 / (MBS * 8))); [ "$ACCUM" -lt 1 ] && ACCUM=1 ;;
esac
GBS=$((MBS * 8 * ACCUM))

echo "===== ArmE-R2 open_clip ViT-L/14 (224px) + AIMv2-style START $(date '+%F %T') =====" | tee "$LOG"
echo "[ArmE-R2] model=open_clip ViT-L/14 224px (304.0M visual, 427.6M total, from scratch)" >> "$LOG"
echo "[ArmE-R2] objective=AIMv2-style: 1.0*InfoNCE + 1.0*masked-patch-MSE (mask_ratio=0.6)" >> "$LOG"
echo "[ArmE-R2] data=$FAIR_DATA (6-source snapshot, UNCHANGED from ArmE/ArmD: 14589 shards / 173M pairs)" >> "$LOG"
echo "[ArmE-R2] schedule: lr=5e-4, warmup=3000, cosine->min_lr=1e-5, steps=$STEPS (3 epochs)" >> "$LOG"
echo "[ArmE-R2] batch=MBS=${MBS}/GPU x accum=${ACCUM} -> GBS=${GBS} (PRESERVED=8192), AdamW wd=0.01 betas=(0.9,0.98), bf16 fused" >> "$LOG"
echo "[ArmE-R2] vs ArmE: ONLY 2 vars = peak LR 1e-3->5e-4 + warmup 2000->3000 (tower/data/GBS/steps all SAME)" >> "$LOG"
echo "[ArmE-R2] vs ArmD-R2: 3 vars = tower(B->L) + LR + warmup (report separately)" >> "$LOG"
echo "[ArmE-R2] UNAVOIDABLE confound (inherited from ArmE): per-micro-batch contrastive batch 4096->2048 (MBS 512->256, OOM-forced). GBS+steps PRESERVED." >> "$LOG"
echo "[ArmE-R2] output_dir=$OUT" >> "$LOG"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv >> "$LOG" 2>&1

run_train () {
    local mbs=$1 accum=$2
    "$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
        --master_addr=$MASTER_ADDR --master_port=$((29800 + RANDOM % 1000)) \
        armE_r2_aimv2_openclip_vitl14.py \
        --data "$FAIR_DATA" --data-source mixed --caption-type all \
        --output-dir "$OUT" --steps "$STEPS" \
        --batch-size "$mbs" --accumulate "$accum" \
        --lr 5e-4 --min-lr 1e-5 --warmup 3000 \
        --wd 0.01 --beta1 0.9 --beta2 0.98 --precision bf16 --grad-clip 1.0 \
        --contrast-weight 1.0 --patch-loss-weight 1.0 --mask-ratio 0.6 \
        --save-every 10000 --log-every 20 --num-workers 12 --seed 1234 \
        --persistent-workers --prefetch-factor 4 --pin-memory \
        --cudnn-benchmark --fused-adamw --keep-ckpts 2 \
        $RESUME_FLAG >> "$LOG" 2>&1
}

RESUME_FLAG=""
if [ -f "$OUT/latest.pt" ]; then
    RESUME_FLAG="--resume"
    echo "[ArmE-R2] found latest.pt -> resuming" >> "$LOG"
fi

run_train "$MBS" "$ACCUM"
rc=$?

# OOM fallback chain (preserve GBS=8192 by raising accum): 256->128
if [ $rc -ne 0 ] && [ "$MBS" = "256" ] && grep -qi "out of memory\|CUDA error\|OutOfMemory" "$LOG"; then
    echo "===== OOM at MBS=256/accum=4 (peak too high in real DDP), falling back to MBS=128/accum=8 GBS=8192 STEPS=$STEPS $(date '+%F %T') =====" >> "$LOG"
    MBS=128; ACCUM=8
    run_train "$MBS" "$ACCUM"
    rc=$?
fi
# also allow 512->256 fallback if someone launched with 512
if [ $rc -ne 0 ] && [ "$MBS" = "512" ] && grep -qi "out of memory\|CUDA error\|OutOfMemory" "$LOG"; then
    echo "===== OOM at MBS=512, falling back to MBS=256/accum=4 GBS=8192 STEPS=$STEPS $(date '+%F %T') =====" >> "$LOG"
    MBS=256; ACCUM=4
    run_train "$MBS" "$ACCUM"
    rc=$?
fi

echo "===== ArmE done (exit $rc) $(date '+%F %T') =====" >> "$LOG"
exit $rc
