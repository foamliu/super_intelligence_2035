#!/bin/bash
# launch_infra_rerun.sh — 夜间 infra 重跑启动器 (21:00–09:00 窗口)
#
# 2026-11-23 用户令·第二步: 重跑 infra failed (从 cline 起，按 infra 数量降序)
# 用法: bash launch_infra_rerun.sh [--dry-run] [--route X]
#
# 硬护栏: predict_guarded.sh (ulimit200GiB + OMP8 + nice19 + ionice3)
#          swebench_guarded_eval.py (docker mem128g/cpu16)
#          harness_resource_guard.sh (PID931671) 常开
# 并发: ≤1 路 (首夜保守; 后续可调 RERUN_MAX_CONCURRENT)
set -eu

HARNESS_DIR="$(cd "$(dirname "$0")" && pwd)"
VF_DIR="$HARNESS_DIR/swebench_verified_full"

# 环境变量 (与原 predict 一致)
export MODEL_SUFFIX="${MODEL_SUFFIX:-glm-5.3-flash}"
export EVAL_TAG="${EVAL_TAG:-glm53_}"
export PRED_SUBDIR="${PRED_SUBDIR:-predictions_glm53}"
export WORKDIR_TAG="${WORKDIR_TAG:-_glm53}"
export RUN_ID_PREFIX="${RUN_ID_PREFIX:-verified_full}"
export EVAL_MAX_WORKERS="${EVAL_MAX_WORKERS:-4}"

# 窗口检查
H=$(date +%H)
if [ "$H" -ge 21 ] || [ "$H" -lt 9 ]; then
  echo "[launch] 窗口内 (hour=$H); 启动 infra 重跑"
else
  echo "[launch] 窗口外 (hour=$H); park. 下一窗口 21:00."
  exit 0
fi

# 用 predict_guarded.sh 包裹 (ulimit200GiB + OMP8 + nice19 + ionice3)
cd "$VF_DIR"
exec bash "$HARNESS_DIR/predict_guarded.sh" python3 rerun_infra_verified.py --skip-window-check "$@"
