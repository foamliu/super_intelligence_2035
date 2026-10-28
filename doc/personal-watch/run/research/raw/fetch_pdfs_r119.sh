#!/usr/bin/env bash
# 第一百一十八轮（AM 早 3）：PDF 并行分段下载（补 2 篇）。
#
# 背景（2026-10-29 18:11–18:23 实测，全部如实记录）：
#   1) `arxiv.org` / `export.arxiv.org` 的 DNS 解析在本机偶发失效（直连 curl 20s 无响应、无 TCP 连接）；
#      用 `--resolve` 固定到实测可用 Fastly IP `151.101.67.42`（**TLS/SNI/Host 不变**）后可连。
#   2) 单连接带宽极低（≈2.7 KB/s）：`2610.37649` 共 5,773,268 B ⇒ 单流需 ≈35 min，且 `-C -` 续传
#      在服务端回 200（非 206）时会从头覆盖 ⇒ 反复归零。故改为 **HTTP Range 并行分段**（12 段并发）。
#   3) 服务端 `etag: "sha256:<hex>"` = 整文件 sha256 ⇒ 用它做**端到端**校验（比只看头尾更强）。
# 校验：分段拼接后 sha256 == etag 的 sha256；失败即删，绝不把截断文件当成功（2026-10-15 教训）。
# `pdf/` 已在 research/.gitignore ⇒ 不入 git。
set -u
cd "$(dirname "$0")/.." || exit 1
OUT="pdf/2026-10-29"
IP="151.101.67.42"
TMP="/tmp/pdfr119"
NSEG=12
mkdir -p "$OUT" "$TMP"

IDS=("2610.37647" "2610.37609" "2610.36114")

for aid in "${IDS[@]}"; do
  url="https://arxiv.org/pdf/$aid"
  hdr="$TMP/$aid.hdr"
  curl -sS --max-time 60 --resolve "arxiv.org:443:$IP" -r 0-0 -D "$hdr" -o /dev/null "$url" || true
  total=$(grep -i '^content-range:' "$hdr" | tr -d '\r' | sed 's#.*/##')
  etag=$(grep -i '^etag:' "$hdr" | tr -d '\r"' | awk '{print $2}' | sed 's/^sha256://')
  echo "$aid | total=${total:-?} | etag_sha256=${etag:-?}"
  if [ -z "${total:-}" ]; then echo "FAIL $aid（拿不到 Content-Range，跳过）"; continue; fi

  per=$(( (total + NSEG - 1) / NSEG ))
  rm -f "$TMP/$aid".part*
  for i in $(seq 0 $((NSEG - 1))); do
    s=$(( i * per )); e=$(( s + per - 1 ))
    [ "$e" -ge "$total" ] && e=$(( total - 1 ))
    echo "$i $s $e"
  done > "$TMP/$aid.ranges"

  # 每段最多重试 3 次（逐段重下，段内不受整文件归零影响）
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
  tail5=$(tail -c 5 "$TMP/$aid.pdf" | tr -d '\n')
  if [ "$size" = "$total" ] && [ "$head5" = "%PDF-" ] && [ "$tail5" = "%%EOF" ] && { [ -z "${etag:-}" ] || [ "$sha" = "$etag" ]; }; then
    cp "$TMP/$aid.pdf" "$OUT/$aid.pdf"
    echo "OK $OUT/$aid.pdf bytes=$size sha256=$sha"
  else
    echo "FAIL $aid（校验不过：bytes=$size/$total head=$head5 tail=$tail5 sha=$sha etag=${etag:-none}）"
  fi
done

