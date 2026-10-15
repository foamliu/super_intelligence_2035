#!/usr/bin/env python3
"""Generate Chinese HTML report with scaling comparison curves: BaiZe vs Xmodel-2 vs Xmodel-2.5."""
import json, os, sys, math
from datetime import datetime

# BaiZe P-5b + P-8 scaling data (from EXPERIMENTS_PRETRAIN_2B.md)
BAIZE_DATA = [
    (0.655, 31.09, 33.26, 'P-5b 655M'),
    (1.31,  34.06, 36.02, 'P-5b 1.31B'),
    (2.62,  40.38, 40.99, 'P-5b 2.62B'),
    (4.4,   42.86, 43.95, 'P-8 iter_1049'),
    (5.24,  43.84, 44.40, 'P-5b 5.24B'),
    (10.5,  46.31, 47.14, 'P-5b 10.5B'),
    (13.2,  46.58, 47.83, 'P-8 iter_3147'),
    (20.0,  47.91, 49.22, 'P-5b 20B'),
    (22.0,  47.44, 48.54, 'P-8 iter_5245'),
    (30.8,  48.36, 49.50, 'P-8 iter_7343'),
    (39.6,  47.55, 49.32, 'P-8 iter_9441'),
    (44.4,  48.01, 49.22, 'P-8 final'),
]

XMODEL2_PAPER = {
    'tokens_B': 1452.0, 'avg': 61.79,
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
    parts.append(f'<text x="20" y="{height/2}" text-anchor="middle" font-size="13" fill="#333" transform="rotate(-90 20 {height/2})">Common8 Avg (raw acc %)</text>')

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
    h.append('<tr><td>Xmodel-2 s1/10000</td><td>10K</td><td>12.3B</td><td>P-8 iter_3147 (13.2B)</td></tr>')
    h.append('<tr><td>Xmodel-2 s1/20000</td><td>20K</td><td>24.6B</td><td>P-8 iter_5245 (22.0B)</td></tr>')
    h.append('<tr><td>Xmodel-2 s1/30000</td><td>30K</td><td>36.9B</td><td>P-8 iter_7343 (30.8B)</td></tr>')
    h.append('<tr><td>Xmodel-2 s1/40000</td><td>40K</td><td>49.2B</td><td>P-8 final (44.4B)</td></tr>')
    h.append('<tr><td>Xmodel-2 final</td><td>decay</td><td>~1.45T</td><td>论文参考点</td></tr>')
    h.append('<tr><td>Xmodel-2.5 step 2000</td><td>2K</td><td>~5.0B</td><td>P-8 iter_1049 (4.4B)</td></tr>')
    h.append('<tr><td>Xmodel-2.5 step 10000</td><td>10K</td><td>~25.0B</td><td>P-5b 20B</td></tr>')
    h.append('<tr><td>Xmodel-2.5 step 18000</td><td>18K</td><td>~45.0B</td><td>P-8 final (44.4B)</td></tr></table>')
    h.append('<h2>3. 缩放曲线对比</h2>')
    h.append('<div class="svg-container">')
    h.append(svg_scaling_curve(BAIZE_DATA, xmodel2_data, xmodel25_data))
    h.append('</div>')
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
    xm2_valid = [d for d in xmodel2_data if d.get('avg') is not None and d['tokens'] < 100]
    h.append('<ul>')
    if xm2_valid:
        avg_diff = sum(d['avg'] - min(BAIZE_DATA, key=lambda b: abs(b[0]-d['tokens']))[1] for d in xm2_valid) / len(xm2_valid)
        sign = 'good' if avg_diff < 0 else 'bad'
        h.append(f'<li>Xmodel-2 在相近 token 量时 Common8 均分比 BaiZe-2B 平均 <b class="{sign}">{avg_diff:+.2f}pp</b>。</li>')
    baize_44b = 48.01
    h.append(f'<li>BaiZe-2B 在 44.4B tokens 达到 {baize_44b:.2f}%，Xmodel-2 论文在 1.5T 达到 {XMODEL2_PAPER["avg"]:.2f}%（训练量差 33×）。</li>')
    h.append('<li>BaiZe-2B 在 ~20B tokens 后进入平台期（48±0.5%），与 P-5b 独立验证一致。</li>')
    h.append('<li>三者架构/参数量/tokenizer 不同，对比为量级参照而非严格对照。</li>')
    h.append('</ul>')
    h.append('<h3>5.3 结论</h3>')
    h.append('<div class="note">')
    if xm2_valid:
        xm2_avg = sum(d['avg'] for d in xm2_valid) / len(xm2_valid)
        baize_avg = sum(min(BAIZE_DATA, key=lambda b: abs(b[0]-d['tokens']))[1] for d in xm2_valid) / len(xm2_valid)
        diff = xm2_avg - baize_avg
        h.append(f'<p>在 4.4B–49.2B token 范围内，Xmodel-2 平均 {xm2_avg:.2f}%，BaiZe-2B 平均 {baize_avg:.2f}%，'
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
