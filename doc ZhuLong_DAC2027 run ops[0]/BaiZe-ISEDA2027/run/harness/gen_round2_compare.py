#!/usr/bin/env python3
"""Generate SWEBENCH_COMPARE.html — Round-2 7×100 harness cross-eval.

Per operator instruction 2026-10-08⑦:
  - 100 instances (30 R1 reused + 70 stratified new) × 7 harnesses
  - Same model (kimi-k2.6-cloud), same sandbox, same PreToolUse/anti-cheat
  - R1 30 instances were serial (concurrency=1); R2 70 new instances are
    7-harness parallel (serial=1 per harness, 7 harnesses concurrent)
  - --resume reuses R1 serial results for the 30 overlapping instances
  - "复用/新跑" marker column required in detail table
  - 口径与并发 disclosure section required
  - Monitor quota-blocked/timeout/no-patch rates: R1(30) vs R2(70)
"""
import json, html
from pathlib import Path
from collections import defaultdict
from datetime import datetime

HERE = Path(__file__).resolve().parent
RESULTS_FILE = HERE / "kimi_pilot_results.json"
SELECTION_FILE = HERE / "instance_selection_100.json"
MODEL = "kimi-k2.6-cloud"
GATEWAY = "http://agi-gateway.cxmt.com/cloud/v1"
HARNESS_ORDER = ["cline-patched", "codex", "opencode", "claude-code", "deepseek-harness", "pi", "hermes"]
DISPLAY_NAMES = {
    "cline-patched": "cline-patched", "codex": "codex", "opencode": "opencode",
    "claude-code": "claude-code", "deepseek-harness": "deepseek-harness",
    "pi": "Pi", "hermes": "Hermes Agent",
}
TOTAL_PLANNED = 100


def load_results():
    if not RESULTS_FILE.exists():
        return []
    return json.loads(RESULTS_FILE.read_text())


def load_selection():
    sel = json.loads(SELECTION_FILE.read_text())
    instances = sel["instances"]
    r1_set = set(instances[:sel["round1_count"]])
    all_set = set(instances)
    return all_set, r1_set, instances


def classify_entry(e):
    cls = e.get("classification", "blocked")
    if cls == "resolved":
        return "&#10004;", "resolved"
    elif cls == "patch-but-failed":
        return "&#10006;", "failed"
    elif cls == "quota-blocked":
        return "&#9728;", "blocked"
    else:
        return "&#9888;", "infblocked"


def compute_stats(entries, r1_set):
    r1_entries = [e for e in entries if e["instance_id"] in r1_set]
    r2_entries = [e for e in entries if e["instance_id"] not in r1_set]

    def _stats(es):
        resolved = sum(1 for e in es if e.get("classification") == "resolved")
        pbf = sum(1 for e in es if e.get("classification") == "patch-but-failed")
        qb = sum(1 for e in es if e.get("classification") == "quota-blocked")
        blk = sum(1 for e in es if e.get("classification") == "blocked")
        scored = resolved + pbf
        walls = [e.get("harness_result", {}).get("wall_s") for e in es
                 if isinstance(e.get("harness_result", {}).get("wall_s"), (int, float))]
        avg_wall = f"{sum(walls)/len(walls):.0f}s" if walls else "—"
        resolve_rate = f"{resolved}/{scored} ({100*resolved/scored:.1f}%)" if scored > 0 else "—"
        return {"total": len(es), "scored": scored, "resolved": resolved,
                "pbf": pbf, "qb": qb, "blk": blk,
                "resolve_rate": resolve_rate, "avg_wall": avg_wall}

    return _stats(r1_entries), _stats(r2_entries), _stats(entries)


