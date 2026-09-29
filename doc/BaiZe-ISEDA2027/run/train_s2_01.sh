#!/bin/bash
# S2-01 单变量扫描：Stable LR 6e-4 → 1e-3（其余同 S1-01 基线），80 steps
# 目的：定位学习率敏感性（无模型改动，最便宜）
# 先试 micro_batch_size=2 提速；OOM 则自动回退 micro_batch_size=1
set -uo pipefail
cd /nas_train/app.e0031982/code/BaiZe-ISEDA2027

export PYTORCH_CUDA_ALLOC_CONF='expandable_segments:True'
export NPROC_PER_NODE=8
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
# flash_attn_2_cuda C++ 扩展依赖 torch/lib 下的 libc10.so 等共享库
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:$LD_LIBRARY_PATH
export MASTER_ADDR=127.0.0.1

PYPY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
MEGATRON=/nas_train/app.e0031982/miniforge3/envs/py310/bin/megatron

# 核心训练命令；$1 = micro_batch_size
run_pt() {
    local MB="$1"
    "$MEGATRON" pt \
        --model models/MiniCPM5-1B \
        --save_safetensors true \
        --dataset /nas_inference/app.e0031982/datasets/openbmb/Ultra-FineWeb-L3/data/ultrafineweb_en_l3/qa \
        --streaming true \
        --packing true \
        --packing_length 4096 \
        --max_length 4096 \
        --tensor_model_parallel_size 1 \
        --micro_batch_size "$MB" \
        --global_batch_size 1024 \
        --train_iters 80 \
        --finetune true \
        --cross_entropy_loss_fusion true \
        --recompute_granularity selective \
        --optimizer adam \
        --lr 1e-3 \
        --lr_warmup_iters 10 \
        --min_lr 1e-4 \
        --lr_decay_style WSD \
        --lr_wsd_decay_iters 8 \
        --lr_wsd_decay_style exponential \
        --weight_decay 0.1 \
        --output_dir output/S2-01 \
        --save_steps 100 \
        --eval_steps 1000 \
        --eval_iters 10 \
        --dataloader_num_workers 4 \
        --dataset_num_proc 8 \
        --no_save_optim true \
        --no_save_rng true \
        --attention_backend fused
}

# 带端口冲突重试的拉起；返回值：0 成功，否则失败（rc 透传）
launch() {
    local MB="$1"
    local TAG="mb${MB}"
    for attempt in 1 2 3 4 5; do
        export MASTER_PORT=$("$PYPY" -c "import socket; s=socket.socket(); s.bind(('127.0.0.1',0)); print(s.getsockname()[1]); s.close()")
        local tmp="/tmp/BAIZE_S2-01.${TAG}.attempt${attempt}.log"
        echo "===== LAUNCH mb=$MB attempt=$attempt MASTER_PORT=$MASTER_PORT @ $(date '+%F %T') ====="
        if run_pt "$MB" > "$tmp" 2>&1; then
            cat "$tmp"
            echo "===== SUCCESS (mb=$MB attempt=$attempt) @ $(date '+%F %T') ====="
            return 0
        else
            local rc=$?
            cat "$tmp"
            if grep -q 'address already in use' "$tmp"; then
                echo "===== PORT CONFLICT ($MASTER_PORT), retrying ... ====="
                sleep 2
                continue
            fi
            echo "===== NON-PORT failure (mb=$MB rc=$rc), keep log $tmp ====="
            return "$rc"
        fi
    done
    echo "===== exhausted 5 retries (mb=$MB) @ $(date '+%F %T') ====="
    return 1
}

# 先试 micro_batch_size=2 提速；OOM 则回退 1
launch 2
rc=$?
if [ "$rc" -ne 0 ]; then
    if cat /tmp/BAIZE_S2-01.mb2.attempt*.log 2>/dev/null | grep -qiE 'out of memory|CUDA error|RuntimeError.*memory'; then
        echo "===== OOM with mb=2 detected, falling back to mb=1 @ $(date '+%F %T') ====="
        launch 1
        exit $?
    fi
    exit "$rc"
fi
exit 0