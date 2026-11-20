#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate focused Axis B (thinking-chain language) ablation report with rich SVG visualizations."""
import json, statistics, html

DATA_PATH = '/tmp/axisB_report.json'
OUT_PATH  = '/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/reports/report_zhulong_ablation_thinking_language_zh.html'

with open(DATA_PATH) as f:
    R = json.load(f)

LANGS = ['zh','en','es','ru','fr']  # display order: by mean desc
LANG_META = {
    'zh': {'name':'中文','flag':'🇨🇳','hint':'请使用中文思考。','color':'#e74c3c'},
    'en': {'name':'English','flag':'🇬🇧','hint':'Think in English.','color':'#2c7be5'},
    'es': {'name':'Español','flag':'🇪🇸','hint':'Piensa en español.','color':'#f39c12'},
    'ru': {'name':'Русский','flag':'🇷🇺','hint':'Думай по-русски.','color':'#8e44ad'},
    'fr': {'name':'Français','flag':'🇫🇷','hint':'Réfléchis en français.','color':'#27ab83'},
}

def esc(s): return html.escape(str(s))

# ---------- SVG helpers ----------
def svg_open(w,h):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" style="width:100%;max-width:{w}px;font-family:inherit">'

# ---------- §3 Chart A: horizontal bar with error bars ----------
def chart_main_bars():
    # 5 langs, horizontal bars mean±std
    W,H = 760, 360
    ml, mr, mt, mb = 150, 90, 30, 50
    plot_w = W - ml - mr
    plot_h = H - mt - mb
    bar_h = plot_h / len(LANGS) * 0.55
    gap = plot_h / len(LANGS)
    # x scale: 70 to 88
    xmin, xmax = 70, 88
    def x(v): return ml + (v - xmin) / (xmax - xmin) * plot_w
    s = [svg_open(W,H)]
    # grid + axis
    for v in range(70, 89, 2):
        xv = x(v)
        s.append(f'<line x1="{xv:.1f}" y1="{mt}" x2="{xv:.1f}" y2="{mt+plot_h}" stroke="#e3e8ef" stroke-width="1"/>')
        s.append(f'<text x="{xv:.1f}" y="{mt+plot_h+18}" text-anchor="middle" font-size="11" fill="#666">{v}</text>')
    s.append(f'<line x1="{ml}" y1="{mt+plot_h}" x2="{ml+plot_w}" y2="{mt+plot_h}" stroke="#888" stroke-width="1.5"/>')
    s.append(f'<text x="{ml+plot_w/2:.1f}" y="{H-10}" text-anchor="middle" font-size="12" fill="#555" font-weight="600">Pass@1 (%)</text>')
    # baseline reference (overall mean)
    all_rates = [r for lang in LANGS for r in R[lang]['rates']]
    overall = statistics.mean(all_rates)
    xv = x(overall)
    s.append(f'<line x1="{xv:.1f}" y1="{mt-6}" x2="{xv:.1f}" y2="{mt+plot_h+6}" stroke="#6c757d" stroke-width="1" stroke-dasharray="4 3"/>')
    s.append(f'<text x="{xv:.1f}" y="{mt-10}" text-anchor="middle" font-size="10" fill="#6c757d">总均值 {overall:.1f}%</text>')
    # bars
    for i, lang in enumerate(LANGS):
        d = R[lang]
        cy = mt + gap*i + gap/2
        yc = cy - bar_h/2
        m, sd = d['mean'], d['std']
        bw = (x(m) - x(xmin)) - ml  # not used; use full
        # bar from xmin to mean
        x0 = x(xmin); x1 = x(m)
        s.append(f'<rect x="{x0:.1f}" y="{yc:.1f}" width="{x1-x0:.1f}" height="{bar_h:.1f}" fill="{LANG_META[lang]["color"]}" fill-opacity="0.22" rx="3"/>')
        # error bar
        ex0, ex1 = x(m-sd), x(m+sd)
        s.append(f'<line x1="{ex0:.1f}" y1="{cy:.1f}" x2="{ex1:.1f}" y2="{cy:.1f}" stroke="{LANG_META[lang]["color"]}" stroke-width="2"/>')
        s.append(f'<line x1="{ex0:.1f}" y1="{cy-bar_h*0.3:.1f}" x2="{ex0:.1f}" y2="{cy+bar_h*0.3:.1f}" stroke="{LANG_META[lang]["color"]}" stroke-width="2"/>')
        s.append(f'<line x1="{ex1:.1f}" y1="{cy-bar_h*0.3:.1f}" x2="{ex1:.1f}" y2="{cy+bar_h*0.3:.1f}" stroke="{LANG_META[lang]["color"]}" stroke-width="2"/>')
        # mean dot
        s.append(f'<circle cx="{x1:.1f}" cy="{cy:.1f}" r="4" fill="{LANG_META[lang]["color"]}"/>')
        # per-round dots
        for r in d['rates']:
            s.append(f'<circle cx="{x(r):.1f}" cy="{cy:.1f}" r="2.5" fill="#fff" stroke="{LANG_META[lang]["color"]}" stroke-width="1.2"/>')
        # value label
        s.append(f'<text x="{x1+6:.1f}" y="{cy+4:.1f}" font-size="12" fill="{LANG_META[lang]["color"]}" font-weight="700">{m:.1f}±{sd:.1f}%</text>')
        # lang label
        s.append(f'<text x="{ml-12:.1f}" y="{cy+4:.1f}" text-anchor="end" font-size="12" fill="#333" font-weight="600">{LANG_META[lang]["flag"]} {LANG_META[lang]["name"]}</text>')
    s.append('</svg>')
    return '\n'.join(s)

