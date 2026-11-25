#!/bin/bash
# ==============================================================================
# run_stage2_armB.sh — Stage-2 Instruct Tuning for ArmB (open_clip ViT-B/16, 768-dim)
#
# Operator instruction 2026-10-18 P0 ④ (Stage-2 Instruct):
#   - Vision tower: ArmB open_clip_state_dict.pt (86.2M, 768-dim, FROZEN)
#   - Projector: 2-layer MLP 768->2560 (trainable, loaded from Stage-1.5 step20000)
#   - LLM: Qwen3-4B-Instruct-2507 + LoRA r=64/alpha=128 (trainable, loaded from Stage-1.5)
#   - LR: LoRA=1e-5 / Proj=5e-6, cosine->min_lr=1e-7, warmup 0.01
#   - Steps: 3500, GBS=8, MBS=1, save every 500, log every 50
#   - Data: LLaVA-NeXT-780k Instruct WebDataset (same as ④-4ep)
#   - Image: 224px, 196 tokens, no spatial merge
#
# PREREQUISITE: Stage-1.5 must have finished (mllm_stage15_armB/step20000/ exists).
#
# Launch (.12, 8xH100), AFTER Stage-1.5 done + smoke test passed:
#   setsid bash run_stage2_armB.sh > /tmp/stage2_armB.log 2>&1 < /dev/null &
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
LOG=/tmp/stage2_armB.log

STAGE15_FINAL=/nas_train/app.e0031982/datasets/baize-vision/out/mllm_stage15_armB/step20000
if [ ! -f "$STAGE15_FINAL/projector.pt" ]; then
    echo "[stage2-armB] FATAL: Stage-1.5 final projector not found at $STAGE15_FINAL/projector.pt" | tee "$LOG"
    echo "[stage2-armB] Stage-1.5 must complete before Stage-2. Aborting." | tee -a "$LOG"
    exit 2
fi

echo "===== ArmB Stage-2 Instruct Tuning START $(date '+%F %T') =====" | tee "$LOG"
echo "[stage2-armB] vision=ArmB open_clip ViT-B/16 (86.2M, 768-dim, FROZEN)" >> "$LOG"
echo "[stage2-armB] projector=2-layer MLP 768->2560 (trainable, from Stage-1.5 step20000)" >> "$LOG"
echo "[stage2-armB] llm=Qwen3-4B-Instruct-2507 + LoRA r=64/alpha=128 (from Stage-1.5, trainable)" >> "$LOG"
echo "[stage2-armB] lr_lora=1e-5 lr_proj=5e-6 ->1e-7, 3500 steps, GBS=8, MBS=1, data=LLaVA-NeXT-780k" >> "$LOG"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv >> "$LOG" 2>&1

"$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
    --master_addr=$MASTER_ADDR --master_port=$((29900 + RANDOM % 1000)) \
    mllm_bridge/stage2_train_armB.py \
    --lr_lora 1e-5 --lr_proj 5e-6 --min_lr 1e-7 --nsteps 3500 \
    --gbs 8 --mbs 1 --warmup_frac 0.01 \
    --seq_len 2048 --num_workers 4 \
    --save_steps 500 --log_steps 50 \
    >> "$LOG" 2>&1

rc=$?
echo "===== ArmB Stage-2 done (exit $rc) $(date '+%F %T') =====" >> "$LOG"
exit $rc
