#!/bin/bash
# BaiZe Stage(i) R2 P-9.5 Level-3：torch.profiler top kernels。
# 载体：bf16 速度最优配置 TP1·DP8·MBS2·seq4096（P-9.3/P-9.1 实测 249K tok/s）。
# 跑 50 步，profile 窗口 [10,40)（rank 0），profile_memory=True/record_shapes=True/with_stack=True。
# on_trace_ready 把 key_averages 文本表（按 self CUDA time 排序 top-30）写到 $KEYAVG。
# 不写 chrome trace（任务要求只留摘要）。峰值显存由后台 nvidia-smi 采样。
# 铁律：不改 P-5b recipe；只给结论供 P-8 参考。
# 启动：setsid bash baize_p95_prof.sh &（PPID=1 真后台）
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
OUT="$BASE/data/p5b_l3"
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230

BLEND="1 ${OUT}/p5b_l3_train_s0 1 ${OUT}/p5b_l3_train_s1 1 ${OUT}/p5b_l3_train_s2 1 ${OUT}/p5b_l3_train_s3 1 ${OUT}/p5b_l3_train_s4 1 ${OUT}/p5b_l3_train_s5 1 ${OUT}/p5b_l3_train_s6 1 ${OUT}/p5b_l3_train_s7 1 ${OUT}/p5b_l3_train_s8 1 ${OUT}/p5b_l3_train_s9 1 ${OUT}/p5b_l3_train_s10 1 ${OUT}/p5b_l3_train_s11 1 ${OUT}/p5b_l3_train_s12 1 ${OUT}/p5b_l3_train_s13 1 ${OUT}/p5b_l3_train_s14 1 ${OUT}/p5b_l3_train_s15"

NAME="p95_prof"
LOG="/tmp/baize_${NAME}.log"
KEYAVG="/tmp/baize_p95_keyavg.txt"
SUM="/tmp/baize_p95_prof.log"
: > "$KEYAVG"
: > "$SUM"
echo "===== P-9.5 torch.profiler START @ $(date '+%F %T') config=TP1·DP8·MBS2·seq4096·bf16 iters=50 prof=[10,40) =====" > "$SUM"

# 后台采样峰值显存
PEAK_FILE="/tmp/baize_${NAME}.peakmem"
: > "$PEAK_FILE"
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

cd "$BASE" || exit 1
export BAIZE_PROF_OUT="$KEYAVG"
export BAIZE_PROF_START=10
export BAIZE_PROF_END=40
"$PY/torchrun" --nnodes=1 --nproc_per_node=8 \
    --master_addr=127.0.0.1 --master_port=29931 \
    pretrain_profile_launcher.py \
    --arch mamba2 --name "$NAME" --dir "$BASE/nemo_experiments" \
    --tokenizer-path "$BASE/data/tokenizer_eod" \
    --train-data-path $BLEND \
    --tensor-parallel 1 \
    --train-iters 50 --global-batch-size 1024 --micro-batch-size 2 --seq-length 4096 \
    --eval-interval 250 --eval-iters 0 \
    --save-interval 0 \
    --lr 1e-3 --min-lr 1e-5 --lr-warmup-iters 10 --lr-decay-iters 10 --lr-decay-style WSD \
    --seed 1234 \
    --precision bf16_mixed > "$LOG" 2>&1
RC=$?

kill "$SAMPLER_PID" 2>/dev/null
wait "$SAMPLER_PID" 2>/dev/null
PEAK=$(cat "$PEAK_FILE" 2>/dev/null)

echo "  rc=${RC} peak_gpu_mem_MiB=${PEAK} (max over 8 gpus)" >> "$SUM"

if [ "$RC" -ne 0 ]; then
    echo "  ❌ ERROR 最后 10 行：" >> "$SUM"
    tail -10 "$LOG" >> "$SUM"
else
    echo "  s/iter (last 5) :" >> "$SUM"
    grep -E 'iteration +' "$LOG" | tail -5 >> "$SUM"
    echo "  first iter line :" >> "$SUM"
    grep -E 'iteration +' "$LOG" | head -1 >> "$SUM"
fi

echo "  --- key_averages head (self_cuda_time_total) ---" >> "$SUM"
head -25 "$KEYAVG" >> "$SUM"
echo "" >> "$SUM"
echo "===== P-9.5 torch.profiler END @ $(date '+%F %T') rc=${RC} =====" >> "$SUM"
echo "LOG=$LOG  KEYAVG=$KEYAVG  SUM=$SUM"
