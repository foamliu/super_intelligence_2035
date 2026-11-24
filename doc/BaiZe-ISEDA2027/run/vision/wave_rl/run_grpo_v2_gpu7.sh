#!/usr/bin/env bash
# run_grpo_v2_gpu7.sh — Stage-2W GRPOv2 launcher (用户令 2026-11-24 · GRPO 改进).
# 改进：① 冷启动 SFT(0.70) 非 RFT2(0.90) ② 奖励分解 β>α ③ 更难训练题 ④ ≥500 步+配对检验.
# 用法: setsid bash vision/wave_rl/run_grpo_v2_gpu7.sh > /tmp/grpo_v2_launch.log 2>&1 < /dev/null &
set -euo pipefail
CUDA_VIS="${CUDA_VIS:-7}"
N_STEPS="${N_STEPS:-500}"
GROUP="${GROUP:-4}"
BATCH="${BATCH:-2}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VQA_TOOL="$(dirname "$SCRIPT_DIR")/vqa_tool"
INIT_ADAPTER="${INIT_ADAPTER:-$VQA_TOOL/strengthen_runs/sft2_adapter_seed11}"
PY="${PY:-/nas_data/app.e0031982/miniforge3/envs/py310/bin/python}"
LOCK=/tmp/run_grpo_v2_gpu7.lock
exec 9>"$LOCK"
if ! flock -n 9; then echo "[$(date +%H:%M:%S)] another run holds lock. exit." >&2; exit 0; fi
# GPU 空闲守卫
idle_count=0
while [ "$idle_count" -lt 2 ]; do
  busy=0
  for idx in $(echo "$CUDA_VIS" | tr ',' ' '); do
    mem=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i "$idx" 2>/dev/null | tr -d ' ')
    util=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits -i "$idx" 2>/dev/null | tr -d ' ')
    if [ "${mem:-0}" -ge 5000 ] || [ "${util:-0}" -ge 10 ]; then busy=1; fi
  done
  if [ "$busy" = "0" ]; then idle_count=$((idle_count+1)); else idle_count=0; fi
  [ "$idle_count" -ge 2 ] && break
  echo "[$(date +%H:%M:%S)] waiting GPU $CUDA_VIS idle..."; sleep 60
done
echo "[$(date +%H:%M:%S)] GPU $CUDA_VIS free.Launching GRPOv2 (cold-start SFT=$INIT_ADAPTER, steps=$N_STEPS)."
cd "$VQA_TOOL"
export CUDA_VISIBLE_DEVICES="$CUDA_VIS" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
$PY grpo_mllm_wave_v2.py --init_adapter "$INIT_ADAPTER" \
  --total_steps "$N_STEPS" --group_size "$GROUP" --batch_prompts "$BATCH"
echo "[$(date +%H:%M:%S)] GRPOv2 finished."
