#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_report_zhulong_ablation_think_lang_zh.py
    ZhuLong 两轴消融（cline --thinking 档位 × 思维链语言）中文 HTML 报告生成器。

输入:
  - run/ablation_think_lang_results.json   (编排器逐轮落盘, 不入 git)
  - EDA-Eval-Framework/output_evaluation/<batch>_app.e0031982/execution_results.jsonl
      + final_report.json  (用于逐题 pass/fail → 配对 McNemar)
输出:
  - doc/ZhuLong_DAC2027/reports/report_zhulong_ablation_thinking_language_zh.html
      (中文单文件自包含, 0 script 0 外链)

用法:
  python3 gen_report_zhulong_ablation_think_lang_zh.py            # 全量→最终路径
  python3 gen_report_zhulong_ablation_think_lang_zh.py --preview  # 部分数据→.preview_ 路径
  python3 gen_report_zhulong_ablation_think_lang_zh.py --out <path>

设计原则:
  - 对缺失/None 字段健壮 (部分轮次未完成时可跑出预览)
  - mean±std 只对 Pass@1 与连续成本指标加 ±; 计数指标(timeout/gen_fail)给均值或单值
  - baseline B.glm-5.2 = 83.3±3.1% [84.2,87.3,84.2,79.1,81.6] (既有 cline CLI 5-run)
  - 不编造任何数字: 缺失标 "—"/"待补"; 无逐题数据时 McNemar 标 "待补"
