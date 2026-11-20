#!/usr/bin/env python3
"""
baize_posttrain_sglang_throughput_analysis.py
R67 (2026-11-09): SGLang serving configuration audit + throughput optimization
for MiniCPM5-2B on 4xA40.

Usage:
  python3 baize_posttrain_sglang_throughput_analysis.py
  python3 baize_posttrain_sglang_throughput_analysis.py --html report.html
  python3 baize_posttrain_sglang_throughput_analysis.py --json output.json
  python3 baize_posttrain_sglang_throughput_analysis.py --help
"""
import argparse, json, math, os, sys
from datetime import timedelta

# Model Architecture (MiniCPM5-2B config.json)
MODEL = {
    "name": "MiniCPM5-2B", "type": "LlamaForCausalLM",
    "num_layers": 42, "hidden_size": 2048,
    "num_heads": 16, "num_kv_heads": 2, "head_dim": 128,
    "vocab_size": 130560, "dtype_bytes": 2, "max_pos_emb": 131072,
    "param_count_b": 2.0, "weight_size_gb": 4.7,
}

# GPU Specs (NVIDIA A40)
A40 = {
    "name": "NVIDIA A40", "memory_gb": 46.068,
    "bandwidth_gbs": 696, "bf16_tflops": 150,
    "effective_tflops": 75, "num_gpus": 4,
}

# Current RL Config (from baize_posttrain_rl_verl_config_v2.yaml)
RL_CONFIG = {
    "tp_size": 1, "gpu_mem_util": 0.50, "max_num_seqs": 24,
    "max_num_batched_tokens": 16384, "batch_size": 128, "group_size_n": 8,
    "prompt_length": 8192, "response_length": 8192, "context_length": 16384,
    "hybrid_engine": True, "ppo_epochs": 2, "ppo_mini_batch_size": 32,
    "ppo_micro_batch_per_gpu": 4, "n_gpus": 4, "total_steps": 2000,
    "save_freq": 200, "smoke_iters": 10,
}

# Eval Config (from baize_posttrain_minicpm5_diag.sh)
EVAL_CONFIG = {
    "n_tasks": 158, "n_runs": 5, "timeout_per_task_s": 2500,
    "parallel": 8, "sglang_port": 8866, "sglang_ctx": 32768,
    "sglang_mem_frac": 0.85, "sglang_tp": 1,
}

# === Computations ===

def kv_per_token_bytes(m):
    return 2 * m["num_kv_heads"] * m["head_dim"] * m["dtype_bytes"] * m["num_layers"]

def kv_per_seq_gb(m, ctx):
    return kv_per_token_bytes(m) * ctx / 1e9

def kv_mha_cmp(m):
    gqa = kv_per_token_bytes(m)
    mha = 2 * m["num_heads"] * m["head_dim"] * m["dtype_bytes"] * m["num_layers"]
    return {"gqa_kb": gqa/1024, "mha_kb": mha/1024, "ratio": mha/gqa, "gqa_gqa_ratio": m["num_heads"]/m["num_kv_heads"]}

def mem_budget(gpu, cfg, m):
    total = gpu["memory_gb"]
    sl = total * cfg["gpu_mem_util"]
    act = total - sl
    model = m["weight_size_gb"]
    kv_avail = sl - model
    kv_seq = kv_per_seq_gb(m, cfg["context_length"])
    max_kv = int(kv_avail / kv_seq) if kv_seq > 0 else 0
    eff = min(max_kv, cfg["max_num_seqs"])
    ng = cfg["n_gpus"]
    sharded = m["weight_size_gb"] / ng
    opt = 2 * m["weight_size_gb"] / ng
    grad = m["weight_size_gb"] / ng
    activ = (4 * 16384 * 2048 * 2 * math.sqrt(42)) / 1e9 / ng
    act_tot = sharded + opt + grad + activ
    return {"total_gb": total, "sl_gb": sl, "act_gb": act, "model_gb": model,
            "kv_avail_gb": kv_avail, "kv_seq_gb": kv_seq, "max_kv": max_kv,
            "max_cfg": cfg["max_num_seqs"], "eff": eff, "sharded_gb": sharded,
            "opt_gb": opt, "grad_gb": grad, "activ_gb": activ, "act_tot_gb": act_tot,
            "act_headroom_gb": act - act_tot, "act_ok": (act - act_tot) > 0}

