#!/bin/bash
# R1486 incremental eval: 3 NEW real patches (found by scan_backlog.py after R1485).
#   codex  : sympy__sympy-19495 (patchlen=1140), sympy__sympy-19637 (patchlen=415)
#   hermes : sphinx-doc__sphinx-8638 (patchlen=685)
# 2 routes -> run sequentially (codex first, then hermes) to avoid container collision.
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
# CPU self-check PASSED (运维令 11-02): load 29.70/224 ~13.3% busy, no this-line proc >8000%.
# Memory self-check PASSED (运维令 10-30): avail ~1.3Ti, no this-line proc >50GB.
# Guardrails: OMP_NUM_THREADS=8 (limit per-container threads, avoid sklearn n_jobs runaway),
#             max_workers=1, setsid detached (R1083 lesson).
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs/incr_eval_2route_R1486.log
exec >>"$LOG" 2>&1
echo "=== incr_eval_2route R1486 START $(date) === (py=$PY)"

export OMP_NUM_THREADS=8
export OPENBLAS_NUM_THREADS=8
export MKL_NUM_THREADS=8

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
      --max_workers 1 \
      --run_id verified_full_${harness} \
      --timeout 1800" 2>&1
    echo "[$(date)] === $harness eval DONE ==="
}

# Step 1: codex — merge + eval sympy-19495, sympy-19637.
merge_preds "codex"
eval_ids "codex" "sympy__sympy-19495 sympy__sympy-19637"

# Step 2: hermes — merge + eval sphinx-8638.
merge_preds "hermes"
eval_ids "hermes" "sphinx-doc__sphinx-8638"

# Step 3: regen summaries + HTML report.
echo "[$(date)] === regen eval summaries ==="
$PY regen_eval_summaries.py 2>&1
echo "[$(date)] === gen report HTML ==="
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness
$PY gen_report_swebench_verified_full500_zh.py 2>&1 | tail -5
echo "=== incr_eval_2route R1486 DONE $(date) ==="
