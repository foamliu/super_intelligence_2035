#!/bin/bash
# 第 102 轮：下载 2 篇晚报论文 PDF（严格校验，防截断）
set -u
D=/home/liuyang/super_intelligence_2035/doc/personal-watch/run/research/pdf/2026-10-20
mkdir -p "$D"
for id in 2610.26781 2610.26851; do
  echo "== $id =="
  for try in 1 2 3; do
    curl -sSL --retry 2 --retry-delay 3 -m 300 \
      -A 'Mozilla/5.0 (research-agent; contact foamliu@yeah.net)' \
      -o "$D/$id.pdf" "https://arxiv.org/pdf/$id" 2>"$D/dl_$id.log"
    sz=$(stat -c%s "$D/$id.pdf" 2>/dev/null || echo 0)
    hdr=$(head -c 5 "$D/$id.pdf" 2>/dev/null)
    if [ "$hdr" = "%PDF-" ] && [ "$sz" -gt 100000 ]; then
      tail -c 1024 "$D/$id.pdf" | grep -q '%%EOF' && echo "OK $id bytes=$sz" && break
    fi
    echo "RETRY $id try=$try bytes=$sz hdr=$hdr"
    sleep 5
  done
done
