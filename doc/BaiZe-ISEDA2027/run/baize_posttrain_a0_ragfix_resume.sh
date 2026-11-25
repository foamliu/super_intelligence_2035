#!/usr/bin/env bash
# baize_posttrain_a0_ragfix_resume.sh
# Resume the A0_base_ragfix 5-run eval after its orchestrator
# (baize_posttrain_5run_eval.sh --run-all, PID 3212761) died mid-run2.
#
# Situation found (wake812, 2026-11-25 08:4x):
#   run1 DONE  -> /tmp/posttrain_5run_eval/A0_base_ragfix/run1/final_report.json (41.14%)
#   run2 codegen ~96% done by ORPHANED cline workers (master run_cli.sh 3603183 + 7
#                 workers, batch dir 2026_1125_042009), but run_cline_script.sh (which
#                 does the final format->complete->eval assembly) is DEAD, so run2 was
#                 never assembled/evaluated, and run3-5 never started.
#
# This script (launched detached via setsid) autonomously:
#   1. Waits for the run2 orphan workers to finish the last tasks.
#   2. SALVAGES run2: runs the assembly steps (format_cline_cli_output.py ->
#      complete_code_generation.py -> run_eval.py) that run_cline_script.sh would have
#      run, producing run2/final_report.json. (Same path that gave run1 41.14%.)
#   3. Sanity-checks run2 pass_rate; if missing/near-0 (format bug) FALLS BACK to a
#      clean `5run_eval.sh --run 2`.
#   4. Runs run3, run4, run5 cleanly via baize_posttrain_5run_eval.sh --run N.
#   5. Finalizes: baize_posttrain_a0_finalize_5run.py --require-all
#      -> baseline_A0_base_ragfix_run{1..5}_pertask.json + 5run_summary.json
#
# Protocol frozen (总纲 §2): 158 / Pass@1 / 2500s / single-trace / 5-run / -p 8 -n.
# Does NOT touch protocol / benchmark / check.py / .env / MCP. GPU4 :8098 only.
set -uo pipefail

RUN_DIR="/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run"
EDA_BASE="/home/app.e0031982/code/eda_fastmcp"
VENV_PY="$EDA_BASE/.venv/bin/python"
RESULTS_DIR="/tmp/posttrain_5run_eval"
LABEL="A0_base_ragfix"
ENDPOINT="http://127.0.0.1:8098/v1"
MODEL="minicpm5-2b"
RUN2_BATCH="2026_1125_042009"
BENCH="$EDA_BASE/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"
EVAL_ROOT="$HOME/eda_code_eval"
LOG="/tmp/posttrain_a0_ragfix_resume.log"

ts(){ date '+%Y-%m-%d %H:%M:%S'; }
log(){ echo "[$(ts)] $*" | tee -a "$LOG"; }

log "================ resume START ================"
log "label=$LABEL  run2_batch=$RUN2_BATCH  endpoint=$ENDPOINT"

# ---- health precheck ----
curl -s -m 5 "$ENDPOINT/models" >/dev/null 2>&1 || { log "FATAL: vLLM :8098 down"; exit 3; }
curl -s -m 5 http://127.0.0.1:9003/health >/dev/null 2>&1 || log "WARN: RAG :9003 down (non-fatal for eval)"

# ---- helpers ----
run2_terminal(){
  local s=0 f=0 t=0
  [ -f "$EVAL_ROOT/$RUN2_BATCH/stats/success" ] && s=$(cat "$EVAL_ROOT/$RUN2_BATCH/stats/success" 2>/dev/null | tr -d '[:space:]')
  [ -f "$EVAL_ROOT/$RUN2_BATCH/stats/failure" ] && f=$(cat "$EVAL_ROOT/$RUN2_BATCH/stats/failure" 2>/dev/null | tr -d '[:space:]')
  [ -f "$EVAL_ROOT/$RUN2_BATCH/stats/timeout" ] && t=$(cat "$EVAL_ROOT/$RUN2_BATCH/stats/timeout" 2>/dev/null | tr -d '[:space:]')
  s=${s:-0}; f=${f:-0}; t=${t:-0}
  echo $(( s + f + t ))
}
run2_active_workers(){
  ps -eo args= 2>/dev/null | grep "eda_code_eval/$RUN2_BATCH" | grep -c -E 'cline|timeout' || true
}

