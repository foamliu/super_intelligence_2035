#!/bin/bash
# BaiZe-2B throughput optim ROUND 2c (2026-10-24): final MBS increase attempts
# REF: e09_fp8_tw_cg = 297279 tok/s (best). R2/R2b exhausted most options.
# R2c: #1 MBS3 GBS1008 (divisible by 3*8=24) + defrag + CG  -- key untested MBS3
#      #1 MBS4 NO CG + FP8 TW -- trade 30GB CG pools for MBS4
#      #1 MBS3 NO CG + FP8 TW -- fallback if e18 OOMs
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
OUT="$BASE/data/p5b_l3"
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230
BLEND="1 ${OUT}/p5b_l3_train_s0 1 ${OUT}/p5b_l3_train_s1 1 ${OUT}/p5b_l3_train_s2 1 ${OUT}/p5b_l3_train_s3 1 ${OUT}/p5b_l3_train_s4 1 ${OUT}/p5b_l3_train_s5 1 ${OUT}/p5b_l3_train_s6 1 ${OUT}/p5b_l3_train_s7 1 ${OUT}/p5b_l3_train_s8 1 ${OUT}/p5b_l3_train_s9 1 ${OUT}/p5b_l3_train_s10 1 ${OUT}/p5b_l3_train_s11 1 ${OUT}/p5b_l3_train_s12 1 ${OUT}/p5b_l3_train_s13 1 ${OUT}/p5b_l3_train_s14 1 ${OUT}/p5b_l3_train_s15"
ITERS=80; SEQ=4096
R="/tmp/baize_perf_r2c"; mkdir -p "$R"; SUM="$R/summary.txt"
echo "ROUND2c START @ $(date '+%F %T')" >> "$SUM"
echo "REF: e09_fp8_tw_cg = 297279 tok/s med_ms=14109 peak=66923MiB MBS2/GBS1024" >> "$SUM"
echo "R2b recap: e10b MBS4+defrag OOM(80.6GB) | e11b MBS3 GBS1024 FAIL(divisibility) | e15 GBS2048=297K | e16 SP FAIL | e17 MBS4+flbf16 OOM(76GB)" >> "$SUM"
nvidia-smi --query-gpu=index,memory.used --format=csv,noheader >> "$SUM" 2>&1
echo "" >> "$SUM"
pkill -f 'perf_r2c_' 2>/dev/null; sleep 3

run_exp() {
    local LABEL="$1"; local MBS="$2"; local GBS="$3"; local ENVV="$4"; shift 4
    local EXTRA="$@"
    local NAME="perf_r2c_${LABEL}"
    local LOG="$R/${NAME}.log"; local PF="$R/${NAME}.peakmem"; local RF="$R/${NAME}.result"
    : > "$PF"
    echo "" >> "$SUM"
    echo "===== EXP ${LABEL} @ $(date '+%F %T') MBS=${MBS} GBS=${GBS} env=[${ENVV}] args=[${EXTRA}] =====" >> "$SUM"
    ( MAX=0; while :; do
        U=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1)
        [ -n "$U" ] && [ "$U" -gt "$MAX" ] && MAX=$U; echo "$MAX" > "$PF"; sleep 2
      done ) &
    local SP=$!
    cd "$BASE" || exit 1
    env $ENVV "$PY/torchrun" --nnodes=1 --nproc_per_node=8 \
        --master_addr=127.0.0.1 --master_port=29973 \
        pretrain_launcher.py \
        --arch mamba2 --name "$NAME" --dir "$BASE/nemo_experiments" \
        --tokenizer-path "$BASE/data/tokenizer_eod" \
        --train-data-path $BLEND \
        --train-iters "$ITERS" --global-batch-size "$GBS" --micro-batch-size "$MBS" --seq-length "$SEQ" \
        --tensor-parallel 1 --eval-interval 99999 --eval-iters 0 --save-interval 0 \
        --lr 1e-3 --min-lr 1e-5 --lr-warmup-iters 5 --lr-decay-iters 5 --lr-decay-style WSD \
        --seed 1234 --precision bf16_mixed $EXTRA > "$LOG" 2>&1
    local RC=$?
    kill "$SP" 2>/dev/null; wait "$SP" 2>/dev/null
    local PEAK=$(cat "$PF" 2>/dev/null)
    echo "  rc=${RC} peak=${PEAK}" >> "$SUM"
    if [ "$RC" -ne 0 ]; then
        grep -iE "OutOfMemory|CUDA out of memory|AssertionError|RuntimeError|unrecognized|invalid|ValueError" "$LOG" | head -3 >> "$SUM"
        tail -6 "$LOG" >> "$SUM"
        echo "FAIL|${LABEL}|${RC}|${PEAK}|0|0|0|0|0|0|0" >> "$RF"
        echo "===== END ${LABEL} rc=${RC} =====" >> "$SUM"; sleep 10; return
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
        NC=$(echo "$IL" | grep -oP 'number of nan iterations:\s+\K[0-9]+' | awk '{s+=$1} END{print s+0}')
        echo "  pts=${MC} med_ms=${MM} med_toks=${MT} tflop=${AT} loss=${AL} gnorm=${AG} nan=${NC}" >> "$SUM"
        echo "OK|${LABEL}|0|${PEAK}|${AM}|${MM}|${MT}|${AT}|${AL}|${AG}|${NC}" >> "$RF"
    else
        echo "  PARSE_FAIL" >> "$SUM"
        echo "PARSE_FAIL|${LABEL}|0|${PEAK}|0|0|0|0|0|0|0" >> "$RF"
    fi
    grep -E '^\s*\[.*iteration\s+' "$LOG" | head -3 >> "$SUM"
    echo "===== END ${LABEL} rc=${RC} =====" >> "$SUM"
    sleep 10
}

# === ROUND 2c EXPERIMENTS ===
# #1 THE key untested: MBS3 GBS1008 (1008/24=42 divisible) + defrag + CG + FP8 TW
# R2b e11b FAILED on divisibility (GBS1024%24!=0), NOT on OOM. With GBS1008 + expandable_segments,
# MBS3+CG might fit (~77-78GB est, within 80GB).
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True NCCL_GRAPH_REGISTER=0 run_exp "e18_mbs3_gbs1008_cg" 3 1008 "" --fp8-recipe tensorwise --enable-cuda-graph

# #1 trade CG for MBS4: NO CUDA Graphs (frees ~30GB CG pools) + FP8 TW + MBS4
# Without CG, FP8 has kernel launch overhead, but MBS4 may give better GPU utilization.
run_exp "e19_mbs4_nocg_fp8" 4 1024 "" --fp8-recipe tensorwise

# #1 fallback: MBS3 NO CG + FP8 TW. If e18 OOMs, this tests MBS3 without 30GB CG overhead.
run_exp "e20_mbs3_nocg_fp8" 3 1008 "" --fp8-recipe tensorwise

# === FINAL SUMMARY ===
echo "" >> "$SUM"
echo "===== ROUND2c FINAL TABLE =====" >> "$SUM"
echo "label|status|rc|peak|avg_ms|med_ms|med_toks|tflop|loss|gnorm|nan" >> "$SUM"
for f in "$R"/perf_r2c_*.result; do [ -f "$f" ] && cat "$f" >> "$SUM"; done
echo "===== ROUND2c ALL DONE @ $(date '+%F %T') =====" >> "$SUM"
echo "SUM=$SUM R=$R"
