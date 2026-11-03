#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""06_report_zh.py — 把 compare.json 生成中文 HTML 报告（自包含，0 script/0 外链）。"""
import argparse
import html
import json
import os
import sys
from datetime import datetime


def esc(s):
    return html.escape(str(s))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--compare", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    d = json.load(open(args.compare, encoding="utf-8"))

    h = []
    h.append("<!DOCTYPE html><html lang='zh'><head><meta charset='utf-8'>")
    h.append("<title>DesignFlow trace 语义预筛报告</title><style>")
    h.append("body{font-family:Segoe UI,Microsoft YaHei,sans-serif;max-width:980px;margin:24px auto;"
             "padding:0 16px;color:#222;line-height:1.6}h1{font-size:1.5rem;border-bottom:3px solid #2b6cb0;"
             "padding-bottom:8px}h2{font-size:1.15rem;color:#2b6cb0;margin-top:28px;border-left:5px solid #2b6cb0;"
             "padding-left:10px}table{border-collapse:collapse;width:100%;margin:10px 0;font-size:.9rem}"
             "th,td{border:1px solid #e2e8f0;padding:6px 8px;text-align:center}th{background:#edf2f7}"
             "td.l{text-align:left}.card{background:#f7fafc;border:1px solid #e2e8f0;border-radius:8px;padding:14px 18px;margin:12px 0}"
             ".warn{background:#fffbeb;border:1px solid #fbd38d;color:#744210}.ok{background:#f0fff4;border:1px solid #9ae6b4}"
             ".foot{color:#888;font-size:.8rem;margin-top:36px;border-top:1px solid #e2e8f0;padding-top:10px}</style></head><body>")
    h.append("<h1>DesignFlow trace 语义预筛（Qwen3.5-0.8B Q8_0 / llama.cpp）</h1>")
    h.append(f"<div class='card'>样本 <b>{d.get('n_total')}</b> 条；新候选池 <b>{d.get('pool_size')}</b> 条；"
             f"生成时间 {esc(datetime.now().strftime('%Y-%m-%d %H:%M'))}</div>")

    h.append("<h2>1. 分箱结果（mc vs 语义判定）</h2><table>"
             "<tr><th>mc 区间</th><th>样本</th><th>EDA 真</th><th>比例</th><th>平均置信度</th></tr>")
    for s in d.get("bins", []):
        h.append(f"<tr><td>{esc(s['bin'])}</td><td>{s['n']}</td><td>{s['eda_true']}</td>"
                 f"<td>{s['eda_rate']*100:.1f}%</td><td>{s['mean_conf']:.2f}</td></tr>")
    h.append("</table>")

    m = d.get("mc100", {})
    l = d.get("mc_lt100", {})
    h.append("<h2>2. 两个核心问题</h2>")
    if m.get("precision") is not None:
        h.append(f"<div class='card warn'><b>Q1：mc>=100 的候选里有多少不是真 EDA？</b><br>"
                 f"precision = <b>{m['precision']*100:.1f}%</b>（{m['eda_true']}/{m['n']}）"
                 f"⇒ 误命中约 <b>{(1-m['precision'])*100:.1f}%</b>。</div>")
    h.append(f"<div class='card ok'><b>Q2：mc<100 里找回了多少真 EDA？</b><br>"
             f"低 mc 样本 {l.get('n')} 条，其中语义判定为 EDA <b>{l.get('eda_true')}</b> 条。"
             f"这些就是被 mc 粗筛漏掉的候选。</div>")
    if l.get("recovered"):
        h.append("<table><tr><th>sid</th><th>mc</th><th>domain</th><th>task_type</th><th>conf</th></tr>")
        for r in l["recovered"][:20]:
            h.append(f"<tr><td>{esc(r['sid'])}</td><td>{r['mc']}</td><td>{esc(r['domain'])}</td>"
                     f"<td class='l'>{esc(r['task_type'])}</td><td>{r['conf']:.2f}</td></tr>")
        h.append("</table>")

    g = d.get("gold", {})
    h.append("<h2>3. 金标一致率</h2>")
    if g.get("n"):
        h.append(f"<div class='card'><b>{g['agreement']*100:.1f}%</b>（{g['n']} 条人工标签）；"
                 f"confusion = {esc(g['confusion'])}</div>")
    else:
        h.append("<div class='card warn'>未提供 gold.tsv，无法评估；上线前必须补 20 条人工标签。</div>")

    h.append("<h2>4. 域分布（is_eda=true）</h2><table><tr><th>domain</th><th>条数</th></tr>")
    for k, v in sorted(d.get("domain_dist", {}).items(), key=lambda kv: -kv[1]):
        h.append(f"<tr><td>{esc(k)}</td><td>{v}</td></tr>")
    h.append("</table>")

    h.append("<h2>5. 结论与限制</h2><div class='card warn'>")
    h.append("0.8B 结果只能用于 <b>triage / 候选排序</b>，不能作为「已确认 EDA case」。"
             "正式 case 仍需 deepread + 实跑验证。若金标一致率 &lt; 80%，需先调 prompt/few-shot 再上线。")
    h.append("</div>")
    h.append("<div class='foot'>生成器：<code>06_report_zh.py</code>；数据：<code>compare.json</code>；"
             "模型：Qwen3.5-0.8B Q8_0（llama.cpp）。</div></body></html>")

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(h))
    print(f"[report] {args.out} ({os.path.getsize(args.out)} B)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
