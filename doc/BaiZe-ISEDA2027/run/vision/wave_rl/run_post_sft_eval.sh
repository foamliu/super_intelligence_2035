#!/usr/bin/env bash
# run_post_sft_eval.sh — Post-SFT fixed-eval wrapper (vision wake#791, 2026-11-06).
#
# WHY THIS EXISTS:
#   The CPU SFT training (sft_train_wave.py PID 2882778) started BEFORE the
#   wake#790 eval-design-flaw fix was saved to disk.  The running process has
#   the OLD flawed evaluate_format_and_submit() in memory: it only generates
#   at the 1st assistant turn and looks for submit() there, but submit() is
#   always in the 4th turn  =>  submit_success_rate is always 0%  =>  the
#   eval_results.json the training writes at step3000 will be WRONG (pass=false).
#
#   The fix is on disk (eval_sft_wave.py + sft_train_wave.py) but cannot be
#   injected into the running process.  So this wrapper waits for the training
#   to FINISH, then re-runs the FIXED standalone eval (eval_sft_wave.py) on the
#   final checkpoint, OVERWRITING the flawed eval_results.json with the correct
#   one.  If the fixed eval PASSES (fmt>=90% AND submit>=70%), it relaunches the
#   GRPO chain (run_grpo_wave.sh, which itself safely waits for a free GPU).
#   If it FAILS, it logs and exits — the agent will handle a restart
#   (nsteps=24000) on the next wake.
#
# Safety: runs eval on CPU (GPU is occupied by pretrain until ~12/24).  flock so
# a second wake cannot double-fire it.
#
# Usage:  setsid bash run_post_sft_eval.sh > /tmp/post_sft_eval_launch.log 2>&1 < /dev/null &
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SFT_OUT="/nas_train/app.e0031982/datasets/baize-vision/out/wave_sft_stage1w"
LLM_2B="$SFT_OUT/qwen3vl_2b_text_extracted"
HOLDOUT="$SCRIPT_DIR/sft_holdout_500.jsonl"
EVAL_JSON="$SFT_OUT/eval_results.json"
LOG="$SFT_OUT/post_sft_eval.log"

exec 9>"$SFT_OUT/run_post_sft_eval.lock"
if ! flock -n 9; then
  echo "[$(date +%H:%M:%S)] Another run_post_sft_eval.sh holds the lock. Exiting." | tee -a "$LOG"
  exit 0
fi

SFT_PID="${1:-2882778}"

echo "============================================================" | tee -a "$LOG"
echo "[$(date '+%F %T')] post-SFT fixed-eval wrapper started" | tee -a "$LOG"
echo "  SFT_OUT:   $SFT_OUT" | tee -a "$LOG"
echo "  SFT_PID:   $SFT_PID" | tee -a "$LOG"
echo "  LLM_2B:    $LLM_2B" | tee -a "$LOG"
echo "  HOLDOUT:   $HOLDOUT" | tee -a "$LOG"
echo "  EVAL_JSON: $EVAL_JSON" | tee -a "$LOG"

# STEP 1: Wait for training to finish (eval_results.json appears OR PID dies).
echo "" | tee -a "$LOG"
echo "[Step 1] Waiting for SFT training to finish..." | tee -a "$LOG"
POLL=30
WAITED=0
MAX_WAIT=21600   # 6 h safety cap
while true; do
  if [ -f "$EVAL_JSON" ]; then
    echo "[$(date +%H:%M:%S)] eval_results.json appeared. Training DONE." | tee -a "$LOG"
    break
  fi
  if ! kill -0 "$SFT_PID" 2>/dev/null; then
    sleep 5
    if [ -f "$EVAL_JSON" ]; then
      echo "[$(date +%H:%M:%S)] PID $SFT_PID exited; eval_results.json present. DONE." | tee -a "$LOG"
      break
    fi
    echo "[$(date +%H:%M:%S)] ERROR: PID $SFT_PID gone, NO eval_results.json. Training CRASHED? Aborting." | tee -a "$LOG"
    exit 2
  fi
  if [ "$WAITED" -ge "$MAX_WAIT" ]; then
    echo "[$(date +%H:%M:%S)] TIMEOUT after ${WAITED}s. Aborting." | tee -a "$LOG"
    exit 3
  fi
  echo "[$(date +%H:%M:%S)] training still running (waited ${WAITED}s)..." | tee -a "$LOG"
  sleep "$POLL"
  WAITED=$((WAITED + POLL))
done

sleep 10

