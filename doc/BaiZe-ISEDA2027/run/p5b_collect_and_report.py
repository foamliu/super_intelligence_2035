#!/usr/bin/env python3
"""P-5b ②③: Collect lm_eval results from all 6 milestone checkpoints and generate
two self-contained HTML reports:
  1. report_pretrain_p5b_8sets.html — P-5b 8-set common-sense eval + data scaling
  2. report_pretrain_p6b_scaling.html — P-6② capability vs token scaling law
"""
import json, os, glob, math
from collections import defaultdict

BASE = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p5b/lm_eval_results"
DOC = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027"

MILESTONES = [
    (156,  0.655, "655M"), (312, 1.31, "1.3B"), (624, 2.62, "2.6B"),
    (1248, 5.24, "5.2B"), (2496, 10.48, "10.5B"), (4771, 20.05, "20B"),
]
TASKS = [
    ("arc_challenge","acc_norm","ARC-Challenge"),("arc_easy","acc_norm","ARC-Easy"),
    ("boolq","acc","BoolQ"),("hellaswag","acc_norm","HellaSwag"),
    ("openbookqa","acc_norm","OpenBookQA"),("piqa","acc_norm","PiQA"),
    ("sciq","acc_norm","SciQ"),("winogrande","acc","Winogrande"),
]
REF_MODELS = [
    ("TinyLLaMA1.1-1.1B",55.24),("Llama-3.2-1B",57.70),("OpenELM-1.1B",56.95),
    ("MiniCPM-1.2B",59.45),("Xmodel-2-1.2B",61.79),("Qwen2.5-1.5B",63.14),("Phi-1.5-1.3B",65.68),
]

def collect_results():
    results = {}
    for iter_num, tokens, label in MILESTONES:
        iter_str = f"iter_{iter_num:04d}"
        iter_dir = os.path.join(BASE, iter_str)
        if not os.path.isdir(iter_dir):
            continue
        task_results = {}
        for json_path in glob.glob(os.path.join(iter_dir, "**", "results_*.json"), recursive=True):
            with open(json_path) as f:
                data = json.load(f)
            for task_name, task_data in data.get("results", {}).items():
                if task_name in [t[0] for t in TASKS]:
                    task_results[task_name] = task_data
        results[iter_num] = task_results
        print(f"  {iter_str}: {len(task_results)}/8 tasks")
    return results

def get_metric(td, m):
    return td.get(f"{m},none", None)

def compute_avg(tr):
    vals = []
    for tid, metric, _ in TASKS:
        if tid in tr:
            v = get_metric(tr[tid], metric)
            if v is not None:
                vals.append(v)
    return sum(vals)/len(vals) if vals else None

def generate_svg(points, refs, title, y_label, w=800, h=500):
    all_y = [v for _, v, _ in points if v is not None] + [v/100 for _, v in refs]
    if not all_y:
        all_y = [0, 1]
    y_min = min(min(all_y)*0.9, 0)
    y_max = max(max(all_y)*1.1, 0.7)
    x_min, x_max = 0.1, 100
    lm, lM = math.log10(x_min), math.log10(x_max)
    def xp(x): return 80 + (math.log10(x)-lm)/(lM-lm)*(w-120)
    def yp(y): return h-60 - (y-y_min)/(y_max-y_min)*(h-100)
    s = [f'<svg width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg" style="font-family:monospace;font-size:11px">']
    s.append(f'<rect x="0" y="0" width="{w}" height="{h}" fill="#1a1a2e"/>')
    for xt in [0.1,1,10,100]:
        px = xp(xt); lab = f"{xt}B" if xt>=1 else f"{int(xt*1000)}M"
        s.append(f'<line x1="{px:.1f}" y1="{h-60}" x2="{px:.1f}" y2="{h-55}" stroke="#666"/>')
        s.append(f'<text x="{px:.1f}" y="{h-40}" fill="#aaa" text-anchor="middle">{lab}</text>')
        s.append(f'<line x1="{px:.1f}" y1="20" x2="{px:.1f}" y2="{h-60}" stroke="#333" stroke-dasharray="2,4"/>')
    for i in range(6):
        yv = y_min+(y_max-y_min)*i/5; py = yp(yv)
        s.append(f'<line x1="75" y1="{py:.1f}" x2="80" y2="{py:.1f}" stroke="#666"/>')
        s.append(f'<text x="70" y="{py+4:.1f}" fill="#aaa" text-anchor="end">{yv*100:.1f}%</text>')
    s.append(f'<text x="{w/2}" y="{h-10}" fill="#ccc" text-anchor="middle">Training Tokens (log)</text>')
    s.append(f'<text x="20" y="{h/2}" fill="#ccc" text-anchor="middle" transform="rotate(-90,20,{h/2})">{y_label}</text>')
    cols = ['#e74c3c','#f39c12','#9b59b6','#1abc9c','#3498db','#e67e22','#2ecc71']
    for i,(nm,vl) in enumerate(refs):
        py = yp(vl/100); c = cols[i%len(cols)]
        s.append(f'<line x1="80" y1="{py:.1f}" x2="{w-40}" y2="{py:.1f}" stroke="{c}" stroke-dasharray="4,4" opacity="0.6"/>')
        s.append(f'<text x="{w-35}" y="{py+4:.1f}" fill="{c}" font-size="10">{nm}({vl:.1f}%)</text>')
    vp = [(t,v,l) for t,v,l in points if v is not None]
    if len(vp)>=2:
        pts = " ".join(f"{xp(t):.1f},{yp(v):.1f}" for t,v,_ in vp)
        s.append(f'<polyline points="{pts}" fill="none" stroke="#00ff88" stroke-width="2.5"/>')
    for t,v,l in vp:
        px,py = xp(t),yp(v)
        s.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="#00ff88" stroke="#fff"/>')
        s.append(f'<text x="{px+6:.1f}" y="{py-8:.1f}" fill="#fff" font-size="10">{l}</text>')
    s.append(f'<text x="{w/2}" y="15" fill="#fff" text-anchor="middle" font-size="13" font-weight="bold">{title}</text>')
    s.append('</svg>')
    return '\n'.join(s)

