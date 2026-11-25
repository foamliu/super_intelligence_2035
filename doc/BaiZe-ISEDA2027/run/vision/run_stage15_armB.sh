#!/bin/bash
# ==============================================================================
# run_stage15_armB.sh — Stage-1.5 Mid-Training for ArmB (open_clip ViT-B/16, 768-dim)
#
# Operator instruction 2026-10-18 P0 ④ (Stage-1.5 Mid):
#   - Vision tower: ArmB open_clip_state_dict.pt (86.2M, 768-dim, FROZEN)
#   - Projector: 2-layer MLP 768->2560 (trainable, loaded from Stage-1 step2500)
#   - LLM: Qwen3-4B-Instruct-2507 + LoRA r=64/alpha=128 (trainable)
#   - LR: LoRA=2e-5 / Proj=1e-5, cosine->min_lr=1e-6, warmup 0.002
#   - Steps: 20000, GBS=8, MBS=1, save every 2000, log every 50
#   - Data: LLaVA-558K WebDataset (same as Stage-1 / ④-4ep)
#   - Image: 224px, 196 tokens, no spatial merge
#
# Launch (.12, 8xH100):
#   setsid bash run_stage15_armB.sh > /tmp/stage15_armB.log 2>&1 < /dev/null &
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
LOG=/tmp/stage15_armB.log

echo "===== ArmB Stage-1.5 Mid-Training START $(date '+%F %T') =====" | tee "$LOG"
echo "[stage15-armB] vision=ArmB open_clip ViT-B/16 (86.2M, 768-dim, FROZEN)" >> "$LOG"
echo "[stage15-armB] projector=2-layer MLP 768->2560 (trainable, from Stage-1 step2500)" >> "$LOG"
echo "[stage15-armB] llm=Qwen3-4B-Instruct-2507 + LoRA r=64/alpha=128 (trainable)" >> "$LOG"
echo "[stage15-armB] lr_lora=2e-5 lr_proj=1e-5 ->1e-6, 20000 steps, GBS=8, MBS=1" >> "$LOG"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv >> "$LOG" 2>&1

"$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
    --master_addr=$MASTER_ADDR --master_port=$((29900 + RANDOM % 1000)) \
    mllm_bridge/stage15_train_armB.py \
    --lr_lora 2e-5 --lr_proj 1e-5 --min_lr 1e-6 --nsteps 20000 \
    --gbs 8 --mbs 1 --warmup_frac 0.002 \
    --seq_len 2048 --num_workers 4 \
    --save_steps 2000 --log_steps 50 \
    --lora_r 64 --lora_alpha 128 --lora_dropout 0.05 \
    >> "$LOG" 2>&1

rc=$?
echo "===== ArmB Stage-1.5 done (exit $rc) $(date '+%F %T') =====" >> "$LOG"
exit $rc
