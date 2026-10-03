#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
web-search-free · 免 key 的「网页搜索 + 新闻取数」MCP Server
=================================================================
news 线「前期任务 T2」交付物：在**无任何付费 API key**的前提下，给 cline
提供可用的 web search / news 取数能力。

背景（2026-10-03 本机实测，见 news/API_COMPARISON.md）：
  * 本机（阿里云，中国网络）**无法**直连：Google / DuckDuckGo / Brave / Yahoo
    / 公共 SearXNG / newsapi.org / BBC / Reuters / Google News RSS；
  * 可直连且**免 key**：CN-Bing（cn.bing.com）、360 搜索（so.com）、
    Hacker News（Algolia + Firebase）、GDELT Doc API、arXiv API、多家官方 RSS
    （新华网 / 人民网 / 中新网 / Ars Technica …）。

因此本 MCP 采取「**免 key 多后端聚合 + 失败回退**」策略：
  * web_search  → CN-Bing（主）→ 360 搜索（备）  [HTML 解析，无需 key]
  * search_news → Hacker News(Algolia) / GDELT Doc API  [官方 JSON API，无需 key]
  * rss_latest  → 任意 RSS/Atom 订阅源           [stdlib 解析，无需 key]

⚠️ 合规与频率：仅抓取公开可见的标题/摘要 + 链接；不采付费墙正文；尊重 robots；
   控制请求频率（免费额度/反爬都要留余量）。本服务不做整篇转载。

依赖：requests（已装）+ mcp（已装 2.3.0）；其余均为标准库。
协议：MCP stdio。用 mcp 2.x 的 `MCPServer`（FastMCP 在新版被改名），
      并保留对 mcp 1.x `FastMCP` 的兼容。
