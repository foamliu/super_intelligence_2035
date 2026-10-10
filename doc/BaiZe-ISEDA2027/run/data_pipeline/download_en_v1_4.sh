#!/usr/bin/env bash
# download_en_v1_4.sh — Per-snapshot download of Ultra-FineWeb en_v1_4 (110 CC-MAIN dirs)
# Launch: setsid -f nohup bash download_en_v1_4.sh > /tmp/en_v1_4_dl.log 2>&1 &
#
# Why per-snapshot: `hf download --include 'data/ultrafineweb_en_v1_4/*'` fails with
# `ValueError: min() arg is an empty sequence` because list_repo_tree times out
# for 56K+ files. Each snapshot dir has ~512 files, which is manageable.

# NOTE: No `set -e` — we handle errors ourselves with retry logic
export PATH="/nas_train/app.e0031982/miniforge3/envs/py310/bin:$PATH"
export https_proxy=http://172.19.92.25:13128
export http_proxy=http://172.19.92.25:13128
export HF_HUB_DOWNLOAD_TIMEOUT=120
export HF_HUB_ENABLE_HF_TRANSFER=1

LOCAL_DIR="/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb"
REPO="openbmb/Ultra-FineWeb"
BASE_INCLUDE="data/ultrafineweb_en_v1_4"

# Fetch snapshot list dynamically (non-recursive, fast for 110 dirs)
echo "[$(date '+%H:%M:%S')] Fetching snapshot list from HF API..."
SNAPSHOTS_STR=$(python3 -c "
from huggingface_hub import HfApi
api = HfApi()
entries = list(api.list_repo_tree('${REPO}', repo_type='dataset', path_in_repo='${BASE_INCLUDE}', recursive=False))
dirs = sorted([e.path.split('/')[-1] for e in entries if hasattr(e, 'path')])
print(' '.join(dirs))
" 2>&1)

if [ -z "$SNAPSHOTS_STR" ]; then
  echo "[$(date '+%H:%M:%S')] FATAL: Failed to fetch snapshot list from API"
  exit 1
fi

read -ra SNAPSHOTS <<< "$SNAPSHOTS_STR"
TOTAL=${#SNAPSHOTS[@]}
echo "[$(date '+%H:%M:%S')] Found ${TOTAL} snapshots"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] === en_v1_4 download START === ${TOTAL} snapshots"

COMPLETED=0
FAILED=0
SKIPPED=0

for i in "${!SNAPSHOTS[@]}"; do
  SNAP="${SNAPSHOTS[$i]}"
  IDX=$((i + 1))
  SNAP_DIR="${LOCAL_DIR}/data/ultrafineweb_en_v1_4/${SNAP}"

  # Check if already complete (>= 512 parquet files, no .incomplete)
  if [ -d "$SNAP_DIR" ]; then
    PARQUET_COUNT=$(ls "$SNAP_DIR"/*.parquet 2>/dev/null | wc -l)
    INCOMPLETE_COUNT=$(ls "$SNAP_DIR"/*.incomplete 2>/dev/null | wc -l)
    if [ "$PARQUET_COUNT" -ge 512 ] && [ "$INCOMPLETE_COUNT" -eq 0 ]; then
      echo "[$(date '+%H:%M:%S')] [${IDX}/${TOTAL}] ${SNAP}: SKIP (already ${PARQUET_COUNT}/512 parquet, 0 incomplete)"
      SKIPPED=$((SKIPPED + 1))
      continue
    fi
  fi

  echo "[$(date '+%H:%M:%S')] [${IDX}/${TOTAL}] ${SNAP}: downloading..."

  RETRY=0
  MAX_RETRIES=5
  while [ "$RETRY" -lt "$MAX_RETRIES" ]; do
    if hf download --repo-type dataset "$REPO" \
      --local-dir "$LOCAL_DIR" \
      --include "${BASE_INCLUDE}/${SNAP}/*" \
      2>&1; then
      echo "[$(date '+%H:%M:%S')] [${IDX}/${TOTAL}] ${SNAP}: DONE"
      COMPLETED=$((COMPLETED + 1))
      break
    else
      RETRY=$((RETRY + 1))
      echo "[$(date '+%H:%M:%S')] [${IDX}/${TOTAL}] ${SNAP}: FAIL (retry ${RETRY}/${MAX_RETRIES})"
      if [ "$RETRY" -lt "$MAX_RETRIES" ]; then
        sleep 30
      fi
    fi
  done

  if [ "$RETRY" -ge "$MAX_RETRIES" ]; then
    echo "[$(date '+%H:%M:%S')] [${IDX}/${TOTAL}] ${SNAP}: GIVE UP after ${MAX_RETRIES} retries"
    FAILED=$((FAILED + 1))
  fi
done

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === en_v1_4 download END === completed=${COMPLETED} skipped=${SKIPPED} failed=${FAILED} / total=${TOTAL}"

# Final count
FINAL_PARQUET=$(find "${LOCAL_DIR}/data/ultrafineweb_en_v1_4" -name '*.parquet' 2>/dev/null | wc -l)
FINAL_INCOMPLETE=$(find "${LOCAL_DIR}/data/ultrafineweb_en_v1_4" -name '*.incomplete' 2>/dev/null | wc -l)
echo "[$(date '+%H:%M:%S')] FINAL: ${FINAL_PARQUET} parquet files, ${FINAL_INCOMPLETE} .incomplete files"
