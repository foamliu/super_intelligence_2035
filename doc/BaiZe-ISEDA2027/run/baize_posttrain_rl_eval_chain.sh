#!/usr/bin/env bash
# baize_posttrain_rl_eval_chain.sh -- Autonomous post-RL 158-task 5-run eval chain.
#
# Purpose (用户令 2026-11-13 13:3x): RL 起跑后，取 RL ckpt -> vLLM serve ->
#   EDA-Eval-PyAether 158 题 5-run mean+-std vs SFT step105 base~2.74% 配对检验
#   (McNemar / paired bootstrap). 无提升/退化如实记录（vision v10 教训）。
#
# This daemon waits for the GRPO training process to finish (so GPU7 frees),
# AND for the running SFT eval chain to finish (providers.json is a shared
# singleton that 5run_eval.sh rewrites per-run -> concurrent evals clobber each
# other, so RL eval MUST serialize behind the existing step105/step60/base chain).
# Then it serves the latest RL checkpoint on GPU7:8095 and runs 5-run eval.
#
# 报告口径：替身预演，收益不可迁移到 BaiZe。
# 冻结协议（总纲 §2）：158 任务 / Pass@1 / 2500s / 单 trace / 5-run / -p 8 -n。
# 红线：anti-cheat 全程开（cline harness 内置）；cheat rate 由训练侧 cheat_rate.json 报。
#
# Usage (background, fire-and-forget after launching GRPO training):
#   nohup bash baize_posttrain_rl_eval_chain.sh \
#     --grpo-pid 1887597 --eval-chain-pid 1161064 \
#     --rl-run-dir rl_surrogate_runs/minicpm5_grpo_loop_R0_200step \
#     > /tmp/posttrain_rl_eval_chain.log 2>&1 &
#
#   bash baize_posttrain_rl_eval_chain.sh --dry-run      # print recipe only
#   bash baize_posttrain_rl_eval_chain.sh --status       # show wait/serve/eval status
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVE_SCRIPT="$SCRIPT_DIR/baize_posttrain_sft_surrogate_serve.sh"
EVAL_SCRIPT="$SCRIPT_DIR/baize_posttrain_5run_eval.sh"
ANALYSIS_SCRIPT="$SCRIPT_DIR/baize_posttrain_5run_analysis.py"

GRPO_PID="1887597"
EVAL_CHAIN_PID="1161064"
RL_RUN_DIR="$SCRIPT_DIR/rl_surrogate_runs/minicpm5_grpo_loop_R0_200step"
GPU="7"
PORT="8095"
BASE_LABEL="step105"
# Label prefixes (parameterized so R0/R2/R3 arms don't clobber each other).
# Defaults preserve the original R0 behavior.
RL_LABEL_PREFIX="grpo_R0_step"
SERVED_NAME_PREFIX="minicpm5-2b-grpo-R0-step"
# OOM mitigation (wake429 lesson): before serving the RL ckpt, tear down the
# vLLM serve on this GPU (frees a card -> fewer concurrent serves). Empty=skip.
PRE_TEARDOWN_GPU=""
ANALYSIS_OUTPUT="/tmp/posttrain_5run_eval/5run_rl_analysis.json"
DRY_RUN=0; STATUS_ONLY=0

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)            DRY_RUN=1 ;;
    --status)             STATUS_ONLY=1 ;;
    --grpo-pid)           GRPO_PID="$2"; shift ;;
    --eval-chain-pid)     EVAL_CHAIN_PID="$2"; shift ;;
    --rl-run-dir)         RL_RUN_DIR="$2"; shift ;;
    --gpu)                GPU="$2"; shift ;;
    --port)               PORT="$2"; shift ;;
    --base-label)         BASE_LABEL="$2"; shift ;;
    --rl-label-prefix)    RL_LABEL_PREFIX="$2"; shift ;;
    --served-name-prefix) SERVED_NAME_PREFIX="$2"; shift ;;
    --pre-teardown-gpu)   PRE_TEARDOWN_GPU="$2"; shift ;;
    --analysis-output)    ANALYSIS_OUTPUT="$2"; shift ;;
    *) echo "unknown: $1"; exit 1 ;;
  esac
  shift
done

latest_ckpt() {
  # Pick the highest-numbered global_step_* dir under RL_RUN_DIR.
  find "$RL_RUN_DIR" -maxdepth 1 -type d -name 'global_step_*' 2>/dev/null \
    | sed 's#.*/global_step_##' | sort -n | tail -1 \
    | while read -r n; do [ -n "$n" ] && echo "$RL_RUN_DIR/global_step_$n"; done
}

