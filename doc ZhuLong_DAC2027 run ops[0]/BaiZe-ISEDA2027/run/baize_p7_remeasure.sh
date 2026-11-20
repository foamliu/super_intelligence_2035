#!/bin/bash
# BaiZe Stage(i) R2 P-7：训练吞吐幅度核查 —— dense(minicpm5) vs hybrid(mamba2) 同节点同配置稳态 ms/iter 重测。
#   口径 = Round 1 架构对比 / P-3 完全一致：6 卡 TP1/DP6/GBS=6/seq4096/cosine/lr3e-4/warmup100/min_lr3e-5/seed1234/bf16。
#   两个架构都在本节点 (10.239.2.29) 串行跑，train-iters=330（剔除首步后 ≥320 稳态点）。
#   目的：P-7 查明 tab:archcomp 的 "+24%" 是否来自 Round 1 把 hybrid 放到 10.239.2.12（另一节点）测所致。
# 启动：setsid bash baize_p7_remeasure.sh &
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
LOGDIR=/tmp
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230
L3="$BASE/data/ultrafineweb_l3_qa"

SUM="$LOGDIR/baize_p7_sweep.log"
echo "===== P-7 throughput re-measure START @ $(date '+%F %T') (dense=minicpm5 / hybrid=mamba2, 6卡/GBS=6/cosine/lr3e-4/warmup100/seq4096/seed1234/330步) =====" > "$SUM"

# GPU 独占核验（测量前）
{
  echo "--- GPU exclusivity BEFORE @ $(date '+%F %T') ---"
  nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader
  echo "--- compute apps BEFORE ---"
  nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader
} >> "$SUM"

run() {  # $1=ARCH $2=NAME $3=PORT
    local ARCH="$1" NAME="$2" PORT="$3"
    local LOG="$LOGDIR/baize_${NAME}.log"
    echo "===== ${NAME} (arch=${ARCH}) START @ $(date '+%F %T') =====" >> "$SUM"
    cd "$BASE" || exit 1
    "$PY/torchrun" --nnodes=1 --nproc_per_node=6 \
        --master_addr=127.0.0.1 --master_port="$PORT" \
        pretrain_launcher.py \
        --arch "$ARCH" --name "$NAME" --dir "$BASE/nemo_experiments" \
        --tokenizer-path "$BASE/data/tokenizer_eod" \
        --train-data-path "$L3" \
        --tensor-parallel 1 \
        --train-iters 330 --global-batch-size 6 --micro-batch-size 1 --seq-length 4096 \
        --eval-interval 10000 --eval-iters 0 \
        --lr 3e-4 --min-lr 3e-5 --lr-warmup-iters 100 --lr-decay-iters 1000 --lr-decay-style cosine \
        --seed 1234 --precision bf16_mixed > "$LOG" 2>&1
    local RC=$?
    echo "  rc=${RC}" >> "$SUM"
    # 稳态 ms/iter（剔除前 10 步编译/warmup 开销）：mean / median / min / max
    grep -oE 'elapsed time per iteration \(ms\): [0-9.]+' "$LOG" | awk '{print $NF}' > /tmp/.p7_${NAME}_ms.txt
    awk 'NR>10{n++; s+=$1; a[n]=$1; if(min==0||$1<min)min=$1; if($1>max)max=$1} END{for(i=1;i<=n;i++)b[i]=a[i]; asort(b); printf "  steady-state ms/iter: n=%d mean=%.2f median=%.2f min=%.2f max=%.2f\n", n, s/n, (n%2? b[int(n/2)+1] : (b[int(n/2)]+b[int(n/2)+1])/2), min, max}' /tmp/.p7_${NAME}_ms.txt >> "$SUM"
    echo "  ${NAME} DONE @ $(date '+%F %T')" >> "$SUM"
}

run minicpm5 p7_dense 29741
run mamba2 p7_hybrid 29742

# GPU 独占核验（测量后）
{
  echo "--- GPU exclusivity AFTER @ $(date '+%F %T') ---"
  nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader
  echo "--- compute apps AFTER ---"
  nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader
} >> "$SUM"

echo "===== P-7 throughput re-measure ALL DONE @ $(date '+%F %T') =====" >> "$SUM"