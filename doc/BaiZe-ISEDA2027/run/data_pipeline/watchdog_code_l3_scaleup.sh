#!/bin/bash
# watchdog_code_l3_scaleup.sh
# Auto-scale: wait for Code L3 (64-worker run) to complete, then kill + restart
# run_full_tokenize.sh with MAX_CONCURRENT=160 for remaining sources
# (Math L3 → Code L2 → UFW-L3 → Math L1).
#
# Rationale: Code L3 is already 63% done with 64 workers; killing now wastes
# ~372GB of NFS I/O. Instead, let it finish, then scale to 160 for the
# remaining ~1,316B tokens (saves ~23h vs staying at 64).
#
# Speed test (64 workers, 107 min): ~220K tok/s/worker, ~14M tok/s aggregate,
# CPU ~104/224 cores, mem 1205GB avail, en_v1_4 download healthy at 9.6MB/s.
# Linear extrapolation to 160: ~35M tok/s, ~200/224 cores, ~320GB mem — safe.
#
# Launch:
#   setsid -f nohup bash watchdog_code_l3_scaleup.sh > /tmp/watchdog_code_l3_scaleup.log 2>&1 &

CODE_L3_DIR=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/data/full_ultradata_code_l3
RUN_SCRIPT=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data_pipeline/run_full_tokenize_scaled.sh
LOG=/tmp/watchdog_code_l3_scaleup.log
EXPECTED_IDX=63  # s0–s62 (s63 launched with 0 parquet → crashes, no .idx)

echo "=== watchdog START $(date '+%F %T') ===" >> "$LOG"
echo "Monitoring $CODE_L3_DIR for $EXPECTED_IDX .idx files" >> "$LOG"

while true; do
  done_count=$(ls "$CODE_L3_DIR"/*.idx 2>/dev/null | wc -l)
  ts=$(date '+%F %T')
  echo "[$ts] Code L3 .idx count: $done_count/$EXPECTED_IDX" >> "$LOG"

  if [ "$done_count" -ge "$EXPECTED_IDX" ]; then
    echo "[$ts] Code L3 COMPLETE! Scaling up to 160 workers..." >> "$LOG"

    # 1) Kill the run_full_tokenize.sh parent script (PID 1253330 or whatever)
    pkill -f 'bash run_full_tokenize\.sh' 2>/dev/null
    echo "[$ts] Killed run_full_tokenize.sh parent" >> "$LOG"
    sleep 3

    # 2) Kill ANY of our workers (full_ultradata / full_ufw) that are still
    #    running — including Math L3 workers the script may have already
    #    launched.  DO NOT touch env14_ workers (en_v1_4 fullsource).
    pkill -f 'preprocess_data_cm.*full_ultradata' 2>/dev/null
    pkill -f 'preprocess_data_cm.*full_ufw' 2>/dev/null
    echo "[$ts] Killed full_ultradata/full_ufw workers" >> "$LOG"
    sleep 5

    # 3) Verify our workers are gone
    remaining=$(pgrep -af 'preprocess_data_cm.*full_ultradata' 2>/dev/null | grep -v grep | wc -l)
    remaining2=$(pgrep -af 'preprocess_data_cm.*full_ufw' 2>/dev/null | grep -v grep | wc -l)
    echo "[$ts] Remaining our workers: full_ultradata=$remaining full_ufw=$remaining2" >> "$LOG"

    # 4) Quick sanity: verify en_v1_4 workers are still alive (we must not have killed them)
    env14_alive=$(pgrep -af 'preprocess_data_cm.*env14_' 2>/dev/null | grep -v grep | wc -l)
    echo "[$ts] en_v1_4 workers still alive: $env14_alive" >> "$LOG"

    # 5) Restart with MAX_CONCURRENT=160 using scaled script (skips Code L3).
    #    run_full_tokenize_scaled.sh processes only Math L3 → Code L2 → UFW-L3 → Math L1.
    #    This avoids re-tokenizing Code L3 with different shard boundaries (160 vs 64).
    MAX_CONCURRENT=160 setsid -f nohup bash "$RUN_SCRIPT" > /tmp/run_full_tokenize_160.log 2>&1 &
    new_pid=$!
    echo "[$ts] Restarted with MAX_CONCURRENT=160 (scaled script), PID=$new_pid" >> "$LOG"
    echo "[$ts] New log: /tmp/run_full_tokenize_160.log" >> "$LOG"

    # 6) Wait a moment and verify the new run started
    sleep 10
    new_alive=$(pgrep -f 'run_full_tokenize_scaled' 2>/dev/null | grep -v grep | wc -l)
    echo "[$ts] run_full_tokenize_scaled.sh alive: $new_alive" >> "$LOG"
    break
  fi
  sleep 60
done

echo "=== watchdog DONE $(date '+%F %T') ===" >> "$LOG"
