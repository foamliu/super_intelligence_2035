#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百二十七轮（本地 2026-11-02 06:00 AM「早 3」轮）：跑 `arxiv_fetch.py --fetch --seen`。

`export.arxiv.org` 走系统 DNS（199.232.163.42 实测可用）⇒ 不做 DNS 覆盖。
产出：`research/raw/2026-11-02-am-fetch-r127-seen.json`
"""
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent.parent  # research/
sys.path.insert(0, str(BASE))

import arxiv_fetch  # noqa: E402

OUT = BASE / "raw" / "2026-11-02-am-fetch-r127-seen.json"

if __name__ == "__main__":
    raise SystemExit(arxiv_fetch.main([
        "--fetch",
        "--seen", str(BASE / "SEEN.md"),
        "--json", "--out", str(OUT),
    ]))
