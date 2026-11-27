#!/usr/bin/env bash
# baize_posttrain_a5_resume_when_tunnel.sh — one-click A5 eval resume once the
# dual-nix-tunnel (:3333) is restored by ops (Windows tunnel.ps1).
#
# Context: A5 = Qwen3.5-2B fp16 vLLM serve @ GPU5:8097 (tool-parser qwen3_xml).
#   The ONLY blocker for the 158-task EDA-Eval-PyAether eval is the sandbox
#   scoring path run_eval.py -> run_on_sandbox.py -> 127.0.0.1:8664 (SSH -L ->
#   10.251.36.15 -> 10.129.32.75 remote EDA sandbox), which needs the :3333
#   tunnel built by Windows relay `tunnel.ps1` (ops responsibility).
#
# This script: (1) verifies tunnel+serve+MCP+RAG are all UP,
#   (2) rebuilds the 8664-8669 SSH -L forwards through :3333,
#   (3) runs a 1-run smoke, then (4) --run-all 5-run, then (5) paired compare.
#
# Usage:
#   bash baize_posttrain_a5_resume_when_tunnel.sh --check     # preflight only
#   bash baize_posttrain_a5_resume_when_tunnel.sh --smoke     # 1-run smoke
#   bash baize_posttrain_a5_resume_when_tunnel.sh --run-all   # 5-run
set -uo pipefail

RUN_DIR="/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run"
EVAL_SH="$RUN_DIR/baize_posttrain_5run_eval.sh"
ENDPOINT="http://127.0.0.1:8097/v1"
MODEL="qwen3.5-2b-a5"
LABEL="A5_qwen35_2b"
# sandbox ports forwarded through :3333 -> 10.129.32.75 (matches .env SANDBOX_ENDPOINTS)
FWD_PORTS="8664 8665 8653 8669 8668 8652"
SANDBOX_HOST="10.129.32.75"

MODE="--check"
[ $# -ge 1 ] && MODE="$1"

echo "===== A5 resume preflight @ $(date '+%F %T') ====="

# --- 1. tunnel :3333 ---
if (exec 3<>/dev/tcp/127.0.0.1/3333) 2>/dev/null; then
  echo "[1/5] tunnel :3333  UP"
  exec 3>&- 3<&-
else
  echo "[1/5] tunnel :3333  DOWN — ops must run tunnel.ps1 on Windows relay (172.19.195.133). ABORT."
  exit 1
fi

# --- 2. A5 serve :8097 ---
if curl -s --max-time 5 "$ENDPOINT/models" | grep -q "qwen3.5-2b-a5"; then
  echo "[2/5] A5 serve :8097  UP (B1 id=qwen3.5-2b-a5)"
else
  echo "[2/5] A5 serve :8097  DOWN — restart with baize_posttrain_a5_serve (~/code/vllm_venv, --tool-call-parser qwen3_xml). ABORT."
  exit 1
fi

# --- 3. eda-mcp :18888 + RAG :9003 ---
if (exec 3<>/dev/tcp/127.0.0.1/18888) 2>/dev/null; then echo "[3/5] eda-mcp :18888  UP"; exec 3>&- 3<&-; else echo "[3/5] eda-mcp :18888  DOWN — start main.py. ABORT."; exit 1; fi
if curl -s --max-time 5 http://127.0.0.1:9003/health | grep -q executor_ready\":true; then echo "[4/5] RAG :9003  UP"; else echo "[4/5] RAG :9003  DOWN — start eda_api_recall (CPU-only). ABORT."; exit 1; fi

# --- 4. rebuild SSH -L sandbox forwards through :3333 ---
echo "[5/5] rebuilding SSH -L sandbox forwards (8664-8669 -> $SANDBOX_HOST via :3333)..."
# kill stale forwards (match our marker)
pkill -f 'A5_SANDBOX_FWD' 2>/dev/null || true
sleep 1
FWD_ARGS=""
for p in $FWD_PORTS; do FWD_ARGS="$FWD_ARGS -L 127.0.0.1:${p}:${SANDBOX_HOST}:${p}"; done
# -o ExitOnForwardFailure=yes so it fails loud if a port is taken
ssh -p 3333 -fN -o BatchMode=yes -o StrictHostKeyChecking=no \
  -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -o ExitOnForwardFailure=yes \
  $FWD_ARGS app.e0031982@localhost 2>/tmp/a5_fwd_err.log
FWD_RC=$?
if [ $FWD_RC -ne 0 ]; then
  echo "     SSH -L forward FAILED (rc=$FWD_RC):"; cat /tmp/a5_fwd_err.log
  echo "     ABORT."
  exit 1
fi
# verify :8664 now open
if (exec 3<>/dev/tcp/127.0.0.1/8664) 2>/dev/null; then
  echo "     :8664 OPEN — sandbox forwards established."
  exec 3>&- 3<&-
else
  echo "     :8664 still CLOSED after forward — ABORT."
  exit 1
fi

echo "===== preflight PASS — all 5 gates UP ====="
[ "$MODE" = "--check" ] && { echo "[--check] done, not launching eval."; exit 0; }

# --- 5. launch eval ---
cd "$RUN_DIR"
if [ "$MODE" = "--smoke" ]; then
  echo ">>> 1-run smoke"
  bash "$EVAL_SH" --endpoint "$ENDPOINT" --model "$MODEL" --label "$LABEL" --run 1
elif [ "$MODE" = "--run-all" ]; then
  echo ">>> 5-run full"
  bash "$EVAL_SH" --endpoint "$ENDPOINT" --model "$MODEL" --label "$LABEL" --run-all
else
  echo "unknown mode: $MODE (use --check/--smoke/--run-all)"; exit 1
fi
echo "===== A5 resume complete @ $(date '+%F %T') ====="