def main():
    data = load_results()
    all_set, r1_set, instances_ordered = load_selection()
    data = [e for e in data if e.get("instance_id") in all_set]

    by_harness = defaultdict(list)
    for entry in data:
        by_harness[entry.get("harness", "unknown")].append(entry)

    summary_rows = []
    monitor_rows = []
    for h in HARNESS_ORDER:
        entries = by_harness.get(h, [])
        r1s, r2s, alls = compute_stats(entries, r1_set)
        total_done = len(entries)
        remaining = TOTAL_PLANNED - total_done
        if total_done == 0:
            status = "⬜ not started"
        elif remaining > 0:
            status = f"🔄 in progress ({total_done}/{TOTAL_PLANNED})"
        else:
            status = "✅ done"
        dn = DISPLAY_NAMES.get(h, h)
        summary_rows.append(
            f"<tr><td class='hname'>{dn}</td>"
            f"<td>{alls['scored']}</td><td>{alls['resolved']}</td><td>{alls['pbf']}</td>"
            f"<td>{alls['qb']}</td><td>{alls['blk']}</td>"
            f"<td>{alls['resolve_rate']}</td><td>{alls['avg_wall']}</td><td>{status}</td></tr>")
        monitor_rows.append(
            f"<tr><td class='hname'>{dn}</td>"
            f"<td>{r1s['resolved']}/{r1s['scored']}</td><td>{r1s['qb']}</td><td>{r1s['blk']}</td>"
            f"<td>{r2s['resolved']}/{r2s['scored']}</td><td>{r2s['qb']}</td><td>{r2s['blk']}</td></tr>")

    instances_sorted = sorted(instances_ordered)
    rows_detail = []
    for iid in instances_sorted:
        is_r1 = iid in r1_set
        marker = '<small class="r1tag">R1复用</small>' if is_r1 else '<small class="r2tag">R2新跑</small>'
        cells = []
        for h in HARNESS_ORDER:
            matching = [e for e in data if e["instance_id"] == iid and e.get("harness") == h]
            if not matching:
                cells.append('<td class="pending">—</td>')
                continue
            e = matching[0]
            icon, cell_cls = classify_entry(e)
            wall = e.get("harness_result", {}).get("wall_s", "—")
            wall_str = f"{wall:.0f}s" if isinstance(wall, (int, float)) else str(wall)
            cells.append(f'<td class="{cell_cls}">{icon}<br><small>{wall_str}</small></td>')
        rows_detail.append(f"<tr><td class='iid'>{html.escape(iid)}</td><td class='marker'>{marker}</td>{''.join(cells)}</tr>")

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_entries = len(data)
    total_resolved = sum(1 for e in data if e.get("classification") == "resolved")
    rows_joined = chr(10).join(rows_detail) if rows_detail else ""
    summary_joined = chr(10).join(summary_rows)
    monitor_joined = chr(10).join(monitor_rows)

    r1_done = {h: sum(1 for e in by_harness.get(h, []) if e["instance_id"] in r1_set) for h in HARNESS_ORDER}
    r2_done = {h: sum(1 for e in by_harness.get(h, []) if e["instance_id"] not in r1_set) for h in HARNESS_ORDER}

    html_content = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>SWE-bench Round-2 Cross-Eval — {MODEL} (7x100)</title>
