#!/usr/bin/env bash
# baize_l3_terminalbench_vllm.sh — L3 Agentic eval via Terminal-Bench 2.0
# Evaluates BaiZe 2B checkpoint on Terminal-Bench tasks using vLLM + Harbor.
# Usage: bash baize_l3_terminalbench_vllm.sh <iter> [--smoke]
# Prereqs: GPU(>10GB free), vLLM, Harbor (uv tool install harbor), Docker
set -uo pipefail
REPO="/nas_train/app.e0031982/code/super_intelligence_2035"
NEMO_DIR="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b"
CONVERTER="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/convert_mcore_to_hf.py"
VLLM_PY="/nas_train/app.e0031982/miniforge3/envs/vllm/bin/python"
PY310="/nas_train/app.e0031982/miniforge3/envs/py310/bin/python"
TB_DIR="$REPO/doc/BaiZe-ISEDA2027/run/harness/terminalbench"
HARNESS_DIR="$REPO/doc/BaiZe-ISEDA2027/run/harness"
RES_DIR="$NEMO_DIR/lm_eval_results"
VLLM_PORT=8000
VLLM_PID=""
ITER="${1:?Usage: baize_l3_terminalbench_vllm.sh <iter> [--smoke]}"
SMOKE=0; [[ "${2:-}" == "--smoke" ]] && SMOKE=1
HF_DIR="$NEMO_DIR/hf_iter_${ITER}"
TB_RES_DIR="$RES_DIR/tb_iter_${ITER}"
LOG="/tmp/baize_l3_tb_${ITER}.log"
SMOKE_TASKS=(bn-fit-modify break-filter-js-from-html chess-best-move fix-git log-summary-date-ranges)
ts() { date '+%Y-%m-%d %H:%M:%S'; }
log() { echo "[$(ts)] [L3-TB] $*"; }
cleanup() { [[ -n "$VLLM_PID" ]] && kill -0 "$VLLM_PID" 2>/dev/null && kill "$VLLM_PID" 2>/dev/null && sleep 2 && kill -9 "$VLLM_PID" 2>/dev/null; }
trap cleanup EXIT
check_prereqs() {
  local ok=1
  local gpu_free=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits 2>/dev/null | head -1)
  if [[ -z "$gpu_free" || "$gpu_free" -lt 10000 ]]; then log "FAIL: no GPU >10GB free"; ok=0; else log "OK: GPU ${gpu_free}MiB free"; fi
  "$VLLM_PY" -c "import vllm" >/dev/null 2>&1 || { log "FAIL: vLLM not importable"; ok=0; }
  command -v harbor >/dev/null 2>&1 || { log "WARN: harbor not in PATH"; ok=0; }
  docker info >/dev/null 2>&1 || { log "FAIL: docker not accessible"; ok=0; }
  [[ -d "$HOME/terminal-bench" ]] || { log "WARN: ~/terminal-bench missing"; ok=0; }
  [[ $ok -eq 0 ]] && { log "PREREQ CHECK FAILED"; return 1; } || return 0
}
export_hf() {
  [[ -f "$HF_DIR/config.json" ]] && { log "HF export exists, skip"; return 0; }
  log "exporting ckpt iter_${ITER} to HF..."
  "$PY310" "$CONVERTER" --checkpoint-dir "$NEMO_DIR/checkpoints/iter_$(printf '%07d' "$ITER")" --output-dir "$HF_DIR" --tokenizer-path "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/data/tokenizer_eod" 2>&1 | tee -a "$LOG"
  [[ -f "$HF_DIR/config.json" ]] || { log "FAIL: HF export failed"; return 1; }
  return 0
}
start_vllm() {
  log "starting vLLM on port $VLLM_PORT..."
  export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
  "$VLLM_PY" -m vllm.entrypoints.openai.api_server --model "$HF_DIR" --port "$VLLM_PORT" --dtype bfloat16 --max-model-len 4096 --gpu-memory-utilization 0.85 --trust-remote-code > /tmp/vllm_l3_tb_${ITER}.log 2>&1 &
  VLLM_PID=$!
  local w=0
  while [[ $w -lt 120 ]]; do
    curl -s "http://127.0.0.1:${VLLM_PORT}/v1/models" >/dev/null 2>&1 && { log "vLLM ready (${w}s)"; return 0; }
    kill -0 "$VLLM_PID" 2>/dev/null || { log "FAIL: vLLM died"; return 1; }
    sleep 5; w=$((w+5))
  done
  log "FAIL: vLLM not ready after 120s"; return 1
}
run_terminalbench() {
  log "running Terminal-Bench (smoke=$SMOKE)..."
  mkdir -p "$TB_RES_DIR" "$TB_RES_DIR/traces"
  export TB_BASE_URL="http://127.0.0.1:${VLLM_PORT}/v1" TB_MODEL="baize-2b" TB_API_KEY="dummy" TB_DUMMY_KEY="dummy"
  export PYTHONPATH="${HARNESS_DIR}:${PYTHONPATH:-}" TB_TASKS_DIR="${TB_TASKS_DIR:-${HOME}/terminal-bench}"
  local ddir; ddir=$(mktemp -d -t tb_l3_ds_XXXXXX)
  if [[ $SMOKE -eq 1 ]]; then
    for t in "${SMOKE_TASKS[@]}"; do [[ -d "$TB_TASKS_DIR/$t" ]] && ln -sf "$TB_TASKS_DIR/$t" "$ddir/$t"; done
  else
    for d in "$TB_TASKS_DIR"/*/; do local t=$(basename "$d"); docker image inspect "alexgshaw/$t:20251031" >/dev/null 2>&1 && ln -sf "$d" "$ddir/$t"; done
  fi
  local n; n=$(ls -d "$ddir"/*/ 2>/dev/null | wc -l); log "dataset: ${n} tasks"
  [[ $n -eq 0 ]] && { log "FAIL: no tasks"; return 1; }
  cd "$TB_DIR" || return 1
  nice -n 19 harbor run --dataset "$ddir" --agent "terminalbench.agents.cline_patched" --overlay "$TB_DIR/overlay-network-host.yml" --traces-dir "$TB_RES_DIR/traces" --concurrency 1 --timeout 600 2>&1 | tee -a "$LOG"
  local pass=0 fail=0 total=0; local sm="$TB_RES_DIR/summary.json"
  echo "{\"iter\":$ITER,\"model\":\"baize-2b\",\"harness\":\"cline-patched\",\"smoke\":$SMOKE,\"timestamp\":\"$(ts)\",\"tasks\":[" > "$sm"
  local first=1
  for d in "$TB_RES_DIR/traces"/*/; do
    [[ ! -d "$d" ]] && continue
    local task=$(basename "$d") r="N/A"
    [[ -f "$d/reward.txt" ]] && r=$(grep -oP 'reward=\K[0-9]' "$d/reward.txt" || echo "N/A")
    total=$((total+1)); [[ "$r" == "1" ]] && pass=$((pass+1)) || fail=$((fail+1))
    [[ $first -eq 0 ]] && echo -n "," >> "$sm"; first=0
    echo -n "{\"task\":\"$task\",\"reward\":$r}" >> "$sm"
  done
  echo "],\"pass\":$pass,\"fail\":$fail,\"total\":$total,\"pass_rate\":$(echo "scale=4;$pass/$total"|bc 2>/dev/null||echo 0)}" >> "$sm"
  log "RESULTS: pass=$pass fail=$fail total=$total"; return 0
}
log "=== BaiZe L3 Terminal-Bench (iter=$ITER smoke=$SMOKE) ==="
check_prereqs || exit 1
export_hf || exit 1
start_vllm || exit 1
run_terminalbench || exit 1
log "=== L3 complete ==="
exit 0
