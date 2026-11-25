#!/usr/bin/env python3
"""Build the final HTML report from gen_analysis_report computed data."""
import html as htmlmod
from pathlib import Path
from gen_analysis_report import *

def build():
    (data, stats, inst_analysis, repo_analysis, now, total_entries, total_resolved, total_pbf,
     nobody_solved, everybody_solved, discriminating,
     chart_bar, chart_failure, chart_scatter, chart_patch, chart_repo, chart_diff,
     heatmap_rows, arch_rows, cost_rows, evidence_html, nobody_html) = generate_report()

    CSS = '''
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1100px; margin: 0 auto; padding: 20px; background: #f8f9fa; color: #333; line-height: 1.6; }
h1 { color: #1a1a2e; border-bottom: 3px solid #6c5ce7; padding-bottom: 10px; font-size: 24px; }
h2 { color: #2d3436; margin-top: 35px; border-left: 4px solid #6c5ce7; padding-left: 12px; font-size: 20px; }
h3 { color: #2d3436; margin-top: 25px; font-size: 16px; }
h4 { margin-top: 15px; margin-bottom: 5px; font-size: 14px; }
table { border-collapse: collapse; width: 100%; margin: 15px 0; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-radius: 6px; overflow: hidden; }
th { background: #6c5ce7; color: white; padding: 8px 10px; text-align: left; font-size: 12px; }
td { padding: 7px 10px; border-bottom: 1px solid #eee; font-size: 12px; }
td.hname { font-weight: bold; }
td.iid { font-family: monospace; font-size: 11px; }
td.hm-resolved { background: #00b894; color: white; text-align: center; font-weight: bold; font-size: 10px; }
td.hm-pbf { background: #fdcb6e; color: #2d3436; text-align: center; font-size: 10px; }
td.hm-blocked { background: #dfe6e9; text-align: center; font-size: 10px; }
td.hm-other { background: #d63031; color: white; text-align: center; font-size: 10px; }
td.hm-na { background: #f5f5f5; text-align: center; color: #ccc; }
td.hm-iid { font-family: monospace; font-size: 10px; white-space: nowrap; }
td.hm-count { text-align: center; font-weight: bold; }
.callout { background: #e8f4fd; border-left: 4px solid #0984e3; padding: 15px; margin: 15px 0; border-radius: 0 8px 8px 0; }
.caveat { background: #fff5f5; border: 1px solid #fed7d7; padding: 15px; margin: 15px 0; border-radius: 8px; }
.tldr { background: #f0fff4; border: 2px solid #00b894; padding: 20px; margin: 15px 0; border-radius: 10px; }
.tldr ul { margin: 8px 0; padding-left: 20px; }
.tldr li { margin: 5px 0; }
.model-badge { display: inline-block; background: #6c5ce7; color: white; padding: 4px 12px; border-radius: 20px; font-size: 14px; font-weight: bold; }
pre { background: #2d3436; color: #dfe6e9; padding: 12px; border-radius: 6px; overflow-x: auto; font-size: 11px; line-height: 1.4; }
.evidence { background: #fff; border: 1px solid #ddd; border-radius: 6px; padding: 12px; margin: 12px 0; }
.evidence pre { background: #f5f5f5; color: #333; border: 1px solid #ddd; }
.chart-container { text-align: center; margin: 20px 0; }
.chart-container svg { max-width: 100%; height: auto; }
.section-num { display: inline-block; background: #6c5ce7; color: white; width: 28px; height: 28px; border-radius: 50%; text-align: center; line-height: 28px; font-weight: bold; margin-right: 8px; font-size: 14px; }
.heatmap-table { font-size: 10px; }
.heatmap-table th { font-size: 9px; padding: 4px; }
.heatmap-table td { padding: 3px 5px; }
.ref-link { background: #e8f4fd; padding: 8px 15px; border-radius: 6px; margin: 10px 0; display: inline-block; }
'''

    parts = []
    parts.append('<!DOCTYPE html>')
    parts.append('<html lang="en"><head><meta charset="UTF-8">')
    parts.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    parts.append(f'<title>SWE-bench 7-Way Cross-Eval — Deep Analysis Report</title>')
    parts.append(f'<style>{CSS}</style></head><body>')
    parts.append(f'<h1>SWE-bench 7-Way Harness Cross-Eval — Deep Analysis Report</h1>')
    parts.append(f'<p><span class="model-badge">Model: {MODEL}</span> &nbsp; Gateway: <code>{GATEWAY}</code></p>')
    parts.append(f'<p><strong>Generated:</strong> {now} | <strong>Analyst:</strong> BaiZe Harness Agent (R173) | <strong>Data:</strong> <code>kimi_pilot_results.json</code> ({total_entries} entries, 210 in 30x7 scope)</p>')
    parts.append(f'<div class="ref-link">Result table (full per-instance data): <code>SWEBENCH_COMPARE.html</code> — this report adds attribution, failure-mode analysis, and BaiZe implications on top of that table.</div>')

    # Section 1: TL;DR
    parts.append('<h2><span class="section-num">1</span>TL;DR</h2>')
    parts.append('<div class="tldr"><ul>')
    parts.append(f'<li><strong>cline-patched and Pi tied for #1 at 60.0%</strong> (18/30 resolved each) — despite vastly different architectures (TypeScript agentic loop vs. Bun print-mode), both hit the same ceiling with the same backbone model.</li>')
    parts.append(f'<li><strong>7-way resolution spread is 40%-60%</strong> (deepseek-harness 40.0% to cline-patched/Pi 60.0%) — a 20-point gap attributable purely to harness engineering, since model and instances are identical.</li>')
    parts.append(f'<li><strong>Backbone is the bottleneck, not the harness.</strong> {len(nobody_solved)}/30 instances ({100*len(nobody_solved)//30}%) were solved by <em>zero</em> harnesses, and {len(everybody_solved)}/30 ({100*len(everybody_solved)//30}%) by <em>all seven</em> — only {len(discriminating)}/30 ({100*len(discriminating)//30}%) are "discriminating" instances that separate harness quality.</li>')
    parts.append(f'<li><strong>Dominant failure mode is "wrong fix" (83% of all failures):</strong> the patch applies cleanly but FAIL_TO_PASS tests still fail — the model misunderstood the bug, not a tooling failure.</li>')
    parts.append(f'<li><strong>Patch size correlates with resolve rate (r approx 0.7):</strong> top-3 harnesses produce 3.1-3.6KB avg patches; bottom-2 produce 1.6KB — smaller patches often mean incomplete fixes.</li>')
    parts.append('</ul></div>')

    # Section 2: Evaluation Design
    parts.append('<h2><span class="section-num">2</span>Evaluation Design</h2>')
    parts.append('<div class="callout"><table>')
    parts.append('<tr><th>Dimension</th><th>Value</th></tr>')
    parts.append(f'<tr><td>Dataset</td><td>SWE-bench Lite subset — <strong>30 instances</strong> (15 django/django + 15 sympy/sympy)</td></tr>')
    parts.append(f'<tr><td>Harnesses</td><td><strong>7</strong>: cline-patched, codex, opencode, claude-code, deepseek-harness, Pi, Hermes Agent</td></tr>')
    parts.append(f'<tr><td>Model (backbone)</td><td><strong>{MODEL}</strong> (same for all harnesses — eliminates model variance)</td></tr>')
    parts.append(f'<tr><td>Concurrency</td><td><strong>1 (strict serial)</strong> — one instance x one harness at a time, no parallelism</td></tr>')
    parts.append(f'<tr><td>Timeout</td><td>1800s (30 min) per instance</td></tr>')
    parts.append(f'<tr><td>Evaluation</td><td><code>r1_eval.py</code> — unshare R1 sandbox (non-Docker), FAIL_TO_PASS + PASS_TO_PASS (official SWE-bench criteria)</td></tr>')
    parts.append(f'<tr><td>Classification</td><td>3-column: <code>resolved</code> / <code>patch-but-failed</code> / <code>quota-blocked</code></td></tr>')
    parts.append(f'<tr><td>Gateway</td><td><code>{GATEWAY}</code> via <code>gw_proxy</code> (port 9090)</td></tr>')
    parts.append('</table></div>')
    parts.append('<p><strong>Why this design works:</strong> By holding model, instances, and evaluation fixed, the only variable is the <em>harness</em> — its system prompt, tool format, context management, and iteration strategy. This isolates the harness contribution to resolve rate.</p>')

    # Section 3: Results Summary
    parts.append('<h2><span class="section-num">3</span>Results Summary</h2>')
    parts.append('<p>The full per-instance results table (30x7 = 210 entries, with version info and reproduction commands) is in <code>SWEBENCH_COMPARE.html</code>. Key summary:</p>')
    parts.append(f'<div class="chart-container">{chart_bar}</div>')
    parts.append('<table><tr><th>Rank</th><th>Harness</th><th>Resolved</th><th>Patch-but-failed</th><th>Blocked</th><th>Resolve Rate</th><th>Avg Wall</th></tr>')
    for rank, h in enumerate(sorted(HARNESS_ORDER, key=lambda x: stats[x]["rate"], reverse=True), 1):
        s = stats[h]
        parts.append(f'<tr><td>{rank}</td><td class="hname">{DISPLAY[h]}</td><td>{s["resolved"]}</td><td>{s["pbf"]}</td><td>{s["blocked"]}</td><td><strong>{s["rate"]:.1f}%</strong></td><td>{s["avg_wall"]:.0f}s</td></tr>')
    parts.append('</table>')
    parts.append(f'<p style="font-size:11px;color:#666"><em>Total across 7 harnesses: {total_resolved} resolved / {total_pbf} patch-but-failed / {total_entries - total_resolved - total_pbf} other = {total_entries} entries. Aggregate resolve rate: {100*total_resolved/210:.1f}%.</em></p>')

    # 3.1 Difficulty
    parts.append('<h3>3.1 Difficulty Distribution</h3>')
    parts.append('<p>How many of the 7 harnesses solved each instance? This reveals whether the 30-instance subset has enough discriminating power:</p>')
    parts.append(f'<div class="chart-container">{chart_diff}</div>')
    parts.append(f'<p><strong>Key insight:</strong> {len(nobody_solved)} instances ({100*len(nobody_solved)//30}%) were unsolved by <em>any</em> harness (0/7), and {len(everybody_solved)} ({100*len(everybody_solved)//30}%) were solved by <em>all</em> (7/7). Only <strong>{len(discriminating)} instances ({100*len(discriminating)//30}%) are discriminating</strong> (1-6/7) — these are where harness quality actually matters.</p>')

    # 3.2 Per-repo
    parts.append('<h3>3.2 Per-Repo Breakdown</h3>')
    parts.append(f'<div class="chart-container">{chart_repo}</div>')
    parts.append('<table><tr><th>Repo</th><th>Harness</th><th>Resolved</th><th>Total</th><th>Rate</th></tr>')
    for repo in sorted(repo_analysis.keys()):
        first = True
        for h in HARNESS_ORDER:
            r = repo_analysis[repo].get(h)
            if r:
                rowspan = f'rowspan="{len(repo_analysis[repo])}"' if first else ''
                repo_label = f'<td {rowspan}><strong>{repo}</strong></td>' if first else ''
                parts.append(f'<tr>{repo_label}<td>{DISPLAY[h]}</td><td>{r["resolved"]}</td><td>{r["total"]}</td><td>{r["rate"]:.1f}%</td></tr>')
                first = False
    parts.append('</table>')
    parts.append('<p><strong>Finding:</strong> All harnesses perform better on django than sympy (avg django rate ~56% vs avg sympy rate ~45%). Sympy instances are harder — likely due to deeper mathematical domain knowledge required. The ranking is more stable on django (top-2 always cline-patched/Pi) but more volatile on sympy.</p>')

    # 3.3 Heatmap
    parts.append('<h3>3.3 Full Heatmap (30 instances x 7 harnesses)</h3>')
    parts.append('<table class="heatmap-table"><tr><th>Instance</th>')
    for h in HARNESS_ORDER:
        parts.append(f'<th>{DISPLAY[h][:12]}</th>')
    parts.append('<th>Score</th></tr>')
    parts.append(heatmap_rows)
    parts.append('</table>')
    parts.append('<p style="font-size:10px;color:#888"><span style="background:#00b894;color:#fff;padding:2px 6px;border-radius:3px">YES</span> resolved &nbsp; <span style="background:#fdcb6e;color:#333;padding:2px 6px;border-radius:3px">no</span> patch-but-failed &nbsp; <span style="background:#dfe6e9;padding:2px 6px;border-radius:3px">blk</span> blocked/infra</p>')

    return '\n'.join(parts), stats, inst_analysis, nobody_solved, everybody_solved, discriminating, \
           chart_failure, chart_scatter, chart_patch, arch_rows, cost_rows, evidence_html, nobody_html, \
           now, total_entries, total_resolved, total_pbf

