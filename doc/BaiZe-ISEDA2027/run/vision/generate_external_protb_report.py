#!/usr/bin/env python
"""generate_external_protb_report.py - Generate HTML report for external encoder ProtB evaluation.

Reads external_protb_results_*.json files and produces a self-contained
Chinese HTML report with inline CSS/SVG, zero external dependencies.
"""
import argparse, glob, json, os, sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT = os.path.join(os.path.dirname(SCRIPT_DIR),
                              'report_vision_external_protb_reference_zh.html')

MODEL_INFO = {
    'clip-vitl14-336': {'display': 'CLIP ViT-L/14@336', 'params': '~304M (vision)',
        'paper_lp': '~88.1%', 'paper_ref': 'OpenCLIP linear probe',
        'notes': 'OpenAI \u539f\u7248\uff0c\u672c\u7ebf\u51bb\u7ed3\u6587\u672c\u5854\u540c\u6e90'},
    'siglip2-so400m-384': {'display': 'SigLIP2 so400m@384', 'params': '~400M (vision)',
        'paper_lp': '~83.1%', 'paper_ref': 'HF linear probe',
        'notes': 'Google SigLIP2\uff0c\u65e0\u539f\u7248 SigLIP'},
    'aimv2-1B-336': {'display': 'AIMv2-1B@336', 'params': '~1B',
        'paper_lp': '~87.6%', 'paper_ref': 'Apple frozen trunk lp',
        'notes': 'Apple AIMv2\uff0c\u81ea\u5b9a\u4e49 modeling'},
    'openvision2-vitl14-336': {'display': 'OpenVision2 ViT-L/14@336', 'params': '~304M (vision)',
        'paper_lp': '79.81%', 'paper_ref': 'BaiZe ProtA R13',
        'notes': 'UCSC-VLAA \u5b98\u65b9\u6743\u91cd'},
    'rice-vitl14-560': {'display': 'RICE-ViT-L@560', 'params': '~304M (vision)',
        'paper_lp': '~84.0%', 'paper_ref': '\u4f30\u7b97\u503c\uff08\u5f85\u6838\uff09',
        'notes': 'DeepGlint-AI\uff0c\u9ad8\u5206\u8fa8\u7387 560px'},
}

BAIZE_REF = {'protb': 67.05, 'std': 0.02, 'resolution': 224, 'dim': 512, 'params': '126.8M'}

def load_results():
    pattern = os.path.join(SCRIPT_DIR, 'external_protb_results_*.json')
    files = sorted(glob.glob(pattern))
    files = [f for f in files if 'merged' not in os.path.basename(f)]
    results = []
    for f in files:
        try:
            data = json.load(open(f))
            if isinstance(data, list): results.extend(data)
            else: results.append(data)
        except Exception as e:
            print(f'  WARNING: failed to load {f}: {e}', file=sys.stderr)
    return results

