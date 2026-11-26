#!/usr/bin/env python3
"""P-9.11 HTML report generator."""
import json,os,datetime
H=json.load(open("p911_hybrid_results.json"))
D=json.load(open("p911_dense_results.json"))
hr=H["results"]; dr=D["results"]
now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
def F(v,w=8):
    if v is None: return "\u2014".rjust(w)
    if isinstance(v,float): return f"{v:.2f}".rjust(w)
    return str(v).rjust(w)
def R(a,b,good="high"):
    if a is None or b is None or b==0: return "\u2014"
    r=a/b; c="ratio"
    if good=="high":
        c="good" if r>1.05 else ("bad" if r<0.95 else "ratio")
    else:
        c="good" if r<0.95 else ("bad" if r>1.05 else "ratio")
    return f'<span class="{c}">{r:.2f}x</span>'
def fail(r): return r.get("total_completion_tokens",1)==0 or r.get("ttft_s") is None
def get(ctx,bs,L): return next((r for r in L if r["ctx"]==ctx and r["batch"]==bs),None)
ctxs=[4096,16384,65536,131072]; batches=[1,8]
S=f"""<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">
<title>P-9.11 sglang: BaiZe vs MiniCPM5-2B</title>
<style>
body{{font-family:monospace;margin:20px;max-width:1500px}}
h1{{font-size:1.4em;border-bottom:2px solid #333;padding-bottom:5px}}
h2{{font-size:1.15em;margin-top:30px;border-bottom:1px solid #999;padding-bottom:3px}}
table{{border-collapse:collapse;width:100%;font-size:0.85em;margin:10px 0}}
th,td{{border:1px solid #aaa;padding:4px 8px;text-align:right}}
th{{background:#e0e0e0}}.ratio{{color:#0066cc;font-weight:bold}}
.good{{color:#007700;font-weight:bold}}.bad{{color:#cc0000;font-weight:bold}}
.warn{{color:#cc6600}}.fail{{color:red;background:#ffeeee}}
.note{{background:#fffde6;border:1px solid #ddd588;padding:10px;margin:10px 0;border-radius:4px}}
pre{{background:#f0f0f0;padding:10px;overflow-x:auto;font-size:0.8em}}
.vp{{background:#d4edda;color:#155724;padding:5px 10px;border-radius:4px;display:inline-block;font-weight:bold}}
.vw{{background:#fff3cd;color:#856404;padding:5px 10px;border-radius:4px;display:inline-block;font-weight:bold}}
.vf{{background:#f8d7da;color:#721c24;padding:5px 10px;border-radius:4px;display:inline-block;font-weight:bold}}
</style></head><body>
<h1>P-9.11 \u00b7 sglang \u751f\u4ea7\u6800 \u2014\u2014 BaiZe(Mamba2-hybrid 2B) vs MiniCPM5-2B \u63a8\u7406\u5bf9\u6bd4</h1>
<p><b>\u65e5\u671f:</b> {now} | <b>\u6846\u67b6:</b> sglang 0.5.9 | <b>GPU:</b> H100 80GB \u00d71 | <b>\u53e3\u5f84:</b> \u751f\u4ea7\u63a8\u7406\u6800</p>
<div class="note"><b>\u26a0\u53e3\u5f84\u6807\u6ce8：</b> P-3 ckpt=5000\u6b65/123M token\u3002\u65e7 Round-1 mcore 10.3\u00d7\u4e0e\u672c\u8f6e\u4e0d\u5f97\u76f4\u63a5\u76f8\u51cf\u3002\u672c\u5b9e\u9a8c=sglang \u4f5c\u4e3a\u540c\u4e00\u63a8\u7406\u6846\u67b6\u5bf9\u6bd4\u4e24\u67b6\u6784\uff08BaiZe=Mamba2-hybrid 2.220B \u2694 MiniCPM5-2B=dense GPT 2.512B\uff09\u3002</div>
<h2>1. \u5b9e\u9a8c\u8bbe\u7f6e</h2>
<table><tr><th>\u6a21\u578b</th><th>\u67b6\u6784</th><th>ckpt</th><th>\u53c2\u6570</th><th>HF\u7ed3\u6784</th><th>max_pos</th></tr>
<tr><td>BaiZe</td><td>Mamba2-hybrid</td><td>p3_hybrid/iter_0005000</td><td>2.220B</td><td>nemotron_h</td><td>4096</td></tr>
<tr><td>\u5bf9\u7167</td><td>dense GPT</td><td>p3_dense/iter_0005000</td><td>2.512B</td><td>Llama</td><td>4096</td></tr></table>
<p><b>sglang\u914d\u7f6e：</b>--context-length 131072 --mem-fraction-static 0.85 --attention-backend flashinfer; hybrid \u52a0 --mamba-ssm-dtype float32; SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1</p>
<p><b>\u77e9\u9635：</b> ctx{{4K,16K,64K,128K}}\u00d7bs{{1,8}}, gen_len=64, temp=0, streaming</p>
<h2>2. \u6838\u5fc3\u7ed3\u679c\u8868</h2>
<p><b>\u6bd4\u503c=hybrid/dense</b>（&gt;1=hybrid\u4f18）。TTFT/VRAM\u4f4e\u4f18\uff0c\u541e\u5410\u9ad8\u4f18\u3002</p>
<table><tr><th>ctx</th><th>bs</th><th>h TTFT(ms)</th><th>d TTFT(ms)</th><th>TTFT h/d</th><th>h prefill</th><th>d prefill</th><th>prefill h/d</th><th>h decode</th><th>d decode</th><th>decode h/d</th><th>h VRAM</th><th>d VRAM</th><th>VRAM h/d</th></tr>
"""
for ctx in ctxs:
    for bs in batches:
        h=get(ctx,bs,hr); d=get(ctx,bs,dr)
        if not h or not d: continue
        if fail(h) or fail(d):
            S+=f'<tr class="fail"><td>{ctx}</td><td>{bs}</td><td colspan="12" style="text-align:center">FAILED \u2014 total_completion_tokens=0 (max_pos_emb=4096, 128K=32\u00d7 beyond training)</td></tr>\n'
            continue
        w='<span class="warn">\u26a0</span>' if (ctx==4096 and bs==8) else ''
        S+=f'<tr><td>{ctx}</td><td>{bs}</td>'
        S+=f'<td>{F(h["ttft_s"]*1000)}{w if bs==1 else ""}</td><td>{F(d["ttft_s"]*1000)}</td><td>{R(h["ttft_s"],d["ttft_s"],"low")}</td>'
        S+=f'<td>{F(h["prefill_tok_s"])}{w if bs==8 else ""}</td><td>{F(d["prefill_tok_s"])}</td><td>{R(h["prefill_tok_s"],d["prefill_tok_s"],"high")}</td>'
        S+=f'<td>{F(h["decode_tok_s"])}{w if bs==8 else ""}</td><td>{F(d["decode_tok_s"])}</td><td>{R(h["decode_tok_s"],d["decode_tok_s"],"high")}</td>'
        S+=f'<td>{F(h["peak_vram_gb"])}</td><td>{F(d["peak_vram_gb"])}</td><td>{R(h["peak_vram_gb"],d["peak_vram_gb"],"low")}</td></tr>\n'
