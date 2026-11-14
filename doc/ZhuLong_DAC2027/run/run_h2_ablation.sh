#!/bin/bash
# run_h2_ablation.sh — ZhuLong H2 sub-agent weak-model gradient ablation
# Patches cline (v3.0.74 + commit 39ccd44cc) lets spawned sub-agents use a WEAK model via env,
#   and inherit parent MCP tools (CLINE_SUBAGENT_INHERIT_MCP=1).
# Arms (all on H2 wrapper, anonymous spawn_agent, NO researcher.yaml, INHERIT_MCP=1, 40-task subset):
#   B1: sub inherits parent (deepseek-v4-pro-cloud) — gradient strong end / anchor
#   B2: sub = deepseek-v4-flash        (key c43c1f4a on /v1 — NOT /cloud/v1 which 403s)
#   B3: sub = doubao-seed-2.0-pro-cloud
#   B4: sub = doubao-seed-2.0-mini-cloud
#   B5: sub = doubao-seed-2.0-lite-cloud      — gradient weak end
# Main agent ALWAYS = deepseek-v4-pro-cloud (openai-compatible). 3 rounds/arm, -p 8 -n, compaction=basic, thinking=medium.
# Pre-registered H2 judgment: B1 vs B3-B5 Δ≥3pp + bootstrap CI not crossing 0 + gradient regression R²>0.7 + B5 per-pass token drop ≥20%.
set -uo pipefail

REPO_RUN="/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run"
BASE_DIR="/nasdata/app.e0031982/code/eda_fastmcp"
EVAL_FW="/nasdata/app.e0031982/code/EDA-Eval-Framework"
export PYTHON="${PYTHON:-/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python}"

ARM_DIR_ROOT="/nasdata/app.e0031982/subagent_ablation"
A1_DIR="$ARM_DIR_ROOT/A1"   # shared CLI_DATA_DIR for all H2 arms (main=dsv4-pro; sub model is env-driven)

EVAL_ROOT_OVERRIDE="/tmp/zhulong_h2_eval"        # /nasdata space control; cleaned per round
TRACE_BASE="/tmp/zhulong_h2_trace"
RESULTS_JSON="$REPO_RUN/ablation_h2_results.json"
SUBSET_FILE="${SUBSET_FILE:-$REPO_RUN/compaction_subset_40.txt}"
MASTER_LOG="/tmp/zhulong_h2_ablation_master.log"

PARALLEL=8
ROUNDS="${ROUNDS:-3}"

# ===== per-arm sub-agent model config =====
# Format: "ARM|PROVIDER_ID|MODEL_ID|API_KEY|BASE_URL"  (empty fields => inherit parent)
declare -A ARM_SUB
ARM_SUB["B1"]="|||"                                              # sub = parent (dsv4-pro)
ARM_SUB["B2"]="openai-compatible|deepseek-v4-flash|02_088EE9051AAE4BF0ABFC7130331BF697_c43c1f4a-03c6-4148-b722-f4c8604c78d3|http://agi-gateway.cxmt.com/v1"
ARM_SUB["B3"]="openai-compatible|doubao-seed-2.0-pro-cloud|02_088EE9051AAE4BF0ABFC7130331BF697_3dd97aea-258e-4a53-a290-4f1425cdc15f|http://agi-gateway.cxmt.com/cloud/v1"
ARM_SUB["B4"]="openai-compatible|doubao-seed-2.0-mini-cloud|02_088EE9051AAE4BF0ABFC7130331BF697_caa8bffa-b976-47f5-acc3-4141f6c5b90f|http://agi-gateway.cxmt.com/cloud/v1"
ARM_SUB["B5"]="openai-compatible|doubao-seed-2.0-lite-cloud|02_088EE9051AAE4BF0ABFC7130331BF697_78b81092-7e90-436e-aa8a-5ab8510567fe|http://agi-gateway.cxmt.com/cloud/v1"

RUN_ORDER=(B1 B2 B3 B4 B5)

