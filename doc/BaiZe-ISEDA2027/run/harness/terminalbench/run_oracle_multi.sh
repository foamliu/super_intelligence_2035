#!/usr/bin/env bash
# run_oracle_multi.sh — P0: run oracle on multiple TB4 tasks to determine if
# the artifact permission issue (640, no others-read) is universal or task-specific.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TB4_DATASET="${HOME}/terminal-bench-4.0"
JOBS_DIR="${SCRIPT_DIR}/jobs_tb4_oracle_multi"
LOG="/tmp/oracle_multi.log"

mkdir -p "${JOBS_DIR}"
echo "=== Oracle multi-test start: $(date '+%F %T') ===" > "${LOG}"

for TASK in coq-block-bound cad-model html-js-filter atrx-vep-crispr; do
    echo "--- Oracle on ${TASK} ---" >> "${LOG}"
    harbor run -p "${TB4_DATASET}" --agent oracle -k 1 --n-concurrent 1 \
        -i "${TASK}" \
        --jobs-dir "${JOBS_DIR}" >> "${LOG}" 2>&1 || echo "  (harbor exit $?)"
    # Extract reward
    REWARD=$(find "${JOBS_DIR}" -path "*${TASK}*/verifier/reward.txt" -exec cat {} \; 2>/dev/null | tail -1)
    echo "  ${TASK} reward=${REWARD:-N/A}" >> "${LOG}"
done

echo "=== Oracle multi-test done: $(date '+%F %T') ===" >> "${LOG}"
