#!/bin/bash
# ============================================================================
# Scaling Comparison Experiment (2026-10-08⑤ → ⑥ revision)
#   E1: OpenVision2 w512/d30, patch16, 224, 126.78M  (existing self-research)
#   E2: OpenVision2 w768/d30, patch16, 224, 284.54M  (SAME family, only width 512→768)
#       (⑥ revision 2026-10-08: old E2 = official OV2 w1024/d24/p14/336/304M ABANDONED
#        — it changed 4 variables at once; now only "width" differs = standard scaling axis)
#   Same: AIMv2 dense objective, same data (94.9M), 1 epoch, bs512/8GPU, seed 1234
#
# Usage:
#   bash run_scaling_experiment.sh smoke      # 30-step throughput test for both arms
#   bash run_scaling_experiment.sh e1 [steps]  # train E1 only (default = 1 epoch)
#   bash run_scaling_experiment.sh e2 [steps]  # train E2 only
#   bash run_scaling_experiment.sh both [steps] # train E1 then E2 sequentially
# ============================================================================
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export MASTER_ADDR=127.0.0.1
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python

GPIC='/nas_inference/app.e0031982/datasets/stanford-vision-lab/gpic/train/*.tar'
CC12M='/nas_train/app.e0031982/datasets/conceptual-captions-12m-webdataset/data/*.tar'
AMSH='/nas_user/app.e0031982/datasets/Amshaker/Mobile-O-Pre-Train/*.tar'
DATA="${GPIC},${CC12M},${AMSH}"
EVAL='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out

GPIC_N=$(ls $GPIC 2>/dev/null | wc -l)
CC12M_N=$(ls $CC12M 2>/dev/null | wc -l)
AMSH_N=$(ls $AMSH 2>/dev/null | wc -l)
GPIC_PAIRS=$((GPIC_N * 12639))
CC12M_PAIRS=$((CC12M_N * 10000))
AMSH_PAIRS=$((AMSH_N * 2646))
TOTAL_PAIRS=$((GPIC_PAIRS + CC12M_PAIRS + AMSH_PAIRS))
EPOCH_STEPS=$(( (TOTAL_PAIRS + 511) / 512 ))

echo "===== Scaling: GPIC=$GPIC_N CC12M=$CC12M_N Amshaker=$AMSH_N pairs≈$TOTAL_PAIRS 1ep≈${EPOCH_STEPS}steps ====="

MODE="${1:-smoke}"
STEPS="${2:-$EPOCH_STEPS}"
NW="${3:-6}"

run_e1() {
    local _steps="$1" _nw="$2"
    local OUT="$OUTROOT/scaling_E1_ov2_w512_d30_p16_224"
    local LOG=/tmp/scaling_e1.log
    echo "===== E1 START steps=$_steps $(date '+%F %T') =====" | tee "$LOG"
    nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1
    "$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
        --master_addr=$MASTER_ADDR --master_port=$((29800 + RANDOM % 1000)) \
        r9_train.py --tower openvision2 --width 512 --depth 30 \
        --steps "$_steps" --resolution 224 --patch 16 \
        --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234 \
        --loss aimv2 --mask-ratio 0.6 --patch-loss-weight 1.0 --contrast-weight 1.0 \
        --data "$DATA" --data-source mixed --caption-type all --output-dir "$OUT" \
        --log-every 10 --probe-every 300 --probe-n 128 --num-workers "$_nw" \
        --save-every 10000 --eval-data "$EVAL" >> "$LOG" 2>&1
    echo "===== E1 done (exit $?) $(date '+%F %T') =====" >> "$LOG"
}

