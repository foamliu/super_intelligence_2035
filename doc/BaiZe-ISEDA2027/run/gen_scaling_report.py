#!/usr/bin/env python3
"""Generate updated scaling_data.json + scaling_report.html with Xmodel-2 s1 history."""
import json, os, datetime

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
SCALING_DIR = os.path.join(RUN_DIR, "scaling_report")
DATA_PATH = os.path.join(SCALING_DIR, "scaling_data.json")
REPORT_PATH = os.path.join(SCALING_DIR, "scaling_report.html")

with open(DATA_PATH) as f:
    data = json.load(f)

xmodel2_s1_new = [
    {"label":"Xmodel-2 s1/10K (39.3B)","tokens_B":39.3,"params_B":1.2,"cs_avg":0.4665,
     "cs_per_task":{"hellaswag":0.3988,"arc_easy":0.4137,"boolq":0.5875,"arc_challenge":0.2381,"sciq":0.673,"piqa":0.6404,"winogrande":0.4988,"openbookqa":0.282},
     "complex_avg":0.0849,"complex_per_task":{"gsm8k":0.0121,"hendrycks_math500":0.034,"mmlu":0.2545,"bbh_zeroshot":0.201,"humaneval":0.0,"mbpp":0.008},
     "source":"Xmodel-2-History s1/10K re-eval"},
    {"label":"Xmodel-2 s1/20K (78.6B)","tokens_B":78.6,"params_B":1.2,"cs_avg":0.4907,
     "cs_per_task":{"hellaswag":0.4314,"arc_easy":0.4339,"boolq":0.618,"arc_challenge":0.2637,"sciq":0.692,"piqa":0.6752,"winogrande":0.5233,"openbookqa":0.288},
     "complex_avg":None,"complex_per_task":{"gsm8k":0.0091,"hendrycks_math500":0.034,"mmlu":0.2656,"bbh_zeroshot":0.2281,"humaneval":None,"mbpp":None},
     "source":"Xmodel-2-History s1/20K re-eval"},
    {"label":"Xmodel-2 s1/30K (117.9B)","tokens_B":117.9,"params_B":1.2,"cs_avg":0.4960,
     "cs_per_task":{"hellaswag":0.4516,"arc_easy":0.4335,"boolq":0.5817,"arc_challenge":0.2577,"sciq":0.734,"piqa":0.6817,"winogrande":0.528,"openbookqa":0.30},
     "complex_avg":None,"complex_per_task":{"gsm8k":0.0159,"hendrycks_math500":0.03,"mmlu":0.2599,"bbh_zeroshot":0.249,"humaneval":None,"mbpp":None},
     "source":"Xmodel-2-History s1/30K re-eval"},
    {"label":"Xmodel-2 s1/40K (157.2B)","tokens_B":157.2,"params_B":1.2,"cs_avg":0.5031,
     "cs_per_task":{"hellaswag":0.4665,"arc_easy":0.4575,"boolq":0.6138,"arc_challenge":0.2645,"sciq":0.724,"piqa":0.6763,"winogrande":0.532,"openbookqa":0.29},
     "complex_avg":None,"complex_per_task":{"gsm8k":0.0099,"hendrycks_math500":0.04,"mmlu":0.2581,"bbh_zeroshot":0.2256,"humaneval":None,"mbpp":None},
     "source":"Xmodel-2-History s1/40K re-eval"},
]
existing_xm2 = [p for p in data.get("xmodel_2",[]) if not p["label"].startswith("Xmodel-2 s1/")]
data["xmodel_2"] = xmodel2_s1_new + existing_xm2
with open(DATA_PATH,"w") as f:
    json.dump(data,f,indent=2,ensure_ascii=False)
print(f"[OK] scaling_data.json updated: xmodel_2 has {len(data['xmodel_2'])} points")

def to_pct(v):
    return f"{v*100:.2f}%" if v is not None else "N/A"

