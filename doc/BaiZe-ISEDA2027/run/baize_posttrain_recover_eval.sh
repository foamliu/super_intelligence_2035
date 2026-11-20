#!/usr/bin/env bash
# baize_posttrain_recover_eval.sh — Recover a 5-run eval whose codegen COMPLETED
# but whose final_report.json is missing.
#
# Context: baize_posttrain_5run_eval.sh had 3 bugs (R408) that broke the eval step
# AFTER codegen succeeded, so the (expensive, ~3h) codegen output was orphaned:
#   A) grep without -a  → JSONL path not detected (binary codegen.log)
#   B) bare `python`    → run_eval.py never launched (rc=127; no `python` on host)
#   C) wrong search dir → final_report.json never found ($HOME/eda_code_eval vs
#                        $EVAL_FW_DIR/output_evaluation)
# All three are fixed in baize_posttrain_5run_eval.sh now; this script salvages
# runs that were already mid-flight with the old in-memory script (e.g. run4).
#
# run_eval.py is PURE SCORING: it reads pre-executed results baked into the codegen
# JSONL (assemble + calculate, ~2s). It does NOT re-execute in the sandbox and does
# NOT call the LLM endpoint → safe to run any time after codegen, even concurrently
# with another run's codegen.
#
# Usage:
#   bash baize_posttrain_recover_eval.sh --label step105 --run 3
#   bash baize_posttrain_recover_eval.sh --label step105 --run 4 --wait   # poll for JSONL
set -uo pipefail

EDA_BASE="/home/app.e0031982/code/eda_fastmcp"
VENV_PYTHON="$EDA_BASE/.venv/bin/python"
RESULTS_DIR="/tmp/posttrain_5run_eval"

LABEL=""; RUN_NUM=""; WAIT=0
while [ $# -gt 0 ]; do
  case "$1" in
    --label) LABEL="$2"; shift ;;
    --run)   RUN_NUM="$2"; shift ;;
    --wait)  WAIT=1 ;;
    *) echo "unknown: $1" ;;
  esac
  shift
done
if [ -z "$LABEL" ] || [ -z "$RUN_NUM" ]; then
  echo "usage: $0 --label <LABEL> --run <N> [--wait]"; exit 1
fi

run_dir="$RESULTS_DIR/$LABEL/run${RUN_NUM}"
mkdir -p "$run_dir"
jsonl="$run_dir/completed_code_generation.jsonl"

resolve_jsonl() {
  # If the run dir's copy is missing, parse codegen.log for the "输出文件:" path.
  if [ ! -f "$jsonl" ] && [ -f "$run_dir/codegen.log" ]; then
    local orig
    orig=$(grep -a -oP '输出文件: \K\S+' "$run_dir/codegen.log" 2>/dev/null | head -1)
    if [ -n "$orig" ] && [ -f "$orig" ]; then cp "$orig" "$jsonl"; fi
  fi
}

if [ "$WAIT" = 1 ]; then
  echo "[recover] $LABEL run$RUN_NUM: waiting for codegen JSONL ..."
  while [ ! -f "$jsonl" ]; do
    resolve_jsonl
    [ -f "$jsonl" ] && break
    sleep 60
  done
else
  resolve_jsonl
fi

if [ ! -f "$jsonl" ]; then
  echo "[recover] $LABEL run$RUN_NUM FATAL: no JSONL found"; exit 1
fi
if [ -f "$run_dir/final_report.json" ]; then
  echo "[recover] $LABEL run$RUN_NUM: final_report.json already present — skip"
  exit 0
fi

echo "[recover] $LABEL run$RUN_NUM: running run_eval.py on $jsonl"
cd "$EDA_BASE"
eval_marker="$run_dir/.recover_eval_start"; touch "$eval_marker"
PYTHON="$VENV_PYTHON" "$VENV_PYTHON" scripts/run_eval.py --generations "$jsonl" > "$run_dir/eval.log" 2>&1
echo "[recover] eval rc=$?"

eval_fw_dir=$(grep -E '^EVAL_FW_DIR=' "$EDA_BASE/.env" 2>/dev/null | tail -1 | cut -d= -f2-)
eval_fw_dir="${eval_fw_dir:-/home/app.e0031982/code/EDA-Eval-Framework}"
fr=$(find "$eval_fw_dir/output_evaluation" -name 'final_report*.json' -newer "$eval_marker" 2>/dev/null | head -1)
if [ -n "$fr" ]; then
  cp "$fr" "$run_dir/final_report.json"
  pr=$(python3 -c "import json;d=json.load(open('$run_dir/final_report.json'));print(d.get('metrics',{}).get('pass_rate','N/A'))" 2>/dev/null)
  echo "[recover] $LABEL run$RUN_NUM: final_report.json copied, Pass@1(metrics.pass_rate)=$pr"
else
  echo "[recover] $LABEL run$RUN_NUM WARNING: no final_report.json (checked $eval_fw_dir/output_evaluation)"
fi
