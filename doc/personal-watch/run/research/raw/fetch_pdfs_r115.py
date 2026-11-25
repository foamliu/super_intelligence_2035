#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百一十五轮：下 3 篇 PDF 到 research/pdf/2026-10-27/ 并做双端完整性校验。

- 校验：HTTP 200 + Content-Type: application/pdf + `%PDF-` 头 + `%%EOF` 尾 + 字节 == Content-Length
- 校验失败即删除，绝不把截断文件当成功（2026-10-15 教训）
- `pdf/` 已在 research/.gitignore ⇒ 不入 git
"""
import sys
import time
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
OUT = BASE / "pdf" / "2026-10-27"
IDS = ["2610.32951", "2610.32881", "2610.32483"]


def fetch_one(aid):
    url = "https://arxiv.org/pdf/%s" % aid
    req = urllib.request.Request(url, headers={
        "User-Agent": "research-watch/1.0 (mailto:foamliu@yeah.net)",
    })
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=120) as resp:
        raw = resp.read()
        ctype = resp.headers.get("Content-Type", "")
        clen = resp.headers.get("Content-Length")
    dt = time.time() - t0
    ok = (
        ctype.startswith("application/pdf")
        and raw[:5] == b"%PDF-"
        and raw.rstrip()[-5:] == b"%%EOF"
        and (clen is None or int(clen) == len(raw))
    )
    print("%s | ct=%s | bytes=%d | clen=%s | head=%s | tail=%s | %.1fs | %s"
          % (aid, ctype, len(raw), clen, raw[:5], raw.rstrip()[-5:], dt,
             "OK" if ok else "FAIL"))
    if not ok:
        return False
    path = OUT / ("%s.pdf" % aid)
    path.write_bytes(raw)
    print("saved %s" % path)
    return True


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    bad = [a for a in IDS if not fetch_one(a)]
    time.sleep(3)
    if bad:
        print("FAILED: %s" % ",".join(bad))
        sys.exit(1)
    print("ALL 3 OK")


if __name__ == "__main__":
    main()
