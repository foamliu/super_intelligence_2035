#!/bin/bash
# rerun_doubao_arms.sh — 重跑 B3/B4/B5 (doubao) with fixed tokenSource="manual"
set -euo pipefail

REPO_RUN="/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run"
BASE_DIR="/nasdata/app.e0031982/code/eda_fastmcp"
export PYTHON="/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python"
export CLI_AGENT=cline
EVAL_ROOT_OVERRIDE="/tmp/zhulong_subagent_eval"
TRACE_BASE="/nasdata/app.e0031982/code/ZhuLong_DAC2027/trace_ablation_subagent"
SUBSET_FILE="$REPO_RUN/subagent_pilot8.txt"
ARM_DIR_ROOT="/nasdata/app.e0031982/subagent_ablation"
MASTER_LOG="/tmp/zhulong_subagent_ablation.log"
PARALLEL=8
export PATH="/home/app.e0031982/.local/node-20/bin:$PATH"
export NO_PROXY="agi-gateway.cxmt.com,10.129.32.75,localhost,127.0.0.1"
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY

SUBAGENT_HINT="
## 重要：工作流程要求
在写代码之前，你**必须**先调用 \`subagent_researcher\` 工具，让它查询本任务涉及的所有 pyAether API 文档。拿到 API 文档摘要后，再开始写代码。这是强制步骤。"

log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$MASTER_LOG"; }

RERUN_ARMS=("B3" "B4" "B5")
TASK_FILTER=$(tr '\n' ',' < "$SUBSET_FILE" | sed 's/,$//')
export TASK_FILTER
log "rerun doubao arms: ${RERUN_ARMS[*]}  subset=$(wc -l < $SUBSET_FILE) tasks"

run_arm() {
  local ARM="$1"
  local ARM_DIR="$ARM_DIR_ROOT/$ARM"
  local AGENTS_DIR="$ARM_DIR/agents"
  local round_log="/tmp/subagent_${ARM}_r1.log"
  local cost_json="$REPO_RUN/cost_S_${ARM}_r1.json"

  log "=== arm=$ARM (doubao rerun) ==="
  python3 "$REPO_RUN/setup_subagent_arm_dirs.py" --arm "$ARM" --providers-only 2>>"$MASTER_LOG"

  export CLI_DATA_DIR="$ARM_DIR"
  export CLINE_COMPACTION="basic"
  export CLINE_THINKING="medium"
  export LANG_HINT="$SUBAGENT_HINT"
  export EVAL_BENCHMARK="benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl"
  export EVAL_ROOT_DIR_OVERRIDE="$EVAL_ROOT_OVERRIDE"
  export SUBSET_FILE
  export PARALLEL
  export CLINE_AGENTS_SRC="$AGENTS_DIR"

  : > "$round_log"
  cd "$BASE_DIR"
  log "  launching -> $round_log"
  timeout --signal=TERM --kill-after=120 43200 bash scripts/run_cline_script.sh -p "$PARALLEL" -n >> "$round_log" 2>&1
  local exit_code=$?
  log "  arm=$ARM exit=$exit_code"

  local batch_dir=$(ls -td "$EVAL_ROOT_OVERRIDE"/*/ 2>/dev/null | head -1)
  local n_tasks=$(wc -l < "$SUBSET_FILE" 2>/dev/null || echo 0)
  "$PYTHON" "$REPO_RUN/collect_subagent_cost.py" \
    --arm "$ARM" --round 1 --batch-dir "${batch_dir%/}" \
    --log "$round_log" --n-tasks "$n_tasks" --out "$cost_json" 2>&1 | tee -a "$MASTER_LOG" || log "  cost fail"

  if [[ -n "$batch_dir" && -d "${batch_dir%/}/trace" ]]; then
    local trace_dst="$TRACE_BASE/$ARM/$(basename "${batch_dir%/}")"
    rm -rf "$trace_dst"; mkdir -p "$trace_dst"
    cp -a "${batch_dir%/}/trace/." "$trace_dst/" 2>/dev/null && log "  trace → $trace_dst" || log "  trace fail"
  fi
  log "  arm=$ARM done"
}

mkdir -p "$EVAL_ROOT_OVERRIDE" "$TRACE_BASE"
for arm in "${RERUN_ARMS[@]}"; do
  run_arm "$arm"
done
log "=========================================="
log "doubao rerun 完成: ${RERUN_ARMS[*]}"
log "=========================================="
