#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百二十四轮（PM 晚 2 · 科普）：PDF 分段下载 + **断点续传兜底**。

背景：本机到 arXiv 的 Fastly 边缘单连接极慢且会中途超时（实测 300s 只收到 2–500 KB），
r119 的 `xargs + curl` 方案在「某一段 3 次重试都用完」时会整篇失败。本脚本对**每一段**
做「Range 续传 + 最多 N 次补拉」，只要服务端支持 206 就能把段补满。

校验（缺一不可，绝不把截断文件当成功）：
  - 本地字节数 == 服务端 `Content-Range` total
  - 文件头 `%PDF-`
  - `pdfinfo` 能解析出 `Pages`
  - `pdftotext` 抽取字符数 > 2000
  - sha256 与 etag **并列记录**（CDN etag 有 hex / base64 两种口径，不一致时如实写「哈希未对齐」）

用法：`python3 research/raw/pdf_range_resume_r124.py <arXiv_ID> [nseg]`
产出：`research/pdf/2026-10-29/<id>.pdf`（`pdf/` 在 .gitignore ⇒ 不入 git）
"""
import hashlib
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

GOOD_IP = "151.101.67.42"
HOST = "arxiv.org"
BASE = Path(__file__).resolve().parent.parent  # research/
TMP = Path("/tmp/pdfr124rr")
OUT_DIR = BASE / "pdf" / "2026-10-31"

_orig = socket.getaddrinfo


def _gai(host, port, *args, **kwargs):
    if host == HOST:
        return _orig(GOOD_IP, port, *args, **kwargs)
    return _orig(host, port, *args, **kwargs)


socket.getaddrinfo = _gai

UA = {"User-Agent": "research-watch/1.0 (mailto:foamliu@yeah.net)"}


def head(aid):
    url = "https://%s/pdf/%s" % (HOST, aid)
    req = urllib.request.Request(url, headers=dict(UA, Range="bytes=0-0"))
    with urllib.request.urlopen(req, timeout=60) as resp:
        cr = resp.headers.get("Content-Range")
        etag = resp.headers.get("ETag")
    total = int(cr.rsplit("/", 1)[-1])
    return url, total, etag


def fetch_segment(url, path, s, e, attempts=40):
    """把 [s, e] 续传到 path；只用 Range，绝不整文件重下。"""
    want = e - s + 1
    for k in range(attempts):
        got = path.stat().st_size if path.exists() else 0
        if got == want:
            return True
        if got > want:  # 越界说明服务端没按 Range 回 ⇒ 删了重来
            path.unlink()
            got = 0
        req = urllib.request.Request(url, headers=dict(UA, Range="bytes=%d-%d" % (s + got, e)))
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                if resp.status not in (200, 206):
                    print("  seg [%d,%d] HTTP %s" % (s, e, resp.status), flush=True)
                    time.sleep(3)
                    continue
                with path.open("ab") as f:
                    while True:
                        chunk = resp.read(65536)
                        if not chunk:
                            break
                        f.write(chunk)
        except Exception as exc:  # noqa: BLE001
            print("  seg [%d,%d] try %d: %r" % (s, e, k + 1, exc)[:200], flush=True)
            time.sleep(2)
    return path.exists() and path.stat().st_size == want


def main():
    aid = sys.argv[1]
    nseg = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    TMP.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    url, total, etag = head(aid)
    print("%s | total=%d | etag=%s" % (aid, total, etag), flush=True)

    per = (total + nseg - 1) // nseg
    ranges = []
    for i in range(nseg):
        s = i * per
        e = min(s + per - 1, total - 1)
        ranges.append((i, s, e))

    from concurrent.futures import ThreadPoolExecutor

    def _one(r):
        i, s, e = r
        p = TMP / ("%s.part%d" % (aid, i))
        ok = fetch_segment(url, p, s, e)
        print("seg %d [%d,%d] %s %s" % (i, s, e, "OK" if ok else "FAIL",
                                        p.stat().st_size if p.exists() else 0), flush=True)
        return ok

    with ThreadPoolExecutor(max_workers=len(ranges)) as ex:
        list(ex.map(_one, ranges))


    parts = [TMP / ("%s.part%d" % (aid, i)) for i, _, _ in ranges]
    if any((not p.exists()) or p.stat().st_size != (r[2] - r[1] + 1) for p, r in zip(parts, ranges)):
        print("FAIL %s（分段不全，不合并）" % aid)
        return 1

    merged = TMP / ("%s.pdf" % aid)
    with merged.open("wb") as out:
        for p in parts:
            out.write(p.read_bytes())

    size = merged.stat().st_size
    sha = hashlib.sha256(merged.read_bytes()).hexdigest()
    head5 = merged.read_bytes()[:5].decode("latin-1")
    tail = merged.read_bytes()[-8:].decode("latin-1")
    try:
        info = subprocess.run(["pdfinfo", str(merged)], capture_output=True, text=True, timeout=120).stdout
        pages = [ln.split(":", 1)[1].strip() for ln in info.splitlines() if ln.startswith("Pages:")]
        pages = pages[0] if pages else None
        txt = subprocess.run(["pdftotext", str(merged), "-"], capture_output=True, text=True,
                             timeout=180).stdout
        chars = len("".join(txt.split()))
    except Exception as exc:  # noqa: BLE001
        pages, chars = None, 0
        print("  pdfinfo/pdftotext error: %r" % (exc,), flush=True)

    ok = (size == total and head5 == "%PDF-" and "%%EOF" in tail and pages and chars > 2000)
    print("bytes=%d/%d pages=%s chars=%d sha256=%s tail_ok=%s" %
          (size, total, pages, chars, sha, "%%EOF" in tail), flush=True)
    if not ok:
        print("FAIL %s（校验不过，文件删除）" % aid)
        merged.unlink(missing_ok=True)
        return 1
    dst = OUT_DIR / ("%s.pdf" % aid)
    dst.write_bytes(merged.read_bytes())
    print("OK %s bytes=%d pages=%s chars=%d sha256=%s etag_match=%s" %
          (dst, size, pages, chars, sha, etag is not None and sha in (etag or "")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
