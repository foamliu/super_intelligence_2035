#!/usr/bin/env bash
# run_grpo_wave_gpu67.sh — Stage-2W GRPO launcher for .17 (用户令 2026-11-19 · 修正 Option B).
#
# 演进：
#   * 旧版（已备份为 .obsolete_textbackbone_20261119.bak）面向 .12 文本骨干，强制校验
#     /nas_data/.../wave_sft_stage1w/{qwen3vl_2b_text_extracted,eval_results.json,step*/adapter_config.json}
#     在位，缺则 BLOCKED——等「运维 staging 或 Option B 拍板」。
#   * 2026-11-19「修正 Option B」：Qwen3.5-2B 是原生多模态 MLLM，**直接对完整模型（含视觉塔）
#     做 LoRA 微调，不剥离视觉塔**。Option B 已在 BAIZE_VISION_TASK.md 授权（commit
#     40e70ea75「授权Option B」+ f98ac524f「修正Option B」）——**不再等拍板**。
#   * step (b) SFT 已由 v2 加强管线完成：vision/vqa_tool/strengthen_runs/rft2_adapter_seed11
#     （pre 60%→v2-RFT 90%，McNemar b=7/c=0/p=0.0156），在 :30003 服务，WaveView 全队列
#     V2 vs V0 p=0.008 验证。故本脚本直接补 step (c) 缺口=完整 MLLM 上的 GRPO。
#
# 本脚本启动 vision/vqa_tool/grpo_mllm_wave.py（完整 Qwen3.5-2B MLLM + LoRA + 可验证奖励）。
#   - 冷启动挂 v2 RFT adapter（is_trainable=True），从已强化的策略继续 GRPO。
#   - 默认单卡 GPU 7（2B LoRA 足够；**不扰 GPU 6 上的常驻 VQA 服务**）。可用 CUDA_VIS 覆盖。
#
# 用法：
#   setsid bash vision/wave_rl/run_grpo_wave_gpu67.sh > /tmp/grpo_wave_gpu67.log 2>&1 < /dev/null &
# 可覆盖：CUDA_VIS / N_STEPS / GROUP / BATCH / INIT_ADAPTER / GRPO_OUT

set -euo pipefail

CUDA_VIS="${CUDA_VIS:-7}"            # 单卡=GPU7；如要 GPU6-7 双卡改 "6,7" 并配脚本
N_STEPS="${N_STEPS:-500}"
GROUP="${GROUP:-4}"
BATCH="${BATCH:-2}"
GRPO_OUT="${GRPO_OUT:-/nas_data/app.e0031982/datasets/baize-vision/out/wave_grpo_stage2w_mllm}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VISION_DIR="$(dirname "$SCRIPT_DIR")"
VQA_TOOL="$VISION_DIR/vqa_tool"
INIT_ADAPTER="${INIT_ADAPTER:-$VQA_TOOL/strengthen_runs/rft2_adapter_seed11}"
PY="${PY:-/nas_data/app.e0031982/miniforge3/envs/py310/bin/python}"
mkdir -p "$GRPO_OUT"

LOCK=/tmp/run_grpo_wave_gpu67.lock
exec 9>"$LOCK"
if ! flock -n 9; then
  echo "[$(date +%H:%M:%S)] Another run_grpo_wave_gpu67.sh holds the lock. Exiting." >&2
  exit 0
fi

LOG="$GRPO_OUT/launcher_$(date +%Y%m%d_%H%M%S).log"
{
  echo "=== Stage-2W GRPO launcher · 修正 Option B（完整 MLLM）==="
  echo "  CUDA_VISIBLE_DEVICES: $CUDA_VIS"
  echo "  script : $VQA_TOOL/grpo_mllm_wave.py"
  echo "  init_adapter(cold-start): $INIT_ADAPTER"
  echo "  out    : $GRPO_OUT"
  echo "  steps=$N_STEPS group=$GROUP batch=$BATCH"
  echo "  Started: $(date)"
} | tee "$LOG"

# ── 前置校验（不再 BLOCKED 等拍板；只校验脚本与冷启动 adapter 在位）──
if [ ! -f "$VQA_TOOL/grpo_mllm_wave.py" ]; then
  echo "[ERROR] 缺 GRPO 脚本: $VQA_TOOL/grpo_mllm_wave.py" | tee -a "$LOG"; exit 1
fi
if [ ! -d "$INIT_ADAPTER" ]; then
  echo "[WARN] 冷启动 adapter 不在位: $INIT_ADAPTER —— 将用 fresh LoRA（从基模起步）" | tee -a "$LOG"
  ADAPTER_ARG=""
else
  echo "[OK] 冷启动 adapter 在位: $INIT_ADAPTER" | tee -a "$LOG"
  ADAPTER_ARG="--init_adapter $INIT_ADAPTER"
fi

# ── GPU 空闲守卫（沿用 run_sft_wave.sh 的安全口径：不打扰常驻 VQA/pretrain）──
# 仅当目标卡 mem<5000MiB 且 util<10% 持续 2 次才启动，避免抢卡 OOM。
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
  echo "[$(date +%H:%M:%S)] waiting for GPU $CUDA_VIS idle (mem<5000/util<10)..." | tee -a "$LOG"
  sleep 60
done
echo "[$(date +%H:%M:%S)] GPU $CUDA_VIS confirmed free. Launching GRPO." | tee -a "$LOG"

cd "$VQA_TOOL"
export CUDA_VISIBLE_DEVICES="$CUDA_VIS"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
TRAIN_LOG="$GRPO_OUT/grpo_mllm_$(date +%Y%m%d_%H%M%S).log"
echo "[launch] $PY grpo_mllm_wave.py  log=$TRAIN_LOG" | tee -a "$LOG"
$PY grpo_mllm_wave.py \
  --output_dir "$GRPO_OUT" \
  --total_steps "$N_STEPS" --group_size "$GROUP" --batch_prompts "$BATCH" \
  $ADAPTER_ARG \
  2>&1 | tee "$TRAIN_LOG"
echo "[$(date +%H:%M:%S)] GRPO finished. log=$TRAIN_LOG" | tee -a "$LOG"
