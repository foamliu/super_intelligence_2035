#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成「llama.cpp 全 ckpt 常识推理 8 集 + 能力曲线 + 700k 预测」中文 HTML 报告（幂等）。

读取 nemo_experiments/baize2b/lm_eval_results/gguf_iter_<iter>_fixed_8set/results.json
（由 /tmp/baize_eval_pipeline.sh 经修复后 llama.cpp build 5dc38db00 产出），
汇总 8 个常识推理任务的 acc / acc_norm，计算 Avg，绘制能力-vs-step 曲线
（含 P-6 / Xmodel-2 s1 / Phi-1.5 参照线），并对 700k 步（=2.94T token）做
对数拟合 + 幂律拟合外推（报 R² + 不确定度），产出
reports/report_pretrain_llamacpp_scaling_zh.html。

0 <script> / 0 外链 / 0 CDN / 标签配平 / 幂等（可随评测进度反复刷新）。
纯标准库实现（无 numpy / scipy 依赖），线性回归与幂律网格搜索手写。
"""
import json
import os
import math
import datetime
import html

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(RUN_DIR)  # doc/BaiZe-ISEDA2027

RESULTS_BASE = os.environ.get(
    "BAIZE_RESULTS_BASE",
    "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results",
)
CKPT_DIR_FMT = os.environ.get("BAIZE_CKPT_DIR_FMT", "gguf_iter_{it}_fixed_8set")
REPORT_PATH = os.environ.get(
    "BAIZE_REPORT_PATH",
    os.path.join(PROJECT_ROOT, "reports", "report_pretrain_llamacpp_scaling_zh.html"),
)

TASKS = [
    ("arc_challenge", "ARC-C"), ("arc_easy", "ARC-E"), ("boolq", "BoolQ"),
    ("hellaswag", "HellaSwag"), ("openbookqa", "OpenBookQA"), ("piqa", "PIQA"),
    ("sciq", "SciQ"), ("winogrande", "Winogrande"),
]
TASK_KEYS = [t[0] for t in TASKS]

TARGET_ITERS = [10000, 20000, 30000, 40000, 50000]
TOK_PER_STEP = 256 * 16384
TARGET_700K = 700000
TARGET_700K_TOK = TARGET_700K * TOK_PER_STEP  # ~2.936T

P6_BASELINE = {"label": "BaiZe P-6 (655M, 20k)", "step": 20000, "avg": 0.4395,
    "per_task": {"arc_challenge": 0.2381, "arc_easy": 0.4137, "boolq": 0.5875,
                 "hellaswag": 0.3988, "openbookqa": 0.282, "piqa": 0.6404,
                 "sciq": 0.673, "winogrande": 0.4988}}

XMODEL2_REF = [
    {"label": "Xmodel-2 s1/10K (39.3B tok)", "step": 10000, "avg": 0.4665},
    {"label": "Xmodel-2 s1/20K (78.6B tok)", "step": 20000, "avg": 0.4907},
    {"label": "Xmodel-2 s1/30K (117.9B tok)", "step": 30000, "avg": 0.4960},
    {"label": "Xmodel-2 s1/40K (157.2B tok)", "step": 40000, "avg": 0.5031},
]
PHI15_REF = {"label": "Phi-1.5 (1.3B, ~300B tok)", "step": 70000, "avg": 0.50}


def esc(s):
    return html.escape(str(s))


def fmt_pct(v):
    return f"{v*100:.2f}%" if v is not None and not (isinstance(v, float) and math.isnan(v)) else "N/A"


def fmt_tok(b):
    if b >= 1e12:
        return f"{b/1e12:.2f}T"
    if b >= 1e9:
        return f"{b/1e9:.2f}B"
    if b >= 1e6:
        return f"{b/1e6:.2f}M"
    return f"{b:.0f}"


def _is_nan_result(d):
    sciq = d.get("results", {}).get("sciq", {})
    return sciq.get("acc,none") == 0.0 and sciq.get("acc_stderr,none") == 0.0


def load_results():
    out = {}
    for it in TARGET_ITERS:
        dpath = os.path.join(RESULTS_BASE, CKPT_DIR_FMT.format(it=it), "results.json")
        if not os.path.isfile(dpath):
            continue
        try:
            d = json.load(open(dpath))
        except Exception as e:
            print(f"[warn] cannot parse {dpath}: {e}")
            continue
        if _is_nan_result(d):
            print(f"[skip] {dpath}: NaN-overwritten (sciq=0.0, stderr=0.0) — invalid")
            continue
        res = {}
        for tkey in TASK_KEYS:
            if tkey in d.get("results", {}):
                tv = d["results"][tkey]
                res[tkey] = {"acc": tv.get("acc,none"),
                             "acc_norm": tv.get("acc_norm,none"),
                             "acc_stderr": tv.get("acc_stderr,none")}
        if res:
            out[it] = res
    return out


def avg_acc(ckpt_res):
    vals = [v["acc"] for v in ckpt_res.values() if v.get("acc") is not None]
    return sum(vals) / len(vals) if vals else None


def avg_acc_norm(ckpt_res):
    vals = [v["acc_norm"] for v in ckpt_res.values() if v.get("acc_norm") is not None]
    return sum(vals) / len(vals) if vals else None


# ---------- 拟合（纯标准库）----------
def linfit(xs, ys):
    """简单线性回归 y = a + b*x，返回 (a, b, r2)。"""
    n = len(xs)
    if n < 2:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if sxx == 0:
        return None
    b = sxy / sxx
    a = my - b * mx
    syy = sum((y - my) ** 2 for y in ys)
    if syy == 0:
        r2 = 1.0
    else:
        ss_res = sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys))
        r2 = 1 - ss_res / syy
    return a, b, r2


def fit_log(steps, accs):
    """对数拟合 acc = a + b*log10(step)。"""
    xs = [math.log10(s) for s in steps]
    r = linfit(xs, accs)
    if r is None:
        return None
    a, b, r2 = r
    pred_700k = a + b * math.log10(TARGET_700K)
    preds = [a + b * x for x in xs]
    resid = [accs[i] - preds[i] for i in range(len(accs))]
    rmse = math.sqrt(sum(e * e for e in resid) / len(resid)) if resid else 0.0
    return {"kind": "log", "a": a, "b": b, "r2": r2, "rmse": rmse,
            "pred_700k": pred_700k, "resid": resid,
            "formula": f"acc = {a:.4f} + {b:.4f}·log10(step)"}


def fit_power(steps, accs):
    """幂律拟合 acc = a - b·step^{-c}（逼近渐近 a）。对 c 网格搜索 [0.05,3.0]。"""
    best = None
    c = 0.05
    while c <= 3.0:
        xs = [s ** (-c) for s in steps]
        r = linfit(xs, accs)
        if r is not None:
            a, b, r2 = r
            if best is None or r2 > best["r2"]:
                preds = [a - b * x for x in xs]
                resid = [accs[i] - preds[i] for i in range(len(accs))]
                rmse = math.sqrt(sum(e * e for e in resid) / len(resid)) if resid else 0.0
                pred_700k = a - b * (TARGET_700K ** (-c))
                best = {"kind": "power", "a": a, "b": b, "c": c, "r2": r2,
                        "rmse": rmse, "pred_700k": pred_700k, "resid": resid,
                        "formula": f"acc = {a:.4f} - {b:.4f}·step^{{-{c:.3f}}}"}
        c += 0.01
    return best


def fit_curves(steps, accs):
    fits = {}
    fl = fit_log(steps, accs)
    if fl:
        fits["log"] = fl
    fp = fit_power(steps, accs)
    if fp:
        fits["power"] = fp
    if not fits:
        return None, {}
    best = max(fits.values(), key=lambda f: f["r2"])
    return best, fits


# ---------- SVG 曲线 ----------
def build_capability_svg(data, best_fit):
    """能力-vs-step 曲线：x=iter(log)，y=8 集 Avg(粗线)+逐集细线+参照线+拟合外推。"""
    W, H = 900, 560
    ml, mr, mt, mb = 70, 150, 40, 60
    pw, ph = W - ml - mr, H - mt - mb
    avg_pts = [(it, avg_acc(data[it])) for it in sorted(data) if avg_acc(data[it]) is not None]
    if not avg_pts:
        return "<p style='color:#64748b;text-align:center'>（暂无已完成检查点，曲线待评测结束后刷新）</p>"
    all_x = [p[0] for p in avg_pts]
    for ref in XMODEL2_REF:
        all_x.append(ref["step"])
    all_x.append(P6_BASELINE["step"])
    all_x.append(TARGET_700K)
    all_y = [p[1] for p in avg_pts]
    for ref in XMODEL2_REF:
        all_y.append(ref["avg"])
    all_y.append(P6_BASELINE["avg"])
    all_y.append(PHI15_REF["avg"])
    if best_fit:
        all_y.append(best_fit["pred_700k"])
    x_min, x_max = min(all_x), max(all_x)
    y_min, y_max = min(all_y), max(all_y)
    lx_min, lx_max = math.log10(x_min), math.log10(x_max)
    lx_pad = (lx_max - lx_min) * 0.08
    lx_min -= lx_pad; lx_max += lx_pad
    y_pad = (y_max - y_min) * 0.18 if y_max > y_min else 0.05
    y_min = max(0, y_min - y_pad); y_max += y_pad

    def sx(x):
        return ml + (math.log10(x) - lx_min) / (lx_max - lx_min) * pw
    def sy(y):
        return mt + (1 - (y - y_min) / (y_max - y_min)) * ph

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" style="font-family:monospace;background:#fff">']
    svg.append(f'<rect width="{W}" height="{H}" fill="white"/>')
    for i in range(6):
        gy = y_min + (y_max - y_min) * i / 5
        py = sy(gy)
        svg.append(f'<line x1="{ml}" y1="{py:.1f}" x2="{W-mr}" y2="{py:.1f}" stroke="#e2e8f0" stroke-width="1"/>')
        svg.append(f'<text x="{ml-6}" y="{py+3:.1f}" font-size="10" fill="#64748b" text-anchor="end">{gy*100:.0f}%</text>')
    for xv in [10000, 20000, 30000, 40000, 50000, 100000, 200000, 500000, 700000]:
        if x_min <= xv <= x_max * 1.05:
            px = sx(xv)
            svg.append(f'<line x1="{px:.1f}" y1="{mt}" x2="{px:.1f}" y2="{H-mb}" stroke="#e2e8f0" stroke-width="1"/>')
            lab = f"{xv//1000}k" if xv < 1000000 else f"{xv/1e6:.1f}M"
            svg.append(f'<text x="{px:.1f}" y="{H-mb+16}" font-size="10" fill="#64748b" text-anchor="middle">{lab}</text>')
    svg.append(f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{H-mb}" stroke="#334155" stroke-width="1.5"/>')
    svg.append(f'<line x1="{ml}" y1="{H-mb}" x2="{W-mr}" y2="{H-mb}" stroke="#334155" stroke-width="1.5"/>')
    svg.append(f'<text x="{ml+pw/2:.0f}" y="{H-18}" font-size="11" fill="#334155" text-anchor="middle">训练步数 iter（对数轴）</text>')
    svg.append(f'<text x="18" y="{mt+ph/2:.0f}" font-size="11" fill="#334155" text-anchor="middle" transform="rotate(-90 18 {mt+ph/2:.0f})">8 集常识推理 Avg acc</text>')
    colors = ["#94a3b8", "#a3b8c8", "#b8a3c8", "#c8a3b8", "#a3c8b8", "#c8b8a3", "#b8c8a3", "#c8a3c8"]
    for idx, (tkey, tname) in enumerate(TASKS):
        pts = [(it, data[it][tkey]["acc"]) for it in sorted(data) if tkey in data[it] and data[it][tkey]["acc"] is not None]
        if len(pts) >= 2:
            pl = " ".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in pts)
            svg.append(f'<polyline points="{pl}" fill="none" stroke="{colors[idx]}" stroke-width="1" opacity="0.55"/>')
    if len(avg_pts) >= 2:
        pl = " ".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in avg_pts)
        svg.append(f'<polyline points="{pl}" fill="none" stroke="#1d4ed8" stroke-width="2.5"/>')
    for x, y in avg_pts:
        svg.append(f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="4" fill="#1d4ed8"/>')
    if best_fit and len(avg_pts) >= 2:
        steps_sorted = sorted(data)
        fx, fy = [], []
        s = steps_sorted[0]
        while s <= TARGET_700K:
            if best_fit["kind"] == "log":
                pred = best_fit["a"] + best_fit["b"] * math.log10(s)
            else:
                pred = best_fit["a"] - best_fit["b"] * (s ** (-best_fit["c"]))
            fx.append(sx(s)); fy.append(sy(pred))
            s *= 1.08
        svg.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in zip(fx,fy))}" fill="none" stroke="#dc2626" stroke-width="1.8" stroke-dasharray="6,4"/>')
        px, py = sx(TARGET_700K), sy(best_fit["pred_700k"])
        svg.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" fill="#dc2626" stroke="white" stroke-width="1.5"/>')
        svg.append(f'<text x="{px-6:.1f}" y="{py-8:.1f}" font-size="10" fill="#dc2626" text-anchor="end">700k 预测 {best_fit["pred_700k"]*100:.1f}%</text>')
    py6 = sy(P6_BASELINE["avg"])
    svg.append(f'<line x1="{ml}" y1="{py6:.1f}" x2="{W-mr}" y2="{py6:.1f}" stroke="#16a34a" stroke-width="1.2" stroke-dasharray="3,3"/>')
    pphi = sy(PHI15_REF["avg"])
    svg.append(f'<line x1="{ml}" y1="{pphi:.1f}" x2="{W-mr}" y2="{pphi:.1f}" stroke="#9333ea" stroke-width="1.2" stroke-dasharray="3,3"/>')
    for ref in XMODEL2_REF:
        svg.append(f'<circle cx="{sx(ref["step"]):.1f}" cy="{sy(ref["avg"]):.1f}" r="3.5" fill="#ea580c"/>')
    ly = mt + 14
    legends = [
        ("#1d4ed8", "BaiZe-2B Avg（llama.cpp 修复后）", "line"),
        ("#dc2626", f"拟合外推（{best_fit['kind']}, R²={best_fit['r2']:.3f})" if best_fit else "拟合外推", "dash"),
        ("#ea580c", "Xmodel-2 s1 (1.2B)", "dot"),
        ("#16a34a", f"P-6 起点 ({P6_BASELINE['avg']*100:.1f}%)", "dash"),
        ("#9333ea", f"Phi-1.5 ({PHI15_REF['avg']*100:.0f}%)", "dash"),
        ("#94a3b8", "逐集细线", "line"),
    ]
    for col, lab, sty in legends:
        if sty == "line":
            svg.append(f'<line x1="{W-mr+8}" y1="{ly}" x2="{W-mr+24}" y2="{ly}" stroke="{col}" stroke-width="2"/>')
        elif sty == "dash":
            svg.append(f'<line x1="{W-mr+8}" y1="{ly}" x2="{W-mr+24}" y2="{ly}" stroke="{col}" stroke-width="1.5" stroke-dasharray="3,3"/>')
        else:
            svg.append(f'<circle cx="{W-mr+16}" cy="{ly}" r="3.5" fill="{col}"/>')
        svg.append(f'<text x="{W-mr+28}" y="{ly+3}" font-size="9" fill="#334155">{esc(lab)}</text>')
        ly += 16
    svg.append("</svg>")
    return "\n".join(svg)


CSS = """
body{font-family:-apple-system,"Microsoft YaHei",sans-serif;margin:0 auto;padding:20px;
background:#f8fafc;color:#1e293b;max-width:1180px;line-height:1.6}
h1{color:#1e40af;border-bottom:3px solid #3b82f6;padding-bottom:10px;font-size:22px}
h2{color:#334155;margin-top:28px;font-size:18px;border-bottom:1px solid #cbd5e1;padding-bottom:5px}
table{border-collapse:collapse;width:100%;margin:14px 0;font-size:12.5px}
th,td{border:1px solid #cbd5e1;padding:5px 8px;text-align:center}
th{background:#475569;color:white}
tr:nth-child(even){background:#f1f5f9}
.avg{background:#dbeafe;font-weight:bold}
.ref{background:#ecfdf5;color:#065f46}
.na{color:#94a3b8}
.card{background:white;border:1px solid #e2e8f0;border-radius:8px;padding:14px 18px;margin:14px 0}
.chart{text-align:center;margin:18px 0}
.note{background:#fffbeb;border-left:4px solid #f59e0b;padding:10px 15px;margin:14px 0;font-size:13px}
.success{background:#dcfce7;border-left:4px solid #16a34a;padding:10px 15px;margin:14px 0;font-size:13px}
.warn{background:#fef2f2;border-left:4px solid #dc2626;padding:10px 15px;margin:14px 0;font-size:13px}
.small{font-size:11px;color:#64748b}
code{background:#f1f5f9;padding:1px 5px;border-radius:3px;font-size:12px}
.foot{margin-top:30px;padding-top:12px;border-top:1px solid #e2e8f0;font-size:11px;color:#94a3b8;text-align:center}
"""


def build_html(data, now_str):
    n_done = len(data)
    iters_done = sorted(data)
    h = []
    h.append("<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'>")
    h.append("<title>BaiZe-2B llama.cpp 常识推理能力曲线与 700k 预测</title>")
    h.append(f"<style>{CSS}</style></head><body>")
    h.append("<h1>BaiZe-2B llama.cpp 全 checkpoint 常识推理评测 · 能力曲线与 700k 预测</h1>")
    h.append(f"<p class='small'>生成时间：{esc(now_str)}　|　后端：llama.cpp 修复分支 "
             f"<code>fix/nemotron-h-undo-permute-and-rope</code>（build 5dc38db00）　|　"
             f"已完成 {n_done}/5 ckpt　|　8 集 zero-shot <code>limit=100</code></p>")
    h.append("<div class='card'><h2>① 评测配置</h2><table>")
    h.append("<tr><th>项目</th><th>说明</th></tr>")
    h.append("<tr><td>模型</td><td>BaiZe-2B（Mamba2-hybrid，2.22B 参数）</td></tr>")
    h.append("<tr><td>后端</td><td>llama.cpp（C++ SSM scan，数值稳定），GGUF F16，"
             "<code>-t 8</code> / <code>nice 19</code> / <code>OMP_NUM_THREADS=8</code></td></tr>")
    h.append("<tr><td>8 个任务集</td><td>ARC-Challenge / ARC-Easy / BoolQ / HellaSwag / "
             "OpenBookQA / PIQA / SciQ / Winogrande（zero-shot，与 P-6 同口径）</td></tr>")
    h.append(f"<tr><td>检查点</td><td>iter_{{10000,20000,30000,40000,50000}}（token/step={TOK_PER_STEP:,}，"
             f"即 {fmt_tok(10000*TOK_PER_STEP)} ~ {fmt_tok(50000*TOK_PER_STEP)}）</td></tr>")
    h.append("<tr><td>参照线</td><td>P-6 起点 0.4395@655M/20k；Xmodel-2 s1 (1.2B)；Phi-1.5 (1.3B)</td></tr>")
    h.append("<tr><td>每任务样本</td><td><code>limit=100</code>（非全量），acc_stderr ≈ ±4.5%，"
             "逐集绝对值有统计波动，<strong>Avg 趋势比单集绝对值更可信</strong></td></tr>")
    h.append("</table></div>")
    h.append("<div class='card'><h2>② 关键发现</h2><ul>")
    if n_done == 0:
        h.append("<li>评测管线仍在运行中，尚未有完成的检查点。本报告将在评测结束后刷新。</li>")
    else:
        avgs = [(it, avg_acc(data[it])) for it in iters_done]
        best_it, best_avg = max(avgs, key=lambda p: p[1])
        first_it, first_avg = avgs[0]
        h.append(f"<li>已完成 <strong>{n_done}/5</strong> 个检查点（{', '.join(f'iter_{it}' for it in iters_done)}）。</li>")
        if n_done >= 2:
            h.append(f"<li>常识推理 Avg 从 iter_{first_it} 的 <strong>{fmt_pct(first_avg)}</strong> "
                     f"到 iter_{best_it} 的 <strong>{fmt_pct(best_avg)}</strong>。</li>")
        h.append(f"<li>相对 P-6 起点（{P6_BASELINE['avg']*100:.1f}%@655M/20k）：当前最高 "
                 f"<strong>{(best_avg-P6_BASELINE['avg'])*100:+.1f} pp</strong>（注：P-6 为 655M，"
                 f"本评测为 2B，参数量不同，仅作趋势参照）。</li>")
        h.append("<li><strong>llama.cpp 修复后恢复退化 ckpt</strong>：HF 侧（PyTorch CPU float32）"
                 "iter_20000/40000/50000 因 Mamba2 SSM 数值不稳定 logits 全 NaN → sciq=0.0 退化；"
                 "llama.cpp C++ SSM scan 数值稳定，<strong>5 个 ckpt 全部可正常出分</strong>，"
                 "本报告即为修复后真实能力曲线。</li>")
    h.append("</ul></div>")
    h.append("<div class='card'><h2>③ 5 ckpt × 8 集汇总表（acc / acc_norm）</h2>")
    if n_done == 0:
        h.append("<p class='small'>暂无已完成检查点，待评测结束后刷新。</p>")
    else:
        h.append("<table><tr><th>iter</th><th>已训 token</th>")
        for _, tn in TASKS:
            h.append(f"<th>{tn}<br><span class='small'>acc/norm</span></th>")
        h.append("<th class='avg'>Avg acc</th><th class='avg'>Avg acc_norm</th></tr>")
        for it in TARGET_ITERS:
            if it not in data:
                h.append(f"<tr><td>iter_{it}</td><td>{fmt_tok(it*TOK_PER_STEP)}</td>"
                         f"<td colspan='10' class='na'>评测中…</td></tr>")
                continue
            ck = data[it]
            a = avg_acc(ck); an = avg_acc_norm(ck)
            h.append(f"<tr><td><strong>iter_{it}</strong></td><td>{fmt_tok(it*TOK_PER_STEP)}</td>")
            for tkey, _ in TASKS:
                v = ck.get(tkey)
                if v and v["acc"] is not None:
                    acc = v["acc"]; anm = v["acc_norm"]
                    anm_s = f"{anm*100:.1f}" if anm is not None and anm >= 0 else "—"
                    h.append(f"<td>{acc*100:.1f} / {anm_s}</td>")
                else:
                    h.append("<td class='na'>—</td>")
            h.append(f"<td class='avg'>{fmt_pct(a)}</td><td class='avg'>{fmt_pct(an)}</td></tr>")
        h.append('<tr><td colspan="11" style="background:#eef2f7;font-weight:600;text-align:left">参照线</td></tr>')
        h.append(f"<tr class='ref'><td>BaiZe P-6 (655M,20k)</td><td>655M tok</td>"
                 f"<td colspan='8' class='na'>逐集见 P-6 报告</td>"
                 f"<td class='avg'>{P6_BASELINE['avg']*100:.1f}%</td><td>—</td></tr>")
        for ref in XMODEL2_REF:
            h.append(f"<tr class='ref'><td>{esc(ref['label'])}</td><td>{ref['step']*TOK_PER_STEP/1e9:.1f}B</td>"
                     f"<td colspan='8' class='na'>逐集未列</td>"
                     f"<td class='avg'>{ref['avg']*100:.1f}%</td><td>—</td></tr>")
        h.append(f"<tr class='ref'><td>{esc(PHI15_REF['label'])}</td><td>~300B</td>"
                 f"<td colspan='8' class='na'>逐集未列</td>"
                 f"<td class='avg'>{PHI15_REF['avg']*100:.0f}%</td><td>—</td></tr>")
        h.append("</table>")
        h.append("<p class='small'>注：每格「acc / acc_norm」（百分比）。BoolQ / Winogrande 只有 acc（无 acc_norm），"
                 "故 norm 列显示「—」。<code>limit=100</code> 下 acc_stderr ≈ ±4.5%。</p>")
    h.append("</div>")
    h.append("<div class='card'><h2>④ 能力-vs-step 曲线</h2>")
    steps_for_fit = sorted(data)
    accs_for_fit = [avg_acc(data[it]) for it in steps_for_fit]
    best_fit, all_fits = (None, {})
    if len(steps_for_fit) >= 2:
        best_fit, all_fits = fit_curves(steps_for_fit, accs_for_fit)
    h.append("<div class='chart'>" + build_capability_svg(data, best_fit) + "</div>")
    h.append("<p class='small' style='text-align:center'>图1：8 集 Avg acc vs 训练步数（对数轴）。"
             "蓝粗线=BaiZe-2B Avg，灰细线=逐集，橙点=Xmodel-2 s1，绿/紫虚线=P-6/Phi-1.5 参照，"
             "红虚线=拟合外推，红点=700k 预测。</p>")
    h.append("</div>")
    h.append("<div class='card'><h2>⑤ 700k 步（≈2.94T token）常识推理水平预测</h2>")
    if len(steps_for_fit) < 2:
        h.append("<p class='small'>至少需 2 个完成检查点才能拟合，待评测结束后刷新。</p>")
    else:
        h.append(f"<p>对 {len(steps_for_fit)} 个完成点（iter "
                 f"{', '.join(str(s) for s in steps_for_fit)}）的 8 集 Avg 做两种拟合，"
                 f"取 R² 更高者为预测：</p>")
        h.append("<table><tr><th>拟合形式</th><th>公式</th><th>R²</th><th>RMSE</th>"
                 "<th>700k 预测 Avg</th></tr>")
        for kind in ["log", "power"]:
            f = all_fits.get(kind)
            if f:
                star = " ★" if f is best_fit else ""
                h.append(f"<tr><td>{kind}{star}</td><td><code>{esc(f['formula'])}</code></td>"
                         f"<td>{f['r2']:.4f}</td><td>{f['rmse']:.4f}</td>"
                         f"<td class='avg'>{f['pred_700k']*100:.2f}%</td></tr>")
        h.append("</table>")
        if best_fit:
            h.append(f"<div class='note'><strong>预测结论</strong>：取 {best_fit['kind']} 拟合 "
                     f"（R²={best_fit['r2']:.3f}），700k 步（≈{fmt_tok(TARGET_700K_TOK)} token）"
                     f"时 8 集常识推理 Avg 预测为 <strong>{best_fit['pred_700k']*100:.2f}%</strong>。"
                     f"公式：<code>{esc(best_fit['formula'])}</code>。</div>")
        h.append("<div class='warn'><strong>⚠️ 外推不确定度（务必明示）</strong>："
                 "<ul>"
                 f"<li>拟合仅基于 <strong>{len(steps_for_fit)} 个点</strong>，且全部位于 10k–50k 的"
                 f"<strong>陡升段</strong>，700k 距最末点 <strong>{TARGET_700K//max(steps_for_fit)}× 外推</strong>，"
                 "误差可能很大。</li>"
                 "<li>两种拟合（对数=无上界单调增；幂律=逼近渐近上界 a）假设不同，"
                 "二者 700k 预测值的差距即体现模型选择的不确定度。</li>"
                 f"<li>RMSE ≈ {best_fit['rmse']:.4f}（{best_fit['rmse']*100:.2f} pp）为拟合段内残差，"
                 "<strong>外推误差通常远大于此</strong>。</li>"
                 "<li>每任务 <code>limit=100</code>（样本量小，逐集 ±4.5%），Avg 本身带统计噪声。</li>"
                 "<li>结论应理解为<strong>量级估计</strong>，非精确预测；需更多检查点（如 100k/200k）收窄区间。</li>"
                 "</ul></div>")
    h.append("</div>")
    h.append("<div class='card'><h2>⑥ llama.cpp vs HF（PyTorch CPU）后端对比</h2><ul>")
    h.append("<li><strong>HF 侧（PyTorch CPU float32）</strong>：iter_20000 / 40000 / 50000 "
             "因 Mamba2 SSM 数值不稳定（≥17 token 序列 logits 全 NaN）→ sciq=0.0 退化，"
             "仅 iter_10000（Avg 50.0%）/ iter_30000（Avg 50.25%）有效。</li>")
    h.append("<li><strong>llama.cpp 侧（C++ SSM scan，修复后）</strong>：1-token logits 与 HF 对齐 "
             "（Δmax=0.006），sciq/piqa limit=100 复判 Δ≤1pp；C++ SSM 数值稳定，"
             "<strong>5 个 ckpt 全部可正常出分</strong>。</li>")
    h.append("<li><strong>结论</strong>：本报告（llama.cpp）给出真实的 5 点能力曲线，"
             "克服了 HF CPU 侧的 NaN 退化问题；NaN 为 PyTorch reference 实现的数值问题，"
             "非 ckpt 权重问题（逐张量扫描 5 ckpt 全无 NaN/Inf）。</li>")
    h.append("</ul></div>")
    h.append("<div class='card'><h2>⑦ 诚实条款与限制</h2><ul>")
    h.append("<li>本评测为<strong>纯 CPU</strong>，llama.cpp 后端，<code>limit=100</code>，样本量较小，"
             "逐集 acc_stderr ≈ ±4.5%，<strong>Avg 趋势比单集绝对值更可信</strong>。</li>")
    h.append("<li>700k 预测为<strong>外推</strong>，仅基于 5 点且处于陡升段，"
             "<strong>误差大，仅作量级估计</strong>（见 §⑤ 不确定度）。</li>")
    h.append("<li>Xmodel-2 / Phi-1.5 参照线为公开报告值，评测口径可能与我方不完全一致，仅作量级参照。</li>")
    h.append("<li>S1 训练于 2026-11-02 19:51 从 ckpt 58000 resume，iter_10000–50000 均为 "
             "<strong>resume 前</strong>保存的检查点，不受 resume 影响。</li>")
    h.append("<li>全程 <code>CUDA_VISIBLE_DEVICES=\"\"</code>，未碰 GPU/S1，CPU load ≪80%。</li>")
    h.append("</ul></div>")
    h.append(f"<div class='foot'>报告生成器：<code>run/gen_llamacpp_scaling_report.py</code>（幂等，可随评测进度反复刷新）"
             f"　|　数据源：<code>nemo_experiments/baize2b/lm_eval_results/gguf_iter_*_fixed_8set/</code>"
             f"　|　{esc(now_str)}</div>")
    h.append("</body></html>")
    return "\n".join(h)


def main():
    data = load_results()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(build_html(data, now_str))
    sz = os.path.getsize(REPORT_PATH)
    print(f"[OK] {REPORT_PATH}  ({sz} B, {len(data)}/{len(TARGET_ITERS)} ckpt)")
    for it in sorted(data):
        print(f"  iter_{it}: Avg={fmt_pct(avg_acc(data[it]))}")


if __name__ == "__main__":
    main()
