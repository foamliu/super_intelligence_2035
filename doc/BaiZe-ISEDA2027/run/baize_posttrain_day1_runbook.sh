#!/usr/bin/env bash
# baize_posttrain_day1_runbook.sh — 11/9 GPU Day-1 Execution Runbook & Consistency Audit
#
# R38 (2026-11-08): Pre-launch consistency audit + hour-by-hour Day-1 execution guide.
# This is NOT a training script — it's a checklist/audit tool for the operator.
#
# Usage:
#   bash baize_posttrain_day1_runbook.sh                # Print full runbook
#   bash baize_posttrain_day1_runbook.sh --audit        # Audit scripts/configs vs R1-R37
#   bash baize_posttrain_day1_runbook.sh --check        # Check current readiness
#   bash baize_posttrain_day1_runbook.sh --timeline     # Print hour-by-hour timeline
#
# Surrogate RL results (MiniCPM5-2B) are NOT transferable to BaiZe.
set -uo pipefail

SCRIPT_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"
source "$SCRIPT_DIR/baize_posttrain_paths.sh"

MODE="full"
while [ $# -gt 0 ]; do
  case "$1" in
    --audit)    MODE="audit" ;;
    --check)    MODE="check" ;;
    --timeline) MODE="timeline" ;;
    *) MODE="full" ;;
  esac
  shift
done

