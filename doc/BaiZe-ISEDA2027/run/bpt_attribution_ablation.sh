#!/usr/bin/env bash
# bpt_attribution_ablation.sh — 5x 跳升单变量归因 (Task A, POSTTRAIN_ENV_ATTRIBUTION_SPEC.md §2)
# 在 36.15 上跑 4 臂 × 40 题: A0(基线=36.15现配置) / A1(提示->no_sandbox) / A2(RAG->本地:18888) / A3(沙盒关+提示no_sandbox≈还原.17)
# 每臂只改一个变量, 其余与 36.15 逐字节一致. 预注册判据见 spec §2.
# ⚠️ 依赖: 36.15 5-run baseline (bpt_eval.sh --run-all) 必须先完成, 释放模型隧道+ harness. 不与运行中 eval 并跑.
# 复用 bpt_eval.sh 的 run_cline_script.sh / CLI_DATA_DIR / EVAL_FW_DIR 口径.
set -uo pipefail
EDA_BASE="/nasdata/app.e0031982/code/eda_fastmcp"
CLI_DATA_DIR="/nasdata/app.e0031982/.cline_posttrain_baseline/data"
EVAL_FW_DIR="/nasdata/app.e0031982/code/EDA-Eval-Framework"
VENV_PYTHON="$EDA_BASE/venv/bin/python"
DATASET="EDA-Eval-PyAether-v20260311_fixed.jsonl"
RESULTS_DIR="/tmp/posttrain_attribution_ablation"
MODEL_URL="http://127.0.0.1:18096/v1"   # 反向隧道 -> .17 GPU6:8096
MODEL_ID="minicpm5-2b-sft-v39-final"
# 40 题分层抽样 (按 旧5-run 是否至少通过1次 × 失败类型, 种子固定).
# 生成器: posttrain_attribution_stratified_sample.py (seed=20261114, 可复算) -> attribution_stratified_40.json
# 分层结果: 40 题 = passed_any×5 + gen_fail×29 + timeout×1 + success×10 (proportional alloc).
DEFAULT_TASKS_40="005,007,013,024,025,028,037,041,049,051,064,067,069,072,073,077,080,081,083,086,087,089,091,092,094,099,100,102,103,106,114,117,120,124,141,144,145,147,150,157"
TASKS_40="$DEFAULT_TASKS_40"
ARM=""; DRY_RUN=0; STATUS_ONLY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --arm) ARM="$2"; shift ;; --dry-run) DRY_RUN=1 ;; --status) STATUS_ONLY=1 ;;
    --tasks) TASKS_40="$2"; shift ;; *) echo "未知参数: $1" ;;
  esac; shift
done
mkdir -p "$RESULTS_DIR"
if [ "$STATUS_ONLY" = 1 ]; then
  echo "===== attribution ablation status @ $(date '+%F %T') ====="
  for a in A0 A1 A2 A3; do
    fr="$RESULTS_DIR/$a/final_report.json"
    [ -f "$fr" ] && echo "  $a: DONE $(grep -oE '\"pass_rate\"[: ]*[0-9.]+' "$fr" 2>/dev/null | head -1)" || echo "  $a: (未完成)"
  done; exit 0
fi
# 臂配置: 每臂只改一项. EDA_PROMPT_TEMPLATE / MCP 后端 / 沙盒开关.
case "$ARM" in
  A0) PROMPT_TPL="eval_sys_prompt_template_old.md"; MCP_CFG="cline_mcp_settings.json"; SANDBOX_ON=1 ;;  # 36.15 基线
  A1) PROMPT_TPL="eval_sys_prompt_template_no_sandbox.md"; MCP_CFG="cline_mcp_settings.json"; SANDBOX_ON=1 ;;  # 只改提示
  A2) PROMPT_TPL="eval_sys_prompt_template_old.md"; MCP_CFG="cline_mcp_settings_local18888.json"; SANDBOX_ON=1 ;;  # 只改 RAG 后端
  A3) PROMPT_TPL="eval_sys_prompt_template_no_sandbox.md"; MCP_CFG="cline_mcp_settings_nosandbox.json"; SANDBOX_ON=0 ;;  # 沙盒关+提示同步
  *) echo "用法: $0 --arm A0|A1|A2|A3 [--tasks <40 ids>] [--dry-run] [--status]"; exit 1 ;;
