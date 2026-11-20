#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百零九轮取数包装器（**不改工具代码**）。

成因（本轮实测）：`export.arxiv.org` 的 DNS 答案 `146.75.115.42`（Fastly 边缘）
在运行机不可达 —— `curl --max-time 12` 12s 超时（`http_code=000`）；
同域其余 Fastly 边缘（151.101.67.42 / .3.42 / .131.42 / .195.42）均 `HTTP 200` + `t<0.8s`。
=> 运行期只对 `export.arxiv.org` 覆盖 `socket.getaddrinfo` 到可用边缘，
   TLS 仍按 `export.arxiv.org` 校验（SNI/证书不变），arXiv 侧看到的主机名不变。

用法：`python3 research/raw/run_arxiv_r109.py --fetch --seen research/SEEN.md --json --out ...`
"""
import runpy
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

SCRIPT = Path(__file__).resolve().parent.parent / "arxiv_fetch.py"
sys.argv = [str(SCRIPT)] + sys.argv[1:]
runpy.run_path(str(SCRIPT), run_name="__main__")