run_e2() {
    local _steps="$1" _nw="$2"
    # ⑥ revision 2026-10-08: E2 = same-family OV2 w768/d30 (284.54M), NOT official w1024/d24/336/304M
    # Only "width" differs from E1 (512→768), heads/mlp_dim scale with width — standard scaling axis
    local OUT="$OUTROOT/scaling_E2_ov2_w768_d30_p16_224"
    local LOG=/tmp/scaling_e2.log
    echo "===== E2 START (w768/d30, 284.54M) steps=$_steps $(date '+%F %T') =====" | tee "$LOG"
    nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1
    "$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
        --master_addr=$MASTER_ADDR --master_port=$((29900 + RANDOM % 1000)) \
        r9_train.py --tower openvision2 --width 768 --depth 30 \
        --steps "$_steps" --resolution 224 --patch 16 \
        --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234 \
        --loss aimv2 --mask-ratio 0.6 --patch-loss-weight 1.0 --contrast-weight 1.0 \
        --data "$DATA" --data-source mixed --caption-type all --output-dir "$OUT" \
        --log-every 10 --probe-every 300 --probe-n 128 --num-workers "$_nw" \
        --save-every 10000 --eval-data "$EVAL" >> "$LOG" 2>&1
    echo "===== E2 done (exit $?) $(date '+%F %T') =====" >> "$LOG"
}

run_eval() {
    local arm="$1" out_dir="$2"
    local LOG=/tmp/scaling_${arm}_eval.log
    echo "===== ${arm} eval START $(date '+%F %T') =====" | tee "$LOG"
    CKPTS=()
    while IFS= read -r f; do CKPTS+=("$f"); done < <(printf '%s\n' "$out_dir"/vision_step*.pt 2>/dev/null | sort -V)
    FINAL="$out_dir/vision.pt"; [ -f "$FINAL" ] || FINAL="$out_dir/vision_fused.pt"
    [ -f "$FINAL" ] && CKPTS+=("$FINAL")
    if [ "${#CKPTS[@]}" -eq 0 ]; then echo "ERROR: zero ckpts" >> "$LOG"; return 1; fi
    "$PY" lp_protocol_bridge.py --ckpts "${CKPTS[@]}" --protocol B --probe-full-train >> "$LOG" 2>&1
    "$PY" lp_protocol_bridge.py --ckpts "${CKPTS[@]}" --protocol A >> "$LOG" 2>&1
    echo "===== ${arm} eval DONE $(date '+%F %T') =====" >> "$LOG"
}

case "$MODE" in
    smoke)
        echo "########## SMOKE E1 (30 steps) ##########"
        run_e1 30 6
        echo "########## SMOKE E2 (30 steps) ##########"
        run_e2 30 6
        echo "===== SMOKE DONE — /tmp/scaling_e1.log /tmp/scaling_e2.log ====="
        grep -E 'image/s|params' /tmp/scaling_e1.log | tail -5
        grep -E 'image/s|params' /tmp/scaling_e2.log | tail -5
        ;;
    smoke_e1)
        echo "########## SMOKE E1 only (30 steps) ##########"
        run_e1 30 6
        grep -E 'image/s|params' /tmp/scaling_e1.log | tail -5
        ;;
    smoke_e2)
        echo "########## SMOKE E2 only (30 steps, w768/d30) ##########"
        run_e2 30 6
        grep -E 'image/s|params' /tmp/scaling_e2.log | tail -5
        ;;
    e1)
        run_e1 "$STEPS" "$NW"; rc=$?
        [ "$STEPS" -gt 1000 ] && [ $rc -eq 0 ] && run_eval e1 "$OUTROOT/scaling_E1_ov2_w512_d30_p16_224"
        ;;
    e2)
        run_e2 "$STEPS" "$NW"; rc=$?
        [ "$STEPS" -gt 1000 ] && [ $rc -eq 0 ] && run_eval e2 "$OUTROOT/scaling_E2_ov2_w768_d30_p16_224"
        ;;
    both)
        run_e1 "$STEPS" "$NW"; rc1=$?
        [ "$STEPS" -gt 1000 ] && [ $rc1 -eq 0 ] && run_eval e1 "$OUTROOT/scaling_E1_ov2_w512_d30_p16_224"
        run_e2 "$STEPS" "$NW"; rc2=$?
        [ "$STEPS" -gt 1000 ] && [ $rc2 -eq 0 ] && run_eval e2 "$OUTROOT/scaling_E2_ov2_w768_d30_p16_224"
        ;;
    *)
        echo "Usage: bash run_scaling_experiment.sh {smoke|smoke_e1|smoke_e2|e1|e2|both} [steps] [nw]"; exit 1
        ;;
esac