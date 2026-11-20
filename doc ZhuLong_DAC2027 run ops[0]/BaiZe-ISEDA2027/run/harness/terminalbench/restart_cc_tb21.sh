#!/usr/bin/env bash
# Restart claude-code TB-2.1 (docker was down during serial launcher pass)
export TB_MODEL="glm-5.3-flash"
export TB_API_KEY="02_088EE9051AAE4BF0ABFC7130331BF697_6903b05e-6f2d-4a69-93be-96e2b790053f"
export TB_BASE_URL="http://agi-gateway.cxmt.com/v1"
export TB_GW_PROXY_URL="http://127.0.0.1:9092/v1"
export TB_AGENT_TIMEOUT=3600
export PYTHONPATH="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness:${PYTHONPATH:-}"
export no_proxy="127.0.0.1,localhost,agi-gateway.cxmt.com"
export PATH="$HOME/.bun/bin:$HOME/.local/bin:$PATH"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
sg docker -c "nice -n 19 harbor run -p $HOME/terminal-bench --agent terminalbench.agents.claude_code:ClaudeCodeTB -k 1 --n-concurrent 1 --extra-docker-compose $SCRIPT_DIR/overlay-network-host.yml --jobs-dir /tmp/tb21_glm53_jobs/claude-code" 2>&1 | tee "$SCRIPT_DIR/traces/tb21_claude-code_rerun3.log"
