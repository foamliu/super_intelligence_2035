#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百二十六轮（PM 晚 2 轮）：公告批次「是否刷新」独立复核（3 条查询，间隔 ≥3.2s）。

与 r122 的 verify_r122.py 同口径，本轮**新增第 4 条**：
  ④ 广度 5 分类 `cat:cs.CL OR cat:cs.CV OR cat:cs.SE OR cat:cs.AI OR cat:cs.LG`
     （对齐 `--fetch` 的 sweep 查询，确认 totalResults 是否仍为 639590）

输出同时写 `raw/2026-11-01-pm-verify-r126.txt`（stdout tee），作为心跳/日报的可核验证据。
"""
import io
import socket
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

HOST = "export.arxiv.org"
BASE = Path(__file__).resolve().parent.parent  # research/
OUT = BASE / "raw" / "2026-11-01-pm-verify-r126.txt"

# r126：本轮 export.arxiv.org 系统 DNS 实测可用 ⇒ 不覆盖解析结果

NS = {"a": "http://www.w3.org/2005/Atom",
      "x": "http://arxiv.org/schemas/atom",
      "o": "http://a9.com/-/spec/opensearch/1.1/"}

BUF = io.StringIO()


def say(msg):
    print(msg, flush=True)
    BUF.write(msg + "\n")


def q(name, params):
    url = "https://%s/api/query?%s" % (HOST, urllib.parse.urlencode(params))
    req = urllib.request.Request(url, headers={
        "User-Agent": "research-watch/1.0 (mailto:foamliu@yeah.net)"})
    t0 = time.time()
    # r126：本机到 arXiv 的 TLS 握手偶发 `ConnectionResetError` ⇒ 每条查询最多 3 次尝试（诚实记录次数）
    last = None
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read()
                st = r.status
                ct = r.headers.get("Content-Type")
            say("    attempts=%d" % attempt)
            break
        except Exception as exc:  # noqa: BLE001
            last = exc
            say("    attempt %d failed: %r" % (attempt, exc))
            time.sleep(3.2)
    else:
        raise last
    root = ET.fromstring(raw)
    tot = root.find("o:totalResults", NS)
    ents = root.findall("a:entry", NS)
    say("--- %s\n    url=%s\n    status=%s ct=%s total=%s n_entries=%d %.2fs" % (
        name, url, st, ct, tot.text if tot is not None else None, len(ents), time.time() - t0))
    for e in ents[:5]:
        say("    %s %s %s %s %s" % (
            e.find("a:id", NS).text.split("/abs/")[-1],
            e.find("a:published", NS).text,
            e.find("a:updated", NS).text,
            e.find("x:primary_category", NS).attrib["term"],
            " ".join(e.find("a:title", NS).text.split())[:70]))
    return raw


def main():
    q("① lastUpdatedDate cs.CL", {
        "search_query": "cat:cs.CL", "start": 0, "max_results": 5,
        "sortBy": "lastUpdatedDate", "sortOrder": "descending"})
    time.sleep(3.2)
    q("② submittedDate 20261030-20261101 (cs.CL)", {
        "search_query": "cat:cs.CL AND submittedDate:[202610300000 TO 202611012359]",
        "start": 0, "max_results": 5,
        "sortBy": "submittedDate", "sortOrder": "descending"})
    time.sleep(3.2)
    q("③ submittedDate 20261030-20261101 (全库，不加分类)", {
        "search_query": "submittedDate:[202610300000 TO 202611012359]",
        "start": 0, "max_results": 5,
        "sortBy": "submittedDate", "sortOrder": "descending"})
    time.sleep(3.2)
    q("④ 广度 sweep 5 分类", {
        "search_query": "cat:cs.CL OR cat:cs.CV OR cat:cs.SE OR cat:cs.AI OR cat:cs.LG",
        "start": 0, "max_results": 3,
        "sortBy": "submittedDate", "sortOrder": "descending"})
    OUT.write_text(BUF.getvalue(), encoding="utf-8")
    print("\nSAVED=%s" % OUT)


if __name__ == "__main__":
    main()
