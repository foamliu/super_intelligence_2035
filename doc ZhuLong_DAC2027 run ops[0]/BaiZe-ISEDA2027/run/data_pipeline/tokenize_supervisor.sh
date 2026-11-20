#!/usr/bin/env bash
# tokenize_supervisor.sh — 反复拉起 run_tokenize_untokenized.sh，直到无新增或全 DONE
set -u
R=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027
B=/nas_train/app.e0031982/datasets/baize-data
SH=$R/run/data_pipeline/run_tokenize_untokenized.sh
cd "$R/run/data_pipeline" || exit 1
idle=0
for i in $(seq 1 240); do
  before=$(ls "$B/text"/*.bin 2>/dev/null | wc -l)
  running=$(ps -eo args= | grep -c '[p]reprocess_data' || true)
  if [ "$running" -eq 0 ]; then
    echo "[sup $(date +%H:%M:%S)] relaunch #$i (bin=$before)"
    bash "$SH" >> "/tmp/tokenize_untokenized_sup.log" 2>&1 &
    sleep 45
  fi
  after=$(ls "$B/text"/*.bin 2>/dev/null | wc -l)
  echo "[sup $(date +%H:%M:%S)] bin=$after running=$(ps -eo args= | grep -c '[p]reprocess_data' || true)"
  if [ "$after" -ge 285 ]; then echo "[sup] DONE 285"; break; fi
  if [ "$after" -eq "$before" ]; then idle=$((idle+1)); else idle=0; fi
  [ "$idle" -ge 5 ] && { echo "[sup] no progress x5 -> stop"; break; }
  sleep 60
done
