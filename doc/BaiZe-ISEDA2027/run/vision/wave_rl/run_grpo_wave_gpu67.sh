#!/usr/bin/env bash
# run_grpo_wave_gpu67.sh — Stage-2W GRPO launcher for .17 GPU 6-7 (用户令 2026-11-19).
#
# 背景：vision 线 2026-11-13 由 .12 迁到 .17（8×A40）。2026-11-19 用户令分配
#   GPU 4-5 → posttrain、GPU 6-7 → vision，要求把之前因 GPU 不足改用 CPU 的
#   波形 RL 训练（Stage-2W GRPO）迁回 GPU 训练。Qwen3.5-2B 是 2B 模型，2×A40 足够。
#
# 与 run_grpo_wave.sh 的区别：
#   * run_grpo_wave.sh 面向 .12/.29 的 /nas_train NFS，且内含「等 SFT 完成」长链。
#   * 本脚本面向 .17：用 /nas_data 路径 + CUDA_VISIBLE_DEVICES=6,7，**直接跑 GRPO**
#     （SFT Stage-1W 已在 .12 验收 PASS，这里不再重跑 SFT，只消费其 checkpoint）。
#
# ⚠️ 阻塞守卫（BLOCKED guard）：.17 上 /nas_train 不可用（→ /H100_train，无 app 数据），
#   且 .17↔.12/.29 SSH 超时，无法自取 SFT checkpoint。故本脚本在启动前**强制校验**
#   「2B text backbone」与「SFT checkpoint」在 .17 /nas_data 在位；缺任一项即打印
#   BLOCKED + 落盘方法后 **exit 0**（绝不空跑 / 绝不编造训练）。
#
# 解阻塞（二选一）：
#   A) 运维把 .12 /nas_train 的 Stage-1W 产物拷到 .17（推荐 = 迁移而非重跑）：
#        # 在 .12 上（或能同时访问两侧的机器）：
#        rsync -az /nas_train/app.e0031982/datasets/baize-vision/out/wave_sft_stage1w/ \
#          <staging>/wave_sft_stage1w/
#        # 在 .17 上落到：
#        /nas_data/app.e0031982/datasets/baize-vision/out/wave_sft_stage1w/
#      需含：qwen3vl_2b_text_extracted/（2B text backbone，HF Qwen3ForCausalLM）
#            eval_results.json（SFT 验收 PASS）
#            step{N}/adapter_config.json（SFT LoRA checkpoint）
#   B) 在 .17 上重生成（redo，非 migrate，需用户拍板）：
#        python wave_rl/extract_qwen3vl_2b_text.py   # 从本地 Qwen3.5-2B 抽 text backbone
#        bash wave_rl/run_sft_wave.sh 1              # 重跑 Stage-1W SFT（GPU 6-7）
#      ⚠️ Qwen3.5-2B（qwen3_5 架构）与原 extract 脚本预期的 Qwen3-VL-2B（qwen3_vl）
#         架构不同，extract 可能需适配；重跑 SFT 亦非「迁回」语义，先报后做。
#
# 用法（解阻塞后）：
#   setsid bash vision/wave_rl/run_grpo_wave_gpu67.sh > /tmp/grpo_wave_gpu67.log 2>&1 < /dev/null &
# 路径可用环境变量覆盖：SFT_OUT / GRPO_OUT / LLM_2B / N_GPUS / CUDA_VIS

set -euo pipefail

CUDA_VIS="${CUDA_VIS:-6,7}"
N_GPUS="${N_GPUS:-2}"
SFT_OUT="${SFT_OUT:-/nas_data/app.e0031982/datasets/baize-vision/out/wave_sft_stage1w}"
GRPO_OUT="${GRPO_OUT:-/nas_data/app.e0031982/datasets/baize-vision/out/wave_grpo_stage2w}"
LLM_2B="${LLM_2B:-$SFT_OUT/qwen3vl_2b_text_extracted}"
SFT_EVAL_JSON="$SFT_OUT/eval_results.json"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VISION_DIR="$(dirname "$SCRIPT_DIR")"
mkdir -p "$GRPO_OUT"
GUARD_LOG="$GRPO_OUT/gpu67_guard_$(date +%Y%m%d_%H%M%S).log"

