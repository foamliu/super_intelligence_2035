#!/bin/bash
# R11-F continuation — runs ONLY arms B, C, E, D (Arm A already completed 2026-10-04 21:44).
#   Reuses the SAME frozen GPIC tar snapshot (/tmp/r11f_gpic_snapshot.txt, 2424 tars)
#   so A/B/C remain comparable.  Appends to the same log /tmp/r11f_datasource.log.
#
#   Arms (same as r11_run_datasource.sh minus A):
#     B  GPIC medium         (--data-source gpic --caption-type medium)
#     C  GPIC short+medium   (--data-source gpic --caption-type short+medium, ≈90%)
#     E  CC12M (pure)        (--data-source wds, NO Amshaker)
#     D  en500k              (--data-source wds; ⚠️ in-domain, single-listed)
#   Order: B → C → E → D
#
# Usage:  setsid bash r11f_continue.sh 30000 6 &
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

CC12M='/nas_train/app.e0031982/datasets/conceptual-captions-12m-webdataset/data/*.tar'
EN500K='/nas_train/app.e0031982/datasets/baize-vision/en500k/*.tar'
EVAL='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out
LOG=/tmp/r11f_datasource.log          # append to same log
SNAPSHOT=/tmp/r11f_gpic_snapshot.txt   # reuse frozen snapshot (2424 tars)

echo "" >> "$LOG"
echo "===== R11-F CONTINUATION (arms B,C,E,D) START steps=$STEPS nw=$NW $(date '+%F %T') =====" >> "$LOG"
echo "----- reusing frozen GPIC snapshot: $(wc -l < "$SNAPSHOT") tars -----" >> "$LOG"
echo "----- GPU exclusivity check -----" >> "$LOG"
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1

# ---- helper: run one arm (train 30k + auto 4-ckpt IN-1k lp) ---- #
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

# ---- Arm B: GPIC medium (Q1: longer caption) ---- #
run_arm B "$SNAPSHOT" gpic medium R11F_gpic_medium_w512

# ---- Arm C: GPIC short+medium ≈90% (Q3: merge) ---- #
run_arm C "$SNAPSHOT" gpic short+medium R11F_gpic_shortmedium_w512

# ---- Arm E: pure CC12M (no Amshaker) ---- #
run_arm E "$CC12M" wds short R11F_cc12m_w512

# ---- Arm D: en500k (⚠️ in-domain, single-listed, NOT ranked) ---- #
run_arm D "$EN500K" wds short R11F_en500k_w512

echo "===== R11-F CONTINUATION ALL DONE (arms B,C,E,D) $(date '+%F %T') =====" >> "$LOG"
