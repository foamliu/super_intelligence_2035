#!/usr/bin/env bash
# Auto-trigger incremental eval+merge+regen after the LIVE cline-patched predict finishes.
# Safety: only runs eval if predict exited AND log contains 'merged' marker.
set -u
LOG=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/logs/parallel_cline_predict.log
EVAL_LOG=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/logs/auto_eval_after_predict.log
PRED_PID=1891311
ts(){ date '+%Y-%m-%d %H:%M:%S'; }
echo "[$(ts)] auto-eval watcher started, waiting for predict PID $PRED_PID to exit" > "$EVAL_LOG"
# Wait for predict process to exit
while kill -0 "$PRED_PID" 2>/dev/null; do sleep 30; done
echo "[$(ts)] predict PID $PRED_PID exited" >> "$EVAL_LOG"
# Give filesystem a moment to flush
sleep 5
# Verify merged marker
if ! tail -30 "$LOG" | grep -q 'merged'; then
  echo "[$(ts)] WARN: no 'merged' marker in predict log tail — NOT running eval (agent will inspect)" >> "$EVAL_LOG"
  tail -15 "$LOG" >> "$EVAL_LOG"
  exit 1
fi
echo "[$(ts)] merged marker confirmed" >> "$EVAL_LOG"
# Count nonempty patches
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
NONEMPTY=$(python3 -c "import json,glob;n=0
for f in glob.glob('predictions_glm53/cline-patched__*.json'):
  if 'predictions_cline' in f: continue
  try:
    d=json.load(open(f))
    if isinstance(d,list): d=d[0] if d else {}
    if str(d.get('model_patch','') or '').strip(): n+=1
  except: pass
print(n)")
echo "[$(ts)] cline-patched nonempty patches: $NONEMPTY/500" >> "$EVAL_LOG"
# Run incremental eval+merge+regen with required env vars + guardrails
echo "[$(ts)] starting incremental_eval_merge.py --route cline-patched --regen" >> "$EVAL_LOG"
PRED_SUBDIR=predictions_glm53 WORKDIR_TAG=_glm53 EVAL_TAG=glm53_ MODEL_SUFFIX=glm-5.3-flash \
  nice -n 19 ionice -c 3 python3 incremental_eval_merge.py --route cline-patched --regen >> "$EVAL_LOG" 2>&1
RC=$?
echo "[$(ts)] incremental_eval_merge.py finished rc=$RC" >> "$EVAL_LOG"
