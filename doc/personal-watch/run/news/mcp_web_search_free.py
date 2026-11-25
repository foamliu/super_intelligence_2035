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
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Dict, List, Literal, Tuple

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


# ──────────────────── T10：统一中文新闻入口 fetch_cn_news() ────────────────────
#
# 背景（2026-10-03 实测，见 news/API_COMPARISON.md 与 news/FETCH_CN_NEWS.md）：
#   🔴 中文权威源里「接口 200」≠「有新闻」—— 死源照样返 200/300 条。
#   本函数把**已实测活源**固化为统一入口，并内建 **死源黑名单 / pubDate≤72h / Content-Type 校验**。
#
# 🔴 死源黑名单（返 200 但内容不更新，**永不请求**；内容停更时间 = 2026-10-03 实测）：
#   - 新华网   www.xinhuanet.com/{tech,politics,world}/news_*.xml   → 内容停在 2022
#   - 新华英文 www.xinhuanet.com/english/rss/*                       → 停在 2017/2018
#   - 人民网   www.people.com.cn/rss/*.xml                           → 停在 2021/2024
#   - 央视RSS  www.cctv.com/program/rss/**/index.xml                 → 停在 2006/2007
#   （要新华/人民/央视的实时内容 → 只能走"网页列表页 / 站内接口"并校验页面日期；
#     央视网已实测可用**站内 JSONP 接口**，见下。本函数**绝不**请求上述死源。）
DEAD_SOURCES: List[str] = [
    "www.xinhuanet.com/{tech,politics,world}/news_*.xml（内容停在 2022）",
    "www.xinhuanet.com/english/rss/*（停在 2017/2018）",
    "www.people.com.cn/rss/*.xml（停在 2021/2024）",
    "www.cctv.com/program/rss/*（停在 2006/2007）",
]

# ✅ 已实测活源白名单：(媒体名, URL, 类型)
CN_LIVE_SOURCES: List[Tuple[str, str, str]] = [
    ("中新网", "https://www.chinanews.com.cn/rss/scroll-news.xml", "rss"),   # 即时（当日持续更新）
    ("中新网", "https://www.chinanews.com.cn/rss/world.xml", "rss"),         # 国际
    ("中新网", "https://www.chinanews.com.cn/rss/finance.xml", "rss"),       # 财经
    # ⚠️ URL 必须写死正确值：news.un.org/zh/rss 会 404 并返回 HTML（那才是"unable to parse"的真因）
    ("联合国新闻", "https://news.un.org/feed/subscribe/zh/news/all/rss.xml", "rss"),
    # 央视网 news.cctv.com 的 HTML 是 JS 渲染 → 走其**站内 JSONP 接口**（数据源，带 focus_date）
    ("央视网", "https://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/news_1.jsonp", "cctv"),
    ("央视网", "https://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/tech_1.jsonp", "cctv"),
]

CN_UA = "Mozilla/5.0 (compatible; PersonalWatch/1.0)"  # 可识别 UA（通用防御）
CN_MAX_AGE_HOURS = 72                                  # 日报口径：只留 ≤72h
RSS_CONTENT_TYPES = ("application/rss+xml", "text/xml", "application/xml", "application/atom+xml")


def _iso(dt: datetime) -> str:
    """转 ISO8601（UTC）。"""
    return dt.astimezone(timezone.utc).isoformat()


def _parse_rfc822(s: str):
    """解析 RSS pubDate（RFC822）。失败 → None（该条**丢弃**，不用抓取时间冒充）。"""
    try:
        dt = parsedate_to_datetime((s or "").strip())
        if dt is None:
            return None
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:  # noqa: BLE001
        return None


def _parse_cctv_date(s: str):
    """解析央视 focus_date（形如 '2026-10-03 11:32:17'，北京时间）。失败 → None。"""
    try:
        dt = datetime.strptime((s or "").strip(), "%Y-%m-%d %H:%M:%S")
        return dt.replace(tzinfo=timezone(timedelta(hours=8)))  # 中国标准时间
    except Exception:  # noqa: BLE001
        return None


