#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
news/signal/fetch_prices.py — 第11批(P0) 十年资产价格采集器
============================================================================
用途：为「新闻信号 → 资产价格 · 滞后相关/预测力」研究抓取 **2016–2026 日频收盘**。
规格：`run/NEWS_PRICE_SIGNAL_SPEC.md` §1（agent 只读）；本脚本只实现、不回改口径。

资产宇宙（38 标的 / 3 类；按用户 2026-10-07 晚修正：无指数/无海外/无债券）：
  * ① A股个股 21   → 腾讯 qfq 日K（**按年分页**，单次 n 有上限）
  * ② 汇率 10 vs RMB → 新浪外汇日K `cnyXXX`（1 CNY = X 外币）→ **取倒数** 得 `XXXCNY`
  * ③ 大宗商品 7    → 新浪国内期货日K `X0`（主力连续）
    ⚠️ 「南华商品指数」实测端点返回 null ⇒ 不可得；第 7 个改 `TA0` PTA（**替换关系已注明**）。

⚠️ 口径与 `news/policy/explore_l2.py` **一致**（同源 ifzq + qfq + 对数收益）——两套口径不许打架。
⚠️ 只读公开行情；限速 ≥1s；失败逐条如实报；🚫 不编造 / 不插值补造。

用法：
  python3 news/signal/fetch_prices.py                 # 增量取价（写盘）
  python3 news/signal/fetch_prices.py --refetch       # 强制全量重取
  python3 news/signal/fetch_prices.py --check         # 只打印实测表（HTTP/CT/首末/行数），不写盘
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
import urllib.request
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))      # news/signal
PRICE_DIR = os.path.join(HERE, "prices")

UA = "Mozilla/5.0 (compatible; PersonalWatch/1.0)"
START = "2016-01-01"
END = "2026-10-08"          # 区间末 = 采集日（规格 §1.1「能取到的最晚为准」）
RATE = 1.0          # 限速（秒）
RETRY = 3
TIMEOUT = 30

TENCENT = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
SINA_FX = ("https://vip.stock.finance.sina.com.cn/forex/api/jsonp.php/"
           "var%20_{sym}=/NewForexService.getDayKLine?symbol={sym}")
SINA_FUT = ("https://stock2.finance.sina.com.cn/futures/api/jsonp.php/"
            "var%20_{sym}=/InnerFuturesNewService.getDailyKLine?symbol={sym}")

# ── 资产宇宙（预注册 §2；跑前写死）─────────────────────────────────────────────
STOCKS = [
    ("sz000977", "浪潮信息", "算力/服务器"), ("sh603019", "中科曙光", "算力/服务器"),
    ("sh601138", "工业富联", "算力/服务器"),
    ("sh688256", "寒武纪", "半导体/设备"), ("sh688041", "海光信息", "半导体/设备"),
    ("sh688981", "中芯国际", "半导体/设备"), ("sz002371", "北方华创", "半导体/设备"),
    ("sh688012", "中微公司", "半导体/设备"), ("sh603986", "兆易创新", "半导体/设备"),
    ("sz300308", "中际旭创", "光模块/PCB"), ("sz300502", "新易盛", "光模块/PCB"),
    ("sz002463", "沪电股份", "光模块/PCB"),
    ("sz002230", "科大讯飞", "软件/大模型"), ("sh601360", "三六零", "软件/大模型"),
    ("sh688111", "金山办公", "软件/大模型"),
    ("sz300124", "汇川技术", "机器人/自动化"), ("sz002747", "埃斯顿", "机器人/自动化"),
    ("sz002475", "立讯精密", "消费电子"), ("sz002241", "歌尔股份", "消费电子"),
    ("sz300750", "宁德时代", "非科技对照"), ("sz002594", "比亚迪", "非科技对照"),
]
# 汇率：报告资产 = XXXCNY（1 外币 = X 人民币）；源 = cnyXXX（取倒数）
FX = [
    ("USDCNY", "美元", "cnyusd"), ("EURCNY", "欧元", "cnyeur"),
    ("JPYCNY", "日元", "cnyjpy"), ("GBPCNY", "英镑", "cnygbp"),
    ("HKDCNY", "港币", "cnyhkd"), ("AUDCNY", "澳元", "cnyaud"),
    ("CADCNY", "加元", "cnycad"), ("CHFCNY", "瑞郎", "cnychf"),
    ("SGDCNY", "新元", "cnysgd"), ("NZDCNY", "新西兰元", "cnynzd"),
]
FUT = [
    ("AU0", "沪金", "贵金属"), ("SC0", "原油(INE)", "能源"), ("CU0", "沪铜", "有色"),
    ("RB0", "螺纹钢", "黑色"), ("I0", "铁矿石", "黑色"), ("M0", "豆粕", "农产品"),
    ("TA0", "PTA", "化工"),   # ⚠️ 替换「南华商品指数」（不可得）——见 SOURCE_TEST.md
]


