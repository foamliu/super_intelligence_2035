#!/usr/bin/env bash
# Start vLLM OpenAI-compatible server for BaiZe 2B (NemotronH) @ 160k
# Purpose: Replace llama.cpp for generative evals (GSM8K/BBH/HumanEval/MBPP/MATH)
# vLLM has native NemotronHForCausalLM support with proper SSM generation.
#
# Usage (when GPU window available):
#   export CUDA_VISIBLE_DEVICES=0  # single GPU
#   setsid bash baize_vllm_server_160k.sh > /tmp/baize_vllm_server.log 2>&1 < /dev/null &
#
# On .17 (A40, 4 GPUs allocated to posttrain from 11-09):
#   export CUDA_VISIBLE_DEVICES=0
#   setsid bash baize_vllm_server_160k.sh > /tmp/baize_vllm_server.log 2>&1 < /dev/null &
#
# On .29 (during GPU window, share with training — RISKY):
#   export CUDA_VISIBLE_DEVICES=0
#   VLLM_GPU_MEM_UTIL=0.05 setsid bash baize_vllm_server_160k.sh > /tmp/baize_vllm_server.log 2>&1 < /dev/null &

set -euo pipefail

MODEL_PATH="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/hf_iter_160000"
PORT=${VLLM_PORT:-8084}
GPU_MEM_UTIL=${VLLM_GPU_MEM_UTIL:-0.9}
MAX_MODEL_LEN=${VLLM_MAX_MODEL_LEN:-8192}
PY="/nas_train/app.e0031982/miniforge3/envs/vllm/bin/python"

echo "[$(date +%T)] Starting vLLM server..."
echo "  model=$MODEL_PATH"
echo "  port=$PORT"
echo "  gpu_mem_util=$GPU_MEM_UTIL"
echo "  max_model_len=$MAX_MODEL_LEN"

exec "$PY" -m vllm.entrypoints.openai.api_server \
    --model "$MODEL_PATH" \
    --dtype float16 \
    --gpu-memory-utilization "$GPU_MEM_UTIL" \
    --max-model-len "$MAX_MODEL_LEN" \
    --enforce-eager \
    --trust-remote-code \
    --host 127.0.0.1 \
    --port "$PORT" \
    --disable-log-requests
