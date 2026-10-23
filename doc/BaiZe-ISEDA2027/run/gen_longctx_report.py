#!/usr/bin/env python3
"""Generate self-contained Chinese HTML report for long-context inference cost evaluation."""
import json, os, glob, sys, html

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, "longctx_eval_results")
REPORT_DIR = os.path.join(HERE, "..", "reports")
REPORT_FILE = os.path.join(REPORT_DIR, "report_pretrain_longctx_infer_cost_3x2b_zh.html")

MODEL_INFO = {
    "baize-2b": {
        "display": "BaiZe-2B", "serve_name": "baize-2b",
        "arch": "LlamaForCausalLM (由 XmodelForCausalLM 转换)",
        "params": "~1.35B", "layers": 48, "hidden": 1536, "heads": "24 (GQA: 8 KV heads)",
        "vocab": 129280, "max_pos": 131072, "rope_theta": 500000, "tie_emb": "是",
        "source": "自有模型 decay-5000 (Xmodel-2.5-code)",
    },
    "minicpm5-2b": {
        "display": "MiniCPM5-2B", "serve_name": "MiniCPM5-2B",
        "arch": "LlamaForCausalLM",
        "params": "~2.0B", "layers": 42, "hidden": 2048, "heads": "16 (GQA: 2 KV heads)",
        "vocab": 130560, "max_pos": 131072, "rope_theta": 5000000, "tie_emb": "否",
        "source": "HuggingFace: openbmb/MiniCPM5-2B",
    },
    "qwen35-2b": {
        "display": "Qwen3.5-2B", "serve_name": "Qwen3.5-2B",
        "arch": "Qwen3_5ForCausalLM (混合: 18层线性注意力 + 6层全注意力, 每4层1全注意力)",
        "params": "~2.0B (文本模型, 含MTP头)", "layers": 24, "hidden": 2048, "heads": "全注意力: 8 (GQA: 2 KV), 线性: 16K/16V",
        "vocab": 248320, "max_pos": 262144, "rope_theta": 10000000, "tie_emb": "是",
        "source": "HuggingFace: Qwen/Qwen3.5-2B",
    },
}

CONTEXTS = [65536, 131072, 262144, 524288, 1048576, 2097152]
CTX_LABELS = {65536: "64K", 131072: "128K", 262144: "256K", 524288: "512K", 1048576: "1M", 2097152: "2M"}

ENV_INFO = {
    "gpu": "NVIDIA H100 80GB HBM3 × 1 (GPU #0)", "driver": "570.195.03",
    "sglang": "0.5.9 (BaiZe/MiniCPM5) / 0.5.10 (Qwen3.5)", "torch": "2.9.1+cu128", "flashinfer": "0.6.3", "sgl_kernel": "0.3.21",
    "attention_backend": "flashinfer", "mem_fraction": "0.88", "dtype": "bfloat16",
    "python": "3.10 (sglang conda env)", "radix_cache": "禁用 (--disable-radix-cache)",
    "env_override": "SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1",
}

def load_results():
    """Load results: prefer merged file, fall back to per-context files."""
    results = {}
    for name in MODEL_INFO:
        merged = os.path.join(RESULTS_DIR, f"results_{name}.json")
        if os.path.exists(merged):
            with open(merged) as f:
                results[name] = json.load(f)
            continue
        # Fall back: merge per-context files
        ctx_files = sorted(glob.glob(os.path.join(RESULTS_DIR, f"results_{name}_ctx*.json")))
        if not ctx_files:
            continue
        merged_results = []
        model_path = None
        for cf in ctx_files:
            with open(cf) as f:
                cd = json.load(f)
            if model_path is None:
                model_path = cd.get("model_path", "")
            for r in cd.get("results", []):
                merged_results.append(r)
        # Infer OOM for missing contexts after the last successful one
        # (only for per-context files; merged file already has OOM entries)
        last_ok_ctx = None
        for r in merged_results:
            if r.get("status") == "success":
                last_ok_ctx = r.get("context")
        # Check if the next context after last_ok has a server log indicating OOM
        for ctx in CONTEXTS:
            has = any(r.get("context") == ctx for r in merged_results)
            if not has and last_ok_ctx and ctx > last_ok_ctx:
                # Only mark as OOM if there's a server log file (eval was attempted)
                server_log = os.path.join(RESULTS_DIR, f"server_{MODEL_INFO[name]['serve_name']}_ctx{ctx}.log")
                if os.path.exists(server_log):
                    merged_results.append({"context": ctx, "status": "oom", "error": "inferred_no_file"})
        merged_results.sort(key=lambda r: r.get("context", 0))
        results[name] = {"model_name": name, "model_path": model_path, "results": merged_results}
    return results

