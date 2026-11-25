#!/bin/bash
# R11-E — GPIC data axis ("10.9M same-N two points" version, approved 2026-10-04(四)).
#   Question: does swapping the data arm to GPIC `short` raise the IN-1k frozen-trunk lp
#   ceiling vs the CC12M+Amshaker baseline, at the SAME sample budget N?
#   Fixed recipe (identical to R9 stage-1 w512 / R11-L arm ① baseline, ONLY the data changes):
#   - Tower: OpenVision2 w512 (126.78M), depth30 / patch16 / 224².
#   - Text tower: FROZEN CLIP-768 (openai/clip-vit-large-patch14-336), context 77.
#   - Optimizer/schedule: AdamW lr 3e-3 warmup 20, seed 1234, bf16, bs64×8=512.
#   - Objective: InfoNCE (CLIP, 512-negative) — identical to baseline arm ①.
#   - Data: GPIC `short` only (~10.9M pairs; --data-source gpic filters caption_type=='short').
#   - Sample budget: N=15.36M = 30k steps; comparison points = step{10k,20k} = N{5.12,10.24}M.
#   - Eval: IN-1k frozen-trunk lp (r8_eval_in1k.py) on step{10k,20k,30k}+final.
#   Pre-registered verdict (EXPERIMENTS_VISION_ROUND11.md §13.3):
#     baseline   @5.12M=3.43%    @10.24M=5.45%
#     both ≥ +1.5 (≥4.93 / ≥6.95) -> "GPIC raises ceiling"
#     both ≤ −1.5 (≤1.93 / ≤3.95) -> "GPIC worse"
#     else                        -> "no significant difference (not raised)"
#   Comparable range: ≤10.9M unique short pairs -> verdict only for N≤10.24M; step 30k repeats data.
# Usage:
#   bash r11_run_gpic.sh [steps=30000] [num_workers=6]
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

# Data arm B: GPIC train tars (raw {key}.json + {key}.jpg|png; loader keeps caption_type=='short').
GPIC='/nas_inference/app.e0031982/datasets/stanford-vision-lab/gpic/train/*.tar'
DATA="$GPIC"
EVAL='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out
OUT="$OUTROOT/R11E_gpic_w512"
LOG=/tmp/r11_gpic.log

echo "===== R11-E GPIC-short START steps=$STEPS nw=$NW $(date '+%F %T') =====" > "$LOG"
echo "----- hostname -----" >> "$LOG"
hostname >> "$LOG" 2>&1
echo "----- GPIC train tar count (verbatim) -----" >> "$LOG"
/bin/ls $GPIC 2>/dev/null | wc -l >> "$LOG" 2>&1
echo "----- GPU exclusivity check (verbatim) -----" >> "$LOG"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv >> "$LOG" 2>&1
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1

echo "===== R11-E openvision2 width=512 loss=clip data-source=gpic ($STEPS steps) START $(date '+%F %T') =====" >> "$LOG"
"$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
    --master_addr=$MASTER_ADDR --master_port=$((29400 + RANDOM % 1000)) \
    r9_train.py --tower openvision2 --width 512 --depth 30 \
    --steps "$STEPS" --resolution 224 --patch 16 \
    --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234 \
    --loss clip \
    --data "$DATA" --data-source gpic --output-dir "$OUT" \
    --log-every 50 --probe-every 300 --probe-n 128 --num-workers "$NW" \
    --eval-data "$EVAL" \
    >> "$LOG" 2>&1
rc=$?
echo "===== R11-E openvision2 width=512 loss=clip data-source=gpic done (exit $rc) $(date '+%F %T') =====" >> "$LOG"

CKPTS=()
if [ "$rc" -eq 0 ]; then
    for f in "$OUT"/vision_step10000.pt "$OUT"/vision_step20000.pt "$OUT"/vision_step30000.pt; do
        [ -f "$f" ] && CKPTS+=("$f") || echo "[skip missing] $f" >> "$LOG"
    done
    FINAL="$OUT/vision.pt"; [ -f "$FINAL" ] || FINAL="$OUT/vision_fused.pt"
    [ -f "$FINAL" ] && CKPTS+=("$FINAL") || echo "[skip missing] $OUT/vision.pt|vision_fused.pt" >> "$LOG"
    echo "===== R11-E training done; IN-1k eval on ${#CKPTS[@]} ckpts =====" >> "$LOG"
    if [ "${#CKPTS[@]}" -gt 0 ]; then
        "$PY" r8_eval_in1k.py --ckpts "${CKPTS[@]}" >> "$LOG" 2>&1
    fi
else
    echo "===== R11-E FAILED exit $rc; skip eval =====" >> "$LOG"
fi
echo "===== R11-E GPIC-short ALL DONE $(date '+%F %T') =====" >> "$LOG"