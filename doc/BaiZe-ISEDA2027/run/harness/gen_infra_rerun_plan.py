#!/usr/bin/env python3
"""Generate reports/report_harness_infra_rerun_plan_zh.html from infra_rerun_classify_7way.json.

Self-contained Chinese HTML, 0 script, 0 external links (per report discipline).
"""
import json, os, html

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "swebench_verified_full", "infra_rerun_classify_7way.json")
# BASE = run/harness  ->  os.path.dirname(BASE) = run  ->  run/reports
OUT = os.path.join(os.path.dirname(BASE), "reports",
                   "report_harness_infra_rerun_plan_zh.html")
OUT = os.path.normpath(OUT)

d = json.load(open(SRC))
routes = d["routes"]
ORDER = ["cline-patched", "codex", "opencode", "claude-code", "pi", "hermes", "deepseek-harness"]
LABEL = {
    "cline-patched": "cline", "codex": "codex", "opencode": "opencode",
    "claude-code": "claude-code", "pi": "pi", "hermes": "hermes",
    "deepseek-harness": "deepseek",
}

# rerun order: cline first, rest by infra count desc
rest = [r for r in ORDER if r != "cline-patched"]
rest.sort(key=lambda r: routes[r]["counts"].get("infra_failed", 0), reverse=True)
rerun_order = ["cline-patched"] + rest


def esc(s):
    return html.escape(str(s))


def trunc(s, n=160):
    s = s or ""
    return esc(s[-n:]) if len(s) > n else esc(s)


# --- build summary rows ---
sum_rows = ""
grand_infra = grand_abil = grand_pend = grand_peval = grand_rerun = 0
for r in ORDER:
    rd = routes[r]
    c = rd["counts"]
    infra = c.get("infra_failed", 0)
    abil = c.get("ability_failed", 0)
    pend = c.get("pending", 0)
    peval = c.get("pending_eval", 0)
    rerun = infra + pend
    grand_infra += infra; grand_abil += abil; grand_pend += pend
    grand_peval += peval; grand_rerun += rerun
    pct = "%.1f%%" % (rd["resolved"] / 500 * 100) if rd["eval_n"] else "?"
    sum_rows += (
        "<tr><td><strong>%s</strong></td><td>%d</td><td class='pass'>%d</td>"
        "<td>%s</td><td class='fail'>%d</td><td class='warn'>%d</td>"
        "<td>%d</td><td>%d</td><td class='key'>%d</td></tr>" % (
            esc(LABEL[r]), rd["eval_n"], rd["resolved"], pct,
            infra, abil, pend, peval, rerun))
sum_rows += (
    "<tr style='font-weight:bold;background:#d5dbdb'><td>合计</td><td>-</td><td>-</td>"
    "<td>-</td><td class='fail'>%d</td><td>%d</td><td>%d</td>"
    "<td>%d</td><td class='key'>%d</td></tr>" % (
        grand_infra, grand_abil, grand_pend, grand_peval, grand_rerun))

# --- rerun order block ---
rerun_rows = ""
for i, r in enumerate(rerun_order, 1):
    rd = routes[r]
    c = rd["counts"]
    infra = c.get("infra_failed", 0)
    pend = c.get("pending", 0)
    rerun_rows += "<tr><td>%d</td><td><strong>%s</strong></td><td class='fail'>%d</td><td>%d</td><td class='key'>%d</td></tr>" % (
        i, esc(LABEL[r]), infra, pend, infra + pend)


def detail_table(items, bucket_label):
    """Render a per-case table for one bucket."""
    if not items:
        return "<p class='small'>(无)</p>"
    rows = ""
    for x in items:
        tail = (x.get("stdout_tail", "") + " | " + x.get("stderr_tail", "")).strip(" |")
        rows += (
            "<tr><td>%s</td><td>%s</td><td>%s</td><td>%.0f</td><td>%s</td>"
            "<td>%s</td><td class='small'>%s</td></tr>" % (
                esc(x["instance_id"]), esc(x.get("reason", "")),
                esc(x.get("classification", "")), x.get("wall_s", 0) or 0,
                esc(x.get("returncode")), "Y" if x.get("quota_blocked") else ("T" if x.get("timeout") else ""),
                trunc(tail, 120)))
    return (
        "<table class='detail'><thead><tr><th>instance_id</th><th>归因</th>"
        "<th>progress分类</th><th>wall_s</th><th>rc</th><th>flag</th>"
        "<th>tail摘要</th></tr></thead><tbody>%s</tbody></table>" % rows)


