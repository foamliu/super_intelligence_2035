#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
arxiv_fetch · arXiv 论文取数（research 线 R1/R2 交付物）
=================================================================
目的：把「每轮要跑的查询清单」**固化**（read research/queries.json），
      并对 arXiv 官方 API（`https://export.arxiv.org/api/query`，Atom XML）
      做**可复现、带校验**的取数 —— 供 research agent 每轮采集复用。

硬规则（继承 news 线铁律）：
  1. **礼貌限速**：相邻请求间隔 >= rate_limit_seconds（默认 3s，arXiv 官方要求）。
  2. **`200 != 有料`**：HTTP 200 之后**必须**校验 `Content-Type` 为 XML
     （application/atom+xml / text/xml / application/xml），否则判**源失败**并记录；
     再校验能解析出 Atom `entry`（拿到 HTML/404/空 feed 一律判失败）。
  3. **新鲜度窗口**：只保留 `max(published, updated)` 在 window_hours（默认 72h）内的条目；
     **解析不到日期 -> 丢弃**（不许用抓取时间冒充发布日期）。
  4. **去重主键 = arXiv ID**（去版本号后的 `YYYY.MMNNN`）；本轮内去重 + 可选比对 SEEN。
  5. **限流退避**：HTTP 429/503 做**有界重试**（`retries` 次，间隔 `retry_backoff_seconds`）；
     其余失败（200 非 XML / 解析失败 / 空 feed）**一律记录为 FAIL**，不重试、不静默丢弃。

依赖：requests（本机已装）；其余为标准库。

CLI 用法：
  python3 research/arxiv_fetch.py --selftest                 # 单点自测（端点/CT/解析，贴证据用）
  python3 research/arxiv_fetch.py --fetch                    # 跑 queries.json 全部查询（人类可读）
  python3 research/arxiv_fetch.py --fetch --json             # JSON（items + meta.per_query）
  python3 research/arxiv_fetch.py --fetch --json --out research/_last_fetch.json
  python3 research/arxiv_fetch.py --query 'cat:cs.CL AND all:"large language model"' --max-results 5 --json
  python3 research/arxiv_fetch.py --fetch --seen research/SEEN.md   # 过滤已收录 ID
