#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百三十四轮（本地 2026-11-05 18:00 PM「晚报 2」轮）：公告批次「是否刷新」独立复核（4 条查询，间隔 ≥3.2s）。

与 r133 同口径，`submittedDate` 区间右移一天（`20261102 TO 202611062359`）。
预期：美东 11-04 20:00 ET 新批 = 本地 11-05 09:00 已发布 ⇒ 本轮应看到 `2026-11-04` 批。
输出同时写 `raw/2026-11-05-pm-verify-r134.txt`，作为心跳/日报的可核验证据。
"""
import io
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

HOST = "export.arxiv.org"
BASE = Path(__file__).resolve().parent.parent  # research/
OUT = BASE / "raw" / "2026-11-05-pm-verify-r134.txt"

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


QUERIES = [
    ("① lastUpdatedDate cs.CL", {
        "search_query": "cat:cs.CL", "start": 0, "max_results": 5,
        "sortBy": "lastUpdatedDate", "sortOrder": "descending"}, 0),
    ("② submittedDate 20261102-20261106 (cs.CL)", {
        "search_query": "cat:cs.CL AND submittedDate:[202611020000 TO 202611062359]",
        "start": 0, "max_results": 8,
        "sortBy": "submittedDate", "sortOrder": "descending"}, 6),
    ("③ submittedDate 20261102-20261106 (全库，不加分类)", {
        "search_query": "submittedDate:[202611020000 TO 202611062359]",
        "start": 0, "max_results": 8,
        "sortBy": "submittedDate", "sortOrder": "descending"}, 6),
    ("④ 广度 sweep 5 分类", {
        "search_query": "cat:cs.CL OR cat:cs.CV OR cat:cs.SE OR cat:cs.AI OR cat:cs.LG",
        "start": 0, "max_results": 3,
        "sortBy": "submittedDate", "sortOrder": "descending"}, 20),
]


def main():
    # 单条失败不中断（429 限速时如实登记），保证证据文件总能落盘。
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