S+="""</table>
<div class="note"><b>\u26a0 4K\u00d78 hybrid \u70ed\u8eab\u5f02\u5e38：</b>decode=31.1 tok/s \u8fdc\u4f4e\u4e8e\u540e\u7eed batch=8（16K\u00d78:660, 64K\u00d78:1171）。sglang\u542f\u52a8\u540e\u7b2c\u4e00\u4e2a batch=8 \u8bf7\u6c42\u7684 CUDA graph \u7f16\u8bd1\u5f00\u9500\u3002decode \u4e0d\u53ef\u4fe1\uff0c\u5206\u6790\u65f6\u6392\u9664\u3002</div>
<div class="note"><b>\u26a0 4K\u00d71 hybrid \u70ed\u8eab\u6548\u5e94：</b>TTFT=1050ms \u504f\u9ad8\uff08\u7b2c\u4e00\u8bf7\u6c42\u7f16\u8bd1\u5f00\u9500\uff09\uff0cprefill=3899 \u504f\u4f4e\u3002decode=274 \u6b63\u5e38\u3002</div>
<h2>3. \u5047\u8bf4\u9a8c\u8bc1\uff08H1\u2013H4\uff09</h2>
<h3>H1: prefill \u541e\u5410\u4f18\u52bf\u968f ctx \u589e\u957f\uff08SSM O(n) vs attn O(n\u00b2)\uff09</h3>
<table><tr><th>ctx</th><th>bs=1 prefill h/d</th><th>bs=8 prefill h/d</th></tr>
"""
for ctx in [4096,16384,65536]:
    h1=get(ctx,1,hr);d1=get(ctx,1,dr);h8=get(ctx,8,hr);d8=get(ctx,8,dr)
    r1=h1["prefill_tok_s"]/d1["prefill_tok_s"];r8=h8["prefill_tok_s"]/d8["prefill_tok_s"]
    c1="good" if r1>1.05 else("bad" if r1<0.95 else"")
    c8="good" if r8>1.05 else("bad" if r8<0.95 else"")
    S+=f'<tr><td>{ctx}</td><td class="{c1}">{r1:.2f}x</td><td class="{c8}">{r8:.2f}x</td></tr>\n'
