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
    qs = urllib.parse.urlencode(params)
    req = urllib.request.Request(url + "?" + qs, headers=HEADERS)
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
    p = _parse_dt(entry.get("published"))
    u = _parse_dt(entry.get("updated"))
    stamps = [d for d in (p, u) if d is not None]
    if not stamps:
        return False, "no parseable date"
    newest = max(stamps)
    age_h = (now - newest).total_seconds() / 3600.0
    if age_h <= window_hours:
        return True, "age %.1fh <= %dh" % (age_h, window_hours)
    return False, "stale %.1fh > %dh" % (age_h, window_hours)


def load_config(path=DEFAULT_CONFIG):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def fetch_all(config, window_hours=None, seen_ids=None, max_results=None):
    """跑 config['queries'] 全部查询 -> 去重 + 新鲜度过滤。返回 {"items": [...], "meta": {...}}。"""
    now = _now_utc()
    wh = window_hours if window_hours is not None else config.get("window_hours", 72)
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


def _load_seen_ids(path):
    ids = set()
    p = Path(path)
    if not p.exists():
        return ids
    for line in p.read_text(encoding="utf-8").splitlines():
        for m in re.finditer(r"\b([0-9]{4}\.[0-9]{4,5})\b", line):
            ids.add(m.group(1))
    return ids


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