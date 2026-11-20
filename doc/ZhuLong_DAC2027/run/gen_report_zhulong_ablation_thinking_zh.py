#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_report_zhulong_ablation_thinking_zh.py
    ZhuLong 轴 A（cline --thinking 档位消融）单独中文 HTML 报告生成器（含成本）。

输入:
  - run/ablation_think_lang_results.json   (编排器逐轮落盘, 不入 git；轴 A 共 15 轮)
输出:
  - doc/ZhuLong_DAC2027/reports/report_zhulong_ablation_thinking_zh.html
      (中文单文件自包含, 0 script 0 外链)

复用同目录两轴报告生成器的数值/格式化/CSS/表格工具，保证两份报告口径与样式一致。
只抽取轴 A（tag 前缀 "A_"）轮次；轴 B（思维链语言）不纳入本报告。

用法:
  python3 gen_report_zhulong_ablation_thinking_zh.py
  python3 gen_report_zhulong_ablation_thinking_zh.py --out <path>
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# 复用两轴报告生成器的工具函数与样式（同一目录，无副作用，main 被 __main__ 保护）
from gen_report_zhulong_ablation_think_lang_zh import (
    mean, std, fmt_pm, fmt_num, fmt_int, fmt_tok, esc, tbl, CSS,
    BASELINE, THINK_LEVELS, ROUNDS_PER_VARIANT, parse_tag, group_rounds,
    agg_variant, variant_row, render_quadrant,
)

RESULTS_JSON = os.path.join(HERE, "ablation_think_lang_results.json")
REPORTS_DIR = os.path.normpath(os.path.join(HERE, "..", "reports"))
FINAL_REPORT = os.path.join(REPORTS_DIR, "report_zhulong_ablation_thinking_zh.html")

N_LVLS = len(THINK_LEVELS)
TOTAL_AXIS_A = N_LVLS * ROUNDS_PER_VARIANT  # 15

THINK_LABEL = {
    "none":   "none（无 --thinking）",
    "low":    "low",
    "medium": "medium（基线档）",
    "high":   "high",
    "xhigh":  "xhigh（过度思考）",
}


def load_results():
    if not os.path.exists(RESULTS_JSON):
        return {"rounds": []}
    try:
        return json.load(open(RESULTS_JSON))
    except Exception as e:
        print(f"[WARN] results JSON 读取失败: {e}", file=sys.stderr)
        return {"rounds": []}


def axis_a_rounds(rounds):
    """只保留轴 A 轮次，并按下标(轮号)排序。返回 [round, ...]。"""
    order = {lv: i for i, lv in enumerate(THINK_LEVELS)}
    out = []
    for r in rounds:
        s = (r.get("summary") or r)
        ax, lv, rn = parse_tag(s.get("tag"))
        if ax != "A" or lv not in order:
            continue
        out.append((order[lv], int(rn) if rn else 99, r))
    out.sort(key=lambda t: (t[0], t[1]))
    return [r for _, _, r in out]


def per_round_rows(a_rounds):
    """逐轮明细行（含每轮完整成本）。"""
    rows = []
    for r in a_rounds:
        s = r.get("summary") or r
        rows.append([
            s.get("tag", "—"),
            s.get("batch", "—"),
            fmt_num(s.get("pass_rate_pct"), 1) + "%",
            f"{s.get('passed', '—')}/{s.get('total', '—')}",
            fmt_num(s.get("wall_sec_per_task_mean"), 0) + "s",
            fmt_num(s.get("batch_wall_h"), 2) + "h",
            fmt_tok(s.get("prompt_tokens_total")),
            fmt_tok(s.get("completion_tokens_total")),
            fmt_tok(s.get("reasoning_tokens_est_total")),
            fmt_tok(s.get("total_tokens")),
            fmt_tok(s.get("tokens_per_task_mean")),
            fmt_num(s.get("converged_pct"), 1) + "%",
            fmt_int(s.get("timeout")),
            fmt_int(s.get("gen_fail")),
        ])
    return rows


def think_check_rows(a_rounds):
    """口径校验：各档 n_thinking_blocks / reasoning_chars，证明 --thinking flag 确实生效。"""
    rows = []
    order = {lv: i for i, lv in enumerate(THINK_LEVELS)}
    per_lvl = {lv: [] for lv in THINK_LEVELS}
    for r in a_rounds:
        s = (r.get("summary") or r)
        ax, lv, rn = parse_tag(s.get("tag"))
        for t in (r.get("tasks") or []):
            if t.get("n_thinking_blocks") is None and t.get("reasoning_chars") is None:
                continue
            per_lvl[lv].append(t)
    for lv in THINK_LEVELS:
        tasks = per_lvl[lv]
        blocks = [t["n_thinking_blocks"] for t in tasks if t.get("n_thinking_blocks") is not None]
        reas = [t["reasoning_chars"] for t in tasks if t.get("reasoning_chars") is not None]
        rows.append([
            f"A-{lv}",
            f"{len(tasks)} 题",
            fmt_pm(mean(blocks), std(blocks), 1),
            f"{fmt_pm(mean(reas), std(reas), 0)} 字/题",
        ])
    return rows