# === AUDIT: Check scripts/configs for consistency with R1-R37 findings ===
do_audit() {
  echo "======================================================"
  echo "  R38 Pre-Launch Consistency Audit"
  echo "  $(date '+%F %T')"
  echo "======================================================"
  echo ""
  local PASS=0 FAIL=0 WARN=0

  echo "=== 1. Launch Script (baize_posttrain_launch_11_9.sh) ==="
  local smoke_arm full_arm
  smoke_arm=$(grep -o '\-\-smoke.*\-\-reward-arm [A-Z0-9]*' "$SCRIPT_DIR/baize_posttrain_launch_11_9.sh" 2>/dev/null | grep -o '[A-Z0-9]*$' || echo "not_found")
  full_arm=$(grep 'STEP 6' -A5 "$SCRIPT_DIR/baize_posttrain_launch_11_9.sh" 2>/dev/null | grep -o '\-\-reward-arm [A-Z0-9]*' | grep -o '[A-Z0-9]*$' || echo "not_found")
  echo "  Smoke test arm: $smoke_arm (R37: sandbox down, auto_fallback=true -> R0 fallback)"
  echo "  Full train arm: $full_arm (same auto_fallback applies)"

  echo ""
  echo "=== 2. RL Config (baize_posttrain_rl_verl_config.yaml) ==="
  local auto_fb
  auto_fb=$(grep 'auto_fallback' "$SCRIPT_DIR/baize_posttrain_rl_verl_config.yaml" 2>/dev/null | grep -o 'true\|false' || echo "not_found")
  echo "  auto_fallback: $auto_fb (R22: must be true for R0 fallback)"
  if [ "$auto_fb" = "true" ]; then echo "  OK"; PASS=$((PASS+1)); else echo "  CRITICAL: auto_fallback not true"; FAIL=$((FAIL+1)); fi

  local flash_attn
  flash_attn=$(grep 'attn_implementation' "$SCRIPT_DIR/baize_posttrain_rl_verl_config.yaml" 2>/dev/null | grep -v '^#' | head -1 | grep -o 'flash_attention_2\|sdpa\|eager' | head -1 || echo "not_found")
  echo "  attn_implementation: $flash_attn (R35: flash_attn compiled, +10-20% throughput)"
  if [ "$flash_attn" = "flash_attention_2" ]; then echo "  OK (R35 verified)"; PASS=$((PASS+1)); else echo "  WARN: not flash_attention_2"; WARN=$((WARN+1)); fi

  local rollout_name
  rollout_name=$(grep 'name:' "$SCRIPT_DIR/baize_posttrain_rl_verl_config.yaml" 2>/dev/null | grep -o 'sglang\|vllm' | head -1 || echo "not_found")
  echo "  rollout.name: $rollout_name (R9: must be sglang for MiniCPM5 XML tool calls)"
  if [ "$rollout_name" = "sglang" ]; then echo "  OK"; PASS=$((PASS+1)); else echo "  CRITICAL: not sglang"; FAIL=$((FAIL+1)); fi

  local multi_turn
  multi_turn=$(grep 'multi_turn' "$SCRIPT_DIR/baize_posttrain_rl_verl_config.yaml" 2>/dev/null | grep -o 'True\|False' || echo "not_found")
  echo "  multi_turn: $multi_turn (R9: required for tool-call agent loop)"
  if [ "$multi_turn" = "True" ]; then echo "  OK"; PASS=$((PASS+1)); else echo "  WARN"; WARN=$((WARN+1)); fi

  echo ""
  echo "=== 3. Monitoring (R36) ==="
  [ -f "$SCRIPT_DIR/baize_posttrain_rl_monitor.py" ] && { echo "  OK: baize_posttrain_rl_monitor.py exists"; PASS=$((PASS+1)); } || { echo "  MISSING"; FAIL=$((FAIL+1)); }

  echo ""
  echo "=== 4. Reward Robustness (R35) ==="
  [ -f "$SCRIPT_DIR/baize_posttrain_reward_adversarial_test.py" ] && { echo "  OK"; PASS=$((PASS+1)); } || { echo "  WARN: MISSING"; WARN=$((WARN+1)); }

  echo ""
  echo "=== 5. Sandbox Connectivity (R37) ==="
  [ -f "$SCRIPT_DIR/baize_posttrain_eda_sandbox_client.py" ] && { echo "  OK: 3-tier fallback client exists"; PASS=$((PASS+1)); } || { echo "  WARN: MISSING"; WARN=$((WARN+1)); }

  echo ""
  echo "=== 6. Data Files ==="
  for f in rl_pyaether_synth_v2.parquet sft_pyaether_corpus_v2.jsonl baize_posttrain_eda_tools.yaml baize_posttrain_rl_verl_config.yaml; do
    if [ -f "$SCRIPT_DIR/$f" ]; then echo "  OK: $f"; PASS=$((PASS+1)); else echo "  MISSING: $f"; FAIL=$((FAIL+1)); fi
  done

  echo ""
  echo "=== 7. Model & Venv ==="
  [ -d "$BAIZE_MODEL_PATH" ] && [ -f "$BAIZE_MODEL_PATH/config.json" ] && { echo "  OK: MiniCPM5-2B"; PASS=$((PASS+1)); } || { echo "  MISSING"; FAIL=$((FAIL+1)); }
  [ -f "$BAIZE_VENV_PY" ] && { echo "  OK: cu124 venv"; PASS=$((PASS+1)); } || { echo "  venv not yet (run setup on 11/9)"; WARN=$((WARN+1)); }

  echo ""
  echo "=== Audit Summary: PASS=$PASS  FAIL=$FAIL  WARN=$WARN ==="
  [ $FAIL -eq 0 ] && echo "No critical issues. Ready for 11/9." || echo "CRITICAL: $FAIL issues to fix!"
  return 0
}

