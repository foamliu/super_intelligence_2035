#!/usr/bin/env bash
# baize_posttrain_rl_grpo.sh — BaiZe Stage(ii) 步骤 2：RLVR + GRPO 配方骨架（4 臂奖励 R1–R4）
#
# 用途：从 SFT ckpt 起，用执行沙盒把正确性转为可验证奖励，以 GRPO（无价值网络、组相对策略优化）优化。
#       论文 §5.3 + Table\ref{tab:reward}：
#         R1 = 二值 pass/fail
#         R2 = 可执行 + 断言通过率（部分分，缓解 pass/fail 稀疏）
#         R3 = R2 + 工具调用惩罚（与 harness 成本模型对齐）
#         R4 = R3 + API 合法性项（惩罚虚构符号）
# 机器：10.252.32.17（post-train 线；需 GPU + 沙盒并发）。
#
# ⚠️ Reward hacking 是最大风险：
#   - anti-cheat：harness 的 PreToolUse hook 全程逐字节一致启用；BaiZe RL 挂同一套 anti-cheat。
#   - 每个准确率数字旁必须报告 cheat rate。
#   - 预算口径：带沙盒执行时是「沙盒时延 bound」，按「沙盒并发数 × 墙钟」规划，不沿用 GPU-hour。
#
# 红线：RL 训练任务必须与 EDA-Eval-PyAether 158 评测任务隔离（污染隔离 §5.1）——
#       RL 用「同分布合成任务」或「API 文档派生任务」，绝不用 158 评测题。
#
# 用法：
#   bash baize_posttrain_rl_grpo.sh --dry-run                    # 默认 R1
#   bash baize_posttrain_rl_grpo.sh --dry-run --reward-arm R4 --sandbox-concurrency 16
#   RESUME_DIR=<sft_ckpt> bash baize_posttrain_rl_grpo.sh --reward-arm R3
#
# ⚠️ 配方骨架：训练入口 grpo_train.py + 奖励计算 reward_compute.py 为占位（待确认 verl/OpenRLHF/自研）。
set -uo pipefail

BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
DATA="$BASE/data"
RUN_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
OUTPUT_DIR="$BASE/nemo_experiments/baize_posttrain_rl_grpo"
RESUME_DIR="${RESUME_DIR:-$BASE/nemo_experiments/baize_posttrain_sft/step_final}"

REWARD_ARM=R1
SANDBOX_CONCURRENCY=8
GROUP_SIZE=16
NP=8; INFERENCE_GPU=0; PORT=29822; VLLM_PORT=8000; NAME="posttrain_rl_grpo"
ITERS=2000; LR=1e-6; SAVE_INTERVAL=200; KL_COEF=0.04
MAX_TURNS=3; TASK_TIMEOUT=2500

RL_TASKS="${DATA}/rl_pyaether_synth_tasks.jsonl"   # ⚠️ 合成任务，绝不用 158 评测题
TOKENIZER="$DATA/tokenizer_eod"

DRY_RUN=0; SMOKE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;; --smoke) SMOKE=1 ;;
    --reward-arm) REWARD_ARM="$2"; shift ;;
    --sandbox-concurrency) SANDBOX_CONCURRENCY="$2"; shift ;;
    --group-size) GROUP_SIZE="$2"; shift ;;
    --resume) RESUME_DIR="$2"; shift ;;
    *) echo "未知参数: $1" ;;
  esac
  shift
done

case "$REWARD_ARM" in R1|R2|R3|R4) ;; *) echo "❌ --reward-arm 必须是 R1/R2/R3/R4"; exit 1;; esac

cat <<EOF
===== BaiZe Stage(ii) RLVR+GRPO — RECIPE @ $(date '+%F %T') =====
  mode              : $([ $DRY_RUN = 1 ] && echo DRY-RUN || ([ $SMOKE = 1 ] && echo SMOKE || echo TRAIN))
  resume_ckpt(sft)  : ${RESUME_DIR}
  output_dir        : ${OUTPUT_DIR}
  reward_arm        : ${REWARD_ARM}
    R1=binary | R2=exec+assertion_ratio | R3=R2+tool_call_penalty | R4=R3+API_legality
  group_size (GRPO) : ${GROUP_SIZE}
  sandbox_concurrency: ${SANDBOX_CONCURRENCY}   (预算口径 = 并发 × 墙钟，非 GPU-hour)
  max_turns         : ${MAX_TURNS}   (M3 多轮改进对齐)
  task_timeout      : ${TASK_TIMEOUT}s
  train GPU(NP)     : ${NP}   inference GPU : ${INFERENCE_GPU} (vLLM port ${VLLM_PORT})
  steps / LR        : ${ITERS} / ${LR}  (KL_coef=${KL_COEF})
  save_interval     : ${SAVE_INTERVAL}
  rl_tasks          : ${RL_TASKS}  (⚠️ 合成任务，与 158 评测隔离)
  anti-cheat        : PreToolUse hook 全程启用，逐字节一致；报告 cheat rate
  red line          : RL 任务 ≠ EDA-Eval-PyAether 158 题（污染隔离 §5.1）
  entrypoint        : grpo_train.py + reward_compute.py（占位，待确认 verl/OpenRLHF/自研）