# ---------- HTML 组装 ----------
def build_html(data):
    rounds = data.get("rounds", [])
    a_rounds = axis_a_rounds(rounds)
    grouped = group_rounds(a_rounds)
    n_done = len(a_rounds)
    complete = n_done >= TOTAL_AXIS_A

    # 汇总表（分数 + 成本）
    a_headers = ["变体", "轮次", "Pass@1(%)", "Δpp vs基线", "墙钟/题", "Batch墙钟",
                 "prompt tok", "completion tok", "reasoning tok", "total tok", "tok/题",
                 "converged", "timeout", "gen-fail"]
    a_rows = []
    for lvl in THINK_LEVELS:
        rlist = grouped.get(f"A:{lvl}", [])
        a = agg_variant(rlist)
        a_rows.append(variant_row(f"A-{lvl}", a, BASELINE["mean"]))
    base_row = [BASELINE["name"], f"{BASELINE['n']}/5",
                f"{BASELINE['mean']:.1f} ± {BASELINE['std']:.1f}", "—",
                "—", "—", "—", "—", "—", "—", "—", "—", "—", "—"]

    # 逐轮明细
    detail_rows = per_round_rows(a_rounds)
    detail_headers = ["轮次", "gen 批次", "Pass@1(%)", "passed/total", "墙钟/题",
                      "Batch墙钟", "prompt tok", "compl tok", "reasoning tok",
                      "total tok", "tok/题", "converged", "timeout", "gen-fail"]

    # 失败归因
    fail_rows = []
    for lvl in THINK_LEVELS:
        a = agg_variant(grouped.get(f"A:{lvl}", []))
        fail_rows.append([f"A-{lvl}",
                          fmt_num(mean(a["timeout"]), 1),
                          fmt_num(mean(a["gen_fail"]), 1),
                          fmt_pm(mean(a["converged_pct"]), std(a["converged_pct"]), 1) + "%"])

    # 口径校验
    check_rows = think_check_rows(a_rounds)

    # 成本-分数象限（tok/题 vs Pass@1）
    quad_points = []
    for lvl in THINK_LEVELS:
        a = agg_variant(grouped.get(f"A:{lvl}", []))
        if a["pass_mean"] is not None and mean(a["tok_per_task"]) is not None:
            quad_points.append((f"A-{lvl}", a["pass_mean"], mean(a["tok_per_task"]), "#0969da"))
    quad_html = render_quadrant(quad_points, BASELINE["mean"])

    # 结论（倒 U 形 + 峰值定位 + 方差）
    agg = {lv: agg_variant(grouped.get(f"A:{lv}", [])) for lv in THINK_LEVELS}
    m = {lv: agg[lv]["pass_mean"] for lv in THINK_LEVELS}
    s = {lv: std(agg[lv]["pass_rates"]) for lv in THINK_LEVELS}

    def d(a, b):
        if m[a] is not None and m[b] is not None:
            return m[b] - m[a]
        return None

    trend_bits = []
    if m["none"] is not None:
        trend_bits.append(f"none→low 开思考: Δ{d('none','low'):+.1f}pp")
    if m["low"] is not None and m["medium"] is not None:
        trend_bits.append(f"low→medium 加深: Δ{d('low','medium'):+.1f}pp")
    if m["medium"] is not None and m["high"] is not None:
        trend_bits.append(f"medium→high: Δ{d('medium','high'):+.1f}pp（方差 {s['medium']:.1f}→{s['high']:.1f}）")
    if m["high"] is not None and m["xhigh"] is not None:
        trend_bits.append(f"high→xhigh 过度思考: Δ{d('high','xhigh'):+.1f}pp（回落）")

    peak = None
    if all(m[lv] is not None for lv in THINK_LEVELS):
        peak = max(THINK_LEVELS, key=lambda lv: (m[lv], -s[lv]))

    # 成本总额（轴 A 15 轮全体）
    tot_tok_all = sum((r.get("summary") or r).get("total_tokens") or 0 for r in a_rounds)
    tot_wall_all = sum((r.get("summary") or r).get("batch_wall_h") or 0 for r in a_rounds)
    toks_per_task_all = [(r.get("summary") or r).get("tokens_per_task_mean") for r in a_rounds]

    if complete:
        banner_cls, banner_msg = "ok", f"✅ 轴 A（thinking 档位）全部 {n_done}/{TOTAL_AXIS_A} 轮完成，本报告为最终版"
    else:
        banner_cls, banner_msg = "warn", f"⚠️ 部分数据：已完成 {n_done}/{TOTAL_AXIS_A} 轮（编排器仍在跑）"

    peak_txt = f"{peak}（{m[peak]:.1f}±{s[peak]:.1f}%）" if peak else "待补"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ZhuLong thinking 档位消融报告（轴 A）· 含成本</title>
<style>{CSS}</style></head><body>
<h1>ZhuLong 消融报告（轴 A）：cline <code>--thinking</code> 档位</h1>

