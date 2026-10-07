#!/usr/bin/env python3
"""Generate SWEBENCH_COMPARE.html from kimi_pilot_results.json — 30×5 harness comparison.

Per operator instruction 2026-10-07: same 30 instances (15 django + 15 sympy) × 5 harnesses,
single model (kimi-k2.6-cloud), concurrency=1 strict serial.
"""
import json, html
from pathlib import Path
from collections import defaultdict
from datetime import datetime

HERE = Path(__file__).resolve().parent
RESULTS_FILE = HERE / "kimi_pilot_results.json"
MODEL = "kimi-k2.6-cloud"
GATEWAY = "http://agi-gateway.cxmt.com/cloud/v1"
HARNESS_ORDER = ["cline-patched", "codex", "opencode", "claude-code", "deepseek-harness"]
TOTAL_PLANNED = 30  # 15 django + 15 sympy

def load_results():
    if not RESULTS_FILE.exists():
        return []
    return json.loads(RESULTS_FILE.read_text())

def get_target_instances(data):
    """The 30 instances are defined by the cline-patched run (15 django + 15 sympy)."""
    cl_ids = set(e["instance_id"] for e in data if e.get("harness") == "cline-patched")
    if not cl_ids:
        # Fallback: if cline-patched not yet run, use the first 30 django+sympy from codex
        cl_ids = set(e["instance_id"] for e in data
                      if e.get("harness") == "codex"
                      and ("django" in e["instance_id"] or "sympy" in e["instance_id"]))
        # Take first 30 sorted
        cl_ids = set(sorted(cl_ids)[:30])
    return cl_ids

