#!/usr/bin/env python3
"""gen_infra_rerun_plan.py — Generate report_harness_infra_rerun_plan_zh.html

2026-11-23 用户令·交付物①: 各线 infra/ability/待定 三列清单 + 重跑顺序 + 窗口策略 + 每晚进度。
Reads infra_rerun_classify_7way.json (current state) + original snapshot for progress comparison.

Output: reports/report_harness_infra_rerun_plan_zh.html (self-contained, 0 script, 0 外链)
"""
import json, os, time, html
from pathlib import Path

HERE = Path(__file__).resolve().parent
VF = HERE / "swebench_verified_full"
CLASSIFY_JSON = VF / "infra_rerun_classify_7way.json"
REPORTS = HERE.parent.parent / "reports"
OUT = REPORTS / "report_harness_infra_rerun_plan_zh.html"

# Original classification snapshot (pre-rerun, 2026-11-23) for progress comparison
ORIG = {
    "cline-patched":     {"resolved": 303, "infra": 68,  "pending": 27,  "ability": 102, "rerun": 95},
    "codex":             {"resolved": 115, "infra": 251, "pending": 78,  "ability": 55,  "rerun": 329},
    "deepseek-harness":  {"resolved": 195, "infra": 87,  "pending": 178, "ability": 40,  "rerun": 265},
    "pi":                {"resolved": 247, "infra": 15,  "pending": 144, "ability": 94,  "rerun": 159},
    "claude-code":       {"resolved": 295, "infra": 19,  "pending": 122, "ability": 64,  "rerun": 141},
    "hermes":            {"resolved": 444, "infra": 5,   "pending": 5,   "ability": 46,  "rerun": 10},
    "opencode":          {"resolved": 415, "infra": 1,   "pending": 0,   "ability": 84,  "rerun": 1},
}

RERUN_ORDER = ["cline-patched", "codex", "deepseek-harness", "claude-code",
               "pi", "hermes", "opencode"]

DISPLAY = {"cline-patched": "cline", "deepseek-harness": "deepseek",
           "claude-code": "claude-code", "opencode": "opencode",
           "codex": "codex", "pi": "pi", "hermes": "hermes"}


def disp(r):
    return DISPLAY.get(r, r)


def esc(s):
    return html.escape(str(s))


def shorten(s, n=120):
    s = s.replace("\n", " ").strip()
    return s[:n] + "…" if len(s) > n else s


def load_data():
    return json.loads(CLASSIFY_JSON.read_text())


def case_rows(cases, max_show=50):
    out = []
    for c in cases[:max_show]:
        iid = esc(c["instance_id"])
        wall = c.get("wall_s", 0) or 0
        rc = c.get("returncode", "")
        qb = "是" if c.get("quota_blocked") else ""
        to = "是" if c.get("timeout") else ""
        mpl = c.get("model_patch_len", 0) or 0
        reason = esc(c.get("reason", ""))
        tail = esc(shorten(c.get("stdout_tail", "") + " | " + c.get("stderr_tail", ""), 100))
        out.append(f'<tr><td>{iid}</td><td>{wall:.0f}s</td><td>{rc}</td>'
                   f'<td>{qb}</td><td>{to}</td><td>{mpl}</td>'
                   f'<td>{reason}</td><td class="tail">{tail}</td></tr>')
    if len(cases) > max_show:
        out.append(f'<tr><td colspan="8" class="more">… 还有 {len(cases) - max_show} 题，详见 JSON</td></tr>')
    return "\n".join(out)


def bucket_section(title, cls, cases):
    n = len(cases)
    icon = "🔴" if "infra" in cls else ("🟢" if "ability" in cls else "🟡")
    open_attr = "open" if cls == "infra-failed" and n > 0 else ""
    return f'''<details class="bucket {cls}" {open_attr}>
<summary>{icon} {title}（{n} 题）</summary>
<table class="case-table">
<tr><th>instance_id</th><th>wall</th><th>rc</th><th>quota</th><th>timeout</th><th>patch_len</th><th>归因</th><th>tail 摘要</th></tr>
{case_rows(cases)}
</table>
</details>'''


