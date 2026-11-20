#!/usr/bin/env python3
"""P-9.11-F: Generate Chinese HTML comparison report from benchmark results."""
import json, os, glob, sys
from datetime import datetime

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
RESULT_DIR = os.path.join(RUN_DIR, "p911f_results")
REPORT_PATH = os.path.join(RUN_DIR, "report_pretrain_baize_vs_dense_fair_zh.html")

CTX_LABELS = {131072:"128K",262144:"256K",524288:"512K",1048576:"1M",2097152:"2M",4194304:"4M",8388608:"8M"}
MODELS = ["hybrid_2.220b","dense_matched_2.229b","dense_ref_2.512b"]
M_SHORT = {"hybrid_2.220b":"Hybrid","dense_matched_2.229b":"Dense-Match","dense_ref_2.512b":"Dense-Ref"}
M_COLOR = {"hybrid_2.220b":"#e74c3c","dense_matched_2.229b":"#3498db","dense_ref_2.512b":"#2ecc71"}

def load_results():
    data = {}
    for f in sorted(glob.glob(os.path.join(RESULT_DIR, "bench_*.json"))):
        try:
            r = json.load(open(f))
            base = os.path.basename(f).replace("bench_","").replace(".json","")
            parts = base.split("_")
            gi = next((i for i,p in enumerate(parts) if p.startswith("gpu")), len(parts))
            mk = "_".join(parts[:gi])
            data[(mk, r.get("mem_frac",0.6), r.get("ctx",0), r.get("batch",1))] = r
        except: pass
    return data

def gv(data,mk,mf,ctx,bs,field):
    r = data.get((mk,mf,ctx,bs))
    if not r: return None
    if r.get("error"): return None  # don't return values from errored/rejected results
    return r.get(field)

def fmt(v):
    if v is None: return "—"
    if abs(v)>=1e6: return f"{v/1e6:.1f}M"
    if abs(v)>=1e3: return f"{v/1e3:.1f}K"
    return f"{v:.1f}"

def ratio(h,d):
    if not h or not d: return "—"
    return f"{h/d:.2f}×"

def gen_table(data,field,mf,bs):
    ctxs = sorted(CTX_LABELS.keys())
    rows = []
    for ctx in ctxs:
        row = {"ctx": CTX_LABELS[ctx]}
        vals = {}
        for mk in MODELS:
            v = gv(data,mk,mf,ctx,bs,field)
            vals[mk] = v
            row[mk] = fmt(v) if field != "peak_vram_gb" else (f"{v:.2f}" if v else "—")
        row["rdm"] = ratio(vals["hybrid_2.220b"],vals["dense_matched_2.229b"])
        row["rdr"] = ratio(vals["hybrid_2.220b"],vals["dense_ref_2.512b"])
        rows.append(row)
    return rows

