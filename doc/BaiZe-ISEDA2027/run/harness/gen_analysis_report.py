#!/usr/bin/env python3
"""Generate report_harness_swebench_analysis.html — deep analysis of 30x7 SWE-bench cross-eval.

Per operator instruction 2026-10-08: deeper than SWEBENCH_COMPARE.html — includes
failure mode analysis, cost analysis, harness architecture correlation, BaiZe implications.
Self-contained HTML with inline SVG charts from real data.
"""
import json, html, math
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

HERE = Path(__file__).resolve().parent
RESULTS_FILE = HERE / "kimi_pilot_results.json"
MODEL = "kimi-k2.6-cloud"
GATEWAY = "http://agi-gateway.cxmt.com/cloud/v1"
HARNESS_ORDER = ["cline-patched", "codex", "opencode", "claude-code", "deepseek-harness", "pi", "hermes"]
DISPLAY = {
    "cline-patched": "cline-patched", "codex": "codex", "opencode": "opencode",
    "claude-code": "claude-code", "deepseek-harness": "deepseek-harness",
    "pi": "Pi", "hermes": "Hermes Agent",
}
COLORS = {
    "cline-patched": "#6c5ce7", "codex": "#e17055", "opencode": "#00b894",
    "claude-code": "#d63031", "deepseek-harness": "#fdcb6e", "pi": "#0984e3", "hermes": "#a29bfe",
}
TIMEOUT_THRESHOLD = 1790

def load_data():
    data = json.loads(RESULTS_FILE.read_text())
    target_ids = set(e["instance_id"] for e in data if e.get("harness") == "cline-patched")
    return [e for e in data if e["instance_id"] in target_ids]

def compute_stats(data):
    stats = {}
    for h in HARNESS_ORDER:
        entries = [e for e in data if e.get("harness") == h]
        resolved = sum(1 for e in entries if e.get("classification") == "resolved")
        pbf = sum(1 for e in entries if e.get("classification") == "patch-but-failed")
        blocked = sum(1 for e in entries if e.get("classification") == "blocked")
        scored = resolved + pbf
        walls = [e.get("harness_result", {}).get("wall_s", 0) for e in entries
                 if isinstance(e.get("harness_result", {}).get("wall_s"), (int, float))]
        rcs = Counter(e.get("harness_result", {}).get("returncode") for e in entries)
        timeouts = sum(1 for w in walls if w >= TIMEOUT_THRESHOLD)
        patch_sizes = []
        for e in entries:
            stdout = e.get("harness_result", {}).get("stdout_tail", "")
            if "model_patch:" in stdout:
                try:
                    ps = stdout.split("model_patch:")[1].split("bytes")[0].strip()
                    patch_sizes.append(int(ps))
                except:
                    pass
        f2p_only = p2p_only = both_fail = no_patch = 0
        for e in entries:
            if e.get("classification") != "patch-but-failed":
                continue
            ev = e.get("harness_result", {}).get("eval", {})
            f2p_pass, f2p_total = ev.get("f2p_pass", 0), ev.get("f2p_total", 0)
            p2p_pass, p2p_total = ev.get("p2p_pass", 0), ev.get("p2p_total", 0)
            pa = ev.get("patch_applied", False)
            if not pa:
                no_patch += 1
            elif f2p_pass < f2p_total and p2p_pass >= p2p_total:
                f2p_only += 1
            elif f2p_pass >= f2p_total and p2p_pass < p2p_total:
                p2p_only += 1
            elif f2p_pass < f2p_total and p2p_pass < p2p_total:
                both_fail += 1
        stats[h] = {
            "total": len(entries), "resolved": resolved, "pbf": pbf, "blocked": blocked,
            "scored": scored, "rate": 100*resolved/scored if scored else 0,
            "walls": walls, "avg_wall": sum(walls)/len(walls) if walls else 0,
            "total_wall": sum(walls) if walls else 0,
            "min_wall": min(walls) if walls else 0, "max_wall": max(walls) if walls else 0,
            "rcs": dict(rcs), "timeouts": timeouts,
            "avg_patch": sum(patch_sizes)/len(patch_sizes) if patch_sizes else 0,
            "f2p_only": f2p_only, "p2p_only": p2p_only, "both_fail": both_fail, "no_patch": no_patch,
        }
    return stats

