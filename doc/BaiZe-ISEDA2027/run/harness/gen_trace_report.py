#!/usr/bin/env python3
"""Generate report_harness_interaction_traces.html — 7-way harness feature comparison + 20pp gap analysis."""
import json, re, statistics, html
from pathlib import Path
from collections import defaultdict, Counter

HERE = Path(__file__).resolve().parent
DATA = json.load(open(HERE / "kimi_pilot_results.json"))
WD = Path("/dev/shm/harness_work/workdirs")
ORDER = ["cline-patched", "pi", "hermes", "opencode", "codex", "claude-code", "deepseek-harness"]
DISPLAY = {"cline-patched":"cline-patched","pi":"Pi","hermes":"Hermes","opencode":"opencode",
           "codex":"codex","claude-code":"claude-code","deepseek-harness":"deepseek-harness"}
COLORS = {"cline-patched":"#3fb950","pi":"#58a6ff","hermes":"#bc8cff","opencode":"#d29922",
          "codex":"#f0883e","claude-code":"#f85149","deepseek-harness":"#e6e6e6"}
ref_insts = sorted(set(e["instance_id"] for e in DATA if e["harness"]=="cline-patched"))
subset = [e for e in DATA if e["instance_id"] in set(ref_insts)]

# --- Compute stats ---
stats = {}
for h in ORDER:
    entries = [e for e in subset if e["harness"]==h]
    s = {"total":len(entries),"resolved":0,"pbf":0,"quota":0,
         "walls_all":[],"walls_res":[],"walls_fail":[],
         "patch_sizes_all":[],"patch_sizes_res":[],"patch_sizes_fail":[],
         "fail_modes":Counter(),"returncodes":Counter(),
         "repos":defaultdict(lambda:{"total":0,"resolved":0}),
         "files_touched":[],"lines_added":[],"lines_removed":[],"patches_found":0}
    for e in entries:
        hr = e.get("harness_result",{}); cls = e.get("classification","")
        wall = hr.get("wall_s",0); rc = hr.get("returncode",0)
        s["returncodes"][rc] += 1; s["walls_all"].append(wall)
        s["repos"][e["repo"]]["total"] += 1
        tail = hr.get("stdout_tail","") or ""
        m = re.search(r"model_patch:\s*(\d+)\s*bytes", tail)
        patch_sz = int(m.group(1)) if m else 0
        s["patch_sizes_all"].append(patch_sz)
        if hr.get("quota_blocked"): s["quota"]+=1; s["fail_modes"]["quota_blocked"]+=1
        elif cls=="resolved":
            s["resolved"]+=1; s["walls_res"].append(wall); s["patch_sizes_res"].append(patch_sz)
            s["repos"][e["repo"]]["resolved"]+=1
        elif cls=="patch-but-failed":
            s["pbf"]+=1; s["walls_fail"].append(wall); s["patch_sizes_fail"].append(patch_sz)
            ev = hr.get("eval",{})
            if patch_sz==0: s["fail_modes"]["no_patch"]+=1
            elif not ev.get("patch_applied",False): s["fail_modes"]["patch_not_applied"]+=1
            elif ev.get("f2p_pass",0)<ev.get("f2p_total",1): s["fail_modes"]["f2p_fail"]+=1
            else: s["fail_modes"]["p2p_fail"]+=1
        else: s["fail_modes"]["other"]+=1; s["walls_fail"].append(wall); s["patch_sizes_fail"].append(patch_sz)
        # Patch characteristics from predictions files
        inst = e["instance_id"]; h_slug = h.replace("-","_"); inst_slug = inst.replace("/","__")
        fpath = WD / f"predictions_kimi_{h_slug}_{inst_slug}.json"
        if not fpath.exists(): fpath = WD / f"predictions_{h_slug}_{inst_slug}.json"
        if fpath.exists():
            try:
                pd = json.load(open(fpath))
                patch = (pd[0] if isinstance(pd,list) else pd).get("model_patch","")
                if patch:
                    s["patches_found"] += 1
                    diff_files = set(); added = 0; removed = 0
                    for line in patch.split("\n"):
                        if line.startswith("+++ "):
                            f = line[4:].strip()
                            if f != "/dev/null": diff_files.add(f.lstrip("b/"))
                        elif line.startswith("+") and not line.startswith("+++"): added += 1
                        elif line.startswith("-") and not line.startswith("---"): removed += 1
                    s["files_touched"].append(len(diff_files))
                    s["lines_added"].append(added); s["lines_removed"].append(removed)
            except: pass
    stats[h] = s

