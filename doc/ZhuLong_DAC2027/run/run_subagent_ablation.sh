#!/bin/bash
# run_subagent_ablation.sh — ZhuLong subagent 消融自主编排
# 单轴: cline subagent 机制 (spawn / configured agent / 基座梯度 / maxIter) × 3 轮
#
# 臂设计 (9 臂):
#   A0: baseline (spawn off)        — 复用 compaction basic r1-r3 数据
#   A1: spawn-on (自主 spawn)
#   B1: cfg-same (同基座 dsv4-pro)
#   B2: cfg-dsv4-flash
#   B3: cfg-doubao-pro
#   B4: cfg-doubao-mini
#   B5: cfg-doubao-lite
#   C1: cfg-iter5 (maxIter=5)
#   C2: cfg-iter30 (maxIter=30)
#
# 产物: cost_S_{arm}_r{round}.json, ablation_subagent_results.json, trace_ablation_subagent/
set -euo pipefail

REPO_RUN="/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run"
BASE_DIR="/nasdata/app.e0031982/code/eda_fastmcp"
EVAL_FW="/nasdata/app.e0031982/code/EDA-Eval-Framework"
PYTHON="${PYTHON:-/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python}"

EVAL_ROOT_OVERRIDE="/tmp/zhulong_subagent_eval"   # /nasdata 100% 满; 用 /tmp (24G), 每轮清理
TRACE_BASE="/nasdata/app.e0031982/code/ZhuLong_DAC2027/trace_ablation_subagent"
RESULTS_JSON="$REPO_RUN/ablation_subagent_results.json"
SUBSET_FILE="$REPO_RUN/compaction_subset_40.txt"  # 复用 compaction 40 题子集
MASTER_LOG="/tmp/zhulong_subagent_ablation.log"

ARM_DIR_ROOT="/nasdata/app.e0031982/subagent_ablation"

PARALLEL=8
ROUNDS=3
DS_MODEL="deepseek-v4-pro-cloud"

# 强提示: 要求主 agent 先调 subagent_researcher
SUBAGENT_HINT="
## 重要：工作流程要求
在写代码之前，你**必须**先调用 \`subagent_researcher\` 工具，让它查询本任务涉及的所有 pyAether API 文档。拿到 API 文档摘要后，再开始写代码。这是强制步骤。"

log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$MASTER_LOG"; }

# 臂列表 (A0 复用, 不跑)
RUN_ARMS=("A1" "B1" "B2" "B3" "B4" "B5" "C1" "C2")

# ABBA-like 顺序: 先跑 B 系列确认 subagent 有效, 再跑 A1/C
RUN_ORDER=("B1" "B2" "B3" "B4" "B5" "C1" "C2" "A1")

run_round() {
  local ARM="$1" ROUND="$2"
  local ARM_DIR="$ARM_DIR_ROOT/$ARM"
  local AGENTS_DIR="$ARM_DIR/agents"  # researcher.yaml 所在
  local round_log="/tmp/subagent_${ARM}_r${ROUND}.log"
  local cost_json="$REPO_RUN/cost_S_${ARM}_r${ROUND}.json"

  log "=== Round $ROUND: arm=$ARM ==="

  # 验证 arm data-dir
  if [[ ! -d "$ARM_DIR/settings" ]]; then
    log "❌ arm data-dir 不存在: $ARM_DIR (先跑 setup_subagent_arm_dirs.py)"
    return 1
  fi

  # 验证 providers.json (cline auto-migration 可能重置)
  local prov="$ARM_DIR/settings/providers.json"
  if ! python3 -c "import json; d=json.load(open('$prov')); assert 'openai-compatible' in d['providers']" 2>/dev/null; then
    log "⚠️ providers.json 被重置, 重新 setup..."
    python3 "$REPO_RUN/setup_subagent_arm_dirs.py" 2>&1 | tail -3
  fi

  # 设置环境变量
  export CLI_DATA_DIR="$ARM_DIR"
  export CLINE_COMPACTION="basic"
  export CLINE_THINKING="medium"
  export LANG_HINT=""  # 轴 B 空提示
  export EVAL_BENCHMARK="benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl"
  export EVAL_ROOT_DIR="$EVAL_ROOT_OVERRIDE"
  export SUBSET_FILE
  export PARALLEL

  # 注入 configured agent (researcher.yaml)
  if [[ -d "$AGENTS_DIR" ]]; then
    export CLINE_AGENTS_SRC="$AGENTS_DIR"
    log "  CLINE_AGENTS_SRC=$AGENTS_DIR (researcher.yaml 注入)"
  else
    unset CLINE_AGENTS_SRC
    log "  无 configured agent (A1 spawn-only)"
  fi

  # 注入 subagent 强提示 (B1-B5/C1/C2 臂; A1 不注入因为没 researcher)
  if [[ "$ARM" != "A1" ]]; then
    export LANG_HINT="$SUBAGENT_HINT"
  fi

  # 启动 eval
  log "  launching run_cline_script.sh (foreground, 12h cap) -> $round_log"
  cd "$BASE_DIR"
  timeout --signal=TERM --kill-after=120 43200 bash scripts/run_cline_script.sh -p "$PARALLEL" -n >> "$round_log" 2>&1
  local exit_code=$?

  if [[ $exit_code -ne 0 && $exit_code -ne 124 ]]; then
    log "❌ arm=$ARM r=$ROUND 失败 (exit=$exit_code)"
  fi

  # 收集 cost
  local batch_dir=$(ls -td "$EVAL_ROOT_OVERRIDE"/*/ 2>/dev/null | head -1)
  if [[ -n "$batch_dir" ]]; then
    "$PYTHON" -c "
import json, os, glob, sys
# 从 trace 收集 cost 数据
cost = {'arm': '$ARM', 'round': $ROUND, 'batch': os.path.basename('${batch_dir%/}'), 'tasks': []}
# TODO: 从 session usage 收集 token 数据
json.dump(cost, open('$cost_json', 'w'), indent=2)
print(f'cost saved: $cost_json')
" 2>&1 || log "⚠️ cost 收集失败"
  fi

  log "  arm=$ARM r=$ROUND 完成 (exit=$exit_code)"
}

# ===== main =====
mkdir -p "$EVAL_ROOT_OVERRIDE" "$TRACE_BASE"
log "=========================================="
log "ZhuLong Subagent 消融实验启动"
log "base=$DS_MODEL  harness=cline 3.0.51  dataset=EDA-Eval-PyAether-158 (subset=40)"
log "-p $PARALLEL  rounds/arm=$ROUNDS  arms=${#RUN_ARMS[@]}"
log "=========================================="

# 预检
if [[ ! -f "$SUBSET_FILE" ]]; then
  log "❌ 子集文件不存在: $SUBSET_FILE"
  exit 1
fi
if [[ ! -d "$ARM_DIR_ROOT/A1" ]]; then
  log "❌ arm data-dir 未建, 先跑 setup_subagent_arm_dirs.py"
  exit 1
fi

# 沙盒端口检查
for port in 8664 8665 8653 8669; do
  if ! timeout 2 bash -c "echo > /dev/tcp/127.0.0.1/$port" 2>/dev/null; then
    log "⚠️ 沙盒端口 $port 不可达"
  fi
done

# 主循环
RESULTS=()
for round in $(seq 1 $ROUNDS); do
  for arm in "${RUN_ORDER[@]}"; do
    run_round "$arm" "$round"
  done
done

log "=========================================="
log "全部 $ROUNDS 轮 × ${#RUN_ARMS[@]} 臂完成"
log "=========================================="
