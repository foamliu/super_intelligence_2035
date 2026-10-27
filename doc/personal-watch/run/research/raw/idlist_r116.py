#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百一十六轮（PM「晚 2」收口轮）：`id_list` 权威复核（只用官方 Atom 元数据）。

用法（在 run/ 目录）：`python3 research/raw/idlist_r115.py <batch后缀> <id1> <id2> ...`
产出：`research/raw/2026-10-27-pm-idlist-r116<后缀>.xml` + `.headers`
      （DNS 边缘兜底同 `run_arxiv_r109.py`：只覆盖 export.arxiv.org，TLS/SNI/Host 不变）
"""
import socket
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

GOOD_IP = "151.101.67.42"
HOST = "export.arxiv.org"
BASE = Path(__file__).resolve().parent.parent  # research/

_orig = socket.getaddrinfo


def _gai(host, port, *args, **kwargs):
    if host == HOST:
        return _orig(GOOD_IP, port, *args, **kwargs)
    return _orig(host, port, *args, **kwargs)


socket.getaddrinfo = _gai


def main():
    suffix = sys.argv[1]
    ids = sys.argv[2:]
    assert ids, "need at least one arXiv id"
    qs = urllib.parse.urlencode({
        "id_list": ",".join(ids),
        "max_results": str(len(ids)),
    })
    url = "https://%s/api/query?%s" % (HOST, qs)
    req = urllib.request.Request(url, headers={
        "User-Agent": "research-watch/1.0 (mailto:foamliu@yeah.net)",
    })
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read()
        ctype = resp.headers.get("Content-Type")
        status = resp.status
    dt = time.time() - t0
    out_xml = BASE / "raw" / ("2026-10-27-pm-idlist-r116%s.xml" % suffix)
    out_hdr = BASE / "raw" / ("2026-10-27-pm-idlist-r116%s.headers" % suffix)
    out_xml.write_bytes(raw)
    out_hdr.write_text(
        "url: %s\nstatus: %s\ncontent-type: %s\nbytes: %d\nelapsed: %.2fs\n"
        % (url, status, ctype, len(raw), dt),
        encoding="utf-8",
    )
    print("STATUS=%s CTYPE=%s BYTES=%d ELAPSED=%.2fs" % (status, ctype, len(raw), dt))
    print("SAVED=%s" % out_xml)


if __name__ == "__main__":
    main()
