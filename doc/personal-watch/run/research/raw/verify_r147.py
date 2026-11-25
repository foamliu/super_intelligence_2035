#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百四十七轮（本地 2026-11-11 12:00 午间轮）：公告批次「是否刷新」独立复核（轻量版）。

为什么是轻量版：r144 的 ④ 广度 sweep（5 分类 OR）在 12:00 实测 60s 读超时
（`TimeoutError('The read operation timed out')`），本轮改为**单分类小查询**做同样判读，
避免把「接口慢」误记成「无新增」。广度合计由 `candidates_r147.py` 的 5 次单分类
`totalResults` 提供（同轮实测）。

输出写 `raw/2026-11-11-midday-verify-r147.txt`，作为心跳/日报的可核验证据。
"""
import io
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

HOST = "export.arxiv.org"
BASE = Path(__file__).resolve().parent.parent  # research/
OUT = BASE / "raw" / "2026-11-11-midday-verify-r147.txt"

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
    last = None
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
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


QUERIES = [
    ("① cs.CL 最新提交（submittedDate desc）", {
        "search_query": "cat:cs.CL", "start": 0, "max_results": 5,
        "sortBy": "submittedDate", "sortOrder": "descending"}, 0),
    ("② submittedDate 20261110-20261114（cs.CL）", {
        "search_query": "cat:cs.CL AND submittedDate:[202611100000 TO 202611142359]",
        "start": 0, "max_results": 8,
        "sortBy": "submittedDate", "sortOrder": "descending"}, 6),
    ("③ submittedDate 20261111-20261115（cs.CL，明日区间对照）", {
        "search_query": "cat:cs.CL AND submittedDate:[202611110000 TO 202611152359]",
        "start": 0, "max_results": 8,
        "sortBy": "submittedDate", "sortOrder": "descending"}, 6),
    ("④ submittedDate 20261110-20261114（cs.LG，跨分类对照）", {
        "search_query": "cat:cs.LG AND submittedDate:[202611100000 TO 202611142359]",
        "start": 0, "max_results": 8,
        "sortBy": "submittedDate", "sortOrder": "descending"}, 6),
]


def main():
    for name, params, gap in QUERIES:
        if gap:
            time.sleep(gap)
        try:
            q(name, params)
        except Exception as exc:  # noqa: BLE001
            say("--- %s\n    FAILED: %r" % (name, exc))
    OUT.write_text(BUF.getvalue(), encoding="utf-8")
    print("\nSAVED=%s" % OUT)


if __name__ == "__main__":
    main()
