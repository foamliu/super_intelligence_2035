#!/usr/bin/env bash
# Watcher: wait for hermes eval to finish, then regenerate the final pilot20 report.
# Signals completion via .hermes_eval_done marker.
set -u
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_pilot
MARKER=.hermes_eval_done
EVAL=reports/eval_hermes.json
GEN=../gen_report_swebench_verified_pilot20_zh.py
rm -f "$MARKER"
for i in $(seq 1 60); do   # up to 30 min (60 x 30s)
  if [ -f "$EVAL" ]; then
    RID=$(python3 -c "import json,sys; print(json.load(open('$EVAL')).get('run_id',''))" 2>/dev/null || echo "")
    if [ -n "$RID" ] && [[ "$RID" != *"_smoke"* ]]; then
      echo "[watcher] hermes eval done (run_id=$RID) at $(date +%H:%M:%S)"
      python3 "$GEN" > watcher_regen.log 2>&1
      echo "[watcher] report regenerated at $(date +%H:%M:%S)" >> watcher_regen.log
      echo "DONE run_id=$RID ts=$(date +%s)" > "$MARKER"
      cat watcher_regen.log
      exit 0
    fi
  fi
  sleep 30
done
echo "TIMEOUT after 30 min" > "$MARKER"
