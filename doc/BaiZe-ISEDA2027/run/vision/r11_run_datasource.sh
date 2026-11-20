#!/bin/bash
# R11-F — Data-source horizontal comparison (approved 2026-10-04(六)).
#   5 arms, fixed 30k steps / w512 / InfoNCE / frozen CLIP-768 / IN-1k frozen-trunk lp.
#   ONLY the data source / caption granularity changes:
#     A  GPIC short          (--data-source gpic --caption-type short)
#     B  GPIC medium         (--data-source gpic --caption-type medium)
#     C  GPIC short+medium   (--data-source gpic --caption-type short+medium, ≈90%)
#     E  CC12M (pure)        (--data-source wds, NO Amshaker)
#     D  en500k              (--data-source wds; ⚠️ in-domain for IN-1k, single-listed)
#   Order: A → B → C → E → D  (answer Q1/Q3 first; D last, special-cased).
#
#   ⚠️ GPIC arms A/B/C use the SAME frozen tar snapshot (written to
#      /tmp/r11f_gpic_snapshot.txt at script start) so the download adding
#      tars between arms does not break comparability.
#
# Pre-registered verdicts (EXPERIMENTS_VISION_ROUND11.md §15.3):
#   Q1: medium−short ≥ +1.5 lp pp @step30k -> "longer caption helps"
#       medium−short ≤ −1.5                -> "longer caption hurts"
#       else                               -> "no significant difference"
#   Q2: best of {A,B,E} leads 2nd by ≥ +1.5 -> "significantly better source"
#       else                                -> "no significant difference"
#   Q3: C−A ≥ +1.5 -> "merging helps"; else -> "no significant difference"
#   D:  en500k single-listed (in-domain + ~30 epochs repeat), NOT ranked with A/B/C/E.
#
# Noise band (ROUND10 §1.5): same-(N,M) cross-run variance ≈ 0.5–1.1 pp → threshold ±1.5.
# Main metric = IN-1k frozen-trunk lp @ step30k (with step10k/20k trajectory).
#
# Usage:
#   bash r11_run_datasource.sh [steps=30000] [num_workers=6]
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export MASTER_ADDR=127.0.0.1
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
STEPS="${1:-30000}"
NW="${2:-6}"

GPIC='/nas_inference/app.e0031982/datasets/stanford-vision-lab/gpic/train/*.tar'
CC12M='/nas_train/app.e0031982/datasets/conceptual-captions-12m-webdataset/data/*.tar'
EN500K='/nas_train/app.e0031982/datasets/baize-vision/en500k/*.tar'
EVAL='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out
LOG=/tmp/r11f_datasource.log
SNAPSHOT=/tmp/r11f_gpic_snapshot.txt

# ---- freeze GPIC tar snapshot (A/B/C comparability) ---- #
/bin/ls $GPIC 2>/dev/null | sort > "$SNAPSHOT"
GPIC_TAR_COUNT=$(wc -l < "$SNAPSHOT")

echo "===== R11-F data-source comparison START steps=$STEPS nw=$NW $(date '+%F %T') =====" > "$LOG"
echo "----- hostname -----" >> "$LOG"
hostname >> "$LOG" 2>&1
echo "----- GPIC frozen tar snapshot: $GPIC_TAR_COUNT tars -> $SNAPSHOT -----" >> "$LOG"
echo "----- CC12M tar count -----" >> "$LOG"
/bin/ls $CC12M 2>/dev/null | wc -l >> "$LOG" 2>&1
echo "----- en500k tar count -----" >> "$LOG"
/bin/ls $EN500K 2>/dev/null | wc -l >> "$LOG" 2>&1
echo "----- GPU exclusivity check (verbatim) -----" >> "$LOG"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv >> "$LOG" 2>&1
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1

# ---- helper: run one arm (train 30k + auto 4-ckpt IN-1k lp) ---- #
# args: arm_label  data_arg  data_source  caption_type  out_subdir
run_arm() {
    local ARM="$1" DATAARG="$2" DS="$3" CT="$4" OUTSUB="$5"
    local OUT="$OUTROOT/$OUTSUB"
    echo "===== R11-F arm $ARM START data-source=$DS caption-type=$CT $(date '+%F %T') =====" >> "$LOG"
    "$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
        --master_addr=$MASTER_ADDR --master_port=$((29400 + RANDOM % 1000)) \
        r9_train.py --tower openvision2 --width 512 --depth 30 \
        --steps "$STEPS" --resolution 224 --patch 16 \
        --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234 \
        --loss clip \
        --data "$DATAARG" --data-source "$DS" --caption-type "$CT" \
        --output-dir "$OUT" \
        --log-every 50 --probe-every 300 --probe-n 128 --num-workers "$NW" \
        --eval-data "$EVAL" \
        >> "$LOG" 2>&1
    local rc=$?
    echo "===== R11-F arm $ARM training done (exit $rc) $(date '+%F %T') =====" >> "$LOG"
    local CKPTS=()
    if [ "$rc" -eq 0 ]; then
        for f in "$OUT"/vision_step10000.pt "$OUT"/vision_step20000.pt "$OUT"/vision_step30000.pt; do
            [ -f "$f" ] && CKPTS+=("$f") || echo "[skip missing] $f" >> "$LOG"
        done
        local FINAL="$OUT/vision.pt"; [ -f "$FINAL" ] || FINAL="$OUT/vision_fused.pt"
        [ -f "$FINAL" ] && CKPTS+=("$FINAL") || echo "[skip missing] $OUT/vision.pt|vision_fused.pt" >> "$LOG"
        echo "===== R11-F arm $ARM IN-1k eval on ${#CKPTS[@]} ckpts =====" >> "$LOG"
        if [ "${#CKPTS[@]}" -gt 0 ]; then
            "$PY" r8_eval_in1k.py --ckpts "${CKPTS[@]}" >> "$LOG" 2>&1
        fi
    else
        echo "===== R11-F arm $ARM FAILED exit $rc; skip eval =====" >> "$LOG"
    fi
    echo "===== R11-F arm $ARM ALL DONE $(date '+%F %T') =====" >> "$LOG"
}

# ---- Arm A: GPIC short (consistency cross-check vs R11-E) ---- #
run_arm A "$SNAPSHOT" gpic short R11F_gpic_short_w512

# ---- Arm B: GPIC medium (Q1: longer caption) ---- #
run_arm B "$SNAPSHOT" gpic medium R11F_gpic_medium_w512

# ---- Arm C: GPIC short+medium ≈90% (Q3: merge) ---- #
run_arm C "$SNAPSHOT" gpic short+medium R11F_gpic_shortmedium_w512

# ---- Arm E: pure CC12M (no Amshaker) ---- #
run_arm E "$CC12M" wds short R11F_cc12m_w512

# ---- Arm D: en500k (⚠️ in-domain, single-listed, NOT ranked) ---- #
run_arm D "$EN500K" wds short R11F_en500k_w512

echo "===== R11-F ALL 5 ARMS DONE $(date '+%F %T') =====" >> "$LOG"
