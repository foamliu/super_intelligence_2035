#!/usr/bin/env bash
# baize_posttrain_rl_grpo_surrogate.sh — Phase 3 surrogate RL/GRPO launch (verl 0.4.0)
#
# Purpose: End-to-end RLVR+GRPO validation on MiniCPM5-2B (2B, Llama-arch,
#          Apache 2.0) as a BaiZe surrogate, starting from the Phase 2 SFT
#          surrogate checkpoint. Validates the RL recipe (GRPO + 4 reward
#          arms R1-R4 + 6 lifecycle hooks + anti-cheat) before BaiZe ckpt.
#
# Framework: verl 0.4.0 GRPO (verl.trainer.main_ppo) via baize_posttrain_verl_wrapper.py
#   (R21: in-process MiniCPM5 XML tool-call parser registered in the SAME process
#    as verl training, so multi-turn RL does not silently fail).
#   Config: baize_posttrain_rl_verl_config_v2.yaml (R47: fixes 5 critical bugs).
#   Reward: baize_posttrain_reward_functions.py compute_score, arms R0-R4.
#   Hooks:  baize_posttrain_hooks.py (R144) + hooks_config.yaml (R145):
#             1) resilience 2) curriculum 3) rollout_scheduler
#             4) kl_scheduler 5) anti_cheat 6) early_stop
#
# GPU: 4xA40 (indices 4,5,6,7 default) per 2026-11-10 13:40 order "GPU4-7 全部投入".
#   Per 17:10 order GPU5-7 hold vLLM serve until sandbox restored — GPU-busy
#   guard prevents launching on occupied GPUs (does NOT kill any serve process).
#
# Sandbox: RL reward arms R1-R4 require EDA sandbox (10.129.32.75:8667) to turn
#   correctness into verifiable reward. R0 = skeleton (static, no sandbox).
#   --sandbox-check tests connectivity; if sandbox DOWN only R0 allowed (R22 auto_fallback).
#
# Red lines:
#   §5.1 contam — RL tasks (rl_pyaether_synth_v2.parquet, 3347 synthetic) must
#       NOT overlap 158 eval tasks. --contam-check runs gate before launch.
#   §5.2 anti-cheat — PreToolUse hook + cheat-rate report on every accuracy number.
#   Report MUST label results "替身预演，收益不可迁移到 BaiZe".
#
# Usage:
#   bash baize_posttrain_rl_grpo_surrogate.sh --dry-run
#   bash baize_posttrain_rl_grpo_surrogate.sh --sandbox-check
#   bash baize_posttrain_rl_grpo_surrogate.sh --contam-check
#   bash baize_posttrain_rl_grpo_surrogate.sh --smoke
#   bash baize_posttrain_rl_grpo_surrogate.sh --reward-arm R2
#   SFT_CKPT=/path/to/step_X bash baize_posttrain_rl_grpo_surrogate.sh --reward-arm R4
#   GPUS="4,5,6,7" bash baize_posttrain_rl_grpo_surrogate.sh --reward-arm R2
set -uo pipefail

SCRIPT_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"

# ============ paths ============
VERL_PY="$HOME/code/verl_cu124_venv/bin/python"
VERL_TORCHRUN="$HOME/code/verl_cu124_venv/bin/torchrun"
BASE_MODEL="/nas_data/app.e0031982/models/MiniCPM5-2B"
CONFIG_FILE="$SCRIPT_DIR/baize_posttrain_rl_verl_config_v2_merged.yaml"
RL_DATA="$SCRIPT_DIR/rl_pyaether_synth_v2.parquet"
HOOKS_CONFIG="$SCRIPT_DIR/baize_posttrain_hooks_config.yaml"
# R337 (2026-11-12): sandbox now reachable via SSH tunnel (dual-nix-tunnel port 3333
#   → 10.251.36.15 → 10.129.32.75). .17 localhost:8664 is forwarded to sandbox.
#   8667 is dead on sandbox; 8664 is the alive port (per eda_fastmcp .env R325).
#   Old direct path 10.129.32.75:8667 was unreachable for 42 wakes (cross-subnet ACL).
SANDBOX_HOST="${SANDBOX_HOST:-127.0.0.1}"
SANDBOX_PORT="${SANDBOX_PORT_HTTP:-8664}"
OUTPUT_DIR="$SCRIPT_DIR/rl_surrogate_runs/minicpm5_grpo_v1"
LOG_FILE="/tmp/baize_posttrain_rl_grpo_surrogate.log"

