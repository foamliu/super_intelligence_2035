#!/usr/bin/env bash
# run_grpo_wave.sh — Chained launcher for Stage-2W GRPO (Phase 2 wave RL).
#
# Wake#624: Automates the Phase 1 → Phase 2 transition so that when the SFT
# poller (run_sft_wave.sh) finishes Stage-1W training, this script:
#   1. Detects SFT completion (eval_results.json appears in SFT output dir)
#   2. Checks SFT acceptance criteria (format >=90%, submit >=70%)
#   3. Finds latest SFT checkpoint (highest step{N}/ with adapter_config.json)
#   4. Safe GPU-wait (same guard as run_sft_wave.sh)
#   5. Launches GRPO training (grpo_train_wave.py)
#   6. After GRPO -> runs WaveQA-RL evaluation (waveqa_eval.py)
#
# If SFT fails acceptance, this script logs the failure and exits (does NOT
# start GRPO — per the task's gate).
#
# Usage:
#   setsid bash run_grpo_wave.sh [n_gpus] > /tmp/grpo_wave.log 2>&1 < /dev/null &
#   bash run_grpo_wave.sh 8        # 8 GPUs (default)
#
# Safety: uses a SEPARATE flock from run_sft_wave.sh so both can coexist.

set -euo pipefail

# ── flock guard: prevent duplicate GRPO launchers ──
LOCK_FILE="/nas_train/app.e0031982/datasets/baize-vision/out/wave_grpo_stage2w/run_grpo_wave.lock"
mkdir -p "$(dirname "$LOCK_FILE")"
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "[$(date +%H:%M:%S)] Another run_grpo_wave.sh instance holds the lock. Exiting." >&2
  exit 0
fi
echo "[$(date +%H:%M:%S)] Acquired exclusive lock (fd 9 -> $LOCK_FILE)."

N_GPUS="${1:-8}"
CONSECUTIVE_IDLE=3
IDLE_POLL_INTERVAL=60
UTIL_THRESHOLD=10
MEM_THRESHOLD=5000

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VISION_DIR="$(dirname "$SCRIPT_DIR")"

SFT_OUT="/nas_train/app.e0031982/datasets/baize-vision/out/wave_sft_stage1w"
GRPO_OUT="/nas_train/app.e0031982/datasets/baize-vision/out/wave_grpo_stage2w"
LLM_2B="$SFT_OUT/qwen3vl_2b_text_extracted"
HOLDOUT="$SCRIPT_DIR/sft_holdout_500.jsonl"
SFT_EVAL_JSON="$SFT_OUT/eval_results.json"

mkdir -p "$GRPO_OUT"
CHAIN_LOG="$GRPO_OUT/grpo_chain_$(date +%Y%m%d_%H%M%S).log"
GRPO_LOG="$GRPO_OUT/grpo_train_$(date +%Y%m%d_%H%M%S).log"

echo "=== Stage-2W GRPO Chained Launcher (wake#624) ===" | tee "$CHAIN_LOG"
echo "  SFT output:  $SFT_OUT" | tee -a "$CHAIN_LOG"
echo "  GRPO output: $GRPO_OUT" | tee -a "$CHAIN_LOG"
echo "  2B backbone: $LLM_2B" | tee -a "$CHAIN_LOG"
echo "  Chain log:   $CHAIN_LOG" | tee -a "$CHAIN_LOG"
echo "  Started:     $(date)" | tee -a "$CHAIN_LOG"

# ═══════════════════════════════════════════════════════════════
# STEP 1: Wait for SFT to complete (eval_results.json appears)
# ═══════════════════════════════════════════════════════════════
echo "" | tee -a "$CHAIN_LOG"
echo "[Step 1] Waiting for SFT completion (eval_results.json)..." | tee -a "$CHAIN_LOG"
SFT_WAIT_INTERVAL=120
SFT_WAIT_MAX=2592000  # 30 days max wait (GPU may be occupied ~20 days by R9 pretrain)
SFT_WAITED=0
while true; do
  if [ -f "$SFT_EVAL_JSON" ]; then
    echo "[$(date +%H:%M:%S)] SFT eval_results.json found!" | tee -a "$CHAIN_LOG"
    break
  fi
  if [ "$SFT_WAITED" -ge "$SFT_WAIT_MAX" ]; then
    echo "[$(date +%H:%M:%S)] TIMEOUT: SFT did not complete within ${SFT_WAIT_MAX}s. Exiting." | tee -a "$CHAIN_LOG"
    exit 1
  fi
  echo "[$(date +%H:%M:%S)] SFT not done yet (waited ${SFT_WAITED}s/$SFT_WAIT_MAX)..." | tee -a "$CHAIN_LOG"
  sleep "$SFT_WAIT_INTERVAL"
  SFT_WAITED=$((SFT_WAITED + SFT_WAIT_INTERVAL))