def log(msg: str) -> None:
    print(msg, flush=True)


def http_get(url: str):
    """返回 (body_bytes, status, content_type)。带重试。"""
    last = None
    for i in range(RETRY):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA,
                                                       "Referer": "https://finance.sina.com.cn/"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return r.read(), getattr(r, "status", 200), r.headers.get("Content-Type", "")
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(1.5 * (i + 1))
    raise last


# ── 解析器 ───────────────────────────────────────────────────────────────────
def parse_tencent(body: bytes):
    """腾讯 qfq 日K → [(date, close)]。"""
    obj = json.loads(body.decode("utf-8", "replace"))
    data = obj.get("data") or {}
    out = []
    for _code, node in data.items():
        rows = node.get("qfqday") or node.get("day") or []
        for r in rows:
            out.append((r[0], float(r[2])))     # [date, open, close, high, low, vol]
    return out


def parse_sina_fx(body: bytes):
    """新浪外汇 jsonp → [(date, close_of_cnyXXX)]（1 CNY = X 外币）。"""
    txt = body.decode("utf-8", "replace")
    a, b = txt.find("=("), txt.rfind(")")
    inner = txt[a + 2:b]
    out = []
    for seg in inner.split("|"):
        seg = seg.strip().strip('"')
        if not seg:
            continue
        parts = [p for p in seg.split(",") if p != ""]
        if len(parts) < 2:
            continue
        try:
            out.append((parts[0], float(parts[-1])))   # last field = close
        except ValueError:
            continue
    return out


def parse_sina_fut(body: bytes):
    """新浪国内期货 jsonp → [(date, close)]。"""
    txt = body.decode("utf-8", "replace")
    a, b = txt.find("=("), txt.rfind(")")
    # body = "/*<script>…*/ var _X=([{...}])" ⇒ '[' 位于 a+2（修复 2026-10-07 R1）
    arr = json.loads(txt[a + 2:b])
    return [(r["d"], float(r["c"])) for r in arr if r.get("c") not in (None, "")]


# ── 抓取（分类）─────────────────────────────────────────────────────────────
# ⚠️ 端点实测（2026-10-08 晚报轮）：腾讯 `fqkline` **缓存不一致** —— **同一 `param`
#    会被负载均衡到不同后端，部分后端缺「当日 bar」**（实测同一 code 同区间：
#    `count=100/350` 返回到 2026-10-08，而 `count=200/400` 只到 2026-09-30）。
#    ⇒ 对**最后一年**用「多 count 轮询、取末日最大」，直到末日 = 请求末日为止。
STOCK_COUNTS = (400, 350, 300, 250, 200, 150, 100, 60, 30)


def _stock_slice(code: str, s: str, e: str, count: int):
    url = f"{TENCENT}?param={code},day,{s},{e},{count},qfq"
    body, st, ct = http_get(url)
    return parse_tencent(body), (st, ct)