# ============ SFT ckpt auto-detect (Phase 2 output) ============
SFT_RUNS_DIR="$SCRIPT_DIR/sft_surrogate_runs"
detect_sft_ckpt() {
  # Sort by step number extracted from basename; exclude _smoke dirs (prefer full runs).
  # FIX R173: old `sort -t_ -k3 -n` mis-parsed paths with multiple '_' delimiters,
  # picking smoke global_step_5 over full-run global_step_72.
  find "$SFT_RUNS_DIR" -type d -name 'global_step_*' ! -path '*_smoke*' 2>/dev/null | \
    while IFS= read -r d; do
      step=$(basename "$d" | sed 's/global_step_//')
      printf '%s\t%s\n' "$step" "$d"
    done | sort -t$'\t' -k1,1n | tail -1 | cut -f2
}
SFT_CKPT="${SFT_CKPT:-$(detect_sft_ckpt)}"

# ============ GPU config ============
GPUS="${GPUS:-4,5,6,7}"
NGPU=$(echo "$GPUS" | tr ',' '\n' | wc -l)

# ============ training hyperparams (R47 v2 defaults + research tuning) ============
REWARD_ARM=R0          # START R0 (skeleton, no sandbox); switch R1-R4 when sandbox up
GROUP_SIZE=8           # R140: G=8 optimal for 2B on A40
TOTAL_STEPS=3000       # 13:40 order: ~3000 steps, ~2-3 days @ 666 R/hr
SAVE_FREQ=100
KL_COEF=0.02           # R132: KL control, low_var_kl
CLIP_RATIO=0.2
LR=3.0e-6              # R47 config default
TEMPERATURE=0.7
SEED=42
HOOKS=1
RESUME_CKPT=""

# ============ mode switches ============
DRY_RUN=0; SMOKE=0; SANDBOX_CHECK=0; CONTAM_CHECK=0
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --smoke) SMOKE=1 ;;
    --sandbox-check) SANDBOX_CHECK=1 ;;
    --contam-check) CONTAM_CHECK=1 ;;
    --reward-arm) REWARD_ARM="$2"; shift ;;
    --sft-ckpt) SFT_CKPT="$2"; shift ;;
    --config) CONFIG_FILE="$2"; shift ;;
    --gpus) GPUS="$2"; shift; NGPU=$(echo "$GPUS" | tr ',' '\n' | wc -l) ;;
    --group-size) GROUP_SIZE="$2"; shift ;;
    --total-steps) TOTAL_STEPS="$2"; shift ;;
    --lr) LR="$2"; shift ;;
    --kl-coef) KL_COEF="$2"; shift ;;
    --no-hooks) HOOKS=0 ;;
    --resume-ckpt) RESUME_CKPT="$2"; shift ;;
    *) echo "unknown arg: $1" ;;
  esac
  shift
done

case "$REWARD_ARM" in R0|R1|R2|R3|R4) ;; *) echo "ERROR: --reward-arm must be R0/R1/R2/R3/R4"; exit 1;; esac

# ============ recipe print ============
print_recipe() {
  local mode
  mode=$([ $DRY_RUN = 1 ] && echo DRY-RUN || ([ $SMOKE = 1 ] && echo SMOKE || echo TRAIN))
  cat <<EOF
===== BaiZe Phase 3 Surrogate RL/GRPO — RECIPE @ $(date '+%F %T') =====
  mode            : $mode
  surrogate note  : 替身预演，收益不可迁移到 BaiZe (MiniCPM5-2B Llama-arch != BaiZe Mamba2)
  base model      : $BASE_MODEL (MiniCPM5-2B, 2B, LlamaForCausalLM)
  sft ckpt        : ${SFT_CKPT:-(none — use base model; run Phase 2 SFT first)}
  framework       : verl 0.4.0 GRPO via baize_posttrain_verl_wrapper.py (R21 in-process parser)
  config          : $CONFIG_FILE (R47 v2)
  rl data         : $RL_DATA (3347 synthetic API-derived tasks, NOT 158 eval)
  reward arm      : $REWARD_ARM
    R0=skeleton(no sandbox) | R1=binary | R2=exec+assertion_ratio | R3=R2+tool_penalty | R4=R3+api_legality
  hooks (R143/R144/R145) : $([ $HOOKS = 1 ] && echo "ENABLED (6 hooks)" || echo DISABLED)
  hooks config    : $HOOKS_CONFIG
  gpu             : $GPUS ($NGPU xA40, FSDP)
  group_size (G)  : $GROUP_SIZE  (R140)
  total_steps     : $TOTAL_STEPS  (13:40 order: ~3000 steps, ~2-3 days)
  kl_coef         : $KL_COEF  (R132 low_var_kl)
  clip_ratio      : $CLIP_RATIO
  lr              : $LR
  temperature     : $TEMPERATURE
  sandbox         : $SANDBOX_HOST:$SANDBOX_PORT (R1-R4 require sandbox; R0 does not)
  output_dir      : $OUTPUT_DIR
  red lines       : §5.1 contam gate | §5.2 anti-cheat + cheat-rate report | surrogate label
===== END RECIPE =====
EOF
}
# ============ sandbox connectivity check ============
check_sandbox() {
  echo "[sandbox] checking $SANDBOX_HOST:$SANDBOX_PORT ..."
  if timeout 8 bash -c "cat < /dev/null > /dev/tcp/$SANDBOX_HOST/$SANDBOX_PORT" 2>/dev/null; then
    echo "[sandbox] OK TCP $SANDBOX_PORT OPEN"
    return 0
  else
    echo "[sandbox] FAIL TCP $SANDBOX_PORT unreachable (exit=$?)"
    echo "[sandbox]    RL reward arms R1-R4 BLOCKED. Only R0 (skeleton) allowed."
    echo "[sandbox]    Sandbox down 29+ consecutive wakes (host-level firewall)."
    return 1
  fi
}