def build_svg(series_list, title, y_label, width=800, height=500):
    all_x=[p[0] for s in series_list for p in s[2] if p[1] is not None]
    all_y=[p[1] for s in series_list for p in s[2] if p[1] is not None]
    if not all_x or not all_y:
        return "<p>No data</p>"
    x_min,x_max=min(all_x),max(all_x)
    y_min,y_max=min(all_y),max(all_y)
    x_pad=(x_max-x_min)*0.1 if x_max>x_min else 10
    y_pad=(y_max-y_min)*0.15 if y_max>y_min else 0.05
    x_min-=x_pad; x_max+=x_pad
    y_min=max(0,y_min-y_pad); y_max+=y_pad
    ml,mr,mt,mb=70,120,30,50
    pw=width-ml-mr; ph=height-mt-mb
    def sx(x): return ml+(x-x_min)/(x_max-x_min)*pw
    def sy(y): return mt+(1-(y-y_min)/(y_max-y_min))*ph
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" style="font-family:monospace">\n'
    svg+=f'<rect width="{width}" height="{height}" fill="white"/>\n'
    for i in range(5):
        gy=y_min+(y_max-y_min)*i/4; py=sy(gy)
        svg+=f'<line x1="{ml}" y1="{py:.1f}" x2="{width-mr}" y2="{py:.1f}" stroke="#e2e8f0" stroke-width="1"/>\n'
        svg+=f'<text x="{ml-5}" y="{py+4:.1f}" text-anchor="end" font-size="10" fill="#64748b">{gy*100:.1f}%</text>\n'
    for xv in [5,10,20,50,100,200,500,1000,1500]:
        if x_min<=xv<=x_max:
            px=sx(xv)
            svg+=f'<line x1="{px:.1f}" y1="{height-mb}" x2="{px:.1f}" y2="{height-mb+4}" stroke="#64748b" stroke-width="1"/>\n'
            svg+=f'<text x="{px:.1f}" y="{height-mb+18}" text-anchor="middle" font-size="10" fill="#64748b">{xv}B</text>\n'
    svg+=f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{height-mb}" stroke="#334155" stroke-width="1.5"/>\n'
    svg+=f'<line x1="{ml}" y1="{height-mb}" x2="{width-mr}" y2="{height-mb}" stroke="#334155" stroke-width="1.5"/>\n'
    svg+=f'<text x="{width/2}" y="{height-8}" text-anchor="middle" font-size="12" fill="#334155">Training Tokens (B)</text>\n'
    svg+=f'<text x="15" y="{height/2}" text-anchor="middle" font-size="12" fill="#334155" transform="rotate(-90 15 {height/2})">{y_label}</text>\n'
    svg+=f'<text x="{width/2}" y="20" text-anchor="middle" font-size="13" fill="#1e293b" font-weight="bold">{title}</text>\n'
    for label,color,points in series_list:
        valid=sorted([(x,y) for x,y in points if y is not None],key=lambda p:p[0])
        if len(valid)<2:
            if len(valid)==1:
                px,py=sx(valid[0][0]),sy(valid[0][1])
                svg+=f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{color}"/>\n'
            continue
        path_d=" ".join(f"L{sx(x):.1f} {sy(y):.1f}" for x,y in valid)
        path_d="M"+path_d[1:]
        svg+=f'<path d="{path_d}" fill="none" stroke="{color}" stroke-width="2"/>\n'
        for x,y in valid:
            px,py=sx(x),sy(y)
            svg+=f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.5" fill="{color}"/>\n'
    ly=mt+10
    for label,color,_ in series_list:
        svg+=f'<rect x="{width-mr+10}" y="{ly}" width="12" height="12" fill="{color}"/>\n'
        svg+=f'<text x="{width-mr+28}" y="{ly+10}" font-size="10" fill="#334155">{label}</text>\n'
        ly+=18
    svg+='</svg>'
    return svg

cs8_series=[
    ("BaiZe-2B (2.22B)","#2563eb",[(p["tokens_B"],p["cs_avg"]) for p in data["baize_2b"]]),
    ("Xmodel-2 (1.2B)","#dc2626",[(p["tokens_B"],p["cs_avg"]) for p in data["xmodel_2"]]),
    ("Xmodel-2.5 (1.3B)","#16a34a",[(p["tokens_B"],p["cs_avg"]) for p in data["xmodel_25"]]),
]
cx_series=[
    ("BaiZe-2B (2.22B)","#2563eb",[(p["tokens_B"],p.get("complex_avg")) for p in data["baize_2b"]]),
    ("Xmodel-2 (1.2B)","#dc2626",[(p["tokens_B"],p.get("complex_avg")) for p in data["xmodel_2"]]),
    ("Xmodel-2.5 (1.3B)","#16a34a",[(p["tokens_B"],p.get("complex_avg")) for p in data["xmodel_25"]]),
]
all_points=[]
for p in data["baize_2b"]: all_points.append(("BaiZe-2B",p))
for p in data["xmodel_2"]: all_points.append(("Xmodel-2",p))
for p in data["xmodel_25"]: all_points.append(("Xmodel-2.5",p))
all_points.sort(key=lambda x:x[1]["tokens_B"])
rows=""
for model,p in all_points:
    hl=' class="highlight"' if model=="BaiZe-2B" else ""
    rows+=f"<tr{hl}><td>{model}</td><td>{p['label']}</td><td>{p['tokens_B']:.1f}B</td><td>{p['params_B']}B</td><td>{to_pct(p['cs_avg'])}</td><td>{to_pct(p.get('complex_avg'))}</td></tr>\n"
