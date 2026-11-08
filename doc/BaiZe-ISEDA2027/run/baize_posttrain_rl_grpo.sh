#!/usr/bin/env bash
# baize_posttrain_rl_grpo.sh — BaiZe Stage(ii) 步骤 2：RLVR + GRPO（verl 框架）
#
# 🔴 R12 UPDATE (2026-11-07): Complete rewrite from placeholder to verl entry point.
#   - Replaced placeholder grpo_train.py with `python -m verl.trainer.main_ppo`
#   - Uses baize_posttrain_rl_verl_config.yaml as config source
#   - Auto-detects /nas_data vs /nas_train (R12 path fix)
#   - SGLang backend (R8/R9: MiniCPM5-2B XML tool calls need SGLang parser)
#
# 用途：从 SFT ckpt（或 base model for surrogate）起，用执行沙盒把正确性转为可验证奖励，
#       以 GRPO（无价值网络、组相对策略优化）优化。
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
#   bash baize_posttrain_rl_grpo.sh --dry-run                    # 打印配方
#   bash baize_posttrain_rl_grpo.sh --dry-run --reward-arm R4    # R4 臂配方
#   bash baize_posttrain_rl_grpo.sh --smoke                      # smoke test (10 iters)
#   RESUME_DIR=/tmp/models/MiniCPM5-2B bash baize_posttrain_rl_grpo.sh --reward-arm R2  # 替身预演
set -uo pipefail

# === Auto-detect paths (R12: /nas_train empty on .17, use /nas_data) ===
SCRIPT_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"
source "$SCRIPT_DIR/baize_posttrain_paths.sh"

OUTPUT_DIR="${BAIZE_EXP_DIR}/baize_posttrain_rl_grpo"
CONFIG_FILE="$SCRIPT_DIR/baize_posttrain_rl_verl_config_v2.yaml"  # R47: v2 fixes 5 critical bugs
RESUME_DIR="${RESUME_DIR:-${BAIZE_MODEL_PATH}}"  # Default: MiniCPM5-2B for surrogate
REWARD_ARM=R0  # R47: default R0 (skeleton, no sandbox); switch to R2 when sandbox ready
NP=4  # 4×A40 on .17

DRY_RUN=0; SMOKE=0; GPU_IDS=""
RESUME_CKPT=""  # R22: verl checkpoint resume path (different from --resume which is model path)
MONITOR=1       # R22: enable monitoring hooks by default
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;; --smoke) SMOKE=1 ;;
    --reward-arm) REWARD_ARM="$2"; shift ;;
    --resume) RESUME_DIR="$2"; shift ;;
    --resume-ckpt) RESUME_CKPT="$2"; shift ;;  # R22: verl checkpoint dir for crash recovery
    --config) CONFIG_FILE="$2"; shift ;;
    --gpu-ids) GPU_IDS="$2"; shift ;;
    --no-monitor) MONITOR=0 ;;  # R22: disable monitoring
    *) echo "未知参数: $1" ;;
  esac
  shift
done

case "$REWARD_ARM" in R0|R1|R2|R3|R4) ;; *) echo "❌ --reward-arm 必须是 R0/R1/R2/R3/R4"; exit 1;; esac

cat <<EOF
===== BaiZe Stage(ii) RLVR+GRPO (verl) — RECIPE @ $(date '+%F %T') =====
  mode              : $([ $DRY_RUN = 1 ] && echo DRY-RUN || ([ $SMOKE = 1 ] && echo SMOKE || echo TRAIN))
  framework         : verl via baize_posttrain_verl_wrapper.py (R21: in-process parser)
  config            : ${CONFIG_FILE}
  resume_ckpt       : ${RESUME_DIR}
  output_dir        : ${OUTPUT_DIR}
  reward_arm        : ${REWARD_ARM}
    R1=binary | R2=exec+assertion_ratio | R3=R2+tool_call_penalty | R4=R3+API_legality
  inference backend : SGLang (R16: verl ToolParser handles XML tool calls, not SGLang)
  n_gpus            : ${NP} (4×A40 48GB)
  anti-cheat        : PreToolUse hook 全程启用，逐字节一致；报告 cheat rate
  red line          : RL 任务 ≠ EDA-Eval-PyAether 158 题（污染隔离 §5.1）
  warning           : 替身 RL 结果不可迁移到白泽（surrogate rehearsal only）
