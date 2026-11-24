#!/usr/bin/env bash
# Night-window launcher: re-attempt remaining empty cline-patched patches.
# - Waits until 21:00 local, then runs predict --workers 8 on round2 ids (66 empty).
# - After predict exits, auto-runs incremental_eval_merge.py --regen.
# - Resource guardrails: nice19, ionice3, ulimit -v 209715200.
# - Per 11-24 user directive: --workers 8 (429 auto 8->4->2), 4 env vars required.
set -u

HERE=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
IDS_FILE="$HERE/rerun_ids/cline-patched_rerun_ids_round2.txt"
PRED_LOG="$HERE/logs/parallel_cline_predict_round2.log"
EVAL_LOG="$HERE/logs/auto_eval_after_predict_round2.log"
ROUTE=cline-patched

# 4 required env vars (11-24 directive step 4)
export PRED_SUBDIR=predictions_glm53
export WORKDIR_TAG=_glm53
export EVAL_TAG=glm53_
export MODEL_SUFFIX=glm-5.3-flash

# Resource guardrails
ulimit -v 209715200 2>/dev/null || true
export OMP_NUM_THREADS=8

ts(){ date '+%Y-%m-%d %H:%M:%S'; }

echo "[$(ts)] night_predict launcher started, waiting for 21:00 window" > "$PRED_LOG"

# Wait until 21:00 (local time)
while true; do
  H=$(date +%H)
  if [ "$H" -ge 21 ] || [ "$H" -lt 9 ]; then
    break
  fi
  echo "[$(ts)] outside window (H=$H), sleeping 600s until 21:00" >> "$PRED_LOG"
  sleep 600
done

echo "[$(ts)] window entered (H=$(date +%H)), starting predict" >> "$PRED_LOG"

# Launch predict with --workers 8
nice -n 19 ionice -c 3 python3 "$HERE/run_verified_full.py" predict \
  --harness "$ROUTE" \
  --ids-file "$IDS_FILE" \
  --workers 8 >> "$PRED_LOG" 2>&1
PRED_RC=$?
echo "[$(ts)] predict finished rc=$PRED_RC" >> "$PRED_LOG"

# Auto-eval+merge+regen (same as auto_eval_after_predict.sh)
sleep 5
echo "[$(ts)] starting incremental_eval_merge.py --regen" > "$EVAL_LOG"
if ! tail -30 "$PRED_LOG" | grep -q 'merged'; then
  echo "[$(ts)] WARN: no 'merged' marker -- skipping eval (agent will inspect)" >> "$EVAL_LOG"
  tail -15 "$PRED_LOG" >> "$EVAL_LOG"
  exit 1
fi
echo "[$(ts)] merged marker confirmed" >> "$EVAL_LOG"

cd "$HERE"
nice -n 19 ionice -c 3 python3 incremental_eval_merge.py --route "$ROUTE" --regen >> "$EVAL_LOG" 2>&1
EVAL_RC=$?
echo "[$(ts)] incremental_eval_merge.py finished rc=$EVAL_RC" >> "$EVAL_LOG"