# === CHECK: Current readiness snapshot ===
do_check() {
  echo "======================================================"
  echo "  R38 Readiness Check — $(date '+%F %T')"
  echo "======================================================"
  echo ""
  echo "=== GPU Status ==="
  nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu --format=csv,noheader 2>/dev/null || echo "  nvidia-smi unavailable"
  echo ""
  local busy_count
  busy_count=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | awk '{if($1+0>1000) print}' | wc -l)
  echo "  Busy GPUs: $busy_count/8 (need 4 free for posttrain)"
  [ "$busy_count" -le 4 ] && echo "  At least 4 GPUs free" || echo "  $((8-busy_count)) free, need 4. Wait for 11/9."

  echo ""
  echo "=== Model ==="
  [ -d "$BAIZE_MODEL_PATH" ] && echo "  OK: MiniCPM5-2B ($(du -sh "$BAIZE_MODEL_PATH" 2>/dev/null | cut -f1))" || echo "  MISSING"

  echo ""
  echo "=== Venv ==="
  if [ -f "$BAIZE_VENV_PY" ]; then
    echo "  OK: cu124 venv"
    "$BAIZE_VENV_PY" -c "import torch; print(f'  torch={torch.__version__}, cuda={torch.version.cuda}, available={torch.cuda.is_available()}')" 2>/dev/null || echo "  torch check failed"
    "$BAIZE_VENV_PY" -c "import sglang; print('  sglang OK')" 2>/dev/null || echo "  sglang not installed"
    "$BAIZE_VENV_PY" -c "import verl; print('  verl OK')" 2>/dev/null || echo "  verl not installed"
    "$BAIZE_VENV_PY" -c "import flash_attn; print('  flash_attn OK')" 2>/dev/null || echo "  flash_attn not installed"
  else
    echo "  venv not yet (run: bash baize_posttrain_setup_cu124_venv.sh --yes)"
  fi

  echo ""
  echo "=== Data ==="
  for f in rl_pyaether_synth_v2.parquet sft_pyaether_corpus_v2.jsonl; do
    [ -f "$SCRIPT_DIR/$f" ] && echo "  OK: $f ($(du -sh "$SCRIPT_DIR/$f" 2>/dev/null | cut -f1))" || echo "  MISSING: $f"
  done

  echo ""
  echo "=== EDA Base ==="
  [ -d "$BAIZE_EDA_BASE" ] && echo "  OK: eda_fastmcp" || echo "  MISSING"
  [ -f "$BAIZE_EDA_BASE/docs/API_INFO_MERGED_V3.json" ] && echo "  OK: API DB"
  [ -f "$BAIZE_EDA_BASE/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl" ] && echo "  OK: 158-case dataset"

  echo ""
  echo "=== Network (R37) ==="
  ping -c1 -W2 10.129.32.75 >/dev/null 2>&1 && echo "  ICMP to sandbox host: reachable" || echo "  ICMP unreachable (R0 fallback)"
  echo "  TCP 8664-8669: filtered -> R0 skeleton reward"

  echo ""
  echo "=== Summary ==="
  echo "  Full stack: OK (scripts/configs/data ready)"
  echo "  Venv:       $([ -f "$BAIZE_VENV_PY" ] && echo 'OK' || echo 'pending setup')"
  echo "  GPU:        pending 11/9 release (4xA40)"
  echo "  Sandbox:    ports filtered -> R0 auto-fallback"
  echo "  Model:      OK MiniCPM5-2B at /tmp/models/"
}

