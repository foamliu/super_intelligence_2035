#!/usr/bin/env bash
# launch_tb_7way.sh — Terminal-Bench 2.0 · 7-harness cross-evaluation launcher
#
# Usage:
#   TB_API_KEY=<key_from_doc/keys.txt> bash launch_tb_7way.sh [--pilot]
#
# Flags:
#   --pilot   Run 7×5 pilot (35 trials) instead of full 7×89 (623 trials)
#
# Prerequisites:
#   - Docker daemon accessible (docker info succeeds)
#   - Harbor installed: uv tool install harbor
#   - Dataset: terminal-bench@2.0 downloaded
#   - TB_API_KEY env var set (from doc/keys.txt kimi-k2.6-cloud entry)
#
# Discipline (per BAIZE_HARNESS_TASK.md):
#   - Concurrency = 1 per harness; 7 parallel if no 429, else drop to 2-3
#   - nice -n 19 to avoid IO contention with training on .12/.29
#   - Results saved to terminalbench_kimi_k2.6_results.json
#   - Traces saved to traces/

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# bug-A fix (R431): harbor is a uv tool (isolated venv) and cannot import our
# custom adapters from `terminalbench.agents.*` unless the parent of the
# `terminalbench` package is on PYTHONPATH.  SCRIPT_DIR is .../terminalbench,
# so its parent (the harness/ dir) is what must be importable.
# Verified: PYTHONPATH=<harness> python -c "import terminalbench.agents.cline_patched" → OK.
export PYTHONPATH="${SCRIPT_DIR}/..:${PYTHONPATH:-}"
RESULTS_FILE="${SCRIPT_DIR}/../terminalbench_kimi_k2.6_results.json"
TRACES_DIR="${SCRIPT_DIR}/traces"
DATASET="terminal-bench@2.0"
# Local task directory on .29 (226 task dirs present; TB 2.0 spec lists 89 —
# we run whatever is present, per task §① "以实际为准").  Used with -p since
# Harbor Hub auth is not set up.  ~/terminal-bench is a symlink to
# /tmp/terminal-bench-repo/original-tasks (created by the agent; /tmp is
# volatile — if cleaned, re-download or restore the symlink).
TB_TASKS_DIR="${TB_TASKS_DIR:-${HOME}/terminal-bench}"
HARNESSES=("cline-patched" "codex" "hermes" "opencode" "claude-code" "deepseek-harness" "pi")
N_CONCURRENT=1
K_ATTEMPTS=1
PILOT_TASKS=5
FULL_TASKS=89

# 5 diverse pilot tasks covering different task families:
#   - break-filter-js-from-html  (text/JS parsing)
#   - bn-fit-modify              (scientific Python)
#   - regex-log                  (shell/regex)
#   - sqlite-db-truncate         (database)
#   - fix-git                    (git workflow)
PILOT_TASK_NAMES=(
    "break-filter-js-from-html"
    "bn-fit-modify"
    "regex-log"
    "sqlite-db-truncate"
    "fix-git"
)

# Docker overlay for network/host mode (proxy + mirrors).  Required for
# package installs inside containers (MITM proxy blocks external repos).
# Overlay now lives in the repo (stable) instead of /tmp (volatile).  It mounts
# both /opt/node and /opt/cline-modules so the cline-patched fast path triggers.
TB_OVERLAY="${TB_OVERLAY:-${SCRIPT_DIR}/overlay-network-host.yml}"

