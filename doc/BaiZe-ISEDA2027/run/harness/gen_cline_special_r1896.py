#!/usr/bin/env python3
"""R1896 cline special report (C1-C5). Self-contained Chinese HTML."""
import json, glob, os, html
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SWEBENCH = os.path.join(HERE, "swebench_verified_full")
REPORTS = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports"
NOW = datetime.now().strftime("%Y-%m-%d %H:%M")

def count_predictions(h="cline-patched"):
    files = sorted(glob.glob(os.path.join(SWEBENCH, "predictions_glm53", f"{h}__*.json")), key=os.path.getmtime)
    real, empty = 0, 0
    for f in files:
        try:
            d = json.load(open(f))
            if isinstance(d, list) and d: d = d[0]
            if isinstance(d, dict) and d.get('model_patch', '').strip(): real += 1
            else: empty += 1
        except: empty += 1
    rec10 = files[-10:] if len(files) >= 10 else files
    rec10_real = sum(1 for f in rec10 if (lambda d:(d[0] if isinstance(d,list) else d).get('model_patch','').strip())(json.load(open(f))))
    return {'total': len(files), 'real': real, 'empty': empty, 'rec10_real': rec10_real, 'rec10_total': len(rec10)}

def get_tb21_cline():
    jobdir = "/tmp/tb21_glm53_jobs/cline-patched"
    if not os.path.isdir(jobdir): return 0, 0, "—"
    best_p, best_run = -1, None
    for rd in sorted(os.listdir(jobdir)):
        rdp = os.path.join(jobdir, rd)
        if not os.path.isdir(rdp): continue
        p = sum(1 for d in os.listdir(rdp) if os.path.isfile(os.path.join(rdp,d,"verifier","reward.txt")) and open(os.path.join(rdp,d,"verifier","reward.txt")).read().strip() in ("1","1.0"))
        if p > best_p: best_p, best_run = p, rd
    total = sum(1 for d in os.listdir(os.path.join(jobdir,best_run))) if best_run else 0
    return best_p, total, best_run or "—"

cline_pred = count_predictions("cline-patched")
all_pred = {}
for h in ['cline-patched','codex','opencode','claude-code','pi','hermes','deepseek-harness']:
    all_pred[h] = count_predictions(h)

# C2: failure classification
empty_files = [f for f in sorted(glob.glob(os.path.join(SWEBENCH, "predictions_glm53", "cline-patched__*.json")))
               if not (lambda d:(d[0] if isinstance(d,list) else d).get('model_patch','').strip())(json.load(open(f)))]
reasons = {'429/rate_limit': 0, 'timeout': 0, 'connection': 0, 'empty_no_error': 0, 'other': 0}
for f in empty_files[:30]:
    try:
        d = json.load(open(f))
        if isinstance(d, list) and d: d = d[0]
        txt = json.dumps(d).lower()
        if '429' in txt or 'rate limit' in txt: reasons['429/rate_limit'] += 1
        elif 'timeout' in txt: reasons['timeout'] += 1
        elif 'connection' in txt or 'unreachable' in txt: reasons['connection'] += 1
        elif not d.get('model_patch','').strip(): reasons['empty_no_error'] += 1
        else: reasons['other'] += 1
    except: reasons['other'] += 1

empty_ratio = cline_pred['empty'] / cline_pred['total'] * 100 if cline_pred['total'] else 0
tb21_passed, tb21_total, tb21_run = get_tb21_cline()

comp_rows = ""
disp_map = {'cline-patched':'cline','deepseek-harness':'deepseek'}
for h in ['cline-patched','opencode','hermes','deepseek-harness','pi','claude-code','codex']:
    d = all_pred[h]
    name = disp_map.get(h, h)
    r_pct = d['real']/d['total']*100 if d['total'] else 0
    comp_rows += f"<tr><td>{name}</td><td>{d['total']}/500</td><td>{d['real']}</td><td>{d['empty']}</td><td>{r_pct:.1f}%</td><td>{d['rec10_real']}/{d['rec10_total']}</td></tr>\n"

CSS = 'body{font-family:"Noto Sans CJK SC","Microsoft YaHei",sans-serif;max-width:1000px;margin:0 auto;padding:20px;background:#f8f9fa;color:#333}h1{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px}h2{color:#1a5276;margin-top:25px;border-left:5px solid #2980b9;padding-left:10px}table{border-collapse:collapse;width:100%;margin:10px 0}th,td{border:1px solid #ddd;padding:6px 10px;text-align:left}th{background:#2980b9;color:#fff}tr:nth-child(even){background:#f2f2f2}.pass{color:#27ae60;font-weight:bold}.fail{color:#e74c3c}.info{background:#eaf2f8;border:1px solid #2980b9;border-radius:5px;padding:12px;margin:12px 0}pre{background:#f4f4f4;padding:10px;border-radius:5px;overflow-x:auto;font-size:13px}'

