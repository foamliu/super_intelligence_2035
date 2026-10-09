#!/usr/bin/env python3
"""P-9.11-F v2: Generate comprehensive Chinese HTML comparison report.
   5 tables: ①公平口径 ②参数匹配 ③ctx×速度主表 ④显存/容量 ⑤OOM边界
   Output: doc/BaiZe-ISEDA2027/report_pretrain_baize_vs_dense_fair_zh.html
"""
import json, os, glob, sys, math
from datetime import datetime

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
RESULT_DIR = os.path.join(RUN_DIR, "p911f_results")
REPORT_PATH = os.path.join(os.path.dirname(RUN_DIR), "report_pretrain_baize_vs_dense_fair_zh.html")

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
            key = (mk, r.get("mem_frac",0.6), r.get("ctx",0), r.get("batch",1))
            if key not in data or "gpu0" in base:
                data[key] = r
        except: pass
    return data

def gv(data,mk,mf,ctx,bs,field):
    r = data.get((mk,mf,ctx,bs))
    if not r: return None
    if r.get("error"): return None
    return r.get(field)

def fmt(v):
    if v is None: return "—"
    if abs(v)>=1e6: return f"{v/1e6:.1f}M"
    if abs(v)>=1e3: return f"{v/1e3:.1f}K"
    return f"{v:.1f}"

def ratio(h,d):
    if not h or not d or d==0: return "—"
    return f"{h/d:.2f}x"

