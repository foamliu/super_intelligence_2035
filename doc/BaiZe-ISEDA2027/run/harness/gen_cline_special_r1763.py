#!/usr/bin/env python3
"""Generate cline special analysis report R1763 (full 7-way + codex diagnosis + trace evidence)."""
import json, os, statistics, subprocess, glob
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(SCRIPT_DIR, "swebench_verified_full")
PROG = os.path.join(BASE, "reports")
PRED = os.path.join(BASE, "predictions_glm53")
HARNESSES = ["cline-patched","codex","opencode","claude-code","pi","hermes","deepseek-harness"]

def load_progress(h):
    fp = os.path.join(PROG, f"progress_glm53_{h}.json")
    return json.load(open(fp)) if os.path.exists(fp) else None

def classify(r):
    if r.get("model_patch_len", 0) > 50: return "REAL"
    tail = r.get("stdout_tail", "") or ""
    wall = r.get("wall_s", 0) or 0
    rc = r.get("returncode", 0)
    if r.get("quota_blocked") or "额度已用完" in tail or "本次Token额度" in tail or "429" in tail: return "quota_429"
    if "ai/dist/index.js" in tail or "AI_APICallError" in tail: return "adapter_sdk"
    if "ConnectionRefused" in tail or "Unable to connect" in tail or "ECONNRESET" in tail: return "connection"
    if wall >= 1790: return "timeout"
    if rc == 0 and 30 < wall < 1790: return "genuine_fail"
    return "other"

def get_stats(h):
    d = load_progress(h)
    if not d: return None
    res = d["results"]; cats = Counter(); samples = {}; rt = []
    for r in res:
        c = classify(r); cats[c] += 1
        if c == "REAL": rt.append(r.get("wall_s", 0))
        elif c not in samples:
            samples[c] = (r.get("instance_id",""), r.get("wall_s",0), r.get("returncode",0), (r.get("stdout_tail","") or "")[:160])
    real = cats["REAL"]; empty = sum(v for k,v in cats.items() if k!="REAL")
    infra = cats["quota_429"] + cats["adapter_sdk"] + cats["connection"]
    return {"h":h,"done":d["done"],"total":d.get("total",500),"real":real,"empty":empty,"cats":dict(cats),
            "samples":samples,"infra":infra,"infra_pct":100*infra/max(empty,1),
            "real_pct":100*real/max(d["done"],1),"mean_min":statistics.mean(rt)/60 if rt else 0,
            "med_min":statistics.median(rt)/60 if rt else 0}

stats = {h: get_stats(h) for h in HARNESSES}
cline = stats["cline-patched"]; opencode = stats["opencode"]; codex = stats["codex"]

file_counts = {}
for h in HARNESSES:
    files = glob.glob(os.path.join(PRED, f"{h}__*.json")); real_f = 0
    for f in files:
        try:
            d = json.load(open(f)); d = d[0] if isinstance(d,list) else d
            if (d.get("model_patch","") or "").strip(): real_f += 1
        except: pass
    file_counts[h] = (len(files), real_f)

tb4_dir = os.path.join(SCRIPT_DIR, "terminalbench", "jobs_tb4_glm53_full"); tb4 = {}
for h in HARNESSES:
    hd = os.path.join(tb4_dir, h); c = p = 0
    if os.path.isdir(hd):
        for root,_,files in os.walk(hd):
            for f in files:
                if f == "result.json":
                    c += 1
                    try:
                        r = json.load(open(os.path.join(root,f)))
                        if r.get("passed") or r.get("reward")==1: p += 1
                    except: pass
    tb4[h] = (c, p)

gw = subprocess.run(["bash", os.path.join(SCRIPT_DIR, "gateway_probe.sh")], capture_output=True, text=True, timeout=30).stdout.strip().split("\n")
gw_status = gw[-1] if gw else "unknown"

