#!/usr/bin/env bash
# baize_posttrain_a0_ragfix_salvage_run3.sh
# Salvage A0_base_ragfix run3 whose /tmp run-dir was wiped by the rogue
# `rm -rf /tmp/posttrain_5run_eval/A0_base_ragfix` (wake813) mid-codegen.
# run3 codegen actually COMPLETED (rc=0, batch 2026_1125_092258, 146+5+7=158),
# but the assembly (format->complete->eval) never ran because the run-dir
# (providers.json.bak / .eval_start / eval.log targets) was gone.
#
# This script mirrors the run2 SALVAGE path in baize_posttrain_a0_ragfix_resume.sh
# step2 exactly, then writes run3/final_report.json so the resume script's step5
# finalize sees all 5 runs present -> --require-all passes.
#
# CPU-only scoring (run_eval reads pre-executed codegen results); NO :8098
# contention with run4 codegen. Protocol frozen (总纲 §2).
set -uo pipefail

RUN_DIR="/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run"
EDA_BASE="/home/app.e0031982/code/eda_fastmcp"
VENV_PY="$EDA_BASE/.venv/bin/python"
RESULTS_DIR="/tmp/posttrain_5run_eval"
LABEL="A0_base_ragfix"
RUN3_BATCH="2026_1125_092258"
BENCH="$EDA_BASE/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"
EVAL_ROOT="$HOME/eda_code_eval"
LOG="/tmp/posttrain_a0_ragfix_salvage_run3.log"

ts(){ date '+%Y-%m-%d %H:%M:%S'; }
log(){ echo "[$(ts)] $*" | tee -a "$LOG"; }

log "================ run3 salvage START ================"
log "batch=$RUN3_BATCH"

CG_JSONL="$EVAL_ROOT/code_generation_$RUN3_BATCH.jsonl"
COMP_JSONL="$EVAL_ROOT/completed_code_generation_$RUN3_BATCH.jsonl"
CODE_DIR="$EVAL_ROOT/$RUN3_BATCH/code"
LOG_DIR="$EVAL_ROOT/$RUN3_BATCH/logs"

# stats sanity
s=$(cat "$EVAL_ROOT/$RUN3_BATCH/stats/success" 2>/dev/null | tr -d '[:space:]')
f=$(cat "$EVAL_ROOT/$RUN3_BATCH/stats/failure" 2>/dev/null | tr -d '[:space:]')
t=$(cat "$EVAL_ROOT/$RUN3_BATCH/stats/timeout" 2>/dev/null | tr -d '[:space:]')
s=${s:-0}; f=${f:-0}; t=${t:-0}
log "stats: success=$s failure=$f timeout=$t total=$((s+f+t))"
[ $((s+f+t)) -ge 158 ] || { log "FATAL: batch not complete ($((s+f+t))/158)"; exit 3; }

mkdir -p "$RESULTS_DIR/$LABEL/run3"
cd "$EDA_BASE" || { log "FATAL: cannot cd $EDA_BASE"; exit 3; }
export PYTHON="$VENV_PY"
export PATH="$HOME/.bun/bin:$PATH"

log "step1: format_cline_cli_output.py code=$CODE_DIR -> $CG_JSONL"
"$VENV_PY" pyAether-eval/script/format_cline_cli_output.py \
  --input_dir="$CODE_DIR" --output_file="$CG_JSONL" >> "$LOG" 2>&1 \
  || log "step1: WARN format rc=$?"
[ -f "$CG_JSONL" ] || { log "FATAL: code_generation jsonl missing: $CG_JSONL"; exit 3; }
log "step1: CG_JSONL lines=$(wc -l < "$CG_JSONL")"

log "step2: complete_code_generation.py -o=$BENCH -l=$LOG_DIR -c=$CG_JSONL"
"$VENV_PY" pyAether-eval/script/complete_code_generation.py \
  -o="$BENCH" -l="$LOG_DIR" -c="$CG_JSONL" >> "$LOG" 2>&1 \
  || log "step2: WARN complete rc=$?"
[ -f "$COMP_JSONL" ] || { log "FATAL: completed jsonl missing: $COMP_JSONL"; exit 3; }
log "step2: COMP_JSONL lines=$(wc -l < "$COMP_JSONL")"

eval_fw_dir=$(grep -E '^EVAL_FW_DIR=' "$EDA_BASE/.env" 2>/dev/null | tail -1 | cut -d= -f2-)
eval_fw_dir="${eval_fw_dir:-/home/app.e0031982/code/EDA-Eval-Framework}"
eval_marker="$RESULTS_DIR/$LABEL/run3/.eval_start"
touch "$eval_marker"
log "step3: run_eval.py --generations $COMP_JSONL"
PYTHON="$VENV_PY" "$VENV_PY" scripts/run_eval.py --generations "$COMP_JSONL" \
  > "$RESULTS_DIR/$LABEL/run3/eval.log" 2>&1
log "step3: eval rc=$?"

fr=$(find "$eval_fw_dir/output_evaluation" -name 'final_report*.json' -newer "$eval_marker" 2>/dev/null | head -1)
if [ -n "$fr" ]; then
  cp "$fr" "$RESULTS_DIR/$LABEL/run3/final_report.json"
  cp "$COMP_JSONL" "$RESULTS_DIR/$LABEL/run3/completed_code_generation.jsonl"
  pr=$(python3 -c "import json;d=json.load(open('$RESULTS_DIR/$LABEL/run3/final_report.json'));m=d.get('metrics',{});print(m.get('pass_rate',''))" 2>/dev/null)
  log "step3: run3 salvaged pass_rate=$pr (final_report copied from $fr)"
else
  log "FATAL: no final_report.json found in $eval_fw_dir/output_evaluation"
  exit 4
fi

log "================ run3 salvage END ================"
exit 0
