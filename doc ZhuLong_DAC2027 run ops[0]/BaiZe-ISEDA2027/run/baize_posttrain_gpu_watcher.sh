#!/usr/bin/env bash
# baize_posttrain_gpu_watcher.sh — GPU availability watcher + NFS warm-up + auto-launch
#
# R46 (2026-11-08): T-1 deliverable. On 11/9, GPUs (4×A40) are released.
# This script:
#   1. Polls nvidia-smi every POLL_INTERVAL seconds for free GPU memory
#   2. When ≥ MIN_FREE_GPUS GPUs have ≥ MIN_FREE_MIB MiB free, triggers:
#      a. NFS warm-up (pre-cache model files, venv packages, data)
#      b. The master launch sequence (baize_posttrain_launch_11_9.sh)
#   3. Logs everything to WATCH_LOG for post-hoc diagnosis
#
# Usage:
#   bash baize_posttrain_gpu_watcher.sh                    # Watch + auto-launch
#   bash baize_posttrain_gpu_watcher.sh --dry-run          # Print what would happen
#   bash baize_posttrain_gpu_watcher.sh --warmup-only       # Only run NFS warm-up
#   bash baize_posttrain_gpu_watcher.sh --check-now         # Check GPU once + exit
#   bash baize_posttrain_gpu_watcher.sh --poll-interval 30  # Custom poll interval
#   bash baize_posttrain_gpu_watcher.sh --gpu-ids 0,1,2,3   # Specify GPU IDs for launch
#   bash baize_posttrain_gpu_watcher.sh --launch-steps 1-5  # Steps to run
#   bash baize_posttrain_gpu_watcher.sh --max-wait 86400    # Max wait seconds (default 24h)
#
# ⚠️ Surrogate RL results are NOT transferable to BaiZe.
set -uo pipefail

SCRIPT_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"
source "$SCRIPT_DIR/baize_posttrain_paths.sh"

# ── Defaults ──
DRY_RUN=0
WARMUP_ONLY=0
CHECK_NOW=0
POLL_INTERVAL=60
MIN_FREE_GPUS=4
MIN_FREE_MIB=40000
MAX_WAIT=86400
GPU_IDS=""
LAUNCH_STEPS="1-5"
WATCH_LOG=""

# ── Parse args ──
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)      DRY_RUN=1 ;;
    --warmup-only)  WARMUP_ONLY=1 ;;
    --check-now)    CHECK_NOW=1 ;;
    --poll-interval) POLL_INTERVAL="$2"; shift ;;
    --min-free-gpus) MIN_FREE_GPUS="$2"; shift ;;
    --min-free-mib)  MIN_FREE_MIB="$2"; shift ;;
    --max-wait)      MAX_WAIT="$2"; shift ;;
    --gpu-ids)       GPU_IDS="$2"; shift ;;
    --launch-steps)  LAUNCH_STEPS="$2"; shift ;;
    --log)           WATCH_LOG="$2"; shift ;;
    *) echo "Unknown arg: $1" >&2 ;;
  esac
  shift
done

# Set default watch log after args parsed (so --log can override)
if [ -z "$WATCH_LOG" ]; then
  WATCH_LOG="${BAIZE_EXP_DIR:-/tmp}/gpu_watcher_$(date '+%Y%m%d_%H%M%S').log"
fi

mkdir -p "$(dirname "$WATCH_LOG")"

log() {
  local ts
  ts="$(date '+%F %T')"
  echo "[$ts] $*" | tee -a "$WATCH_LOG"
}

