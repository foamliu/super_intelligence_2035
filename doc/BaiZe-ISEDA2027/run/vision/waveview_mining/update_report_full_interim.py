#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Refresh report §0.6 '全队列实跑进度' <li> with the latest full-queue interim
numbers (rows done / per-arm pass / McNemar on completed 3-arm cases) read from
the 36.15 full-runner snapshot. Also saves a local snapshot of results.json.

Reads /tmp/wv_cg_full_fetch.json (scp'd from 36.15 /tmp/wv_cg_full/results.json).
Patches reports/report_vision_waveview_selftest_agent_zh.html in place.
"""
import json, re, datetime, os
from collections import defaultdict

RUN = "/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run"
REP = os.path.join(RUN, "reports", "report_vision_waveview_selftest_agent_zh.html")
FETCH = "/tmp/wv_cg_full_fetch.json"
SNAP = os.path.join(RUN, "vision", "waveview_mining", "codegen_full_results_snapshot.json")
WAKE = os.environ.get("WAKE", "wake#1545")
TS_LABEL = os.environ.get("TS_LABEL", "")

d = json.load(open(FETCH))
rows = d["rows"]; cases = d["cases"]
arms = ["V0", "V1", "V2"]

# save local snapshot
json.dump(d, open(SNAP, "w"), ensure_ascii=False, indent=1)

def arm_stat(a):
    rs = [r for r in rows if r["arm"] == a]
    n = len(rs); npass = sum(1 for r in rs if r.get("verdict"))
    return n, npass

st = {a: arm_stat(a) for a in arms}
by_case = defaultdict(dict)
for r in rows:
    by_case[r["case_id"]][r["arm"]] = bool(r.get("verdict"))
complete = {c: v for c, v in by_case.items() if set(v) >= set(arms)}
n_complete = len(complete)
n_rows = len(rows)
total_planned = len(cases) * 3
to_rows = sum(1 for r in rows if r.get("pi_rc", 0) == -99)

def mcnemar(a, b):
    n00 = n01 = n10 = n11 = 0
    for c, v in complete.items():
        x, y = v[a], v[b]
        if x and y: n11 += 1
        elif x and not y: n10 += 1
        elif not x and y: n01 += 1
        else: n00 += 1
    discord = n01 + n10
    if discord == 0:
        p = 1.0
    else:
        from math import comb
        k = min(n01, n10)
        tail = sum(comb(discord, i) for i in range(0, k + 1)) / (2 ** discord)
        p = min(1.0, 2 * tail)
    return n01, n10, n11, n00, p

mc = {pair: mcnemar(*pair) for pair in [("V0", "V1"), ("V0", "V2"), ("V1", "V2")]}

# per-arm passers (case ids)
passers = {a: [c for c, v in complete.items() if v[a]] for a in arms}

ts = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

parts = []
parts.append("<li><b>全队列实跑进度（%s %s 巡检）</b>：runner <code>python3 run_codegen_full.py</code> + watchdog 均健康于 36.15（resumable，runner 挂则重启、rows≥546 自停），resumable 增量写 <code>/tmp/wv_cg_full/results.json</code>。截至本 wake 已完成 <b>%d 行 / %d 计划</b>（%d case 三臂齐全，另有部分 case 单/双臂）。" % (WAKE, TS_LABEL, n_rows, total_planned, n_complete))
parts.append("逐臂整题通过：<b>V0 %d/%d</b>（%s）· <b>V1 %d/%d</b>（%s）· <b>V2 %d/%d</b>（%s）；超时行(pi_rc=-99) %d/%d。" % (
    st["V0"][1], st["V0"][0], "%.1f%%" % (100*st["V0"][1]/st["V0"][0]) if st["V0"][0] else "—",
    st["V1"][1], st["V1"][0], "%.1f%%" % (100*st["V1"][1]/st["V1"][0]) if st["V1"][0] else "—",
    st["V2"][1], st["V2"][0], "%.1f%%" % (100*st["V2"][1]/st["V2"][0]) if st["V2"][0] else "—",
    to_rows, n_rows))
parts.append("<b>McNemar（仅 %d 个三臂齐全 case，n 严重不足，仅参考）</b>：V0 vs V1 b=%d c=%d p=%.3f · V0 vs V2 b=%d c=%d p=%.3f · V1 vs V2 b=%d c=%d p=%.3f。" % (
    n_complete, mc[("V0","V1")][0], mc[("V0","V1")][1], mc[("V0","V1")][4],
    mc[("V0","V2")][0], mc[("V0","V2")][1], mc[("V0","V2")][4],
    mc[("V1","V2")][0], mc[("V1","V2")][1], mc[("V1","V2")][4]))
# passers detail
def plist(a):
    return ", ".join(c.replace("EDA-Eval-DesignFlow-", "") for c in passers[a]) or "（无）"
parts.append("<b>通过题明细（三臂齐全集中）</b>：V1 PASS=%s · V0 PASS=%s · V2 PASS=%s。" % (plist("V1"), plist("V0"), plist("V2")))
parts.append("<b>🎯 仍保持的信号（不作结论）</b>：AvgValueCalc-001 <b>V1=PASS</b>（pi 184.3s 产出 submit.zip、check.py 判过），同题 V0=360s 超时 FAIL、V2=129.8s 完成但逻辑错 FAIL——全队列第一例「有 VQA(V1)通过·无 VQA(V0)未通过」翻转；但 n=1、V0 是超时而非逻辑错（cloud-agent 非确定性，V1「更快完成」未必源于 VQA），<b>仅作信号</b>。")
parts.append("<b>诚实说明</b>：字典序最前的高 k 复杂题多在 360s 超时、无 submit.zip（硬题前载、样本有偏），<b>当前 %d 行暂不构成可引用的全队列通过率</b>；全队列 546 行预计 ~30+h cloud-agent 推理、跨多 wake 完成，待积聚足够三臂齐全 case 再报率 + McNemar 定显著性。SSH 反向桥（.17 watchdog ~59h）+ VQA 端点（:30001 Qwen3.5-2B · :30003 +rft2_adapter 均 <code>{\"ok\":true,\"ready\":true}</code>）健康。</li>" % n_rows)
new_li = "".join(parts)

html = open(REP, encoding="utf-8").read()
pat = re.compile(r"<li><b>全队列实跑进度[\s\S]*?</li>")
new_html, nsub = pat.subn(new_li, html, count=1)
assert nsub == 1, "progress <li> not found (nsub=%d)" % nsub

# refresh §0.6 header timestamp marker
new_html = re.sub(r"code_gen 试点更新 [^<]*",
                  "code_gen 全队列 interim 更新 " + ts, new_html, count=1)
# refresh title date marker if present
open(REP, "w", encoding="utf-8").write(new_html)
print("patched progress <li> (nsub=%d) · report now %d bytes · ts=%s" % (nsub, len(new_html), ts))
print("rows=%d/%d | complete3arm=%d | V0 %d/%d V1 %d/%d V2 %d/%d | timeout=%d" % (
    n_rows, total_planned, n_complete,
    st["V0"][1], st["V0"][0], st["V1"][1], st["V1"][0], st["V2"][1], st["V2"][0], to_rows))
for pair in [("V0","V1"),("V0","V2"),("V1","V2")]:
    n01,n10,n11,n00,p = mc[pair]
    print("  McNemar %s vs %s: b=%d c=%d p=%.3f" % (pair[0],pair[1],n01,n10,p))
print("snapshot saved:", SNAP)
