#!/usr/bin/env bash
# run_oracle_test.sh — P0 verification: run oracle on 1 TB4 task to confirm verifier works.
# Oracle applies the gold solution; if reward=1.0 the verifier infra is sound.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TB4_DATASET="${HOME}/terminal-bench-4.0"
JOBS_DIR="${SCRIPT_DIR}/jobs_tb4_oracle_test"
LOG="/tmp/oracle_test_data_anon.log"

mkdir -p "${JOBS_DIR}"
echo "=== Oracle test start: $(date '+%F %T') ===" > "${LOG}"
harbor run -p "${TB4_DATASET}" --agent oracle -k 1 --n-concurrent 1 \
    -i 'data-anonymization' \
    --jobs-dir "${JOBS_DIR}" >> "${LOG}" 2>&1
echo "EXIT=$?" >> "${LOG}"
echo "=== Oracle test done: $(date '+%F %T') ===" >> "${LOG}"