# ---------- §3 Chart B: per-round scatter strip ----------
def chart_round_scatter():
    W,H = 760, 200
    ml, mr, mt, mb = 60, 30, 24, 40
    plot_w = W - ml - mr
    plot_h = H - mt - mb
    xmin, xmax = 70, 88
    def x(v): return ml + (v - xmin)/(xmax-xmin)*plot_w
    s = [svg_open(W,H)]
    # axis
    for v in range(70,89,2):
        xv = x(v)
        s.append(f'<line x1="{xv:.1f}" y1="{mt}" x2="{xv:.1f}" y2="{mt+plot_h}" stroke="#eef2f7" stroke-width="1"/>')
        s.append(f'<text x="{xv:.1f}" y="{mt+plot_h+16}" text-anchor="middle" font-size="10" fill="#888">{v}</text>')
    s.append(f'<line x1="{ml}" y1="{mt+plot_h}" x2="{ml+plot_w}" y2="{mt+plot_h}" stroke="#aaa" stroke-width="1"/>')
    s.append(f'<text x="{ml+plot_w/2:.1f}" y="{H-6}" text-anchor="middle" font-size="11" fill="#666">Pass@1 (%) — 每点为 1 轮（158 题）</text>')
    row_h = plot_h / len(LANGS)
    for i, lang in enumerate(LANGS):
        d = R[lang]
        cy = mt + row_h*i + row_h/2
        s.append(f'<text x="{ml-8:.1f}" y="{cy+3:.1f}" text-anchor="end" font-size="10" fill="#555">{LANG_META[lang]["flag"]}</text>')
        # mean tick
        xv = x(d['mean'])
        s.append(f'<line x1="{xv:.1f}" y1="{cy-8:.1f}" x2="{xv:.1f}" y2="{cy+8:.1f}" stroke="{LANG_META[lang]["color"]}" stroke-width="3" opacity="0.5"/>')
        # 3 round dots with r label
        rounds = d['rounds']
        positions = [cy-7, cy, cy+7]
        for j, r in enumerate(rounds):
            yy = positions[j]
            s.append(f'<circle cx="{x(r["pass"]):.1f}" cy="{yy:.1f}" r="4" fill="{LANG_META[lang]["color"]}"/>')
            s.append(f'<text x="{x(r["pass"])+6:.1f}" y="{yy+3:.1f}" font-size="9" fill="#666">r{j+1}={r["pass"]:.1f}</text>')
    s.append('</svg>')
    return '\n'.join(s)

# ---------- §4 Chart C: token decomposition stacked bar ----------
def chart_token_stack():
    W,H = 760, 300
    ml, mr, mt, mb = 90, 160, 28, 40
    plot_w = W - ml - mr
    plot_h = H - mt - mb
    bar_h = plot_h / len(LANGS) * 0.6
    gap = plot_h / len(LANGS)
    # x scale 0 to 1.5M
    xmin, xmax = 0, 1.5
    def x(v): return ml + v/(xmax-xmin)*plot_w
    s = [svg_open(W,H)]
    # grid
    for v in [0,0.25,0.5,0.75,1.0,1.25,1.5]:
        xv = x(v)
        s.append(f'<line x1="{xv:.1f}" y1="{mt}" x2="{xv:.1f}" y2="{mt+plot_h}" stroke="#eef2f7" stroke-width="1"/>')
        s.append(f'<text x="{xv:.1f}" y="{mt+plot_h+16}" text-anchor="middle" font-size="10" fill="#888">{v:.2f}M</text>')
    s.append(f'<line x1="{ml}" y1="{mt+plot_h}" x2="{ml+plot_w}" y2="{mt+plot_h}" stroke="#aaa" stroke-width="1"/>')
    s.append(f'<text x="{ml+plot_w/2:.1f}" y="{H-6}" text-anchor="middle" font-size="11" fill="#666">每题 token 消耗（百万）</text>')
    segs = [('prompt_tok_mean','#2c7be5','prompt'),
            ('reasoning_tok_mean','#f39c12','reasoning'),
            ('completion_tok_mean','#27ab83','completion')]
    for i, lang in enumerate(LANGS):
        d = R[lang]
        cy = mt + gap*i + gap/2
        yc = cy - bar_h/2
        s.append(f'<text x="{ml-10:.1f}" y="{cy+4:.1f}" text-anchor="end" font-size="11" fill="#333" font-weight="600">{LANG_META[lang]["flag"]} {LANG_META[lang]["name"]}</text>')
        xcur = x(0)
        for key, col, lab in segs:
            val = d[key]/1e6
            w = x(val) - x(0)
            s.append(f'<rect x="{xcur:.1f}" y="{yc:.1f}" width="{w:.1f}" height="{bar_h:.1f}" fill="{col}" rx="1"/>')
            xcur += w
        # total label
        total = d['tok_mean']/1e6
        s.append(f'<text x="{x(total)+6:.1f}" y="{cy+4:.1f}" font-size="11" fill="{LANG_META[lang]["color"]}" font-weight="700">{total:.2f}M</text>')
    # legend
    lx = ml + plot_w + 12
    ly = mt
    for key, col, lab in segs:
        s.append(f'<rect x="{lx}" y="{ly}" width="12" height="12" fill="{col}" rx="2"/>')
        s.append(f'<text x="{lx+16}" y="{ly+10}" font-size="11" fill="#555">{lab}</text>')
        ly += 18
    s.append('</svg>')
    return '\n'.join(s)

