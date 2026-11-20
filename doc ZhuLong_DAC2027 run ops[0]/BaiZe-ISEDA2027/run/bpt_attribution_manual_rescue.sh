#!/usr/bin/env bash
# bpt_attribution_manual_rescue.sh — 归因臂 standalone rescue (wake520)
#
# 背景: bpt_attribution_ablation.sh / bpt_attribution_prompt_dev_eval.sh 的内嵌 auto-rescue
# 用 `grep -aoE` 从 codegen.log 取 batch dir (修 binary-file-matches bug, wake519)。
# 但 relaunch515b 链中 A1/A3 的 bash 进程在 fix 落盘(04:20 git pull, new inode)前已启动,
# 仍持有旧脚本 -> auto-rescue 被跳过(报 "binary file matches" / "未找到 batch dir")。
# 本脚本 = 把 rescue 块抽成可独立调用的 helper, 供链完成后对 A3(及核验 P0base/P0p0)手动补 rescue。
#
# 幂等: 若 pyAether_code 已被前次 rescue 移入 ws/, 本次 moved=0, format 仍从 ws/ 正确读取,
# 重跑 run_eval 复现同一 final_report (不会破坏已有产物)。
#
# 用法 (在 36.15 上):
#   bash bpt_attribution_manual_rescue.sh --arm A3
#   bash bpt_attribution_manual_rescue.sh --arm-dir /tmp/posttrain_attribution_prompt/p0_dev
#   bash bpt_attribution_manual_rescue.sh --arm A1 --results-dir /tmp/posttrain_attribution_ablation
#
# 产物: <ARM_DIR>/final_report_rescued.json + <ARM_DIR>/final_report.json (覆盖)
#        + rescue_format.log / rescue_complete.log / rescue_eval.log
set -uo pipefail
EDA_BASE="/nasdata/app.e0031982/code/eda_fastmcp"
EVAL_FW_DIR="/nasdata/app.e0031982/code/EDA-Eval-Framework"
VENV_PYTHON="$EDA_BASE/venv/bin/python"
DATASET="EDA-Eval-PyAether-v20260311_fixed.jsonl"
BENCH="$EVAL_FW_DIR/benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl"

ARM=""; ARM_DIR=""; RESULTS_DIR="/tmp/posttrain_attribution_ablation"
while [ $# -gt 0 ]; do
  case "$1" in
    --arm) ARM="$2"; shift ;;
    --arm-dir) ARM_DIR="$2"; shift ;;
    --results-dir) RESULTS_DIR="$2"; shift ;;
    -h|--help) echo "用法: $0 --arm <ARM> [--results-dir <dir>] | --arm-dir <path>"; exit 0 ;;
    *) echo "未知参数: $1" ;;
  esac; shift
done
[ -n "$ARM" ] && [ -z "$ARM_DIR" ] && ARM_DIR="$RESULTS_DIR/$ARM"
[ -d "$ARM_DIR" ] || { echo "[FATAL] ARM_DIR 不存在: $ARM_DIR"; exit 1; }
CODEGEN_LOG="$ARM_DIR/codegen.log"
[ -f "$CODEGEN_LOG" ] || { echo "[FATAL] codegen.log 不存在: $CODEGEN_LOG"; exit 1; }
[ -x "$VENV_PYTHON" ] || { echo "[FATAL] venv python 不可用: $VENV_PYTHON"; exit 1; }
[ -f "$BENCH" ] || { echo "[FATAL] benchmark 不存在: $BENCH"; exit 1; }

BATCH_DIR=$(grep -aoE '输出目录:[[:space:]]*/home/[^[:space:]]+' "$CODEGEN_LOG" | tail -1 | sed 's/.*输出目录:[[:space:]]*//')
[ -n "$BATCH_DIR" ] || { echo "[FATAL] codegen.log 无 输出目录 行 (grep -aoE)"; exit 1; }
[ -d "$BATCH_DIR/code" ] || { echo "[FATAL] BATCH_DIR/code 不存在: $BATCH_DIR/code"; exit 1; }
echo "[rescue $ARM_DIR] BATCH_DIR=$BATCH_DIR  $(date '+%F %T')"

moved=0
for d in "$BATCH_DIR/code"/EDA-Eval-PyAether-*/pyAether_code; do
  [ -d "$d" ] || continue
  td=$(dirname "$d"); ws="$td/ws"; mkdir -p "$ws"
  [ -e "$ws/pyAether_code" ] || { mv "$d" "$ws/pyAether_code"; moved=$((moved+1)); }
done
echo "[rescue] moved $moved pyAether_code dirs into ws/ (0=已被前次 rescue 移走, 幂等)"

TS=$(basename "$BATCH_DIR")
CG="$HOME/eda_code_eval/code_generation_${TS}.jsonl"
CMP="$HOME/eda_code_eval/completed_code_generation_${TS}.jsonl"
cd "$EDA_BASE"; export EVAL_FW_DIR
"$VENV_PYTHON" pyAether-eval/script/format_cline_cli_output.py --input_dir="$BATCH_DIR/code" --output_file="$CG" > "$ARM_DIR/rescue_format.log" 2>&1
"$VENV_PYTHON" pyAether-eval/script/complete_code_generation.py -o="$EDA_BASE/pyAether-eval/original_dataset/$DATASET" -l="$BATCH_DIR/logs" -c="$CG" > "$ARM_DIR/rescue_complete.log" 2>&1
"$VENV_PYTHON" scripts/run_eval.py -g "$CMP" --benchmark "$BENCH" > "$ARM_DIR/rescue_eval.log" 2>&1

RD=$(grep -aoE '唯一输出目录:[[:space:]]*[^[:space:]]+' "$ARM_DIR/rescue_eval.log" | tail -1 | sed 's/.*唯一输出目录:[[:space:]]*//')
# wake520 修正: RD 来自 "唯一输出目录: <path>" 无尾斜杠 -> 必须补 "/" 否则 ${RD}final_report.json 拼错路径。
case "$RD" in */) ;; *) RD="$RD/" ;; esac
if [ -n "$RD" ] && [ -f "${RD}final_report.json" ]; then
  cp "${RD}final_report.json" "$ARM_DIR/final_report_rescued.json"
  cp "${RD}final_report.json" "$ARM_DIR/final_report.json"
  echo "[rescue] final_report -> $ARM_DIR/final_report.json (from $RD)"
  grep -oE 'pass_rate[^,}]*' "$ARM_DIR/final_report_rescued.json" | head -1 | sed "s/^/[rescue] RESCUE pass_rate=/"
  echo "[rescue] DONE $(date '+%F %T')"
  exit 0
else
  echo "[rescue] eval 未产出 final_report (见 $ARM_DIR/rescue_eval.log)"; exit 2
fi
