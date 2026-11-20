#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百二十二轮（本地 2026-10-30 18:00 PM「晚 2」轮）：带 DNS 边缘兜底跑 `arxiv_fetch.py --fetch --seen`。

背景：本机 `export.arxiv.org` 的 DNS 解析偶发卡死（r121 直跑 4 分钟无输出）
⇒ 沿用 `run_arxiv_r109.py` / `probe_r12x.py` 口径：**只覆盖 `export.arxiv.org` 的解析结果到实测可用 IP**，
TLS/SNI/Host 与证书校验完全不变。

产出：`research/raw/2026-10-30-pm-fetch-r122-seen.json`
"""
import socket
import sys
from pathlib import Path

GOOD_IP = "151.101.67.42"
HOST = "export.arxiv.org"

_orig = socket.getaddrinfo


def _gai(host, port, *args, **kwargs):
    if host == HOST:
        return _orig(GOOD_IP, port, *args, **kwargs)
    return _orig(host, port, *args, **kwargs)


socket.getaddrinfo = _gai

BASE = Path(__file__).resolve().parent.parent  # research/
sys.path.insert(0, str(BASE))

import arxiv_fetch  # noqa: E402

OUT = BASE / "raw" / "2026-10-30-pm-fetch-r122-seen.json"

if __name__ == "__main__":
    raise SystemExit(arxiv_fetch.main([
        "--fetch",
        "--seen", str(BASE / "SEEN.md"),
        "--json", "--out", str(OUT),
    ]))
