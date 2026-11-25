#!/bin/bash
# R1039b incremental eval (FIXED python path: use miniforge py310 which has swebench).
# Recompute uneval fresh, merge, eval with correct python via sg docker, regen.
set -uo pipefail
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs/incr_eval_R1039b.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R1039b START $(date) === (py=$PY)"

# recompute uneval + merge for all 7 routes
$PY - <<'PYEOF'
import json, glob, os
from pathlib import Path
HERE=Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full")
EVAL_ROOT=HERE/"logs"/"run_evaluation"
MAP={"cline-patched":"cline-kimi-k2.6-cloud","opencode":"opencode-kimi-k2.6-cloud","pi":"pi-kimi-k2.6-cloud","claude-code":"claude-code-kimi-k2.6-cloud","codex":"codex-kimi-k2.6-cloud","hermes":"hermes-kimi-k2.6-cloud","deepseek-harness":"deepseek-harness-kimi-k2.6-cloud"}
for h,model in MAP.items():
    all_preds=[]; patch_ids=[]
    for f in sorted(glob.glob(str(HERE/"predictions"/(h+"__*.json")))):
        if os.path.getsize(f)<30: continue
        try:
            p=json.loads(open(f).read())
            if p and p[0].get("model_patch","").strip():
                all_preds.extend(p); patch_ids.append(p[0].get("instance_id",""))
        except: pass
    with open(str(HERE/"predictions"/("predictions_"+h+".json")),"w") as fh: json.dump(all_preds,fh,indent=2)
    run_dir=EVAL_ROOT/("verified_full_"+h)/model
    have=set()
    if run_dir.exists():
        have=set(d2.name for d2 in run_dir.iterdir() if d2.is_dir() and (d2/"report.json").exists())
    uneval=[i for i in patch_ids if i not in have]
    tag=h.replace("-","_")
    open("/tmp/%s_uneval_R1039b.txt"%tag,"w").write("\n".join(uneval)+("\n" if uneval else ""))
    print(f"{h}: merged {len(all_preds)} patches, report_json={len(have)}, uneval={len(uneval)}")
PYEOF

eval_one() {
    local h="$1"
    local tag="$(echo $h | tr '-' '_')"
    local ids_file="/tmp/${tag}_uneval_R1039b.txt"
    local ids=$(tr '\n' ' ' < "$ids_file" 2>/dev/null)
    if [ -z "$ids" ]; then echo "[$(date)] $h: no unevaluated IDs, skip"; return; fi
    echo "[$(date)] === $h eval START $(echo $ids | wc -w) instances: $ids ==="
    sg docker -c "$PY -m swebench.harness.run_evaluation \
      --predictions_path $(pwd)/predictions/predictions_${h}.json \
      --dataset_name $(pwd)/enriched_500.json \
      --split test \
      --instance_ids $ids \
      --max_workers 8 \
      --run_id verified_full_${h} \
      --timeout 1800" 2>&1
    echo "[$(date)] === $h eval DONE ==="
}

eval_one "cline-patched"
eval_one "opencode"
eval_one "pi"
eval_one "claude-code"
eval_one "codex"
eval_one "hermes"
eval_one "deepseek-harness"

echo "[$(date)] === regen summaries ==="
$PY regen_eval_summaries.py 2>&1
echo "=== incr_eval R1039b DONE $(date) ==="
