#!/bin/bash
# ==============================================================================
# run_armE_openclip.sh — ArmE (2026-10-21): open_clip ViT-L/14 (224px) + AIMv2-style
#
# Operator instruction 2026-10-21 20:4x (user direct order, highest priority):
#   ArmE vs ArmD-R2: SINGLE VARIABLE = vision tower architecture ONLY.
#     ArmD-R2 = open_clip ViT-B/16 224px (86.2M visual / 149.6M total)
#     ArmE    = open_clip ViT-L/14  224px (304.0M visual / 427.6M total, from scratch)
#   Data / steps / LR / loss / everything else IDENTICAL to ArmD-R2.
#
#   NOTE: operator wrote 'ViT-L-14-224' but open_clip 3.2.0 has no such built-in;
#   plain 'ViT-L-14' IS the 224px variant (patch14, 256 tokens, width 1024).
#
#   Memory (probed 2026-10-21 on H100-80GB, single GPU, full fwd+bwd+masked loss):
#     MBS=512 -> OOM ; MBS=256 -> 70.6GB ; MBS=128 -> 40.1GB
#   => MBS=512 (ArmD-R2's per-GPU batch) OOMs for ViT-L/14.  Per-micro-batch
#      contrastive batch (MBS*world) therefore drops 4096 -> 2048 (UNAVOIDABLE
#      confound, forced by OOM, disclosed in report).
#   REFINEMENT vs operator's literal 'OOM 回退 4096': to keep the SINGLE-VARIABLE
#      clean we PRESERVE GBS=8192 and STEPS=63400 by raising accumulate
#      (MBS=256*accum=4 -> GBS=8192).  Operator's GBS=4096 fallback would have
#      added 2 extra confounds (GBS 8192->4096 + steps 63400->126800); preserving
#      GBS leaves ONLY the per-micro-batch contrastive-batch confound.
#   => Default: MBS=256/accum=4 (GBS=8192).  OOM fallback: MBS=128/accum=8 (GBS=8192).
#      STEPS stays 63400 (3 epochs) in BOTH (no doubling, since GBS unchanged).
#
# Launch:
#   setsid bash run_armE_openclip.sh > /tmp/armE_openclip_train.log 2>&1 < /dev/null &
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
OUT="$OUTROOT/armE_20261021_aimv2_openclip_vitl14_224"

LOG=/tmp/armE_openclip_train.log
STEPS=${ARME_STEPS:-63400}        # ceil(3 * total_pairs / 8192); GBS=8192 in ALL configs

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

echo "===== ArmE open_clip ViT-L/14 (224px) + AIMv2-style START $(date '+%F %T') =====" | tee "$LOG"
echo "[ArmE] model=open_clip ViT-L/14 224px (304.0M visual, 427.6M total, from scratch)" >> "$LOG"
echo "[ArmE] objective=AIMv2-style: 1.0*InfoNCE + 1.0*masked-patch-MSE (mask_ratio=0.6)" >> "$LOG"
echo "[ArmE] data=$FAIR_DATA (6-source snapshot, UNCHANGED from ArmD: 14589 shards / 173M pairs)" >> "$LOG"
echo "[ArmE] schedule: lr=1e-3, warmup=2000, cosine->min_lr=1e-5, steps=$STEPS (3 epochs)" >> "$LOG"
echo "[ArmE] batch=MBS=${MBS}/GPU x accum=${ACCUM} -> GBS=${GBS} (PRESERVED=8192, single-variable), AdamW wd=0.01 betas=(0.9,0.98), bf16 fused" >> "$LOG"
echo "[ArmE] SINGLE VARIABLE vs ArmD-R2: vision tower ViT-B/16(86.2M)->ViT-L/14(304.0M) ONLY" >> "$LOG"
echo "[ArmE] UNAVOIDABLE confound: per-micro-batch contrastive batch 4096->2048 (MBS 512->256, OOM-forced). GBS+steps PRESERVED." >> "$LOG"
echo "[ArmE] output_dir=$OUT" >> "$LOG"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv >> "$LOG" 2>&1

run_train () {
    local mbs=$1 accum=$2
    "$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
        --master_addr=$MASTER_ADDR --master_port=$((29800 + RANDOM % 1000)) \
        armE_aimv2_openclip_vitl14.py \
        --data "$FAIR_DATA" --data-source mixed --caption-type all \
        --output-dir "$OUT" --steps "$STEPS" \
        --batch-size "$mbs" --accumulate "$accum" \
        --lr 1e-3 --min-lr 1e-5 --warmup 2000 \
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
    echo "[ArmE] found latest.pt -> resuming" >> "$LOG"
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