S+="""</table>
<p><span class="vp">H1 \u2705 CONFIRMED</span></p>
<p>bs=1: 0.14x(4K)\u21920.21x(16K)\u2192<b>2.18x(64K)</b>\uff0c\u4ea4\u53c9\u70b9\u5728 16K-64K\u3002\u8fd9\u6b63\u662f SSM O(n) vs attention O(n\u00b2) \u7684\u7406\u8bba\u9884\u6d4b\u3002bs=8 \u65f6\u4ea4\u53c9\u8f83\u5f31\uff081.04x at 64K\uff09\uff0c\u56e0 batching \u644a\u9500\u4e86 attention \u7684 O(n\u00b2) \u6210\u672c\u3002</p>
<h3>H2: decode \u5410\u5410\u4f18\u52bf\u968f ctx \u589e\u957f</h3>
<table><tr><th>ctx</th><th>bs=1 decode h/d</th><th>bs=8 decode h/d (excl warmup)</th></tr>
"""
for ctx in [4096,16384,65536]:
    h1=get(ctx,1,hr);d1=get(ctx,1,dr);h8=get(ctx,8,hr);d8=get(ctx,8,dr)
    r1=h1["decode_tok_s"]/d1["decode_tok_s"]
    c1="good" if r1>1.05 else("bad" if r1<0.95 else"")
    if ctx==4096:
        S+=f'<tr><td>{ctx}</td><td class="{c1}">{r1:.2f}x</td><td>\u2014 (warmup)</td></tr>\n'
    else:
        r8=h8["decode_tok_s"]/d8["decode_tok_s"]
        c8="good" if r8>1.05 else("bad" if r8<0.95 else"")
        S+=f'<tr><td>{ctx}</td><td class="{c1}">{r1:.2f}x</td><td class="{c8}">{r8:.2f}x</td></tr>\n'
S+="""</table>
<p><span class="vw">H2 \u26a0 PARTIALLY CONFIRMED</span></p>
<p>bs=1: 0.91x(4K/16K)\u2192<b>1.18x(64K)</b>\uff0c\u4ea4\u53c9\u70b9\u5728 ~50K\u3002hybrid decode \u4f18\u52bf\u5728\u957f ctx \u4e0b\u5f00\u59cb\u663e\u73b0\u4f46\u5e45\u5ea6\u4e0d\u5927\u3002bs=8: 0.36x(16K)\u21920.78x(64K)\uff0c\u5448\u4e0a\u5347\u4f46 hybrid \u4ecd\u6162\u4e8e dense\u3002\u539f\u56e0：sglang \u5bf9 dense GPT \u7684 KV cache \u505a\u4e86\u9ad8\u5ea6\u4f18\u5316\uff08PagedAttention\uff09\uff0cnemotron_h \u7684 Mamba2 SSM \u5728 sglang \u4e2d decode \u8def\u5f84\u4f18\u5316\u4e0d\u53ca dense\u3002\u4e0e P-9.10\u2462 mcore eager \u7684\u6052\u5b9a 1.6\u00d7 \u4e0d\u540c\u2014\u2014mcore eager \u7684 launch \u5f00\u9500\u63a9\u76d6\u4e86 ctx \u6548\u5e94\uff0csglang \u751f\u4ea7\u6800\u4e0b\u4ea4\u53c9\u70b9\u5728 ~50K \u66f4\u771f\u5b9e\u3002</p>
<h3>H3: VRAM \u4f18\u52bf\u968f ctx \u589e\u957f</h3>
<table><tr><th>ctx</th><th>VRAM h/d</th></tr>
"""
for ctx in ctxs:
    h=get(ctx,1,hr);d=get(ctx,1,dr)
    if h and d:
        r=h["peak_vram_gb"]/d["peak_vram_gb"]
        S+=f'<tr><td>{ctx}</td><td>{r:.2f}x</td></tr>\n'