def fetch_stock(code: str, since: str, until: str):
    """腾讯按年分页（单次 count 有上限）。返回 (rows, [meta...])。
    末年起改用 `STOCK_COUNTS` 轮询（见上方缓存不一致说明）。"""
    rows, metas = [], []
    y0, y1 = int(since[:4]), int(until[:4])
    for y in range(y0, y1 + 1):
        s = max(f"{y}-01-01", since)
        e = min(f"{y}-12-31", until)
        counts = STOCK_COUNTS if y == y1 else (400,)
        best, best_meta = [], None
        for c in counts:
            try:
                got, (st, ct) = _stock_slice(code, s, e, c)
            except Exception as exc:  # noqa: BLE001
                best_meta = best_meta or (f"{s}~{e}", "ERR", str(exc)[:60], 0)
                continue
            if got and (not best or got[-1][0] > best[-1][0]):
                best, best_meta = got, (f"{s}~{e}", st, ct, len(got))
            time.sleep(RATE)
            if best and best[-1][0] >= e:      # 已取到请求末日
                break
        rows.extend(best)
        metas.append(best_meta or (f"{s}~{e}", "ERR", "empty", 0))
    return rows, metas


def fetch_fx(sym: str, since: str, until: str):
    url = SINA_FX.format(sym=sym)
    body, st, ct = http_get(url)
    raw = parse_sina_fx(body)                    # (date, cnyXXX_close)
    rows = [(d, 1.0 / v) for d, v in raw if v]   # → XXXCNY（1 外币 = X 人民币）
    rows = [(d, v) for d, v in rows if since <= d <= until]
    time.sleep(RATE)
    return rows, [("full", st, ct, len(rows))]


def fetch_fut(sym: str, since: str, until: str):
    url = SINA_FUT.format(sym=sym)
    body, st, ct = http_get(url)
    raw = parse_sina_fut(body)
    rows = [(d, v) for d, v in raw if since <= d <= until]
    time.sleep(RATE)
    return rows, [("full", st, ct, len(rows))]


def dedup_sort(rows):
    seen = {}
    for d, v in rows:
        seen[d] = v
    return sorted(seen.items())


def sha16(rows) -> str:
    h = hashlib.sha256()
    for d, v in rows:
        h.update(f"{d},{v:.6f};".encode())
    return h.hexdigest()[:16]



