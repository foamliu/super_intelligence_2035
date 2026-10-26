#!/usr/bin/env bash
# ============================================================
# baize-llm · 公共函数库（由 preflight/train/status/tb 脚本 source）
# 约定：只读、无副作用；不在此处读 configs（由调用方先 source common.env）
# ============================================================
set -uo pipefail

BAIZE_LLM_HOME="${BAIZE_LLM_HOME:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
export BAIZE_LLM_HOME

ts()   { date '+%F %T'; }
log()  { echo "[$(ts)] $*"; }
warn() { echo "[$(ts)] WARN: $*" >&2; }
err()  { echo "[$(ts)] FAIL: $*" >&2; }
die()  { echo "[$(ts)] FATAL: $*" >&2; exit 1; }
pass() { echo "[$(ts)] PASS: $*"; }

# ---- launcher --help 缓存（特性探测，避免每次重启 python）----
launcher_help() {
  local cache="/tmp/baize_llm_launcher_help.txt"
  if [ ! -s "$cache" ] || [ "${BAIZE_REPROBE:-0}" = "1" ]; then
    ( cd "$BAIZE_TRAIN_CODE" && timeout 180 "$PY/python" pretrain_launcher.py --help ) >"$cache" 2>&1 || true
  fi
  printf '%s\n' "$cache"
}

# has_flag --foo  ⇒ 0=支持 / 1=不支持
has_flag() {
  local f="$1" h
  h="$(launcher_help)"
  grep -q -- "$f" "$h"
}

# ---- GPU 空闲判定（单卡 used < 2GB 视为空闲）----
gpus_free_local() {
  local u
  u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1)
  [ -n "$u" ] && [ "$u" -lt 2000 ]
}
gpus_free_remote() {
  local u
  u=$(timeout 15 ssh -o StrictHostKeyChecking=no -o BatchMode=yes "$MASTER_IP" \
        'nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1' 2>/dev/null)
  [ -n "$u" ] && [ "$u" -lt 2000 ]
}
ssh_ok() {
  timeout 15 ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o ConnectTimeout=8 "$MASTER_IP" true 2>/dev/null
}

# ---- 小工具 ----
accum_of() { echo $(( GBS / (MBS * DP) )); }
tok_per_step() { echo $(( GBS * SEQ )); }
used_port() { ss -ltn 2>/dev/null | awk '{print $4}' | grep -q ":$1\$"; }