exec 9>/tmp/run_grpo_wave_gpu67.lock
if ! flock -n 9; then
  echo "[$(date +%H:%M:%S)] Another run_grpo_wave_gpu67.sh holds the lock. Exiting." >&2
  exit 0
fi
# 注：lock 放 /tmp（本地盘）。/nas_data 是 NFS，flock 会报 "No locks available"。

{
  echo "=== Stage-2W GRPO .17 GPU6-7 launcher (用户令 2026-11-19) ==="
  echo "  CUDA_VISIBLE_DEVICES: $CUDA_VIS  (N_GPUS=$N_GPUS)"
  echo "  SFT_OUT : $SFT_OUT"
  echo "  GRPO_OUT: $GRPO_OUT"
  echo "  LLM_2B  : $LLM_2B"
  echo "  Started : $(date)"
} | tee "$GUARD_LOG"

# ── BLOCKED guard ──
BLOCK=0
[ -f "$SFT_EVAL_JSON" ]              || { echo "[BLOCKED] 缺 SFT 验收文件: $SFT_EVAL_JSON" | tee -a "$GUARD_LOG"; BLOCK=1; }
[ -d "$LLM_2B" ]                     || { echo "[BLOCKED] 缺 2B text backbone 目录: $LLM_2B" | tee -a "$GUARD_LOG"; BLOCK=1; }
SFT_STEP=$(find "$SFT_OUT" -maxdepth 2 -name adapter_config.json -path '*/step*' 2>/dev/null | sort -V | tail -1 || true)
[ -n "$SFT_STEP" ]                   || { echo "[BLOCKED] 缺 SFT LoRA checkpoint (step*/adapter_config.json) under $SFT_OUT" | tee -a "$GUARD_LOG"; BLOCK=1; }

if [ "$BLOCK" = "1" ]; then
  echo "" | tee -a "$GUARD_LOG"
  echo "[BLOCKED] Stage-2W GRPO 无法在 .17 GPU6-7 启动：SFT Stage-1W 产物未在 .17 /nas_data 在位。" | tee -a "$GUARD_LOG"
  echo "  根因：.17 /nas_train 不可用（→/H100_train 无 app 数据）；.17↔.12/.29 SSH 超时，agent 无法自取。" | tee -a "$GUARD_LOG"
  echo "  解法：见本脚本头部「解阻塞」A（运维拷贝，推荐）/ B（.17 重生成，需拍板）。" | tee -a "$GUARD_LOG"
  echo "  产物到位后重跑本脚本即自动启动 GRPO（不会空跑）。" | tee -a "$GUARD_LOG"
  echo "[EXIT 0] BLOCKED — 未启动训练，未编造结果。" | tee -a "$GUARD_LOG"
  exit 0
fi

SFT_CKPT_DIR="$(dirname "$SFT_STEP")"
echo "[OK] 前置校验通过：SFT ckpt=$SFT_CKPT_DIR  backbone=$LLM_2B  eval=$SFT_EVAL_JSON" | tee -a "$GUARD_LOG"

# ── 真正启动 GRPO（2B 模型，2×A40）──
cd "$VISION_DIR"
export CUDA_VISIBLE_DEVICES="$CUDA_VIS"
GRPO_LOG="$GRPO_OUT/grpo_train_$(date +%Y%m%d_%H%M%S).log"
echo "[launch] torchrun --nproc_per_node=$N_GPUS  log=$GRPO_LOG" | tee -a "$GUARD_LOG"
torchrun --nproc_per_node="$N_GPUS" wave_rl/grpo_train_wave.py \
  --sft_ckpt_dir "$SFT_OUT" \
  --model_path "$LLM_2B" \
  --output_dir "$GRPO_OUT" \
  --device auto \
  2>&1 | tee "$GRPO_LOG"
echo "[$(date +%H:%M:%S)] GRPO training finished. log=$GRPO_LOG" | tee -a "$GUARD_LOG"
