#!/bin/bash
# BaiZe Stage(i) R2 P-9.8：bf16 vs FP8 长程一致性 A/B（各 1000 步）。
# 运维 2026-10-04 批准；目的：关闭 P-9.6② 自标的「长跑 loss 质量」风险，为 P-8 配置决策定精度。
# 载体 = P-9.6② 的 FP8 转正点：TP4 · SP-on · MBS8 · seq8192（M=65536）· GBS=512（守 §P-9.0 ≈4.19M tok/步 不变量）。
# 控变量：**只变精度** bf16 vs FP8；两臂共同 CUDA_DEVICE_MAX_CONNECTIONS=1 · seed1234 · WSD/1e-3 不变 · --save-interval 0（不存 ckpt）。
#   臂 A（对照）= bf16_mixed（MAX_CONN=1）—— 全新基线（点8 的 22.16s 是默认连接，此处隔离 MAX_CONN 因子）。
#   臂 B（待测）= FP8 bf16_with_fp8_delayed_scaling_mixed（MAX_CONN=1）—— P-9.6② 实测 17.76s/iter s=1.24。
# 打点：每 100 步记 loss/grad-norm/nan/skipped（从既有 iteration 行抽取 iter 100..1000）；末段报 s/iter/tok/s/峰值显存/TFLOP/s/GPU。
# 🔒 预注册判据（四条全过才「FP8 长程与 bf16 一致」）：
#   1 同 step loss 相对差（末段100步均值）≤1%  2 nan/skipped=0 全程  3 grad-norm 漂移（末段 vs 首段中位/分位）≤10%  4 每100步 loss 曲线最大偏离 ≤2%
# 裁定：四条全过→「FP8 长程可用于 P-8」（候选A 保持 FP8）；任一不过→「P-8 定 bf16」。
# 窗口纪律：若 08:30 未跑完 → 截到已完成步数、如实报告（不硬撑、不挤占 P-6②）。
# 铁律：不改 P-5b recipe、不回训、不存 ckpt、不产出模型；🚫 绝不 kill watchdog loop。
# 顺序：臂 A(bf16) 先 → 臂 B(FP8) 后（bf16 控制臂优先完整跑完）。启动：setsid bash baize_p98_fp8_consistency.sh &
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230
OUT="$BASE/data/p5b_l3"

BLEND="1 ${OUT}/p5b_l3_train_s0 1 ${OUT}/p5b_l3_train_s1 1 ${OUT}/p5b_l3_train_s2 1 ${OUT}/p5b_l3_train_s3 1 ${OUT}/p5b_l3_train_s4 1 ${OUT}/p5b_l3_train_s5 1 ${OUT}/p5b_l3_train_s6 1 ${OUT}/p5b_l3_train_s7 1 ${OUT}/p5b_l3_train_s8 1 ${OUT}/p5b_l3_train_s9 1 ${OUT}/p5b_l3_train_s10 1 ${OUT}/p5b_l3_train_s11 1 ${OUT}/p5b_l3_train_s12 1 ${OUT}/p5b_l3_train_s13 1 ${OUT}/p5b_l3_train_s14 1 ${OUT}/p5b_l3_train_s15"

ITERS=1000
SEQ=8192
GBS=512
TP=4
SP=1
MBS=8
TOKENS_PER_STEP=$(( GBS * SEQ ))   # = 4,194,304 = 4.19M
SUM="/tmp/baize_p98_consistency.log"
: > "$SUM"
echo "===== P-9.8 bf16 vs FP8 long-horizon consistency A/B START @ $(date '+%F %T') =====" > "$SUM"
echo "  载体: TP=${TP} SP-on MBS=${MBS} seq=${SEQ} GBS=${GBS} M=$(( MBS * SEQ )) token/step=${TOKENS_PER_STEP} iters=${ITERS} seed=1234 save-interval=0" >> "$SUM"
echo "  两臂共同: CUDA_DEVICE_MAX_CONNECTIONS=1 · WSD lr=1e-3 min-lr=1e-5 warmup10 decay10" >> "$SUM"
echo "  臂 A(对照)=bf16_mixed  臂 B(待测)=FP8 bf16_with_fp8_delayed_scaling_mixed" >> "$SUM"
echo "  P-9.6② 参考: FP8(MAX_CONN=1)=17.76s/iter s=1.24 / bf16(默认连接)=22.16s/iter ~189K tok/s" >> "$SUM"
echo "  预期成本: bf16 1000×22.16s≈6.2h + FP8 1000×17.76s≈5.0h → 合计≈11.2h（略超 ~10h 夜间窗口）" >> "$SUM"
echo "  🔒 预注册判据: 1)loss末段100步相对差≤1% 2)nan/skipped=0全程 3)grad-norm漂移≤10% 4)每100步loss最大偏离≤2%" >> "$SUM"