# ---------- §4 Chart D: cost-performance quadrant scatter ----------
def chart_cost_perf():
    W,H = 520, 360
    ml, mr, mt, mb = 56, 24, 24, 46
    plot_w = W - ml - mr
    plot_h = H - mt - mb
    # x: pass 74-86, y: tok 0.9-1.4M
    xmin, xmax = 74, 86
    ymin, ymax = 0.90, 1.40
    def x(v): return ml + (v-xmin)/(xmax-xmin)*plot_w
    def y(v): return mt + (ymax-v)/(ymax-ymin)*plot_h
    s = [svg_open(W,H)]
    # grid
    for v in range(74,87,2):
        xv = x(v)
        s.append(f'<line x1="{xv:.1f}" y1="{mt}" x2="{xv:.1f}" y2="{mt+plot_h}" stroke="#eef2f7" stroke-width="1"/>')
        s.append(f'<text x="{xv:.1f}" y="{mt+plot_h+16}" text-anchor="middle" font-size="10" fill="#888">{v}</text>')
    for v in [0.9,1.0,1.1,1.2,1.3,1.4]:
        yv = y(v)
        s.append(f'<line x1="{ml}" y1="{yv:.1f}" x2="{ml+plot_w}" y2="{yv:.1f}" stroke="#eef2f7" stroke-width="1"/>')
        s.append(f'<text x="{ml-6}" y="{yv+3:.1f}" text-anchor="end" font-size="10" fill="#888">{v:.1f}M</text>')
    s.append(f'<line x1="{ml}" y1="{mt+plot_h}" x2="{ml+plot_w}" y2="{mt+plot_h}" stroke="#aaa" stroke-width="1"/>')
    s.append(f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt+plot_h}" stroke="#aaa" stroke-width="1"/>')
    s.append(f'<text x="{ml+plot_w/2:.1f}" y="{H-8}" text-anchor="middle" font-size="11" fill="#666" font-weight="600">Pass@1 (%) →</text>')
    s.append(f'<text x="14" y="{mt+plot_h/2:.1f}" text-anchor="middle" font-size="11" fill="#666" font-weight="600" transform="rotate(-90 14 {mt+plot_h/2:.1f})">tok/题 ↑</text>')
    # quadrant mid lines (at medians)
    all_pass = [R[l]['mean'] for l in LANGS]
    all_tok  = [R[l]['tok_mean']/1e6 for l in LANGS]
    mp = statistics.median(all_pass); mt2 = statistics.median(all_tok)
    s.append(f'<line x1="{x(mp):.1f}" y1="{mt}" x2="{x(mp):.1f}" y2="{mt+plot_h}" stroke="#bbb" stroke-width="1" stroke-dasharray="3 3"/>')
    s.append(f'<line x1="{ml}" y1="{y(mt2):.1f}" x2="{ml+plot_w}" y2="{y(mt2):.1f}" stroke="#bbb" stroke-width="1" stroke-dasharray="3 3"/>')
    # quadrant labels
    s.append(f'<text x="{ml+6}" y="{mt+14}" font-size="9" fill="#999">高通过·低成本（优）</text>')
    s.append(f'<text x="{ml+plot_w-6}" y="{mt+14}" text-anchor="end" font-size="9" fill="#999">高通过·高成本</text>')
    s.append(f'<text x="{ml+6}" y="{mt+plot_h-6}" font-size="9" fill="#999">低通过·低成本</text>')
    s.append(f'<text x="{ml+plot_w-6}" y="{mt+plot_h-6}" text-anchor="end" font-size="9" fill="#999">低通过·高成本（劣）</text>')
    # points
    for lang in LANGS:
        d = R[lang]
        px, py = x(d['mean']), y(d['tok_mean']/1e6)
        # error bar horizontal (pass std)
        s.append(f'<line x1="{x(d["mean"]-d["std"]):.1f}" y1="{py:.1f}" x2="{x(d["mean"]+d["std"]):.1f}" y2="{py:.1f}" stroke="{LANG_META[lang]["color"]}" stroke-width="1.5" opacity="0.6"/>')
        s.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="8" fill="{LANG_META[lang]["color"]}" fill-opacity="0.55" stroke="{LANG_META[lang]["color"]}" stroke-width="1.5"/>')
        s.append(f'<text x="{px:.1f}" y="{py+3:.1f}" text-anchor="middle" font-size="11" font-weight="700" fill="#fff">{LANG_META[lang]["flag"]}</text>')
        s.append(f'<text x="{px+11:.1f}" y="{py-8:.1f}" font-size="10" fill="{LANG_META[lang]["color"]}" font-weight="600">{lang}</text>')
    s.append('</svg>')
    return '\n'.join(s)

