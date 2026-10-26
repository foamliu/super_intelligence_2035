#!/bin/bash
# migrate_4sources_to_nas_env.sh — 迁移 4 份新分词数据到 /nas_env (运维令 2026-10-26 13:1x)
#
# 复用 migrate_to_nas_env_fast.sh 的安全口径：
#   ① rsync -a --partial --bwlimit（不用 mv：跨挂载 mv = 复制+删除，中断两边都不完整）
#   ② 每源校验 .bin/.idx/.json 计数 + du -sb 总字节，全等才算成功
#   ③ 校验通过后才删源（先删 text/ 真身，再删 tokenized/ hardlink 名 → /nas_train 释放空间）
#   ④ 任一源失败 ⇒ 立即停（不 continue），源码一律不删
#   ⑤ flock 单实例锁 = /tmp/migrate_to_nas_env.lock（与旧迁移同锁，串行所有迁移，不抢带宽）
#
# 为什么新建脚本而不改 migrate_to_nas_env_fast.sh：
#   ① bash 按字节偏移增量读脚本，就地改运行中的脚本会读错位（AGENTS.md 铁律）
#   ② 4 个新源的「真身」是 text/<prefix>_s* 散文件（hardlink 进 tokenized/<dir>/），
#      结构与旧 5 源的「full_* 整目录」不同 ⇒ 需 hardlink→symlink 的两步删除
#
# 迁移对象（tokenized 镜像内 4 个 hardlink 目录，131 shard ≈ 4.05TB）：
#   tokenized/Ultra-FineWeb/ultrafineweb_en       (32 shard)  text/ufw_en_train_s*
#   tokenized/Ultra-FineWeb/ultrafineweb_l1_en_hq (94 shard)  text/ufw_l1_en_hq_train_s*
#   tokenized/Ultra-FineWeb/ultrafineweb_zh       (4 shard)   text/ufw_zh_train_s*
#   tokenized/UltraX-Preview/UltraX-AICC          (1 shard)   text/ultrax_aicc_train_s*
#
# 每源流程：
#   ① rsync -a --partial --bwlimit=300000  tokenized/<dir>/  ->  /nas_env/.../full_<name>/
#      （tokenized/<dir>/ 内是 text/ 的 hardlink；rsync -a 不带 -H ⇒ 按内容独立复制，/nas_env 得独立副本 + MANIFEST.json）
#   ② 校验 .bin/.idx/.json 计数 + du -sb 字节 全等
#   ③ rm text/<prefix>_s*.bin/.idx/.json  （真身；tokenized/ hardlink 仍持有 inode，link count→1，数据仍在 /nas_train）
#   ④ rm tokenized/<dir>/*.bin *.idx *.json （hardlink 名；link count→0，/nas_train 释放空间）
#      保留 tokenized/<dir>/ 目录本身 + MANIFEST.json（随后 build_tokenized_mirror.py 重建 per-file symlink + MANIFEST）
#
# 用法：
#   BWLIMIT=300000 setsid -f nohup bash migrate_4sources_to_nas_env.sh \
#     > /tmp/migrate_4sources_to_nas_env.log 2>&1 < /dev/null &
#   BWLIMIT 单位 KiB/s（rsync 默认）；0 = 不限速

set -uo pipefail

TOK_ROOT="/nas_train/app.e0031982/datasets/baize-data/tokenized"
TEXT_DIR="/nas_train/app.e0031982/datasets/baize-data/text"
DST_BASE="/nas_env/app.e0031982/baize-data"
NICE_VAL="${NICE_VAL:-10}"
BWLIMIT="${BWLIMIT:-300000}"        # KiB/s; 300000 KiB/s ≈ 293 MB/s; 0 = unlimited
LOCK="/tmp/migrate_to_nas_env.lock"  # 与旧 migrate_to_nas_env_fast.sh 同锁 ⇒ 串行所有迁移

