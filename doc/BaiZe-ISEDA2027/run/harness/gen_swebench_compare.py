#!/usr/bin/env python3
"""Generate SWEBENCH_COMPARE.html from pilot_results.json + prediction files."""
import json, html
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKDIRS = Path("/dev/shm/harness_work/workdirs")
SUMMARY = json.loads((Path("/nas_train/app.e0031982/harness_work/pilot_results.json")).read_text())
HARNESSES = ["cline-patched", "codex", "opencode", "claude-code"]

def patch_size(iid, h):
    pred_key = h.replace("-", "_")
    f = WORKDIRS / f"predictions_{pred_key}_{iid}.json"
    return f.stat().st_size if f.exists() else 0

# Compute stats
stats = {}
for h in HARNESSES:
    walls, patch_sizes, resolved, genuine, resolved_genuine = [], [], 0, 0, 0
    for r in SUMMARY:
        if "blocked" in r:
            continue
        hres = r.get("harnesses", {}).get(h, {})
        ev = hres.get("eval", {})
        wall = hres.get("wall_s")
        if wall and isinstance(wall, (int, float)):
            walls.append(wall)
        ps = patch_size(r["instance_id"], h)
        patch_sizes.append(ps)
        if ev.get("resolved") == True:
            resolved += 1
        if ps > 200:
            genuine += 1
            if ev.get("resolved") == True:
                resolved_genuine += 1
    walls_g = [w for w, ps in zip(walls, patch_sizes) if ps > 200]
    patches_g = [ps for ps in patch_sizes if ps > 200]
    total = len([r for r in SUMMARY if "blocked" not in r])
    stats[h] = {
        "total": total, "resolved": resolved, "genuine": genuine, "resolved_genuine": resolved_genuine,
        "resolve_rate": f"{resolved}/{total} ({100*resolved/total:.1f}%)" if total else "N/A",
        "fair_rate": f"{resolved_genuine}/{genuine} ({100*resolved_genuine/genuine:.0f}%)" if genuine > 0 else "N/A",
        "avg_wall_all": f"{sum(walls)/len(walls):.1f}s" if walls else "N/A",
        "avg_wall_g": f"{sum(walls_g)/len(walls_g):.1f}s" if walls_g else "N/A",
        "avg_patch_g": f"{sum(patches_g)/len(patches_g):.0f}B" if patches_g else "N/A",
    }

blocked_count = len([r for r in SUMMARY if "blocked" in r])
completed = len(SUMMARY) - blocked_count

# Build detail rows
rows_detail = []
for r in SUMMARY:
    iid = r.get("instance_id", "?")
    if "blocked" in r:
        rows_detail.append(f'<tr class="blocked"><td>{html.escape(iid)}</td><td colspan="5" class="blocked-msg">BLOCKED: {html.escape(r["blocked"][:80])}</td></tr>')
        continue
    cells = []
    for h in HARNESSES:
        hres = r.get("harnesses", {}).get(h, {})
        ev = hres.get("eval", {})
        wall = hres.get("wall_s", "?")
        ps = patch_size(iid, h)
        resolved = ev.get("resolved", None)
        genuine = ps > 200
        r_icon = "&#10004;" if resolved == True else "&#10006;" if resolved is False else "?"
        cls = "resolved" if resolved == True else "failed"
        g_tag = ' <span class="genuine">G</span>' if genuine else ' <span class="empty">E</span>'
        wall_str = f"{wall:.1f}s" if isinstance(wall, (int, float)) else str(wall)
        cells.append(f'<td class="{cls}">{r_icon}{g_tag}<br><small>{wall_str} / {ps}B</small></td>')
    rows_detail.append(f"<tr><td class='iid'>{html.escape(iid)}</td>{''.join(cells)}</tr>")

summary_rows = []
for h in HARNESSES:
    s = stats[h]
    summary_rows.append(
        f"<tr><td class='hname'>{h}</td>"
        f"<td>{s['resolve_rate']}</td>"
        f"<td class='fair'>{s['fair_rate']}</td>"
        f"<td>{s['genuine']}/{s['total']}</td>"
        f"<td>{s['avg_wall_all']}</td>"
        f"<td>{s['avg_wall_g']}</td>"
        f"<td>{s['avg_patch_g']}</td></tr>"
    )

