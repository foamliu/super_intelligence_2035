#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ith_dedup.py — IT之家 RSS 去重（只认标准库，🚫 不用 requests / re 路径式正则）。

实测踩坑（2026-11-15 第 281 轮）：
  · 本机 `re` 对「含 `/` 的路径式 pattern」匹配异常：`re.search('/1/027/', 'x/1/027/302.htm')` → None
    （同 pattern 去掉前导 `/` 就正常）⇒ 去重**一律用子串 `in` 判」（`'1/027/302.htm' in seen`），不用 `/…/` 正则。
  · 本机 `ws` / `requests` / `urllib3` 不可靠 ⇒ 抓取走 `news/fetch.py`（纯 urllib）。

用法：
  python3 news/ith_dedup.py                # 打印 RSS 60 条中 NEW / SEEN_HIT 计数 + NEW 列表
  python3 news/ith_dedup.py --json         # 机器可读
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fetch import get_text  # noqa: E402

SEEN = os.path.join(HERE, "SEEN.md")
RSS = "https://www.ithome.com/rss/"
TAG = "1/027/"


def parse_items(xml):
    """把 RSS 切成 item 段（不用 re，避免本机 re 路径式 pattern 的坑）。"""
    out = []
    i = 0
    while True:
        a = xml.find("<item>", i)
        if a < 0:
            break
        b = xml.find("</item>", a)
        if b < 0:
            break
        out.append(xml[a + 6:b])
        i = b + 7
    return out


def field(item, tag):
    a = item.find("<%s>" % tag)
    if a < 0:
        return ""
    a += len(tag) + 2
    b = item.find("</%s>" % tag, a)
    v = item[a:b] if b > 0 else ""
    if v.startswith("<![CDATA["):
        v = v[9:]
    if v.endswith("]]>"):
        v = v[:-3]
    return v.strip()


def art_id(link):
    i = link.find(TAG)
    if i < 0:
        return None
    j = i + len(TAG)
    k = j
    while k < len(link) and link[k].isdigit():
        k += 1
    return link[j:k] or None


def main():
    seen = open(SEEN, encoding="utf-8").read()
    xml = get_text(RSS)
    items = parse_items(xml)
    rows = []
    for it in items:
        link = field(it, "link")
        i = art_id(link)
        if not i:
            continue
        rows.append({"id": i, "link": link, "title": field(it, "title"),
                     "date": field(it, "pubDate"),
                     "hit": (TAG + i + ".htm") in seen})
    new = [r for r in rows if not r["hit"]]
    if "--json" in sys.argv:
        print(json.dumps({"total": len(rows), "hit": len(rows) - len(new),
                          "new": len(new), "rows": rows}, ensure_ascii=False, indent=1))
        return
    print("RSS_ITEMS %d  SEEN_HIT %d  NEW %d" % (len(rows), len(rows) - len(new), len(new)))
    for r in new:
        print("%s | %s | %s" % (r["date"][:22], r["id"], r["title"][:80]))


if __name__ == "__main__":
    main()
