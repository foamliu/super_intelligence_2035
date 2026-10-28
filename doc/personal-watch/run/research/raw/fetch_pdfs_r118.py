#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百一十八轮（PM 晚 2）：下 2 篇 PDF 到 research/pdf/2026-10-28/ 并做完整性校验。

- 校验：HTTP 200 + Content-Type: application/pdf + `%PDF-` 头 + `%%EOF` 尾 + 字节 == Content-Length
- **分块读取 + 停滞检测**（2026-10-28 18:11 实测：单次 `read()` 在 ~2.97 MB 处停滞 >2min，
  改为 64 KB 分块 + 30s 读超时 + 停滞 45s 即判失败重试，绝不无限等）
- 校验失败即删除，绝不把截断文件当成功（2026-10-15 教训）
- `pdf/` 已在 research/.gitignore ⇒ 不入 git
"""
import hashlib
import socket
import sys
import time
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
OUT = BASE / "pdf" / "2026-10-28"
IDS = ["2610.37649", "2610.36668"]
CHUNK = 64 * 1024
READ_TIMEOUT = 30
STALL_LIMIT = 45  # 已由 socket 读超时（READ_TIMEOUT）实现，保留仅作文档
MAX_TRY = 3


def _download(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "research-watch/1.0 (mailto:foamliu@yeah.net)",
    })
    buf = bytearray()
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=READ_TIMEOUT) as resp:
        ctype = resp.headers.get("Content-Type", "")
        clen = resp.headers.get("Content-Length")
        status = resp.status
        while True:
            try:
                chunk = resp.read(CHUNK)
            except socket.timeout as exc:  # 单次读 > READ_TIMEOUT 无数据 ⇒ 判停滞
                raise TimeoutError("read stall > %ds at %d bytes: %r"
                                   % (READ_TIMEOUT, len(buf), repr(exc)[:80]))
            if not chunk:
                break
            buf.extend(chunk)
    return status, ctype, clen, bytes(buf), time.time() - t0


def fetch_one(aid):
    url = "https://arxiv.org/pdf/%s" % aid
    for attempt in range(1, MAX_TRY + 1):
        try:
            status, ctype, clen, raw, dt = _download(url)
        except Exception as exc:  # noqa: BLE001
            print("%s | attempt %d | DOWNLOAD ERROR %r" % (aid, attempt, repr(exc)[:160]))
            time.sleep(5)
            continue
        ok = (
            status == 200
            and ctype.startswith("application/pdf")
            and raw[:5] == b"%PDF-"
            and raw.rstrip()[-5:] == b"%%EOF"
            and (clen is None or int(clen) == len(raw))
        )
        print("%s | attempt %d | status=%s ct=%s bytes=%d clen=%s head=%s tail=%s | %.1fs | %s"
              % (aid, attempt, status, ctype, len(raw), clen, raw[:5],
                 raw.rstrip()[-5:], dt, "OK" if ok else "FAIL"))
        if not ok:
            time.sleep(5)
            continue
        path = OUT / ("%s.pdf" % aid)
        path.write_bytes(raw)
        print("saved %s | sha256=%s" % (path, hashlib.sha256(raw).hexdigest()))
        return True
    return False


def main():
    socket.setdefaulttimeout(READ_TIMEOUT)
    OUT.mkdir(parents=True, exist_ok=True)
    bad = []
    for i, aid in enumerate(IDS):
        if i:
            time.sleep(3)
        if not fetch_one(aid):
            bad.append(aid)
    if bad:
        print("FAILED: %s" % ",".join(bad))
        sys.exit(1)
    print("ALL %d OK" % len(IDS))


if __name__ == "__main__":
    main()

