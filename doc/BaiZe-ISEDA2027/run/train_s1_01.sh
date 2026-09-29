#!/bin/bash
# S1-01 基线短程试验：MiniCPM5-1B (LlamaForCausalLM, 24层, GQA KV=2, ~1.04B) 预训练 from scratch
# 阶段 S1 基线复现：建立 loss/吞吐基准
# 带端口冲突自动重试：机房共享节点上 --master_port 可能与其它作业撞车(EADDRINUSE)
set -uo pipefail
cd /nas_train/app.e0031982/code/BaiZe-ISEDA2027

export PYTORCH_CUDA_ALLOC_CONF='expandable_segments:True'
export NPROC_PER_NODE=8
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
# flash_attn_2_cuda C++ 扩展依赖 torch/lib 下的 libc10.so 等共享库
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:$LD_LIBRARY_PATH
export MASTER_ADDR=127.0.0.1

PYPY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python

run_pt() {
    /nas_train/app.e0031982/miniforge3/envs/py310/bin/megatron pt \
        --model models/MiniCPM5-1B \
        --save_safetensors true \
        --dataset /nas_inference/app.e0031982/datasets/openbmb/Ultra-FineWeb-L3/data/ultrafineweb_en_l3/qa \
        --streaming true \
        --packing true \
        --packing_length 4096 \
        --max_length 4096 \
        --tensor_model_parallel_size 1 \
        --micro_batch_size 1 \
        --global_batch_size 1024 \
        --train_iters 300 \
        --finetune true \
        --cross_entropy_loss_fusion true \
        --recompute_granularity selective \
        --optimizer adam \
        --lr 6e-4 \
        --lr_warmup_iters 10 \
        --min_lr 6e-5 \
        --lr_decay_style WSD \
        --lr_wsd_decay_iters 30 \
        --lr_wsd_decay_style exponential \
        --weight_decay 0.1 \
        --output_dir output/S1-01 \
        --save_steps 100 \
        --eval_steps 1000 \
        --eval_iters 10 \
        --dataloader_num_workers 4 \
        --dataset_num_proc 8 \
        --no_save_optim true \
        --no_save_rng true \
        --attention_backend fused
}

for attempt in 1 2 3 4 5; do
    export MASTER_PORT=$($PYPY -c "import socket; s=socket.socket(); s.bind(('127.0.0.1',0)); print(s.getsockname()[1]); s.close()")
    echo "===== LAUNCH attempt=$attempt MASTER_PORT=$MASTER_PORT @ $(date '+%F %T') ====="
    tmp=/tmp/BAIZE_S1-01.attempt${attempt}.log
    if run_pt > "$tmp" 2>&1; then
        cat "$tmp"
        echo "===== SUCCESS (attempt=$attempt) @ $(date '+%F %T') ====="
        exit 0
    else
        rc=$?
        cat "$tmp"
        if grep -q 'address already in use' "$tmp"; then
            echo "===== PORT CONFLICT ($MASTER_PORT), retrying ... ====="
            sleep 2
            continue
        fi
        echo "===== NON-PORT failure (rc=$rc), giving up @ $(date '+%F %T') ====="
        exit $rc
    fi
done
echo "===== exhausted 5 retries @ $(date '+%F %T') ====="
exit 1