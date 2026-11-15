#!/bin/bash
# run_a0prime_ablation.sh — ZhuLong A0′ 预算基线 (单 agent · 无 spawn · 强制小预算)
#
# 设计 (2026-11-15 用户令放行 A3-A6, A0′ = A3 的预注册锚点):
#   A0  = compaction-basic · in<=32K(contextWindow=32000) · out<=16384 · 无 spawn · compact@28.8K = 69.2%
#   A0′ = A0 配置 + maxTokens 16384->4096 (out<=4K) · in<=32K 不变 · 无 spawn · compact@28.8K
#   唯一变量 vs A0 = out-budget (16K->4K); A3 vs A0′ = spawn (单变量).
#   in<=32K 经 models.json contextWindow=32000 实现 → compaction=basic 在 ~28.8K 触发 (H_ctx 强制压缩 regime).
#
# 沙盒错峰: 用 8650 池 (8650/8651/8652/8654, workdir t0002997_{1,2,3,4})，不干扰 8664 池在跑的 post-train eval.
#   每轮: 备份 .env -> sed 改 PROXY_PORTS/SANDBOX_ENDPOINTS/EVAL_SANDBOX_WORKERS 为 8650 池 -> 跑 -> trap 还原.
#   post-train eval (PID1910477) 已在内存中持有 8664 环境且不重读 .env → 不受影响.
#
# 用法:
#   全量: bash run_a0prime_ablation.sh            # 3 轮 × 40 题 · -p 4
#   smoke: SUBSET_FILE=.../smoke8.txt ROUNDS=1 bash run_a0prime_ablation.sh
set -uo pipefail

REPO_RUN="/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run"
BASE_DIR="/nasdata/app.e0031982/code/eda_fastmcp"
export PYTHON="${PYTHON:-/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python}"

ARM="A0prime"
ARM_DIR="/nasdata/app.e0031982/subagent_ablation/A0prime"
EVAL_ROOT_OVERRIDE="/tmp/zhulong_a0prime_eval"      # /nasdata 95% 满 → trace 落 /tmp
TRACE_BASE="/tmp/zhulong_a0prime_trace"
MASTER_LOG="/tmp/zhulong_a0prime_ablation.log"

SUBSET_FILE="${SUBSET_FILE:-$REPO_RUN/compaction_subset_40.txt}"
PARALLEL="${PARALLEL:-4}"
ROUNDS="${ROUNDS:-3}"

# 8650 池 (错峰 · 与 8664 池 post-train eval 隔离)
POOL_8650_PORTS="8650,8651,8652,8654"
POOL_8650_ENDPOINTS="8650:/proj/train/AI/workdir/t0002997_1,8651:/proj/train/AI/workdir/t0002997_2,8652:/proj/train/AI/workdir/t0002997_3,8654:/proj/train/AI/workdir/t0002997_4"
POOL_8650_WORKERS="4"

ENV_BAK="$BASE_DIR/.env.bak.a0prime.$$"

log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$MASTER_LOG"; }

swap_env_to_8650() {
  # 备份 .env, 改 3 行到 8650 池 (串行, 不并发)
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
  local round_log="/tmp/a0prime_r${ROUND}.log"
  log "=== Round $ROUND: arm=$ARM (in<=32K · out<=4096 · no spawn · compact@28.8K) ==="

  if [[ ! -d "$ARM_DIR/settings" ]]; then log "❌ arm dir 缺失: $ARM_DIR"; return 1; fi

  # providers.json 防御性重写 (cline auto-migration 可能覆盖)
  "$PYTHON" - <<'PYEOF'
import json
p="/nasdata/app.e0031982/subagent_ablation/A0prime/settings/providers.json"
d=json.load(open(p))
d["providers"]["openai-compatible"]["settings"]["maxTokens"]=4096
d["providers"]["openai-compatible"]["settings"]["model"]="deepseek-v4-pro-cloud"
d["providers"]["openai-compatible"]["settings"]["baseUrl"]="http://agi-gateway.cxmt.com/cloud/v1"
json.dump(d,open(p,"w"),ensure_ascii=False,indent=2)
print("providers.json maxTokens=",d["providers"]["openai-compatible"]["settings"]["maxTokens"])
PYEOF

  # 环境变量 (匹配 A0/compaction-basic, 仅 maxTokens=4096 不同; 无 spawn hint)
  export CLI_AGENT=cline
  export CLI_DATA_DIR="$ARM_DIR"
  export CLINE_COMPACTION="basic"
  export CLINE_THINKING="medium"
  export LANG_HINT=""                 # 无 spawn 提示 (A0′ = 无 spawn)
  export CLINE_UNIFIED_DATA_DIR=1
  export EVAL_BENCHMARK="benchmarks/EDA-Eval-pyAether/EDA-Eval-PyAether-158.jsonl"
  export EVAL_ROOT_DIR_OVERRIDE="$EVAL_ROOT_OVERRIDE"
  export PARALLEL
  unset CLINE_AGENTS_SRC              # 无 configured agent

  # TASK_FILTER (逗号分隔)
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

  # 评分 (Pass@1 口径 = log 里 pass (xx.x%))
  log "  --- 评分 ---"
  grep -E 'pass \(|评估结果汇总|PASS_RATE|generated|completed' "$round_log" | tail -8 | tee -a "$MASTER_LOG"

  # trace 归档 (code/ 下 sessions, 控体积)
  local batch_dir=$(ls -td "$EVAL_ROOT_OVERRIDE"/*/ 2>/dev/null | head -1)
  if [[ -n "$batch_dir" && -d "${batch_dir%/}/code" ]]; then
    local trace_dst="$TRACE_BASE/r${ROUND}/$(basename "${batch_dir%/}")"
    mkdir -p "$trace_dst"
    cp -a "${batch_dir%/}/code/." "$trace_dst/" 2>/dev/null && log "  trace → $trace_dst" || true
  fi
  # 清旧 batch (控 /tmp 体积)
  for _old in "$EVAL_ROOT_OVERRIDE"/*/; do
    [[ "$_old" == "${batch_dir}" ]] && continue
    [[ -d "$_old" ]] && rm -rf "$_old"
  done
  log "  round $ROUND done"
}

# ===== main =====
mkdir -p "$EVAL_ROOT_OVERRIDE" "$TRACE_BASE"
log "=========================================="
log "ZhuLong A0′ 预算基线 (in<=32K · out<=4096 · no spawn · compact@28.8K)"
log "base=deepseek-v4-pro-cloud  harness=cline 3.0.51  compaction=basic  thinking=medium"
log "subset=${SUBSET_FILE##*/}  -p $PARALLEL  rounds=$ROUNDS  sandbox=8650pool(错峰)"
log "对照: A0(compaction-basic 69.2±1.4%) · 唯一变量=out-budget 16384->4096"
log "=========================================="

for round in $(seq 1 "$ROUNDS"); do
  run_round "$round"
done

log "=========================================="
log "A0′ 全部 $ROUNDS 轮完成 — 评分见本日志 + /tmp/a0prime_r*.log"
log "=========================================="
