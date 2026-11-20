#!/usr/bin/env bash
# baize_posttrain_rl_grpo_loop.sh — launch the self-written single-process GRPO
# loop (baize_posttrain_rl_grpo_loop.py). This REPLACES the verl path
# (baize_posttrain_rl_grpo_surrogate.sh) which is conclusively BLOCKED on this
# host (verl 0.4.0 Ray named-actor handshake deadlock; see EXPERIMENTS §R411).
#
# No Ray, no torchrun, no colocated workers -> single process on one GPU.
#
# Usage:
#   bash baize_posttrain_rl_grpo_loop.sh --dry-run
#   bash baize_posttrain_rl_grpo_loop.sh --contam-check
#   bash baize_posttrain_rl_grpo_loop.sh --smoke            # GPU7, 3 steps, R0
#   bash baize_posttrain_rl_grpo_loop.sh --reward-arm R0 --total-steps 200
#   GPUS=7 SFT_CKPT=/path/step105 bash baize_posttrain_rl_grpo_loop.sh --smoke
set -uo pipefail

SCRIPT_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"
VENV_PY="${VENV_PY:-$HOME/code/verl_cu124_venv/bin/python}"
GPUS="${GPUS:-7}"          # default GPU7 (only free GPU; GPU4/5/6 = L4 eval serves)
SFT_CKPT="${SFT_CKPT:-$SCRIPT_DIR/sft_surrogate_runs/minicpm5_agentic_v39_pretok/global_step_105}"

# ---- in-container network hardening (R-launch-fix4, kept; harmless for 1 proc) ----
export NCCL_SOCKET_IFNAME="${NCCL_SOCKET_IFNAME:-bond0}"
export GLOO_SOCKET_IFNAME="${GLOO_SOCKET_IFNAME:-bond0}"
export NCCL_IB_DISABLE="${NCCL_IB_DISABLE:-1}"
export NCCL_NET="${NCCL_NET:-Socket}"
# ---- offline / cache ----
export HF_HUB_OFFLINE="${HF_HUB_OFFLINE:-1}"
export TRANSFORMERS_OFFLINE="${TRANSFORMERS_OFFLINE:-1}"
export TOKENIZERS_PARALLELISM=false

CUDA_VISIBLE_DEVICES="$GPUS" exec "$VENV_PY" "$SCRIPT_DIR/baize_posttrain_rl_grpo_loop.py" \
  --sft-ckpt "$SFT_CKPT" "$@"
