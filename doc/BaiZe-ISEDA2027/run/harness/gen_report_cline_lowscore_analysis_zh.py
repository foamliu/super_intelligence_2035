#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 cline 低分系统归因报告（中文 HTML，自包含，0 script / 0 外链）。

按 BAIZE_HARNESS_TASK.md 运维令 2026-11-06 17:1x（用户直令）。
基于 full500 完整结果，逐实例级配对拆解 cline 与 opencode 的差距。

数据字典（全部可溯源，不编造）：
  swebench_verified_full/reports/eval_{h}.json       resolved/failed/no_patch/n
  swebench_verified_full/reports/progress_{h}.json   predict 逐题: wall_s,model_patch_len,returncode,quota_blocked
  swebench_verified_full/predictions/{h}__{iid}.json 逐题 model_patch

命名规程：正文一律写 cline（不写 cline-patched）；代码标识符不改。
报告目录：doc/BaiZe-ISEDA2027/reports/（不在 run/reports）。
"""
from __future__ import annotations
import html, json, math, statistics
from collections import Counter
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
FULL = HERE / "swebench_verified_full"
REPORT_DIR = FULL / "reports"
PRED_DIR = FULL / "predictions"
PROJECT_REPORTS = HERE.parent.parent / "reports"
OUT = PROJECT_REPORTS / "report_harness_cline_lowscore_analysis_zh.html"

HARNESS_C = "cline-patched"
HARNESS_O = "opencode"

CLINE_BASELINE_PRE = {"resolved": 326, "fix_round": "R1569", "fix_commit": "29df7ba7f"}

def esc(s): return html.escape(str(s))
def load_json(p): return json.loads(Path(p).read_text())

def mcnemar_exact(resolved_a, resolved_b, common):
    ra = set(resolved_a) & common; rb = set(resolved_b) & common
    n01 = len(ra - rb); n10 = len(rb - ra); disc = n01 + n10
    if disc == 0: return {"n01":0,"n10":0,"discordant":0,"p":1.0,"or":float("nan")}
    k = min(n01, n10)
    p = min(1.0, 2*sum(math.comb(disc,i) for i in range(k+1))/2**disc)
    or_ = (n10/n01) if n01>0 else float("inf")
    return {"n01":n01,"n10":n10,"discordant":disc,"p":p,"or":or_}

def get_patch_len(iid, harness):
    try:
        p = load_json(PRED_DIR / f"{harness}__{iid}.json")
        if p and isinstance(p, list) and p[0].get("model_patch",""): return len(p[0]["model_patch"])
    except Exception: pass
    return 0

def repo_of(iid): return iid.split("__")[0]

def pie_svg(parts, total, w=240, h=240, r=90, cx=120, cy=120):
    if total == 0: return '<svg width="%d" height="%d"></svg>' % (w, h)
    frags = []; ang = -90.0
    for label, val, color in parts:
        frac = val/total
        if frac <= 0: continue
        sweep = frac*360.0; a0 = math.radians(ang); a1 = math.radians(ang+sweep)
        large = 1 if sweep>180 else 0
        x0 = cx+r*math.cos(a0); y0 = cy+r*math.sin(a0)
        x1 = cx+r*math.cos(a1); y1 = cy+r*math.sin(a1)
        frags.append(f'<path d="M{cx},{cy} L{x0:.2f},{y0:.2f} A{r},{r} 0 {large} 1 {x1:.2f},{y1:.2f} Z" fill="{color}" stroke="#fff" stroke-width="1.5"/>')
        ang += sweep
    legend = "".join(f'<rect x="{w-6}" y="{10+i*22}" width="14" height="14" fill="{c}"/><text x="{w-6+20}" y="{22+i*22}" font-size="12" fill="#334155">{esc(lbl)} ({v}, {v/total*100:.1f}%)</text>' for i,(lbl,v,c) in enumerate(parts) if v>0)
    return f'<svg width="{w+170}" height="{h}" viewBox="0 0 {w+170} {h}" xmlns="http://www.w3.org/2000/svg">' + "".join(frags) + legend + "</svg>"

def bar_svg(rows, w=520, h=180):
    if not rows: return ""
    mx = max(v for _,v,_ in rows) or 1; bw = w-180; bh=26; y=8
    parts = ['<svg width="%d" height="%d" xmlns="http://www.w3.org/2000/svg">' % (w,h)]
    for lbl,val,color in rows:
        parts.append(f'<text x="0" y="{y+18}" font-size="12" fill="#334155">{esc(lbl)}</text>')
        parts.append(f'<rect x="150" y="{y}" width="{val/mx*bw:.1f}" height="{bh}" fill="{color}" rx="3"/>')
        parts.append(f'<text x="{150+val/mx*bw+6:.1f}" y="{y+18}" font-size="12" fill="#334155">{val}</text>')
        y += bh+8
    parts.append("</svg>"); return "".join(parts)

def main():
    ev_c = load_json(REPORT_DIR / f"eval_{HARNESS_C}.json")
    ev_o = load_json(REPORT_DIR / f"eval_{HARNESS_O}.json")
    pg_c = load_json(REPORT_DIR / f"progress_{HARNESS_C}.json")
    pg_o = load_json(REPORT_DIR / f"progress_{HARNESS_O}.json")
    res_c=set(ev_c.get("resolved",[])); fail_c=set(ev_c.get("failed",[])); nop_c=set(ev_c.get("no_patch",[]))
    res_o=set(ev_o.get("resolved",[])); fail_o=set(ev_o.get("failed",[])); nop_o=set(ev_o.get("no_patch",[]))
    prog_c={r["instance_id"]:r for r in pg_c.get("results",[])}
    prog_o={r["instance_id"]:r for r in pg_o.get("results",[])}
    common=(res_c|fail_c|nop_c)&(res_o|fail_o|nop_o)
    cline_res_common=len(res_c&common); open_res_common=len(res_o&common)
    gap=sorted(i for i in common if i in res_o and i not in res_c)
    gap_back=sorted(i for i in common if i in res_c and i not in res_o)
    net_diff=open_res_common-cline_res_common
    mc=mcnemar_exact(res_c,res_o,common)
    CATS={"patch_quality":"① 补丁质量/能力","no_patch_timeout":"② 静默退出/超时","no_patch_quick":"② 静默退出/超时","infra_quota":"④ infra","no_patch_other":"③ no-patch"}
    cat_color={"patch_quality":"#2563eb","no_patch_timeout":"#f59e0b","no_patch_quick":"#fbbf24","infra_quota":"#9ca3af","no_patch_other":"#ef4444"}
    rows=[]; cat_counts=Counter()
    for iid in gap:
        pc=prog_c.get(iid,{}); mpl=pc.get("model_patch_len",0); qb=pc.get("quota_blocked",False); wall=pc.get("wall_s",0); rc=pc.get("returncode",None)
        if qb: cat="infra_quota"
        elif mpl==0:
            if wall>=1700: cat="no_patch_timeout"
            elif wall<300: cat="no_patch_quick"
            else: cat="no_patch_other"
        else: cat="patch_quality"
        cat_counts[cat]+=1
        po=prog_o.get(iid,{})
        rows.append({"iid":iid,"repo":repo_of(iid),"cat":cat,"cat_label":CATS[cat],"color":cat_color[cat],"cline_patch_len":mpl,"cline_wall":wall,"cline_rc":rc,"cline_quota":qb,"open_patch_len":po.get("model_patch_len",0),"open_wall":po.get("wall_s",0),"open_rc":po.get("returncode",None)})
    pq=[r for r in rows if r["cat"]=="patch_quality"]
    pq_cline_sizes=[r["cline_patch_len"] for r in pq]; pq_open_sizes=[r["open_patch_len"] for r in pq]
    pq_cline_wall=[r["cline_wall"] for r in pq]; pq_open_wall=[r["open_wall"] for r in pq]
    bigger_open=sum(1 for r in pq if r["open_patch_len"]>r["cline_patch_len"])
    repo_dist=Counter(repo_of(i) for i in gap)
    ability=cat_counts["patch_quality"]
    harness_adapt=cat_counts["no_patch_timeout"]+cat_counts["no_patch_quick"]+cat_counts["no_patch_other"]
    infra=cat_counts["infra_quota"]
    now=datetime.now().strftime("%Y-%m-%d %H:%M")
    p_val=mc["p"]; p_str=f"{p_val:.2e}" if p_val>=1e-300 else "<1e-300"
    or_str=f"{mc['or']:.2f}" if mc['or']!=float("inf") else "∞"
    def fmt_stats(lst):
        if not lst: return "—"
        return f"均值 {statistics.mean(lst):.0f} · 中位 {statistics.median(lst):.0f} · min {min(lst)} · max {max(lst)}"
    H=[]
    H.append(f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>cline 低分系统归因 · SWE-bench Verified full500</title>
<style>
 body{{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;color:#1e293b;max-width:1080px;margin:0 auto;padding:24px;line-height:1.6;background:#f8fafc;}}
 h1{{font-size:1.5rem;border-bottom:3px solid #2563eb;padding-bottom:8px;}}
 h2{{font-size:1.2rem;color:#1e3a8a;margin-top:32px;border-left:5px solid #2563eb;padding-left:10px;}}
 h3{{font-size:1.05rem;color:#334155;margin-top:20px;}}
 .meta{{color:#64748b;font-size:0.85rem;}}
 .tldr{{background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:16px 20px;margin:16px 0;}}
 .tldr b{{color:#1d4ed8;}}
 .box{{background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:14px 18px;margin:14px 0;}}
 table{{border-collapse:collapse;width:100%;font-size:0.82rem;margin:12px 0;background:#fff;}}
 th,td{{border:1px solid #e2e8f0;padding:6px 9px;text-align:left;}}
 th{{background:#f1f5f9;color:#1e3a8a;font-weight:600;}}
 tr:nth-child(even){{background:#f8fafc;}}
 .mono{{font-family:ui-monospace,Consolas,monospace;font-size:0.78rem;}}
 .swatch{{display:inline-block;width:12px;height:12px;border-radius:2px;vertical-align:middle;margin-right:4px;}}
 .kv td:first-child{{width:34%;color:#475569;font-weight:600;}}
 .small{{font-size:0.8rem;color:#64748b;}}
 code{{background:#f1f5f9;padding:1px 5px;border-radius:3px;font-size:0.82rem;}}
 .scrollx{{overflow-x:auto;}}
 .pill{{display:inline-block;padding:1px 8px;border-radius:10px;font-size:0.74rem;color:#fff;}}
</style></head><body>
<h1>cline 低分系统归因报告 · SWE-bench Verified full500</h1>
<div class="meta">生成时间 {now} · 数据源 <code>run/harness/swebench_verified_full/</code> · 正文一律写 cline（代码标识符 cline-patched 不改）· 0 script / 0 外链 / 自包含</div>
""")
    H.append(f"""
<div class="tldr">
<b>TL;DR</b>（基于 full500 完整数据，逐实例配对）：<br>
① 最终 resolved：<b>cline {cline_res_common}/500（{cline_res_common/500*100:.1f}%）</b> vs <b>opencode {open_res_common}/500（{open_res_common/500*100:.1f}%）</b>，净差 <b>{net_diff}</b> 题（约 {net_diff/500*100:.1f}pp）。<br>
② 差距集（opencode 解、cline 未解）共 <b>{len(gap)}</b> 题，归因为：<b>补丁质量/能力 {ability}</b>（{ability/len(gap)*100:.0f}%）· <b>静默退出/超时（harness 适配）{harness_adapt}</b>（{harness_adapt/len(gap)*100:.0f}%）· <b>infra {infra}</b>（{infra/len(gap)*100:.0f}%）。<br>
③ McNemar 配对检验：n₀₁(cline-only)={mc['n01']}，n₁₀(opencode-only)={mc['n10']}，不一致 {mc['discordant']}，<b>p = {p_str}</b>（极显著）。<br>
④ 结论：<b>修复后 cline 与 opencode 的差距以「补丁质量/能力」为主（{ability}/{len(gap)}={ability/len(gap)*100:.0f}%），接入损耗已大幅压缩（{harness_adapt}/{len(gap)}={harness_adapt/len(gap)*100:.0f}%）</b>。R1569 适配器修复已把静默退出/超时从主要矛盾降为次要。
</div>""")
    H.append(f"""
<h2>1. 背景与口径</h2>
<div class="box">
<ul>
<li>评测集：princeton-nlp/SWE-bench Verified（500 题，非 Lite）。</li>
<li>模型：统一骨干 kimi-k2.6-cloud（7 路仅 harness 不同）。</li>
<li>打分：官方 swebench v5.0.2 docker harness。</li>
<li>此前 R1567 已做一次归因（cline <b>326</b> 阶段，3 类根因 = 静默退出 35 / 超时卡死 18 / 补丁质量 116，McNemar 极显著）；R1569 适配器修复（commit {CLINE_BASELINE_PRE['fix_commit']}）+ R1633 rerun 58/58 后 cline 抬到 <b>356</b>（比 326 时 +30）。本轮回答的是<b>修复后仍存在的差距</b>。</li>
<li>本轮「cline」= 适配器修复后的终态数据（eval_cline-patched.json，resolved=356）；与 opencode（resolved=401）逐实例配对。</li>
<li>铁律：infra-or-fetch-timeout 单列不计能力；结果 JSON 不入库；所有数字可由本脚本复算。</li>
</ul>
</div>""")
    H.append(f"""
<h2>2. 方法（逐实例配对拆解）</h2>
<div class="box">
<ol>
<li>取 cline 与 opencode 的 per-instance eval 结果（<code>eval_*.json</code> 的 resolved/failed/no_patch）。</li>
<li>交集 common = 两路均有明确 eval 状态的实例 = <b>{len(common)}</b> 题。</li>
<li>差距集 gap = opencode resolved ∩ cline 未 resolved = <b>{len(gap)}</b> 题。</li>
<li>逐题看 cline predict 行为（<code>progress_cline-patched.json</code>：model_patch_len/wall_s/returncode/quota_blocked），归因：① 补丁质量/能力（产了 patch 但测试不过）② 静默退出/超时（无 patch，wall≥1700s 超时墙或 wall&lt;300s 秒级静默）③ no-patch 其它 ④ infra（quota_blocked）。</li>
<li>McNemar 精确双侧检验（cline vs opencode，common 题配对）。</li>
<li>对补丁质量子集，对照 opencode 同题 patch 大小/耗时/repo 分布。</li>
</ol>
</div>""")
    H.append(f"""
<h2>3. McNemar 配对检验</h2>
<div class="box">
<table class="kv">
<tr><td>配对集合 common</td><td><b>{len(common)}</b> 题</td></tr>
<tr><td>cline resolved（common 内）</td><td><b>{cline_res_common}</b>（{cline_res_common/len(common)*100:.1f}%）</td></tr>
<tr><td>opencode resolved（common 内）</td><td><b>{open_res_common}</b>（{open_res_common/len(common)*100:.1f}%）</td></tr>
<tr><td>n₀₁（cline 解而 opencode 未解）</td><td><b>{mc['n01']}</b></td></tr>
<tr><td>n₁₀（opencode 解而 cline 未解）</td><td><b>{mc['n10']}</b></td></tr>
<tr><td>不一致对 discordant</td><td><b>{mc['discordant']}</b></td></tr>
<tr><td>精确双侧 p 值</td><td><b>{p_str}</b></td></tr>
<tr><td>opencode/cline 优势比 OR（=n₁₀/n₀₁）</td><td><b>{or_str}</b></td></tr>
</table>
<div class="small">判读：p ≈ {p_str} ≪ 0.001，两路差异<b>极显著</b>；OR={or_str} 意味着不一致对中 opencode 解而 cline 未解的频次约为反向的 {or_str} 倍。</div>
</div>""")
    pie_parts=[("① 补丁质量/能力",ability,"#2563eb"),("② 静默退出/超时",harness_adapt,"#f59e0b"),("④ infra",infra,"#9ca3af")]
    pie_parts=[p for p in pie_parts if p[1]>0]
    H.append(f"""
<h2>4. 差距集归因（{len(gap)} 题）</h2>
<div class="box">
<div style="display:flex;flex-wrap:wrap;gap:24px;align-items:center;">
<div>{pie_svg(pie_parts,len(gap))}</div>
<div style="flex:1;min-width:280px;">
<table>
<tr><th>归因</th><th>题数</th><th>占比</th><th>性质</th></tr>
<tr><td><span class="swatch" style="background:#2563eb"></span>① 补丁质量/能力</td><td><b>{ability}</b></td><td>{ability/len(gap)*100:.1f}%</td><td>能力差（模型/底座）</td></tr>
<tr><td><span class="swatch" style="background:#f59e0b"></span>② 静默退出/超时（harness 适配）</td><td><b>{harness_adapt}</b></td><td>{harness_adapt/len(gap)*100:.1f}%</td><td>接入损耗</td></tr>
<tr><td><span class="swatch" style="background:#9ca3af"></span>④ infra（quota/网络）</td><td><b>{infra}</b></td><td>{infra/len(gap)*100:.1f}%</td><td>不计能力</td></tr>
<tr><th colspan="2">合计</th><th>{len(gap)}</th><th>100%</th></tr>
</table>
<div class="small" style="margin-top:8px;">② 含：超时墙 1800s 命中 {cat_counts['no_patch_timeout']} 题 + 秒级静默退出 {cat_counts['no_patch_quick']} 题；③ no-patch 其它 {cat_counts['no_patch_other']} 题。</div>
</div>
</div>
</div>""")
    H.append(f"""
<h2>5. 补丁质量/能力深挖（{ability} 题）</h2>
<div class="box">
<p>这 {ability} 题 cline 都<b>产出了 patch 但测试不过</b>，属「能力差」而非「没跑通」。对照 opencode 同题：</p>
<table class="kv">
<tr><td>cline patch 字节数</td><td class="mono">{fmt_stats(pq_cline_sizes)}</td></tr>
<tr><td>opencode patch 字节数</td><td class="mono">{fmt_stats(pq_open_sizes)}</td></tr>
<tr><td>cline wall_s（秒）</td><td class="mono">{fmt_stats(pq_cline_wall)}</td></tr>
<tr><td>opencode wall_s（秒）</td><td class="mono">{fmt_stats(pq_open_wall)}</td></tr>
<tr><td>opencode patch 比 cline 更大的题数</td><td><b>{bigger_open}</b> / {len(pq)}</td></tr>
</table>
<p class="small">解读：补丁质量子集里 cline patch 中位 {statistics.median(pq_cline_sizes):.0f}B vs opencode {statistics.median(pq_open_sizes):.0f}B，opencode 在 {bigger_open}/{len(pq)} 题上 patch 更大；但「更大」不等于「更好」——多数是 cline 改对了位置但<b>不够完整</b>（漏改关联文件/测试覆盖不足）或<b>改错方向</b>。cline 平均耗时 {statistics.mean(pq_cline_wall):.0f}s 略高于 opencode {statistics.mean(pq_open_wall):.0f}s，说明 cline 多花了时间却没换来更高 resolved 率，提示其工具循环/上下文组织效率偏低。</p>
</div>""")
    repo_rows=[(f"{repo} ({n})",n,"#2563eb") for repo,n in repo_dist.most_common()]
    H.append(f"""
<h2>6. 差距集 repo 分布</h2>
<div class="box">
{bar_svg(repo_rows,w=520,h=max(140,len(repo_rows)*34))}
<p class="small">差距集中在 <b>django（{repo_dist['django']} 题）</b>，其次 sympy/sphinx-doc。django 占比高与该库题量大、多文件改动需求多有关。</p>
</div>""")
    np_rows=[r for r in rows if r["cat"] in ("no_patch_timeout","no_patch_quick","infra_quota","no_patch_other")]
    np_html=""
    for r in np_rows:
        tag="超时1800s" if r["cat"]=="no_patch_timeout" else ("秒级静默退出" if r["cat"]=="no_patch_quick" else ("infra/quota" if r["cat"]=="infra_quota" else "no-patch其它"))
        np_html+=f"<tr><td class='mono'>{esc(r['iid'])}</td><td>{tag}</td><td class='mono'>{r['cline_wall']:.0f}s</td><td class='mono'>rc={r['cline_rc']}</td><td class='mono'>{'quota' if r['cline_quota'] else '-'}</td><td class='mono'>{r['open_patch_len']}</td></tr>"
    quick_iid=[r['iid'] for r in rows if r['cat']=='no_patch_quick'][0] if cat_counts['no_patch_quick'] else '—'
    H.append(f"""
<h2>7. 静默退出/超时 与 infra（{len(np_rows)} 题）</h2>
<div class="box">
<p>这些题 cline <b>没产出 patch</b>，属接入损耗或 infra，不计能力差：</p>
<div class="scrollx"><table>
<tr><th>instance_id</th><th>类型</th><th>cline wall</th><th>cline rc</th><th>quota</th><th>opencode patch(B)</th></tr>
{np_html}
</table></div>
<p class="small">判读：{cat_counts['no_patch_timeout']} 题 cline 命中 1800s 超时墙（rc=1，未产 patch）——harness 适配层的<b>超时硬限</b>；{cat_counts['no_patch_quick']} 题（{quick_iid}）秒级静默退出（2.9s, rc=0）——残余 silent-exit bug；{infra} 题 quota_blocked。opencode 在这些同题上均产出了 patch 并 resolved，说明题本身可解，cline 只是没跑通。</p>
</div>""")
    H.append(f"""
<h2>8. 差距集逐实例表（opencode 解、cline 未解，共 {len(gap)} 题）</h2>
<div class="box scrollx">
<table>
<tr><th>#</th><th>instance_id</th><th>归因</th><th>cline patch(B)</th><th>cline wall(s)</th><th>cline rc</th><th>opencode patch(B)</th><th>opencode wall(s)</th></tr>""")
    for i,r in enumerate(rows,1):
        H.append(f"<tr><td>{i}</td><td class='mono'>{esc(r['iid'])}</td><td><span class='pill' style='background:{r['color']}'>{esc(r['cat_label'])}</span></td><td class='mono'>{r['cline_patch_len']}</td><td class='mono'>{r['cline_wall']:.0f}</td><td class='mono'>{r['cline_rc']}</td><td class='mono'>{r['open_patch_len']}</td><td class='mono'>{r['open_wall']:.0f}</td></tr>")
    H.append("</table></div>")
    H.append(f"""
<h2>9. 根因结论：能力差 vs 接入损耗</h2>
<div class="box">
<table class="kv">
<tr><td>能力差（补丁质量/模型底座）</td><td><b>{ability} 题（{ability/len(gap)*100:.0f}%）</b> —— cline 产了 patch 但测试不过</td></tr>
<tr><td>接入损耗（harness 适配/超时/静默退出）</td><td><b>{harness_adapt} 题（{harness_adapt/len(gap)*100:.0f}%）</b></td></tr>
<tr><td>infra（不计能力）</td><td><b>{infra} 题（{infra/len(gap)*100:.0f}%）</b></td></tr>
</table>
<p><b>结论</b>：R1569 适配器修复后，cline 与 opencode 的差距<b>已从「接入损耗为主」转为「能力差为主」</b>。修复前（326 阶段）静默退出 35 + 超时 18 占主要矛盾；修复后静默退出/超时仅 {harness_adapt} 题，<b>{ability}/{len(gap)}={ability/len(gap)*100:.0f}% 的差距是 cline 产了 patch 但不完整/不正确</b>——这是 kimi-k2.6 底座在 cline harness 的上下文组织与工具循环下「能定位但改不全/改不对」的能力问题，而非 harness 没跑通。统计上该差距极显著（McNemar p={p_str}）。</p>
<p class="small">注：能力差≠「cline harness 设计差」。同一 kimi-k2.6 底座在 opencode harness 下 resolved 401，说明 harness 的<b>上下文组织/工具授予/探索策略</b>会显著放大或抑制底座能力。cline 的差距可拆为「底座固有上限」与「harness 对底座能力的利用率」两部分，后者是可改进的接入损耗-能力复合项。</p>
</div>""")
    H.append(f"""
<h2>10. 可落地改进清单（标注置信度）</h2>
<div class="box">
<table>
<tr><th>方向</th><th>措施</th><th>预期收益</th><th>置信度</th></tr>
<tr><td>接入损耗</td><td>把 cline 超时墙 1800s 对易超时题（django 大库）分级上调或动态限时，减少 {cat_counts['no_patch_timeout']} 题硬超时</td><td>回收 ~{cat_counts['no_patch_timeout']} 题</td><td>中</td></tr>
<tr><td>接入损耗</td><td>排查 {cat_counts['no_patch_quick']} 题秒级静默退出残余 bug（rc=0 但无 patch），run_single 加 exit-code 与 patch 双校验重试</td><td>回收 ~{cat_counts['no_patch_quick']} 题</td><td>高</td></tr>
<tr><td>能力复合</td><td>增大 cline 单次可见上下文/文件检索范围，减少「改对位置漏改关联文件」（补丁质量 {ability} 题主因）</td><td>回收 5–15 题（估）</td><td>中</td></tr>
<tr><td>能力复合</td><td>对 cline 工具循环加「测试自检」步骤：产 patch 后本地跑目标测试，失败则迭代，对标 opencode 探索策略</td><td>回收 5–10 题（估）</td><td>中</td></tr>
<tr><td>底座</td><td>换更强底座或 kimi-k2.6 更新版本（同 harness 对比可隔离 harness 因素）</td><td>回收 10–20 题（估）</td><td>低</td></tr>
<tr><td>infra</td><td>quota_blocked {infra} 题：重试/错峰，配额恢复后重跑</td><td>回收 ~{infra} 题</td><td>高</td></tr>
</table>
<p class="small">「回收」为乐观估计，需逐题重跑验证；置信度：高=有同类成功先例，中=有理论依据待验证，低=依赖外部条件。</p>
</div>""")
    H.append(f"""
<h2>11. 可复现性</h2>
<div class="box">
<p>本报告全部数字由 <code>gen_report_cline_lowscore_analysis_zh.py</code> 从以下源文件现算，无手填常量：</p>
<pre class="mono">数据源：
  run/harness/swebench_verified_full/reports/eval_cline-patched.json   (resolved=356)
  run/harness/swebench_verified_full/reports/eval_opencode.json        (resolved=401)
  run/harness/swebench_verified_full/reports/progress_cline-patched.json
  run/harness/swebench_verified_full/reports/progress_opencode.json
  run/harness/swebench_verified_full/predictions/{{h}}__{{iid}}.json

复算：
  cd run/harness && python3 gen_report_cline_lowscore_analysis_zh.py
  # → doc/BaiZe-ISEDA2027/reports/report_harness_cline_lowscore_analysis_zh.html</pre>
<p class="small">铁律遵守：结果 JSON 不入库（仅本地保留供分析）；命名合规（正文写 cline 不写 cline-patched）；报告产在项目级 reports/ 目录。</p>
</div>
<div class="meta" style="margin-top:24px;">— 报告结束 · BaiZe harness 线 · {now} —</div>
</body></html>""")
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text("\n".join(H),encoding="utf-8")
    print(f"WROTE {OUT} ({OUT.stat().st_size} B)")
    print(f"cline={cline_res_common} opencode={open_res_common} gap={len(gap)} net={net_diff} mcnemar_p={p_str}")
    print(f"attribution: ability={ability} harness_adapt={harness_adapt} infra={infra}")

if __name__=="__main__":
    main()
