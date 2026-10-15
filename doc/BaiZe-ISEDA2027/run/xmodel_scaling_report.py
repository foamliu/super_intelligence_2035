#!/usr/bin/env python3
"""Generate Chinese HTML report with scaling comparison curves: BaiZe vs Xmodel-2 vs Xmodel-2.5."""
import json, os, sys, math
from datetime import datetime

# BaiZe P-5b + P-8 scaling data
# Format: (tokens_B, norm_acc_avg, raw_acc_avg, label)
# norm_acc_avg = acc_norm for {openbookqa,arc_easy,arc_challenge,hellaswag,piqa,sciq} + acc for {boolq,winogrande}
# This matches xmodel_collect_results.py compute_avg() for consistent comparison
BAIZE_DATA = [
    # P-5b (smaller model, different arch proportions) — from EXPERIMENTS_PRETRAIN_2B.md
    (0.655, 33.26, 31.09, 'P-5b 655M'),
    (1.31,  36.02, 34.06, 'P-5b 1.31B'),
    (2.62,  40.99, 40.38, 'P-5b 2.62B'),
    (5.24,  44.40, 43.84, 'P-5b 5.24B'),
    (10.5,  47.14, 46.31, 'P-5b 10.5B'),
    (20.0,  49.22, 47.91, 'P-5b 20B'),
    # P-8 (2.2B Mamba2-hybrid, seq=4094, AdamW) — from baize_p8_collect_cs8.py (verified 2026-10-15)
    (4.4,   44.04, 42.86, 'P-8 iter_1049'),
    (13.2,  47.79, 46.58, 'P-8 iter_3147'),
    (22.0,  48.55, 47.44, 'P-8 iter_5245'),
    (30.8,  49.50, 48.36, 'P-8 iter_7343'),
    (39.6,  49.32, 47.55, 'P-8 iter_9441'),
    (44.4,  49.22, 48.01, 'P-8 final (decay)'),
]

# BaiZe complex6 data (gsm8k, math500, mmlu, bbh, humaneval, mbpp)
# Format: (tokens_B, avg_6task, label, {task: score})
BAIZE_COMPLEX6_DATA = [
    # P-5b (from p5b/lm_eval_complex/complex6_summary.json)
    (0.655,  4.33, 'P-5b 655M',  {'gsm8k':0.0,'math500':0.0,'mmlu':22.92,'bbh':3.07,'humaneval':0.0,'mbpp':0.0}),
    (1.31,   5.45, 'P-5b 1.31B', {'gsm8k':3.0,'math500':0.0,'mmlu':23.12,'bbh':6.56,'humaneval':0.0,'mbpp':0.0}),
    (2.62,   6.47, 'P-5b 2.62B', {'gsm8k':1.0,'math500':0.0,'mmlu':23.58,'bbh':14.26,'humaneval':0.0,'mbpp':0.0}),
    (5.24,   5.51, 'P-5b 5.24B', {'gsm8k':1.0,'math500':0.0,'mmlu':23.52,'bbh':9.56,'humaneval':0.0,'mbpp':0.0}),
    (10.5,   5.10, 'P-5b 10.5B', {'gsm8k':0.0,'math500':0.0,'mmlu':23.46,'bbh':7.15,'humaneval':0.0,'mbpp':0.0}),
    (20.0,   5.80, 'P-5b 20B',   {'gsm8k':1.0,'math500':0.0,'mmlu':25.0,'bbh':8.78,'humaneval':0.0,'mbpp':0.0}),
    # P-8 decay 44.4B (from p8_adamw_decay/lm_eval_14, BBH pending → 5-task avg)
    (44.4,   5.30, 'P-8 44.4B (BBH pending)', {'gsm8k':1.59,'math500':0.0,'mmlu':24.28,'bbh':None,'humaneval':0.61,'mbpp':0.0}),
]

XMODEL2_PAPER = {
    'tokens_B': 1500.0, 'avg': 61.79,
    'per_task': {
        'arc_challenge': 39.16, 'arc_easy': 71.55, 'boolq': 74.65,
        'hellaswag': 47.45, 'openbookqa': 29.20, 'piqa': 74.81,
        'sciq': 93.60, 'winogrande': 63.93,
    }
}