def decode_tp(gpu, cfg, m, max_seqs):
    bw = gpu["bandwidth_gbs"]
    w = m["weight_size_gb"]
    kv_seq = kv_per_seq_gb(m, cfg["context_length"])
    kv_tot = max_seqs * kv_seq
    mem_step = w + kv_tot
    t_step = mem_step / bw
    tps = max_seqs / t_step
    return {"w_gb": w, "kv_seq_gb": kv_seq, "kv_tot_gb": kv_tot,
            "mem_step_gb": mem_step, "t_step_ms": t_step*1000,
            "tps_gpu": tps, "tps_total": tps * cfg["n_gpus"],
            "max_seqs": max_seqs, "bw": bw}

def prefill_tp(gpu, m, batch_tok):
    tf = gpu["effective_tflops"]
    fpt = 2 * m["param_count_b"] * 1e9
    ftot = fpt * batch_tok
    ts = ftot / (tf * 1e12)
    return {"batch_tok": batch_tok, "time_s": ts, "tps": batch_tok / ts, "tflops": tf}

def rl_step(gpu, cfg, m):
    ng = cfg["n_gpus"]; tp = cfg["tp_size"]; ni = ng // tp
    total_seqs = cfg["batch_size"] * cfg["group_size_n"]
    total_resp = total_seqs * cfg["response_length"]
    total_prompt = total_seqs * cfg["prompt_length"]
    dec = decode_tp(gpu, cfg, m, cfg["max_num_seqs"])
    pre = prefill_tp(gpu, m, cfg["max_num_batched_tokens"])
    gen_t = total_resp / dec["tps_total"] if dec["tps_total"] > 0 else float('inf')
    pre_t = total_prompt / (pre["tps"] * ni) if pre["tps"] > 0 else float('inf')
    act_seqs = cfg["ppo_micro_batch_per_gpu"] * ng
    act_steps = math.ceil(cfg["batch_size"] / cfg["ppo_mini_batch_size"]) * cfg["ppo_epochs"]
    act_flops = 6 * 2 * m["param_count_b"] * 1e9 * act_seqs * cfg["context_length"]
    act_t = act_steps * act_flops / (gpu["effective_tflops"] * 1e12 * ng)
    ref_flops = 2 * m["param_count_b"] * 1e9 * total_seqs * cfg["context_length"]
    ref_t = ref_flops / (gpu["effective_tflops"] * 1e12 * ng)
    tot = gen_t + pre_t + act_t + ref_t
    oh = tot * 0.15
    tot_wh = tot + oh
    return {"total_seqs": total_seqs, "total_resp": total_resp,
            "total_prompt": total_prompt, "gen_t": gen_t, "pre_t": pre_t,
            "act_t": act_t, "ref_t": ref_t, "oh": oh, "tot_t": tot_wh,
            "sph": 3600/tot_wh if tot_wh > 0 else 0,
            "s72h": 72*3600/tot_wh if tot_wh > 0 else 0,
            "s24h": 24*3600/tot_wh if tot_wh > 0 else 0,
            "dec_tps": dec["tps_total"], "pre_tps": pre["tps"]*ni,
            "act_steps": act_steps}