# 4 sources: name | tokenized subdir | text prefix | dst name
SOURCES=(
  "ufw_en|Ultra-FineWeb/ultrafineweb_en|ufw_en_train_s|full_ufw_en"
  "ufw_l1_en_hq|Ultra-FineWeb/ultrafineweb_l1_en_hq|ufw_l1_en_hq_train_s|full_ufw_l1_en_hq"
  "ufw_zh|Ultra-FineWeb/ultrafineweb_zh|ufw_zh_train_s|full_ufw_zh"
  "ultrax_aicc|UltraX-Preview/UltraX-AICC|ultrax_aicc_train_s|full_ultrax_aicc"
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

echo "=== MIGRATION(4SOURCES) START $(date '+%F %T') ==="
echo "tok_root=$TOK_ROOT"
echo "text_dir=$TEXT_DIR"
echo "dst_base=$DST_BASE"
echo "nice=$NICE_VAL bwlimit=${BWLIMIT}KiB/s ($(( BWLIMIT / 1024 )) MB/s) partial=on"
echo "sources: ${SOURCES[*]}"
echo ""
df -h /nas_train /nas_env | sed 's/^/[df] /'
echo ""

# ── rsync 选项（必须在循环之前定义；循环内引用 ${RSYNC_OPTS[@]}）──────────
#   旧 bug 修复（2026-10-26）：本块原误置于文件末尾（循环之后），
#   导致循环内 RSYNC_OPTS 未定义 → rsync 以裸参数运行（无 -a/-r）→ "skipping directory ."。
RSYNC_OPTS=(-a --partial --no-inc-recursive --info=progress2)
if [ "${BWLIMIT:-0}" -gt 0 ] 2>/dev/null; then
  RSYNC_OPTS+=(--bwlimit="$BWLIMIT")
fi
echo "[opts] rsync ${RSYNC_OPTS[*]}"
echo ""


IT=0
for entry in "${SOURCES[@]}"; do
  IFS='|' read -r name tok_sub text_pfx dst_name <<< "$entry"
  IT=$((IT + 1))
  SRC_TOK="$TOK_ROOT/$tok_sub"
  DST="$DST_BASE/$dst_name"

  echo "=== Migrating $name ($IT/${#SOURCES[@]}) ==="
  echo "  tok_dir=$SRC_TOK"
  echo "  text_pfx=$TEXT_DIR/${text_pfx}*"
  echo "  dst=$DST"

  if [ ! -d "$SRC_TOK" ]; then
    echo "  [$(date '+%T')] SKIP: tokenized dir not found: $SRC_TOK"
    echo ""; continue
  fi
  sample_bin=$(find "$SRC_TOK" -maxdepth 1 -name '*.bin' 2>/dev/null | head -1)
  if [ -n "$sample_bin" ] && [ -L "$sample_bin" ]; then
    echo "  [$(date '+%T')] SKIP: $SRC_TOK already per-file symlink mode -> $(readlink "$sample_bin")"
    echo ""; continue
  fi
  if [ -z "$sample_bin" ]; then
    echo "  [$(date '+%T')] SKIP: no .bin in $SRC_TOK (already cleaned? symlink rebuild pending)"
    echo ""; continue
  fi

  SRC_BINS=$(find "$SRC_TOK" -maxdepth 1 -name '*.bin' 2>/dev/null | wc -l)
  SRC_IDXS=$(find "$SRC_TOK" -maxdepth 1 -name '*.idx' 2>/dev/null | wc -l)
  SRC_JSONS=$(find "$SRC_TOK" -maxdepth 1 -name '*.json' ! -name 'MANIFEST.json' 2>/dev/null | wc -l)
  # 2026-10-26 修复：du -sb 跨 NFS 会因目录元数据大小不同而误报 MISMATCH（run1/run2 即因此停下）。
  # 改为对各 .bin/.idx/.json 逐文件 stat -c%s 求和（排除 MANIFEST.json，与计数口径一致），
  # 配合计数校验 ⇒ 任一文件尺寸不对即和值不等，足以判定 rsync 是否完整。
  SRC_BYTES=$(find "$SRC_TOK" -maxdepth 1 \( -name '*.bin' -o -name '*.idx' -o -name '*.json' \) ! -name 'MANIFEST.json' -exec stat -c%s {} + 2>/dev/null | awk '{s+=$1} END{print s+0}')
  echo "  [$(date '+%T')] src tok: ${SRC_BINS} .bin, ${SRC_IDXS} .idx, ${SRC_JSONS} .json, ${SRC_BYTES} bytes"

  echo "  [$(date '+%T')] starting rsync (bwlimit=${BWLIMIT}KiB/s)..."
  T0=$(date '+%s')
  nice -n "$NICE_VAL" rsync "${RSYNC_OPTS[@]}" "$SRC_TOK/" "$DST/" 2>&1 | sed 's/^/    /'
  RSYNC_RC=${PIPESTATUS[0]}
  T1=$(date '+%s')
  echo "  [$(date '+%T')] rsync rc=$RSYNC_RC, elapsed=$((T1 - T0))s"

  if [ "$RSYNC_RC" -ne 0 ]; then
    echo "  [$(date '+%T')] ERROR: rsync failed (rc=$RSYNC_RC). 源码一律不删；整条迁移停下。"
    exit 1
  fi

  DST_BINS=$(find "$DST" -maxdepth 1 -name '*.bin' 2>/dev/null | wc -l)
  DST_IDXS=$(find "$DST" -maxdepth 1 -name '*.idx' 2>/dev/null | wc -l)
  DST_JSONS=$(find "$DST" -maxdepth 1 -name '*.json' ! -name 'MANIFEST.json' 2>/dev/null | wc -l)
  # 2026-10-26 修复：同 SRC_BYTES，改 du -sb 为逐文件 stat -c%s 求和（跨 NFS 目录元数据不一致的根因）。
  DST_BYTES=$(find "$DST" -maxdepth 1 \( -name '*.bin' -o -name '*.idx' -o -name '*.json' \) ! -name 'MANIFEST.json' -exec stat -c%s {} + 2>/dev/null | awk '{s+=$1} END{print s+0}')
  echo "  [$(date '+%T')] dst:      ${DST_BINS} .bin, ${DST_IDXS} .idx, ${DST_JSONS} .json, ${DST_BYTES} bytes"

  OK=1
  [ "$SRC_BINS"  -ne "$DST_BINS"  ] && { echo "  [$(date '+%T')] MISMATCH: .bin  $SRC_BINS != $DST_BINS";   OK=0; }
  [ "$SRC_IDXS"  -ne "$DST_IDXS"  ] && { echo "  [$(date '+%T')] MISMATCH: .idx  $SRC_IDXS != $DST_IDXS";   OK=0; }
  [ "$SRC_JSONS" -ne "$DST_JSONS" ] && { echo "  [$(date '+%T')] MISMATCH: .json $SRC_JSONS != $DST_JSONS"; OK=0; }
  # DST_BYTES 可能为空（du 对不存在目录返回空）→ 用 -z 兜底，避免 [: integer expression expected
  if [ -z "$DST_BYTES" ] || [ "$SRC_BYTES" -ne "$DST_BYTES" ]; then
    echo "  [$(date '+%T')] MISMATCH: bytes $SRC_BYTES != ${DST_BYTES:-<missing>}"
    OK=0
  fi

  if [ "$OK" -ne 1 ]; then
    echo "  [$(date '+%T')] VERIFY FAILED: 不删源、不删 hardlink。两边都保留。整条迁移停下。"
    exit 1
  fi
  echo "  [$(date '+%T')] VERIFY OK: counts + bytes match"

  # ① 删 text/<prefix>_s*（真身；tokenized/ hardlink 仍持有 inode，link count→1，数据仍在 /nas_train）
  echo "  [$(date '+%T')] removing real source in text/: ${text_pfx}*"
  rm -f "$TEXT_DIR"/${text_pfx}*.bin "$TEXT_DIR"/${text_pfx}*.idx "$TEXT_DIR"/${text_pfx}*.json
  echo "  [$(date '+%T')] text/ ${text_pfx}* removed (remaining .bin for this prefix: $(ls "$TEXT_DIR"/${text_pfx}*.bin 2>/dev/null | wc -l))"

  # ② 删 tokenized/<dir>/*.bin *.idx *.json（hardlink 名；link count→0，/nas_train 释放空间）
  #    保留 tokenized/<dir>/ 目录本身 + MANIFEST.json（build_tokenized_mirror.py 随后重建 per-file symlink + MANIFEST）
  echo "  [$(date '+%T')] removing hardlink files in tokenized dir (keeping dir + MANIFEST.json)"
  find "$SRC_TOK" -maxdepth 1 -name '*.bin' -delete 2>/dev/null
  find "$SRC_TOK" -maxdepth 1 -name '*.idx' -delete 2>/dev/null
  find "$SRC_TOK" -maxdepth 1 -name '*.json' ! -name 'MANIFEST.json' -delete 2>/dev/null
  echo "  [$(date '+%T')] tokenized dir cleaned (remaining .bin: $(find "$SRC_TOK" -maxdepth 1 -name '*.bin' 2>/dev/null | wc -l), MANIFEST.json kept: $(ls "$SRC_TOK"/MANIFEST.json 2>/dev/null | wc -l))"

  echo "  [$(date '+%T')] DONE: $name migrated to $DST (per-file symlinks to be built by build_tokenized_mirror.py)"
  echo "  [df] $(df -h /nas_train /nas_env | tail -2 | tr '\n' ' ')"
  echo ""
done

echo "=== MIGRATION(4SOURCES) END $(date '+%F %T') ==="
echo ""
df -h /nas_train /nas_env | sed 's/^/[df] /'
echo ""
echo "NEXT STEPS (本脚本之外，由 agent 在迁移完成后执行):"
echo "  1. 更新 build_tokenized_mirror.py ENTRIES 第 31-34 行: src_dir→/nas_env/.../full_<name>, storage→\"symlink\""
echo "  2. 重跑 build_tokenized_mirror.py → 重建 per-file symlink + MANIFEST.json + INDEX.tsv"
echo "  3. 重跑 gen_data_mapping_md.py --measure → 刷新 DATA_MAPPING.md (storage=symlink)"
echo "  4. 重生成 reports/report_data_mapping_zh.html"
echo "  5. git add + commit (data migrate:) + push"
