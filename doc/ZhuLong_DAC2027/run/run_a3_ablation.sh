#!/bin/bash
# run_a3_ablation.sh — ZhuLong A3 臂 (强制小预算 + research spawn · H_ctx 检验)
#
# 设计 (2026-11-15 用户令放行 A3-A6; A0′ 已测 = 16.7±0.8%):
#   A0′ = in<=32K · out<=4096 · 无 spawn · compact@28.8K = 16.7±0.8% (3 valid: r2=15.8/r3=17.1/r4=17.1)
#   A3  = A0′ 配置 + research spawn (hint 注入; 子 agent 继承无 MCP, 用 read_files/search_codebase)
#   唯一变量 vs A0′ = spawn (单变量). 子 agent 继承同样 32K/4K 预算 ⇒ 预算本身即强制交付机制.
#   预注册判据: A3 ITT >= A0′ ITT + 3pp (>=19.7%) · McNemar 方向一致 (b>=6, c>=6).
#   假设 H_ctx: 在小预算下, 把调研委托给独立上下文子 agent > 单 agent 压缩 (Δ 与 所需上下文/窗口 正相关).
#
# v1 说明 (MEMORY 已记理由): hint-only spawn, 不依赖 H2 wrapper (H2 列为 A4 前置).
#   子 agent 无 MCP (cline 3.0.51 已知限制) ⇒ 只做 read_files/search_codebase 调研, 主 agent 用 MCP 验证执行.
#   若 A3 v1 显示苗头, 再上 A3′ (hook 强制交接 + H2 INHERIT_MCP=1).
#
# 沙盒错峰: 8650 池 (与 A0′ 同池, 不干扰 8664 池他线 eval).
# 用法:
#   全量: bash run_a3_ablation.sh                       # 3 轮 × 40 题 · -p 4
#   smoke: SUBSET_FILE=.../smoke8_a0prime.txt ROUNDS=1 bash run_a3_ablation.sh
set -uo pipefail

REPO_RUN="/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run"
BASE_DIR="/nasdata/app.e0031982/code/eda_fastmcp"
export PYTHON="${PYTHON:-/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python}"

ARM="A3"
ARM_DIR="/nasdata/app.e0031982/subagent_ablation/A3"
EVAL_ROOT_OVERRIDE="/tmp/zhulong_a3_eval"
TRACE_BASE="/tmp/zhulong_a3_trace"
MASTER_LOG="/tmp/zhulong_a3_ablation.log"
HINT_FILE="$REPO_RUN/subagent_hint_a3.txt"

SUBSET_FILE="${SUBSET_FILE:-$REPO_RUN/compaction_subset_40.txt}"
PARALLEL="${PARALLEL:-4}"
ROUNDS="${ROUNDS:-3}"
START_ROUND="${START_ROUND:-1}"

# 8650 池 (与 A0′ 同池 · 错峰)
POOL_8650_PORTS="8650,8651,8652,8654"
POOL_8650_ENDPOINTS="8650:/proj/train/AI/workdir/t0002997_1,8651:/proj/train/AI/workdir/t0002997_2,8652:/proj/train/AI/workdir/t0002997_3,8654:/proj/train/AI/workdir/t0002997_4"
POOL_8650_WORKERS="4"

ENV_BAK="$BASE_DIR/.env.bak.a3.$$"

log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$MASTER_LOG"; }

swap_env_to_8650() {
  cp -a "$BASE_DIR/.env" "$ENV_BAK"
  "$PYTHON" - <<PYEOF
import re,sys
p="$BASE_DIR/.env"
s=open(p).read()
def rep(line,var,val):
    return re.sub(r'^'+var+r'=.*', var+'='+val, line, flags=re.M)
s=rep(s,"PROXY_PORTS","$POOL_8650_PORTS")
s=rep(s,"SANDBOX_ENDPOINTS","$POOL_8650_ENDPOINTS")
s=rep(s,"EVAL_SANDBOX_WORKERS","$POOL_8650_WORKERS")
open(p,"w").write(s)
PYEOF
  log "  .env swapped to 8650 pool (bak=$ENV_BAK)"
}

restore_env() {
  if [[ -f "$ENV_BAK" ]]; then
    cp -a "$ENV_BAK" "$BASE_DIR/.env"
    rm -f "$ENV_BAK"
    log "  .env restored from backup"
  fi
}
trap restore_env EXIT INT TERM

