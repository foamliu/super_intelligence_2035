#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百三十四轮（本地 2026-11-05 18:00 PM「晚报 2」轮）：新批次候选池。

背景：`arxiv_fetch.py --fetch` 的 `cat:A OR cat:B ...` 合并查询存在**索引滞后**；
r133 起改用**单分类**各取最新 100 条，合并去重后只留 `published >= MIN_PUBLISHED`。
本轮新批已刷新（最晚 `2026-11-04T18:58:23Z`，`2611.06914`）⇒ MIN_PUBLISHED = 2026-11-04。

限速：每查询间隔 ≥3.2s（arXiv 官方要求 ≥3s）。
产出：`research/raw/2026-11-06-am-candidates-r135.json`
"""
import json
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

HOST = "export.arxiv.org"
BASE = Path(__file__).resolve().parent.parent  # research/
OUT = BASE / "raw" / "2026-11-06-am-candidates-r135.json"

NS = {"a": "http://www.w3.org/2005/Atom",
      "x": "http://arxiv.org/schemas/atom"}

CATS = ["cs.CL", "cs.CV", "cs.LG", "cs.AI", "cs.SE"]
MIN_PUBLISHED = "2026-11-04"


def query(cat):
    url = "https://%s/api/query?%s" % (HOST, urllib.parse.urlencode({
        "search_query": "cat:%s" % cat,
        "start": 0, "max_results": 100,
        "sortBy": "submittedDate", "sortOrder": "descending",
    }))
    req = urllib.request.Request(url, headers={
        "User-Agent": "research-watch/1.0 (mailto:foamliu@yeah.net)"})
    t0 = time.time()
    last = None
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read()
                status = r.status
                ctype = r.headers.get("Content-Type")
            break
        except Exception as exc:  # noqa: BLE001
            last = exc
            print("  attempt %d failed: %r" % (attempt, exc), flush=True)
            time.sleep(3.2)
    else:
        raise last
    root = ET.fromstring(raw)
    tr = root.find("{http://a9.com/-/spec/opensearch/1.1/}totalResults")
    rec = {"category": cat, "url": url, "status": status, "content_type": ctype,
           "total_results": int(tr.text) if tr is not None else None,
           "n_entries": len(root.findall("a:entry", NS)),
           "elapsed_s": round(time.time() - t0, 2), "items": []}
    for e in root.findall("a:entry", NS):
        rec["items"].append({
            "arxiv_id": e.find("a:id", NS).text.split("/abs/")[-1].split("v")[0],
            "title": " ".join(e.find("a:title", NS).text.split()),
            "summary": " ".join(e.find("a:summary", NS).text.split()),
            "authors": [a.find("a:name", NS).text for a in e.findall("a:author", NS)],
            "published": e.find("a:published", NS).text,
            "updated": e.find("a:updated", NS).text,
            "category": e.find("x:primary_category", NS).attrib["term"],
        })
    print("  %-6s status=%s ct=%s total=%s n=%d %.2fs" % (
        cat, status, ctype, rec["total_results"], rec["n_entries"], rec["elapsed_s"]), flush=True)
    return rec


def main():
    recs = []
    for i, cat in enumerate(CATS):
        if i:
            time.sleep(3.2)
        recs.append(query(cat))

    merged = {}
    for rec in recs:
        for it in rec["items"]:
            if it["published"] < MIN_PUBLISHED:
                continue
            merged.setdefault(it["arxiv_id"], it)

    # 与 SEEN 去重（主键 arXiv ID）
    seen = set()
    for ln in (BASE / "SEEN.md").read_text(encoding="utf-8").splitlines():
        if ln.startswith("|"):
            parts = [p.strip() for p in ln.strip("|").split("|")]
            if len(parts) >= 2 and parts[1].count(".") == 1:
                seen.add(parts[1])
    fresh = {k: v for k, v in merged.items() if k not in seen}

    payload = {"generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
               "host": HOST, "min_published": MIN_PUBLISHED,
               "queries": [{k: v for k, v in r.items() if k != "items"} for r in recs],
               "n_merged": len(merged), "n_seen": len(merged) - len(fresh),
               "n_fresh": len(fresh),
               "fresh": sorted(fresh.values(), key=lambda x: x["published"], reverse=True)}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print("MERGED=%d SEEN=%d FRESH=%d" % (len(merged), len(merged) - len(fresh), len(fresh)))
    print("SAVED=%s" % OUT)


if __name__ == "__main__":
    main()