def compute_instance_analysis(data):
    inst = defaultdict(dict)
    for e in data:
        inst[e["instance_id"]][e["harness"]] = e.get("classification")
    result = {}
    for iid in sorted(inst.keys()):
        r = inst[iid]
        res = sum(1 for v in r.values() if v == "resolved")
        pbf = sum(1 for v in r.values() if v == "patch-but-failed")
        result[iid] = {"resolved": res, "pbf": pbf, "other": 7-res-pbf, "repo": iid.split("__")[0]}
    return result

def compute_repo_analysis(data):
    repos = defaultdict(lambda: defaultdict(list))
    for e in data:
        repos[e["repo"]][e["harness"]].append(e)
    result = {}
    for repo in sorted(repos.keys()):
        result[repo] = {}
        for h in HARNESS_ORDER:
            entries = repos[repo][h]
            if entries:
                resolved = sum(1 for e in entries if e.get("classification") == "resolved")
                result[repo][h] = {"resolved": resolved, "total": len(entries),
                                   "rate": 100*resolved/len(entries)}
    return result

def svg_bar_chart(stats, width=600, height=350):
    bar_h = 38
    margin_l, margin_r, margin_t, margin_b = 140, 60, 30, 40
    chart_w = width - margin_l - margin_r
    n = len(HARNESS_ORDER)
    chart_h = n * bar_h + 10
    total_h = chart_h + margin_t + margin_b
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{total_h}" viewBox="0 0 {width} {total_h}">']
    for pct in range(0, 101, 20):
        x = margin_l + chart_w * pct / 100
        parts.append(f'<line x1="{x}" y1="{margin_t}" x2="{x}" y2="{margin_t+chart_h}" stroke="#ddd" stroke-width="1"/>')
        parts.append(f'<text x="{x}" y="{total_h-15}" text-anchor="middle" font-size="11" fill="#666">{pct}%</text>')
    parts.append(f'<line x1="{margin_l}" y1="{margin_t}" x2="{margin_l}" y2="{margin_t+chart_h}" stroke="#333" stroke-width="1"/>')
    for i, h in enumerate(HARNESS_ORDER):
        s = stats[h]
        y = margin_t + i * bar_h + 5
        rate = s["rate"]
        bw = chart_w * rate / 100
        color = COLORS[h]
        parts.append(f'<rect x="{margin_l}" y="{y}" width="{bw:.1f}" height="{bar_h-10}" fill="{color}" rx="3"/>')
        parts.append(f'<text x="{margin_l-8}" y="{y+bar_h/2-1}" text-anchor="end" font-size="12" font-weight="bold" fill="#333">{DISPLAY[h]}</text>')
        parts.append(f'<text x="{margin_l+bw+5:.1f}" y="{y+bar_h/2-1}" font-size="12" fill="#333">{s["resolved"]}/{s["scored"]} ({rate:.1f}%)</text>')
    parts.append('</svg>')
    return "\n".join(parts)