# ============ contamination gate ============
run_contam_gate() {
  echo "[contam] running contamination gate on RL training data ..."
  bash "$SCRIPT_DIR/baize_posttrain_contamination_gate.sh" 2>&1 | tail -15
  local rc=${PIPESTATUS[0]}
  if [ "$rc" -ne 0 ]; then
    echo "[contam] FAIL contamination gate (rc=$rc) — RL launch ABORTED (red-line §5.1)"
    return 1
  fi
  echo "[contam] PASS contamination gate — RL data isolated from 158 eval"
  return 0
}

# ============ dependency checks ============
check_deps() {
  local missing=0
  for f in "$VERL_PY" "$VERL_TORCHRUN" "$BASE_MODEL" "$CONFIG_FILE" "$RL_DATA" "$HOOKS_CONFIG" \
           "$SCRIPT_DIR/baize_posttrain_verl_wrapper.py" "$SCRIPT_DIR/baize_posttrain_reward_functions.py" \
           "$SCRIPT_DIR/baize_posttrain_hooks.py" "$SCRIPT_DIR/baize_posttrain_minicpm5_parser.py"; do
    [ -e "$f" ] || { echo "ERROR: missing $f"; missing=1; }
  done
  "$VERL_PY" -c "from verl.trainer import main_ppo; print('[deps] verl main_ppo OK')" 2>/dev/null || {
    echo "ERROR: verl main_ppo import failed"; missing=1; }
  "$VERL_PY" -c "import pyarrow.parquet as pq; t=pq.read_table('$RL_DATA'); assert t.num_rows>0; print('[deps] RL data', t.num_rows, 'rows OK')" 2>/dev/null || {
    echo "ERROR: cannot read RL parquet $RL_DATA"; missing=1; }
  return $missing
}

# ============ sandbox-check mode ============
if [ $SANDBOX_CHECK = 1 ]; then
  echo "===== BaiZe Surrogate RL — SANDBOX CHECK @ $(date '+%F %T') ====="
  check_sandbox
  echo "===== END SANDBOX CHECK ====="
  exit $?
fi

# ============ contam-check mode ============
if [ $CONTAM_CHECK = 1 ]; then
  echo "===== BaiZe Surrogate RL — CONTAMINATION GATE @ $(date '+%F %T') ====="
  run_contam_gate
  exit $?
fi


# ============ dry-run ============
if [ $DRY_RUN = 1 ]; then
  print_recipe
  echo ""
  echo "--- dependency check ---"
  check_deps && echo "[dry-run] deps OK" || echo "[dry-run] FAIL deps missing"
  echo ""
  echo "--- sandbox check ---"
  check_sandbox
  echo ""
  echo "--- contamination gate ---"
  run_contam_gate
  echo ""
  if [ -z "$SFT_CKPT" ]; then
    echo "[dry-run] WARN No SFT ckpt under $SFT_RUNS_DIR — will use base model."
    echo "          Run Phase 2 (baize_posttrain_sft_surrogate.sh) first for full Phase 3."
  else
    echo "[dry-run] OK SFT ckpt detected: $SFT_CKPT"
  fi
  echo ""
  echo "[dry-run] Recipe + deps + sandbox + contam verified. No training launched."
  exit 0
fi

