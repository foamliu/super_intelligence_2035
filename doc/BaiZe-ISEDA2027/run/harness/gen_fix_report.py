#!/usr/bin/env python3
"""Generate before/after comparison HTML report from fix1 re-eval results."""
from __future__ import annotations
import json, sys
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

HERE = Path(__file__).resolve().parent
ORIG_JSON = HERE / "kimi_pilot_results.json"
FIX1_JSON = HERE / "kimi_pilot_results.fix1.json"
OUTPUT_HTML = HERE.parent / "report_harness_eval_fix_rerun.html"

def load_json(path):
    if not path.exists():
        print(f"WARNING: {path} not found")
        return []
    return json.load(open(path))

def main():
    orig = load_json(ORIG_JSON)
    fix1 = load_json(FIX1_JSON)
    fix1_map = {r.get("key", ""): r for r in fix1 if r.get("key")}

    orig_by_repo = defaultdict(lambda: {"total": 0, "resolved": 0, "patch_fail": 0, "test_fail": 0})
    for x in orig:
        repo = x.get("repo", "unknown")
        cls = x.get("classification", "")
        hr = x.get("harness_result", {})
        ev = hr.get("eval", {})
        orig_by_repo[repo]["total"] += 1
        if cls == "resolved":
            orig_by_repo[repo]["resolved"] += 1
        elif not ev.get("patch_applied", False) and ev.get("f2p_total", 0) == 0:
            orig_by_repo[repo]["patch_fail"] += 1
        elif ev.get("patch_applied", False):
            orig_by_repo[repo]["test_fail"] += 1

    fix1_by_repo = defaultdict(lambda: {"total": 0, "resolved": 0, "patch_applied": 0,
                                         "test_run": 0, "flipped": 0, "errors": 0})
    flip_details = []
    for r in fix1:
        repo = r.get("repo", "unknown")
        fix1_by_repo[repo]["total"] += 1
        ne = r.get("new_eval", {})
        oe = r.get("old_eval", {})
        if "error" in r:
            fix1_by_repo[repo]["errors"] += 1
            continue
        if ne.get("resolved"):
            fix1_by_repo[repo]["resolved"] += 1
            if not oe.get("resolved"):
                fix1_by_repo[repo]["flipped"] += 1
                flip_details.append({
                    "instance_id": r.get("instance_id"), "repo": repo, "harness": r.get("harness"),
                    "old": f"resolved={oe.get('resolved')}, patch={oe.get('patch_applied')}, f2p={oe.get('f2p_pass')}/{oe.get('f2p_total')}",
                    "new": f"resolved={ne.get('resolved')}, patch={ne.get('patch_applied')}, f2p={ne.get('f2p_pass')}/{ne.get('f2p_total')}, p2p={ne.get('p2p_pass')}/{ne.get('p2p_total')}",
                })
        if ne.get("patch_applied"):
            fix1_by_repo[repo]["patch_applied"] += 1
        if ne.get("f2p_total", 0) > 0 or ne.get("p2p_total", 0) > 0:
            fix1_by_repo[repo]["test_run"] += 1

    total_flipped = sum(f["flipped"] for f in fix1_by_repo.values())
    total_reval = sum(f["total"] for f in fix1_by_repo.values())
    total_patch_fixed = sum(f["patch_applied"] for f in fix1_by_repo.values())
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    all_repos = sorted(set(list(orig_by_repo.keys()) + list(fix1_by_repo.keys())))

    rows = []
    for repo in all_repos:
        o = orig_by_repo[repo]
        f = fix1_by_repo[repo]
        rows.append(f"<tr><td>{repo}</td><td>{o['total']}</td><td>{o['resolved']}</td><td>{o['patch_fail']}</td>"
                    f"<td>{f['total']}</td><td>{f['resolved']}</td><td>{f['patch_applied']}</td><td>{f['test_run']}</td>"
                    f"<td style='color:{'green' if f['flipped'] > 0 else 'black'};font-weight:bold'>+{f['flipped']}</td>"
                    f"<td>{f['errors']}</td></tr>")

    flip_rows = []
    for fd in sorted(flip_details, key=lambda x: (x["repo"], x["harness"], x["instance_id"])):
        flip_rows.append(f"<tr><td>{fd['instance_id']}</td><td>{fd['repo']}</td><td>{fd['harness']}</td>"
                         f"<td>{fd['old']}</td><td style='color:green;font-weight:bold'>{fd['new']}</td></tr>")

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>Harness Eval Fix Re-run Report — {now}</title>
<style>
body {{ font-family: -apple-system, sans-serif; margin: 2em; background: #f5f5f5; }}
h1 {{ color: #333; }} h2 {{ color: #444; margin-top: 1.5em; }}
table {{ border-collapse: collapse; width: 100%; margin: 1em 0; background: white; }}
th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
th {{ background: #4CAF50; color: white; }} tr:nth-child(even) {{ background: #f9f9f9; }}
.summary {{ background: #e8f5e9; padding: 1em; border-radius: 8px; margin: 1em 0; }}
.fix-desc {{ background: #fff3e0; padding: 1em; border-radius: 8px; margin: 1em 0; }}
code {{ background: #f0f0f0; padding: 2px 6px; border-radius: 3px; }}
</style></head><body>
<h1>Harness Eval Fix Re-run Report</h1><p>Generated: {now}</p>
<div class="summary"><h2>Summary</h2>
<p><strong>Re-evaluated:</strong> {total_reval} entries across {len(fix1_by_repo)} repos</p>
<p><strong>Patch now applies:</strong> {total_patch_fixed} entries (infra fix confirmed)</p>
<p><strong>Newly resolved:</strong> <span style="color:green;font-weight:bold">+{total_flipped}</span> flipped</p></div>
<div class="fix-desc"><h2>Fixes Applied (P0, 2026-10-13)</h2><ol>
<li><strong>matplotlib</strong>: freetype headers+lib in conda env + <code>mplsetup.cfg</code> + <code>MPLSETUPCFG</code> env var</li>
<li><strong>pytest</strong>: <code>SETUPTOOLS_SCM_PRETEND_VERSION=8.0.0</code> env var</li>
<li><strong>Unify</strong>: <code>PIP_NO_BUILD_ISOLATION=1</code> for all repos</li>
<li><strong>sphinx</strong>: jinja2 3.1.4 aliases + git fetch retry for base_commit</li></ol></div>
<h2>Per-Repo Comparison</h2>
<table><thead><tr><th rowspan="2">Repo</th><th colspan="3">Original</th><th colspan="6">Fix1 Re-eval</th></tr>
<tr><th>Total</th><th>Resolved</th><th>Patch Fail</th><th>Re-eval'd</th><th>Resolved</th><th>Patch OK</th><th>Tests Ran</th><th>Flipped</th><th>Errors</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<h2>Newly Resolved (Flipped)</h2><p>Total: <strong>{total_flipped}</strong></p>
{('<table><thead><tr><th>Instance</th><th>Repo</th><th>Harness</th><th>Before</th><th>After</th></tr></thead><tbody>' + ''.join(flip_rows) + '</tbody></table>') if flip_rows else '<p>No instances flipped in this batch.</p>'}
<h2>Methodology</h2><ol>
<li>Loaded kimi_pilot_results.json (original eval)</li>
<li>Filtered non-resolved entries with patches in target repos</li>
<li>Re-ran through r1_eval.py with fixed rootfs + injected env vars</li>
<li>Compared old_eval vs new_eval; "flipped" = not-resolved → resolved</li></ol>
</body></html>"""

    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_HTML, "w") as f:
        f.write(html)
    print(f"Report: {OUTPUT_HTML}")
    print(f"  Re-evaluated: {total_reval}, Patch fixed: {total_patch_fixed}, Flipped: +{total_flipped}")

if __name__ == "__main__":
    main()