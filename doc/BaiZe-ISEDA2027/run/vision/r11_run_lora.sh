#!/bin/bash
# R11-L2 — text-tower unfreeze arm: LoRA (lightweight) vs frozen CLIP-768 baseline.
#   Fixed recipe (identical to R9 stage-1 w512 / R11-L arm ① baseline, ONLY the text tower changes):
#   - Tower: OpenVision2 w512 (126.78M), depth30 / patch16 / 224².
#   - Text tower: CLIP-768 (openai/clip-vit-large-patch14-336), context 77, with
#     zero-init LoRA on q_proj+v_proj (r=8, alpha=16) of each of the 12 BERT layers.
#     LoRA adds +0 to the weights at step 0 -> the arm starts byte-identical to frozen.
#     Pre-trained CLIP weights stay frozen; only lora_A/lora_B train (~0.30M params).
#     LoRA uses a SEPARATE lr group (lr=1e-4, warmup 20, wd=0) vs vision lr=3e-3.
#   - Data: CC12M + Amshaker (same globs as R9/R10/R11-L).
#   - Optimizer/schedule: AdamW; vision lr 3e-3 warmup 20; seed 1234; bf16; bs64×8=512.
#   - Sample budget: N=15.36M = 30k steps (= R9 stage-1 anchor).
#   - Objective: InfoNCE (CLIP, 512-negative) — identical to baseline arm ①.
#   - Eval: IN-1k frozen-trunk lp (r8_eval_in1k.py) on step{10k,20k,30k}+final (vision trunk only).
#   - MUST re-run R4 collapse criteria C1–C4 (probe-every 300, auto-abort on collapse).
#   Pre-registered verdict (EXPERIMENTS_VISION_ROUND11.md §11):
#     - collapse (C1>0.95 or C2_gap≤0.005 or C4 fail)     -> NEGATIVE (unfreeze@this recipe collapses).
#     - lp > baseline(6.08%@15.36M) + 1.5                  -> text-tower freeze IS capping the asymptote.
#   Fairness (§3/§11): LoRA adds ~0.30M text params (reported), no extra tokens (no decoder).
# Usage:
#   bash r11_run_lora.sh [steps=30000]
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export MASTER_ADDR=127.0.0.1
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
STEPS="${1:-30000}"
NW=6

CC12M='/nas_train/app.e0031982/datasets/conceptual-captions-12m-webdataset/data/*.tar'
AMSH='/nas_user/app.e0031982/datasets/Amshaker/Mobile-O-Pre-Train/*.tar'
DATA="${CC12M},${AMSH}"
EVAL='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out
OUT="$OUTROOT/R11L2_lora_w512"
LOG=/tmp/r11_lora.log

echo "===== R11-L2 LoRA(w512) START steps=$STEPS $(date '+%F %T') =====" > "$LOG"
echo "----- hostname -----" >> "$LOG"
hostname >> "$LOG" 2>&1
echo "----- GPU exclusivity check (verbatim) -----" >> "$LOG"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv >> "$LOG" 2>&1
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1

echo "===== R11-L2 openvision2 width=512 loss=clip text-finetune=lora ($STEPS steps) START $(date '+%F %T') =====" >> "$LOG"
"$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
    --master_addr=$MASTER_ADDR --master_port=$((29400 + RANDOM % 1000)) \
    r9_train.py --tower openvision2 --width 512 --depth 30 \
    --steps "$STEPS" --resolution 224 --patch 16 \
    --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234 \
    --loss clip --text-finetune lora --lora-rank 8 --lora-alpha 16 --lora-lr 1e-4 \
    --data "$DATA" --data-source wds --output-dir "$OUT" \
    --log-every 50 --probe-every 300 --probe-n 128 --num-workers "$NW" \
    --eval-data "$EVAL" \
    >> "$LOG" 2>&1
rc=$?
echo "===== R11-L2 openvision2 width=512 loss=clip text-finetune=lora done (exit $rc) $(date '+%F %T') =====" >> "$LOG"

CKPTS=()
if [ "$rc" -eq 0 ]; then
    for f in "$OUT"/vision_step10000.pt "$OUT"/vision_step20000.pt "$OUT"/vision_step30000.pt; do
        [ -f "$f" ] && CKPTS+=("$f") || echo "[skip missing] $f" >> "$LOG"
    done
    FINAL="$OUT/vision.pt"; [ -f "$FINAL" ] || FINAL="$OUT/vision_fused.pt"
    [ -f "$FINAL" ] && CKPTS+=("$FINAL") || echo "[skip missing] $OUT/vision.pt|vision_fused.pt" >> "$LOG"
    echo "===== R11-L2 training done; IN-1k eval on ${#CKPTS[@]} ckpts ===== " >> "$LOG"
    if [ "${#CKPTS[@]}" -gt 0 ]; then
        "$PY" r8_eval_in1k.py --ckpts "${CKPTS[@]}" >> "$LOG" 2>&1
    fi
else
    echo "===== R11-L2 lora FAILED with exit $rc; skipping eval. =====" >> "$LOG"
fi
echo "===== R11-L2 LoRA(w512) ALL DONE $(date '+%F %T') =====" >> "$LOG"