def generate_bar_chart_svg(results):
    sorted_r = sorted(results, key=lambda r: r['protb_mean'], reverse=True)
    n = len(sorted_r) + 1
    bh, bg, lw, cw = 32, 8, 180, 500
    th = n * (bh + bg) + 40
    colors = ['#58a6ff', '#3fb950', '#bc8cff', '#39d2c5', '#e8873c']
    bars, y = [], 20
    for i, r in enumerate(sorted_r):
        info = MODEL_INFO.get(r['model'], {})
        disp = info.get('display', r['model'])
        val = r['protb_mean'] * 100; std = r['protb_std'] * 100
        bw = (val / 100) * cw; col = colors[i % len(colors)]
        ex1 = ((val - std) / 100) * cw + lw; ex2 = ((val + std) / 100) * cw + lw
        ey = y + bh / 2
        bars.append(f'<text x="{lw-8}" y="{y+bh*0.7}" text-anchor="end" fill="#e6edf3" font-size="11">{disp}</text>')
        bars.append(f'<rect x="{lw}" y="{y}" width="{bw:.1f}" height="{bh}" fill="{col}" rx="3" opacity="0.85"/>')
        bars.append(f'<line x1="{ex1:.1f}" y1="{ey}" x2="{ex2:.1f}" y2="{ey}" stroke="#e6edf3" stroke-width="1.5" opacity="0.6"/>')
        bars.append(f'<line x1="{ex1:.1f}" y1="{ey-4}" x2="{ex1:.1f}" y2="{ey+4}" stroke="#e6edf3" stroke-width="1.5" opacity="0.6"/>')
        bars.append(f'<line x1="{ex2:.1f}" y1="{ey-4}" x2="{ex2:.1f}" y2="{ey+4}" stroke="#e6edf3" stroke-width="1.5" opacity="0.6"/>')
        bars.append(f'<text x="{lw+bw+8:.1f}" y="{y+bh*0.7}" fill="#e6edf3" font-size="11">{val:.2f}%</text>')
        y += bh + bg
    val = BAIZE_REF['protb']; bw = (val / 100) * cw
    bars.append(f'<text x="{lw-8}" y="{y+bh*0.7}" text-anchor="end" fill="#f85149" font-size="11">BaiZe 4-4ep (from-scratch)</text>')
    bars.append(f'<rect x="{lw}" y="{y}" width="{bw:.1f}" height="{bh}" fill="none" stroke="#f85149" stroke-width="2" stroke-dasharray="4,2" rx="3" opacity="0.8"/>')
    bars.append(f'<text x="{lw+bw+8:.1f}" y="{y+bh*0.7}" fill="#f85149" font-size="11">{val:.2f}%</text>')
    ax = []
    for v in [0, 20, 40, 60, 80, 100]:
        x = lw + (v / 100) * cw
        ax.append(f'<line x1="{x:.1f}" y1="10" x2="{x:.1f}" y2="{th-15}" stroke="#30363d" stroke-dasharray="2,3"/>')
        ax.append(f'<text x="{x:.1f}" y="{th-2}" text-anchor="middle" fill="#8b949e" font-size="10">{v}%</text>')
    return f'<svg viewBox="0 0 {lw+cw+80} {th}" xmlns="http://www.w3.org/2000/svg">{chr(10).join(ax)}{chr(10).join(bars)}</svg>'

def generate_html(results):
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    sr = sorted(results, key=lambda r: r['protb_mean'], reverse=True)
    rows = []
    for i, r in enumerate(sr):
        info = MODEL_INFO.get(r['model'], {})
        disp = info.get('display', r['model']); params = info.get('params', '?')
        plp = info.get('paper_lp', 'N/A'); pref = info.get('paper_ref', ''); notes = info.get('notes', '')
        p = r['protb_mean'] * 100; s = r['protb_std'] * 100
        runs = r.get('protb_runs', []); rstr = ' / '.join(f'{x*100:.2f}%' for x in runs) if runs else ''
        rc = 'best' if i == 0 else ''
        rows.append(f'<tr><td class="{rc}">{disp}</td><td>{r["resolution"]}px</td><td>{r["feature_dim"]}</td><td>{params}</td><td class="{rc}">{p:.2f} +/- {s:.2f}%</td><td class="note">{rstr}</td><td class="note">{plp}<br><span class="note">{pref}</span></td><td class="note">{notes}</td></tr>')
    bz = f'<tr style="border-top:2px solid #f85149"><td style="color:#f85149">BaiZe 4-4ep (from-scratch)</td><td>224px</td><td>512</td><td>126.8M</td><td style="color:#f85149">67.05 +/- 0.02%</td><td class="note">67.03 / 67.08 / 67.04%</td><td class="note">-</td><td class="note" style="color:#f85149">\u672c\u9879\u76ee\u4ece\u96f6\u8bad\u7ec3\uff0c\u4ec5\u4f9b\u53c2\u8003</td></tr>'
    svg = generate_bar_chart_svg(results)
    return build_full_html(now, rows, bz, svg)

