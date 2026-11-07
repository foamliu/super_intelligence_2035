#!/bin/bash
# =====================================================================
# run_think_lang_ablation.sh — ZhuLong 两轴消融自主编排
# 轴 A: cline --thinking 档位 (none/low/medium/high/xhigh) × 3 轮
# 轴 B: 思维链语言 (en/zh/es/fr/ru, thinking 固定 medium) × 3 轮
# 基座恒定: glm-5.2 (cline CLI 3.0.51, PyAether 158, -p 8 -n, Pass@1)
# 设计: 单轴扫描(不做笛卡尔积), 每轮全量 158 题, 串行, 可恢复
# =====================================================================
set -uo pipefail

# ---------- 路径 / 常量 ----------
REPO_RUN="/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run"
BASE_DIR="/nasdata/app.e0031982/code/eda_fastmcp"
EVAL_FW="/nasdata/app.e0031982/code/EDA-Eval-Framework"
EVAL_ROOT_OVERRIDE="/nasdata/app.e0031982/code/eda_code_eval"   # 大盘, 避免 /home 撑爆
TRACE_BASE="/nasdata/app.e0031982/code/ZhuLong_DAC2027/trace_ablation_think_lang"
RESULTS_JSON="$REPO_RUN/ablation_think_lang_results.json"
EXTRACT="$REPO_RUN/extract_cost.py"
MASTER_LOG="/tmp/zhulong_think_lang_ablation.log"
PYTHON="/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python"
ROUNDS="${ROUNDS:-3}"                                            # 每变体轮数 (默认 3)

mkdir -p "$TRACE_BASE" "$EVAL_ROOT_OVERRIDE"
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$MASTER_LOG"; }

# ---------- 环境 (cline 必须不走代理访问内部 gateway) ----------
export PATH="/home/app.e0031982/.local/node-20/bin:$PATH"
export CLI_AGENT=cline                  # ③ cline harness (基线口径)
export EVAL_FW_DIR="$EVAL_FW"
export EVAL_ROOT_DIR_OVERRIDE="$EVAL_ROOT_OVERRIDE"
export PYTHON="$BASE_DIR/venv/bin/python"   # venv (含 pydantic 等), 否则 run_python_script 退回 bare python 缺包
export NO_PROXY="agi-gateway.cxmt.com,10.129.32.75,localhost,127.0.0.1"
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY   # cline 直连内部 gateway

# ---------- 变体定义 ----------
# 轴 A: thinking 档位 (LANG_HINT 空)
THINK_LEVELS=(none low medium high xhigh)
# 轴 B: 思维链语言 (CLINE_THINKING=medium)
declare -A LANG_HINT_FOR=(
  [en]="Think in English."
  [zh]="请使用中文思考。"
  [es]="Piensa en español."
  [fr]="Réfléchis en français."
  [ru]="Думай по-русски."
)
LANGS=(en zh es fr ru)

# ---------- 结果 JSON 追加 (幂等: 已存在 TAG 跳过) ----------
json_has_tag() { "$PYTHON" -c "
import json,sys
try:
    d=json.load(open('$RESULTS_JSON'))
except Exception:
    d={'rounds':[]}
print(1 if any(r.get('tag')=='$1' for r in d.get('rounds',[])) else 0)
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
  local cap=28800  # 8h 硬上限
  local t=0
  while pgrep -f '^bash scripts/run_cline_script' >/dev/null 2>&1; do
    sleep 60; t=$((t+60))
    if [[ $t -ge $cap ]]; then
      log "  ⚠️ round 超过 ${cap}s 仍 in-progress, 继续等 (不强制 kill, 让 pipeline 自然收口)"
      return 0
    fi
  done
  log "  round pipeline 结束 (waited ~${t}s)"
  return 0
}

# ---------- 找本轮最新 gen batch 目录 ----------
newest_gen_batch() {
  ls -dt "$EVAL_ROOT_OVERRIDE"/2026_* 2>/dev/null | head -1
}

# ---------- 找本轮最新 eval output_evaluation batch ----------
newest_eval_batch() {
  ls -dt "$EVAL_FW"/output_evaluation/2026*_app.e0031982 2>/dev/null | head -1
}