def _fetch_rss(source: str, url: str, now: datetime, max_age_hours: float):
    """抓单个 RSS 活源 → (items, meta)。失败**降级**（返回空 + 原因），不抛、不阻塞整轮。"""
    meta: Dict[str, Any] = {"source": source, "url": url, "kind": "rss",
                            "status": None, "content_type": None, "kept": 0, "dropped": []}
    try:
        r = requests.get(url, headers={"User-Agent": CN_UA, "Accept-Language": "zh-CN,zh;q=0.9"},
                         timeout=TIMEOUT)
    except Exception as e:  # noqa: BLE001
        meta["status"] = "REQUEST_FAIL"
        meta["dropped"].append(f"请求失败 {type(e).__name__}: {e}")
        return [], meta
    meta["status"] = r.status_code
    ct = (r.headers.get("Content-Type") or "").lower()
    meta["content_type"] = ct
    # 🔴 Content-Type 校验：非 rss/xml（拿到 HTML / 404 页）→ **判源失败并记录**（不得静默当"无新增"）
    if r.status_code != 200 or not any(k in ct for k in RSS_CONTENT_TYPES):
        meta["dropped"].append(f"Content-Type/status 不符（status={r.status_code}, ct={ct!r}）→ 判源失败")
        return [], meta
    try:
        root = ET.fromstring(r.content)
    except Exception as e:  # noqa: BLE001
        meta["dropped"].append(f"XML 解析失败 {type(e).__name__}: {e}")
        return [], meta
    items: List[Dict[str, Any]] = []
    for it in root.findall(".//item"):
        title = _clean(it.findtext("title", ""))
        link = (it.findtext("link", "") or "").strip()
        pub = (it.findtext("pubDate", "") or "").strip()
        if not title or not link:
            meta["dropped"].append(f"缺 title/link：{title[:24]!r}")
            continue
        dt = _parse_rfc822(pub)
        if dt is None:
            meta["dropped"].append(f"无/坏 pubDate（{pub[:31]!r}）：{title[:24]!r}")
            continue
        age_h = (now - dt).total_seconds() / 3600.0
        if age_h > max_age_hours:
            meta["dropped"].append(f"超龄 {age_h:.1f}h>{max_age_hours}h：{title[:24]!r}")
            continue
        items.append({"title": title, "source": source, "url": link,
                      "published": _iso(dt), "lang": "zh", "type": "news",
                      "snippet": _clean(it.findtext("description", ""))[:160]})
    meta["kept"] = len(items)
    return items, meta


def _fetch_cctv(source: str, url: str, now: datetime, max_age_hours: float):
    """抓央视网**站内 JSONP 接口**（news.cctv.com 页面为 JS 渲染，真实数据在此接口）。"""
    meta: Dict[str, Any] = {"source": source, "url": url, "kind": "cctv-jsonp",
                            "status": None, "content_type": None, "kept": 0, "dropped": []}
    try:
        r = requests.get(url, headers={"User-Agent": CN_UA}, timeout=TIMEOUT)
    except Exception as e:  # noqa: BLE001
        meta["status"] = "REQUEST_FAIL"
        meta["dropped"].append(f"请求失败 {type(e).__name__}: {e}")
        return [], meta
    meta["status"] = r.status_code
    meta["content_type"] = (r.headers.get("Content-Type") or "").lower()
    if r.status_code != 200:
        meta["dropped"].append(f"HTTP {r.status_code} → 判源失败")
        return [], meta
    # ⚠️ JSONP 接口的 Content-Type 是 text/html（非 xml）；此处改以「能否解析出 JSONP.data.list」作校验：
    #    若拿到 HTML/404 页 → JSON 解析必失败 → 同样**判失败并记录**（等价满足 Content-Type 校验的目的）。
    body = r.content.decode("utf-8", errors="replace")
    m = re.search(r"\(([\s\S]*)\)\s*;?\s*$", body.strip())
    if not m:
        meta["dropped"].append("非 JSONP 结构（疑似拿到 HTML/404 页）→ 判源失败")
        return [], meta
    try:
        lst = json.loads(m.group(1)).get("data", {}).get("list", [])
    except Exception as e:  # noqa: BLE001
        meta["dropped"].append(f"JSONP 解析失败 {type(e).__name__}: {e}")
        return [], meta
    items: List[Dict[str, Any]] = []
    for rec in lst:
        title = _clean(rec.get("title", ""))
        link = (rec.get("url", "") or "").strip()
        dt = _parse_cctv_date(rec.get("focus_date", ""))
        if not title or not link:
            meta["dropped"].append(f"缺 title/url：{title[:24]!r}")
            continue
        if dt is None:
            meta["dropped"].append(f"无/坏 focus_date：{title[:24]!r}")
            continue
        age_h = (now - dt).total_seconds() / 3600.0
        if age_h > max_age_hours:
            meta["dropped"].append(f"超龄 {age_h:.1f}h>{max_age_hours}h：{title[:24]!r}")
            continue
        items.append({"title": title, "source": source, "url": link,
                      "published": _iso(dt), "lang": "zh", "type": "news",
                      "snippet": _clean(rec.get("brief", ""))[:160]})
    meta["kept"] = len(items)
    return items, meta


