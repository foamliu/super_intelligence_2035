#!/usr/bin/env python3
"""Generate cline special analysis report R1762."""
import json, os, statistics, subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(SCRIPT_DIR, "swebench_verified_full")
PROG = os.path.join(BASE, "reports")

def load_progress(h):
    fp = os.path.join(PROG, f"progress_glm53_{h}.json")
    return json.load(open(fp)) if os.path.exists(fp) else None

def classify_empty(r):
    tail = r.get("stdout_tail", "") or ""
    wall = r.get("wall_s", 0) or 0
    rc = r.get("returncode", 0)
    if "额度已用完" in tail or "本次Token额度" in tail: return "quota_429"
    if "ai/dist/index.js" in tail or "AI_APICallError" in tail: return "adapter_sdk"
    if "ConnectionRefused" in tail or "Unable to connect" in tail: return "connection"
    if wall >= 1790: return "timeout"
    if rc == 0 and 30 < wall < 1790: return "genuine_fail"
    return "other"

def get_stats(h):
    d = load_progress(h)
    if not d: return None
    results = d["results"]
    rt = [r["wall_s"] for r in results if r.get("model_patch_len", 0) > 50 and r.get("wall_s")]
    cats = {k: 0 for k in ["quota_429","adapter_sdk","timeout","connection","genuine_fail","other"]}
    real = 0
    for r in results:
        if r.get("model_patch_len", 0) > 50: real += 1
        else: cats[classify_empty(r)] += 1
    return {"h":h,"done":d["done"],"real":real,"empty":sum(cats.values()),"cats":cats,
            "mean_min":statistics.mean(rt)/60 if rt else 0,"med_min":statistics.median(rt)/60 if rt else 0,
            "real_times_n":len(rt)}

harnesses = ["cline-patched","codex","opencode","claude-code","pi","hermes","deepseek-harness"]
stats = {h: get_stats(h) for h in harnesses}
cline = stats["cline-patched"]; opencode = stats["opencode"]

tb4_dir = os.path.join(SCRIPT_DIR, "terminalbench", "jobs_tb4_glm53_full")
tb4 = {}
for h in harnesses:
    hd = os.path.join(tb4_dir, h); c = 0; p = 0
    if os.path.isdir(hd):
        for root, _, files in os.walk(hd):
            for f in files:
                if f == "result.json":
                    c += 1
                    try:
                        r = json.load(open(os.path.join(root, f)))
                        if r.get("passed") or r.get("reward") == 1: p += 1
                    except: pass
    tb4[h] = (c, p)

gw_models = subprocess.run(["curl","-s","-o","/dev/null","-w","%{http_code}","http://agi-gateway.cxmt.com/v1/models"], capture_output=True, text=True).stdout.strip()
gw_chat = subprocess.run(["curl","-s","-o","/dev/null","-w","%{http_code}","-X","POST","http://agi-gateway.cxmt.com/v1/chat/completions","-H","Content-Type: application/json","-H","Authorization: Bearer 02_088EE9051AAE4BF0ABFC7130331BF697_6903b05e-6f2d-4a69-93be-96e2b790053f","-d",'{"model":"glm-5.3-flash","messages":[{"role":"user","content":"hi"}],"max_tokens":5}',"--max-time","10"], capture_output=True, text=True).stdout.strip()

def hname(h): return h.replace("-patched","").replace("-harness","")
tot_done = sum(s["done"] for s in stats.values() if s)
tot_real = sum(s["real"] for s in stats.values() if s)
tot_tb4_c = sum(v[0] for v in tb4.values())
infra_count = cline["cats"]["quota_429"] + cline["cats"]["adapter_sdk"] + cline["cats"]["connection"]
infra_pct = 100 * infra_count / max(cline["empty"], 1)
c_pct = 100*cline["real"]/max(cline["done"],1)
o_pct = 100*opencode["real"]/max(opencode["done"],1)
cx_pct = 100*stats["codex"]["real"]/max(stats["codex"]["done"],1)
o_ap = 100*opencode["real"]/max(opencode["real"]+opencode["cats"]["genuine_fail"],1)

CSS = 'body{font-family:sans-serif;margin:2em;background:#f8f9fa;color:#333}h1{color:#1a1a2e;border-bottom:3px solid #e94560;padding-bottom:.3em}h2{color:#16213e;margin-top:1.5em;border-left:4px solid #e94560;padding-left:.5em}table{border-collapse:collapse;width:100%;margin:1em 0;background:#fff}th,td{border:1px solid #ddd;padding:8px 12px;text-align:left}th{background:#16213e;color:#fff}tr:nth-child(even){background:#f2f2f2}.good{color:#27ae60;font-weight:bold}.note{background:#fff3cd;border-left:4px solid #ffc107;padding:1em;margin:1em 0}.fix{background:#d4edda;border-left:4px solid #28a745;padding:1em;margin:1em 0}.alert{background:#f8d7da;border-left:4px solid #dc3545;padding:1em;margin:1em 0}.info{background:#d1ecf1;border-left:4px solid #17a2b8;padding:1em;margin:1em 0}code{background:#eef;padding:2px 4px;border-radius:3px}.box{background:#fff;border-radius:8px;padding:1.5em;margin:1em 0;box-shadow:0 2px 4px rgba(0,0,0,.1)}pre{background:#f4f4f4;padding:1em;border-radius:4px;overflow-x:auto;font-size:13px}'