# ---------- 跑一轮 ----------
run_round() {
  local TAG="$1"      # e.g. A_none_r1
  local THINK="$2"    # none|low|medium|high|xhigh 或 "medium"
  local HINT="$3"     # 语言后缀 (轴 A 为空)

  if [[ "$(json_has_tag "$TAG")" == "1" ]]; then
    log ">>> SKIP $TAG (已在 results JSON, 幂等跳过)"
    return 0
  fi

  # 前置: 不打断在跑的评测 (用 ^锚定, 避免误匹配 opencode agent 的长 cmdline)
  if pgrep -f '^bash scripts/run_cline_script' >/dev/null 2>&1; then
    log ">>> WAIT $TAG: 有其他评测在跑, 等其结束"
    wait_round_done
  fi

  log ">>> START $TAG  (thinking=$THINK  lang_hint=${HINT:+<set>})"

  # 记录本轮开始前的最新 batch (用于事后 diff 找新 batch)
  local before_gen before_eval
  before_gen=$(newest_gen_batch)
  before_eval=$(newest_eval_batch)

  # 注入环境
  export CLINE_THINKING="$THINK"
  export LANG_HINT="$HINT"
  export PARALLEL=8

  local round_log="/tmp/ABL_${TAG}.log"
  : > "$round_log"

  # 启动并前台等待 (orchestrator 自身已 setsid 长驻, 前台阻塞安全; timeout 8h 硬上限)
  cd "$BASE_DIR"
  log "  launching run_cline_script.sh (foreground, 8h cap) -> $round_log"
  timeout --signal=TERM --kill-after=120 28800 bash scripts/run_cline_script.sh -p 8 -n >> "$round_log" 2>&1
  local ec=$?
  if [[ $ec -eq 124 ]]; then
    log "  ⚠️ $TAG round 命中 8h 超时上限 (timeout=124)"
  fi
  # 兜底清理可能残留的 worker
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

  # trace 保留 (gen batch cli_data + eval output)
  local dest="$TRACE_BASE/$TAG"
  mkdir -p "$dest"
  if [[ -n "$gen_batch" ]]; then
    cp -a "$gen_batch" "$dest/" 2>>"$MASTER_LOG" && log "  trace: gen_batch -> $dest/ ($(du -sh "$gen_batch" 2>/dev/null | cut -f1))"
  fi
  if [[ -n "$eval_batch" ]]; then
    cp -a "$eval_batch" "$dest/" 2>>"$MASTER_LOG" && log "  trace: eval_batch -> $dest/"
  fi

  # 记进 results JSON
  json_append "$cost_json"
  log "  $TAG DONE  pass=${pass_pct:-NA}%  results -> $RESULTS_JSON"

  # 清理 gen batch 释放空间 (DEST 已存档; eval output 保留在 EVAL_FW)
  if [[ -n "$gen_batch" && -d "$dest/$(basename "$gen_batch")" ]]; then
    rm -rf "$gen_batch" 2>/dev/null && log "  cleaned gen_batch $gen_batch (已存档至 DEST)"
  fi

  return 0
}

# =====================================================================
# 主流程
# =====================================================================
log "================ ZhuLong think×lang 消融编排启动 ================"
log "base=glm-5.2  harness=cline 3.0.51  dataset=EDA-Eval-PyAether 158  -p 8 -n  rounds/variant=$ROUNDS"
log "轴 A: ${THINK_LEVELS[*]}  轴 B: ${LANGS[*]} (thinking=medium)"

# 轴 A: thinking 扫描 (LANG_HINT 空)
for lvl in "${THINK_LEVELS[@]}"; do
  for r in $(seq 1 "$ROUNDS"); do
    run_round "A_${lvl}_r${r}" "$lvl" ""
  done
done

# 轴 B: 语言扫描 (thinking 固定 medium)
for lang in "${LANGS[@]}"; do
  hint="${LANG_HINT_FOR[$lang]}"
  for r in $(seq 1 "$ROUNDS"); do
    run_round "B_${lang}_r${r}" "medium" "$hint"
  done
done

log "================ 全部变体完成 ================"
log "results: $RESULTS_JSON"
log "traces:  $TRACE_BASE"
# 哨兵文件: 报告生成可据此触发
touch "$REPO_RUN/.ablation_think_lang_DONE"
