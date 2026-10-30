#!/bin/bash
# Smoke test: deepseek-harness on django__django-10097 (gate instance).
# Replicates the DeepseekHarnessDriver env (run_harness.py:350-399):
#   - SDK at /tmp/dsh_sdk on PYTHONPATH (the driver adds it to sys.path)
#   - base_url = http://127.0.0.1:9091/v1 (gw_proxy_dsh)
#   - no external proxy (predict_one with_proxy=False)
set -uo pipefail
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full

INST=django__django-10097
INST_JSON="instances/${INST}.json"
WORKDIR="/dev/shm/harness_verified_full/workdirs/deepseek-harness/django_django"
OUT="reports/harness_zero_debug/deepseek-harness/smoke_${INST}.log"
PATCHOUT="/dev/shm/harness_verified_full/workdirs/deepseek-harness/smoke_${INST}.patch"

echo "=== DEEPSEEK-HARNESS SMOKE TEST ==="
echo "instance: $INST"
echo "workdir:  $WORKDIR"
echo "timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo "gw_proxy_dsh 9091 chat test:"
curl -s -o /dev/null -w '  HTTP %{http_code}\n' -X POST http://127.0.0.1:9091/v1/chat/completions \
    -H 'Content-Type: application/json' -H 'Authorization: Bearer dummy-key-for-proxy' \
    -d '{"model":"kimi-k2.6-cloud","messages":[{"role":"user","content":"hi"}],"max_tokens":5}'
echo ""

# Reset workdir to base_commit
echo "--- git reset ---"
git -C "$WORKDIR" reset --hard b9cf764be62e 2>&1 | tail -2
git -C "$WORKDIR" clean -fdq 2>&1 | tail -2
echo ""

# Run via run_single.py
# deepseek needs PYTHONPATH=/tmp/dsh_sdk (the driver adds it to sys.path internally,
# but launch_gate.sh also exports it — replicate both to be faithful)
echo "--- running deepseek-harness (timeout 600s) ---"
export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH"
export PYTHONPATH="/tmp/dsh_sdk:${PYTHONPATH:-}"
# Strip external proxy (predict_one with_proxy=False), keep no_proxy for 127.0.0.1
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY \
    no_proxy="127.0.0.1,localhost" \
    NO_PROXY="127.0.0.1,localhost" \
    PYTHONPATH="/tmp/dsh_sdk" \
    timeout 600 python3 ../run_single.py \
    --harness deepseek-harness \
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