def main():
    data = load_results()
    target_ids = get_target_instances(data)
    # Filter to only the 30 target instances
    data = [e for e in data if e["instance_id"] in target_ids]

    by_harness = defaultdict(list)
    for entry in data:
        h = entry.get("harness", "unknown")
        by_harness[h].append(entry)

    stats = {}
    for h in HARNESS_ORDER:
        entries = by_harness.get(h, [])
        resolved = sum(1 for e in entries if e.get("classification") == "resolved")
        pbf = sum(1 for e in entries if e.get("classification") == "patch-but-failed")
        qb = sum(1 for e in entries if e.get("classification") == "quota-blocked")
        blk = sum(1 for e in entries if e.get("classification") == "blocked")
        scored = resolved + pbf
        walls = [e.get("harness_result", {}).get("wall_s") for e in entries
                 if isinstance(e.get("harness_result", {}).get("wall_s"), (int, float))]
        avg_wall = f"{sum(walls)/len(walls):.0f}s" if walls else "N/A"
        resolve_rate = f"{resolved}/{scored} ({100*resolved/scored:.1f}%)" if scored > 0 else "N/A"
        stats[h] = {
            "scored": scored, "resolved": resolved, "pbf": pbf, "qb": qb, "blk": blk,
            "total": len(entries),
            "remaining": TOTAL_PLANNED - len(entries),
            "resolve_rate": resolve_rate, "avg_wall": avg_wall,
            "in_progress": 0 < len(entries) < TOTAL_PLANNED,
            "not_started": len(entries) == 0,
        }

    instances = sorted(target_ids)
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
            wall = e.get("harness_result", {}).get("wall_s", "—")
            wall_str = f"{wall:.0f}s" if isinstance(wall, (int, float)) else str(wall)
            if cls == "resolved":
                icon = "&#10004;"; cell_cls = "resolved"
            elif cls == "patch-but-failed":
                icon = "&#10006;"; cell_cls = "failed"
            elif cls == "quota-blocked":
                icon = "&#9728;"; cell_cls = "blocked"
            else:  # "blocked" = infrastructure failure (git fetch timeout etc.)
                icon = "&#9888;"; cell_cls = "infblocked"
            cells.append(f'<td class="{cell_cls}">{icon}<br><small>{wall_str}</small></td>')
        rows_detail.append(f"<tr><td class='iid'>{html.escape(iid)}</td>{''.join(cells)}</tr>")

    summary_rows = []
    for h in HARNESS_ORDER:
        s = stats[h]
        if s["not_started"]:
            status = "⬜ not started"
        elif s["in_progress"]:
            status = f"🔄 in progress ({s['total']}/{TOTAL_PLANNED})"
        else:
            status = "✅ done"
        summary_rows.append(
            f"<tr><td class='hname'>{h}</td>"
            f"<td>{s['scored']}</td><td>{s['resolved']}</td><td>{s['pbf']}</td>"
            f"<td>{s['qb']}</td><td>{s['blk']}</td>"
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
td.infblocked {{ background: #fce4ec; color: #880e4f; text-align: center; }}
td.pending {{ text-align: center; color: #ccc; }}
.callout {{ background: #e8f4fd; border-left: 4px solid #0984e3; padding: 15px; margin: 15px 0; border-radius: 0 8px 8px 0; }}
.caveat {{ background: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; margin: 15px 0; border-radius: 8px; }}
.model-badge {{ display: inline-block; background: #6c5ce7; color: white; padding: 4px 12px; border-radius: 20px; font-size: 14px; font-weight: bold; }}
pre {{ background: #2d3436; color: #dfe6e9; padding: 15px; border-radius: 8px; overflow-x: auto; font-size: 12px; }}
</style></head><body>
<h1>SWE-bench 30×5 Harness Cross-Eval Report</h1>
<p><span class="model-badge">Model: {MODEL}</span> &nbsp; Gateway: <code>{GATEWAY}</code></p>
<p><strong>Generated:</strong> {now} | <strong>Scope:</strong> 30 instances (15 django + 15 sympy) × 5 harnesses | <strong>Concurrency:</strong> 1 (strict serial)</p>
<div class="callout">
<p><strong>📋 Key Design (per operator instruction 2026-10-07):</strong></p>
<ul>
<li><strong>Same 30 instances</strong> across all 5 harnesses (15 django + 15 sympy, fixed set)</li>
<li><strong>Single model</strong> ({MODEL}) — no model mixing (fair comparison)</li>
<li><strong>Strict serial</strong> (concurrency=1) — one instance × one harness at a time</li>
<li><strong>Three-column classification:</strong> <code>resolved</code> / <code>patch-but-failed</code> / <code>quota-blocked</code></li>
<li><strong>Quota failures are NOT counted as harness failures</strong></li>
<li><strong>Immediate固化:</strong> results saved to JSON after each instance</li>
</ul>
</div>
<h2>1. Summary by Harness (30 instances each)</h2>
<table>
<tr><th>Harness</th><th>Scored</th><th>Resolved</th><th>Patch-but-failed</th><th>Quota-blocked</th><th>Blocked (infra)</th><th>Resolve Rate</th><th>Avg Wall</th><th>Status</th></tr>
{summary_joined}
</table>
<div class="callout">
<p><strong>📊 Overall:</strong> {total_entries} entries on 30 instances | {total_resolved} total resolved across all harnesses</p>
</div>
<h2>2. Instance-level Detail</h2>
<p>Legend: &#10004;=resolved, &#10006;=patch-but-failed, &#9728;=quota-blocked, &#9888;=infra-blocked (git/rootfs failure), — = not yet run</p>
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
# The 30 instances are defined by the cline-patched run (15 django + 15 sympy)
INSTS=$(python3 -c "import json; d=json.load(open('kimi_pilot_results.json')); print(' '.join(sorted(set(e['instance_id'] for e in d if e['harness']=='cline-patched'))))")
PYTHONUNBUFFERED=1 HARNESS_MODEL={MODEL} python3 run_serial_kimi.py --harness &lt;harness_name&gt; --instances $INSTS --resume
python3 gen_kimi_compare.py</code></pre>
<h2>5. Caveats</h2>
<div class="caveat">
<ol>
<li><strong>NOT a standard SWE-bench leaderboard score.</strong> Internal cross-harness comparison only.</li>
<li><strong>Non-Docker sandbox</strong> (unshare R1) — may differ from official Docker-based eval.</li>
<li><strong>Single model</strong> ({MODEL}) — comparable across harnesses, not vs leaderboard.</li>
<li><strong>30 instances only</strong> — small sample, confidence intervals are wide.</li>
<li><strong>cline-patched</strong> is a modified cline, not vanilla.</li>
<li><strong>Harnesses not yet run</strong> are marked "⬜ not started" — results update as runs complete.</li>
</ol>
</div>
<hr>
<p><small>BaiZe Harness H-A, 30×5 cross-eval, {now}. Model: {MODEL}. Serial concurrency=1. Data: kimi_pilot_results.json (filtered to 30 instances, {total_entries} entries).</small></p>
</body></html>"""

    out = HERE / "SWEBENCH_COMPARE.html"
    out.write_text(html_content)
    print(f"Written: {out} ({out.stat().st_size} bytes)")
    print(f"  Total entries: {total_entries}, Resolved: {total_resolved}")

if __name__ == "__main__":
    main()