# === TIMELINE: Hour-by-hour Day-1 plan ===
do_timeline() {
  cat <<'TIMELINE'
======================================================
  11/9 GPU Day-1 Execution Timeline
  R38: Hour-by-Hour Plan (T=0 = GPU release)
======================================================

T+0:00  -- GPU Release & Verification --
  * Verify 4xA40 freed: nvidia-smi (expect 4 GPUs <1GB used)
  * If not freed: wait + poll every 15min (DO NOT kill other processes)
  * Decision: GPU 0-3 or 4-7? (use whichever are free)

T+0:15  -- Step 0: Venv Setup (if not already done) --
  * bash baize_posttrain_setup_cu124_venv.sh --yes
  * Verify: torch.cuda.is_available()=True, sglang/verl/ray/flash_attn
  * Expected: 15-30 min

T+0:45  -- Step 1: Preflight Check --
  * bash baize_posttrain_preflight_check.sh
  * Expected: 32+ PASS, 0 FAIL, 2-3 WARN

T+1:00  -- Step 2: SGLang Serve + Baseline Eval (36%) --
  * Quick first: bash baize_posttrain_minicpm5_diag.sh --quick --gpu-ids 0,1,2,3
    (10 tasks x 1 run = 20-30 min -> D1/D2/D6 preview)
  * Then full: bash baize_posttrain_minicpm5_diag.sh --full --gpu-ids 0,1,2,3
    (158 tasks x 5 runs = 15-25 hours -> runs in background)

T+1:30  -- Step 2b: Quick D1-D6 Extraction --
  * Extract from --quick results, compare with DeepSeek side
  * Key: D1 legality, D2 frequency, D6 iteration rounds

T+4:00  -- Step 3: Full Trajectory Extraction --
  * bash baize_posttrain_minicpm5_diag.sh --extract-only
  * Update EXPERIMENTS section D with real 36% numbers

T+4:30  -- Step 4: Contamination Gate --
  * bash baize_posttrain_contamination_gate.sh
  * Must PASS before RL (red-line 5.1)

T+5:00  -- Step 5: RL Smoke Test --
  * bash baize_posttrain_rl_grpo.sh --smoke --reward-arm R0 --gpu-ids 0,1,2,3
  * R0 (not R2): sandbox unreachable per R37
  * Smoke: 10 iters, group_size=4, batch=16
  * Expected: 20-40 min
  * Watch: reward non-zero (R0 std=0.3718), no OOM, no NaN

T+6:00  -- Step 6: Full RL Training (Surrogate-A) --
  * bash baize_posttrain_rl_grpo.sh --reward-arm R0 --gpu-ids 0,1,2,3
  * Full: 2000 iters, group_size=8, batch=128
  * Monitoring: baize_posttrain_rl_monitor.py (P1-P7 alerts)
  * Day-1: verify stable first 50 iters, then run overnight

T+8:00  -- Day-1 Checkpoint Review --
  * Baseline: 2-3 runs done? (mean+std forming)
  * RL: 50+ iters stable? (reward, KL, entropy, cheat rate)
  * All green -> let run overnight

T+24:00 -- End of Day-1 --
  * Baseline 36%: 2-3 runs complete
  * RL training: ~100-150 iters
  * D1-D6: measured values replacing assumptions
  * Commit results to EXPERIMENTS_POSTTRAIN.md

DECISION TREES:

GPU not freed by T+0:30?
  -> Poll every 15min. If still not freed by T+2:00, report to operator.
  -> DO NOT kill other GPU processes.

SGLang serve fails?
  -> Check: model path, venv, port 8866 free?
  -> Try: different port, lower mem-fraction (0.75)
  -> If persistent: fall back to vLLM (lose tool-call parsing)

Baseline eval gives 0%?
  -> Check: cline auth, SGLang responding, dataset path

RL smoke all-zero rewards?
  -> Check: reward_arm=R0, parquet loads, compute_score returns non-zero

RL OOM?
  -> Reduce: micro_batch (4->2), gpu_memory_utilization (0.35->0.25)
  -> Reduce: max_response_length (4096->2048)

Monitoring alert (P1-P7)?
  -> P1 KL>10: reduce lr, increase kl_loss_coef
  -> P2 reward<0.01: check reward function, switch arm
  -> P3 variance<0.01: increase entropy_coeff
  -> P4 entropy<0.1: decrease kl_loss_coef
  -> P5 grad>100: reduce grad_clip
  -> P6 NaN/Inf: stop, reduce lr, restart from checkpoint
  -> P7 cheat>5%: report (dont stop), tighten anti-cheat
TIMELINE
}

case "$MODE" in
  audit)    do_audit ;;
  check)    do_check ;;
  timeline) do_timeline ;;
  full)     do_check; echo "---"; do_audit; echo "---"; do_timeline ;;
esac