# ── GPU check function ──
check_gpus() {
  local gpu_output
  gpu_output="$(nvidia-smi --query-gpu=index,memory.free,memory.total,utilization.gpu --format=csv,noheader,nounits 2>/dev/null)"
  if [ $? -ne 0 ]; then
    log "ERROR: nvidia-smi failed"
    return 1
  fi

  local free_count=0 total_count=0 details=""
  while IFS=',' read -r idx free_mib total_mib util; do
    idx=$(echo "$idx" | tr -d ' ')
    free_mib=$(echo "$free_mib" | tr -d ' ')
    total_mib=$(echo "$total_mib" | tr -d ' ')
    util=$(echo "$util" | tr -d ' ')
    total_count=$((total_count + 1))
    details="${details}GPU${idx}:${free_mib}MiB/${total_mib}MiB(${util}%) "
    if [ "$free_mib" -ge "$MIN_FREE_MIB" ] 2>/dev/null; then
      free_count=$((free_count + 1))
    fi
  done <<< "$gpu_output"

  echo "FREE_GPUS=$free_count TOTAL_GPUS=$total_count DETAILS=$details"
  log "GPU check: free=$free_count/$total_count (need ≥$MIN_FREE_GPUS with ≥${MIN_FREE_MIB}MiB free each)"
  log "  Details: $details"

  if [ "$free_count" -ge "$MIN_FREE_GPUS" ]; then
    return 0
  else
    return 1
  fi
}

