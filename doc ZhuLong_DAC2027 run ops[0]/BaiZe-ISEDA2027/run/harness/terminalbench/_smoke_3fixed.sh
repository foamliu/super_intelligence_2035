#!/usr/bin/env bash
# _smoke_3fixed.sh — R493 smoke test for the 3 fixed 0%-pass adapters.
# Validates R492 fixes (hermes/deepseek-harness/claude-code) on 5 oracle-solvable
# Terminal-Bench tasks.  Per 2026-10-25 operator directive ③:
#   - 判据 = at least 1/5 pass per harness (else not fixed -> diagnose).
#   - 三个逐个验 (validate ONE AT A TIME, sequentially, NOT parallel).
#   - Reuse EXISTING gw_proxy (9090 chat/anthropic + 9091 dsh) from the 7x89
#     launcher; do NOT restart it (would disturb the 4 survivors).  Only start
#     our own if the ports are down, and clean up only our own.
# Tasks (oracle-verified reward=1 on 2026-10-24):
#   bn-fit-modify, break-filter-js-from-html, chess-best-move, fix-git,
#   log-summary-date-ranges
set -uo pipefail
export PATH="/home/app.e0031982/.local/bin:${PATH}"
REPO="/nas_train/app.e0031982/code/super_intelligence_2035"
TB_DIR="$REPO/doc/BaiZe-ISEDA2027/run/harness/terminalbench"
HARNESS_DIR="$REPO/doc/BaiZe-ISEDA2027/run/harness"
SMOKE_ROOT="/tmp/tb_smoke"
mkdir -p "$SMOKE_ROOT" "$SMOKE_ROOT/traces"
export TB_API_KEY="$(grep -A2 'kimi-k2.6-cloud' "$REPO/doc/keys.txt" | grep 'API Key' | awk -F'：' '{print $2}' | tr -d '[:space:]')"
echo "[smoke] HOST=$(hostname) TB_API_KEY_len=${#TB_API_KEY} harbor=$(command -v harbor || echo MISSING) date=$(date '+%F %T')"
if [[ -z "${TB_API_KEY}" ]]; then echo "[smoke] FATAL: TB_API_KEY empty"; exit 1; fi
cd "$TB_DIR" || { echo "[smoke] FATAL: cd failed"; exit 2; }
TASKS=(bn-fit-modify break-filter-js-from-html chess-best-move fix-git log-summary-date-ranges)
DATASET="$(mktemp -d -t tb_smoke_dataset_XXXXXX)"
for t in "${TASKS[@]}"; do
    if docker image inspect "alexgshaw/$t:20251031" >/dev/null 2>&1; then
        ln -sf "${HOME}/terminal-bench/${t}" "${DATASET}/${t}"
        echo "[smoke] task $t -> image OK"
    else
        echo "[smoke] WARNING: image alexgshaw/$t:20251031 MISSING"
    fi