# Instance-level
inst_results = defaultdict(dict)
for e in subset: inst_results[e["instance_id"]][e["harness"]] = (e.get("classification")=="resolved")
res_sets = {h: set(i for i,c in inst_results.items() if c.get(h)) for h in ORDER}
all_pass = [i for i,v in inst_results.items() if all(v.values())]
none_pass = [i for i,v in inst_results.items() if not any(v.values())]
some_pass = [i for i,v in inst_results.items() if any(v.values()) and not all(v.values())]

# Architecture info (from run_harness.py source code, path:line cited)
ARCH = {
    "cline-patched": {"entry":"cline CLI v4.1.21 (bun)","invocation":"-c <cwd> -m <model> -k <key> --auto-approve true --json <prompt>",
                      "autonomy":"Full auto (--auto-approve true)","provider":"OpenAI @ gw_proxy","src":"run_harness.py:115-154"},
    "pi": {"entry":"pi CLI v0.2.15 (bun)","invocation":"-p (print mode) --provider gw --model <model> --api-key <key> <prompt>",
           "autonomy":"Full auto (print mode, non-interactive)","provider":"gw custom @ gw_proxy","src":"run_harness.py:378-419"},
    "hermes": {"entry":"hermes CLI (NousResearch/hermes-agent)","invocation":"-z<prompt> (oneshot) --provider kimi-proxy --model <model> --yolo",
               "autonomy":"Full auto (--yolo skip approvals), max_turns=50","provider":"kimi-proxy @ gw_proxy","src":"run_harness.py:422-469"},
    "opencode": {"entry":"opencode CLI v1.18.27","invocation":"opencode run --dir <cwd> --model <model> --auto <prompt>",
                 "autonomy":"Full auto (--auto approves tool calls)","provider":"@ai-sdk/openai-compatible @ gw_proxy","src":"run_harness.py:190-215"},
    "codex": {"entry":"codex CLI v0.94.0 (pinned)","invocation":"codex exec --cd <cwd> --model <model> --sandbox workspace-write --json <prompt>",
              "autonomy":"Sandboxed (workspace-write), no git check","provider":"OpenAI chat @ gw_proxy","src":"run_harness.py:157-187"},
    "claude-code": {"entry":"claude-code (leaked src, bun)","invocation":"bun run cli.tsx -- -p <prompt> --model <model> --bare --dangerously-skip-permissions",
                    "autonomy":"Full auto (skip permissions, print mode)","provider":"Anthropic SDK @ gw_proxy","src":"run_harness.py:235-298"},
    "deepseek-harness": {"entry":"deepseek_harness Python SDK","invocation":"DeepSeekHarness(provider, model, base_url, cwd).run(prompt)",
                         "autonomy":"SDK-managed (profile=sdk-minimal)","provider":"deepseek-official @ gw_proxy:9091","src":"run_harness.py:301-375"},
}