# ===== SUBAGENT_HINT (same as run_subagent_ablation.sh — forces spawn_agent) =====
SUBAGENT_HINT="
## CRITICAL WORKFLOW REQUIREMENT
Before writing any code, you MUST use the \`spawn_agent\` tool to delegate to a researcher sub-agent.
Call \`spawn_agent\` with a systemPrompt describing a pyAether API researcher, and a task asking it to
look up the pyAether APIs relevant to this problem using the search_apis and get_api_details tools.
Do NOT answer directly or write code until the sub-agent returns its findings. This is a mandatory step."

log() { echo "[$(date '+%F %H:%M:%S')] $*" | tee -a "$MASTER_LOG"; }

setup_arm_env() {
  local ARM="$1"
  local cfg="${ARM_SUB[$ARM]}"
  # clear then set
  unset CLINE_SUBAGENT_PROVIDER_ID CLINE_SUBAGENT_MODEL_ID CLINE_SUBAGENT_API_KEY CLINE_SUBAGENT_BASE_URL
  export CLINE_SUBAGENT_INHERIT_MCP=1   # ALL H2 arms: sub inherits parent MCP tools (the bug fix)
  if [[ "$cfg" == "|||" ]]; then
    log "  arm=$ARM: sub=parent (no CLINE_SUBAGENT_* override) INHERIT_MCP=1"
  else
    IFS='|' read -r pid mid key url <<< "$cfg"
    export CLINE_SUBAGENT_PROVIDER_ID="$pid"
    export CLINE_SUBAGENT_MODEL_ID="$mid"
    export CLINE_SUBAGENT_API_KEY="$key"
    export CLINE_SUBAGENT_BASE_URL="$url"
    log "  arm=$ARM: sub=$mid INHERIT_MCP=1"
  fi
}

run_round() {
  local ARM="$1" ROUND="$2"
  local round_log="/tmp/h2_${ARM}_r${ROUND}.log"
  local cost_json="$REPO_RUN/cost_H2_${ARM}_r${ROUND}.json"

  log "=== Round $ROUND: arm=$ARM ==="
  setup_arm_env "$ARM"

  # common env
  export CLI_DATA_DIR="$A1_DIR"
  export CLI_AGENT=cline
  export CLINE_COMPACTION="basic"
  export CLINE_THINKING="medium"
  export LANG_HINT="$SUBAGENT_HINT"
  export CLINE_UNIFIED_DATA_DIR=1
  export EVAL_BENCHMARK="benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl"
  export EVAL_ROOT_DIR_OVERRIDE="$EVAL_ROOT_OVERRIDE"
  export SUBSET_FILE
  export PARALLEL
  unset CLINE_AGENTS_SRC   # anonymous spawn, no configured agent
  # H2 wrapper FIRST on PATH (use /home wrapper — stable across /tmp cleanup; identical to /tmp/cline-h2)
  export PATH="/home/app.e0031982/.local/bin/h2:/tmp/cline-h2/bin:/nasdata/app.e0031982/code/eda_fastmcp/venv/bin:/home/app.e0031982/.local/node-20/bin:${PATH}"
  export NO_PROXY="agi-gateway.cxmt.com,10.129.32.75,10.251.36.15,localhost,127.0.0.1"
  unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY

  # ensure A1 providers.json is the dsv4-pro template (cline auto-migration guard)
  if ! grep -q 'deepseek-v4-pro-cloud' "$A1_DIR/settings/providers.json" 2>/dev/null; then
    log "  ⚠️ A1 providers.json missing dsv4-pro; restoring from compaction basic template"
    python3 -c "
import json
t=json.load(open('/nasdata/app.e0031982/compaction_ablation/basic/settings/providers.json'))
json.dump(t, open('$A1_DIR/settings/providers.json','w'), ensure_ascii=False, indent=2)
"
  fi

  : > "$round_log"
  log "  launching run_cline_script.sh -p $PARALLEL -n (foreground, 12h cap) -> $round_log  (cline v$(cline --version 2>&1|head -1))"
  cd "$BASE_DIR"
  timeout --signal=TERM --kill-after=120 43200 bash scripts/run_cline_script.sh -p "$PARALLEL" -n >> "$round_log" 2>&1
  local ec=$?
  log "  arm=$ARM r=$ROUND harness exit=$ec"

  # cost + spawn collection
  local batch_dir=$(ls -td "$EVAL_ROOT_OVERRIDE"/*/ 2>/dev/null | head -1)
  local n_tasks=$(wc -l < "$SUBSET_FILE" 2>/dev/null || echo 0)
  "$PYTHON" "$REPO_RUN/collect_subagent_cost.py" \
    --arm "$ARM" --round "$ROUND" --batch-dir "${batch_dir%/}" \
    --log "$round_log" --n-tasks "$n_tasks" --out "$cost_json" 2>&1 | tee -a "$MASTER_LOG" || log "  ⚠️ cost collection failed"

  # trace archive
  if [[ -n "$batch_dir" && -d "${batch_dir%/}/code" ]]; then
    local trace_dst="$TRACE_BASE/$ARM/$(basename "${batch_dir%/}")"
    mkdir -p "$trace_dst"
    cp -a "${batch_dir%/}/code/." "$trace_dst/" 2>/dev/null && log "  trace archived -> $trace_dst" || log "  ⚠️ trace archive failed"
  fi
  # cleanup old batches (keep current; /tmp space control)
  for _old in "$EVAL_ROOT_OVERRIDE"/*/; do
    [[ "$_old" == "$batch_dir" ]] && continue
    [[ -d "$_old" ]] && rm -rf "$_old"
  done
  log "  arm=$ARM r=$ROUND DONE"
}

# ===== main =====
mkdir -p "$EVAL_ROOT_OVERRIDE" "$TRACE_BASE" "$A1_DIR/settings"
log "=========================================="
log "ZhuLong H2 sub-agent weak-model gradient ablation"
log "wrapper=cline v3.0.74 (commit 39ccd44cc)  main=deepseek-v4-pro-cloud  INHERIT_MCP=1 (all arms)"
log "subset=$(wc -l < "$SUBSET_FILE" 2>/dev/null)  -p $PARALLEL  rounds/arm=$ROUNDS  arms=${RUN_ORDER[*]}"
log "B2 dsv4-flash uses /v1 (not /cloud/v1).  RESULTS -> $RESULTS_JSON  trace -> $TRACE_BASE"
log "=========================================="

if [[ ! -f "$SUBSET_FILE" ]]; then log "❌ subset missing: $SUBSET_FILE"; exit 1; fi
if [[ ! -d "$A1_DIR/settings" ]]; then log "❌ A1 dir missing"; exit 1; fi

# TASK_FILTER from subset (harness reads TASK_FILTER, comma-sep)
TASK_FILTER=$(tr '\n' ',' < "$SUBSET_FILE" | sed 's/,$//')
export TASK_FILTER
log "TASK_FILTER: ${#TASK_FILTER} chars, $(wc -l < "$SUBSET_FILE") tasks"

for round in $(seq 1 $ROUNDS); do
  for arm in "${RUN_ORDER[@]}"; do
    run_round "$arm" "$round"
  done
done

log "=========================================="
log "ALL $ROUNDS rounds × ${#RUN_ORDER[@]} arms DONE. Run analyze_h2_results.py next."
log "=========================================="
