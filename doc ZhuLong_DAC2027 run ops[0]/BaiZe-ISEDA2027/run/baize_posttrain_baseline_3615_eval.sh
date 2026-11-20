#!/usr/bin/env bash
# baize_posttrain_baseline_3615_eval.sh
# EDA-Eval-PyAether(158) 基线重测 —— 在 36.15 启动（RAG+MCP+沙盒可达）。
# 模型 SFT step105 经反向隧道 .17:8096 -> 36.15 localhost:18096。
# 冻结协议：158 / Pass@1 / 2500s / 5-run / -p 8 -n（与旧基线同判据）。
# -n 禁用 Memory Bank 自动注入，但 cline 经 MCP 仍可主动调 search_apis(RAG)/run_code(沙盒)。
set -uo pipefail
EDA_BASE="/nasdata/app.e0031982/code/eda_fastmcp"
CLI_DATA_DIR="/nasdata/app.e0031982/.cline_posttrain_baseline/data"
EVAL_FW_DIR="/nasdata/app.e0031982/code/EDA-Eval-Framework"
VENV_PYTHON="$EDA_BASE/venv/bin/python"
DATASET="EDA-Eval-PyAether-v20260311_fixed.jsonl"
RESULTS_DIR="/tmp/posttrain_baseline_3615"
LABEL="step105_3615"
SMOKE_TASKS="001,010,050,100,150"
RUN_ALL=0; RUN_NUM=""; SMOKE=0; DRY_RUN=0; STATUS_ONLY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;; --smoke) SMOKE=1 ;; --run) RUN_NUM="$2"; shift ;;
    --run-all) RUN_ALL=1 ;; --status) STATUS_ONLY=1 ;; *) echo "未知参数: $1" ;;
  esac; shift
done
mkdir -p "$RESULTS_DIR"
if [ "$STATUS_ONLY" = 1 ]; then
  echo "===== baseline 36.15 status @ $(date '+%F %T') =====  RESULTS_DIR=$RESULTS_DIR"
  for r in 1 2 3 4 5; do
    fr="$RESULTS_DIR/run${r}/final_report.json"
    [ -f "$fr" ] && echo "  run${r}: DONE $(grep -oE '\"pass_rate\"[: ]*[0-9.]+' "$fr" 2>/dev/null | head -1)" || echo "  run${r}: (未完成)"
  done; exit 0
fi
echo "===== baseline 36.15 eval @ $(date '+%F %T') ====="
echo "  model=minicpm5-2b-sft-v39-final @ http://127.0.0.1:18096/v1 (隧道->.17 GPU6:8096)"
echo "  MCP: pyAether_MCP_server:8090 (RAG) + eda_flow:18891 (沙盒)  DATASET=$DATASET(158)"
echo "  protocol: 158/Pass@1/2500s/5-run/-p 8 -n  CLI_DATA_DIR=$CLI_DATA_DIR"
[ $SMOKE = 1 ] && echo "  MODE=SMOKE(tasks=$SMOKE_TASKS)"
[ $DRY_RUN = 1 ] && { echo "[dry-run] 不执行。"; exit 0; }
chk() { [ -e "$1" ] || { echo "[FATAL] 缺失: $1"; exit 1; }; }
chk "$VENV_PYTHON"; chk "$EDA_BASE/scripts/run_cline_script.sh"
chk "$CLI_DATA_DIR/settings/providers.json"; chk "$CLI_DATA_DIR/settings/cline_mcp_settings.json"
chk "$EDA_BASE/pyAether-eval/original_dataset/$DATASET"
curl -s --max-time 8 http://127.0.0.1:18096/v1/models >/dev/null 2>&1 || { echo "[FATAL] 模型端点 18096 不可达"; exit 1; }
echo "[check] 前置检查通过。"
run_single() {
  local run_n="$1"
  local run_dir="$RESULTS_DIR/run${run_n}"
  mkdir -p "$run_dir"
  local stamp=$(date '+%Y_%m%d_%H%M%S')
  local before=$(ls -dt "$EVAL_FW_DIR/output_evaluation/"*/ 2>/dev/null | head -1)
  echo "[run $run_n] === START $(date '+%F %T') ==="
  cd "$EDA_BASE"
  export PYTHON="$VENV_PYTHON" CLI_DATA_DIR="$CLI_DATA_DIR" EVAL_FW_DIR="$EVAL_FW_DIR"
  export PATH="$HOME/.local/bin:$HOME/.local/node-20/bin:$HOME/.bun/bin:$PATH"
  local task_flag=""; [ $SMOKE = 1 ] && task_flag="-t $SMOKE_TASKS"
  echo "[run $run_n] code-gen+eval starting..."
  BATCH_ID="baseline3615_run${run_n}_${stamp}" \
    timeout --signal=TERM --kill-after=120 72000 \
    bash scripts/run_cline_script.sh -p 8 -n -b "$DATASET" $task_flag > "$run_dir/codegen.log" 2>&1
  echo "[run $run_n] code-gen+eval done (rc=$?) $(date '+%F %T')"
  local fr=$(ls -dt "$EVAL_FW_DIR/output_evaluation/"*/final_report.json 2>/dev/null | head -1)
  [ -n "$fr" ] && cp "$fr" "$run_dir/final_report.json" && echo "[run $run_n] final_report -> $run_dir/final_report.json"
  local er=$(ls -dt "$EVAL_FW_DIR/output_evaluation/"*/execution_results.jsonl 2>/dev/null | head -1)
  [ -n "$er" ] && cp "$er" "$run_dir/execution_results.jsonl" 2>/dev/null || true
  local cg=$(ls -t "$HOME/eda_code_eval/completed_code_generation_"*.jsonl 2>/dev/null | head -1)
  [ -n "$cg" ] && cp "$cg" "$run_dir/completed_code_generation.jsonl" 2>/dev/null || true
  [ -f "$run_dir/final_report.json" ] && grep -oE '\"pass_rate\"[: ]*[0-9.]+' "$run_dir/final_report.json" | head -1 | sed "s/^/[run $run_n] /" || echo "[run $run_n] WARNING: 无 final_report"
  echo "[run $run_n] === END $(date '+%F %T') ==="
}
if [ $SMOKE = 1 ]; then run_single 1
elif [ $RUN_ALL = 1 ]; then for r in 1 2 3 4 5; do run_single "$r"; done
elif [ -n "$RUN_NUM" ]; then run_single "$RUN_NUM"
else echo "用法: $0 --dry-run|--smoke|--run N|--run-all|--status"; exit 1; fi
echo "===== done @ $(date '+%F %T') ====="
