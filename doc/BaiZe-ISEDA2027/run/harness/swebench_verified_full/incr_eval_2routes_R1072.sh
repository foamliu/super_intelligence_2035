#!/bin/bash
# R1072 incremental eval: 2 NEW real patches (found by scan_backlog.py at R1072).
#   hermes          : sympy__sympy-18763     (patch_len=539)
#   deepseek-harness: astropy__astropy-14365 (patch_len=2183)
# NOTE: R1071 incr_eval (deepseek astropy-14309) is STILL RUNNING with run_id
#   verified_full_deepseek-harness. To avoid a concurrent same-run_id container
#   name collision (sweb.eval.astropy__astropy-14309...), this script evals
#   hermes FIRST, then WAITS for the R1071 container to exit before re-merging
#   + eval'ing deepseek astropy-14365.
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
# Memory self-check PASSED (111th): avail ~1.4TiB, no this-line proc >50GB
#   (max cline-hub-daemon ~2.8GB, opencode 1.1GB); no partitions() runaway.
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs/incr_eval_2routes_R1072.log
exec >>"$LOG" 2>&1
echo "=== incr_eval_2routes R1072 START $(date) === (py=$PY)"

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
    echo "[$(date)] === $harness eval START $(echo $ids | wc -w) new instances ==="
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

# Step 1: hermes (independent route, no conflict) — merge + eval sympy-18763.
merge_preds "hermes"
eval_ids "hermes" "sympy__sympy-18763"

# Step 2: WAIT for R1071 deepseek eval (astropy-14309) to finish before
#   re-using run_id verified_full_deepseek-harness (avoid container collision).
echo "[$(date)] === waiting for R1071 deepseek container (astropy-14309) to exit ==="
for i in $(seq 1 120); do
    cnt=$(sg docker -c 'docker ps --format "{{.Names}}"' 2>/dev/null | grep -c 'sweb.eval.astropy__astropy-14309.verified_full_deepseek-harness')
    if [ "$cnt" = "0" ]; then
        echo "[$(date)] === R1071 deepseek container exited (waited $i x30s) ==="
        break
    fi
    sleep 30
done

# Step 3: deepseek — re-merge (now includes astropy-14365) + eval astropy-14365.
merge_preds "deepseek-harness"
eval_ids "deepseek-harness" "astropy__astropy-14365"

# Step 4: regen summaries + HTML report.
echo "[$(date)] === regen eval summaries ==="
$PY regen_eval_summaries.py 2>&1
echo "[$(date)] === gen report HTML ==="
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness
$PY gen_report_swebench_verified_full500_zh.py 2>&1 | tail -5
echo "=== incr_eval_2routes R1072 DONE $(date) ==="
