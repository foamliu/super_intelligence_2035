#!/bin/bash
# =====================================================================
# baize_posttrain_zhulong_baseline_5run_chain.sh
# zhulong 口径 5-run 基线复测链（EDA-Eval-PyAether-158）
# 2026-11-15 用户令：158 评测改用 zhulong 方式（36.15 eda_fastmcp）
#
# 设计：
#   - run1（attribution_3615_run1, 18.99%）已存在 = zhulong 口径第 1 run
#   - 本链再跑 4 run（run2-run5），凑齐 5-run mean±std（总纲 §2 冻结协议）
#   - 每跑前 GATE：等 R2 eval 链(PID)死 + 36.15 无 run_cline_script.sh → 避让沙盒争用
#   - 照抄 zhulong 入口：run_cline_script.sh -p 8 -n -b ..._fixed.jsonl（CLI_AGENT=zhulong 默认）
#   - run_commands 保持禁用（PreToolUse hook 白名单，防泄题）
#   - 不改 eda_fastmcp 代码，只复用入口
#   - 每跑后把 final_report.json + execution_results.jsonl + 拒绝统计 拷回 .17
#   - 5 run 齐后 → 5run_zhulong_baseline_analysis.json（mean±std + 配对检验 vs 旧 .17 5-run）
# =====================================================================
set -uo pipefail

RUN_DIR="/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run"
SSH="ssh -p 3333 -o ConnectTimeout=25 -o StrictHostKeyChecking=no -o BatchMode=yes app.e0031982@localhost"
REMOTE_BASE="/nasdata/app.e0031982/code/eda_fastmcp"
BENCH="EDA-Eval-PyAether-v20260311_fixed.jsonl"
NUM_NEW_RUNS="${NUM_NEW_RUNS:-4}"          # run2..run(1+NUM)，与 run1 凑 5-run
R2_CHAIN_PID="${R2_CHAIN_PID:-2322797}"    # .17 上 R2 5-run eval 链 PID（死后释放沙盒隧道）
LOG="/tmp/posttrain_zhulong_baseline_5run_chain.log"
ANALYSIS_PY="$RUN_DIR/bpt_zhulong_baseline_5run_analysis.py"
ANALYSIS_OUT="$RUN_DIR/5run_zhulong_baseline_analysis.json"

ts(){ date '+%Y-%m-%d %H:%M:%S'; }
log(){ echo "[$(ts)] $*" | tee -a "$LOG"; }

# ---- GATE：等沙盒空闲 ----
gate_wait(){
  local r2pid="$1"
  log "[gate] 等待沙盒空闲：R2链PID=$r2pid 死 + 36.15 无 run_cline_script.sh ..."
  while :; do
    # 1) .17 上 R2 eval 链是否仍活（活→占沙盒隧道 8664-8668）
    local r2alive=0
    if [ -n "$r2pid" ] && kill -0 "$r2pid" 2>/dev/null; then r2alive=1; fi
    # 2) 36.15 上是否有 run_cline_script.sh 在跑（本机/zhulong 的 eval）
    local rem_busy=0
    # NOTE: 用 [r] grep 技巧避免 self-match —— pgrep -f "run_cline_script.sh" 会
    # 匹配到运行该 pgrep 的 bash -c shell 自身（其 cmdline 含搜索串），导致
    # rem_busy 永远非空、gate 永不放行。[r]un_cline_script.sh 作为 regex 匹配
    # run_cline_script.sh，但字面串 [r]un_cline_script.sh 不含子串 run_cline_script.sh，
    # 故 grep 不会命中自身 shell。
    rem_busy=$($SSH 'ps -eo pid=,cmd= 2>/dev/null | grep "[r]un_cline_script.sh" | head -1' 2>/dev/null | awk '{print $1}' | tr -d '[:space:]')
    if [ "$r2alive" = "0" ] && [ -z "$rem_busy" ]; then
      log "[gate] 沙盒空闲（R2链已死 + 36.15 无 eval）→ 放行"
      return 0
    fi
    log "[gate] 仍忙（r2alive=$r2alive rem_busy=${rem_busy:-none}）→ 300s 后再探"
    sleep 300
  done
}