log "step1: waiting for run2 orphan codegen to finish (batch $RUN2_BATCH)..."
wait_start=$(date +%s)
while :; do
  n_workers=$(run2_active_workers)
  n_term=$(run2_terminal)
  q_empty=0
  [ -s "$EVAL_ROOT/$RUN2_BATCH/.task_queue" ] || q_empty=1
  if [ "$n_workers" -eq 0 ] && [ "$n_term" -ge 158 ]; then
    log "step1: run2 codegen done (workers=$n_workers, terminal=$n_term/158, queue_empty=$q_empty)"
    break
  fi
  now=$(date +%s); elapsed=$(( now - wait_start ))
  if [ "$elapsed" -gt 10800 ]; then
    log "step1: WARN 3h grace exceeded (workers=$n_workers terminal=$n_term) - proceeding anyway"
    break
  fi
  log "step1: still running (workers=$n_workers terminal=$n_term/158 queue_empty=$q_empty) - sleep 120s"
  sleep 120
done

# Kill lingering run2 orphan run_cli.sh so they cannot contend with run3 on :8098.
# On .17 run_cli.sh is used only by posttrain eval -> safe to clear.
orphan_master=$(ps -eo pid=,args= 2>/dev/null | awk '/run_cli\.sh/{print $1}' | head -20)
if [ -n "$orphan_master" ]; then
  log "step1: killing lingering run_cli.sh orphans: $(echo $orphan_master | tr '\n' ' ')"
  for p in $orphan_master; do kill "$p" 2>/dev/null || true; done
  sleep 5
  for p in $orphan_master; do kill -9 "$p" 2>/dev/null || true; done
fi
pkill -f "eda_code_eval/$RUN2_BATCH" 2>/dev/null || true
sleep 3
log "step1: orphan cleanup done. active_workers=$(run2_active_workers)"

# ===== 2. SALVAGE run2: format -> complete -> eval =====
log "step2: SALVAGE run2 assembly..."
mkdir -p "$RESULTS_DIR/$LABEL/run2"
cd "$EDA_BASE" || { log "FATAL: cannot cd $EDA_BASE"; exit 3; }
export PYTHON="$VENV_PY"
export PATH="$HOME/.bun/bin:$PATH"

CG_JSONL="$EVAL_ROOT/code_generation_$RUN2_BATCH.jsonl"
COMP_JSONL="$EVAL_ROOT/completed_code_generation_$RUN2_BATCH.jsonl"
CODE_DIR="$EVAL_ROOT/$RUN2_BATCH/code"
LOG_DIR="$EVAL_ROOT/$RUN2_BATCH/logs"

log "step2: format_cline_cli_output.py  code=$CODE_DIR -> $CG_JSONL"
"$VENV_PY" pyAether-eval/script/format_cline_cli_output.py \
  --input_dir="$CODE_DIR" --output_file="$CG_JSONL" >> "$LOG" 2>&1 \
  || log "step2: WARN format rc=$?"
[ -f "$CG_JSONL" ] || log "step2: WARN code_generation jsonl missing: $CG_JSONL"

log "step2: complete_code_generation.py  -o=$BENCH -l=$LOG_DIR -c=$CG_JSONL"
"$VENV_PY" pyAether-eval/script/complete_code_generation.py \
  -o="$BENCH" -l="$LOG_DIR" -c="$CG_JSONL" >> "$LOG" 2>&1 \
  || log "step2: WARN complete rc=$?"
[ -f "$COMP_JSONL" ] || log "step2: WARN completed jsonl missing: $COMP_JSONL"

eval_fw_dir=$(grep -E '^EVAL_FW_DIR=' "$EDA_BASE/.env" 2>/dev/null | tail -1 | cut -d= -f2-)
eval_fw_dir="${eval_fw_dir:-/home/app.e0031982/code/EDA-Eval-Framework}"
eval_marker="$RESULTS_DIR/$LABEL/run2/.eval_start"
touch "$eval_marker"
log "step2: run_eval.py --generations $COMP_JSONL"
PYTHON="$VENV_PY" "$VENV_PY" scripts/run_eval.py --generations "$COMP_JSONL" \
  > "$RESULTS_DIR/$LABEL/run2/eval.log" 2>&1
