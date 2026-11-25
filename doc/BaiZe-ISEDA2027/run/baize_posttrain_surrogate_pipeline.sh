#!/usr/bin/env bash
# baize_posttrain_surrogate_pipeline.sh — R156: End-to-end Surrogate Campaign Orchestrator
#
# Purpose: Single entry point that chains the BaiZe Stage(ii) SURROGATE campaign
#   Phase 1: 3-model baseline eval (MiniCPM5-2B @ :8098 + Qwen3.8-27B @ :8099 + cloud)
#            -> reports/report_posttrain_baseline_3model_zh.html
#   Phase 2: Surrogate SFT (MiniCPM5-2B, verl FSDP, GPU 6-7) -> SFT ckpt
#            + post-SFT eval -> reports/report_posttrain_sft_surrogate_zh.html
#   Phase 3: Surrogate RL/GRPO (verl 0.4.0, R0-R4 reward arms, GPU 4-7) from SFT ckpt
#            + post-RL eval + cheat-rate -> reports/report_posttrain_rl_surrogate_zh.html
#
# This orchestrator does NOT duplicate sub-scripts; it validates, sequences, and
# enforces gates between phases. Each phase delegates to its own launch script.
#
# Red lines (总纲 §5):
#   - 污染隔离: contamination gate must PASS before any training/eval data is used.
#   - 反作弊:   PreToolUse hook + cheat_rate.json reported for every eval/RL arm.
#   - 口径一致: 158 tasks / Pass@1 / 2500s / single-trace / 5-run / -p 8 -n (frozen).
#   - 预注册:   M1-M4 success ladder fixed before testing.
#   All reports MUST label "替身预演，收益不可迁移到 BaiZe".
#
# Sub-scripts (each has its own --dry-run):
#   Phase 1 : baize_posttrain_phase1_baseline.sh      (3-model eval, needs sandbox)
#   Phase 2 : baize_posttrain_sft_surrogate.sh        (verl FSDP SFT, GPU 6-7)
#   Phase 3 : baize_posttrain_rl_grpo_surrogate.sh    (verl GRPO, GPU 4-7, needs SFT ckpt)
#   Gate    : baize_posttrain_contamination_gate.sh   (pollution isolation)
#   Eval    : baize_posttrain_eval.sh                 (single-backbone eval, post-SFT/RL)
#
# Usage:
#   bash baize_posttrain_surrogate_pipeline.sh --dry-run        # validate entire chain
#   bash baize_posttrain_surrogate_pipeline.sh --status         # per-phase readiness
#   bash baize_posttrain_surrogate_pipeline.sh --phase1         # run baseline eval only
#   bash baize_posttrain_surrogate_pipeline.sh --phase2         # run SFT (+post-SFT eval)
#   bash baize_posttrain_surrogate_pipeline.sh --phase3         # run RL (+post-RL eval)
#   bash baize_posttrain_surrogate_pipeline.sh --all            # 1->2->3 sequential w/ gates
#   bash baize_posttrain_surrogate_pipeline.sh --phase2 --smoke # smoke mode for SFT
#
# ⚠️ Surrogate results are NOT transferable to BaiZe (MiniCPM5-2B Llama-arch != BaiZe Mamba2).
set -uo pipefail

SCRIPT_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/baize_posttrain_paths.sh"

# ============ sub-script paths ============
PHASE1_SCRIPT="$SCRIPT_DIR/baize_posttrain_phase1_baseline.sh"
PHASE2_SCRIPT="$SCRIPT_DIR/baize_posttrain_sft_surrogate.sh"
PHASE3_SCRIPT="$SCRIPT_DIR/baize_posttrain_rl_grpo_surrogate.sh"
CONTAM_SCRIPT="$SCRIPT_DIR/baize_posttrain_contamination_gate.sh"
EVAL_SCRIPT="$SCRIPT_DIR/baize_posttrain_eval.sh"