def build_route_section(route, rd, orig):
    buckets = rd.get("buckets", {})
    counts = rd.get("counts", {})
    cur_resolved = rd.get("resolved", 0)
    recovered = cur_resolved - orig["resolved"]
    infra = counts.get("infra_failed", 0)
    ability = counts.get("ability_failed", 0)
    pend = counts.get("pending", 0)
    peval = counts.get("pending_eval", 0)
    rerun_cur = infra + pend

    summary = f'''<table class="summary-table">
<tr><th>指标</th><th>重跑前(11-23)</th><th>当前</th><th>变化</th></tr>
<tr><td>resolved</td><td>{orig["resolved"]}</td><td>{cur_resolved}</td><td class="{'pos' if recovered > 0 else ''}">{'+' if recovered > 0 else ''}{recovered}</td></tr>
<tr><td>infra_failed (需重跑)</td><td>{orig["infra"]}</td><td>{infra}</td><td>{infra - orig["infra"]}</td></tr>
<tr><td>ability_failed (不重跑)</td><td>{orig["ability"]}</td><td>{ability}</td><td>{ability - orig["ability"]}</td></tr>
<tr><td>pending (需transcript)</td><td>{orig["pending"]}</td><td>{pend}</td><td>{pend - orig["pending"]}</td></tr>
<tr><td>待评测 (real patch未eval)</td><td>—</td><td>{peval}</td><td></td></tr>
<tr><td><b>重跑目标合计</b></td><td><b>{orig["rerun"]}</b></td><td><b>{rerun_cur}</b></td><td></td></tr>
</table>'''

    peval_section = bucket_section("待评测（real patch 尚未 eval）", "pending-eval", buckets.get("pending_eval", [])) if peval else ""

    return f'''<div class="route-card" id="route-{esc(route)}">
<h3>{esc(disp(route))} <span class="route-code">({esc(route)})</span></h3>
{summary}
<div class="buckets">
{bucket_section("Infra 失败（需重跑）", "infra-failed", buckets.get("infra_failed", []))}
{bucket_section("能力失败（不重跑）", "ability-failed", buckets.get("ability_failed", []))}
{bucket_section("待定（空 patch 无 infra 信号·需 transcript）", "pending", buckets.get("pending", []))}
{peval_section}
</div>
</div>'''