def svg_resolve_bars():
    ml, mb, mt = 55, 40, 30; bw, gap = 70, 30; n = len(ORDER)
    w = ml + n*(bw+gap) - gap + 20; h = 320
    p = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;">']
    for pct in [0,20,40,60,80,100]:
        gy = h-mb-(pct/100)*(h-mb-mt)
        p.append(f'<line x1="{ml}" y1="{gy}" x2="{w-20}" y2="{gy}" stroke="#30363d" stroke-width="0.5"/>')
        p.append(f'<text x="{ml-8}" y="{gy+4}" fill="#8b949e" font-size="10" text-anchor="end">{pct}%</text>')
    for i, h_key in enumerate(ORDER):
        s = stats[h_key]; rate = s["resolved"]/s["total"]*100
        x = ml + i*(bw+gap); bh = (rate/100)*(h-mb-mt); y = h-mb-bh; col = COLORS[h_key]
        p.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" fill="{col}" rx="3"/>')
        p.append(f'<text x="{x+bw/2}" y="{y-6}" fill="{col}" font-size="13" font-weight="bold" text-anchor="middle">{rate:.1f}%</text>')
        p.append(f'<text x="{x+bw/2}" y="{h-mb+16}" fill="#c9d1d9" font-size="9" text-anchor="middle">{DISPLAY[h_key]}</text>')
        p.append(f'<text x="{x+bw/2}" y="{h-mb+28}" fill="#8b949e" font-size="8" text-anchor="middle">{s["resolved"]}/{s["total"]}</text>')
    return "\n".join(p) + "</svg>"

def svg_failure_modes():
    cats = ["no_patch","f2p_fail","p2p_fail"]; cat_labels = ["No patch","F2P fail","P2P fail"]
    ml, mb, mt = 100, 35, 25; bw, gap = 45, 12; n = len(ORDER)
    w = ml + n*(len(cats)*bw + gap) - gap + 20; h = 260; max_v = 15
    p = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;">']
    for v in [0,5,10,15]:
        gy = h-mb-(v/max_v)*(h-mb-mt)
        p.append(f'<line x1="{ml}" y1="{gy}" x2="{w-20}" y2="{gy}" stroke="#30363d" stroke-width="0.5"/>')
        p.append(f'<text x="{ml-8}" y="{gy+4}" fill="#8b949e" font-size="10" text-anchor="end">{v}</text>')
    for i, h_key in enumerate(ORDER):
        s = stats[h_key]; fm = s["fail_modes"]; x = ml + i*(len(cats)*bw + gap)
        for j, cat in enumerate(cats):
            val = fm.get(cat, 0); bh = (val/max_v)*(h-mb-mt)
            p.append(f'<rect x="{x+j*bw}" y="{h-mb-bh}" width="{bw-2}" height="{bh}" fill="{COLORS[h_key]}" opacity="{0.9-j*0.2}" rx="2"/>')
            if val > 0: p.append(f'<text x="{x+j*bw+(bw-2)/2}" y="{h-mb-bh-4}" fill="{COLORS[h_key]}" font-size="9" text-anchor="middle">{val}</text>')
        p.append(f'<text x="{x+len(cats)*bw/2}" y="{h-mb+16}" fill="#c9d1d9" font-size="8" text-anchor="middle">{DISPLAY[h_key]}</text>')
    for j, label in enumerate(cat_labels):
        p.append(f'<text x="{ml+j*bw+(bw-2)/2}" y="{mt-6}" fill="#8b949e" font-size="8" text-anchor="middle">{label}</text>')
    return "\n".join(p) + "</svg>"

