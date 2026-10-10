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

# ---- 2026-10-09⑨ fair rerun: frozen data snapshot + new lr recipe ----
# The snapshot file ensures both E1fair and E2fair train on byte-identical tars
# (GPIC download is ongoing; $GPIC_N changes between arm launches).
SNAPSHOT_FILE="$(dirname "$(readlink -f "$BASH_SOURCE[0]")")/data_snapshot_20261009.txt"
# V3 full-data snapshot: 8000 GPIC tars (download completed 2026-10-10)
SNAPSHOT_FULL="$(dirname "$(readlink -f "$BASH_SOURCE[0]")")/data_snapshot_20261010_full.txt"

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
    local _resume="${3:-}"
    local OUT="$OUTROOT/scaling_E1_ov2_w512_d30_p16_224"
    local LOG=/tmp/scaling_e1.log
    echo "===== E1 START steps=$_steps resume=${_resume:-none} $(date '+%F %T') =====" | tee "$LOG"
    nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1
    local RESUME_ARG=""
    [ -n "$_resume" ] && RESUME_ARG="--resume $_resume"
    "$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
        --master_addr=$MASTER_ADDR --master_port=$((29800 + RANDOM % 1000)) \
        r9_train.py --tower openvision2 --width 512 --depth 30 \
        --steps "$_steps" --resolution 224 --patch 16 \
        --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234 \
        --loss aimv2 --mask-ratio 0.6 --patch-loss-weight 1.0 --contrast-weight 1.0 \
        --data "$DATA" --data-source mixed --caption-type all --output-dir "$OUT" \
        --log-every 10 --probe-every 300 --probe-n 128 --num-workers "$_nw" \
        --save-every 10000 --eval-data "$EVAL" $RESUME_ARG >> "$LOG" 2>&1
    local rc=$?
    echo "===== E1 done (exit $rc) $(date '+%F %T') =====" >> "$LOG"
    return $rc
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
    local rc=$?
    echo "===== E2 done (exit $rc) $(date '+%F %T') =====" >> "$LOG"
    return $rc
}

# ============================================================================
# 2026-10-09⑨ FAIR RERUN: lr=5e-4, warmup=2000, scheduler=cosine, min_lr=5e-5
#   Same frozen data snapshot for both arms (byte-identical tars).
#   New output dirs: scaling_E{1,2}fair_* (old dirs preserved, NOT overwritten).
# ============================================================================

run_e1fair() {
    local _steps="$1" _nw="$2"
    local OUT="$OUTROOT/scaling_E1fair_ov2_w512_d30_p16_224"
    local LOG=/tmp/scaling_e1fair.log
    local FAIR_DATA="${SNAPSHOT_FILE},${CC12M},${AMSH}"
    echo "===== E1fair START (w512/d30, fair recipe) steps=$_steps $(date '+%F %T') =====" | tee "$LOG"
    echo "[fair] snapshot=$SNAPSHOT_FILE  data=$FAIR_DATA" >> "$LOG"
    nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1
    "$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
        --master_addr=$MASTER_ADDR --master_port=$((29800 + RANDOM % 1000)) \
        r9_train.py --tower openvision2 --width 512 --depth 30 \
        --steps "$_steps" --resolution 224 --patch 16 \
        --batch-size 64 --lr 5e-4 --warmup 2000 --scheduler cosine --min-lr 5e-5 --seed 1234 \
        --loss aimv2 --mask-ratio 0.6 --patch-loss-weight 1.0 --contrast-weight 1.0 \
        --data "$FAIR_DATA" --data-source mixed --caption-type all --output-dir "$OUT" \
        --log-every 10 --probe-every 300 --probe-n 128 --num-workers "$_nw" \
        --save-every 10000 --eval-data "$EVAL" >> "$LOG" 2>&1
    local rc=$?
    echo "===== E1fair done (exit $rc) $(date '+%F %T') =====" >> "$LOG"
    return $rc
}