def main():
    data = load_data()
    routes = data["routes"]
    gen_ts = time.strftime("%Y-%m-%d %H:%M:%S")

    # Overview table rows
    overview_rows = []
    for route in RERUN_ORDER:
        rd = routes[route]
        orig = ORIG[route]
        c = rd["counts"]
        infra = c.get("infra_failed", 0)
        pend = c.get("pending", 0)
        ability = c.get("ability_failed", 0)
        peval = c.get("pending_eval", 0)
        rerun_cur = infra + pend
        recovered = rd["resolved"] - orig["resolved"]
        if rerun_cur == 0 and route != "cline-patched":
            status = "✅ 完成"
        elif route == "cline-patched":
            status = "🔄 重跑中"
        else:
            status = "⏳ 排队"
        overview_rows.append(f'<tr><td class="rt">{esc(disp(route))}</td>'
            f'<td>{rd.get("eval_n", 0)}</td><td>{rd["resolved"]}</td>'
            f'<td>{orig["resolved"]}</td><td class="pos">+{recovered}</td>'
            f'<td class="infra-cell">{infra}</td><td class="ability-cell">{ability}</td>'
            f'<td class="pending-cell">{pend}</td><td>{peval}</td>'
            f'<td><b>{rerun_cur}</b></td><td>{orig["rerun"]}</td><td>{status}</td></tr>')

    # Rerun order rows
    order_items = []
    for i, route in enumerate(RERUN_ORDER):
        rd = routes[route]; orig = ORIG[route]; c = rd["counts"]
        rerun_cur = c.get("infra_failed", 0) + c.get("pending", 0)
        recovered = rd["resolved"] - orig["resolved"]
        if route == "cline-patched":
            note = f"🔄 重跑中 · 已回收 {recovered} 题 · 剩余 {rerun_cur} 题待重跑"
        elif rerun_cur == 0:
            note = "✅ 无需重跑"
        else:
            note = f"⏳ 排队 · 待重跑 {rerun_cur} 题"
        order_items.append(f'<tr><td>{i+1}</td><td class="rt">{esc(disp(route))}</td>'
            f'<td>{orig["infra"]}</td><td>{orig["pending"]}</td>'
            f'<td>{orig["rerun"]}</td><td>{note}</td></tr>')

    # Per-route sections
    route_sections = [build_route_section(r, routes[r], ORIG[r]) for r in RERUN_ORDER]

    # Totals
    total_orig_resolved = sum(ORIG[r]["resolved"] for r in RERUN_ORDER)
    total_cur_resolved = sum(routes[r]["resolved"] for r in RERUN_ORDER)
    total_recovered = total_cur_resolved - total_orig_resolved
    total_orig_rerun = sum(ORIG[r]["rerun"] for r in RERUN_ORDER)
    total_cur_rerun = sum(routes[r]["counts"].get("infra_failed", 0) +
                          routes[r]["counts"].get("pending", 0) for r in RERUN_ORDER)
    tot_infra = sum(routes[r]["counts"].get("infra_failed", 0) for r in RERUN_ORDER)
    tot_ability = sum(routes[r]["counts"].get("ability_failed", 0) for r in RERUN_ORDER)
    tot_pending = sum(routes[r]["counts"].get("pending", 0) for r in RERUN_ORDER)
    tot_peval = sum(routes[r]["counts"].get("pending_eval", 0) for r in RERUN_ORDER)

    css = '''
:root{--bg:#0d1117;--card:#161b22;--border:#30363d;--text:#c9d1d9;--text-dim:#8b949e;--accent:#58a6ff;--infra:#f85149;--ability:#3fb950;--pending:#d29922}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;font-size:14px;line-height:1.6;padding:20px;max-width:1400px;margin:0 auto}
h1{color:var(--accent);font-size:1.5em;margin-bottom:8px}
h2{color:var(--accent);font-size:1.2em;margin:24px 0 12px;border-bottom:1px solid var(--border);padding-bottom:6px}
h3{color:var(--text);font-size:1.05em;margin-bottom:8px}
.meta{color:var(--text-dim);font-size:.85em;margin-bottom:16px}
.route-code{color:var(--text-dim);font-size:.85em;font-weight:normal}
table{border-collapse:collapse;width:100%;margin-bottom:16px;font-size:.85em}
th,td{border:1px solid var(--border);padding:6px 10px;text-align:left}
th{background:#21262d;color:var(--accent);font-weight:600;white-space:nowrap}
td.rt{font-weight:600;color:var(--accent)}
td.pos{color:var(--ability);font-weight:600}
td.infra-cell{color:var(--infra);font-weight:600}
td.ability-cell{color:var(--ability)}
td.pending-cell{color:var(--pending)}
.route-card{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:16px;margin-bottom:20px}
.summary-table{margin-bottom:12px}
.details,details{margin-top:8px}
details summary{cursor:pointer;padding:8px 12px;background:#21262d;border-radius:4px;font-weight:600;font-size:.9em}
details[open] summary{margin-bottom:8px}
.case-table{font-size:.8em}
.case-table th{background:#1c2128}
.tail{color:var(--text-dim);font-family:monospace;font-size:.85em;max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.more{text-align:center;color:var(--text-dim);font-style:italic}
.note{background:#1c2128;border-left:3px solid var(--accent);padding:12px 16px;margin:12px 0;border-radius:0 4px 4px 0}
.note-infra{border-left-color:var(--infra)}
.redline{color:var(--infra);font-weight:600}
'''

    html_doc = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Harness Infra 重跑计划 — SWE-bench Verified 7-way</title>
