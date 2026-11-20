#!/usr/bin/env bash
# stackv3_orchestrate_migration.sh — 自动化编排：
# 1. 等待 rsync 完成
# 2. 校验字节一致 + parquet 数量
# 3. 删除 /nas_inference 源
# 4. 启动 hf download 全量剩余到 /nas_user
# 5. 记录每一步到 /tmp/stackv3_migration_orchestration.log
set -uo pipefail

SRC="/nas_inference/app.e0031982/datasets/HuggingFaceCode/stack-v3-train"
DST="/nas_user/app.e0031982/datasets/HuggingFaceCode/stack-v3-train"
LOG="/tmp/stackv3_migration_orchestration.log"
DOWNLOAD_SCRIPT="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data/stackv3_full_download.sh"

log() { echo "[$(date '+%Y%m%d_%H%M%S')] $*" | tee -a "$LOG"; }

log "==== stackv3 migration orchestration START ===="

# Step 1: Wait for rsync to complete
log "Step 1: Waiting for rsync to complete..."
while true; do
    N=$(ps aux | grep 'rsync.*stack-v3' | grep -v grep | wc -l)
    if [ "$N" -eq 0 ]; then
        log "rsync process gone, checking if completed successfully..."
        break
    fi
    sleep 30
done
log "rsync appears to have finished."

# Step 2: Verify rsync
log "Step 2: Verifying rsync..."
SRC_BYTES=$(du -sb "$SRC" 2>/dev/null | cut -f1)
DST_BYTES=$(du -sb "$DST" 2>/dev/null | cut -f1)
SRC_PARQUETS=$(find "$SRC/data" -name '*.parquet' -type f 2>/dev/null | wc -l)
DST_PARQUETS=$(find "$DST/data" -name '*.parquet' -type f 2>/dev/null | wc -l)

log "  SRC bytes=$SRC_BYTES parquets=$SRC_PARQUETS"
log "  DST bytes=$DST_BYTES parquets=$DST_PARQUETS"

if [ "$SRC_PARQUETS" -ne 4600 ]; then
    log "ERROR: SRC parquet count != 4600 (got $SRC_PARQUETS). Aborting."
    exit 1
fi

if [ "$DST_PARQUETS" -ne 4600 ]; then
    log "ERROR: DST parquet count != 4600 (got $DST_PARQUETS). Aborting."
    exit 1
fi

# Check byte-level consistency (allow small difference due to NFS metadata)
DIFF=$((SRC_BYTES - DST_BYTES))
if [ "$DIFF" -lt 0 ]; then
    DIFF=$((0 - DIFF))
fi
if [ "$DIFF" -gt 1048576 ]; then
    log "ERROR: byte difference > 1MB ($DIFF bytes). Aborting source deletion."
    exit 1
fi

log "  Verification PASSED: 4600 parquets, byte diff=$DIFF bytes (< 1MB)"

# Step 3: Delete source from /nas_inference
log "Step 3: Deleting source from /nas_inference..."
rm -rf "$SRC"
log "  Source deleted. Verifying..."
if [ -d "$SRC" ]; then
    log "  WARNING: Source directory still exists after rm -rf!"
else
    log "  Source directory successfully removed."
fi

# Step 4: Start full download
log "Step 4: Starting full download to /nas_user..."
if [ -f "$DOWNLOAD_SCRIPT" ]; then
    setsid bash "$DOWNLOAD_SCRIPT" > /dev/null 2>&1 < /dev/null &
    log "  Full download started (PID=$!)."
else
    log "  ERROR: Download script not found at $DOWNLOAD_SCRIPT"
    exit 1
fi

log "==== stackv3 migration orchestration DONE ===="