run_round() {
  local ROUND="$1"
  local round_log="/tmp/a3_r${ROUND}.log"
  log "=== Round $ROUND: arm=$ARM (in<=32K · out<=4096 · research spawn · compact@28.8K) ==="

  if [[ ! -d "$ARM_DIR/settings" ]]; then log "❌ arm dir 缺失: $ARM_DIR"; return 1; fi
  if [[ ! -f "$HINT_FILE" ]]; then log "❌ hint 文件缺失: $HINT_FILE"; return 1; fi

  # providers.json 防御性重写 (与 A0′ 一致: maxTokens=4096, dsv4-pro-cloud, /cloud/v1)
  "$PYTHON" - <<'PYEOF'
import json
p="/nasdata/app.e0031982/subagent_ablation/A3/settings/providers.json"
d=json.load(open(p))
d["providers"]["openai-compatible"]["settings"]["maxTokens"]=4096
d["providers"]["openai-compatible"]["settings"]["model"]="deepseek-v4-pro-cloud"
d["providers"]["openai-compatible"]["settings"]["baseUrl"]="http://agi-gateway.cxmt.com/cloud/v1"
json.dump(d,open(p,"w"),ensure_ascii=False,indent=2)
print("providers.json maxTokens=",d["providers"]["openai-compatible"]["settings"]["maxTokens"])
PYEOF

  # 环境变量 (与 A0′ 逐字节一致, 唯一差异 = LANG_HINT 注入 spawn hint)
  export CLI_AGENT=cline
  export CLI_DATA_DIR="$ARM_DIR"
  export CLINE_COMPACTION="basic"
  export CLINE_THINKING="medium"
  export CLINE_UNIFIED_DATA_DIR=1
  export EVAL_BENCHMARK="benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl"
  export EVAL_ROOT_DIR_OVERRIDE="$EVAL_ROOT_OVERRIDE"
  export PARALLEL
  unset CLINE_AGENTS_SRC              # spawn-only (同 A1/A2, 无 configured agent)

  # 🔑 唯一变量: LANG_HINT = A3 research spawn hint (A0′ 此处为空)
  export LANG_HINT="$(cat "$HINT_FILE")"
  log "  hint=$(echo "$LANG_HINT" | head -1) ... ($(echo "$LANG_HINT" | wc -l) lines)"

  if [[ -f "$SUBSET_FILE" ]]; then
    export TASK_FILTER=$(tr '\n' ',' < "$SUBSET_FILE" | sed 's/,$//')
    log "  subset=${SUBSET_FILE##*/} ($(wc -l < "$SUBSET_FILE") tasks) · -p $PARALLEL"
  else
    log "❌ subset 不存在: $SUBSET_FILE"; return 1
  fi

  swap_env_to_8650

  : > "$round_log"
  cd "$BASE_DIR"
  log "  launching run_cline_script.sh (cap 43200s) -> $round_log"
  timeout --signal=TERM --kill-after=120 43200 bash scripts/run_cline_script.sh -p "$PARALLEL" -n >> "$round_log" 2>&1
  local ec=$?
  log "  round $ROUND exit=$ec"

  restore_env

  log "  --- 评分 ---"
  grep -E 'pass \(|评估结果汇总|PASS_RATE|generated|completed' "$round_log" | tail -8 | tee -a "$MASTER_LOG"

  # spawn 调用统计 (验证 hint 生效)
  local n_spawn=$(grep -oiE 'spawn_agent' "$round_log" 2>/dev/null | wc -l)
  log "  spawn_agent mentions in log: $n_spawn (验证 hint 注入生效; A2 r1 参考值=107)"

  # trace 归档
  local batch_dir=$(ls -td "$EVAL_ROOT_OVERRIDE"/*/ 2>/dev/null | head -1)
  if [[ -n "$batch_dir" && -d "${batch_dir%/}/code" ]]; then
    local trace_dst="$TRACE_BASE/r${ROUND}/$(basename "${batch_dir%/}")"
    mkdir -p "$trace_dst"
    cp -a "${batch_dir%/}/code/." "$trace_dst/" 2>/dev/null && log "  trace → $trace_dst" || true
  fi
  for _old in "$EVAL_ROOT_OVERRIDE"/*/; do
    [[ "$_old" == "${batch_dir}" ]] && continue
    [[ -d "$_old" ]] && rm -rf "$_old"
  done
  log "  round $ROUND done"
}

# ===== main =====
mkdir -p "$EVAL_ROOT_OVERRIDE" "$TRACE_BASE"
log "=========================================="
log "ZhuLong A3 臂 (in<=32K · out<=4096 · research spawn · compact@28.8K)"
log "base=deepseek-v4-pro-cloud  harness=cline 3.0.51  compaction=basic  thinking=medium"
log "subset=${SUBSET_FILE##*/}  -p $PARALLEL  rounds=$ROUNDS  sandbox=8650pool(错峰)"
log "对照: A0′(16.7±0.8%) · 唯一变量=spawn · 判据=A3 ITT>=A0′+3pp(>=19.7%) McNemar 方向一致"
log "=========================================="

for round in $(seq "$START_ROUND" "$((START_ROUND+ROUNDS-1))"); do
  run_round "$round"
done

log "=========================================="
log "A3 全部 $ROUNDS 轮完成 — 评分见本日志 + /tmp/a3_r*.log"
log "=========================================="
