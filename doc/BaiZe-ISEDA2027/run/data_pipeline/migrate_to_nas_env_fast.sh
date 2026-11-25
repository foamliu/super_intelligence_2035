#!/bin/bash
# migrate_to_nas_env_fast.sh — 与 migrate_to_nas_env.sh 同口径的安全迁移，但**限速可调、默认大幅提高**。
#
# 为什么新建一个文件而不是改旧脚本：
#   bash 是**按字节偏移增量读脚本**的，进程运行中去改脚本文件会让它读到错位的行
#   ⇒ 必须"先停旧进程，再跑新脚本"，绝不能就地修改正在跑的 migrate_to_nas_env.sh。
#
# 背景（用户令 2026-10-24 18:1x）：「85M 下载优先级不高」
#   ⇒ 不再为 85M 预留 NFS 带宽，迁移从 --bwlimit=50000 (≈51 MB/s) 提到默认 300000 (≈307 MB/s)。
#   实测速率由 NFS/网卡上限决定（不设 0 是为了防止极端情况下打满存储影响其他线）。
#
# 用法：
#   BWLIMIT=300000 setsid -f nohup bash migrate_to_nas_env_fast.sh \
#     > /tmp/migrate_to_nas_env_fast.log 2>&1 < /dev/null &
#   BWLIMIT 单位 KiB/s（rsync 默认单位）；0 = 不限速
#
# 安全铁律（与 v1 完全一致，不降级）：
#   ① rsync -a（不用 mv：跨挂载 mv = 复制+删除，中断两边都不完整）
#   ② 每源校验 shard 数（.bin/.idx/.json）+ 总字节数，全等才算成功
#   ③ 校验通过后**才**删源、再建软链接（旧路径对 pretrain 仍可用）
#   ④ 任一源失败 ⇒ 立即停（不 continue 到下一源），源码一律不删
#   ⑤ flock 单实例锁 ⇒ 防止两个实例各占一份带宽（串行总量才可控）

set -uo pipefail

SRC_BASE="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/data"
DST_BASE="/nas_env/app.e0031982/baize-data"
NICE_VAL="${NICE_VAL:-10}"
BWLIMIT="${BWLIMIT:-300000}"        # KiB/s; 300000 KiB/s ≈ 307 MB/s; 0 = unlimited
LOCK="/tmp/migrate_to_nas_env.lock"

# 顺序不变（小 → 大，先用小源把 rsync→校验→软链接全流程走通）
SOURCES=(
  "full_ultradata_math_l3"
  "full_ultradata_code_l3"
  "full_ultradata_math_l1"
  "full_ufw_l3"
  "full_ultradata_code_l2"
)

mkdir -p "$DST_BASE" || { echo "[FATAL] cannot create $DST_BASE"; exit 1; }

# ── 单实例锁（flock 持有到进程退出；进程死了自动释放，不会残留死锁）────────
if command -v flock >/dev/null 2>&1; then
  exec 9>"$LOCK" || { echo "[FATAL] cannot open lock $LOCK"; exit 1; }
  if ! flock -n 9; then
    echo "[ABORT] another migration instance holds $LOCK — 不启第二个实例（串行才可控）"
    exit 1
  fi
else
  echo "[warn] flock not found, skipping single-instance lock"
fi

echo "=== MIGRATION(FAST) START $(date '+%F %T') ==="
echo "src=$SRC_BASE"
echo "dst=$DST_BASE"
echo "nice=$NICE_VAL bwlimit=${BWLIMIT}KiB/s ($(( BWLIMIT / 1024 )) MB/s) partial=on"
echo "sources: ${SOURCES[*]}"

# ── 前置：/nas_env 余量 ───────────────────────────────────────────────────
AVAIL_KB=$(df -P /nas_env | tail -1 | awk '{print $4}')
NEEDED_KB=$((3980000 * 1024 * 11 / 10))     # 3.98T x 1.1
echo "[preflight] /nas_env available: $((AVAIL_KB / 1024 / 1024)) GB-capacity-unit, needed(3.98T x1.1)=~4.38T"
if [ "${AVAIL_KB:-0}" -lt "$NEEDED_KB" ]; then
  echo "[preflight] WARNING: space may be tight (individual checks below still apply)"
fi