log "step2: eval rc=$?"
fr=$(find "$eval_fw_dir/output_evaluation" -name 'final_report*.json' -newer "$eval_marker" 2>/dev/null | head -1)
run2_pr=""
if [ -n "$fr" ]; then
  cp "$fr" "$RESULTS_DIR/$LABEL/run2/final_report.json"
  [ -f "$COMP_JSONL" ] && cp "$COMP_JSONL" "$RESULTS_DIR/$LABEL/run2/completed_code_generation.jsonl"
  run2_pr=$(python3 -c "import json;d=json.load(open('$RESULTS_DIR/$LABEL/run2/final_report.json'));m=d.get('metrics',{});print(m.get('pass_rate',''))" 2>/dev/null)
  log "step2: run2 salvaged pass_rate=$run2_pr (final_report copied)"
else
  log "step2: WARN no final_report.json found in $eval_fw_dir/output_evaluation"
fi

# ===== 3. Sanity check + fallback =====
salvage_ok=0
if [ -n "$run2_pr" ]; then
  ok=$(python3 -c "print(1 if float('$run2_pr')>=0.05 else 0)" 2>/dev/null)
  [ "$ok" = "1" ] && salvage_ok=1
fi
if [ "$salvage_ok" = "1" ]; then
  log "step3: run2 salvage ACCEPTED (pass_rate=$run2_pr >= 0.05)"
else
  log "step3: run2 salvage FAILED/low (pass_rate='$run2_pr') -> FALLBACK clean --run 2"
  [ -f "$RESULTS_DIR/$LABEL/run2/final_report.json" ] && mv "$RESULTS_DIR/$LABEL/run2/final_report.json" "$RESULTS_DIR/$LABEL/run2/final_report.salvage_fail"
  cd "$RUN_DIR" || { log "FATAL: cannot cd $RUN_DIR"; exit 3; }
  bash baize_posttrain_5run_eval.sh --endpoint "$ENDPOINT" --model "$MODEL" --label "$LABEL" --run 2 >> "$LOG" 2>&1
  log "step3: fallback --run 2 done rc=$?"
fi

# ===== 4. run3 / run4 / run5 clean =====
cd "$RUN_DIR" || { log "FATAL: cannot cd $RUN_DIR"; exit 3; }
for n in 3 4 5; do
  log "step4: starting run $n ..."
  # light gate: ensure no other run_cline_script running on .17 except ours
  gate=0
  while [ "$gate" -eq 0 ]; do
    others=$(ps -eo args= 2>/dev/null | grep -E 'run_cline_script\.sh' | grep -v grep | wc -l | tr -d ' ')
    [ "$others" -eq 0 ] && gate=1 || { log "step4: gate busy ($others run_cline_script) - sleep 120s"; sleep 120; }
  done
  bash baize_posttrain_5run_eval.sh --endpoint "$ENDPOINT" --model "$MODEL" --label "$LABEL" --run "$n" >> "$LOG" 2>&1
  pr=$(python3 -c "import json;d=json.load(open('$RESULTS_DIR/$LABEL/run$n/final_report.json'));m=d.get('metrics',{});print(m.get('pass_rate',''))" 2>/dev/null)
  log "step4: run $n done pass_rate=$pr"
done

# ===== 5. Finalize (pertask JSONs + 5-run summary) =====
log "step5: finalize ..."
present=0
for n in 1 2 3 4 5; do [ -f "$RESULTS_DIR/$LABEL/run$n/final_report.json" ] && present=$((present+1)); done
log "step5: final_report.json present = $present/5"
if [ "$present" -lt 5 ]; then
  log "step5: WARN not all 5 done - running finalize WITHOUT --require-all (best-effort)"
  python3 baize_posttrain_a0_finalize_5run.py --label "$LABEL" --runs 1,2,3,4,5 >> "$LOG" 2>&1
else
  python3 baize_posttrain_a0_finalize_5run.py --label "$LABEL" --runs 1,2,3,4,5 --require-all >> "$LOG" 2>&1
fi
log "step5: finalize rc=$?"
if [ -f "$RUN_DIR/baseline_${LABEL}_5run_summary.json" ]; then
  python3 -c "import json;d=json.load(open('$RUN_DIR/baseline_${LABEL}_5run_summary.json'));print('n_runs=',d.get('n_runs_completed'),'mean=',d.get('five_run_mean'),'std=',d.get('five_run_std'))" 2>/dev/null | tee -a "$LOG"
fi
log "================ resume END ================"
exit 0

