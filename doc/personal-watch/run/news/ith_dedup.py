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

# ⚠️ 2026-11-17 第 291 轮修：原来硬编码 `1/027/`（写死当天的路径段）。
# IT之家 的 URL 路径会翻页（实测 11-17 由 `1/027/` 翻到 `1/028/`）⇒ 硬编码会把**整批新条目**
# 静默丢掉（`art_id()` 返回 None ⇒ 被 continue 跳过），RSS 报 `RSS_ITEMS 12` 而正文其实回 60 条。
# 改为**路径无关**：取 `/1/028/060.htm` 里的 `1/028/060.htm` 三段式 key。
# 去重 key 沿用历史口径（**整段路径 + .htm**），与 SEEN.md 里既有 2,900+ 行格式一致。


def path_key(link):
    """`https://www.ithome.com/1/028/060.htm` -> `1/028/060.htm`（找不到就 None）。"""
    i = link.find("ithome.com/")
    if i < 0:
        return None
    p = link[i + len("ithome.com/"):].strip()
    j = p.find("?")
    if j >= 0:
        p = p[:j]
    seg = p.split("/")
    # 期望 3 段：<d>/<ddd>/<id>.htm（例 `1/028/060.htm`、`1/027/993.htm`）
    if len(seg) < 3 or not seg[0].isdigit() or not seg[1].isdigit():
        return None
    last = seg[2]
    if not last.endswith(".htm") or not last[:-4].isdigit():
        return None
    # ⚠️ 2026-11-17 第 294 轮修（真因）：原来 `"/".join(seg[:3])` 会带出**前导 `/`**
    # （`/1/028/437.htm`）⇒ `k in seen` **永远 False**，去重彻底失效（第 291 轮报的 `SEEN_HIT 8`
    # 实际来自 SEEN.md 里带前导 `/` 的 8 行历史条目）。改为去前导 `/`，与 SEEN.md 主流口径
    # （`1/028/256` 式）一致，另外在 main() 里对首个 `/` 变体做兜底匹配。
    return "/".join(seg[:3]).lstrip("/")


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
    """兼容旧调用：返回短 id（`1/028/060.htm` -> `060`）。"""
    k = path_key(link)
    if not k:
        return None
    return k.rsplit("/", 1)[1][:-4] or None


def main():
    seen = open(SEEN, encoding="utf-8").read()
    xml = get_text(RSS)
    items = parse_items(xml)
    rows = []
    for it in items:
        link = field(it, "link")
        k = path_key(link)
        if not k:
            continue
        rows.append({"id": k.rsplit("/", 1)[1][:-4], "key": k, "link": link,
                     "title": field(it, "title"),
                     "date": field(it, "pubDate"),
                     "hit": (k in seen) or ("/" + k in seen)})
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
