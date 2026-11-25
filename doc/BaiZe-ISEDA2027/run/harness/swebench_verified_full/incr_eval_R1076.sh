#!/bin/bash
# R1076 incremental eval: 3 backlog items after killing stuck R1071 container.
#   1. codex           : django__django-12039     (NEW prediction, patchlen=3561)
#   2. hermes          : sympy__sympy-19346       (NEW prediction, patchlen=2095)
#   3. deepseek-harness: astropy__astropy-14309   (RE-EVAL: R1071 container was stuck
#      running tail -f /dev/null for 55min, killed at R1076. No report.json produced.)
# NOTE: R1072 (PID 1702456) is currently eval'ing deepseek astropy-14365 with
#   run_id verified_full_deepseek-harness. This script WAITS for R1072 to finish
#   before re-using that run_id (avoid container name collision).
#   codex + hermes use different run_ids, but we still wait to avoid
#   regen_eval_summaries.py race conditions on the shared eval_*.json files.
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
# Memory self-check PASSED (115th): avail ~1.4TiB, no this-line proc >50GB
#   (max cline-hub-daemon ~3.2GB, opencode 1.1GB); no partitions() runaway.
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs/incr_eval_R1076.log
R1072_PID=1702456

exec >>"$LOG" 2>&1
echo "=== incr_eval R1076 START $(date) === (py=$PY)"

# ── Wait for R1072 to finish (deepseek astropy-14365 eval + regen) ──
echo "[$(date)] === waiting for R1072 (PID $R1072_PID) to finish ==="
waited=0
while kill -0 "$R1072_PID" 2>/dev/null; do
    sleep 30
    waited=$((waited + 1))
    if [ "$waited" -ge 120 ]; then
        echo "[$(date)] === R1072 still alive after 60min, proceeding anyway ==="
        break
    fi
done
echo "[$(date)] === R1072 finished (waited ${waited}x30s) ==="

merge_preds() {
    local harness="$1"
    echo "[$(date)] === merge $harness predictions ==="
    $PY -c "
import json, glob, os
R='$(pwd)'
all_preds=[]
for f in sorted(glob.glob(f'{R}/predictions/${harness}__*.json')):
    if os.path.getsize(f)<30: continue
    try:
        preds=json.loads(open(f).read())
        if preds and preds[0].get('model_patch','').strip():
            all_preds.extend(preds)
    except: pass
with open(f'{R}/predictions/predictions_${harness}.json','w') as fh:
    json.dump(all_preds,fh,indent=2)
print(f'${harness}: {len(all_preds)} real patches merged')
"
}

eval_ids() {
    local harness="$1"; shift
    local ids="$*"
    echo "[$(date)] === $harness eval START $(echo $ids | wc -w) instances: $ids ==="
    sg docker -c "$PY -m swebench.harness.run_evaluation \
      --predictions_path $(pwd)/predictions/predictions_${harness}.json \
      --dataset_name $(pwd)/enriched_500.json \
      --split test \
      --instance_ids $ids \
      --max_workers 8 \
      --run_id verified_full_${harness} \
      --timeout 1800" 2>&1
    echo "[$(date)] === $harness eval DONE ==="
}

# ── Step 1: codex django-12039 (independent route) ──
merge_preds "codex"
eval_ids "codex" "django__django-12039"

# ── Step 2: hermes sympy-19346 (independent route) ──
merge_preds "hermes"
eval_ids "hermes" "sympy__sympy-19346"

# ── Step 3: deepseek astropy-14309 (RE-EVAL after R1071 container kill) ──
merge_preds "deepseek-harness"
eval_ids "deepseek-harness" "astropy__astropy-14309"

# ── Step 4: regen summaries + HTML report ──
echo "[$(date)] === regen eval summaries ==="
$PY regen_eval_summaries.py 2>&1
echo "[$(date)] === gen report HTML ==="
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness
$PY gen_report_swebench_verified_full500_zh.py 2>&1 | tail -5
echo "=== incr_eval R1076 DONE $(date) ==="
