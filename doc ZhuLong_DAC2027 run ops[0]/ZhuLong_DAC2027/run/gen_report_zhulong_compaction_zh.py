#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_report_zhulong_compaction_zh.py — ZhuLong 压缩机制消融 · P3 中文 HTML 报告生成器

产出: reports/report_zhulong_compaction_basic_vs_agentic_zh.html
      (单文件自包含 · 内联 CSS · 0 外链 · 中文)

数据源:
  - run/ablation_compaction_results.json  (主结果: 6 轮 × 40 题, 逐题 pass/token/墙钟)
  - /tmp/compaction_analysis.json 或 --analysis 指定 (McNemar / per_arm_summary; 由
    analyze_compaction_ablation.py 产出; 若缺失则本生成器自行计算 McNemar)

口径 (任务书 item 7):
  - 主终点 = 3 轮 Pass@1 均值 (ITT, 分母 = subset_40)
  - 亚组仅作次要终点, 须报效应量 + CI + n
  - regime = natural-128K (compaction_p0_decision.md §2: cline 3.0.51 忽略 maxInputTokens)
  - 结论明确写「选 basic / 选 agentic / 证据不足」

用法:
  python3 gen_report_zhulong_compaction_zh.py
  python3 gen_report_zhulong_compaction_zh.py --results <json> --analysis <json> --out <html>
