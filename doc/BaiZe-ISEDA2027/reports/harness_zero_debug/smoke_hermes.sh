#!/bin/bash
# Smoke test: hermes on django__django-10097 (the gate instance that failed
# with "cannot import name 'ArgsKwargs'" due to PYTHONPATH poisoning).
# Replicates the EXACT env the HermesDriver sets (run_harness.py:486-491):
#   - PYTHONPATH stripped (R548 fix)
#   - no_proxy=127.0.0.1,localhost (gw_proxy reachable)
#   - no external proxy (predict_one with_proxy=False)
set -uo pipefail
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full

INST=django__django-10097
INST_JSON="instances/${INST}.json"
WORKDIR="/dev/shm/harness_verified_full/workdirs/hermes/django_django"
OUT="reports/harness_zero_debug/hermes/smoke_${INST}.log"
PATCHOUT="/dev/shm/harness_verified_full/workdirs/hermes/smoke_${INST}.patch"

echo "=== HERMES SMOKE TEST ===" 
echo "instance: $INST"
echo "workdir:  $WORKDIR"
echo "timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo "env PYTHONPATH (should be empty): '${PYTHONPATH:-}'"
echo ""

# Reset workdir to base_commit (clean state)
echo "--- git reset ---"
git -C "$WORKDIR" reset --hard b9cf764be62e 2>&1 | tail -2
git -C "$WORKDIR" clean -fdq 2>&1 | tail -2
echo ""

# Run via run_single.py with the driver env (PYTHONPATH stripped, no_proxy set)
# Timeout 600s (real model calls take 200-600s; broken adapter exits ~2-3s)
echo "--- running hermes (timeout 600s) ---"
export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH"
# Replicate HermesDriver env: strip PYTHONPATH, set no_proxy
env -u PYTHONPATH \
    no_proxy="127.0.0.1,localhost" \
    NO_PROXY="127.0.0.1,localhost" \
    http_proxy= https_proxy= HTTP_PROXY= HTTPS_PROXY= \
    timeout 600 python3 ../run_single.py \
    --harness hermes \
    --instance-json "$INST_JSON" \
    --workdir "$WORKDIR" \
    --base-commit b9cf764be62e \
    --timeout 540 \
    --out-patch "$PATCHOUT" 2>&1
RC=$?
echo ""
echo "=== SMOKE RESULT: rc=$RC ==="
echo "patch size: $(wc -c < "$PATCHOUT" 2>/dev/null || echo 0) bytes"
echo "timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