if [ $STATUS_ONLY -eq 1 ]; then
  echo "[status] GRPO training PID=$GRPO_PID: $(kill -0 "$GRPO_PID" 2>/dev/null && echo RUNNING || echo DONE)"
  echo "[status] eval-chain PID=$EVAL_CHAIN_PID: $(kill -0 "$EVAL_CHAIN_PID" 2>/dev/null && echo RUNNING || echo DONE)"
  CKPT="$(latest_ckpt)"
  echo "[status] latest RL ckpt: ${CKPT:-<none yet>}"
  echo "[status] serve on GPU${GPU} port ${PORT}:"
  curl -s --max-time 3 "http://localhost:${PORT}/v1/models" 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "  (not serving)"
  exit 0
fi

echo "===== Post-RL Eval Chain Daemon @ $(date '+%F %T') ====="
echo "  grpo-pid=$GRPO_PID  eval-chain-pid=$EVAL_CHAIN_PID"
echo "  rl-run-dir=$RL_RUN_DIR  gpu=$GPU  port=$PORT  base-label=$BASE_LABEL"

if [ $DRY_RUN -eq 1 ]; then
  echo "[dry-run] Would: wait GRPO PID $GRPO_PID -> wait eval-chain PID $EVAL_CHAIN_PID ->"
  [ -n "$PRE_TEARDOWN_GPU" ] && echo "[dry-run]   pre-teardown vLLM serve on GPU${PRE_TEARDOWN_GPU} (OOM mitigation, wake429 lesson) ->"
  echo "[dry-run]   serve latest ckpt from $RL_RUN_DIR on GPU${GPU}:${PORT} (served-name=${SERVED_NAME_PREFIX}<N>) ->"
  echo "[dry-run]   run 5-run eval (label=${RL_LABEL_PREFIX}<N>) ->"
  echo "[dry-run]   compare vs $BASE_LABEL (McNemar + paired bootstrap) -> $ANALYSIS_OUTPUT"
  exit 0
fi

# ---- helpers ---------------------------------------------------------------

# Kill any vLLM api_server serve occupying GPU<g> (frees the card + its RAM).
# Mirrors baize_posttrain_r2_autofire_chain.sh::kill_gpu_serve.
kill_gpu_serve() {
  local g="$1"
  local pids
  pids=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits -i "$g" 2>/dev/null | tr -d ' ')
  [ -z "$pids" ] && { echo "[chain] GPU${g} already free (no compute-apps)."; return 0; }
  for pid in $pids; do
    local cmd
    cmd=$(ps -o args= -p "$pid" 2>/dev/null)
    if echo "$cmd" | grep -q "vllm.entrypoints.openai.api_server"; then
      echo "[chain] pre-teardown: killing vLLM serve PID $pid on GPU${g}..."
      kill -TERM "$pid" 2>/dev/null || true; sleep 4
      kill -9 "$pid" 2>/dev/null || true
    else
      echo "[chain] pre-teardown: GPU${g} PID $pid is not vLLM serve (skip): ${cmd:0:70}"
    fi
  done
}

wait_gpu_free() {
  local g="$1" i
  for i in $(seq 1 40); do
    local used
    used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i "$g" 2>/dev/null | tr -d ' ')
    if [ -z "$used" ] || [ "$used" -lt 1000 ]; then
      echo "[chain] GPU${g} free (memory.used=${used}MiB) after ${i}x6s"
      return 0
    fi
    sleep 6
  done
  echo "[chain] WARN: GPU${g} still not free after 4min (will attempt serve anyway)"
  return 0
}

# 1. Wait for GRPO training to finish (GPU7 must free before serve).
echo "[chain] Waiting for GRPO training (PID $GRPO_PID) to finish..."
while kill -0 "$GRPO_PID" 2>/dev/null; do
  echo "[chain]   GRPO still running ($(date '+%T'))... sleeping 120s"
  sleep 120
done
echo "[chain] GRPO training finished at $(date '+%F %T')"

# Give CUDA a moment to release GPU memory.
sleep 15
GPU_USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i "$GPU" 2>/dev/null | tr -d ' ')
echo "[chain] GPU${GPU} memory.used=${GPU_USED}MiB after training exit"

# 2. Pick latest RL checkpoint.
CKPT="$(latest_ckpt)"
if [ -z "$CKPT" ] || [ ! -d "$CKPT" ]; then
  echo "[chain] FATAL: no global_step_* checkpoint found under $RL_RUN_DIR - aborting."
  exit 2