now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
cs8_svg=build_svg(cs8_series,"CS8 Avg vs Training Tokens","CS8 Avg")
cx_svg=build_svg(cx_series,"Complex6 Avg vs Training Tokens","Complex6 Avg")
html=f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">
<title>BaiZe-2B vs Xmodel Scaling (Updated)</title>
<style>
body{{font-family:-apple-system,"Microsoft YaHei",sans-serif;margin:0 auto;padding:20px;background:#f8fafc;color:#1e293b;max-width:1200px}}
h1{{color:#1e40af;border-bottom:3px solid #3b82f6;padding-bottom:10px;font-size:22px}}
h2{{color:#334155;margin-top:30px;font-size:18px;border-bottom:1px solid #cbd5e1;padding-bottom:5px}}
table{{border-collapse:collapse;width:100%;margin:15px 0;font-size:13px}}
th,td{{border:1px solid #cbd5e1;padding:6px 10px;text-align:center}}
th{{background:#475569;color:white}}tr:nth-child(even){{background:#f1f5f9}}
.highlight{{background:#fef3c7;font-weight:bold}}
.note{{background:#fffbeb;border-left:4px solid #f59e0b;padding:10px 15px;margin:15px 0;font-size:13px}}
.success{{background:#dcfce7;border-left:4px solid #16a34a;padding:10px 15px;margin:15px 0;font-size:13px}}
.chart{{text-align:center;margin:20px 0}}
.small{{font-size:11px;color:#64748b}}
</style></head><body>
<h1>BaiZe-2B vs Xmodel-2/2.5 Scaling (Updated)</h1>
<p class="small">生成: {now} | CS8 0-shot + Complex6 default shots | lm-eval v0.4.x</p>
<div class="success"><strong>核心发现</strong>：BaiZe-2B P-8 (39.6B) CS8=49.21% > Xmodel-2 s1/10K (39.3B) CS8=46.65%（+2.56pp）。相近 token 量下 BaiZe 常识推理不弱于 Xmodel-2。</div>
<h2>1. 架构对比</h2>
<table><tr><th>模型</th><th>参数</th><th>Token</th><th>架构</th><th>LR</th></tr>
<tr class="highlight"><td>BaiZe-2B</td><td>2.22B</td><td>44.4B</td><td>Mamba2-hybrid</td><td>1e-3</td></tr>
<tr><td>Xmodel-2.5</td><td>1.30B</td><td>1.4T</td><td>Dense 48L</td><td>1.67e-3</td></tr>
<tr><td>Xmodel-2</td><td>1.20B</td><td>1.5T</td><td>Dense 48L</td><td>0.01</td></tr></table>
<h2>2. CS8 Scaling 曲线</h2>
<div class="chart">{cs8_svg}</div>
<p class="small" style="text-align:center">图1：CS8 vs Token。蓝=BaiZe 红=Xmodel-2 绿=Xmodel-2.5。Xmodel-2 s1=stable段历史ckpt。</p>
<h2>3. Complex6 Scaling 曲线</h2>
<div class="chart">{cx_svg}</div>
<p class="small" style="text-align:center">图2：Complex6 vs Token。Xmodel-2 s1/20K-40K缺HumanEval/MBPP（null）。</p>
<h2>4. 逐Checkpoint分数表</h2>
<table><tr><th>模型</th><th>Checkpoint</th><th>Token</th><th>参数</th><th>CS8</th><th>Complex6</th></tr>
{rows}</table>
<h2>5. 关键结论</h2>
<div class="note">
<strong>5.1 相近Token对比 (~39B)</strong><br>
BaiZe P-8 (39.6B) CS8=49.32% vs Xmodel-2 s1/10K (39.3B) CS8=46.65% → BaiZe +2.67pp。<br>
BaiZe final (44.4B) Complex6=6.81% vs Xmodel-2 s1/10K (39.3B) Complex6=8.49% → BaiZe -1.68pp。<br>
<strong>结论</strong>：BaiZe 常识推理更强（+2.56pp），复杂推理略弱（-1.68pp，受44B token量限制）。
</div>
<div class="note">
<strong>5.2 缩放趋势</strong><br>
BaiZe CS8: 4.4B→44.4B = 44.04%→49.21% (+5.17pp)，~20B后趋于平坦。<br>
Xmodel-2 CS8: 39.3B→157.2B = 46.65%→50.31% (+3.66pp)，1.5T final=64.82%。<br>
Xmodel-2.5 CS8: 26.4B→1400B = 46.12%→65.40% (+19.28pp)。<br>
BaiZe在44B token已接近Xmodel-2在157B的CS8水平（49.21% vs 50.31%）。
</div>
<div class="note">
<strong>5.3 架构差异</strong><br>
BaiZe 2.22B约为Xmodel-2 1.2B的1.85×参数。LR低10×（1e-3 vs 0.01）。<br>
Xmodel-2 CS8跃升主要在decay段（SFT+LR退火），BaiZe decay仅4.8B（vs 20B）。
</div>
<hr style="margin:2em 0;border:none;border-top:1px solid #ddd">
<p class="small" style="text-align:center;color:#888">
BaiZe-2B vs Xmodel Scaling · {now}<br>
lm-eval v0.4.x · trust_remote_code=True · Xmodel-2 s1 re-eval 2026-10-16
</p></body></html>"""
with open(REPORT_PATH,"w") as f:
    f.write(html)
print(f"[OK] scaling_report.html updated ({len(html)} bytes)")
print(f"[OK] Points: BaiZe={len(data['baize_2b'])}, XM2={len(data['xmodel_2'])}, XM25={len(data['xmodel_25'])}")
