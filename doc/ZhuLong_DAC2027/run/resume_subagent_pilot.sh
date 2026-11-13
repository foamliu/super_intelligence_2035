#!/bin/bash
# resume_subagent_pilot.sh — 恢复 subagent 消融 pilot
# 编排器 (run_subagent_ablation.sh) 在 C1 跑到一半时死了.
# C1 的 cline 进程仍在跑 (orphaned, 写 /tmp/subagent_C1_r1.log).
# 本脚本: 等 C1 完成 → 收 C1 cost/trace → 跑 C2 → 收 C2 → 跑 A1 → 收 A1.
set -uo pipefail

REPO_RUN="/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run"
BASE_DIR="/nasdata/app.e0031982/code/eda_fastmcp"
export PYTHON="${PYTHON:-/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python}"
export CLI_AGENT=cline

EVAL_ROOT_OVERRIDE="/tmp/zhulong_subagent_eval"
TRACE_BASE="/nasdata/app.e0031982/code/ZhuLong_DAC2027/trace_ablation_subagent"
ARM_DIR_ROOT="/nasdata/app.e0031982/subagent_ablation"
SUBSET_FILE="$REPO_RUN/subagent_pilot_8.txt"
MASTER_LOG="/tmp/zhulong_subagent_ablation.log"
PARALLEL=8

SUBAGENT_HINT="
## 重要：工作流程要求
在写代码之前，你**必须**先调用 \`subagent_researcher\` 工具，让它查询本任务涉及的所有 pyAether API 文档。拿到 API 文档摘要后，再开始写代码。这是强制步骤。"

log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$MASTER_LOG"; }

# TASK_FILTER (comma-separated, harness reads this not SUBSET_FILE)
export TASK_FILTER=$(tr '\n' ',' < "$SUBSET_FILE" | sed 's/,$//')
export EVAL_BENCHMARK="benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl"
export EVAL_ROOT_DIR_OVERRIDE="$EVAL_ROOT_OVERRIDE"
export SUBSET_FILE
export PARALLEL
export CLINE_COMPACTION="basic"
export CLINE_THINKING="medium"

post_process() {
  local ARM="$1" ROUND="$2" round_log="/tmp/subagent_${1}_r${2}.log"
  local cost_json="$REPO_RUN/cost_S_${ARM}_r${ROUND}.json"
  local batch_dir=$(ls -td "$EVAL_ROOT_OVERRIDE"/*/ 2>/dev/null | head -1)
  local n_tasks=$(wc -l < "$SUBSET_FILE" 2>/dev/null || echo 0)
  "$PYTHON" "$REPO_RUN/collect_subagent_cost.py" \
    --arm "$ARM" --round "$ROUND" --batch-dir "${batch_dir%/}" \
    --log "$round_log" --n-tasks "$n_tasks" --out "$cost_json" 2>&1 | tee -a "$MASTER_LOG" || log "⚠️ cost 收集失败 for $ARM"
  if [[ -n "$batch_dir" && -d "${batch_dir%/}/trace" ]]; then
    local trace_dst="$TRACE_BASE/$ARM/$(basename "${batch_dir%/}")"
    mkdir -p "$trace_dst"
    cp -a "${batch_dir%/}/trace/." "$trace_dst/" 2>/dev/null && log "  trace 归档 → $trace_dst" || log "⚠️ trace 归档失败 for $ARM"
  fi
  log "  arm=$ARM r=$ROUND post-process 完成"
}

run_arm() {
  local ARM="$1" ROUND="${2:-1}"
  local ARM_DIR="$ARM_DIR_ROOT/$ARM"
  local AGENTS_DIR="$ARM_DIR/agents"
  local round_log="/tmp/subagent_${ARM}_r${ROUND}.log"

  log "=== Round $ROUND: arm=$ARM (resume) ==="

  # 修复 providers.json (cline auto-migration 覆盖)
  python3 "$REPO_RUN/setup_subagent_arm_dirs.py" --arm "$ARM" --providers-only 2>>"$MASTER_LOG" || {
    python3 -c "
import json
template = json.load(open('/nasdata/app.e0031982/compaction_ablation/basic/settings/providers.json'))
json.dump(template, open('$ARM_DIR/settings/providers.json', 'w'), ensure_ascii=False, indent=2)
print('providers.json reset from template')
" 2>>"$MASTER_LOG"
  }

  export CLI_DATA_DIR="$ARM_DIR"
  if [[ "$ARM" != "A1" ]]; then
    export LANG_HINT="$SUBAGENT_HINT"
    [[ -d "$AGENTS_DIR" ]] && export CLINE_AGENTS_SRC="$AGENTS_DIR" || unset CLINE_AGENTS_SRC
  else
    export LANG_HINT=""
    unset CLINE_AGENTS_SRC
  fi

  log "  launching run_cline_script.sh -> $round_log"
  : > "$round_log"
  cd "$BASE_DIR"
  timeout --signal=TERM --kill-after=120 43200 bash scripts/run_cline_script.sh -p "$PARALLEL" -n >> "$round_log" 2>&1
  local exit_code=$?
  log "  arm=$ARM r=$ROUND cline 退出 (exit=$exit_code)"
  post_process "$ARM" "$ROUND"
}

# ===== Step 1: 等 C1 完成 =====
log "=========================================="
log "resume_subagent_pilot.sh 启动"
log "等待 C1 cline 完成 (log 停止增长)..."
log "=========================================="

C1_LOG="/tmp/subagent_C1_r1.log"
while true; do
  s1=$(stat -c %s "$C1_LOG" 2>/dev/null || echo 0)
  sleep 30
  s2=$(stat -c %s "$C1_LOG" 2>/dev/null || echo 0)
  delta=$((s2 - s1))
  if [[ $delta -eq 0 ]]; then
    # 二次确认 (60s 无增长 = cline 退出)
    sleep 30
    s3=$(stat -c %s "$C1_LOG" 2>/dev/null || echo 0)
    if [[ $s3 -eq $s2 ]]; then
      log "C1 log 停止增长 (size=$s2), 判定 cline 已退出"
      break
    fi
  fi
  log "  C1 仍在跑 (size=$s2, delta=${delta}/30s)..."
done

# C1 post-process
post_process "C1" "1"
log "  arm=C1 r=1 完成 (post-process)"

# ===== Step 2: 跑 C2 =====
run_arm "C2" "1"

# ===== Step 3: 跑 A1 =====
run_arm "A1" "1"

log "=========================================="
log "pilot 恢复完成: C1(post) + C2 + A1 全部完成"
log "=========================================="
