#!/bin/bash
# migrate_to_nas_env.sh — Migrate 5-source tokenized products from /nas_train to /nas_env
# Safety: rsync -a (not mv), verify shard count + bytes, create symlink, THEN rm source
# Per 2026-10-23 ④ operator instruction (user direct order)
#
# Usage: setsid -f nohup bash migrate_to_nas_env.sh > /tmp/migrate_to_nas_env.log 2>&1 &
#
# 5 sources (smallest first for quick validation):
#   full_ultradata_math_l3   292G  67 shards
#   full_ultradata_code_l3   481G  63 shards
#   full_ultradata_math_l1   615G  149 shards
#   full_ufw_l3              990G  154 shards
#   full_ultradata_code_l2   1.6T  141 shards
#   Total: ~3.98T → /nas_env (9.6T available, 9.6 > 4.38 = 3.98×1.1 ✓)

set -uo pipefail

SRC_BASE="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/data"
DST_BASE="/nas_env/app.e0031982/baize-data"
NICE_VAL=10
BWLIMIT=50000  # 50 MB/s per file (leaves NFS bandwidth for 85M download)

# Source directories in order (smallest first)
SOURCES=(
  "full_ultradata_math_l3"
  "full_ultradata_code_l3"
  "full_ultradata_math_l1"
  "full_ufw_l3"
  "full_ultradata_code_l2"
)

mkdir -p "$DST_BASE"

echo "=== MIGRATION START $(date '+%F %T') ==="
echo "src=$SRC_BASE"
echo "dst=$DST_BASE"
echo "nice=$NICE_VAL bwlimit=${BWLIMIT}KB/s"
echo "sources: ${SOURCES[*]}"
echo ""

# Pre-flight: check /nas_env available space
AVAIL_KB=$(df -P /nas_env | tail -1 | awk '{print $4}')
NEEDED_KB=$((3980000 * 1024 * 11 / 10))  # 3.98T × 1.1 in KB (rough)
echo "[preflight] /nas_env available: $((AVAIL_KB / 1024 / 1024)) TB"
echo "[preflight] needed (3.98T × 1.1): ~4.38 TB"
if [ "$AVAIL_KB" -lt "$NEEDED_KB" ]; then
  echo "[preflight] WARNING: space may be tight, but proceeding (individual checks below)"
fi
echo ""

for SRC_NAME in "${SOURCES[@]}"; do
  SRC="$SRC_BASE/$SRC_NAME"
  DST="$DST_BASE/$SRC_NAME"

  echo "=== Migrating $SRC_NAME ==="
  echo "[$(date '+%T')] src=$SRC"
  echo "[$(date '+%T')] dst=$DST"

  if [ ! -d "$SRC" ]; then
    echo "[$(date '+%T')] SKIP: source dir not found"
    continue
  fi

  # If dst already exists and is complete (has same shard count), skip rsync
  if [ -d "$DST" ]; then
    SRC_BINS=$(find "$SRC" -name '*.bin' 2>/dev/null | wc -l)
    DST_BINS=$(find "$DST" -name '*.bin' 2>/dev/null | wc -l)
    if [ "$SRC_BINS" -gt 0 ] && [ "$SRC_BINS" -eq "$DST_BINS" ]; then
      echo "[$(date '+%T')] dst already has $DST_BINS .bin (src has $SRC_BINS), verifying..."
    else
      echo "[$(date '+%T')] dst exists but incomplete ($DST_BINS/$SRC_BINS .bin), continuing rsync..."
    fi
  fi

  # Step 1: Count source shards
  SRC_BINS=$(find "$SRC" -name '*.bin' 2>/dev/null | wc -l)
  SRC_IDXS=$(find "$SRC" -name '*.idx' 2>/dev/null | wc -l)
  SRC_JSONS=$(find "$SRC" -name '*.json' 2>/dev/null | wc -l)
  SRC_BYTES=$(du -sb "$SRC" 2>/dev/null | awk '{print $1}')
  echo "[$(date '+%T')] source: $SRC_BINS .bin, $SRC_IDXS .idx, $SRC_JSONS .json, $SRC_BYTES bytes"

  # Step 2: rsync -a (archive mode, preserves perms/timestamps, not mv)
  echo "[$(date '+%T')] starting rsync..."
  nice -n "$NICE_VAL" rsync -a --bwlimit="$BWLIMIT" "$SRC/" "$DST/" 2>&1
  RSYNC_RC=$?
  echo "[$(date '+%T')] rsync completed, rc=$RSYNC_RC"

  if [ "$RSYNC_RC" -ne 0 ]; then
    echo "[$(date '+%T')] ERROR: rsync failed (rc=$RSYNC_RC), NOT deleting source"
    continue
  fi

  # Step 3: Verify destination
  DST_BINS=$(find "$DST" -name '*.bin' 2>/dev/null | wc -l)
  DST_IDXS=$(find "$DST" -name '*.idx' 2>/dev/null | wc -l)
  DST_JSONS=$(find "$DST" -name '*.json' 2>/dev/null | wc -l)
  DST_BYTES=$(du -sb "$DST" 2>/dev/null | awk '{print $1}')
  echo "[$(date '+%T')] dest: $DST_BINS .bin, $DST_IDXS .idx, $DST_JSONS .json, $DST_BYTES bytes"

  # Step 4: Verify match
  OK=1
  if [ "$SRC_BINS" -ne "$DST_BINS" ]; then
    echo "[$(date '+%T')] MISMATCH: .bin count $SRC_BINS != $DST_BINS"; OK=0
  fi
  if [ "$SRC_IDXS" -ne "$DST_IDXS" ]; then
    echo "[$(date '+%T')] MISMATCH: .idx count $SRC_IDXS != $DST_IDXS"; OK=0
  fi
  if [ "$SRC_JSONS" -ne "$DST_JSONS" ]; then
    echo "[$(date '+%T')] MISMATCH: .json count $SRC_JSONS != $DST_JSONS"; OK=0
  fi
  if [ "$SRC_BYTES" -ne "$DST_BYTES" ]; then
    echo "[$(date '+%T')] MISMATCH: bytes $SRC_BYTES != $DST_BYTES"; OK=0
  fi

  if [ "$OK" -eq 1 ]; then
    echo "[$(date '+%T')] VERIFY OK: all counts + bytes match"

    # Step 5: Create symlink at old path (so old paths still work)
    rm -rf "$SRC"
    ln -s "$DST" "$SRC"
    echo "[$(date '+%T')] SYMLINK: $SRC -> $DST"
    echo "[$(date '+%T')] DONE: $SRC_NAME migrated successfully"
  else
    echo "[$(date '+%T')] VERIFY FAILED: NOT deleting source, keeping both copies"
  fi

  echo ""
done

echo "=== MIGRATION END $(date '+%F %T') ==="