# ============ pre-launch checks ============
echo "===== BaiZe Phase 3 Surrogate RL/GRPO — PRELAUNCH @ $(date '+%F %T') ====="
print_recipe
echo ""
check_deps || { echo "ERROR: dependency check failed"; exit 1; }

# Sandbox requirement per reward arm
if [ "$REWARD_ARM" != "R0" ]; then
  check_sandbox || {
    echo "ERROR: reward arm $REWARD_ARM requires sandbox but unreachable."
    echo "       Restore sandbox, or use --reward-arm R0 for pipeline validation."
    exit 1; }
else
  echo "[sandbox] R0 (skeleton) selected — sandbox not required."
fi

# Contamination gate (red-line §5.1)
run_contam_gate || exit 1

# SFT ckpt selection
RESUME_MODEL="$BASE_MODEL"
if [ -n "$SFT_CKPT" ] && [ -d "$SFT_CKPT" ]; then
  RESUME_MODEL="$SFT_CKPT"
  echo "[ckpt] Using SFT surrogate ckpt: $SFT_CKPT"
elif [ -n "$RESUME_CKPT" ] && [ -d "$RESUME_CKPT" ]; then
  RESUME_MODEL="$RESUME_CKPT"
  echo "[ckpt] Using resume ckpt (crash recovery): $RESUME_CKPT"
else
  echo "[ckpt] WARN No SFT ckpt — using base model $BASE_MODEL (R0 pipeline validation only)."
fi

# GPU busy guard (respect 17:10 serve — do NOT kill)
echo "[guard] checking GPU $GPUS are free..."
GPU_LIST=$(echo "$GPUS" | tr ',' ' ')
BUSY=""
for gi in $GPU_LIST; do
  used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i "$gi" 2>/dev/null | tr -d ' ')
  if [ "${used:-0}" -gt 1000 ]; then BUSY="$BUSY $gi(${used}MiB)"; fi
done
if [ -n "$BUSY" ]; then
  echo "ERROR: GPU$BUSY occupied (used > 1GB)."
  echo "       Per 17:10 order GPU5-7 may hold vLLM serve (do NOT kill)."
  echo "       Wait for sandbox restore + stop serve, then re-run. Or GPUS=\"<free>\" bash $0"
  exit 1
fi
echo "[guard] GPU $GPUS all free OK"

# Smoke override
if [ $SMOKE = 1 ]; then
  TOTAL_STEPS=10; GROUP_SIZE=4; SAVE_FREQ=5; OUTPUT_DIR="${OUTPUT_DIR}_smoke"
  echo "[smoke] steps=10 group=4 save_freq=5 output=$OUTPUT_DIR"
fi

# ============ launch verl GRPO via wrapper ============
mkdir -p "$OUTPUT_DIR"
export CUDA_VISIBLE_DEVICES="$GPUS"
export HF_HOME="/tmp/hf_home"
export HF_MODULES_CACHE="/tmp/hf_home/modules"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export TORCH_NCCL_ASYNC_ERROR_HANDLING=1
export TOKENIZERS_PARALLELISM=true
export WANDB_MODE=disabled
export SANDBOX_HOST="$SANDBOX_HOST"
export SANDBOX_PORT_HTTP="$SANDBOX_PORT"

HOOKS_FLAG=""
if [ $HOOKS = 1 ]; then HOOKS_FLAG="+trainer.hooks_config_path=$HOOKS_CONFIG"; fi

# R-launch-fix (2026-11-13): Load the project config (v2/v3) as the Hydra PRIMARY
# config instead of verl's built-in `ppo_trainer.yaml`. The built-in default lacks
# structured keys (e.g. custom_reward_function.reward_kwargs) so Hydra struct-mode
# rejects CLI overrides like `custom_reward_function.reward_kwargs.arm=R0`. The
# project configs are complete standalone configs (no `defaults:` list), so they can
# serve as the primary config directly. CONFIG_FILE was previously set but never
# passed to verl — this feeds it via --config-path/--config-name.
# R-launch-fix2 (wake410): Hydra resolves a RELATIVE --config-path against the
# @hydra.main decorator's package dir (verl.trainer), NOT the CWD — so a relative
# CFG_DIR="." makes the primary config unfindable ("Cannot find primary config").
# Force an ABSOLUTE path so the project config (with sdpa / hybrid_engine / etc.)
# is actually loaded. Without this, verl silently falls back to its built-in
# ppo_trainer.yaml (flash_attention_2 → crashes on CPU meta tensor during FSDP
# init → colocated worker exits silently → looks like a "register-center hang").
CFG_DIR="$(cd "$(dirname "$CONFIG_FILE")" && pwd)"
CFG_NAME="$(basename "$CONFIG_FILE" .yaml)"