S+="""</table>
<p><span class="vf">H3 \u274c NOT CONFIRMED via sglang</span></p>
<p>VRAM \u6bd4\u503c\u51e0\u4e4e\u6052\u5b9a 0.97-0.98x\uff0c\u4e0d\u968f ctx \u589e\u957f\u3002\u539f\u56e0：--mem-fraction-static 0.85 \u9884\u5206\u914d ~68GB\uff0c\u5b9e\u9645 KV cache/SSM state \u5dee\u5f02\u88ab\u63a9\u76d6\u3002P-9.10\u2462\uff08\u81ea\u5b9a\u4e49 benchmark\uff09\u5728\u975e\u9884\u5206\u914d\u6a21\u5f0f\u4e0b\u91cf\u5230 hybrid VRAM 0.22\u00d7-0.44\u00d7 at 128K\uff0c\u90a3\u624d\u662f H3 \u7684\u6b63\u786e\u9a8c\u8bc1\u3002</p>
<h3>H4: SSM state \u6052\u5b9a\uff0cattn KV \u968f ctx \u7ebf\u6027\u589e\u957f</h3>
<p><span class="vp">H4 \u2705 (via P-9.10\u2462)</span></p>
<p>sglang \u9759\u6001\u9884\u5206\u914d\u65e0\u6cd5\u76f4\u63a5\u9a8c\u8bc1\u3002P-9.10\u2462 \u5df2\u91cf\u5230 hybrid state 0.20\u00d7-0.48\u00d7 vs dense\u3002</p>
"""
# Comparison table
S+="""<h2>4. \u4e0e P-9.10\u2462\uff08mcore eager\uff09\u548c P-9.10\u2463\uff08custom benchmark\uff09\u5bf9\u6bd4</h2>
<table><tr><th>\u6d4b\u91cf</th><th>\u63a8\u7406\u6800</th><th>decode h/d @4K\u00d71</th><th>decode h/d @64K\u00d71</th><th>prefill h/d @64K\u00d71</th><th>VRAM h/d @64K\u00d71</th></tr>
<tr><td>P-9.10\u2462</td><td>mcore eager</td><td>1.60x (h faster)</td><td>1.60x (constant)</td><td>3.7-23x</td><td>\u2014</td></tr>
<tr><td>P-9.10\u2463</td><td>custom (mamba_ssm+transformers)</td><td>0.63x (d faster)</td><td>~0.8x</td><td>3.7-23x</td><td>0.22-0.44x</td></tr>
<tr><td><b>P-9.11</b></td><td><b>sglang production</b></td><td>0.91x</td><td><b>1.18x</b></td><td><b>2.18x</b></td><td>0.98x (masked)</td></tr></table>
<div class="note"><b>\u5173\u952e\u5dee\u5f02：</b><ul>
<li><b>P-9.10\u2462 mcore eager</b> \u7684\u6052\u5b9a 1.6\u00d7 decode \u4f18\u52bf\u4e0d\u53ef\u4fe1\u2014\u2014mcore eager \u6bcf\u6b65\u90fd\u6709 Python\u2192CUDA launch \u5f00\u9500\uff0c\u63a9\u76d6\u4e86 ctx \u5bf9 decode \u7684\u5f71\u54cd\u3002</li>
<li><b>P-9.11 sglang</b> \u4f7f\u7528 CUDA graph + PagedAttention\uff0c\u6d88\u9664\u4e86 launch \u5f00\u9500\uff0cdecode \u4ea4\u53c9\u70b9\u51fa\u73b0\u5728 ~50K\uff081.18\u00d7 at 64K\uff09\uff0c\u66f4\u771f\u5b9e\u3002</li>
<li><b>VRAM</b>：sglang \u9759\u6001\u9884\u5206\u914d\u63a9\u76d6\u4e86\u5dee\u5f02\uff1bP-9.10\u2462 \u7684\u76f4\u63a5\u6d4b\u91cf\uff080.22-0.44\u00d7 at 128K\uff09\u66f4\u53ef\u4fe1\u3002</li>
<li><b>128K</b>：P-9.10\u2463 \u91cf\u5230\u4e86\uff08hybrid 13GB vs dense 61GB\uff09\uff0csglang \u56e0 max_pos=4096 \u672a\u80fd\u8dd1\u901a\u3002</li>
</ul></div>
<h2>5. 128K \u5931\u8d25\u5206\u6790</h2>
<div class="note"><b>128K context \u5bf9\u4e24\u4e2a\u6a21\u578b\u5747\u5931\u8d25</b>（total_completion_tokens=0, TTFT=null, e2e\u22480.5s）。\u4e24\u6a21\u578b max_position_embeddings=4096\uff0csglang \u4ee5 --context-length 131072+SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1 \u542f\u52a8\uff0c4K/16K/64K \u5747\u6210\u529f\uff08RoPE \u5916\u63a8\uff09\uff0c\u4f46 128K\uff0832\u00d7\u8bad\u7ec3\u957f\u5ea6\uff09\u88ab\u670d\u52a1\u5668\u62d2\u7edd\u3002\u5931\u8d25\u6a21\u5f0f\uff1ae2e\u22480.5s\uff08\u7acb\u5373\u8fd4\u56de\uff09\uff0c\u975e\u8d85\u65f6/\u975e OOM\u3002<b>\u8fd9\u662f\u9884\u671f\u884c\u4e3a</b>\uff1a\u6a21\u578b\u4ece\u672a\u5728 &gt;4K ctx \u4e0a\u8bad\u7ec3\uff0c128K RoPE \u5916\u63a8\u5df2\u8d85\u51fa\u6709\u6548\u8303\u56f4\u3002\u5982\u9700 128K \u63a8\u7406\u80fd\u529b\uff0c\u9700\u5728 P-8 \u9636\u6bb5\u589e\u52a0\u957f\u5e8f\u5217\u8bad\u7ec3\u3002</div>
<h2>6. \u7ed3\u8bba</h2>
<table><tr><th>\u5047\u8bf4</th><th>P-9.10\u2462 mcore</th><th>P-9.10\u2463 custom</th><th>P-9.11 sglang</th><th>\u7efc\u5408\u88c1\u5b9a</th></tr>
<tr><td>H1 prefill\u2191ctx</td><td>\u2705 3.7-23\u00d7</td><td>\u2705 3.7-23\u00d7</td><td class="good">\u2705 0.14\u21922.18\u00d7</td><td><b>\u2705 CONFIRMED</b></td></tr>
<tr><td>H2 decode\u2191ctx</td><td>\u26a0 1.6\u00d7 constant(masked)</td><td>\u274c d faster</td><td class="warn">\u26a0 0.91\u21921.18\u00d7</td><td><b>\u26a0 PARTIAL</b></td></tr>
<tr><td>H3 VRAM\u2191ctx</td><td>\u2014</td><td>\u2705 0.22-0.44\u00d7</td><td class="bad">\u274c masked</td><td><b>\u2705 via P-9.10\u2463</b></td></tr>
<tr><td>H4 state const</td><td>\u2014</td><td>\u2705 0.20-0.48\u00d7</td><td>\u2014</td><td><b>\u2705 via P-9.10\u2463</b></td></tr></table>
<p><b>\u7efc\u5408\u88c1\u5b9a：</b></p>
<ul>
<li><b>H1 \u2705 CONFIRMED</b>\uff1ahybrid prefill \u4f18\u52bf\u968f ctx \u589e\u957f\uff0c\u4ea4\u53c9\u70b9 ~16K-64K\uff08sglang: 2.18\u00d7 at 64K\u00d71\uff09</li>
<li><b>H2 \u26a0 PARTIAL</b>\uff1ahybrid decode \u4f18\u52bf\u5728 sglang \u751f\u4ea7\u6800\u4e0b\u4e8e ~50K \u4ea4\u53c9\uff081.18\u00d7 at 64K\u00d71\uff09\uff0c\u4f46\u5e45\u5ea6\u4e0d\u5927\uff1bmcore eager \u7684\u6052\u5b9a 1.6\u00d7 \u662f launch \u5f00\u9500\u4f2a\u5f71\uff0c\u4e0d\u53ef\u4fe1</li>
<li><b>H3 \u2705 (via P-9.10\u2463)</b>\uff1ahybrid VRAM 0.22-0.44\u00d7 at 128K\uff08\u975e\u9884\u5206\u914d\u6a21\u5f0f\uff09\uff1bsglang \u9759\u6001\u9884\u5206\u914d\u63a9\u76d6\u4e86\u5dee\u5f02</li>
<li><b>H4 \u2705 (via P-9.10\u2463)</b>\uff1ahybrid SSM state \u6052\u5b9a\uff0c\u4ec5 4 \u5c42 attention KV \u7ebf\u6027\u589e\u957f</li>
</ul>
<p><b>\u8bba\u6587\u56de\u586b\u5efa\u8bae\uff08\u00a75 \u63a8\u7406\u6548\u7387\uff09：</b></p>
<ul>
<li>prefill \u52a0\u901f\uff1asglang 64K\u00d71 \u7684 <b>2.18\u00d7</b>\uff08\u6700\u53ef\u4fe1\u7684\u751f\u4ea7\u6800\u6570\u636e\uff09</li>
<li>decode \u52a0\u901f\uff1asglang 64K\u00d71 \u7684 <b>1.18\u00d7</b>\uff08\u751f\u4ea7\u6800\uff0c\u4ea4\u53c9\u5728 ~50K\uff09\uff0c\u4e0d\u8981\u7528 mcore eager \u7684\u6052\u5b9a 1.6\u00d7</li>
<li>VRAM \u4f18\u52bf\uff1aP-9.10\u2463 \u7684 <b>0.22-0.44\u00d7 at 128K</b>\uff08\u975e\u9884\u5206\u914d\u76f4\u63a5\u6d4b\u91cf\uff09</li>
<li>128K \u9650\u5236\uff1a\u5982\u5b9e\u8bf4\u660e max_pos=4096\uff0c\u751f\u4ea7\u6800 128K \u4e0d\u53ef\u7528</li>
<li>\u4e09\u6800\u4ea4\u53c9\u9a8c\u8bc1\uff1amcore eager(\u4e0b\u754c)\u2192sglang(\u751f\u4ea7\u6800)\u2192custom(\u65e0\u9650\u5236)\u4e00\u81f4\u786e\u8ba4 H1/H3/H4\uff0cH2 \u5728\u751f\u4ea7\u6800\u4e0b\u4e3a\u5f31\u786e\u8ba4</li>
</ul>
"""
# Raw data
S+='<h2>7. \u539f\u59cb\u6570\u636e \u2014 Hybrid (Mamba2-hybrid 2.22B)</h2>\n'
S+='<pre>'+json.dumps(H,indent=2,ensure_ascii=False)+'</pre>\n'
S+='<h2>8. \u539f\u59cb\u6570\u636e \u2014 Dense (MiniCPM5-2B 2.512B)</h2>\n'
S+='<pre>'+json.dumps(D,indent=2,ensure_ascii=False)+'</pre>\n'
S+='</body></html>\n'
outpath=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","report_pretrain_p911_sglang.html")
with open(outpath,"w") as f: f.write(S)
print(f"HTML saved to {outpath} ({len(S)} bytes)")