def svg_stacked_failure(stats, width=600, height=350):
    bar_h = 38
    margin_l, margin_r, margin_t, margin_b = 140, 10, 30, 40
    chart_w = width - margin_l - margin_r
    n = len(HARNESS_ORDER)
    chart_h = n * bar_h + 10
    total_h = chart_h + margin_t + margin_b
    max_total = 30
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{total_h}" viewBox="0 0 {width} {total_h}">']
    for cnt in range(0, 31, 5):
        x = margin_l + chart_w * cnt / max_total
        parts.append(f'<line x1="{x}" y1="{margin_t}" x2="{x}" y2="{margin_t+chart_h}" stroke="#ddd" stroke-width="1"/>')
        parts.append(f'<text x="{x}" y="{total_h-15}" text-anchor="middle" font-size="11" fill="#666">{cnt}</text>')
    parts.append(f'<line x1="{margin_l}" y1="{margin_t}" x2="{margin_l}" y2="{margin_t+chart_h}" stroke="#333" stroke-width="1"/>')
    cat_colors = {"resolved": "#00b894", "f2p_only": "#fdcb6e", "p2p_only": "#e17055",
                  "both_fail": "#d63031", "no_patch": "#636e72", "blocked": "#b2bec3", "timeout": "#2d3436"}
    for i, h in enumerate(HARNESS_ORDER):
        s = stats[h]
        y = margin_t + i * bar_h + 5
        x = margin_l
        cats = [("resolved", s["resolved"]), ("f2p_only", s["f2p_only"]), ("p2p_only", s["p2p_only"]),
                ("both_fail", s["both_fail"]), ("no_patch", s["no_patch"]), ("blocked", s["blocked"]),
                ("timeout", s["timeouts"])]
        for cat, val in cats:
            if val > 0:
                bw = chart_w * val / max_total
                parts.append(f'<rect x="{x:.1f}" y="{y}" width="{bw:.1f}" height="{bar_h-10}" fill="{cat_colors[cat]}" rx="1"/>')
                if bw > 20:
                    parts.append(f'<text x="{x+bw/2:.1f}" y="{y+bar_h/2-1}" text-anchor="middle" font-size="10" fill="#fff" font-weight="bold">{val}</text>')
                x += bw
        parts.append(f'<text x="{margin_l-8}" y="{y+bar_h/2-1}" text-anchor="end" font-size="12" font-weight="bold" fill="#333">{DISPLAY[h]}</text>')
    parts.append('</svg>')
    cat_labels = {"resolved": "Resolved", "f2p_only": "FAIL_TO_PASS only", "p2p_only": "PASS_TO_PASS only",
                  "both_fail": "Both fail", "no_patch": "No patch", "blocked": "Blocked", "timeout": "Timeout"}
    legend = ['<svg xmlns="http://www.w3.org/2000/svg" width="600" height="30">']
    lx = 10
    for cat in ["resolved", "f2p_only", "p2p_only", "both_fail", "no_patch", "blocked", "timeout"]:
        legend.append(f'<rect x="{lx}" y="5" width="12" height="12" fill="{cat_colors[cat]}"/>')
        legend.append(f'<text x="{lx+16}" y="15" font-size="11" fill="#333">{cat_labels[cat]}</text>')
        lx += len(cat_labels[cat]) * 7 + 30
    legend.append('</svg>')
    return "\n".join(parts) + "\n" + "\n".join(legend)

def svg_scatter_wall_vs_rate(stats, width=600, height=400):
    margin_l, margin_r, margin_t, margin_b = 60, 30, 30, 50
    chart_w = width - margin_l - margin_r
    chart_h = height - margin_t - margin_b
    max_wall = 1000
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">']
    for pct in range(0, 101, 20):
        y = margin_t + chart_h * (1 - pct/100)
        parts.append(f'<line x1="{margin_l}" y1="{y:.1f}" x2="{margin_l+chart_w}" y2="{y:.1f}" stroke="#eee" stroke-width="1"/>')
        parts.append(f'<text x="{margin_l-8}" y="{y+4:.1f}" text-anchor="end" font-size="10" fill="#666">{pct}%</text>')
    for sec in range(0, 1001, 200):
        x = margin_l + chart_w * sec / max_wall
        parts.append(f'<line x1="{x:.1f}" y1="{margin_t}" x2="{x:.1f}" y2="{margin_t+chart_h}" stroke="#eee" stroke-width="1"/>')
        parts.append(f'<text x="{x:.1f}" y="{margin_t+chart_h+15}" text-anchor="middle" font-size="10" fill="#666">{sec}s</text>')
    parts.append(f'<line x1="{margin_l}" y1="{margin_t}" x2="{margin_l}" y2="{margin_t+chart_h}" stroke="#333"/>')
    parts.append(f'<line x1="{margin_l}" y1="{margin_t+chart_h}" x2="{margin_l+chart_w}" y2="{margin_t+chart_h}" stroke="#333"/>')
    parts.append(f'<text x="{margin_l+chart_w/2}" y="{height-10}" text-anchor="middle" font-size="12" fill="#333">Avg Wall Time (seconds)</text>')
    parts.append(f'<text x="15" y="{margin_t+chart_h/2}" text-anchor="middle" font-size="12" fill="#333" transform="rotate(-90 15 {margin_t+chart_h/2})">Resolve Rate (%)</text>')
    for h in HARNESS_ORDER:
        s = stats[h]
        x = margin_l + chart_w * min(s["avg_wall"], max_wall) / max_wall
        y = margin_t + chart_h * (1 - s["rate"]/100)
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="{COLORS[h]}" opacity="0.8"/>')
        parts.append(f'<text x="{x+12:.1f}" y="{y+4:.1f}" font-size="11" fill="#333" font-weight="bold">{DISPLAY[h]}</text>')
    parts.append('</svg>')
    return "\n".join(parts)