fi
STEP_N="$(basename "$CKPT" | sed 's/global_step_//')"
RL_LABEL="${RL_LABEL_PREFIX}${STEP_N}"
SERVED_NAME="${SERVED_NAME_PREFIX}${STEP_N}"
echo "[chain] Latest RL ckpt: $CKPT  (step=$STEP_N, label=$RL_LABEL)"

# 3. Wait for the existing SFT eval chain to finish (serialize providers.json).
echo "[chain] Waiting for existing eval chain (PID $EVAL_CHAIN_PID) to finish..."
while kill -0 "$EVAL_CHAIN_PID" 2>/dev/null; do
  echo "[chain]   eval-chain still running ($(date '+%T'))... sleeping 180s"
  sleep 180
done
echo "[chain] eval-chain finished at $(date '+%F %T') - providers.json now free."

# 3b. OOM mitigation (wake429 lesson: 4 concurrent vLLM serves + 8-parallel
#     cline eval workers crashed the R0 serve in CPU RAM). If requested, tear
#     down the vLLM serve on PRE_TEARDOWN_GPU (an orphaned/superseded serve,
#     e.g. the step60 SFT serve once step105-final is the baseline) BEFORE
#     bringing up the RL serve -> stays at 3 concurrent serves.
if [ -n "$PRE_TEARDOWN_GPU" ]; then
  echo "[chain] === Pre-teardown vLLM serve on GPU${PRE_TEARDOWN_GPU} (OOM mitigation) @ $(date '+%F %T') ==="
  kill_gpu_serve "$PRE_TEARDOWN_GPU"
  wait_gpu_free "$PRE_TEARDOWN_GPU"
fi

# 4. Serve the RL ckpt on GPU7:8095 via the (parameterized) SFT serve script.
echo "[chain] === Serving RL ckpt on GPU${GPU}:${PORT} @ $(date '+%F %T') ==="
bash "$SERVE_SCRIPT" --ckpt "$CKPT" --gpu "$GPU" --port "$PORT" --name "$SERVED_NAME" 2>&1
echo "[chain] serve launch returned (rc=$?) at $(date '+%F %T')"

# 5. Wait for serve health (vLLM load can take a few minutes).
echo "[chain] Waiting for /v1/models health on port ${PORT}..."
HEALTHY=0
for i in $(seq 1 60); do
  if curl -s --max-time 5 "http://localhost:${PORT}/v1/models" | grep -q "$SERVED_NAME"; then
    echo "[chain]   serve HEALTHY at $(date '+%F %T') (after ${i}x15s)"
    curl -s --max-time 5 "http://localhost:${PORT}/v1/models" | python3 -m json.tool 2>/dev/null
    HEALTHY=1
    break
  fi
  sleep 15
done
if [ $HEALTHY -eq 0 ]; then
  echo "[chain] FATAL: serve did not become healthy within 15min. Check /tmp/vllm_sft_serve_gpu${GPU}.log"
  exit 3
fi

# 6. Run 5-run eval (frozen protocol: 158 tasks, Pass@1, 2500s, 5-run, -p 8 -n).
echo "[chain] === Starting 5-run eval (label=$RL_LABEL) @ $(date '+%F %T') ==="
for run_n in 1 2 3 4 5; do
  echo "[chain] $RL_LABEL run${run_n} START @ $(date '+%F %T')"
  bash "$EVAL_SCRIPT" --endpoint "http://127.0.0.1:${PORT}/v1" --model "$SERVED_NAME" --label "$RL_LABEL" --run "$run_n" 2>&1
  echo "[chain] $RL_LABEL run${run_n} END @ $(date '+%F %T')"
done

# 7. Analysis: 5-run mean+-std + paired comparison vs SFT baseline (McNemar + bootstrap).
echo "[chain] === Running 5-run analysis (compare $RL_LABEL vs $BASE_LABEL) @ $(date '+%F %T') ==="
python3 "$ANALYSIS_SCRIPT" --compare "$RL_LABEL" "$BASE_LABEL" \
  --output "$ANALYSIS_OUTPUT" 2>&1
echo "[chain] === Analysis complete @ $(date '+%F %T') ==="
echo "[chain] Results: $ANALYSIS_OUTPUT"
echo "[chain] Per-run: /tmp/posttrain_5run_eval/${RL_LABEL}/run*/final_report.json"
echo "[chain] === Post-RL eval chain DONE ==="