# ============ ckpt / data handoff ============
SFT_RUN_DIR="$SCRIPT_DIR/sft_surrogate_runs/minicpm5_pyaether_v1"
RL_RUN_DIR="$SCRIPT_DIR/rl_surrogate_runs/minicpm5_grpo_v1"
SFT_PARQUET="$SCRIPT_DIR/sft_pyaether_corpus_unified_v5v6v7.parquet"
ANNEAL_CORPUS="$SCRIPT_DIR/pyAether_api_anneal_corpus.jsonl"
REPORT_DIR="${BAIZE_REPORT_DIR:-$(dirname "$SCRIPT_DIR")/reports}"

# ============ endpoints / sandbox ============
EP_MINICPM5="http://localhost:8098/v1"
EP_QWEN38="http://localhost:8099/v1"
SANDBOX_HOST="${SANDBOX_HOST:-10.129.32.75}"
SANDBOX_PORT="${SANDBOX_PORT_HTTP:-8667}"

# ============ mode switches ============
DRY_RUN=0; STATUS=0; RUN_PHASE1=0; RUN_PHASE2=0; RUN_PHASE3=0; RUN_ALL=0; SMOKE=0
REWARD_ARM="R2"
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)  DRY_RUN=1 ;;
    --status)   STATUS=1 ;;
    --phase1)   RUN_PHASE1=1 ;;
    --phase2)   RUN_PHASE2=1 ;;
    --phase3)   RUN_PHASE3=1 ;;
    --all)      RUN_ALL=1 ;;
    --smoke)    SMOKE=1 ;;
    --reward-arm) REWARD_ARM="$2"; shift ;;
    *) echo "unknown arg: $1" ;;
  esac
  shift
done
if [ $DRY_RUN = 0 ] && [ $STATUS = 0 ] && [ $RUN_PHASE1 = 0 ] && [ $RUN_PHASE2 = 0 ] \
   && [ $RUN_PHASE3 = 0 ] && [ $RUN_ALL = 0 ]; then DRY_RUN=1; fi

# ============ helpers ============
ok(){ printf '  \033[32mPASS\033[0m %s\n' "$1"; }
no(){ printf '  \033[31mFAIL\033[0m %s\n' "$1"; }
wa(){ printf '  \033[33mWARN\033[0m %s\n' "$1"; }
hr(){ printf '  %s\n' "$(printf -- '-%.0s' $(seq 1 60))"; }

check_endpoint(){ # $1=url $2=name
  local code; code=$(curl -s -o /dev/null -m 3 -w '%{http_code}' "$1/models" 2>/dev/null || echo 000)
  if [ "$code" = "200" ]; then ok "endpoint $2 ($1) reachable (HTTP $code)"
  else no "endpoint $2 ($1) unreachable (HTTP $code)"; fi
}

check_sandbox(){
  if timeout 6 bash -c "echo > /dev/tcp/$SANDBOX_HOST/$SANDBOX_PORT" 2>/dev/null; then
    ok "sandbox $SANDBOX_HOST:$SANDBOX_PORT TCP OPEN"; return 0
  else
    no "sandbox $SANDBOX_HOST:$SANDBOX_PORT TCP CLOSED (Phase 1 eval + Phase 3 RL R1-R4 blocked)"; return 1
  fi
}

check_gpu_free(){ # $1=comma-idx-list $2=label
  local gpus="$1" label="$2" allfree=1
  for i in $(echo "$gpus" | tr ',' ' '); do
    local used; used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i "$i" 2>/dev/null | tr -d ' ')
    if [ -z "$used" ]; then wa "GPU $i: query failed"; allfree=0; continue; fi
    if [ "$used" -lt 1024 ]; then ok "GPU $i free (${used} MiB) — $label"
    else no "GPU $i occupied (${used} MiB) — $label blocked"; allfree=0; fi
  done
  return $allfree
}

