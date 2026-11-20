#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate Chinese self-contained HTML RCA report for MiniCPM5-2B SFT step105 baseline
on EDA-Eval-PyAether (158), 5-run mean Pass@1 = 3.04%. Inline SVG pie, 0 external links."""
import json, collections, math, html, os

DATA = json.load(open("/tmp/rca_baseline_enriched.json"))
tasks = DATA["tasks"]
OUT = "/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports/report_posttrain_baseline_pyaether_rca_zh.html"

# ---------- aggregates ----------
per_run_count = [6, 3, 4, 5, 6]
per_run_rate = [r/158*100 for r in per_run_count]
mean = DATA["mean"]; std = DATA["std"]
union_pass = sorted([t for t, r in tasks.items() if r["pass_count"] > 0],
                    key=lambda x: int(x.split("-")[-1]))

# per (task,run) 7-bucket root-cause counts (790 samples)
prc = DATA["per_run_cat"]
# regroup into 7 root-cause buckets
buckets = collections.OrderedDict()
buckets["C5"] = {"name": "⑤ 推理/规划", "count": prc.get("C5_degenerate_pass", 0) + prc.get("C4_gen_fail_other", 0),
                 "desc": "代码生成阶段未产出有效 .py 文件（模型幻觉 submit_and_exit verified=true 即放弃）"}
# C3 excludes the 54 AttributeError (carved out into C2). C3_code_runtime(122) = 54 AttributeError + 68 TypeError/NameError/...
buckets["C3"] = {"name": "③ 代码语义", "count": prc.get("C3_code_syntax", 0) + (prc.get("C3_code_runtime", 0) - 54) + prc.get("C3_code_assert", 0) + prc.get("C3_code_other", 0) + prc.get("C7_other", 0),
                 "desc": "产出了代码但执行失败：语法错 / 类型/参数错 / 断言失败（54 个 API属性幻觉已单列②）"}
buckets["C2"] = {"name": "② 工具调用/协议", "count": 54,
                 "desc": "调用不存在的 API/属性（AttributeError 'module has no attribute'），API 名称幻觉"}
buckets["C6"] = {"name": "⑥ 超时/预算", "count": prc.get("C6_timeout", 0),
                 "desc": "代码生成超过 2500s 预算被杀"}
buckets["C1"] = {"name": "① 环境/依赖", "count": prc.get("C1_env_import", 0),
                 "desc": "ModuleNotFoundError / ImportError（pyAether 子模块路径错）"}
buckets["PASS"] = {"name": "✓ 通过", "count": prc.get("PASS", 0),
                   "desc": "执行通过断言测试"}
# C3 sub-split
c3_sub = {
    "语法 (SyntaxError/IndentationError)": prc.get("C3_code_syntax", 0),
    "运行时 (TypeError/NameError/KeyError/ValueError)": 68,
    "API属性幻觉 (AttributeError, 已计入②)": 54,
    "断言/逻辑 (AssertionError)": prc.get("C3_code_assert", 0),
    "其它 (Unknown)": prc.get("C7_other", 0),
}
TOTAL = 790
fail_total = TOTAL - prc.get("PASS", 0)

def pct(n): return f"{n/TOTAL*100:.1f}%"
def pctf(n): return f"{n/TOTAL*100:.2f}%"

# ---------- helpers ----------
def esc(s): return html.escape(str(s))
def svg_pie(data, colors, w=420, h=300, r=110, cx=150, cy=150):
    # data: list of (label, count, color)
    total = sum(c for _, c, _ in data)
    parts = []
    parts.append(f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="失败类别占比饼图">')
    angle = -90.0
    for label, cnt, col in data:
        if cnt <= 0: continue
        frac = cnt/total
        a1 = math.radians(angle); a2 = math.radians(angle + 360*frac)
        large = 1 if frac > 0.5 else 0
        x1 = cx + r*math.cos(a1); y1 = cy + r*math.sin(a1)
        x2 = cx + r*math.cos(a2); y2 = cy + r*math.sin(a2)
        if frac >= 0.999:
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{col}" stroke="#fff" stroke-width="1.5"/>')
        else:
            parts.append(f'<path d="M{cx},{cy} L{x1:.2f},{y1:.2f} A{r},{r} 0 {large},1 {x2:.2f},{y2:.2f} Z" fill="{col}" stroke="#fff" stroke-width="1.5"/>')
        angle += 360*frac
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r*0.46}" fill="#fff"/>')
    parts.append(f'<text x="{cx}" y="{cy-6}" text-anchor="middle" font-size="15" font-weight="700" fill="#222">失败 {fail_total}</text>')
    parts.append(f'<text x="{cx}" y="{cy+14}" text-anchor="middle" font-size="11" fill="#666">/ {TOTAL} 样本</text>')
    # legend
    lx = 285; ly = 30
    for label, cnt, col in data:
        if cnt <= 0: continue
        parts.append(f'<rect x="{lx}" y="{ly}" width="14" height="14" fill="{col}"/>')
        parts.append(f'<text x="{lx+20}" y="{ly+12}" font-size="12" fill="#333">{esc(label)} {cnt} ({cnt/total*100:.1f}%)</text>')
        ly += 24
    parts.append("</svg>")
    return "".join(parts)
print("aggregates ready", file=__import__("sys").stderr)

# ---------- per-task table ----------
def task_summary(rec):
    pc = rec["pass_count"]
    if pc == 5: return ("PASS", "5 次全通过")
    if pc > 0: return ("PART", "部分通过 %d/5" % pc)
    tc = rec["task_cat"]
    if tc in ("C5_degenerate_pass", "C4_gen_fail_other"): return ("CODE", "未产出 .py（幻觉 submit）")
    if tc == "C6_timeout": return ("CODE", "代码生成超时 (>2500s)")
    if tc == "C1_env_import": return ("RUN", "环境/依赖: ModuleNotFoundError")
    if tc == "C3_code_syntax": return ("RUN", "语法错误 (SyntaxError/IndentationError)")
    if tc == "C3_code_runtime": return ("RUN", "运行时错 (TypeError/NameError/AttributeError)")
    if tc == "C3_code_assert": return ("RUN", "断言失败 (AssertionError)")
    if tc == "C7_other": return ("RUN", "Unknown Failure")
    return ("RUN", "执行失败")

def task_rows_html():
    rows = []
    for idx, tid in enumerate(sorted(tasks.keys(), key=lambda x: int(x.split("-")[-1])), 1):
        r = tasks[tid]
        phase, summ = task_summary(r)
        avg_sess = sum(rr["iterations"] for rr in r["runs"]) / (5*2.0)
        avg_wall = sum(rr["wall_s"] for rr in r["runs"]) / 5.0
        avg_tok = sum(rr["tokens"] for rr in r["runs"]) / 5.0
        tok_str = "%.0f" % avg_tok if avg_tok > 0 else "N/A"
        pcell = "PASS" if r["pass_count"] == 5 else ("%d/5" % r["pass_count"] if r["pass_count"] > 0 else "0/5")
        pcls = "pass" if r["pass_count"] > 0 else "fail"
        rows.append("<tr><td>%d</td><td class='tid'>%s</td><td>%s</td><td>%s</td><td class='%s'>%s</td><td>%.1f</td><td>%.0f</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (idx, esc(tid), esc(r["scenario"]), esc(r["category"]), pcls, pcell, avg_sess, avg_wall, tok_str, phase, esc(summ)))
    return "\n".join(rows)

def scenario_table():
    rows = []
    for scen in ["Layout", "Schematic", "Design Management", "Others"]:
        tot = sum(1 for t, r in tasks.items() if r["scenario"] == scen)
        pas = sum(r["pass_count"] for t, r in tasks.items() if r["scenario"] == scen)
        union = sum(1 for t, r in tasks.items() if r["scenario"] == scen and r["pass_count"] > 0)
        rows.append("<tr><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%.1f%%</td></tr>" % (esc(scen), tot, union, pas, pas/(tot*5)*100))
    return "\n".join(rows)

def category_table():
    rows = []
    for cat in sorted(set(r["category"] for r in tasks.values())):
        tot = sum(1 for t, r in tasks.items() if r["category"] == cat)
        pas = sum(r["pass_count"] for t, r in tasks.items() if r["category"] == cat)
        union = sum(1 for t, r in tasks.items() if r["category"] == cat and r["pass_count"] > 0)
        rows.append("<tr><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%.1f%%</td></tr>" % (esc(cat), tot, union, pas, pas/(tot*5)*100))
    return "\n".join(rows)


# ---------- HTML assembly ----------
CSS = """
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;max-width:1180px;margin:0 auto;padding:24px;color:#222;background:#fafafa;line-height:1.6}
h1{font-size:24px;border-bottom:3px solid #c0392b;padding-bottom:8px}
h2{font-size:19px;margin-top:34px;border-left:5px solid #c0392b;padding-left:10px;background:#f0f0f0;padding:6px 10px}
h3{font-size:16px;margin-top:22px;color:#c0392b}
table{border-collapse:collapse;width:100%;margin:10px 0;font-size:13px;background:#fff}
th,td{border:1px solid #ddd;padding:5px 7px;text-align:left}
th{background:#e8e8e8}
tr:nth-child(even){background:#f7f7f7}
td.tid{font-family:monospace;font-size:12px}
td.pass{color:#1a7d1a;font-weight:700}
td.fail{color:#c0392b}
.box{background:#fff;border:1px solid #ddd;border-radius:6px;padding:14px 18px;margin:12px 0}
.meta{background:#fff7e6;border:1px solid #f0c36d}
.key{background:#fdecea;border:1px solid #e74c3c}
.kpi{display:flex;gap:14px;flex-wrap:wrap;margin:10px 0}
.kpi div{flex:1;min-width:150px;background:#fff;border:1px solid #ddd;border-radius:6px;padding:10px;text-align:center}
.kpi .n{font-size:24px;font-weight:700;color:#c0392b}
.kpi .l{font-size:12px;color:#666}
.snip{background:#1e1e1e;color:#eee;border-radius:5px;padding:10px 12px;font-family:monospace;font-size:12px;white-space:pre-wrap;overflow-x:auto;margin:6px 0}
.snip .path{color:#7fbfff;font-size:11px}
.snip .q{color:#9ccc65}
.tag{display:inline-block;padding:1px 7px;border-radius:10px;font-size:11px;color:#fff}
.p0{background:#c0392b}.p1{background:#e67e22}.p2{background:#27ae60}
details{margin:8px 0}
summary{cursor:pointer;font-weight:600;padding:6px;background:#e8e8e8;border:1px solid #ddd;border-radius:4px}
.tbd{color:#888;font-style:italic}
.chart{display:flex;flex-wrap:wrap;gap:20px;align-items:flex-start}
"""

PIE_COLORS = {"C5": "#c0392b", "C3": "#2980b9", "C2": "#8e44ad", "C6": "#e67e22", "C1": "#16a085", "PASS": "#27ae60"}
pie_data = [(buckets[k]["name"], buckets[k]["count"], PIE_COLORS[k]) for k in ["C5", "C3", "C2", "C6", "C1", "PASS"]]

# failure-stage bar (SVG)
def stage_bar():
    stages = [("代码生成未产出", 489, "#c0392b"), ("执行失败", 232, "#2980b9"), ("超时", 45, "#e67e22"), ("通过", 24, "#27ae60")]
    mx = max(c for _, c, _ in stages)
    W = 460; barw = 300; H = 26
    p = [f'<svg width="{W}" height="{len(stages)*H+10}" xmlns="http://www.w3.org/2000/svg">']
    y = 4
    for name, cnt, col in stages:
        w = cnt/mx*barw
        p.append(f'<rect x="150" y="{y}" width="{w:.0f}" height="18" fill="{col}"/>')
        p.append(f'<text x="145" y="{y+14}" text-anchor="end" font-size="12" fill="#333">{esc(name)}</text>')
        p.append(f'<text x="{150+w+6:.0f}" y="{y+14}" font-size="12" fill="#333">{cnt} ({cnt/790*100:.1f}%)</text>')
        y += H
    p.append("</svg>")
    return "".join(p)

print("head ready", file=__import__("sys").stderr)


# ---------- trace snippets (real, from run1 baseline) ----------
SNIP_C5_1 = ('EDA-Eval-PyAether-002 / run1',
  '~/eda_code_eval/2026_1113_024153/trace/EDA-Eval-PyAether-002/1794508916752_k92xl.messages.json',
  '模型声称: "I created the file `pyAether_code/dbOpenCV.py` with full docstring, type checks, and kwargs validation. Verified it\'s at the correct path inside the `pyAether_code` directory." 随后 16 次重复 "## summary / I completed the task by calling submit_and_exit. / ## verified / True"。\n'
  '实际: code/EDA-Eval-PyAether-002/ 目录为空——未写任何 .py 文件。harness 记录 completion="pass", status="fail"。',
  'ls code/EDA-Eval-PyAether-002/ => 空（无 pyAether_code 目录）')
SNIP_C5_2 = ('EDA-Eval-PyAether-001 / run1',
  '~/eda_code_eval/2026_1113_024153/trace/EDA-Eval-PyAether-001/',
  '模型在 1 个 cline 会话内调用 search_apis/get_api_details 共 ~243 次，反复得到 "All detail checks returned no useful result"，最终 "I\'ll complete the work" → submit_and_exit verified=true。9 个 session 文件，code 目录空。\n'
  '根因: 任务规范 API emyStringGetNumUniqueBits 模型未能通过 MCP 检索定位，陷入搜索循环后放弃。',
  '会话数=9 (异常 looping), code/EDA-Eval-PyAether-001/ 空')
SNIP_C5_3 = ('规模统计 / 全部 5 run',
  '421 个 degenerate (task,run) 样本中，submit_and_exit 的 verified 字段: true=307 (72.9%), false=26, 未捕获=88。',
  '即 ~73% 的"未产出文件"失败里，模型以 verified=true 自证完成——典型的幻觉式过早终止 (hallucinated completion)。',
  'python3 /tmp/rca_snip2.py  # verified 分布')
SNIP_C2_1 = ('EDA-Eval-PyAether-017 / run1',
  'output_evaluation/20261113_2012_app.e0031982/execution_results.jsonl',
  "stdout: FAIL: AttributeError: module 'pyAether' has no attribute 'enListAObject'",
  '模型幻觉了一个不存在的 API 名 enListAObject')
SNIP_C2_2 = ('EDA-Eval-PyAether-157 / run1',
  'execution_results.jsonl (同上)',
  "stdout: FAIL: AttributeError: module 'pyAether' has no attribute 'dbgetdbsrc'",
  'dbgetdbsrc 不是真实 API（真实为 dbGetDb... 类）')
SNIP_C2_3 = ('EDA-Eval-PyAether-021 / run1',
  'execution_results.jsonl (同上)',
  "stdout: FAIL: AttributeError: module 'pyAether' has no attribute 'dbInstall'",
  'API 名称幻觉 dbInstall')
SNIP_C3S_1 = ('EDA-Eval-PyAether-106 / run1', 'execution_results.jsonl',
  "stdout: FAIL: SyntaxError: invalid character '，' (U+FF0C)", '代码中混入全角中文逗号（tokenizer/编码问题）')
SNIP_C3S_2 = ('EDA-Eval-PyAether-114 / run1', 'execution_results.jsonl',
  "stdout: FAIL: SyntaxError: invalid syntax", '生成代码语法不完整')
SNIP_C3R_1 = ('EDA-Eval-PyAether-061 / run1', 'execution_results.jsonl',
  "stdout: FAIL: TypeError: has_matching_enclosure() takes 0 positional arguments but 5 were given",
  'SWIG positional-only API 用 kwargs/位置参数传错（prompt 已警告但仍犯）')
SNIP_C3R_2 = ('EDA-Eval-PyAether-042 / run1', 'execution_results.jsonl',
  "stdout: FAIL: TypeError: __init__() got an unexpected keyword argument 'lib_name'",
  '构造函数参数名幻觉 lib_name')
SNIP_C3A_1 = ('EDA-Eval-PyAether-006 / run1', 'execution_results.jsonl',
  "stdout: FAIL: AssertionError: Test Case 1 Failed: Asymmetric values", '逻辑/约束漏读：对称性要求未满足')
SNIP_C3A_2 = ('EDA-Eval-PyAether-024 / run1', 'execution_results.jsonl',
  "stdout: FAIL: AssertionError: Failed on overlapping boxes", '几何重叠判定逻辑错')
SNIP_C1_1 = ('EDA-Eval-PyAether-010 / run1', 'execution_results.jsonl',
  "stdout: FAIL: ModuleNotFoundError: No module named 'pyAether.emyString'", '误把 emyString 当子模块 import（应作属性访问）')
SNIP_C6_1 = ('EDA-Eval-PyAether-0xx / 5 run 汇总', 'final_report.json summary',
  '45 个 (task,run) 样本 generation_statuses=timeout，平均 wall≈2579s（触及 2500s 预算上限被杀），未产出代码。',
  'gen timeout 计数 = error_types "Generation timeout" = 45')


def snip_block(s):
    return '<div class="snip"><span class="path">[%s]</span>\n<span class="path">路径: %s</span>\n%s\n<span class="q">证据: %s</span></div>' % (esc(s[0]), esc(s[1]), esc(s[2]), esc(s[3]))

def fix_row(action, lift, cost, pri):
    cls = {"P0": "p0", "P1": "p1", "P2": "p2"}[pri]
    return "<tr><td>%s</td><td>%s</td><td>%s</td><td><span class='tag %s'>%s</span></td></tr>" % (esc(action), esc(lift), esc(cost), cls, pri)

H = []
H.append("<!DOCTYPE html><html lang='zh-CN'><head><meta charset='utf-8'>")
H.append("<meta name='viewport' content='width=device-width,initial-scale=1'>")
H.append("<title>MiniCPM5-2B 基线 EDA-Eval-PyAether(158) RCA 报告</title>")
H.append("<style>%s</style></head><body>" % CSS)
H.append("<h1>MiniCPM5-2B（SFT step105）基线在 EDA-Eval-PyAether(158) 的 3.04% 逐题归因报告</h1>")
H.append("<p style='color:#666'>后训练线 · 基线根因分析 (RCA) · 2026-11-14 · 单文件自包含 / 0 外链 / 0 script / 内联 SVG</p>")

# meta box
H.append("<div class='box meta'><h3>一、分析对象与口径（原始数据，可复算）</h3>")
H.append("<ul>"
  "<li><b>基线 ckpt</b>：<code>minicpm5-2b-sft-v39-final</code>（SFT step105；替身 MiniCPM5-2B，v11–v38 语料 1344 对）</li>"
  "<li><b>Serve 配置</b>：vLLM，GPU6，endpoint <code>http://127.0.0.1:8096/v1</code>，served-model-name <code>minicpm5-2b-sft-v39-final</code></li>"
  "<li><b>数据集</b>：EDA-Eval-PyAether-v20260311_fixed.jsonl，158 题（Layout 64 / Schematic 47 / Design Management 24 / Others 23）</li>"
  "<li><b>评测协议</b>：cline harness + pyAether MCP 工具（search_apis/get_api_details），沙盒经 dual-nix-tunnel，2500s 超时，单 trace，5-run，Pass@1 口径</li>"
  "<li><b>结果复核</b>：5 run Pass@1 = 6/158, 3/158, 4/158, 5/158, 6/158 → <b>mean = 3.04% ± 0.83%</b>（分子 4.8/158，与 3.04% 一致）</li>"
  "<li><b>数据来源</b>：<code>/tmp/posttrain_5run_eval/step105/run{1..5}/final_report.json</code> + 逐题 <code>~/eda_code_eval/&lt;batch&gt;/trace/</code> + <code>output_evaluation/20261113_2012/execution_results.jsonl</code></li>"
  "</ul></div>")

# KPI
H.append("<div class='kpi'>"
  f"<div><div class='n'>3.04%</div><div class='l'>5-run mean Pass@1</div></div>"
  f"<div><div class='n'>4.8/158</div><div class='l'>平均通过题数</div></div>"
  f"<div><div class='n'>22</div><div class='l'>至少 1 run 通过的题（并集）</div></div>"
  f"<div><div class='n'>61.9%</div><div class='l'>失败样本=未产出文件</div></div>"
  f"<div><div class='n'>307/421</div><div class='l'>未产出却 verified=true</div></div>"
  "</div>")

# Section: executive summary
H.append("<div class='box key'><h3>二、一句话结论（先看这个）</h3>")
H.append("<p>3.04% 主要<b>卡在 agentic 执行层（推理/规划 + 工具协议），而非代码正确性层</b>。"
  f"790 个 (任务,run) 样本里 <b>{buckets['C5']['count']}（{pct(buckets['C5']['count'])}）</b>是「模型根本没把 .py 写到 <code>pyAether_code/</code>」——"
  f"其中 307 例模型以 <code>submit_and_exit verified=true</code> 自证完成（幻觉式过早终止）；"
  f"另有 <b>{buckets['C2']['count']}</b> 例调用<b>不存在的 API</b>（API 名称幻觉）。"
  "真正「写了代码但逻辑错」的只占少数。<b>若只修一件事</b>：修掉「未产出文件就 submit」的幻觉终止 + 强制写文件闸门（详见 §5 ⑤的 P0 fix）。</p></div>")

# Section: per-task table
H.append("<h2>三、逐题总表（158 行，可折叠）</h2>")
H.append("<details><summary>展开/收起 158 题逐题表（# / task_id / 场景 / 类别 / Pass x/5 / 平均会话数 / 平均耗时(s) / tokens / 失败阶段 / 一句话摘要）</summary>")
H.append("<table><thead><tr><th>#</th><th>task_id</th><th>场景</th><th>类别</th><th>Pass</th><th>会话数</th><th>耗时(s)</th><th>tokens</th><th>失败阶段</th><th>一句话失败摘要</th></tr></thead><tbody>")
H.append(task_rows_html())
H.append("</tbody></table></details>")
H.append("<p class='tbd'>注：tokens 列标注 N/A——cline session 元数据未逐消息记录 usage，无原始值可取（按纪律不估）。会话数=trace 中 session .json 数；耗时=单次 cline run 墙钟秒。</p>")
print("body1 ready", file=__import__("sys").stderr)


# Section: failure attribution
H.append("<h2>四、失败归因分类（核心）</h2>")
H.append("<p>以 790 个 (任务,run) 样本为口径，按<b>根因</b>归入 6 类（5 类失败 + 通过；由 158 题实际结果 + trace 原文自行提炼，未套用预设分类表）。每类附题数、占比、典型 trace 片段（原文摘引 + 路径）。</p>")
H.append("<table><thead><tr><th>类别</th><th>题数(样本)</th><th>占比</th><th>说明</th></tr></thead><tbody>")
order = ["C5", "C3", "C2", "C6", "C1", "PASS"]
for k in order:
    b = buckets[k]
    H.append("<tr><td><b>%s</b></td><td>%d</td><td>%s</td><td>%s</td></tr>" % (esc(b["name"]), b["count"], pct(b["count"]), esc(b["desc"])))
H.append("</tbody></table>")
H.append("<p><b>③ 代码语义 细分</b>：语法(SyntaxError/IndentationError) 86；运行时(TypeError/NameError/KeyError/ValueError) 68；API属性幻觉(AttributeError，已单列②) 54；断言/逻辑(AssertionError) 14；其它(Unknown) 3。</p>")

# pie + stage bar
H.append("<h2>五、图表</h2>")
H.append("<div class='chart'><div>%s</div><div>%s</div></div>" % (svg_pie(pie_data, PIE_COLORS), stage_bar()))
H.append("<p style='font-size:12px;color:#666'>左：失败类别占比饼图（内联 SVG）。右：失败阶段条形图（代码生成未产出 489 / 执行失败 232 / 超时 45 / 通过 24）。</p>")

# category x pass rate tables
H.append("<h3>5.1 按场景的通过率</h3><table><thead><tr><th>场景</th><th>题数</th><th>并集通过</th><th>通过样本数</th><th>样本通过率</th></tr></thead><tbody>%s</tbody></table>" % scenario_table())
H.append("<h3>5.2 按类别的通过率</h3><table><thead><tr><th>类别</th><th>题数</th><th>并集通过</th><th>通过样本数</th><th>样本通过率</th></tr></thead><tbody>%s</tbody></table>" % category_table())

# per-cat avg
H.append("<h3>5.3 各失败类别平均耗时/会话数</h3><table><thead><tr><th>类别</th><th>样本</th><th>平均会话数</th><th>平均墙钟(s)</th></tr></thead><tbody>")
avg = {"C5":(479,1.9,393),"C3_runtime":(122,2.0,358),"C3_syntax":(86,2.3,482),"C6":(45,2.2,2579),"PASS":(24,2.1,237),"C3_assert":(14,2.1,376),"C1":(7,2.0,216)}
for k,(n,it,w) in avg.items():
    H.append("<tr><td>%s</td><td>%d</td><td>%.1f</td><td>%d</td></tr>" % (k,n,it,w))
H.append("</tbody></table><p class='tbd'>会话数为 trace 文件计数/2（每 session 含 .json+.messages.json 两文件）。超时类平均 2579s≈触及 2500s 上限。</p>")

# pass commonality
H.append("<h3>5.4 通过题的共性（22 题并集，正向样本）</h3><div class='box'>")
H.append("<ul>"
  "<li><b>场景</b>：Others 6.1% &gt; Schematic 3.8% &gt; Layout 2.2% &gt; Design Management 0.8%。Others（工具/仿真配置类）最易。</li>"
  "<li><b>类别</b>：Simulation & Analysis Configuration 7.6% &gt; Utilities 5.3% &gt; Geometry 3.8%；Design Content Creation（46 题）仅 1.3% 最难。</li>"
  "<li><b>API</b>：通过的题集中在<b>简单、高频的 db*/emyPoint* 基础 API</b>（dbOpenCVByType、dbCloseCV、dbGetAllLibs、dbCreateLib、emyPoint、emyPointArray），即「单个高层操作」类任务。</li>"
  "<li><b>代码量</b>：参考解 lines_of_code 集中在 1–10 行（短函数）；长程/批量创建类（schematic 体系）几乎全失败。</li>"
  "<li><b>结论</b>：通过=「API 易检索 + 单步操作 + 短代码」。失败=「API 难检索 + 多步/批量 + 需 SWIG positional 细节」。</li>"
  "</ul></div>")

# snippets per category
H.append("<h2>六、各类典型 trace 片段（原文摘引 + 路径）</h2>")
H.append("<h3>⑤ 推理/规划（未产出文件 + 幻觉 submit）</h3>%s%s%s" % (snip_block(SNIP_C5_1), snip_block(SNIP_C5_2), snip_block(SNIP_C5_3)))
H.append("<h3>② 工具调用/协议（API 名称幻觉）</h3>%s%s%s" % (snip_block(SNIP_C2_1), snip_block(SNIP_C2_2), snip_block(SNIP_C2_3)))
H.append("<h3>③ 代码语义—语法</h3>%s%s" % (snip_block(SNIP_C3S_1), snip_block(SNIP_C3S_2)))
H.append("<h3>③ 代码语义—运行时/SWIG 参数</h3>%s%s" % (snip_block(SNIP_C3R_1), snip_block(SNIP_C3R_2)))
H.append("<h3>③ 代码语义—断言/逻辑</h3>%s%s" % (snip_block(SNIP_C3A_1), snip_block(SNIP_C3A_2)))
H.append("<h3>① 环境/依赖</h3>%s" % snip_block(SNIP_C1_1))
H.append("<h3>⑥ 超时/预算</h3>%s" % snip_block(SNIP_C6_1))
print("body2 ready", file=__import__("sys").stderr)


# Section: per-category fixes
H.append("<h2>七、逐类 fix 方案（可执行）</h2>")

H.append("<h3>⑤ 推理/规划（未产出文件 + 幻觉终止）— 占失败 64%</h3>")
H.append("<p><b>根因</b>：模型在 API 检索受挫后，不调用写文件工具、直接 <code>submit_and_exit verified=true</code> 幻觉式自证完成；harness 无「文件存在」闸门，照单全收为 fail。</p>")
H.append("<table><thead><tr><th>具体改动点</th><th>预期提升</th><th>实施成本</th><th>优先级</th></tr></thead><tbody>")
H.append(fix_row("评测侧：harness 增加 PreSubmit 闸门——submit_and_exit 前校验 pyAether_code/<entry_point>.py 存在且非空，否则拒绝并强制继续（最直接回收）", "保守 +8~15pp（把'幻觉 submit'转成真实产出）", "2 人时（改 run_cline_script.sh + cline 工具层）", "P0"))
H.append(fix_row("推理侧：在系统 prompt 注入硬约束「必须先 write_to_file 再 submit；verified=true 前读取文件确认存在」+ 失败重试策略（搜索 5 次未中则用关键词补路/列举 API 族）", "+5~10pp", "1 人时", "P0"))
H.append(fix_row("数据侧：补「检索失败→兜底编码」正样本 SFT（API 搜不到时基于已知 API 族直接写骨架），抑制放弃行为", "+3~6pp", "8 机时（造 200~400 对）", "P1"))
H.append("</tbody></table>")

H.append("<h3>② 工具调用/协议（API 名称幻觉）— 54 样本</h3>")
H.append("<p><b>根因</b>：模型编造不存在的 API 名（enListAObject / dbgetdbsrc / dbInstall）。MCP search_apis 已可用但模型未检索确认即编码。</p>")
H.append("<table><thead><tr><th>具体改动点</th><th>预期提升</th><th>实施成本</th><th>优先级</th></tr></thead><tbody>")
H.append(fix_row("推理侧：编码前强制 get_api_details 校验每个 API 名存在；不存在的禁止使用（工具 schema 校验 hook）", "+3~5pp", "2 人时", "P0"))
H.append(fix_row("数据侧：SFT 增补「API 名幻觉→纠正」负样本 + 完整 API 名表注入上下文", "+2~4pp", "6 机时", "P1"))
H.append("</tbody></table>")

H.append("<h3>③ 代码语义（语法/运行时/断言）— 171 样本</h3>")
H.append("<p><b>根因</b>：SWIG positional-only 误用 kwargs（takes 0 positional arguments but 5 were given）、全角字符混入、构造参数名幻觉、几何/对称约束漏读。</p>")
H.append("<table><thead><tr><th>具体改动点</th><th>预期提升</th><th>实施成本</th><th>优先级</th></tr></thead><tbody>")
H.append(fix_row("数据侧：SFT 增补 SWIG positional-only 正样本 + 全角字符清洗 + emy*.create 族参数签名对照表", "+4~7pp", "10 机时", "P1"))
H.append(fix_row("推理侧：沙盒执行反馈闭环——run 失败后把 traceback 喂回模型自纠一轮（当前无沙盒执行反馈，仅脑内推演）", "+3~6pp", "需沙盒，4 人时", "P1"))
H.append(fix_row("数据侧：针对断言失败类补「约束逐条核对」CoT 样本（对称/重叠/边界）", "+1~3pp", "6 机时", "P2"))
H.append("</tbody></table>")

H.append("<h3>⑥ 超时/预算 — 45 样本</h3>")
H.append("<p><b>根因</b>：搜索循环（task 001 单 session 243 次检索）耗尽 2500s。与 ⑤ 同源（搜索不收敛）。</p>")
H.append("<table><thead><tr><th>具体改动点</th><th>预期提升</th><th>实施成本</th><th>优先级</th></tr></thead><tbody>")
H.append(fix_row("推理侧：检索次数硬上限 + 命中即停策略 + 超时降级为'基于已有结果编码'", "+1~2pp", "1 人时", "P1"))
H.append(fix_row("评测侧：评估是否对'搜索循环'单独计为协议失败而非能力失败（口径透明化）", "0pp（口径）", "0.5 人时", "P2"))
H.append("</tbody></table>")

H.append("<h3>① 环境/依赖 — 7 样本</h3>")
H.append("<p><b>根因</b>：<code>import pyAether.emyString</code> 误把属性当子模块。属代码语义边缘，并入 ③ 数据侧修。</p>")

H.append("<h3>「先做这 3 件」排序建议（按 ROI）</h3>")
H.append("<table><thead><tr><th>#</th><th>动作</th><th>预期提升</th><th>成本</th></tr></thead><tbody>")
H.append("<tr><td>1</td><td><b>PreSubmit 文件存在闸门 + 系统prompt硬约束「先写文件再 submit」</b>（⑤，P0）</td><td>+8~15pp</td><td>3 人时</td></tr>")
H.append("<tr><td>2</td><td><b>编码前强制 get_api_details 校验 API 名存在</b>（②，P0）</td><td>+3~5pp</td><td>2 人时</td></tr>")
H.append("<tr><td>3</td><td><b>SFT 增补 SWIG positional-only + API 名纠正 + 兜底编码正样本</b>（②③⑤，P1）</td><td>+5~10pp</td><td>~24 机时</td></tr>")
H.append("</tbody></table>")
H.append("<p>三者合计保守预期 <b>+16~30pp</b>，即从 3.04% 推到 ~19~33%（对应预注册阶梯 M1 50% 仍需 RL，但先回收这层'协议/执行'损失是前提）。</p>")

# conclusion
H.append("<h2>八、结论与下一步</h2>")
H.append("<div class='box key'>")
H.append("<p><b>3.04% 主要卡在哪一层</b>：<b>agentic 执行层（推理/规划 + 工具协议）</b>，而非代码语义层。"
  f"790 样本中 {buckets['C5']['count']}（{pct(buckets['C5']['count'])}）是「根本没写出文件」、{buckets['C2']['count']} 是「调用不存在的 API」——"
  "二者合计 ~69% 的失败是<b>协议/执行可回收损失</b>，与 R0 诊断 D1（工具调用合法率低）一致。"
  "真正的「写了代码但逻辑错」（③ 去除 ② 后约 117 样本，14.8%）才是纯能力差距。</p>")
H.append("<p><b>若只修一件事</b>：修「未产出文件就 submit_and_exit verified=true」——加 PreSubmit 文件存在闸门 + prompt 硬约束。这是 ROI 最高、成本最低（3 人时）、且不依赖 GPU 的一刀。</p>")
H.append("<p><b>下一步</b>：① 落地 P0 两件（文件闸门 + API 名校验）后重跑 5-run baseline，验证「协议可回收」能拿回多少 pp；"
  "② 再决定 RL（R2 已显负信号，先回收协议层再 RL 更可能产生正向增益）；③ SFT 语料按 ②③⑤ 比例补样本。</p>")
H.append("</div>")

# appendix: reproduce commands
H.append("<h2>附录：复算命令（所有数字可追到落盘文件）</h2>")
H.append("<div class='snip'>"
  "# 5-run mean\n"
  "cat /tmp/posttrain_5run_eval/5run_analysis.json\n"
  "# 单 run 逐题\n"
  "python3 -c \"import json;d=json.load(open('/tmp/posttrain_5run_eval/step105/run1/final_report.json'));print(d['metrics'],d['summary'])\"\n"
  "# 790 样本 (gen,exec,error_types) 分布\n"
  "python3 rca_baseline_aggregate.py && python3 rca_baseline_enrich.py\n"
  "# 执行 traceback（run1）\n"
  "cat ~/code/EDA-Eval-Framework/output_evaluation/20261113_2012_app.e0031982/execution_results.jsonl\n"
  "# degenerate submit verified 分布\n"
  "python3 /tmp/rca_snip2.py\n"
  "# 任务场景/类别\n"
  "python3 -c \"import json,collections;[print(collections.Counter(json.loads(l)['metadata']['scenario'] for l in open('~/code/EDA-Eval-Framework/benchmarks/v20260602/EDA-Eval-PyAether-v20260311_fixed.jsonl'.replace('~','/home/app.e0031982'))))]\"\n"
  "</div>")
H.append("<p class='tbd'>数据口径声明：①②③⑥① 的样本计数来自 5 run 的 final_report.json details_per_task.error_types（精确）；②「has no attribute」占比 93% 来自 run1 execution_results 抽查（14/15），用于定性而非改变桶计数；trace 片段均原文摘自上述路径，未编造。</p>")
H.append("<p style='color:#999;margin-top:30px'>— 报告结束 · posttrain 线 RCA · 2026-11-14 —</p>")
H.append("</body></html>")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(H))
print("WROTE", OUT, "bytes=", os.path.getsize(OUT), file=__import__("sys").stderr)

