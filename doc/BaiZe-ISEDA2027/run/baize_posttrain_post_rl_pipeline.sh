#!/usr/bin/env bash
# baize_posttrain_post_rl_pipeline.sh — R63: Post-RL Evaluation Pipeline
#
# Step 7 of the 11/9 launch sequence (missing from launch_11_9.sh steps 0-6).
# After RL training completes, this script:
#   7a. Select best RL checkpoint (baize_posttrain_ckpt_selector.py)
#   7b. SGLang serve the selected checkpoint
#   7c. Run 158-case eval (5-run, 2500s, -p 8 -n) via baize_posttrain_eval.sh
#   7d. Run eval_analysis.py (McNemar + paired bootstrap vs baseline)
#   7e. Run baseline_gate.py (milestone M1-M4 check)
#   7f. Generate final HTML report
#   7g. Print summary
#
# Usage:
#   bash baize_posttrain_post_rl_pipeline.sh --dry-run
#   bash baize_posttrain_post_rl_pipeline.sh --rl-dir /path/to/rl_output
#   bash baize_posttrain_post_rl_pipeline.sh --rl-dir <dir> --baseline-dir <dir>
#   bash baize_posttrain_post_rl_pipeline.sh --rl-dir <dir> --quick  # 10 tasks, 1 run
#
# ⚠️ Surrogate RL results are NOT transferable to BaiZe.
set -uo pipefail

SCRIPT_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"
source "$SCRIPT_DIR/baize_posttrain_paths.sh"

DRY_RUN=0
RL_DIR=""
BASELINE_DIR="${BAIZE_EXP_DIR}/baize_posttrain_eval/baseline"
QUICK=0
GPU_IDS=""
REPORT_DIR="${BAIZE_REPORT_DIR:-$(dirname "$SCRIPT_DIR")/reports}"

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)     DRY_RUN=1 ;;
    --rl-dir)      RL_DIR="$2"; shift ;;
    --baseline-dir) BASELINE_DIR="$2"; shift ;;
    --quick)       QUICK=1 ;;
    --gpu-ids)     GPU_IDS="$2"; shift ;;
    --report-dir)  REPORT_DIR="$2"; shift ;;
    *) echo "Unknown: $1" ;;
  esac
  shift
done

if [ -z "$RL_DIR" ]; then
  RL_DIR="${BAIZE_EXP_DIR}/baize_posttrain_rl_grpo"
  echo "[R63] --rl-dir not specified, defaulting to: $RL_DIR"
fi

GPU_FLAG=""
[ -n "$GPU_IDS" ] && GPU_FLAG="--gpu-ids $GPU_IDS"
EVAL_QUICK=""
[ $QUICK = 1 ] && EVAL_QUICK="--quick"

cat <<EOF
╔══════════════════════════════════════════════════╗
║  R63: Post-RL Evaluation Pipeline (Step 7)       ║
╚══════════════════════════════════════════════════╝
  Mode       : $([ $DRY_RUN = 1 ] && echo 'DRY-RUN' || echo 'EXECUTE')
  RL output  : $RL_DIR
  Baseline   : $BASELINE_DIR
  Report dir : $REPORT_DIR
  Quick      : $QUICK
  $(date '+%F %T')
EOF

run_sub() {
  local num=$1 name=$2 cmd=$3
  echo ""
  echo "── Step 7$num: $name ──"
  if [ $DRY_RUN = 1 ]; then
    echo "  [dry-run] Would run: $cmd"
    return 0
  fi
  eval "$cmd"
  local rc=$?
  if [ $rc -ne 0 ]; then
    echo "  ❌ Step 7$num FAILED (rc=$rc)"
    return $rc
  fi
  echo "  ✅ Step 7$num DONE"
  return 0
}

# ── Step 7a: Select best checkpoint ──
CKPT_JSON="$RL_DIR/best_ckpt.json"
run_sub a "Select best RL checkpoint" \
  "python3 '$SCRIPT_DIR/baize_posttrain_ckpt_selector.py' \
    --ckpt-dir '$RL_DIR' \
    --log '$RL_DIR/verl_train.log' \
    --json '$CKPT_JSON' \
    --html '$REPORT_DIR/report_posttrain_r63_ckpt_selector_zh.html'" || exit $?

if [ $DRY_RUN = 1 ]; then
  BEST_CKPT="/tmp/dryrun/global_step_100"
  echo "  [dry-run] Best checkpoint: $BEST_CKPT"
else
  BEST_CKPT=$(python3 -c "import json; d=json.load(open('$CKPT_JSON')); print(d['selected']['path'])" 2>/dev/null || echo "")
  if [ -z "$BEST_CKPT" ]; then
    echo "❌ Failed to extract best checkpoint path from JSON"
    exit 1
  fi
  echo "  Best checkpoint: $BEST_CKPT"
fi

# ── Step 7b: SGLang serve + eval ──
# The eval script handles SGLang serve internally via the driver
EVAL_BACKBONE="baize-rl"
EVAL_OUT="${BAIZE_EXP_DIR}/baize_posttrain_eval/${EVAL_BACKBONE}"

run_sub b "158-case eval (5-run, frozen protocol)" \
  "bash '$SCRIPT_DIR/baize_posttrain_eval.sh' \
    --backbone $EVAL_BACKBONE \
    --endpoint http://127.0.0.1:8000/v1 \
    --model $EVAL_BACKBONE \
    --out-base '${BAIZE_EXP_DIR}/baize_posttrain_eval' $EVAL_QUICK" || exit $?

# ── Step 7c: Statistical analysis (McNemar + bootstrap) ──
run_sub c "Eval analysis: McNemar + paired bootstrap vs baseline" \
  "python3 '$SCRIPT_DIR/baize_posttrain_eval_analysis.py' \
    --ckpt baseline --dir '$BASELINE_DIR' \
    --ckpt $EVAL_BACKBONE --dir '$EVAL_OUT' \
    --compare \
    --html '$REPORT_DIR/report_posttrain_r63_eval_comparison_zh.html'" || exit $?

# ── Step 7d: Milestone gate check ──
run_sub d "Baseline gate: M1-M4 milestone check" \
  "python3 '$SCRIPT_DIR/baize_posttrain_baseline_gate.py' \
    --dir '$EVAL_OUT' \
    --baseline-dir '$BASELINE_DIR' \
    --html '$REPORT_DIR/report_posttrain_r63_milestone_gate_zh.html'" || exit $?

# ── Step 7e: Summary ──
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  R63 Post-RL Pipeline Complete                   ║"
echo "╚══════════════════════════════════════════════════╝"
echo "  Best checkpoint : $BEST_CKPT"
echo "  Eval results    : $EVAL_OUT"
echo "  Reports         :"
echo "    $REPORT_DIR/report_posttrain_r63_ckpt_selector_zh.html"
echo "    $REPORT_DIR/report_posttrain_r63_eval_comparison_zh.html"
echo "    $REPORT_DIR/report_posttrain_r63_milestone_gate_zh.html"
echo ""
echo "⚠️  Surrogate RL results are NOT transferable to BaiZe."
echo "    These validate the method chain and produce reusable pipeline artifacts."