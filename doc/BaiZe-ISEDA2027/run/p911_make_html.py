#!/usr/bin/env python3
"""Generate P-9.11 HTML report from benchmark JSON results."""
import json, sys, os

def load_results(path):
    with open(path) as f:
        return json.load(f)

def fmt(v, suffix=""):
    if v is None: return "—"
    if isinstance(v, float): return f"{v:.2f}{suffix}"
    return f"{v}{suffix}"

def make_table(hybrid, dense):
    ctxs = sorted(set(r["ctx"] for r in hybrid["results"] if "error" not in r))
    batches = sorted(set(r["batch"] for r in hybrid["results"] if "error" not in r))
    rows = []
    for ctx in ctxs:
        for bs in batches:
            hr = next((r for r in hybrid["results"] if r.get("ctx")==ctx and r.get("batch")==bs and "error" not in r), None)
            dr = next((r for r in dense["results"] if r.get("ctx")==ctx and r.get("batch")==bs and "error" not in r), None)
            rows.append((ctx, bs, hr, dr))
    return rows

def build_html(hybrid, dense):
    rows = make_table(hybrid, dense)
    html = []
    html.append("<!DOCTYPE html><html><head><meta charset='utf-8'>")
    html.append("<title>P-9.11 sglang Production-Stack: BaiZe vs MiniCPM5-2B</title>")
    html.append("<style>body{font-family:monospace;margin:20px;max-width:1400px}")
    html.append("table{border-collapse:collapse;width:100%}th,td{border:1px solid #999;padding:4px 8px;text-align:right}")
    html.append("th{background:#e0e0e0}tr:hover{background:#f5f5f5}")
    html.append(".ratio{color:#0066cc;font-weight:bold}.err{color:red}")
    html.append("h2{margin-top:30px}pre{background:#f0f0f0;padding:10px;overflow-x:auto}</style></head><body>")
    html.append("<h1>P-9.11 · sglang 生产栈 —— BaiZe(Mamba2-hybrid 2B) vs MiniCPM5-2B 推理对比</h1>")
    html.append(f"<p>生成时间: {hybrid.get('timestamp','')} | sglang 0.5.9 | torch 2.9.1+cu128 | GPU: H100 80GB</p>")
    html.append("<h2>测试矩阵</h2>")
    html.append("<p>context ∈ {4K,16K,64K,128K} × batch ∈ {1,8}, gen_len=64</p>")
    html.append("<h2>核心结果表</h2>")
    html.append("<table><tr><th>ctx</th><th>bs</th>")
    html.append("<th>hybrid TTFT(ms)</th><th>dense TTFT(ms)</th><th>TTFT比值</th>")
    html.append("<th>hybrid prefill(tok/s)</th><th>dense prefill(tok/s)</th><th>prefill比值</th>")
    html.append("<th>hybrid decode(tok/s)</th><th>dense decode(tok/s)</th><th>decode比值</th>")
    html.append("<th>hybrid VRAM(GB)</th><th>dense VRAM(GB)</th><th>VRAM比值</th></tr>")
    for ctx, bs, hr, dr in rows:
        html.append(f"<tr><td>{ctx}</td><td>{bs}</td>")
        if hr and dr:
            ht, dt = hr.get("ttft_s"), dr.get("ttft_s")
            hp, dp = hr.get("prefill_tok_s"), dr.get("prefill_tok_s")
            hd, dd = hr.get("decode_tok_s"), dr.get("decode_tok_s")
            hv, dv = hr.get("peak_vram_gb"), dr.get("peak_vram_gb")
            ttft_r = f"{dt/ht:.2f}x" if ht and dt else "—"
            prefill_r = f"{hp/dp:.2f}x" if hp and dp else "—"
            decode_r = f"{hd/dd:.2f}x" if hd and dd else "—"
            vram_r = f"{hv/dv:.2f}x" if hv and dv else "—"
            html.append(f"<td>{fmt(ht*1000)}</td><td>{fmt(dt*1000)}</td><td class='ratio'>{ttft_r}</td>")
            html.append(f"<td>{fmt(hp)}</td><td>{fmt(dp)}</td><td class='ratio'>{prefill_r}</td>")
            html.append(f"<td>{fmt(hd)}</td><td>{fmt(dd)}</td><td class='ratio'>{decode_r}</td>")
            html.append(f"<td>{fmt(hv)}</td><td>{fmt(dv)}</td><td class='ratio'>{vram_r}</td>")
        elif hr:
            html.append(f"<td>{fmt(hr.get('ttft_s',0)*1000)}</td><td>—</td><td>—</td>")
            html.append(f"<td>{fmt(hr.get('prefill_tok_s'))}</td><td>—</td><td>—</td>")
            html.append(f"<td>{fmt(hr.get('decode_tok_s'))}</td><td>—</td><td>—</td>")
            html.append(f"<td>{fmt(hr.get('peak_vram_gb'))}</td><td>—</td><td>—</td>")
        elif dr:
            html.append(f"<td>—</td><td>{fmt(dr.get('ttft_s',0)*1000)}</td><td>—</td>")
            html.append(f"<td>—</td><td>{fmt(dr.get('prefill_tok_s'))}</td><td>—</td>")
            html.append(f"<td>—</td><td>{fmt(dr.get('decode_tok_s'))}</td><td>—</td>")
            html.append(f"<td>—</td><td>{fmt(dr.get('peak_vram_gb'))}</td><td>—</td>")
        else:
            html.append("<td colspan='12'>—</td>")
        html.append("</tr>")
    html.append("</table>")
    html.append("<h2>详细结果 — Hybrid (Mamba2-hybrid 2.22B)</h2>")
    html.append("<pre>" + json.dumps(hybrid, indent=2) + "</pre>")
    html.append("<h2>详细结果 — Dense (MiniCPM5-2B 2.512B)</h2>")
    html.append("<pre>" + json.dumps(dense, indent=2) + "</pre>")
    html.append("</body></html>")
    return "\n".join(html)

if __name__ == "__main__":
    hybrid_path = sys.argv[1] if len(sys.argv) > 1 else "p911_hybrid_results.json"
    dense_path = sys.argv[2] if len(sys.argv) > 2 else "p911_dense_results.json"
    out_path = sys.argv[3] if len(sys.argv) > 3 else "report_pretrain_p911_sglang.html"
    hybrid = load_results(hybrid_path)
    dense = load_results(dense_path)
    html = build_html(hybrid, dense)
    out_full = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", out_path)
    with open(out_full, "w") as f:
        f.write(html)
    print(f"HTML report saved to {out_full} ({len(html)} bytes)")