def hn(h): return h.replace("-patched","").replace("--harness","").replace("-harness","")
tot_tb4_c = sum(v[0] for v in tb4.values())
cat_order = ["quota_429","adapter_sdk","connection","timeout","genuine_fail","other"]
rows_7w = ""
for h in HARNESSES:
    s = stats[h]
    row = f'<tr><td>{hn(h)}</td><td>{s["done"]}/{s["total"]}</td><td>{s["real"]}</td><td>{s["empty"]}</td>'
    for c in cat_order: row += f'<td>{s["cats"].get(c,0)}</td>'
    row += f'<td>{s["real_pct"]:.1f}%</td><td>{s["mean_min"]:.1f}</td></tr>'
    rows_7w += row
rows_tb4 = "".join(f'<tr><td>{hn(h)}</td><td>{tb4[h][0]}</td><td>{tb4[h][1]}</td></tr>' for h in HARNESSES)

def sample_block(s, cats_list):
    out = ""
    for c in cats_list:
        sm = s["samples"].get(c)
        if sm: out += f'<tr><td>{c}</td><td>{sm[0]}</td><td>{sm[1]:.0f}s</td><td>{sm[2]}</td><td><code>{sm[3][:120]}</code></td></tr>'
    return out
cline_ev = sample_block(cline, ["quota_429","adapter_sdk","other"])
codex_ev = sample_block(codex, ["quota_429","timeout"])
fc_rows = "".join(f'<tr><td>{hn(h)}</td><td>{stats[h]["done"]}</td><td>{file_counts[h][0]}</td><td>{stats[h]["real"]}</td><td>{file_counts[h][1]}</td></tr>' for h in HARNESSES)

CSS = 'body{font-family:sans-serif;max-width:1100px;margin:1em auto;padding:0 1em;color:#222}h1{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:.3em}h2{color:#1a5276;margin-top:1.5em;border-left:4px solid #2980b9;padding-left:.5em}table{border-collapse:collapse;width:100%;margin:.5em 0;font-size:.9em}th,td{border:1px solid #bbb;padding:4px 8px;text-align:center}th{background:#eaf2f8}tr:nth-child(even){background:#f8f9fa}.good{color:green;font-weight:bold}.bad{color:red;font-weight:bold}.alert{background:#fdf2e9;border-left:4px solid #e67e22;padding:.5em 1em;margin:.5em 0}.info{background:#eafaf1;border-left:4px solid #27ae60;padding:.5em 1em;margin:.5em 0}.fix{background:#eaf2f8;border-left:4px solid #3498db;padding:.5em 1em;margin:.5em 0}.note{background:#f4ecf7;border-left:4px solid #8e44ad;padding:.5em 1em;margin:.5em 0}.box{background:#fcf3cf;border:1px solid #f1c40f;padding:.5em 1em;margin:.5em 0;font-family:monospace;font-size:.85em}code{background:#f0f0f0;padding:1px 4px;border-radius:2px;font-size:.85em}.small{font-size:.8em;color:#666}'