# ---- 前置争用核验 ----
echo "" >> "$SUM"
echo "  --- pre-flight contention check @ $(date '+%F %T') ---" >> "$SUM"
echo "  [nvidia-smi compute-apps]:" >> "$SUM"
nvidia-smi --query-compute-apps=pid,process_name,used_gpu_memory --format=csv 2>/dev/null | cut -c1-120 >> "$SUM"
echo "  [pgrep other training/pretrain_launcher]:" >> "$SUM"
pgrep -af 'pretrain_launcher|torchrun|baize_p9' 2>/dev/null | grep -v "baize_p98" | cut -c1-120 >> "$SUM"
echo "  [GPU util snapshot]:" >> "$SUM"
nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv 2>/dev/null >> "$SUM"

run_arm() {
    local NAME="$1" PREC="$2" PORT="$3"
    local LOG="/tmp/baize_${NAME}.log"
    local PEAK_FILE="/tmp/baize_${NAME}.peakmem"
    : > "$PEAK_FILE"
    echo "" >> "$SUM"
    echo "===== ${NAME} START @ $(date '+%F %T') precision=${PREC} MAX_CONN=1 M=$(( MBS * SEQ )) port=${PORT} =====" >> "$SUM"

    # 峰值显存采样器（每 3s 取 8 卡最大 used 的最大值）
    (
      MAX=0
      while :; do
        USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1)
        [ -n "$USED" ] && [ "$USED" -gt "$MAX" ] && MAX=$USED
        echo "$MAX" > "$PEAK_FILE"
        sleep 3
      done
    ) &
    local SAMPLER_PID=$!

    cd "$BASE" || exit 1
    # --save-interval 0：不存 ckpt（避免尾部 save gather 干扰；与 P-9.6②/P-9.7 同口径）。
    CUDA_DEVICE_MAX_CONNECTIONS=1 "$PY/torchrun" --nnodes=1 --nproc_per_node=8 \
      --master_addr=127.0.0.1 --master_port="$PORT" \
      pretrain_launcher.py \
      --arch mamba2 --name "$NAME" --dir "$BASE/nemo_experiments" \
      --tokenizer-path "$BASE/data/tokenizer_eod" \
      --train-data-path $BLEND \
      --tensor-parallel "$TP" --sequence-parallel \
      --train-iters "$ITERS" --global-batch-size "$GBS" --micro-batch-size "$MBS" --seq-length "$SEQ" \
      --eval-interval 250 --eval-iters 0 \
      --save-interval 0 \
      --lr 1e-3 --min-lr 1e-5 --lr-warmup-iters 10 --lr-decay-iters 10 --lr-decay-style WSD \
      --seed 1234 \
      --precision "$PREC" > "$LOG" 2>&1
    local RC=$?

    kill "$SAMPLER_PID" 2>/dev/null
    wait "$SAMPLER_PID" 2>/dev/null
    local PEAK=$(cat "$PEAK_FILE" 2>/dev/null)
    echo "  rc=${RC} peak_gpu_mem_MiB=${PEAK} (max over 8 gpus)" >> "$SUM"

    if [ "$RC" -ne 0 ]; then
        echo "  ⚠️ rc!=0（可能尾部存 ckpt OOM，但 s/iter 已在 iteration 行测到）。最后 6 行：" >> "$SUM"
        tail -6 "$LOG" >> "$SUM"
    fi

    # ---- 每 100 步打点：loss / grad norm / number of skipped ----
    echo "  --- per-100-step metrics (loss / grad-norm / skipped) ---" >> "$SUM"
    local i
    for i in 100 200 300 400 500 600 700 800 900 1000; do
        local LINE
        LINE=$(grep -E "iteration +${i}/" "$LOG" | tail -1)
        if [ -n "$LINE" ]; then
            local LOSS GN SKIP ELAPSED
            LOSS=$(echo "$LINE" | grep -oE 'lm loss: [0-9.eE+-]+' | head -1 | sed 's/lm loss: //')
            GN=$(echo "$LINE"   | grep -oE 'grad norm: [0-9.eE+-]+' | head -1 | sed 's/grad norm: //')
            SKIP=$(echo "$LINE" | grep -oE 'number of ski[a-z]*: [0-9]+' | head -1)
            ELAPSED=$(echo "$LINE" | grep -oE 'elapsed time per iteration \(ms\): [0-9.]+' | grep -oE '[0-9.]+$')
            printf "    iter=%4s  loss=%-12s grad_norm=%-8s %-22s elapsed_ms=%s\n" "$i" "$LOSS" "$GN" "$SKIP" "$ELAPSED" >> "$SUM"
        else
            echo "    iter=${i}  (NO LOG LINE — 未跑到此步)" >> "$SUM"
        fi
    done
    # NaN 检测：扫全日志有无 nan/inf/overflow/skip
    local NANCNT
    NANCNT=$(grep -iE 'nan|inf |overflow|loss scale: 0' "$LOG" | grep -viE 'loss scale: 1.0|contain|install|channel' | wc -l)
    echo "  nan/overflow 疑似行数(粗扫, 排除 loss-scale=1.0/无关) = ${NANCNT}" >> "$SUM"

    # ---- 末段 last-100 步稳态：s/iter / tok/s ----
    echo "  --- last-100-step steady-state (iters $(( ITERS-100 ))-${ITERS}) ---" >> "$SUM"
    grep -E 'iteration +' "$LOG" | awk -v lo=$(( ITERS-100 )) -v hi="$ITERS" '
        { for(i=1;i<=NF;i++){ if($i ~ /iteration/){ split($(i+1),a,"/"); it=a[1]+0 } }
          if(it>=lo && it<=hi){
            ms=0; for(i=1;i<=NF;i++){ if($i ~ /elapsed/){ split($(i+4),b,"("); ms=b[1]+0 } }
            if(ms>0){ n++; sum+=ms }
          } }
        END{ if(n>0) printf "    last-100 n=%d mean_s_per_iter=%.3f  tok/s=%.0f\n", n, sum/n/1000, ('"$TOKENS_PER_STEP"'*n)/(sum/1000) }' >> "$SUM"
    echo "  TFLOP/s/GPU (末段, 从 Step Time 行)：" >> "$SUM"
    grep -oE 'GPU utilization: [0-9.]+TFLOP/s/GPU' "$LOG" | tail -10 >> "$SUM"

    echo "===== ${NAME} END @ $(date '+%F %T') rc=${RC} =====" >> "$SUM"
}

# 臂 A（对照）= bf16 —— 先跑（控制臂优先完整跑完）
run_arm p98_armA_bf16_tp4sp_mbs8  bf16_mixed                              29931
# 臂 B（待测）= FP8 —— 后跑
run_arm p98_armB_fp8_tp4sp_mbs8   bf16_with_fp8_delayed_scaling_mixed    29933

echo "" >> "$SUM"
echo "===== P-9.8 A/B END @ $(date '+%F %T') =====" >> "$SUM"
echo "  下一步（运维裁决后由 agent 执行）：比对两臂逐 100 步 loss/grad-norm/skip → 按预注册四判据裁定 → 写入 EXPERIMENTS_ROUND2 P-9.8 节" >> "$SUM"
