#!/usr/bin/env bash
# 第一百二十轮（PM 晚 2 · 科普）：PDF 并行分段下载。
#
# 与 r119 的差异（修正 r119 已记录的两个真实异常）：
#   1) 尾部断言 `tail -c 5` 在文件以 `%%EOF\n` 结尾时被截成 `%EOF` ⇒ 误判 FAIL。
#      本轮改为 `tail -c 8 | tr -d '\n'` 后按子串匹配 `%%EOF`。
#   2) 完整性证据不只看 sha256 == etag（CDN etag 有 hex/base64 两种口径）：
#      以 **字节数 == Content-Range total** + `%PDF-` 头 + `%%EOF` 尾 + `pdfinfo` 页数 + `pdftotext` 字符数 为准；
#      sha256 与 etag 仅**并列记录**，不一致时如实写「结构校验通过、哈希未对齐」。
# 单连接带宽极低（≈2.7 KB/s 实测）⇒ HTTP Range 并行分段；失败即删，绝不把截断文件当成功。
# `pdf/` 已在 research/.gitignore ⇒ 不入 git。
set -u
cd "$(dirname "$0")/.." || exit 1
OUT="pdf/2026-10-29"
IP="151.101.67.42"
TMP="/tmp/pdfr120"
NSEG=8
mkdir -p "$OUT" "$TMP"

IDS=("2610.36195" "2610.37619")

for aid in "${IDS[@]}"; do
  url="https://arxiv.org/pdf/$aid"
  hdr="$TMP/$aid.hdr"
  curl -sS --max-time 60 --resolve "arxiv.org:443:$IP" -r 0-0 -D "$hdr" -o /dev/null "$url" || true
  total=$(grep -i '^content-range:' "$hdr" | tr -d '\r' | sed 's#.*/##')
  etag=$(grep -i '^etag:' "$hdr" | tr -d '\r"' | awk '{print $2}' | sed 's/^sha256://')
  echo "$aid | total=${total:-?} | etag=${etag:-?}"
  if [ -z "${total:-}" ]; then echo "FAIL $aid（拿不到 Content-Range，跳过）"; continue; fi

  per=$(( (total + NSEG - 1) / NSEG ))
  rm -f "$TMP/$aid".part*
  for i in $(seq 0 $((NSEG - 1))); do
    s=$(( i * per )); e=$(( s + per - 1 ))
    [ "$e" -ge "$total" ] && e=$(( total - 1 ))
    echo "$i $s $e"
  done > "$TMP/$aid.ranges"

  URL="$url" cat "$TMP/$aid.ranges" | URL="$url" xargs -P 8 -n 3 bash -c '
    i=$1; s=$2; e=$3; url=$URL; f='"$TMP"'/'"$aid"'.part$i
    for t in 1 2 3; do
      curl -sS --max-time 300 --resolve "arxiv.org:443:'"$IP"'" -r "$s-$e" -o "$f" "$url" && break
      sleep 3
    done
    want=$(( e - s + 1 )); got=$(stat -c %s "$f" 2>/dev/null || echo 0)
    if [ "$got" = "$want" ]; then echo "seg $i OK $got"; else echo "seg $i BAD got=$got want=$want"; fi
  ' _

  parts_ok=1
  for i in $(seq 0 $((NSEG - 1))); do
    f="$TMP/$aid.part$i"
    want=$(awk -v k="$i" '$1==k {print $3-$2+1}' "$TMP/$aid.ranges")
    got=$(stat -c %s "$f" 2>/dev/null || echo 0)
    [ "$got" = "$want" ] || { parts_ok=0; echo "  seg $i missing/short: $got/$want"; }
  done

  if [ "$parts_ok" != "1" ]; then echo "FAIL $aid（分段不全，不合并、不记成功）"; continue; fi

  cat $(for i in $(seq 0 $((NSEG - 1))); do echo "$TMP/$aid.part$i"; done) > "$TMP/$aid.pdf"
  size=$(stat -c %s "$TMP/$aid.pdf")
  sha=$(sha256sum "$TMP/$aid.pdf" | cut -d' ' -f1)
  head5=$(head -c 5 "$TMP/$aid.pdf")
  tail8=$(tail -c 8 "$TMP/$aid.pdf" | tr -d '\n')
  case "$tail8" in *'%%EOF'*) tail_ok=1 ;; *) tail_ok=0 ;; esac
  pages=$(pdfinfo "$TMP/$aid.pdf" 2>/dev/null | awk '/^Pages:/ {print $2}')
  chars=$(pdftotext "$TMP/$aid.pdf" - 2>/dev/null | tr -d '[:space:]' | wc -c)

  if [ "$size" = "$total" ] && [ "$head5" = "%PDF-" ] && [ "$tail_ok" = "1" ] \
     && [ -n "${pages:-}" ] && [ "${chars:-0}" -gt 2000 ]; then
    cp "$TMP/$aid.pdf" "$OUT/$aid.pdf"
    echo "OK $OUT/$aid.pdf bytes=$size pages=$pages chars=$chars sha256=$sha etag=${etag:-none}"
  else
    echo "FAIL $aid（校验不过：bytes=$size/$total head=$head5 tail8=$tail8 pages=${pages:-none} chars=${chars:-0}）"
  fi
done
