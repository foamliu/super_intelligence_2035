#!/usr/bin/env bash
# baize_l3_tb_smoke.sh — BaiZe 2B L3 Terminal-Bench smoke test
#
# Runs 2 easy/medium Terminal-Bench tasks with BaiZe 2B (160k ckpt) as the
# LLM backend via llama-server (CPU, F16 GGUF).  Uses the harness line's
# existing Harbor + cline-patched infrastructure (read-only — no harness
# files are modified).
#
# Prerequisites:
#   - Training healthy (step < 7.4s) — checked at startup
#   - No other llama-server on port 8083
#   - Docker daemon running on .29
#   - Harbor at ~/.local/bin/harbor
#   - TB tasks at ~/terminal-bench/
#
# Usage:
#   ssh 10.239.2.29
#   bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_l3_tb_smoke.sh
#
# Results: run/baize_l3_tb_smoke_results/

set -euo pipefail

# --- Config ---
GGUF="/nas_train/app.e0031982/models/baize2b_gguf/bz2b-160000-f16.gguf"
PORT=8083
TB_THREADS=4
TB_AGENT_TIMEOUT=600
TB_TASKS_DIR="${HOME}/terminal-bench"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_DIR="${SCRIPT_DIR}/harness"
TB_OVERLAY="${HARNESS_DIR}/terminalbench/overlay-network-host.yml"
JOBS_DIR="${SCRIPT_DIR}/baize_l3_tb_smoke_results"
RESULTS_FILE="${JOBS_DIR}/results_summary.txt"
LLAMA_SERVER_BIN="/nas_train/app.e0031982/tools/llama.cpp/build/bin/llama-server"
PILOT_TASKS=("fix-git" "break-filter-js-from-html")

# --- Pre-flight: training health ---
echo "=== Pre-flight: training health check ==="
TRAIN_PID=$(pgrep -f "baize_xmodel25_decay_v2" 2>/dev/null | head -1)
if [[ -n "$TRAIN_PID" ]]; then
    STEP_TIME=$(tail -5 /proc/${TRAIN_PID}/fd/1 2>/dev/null | grep -oP 'elapsed time per iteration \(ms\): \K\d+' | tail -1)
    if [[ -n "$STEP_TIME" ]]; then
        echo "Training step time: ${STEP_TIME}ms (PID ${TRAIN_PID})"
        if (( STEP_TIME > 7400 )); then
            echo "ERROR: Training step time > 7400ms — aborting"
            exit 1
        fi
    else
        echo "WARNING: Could not parse step time from /proc/${TRAIN_PID}/fd/1"
    fi
else
    echo "WARNING: Training process not found (pgrep baize_xmodel25_decay_v2)"
fi

# --- Pre-flight: port + docker + harbor ---
if curl -s -o /dev/null "http://127.0.0.1:${PORT}/" 2>/dev/null; then
    echo "ERROR: Port ${PORT} already in use"; exit 1
fi
if ! docker info >/dev/null 2>&1; then echo "ERROR: Docker not accessible"; exit 1; fi
export PATH="${HOME}/.local/bin:${PATH}"
if ! command -v harbor >/dev/null 2>&1; then echo "ERROR: harbor not found"; exit 1; fi

# --- Pre-flight: TB tasks ---
for task in "${PILOT_TASKS[@]}"; do
    if [[ ! -d "${TB_TASKS_DIR}/${task}" ]]; then
        echo "ERROR: TB task dir not found: ${TB_TASKS_DIR}/${task}"; exit 1
    fi
done
echo "=== All pre-flight checks passed ==="

# --- Start llama-server ---
echo "=== Starting llama-server (port ${PORT}, -t ${TB_THREADS}, nice 19) ==="
nice -n 19 "$LLAMA_SERVER_BIN" \
    -m "$GGUF" -t "$TB_THREADS" -tb "$TB_THREADS" \
    -c 4096 --parallel 1 --host 127.0.0.1 --port "$PORT" \
    --no-warmup --temp 0 --top-k 1 --seed 1234 \
    > /tmp/baize_l3_llama_server.log 2>&1 &
LLAMA_PID=$!
echo "llama-server PID: $LLAMA_PID"
for i in $(seq 1 60); do
    if curl -s -o /dev/null "http://127.0.0.1:${PORT}/health" 2>/dev/null; then
        echo "llama-server ready (waited ${i}s)"; break
    fi
    if ! kill -0 "$LLAMA_PID" 2>/dev/null; then
        echo "ERROR: llama-server died"; cat /tmp/baize_l3_llama_server.log; exit 1
    fi
    sleep 1