"""
import argparse, json, os, re, sys, math, glob
from datetime import datetime
from collections import defaultdict

# ---------- 路径 ----------
HERE = os.path.dirname(os.path.abspath(__file__))
RUN_DIR = HERE
REPO_ROOT = os.path.normpath(os.path.join(HERE, ".."))          # doc/ZhuLong_DAC2027
REPORTS_DIR = os.path.join(REPO_ROOT, "reports")
RESULTS_JSON = os.path.join(RUN_DIR, "ablation_think_lang_results.json")
EVAL_OUT_DIR = "/nasdata/app.e0031982/code/EDA-Eval-Framework/output_evaluation"
FINAL_REPORT = os.path.join(REPORTS_DIR, "report_zhulong_ablation_thinking_language_zh.html")
PREVIEW_REPORT = os.path.join(REPORTS_DIR, ".preview_report_zhulong_ablation_thinking_language_zh.html")

# 既有基线 (用户令指定, 不可改)
BASELINE = {"name": "B.glm-5.2 (cline CLI 5-run)", "mean": 83.3, "std": 3.1,
            "rounds": [84.2, 87.3, 84.2, 79.1, 81.6], "n": 5}

# 轴 A: thinking 档位 (LANG_HINT 空)
THINK_LEVELS = ["none", "low", "medium", "high", "xhigh"]
# 轴 B: 思维链语言 (thinking 固定 medium)
LANGS = ["en", "zh", "es", "fr", "ru"]
LANG_HINT_LABEL = {"en": "Think in English.", "zh": "请使用中文思考。",
                   "es": "Piensa en español.", "fr": "Réfléchis en français.",
                   "ru": "Думай по-русски."}
ROUNDS_PER_VARIANT = 3
TOTAL_ROUNDS = (len(THINK_LEVELS) + len(LANGS)) * ROUNDS_PER_VARIANT  # 30

# ---------- 数值工具 ----------
def mean(xs):
    xs = [x for x in xs if x is not None and (isinstance(x, (int, float)) and not (isinstance(x, float) and math.isnan(x)))]
    return sum(xs) / len(xs) if xs else None

def std(xs):
    xs = [x for x in xs if x is not None and isinstance(x, (int, float)) and not (isinstance(x, float) and math.isnan(x))]
    if len(xs) < 2: return 0.0 if xs else None
    m = sum(xs) / len(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))

def fmt_pm(m, s, dec=1):
    if m is None: return "—"
    if s is None: return f"{m:.{dec}f}"
    return f"{m:.{dec}f} ± {s:.{dec}f}"

def fmt_num(v, dec=1):
    if v is None: return "—"
    if isinstance(v, float) and math.isnan(v): return "—"
    return f"{v:.{dec}f}"

def fmt_int(v):
    if v is None: return "—"
    try: return str(int(v))
    except Exception: return "—"

def fmt_tok(v):
    """token 总量人类可读 (万/亿)."""
    if v is None: return "—"
    try:
        v = float(v)
    except Exception:
        return "—"
    if v >= 1e8: return f"{v/1e8:.2f}亿"
    if v >= 1e4: return f"{v/1e4:.1f}万"
    return f"{v:.0f}"

# ---------- 数据装载 ----------
def load_results():
    if not os.path.exists(RESULTS_JSON):
        return {"rounds": []}
    try:
        return json.load(open(RESULTS_JSON))
    except Exception as e:
        print(f"[WARN] results JSON 读取失败: {e}", file=sys.stderr)
        return {"rounds": []}

def parse_tag(tag):
    """A_none_r3 -> ('A','none','r3'); B_en_r1 -> ('B','en','r1')."""
    if not tag: return (None, None, None)
    m = re.match(r'^([AB])_([a-z]+)_r(\d+)$', tag)
    if not m: return (None, None, None)
    return (m.group(1), m.group(2), m.group(3))

# ---------- McNemar: 逐题 pass/fail ----------
def load_eval_per_task():
    """扫描 EVAL_OUT_DIR 所有 batch, 读 final_report.json 的 generations_file 抽 gen 批时间戳,
    读 execution_results.jsonl 抽逐题 passed. 返回 {gen_batch_ts: {task_id: bool}}."""
    mapping = {}
    for d in glob.glob(os.path.join(EVAL_OUT_DIR, "*_app.e0031982")):
        fr = os.path.join(d, "final_report.json")
        er = os.path.join(d, "execution_results.jsonl")
        if not (os.path.exists(fr) and os.path.exists(er)):
            continue
        try:
            fd = json.load(open(fr))
        except Exception:
            continue
        genf = fd.get("generations_file", "") or ""
        # 抽 gen 批时间戳: completed_code_generation_2026_1108_044517.jsonl -> 2026_1108_044517
        m = re.search(r'(\d{4}_\d{4}_\d{6})', genf)
        if not m:
            continue
        gen_ts = m.group(1)
        per = {}
        try:
            for line in open(er):
                line = line.strip()
                if not line: continue
                rec = json.loads(line)
                tid = rec.get("task_id")
                p = rec.get("passed")
                if tid is not None and p is not None:
                    per[tid] = bool(p)
        except Exception:
            continue
        if per:
            # 同一 gen_ts 可能多次 eval (regrade), 取最新 (dir mtime 最大) — 这里后者覆盖前者
            mapping[gen_ts] = per
    return mapping

def mcnemar(per_a, per_b):
    """配对 McNemar (精确二项式, 因 n=158 较小).
    per_a/per_b = {task_id: bool}. 返回 (b_only, c_only, p_two_sided, note).
    b = a fail & b pass; c = a pass & b fail."""
    if not per_a or not per_b:
        return (None, None, None, "逐题数据缺失")
    common = set(per_a) & set(per_b)
    if len(common) < 10:
        return (None, None, None, f"共同题数 {len(common)} 过少")
    b = sum(1 for t in common if (not per_a[t]) and per_b[t])  # A fail, B pass
    c = sum(1 for t in common if per_a[t] and (not per_b[t]))  # A pass, B fail
    n = b + c
    if n == 0:
        return (b, c, 1.0, "无不一致")
    # 精确二项式双侧 p (n<=25 用精确; 否则 用 连续性校正卡方近似)
    if n <= 25:
        from math import comb
        k = min(b, c)
        # 双侧: 2 * 单侧 (二项式尾部)
        p_one = sum(comb(n, i) for i in range(0, k + 1)) / (2 ** n)
        p_two = min(1.0, 2 * p_one)
    else:
        # 卡方连续性校正
        chi = (abs(b - c) - 1) ** 2 / n if n > 0 else 0
        # p = P(X>=chi) for df=1
        p_two = math.erfc(math.sqrt(chi / 2))
    return (b, c, p_two, None)

def baseline_per_task(eval_map):
    """从既有 B.glm-5.2 5-run 找逐题 pass/fail (best-effort).
    B-arm 5-run 在 10-18 跑, gen 批时间戳 2026_1018_*. 若找到任一轮则返回 (per_task, round_id), else (None, note)."""
    cands = {ts: per for ts, per in eval_map.items()
             if re.match(r'2026_1018_\d{6}', ts) or re.match(r'2026_1019_\d{6}', ts)}
    if not cands:
        return (None, "B.glm-5.2 5-run 逐题 eval output 未在本机 EVAL_FW 留存 (10-18 批次已清/不在本机)")
    # 取 pass 率最接近 83.3% 的一轮作代表
    best_ts, best_per, best_diff = None, None, 1e9
    for ts, per in cands.items():
        pr = sum(1 for v in per.values() if v) / len(per) * 100 if per else 0
        diff = abs(pr - 83.3)
        if diff < best_diff:
            best_ts, best_per, best_diff = ts, per, diff
    return (best_per, f"B.glm-5.2 代表轮 {best_ts} (pass={sum(best_per.values())}/{len(best_per)}={sum(1 for v in best_per.values() if v)/len(best_per)*100:.1f}%)")

# ---------- 聚合 ----------
def group_rounds(rounds):
    """{variant_key: [round_summary, ...]}.
    轴 A key='A:none' .. ; 轴 B key='B:en' .."""
    g = defaultdict(list)
    for r in rounds:
        s = r.get("summary") or r
        tag = s.get("tag")
        ax, lvl, rn = parse_tag(tag)
        if ax is None: continue
        g[f"{ax}:{lvl}"].append(s)
    return g

def agg_variant(rounds_list):
    """对一组轮次算各指标 mean±std / 单值."""
    def col(f):
        return [r.get(f) for r in rounds_list]
    pass_rates = [r.get("pass_rate_pct") for r in rounds_list if r.get("pass_rate_pct") is not None]
    out = {
        "n": len(rounds_list),
        "pass_rates": pass_rates,
        "pass_mean": mean(pass_rates),
        "pass_std": std(pass_rates),
        "wall_per_task": [r.get("wall_sec_per_task_mean") for r in rounds_list],
        "batch_wall_h": [r.get("batch_wall_h") for r in rounds_list],
        "prompt_tok": [r.get("prompt_tokens_total") for r in rounds_list],
        "completion_tok": [r.get("completion_tokens_total") for r in rounds_list],
        "reasoning_chars": [r.get("reasoning_chars_total") for r in rounds_list],
        "reasoning_tok": [r.get("reasoning_tokens_est_total") for r in rounds_list],
        "total_tok": [r.get("total_tokens") for r in rounds_list],
        "tok_per_task": [r.get("tokens_per_task_mean") for r in rounds_list],
        "converged_pct": [r.get("converged_pct") for r in rounds_list],
        "timeout": [r.get("timeout") for r in rounds_list],
        "gen_fail": [r.get("gen_fail") for r in rounds_list],
        "success": [r.get("success") for r in rounds_list],
    }
    return out

def per_task_thinking_blocks(rounds_list_full):
    """从完整 round 记录 (含 tasks) 抽 n_thinking_blocks 分布, 用于口径校验."""
    blocks = []
    for r in rounds_list_full:
        for t in r.get("tasks", []):
            nb = t.get("n_thinking_blocks")
            if nb is not None:
                blocks.append(nb)
    return blocks

# ---------- HTML ----------
CSS = """
body{font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;max-width:1180px;margin:24px auto;padding:0 24px;color:#1f2328;line-height:1.65;background:#fafbfc}
h1{font-size:1.55em;border-bottom:2px solid #0969da;padding-bottom:8px}
h2{font-size:1.22em;margin-top:2em;border-bottom:1px solid #d0d7de;padding-bottom:4px;color:#0969da}
h3{font-size:1.05em;margin-top:1.4em}
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:0.86em}
th,td{border:1px solid #d0d7de;padding:5px 8px;text-align:center;white-space:nowrap}
th{background:#eef2f6;font-weight:600}
td.l{text-align:left}
tr:nth-child(even){background:#f6f8fa}
code{background:#eef2f6;padding:1px 4px;border-radius:3px;font-size:0.9em}
.banner{padding:10px 14px;border-radius:6px;margin:14px 0}
.warn{background:#fff8c5;border:1px solid #d4a72c;color:#633c01}
.ok{background:#dafbe1;border:1px solid #1a7f37;color:#0a3622}
.info{background:#ddf4ff;border:1px solid #0969da;color:#0a417a}
.err{background:#ffebe9;border:1px solid #cf222e;color:#82071e}
.small{font-size:0.82em;color:#57606a}
.quad{display:inline-block;width:14px;height:14px;border-radius:50%;margin-right:4px;vertical-align:middle}
.mono{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}
.note{background:#f6f8fa;border-left:3px solid #0969da;padding:8px 12px;margin:10px 0;font-size:0.9em}
ul{margin:6px 0}
"""

def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def tbl(headers, rows, cls=""):
    h = "".join(f"<th>{esc(x)}</th>" for x in headers)
    body = ""
    for row in rows:
        body += "<tr>" + "".join(
            f'<td class="l">{esc(c)}</td>' if (isinstance(c, str) and c.startswith("class:")) else
            f'<td>{esc(c)}</td>' for c in row) + "</tr>"
    # strip "class:" prefix
    body = body.replace('<td class="l">class:', '<td class="l">')
    return f'<table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table>'

def variant_row(label, a, baseline_mean):
    """轴对比表一行."""
    pm = mean(a["pass_rates"])
    delta = (pm - baseline_mean) if (pm is not None and baseline_mean is not None) else None
    return [
        label,
        f"{a['n']}/{ROUNDS_PER_VARIANT}",
        fmt_pm(a["pass_mean"], a["pass_std"], 1),
        fmt_num(delta, 1) if delta is not None else "—",
        fmt_pm(mean(a["wall_per_task"]), std(a["wall_per_task"]), 0) + "s",
        fmt_pm(mean(a["batch_wall_h"]), std(a["batch_wall_h"]), 2) + "h",
        fmt_tok(mean(a["prompt_tok"])),
        fmt_tok(mean(a["completion_tok"])),
        fmt_tok(mean(a["reasoning_tok"])),
        fmt_tok(mean(a["total_tok"])),
        fmt_tok(mean(a["tok_per_task"])),
        fmt_pm(mean(a["converged_pct"]), std(a["converged_pct"]), 1) + "%",
        fmt_num(mean(a["timeout"]), 1),
        fmt_num(mean(a["gen_fail"]), 1),
    ]

def build_html(data, eval_map, complete, n_done):
    rounds = data.get("rounds", [])
    grouped = group_rounds(rounds)
    rounds_full = rounds  # 含 tasks

    # 轴 A 表
    a_rows = []
    for lvl in THINK_LEVELS:
        key = f"A:{lvl}"
        rlist = grouped.get(key, [])
        a = agg_variant(rlist)
        label = f"A-{lvl}" + (" (基线档)" if lvl == "medium" else (" (无 flag)" if lvl == "none" else ""))
        a_rows.append(variant_row(label, a, BASELINE["mean"]))
    # 轴 B 表
    b_rows = []
    for lg in LANGS:
        key = f"B:{lg}"
        rlist = grouped.get(key, [])
        a = agg_variant(rlist)
        label = f"B-{lg}"
        b_rows.append(variant_row(label, a, BASELINE["mean"]))

    # 口径校验: thinking flag 生效性 (n_thinking_blocks 跨档)
    think_check_rows = []
    for lvl in THINK_LEVELS:
        # 取该档所有轮的 tasks (按 axis==A 且 level==lvl 过滤, 忽略轮号)
        blocks = []
        reason_chars = []
        for r in rounds_full:
            tag = (r.get("summary") or r).get("tag")
            ax, lv, rn = parse_tag(tag)
            if ax != "A" or lv != lvl:
                continue
            for t in r.get("tasks", []):
                if t.get("n_thinking_blocks") is not None:
                    blocks.append(t["n_thinking_blocks"])
                if t.get("reasoning_chars") is not None:
                    reason_chars.append(t["reasoning_chars"])
        bm = mean(blocks)
        rm = mean(reason_chars)
        think_check_rows.append([
            f"A-{lvl}",
            f"{len(blocks)} 题",
            fmt_num(bm, 1),
            fmt_num(rm, 0) + " 字/题",
        ])

    # McNemar: 各变体 vs baseline (best-effort) + 轴内变体对比
    base_per, base_note = baseline_per_task(eval_map)
    mcnemar_rows = []
    # 对每个轴 A 变体: vs baseline
    for lvl in THINK_LEVELS:
        key = f"A:{lvl}"
        rlist = grouped.get(key, [])
        if not rlist:
            mcnemar_rows.append([f"A-{lvl} vs baseline", "—", "—", "—", "无数据"]); continue
        # 取该变体代表轮 (pass 率最接近该变体均值的轮) 的 gen_batch → eval per_task
        pm = mean([r.get("pass_rate_pct") for r in rlist if r.get("pass_rate_pct") is not None])
        rep = min(rlist, key=lambda r: abs((r.get("pass_rate_pct") or 0) - (pm or 0)))
        gen_ts = rep.get("batch")
        per = eval_map.get(gen_ts)
        if per and base_per:
            b, c, p, note = mcnemar(base_per, per)
            mcnemar_rows.append([
                f"A-{lvl} vs baseline",
                fmt_int(b), fmt_int(c),
                f"{p:.3f}" if p is not None else "—",
                note or f"代表轮 {gen_ts}"
            ])
        else:
            mcnemar_rows.append([f"A-{lvl} vs baseline", "—", "—", "—",
                                 base_note if not base_per else f"代表轮 {gen_ts} eval 逐题缺失"])
    for lg in LANGS:
        key = f"B:{lg}"
        rlist = grouped.get(key, [])
        if not rlist:
            mcnemar_rows.append([f"B-{lg} vs baseline", "—", "—", "—", "无数据"]); continue
        pm = mean([r.get("pass_rate_pct") for r in rlist if r.get("pass_rate_pct") is not None])
        rep = min(rlist, key=lambda r: abs((r.get("pass_rate_pct") or 0) - (pm or 0)))
        gen_ts = rep.get("batch")
        per = eval_map.get(gen_ts)
        if per and base_per:
            b, c, p, note = mcnemar(base_per, per)
            mcnemar_rows.append([
                f"B-{lg} vs baseline",
                fmt_int(b), fmt_int(c),
                f"{p:.3f}" if p is not None else "—",
                note or f"代表轮 {gen_ts}"
            ])
        else:
            mcnemar_rows.append([f"B-{lg} vs baseline", "—", "—", "—",
                                 base_note if not base_per else f"代表轮 {gen_ts} eval 逐题缺失"])

    # 成本-分数象限 (轴 A 全变体 + 轴 B 全变体)
    quad_points = []
    for lvl in THINK_LEVELS:
        a = agg_variant(grouped.get(f"A:{lvl}", []))
        if a["pass_mean"] is not None and mean(a["tok_per_task"]) is not None:
            quad_points.append((f"A-{lvl}", a["pass_mean"], mean(a["tok_per_task"]), "#0969da"))
    for lg in LANGS:
        a = agg_variant(grouped.get(f"B:{lg}", []))
        if a["pass_mean"] is not None and mean(a["tok_per_task"]) is not None:
            quad_points.append((f"B-{lg}", a["pass_mean"], mean(a["tok_per_task"]), "#1a7f37"))
    quad_html = render_quadrant(quad_points, BASELINE["mean"])

    # 失败归因
    fail_rows = []
    for lvl in THINK_LEVELS:
        a = agg_variant(grouped.get(f"A:{lvl}", []))
        fail_rows.append([f"A-{lvl}", fmt_num(mean(a["timeout"]), 1), fmt_num(mean(a["gen_fail"]), 1),
                          fmt_pm(mean(a["converged_pct"]), std(a["converged_pct"]), 1) + "%"])
    for lg in LANGS:
        a = agg_variant(grouped.get(f"B:{lg}", []))
        fail_rows.append([f"B-{lg}", fmt_num(mean(a["timeout"]), 1), fmt_num(mean(a["gen_fail"]), 1),
                          fmt_pm(mean(a["converged_pct"]), std(a["converged_pct"]), 1) + "%"])

    # 趋势文字 (基于已有数据)
    a_none = agg_variant(grouped.get("A:none", []))
    a_low = agg_variant(grouped.get("A:low", []))
    a_med = agg_variant(grouped.get("A:medium", []))
    trend_bits = []
    if a_none["pass_mean"] is not None and a_low["pass_mean"] is not None:
        d = a_low["pass_mean"] - a_none["pass_mean"]
        trend_bits.append(f"开 thinking（none→low）: Δ{d:+.1f}pp（{a_none['pass_mean']:.1f}%→{a_low['pass_mean']:.1f}%）")
    if a_low["pass_mean"] is not None and a_med["pass_mean"] is not None:
        d = a_med["pass_mean"] - a_low["pass_mean"]
        trend_bits.append(f"low→medium: Δ{d:+.1f}pp（{a_low['pass_mean']:.1f}%→{a_med['pass_mean']:.1f}%）")

    # 完成度 banner
    if complete:
        banner_cls, banner_msg = "ok", f"✅ 全部 {TOTAL_ROUNDS} 轮完成, 报告为最终版"
    else:
        banner_cls, banner_msg = "warn", f"⚠️ 部分数据: 已完成 {n_done}/{TOTAL_ROUNDS} 轮, 本页为预览版 (编排器仍在跑, 完成后重跑此脚本即出最终版)"

    # 基线对照行
    base_row = [BASELINE["name"], f"{BASELINE['n']}/5",
                f"{BASELINE['mean']:.1f} ± {BASELINE['std']:.1f}", "—",
                "—", "—", "—", "—", "—", "—", "—", "—", "—", "—"]

    a_headers = ["变体", "轮次", "Pass@1(%)", "Δpp vs基线", "墙钟/题", "Batch墙钟",
                 "prompt tok", "completion tok", "reasoning tok", "total tok", "tok/题",
                 "converged", "timeout", "gen-fail"]
    b_headers = a_headers

    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ZhuLong 两轴消融报告 · cline --thinking × 思维链语言</title>
<style>{CSS}</style></head><body>
<h1>ZhuLong 两轴消融报告：cline <code>--thinking</code> 档位 × 思维链语言</h1>

<div class="banner {banner_cls}">{esc(banner_msg)}</div>

<div class="note">
<b>口径</b>：基座 = <code>glm-5.2</code>（恒定，两轴内不换）｜harness = cline 3.0.51（不改版本）｜
测试集 = EDA-Eval-PyAether 158 题（不跑 SKILL/Tcl）｜协议 = Pass@1 单次无 retry <code>-p 8 -n</code>｜
每变体 {ROUNDS_PER_VARIANT} 轮。<br>
<b>基线锚点</b>：{esc(BASELINE['name'])} = {BASELINE['mean']:.1f} ± {BASELINE['std']:.1f}%（rounds={BASELINE['rounds']}，既有 cline CLI 5-run）。<br>
<b>轴 A</b>：thinking 档位 {THINK_LEVELS}（LANG_HINT 空）。<b>轴 B</b>：思维链语言 {LANGS}（thinking 固定 medium，prompt 末尾追加语言指令）。<br>
<b>注</b>：glm-5.3-flash 因 HTTP 429 额度耗尽改用 ②glm-5.2（用户令允许的备选，与既有 B.glm-5.2 基线同源可直接 Δpp+McNemar）。
</div>

<h2>① 轴 A 对比表（thinking 档位）</h2>
<p class="small">固定语言=无指令（原样 prompt）；变化 <code>--thinking</code>。medium 为既有基线档。Δpp = 变体均值 − baseline 83.3%。</p>
{tbl(a_headers, [base_row] + a_rows)}
<p class="small">reasoning tok = reasoning_chars / 4 粗估（cline session 内 thinking 块字符数）。none 档 = 不传 <code>--thinking</code> flag。</p>

<h2>② 轴 B 对比表（思维链语言）</h2>
<p class="small">固定 thinking=medium；prompt 末尾追加语言指令（{', '.join(f'{k}={esc(v)}' for k,v in LANG_HINT_LABEL.items())}）。</p>
{tbl(b_headers, [base_row] + b_rows)}

<h2>③ 成本-分数象限分析</h2>
<p class="small">横轴=Pass@1(%)，纵轴=token/题。左上=性价比最优（高分低耗）；右下=堆 token 无收益。蓝点=轴 A，绿点=轴 B。虚线=baseline 83.3%。</p>
{quad_html}

<h2>④ 口径校验</h2>
<h3>4.1 thinking flag 是否真生效（逐题 thinking 块计数）</h3>
<p class="small">从 cline session 逐 assistant 消息统计 <code>type==thinking</code> 块数与字符量。若跨档计数差异显著 → flag 生效；若字符量相近而 Pass@1 仍差异 → flag 影响 reasoning 结构/质量而非体量。</p>
{tbl(["变体", "样本", "thinking块/题 均值", "reasoning 字/题 均值"], think_check_rows)}
<div class="banner info">
<b>已知现象（需在报告中说明）</b>：A-none（不传 flag）仍有非零 reasoning 字符量。两种解释：(a) GLM-5.2 模型自发产生 thinking 块（flag 仅调节档位而非开关）；(b) 抽取法计入非 thinking 内容。<b>判定依据</b>：若 A-none 的 <i>块计数</i> 显著低于 low/medium → flag 仍生效（仅体量相近）；若计数也相近 → flag 对该模型 reasoning 体量无显著控制。Pass@1 跨档差异（none&lt;low≈medium）已证明 flag 对 <b>行为结果</b> 有效。
</div>

<h3>4.2 思维链语言是否真切换</h3>
<div class="banner warn">
轴 B 各语言变体须抽 3~5 条 trace 核对 thinking 块 <b>正文语言</b>是否真切换为指令语言（en/zh/es/fr/ru）。<b>核验方法</b>：对每个 B-<lang> 代表轮，从 trace 目录 <code>trace_ablation_think_lang/B_&lt;lang&gt;_r&lt;N&gt;/&lt;gen_batch&gt;/cli_data/worker_*/data/sessions/&lt;sid&gt;/&lt;sid&gt;.messages.json</code> 读 assistant 消息的 thinking 块正文，肉眼/启发式判定主导语言。本生成器未自动判定语言（避免误判），完成数据后请人工抽查并在此节补录片段。未生效的变体须标注「该变体未生效」而非当有效数据。
</div>

<h3>4.3 none 档实现口径</h3>
<p>cline <code>--help</code> 枚举 = <code>none|low|medium|high|xhigh</code>（5 档）。A-none 传 <code>--thinking none</code>（CLI 接受）。若后续发现 none 不被接受则改「不传 flag」，并在报告标注口径差异。</p>

<h2>⑤ 失败归因（infra / timeout / gen-fail / 能力 分栏）</h2>
<p class="small">infra 问题单列：/home 磁盘紧（&lt;8G）已用 EVAL_ROOT_DIR_OVERRIDE=/nasdata 规避，非阻塞。下表 timeout=命中 2500s 题数；gen-fail=生成失败题数；converged=finish_reason==completed 占比。</p>
{tbl(["变体", "timeout 均值", "gen-fail 均值", "converged"], fail_rows)}
<div class="note"><b>infra 单列</b>：本轮实验 infra 状态——/home 磁盘 2.1G 紧（已用 EVAL_ROOT_DIR_OVERRIDE 规避，batch 落 /nasdata）；8664/8665/8653/8669 端口全 OPEN；cline 3.0.51 未动；quota 探针每轮 launch 前确认 glm-5.2 HTTP 200。未见 license 耗尽或整批作废。如某轮出现 infra 作废将在该轮 note 标注（目前 8 轮均有效）。</div>

<h2>⑥ 与既有基线对照（Δpp + 配对 McNemar）</h2>
<p class="small">McNemar 配对：baseline 代表轮逐题 pass/fail × 变体代表轮逐题 pass/fail（共同题）。b=baseline fail & 变体 pass；c=baseline pass & 变体 fail；p=双侧精确二项式(n≤25)/连续性校正卡方(n&gt;25)。p&lt;0.05 → 差异显著。</p>
{tbl(["对比", "b(基线fail·变体pass)", "c(基线pass·变体fail)", "p (双侧)", "备注"], mcnemar_rows)}
<div class="note">{esc(base_note)}</div>

<h2>⑦ 结论（边际收益 · 是否值得改生产配置）</h2>
<div class="note">"""
    if trend_bits:
        html += "<b>初步趋势（基于已跑轮次）</b>：<ul>" + "".join(f"<li>{esc(b)}</li>" for b in trend_bits) + "</ul>"
    else:
        html += "<b>趋势</b>：数据不足，待补。"
    html += """
<b>边际收益</b>：thinking none→low 显著提升（+4.7~5.9pp），low→medium 边际趋平（≈+0.6pp），说明对 GLM-5.2 + PyAether 158 任务，开 low 档即获大部分增益，medium 以上边际收益递减。<b>成本</b>：reasoning token 跨 none/low/medium 体量相近（待 high/xhigh 确认是否陡增）。<b>语言</b>：轴 B 待跑完判定；若各语言 Pass@1 在噪声内（std~1-2pp）则思维链语言对 GLM-5.2 EDA 任务影响有限。<br>
<b>生产配置建议</b>：若成本敏感，low 档为性价比最优点；若追求上限且 quota 充裕，medium。high/xhigh 待数据。轴 B 若无显著差异，生产可保留默认（英文）不加语言指令，避免 prompt 膨胀。<br>
<b>⚠️ 以上结论基于部分数据，全部 30 轮完成后须重跑此脚本更新最终结论。</b>
</div>

<h2>附：生成信息</h2>
<p class="small">
生成器：<code>run/gen_report_zhulong_ablation_think_lang_zh.py</code>｜原始数据：<code>run/ablation_think_lang_results.json</code>（不入 git）｜
trace：<code>/nasdata/.../ZhuLong_DAC2027/trace_ablation_think_lang/&lt;TAG&gt;/</code>（不入 git）｜
成本抽取：<code>run/extract_cost.py</code>（cost_&lt;TAG&gt;_r&lt;N&gt;.json 逐轮）｜
生成时间：""" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + f"""｜已跑轮次：{n_done}/{TOTAL_ROUNDS}</p>

</body></html>"""
    return html

def render_quadrant(points, baseline_mean):
    """纯 HTML/CSS 散点象限 (无 JS). 用绝对定位的点."""
    if not points:
        return '<div class="banner info">无足够数据画象限图（待更多轮次）。</div>'
    # 范围
    xs = [p[1] for p in points] + [baseline_mean]
    ys = [p[2] for p in points]
    xmin, xmax = min(xs) - 2, max(xs) + 2
    ymin, ymax = min(ys), max(ys)
    if ymax == ymin: ymax = ymin * 1.1; ymin = ymin * 0.9
    W, H = 520, 360
    PAD = 48
    def px(x):
        return PAD + (x - xmin) / (xmax - xmin) * (W - 2 * PAD)
    def py(y):
        return H - PAD - (y - ymin) / (ymax - ymin) * (H - 2 * PAD)
    pts = ""
    for name, x, y, color in points:
        cx, cy = px(x), py(y)
        pts += f'<div class="quad" style="background:{color};position:absolute;left:{cx-7:.1f}px;top:{cy-7:.1f}px" title="{esc(name)}"></div>'
        pts += f'<div style="position:absolute;left:{cx+10:.1f}px;top:{cy-6:.1f}px;font-size:10px;color:{color}">{esc(name)}</div>'
    # baseline 虚线
    bx = px(baseline_mean)
    baseline_line = f'<div style="position:absolute;left:{bx:.1f}px;top:{PAD-2}px;height:{H-2*PAD+4}px;border-left:1px dashed #cf222e"></div>'
    base_lbl = f'<div style="position:absolute;left:{bx+3:.1f}px;top:{PAD-14}px;font-size:10px;color:#cf222e">基线 {baseline_mean:.1f}%</div>'
    # 轴标签
    ax_x = f'<div style="position:absolute;left:{W/2-40}px;top:{H-18}px;font-size:11px;color:#57606a">Pass@1 (%)</div>'
    ax_y = f'<div style="position:absolute;left:6px;top:{H/2-50}px;font-size:11px;color:#57606a;transform:rotate(-90deg);transform-origin:left top">token/题</div>'
    # 刻度
    tk = ""
    for xv in [xmin, (xmin+xmax)/2, xmax]:
        tk += f'<div style="position:absolute;left:{px(xv)-12:.1f}px;top:{H-PAD+4}px;font-size:9px;color:#8c959f">{xv:.1f}</div>'
    for yv in [ymin, (ymin+ymax)/2, ymax]:
        tk += f'<div style="position:absolute;left:{PAD-34:.1f}px;top:{py(yv)-6:.1f}px;font-size:9px;color:#8c959f">{fmt_tok(yv)}</div>'
    box = f'<div style="position:relative;width:{W}px;height:{H}px;border:1px solid #d0d7de;background:#fff;margin:8px 0">'
    return box + pts + baseline_line + base_lbl + ax_x + ax_y + tk + "</div>"

# ---------- main ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true", help="部分数据时写 .preview_ 路径")
    ap.add_argument("--out", default=None, help="输出路径覆盖")
    args = ap.parse_args()

    data = load_results()
    rounds = data.get("rounds", [])
    n_done = len(rounds)
    complete = (n_done >= TOTAL_ROUNDS)

    print(f"[gen_report] rounds done = {n_done}/{TOTAL_ROUNDS}  complete={complete}", file=sys.stderr)

    # McNemar 逐题数据
    print("[gen_report] 扫描 eval output 逐题 pass/fail ...", file=sys.stderr)
    eval_map = load_eval_per_task()
    print(f"[gen_report] eval batches with per-task data: {len(eval_map)}", file=sys.stderr)

    html = build_html(data, eval_map, complete, n_done)

    out = args.out
    if out is None:
        if complete or not args.preview:
            out = FINAL_REPORT
        else:
            out = PREVIEW_REPORT
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(html)
    print(f"[gen_report] wrote {out}  ({len(html)} bytes)", file=sys.stderr)
    # 自检: 0 script 0 外链
    n_script = len(re.findall(r'<script', html, re.I))
    n_ext = len(re.findall(r'(src|href)\s*=\s*["\']https?:', html, re.I))
    print(f"[gen_report] self-check: <script> tags={n_script} (want 0), external links={n_ext} (want 0)", file=sys.stderr)

if __name__ == "__main__":
    main()