def fetch_cn_news(limit: int = 30, max_age_hours: float = CN_MAX_AGE_HOURS) -> Dict[str, Any]:
    """统一中文新闻入口（T10）：聚合已实测活源 → 去重 → 按 published 倒序。

    返回 ``{"items": [...], "meta": {...}}``；每条 item =
    ``{title, source, url, published(ISO8601), lang:"zh", type:"news"}``（+ snippet 便于落盘）。
    单源失败**降级**：记录到 meta.per_source，不影响其它源。
    """
    now = datetime.now(timezone.utc)
    items: List[Dict[str, Any]] = []
    metas: List[Dict[str, Any]] = []
    seen = set()
    for source, url, kind in CN_LIVE_SOURCES:
        fn = _fetch_rss if kind == "rss" else _fetch_cctv
        try:
            got, meta = fn(source, url, now, max_age_hours)
        except Exception as e:  # noqa: BLE001  # 兜底：整轮不得因一个源卡死
            got, meta = [], {"source": source, "url": url, "kind": kind, "status": "EXC",
                             "content_type": None, "kept": 0,
                             "dropped": [f"{type(e).__name__}: {e}"]}
        metas.append(meta)
        for it in got:
            key = it["url"].split("?")[0]
            if key in seen:
                continue
            seen.add(key)
            items.append(it)
    items.sort(key=lambda x: x["published"], reverse=True)
    items = items[:limit]
    return {"items": items,
            "meta": {"generated": _iso(now), "per_source": metas,
                     "dropped_total": sum(len(m["dropped"]) for m in metas)}}


def cn_news_report(limit: int = 30, max_age_hours: float = CN_MAX_AGE_HOURS,
                   as_json: bool = False) -> str:
    """``fetch_cn_news`` 的报告（人类可读 / JSON）：条目 + 各源新鲜度 + 丢弃原因。"""
    res = fetch_cn_news(limit, max_age_hours)
    if as_json:
        return json.dumps(res, ensure_ascii=False, indent=2)
    out = [f"[cn_news] 生成 {res['meta']['generated']} ｜ 新鲜度窗口 ≤{max_age_hours}h ｜ 活源 {len(CN_LIVE_SOURCES)} 个",
           f"命中 {len(res['items'])} 条（按发布时间倒序）：", ""]
    for i, it in enumerate(res["items"], 1):
        out.append(f"{i}. {it['title']}")
        out.append(f"   🔗 {it['url']}")
        out.append(f"   🏷 来源：{it['source']} ｜ 发布：{it['published']} ｜ lang={it['lang']} type={it['type']}")
        if it.get("snippet"):
            out.append(f"   摘要：{it['snippet']}")
        out.append("")
    out.append("—— 各源状态 / 新鲜度 / 丢弃 ——")
    for m in res["meta"]["per_source"]:
        out.append(f"• {m['source']} <{m['kind']}> status={m['status']} ct={m['content_type']!r} "
                   f"kept={m['kept']} dropped={len(m['dropped'])}")
        for d in m["dropped"][:6]:
            out.append(f"    - {d}")
    out.append(f"\n丢弃合计：{res['meta']['dropped_total']} 条（原因见上）")
    out.append("死源黑名单（永不请求）：" + " ；".join(DEAD_SOURCES))
    return "\n".join(out)


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


@mcp.tool(name="cn_news")
def _tool_cn_news(limit: int = 30, max_age_hours: float = CN_MAX_AGE_HOURS) -> str:
    """统一中文新闻入口（T10）：中新网 RSS + 联合国新闻·中文 RSS + 央视网站内接口（均已实测活源）。

    内建死源黑名单 + pubDate≤72h 校验 + Content-Type 校验；单源失败降级不阻塞整轮。
    """
    return cn_news_report(limit, max_age_hours)


# ──────────────────── CLI（T10：MCP 未装进 cline 时，直调是"一等公民"）────────────────────
def _cli_cn_news(argv: List[str]) -> int:
    import argparse
    p = argparse.ArgumentParser(
        prog="mcp_web_search_free.py --cn-news",
        description="统一中文新闻入口（T10）：聚合 中新网 / 联合国新闻·中文 / 央视网 已实测活源")
    p.add_argument("--cn-news", action="store_true", help="抓取中文活源新闻（本入口）")
    p.add_argument("--limit", type=int, default=30, help="最多返回条数（默认 30）")
    p.add_argument("--max-age-hours", type=float, default=CN_MAX_AGE_HOURS,
                   help="新鲜度窗口（小时，默认 72）")
    p.add_argument("--json", action="store_true", help="输出 JSON（含 meta：各源新鲜度 / 丢弃原因）")
    a = p.parse_args(argv)
    print(cn_news_report(a.limit, a.max_age_hours, a.json))
    return 0


if __name__ == "__main__":
    import sys as _sys
    if "--cn-news" in _sys.argv:       # CLI 直调模式
        raise SystemExit(_cli_cn_news(_sys.argv[1:]))
    mcp.run()                          # 默认 stdio 传输（MCP）