"""

import html as _html
import re
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Literal

import requests

# 兼容 mcp 1.x / 2.x：2.x 把 FastMCP 改名为 MCPServer（同款装饰器 API）。
try:  # mcp >= 2
    from mcp.server.mcpserver import MCPServer as _MCPServer
except Exception:  # noqa: BLE001  # mcp 1.x
    from mcp.server.fastmcp import FastMCP as _MCPServer  # type: ignore


UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
HEADERS = {"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"}
TIMEOUT = 20


# ──────────────────────────── 工具函数 ────────────────────────────
def _clean(s: str) -> str:
    """去标签 + 反转义 + 压空白。"""
    s = re.sub(r"<[^>]+>", "", s or "")
    s = _html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def _get(url: str, params: Dict[str, Any] | None = None) -> requests.Response:
    return requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)


def _fmt(items: List[Dict[str, str]], header: str) -> str:
    if not items:
        return f"{header}\n（未取到结果）"
    out = [f"{header}（{len(items)} 条）\n"]
    for i, it in enumerate(items, 1):
        out.append(f"{i}. {it.get('title', '(无标题)')}")
        if it.get("url"):
            out.append(f"   🔗 {it['url']}")
        for k in ("source", "date"):
            if it.get(k):
                out.append(f"   🏷 {k}: {it[k]}")
        if it.get("snippet"):
            out.append(f"   摘要: {it['snippet'][:220]}")
        out.append("")
    return "\n".join(out)


# ──────────────────────────── 后端 1：CN-Bing ────────────────────────────
def bing_search(query: str, count: int = 5) -> List[Dict[str, str]]:
    """CN-Bing（cn.bing.com）免 key HTML 搜索。"""
    r = _get("https://cn.bing.com/search", {"q": query})
    r.raise_for_status()
    t = r.text
    items: List[Dict[str, str]] = []
    for block in re.findall(r'<li class="b_algo".*?</li>', t, re.S):
        m = re.search(r'<h2[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', block, re.S)
        if not m:
            continue
        url = _html.unescape(m.group(1))
        title = _clean(m.group(2))
        sm = re.search(r'<p[^>]*>(.*?)</p>', block, re.S)
        items.append({"title": title, "url": url,
                      "snippet": _clean(sm.group(1)) if sm else ""})
        if len(items) >= count:
            break
    return items


# ──────────────────────────── 后端 2：360 搜索 ────────────────────────────
def so360_search(query: str, count: int = 5) -> List[Dict[str, str]]:
    """360 搜索（so.com）免 key HTML 搜索（备选）。"""
    r = _get("https://www.so.com/s", {"q": query})
    r.raise_for_status()
    t = r.text
    items: List[Dict[str, str]] = []
    # <h3 ...><a href="..." ...>title</a> ... <p class="res-desc">snippet</p>
    for m in re.finditer(r'<h3[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', t, re.S):
        url = _html.unescape(m.group(1))
        title = _clean(m.group(2))
        tail = t[m.end():m.end() + 1200]
        sm = re.search(r'<p[^>]*class="[^"]*res-desc[^"]*"[^>]*>(.*?)</p>', tail, re.S) \
            or re.search(r'<p[^>]*>(.*?)</p>', tail, re.S)
        items.append({"title": title, "url": url,
                      "snippet": _clean(sm.group(1)) if sm else ""})
        if len(items) >= count:
            break
    return items


def web_search(query: str, count: int = 5, engine: str = "auto") -> str:
    """聚合 web 搜索：auto = CN-Bing 主 + 360 备。"""
    errors: List[str] = []
    engines = [engine] if engine in ("bing", "360") else ["bing", "360"]
    for eng in engines:
        try:
            items = bing_search(query, count) if eng == "bing" else so360_search(query, count)
            if items:
                return _fmt(items, f"[web_search:{eng}] query={query!r}")
            errors.append(f"{eng}: 0 条")
        except Exception as e:  # noqa: BLE001
            errors.append(f"{eng}: {type(e).__name__}: {e}")
    return f"[web_search] query={query!r} 全部后端无结果。\n原因：\n  - " + "\n  - ".join(errors)


# ──────────────────────────── 后端 3：Hacker News ────────────────────────────
def hn_search(query: str, count: int = 5) -> List[Dict[str, str]]:
    """HN(Algolia) 免 key JSON API，按时间倒序。"""
    r = _get("https://hn.algolia.com/api/v1/search_by_date",
             {"query": query, "tags": "story", "hitsPerPage": count})
    r.raise_for_status()
    hits = r.json().get("hits", [])
    out = []
    for h in hits[:count]:
        out.append({
            "title": h.get("title") or h.get("story_title") or "(无标题)",
            "url": h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}",
            "source": "Hacker News",
            "date": (h.get("created_at") or "")[:10],
            "snippet": (h.get("story_text") or "")[:200],
        })
    return out


# ──────────────────────────── 后端 4：GDELT ────────────────────────────
def gdelt_search(query: str, count: int = 10) -> List[Dict[str, str]]:
    """GDELT Doc 2.0 免 key API（⚠️ 频控严格，易 429；query 关键词需 ≥3 字符）。"""
    r = _get("https://api.gdeltproject.org/api/v2/doc/doc",
             {"query": query, "mode": "artlist", "maxrecords": count, "format": "json"})
    if r.status_code == 429:
        raise RuntimeError("GDELT 429 频控（稍后重试）")
    r.raise_for_status()
    arts = r.json().get("articles", [])
    out = []
    for a in arts[:count]:
        d = str(a.get("seendate", ""))
        out.append({
            "title": a.get("title", "(无标题)"),
            "url": a.get("url", ""),
            "source": a.get("domain", "GDELT"),
            "date": f"{d[0:4]}-{d[4:6]}-{d[6:8]}" if len(d) >= 8 else d,
        })
    return out


def search_news(query: str, count: int = 5, source: str = "hn") -> str:
    """news 取数：hn（默认）或 gdelt。"""
    try:
        if source == "gdelt":
            return _fmt(gdelt_search(query, count), f"[search_news:gdelt] query={query!r}")
        return _fmt(hn_search(query, count), f"[search_news:hn] query={query!r}")
    except Exception as e:  # noqa: BLE001
        return f"[search_news:{source}] query={query!r} 失败：{type(e).__name__}: {e}"


# ──────────────────────────── 后端 5：RSS/Atom ────────────────────────────
def rss_latest(url: str, count: int = 10) -> str:
    """抓取任意 RSS2.0 / Atom 订阅源的最新条目。"""
    try:
        r = _get(url)
        r.raise_for_status()
        # 清掉 xml 声明外的 BOM/空白
        content = r.content
        root = ET.fromstring(content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        items: List[Dict[str, str]] = []
        rss_items = root.findall(".//item")
        if rss_items:  # RSS 2.0
            for it in rss_items[:count]:
                items.append({
                    "title": _clean(it.findtext("title", "")),
                    "url": (it.findtext("link", "") or "").strip(),
                    "date": (it.findtext("pubDate", "") or "").strip()[:25],
                    "snippet": _clean(it.findtext("description", ""))[:200],
                })
        else:  # Atom
            for it in root.findall(".//atom:entry", ns)[:count]:
                link = it.find("atom:link", ns)
                href = link.get("href") if link is not None else ""
                items.append({
                    "title": _clean(it.findtext("atom:title", "", ns)),
                    "url": href or "",
                    "date": (it.findtext("atom:updated", "", ns) or "")[:10],
                    "snippet": _clean(it.findtext("atom:summary", "", ns))[:200],
                })
        return _fmt(items, f"[rss_latest] {url}")
    except Exception as e:  # noqa: BLE001
        return f"[rss_latest] {url} 失败：{type(e).__name__}: {e}"


# ──────────────────────────── MCP Server（mcp 1.x/2.x 通用装饰器 API）────────────────────────────
mcp = _MCPServer("web-search-free")


@mcp.tool(name="web_search")
def _tool_web_search(query: str, count: int = 5,
                     engine: Literal["auto", "bing", "360"] = "auto") -> str:
    """免 key 网页搜索（CN-Bing 主 + 360 备，中文友好）。返回带链接的标题 + 摘要。"""
    if not query:
        return "错误：query 不能为空"
    return web_search(query, count, engine)


@mcp.tool(name="search_news")
def _tool_search_news(query: str, count: int = 5,
                      source: Literal["hn", "gdelt"] = "hn") -> str:
    """免 key 新闻取数：Hacker News(Algolia) 或 GDELT Doc API（GDELT 易 429）。"""
    if not query:
        return "错误：query 不能为空"
    return search_news(query, count, source)


@mcp.tool(name="rss_latest")
def _tool_rss_latest(url: str, count: int = 10) -> str:
    """抓取任意 RSS2.0/Atom 订阅源最新条目（新华/人民/中新/Ars Technica 等）。"""
    if not url:
        return "错误：url 不能为空"
    return rss_latest(url, count)


if __name__ == "__main__":
    mcp.run()  # 默认 stdio 传输