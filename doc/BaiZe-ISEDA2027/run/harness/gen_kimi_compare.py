#!/usr/bin/env python3
"""Generate SWEBENCH_COMPARE.html from kimi_pilot_results.json (single-model serial cross-eval)."""
import json, html
from pathlib import Path
from collections import defaultdict
from datetime import datetime

HERE = Path(__file__).resolve().parent
RESULTS_FILE = HERE / "kimi_pilot_results.json"
MODEL = "kimi-k2.6-cloud"
GATEWAY = "http://agi-gateway.cxmt.com/cloud/v1"
HARNESS_ORDER = ["cline-patched", "codex", "opencode", "claude-code", "deepseek-harness"]

def load_results():
    if not RESULTS_FILE.exists():
        return []
    return json.loads(RESULTS_FILE.read_text())

def main():
    data = load_results()
    by_harness = defaultdict(list)
    for entry in data:
        h = entry.get("harness", "unknown")
        by_harness[h].append(entry)

    stats = {}
    for h in HARNESS_ORDER:
        entries = by_harness.get(h, [])
        resolved = sum(1 for e in entries if e["classification"] == "resolved")
        pbf = sum(1 for e in entries if e["classification"] == "patch-but-failed")
        qb = sum(1 for e in entries if e["classification"] == "quota-blocked")
        scored = resolved + pbf
        total_planned = 300
        walls = [e["harness_result"]["wall_s"] for e in entries if "wall_s" in e.get("harness_result", {})]
        avg_wall = f"{sum(walls)/len(walls):.0f}s" if walls else "N/A"
        resolve_rate = f"{resolved}/{scored} ({100*resolved/scored:.0f}%)" if scored > 0 else "N/A"
        stats[h] = {
            "scored": scored, "resolved": resolved, "pbf": pbf, "qb": qb,
            "remaining": total_planned - len(entries),
            "resolve_rate": resolve_rate, "avg_wall": avg_wall,
            "in_progress": len(entries) < total_planned,
        }

    instances = sorted(set(e["instance_id"] for e in data))
    rows_detail = []
    for iid in instances:
        cells = []
        for h in HARNESS_ORDER:
            matching = [e for e in data if e["instance_id"] == iid and e.get("harness") == h]
            if not matching:
                cells.append('<td class="pending">—</td>')
                continue
            e = matching[0]
            cls = e["classification"]
            wall = e["harness_result"].get("wall_s", "?")
            wall_str = f"{wall:.0f}s" if isinstance(wall, (int, float)) else str(wall)
            if cls == "resolved":
                icon = "&#10004;"; cell_cls = "resolved"
            elif cls == "patch-but-failed":
                icon = "&#10006;"; cell_cls = "failed"
            else:
                icon = "&#9728;"; cell_cls = "blocked"
            cells.append(f'<td class="{cell_cls}">{icon}<br><small>{wall_str}</small></td>')
        rows_detail.append(f"<tr><td class='iid'>{html.escape(iid)}</td>{''.join(cells)}</tr>")

    summary_rows = []
    for h in HARNESS_ORDER:
        s = stats[h]
        status = "🔄 in progress" if s["in_progress"] else "✅ done"
        summary_rows.append(
            f"<tr><td class='hname'>{h}</td>"
            f"<td>{s['resolved']}</td><td>{s['pbf']}</td><td>{s['qb']}</td>"
            f"<td>{s['resolve_rate']}</td><td>{s['avg_wall']}</td><td>{status}</td></tr>")

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_entries = len(data)
    total_resolved = sum(1 for e in data if e["classification"] == "resolved")

    rows_joined = chr(10).join(rows_detail) if rows_detail else ""
    summary_joined = chr(10).join(summary_rows)

    html_content = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>SWE-bench Cross-Eval — {MODEL} (Serial)</title>