def save(code, name, kind, source, quote_dir, derivation, rows, metas):
    os.makedirs(PRICE_DIR, exist_ok=True)
    rec = {
        "code": code, "name": name, "kind": kind, "source": source,
        "quote_dir": quote_dir, "derivation": derivation,
        "rows": [[d, v] for d, v in rows],
        "n": len(rows), "first": rows[0][0] if rows else None,
        "last": rows[-1][0] if rows else None, "sha16": sha16(rows),
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "requests": metas,
        "note": "",
    }
    path = os.path.join(PRICE_DIR, f"{code}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False)
    return rec


def write_source_test(table):
    path = os.path.join(HERE, "SOURCE_TEST.md")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# SOURCE_TEST — 价格源实测表（第11批 · R1）",
        "",
        f"> 生成：{ts}（`fetch_prices.py`；运行机 = 本仓库所在机 · 中国网络）",
        "> 列：类别 / code / 名称 / HTTP / Content-Type / 首日 / 末日 / 行数。**含失败项**。",
        "",
        "| 类别 | code | 名称 | HTTP | Content-Type | 首日 | 末日 | 行数 |",
        "|:--|:--|:--|:--|:--|:--|:--|--:|",
    ]
    for kind, code, name, st, ct, first, last, n in table:
        lines.append(f"| {kind} | `{code}` | {name} | {st} | {ct} | {first} | {last} | {n} |")
    lines += [
        "",
        "## 端点结论（实测）",
        "- ✅ **A股个股**：腾讯 `web.ifzq.gtimg.cn/appstock/app/fqkline/get`（`qfq`）—— **按年分页**（单次 count 有上限，`3000`→`param error`）。",
        "- ✅ **汇率**：新浪 `NewForexService.getDayKLine`（源 `cnyXXX`）—— 全历史约 2014-11 起（USD/JPY 更早）。",
        "- ✅ **大宗商品**：新浪 `InnerFuturesNewService.getDailyKLine`（`X0` 主力连续）。",
        "- ❌ **腾讯外汇 / 期货** `fqkline?param=fx_* / nf_*` → `param error`（不可用）。",
        "- ❌ **南华商品指数** `NH` / `NHCI`（含 `GlobalFuturesService`）→ 返回 `null`（**本类不可得**）⇒ 第 7 个大宗改 **`TA0` PTA**（替换关系已注明）。",
        "- ❌ **东财** `push2his.eastmoney.com` → 运行机 TLS 被重置（不试不用）。",
        "",
        "> ⚠️ 复现：`python3 news/signal/fetch_prices.py --check --refetch`（限速 ≥1s）。",
        "",
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    log(f"[write] {path}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=START)
    ap.add_argument("--until", default=END)
    ap.add_argument("--refetch", action="store_true", help="强制全量重取（忽略缓存）")
    ap.add_argument("--check", action="store_true", help="只打印实测表，不写盘")
    args = ap.parse_args()

    tasks = ([("stock", c, n, g) for c, n, g in STOCKS]
             + [("fx", c, n, s) for c, n, s in FX]
             + [("fut", c, n, s) for c, n, s in FUT])

    log(f"=== fetch_prices · {len(tasks)} 标的 · {args.since}~{args.until} "
        f"· check={args.check} refetch={args.refetch} ===")

    table, ok, fail = [], 0, 0
    for kind, code, name, key in tasks:
        try:
            # ⚠️ 符号口径（修复 bug 2026-10-07 R1）：
            #   stock/fut 的第 3 字段 = 展示分组（非符号）⇒ 取符号用 code；
            #   fx 的第 3 字段 = 源符号（cnyXXX）⇒ 取符号用 key。
            sym = key if kind == "fx" else code
            if kind == "stock":
                rows, metas = fetch_stock(sym, args.since, args.until)
                source = "tencent.ifzq.fqkline(qfq,按年分页)"
                qd, deriv = "CNY/股", ""
            elif kind == "fx":
                rows, metas = fetch_fx(sym, args.since, args.until)
                source = "sina.NewForexService.getDayKLine"
                qd, deriv = "1外币=X人民币", f"1/{key}"
            else:
                rows, metas = fetch_fut(sym, args.since, args.until)
                source = "sina.InnerFuturesNewService.getDailyKLine"
                qd, deriv = "元/吨(或合约口径)", ""
            rows = dedup_sort(rows)
            req0 = metas[0]
            st = "200" if req0[1] == 200 else str(req0[1])
            ct = (req0[2] or "")[:28]
            first = rows[0][0] if rows else "-"
            last = rows[-1][0] if rows else "-"
            if args.check:
                log(f"[{kind:5}] {code:9} {name:8} HTTP={st:4} CT={ct:28} "
                    f"n={len(rows):5} {first:10}~{last:10}")
            else:
                rec = save(code, name, kind, source, qd, deriv, rows, metas)
                log(f"[{kind:5}] {code:9} {name:8} OK n={rec['n']:5} "
                    f"{rec['first']}~{rec['last']} sha16={rec['sha16']}")
            table.append((kind, code, name, st, ct, first, last, len(rows)))
            ok += 1
        except Exception as e:  # noqa: BLE001
            fail += 1
            log(f"[{kind:5}] {code:9} {name:8} FAIL: {str(e)[:80]}")
            table.append((kind, code, name, "ERR", str(e)[:40], "-", "-", 0))

    log(f"=== done: ok={ok} fail={fail} ===")
    if not args.check:
        write_source_test(table)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