<style>
body {{ font-family: -apple-system, sans-serif; max-width: 1400px; margin: 0 auto; padding: 20px; background: #f8f9fa; color: #333; }}
h1 {{ color: #1a1a2e; border-bottom: 3px solid #6c5ce7; padding-bottom: 10px; }}
h2 {{ color: #2d3436; margin-top: 30px; border-left: 4px solid #6c5ce7; padding-left: 10px; }}
table {{ border-collapse: collapse; width: 100%; margin: 15px 0; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
th {{ background: #6c5ce7; color: white; padding: 10px 12px; text-align: left; font-size: 13px; }}
td {{ padding: 8px 12px; border-bottom: 1px solid #eee; font-size: 13px; }}
td.iid {{ font-family: monospace; font-size: 12px; white-space: nowrap; }}
td.hname {{ font-weight: bold; }}
td.marker {{ text-align: center; white-space: nowrap; }}
td.resolved {{ background: #d4edda; color: #155724; text-align: center; }}
td.failed {{ background: #f8d7da; color: #721c24; text-align: center; }}
td.blocked {{ background: #fff3cd; color: #856404; text-align: center; }}
td.infblocked {{ background: #fce4ec; color: #880e4f; text-align: center; }}
td.pending {{ text-align: center; color: #ccc; }}
.r1tag {{ background: #e3f2fd; color: #1565c0; padding: 2px 6px; border-radius: 3px; font-size: 10px; font-weight: bold; }}
.r2tag {{ background: #fff3e0; color: #e65100; padding: 2px 6px; border-radius: 3px; font-size: 10px; font-weight: bold; }}
.callout {{ background: #e8f4fd; border-left: 4px solid #0984e3; padding: 15px; margin: 15px 0; border-radius: 0 8px 8px 0; }}
.caveat {{ background: #fff8e1; border: 1px solid #ffe082; padding: 15px; margin: 15px 0; border-radius: 8px; }}
.caliber {{ background: #f3e5f5; border-left: 4px solid #8e24aa; padding: 15px; margin: 15px 0; border-radius: 0 8px 8px 0; }}
.model-badge {{ display: inline-block; background: #6c5ce7; color: white; padding: 4px 12px; border-radius: 20px; font-size: 14px; font-weight: bold; }}
pre {{ background: #2d3436; color: #dfe6e9; padding: 15px; border-radius: 8px; overflow-x: auto; font-size: 12px; }}
</style></head><body>
<h1>SWE-bench Round-2 · 7x100 Harness Cross-Eval Report</h1>
<p><span class="model-badge">Model: {MODEL}</span> &nbsp; Gateway: <code>{GATEWAY}</code></p>
<p><strong>Generated:</strong> {now} | <strong>Scope:</strong> 100 instances (30 R1 reused + 70 new) x 7 | <strong>Concurrency:</strong> R1=serial(1), R2=7-parallel</p>
<div class="caliber">
<h2>Caliber &amp; Concurrency Disclosure (口径与并发)</h2>
<p><strong>Per operator instruction 2026-10-08 (7th) — read before interpreting numbers.</strong></p>
<table>
<tr><th>Dimension</th><th>Round-1 (30)</th><th>Round-2 (70 new)</th></tr>
<tr><td>Concurrency</td><td><strong>Serial (1)</strong></td><td><strong>7-harness parallel</strong></td></tr>
<tr><td>Run condition</td><td>No contention</td><td>7 harnesses compete for gateway/sandbox/I/O</td></tr>
<tr><td>--resume</td><td colspan="2">R2 reuses R1's 30 serial results. Only 70 new evaluated under R2 parallel.</td></tr>
<tr><td>Comparability</td><td colspan="2"><strong>Cross-round not strictly comparable:</strong> 30 R1 rows=serial, 70 R2 rows=parallel.</td></tr>
</table>
<p><strong>Marker:</strong> <span class="r1tag">R1复用</span>=serial(--resume) <span class="r2tag">R2新跑</span>=parallel(fresh). Codex's 70 new were from 300 serial superset, not R2 parallel.</p>
<p><strong>Monitoring:</strong> R2 quota-blocked/timeout/no-patch vs R1 same 30. If R2 higher => parallel contamination. See S2.</p>
</div>
<div class="callout"><p><strong>Key Design:</strong> Same 100 x 7 | Single model ({MODEL}) | Same sandbox/eval | Quota failures NOT counted</p></div>
<h2>1. Summary by Harness (100 each)</h2>
<table>
<tr><th>Harness</th><th>Scored</th><th>Resolved</th><th>PBF</th><th>Quota-blk</th><th>Infra-blk</th><th>Resolve Rate</th><th>Avg Wall</th><th>Status</th></tr>
{summary_joined}
</table>
<div class="callout"><p><strong>Overall:</strong> {total_entries} entries | {total_resolved} resolved</p></div>
<h2>2. Monitoring: R1(30,serial) vs R2(new,parallel)</h2>
<table>
<tr><th>Harness</th><th>R1 Res/Sc</th><th>R1 Q</th><th>R1 B</th><th>R2 Res/Sc</th><th>R2 Q</th><th>R2 B</th></tr>
{monitor_joined}
</table>
<h2>3. Instance-level Detail (100 x 7)</h2>
<p>Legend: &#10004;=resolved &#10006;=patch-but-failed &#9728;=quota-blocked &#9888;=infra-blocked —=not run. <span class="r1tag">R1复用</span>=serial <span class="r2tag">R2新跑</span>=parallel</p>
<table>
<tr><th>Instance</th><th>Run</th><th>cline</th><th>codex</th><th>opencode</th><th>claude-code</th><th>deepseek-hs</th><th>Pi</th><th>Hermes</th></tr>
{rows_joined}
</table>
<h2>4. Reproduction</h2>
<pre><code>cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness
INSTS=$(python3 -c "import json; d=json.load(open('instance_selection_100.json')); print(' '.join(d['instances']))")
PYTHONUNBUFFERED=1 HARNESS_MODEL={MODEL} python3 run_serial_kimi.py --harness &lt;name&gt; --instances $INSTS --resume
python3 gen_round2_compare.py</code></pre>
<h2>5. Caveats</h2>
<div class="caveat">
<ol>
<li><strong>NOT standard SWE-bench leaderboard score.</strong> Internal comparison only.</li>
<li><strong>Non-Docker sandbox</strong> (unshare R1).</li>
<li><strong>Mixed run conditions:</strong> 30 serial (R1), 70 parallel (R2). See caliber section.</li>
<li><strong>Codex 300 superset:</strong> codex's 70 new were serial, not R2 parallel.</li>
<li><strong>cline-patched</strong> is modified, not vanilla.</li>
</ol>
</div>
<hr>
<p><small>BaiZe Harness H-A, Round-2 7x100, {now}. Model: {MODEL}. R1=serial(30), R2=parallel(70). Data: kimi_pilot_results.json ({total_entries} entries in 100-set).</small></p>
</body></html>"""

    out = HERE / "SWEBENCH_COMPARE.html"
    out.write_text(html_content)
    print(f"Written: {out} ({out.stat().st_size} bytes)")
    print(f"  Total entries in 100-set: {total_entries}, Resolved: {total_resolved}")
    for h in HARNESS_ORDER:
        print(f"  {h}: R1={r1_done[h]}/30, R2={r2_done[h]}/70")


if __name__ == "__main__":
    main()