CSS = "body{background:#0d1117;color:#c9d1d9;font-family:monospace;margin:0;padding:20px;max-width:1200px}" \
      "h1{color:#58a6ff;border-bottom:1px solid #30363d;padding-bottom:10px}" \
      "h2{color:#79c0ff;margin-top:30px}h3{color:#79c0ff}" \
      "table{border-collapse:collapse;width:100%;margin:10px 0}" \
      "th,td{border:1px solid #30363d;padding:6px 10px;text-align:center}" \
      "th{background:#161b22;color:#58a6ff}.best{color:#3fb950;font-weight:bold}.warn{color:#f85149}" \
      ".meta{color:#8b949e;font-size:12px;margin:5px 0}" \
      ".cmd{background:#161b22;padding:10px;border-radius:5px;overflow-x:auto;color:#8b949e;font-size:12px;border:1px solid #30363d}" \
      ".conclusion{background:#161b22;padding:15px;border-radius:5px;border-left:3px solid #f0883e;margin:15px 0}"

def generate_p5b_html(results):
    h = [f"<!DOCTYPE html><html><head><meta charset='UTF-8'><title>P-5b 8-Set Eval</title>",
         f"<style>{CSS}</style></head><body>",
         "<h1>P-5b: 8-Set Common-Sense Zero-Shot Evaluation + Data Scaling</h1>",
         "<div class='meta'>BaiZe (Mamba2-hybrid 2.22B) | lm-eval 0.4.13 | zero-shot | 2026-10-05<br>"
         "Conversion: mcore distcp → HF nemotron_h (323 keys, 2.220B params) | GPU: .29 GPU0-1</div>",
         "<h2>1. Conversion + Evaluation Pipeline</h2>",
         "<div class='cmd'>PYTHONPATH=.../omegaconf_230 python baize_p6_ckpt_to_hf.py --ckpt .../iter_0000XXXX "
         "--tokenizer .../tokenizer_eod --out .../hf_iter_XXXX<br><br>"
         "HF_DATASETS_OFFLINE=1 PYTHONPATH=.../p6_tf5 python -m lm_eval --model hf "
         "--model_args 'pretrained=.../hf_iter_XXXX,dtype=bfloat16' --tasks &lt;task&gt; --num_fewshot 0 --batch_size 8</div>",
         "<div class='meta'>8 tasks: ARC-C, ARC-E, BoolQ, HellaSwag, OBQA, PiQA, SciQ, Winogrande. "
         "Avg = acc_norm for MC tasks, acc for BoolQ/Winogrande. TriviaQA excluded (not in Table 2).</div>",
         "<h2>2. Full Results (harness-standard Avg)</h2>",
         "<table><tr><th>Tokens</th><th>Iter</th>"]
    for _,_,lab in TASKS:
        h.append(f"<th>{lab}</th>")
    h.append("<th><b>Avg</b></th></tr>")
    for it,tk,lab in MILESTONES:
        tr = results.get(it,{}); avg = compute_avg(tr)
        h.append(f"<tr><td>{lab}</td><td>{it}</td>")
        for tid,mt,_ in TASKS:
            v = get_metric(tr.get(tid,{}),mt) if tid in tr else None
            h.append(f"<td>{v*100:.2f}%</td>" if v is not None else "<td class='warn'>—</td>")
        h.append(f"<td class='best'>{avg*100:.2f}%</td></tr>" if avg else "<td class='warn'>—</td></tr>")
    h.append("</table>")
    # Raw acc table
    h.append("<h2>3. Raw Accuracy (acc)</h2><table><tr><th>Tokens</th>")
    for _,_,lab in TASKS: h.append(f"<th>{lab}</th>")
    h.append("<th>raw Avg</th></tr>")
    for it,tk,lab in MILESTONES:
        tr = results.get(it,{}); vs=[]
        h.append(f"<tr><td>{lab}</td>")
        for tid,_,_ in TASKS:
            v = get_metric(tr.get(tid,{}),"acc") if tid in tr else None
            if v is not None: vs.append(v); h.append(f"<td>{v*100:.2f}%</td>")
            else: h.append("<td class='warn'>—</td>")
        h.append(f"<td>{sum(vs)/len(vs)*100:.2f}%</td></tr>" if vs else "<td class='warn'>—</td></tr>")
    h.append("</table>")
    # Scaling chart
    h.append("<h2>4. Data Scaling Curve</h2>")
    ap = [(tk, compute_avg(results.get(it,{})), lab) for it,tk,lab in MILESTONES if compute_avg(results.get(it,{}))]
    if ap:
        h.append(generate_svg(ap, REF_MODELS, "Common-Sense Avg vs Training Tokens", "Avg Accuracy (%)"))
        h.append("<h2>5. Per-Task Scaling</h2>")
        for tid,mt,lab in TASKS:
            pts = [(tk, get_metric(results.get(it,{}).get(tid,{}),mt), tl) for it,tk,tl in MILESTONES if get_metric(results.get(it,{}).get(tid,{}),mt) is not None]
            if pts:
                h.append(f"<h3>{lab}</h3>")
                h.append(generate_svg(pts, [], f"{lab} vs Tokens", f"{mt} (%)", 700, 350))
    else:
        h.append("<p class='warn'>No data yet.</p>")
    h.append("</body></html>")
    return '\n'.join(h)