<style>{css}</style>
</head>
<body>
<h1>Harness Infra 重跑计划 — SWE-bench Verified 7-way</h1>
<div class="meta">生成时间：{gen_ts} · 数据源：eval_glm53_*.json + progress_glm53_*.json + predictions_glm53/<br>依据：2026-11-23 用户令 · 全量 infra 排查 + 夜间重跑（21:00–09:00）· 从 cline 起</div>

<div class="note note-infra"><b>🔴 核心问题</b>：7-way 里 cline 的 Pass% 被 93 个空 patch 拖低（opencode 仅 1 / hermes 仅 4）。运维已初查：cline 93 个空 patch 中 <b>58 个是 infra</b>（38 Token 额度 429 + 13 超时 + 5 上游 5xx + 2 鉴权），但最终 eval 的 <code>infra_or_quota</code> 却记为 0 —— infra 失败被并进「能力失败」桶，夸大了能力差距。详见 <code>report_harness_cline_lag_analysis_zh.html</code>。</div>

<h2>① 全局概览（7 路）</h2>
<table>
<tr><th>路线</th><th>题集</th><th>当前 resolved</th><th>重跑前 resolved</th><th>已回收</th><th>infra (需重跑)</th><th>能力失败 (不重跑)</th><th>待定 (需transcript)</th><th>待评测</th><th>当前重跑目标</th><th>原始重跑目标</th><th>状态</th></tr>
{chr(10).join(overview_rows)}
<tr style="font-weight:bold;background:#21262d"><td>合计</td><td>—</td><td>{total_cur_resolved}</td><td>{total_orig_resolved}</td><td class="pos">+{total_recovered}</td><td class="infra-cell">{tot_infra}</td><td class="ability-cell">{tot_ability}</td><td class="pending-cell">{tot_pending}</td><td>{tot_peval}</td><td>{total_cur_rerun}</td><td>{total_orig_rerun}</td><td>—</td></tr>
</table>

<div class="note"><b>分类口径</b>（复用并推广 <code>c2_cline_R2233.py</code> 框架）：<br><span class="redline">🔴 infra</span>：Token 额度/429/rate-limit、超时、上游 500/502/503/504、鉴权 401/403/forbidden/适配器、<code>quota_blocked</code>/<code>timeout</code> 标志位 → <b>需重跑</b><br><span style="color:var(--ability)">🟢 ability</span>：确实产出了 real patch、但 apply+test 失败 → <b>不重跑</b>（这是能力，重跑无意义、属造假风险）<br><span style="color:var(--pending)">🟡 待定</span>：空 patch 且 rc=0 无报错（无法从 tail 判定）→ <b>需 transcript</b>，空 patch 重跑成本低、大概率能出分，也纳入重跑<br><b>待评测</b>：real patch 已产出但尚未 eval（codex/pi/deepseek 部分题未跑完 eval）→ 需 eval，不重跑 predict</div>

<h2>② 重跑顺序</h2>
<table>
<tr><th>#</th><th>路线</th><th>原始 infra</th><th>原始待定</th><th>原始重跑目标</th><th>当前状态</th></tr>
{chr(10).join(order_items)}
</table>
<div class="note"><b>顺序规则</b>：cline 先行（用户指定）→ 其余按 infra 数量降序。<br><b>总重跑目标</b>：{total_orig_rerun} 题（原始） → 当前剩余 {total_cur_rerun} 题（cline 已回收 {total_recovered} 题）</div>

