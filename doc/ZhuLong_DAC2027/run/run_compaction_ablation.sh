#!/bin/bash
# =====================================================================
# run_compaction_ablation.sh — ZhuLong 压缩机制消融自主编排
# 单轴: cline --compaction 档位 (basic / agentic) × 3 轮
# 基座恒定: deepseek-v4-pro-cloud (cline CLI 3.0.51, PyAether 158 → 40-task 子集, -p 8 -n, Pass@1)
# 设计: 2 臂 × 3 轮 = 6 轮, ABBA 反平衡 (r1=basic,agentic; r2=agentic,basic; r3=basic,agentic)
#       仅 --compaction 与 CLI_DATA_DIR 跨臂不同, 其余全恒定 (模型/版本/协议/thinking/子集)
# 产物: cost_C_{arm}_r{round}.json, ablation_compaction_results.json, trace_ablation_compaction/
# 可恢复: 已在 results JSON 的 TAG 幂等跳过
# =====================================================================
set -uo pipefail

# ---------- 路径 / 常量 ----------
REPO_RUN="/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run"
BASE_DIR="/nasdata/app.e0031982/code/eda_fastmcp"
EVAL_FW="/nasdata/app.e0031982/code/EDA-Eval-Framework"
EVAL_ROOT_OVERRIDE="/tmp/zhulong_compaction_eval"   # /nasdata 100% 满; 用 /tmp (24G), 每轮清理
TRACE_BASE="/nasdata/app.e0031982/code/ZhuLong_DAC2027/trace_ablation_compaction"  # 仅存 compaction.json + cost (小文件)
RESULTS_JSON="$REPO_RUN/ablation_compaction_results.json"
EXTRACT="$REPO_RUN/extract_cost.py"
SUBSET_FILE="$REPO_RUN/compaction_subset_40.txt"
MASTER_LOG="/tmp/zhulong_compaction_ablation.log"
PYTHON="/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python"
ROUNDS="${ROUNDS:-3}"                                            # 每臂轮数 (默认 3)
PARALLEL="${PARALLEL:-8}"                                        # 并行 worker (plan §11: -p 8)

# ---------- 两臂 data-dir (setup_compaction_arm_dirs.py 已建) ----------
ARM_DIR_BASIC="/nasdata/app.e0031982/compaction_ablation/basic"
ARM_DIR_AGENTIC="/nasdata/app.e0031982/compaction_ablation/agentic"

mkdir -p "$TRACE_BASE" "$EVAL_ROOT_OVERRIDE"
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$MASTER_LOG"; }

# ---------- 环境 (cline 必须不走代理访问内部 gateway; venv 含 pydantic) ----------
export PATH="/home/app.e0031982/.local/node-20/bin:$PATH"
export CLI_AGENT=cline                  # cline harness
export EVAL_FW_DIR="$EVAL_FW"
export EVAL_ROOT_DIR_OVERRIDE="$EVAL_ROOT_OVERRIDE"
export EVAL_BENCHMARK="benchmarks/EDA-Eval-pyAether/EDA-Eval-PyAether-158.jsonl"
export PYTHON="$BASE_DIR/venv/bin/python"
export NO_PROXY="agi-gateway.cxmt.com,10.129.32.75,localhost,127.0.0.1"
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY   # cline 直连内部 gateway

# ---------- 恒定协议 (跨臂不变, 仅 compaction 变) ----------
export CLINE_THINKING="medium"          # plan §11: thinking=medium
export LANG_HINT=""                     # plan §11: LANG_HINT 空 (不加思维链语言后缀)

# ---------- 40-task 子集 → TASK_FILTER (逗号分隔) ----------
if [[ ! -f "$SUBSET_FILE" ]]; then
  log "❌ 子集文件不存在: $SUBSET_FILE  (先跑 build_compaction_subset.py)"
  exit 1
fi
TASK_FILTER=$(tr '\n' ',' < "$SUBSET_FILE" | sed 's/,$//')
export TASK_FILTER
log "子集: ${SUBSET_FILE##*/}  ($(wc -l < "$SUBSET_FILE") tasks)  TASK_FILTER 长度=${#TASK_FILTER}"

# ---------- quota 探针 (deepseek-v4-pro-cloud; 防止额度耗尽空转级联) ----------
DS_KEY="02_088EE9051AAE4BF0ABFC7130331BF697_e13f4f37-836a-48a5-b149-044c8aa0785e"
DS_ENDPOINT="http://agi-gateway.cxmt.com/cloud/v1/chat/completions"
DS_MODEL="deepseek-v4-pro-cloud"
probe_quota() {
  local max_waits=48   # 48 × 300s = 4h max wait
  local w=0
  while [[ $w -lt $max_waits ]]; do
    local resp
    resp=$(curl -s -m 25 --noproxy '*' -X POST "$DS_ENDPOINT" \
      -H "Authorization: Bearer $DS_KEY" \
      -H "Content-Type: application/json" \
      -d '{"model":"'"$DS_MODEL"'","messages":[{"role":"user","content":"reply OK"}],"max_tokens":80}' 2>/dev/null)
    if echo "$resp" | grep -q '"choices"'; then
      [[ $w -gt 0 ]] && log "  ✅ quota 恢复 (waited ~$((w*5))min)"
      return 0
    fi
    if echo "$resp" | grep -q '额度已用完\|quota\|429\|rate.limit\|RateLimit'; then
      [[ $((w % 3)) -eq 0 ]] && log "  ⏳ quota exhausted, wait 300s (attempt $((w+1))/$max_waits) before $1"
    else
      log "  ⚠️ quota probe 异常响应: ${resp:0:160}"
    fi
    sleep 300; w=$((w+1))
  done
  log "  ❌ quota 未在 $((max_waits*5))min 内恢复, 放弃等待直接起跑 (可能 NA)"
  return 0
}

