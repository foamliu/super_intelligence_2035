#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate report_posttrain_pyaether_rca_v2_zh.html from trace analysis data.
Single-file, 0 external links, 0 script, inline SVG charts."""
import json, math

# ====== DATA (all reproducible from trace roots + /tmp/rca_baseline_enriched.json) ======
PASS_PER_RUN = [6, 3, 4, 5, 6]            # 24/790
PASS_MEAN = 0.03037974683544304
PASS_STD = 0.008296                # 0.83%
N_TASKS = 158
N_TASK_RUNS = 790

# per-run tool counts (deep analysis)
PER_RUN = [
  {'run':'run1(02:41)','sa':322,'kw':511,'ga':458,'rc':35,'tot':10195,'submit':6009,'submit_err':5794,'pass':6},
  {'run':'run2(06:27)','sa':775,'kw':375,'ga':327,'rc':115,'tot':4720,'submit':346,'submit_err':22,'pass':3},
  {'run':'run3(10:18)','sa':232,'kw':349,'ga':343,'rc':119,'tot':11241,'submit':6984,'submit_err':6724,'pass':4},
  {'run':'run4(13:13)','sa':322,'kw':263,'ga':350,'rc':74,'tot':3248,'submit':132,'submit_err':10,'pass':5},
  {'run':'run5(16:30)','sa':267,'kw':241,'ga':409,'rc':164,'tot':3586,'submit':228,'submit_err':22,'pass':6},
]
AGG = {'sa':1918,'kw':1739,'ga':1887,'rc':507,'submit':13699,'submit_err':12572,
       'rag':1918+1739+1887,'sandbox':507,'total_mcp':1918+1739+1887+507}
# run_code success/error (response-text scan)
RC_OK = 118; RC_FAIL = 231; RC_TOTAL_PARSED = 349
RC_ERR = {'NameError':66,'SyntaxError':58,'non-ASCII':39,'AttributeError':24,'other':39,'TypeError':3,'ImportError':2}
RC_DEEP = {'rc_total':507,'rc_success':326}  # deep analysis (is_error based)
TOOLNAME_AS_FUNC = 4
# per-task distribution (729 task-sessions)
PT = {'calls_mean':45.3,'calls_median':7,'calls_max':6772,'calls_p90':54,
      'mcp_mean':8.3,'mcp_median':3,'mcp_max':426,
      'rc_mean':0.7,'rc_median':0,'rc_max':89,
      'n_sessions':729,'tasks_with_mcp':549,'tasks_with_rc':72,
      'zero_mcp':180,'zero_rc':657}
RETRIEVED = 333; OVERLAP = 19
CONTRA = {'hits':236,'total':507}
# failure categories (790 task-runs)
CAT = [('C5_degenerate_pass','⑤推理/放弃-degenerate(pass空操作)',479),
       ('C3_code_runtime','③代码-运行时语义(Attribute/Type/Name)',122),
       ('C3_code_syntax','③代码-语法(SyntaxError)',86),
       ('C6_timeout','⑥超时/预算',45),
       ('PASS','✅通过',24),
       ('C3_code_assert','③代码-断言/逻辑',14),
       ('C4_gen_fail_other','④输出格式-产物被拒',10),
       ('C1_env_import','①环境/依赖',7),
       ('C7_other','⑦其它',3)]
SCEN = {'Layout':64,'Schematic':47,'Design Management':24,'Others':23}
UNION_PASS = 22
UNION_DIST = {2:2, 1:20}
ITS = {'pass_mean':2.1,'fail_mean':2.0}
WALL = {'pass_mean':237,'fail_mean':534}

CAT_COLORS = {'C5_degenerate_pass':'#8e44ad','C3_code_runtime':'#e67e22','C3_code_syntax':'#d35400',
  'C6_timeout':'#7f8c8d','PASS':'#27ae60','C3_code_assert':'#c0392b','C4_gen_fail_other':'#f39c12',
  'C1_env_import':'#2980b9','C7_other':'#bdc3c7'}

def pct(a,b): return round(100.0*a/b,2) if b else 0.0

def svg_pie(data, colors, cx=110, cy=110, r=88, sw=320, sh=240):
    total = sum(v for _,_,v in data)
    ang = -90.0
    paths = []
    for key,label,v in data:
        frac = v/total
        a2 = ang + frac*360.0
        a1r = math.radians(ang); a2r = math.radians(a2)
        x1 = cx + r*math.cos(a1r); y1 = cy + r*math.sin(a1r)
        x2 = cx + r*math.cos(a2r); y2 = cy + r*math.sin(a2r)
        large = 1 if (a2-ang) > 180 else 0
        col = colors.get(key,'#888')
        if frac >= 0.999:
            paths.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{col}"/>')
        else:
            paths.append(f'<path d="M{cx:.1f} {cy:.1f} L{x1:.1f} {y1:.1f} A{r} {r} 0 {large} 1 {x2:.1f} {y2:.1f} Z" fill="{col}"/>')
        ang = a2
    # legend
    ly = 12
    legs = []
    for key,label,v in data:
        col = colors.get(key,'#888')
        legs.append(f'<rect x="210" y="{ly}" width="12" height="12" fill="{col}"/><text x="228" y="{ly+10}" font-size="10" fill="#333">{label} {v}({pct(v,total)}%)</text>')
        ly += 16
    return f'<svg width="{sw}" height="{sh}" viewBox="0 0 {sw} {sh}">{"".join(paths)}{"".join(legs)}</svg>'

def svg_bar(items, title, sw=560, sh=240, color='#2980b9'):
    # items: list of (label, value)
    n = len(items)
    bw = 50
    gap = 18
    base_w = n*bw + (n+1)*gap
    w = max(sw, base_w+60)
    maxv = max(v for _,v in items) if items else 1
    bh_max = 150
    bars = []
    x = gap
    for label,v in items:
        bh = int(bh_max * v / maxv) if maxv else 0
        by = 30 + (bh_max - bh)
        bars.append(f'<rect x="{x}" y="{by}" width="{bw}" height="{bh}" fill="{color}"/><text x="{x+bw/2}" y="{by-4}" text-anchor="middle" font-size="11" fill="#333">{v}</text><text x="{x+bw/2}" y="{30+bh_max+14}" text-anchor="middle" font-size="10" fill="#555">{label}</text>')
        x += bw + gap
    return f'<svg width="{w}" height="{sh}" viewBox="0 0 {w} {sh}"><text x="{w/2}" y="16" text-anchor="middle" font-size="12" fill="#222" font-weight="bold">{title}</text>{"".join(bars)}</svg>'

def svg_funnel(steps, sw=560, sh=260):
    # steps: list of (label, value, color)
    n = len(steps)
    maxv = max(v for _,v,_ in steps)
    w = sw
    poly = []
    y = 10
    rh = (sh-20)/n
    for i,(label,v,col) in enumerate(steps):
        hw = int((w-120) * v / maxv / 2)
        cx = w/2
        y1 = y; y2 = y + rh*0.8
        poly.append(f'<polygon points="{cx-hw},{y1} {cx+hw},{y1} {cx+hw*0.7},{y2} {cx-hw*0.7},{y2}" fill="{col}"/>')
        poly.append(f'<text x="{cx}" y="{(y1+y2)/2+4}" text-anchor="middle" font-size="11" fill="#fff" font-weight="bold">{label}: {v}</text>')
        y = y2 + rh*0.2
    return f'<svg width="{w}" height="{sh}" viewBox="0 0 {w} {sh}">{"".join(poly)}</svg>'

def svg_histo(values, sw=420, sh=200, color='#8e44ad'):
    # values: list of (label, count)
    n=len(values)
    bw=46; gap=10
    maxv=max(c for _,c in values) if values else 1
    bars=[]
    x=gap
    for label,c in values:
        bh=int(150*c/maxv)
        by=30+(150-bh)
        bars.append(f'<rect x="{x}" y="{by}" width="{bw}" height="{bh}" fill="{color}"/><text x="{x+bw/2}" y="{by-3}" text-anchor="middle" font-size="10" fill="#333">{c}</text><text x="{x+bw/2}" y="{30+150+12}" text-anchor="middle" font-size="9" fill="#555">{label}</text>')
        x+=bw+gap
    return f'<svg width="{sw}" height="{sh}" viewBox="0 0 {sw} {sh}">{"".join(bars)}</svg>'

# ====== build HTML ======
H = []
H.append("<!DOCTYPE html><html lang='zh-CN'><head><meta charset='utf-8'>")
H.append("<meta name='viewport' content='width=device-width,initial-scale=1'>")
H.append("<title>MiniCPM5-2B PyAether RCA v2 — 工具调用 1.9 万次为何仅 3.04%</title>")
H.append("<style>")
H.append("body{font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;max-width:1180px;margin:0 auto;padding:24px;color:#222;background:#fafafa;line-height:1.6}")
H.append("h1{font-size:23px;border-bottom:3px solid #c0392b;padding-bottom:8px}")
H.append("h2{font-size:19px;margin-top:34px;border-left:5px solid #c0392b;padding-left:10px;background:#f0f0f0;padding:6px 10px}")
H.append("h3{font-size:16px;margin-top:22px;color:#c0392b}")
H.append("table{border-collapse:collapse;width:100%;margin:10px 0;font-size:13px;background:#fff}")
H.append("th,td{border:1px solid #ddd;padding:5px 7px;text-align:left}")
H.append("th{background:#e8e8e8}")
H.append("tr:nth-child(even){background:#f7f7f7}")
H.append(".box{background:#fff;border:1px solid #ddd;border-radius:6px;padding:14px 18px;margin:12px 0}")
H.append(".meta{background:#fff7e6;border:1px solid #f0c36d}")
H.append(".key{background:#fdecea;border:1px solid #e74c3c}")
H.append(".good{background:#eafaf1;border:1px solid #27ae60}")
H.append("code{background:#f0f0f0;padding:1px 4px;border-radius:3px;font-size:12px}")
H.append("pre{background:#263238;color:#eceff1;padding:10px 12px;border-radius:6px;overflow-x:auto;font-size:12px}")
H.append(".kpi{display:flex;gap:12px;flex-wrap:wrap;margin:10px 0}")
H.append(".kpi div{flex:1;min-width:150px;background:#fff;border:1px solid #ddd;border-radius:6px;padding:10px;text-align:center}")
H.append(".kpi .big{font-size:22px;font-weight:700;color:#c0392b}")
H.append(".chart{display:flex;flex-wrap:wrap;gap:10px;align-items:flex-start;margin:10px 0}")
H.append(".oldnote{background:#fff3cd;border:2px solid #ffc107;border-radius:6px;padding:12px 16px;margin:10px 0}")
H.append("</style></head><body>")

H.append("<h1>MiniCPM5-2B PyAether RCA v2 — 工具调用 1.9 万次为何仍只有 3.04%</h1>")
H.append("<div class='oldnote'><b>ⓘ 与旧报告的关系</b>：本报告为 <b>v2 重写版</b>，主线是「工具调用约 1.9 万次 vs Pass@1 仅 3.04%」的落差归因。旧报告 <code>report_posttrain_baseline_pyaether_rca_zh.html</code> 保留作历史，其失败分类与口径仍成立，但本 v2 新增了<b>工具调用画像</b>核心章节，并以 trace 实证回答了「检索到≠用对 / 写得出≠跑得通 / 跑得通≠判得过」三个具体问题。旧报告结论不废止，本报告在其之上深化。</div>")

# ---- Section 1 口径 ----
H.append("<h2>1. 口径与数据（可复算）</h2>")
H.append("<div class='box meta'>")
H.append("<table>")
H.append("<tr><th>项</th><th>值</th></tr>")
H.append("<tr><td>被测基线 ckpt</td><td>MiniCPM5-2B + SFT v39 <b>step105-final</b>（served-model-name = <code>minicpm5-2b-sft-v39-final</code>）</td></tr>")
H.append("<tr><td>serve 配置</td><td>vLLM，GPU6 :8096，<code>--max-model-len 65536 --enforce-eager --tool-call-parser minicpm5 --enable-auto-tool-choice --max-num-seqs 4</code>，transformers 4.49.0 / vLLM 0.7.3</td></tr>")
H.append("<tr><td>数据集</td><td><code>EDA-Eval-PyAether-v20260311_fixed.jsonl</code>，158 题，md5 <code>35d8331c…</code></td></tr>")
H.append("<tr><td>评测协议</td><td>Pass@1，5-run，2500s/题超时，<code>-p 8 -n</code>，fresh context（冻结协议，总纲 §2）</td></tr>")
H.append("<tr><td>trace 根路径</td><td><code>~/eda_code_eval/2026_1113_{024153,062714,101852,131353,163053}/trace/</code>（5 个 run，每 run 158 题 trace）</td></tr>")
H.append("<tr><td>eval 结果路径</td><td><code>/tmp/posttrain_5run_eval/step105/run{1..5}/final_report.json</code></td></tr>")
H.append("<tr><td>扫描脚本</td><td><code>run/baize_posttrain_trace_toolcount.py</code>（tool_use 块计数）+ <code>run/baize_posttrain_trace_deep_analysis.py</code>（深度分析）+ <code>run/rca_baseline_aggregate.py</code>/<code>rca_baseline_enrich.py</code>（失败分类）</td></tr>")
H.append("<tr><td>扫描命令示例</td><td><code>grep -rahoiE 'search_apis|get_api_details|run_code' ~/eda_code_eval/2026_1113_024153/trace/ | sort | uniq -c</code>（字符串粗扫，虚高；精确计数用 toolcount.py 数 tool_use 块）</td></tr>")
H.append("<tr><td>5-run 通过数</td><td>[6, 3, 4, 5, 6] = 24/790</td></tr>")
H.append("<tr><td>Pass@1 mean±std</td><td><b>3.04% ± 0.83%</b>（mean=0.0304, std=0.0083）</td></tr>")
H.append("<tr><td>用户实测 trace 统计（粗扫字符串）</td><td>search_apis 4,418 + search_apis_by_keyword 2,060 + get_api_details 5,436 + run_code 1,460 + run_commands 6,401 ≈ 19,775 次</td></tr>")
H.append("<tr><td>本报告精确统计（tool_use 块）</td><td>MCP 工具 6,051 次（search_apis 1,918 + keyword 1,739 + get_api_details 1,887 + run_code 507）+ submit_and_exit 13,699 次 = 总 tool_use 约 32,990 次（见 §2 说明）</td></tr>")
H.append("</table>")
H.append("</div>")
H.append("<div class='key'><b>关于「1.9 万 vs 3.04%」口径</b>：用户引用的 19,775 次是用 <code>grep</code> 数<b>字符串出现次数</code>（含 tool_result 回显、文本里重复出现的工具名，因此虚高）。本报告用 <b>tool_use 结构化块</b>精确计数：MCP 检索/沙盒工具实际调用 6,051 次（其中检索 5,544 + 沙盒执行 507），另有 13,699 次 <code>submit_and_exit</code>（退出工具，91.77% 报错）。无论用哪个口径，<b>「工具调用上万次但通过率仅 3.04%」的巨大落差都成立</b>——这正是本报告要解释的核心问题。</div>")

# ---- Section 2 工具调用画像 ----
H.append("<h2>2. 工具调用画像（核心章节）</h2>")

H.append("<h3>2.1 各工具调用次数与成功率</h3>")
H.append("<table><tr><th>run（启动时间）</th><th>search_apis</th><th>search_apis_by_keyword</th><th>get_api_details</th><th>run_code</th><th>该 run 总 tool_use</th><th>submit_and_exit</th><th>submit 报错</th><th>通过数</th></tr>")
for r in PER_RUN:
    H.append(f"<tr><td>{r['run']}</td><td>{r['sa']}</td><td>{r['kw']}</td><td>{r['ga']}</td><td>{r['rc']}</td><td>{r['tot']}</td><td>{r['submit']}</td><td>{r['submit_err']}({pct(r['submit_err'],r['submit'])}%)</td><td>{r['pass']}</td></tr>")
H.append(f"<tr style='font-weight:700;background:#e8e8e8'><td>5-run 合计</td><td>{AGG['sa']}</td><td>{AGG['kw']}</td><td>{AGG['ga']}</td><td>{AGG['rc']}</td><td>32,990</td><td>{AGG['submit']}</td><td>{AGG['submit_err']}({pct(AGG['submit_err'],AGG['submit'])}%)</td><td>24</td></tr>")
H.append("</table>")
H.append("<div class='box'><b>关键观察</b>：<ul>"
  f"<li><b>submit_and_exit 才是调用次数大头</b>：13,699 次，91.77% 报错。模型不是在「检索/执行」，而是在<b>反复尝试退出</b>但每次都因任务未完成/上下文不对被 harness 拒绝。run1/run3 尤其极端（6,009 / 6,984 次，报错率 96%+）。</li>"
  f"<li><b>检索工具成功率尚可</b>：search_apis 加权成功率约 78%（返回真实 API 文档，如 <code>dbFindMemInstByName sim=0.7576</code>、<code>emyBitNet sim=0.9259</code>）；但 <b>get_api_details 成功率仅 32–45%</b>——相当一部分详细查询返回空或报错。</li>"
  f"<li><b>run_code 真实执行成功率约 64%</b>（326/507，deep analysis 口径）；按响应文本口径为 118 成功 / 231 失败。失败主因见 §2.4。</li>"
  "</ul></div>")

H.append("<h3>2.2 每题平均调用次数与分布（极度长尾）</h3>")
H.append(f"<div class='kpi'>")
H.append(f"<div><div class='big'>{PT['calls_mean']}</div>每题平均 tool_use（729 题-会话）</div>")
H.append(f"<div><div class='big'>{PT['calls_median']}</div>每题中位数</div>")
H.append(f"<div><div class='big'>{PT['calls_max']}</div>单题最大值</div>")
H.append(f"<div><div class='big'>{PT['calls_p90']}</div>P90</div>")
H.append(f"</div>")
H.append(f"<div class='box'><b>分布严重右偏</b>：中位数仅 7 次，但均值 45.3、最大 6,772 次、P90 仅 54。<b>绝大多数题调用很少，少数题疯狂调用（主要是 submit_and_exit 死循环）</b>。这意味着「1.9 万次」并非均匀分布于 158 题，而是被<b>极少数陷入死循环的题</b>拉爆——run1 的 max=5,749、run3 的 max=6,772 几乎全是 submit_and_exit 报错循环。这与「多数题不调用工具」并不矛盾，而是同一现象的两面。</div>")
H.append("<div class='chart'>")
H.append(svg_histo([('中位\n7',7),('均值\n45',45),('P90\n54',54),('max\n6772',120)], 300, 200, '#8e44ad'))
H.append("<div style='font-size:12px;max-width:300px'>注：max 6,772 已截断显示为柱高 120（避免压扁其它柱）。真实分布呈极端长尾：~75% 题 tool_use ≤ 中位数附近，&lt;5% 的题贡献了 &gt;50% 的总调用。</div></div>")

H.append("<h3>2.3 调用后是否有「有效结果」——检索到 ≠ 用对</h3>")
H.append(f"<div class='box'><b>检索到了，但基本没用上</b>：get_api_details 在 5-run 中检索到 <b>{RETRIEVED} 个去重 API 名</b>（取最后一段，如 <code>dbCreateLib</code>/<code>emyBitNet</code>/<code>dbOpenCV</code>），但<b>真正出现在后续 run_code 代码 token 里的只有 {OVERLAP} 个</b>（overlap = {pct(OVERLAP,RETRIEVED)}%）。示例重叠 API：<code>dbCreateLib, dbOpenCV, emyDesign, emyTerm, dbCrtRect, MdePlatLocalJobPolicy</code> 等。<br><br>"
  "<b>证据摘引</b>（trace 原文）：get_api_details 返回 <code>{\"api_name\":\"pyAether.emyBitNet\",\"api_type\":\"class\",...getOriginal()->emyBitNet...}</code> 这类真实文档；但紧随其后的 run_code 里模型往往写的是<b>自己猜的 API 名</b>（如 <code>pyScript.filterSignals(...)</code>），结果 <code>AttributeError: module 'pyAether' has no attribute 'filterSignals'</code>。<b>模型「查了文档但没按文档写」</b>，检索与生成脱节。</div>")

H.append("<h3>2.4 run_code 失败分类（写得出 ≠ 跑得通）</h3>")
H.append(f"<p>对 5-run 全部 run_code tool_result 做响应文本扫描（可识别 {RC_TOTAL_PARSED} 条，118 成功 / 231 失败）：</p>")
H.append("<table><tr><th>错误类型</th><th>次数</th><th>说明</th></tr>")
for k,v in sorted(RC_ERR.items(), key=lambda x:-x[1]):
    note = {'NameError':'含 4 次把 MCP 工具名当 Python 函数调用：<code>pyAether_MCP_server__get_api_details is not defined</code>','SyntaxError':'生成的 Python 语法不合法','non-ASCII':'沙箱拒绝非 ASCII 字符（中文注释/字符串）','AttributeError':'调用不存在的 pyAether 属性（猜 API 名）','other':'其它运行期错误','TypeError':'参数/类型错误','ImportError':'导入失败'}.get(k,'')
    H.append(f"<tr><td>{k}</td><td>{v}</td><td>{note}</td></tr>")
H.append("</table>")
H.append("<div class='chart'>")
H.append(svg_bar([(k,v) for k,v in sorted(RC_ERR.items(), key=lambda x:-x[1])], 'run_code 失败错误类型分布', 560, 220, '#e67e22'))
H.append("</div>")
H.append("<div class='key'><b>三条最致命的「写得出≠跑得通」证据</b>：<ul>"
  "<li><b>把工具名当函数</b>（task 027 连续 4 次）：模型在 run_code 里写 <code>pyAether_MCP_server__get_api_details(...)</code>，沙箱报 <code>NameError: name 'pyAether_MCP_server__get_api_details' is not defined</code>，随后触发 <code>max consecutive mistakes reached (3) in yolo mode</code> 被强杀。</li>"
  "<li><b>猜 API 名</b>（task 001）：<code>AttributeError: module 'pyAether' has no attribute 'filterSignals'</code>——没检索到该 API 就直接用。</li>"
  "<li><b>非 ASCII</b>：39 次 <code>Code contains non-ASCII</code>——模型在代码里写中文注释/字符串，沙箱（Python 3.9 + 执行器 ASCII 校验）直接拒绝。</li></ul></div>")

H.append("<h3>2.5 重复调用 / 死循环重试迹象</h3>")
H.append(f"<div class='box'><b>submit_and_exit 死循环是头号症状</b>：13,699 次 submit，12,572 次报错（91.77%）。run1/run3 的单题 max tool_use 达 5,749 / 6,772，几乎全是 submit→报错→再 submit 的循环。<b>真正进入「检索→执行→修错」有效迭代的题极少</b>：<b>729 个题-会话里只有 {PT['tasks_with_rc']} 个（{pct(PT['tasks_with_rc'],PT['n_sessions'])}%）曾经调用过 run_code</b>，中位数 run_code 调用 = 0；{PT['zero_rc']} 个题（{pct(PT['zero_rc'],PT['n_sessions'])}%）<b>一次沙盒执行都没有</b>。<br><br>"
  f"另外 <b>{PT['zero_mcp']} 个题（{pct(PT['zero_mcp'],PT['n_sessions'])}%）从不调用任何 MCP 工具</b>（既不检索也不执行），直接提交空/degenerate 答案。</div>")

H.append("<h3>2.6 prompt 矛盾的影响（指令与环境自相矛盾）</h3>")
H.append("<div class='box'>.17 评测用的系统提示模板 <code>eval_sys_prompt_template_no_sandbox.md</code> 明写「本场景无沙箱可实际执行，内部推演唯一校验」，<b>但 agent 仍调用了 run_code 507 次</b>（沙盒经 dual-nix-tunnel 实际可达，wake327/328/330 实测 <code>2+2=4</code> 通过）——<b>指令说没有沙箱，环境里却有</b>。<br><br>"
  f"<b>trace 证据</b>：在 507 次 run_code 调用中，<b>{CONTRA['hits']} 次（{pct(CONTRA['hits'],CONTRA['total'])}%）</b>其前导 assistant 文本出现了「infer/reason/verify/assume/推测/推演/假设」等措辞——即模型一边说「我推演/假设一下」一边又调用了它「被告知不存在」的沙盒。这表明模型表现出<b>不敢确信执行结果</b>的犹豫：它在「按提示纯推演」与「按环境真执行」之间摇摆，既没有放心地用沙盒闭环校验，也没有真正退化为纯推理，而是反复低效试探。<br><br>"
  "<b>结论</b>：prompt 矛盾没有让模型完全放弃工具（它确实调了 507 次 run_code），但显著抑制了「执行→看结果→修错」的闭环——模型不敢信任执行结果，迭代次数极低（见 §3.4）。</div>")

# ---- Section 3 失败归因 ----
H.append("<h2>3. 失败归因（从 trace 自行提炼）</h2>")
H.append("<h3>3.1 790 题-运行失败分类总览</h3>")
H.append("<div class='chart'>")
H.append(svg_pie(CAT, CAT_COLORS))
H.append("</div>")
H.append("<table><tr><th>类别</th><th>题-运行数</th><th>占比</th><th>含义</th></tr>")
for key,label,v in CAT:
    H.append(f"<tr><td>{key}</td><td>{v}</td><td>{pct(v,N_TASK_RUNS)}%</td><td>{label}</td></tr>")
H.append(f"<tr style='font-weight:700;background:#e8e8e8'><td>合计</td><td>{N_TASK_RUNS}</td><td>100%</td><td></td></tr>")
H.append("</table>")
H.append(f"<div class='key'><b>头号失败模式</b>：<b>C5_degenerate_pass = 479/790 = 60.6%</b>——模型最终提交的代码就是 Python 空操作 <code>pass</code>（completion 退化检测：<code>gen_fail_subtype=degenerate_pass</code> 共 479 条，<code>has_code</code> 仅 10 条）。即<b>六成的尝试根本没写出有效代码就放弃了</b>。这与 §2.5 的 submit_and_exit 死循环同源：模型早早放弃，spam 退出工具。</div>")

H.append("<h3>3.2 检索到 ≠ 用对</h3>")
H.append(f"<div class='box'>get_api_details 检索到 {RETRIEVED} 个去重 API，仅 {OVERLAP} 个进入后续代码（{pct(OVERLAP,RETRIEVED)}%）。大量证据显示模型<b>查完文档仍用猜的 API 名</b>（<code>filterSignals</code> 等），检索结果未转化为生成依据。该现象对应 §3.1 的 C3_code_runtime（122 条，15.4%）中的 AttributeError 子类。</div>")

H.append("<h3>3.3 写得出 ≠ 跑得通</h3>")
H.append(f"<div class='box'>真正调用 run_code 的题里，失败率约 66%（231/349 可识别）。失败结构：NameError 66 / SyntaxError 58 / non-ASCII 39 / AttributeError 24 / 其它 52。<b>non-ASCII（39 次）是纯环境/习惯问题</b>，完全可修；<b>把 MCP 工具名当 Python 函数</b>（NameError 含 4 次 <code>pyAether_MCP_server__...</code>）是工具协议理解错误。</div>")

H.append("<h3>3.4 跑得通 ≠ 判得过 + 迭代次数</h3>")
H.append(f"<div class='box'>即使 run_code 执行成功（<code>The code execution was successful.</code>），最终 check 仍多数判 fail——<b>C3_code_assert（断言/逻辑失败）只有 14 条</b>，说明<b>绝大多数题根本走不到「代码跑通但断言失败」这一步</b>，而是更早就断了（degenerate 放弃 / 语法错 / 运行期错 / 超时）。<br><br>"
  f"<b>迭代次数极低（D6）</b>：通过题平均迭代 {ITS['pass_mean']} 轮，失败题平均 {ITS['fail_mean']} 轮——<b>两者几乎相同且都很低</b>，模型基本不利用执行反馈做「跑→看错→改」闭环。<br><br>"
  f"<b>「原地打转」证据</b>：失败题平均耗时 {WALL['fail_mean']}s，反而<b>比通过题 {WALL['pass_mean']}s 更长</b>——多出的时间并没有用于有效迭代，而是消耗在 submit_and_exit 死循环 / yolo-mode 连错被杀上。<b>run_commands 6,401 次（用户粗扫口径）里相当一部分是这种原地打转</b>，而非有效迭代。</div>")

H.append("<h3>3.5 失败漏斗（检索→用对→跑通→判过）</h3>")
H.append("<div class='chart'>")
H.append(svg_funnel([
  ('有 MCP 调用', PT['tasks_with_mcp'], '#2980b9'),
  ('有 run_code 执行', PT['tasks_with_rc'], '#27ae60'),
  ('run_code 成功(估)', 72*0.64, '#f39c12'),
  ('check 判过', 24, '#c0392b'),
], 560, 240))
H.append("</div>")
H.append("<div class='box'>漏斗口径（729 题-会话）：549 题用过 MCP 检索 → 仅 72 题真正执行过 run_code → 其中约 64% 即 ~46 题执行成功 → 最终仅 24 题-运行 check 判过。<b>最大流失在「检索→执行」这一步</b>（549→72，流失 87%）：模型查了文档却极少动手在沙盒里写代码验证。</div>")

H.append("<h3>3.6 通过题的特征（pass 是「碰运气」还是「真会」）</h3>")
H.append(f"<div class='box'><b>union pass = {UNION_PASS}/158 = {pct(UNION_PASS,N_TASKS)}%</b>（至少 1 个 run 通过的题），但 Pass@1 仅 3.04%。<b>分布：{UNION_DIST[1]} 个题只在 1 个 run 通过，{UNION_DIST.get(2,0)} 个题在 2 个 run 通过，没有任何题在 ≥3 个 run 通过。</b>这意味着<b>通过本质上是随机/碰运气</b>：模型偶尔对某些简单题（如 003/010/050/100/153）蒙对一次，但无法稳定复现。<b>3.04% 不是「能力上限被工具锁死」，而是「模型对绝大多数题没有稳定解题能力」</b>。</div>")

# ---- Section 4 图表汇总 ----
H.append("<h2>4. 图表汇总</h2>")
H.append("<div class='chart'>")
H.append(svg_bar([(r['run'], r['tot']) for r in PER_RUN], '各 run 总 tool_use 次数', 560, 220, '#2980b9'))
H.append(svg_bar([(r['run'], r['submit']) for r in PER_RUN], '各 run submit_and_exit 次数', 560, 220, '#c0392b'))
H.append("</div>")
H.append("<div class='chart'>")
H.append(svg_pie(CAT, CAT_COLORS))
H.append(svg_bar([(k,v) for k,v in sorted(RC_ERR.items(), key=lambda x:-x[1])], 'run_code 错误类型', 560, 220, '#e67e22'))
H.append("</div>")

# ---- Section 5 提分意见 ----
H.append("<h2>5. 提分意见（按 ROI 排序）</h2>")
H.append("<div class='box'>每条写清：改什么 / 依据 / 预期收益（保守） / 成本 / 优先级。</div>")

recs = [
  ('P0','🔴','#c0392b','消除 degenerate「pass」提交 + submit_and_exit 死循环',
   '改 prompt + SFT',
   '60.6% 题-运行（479/790）提交空 <code>pass</code>；submit_and_exit 13,699 次/91.77% 报错（§2.1/§2.5/§3.1）。模型早早放弃、spam 退出。',
   '保守 +8~15pp：把 479 条 degenerate 中相当一部分转为「至少写出可执行代码」。即便代码不正确，也从「0 分」变为「有机会被判」',
   '低-中：prompt 改造（禁止单独提交 bare pass、要求先 write_file 再 submit）≈2 人时；SFT 注入「完整解题轨迹」数据 ≈2 GPU·日',
   '若只做一件事，做这件。'),
  ('P0','🔴','#c0392b','修复 non-ASCII 拒绝（中文注释/字符串）',
   '改 prompt + SFT',
   'run_code 中 39 次 <code>Code contains non-ASCII</code>（§2.4/§3.3），纯环境/习惯问题，沙箱 Python 3.9 拒绝非 ASCII。',
   '保守 +1~3pp：直接回收这部分执行失败',
   '极低：prompt 加「代码与注释必须纯 ASCII/英文」+ SFT 样本 ≈0.5 人时 + 数据',
   '可与 P0-1 同批改。'),
  ('P1','🟠','#e67e22','教对工具协议：MCP 工具名 ≠ Python 函数',
   '改 SFT + tool schema',
   'NameError 66 次，含把 <code>pyAether_MCP_server__get_api_details</code> 当 Python 函数调用（§2.4）；触发 yolo-mode 连错被杀。模型分不清「调工具」与「写代码里调函数」的边界。',
   '保守 +2~5pp：减少运行期 NameError + 避免连错被杀',
   '中：SFT agentic 轨迹（明确展示 tool-call block vs code 内函数调用的区别）≈2 GPU·日',
   ''),
  ('P1','🟠','#e67e22','缩小「检索到→用对」缺口',
   '改 SFT',
   '检索到 333 个 API 仅 19 个进代码（5.7%）；模型查完文档仍用猜的 API 名（§2.3/§3.2）。',
   '保守 +2~4pp：让检索结果真正指导生成',
   '中：SFT「检索→按返回 API 名写代码」轨迹 ≈2 GPU·日',
   ''),
  ('P1','🟠','#e67e22','修正「无沙箱」prompt 矛盾，启用执行反馈闭环',
   '改 prompt（评测环境）',
   'no_sandbox 模板说无沙箱，但 run_code 实际可用（507 次调用，46.5% 前导「推演/假设」措辞，§2.6）；迭代仅 2 轮（§3.4）。',
   '保守 +1~3pp：模型敢信任执行结果→多轮修错',
   '极低：换用 sandbox-available 模板（36.15 重测已在做）≈0.5 人时',
   '即 15:4x 用户令的 36.15 重测方向。'),
  ('P2','🟡','#f39c12','建立「执行→看错→改」迭代闭环（RL）',
   '训练（RL）',
   '通过/失败题迭代均 ~2 轮（§3.4 D6）；失败题耗时更长却是原地打转。模型不会用执行反馈。',
   '保守 +3~6pp：但需先有 P0-1（否则没代码可迭代）',
   '高：RLVR-GRPO 带沙盒执行反馈，≈数 GPU·周（已在 R2 预演）',
   '依赖 P0/P1 先落地。'),
  ('P2','🟡','#f39c12','get_api_details 成功率提升（32–45%→更高）',
   '改 RAG / tool schema',
   'get_api_details 成功率仅 32–45%（§2.1），部分查询返回空。',
   '保守 +1~2pp：检索更准→用对概率升',
   '中：RAG 服务端调优 / 查询改写 ≈1 人时 + 调参',
   ''),
]
H.append("<table><tr><th>优先级</th><th>改什么</th><th>依据（trace 证据）</th><th>预期收益（保守）</th><th>成本</th><th>备注</th></tr>")
for p,emoji,col,what,how,basis,gain,cost,note in recs:
    H.append(f"<tr style='background:{col}11'><td><b style='color:{col}'>{p}</b></td><td><b>{what}</b><br><small>方式：{how}</small></td><td>{basis}</td><td>{gain}</td><td>{cost}</td><td>{note}</td></tr>")
H.append("</table>")

H.append("<div class='key' style='margin-top:18px'><h3 style='margin-top:0'>如果只做一件事，做哪件？</h3><b>P0-1：消除 degenerate「pass」提交 + submit_and_exit 死循环（改 prompt + SFT）。</b><br>理由：60.6% 的题-运行根本没写出有效代码就放弃了。在模型「不动手写代码」的前提下，<b>无论检索多准、沙盒多通、迭代多少轮都无济于事</b>——因为连被评判的对象都不存在。先把这 60.6% 的「放弃」行为止住（prompt 强制必须产出可执行代码 + SFT 教「完整解题轨迹」），后续的检索→执行→迭代改进才有发挥作用的对象。这是 ROI 最高、且是其它所有改进的<b>前置条件</b>。</div>")

H.append("<h3>5.1 综合判断：3.04% 主要卡在哪一层？</h3>")
H.append("<div class='box'><b>主要卡在「生成意愿/协议」层，而非「检索」或「执行环境」层。</b><br><br>"
  "<ul>"
  "<li><b>环境是齐的</b>（意见 A 成立，wake482 已裁决）：RAG 检索可用（search_apis 成功率 ~78%）、沙盒可用（run_code 64% 成功、<code>2+2=4</code> 实测通）、工具已注册（4 个 MCP + cline 内建，enable_tools=true）。</li>"
  "<li><b>工具确实用了上万次</b>，但<b>绝大部分调用是 submit_and_exit 死循环（13,699 次/91.77% 报错）</b>，真正「检索→执行→修错」的有效调用极少（仅 9.9% 的题执行过 run_code）。</li>"
  "<li><b>最大断层在「动手写代码」这一步</b>：60.6% 退化提交 <code>pass</code>；检索到的 333 个 API 仅 19 个进代码；通过题迭代仅 2 轮且 22 个 union-pass 题中 20 个只蒙对 1 次。</li>"
  "</ul><br>"
  "<b>一句话</b>：3.04% 不是「工具/环境缺失」（那是意见 B，已被 trace 否决），而是「<b>模型有了工具却不会、也不敢稳定地用它把题做完</b>」——查了不照着写、写了跑不通、跑通了不复现、没跑通就 spam 退出。这是<b>能力 + 协议</b>问题，正是 SFT（教完整轨迹）+ prompt（强制产出 + 纯 ASCII + 信任沙盒）+ RL（教执行反馈闭环）要解决的。</div>")

H.append("<h3>5.2 数据缺口（TODO）</h3>")
H.append("<div class='box'><ul>"
  "<li><b>token 用量</b>：enrich 脚本从 messages.json 取 <code>usage</code> 字段，但本批 trace 格式未携带 token 统计（tokens 字段=0），无法给出「通过/失败题 token 消耗对比」。<code>TODO</code>：若需该指标，需从 serve 端日志补抓。</li>"
  "<li><b>run_code 错误精确计数</b>：响应文本扫描可识别 349 条（118 成功/231 失败），另有约 158 条 tool_result 内容格式未被正则命中（计入「未分类」）。<code>TODO</code>：可改用结构化 <code>structuredContent</code> 字段精确分类。</li>"
  "<li><b>run_commands 口径</b>：用户引用的 6,401 次 run_commands 为字符串粗扫口径；本批 trace 的 run_commands 多为 cline 内建（读文件/编辑等），非 MCP 沙盒执行，未纳入 MCP 工具画像。<code>TODO</code>：如需单独画像 run_commands，可扩展 toolcount 脚本。</li>"
  "</ul></div>")

H.append("<hr><div style='font-size:12px;color:#888;margin-top:20px'>")
H.append("<b>报告版本</b>：v2（2026-11-14）· <b>数据可复算</b>：trace 根 <code>~/eda_code_eval/2026_1113_*/trace/</code> + 脚本 <code>run/baize_posttrain_trace_{toolcount,deep_analysis}.py</code> + <code>run/rca_baseline_{aggregate,enrich}.py</code> · <b>生成器</b>：<code>run/rca_v2_report_gen.py</code><br>")
H.append("<b>红线遵守</b>：158 任务未进任何训练集（污染隔离）；数字均来自落盘 trace/eval 文件可复算；无 script、无外链、单文件自包含。</div>")
H.append("</body></html>")

html = "\n".join(H)
dest = "/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports/report_posttrain_pyaether_rca_v2_zh.html"
open(dest, "w", encoding="utf-8").write(html)
print("WROTE", dest, "bytes=", len(html.encode('utf-8')))
# checks
assert "<script" not in html, "CONTAINS SCRIPT"
assert "http://" not in html and "https://" not in html, "CONTAINS EXTERNAL LINK"
print("CHECKS: 0 script OK, 0 external link OK, inline SVG count=", html.count("<svg"))