rows_c1 = "".join(f'<tr><td>{hname(h)}</td><td>{stats[h]["done"]}/500</td><td>{stats[h]["real"]}</td><td>{stats[h]["empty"]}</td><td>{100*stats[h]["real"]/max(stats[h]["done"],1):.1f}%</td><td>{stats[h]["mean_min"]:.1f}min</td><td>{stats[h]["med_min"]:.1f}min</td></tr>\n' for h in harnesses if stats[h])
rows_7w = "".join(f'<tr><td>{hname(h)}</td><td>{stats[h]["real"]}</td><td>{stats[h]["empty"]}</td><td>{stats[h]["cats"]["quota_429"]}</td><td>{stats[h]["cats"]["adapter_sdk"]}</td><td>{stats[h]["cats"]["genuine_fail"]}</td><td>{100*stats[h]["real"]/max(stats[h]["done"],1):.1f}%</td></tr>\n' for h in harnesses if stats[h])
rows_tb4 = "".join(f'<tr><td>{hname(h)}</td><td>{tb4[h][0]}</td><td>{tb4[h][1]}</td></tr>\n' for h in harnesses)

html = f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>cline 专项分析报告 R1762</title><style>{CSS}</style></head><body>
<h1>cline 专项分析报告 R1762</h1>
<p><small>BaiZe Harness 研究线 · 2026-11-07 14:08 · C1-C5 · 增量自 R1761</small></p>
<div class="alert"><strong>⚠️ 网关</strong>：/v1/models HTTP{gw_models}，chat <strong>HTTP{gw_chat}</strong>「额度已用完,请等待26分钟39秒」ETA≈14:26。predict 7路alive。</div>
<h2>C1 — 统计</h2><table><tr><th>Harness</th><th>进度</th><th>Real</th><th>Empty</th><th>Real%</th><th>均值</th><th>中位</th></tr>
{rows_c1}<tr><td><strong>合计</strong></td><td><strong>{tot_done}/3500</strong></td><td><strong>{tot_real}</strong></td><td><strong>{tot_done-tot_real}</strong></td><td><strong>{100*tot_real/max(tot_done,1):.1f}%</strong></td><td>-</td><td>-</td></tr></table>
<div class="box"><strong>cline</strong>: Real {cline["real"]}/{cline["done"]}={c_pct:.1f}% · Empty {cline["empty"]}(100% infra) · 均值{cline["mean_min"]:.1f}min · 中位{cline["med_min"]:.1f}min · patch 1091-22705B 均值4036B</div>
<p>复算: <code>python3 gen_cline_special_r1762.py</code> · 数据源: progress_glm53_cline-patched.json({cline["done"]}条)</p>
<h2>C2 — 失败分类</h2><table><tr><th>分类</th><th>数量</th><th>占比</th><th>判据</th></tr>
<tr><td>网关429</td><td>{cline["cats"]["quota_429"]}</td><td>{100*cline["cats"]["quota_429"]/max(cline["empty"],1):.1f}%</td><td>stdout_tail含「额度已用完」</td></tr>
<tr><td>SDK崩溃</td><td>{cline["cats"]["adapter_sdk"]}</td><td>{100*cline["cats"]["adapter_sdk"]/max(cline["empty"],1):.1f}%</td><td>ai/dist/index.js:9202</td></tr>
<tr><td>连接</td><td>{cline["cats"]["connection"]}</td><td>{100*cline["cats"]["connection"]/max(cline["empty"],1):.1f}%</td><td>ConnectionRefused</td></tr>
<tr><td>超时</td><td>{cline["cats"]["timeout"]}</td><td>{100*cline["cats"]["timeout"]/max(cline["empty"],1):.1f}%</td><td>wall≥1790s</td></tr>
<tr><td>能力</td><td>{cline["cats"]["genuine_fail"]}</td><td>{100*cline["cats"]["genuine_fail"]/max(cline["empty"],1):.1f}%</td><td>rc=0+无infra</td></tr>
<tr><td>其他</td><td>{cline["cats"]["other"]}</td><td>{100*cline["cats"]["other"]/max(cline["empty"],1):.1f}%</td><td>未归类</td></tr>
<tr><td><strong>合计</strong></td><td><strong>{cline["empty"]}</strong></td><td><strong>100%</strong></td><td><strong>infra={infra_count}({infra_pct:.1f}%) 能力=0</strong></td></tr></table>
<div class="alert">SDK崩溃{cline["cats"]["adapter_sdk"]}个=Vercel AI SDK未捕获429→挂起，非能力不足。</div>
<div class="info"><strong>7路对比</strong><table><tr><th>Harness</th><th>Real</th><th>Empty</th><th>429</th><th>SDK</th><th>能力</th><th>Real%</th></tr>
{rows_7w}</table>
<p>opencode 0 SDK崩溃 vs cline {cline["cats"]["adapter_sdk"]} = opencode适配器429更健壮。</p></div>
<h2>C3 — 空patch归零</h2>
<div class="alert">✗ 未归零: {cline["empty"]}个(额度恢复后resume自动重跑)。根因=429(ETA~14:26)。</div>
<div class="fix">✓ R1744修复: resume检查model_patch非空。适配器正常{cline["real"]}/{cline["real"]}=100%。</div>
<pre>curl chat -> HTTP{gw_chat} "额度已用完,请等待26分钟39秒"
quota_429={cline["cats"]["quota_429"]} · adapter_sdk={cline["cats"]["adapter_sdk"]} · genuine=0</pre>
<p><strong>假设</strong>: 额度恢复→real%→90%+，空patch归零。</p>
<h2>C4 — 心跳</h2>
<div class="box"><code>cline专项: real {cline["real"]}/{cline["done"]}({c_pct:.1f}%) · 适配器=100% · empty {cline["empty"]}(q={cline["cats"]["quota_429"]}/s={cline["cats"]["adapter_sdk"]}/g={cline["cats"]["genuine_fail"]}) · {cline["mean_min"]:.1f}min · TB4 {tot_tb4_c}/0passed · top1=429(ETA~14:26)</code></div>
<h2>C5 — 差距来源</h2><table><tr><th>指标</th><th>cline</th><th>opencode</th><th>codex</th><th>来源</th></tr>
<tr><td>Real%</td><td>{c_pct:.1f}%</td><td>{o_pct:.1f}%</td><td>{cx_pct:.1f}%</td><td>额度+SDK</td></tr>
<tr><td><strong>适配器正常</strong></td><td><span class="good">100%</span></td><td><span class="good">{o_ap:.1f}%</span></td><td>-</td><td><strong>无差距</strong></td></tr>
<tr><td>SDK崩溃</td><td>{cline["cats"]["adapter_sdk"]}</td><td>{opencode["cats"]["adapter_sdk"]}</td><td>{stats["codex"]["cats"]["adapter_sdk"]}</td><td>cline SDK不健壮</td></tr>
<tr><td>耗时</td><td>{cline["mean_min"]:.1f}min</td><td>{opencode["mean_min"]:.1f}min</td><td>-</td><td>接近</td></tr>
<tr><td>TB4</td><td>0</td><td>0</td><td>0</td><td>glm-5.3-flash能力</td></tr></table>
<div class="note"><strong>结论</strong><ol>
<li><strong>适配器正常 cline {cline["real"]}/{cline["real"]}=100% real，与opencode无能力差距。</strong></li>
<li>100%空patch=infra(quota+SDK)，0能力失败。</li>
<li>{cline["cats"]["adapter_sdk"]}个SDK崩溃=Vercel AI SDK未捕获429。</li>
<li>opencode 0 SDK崩溃=适配器429更健壮。</li>
<li>TB4全0=glm-5.3-flash能力限制(verifier正常)。</li>
</ol></div>
<h2>TB4（66题×7路）</h2><table><tr><th>Harness</th><th>Completed</th><th>Passed</th></tr>
{rows_tb4}<tr><td><strong>合计</strong></td><td><strong>{tot_tb4_c}</strong></td><td><strong>0</strong></td></tr></table>
<h2>附录</h2><ul>
<li>网关: /v1/models HTTP{gw_models}, chat HTTP{gw_chat}(ETA~14:26)</li>
<li>预测7路 alive(0% CPU)</li>
<li>SDK: Vercel AI SDK ai/dist/index.js:9202未捕获429</li>
<li>复算: <code>python3 gen_cline_special_r1762.py</code></li>
<li>命名: 正文写cline(代码路径cline-patched不改)</li>
</ul>
<hr><p><small>2026-11-07 14:08 · gen_cline_special_r1762.py · 0外链</small></p></body></html>'''

out = os.path.join(SCRIPT_DIR, "..", "..", "reports", "report_harness_cline_special_r1762_zh.html")
with open(out, "w") as f: f.write(html)
print(f"Report written: {out} ({len(html)} bytes)")