===== END RECIPE =====
EOF

[ $DRY_RUN = 1 ] && { echo "[dry-run] 配方已打印，不执行训练。"; exit 0; }

# === Pre-flight checks ===
[ -f "$CONFIG_FILE" ] || { echo "❌ verl 配置不存在: $CONFIG_FILE"; exit 1; }
[ -d "$RESUME_DIR" ] || { echo "❌ resume ckpt 不存在: $RESUME_DIR"; exit 1; }
[ -f "$BAIZE_VENV_PY" ] || { echo "❌ verl cu124 venv 未就绪: $BAIZE_VENV_PY（先跑 baize_posttrain_setup_cu124_venv.sh）"; exit 1; }

# Check RL parquet data
RL_PARQUET="$SCRIPT_DIR/rl_pyaether_synth_v2.parquet"
[ -f "$RL_PARQUET" ] || { echo "❌ RL parquet 不存在: $RL_PARQUET"; exit 1; }

# === GPU allocation (R21: support --gpu-ids for 4-of-8 allocation) ===
if [ -n "$GPU_IDS" ]; then
    export CUDA_VISIBLE_DEVICES="$GPU_IDS"
    echo "[rl] CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"
    NP=$(echo "$GPU_IDS" | tr ',' '\n' | wc -l)
else
    # Check GPU availability (all GPUs must be free if no explicit allocation)
    GPU_BUSY=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader 2>/dev/null | awk -F', ' '{gsub(/[^0-9]/,"",$2); if($2+0>1000) print $1}')
    [ -n "$GPU_BUSY" ] && { echo "❌ GPU $GPU_BUSY 非空（used>1GB），停手。用 --gpu-ids 0,1,2,3 指定GPU"; exit 1; }
fi

# === Environment ===
export HF_HOME="${NAS_ROOT}/app.e0031982/.cache"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export TORCH_NCCL_ASYNC_ERROR_HANDLING=1
export NCCL_TIMEOUT=1800
export OMP_NUM_THREADS=8

# === Build verl command ===
VERL_ARGS=(
    --config "$CONFIG_FILE"
    --actor_rollout_ref.model.path "$RESUME_DIR"
    --data.train_files "$RL_PARQUET"
    --reward.arm "$REWARD_ARM"
    --trainer.save_dir "$OUTPUT_DIR"
    --trainer.log_dir "${OUTPUT_DIR}/logs"
    --runtime.n_gpus "$NP"
)

# R22: Checkpoint resume — verl supports --trainer.resume_from_checkpoint
if [ -n "$RESUME_CKPT" ]; then
    if [ -d "$RESUME_CKPT" ]; then
        VERL_ARGS+=(--trainer.resume_from_checkpoint "$RESUME_CKPT")
        echo "[rl] R22: Resuming from checkpoint: $RESUME_CKPT"
    else
        echo "❌ --resume-ckpt 目录不存在: $RESUME_CKPT"; exit 1
    fi
fi

if [ $SMOKE = 1 ]; then
    VERL_ARGS+=(
        --trainer.total_epochs 1
        --trainer.save_interval 5
        --algorithm.group_size 4
        --actor_rollout_ref.rollout.max_num_seqs 4
        --data.train_batch_size 16
        --actor_rollout_ref.actor.ppo_mini_batch_size 8
    )
    OUTPUT_DIR="${OUTPUT_DIR}_smoke"
    VERL_ARGS+=(--trainer.save_dir "$OUTPUT_DIR")
    echo "[smoke] Reduced params: group_size=4, batch=16, iters=10"
fi

# === Launch verl GRPO training ===
LOG=/tmp/baize_posttrain_rl_train.log
echo "===== RL GRPO START @ $(date '+%F %T') reward=${REWARD_ARM} =====" | tee /tmp/baize_posttrain_rl.sum
echo "[rl] verl entry point: $BAIZE_VENV_PY -m verl.trainer.main_ppo"
echo "[rl] config: $CONFIG_FILE"
echo "[rl] resume: $RESUME_DIR"
echo "[rl] output: $OUTPUT_DIR"

cd "$SCRIPT_DIR" || { echo "❌ Cannot cd to $SCRIPT_DIR"; exit 1; }

