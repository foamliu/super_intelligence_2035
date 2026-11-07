#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百三十八轮（本地 2026-11-07 18:00 PM「晚报 2 科普 + 论文观察日报」轮）：公告批次「是否刷新」独立复核。

与 r137（AM）同口径；`submittedDate` 区间顺延（`202611050000 TO 202611092359`）。
预期：美东 11-06 20:00 ET 新批 = 本地 11-07 09:00，早于 PM 约 9h ⇒ 本轮预计见 `2026-11-06`。

输出写 `raw/2026-11-07-pm-verify-r138.txt`，作为心跳/日报的可核验证据。
"""
import io
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

HOST = "export.arxiv.org"
BASE = Path(__file__).resolve().parent.parent  # research/
OUT = BASE / "raw" / "2026-11-07-pm-verify-r138.txt"

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
    ("② submittedDate 20261105-20261109 (cs.CL)", {
        "search_query": "cat:cs.CL AND submittedDate:[202611050000 TO 202611092359]",
        "start": 0, "max_results": 8,
        "sortBy": "submittedDate", "sortOrder": "descending"}, 6),
    ("③ submittedDate 20261105-20261109 (全库，不加分类)", {
        "search_query": "submittedDate:[202611050000 TO 202611092359]",
        "start": 0, "max_results": 8,
        "sortBy": "submittedDate", "sortOrder": "descending"}, 6),
    ("④ 广度 sweep 5 分类", {
        "search_query": "cat:cs.CL OR cat:cs.CV OR cat:cs.SE OR cat:cs.AI OR cat:cs.LG",
        "start": 0, "max_results": 3,
        "sortBy": "submittedDate", "sortOrder": "descending"}, 20),
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
