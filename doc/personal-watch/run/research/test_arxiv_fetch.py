#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_arxiv_fetch · `arxiv_fetch.py` 的**离线**校验（**不联网**）
================================================================
把 R1 铁律变成**可回归**的断言（不依赖 arXiv 可用性 / 限流，可随时复跑）：
  1. Atom 解析：`id` / `version` / `published` / `updated` / `primary_category` / `link(alternate+pdf)`
  2. **`200 != 有料`**：HTTP 200 + `text/html` → 判 **FAIL**（并带原因）
  3. **空 feed** → 判 **FAIL**（不得当成"无新增"）
  4. **429/503 → 有界退避重试**：重试后成功则 ok；重试耗尽则 FAIL 且记录 `attempts`
  5. 新鲜度窗口：过期 → 丢弃；解析不到日期 → 丢弃
  6. `_fmt_human()` 对「多查询 meta」与「单查询 meta」两种形状都**不崩**（回归曾崩的路径）
  7. CLI `--query --out`：落盘 JSON（含完整 meta）+ 退出码 0（网络层被 stub）

用法：`python3 research/test_arxiv_fetch.py`   # 全 PASS 退出码 0
"""
import contextlib
import io
import json
import os
import sys
import tempfile
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import arxiv_fetch as af  # noqa: E402

XML_CT = "application/atom+xml; charset=utf-8"

SAMPLE = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom" xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">
  <opensearch:totalResults>2</opensearch:totalResults>
  <entry>
    <id>http://arxiv.org/abs/2610.09999v1</id>
    <updated>2026-10-01T12:00:00Z</updated>
    <published>2026-10-01T12:00:00Z</published>
    <title>Test Paper Alpha</title>
    <summary>Alpha abstract.</summary>
    <author><name>Alice A</name></author>
    <author><name>Bob B</name></author>
    <link href="https://arxiv.org/abs/2610.09999v1" rel="alternate" type="text/html"/>
    <link href="https://arxiv.org/pdf/2610.09999v1" rel="related" title="pdf" type="application/pdf"/>
    <arxiv:primary_category term="cs.CL"/>
    <category term="cs.CL"/>
    <category term="cs.AI"/>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/2610.09998v2</id>
    <updated>2026-10-01T13:00:00Z</updated>
    <published>2026-09-30T08:00:00Z</published>
    <title>Test Paper Beta</title>
    <summary>Beta abstract.</summary>
    <author><name>Carol C</name></author>
    <link href="https://arxiv.org/abs/2610.09998v2" rel="alternate" type="text/html"/>
    <link href="https://arxiv.org/pdf/2610.09998v2" rel="related" title="pdf" type="application/pdf"/>
    <arxiv:primary_category term="cs.CV"/>
    <category term="cs.CV"/>
  </entry>
</feed>
"""

EMPTY = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">
  <opensearch:totalResults>0</opensearch:totalResults>
