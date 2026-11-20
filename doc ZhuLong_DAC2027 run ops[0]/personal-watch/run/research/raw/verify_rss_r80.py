#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r80 一次性辅助脚本：对 RSS 发现的 2610.* 候选池做 arXiv API 批量核验
（校验 HTTP 200 + Content-Type XML + published），产出 published 等权威字段。
限速 >=3s。**不是长期工具**，仅本轮落盘用。
"""
import json, re, time, urllib.request
import xml.etree.ElementTree as ET

NS = "{http://www.w3.org/2005/Atom}"
AX = "{http://arxiv.org/schemas/atom}"
EP = "https://export.arxiv.org/api/query"

ids = json.load(open("research/raw/2026-10-08-rss-2610-ids.txt"))
out, fail = [], []
for i in range(0, len(ids), 40):
    chunk = ids[i:i + 40]
    url = EP + "?id_list=" + ",".join(chunk) + "&max_results=40"
    req = urllib.request.Request(url, headers={"User-Agent": "PersonalWatch/1.0 (research line)"})
    try:
        r = urllib.request.urlopen(req, timeout=40)
        ct = r.headers.get("Content-Type", "")
        raw = r.read()
        if r.status != 200 or "xml" not in ct.lower():
            fail.append({"chunk": i, "status": r.status, "ct": ct})
            continue
        root = ET.fromstring(raw)
        for e in root.findall(NS + "entry"):
            aid = e.findtext(NS + "id", "").rsplit("/", 1)[-1]
            pc = e.find(AX + "primary_category")
            out.append({
                "id": aid,
                "title": re.sub(r"\s+", " ", e.findtext(NS + "title", "")).strip(),
                "published": e.findtext(NS + "published", ""),
                "updated": e.findtext(NS + "updated", ""),
                "primary": pc.get("term") if pc is not None else "",
            })
    except Exception as ex:
        fail.append({"chunk": i, "error": str(ex)})
    time.sleep(3.0)

json.dump({"n_ids": len(ids), "n_entries": len(out), "fails": fail, "entries": out},
          open("research/raw/2026-10-08-rss-verify-r80.json", "w"),
          ensure_ascii=False, indent=1)
print("done", len(out), "entries, fails", len(fail))