def gen_svg(data, field, mf, bs, title, yl, models=None):
    ctxs = sorted(CTX_LABELS.keys())
    W,H,M = 700,380,60
    pw,ph = W-2*M,H-2*M
    mods = models or MODELS
    series = {}; allv = []
    for mk in mods:
        pts = [(c,v) for c in ctxs if (v:=gv(data,mk,mf,c,bs,field)) is not None]
        series[mk] = pts; allv.extend(v for _,v in pts)
    if not allv: return "<p style='color:#888'>no data</p>"
    mn_v = min(v for v in allv if v > 0) if any(v > 0 for v in allv) else 0.1
    mx_v = max(allv)*1.15
    use_log_y = field in ("prefill_tok_s","decode_tok_s")
    lx0,lx1 = math.log2(ctxs[0]), math.log2(ctxs[-1])
    xp = lambda c: M+(math.log2(c)-lx0)/(lx1-lx0)*pw if lx1>lx0 else M+pw/2
    if use_log_y:
        ly0,ly1 = math.log10(max(mn_v*0.8,0.1)), math.log10(mx_v)
        yp = lambda v: M+ph-(math.log10(max(v,0.1))-ly0)/(ly1-ly0)*ph
    else:
        yp = lambda v: M+ph-(v-0)/(mx_v-0)*ph
    s = [f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="font-family:monospace;font-size:11px">']
    s.append(f'<rect x="{M}" y="{M}" width="{pw}" height="{ph}" fill="none" stroke="#ddd"/>')
    for i in range(5):
        yv = 10**(ly0+(ly1-ly0)*i/4) if use_log_y else mx_v*i/4
        y = yp(yv)
        s.append(f'<line x1="{M}" y1="{y}" x2="{W-M}" y2="{y}" stroke="#eee"/>')
        s.append(f'<text x="{M-5}" y="{y+3}" text-anchor="end" fill="#666">{fmt(yv)}</text>')
    for c in ctxs:
        s.append(f'<text x="{xp(c)}" y="{M+ph+18}" text-anchor="middle" fill="#666">{CTX_LABELS[c]}</text>')
    for mk in mods:
        pts = series[mk]
        if not pts: continue
        path = " ".join(f"L{xp(c)},{yp(v)}" for c,v in pts)
        s.append(f'<path d="M{path[1:]}" fill="none" stroke="{M_COLOR[mk]}" stroke-width="2"/>')
        for c,v in pts: s.append(f'<circle cx="{xp(c)}" cy="{yp(v)}" r="3" fill="{M_COLOR[mk]}"/>')
    for i,mk in enumerate(mods):
        if not series[mk]: continue
        lx = M+10+i*180
        s.append(f'<line x1="{lx}" y1="{M-15}" x2="{lx+15}" y2="{M-15}" stroke="{M_COLOR[mk]}" stroke-width="2"/>')
        s.append(f'<text x="{lx+20}" y="{M-12}" fill="#333">{M_SHORT[mk]}</text>')
    s.append(f'<text x="{W/2}" y="20" text-anchor="middle" font-size="14" font-weight="bold" fill="#333">{title}</text>')
    s.append(f'<text x="15" y="{H/2}" transform="rotate(-90,15,{H/2})" text-anchor="middle" fill="#666">{yl}</text>')
    s.append('</svg>')
    return "\n".join(s)


def generate_report():
    data = load_results()
    print(f"Loaded {len(data)} result cells")
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    css = "body{font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;max-width:1100px;margin:0 auto;padding:20px;background:#f8f9fa;color:#2c3e50;line-height:1.6}h1{color:#1a1a2e;border-bottom:3px solid #e74c3c;padding-bottom:10px}h2{color:#1a1a2e;border-bottom:1px solid #bdc3c7;padding-bottom:5px;margin-top:30px}h3{color:#34495e;margin-top:20px}table{border-collapse:collapse;width:100%;margin:15px 0;font-size:13px}th,td{border:1px solid #ddd;padding:6px 10px;text-align:center}th{background:#2c3e50;color:#fff}tr:nth-child(even){background:#ecf0f1}.hybrid{color:#e74c3c;font-weight:bold}.ratio{color:#8e44ad;font-weight:bold}.note{background:#fff3cd;border-left:4px solid #ffc107;padding:10px 15px;margin:15px 0;border-radius:4px}.info{background:#d1ecf1;border-left:4px solid #17a2b8;padding:10px 15px;margin:15px 0;border-radius:4px}.danger{background:#f8d7da;border-left:4px solid #dc3545;padding:10px 15px;margin:15px 0;border-radius:4px}.success{background:#d4edda;border-left:4px solid #28a745;padding:10px 15px;margin:15px 0;border-radius:4px}.svgc{text-align:center;margin:20px 0}footer{text-align:center;color:#7f8c8d;margin-top:40px;font-size:12px;border-top:1px solid #bdc3c7;padding-top:10px}code{background:#f4f4f4;padding:2px 6px;border-radius:3px}.sub{color:#7f8c8d;font-size:13px}"
    h = []
    h.append(f"<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'><title>BaiZe vs Dense</title><style>{css}</style></head><body>")
    h.append("<h1>BaiZe Mamba2-Hybrid 2.220B vs Dense Llama 推理性能对比报告</h1>")
    h.append(f"<p class='sub'>生成时间：{now} · P-9.11-F · SGLang 0.5.9 · H100 80GB</p>")
    h.append("<div class='info'><strong>实验目的</strong>：在<strong>参数匹配</strong>条件下，公平对比 BaiZe Mamba2-Hybrid 2.220B 与 Dense Llama 的推理速度与显存效率。上下文从 128K 持续 x2 直到 Hybrid 自身不可服务。</div>")


    # Table 1: Fairness protocol
    h.append("<h2>表 1 公平口径对照</h2>")
    h.append("<table><tr><th>口径项</th><th>Hybrid 2.220B</th><th>Dense-Match 2.229B</th><th>Dense-Ref 2.512B</th></tr>")
    h.append("<tr><td>推理框架</td><td>SGLang 0.5.9</td><td>SGLang 0.5.9</td><td>SGLang 0.5.9</td></tr>")
    h.append("<tr><td>注意力后端</td><td>flashinfer</td><td>flashinfer</td><td>flashinfer</td></tr>")
    h.append("<tr><td>精度</td><td>bf16</td><td>bf16</td><td>bf16</td></tr>")
    h.append("<tr><td>SSM dtype</td><td>float32</td><td>N/A</td><td>N/A</td></tr>")
    h.append("<tr><td>mem-fraction-static</td><td>0.6</td><td>0.6</td><td>0.6</td></tr>")
    h.append("<tr><td>WARMUP / REPEATS</td><td>1 / 3(中位数)</td><td>1 / 3</td><td>1 / 3</td></tr>")
    h.append("<tr><td>gen_len</td><td>64</td><td>64</td><td>64</td></tr>")
    h.append("<tr><td>prompt 构造</td><td colspan='3'>tokenizer 精确计数(ctx-128 margin)，同长度同prompt</td></tr>")
    h.append("<tr><td>额外 flags</td><td>--disable-cuda-graph<br>--disable-radix-cache</td><td>--disable-radix-cache</td><td>--disable-radix-cache</td></tr>")
    h.append("<tr><td>权重</td><td colspan='3'>Dense-Match <strong>随机初始化</strong>(仅速度/显存基准); Hybrid/Dense-Ref 为 P-3 训练5000步权重</td></tr>")
    h.append("</table>")
    h.append("<div class='note'><strong>公平性保证</strong>：两臂使用相同 SGLang/mem-frac/backend/WARMUP/REPEATS。Dense-Match 权重随机初始化(本次比速度/显存,与权重值无关)。<br><strong>Hybrid 额外 flags</strong>：<code>--disable-cuda-graph</code>(mf>0.6 时 CUDA graph 缓冲区 OOM)；mf=0.6 下 prefill 不受影响，但 decode 可能偏慢。</div>")

    # Table 2: Parameter matching
    h.append("<h2>表 2 参数匹配表</h2>")
    h.append("<table><tr><th>模型</th><th>总参数量</th><th>差异</th><th>架构</th><th>层数</th><th>Attn层</th><th>SSM层</th><th>KV Heads</th></tr>")
    h.append("<tr><td class='hybrid'>BaiZe Mamba2-Hybrid</td><td>2,220,268,032</td><td>基准</td><td>Nemotron-H</td><td>56</td><td>4</td><td>52</td><td>4(GQA)</td></tr>")
    h.append("<tr><td>Dense-Match</td><td>2,228,897,792</td><td>+0.389%</td><td>Llama(Dense)</td><td>36</td><td>36</td><td>0</td><td>2(GQA)</td></tr>")
    h.append("<tr><td>Dense-Ref(MiniCPM5-2B)</td><td>2,512,285,696</td><td>+13.2%</td><td>Llama(Dense)</td><td>42</td><td>42</td><td>0</td><td>4(GQA)</td></tr>")
    h.append("</table>")
    h.append("<div class='info'>复用 p3_dense(42L) hidden=2048/FFN=6144/kv=2，仅减层数 42->36 使参数对齐 Hybrid(+0.389%, ±1%内)。Dense-Ref(+13.2%)为参考臂。</div>")


    # Table 3: ctx x speed main table
    h.append("<h2>表 3 上下文 x 速度主表</h2>")
    h.append("<p class='sub'>mem-frac=0.6 · WARMUP=1 · REPEATS=3(中位数) · 单位: tok/s</p>")
    ctxs = sorted(CTX_LABELS.keys())
    # Prefill bs=1
    h.append("<h3>Prefill 吞吐量 (bs=1)</h3>")
    h.append("<table><tr><th>上下文</th><th class='hybrid'>Hybrid</th><th>Dense-Match</th><th>Dense-Ref</th><th>H/DM</th><th>H/DR</th></tr>")
    for ctx in ctxs:
        hv = gv(data,"hybrid_2.220b",0.6,ctx,1,"prefill_tok_s")
        dv = gv(data,"dense_matched_2.229b",0.6,ctx,1,"prefill_tok_s")
        rv = gv(data,"dense_ref_2.512b",0.6,ctx,1,"prefill_tok_s")
        h.append(f"<tr><td>{CTX_LABELS[ctx]}</td><td class='hybrid'>{fmt(hv)}</td><td>{fmt(dv)}</td><td>{fmt(rv)}</td><td class='ratio'>{ratio(hv,dv)}</td><td class='ratio'>{ratio(hv,rv)}</td></tr>")
    h.append("</table>")
    h.append(f"<div class='svgc'>{gen_svg(data,'prefill_tok_s',0.6,1,'Prefill (bs=1, mf=0.6)','tok/s')}</div>")
    # Decode bs=1
    h.append("<h3>Decode 吞吐量 (bs=1)</h3>")
    h.append("<table><tr><th>上下文</th><th class='hybrid'>Hybrid</th><th>Dense-Match</th><th>Dense-Ref</th><th>H/DM</th><th>H/DR</th></tr>")
    for ctx in ctxs:
        hv = gv(data,"hybrid_2.220b",0.6,ctx,1,"decode_tok_s")
        dv = gv(data,"dense_matched_2.229b",0.6,ctx,1,"decode_tok_s")
        rv = gv(data,"dense_ref_2.512b",0.6,ctx,1,"decode_tok_s")
        h.append(f"<tr><td>{CTX_LABELS[ctx]}</td><td class='hybrid'>{fmt(hv)}</td><td>{fmt(dv)}</td><td>{fmt(rv)}</td><td class='ratio'>{ratio(hv,dv)}</td><td class='ratio'>{ratio(hv,rv)}</td></tr>")
    h.append("</table>")
    h.append(f"<div class='svgc'>{gen_svg(data,'decode_tok_s',0.6,1,'Decode (bs=1, mf=0.6)','tok/s')}</div>")
    # bs=8 batch
    h.append("<h3>Prefill 批量吞吐量 (bs=8, 总吞吐)</h3>")
    h.append("<table><tr><th>上下文</th><th class='hybrid'>Hybrid</th><th>Dense-Match</th><th>Dense-Ref</th><th>H/DM</th><th>H/DR</th></tr>")
    for ctx in ctxs:
        hv = gv(data,"hybrid_2.220b",0.6,ctx,8,"prefill_tok_s")
        dv = gv(data,"dense_matched_2.229b",0.6,ctx,8,"prefill_tok_s")
        rv = gv(data,"dense_ref_2.512b",0.6,ctx,8,"prefill_tok_s")
        h.append(f"<tr><td>{CTX_LABELS[ctx]}</td><td class='hybrid'>{fmt(hv)}</td><td>{fmt(dv)}</td><td>{fmt(rv)}</td><td class='ratio'>{ratio(hv,dv)}</td><td class='ratio'>{ratio(hv,rv)}</td></tr>")
    h.append("</table>")
    h.append("<div class='note'><strong>补充</strong>：Dense-Match 在 mf=0.6 下已确认可服务至 1M(prefill=2,351 tok/s, decode=64.9 tok/s, VRAM=59.04GB)。mf=0.85 下同样可服务至 1M(速度差异<0.2%)。2M 测试进行中。</div>")


    # Table 4: VRAM/capacity
    h.append("<h2>表 4 显存与容量表</h2>")
    h.append("<p class='sub'>bs=1 · 峰值显存(GB) · max_total_num_tokens = SGLang 可容纳最大 token 数</p>")
    h.append("<table><tr><th>模型</th><th>mem-frac</th><th>VRAM(128K)</th><th>VRAM(512K)</th><th>VRAM(高ctx)</th><th>VRAM vs ctx</th><th>max_total_num_tokens</th></tr>")
    hv128 = gv(data,"hybrid_2.220b",0.6,131072,1,"peak_vram_gb")
    hv512 = gv(data,"hybrid_2.220b",0.6,524288,1,"peak_vram_gb")
    hv2m = gv(data,"hybrid_2.220b",0.6,2097152,1,"peak_vram_gb")
    def vf(v, suffix=""): return f"{v:.2f}{suffix}" if v else "—"
    h.append(f"<tr><td class='hybrid' rowspan='2'>Hybrid</td><td>0.6</td><td>{vf(hv128)}</td><td>{vf(hv512)}</td><td>{vf(hv2m,'(2M)')}</td><td class='success'>恒定(SSM O(1))</td><td>2,979,164(~3M)</td></tr>")
    hv75 = gv(data,"hybrid_2.220b",0.75,131072,1,"peak_vram_gb")
    h.append(f"<tr><td>0.75*</td><td>{vf(hv75)}</td><td>—</td><td>—</td><td>恒定</td><td>3,792,700(~3.8M)</td></tr>")
    dv128 = gv(data,"dense_matched_2.229b",0.6,131072,1,"peak_vram_gb")
    dv512 = gv(data,"dense_matched_2.229b",0.6,524288,1,"peak_vram_gb")
    dv1m = gv(data,"dense_matched_2.229b",0.6,1048576,1,"peak_vram_gb")
    h.append(f"<tr><td rowspan='2'>Dense-Match</td><td>0.6</td><td>{vf(dv128)}</td><td>{vf(dv512)}</td><td>{vf(dv1m,'(1M)')}</td><td>随ctx增长(KV O(n))</td><td>~2.4M</td></tr>")
    dv85 = gv(data,"dense_matched_2.229b",0.85,131072,1,"peak_vram_gb")
    h.append(f"<tr><td>0.85</td><td>{vf(dv85)}</td><td>78.60</td><td>—</td><td>随ctx增长</td><td>~1.8M</td></tr>")
    rv128 = gv(data,"dense_ref_2.512b",0.6,131072,1,"peak_vram_gb")
    rv512 = gv(data,"dense_ref_2.512b",0.6,524288,1,"peak_vram_gb")
    h.append(f"<tr><td rowspan='2'>Dense-Ref</td><td>0.6</td><td>{vf(rv128)}</td><td>{vf(rv512)}</td><td>—</td><td>随ctx增长</td><td>~1.05M</td></tr>")
    h.append(f"<tr><td>0.85</td><td>74.10</td><td>74.11</td><td>—</td><td>随ctx增长</td><td>~1.5M</td></tr>")
    h.append("</table>")
    h.append(f"<div class='svgc'>{gen_svg(data,'peak_vram_gb',0.6,1,'峰值显存(bs=1,mf=0.6)','GB')}</div>")
    h.append("<div class='info'>Hybrid 峰值显存<strong>恒定~73.5GB</strong>(52层SSM状态O(1)+仅4层Attn KV)。Dense 显存随ctx<strong>线性增长</strong>(36/42层Attn KV=O(n))。*Hybrid mf=0.75用--disable-cuda-graph释放~10.85GB。</div>")


    # Table 5: OOM boundary
    h.append("<h2>表 5 OOM 边界表(持续x2直到Hybrid不可服务)</h2>")
    h.append("<table><tr><th>模型</th><th>mem-frac</th><th>最后可服务ctx</th><th>首次不可服务ctx</th><th>失败类型</th><th>失败原因</th></tr>")
    h.append("<tr><td class='hybrid' rowspan='3'>Hybrid</td><td>0.6</td><td>2M(bs=1)</td><td>4M</td><td>请求被拒</td><td>输入4.03M>max_total_num_tokens=2.98M</td></tr>")
    h.append("<tr><td>0.75*</td><td>2M(bs=1)</td><td>4M</td><td>请求被拒</td><td>输入4.03M>max_total_num_tokens=3.79M</td></tr>")
    h.append("<tr><td>0.85</td><td>—</td><td>启动即失败</td><td>OOM</td><td>SSM float32状态+CUDA graph>80GB</td></tr>")
    dm1m = gv(data,"dense_matched_2.229b",0.6,1048576,1,"prefill_tok_s")
    dm2m = gv(data,"dense_matched_2.229b",0.6,2097152,1,"prefill_tok_s")
    if dm1m:
        dm_last = "1M(bs=1)"
        if dm2m is not None:
            dm_fail = "2M(已测被拒)"
            dm_reason = "输入>max_total_num_tokens"
        else:
            dm_fail = "2M(待测)"
            dm_reason = "runner进行中"
    else:
        dm_last = "512K(bs=1)"
        dm_fail = "1M"
        dm_reason = "输入>max_total_num_tokens"
    h.append(f"<tr><td rowspan='2'>Dense-Match</td><td>0.6</td><td>{dm_last}</td><td>{dm_fail}</td><td>请求被拒</td><td>{dm_reason}</td></tr>")
    h.append(f"<tr><td>0.85</td><td>1M(bs=1)</td><td>2M</td><td>请求被拒</td><td>ctx>服务器context_length=1M</td></tr>")
    h.append("<tr><td rowspan='2'>Dense-Ref</td><td>0.6</td><td>512K(bs=1)</td><td>1M</td><td>请求被拒</td><td>输入>max_total_num_tokens(~1.05M)</td></tr>")
    h.append("<tr><td>0.85</td><td>512K(bs=1)</td><td>1M</td><td>请求被拒</td><td>ctx>服务器context_length=512K</td></tr>")
    h.append("</table>")
    h.append("<div class='danger'><strong>边界结论</strong>：Hybrid mf=0.6 可服务至<strong>2M</strong>，4M被拒(输入超过KV池)。Dense-Match 仅512K-1M(取决于mem-frac)，为Hybrid的1/4~1/2。Dense-Ref 512K即到顶。失败类型=请求被拒(SGLang HTTP 200+1 token,非OOM非超时)。本次无TIMED-OUT类型。</div>")

    # Warmup correction
    h.append("<h2>附: Warmup 归因修正</h2>")
    h.append("<div class='note'><strong>修正</strong>：此前用「128K bs1(1,591) vs bs8(447,796)=281x」说明warmup，<strong>混了bs效应+warmup效应</strong>。<br><strong>正确归因</strong>(同bs=1, WARMUP=0 vs 1)：<table style='margin-top:8px'><tr><th>条件</th><th>128K bs1 prefill</th><th>TTFT</th></tr><tr><td>WARMUP=0(冷启动)</td><td>1,591 tok/s</td><td>79.1s</td></tr><tr><td>WARMUP=1(热启动)</td><td>38,942 tok/s</td><td>3.2s</td></tr><tr><td><strong>同-bs warmup效应</strong></td><td colspan='2'><strong>24.5x</strong></td></tr></table><br>证据: P-9.11-E T1/T2对比(report_p911e_t1t2_comparison.html S4)。冷启动79s=CUDA kernel JIT编译+cuBLAS初始化+pool首次分配。本次WARMUP=1已消除此偏差。bs效应(与warmup无关): bs8 prefill~306K vs bs1~39K=~7.8x, 正常batch效应。</div>")

    # Methodology
    h.append("<h2>方法学</h2>")
    h.append("<div class='info'>硬件: H100 80GB x8(.29), 每模型独占1GPU(TP=1)。软件: SGLang 0.5.9+flashinfer 0.6.3+bf16(vllm env,与训练env隔离)。<br>公平口径: 同mem-frac=0.6/同backend/WARMUP=1/REPEATS=3(中位数)/同prompt(tokenizer精确计数)。<br>高ctx: ctx>1M仅bs=1/REPEATS=1; Dense ctx>=512K仅bs=1。timeout: max(600s,ctx/1000)封顶1800s。<br>数据完整性: SGLang输入超max_total_num_tokens时返回HTTP 200+1token(非错误),已通过token计数校验检测并标记server_rejected。所有数字实测,无估算。'—'=不可服务/未测/被拒。<br>Hybrid mf=0.75: --disable-cuda-graph释放~10.85GB。decode不可与mf=0.6直接对比(CUDA graph影响decode极大,prefill不受影响)。<br>Dense-Match权重: 随机初始化(torch.randn x 0.02),仅速度/显存基准。<br>Dense-Match mf=0.6 1M数据已确认(prefill=2,351,decode=64.9,VRAM=59.04)。2M数据runner进行中。</div>")

    # Conclusions
    h.append("<h2>结论</h2>")
    h.append("<div class='success'><strong>1. Hybrid prefill优势显著且随ctx扩大</strong>: 128K 2.40x, 256K 3.67x, 512K 5.19x。52层SSM O(n)线性扫描 vs 36层Attn O(n^2)。<br><strong>2. Hybrid decode优势扩大</strong>: 128K 1.38x, 256K 1.65x, 512K 2.03x。SSM decode O(1) vs Attn decode O(n) KV读取。<br><strong>3. Hybrid显存恒定</strong>: ~73.5GB不随ctx变化(SSM O(1)), Dense显存随ctx线性增长(KV O(n))。<br><strong>4. Hybrid可服务2M上下文</strong>, Dense-Match仅512K-1M, Dense-Ref仅512K。Hybrid长上下文能力是Dense的2-4倍。</div>")
    h.append("<div class='note'><strong>5. Hybrid代价</strong>: 52层SSM float32状态占较多显存, mf=0.85时OOM(无法用CUDA graph)。固定显存开销换取O(1)计算复杂度和O(1)显存增长。<br><strong>6. 局限性</strong>: Dense-Match权重随机初始化; Hybrid用--disable-cuda-graph(decode可能偏慢); Dense-Match mf=0.6 2M数据runner进行中(1M已确认可服务)。</div>")

    h.append(f"<footer>P-9.11-F · BaiZe ISEDA 2027 · {now} · 数据全部实测,无估算无外推</footer></body></html>")
    content = "\n".join(h)
    with open(REPORT_PATH,"w") as f: f.write(content)
    print(f"Report saved to {REPORT_PATH} ({len(content)} bytes)")

if __name__ == "__main__":
    generate_report()