# 🔴 R21 FIX (2026-11-07): Use wrapper script instead of separate process.
#   Previously, parser was imported in a throwaway `python -c` process — the
#   registration was lost when that process exited, and verl training started
#   WITHOUT the "minicpm5" parser registered → multi-turn RL would silently
#   fail. The wrapper imports the parser IN THE SAME PROCESS as verl training.
echo "[rl] Launching verl via wrapper (parser registered in-process, R21 fix)..."

"$BAIZE_VENV_PY" "$SCRIPT_DIR/baize_posttrain_verl_wrapper.py" "${VERL_ARGS[@]}" > "$LOG" 2>&1
RC=$?

echo "  rc=${RC}" | tee -a /tmp/baize_posttrain_rl.sum
echo "  log: $LOG" | tee -a /tmp/baize_posttrain_rl.sum
echo "===== RL GRPO END @ $(date '+%F %T') rc=${RC} =====" | tee -a /tmp/baize_posttrain_rl.sum

# === R22: Post-training monitoring ===
# List checkpoints for resume reference
echo "===== R22 POST-TRAINING MONITORING @ $(date '+%F %T') =====" | tee -a /tmp/baize_posttrain_rl.sum
if [ -d "${OUTPUT_DIR}" ]; then
    echo "[post] Checkpoints in ${OUTPUT_DIR}:" | tee -a /tmp/baize_posttrain_rl.sum
    find "${OUTPUT_DIR}" -name "*.pt" -o -name "*.safetensors" 2>/dev/null | head -20 | tee -a /tmp/baize_posttrain_rl.sum
    LATEST_CKPT=$(find "${OUTPUT_DIR}" -type d -name "global_step_*" 2>/dev/null | sort -t_ -k3 -n | tail -1)
    if [ -n "$LATEST_CKPT" ]; then
        echo "[post] Latest checkpoint: $LATEST_CKPT" | tee -a /tmp/baize_posttrain_rl.sum
        echo "[post] To resume: bash baize_posttrain_rl_grpo.sh --reward-arm ${REWARD_ARM} --gpu-ids ${GPU_IDS:-0,1,2,3} --resume-ckpt ${LATEST_CKPT}" | tee -a /tmp/baize_posttrain_rl.sum
    fi
fi

# R22: Save cheat rate report (red-line §5.2)
CHEAT_JSON="${OUTPUT_DIR}/cheat_rate.json"
if [ -f "$CHEAT_JSON" ]; then
    echo "[post] Cheat rate report:" | tee -a /tmp/baize_posttrain_rl.sum
    cat "$CHEAT_JSON" | tee -a /tmp/baize_posttrain_rl.sum
else
    # Try to generate it from the reward module
    "$BAIZE_VENV_PY" -c "
import sys; sys.path.insert(0, '$SCRIPT_DIR')
from baize_posttrain_reward_functions import save_cheat_rate_report
save_cheat_rate_report('$CHEAT_JSON')
" 2>/dev/null && {
        echo "[post] Cheat rate report (generated):" | tee -a /tmp/baize_posttrain_rl.sum
        cat "$CHEAT_JSON" 2>/dev/null | tee -a /tmp/baize_posttrain_rl.sum
    } || echo "[post] Cheat rate: not yet available (skeleton mode, no rollouts completed)" | tee -a /tmp/baize_posttrain_rl.sum
fi

# R22: Training health summary
echo "[post] Training health:" | tee -a /tmp/baize_posttrain_rl.sum
echo "  exit_code: $RC" | tee -a /tmp/baize_posttrain_rl.sum
echo "  log_file: $LOG" | tee -a /tmp/baize_posttrain_rl.sum
echo "  output_dir: $OUTPUT_DIR" | tee -a /tmp/baize_posttrain_rl.sum
if [ $RC -ne 0 ]; then
    echo "[post] ⚠️ Non-zero exit code — check $LOG for errors" | tee -a /tmp/baize_posttrain_rl.sum
    echo "[post] Last 20 lines of log:" | tee -a /tmp/baize_posttrain_rl.sum
    tail -20 "$LOG" 2>/dev/null | tee -a /tmp/baize_posttrain_rl.sum
fi
echo "===== R22 MONITORING END =====" | tee -a /tmp/baize_posttrain_rl.sum

exit $RC