# ---------- 结果 JSON 追加 (幂等: 已存在 TAG 跳过) ----------
json_has_tag() { "$PYTHON" -c "
import json,sys
try:
    d=json.load(open('$RESULTS_JSON'))
except Exception:
    d={'rounds':[]}
print(1 if any(((r.get('summary') or {}).get('tag') or r.get('tag'))=='$1' for r in d.get('rounds',[])) else 0)
" 2>/dev/null; }

json_append() {  # $1=summary_json_filepath
  "$PYTHON" -c "
import json
try:
    d=json.load(open('$RESULTS_JSON'))
except Exception:
    d={'rounds':[]}
d.setdefault('rounds',[]).append(json.load(open('$1')))
open('$RESULTS_JSON','w').write(json.dumps(d,ensure_ascii=False,indent=2))
"
}

# ---------- 等待一轮结束 ----------
wait_round_done() {
  local cap=43200  # 12h 硬上限
  local t=0
  while pgrep -f '^bash scripts/run_cline_script' >/dev/null 2>&1; do
    sleep 60; t=$((t+60))
    if [[ $t -ge $cap ]]; then
      log "  ⚠️ round 超过 ${cap}s 仍 in-progress, 继续等 (不强制 kill)"
      return 0
    fi
  done
  log "  round pipeline 结束 (waited ~${t}s)"
  return 0
}

newest_gen_batch() { ls -dt "$EVAL_ROOT_OVERRIDE"/2026_* 2>/dev/null | head -1; }
newest_eval_batch() { ls -dt "$EVAL_FW"/output_evaluation/2026*_app.e0031982 2>/dev/null | head -1; }

# ---------- 跑一轮 ----------
# $1=TAG (C_basic_r1)  $2=ARM (basic|agentic)  $3=ROUND (1..3)
run_round() {
  local TAG="$1" ARM="$2" ROUND="$3"

  local ARM_DIR COMP
  if [[ "$ARM" == "basic" ]]; then ARM_DIR="$ARM_DIR_BASIC"; COMP="basic";
  elif [[ "$ARM" == "agentic" ]]; then ARM_DIR="$ARM_DIR_AGENTIC"; COMP="agentic";
  else log "❌ 未知 ARM=$ARM"; return 1; fi

  if [[ "$(json_has_tag "$TAG")" == "1" ]]; then
    log ">>> SKIP $TAG (已在 results JSON, 幂等跳过)"
    return 0
  fi

  # 前置: 不打断在跑的评测
  if pgrep -f '^bash scripts/run_cline_script' >/dev/null 2>&1; then
    log ">>> WAIT $TAG: 有其他评测在跑, 等其结束"
    wait_round_done
  fi

  # quota 探针
  probe_quota "$TAG"

  log ">>> START $TAG  (arm=$ARM  compaction=$COMP  round=$ROUND  subset=40  -p $PARALLEL)"

  # 验证 arm data-dir 完整 (cline auto-migration 可能重置 providers.json)
  local prov="$ARM_DIR/settings/providers.json"
  if ! grep -q '/cloud/v1' "$prov" 2>/dev/null; then
    log "  ⚠️ $ARM arm providers.json 疑被 reset, 重新 cline auth..."
    ( export PATH="/home/app.e0031982/.local/node-20/bin:$PATH"; export NO_PROXY="$NO_PROXY"; unset http_proxy https_proxy
      cline auth --data-dir "$ARM_DIR" --provider openai-compatible \
        --apiKey "$DS_KEY" --model "$DS_MODEL" --baseUrl "http://agi-gateway.cxmt.com/cloud/v1" \
        2>>"$MASTER_LOG" ) || log "  ❌ cline auth 失败 for $ARM"
  fi

  # 注入跨臂变量 (仅这两项随臂变)
  export CLINE_COMPACTION="$COMP"
  export CLI_DATA_DIR="$ARM_DIR"
  export PARALLEL="$PARALLEL"

  local before_gen before_eval
  before_gen=$(newest_gen_batch)
  before_eval=$(newest_eval_batch)

  local round_log="/tmp/ABL_${TAG}.log"
  : > "$round_log"

  cd "$BASE_DIR"
  log "  launching run_cline_script.sh (foreground, 12h cap) -> $round_log"
  timeout --signal=TERM --kill-after=120 43200 bash scripts/run_cline_script.sh -p "$PARALLEL" -n >> "$round_log" 2>&1
  local ec=$?
  [[ $ec -eq 124 ]] && log "  ⚠️ $TAG round 命中 12h 超时上限"
  pkill -f '^bash scripts/run_cline_script' 2>/dev/null || true

  # 评分 (grep log)
  local pass_pct pass_str
  pass_str=$(grep -oE 'pass \([0-9.]+%\)' "$round_log" | tail -1)
  pass_pct=$(echo "$pass_str" | grep -oE '[0-9.]+' | head -1)
  log "  $TAG score: ${pass_str:-<未找到 pass>}"

  # 找本轮新 gen batch
  local gen_batch eval_batch
  gen_batch=$(newest_gen_batch)
  [[ "$gen_batch" == "$before_gen" ]] && gen_batch=""
  eval_batch=$(newest_eval_batch)
  [[ "$eval_batch" == "$before_eval" ]] && eval_batch=""
  log "  gen_batch=${gen_batch:-<none>}  eval_batch=${eval_batch:-<none>}"

  # 成本抽取
  local cost_json="$REPO_RUN/cost_${TAG}.json"
  if [[ -n "$gen_batch" ]]; then
    "$PYTHON" "$EXTRACT" --batch "$gen_batch" --log "$round_log" --tag "$TAG" --out "$cost_json" 2>>"$MASTER_LOG" || log "  ⚠️ extract_cost 失败 for $TAG"
  else
    log "  ⚠️ 未找到 gen_batch, cost 抽取跳过"
    echo '{"summary":{"tag":"'"$TAG"'","pass_rate_pct":'"${pass_pct:-null}"',"n_tasks":0,"note":"gen_batch not found"}}' > "$cost_json"
  fi

  # trace 保留: 仅 compaction.json + session meta (小文件; /nasdata 100% 满不放全量 messages.json)
  local dest="$TRACE_BASE/$TAG"
  mkdir -p "$dest"
  if [[ -n "$gen_batch" ]]; then
    # 抽取所有 compaction.json + session .json (meta) 到 trace dest
    local sess_dir="$gen_batch/cli_data"
    if [[ -d "$sess_dir" ]]; then
      find "$sess_dir" -name "*.compaction.json" -exec cp --parents {} "$dest/" \; 2>>"$MASTER_LOG"
      find "$sess_dir" -path "*/sessions/*" -name "*.json" ! -name "*.messages.json" ! -name "*.compaction.json" -exec cp --parents {} "$dest/" \; 2>>"$MASTER_LOG"
      local n_comp=$(find "$dest" -name "*.compaction.json" 2>/dev/null | wc -l)
      log "  trace: $n_comp compaction.json + meta -> $dest/ (full sessions skipped, /nasdata full)"
    fi
  fi
  if [[ -n "$eval_batch" ]]; then
    cp -a "$eval_batch" "$dest/" 2>>"$MASTER_LOG" && log "  trace: eval_batch -> $dest/"
  fi

  # 记进 results JSON
  json_append "$cost_json"
  log "  $TAG DONE  pass=${pass_pct:-NA}%  results -> $RESULTS_JSON"

  # 清理 gen batch 释放空间 (eval root 在 /tmp, 24G 有限; cost + compaction.json 已抽取)
  if [[ -n "$gen_batch" ]]; then
    rm -rf "$gen_batch" 2>/dev/null && log "  cleaned gen_batch $gen_batch (cost+compaction.json 已存档)"
  fi

  return 0
}

# =====================================================================
# 主流程 — ABBA 反平衡: r1=basic,agentic; r2=agentic,basic; r3=basic,agentic
# 序列: C_basic_r1 → C_agentic_r1 → C_agentic_r2 → C_basic_r2 → C_basic_r3 → C_agentic_r3
# (每轮内臂序交替, 抵消时间漂移 / quota 波动对单臂的系统性偏差)
# =====================================================================
log "================ ZhuLong compaction 消融编排启动 ================"
log "base=$DS_MODEL  harness=cline 3.0.51  dataset=EDA-Eval-PyAether-158 (subset=40)  -p $PARALLEL -n  rounds/arm=$ROUNDS"
log "arms: basic (rule-fold) vs agentic (LLM summary)  thinking=medium  LANG_HINT=空"
log "ABBA 序列: basic_r1, agentic_r1, agentic_r2, basic_r2, basic_r3, agentic_r3"

run_round "C_basic_r1"    "basic"    1
run_round "C_agentic_r1"  "agentic"  1
run_round "C_agentic_r2"  "agentic"  2
run_round "C_basic_r2"    "basic"    2
run_round "C_basic_r3"    "basic"    3
run_round "C_agentic_r3"  "agentic"  3

log "================ 全部变体完成 ================"
log "results: $RESULTS_JSON"
log "traces:  $TRACE_BASE"
# 哨兵文件: 报告生成可据此触发
touch "$REPO_RUN/.ablation_compaction_DONE"