echo ""
echo "===== Surrogate RL/GRPO START @ $(date '+%F %T') reward=$REWARD_ARM =====" | tee "$LOG_FILE"
echo "[rl] verl entry: $VERL_TORCHRUN -m verl.trainer.main_ppo (via verl_wrapper, R21 parser)" | tee -a "$LOG_FILE"
echo "[rl] config: $CONFIG_FILE" | tee -a "$LOG_FILE"
echo "[rl] resume: $RESUME_MODEL" | tee -a "$LOG_FILE"
echo "[rl] output: $OUTPUT_DIR" | tee -a "$LOG_FILE"

"$VERL_TORCHRUN" --nproc_per_node="$NGPU" --master_addr=127.0.0.1 --master_port=29831 \
  "$SCRIPT_DIR/baize_posttrain_verl_wrapper.py" \
  --config-path "$CFG_DIR" --config-name "$CFG_NAME" \
  data.train_files="$RL_DATA" \
  data.val_files="$RL_DATA" \
  custom_reward_function.path="$SCRIPT_DIR/baize_posttrain_reward_functions.py" \
  custom_reward_function.name=compute_score \
  custom_reward_function.reward_kwargs.arm="$REWARD_ARM" \
  custom_reward_function.reward_kwargs.api_database="$HOME/code/eda_fastmcp/docs/API_INFO_MERGED_V3.json" \
  custom_reward_function.reward_kwargs.auto_fallback=true \
  actor_rollout_ref.model.path="$RESUME_MODEL" \
  actor_rollout_ref.rollout.n="$GROUP_SIZE" \
  actor_rollout_ref.actor.kl_loss_coef="$KL_COEF" \
  actor_rollout_ref.actor.clip_ratio="$CLIP_RATIO" \
  actor_rollout_ref.actor.optim.lr="$LR" \
  actor_rollout_ref.rollout.temperature="$TEMPERATURE" \
  algorithm.adv_estimator=grpo \
  trainer.total_training_steps="$TOTAL_STEPS" \
  trainer.save_freq="$SAVE_FREQ" \
  trainer.n_gpus_per_node="$NGPU" \
  trainer.nnodes=1 \
  trainer.project_name=baize_posttrain_rl_surrogate \
  trainer.experiment_name=minicpm5_grpo_v1 \
  trainer.default_local_dir="$OUTPUT_DIR" \
  +trainer.seed="$SEED" \
  $HOOKS_FLAG \
  2>&1 | tee -a "$LOG_FILE"

RC=${PIPESTATUS[0]}
echo "  rc=$RC" | tee -a "$LOG_FILE"
echo "===== Surrogate RL/GRPO END @ $(date '+%F %T') rc=$RC =====" | tee -a "$LOG_FILE"

# ============ post-training: cheat rate report (red-line §5.2) ============
CHEAT_JSON="$OUTPUT_DIR/cheat_rate.json"
echo "===== POST-TRAINING @ $(date '+%F %T') =====" | tee -a "$LOG_FILE"
"$VERL_PY" -c "
import sys; sys.path.insert(0, '$SCRIPT_DIR')
from baize_posttrain_reward_functions import save_cheat_rate_report
save_cheat_rate_report('$CHEAT_JSON')
" 2>/dev/null && { echo "[post] cheat rate report:"; cat "$CHEAT_JSON" 2>/dev/null; } \
  || echo "[post] cheat rate: not available (no rollouts completed or skeleton mode)" | tee -a "$LOG_FILE"

# Checkpoints
if [ -d "$OUTPUT_DIR" ]; then
  LATEST_CKPT=$(find "$OUTPUT_DIR" -type d -name 'global_step_*' 2>/dev/null | sort -t_ -k3 -n | tail -1)
  [ -n "$LATEST_CKPT" ] && echo "[post] latest ckpt: $LATEST_CKPT" | tee -a "$LOG_FILE" \
    && echo "[post] resume: bash $0 --reward-arm $REWARD_ARM --resume-ckpt $LATEST_CKPT" | tee -a "$LOG_FILE"
fi

if [ $RC -eq 0 ]; then
  echo ""
  echo "RL complete. Next: serve RL ckpt with vLLM, run EDA-Eval (baize_posttrain_eval.sh)."
  echo "  WARN Report results as: 替身预演，收益不可迁移到 BaiZe"
  echo "  WARN Every accuracy number MUST pair with cheat rate (red-line §5.2)."
fi
exit $RC