# ── NFS warm-up function ──
nfs_warmup() {
  log "═══ NFS Warm-up Start ═══"

  local model_path="${BAIZE_MODEL_PATH:-/tmp/models/MiniCPM5-2B}"
  if [ -d "$model_path" ]; then
    log "  Warming model files: $model_path"
    if [ $DRY_RUN = 1 ]; then
      echo "  [dry-run] Would: find $model_path -type f -exec cat {} + > /dev/null"
    else
      find "$model_path" -type f -exec cat {} + > /dev/null 2>&1 &
      log "  Model warm-up PID=$! (background)"
    fi
  else
    log "  WARN: Model path not found: $model_path"
  fi

  local venv_site="${BAIZE_VENV_DIR:-$HOME/code/verl_cu124_venv}/lib/python*/site-packages"
  if ls -d $venv_site 2>/dev/null | head -1 > /dev/null; then
    local site_dir
    site_dir="$(ls -d $venv_site 2>/dev/null | head -1)"
    log "  Warming venv site-packages: $site_dir"
    if [ $DRY_RUN = 1 ]; then
      echo "  [dry-run] Would: warm critical packages in $site_dir"
    else
      for pkg in torch sglang verl flash_attn ray flashinfer numpy transformers; do
        if [ -d "$site_dir/$pkg" ]; then
          find "$site_dir/$pkg" -name '*.py' -exec cat {} + > /dev/null 2>&1 &
          log "    $pkg warmed (PID=$!)"
        fi
      done
    fi
  else
    log "  WARN: Venv site-packages not found: $venv_site"
  fi

  log "  Warming data files (parquet + jsonl)..."
  if [ $DRY_RUN = 1 ]; then
    echo "  [dry-run] Would: cat RL/SFT parquet + jsonl files"
  else
    for f in "$SCRIPT_DIR"/rl_pyaether_synth_v2.parquet \
             "$SCRIPT_DIR"/sft_pyaether_corpus.parquet \
             "$SCRIPT_DIR"/rl_pyaether_synth_v2.jsonl \
             "$SCRIPT_DIR"/sft_pyaether_corpus_v2.jsonl; do
      if [ -f "$f" ]; then
        cat "$f" > /dev/null 2>&1 &
        log "    $(basename "$f") warmed (PID=$!)"
      fi
    done
  fi

  local eval_ds="${BAIZE_EDA_BASE:-$HOME/code/eda_fastmcp}/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"
  if [ -f "$eval_ds" ]; then
    log "  Warming eval dataset: $eval_ds"
    if [ $DRY_RUN = 1 ]; then
      echo "  [dry-run] Would: cat $eval_ds > /dev/null"
    else
      cat "$eval_ds" > /dev/null 2>&1 &
      log "    eval dataset warmed (PID=$!)"
    fi
  fi

  if [ $DRY_RUN = 0 ]; then
    log "  Waiting for warm-up jobs to complete..."
    wait
    log "  Warm-up complete. NFS cache should be hot now."
  fi

  if [ $DRY_RUN = 0 ] && [ -d "${BAIZE_VENV_DIR:-$HOME/code/verl_cu124_venv}" ]; then
    local venv_python="${BAIZE_VENV_DIR:-$HOME/code/verl_cu124_venv}/bin/python"
    if [ -x "$venv_python" ]; then
      log "  Verifying torch import speed..."
      local import_time
      import_time=$("$venv_python" -c "
import time; t0=time.time(); import torch; t1=time.time()
print(f'{t1-t0:.1f}s'); print(f'cuda_available={torch.cuda.is_available()}')
" 2>&1)
      log "  torch import result: $import_time"
    fi
  fi
  log "═══ NFS Warm-up Done ═══"
}

# ── Launch trigger function ──
trigger_launch() {
  local gpu_flag=""
  [ -n "$GPU_IDS" ] && gpu_flag="--gpu-ids $GPU_IDS"

  log "═══ Launch Sequence Start ═══"
  log "  Script: baize_posttrain_launch_11_9.sh"
  log "  Steps: $LAUNCH_STEPS"
  log "  GPU IDs: ${GPU_IDS:-auto}"

  if [ $DRY_RUN = 1 ]; then
    echo "  [dry-run] Would run:"
    echo "    bash '$SCRIPT_DIR/baize_posttrain_launch_11_9.sh' --step $LAUNCH_STEPS $gpu_flag"
    return 0
  fi

  bash "$SCRIPT_DIR/baize_posttrain_launch_11_9.sh" --step "$LAUNCH_STEPS" $gpu_flag 2>&1 | tee -a "$WATCH_LOG"
  local rc=$?

  if [ $rc -eq 0 ]; then
    log "  PASS: Launch sequence completed successfully"
  else
    log "  FAIL: Launch sequence FAILED (rc=$rc)"
    log "  Manual recovery:"
    log "    1. Check SGLang: curl http://localhost:30000/health"
    log "    2. Check GPU: nvidia-smi"
    log "    3. Re-run failed step: bash baize_posttrain_launch_11_9.sh --step <N>"
  fi
  return $rc
}

# ── Main ──
log "BaiZe Post-Train GPU Watcher + Auto-Launch (R46)"
log "  Mode         : $([ $DRY_RUN = 1 ] && echo 'DRY-RUN' || echo 'EXECUTE')$([ $WARMUP_ONLY = 1 ] && echo ' (warmup-only)' || echo '')$([ $CHECK_NOW = 1 ] && echo ' (check-now)' || echo '')"
log "  Poll interval: ${POLL_INTERVAL}s"
log "  Min free GPUs: $MIN_FREE_GPUS (>= ${MIN_FREE_MIB} MiB each)"
log "  Max wait      : ${MAX_WAIT}s"
log "  Launch steps  : $LAUNCH_STEPS"
log "  GPU IDs       : ${GPU_IDS:-auto}"
log "  Watch log     : $WATCH_LOG"

if [ $CHECK_NOW = 1 ]; then
  log "One-shot GPU check"
  check_gpus
  exit $?
fi

if [ $WARMUP_ONLY = 1 ]; then
  nfs_warmup
  exit $?
fi

# ── Main watch loop ──
elapsed=0
iteration=0

while [ $elapsed -lt $MAX_WAIT ]; do
  iteration=$((iteration + 1))
  log "Watch iteration #$iteration (elapsed=${elapsed}s / max=${MAX_WAIT}s)"

  if check_gpus; then
    log "GPUs are free! Starting launch sequence..."
    nfs_warmup
    trigger_launch
    exit $?
  fi

  if [ $DRY_RUN = 1 ]; then
    log "[dry-run] Would sleep ${POLL_INTERVAL}s and check again. Exiting."
    exit 0
  fi

  sleep "$POLL_INTERVAL"
  elapsed=$((elapsed + POLL_INTERVAL))
done

log "Max wait time (${MAX_WAIT}s) exceeded. GPUs did not become free."
log "Manual launch: bash baize_posttrain_launch_11_9.sh --step $LAUNCH_STEPS ${GPU_IDS:+--gpu-ids $GPU_IDS}"
exit 1