def build_full_html(now, rows, bz, svg):
    CSS = ''':root{--bg:#0d1117;--card:#161b22;--border:#30363d;--text:#e6edf3;--muted:#8b949e;--accent:#58a6ff;--green:#3fb950;--red:#f85149;--yellow:#d29922;--purple:#bc8cff;--orange:#e8873c;--cyan:#39d2c5}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei','Segoe UI',Helvetica,Arial,sans-serif;line-height:1.7;max-width:1200px;margin:0 auto;padding:20px}
h1{font-size:1.8em;color:var(--accent);border-bottom:2px solid var(--border);padding-bottom:.3em;margin:1.5em 0 .5em}
h2{font-size:1.4em;color:var(--purple);margin:1.2em 0 .5em;border-bottom:1px solid var(--border);padding-bottom:.2em}
h3{font-size:1.15em;color:var(--green);margin:1em 0 .4em}
p{margin:.5em 0}
table{border-collapse:collapse;width:100%;margin:.8em 0;font-size:.9em}
th,td{border:1px solid var(--border);padding:.4em .6em;text-align:center}
th{background:var(--card);color:var(--accent);font-weight:600}
td:first-child,th:first-child{text-align:left}
.best{color:var(--green);font-weight:700}
.note{color:var(--muted);font-size:.85em;font-style:italic}
.card{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:1em 1.2em;margin:.8em 0}
.tldr{background:linear-gradient(135deg,#161b22,#1a2332);border-left:4px solid var(--accent)}
.tldr ul{margin:.3em 0 .3em 1.2em}
.tldr li{margin:.3em 0}
code{background:var(--card);padding:.1em .3em;border-radius:3px;font-family:'SF Mono',Consolas,monospace;font-size:.85em;color:var(--orange)}
.svg-container{margin:1em 0;text-align:center}
.svg-container svg{max-width:100%;height:auto}
.tag{display:inline-block;padding:.1em .5em;border-radius:10px;font-size:.75em;font-weight:600}
.tag-warn{background:rgba(248,81,73,.2);color:var(--red)}
.refs{font-size:.85em;color:var(--muted);margin-top:2em;border-top:1px solid var(--border);padding-top:.5em}
.warn-box{background:linear-gradient(135deg,#1f0d0d,#1a0a0a);border:2px solid var(--red);border-radius:8px;padding:1em 1.2em;margin:1em 0}
.warn-box h3{color:var(--red);margin-top:0}
.info-box{background:linear-gradient(135deg,#0d1f1f,#0a1a1a);border:2px solid var(--cyan);border-radius:8px;padding:1em 1.2em;margin:1em 0}
.info-box h3{color:var(--cyan);margin-top:0}'''
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BaiZe \u89c6\u89c9\u7f16\u7801\u5668 - \u5916\u90e8\u516c\u4f17\u7f16\u7801\u5668 ProtB \u53c2\u8003\u8bc4\u6d4b\u62a5\u544a\uff08\u4e2d\u6587 \u00b7 2026-10-13\uff09</title>
<style>{CSS}</style>
</head>
<body>
<h1>BaiZe \u89c6\u89c9\u7f16\u7801\u5668 - \u5916\u90e8\u516c\u4f17\u7f16\u7801\u5668 ProtB \u53c2\u8003\u8bc4\u6d4b\u62a5\u544a</h1>
<p class="note">\u751f\u6210\u65f6\u95f4\uff1a{now} \u00b7 \u7ebf\uff1avision \u00b7 \u8bed\u8a00\uff1a\u4e2d\u6587 \u00b7 \u6027\u8d28\uff1a\u8bc4\u6d4b\u7c7b\uff08\u5360 GPU \u00b7 .12\uff09\u00b7 \u534f\u8bae\uff1aProtocol B\uff08mainstream linear probe\uff09</p>
'''

def build_body(rows, bz, svg):
    return f'''
