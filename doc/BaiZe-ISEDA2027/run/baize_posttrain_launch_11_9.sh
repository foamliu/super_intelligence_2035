#!/usr/bin/env bash
# baize_posttrain_launch_11_9.sh — Master launch orchestration for 11/9 GPU arrival
#
# R12 (2026-11-07): End-to-end launch sequence for surrogate RL rehearsal.
# Orchestrates: venv setup → preflight → SGLang serve → baseline eval →
#               trajectory collection → RL smoke test
#
# Usage:
#   bash baize_posttrain_launch_11_9.sh --dry-run          # Print full sequence
#   bash baize_posttrain_launch_11_9.sh --step 0           # Run only step 0
#   bash baize_posttrain_launch_11_9.sh --step 1-3         # Run steps 1 through 3
#   bash baize_posttrain_launch_11_9.sh                    # Run all steps
#   bash baize_posttrain_launch_11_9.sh --quick            # Quick mode (10 tasks, 1 run)
#
# ⚠️ Surrogate RL results are NOT transferable to BaiZe.
set -uo pipefail

SCRIPT_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"
source "$SCRIPT_DIR/baize_posttrain_paths.sh"

DRY_RUN=0
STEP_RANGE=""
QUICK=0
GPU_IDS=""

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --step) STEP_RANGE="$2"; shift ;;
    --quick) QUICK=1 ;;
    --gpu-ids) GPU_IDS="$2"; shift ;;
    *) echo "Unknown: $1" ;;
  esac
  shift
done

# Parse step range
if [ -z "$STEP_RANGE" ]; then
  STEP_START=0; STEP_END=6
elif echo "$STEP_RANGE" | grep -q '-'; then
  STEP_START=$(echo "$STEP_RANGE" | cut -d- -f1)
  STEP_END=$(echo "$STEP_RANGE" | cut -d- -f2)
else
  STEP_START=$STEP_RANGE; STEP_END=$STEP_RANGE
fi

run_step() {
  local num=$1
  local name=$2
  local cmd=$3
  echo ""
  echo "══════════════════════════════════════════════════"
  echo "  STEP $num: $name"
  echo "  $(date '+%F %T')"
  echo "══════════════════════════════════════════════════"
  if [ $DRY_RUN = 1 ]; then
    echo "  [dry-run] Would run: $cmd"
    return 0
  fi
  eval "$cmd"
  local rc=$?
  if [ $rc -ne 0 ]; then
    echo "  ❌ STEP $num FAILED (rc=$rc)"
    return $rc
  fi
  echo "  ✅ STEP $num DONE"
  return 0
}

cat <<EOF
╔══════════════════════════════════════════════════╗
║  BaiZe Post-Train 11/9 Launch Orchestrator       ║
║  R12: Launch Readiness + GRPO Hyperparam Audit   ║
╚══════════════════════════════════════════════════╝
  Mode      : $([ $DRY_RUN = 1 ] && echo 'DRY-RUN' || echo 'EXECUTE')
  Steps     : $STEP_START-$STEP_END
  Quick     : $QUICK
  NAS_ROOT  : $NAS_ROOT
  GPU IDs   : ${GPU_IDS:-auto}
  Venv      : $BAIZE_VENV_DIR ($([ -d "$BAIZE_VENV_DIR" ] && echo 'exists' || echo 'NOT YET'))
  Model     : $BAIZE_MODEL_PATH ($([ -d "$BAIZE_MODEL_PATH" ] && echo 'exists' || echo 'MISSING'))
  EDA Base  : $BAIZE_EDA_BASE ($([ -d "$BAIZE_EDA_BASE" ] && echo 'exists' || echo 'MISSING'))
EOF

GPU_FLAG=""
[ -n "$GPU_IDS" ] && GPU_FLAG="--gpu-ids $GPU_IDS"

DIAG_FLAGS="--full"
[ $QUICK = 1 ] && DIAG_FLAGS="--quick"

# === STEP 0: Setup cu124 venv ===
if [ $STEP_START -le 0 ] && [ $STEP_END -ge 0 ]; then
  run_step 0 "Setup CUDA 12.4 venv (torch+sglang+verl)" \
    "bash '$SCRIPT_DIR/baize_posttrain_setup_cu124_venv.sh' --yes" || exit $?
fi

# === STEP 1: Preflight check ===
if [ $STEP_START -le 1 ] && [ $STEP_END -ge 1 ]; then
  run_step 1 "Preflight check (env+data+scripts)" \
    "bash '$SCRIPT_DIR/baize_posttrain_preflight_check.sh'" || exit $?
fi

# === STEP 2: SGLang serve + Baseline eval (36%复测) ===
if [ $STEP_START -le 2 ] && [ $STEP_END -ge 2 ]; then
  run_step 2 "SGLang serve MiniCPM5-2B + Baseline eval (36%)" \
    "bash '$SCRIPT_DIR/baize_posttrain_minicpm5_diag.sh' $DIAG_FLAGS $GPU_FLAG" || exit $?
fi

# === STEP 3: Collect failure trajectories (D1-D6 extraction) ===
if [ $STEP_START -le 3 ] && [ $STEP_END -ge 3 ]; then
  run_step 3 "Extract D1-D6 from failure trajectories" \
    "bash '$SCRIPT_DIR/baize_posttrain_minicpm5_diag.sh' --extract-only $GPU_FLAG" || exit $?
fi

# === STEP 4: Contamination gate (verify no eval data in training) ===
if [ $STEP_START -le 4 ] && [ $STEP_END -ge 4 ]; then
  run_step 4 "Contamination gate check" \
    "bash '$SCRIPT_DIR/baize_posttrain_contamination_gate.sh'" || {
      echo "  ⚠️ Contamination gate failed — DO NOT proceed to RL"
      exit 1
    }
fi

# === STEP 5: RL smoke test (10 iters, R2 reward arm) ===
if [ $STEP_START -le 5 ] && [ $STEP_END -ge 5 ]; then
  run_step 5 "RL smoke test (GRPO R2, 10 iters)" \
    "bash '$SCRIPT_DIR/baize_posttrain_rl_grpo.sh' --smoke --reward-arm R2 $GPU_FLAG" || exit $?
fi

# === STEP 6: Full RL training (R2 reward arm, 2000 iters) ===
if [ $STEP_START -le 6 ] && [ $STEP_END -ge 6 ]; then
  run_step 6 "Full RL training (GRPO R2, surrogate)" \
    "bash '$SCRIPT_DIR/baize_posttrain_rl_grpo.sh' --reward-arm R2 $GPU_FLAG" || exit $?
fi

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  11/9 Launch Sequence Complete                   ║"
echo "║  Results: $BAIZE_EXP_DIR/baize_posttrain_rl_grpo  ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
echo "⚠️  Surrogate RL results are NOT transferable to BaiZe."
echo "    These validate the method chain and produce reusable pipeline artifacts."