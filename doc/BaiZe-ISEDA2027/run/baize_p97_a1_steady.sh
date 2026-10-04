#!/bin/bash
# BaiZe Stage(i) R2 P-9.7：A1 稳态吞吐确认（≥1000 步长跑）。
# 运维指令 2026-10-04：P-9.6 短测 A1=249K vs P-9.1 早测 218K 差 14%（疑早测有争用），
#   必须用 ≥1000 步长跑确认 A1 稳态吞吐。
# 配置固定 A1 = P-9.1 胜出点：seq=4096 / GBS=1024 / TP1·DP8 / MBS=2 / bf16。
# --save-interval 0 不存 ckpt（避免尾部 save gather 干扰）。
# 取 last 100 步稳态均值的 s/iter 与 tok/s；同时报 TFLOP/s/GPU、峰值显存、争用核查。
# 预注册判据：≥240K→确认 249K 可信；218K–240K→取实测值注明短测不可用；<218K→以长跑为准。
# 铁律：不改 recipe、不回训、不存 ckpt —— 只测吞吐。
# 启动：setsid bash baize_p97_a1_steady.sh &（PPID=1 真后台）
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
OUT="$BASE/data/p5b_l3"
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230

BLEND="1 ${OUT}/p5b_l3_train_s0 1 ${OUT}/p5b_l3_train_s1 1 ${OUT}/p5b_l3_train_s2 1 ${OUT}/p5b_l3_train_s3 1 ${OUT}/p5b_l3_train_s4 1 ${OUT}/p5b_l3_train_s5 1 ${OUT}/p5b_l3_train_s6 1 ${OUT}/p5b_l3_train_s7 1 ${OUT}/p5b_l3_train_s8 1 ${OUT}/p5b_l3_train_s9 1 ${OUT}/p5b_l3_train_s10 1 ${OUT}/p5b_l3_train_s11 1 ${OUT}/p5b_l3_train_s12 1 ${OUT}/p5b_l3_train_s13 1 ${OUT}/p5b_l3_train_s14 1 ${OUT}/p5b_l3_train_s15"

NAME="p97_a1_steady"
LOG="/tmp/baize_${NAME}.log"
SUM="/tmp/baize_${NAME}.sum"
PEAK_FILE="/tmp/baize_${NAME}.peakmem"
: > "$LOG"
: > "$SUM"
: > "$PEAK_FILE"

ITERS=1100
SEQ=4096
GBS=1024
MBS=2
TP=1
PORT=29937

echo "===== P-9.7 A1 steady-state throughput START @ $(date '+%F %T') =====" > "$SUM"
echo "  config: TP=${TP} DP=8 MBS=${MBS} seq=${SEQ} GBS=${GBS} bf16 iters=${ITERS} save-interval=0" >> "$SUM"
echo "  M = MBS*seq = $(( MBS * SEQ ))" >> "$SUM"
echo "  token/step = GBS*seq = $(( GBS * SEQ )) = 4.19M" >> "$SUM"

# --- 前置争用核查 ---
echo "" >> "$SUM"
echo "  --- pre-flight contention check ---" >> "$SUM"
echo "  [nvidia-smi compute-apps]:" >> "$SUM"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv 2>&1 >> "$SUM"
echo "  [pgrep other training]:" >> "$SUM"
pgrep -af 'torchrun|pretrain_launcher|python.*train' 2>&1 | grep -v "baize_p97\|$$\|grep" | cut -c1-120 >> "$SUM"
echo "  [GPU util snapshot]:" >> "$SUM"
nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv 2>&1 >> "$SUM"

# --- 后台采样峰值显存 ---
(
  MAX=0
  while :; do
    USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1)
    [ -n "$USED" ] && [ "$USED" -gt "$MAX" ] && MAX=$USED
    echo "$MAX" > "$PEAK_FILE"
    sleep 2
  done
) &
SAMPLER_PID=$!

echo "" >> "$SUM"
echo "  torchrun START @ $(date '+%F %T')" >> "$SUM"

cd "$BASE" || exit 1
"$PY/torchrun" --nnodes=1 --nproc_per_node=8 \
    --master_addr=127.0.0.1 --master_port="$PORT" \
    pretrain_launcher.py \
    --arch mamba2 --name "$NAME" --dir "$BASE/nemo_experiments" \
    --tokenizer-path "$BASE/data/tokenizer_eod" \
    --train-data-path $BLEND \
    --tensor-parallel "$TP" \
    --train-iters "$ITERS" --global-batch-size "$GBS" --micro-batch-size "$MBS" --seq-length "$SEQ" \
    --eval-interval 250 --eval-iters 0 \
    --save-interval 0 \
    --lr 1e-3 --min-lr 1e-5 --lr-warmup-iters 10 --lr-decay-iters 10 --lr-decay-style WSD \
    --seed 1234 \
    --precision bf16_mixed > "$LOG" 2>&1
RC=$?

kill "$SAMPLER_PID" 2>/dev/null
wait "$SAMPLER_PID" 2>/dev/null
PEAK=$(cat "$PEAK_FILE" 2>/dev/null)

echo "  torchrun END @ $(date '+%F %T') rc=${RC}" >> "$SUM"
echo "  peak_gpu_mem_MiB=${PEAK} (max over 8 gpus)" >> "$SUM"