run_e2fair() {
    local _steps="$1" _nw="$2"
    local OUT="$OUTROOT/scaling_E2fair_ov2_w768_d30_p16_224"
    local LOG=/tmp/scaling_e2fair.log
    local FAIR_DATA="${SNAPSHOT_FILE},${CC12M},${AMSH}"
    echo "===== E2fair START (w768/d30, fair recipe) steps=$_steps $(date '+%F %T') =====" | tee "$LOG"
    echo "[fair] snapshot=$SNAPSHOT_FILE  data=$FAIR_DATA" >> "$LOG"
    nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1
    "$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
        --master_addr=$MASTER_ADDR --master_port=$((29900 + RANDOM % 1000)) \
        r9_train.py --tower openvision2 --width 768 --depth 30 \
        --steps "$_steps" --resolution 224 --patch 16 \
        --batch-size 64 --lr 5e-4 --warmup 2000 --scheduler cosine --min-lr 5e-5 --seed 1234 \
        --loss aimv2 --mask-ratio 0.6 --patch-loss-weight 1.0 --contrast-weight 1.0 \
        --data "$FAIR_DATA" --data-source mixed --caption-type all --output-dir "$OUT" \
        --log-every 10 --probe-every 300 --probe-n 128 --num-workers "$_nw" \
        --save-every 10000 --eval-data "$EVAL" >> "$LOG" 2>&1
    local rc=$?
    echo "===== E2fair done (exit $rc) $(date '+%F %T') =====" >> "$LOG"
    return $rc
}

# ============================================================================
# 2026-10-10 THREE-VARIANT EXPERIMENT (vs E1fair baseline)
#   V1: resolution 224→336 (patch 16, 196→441 patches)
#   V2: optimizer AdamW→Muon (Newton-Schulz orthogonalized momentum)
#   V3: full GPIC data (8000 tars vs 7437 in E1fair snapshot)
#   Each variant is byte-identical to E1fair except the single tested variable.
#   Baseline: E1fair ProtB=62.34±0.01%, ProtA=49.70%.
# ============================================================================

run_v1_res336() {
    local _steps="$1" _nw="$2"
    local OUT="$OUTROOT/scaling_V1_res336_ov2_w512_d30_p16_336"
    local LOG=/tmp/scaling_v1_res336.log
    local FAIR_DATA="${SNAPSHOT_FILE},${CC12M},${AMSH}"
    echo "===== V1 START (w512/d30, res=336/p16, fair recipe) steps=$_steps $(date '+%F %T') =====" | tee "$LOG"
    echo "[V1] resolution 224→336, patch 16 (196→441 patches), from scratch" >> "$LOG"
    echo "[V1] snapshot=$SNAPSHOT_FILE  data=$FAIR_DATA" >> "$LOG"
    nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1
    "$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
        --master_addr=$MASTER_ADDR --master_port=$((29800 + RANDOM % 1000)) \
        r9_train.py --tower openvision2 --width 512 --depth 30 \
        --steps "$_steps" --resolution 336 --patch 16 \
        --batch-size 64 --lr 5e-4 --warmup 2000 --scheduler cosine --min-lr 5e-5 --seed 1234 \
        --loss aimv2 --mask-ratio 0.6 --patch-loss-weight 1.0 --contrast-weight 1.0 \
        --data "$FAIR_DATA" --data-source mixed --caption-type all --output-dir "$OUT" \
        --log-every 10 --probe-every 300 --probe-n 128 --num-workers "$_nw" \
        --save-every 10000 --eval-data "$EVAL" >> "$LOG" 2>&1
    local rc=$?
    echo "===== V1 done (exit $rc) $(date '+%F %T') =====" >> "$LOG"
    return $rc
}