<div class="warn-box">
<h3>\U0001f6ab \u7ea2\u7ebf\u58f0\u660e</h3>
<p>\u672c\u62a5\u544a\u6240\u6709\u6570\u5b57\u5747\u4e3a<strong>\u516c\u4f17\u9884\u8bad\u7ec3\u6a21\u578b\u7684\u53c2\u8003\u503c</strong>\uff0c\u5fc5\u987b<strong>\u72ec\u7acb\u6210\u8868</strong>\uff0c<strong>\u7edd\u4e0d</strong>\u4e0e BaiZe from-scratch \u4ece\u96f6\u8bad\u7ec3\u6a21\u578b\u653e\u5728\u540c\u4e00\u699c\u5355\u4e2d\u6392\u540d\u3002<strong>\u8bad\u7ec3\u8fc7\u7684\u6a21\u578b</strong>\u6253<strong>\u4ece\u96f6\u7684\u6a21\u578b</strong>\u662f\u4f5c\u5f0a\u53e3\u5f84\u3002</p>
<p>\u5404\u6a21\u578b\u4f7f\u7528\u5404\u81ea <strong>native \u5206\u8fa8\u7387</strong>\uff08224/336/384/448/560\uff09\u548c <strong>native mean/std</strong> \u9884\u5904\u7406 \u2192 <strong>\u8de8\u5206\u8fa8\u7387 lp \u4e0d\u53ef\u76f4\u63a5\u6392\u9ad8\u4e0b</strong>\uff0c\u6bcf\u884c\u5df2\u663e\u5f0f\u6807\u6ce8 native \u5206\u8fa8\u7387\u3002</p>
<p>\u516c\u5f00\u8bba\u6587 lp/zero-shot \u6570\u5b57\u4ec5\u4f5c<strong>\u6587\u732e\u951a\u70b9 \u00b7 \u5f85\u6838</strong>\u6807\u6ce8\uff0c<strong>\u4e0d\u5f97\u5f53\u672c\u9879\u76ee\u7ed3\u8bba</strong>\u3002</p>
</div>

<div class="card tldr">
<h3 style="color:var(--accent);margin-top:0">\U0001f3af \u4e00\u53e5\u8bdd\u603b\u7ed3</h3>
<ul>
<li>\u4f7f\u7528 <strong>Protocol B</strong>\uff08SGD+momentum0.9+cosine 90ep, bs1024, IN-1k full train 1.28M, 3 seeds\uff09\u5bf9 <strong>5 \u4e2a\u516c\u4f17\u89c6\u89c9\u7f16\u7801\u5668</strong>\u8fdb\u884c linear-probe \u8bc4\u6d4b\uff0c\u4f5c\u4e3a BaiZe from-scratch \u6a21\u578b\u7684<strong>\u53c2\u8003\u5bf9\u7167</strong>\u3002</li>
<li>\u5404\u6a21\u578b\u5747\u4f7f\u7528 native \u5206\u8fa8\u7387\u4e0e native \u9884\u5904\u7406\uff0c\u63d0\u53d6 pooled/CLS \u7279\u5f81\u540e\u51bb\u7ed3\u8fdb\u884c linear probe\u3002</li>
<li>BaiZe from-scratch \u2463-4ep ProtB = <strong>67.05+/-0.02%</strong>\uff08224px, 512-dim, 126.8M\uff09\uff0c\u5217\u4e8e\u8868\u672b<strong>\u4ec5\u4f9b\u53c2\u8003</strong>\uff0c\u4e0d\u53c2\u4e0e\u6392\u540d\u3002</li>
</ul>
</div>