done
N_TASKS=$(ls -d "${DATASET}"/*/ 2>/dev/null | wc -l)
echo "[smoke] dataset has ${N_TASKS} tasks at ${DATASET}"
TB_OVERLAY="${TB_DIR}/overlay-network-host.yml"
export PYTHONPATH="${HARNESS_DIR}:${PYTHONPATH:-}"
OWNS_GW=0
GW_PIDS=()
ensure_gw() {
    if curl -s -o /dev/null http://127.0.0.1:9090/ 2>/dev/null && \
       curl -s -o /dev/null http://127.0.0.1:9091/ 2>/dev/null; then
        echo "[smoke] gw_proxy already up on 9090+9091 — reusing (NOT restarting, survivors safe)"
        return
    fi
    echo "[smoke] gw_proxy NOT up — starting own"
    GW_API_KEY="$TB_API_KEY" GW_UPSTREAM="http://agi-gateway.cxmt.com/cloud/v1" GW_PROXY_PORT=9090 \
        python3 /nas_train/app.e0031982/harness_work/gw_proxy.py >"$SMOKE_ROOT/gw_proxy.log" 2>&1 &
    GW_PIDS+=($!)
    GW_API_KEY="$TB_API_KEY" GW_UPSTREAM="http://agi-gateway.cxmt.com/cloud/v1" GW_PROXY_PORT=9091 \
        python3 /nas_train/app.e0031982/harness_work/gw_proxy_dsh.py >"$SMOKE_ROOT/gw_proxy_dsh.log" 2>&1 &
    GW_PIDS+=($!)
    OWNS_GW=1
    for _ in $(seq 1 20); do curl -s -o /dev/null http://127.0.0.1:9090/ 2>/dev/null && break; sleep 0.5; done
}
cleanup() {
    if [[ $OWNS_GW -eq 1 ]]; then
        echo "[smoke] cleanup: killing our own gw_proxy ${GW_PIDS[*]:-}"
        for _pid in "${GW_PIDS[@]:-}"; do kill "$_pid" 2>/dev/null || true; done
    else
        echo "[smoke] cleanup: gw_proxy reused (NOT killing — survivors may need it)"
    fi
}
trap cleanup EXIT
ensure_gw
HARNESSES=(deepseek-harness hermes claude-code)
declare -A AGENT_PATH=(
    [deepseek-harness]="terminalbench.agents.deepseek_harness:DeepseekHarnessTB"
    [hermes]="terminalbench.agents.hermes:HermesTB"
    [claude-code]="terminalbench.agents.claude_code:ClaudeCodeTB"
)
echo "[smoke] === Sequential smoke: ${#HARNESSES[@]} harnesses x ${N_TASKS} tasks ==="
echo "[smoke] Mode: SEQUENTIAL (one at a time, --n-concurrent 1) starting $(date '+%F %T')"
for harness in "${HARNESSES[@]}"; do
    ap="${AGENT_PATH[$harness]}"
    jobs_dir="$SMOKE_ROOT/jobs_${harness}"
    mkdir -p "$jobs_dir"
    log="$SMOKE_ROOT/traces/${harness}_smoke.log"
    echo ""
    echo "[smoke] >>>>>> ${harness} (agent=${ap}) start $(date '+%F %T') >>>>>>"
    nice -n 19 harbor run -p "${DATASET}" --agent "${ap}" -k 1 --n-concurrent 1 \
        --extra-docker-compose "${TB_OVERLAY}" --jobs-dir "${jobs_dir}" > "${log}" 2>&1
    status=$?
    echo "[smoke] <<<<<< ${harness} harbor exit=${status} end $(date '+%F %T') <<<<<<"
    done_n=$(find "${jobs_dir}" -name reward.txt 2>/dev/null | wc -l)
    pass_n=$(find "${jobs_dir}" -name reward.txt -exec cat {} \; 2>/dev/null | grep -c '^1')
    err_n=$(find "${jobs_dir}" -name exception.txt 2>/dev/null | wc -l)
    echo "[smoke] ${harness}: done=${done_n}/${N_TASKS} pass=${pass_n} err=${err_n} (判据 pass>=1)"
    if [[ ${pass_n} -ge 1 ]]; then echo "[smoke] ${harness}: SMOKE PASS"; else echo "[smoke] ${harness}: SMOKE FAIL — check ${log}"; fi
done
echo ""
echo "[smoke] === All 3 smoke harnesses complete at $(date '+%F %T') ==="
echo "[smoke] Summary:"
for harness in "${HARNESSES[@]}"; do
    jobs_dir="$SMOKE_ROOT/jobs_${harness}"
    done_n=$(find "${jobs_dir}" -name reward.txt 2>/dev/null | wc -l)
    pass_n=$(find "${jobs_dir}" -name reward.txt -exec cat {} \; 2>/dev/null | grep -c '^1')
    err_n=$(find "${jobs_dir}" -name exception.txt 2>/dev/null | wc -l)
    echo "[smoke]   ${harness}: done=${done_n} pass=${pass_n} err=${err_n}"
done