"""

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None

ENDPOINT = "https://export.arxiv.org/api/query"
ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV = "{http://arxiv.org/schemas/atom}"
OPENSEARCH = "{http://a9.com/-/spec/opensearch/1.1/}"
XML_CT_OK = ("application/atom+xml", "application/xml", "text/xml")
HEADERS = {"User-Agent": "PersonalWatch/1.0 (research line; contact: local)"}
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG = SCRIPT_DIR / "queries.json"

_LAST_CALL = [0.0]


# ──────────────────────────── 基础工具 ────────────────────────────
def _now_utc():
    return datetime.now(timezone.utc)


def _clean(s):
    """压缩空白（Atom title/summary 常含换行）。"""
    return re.sub(r"\s+", " ", (s or "")).strip()


def _parse_dt(s):
    """arXiv 时间戳：2026-10-01T17:59:55Z（偶见 +00:00）。解析失败返回 None。"""
    if not s:
        return None
    s = s.strip()
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _throttle(min_interval):
    """保证相邻请求间隔 >= min_interval 秒（礼貌限速）。"""
    dt = time.monotonic() - _LAST_CALL[0]
    if _LAST_CALL[0] and dt < min_interval:
        time.sleep(min_interval - dt)
    _LAST_CALL[0] = time.monotonic()


def _http_get(url, params, timeout):
    if requests is not None:
        r = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
        return r.status_code, r.headers.get("Content-Type", ""), r.text
    qs = urllib.parse.urlencode(params) if params else ""
    req = urllib.request.Request(url + ("?" + qs if qs else ""), headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
        return resp.status, resp.headers.get("Content-Type", ""), resp.read().decode("utf-8", "replace")


# ──────────────────────────── Atom 解析 ────────────────────────────
def _parse_feed(body):
    """解析 Atom feed -> (total_results, entries)。解析失败抛错。"""
    root = ET.fromstring(body)
    total = root.findtext(OPENSEARCH + "totalResults")
    entries = []
    for e in root.findall(ATOM + "entry"):
        raw_id = e.findtext(ATOM + "id") or ""
        m = re.search(r"abs/([0-9]{4}\.[0-9]{4,5})(v\d+)?", raw_id)
        arxiv_id = m.group(1) if m else ""
        version = (m.group(2) or "") if m else ""
        cats = [c.get("term") for c in e.findall(ATOM + "category") if c.get("term")]
        prim = e.find(ARXIV + "primary_category")
        primary = prim.get("term") if prim is not None else (cats[0] if cats else "")
        abs_url = pdf_url = ""
        for l in e.findall(ATOM + "link"):
            if l.get("rel") == "alternate":
                abs_url = l.get("href") or abs_url
            if l.get("title") == "pdf" or l.get("type") == "application/pdf":
                pdf_url = l.get("href") or pdf_url
        if not abs_url and arxiv_id:
            abs_url = "https://arxiv.org/abs/" + arxiv_id
        if not pdf_url and arxiv_id:
            pdf_url = "https://arxiv.org/pdf/" + arxiv_id
        entries.append({
            "arxiv_id": arxiv_id,
            "version": version,
            "title": _clean(e.findtext(ATOM + "title")),
            "authors": [a.findtext(ATOM + "name") for a in e.findall(ATOM + "author")
                        if a.findtext(ATOM + "name")],
            "published": (e.findtext(ATOM + "published") or "").strip(),
            "updated": (e.findtext(ATOM + "updated") or "").strip(),
            "category": primary,
            "categories": cats,
            "summary": _clean(e.findtext(ATOM + "summary")),
            "abs_url": abs_url,
            "pdf_url": pdf_url,
            "comment": _clean(e.findtext(ARXIV + "comment")),
            "journal_ref": _clean(e.findtext(ARXIV + "journal_ref")),
        })
    return (int(total) if total and total.isdigit() else None), entries


# ──────────────────────────── 取数 ────────────────────────────
def query_arxiv(search_query, max_results=40, start=0, sort_by="submittedDate",
                sort_order="descending", min_interval=3.0, timeout=30,
                retries=2, retry_backoff=20.0):
    """跑一次查询。返回 (meta, entries)。meta 记录 status / content_type / ok / error / attempts。

    对 **429 / 503（限流 / 暂不可用）** 做**有界重试**（最多 `retries` 次，间隔 `retry_backoff` 秒，
    每次仍遵守 >= min_interval 的礼貌限速）；**其余情况按铁律判失败并记录**
    （200 但非 XML、解析失败、空 feed 一律 FAIL，不重试、不静默丢弃）。
    """
    params = {
        "search_query": search_query,
        "start": start,
        "max_results": max_results,
        "sortBy": sort_by,
        "sortOrder": sort_order,
    }
    meta = {
        "search_query": search_query, "status": None, "content_type": "",
        "ok": False, "error": None, "total_results": None, "n_entries": 0,
        "attempts": 0, "retries": [],
    }
    for attempt in range(1, retries + 2):
        meta["attempts"] = attempt
        _throttle(min_interval)
        try:
            status, ctype, body = _http_get(ENDPOINT, params, timeout)
        except Exception as exc:  # noqa: BLE001
            meta["error"] = "request failed: %s" % exc
            if attempt <= retries:
                meta["retries"].append("attempt %d: %s -> backoff %.0fs" % (attempt, exc, retry_backoff))
                time.sleep(retry_backoff)
                continue
            return meta, []
        meta["status"] = status
        meta["content_type"] = ctype
        if status in (429, 503) and attempt <= retries:  # 限流/暂不可用 -> 退避重试
            meta["retries"].append("attempt %d: HTTP %s -> backoff %.0fs" % (attempt, status, retry_backoff))
            time.sleep(retry_backoff)
            continue
        if status != 200:
            meta["error"] = "HTTP %s (expected 200)" % status
            return meta, []
        if not any(ok in ctype.lower() for ok in XML_CT_OK):
            meta["error"] = "content-type not XML: %r (200 != 有料)" % ctype
            return meta, []
        try:
            total, entries = _parse_feed(body)
        except ET.ParseError as exc:
            meta["error"] = "atom parse error: %s" % exc
            return meta, []
        meta["ok"] = True
        meta["total_results"] = total
        meta["n_entries"] = len(entries)
        if not entries:
            meta["ok"] = False  # 铁律：空 feed 判失败（不得当成"无新增"）
            meta["error"] = "empty feed (200 but no <entry>)"
        return meta, entries
    return meta, []


def _within_window(entry, window_hours, now):
    """R2′ 口径：新鲜度**以首次提交（`published`）为准**。
    `updated` 也解析（用于交叉核对 / 展示），但**不得**用「近期更新」把陈年论文洗成新论文；
    `published` 缺失时才退回 `updated`；两者都解析不到 -> **丢弃**（不许用抓取时间冒充）。"""
    p = _parse_dt(entry.get("published"))
    u = _parse_dt(entry.get("updated"))
    first = p if p is not None else u
    if first is None:
        return False, "no parseable date"
    age_h = (now - first).total_seconds() / 3600.0
    if age_h <= window_hours:
        note = ""
        if p is not None and u is not None and u > p:
            note = " (updated 较新，但以首次提交计)"
        return True, "since-first-submit %.1fh <= %gh%s" % (age_h, window_hours, note)
    return False, "stale %.1fh > %gh (since first submit)" % (age_h, window_hours)


def auto_window_hours(now, config):
    """R2′ 时效口径（自动）：

    - **常态（工作日）**：日报口径 <= `window_hours`（默认 72h）；
    - **周末 / 周一早**：arXiv **工作日 20:00 ET 公告、周末不发**（周五投的周一才公告）
      -> 放宽到覆盖「**最近一次公告批次**」（`window_hours_weekend`，默认 120h），
      并要求日报**如实标注实际日期区间**（例：`10-01 ~ 10-03（含周末，取最近公告批次）`）。

    返回 `(window_hours, mode, note)`。
    """
    base = float(config.get("window_hours", 72))
    we = float(config.get("window_hours_weekend", 120))
    wd = now.weekday()  # Mon=0 .. Sun=6
    # 10 月美东为 EDT(UTC-4)：周一 UTC 13:00 前视为「周一早」（周一公告尚未刷新）
    if wd in (5, 6) or (wd == 0 and now.hour < 13):
        return we, "weekend_batch", (
            "含周末：arXiv 周末不公告 → 放宽至最近一次公告批次（<=%gh）；日报须如实标注实际日期区间" % we)
    return base, "daily", "日报口径：首次提交 <= %gh" % base


def load_config(path=DEFAULT_CONFIG):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def fetch_all(config, window_hours=None, seen_ids=None, max_results=None):
    """跑 config['queries'] 全部查询 -> 去重 + 新鲜度过滤。返回 {"items": [...], "meta": {...}}。"""
    now = _now_utc()
    win_mode = config.get("window_mode", "fixed")
    if window_hours is not None:
        wh = window_hours
        win_label, win_note = "override", "命令行 --window-hours 覆盖（不再自动切换）"
    elif win_mode == "auto":
        wh, win_label, win_note = auto_window_hours(now, config)
    else:
        wh = config.get("window_hours", 72)
        win_label, win_note = "fixed", "固定口径：首次提交 <= %gh" % wh
    mi = config.get("rate_limit_seconds", 3.0)
    mr = max_results if max_results is not None else config.get("max_results_per_query", 40)
    seen_ids = seen_ids or set()
    items, per_query = {}, []
    dropped = []
    for q in config["queries"]:
        meta, entries = query_arxiv(
            q["search_query"], max_results=mr, min_interval=mi,
            sort_by=config.get("sort_by", "submittedDate"),
            sort_order=config.get("sort_order", "descending"),
            timeout=config.get("timeout_seconds", 30),
            retries=config.get("retries", 2),
            retry_backoff=config.get("retry_backoff_seconds", 20.0),
        )
        meta["area"] = q.get("area")
        meta["name"] = q.get("name")
        kept = 0
        for e in entries:
            eid = e.get("arxiv_id")
            if not eid:
                continue
            if eid in seen_ids:
                dropped.append((eid, "already in SEEN", q.get("name")))
                continue
            ok, why = _within_window(e, wh, now)
            if not ok:
                dropped.append((eid, why, q.get("name")))
                continue
            if eid in items:
                items[eid]["areas"] = sorted(set(items[eid]["areas"] + [q.get("area")]))
                continue
            e["areas"] = [q.get("area")]
            e["first_seen"] = now.strftime("%Y-%m-%d")
            e["matched_query"] = q.get("name")
            items[eid] = e
            kept += 1
        meta["kept"] = kept
        per_query.append(meta)
    ordered = sorted(items.values(),
                     key=lambda x: x.get("published") or "", reverse=True)
    return {
        "items": ordered,
        "meta": {
            "generated": now.isoformat(),
            "endpoint": config.get("endpoint", ENDPOINT),
            "window_hours": wh,
            "window_mode": win_label,
            "window_note": win_note,
            "rate_limit_seconds": mi,
            "n_queries": len(config["queries"]),
            "n_kept": len(ordered),
            "n_dropped": len(dropped),
            "per_query": per_query,
            "dropped": dropped,
        },
    }


# ──────────────────────────── 输出 ────────────────────────────
def _fmt_human(res):
    lines = []
    m = res["meta"]
    wh = m.get("window_hours")
    wh_s = ("%gh" % wh) if isinstance(wh, (int, float)) else str(wh)
    lines.append("[arxiv_fetch] %s | endpoint=%s | 窗口<=%s | 查询 %d 次 | 保留 %d 篇（丢弃 %d）"
                 % (m["generated"], m["endpoint"], wh_s, m["n_queries"],
                    m["n_kept"], m["n_dropped"]))
    if m.get("window_note"):
        lines.append("  ⏱ 口径: %s（window_mode=%s）" % (m["window_note"], m.get("window_mode")))
    for it in res["items"]:
        au = it["authors"]
        alist = (", ".join(au[:3]) + (" et al" if len(au) > 3 else "")) if au else "(无作者)"
        lines.append("")
        lines.append("- [%s] %s" % (it["category"] or "?", it["title"]))
        areas = it.get("areas") or ([it["category"]] if it.get("category") else [])
        lines.append("  arXiv:%s%s | 领域: %s | published=%s updated=%s"
                     % (it["arxiv_id"], it["version"], "/".join(areas),
                        it["published"], it["updated"]))
        lines.append("  作者: %s" % alist)
        lines.append("  abs: %s" % it["abs_url"])
    lines.append("")
    lines.append("—— 各查询状态 ——")
    for q in m["per_query"]:
        flag = "OK " if q.get("ok") else "FAIL"
        label = (q.get("name") or q.get("search_query") or "?")
        att = (" attempts=%s" % q["attempts"]) if q.get("attempts", 1) > 1 else ""
        lines.append("• [%s] %-28s status=%s ct=%r kept=%s total=%s%s%s"
                     % (flag, label[:28], q.get("status"), q.get("content_type"),
                        q.get("kept", "—"), q.get("total_results"),
                        att,
                        (" err=%s" % q["error"]) if q.get("error") else ""))
    if m["dropped"]:
        lines.append("—— 丢弃（前 40）——")
        for eid, why, qn in m["dropped"][:40]:
            lines.append("  - %s [%s] %s" % (eid, qn, why))
    return "\n".join(lines)


def _fmt_probe(ev):
    """R1′ 取源复验证据的人类可读输出。"""
    lines = ["[probe] %s" % ev.get("generated")]
    a = ev.get("arxiv_api") or {}
    lines.append("• arXiv API（主力）: status=%s ok=%s ct=%r entries=%s total=%s%s"
                 % (a.get("status"), a.get("ok"), a.get("content_type"),
                    a.get("n_entries"), a.get("total_results"),
                    (" err=%s" % a["error"]) if a.get("error") else ""))
    for s in a.get("sample") or []:
        lines.append("    - arXiv:%s | %s | published=%s" % (s.get("arxiv_id"), s.get("category"), s.get("published")))
    h = ev.get("hf_daily")
    if h is not None:
        lines.append("• HF Daily Papers（副源/社区加权）: ok=%s n_ids=%s%s"
                     % (h.get("ok"), h.get("n_ids"),
                        (" ⚠ %s" % h["error"]) if h.get("error") else ""))
    r = ev.get("arxiv_rss")
    if r:
        for c, v in r.items():
            lines.append("• RSS %s: status=%s ct=%r items=%s%s"
                         % (c, v.get("status"), v.get("content_type"), v.get("items"),
                            (" note=%s" % v["note"]) if v.get("note") else ""))
    return "\n".join(lines)


def _load_seen_ids(path):
    ids = set()
    p = Path(path)
    if not p.exists():
        return ids
    for line in p.read_text(encoding="utf-8").splitlines():
        for m in re.finditer(r"\b([0-9]{4}\.[0-9]{4,5})\b", line):
            ids.add(m.group(1))
    return ids


# ─────────── 副源（R1′）：HF Daily Papers / arXiv RSS —— 可达性与加权 ───────────
HF_DAILY_ENDPOINT = "https://huggingface.co/api/daily_papers"
RSS_ENDPOINT = "https://rss.arxiv.org/rss/"


def fetch_hf_daily(timeout=15):
    """**副源**：HF Daily Papers API。用途 = 给**已收论文**打社区精选标记（`🏷 hf_daily`）。

    ⚠️ `publishedAt` 实测滞后 3~8 天 -> **不得**作新鲜度依据。
    返回 `(ok, {arxiv_id: {...}} | None, error)`；**不可达/非 JSON/空** 一律 `ok=False`
    （如实记录，**不编造标记**）。主键取 paper.id 的 arXiv ID（去版本号）。
    """
    try:
        status, ctype, body = _http_get(HF_DAILY_ENDPOINT, None, timeout)
    except Exception as exc:  # noqa: BLE001
        return False, None, "request failed: %s" % exc
    if status != 200:
        return False, None, "HTTP %s (expected 200)" % status
    if "json" not in (ctype or "").lower():
        return False, None, "content-type not JSON: %r (200 != 有料)" % ctype
    try:
        data = json.loads(body)
    except ValueError as exc:
        return False, None, "JSON parse error: %s" % exc
    if not isinstance(data, list) or not data:
        return False, None, "empty/invalid HF payload"
    ids = {}
    for row in data:
        paper = row.get("paper") or {}
        m = re.match(r"^\s*([0-9]{4}\.[0-9]{4,5})", paper.get("id") or "")
        if m:
            ids[m.group(1)] = {"publishedAt": row.get("publishedAt"), "title": paper.get("title")}
    if not ids:
        return False, None, "no parseable arXiv IDs in HF payload"
    return True, ids, None


def probe_rss(categories, timeout=20, min_interval=3.0):
    """arXiv RSS（**仅工作日可作补充**；周末必空）。返回 `{cat: {status, content_type, items, note}}`。

    空 feed（200 + `items==0`）**不得**当作「无新增」，标注「周末/未公告」。"""
    out = {}
    for c in categories:
        _throttle(min_interval)
        try:
            status, ctype, body = _http_get(RSS_ENDPOINT + c, None, timeout)
            n = body.count("<item>") if isinstance(body, str) else 0
            out[c] = {"status": status, "content_type": ctype, "items": n,
                      "note": ("周末/未公告（rss 空 feed）" if (status == 200 and n == 0) else "")}
        except Exception as exc:  # noqa: BLE001
            out[c] = {"status": None, "content_type": "", "items": 0, "error": str(exc)}
    return out


def probe_sources(config):
    """R1′：在**运行机**复验取源可达性（arXiv API 主源 / HF 副源 / RSS 工作日补充）。

    返回可直接写入 `ARXIV_API.md` / 日报的证据 dict。"""
    mi = config.get("rate_limit_seconds", 3.0)
    timeout = config.get("timeout_seconds", 30)
    first_q = config["queries"][0]["search_query"]
    meta, entries = query_arxiv(first_q, max_results=3, min_interval=mi, timeout=timeout,
                                retries=config.get("retries", 2),
                                retry_backoff=config.get("retry_backoff_seconds", 20.0))
    out = {"generated": _now_utc().isoformat(),
           "arxiv_api": {"endpoint": ENDPOINT, "status": meta["status"],
                         "content_type": meta["content_type"], "ok": meta["ok"],
                         "total_results": meta["total_results"], "n_entries": len(entries),
                         "sample": [{"arxiv_id": e["arxiv_id"], "published": e["published"],
                                     "category": e["category"]} for e in entries[:3]],
                         "error": meta["error"]}}
    hf_cfg = config.get("hf_daily") or {}
    if hf_cfg.get("enabled", True):
        ok, ids, err = fetch_hf_daily(timeout=15)
        out["hf_daily"] = {"endpoint": HF_DAILY_ENDPOINT, "ok": ok,
                           "n_ids": (len(ids) if ids else 0), "error": err}
    rss_cfg = config.get("rss") or {}
    if rss_cfg.get("categories"):
        out["arxiv_rss"] = probe_rss(rss_cfg["categories"][:3], timeout=timeout, min_interval=mi)
    return out


def _selftest(config):
    q = config["queries"][0]["search_query"]
    mi = config.get("rate_limit_seconds", 3.0)
    print("[selftest] endpoint =", config.get("endpoint", ENDPOINT))
    print("[selftest] query    =", q)
    meta, entries = query_arxiv(q, max_results=3, min_interval=mi,
                                retries=config.get("retries", 2),
                                retry_backoff=config.get("retry_backoff_seconds", 20.0))
    print("[selftest] status=%s  content_type=%r  ok=%s  total_results=%s  entries=%d  attempts=%s"
          % (meta["status"], meta["content_type"], meta["ok"], meta["total_results"],
             len(entries), meta.get("attempts")))
    if meta.get("retries"):
        print("[selftest] retries:", "; ".join(meta["retries"]))
    if meta["error"]:
        print("[selftest] ERROR:", meta["error"])
    for e in entries:
        print("  - arXiv:%s%s | %s | published=%s updated=%s | primary=%s"
              % (e["arxiv_id"], e["version"], e["title"], e["published"], e["updated"], e["category"]))
        print("    abs=%s" % e["abs_url"])
    ok = bool(meta["ok"] and len(entries) >= 1
              and all(e["arxiv_id"] and e["title"] and e["published"] for e in entries))
    print("[selftest] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="arXiv 论文取数（research 线）")
    ap.add_argument("--config", default=str(DEFAULT_CONFIG))
    ap.add_argument("--selftest", action="store_true", help="单点自测（端点/Content-Type/解析）")
    ap.add_argument("--probe", action="store_true", help="R1′：复现取源可达性（arXiv 主源 / HF 副源 / RSS）")
    ap.add_argument("--fetch", action="store_true", help="跑 queries.json 全部查询（默认动作）")
    ap.add_argument("--query", help="临时单条 search_query（配合 --max-results）")
    ap.add_argument("--max-results", type=int, default=None)
    ap.add_argument("--window-hours", type=float, default=None)
    ap.add_argument("--seen", help="SEEN.md 路径：过滤已收录 arXiv ID")
    ap.add_argument("--limit", type=int, default=None, help="输出条目上限")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出")
    ap.add_argument("--out", help="把 JSON 结果写入文件")
    args = ap.parse_args(argv)

    config = load_config(args.config)

    if args.selftest:
        return _selftest(config)

    if args.probe:
        ev = probe_sources(config)
        if args.out:
            Path(args.out).write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        if args.json:
            print(json.dumps(ev, ensure_ascii=False, indent=2))
        else:
            print(_fmt_probe(ev))
        return 0 if (ev.get("arxiv_api") or {}).get("ok") else 1

    if args.query:
        meta, entries = query_arxiv(
            args.query, max_results=args.max_results or 10,
            min_interval=config.get("rate_limit_seconds", 3.0),
            timeout=config.get("timeout_seconds", 30),
            retries=config.get("retries", 2),
            retry_backoff=config.get("retry_backoff_seconds", 20.0),
        )
        res = {"items": entries, "meta": {
            "generated": _now_utc().isoformat(), "endpoint": ENDPOINT,
            "window_hours": args.window_hours if args.window_hours is not None else "n/a",
            "n_queries": 1, "n_kept": len(entries), "n_dropped": 0,
            "per_query": [meta], "dropped": []}}
        if args.limit:
            res["items"] = res["items"][:args.limit]
        if args.out:
            Path(args.out).write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(_fmt_human(res))
        return 0 if meta["ok"] else 1

    seen = _load_seen_ids(args.seen) if args.seen else set()
    res = fetch_all(config, window_hours=args.window_hours, seen_ids=seen,
                    max_results=args.max_results)
    if args.limit:
        res["items"] = res["items"][:args.limit]
    if args.out:
        Path(args.out).write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(_fmt_human(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())