#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百四十七轮 · B 轨第三轮：候选经典论文元数据 + 被引数核验。

候选（PAPERS.md 候选池已实测元数据，本轮转正）：
  2104.09864 RoFormer · 2310.06770 SWE-bench · 2303.11366 Reflexion · 2201.11903 CoT

口径（与首轮/第二轮一致）：
  - 标题 / 首次提交 / comment（会议线索）取自 arXiv 官方 API `id_list`（单请求，实测 Content-Type）。
  - 被引数取自 OpenAlex `api.openalex.org/works/https://doi.org/10.48550/arxiv.<ID>`，逐条记查询日。
  - S2（semanticscholar）本轮仍不请求（首轮 429）⇒ 一律记「未查」，不估算、不跨源比较。
产出：`raw/2026-11-11-classic-r147.json`
"""
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
OUT = BASE / "raw" / "2026-11-11-classic-r147.json"
IDS = ["2104.09864", "2310.06770", "2303.11366", "2201.11903"]
UA = "research-watch/1.0 (mailto:foamliu@yeah.net)"
NS = {"a": "http://www.w3.org/2005/Atom",
      "x": "http://arxiv.org/schemas/atom"}


def get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        return raw, r.status, r.headers.get("Content-Type"), round(time.time() - t0, 2)


def arxiv_meta():
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"id_list": ",".join(IDS), "max_results": 10})
    raw, st, ct, el = get(url)
    root = ET.fromstring(raw)
    out = {}
    for e in root.findall("a:entry", NS):
        aid = e.find("a:id", NS).text.split("/abs/")[-1].split("v")[0]
        out[aid] = {
            "title": " ".join(e.find("a:title", NS).text.split()),
            "published": e.find("a:published", NS).text,
            "updated": e.find("a:updated", NS).text,
            "category": e.find("x:primary_category", NS).attrib["term"],
            "authors": [a.find("a:name", NS).text for a in e.findall("a:author", NS)],
            "comment": (e.find("x:comment", NS).text if e.find("x:comment", NS) is not None else None),
            "journal_ref": (e.find("x:journal_ref", NS).text if e.find("x:journal_ref", NS) is not None else None),
        }
    return {"url": url, "status": st, "content_type": ct, "elapsed_s": el,
            "n_entries": len(out), "items": out}


def openalex(aid):
    url = "https://api.openalex.org/works/https://doi.org/10.48550/arxiv.%s?mailto=foamliu@yeah.net" % aid
    try:
        raw, st, ct, el = get(url, timeout=40)
    except Exception as exc:  # noqa: BLE001
        return {"arxiv_id": aid, "url": url, "error": repr(exc)}
    w = json.loads(raw.decode("utf-8"))
    loc = w.get("primary_location") or {}
    src = loc.get("source") or {}
    return {"arxiv_id": aid, "url": url, "status": st,
            "cited_by_count": w.get("cited_by_count"),
            "publication_year": w.get("publication_year"),
            "source_name": src.get("display_name"),
            "biblio": w.get("biblio"),
            "landing_page_url": loc.get("landing_page_url"),
            "elapsed_s": el}


def main():
    print("[1/2] arXiv id_list ...", flush=True)
    ax = arxiv_meta()
    print("  status=%s ct=%s n=%d %.2fs" % (ax["status"], ax["content_type"], ax["n_entries"], ax["elapsed_s"]), flush=True)
    for aid, it in ax["items"].items():
        print("  %s %s | %s | comment=%r" % (aid, it["published"], it["title"][:60], it["comment"]), flush=True)
    print("[2/2] OpenAlex citations ...", flush=True)
    oa = []
    for i, aid in enumerate(IDS):
        if i:
            time.sleep(1.2)
        r = openalex(aid)
        oa.append(r)
        print("  %s cited_by=%s year=%s src=%r" % (aid, r.get("cited_by_count"), r.get("publication_year"), r.get("source_name")), flush=True)
    payload = {"generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
               "query_date": time.strftime("%Y-%m-%d"),
               "arxiv": ax, "openalex": oa,
               "note": "S2 本轮未请求（首轮 429）⇒ 被引数仅 OpenAlex 单源，禁止跨源比较"}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print("SAVED=%s" % OUT)


if __name__ == "__main__":
    main()