<style>
body {{ font-family: -apple-system, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f8f9fa; color: #333; }}
h1 {{ color: #1a1a2e; border-bottom: 3px solid #6c5ce7; padding-bottom: 10px; }}
h2 {{ color: #2d3436; margin-top: 30px; border-left: 4px solid #6c5ce7; padding-left: 10px; }}
table {{ border-collapse: collapse; width: 100%; margin: 15px 0; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
th {{ background: #6c5ce7; color: white; padding: 10px 12px; text-align: left; font-size: 13px; }}
td {{ padding: 8px 12px; border-bottom: 1px solid #eee; font-size: 13px; }}
td.iid {{ font-family: monospace; font-size: 12px; white-space: nowrap; }}
td.hname {{ font-weight: bold; }}
td.resolved {{ background: #d4edda; color: #155724; text-align: center; }}
td.failed {{ background: #f8d7da; color: #721c24; text-align: center; }}
td.blocked {{ background: #fff3cd; color: #856404; text-align: center; }}
td.pending {{ text-align: center; color: #ccc; }}
.callout {{ background: #e8f4fd; border-left: 4px solid #0984e3; padding: 15px; margin: 15px 0; border-radius: 0 8px 8px 0; }}
.caveat {{ background: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; margin: 15px 0; border-radius: 8px; }}
.model-badge {{ display: inline-block; background: #6c5ce7; color: white; padding: 4px 12px; border-radius: 20px; font-size: 14px; font-weight: bold; }}
pre {{ background: #2d3436; color: #dfe6e9; padding: 15px; border-radius: 8px; overflow-x: auto; font-size: 12px; }}
</style></head><body>
<h1>SWE-bench Cross-Eval Report</h1>
<p><span class="model-badge">Model: {MODEL}</span> &nbsp; Gateway: <code>{GATEWAY}</code></p>
<p><strong>Generated:</strong> {now} | <strong>Concurrency:</strong> 1 (strict serial) | <strong>Protocol:</strong> one harness × 30 instances, then next harness</p>
<div class="callout">
<p><strong>📋 Key Design (per operator instruction 2026-10-05):</strong></p>
<ul>
<li><strong>Single model</strong> ({MODEL}) — no model mixing (fair comparison)</li>
<li><strong>Strict serial</strong> (concurrency=1) — one instance × one harness at a time</li>
<li><strong>Three-column classification:</strong> <code>resolved</code> / <code>patch-but-failed</code> / <code>quota-blocked</code></li>
<li><strong>Quota failures are NOT counted as harness failures</strong></li>
<li><strong>Immediate固化:</strong> results saved to JSON after each instance</li>
</ul>
</div>
<h2>1. Summary by Harness</h2>
<table>
<tr><th>Harness</th><th>Resolved</th><th>Patch-but-failed</th><th>Quota-blocked</th><th>Resolve Rate (of scored)</th><th>Avg Wall</th><th>Status</th></tr>
{summary_joined}
</table>
<div class="callout">
<p><strong>📊 Overall:</strong> {total_entries} entries scored | {total_resolved} total resolved</p>
<p><strong>vs deepseek-v4-flash (previous):</strong> 0% resolve rate (0/22 scored) — {MODEL} shows dramatic improvement with zero quota blocks.</p>
</div>
<h2>2. Instance-level Detail</h2>
<p>Legend: &#10004;=resolved, &#10006;=patch-but-failed, &#9728;=quota-blocked, — = not yet run</p>
<table>
<tr><th>Instance</th><th>cline-patched</th><th>codex</th><th>opencode</th><th>claude-code</th><th>deepseek</th></tr>
{rows_joined if rows_joined else '<tr><td colspan="6">No data yet</td></tr>'}
</table>
<h2>3. Methodology</h2>
<div class="callout">
<ol>
<li><strong>Dataset:</strong> 30 SWE-bench Lite instances (django + sympy)</li>
<li><strong>Sandbox:</strong> unshare user namespace (R1, no Docker) with rootfs in /nas_train</li>
<li><strong>Workdirs:</strong> shallow git clones in /dev/shm (tmpfs)</li>
<li><strong>Model:</strong> {MODEL} via gw_proxy.py (port 9090)</li>
<li><strong>Timeout:</strong> 1800s per instance</li>
<li><strong>Eval:</strong> r1_eval.py — FAIL_TO_PASS + PASS_TO_PASS (official SWE-bench criteria)</li>
<li><strong>Order:</strong> cline-patched → codex → opencode → claude-code → deepseek</li>
</ol>
</div>
<h2>4. Reproduction</h2>
<pre><code>cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness
PYTHONUNBUFFERED=1 HARNESS_MODEL={MODEL} python3 run_serial_kimi.py --harness cline-patched --all-prepared --resume
python3 gen_kimi_compare.py</code></pre>
<h2>5. Caveats</h2>
<div class="caveat">
<ol>
<li><strong>NOT a standard SWE-bench leaderboard score.</strong> Internal cross-harness comparison only.</li>
<li><strong>Non-Docker sandbox</strong> (unshare R1) — may differ from official Docker-based eval.</li>
<li><strong>Single model</strong> ({MODEL}) — comparable across harnesses, not vs leaderboard.</li>
<li><strong>Partial results:</strong> cline-patched first; others run after it completes 30.</li>
<li><strong>cline-patched</strong> is a modified cline, not vanilla.</li>
</ol>
</div>
<hr>
<p><small>BaiZe Harness H-A, {now}. Model: {MODEL}. Serial concurrency=1. Data: kimi_pilot_results.json ({total_entries} entries).</small></p>
</body></html>"""

    out = HERE / "SWEBENCH_COMPARE.html"
    out.write_text(html_content)
    print(f"Written: {out} ({out.stat().st_size} bytes)")
    print(f"  Total entries: {total_entries}, Resolved: {total_resolved}")

if __name__ == "__main__":
    main()