if [ "$RC" -ne 0 ]; then
    echo "  ❌ ERROR 最后 15 行：" >> "$SUM"
    tail -15 "$LOG" >> "$SUM"
    echo "" >> "$SUM"
    echo "===== P-9.7 END @ $(date '+%F %T') rc=${RC} =====" >> "$SUM"
    echo "SUM=$SUM  LOG=$LOG"
    exit 1
fi

# --- 稳态分析：last 100 步（log-interval=10 → step ≥ 1000 的 log 行） ---
echo "" >> "$SUM"
echo "  --- steady-state analysis (last 100 steps, step >= 1000) ---" >> "$SUM"

ITER_LINES=$(grep -E '^\s*\[.*iteration\s+' "$LOG" | awk '{for(i=1;i<=NF;i++) if($i ~ /^iteration$/) {step=$(i+1); gsub(/\/.*/,"",step); if(step+0 >= 1000) print $0}}')

if [ -z "$ITER_LINES" ]; then
    echo "  ⚠️ No iteration lines with step >= 1000 found, falling back to last 10" >> "$SUM"
    ITER_LINES=$(grep -E '^\s*\[.*iteration\s+' "$LOG" | tail -10)
fi

echo "  iteration lines (step >= 1000):" >> "$SUM"
echo "$ITER_LINES" >> "$SUM"

MS_LIST=$(echo "$ITER_LINES" | grep -oP 'elapsed time per iteration \(ms\): \K[0-9.]+')
MS_COUNT=$(echo "$MS_LIST" | wc -l)
if [ "$MS_COUNT" -gt 0 ]; then
    AVG_MS=$(echo "$MS_LIST" | awk '{s+=$1; n++} END {printf "%.1f", s/n}')
    MIN_MS=$(echo "$MS_LIST" | sort -n | head -1)
    MAX_MS=$(echo "$MS_LIST" | sort -n | tail -1)
    TOK_PER_STEP=$(( GBS * SEQ ))
    AVG_TPS=$(awk -v t="$TOK_PER_STEP" -v m="$AVG_MS" 'BEGIN {printf "%.0f", t / (m/1000)}')
    MIN_TPS=$(awk -v t="$TOK_PER_STEP" -v m="$MAX_MS" 'BEGIN {printf "%.0f", t / (m/1000)}')
    MAX_TPS=$(awk -v t="$TOK_PER_STEP" -v m="$MIN_MS" 'BEGIN {printf "%.0f", t / (m/1000)}')
    echo "" >> "$SUM"
    echo "  data points: ${MS_COUNT}" >> "$SUM"
    echo "  avg ms/iter: ${AVG_MS}" >> "$SUM"
    echo "  min ms/iter: ${MIN_MS} (max tok/s: ${MAX_TPS})" >> "$SUM"
    echo "  max ms/iter: ${MAX_MS} (min tok/s: ${MIN_TPS})" >> "$SUM"
    echo "  ★ avg tok/s: ${AVG_TPS}" >> "$SUM"
    echo "" >> "$SUM"
    echo "  --- pre-registered verdict ---" >> "$SUM"
    if [ "$AVG_TPS" -ge 240000 ]; then
        echo "  ✅ ≥240K → 确认 249K 可信 → P-8 按 A1 定（吞吐优先）" >> "$SUM"
    elif [ "$AVG_TPS" -ge 218000 ]; then
        echo "  ⚠️ 218K–240K → 取实测稳态值 ${AVG_TPS} 作为 P-8 基线，注明短测不可用" >> "$SUM"
    else
        echo "  ❌ <218K → 短测有系统性偏差 → 一律以长跑为准 (${AVG_TPS})" >> "$SUM"
    fi
else
    echo "  ⚠️ Could not parse ms/iter from log lines" >> "$SUM"
fi

# TFLOP/s/GPU
TFLOP_LINES=$(echo "$ITER_LINES" | grep -oP 'GPU utilization: \K[0-9.]+(?= TFLOP/s/GPU)')
if [ -n "$TFLOP_LINES" ]; then
    AVG_TFLOP=$(echo "$TFLOP_LINES" | awk '{s+=$1; n++} END {printf "%.1f", s/n}')
    echo "  avg TFLOP/s/GPU: ${AVG_TFLOP}" >> "$SUM"
else
    STEP_TFLOP=$(grep -E 'Step Time.*TFLOP' "$LOG" | tail -10 | grep -oP 'GPU \K[0-9.]+(?= TFLOP/s/GPU)')
    if [ -n "$STEP_TFLOP" ]; then
        AVG_TFLOP=$(echo "$STEP_TFLOP" | awk '{s+=$1; n++} END {printf "%.1f", s/n}')
        echo "  avg TFLOP/s/GPU (from Step Time): ${AVG_TFLOP}" >> "$SUM"
    fi
fi

echo "" >> "$SUM"
echo "  --- early steps (first 3 iteration lines, for comparison) ---" >> "$SUM"
grep -E '^\s*\[.*iteration\s+' "$LOG" | head -3 >> "$SUM"

echo "" >> "$SUM"
echo "===== P-9.7 END @ $(date '+%F %T') rc=${RC} =====" >> "$SUM"
echo "SUM=$SUM  LOG=$LOG  PEAK=$PEAK MiB"