# ---- 单 run：在 36.15 跑全量 158 ----
run_one(){
  local runidx="$1"
  local dest="$RUN_DIR/attribution_3615_run${runidx}"
  mkdir -p "$dest"
  # 幂等：若本 run 已有可解析 pass_rate 的 final_report.json → 跳过，复用既有产物
  # （pass_rate=0.0 也算有效，不会被误判为缺失）
  if [ -f "$dest/final_report.json" ]; then
    local ex_pr
    ex_pr=$(python3 -c "import json;d=json.load(open('$dest/final_report.json'));m=d.get('metrics',{});print(m.get('pass_rate', d.get('pass_rate','NA')))" 2>/dev/null || echo NA)
    if [ "$ex_pr" != "NA" ]; then
      log "[run $runidx] 既有有效 Pass@1=$ex_pr → 跳过（幂等复用）"
      echo "$ex_pr"
      return 0
    fi
  fi
  log "[run $runidx] GATE 开始"
  gate_wait "$R2_CHAIN_PID"
  log "[run $runidx] 在 36.15 启动全量158（zhulong 口径, -p 8 -n, CLI_AGENT=zhulong）..."
  # 照抄 zhulong 启动方式：必须显式传 PYTHON(venv 含 pydantic) + EVAL_FW_DIR(默认路径缺失)
  # 来源：ZhuLong ops/outbox.md L4364 `export PYTHON=.../venv/bin/python` + EVAL_FW_DIR
  local py_venv="/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python"
  local eval_fw="/nasdata/app.e0031982/code/EDA-Eval-Framework"
  # 用 bash -lc（登录 shell）确保 PATH 含 ~/.local/bin(zhulong) + node-20/bin(bun)，
  # 否则非交互 SSH 找不到 zhulong 命令（Exit 127）。
  local cmd="bash -lc 'cd $REMOTE_BASE && PYTHON=$py_venv EVAL_FW_DIR=$eval_fw timeout --signal=TERM --kill-after=120 80000 bash scripts/run_cline_script.sh -p 8 -n -b $BENCH'"
  local rc=0
  $SSH "$cmd" >>"$LOG" 2>&1 || rc=$?
  log "[run $runidx] 36.15 流水线退出 rc=$rc"
  # 找最新 batch 目录（cli_data/code/stats；BATCH_ID = 目录名）
  local latest batch_id
  latest=$($SSH 'ls -dt ~/eda_code_eval/*/ 2>/dev/null | head -1' 2>/dev/null | tr -d '\r')
  batch_id=$(basename "${latest%/}")
  log "[run $runidx] 最新 batch=$latest (BATCH_ID=$batch_id)"
  if [ -z "$latest" ]; then log "[run $runidx] ⚠ 未找到 batch 目录"; return 1; fi
  # ⚠ copy-path 修复（2026-11-15）：final_report.json + execution_results.jsonl 在
  # EDA-Eval-Framework/output_evaluation/<时间戳>/，不在 ~/eda_code_eval/<batch>/。
  # 旧脚本从 batch 目录 cat 这些文件 → 永远空 → Pass@1=NA。现从正确位置取。
  local latest_oe
  latest_oe=$($SSH 'ls -dt /nasdata/app.e0031982/code/EDA-Eval-Framework/output_evaluation/*_app.e0031982/ 2>/dev/null | head -1' 2>/dev/null | tr -d '\r')
  log "[run $runidx] 最新 output_evaluation=$latest_oe"
  # 1) final_report.json + execution_results.jsonl ← output_evaluation（评分产物）
  for f in final_report.json execution_results.jsonl; do
    $SSH "cat '${latest_oe}${f}' 2>/dev/null" >"$dest/$f" 2>/dev/null || true
  done
  # 2) completed_code_generation_<BATCH_ID>.jsonl ← ~/eda_code_eval/（生成产物，EVAL_ROOT 级）
  $SSH "cat ~/eda_code_eval/completed_code_generation_${batch_id}.jsonl 2>/dev/null" >"$dest/completed_code_generation.jsonl" 2>/dev/null || true
  # 3) codegen_rejection_stats.json ← best-effort（run1 的系手动生成；本管线可能不产）
  $SSH "find '$latest' -maxdepth 3 -name 'codegen_rejection_stats.json' 2>/dev/null | head -1 | xargs -r cat 2>/dev/null" >"$dest/codegen_rejection_stats.json" 2>/dev/null || true
  local pr
  pr=$(python3 -c "import json;d=json.load(open('$dest/final_report.json'));m=d.get('metrics',{});print(m.get('pass_rate', d.get('pass_rate','NA')))" 2>/dev/null || echo NA)
  log "[run $runidx] Pass@1=$pr （产物→ $dest）"
  echo "$pr"
}

# ---- 主流程 ----
log "===== zhulong 口径 5-run 基线复测链 START ====="
log "NUM_NEW_RUNS=$NUM_NEW_RUNS (run2..run$((1+NUM_NEW_RUNS))), 与 run1 凑 $((1+NUM_NEW_RUNS))-run"
log "BENCH=$BENCH  R2_CHAIN_PID=$R2_CHAIN_PID"

declare -a PASS_RATES=()
# run1 已存在，直接读
pr1=$(python3 -c "import json;d=json.load(open('$RUN_DIR/attribution_3615_run1/final_report.json'));m=d.get('metrics',{});print(m.get('pass_rate', d.get('pass_rate','NA')))" 2>/dev/null || echo NA)
log "[run 1] 既有 Pass@1=$pr1 (attribution_3615_run1)"
PASS_RATES+=("$pr1")

for i in $(seq 2 $((1+NUM_NEW_RUNS))); do
  pr=$(run_one "$i")
  PASS_RATES+=("$pr")
done

log "5-run Pass@1 序列: ${PASS_RATES[*]}"

# ---- 分析 ----
if [ -f "$ANALYSIS_PY" ]; then
  log "运行分析 $ANALYSIS_PY"
  python3 "$ANALYSIS_PY" --run-dir "$RUN_DIR" --num-runs $((1+NUM_NEW_RUNS)) --out "$ANALYSIS_OUT" >>"$LOG" 2>&1 || log "⚠ 分析脚本退出非0"
  log "分析产物 → $ANALYSIS_OUT"
else
  log "⚠ 分析脚本不存在：$ANALYSIS_PY（仅记 Pass@1 序列）"
fi

log "===== zhulong 口径 5-run 基线复测链 END ====="