esac
echo "===== attribution ablation arm=$ARM @ $(date '+%F %T') ====="
echo "  prompt=$PROMPT_TPL  mcp_cfg=$MCP_CFG  sandbox_on=$SANDBOX_ON"
echo "  model=$MODEL_ID @ $MODEL_URL  tasks=${TASKS_40:-<未指定, 待 stratified sample>}"
[ $DRY_RUN = 1 ] && { echo "[dry-run] 不执行. 提示: 需先 bpt_eval.sh --status 确认 5-run 全 DONE, 再依次 --arm A0 A1 A2 A3."; exit 0; }
[ -z "$TASKS_40" ] && { echo "[FATAL] --tasks 未指定 40 题 (stratified sample)."; exit 1; }
chk() { [ -e "$1" ] || { echo "[FATAL] 缺失: $1"; exit 1; }; }
chk "$VENV_PYTHON"; chk "$EDA_BASE/scripts/run_cline_script.sh"
chk "$CLI_DATA_DIR/settings/providers.json"; chk "$EDA_BASE/pyAether-eval/original_dataset/$DATASET"
curl -s --max-time 8 "$MODEL_URL/models" >/dev/null 2>&1 || { echo "[FATAL] 模型端点 18096 不可达"; exit 1; }
ARM_DIR="$RESULTS_DIR/$ARM"; mkdir -p "$ARM_DIR"
export EDA_PROMPT_TEMPLATE_PYAETHER="$PROMPT_TPL"   # run_cline_script.sh L26 读此 env
# --- per-arm MCP 暂存 (wake506 修复) ---
# run_cline_script.sh 不读 MCP_CFG/SANDBOX_ON env; cline 的 MCP 来自 CLI_DATA_DIR/settings/cline_mcp_settings.json,
# run_cli.sh L85-101 会把该文件复制进每个并行 worker 的隔离目录. 故按臂 stage 一个独立 CLI_DATA_DIR:
#   A0/A1 = 基线 MCP(RAG:8090 + eda_flow:18891 全开, 不改); A2 = RAG->本地:18888; A3 = 移除 eda_flow(沙盒关).
STAGE_DIR="$RESULTS_DIR/cli_data_${ARM}"
rm -rf "$STAGE_DIR"; mkdir -p "$STAGE_DIR/settings"
cp -f "$CLI_DATA_DIR/settings/cline_mcp_settings.json" "$STAGE_DIR/settings/" 2>/dev/null
cp -f "$CLI_DATA_DIR/settings/providers.json"           "$STAGE_DIR/settings/" 2>/dev/null
cp -f "$CLI_DATA_DIR/settings/models.json"              "$STAGE_DIR/settings/" 2>/dev/null
cp -f "$CLI_DATA_DIR/settings/global-settings.json"     "$STAGE_DIR/settings/" 2>/dev/null
MCP_FILE="$STAGE_DIR/settings/cline_mcp_settings.json"
case "$ARM" in
  A0|A1) : ;;  # 基线 MCP 全开, 不改
  A2) python3 -c "import json,sys; p=sys.argv[1]; d=json.load(open(p)); d.setdefault('mcpServers',{})['pyAether_MCP_server']['url']='http://127.0.0.1:18888/mcp'; json.dump(d,open(p,'w'),indent=2,ensure_ascii=False)" "$MCP_FILE" ;;
  A3) python3 -c "import json,sys; p=sys.argv[1]; d=json.load(open(p)); d.setdefault('mcpServers',{}).pop('eda_flow',None); json.dump(d,open(p,'w'),indent=2,ensure_ascii=False)" "$MCP_FILE" ;;
esac
echo "[arm $ARM] staged MCP ($MCP_FILE):"; cat "$MCP_FILE"
export CLI_DATA_DIR="$STAGE_DIR" MCP_CFG SANDBOX_ON PYTHON="$VENV_PYTHON" EVAL_FW_DIR
export PATH="$HOME/.local/bin:$HOME/.local/node-20/bin:$HOME/.bun/bin:$PATH"
cd "$EDA_BASE"
echo "[arm $ARM] code-gen+eval starting..."
PRE_EVAL_DIRS=$(ls -d "$EVAL_FW_DIR/output_evaluation/"*/ 2>/dev/null | sort)
BATCH_ID="attribution_${ARM}_$(date '+%Y_%m%d_%H%M%S')" \
  timeout --signal=TERM --kill-after=120 72000 \
  bash scripts/run_cline_script.sh -p 8 -n -b "$DATASET" -t "$TASKS_40" > "$ARM_DIR/codegen.log" 2>&1