# STEP 2: Back up the flawed eval_results.json from the training.
FLAWED_BAK="$SFT_OUT/eval_results_flawed_training_$(date +%Y%m%d_%H%M%S).json"
cp -f "$EVAL_JSON" "$FLAWED_BAK"
echo "" | tee -a "$LOG"
echo "[Step 2] Backed up flawed training eval -> $FLAWED_BAK" | tee -a "$LOG"
cat "$FLAWED_BAK" | tee -a "$LOG"

# STEP 3: Find the latest checkpoint (highest step{N}).
LATEST_CKPT=$(ls -d "$SFT_OUT"/step[0-9]* 2>/dev/null | sort -V | tail -1)
if [ -z "$LATEST_CKPT" ] || [ ! -f "$LATEST_CKPT/adapter_config.json" ]; then
  echo "[$(date +%H:%M:%S)] ERROR: no valid step{N} ckpt with adapter_config.json. Aborting." | tee -a "$LOG"
  exit 4
fi
echo "" | tee -a "$LOG"
echo "[Step 3] Latest SFT checkpoint: $LATEST_CKPT" | tee -a "$LOG"

# STEP 4: Run the FIXED standalone eval (CPU) — overwrites eval_results.json.
#   GPU occupied by pretrain (ETA ~12/24) => eval on CPU.  224 cores free after
#   training exits.  max_eval=100 => 200 generations ~ 15-25 min on CPU.
echo "" | tee -a "$LOG"
echo "[Step 4] Running FIXED eval_sft_wave.py (CPU, max_eval=100)..." | tee -a "$LOG"
EVAL_LOG="$SFT_OUT/post_sft_fixed_eval_$(date +%Y%m%d_%H%M%S).log"
OMP_NUM_THREADS=64 python3 "$SCRIPT_DIR/eval_sft_wave.py" \
  --model_path "$LLM_2B" \
  --adapter_path "$LATEST_CKPT" \
  --eval_file "$HOLDOUT" \
  --output "$EVAL_JSON" \
  --device cpu \
  --max_eval 100 \
  --max_new_tokens 256 \
  2>&1 | tee "$EVAL_LOG" | tee -a "$LOG"
EVAL_RC=${PIPESTATUS[0]}
echo "[$(date +%H:%M:%S)] eval_sft_wave.py exit code: $EVAL_RC (log: $EVAL_LOG)" | tee -a "$LOG"
if [ "$EVAL_RC" -ne 0 ]; then
  echo "[$(date +%H:%M:%S)] ERROR: fixed eval failed (rc=$EVAL_RC). Restoring flawed backup; NOT starting GRPO. Agent inspects next wake." | tee -a "$LOG"
  cp -f "$FLAWED_BAK" "$EVAL_JSON"
  exit 5
fi

# STEP 5: Read pass/fail; relaunch GRPO chain if PASS.
echo "" | tee -a "$LOG"
echo "[Step 5] Reading fixed eval_results.json pass/fail..." | tee -a "$LOG"
FIXED_PASS=$(python3 -c "
import json
with open('$EVAL_JSON') as f:
    d = json.load(f)
print('true' if d.get('pass', False) else 'false')
print(f\"  FIXED format={d.get('format_correctness',0):.1%} submit={d.get('submit_success_rate',0):.1%} pass={d.get('pass',False)} n={d.get('total_evaluated',0)}\")
" 2>&1 | tee -a "$LOG")

if echo "$FIXED_PASS" | grep -q '^true'; then
  echo "[$(date +%H:%M:%S)] FIXED EVAL PASSED. Relaunching GRPO chain (run_grpo_wave.sh 8)..." | tee -a "$LOG"
  setsid bash "$SCRIPT_DIR/run_grpo_wave.sh" 8 > /tmp/grpo_chain_relaunch.log 2>&1 < /dev/null &
  GRPO_PID=$!
  echo "[$(date +%H:%M:%S)] GRPO chain relaunched: PID $GRPO_PID (see /tmp/grpo_chain_relaunch.log)" | tee -a "$LOG"
  echo "  GRPO chain will safely wait for a free GPU (pretrain ETA ~12/24) before training." | tee -a "$LOG"
else
  echo "[$(date +%H:%M:%S)] FIXED EVAL FAILED acceptance (fmt<90% OR submit<70%). NOT starting GRPO." | tee -a "$LOG"
  echo "  Per task: agent should restart SFT with nsteps=24000 on next wake." | tee -a "$LOG"
  echo "  Fixed eval summary:" | tee -a "$LOG"
  cat "$EVAL_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps({k:v for k,v in d.items() if k!='per_sample'}, indent=2))" | tee -a "$LOG"
fi

echo "" | tee -a "$LOG"
echo "[$(date '+%F %T')] post-SFT fixed-eval wrapper FINISHED." | tee -a "$LOG"
echo "============================================================" | tee -a "$LOG"
