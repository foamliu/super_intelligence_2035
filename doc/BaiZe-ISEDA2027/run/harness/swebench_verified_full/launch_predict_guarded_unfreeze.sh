#!/bin/bash
# launch_predict_guarded_unfreeze.sh — 2026-11-20 16:3x 解冻令·Step 2.1
#   Verified predict 3 路（codex/pi/dsh）续跑，限并发 ≤2 路。
#   每路经 predict_guarded.sh（ulimit -v 200GiB + OMP≤8 + nice19/ionice3）。
#
# Usage:
#   bash launch_predict_guarded_unfreeze.sh codex pi      # 启动 2 路（≤2 并发）
#   bash launch_predict_guarded_unfreeze.sh deepseek-harness   # 启动 1 路（等前面某路完成后再起）
#   bash launch_predict_guarded_unfreeze.sh status       # 查看进度
#
# 判据（每轮自检）：pretrain step ≤7.4s；宿主 mem avail ≥512G；超了即暂停。
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LOGDIR="$HERE/logs_glm53"
mkdir -p "$LOGDIR"
GUARD="$HERE/../predict_guarded.sh"

export HARNESS_MODEL="glm-5.3-flash"
export OPENAI_API_KEY="02_088EE9051AAE4BF0ABFC7130331BF697_6903b05e-6f2d-4a69-93be-96e2b790053f"
export MODEL_SUFFIX="glm-5.3-flash"
export RUN_ID_PREFIX="verified_full_glm53"
export EVAL_TAG="glm53_"
export PRED_SUBDIR="predictions_glm53"
export WORKDIR_TAG="_glm53"
export GW_PROXY_PORT="9092"
export GW_DSH_PORT="9093"
export PYTHONUNBUFFERED=1
export PATH="$HOME/.bun/bin:$HOME/.local/bin:$PATH"
export PYTHONPATH="/tmp/dsh_sdk:${PYTHONPATH:-}"
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY 2>/dev/null || true
export no_proxy="127.0.0.1,localhost,agi-gateway.cxmt.com"
export NO_PROXY="127.0.0.1,localhost,agi-gateway.cxmt.com"

if [ "${1:-}" = "status" ]; then
  for h in codex pi deepseek-harness; do
    n=$(ls "$HERE/predictions_glm53/${h}__"*.json 2>/dev/null | wc -l)
    running=$(pgrep -f "run_verified_full.py predict --harness $h" >/dev/null 2>&1 && echo "RUN" || echo "idle")
    printf '  %-20s %3s/500 done | %s\n' "$h" "$n" "$running"
  done
  exit 0
fi

# 并发上限 2（解冻令判据）
MAX_CONCURRENT=2
ROUTES=("$@")
if [ "${#ROUTES[@]}" -eq 0 ]; then
  echo "Usage: $0 <harness1> [harness2]   (max 2 concurrent)" >&2
  exit 2
fi
if [ "${#ROUTES[@]}" -gt "$MAX_CONCURRENT" ]; then
  echo "ERROR: max $MAX_CONCURRENT concurrent routes (got ${#ROUTES[@]})" >&2
  exit 1
fi

echo "=== guarded predict unfreeze | $(date) | routes: ${ROUTES[*]} ==="
for h in "${ROUTES[@]}"; do
  if pgrep -f "run_verified_full.py predict --harness $h" >/dev/null 2>&1; then
    echo "  $h already running, skip"
    continue
  fi
  LOG="$LOGDIR/predict_${h}_glm53_guarded.log"
  echo "  launching $h -> $LOG (through predict_guarded.sh)"
  setsid bash -c "cd '$HERE' && bash '$GUARD' python3 run_verified_full.py predict --harness '$h'" \
    < /dev/null > "$LOG" 2>&1 &
  echo "  PID=$!"
  sleep 3   # stagger to avoid gateway thundering herd
done
echo "Launched. Monitor: bash $0 status"
