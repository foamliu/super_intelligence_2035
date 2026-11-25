#!/usr/bin/env bash
# baize_posttrain_r3_ppo2_launch.sh — R3 GRPO launcher (R2 config + --ppo-epochs 2).
#
# 为什么需要 R3（wake504 诊断，GPU-free，落盘证据）：
#   R2（rl_surrogate_runs/minicpm5_grpo_loop_R2_sandbox_200step/metrics.jsonl）
#   全 200 步 mean_ratio==1.000（min=max=1.0，唯一值=1.0），其中 110 步有真实非零
#   reward 仍 ratio==1.0 → PPO clip 全程失效（torch.clamp 对已=1.0 的 ratio 是 no-op）
#   → PPO 退化为 ratio≡1 的 vanilla policy-gradient（无 trust region），与 reward
#   在 step100 后平台/回落（seg 51-100=0.1114 → 151-200=0.0895）吻合。
#
#   根因 = ppo_epochs=1：唯一 epoch 里 new_logp（带 grad、未更新策略）== old_logp
#   （冻结、更新前）→ ratio≡1 → clip 不生效。old_logp 已正确冻结（loop.py L372-374
#   no_grad 计算一次，epoch 循环内不重算），故 R3 修复 = 仅 ppo_epochs=2：第 2 epoch
#   在已更新策略上重算 new_logp → ratio≠1 → clip 生效，恢复 PPO trust region。
#
#   内存：epoch 顺序执行、张量形状相同 → 峰值显存不增；R2 实测 --batch-prompts 1
#   --group-size 8（cheat_rate.json total_rollouts=1600=200×8）无 OOM，R3 沿用。
#   仅每步 wall time 约 +1 个 loss pass（generation+sandbox 不变）。
#
#   对应用户令#4 / 决策门 §R425 C：R2 负结果 → 「修 ppo_epochs≥2 + old_logp 冻结
#   使 clip 生效再跑一轮」。old_logp 冻结已满足，本脚本仅加 --ppo-epochs 2。
#
# 用法：
#   bash baize_posttrain_r3_ppo2_launch.sh --dry-run     # 只打印命令，不加载模型/不占GPU
#   bash baize_posttrain_r3_ppo2_launch.sh --status      # 看 GPU7/serve/R2-eval-chain 占用
#   bash baize_posttrain_r3_ppo2_launch.sh               # 真正起跑（需 GPU7 空闲 + serve 槽空）
#
# ⚠️ 本脚本默认行为是 --dry-run 之外的「真正起跑」会先做占用检查；R2 5-run eval
#    chain（PID 2322797, GPU7:8095）仍在跑时拒绝起跑，避免争资源/杀健康 eval。
set -uo pipefail

SCRIPT_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"
VENV_PY="${VENV_PY:-$HOME/code/verl_cu124_venv/bin/python}"
GPU="${GPU:-7}"
SFT_CKPT="${SFT_CKPT:-$SCRIPT_DIR/sft_surrogate_runs/minicpm5_agentic_v39_pretok/global_step_105}"
R3_OUTDIR="${R3_OUTDIR:-$SCRIPT_DIR/rl_surrogate_runs/minicpm5_grpo_loop_R3_sandbox_200step_ppo2}"
R3_LOG="${R3_LOG:-/tmp/grpo_loop_R3_sandbox_200step_ppo2.log}"
GRPO_LOOP="$SCRIPT_DIR/baize_posttrain_rl_grpo_loop.py"

DRY_RUN=0
STATUS_ONLY=0
for a in "$@"; do
  case "$a" in
    --dry-run) DRY_RUN=1 ;;
    --status)  STATUS_ONLY=1 ;;
  esac
done

# ---- in-container network hardening (R-launch-fix4, kept; harmless for 1 proc) ----
export NCCL_SOCKET_IFNAME="${NCCL_SOCKET_IFNAME:-bond0}"
export GLOO_SOCKET_IFNAME="${GLOO_SOCKET_IFNAME:-bond0}"
export NCCL_IB_DISABLE="${NCCL_IB_DISABLE:-1}"
export NCCL_NET="${NCCL_NET:-Socket}"
export HF_HUB_OFFLINE="${HF_HUB_OFFLINE:-1}"
export TRANSFORMERS_OFFLINE="${TRANSFORMERS_OFFLINE:-1}"
export TOKENIZERS_PARALLELISM=false
# R2 OOM mitigation (wake429)：A40 44GB 对 2B 全参 GRPO 预算紧，必须带此 env。
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"