<h2>③ 重跑时间窗策略</h2>
<div class="note"><b>窗口</b>：每晚 21:00 – 次日 09:00（12 小时）<br><b>窗口内</b>：启动/继续重跑（predict → eval → merge → REGEN 7way 报告）<br><b>窗口外</b>（09:00–21:00）：只 park —— 不启动新 predict/eval，队列存着等下一个 21:00<br><b>原因</b>：避开 glm-5.3-flash 网关白天使用高峰（额度 429 正是高峰产物）+ 白天 CPU 争抢<br><b>判据</b>：<code>H=$(date +%H); [ "$H" -ge 21 ] || [ "$H" -lt 9 ] && echo 窗口内</code><br><b>并发</b>：限 ≤2 路；额度 429 重试带指数退避（2/4/8/16s，上限 4 次）<br><b>硬护栏</b>：docker eval <code>--memory 128g --cpus 16</code> · predict <code>ulimit -v 209715200</code> + nice19 + OMP≤8 · <code>harness_resource_guard.sh</code>（PID931671）常开 · pretrain step ≤7.4s 越界即降载 · load 闸 ≤120</div>

<h2>④ 每晚进度</h2>
<table>
<tr><th>日期</th><th>窗口</th><th>路线</th><th>重跑目标</th><th>已回收</th><th>备注</th></tr>
<tr><td>2026-11-23</td><td>21:00→09:00</td><td>cline-patched</td><td>95</td><td class="pos">+{total_recovered}</td><td>orchestrator PID4191374 运行中 · stop script PID2781365 09:00 截止 · 增量 eval+merge 每轮执行 · 7way 报告已 REGEN</td></tr>
<tr><td colspan="6" class="more">后续窗口待 cline 完成后按顺序续跑 codex → deepseek → cc → pi → hermes → opencode</td></tr>
</table>

<h2>⑤ 各路逐题清单（infra / ability / 待定 三列）</h2>
{chr(10).join(route_sections)}

<h2>⑥ 纪律与防伪底线</h2>
<div class="note"><ul>
<li><b>只重跑 infra 类</b>（含「待定」里的空 patch —— 空 patch 重跑成本低、大概率能出分），<span class="redline">🚫 不重跑 ability 类</span>（那是能力，重跑无意义、属造假风险）</li>
<li>重跑过程必须继续守硬护栏：docker eval mem128g/cpu16 · predict ulimit+nice19+OMP≤8 · guard PID931671 常开 · pretrain step ≤7.4s · load 闸</li>
<li>夜间重跑也限并发 ≤2 路，别再触发额度</li>
<li>只动本线文件；不碰 pretrain/data/vision/zhulong</li>
<li>额度 429 重试要带退避（指数退避 + 重试上限），不要裸刷网关</li>
<li>诚实：重跑结果标注「夜间重跑」口径</li>
<li><b>红线</b>：429/5xx/timeout/auth = infra（NOT capability）；real-patch-tests-fail = capability；不编造数字、infra≠能力、判据不放宽</li>
</ul></div>

<div class="meta" style="margin-top:24px;border-top:1px solid var(--border);padding-top:12px">生成器：<code>run/harness/gen_infra_rerun_plan.py</code> · 数据：<code>infra_rerun_classify_7way.json</code><br>分类框架基于：<code>c2_cline_R2233.py</code>（推广至 7 路）· 0 script / 0 外链</div>
</body></html>'''

    REPORTS.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html_doc)
    sz = OUT.stat().st_size
    print(f"Written: {OUT} ({sz} bytes)")
    for r in RERUN_ORDER:
        rd = routes[r]; c = rd["counts"]
        print(f"  {disp(r):12s} resolved={rd['resolved']:3d} infra={c.get('infra_failed',0):3d} "
              f"ability={c.get('ability_failed',0):3d} pending={c.get('pending',0):3d} "
              f"rerun={c.get('infra_failed',0)+c.get('pending',0):3d}")

if __name__ == "__main__":
    main()
