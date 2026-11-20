#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fetch.py — news 线采集用最小 HTTP 抓取器（零依赖，只用 urllib）。

为什么存在：
  `~/.local/lib/python3*/site-packages/urllib3/_collections.py` 这个第三方包在本机**行为异常**
  （实测只保留部分元素，导致 requests/urllib3 返回**被截断的正文**，且不报错）。
  故采集一律走本文件（只 import 标准库），🚫 不用 requests / urllib3。

用法（库）：
  from fetch import get, get_text
  r = get(url, referer=None)          # -> {'status','ctype','body'(bytes),'url','err'}
  t = get_text(url, referer=None)     # -> str（按 charset 解码；失败按 utf-8, gbk 兜底）

命令行：
  python3 fetch.py <url> [--out FILE] [--referer REF]
"""
import sys
import urllib.request

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36")


def get(url, referer=None, timeout=25):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/*,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.6",
        **({"Referer": referer} if referer else {}),
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return {"status": r.status, "ctype": r.headers.get("Content-Type", ""),
                    "body": r.read(), "url": r.geturl(), "err": None}
    except Exception as e:  # noqa: BLE001
        return {"status": None, "ctype": "", "body": b"", "url": url,
                "err": "%s: %s" % (type(e).__name__, e)}


def _decode(body, ctype):
    cs = "utf-8"
    i = ctype.lower().find("charset=")
    if i >= 0:
        cs = ctype[i + 8:].split(";")[0].strip().strip('"')
    for c in (cs, "utf-8", "gbk"):
        try:
            return body.decode(c, "replace")
        except LookupError:
            continue
    return body.decode("utf-8", "replace")


def get_text(url, referer=None, timeout=25):
    r = get(url, referer=referer, timeout=timeout)
    return _decode(r["body"], r["ctype"])


if __name__ == "__main__":
    u = sys.argv[1]
    out = None
    ref = None
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
    if "--referer" in sys.argv:
        ref = sys.argv[sys.argv.index("--referer") + 1]
    r = get(u, referer=ref)
    if out:
        with open(out, "wb") as f:
            f.write(r["body"])
        print("HTTP %s %s %d B -> %s" % (r["status"], r["ctype"], len(r["body"]), out))
    else:
        print("HTTP %s %s %d B err=%s" % (r["status"], r["ctype"], len(r["body"]), r["err"]))
