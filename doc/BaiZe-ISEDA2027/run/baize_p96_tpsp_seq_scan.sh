#!/bin/bash
# BaiZe Stage(i) R2 P-9.6 ①：bf16「训练速度最优」配置搜索（运维 2026-10-04 最高优先指令）。
# 背景：当前最优 ④ TP2·SP·MBS4 峰值仅 51.0G/80G → 余量 ~29G，MBS 还能上抬。
#       要回答「FP8 是否转正」必须先把 M=MBS×seq 抬到 ≥32768（FP8 交叉点 M≈30–32K，非 16K）。
# 两步法：① 先在 bf16 下扫出「训练速度最优」配置（本脚本）→ ② 在该点测 bf16 vs FP8。
# 运维指定方法（④ 确认 12:30）：以「seq 轴」为主轴，不要单纯堆 MBS。
# 杠杆：M = MBS × seq。抬 seq（8192→GBS512 / 16384→GBS256）一次给两样：过 FP8 交叉点 + 长上下文能力。
# 口径不变量（P-9.0）：每步 ≈4.19M token（GBS×seq 同步）：4096→1024 / 8192→512 / 16384→256。
# 其余固定：bf16 / seed1234 / 8×H100（.29）/ 60 步短测 / 不存 ckpt。
# 判据（预注册）：吞吐最优 且 峰值显存 ≤72G（留 ≥8G 余量，避免长跑 OOM）。
# 运维推荐扫描顺序（每点 60 步，M=MBS×seq 均已标）：
#   序 seq   GBS  TP SP  MBS  M     作用
#   1  8192  512  2  on  4   32768  🎯运维预测最优点（过 FP8 交叉点）
#   2  8192  512  2  off 4   32768  SP 对照
#   3  16384 256  2  on  4   65536  更远，看 M 涨是否还涨吞吐
#   4  16384 256  2  off 4   65536  SP 对照
#   5  4096  1024 2  on  8   32768  MBS 轴对照（堆 MBS 到 M=32768）
#   6  4096  1024 2  off 8   32768  MBS/SP 交叉
#   7  4096  1024 2  on  16  65536  上探（预期 OOM，OOM 如实记）
#   8  8192  512  4  on  8   65536  TP4 换显存（若 5/7 OOM 才做）
# 注：点9（TP1·off·MBS2·seq8192）已被正在跑的 P-9.3 seq 扫描覆盖；点10（TP2·SP·MBS4·seq4096）= P-9.2 config④（已测 210K/51021MiB）。
# 剪枝：若点1/2 峰值 >72G 或 OOM → 跳到 3/4、5/6；若点1 吞吐已优于 210K → 优先扩 seq（3/4），不必再堆 MBS。
# 铁律：不改 P-5b recipe、不回训、不改训练代码。启动：setsid bash baize_p96_tpsp_seq_scan.sh &（在 P-9.3 seq scan 结束后再启）。
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
OUT="$BASE/data/p5b_l3"
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230

BLEND="1 ${OUT}/p5b_l3_train_s0 1 ${OUT}/p5b_l3_train_s1 1 ${OUT}/p5b_l3_train_s2 1 ${OUT}/p5b_l3_train_s3 1 ${OUT}/p5b_l3_train_s4 1 ${OUT}/p5b_l3_train_s5 1 ${OUT}/p5b_l3_train_s6 1 ${OUT}/p5b_l3_train_s7 1 ${OUT}/p5b_l3_train_s8 1 ${OUT}/p5b_l3_train_s9 1 ${OUT}/p5b_l3_train_s10 1 ${OUT}/p5b_l3_train_s11 1 ${OUT}/p5b_l3_train_s12 1 ${OUT}/p5b_l3_train_s13 1 ${OUT}/p5b_l3_train_s14 1 ${OUT}/p5b_l3_train_s15"

ITERS=60
SUM="/tmp/baize_p96_tpsp_seq_scan.log"
: > "$SUM"
echo "===== P-9.6① bf16 最优配置搜索 START @ $(date '+%F %T') iters=${ITERS} precision=bf16_mixed ===== " > "$SUM"

# 配置：NAME|seq|GBS|TP|SP(0/1)|MBS|port
run_one() {
    local NAME="$1" SEQ="$2" GBS="$3" TP="$4" SP="$5" MBS="$6" PORT="$7"
    local LOG="/tmp/baize_${NAME}.log"
    echo "" >> "$SUM"
    echo "===== ${NAME} START @ $(date '+%F %T') seq=${SEQ} GBS=${GBS} TP=${TP} SP=${SP} MBS=${MBS} M=$(( MBS * SEQ )) port=${PORT} =====" >> "$SUM"

    local PEAK_FILE="/tmp/baize_${NAME}.peakmem"
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
    local SAMPLER_PID=$!

    cd "$BASE" || exit 1
    local SPARG=""
    [ "$SP" = "1" ] && SPARG="--sequence-parallel"
    "$PY/torchrun" --nnodes=1 --nproc_per_node=8 \
        --master_addr=127.0.0.1 --master_port="$PORT" \
        pretrain_launcher.py \
        --arch mamba2 --name "$NAME" --dir "$BASE/nemo_experiments" \
        --tokenizer-path "$BASE/data/tokenizer_eod" \
        --train-data-path $BLEND \
        --tensor-parallel "$TP" $SPARG \
        --train-iters "$ITERS" --global-batch-size "$GBS" --micro-batch-size "$MBS" --seq-length "$SEQ" \
        --eval-interval 250 --eval-iters 0 \
        --save-interval 99999 \
        --lr 1e-3 --min-lr 1e-5 --lr-warmup-iters 10 --lr-decay-iters 10 --lr-decay-style WSD \
        --seed 1234 \
        --precision bf16_mixed > "$LOG" 2>&1
    local RC=$?

    kill "$SAMPLER_PID" 2>/dev/null
    wait "$SAMPLER_PID" 2>/dev/null
    local PEAK=$(cat "$PEAK_FILE" 2>/dev/null)
    echo "  rc=${RC} peak_gpu_mem_MiB=${PEAK} (max over 8 gpus)" >> "$SUM"

    if [ "$RC" -ne 0 ]; then
        echo "  ❌ OOM/ERROR 最后 5 行：" >> "$SUM"
        tail -5 "$LOG" >> "$SUM"
        return
    fi
    echo "  s/iter (last 5) + tok/s:" >> "$SUM"
    grep -E 'iteration +' "$LOG" | tail -5 >> "$SUM"
    echo "===== ${NAME} END @ $(date '+%F %T') rc=${RC} =====" >> "$SUM"
}

# 序  seq   GBS  TP SP MBS port   M
run_one p96_s8192_tp2sp_mbs4   8192  512  2  1  4  29901   # 32768 🎯
run_one p96_s8192_tp2_mbs4     8192  512  2  0  4  29903   # 32768
run_one p96_s16384_tp2sp_mbs4  16384 256  2  1  4  29905   # 65536
run_one p96_s16384_tp2_mbs4    16384 256  2  0  4  29907   # 65536
run_one p96_s4096_tp2sp_mbs8   4096  1024 2  1  8  29909   # 32768
run_one p96_s4096_tp2_mbs8     4096  1024 2  0  8  29911   # 32768
run_one p96_s4096_tp2sp_mbs16  4096  1024 2  1  16 29913   # 65536（预期 OOM）
run_one p96_s8192_tp4sp_mbs8   8192  512  4  1  8  29915   # 65536

echo "" >> "$SUM"
echo "===== P-9.6① bf16 最优配置搜索 END @ $(date '+%F %T') ===== " >> "$SUM"