def generate_p6b_html(results):
    h = [f"<!DOCTYPE html><html><head><meta charset='UTF-8'><title>P-6② Scaling</title>",
         f"<style>{CSS}</style></head><body>",
         "<h1>P-6②: Capability vs Token Scaling Law + Extrapolation</h1>",
         "<div class='meta'>BaiZe (Mamba2-hybrid 2.22B) | 6 milestones: 655M → 20B tokens | 2026-10-05</div>",
         "<h2>1. Purpose</h2>",
         "<p>Trace how common-sense reasoning scales with training tokens using 6 P-5b milestone checkpoints. "
         "Extrapolate to estimate token budget for target accuracy → inform P-8 decision.</p>",
         "<h2>2. Input Checkpoints</h2>",
         "<table><tr><th>Iter</th><th>Tokens</th><th>Label</th></tr>"]
    losses = {156:"~5.5",312:"~4.8",624:"~4.0",1248:"~3.2",2496:"~2.5",4771:"1.9141"}
    for it,tk,lab in MILESTONES:
        h.append(f"<tr><td>{it}</td><td>{tk}B</td><td>{lab}</td></tr>")
    h.append("</table>")
    h.append("<h2>3. Pre-Registered Criteria</h2><ul>"
             "<li><b>Primary</b>: Clear power-law/log trend in Avg vs tokens?</li>"
             "<li><b>Targets</b>: 50% (weakest 1B), 55% (TinyLLaMA), 60% (above Xmodel-2)</li>"
             "<li><b>Fit</b>: acc = a − b·N^(−c) or acc = a + b·log10(N); report R²</li>"
             "<li><b>Caveat</b>: ≤6 points, steep-rise → high uncertainty</li></ul>")
    # Scaling curve + extrapolation
    h.append("<h2>4. Scaling Curve + Fit</h2>")
    ap = [(tk, compute_avg(results.get(it,{})), lab) for it,tk,lab in MILESTONES if compute_avg(results.get(it,{}))]
    if ap and len(ap) >= 2:
        h.append(generate_svg(ap, REF_MODELS, "Avg vs Training Tokens (scaling law)", "Avg Accuracy (%)"))
        import numpy as np
        ta = np.array([p[0] for p in ap]); aa = np.array([p[1]*100 for p in ap])
        lt = np.log10(ta); c = np.polyfit(lt, aa, 1)
        r2 = 1 - np.sum((aa - np.polyval(c, lt))**2) / np.sum((aa - np.mean(aa))**2)
        h.append(f"<h3>Log-Linear: acc = {c[0]:.2f}×log10(N) + {c[1]:.2f} (R²={r2:.4f})</h3>")
        h.append("<table><tr><th>Target</th><th>Est. Tokens</th><th>GPU-days (8×H100@92.6K tok/s)</th></tr>")
        for tgt in [50,55,60]:
            if c[0] > 0:
                ln = (tgt - c[1]) / c[0]; n = 10**ln
                gd = n*1e9/92600/86400
                h.append(f"<tr><td>{tgt}%</td><td>{n:.1f}B</td><td>{gd:.1f} days</td></tr>")
            else:
                h.append(f"<tr><td>{tgt}%</td><td colspan='2' class='warn'>Slope ≤0</td></tr>")
        h.append("</table>")
        # Power-law fit
        try:
            from scipy.optimize import curve_fit
            def pl(N,a,b,cc): return a - b*np.power(N,-cc)
            popt,_ = curve_fit(pl, ta, aa, p0=[70,70,0.3], maxfev=10000)
            pr2 = 1 - np.sum((aa - pl(ta,*popt))**2) / np.sum((aa - np.mean(aa))**2)
            h.append(f"<h3>Power-Law: acc = {popt[0]:.2f} − {popt[1]:.2f}×N^(−{popt[2]:.3f}) (R²={pr2:.4f})</h3>")
        except Exception as e:
            h.append(f"<p class='warn'>Power-law fit failed: {e}</p>")
    else:
        h.append("<p class='warn'>Insufficient data.</p>")
    # Conclusion
    h.append("<h2>5. Conclusion for P-8 Token Budget</h2><div class='conclusion'>")
    if ap and len(ap) >= 3:
        import numpy as np
        ta = np.array([p[0] for p in ap]); aa = np.array([p[1]*100 for p in ap])
        lt = np.log10(ta); c = np.polyfit(lt, aa, 1)
        r2 = 1 - np.sum((aa - np.polyval(c, lt))**2) / np.sum((aa - np.mean(aa))**2)
        if c[0] > 0 and r2 > 0.8:
            n55 = 10**((55-c[1])/c[0]); gd55 = n55*1e9/92600/86400
            h.append(f"<p>Log-linear (R²={r2:.3f}): 55% Avg needs ~{n55:.0f}B tokens (~{gd55:.0f} GPU-days).</p>")
            if gd55 < 30:
                h.append(f"<p class='ok'>→ Feasible. P-8 budget: ~{n55:.0f}B tokens.</p>")
            else:
                h.append(f"<p class='warn'>→ {gd55:.0f} days may exceed timeline. Recommend 100B, note 55% may not be reached.</p>")
        elif r2 <= 0.8:
            h.append(f"<p>R²={r2:.3f} too low for reliable extrapolation with {len(ap)} points in steep-rise.</p>")
            h.append("<p>→ Recommend 100B budget (per task spec), re-evaluate after P-8.</p>")
        else:
            h.append("<p>Slope ≤ 0 — unexpected. Investigate.</p>")
    else:
        h.append("<p>Will be updated when eval completes.</p>")
    h.append("</div>")
    h.append("<h2>6. Uncertainty</h2><div class='meta'>"
             "⚠️ ≤6 points in steep-rise → high uncertainty. Power-law and log-linear may diverge. "
             "Treat as order-of-magnitude guidelines. P-8 run = true out-of-sample test.</div>")
    h.append("</body></html>")
    return '\n'.join(h)

def main():
    print("Collecting results..."); results = collect_results()
    print("Generating P-5b HTML..."); 
    with open(os.path.join(DOC,"report_pretrain_p5b_8sets.html"),'w') as f:
        f.write(generate_p5b_html(results))
    print("Generating P-6② HTML...")
    with open(os.path.join(DOC,"report_pretrain_p6b_scaling.html"),'w') as f:
        f.write(generate_p6b_html(results))
    print("Done!")

if __name__ == "__main__":
    main()