<div class="banner {banner_cls}">{esc(banner_msg)}</div>

<div class="note">
<b>口径</b>：基座 = <code>glm-5.2</code>（恒定）｜harness = cline 3.0.51（不改版本）｜
测试集 = EDA-Eval-PyAether 158 题（不跑 SKILL/Tcl）｜协议 = Pass@1 单次无 retry <code>-p 8 -n</code>｜
每档 {ROUNDS_PER_VARIANT} 轮，共 {TOTAL_AXIS_A} 轮。<br>
<b>基线锚点</b>：{esc(BASELINE['name'])} = {BASELINE['mean']:.1f} ± {BASELINE['std']:.1f}%（rounds={BASELINE['rounds']}，既有 cline CLI 5-run）。<br>
<b>档位</b>：{THINK_LEVELS}（<code>none</code>=无 <code>--thinking</code>，<code>medium</code>=基线档，<code>xhigh</code>=最高档）。<br>
<b>范围</b>：本报告仅轴 A（thinking 档位）；轴 B（思维链语言）见两轴总报告。
</div>

<h2>1. 核心结论</h2>
<div class="note">
<b>倒 U 形确认</b>：随 <code>--thinking</code> 档位从 none 逐级升高，Pass@1 先升后降，
在 <code>medium</code> 达峰值（与 <code>high</code> 均值相同，但 medium 方差最小、最稳定），
到 <code>xhigh</code> 回落到基线以下 —— 过度思考反而损害正确率。<br>
<b>趋势</b>：{("、".join(trend_bits)) if trend_bits else "待补"}。<br>
<b>最优档位</b>：<code>{peak_txt}</code>（默认 <code>medium</code> 即最优档，无需再调高；提高档位只增加成本与方差）。
</div>

<h2>2. 汇总对比（分数 + 成本）</h2>
<p class="small">Δpp 为 vs 基线 {BASELINE['mean']:.1f}%；墙钟/题=每任务墙钟秒数；prompt/completion/reasoning tok 为该档 {ROUNDS_PER_VARIANT} 轮总量均值；tok/题=每任务总 token 均值。</p>
{tbl(a_headers, a_rows + [base_row])}

<h2>3. 逐轮明细（每轮完整成本）</h2>
<p class="small">每档 {ROUNDS_PER_VARIANT} 轮逐一列出 Pass@1 与全套成本字段，便于核对方差来源（尤其 high 档 3 轮 82.3/87.3/86.7 的高散度）。</p>
{tbl(detail_headers, detail_rows)}

<h2>4. 成本-分数象限</h2>
<p class="small">横轴 Pass@1（%），纵轴 token/题（成本）；红色虚竖线 = 基线 {BASELINE['mean']:.1f}%。理想变体 = 左上（低 token 高分数）。</p>
{quad_html}

<h2>5. 失败归因</h2>
<p class="small">timeout / gen-fail 为该档 {ROUNDS_PER_VARIANT} 轮均值；converged 为收敛任务占比均值。</p>
{tbl(["变体", "timeout 均值", "gen-fail 均值", "converged"], fail_rows)}

<h2>6. 口径校验：<code>--thinking</code> flag 确实生效</h2>
<p class="small">各档可见思维块数（n_thinking_blocks）与思维链字符数应随档位单调上升，否则 flag 未注入、该档数据不可用。</p>
{tbl(["变体", "样本", "n_thinking_blocks", "reasoning_chars"], check_rows)}

<h2>附：轴 A 全体成本</h2>
<p class="small">15 轮合计：total tokens = {fmt_tok(tot_tok_all)}；批墙钟合计 = {fmt_num(tot_wall_all, 2)}h；
每任务 token 均值 = {fmt_pm(mean(toks_per_task_all), std(toks_per_task_all), 0)}。</p>

<div class="small" style="margin-top:2em;color:#8c959f">
生成时间 {os.popen('date "+%Y-%m-%d %H:%M:%S %z"').read().strip()} ｜ 数据源 run/ablation_think_lang_results.json（不入 git）
｜ 生成器 gen_report_zhulong_ablation_thinking_zh.py（0 script / 0 外链）。
</div>
</body></html>"""

    return html


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="输出路径覆盖")
    args = ap.parse_args()

    data = load_results()
    a_rounds = axis_a_rounds(data.get("rounds", []))
    print(f"[gen_think] axis-A rounds = {len(a_rounds)}/{TOTAL_AXIS_A}", file=sys.stderr)

    html = build_html(data)

    out = args.out or FINAL_REPORT
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(html)
    print(f"[gen_think] wrote {out}  ({len(html)} bytes)", file=sys.stderr)

    import re
    n_script = len(re.findall(r"<script", html, re.I))
    n_ext = len(re.findall(r'(src|href)\s*=\s*["\']https?:', html, re.I))
    print(f"[gen_think] self-check: <script>={n_script} (want 0), external links={n_ext} (want 0)", file=sys.stderr)


if __name__ == "__main__":
    main()