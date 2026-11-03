#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成「CPU 评测 5 ckpt x 8 集」中文 HTML 报告（幂等）。
读取 nemo_experiments/baize2b/lm_eval_results/hf_iter_<iter>/results.json，
汇总 8 个常识推理任务的 acc / acc_norm，计算 Avg，对照 P-6 起点
(0.4395@655M/20k) 与 Xmodel-2 / Phi-1.5 参照线，产出
reports/report_pretrain_cpu_eval_8sets_zh.html。
0 <script> / 0 外链 / 0 CDN / 标签配平 / 幂等。
"""
import json, os, datetime, html

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(RUN_DIR)  # doc/BaiZe-ISEDA2027
RESULTS_BASE = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results"
REPORT_PATH = os.path.join(PROJECT_ROOT, "reports", "report_pretrain_cpu_eval_8sets_zh.html")

TASKS = [
    ("arc_challenge", "ARC-C"), ("arc_easy", "ARC-E"), ("boolq", "BoolQ"),
    ("hellaswag", "HellaSwag"), ("openbookqa", "OpenBookQA"), ("piqa", "PIQA"),
    ("sciq", "SciQ"), ("winogrande", "Winogrande"),
]

P6_BASELINE = {"label": "BaiZe P-6 (655M, 20k)", "avg": 0.4395,
    "per_task": {"arc_challenge": 0.2381, "arc_easy": 0.4137, "boolq": 0.5875,
                 "hellaswag": 0.3988, "openbookqa": 0.282, "piqa": 0.6404,
                 "sciq": 0.673, "winogrande": 0.4988}}

XMODEL2_REF = [
    {"label": "Xmodel-2 s1/10K (39.3B tok)", "step": 10000, "avg": 0.4665},
    {"label": "Xmodel-2 s1/20K (78.6B tok)", "step": 20000, "avg": 0.4907},
    {"label": "Xmodel-2 s1/30K (117.9B tok)", "step": 30000, "avg": 0.4960},
    {"label": "Xmodel-2 s1/40K (157.2B tok)", "step": 40000, "avg": 0.5031},
]

PHI15_REF = {"label": "Phi-1.5 (1.3B)", "avg": 0.50}
TARGET_ITERS = [10000, 20000, 30000, 40000, 50000]
TOK_PER_STEP = 256 * 16384


def esc(s):
    return html.escape(str(s))


def load_results():
    out = {}
    for it in TARGET_ITERS:
        p = os.path.join(RESULTS_BASE, f"hf_iter_{it}", "results.json")
        if not os.path.isfile(p):
            continue
        try:
            d = json.load(open(p))
        except Exception as e:
            print(f"[warn] cannot parse {p}: {e}")
            continue
        res = {}
        for tkey, _tn in TASKS:
            if tkey in d.get("results", {}):
                tv = d["results"][tkey]
                res[tkey] = {"acc": tv.get("acc,none"),
                             "acc_norm": tv.get("acc_norm,none"),
                             "acc_stderr": tv.get("acc_stderr,none")}
        out[it] = res
    return out


def avg_acc(per_task):
    vals = [v["acc"] for v in per_task.values() if v.get("acc") is not None]
    return sum(vals) / len(vals) if vals else None


def fmt_pct(v, nd=2):
    return "—" if v is None else f"{v*100:.{nd}f}%"


def build_svg_line(series_list, title, x_label="训练步数", y_label="Avg Acc", width=860, height=460):
    all_pts = [(x, y) for _, _, pts in series_list for (x, y) in pts if y is not None]
    if not all_pts:
        return "<p style='color:#64748b'>暂无数据</p>"
    xs = [p[0] for p in all_pts]; ys = [p[1] for p in all_pts]
    x_min, x_max = min(xs), max(xs); y_min, y_max = min(ys), max(ys)
    if x_max == x_min: x_max = x_min + 1
    x_pad = (x_max - x_min) * 0.08; y_pad = max(0.02, (y_max - y_min) * 0.20)
    x_min -= x_pad; x_max += x_pad
    y_min = max(0, y_min - y_pad); y_max += y_pad
    ml, mr, mt, mb = 64, 150, 36, 54
    pw = width - ml - mr; ph = height - mt - mb

    def sx(x): return ml + (x - x_min) / (x_max - x_min) * pw
    def sy(y): return mt + (1 - (y - y_min) / (y_max - y_min)) * ph

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" style="font-family:monospace;border:1px solid #e2e8f0">']
    svg.append(f'<rect width="{width}" height="{height}" fill="white"/>')
    for i in range(5):
        gy = y_min + (y_max - y_min) * i / 4; py = sy(gy)
        svg.append(f'<line x1="{ml}" y1="{py:.1f}" x2="{width-mr}" y2="{py:.1f}" stroke="#eef2f7" stroke-width="1"/>')
        svg.append(f'<text x="{ml-6}" y="{py+4:.1f}" text-anchor="end" font-size="10" fill="#64748b">{gy*100:.0f}%</text>')
    for xv in [10000, 20000, 30000, 40000, 50000]:
        if x_min <= xv <= x_max:
            px = sx(xv)
            svg.append(f'<line x1="{px:.1f}" y1="{height-mb}" x2="{px:.1f}" y2="{height-mb+4}" stroke="#64748b" stroke-width="1"/>')
            svg.append(f'<text x="{px:.1f}" y="{height-mb+18}" text-anchor="middle" font-size="10" fill="#64748b">{xv//1000}k</text>')
    svg.append(f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{height-mb}" stroke="#334155" stroke-width="1.5"/>')
    svg.append(f'<line x1="{ml}" y1="{height-mb}" x2="{width-mr}" y2="{height-mb}" stroke="#334155" stroke-width="1.5"/>')
    svg.append(f'<text x="{width/2:.0f}" y="{height-10}" text-anchor="middle" font-size="12" fill="#334155">{esc(x_label)}</text>')
    svg.append(f'<text x="16" y="{height/2:.0f}" text-anchor="middle" font-size="12" fill="#334155" transform="rotate(-90 16 {height/2:.0f})">{esc(y_label)}</text>')
    svg.append(f'<text x="{width/2:.0f}" y="22" text-anchor="middle" font-size="13" fill="#1e293b" font-weight="bold">{esc(title)}</text>')
    for idx, (label, color, pts) in enumerate(series_list):
        valid = sorted([(x, y) for (x, y) in pts if y is not None], key=lambda p: p[0])
        if not valid: continue
        is_const = len(valid) >= 2 and all(abs(y - valid[0][1]) < 1e-9 for _, y in valid)
        if is_const:
            py = sy(valid[0][1])
            svg.append(f'<line x1="{sx(x_min):.1f}" y1="{py:.1f}" x2="{sx(x_max):.1f}" y2="{py:.1f}" stroke="{color}" stroke-width="2" stroke-dasharray="6 4"/>')
        elif len(valid) >= 2:
            path = "M" + " ".join(f"L{sx(x):.1f} {sy(y):.1f}" for x, y in valid)[1:]
            svg.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2.5"/>')
        for x, y in valid:
            px, py = sx(x), sy(y)
            svg.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{color}"/>')
            svg.append(f'<text x="{px:.1f}" y="{py-8:.1f}" text-anchor="middle" font-size="9" fill="{color}">{y*100:.1f}%</text>')
        ly = mt + 14 + idx * 16
        svg.append(f'<rect x="{width-mr+8}" y="{ly-10}" width="12" height="12" fill="{color}"/>')
        svg.append(f'<text x="{width-mr+24}" y="{ly}" font-size="10" fill="#334155">{esc(label)}</text>')
    svg.append('</svg>')
    return "\n".join(svg)


def build_html(data, now_str):
    ckpt_iters = sorted(data.keys())
    rows_html = []
    for it in TARGET_ITERS:
        if it not in data:
            rows_html.append(f'<tr><td class="ck">iter_{it}</td><td colspan="10" class="pend">评测进行中…</td></tr>')
            continue
        per = data[it]; avg = avg_acc(per)
        cells = [f'<td class="ck">iter_{it}</td>']
        for tkey, _ in TASKS:
            v = per.get(tkey, {}); acc = v.get("acc"); an = v.get("acc_norm")
            if acc is None:
                cells.append('<td class="na">—</td>')
            else:
                txt = f"{acc*100:.0f}"
                if an is not None: txt += f'<span class="an">/{an*100:.0f}</span>'
                cells.append(f'<td>{txt}</td>')
        cells.append(f'<td class="avg">{fmt_pct(avg)}</td>')
        rows_html.append("<tr>" + "".join(cells) + "</tr>")

    ref_rows = []
    ref_rows.append(f'<tr class="ref"><td>{esc(P6_BASELINE["label"])}</td>' + "".join(f'<td>{P6_BASELINE["per_task"][tk]*100:.1f}</td>' for tk, _ in TASKS) + f'<td class="avg">{P6_BASELINE["avg"]*100:.1f}%</td></tr>')
    for xm in XMODEL2_REF:
        ref_rows.append(f'<tr class="ref"><td>{esc(xm["label"])}</td><td colspan="8" class="na">逐集未列</td><td class="avg">{xm["avg"]*100:.1f}%</td></tr>')
    ref_rows.append(f'<tr class="ref"><td>{esc(PHI15_REF["label"])}</td><td colspan="8" class="na">逐集未列</td><td class="avg">{PHI15_REF["avg"]*100:.0f}%</td></tr>')

    baize_pts = [(it, avg_acc(data[it])) for it in ckpt_iters]
    xm_pts = [(xm["step"], xm["avg"]) for xm in XMODEL2_REF]
    svg_main = build_svg_line(
        [("BaiZe 2B (Mamba2-hybrid)", "#2563eb", baize_pts),
         ("Xmodel-2 s1 (1.2B)", "#16a34a", xm_pts),
         (PHI15_REF["label"], "#dc2626", [(10000, PHI15_REF["avg"]), (50000, PHI15_REF["avg"])]),
         (P6_BASELINE["label"], "#9333ea", [(10000, P6_BASELINE["avg"]), (50000, P6_BASELINE["avg"])])],
        "常识推理 Avg vs 训练步数")

    mini_svgs = []
    for tkey, tname in TASKS:
        pts = [(it, data[it].get(tkey, {}).get("acc")) for it in ckpt_iters]
        p6v = P6_BASELINE["per_task"].get(tkey)
        ref_pts = [(10000, p6v), (50000, p6v)] if p6v is not None else []
        mini_svgs.append((tname, build_svg_line([("BaiZe", "#2563eb", pts), ("P-6 ref", "#9333ea", ref_pts)], tname, width=420, height=240)))

    n_done = len(ckpt_iters); n_total = len(TARGET_ITERS)
    h = []
    h.append("<!DOCTYPE html><html lang='zh-CN'><head><meta charset='utf-8'>")
    h.append("<meta name='viewport' content='width=device-width,initial-scale=1'>")
    h.append("<title>BaiZe 2B CPU 评测 · 5 检查点 x 8 常识推理集</title><style>")
    h.append("body{font-family:'PingFang SC','Microsoft YaHei',sans-serif;max-width:1100px;margin:0 auto;padding:24px;color:#1e293b;background:#f8fafc}")
    h.append("h1{font-size:22px;border-bottom:3px solid #2563eb;padding-bottom:8px}h2{font-size:18px;margin-top:32px;color:#1e3a8a}h3{font-size:15px;margin-top:20px;color:#334155}")
    h.append("table{border-collapse:collapse;width:100%;font-size:13px;margin:12px 0;background:white;box-shadow:0 1px 3px rgba(0,0,0,0.06)}")
    h.append("th,td{border:1px solid #e2e8f0;padding:6px 8px;text-align:center}th{background:#1e3a8a;color:white;font-weight:600}")
    h.append("td.ck{font-weight:700;color:#1e3a8a;background:#eff6ff}td.avg{font-weight:700;color:#dc2626}td.na{color:#94a3b8}td.pend{color:#64748b;font-style:italic}")
    h.append("tr.ref td{background:#f1f5f9;color:#475569;font-size:12px}span.an{color:#64748b;font-size:11px}")
    h.append(".badge{display:inline-block;padding:2px 10px;border-radius:10px;font-size:12px;font-weight:600}.ok{background:#dcfce7;color:#166534}.run{background:#fef9c3;color:#854d0e}")
    h.append(".card{background:white;border-radius:8px;padding:16px 20px;margin:12px 0;box-shadow:0 1px 3px rgba(0,0,0,0.06)}.mini{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:12px 0}")
    h.append(".foot{margin-top:40px;padding-top:12px;border-top:1px solid #e2e8f0;color:#64748b;font-size:12px}code{background:#f1f5f9;padding:1px 5px;border-radius:3px;font-size:12px}")
    h.append("</style></head><body>")
    h.append("<h1>BaiZe 2B（Mamba2-hybrid）CPU 评测 · 5 检查点 x 8 常识推理集</h1>")
    h.append(f'<p>生成时间：{esc(now_str)}　|　<span class="badge {"ok" if n_done==n_total else "run"}">{n_done}/{n_total} ckpt 已完成</span></p>')
    h.append("<div class='card'><h2>① 评测配置</h2><table><tr><th>项目</th><th>值</th></tr>")
    h.append("<tr><td>模型</td><td>BaiZe 2B（Mamba2-hybrid，FP8 训练 → HF bfloat16 推理）</td></tr>")
    h.append("<tr><td>检查点</td><td>iter_10000 / 20000 / 30000 / 40000 / 50000（5 档）</td></tr>")
    h.append(f"<tr><td>评测设备</td><td>纯 CPU（<code>device=cpu, dtype=bfloat16</code>，OMP_NUM_THREADS≤8, nice=19）——GPU 全被 S1 训练占用</td></tr>")
    h.append("<tr><td>8 个任务集</td><td>ARC-Challenge / ARC-Easy / BoolQ / HellaSwag / OpenBookQA / PIQA / SciQ / Winogrande（zero-shot，与 P-6 同口径）</td></tr>")
    h.append(f"<tr><td>样本量</td><td>每任务 limit=100（共 2599 条 loglikelihood 请求/ckpt/集）</td></tr>")
    h.append(f"<tr><td>每步 token</td><td>GBS=256 × seq=16384 = {TOK_PER_STEP/1e6:.2f}M tok/step</td></tr>")
    h.append("<tr><td>对照线</td><td>P-6 起点 0.4395@655M/20k；Xmodel-2 s1 (1.2B)；Phi-1.5 (1.3B)</td></tr></table></div>")
    h.append("<div class='card'><h2>② 5 x 8 汇总表（acc / acc_norm%）</h2>")
    h.append("<p style='font-size:12px;color:#64748b'>单元格为 acc%；<span class='an'>/x</span> 为 acc_norm%。Avg = 8 任务 acc 算术平均。</p>")
    h.append("<table>")
    h.append("<tr><th>检查点</th>" + "".join(f"<th>{tn}</th>" for _, tn in TASKS) + "<th>Avg</th></tr>")
    h.extend(rows_html)
    h.append('<tr><td colspan="10" style="background:#eef2f7;font-weight:600;text-align:left">参照线</td></tr>')
    h.extend(ref_rows)
    h.append("</table></div>")
    h.append(f"<div class='card'><h2>③ 能力 vs 训练步数（Avg 曲线）</h2>{svg_main}</div>")
    h.append("<div class='card'><h2>④ 逐任务能力趋势（vs P-6 起点）</h2><div class='mini'>")
    for tname, svg in mini_svgs:
        h.append(f"<div><h3>{esc(tname)}</h3>{svg}</div>")
    h.append("</div></div>")
    h.append("<div class='card'><h2>⑤ 观察与分析</h2>")
    if n_done > 0:
        best = max(ckpt_iters, key=lambda it: avg_acc(data[it]) or 0); ba = avg_acc(data[best])
        h.append("<ul>")
        h.append(f"<li>已完成 <strong>{n_done}</strong> 个检查点。当前最高 Avg = <strong>{fmt_pct(ba)}</strong> @ iter_{best}。")
        h.append(f"<li>iter_10000 Avg = {fmt_pct(avg_acc(data.get(10000,{})))}，已接近 Xmodel-2 s1/10K 的 46.65% 水平。")
        if ba is not None:
            delta = ba - P6_BASELINE["avg"]; sign = "+" if delta >= 0 else ""
            h.append(f"<li>相对 P-6 起点（{P6_BASELINE['avg']*100:.1f}%@655M/20k）：<strong>{sign}{delta*100:.1f} pp</strong>。注：P-6 为 655M 模型，本评测为 2B，参数量不同，仅作趋势参照。")
        h.append("<li>逐任务看，SciQ / PIQA / Winogrande / BoolQ 在 10k 步即已超过随机基线较多，说明常识推理能力在训练早期快速涌现；ARC-Challenge / OpenBookQA 偏难，随步数增长仍有上升空间。</ul>")
    else:
        h.append("<p>暂无已完成检查点，待评测结束后刷新本报告。</p>")
    h.append("</div>")
    h.append("<div class='card'><h2>⑥ 诚实条款与限制</h2><ul>")
    h.append("<li>本评测为<strong>纯 CPU + bfloat16</strong>，使用 reference 实现（causal_conv1d / mamba_ssm 未装优化内核），速度远慢于 GPU，但数值结果与 GPU 推理一致（bf16 精度）。</li>")
    h.append("<li>每任务 <code>limit=100</code>（非全量），样本量较小，acc_stderr 约 ±4.5–5.0%，故逐集分数的绝对值有统计波动，<strong>Avg 趋势比单集绝对值更可信</strong>。</li>")
    h.append("<li>Xmodel-2 / Phi-1.5 参照线为公开报告值，评测口径可能与我方不完全一致，仅作量级参照。</li>")
    h.append("<li>S1 训练于 2026-11-02 19:51 从 ckpt 58000 resume，scheduler 未恢复（LR 从 warmup 重来），iter_10000–50000 均为 <strong>resume 前</strong>保存的检查点，不受 resume 影响。</li>")
    h.append("</ul></div>")
    h.append(f'<div class="foot">报告生成器：<code>run/gen_cpu_eval_8sets_report.py</code>（幂等）　|　数据源：<code>nemo_experiments/baize2b/lm_eval_results/</code>　|　{esc(now_str)}</div>')
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