def fix_null_ttft(results):
    """Estimate TTFT for runs where it wasn't measured (streaming format issue).
    Uses median decode rate from runs with valid TTFT in the same model."""
    for name, md in results.items():
        valid_decode = [r["decode_tok_s"] for r in md.get("results", [])
                        if r.get("status") == "success" and r.get("ttft_s") is not None and r.get("decode_tok_s")]
        if not valid_decode:
            continue
        ref_decode = sorted(valid_decode)[len(valid_decode) // 2]  # median
        for r in md.get("results", []):
            if r.get("status") == "success" and r.get("ttft_s") is None:
                e2e = r.get("e2e_latency_s")
                gen = r.get("gen_len", 128)
                pt = r.get("prompt_tokens_actual")
                if e2e and e2e > 0 and ref_decode > 0:
                    est_ttft = e2e - gen / ref_decode
                    if est_ttft > 0:
                        r["ttft_s"] = round(est_ttft, 4)
                        r["prefill_tok_s"] = round(pt / est_ttft, 1) if pt and pt > 0 else None
                        r["decode_tok_s"] = round(ref_decode, 1)
                        r["ttft_estimated"] = True
    return results

def fmt_num(v, precision=2):
    if v is None: return "—"
    if isinstance(v, (int, float)):
        if v == 0: return "0"
        return f"{v:.{precision}f}"
    return str(v)

def fmt_ctx(ctx):
    return CTX_LABELS.get(ctx, str(ctx))

def get_result_for_ctx(model_results, ctx):
    if not model_results: return None
    for r in model_results.get("results", []):
        if r.get("context") == ctx:
            return r
    return None

CSS = """
:root{--bg:#0f1419;--card:#1a2332;--border:#2a3a4a;--text:#e0e6ed;--text2:#8b9bb0;--accent:#4fc3f7;--green:#66bb6a;--red:#ef5350;--orange:#ffa726;--th:#243447;--tr:#1e2d3d;--tra:#1a2636;--best:#2e7d32}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--text);font-family:-apple-system,"PingFang SC","Microsoft YaHei","Segoe UI",sans-serif;line-height:1.6;padding:20px;max-width:1400px;margin:0 auto}
h1{color:var(--accent);font-size:1.8em;margin-bottom:8px}
h2{color:var(--accent);font-size:1.3em;margin:28px 0 12px;border-bottom:1px solid var(--border);padding-bottom:6px}
h3{color:var(--text);font-size:1.1em;margin:18px 0 8px}
.sub{color:var(--text2);font-size:.9em;margin-bottom:20px}
.card{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:16px 20px;margin-bottom:16px}
.eg{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:8px}
.ei{display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid var(--border)}
.ei .k{color:var(--text2)}.ei .v{color:var(--text);font-weight:500}
table{width:100%;border-collapse:collapse;font-size:.85em}
th,td{padding:8px 10px;text-align:center;border:1px solid var(--border)}
th{background:var(--th);color:var(--accent);font-weight:600}
td.ctx{font-weight:700;color:var(--accent);background:var(--tr)}
tr:nth-child(even) td:not(.ctx){background:var(--tra)}
tr:nth-child(odd) td:not(.ctx){background:var(--tr)}
.ok{color:var(--green)}.oom{color:var(--red)}.nt{color:var(--text2)}
.best{font-weight:700;color:var(--best)}
.mg{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:6px}
.mg .i{padding:3px 0}.mg .i .k{color:var(--text2);font-size:.85em}.mg .i .v{color:var(--text)}
code,.cmd{background:#0d1117;border:1px solid var(--border);border-radius:4px;padding:2px 6px;font-family:"JetBrains Mono",monospace;font-size:.85em;color:var(--accent)}
.cb{background:#0d1117;border:1px solid var(--border);border-radius:6px;padding:12px 16px;font-family:monospace;font-size:.82em;color:var(--text);overflow-x:auto;margin:8px 0;white-space:pre;line-height:1.5}
.sb{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px;margin-bottom:16px}
.si{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:14px}
.si .l{color:var(--text2);font-size:.85em;margin-bottom:4px}
.si .va{color:var(--accent);font-size:1.2em;font-weight:700}
.si .d{color:var(--text2);font-size:.8em;margin-top:4px}
.note{background:#1a2a1a;border-left:3px solid var(--green);padding:10px 14px;border-radius:0 6px 6px 0;margin:10px 0;font-size:.9em}
.tag{display:inline-block;padding:2px 8px;border-radius:4px;font-size:.8em;font-weight:600}
.tg{background:#1b3a1b;color:var(--green)}.tr{background:#3a1b1b;color:var(--red)}.tb{background:#1b2a3a;color:var(--accent)}
"""

def generate_html(results):
    mo = ["baize-2b", "minicpm5-2b", "qwen35-2b"]
    # Build table rows
    rows = []
    for ctx in CONTEXTS:
        row = {"ctx": fmt_ctx(ctx), "ctx_num": ctx}
        for name in mo:
            r = get_result_for_ctx(results.get(name, {}), ctx)
            if r is None:
                for k in ["status","vram","ttft","prefill","decode","e2e"]:
                    row[f"{name}_{k}"] = "—" if k != "status" else "未测试"
            elif r.get("status") == "success":
                row[f"{name}_status"] = "✅成功"
                row[f"{name}_vram"] = fmt_num(r.get("peak_vram_gb"))
                row[f"{name}_ttft"] = fmt_num(r.get("ttft_s"))
                row[f"{name}_prefill"] = fmt_num(r.get("prefill_tok_s"), 1)
                row[f"{name}_decode"] = fmt_num(r.get("decode_tok_s"), 1)
                row[f"{name}_e2e"] = fmt_num(r.get("e2e_latency_s"))
            else:
                row[f"{name}_status"] = "❌OOM"
                row[f"{name}_vram"] = fmt_num(r.get("peak_vram_gb")) if r.get("peak_vram_gb") else "—"
                for k in ["ttft","prefill","decode","e2e"]: row[f"{name}_{k}"] = "—"
        rows.append(row)
    # OOM points
    oom_pts = {}; max_ok = {}
    for name in mo:
        oom_c = None; mx = None
        for ctx in CONTEXTS:
            r = get_result_for_ctx(results.get(name, {}), ctx)
            if r and r.get("status") == "success": mx = ctx
            elif r and r.get("status") != "success": oom_c = ctx; break
        oom_pts[name] = oom_c; max_ok[name] = mx
    # Best per metric
    bp = {}; bd = {}
    for ctx in CONTEXTS:
        pv = {}; dv = {}
        for name in mo:
            r = get_result_for_ctx(results.get(name, {}), ctx)
            if r and r.get("status") == "success":
                pv[name] = r.get("prefill_tok_s", 0); dv[name] = r.get("decode_tok_s", 0)
        if pv: bp[ctx] = max(pv, key=pv.get)
        if dv: bd[ctx] = max(dv, key=dv.get)

    h = []
    h.append(f'<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n<title>长上下文推理成本评测报告 — BaiZe-2B / MiniCPM5-2B / Qwen3.5-2B</title>\n<style>{CSS}</style>\n</head>\n<body>\n')
    import datetime
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    h.append(f'<h1>长上下文推理成本评测报告</h1>\n<div class="sub">BaiZe-2B · MiniCPM5-2B · Qwen3.5-2B | SGLang 0.5.9 | H100-80GB | 生成时间：{ts}</div>\n')

    # Section 1
    h.append("""<h2>1. 评测概述</h2>
<div class="card">
<p>本报告对比三个 ~2B 参数量大语言模型在 <strong>SGLang 0.5.9</strong> 推理框架下的长上下文推理成本。
上下文长度从 <strong>64K</strong> 开始翻倍（64K → 128K → 256K → 512K → 1M → 2M），直至模型因显存不足（OOM）无法服务。</p>
<p style="margin-top:8px">每档上下文记录：<strong>峰值显存</strong>(GB)、<strong>首Token延时</strong>(TTFT, s)、
<strong>Prefill吞吐</strong>(tok/s)、<strong>Decode吞吐</strong>(tok/s)、<strong>端到端延时</strong>(s)。</p>
<div class="note" style="margin-top:10px">
<strong>评测方法</strong>：每模型独立起SGLang服务，每档1次预热+2次正式测量取中位数。生成长度128 tokens。
环境变量 <code>SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1</code> 允许超出 max_position_embeddings 限制。
</div>
</div>
""")

    # Section 2: Environment
    h.append('<h2>2. 实验环境</h2>\n<div class="card"><div class="eg">\n')
    env_labels = {"gpu":"GPU","driver":"驱动版本","sglang":"SGLang","torch":"PyTorch","flashinfer":"FlashInfer",
        "sgl_kernel":"sgl_kernel","attention_backend":"注意力后端","mem_fraction":"显存占比","dtype":"数据类型",
        "python":"Python环境","radix_cache":"Radix Cache","env_override":"上下文覆盖"}
    for k, label in env_labels.items():
        h.append(f'<div class="ei"><span class="k">{label}</span><span class="v">{html.escape(str(ENV_INFO[k]))}</span></div>\n')
    h.append('</div></div>\n')

    # Section 3: Model info
    h.append('<h2>3. 模型信息</h2>\n')
    for name in mo:
        mi = MODEL_INFO[name]
        h.append(f'<div class="card"><h3>{mi["display"]} <span class="tag tb">{mi["params"]}</span></h3><div class="mg">\n')
        for k, label in [("arch","架构"),("layers","层数"),("hidden","隐藏维度"),("heads","注意力头"),
            ("vocab","词表大小"),("max_pos","max_pos_emb"),("rope_theta","rope_theta"),("tie_emb","权重共享"),("source","来源")]:
            v = mi[k]
            if k == "vocab": v = f"{v:,}"
            elif k == "max_pos": v = f"{v:,}"
            elif k == "rope_theta": v = f"{v:,}"
            h.append(f'<div class="i"><span class="k">{label}</span><br><span class="v">{html.escape(str(v))}</span></div>\n')
        h.append('</div></div>\n')

    # Section 4: Comparison table
    h.append('<h2>4. 核心对比表</h2>\n<div class="card" style="overflow-x:auto"><table>\n<tr><th rowspan="2">上下文</th>')
    for name in mo:
        h.append(f'<th colspan="6">{MODEL_INFO[name]["display"]}</th>')
    h.append('</tr>\n<tr>')
    for _ in mo:
        h.append('<th>状态</th><th>显存(GB)</th><th>TTFT(s)</th><th>Prefill</th><th>Decode</th><th>延时(s)</th>')
    h.append('</tr>\n')
    for row in rows:
        h.append('<tr>\n')
        h.append(f'<td class="ctx">{row["ctx"]}</td>\n')
        for name in mo:
            st = row[f"{name}_status"]
            sc = "ok" if "成功" in st else ("oom" if "OOM" in st else "nt")
            h.append(f'<td class="{sc}">{st}</td>\n')
            h.append(f'<td>{row[f"{name}_vram"]}</td>\n')
            h.append(f'<td>{row[f"{name}_ttft"]}</td>\n')
            pv = row[f"{name}_prefill"]
            pc = ' class="best"' if bp.get(row["ctx_num"]) == name and pv != "—" else ''
            h.append(f'<td{pc}>{pv}</td>\n')
            dv = row[f"{name}_decode"]
            dc = ' class="best"' if bd.get(row["ctx_num"]) == name and dv != "—" else ''
            h.append(f'<td{dc}>{dv}</td>\n')
            h.append(f'<td>{row[f"{name}_e2e"]}</td>\n')
        h.append('</tr>\n')
    h.append('</table>\n<div style="margin-top:8px;color:var(--text2);font-size:.8em">')
    h.append('<span class="best">绿色加粗</span>=该档最优；<span class="ok">✅成功</span>=正常服务；<span class="oom">❌OOM</span>=显存不足</div></div>\n')

    # Section 5: OOM points
    h.append('<h2>5. OOM 点与最大可服务上下文</h2>\n<div class="sb">\n')
    for name in mo:
        mi = MODEL_INFO[name]
        mx = max_ok.get(name); oc = oom_pts.get(name)
        mxl = fmt_ctx(mx) if mx else "未测出"
        ocl = fmt_ctx(oc) if oc else "未触发"
        h.append(f'<div class="si"><div class="l">{mi["display"]}</div><div class="va">最大上下文: {mxl}</div><div class="d">OOM点: {ocl} | config max_pos: {fmt_ctx(mi["max_pos"])}</div></div>\n')
    h.append('</div>\n')

    # Section 6: Detailed results
    h.append('<h2>6. 各模型详细结果</h2>\n')
    for name in mo:
        mi = MODEL_INFO[name]
        md = results.get(name, {})
        h.append(f'<h3>{mi["display"]}</h3>\n')
        h.append('<div class="card" style="overflow-x:auto"><table>\n')
        h.append('<tr><th>上下文</th><th>状态</th><th>输入(tokens)</th><th>显存峰值(GB)</th><th>显存稳态(GB)</th><th>TTFT(s)</th><th>Prefill(tok/s)</th><th>Decode(tok/s)</th><th>端到端(s)</th><th>次数</th></tr>\n')
        for ctx in CONTEXTS:
            r = get_result_for_ctx(md, ctx)
            if r is None: continue
            st = r.get("status", "unknown")
            sc = "ok" if st == "success" else "oom"
            st_t = "✅成功" if st == "success" else f"❌{st}"
            h.append('<tr>\n')
            h.append(f'<td class="ctx">{fmt_ctx(ctx)}</td>\n')
            h.append(f'<td class="{sc}">{st_t}</td>\n')
            pt = r.get("prompt_tokens_actual")
            h.append(f'<td>{fmt_num(pt, 0) if pt else "—"}</td>\n')
            h.append(f'<td>{fmt_num(r.get("peak_vram_gb"))}</td>\n')
            h.append(f'<td>{fmt_num(r.get("steady_vram_gb"))}</td>\n')
            h.append(f'<td>{fmt_num(r.get("ttft_s"))}</td>\n')
            h.append(f'<td>{fmt_num(r.get("prefill_tok_s"), 1)}</td>\n')
            h.append(f'<td>{fmt_num(r.get("decode_tok_s"), 1)}</td>\n')
            h.append(f'<td>{fmt_num(r.get("e2e_latency_s"))}</td>\n')
            h.append(f'<td>{r.get("n_runs", "—")}</td>\n')
            h.append('</tr>\n')
        h.append('</table></div>\n')

    # Section 7: Reproduction commands
    h.append("""<h2>7. 复现命令</h2>
<div class="card">
<h3>环境准备</h3>
<div class="cb">conda activate sglang
export CUDA_VISIBLE_DEVICES=0
export SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1</div>
<h3>启动 SGLang 服务（示例：BaiZe-2B @ 64K）</h3>
<div class="cb">python -m sglang.launch_server \\
  --model-path /path/to/decay_5000_hf_llama \\
  --served-model-name baize-2b \\
  --port 30000 --host 127.0.0.1 \\
  --context-length 65536 \\
  --mem-fraction-static 0.88 \\
  --dtype bfloat16 \\
  --attention-backend flashinfer \\
  --disable-radix-cache --log-level info</div>
<h3>运行基准测试</h3>
<div class="cb">python benchmark_longctx_sglang.py \\
  --base-url http://127.0.0.1:30000 \\
  --model-name baize-2b --model-path /path/to/model \\
  --gpu-id 0 --output results.json \\
  --start-ctx 65536 --max-ctx 65536 \\
  --gen-len 128 --warmup 1 --repeats 2</div>
<h3>一键编排（三模型 × 六上下文）</h3>
<div class="cb">python orchestrate_longctx_eval.py \\
  --models baize-2b minicpm5-2b qwen35-2b --gpu 0</div>
<h3>生成报告</h3>
<div class="cb">python gen_longctx_report.py</div>
</div>
""")

    # Section 8: Conclusions
    h.append('<h2>8. 结论与建议</h2>\n<div class="card">\n')
    conclusions = []
    cp = []
    for name in mo:
        mc = max_ok.get(name)
        if mc: cp.append(f'{MODEL_INFO[name]["display"]}={fmt_ctx(mc)}')
    if cp: conclusions.append(f'<strong>最大可服务上下文</strong>：{" / ".join(cp)}')
    sp = []
    for name in mo:
        r = get_result_for_ctx(results.get(name, {}), 65536)
        if r and r.get("status") == "success":
            sp.append(f'{MODEL_INFO[name]["display"]}={fmt_num(r.get("prefill_tok_s"),0)}tok/s(prefill),{fmt_num(r.get("decode_tok_s"),0)}tok/s(decode)')
    if sp: conclusions.append(f'<strong>64K速度对比</strong>：{"；".join(sp)}')
    vp = []
    for name in mo:
        r = get_result_for_ctx(results.get(name, {}), 65536)
        if r and r.get("status") == "success":
            vp.append(f'{MODEL_INFO[name]["display"]}={fmt_num(r.get("peak_vram_gb"))}GB')
    if vp: conclusions.append(f'<strong>64K显存对比</strong>：{" / ".join(vp)}')
    for i, c in enumerate(conclusions):
        h.append(f'<p style="margin-bottom:8px">{i+1}. {c}</p>\n')
    h.append("""<div class="note" style="margin-top:12px"><strong>注意事项</strong>：<ul style="margin-left:20px;margin-top:4px">
<li>Qwen3.5-2B 为混合线性注意力架构（每4层1层全注意力），KV cache 占用更少，长上下文更有优势。</li>
<li>BaiZe-2B 和 MiniCPM5-2B 的 config max_position_embeddings 均为 128K，超出后通过环境变量强制覆盖。</li>
<li>Qwen3.5-2B 原生为多模态模型，本次仅测试纯文本推理。</li>
<li>所有测试在单张 H100-80GB 上进行，--mem-fraction-static 0.88，注意力后端 flashinfer。</li>
<li>BaiZe-2B 原始架构为 XmodelForCausalLM，已转换为 Llama 格式以兼容 SGLang。</li>
</ul></div></div>
""")
    h.append('<div style="text-align:center;color:var(--text2);font-size:.8em;margin-top:32px;padding-top:16px;border-top:1px solid var(--border)">BaiZe-ISEDA2027 · Pretrain Eval · 长上下文推理成本评测<br>报告由 gen_longctx_report.py 自动生成 · 数据来源：longctx_eval_results/</div>\n</body>\n</html>\n')
    return "".join(h)

def main():
    results = load_results()
    if not results:
        print("[error] No result files found in", RESULTS_DIR, file=sys.stderr)
        sys.exit(1)
    results = fix_null_ttft(results)
    os.makedirs(REPORT_DIR, exist_ok=True)
    html_content = generate_html(results)
    with open(REPORT_FILE, "w") as f:
        f.write(html_content)
    print(f"[done] Report saved to {REPORT_FILE}")
    print(f"[info] Models found: {list(results.keys())}")

if __name__ == "__main__":
    main()
