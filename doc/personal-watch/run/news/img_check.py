#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""img_check.py — 校验候选配图 URL 可用性（**只在内存里收 body，不落盘**）。

判据（配图令 ①/② 的下游口径）：
  · HTTP 200
  · Content-Type 以 `image/` 开头
  · body 字节数 > 5120（>5KB；发布前下载时再用本地文件大小复检一次）
  · URL 带 `watermark` / `x-bce-process=…watermark` ⇒ 标 `WARN_WATERMARK`（下游禁用）

用法：
  python3 news/img_check.py <url> [<url> ...]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fetch import get  # noqa: E402

REF = "https://www.ithome.com/"


def check(url, referer=REF):
    r = get(url, referer=referer)
    body = r["body"] or b""
    ctype = r["ctype"] or ""
    n = len(body)
    ok = bool(r["status"] == 200 and ctype.startswith("image/") and n > 5120)
    warn = "watermark" in url.lower()
    return {"url": url, "status": r["status"], "ctype": ctype.split(";")[0],
            "bytes": n, "ok": ok, "warn_watermark": warn, "err": r["err"]}


def main():
    bad = 0
    urls = sys.argv[1:]
    for u in urls:
        d = check(u)
        flag = "OK  " if (d["ok"] and not d["warn_watermark"]) else ("WARN" if d["ok"] else "BAD ")
        if not d["ok"]:
            bad += 1
        print("%s %s %-12s %8d %s" % (flag, d["status"], d["ctype"], d["bytes"], u))
    print("BAD %d / %d" % (bad, len(urls)))


if __name__ == "__main__":
    main()