def svg_repo_comparison(repo_analysis, width=600, height=300):
    margin_l, margin_r, margin_t, margin_b = 100, 10, 40, 50
    chart_w = width - margin_l - margin_r
    chart_h = height - margin_t - margin_b
    repos = sorted(repo_analysis.keys())
    n_repos = len(repos)
    group_w = chart_w / n_repos
    bar_w = group_w / (len(HARNESS_ORDER) + 1)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">']
    for pct in range(0, 101, 20):
        y = margin_t + chart_h * (1 - pct/100)
        parts.append(f'<line x1="{margin_l}" y1="{y:.1f}" x2="{margin_l+chart_w}" y2="{y:.1f}" stroke="#eee" stroke-width="1"/>')
        parts.append(f'<text x="{margin_l-8}" y="{y+4:.1f}" text-anchor="end" font-size="10" fill="#666">{pct}%</text>')
    parts.append(f'<line x1="{margin_l}" y1="{margin_t}" x2="{margin_l}" y2="{margin_t+chart_h}" stroke="#333"/>')
    parts.append(f'<line x1="{margin_l}" y1="{margin_t+chart_h}" x2="{margin_l+chart_w}" y2="{margin_t+chart_h}" stroke="#333"/>')
    for ri, repo in enumerate(repos):
        gx = margin_l + ri * group_w
        short = repo.replace("django/django", "django").replace("sympy/sympy", "sympy")
        parts.append(f'<text x="{gx+group_w/2}" y="{margin_t+chart_h+18}" text-anchor="middle" font-size="12" font-weight="bold" fill="#333">{short}</text>')
        for hi, h in enumerate(HARNESS_ORDER):
            r = repo_analysis[repo].get(h)
            if r:
                bx = gx + hi * bar_w + bar_w/2
                bh = chart_h * r["rate"] / 100
                by = margin_t + chart_h - bh
                parts.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w-1:.1f}" height="{bh:.1f}" fill="{COLORS[h]}" rx="1"/>')
                parts.append(f'<text x="{bx+bar_w/2:.1f}" y="{by-3:.1f}" text-anchor="middle" font-size="8" fill="#666">{r["resolved"]}</text>')
    parts.append('</svg>')
    legend = ['<svg xmlns="http://www.w3.org/2000/svg" width="600" height="25">']
    lx = 5
    for h in HARNESS_ORDER:
        legend.append(f'<rect x="{lx}" y="5" width="10" height="10" fill="{COLORS[h]}"/>')
        legend.append(f'<text x="{lx+13}" y="14" font-size="10" fill="#333">{DISPLAY[h]}</text>')
        lx += len(DISPLAY[h]) * 6 + 25
    legend.append('</svg>')
    return "\n".join(parts) + "\n" + "\n".join(legend)

