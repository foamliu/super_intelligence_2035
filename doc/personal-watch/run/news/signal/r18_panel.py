#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
news/signal/r18_panel.py — R18（2026-10-22 15:00 轮）**只读盘面统计**

⚠️ 定位：**不是新研究、不是新统计检验**。只做两件既有日报 §2.1 里做过的事：
  ① 主交易历（A股个股日线并集）上「最新交易日」三类资产的涨跌家数 / 中位数 / 均幅；
  ② 本周一 ~ 最新交易日的**累计涨跌幅**（逐日涨跌幅连乘，口径与 §2.1 同源）。
🚫 不做：滞后相关重算、不换窗口、不换资产、不加检验 ⇒ **不构成任何结论**。
🚫 措辞红线：只写「涨/跌/中位数」，🚫 不写「影响/导致/利好/利空/冲击」，🚫 不写点位预测/仓位/择时。
✅ 本脚本**只读** `prices/*.json`，不写盘（输出到 stdout）。
"""
from __future__ import annotations

import glob
import json
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
PRICES = os.path.join(HERE, "prices")


def load():
    out = []
    for p in sorted(glob.glob(os.path.join(PRICES, "*.json"))):
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        rows = [(r[0], float(r[1])) for r in d.get("rows", []) if r and r[1] is not None]
        if not rows:
            continue
        out.append({"code": d.get("code"), "name": d.get("name"), "kind": d.get("kind"), "rows": rows})
    return out


def main() -> int:
    A = load()
    cal = sorted({d for a in A if a["kind"] == "stock" for d, _ in a["rows"]})
    if not cal:
        print("EMPTY calendar")
        return 1
    last = cal[-1]
    prev = cal[-2]
    print(f"assets={len(A)} last_cal={last} prev_cal={prev}")

    by_kind = {}
    na = 0
    for a in A:
        m = dict(a["rows"])
        if last not in m:
            na += 1
            continue
        p_last = m[last]
        # 上一有效价（主历前一日；缺失即跳过，🚫 不插值）
        p_prev = m.get(prev)
        if not p_prev:
            continue
        r1 = (p_last / p_prev - 1.0) * 100
        # 本周（该资产自身最近 5 个交易日内首日）累计
        ds = [d for d in cal if d in m and d <= last][-5:]
        r5 = (p_last / m[ds[0]] - 1.0) * 100 if len(ds) >= 2 else None
        by_kind.setdefault(a["kind"], []).append({"code": a["code"], "name": a["name"], "r1": r1, "r5": r5})

    for kind in ("stock", "fx", "fut"):
        L = by_kind.get(kind) or []
        if not L:
            print(f"[{kind}] n=0")
            continue
        up = sum(1 for x in L if x["r1"] > 0)
        dn = sum(1 for x in L if x["r1"] < 0)
        fl = sum(1 for x in L if x["r1"] == 0)
        med = st.median([x["r1"] for x in L])
        mean = sum(x["r1"] for x in L) / len(L)
        med5 = st.median([x["r5"] for x in L if x["r5"] is not None])
        print(f"[{kind}] n={len(L)} up={up} down={dn} flat={fl} "
              f"median1d={med:+.4f}% mean1d={mean:+.4f}% median_week={med5:+.4f}%")
        for x in sorted(L, key=lambda y: -y["r1"])[:3] + sorted(L, key=lambda y: y["r1"])[:3]:
            w = f"{x['r5']:+.2f}%" if x["r5"] is not None else "NA"
            print(f"    {x['code']} {x['name']}: 1d {x['r1']:+.2f}% | 本周 {w}")
    print(f"skipped(no row on {last})={na}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