run_v2_muon() {
    local _steps="$1" _nw="$2"
    local _lr="${3:-5e-4}"
    local OUT="$OUTROOT/scaling_V2_muon_ov2_w512_d30_p16_224"
    local LOG=/tmp/scaling_v2_muon.log
    local FAIR_DATA="${SNAPSHOT_FILE},${CC12M},${AMSH}"
    echo "===== V2 START (w512/d30, optimizer=Muon, lr=$_lr, fair recipe) steps=$_steps $(date '+%F %T') =====" | tee "$LOG"
    echo "[V2] optimizer AdamW→Muon (momentum=0.95, nesterov, ns_steps=5)" >> "$LOG"
    echo "[V2] 2D weights→Muon, 1D params→AdamW (pretrain dist_muon convention)" >> "$LOG"
    echo "[V2] snapshot=$SNAPSHOT_FILE  data=$FAIR_DATA  lr=$_lr" >> "$LOG"
    nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1
    "$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
        --master_addr=$MASTER_ADDR --master_port=$((29800 + RANDOM % 1000)) \
        r9_train.py --tower openvision2 --width 512 --depth 30 \
        --steps "$_steps" --resolution 224 --patch 16 \
        --batch-size 64 --lr "$_lr" --warmup 2000 --scheduler cosine --min-lr 5e-5 --seed 1234 \
        --optimizer muon \
        --loss aimv2 --mask-ratio 0.6 --patch-loss-weight 1.0 --contrast-weight 1.0 \
        --data "$FAIR_DATA" --data-source mixed --caption-type all --output-dir "$OUT" \
        --log-every 10 --probe-every 300 --probe-n 128 --num-workers "$_nw" \
        --save-every 10000 --eval-data "$EVAL" >> "$LOG" 2>&1
    local rc=$?
    echo "===== V2 done (exit $rc) $(date '+%F %T') =====" >> "$LOG"
    return $rc
}

run_v3_fulldata() {
    local _steps="$1" _nw="$2"
    local OUT="$OUTROOT/scaling_V3_fulldata_ov2_w512_d30_p16_224"
    local LOG=/tmp/scaling_v3_fulldata.log
    local FULL_DATA="${SNAPSHOT_FULL},${CC12M},${AMSH}"
    echo "===== V3 START (w512/d30, full GPIC data, fair recipe) steps=$_steps $(date '+%F %T') =====" | tee "$LOG"
    echo "[V3] full GPIC data: 8000 tars (vs E1fair snapshot 7437 tars)" >> "$LOG"
    echo "[V3] snapshot=$SNAPSHOT_FULL  data=$FULL_DATA" >> "$LOG"
    nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1
    "$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
        --master_addr=$MASTER_ADDR --master_port=$((29800 + RANDOM % 1000)) \
        r9_train.py --tower openvision2 --width 512 --depth 30 \
        --steps "$_steps" --resolution 224 --patch 16 \
        --batch-size 64 --lr 5e-4 --warmup 2000 --scheduler cosine --min-lr 5e-5 --seed 1234 \
        --loss aimv2 --mask-ratio 0.6 --patch-loss-weight 1.0 --contrast-weight 1.0 \
        --data "$FULL_DATA" --data-source mixed --caption-type all --output-dir "$OUT" \
        --log-every 10 --probe-every 300 --probe-n 128 --num-workers "$_nw" \
        --save-every 10000 --eval-data "$EVAL" >> "$LOG" 2>&1
    local rc=$?
    echo "===== V3 done (exit $rc) $(date '+%F %T') =====" >> "$LOG"
    return $rc
}