def svg_difficulty_distribution(inst_analysis, width=600, height=300):
    margin_l, margin_r, margin_t, margin_b = 60, 30, 30, 50
    chart_w = width - margin_l - margin_r
    chart_h = height - margin_t - margin_b
    dist = Counter()
    for iid, r in inst_analysis.items():
        dist[r["resolved"]] += 1
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">']
    max_count = max(dist.values()) if dist else 1
    bar_w = chart_w / 8
    for i in range(8):
        count = dist.get(i, 0)
        x = margin_l + i * bar_w + bar_w * 0.15
        bh = chart_h * count / max_count
        by = margin_t + chart_h - bh
        color = "#00b894" if i >= 5 else ("#fdcb6e" if i >= 1 else "#d63031")
        parts.append(f'<rect x="{x:.1f}" y="{by:.1f}" width="{bar_w*0.7:.1f}" height="{bh:.1f}" fill="{color}" rx="3"/>')
        parts.append(f'<text x="{x+bar_w*0.35:.1f}" y="{by-5:.1f}" text-anchor="middle" font-size="13" font-weight="bold" fill="#333">{count}</text>')
        parts.append(f'<text x="{x+bar_w*0.35:.1f}" y="{margin_t+chart_h+18}" text-anchor="middle" font-size="11" fill="#666">{i}/7</text>')
    parts.append(f'<line x1="{margin_l}" y1="{margin_t}" x2="{margin_l}" y2="{margin_t+chart_h}" stroke="#333"/>')
    parts.append(f'<line x1="{margin_l}" y1="{margin_t+chart_h}" x2="{margin_l+chart_w}" y2="{margin_t+chart_h}" stroke="#333"/>')
    parts.append(f'<text x="{margin_l+chart_w/2}" y="{height-8}" text-anchor="middle" font-size="12" fill="#333"># Harnesses that Resolved Instance</text>')
    parts.append(f'<text x="20" y="{margin_t+chart_h/2}" text-anchor="middle" font-size="12" fill="#333" transform="rotate(-90 20 {margin_t+chart_h/2})"># Instances</text>')
    parts.append('</svg>')
    return "\n".join(parts)

def svg_patch_vs_rate(stats, width=600, height=400):
    margin_l, margin_r, margin_t, margin_b = 60, 30, 30, 50
    chart_w = width - margin_l - margin_r
    chart_h = height - margin_t - margin_b
    max_patch = 4000
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">']
    for pct in range(0, 101, 20):
        y = margin_t + chart_h * (1 - pct/100)
        parts.append(f'<line x1="{margin_l}" y1="{y:.1f}" x2="{margin_l+chart_w}" y2="{y:.1f}" stroke="#eee" stroke-width="1"/>')
        parts.append(f'<text x="{margin_l-8}" y="{y+4:.1f}" text-anchor="end" font-size="10" fill="#666">{pct}%</text>')
    for kb in range(0, 4001, 1000):
        x = margin_l + chart_w * kb / max_patch
        parts.append(f'<line x1="{x:.1f}" y1="{margin_t}" x2="{x:.1f}" y2="{margin_t+chart_h}" stroke="#eee" stroke-width="1"/>')
        parts.append(f'<text x="{x:.1f}" y="{margin_t+chart_h+15}" text-anchor="middle" font-size="10" fill="#666">{kb//1000}KB</text>')
    parts.append(f'<line x1="{margin_l}" y1="{margin_t}" x2="{margin_l}" y2="{margin_t+chart_h}" stroke="#333"/>')
    parts.append(f'<line x1="{margin_l}" y1="{margin_t+chart_h}" x2="{margin_l+chart_w}" y2="{margin_t+chart_h}" stroke="#333"/>')
    parts.append(f'<text x="{margin_l+chart_w/2}" y="{height-10}" text-anchor="middle" font-size="12" fill="#333">Avg Patch Size (bytes)</text>')
    parts.append(f'<text x="15" y="{margin_t+chart_h/2}" text-anchor="middle" font-size="12" fill="#333" transform="rotate(-90 15 {margin_t+chart_h/2})">Resolve Rate (%)</text>')
    for h in HARNESS_ORDER:
        s = stats[h]
        x = margin_l + chart_w * min(s["avg_patch"], max_patch) / max_patch
        y = margin_t + chart_h * (1 - s["rate"]/100)
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="{COLORS[h]}" opacity="0.8"/>')
        parts.append(f'<text x="{x+12:.1f}" y="{y+4:.1f}" font-size="11" fill="#333" font-weight="bold">{DISPLAY[h]}</text>')
    parts.append('</svg>')
    return "\n".join(parts)