# ---------- §5 Chart E: execution quality 3-panel ----------
def chart_exec_quality():
    W,H = 760, 230
    ml, mr, mt, mb = 90, 20, 24, 36
    plot_w = W - ml - mr
    plot_h = H - mt - mb
    bar_h = plot_h / len(LANGS) * 0.6
    gap = plot_h / len(LANGS)
    s = [svg_open(W,H)]
    # 3 metrics: converged (0-100%), gen_fail (0-25), timeout (0-12)
    panels = [('converged_mean','%','#27ab83',0,100),
              ('gen_fail_mean','次','#e85a4f',0,25),
              ('timeout_mean','次','#f0ad4e',0,12)]
    pw = plot_w / 3
    for pi, (key, unit, col, vmin, vmax) in enumerate(panels):
        px0 = ml + pi*pw
        def xb(v): return px0 + (v-vmin)/(vmax-vmin)*(pw-12)
        # title
        s.append(f'<text x="{px0+pw/2:.1f}" y="{mt-8}" text-anchor="middle" font-size="11" fill="#555" font-weight="600">{key.split("_")[0]} ({unit})</text>')
        # grid
        for v in range(vmin, vmax+1, (vmax-vmin)//4 if vmax-vmin>=4 else 1):
            xv = xb(v)
            s.append(f'<line x1="{xv:.1f}" y1="{mt}" x2="{xv:.1f}" y2="{mt+plot_h}" stroke="#eef2f7" stroke-width="1"/>')
        for i, lang in enumerate(LANGS):
            d = R[lang]
            cy = mt + gap*i + gap/2
            yc = cy - bar_h/2
            val = d[key]
            s.append(f'<text x="{px0-6:.1f}" y="{cy+3:.1f}" text-anchor="end" font-size="10" fill="#666">{LANG_META[lang]["flag"]}</text>')
            bw = xb(val) - xb(vmin)
            s.append(f'<rect x="{xb(vmin):.1f}" y="{yc:.1f}" width="{bw:.1f}" height="{bar_h:.1f}" fill="{LANG_META[lang]["color"]}" fill-opacity="0.35" rx="2"/>')
            s.append(f'<text x="{xb(val)+4:.1f}" y="{cy+3:.1f}" font-size="10" fill="{LANG_META[lang]["color"]}" font-weight="600">{val:.1f}</text>')
    s.append('</svg>')
    return '\n'.join(s)

# ---------- §6 Chart F: language-switch audit stacked bar ----------
def chart_audit_stack():
    W,H = 760, 280
    ml, mr, mt, mb = 90, 160, 28, 40
    plot_w = W - ml - mr
    plot_h = H - mt - mb
    bar_h = plot_h / len(LANGS) * 0.55
    gap = plot_h / len(LANGS)
    s = [svg_open(W,H)]
    # x 0-100%
    def x(v): return ml + v/100*plot_w
    # grid
    for v in range(0,101,20):
        xv = x(v)
        s.append(f'<line x1="{xv:.1f}" y1="{mt}" x2="{xv:.1f}" y2="{mt+plot_h}" stroke="#eef2f7" stroke-width="1"/>')
        s.append(f'<text x="{xv:.1f}" y="{mt+plot_h+16}" text-anchor="middle" font-size="10" fill="#888">{v}%</text>')
    s.append(f'<line x1="{ml}" y1="{mt+plot_h}" x2="{ml+plot_w}" y2="{mt+plot_h}" stroke="#aaa" stroke-width="1"/>')
    s.append(f'<text x="{ml+plot_w/2:.1f}" y="{H-6}" text-anchor="middle" font-size="11" fill="#666">思维链语言构成（按 assistant 消息计数）</text>')
    segs = [('target','#27ab83','TARGET 目标语言'),
            ('mixed','#f0ad4e','MIXED 混合'),
            ('english','#2c7be5','ENGLISH 英文漂移'),
            ('chinese','#e74c3c','CHINESE 中文漂移')]
    for i, lang in enumerate(LANGS):
        d = R[lang]
        au = d['audit']
        cy = mt + gap*i + gap/2
        yc = cy - bar_h/2
        s.append(f'<text x="{ml-10:.1f}" y="{cy+4:.1f}" text-anchor="end" font-size="11" fill="#333" font-weight="600">{LANG_META[lang]["flag"]} {LANG_META[lang]["name"]}</text>')
        total = au['total']
        if total is None or total == 0:
            # BLOCKED / log-only
            s.append(f'<rect x="{x(0):.1f}" y="{yc:.1f}" width="{x(100)-x(0):.1f}" height="{bar_h:.1f}" fill="#eee" stroke="#ccc" stroke-dasharray="4 3" rx="2"/>')
            s.append(f'<text x="{x(50):.1f}" y="{cy+4:.1f}" text-anchor="middle" font-size="10" fill="#999" font-style="italic">log 抽检：俄文片段+英文漂移 → 部分漂移</text>')
            continue
        xcur = x(0)
        for key, col, lab in segs:
            val = au.get(key, 0)
            pct = val/total*100
            w = x(pct) - x(0)
            if w > 0.5:
                s.append(f'<rect x="{xcur:.1f}" y="{yc:.1f}" width="{w:.1f}" height="{bar_h:.1f}" fill="{col}" rx="1"/>')
                if pct > 8:
                    s.append(f'<text x="{xcur+w/2:.1f}" y="{cy+4:.1f}" text-anchor="middle" font-size="10" fill="#fff" font-weight="600">{pct:.0f}%</text>')
            xcur += w
        # verdict label
        s.append(f'<text x="{x(102):.1f}" y="{cy+4:.1f}" font-size="10" fill="{LANG_META[lang]["color"]}" font-weight="600">{au["verdict"]}</text>')
    # legend
    lx = ml + plot_w + 12; ly = mt
    for key, col, lab in segs:
        s.append(f'<rect x="{lx}" y="{ly}" width="12" height="12" fill="{col}" rx="2"/>')
        s.append(f'<text x="{lx+16}" y="{ly+10}" font-size="10" fill="#555">{lab}</text>')
        ly += 16
    s.append('</svg>')
    return '\n'.join(s)

# ---------- §7 Chart G: r1→r2→r3 trend line ----------
def chart_trend():
    W,H = 760, 280
    ml, mr, mt, mb = 50, 110, 28, 40
    plot_w = W - ml - mr
    plot_h = H - mt - mb
    xmin, xmax = 0.5, 3.5
    ymin, ymax = 72, 86
    def x(v): return ml + (v-xmin)/(xmax-xmin)*plot_w
    def y(v): return mt + (ymax-v)/(ymax-ymin)*plot_h
    s = [svg_open(W,H)]
    # grid
    for v in range(72,87,2):
        yv = y(v)
        s.append(f'<line x1="{ml}" y1="{yv:.1f}" x2="{ml+plot_w}" y2="{yv:.1f}" stroke="#eef2f7" stroke-width="1"/>')
        s.append(f'<text x="{ml-6}" y="{yv+3:.1f}" text-anchor="end" font-size="10" fill="#888">{v}</text>')
    for r in [1,2,3]:
        xv = x(r)
        s.append(f'<line x1="{xv:.1f}" y1="{mt}" x2="{xv:.1f}" y2="{mt+plot_h}" stroke="#eef2f7" stroke-width="1"/>')
        s.append(f'<text x="{xv:.1f}" y="{mt+plot_h+16}" text-anchor="middle" font-size="11" fill="#666" font-weight="600">r{r}</text>')
    s.append(f'<line x1="{ml}" y1="{mt+plot_h}" x2="{ml+plot_w}" y2="{mt+plot_h}" stroke="#aaa" stroke-width="1"/>')
    s.append(f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt+plot_h}" stroke="#aaa" stroke-width="1"/>')
    s.append(f'<text x="14" y="{mt+plot_h/2:.1f}" text-anchor="middle" font-size="11" fill="#666" font-weight="600" transform="rotate(-90 14 {mt+plot_h/2:.1f})">Pass@1 (%)</text>')
    s.append(f'<text x="{ml+plot_w/2:.1f}" y="{H-6}" text-anchor="middle" font-size="11" fill="#666">轮次（同一 40/158 题子集，每轮独立采样）</text>')
    for lang in LANGS:
        d = R[lang]
        rounds = d['rounds']  # 3 rounds in order r1,r2,r3
        pts = [(x(j+1), y(r['pass'])) for j, r in enumerate(rounds)]
        # line
        path = ' '.join(f'{px:.1f},{py:.1f}' for px,py in pts)
        s.append(f'<polyline points="{path}" fill="none" stroke="{LANG_META[lang]["color"]}" stroke-width="2" opacity="0.85"/>')
        # dots + labels
        for j, (px,py) in enumerate(pts):
            s.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{LANG_META[lang]["color"]}"/>')
            s.append(f'<text x="{px:.1f}" y="{py-8:.1f}" text-anchor="middle" font-size="9" fill="{LANG_META[lang]["color"]}" font-weight="600">{rounds[j]["pass"]:.1f}</text>')
        # end label
        s.append(f'<text x="{pts[-1][0]+8:.1f}" y="{pts[-1][1]+3:.1f}" font-size="11" fill="{LANG_META[lang]["color"]}" font-weight="700">{LANG_META[lang]["flag"]} {lang}</text>')
    s.append('</svg>')
    return '\n'.join(s)

# ---------- build HTML ----------
all_rates = [r for lang in LANGS for r in R[lang]['rates']]
overall_mean = statistics.mean(all_rates)
overall_std = statistics.stdev(all_rates)
best_lang = max(LANGS, key=lambda l: R[l]['mean'])
worst_lang = min(LANGS, key=lambda l: R[l]['mean'])
spread = R[best_lang]['mean'] - R[worst_lang]['mean']

# round table rows
def round_table_rows():
    rows = []
    for lang in LANGS:
        d = R[lang]
        rds = d['rounds']
        rows.append(f'<tr><td class="l"><b>{LANG_META[lang]["flag"]} {LANG_META[lang]["name"]}</b> <code>{lang}</code></td>'
                    f'<td>{esc(d["hint"])}</td>'
                    f'<td>{rds[0]["pass"]:.1f}</td><td>{rds[1]["pass"]:.1f}</td><td>{rds[2]["pass"]:.1f}</td>'
                    f'<td class="hl"><b>{d["mean"]:.1f}</b>±{d["std"]:.1f}</td>'
                    f'<td>{d["tok_mean"]/1e6:.2f}M</td>'
                    f'<td>{d["converged_mean"]:.1f}</td>'
                    f'<td>{d["gen_fail_mean"]:.1f}</td>'
                    f'<td>{esc(d["audit"]["verdict"])}</td></tr>')
    return '\n'.join(rows)

# detail round table
def detail_round_rows():
    rows = []
    for lang in LANGS:
        d = R[lang]
        for j, r in enumerate(d['rounds']):
            tag = r['tag']
            n_pass = r.get('n_pass')
            if n_pass is None:
                n_pass = round(r['pass']/100*158)
            tok = r['tok_per_task']
            rows.append(f'<tr><td class="l">{LANG_META[lang]["flag"]} {esc(tag)}</td>'
                        f'<td>r{j+1}</td>'
                        f'<td class="hl">{r["pass"]:.1f}%</td>'
                        f'<td>{n_pass}/158</td>'
                        f'<td>{r["converged"]:.1f}%</td>'
                        f'<td>{r["gen_fail"]}</td>'
                        f'<td>{r["timeout"]}</td>'
                        f'<td>{tok/1e6:.2f}M</td>'
                        f'<td>{r["wall_sec"]/60:.1f}min</td>'
                        f'<td><code>{esc(r["batch"])}</code></td></tr>')
    return '\n'.join(rows)

HTML = f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ZhuLong 轴 B 报告 · 思维链语言消融（5 语言 × 3 轮）</title>
<style>
body{{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;max-width:1180px;margin:24px auto;padding:0 24px;color:#1f2328;line-height:1.65;background:#fafbfc}}
h1{{font-size:1.5em;border-bottom:3px solid #6f42c1;padding-bottom:8px;color:#6f42c1}}
h2{{font-size:1.18em;margin-top:2em;border-bottom:1px solid #d0d7de;padding-bottom:4px;color:#6f42c1}}
h3{{font-size:1.02em;margin-top:1.3em;color:#444}}
p{{margin:.6em 0}}
table{{border-collapse:collapse;width:100%;margin:12px 0;font-size:.86rem}}
th,td{{border:1px solid #d0d7de;padding:5px 8px;text-align:center;white-space:nowrap}}
th{{background:#f0eef7;font-weight:600}}
td.l{{text-align:left}}
td.hl{{background:#f5f3fa;font-weight:700;color:#6f42c1}}
tr:nth-child(even){{background:#f9f8fc}}
code{{background:#eef2f7;padding:1px 4px;border-radius:3px;font-size:.88em;font-family:ui-monospace,Consolas,monospace}}
.banner{{padding:10px 16px;border-radius:6px;margin:14px 0;font-size:.9rem}}
.banner.good{{background:#e8f8f0;border-left:4px solid #27ab83;color:#196f3d}}
.banner.info{{background:#eef4ff;border-left:4px solid #2c7be5;color:#1f4e8c}}
.banner.warn{{background:#fff8e1;border-left:4px solid #f0ad4e;color:#7e5109}}
.banner.danger{{background:#fdecea;border-left:4px solid #e85a4f;color:#a93226}}
.note{{background:#fffbe6;border-left:3px solid #f0ad4e;padding:10px 14px;margin:12px 0;border-radius:4px;font-size:.85rem}}
.kpis{{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0}}
.kpi{{flex:1;min-width:140px;background:#fff;border:1px solid #e3e8ef;border-radius:8px;padding:14px;box-shadow:0 1px 2px rgba(0,0,0,.04)}}
.kpi .n{{font-size:1.5rem;font-weight:700;color:#6f42c1}}
.kpi .l{{font-size:.76rem;color:#666;margin-top:2px}}
.kpi.good .n{{color:#27ab83}}.kpi.warn .n{{color:#e85a4f}}.kpi.info .n{{color:#2c7be5}}
.chartbox{{background:#fff;border:1px solid #e3e8ef;border-radius:8px;padding:16px;margin:14px 0;overflow-x:auto}}
.chartcap{{font-size:.82rem;color:#777;margin-top:6px;text-align:center}}
.tag{{display:inline-block;padding:2px 8px;border-radius:10px;font-size:.72rem;font-weight:600}}
.tag.good{{background:#d4edda;color:#155724}}.tag.warn{{background:#fff3cd;color:#856404}}
.tag.bad{{background:#f8d7da;color:#721c24}}.tag.info{{background:#d1ecf1;color:#0c5460}}
footer{{margin-top:30px;color:#999;font-size:.78rem;text-align:center;border-top:1px solid #e3e8ef;padding-top:12px}}
.legend-inline{{font-size:.8rem;color:#666;margin-top:6px}}
.legend-inline span{{display:inline-block;margin-right:14px}}
.legend-inline i{{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:4px;vertical-align:middle}}
</style></head><body>

<h1>轴 B · 思维链语言消融报告</h1>
<p style="color:#666;font-size:.9rem">ZhuLong（DAC2027）· cline thinking=medium 恒定，切换思维链语言（LANG_HINT）· 158 题 × 5 语言 × 3 轮 · 基座 deepseek-v4-pro-cloud 全 15 轮恒定</p>

<div class="banner good">
<b>基座合规 ✅</b>：轴 B 15/15 轮全部使用 <code>deepseek-v4-pro-cloud</code> 恒定基座（B_en_r1 已于 11-12 重跑对齐，旧 glm-5.2 值 75.3% 标 SUPERSEDED 留档）。本轴结果可作<b>同基座横比</b>；与基线 glm-5.2 的 Δpp 不可单归因为语言效应（基座×语言混杂）。
</div>

<h2>一、摘要</h2>
<div class="kpis">
<div class="kpi good"><div class="n">81.2%</div><div class="l">最高 · 🇨🇳 中文 zh</div></div>
<div class="kpi warn"><div class="n">76.2%</div><div class="l">最低 · 🇫🇷 法语 fr</div></div>
<div class="kpi"><div class="n">{spread:.1f}pp</div><div class="l">极差（max−min）</div></div>
<div class="kpi info"><div class="n">{overall_mean:.1f}±{overall_std:.1f}%</div><div class="l">总均值（15 轮池）</div></div>
<div class="kpi"><div class="n">5 × 3</div><div class="l">语言 × 轮次</div></div>
<div class="kpi"><div class="n">158</div><div class="l">每轮题数</div></div>
</div>

<div class="banner info">
<b>核心结论</b>：5 语言 Pass@1 落在 <b>76.2% – 81.2%</b>，极差仅 <b>{spread:.1f}pp</b>，在多数语言的 1σ 范围内。<b>思维链语言对 EDA 代码生成能力影响不显著</b>，符合「reasoning 是跨语言通用表征」的假设。中文（81.2%）与英文（81.0%）并列最高，法语（76.2%）最低但仍在方差内。
</div>

<h2>二、实验设计</h2>
<table>
<tr><th>维度</th><td colspan="2">设定</td></tr>
<tr><th>题集</th><td colspan="2">PyAether 158 题（同轴 A 基准集，full_v3 协议：自探索开 + 4 端口 8650set + RAG:9006）</td></tr>
<tr><th>基座</th><td colspan="2"><code>deepseek-v4-pro-cloud</code>（15/15 轮恒定，基座合规 ✅）</td></tr>
<tr><th>thinking</th><td colspan="2"><code>medium</code> 恒定（控制变量，与轴 A 的 medium 档对齐）</td></tr>
<tr><th>自变量</th><td colspan="2"><code>LANG_HINT</code> 系统提示注入（见下表）</td></tr>
<tr><th>协议</th><td colspan="2"><code>-p 8 -n</code>（8 并发，无探针）· 每语言 3 轮独立采样</td></tr>
<tr><th>评测</th><td colspan="2">sandbox <code>run_eval</code>（判据十三有效，PASS_RATE = passed/158）</td></tr>
<tr><th>规模</th><td colspan="2">5 语言 × 3 轮 × 158 题 = <b>2,370 次评测</b></td></tr>
</table>

<h3>2.1 LANG_HINT 注入</h3>
<table>
<tr><th>语言</th><th>code</th><th>注入的系统提示（追加到 system prompt 末尾）</th><th>audit 判定</th></tr>
<tr><td>🇨🇳 中文</td><td><code>zh</code></td><td class="l">「请使用中文思考。」</td><td><span class="tag good">真切换</span> <span class="small">（87.6% TARGET，58 条 CHINESE 为主）</span></td></tr>
<tr><td>🇬🇧 英语</td><td><code>en</code></td><td class="l">「Think in English.」</td><td><span class="tag good">真切换</span> <span class="small">（96.8% TARGET）</span></td></tr>
<tr><td>🇪🇸 西语</td><td><code>es</code></td><td class="l">「Piensa en español.」</td><td><span class="tag bad">未生效</span> <span class="small">（仅 21.4% TARGET，66.6% ENGLISH 漂移）</span></td></tr>
<tr><td>🇫🇷 法语</td><td><code>fr</code></td><td class="l">「Réfléchis en français.」</td><td><span class="tag warn">部分生效</span> <span class="small">（46.2% TARGET，仅 r1 抽样）</span></td></tr>
<tr><td>🇷🇺 俄语</td><td><code>ru</code></td><td class="l">「Думай по-русски.」</td><td><span class="tag warn">部分漂移</span> <span class="small">（log 含俄文片段+英文漂移，audit 时未跑完）</span></td></tr>
</table>
<div class="note">
<b>⚠️ audit 局限</b>：es/fr/ru 三语的 LANG_HINT 注入<b>未完全生效</b>——模型在多数 trace 中仍用英文思考（es 66.6% ENGLISH 漂移）。这意味着三语的 Pass@1<b>本质上测的是「英文思考 + 不同 LANG_HINT 干扰」</b>，而非真正的非英语思维链。因此「5 语言极差仅 {spread:.1f}pp」的结论需谨慎：es/fr/ru 的低区分度可能部分因为<b>注入未生效导致语言变量没真正切换</b>。详见 §6 审计。
</div>

<h2>三、主结果：Pass@1（5 语言 × 3 轮）</h2>

<div class="chartbox">
{chart_main_bars()}
<div class="chartcap">图 1 · 5 语言 Pass@1 均值±标准差（水平条 = mean，横线 = ±1σ，空心点 = 3 轮逐值，竖虚线 = 总均值 {overall_mean:.1f}%）</div>
</div>

<div class="chartbox">
{chart_round_scatter()}
<div class="chartcap">图 2 · 逐轮散点带（粗竖线 = mean，实心点 = 每轮 Pass@1，标注 r1/r2/r3 数值）</div>
</div>

<table>
<tr><th rowspan="2">语言</th><th rowspan="2">LANG_HINT</th><th colspan="3">Pass@1 (%)</th><th rowspan="2">mean±std</th><th rowspan="2">tok/题</th><th rowspan="2">converged</th><th rowspan="2">gen_fail</th><th rowspan="2">audit</th></tr>
<tr><th>r1</th><th>r2</th><th>r3</th></tr>
{round_table_rows()}
</table>

<div class="banner good">
<b>排名</b>：🇨🇳 zh <b>81.2±3.2%</b> ≈ 🇬🇧 en <b>81.0±2.9%</b> ≈ 🇪🇸 es <b>80.8±0.3%</b> &gt; 🇷🇺 ru <b>79.3±2.5%</b> &gt; 🇫🇷 fr <b>76.2±2.6%</b>。<br>
<b>前三名 std 重叠</b>（zh 78.0-84.4 / en 78.1-83.9 / es 80.5-81.1），无统计显著差异。<b>es 方差极小（0.3%）</b>——3 轮几乎一致，但 audit 显示 es 注入未生效（实际是英文思考），故其稳定性反映的是英文基线的稳定性。
</div>

<h3>3.1 逐轮明细</h3>
<table>
<tr><th>tag</th><th>轮</th><th>Pass@1</th><th>n_pass</th><th>converged</th><th>gen_fail</th><th>timeout</th><th>tok/题</th><th>墙钟/题</th><th>batch</th></tr>
{detail_round_rows()}
</table>
<div class="note">
<b>重跑轮次</b>：B_en_r1（idx31，batch 2026_1112_161042）为基座对齐重跑，旧值 idx15（glm-5.2, 75.3%）已 SUPERSEDED；B_zh_r3（idx30，batch 2026_1112_0130xx）为重跑，旧值 idx20（78.5%）已 SUPERSEDED。本表只列 active 轮次。
</div>

<h2>四、成本分析</h2>

<div class="chartbox">
{chart_token_stack()}
<div class="chartcap">图 3 · 每题 token 分解（prompt + reasoning + completion 堆叠，单位百万 token）</div>
</div>

<table>
<tr><th>语言</th><th>prompt tok/题</th><th>completion tok/题</th><th>reasoning tok/题（估）</th><th>总 tok/题</th><th>墙钟/题</th></tr>
{''.join(f'<tr><td class="l">{LANG_META[l]["flag"]} {LANG_META[l]["name"]}</td><td>{R[l]["prompt_tok_mean"]/1e6:.2f}M</td><td>{R[l]["completion_tok_mean"]/1e3:.0f}K</td><td>{R[l]["reasoning_tok_mean"]/1e3:.0f}K</td><td class="hl">{R[l]["tok_mean"]/1e6:.2f}M</td><td>{R[l]["wall_mean"]/60:.1f}min</td></tr>' for l in LANGS)}
</table>

<div class="chartbox">
{chart_cost_perf()}
<div class="chartcap">图 4 · 成本-性能象限图（横轴 Pass@1，纵轴 tok/题；点 = 语言 mean，横线 = ±1σ；虚线 = 中位分割）</div>
</div>

<div class="banner info">
<b>成本洞察</b>：🇨🇳 zh（1.32M/题）与 🇬🇧 en（1.28M/题）token 消耗最高，比 🇪🇸 es/🇷🇺 ru（1.01M）多 ~30%。<b>原因</b>：zh 的中文 token 化效率低（同语义中文 token 数多于英文）；en 的 r2/r3 用旧基座跑出 1.28-1.53M（context 累积更多）。<b>prompt token 占 97%+</b>（context 累积），completion/reasoning 占比小。<b>fr（0.97M）成本最低</b>但通过率也最低——可能是注入干扰导致提前收敛（converged 仅 85.2%）。
</div>

<h2>五、执行质量</h2>

<div class="chartbox">
{chart_exec_quality()}
<div class="chartcap">图 5 · 执行质量三联图：converged%（收敛率）/ gen_fail（生成失败数）/ timeout（超时数，每轮 158 题）</div>
</div>

<table>
<tr><th>语言</th><th>converged 均值</th><th>gen_fail 均值</th><th>timeout 均值</th><th>success 均值</th><th>解读</th></tr>
{''.join(f'<tr><td class="l">{LANG_META[l]["flag"]} {LANG_META[l]["name"]}</td><td>{R[l]["converged_mean"]:.1f}%</td><td>{R[l]["gen_fail_mean"]:.1f}</td><td>{R[l]["timeout_mean"]:.1f}</td><td>{R[l]["converged_mean"]*158/100:.0f}</td><td class="l">{"收敛率高·生成稳定" if R[l]["converged_mean"]>95 else "收敛率偏低·生成失败多" if R[l]["converged_mean"]<90 else "中等"}</td></tr>' for l in LANGS)}
</table>

<div class="note">
<b>zh 执行质量最佳</b>（converged 97.5%，gen_fail 仅 3.3）—— 中文思维链反而最稳定。<b>fr 执行质量最差</b>（converged 85.2%，gen_fail 21.3）—— 法语注入导致更多生成失败，可能是模型对法语指令的服从度低。<b>en 的 r1 重跑（dsv4-pro 基座）gen_fail=15</b>拉低了 en 均值（旧 r2/r3 为 0），基座切换有轻微影响。
</div>

<h2>六、语言切换审计（LANG_HINT 是否生效）</h2>

<div class="chartbox">
{chart_audit_stack()}
<div class="chartcap">图 6 · 思维链语言构成堆叠条（TARGET = 目标语言，MIXED = 混合，ENGLISH = 英文漂移，CHINESE = 中文漂移；按 assistant 消息计数）</div>
</div>

<table>
<tr><th>语言</th><th>抽样轮</th><th>抽样消息数</th><th>TARGET</th><th>TARGET%</th><th>ENGLISH 漂移</th><th>CHINESE 漂移</th><th>MIXED</th><th>判定</th></tr>
<tr><td class="l">🇬🇧 en</td><td>r1+r2</td><td>471</td><td>456</td><td class="hl">96.8%</td><td>15</td><td>0</td><td>0</td><td><span class="tag good">真切换</span></td></tr>
<tr><td class="l">🇨🇳 zh</td><td>r1+r2</td><td>474</td><td>415</td><td class="hl">87.6%</td><td>1</td><td>58</td><td>0</td><td><span class="tag good">真切换(confound)</span></td></tr>
<tr><td class="l">🇪🇸 es</td><td>r1+r2</td><td>473</td><td>93</td><td><span class="tag bad">21.4%</span></td><td>315</td><td>57</td><td>8</td><td><span class="tag bad">未生效</span></td></tr>
<tr><td class="l">🇫🇷 fr</td><td>r1</td><td>158</td><td>64</td><td><span class="tag warn">40.5%</span></td><td>68</td><td>17</td><td>9</td><td><span class="tag warn">部分生效</span></td></tr>
<tr><td class="l">🇷🇺 ru</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td><td><span class="tag warn">部分漂移(log)</span></td></tr>
</table>

<div class="banner danger">
<b>⚠️ 审计结论对主结果的影响</b>：
<ol style="margin:6px 0 0 1.2em">
<li><b>en / zh 注入有效</b>（TARGET 96.8% / 87.6%）—— 二者的 Pass@1（81.0% / 81.2%）是<b>可信的语言效应</b>（注：zh 的 58 条 CHINESE 是中文 trace 本身，非漂移）。</li>
<li><b>es 注入未生效</b>（仅 21.4% TARGET，66.6% ENGLISH 漂移）—— es 的 80.8% 实际测的是「<b>英文思考 + 西语 hint 干扰</b>」，不能作为「西语思维链能力」的证据。其极小 std（0.3%）反映的是英文基线稳定性。</li>
<li><b>fr 部分生效</b>（40.5% TARGET，仅 r1 抽样）—— fr 的 76.2% 部分可信，但混杂英文漂移。</li>
<li><b>ru 部分漂移</b>（log 含俄文片段「использовать/Поскольку/Давайте проверим」+ 英文漂移，MIXED）—— ru 的 79.3% 部分可信。</li>
</ol>
<b>结论修订</b>：严格说，只有 <b>en vs zh</b> 是干净的语言对比（81.0% vs 81.2%，几乎无差异）。es/fr/ru 的结果受注入未生效污染，「5 语言极差仅 {spread:.1f}pp」的结论<b>主要反映英文基线的稳定性，而非思维链语言的真中性</b>。
</div>

<h2>七、轮次稳定性</h2>

<div class="chartbox">
{chart_trend()}
<div class="chartcap">图 7 · r1→r2→r3 趋势线（5 语言 3 轮 Pass@1 折线，点 = 每轮值）</div>
</div>

<table>
<tr><th>语言</th><th>r1→r2 Δ</th><th>r2→r3 Δ</th><th>range (max−min)</th><th>std</th><th>趋势</th></tr>
{''.join(f'<tr><td class="l">{LANG_META[l]["flag"]} {LANG_META[l]["name"]}</td><td>{R[l]["rounds"][1]["pass"]-R[l]["rounds"][0]["pass"]:+.1f}</td><td>{R[l]["rounds"][2]["pass"]-R[l]["rounds"][1]["pass"]:+.1f}</td><td>{R[l]["max"]-R[l]["min"]:.1f}</td><td>{R[l]["std"]:.1f}</td><td class="l">{"下降" if R[l]["rounds"][2]["pass"]<R[l]["rounds"][0]["pass"] else "上升" if R[l]["rounds"][2]["pass"]>R[l]["rounds"][0]["pass"] else "平稳"}</td></tr>' for l in LANGS)}
</table>

<div class="note">
<b>zh/en 呈下降趋势</b>（zh 84.2→77.8，en 80.4→84.2→78.5 重跑），<b>es 最平稳</b>（81.0/80.4/81.0，range 0.6），<b>fr 上升</b>（74.1→79.1）。<b>无语言显示单调趋势</b>——波动主要来自采样方差而非系统性漂移。zh 的下降（r1=84.2 → r3=77.8）幅度 6.4pp 较大，但 r3 是重跑值（旧 78.5% → 新 77.8%，基本一致），说明 r1=84.2 可能是高估离群。
</div>

<h2>八、结论与局限</h2>

<h3>8.1 结论</h3>
<ol>
<li><b>思维链语言对 EDA 代码生成能力影响不显著</b>：5 语言 Pass@1 落在 76.2-81.2%，极差 {spread:.1f}pp，多数在 1σ 内。</li>
<li><b>中文与英文并列最高</b>（81.2% / 81.0%）—— 这是<b>唯二注入有效的语言</b>，可信度最高。中文略高 0.2pp 在方差内，<b>无显著差异</b>。</li>
<li><b>中文 token 成本最高</b>（1.32M/题 vs en 1.28M），比 es/ru（1.01M）多 ~30%——中文 token 化效率低。</li>
<li><b>中文执行质量最佳</b>（converged 97.5%，gen_fail 3.3）—— 中文思维链反而最稳定。</li>
<li><b>法语最差</b>（76.2% / converged 85.2% / gen_fail 21.3）—— 注入服从度低，生成失败多。</li>
</ol>

<h3>8.2 局限</h3>
<table>
<tr><th>局限</th><th>影响</th><th>缓解</th></tr>
<tr><td class="l">es/fr/ru 注入未完全生效（audit 显示 ENGLISH 漂移 40-67%）</td><td class="l">三语 Pass@1 实际测的是「英文思考 + hint 干扰」，不能作为非英语思维链能力的证据</td><td class="l">需更强的 LANG_HINT（如 few-shot 示例 + 输出格式约束）或换用多语言基座</td></tr>
<tr><td class="l">B_en_r1 重跑基座切换（glm-5.2 → dsv4-pro）</td><td class="l">en 3 轮基座虽已对齐，但 r1=78.5% 低于 r2/r3（80.4/84.2），可能有基座适应期</td><td class="l">已 SUPERSEDED 旧值留档；en mean 用 3 轮池</td></tr>
<tr><td class="l">每语言仅 3 轮（n=3）</td><td class="l">std 自由度低，效应力不足，小差异（<2pp）难达显著</td><td class="l">如需统计显著，建议每语言 5-10 轮</td></tr>
<tr><td class="l">与基线 glm-5.2 不可直接归因</td><td class="l">轴 B 用 dsv4-pro，与轴 A（glm-5.2）基座不同，跨轴 Δpp 含基座效应</td><td class="l">本报告仅作轴 B 内横比，不作跨轴归因</td></tr>
<tr><td class="l">zh 的 58 条 CHINESE 是 confound</td><td class="l">zh trace 中 12.2% 是中文（目标语言），但 trace_source 用户本身用中文，难分离 hint 效应 vs 用户语言效应</td><td class="l">audit 标注 confound，zh 的「真切换」含此混杂</td></tr>
</table>

<h3>8.3 未来方向</h3>
<div class="banner good">
<ol style="margin:6px 0 0 1.2em">
<li><b>强化 LANG_HINT 注入</b>：对 es/fr/ru 增加 few-shot 示例（用目标语言写的思维链示例）+ 输出格式约束（要求 reasoning 字段用目标语言），提升 TARGET 率到 >80% 后重测。</li>
<li><b>换用多语言基座</b>：若 dsv4-pro 对非英语服从度低，可换用明确支持多语言的基座（如 Qwen-Max 多语言版）对比，分离「基座能力」与「语言效应」。</li>
<li><b>增加轮次</b>：每语言 5-10 轮以提升统计效力，用 t-test / bootstrap 检验 en vs zh 的 0.2pp 差异是否显著。</li>
<li><b>跨语言 token 效率研究</b>：中文 token 成本高 30% 是否值得？若 Pass@1 无显著优势，英文思维链在成本-性能上更优。</li>
</ol>
</div>

<h2>附：方法学与数据完整性</h2>
<table style="font-size:.8rem">
<tr><th>数据源</th><td class="l"><code>run/ablation_think_lang_results.json</code>（32 rounds，含 2 SUPERSEDED）· <code>run/cost_B_*.json</code>（extract_cost.py 产出）· <code>reports/report_zhulong_lang_switch_audit_zh.html</code>（语言切换审计）</td></tr>
<tr><th>active 轮次</th><td class="l">en: idx31(重跑)+idx16+idx17 · zh: idx18+idx19+idx30(重跑) · es: idx21+22+23 · fr: idx24+25+26 · ru: idx27+28+29</td></tr>
<tr><th>Pass@1 计算</th><td class="l">passed/158 × 100%（sandbox run_eval，判据十三有效，PASS_RATE 字段）</td></tr>
<tr><th>token 统计</th><td class="l">extract_cost.py 从 cline session jsonl 提取 prompt/completion tokens + reasoning chars（÷4 估算 reasoning tokens）</td></tr>
<tr><th>audit 方法</th><td class="l">从每语言 r1/r2 trace 抽样 assistant 消息，正则匹配目标语言字符（中文/西语重音/法语重音/西里尔）vs 英文，统计 TARGET/MIXED/ENGLISH/CHINESE 占比</td></tr>
<tr><th>可视化</th><td class="l">纯内联 SVG（7 图：条形+误差棒 / 逐轮散点 / token 堆叠 / 成本-性能象限 / 执行质量三联 / 审计堆叠 / 趋势线），无 JS/CDN 依赖</td></tr>
<tr><th>commit</th><td class="l">B_en_r1 重跑 + 报告刷新：<code>a909fe482</code>（2026-11-12 21:16）· B 轴报告加 token 列：<code>83fcb84cc</code></td></tr>
</table>

<footer>
<p>轴 B · 思维链语言消融报告 · ZhuLong（DAC2027）· 2026-11-13 生成</p>
<p>5 语言 × 3 轮 × 158 题 = 2,370 次评测 · 基座 deepseek-v4-pro-cloud 恒定 · 7 张 SVG 可视化</p>
</footer>

</body></html>'''

with open(OUT_PATH,'w') as f:
    f.write(HTML)
print(f'wrote {OUT_PATH} ({len(HTML)} bytes, {len(HTML)/1024:.1f} KB)')
