#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百四十七轮补跑：只跑 2 条查询，把「批次刷新」证据落盘。

背景：12:0x 首跑时 ②/③/④ 与并发取数撞限速 ⇒ `HTTP 429`，进程被手工终止，
`raw/2026-11-11-midday-verify-r147.txt` 未写出。本脚本只做 ①（cs.CL 最新）
+ ②（cs.CL 的 2026-11-10~14 区间），间隔 12s，把真实输出写回同一文件。
"""
import io
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

HOST = "export.arxiv.org"
BASE = Path(__file__).resolve().parent.parent
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
            time.sleep(10)
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


QUERIES = [
    ("① cs.CL 最新提交（submittedDate desc）", {
        "search_query": "cat:cs.CL", "start": 0, "max_results": 5,
        "sortBy": "submittedDate", "sortOrder": "descending"}, 0),
    ("② submittedDate 20261110-20261114（cs.CL）", {
        "search_query": "cat:cs.CL AND submittedDate:[202611100000 TO 202611142359]",
        "start": 0, "max_results": 8,
        "sortBy": "submittedDate", "sortOrder": "descending"}, 12),
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
