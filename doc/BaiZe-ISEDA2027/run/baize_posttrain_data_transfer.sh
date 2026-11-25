#!/usr/bin/env bash
# baize_posttrain_data_transfer.sh — R113: Transfer SFT/Anneal data from .29/.12 to .17
# Usage:
#   bash baize_posttrain_data_transfer.sh --dry-run     # Show what would transfer
#   bash baize_posttrain_data_transfer.sh --check        # Check source availability
#   bash baize_posttrain_data_transfer.sh --sft          # Transfer SFT data only
#   bash baize_posttrain_data_transfer.sh --anneal       # Transfer anneal data only
#   bash baize_posttrain_data_transfer.sh --all          # Transfer everything
#   bash baize_posttrain_data_transfer.sh --verify       # Verify post-transfer
set -uo pipefail

SRC_HOST="${SRC_HOST:-10.239.2.29}"
SRC_BASE="/nas_train/app.e0031982/code/BaiZe-ISEDA2027"
DST_BASE="/nas_data/app.e0031982/code/BaiZe-ISEDA2027"
RSYNC_OPTS="-av --progress --partial --inplace --checksum"

DRY_RUN=0; CHECK_ONLY=0; DO_SFT=0; DO_ANNEAL=0; DO_ALL=0; VERIFY=0
for arg in "$@"; do
  case "$arg" in
    --dry-run)  DRY_RUN=1; RSYNC_OPTS="$RSYNC_OPTS --dry-run" ;;
    --check)    CHECK_ONLY=1 ;;
    --sft)      DO_SFT=1 ;;
    --anneal)   DO_ANNEAL=1 ;;
    --all)      DO_ALL=1 ;;
    --verify)   VERIFY=1 ;;
    *) echo "Unknown arg: $arg"; exit 1 ;;
  esac
done
[ $DO_ALL = 1 ] && { DO_SFT=1; DO_ANNEAL=1; }

if [ $CHECK_ONLY = 1 ]; then
  echo "=== Checking source on $SRC_HOST ==="
  for item in data/sft_agent_ultradata_2609 data/sft_ultradata_2605 data/pyAether_api_anneal data/mix_base data/full_ultradata_code_l3 data/full_ultradata_math_l3 data/tokenizer_eod nemo_experiments/baize2b/step_700000; do
    echo -n "  $item: "
    ssh -o ConnectTimeout=10 "$SRC_HOST" "test -e $SRC_BASE/$item && echo EXISTS || echo MISSING" 2>/dev/null || echo SSH_FAIL
  done
  echo "=== Checking destination on .17 ==="
  for item in data/sft_agent_ultradata_2609 data/sft_ultradata_2605 data/pyAether_api_anneal data/mix_base data/tokenizer_eod; do
    echo -n "  /nas_data/.../$item: "
    [ -e "$DST_BASE/$item" ] && echo EXISTS || echo MISSING
  done
  exit 0
fi

mkdir -p "$DST_BASE/data" 2>/dev/null || true

if [ $DO_SFT = 1 ]; then
  echo "===== SFT Data Transfer ====="
  echo "[1/2] SFT Agent (~23.89 GB)..."
  rsync $RSYNC_OPTS "${SRC_HOST}:${SRC_BASE}/data/sft_agent_ultradata_2609"* "$DST_BASE/data/" 2>&1 | tail -5
  echo "  rc=$?"
  echo "[2/2] SFT General (~75.87 GB)..."
  rsync $RSYNC_OPTS "${SRC_HOST}:${SRC_BASE}/data/sft_ultradata_2605"* "$DST_BASE/data/" 2>&1 | tail -5
  echo "  rc=$?"
fi

if [ $DO_ANNEAL = 1 ]; then
  echo "===== Anneal Data Transfer ====="
  for item in pyAether_api_anneal mix_base full_ultradata_code_l3 full_ultradata_math_l3 tokenizer_eod; do
    echo "[Anneal] $item..."
    rsync $RSYNC_OPTS "${SRC_HOST}:${SRC_BASE}/data/${item}"* "$DST_BASE/data/" 2>&1 | tail -3
    echo "  rc=$?"
  done
fi

if [ $VERIFY = 1 ]; then
  echo "===== Verification ====="
  for item in sft_agent_ultradata_2609 sft_ultradata_2605; do
    for ext in bin idx; do
      f="$DST_BASE/data/${item}.${ext}"
      if [ -f "$f" ]; then
        sz=$(stat -c%s "$f" 2>/dev/null || echo 0)
        echo "  OK $f ($sz bytes)"
      else
        echo "  MISSING $f"
      fi
    done
  done
fi
echo "===== Transfer complete @ $(date '+%F %T') ====="
