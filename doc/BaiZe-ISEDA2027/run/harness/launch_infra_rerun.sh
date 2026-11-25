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

# ── gw_proxy 自动启动 (2026-11-23 修复: cline 读 ~/.cline/data/globalState.json
#    的 openAiBaseUrl=127.0.0.1:9092，其他 harness 读 OPENAI_BASE_URL env=9090，
#    deepseek-harness 用 gw_proxy_dsh on 9091。三个 proxy 缺一 → 静默空 patch) ──
GW_PROXY_PY="/nas_train/app.e0031982/harness_work/gw_proxy.py"
GW_PROXY_DSH_PY="/nas_train/app.e0031982/harness_work/gw_proxy_dsh.py"
GLM53_KEY="02_088EE9051AAE4BF0ABFC7130331BF697_6903b05e-6f2d-4a69-93be-96e2b790053f"
GLM53_UPSTREAM="http://agi-gateway.cxmt.com/v1"
# 9090: codex/opencode/cc/pi/hermes (via OPENAI_BASE_URL env, default GW_PROXY_PORT)
if ! pgrep -f "gw_proxy.py.*GW_PROXY_PORT=9090" > /dev/null 2>&1; then
  GW_API_KEY="$GLM53_KEY" GW_UPSTREAM="$GLM53_UPSTREAM" GW_PROXY_PORT=9090 GW_PROXY_HOST=127.0.0.1 \
    setsid python3 "$GW_PROXY_PY" > /tmp/gw_proxy_9090.log 2>&1 < /dev/null &
  echo "[launch] started gw_proxy on 9090 (PID=$!)"
fi
# 9092: cline (reads openAiBaseUrl from ~/.cline/data/globalState.json)
if ! pgrep -f "gw_proxy.py.*GW_PROXY_PORT=9092" > /dev/null 2>&1; then
  GW_API_KEY="$GLM53_KEY" GW_UPSTREAM="$GLM53_UPSTREAM" GW_PROXY_PORT=9092 GW_PROXY_HOST=127.0.0.1 \
    setsid python3 "$GW_PROXY_PY" > /tmp/gw_proxy_9092.log 2>&1 < /dev/null &
  echo "[launch] started gw_proxy on 9092 (PID=$!)"
fi
# 9091: deepseek-harness (gw_proxy_dsh, strips DeepSeek-specific params)
if ! pgrep -f "gw_proxy_dsh.py" > /dev/null 2>&1; then
  GW_API_KEY="$GLM53_KEY" GW_UPSTREAM="http://agi-gateway.cxmt.com/cloud" GW_PROXY_PORT=9091 GW_PROXY_HOST=127.0.0.1 \
    setsid python3 "$GW_PROXY_DSH_PY" > /tmp/gw_proxy_dsh_9091.log 2>&1 < /dev/null &
  echo "[launch] started gw_proxy_dsh on 9091 (PID=$!)"
fi
sleep 2  # let proxies bind

# 窗口检查 (belt-and-suspenders; orchestrator 也有 in_window() 自检)
H=$(date +%H)
if [ "$H" -ge 21 ] || [ "$H" -lt 9 ]; then
  echo "[launch] 窗口内 (hour=$H); 启动 infra 重跑 (background)"
else
  echo "[launch] 窗口外 (hour=$H); park. 下一窗口 21:00."
  exit 0
fi

# 后台运行: setsid 脱离 cline 60min 超时; orchestrator 自管窗口结束(09:00 REGEN+stop)
# 不传 --skip-window-check: 让 orchestrator 在每路之间检查 in_window()，09:00 自动停
LOG="$VF_DIR/logs/rerun_infra_nightly.log"
mkdir -p "$VF_DIR/logs"
cd "$VF_DIR"
setsid bash "$HARNESS_DIR/predict_guarded.sh" python3 rerun_infra_verified.py "$@" \
  > "$LOG" 2>&1 < /dev/null &
LAUNCH_PID=$!
echo "[launch] 后台启动 PID=$LAUNCH_PID · log=$LOG"
echo "[launch] orchestrator 将在 09:00 窗口结束时自动 REGEN+stop"