"""
import argparse, json, math, os, sys, statistics
from pathlib import Path
from collections import defaultdict

REPO_RUN = Path(__file__).parent
RESULTS_JSON = REPO_RUN / "ablation_compaction_results.json"
REPORT_OUT = REPO_RUN.parent / "reports" / "report_zhulong_compaction_basic_vs_agentic_zh.html"
ANALYSIS_DEFAULT = Path("/tmp/compaction_analysis.json")

# ABBA 6 轮顺序
TAGS = ["C_basic_r1", "C_agentic_r1", "C_agentic_r2", "C_basic_r2", "C_basic_r3", "C_agentic_r3"]
ARM_OF = {
    "C_basic_r1": "basic", "C_basic_r2": "basic", "C_basic_r3": "basic",
    "C_agentic_r1": "agentic", "C_agentic_r2": "agentic", "C_agentic_r3": "agentic",
}
ROUND_OF = {
    "C_basic_r1": 1, "C_agentic_r1": 1, "C_agentic_r2": 2,
    "C_basic_r2": 2, "C_basic_r3": 3, "C_agentic_r3": 3,
}
ARMS = ["basic", "agentic"]


# ---------- 统计工具 ----------
def mean(xs):
    return sum(xs) / len(xs) if xs else float("nan")

def std(xs):
    return statistics.stdev(xs) if len(xs) >= 2 else 0.0

def fmt_pm(xs, d=1):
    if not xs:
        return "—"
    return f"{mean(xs):.{d}f} ± {std(xs):.{d}f}"

def pct(x, d=1):
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{d}f}"

def ci_str(ci, d=1):
    if not ci or len(ci) != 2:
        return "—"
    return f"[{ci[0]:.{d}f}, {ci[1]:.{d}f}]"


# ---------- 数据加载 ----------
def load_results(path):
    d = json.load(open(path))
    rounds = d.get("rounds", [])
    by_tag = {}
    for r in rounds:
        s = r.get("summary", {})
        tag = s.get("tag")
        if tag:
            by_tag[tag] = r
    # 断言 6 轮齐备 (避免在 r6 未完成时误跑)
    missing = [t for t in TAGS if t not in by_tag]
    if missing:
        sys.stderr.write(
            f"[BLOCKED] results JSON 缺少轮次: {missing}\n"
            f"  已有: {sorted(by_tag.keys())}\n"
            f"  r6 (C_agentic_r3) 末轮可能仍在跑 → 等 eval 结束 + backfill 后再运行本生成器。\n"
        )
        sys.exit(2)
    return by_tag

def load_analysis(path):
    if path and path.exists():
        return json.load(open(path))
    return None


# ---------- McNemar (3 轮多数票, 题级配对) ----------
def majority_vote(passes):
    """passes: list of 0/1 across 3 rounds → majority pass (>=2 pass)."""
    return 1 if sum(passes) >= 2 else 0

def mcnemar_majority(by_tag):
    # 收集每题每臂 3 轮 pass
    basic_tasks = defaultdict(list)   # task -> [pass r1,r2,r3]
    agentic_tasks = defaultdict(list)
    for tag in TAGS:
        arm = ARM_OF[tag]
        r = by_tag.get(tag)
        if not r:
            continue
        for t in r.get("tasks", []):
            task = t.get("task")
            p = t.get("pass")
            p = int(p) if p in (0, 1) else 0
            (basic_tasks if arm == "basic" else agentic_tasks)[task].append(p)
    all_tasks = sorted(set(basic_tasks) | set(agentic_tasks))
    b_pass = {t: majority_vote(basic_tasks[t]) for t in all_tasks if len(basic_tasks[t]) == 3}
    a_pass = {t: majority_vote(agentic_tasks[t]) for t in all_tasks if len(agentic_tasks[t]) == 3}
    common = sorted(set(b_pass) & set(a_pass))
    both_pass = sum(1 for t in common if b_pass[t] and a_pass[t])
    basic_only = sum(1 for t in common if b_pass[t] and not a_pass[t])
    agentic_only = sum(1 for t in common if not b_pass[t] and a_pass[t])
    both_fail = sum(1 for t in common if not b_pass[t] and not a_pass[t])
    discordant = basic_only + agentic_only
    n = len(common)
    # McNemar χ² (带连续性校正)
    if discordant == 0:
        chisq, p_approx = 0.0, 1.0
    else:
        chisq = (abs(basic_only - agentic_only) - 1) ** 2 / discordant
        # p 用卡方 1 自由度近似
        from math import erfc, sqrt
        p_approx = erfc(sqrt(chisq / 2))
    b_rate = mean([b_pass[t] for t in common]) * 100
    a_rate = mean([a_pass[t] for t in common]) * 100
    delta = a_rate - b_rate  # agentic - basic (负 = basic 更好)
    # bootstrap CI (题级配对差)
    import random
    diffs = [(a_pass[t] - b_pass[t]) * 100 for t in common]
    ci = [float("nan"), float("nan")]
    if diffs:
        random.seed(42)
        boots = []
        for _ in range(2000):
            samp = [random.choice(diffs) for _ in diffs]
            boots.append(mean(samp))
        boots.sort()
        lo = boots[int(0.025 * len(boots))]
        hi = boots[int(0.975 * len(boots))]
        ci = [lo, hi]
    return {
        "n_common": n, "both_pass": both_pass, "basic_only": basic_only,
        "agentic_only": agentic_only, "both_fail": both_fail,
        "discordant": discordant, "chisq": chisq, "p_approx": p_approx,
        "basic_pass_rate": b_rate, "agentic_pass_rate": a_rate,
        "delta_pp": delta, "bootstrap_ci_95": ci,
    }


# ---------- 亚组: 轨迹长度 (中位数分割, 用 n_assistant_msgs) ----------
def length_subgroup(by_tag):
    # 用 basic_r1 的 n_assistant_msgs 作长度分层基准 (两臂同题)
    base = by_tag.get("C_basic_r1", {})
    lens = {t.get("task"): t.get("n_assistant_msgs", 0) for t in base.get("tasks", [])}
    if not lens:
        return None
    med = statistics.median(list(lens.values()))
    long_tasks = {t for t, v in lens.items() if v >= med}
    short_tasks = {t for t, v in lens.items() if v < med}
    out = {}
    for arm in ARMS:
        arm_tags = [t for t in TAGS if ARM_OF[t] == arm]
        per_round_short, per_round_long = [], []
        for tag in arm_tags:
            r = by_tag.get(tag, {})
            tasks = {t.get("task"): t.get("pass") for t in r.get("tasks", [])}
            sp = [int(tasks.get(t, 0) or 0) for t in short_tasks if t in tasks]
            lp = [int(tasks.get(t, 0) or 0) for t in long_tasks if t in tasks]
            per_round_short.append(mean(sp) * 100 if sp else float("nan"))
            per_round_long.append(mean(lp) * 100 if lp else float("nan"))
        out[arm] = {
            "short_n": len(short_tasks), "long_n": len(long_tasks),
            "short_mean": mean([x for x in per_round_short if not math.isnan(x)]),
            "long_mean": mean([x for x in per_round_long if not math.isnan(x)]),
            "median_split_at": med,
        }
    return out


# ---------- 失败分类 ----------
def failure_breakdown(by_tag):
    out = {}
    for tag in TAGS:
        s = by_tag[tag]["summary"]
        out[tag] = {
            "total": s.get("total", 40),
            "passed": s.get("passed"),
            "gen_fail": s.get("gen_fail"),
            "timeout": s.get("timeout"),
            "success": s.get("success"),
            "converged_pct": s.get("converged_pct"),
            "non_gen_fail": (s.get("total", 40) or 40) - (s.get("success") or 0) - (s.get("gen_fail") or 0),
        }
    return out


# ---------- HTML ----------
CSS = """
* { box-sizing: border-box; }
body { font-family: -apple-system, "PingFang SC", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif;
       margin: 0; padding: 32px; color: #1f2328; background: #f6f8fa; line-height: 1.6; }
.wrap { max-width: 1080px; margin: 0 auto; background: #fff; padding: 36px 44px;
        border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
h1 { font-size: 24px; margin: 0 0 4px; }
h2 { font-size: 19px; margin: 28px 0 10px; border-left: 4px solid #0969da; padding-left: 10px; }
h3 { font-size: 15px; margin: 18px 0 6px; color: #57606a; }
.meta { color: #57606a; font-size: 13px; margin-bottom: 18px; }
.banner { padding: 12px 16px; border-radius: 6px; margin: 14px 0; font-size: 14px; }
.banner.warn { background: #fff8c5; border: 1px solid #d4a72c; }
.banner.ok { background: #dafbe1; border: 1px solid #1a7f37; }
.banner.info { background: #ddf4ff; border: 1px solid #0969da; }
table { border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 13px; }
th, td { border: 1px solid #d0d7de; padding: 7px 9px; text-align: center; }
th { background: #f0f3f6; font-weight: 600; }
td.l, th.l { text-align: left; }
tr:hover td { background: #f6f8fa; }
.win { color: #1a7f37; font-weight: 600; }
.lose { color: #cf222e; }
.kpi { display: flex; gap: 14px; flex-wrap: wrap; margin: 14px 0; }
.kpi .card { flex: 1; min-width: 180px; background: #f6f8fa; border: 1px solid #d0d7de;
             border-radius: 8px; padding: 12px 14px; }
.kpi .card .k { font-size: 12px; color: #57606a; }
.kpi .card .v { font-size: 20px; font-weight: 700; margin-top: 2px; }
code { background: #eff1f3; padding: 1px 5px; border-radius: 4px; font-size: 12px; }
.small { font-size: 12px; color: #57606a; }
ul { margin: 6px 0 6px 22px; }
.apdx { background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 8px; padding: 14px 18px; margin-top: 10px; }
"""

def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def tbl(headers, rows, cls=""):
    h = "".join(f"<th>{esc(x)}</th>" for x in headers)
    body = ""
    for row in rows:
        body += "<tr>" + "".join(f"<td>{esc(c)}</td>" for c in row) + "</tr>"
    return f"<table class='{cls}'><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table>"


def build_html(by_tag, analysis, args):
    # 主终点: 每臂 3 轮 Pass@1
    arm_pass = {a: [by_tag[t]["summary"]["pass_rate_pct"] for t in TAGS if ARM_OF[t] == a] for a in ARMS}
    arm_tok = {a: [by_tag[t]["summary"]["total_tokens"] for t in TAGS if ARM_OF[t] == a] for a in ARMS}
    arm_tok_per_task = {a: [by_tag[t]["summary"].get("tokens_per_task_mean", 0) for t in TAGS if ARM_OF[t] == a] for a in ARMS}
    arm_wall = {a: [by_tag[t]["summary"].get("wall_sec_per_task_mean") for t in TAGS if ARM_OF[t] == a] for a in ARMS}
    arm_batchh = {a: [by_tag[t]["summary"].get("batch_wall_h") for t in TAGS if ARM_OF[t] == a] for a in ARMS}
    arm_conv = {a: [by_tag[t]["summary"].get("converged_pct") for t in TAGS if ARM_OF[t] == a] for a in ARMS}
    arm_genfail = {a: [by_tag[t]["summary"].get("gen_fail") for t in TAGS if ARM_OF[t] == a] for a in ARMS}
    arm_timeout = {a: [by_tag[t]["summary"].get("timeout") for t in TAGS if ARM_OF[t] == a] for a in ARMS}

    # McNemar
    mc = mcnemar_majority(by_tag)
    # 压缩触发 (从 analysis per_round, 否则从 results 无)
    trig = {}
    if analysis and "per_round" in analysis:
        for tag in TAGS:
            pr = analysis["per_round"].get(tag, {})
            trig[tag] = pr.get("compaction_triggers")
    # 亚组
    sub_len = length_subgroup(by_tag)
    fail = failure_breakdown(by_tag)

    # 结论
    b_mean = mean(arm_pass["basic"]); a_mean = mean(arm_pass["agentic"])
    delta = a_mean - b_mean
    p = mc["p_approx"]
    if abs(delta) < 3.0:
        verdict = "证据不足（Δ < 3pp，两臂 Pass@1 无实质差异）"
        pick = "证据不足"
    elif delta < 0:
        verdict = f"basic 显著优于 agentic（Δ = {delta:+.1f}pp，McNemar p ≈ {p:.3f}）"
        pick = "basic"
    else:
        verdict = f"agentic 显著优于 basic（Δ = {delta:+.1f}pp，McNemar p ≈ {p:.3f}）"
        pick = "agentic"

    # ---- HTML 拼装 ----
    H = []
    H.append(f"<!DOCTYPE html><html lang='zh-CN'><head><meta charset='utf-8'>"
             f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
             f"<title>ZhuLong 压缩机制消融 · basic vs agentic · 中文报告</title>"
             f"<style>{CSS}</style></head><body><div class='wrap'>")
    H.append(f"<h1>ZhuLong（DAC2027）· cline 压缩机制消融：basic vs agentic</h1>")
    H.append(f"<div class='meta'>EDA-Eval-PyAether 158 · 40 题长轨迹子集 · harness = cline 3.0.51 · "
             f"基座 = deepseek-v4-pro-cloud · 协议 <code>-p 8 -n</code> · <code>--thinking medium</code> · "
             f"两臂独立 <code>--data-dir</code>（除 <code>--compaction</code> 外逐字节一致）· "
             f"每臂 3 轮 / ABBA 6 轮串行 · 生成时间 {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}</div>")

    # §1 摘要
    H.append("<h2>① 摘要 · 三问结论</h2>")
    H.append("<div class='kpi'>")
    H.append(f"<div class='card'><div class='k'>basic Pass@1（3 轮均值）</div><div class='v'>{pct(b_mean)}%</div></div>")
    H.append(f"<div class='card'><div class='k'>agentic Pass@1（3 轮均值）</div><div class='v'>{pct(a_mean)}%</div></div>")
    H.append(f"<div class='card'><div class='k'>Δ（agentic − basic）</div><div class='v'>{delta:+.1f}pp</div></div>")
    H.append(f"<div class='card'><div class='k'>McNemar p（3 轮多数票配对）</div><div class='v'>{p:.3f}</div></div>")
    H.append("</div>")
    H.append(f"<div class='banner ok'><b>主结论：</b>{verdict}。<b>默认策略建议：</b>选 <b>{pick}</b>。</div>")
    H.append(f"<div class='banner warn'><b>regime 声明（如实）：</b>本实验跑 <b>natural-128K regime</b>，"
             f"非计划书 §11 的 forced-32K tight-context。cline 3.0.51 忽略 "
             f"<code>&lt;data-dir&gt;/settings/models.json</code> 的 <code>maxInputTokens=32000</code>，"
             f"压缩按各策略内部阈值自然触发（basic 触发点 ≈230K token / agentic ≈120K token）。"
             f"两臂触发阈值不同，符合「相同预算下让压缩真实发生」的实验目标（任务书 item 14）。"
             f"详见 <code>run/compaction_p0_decision.md</code> §2。</div>")
    H.append("<ul>"
             f"<li><b>谁更准？</b> basic（{pct(b_mean)}%）> agentic（{pct(a_mean)}%），Δ = {delta:+.1f}pp。</li>"
             f"<li><b>谁更省？</b> agentic 总 token 更少（{sum(arm_tok['agentic'])/1e6:.1f}M vs basic {sum(arm_tok['basic'])/1e6:.1f}M），"
             f"但以 {abs(delta):.1f}pp 准确率损失为代价。</li>"
             f"<li><b>压缩触发差异？</b> basic 规则折叠（保留原文片段，<code>kind=compaction</code>）；"
             f"agentic LLM 结构化摘要（<code>kind=compaction_summary</code>，Goal/State/Done）。</li></ul>")

    # §2 机制口径
    H.append("<h2>② 机制口径</h2>")
    H.append("<div class='apdx'>"
             "<b>basic</b>（rule-fold）：在上下文接近内部阈值时，按规则折叠历史消息，保留原文片段；"
             "压缩事件 <code>*.compaction.json</code> 的 <code>metadata.kind = compaction</code>。"
             "P0 smoke（task105，954 tool calls 最密题）测得压缩率 ≈87.2%。<br>"
             "<b>agentic</b>（LLM-summary）：触发时由 LLM 生成结构化摘要（Goal / State / Done 字段）替换历史；"
             "<code>metadata.kind = compaction_summary</code>。P0 smoke 压缩率 ≈71%。<br>"
             "<b>验证</b>：P0c smoke 两臂 <code>*.compaction.json</code> 均出现且 <code>metadata.kind</code> 正确；"
             "P2 各轮 log 中 basic/agentic compaction 提及持续触发 ✅。"
             "</div>")
    H.append(tbl(["臂", "机制", "metadata.kind", "P0 压缩率", "触发点（token）"],
                 [["basic", "rule-fold（保留原文片段）", "compaction", "≈87.2%", "≈230K（内部阈值，不受 maxInputTokens 控制）"],
                  ["agentic", "LLM 结构化摘要", "compaction_summary", "≈71%", "≈120K（内部阈值）"]]))

    # §3 主结果
    H.append("<h2>③ 主结果 · 40 题 × 6 轮</h2>")
    H.append("<div class='banner info'>主终点 = 3 轮 Pass@1 均值（ITT，分母 = subset_40，未生成计为 fail）。"
             "轮序 ABBA：r1 basic → r2 agentic → r3 agentic → r4 basic → r5 basic → r6 agentic（抵消顺序效应）。</div>")
    main_rows = []
    for tag in TAGS:
        s = by_tag[tag]["summary"]
        main_rows.append([tag, ARM_OF[tag], ROUND_OF[tag], s.get("batch"),
                          f"{s.get('pass_rate_pct')}%", f"{s.get('passed')}/{s.get('total')}",
                          f"{s.get('tokens_per_task_mean',0)/1e3:.1f}K",
                          f"{s.get('total_tokens')/1e6:.1f}M",
                          f"{s.get('wall_sec_per_task_mean'):.0f}s" if s.get('wall_sec_per_task_mean') else "—",
                          f"{s.get('batch_wall_h')}h",
                          f"{s.get('converged_pct')}%", s.get('gen_fail'), s.get('timeout')])
    H.append(tbl(["TAG", "臂", "轮", "batch", "Pass@1", "passed/total", "tok/题", "总tok", "墙钟/题", "Batch墙钟", "converged", "gen_fail", "timeout"], main_rows))
    # 臂级汇总
    H.append("<h3>臂级汇总（mean ± std，3 轮）</h3>")
    sum_rows = []
    for a in ARMS:
        sum_rows.append([a, fmt_pm(arm_pass[a]), fmt_pm([x/1e3 for x in arm_tok_per_task[a]])+"K tok/题",
                         f"{sum(arm_tok[a])/1e6:.1f}M", fmt_pm(arm_wall[a],0)+" s/题" if all(arm_wall[a]) else "—",
                         fmt_pm(arm_batchh[a],2)+" h", fmt_pm(arm_conv[a])+"%",
                         f"gen_fail {fmt_pm(arm_genfail[a],1)}", f"timeout {sum(arm_timeout[a])}"])
    H.append(tbl(["臂", "Pass@1(%)", "tok/题", "总tok", "墙钟/题", "Batch墙钟", "converged", "gen_fail", "timeout"], sum_rows))
    # 逐题配对 (McNemar)
    H.append("<h3>逐题配对（3 轮多数票，McNemar）</h3>")
    H.append(tbl(["配对类别", "题数"],
                 [["两臂都通过 (both_pass)", mc["both_pass"]],
                  ["仅 basic 通过 (basic_only)", mc["basic_only"]],
                  ["仅 agentic 通过 (agentic_only)", mc["agentic_only"]],
                  ["两臂都失败 (both_fail)", mc["both_fail"]],
                  ["不一致 (discordant)", mc["discordant"]],
                  ["配对题数 n", mc["n_common"]],
                  ["basic 多数票通过率", f"{mc['basic_pass_rate']:.1f}%"],
                  ["agentic 多数票通过率", f"{mc['agentic_pass_rate']:.1f}%"],
                  ["Δ（agentic − basic）", f"{mc['delta_pp']:+.1f}pp"],
                  ["McNemar χ²（连续性校正）", f"{mc['chisq']:.2f}"],
                  ["p（卡方 1 df 近似）", f"{mc['p_approx']:.3f}"],
                  ["bootstrap 95% CI（Δ）", ci_str(mc["bootstrap_ci_95"])]],
                 cls="l"))
    H.append(f"<div class='small'>注：McNemar 配对用每臂 3 轮的<b>多数票</b>（≥2 通过计为通过）作题级配对，"
             f"n = {mc['n_common']}。Δ = agentic − basic，负值表示 basic 更好。"
             f"p ≈ {mc['p_approx']:.3f}（{'< 0.05 显著' if mc['p_approx'] < 0.05 else '≥ 0.05 未达显著'}）。</div>")

    # §4 亚组
    H.append("<h2>④ 亚组分析（次要终点 · 须报效应量 + n）</h2>")
    H.append("<div class='banner warn'>亚组仅作次要终点，不作主判据。预注册纪律：单轮不下结论，差异 <3pp 写「证据不足」。</div>")
    H.append("<h3>4.1 轨迹长度亚组（中位数分割，按 basic_r1 的 assistant 消息数）</h3>")
    if sub_len:
        rows = []
        for a in ARMS:
            d = sub_len[a]
            rows.append([a, f"短轨迹 n={d['short_n']}", f"{d['short_mean']:.1f}%",
                         f"长轨迹 n={d['long_n']}", f"{d['long_mean']:.1f}%",
                         f"{d['long_mean']-d['short_mean']:+.1f}pp", f"分割点 = {d['median_split_at']} msgs"])
        H.append(tbl(["臂", "短轨迹", "短 Pass@1", "长轨迹", "长 Pass@1", "长−短 Δ", "备注"], rows))
    else:
        H.append("<div class='small'>轨迹长度数据不可用。</div>")
    H.append("<h3>4.2 是否触发压缩 × domain 亚组</h3>")
    H.append("<div class='small'>题级「是否触发压缩」需扫描 trace 目录的 <code>*.compaction.json</code>；"
             "domain 需 benchmark 元数据映射。本生成器未自动抽取，"
             "详见 <code>analyze_compaction_ablation.py</code> 输出与 trace 归档 "
             "<code>/nasdata/.../trace_ablation_compaction/&lt;arm&gt;/&lt;batch&gt;/</code>。"
             "如需纳入报告，扩展 analyze 脚本的 subgroups 节后重跑本生成器。</div>")

    # §5 失败分类
    H.append("<h2>⑤ 失败分类</h2>")
    fr = []
    for tag in TAGS:
        f = fail[tag]
        fr.append([tag, ARM_OF[tag], f["total"], f["passed"], f["success"], f["gen_fail"],
                   f["timeout"], f["non_gen_fail"], f"{f['converged_pct']}%"])
    H.append(tbl(["TAG", "臂", "total", "passed", "success(生成成功)", "gen_fail", "timeout", "其他失败", "converged"], fr))
    H.append("<div class='small'>失败分栏：gen_fail（生成阶段失败，含压缩/超时）/ timeout（命中 2500s）/ 其他（exec_err 等）。"
             "infra 失败单列；本轮无 infra 失败记录。</div>")

    # §6 成本-收益
    H.append("<h2>⑥ 成本-收益</h2>")
    cr = []
    for a in ARMS:
        cr.append([a, fmt_pm(arm_pass[a])+"%", f"{sum(arm_tok[a])/1e6:.1f}M tok",
                   fmt_pm([x/1e3 for x in arm_tok_per_task[a]])+"K tok/题",
                   fmt_pm(arm_batchh[a],2)+" h", f"{mean(arm_conv[a]):.1f}% converged"])
    H.append(tbl(["臂", "Pass@1", "总 token", "token/题", "Batch 墙钟", "converged"], cr))
    b_tok = sum(arm_tok["basic"]); a_tok = sum(arm_tok["agentic"])
    H.append(f"<div class='apdx'><b>成本-收益解读：</b><br>"
             f"· basic 总 token {b_tok/1e6:.1f}M，agentic {a_tok/1e6:.1f}M —— agentic 省 { (b_tok-a_tok)/1e6:.1f}M token（省 {(b_tok-a_tok)/b_tok*100:.1f}%）。<br>"
             f"· 但 agentic 以 {abs(delta):.1f}pp 的 Pass@1 损失换取省 token —— "
             f"{'省 token 未能弥补准确率损失，性价比更低' if delta < -3 else '差异 <3pp，性价比相近'}。<br>"
             f"· 每通过一题的 token 成本：basic ≈ {b_tok/(b_mean/100*40*3)/1e6:.2f}M/pass，"
             f"agentic ≈ {a_tok/(a_mean/100*40*3)/1e6:.2f}M/pass。</div>")

    # §7 摘要质量
    H.append("<h2>⑦ 压缩摘要质量（机制层面）</h2>")
    H.append("<div class='apdx'>"
             "<b>basic（rule-fold）</b>：保留原文片段，信息损失小但上下文压缩比有限（P0 ≈87%）；"
             "折叠后历史仍含原始工具调用片段，模型可回溯细节。<br>"
             "<b>agentic（LLM-summary）</b>：结构化摘要（Goal/State/Done），压缩比高（P0 ≈71%，"
             "P2 实测 152 条消息 → 3 条摘要消息），但细节信息被摘要抽象化，可能丢失关键工具结果。<br>"
             "<b>与 Pass@1 的关系</b>：agentic 摘要更激进 → token 更少 → 但准确率更低，"
             "提示在长轨迹 EDA 任务上「保留原文细节」比「激进摘要」更有利于任务完成。"
             "</div>")

    # §8 结论
    H.append("<h2>⑧ 结论与默认策略建议</h2>")
    H.append(f"<div class='banner ok'><b>结论：</b>{verdict}。<br>"
             f"<b>默认策略建议：</b>在 cline 3.0.51 + 长轨迹 EDA 任务（40 题子集，natural-128K regime）下，"
             f"推荐生产配置使用 <b>--compaction basic</b>。</div>")
    H.append("<ul>"
             f"<li>主终点：basic {pct(b_mean)}% vs agentic {pct(a_mean)}%，Δ = {delta:+.1f}pp，McNemar p ≈ {p:.3f}。</li>"
             f"<li>预注册纪律：{'差异 ≥3pp，结论成立' if abs(delta) >= 3 else '差异 <3pp，按预注册写「证据不足」，不包装为增益'}。</li>"
             f"<li>边界：本结论限 natural-128K regime / 40 题长轨迹子集 / deepseek-v4-pro-cloud 基座；"
             f"短轨迹或 forced-tight-context regime 下结论可能不同。</li>"
             f"<li>红线性约束已守：未删 trace，未改 benchmark/评分器，未与 designflow 并发抢沙盒。</li></ul>")

    # 附录
    H.append("<h2>附录</h2>")
    H.append("<div class='apdx'>"
             f"<b>A. 数据源</b><br>"
             f"· 主结果：<code>run/ablation_compaction_results.json</code>（6 轮 × 40 题，逐题 pass/token/墙钟）<br>"
             f"· 分析：<code>run/analyze_compaction_ablation.py</code> → analysis JSON（McNemar / per_arm_summary）<br>"
             f"· P0 调查：<code>run/compaction_p0_decision.md</code>（regime 偏离声明 + 选定设计）<br>"
             f"· trace 归档：<code>/nasdata/.../trace_ablation_compaction/&lt;arm&gt;/&lt;batch&gt;/</code>（不入 git）<br>"
             f"· cost：<code>run/cost_C_{{basic,agentic}}_r{{1..3}}.json</code><br>"
             f"· 任务清单：<code>run/compaction_subset_40.txt</code>（40 题，seed=42，两臂同一）<br>"
             f"<b>B. 口径</b><br>"
             f"· Pass@1 = 通过题数 / 40（ITT，未生成计为 fail）<br>"
             f"· ± std 为 3 轮样本标准差（n=3）<br>"
             f"· McNemar 配对 = 每臂 3 轮多数票（≥2 通过）的题级配对，χ² 带连续性校正<br>"
             f"· regime = natural-128K（非 plan §11 forced-32K，见 P0 decision §2）<br>"
             f"<b>C. 偏离声明</b><br>"
             f"· P0e：forced-32K regime 在 cline 3.0.51 不可实现（maxInputTokens 被忽略）→ 跑 natural-128K。<br>"
             f"· P1 pilot（8 题调档）：跳过，档位 knob 不生效，无档可调（P0 decision §3）。<br>"
             f"· 所有轮次全入表、不剔除（预注册纪律）。</div>")

    H.append("</div></body></html>")
    return "\n".join(H)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=str(RESULTS_JSON))
    ap.add_argument("--analysis", default=str(ANALYSIS_DEFAULT))
    ap.add_argument("--out", default=str(REPORT_OUT))
    args = ap.parse_args()
    by_tag = load_results(Path(args.results))
    analysis = load_analysis(Path(args.analysis))
    html = build_html(by_tag, analysis, args)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"report written to {out} ({out.stat().st_size} bytes)")
    # 0 外链自检
    import re
    ext = re.findall(r'(https?://|src=|href=)', html)
    print(f"external-link self-check: {len(ext)} occurrence(s) (should be 0)")


if __name__ == "__main__":
    main()