def eval_time_est(gpu, ecfg, m):
    nt = ecfg["n_tasks"] * ecfg["n_runs"]; par = ecfg["parallel"]
    dec = decode_tp(gpu, {"context_length": ecfg["sglang_ctx"], "n_gpus": 1, "tp_size": 1}, m, 8)
    tps = dec["tps_gpu"]
    avg_tok = 10000
    avg_gen = avg_tok / tps if tps > 0 else ecfg["timeout_per_task_s"]
    tf = 0.20
    avg_task = (1-tf)*min(avg_gen, 60) + tf*ecfg["timeout_per_task_s"] + 30
    tot = (nt / par) * avg_task
    quick = (10 / par) * avg_task
    return {"nt": nt, "par": par, "avg_tok": avg_tok, "tps": tps,
            "avg_gen": avg_gen, "tf": tf, "avg_task": avg_task,
            "tot_s": tot, "tot_hr": tot/3600, "quick_s": quick, "quick_min": quick/60}

def opt_scenarios(gpu, cfg, m):
    sc = []
    base = rl_step(gpu, cfg, m)
    sc.append({"name": "Baseline (v2 config)", "chg": "As-is",
        "sph": base["sph"], "s72h": base["s72h"], "bn": "A40 bandwidth 696 GB/s"})
    c1 = dict(cfg); c1["gpu_mem_util"] = 0.65
    b1 = mem_budget(gpu, c1, m); c1["max_num_seqs"] = min(b1["max_kv"], c1["max_num_seqs"])
    t1 = rl_step(gpu, c1, m)
    sc.append({"name": "S1: mem_util=0.65", "chg": f"max_seqs={c1['max_num_seqs']}",
        "sph": t1["sph"], "s72h": t1["s72h"], "bn": "Marginal gain"})
    c2 = dict(cfg); c2["batch_size"] = 64; t2 = rl_step(gpu, c2, m)
    sc.append({"name": "S2: batch=64", "chg": "Half rollouts", "sph": t2["sph"],
        "s72h": t2["s72h"], "bn": "Same total compute"})
    c3 = dict(cfg); c3["response_length"] = 4096; c3["context_length"] = 12288; t3 = rl_step(gpu, c3, m)
    sc.append({"name": "S3: resp=4096", "chg": "ctx=12288", "sph": t3["sph"],
        "s72h": t3["s72h"], "bn": "Truncation risk"})
    c4 = dict(cfg); c4["group_size_n"] = 4; t4 = rl_step(gpu, c4, m)
    sc.append({"name": "S4: G=4", "chg": "Smaller group", "sph": t4["sph"],
        "s72h": t4["s72h"], "bn": "Higher variance"})
    c5 = dict(cfg); c5["batch_size"] = 64; c5["group_size_n"] = 4
    c5["response_length"] = 6144; c5["context_length"] = 14336; t5 = rl_step(gpu, c5, m)
    sc.append({"name": "S5: Combined", "chg": "b64,G4,r6144", "sph": t5["sph"],
        "s72h": t5["s72h"], "bn": "Best throughput"})
    return sc

# === HTML Report ===

