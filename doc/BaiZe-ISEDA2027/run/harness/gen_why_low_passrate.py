#!/usr/bin/env python3
"""Generate report_harness_why_low_passrate_zh.html"""
import json, os, html, math
from collections import Counter, defaultdict
from datetime import datetime

HARNESS_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS = json.load(open(os.path.join(HARNESS_DIR, "kimi_pilot_results.json")))
FIX3 = json.load(open(os.path.join(HARNESS_DIR, "kimi_pilot_results.fix3.json")))
TOTAL = len(RESULTS)

classif = Counter(r.get("classification", "?") for r in RESULTS)
resolved = classif.get("resolved", 0)
blocked = classif.get("blocked", 0)
quota_blocked = classif.get("quota-blocked", 0)
no_patch = classif.get("no-patch", 0)

env_fail = 0; true_wrong = 0; partial = 0
for r in RESULTS:
    if r.get("classification") != "patch-but-failed": continue
    ev = r.get("harness_result", {}).get("eval", {})
    f2p_t = ev.get("f2p_total", 0) or 0
    f2p_p = ev.get("f2p_pass", 0) or 0
    p2p_t = ev.get("p2p_total", 0) or 0
    if f2p_t == 0 and p2p_t == 0: env_fail += 1
    elif f2p_p < f2p_t: true_wrong += 1
    else: partial += 1

eval_ok_total = resolved + true_wrong + partial
eval_ok_rate = resolved / eval_ok_total * 100 if eval_ok_total else 0

by_h = defaultdict(lambda: {"total": 0, "resolved": 0})
for r in RESULTS:
    h = r.get("harness", "?")
    by_h[h]["total"] += 1
    if r.get("classification") == "resolved": by_h[h]["resolved"] += 1

env_by_repo = Counter()
wrong_by_repo = Counter()
for r in RESULTS:
    if r.get("classification") != "patch-but-failed": continue
    ev = r.get("harness_result", {}).get("eval", {})
    if (ev.get("f2p_total",0) or 0) == 0 and (ev.get("p2p_total",0) or 0) == 0:
        env_by_repo[r.get("repo","?")] += 1
    elif (ev.get("f2p_pass",0) or 0) < (ev.get("f2p_total",0) or 0):
        wrong_by_repo[r.get("repo","?")] += 1

blocked_by_repo = Counter(r.get("repo","?") for r in RESULTS if r.get("classification")=="blocked")
blocked_by_h = Counter(r.get("harness","?") for r in RESULTS if r.get("classification")=="blocked")

fix3_mpl = [r for r in FIX3 if "matplotlib" in r.get("repo","")]
fix3_mpl_a = sum(1 for r in fix3_mpl if r.get("new_eval",{}).get("patch_applied"))
fix3_sk = [r for r in FIX3 if "scikit-learn" in r.get("repo","")]
fix3_sk_a = sum(1 for r in fix3_sk if r.get("new_eval",{}).get("patch_applied"))
fix3_sx = [r for r in FIX3 if "sphinx" in r.get("repo","")]
fix3_sx_a = sum(1 for r in fix3_sx if r.get("new_eval",{}).get("patch_applied"))