<h2>1. \u8bc4\u6d4b\u534f\u8bae\uff08Protocol B\uff09</h2>
<div class="card">
<table>
<tr><th>\u53c2\u6570</th><th>\u503c</th></tr>
<tr><td>\u8bc4\u6d4b\u534f\u8bae</td><td><strong>Protocol B</strong>\uff08mainstream linear probe\uff09</td></tr>
<tr><td>\u4f18\u5316\u5668</td><td>SGD + momentum 0.9</td></tr>
<tr><td>\u5b66\u4e60\u7387\u8c03\u5ea6</td><td>cosine\uff0c5-epoch warmup</td></tr>
<tr><td>\u8bad\u7ec3\u8f6e\u6570</td><td>90 epochs</td></tr>
<tr><td>\u6279\u5927\u5c0f</td><td>1024</td></tr>
<tr><td>Probe-train \u6570\u636e</td><td>IN-1k full train = 1,281,167 \u5f20</td></tr>
<tr><td>\u8bc4\u6d4b\u96c6</td><td>IN-1k \u5b98\u65b9 validation = 50,000 \u5f20</td></tr>
<tr><td>\u5f52\u4e00\u5316</td><td>ImageNet mean/std\uff08probe \u9636\u6bb5\uff09</td></tr>
<tr><td>\u7279\u5f81\u63d0\u53d6</td><td>\u5404\u6a21\u578b native \u5206\u8fa8\u7387 + native mean/std</td></tr>
<tr><td>\u7279\u5f81\u7c7b\u578b</td><td>pooled / CLS token output\uff08\u51bb\u7ed3\uff09</td></tr>
<tr><td>\u968f\u673a\u79cd\u5b50</td><td>3 seeds (0, 1, 2) -> mean +/- std</td></tr>
<tr><td>\u4ee3\u7801</td><td><code>vision/external_encoder_protb.py</code> + <code>vision/lp_protocol_bridge.py</code></td></tr>
</table>
</div>
'''

def build_body2(rows, bz, svg):
    return f'''
<h2>2. \u8bc4\u6d4b\u6a21\u578b\u6e05\u5355</h2>
<div class="card">
<table>
<tr><th>\u6a21\u578b</th><th>\u8def\u5f84</th><th>\u52a0\u8f7d\u65b9\u5f0f</th><th>Native \u5206\u8fa8\u7387</th><th>\u7279\u5f81\u7ef4</th></tr>
<tr><td>CLIP ViT-L/14</td><td><code>openai/clip-vit-large-patch14-336</code></td><td>transformers CLIPVisionModel</td><td>336px</td><td>1024</td></tr>
<tr><td>SigLIP2 so400m</td><td><code>google/siglip2-so400m-patch14-384</code></td><td>transformers Siglip2VisionModel</td><td>384px</td><td>1152</td></tr>
<tr><td>AIMv2-1B</td><td><code>apple/aimv2-1B-patch14-336</code></td><td>HF \u81ea\u5b9a\u4e49 modeling_aimv2.py</td><td>336px</td><td>2048</td></tr>
<tr><td>OpenVision2</td><td><code>UCSC-VLAA/openvision2-vit-large-patch14-336-vision-only</code></td><td>open_clip</td><td>336px</td><td>1024</td></tr>
<tr><td>RICE-ViT-L</td><td><code>DeepGlint-AI/rice-vit-large-patch14-560</code></td><td>HF AutoModel (trust_remote_code)</td><td>560px</td><td>1024</td></tr>
</table>
<p class="note">\u6240\u6709\u6a21\u578b\u5747\u5df2\u4e0b\u8f7d\u81f3 <code>/nas_train/app.e0031982/models/</code>\u3002\u26a0\ufe0f \u65e0\u539f\u7248 SigLIP\uff0c\u4ec5\u6709 SigLIP2\u3002</p>
</div>