===== END RECIPE =====
EOF

[ $DRY_RUN = 1 ] && { echo "[dry-run] 配方已打印，不执行训练。"; exit 0; }

cd "$RUN_DIR" || { echo "❌ RUN_DIR 不存在: $RUN_DIR"; exit 1; }
[ -d "$RESUME_DIR" ] || { echo "❌ SFT ckpt 不存在: $RESUME_DIR"; exit 1; }
[ -f "$RL_TASKS" ] || { echo "❌ RL 合成任务集不存在: $RL_TASKS（待 P2 合成，⚠️ 禁用 158 评测题）"; exit 1; }
GPU_BUSY=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader 2>/dev/null | awk -F', ' '{gsub(/[^0-9]/,"",$2); if($2+0>1000) print $1}')
[ -n "$GPU_BUSY" ] && { echo "❌ GPU $GPU_BUSY 非空，停手"; exit 1; }

[ $SMOKE = 1 ] && { ITERS=10; SAVE_INTERVAL=5; OUTPUT_DIR="${OUTPUT_DIR}_smoke"; SANDBOX_CONCURRENCY=2; GROUP_SIZE=4; }

export HF_HOME=/nas_train/app.e0031982/.cache
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export TORCH_NCCL_ASYNC_ERROR_HANDLING=1

echo "[rl] 启动推理服务 vLLM @ port ${VLLM_PORT} (model=${RESUME_DIR}) ..."
# TODO(框架确认): 以下 vLLM serve 占位；若用 SGLang 或 verl 内置推理引擎，替换此处。
# "$PY/vllm" serve "$RESUME_DIR" --port "$VLLM_PORT" --dtype bfloat16 \
#     --max-model-len 16384 --gpu-memory-utilization 0.4 > /tmp/baize_posttrain_rl_vllm.log 2>&1 &
# VLLM_PID=$!; sleep 60

LOG=/tmp/baize_posttrain_rl_train.log
echo "===== RL GRPO START @ $(date '+%F %T') reward=${REWARD_ARM} =====" | tee /tmp/baize_posttrain_rl.sum
"$PY/torchrun" --nnodes=1 --nproc_per_node="$NP" \
    --master_addr=127.0.0.1 --master_port="$PORT" \
    grpo_train.py \
    --arch mamba2 --name "$NAME" --dir "$BASE/nemo_experiments" \
    --tokenizer-path "$TOKENIZER" \
    --init-from-ckpt "$RESUME_DIR" \
    --rl-tasks "$RL_TASKS" \
    --reward-arm "$REWARD_ARM" \
    --reward-compute "$RUN_DIR/reward_compute.py" \
    --group-size "$GROUP_SIZE" \
    --sandbox-concurrency "$SANDBOX_CONCURRENCY" \
    --max-turns "$MAX_TURNS" --task-timeout "$TASK_TIMEOUT" \
    --inference-endpoint "http://127.0.0.1:${VLLM_PORT}/v1" \
    --train-iters "$ITERS" --lr "$LR" --kl-coef "$KL_COEF" \
    --save-interval "$SAVE_INTERVAL" --seed 1234 --precision bf16_mixed \
    --anti-cheat-hook enabled --report-cheat-rate > "$LOG" 2>&1
RC=$?
# [ -n "${VLLM_PID:-}" ] && kill "$VLLM_PID" 2>/dev/null
echo "  rc=${RC}" | tee -a /tmp/baize_posttrain_rl.sum
echo "===== RL GRPO END @ $(date '+%F %T') rc=${RC} =====" | tee -a /tmp/baize_posttrain_rl.sum
exit $RC