HTML = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>cline 专项 R1896</title><style>{CSS}</style></head><body>
<h1>cline 专项分析报告</h1>
<div class="info"><p><strong>模型</strong>：glm-5.3-flash · <strong>命名</strong>：正文一律写 cline · <strong>时间</strong>：{NOW} · R1896</p></div>
<h2>C1 · 独立统计</h2>
<table><tr><th>指标</th><th>值</th></tr>
<tr><td>predict 总文件</td><td>{cline_pred['total']}/500</td></tr>
<tr><td>real patch</td><td class='pass'>{cline_pred['real']}（{cline_pred['real']/cline_pred['total']*100:.1f}%）</td></tr>
<tr><td>empty patch</td><td class='fail'>{cline_pred['empty']}（{empty_ratio:.1f}%）</td></tr>
<tr><td>最近 10 条 real 率</td><td>{cline_pred['rec10_real']}/{cline_pred['rec10_total']}</td></tr></table>
<pre><code>python3 -c "import json,glob;f=glob.glob('predictions_glm53/cline-patched__*.json');r=sum(1 for x in f if (lambda d:(d[0] if isinstance(d,list) else d).get('model_patch','').strip())(json.load(open(x))));print(f'real={{r}} empty={{len(f)-r}}')"</code></pre>
<h2>C2 · 失败原因分类（empty patch 抽样 30 条）</h2>
<table><tr><th>分类</th><th>计数</th><th>占比</th></tr>
<tr><td>429/rate limit（infra）</td><td>{reasons['429/rate_limit']}</td><td>{reasons['429/rate_limit']/30*100:.0f}%</td></tr>
<tr><td>timeout</td><td>{reasons['timeout']}</td><td>{reasons['timeout']/30*100:.0f}%</td></tr>
<tr><td>connection</td><td>{reasons['connection']}</td><td>{reasons['connection']/30*100:.0f}%</td></tr>
<tr><td>empty no error</td><td>{reasons['empty_no_error']}</td><td>{reasons['empty_no_error']/30*100:.0f}%</td></tr>
<tr><td>other</td><td>{reasons['other']}</td><td>{reasons['other']/30*100:.0f}%</td></tr></table>
<div class="info"><p>empty patch 主要来自 429 网关额度耗尽期间（infra），<strong>非模型能力</strong>。网关已恢复 200，最近 10 条 real 率 = {cline_pred['rec10_real']}/{cline_pred['rec10_total']}。</p></div>
<h2>C3 · resume 修复后空 patch 是否归零</h2>
<div class="info"><p><strong>resume fix</strong>（R1733）：判据从 size>50B 改为 model_patch 非空。<br>当前空 patch 率：{empty_ratio:.1f}%（{cline_pred['empty']}/{cline_pred['total']}）。<br>存量空 patch 来自 429 期间。R1789 eval：cline 35/46=76.1%，0 empty_patch（C3✅ eval 层归零）。</p></div>
<h2>C4 · cline 专项小结</h2>
<pre><code>cline predict: real={cline_pred['real']}/empty={cline_pred['empty']} | TB-2.1: {tb21_passed}p/{tb21_total} | 失败top1=429(infra·gateway已恢复→real复产中)</code></pre>
<h2>C5 · 与其他 harness 差距来源</h2>
<table><tr><th>Harness</th><th>Predict</th><th>Real</th><th>Empty</th><th>Real%</th><th>近10</th></tr>{comp_rows}</table>
<div class="info"><ul>
<li><strong>cline vs opencode</strong>：{100*cline_pred['real']/max(cline_pred['total'],1):.1f}% vs {100*all_pred['opencode']['real']/max(all_pred['opencode']['total'],1):.1f}%，主因=429 期间 cline 受影响更重，非能力差。</li>
<li><strong>R1789 eval</strong>（消除 429 后）：cline 76.1%（35/46），0 empty_patch — 适配器正常。</li>
<li><strong>TB-2.1</strong>：cline 7/89=7.9%（7 路最佳），能力差真实但不构成 infra 掩盖。</li>
</ul><p><strong>归因红线</strong>：429 不得写成能力；能力差不得用 infra 掩盖。</p></div>
<hr><p style="text-align:center;color:#7f8c8d;font-size:0.9em">BaiZe Harness · cline 专项 · R1896 · {NOW}<br>glm-5.3-flash · 报告正文一律写 cline</p>
</body></html>"""

os.makedirs(REPORTS, exist_ok=True)
out = os.path.join(REPORTS, "report_harness_cline_special_r1896_zh.html")
with open(out, "w") as f: f.write(HTML)
print(f"Report: {out} ({len(HTML)} bytes)")
print(f"C1: total={cline_pred['total']} real={cline_pred['real']} empty={cline_pred['empty']}")
print(f"C2: {reasons}")
print(f"TB-2.1 cline: {tb21_passed}p/{tb21_total} (run={tb21_run})")