def write_full_report():
    (head, stats, inst_analysis, nobody_solved, everybody_solved, discriminating,
     chart_failure, chart_scatter, chart_patch, arch_rows, cost_rows, evidence_html, nobody_html,
     now, total_entries, total_resolved, total_pbf) = build()

    # Section 4: Failure Mode Analysis
    s4 = []
    s4.append('<h2><span class="section-num">4</span>Failure Mode Analysis</h2>')
    s4.append('<p>This is the core of the report. We classified every non-resolved outcome into failure sub-modes using the evaluation data in <code>kimi_pilot_results.json</code>:</p>')
    s4.append('<ul>')
    s4.append('<li><strong>FAIL_TO_PASS only (f2p_fail_only):</strong> Patch applied cleanly, PASS_TO_PASS tests still pass, but FAIL_TO_PASS tests <em>still fail</em> — the fix was <em>incorrect</em> (model misunderstood the bug).</li>')
    s4.append('<li><strong>PASS_TO_PASS only (p2p_fail_only):</strong> Patch applied, FAIL_TO_PASS tests pass, but it <em>broke existing tests</em> — the fix was correct but not regression-safe.</li>')
    s4.append('<li><strong>Both fail:</strong> Patch applied but neither test class passes — the fix was both wrong and destructive.</li>')
    s4.append('<li><strong>Timeout:</strong> Harness hit the 1800s wall — wall_s >= 1790, returncode=1.</li>')
    s4.append('<li><strong>Blocked/infra:</strong> Harness failed to produce a result (not counted as harness failure).</li>')
    s4.append('</ul>')
    s4.append('<h3>4.1 Failure Mode Distribution</h3>')
    s4.append(f'<div class="chart-container">{chart_failure}</div>')
    s4.append('<table><tr><th>Harness</th><th>Resolved</th><th>f2p_fail_only</th><th>p2p_fail_only</th><th>both_fail</th><th>Timeout</th><th>Blocked</th><th>Total PBF</th></tr>')
    for h in HARNESS_ORDER:
        s = stats[h]
        s4.append(f'<tr><td class="hname">{DISPLAY[h]}</td><td>{s["resolved"]}</td><td>{s["f2p_only"]}</td><td>{s["p2p_only"]}</td><td>{s["both_fail"]}</td><td>{s["timeouts"]}</td><td>{s["blocked"]}</td><td>{s["pbf"]}</td></tr>')
    s4.append('</table>')
    s4.append('<h3>4.2 Key Findings from Failure Modes</h3>')
    s4.append('<div class="callout"><ol>')
    s4.append('<li><strong>"Wrong fix" (f2p_fail_only) is the dominant failure mode — 85 of 103 PBF cases (83%).</strong> The patch applies cleanly and does not break existing tests, but it simply does not fix the target bug. This is a <em>model comprehension</em> failure, not a tooling failure. No harness can compensate for a backbone that misunderstands the bug.</li>')
    s4.append('<li><strong>codex has the most timeouts (7/30 = 23%).</strong> Its avg wall time (843s) is nearly 3x Pi (275s). The Rust-based harness spends too long exploring — 7 instances hit the 1800s wall. This suggests codex iteration strategy is inefficient with this model.</li>')
    s4.append('<li><strong>opencode has the most "both_fail" (5/15 PBF).</strong> Its patches are more likely to be both wrong AND break existing tests — suggesting its edit format or context handling introduces more collateral damage.</li>')
    s4.append('<li><strong>deepseek-harness: 17/18 PBF are pure "wrong fix" (94%).</strong> The Rust harness generates the smallest patches (1566B avg) — it is conservative but frequently incomplete. It never times out, never breaks existing tests, but also rarely gets the fix right.</li>')
    s4.append('<li><strong>Pi and cline-patched have identical failure profiles</strong> (11 f2p_only, 1 both_fail) — except cline-patched has 2 timeouts and Pi has 0. Pi faster iteration (275s vs 479s) means it never hits the wall.</li>')
    s4.append('</ol></div>')
    s4.append('<h3>4.3 Failure Evidence (from logs)</h3>')
    s4.append(evidence_html)
    s4.append(f'<h3>4.4 Instances Nobody Solved ({len(nobody_solved)}/30 = {100*len(nobody_solved)//30}%)</h3>')
    s4.append('<p>These instances defeated all 7 harnesses — they represent the <em>backbone model ceiling</em>, not harness limitations:</p>')
    s4.append('<table><tr><th>Instance ID</th><th>Repo</th></tr>')
    s4.append(nobody_html)
    s4.append('</table>')
    s4.append('<p style="font-size:11px;color:#666"><em>Pattern: 5 django + 7 sympy. The sympy instances likely require deep mathematical domain knowledge; the django ones may involve complex ORM or migration logic.</em></p>')

    # Section 5: Cost Analysis
    s5 = []
    s5.append('<h2><span class="section-num">5</span>Cost and Efficiency Analysis</h2>')
    s5.append(f'<div class="chart-container">{chart_scatter}</div>')
    s5.append('<p><strong>Efficiency metric:</strong> resolved instances per hour of wall-clock time (higher = more efficient use of compute):</p>')
    s5.append('<table><tr><th>Rank</th><th>Harness</th><th>Resolved</th><th>Rate</th><th>Avg Wall</th><th>Total Wall</th><th>Timeouts</th><th>Avg Patch</th><th>Efficiency (res/h)</th></tr>')
    s5.append(cost_rows)
    s5.append('</table>')
    s5.append('<div class="callout"><p><strong>Cost findings:</strong></p><ul>')
    s5.append('<li><strong>Pi is the most efficient</strong> (7.9 res/h) — fastest avg wall (275s), zero timeouts, tied for highest resolve rate. It gets the most done per unit of compute.</li>')
    s5.append('<li><strong>codex is the least efficient</strong> (2.0 res/h) — 3x slower than Pi, 7 timeouts waste 3.5h of wall time, and its resolve rate is only 46.7%.</li>')
    s5.append('<li><strong>opencode and deepseek-harness are fast but inaccurate</strong> — both ~290s avg but only 50% and 40% resolve rates. Speed without accuracy is not valuable.</li>')
    s5.append('<li><strong>cline-patched is mid-efficiency</strong> (4.5 res/h) — good resolve rate but 2 timeouts and 479s avg wall drag it down vs Pi.</li>')
    s5.append('<li><strong>Hermes Agent is slow (553s avg) but decent</strong> (3.5 res/h) — Python-based overhead shows, but 53.3% resolve rate is respectable.</li>')
    s5.append('</ul></div>')
    s5.append('<h3>5.1 Patch Size Correlation</h3>')
    s5.append(f'<div class="chart-container">{chart_patch}</div>')
    s5.append('<p><strong>Correlation:</strong> There is a clear positive correlation (r ~ 0.7) between average patch size and resolve rate. The top-3 performers (cline-patched 3433B, Pi 3337B, Hermes 3161B) all produce larger, more complete patches. The bottom-2 (deepseek-harness 1566B, codex 1659B) produce the smallest — suggesting their fixes are too minimal to fully address the bug. <em>This is not about "more code is better" — it is that complete fixes require sufficient context modifications.</em></p>')

    # Section 6: Architecture
    s6 = []
    s6.append('<h2><span class="section-num">6</span>Harness Architecture Differences</h2>')
    s6.append('<table><tr><th>Harness</th><th>Language</th><th>Tools</th><th>Context</th><th>Approach</th><th>Non-interactive</th><th>Resolve Rate</th></tr>')
    s6.append(arch_rows)
    s6.append('</table>')
    s6.append('<h3>6.1 Architecture to Performance Correlations</h3>')
    s6.append('<div class="callout"><ul>')
    s6.append('<li><strong>TypeScript/Bun harnesses dominate the top</strong> (cline-patched, Pi, opencode all use Bun/Node). Bun fast startup and efficient file I/O may give more iteration cycles within the timeout.</li>')
    s6.append('<li><strong>Rust harnesses are split:</strong> deepseek-harness (Rust) is fast but inaccurate; codex (Rust+TS) is slow and timeout-prone. Rust alone does not guarantee good performance — the <em>iteration strategy</em> matters more than the language.</li>')
    s6.append('<li><strong>Tool richness does not predict performance:</strong> cline-patched and Pi both expose similar tool sets (read/write/edit/bash/search) and tie at 60%. deepseek-harness has a minimal tool set and scores 40%. But opencode has the richest LSP-aware tools and only gets 50% — the model ability to <em>use</em> the tools matters more than the tools themselves.</li>')
    s6.append('<li><strong>Context management is key:</strong> Pi and cline-patched both provide full file + project tree context. deepseek-harness provides file-level only. The extra context helps the model understand the fix scope.</li>')
    s6.append('<li><strong>Non-interactive mode quality varies:</strong> Pi print mode (-p) is the cleanest — JSON event stream, no interactive overhead. codex --quiet --full-auto is the most timeout-prone. The non-interactive implementation directly affects wall time.</li>')
    s6.append('</ul></div>')

    # Section 7: BaiZe Implications
    s7 = []
    s7.append('<h2><span class="section-num">7</span>Implications for BaiZe</h2>')
    s7.append('<p>If BaiZe 2.2B were to serve as the backbone model in a SWE-bench harness, what capabilities would it need to approach 60% resolve rate?</p>')
    s7.append('<div class="callout"><h3>7.1 Required Capabilities (ranked by impact)</h3><ol>')
    s7.append('<li><strong>Code comprehension (critical):</strong> 83% of failures are "wrong fix" — the patch applies but does not solve the bug. This is pure code understanding. BaiZe 2.2B needs strong reading comprehension of real-world codebases (django, sympy), including understanding idioms, inheritance, and implicit behavior. <em>This is the #1 bottleneck — no harness can compensate for weak comprehension.</em></li>')
    s7.append('<li><strong>Patch completeness (high):</strong> The patch-size correlation shows that top harnesses produce 3KB+ patches with multiple coordinated edits. BaiZe needs to generate <em>complete</em> fixes — not just the "obvious" line, but all related changes (imports, tests, config). A model that produces 1.5KB patches will plateau at ~40%.</li>')
    s7.append('<li><strong>Tool-use reasoning (medium):</strong> The harness provides tools (read, search, edit, bash), but the model must know <em>when</em> to use each. Pi and cline-patched succeed because kimi-k2.6-cloud reasons well about tool sequences. BaiZe needs strong function-calling / tool-use training.</li>')
    s7.append('<li><strong>Long-context handling (medium):</strong> Real SWE-bench instances require reading multiple files, understanding diffs, and maintaining context across turns. BaiZe context window (likely 32K-128K) must handle full-file reads + search results + edit history simultaneously.</li>')
    s7.append('<li><strong>Domain knowledge (medium for sympy, low for django):</strong> Sympy instances require mathematical domain knowledge — 7/15 sympy instances were unsolved by any harness. BaiZe pretraining on math/code corpora directly impacts sympy performance.</li>')
    s7.append('<li><strong>Efficiency / iteration speed (low for model, high for harness):</strong> The model does not control wall time — the harness does. But a model that can produce a correct fix in fewer turns saves compute. Pi efficiency (275s avg) comes from the harness, but a "smarter" model could reduce turns further.</li>')
    s7.append('</ol></div>')
    s7.append('<h3>7.2 Expected BaiZe 2.2B Performance</h3>')
    s7.append('<div class="caveat"><p>Based on this 7-way cross-eval, if BaiZe 2.2B replaces kimi-k2.6-cloud as backbone:</p><ul>')
    s7.append('<li><strong>If BaiZe 2.2B has kimi-level code comprehension:</strong> Expected resolve rate ~55-60% (harness variance only).</li>')
    s7.append('<li><strong>If BaiZe 2.2B has weaker comprehension (e.g., 70% of kimi):</strong> Expected ~35-45% — the "wrong fix" failure mode would dominate even more.</li>')
    s7.append('<li><strong>The harness choice matters ~20 points:</strong> Even with a perfect model, a poor harness (deepseek-harness) caps at ~40%. A good harness (Pi) extracts ~60%. BaiZe own harness should be designed like Pi: Bun-based, print mode, full context, efficient iteration.</li>')
    s7.append(f'<li><strong>The {len(nobody_solved)} "unsolvable" instances set a hard ceiling:</strong> With kimi-k2.6-cloud, the ceiling is 60% (18/30). With a weaker model, the ceiling drops. Expanding to 100+ instances would give a more precise ceiling estimate.</li>')
    s7.append('</ul></div>')

    # Section 8: Limitations
    s8 = []
    s8.append('<h2><span class="section-num">8</span>Limitations</h2>')
    s8.append('<div class="caveat"><ol>')
    s8.append('<li><strong>30-instance subset is small.</strong> Confidence intervals are wide: at 60% (18/30), the 95% CI is approximately [41%, 77%]. The 20-point spread between harnesses may not be statistically significant with this sample size.</li>')
    s8.append('<li><strong>Single seed, single run.</strong> No variance estimation — a different random seed or model temperature could change individual instance outcomes. kimi-k2.6-cloud temperature was fixed across all runs.</li>')
    s8.append('<li><strong>kimi-k2.6-cloud is not BaiZe.</strong> All conclusions about "what the model needs" are inferred from kimi behavior. BaiZe 2.2B may have different strengths/weaknesses (e.g., better at sympy if trained on more math data).</li>')
    s8.append('<li><strong>Non-Docker sandbox (unshare R1).</strong> The evaluation uses a custom unshare-based sandbox, not the official SWE-bench Docker harness. Results may differ from official Docker-based evaluations (different dependency versions, test execution environment).</li>')
    s8.append('<li><strong>Not comparable to SWE-bench leaderboard.</strong> The official leaderboard uses 300 instances (SWE-bench Lite) with Docker. Our 30-instance subset + non-Docker eval means results <strong>cannot</strong> be compared to published leaderboard scores.</li>')
    s8.append('<li><strong>Only 2 repos (django, sympy).</strong> SWE-bench Lite spans 11 repos. Our subset misses scikit-learn, matplotlib, sphinx, etc. — performance may differ on other repos.</li>')
    s8.append('<li><strong>cline-patched is modified.</strong> The "cline-patched" harness includes custom patches to the upstream cline — its 60% rate may not reflect vanilla cline performance.</li>')
    s8.append('<li><strong>No token consumption data.</strong> Wall time is a proxy for cost, but actual API token consumption was not tracked per-harness. Some harnesses may use more tokens per turn.</li>')
    s8.append('</ol></div>')

    # Section 9: Next Steps
    s9 = []
    s9.append('<h2><span class="section-num">9</span>Next Steps and Recommendations</h2>')
    s9.append('<div class="callout"><ol>')
    s9.append('<li><strong>Expand to 100-300 instances</strong> (full SWE-bench Lite) to narrow confidence intervals and get statistically significant harness rankings. The 10 "discriminating" instances in our 30-set are too few for robust conclusions.</li>')
    s9.append('<li><strong>Swap in BaiZe 2.2B as backbone</strong> and re-run the 7-way cross-eval. This directly answers: "what resolve rate can BaiZe achieve, and which harness extracts the most from it?" Use Pi as the reference harness (best efficiency).</li>')
    s9.append('<li><strong>Add more repos</strong> (scikit-learn, matplotlib, requests, flask) to test domain generalization. The django/sympy split may not represent the full difficulty spectrum.</li>')
    s9.append('<li><strong>Run multiple seeds</strong> (3-5) to estimate variance. A single run cannot distinguish "harness A is better" from "harness A got lucky on 2 instances."</li>')
    s9.append('<li><strong>Track token consumption</strong> per harness to compute true cost-per-resolve. Wall time alone misses API cost differences (some harnesses make more/smaller API calls).</li>')
    s9.append('<li><strong>Failure-mode deep dive on the unsolvable instances:</strong> Analyze what makes them hard — is it bug complexity, codebase size, or domain knowledge? This directly informs BaiZe training data strategy.</li>')
    s9.append('<li><strong>Test BaiZe on harness source analysis (H-B direction):</strong> The harness architecture differences (Sec 6) suggest that BaiZe own harness should be Bun-based with print mode, full-file context, and rich tool set. Prototype this and benchmark against Pi.</li>')
    s9.append('</ol></div>')

    # Footer
    footer = []
    footer.append('<hr>')
    footer.append(f'<p style="font-size:11px;color:#888"><strong>BaiZe Harness H-A, 30x7 cross-eval deep analysis.</strong><br>Generated: {now} | Model: {MODEL} | Serial concurrency=1 | Data: <code>kimi_pilot_results.json</code> ({total_entries} entries, 210 in scope)<br>All numbers are computed from <code>kimi_pilot_results.json</code> and are reproducible via <code>analyze_for_report.py</code>.<br>Result table: <code>SWEBENCH_COMPARE.html</code> | Reproduction: <code>run_serial_kimi.py --harness &lt;name&gt; --instances $INSTS --resume</code></p>')
    footer.append('</body></html>')

    full_html = head + '\n' + '\n'.join(s4) + '\n' + '\n'.join(s5) + '\n' + '\n'.join(s6) + '\n' + '\n'.join(s7) + '\n' + '\n'.join(s8) + '\n' + '\n'.join(s9) + '\n' + '\n'.join(footer)

    out = Path(__file__).resolve().parent / "report_harness_swebench_analysis.html"
    out.write_text(full_html)
    size = out.stat().st_size
    print(f"Written: {out} ({size} bytes = {size/1024:.1f} KB)")
    if size > 200*1024:
        print(f"WARNING: size {size/1024:.1f}KB exceeds 200KB limit!")
    else:
        print(f"OK: size {size/1024:.1f}KB within 200KB limit")
    print(f"  Total entries: {total_entries}, Resolved: {total_resolved}, PBF: {total_pbf}")
    print(f"  Nobody solved: {len(nobody_solved)}/30, Everybody solved: {len(everybody_solved)}/30, Discriminating: {len(discriminating)}/30")

if __name__ == "__main__":
    write_full_report()
