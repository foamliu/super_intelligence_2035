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

# 🔑 关键修复 2026-11-14 wake#925: 
#   1. configured agent 独立工具 subagent_researcher 在 cline 3.0.51 不注册 → 改用 anonymous spawn_agent
#   2. PreToolUse hook 拦截 spawn_agent (白名单缺) → e.trim → 已修 hook 加 SPAWN_TOOLS 白名单
#   3. LANG_HINT 改用 spawn_agent 措辞 (复刻 smoke 3074b 成功 prompt)
#   4. 所有 spawn 臂 (A1/B1-B5/C1/C2) 都注入强提示 (A1 也要, 否则 H1 无效)
#   smoke 3074b 证据: anonymous spawn_agent 子 session n_msgs=15 model=dsv4-pro (直接 cline 无 hook)
export CLI_AGENT=cline

EVAL_ROOT_OVERRIDE="/tmp/zhulong_subagent_eval"   # /nasdata 100% 满; 用 /tmp (24G), 每轮清理
TRACE_BASE="/tmp/zhulong_subagent_trace"            # /nasdata 99% 满 → trace 落 /tmp 并按轮归档
RESULTS_JSON="$REPO_RUN/ablation_subagent_results.json"
SUBSET_FILE="${SUBSET_FILE:-$REPO_RUN/compaction_subset_40.txt}"  # 复用 compaction 40 题子集; P1 pilot 覆盖为 8 题
MASTER_LOG="/tmp/zhulong_subagent_ablation.log"

ARM_DIR_ROOT="/nasdata/app.e0031982/subagent_ablation"

PARALLEL=8
ROUNDS="${ROUNDS:-3}"
DS_MODEL="deepseek-v4-pro-cloud"

# 强提示: 要求主 agent 先调 spawn_agent (anonymous subagent)
# 🔑 2026-11-14 wake#925: 改用 spawn_agent 措辞 (cline 3.0.51 不注册 configured agent 独立工具 subagent_researcher;
#   anonymous spawn_agent 可用但需 prompt 明确要求, 复刻 smoke 3074b 成功 prompt 措辞)
SUBAGENT_HINT="
## CRITICAL WORKFLOW REQUIREMENT
Before writing any code, you MUST use the \`spawn_agent\` tool to delegate to a researcher sub-agent.
Call \`spawn_agent\` with a systemPrompt describing a pyAether API researcher, and a task asking it to
look up the pyAether APIs relevant to this problem using the search_apis and get_api_details tools.
Do NOT answer directly or write code until the sub-agent returns its findings. This is a mandatory step."

log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$MASTER_LOG"; }

# 臂列表 (A0 复用, 不跑) — wake#926: H2/H3 技术不可行, 裁 B1-B5/C1/C2, 只跑 A1 (H1-only)
RUN_ARMS=("A1")

# ABBA-like 顺序: wake#926 H1-only — 只跑 A1
RUN_ORDER=("A1")

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

  # 验证 providers.json (主基座 dsv4-pro 恒定; doubao provider 按臂追加)
  local prov="$ARM_DIR/settings/providers.json"
  if ! grep -q '/cloud/v1' "$prov" 2>/dev/null || ! grep -q 'deepseek-v4-pro-cloud' "$prov" 2>/dev/null; then
    log "  ❌ $ARM providers.json 修复后仍不对 (缺 /cloud/v1 或 dsv4-pro 主基座), 跳过此轮"
    return 1
  fi

  # 设置环境变量
  export CLI_DATA_DIR="$ARM_DIR"
  export CLINE_COMPACTION="basic"
  export CLINE_THINKING="medium"
  export LANG_HINT=""  # 轴 B 空提示
  # 🔑 wake#925 Option B: 统一 cwd=data-dir=ws_dir → 避免 e.trim + 子 agent 用臂配置模型
  #   run_cli.sh 据此把 --data-dir 指向 ws_dir 并复制 settings/agents 进 ws_dir (保留 -p8)
  export CLINE_UNIFIED_DATA_DIR=1
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

  # 注入 subagent 强提示 (所有 spawn 臂 A1/B1-B5/C1/C2 都需要, 否则 agent 不自然调 spawn_agent)
  # 🔑 wake#925: A1 也注入 — A1=spawn-on 需强提示才会调 spawn_agent, 否则 A1≈A0 使 H1 无效
  export LANG_HINT="$SUBAGENT_HINT"

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

  # trace 归档 (不删原 batch; /nasdata 若满改 /tmp) — sessions 在 code/ 下 (CLINE_UNIFIED_DATA_DIR)
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
