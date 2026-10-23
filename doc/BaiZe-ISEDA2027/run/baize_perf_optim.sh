#!/bin/bash
# BaiZe-2B 训练吞吐优化实验（2026-10-23 运维令：目标 > 249K tok/s）
# 基线 = TP1·DP8·MBS2·seq4096·bf16 = 249K tok/s（P-9.7 确认）
# 每个实验 80 步（discard first 30, take last 50 as steady-state）
# 只在 .29 8×H100 上跑
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
OUT="$BASE/data/p5b_l3"
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230

BLEND="1 ${OUT}/p5b_l3_train_s0 1 ${OUT}/p5b_l3_train_s1 1 ${OUT}/p5b_l3_train_s2 1 ${OUT}/p5b_l3_train_s3 1 ${OUT}/p5b_l3_train_s4 1 ${OUT}/p5b_l3_train_s5 1 ${OUT}/p5b_l3_train_s6 1 ${OUT}/p5b_l3_train_s7 1 ${OUT}/p5b_l3_train_s8 1 ${OUT}/p5b_l3_train_s9 1 ${OUT}/p5b_l3_train_s10 1 ${OUT}/p5b_l3_train_s11 1 ${OUT}/p5b_l3_train_s12 1 ${OUT}/p5b_l3_train_s13 1 ${OUT}/p5b_l3_train_s14 1 ${OUT}/p5b_l3_train_s15"

ITERS=80
SEQ=4096
GBS=1024
RESULTS_DIR="/tmp/baize_perf_results"
mkdir -p "$RESULTS_DIR"
SUM="$RESULTS_DIR/summary.txt"
: > "$SUM"

echo "===== BaiZe-2B Throughput Optimization START @ $(date '+%F %T') =====" >> "$SUM"
echo "  baseline = 249K tok/s @ TP1 DP8 MBS2 seq4096 bf16 (P-9.7)" >> "$SUM"
echo "  each experiment: ${ITERS} steps, discard first 30, take last 50 as steady" >> "$SUM"
echo "" >> "$SUM"

echo "--- pre-flight contention check ---" >> "$SUM"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv 2>&1 >> "$SUM"
nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv 2>&1 >> "$SUM"
pgrep -af 'torchrun|pretrain_launcher' 2>&1 | grep -v "baize_perf\|$$\|grep" | cut -c1-120 >> "$SUM"
echo "" >> "$SUM"
run_experiment() {
    local LABEL="$1"; shift
    local EXTRA_ARGS="$@"
    local NAME="perf_${LABEL}"
    local LOG="$RESULTS_DIR/${NAME}.log"
    local PEAK_FILE="$RESULTS_DIR/${NAME}.peakmem"
    local RESULT_FILE="$RESULTS_DIR/${NAME}.result"
    : > "$PEAK_FILE"
    echo "" >> "$SUM"
    echo "===== EXP ${LABEL} START @ $(date '+%F %T') =====" >> "$SUM"
    echo "  extra_args: ${EXTRA_ARGS}" >> "$SUM"
    ( MAX=0; while :; do
        USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1)
        [ -n "$USED" ] && [ "$USED" -gt "$MAX" ] && MAX=$USED; echo "$MAX" > "$PEAK_FILE"; sleep 2
      done ) &
    local SP=$!
    cd "$BASE" || exit 1
    "$PY/torchrun" --nnodes=1 --nproc_per_node=8 \
        --master_addr=127.0.0.1 --master_port=29960 \
        pretrain_launcher.py \
        --arch mamba2 --name "$NAME" --dir "$BASE/nemo_experiments" \
        --tokenizer-path "$BASE/data/tokenizer_eod" \
        --train-data-path $BLEND \
        --train-iters "$ITERS" --global-batch-size "$GBS" --micro-batch-size 2 --seq-length "$SEQ" \
        --tensor-parallel 1 \
        --eval-interval 99999 --eval-iters 0 --save-interval 0 \
        --lr 1e-3 --min-lr 1e-5 --lr-warmup-iters 5 --lr-decay-iters 5 --lr-decay-style WSD \
        --seed 1234 --precision bf16_mixed \
        $EXTRA_ARGS > "$LOG" 2>&1
    local RC=$?
    kill "$SP" 2>/dev/null; wait "$SP" 2>/dev/null
    local PEAK=$(cat "$PEAK_FILE" 2>/dev/null)
    echo "  rc=${RC} peak_gpu_mem_MiB=${PEAK}" >> "$SUM"
    if [ "$RC" -ne 0 ]; then
        echo "  ERROR/OOM last 10 lines:" >> "$SUM"; tail -10 "$LOG" >> "$SUM"
        echo "FAIL|${LABEL}|${RC}|${PEAK}|0|0|0|0|0|0|0" >> "$RESULT_FILE"
        echo "===== EXP ${LABEL} END @ $(date '+%F %T') rc=${RC} =====" >> "$SUM"; return
    fi
    local ITER_LINES
    ITER_LINES=$(grep -E '^\s*\[.*iteration\s+' "$LOG" | awk '{for(i=1;i<=NF;i++) if($i ~ /^iteration$/) {step=$(i+1); gsub(/\//,"",step); if(step+0 >= 30) print $0}}')
    local MS_LIST; MS_LIST=$(echo "$ITER_LINES" | grep -oP 'elapsed time per iteration \(ms\): \K[0-9.]+')
    local MS_COUNT=$(echo "$MS_LIST" | grep -c .)
    local TFLOP_LIST; TFLOP_LIST=$(echo "$ITER_LINES" | grep -oP 'GPU utilization: \K[0-9.]+(?= TFLOP/s/GPU)')
    local LOSS_LIST; LOSS_LIST=$(echo "$ITER_LINES" | grep -oP 'lm loss: \K[0-9.]+')
    local GNORM_LIST; GNORM_LIST=$(echo "$ITER_LINES" | grep -oP 'grad norm: \K[0-9.]+')
    local TOK_PER_STEP=$(( GBS * SEQ ))
    if [ "$MS_COUNT" -gt 0 ]; then
        local AVG_MS MEDIAN_MS AVG_TPS MEDIAN_TPS AVG_TFLOP AVG_LOSS AVG_GNORM NAN_COUNT
        AVG_MS=$(echo "$MS_LIST" | awk '{s+=$1;n++} END{printf "%.1f",s/n}')
        MEDIAN_MS=$(echo "$MS_LIST" | sort -n | awk '{a[NR]=$1} END{if(NR%2) print a[(NR+1)/2]; else printf "%.1f",(a[NR/2]+a[NR/2+1])/2}')
        AVG_TPS=$(awk -v t="$TOK_PER_STEP" -v m="$AVG_MS" 'BEGIN{printf "%.0f",t/(m/1000)}')
        MEDIAN_TPS=$(awk -v t="$TOK_PER_STEP" -v m="$MEDIAN_MS" 'BEGIN{printf "%.0f",t/(m/1000)}')
        AVG_TFLOP=$(echo "$TFLOP_LIST" | awk '{s+=$1;n++} END{printf "%.1f",s/n}')
        AVG_LOSS=$(echo "$LOSS_LIST" | awk '{s+=$1;n++} END{printf "%.4f",s/n}')
        AVG_GNORM=$(echo "$GNORM_LIST" | awk '{s+=$1;n++} END{printf "%.4f",s/n}')
        NAN_COUNT=$(grep -cE 'NaN|inf' "$LOG" 2>/dev/null || echo 0)
        echo "  data_points=${MS_COUNT} avg_ms=${AVG_MS} median_ms=${MEDIAN_MS}" >> "$SUM"
        echo "  avg_toks=${AVG_TPS} median_toks=${MEDIAN_TPS} avg_tflop=${AVG_TFLOP}" >> "$SUM"
        echo "  avg_loss=${AVG_LOSS} avg_gnorm=${AVG_GNORM} nan_count=${NAN_COUNT}" >> "$SUM"
        echo "  peak_VRAM=${PEAK} MiB" >> "$SUM"
        echo "OK|${LABEL}|0|${PEAK}|${AVG_MS}|${MEDIAN_MS}|${MEDIAN_TPS}|${AVG_TFLOP}|${AVG_LOSS}|${AVG_GNORM}|${NAN_COUNT}" >> "$RESULT_FILE"
    else