def svg_wall_time():
    ml, mb, mt = 55, 35, 25; bw, gap = 70, 30; n = len(ORDER)
    max_w = 900; w = ml + n*(bw+gap) - gap + 20; h = 280
    p = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;">']
    for v in [0,200,400,600,800]:
        gy = h-mb-(v/max_w)*(h-mb-mt)
        p.append(f'<line x1="{ml}" y1="{gy}" x2="{w-20}" y2="{gy}" stroke="#30363d" stroke-width="0.5"/>')
        p.append(f'<text x="{ml-8}" y="{gy+4}" fill="#8b949e" font-size="10" text-anchor="end">{v}s</text>')
    for i, h_key in enumerate(ORDER):
        s = stats[h_key]
        avg_res = statistics.mean(s["walls_res"]) if s["walls_res"] else 0
        avg_fail = statistics.mean(s["walls_fail"]) if s["walls_fail"] else 0
        x = ml + i*(bw+gap); col = COLORS[h_key]
        h_res = (avg_res/max_w)*(h-mb-mt); h_fail = (avg_fail/max_w)*(h-mb-mt)
        p.append(f'<rect x="{x}" y="{h-mb-h_res}" width="{bw*0.42}" height="{h_res}" fill="{col}" opacity="0.9" rx="2"/>')
        p.append(f'<rect x="{x+bw*0.48}" y="{h-mb-h_fail}" width="{bw*0.42}" height="{h_fail}" fill="{col}" opacity="0.4" rx="2"/>')
        p.append(f'<text x="{x+bw/2}" y="{h-mb+16}" fill="#c9d1d9" font-size="9" text-anchor="middle">{DISPLAY[h_key]}</text>')
    p.append(f'<rect x="{ml+5}" y="{mt-2}" width="10" height="10" fill="#58a6ff" opacity="0.9"/><text x="{ml+20}" y="{mt+6}" fill="#8b949e" font-size="9">resolved</text>')
    p.append(f'<rect x="{ml+75}" y="{mt-2}" width="10" height="10" fill="#58a6ff" opacity="0.4"/><text x="{ml+90}" y="{mt+6}" fill="#8b949e" font-size="9">failed</text>')
    return "\n".join(p) + "</svg>"

def svg_patch_scope():
    ml, mb, mt = 55, 35, 25; bw, gap = 70, 30; n = len(ORDER)
    max_v = 6; w = ml + n*(bw+gap) - gap + 20; h = 260
    p = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;">']
    for v in [0,1,2,3,4,5]:
        gy = h-mb-(v/max_v)*(h-mb-mt)
        p.append(f'<line x1="{ml}" y1="{gy}" x2="{w-20}" y2="{gy}" stroke="#30363d" stroke-width="0.5"/>')
        p.append(f'<text x="{ml-8}" y="{gy+4}" fill="#8b949e" font-size="10" text-anchor="end">{v}</text>')
    for i, h_key in enumerate(ORDER):
        s = stats[h_key]
        avg_files = statistics.mean(s["files_touched"]) if s["files_touched"] else 0
        avg_add = statistics.mean(s["lines_added"]) if s["lines_added"] else 0
        x = ml + i*(bw+gap); h_files = (avg_files/max_v)*(h-mb-mt); col = COLORS[h_key]
        p.append(f'<rect x="{x}" y="{h-mb-h_files}" width="{bw}" height="{h_files}" fill="{col}" rx="3"/>')
        p.append(f'<text x="{x+bw/2}" y="{h-mb-h_files-5}" fill="{col}" font-size="10" font-weight="bold" text-anchor="middle">{avg_files:.1f}</text>')
        p.append(f'<text x="{x+bw/2}" y="{h-mb+16}" fill="#c9d1d9" font-size="9" text-anchor="middle">{DISPLAY[h_key]}</text>')
        p.append(f'<text x="{x+bw/2}" y="{h-mb+28}" fill="#8b949e" font-size="8" text-anchor="middle">+{avg_add:.0f} lines</text>')
    return "\n".join(p) + "</svg>"

def svg_speed_vs_accuracy():
    mt, mb, ml = 30, 45, 55; w, h = 520, 350
    p = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;">']
    max_wall = 900
    for pct in [0,20,40,60,80]:
        gy = h-mb-(pct/100)*(h-mb-mt)
        p.append(f'<line x1="{ml}" y1="{gy}" x2="{w-10}" y2="{gy}" stroke="#30363d" stroke-width="0.5"/>')
        p.append(f'<text x="{ml-8}" y="{gy+4}" fill="#8b949e" font-size="10" text-anchor="end">{pct}%</text>')
    for v in [0,300,600,900]:
        gx = ml+(v/max_wall)*(w-ml-10)
        p.append(f'<line x1="{gx}" y1="{mt}" x2="{gx}" y2="{h-mb}" stroke="#30363d" stroke-width="0.5"/>')
        p.append(f'<text x="{gx}" y="{h-mb+16}" fill="#8b949e" font-size="10" text-anchor="middle">{v}s</text>')
    p.append(f'<text x="{ml+(w-ml-10)/2}" y="{h-5}" fill="#8b949e" font-size="10" text-anchor="middle">Avg wall time (s)</text>')
    for h_key in ORDER:
        s = stats[h_key]; rate = s["resolved"]/s["total"]*100; avg_w = statistics.mean(s["walls_all"])
        cx = ml + (min(avg_w,max_wall)/max_wall)*(w-ml-10); cy = h-mb-(rate/100)*(h-mb-mt); col = COLORS[h_key]
        p.append(f'<circle cx="{cx}" cy="{cy}" r="8" fill="{col}" opacity="0.8"/>')
        p.append(f'<text x="{cx}" y="{cy-12}" fill="{col}" font-size="9" text-anchor="middle">{DISPLAY[h_key]}</text>')
    return "\n".join(p) + "</svg>"

