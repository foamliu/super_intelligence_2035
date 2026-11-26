#!/usr/bin/env bash
# Restart 4 stopped TB-2.1 routes: cline-patched, codex, hermes, pi
# (deepseek-harness, opencode, claude-code already running separately)
export TB_MODEL="glm-5.3-flash"
export TB_API_KEY="02_088EE9051AAE4BF0ABFC7130331BF697_6903b05e-6f2d-4a69-93be-96e2b790053f"
export TB_BASE_URL="http://agi-gateway.cxmt.com/v1"
export TB_GW_PROXY_URL="http://127.0.0.1:9092/v1"
export TB_AGENT_TIMEOUT=3600
export PYTHONPATH="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness:${PYTHONPATH:-}"
export no_proxy="127.0.0.1,localhost,agi-gateway.cxmt.com"
export NO_PROXY="127.0.0.1,localhost,agi-gateway.cxmt.com"
export PATH="$HOME/.bun/bin:$HOME/.local/bin:$PATH"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TB_OVERLAY="$SCRIPT_DIR/overlay-network-host.yml"
TB_DATASET="$HOME/terminal-bench"
JOBS_BASE="/tmp/tb21_glm53_jobs"

launch_route() {
    local harness="$1"
    local agent_path="$2"
    local HJ="$JOBS_BASE/$harness"
    mkdir -p "$HJ"
    echo "[$(date '+%H:%M:%S')] Starting $harness ..."
    sg docker -c "nice -n 19 harbor run -p $TB_DATASET --agent $agent_path -k 1 --n-concurrent 1 --extra-docker-compose $TB_OVERLAY --jobs-dir $HJ" \
        2>&1 | tee "$SCRIPT_DIR/traces/tb21_${harness}_rerun.log" &
    echo "[$(date '+%H:%M:%S')] $harness launched (PID $!)"
    sleep 5  # stagger starts to avoid docker race
}

launch_route "cline-patched"    "terminalbench.agents.cline_patched:ClinePatched"
launch_route "codex"            "terminalbench.agents.codex:CodexTB"
launch_route "hermes"           "terminalbench.agents.hermes:HermesTB"
launch_route "pi"               "terminalbench.agents.pi:PiTB"

echo "=== All 4 stopped routes relaunched ==="
wait
echo "=== All 4 routes completed ==="