<h2>3. ProtB \u8bc4\u6d4b\u7ed3\u679c\uff08\u53c2\u8003\u503c\u8868\uff09</h2>
<div class="info-box">
<h3>\u26a0\ufe0f \u4ee5\u4e0b\u662f\u516c\u4f17\u9884\u8bad\u7ec3\u6a21\u578b\u7684\u53c2\u8003\u503c\uff0c\u4e0d\u4e0e BaiZe from-scratch \u540c\u8868\u6392\u540d</h3>
</div>
<table>
<tr><th>\u6a21\u578b</th><th>Native \u5206\u8fa8\u7387</th><th>\u7279\u5f81\u7ef4</th><th>\u53c2\u6570\u91cf</th><th>ProtB (3 seeds)</th><th>\u5404 seed \u660e\u7ec6</th><th>\u6587\u732e\u951a\u70b9 \u00b7 \u5f85\u6838</th><th>\u5907\u6ce8</th></tr>
{''.join(rows)}
{bz}
</table>
<p class="note">ProtB = Protocol B linear probe\uff08SGD+momentum0.9+cosine 90ep, bs1024, IN-1k full train 1.28M, IN-1k val 50k, 3 seeds\uff09\u3002\u6587\u732e\u951a\u70b9\u6765\u81ea\u516c\u5f00\u8bba\u6587/\u5b98\u65b9\u62a5\u544a\uff0c\u6807\u6ce8\u300c\u5f85\u6838\u300d\u8868\u793a\u5c1a\u672a\u9010\u5b57\u6838\u5b9e\uff0c\u4ec5\u4f9b\u53c2\u8003\u3002</p>

<h2>4. \u53ef\u89c6\u5316\u5bf9\u6bd4</h2>
<div class="svg-container">
{svg}
</div>
<p class="note">\u6761\u5f62\u56fe\u6309 ProtB mean \u964d\u5e8f\u6392\u5217\u3002BaiZe from-scratch \u4ee5\u865a\u7ebf\u6846\u6807\u6ce8\uff0c\u26a0\ufe0f \u8868\u793a\u4e0d\u53c2\u4e0e\u516c\u4f17\u6a21\u578b\u6392\u540d\u3002\u8bef\u5dee\u68d2\u4e3a 3-seed std\u3002</p>
'''

def build_body3():
    return '''
<h2>5. \u5173\u952e\u89c2\u5bdf</h2>
<div class="card">
<h3>5.1 \u8de8\u5206\u8fa8\u7387\u4e0d\u53ef\u6bd4\u6027</h3>
<p>5 \u4e2a\u6a21\u578b\u7684 native \u5206\u8fa8\u7387\u5206\u522b\u4e3a 336/384/336/336/560 px\u3002\u66f4\u9ad8\u5206\u8fa8\u7387\u610f\u5473\u7740\u66f4\u591a patch token \u548c\u66f4\u4e30\u5bcc\u7684\u7a7a\u95f4\u4fe1\u606f\uff0c\u7406\u8bba\u4e0a\u5bf9 linear probe \u6709\u5229\u3002\u56e0\u6b64<strong>\u8de8\u5206\u8fa8\u7387\u7684 ProtB \u6570\u5b57\u4e0d\u53ef\u76f4\u63a5\u6392\u9ad8\u4e0b</strong>\u2014\u2014RICE-ViT@560 \u7684\u4f18\u52bf\u53ef\u80fd\u90e8\u5206\u6765\u81ea\u5206\u8fa8\u7387\u800c\u975e\u6a21\u578b\u67b6\u6784\u3002</p>

<h3>5.2 \u516c\u4f17\u9884\u8bad\u7ec3 vs from-scratch</h3>
<p>\u516c\u4f17\u6a21\u578b\u5728\u6570\u4ebf\u81f3\u6570\u5341\u4ebf\u56fe\u6587\u5bf9\u4e0a\u8fdb\u884c\u5927\u89c4\u6a21\u9884\u8bad\u7ec3\uff08CLIP ~400M, SigLIP ~4B, AIMv2 ~6B\uff09\uff0c\u800c BaiZe from-scratch \u4ec5\u4f7f\u7528 ~96M \u56fe\u6587\u5bf9\uff084 epoch\uff09\u3002\u4e24\u8005\u6570\u636e\u89c4\u6a21\u76f8\u5dee 1~2 \u4e2a\u6570\u91cf\u7ea7\uff0c<strong>\u4e0d\u5e94\u5728\u540c\u8868\u4e2d\u4e0d\u52a0\u533a\u5206\u5730\u6392\u540d</strong>\u3002</p>

