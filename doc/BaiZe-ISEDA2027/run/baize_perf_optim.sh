#!/bin/bash
# BaiZe-2B throughput optim (2026-10-23): target > 249K tok/s
# baseline = TP1 DP8 MBS2 seq4096 bf16 = 249K (P-9.7)
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
OUT="$BASE/data/p5b_l3"
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230
BLEND="1 ${OUT}/p5b_l3_train_s0 1 ${OUT}/p5b_l3_train_s1 1 ${OUT}/p5b_l3_train_s2 1 ${OUT}/p5b_l3_train_s3 1 ${OUT}/p5b_l3_train_s4 1 ${OUT}/p5b_l3_train_s5 1 ${OUT}/p5b_l3_train_s6 1 ${OUT}/p5b_l3_train_s7 1 ${OUT}/p5b_l3_train_s8 1 ${OUT}/p5b_l3_train_s9 1 ${OUT}/p5b_l3_train_s10 1 ${OUT}/p5b_l3_train_s11 1 ${OUT}/p5b_l3_train_s12 1 ${OUT}/p5b_l3_train_s13 1 ${OUT}/p5b_l3_train_s14 1 ${OUT}/p5b_l3_train_s15"
ITERS=80; SEQ=4096; GBS=1024
R="/tmp/baize_perf_results"; mkdir -p "$R"; SUM="$R/summary.txt"; : > "$SUM"
echo "START @ $(date '+%F %T')" >> "$SUM"
nvidia-smi --query-gpu=index,memory.used --format=csv,noheader >> "$SUM" 2>&1
echo "" >> "$SUM"

run_exp() {
    local LABEL="$1"; shift
    local EXTRA="$@"
    local NAME="perf_${LABEL}"
    local LOG="$R/${NAME}.log"
    local PF="$R/${NAME}.peakmem"
    local RF="$R/${NAME}.result"
    : > "$PF"
    echo "" >> "$SUM"
    echo "===== EXP ${LABEL} @ $(date '+%F %T') args=[${EXTRA}] =====" >> "$SUM"
    ( MAX=0; while :; do
        U=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1)
        [ -n "$U" ] && [ "$U" -gt "$MAX" ] && MAX=$U; echo "$MAX" > "$PF"; sleep 2
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
        --tensor-parallel 1 --eval-interval 99999 --eval-iters 0 --save-interval 0 \
        --lr 1e-3 --min-lr 1e-5 --lr-warmup-iters 5 --lr-decay-iters 5 --lr-decay-style WSD \
        --seed 1234 --precision bf16_mixed $EXTRA > "$LOG" 2>&1
    local RC=$?
    kill "$SP" 2>/dev/null; wait "$SP" 2>/dev/null
    local PEAK=$(cat "$PF" 2>/dev/null)
    echo "  rc=${RC} peak=${PEAK}" >> "$SUM"
    if [ "$RC" -ne 0 ]; then
        tail -10 "$LOG" >> "$SUM"
        echo "FAIL|${LABEL}|${RC}|${PEAK}|0|0|0|0|0|0|0" >> "$RF"
        echo "===== END ${LABEL} rc=${RC} =====" >> "$SUM"; return
    fi
    local IL MS MC TF LG GN TPS
    IL=$(grep -E '^\s*\[.*iteration\s+' "$LOG" | awk '{for(i=1;i<=NF;i++) if($i ~ /^iteration$/) {s=$(i+1); gsub(/\//,"",s); if(s+0>=30) print}}')
    MS=$(echo "$IL" | grep -oP 'elapsed time per iteration \(ms\): \K[0-9.]+')
    MC=$(echo "$MS" | grep -c .)
    TF=$(echo "$IL" | grep -oP 'GPU utilization: \K[0-9.]+(?= TFLOP/s/GPU)')
    LG=$(echo "$IL" | grep -oP 'lm loss: \K[0-9.]+')
    GN=$(echo "$IL" | grep -oP 'grad norm: \K[0-9.]+')
    TPS=$(( GBS * SEQ ))
    if [ "$MC" -gt 0 ]; then
        local AM MM MT AT AL AG NC
        AM=$(echo "$MS" | awk '{s+=$1;n++} END{printf "%.1f",s/n}')
        MM=$(echo "$MS" | sort -n | awk '{a[NR]=$1} END{if(NR%2) print a[(NR+1)/2]; else printf "%.1f",(a[NR/2]+a[NR/2+1])/2}')
        MT=$(awk -v t="$TPS" -v m="$MM" 'BEGIN{printf "%.0f",t/(m/1000)}')
        AT=$(echo "$TF" | awk '{s+=$1;n++} END{printf "%.1f",s/n}')
        AL=$(echo "$LG" | awk '{s+=$1;n++} END{printf "%.4f",s/n}')
        AG=$(echo "$GN" | awk '{s+=$1;n++} END{printf "%.4f",s/n}')
        NC=$(grep -cE 'NaN|inf' "$LOG" 2>/dev/null || echo 0)
        echo "  pts=${MC} med_ms=${MM} med_toks=${MT} tflop=${AT} loss=${AL} gnorm=${AG} nan=${NC}" >> "$SUM"
        echo "OK|${LABEL}|0|${PEAK}|${AM}|${MM}|${MT}|${AT}|${AL}|${AG}|${NC}" >> "$RF"
    else
        echo "  PARSE_FAIL" >> "$SUM"
        echo "PARSE_FAIL|${LABEL}|0|${PEAK}|0|0|0|0|0|0|0" >> "$RF"
    fi
    grep -E '^\s*\[.*iteration\s+' "$LOG" | head -3 >> "$SUM"
    echo "===== END ${LABEL} rc=${RC} =====" >> "$SUM"
}

# === EXPERIMENTS ===
run_exp "e00_baseline"
run_exp "e01_cuda_graph" --enable-cuda-graph
run_exp "e02_fp8_tensorwise" --fp8-recipe tensorwise
run_exp "e03_fp8_blockwise" --fp8-recipe blockwise --first-last-layers-bf16
run_exp "e04_fp8_delayed" --fp8-recipe delayed
run_exp "e05_overlap_optim" --overlap-param-gather-with-optimizer-step
run_exp "e06_ce_fusion" --cross-entropy-loss-fusion
run_exp "e07_fp8_tw_overlap" --fp8-recipe tensorwise --overlap-param-gather-with-optimizer-step
run_exp "e08_fp8_bw_cg" --fp8-recipe blockwise --first-last-layers-bf16 --enable-cuda-graph
run_exp "e09_fp8_tw_cg" --fp8-recipe tensorwise --enable-cuda-graph

# === FINAL SUMMARY ===
echo "" >> "$SUM"
echo "===== FINAL TABLE =====" >> "$SUM"
echo "label|status|rc|peak|avg_ms|med_ms|med_toks|tflop|loss|gnorm|nan" >> "$SUM"
for f in "$R"/perf_*.result; do [ -f "$f" ] && cat "$f" >> "$SUM"; done
echo "===== ALL DONE @ $(date '+%F %T') =====" >> "$SUM"
echo "SUM=$SUM R=$R"