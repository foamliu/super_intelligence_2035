#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pdf_dl_r92.py — 2026-10-15 日报 PDF **补跑下载器**（第九十二轮补跑）

背景（运维指令 2026-10-15）：上一轮因 `pkill -f 'arxiv.org/pdf'` 自匹配误杀 cline，
已下载的 PDF 被截断（xref 无效 / pdftotext 解析 0 字节）⇒ 本轮重下 + 严格校验。

特性（针对本机 arXiv 带宽极慢 ~17KB/s 的现实，避免再次截断）：
  1. **断点续传**：`Range: bytes=<have>-`（实测 export.arxiv.org 支持 206）；
  2. **长超时 + 多次重试**（单文件最多 8 次续传）；
  3. **严格校验**：`%PDF-` 头 + 尾部 `%%EOF` + 字节数下限 + `pdftotext` 可解析（>2000 字符）+ `pdfinfo` 页数；
  4. 校验失败 ⇒ 删除该文件（🚫 不把截断文件当成功记录）；
  5. 输出 size / sha256（元数据入 git，PDF 本体不入 git）。

用法：python3 research/raw/pdf_dl_r92.py            # 下载全部 5 篇
      python3 research/raw/pdf_dl_r92.py <arXiv_ID> # 只下某一篇
"""
import hashlib
import os
import subprocess
import sys
import time

import requests

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../run/research
OUT = os.path.join(BASE, "pdf", "2026-10-15")

# 2026-10-15 日报 5 篇（借鉴 3 + 科普 2）
IDS = ["2610.17637", "2610.17202", "2610.20193", "2610.19587", "2610.19863"]

UA = "Mozilla/5.0 (compatible; watch-research/1.0; +https://arxiv.org)"
MIN_BYTES = 50 * 1024
MAX_TRIES = 8
CHUNK = 64 * 1024


def log(msg):
    print("[%s] %s" % (time.strftime("%H:%M:%S"), msg), flush=True)


def fetch(aid):
    url = "https://export.arxiv.org/pdf/%s" % aid
    path = os.path.join(OUT, aid + ".pdf")
    for attempt in range(1, MAX_TRIES + 1):
        have = os.path.getsize(path) if os.path.exists(path) else 0
        headers = {"User-Agent": UA}
        if have > 0:
            headers["Range"] = "bytes=%d-" % have
        try:
            with requests.get(url, headers=headers, stream=True,
                              timeout=(30, 180), allow_redirects=True) as r:
                if r.status_code == 200 and have > 0:
                    log("  ! server ignored Range -> restart from 0 (attempt %d)" % attempt)
                    have = 0
                if r.status_code not in (200, 206):
                    log("  ! HTTP %s (attempt %d) url=%s hist=%s ctype=%s"
                        % (r.status_code, attempt, r.url,
                           [h.status_code for h in r.history], r.headers.get("content-type")))
                    time.sleep(3)
                    continue
                mode = "ab" if (have > 0 and r.status_code == 206) else "wb"
                got = have
                with open(path, mode) as f:
                    for chunk in r.iter_content(CHUNK):
                        if not chunk:
                            continue
                        f.write(chunk)
                        got += len(chunk)
                log("  attempt %d: %s -> %d bytes (mode=%s)" % (attempt, r.status_code, got, mode))
                # 完整（200 且非分块）或已到末尾 ⇒ 交给校验
        except Exception as e:  # noqa: BLE001
            log("  ! %s: %s (attempt %d)" % (type(e).__name__, e, attempt))
            time.sleep(5)
    return path


def verify(path):
    """返回 (ok, 说明, 字节)"""
    if not os.path.exists(path):
        return False, "missing", 0
    size = os.path.getsize(path)
    if size < MIN_BYTES:
        return False, "too small (%d B < %d)" % (size, MIN_BYTES), size
    with open(path, "rb") as f:
        head = f.read(8)
        f.seek(max(0, size - 2048))
        tail = f.read()
    if not head.startswith(b"%PDF-"):
        return False, "bad header %r" % head, size
    if b"%%EOF" not in tail:
        return False, "missing %%EOF trailer", size
    # pdfinfo：页数
    try:
        pi = subprocess.run(["pdfinfo", path], capture_output=True, timeout=120)
        info = pi.stdout.decode("utf-8", "replace")
        if "Pages:" not in info:
            return False, "pdfinfo broken: %s" % pi.stderr.decode("utf-8", "replace")[:160], size
        pages = [l for l in info.splitlines() if l.startswith("Pages:")][0].split(":", 1)[1].strip()
    except Exception as e:  # noqa: BLE001
        return False, "pdfinfo failed: %s" % e, size
    # pdftotext：正文可解析
    try:
        pt = subprocess.run(["pdftotext", path, "-"], capture_output=True, timeout=180)
        chars = len(pt.stdout.decode("utf-8", "replace"))
        if chars < 2000:
            return False, "pdftotext only %d chars" % chars, size
    except Exception as e:  # noqa: BLE001
        return False, "pdftotext failed: %s" % e, size
    return True, "OK pages=%s text=%d chars" % (pages, chars), size


def main():
    os.makedirs(OUT, exist_ok=True)
    targets = sys.argv[1:] or IDS
    rows = []
    for aid in targets:
        path = os.path.join(OUT, aid + ".pdf")
        # 截断/坏文件先删（不续传坏文件）
        if os.path.exists(path):
            ok, _, _ = verify(path)
            if not ok:
                log("%s: 现存文件校验失败 ⇒ 删除重下" % aid)
                os.remove(path)
            else:
                log("%s: 现存文件已通过校验 ⇒ 跳过" % aid)
                rows.append((aid, True, "preexisting-OK", os.path.getsize(path), ""))
                continue
        log("%s: 开始下载 %s" % (aid, path))
        fetch(aid)
        ok, note, size = verify(path)
        sha = ""
        if ok:
            h = hashlib.sha256()
            with open(path, "rb") as f:
                for b in iter(lambda: f.read(1 << 20), b""):
                    h.update(b)
            sha = h.hexdigest()
        else:
            if os.path.exists(path):
                os.remove(path)
                note += " -> deleted"
            log("%s: ❌ 校验失败：%s" % (aid, note))
        log("%s: %s %s bytes sha256=%s" % (aid, "✅" if ok else "❌", size, sha or "-"))
        rows.append((aid, ok, note, size, sha))
    log("==== 汇总 ====")
    for aid, ok, note, size, sha in rows:
        log("%s  %-6s %10d B  %s  %s" % (aid, "OK" if ok else "FAIL", size, sha[:16], note))
    bad = [r for r in rows if not r[1]]
    log("成功 %d / %d" % (len(rows) - len(bad), len(rows)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
