#!/bin/bash
# =============================================================================
# AIMv2 official AR paradigm — Arm B (VISION_AIMV2_OFFICIAL_PLAN.md, queue ④)
#   Official AIMv2: pure AR (causal ViT + next-patch pixel + text AR), NO InfoNCE.
#   Controlled A/B vs Arm A (our non-AR: bidirectional + InfoNCE + masked-patch-MSE).
#
#   Arm A baseline = R11-G arm⑥-A (lp@30k=12.08%, already exists, NOT re-run).
#
#   Recipe (Arm B):
#   - Tower: OpenVision2 w512 (126.78M), depth30 / patch16 / 224^2.
#   - Causal forward: OpenVision2.forward(causal=True) — lower-triangular mask.
#   - PatchPredictor (~0.66M): next-patch pixel_loss = MSE(pred[:, :-1], target[:, 1:]).
#   - ARTextDecoder (~76.2M, weight-tied): text AR cap_loss = CE(next-token).
#     Cross-attends to CAUSAL vision patches (revision point ②).
#   - Loss: cap_loss + 0.4 * pixel_loss (official AIMv2 alpha≈0.4).
#   - NO InfoNCE, NO frozen CLIP text tower in gradient graph.
#   - Data: CC12M + Amshaker (same as R11-G, for controlled A/B).
#   - Optimizer: AdamW lr 3e-3 warmup 20, seed 1234, bf16, bs64x8=512.
#
#   ⚠️ Handicap (revision point ③): official AIMv2 uses LLaMA-3 long synthetic
#   captions (~12B samples); we use SHORT alt-text (CC12M/Amshaker) → text AR
#   next-token signal is inherently weak. This must be noted in the final report.
#
#   Pre-registered verdict (VISION_AIMV2_OFFICIAL_PLAN.md §5.2):
#     - Arm B lp >= Arm A + 1.5 AND C1-C4 OK → ✅ AR more optimal
#     - Arm B lp <= Arm A - 1.5 → ❌ non-AR + contrastive more optimal
#     - +0.5 < Δlp < +1.5 → 🟡 trend (not significant, need larger scale)
#     - |Δlp| <= 0.5 → ⚪ paradigm equivalent
#     - Arm B C1 > 0.95 → 🔴 AR collapse (no contrastive → collapse)
#     - Δlp large but C1≈0.90 → ⚠️ AR effective but representation degraded
#
#   Cost: 30k steps ≈ 12-20 GPU·h (smoke test first; if wall-clock >3h, reassess)
#
# Usage:
#   bash run_aimv2_ar.sh [steps]
#   Default steps = 30000 (quick A/B); 108000 for medium; 272000 for full
#
# PREREQUISITE: Queue ①②③ must be FINISHED (lp bridge + mask-ratio + weight-ratio
#   ablations). All 8 GPUs must be free.
# =============================================================================
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
OUT="$OUTROOT/R13_aimv2_ar_w512"
LOG=/tmp/r13_aimv2_ar.log

echo "===== AIMv2 AR (Arm B) START steps=$STEPS $(date '+%F %T') =====" > "$LOG"
echo "----- hostname -----" >> "$LOG"
hostname >> "$LOG" 2>&1
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1

CC12M_N=$(ls $CC12M 2>/dev/null | wc -l)
AMSH_N=$(ls $AMSH 2>/dev/null | wc -l)
echo "----- shards: CC12M=$CC12M_N Amshaker=$AMSH_N -----" >> "$LOG"

echo "===== smoke test (30 steps) START $(date '+%F %T') =====" >> "$LOG"
"$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
    --master_addr=$MASTER_ADDR --master_port=$((32000 + RANDOM % 1000)) \
    r9_train.py --tower openvision2 --width 512 --depth 30 \
    --steps 30 --resolution 224 --patch 16 \
    --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234 \
    --loss aimv2_ar --alpha-pixel 0.4 --decoder-depth 4 \
    --c2-collapse-guard 0 \
    --data "$DATA" --data-source wds --output-dir "$OUT" \
    --log-every 10 --probe-every 300 --probe-n 128 --num-workers "$NW" \
    --save-every 0 --eval-data "$EVAL" \
    >> "$LOG" 2>&1
smoke_rc=$?
echo "===== smoke test done (exit $smoke_rc) $(date '+%F %T') =====" >> "$LOG"
if [ "$smoke_rc" -ne 0 ]; then
    echo "  [FATAL] smoke test FAILED — aborting before full run" >> "$LOG"
    cat "$LOG"
    exit 1
fi

# Report smoke test throughput for cost estimation
echo "===== smoke throughput check =====" >> "$LOG"
grep 'image/s=' "$LOG" | tail -3 >> "$LOG"

echo "===== full run ($STEPS steps) START $(date '+%F %T') =====" >> "$LOG"
"$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
    --master_addr=$MASTER_ADDR --master_port=$((32100 + RANDOM % 1000)) \
    r9_train.py --tower openvision2 --width 512 --depth 30 \
    --steps "$STEPS" --resolution 224 --patch 16 \
    --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234 \
    --loss aimv2_ar --alpha-pixel 0.4 --decoder-depth 4 \
    --c2-collapse-guard 0 \
    --data "$DATA" --data-source wds --output-dir "$OUT" \
    --log-every 50 --probe-every 300 --probe-n 128 --num-workers "$NW" \
    --save-every 10000 --eval-data "$EVAL" \
    >> "$LOG" 2>&1
rc=$?
echo "===== full run done (exit $rc) $(date '+%F %T') =====" >> "$LOG"

if [ "$rc" -ne 0 ]; then
    echo "  [WARN] full run FAILED" >> "$LOG"
    cat "$LOG"
    exit 1
fi

# Eval all saved checkpoints
ALL_CKPTS=()
for f in "$OUT"/vision_step10000.pt "$OUT"/vision_step20000.pt "$OUT"/vision_step30000.pt; do
    [ -f "$f" ] && ALL_CKPTS+=("$f") || echo "  [skip missing] $f" >> "$LOG"
done
FINAL="$OUT/vision.pt"; [ -f "$FINAL" ] || FINAL="$OUT/vision_fused.pt"
[ -f "$FINAL" ] && ALL_CKPTS+=("$FINAL")

echo "===== IN-1k eval on ${#ALL_CKPTS[@]} ckpts START $(date '+%F %T') =====" >> "$LOG"
if [ "${#ALL_CKPTS[@]}" -gt 0 ]; then
    "$PY" r8_eval_in1k.py --ckpts "${ALL_CKPTS[@]}" >> "$LOG" 2>&1
fi
echo "===== AIMv2 AR ALL DONE $(date '+%F %T') =====" >> "$LOG"
