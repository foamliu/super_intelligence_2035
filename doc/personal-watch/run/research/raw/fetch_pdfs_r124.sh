#!/usr/bin/env bash
# 第一百二十三轮（AM 早 3）：PDF 并行分段下载（3 篇）。
#
# 沿用 r118/r119/r120 实测口径：
#   1) `arxiv.org` DNS 在本机偶发失效 ⇒ `--resolve` 固定实测可用 Fastly IP `151.101.67.42`
#      （TLS/SNI/Host 与证书校验不变）；
#   2) 单连接带宽极低（历史实测 ≈2.7 KB/s）⇒ 改 **HTTP Range 并行分段**（12 段并发，逐段最多 3 次重试）；
#   3) 分段拼接后校验：字节数 == `Content-Range` total、头 `%PDF-`、尾 `%%EOF`、`pdfinfo`/`pdftotext` 可解析；
#      CDN `etag` 若是 `sha256:<hex>` 则**附加**比对（r120 实测曾出现不一致 ⇒ 只作附注，不单独作为失败判据；
#      完整性证据 = 结构校验 + 字节数一致，**不声称端到端哈希一致**）。
# 任一校验不过 ⇒ 删除、不记成功（2026-10-15 截断 PDF 教训）。
# `pdf/` 已在 research/.gitignore ⇒ 不入 git。
set -u
cd "$(dirname "$0")/.." || exit 1
OUT="pdf/2026-10-31"
IP="151.101.67.42"
TMP="/tmp/pdfr124"
NSEG=12
mkdir -p "$OUT" "$TMP"

IDS=("2610.40530" "2610.38957")

for aid in "${IDS[@]}"; do
  url="https://arxiv.org/pdf/$aid"
  hdr="$TMP/$aid.hdr"
  curl -sS --max-time 60 --resolve "arxiv.org:443:$IP" -r 0-0 -D "$hdr" -o /dev/null "$url" || true
  total=$(grep -i '^content-range:' "$hdr" | tr -d '\r' | sed 's#.*/##')
  etag=$(grep -i '^etag:' "$hdr" | tr -d '\r"' | awk '{print $2}' | sed 's/^sha256://')
  echo "== $aid | total=${total:-?} | etag_sha256=${etag:-?}"
  if [ -z "${total:-}" ]; then echo "FAIL $aid（拿不到 Content-Range，跳过）"; continue; fi

  per=$(( (total + NSEG - 1) / NSEG ))
  rm -f "$TMP/$aid".part*
  for i in $(seq 0 $((NSEG - 1))); do
    s=$(( i * per )); e=$(( s + per - 1 ))
    [ "$e" -ge "$total" ] && e=$(( total - 1 ))
    echo "$i $s $e"
  done > "$TMP/$aid.ranges"

  URL="$url" cat "$TMP/$aid.ranges" | URL="$url" xargs -P 12 -n 3 bash -c '
    i=$1; s=$2; e=$3; url=$URL; f='"$TMP"'/'"$aid"'.part$i
    for t in 1 2 3; do
      curl -sS --max-time 240 --resolve "arxiv.org:443:'"$IP"'" -r "$s-$e" -o "$f" "$url" && break
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
  tail_eof=$(tail -c 64 "$TMP/$aid.pdf" | tr -d '\n' | grep -c '%%EOF')
  hash_note="etag_none"
  if [ -n "${etag:-}" ]; then
    if [ "$sha" = "$etag" ]; then hash_note="etag_match"; else hash_note="etag_MISMATCH"; fi
  fi
  if [ "$size" = "$total" ] && [ "$head5" = "%PDF-" ] && [ "$tail_eof" -ge 1 ]; then
    cp "$TMP/$aid.pdf" "$OUT/$aid.pdf"
    echo "OK $OUT/$aid.pdf bytes=$size sha256=$sha $hash_note"
  else
    echo "FAIL $aid（校验不过：bytes=$size/$total head=$head5 eof_hits=$tail_eof sha=$sha $hash_note）"
  fi
done