def svg_wall_time():
    ml, mb, mt = 55, 35, 25; bw, gap = 70, 30; n = len(ORDER)
    max_w = 900; w = ml + n*(bw+gap) - gap + 20; h = 280
    p = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;">']
    for v in [0,200,400,600,800]:
        gy = h-mb-(v/max_w)*(h-mb-mt)
        p.append(f'<line x1="{ml}" y1="{gy}" x2="{w-20}" y2="{gy}" stroke="#30363d" stroke-width="0.5"/>')
        p.append(f'<text x="{ml-8}" y="{gy+4}" fill="#8b949e" font-size="10" text-anchor="end">{v}s</text>')
    for i, h_key in enumerate(ORDER):
        s = stats[h_key]
        avg_res = statistics.mean(s["walls_res"]) if s["walls_res"] else 0
        avg_fail = statistics.mean(s["walls_fail"]) if s["walls_fail"] else 0
        x = ml + i*(bw+gap); col = COLORS[h_key]
        h_res = (avg_res/max_w)*(h-mb-mt); h_fail = (avg_fail/max_w)*(h-mb-mt)
        p.append(f'<rect x="{x}" y="{h-mb-h_res}" width="{bw*0.42}" height="{h_res}" fill="{col}" opacity="0.9" rx="2"/>')
        p.append(f'<rect x="{x+bw*0.48}" y="{h-mb-h_fail}" width="{bw*0.42}" height="{h_fail}" fill="{col}" opacity="0.4" rx="2"/>')
        p.append(f'<text x="{x+bw/2}" y="{h-mb+16}" fill="#c9d1d9" font-size="9" text-anchor="middle">{DISPLAY[h_key]}</text>')
    p.append(f'<rect x="{ml+5}" y="{mt-2}" width="10" height="10" fill="#58a6ff" opacity="0.9"/><text x="{ml+20}" y="{mt+6}" fill="#8b949e" font-size="9">resolved</text>')
    p.append(f'<rect x="{ml+75}" y="{mt-2}" width="10" height="10" fill="#58a6ff" opacity="0.4"/><text x="{ml+90}" y="{mt+6}" fill="#8b949e" font-size="9">failed</text>')
    return "\n".join(p) + "</svg>"

CSS = """
body{background:#0d1117;color:#c9d1d9;font-family:-apple-system,sans-serif;margin:0;padding:0;line-height:1.6}
.container{max-width:1400px;margin:0 auto;padding:20px}
h1{color:#f0f6fc;font-size:1.8em;border-bottom:1px solid #30363d;padding-bottom:10px}
h2{color:#58a6ff;font-size:1.3em;margin-top:2em;border-bottom:1px solid #21262c;padding-bottom:5px}
h3{color:#c9d1d9;font-size:1.1em;margin-top:1.5em}
table{border-collapse:collapse;width:100%;margin:1em 0;font-size:13px}
th{background:#161b22;color:#f0f6fc;padding:8px 10px;text-align:left;border:1px solid #30363d}
td{padding:6px 10px;border:1px solid #21262c;vertical-align:top}
tr:nth-child(even){background:#161b22}
.chart-box{background:#161b22;border:1px solid #30363d;border-radius:6px;padding:15px;margin:1em 0}
.note{background:#1c2128;border-left:3px solid #58a6ff;padding:10px 15px;margin:1em 0;border-radius:0 6px 6px 0}
.warn{background:#1c2128;border-left:3px solid #d29922;padding:10px 15px;margin:1em 0;border-radius:0 6px 6px 0}
.tag{display:inline-block;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:bold}
.tag-green{background:#1a3a2a;color:#3fb950}.tag-blue{background:#1a2a3a;color:#58a6ff}
.tag-yellow{background:#3a3a1a;color:#d29922}.tag-red{background:#3a1a1a;color:#f85149}
.tag-orange{background:#3a2a1a;color:#f0883e}
code{background:#1c2128;padding:2px 6px;border-radius:4px;font-size:12px;color:#f0883e}
.small{font-size:11px;color:#8b949e}
.tl-dr{background:#1a1f2e;border:2px solid #30363d;border-radius:8px;padding:15px;margin:1em 0}
.tl-dr h2{border:none;margin-top:0}
"""

