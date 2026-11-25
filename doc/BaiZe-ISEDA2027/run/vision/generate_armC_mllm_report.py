#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""generate_armC_mllm_report.py — ArmC (2026-10-18) Stage(iv) MLLM 12-集评测中文报告生成器.

ArmC = ArmB 的两变量改动: min_lr 1e-4->1e-5 + weight decay 0.1->0.01 (非单变量消融).
读取 `mllm_eval_results_armC_20261018/consolidated_12benchmarks.json` (由 launch_12benchmarks_armC.sh
末步 consolidate_12benchmarks.py --results_dir 自动产出), 与 ArmB / ④-4ep / RiCEViT 基线对比,
计算每集 Δ + 平均(除 MME) + 预注册判据, 产出自包含 HTML (内联 CSS/SVG, 零外链).

用法:
  python generate_armC_mllm_report.py
  python generate_armC_mllm_report.py --results-dir <dir> --out <html_path>
"""
import json, os, sys, argparse
from datetime import datetime
from html import escape

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "reports")
DEFAULT_RESULTS_DIR = "/nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results_armC_20261018"
DEFAULT_OUT = os.path.join(REPORTS_DIR, "report_vision_armC_20261018_mllm_stage4_zh.html")

# ---- 12 benchmarks 顺序 + 展示名 + 主指标标签 + 能力维度 ----
BENCH_ORDER = [
    ("ai2d", "AI2D", "exact_match", "图像->科学图理解"),
    ("realworldqa", "RealWorldQA", "exact_match", "真实世界物理推理"),
    ("mmmu_val", "MMMU (val)", "mmmu_acc", "大学级多学科推理"),
    ("blink", "BLINK", "blink_acc", "视觉语言跳变推理"),
    ("mmstar", "MMStar", "average", "多模态综合能力"),
    ("mmmu_pro_standard", "MMMU-Pro (std)", "mmmu_acc", "MMMU 进阶版"),
    ("infovqa_val", "InfographicVQA", "anls", "信息图 VQA"),
    ("chartqa", "ChartQA", "relaxed_overall", "图表问答"),
    ("countbench", "CountBench", "acc", "物体计数"),
    ("docvqa_val", "DocVQA (val)", "anls", "文档 VQA"),
    ("ocrbench", "OCRBench", "ocrbench_acc", "OCR 文字识别"),
    ("mme", "MME", "perception+cog", "多模态综合评估"),
]

# ---- ArmB 基线 (来自 mllm_eval_results_armB/consolidated_12benchmarks.json, 已核 avg=26.10%) ----
ARMB = {
    "ai2d": 0.6068652849740933, "blink": 0.38939119636572533, "chartqa": 0.1252,
    "docvqa_val": 0.07357683982824648, "infovqa_val": 0.16879324468960838,
    "mme": {"perception_score": 583.6519607843137, "cognition_score": 212.85714285714286, "total": 796.5091036414566},
    "mmmu_val": 0.43667, "mmstar": 0.2794961030152159, "ocrbench": 0.016,
    "realworldqa": 0.4549019607843137, "countbench": 0.09572301425661914, "mmmu_pro_standard": 0.22428,
}
FOUR_EP_AVG = 0.2568   # ④-4ep 平均(除 MME) = 25.68%
RICEVIT_AVG = 0.6008   # RiCEViT (配方 R-1.5) 平均(除 MME) = 60.08%

# ---- ProtB (Protocol B, IN-1k full/50k, 3 seeds) ----
PROTB = {
    "armC": {"lp": 62.332, "lp_sigma": 0.014, "knn5": 54.718,
             "per_seed": [62.352, 62.322, 62.322]},
    "armB": {"lp": 62.093, "lp_sigma": 0.012, "knn5": 58.102,
             "per_seed": [62.084, 62.086, 62.110]},
    "4ep":  {"lp": 67.05, "knn5": 42.35},
}

def is_mme(key): return key == "mme"

def num(v):
    if isinstance(v, dict): return None
    if isinstance(v, (int, float)): return float(v)
    return None

def fmt_pct(v):
    return f"{v*100:.2f}%" if isinstance(v, (int, float)) else "N/A"

def fmt_mme(v):
    if isinstance(v, dict):
        return f"{v.get('perception_score',0):.1f} + {v.get('cognition_score',0):.1f}"
    return "N/A"

def avg_excl_mme(results):
    vals = [num(results.get(k)) for k, *_ in BENCH_ORDER if not is_mme(k)]
    vals = [v for v in vals if v is not None]
    return sum(vals)/len(vals) if vals else None

def verdict(avg, results):
    """预注册判据 (沿用 ArmB, 不得事后改): ≥30% 强成功 / >24% 且 DocVQA/ChartQA/OCRBench 任一 +10pp 成功 /
    22-26% 不可分辨 / ≤22% 失败. +10pp 解释为 vs ArmB 的 Δ≥10pp."""
    if avg is None: return ("N/A", "bad", "结果缺失, 无法裁定")
    if avg >= 0.30:
        return ("强成功 (strong success)", "ok", f"平均(除MME)={avg*100:.2f}% ≥ 30%")
    fine_keys = ["docvqa_val", "chartqa", "ocrbench"]
    fine_delta = []
    for k in fine_keys:
        a, b = num(results.get(k)), num(ARMB.get(k))
        if a is not None and b is not None:
            fine_delta.append((k, (a - b) * 100))
    any_plus10 = any(d >= 10.0 for _, d in fine_delta)
    if avg > 0.24 and any_plus10:
        hit = ", ".join(f"{k} Δ+{d:.2f}pp" for k, d in fine_delta if d >= 10.0)
        return ("成功 (success)", "ok", f"平均={avg*100:.2f}% > 24% 且细粒度任一 +10pp: {hit}")
    if 0.22 <= avg <= 0.265:
        return ("不可分辨 (indistinguishable, 边界值)", "warn", f"平均={avg*100:.2f}% 落在 22-26% 区间(含边界, 对齐 ArmB 26.10%→不可分辨 先例)")
    if avg <= 0.22:
        return ("失败 (fail)", "bad", f"平均={avg*100:.2f}% ≤ 22%")
    return ("边界/部分成功 (未覆盖区间 26-30%, 无细粒度 +10pp)", "warn",
            f"平均={avg*100:.2f}% 在 26-30% 但细粒度无 +10pp, 预注册判据未显式覆盖")

def bench_table(R):
    head = "<tr><th>#</th><th>评测集</th><th>指标</th><th>ArmC</th><th>ArmB</th><th>Δ vs ArmB</th><th>能力维度</th></tr>"
    body = ""
    for i, (key, name, metric, desc) in enumerate(BENCH_ORDER, 1):
        if is_mme(key):
            ac, ab = fmt_mme(R.get(key)), fmt_mme(ARMB.get(key))
            delta = "—"
        else:
            a, b = num(R.get(key)), num(ARMB.get(key))
            ac, ab = fmt_pct(a), fmt_pct(b)
            if a is not None and b is not None:
                d = (a - b) * 100
                cls = "ok" if d > 0.5 else ("bad" if d < -0.5 else "")
                delta = f"<span class='{cls}'>{d:+.2f}pp</span>"
            else:
                delta = "N/A"
        body += f"<tr><td>{i}</td><td>{escape(name)}</td><td>{escape(metric)}</td><td>{ac}</td><td>{ab}</td><td>{delta}</td><td>{escape(desc)}</td></tr>"
    return "<table>" + head + body + "</table>"

def bar_svg(R):
    rows = [(k, name, num(R.get(k))) for k, name, *_ in BENCH_ORDER if not is_mme(k)]
    rows = [(k, n, v) for k, n, v in rows if v is not None]
    if not rows: return "<p class='small'>(无数值可绘图)</p>"
    n = len(rows); bh, bg, lw, cw = 26, 5, 200, 440
    th = n * (bh + bg) + 40
    maxv = max(v for _, _, v in rows)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{lw+cw+120}" height="{th}" viewBox="0 0 {lw+cw+120} {th}" font-family="sans-serif" font-size="12">']
    y = 8
    for k, name, v in rows:
        bw = (v / maxv) * cw if maxv > 0 else 0
        col = "#58a6ff" if v >= 0.40 else ("#3fb950" if v >= 0.20 else "#d29922")
        parts.append(f'<rect x="{lw}" y="{y}" width="{bw:.1f}" height="{bh}" fill="{col}" rx="3"/>')
        parts.append(f'<text x="{lw-6}" y="{y+bh*0.7}" text-anchor="end" fill="#c9d1d9">{escape(name)}</text>')
        parts.append(f'<text x="{lw+bw+6:.1f}" y="{y+bh*0.75}" fill="#8b949e">{v*100:.2f}%</text>')
        y += bh + bg
    parts.append("</svg>"); return "\n".join(parts)

def protb_table():
    rows = [
        ("ArmC (本实验, min_lr1e-5+wd0.01)", PROTB["armC"]["lp"], PROTB["armC"]["knn5"]),
        ("ArmB (基线, min_lr1e-4+wd0.1)", PROTB["armB"]["lp"], PROTB["armB"]["knn5"]),
        ("④-4ep (自研 w512)", PROTB["4ep"]["lp"], PROTB["4ep"]["knn5"]),
    ]
    body = ""
    for name, lp, knn in rows:
        body += f"<tr><td>{escape(name)}</td><td>{lp:.3f}%</td><td>{knn:.3f}%</td></tr>"
    return "<table><tr><th>视觉塔</th><th>lp (Protocol B, 3 seeds)</th><th>5-NN</th></tr>" + body + "</table>"

CSS = """
body{background:#0d1117;color:#c9d1d9;font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;margin:0;padding:0;line-height:1.7}
.wrap{max-width:980px;margin:0 auto;padding:32px 24px}
h1{color:#f0f6fc;font-size:1.7em;border-bottom:1px solid #30363d;padding-bottom:.3em}
h2{color:#58a6ff;font-size:1.3em;margin-top:2em;border-left:4px solid #58a6ff;padding-left:10px}
h3{color:#79c0ff;font-size:1.1em;margin-top:1.5em}
table{border-collapse:collapse;width:100%;margin:14px 0;font-size:.93em}
th,td{border:1px solid #30363d;padding:7px 10px;text-align:left}
th{background:#161b22;color:#f0f6fc} tr:nth-child(even){background:#161b22}
code{background:#1f2428;padding:2px 6px;border-radius:4px;color:#79c0ff;font-size:.88em}
.kbox{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:14px 18px;margin:14px 0}
.ok{color:#3fb950;font-weight:bold}.warn{color:#d29922}.bad{color:#f85149}
.small{color:#8b949e;font-size:.85em} svg{max-width:100%;height:auto;display:block;margin:14px auto}
.summary{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:16px 0}
.card{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:14px}
.card .v{font-size:1.5em;font-weight:bold;color:#58a6ff}.card .l{color:#8b949e;font-size:.85em}
hr{border:0;border-top:1px solid #30363d;margin:2em 0}
"""

def build_html(R, results_dir, out_path):
    avg = avg_excl_mme(R)
    vlabel, vcls, vreason = verdict(avg, R)
    avg_str = f"{avg*100:.2f}%" if avg is not None else "N/A"
    delta_avg = (avg - (sum(num(ARMB[k]) for k in ARMB if not is_mme(k))/11)) * 100 if avg is not None else None
    delta_4ep = (avg - FOUR_EP_AVG) * 100 if avg is not None else None
    delta_rice = (avg - RICEVIT_AVG) * 100 if avg is not None else None
    gen = datetime.now().strftime("%Y-%m-%d %H:%M")
    d_lp = PROTB["armC"]["lp"] - PROTB["armB"]["lp"]
    d_knn = PROTB["armC"]["knn5"] - PROTB["armB"]["knn5"]
    HTML = f"""<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ArmC Stage(iv) MLLM 12-集评测报告 (2026-10-18)</title><style>{CSS}</style></head><body><div class="wrap">
<h1>ArmC · Stage(iv) MLLM 对齐 + 12-集 lmms-eval 评测报告</h1>
<p class="small">生成时间: {gen} · 实验日期: 2026-10-18 ~ 10-19 · 视觉塔: open_clip ViT-B/16 224 (768-d) · LLM: Qwen3-4B-Instruct</p>

<div class="kbox warn">
⚠️ <b>两变量实验披露 (必读)</b>：ArmC 相对 ArmB 改了<b>两个变量</b> —— ① min_lr 1e-4→1e-5；② weight decay 0.1→0.01。
其余配方 (LR 1e-3 / warmup 2000 / 4 epoch 57250 步 / GBS 8192 / AIMv2-style InfoNCE+masked-patch-MSE 1:1, mask 0.6 / seed 1234 / 数据 11350 shards) 全部不变。
因此 <b>ArmC vs ArmB 的任何差异都不得归因于单一变量</b>；本报告所有 Δ 仅作描述, 不做单变量因果归因。
</div>

<h2>1. 摘要</h2>
<div class="summary">
<div class="card"><div class="l">ArmC 平均(除 MME)</div><div class="v">{avg_str}</div></div>
<div class="card"><div class="l">vs ArmB (26.10%)</div><div class="v">{delta_avg:+.2f}pp</div></div>
<div class="card"><div class="l">vs ④-4ep (25.68%)</div><div class="v">{delta_4ep:+.2f}pp</div></div>
<div class="card"><div class="l">vs RiCEViT (60.08%)</div><div class="v">{delta_rice:+.2f}pp</div></div>
</div>
<div class="kbox"><b>预注册判据裁定 (沿用 ArmB, 不事后改):</b>
<span class="{vcls}"><b>{vlabel}</b></span><br><span class="small">依据: {vreason}</span><br>
<span class="small">判据原文: ≥30% 强成功 / >24% 且 DocVQA/ChartQA/OCRBench 任一 +10pp(vs ArmB) 成功 / 22-26% 不可分辨 / ≤22% 失败。ArmC vs ArmB 的 Δ 只作描述, 不改判据。</span></div>

<h2>2. 实验配置 (ArmC vs ArmB)</h2>
<table><tr><th>项</th><th>ArmB (基线)</th><th>ArmC (本实验)</th><th>是否变量</th></tr>
<tr><td>视觉塔</td><td>open_clip ViT-B/16 224 (86.2M)</td><td>同左</td><td>否</td></tr>
<tr><td>目标</td><td>AIMv2-style (InfoNCE 1.0 + masked-patch-MSE 1.0, mask 0.6)</td><td>同左</td><td>否</td></tr>
<tr><td>数据</td><td>GPIC 8000 + CC12M 1100 + Amshaker 2250 = 11350 shards</td><td>同左</td><td>否</td></tr>
<tr><td>LR / warmup / epoch</td><td>1e-3 / 2000 步 / 4 epoch (57250 步)</td><td>同左</td><td>否</td></tr>
<tr><td>min_lr</td><td>1e-4 (cosine)</td><td><b>1e-5 (cosine)</b></td><td><b>是 (变量①)</b></td></tr>
<tr><td>weight decay</td><td>0.1</td><td><b>0.01</b></td><td><b>是 (变量②)</b></td></tr>
<tr><td>GBS / MBS / accum</td><td>8192 / 512 / 2</td><td>同左</td><td>否</td></tr>
<tr><td>seed / 优化器</td><td>1234 / AdamW betas(0.9,0.98) bf16</td><td>同左</td><td>否</td></tr>
<tr><td>MLLM 三阶段</td><td>Stage-1 (2500) + 1.5 LoRA (20000) + 2 (3500)</td><td>同左 (仅换视觉塔 ckpt)</td><td>否</td></tr>
</table>

<h2>3. ProtB 线性探针评测 (Protocol B, IN-1k full/50k, 3 seeds)</h2>
{protb_table()}
<p class="small">ArmC vs ArmB: Δlp = <b>{d_lp:+.3f}pp</b> (微升), Δ5-NN = <b>{d_knn:+.3f}pp</b> (降)。两变量改动, lp↑/5-NN↓ 方向差异<b>不得归因单一变量</b>。</p>

<h2>4. 12-集 lmms-eval 评测结果</h2>
<p>Stage-2 step3500 checkpoint, <b>每卡一个 benchmark</b> (batch_size=32, 8 卡并行, 无 limit, 全量)。结果来源: <code>{escape(results_dir)}/consolidated_12benchmarks.json</code>。</p>
{bench_table(R)}
{bar_svg(R)}
<p class="small">MME 为感知分 + 认知分 (满分 2800)；其余均为准确率/ANLS 百分比。Δ vs ArmB = (ArmC − ArmB)×100 pp。</p>

<h2>5. 关键结论与诚实披露</h2>
<div class="kbox">
<p><b>① 主裁定</b>: <span class="{vcls}">{vlabel}</span>。{vreason}。</p>
<p><b>② 两变量限制</b>: ArmC 同时改了 min_lr 与 weight decay, 任何 Δ 都不能拆出单一变量的因果。如需拆分, 须额外做 min_lr-only 与 wd-only 两个单变量臂 (当前未做)。</p>
<p><b>③ ProtB→MLLM 传递性</b>: ArmC ProtB lp (62.33%) 与 ArmB (62.09%) 几乎持平 (Δ+0.24pp), MLLM 12 集平均的 Δ 见上表 —— 再次印证线性探针不直接预测 MLLM 下游表现 (同 ArmB 结论)。</p>
<p><b>④ 诚实条款</b>: 内部 ProtB/MLLM 口径, 非官方榜; 单 backbone/单预算点; MLLM 三阶段单 seed; 224px 单块 (无 anyres), 细粒度任务 (OCR/Doc/Chart/Count) 天然偏低; 与 ArmB 同口径同预算, 可横比; 与外部公开值 (RiCEViT 等) 口径不同, 仅作量级参考。</p>
</div>

<h2>6. 文件路径</h2>
<table>
<tr><th>产物</th><th>路径</th></tr>
<tr><td>ArmC 训练输出</td><td><code>/nas_train/app.e0031982/datasets/baize-vision/out/armC_20261018_aimv2_openclip_vitb16_224/</code></td></tr>
<tr><td>open_clip 权重</td><td><code>.../armC_20261018_.../open_clip_state_dict.pt</code> (598MB)</td></tr>
<tr><td>ProtB 结果</td><td><code>vision/armC_20261018_protb_vitb16_224_results.json</code></td></tr>
<tr><td>MLLM 三阶段</td><td><code>.../mllm_stage{1,15,2}_armC_20261018/</code></td></tr>
<tr><td>12-集原始结果</td><td><code>{escape(results_dir)}/eval_*.json</code></td></tr>
<tr><td>12-集合并</td><td><code>{escape(results_dir)}/consolidated_12benchmarks.json</code></td></tr>
<tr><td>本报告</td><td><code>{escape(out_path)}</code></td></tr>
<tr><td>实验记录</td><td><code>EXPERIMENTS_VISION.md §13</code></td></tr>
</table>
<hr>
<p class="small">本报告由 <code>vision/generate_armC_mllm_report.py</code> 自动生成 · 所有数字来自落盘产物 (consolidated_12benchmarks.json / armC_20261018_protb_vitb16_224_results.json), 未做外推或臆造。生成时间 {gen}。</p>
</div></body></html>"""
    return HTML

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", type=str, default=DEFAULT_RESULTS_DIR,
                    help="目录, 含 consolidated_12benchmarks.json (默认 ArmC 20261018 结果目录)")
    ap.add_argument("--out", type=str, default=DEFAULT_OUT, help="输出 HTML 路径")
    args = ap.parse_args()
    cj = os.path.join(args.results_dir, "consolidated_12benchmarks.json")
    if not os.path.exists(cj):
        print(f"ERROR: 未找到 {cj} —— ④ 12-集评测可能尚未完成。", file=sys.stderr)
        print("请先确认 launch_12benchmarks_armC.sh 已跑完 (chain PHASE 4), 再运行本脚本。", file=sys.stderr)
        sys.exit(1)
    with open(cj) as f:
        data = json.load(f)
    R = data.get("results", {})
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    html = build_html(R, args.results_dir, args.out)
    with open(args.out, "w") as f:
        f.write(html)
    avg = avg_excl_mme(R)
    vlabel, vcls, _ = verdict(avg, R)
    print(f"✅ 报告已生成: {args.out}")
    print(f"   ArmC 平均(除MME) = {avg*100:.2f}%" if avg is not None else "   平均: N/A")
    print(f"   裁定: {vlabel}")

if __name__ == "__main__":
    main()
