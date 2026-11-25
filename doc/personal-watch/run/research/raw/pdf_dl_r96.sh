#!/usr/bin/env bash
# pdf_dl_r96.sh — 2026-10-17 日报 PDF 下载器（第九十六轮 PM · curl 版）
#
# 口径沿用 r94（见 research/raw/pdf_dl_r94.sh 头部注释）：
#   - 传输用 curl（`-C -` 断点续传）；端点 https://export.arxiv.org/pdf/<id>。
#   - 本机 arXiv 带宽约 17–20 KB/s ⇒ 数 MB 的 PDF 需数分钟，**必须后台跑**。
#   - 校验：%PDF- 头 + 字节 ≥ 50KB + pdfinfo 页数 + pdftotext ≥ 2000 字符；坏文件删除重下。
#   - ⚠️ 不使用 pkill -f；如需终止用 `pgrep -af '[p]df_dl_r96'` 看 PID 后 kill <PID>。
#
# 用法：nohup bash research/raw/pdf_dl_r96.sh > /tmp/pdf_dl_r96.log 2>&1 &
#
# ⚠️ 2026-10-17 18:13 修订：2610.22371（Gen4P，TOP-1）服务端 content-length = 38,108,462 B
#   （≈36.3 MB > 单封 20 MB 附件上限）⇒ **不附 PDF、正文给 abs 链接**，从 IDS 移除；
#   本机带宽 ≈13 KB/s 下该文件需 ≈50 min，附了也发不出 ⇒ 直接不做无谓下载。
set -u

RUN_DIR="/home/liuyang/super_intelligence_2035/doc/personal-watch/run"
OUT="$RUN_DIR/research/pdf/2026-10-17"
IDS="2610.21126 2610.20673 2610.22344 2610.22372"   # 22371 超 20MB 不附（见头部修订说明）
UA='Mozilla/5.0 (compatible; watch-research/1.0; +https://arxiv.org)'
MIN_BYTES=$((50 * 1024))
mkdir -p "$OUT"

log() { echo "[$(date +%H:%M:%S)] $*"; }

verify() {  # $1 = 文件路径；返回 0=OK
  local f="$1"
  [ -f "$f" ] || { echo "missing"; return 1; }
  local sz; sz=$(stat -c %s "$f")
  [ "$sz" -ge "$MIN_BYTES" ] || { echo "too small (${sz} B < ${MIN_BYTES})"; return 1; }
  [ "$(head -c 5 "$f")" = "%PDF-" ] || { echo "bad header"; return 1; }
  local pages txt
  pages=$(pdfinfo "$f" 2>/dev/null | awk -F': *' '/^Pages:/{print $2}')
  [ -n "$pages" ] || { echo "pdfinfo broken"; return 1; }
  txt=$(pdftotext "$f" - 2>/dev/null | wc -c)
  [ "$txt" -ge 2000 ] || { echo "pdftotext only ${txt} chars"; return 1; }
  echo "OK pages=${pages} text=${txt}chars"
  return 0
}

FAILED=0
for id in $IDS; do
  f="$OUT/$id.pdf"
  if [ -f "$f" ]; then
    note=$(verify "$f") && { log "$id: 现存文件已通过校验 ⇒ 跳过（$note）"; continue; }
    log "$id: 现存文件校验失败（$note）⇒ 删除重下"; rm -f "$f"
  fi
  for try in 1 2 3 4 5; do
    log "$id: 下载 try=$try（resume from $( [ -f "$f" ] && stat -c %s "$f" || echo 0) B）"
    curl -sS -C - \
      --retry 8 --retry-all-errors --retry-delay 3 \
      --speed-limit 500 --speed-time 45 --max-time 1800 \
      -A "$UA" -o "$f" "https://export.arxiv.org/pdf/$id" >>/tmp/pdf_dl_r96.log 2>&1
    note=$(verify "$f") && break
    log "$id: 第 $try 轮校验未过（$note）"
  done
  if note=$(verify "$f"); then
    log "$id: ✅ $note bytes=$(stat -c %s "$f") sha256=$(sha256sum "$f" | cut -c1-16)"
  else
    log "$id: ❌ 校验失败（$note）⇒ 删除"
    rm -f "$f"; FAILED=$((FAILED + 1))
  fi
done

log "==== 汇总 ===="
TOTAL=0
for id in $IDS; do
  f="$OUT/$id.pdf"
  if [ -f "$f" ]; then
    b=$(stat -c %s "$f"); TOTAL=$((TOTAL + b))
    log "$id OK  ${b} B  sha256=$(sha256sum "$f" | cut -c1-16)  $(pdfinfo "$f" 2>/dev/null | awk -F': *' '/^Pages:/{print "pages="$2}')"
  else
    log "$id FAIL (无文件)"
  fi
done
log "合计 $TOTAL B（$((TOTAL / 1024)) KB）｜ 失败 $FAILED / 5"
exit $FAILED