genuine_rows = []
for r in SUMMARY:
    if "blocked" in r:
        continue
    iid = r["instance_id"]
    for h in HARNESSES:
        ps = patch_size(iid, h)
        if ps > 200:
            hres = r.get("harnesses", {}).get(h, {})
            ev = hres.get("eval", {})
            resolved = ev.get("resolved", None)
            wall = hres.get("wall_s", "?")
            r_icon = "&#10004;" if resolved else "&#10006;"
            wall_str = f"{wall:.1f}s" if isinstance(wall, (int, float)) else str(wall)
            genuine_rows.append(
                f"<tr><td>{html.escape(iid)}</td><td>{h}</td><td>{ps}B</td>"
                f"<td>{wall_str}</td><td class='{'resolved' if resolved else 'failed'}'>{r_icon}</td></tr>"
            )

CSS = """body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 2em; background: #f8f9fa; color: #1a1a1a; line-height: 1.6; }
h1 { color: #1a1a2e; border-bottom: 3px solid #16213e; padding-bottom: 0.3em; }
h2 { color: #16213e; margin-top: 2em; border-left: 4px solid #0f3460; padding-left: 0.5em; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 0.9em; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
th, td { border: 1px solid #dee2e6; padding: 0.5em 0.7em; text-align: center; }
th { background: #16213e; color: white; }
td.iid { text-align: left; font-family: monospace; font-size: 0.85em; }
td.resolved { background: #d4edda; color: #155724; }
td.failed { background: #f8d7da; color: #721c24; }
tr.blocked td { background: #fff3cd; }
.genuine { background: #007bff; color: white; font-size: 0.7em; padding: 0 3px; border-radius: 2px; }
.empty { background: #6c757d; color: white; font-size: 0.7em; padding: 0 3px; border-radius: 2px; }
.fair { font-weight: bold; color: #0f3460; }
.callout { background: #e7f4ff; border-left: 4px solid #007bff; padding: 1em 1.5em; margin: 1em 0; }
.warning { background: #fff3cd; border-left: 4px solid #ffc107; padding: 1em 1.5em; margin: 1em 0; }
.caveat { background: #f8d7da; border-left: 4px solid #dc3545; padding: 1em 1.5em; margin: 1em 0; }
pre { background: #f1f3f5; padding: 1em; border-radius: 4px; overflow-x: auto; }"""

rows_joined = '\n'.join(rows_detail)
summary_joined = '\n'.join(summary_rows)
genuine_joined = '\n'.join(genuine_rows)