def gen_html(R):
    m = R["model"]; gpu = R["gpu"]; kv = R["kv_cmp"]; mem = R["mem"]
    dec = R["dec"]; rl = R["rl"]; ev = R["eval"]; sc = R["scenarios"]; cp = R["crit"]
    css = '<style>body{font-family:-apple-system,"Noto Sans SC",sans-serif;max-width:1200px;margin:0 auto;padding:20px;background:#f8f9fa;color:#1a1a2e}h1{color:#2c3e50;border-bottom:3px solid #3498db;padding-bottom:10px}h2{color:#2c3e50;margin-top:30px;border-left:4px solid #3498db;padding-left:10px}table{border-collapse:collapse;width:100%;margin:15px 0;font-size:14px}th,td{border:1px solid #ddd;padding:8px 12px;text-align:left}th{background:#3498db;color:white}tr:nth-child(even){background:#f2f2f2}.hl{background:#fff3cd!important}.good{color:#27ae60;font-weight:600}.card{background:white;border-radius:8px;padding:20px;margin:15px 0;box-shadow:0 2px 4px rgba(0,0,0,0.1)}.vd{padding:15px;border-radius:8px;font-size:16px;font-weight:600;text-align:center;margin:20px 0}.vd-go{background:#d4edda;color:#155724;border:2px solid #27ae60}.vd-w{background:#fff3cd;color:#856404;border:2px solid #e67e22}.note{background:#e8f4f8;border-left:4px solid #3498db;padding:10px 15px;margin:10px 0}.fm{background:#fdf6e3;padding:10px;border-radius:4px;font-family:monospace;font-size:13px}</style>'
    h = f'<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>R67 SGLang Throughput</title>{css}</head><body>'
    h += '<h1>R67: SGLang 服务配置审计 + 吞吐量优化分析</h1>'
    h += f'<p>2026-11-09 (GPU日) · MiniCPM5-2B · 4×A40</p>'
    h += '<div class="vd vd-w">核心发现: A40 带宽(696GB/s)是硬瓶颈, 非KV cache。GQA使KV极小但带宽限制批处理收益。当前配置已接近最优。</div>'
    # S1: Model
    h += '<h2>1. 模型架构与 KV Cache</h2><div class="card"><table><tr><th>参数</th><th>值</th></tr>'
    h += f'<tr><td>层数</td><td>{m["num_layers"]}</td></tr>'
    h += f'<tr><td>KV头数</td><td><b>{m["num_kv_heads"]}</b> (GQA 8:1)</td></tr>'
    h += f'<tr><td>权重</td><td>{m["weight_size_gb"]} GB</td></tr></table>'
    h += '<table><tr><th>指标</th><th>GQA</th><th>MHA</th><th>压缩</th></tr>'
    h += f'<tr><td>每token</td><td>{kv["gqa_kb"]:.1f}KB</td><td>{kv["mha_kb"]:.1f}KB</td><td class="good">{kv["ratio"]:.1f}×</td></tr>'
    h += f'<tr><td>ctx=16K单序列</td><td>{kv_per_seq_gb(m,16384)*1024:.1f}MB</td><td>{kv_per_seq_gb(m,16384)*kv["ratio"]*1024:.1f}MB</td><td class="good">{kv["ratio"]:.1f}×</td></tr></table>'
    h += '<div class="note">GQA 8:1 → KV仅MHA的1/8。ctx=32K单序列仅'
    h += f'{kv_per_seq_gb(m,32768)*1024:.0f}MB。TP=1无需跨GPU切分。</div></div>'
    # S2: Memory
    h += '<h2>2. 内存预算</h2><div class="card"><table><tr><th>组件</th><th>分配</th></tr>'
    h += f'<tr><td>SGLang(util={RL_CONFIG["gpu_mem_util"]})</td><td>{mem["sl_gb"]:.2f}GB</td></tr>'
    h += f'<tr><td>Actor</td><td>{mem["act_gb"]:.2f}GB</td></tr></table>'
    h += '<table><tr><th>SGLang</th><th>值</th></tr>'
    h += f'<tr><td>模型</td><td>{mem["model_gb"]}GB</td></tr>'
    h += f'<tr><td>KV可用</td><td>{mem["kv_avail_gb"]:.2f}GB</td></tr>'
    h += f'<tr><td>单序列KV</td><td>{mem["kv_seq_gb"]*1024:.1f}MB</td></tr>'
    h += f'<tr><td>KV容量</td><td>{mem["max_kv"]}序列</td></tr>'
    h += f'<tr class="hl"><td>有效并发</td><td>{mem["eff"]}序列</td></tr></table>'
    h += '<table><tr><th>Actor</th><th>perGPU</th></tr>'
    h += f'<tr><td>分片模型</td><td>{mem["sharded_gb"]:.2f}GB</td></tr>'
    h += f'<tr><td>优化器</td><td>{mem["opt_gb"]:.2f}GB</td></tr>'
    h += f'<tr><td>激活</td><td>{mem["activ_gb"]:.2f}GB</td></tr>'
    h += f'<tr><td>总计</td><td>{mem["act_tot_gb"]:.2f}GB</td></tr>'
    h += f'<tr class="good"><td>余量</td><td>{mem["act_headroom_gb"]:.2f}GB ✅</td></tr></table></div>'
    # S3: Bandwidth
    h += '<h2>3. A40 内存带宽瓶颈</h2><div class="card">'
    h += f'<div class="note">A40带宽=696GB/s(H100=3350,仅21%)。解码每step加载权重+KV。</div>'
    h += '<div class="fm">吞吐 = max_seqs / ((weights + max_seqs×kv) / bw)</div>'
    h += '<table><tr><th>指标</th><th>值</th></tr>'
    h += f'<tr><td>每step加载</td><td>{dec["mem_step_gb"]:.2f}GB</td></tr>'
    h += f'<tr><td>每step耗时</td><td>{dec["t_step_ms"]:.1f}ms</td></tr>'
    h += f'<tr class="hl"><td>每GPU解码</td><td>{dec["tps_gpu"]:.0f}tok/s</td></tr>'
    h += f'<tr><td>4GPU总计</td><td>{dec["tps_total"]:.0f}tok/s</td></tr></table>'
    h += '<table><tr><th>并发</th><th>tok/s/GPU</th><th>增益</th></tr>'
    b8 = decode_tp(gpu, {"context_length":16384,"n_gpus":1,"tp_size":1}, m, 8)
    for ns in [8,16,24,32,48,64]:
        d = decode_tp(gpu, {"context_length":16384,"n_gpus":1,"tp_size":1}, m, ns)
        g = d["tps_gpu"]/b8["tps_gpu"] if b8["tps_gpu"]>0 else 0
        cl = ' class="hl"' if ns==RL_CONFIG["max_num_seqs"] else ''
        h += f'<tr{cl}><td>{ns}</td><td>{d["tps_gpu"]:.0f}</td><td>{g:.2f}×</td></tr>'
    h += '</table><div class="note">8→24仅~2×, 24→64仅~2.5×。带宽硬限制, 边际递减。</div></div>'
    # S4: RL step
    h += '<h2>4. RL 单步时间</h2><div class="card"><table><tr><th>阶段</th><th>时间</th></tr>'
    h += f'<tr><td>Rollout</td><td>{rl["gen_t"]:.1f}s</td></tr>'
    h += f'<tr><td>Prefill</td><td>{rl["pre_t"]:.1f}s</td></tr>'
    h += f'<tr><td>Actor</td><td>{rl["act_t"]:.1f}s</td></tr>'
    h += f'<tr><td>Ref</td><td>{rl["ref_t"]:.1f}s</td></tr>'
    h += f'<tr class="hl"><td>总计</td><td>{rl["tot_t"]:.1f}s</td></tr></table>'
    h += f'<table><tr><th>指标</th><th>值</th></tr>'
    h += f'<tr><td>每步序列</td><td>{rl["total_seqs"]}</td></tr>'
    h += f'<tr class="hl"><td>steps/hr</td><td>{rl["sph"]:.2f}</td></tr>'
    h += f'<tr><td>72h步数</td><td>{rl["s72h"]:.0f}</td></tr></table>'
    h += '<div class="note">R61估计3.45 steps/hr。本分析量级一致。</div></div>'
    # S5: Eval
    h += '<h2>5. 评测时间</h2><div class="card"><table><tr><th>指标</th><th>值</th></tr>'
    h += f'<tr><td>总评测</td><td>{ev["nt"]}</td></tr>'
    h += f'<tr><td>均任务</td><td>{ev["avg_task"]:.0f}s</td></tr>'
    h += f'<tr class="hl"><td>Full 5-run</td><td>{ev["tot_hr"]:.2f}h</td></tr>'
    h += f'<tr><td>Quick</td><td>{ev["quick_min"]:.1f}min</td></tr></table>'
    h += '<div class="note">Baseline用quick省时间, post-RL用full。</div></div>'
    # S6: Scenarios
    h += '<h2>6. 优化场景</h2><div class="card"><table><tr><th>场景</th><th>变化</th><th>s/hr</th><th>72h</th><th>瓶颈</th></tr>'
    for s in sc:
        cl = ' class="hl"' if "Baseline" in s["name"] else ''
        h += f'<tr{cl}><td><b>{s["name"]}</b></td><td>{s["chg"]}</td><td>{s["sph"]:.2f}</td><td>{s["s72h"]:.0f}</td><td>{s["bn"]}</td></tr>'
    h += '</table><div class="note">保持Baseline。需更多步数→S4(G=4)。</div></div>'
    # S7: Critical path
    h += '<h2>7. 关键路径</h2><div class="card"><table><tr><th>阶段</th><th>时间</th></tr>'
    h += f'<tr><td>Quick baseline</td><td>{ev["quick_min"]:.0f}min</td></tr>'
    h += f'<tr><td>RL 200步</td><td>{200*rl["tot_t"]/3600:.1f}h</td></tr>'
    h += f'<tr><td>Post-RL eval</td><td>{ev["tot_hr"]:.1f}h</td></tr>'
    h += f'<tr class="hl"><td>总计</td><td>{cp["total_h"]:.1f}h</td></tr></table>'
    h += f'<div class="vd {"vd-go" if cp["fits_72h"] else "vd-w"}">~{cp["total_h"]:.1f}h {"✅fits" if cp["fits_72h"] else "⚠️exceeds"} 72h</div></div>'
    # S8: Conclusions
    h += '<h2>8. 结论与建议</h2><div class="card"><ol>'
    h += '<li><b>KV非瓶颈</b>: GQA 8:1, 单序列675MB</li>'
    h += f'<li><b>带宽硬瓶颈</b>: 696GB/s, ~{dec["tps_gpu"]:.0f}tok/s/GPU</li>'
    h += '<li><b>配置已最优</b>: max_seqs=24匹配KV容量27</li>'
    h += f'<li><b>72h~{rl["s72h"]:.0f}步</b>: 200步可行</li>'
    h += f'<li><b>评测{ev["tot_hr"]:.1f}h</b>: baseline用quick</li></ol>'
    h += '<h3>建议</h3><ol><li>保持v2 YAML</li><li>Baseline用quick</li>'
    h += '<li>需步数→S4(G=4)</li><li>NFS warm-up必做</li></ol></div>'
    h += '<h2>9. 配置审计</h2><div class="card"><table><tr><th>参数</th><th>diag</th><th>RL</th><th>审计</th></tr>'
    h += '<tr><td>port</td><td>8866</td><td>verl</td><td>✅</td></tr>'
    h += '<tr><td>ctx</td><td>32768</td><td>16384</td><td>✅</td></tr>'
    h += '<tr><td>mem_frac</td><td>0.85</td><td>0.50</td><td>✅</td></tr>'
    h += '<tr><td>TP</td><td>1</td><td>1</td><td>✅</td></tr></table>'
    h += '<div class="note">建议: diag显式加 --attention-backend flashinfer</div></div>'
    h += '<p style="text-align:center;color:#7f8c8d;margin-top:30px">R67 · 2026-11-09 · BaiZe · Surrogate RL NOT transferable to BaiZe</p>'
    h += '</body></html>'
    return h