find_latest_ckpt(){ find "$1" -type d -name 'global_step_*' 2>/dev/null | sort -t_ -k3 -n | tail -1; }
# ============ --status ============
do_status(){
  echo "===== BaiZe Stage(ii) Surrogate Campaign — STATUS @ $(date '+%F %T') ====="
  hr
  echo "  Phase 1 (3-model baseline eval):"
  local p1rep="$REPORT_DIR/report_posttrain_baseline_3model_zh.html"
  if [ -f "$p1rep" ]; then ok "report exists: $p1rep"; else
    if check_sandbox >/dev/null 2>&1; then wa "sandbox OPEN but no report yet — ready to run --phase1"
    else no "BLOCKED: sandbox CLOSED (no report)"; fi
  fi
  hr
  echo "  Phase 2 (surrogate SFT):"
  if [ -f "$SFT_PARQUET" ]; then ok "SFT parquet: $SFT_PARQUET ($(du -h "$SFT_PARQUET" 2>/dev/null | cut -f1))"
  else no "SFT parquet MISSING: $SFT_PARQUET"; fi
  local sftckpt; sftckpt=$(find_latest_ckpt "$SFT_RUN_DIR")
  if [ -n "$sftckpt" ]; then ok "SFT ckpt: $sftckpt"; else wa "no SFT ckpt yet (run --phase2)"; fi
  local p2rep="$REPORT_DIR/report_posttrain_sft_surrogate_zh.html"
  if [ -f "$p2rep" ]; then ok "report exists: $p2rep"; else wa "no SFT report yet"; fi
  hr
  echo "  Phase 3 (surrogate RL/GRPO):"
  if [ -n "$sftckpt" ]; then ok "SFT ckpt available for RL init: $sftckpt"
  else no "BLOCKED: no SFT ckpt (run --phase2 first)"; fi
  local rlckpt; rlckpt=$(find_latest_ckpt "$RL_RUN_DIR")
  if [ -n "$rlckpt" ]; then ok "RL ckpt: $rlckpt"; else wa "no RL ckpt yet (run --phase3)"; fi
  if [ -f "$RL_RUN_DIR/cheat_rate.json" ]; then ok "cheat_rate.json exists: $RL_RUN_DIR/cheat_rate.json"
  else wa "no cheat_rate.json yet"; fi
  local p3rep="$REPORT_DIR/report_posttrain_rl_surrogate_zh.html"
  if [ -f "$p3rep" ]; then ok "report exists: $p3rep"; else wa "no RL report yet"; fi
  hr
  echo "  Gates:"; check_sandbox
  echo "  Endpoints:"
  check_endpoint "$EP_MINICPM5" "MiniCPM5-2B (Phase1/eval)"
  check_endpoint "$EP_QWEN38" "Qwen3.8-27B (Phase1)"
  echo
}

