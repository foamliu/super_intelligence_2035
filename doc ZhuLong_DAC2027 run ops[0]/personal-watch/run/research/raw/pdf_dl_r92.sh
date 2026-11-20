#!/usr/bin/env bash
# pdf_dl_r92.sh — 2026-10-15 日报 PDF **补跑下载器**（第九十二轮补跑 · curl 版）
#
# 背景（运维指令 2026-10-15）：上一轮因 `pkill -f 'arxiv.org/pdf'` 自匹配误杀 cline，
# 已下载的 PDF 被截断（`pdfinfo` 报 `Couldn't find trailer dictionary` / `pdftotext` 输出 0 字节）
# ⇒ 本轮**全部重下 + 严格校验**；坏文件一律删除（🚫 不把截断文件当成功记录）。
#
# 为什么用 curl 而不是 python-requests（本轮实测坑）：
#   `requests` + `stream=True` 连 export.arxiv.org（Fastly）时会**卡在首个 chunk 上不返回**
#   （socket ESTAB 但 0 字节流入，60s 无进展）；同一时刻 `curl -C -` 稳定 ~20 KB/s。
#   ⇒ 传输改用 curl（`-C -` 断点续传 + `--retry-all-errors` + `--speed-time` 掉速重连）。
#
# 本机现状：arXiv 带宽极慢（约 17–20 KB/s）⇒ 单篇数 MB 的 PDF 需数分钟，**必须后台跑**。
#
# 用法：nohup bash research/raw/pdf_dl_r92.sh > /tmp/pdf_dl_r92.log 2>&1 &
set -u

RUN_DIR="/home/liuyang/super_intelligence_2035/doc/personal-watch/run"
OUT="$RUN_DIR/research/pdf/2026-10-15"
IDS="2610.17637 2610.17202 2610.20193 2610.19587 2610.19863"
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
      -A "$UA" -o "$f" "https://export.arxiv.org/pdf/$id" >>/tmp/pdf_dl_r92.log 2>&1
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
for id in $IDS; do
  f="$OUT/$id.pdf"
  if [ -f "$f" ]; then
    log "$id OK  $(stat -c %s "$f") B  sha256=$(sha256sum "$f" | cut -c1-16)  $(pdfinfo "$f" 2>/dev/null | awk -F': *' '/^Pages:/{print "pages="$2}')"
  else
    log "$id FAIL (无文件)"
  fi
done
log "失败 $FAILED / 5"
exit $FAILED
