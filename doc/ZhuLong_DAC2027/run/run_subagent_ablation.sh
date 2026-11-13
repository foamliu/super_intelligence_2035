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
export PYTHON="${PYTHON:-/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python}"

# 🔑 关键修复 2026-11-13: 必须用 cline (act 模式), 不能用 zhulong (-y yolo 模式).
#   yolo 预设 enableSpawnAgent=false (presets.ts:106) → subagent_researcher 工具不注册 → 调用率 0%.
#   cline 路径 run_cli.sh 不传 -y → act 预设 enableSpawnAgent=true → 工具注册 → spawn 生效.
#   smoke 验证: act 模式下 [subagent_researcher] 工具被成功调用 (2026-11-13 22:40).
export CLI_AGENT=cline

EVAL_ROOT_OVERRIDE="/tmp/zhulong_subagent_eval"   # /nasdata 100% 满; 用 /tmp (24G), 每轮清理
TRACE_BASE="/nasdata/app.e0031982/code/ZhuLong_DAC2027/trace_ablation_subagent"
RESULTS_JSON="$REPO_RUN/ablation_subagent_results.json"
SUBSET_FILE="${SUBSET_FILE:-$REPO_RUN/compaction_subset_40.txt}"  # 复用 compaction 40 题子集; P1 pilot 覆盖为 8 题
MASTER_LOG="/tmp/zhulong_subagent_ablation.log"

ARM_DIR_ROOT="/nasdata/app.e0031982/subagent_ablation"

PARALLEL=8
ROUNDS="${ROUNDS:-3}"
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

  # ⚠️ 关键: cline auto-migration 会覆盖 providers.json, 每轮前重新写入
  # 用 compaction basic 的验证过的模板 + doubao provider (如果该臂需要)
  python3 "$REPO_RUN/setup_subagent_arm_dirs.py" --arm "$ARM" --providers-only 2>>"$MASTER_LOG" || {
    log "  ⚠️ providers.json 修复失败, 用 inline python 修复"
    python3 -c "
import json, os, copy
template = json.load(open('/nasdata/app.e0031982/compaction_ablation/basic/settings/providers.json'))
p = '$ARM_DIR/settings/providers.json'
json.dump(template, open(p, 'w'), ensure_ascii=False, indent=2)
print('providers.json reset from compaction basic template')
"
  }

  # 验证 providers.json
  local prov="$ARM_DIR/settings/providers.json"
  if ! grep -q '/cloud/v1' "$prov" 2>/dev/null || ! grep -q 'deepseek-v4-pro-cloud' "$prov" 2>/dev/null; then
    log "  ❌ $ARM providers.json 修复后仍不对, 跳过此轮"
    return 1
  fi

  # 设置环境变量
  export CLI_DATA_DIR="$ARM_DIR"
  export CLINE_COMPACTION="basic"
  export CLINE_THINKING="medium"
  export LANG_HINT=""  # 轴 B 空提示
  export EVAL_BENCHMARK="benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl"
  # 🔑 修复: harness run_cline_script.sh:40 读 EVAL_ROOT_DIR_OVERRIDE (不是 EVAL_ROOT_DIR)
  export EVAL_ROOT_DIR_OVERRIDE="$EVAL_ROOT_OVERRIDE"
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
  : > "$round_log"   # truncate: 避免上一轮/旧 run 的残留内容污染 cost 收集
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

  # trace 归档 (不删原 batch; /nasdata 若满改 /tmp)
  if [[ -n "$batch_dir" && -d "${batch_dir%/}/trace" ]]; then
    local trace_dst="$TRACE_BASE/$ARM/$(basename "${batch_dir%/}")"
    mkdir -p "$trace_dst"
    cp -a "${batch_dir%/}/trace/." "$trace_dst/" 2>/dev/null && log "  trace 归档 → $trace_dst" || log "⚠️ trace 归档失败"
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

# 🔑 修复: harness run_cline_script.sh 读 TASK_FILTER (逗号分隔), 不读 SUBSET_FILE.
#   不转换 → 跑全 158 题 (而非子集). 参考 run_compaction_ablation.sh:48-54.
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