# ============ --dry-run ============
do_dry_run(){
  echo "===== BaiZe Stage(ii) Surrogate Campaign — DRY-RUN @ $(date '+%F %T') ====="
  echo "  ⚠️ 替身预演，收益不可迁移到 BaiZe (MiniCPM5-2B Llama-arch != BaiZe Mamba2)"
  hr
  echo "  [A] Sub-script existence + syntax:"
  local nsub=0 nfail=0
  for s in "$PHASE1_SCRIPT" "$PHASE2_SCRIPT" "$PHASE3_SCRIPT" "$CONTAM_SCRIPT" "$EVAL_SCRIPT"; do
    nsub=$((nsub+1)); local name; name=$(basename "$s")
    if [ ! -f "$s" ]; then no "$name MISSING"; nfail=$((nfail+1)); continue; fi
    if bash -n "$s" 2>/dev/null; then ok "$name syntax OK"; else no "$name syntax ERROR"; nfail=$((nfail+1)); fi
  done
  hr
  echo "  [B] Sub-script --dry-run (each phase validates its own deps):"
  echo "    --- Phase 1 (baseline eval) ---"
  bash "$PHASE1_SCRIPT" --dry-run 2>&1 | sed 's/^/      /' | head -30
  echo "    --- Phase 2 (SFT surrogate) ---"
  bash "$PHASE2_SCRIPT" --dry-run 2>&1 | sed 's/^/      /' | head -30
  echo "    --- Phase 3 (RL/GRPO surrogate) ---"
  bash "$PHASE3_SCRIPT" --dry-run 2>&1 | sed 's/^/      /' | head -30
  hr
  echo "  [C] Contamination gate:"
  if [ -f "$CONTAM_SCRIPT" ]; then bash "$CONTAM_SCRIPT" --dry-run 2>&1 | sed 's/^/      /' | head -15
  else no "contamination gate script MISSING"; fi
  hr
  echo "  [D] Serve endpoints (eval needs live model):"
  check_endpoint "$EP_MINICPM5" "MiniCPM5-2B :8098"
  check_endpoint "$EP_QWEN38" "Qwen3.8-27B :8099"
  hr
  echo "  [E] Sandbox gate (Phase 1 eval + Phase 3 RL R1-R4 hard dep):"
  check_sandbox
  hr
  echo "  [F] GPU readiness:"
  check_gpu_free "6,7" "Phase 2 SFT"
  check_gpu_free "4,5,6,7" "Phase 3 RL (full)"
  hr
  echo "  [G] Data assets:"
  if [ -f "$SFT_PARQUET" ]; then ok "SFT parquet: $(du -h "$SFT_PARQUET" | cut -f1)"; else no "SFT parquet MISSING"; fi
  if [ -f "$ANNEAL_CORPUS" ]; then ok "anneal corpus: $(du -h "$ANNEAL_CORPUS" | cut -f1)"; else wa "anneal corpus absent (Phase 0, not blocking surrogate)"; fi
  hr
  echo "  [H] vLLM / verl venvs:"
  if [ -x "$HOME/code/vllm_venv/bin/python" ]; then ok "vllm venv: $HOME/code/vllm_venv"; else no "vllm venv MISSING"; fi
  if [ -x "$HOME/code/verl_cu124_venv/bin/python" ]; then ok "verl venv: $HOME/code/verl_cu124_venv"; else no "verl venv MISSING"; fi
  hr
  echo "  [I] Ckpt handoff plan:"
  echo "    Phase 2 SFT out -> $SFT_RUN_DIR/global_step_*"
  echo "    Phase 3 RL  in  -> auto-detect latest SFT ckpt (detect_sft_ckpt())"
  echo "    Phase 3 RL  out -> $RL_RUN_DIR/global_step_* + cheat_rate.json"
  echo "    Final eval      -> bash baize_posttrain_eval.sh --endpoint <served-ckpt>"
  hr
  echo "  [J] Deliverables (milestone reports):"
  for r in report_posttrain_baseline_3model_zh.html report_posttrain_sft_surrogate_zh.html report_posttrain_rl_surrogate_zh.html; do
    if [ -f "$REPORT_DIR/$r" ]; then ok "$r exists"; else wa "$r pending"; fi
  done
  hr
  if [ $nfail -gt 0 ]; then echo "  RESULT: $nfail/$nsub sub-scripts FAILED — fix before running."
  else echo "  RESULT: all $nsub sub-scripts present + syntax OK. Remaining blockers EXTERNAL (sandbox tunnel / GPU release)."; fi
  echo
}
# ============ gate helpers for --phase* / --all ============
gate_contam(){
  if [ ! -f "$CONTAM_SCRIPT" ]; then no "contamination gate script missing"; return 1; fi
  bash "$CONTAM_SCRIPT" --dry-run >/dev/null 2>&1 && { ok "contamination gate PASS"; return 0; }
  no "contamination gate FAILED — aborting (red line §5.1)"; return 1
}

run_phase1(){
  echo "===== Phase 1: 3-model baseline eval ====="
  check_sandbox || { no "sandbox CLOSED — Phase 1 cannot run (code exec dep). Aborting."; return 1; }
  check_endpoint "$EP_MINICPM5" "MiniCPM5-2B" || return 1
  check_endpoint "$EP_QWEN38" "Qwen3.8-27B" || wa "Qwen3.8-27B down (will skip that backbone)"
  bash "$PHASE1_SCRIPT" "$@"
  echo "[Phase 1] deliverable: reports/report_posttrain_baseline_3model_zh.html"
}