done

# ═══════════════════════════════════════════════════════════════
# STEP 2: Check SFT acceptance criteria
# ═══════════════════════════════════════════════════════════════
echo "" | tee -a "$CHAIN_LOG"
echo "[Step 2] Checking SFT acceptance criteria..." | tee -a "$CHAIN_LOG"
SFT_PASS=$(python3 -c "
import json, sys
with open('$SFT_EVAL_JSON') as f:
    d = json.load(f)
print('true' if d.get('pass', False) else 'false')
print(f\"  SFT format={d.get('format_correctness',0):.1%} submit={d.get('submit_success_rate',0):.1%} pass={d.get('pass',False)}\", file=sys.stderr)
" 2>&1 | tee -a "$CHAIN_LOG")

if echo "$SFT_PASS" | grep -q '^false'; then
  echo "[$(date +%H:%M:%S)] SFT FAILED acceptance criteria. NOT starting GRPO." | tee -a "$CHAIN_LOG"
  echo "  Per task gate: SFT must pass before GRPO. Check SFT eval_results.json." | tee -a "$CHAIN_LOG"
  exit 1
fi
echo "[$(date +%H:%M:%S)] SFT PASSED acceptance criteria. Proceeding to GRPO." | tee -a "$CHAIN_LOG"

# ═══════════════════════════════════════════════════════════════
# STEP 3: Find latest SFT checkpoint (highest step{N}/ with adapter_config.json)
# ═══════════════════════════════════════════════════════════════
echo "" | tee -a "$CHAIN_LOG"
echo "[Step 3] Finding latest SFT checkpoint..." | tee -a "$CHAIN_LOG"
LATEST_SFT_CKPT=$(python3 -c "
import os, glob
sft_dir = '$SFT_OUT'
step_dirs = []
for d in glob.glob(os.path.join(sft_dir, 'step*')):
    num = os.path.basename(d).replace('step', '')
    if num.isdigit() and os.path.exists(os.path.join(d, 'adapter_config.json')):
        step_dirs.append((int(num), d))
step_dirs.sort(key=lambda x: x[0], reverse=True)
if step_dirs:
    print(step_dirs[0][1])
elif os.path.exists(os.path.join(sft_dir, 'adapter_config.json')):
    print(sft_dir)
else:
    print('')
" 2>/dev/null)

if [ -z "$LATEST_SFT_CKPT" ]; then
  echo "[$(date +%H:%M:%S)] ERROR: No SFT checkpoint with adapter_config.json found under $SFT_OUT" | tee -a "$CHAIN_LOG"
  exit 1
fi
echo "  Latest SFT checkpoint: $LATEST_SFT_CKPT" | tee -a "$CHAIN_LOG"

# ═══════════════════════════════════════════════════════════════
# STEP 4: Safe GPU-wait (same guard as run_sft_wave.sh)
# ═══════════════════════════════════════════════════════════════
gpu_is_idle() {
  set +o pipefail
  local out
  out=$(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader,nounits 2>/dev/null | \
    awk -v n="$N_GPUS" -v ut="$UTIL_THRESHOLD" -v mt="$MEM_THRESHOLD" '
      BEGIN { idle=1 }
      NR<=n {
        if ($1+0 >= ut) { idle=0; print "busy_util"; exit }
        if ($2+0 >= mt) { idle=0; print "busy_mem"; exit }
      }
      END { if (idle) print "idle" }
    ' 2>/dev/null) || true
  set -o pipefail
  printf '%s' "$out"
}

echo "" | tee -a "$CHAIN_LOG"
echo "[Step 4] Waiting for GPU to be free before GRPO..." | tee -a "$CHAIN_LOG"
echo "  Guard: util<${UTIL_THRESHOLD}% AND mem<${MEM_THRESHOLD}MiB, ${CONSECUTIVE_IDLE}x @ ${IDLE_POLL_INTERVAL}s" | tee -a "$CHAIN_LOG"
idle_count=0
while true; do
  status="$(gpu_is_idle)"
  ts="$(date +%H:%M:%S)"
  if [ "$status" = "idle" ]; then
    idle_count=$((idle_count + 1))
    echo "[$ts] idle ($idle_count/$CONSECUTIVE_IDLE)" | tee -a "$CHAIN_LOG"
    if [ "$idle_count" -ge "$CONSECUTIVE_IDLE" ]; then
      echo "[$ts] GPU confirmed free. Starting GRPO." | tee -a "$CHAIN_LOG"
      break
    fi
  else
    if [ "$idle_count" -gt 0 ]; then
      echo "[$ts] $status -- resetting (was $idle_count)" | tee -a "$CHAIN_LOG"
    else
      echo "[$ts] $status -- waiting" | tee -a "$CHAIN_LOG"
    fi
    idle_count=0
  fi
  sleep "$IDLE_POLL_INTERVAL"
done

# ═══════════════════════════════════════════════════════════════
# STEP 5: Launch GRPO training
# ═══════════════════════════════════════════════════════════════
echo "" | tee -a "$CHAIN_LOG"
echo "[Step 5] Launching GRPO training..." | tee -a "$CHAIN_LOG"
cd "$VISION_DIR"
if [ "$N_GPUS" -gt 1 ]; then
  torchrun --nproc_per_node="$N_GPUS" wave_rl/grpo_train_wave.py \
    --sft_ckpt_dir "$LATEST_SFT_CKPT" \
    --model_path "$LLM_2B" \
    2>&1 | tee "$GRPO_LOG"
else
  CUDA_VISIBLE_DEVICES=0 python wave_rl/grpo_train_wave.py \
    --sft_ckpt_dir "$LATEST_SFT_CKPT" \
    --model_path "$LLM_2B" \
    2>&1 | tee "$GRPO_LOG"
fi
echo "[$(date +%H:%M:%S)] GRPO training finished." | tee -a "$CHAIN_LOG"
echo "  GRPO train log: $GRPO_LOG" | tee -a "$CHAIN_LOG"

# ═══════════════════════════════════════════════════════════════
# STEP 6: Find latest GRPO checkpoint + run WaveQA-RL evaluation
# ═══════════════════════════════════════════════════════════════
echo "" | tee -a "$CHAIN_LOG"
echo "[Step 6] Finding latest GRPO checkpoint..." | tee -a "$CHAIN_LOG"
LATEST_GRPO_CKPT=$(python3 -c "
import os, glob
grpo_dir = '$GRPO_OUT'
step_dirs = []
for d in glob.glob(os.path.join(grpo_dir, 'step*')):
    num = os.path.basename(d).replace('step', '')
    if num.isdigit() and os.path.exists(os.path.join(d, 'adapter_config.json')):
        step_dirs.append((int(num), d))
step_dirs.sort(key=lambda x: x[0], reverse=True)
if step_dirs:
    print(step_dirs[0][1])
else:
    print('')
" 2>/dev/null)

if [ -z "$LATEST_GRPO_CKPT" ]; then
  echo "[$(date +%H:%M:%S)] WARNING: No GRPO checkpoint found. Skipping WaveQA-RL eval." | tee -a "$CHAIN_LOG"
  exit 1
fi
echo "  Latest GRPO checkpoint: $LATEST_GRPO_CKPT" | tee -a "$CHAIN_LOG"

echo "" | tee -a "$CHAIN_LOG"
echo "[Step 6b] Running WaveQA-RL evaluation (300 questions)..." | tee -a "$CHAIN_LOG"
WAVEQA_OUT="$GRPO_OUT/waveqa_eval_$(date +%Y%m%d_%H%M%S).json"
cd "$VISION_DIR"
python wave_rl/waveqa_eval.py \
  --ckpt_dir "$LATEST_GRPO_CKPT" \
  --model_path "$LLM_2B" \
  --n_questions 300 \
  --output "$WAVEQA_OUT" \
  2>&1 | tee -a "$CHAIN_LOG" || true
echo "  WaveQA-RL results: $WAVEQA_OUT" | tee -a "$CHAIN_LOG"

echo "" | tee -a "$CHAIN_LOG"
echo "=== GRPO chain complete: $(date) ===" | tee -a "$CHAIN_LOG"
echo "  SFT checkpoint:  $LATEST_SFT_CKPT" | tee -a "$CHAIN_LOG"
echo "  GRPO checkpoint: $LATEST_GRPO_CKPT" | tee -a "$CHAIN_LOG"
echo "  WaveQA-RL eval:  $WAVEQA_OUT" | tee -a "$CHAIN_LOG"