def build_comparison_table():
    rows = ""
    for h in ORDER:
        s = stats[h]; a = ARCH[h]; col = COLORS[h]
        rate = s["resolved"]/s["total"]*100
        avg_w = statistics.mean(s["walls_all"]); med_w = statistics.median(s["walls_all"])
        avg_patch = statistics.mean(s["patch_sizes_all"])
        avg_files = statistics.mean(s["files_touched"]) if s["files_touched"] else 0
        avg_add = statistics.mean(s["lines_added"]) if s["lines_added"] else 0
        fm = s["fail_modes"]; no_patch = fm.get("no_patch",0); f2p = fm.get("f2p_fail",0)
        timeouts = sum(1 for w in s["walls_all"] if w > 1700)
        if s["resolved"] >= 16: dom = "Low fail rate"
        elif no_patch >= 7: dom = f"No patch ({no_patch}/30)"
        elif f2p >= 10: dom = f"Wrong fix (F2P {f2p}/30)"
        elif timeouts >= 5: dom = f"Timeout ({timeouts}/30)"
        else: dom = f"F2P fail ({f2p}/30)"
        tc = "tag-green" if rate>=55 else "tag-blue" if rate>=50 else "tag-yellow" if rate>=45 else "tag-orange" if rate>=42 else "tag-red"
        rows += f"""<tr>
<td><span class="tag {tc}">{DISPLAY[h]}</span></td>
<td><code>{html.escape(a['entry'])}</code><br><span class="small">{html.escape(a['src'])}</span></td>
<td>{html.escape(a['autonomy'])}</td>
<td>{html.escape(a['provider'])}</td>
<td>{rate:.1f}%<br><span class="small">{s['resolved']}/{s['total']}</span></td>
<td>{avg_w:.0f}s<br><span class="small">med {med_w:.0f}s</span></td>
<td>{avg_files:.1f} files<br><span class="small">+{avg_add:.0f} lines</span></td>
<td>{avg_patch:.0f}B</td>
<td>{dom}<br><span class="small">no_patch={no_patch} f2p={f2p} timeout={timeouts}</span></td>
<td>{s['patches_found']}/30</td></tr>"""
    return f"""<table><thead><tr><th>Harness</th><th>Entry / Source</th><th>Autonomy</th><th>Provider</th><th>Resolve Rate</th><th>Avg Wall</th><th>Patch Scope</th><th>Avg Patch Size</th><th>Dominant Failure</th><th>Patches Found</th></tr></thead><tbody>{rows}</tbody></table>"""


def build_html():
    P = []
    P.append("<!DOCTYPE html><html><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1'>")
    P.append(f"<title>Harness Interaction Traces & Feature Comparison (7-way x 30)</title>")
    P.append(f"<style>{CSS}</style></head><body><div class='container'>")
    P.append("<h1>Harness Interaction Traces &amp; Feature Comparison</h1>")
    P.append("<p class='small'>7-way SWE-bench Lite cross-eval | 30 instances x 7 harnesses | backbone: kimi-k2.6-cloud | 2026-10-08</p>")
    return "\n".join(P)

