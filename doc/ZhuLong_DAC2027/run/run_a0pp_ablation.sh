#!/bin/bash
# run_a0pp_ablation.sh — ZhuLong A0'' 预算基线 (单 agent · 无 spawn · in=8K · out=16K)
#
# 设计 (2026-11-16 09:0x 用户令: 修正 A0'/A3 — 限制 input 而非 output):
#   A0   = in<=32K · out<=16K · 无 spawn · compact@28.8K = 69.2%        (原 baseline)
#   A0'  = in<=32K · out<=4K  · 无 spawn · compact@28.8K = 16.7±0.8%   (VOID: out-budget 施压错误)
#   A0'' = in<=8K  · out<=16K · 无 spawn · compact@7.2K  = [TBD]        (本臂 · 新 baseline)
#   A3   = A0'' + research spawn (in=8K · out=16K · spawn) = [TBD]      (对照 A0'')
#
# 唯一施压变量 = INPUT 预算 (contextWindow 32K->8K); output 恒定 16K (不限制写代码迭代).
# in<=8K 经 models.json contextWindow=8000 + maxInputTokens=8000 实现
#   -> compaction=basic 在 ~7.2K (0.9×8K) 触发 (逼单 agent 在小 input 下频繁压缩 -> 信息丢失).
# 预期: 单 agent 在 in=8K 下塞不下完整 API 文档 -> 频繁 compaction -> 质量下降 (vs A0 69.2%).
#   A0'' 是 A3 (in=8K + spawn) 的预注册锚点; 判据 = A3 ITT >= A0'' ITT + 3pp + McNemar 方向一致.
#
# 沙盒错峰: 用 8650 池 (8650/8651/8652/8654, workdir t0002997_{1,2,3,4}).
#   每轮: 备份 .env -> sed 改 PROXY_PORTS/SANDBOX_ENDPOINTS/EVAL_SANDBOX_WORKERS 为 8650 池 -> 跑 -> trap 还原.
#
# 用法:
#   全量: bash run_a0pp_ablation.sh                # 3 轮 × 40 题 · -p 4
#   smoke: SUBSET_FILE=.../smoke8_a0prime.txt ROUNDS=1 bash run_a0pp_ablation.sh
set -uo pipefail

REPO_RUN="/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run"
BASE_DIR="/nasdata/app.e0031982/code/eda_fastmcp"
export PYTHON="${PYTHON:-/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python}"

ARM="A0pp"
ARM_DIR="/nasdata/app.e0031982/subagent_ablation/A0pp"
EVAL_ROOT_OVERRIDE="/tmp/zhulong_a0pp_eval"
TRACE_BASE="/tmp/zhulong_a0pp_trace"
MASTER_LOG="/tmp/zhulong_a0pp_ablation.log"

SUBSET_FILE="${SUBSET_FILE:-$REPO_RUN/compaction_subset_40.txt}"
PARALLEL="${PARALLEL:-4}"
ROUNDS="${ROUNDS:-3}"
START_ROUND="${START_ROUND:-1}"

# 8650 池 (错峰)
POOL_8650_PORTS="8650,8651,8652,8654"
POOL_8650_ENDPOINTS="8650:/proj/train/AI/workdir/t0002997_1,8651:/proj/train/AI/workdir/t0002997_2,8652:/proj/train/AI/workdir/t0002997_3,8654:/proj/train/AI/workdir/t0002997_4"
POOL_8650_WORKERS="4"

ENV_BAK="$BASE_DIR/.env.bak.a0pp.$$"

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
  local round_log="/tmp/a0pp_r${ROUND}.log"
  log "=== Round $ROUND: arm=$ARM (in<=8K · out<=16K · no spawn · compact@7.2K) ==="

  if [[ ! -d "$ARM_DIR/settings" ]]; then log "❌ arm dir 缺失: $ARM_DIR"; return 1; fi

  # providers.json 防御性重写 (out=16K) + models.json 防御性重写 (in=8K)
  "$PYTHON" - <<'PYEOF'
import json
# providers.json: maxTokens=16384 (out=16K, 与 A0 一致, 不限制 output)
p1="/nasdata/app.e0031982/subagent_ablation/A0pp/settings/providers.json"
d1=json.load(open(p1))
d1["providers"]["openai-compatible"]["settings"]["maxTokens"]=16384
d1["providers"]["openai-compatible"]["settings"]["model"]="deepseek-v4-pro-cloud"
d1["providers"]["openai-compatible"]["settings"]["baseUrl"]="http://agi-gateway.cxmt.com/cloud/v1"
json.dump(d1,open(p1,"w"),ensure_ascii=False,indent=2)
print("providers.json maxTokens=",d1["providers"]["openai-compatible"]["settings"]["maxTokens"])
# models.json: contextWindow=8000 + maxInputTokens=8000 (in=8K, 唯一施压变量)
p2="/nasdata/app.e0031982/subagent_ablation/A0pp/settings/models.json"
d2=json.load(open(p2))
m=d2["providers"]["openai-compatible"]["models"]["deepseek-v4-pro-cloud"]
m["contextWindow"]=8000
m["maxInputTokens"]=8000
json.dump(d2,open(p2,"w"),ensure_ascii=False,indent=2)
print("models.json contextWindow=",m["contextWindow"],"maxInputTokens=",m["maxInputTokens"])
PYEOF

  export CLI_AGENT=cline
  export CLI_DATA_DIR="$ARM_DIR"
  export CLINE_COMPACTION="basic"
  export CLINE_THINKING="medium"
  export LANG_HINT=""                 # 无 spawn (A0'' = 无 spawn baseline)
  export CLINE_UNIFIED_DATA_DIR=1
  export EVAL_BENCHMARK="benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl"
  export EVAL_ROOT_DIR_OVERRIDE="$EVAL_ROOT_OVERRIDE"
  export PARALLEL
  unset CLINE_AGENTS_SRC

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
log "ZhuLong A0'' 预算基线 (in<=8K · out<=16K · no spawn · compact@7.2K)"
log "base=deepseek-v4-pro-cloud  harness=cline 3.0.51  compaction=basic  thinking=medium"
log "subset=${SUBSET_FILE##*/}  -p $PARALLEL  rounds=$ROUNDS  sandbox=8650pool(错峰)"
log "对照: A0(in=32K,out=16K,69.2%) · 唯一施压变量=input预算 32K->8K · A0'' 是 A3(in=8K,spawn) 锚点"
log "判据(09:0x令): A3 ITT>=A0'' ITT+3pp + McNemar 方向一致(b>=6,c>=6)"
log "=========================================="

for round in $(seq "$START_ROUND" "$((START_ROUND+ROUNDS-1))"); do
  run_round "$round"
done

log "=========================================="
log "A0'' 全部 $ROUNDS 轮完成 — 评分见本日志 + /tmp/a0pp_r*.log"
log "=========================================="