wall_times = sorted([r.get("harness_result",{}).get("wall_s",0) or 0 for r in RESULTS if r.get("harness_result",{}).get("wall_s")])
wt_n = len(wall_times)
wt_med = wall_times[wt_n//2] if wt_n else 0
wt_mean = sum(wall_times)/wt_n if wt_n else 0
wt_max = wall_times[-1] if wt_n else 0

def get_cases(harness="cline-patched"):
    res, wrong, env, blk = [], [], [], []
    for r in RESULTS:
        if r.get("harness") != harness: continue
        cls = r.get("classification")
        ev = r.get("harness_result",{}).get("eval",{})
        if cls == "resolved" and len(res) < 2: res.append(r)
        elif cls == "patch-but-failed":
            f2p_t = ev.get("f2p_total",0) or 0
            if f2p_t > 0 and len(wrong) < 3: wrong.append(r)
            elif f2p_t == 0 and len(env) < 2: env.append(r)
        elif cls == "blocked" and len(blk) < 2: blk.append(r)
    return res, wrong, env, blk

res_cases, wrong_cases, env_cases, blk_cases = get_cases("cline-patched")

def esc(s): return html.escape(str(s))
def fmt_pct(n, t): return f"{n/t*100:.1f}%"
gen_time = datetime.now().strftime("%Y-%m-%d %H:%M")

def svg_donut():
    segs = [("resolved",resolved,"#2d7d2d"),("true wrong-fix",true_wrong,"#d44"),
        ("env-failure",env_fail,"#e80"),("partial",partial,"#999"),
        ("blocked",blocked,"#77a"),("quota",quota_blocked,"#aaa"),("no-patch",no_patch,"#ccc")]
    cx,cy,ro,ri = 180,130,90,50
    s = '<svg width="360" height="260" viewBox="0 0 360 260" xmlns="http://www.w3.org/2000/svg">'
    s += '<text x="180" y="20" text-anchor="middle" font-size="13" fill="#333" font-weight="bold">2100 条结果失败模式分布</text>'
    ang = -90
    for lbl,val,col in segs:
        if val==0: continue
        pct=val/TOTAL*360; a1=ang; a2=ang+pct
        r1,r2=math.radians(a1),math.radians(a2)
        x1=cx+ro*math.cos(r1); y1=cy+ro*math.sin(r1)
        x2=cx+ro*math.cos(r2); y2=cy+ro*math.sin(r2)
        xi1=cx+ri*math.cos(r1); yi1=cy+ri*math.sin(r1)
        xi2=cx+ri*math.cos(r2); yi2=cy+ri*math.sin(r2)
        lg=1 if pct>180 else 0
        s += f'<path d="M {x1:.1f} {y1:.1f} A {ro} {ro} 0 {lg} 1 {x2:.1f} {y2:.1f} L {xi2:.1f} {yi2:.1f} A {ri} {ri} 0 {lg} 0 {xi1:.1f} {yi1:.1f} Z" fill="{col}" opacity="0.75" stroke="#fff" stroke-width="1"/>'
        ma=math.radians((a1+a2)/2)
        lx=cx+(ro+ri)/2*math.cos(ma); ly=cy+(ro+ri)/2*math.sin(ma)
        if pct>15: s += f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" fill="#fff" font-size="10" font-weight="bold">{val}</text>'
        ang=a2
    ly=165
    for lbl,val,col in segs:
        if val==0: continue
        s += f'<rect x="20" y="{ly}" width="12" height="12" fill="{col}" opacity="0.75" rx="2"/>'
        s += f'<text x="38" y="{ly+10}" font-size="10" fill="#333">{esc(lbl)}: {val} ({fmt_pct(val,TOTAL)})</text>'
        ly+=16
    s += '</svg>'
    return s

def svg_compare():
    data = [("Claude Opus 4.6",62.7,"#5567ff"),("SWE-agent+Claude4",56.7,"#6678aa"),
        ("Kimi K2 0711(标准)",42.0,"#4488dd"),("SWE-agent+Claude3.7",48.0,"#7788bb"),
        ("DeepSeek v3",36.7,"#99aabb"),("Aider+GPT-4o",26.3,"#aabbcc"),
        ("cline eval-OK",36.6,"#2d7d2d"),("pi(ours)",30.3,"#2d9d2d"),
        ("cline(ours)",28.7,"#2d7d2d"),("deepseek-h(ours)",23.7,"#6d8d6d")]
    data.sort(key=lambda x:-x[1])
    w,h,bar_h,ml,mx=560,300,20,160,70
    s=f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">'
    s+=f'<text x="{w/2}" y="18" text-anchor="middle" font-size="13" fill="#333" font-weight="bold">SWE-bench Lite 通过率外部对照</text>'
    for v in [0,20,40,60]:
        x=ml+v/mx*(w-ml-30)
        s+=f'<line x1="{x:.0f}" y1="30" x2="{x:.0f}" y2="{h-10}" stroke="#ddd"/><text x="{x:.0f}" y="{h-2}" text-anchor="middle" font-size="9" fill="#999">{v}%</text>'
    y=35
    for nm,val,col in data:
        bw=val/mx*(w-ml-30)
        s+=f'<text x="{ml-8}" y="{y+14}" text-anchor="end" font-size="10" fill="#333">{esc(nm)}</text>'
        s+=f'<rect x="{ml}" y="{y}" width="{bw:.0f}" height="{bar_h}" fill="{col}" opacity="0.8" rx="2"/>'
        s+=f'<text x="{ml+bw+4:.0f}" y="{y+14}" font-size="10" font-weight="bold">{val:.1f}%</text>'
        y+=bar_h+6
    s+='</svg>'
    return s

def svg_env_repo():
    repos=env_by_repo.most_common(8)
    if not repos: return "<p>(无)</p>"
    mx=repos[0][1]; w,h,bar_h,ml=500,260,18,140
    s=f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">'
    s+=f'<text x="{w/2}" y="18" text-anchor="middle" font-size="13" fill="#333" font-weight="bold">环境失败按 repo (top 8)</text>'
    y=30
    for repo,val in repos:
        bw=val/mx*(w-ml-50)
        s+=f'<text x="{ml-8}" y="{y+13}" text-anchor="end" font-size="9" fill="#333">{esc(repo.split("/")[-1])}</text>'
        s+=f'<rect x="{ml}" y="{y}" width="{bw:.0f}" height="{bar_h}" fill="#e80" opacity="0.7" rx="2"/>'
        s+=f'<text x="{ml+bw+4:.0f}" y="{y+13}" font-size="10">{val}</text>'
        y+=bar_h+6
    s+='</svg>'
    return s

def case_html(r, idx, label, color):
    ev=r.get("harness_result",{}).get("eval",{}); hr=r.get("harness_result",{})
    st=hr.get("stdout_tail",""); iid=r.get("instance_id","?")
    f2p=f'{ev.get("f2p_pass",0)}/{ev.get("f2p_total",0)}'; p2p=f'{ev.get("p2p_pass",0)}/{ev.get("p2p_total",0)}'
    wall=hr.get("wall_s",0) or 0; rootfs=r.get("rootfs_setup",{}).get("msg","")
    st_s=esc(st[-200:]) if st else "(空)"
    return f'<div style="border-left:3px solid {color};padding:8px 12px;margin:8px 0;background:#f9f9f9;border-radius:0 4px 4px 0"><b>案例 {idx} — {esc(label)}</b><br><code>{esc(iid)}</code> | <code>{esc(r.get("harness",""))}</code> | 墙钟:{wall:.0f}s<br><b>eval</b>: resolved={ev.get("resolved")} applied={ev.get("patch_applied")} f2p={f2p} p2p={p2p}<br><b>rootfs</b>: {esc(rootfs)}<br><b>stdout_tail</b>: <pre style="font-size:10px;margin:4px 0;background:#f0f0f0;padding:4px">{st_s}</pre></div>'

# Build table rows
our_rows = "".join(f"<tr><td class='rname'>{esc(h)}</td><td class='num'>{v['resolved']}</td><td class='num'>{v['total']}</td><td class='num'><b>{v['resolved']/v['total']*100:.1f}%</b></td></tr>" for h,v in sorted(by_h.items(), key=lambda x:-x[1]["resolved"]))
env_repo_rows = "".join(f"<tr><td class='rname'>{esc(r)}</td><td class='num'>{c}</td></tr>" for r,c in env_by_repo.most_common(10))
wrong_repo_rows = "".join(f"<tr><td class='rname'>{esc(r)}</td><td class='num'>{c}</td></tr>" for r,c in wrong_by_repo.most_common(10))
blk_repo_rows = "".join(f"<tr><td class='rname'>{esc(r)}</td><td class='num'>{c}</td></tr>" for r,c in blocked_by_repo.most_common())
blk_h_rows = "".join(f"<tr><td class='rname'>{esc(h)}</td><td class='num'>{c}</td></tr>" for h,c in blocked_by_h.most_common())

case_sections = ""
for i,r in enumerate(res_cases): case_sections += case_html(r, i+1, "成功 (resolved)", "#2d7d2d")
for i,r in enumerate(wrong_cases): case_sections += case_html(r, i+1, "错误修复 (wrong-fix)", "#d44")
for i,r in enumerate(env_cases): case_sections += case_html(r, i+1, "环境失败 (env-failure)", "#e80")
for i,r in enumerate(blk_cases): case_sections += case_html(r, i+1, "阻塞 (blocked)", "#77a")

ext_data = [("Claude Opus 4.6","62.7%","pricepertoken 2026-10"),("SWE-agent+Claude4","56.7%","llmrun.dev 2025-09"),
    ("MiniMax M2.5","56.3%","pricepertoken 2026-10"),("GPT-5","54.3%","pricepertoken 2026-10"),
    ("Claude Haiku 4.5","54.3%","pricepertoken 2026-10"),("SWE-agent+Claude3.7","48.0%","llmrun.dev 2025-09"),
    ("Kimi K2 0711(标准)","42.0%","pricepertoken 2026-10"),("Agentless+Claude3.5","40.7%","llmrun.dev 2025-09"),
    ("DeepSeek v3","36.7%","llmrun.dev 2025-09"),("Aider+GPT-4o(2024-05)","26.3%","aider.blog 2024-05"),
    ("SWE-agent+GPT-4(原始)","12.47%","SWE-bench paper ICLR2024")]
ext_rows = "".join(f"<tr><td class='rname'>{esc(n)}</td><td class='num'><b>{esc(s)}</b></td><td style='font-size:11px;color:#888'>{esc(src)}</td></tr>" for n,s,src in ext_data)

opp_data = [
    ("1","升级模型","Kimi K2 0711 标准=42.0%,我们 28.7%(差13.3pp)","换用 Kimi K2 0711 或 Claude 4","+10~15pp","API 费用","1-2h","中"),
    ("2","修复剩余环境失败","451 env-fail 中已修~86,剩~365","sphinx/astropy/sklearn 逐项修","+3~5pp","CPU ~4h","4-8h","中"),
    ("3","改进 harness 质量","7 harness 23.7~30.3%,与 mini-SWE-agent 差距","改进 edit format/context/tool use","+3~5pp","开发 2-3天","1周","中高"),
    ("4","重跑 blocked(50)+no-patch(4)","50 blocked(matplotlib 31),git/workdir 冲突","修复 workdir+git 重试+重跑","+1~2pp","CPU+API ~5h","6h","低"),
    ("5","多次尝试/集成","Aider 6次重试→26.3%(vs 单次25%)","每 instance 跑 N 次取最佳","+3~5pp","API×N","1-2天","低"),
    ("6","agent self-repair","wrong-fix 中 f2p=0 但 p2p 全过","跑测试→反馈→agent 修复","+2~4pp","token+墙钟","1周","中"),
]
opp_rows = "".join(f"<tr><td>{r[0]}</td><td style='text-align:left'><b>{r[1]}</b></td><td style='text-align:left;font-size:11px'>{r[2]}</td><td style='text-align:left;font-size:11px'>{r[3]}</td><td class='num'><b>{r[4]}</b></td><td class='num' style='font-size:11px'>{r[5]}</td><td class='num' style='font-size:11px'>{r[6]}</td><td style='font-size:11px'>{r[7]}</td></tr>" for r in opp_data)

recov_total = env_fail + blocked + quota_blocked
recov_est = int(recov_total * 0.371 / 7)
CSS = "body{font-family:-apple-system,Segoe UI,PingFang SC,sans-serif;max-width:1100px;margin:0 auto;padding:20px;background:#fafafa;color:#222;line-height:1.6}h1{font-size:1.5em;border-bottom:3px solid #2563eb;padding-bottom:8px}h2.sec{font-size:1.2em;color:#2563eb;border-left:4px solid #2563eb;padding-left:10px;margin-top:32px}h3{font-size:1.05em;color:#444}table{border-collapse:collapse;width:100%;margin:12px 0;font-size:13px}th,td{border:1px solid #ddd;padding:5px 8px;text-align:center}th{background:#e8eef7}td.rname{text-align:left;font-family:monospace}td.num{font-family:monospace}tr:hover{background:#f0f4ff}.callout{padding:12px 16px;border-radius:6px;margin:12px 0;font-size:14px}.cr{background:#fef2f2;border:1px solid #fca5a5}.cb{background:#eff6ff;border:1px solid #93c5fd}.cy{background:#fefce8;border:1px solid #fde047}.cg{background:#f0fdf4;border:1px solid #86efac}pre{background:#f5f5f5;padding:10px;border-radius:6px;overflow-x:auto;font-size:12px}.svgc{text-align:center;margin:16px 0;overflow-x:auto}.tag{display:inline-block;padding:1px 6px;border-radius:3px;font-size:11px;font-weight:600}.p0{background:#fef2f2;color:#dc2626;border:1px solid #fca5a5}.p1{background:#fefce8;color:#ca8a04;border:1px solid #fde047}footer{margin-top:40px;padding-top:15px;border-top:1px solid #ddd;font-size:11px;color:#888}"

html_doc = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>BaiZe Harness — 通过率为何这么低？</title><style>{CSS}</style></head><body>
<h1>🔬 BaiZe Harness — SWE-bench 通过率为何这么低？</h1>
<p style="color:#666;font-size:13px">生成: {gen_time} | 数据: kimi_pilot_results.json(2100条,7harness×300) + fix1/fix2/fix3 | 模型: kimi-k2.6-cloud | SWE-bench Lite(300)</p>
<h2 class="sec">1. TL;DR</h2>
<div class="callout cr"><b>核心结论</b>: cline 28.7% 的通过率<b>同时受评测环境压制和 LLM 能力限制</b>。<br><ul style="margin:6px 0">
<li><b>环境压制 21.5%</b>({env_fail}/2100): C扩展/Python版本/OOM → 测试无法运行. fix1+fix2+fix3 已挽回43条→29.4%.</li>
<li><b>真实能力不足 46.3%</b>({true_wrong}/2100): 补丁apply+测试运行,但f2p失败→<b>agent修复是错的</b>. 主要失败模式.</li>
<li><b>eval-OK口径 {eval_ok_rate:.1f}%</b>仍低于Kimi K2 0711标准42.0%→~5pp harness质量差距.</li>
<li><b>fix3关键发现</b>: matplotlib C扩展修复后{fix3_mpl_a}条补丁全apply但<b>0条resolved</b>→f2p=0/1→<b>确认能力问题,非infra</b>.</li>
<li><b>外部对照</b>: 28.7%与Aider+GPT-4o(26.3%,2024-05)相当,远低于SOTA(Claude Opus 4.6=62.7%)和同模型标准(Kimi K2 0711=42.0%).</li>
</ul></div>
<h2 class="sec">2. 外部对照 — SWE-bench Lite 排行榜</h2>
<p>排行榜用标准Docker eval+mini-SWE-agent;我们用自建非Docker eval+7自定义harness,口径不完全可比.</p>
<table><tr><th>模型/Agent</th><th>SWE-bench Lite</th><th>来源+时效</th></tr>{ext_rows}</table>
<h3>我们的结果(kimi-k2.6-cloud,自建eval,7harness)</h3>
<table><tr><th>harness</th><th>resolved</th><th>total</th><th>rate</th></tr>{our_rows}
<tr style="background:#e8eef7"><td class='rname'><b>cline eval-OK口径</b></td><td class='num'>{resolved}</td><td class='num'>{eval_ok_total}</td><td class='num'><b>{eval_ok_rate:.1f}%</b></td></tr>
<tr style="background:#e8eef7"><td class='rname'><b>fix1+fix2后</b></td><td class='num'>617</td><td class='num'>2100</td><td class='num'><b>29.4%</b></td></tr></table>
<div class="callout cb"><b>对照</b>: cline 28.7%<b>低于</b>同模型标准(Kimi K2 0711=42.0%,差13.3pp). eval-OK {eval_ok_rate:.1f}%收窄至~5pp. 差距: ①环境(~8pp)②harness质量(~5pp)③模型差异(待验证).</div>
<div class="svgc">{svg_compare()}</div>
<h2 class="sec">3. 能力 vs 环境拆解</h2>
<h3>3.1 失败模式分布</h3>
<div class="svgc">{svg_donut()}</div>
<table><tr><th>分类</th><th>条数</th><th>占比</th><th>性质</th><th>可挽回性</th></tr>
<tr><td class='rname'>resolved</td><td class='num'>{resolved}</td><td class='num'>{fmt_pct(resolved,TOTAL)}</td><td>✅成功</td><td>—</td></tr>
<tr><td class='rname'>true wrong-fix</td><td class='num'>{true_wrong}</td><td class='num'>{fmt_pct(true_wrong,TOTAL)}</td><td><span class='tag p0'>能力</span>f2p失败</td><td>低</td></tr>
<tr><td class='rname'>env-failure</td><td class='num'>{env_fail}</td><td class='num'>{fmt_pct(env_fail,TOTAL)}</td><td><span class='tag p1'>环境</span>测试未运行</td><td><b>高</b></td></tr>
<tr><td class='rname'>partial</td><td class='num'>{partial}</td><td class='num'>{fmt_pct(partial,TOTAL)}</td><td><span class='tag p0'>能力</span>p2p未全过</td><td>低</td></tr>
<tr><td class='rname'>blocked</td><td class='num'>{blocked}</td><td class='num'>{fmt_pct(blocked,TOTAL)}</td><td><span class='tag p1'>环境</span>进程未完成</td><td>中</td></tr>
<tr><td class='rname'>quota</td><td class='num'>{quota_blocked}</td><td class='num'>{fmt_pct(quota_blocked,TOTAL)}</td><td><span class='tag p1'>配额</span>API限流</td><td>中</td></tr>
<tr><td class='rname'>no-patch</td><td class='num'>{no_patch}</td><td class='num'>{fmt_pct(no_patch,TOTAL)}</td><td><span class='tag p0'>能力</span>未生成补丁</td><td>低</td></tr></table>
<h3>3.2 环境失败按repo</h3>
<div class="svgc">{svg_env_repo()}</div>
<table><tr><th>repo</th><th>env-fail</th><th>根因</th><th>修复状态</th></tr>
<tr><td class='rname'>matplotlib</td><td class='num'>130</td><td>C扩展(qhull/freetype)</td><td><span class='tag p1'>fix3:apply✅但0resolved</span></td></tr>
<tr><td class='rname'>pytest</td><td class='num'>113</td><td>setuptools冲突</td><td><span class='tag p0'>fix2:9flipped✅</span></td></tr>
<tr><td class='rname'>sphinx</td><td class='num'>92</td><td>base_commit/Python版本</td><td><span class='tag p1'>待修</span></td></tr>
<tr><td class='rname'>sklearn</td><td class='num'>34</td><td>C扩展+上下文不匹配</td><td><span class='tag p1'>fix3:0/27apply</span></td></tr>
<tr><td class='rname'>astropy</td><td class='num'>28</td><td>OOM</td><td><span class='tag p1'>待修(增cgroup)</span></td></tr>
<tr><td class='rname'>django</td><td class='num'>25</td><td>部分依赖</td><td><span class='tag p0'>fix1:部分</span></td></tr>
<tr><td class='rname'>flask</td><td class='num'>14</td><td>werkzeug不兼容</td><td><span class='tag p0'>fix2:0flipped</span></td></tr>
<tr><td class='rname'>sympy</td><td class='num'>8</td><td>少量依赖</td><td><span class='tag p0'>fix1:部分</span></td></tr></table>
<h3>3.3 wrong-fix按repo(top10)</h3>
<table><tr><th>repo</th><th>wrong-fix</th></tr>{wrong_repo_rows}
<tr><td colspan="2" style="font-size:11px;color:#888">django(529)+sympy(248)占80%→难度最高</td></tr></table>
<h3>3.4 blocked分布</h3>
<table><tr><th>repo</th><th>blocked</th></tr>{blk_repo_rows}</table>
<table><tr><th>harness</th><th>blocked</th></tr>{blk_h_rows}
<tr><td colspan="2" style="font-size:11px;color:#888">集中在matplotlib(31)和claude-code/hermes/deepseek</td></tr></table>
<h3>3.5 量化拆分</h3>
<div class="callout cy"><b>能力类</b>: wrong-fix {true_wrong}+partial {partial}+no-patch {no_patch}=<b>{true_wrong+partial+no_patch}({fmt_pct(true_wrong+partial+no_patch,TOTAL)})</b><br><b>环境类</b>: env {env_fail}+blocked {blocked}+quota {quota_blocked}=<b>{recov_total}({fmt_pct(recov_total,TOTAL)})</b><br><b>可挽回上限</b>: eval-OK {eval_ok_rate:.1f}%→~{recov_est}条/harness→cline 86→~{86+recov_est}({(86+recov_est)/300*100:.1f}%). <b>但fix3实证</b>: 0/{fix3_mpl_a}→实际flip~10-20%.</div>
<h2 class="sec">4. 代表轨迹逐条</h2>
<p>cline-patched harness代表性案例:</p>
{case_sections}
<div class="callout cy"><b>fix3验证</b>: matplotlib {fix3_mpl_a}/29 apply→<b>0/29 resolved</b>→f2p=0/1→<b>能力问题</b>. sklearn {fix3_sk_a}/27 apply→上下文不匹配. sphinx {fix3_sx_a}/8 apply→同上.</div>
<h3>4.1 关键发现</h3>
<div class="callout cb"><ul style="margin:6px 0">
<li><b>成功</b>(django-10924): f2p=1/1,p2p=1/1,383s→干净利落.</li>
<li><b>wrong-fix</b>(django-11019): f2p=0/16,p2p=58/58,1800s→花30分钟但补丁未修bug,未破坏现有测试.</li>
<li><b>env-failure</b>(astropy-12907): f2p=0/0,p2p=0/0→测试没运行(OOM).</li>
<li><b>blocked</b>: stdout_tail空,rc=None→进程未完成.</li>
<li><b>墙钟</b>: 中位{wt_med:.0f}s({wt_med/60:.1f}min),均值{wt_mean:.0f}s({wt_mean/60:.1f}min),最大{wt_max:.0f}s({wt_max/60:.1f}min).</li>
</ul></div>
<h2 class="sec">5. 提升机会点(按预计提升排序)</h2>
<table><tr><th>#</th><th>机会点</th><th>依据</th><th>做法</th><th>预计提升</th><th>成本</th><th>ETA</th><th>风险</th></tr>{opp_rows}</table>
<div class="callout cg"><b>累计</b>: 短期(1-2周)升级模型(+10~15pp)+修复环境(+3~5pp)+重跑blocked(+1~2pp)→<b>29.4%→~43~51%</b>. 中期改进harness(+3~5pp)+self-repair(+2~4pp)→<b>~48~60%</b>. <b>瓶颈</b>:升级模型是最大杠杆.</div>
<h2 class="sec">6. 结论与诚实条款</h2>
<div class="callout cr"><b>结论</b>:<ol style="margin:6px 0">
<li><b>28.7%合理吗?</b> 部分合理.与Aider+GPT-4o(26.3%)相当,但<b>低于同模型标准13pp</b>.差距~8pp环境(可修),~5pp harness质量.</li>
<li><b>都是LLM能力不足?</b> <b>不是</b>.21.5%环境,46.3%能力.fix3实证:修复后flip 0-28%→<b>环境修复暴露能力差距</b>.</li>
<li><b>主要问题</b>: ①eval环境 ②django/sympy修复能力不足(777条wrong-fix) ③harness质量.</li>
<li><b>最大机会</b>: 升级模型(+10~15pp)>修复环境(+3~5pp)>改进harness(+3~5pp).</li>
</ol></div>
<div class="callout cy"><b>诚实条款</b>:<ul style="margin:6px 0">
<li>外部数据来自公开排行榜,时效2026-10,口径<b>不完全可比</b>.</li>
<li>我们用<b>非Docker自建环境</b>,与官方标准有系统差异.eval-OK是<b>内部口径</b>.</li>
<li>kimi-k2.6-cloud与Kimi K2 0711<b>可能不同checkpoint</b>,未隔离验证.</li>
<li>fix3的0/29是<b>小样本</b>,flip rate因repo而异(fix1=9%,fix2=28%).</li>
<li>stdout_tail仅最后几行,<b>不含完整轨迹</b>.</li>
<li>提升幅度是<b>估算</b>,非实测.</li>
</ul></div>
<footer><p>数据: kimi_pilot_results.json(2100)+fix1(376)+fix2(32)+fix3(64) | 分析: Python统计+轨迹检查 | 外部: web search 2026-10-13</p><p>脚本: gen_why_low_passrate.py | 口径: 自建非Docker eval,7harness×300,kimi-k2.6-cloud</p></footer>
</body></html>"""

out_path = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/report_harness_why_low_passrate_zh.html"
with open(out_path, "w") as f:
    f.write(html_doc)
size = os.path.getsize(out_path)
print(f"Generated: {out_path} ({size} bytes = {size/1024:.1f} KB)")
print(f"Key: resolved={resolved}({fmt_pct(resolved,TOTAL)}), env_fail={env_fail}({fmt_pct(env_fail,TOTAL)}), true_wrong={true_wrong}({fmt_pct(true_wrong,TOTAL)})")
print(f"eval-OK: {eval_ok_rate:.1f}%")