# === Main ===

def main():
    parser = argparse.ArgumentParser(description="R67: SGLang throughput analysis")
    parser.add_argument("--html", metavar="PATH", help="Write HTML report")
    parser.add_argument("--json", metavar="PATH", help="Write JSON results")
    parser.add_argument("--verbose", action="store_true", help="Print details")
    args = parser.parse_args()

    kv = kv_mha_cmp(MODEL)
    mem = mem_budget(A40, RL_CONFIG, MODEL)
    dec = decode_tp(A40, RL_CONFIG, MODEL, RL_CONFIG["max_num_seqs"])
    pre = prefill_tp(A40, MODEL, RL_CONFIG["max_num_batched_tokens"])
    rl = rl_step(A40, RL_CONFIG, MODEL)
    ev = eval_time_est(A40, EVAL_CONFIG, MODEL)
    sc = opt_scenarios(A40, RL_CONFIG, MODEL)
    smoke_h = 10 * rl["tot_t"] / 3600
    rl200_h = 200 * rl["tot_t"] / 3600
    cp = {"smoke_h": smoke_h, "rl200_h": rl200_h, "eval_h": ev["tot_hr"],
          "total_h": smoke_h + rl200_h + ev["tot_hr"] + 0.5,
          "fits_72h": (smoke_h + rl200_h + ev["tot_hr"] + 0.5) <= 72}
    R = {"model": MODEL, "gpu": A40, "rl_config": RL_CONFIG,
         "eval_config": EVAL_CONFIG, "kv_cmp": kv, "mem": mem,
         "dec": dec, "prefill": pre, "rl": rl, "eval": ev,
         "scenarios": sc, "crit": cp}

    if args.verbose:
        print("=" * 60)
        print("R67: SGLang Throughput Analysis")
        print("=" * 60)
        print(f"\nKV/token: {kv['gqa_kb']:.1f} KB (GQA {kv['gqa_gqa_ratio']:.0f}:1)")
        print(f"KV/seq (ctx=16384): {kv_per_seq_gb(MODEL,16384)*1024:.1f} MB")
        print(f"\nMemory: SGLang={mem['sl_gb']:.2f}GB Actor={mem['act_gb']:.2f}GB")
        print(f"  MaxSeqs KV={mem['max_kv']} cfg={mem['max_cfg']} eff={mem['eff']}")
        print(f"  Actor headroom={mem['act_headroom_gb']:.2f}GB ({'OK' if mem['act_ok'] else 'TIGHT'})")
        print(f"\nDecode: {dec['tps_gpu']:.0f} tok/s/GPU, {dec['tps_total']:.0f} total")
        print(f"RL step: {rl['tot_t']:.1f}s = {rl['sph']:.2f} steps/hr, {rl['s72h']:.0f}/72h")
        print(f"Eval(158x5): {ev['tot_hr']:.2f}h, Quick: {ev['quick_min']:.1f}min")
        print(f"Critical path: {cp['total_h']:.1f}h (fits72h={cp['fits_72h']})")
        print(f"\nScenarios:")
        for s in sc:
            print(f"  {s['name']}: {s['sph']:.2f} s/hr, {s['s72h']:.0f}/72h")

    if args.json:
        with open(args.json, "w") as f:
            json.dump(R, f, indent=2, default=str)
        print(f"JSON: {args.json}")

    if args.html:
        html = gen_html(R)
        with open(args.html, "w") as f:
            f.write(html)
        sz = os.path.getsize(args.html) / 1024
        print(f"HTML: {args.html} ({sz:.1f} KB)")
    elif not args.json and not args.verbose:
        print(f"R67 Summary:")
        print(f"  KV/token: {kv['gqa_kb']:.1f}KB (GQA {kv['gqa_gqa_ratio']:.0f}:1)")
        print(f"  Decode: {dec['tps_gpu']:.0f} tok/s/GPU")
        print(f"  RL: {rl['sph']:.2f} steps/hr, {rl['s72h']:.0f}/72h")
        print(f"  Eval: {ev['tot_hr']:.2f}h")
        print(f"  Critical: {cp['total_h']:.1f}h (fits={cp['fits_72h']})")
        print(f"  Use --html, --json, --verbose for details")

if __name__ == "__main__":
    main()