echo "[arm $ARM] done (rc=$?) $(date '+%F %T')"
# 36.15 上可能并发其它 eval (如 ZhuLong subagent) 写同目录; 用 pre/post 目录差集精确定位本臂产出的 final_report
POST_EVAL_DIRS=$(ls -d "$EVAL_FW_DIR/output_evaluation/"*/ 2>/dev/null | sort)
NEW_EVAL_DIR=$(comm -13 <(printf '%s\n' "$PRE_EVAL_DIRS") <(printf '%s\n' "$POST_EVAL_DIRS") | head -1)
fr="${NEW_EVAL_DIR}final_report.json"
[ -n "$NEW_EVAL_DIR" ] && [ -f "$fr" ] && cp "$fr" "$ARM_DIR/final_report.json" && echo "[arm $ARM] final_report -> $ARM_DIR/final_report.json (from $NEW_EVAL_DIR)"
[ -f "$ARM_DIR/final_report.json" ] && grep -oE '\"pass_rate\"[: ]*[0-9.]+' "$ARM_DIR/final_report.json" | head -1 | sed "s/^/[arm $ARM] /" || echo "[arm $ARM] WARNING: 无 final_report"
# --- RESCUE (wake515): cline (staged CLI_DATA_DIR /tmp) writes code to code/<task>/pyAether_code/,
# but run_cline_script.sh internal format_cline_cli_output.py reads code/<task>/ws/pyAether_code/ (ws/ empty)
# -> 0 extracted -> 0 scripts -> eval empty -> final_report=0/158 or missing (cross-contam risk).
# Proven on wake515 A1/A3: generated code content valid, only path misplaced.
# Fix = normalize pyAether_code -> ws/pyAether_code, re-run format+complete+eval, overwrite final_report. ---
BATCH_DIR=$(grep -oE '输出目录:[[:space:]]*/home/[^[:space:]]+' "$ARM_DIR/codegen.log" | tail -1 | sed 's/.*输出目录:[[:space:]]*//')
if [ -n "$BATCH_DIR" ] && [ -d "$BATCH_DIR/code" ]; then
  moved=0
  for d in "$BATCH_DIR/code"/EDA-Eval-PyAether-*/pyAether_code; do
    [ -d "$d" ] || continue
    td=$(dirname "$d"); ws="$td/ws"; mkdir -p "$ws"
    [ -e "$ws/pyAether_code" ] || { mv "$d" "$ws/pyAether_code"; moved=$((moved+1)); }
  done
  echo "[arm $ARM] RESCUE: moved $moved pyAether_code dirs into ws/"
  TS=$(basename "$BATCH_DIR")
  CG="$HOME/eda_code_eval/code_generation_${TS}.jsonl"
  CMP="$HOME/eda_code_eval/completed_code_generation_${TS}.jsonl"
  cd "$EDA_BASE"; export EVAL_FW_DIR
  "$VENV_PYTHON" pyAether-eval/script/format_cline_cli_output.py --input_dir="$BATCH_DIR/code" --output_file="$CG" > "$ARM_DIR/rescue_format.log" 2>&1
  "$VENV_PYTHON" pyAether-eval/script/complete_code_generation.py -o="$EDA_BASE/pyAether-eval/original_dataset/$DATASET" -l="$BATCH_DIR/logs" -c="$CG" > "$ARM_DIR/rescue_complete.log" 2>&1
  "$VENV_PYTHON" scripts/run_eval.py -g "$CMP" --benchmark benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl > "$ARM_DIR/rescue_eval.log" 2>&1
  RD=$(grep -oE '唯一输出目录:[[:space:]]*[^[:space:]]+' "$ARM_DIR/rescue_eval.log" | tail -1 | sed 's/.*唯一输出目录:[[:space:]]*//')
  if [ -n "$RD" ] && [ -f "${RD}final_report.json" ]; then
    cp "${RD}final_report.json" "$ARM_DIR/final_report_rescued.json"
    cp "${RD}final_report.json" "$ARM_DIR/final_report.json"
    grep -oE 'pass_rate[^,}]*' "$ARM_DIR/final_report_rescued.json" | head -1 | sed "s/^/[arm $ARM] RESCUE pass_rate=/"
  else
    echo "[arm $ARM] RESCUE: eval 未产出 final_report (见 rescue_eval.log)"
  fi
else
  echo "[arm $ARM] RESCUE: 未找到 batch dir (codegen.log 无 输出目录 行), 跳过"
fi
echo "===== arm $ARM done @ $(date '+%F %T') ====="
