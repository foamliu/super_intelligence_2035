#!/bin/bash
# relaunch_opencode.sh — relaunch opencode predict with doubao-pro (v2.3.2)
# Usage: setsid bash relaunch_opencode.sh > /dev/null 2>&1 < /dev/null &
#
# History:
#   2026-11-26: Created. Root cause of empty patches:
#     1. opencode v2.4.2 tools.edit() bug — doesn't write to disk.
#        Downgraded to v2.3.2 (npm install -g @opencode/cli@2.3.2).
#     2. HARNESS_MODEL env var not set → defaulted to glm-5.3-flash → HTTP 403.
#     3. 40GB opencode.db from v1.18.27 era causing version mismatch.
#        Moved aside; fresh DB created on first run.

HERE="$(cd "$(dirname "$0")" && pwd)"
VF_DIR="$HERE/swebench_verified_full"
LOGDIR="$HERE/logs_doubao_pro"

export HARNESS_MODEL="doubao-seed-2.0-pro-cloud"
export MODEL_SUFFIX="doubao-seed-2.0-pro-cloud"
export PRED_SUBDIR="predictions_doubao_pro"
export WORKDIR_TAG="_doubao_pro"
export EVAL_TAG="doubao_pro_"
export PREDICT_WORKERS="1"
export GW_USAGE_LOG="/tmp/gw_proxy_usage.jsonl"
export no_proxy="127.0.0.1,localhost,agi-gateway.cxmt.com"
export NO_PROXY="127.0.0.1,localhost,agi-gateway.cxmt.com"
export GW_PROXY_PORT="9090"
export GW_DSH_PORT="9091"
export OPENAI_API_KEY="dummy-key-for-proxy"
export PYTHONUNBUFFERED="1"
export PATH="$HOME/.bun/bin:$PATH"
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY 2>/dev/null || true

cd "$VF_DIR"
nice -n 10 python3 run_verified_full.py predict \
  --harness opencode --workers 1 \
  > "$LOGDIR/opencode_doubao_pro.log" 2>&1