done
if ! curl -s -o /dev/null "http://127.0.0.1:${PORT}/health" 2>/dev/null; then
    echo "ERROR: llama-server not ready after 60s"; kill "$LLAMA_PID" 2>/dev/null || true; exit 1
fi

# --- Quick sanity check ---
echo "=== Model sanity check ==="
SANITY=$(curl -s "http://127.0.0.1:${PORT}/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d '{"model":"baize-2b","messages":[{"role":"user","content":"What is 2+3?"}],"max_tokens":32,"temperature":0}' 2>/dev/null)
echo "Response: $(echo "$SANITY" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("choices",[{}])[0].get("message",{}).get("content","NO CONTENT")[:200])' 2>/dev/null || echo 'PARSE FAILED')"

# --- Set up Harbor env ---
export TB_MODEL="baize-2b-local"
export TB_BASE_URL="http://127.0.0.1:${PORT}/v1"
export TB_API_KEY="dummy-key-for-local"
export TB_AGENT_TIMEOUT="$TB_AGENT_TIMEOUT"
export PYTHONPATH="${HARNESS_DIR}:${PYTHONPATH:-}"

# --- Create pilot dataset dir ---
PILOT_DATASET="$(mktemp -d -t tb_baize2b_pilot_XXXXXX)"
for task in "${PILOT_TASKS[@]}"; do
    ln -sf "${TB_TASKS_DIR}/${task}" "${PILOT_DATASET}/${task}"
done
echo "Pilot dataset: ${PILOT_DATASET} (${#PILOT_TASKS[@]} tasks)"

# --- Run Harbor ---
mkdir -p "$JOBS_DIR"
echo "=== Running Harbor (cline-patched x ${#PILOT_TASKS[@]} tasks) ==="
nice -n 19 harbor run \
    -p "$PILOT_DATASET" \
    --agent "terminalbench.agents.cline_patched:ClinePatched" \
    -k 1 --n-concurrent 1 \
    --extra-docker-compose "$TB_OVERLAY" \
    --jobs-dir "$JOBS_DIR" \
    2>&1 | tee "${JOBS_DIR}/harbor_run.log" || {
    echo "WARNING: Harbor run failed. Collecting partial results."
}
echo "=== Harbor run complete ==="

# --- Collect results ---
echo "=== Collecting results ==="
{
echo "BaiZe 2B L3 Terminal-Bench Smoke Test"
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Model: BaiZe 2B 160k GGUF F16 (CPU llama-server -t ${TB_THREADS})"
echo "Agent: cline-patched"
echo "Tasks: ${PILOT_TASKS[*]}"
echo ""
for task in "${PILOT_TASKS[@]}"; do
    echo "--- Task: $task ---"
    TASK_JOB=$(find "$JOBS_DIR" -maxdepth 2 -name "*${task}*" -type d 2>/dev/null | head -1)
    if [[ -n "$TASK_JOB" ]]; then
        REWARD_FILE=$(find "$TASK_JOB" -name 'result*.json' -o -name 'reward*.json' 2>/dev/null | head -1)
        if [[ -n "$REWARD_FILE" ]]; then
            python3 -c "import json; d=json.load(open('$REWARD_FILE')); print(f'  Reward: {d.get(\"reward\",\"N/A\")}')" 2>/dev/null || echo "  Reward: (parse failed)"
        else
            echo "  Reward: (no result file)"
        fi
        LOG_FILE=$(find "$TASK_JOB" -name '*.log' 2>/dev/null | head -1)
        if [[ -n "$LOG_FILE" ]]; then
            echo "  Log: $LOG_FILE"
        fi
    else
        echo "  (task not found in jobs dir)"
    fi
    echo ""
done
} | tee "$RESULTS_FILE"

# --- Cleanup ---
echo "=== Cleanup ==="
kill "$LLAMA_PID" 2>/dev/null && echo "llama-server killed" || echo "llama-server already gone"
rm -rf "$PILOT_DATASET"
sleep 2
kill -0 "$LLAMA_PID" 2>/dev/null && { kill -9 "$LLAMA_PID" 2>/dev/null || true; echo "Force-killed"; }
echo "=== Done ==="
echo "Results: $RESULTS_FILE"
echo "Jobs: $JOBS_DIR/"