gpu_busy() {  # echo 1 if GPU $1 has any compute process
  local g="$1" n
  n=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits -i "$g" 2>/dev/null | grep -c '[0-9]')
  echo "${n:-0}"
}
serve_alive() {  # echo 1 if something answers on :8095
  curl -s --max-time 3 "http://127.0.0.1:8095/v1/models" >/dev/null 2>&1 && echo 1 || echo 0
}
r2_eval_chain_alive() {  # echo 1 if R2 5-run eval chain still running
  pgrep -f 'baize_posttrain_rl_eval_chain.sh' >/dev/null 2>&1 && echo 1 || echo 0
}

if [ "$STATUS_ONLY" = 1 ]; then
  echo "[r3-status] GPU${GPU} compute-apps count: $(gpu_busy "$GPU")"
  echo "[r3-status] :8095 serve alive: $(serve_alive)"
  echo "[r3-status] R2 eval chain alive: $(r2_eval_chain_alive)"
  echo "[r3-status] R3 outdir: $R3_OUTDIR"
  echo "[r3-status] R3 log:    $R3_LOG"
  echo "[r3-status] sft-ckpt:  $SFT_CKPT"
  exit 0
fi

CMD=( "$VENV_PY" "$GRPO_LOOP"
  --reward-arm R2 --sandbox-exec
  --sandbox-ports 8664,8665,8653,8669 --sandbox-timeout 60
  --sft-ckpt "$SFT_CKPT"
  --total-steps 200 --group-size 8 --batch-prompts 1 --save-freq 50
  --lr 3e-6 --kl-coef 0.02
  --ppo-epochs 2
  --output-dir "$R3_OUTDIR" )

echo "[r3] recipe (R2 config + --ppo-epochs 2):"
printf '  CUDA_VISIBLE_DEVICES=%s ' "$GPU"; printf ' %q' "${CMD[@]}"; echo
echo "[r3]   env PYTORCH_CUDA_ALLOC_CONF=$PYTORCH_CUDA_ALLOC_CONF"
echo "[r3]   outdir=$R3_OUTDIR"
echo "[r3]   log=$R3_LOG"

if [ "$DRY_RUN" = 1 ]; then
  echo "[r3] --dry-run: 仅打印命令，不加载模型、不占 GPU。"
  exit 0
fi

# ---- 真正起跑前的占用护栏：不杀健康 eval，不争 serve 槽 ----
if [ "$(r2_eval_chain_alive)" = 1 ]; then
  echo "[r3] FATAL: R2 5-run eval chain 仍在运行（pgrep baize_posttrain_rl_eval_chain.sh 命中）。"
  echo "[r3]        R3 不得与 R2 eval 争 GPU7/serve。待 R2 5-run 完成后再起跑。"
  exit 2
fi
if [ "$(serve_alive)" = 1 ]; then
  echo "[r3] FATAL: :8095 仍有 serve 响应（R2 eval serve 未拆）。R3 训练前需先拆该 serve。"
  exit 2
fi
if [ "$(gpu_busy "$GPU")" != 0 ]; then
  echo "[r3] FATAL: GPU${GPU} 仍有 compute 进程占用。R3 训练需 GPU${GPU} 空闲。"
  exit 2
fi

mkdir -p "$R3_OUTDIR"
cd "$SCRIPT_DIR"
echo "[r3] === Launching R3 GRPO ppo_epochs=2 @ $(date '+%F %T') ==="
CUDA_VISIBLE_DEVICES="$GPU" nohup "${CMD[@]}" > "$R3_LOG" 2>&1 &
R3_PID=$!
echo "[r3] R3 GRPO launched: PID=$R3_PID at $(date '+%F %T')"
echo "[r3] Monitor: tail -f $R3_LOG"
echo "[r3] Dynamics will land: $R3_OUTDIR/*training_dynamics.json + cheat_rate.json"
echo "[r3] 预期：epoch2 ratio≠1.0（clip 生效）；若仍 ratio≡1 则需进一步排查 old_logp 冻结。"
