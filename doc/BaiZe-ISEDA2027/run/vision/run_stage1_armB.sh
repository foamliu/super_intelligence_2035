#!/bin/bash
# ==============================================================================
# run_stage1_armB.sh — Stage-1 Alignment for ArmB (open_clip ViT-B/16, 768-dim)
#
# Operator instruction 2026-10-18 P0 ④:
#   - Vision tower: ArmB open_clip_state_dict.pt (86.2M, 768-dim, FROZEN)
#   - Projector: 2-layer MLP 768->2560 (trainable)
#   - LLM: Qwen3-4B-Instruct-2507 (FROZEN)
#   - LR=1e-4, cosine->min_lr=1e-6, warmup 0.002, 2500 steps, GBS=8, MBS=1
#   - Data: LLaVA-558K WebDataset (same as ④-4ep Stage-1)
#   - Image: 224px, 196 tokens, no spatial merge
#
# Launch (.12, 8xH100):
#   setsid bash run_stage1_armB.sh > /tmp/stage1_armB.log 2>&1 < /dev/null &
# ==============================================================================
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export NCCL_TIMEOUT=1800
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export MASTER_ADDR=127.0.0.1
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
LOG=/tmp/stage1_armB.log

echo "===== ArmB Stage-1 Alignment START $(date '+%F %T') =====" | tee "$LOG"
echo "[stage1-armB] vision=ArmB open_clip ViT-B/16 (86.2M, 768-dim, FROZEN)" >> "$LOG"
echo "[stage1-armB] projector=2-layer MLP 768->2560 (trainable)" >> "$LOG"
echo "[stage1-armB] llm=Qwen3-4B-Instruct-2507 (FROZEN)" >> "$LOG"
echo "[stage1-armB] lr=1e-4 cosine->1e-6, 2500 steps, GBS=8, MBS=1" >> "$LOG"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv >> "$LOG" 2>&1

"$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
    --master_addr=$MASTER_ADDR --master_port=$((29900 + RANDOM % 1000)) \
    mllm_bridge/stage1_train_armB.py \
    --lr 1e-4 --min_lr 1e-6 --nsteps 2500 \
    --gbs 8 --mbs 1 --warmup_frac 0.002 \
    --seq_len 2048 --num_workers 4 \
    --save_steps 500 --log_steps 10 \
    >> "$LOG" 2>&1

rc=$?
echo "===== ArmB Stage-1 done (exit $rc) $(date '+%F %T') =====" >> "$LOG"
exit $rc
