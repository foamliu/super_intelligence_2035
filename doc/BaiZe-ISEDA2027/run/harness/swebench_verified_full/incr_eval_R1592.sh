#!/bin/bash
# R1592 incr_eval: 4 cline rerun ids (previously failed, now have new patches
#   after the 2026-11-04 adapter fix: gw_proxy routing + TS binary + retry).
#   astropy__astropy-7336    (patch=1411B, prev=failed)
#   django__django-11087     (patch=3289B, prev=failed)
#   django__django-14725     (patch=17567B, prev=failed)
#   django__django-15098     (patch=3976B, prev=failed)
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs/incr_eval_R1592.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R1592 START $(date) ==="

# Step 1: incr_eval on 4 cline rerun ids (re-eval previously failed, now patched)
$PY incr_eval_backlog.py cline-patched \
    astropy__astropy-7336 \
    django__django-11087 \
    django__django-14725 \
    django__django-15098 2>&1

# Step 2: regen report
echo "[$(date)] === regen report ==="
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness
$PY gen_report_swebench_verified_full500_zh.py 2>&1 | tail -5

echo "=== incr_eval R1592 DONE $(date) ==="
