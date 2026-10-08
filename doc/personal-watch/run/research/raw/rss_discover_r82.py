#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r82 一次性辅助脚本（P0 早报轮 · 复用 R80 路径）：
RSS（工作日补充源）发现当前公告批次中「不在 SEEN 台账」的 arXiv ID
  -> arXiv API `id_list` 批量复核（HTTP 200 + application/atom+xml + 有 published）
  -> 按 §0.1（published <= 72h）筛选候选。
限速 >=3s。**不是长期工具**，仅本轮落盘用。
"""
import json, re, time, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
NS = "{http://www.w3.org/2005/Atom}"
AX = "{http://arxiv.org/schemas/atom}"
EP = "https://export.arxiv.org/api/query"
RSS = "https://rss.arxiv.org/rss/"
CATS = ["cs.CL", "cs.CV", "cs.LG", "cs.AI", "cs.MM", "cs.SE"]

def http_get(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": "PersonalWatch/1.0 (research line)"})
    r = urllib.request.urlopen(req, timeout=timeout)
    return r.status, r.headers.get("Content-Type", ""), r.read()

# 1) SEEN 已有 ID
seen_txt = SEEN.read_text(encoding="utf-8")
seen_ids = set(re.findall(r"\b(\d{4}\.\d{4,5})\b", seen_txt))
print("SEEN ids:", len(seen_ids))

# 2) RSS 发现
rss_ids = {}
for c in CATS:
    try:
        st, ct, body = http_get(RSS + c)
        ids = re.findall(r"arxiv\.org/abs/(\d{4}\.\d{4,5})", body.decode("utf-8", "replace"))
        items = len(re.findall(r"<item>", body.decode("utf-8", "replace")))
        for i in ids:
            rss_ids.setdefault(i, c)
        print("RSS", c, "status", st, "ct", ct, "items", items, "ids", len(ids))
    except Exception as ex:
        print("RSS FAIL", c, ex)
    time.sleep(3.0)

print("RSS total unique ids:", len(rss_ids))
new_ids = sorted(i for i in rss_ids if i not in seen_ids)
cand = [i for i in new_ids if i.startswith("2610.") or i.startswith("2609.")]
print("uncovered (not in SEEN):", len(new_ids), "of which 2610/2609:", len(cand))

# 3) arXiv API id_list 批量复核
entries, fails = [], []
for k in range(0, len(cand), 40):
    chunk = cand[k:k + 40]
    url = EP + "?id_list=" + ",".join(chunk) + "&max_results=40"
    try:
        st, ct, raw = http_get(url)
        if st != 200 or "xml" not in ct.lower():
            fails.append({"chunk": k, "status": st, "ct": ct})
        else:
            root = ET.fromstring(raw)
            for e in root.findall(NS + "entry"):
                aid = e.findtext(NS + "id", "").rsplit("/", 1)[-1]
                pc = e.find(AX + "primary_category")
                entries.append({
                    "id": aid,
                    "title": re.sub(r"\s+", " ", e.findtext(NS + "title", "")).strip(),
                    "published": e.findtext(NS + "published", ""),
                    "updated": e.findtext(NS + "updated", ""),
                    "primary": pc.get("term") if pc is not None else "",
                })
    except Exception as ex:
        fails.append({"chunk": k, "error": str(ex)})
    time.sleep(3.0)

print("id_list verified:", len(entries), "fails", len(fails))

# 4) 72h 窗
now = datetime.now(timezone.utc)
def within(pub):
    try:
        dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
    except Exception:
        return None
    return (now - dt).total_seconds() / 3600.0

in_win = []
for e in entries:
    h = within(e["published"])
    if h is not None and h <= 72.0:
        e["age_h"] = round(h, 1)
        in_win.append(e)

json.dump({"generated": now.isoformat(), "n_seen_ids": len(seen_ids),
           "n_rss_ids": len(rss_ids), "n_uncovered": len(new_ids),
           "n_checked": len(cand), "n_verified": len(entries), "fails": fails,
           "n_in_window": len(in_win), "in_window": in_win, "verified": entries},
          open(str(BASE / "raw" / "2026-10-09-rss-r82.json"), "w"),
          ensure_ascii=False, indent=1)
print("in_window(<=72h):", len(in_win))
for e in in_win:
    print("  ", e["id"], e["published"], e["primary"], e["title"][:90])