<h3>5.3 BaiZe from-scratch \u5b9a\u4f4d</h3>
<p>BaiZe \u2463-4ep ProtB = 67.05%\uff0c\u4f5c\u4e3a from-scratch \u6a21\u578b\uff08224px, 126.8M, 96M pairs x 4ep\uff09\uff0c\u5176\u7edd\u5bf9\u6570\u503c\u4f4e\u4e8e\u516c\u4f17\u5927\u6a21\u578b\u662f\u9884\u671f\u7684\u3002\u672c\u8bc4\u6d4b\u7684\u4ef7\u503c\u5728\u4e8e\u63d0\u4f9b<strong>\u540c\u534f\u8bae\u4e0b\u7684\u53c2\u8003\u951a\u70b9</strong>\uff0c\u5e2e\u52a9\u7406\u89e3 BaiZe \u6a21\u578b\u5728\u5927\u683c\u5c40\u4e2d\u7684\u76f8\u5bf9\u4f4d\u7f6e\u3002</p>

<h3>5.4 OpenVision2 \u5bf9\u6bd4</h3>
<p>OpenVision2 ViT-L/14@336 \u662f BaiZe \u67b6\u6784\u7684\u539f\u578b\u6765\u6e90\u3002R13 \u5df2\u7528 Protocol A \u6d4b\u5f97 79.81%\uff0c\u672c\u6b21\u7528 Protocol B \u91cd\u65b0\u8bc4\u6d4b\uff0c\u53ef\u5bf9\u6bd4 ProtA/ProtB \u534f\u8bae\u5dee\u5f02\u5728\u8be5\u6a21\u578b\u4e0a\u7684\u8868\u73b0\u3002</p>
</div>

<h2>6. \u5de5\u7a0b\u7ec6\u8282</h2>
<div class="card">
<table>
<tr><th>\u9879</th><th>\u8bf4\u660e</th></tr>
<tr><td>\u7279\u5f81\u63d0\u53d6</td><td>\u6bcf\u4e2a\u6a21\u578b\u4f7f\u7528 native \u5206\u8fa8\u7387 + native mean/std\uff0c\u4ece IN-1k parquet \u63d0\u53d6 pooled/CLS \u7279\u5f81</td></tr>
<tr><td>\u7279\u5f81\u7f13\u5b58</td><td>\u63d0\u53d6\u540e\u7f13\u5b58\u81f3 <code>vision/external_features_cache/</code>\uff08.pt \u6587\u4ef6\uff09\uff0c3-seed probe \u590d\u7528\u540c\u4e00\u7279\u5f81</td></tr>
<tr><td>\u5e76\u884c\u6267\u884c</td><td>5 \u6a21\u578b\u5206\u914d\u81f3 GPU 3/4/5/6/7 \u5e76\u884c\u8fd0\u884c</td></tr>
<tr><td>\u52a0\u8f7d\u5c42</td><td><code>external_encoder_protb.py</code> \u65b0\u589e\u5916\u90e8\u7f16\u7801\u5668\u52a0\u8f7d\u5c42\uff0c\u7edf\u4e00\u66b4\u9732 encode_images(imgs) -> pooled_features</td></tr>
<tr><td>AIMv2 \u52a0\u8f7d</td><td>\u9700 remap state dict\uff08Apple \u539f\u59cb key -> HF modeling key\uff09\uff0c\u8be6\u89c1 load_aimv2()</td></tr>
<tr><td>RICE-ViT \u52a0\u8f7d</td><td>trust_remote_code=True\uff0c\u4f7f\u7528 HF AutoModel</td></tr>
</table>
</div>

