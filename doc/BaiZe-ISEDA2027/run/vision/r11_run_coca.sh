#!/bin/bash
# R11-L arm ④ — CoCa (contrastive + autoregressive caption CE) vs R9 InfoNCE baseline.
#   Fixed recipe (identical to R9 stage-1 w512, ONLY the objective differs):
#   - Tower: OpenVision2 w512 (126.78M), depth30 / patch16 / 224².
#   - Text tower: FROZEN CLIP-768 (openai/clip-vit-large-patch14-336), context 77.
#   - Data: CC12M + Amshaker (same globs as R9/R10).
#   - Optimizer/schedule: AdamW lr 3e-3 warmup 20, seed 1234, bf16, bs64×8=512.
#   - Sample budget: N=15.36M = 30k steps (= R9 stage-1 anchor).
#   - Objective: InfoNCE contrastive (CLIP, 512-neg) + autoregressive caption CE
#     (self-written CoCa-style decoder: causal self-attn + cross-attn to patches,
#      frozen CLIP token embedding; caption_weight=2.0, decoder depth=4/w768/h12).
#   - Eval: IN-1k frozen-trunk lp (r8_eval_in1k.py) on step{10k,20k,30k}+final
#     (only the vision trunk is evaluated, same protocol as baseline).
#   Pre-registered verdict (EXPERIMENTS_VISION_ROUND11.md §1): lp > baseline(6.08%)+1.5
#   → locally overturn "25.1% is the contrastive asymptote". Fairness (§3): decoder
#   adds trainable params (reported as `[decoder] trainable=…M`), per-step caption
#   tokens (reported as `[decoder]` + train.log caption term), per-step wall time.
# Usage:
#   bash r11_run_coca.sh [steps=30000]
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
OUT="$OUTROOT/R11L_coca_w512"
LOG=/tmp/r11_coca.log

echo "===== R11-L arm4 CoCa START steps=$STEPS $(date '+%F %T') =====" > "$LOG"
echo "----- GPU exclusivity check (verbatim) -----" >> "$LOG"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv >> "$LOG" 2>&1
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1

echo "===== R11-L openvision2 width=512 loss=coca ($STEPS steps) START $(date '+%F %T') =====" >> "$LOG"
"$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
    --master_addr=$MASTER_ADDR --master_port=$((29400 + RANDOM % 1000)) \
    r9_train.py --tower openvision2 --width 512 --depth 30 \
    --steps "$STEPS" --resolution 224 --patch 16 \
    --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234 \
    --loss coca --caption-loss-weight 2.0 --decoder-depth 4 \
    --data "$DATA" --data-source wds --output-dir "$OUT" \
    --log-every 50 --probe-every 300 --probe-n 128 --num-workers "$NW" \
    --eval-data "$EVAL" \
    >> "$LOG" 2>&1
rc=$?
echo "===== R11-L openvision2 width=512 loss=coca done (exit $rc) $(date '+%F %T') =====" >> "$LOG"

CKPTS=()
if [ "$rc" -eq 0 ]; then
    for f in "$OUT"/vision_step10000.pt "$OUT"/vision_step20000.pt "$OUT"/vision_step30000.pt; do
        [ -f "$f" ] && CKPTS+=("$f") || echo "[skip missing] $f" >> "$LOG"
    done
    FINAL="$OUT/vision.pt"; [ -f "$FINAL" ] || FINAL="$OUT/vision_fused.pt"
    [ -f "$FINAL" ] && CKPTS+=("$FINAL") || echo "[skip missing] $OUT/vision.pt|vision_fused.pt" >> "$LOG"
    echo "===== R11-L training done; IN-1k eval on ${#CKPTS[@]} ckpts =====" >> "$LOG"
    if [ "${#CKPTS[@]}" -gt 0 ]; then
        "$PY" r8_eval_in1k.py --ckpts "${CKPTS[@]}" >> "$LOG" 2>&1
    fi
else
    echo "===== R11-L coca FAILED with exit $rc; skipping eval. =====" >> "$LOG"
fi
echo "===== R11-L arm4 CoCa ALL DONE $(date '+%F %T') =====" >> "$LOG"