html_content = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SWE-bench Lite Pilot Comparison</title>
<style>{CSS}</style></head><body>
<h1>SWE-bench Lite Pilot Comparison &mdash; 5 Harness Internal Benchmark</h1>
<div class="callout">
<strong>Generated:</strong> 2026-10-05 (Round 62)<br>
<strong>Scope:</strong> 30 instances (django+sympy) &mdash; <strong>{completed} scored, {blocked_count} blocked</strong><br>
<strong>Model:</strong> deepseek-v4-flash (same gateway) | <strong>Sandbox:</strong> unshare (R1, no Docker)<br>
<strong>Eval:</strong> r1_eval.py with FAIL_TO_PASS + PASS_TO_PASS
</div>
<div class="warning">
<strong>&#9888; Quota Contamination:</strong> 5-hour sliding window API quota exhausted after first 3-4 instances.
Only <strong>10 genuine patches (>200B)</strong> across all harnesses. Raw resolve rates are misleading;
<strong>Fair Rate</strong> (genuine attempts only) is the meaningful metric.
</div>
<h2>1. Aggregate Summary (21 Completed)</h2>
<table>
<tr><th>Harness</th><th>Resolve Rate (raw)</th><th>Fair Rate (genuine) &#9733;</th><th>Genuine</th><th>Avg Wall (all)</th><th>Avg Wall (genuine)</th><th>Avg Patch (genuine)</th></tr>
{summary_joined}
</table>
<div class="callout">
<strong>Key Findings:</strong>
<ul>
<li><strong>codex</strong> #1: 2/21 raw (9.5%), 2/3 fair (67%)</li>
<li><strong>claude-code</strong>: 1/1 fair (100%) but only 1 genuine attempt; fastest (11.2s avg)</li>
<li><strong>opencode</strong>: 1/2 fair (50%), middle-ground</li>
<li><strong>cline-patched</strong>: most genuine patches (4/21) but lowest fair rate (1/4=25%)</li>
<li><strong>django-11001</strong>: only instance where ALL 4 resolved</li>
<li><strong>sympy-11870</strong>: 3 genuine patches but NONE resolved</li>
</ul>
</div>
<h2>2. Genuine Patch Details (10 patches >200B)</h2>
<table>
<tr><th>Instance</th><th>Harness</th><th>Patch Size</th><th>Wall Time</th><th>Resolved</th></tr>
{genuine_joined}
</table>
<h2>3. Full Instance-level Results</h2>
<p>Legend: <span class="genuine">G</span>=genuine(>200B), <span class="empty">E</span>=empty(quota), &#10004;=resolved, &#10006;=failed</p>
<table>
<tr><th>Instance</th><th>cline-patched</th><th>codex</th><th>opencode</th><th>claude-code</th></tr>
{rows_joined}
</table>
<h2>4. Failure Mode Analysis</h2>
<h3>4.1 Quota Exhaustion (Primary)</h3>
<div class="warning">
<p><strong>Affected:</strong> 17/21 instances. <strong>Symptom:</strong> empty patches (127-135B). <strong>Root cause:</strong> 5h sliding window API quota. First 3 instances consumed quota; retries within same window also fail. <strong>Evidence:</strong> 33+ QUOTA events in batch log; sympy-11870 got genuine patches at ~05:00 (quota reset). <strong>Mitigation for 300:</strong> higher quota tier, multiple API keys, or 3-4 instances per 5h window (~15 days).</p>
</div>
<h3>4.2 Blocked Instances (9/30)</h3>
<div class="warning">
<p><strong>Affected:</strong> 9 sympy instances (12481-13647). <strong>Root cause:</strong> stale shallow.lock in git workdir. <strong>Fix:</strong> rm -f .../shallow.lock (2026-10-05 07:15). Re-run with --resume.</p>
</div>
<h3>4.3 Harness Patterns</h3>
<table>
<tr><th>Pattern</th><th>cline-patched</th><th>codex</th><th>opencode</th><th>claude-code</th></tr>
<tr><td>Wall (quota-hit)</td><td>~16-18s</td><td>~4-6s</td><td>~70-77s</td><td>~2-4s</td></tr>
<tr><td>Wall (genuine)</td><td>145-614s</td><td>150-400s</td><td>94-496s</td><td>76s</td></tr>
<tr><td>Patch tendency</td><td>Largest</td><td>Large</td><td>Medium</td><td>Small</td></tr>
<tr><td>Genuine rate</td><td>4/21 (19%)</td><td>3/21 (14%)</td><td>2/21 (10%)</td><td>1/21 (5%)</td></tr>
<tr><td>Resolve if genuine</td><td>1/4 (25%)</td><td>2/3 (67%)</td><td>1/2 (50%)</td><td>1/1 (100%)</td></tr>
</table>
<h2>5. Methodology</h2>
<div class="callout">
<ol>
<li>30 SWE-bench Lite instances (15 django + 15 sympy)</li>
<li>Rootfs: 2 templates via unshare sandbox (R1, no Docker)</li>
<li>Workdirs: shallow git clones in /dev/shm (tmpfs)</li>
<li>Run: same model (deepseek-v4-flash), 1800s timeout</li>
<li>Eval: r1_eval.py (F2P + P2P tests)</li>
</ol>
</div>
<h3>Reproduction</h3>
<pre><code>cd /nas_train/app.e0031982/harness_work
PYTHONUNBUFFERED=1 python3 run_pilot_batch.py --all-prepared --out-summary pilot_results.json
# Resume:
python3 run_pilot_batch.py --all-prepared --resume --out-summary pilot_results.json</code></pre>
<h2>6. Caveats</h2>
<div class="caveat">
<ol>
<li>NOT a standard SWE-bench score. Internal cross-harness comparison only.</li>
<li>Only 10 genuine patches. Fair rate denominators (3-4) too small for statistical significance.</li>
<li>9/30 blocked by git lock (fixed). Repo bias: 15 django + 6 sympy.</li>
<li>cline-patched is modified cline, not vanilla.</li>
<li>Single model (deepseek-v4-flash). No Docker (unshare sandbox).</li>
</ol>
</div>
<h2>7. Recommendation for Scaling to 300</h2>
<div class="callout">
<ul>
<li><strong>Option A:</strong> Quota increase or staggered API keys. ~15 days at 4 inst/window.</li>
<li><strong>Option B:</strong> Reduce to 3 harnesses to halve quota.</li>
<li><strong>Option C:</strong> Pre-filter instances likely to get empty patches.</li>
<li><strong>Fixed:</strong> shallow.lock resolved. --resume recovers 9 blocked.</li>
</ul>
</div>
<hr>
<p><small>BaiZe Harness H-A, 2026-10-05 R62. Data: pilot_results.json (30 entries). Predictions: 84 files. Eval logs: 177 files.</small></p>
</body></html>"""

out = HERE / "SWEBENCH_COMPARE.html"
out.write_text(html_content)
print(f"Written: {out} ({out.stat().st_size} bytes)")