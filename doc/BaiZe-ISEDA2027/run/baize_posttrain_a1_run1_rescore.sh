#!/usr/bin/env bash
# wake871: re-extract (fixed format_cline) + rescore A1 (Qwen3.5-2B) run1.
# 修复点：①EVAL_FW_DIR 指向 NFS 规范框架 ②--benchmark pyAether-158
#           ③format_cline_cli_output.py 加 ws/*.py 兜底(补救 Qwen3.5-2B 写 ws/<func>.py 被漏抽)
set -uo pipefail
EDA_BASE=/nas_data/app.e0031982/code/eda_fastmcp
VENV="$EDA_BASE/.venv/bin/python"
BATCH=2026_1128_183414
EVAL_ROOT=/home/app.e0031982/eda_code_eval
CODE_DIR="$EVAL_ROOT/$BATCH/code"
GEN_JSONL="$EVAL_ROOT/code_generation_$BATCH.jsonl"
COMP_JSONL="completed_code_generation_$BATCH.jsonl"   # basename; run_eval reads from EVAL_ROOT
LOG_DIR="$EVAL_ROOT/$BATCH/logs"
DATASET=$EDA_BASE/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl
BENCHMARK=/nas_data/app.e0031982/code/EDA-Eval-Framework/benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl
RUN_DIR=/nas_data/app.e0031982/posttrain_5run_eval/A1_qwen35_2b/run1
LOG="$RUN_DIR/reextract_rescore.log"
mkdir -p "$RUN_DIR"
{ echo "reextract+rescore start $(date '+%F %T')"; } > "$LOG"
cd "$EDA_BASE" || { echo "cd fail"; exit 2; }

echo "=== Step A: format_cline_cli_output (fixed extractor) ===" | tee -a "$LOG"
PYTHON="$VENV" "$VENV" pyAether-eval/script/format_cline_cli_output.py \
  --input_dir="$CODE_DIR" --output_file="$GEN_JSONL" >> "$LOG" 2>&1
echo "format rc=$?" | tee -a "$LOG"

echo "=== Step B: complete_code_generation ===" | tee -a "$LOG"
PYTHON="$VENV" "$VENV" pyAether-eval/script/complete_code_generation.py \
  -o="$DATASET" -l="$LOG_DIR" -c="$GEN_JSONL" >> "$LOG" 2>&1
echo "complete rc=$?" | tee -a "$LOG"

echo "=== Step C: run_eval (rescore) ===" | tee -a "$LOG"
PYTHON="$VENV" "$VENV" scripts/run_eval.py \
  --generations "$COMP_JSONL" --benchmark "$BENCHMARK" >> "$LOG" 2>&1
rc=$?
echo "run_eval rc=$rc" | tee -a "$LOG"

# copy final_report
FR=$(ls -t /nas_data/app.e0031982/code/EDA-Eval-Framework/output_evaluation/*/final_report.json 2>/dev/null | head -1)
[ -n "$FR" ] && cp "$FR" "$RUN_DIR/final_report.json" && echo "copied $FR" | tee -a "$LOG"
cp "$EVAL_ROOT/$COMP_JSONL" "$RUN_DIR/completed_code_generation.jsonl" 2>/dev/null
echo "done $(date '+%F %T')" | tee -a "$LOG"
exit $rc
