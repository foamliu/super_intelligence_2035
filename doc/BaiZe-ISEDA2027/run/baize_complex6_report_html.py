#!/usr/bin/env python3
"""Generate self-contained HTML report for A: 复杂推理 6 集 scaling.
Reads complex6_summary.json and produces report_pretrain_complex6_scaling.html.
"""
import json, os, sys, datetime

SUMMARY = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p5b/lm_eval_complex/complex6_summary.json"
OUT_HTML = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/report_pretrain_complex6_scaling.html"

TASK_LABELS = {
    "gsm8k": "GSM8K", "hendrycks_math500": "MATH-500", "mmlu": "MMLU",
    "bbh_zeroshot": "BBH", "humaneval": "HumanEval", "mbpp": "MBPP",
}
TASK_ORDER = ["gsm8k", "hendrycks_math500", "mmlu", "bbh_zeroshot", "humaneval", "mbpp"]

def fmt_pct(v):
    return "N/A" if v is None else f"{v*100:.2f}%"

def fmt_tok(v):
    if v is None: return "N/A"
    if v >= 1e9: return f"{v/1e9:.1f}B"
    if v >= 1e6: return f"{v/1e6:.0f}M"
    return f"{v:.0f}"

def main():
    if not os.path.exists(SUMMARY):
        print(f"ERROR: {SUMMARY} not found", file=sys.stderr); sys.exit(1)
    data = json.load(open(SUMMARY))
    iters = data["iters"]; tokens = data["tokens"]; table = data["table"]
    tasks = [t for t in TASK_ORDER if t in data.get("tasks", TASK_ORDER)]

    rows_html = ""
    for it in iters:
        tok = tokens.get(it)
        cells = [f"<td class='iter'>{it}</td>", f"<td class='tok'>{fmt_tok(tok)}</td>"]
        for t in tasks:
            v = table.get(it, {}).get(t)
            cls = "val" if v is not None else "na"
            cells.append(f"<td class='{cls}'>{fmt_pct(v)}</td>")
        vals = [table.get(it, {}).get(t) for t in tasks if table.get(it, {}).get(t) is not None]
        avg = sum(vals)/len(vals) if vals else None
        cells.append(f"<td class='avg'>{fmt_pct(avg)}</td>")
        rows_html += f"  <tr>{''.join(cells)}</tr>\n"

    scaling_sections = ""
    for t in tasks:
        label = TASK_LABELS.get(t, t)
        points = []
        for it in iters:
            v = table.get(it, {}).get(t); tok = tokens.get(it, 0)
            if v is not None:
                points.append(f"({tok/1e9:.2f}B,{v*100:.2f}%)")
        pts_str = ", ".join(points) if points else "(no data)"
        scaling_sections += f'\n    <div class="task-card">\n      <h3>{label}</h3>\n      <div class="scaling-points">{pts_str}</div>\n    </div>'

    total = len(iters) * len(tasks)
    filled = sum(1 for it in iters for t in tasks if table.get(it, {}).get(t) is not None)
    is_complete = filled == total
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    badge = "✅ COMPLETE" if is_complete else f"🔄 IN PROGRESS ({filled}/{total} cells)"

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BaiZe Stage(i) · Complex Reasoning 6-Set Scaling</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
       margin: 2rem auto; max-width: 1100px; color: #1a1a2e; background: #f5f5fa; }}
h1 {{ color: #16213e; border-bottom: 3px solid #0f3460; padding-bottom: .5rem; }}
h2 {{ color: #0f3460; margin-top: 2rem; }}
h3 {{ color: #16213e; margin: 0.5rem 0; }}
.meta {{ color: #666; font-size: .9rem; margin-bottom: 1rem; }}
.badge {{ display: inline-block; padding: .3rem .8rem; border-radius: 1rem; font-weight: 600; font-size: .85rem; }}
.badge.complete {{ background: #d4edda; color: #155724; }}
.badge.progress {{ background: #fff3cd; color: #856404; }}
table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; font-size: .9rem; }}
th, td {{ border: 1px solid #ccc; padding: .5rem .7rem; text-align: center; }}
th {{ background: #0f3460; color: #fff; font-weight: 600; }}
td.iter {{ font-weight: 700; background: #e8eaf6; }}
td.tok {{ color: #555; font-size: .85rem; }}
td.na {{ color: #ccc; }}
td.avg {{ font-weight: 600; background: #f0f4c3; }}
tr:nth-child(even) {{ background: #f8f8fc; }}
.task-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 1rem 0; }}
.task-card {{ background: #fff; border: 1px solid #ddd; border-radius: .5rem; padding: .8rem; }}
.scaling-points {{ font-family: monospace; font-size: .8rem; color: #555; }}
.note {{ background: #e3f2fd; border-left: 4px solid #2196f3; padding: .8rem 1rem; margin: 1rem 0; border-radius: .3rem; }}
.footer {{ margin-top: 2rem; color: #999; font-size: .8rem; border-top: 1px solid #ddd; padding-top: .5rem; }}
</style></head><body>
<h1>BaiZe Stage(i) · Complex Reasoning 6-Set Scaling</h1>
<div class="meta">Model: Mamba2-hybrid 2.22B (P-5b) · 6 ckpts (655M–20B tokens)<br>
Tasks: GSM8K, MATH-500, MMLU, BBH, HumanEval, MBPP · zero-shot<br>
Generated: {now} · <span class="badge {'complete' if is_complete else 'progress'}">{badge}</span></div>
<div class="note"><strong>Context:</strong> Operator approved "A (复杂推理 6 集)" 2026-10-06.
Task book requires "常识 8 集 + 复杂 6 集"两条曲线; common-sense 8-set done in P-5b/P-6.
HumanEval/MBPP require <code>HF_ALLOW_CODE_EVAL=1</code> + <code>--confirm_run_unsafe_code</code>;
all scores 0% (model at 20B tokens cannot generate valid code — expected floor).</div>
<h2>Scaling Table</h2>
<table><thead><tr><th>iter</th><th>tokens</th>
{''.join(f'<th>{TASK_LABELS.get(t,t)}</th>' for t in tasks)}<th>Avg</th></tr></thead>
<tbody>{rows_html}</tbody></table>
<h2>Per-Task Scaling (tokens → score%)</h2>
<div class="task-grid">{scaling_sections}
</div>
<h2>Key Observations</h2>
<ul>
<li><strong>BBH</strong>: Clearest scaling signal 3.1%→14.3% (peak @2.62B tok), then fluctuates.</li>
<li><strong>MMLU</strong>: ~23–23.6% flat (near 4-choice floor for 2B at 20B tok).</li>
<li><strong>GSM8K/MATH-500</strong>: Near-zero across all ckpts.</li>
<li><strong>HumanEval/MBPP</strong>: 0% — code gen beyond current capability.</li>
<li><strong>Conclusion</strong>: At 20B tokens, model is at floor for all complex reasoning tasks.
This quantifies the gap for Stage (ii) SFT/RL. The measurement itself is the conclusion.</li>
</ul>
<div class="footer">Data: <code>complex6_summary.json</code> · Collector: <code>baize_complex6_collect.py</code><br>
Eval: <code>baize_complex6_eval_v2.sh</code> · HumanEval/MBPP fix: <code>baize_complex6_humaneval_mbpp_fix.sh</code></div>
</body></html>"""

    with open(OUT_HTML, "w") as f:
        f.write(html)
    print(f"HTML written to {OUT_HTML} ({os.path.getsize(OUT_HTML)} bytes)")
    print(f"Completeness: {filled}/{total} cells filled")

if __name__ == "__main__":
    main()