XMODEL25_PAPER = {'tokens_B': 1400.0, 'avg': 52.49, 'note': '13 reasoning benchmarks avg'}

def load_xmodel_results(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)

def svg_scaling_curve(baize_data, xmodel2_data, xmodel25_data, width=800, height=500):
    margin = {'l': 70, 'r': 30, 't': 40, 'b': 60}
    pw = width - margin['l'] - margin['r']
    ph = height - margin['t'] - margin['b']
    xmin, xmax = 0.5, 2000.0
    ymin, ymax = 25, 70

    def x_pos(t):
        if t <= 0: t = 0.1
        return margin['l'] + (math.log10(t) - math.log10(xmin)) / (math.log10(xmax) - math.log10(xmin)) * pw
    def y_pos(v):
        return margin['t'] + ph - (v - ymin) / (ymax - ymin) * ph

    parts = [f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" style="font-family:monospace">']
    parts.append(f'<rect x="0" y="0" width="{width}" height="{height}" fill="#fafafa"/>')
    for v in range(30, 70, 10):
        y = y_pos(v)
        parts.append(f'<line x1="{margin["l"]}" y1="{y:.1f}" x2="{width-margin["r"]}" y2="{y:.1f}" stroke="#ddd" stroke-width="1"/>')
        parts.append(f'<text x="{margin["l"]-8}" y="{y+4:.1f}" text-anchor="end" font-size="11" fill="#666">{v}%</text>')
    for t in [1, 5, 10, 50, 100, 500, 1000]:
        x = x_pos(t)
        if margin['l'] <= x <= width - margin['r']:
            parts.append(f'<line x1="{x:.1f}" y1="{margin["t"]}" x2="{x:.1f}" y2="{height-margin["b"]}" stroke="#eee" stroke-width="1"/>')
            label = f'{t}B' if t < 1000 else f'{t/1000:.0f}T'
            parts.append(f'<text x="{x:.1f}" y="{height-margin["b"]+18}" text-anchor="middle" font-size="11" fill="#666">{label}</text>')
    parts.append(f'<line x1="{margin["l"]}" y1="{margin["t"]}" x2="{margin["l"]}" y2="{height-margin["b"]}" stroke="#333" stroke-width="1.5"/>')
    parts.append(f'<line x1="{margin["l"]}" y1="{height-margin["b"]}" x2="{width-margin["r"]}" y2="{height-margin["b"]}" stroke="#333" stroke-width="1.5"/>')
    parts.append(f'<text x="{width/2}" y="{height-10}" text-anchor="middle" font-size="13" fill="#333">训练 Token 数 (log scale)</text>')
    parts.append(f'<text x="20" y="{height/2}" text-anchor="middle" font-size="13" fill="#333" transform="rotate(-90 20 {height/2})">Common8 Avg (norm acc %)</text>')

    baize_pts = [(x_pos(t), y_pos(v)) for t, v, _, _ in baize_data if v]
    if len(baize_pts) >= 2:
        path_d = ' '.join(f'{x:.1f},{y:.1f}' for x, y in baize_pts)
        parts.append(f'<polyline points="{path_d}" fill="none" stroke="#2563eb" stroke-width="2.5"/>')
        for x, y in baize_pts:
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#2563eb" stroke="white" stroke-width="1"/>')

    xm2_pts = [(x_pos(d['tokens']), y_pos(d['avg'])) for d in xmodel2_data if d.get('avg') is not None]
    if len(xm2_pts) >= 2:
        path_d = ' '.join(f'{x:.1f},{y:.1f}' for x, y in xm2_pts)
        parts.append(f'<polyline points="{path_d}" fill="none" stroke="#dc2626" stroke-width="2.5" stroke-dasharray="5,3"/>')
        for x, y in xm2_pts:
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#dc2626" stroke="white" stroke-width="1"/>')

    xm25_pts = [(x_pos(d['tokens']), y_pos(d['avg'])) for d in xmodel25_data if d.get('avg') is not None]
    if len(xm25_pts) >= 2:
        path_d = ' '.join(f'{x:.1f},{y:.1f}' for x, y in xm25_pts)
        parts.append(f'<polyline points="{path_d}" fill="none" stroke="#16a34a" stroke-width="2.5" stroke-dasharray="5,3"/>')
        for x, y in xm25_pts:
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#16a34a" stroke="white" stroke-width="1"/>')

    x2p = x_pos(XMODEL2_PAPER['tokens_B'])
    y2p = y_pos(XMODEL2_PAPER['avg'])
    parts.append(f'<circle cx="{x2p:.1f}" cy="{y2p:.1f}" r="5" fill="none" stroke="#dc2626" stroke-width="2"/>')
    parts.append(f'<text x="{x2p-50:.1f}" y="{y2p-8:.1f}" font-size="10" fill="#dc2626">Xmodel-2 论文 1.5T: 61.79%</text>')

    lx = width - margin['r'] - 180
    ly = margin['t'] + 20
    parts.append(f'<rect x="{lx}" y="{ly}" width="170" height="75" fill="white" stroke="#ccc" rx="4"/>')
    parts.append(f'<line x1="{lx+10}" y1="{ly+18}" x2="{lx+35}" y2="{ly+18}" stroke="#2563eb" stroke-width="2.5"/>')
    parts.append(f'<text x="{lx+42}" y="{ly+22}" font-size="11" fill="#333">BaiZe-2B (2.22B)</text>')
    parts.append(f'<line x1="{lx+10}" y1="{ly+38}" x2="{lx+35}" y2="{ly+38}" stroke="#dc2626" stroke-width="2.5" stroke-dasharray="5,3"/>')
    parts.append(f'<text x="{lx+42}" y="{ly+42}" font-size="11" fill="#333">Xmodel-2 (1.2B)</text>')
    parts.append(f'<line x1="{lx+10}" y1="{ly+58}" x2="{lx+35}" y2="{ly+58}" stroke="#16a34a" stroke-width="2.5" stroke-dasharray="5,3"/>')
    parts.append(f'<text x="{lx+42}" y="{ly+62}" font-size="11" fill="#333">Xmodel-2.5 (1.3B)</text>')
    parts.append(f'<text x="{width/2}" y="{margin["t"]-15}" text-anchor="middle" font-size="14" font-weight="bold" fill="#333">常识推理 8 集缩放曲线对比 (Common8 Avg vs Training Tokens)</text>')
    parts.append('</svg>')
    return '\n'.join(parts)

def svg_complex6_curve(baize_c6_data, width=800, height=500):
    """SVG curve for complex6 (gsm8k, math500, mmlu, bbh, humaneval, mbpp) avg vs tokens."""
    margin = {'l': 70, 'r': 30, 't': 40, 'b': 60}
    pw = width - margin['l'] - margin['r']
    ph = height - margin['t'] - margin['b']
    xmin, xmax = 0.5, 100.0
    ymin, ymax = 0, 30

    def x_pos(t):
        if t <= 0: t = 0.1
        return margin['l'] + (math.log10(t) - math.log10(xmin)) / (math.log10(xmax) - math.log10(xmin)) * pw
    def y_pos(v):
        return margin['t'] + ph - (v - ymin) / (ymax - ymin) * ph

    parts = [f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" style="font-family:monospace">']
    parts.append(f'<rect x="0" y="0" width="{width}" height="{height}" fill="#fafafa"/>')
    for v in range(0, 31, 5):
        y = y_pos(v)
        parts.append(f'<line x1="{margin["l"]}" y1="{y:.1f}" x2="{width-margin["r"]}" y2="{y:.1f}" stroke="#ddd" stroke-width="1"/>')
        parts.append(f'<text x="{margin["l"]-8}" y="{y+4:.1f}" text-anchor="end" font-size="11" fill="#666">{v}%</text>')
    for t in [1, 5, 10, 50, 100]:
        x = x_pos(t)
        if margin['l'] <= x <= width - margin['r']:
            parts.append(f'<line x1="{x:.1f}" y1="{margin["t"]}" x2="{x:.1f}" y2="{height-margin["b"]}" stroke="#eee" stroke-width="1"/>')
            parts.append(f'<text x="{x:.1f}" y="{height-margin["b"]+18}" text-anchor="middle" font-size="11" fill="#666">{t}B</text>')
    parts.append(f'<line x1="{margin["l"]}" y1="{margin["t"]}" x2="{margin["l"]}" y2="{height-margin["b"]}" stroke="#333" stroke-width="1.5"/>')
    parts.append(f'<line x1="{margin["l"]}" y1="{height-margin["b"]}" x2="{width-margin["r"]}" y2="{height-margin["b"]}" stroke="#333" stroke-width="1.5"/>')
    parts.append(f'<text x="{width/2}" y="{height-10}" text-anchor="middle" font-size="13" fill="#333">训练 Token 数 (log scale)</text>')
    parts.append(f'<text x="20" y="{height/2}" text-anchor="middle" font-size="13" fill="#333" transform="rotate(-90 20 {height/2})">复杂推理 6 集均分 (%)</text>')

    # P-5b line (blue)
    p5b_pts = [(x_pos(t), y_pos(v)) for t, v, _, _ in baize_c6_data if 'P-5b' in _ and v]
    if len(p5b_pts) >= 2:
        path_d = ' '.join(f'{x:.1f},{y:.1f}' for x, y in p5b_pts)
        parts.append(f'<polyline points="{path_d}" fill="none" stroke="#2563eb" stroke-width="2.5"/>')
        for x, y in p5b_pts:
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#2563eb" stroke="white" stroke-width="1"/>')

    # P-8 point (orange, diamond)
    for t, v, label, _ in baize_c6_data:
        if 'P-8' in label and v:
            x, y = x_pos(t), y_pos(v)
            parts.append(f'<polygon points="{x:.1f},{y-6:.1f} {x+6:.1f},{y:.1f} {x:.1f},{y+6:.1f} {x-6:.1f},{y:.1f}" fill="#f97316" stroke="white" stroke-width="1"/>')
            parts.append(f'<text x="{x+10:.1f}" y="{y-5:.1f}" font-size="10" fill="#f97316">{label}</text>')

    lx = width - margin['r'] - 180
    ly = margin['t'] + 20
    parts.append(f'<rect x="{lx}" y="{ly}" width="170" height="55" fill="white" stroke="#ccc" rx="4"/>')
    parts.append(f'<line x1="{lx+10}" y1="{ly+18}" x2="{lx+35}" y2="{ly+18}" stroke="#2563eb" stroke-width="2.5"/>')
    parts.append(f'<text x="{lx+42}" y="{ly+22}" font-size="11" fill="#333">BaiZe P-5b (2.2B)</text>')
    parts.append(f'<polygon points="{lx+22},{ly+38} {lx+28},{ly+44} {lx+22},{ly+50} {lx+16},{ly+44}" fill="#f97316" stroke="white"/>')
    parts.append(f'<text x="{lx+42}" y="{ly+46}" font-size="11" fill="#333">BaiZe P-8 (2.22B)</text>')
    parts.append(f'<text x="{width/2}" y="{margin["t"]-15}" text-anchor="middle" font-size="14" font-weight="bold" fill="#333">复杂推理 6 集缩放曲线 (Complex6 Avg vs Training Tokens)</text>')
    parts.append('</svg>')
    return '\n'.join(parts)

def generate_html(xmodel2_data, xmodel25_data):
    h = []
    h.append('<!DOCTYPE html><html lang="zh-CN"><head>')
    h.append('<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">')
    h.append('<title>BaiZe-2B vs Xmodel-2/2.5 缩放曲线对比报告</title>')
    h.append('<style>body{font-family:"PingFang SC","Microsoft YaHei",sans-serif;max-width:1200px;margin:0 auto;padding:20px;background:#f5f5f5;color:#333}')
    h.append('h1{color:#1a1a2e;text-align:center;border-bottom:3px solid #2563eb;padding-bottom:10px}')
    h.append('h2{color:#2563eb;margin-top:30px;border-left:4px solid #2563eb;padding-left:10px}')
    h.append('table{border-collapse:collapse;width:100%;margin:15px 0;background:white}')
    h.append('th,td{border:1px solid #ddd;padding:8px 12px;text-align:center;font-size:13px}')
    h.append('th{background:#2563eb;color:white}tr:nth-child(even){background:#f9f9f9}')
    h.append('.highlight{background:#fff3cd;font-weight:bold}')
    h.append('.note{background:#fff3cd;border-left:4px solid #ffc107;padding:10px 15px;margin:15px 0;border-radius:4px}')
    h.append('.good{color:#16a34a;font-weight:bold}.bad{color:#dc2626;font-weight:bold}')
    h.append('.svg-container{text-align:center;margin:20px 0}</style></head><body>')
    h.append('<h1>BaiZe-2B vs Xmodel-2/2.5 预训练缩放曲线对比报告</h1>')
    h.append(f'<p style="text-align:center;color:#666">生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M")} | lm-eval-harness 0.4.13 | 0-shot | H100 80GB</p>')
    h.append('<h2>1. 实验概述</h2>')
    h.append('<p><b>目标</b>：下载 Xmodel-2 / Xmodel-2.5 在 BaiZe-2B 训练 token 范围内的检查点，'
             '使用相同 lm-eval 口径评测常识推理 8 集，绘制缩放曲线，判断 BaiZe-2B 预训练早期的学习能力是否显著弱于 Xmodel 系列。</p>')
    h.append('<table><tr><th>模型</th><th>参数量</th><th>架构</th><th>训练 Token</th><th>Tokenizer</th></tr>')
    h.append('<tr><td>BaiZe-2B (P-8)</td><td>2.22B</td><td>Mamba2-hybrid (56层)</td><td>44.4B</td><td>BPE 32K</td></tr>')
    h.append('<tr><td>Xmodel-2</td><td>1.2B</td><td>Transformer (48层, GQA)</td><td>1.5T</td><td>Unigram 65K</td></tr>')
    h.append('<tr><td>Xmodel-2.5</td><td>1.3B</td><td>Transformer (48层, GQA, μP)</td><td>1.4T</td><td>DeepSeek-v3 129K</td></tr></table>')
    h.append('<div class="note"><b>⚠️ 架构差异</b>：BaiZe-2B 采用 Mamba2-hybrid 架构，Xmodel-2/2.5 采用纯 Transformer 架构。'
             '参数量 BaiZe(2.22B) > Xmodel-2(1.2B) ≈ Xmodel-2.5(1.3B)，tokenizer 不同，对比为<b>量级参照</b>。</div>')
    h.append('<h2>2. 检查点选择与 Token 映射</h2>')
    h.append('<table><tr><th>检查点</th><th>训练步数</th><th>累计 Token</th><th>对应 BaiZe</th></tr>')
    h.append('<tr><td>Xmodel-2 s1/10000</td><td>10K</td><td>39.3B</td><td>P-8 iter_9441 (39.6B)</td></tr>')
    h.append('<tr><td>Xmodel-2 s1/20000</td><td>20K</td><td>78.6B</td><td>— (超 BaiZe 范围)</td></tr>')
    h.append('<tr><td>Xmodel-2 s1/30000</td><td>30K</td><td>117.9B</td><td>— (超 BaiZe 范围)</td></tr>')
    h.append('<tr><td>Xmodel-2 s1/40000</td><td>40K</td><td>157.2B</td><td>— (超 BaiZe 范围)</td></tr>')
    h.append('<tr><td>Xmodel-2 final</td><td>decay</td><td>~1.5T</td><td>论文参考点</td></tr>')
    h.append('<tr><td>Xmodel-2.5 step 2000</td><td>2K</td><td>26.4B</td><td>P-8 iter_3147 (13.2B)</td></tr>')
    h.append('<tr><td>Xmodel-2.5 step 4000</td><td>4K</td><td>52.8B</td><td>— (超 BaiZe 范围)</td></tr>')
    h.append('<tr><td>Xmodel-2.5 step 6000</td><td>6K</td><td>79.2B</td><td>— (超 BaiZe 范围)</td></tr>')
    h.append('<tr><td>Xmodel-2.5 step 8000</td><td>8K</td><td>105.6B</td><td>— (超 BaiZe 范围)</td></tr>')
    h.append('<tr><td>Xmodel-2.5 step 10000</td><td>10K</td><td>132.0B</td><td>— (超 BaiZe 范围)</td></tr>')
    h.append('<tr><td>Xmodel-2.5 step 18000</td><td>18K</td><td>237.6B</td><td>— (超 BaiZe 范围)</td></tr></table>')
    h.append('<h2>3. 缩放曲线对比</h2>')
    h.append('<h3>3.1 常识推理 8 集 (Common8)</h3>')
    h.append('<div class="svg-container">')
    h.append(svg_scaling_curve(BAIZE_DATA, xmodel2_data, xmodel25_data))
    h.append('</div>')
    h.append('<h3>3.2 复杂推理 6 集 (Complex6)</h3>')
    h.append('<div class="svg-container">')
    h.append(svg_complex6_curve(BAIZE_COMPLEX6_DATA))
    h.append('</div>')
    h.append('<div class="note"><b>注</b>：复杂推理 6 集 (GSM8K, MATH500, MMLU, BBH, HumanEval, MBPP) 仅对 BaiZe P-5b/P-8 进行了评测。'
             'Xmodel-2/2.5 的复杂推理评测尚未完成，后续补充。P-8 的 BBH 仍在评测中，图中 P-8 数据点使用 5 任务均分。</div>')
    return '\n'.join(h)

def gen_results_section(h, xmodel2_data, xmodel25_data):
    h.append('<h2>4. 逐检查点详细结果 (Common8, 0-shot, raw acc %)</h2>')
    h.append('<h3>Xmodel-2 检查点</h3>')
    h.append('<table><tr><th>检查点</th><th>Tokens</th><th>ARC-c</th><th>ARC-e</th><th>BoolQ</th><th>HellaSwag</th><th>OBQA</th><th>PiQA</th><th>SciQ</th><th>Winogrande</th><th>Avg</th></tr>')
    for d in xmodel2_data:
        pt = d.get('per_task', {})
        avg = d.get('avg')
        avg_str = f'{avg:.2f}' if avg is not None else '—'
        h.append(f'<tr><td>{d["label"]}</td><td>{d["tokens"]}B</td>')
        for t in ['arc_challenge','arc_easy','boolq','hellaswag','openbookqa','piqa','sciq','winogrande']:
            v = pt.get(t)
            h.append(f'<td>{v*100:.2f}</td>' if isinstance(v, float) else '<td>—</td>')
        h.append(f'<td class="highlight">{avg_str}</td></tr>')
    pp = XMODEL2_PAPER['per_task']
    h.append(f'<tr class="highlight"><td>Xmodel-2 论文 (1.5T)</td><td>1452B</td>')
    for t in ['arc_challenge','arc_easy','boolq','hellaswag','openbookqa','piqa','sciq','winogrande']:
        h.append(f'<td>{pp[t]}</td>')
    h.append(f'<td>{XMODEL2_PAPER["avg"]}</td></tr></table>')
    h.append('<h3>Xmodel-2.5 检查点</h3>')
    h.append('<table><tr><th>检查点</th><th>Tokens</th><th>ARC-c</th><th>ARC-e</th><th>BoolQ</th><th>HellaSwag</th><th>OBQA</th><th>PiQA</th><th>SciQ</th><th>Winogrande</th><th>Avg</th></tr>')
    for d in xmodel25_data:
        pt = d.get('per_task', {})
        avg = d.get('avg')
        avg_str = f'{avg:.2f}' if avg is not None else '—'
        h.append(f'<tr><td>{d["label"]}</td><td>{d["tokens"]}B</td>')
        for t in ['arc_challenge','arc_easy','boolq','hellaswag','openbookqa','piqa','sciq','winogrande']:
            v = pt.get(t)
            h.append(f'<td>{v*100:.2f}</td>' if isinstance(v, float) else '<td>—</td>')
        h.append(f'<td class="highlight">{avg_str}</td></tr></table>')
    h.append('<h3>BaiZe P-5b/P-8 Common8 结果</h3>')
    h.append('<table><tr><th>检查点</th><th>Tokens</th><th>Norm Acc Avg</th><th>Raw Acc Avg</th></tr>')
    for tokens, norm_avg, raw_avg, label in BAIZE_DATA:
        h.append(f'<tr><td>{label}</td><td>{tokens}B</td><td class="highlight">{norm_avg:.2f}</td><td>{raw_avg:.2f}</td></tr>')
    h.append('</table>')
    h.append('<h3>BaiZe P-5b/P-8 Complex6 结果</h3>')
    h.append('<table><tr><th>检查点</th><th>Tokens</th><th>GSM8K</th><th>MATH500</th><th>MMLU</th><th>BBH</th><th>HumanEval</th><th>MBPP</th><th>Avg</th></tr>')
    for tokens, avg, label, tasks in BAIZE_COMPLEX6_DATA:
        bbh_str = f'{tasks["bbh"]:.2f}' if tasks['bbh'] is not None else 'pending'
        h.append(f'<tr><td>{label}</td><td>{tokens}B</td>'
                 f'<td>{tasks["gsm8k"]:.2f}</td><td>{tasks["math500"]:.2f}</td>'
                 f'<td>{tasks["mmlu"]:.2f}</td><td>{bbh_str}</td>'
                 f'<td>{tasks["humaneval"]:.2f}</td><td>{tasks["mbpp"]:.2f}</td>'
                 f'<td class="highlight">{avg:.2f}</td></tr>')
    h.append('</table>')
    return

def gen_analysis_section(h, xmodel2_data, xmodel25_data):
    h.append('<h2>5. 分析与结论</h2>')
    h.append('<h3>5.1 同 Token 量级对比</h3>')
    h.append('<table><tr><th>Token 范围</th><th>BaiZe-2B</th><th>Xmodel-2</th><th>差距(pp)</th><th>Xmodel-2.5</th><th>差距(pp)</th></tr>')
    for d2 in xmodel2_data:
        if d2.get('avg') is None: continue
        tokens = d2['tokens']
        closest = min(BAIZE_DATA, key=lambda b: abs(b[0] - tokens))
        baize_val = closest[1]
        diff = d2['avg'] - baize_val
        closest_25 = min((d for d in xmodel25_data if d.get('avg') is not None), key=lambda d: abs(d['tokens']-tokens), default=None)
        if closest_25 and closest_25.get('avg') is not None:
            diff25 = closest_25['avg'] - baize_val
            h.append(f'<tr><td>~{tokens:.0f}B</td><td>{baize_val:.2f}%</td><td>{d2["avg"]:.2f}%</td>'
                     f'<td class="{"good" if diff>0 else "bad"}">{diff:+.2f}</td>'
                     f'<td>{closest_25["avg"]:.2f}%</td><td class="{"good" if diff25>0 else "bad"}">{diff25:+.2f}</td></tr>')
        else:
            h.append(f'<tr><td>~{tokens:.0f}B</td><td>{baize_val:.2f}%</td><td>{d2["avg"]:.2f}%</td>'
                     f'<td class="{"good" if diff>0 else "bad"}">{diff:+.2f}</td><td>—</td><td>—</td></tr>')
    h.append('</table>')
    h.append('<h3>5.2 关键发现</h3>')
    xm2_valid = [d for d in xmodel2_data if d.get('avg') is not None and d['tokens'] < 200]
    h.append('<ul>')
    if xm2_valid:
        avg_diff = sum(d['avg'] - min(BAIZE_DATA, key=lambda b: abs(b[0]-d['tokens']))[1] for d in xm2_valid) / len(xm2_valid)
        sign = 'good' if avg_diff < 0 else 'bad'
        h.append(f'<li>Xmodel-2 在相近 token 量时 Common8 均分比 BaiZe-2B 平均 <b class="{sign}">{avg_diff:+.2f}pp</b>。</li>')
    baize_44b = 49.22
    h.append(f'<li>BaiZe-2B 在 44.4B tokens 达到 {baize_44b:.2f}%（norm acc），Xmodel-2 论文在 1.5T 达到 {XMODEL2_PAPER["avg"]:.2f}%（训练量差 33×，但论文使用不同 shot 数）。</li>')
    h.append('<li>BaiZe-2B 在 ~20B tokens 后进入平台期（49±0.5%），与 P-5b 独立验证一致。</li>')
    h.append('<li>三者架构/参数量/tokenizer 不同，对比为量级参照而非严格对照。</li>')
    h.append('<li><b>复杂推理 6 集</b>：P-5b 在 0.655B–20B tokens 范围内均分仅 4–7%，主要贡献来自 MMLU (23–25%) 和 BBH (3–14%)。'
             'GSM8K/MATH500/HumanEval/MBPP 几乎为 0%，说明 2B 级模型在 <20B tokens 时尚不具备有意义的复杂推理能力。</li>')
    h.append('<li>P-8 在 44.4B tokens 的 Complex6 均分 (5.30%, BBH pending) 与 P-5b 20B (5.80%) 接近，'
             'MMLU 24.28% vs 25.0%，复杂推理未随 token 量翻倍显著提升。</li>')
    h.append('</ul>')
    h.append('<h3>5.3 结论</h3>')
    h.append('<div class="note">')
    if xm2_valid:
        xm2_avg = sum(d['avg'] for d in xm2_valid) / len(xm2_valid)
        baize_avg = sum(min(BAIZE_DATA, key=lambda b: abs(b[0]-d['tokens']))[1] for d in xm2_valid) / len(xm2_valid)
        diff = xm2_avg - baize_avg
        h.append(f'<p>在 39.3B–157.2B token 范围内，Xmodel-2 平均 {xm2_avg:.2f}%，BaiZe-2B 平均 {baize_avg:.2f}%，'
                 f'差距 <b class="{"bad" if diff>0 else "good"}">{diff:+.2f}pp</b>。</p>')
        if diff > 5:
            h.append(f'<p><b class="bad">BaiZe-2B 在预训练早期的常识推理学习能力显著弱于 Xmodel-2</b>，'
                     f'尽管参数量更大。可能原因：Mamba2-hybrid 早期需更多 token；数据/tokenizer 差异。</p>')
        elif diff > 0:
            h.append(f'<p>BaiZe-2B 早期常识推理略弱于 Xmodel-2（差距 {diff:.2f}pp），考虑架构差异，差距不显著。</p>')
        else:
            h.append(f'<p>BaiZe-2B 早期常识推理能力<b class="good">不低于</b> Xmodel-2（差距 {diff:+.2f}pp）。</p>')
    h.append('</div>')
    h.append('<hr style="margin-top:40px;border-color:#ccc">')
    h.append(f'<p style="text-align:center;color:#999;font-size:12px">BaiZe-ISEDA2027 | lm-eval 0.4.13 | 0-shot | {datetime.now().strftime("%Y-%m-%d")}</p>')
    h.append('</body></html>')
    return

def main():
    base = '/nas_train/app.e0031982/code/BaiZe-ISEDA2027/xmodel_eval'
    summary_path = os.path.join(base, 'xmodel_common8_summary.json')
    all_data = load_xmodel_results(summary_path)
    xmodel2_data = [d for d in all_data if 'xmodel2_s1' in d.get('name','') or 'xmodel2_final' in d.get('name','')]
    xmodel25_data = [d for d in all_data if 'xmodel25' in d.get('name','')]
    html_parts = generate_html(xmodel2_data, xmodel25_data)
    h = [html_parts]
    gen_results_section(h, xmodel2_data, xmodel25_data)
    gen_analysis_section(h, xmodel2_data, xmodel25_data)
    html = '\n'.join(h)
    out_dir = '/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports'
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'report_xmodel_scaling_comparison_zh.html')
    with open(out_path, 'w') as f:
        f.write(html)
    print(f'Report generated: {out_path}')
    print(f'Size: {os.path.getsize(out_path)} bytes')

if __name__ == '__main__':
    main()
