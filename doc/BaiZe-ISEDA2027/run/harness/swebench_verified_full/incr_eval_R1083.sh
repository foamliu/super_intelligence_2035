#!/bin/bash
# R1083 incremental eval: 4 backlog items found by scan_backlog.
#   1. claude-code      : django__django-13410     (patchlen=755,  R1082 transient retry)
#   2. codex            : django__django-12193     (patchlen=1417, NEW predict 289->290)
#   3. deepseek-harness : astropy__astropy-14995   (patchlen=30770,NEW predict 47->48)
#   4. hermes           : sympy__sympy-19954       (patchlen=1268, NEW)
# No other eval processes running. 4 predict orchestrators still alive (claude-code/codex/hermes/deepseek).
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
# Memory self-check PASSED (122nd): avail ~1.4TiB, no this-line proc >50GB.
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs/incr_eval_R1083.log

exec >>"$LOG" 2>&1
echo "=== incr_eval R1083 START $(date) === (py=$PY)"

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

# ── Step 1: claude-code django-13410 ──
merge_preds "claude-code"
eval_ids "claude-code" "django__django-13410"

# ── Step 2: codex django-12193 ──
merge_preds "codex"
eval_ids "codex" "django__django-12193"

# ── Step 3: deepseek-harness astropy-14995 ──
merge_preds "deepseek-harness"
eval_ids "deepseek-harness" "astropy__astropy-14995"

# ── Step 4: hermes sympy-19954 ──
merge_preds "hermes"
eval_ids "hermes" "sympy__sympy-19954"

# ── Step 5: regen summaries + HTML report ──
echo "[$(date)] === regen eval summaries ==="
$PY regen_eval_summaries.py 2>&1
echo "[$(date)] === gen report HTML ==="
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness
$PY gen_report_swebench_verified_full500_zh.py 2>&1 | tail -10
echo "=== incr_eval R1083 DONE $(date) ==="