run_eval() {
    local arm="$1" out_dir="$2"
    local final_only="${3:-}"
    local LOG=/tmp/scaling_${arm}_eval.log
    echo "===== ${arm} eval START $(date '+%F %T') =====" | tee "$LOG"
    local CKPTS=()
    if [ "$final_only" = "final" ]; then
        # Only evaluate the final checkpoint (vision.pt or vision_fused.pt)
        local FINAL="$out_dir/vision.pt"; [ -f "$FINAL" ] || FINAL="$out_dir/vision_fused.pt"
        if [ -f "$FINAL" ]; then
            CKPTS+=("$FINAL")
        else
            # Fallback: use the highest step checkpoint
            local LAST_STEP=$(ls "$out_dir"/vision_step*.pt 2>/dev/null | sort -V | tail -1)
            [ -n "$LAST_STEP" ] && CKPTS+=("$LAST_STEP")
        fi
    else
        while IFS= read -r f; do CKPTS+=("$f"); done < <(printf '%s\n' "$out_dir"/vision_step*.pt 2>/dev/null | sort -V)
        local FINAL="$out_dir/vision.pt"; [ -f "$FINAL" ] || FINAL="$out_dir/vision_fused.pt"
        [ -f "$FINAL" ] && CKPTS+=("$FINAL")
    fi
    if [ "${#CKPTS[@]}" -eq 0 ]; then echo "ERROR: zero ckpts" >> "$LOG"; return 1; fi
    echo "[eval] ckpts: ${#CKPTS[@]} files" >> "$LOG"
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
    resume_e1)
        # Resume E1 from a checkpoint: bash run_scaling_experiment.sh resume_e1 <steps> <nw> <ckpt_path>
        RESUME_CKPT="${4:-$OUTROOT/scaling_E1_ov2_w512_d30_p16_224/vision_step130000.pt}"
        run_e1 "$STEPS" "$NW" "$RESUME_CKPT"; rc=$?
        [ "$STEPS" -gt 1000 ] && [ $rc -eq 0 ] && run_eval e1 "$OUTROOT/scaling_E1_ov2_w512_d30_p16_224" final
        ;;
    e2)
        run_e2 "$STEPS" "$NW"; rc=$?
        [ "$STEPS" -gt 1000 ] && [ $rc -eq 0 ] && run_eval e2 "$OUTROOT/scaling_E2_ov2_w768_d30_p16_224" final
        ;;
    both)
        run_e1 "$STEPS" "$NW"; rc1=$?
        [ "$STEPS" -gt 1000 ] && [ $rc1 -eq 0 ] && run_eval e1 "$OUTROOT/scaling_E1_ov2_w512_d30_p16_224" final
        run_e2 "$STEPS" "$NW"; rc2=$?
        [ "$STEPS" -gt 1000 ] && [ $rc2 -eq 0 ] && run_eval e2 "$OUTROOT/scaling_E2_ov2_w768_d30_p16_224" final
        ;;
    eval_final)
        # Evaluate only the final ckpts of both arms
        run_eval e1 "$OUTROOT/scaling_E1_ov2_w512_d30_p16_224" final
        run_eval e2 "$OUTROOT/scaling_E2_ov2_w768_d30_p16_224" final
        ;;
    # ---- 2026-10-09⑨ fair rerun modes ----
    snapshot_gpic)
        # Freeze GPIC tar list to a .txt snapshot (one absolute path per line).
        # Both fair arms use this snapshot so their data is byte-identical.
        echo "===== Freezing GPIC tar snapshot → $SNAPSHOT_FILE ====="
        ls -1 $GPIC 2>/dev/null | sort > "$SNAPSHOT_FILE"
        _snap_n=$(wc -l < "$SNAPSHOT_FILE")
        echo "Snapshot: $_snap_n GPIC tars written to $SNAPSHOT_FILE"
        echo "CC12M tars: $(ls $CC12M 2>/dev/null | wc -l)  Amshaker tars: $(ls $AMSH 2>/dev/null | wc -l)"
        ;;
    smoke_cos)
        # Fair smoke: 30 steps for both arms with cosine recipe.
        # Verifies lr 4-point self-check + compares total_shards between arms.
        echo "########## SMOKE E1fair (30 steps, cosine) ##########"
        if [ ! -f "$SNAPSHOT_FILE" ]; then
            echo "WARNING: snapshot file not found at $SNAPSHOT_FILE — creating now"
            ls -1 $GPIC 2>/dev/null | sort > "$SNAPSHOT_FILE"
        fi
        echo "Snapshot: $(wc -l < "$SNAPSHOT_FILE") GPIC tars"
        run_e1fair 30 6
        echo "########## SMOKE E2fair (30 steps, cosine) ##########"
        run_e2fair 30 6
        echo "===== SMOKE_COS DONE — /tmp/scaling_e1fair.log /tmp/scaling_e2fair.log ====="
        echo ""
        echo "--- lr self-check (E1fair) ---"
        grep -E 'lr-selfcheck' /tmp/scaling_e1fair.log || echo "(no lr-selfcheck found!)"
        echo "--- lr self-check (E2fair) ---"
        grep -E 'lr-selfcheck' /tmp/scaling_e2fair.log || echo "(no lr-selfcheck found!)"
        echo ""
        echo "--- total_shards comparison ---"
        _ts1=$(grep -oP 'total_shards=\K[0-9]+' /tmp/scaling_e1fair.log | head -1)
        _ts2=$(grep -oP 'total_shards=\K[0-9]+' /tmp/scaling_e2fair.log | head -1)
        echo "E1fair total_shards=$_ts1  E2fair total_shards=$_ts2"
        if [ -n "$_ts1" ] && [ -n "$_ts2" ] && [ "$_ts1" = "$_ts2" ]; then
            echo "✅ SHARD PARITY OK: both arms have $_ts1 shards"
        else
            echo "🚫 SHARD MISMATCH! E1fair=$_ts1 vs E2fair=$_ts2 — DO NOT proceed to full run"
        fi
        echo ""
        grep -E 'image/s|params' /tmp/scaling_e1fair.log | tail -5
        grep -E 'image/s|params' /tmp/scaling_e2fair.log | tail -5
        ;;
    e1fair)
        if [ ! -f "$SNAPSHOT_FILE" ]; then
            echo "ERROR: snapshot file $SNAPSHOT_FILE not found. Run 'snapshot_gpic' first." >&2
            exit 1
        fi
        run_e1fair "$STEPS" "$NW"; rc=$?
        [ "$STEPS" -gt 1000 ] && [ $rc -eq 0 ] && run_eval e1fair "$OUTROOT/scaling_E1fair_ov2_w512_d30_p16_224" final
        ;;
    e2fair)
        if [ ! -f "$SNAPSHOT_FILE" ]; then
            echo "ERROR: snapshot file $SNAPSHOT_FILE not found. Run 'snapshot_gpic' first." >&2
            exit 1
        fi
        run_e2fair "$STEPS" "$NW"; rc=$?
        [ "$STEPS" -gt 1000 ] && [ $rc -eq 0 ] && run_eval e2fair "$OUTROOT/scaling_E2fair_ov2_w768_d30_p16_224" final
        ;;
    bothfair)
        # Chain: E1fair → eval → E2fair → eval (sequential, same GPU)
        if [ ! -f "$SNAPSHOT_FILE" ]; then
            echo "ERROR: snapshot file $SNAPSHOT_FILE not found. Run 'snapshot_gpic' first." >&2
            exit 1
        fi
        echo "===== BOTHAIR: E1fair → E2fair (chained) ====="
        run_e1fair "$STEPS" "$NW"; rc1=$?
        [ "$STEPS" -gt 1000 ] && [ $rc1 -eq 0 ] && run_eval e1fair "$OUTROOT/scaling_E1fair_ov2_w512_d30_p16_224" final
        run_e2fair "$STEPS" "$NW"; rc2=$?
        [ "$STEPS" -gt 1000 ] && [ $rc2 -eq 0 ] && run_eval e2fair "$OUTROOT/scaling_E2fair_ov2_w768_d30_p16_224" final
        echo "===== BOTHAIR done: E1fair rc=$rc1, E2fair rc=$rc2 ====="
        ;;
    smoke_v1)
        # V1 smoke test: 30 steps, resolution 336
        echo "--- V1 smoke (30 steps, res=336) ---"
        run_v1_res336 30 "$NW"
        echo "--- V1 smoke done ---"
        tail -30 /tmp/scaling_v1_res336.log
        grep -E '\[start\]|\[optimizer\]|image/s|tokens/s|loss=' /tmp/scaling_v1_res336.log | tail -15
        ;;
    smoke_v2)
        # V2 smoke test: 30 steps, Muon optimizer, lr=5e-4
        echo "--- V2 smoke (30 steps, optimizer=Muon, lr=5e-4) ---"
        run_v2_muon 30 "$NW" "5e-4"
        echo "--- V2 smoke done ---"
        tail -30 /tmp/scaling_v2_muon.log
        grep -E '\[start\]|\[optimizer\]|image/s|tokens/s|loss=' /tmp/scaling_v2_muon.log | tail -15
        ;;
    smoke_v3)
        # V3 smoke test: 30 steps, full GPIC data
        if [ ! -f "$SNAPSHOT_FULL" ]; then
            echo "ERROR: full snapshot $SNAPSHOT_FULL not found." >&2
            exit 1
        fi
        echo "--- V3 smoke (30 steps, full GPIC data) ---"
        run_v3_fulldata 30 "$NW"
        echo "--- V3 smoke done ---"
        tail -30 /tmp/scaling_v3_fulldata.log
        grep -E '\[start\]|\[optimizer\]|image/s|tokens/s|loss=' /tmp/scaling_v3_fulldata.log | tail -15
        ;;
    v1)
        # V1 full run: resolution 336 (patch 16 → 441 patches), ~2.25× compute, ~20h
        if [ ! -f "$SNAPSHOT_FILE" ]; then
            echo "ERROR: snapshot file $SNAPSHOT_FILE not found. Run 'snapshot_gpic' first." >&2
            exit 1
        fi
        run_v1_res336 "$STEPS" "$NW"; rc=$?
        [ "$STEPS" -gt 1000 ] && [ $rc -eq 0 ] && run_eval v1 "$OUTROOT/scaling_V1_res336_ov2_w512_d30_p16_336" final
        ;;
    v2)
        # V2 full run: Muon optimizer, lr=5e-4 (after probe confirmation)
        if [ ! -f "$SNAPSHOT_FILE" ]; then
            echo "ERROR: snapshot file $SNAPSHOT_FILE not found. Run 'snapshot_gpic' first." >&2
            exit 1
        fi
        run_v2_muon "$STEPS" "$NW" "${3:-5e-4}"; rc=$?
        [ "$STEPS" -gt 1000 ] && [ $rc -eq 0 ] && run_eval v2 "$OUTROOT/scaling_V2_muon_ov2_w512_d30_p16_224" final
        ;;
    v3)
        # V3 full run: full GPIC data (8000 tars)
        if [ ! -f "$SNAPSHOT_FULL" ]; then
            echo "ERROR: full snapshot $SNAPSHOT_FULL not found." >&2
            exit 1
        fi
        run_v3_fulldata "$STEPS" "$NW"; rc=$?
        [ "$STEPS" -gt 1000 ] && [ $rc -eq 0 ] && run_eval v3 "$OUTROOT/scaling_V3_fulldata_ov2_w512_d30_p16_224" final
        ;;
    allvariants)
        # Serial chain: V3 → V1 → V2 (each ~9-20h on 8×H100)
        if [ ! -f "$SNAPSHOT_FILE" ]; then
            echo "ERROR: snapshot file $SNAPSHOT_FILE not found." >&2
            exit 1
        fi
        if [ ! -f "$SNAPSHOT_FULL" ]; then
            echo "ERROR: full snapshot $SNAPSHOT_FULL not found." >&2
            exit 1
        fi
        echo "===== ALLVARIANTS: V3 → V1 → V2 (serial) ====="
        echo "----- V3 (full GPIC data) -----"
        run_v3_fulldata "$STEPS" "$NW"; rc3=$?
        [ "$STEPS" -gt 1000 ] && [ $rc3 -eq 0 ] && run_eval v3 "$OUTROOT/scaling_V3_fulldata_ov2_w512_d30_p16_224" final
        echo "----- V1 (resolution 336) -----"
        run_v1_res336 "$STEPS" "$NW"; rc1=$?
        [ "$STEPS" -gt 1000 ] && [ $rc1 -eq 0 ] && run_eval v1 "$OUTROOT/scaling_V1_res336_ov2_w512_d30_p16_336" final
        echo "----- V2 (Muon optimizer) -----"
        run_v2_muon "$STEPS" "$NW" "5e-4"; rc2=$?
        [ "$STEPS" -gt 1000 ] && [ $rc2 -eq 0 ] && run_eval v2 "$OUTROOT/scaling_V2_muon_ov2_w512_d30_p16_224" final
        echo "===== ALLVARIANTS done: V3 rc=$rc3, V1 rc=$rc1, V2 rc=$rc2 ====="
        ;;
    *)
        echo "Usage: bash run_scaling_experiment.sh {smoke|smoke_e1|smoke_e2|e1|resume_e1|e2|both|eval_final|snapshot_gpic|smoke_cos|e1fair|e2fair|bothfair|smoke_v1|smoke_v2|smoke_v3|v1|v2|v3|allvariants} [steps] [nw] [ckpt_path]"
        exit 1
        ;;
esac