</feed>
"""

_RESULTS = []


def check(name, cond, extra=""):
    _RESULTS.append((name, bool(cond)))
    print("[%s] %s%s" % ("PASS" if cond else "FAIL", name, (" — %s" % extra) if extra else ""))


class _Stub:
    """按顺序返回预置 (status, ctype, body)；用尽后重复最后一项。"""

    def __init__(self, seq):
        self.seq = list(seq)
        self.calls = 0

    def __call__(self, url, params, timeout):
        self.calls += 1
        return self.seq[min(self.calls - 1, len(self.seq) - 1)]


def test_parse():
    total, entries = af._parse_feed(SAMPLE)
    check("parse.total==2", total == 2)
    check("parse.n==2", len(entries) == 2)
    e = entries[0]
    check("parse.id", e["arxiv_id"] == "2610.09999")
    check("parse.version", e["version"] == "v1")
    check("parse.primary", e["category"] == "cs.CL")
    check("parse.published", e["published"] == "2026-10-01T12:00:00Z")
    check("parse.updated", e["updated"] == "2026-10-01T12:00:00Z")
    check("parse.abs/pdf",
          e["abs_url"].endswith("/abs/2610.09999v1") and e["pdf_url"].endswith("/pdf/2610.09999v1"))
    check("parse.authors", e["authors"] == ["Alice A", "Bob B"])


def test_200_html_is_failure():
    af._http_get = _Stub([(200, "text/html; charset=utf-8", "<html>portal</html>")])
    meta, entries = af.query_arxiv("cat:cs.CL", retries=0, min_interval=0.0)
    check("html200.ok==False", meta["ok"] is False)
    check("html200.error", "200 != 有料" in (meta["error"] or ""))
    check("html200.no_entries", entries == [])


def test_empty_feed_is_failure():
    af._http_get = _Stub([(200, XML_CT, EMPTY)])
    meta, entries = af.query_arxiv("cat:cs.CL", retries=0, min_interval=0.0)
    check("empty.ok==False", meta["ok"] is False)
    check("empty.error", "empty feed" in (meta["error"] or ""))


def test_retry_on_429_then_ok():
    stub = _Stub([(429, "text/html", "too many"), (200, XML_CT, SAMPLE)])
    af._http_get = stub
    meta, entries = af.query_arxiv("cat:cs.CL", retries=2, retry_backoff=0.0, min_interval=0.0)
    check("429.ok", meta["ok"] is True and len(entries) == 2)
    check("429.attempts==2", meta["attempts"] == 2)
    check("429.retry_logged", len(meta["retries"]) == 1)
    check("429.calls==2", stub.calls == 2)


def test_retry_exhausted():
    af._http_get = _Stub([(503, "text/html", "unavailable")])
    meta, entries = af.query_arxiv("cat:cs.CL", retries=2, retry_backoff=0.0, min_interval=0.0)
    check("503.ok==False", meta["ok"] is False)
    check("503.attempts==3", meta["attempts"] == 3)
    check("503.error", "HTTP 503" in (meta["error"] or ""))


def test_window():
    now = datetime(2026, 10, 3, 12, 0, 0, tzinfo=timezone.utc)
    fresh = {"published": "2026-10-03T10:00:00Z", "updated": "2026-10-03T10:00:00Z"}
    stale = {"published": "2026-09-01T10:00:00Z", "updated": "2026-09-01T10:00:00Z"}
    bad = {"published": "", "updated": "nope"}
    check("window.fresh", af._within_window(fresh, 72, now)[0] is True)
    check("window.stale", af._within_window(stale, 72, now)[0] is False)
    check("window.no_date", af._within_window(bad, 72, now)[0] is False)


def test_fmt_human_shapes():
    af._http_get = _Stub([(200, XML_CT, SAMPLE)])
    meta, entries = af.query_arxiv("cat:cs.CL", retries=0, min_interval=0.0)
    # 单查询形状（无 name/kept；window_hours 为 "n/a"）—— 曾崩
    single = {"items": entries, "meta": {
        "generated": "x", "endpoint": af.ENDPOINT, "window_hours": "n/a",
        "n_queries": 1, "n_kept": len(entries), "n_dropped": 0,
        "per_query": [meta], "dropped": []}}
    try:
        txt = af._fmt_human(single)
        ok, msg = ("Test Paper Alpha" in txt), ("" if "Test Paper Alpha" in txt else txt[:80])
    except Exception as exc:  # noqa: BLE001
        ok, msg = False, repr(exc)
    check("fmt.single_shape", ok, msg)
    # 多查询形状（有 name/kept/dropped；window_hours 为数字）
    meta2 = dict(meta)
    meta2.update({"name": "llm-x", "kept": 1, "area": "LLM"})
    multi = {"items": entries, "meta": {
        "generated": "x", "endpoint": af.ENDPOINT, "window_hours": 72, "n_queries": 1,
        "n_kept": 1, "n_dropped": 1, "per_query": [meta2],
        "dropped": [("2610.00001", "stale", "llm-x")]}}
    try:
        txt = af._fmt_human(multi)
        ok = ("llm-x" in txt) and ("窗口<=72h" in txt)
        msg = "" if ok else txt[:80]
    except Exception as exc:  # noqa: BLE001
        ok, msg = False, repr(exc)
    check("fmt.multi_shape", ok, msg)


def test_cli_query_out():
    af._http_get = _Stub([(200, XML_CT, SAMPLE)])
    buf = io.StringIO()
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "one.json")
        with contextlib.redirect_stdout(buf):
            rc = af.main(["--query", "cat:cs.CL", "--max-results", "2", "--out", out])
        ok_file = os.path.exists(out)
        data = json.load(open(out, encoding="utf-8")) if ok_file else {}
    check("cli.rc==0", rc == 0)
    check("cli.out_written", ok_file)
    check("cli.items==2", len(data.get("items", [])) == 2)
    check("cli.meta_full",
          {"generated", "endpoint", "window_hours", "per_query"} <= set(data.get("meta", {}).keys()))
    check("cli.human_printed", "Test Paper Alpha" in buf.getvalue())


def main():
    tests = [test_parse, test_200_html_is_failure, test_empty_feed_is_failure,
             test_retry_on_429_then_ok, test_retry_exhausted, test_window,
             test_fmt_human_shapes, test_cli_query_out]
    for t in tests:
        af._LAST_CALL[0] = 0.0  # 重置限速状态，避免测试间互相 sleep
        print("── %s ──" % t.__name__)
        t()
    n = len(_RESULTS)
    f = sum(1 for _, ok in _RESULTS if not ok)
    print("\n[test_arxiv_fetch] %d/%d PASS" % (n - f, n))
    print("[test_arxiv_fetch] RESULT:", "PASS" if f == 0 else "FAIL")
    return 0 if f == 0 else 1


if __name__ == "__main__":
    sys.exit(main())