<div class="refs">
<h3>\u53c2\u8003\u6587\u732e</h3>
<ul>
<li>CLIP: Radford et al., "Learning Transferable Visual Models From Natural Language Supervision", ICML 2021</li>
<li>SigLIP2: Tschannen et al., "SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Alignment", 2024</li>
<li>AIMv2: El-Nouby et al., "Scalable Pre-training of Large Autoregressive Image Models", 2024</li>
<li>OpenVision2: UCSC-VLAA, github.com/UCSC-VLAA/OpenVision</li>
<li>RICE-ViT: DeepGlint-AI, huggingface.co/DeepGlint-AI/rice-vit-large-patch14-560</li>
</ul>
<p>\u6587\u732e lp \u6570\u5b57\u4ec5\u4f5c\u951a\u70b9\u6807\u6ce8\uff0c\u6765\u6e90\u4e3a\u516c\u5f00\u8bba\u6587/\u5b98\u65b9\u62a5\u544a\uff0c\u672a\u9010\u5b57\u6838\u5b9e\u3002</p>
</div>

</body>
</html>'''

def generate_html_v2(results):
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    sr = sorted(results, key=lambda r: r['protb_mean'], reverse=True)
    rows = []
    for i, r in enumerate(sr):
        info = MODEL_INFO.get(r['model'], {})
        disp = info.get('display', r['model']); params = info.get('params', '?')
        plp = info.get('paper_lp', 'N/A'); pref = info.get('paper_ref', ''); notes = info.get('notes', '')
        p = r['protb_mean'] * 100; s = r['protb_std'] * 100
        runs = r.get('protb_runs', []); rstr = ' / '.join(f'{x*100:.2f}%' for x in runs) if runs else ''
        rc = 'best' if i == 0 else ''
        rows.append(f'<tr><td class="{rc}">{disp}</td><td>{r["resolution"]}px</td><td>{r["feature_dim"]}</td><td>{params}</td><td class="{rc}">{p:.2f} +/- {s:.2f}%</td><td class="note">{rstr}</td><td class="note">{plp}<br><span class="note">{pref}</span></td><td class="note">{notes}</td></tr>')
    bz = '<tr style="border-top:2px solid #f85149"><td style="color:#f85149">BaiZe 4-4ep (from-scratch)</td><td>224px</td><td>512</td><td>126.8M</td><td style="color:#f85149">67.05 +/- 0.02%</td><td class="note">67.03 / 67.08 / 67.04%</td><td class="note">-</td><td class="note" style="color:#f85149">\u672c\u9879\u76ee\u4ece\u96f6\u8bad\u7ec3\uff0c\u4ec5\u4f9b\u53c2\u8003</td></tr>'
    svg = generate_bar_chart_svg(results)
    return build_full_html(now, rows, bz, svg) + build_body(rows, bz, svg) + build_body2(rows, bz, svg) + build_body3()

def main():
    ap = argparse.ArgumentParser(description='Generate external encoder ProtB HTML report')
    ap.add_argument('--output', type=str, default=DEFAULT_OUTPUT)
    ap.add_argument('--check-only', action='store_true', help='Only check for results')
    args = ap.parse_args()
    results = load_results()
    print(f'Found {len(results)} result entries')
    if args.check_only:
        for r in results:
            model = r.get('model', '?')
            protb = r.get('protb_mean', 0) * 100
            std = r.get('protb_std', 0) * 100
            print(f'  {model}: ProtB = {protb:.2f} +/- {std:.2f}%')
        return
    if not results:
        print('ERROR: No results found. Run external_encoder_protb.py first.', file=sys.stderr)
        sys.exit(1)
    html = generate_html_v2(results)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Report saved -> {args.output} ({len(html)} bytes)')

if __name__ == '__main__':
    main()
