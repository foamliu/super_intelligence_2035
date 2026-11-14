#!/bin/bash
# run_subagent_ablation_a2.sh — ZhuLong subagent 消融 · A2 臂 (验证型 QA spawn)
#
# 🔴 用户令 2026-11-14 18:3x: A1 强提示方向错了 → 改为 spawn「验证 agent」+ 对抗视角
#   A1 = 原配置 (调研型 spawn + researcher 强提示) — 保持原样把 3 轮跑完 (run_subagent_ablation.sh)
#   A2 = 新配置 (验证型 QA spawn + adversarial 提示, 触发点=代码写好未提交前) — 独立新臂, 3 轮
#   A2 臂配置与 A1 完全一致, 唯一差异 = spawn 提示 (触发点 + 角色 + 任务)
#
# 本脚本是 run_subagent_ablation.sh 的 arm-hint-aware 变体:
#   - A1 → researcher hint (旧, 调研型, 写代码前 spawn)
#   - A2 → verifier hint  (新, 对抗 QA, 写完代码未提交前 spawn) — 从 subagent_hint_a2.txt 读取
#   - RUN_ORDER 默认只跑 A2; 可用 RUN_ORDER_OVERRIDE=A1,A2 覆盖 (例如回滚重跑 A1)
#   - 其余全臂恒定: compaction=basic, thinking=medium, LANG_HINT 空(轴B), -p 8 -n, 主基座 deepseek-v4-pro-cloud
#
# 产物: cost_S_{arm}_r{round}.json, ablation_subagent_results.json, trace_ablation_subagent/
set -euo pipefail

REPO_RUN="/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run"
BASE_DIR="/nasdata/app.e0031982/code/eda_fastmcp"
EVAL_FW="/nasdata/app.e0031982/code/EDA-Eval-Framework"
export PYTHON="${PYTHON:-/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python}"

export CLI_AGENT=cline

EVAL_ROOT_OVERRIDE="/tmp/zhulong_subagent_eval"   # /nasdata 100% 满; 用 /tmp (24G), 每轮清理
TRACE_BASE="/tmp/zhulong_subagent_trace"           # /nasdata 99% 满 → trace 落 /tmp 并按轮归档
RESULTS_JSON="$REPO_RUN/ablation_subagent_results.json"
SUBSET_FILE="${SUBSET_FILE:-$REPO_RUN/compaction_subset_40.txt}"  # 复用 compaction 40 题子集
MASTER_LOG="/tmp/zhulong_subagent_ablation_a2.log"

ARM_DIR_ROOT="/nasdata/app.e0031982/subagent_ablation"

PARALLEL=8
ROUNDS="${ROUNDS:-3}"
DS_MODEL="deepseek-v4-pro-cloud"