# ═══════════════════════════════════════════════════════════════
# EXPERIMENTS (each changes 1 variable from baseline)
# ═══════════════════════════════════════════════════════════════

# Exp 0: Baseline (reproduce 249K)
run_experiment "e00_baseline"

# Exp 1: + CUDA graphs
run_experiment "e01_cuda_graph" --enable-cuda-graph

# Exp 2: + FP8 tensorwise (current scaling)
run_experiment "e02_fp8_tensorwise" --fp8-recipe tensorwise

# Exp 3: + FP8 blockwise + first_last_layers_bf16
run_experiment "e03_fp8_blockwise" --fp8-recipe blockwise --first-last-layers-bf16

# Exp 4: + FP8 delayed
run_experiment "e04_fp8_delayed" --fp8-recipe delayed

# Exp 5: + overlap_param_gather_with_optimizer_step
run_experiment "e05_overlap_optim" --overlap-param-gather-with-optimizer-step

# Exp 6: + cross_entropy_loss_fusion
run_experiment "e06_ce_fusion" --cross-entropy-loss-fusion

# Exp 7: + FP8 tensorwise + overlap
run_experiment "e07_fp8_tw_overlap" --fp8-recipe tensorwise --overlap-param-gather-with-optimizer-step

# Exp 8: + FP8 blockwise + cuda_graph
run_experiment "e08_fp8_bw_cg" --fp8-recipe blockwise --first-last-layers-bf16 --enable-cuda-graph

# Exp 9: + FP8 tensorwise + cuda_graph
run_experiment "e09_fp8_tw_cg" --fp8-recipe tensorwise --enable-cuda-graph

# ── final summary table ──
echo "" >> "$SUM"
echo "===== FINAL SUMMARY TABLE =====" >> "$SUM"
echo "label|status|rc|peak_MiB|avg_ms|median_ms|median_toks|avg_tflop|avg_loss|avg_gnorm|nan_count" >> "$SUM"
for f in "$RESULTS_DIR"/perf_*.result; do
    [ -f "$f" ] && cat "$f" >> "$SUM"
done
echo "" >> "$SUM"
echo "===== ALL EXPERIMENTS DONE @ $(date '+%F %T') =====" >> "$SUM"
echo "SUM=$SUM"
echo "RESULTS_DIR=$RESULTS_DIR"
        echo "  Could not parse ms/iter" >> "$SUM"
        echo "PARSE_FAIL|${LABEL}|0|${PEAK}|0|0|0|0|0|0|0" >> "$RESULT_FILE"
    fi
    grep -E '^\s*\[.*iteration\s+' "$LOG" | head -3 >> "$SUM"
    echo "===== EXP ${LABEL} END @ $(date '+%F %T') rc=${RC} =====" >> "$SUM"
}