run_phase2(){
  echo "===== Phase 2: surrogate SFT (+ post-SFT eval) ====="
  gate_contam || return 1
  [ -f "$SFT_PARQUET" ] || { no "SFT parquet MISSING — run prep first. Aborting."; return 1; }
  check_gpu_free "6,7" "Phase 2 SFT" || { no "GPU 6-7 not free (serve occupying per 17:10 order). Aborting."; return 1; }
  local args=(); [ $SMOKE = 1 ] && args+=(--smoke)
  bash "$PHASE2_SCRIPT" "${args[@]}" "$@"
  local sftckpt; sftckpt=$(find_latest_ckpt "$SFT_RUN_DIR")
  if [ -n "$sftckpt" ]; then
    ok "SFT ckpt produced: $sftckpt"
    echo "[Phase 2] post-SFT eval: serve ckpt -> baize_posttrain_eval.sh (needs sandbox)"
    echo "  SFT_CKPT=$sftckpt bash baize_posttrain_eval.sh --backbone sft-surrogate --endpoint <served>"
  else no "no SFT ckpt found after training — check $SFT_RUN_DIR"; fi
  echo "[Phase 2] deliverable: reports/report_posttrain_sft_surrogate_zh.html"
}

run_phase3(){
  echo "===== Phase 3: surrogate RL/GRPO (+ post-RL eval + cheat rate) ====="
  gate_contam || return 1
  local sftckpt; sftckpt=$(find_latest_ckpt "$SFT_RUN_DIR")
  if [ -n "$sftckpt" ]; then ok "SFT ckpt for RL init: $sftckpt"
  else no "no SFT ckpt — run --phase2 first. Aborting."; return 1; fi
  check_sandbox || wa "sandbox CLOSED — Phase 3 RL R1-R4 (sandbox-exec rewards) blocked; R0 format-only may run"
  check_gpu_free "4,5,6,7" "Phase 3 RL (full)" || { no "GPU 4-7 not free. Aborting."; return 1; }
  local args=(--sft-ckpt "$sftckpt" --reward-arm "$REWARD_ARM")
  [ $SMOKE = 1 ] && args+=(--smoke)
  bash "$PHASE3_SCRIPT" "${args[@]}"
  local rlckpt; rlckpt=$(find_latest_ckpt "$RL_RUN_DIR")
  [ -n "$rlckpt" ] && ok "RL ckpt produced: $rlckpt" || no "no RL ckpt found"
  [ -f "$RL_RUN_DIR/cheat_rate.json" ] && ok "cheat_rate.json: $RL_RUN_DIR/cheat_rate.json (red line §5.2)" \
    || wa "cheat_rate.json missing — must report cheat rate"
  echo "[Phase 3] deliverable: reports/report_posttrain_rl_surrogate_zh.html"
}

run_all(){
  echo "===== FULL surrogate campaign: Phase 1 -> 2 -> 3 (gated) ====="
  run_phase1 || { no "Phase 1 failed — HALTING campaign."; return 1; }
  hr
  run_phase2 || { no "Phase 2 failed — HALTING campaign (Phase 3 needs SFT ckpt)."; return 1; }
  hr
  run_phase3 || { no "Phase 3 failed — campaign incomplete."; return 1; }
  hr
  echo "===== Campaign complete. All 3 deliverables should now exist. ====="
  for r in report_posttrain_baseline_3model_zh.html report_posttrain_sft_surrogate_zh.html report_posttrain_rl_surrogate_zh.html; do
    [ -f "$REPORT_DIR/$r" ] && ok "$r" || no "$r MISSING"
  done
}

# ============ dispatch ============
if [ $STATUS = 1 ]; then do_status
elif [ $DRY_RUN = 1 ]; then do_dry_run
elif [ $RUN_ALL = 1 ]; then run_all
else
  [ $RUN_PHASE1 = 1 ] && run_phase1
  [ $RUN_PHASE2 = 1 ] && run_phase2
  [ $RUN_PHASE3 = 1 ] && run_phase3
fi