def generate_report():
    data = load_data()
    stats = compute_stats(data)
    inst_analysis = compute_instance_analysis(data)
    repo_analysis = compute_repo_analysis(data)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_entries = len(data)
    total_resolved = sum(s["resolved"] for s in stats.values())
    total_pbf = sum(s["pbf"] for s in stats.values())
    nobody_solved = [iid for iid, r in inst_analysis.items() if r["resolved"] == 0]
    everybody_solved = [iid for iid, r in inst_analysis.items() if r["resolved"] == 7]
    discriminating = [iid for iid, r in inst_analysis.items() if 1 <= r["resolved"] <= 6]
    chart_bar = svg_bar_chart(stats)
    chart_failure = svg_stacked_failure(stats)
    chart_scatter = svg_scatter_wall_vs_rate(stats)
    chart_patch = svg_patch_vs_rate(stats)
    chart_repo = svg_repo_comparison(repo_analysis)
    chart_diff = svg_difficulty_distribution(inst_analysis)
    # Build heatmap table
    instances = sorted(inst_analysis.keys())
    heatmap_rows = ""
    for iid in instances:
        short = iid.replace("django__django-", "dj-").replace("sympy__sympy-", "sy-")
        cells = ""
        for h in HARNESS_ORDER:
            e = next((e for e in data if e["instance_id"] == iid and e.get("harness") == h), None)
            if e:
                cls = e.get("classification")
                if cls == "resolved":
                    cells += '<td class="hm-resolved">YES</td>'
                elif cls == "patch-but-failed":
                    cells += '<td class="hm-pbf">no</td>'
                elif cls == "blocked":
                    cells += '<td class="hm-blocked">blk</td>'
                else:
                    cells += '<td class="hm-other">?</td>'
            else:
                cells += '<td class="hm-na">-</td>'
        res_count = inst_analysis[iid]["resolved"]
        heatmap_rows += f'<tr><td class="hm-iid">{short}</td>{cells}<td class="hm-count">{res_count}/7</td></tr>\n'
    # Architecture table data
    arch_data = {
        "cline-patched": {"lang": "TypeScript (Node/Bun)", "tools": "read_file, write_to_file, replace_in_file, execute_command, search_files", "context": "Full file + diff", "approach": "Agentic loop with auto-approve", "non_int": "cline --allowedTools ... -m"},
        "codex": {"lang": "Rust + TypeScript", "tools": "shell, file_edit, apply_patch", "context": "Full repo scan", "approach": "Multi-turn with sandboxed exec", "non_int": "codex --quiet --full-auto"},
        "opencode": {"lang": "TypeScript (Bun)", "tools": "read, write, edit, bash, glob, grep", "context": "File-level with tree", "approach": "LSP-aware, fast iteration", "non_int": "opencode run --non-interactive"},
        "claude-code": {"lang": "TypeScript (Node)", "tools": "Read, Write, Edit, Bash, Glob, Grep", "context": "Full repo", "approach": "Claude-optimized prompt format", "non_int": "claude --print --dangerously-skip-permissions"},
        "deepseek-harness": {"lang": "Rust", "tools": "file_read, file_write, shell_exec", "context": "File-level", "approach": "Minimal overhead, raw patches", "non_int": "Rust binary, headless via env"},
        "pi": {"lang": "TypeScript (Bun)", "tools": "read, write, edit, bash, search", "context": "Full file + project tree", "approach": "Print mode, JSON events", "non_int": "pi -p (print mode)"},
        "hermes": {"lang": "Python", "tools": "file_ops, shell, search, web", "context": "Full repo", "approach": "CLI oneshot with yolo flag", "non_int": "hermes -z --yolo"},
    }
    arch_rows = ""
    for h in HARNESS_ORDER:
        a = arch_data[h]
        s = stats[h]
        arch_rows += f'<tr><td class="hname">{DISPLAY[h]}</td><td>{a["lang"]}</td><td style="font-size:11px">{a["tools"]}</td><td>{a["context"]}</td><td>{a["approach"]}</td><td><code>{a["non_int"]}</code></td><td style="text-align:center;font-weight:bold;color:{COLORS[h]}">{s["rate"]:.1f}%</td></tr>\n'
    # Cost table
    ranked = sorted(HARNESS_ORDER, key=lambda h: stats[h]["rate"], reverse=True)
    cost_rows = ""
    for rank, h in enumerate(ranked, 1):
        s = stats[h]
        total_hours = s["total_wall"] / 3600
        eff = s["resolved"] / total_hours if total_hours > 0 else 0
        cost_rows += f'<tr><td style="text-align:center">{rank}</td><td class="hname">{DISPLAY[h]}</td><td style="text-align:center">{s["resolved"]}/{s["scored"]}</td><td style="text-align:center">{s["rate"]:.1f}%</td><td style="text-align:center">{s["avg_wall"]:.0f}s</td><td style="text-align:center">{s["total_wall"]/3600:.1f}h</td><td style="text-align:center">{s["timeouts"]}</td><td style="text-align:center">{s["avg_patch"]:.0f}B</td><td style="text-align:center;font-weight:bold">{eff:.1f}</td></tr>\n'
    # Failure evidence
    timeout_examples = []
    f2p_examples = []
    both_fail_examples = []
    for e in data:
        hr = e.get("harness_result", {})
        wall = hr.get("wall_s", 0)
        cls = e.get("classification")
        ev = hr.get("eval", {})
        if wall and wall >= TIMEOUT_THRESHOLD and hr.get("returncode") == 1 and len(timeout_examples) < 2:
            timeout_examples.append(e)
        if cls == "patch-but-failed":
            if ev.get("f2p_pass", 0) < ev.get("f2p_total", 0) and ev.get("p2p_pass", 0) >= ev.get("p2p_total", 0) and len(f2p_examples) < 2:
                f2p_examples.append(e)
            if ev.get("f2p_pass", 0) < ev.get("f2p_total", 0) and ev.get("p2p_pass", 0) < ev.get("p2p_total", 0) and len(both_fail_examples) < 1:
                both_fail_examples.append(e)
    evidence_html = ""
    for e in timeout_examples:
        h = e["harness"]; iid = e["instance_id"]
        wall = e["harness_result"]["wall_s"]
        stdout = e["harness_result"].get("stdout_tail", "")
        ev = e["harness_result"].get("eval", {})
        evidence_html += f'<div class="evidence"><h4>TIMEOUT: {DISPLAY[h]} / {iid}</h4><pre>wall_s={wall:.0f}s  returncode=1  eval: f2p={ev.get("f2p_pass",0)}/{ev.get("f2p_total",0)} p2p={ev.get("p2p_pass",0)}/{ev.get("p2p_total",0)}\nstdout_tail: ...{html.escape(stdout[-200:])}</pre></div>\n'
    for e in f2p_examples:
        h = e["harness"]; iid = e["instance_id"]
        ev = e["harness_result"].get("eval", {})
        stdout = e["harness_result"].get("stdout_tail", "")
        patch_size = "N/A"
        if "model_patch:" in stdout:
            try:
                patch_size = stdout.split("model_patch:")[1].split("bytes")[0].strip() + " bytes"
            except: pass
        evidence_html += f'<div class="evidence"><h4>Wrong Fix (FAIL_TO_PASS only): {DISPLAY[h]} / {iid}</h4><pre>patch_applied=True  patch_size={patch_size}\neval: f2p={ev.get("f2p_pass",0)}/{ev.get("f2p_total",0)} (FAIL)  p2p={ev.get("p2p_pass",0)}/{ev.get("p2p_total",0)} (PASS)\nPatch was applied cleanly but did not fix the target bug</pre></div>\n'
    for e in both_fail_examples:
        h = e["harness"]; iid = e["instance_id"]
        ev = e["harness_result"].get("eval", {})
        evidence_html += f'<div class="evidence"><h4>Both Fail: {DISPLAY[h]} / {iid}</h4><pre>eval: f2p={ev.get("f2p_pass",0)}/{ev.get("f2p_total",0)} (FAIL)  p2p={ev.get("p2p_pass",0)}/{ev.get("p2p_total",0)} (FAIL)\nPatch did not fix the bug AND broke existing tests</pre></div>\n'
    nobody_html = ""
    for iid in nobody_solved:
        repo = iid.split("__")[0]
        nobody_html += f"<tr><td class='iid'>{iid}</td><td>{repo}</td></tr>\n"
    return data, stats, inst_analysis, repo_analysis, now, total_entries, total_resolved, total_pbf, \
           nobody_solved, everybody_solved, discriminating, chart_bar, chart_failure, chart_scatter, \
           chart_patch, chart_repo, chart_diff, heatmap_rows, arch_rows, cost_rows, evidence_html, nobody_html

if __name__ == "__main__":
    generate_report()
    print("Analysis computed successfully (HTML generation in separate step)")