# Parse args
MODE="full"
while [[ $# -gt 0 ]]; do
    case "$1" in
        --pilot) MODE="pilot"; shift ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

# --- Pre-flight checks ---
echo "=== Terminal-Bench 2.0 · 7-harness cross-eval ==="
echo "Mode: ${MODE}"

if [[ -z "${TB_API_KEY:-}" ]]; then
    echo "ERROR: TB_API_KEY not set. Source from doc/keys.txt:" >&2
    # bug-B fix (R431): keys.txt uses FULL-WIDTH colon (：), so awk '{print $3}'
    # (whitespace split) returns empty.  Use -A2 + awk -F'：' to split on it.
    # MUST scope to kimi (keys.txt has 12 "API Key" lines; without the kimi
    # filter you'd concatenate all 12 keys).  Verified: yields a 72-char key.
    echo "  export TB_API_KEY=\$(grep -A2 'kimi-k2.6-cloud' doc/keys.txt | grep 'API Key' | awk -F'：' '{print \$2}' | tr -d '[:space:]')" >&2
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    echo "ERROR: Docker daemon not accessible. Run 'docker info' to diagnose." >&2
    echo "  Known blocker on whag0pgpuap12: user not in docker group." >&2
    exit 1
fi

if ! command -v harbor &>/dev/null; then
    echo "ERROR: harbor not found. Install: uv tool install harbor" >&2
    exit 1
fi

echo "harbor version: $(harbor --version)"
echo "docker version: $(docker version --format '{{.Client.Version}}')"
echo "dataset: ${DATASET}"
echo "model: kimi-k2.6-cloud"
echo "results: ${RESULTS_FILE}"
echo ""

# --- Build task paths (local -p, since Harbor Hub auth not set up) ---
if [[ "${MODE}" == "pilot" ]]; then
    TASK_PATHS=""
    for task in "${PILOT_TASK_NAMES[@]}"; do
        TASK_PATHS+=" -p ${TB_TASKS_DIR}/${task}"
    done
    N_TASKS=${#PILOT_TASK_NAMES[@]}
else
    # Full mode: all 89 tasks from local directory
    TASK_PATHS=""
    for task_dir in "${TB_TASKS_DIR}"/*/; do
        task_name=$(basename "${task_dir}")
        TASK_PATHS+=" -p ${TB_TASKS_DIR}/${task_name}"
    done
    N_TASKS=$(ls -d "${TB_TASKS_DIR}"/*/ 2>/dev/null | wc -l)
fi

# --- Oracle check (must pass before full eval) ---
echo "=== Oracle check (${N_TASKS} tasks with overlay) ==="
harbor run ${TASK_PATHS} --agent oracle -k 1 --n-concurrent 4 \
    --extra-docker-compose "${TB_OVERLAY}" \
    --jobs-dir "${SCRIPT_DIR}/oracle_check" 2>&1 | tee "${SCRIPT_DIR}/oracle_check.log"
echo "Oracle check complete. Verify all pass before proceeding."
echo ""

# --- Run each harness ---
echo "=== Running ${#HARNESSES[@]} harnesses × ${N_TASKS} tasks = $(( ${#HARNESSES[@]} * N_TASKS )) trials ==="

for harness in "${HARNESSES[@]}"; do
    echo "--- Harness: ${harness} ---"

    # Each harness uses a custom adapter from our terminalbench/agents/ package
    AGENT_PATH="terminalbench.agents.$(echo "${harness}" | tr '-' '_'):$(echo "${harness}" | sed 's/-./\U&/g; s/-//g' | sed 's/\b./\U&/g')TB"

    # Map harness name to import path
    case "${harness}" in
        cline-patched)     AGENT_PATH="terminalbench.agents.cline_patched:ClinePatched" ;;
        codex)             AGENT_PATH="terminalbench.agents.codex:CodexTB" ;;
        hermes)            AGENT_PATH="terminalbench.agents.hermes:HermesTB" ;;
        opencode)          AGENT_PATH="terminalbench.agents.opencode:OpenCodeTB" ;;
        claude-code)       AGENT_PATH="terminalbench.agents.claude_code:ClaudeCodeTB" ;;
        deepseek-harness)  AGENT_PATH="terminalbench.agents.deepseek_harness:DeepseekHarnessTB" ;;
        pi)                AGENT_PATH="terminalbench.agents.pi:PiTB" ;;
    esac

    nice -n 19 harbor run \
        ${TASK_PATHS} \
        --agent "${AGENT_PATH}" \
        -k "${K_ATTEMPTS}" \
        --n-concurrent "${N_CONCURRENT}" \
        --extra-docker-compose "${TB_OVERLAY}" \
        --jobs-dir "${SCRIPT_DIR}/jobs_${harness}" \
        2>&1 | tee "${TRACES_DIR}/${harness}_run.log" || {
            echo "WARNING: ${harness} run failed (may be quota/infra). Continuing."
        }

    echo "--- ${harness} done ---"
done

echo ""
echo "=== All 7 harnesses complete ==="
echo "Results: ${RESULTS_FILE}"
echo "Traces:  ${TRACES_DIR}/"
echo ""
echo "Next: generate report with gen_report_terminalbench_7way.py"
