#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百二十七轮（本地 2026-11-02 06:00 AM「早 3」轮）R1′ 分源探针。

与 r126 同口径：`export.arxiv.org` 走系统 DNS（实测 199.232.163.42 可用），不覆盖解析。

产出：research/raw/2026-11-02-am-probe-r127.json
"""
import json
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

HOST = "export.arxiv.org"
BASE = Path(__file__).resolve().parent.parent  # research/
OUT = BASE / "raw" / "2026-11-02-am-probe-r127.json"

NS = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}


def probe_arxiv():
    url = ("https://%s/api/query?search_query=cat:cs.CL&start=0&max_results=3"
           "&sortBy=submittedDate&sortOrder=descending" % HOST)
    rec = {"endpoint": "https://export.arxiv.org/api/query", "url": url}
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "PersonalWatch/1.0 (research line; contact: local)"})
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read()
            rec["status"] = resp.status
            rec["content_type"] = resp.headers.get("Content-Type")
        rec["elapsed_s"] = round(time.time() - t0, 2)
        root = ET.fromstring(raw)
        tr = root.find("{http://a9.com/-/spec/opensearch/1.1/}totalResults")
        rec["total_results"] = int(tr.text) if tr is not None else None
        entries = root.findall("a:entry", NS)
        rec["n_entries"] = len(entries)
        rec["sample"] = [{
            "arxiv_id": e.find("a:id", NS).text.split("/abs/")[-1],
            "published": e.find("a:published", NS).text,
            "category": e.find("x:primary_category", NS).attrib["term"],
            "title": " ".join(e.find("a:title", NS).text.split()),
        } for e in entries]
        rec["ok"] = bool(rec["content_type"] and "xml" in rec["content_type"]
                         and rec["n_entries"] > 0)
        rec["error"] = None
    except Exception as exc:  # noqa: BLE001
        rec["ok"] = False
        rec["error"] = repr(exc)[:400]
    return rec


def probe_hf():
    rec = {"endpoint": "https://huggingface.co/api/daily_papers"}
    try:
        req = urllib.request.Request(rec["endpoint"], headers={"User-Agent": "PersonalWatch/1.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        rec["ok"] = True
        rec["n_ids"] = len(data)
        rec["error"] = None
    except Exception as exc:  # noqa: BLE001
        rec["ok"] = False
        rec["n_ids"] = 0
        rec["error"] = repr(exc)[:400]
    return rec


def probe_rss():
    out = {}
    for cat in ("cs.CL", "cs.CV", "cs.LG"):
        url = "https://rss.arxiv.org/rss/%s" % cat
        rec = {"url": url}
        print("[rss] probing %s" % cat, flush=True)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "PersonalWatch/1.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                raw = resp.read()
                rec["status"] = resp.status
                rec["content_type"] = resp.headers.get("Content-Type")
            root = ET.fromstring(raw)
            rec["items"] = len(root.findall("./channel/item"))
            rec["note"] = "" if rec["items"] else "空 feed（周末/未公告），仅作发现"
        except Exception as exc:  # noqa: BLE001
            rec["status"] = None
            rec["items"] = 0
            rec["note"] = "FAIL " + repr(exc)[:200]
        out[cat] = rec
    return out


def main():
    print("[probe] arXiv API...", flush=True)
    arxiv = probe_arxiv()
    print("[probe] arXiv ok=%s total=%s latest=%s" % (
        arxiv.get("ok"), arxiv.get("total_results"),
        (arxiv.get("sample") or [{}])[0].get("published")), flush=True)
    print("[probe] HF daily_papers...", flush=True)
    hf = probe_hf()
    print("[probe] HF ok=%s err=%s" % (hf.get("ok"), hf.get("error")), flush=True)
    rss = probe_rss()
    rec = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "arxiv_api": arxiv,
        "hf_daily": hf,
        "arxiv_rss": rss,
    }
    OUT.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(rec, ensure_ascii=False, indent=2))
    print("SAVED=%s" % OUT)


if __name__ == "__main__":
    main()
