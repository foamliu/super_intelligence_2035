#!/bin/bash
# Wait for the think-lang ablation orchestrator (run_think_lang_ablation.sh) to
# finish ALL 30 rounds, then run the B_zh_r2 regrade in the clean window.
#
# Why wait for the orchestrator (not just run_cline_script): the orchestrator
# serially launches run_cline_script for each round and immediately relaunches
# the next after scoring. The only window where the 4 shared sandbox workdirs
# are truly free is after the orchestrator exits (all 30 rounds done). Waiting
# only for run_cline_script to disappear would fire in the brief inter-round
# gap and the regrade would then collide with the next round on the shared
# workdirs (same 158-task benchmark) -> pollution. See run_B_zh_r2_regrade.sh
# CONCURRENCY NOTE.
#
# Launch (detached):
#   setsid bash run_B_zh_r2_regrade_wait.sh > /tmp/regrade_B_zh_r2_wait.log 2>&1 < /dev/null &
set -uo pipefail

RUN_DIR=/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run
REGRADE_LOG=/tmp/regrade_B_zh_r2.log
WAIT_LOG=/tmp/regrade_B_zh_r2_wait.log

echo "=== B_zh_r2 regrade WAITER START $(date '+%Y-%m-%d %H:%M:%S') ===" | tee -a "$WAIT_LOG"
echo "Waiting for run_think_lang_ablation.sh (orchestrator) to exit before running regrade." | tee -a "$WAIT_LOG"

# 1) Wait for the orchestrator process to be gone.
while pgrep -f 'run_think_lang_ablation.sh' >/dev/null 2>&1; do
  sleep 300
done
echo "[$(date '+%Y-%m-%d %H:%M:%S')] orchestrator gone." | tee -a "$WAIT_LOG"

# 2) Belt-and-suspenders: also ensure no run_cline_script / run_eval is active,
#    and wait out any tail.
while pgrep -f 'run_cline_script|run_eval' >/dev/null 2>&1; do
  sleep 60
done
echo "[$(date '+%Y-%m-%d %H:%M:%S')] no run_cline_script/run_eval active; sandbox should be free." | tee -a "$WAIT_LOG"

# 3) Run the regrade.
echo "[$(date '+%Y-%m-%d %H:%M:%S')] launching run_B_zh_r2_regrade.sh -> $REGRADE_LOG" | tee -a "$WAIT_LOG"
bash "$RUN_DIR/run_B_zh_r2_regrade.sh" > "$REGRADE_LOG" 2>&1
RC=$?
echo "[$(date '+%Y-%m-%d %H:%M:%S')] regrade EXIT=$RC (log: $REGRADE_LOG)" | tee -a "$WAIT_LOG"

# 4) Gate check: n_tasks must == 158.
N=$(grep -oE '样本 [0-9]+/[0-9]+|pass \([0-9.]+%\)|n_tasks[^0-9]*[0-9]+' "$REGRADE_LOG" 2>/dev/null | tail -5)
echo "[$(date '+%Y-%m-%d %H:%M:%S')] regrade gate check snippets: $N" | tee -a "$WAIT_LOG"
echo "=== B_zh_r2 regrade WAITER END $(date '+%Y-%m-%d %H:%M:%S') ===" | tee -a "$WAIT_LOG"
