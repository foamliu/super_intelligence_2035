#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百一十轮（本地 2026-10-24 18:00 PM「晚 2」轮）：下载 2 篇「科普」PDF 并严格校验。

校验链：HTTP content-type=application/pdf + 本地字节 == 服务端 content-length
        + `%PDF-` 头 + `%%EOF` 尾 + `pdfinfo` 页数 + `pdftotext` 字符数。
截断即用 HTTP Range 续传；最终仍不完整则删除并如实记 FAIL（不把截断文件当成功）。
"""
import subprocess
import sys
from pathlib import Path

OUT = Path("/home/liuyang/super_intelligence_2035/doc/personal-watch/run/research/pdf/2026-10-24")
IDS = ["2610.31579", "2610.30740"]
UA = "Mozilla/5.0 (research-agent; contact foamliu@yeah.net)"


def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def head_len(url):
    out = run(f"curl -sSI --max-time 60 -A '{UA}' '{url}'")
    length, ctype = None, ""
    for ln in out.stdout.splitlines():
        low = ln.lower()
        if low.startswith("content-length:"):
            length = int(ln.split(":", 1)[1].strip())
        if low.startswith("content-type:"):
            ctype = ln.split(":", 1)[1].strip()
    return length, ctype


def download(url, dst, total):
    for attempt in range(1, 6):
        have = dst.stat().st_size if dst.exists() else 0
        if total and have >= total:
            return have
        cmd = f"curl -sSL --max-time 600 -A '{UA}' -o '{dst}' '{url}'"
        if have > 0 and total and have < total:
            cmd = (f"curl -sSL --max-time 600 -A '{UA}' "
                   f"-C {have} -o '{dst}' '{url}'")
        run(cmd)
        have = dst.stat().st_size if dst.exists() else 0
        print(f"  attempt={attempt} bytes={have}/{total}", flush=True)
        if total and have == total:
            return have
    return dst.stat().st_size if dst.exists() else 0


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    for aid in IDS:
        url = f"https://arxiv.org/pdf/{aid}"
        dst = OUT / f"{aid}.pdf"
        if dst.exists():
            dst.unlink()
        total, ctype = head_len(url)
        print(f"== {aid} == content-type={ctype!r} content-length={total}", flush=True)
        if ctype != "application/pdf" or not total:
            print(f"FAIL {aid}: bad content-type/length", flush=True)
            results.append((aid, 0, 0, 0, "FAIL ctype"))
            continue
        size = download(url, dst, total)
        raw = dst.read_bytes() if dst.exists() else b""
        ok_head = raw[:5] == b"%PDF-"
        ok_tail = b"%%EOF" in raw[-2048:]
        pages = chars = 0
        if ok_head and ok_tail:
            pi = run(f"pdfinfo '{dst}'")
            for ln in pi.stdout.splitlines():
                if ln.startswith("Pages:"):
                    pages = int(ln.split(":", 1)[1].strip())
            pt = run(f"pdftotext '{dst}' -")
            chars = len(pt.stdout.strip())
        ok = ok_head and ok_tail and size == total and pages > 0 and chars > 2000
        print(f"  bytes={size}/{total} head={ok_head} eof={ok_tail} pages={pages} chars={chars} => {'OK' if ok else 'FAIL'}", flush=True)
        if not ok:
            dst.unlink(missing_ok=True)
        results.append((aid, size, pages, chars, "OK" if ok else "FAIL"))

    print("\n== SUMMARY ==")
    for r in results:
        print("%s bytes=%d pages=%d chars=%d %s" % r)
    return 0 if all(r[4] == "OK" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