def gen_svg(data,field,mf,bs,title,yl):
    import math
    ctxs = sorted(CTX_LABELS.keys())
    W,H,M = 700,380,60
    pw,ph = W-2*M,H-2*M
    series = {}; allv = []
    for mk in MODELS:
        pts = [(c,v) for c in ctxs if (v:=gv(data,mk,mf,c,bs,field)) is not None]
        series[mk] = pts; allv.extend(v for _,v in pts)
    if not allv: return "<p style='color:#888'>暂无数据</p>"
    mn_v = min(v for v in allv if v > 0) if any(v > 0 for v in allv) else 0.1
    mx_v = max(allv)*1.15
    # log-scale Y axis for throughput, linear for VRAM
    use_log_y = field in ("prefill_tok_s","decode_tok_s","prefill_tok_s_perB","decode_tok_s_perB")
    x0,x1 = ctxs[0],ctxs[-1]
    # log-scale X axis (contexts are powers of 2)
    lx0,lx1 = math.log2(x0), math.log2(x1)
    xp = lambda c: M+(math.log2(c)-lx0)/(lx1-lx0)*pw if lx1>lx0 else M+pw/2
    if use_log_y:
        ly0,ly1 = math.log10(max(mn_v*0.8,0.1)), math.log10(mx_v)
        yp = lambda v: M+ph-(math.log10(max(v,0.1))-ly0)/(ly1-ly0)*ph
    else:
        yp = lambda v: M+ph-(v-0)/(mx_v-0)*ph
    s = [f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="font-family:monospace;font-size:11px">']
    s.append(f'<rect x="{M}" y="{M}" width="{pw}" height="{ph}" fill="none" stroke="#ddd"/>')
    for i in range(5):
        if use_log_y:
            yv = 10**(ly0+(ly1-ly0)*i/4)
        else:
            yv = mx_v*i/4
        y = yp(yv)
        s.append(f'<line x1="{M}" y1="{y}" x2="{W-M}" y2="{y}" stroke="#eee"/>')
        s.append(f'<text x="{M-5}" y="{y+3}" text-anchor="end" fill="#666">{fmt(yv)}</text>')
    for c in ctxs:
        x = xp(c)
        s.append(f'<text x="{x}" y="{M+ph+18}" text-anchor="middle" fill="#666">{CTX_LABELS[c]}</text>')
    for mk in MODELS:
        pts = series[mk]
        if len(pts)<1: continue
        path = " ".join(f"L{xp(c)},{yp(v)}" for c,v in pts)
        s.append(f'<path d="M{path[1:]}" fill="none" stroke="{M_COLOR[mk]}" stroke-width="2"/>')
        for c,v in pts: s.append(f'<circle cx="{xp(c)}" cy="{yp(v)}" r="3" fill="{M_COLOR[mk]}"/>')
    for i,mk in enumerate(MODELS):
        if not series[mk]: continue
        lx = M+10+i*180
        s.append(f'<line x1="{lx}" y1="{M-15}" x2="{lx+15}" y2="{M-15}" stroke="{M_COLOR[mk]}" stroke-width="2"/>')
        s.append(f'<text x="{lx+20}" y="{M-12}" fill="#333">{M_SHORT[mk]}</text>')
    s.append(f'<text x="{W/2}" y="20" text-anchor="middle" font-size="14" font-weight="bold" fill="#333">{title}</text>')
    s.append(f'<text x="15" y="{H/2}" transform="rotate(-90,15,{H/2})" text-anchor="middle" fill="#666">{yl}</text>')
    s.append('</svg>')
    return "\n".join(s)


def gen_section(data, field, mf, bs, sec_num, title, subtitle, yl):
    """Generate a complete HTML section: table + SVG chart for one (mf,bs,field)."""
    rows = gen_table(data, field, mf, bs)
    svg = gen_svg(data, field, mf, bs, f"{title} ({subtitle})", yl)
    h = []
    h.append(f"<h2>{sec_num}. {title}</h2><p>{subtitle}</p>")
    h.append("<table><tr><th>上下文</th><th class='hybrid'>Hybrid 2.220B</th><th>Dense-Match</th><th>Dense-Ref</th><th>H/DM</th><th>H/DR</th></tr>")
    for r in rows:
        h.append(f"<tr><td>{r['ctx']}</td><td class='hybrid'>{r['hybrid_2.220b']}</td><td>{r['dense_matched_2.229b']}</td><td>{r['dense_ref_2.512b']}</td><td class='ratio'>{r['rdm']}</td><td class='ratio'>{r['rdr']}</td></tr>")
    h.append("</table>")
    h.append(f"<div class='svgc'>{svg}</div>")
    return "\n".join(h)


def generate_report():
    data = load_results()
    print(f"Loaded {len(data)} result cells")
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    css = "body{font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;max-width:1100px;margin:0 auto;padding:20px;background:#f8f9fa;color:#2c3e50;line-height:1.6}h1{color:#1a1a2e;border-bottom:3px solid #e74c3c;padding-bottom:10px}h2{color:#1a1a2e;border-bottom:1px solid #bdc3c7;padding-bottom:5px;margin-top:30px}table{border-collapse:collapse;width:100%;margin:15px 0;font-size:13px}th,td{border:1px solid #ddd;padding:6px 10px;text-align:center}th{background:#2c3e50;color:#fff}tr:nth-child(even){background:#ecf0f1}.hybrid{color:#e74c3c;font-weight:bold}.ratio{color:#8e44ad;font-weight:bold}.note{background:#fff3cd;border-left:4px solid #ffc107;padding:10px 15px;margin:15px 0;border-radius:4px}.info{background:#d1ecf1;border-left:4px solid #17a2b8;padding:10px 15px;margin:15px 0;border-radius:4px}.svgc{text-align:center;margin:20px 0}footer{text-align:center;color:#7f8c8d;margin-top:40px;font-size:12px;border-top:1px solid #bdc3c7;padding-top:10px}code{background:#f4f4f4;padding:2px 6px;border-radius:3px}"
    h = []
    h.append(f"<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'><title>BaiZe vs Dense 推理对比报告</title><style>{css}</style></head><body>")
    h.append(f"<h1>BaiZe Mamba2-Hybrid 2.220B vs Dense Llama 推理性能对比报告</h1>")
    h.append(f"<p style='color:#7f8c8d'>生成时间：{now} · P-9.11-F · SGLang 0.5.9 · A100 80GB</p>")
    h.append(f"<div class='info'><strong>实验目的</strong>：在<strong>参数匹配</strong>条件下，公平对比 BaiZe Mamba2-Hybrid 2.220B 与 Dense Llama 的推理速度与显存效率。</div>")

    # Section 1: Config
    h.append("<h2>1. 模型配置对比</h2><table><tr><th>模型</th><th>总参数量</th><th>架构</th><th>层数</th><th>注意力层</th><th>KV Heads</th><th>参数差异</th></tr>")
    h.append("<tr><td class='hybrid'>BaiZe Mamba2-Hybrid</td><td>2,220,268,032</td><td>Nemotron-H (SSM+Attn)</td><td>56</td><td>4</td><td>4</td><td>基准</td></tr>")
    h.append("<tr><td>Dense Llama 36L (参数匹配)</td><td>2,228,897,792</td><td>Llama (Dense Attn)</td><td>36</td><td>36</td><td>2 (GQA)</td><td>+0.389%</td></tr>")
    h.append("<tr><td>Dense Llama 42L (参考)</td><td>2,512,285,696</td><td>Llama (Dense Attn)</td><td>42</td><td>42</td><td>4 (GQA)</td><td>+13.2%</td></tr></table>")
    h.append("<div class='note'><strong>公平性</strong>：Dense-Match 参数量与 Hybrid 仅差 0.389%。Dense-Match 权重<strong>随机初始化</strong>，仅用于速度/显存基准。所有模型同 SGLang/mem-frac/attention backend/WARMUP=1/REPEATS=3。</div>")

    # Sections 2-4: mf=0.6, bs=1 (main comparison)
    h.append(gen_section(data, "prefill_tok_s", 0.6, 1, "2", "Prefill 吞吐量", "bs=1, mem-frac=0.6, WARMUP=1, REPEATS=3", "tok/s"))
    h.append(gen_section(data, "decode_tok_s", 0.6, 1, "3", "Decode 吞吐量", "bs=1, mem-frac=0.6", "tok/s"))
    h.append(gen_section(data, "peak_vram_gb", 0.6, 1, "4", "峰值显存", "bs=1, mem-frac=0.6", "GB"))

    # Section 5: mf=0.85, bs=1 (memory fraction effect)
    h.append(gen_section(data, "prefill_tok_s", 0.85, 1, "5", "Prefill 吞吐量 (高KV缓存)", "bs=1, mem-frac=0.85", "tok/s"))
    h.append(gen_section(data, "decode_tok_s", 0.85, 1, "6", "Decode 吞吐量 (高KV缓存)", "bs=1, mem-frac=0.85", "tok/s"))

    # Section 7: bs=8 batch throughput (mf=0.6)
    h.append(gen_section(data, "prefill_tok_s", 0.6, 8, "7", "Prefill 吞吐量 (批量)", "bs=8, mem-frac=0.6 — 总吞吐量", "tok/s"))
    h.append(gen_section(data, "decode_tok_s", 0.6, 8, "8", "Decode 吞吐量 (批量)", "bs=8, mem-frac=0.6 — 总吞吐量", "tok/s"))

    # Section 9: bs=8 batch throughput (mf=0.85)
    h.append(gen_section(data, "prefill_tok_s", 0.85, 8, "9", "Prefill 吞吐量 (批量+高KV)", "bs=8, mem-frac=0.85", "tok/s"))

    # Section 10-11: mf=0.75, bs=1 (hybrid only — --disable-cuda-graph)
    h.append(gen_section(data, "prefill_tok_s", 0.75, 1, "10", "Prefill 吞吐量 (Hybrid mf=0.75)", "bs=1, mem-frac=0.75, Hybrid仅此一列（Dense无mf=0.75数据）", "tok/s"))
    h.append(gen_section(data, "decode_tok_s", 0.75, 1, "11", "Decode 吞吐量 (Hybrid mf=0.75)", "bs=1, mem-frac=0.75 ⚠️ --disable-cuda-graph：decode受kernel launch开销影响，不可与mf=0.6直接对比", "tok/s"))

    # Section 12: bs=8 batch throughput (mf=0.75, hybrid only)
    h.append(gen_section(data, "prefill_tok_s", 0.75, 8, "12", "Prefill 吞吐量 (Hybrid mf=0.75 批量)", "bs=8, mem-frac=0.75, Hybrid仅此一列", "tok/s"))

    # Section 13: Max Context
    h.append("<h2>13. 可服务上下文上限（实测）</h2><table><tr><th>模型</th><th>mem-frac</th><th>max_total_num_tokens</th><th>最大可服务上下文</th><th>受限原因</th></tr>")
    h.append("<tr><td class='hybrid' rowspan='3'>Hybrid 2.220B</td><td>0.6</td><td>2,979,164 (~3M)</td><td>2M (bs=1)</td><td>仅4层Attention KV + 52层SSM状态(float32)占用~72GB</td></tr>")
    h.append("<tr><td>0.75*</td><td>3,792,700 (~3.8M)</td><td>2M (bs=1)</td><td>*--disable-cuda-graph，4M仍超max_total_num_tokens</td></tr>")
    h.append("<tr><td>0.85</td><td colspan='2' style='color:#e74c3c'>OOM — SSM float32状态占72GB + CUDA graph缓冲区不足</td><td>SSM状态显存开销</td></tr>")
    h.append("<tr><td rowspan='2'>Dense-Match 2.229B</td><td>0.6</td><td>1,233,460 (~1.2M)</td><td>512K (bs=1实测)</td><td>36层Dense Attn KV线性增长</td></tr>")
    h.append("<tr><td>0.85</td><td>1,805,689 (~1.8M)</td><td>1M (bs=1, 服务器ctx上限)</td><td>服务器context_length=1M</td></tr>")
    h.append("<tr><td rowspan='2'>Dense-Ref 2.512B</td><td>0.6</td><td>1,050,035 (~1.05M)</td><td>512K (bs=1实测)</td><td>42层Dense Attn，KV更大</td></tr>")
    h.append("<tr><td>0.85</td><td>1,540,517 (~1.5M)</td><td>512K (服务器ctx上限)</td><td>服务器context_length=512K</td></tr></table>")
    h.append("<div class='info'><strong>架构优势</strong>：Hybrid 56层中仅4层使用Attention，SSM层状态固定大小。在相同GPU(A100 80GB)上，Hybrid可服务<strong>2M上下文</strong>，是Dense-Match的<strong>4倍</strong>、Dense-Ref的<strong>4倍</strong>。<br><strong>SSM显存代价</strong>：Hybrid的52层Mamba2 SSM状态以float32存储，占用~72GB显存。mf=0.85时CUDA graph缓冲区OOM；mf=0.75需禁用CUDA graph(--disable-cuda-graph)以释放10.85GB——这是Hybrid架构的已知trade-off。<br><strong>mf=0.75 vs 0.6</strong>：禁用CUDA graph后max_total_num_tokens从2.98M升至3.79M（+27%），prefill吞吐不变（~39K tok/s），但decode吞吐因kernel launch开销下降~6×（53 vs 310 tok/s）。</div>")

    # Section 14: Methodology
    h.append("<h2>14. 方法学</h2><div class='note'><strong>环境</strong>：A100 80GB×3（每模型独占1GPU），SGLang 0.5.9，flashinfer，bf16。<br><strong>公平口径</strong>：同mem-frac/同backend/WARMUP=1/REPEATS=3/同prompt。<br><strong>高ctx优化</strong>：ctx>1M时仅测bs=1/repeats=1；Dense模型ctx≥512K时仅测bs=1；Hybrid模型ctx≥1M时仅测bs=1。<br><strong>timeout</strong>：max(600s,ctx/1000)，封顶1800s。<br><strong>数据完整性</strong>：SGLang在输入超过max_total_num_tokens时返回HTTP 200+1 token（非错误），已通过token计数校验检测并标记为server_rejected。所有数字来自实测，无估算。'—'=不可服务/未测/被拒绝。<br><strong>Hybrid mf=0.75</strong>：SSM float32状态占~72GB，mf=0.85和mf=0.75(含CUDA graph)均OOM。使用--disable-cuda-graph跳过graph捕获以释放10.85GB。⚠️<strong>decode数据不可与mf=0.6直接对比</strong>（CUDA graph对decode影响极大，prefill不受影响）。<br><strong>Hybrid mf=0.85</strong>：完全OOM，无数据。<br><strong>Dense ctx上限</strong>：DM=1M, DR=512K（更高导致启动OOM或超过服务器context_length）。</div>")
    h.append(f"<footer>P-9.11-F Benchmark · BaiZe ISEDA 2027 · {now}</footer></body></html>")
    content = "\n".join(h)
    with open(REPORT_PATH,"w") as f: f.write(content)
    print(f"Report saved to {REPORT_PATH} ({len(content)} bytes)")

if __name__ == "__main__":
    generate_report()
