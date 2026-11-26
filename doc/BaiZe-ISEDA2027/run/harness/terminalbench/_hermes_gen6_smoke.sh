#!/usr/bin/env bash
# _hermes_gen6_smoke.sh — Hermes Gen6 single-task smoke test
#
# Verifies the R457 provider-plugin fix: hermes-agent "Unknown provider kimi-proxy"
# was the Gen5 failure (all 5 trials RuntimeError).  R457 installs a provider
# plugin into $HERMES_HOME/plugins/model-providers/kimi-proxy/ inside the
# container instead of relying on config.yaml (which hermes silently ignores).
#
# This script runs ONE task (fix-git, locally cached image) with the hermes
# adapter.  Success = trial completes without RuntimeError and produces a
# non-empty submission.
#
# Usage:  sg docker -c 'bash _hermes_gen6_smoke.sh'
#   (sg docker needed because user's primary shell session doesn't have the
#    docker group active, even though /etc/group lists app.e0031982 as a member.)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
# Path: .../super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/terminalbench
# Need: .../super_intelligence_2035 (5 levels up from SCRIPT_DIR)
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../../.." && pwd)"   # .../doc
PROJECT_ROOT="$(cd "${PROJECT_ROOT}/.." && pwd)"           # .../super_intelligence_2035
# Verify keys.txt exists
if [[ ! -f "${PROJECT_ROOT}/doc/keys.txt" ]]; then
    echo "ERROR: cannot find doc/keys.txt from PROJECT_ROOT=${PROJECT_ROOT}"
    exit 1
fi

echo "=== Hermes Gen6 Smoke Test | $(date '+%F %T') | host=$(hostname) ==="
echo "SCRIPT_DIR=$SCRIPT_DIR"
echo "HARNESS_DIR=$HARNESS_DIR"
echo ""

# --- 1. Extract API key (never print it) ---
TB_API_KEY=$(grep -A2 'kimi-k2.6-cloud' "${PROJECT_ROOT}/doc/keys.txt" \
    | grep 'API Key' | awk -F'：' '{print $2}' | tr -d '[:space:]')
if [[ ${#TB_API_KEY} -lt 60 ]]; then
    echo "ERROR: TB_API_KEY extraction failed (len=${#TB_API_KEY})"
    exit 1
fi
echo "TB_API_KEY: <REDACTED> (len=${#TB_API_KEY})"
export TB_API_KEY

# --- 2. PYTHONPATH (harbor is a uv tool; needs to find terminalbench.agents.*) ---
export PYTHONPATH="${HARNESS_DIR}:${PYTHONPATH:-}"
echo "PYTHONPATH=$PYTHONPATH"

# --- 3. Verify imports work (non-fatal: harbor runs in its own venv) ---
python3 -c "import terminalbench.agents.hermes; print('import OK: HermesTB')" 2>&1 || {
    echo "NOTE: system python3 can't import harbor (expected — harbor is a uv tool)."
    echo "      harbor run will use its own venv where harbor is installed."
    echo "      Proceeding anyway..."
}

# --- 4. Docker check ---
docker info >/dev/null 2>&1 || {
    echo "ERROR: Docker daemon not accessible"
    exit 1
}
echo "Docker: OK ($(docker version --format '{{.Client.Version}}' 2>/dev/null))"
echo "Harbor: $(harbor --version 2>&1)"
echo ""

# --- 5. Create single-task dataset (fix-git only, image is locally cached) ---
TB_TASKS_DIR="${HOME}/terminal-bench"
SMOKE_DATASET=$(mktemp -d -t tb_hermes_gen6_smoke_XXXXXX)
ln -sf "${TB_TASKS_DIR}/fix-git" "${SMOKE_DATASET}/fix-git"
echo "Smoke dataset: ${SMOKE_DATASET} (1 task: fix-git)"
echo ""

# --- 6. Run harbor with hermes adapter ---
JOBS_DIR="${SCRIPT_DIR}/jobs_hermes_gen6_smoke"
mkdir -p "$JOBS_DIR"

TB_OVERLAY="${SCRIPT_DIR}/overlay-network-host.yml"
echo "Starting harbor run (hermes × fix-git × k=1)..."
echo "  --agent terminalbench.agents.hermes:HermesTB"
echo "  --extra-docker-compose ${TB_OVERLAY}"
echo "  --jobs-dir ${JOBS_DIR}"
echo ""

nice -n 19 harbor run \
    -p "${SMOKE_DATASET}" \
    --agent "terminalbench.agents.hermes:HermesTB" \
    -k 1 \
    --n-concurrent 1 \
    --extra-docker-compose "${TB_OVERLAY}" \
    --jobs-dir "${JOBS_DIR}" \
    2>&1 | tee "${JOBS_DIR}/smoke.log"

echo ""
echo "=== Smoke test complete ==="

# --- 7. Check result ---
RESULT_FILE="${JOBS_DIR}/result.json"
if [[ -f "$RESULT_FILE" ]]; then
    echo "--- result.json ---"
    python3 -c "
import json, sys
with open('$RESULT_FILE') as f:
    d = json.load(f)
stats = d.get('stats', {})
print(f'n_completed={stats.get(\"n_completed_trials\",\"?\")}  n_errored={stats.get(\"n_errored_trials\",\"?\")}')
evals = stats.get('evals', {})
for name, ev in evals.items():
    errs = ev.get('n_errors', 0)
    trials = ev.get('n_trials', 0)
    pa = ev.get('pass_at_k', {})
    exc = ev.get('exception_stats', {})
    print(f'  {name}: trials={trials} errors={errs} pass_at_k={pa} exceptions={list(exc.keys())}')
" 2>&1
else
    echo "WARNING: result.json not found at $RESULT_FILE"
fi

# Cleanup temp dataset (keep jobs dir for inspection)
rm -rf "$SMOKE_DATASET"
echo ""
echo "Jobs dir preserved: ${JOBS_DIR}"
echo "=== DONE ==="