RSYNC_OPTS=(-a --partial --no-inc-recursive --info=progress2)
if [ "${BWLIMIT:-0}" -gt 0 ] 2>/dev/null; then
  RSYNC_OPTS+=(--bwlimit="$BWLIMIT")
fi
echo "[opts] rsync ${RSYNC_OPTS[*]}"
echo ""

IT=0
for SRC_NAME in "${SOURCES[@]}"; do
  SRC="$SRC_BASE/$SRC_NAME"
  DST="$DST_BASE/$SRC_NAME"
  IT=$((IT + 1))

  echo "=== Migrating $SRC_NAME ($IT/${#SOURCES[@]}) ==="

  # 已经是软链接 ⇒ 该源早已迁完
  if [ -L "$SRC" ]; then
    echo "[$(date '+%T')] SKIP: $SRC is already a symlink -> $(readlink "$SRC")"
    echo ""
    continue
  fi
  if [ ! -d "$SRC" ]; then
    echo "[$(date '+%T')] SKIP: source dir not found: $SRC"
    echo ""
    continue
  fi

  SRC_BINS=$(find "$SRC" -name '*.bin' 2>/dev/null | wc -l)
  SRC_IDXS=$(find "$SRC" -name '*.idx' 2>/dev/null | wc -l)
  SRC_JSONS=$(find "$SRC" -name '*.json' 2>/dev/null | wc -l)
  SRC_BYTES=$(du -sb "$SRC" 2>/dev/null | awk '{print $1}')
  echo "[$(date '+%T')] source: ${SRC_BINS} .bin, ${SRC_IDXS} .idx, ${SRC_JSONS} .json, ${SRC_BYTES} bytes"

  echo "[$(date '+%T')] starting rsync (bwlimit=${BWLIMIT}KiB/s)..."
  T0=$(date '+%s')
  nice -n "$NICE_VAL" rsync "${RSYNC_OPTS[@]}" "$SRC/" "$DST/" 2>&1
  RSYNC_RC=$?
  T1=$(date '+%s')
  echo "[$(date '+%T')] rsync completed, rc=$RSYNC_RC, elapsed=$((T1 - T0))s"

  if [ "$RSYNC_RC" -ne 0 ]; then
    echo "[$(date '+%T')] ERROR: rsync failed (rc=$RSYNC_RC). 源码一律不删；整条迁移停下，等人工/下轮处理。"
    exit 1
  fi

  DST_BINS=$(find "$DST" -name '*.bin' 2>/dev/null | wc -l)
  DST_IDXS=$(find "$DST" -name '*.idx' 2>/dev/null | wc -l)
  DST_JSONS=$(find "$DST" -name '*.json' 2>/dev/null | wc -l)
  DST_BYTES=$(du -sb "$DST" 2>/dev/null | awk '{print $1}')
  echo "[$(date '+%T')] dest:   ${DST_BINS} .bin, ${DST_IDXS} .idx, ${DST_JSONS} .json, ${DST_BYTES} bytes"

  OK=1
  [ "$SRC_BINS"  -ne "$DST_BINS"  ] && { echo "[$(date '+%T')] MISMATCH: .bin  $SRC_BINS != $DST_BINS";   OK=0; }
  [ "$SRC_IDXS"  -ne "$DST_IDXS"  ] && { echo "[$(date '+%T')] MISMATCH: .idx  $SRC_IDXS != $DST_IDXS";   OK=0; }
  [ "$SRC_JSONS" -ne "$DST_JSONS" ] && { echo "[$(date '+%T')] MISMATCH: .json $SRC_JSONS != $DST_JSONS"; OK=0; }
  [ "$SRC_BYTES" -ne "$DST_BYTES" ] && { echo "[$(date '+%T')] MISMATCH: bytes $SRC_BYTES != $DST_BYTES"; OK=0; }

  if [ "$OK" -eq 1 ]; then
    echo "[$(date '+%T')] VERIFY OK: counts + bytes match"
    rm -rf "$SRC"
    ln -s "$DST" "$SRC"
    echo "[$(date '+%T')] SYMLINK: $SRC -> $DST"
    echo "[$(date '+%T')] DONE: $SRC_NAME migrated"
  else
    echo "[$(date '+%T')] VERIFY FAILED: 不删源、不建软链接，两边都保留。整条迁移停下。"
    exit 1
  fi
  echo ""
done

echo "=== MIGRATION(FAST) END $(date '+%F %T') ==="