# ===== arm-specific spawn hints =====
# A1 = 旧提示 (调研型 researcher, 写代码前 spawn) — 与 run_subagent_ablation.sh 完全一致, 仅供回滚对比
SUBAGENT_HINT_A1="
## CRITICAL WORKFLOW REQUIREMENT
Before writing any code, you MUST use the \`spawn_agent\` tool to delegate to a researcher sub-agent.
Call \`spawn_agent\` with a systemPrompt describing a pyAether API researcher, and a task asking it to
look up the pyAether APIs relevant to this problem using the search_apis and get_api_details tools.
Do NOT answer directly or write code until the sub-agent returns its findings. This is a mandatory step."

# A2 = 新提示 (对抗型 verifier, 写完代码未提交前 spawn) — 从 subagent_hint_a2.txt 读取
SUBAGENT_HINT_A2_FILE="$REPO_RUN/subagent_hint_a2.txt"
if [[ -f "$SUBAGENT_HINT_A2_FILE" ]]; then
  SUBAGENT_HINT_A2=$(cat "$SUBAGENT_HINT_A2_FILE")
else
  echo "❌ A2 hint 文件不存在: $SUBAGENT_HINT_A2_FILE" >&2
  exit 1
fi

# 按臂名选 hint
hint_for_arm() {
  case "$1" in
    A1) echo "$SUBAGENT_HINT_A1" ;;
    A2) echo "$SUBAGENT_HINT_A2" ;;
    *)  echo "❌ 未知臂 $1, 无 hint" >&2; return 1 ;;
  esac
}

log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$MASTER_LOG"; }

# 臂列表 (A0 复用, 不跑; 本脚本默认跑 A2; A1 可通过 RUN_ORDER_OVERRIDE 回滚)
RUN_ARMS=("A2")

# RUN_ORDER: 默认只跑 A2; env 可覆盖 (逗号分隔, 如 "A2" 或 "A1,A2")
if [[ -n "${RUN_ORDER_OVERRIDE:-}" ]]; then
  IFS=',' read -ra RUN_ORDER <<< "$RUN_ORDER_OVERRIDE"
else
  RUN_ORDER=("A2")
fi

run_round() {
  local ARM="$1" ROUND="$2"
  local ARM_DIR="$ARM_DIR_ROOT/$ARM"
  local AGENTS_DIR="$ARM_DIR/agents"  # configured agent (A2 无, spawn-only)
  local round_log="/tmp/subagent_${ARM}_r${ROUND}.log"
  local cost_json="$REPO_RUN/cost_S_${ARM}_r${ROUND}.json"

  log "=== Round $ROUND: arm=$ARM ==="

  # 验证 arm data-dir
  if [[ ! -d "$ARM_DIR/settings" ]]; then
    log "❌ arm data-dir 不存在: $ARM_DIR (先跑 setup_subagent_arm_dirs.py 或 cp A1)"
    return 1
  fi

  # ⚠️ 关键: cline auto-migration 会覆盖 providers.json, 每轮前重新写入
  python3 "$REPO_RUN/setup_subagent_arm_dirs.py" --arm "$ARM" --providers-only 2>>"$MASTER_LOG" || {
    log "  ⚠️ providers.json 修复失败 (A2 未在 setup 脚本臂列表, 走 inline fallback), 用 inline python 修复"
    python3 -c "
import json, os, copy
template = json.load(open('/nasdata/app.e0031982/compaction_ablation/basic/settings/providers.json'))
p = '$ARM_DIR/settings/providers.json'
json.dump(template, open(p, 'w'), ensure_ascii=False, indent=2)
print('providers.json reset from compaction basic template (A2 fallback)')
"
  }

  # 验证 providers.json (主基座 dsv4-pro 恒定)
  local prov="$ARM_DIR/settings/providers.json"
  if ! grep -q '/cloud/v1' "$prov" 2>/dev/null || ! grep -q 'deepseek-v4-pro-cloud' "$prov" 2>/dev/null; then
    log "  ❌ $ARM providers.json 修复后仍不对 (缺 /cloud/v1 或 dsv4-pro 主基座), 跳过此轮"
    return 1
  fi

  # 设置环境变量 (全臂恒定, 与 A1 完全一致)
  export CLI_DATA_DIR="$ARM_DIR"
  export CLINE_COMPACTION="basic"
  export CLINE_THINKING="medium"
  # 🔑 轴 B 空 hint (LANG_HINT 基线) — 但 spawn 臂用 arm-specific hint 覆盖 (见下)
  export CLINE_UNIFIED_DATA_DIR=1
  export EVAL_BENCHMARK="benchmarks/EDA-Eval-pyAether/EDA-Eval-PyAether-158.jsonl"
  export EVAL_ROOT_DIR_OVERRIDE="$EVAL_ROOT_OVERRIDE"
  export SUBSET_FILE
  export PARALLEL

  # 注入 configured agent (A1/A2 均为 spawn-only, 无 configured agent)
  if [[ -d "$AGENTS_DIR" ]]; then
    export CLINE_AGENTS_SRC="$AGENTS_DIR"
    log "  CLINE_AGENTS_SRC=$AGENTS_DIR"
  else
    unset CLINE_AGENTS_SRC
    log "  无 configured agent ($ARM spawn-only)"
  fi

  # 🔑 arm-specific spawn hint (A1=researcher 旧, A2=verifier 新)
  local hint
  hint=$(hint_for_arm "$ARM") || { log "❌ 无法获取 $ARM hint"; return 1; }
  export LANG_HINT="$hint"
  log "  hint=$(echo "$hint" | head -1) ... ($(echo "$hint" | wc -l) lines)"

  # 启动 eval
  log "  launching run_cline_script.sh (foreground, 12h cap) -> $round_log"
  : > "$round_log"   # truncate: 避免上一轮残留污染 cost 收集
  cd "$BASE_DIR"
  timeout --signal=TERM --kill-after=120 43200 bash scripts/run_cline_script.sh -p "$PARALLEL" -n >> "$round_log" 2>&1
  local exit_code=$?

  if [[ $exit_code -ne 0 && $exit_code -ne 124 ]]; then
    log "❌ arm=$ARM r=$ROUND 失败 (exit=$exit_code)"
  fi

  # 收集 cost + spawn 调用率 + trace 归档
  local batch_dir=$(ls -td "$EVAL_ROOT_OVERRIDE"/*/ 2>/dev/null | head -1)
  local n_tasks=$(wc -l < "$SUBSET_FILE" 2>/dev/null || echo 0)
  "$PYTHON" "$REPO_RUN/collect_subagent_cost.py" \
    --arm "$ARM" --round "$ROUND" --batch-dir "${batch_dir%/}" \
    --log "$round_log" --n-tasks "$n_tasks" --out "$cost_json" 2>&1 | tee -a "$MASTER_LOG" || log "⚠️ cost 收集失败"

  # trace 归档
  if [[ -n "$batch_dir" && -d "${batch_dir%/}/code" ]]; then
    local trace_dst="$TRACE_BASE/$ARM/$(basename "${batch_dir%/}")"
    mkdir -p "$trace_dst"
    cp -a "${batch_dir%/}/code/." "$trace_dst/" 2>/dev/null && log "  trace 归档 → $trace_dst" || log "⚠️ trace 归档失败"
  fi
  # 清理旧 batch (保留当前轮; /tmp 空间控制)
  for _old in "$EVAL_ROOT_OVERRIDE"/*/; do
    [[ "$_old" == "${batch_dir}" ]] && continue
    [[ -d "$_old" ]] && rm -rf "$_old" && log "  清理旧 batch: $(basename "${_old%/}")"
  done

  log "  arm=$ARM r=$ROUND 完成 (exit=$exit_code)"
}

# ===== main =====
mkdir -p "$EVAL_ROOT_OVERRIDE" "$TRACE_BASE"
log "=========================================="
log "ZhuLong Subagent 消融 · A2 臂 (验证型 QA spawn)"
log "base=$DS_MODEL  harness=cline 3.0.51  dataset=EDA-Eval-PyAether-158 (subset=40)"
log "-p $PARALLEL  rounds/arm=$ROUNDS  arms=${#RUN_ORDER[@]}  order=${RUN_ORDER[*]}"
log "=========================================="

# TASK_FILTER 转换 (与原脚本一致)
if [[ -n "$SUBSET_FILE" ]]; then
  TASK_FILTER=$(tr '\n' ',' < "$SUBSET_FILE" | sed 's/,$//')
  export TASK_FILTER
  log "子集: ${SUBSET_FILE##*/} ($(wc -l < "$SUBSET_FILE") tasks) TASK_FILTER 长度=${#TASK_FILTER}"
fi

# 预检
if [[ ! -f "$SUBSET_FILE" ]]; then
  log "❌ 子集文件不存在: $SUBSET_FILE"
  exit 1
fi
for arm in "${RUN_ORDER[@]}"; do
  if [[ ! -d "$ARM_DIR_ROOT/$arm" ]]; then
    log "❌ arm data-dir 未建: $ARM_DIR_ROOT/$arm"
    exit 1
  fi
done

# 沙盒端口检查
for port in 8664 8665 8653 8669; do
  if ! timeout 2 bash -c "echo > /dev/tcp/127.0.0.1/$port" 2>/dev/null; then
    log "⚠️ 沙盒端口 $port 不可达"
  fi
done

# 主循环
for round in $(seq 1 $ROUNDS); do
  for arm in "${RUN_ORDER[@]}"; do
    run_round "$arm" "$round"
  done
done

log "=========================================="
log "全部 $ROUNDS 轮 × ${#RUN_ORDER[@]} 臂完成 (A2)"
log "=========================================="
