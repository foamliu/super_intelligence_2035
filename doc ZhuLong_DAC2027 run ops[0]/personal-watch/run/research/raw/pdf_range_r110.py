#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pdf_range_r110.py — 并行 Range 分段下载（单连接 ~12KB/s 时提速 ~10x）
用法: python3 raw/pdf_range_r110.py <arxiv_id> <url> <out_path> [n_chunks]
- 先用 HEAD/Range 探总长，再按 n_chunks 分片并发下载（每片自带断点续传 + 重试）
- 汇总后校验: 字节数 == 总长, %PDF- 头, %%EOF 尾
- 仅用于本机慢链下的补救；不改 pdf_dl 工具本身
"""
import os, sys, time, urllib.request, concurrent.futures as cf

UA = "Mozilla/5.0 (research-agent; contact foamliu@yeah.net)"

def probe(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Range": "bytes=0-0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        cr = r.headers.get("Content-Range", "")
        return int(r.headers.get("Content-Length", 0)), cr

def get_total(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Range": "bytes=0-0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        cr = r.headers.get("Content-Range", "")
        total = int(cr.split("/")[-1]) if "/" in cr else int(r.headers.get("Content-Length", 0))
    return total

def fetch_chunk(url, idx, start, end, path):
    want = end - start + 1
    for attempt in range(1, 41):
        have = os.path.getsize(path) if os.path.exists(path) else 0
        if have >= want:
            return idx, want, True
        req = urllib.request.Request(url, headers={"User-Agent": UA,
                                                   "Range": "bytes=%d-%d" % (start + have, end)})
        try:
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=120) as r, open(path, "ab") as f:
                while True:
                    b = r.read(65536)
                    if not b:
                        break
                    f.write(b)
            print("  chunk %02d attempt=%d %.0fs have=%d/%d" % (idx, attempt, time.time() - t0,
                  os.path.getsize(path), want), flush=True)
        except Exception as e:
            print("  chunk %02d attempt=%d ERR %s" % (idx, attempt, repr(e)[:160]), flush=True)
            time.sleep(3)
    return idx, want, os.path.getsize(path) == want

def main():
    arxiv_id, url, out = sys.argv[1], sys.argv[2], sys.argv[3]
    n = int(sys.argv[4]) if len(sys.argv) > 4 else 12
    total = get_total(url)
    print("== %s == total=%d n_chunks=%d" % (arxiv_id, total, n), flush=True)
    step = (total + n - 1) // n
    parts = []
    for i in range(n):
        s = i * step
        e = min(total - 1, s + step - 1)
        p = "/tmp/p2_%s_%02d" % (arxiv_id, i)
        if os.path.exists(p) and os.path.getsize(p) > (e - s + 1):
            os.remove(p)
        parts.append((i, s, e, p))
    ok = True
    with cf.ThreadPoolExecutor(max_workers=n) as ex:
        futs = [ex.submit(fetch_chunk, url, i, s, e, p) for i, s, e, p in parts]
        for f in cf.as_completed(futs):
            _, want, good = f.result()
            ok = ok and good
    if not ok:
        print("FAIL: some chunks incomplete", flush=True)
        return 1
    with open(out, "wb") as fo:
        for i, s, e, p in parts:
            with open(p, "rb") as fi:
                while True:
                    b = fi.read(1 << 20)
                    if not b:
                        break
                    fo.write(b)
    size = os.path.getsize(out)
    head = open(out, "rb").read(5) == b"%PDF-"
    with open(out, "rb") as f:
        f.seek(max(0, size - 2048))
        tail = f.read()
    eof = b"%%EOF" in tail
    print("bytes=%d/%d head=%s eof=%s => %s" % (size, total, head, eof,
          "OK" if (size == total and head and eof) else "FAIL"), flush=True)
    for _, _, _, p in parts:
        try:
            os.remove(p)
        except OSError:
            pass
    return 0 if (size == total and head and eof) else 1

if __name__ == "__main__":
    sys.exit(main())
