#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ith_extract.py — 抓 IT之家 正文 + 首图（只存 URL，不下载）。

踩坑记录（沿用 ith_dedup.py 口径）：
  · 正文容器 = `<div class="post_content " id="paragraph">`（class 末尾带空格，别用精确匹配）。
  · 正文图 `src` 常是懒加载占位（`images/v2/t.png` / `data:image`），**真图在 `data-original`**。
  · 排除 logo / icon / avatar / 1x1 / base64；`x-bce-process=…watermark…` 的参数**要保留**（下游据此弃图）。
  · 本机 `re` 对路径式 pattern 不可靠 ⇒ 解析一律用 `find` / `split`。

用法：
  python3 news/ith_extract.py 1/028/028 1/028/024 ...      # 打印正文前 1400 字 + 首图
  python3 news/ith_extract.py --json 1/028/028              # 机器可读（含全部 img）
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fetch import get  # noqa: E402

UA_REF = "https://www.ithome.com/"

BAD_WORDS = ("logo", "icon", "avatar", "1x1", "base64:", "data:image",
             "/v2/t.png", "spacer", "blank.gif", "placeholder")


def _abs(u):
    if not u:
        return ""
    if u.startswith("//"):
        return "https:" + u
    if u.startswith("/"):
        return "https://www.ithome.com" + u
    return u


def _attr(tag, name):
    """从单个 <img ...> 片段里取属性值（支持单/双引号）。"""
    for q in ('"', "'"):
        k = name + "=" + q
        i = tag.find(k)
        if i >= 0:
            j = tag.find(q, i + len(k))
            if j > i:
                return tag[i + len(k):j]
    return ""


def extract(key):
    """key = `1/028/028`（可带 .htm）。返回 dict。"""
    k0 = key.strip("/").replace(".htm", "")
    url = "https://www.ithome.com/%s.htm" % k0
    r = get(url, referer=UA_REF)
    out = {"key": k0, "url": url, "status": r["status"], "err": r["err"],
           "title": "", "text": "", "imgs": [], "chars": 0, "img_url": ""}
    if not r["body"]:
        return out
    h = r["body"].decode("utf-8", "replace")

    t0 = h.find("<title>")
    t1 = h.find("</title>", t0)
    if t0 > 0 and t1 > t0:
        out["title"] = h[t0 + 7:t1].replace(" - IT之家", "").strip()

    i = h.find('id="paragraph"')
    if i < 0:
        return out
    j = h.find('<div class="related_post"', i)
    if j < 0:
        j = h.find('id="prev-related', i)
    if j < 0:
        j = i + 40000
    body = h[i:j]

    for tag in ("script", "style"):
        while True:
            a = body.find("<%s" % tag)
            if a < 0:
                break
            b = body.find("</%s>" % tag, a)
            if b < 0:
                body = body[:a]
                break
            body = body[:a] + body[b + len(tag) + 3:]

    k = 0
    while True:
        a = body.find("<img", k)
        if a < 0:
            break
        b = body.find(">", a)
        if b < 0:
            break
        tag = body[a:b + 1]
        k = b + 1
        cand = _attr(tag, "data-original") or _attr(tag, "data-src") or _attr(tag, "src")
        cand = _abs(cand)
        low = cand.lower()
        if not cand or any(w in low for w in BAD_WORDS):
            continue
        out["imgs"].append({"url": cand, "w": _attr(tag, "w"), "h": _attr(tag, "h")})

    txt = body
    for sep in ("</p>", "<br>", "<br/>", "</div>", "</h2>"):
        txt = txt.replace(sep, "\n")
    while True:
        a = txt.find("<")
        if a < 0:
            break
        b = txt.find(">", a)
        if b < 0:
            txt = txt[:a]
            break
        txt = txt[:a] + txt[b + 1:]
    for a, b in (("&nbsp;", " "), ("&amp;", "&"), ("&quot;", '"'), ("&lt;", "<"),
                 ("&gt;", ">"), ("&#8221;", '"'), ("&#8220;", '"')):
        txt = txt.replace(a, b)
    lines = [" ".join(x.split()) for x in txt.split("\n")]
    lines = [x for x in lines if x and not x.startswith("感谢IT之家网友")]
    out["text"] = "\n".join(lines)
    out["chars"] = len(out["text"].replace("\n", ""))
    if out["imgs"]:
        out["img_url"] = out["imgs"][0]["url"]
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--json" in sys.argv:
        print(json.dumps([extract(a) for a in args], ensure_ascii=False, indent=1))
        return
    for a in args:
        d = extract(a)
        print("=" * 70)
        print("%s | status=%s | chars=%d | imgs=%d" % (d["key"], d["status"], d["chars"], len(d["imgs"])))
        print("TITLE:", d["title"])
        print("IMG0:", d["img_url"] or "无")
        print("-" * 70)
        print(d["text"][:1400])


if __name__ == "__main__":
    main()