detail_sections = ""
for r in rerun_order:
    rd = routes[r]
    bk = rd["buckets"]
    infra_items = bk.get("infra_failed", [])
    abil_items = bk.get("ability_failed", [])
    pend_items = bk.get("pending", [])
    peval_items = bk.get("pending_eval", [])
    detail_sections += "<h3>%s（%s）</h3>" % (esc(LABEL[r]), esc(r))
    detail_sections += "<p class='small'>eval_n=%d · resolved=%d · infra=%d · ability=%d · pending=%d · pending_eval=%d</p>" % (
        rd["eval_n"], rd["resolved"], len(infra_items), len(abil_items),
        len(pend_items), len(peval_items))
    detail_sections += "<h4>🔴 infra_failed（需重跑）· %d 题</h4>" % len(infra_items)
    detail_sections += detail_table(infra_items, "infra")
    detail_sections += "<h4>🔵 ability_failed（不重跑·能力）· %d 题</h4>" % len(abil_items)
    detail_sections += detail_table(abil_items[:30], "ability")
    if len(abil_items) > 30:
        detail_sections += "<p class='small'>…（仅列前 30 题，余 %d 题为 real-patch 测试失败）</p>" % (len(abil_items) - 30)
    detail_sections += "<h4>🟡 pending（需 transcript·空 patch 重跑）· %d 题</h4>" % len(pend_items)
    detail_sections += detail_table(pend_items, "pending")
    if peval_items:
        detail_sections += "<h4>⚪ pending_eval（待评测·非重跑）· %d 题</h4>" % len(peval_items)
        detail_sections += detail_table(peval_items, "peval")

HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>harness 7-way infra 排查与夜间重跑计划 · SWE-bench Verified</title>
<style>
body{font-family:"Noto Sans CJK SC","Microsoft YaHei",sans-serif;max-width:1180px;margin:0 auto;padding:24px;background:#f8f9fa;color:#2c3e50;line-height:1.7}
h1{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:12px}
h2{color:#1a5276;margin-top:34px;border-left:6px solid #2980b9;padding-left:12px}
h3{color:#2874a6;margin-top:26px;border-bottom:1px solid #d5dbdb;padding-bottom:6px}
h4{color:#2c3e50;margin-top:18px}
table{border-collapse:collapse;width:100%;margin:14px 0;font-size:0.92em}
th,td{border:1px solid #ccc;padding:6px 10px;text-align:left;vertical-align:top}
th{background:#2980b9;color:#fff}
tr:nth-child(even){background:#eef4f9}
table.detail{font-size:0.82em}
table.detail td{word-break:break-all;max-width:280px}
.pass{color:#27ae60;font-weight:bold}.fail{color:#e74c3c;font-weight:bold}.warn{color:#e67e22;font-weight:bold}
.big{font-size:1.3em;font-weight:bold}
.key{background:#fef9e7;font-weight:bold}
.info{background:#ebf5fb;border-left:5px solid #3498db;padding:12px 16px;margin:16px 0}
.crit{background:#fdedec;border-left:5px solid #e74c3c;padding:12px 16px;margin:16px 0}
.ok{background:#eafaf1;border-left:5px solid #27ae60;padding:12px 16px;margin:16px 0}
.small{font-size:0.82em;color:#7f8c8d}
code{background:#f0f0f0;padding:2px 6px;border-radius:3px;font-size:0.9em}
</style>
</head>
<body>
<h1>harness 7-way infra 排查与夜间重跑计划</h1>
<div class="info">
<p><strong>评测</strong>：SWE-bench Verified 500 题 · 7 路横评　|　<strong>基座</strong>：glm-5.3-flash　|　<strong>生成</strong>：2026-11-23</p>
<p><strong>背景</strong>：cline 的 Pass% 被 93 个空 patch 拖低，其中多数是基础设施故障（Token 额度 429 / 超时 / 上游 5xx / 鉴权），但最终 eval 的 <code>infra_or_quota</code> 却记为 0 —— infra 失败被并进「能力失败」桶。本报告对 7 路全部未 resolved 的 case 做系统分类，列出需重跑的 infra/pending 题与不重跑的 ability 题。</p>
<p><strong>数据源</strong>：<code>eval_glm53_*.json</code>（resolved/failed/empty_patch/infra_or_quota）＋ <code>progress_glm53_*.json</code>（逐题 wall_s/returncode/quota_blocked/timeout/stdout·stderr_tail）＋ <code>predictions_glm53/*.json</code>（model_patch）</p>
<p><strong>分类脚本</strong>：<code>run/harness/swebench_verified_full/infra_rerun_classify_7way.py</code>（复用并推广 <code>c2_cline_R2233.py</code> 框架）</p>
</div>
<h2>一、分类口径</h2>
<table>
<thead><tr><th>桶</th><th>定义</th><th>是否重跑</th></tr></thead>
<tbody>
<tr><td class="fail">infra_failed</td><td>空（或 real）patch + infra 信号：quota_blocked/timeout 标志位、429/额度/rate-limit、上游 500/502/503/504、鉴权 401/403/forbidden/适配器、超时关键字或 wall&ge;1799s</td><td class="key">是（重跑）</td></tr>
<tr><td>ability_failed</td><td>确实产出了 real patch，但 apply+test 失败（eval <code>failed</code> 集）——这是能力，不是 infra</td><td>否（🚫 不重跑，属造假风险）</td></tr>
<tr><td class="warn">pending</td><td>空 patch 且无明确 infra 信号（rc=0 干净退出、或非 infra 错误）——需 transcript 级复查；空 patch 重跑成本低，一并重跑</td><td class="key">是（重跑）</td></tr>
<tr><td>pending_eval</td><td>real patch 已产出但尚未评测（不在 resolved/failed/empty）——需 eval，非 re-predict</td><td>否（需 eval 而非重跑）</td></tr>
</tbody>
</table>
<div class="crit"><p><strong>红线</strong>：429/5xx/超时/鉴权 = infra（非能力）。real-patch-tests-fail = 能力。空 patch + 无 infra 信号 = pending（需 transcript）。重跑只动 infra + pending，🚫 不碰 ability。</p></div>
<h2>二、7 路总览</h2>
<table>
<thead><tr><th>Harness</th><th>eval_n</th><th>resolved</th><th>Pass%</th><th>infra_failed</th><th>ability_failed</th><th>pending</th><th>pending_eval</th><th>重跑合计</th></tr></thead>
<tbody>
__SUM_ROWS__
</tbody>
</table>
<p class="small">Pass% = resolved/500（分母恒 500）。重跑合计 = infra_failed + pending。pending_eval 不计入重跑（需 eval）。</p>
<h2>三、重跑顺序与窗口策略</h2>
<h3>3.1 重跑顺序</h3>
<p>用户令：「从 cline 起，其余按 infra 数量降序」。</p>
<table>
<thead><tr><th>#</th><th>Harness</th><th>infra</th><th>pending</th><th>重跑合计</th></tr></thead>
<tbody>
__RERUN_ROWS__
</tbody>
</table>
<h3>3.2 时间窗：每晚 21:00 – 次日 09:00（12 小时）</h3>
<div class="info">
<p><strong>窗口判定</strong>：<code>H=$(date +%H); [ "$H" -ge 21 ] || [ "$H" -lt 9 ] &amp;&amp; echo 窗口内 || echo 窗口外</code></p>
<ul>
<li><strong>窗口内（21:00–09:00）</strong>：启动/继续重跑 predict → 复核 → eval → 合并回 <code>eval_glm53_*.json</code> → REGEN 7way 报告。</li>
<li><strong>窗口外（09:00–21:00）</strong>：只 park——不启动新 predict/eval，队列存着等下一个 21:00。</li>
<li><strong>原因</strong>：避开 glm-5.3-flash 网关白天使用高峰（额度 429 正是高峰产物）+ 白天 CPU 争抢。</li>
</ul>
</div>
<h3>3.3 硬护栏（夜间不放松）</h3>
<ul>
<li>docker eval：<code>--memory 128g --memory-swap 128g --cpus 16</code>（swebench_guarded_eval.py monkey-patch）</li>
<li>宿主 predict：<code>ulimit -v 209715200</code>（200GiB）+ <code>nice -n 19</code> <code>ionice -c3</code> + <code>OMP_NUM_THREADS&le;8</code></li>
<li><code>harness_resource_guard.sh</code>（PID931671）常开；pretrain step &le;7.4s 越界即降载；load 闸 &le;120</li>
<li>并发克制：夜间重跑限并发 &le;2 路；额度 429 重试带指数退避（2/4/8/16s，上限 4 次），不裸刷网关</li>
<li>只动本线文件；不碰 pretrain/data/vision/zhulong</li>
</ul>
<h2>四、逐路逐题清单</h2>
__DETAIL_SECTIONS__
<h2>五、每晚进度（滚动更新）</h2>
<div class="ok">
<p><strong>2026-11-23（首日 · 夜间窗口 LIVE）</strong>：Step 1 全量 7 路 infra 排查完成（本报告）。重跑队列总计 <strong>__GRAND_RERUN__ 题</strong>（infra=__GRAND_INFRA__ + pending=__GRAND_PEND__），顺序见 §3.1。</p>
<p><strong>重跑进度</strong>：21:55 orchestrator（<code>rerun_infra_verified.py</code>）启动，首路 cline-patched 95 题预测中（gw_proxy 9090/9091/9092 三代理已修复启动，agent 真正连上 API、产非空 patch）。预计速率 ~7min/题，95 题约 11h，可容于 12h 窗口。窗口结束 09:00 自动 REGEN 7way 报告 + 停止。</p>
<p class="small">每晚窗口结束后更新本节：已回收 X 题 / 7way 报告 REGEN 状态 / MEMORY 心跳「infra 重跑：已回收 X 题」。</p>
</div>
<hr>
<p class="small">
分析脚本：<code>run/harness/swebench_verified_full/infra_rerun_classify_7way.py</code>　|　
生成器：<code>run/harness/gen_infra_rerun_plan.py</code>　|　
JSON：<code>run/harness/swebench_verified_full/infra_rerun_classify_7way.json</code><br>
生成时间：2026-11-23 · harness 线（夜间重跑计划 · Step 1 交付）。
</p>
</body>
</html>"""

HTML = (HTML
        .replace("__SUM_ROWS__", sum_rows)
        .replace("__RERUN_ROWS__", rerun_rows)
        .replace("__DETAIL_SECTIONS__", detail_sections)
        .replace("__GRAND_RERUN__", str(grand_rerun))
        .replace("__GRAND_INFRA__", str(grand_infra))
        .replace("__GRAND_PEND__", str(grand_pend)))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(HTML)
print("Written:", OUT, "(%d bytes)" % len(HTML))