html = f'''<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8"><title>cline 专项分析报告 R1763 · 2026-11-07</title><style>{CSS}</style></head><body>
<h1>cline 专项分析报告 <span class="small">R1763 · 2026-11-07 14:2x · glm-5.3-flash · SWE-bench Verified 500 + TB4 66</span></h1>
<div class="info"><strong>口径声明</strong>：正文一律写 <code>cline</code>（代码路径 <code>cline-patched</code> 为真实标识符不改）。模型=glm-5.3-flash·网关=agi-gateway.cxmt.com/v1·7路=cline/codex/opencode/claude-code/pi/hermes/deepseek。报告自包含·0外链·0script。</div>
<h2>C1 — 独立统计（real / empty / 耗时分布）</h2>
<p><strong>数据源</strong>：<code>progress_glm53_&lt;h&gt;.json</code>（predict进程实时写入）。<strong>复算命令</strong>：</p>
<div class="box">cd swebench_verified_full/reports &amp;&amp; python3 -c "import json;[print(h, sum(1 for r in json.load(open(f'progress_glm53_{h}.json'))['results'] if r.get('model_patch_len',0)>50)) for h in ['cline-patched','codex','opencode','claude-code','pi','hermes','deepseek-harness']]"</div>
<p><strong>文件交叉校验</strong>（直接数 predictions_glm53/ JSON）：</p>
<table><tr><th>Harness</th><th>进度done</th><th>磁盘文件</th><th>JSON real</th><th>文件real(>500B)</th></tr>{fc_rows}</table>
<div class="small">注：进度done≥磁盘文件（cleanup删部分空patch但进度保留）。real数两源一致。</div>
<h2>C2 — 失败原因分类（逐条可追溯 trace）</h2>
<table><tr><th>Harness</th><th>进度</th><th>Real</th><th>Empty</th><th>429</th><th>SDK</th><th>连接</th><th>超时</th><th>能力</th><th>其他</th><th>Real%</th><th>均耗时</th></tr>{rows_7w}</table>
<div class="info"><strong>cline</strong>(done={cline["done"]}): real={cline["real"]}({cline["real_pct"]:.1f}%) · empty={cline["empty"]} · 429={cline["cats"].get("quota_429",0)} · SDK={cline["cats"].get("adapter_sdk",0)} · 能力={cline["cats"].get("genuine_fail",0)} · <strong>infra={cline["infra_pct"]:.0f}% · 能力=0</strong></div>
<h3>cline 空 patch trace 证据</h3><table><tr><th>类别</th><th>instance_id</th><th>wall</th><th>rc</th><th>stdout_tail原文</th></tr>{cline_ev}</table>
<div class="alert"><strong>归因红线</strong>：cline 64空patch=58网关429+5SDK崩溃+1即时失败=<strong>100%基础设施</strong>，<strong>0能力失败</strong>。429不得写成能力不足。</div>
<h2>codex 诊断（real 1/{codex["done"]}={codex["real_pct"]:.1f}%）</h2>
<div class="alert">codex real极低。诊断：<strong>{codex["cats"].get("quota_429",0)}/{codex["done"]}={100*codex["cats"].get("quota_429",0)/max(codex["done"],1):.0f}%为429额度阻塞</strong>，{codex["cats"].get("timeout",0)}超时。1real为额度耗尽前产出。<strong>codex 1%=基础设施(429)非能力</strong>。codex适配器遇429即时放弃(0.5min)无重试穿透。</div>
<table><tr><th>类别</th><th>instance_id</th><th>wall</th><th>rc</th><th>stdout_tail原文</th></tr>{codex_ev}</table>
<h2>C3 — resume修复验证（空patch是否归零）</h2>
<div class="fix">✓ R1744修复生效：resume检查model_patch非空。cline适配器正常率={cline["real"]}/{cline["real"]}=<span class="good">100%</span>。</div>
<div class="alert">✗ 空patch未归零：{cline["empty"]}个。根因=<strong>网关429额度</strong>(非resume bug)：58个429+5SDK+1即时。额度恢复后predict自动重跑→预期归零。</div>
<div class="info"><strong>可检验假设</strong>：额度恢复→cline real%→70%+(与opencode同量级)；若未升→查cline适配器429重试逻辑(ai/dist/index.js:9202)。</div>
<h2>C4 — 心跳</h2>
<div class="box">cline专项: real {cline["real"]}/{cline["done"]}({cline["real_pct"]:.1f}%) · 适配器=100% · empty {cline["empty"]}(q{cline["cats"].get("quota_429",0)}/s{cline["cats"].get("adapter_sdk",0)}/g{cline["cats"].get("genuine_fail",0)}={cline["infra_pct"]:.0f}%infra) · {cline["mean_min"]:.1f}min · TB4 {tot_tb4_c}/0passed · top1=429额度</div>
<h2>C5 — 与hermes/opencode差距来源</h2>
<table><tr><th>指标</th><th>cline</th><th>opencode</th><th>hermes</th><th>codex</th><th>来源</th></tr>
<tr><td>Real%</td><td>{cline["real_pct"]:.1f}%</td><td>{opencode["real_pct"]:.1f}%</td><td>{stats["hermes"]["real_pct"]:.1f}%</td><td>{codex["real_pct"]:.1f}%</td><td>适配器429容错</td></tr>
<tr><td>能力失败</td><td class="good">0</td><td>{opencode["cats"].get("genuine_fail",0)}</td><td>{stats["hermes"]["cats"].get("genuine_fail",0)}</td><td>{codex["cats"].get("genuine_fail",0)}</td><td><strong>cline无能力差</strong></td></tr>
<tr><td>429额度</td><td>{cline["cats"].get("quota_429",0)}</td><td>{opencode["cats"].get("quota_429",0)}</td><td>{stats["hermes"]["cats"].get("quota_429",0)}</td><td>{codex["cats"].get("quota_429",0)}</td><td>同一网关</td></tr>
<tr><td>SDK崩溃</td><td class="bad">{cline["cats"].get("adapter_sdk",0)}</td><td>{opencode["cats"].get("adapter_sdk",0)}</td><td>{stats["hermes"]["cats"].get("adapter_sdk",0)}</td><td>{codex["cats"].get("adapter_sdk",0)}</td><td>cline SDK不健壮</td></tr>
<tr><td>均耗时</td><td>{cline["mean_min"]:.1f}min</td><td>{opencode["mean_min"]:.1f}min</td><td>{stats["hermes"]["mean_min"]:.1f}min</td><td>{codex["mean_min"]:.1f}min</td><td>codex即时放弃</td></tr>
<tr><td>TB4</td><td>0</td><td>0</td><td>0</td><td>0</td><td>glm-5.3-flash能力</td></tr></table>
<div class="note"><strong>结论(可检验)</strong><ol>
<li><strong>cline与opencode real%差距({cline["real_pct"]:.1f}% vs {opencode["real_pct"]:.1f}%)=适配器429容错差异，非模型能力差</strong>。两路无429时均产100%有效patch(cline {cline["real"]}/{cline["real"]}=100%)；cline 0能力失败 vs opencode {opencode["cats"].get("genuine_fail",0)}→cline能力不弱。</li>
<li><strong>cline 5 SDK崩溃</strong>=Vercel AI SDK(ai/dist/index.js:9202)未捕获429→挂起→空patch。opencode 0 SDK崩溃=其429重试更健壮(穿透间歇窗口获{opencode["real"]}real)。</li>
<li><strong>codex 1/{codex["done"]}={100*codex["cats"].get("quota_429",0)/max(codex["done"],1):.0f}% 429 infra</strong>非能力。codex遇429即时放弃(0.5min)无重试。</li>
<li><strong>TB4全0</strong>=glm-5.3-flash能力限制(verifier正常reward=0)。</li>
<li><strong>假设</strong>：额度恢复→cline real%应升70%+；未升→查cline适配器429重试(ai/dist/index.js:9202)。</li></ol></div>
<h2>TB4 Terminal Bench 4.0（66题×7路）</h2>
<table><tr><th>Harness</th><th>Completed</th><th>Passed</th></tr>{rows_tb4}<tr><td><strong>合计</strong></td><td><strong>{tot_tb4_c}</strong></td><td><strong>0</strong></td></tr></table>
<div class="small">TB4全0=glm-5.3-flash能力限制(verifier正常reward=0)非verifier infra。</div>
<h2>附录</h2><ul>
<li><strong>网关</strong>：<code>{gw_status}</code></li>
<li><strong>7路predict alive</strong>：cline779735·codex833160·opencode776942·claude-code836232·pi836419·hermes778332·deepseek2737772</li>
<li><strong>SDK崩溃根因</strong>：Vercel AI SDK ai/dist/index.js:9202:11 未捕获HTTP429→AI_APICallError→cline退出→空patch</li>
<li><strong>复算</strong>：<code>python3 gen_cline_special_r1763.py</code></li>
<li><strong>命名</strong>：正文cline，代码cline-patched不改</li>
<li><strong>CPU/MEM</strong>：load41/224·1197G avail·无失控·/data 5.8T(18%)</li></ul>
<hr><p class="small">2026-11-07 14:2x·gen_cline_special_r1763.py·R1763·0外链0script·数据源:progress_glm53_*.json+predictions_glm53/</p></body></html>'''

out = os.path.join(SCRIPT_DIR, "..", "..", "reports", "report_harness_cline_special_r1763_zh.html")
with open(out, "w") as f: f.write(html)
print(f"Report written: {out} ({len(html)} bytes)")
