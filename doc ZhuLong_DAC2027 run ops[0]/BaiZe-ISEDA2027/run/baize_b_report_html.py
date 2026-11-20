#!/usr/bin/env python3
"""Generate self-contained HTML report for B: 长上下文适配 4096→8192+.
Reads b_longctx_comparison.json + passkey results and produces report_pretrain_longctx.html.
"""
import json, os, sys, datetime

COMP_JSON = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p5b/lm_eval_longctx/b_longctx_comparison.json"
PASSKEY_JSON = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p5b/lm_eval_longctx/passkey_results.json"
OUT_HTML = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/report_pretrain_longctx.html"

TASK_LABELS = {
    "hellaswag": "HellaSwag", "arc_easy": "ARC-Easy",
    "mmlu": "MMLU", "bbh_zeroshot": "BBH",
}

def fmt_pct(v):
    return "N/A" if v is None else f"{v*100:.2f}%"

def main():
    if not os.path.exists(COMP_JSON):
        print(f"WARNING: {COMP_JSON} not found — using empty data", file=sys.stderr)
        comp = {"baseline": {}, "abf_1e6": {}, "passkey": {}}
    else:
        comp = json.load(open(COMP_JSON))
    baseline = comp.get("baseline", {})
    abf = comp.get("abf_1e6", {})
    passkey = comp.get("passkey", {})

    # Also try loading passkey separately if not in comp
    if not passkey and os.path.exists(PASSKEY_JSON):
        try:
            pk_data = json.load(open(PASSKEY_JSON))
            for r in pk_data.get("results", []):
                passkey[r["context"]] = r["passkey_acc"]
        except Exception:
            pass

    all_tasks = sorted(set(list(baseline.keys()) + list(abf.keys())))
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # Build comparison table
    comp_rows = ""
    for t in all_tasks:
        b = baseline.get(t); a = abf.get(t)
        bs = fmt_pct(b); as_ = fmt_pct(a)
        if b is not None and a is not None:
            delta = f"{(a-b)*100:+.2f}pp"
            dcls = "neg" if a < b else ("pos" if a > b else "zero")
        else:
            delta = "N/A"; dcls = "na"
        label = TASK_LABELS.get(t, t)
        comp_rows += f"  <tr><td class='task'>{label}</td><td>{bs}</td><td>{as_}</td><td class='{dcls}'>{delta}</td></tr>\n"

    # Passkey table
    pk_rows = ""
    if passkey:
        for ctx in sorted(passkey.keys()):
            acc = passkey[ctx]
            pk_rows += f"  <tr><td>{ctx}</td><td>{acc*100:.1f}%</td></tr>\n"
    else:
        pk_rows = "  <tr><td colspan='2' class='na'>Passkey results not yet available</td></tr>\n"

    is_complete = len(abf) >= 4 and len(baseline) >= 4
    badge = "✅ COMPLETE" if is_complete else f"🔄 IN PROGRESS (ABF:{len(abf)}/4, baseline:{len(baseline)}/4)"

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BaiZe Stage(i) · Long Context 4096→8192+ Adaptation</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
       margin: 2rem auto; max-width: 1000px; color: #1a1a2e; background: #f5f5fa; }}
h1 {{ color: #16213e; border-bottom: 3px solid #0f3460; padding-bottom: .5rem; }}
h2 {{ color: #0f3460; margin-top: 2rem; }}
.meta {{ color: #666; font-size: .9rem; margin-bottom: 1rem; }}
.badge {{ display: inline-block; padding: .3rem .8rem; border-radius: 1rem; font-weight: 600; font-size: .85rem; }}
.badge.complete {{ background: #d4edda; color: #155724; }}
.badge.progress {{ background: #fff3cd; color: #856404; }}
table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; font-size: .9rem; }}
th, td {{ border: 1px solid #ccc; padding: .5rem .7rem; text-align: center; }}
th {{ background: #0f3460; color: #fff; }}
td.task {{ font-weight: 600; text-align: left; }}
td.neg {{ color: #c62828; font-weight: 600; }}
td.pos {{ color: #2e7d32; font-weight: 600; }}
td.na {{ color: #ccc; }}
tr:nth-child(even) {{ background: #f8f8fc; }}
.note {{ background: #e3f2fd; border-left: 4px solid #2196f3; padding: .8rem 1rem; margin: 1rem 0; border-radius: .3rem; }}
.warn {{ background: #fff3e0; border-left: 4px solid #ff9800; padding: .8rem 1rem; margin: 1rem 0; border-radius: .3rem; }}
.footer {{ margin-top: 2rem; color: #999; font-size: .8rem; border-top: 1px solid #ddd; padding-top: .5rem; }}
</style></head><body>
<h1>BaiZe Stage(i) · Long Context 4096→8192+ Adaptation</h1>
<div class="meta">Model: Mamba2-hybrid 2.22B (iter_4771, 20B tokens)<br>
ABF config: max_pos=8192, rope_theta=1e6 (symlinked weights, config-only change)<br>
Generated: {now} · <span class="badge {'complete' if is_complete else 'progress'}">{badge}</span></div>
<div class="note"><strong>Question:</strong> Does ABF (Adjusted Base Frequency, rope_theta=1e6, max_pos=8192)
degrade short-context zero-shot performance?<br>
<strong>B1 context:</strong> PPL at 4K goes 75→83 with ABF — this eval verifies downstream degradation.<br>
<strong>Why this matters:</strong> README risk #3 says "4096 对 agentic 轨迹过短";
P-9.11② 128K failed (max_pos=4096). ABF is the simplest extension method.</div>
<h2>Zero-Shot Comparison: Baseline (4K) vs ABF (8K)</h2>
<table><thead><tr><th>Task</th><th>Baseline (4K)</th><th>ABF 1e6 (8K)</th><th>Delta</th></tr></thead>
<tbody>{comp_rows}</tbody></table>
<h2>Passkey Retrieval (4K / 8K)</h2>
<table><thead><tr><th>Context Length</th><th>Accuracy</th></tr></thead>
<tbody>{pk_rows}</tbody></table>
<div class="warn"><strong>RoPE scope note:</strong> Only 4 of 56 layers use RoPE attention
(24 Mamba2 SSM layers have no positional encoding, 28 MLP layers).
ABF only affects those 4 attention layers ⇒ benefit may be limited.
This eval tests whether the degradation from B1 (PPL 75→83) manifests in downstream tasks.</div>
<h2>Interpretation Guide</h2>
<ul>
<li><strong>Small delta (< 2pp)</strong>: ABF is safe — short-context performance preserved while extending to 8K.</li>
<li><strong>Large negative delta (> 2pp)</strong>: ABF degrades short-context — need short-context fine-tuning after extension.</li>
<li><strong>Passkey 4K ≈ 8K</strong>: Model can retrieve information at 8K as well as 4K (extension works).</li>
<li><strong>Passkey 8K << 4K</strong>: Extension didn't actually help — model still effectively limited to 4K.</li>
</ul>
<div class="footer">Data: <code>b_longctx_comparison.json</code> + <code>passkey_results.json</code><br>
Collector: <code>baize_b_collect.py</code> · Eval: <code>baize_b_longctx_eval.sh</code></div>
</body></html>"""

    with open(OUT_HTML, "w") as f:
        f.write(html)
    print(f"HTML written to {OUT_HTML} ({os.path.getsize(OUT_HTML)} bytes)")

if __name__ == "__main__":
    main()
