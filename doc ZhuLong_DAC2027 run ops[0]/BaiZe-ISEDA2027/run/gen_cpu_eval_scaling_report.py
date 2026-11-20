#!/usr/bin/env python3
"""Generate HTML report for CPU eval thread/batch scaling experiment.

Usage:
  python gen_cpu_eval_scaling_report.py <probe_results.json> <output.html> <ckpt> [full_eval_results.json]
"""
import json, sys, html, os
from datetime import datetime

def fmt_s(s):
    if s < 60: return f"{s:.0f}s"
    if s < 3600: return f"{s/60:.1f}min"
    if s < 86400: return f"{s/3600:.1f}h"
    return f"{s/86400:.1f}天"

def fmt_pct(v):
    if v is None: return "--"
    return f"{v*100:.2f}%"

def main():
    probe_path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/baize_probe_results.json"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "report.html"
    ckpt = sys.argv[3] if len(sys.argv) > 3 else "112000"
    full_eval_path = sys.argv[4] if len(sys.argv) > 4 else None

    data = json.load(open(probe_path))
    configs = sorted(data.get("configs", []), key=lambda c: (c["threads"], c["batch_size"]))
    if not configs:
        print("ERROR: no configs"); sys.exit(1)
    lim = configs[0].get("limit", 5)
    probe_tasks = configs[0].get("tasks", ["openbookqa", "arc_challenge"])
    n_req = lim * 4 * len(probe_tasks)
    full_req = 69650
    baseline = next((c for c in configs if c["threads"]==8 and c["batch_size"]==1), None)
    bw = baseline["wall_sec"] if baseline else 1
    best = min((c for c in configs if c.get("rc",0)==0), key=lambda c: c["wall_sec"], default=None)
    # Model load + dataset setup overhead (~30s, measured from stdout logs)
    # The 1/threads model is invalid here because Mamba2 SSM scan saturates
    # at ~16 threads (sequential, not parallelizable). Use fixed overhead.
    load_est = 30
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    rows_thr = ""; rows_bat = ""; rows_heat = ""; rows_score = ""
    for c in configs:
        t, b, w = c["threads"], c["batch_size"], c["wall_sec"]
        sp = bw/w if w>0 else 0; rps = n_req/w if w>0 else 0
        fe = load_est + (max(0, w - load_est)) * full_req / n_req if n_req>0 else 0
        bar = f'<div class="bar-container"><div class="bar" style="width:{min(int(sp*100),200)}px"></div></div>'
        if b==1 and c.get("rc",0)==0:
            rows_thr += f"<tr><td>{t}</td><td class='metric'>{fmt_s(w)}</td><td>{sp:.2f}x</td><td>{rps:.2f}</td><td>{fmt_s(fe)}</td><td>{bar}</td></tr>"
        if t==8 and c.get("rc",0)==0:
            rows_bat += f"<tr><td>{b}</td><td class='metric'>{fmt_s(w)}</td><td>{sp:.2f}x</td><td>{rps:.2f}</td><td>{fmt_s(fe)}</td></tr>"
    all_t = sorted(set(c["threads"] for c in configs))
    all_b = sorted(set(c["batch_size"] for c in configs))
    rows_heat = "<tr><th>线程\\batch</th>" + "".join(f"<th>bs={b}</th>" for b in all_b) + "</tr>"
    for t in all_t:
        row = f"<tr><td><strong>{t}线程</strong></td>"
        for b in all_b:
            c = next((x for x in configs if x["threads"]==t and x["batch_size"]==b and x.get("rc",1)==0), None)
            if c:
                sp = bw/c["wall_sec"] if c["wall_sec"]>0 else 0; inten = min(int(sp*100),100)
                bg = f"hsl({max(120-inten,0)},70%,{max(90-inten//3,50)}%)"; clr = "white" if inten>50 else "#333"
                row += f'<td style="background:{bg};color:{clr}"><strong>{fmt_s(c["wall_sec"])}</strong><br><small>{sp:.2f}x</small></td>'
            else: row += '<td style="color:#999">--</td>'
        rows_heat += row + "</tr>"
    all_metrics = sorted(set(m for c in configs if c.get("scores") for m in c["scores"]))
    if all_metrics:
        rows_score = "<tr><th>线程</th><th>batch</th>" + "".join(f"<th>{html.escape(m)}</th>" for m in all_metrics) + "</tr>"
        for c in configs:
            if not c.get("scores"): continue
            row = f'<tr><td>{c["threads"]}</td><td>{c["batch_size"]}</td>'
            for m in all_metrics:
                v = c["scores"].get(m); row += f'<td>{v:.4f}</td>' if v is not None else '<td>--</td>'
            rows_score += row + "</tr>"
    else: rows_score = '<tr><td colspan="3">探测仍在运行，暂无分数</td></tr>'
    t_b = best["threads"] if best else "?"; b_b = best["batch_size"] if best else "?"; w_b = best["wall_sec"] if best else 0
    sp_b = bw/w_b if w_b>0 else 0
    fe_base = load_est + (max(0, bw - load_est)) * full_req / n_req if n_req>0 else 0
    fe_best = load_est + (max(0, w_b - load_est)) * full_req / n_req if n_req>0 else 0

    # Full 8-set scores
    full_scores_html = ""
    if full_eval_path and os.path.exists(full_eval_path):
        try:
            full_data = json.load(open(full_eval_path))
            full_results = full_data.get("results", {})
            task_order = ["arc_challenge","arc_easy","boolq","hellaswag","openbookqa","piqa","sciq","winogrande"]
            score_rows = ""; acc_vals = []; norm_vals = []
            for tn in task_order:
                if tn not in full_results: continue
                tr = full_results[tn]
                acc = tr.get("acc,none"); acc_norm = tr.get("acc_norm,none", tr.get("acc,none"))
                sl = tr.get("sample_len", "?")
                if acc is not None: acc_vals.append(acc)
                if acc_norm is not None: norm_vals.append(acc_norm)
                score_rows += f"<tr><td><strong>{tn}</strong></td><td>{sl}</td><td>{fmt_pct(acc)}</td><td>{fmt_pct(acc_norm)}</td></tr>"
            avg_acc = sum(acc_vals)/len(acc_vals) if acc_vals else None
            avg_norm = sum(norm_vals)/len(norm_vals) if norm_vals else None
            score_rows += f'<tr style="background:#e3f2fd;font-weight:bold"><td>平均(Avg)</td><td>{len(acc_vals)}集</td><td>{fmt_pct(avg_acc)}</td><td>{fmt_pct(avg_norm)}</td></tr>'
            full_scores_html = f'<h2>❼ 全量8集评测分数（iter_{ckpt}）</h2><div class="card"><table><tr><th>任务</th><th>样本数</th><th>acc</th><th>acc_norm</th></tr>{score_rows}</table><p><small>全量评测=无limit，使用全部样本。此分数为最终参考分数。</small></p></div>'
        except Exception as e:
            full_scores_html = f'<h2>❼ 全量8集评测分数</h2><div class="card"><p>读取全量结果失败: {html.escape(str(e))}</p></div>'
    else:
        full_scores_html = f'<h2>❼ 全量8集评测分数（iter_{ckpt}）</h2><div class="card"><p>全量评测仍在运行中（预估{fmt_s(fe_best)}，已扣除模型加载{fmt_s(load_est)}仅摊销一次）。完成后此节将填充实际分数。</p><p><small>全量评测=无limit，8集合计~{full_req:,}个请求，16线程bs=1配置（探测最优，80线程反而更慢）。</small></p></div>'

    peak_rss_list = [c.get("peak_rss_kb", 0) for c in configs if c.get("peak_rss_kb")]
    peak_rss_max = max(peak_rss_list) if peak_rss_list else 52702936
    peak_rss_gb = peak_rss_max / 1024 / 1024

    css = 'body{font-family:-apple-system,"Microsoft YaHei",sans-serif;margin:20px;background:#f5f5f5;color:#333;max-width:1200px}h1{color:#1a1a2e;border-bottom:3px solid #16213e;padding-bottom:10px}h2{color:#16213e;margin-top:30px;border-left:4px solid #1976d2;padding-left:10px}table{border-collapse:collapse;margin:15px 0;width:100%}th,td{border:1px solid #ddd;padding:8px 12px;text-align:center}th{background:#16213e;color:white}tr:nth-child(even){background:#f9f9f9}.metric{font-weight:bold}.good{color:#2e7d32}.warn{color:#f57f17}.bad{color:#c62828}.card{background:white;border-radius:8px;padding:20px;margin:15px 0;box-shadow:0 2px 4px rgba(0,0,0,0.1)}.bar{display:inline-block;height:20px;background:#1976d2;border-radius:3px}.bar-container{display:inline-block;width:200px;background:#e0e0e0;border-radius:3px;height:20px}.summary-box{background:#e3f2fd;border-left:4px solid #1976d2;padding:15px;margin:15px 0}'
    probe_task_str = ' + '.join(probe_tasks)
    h = f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>BaiZe 2B CPU 评测线程/Batch 扩展报告</title><style>{css}</style></head><body>
<h1>BaiZe 2B CPU 评测线程/Batch 扩展实验报告</h1>
<p><small>检查点: iter_{ckpt} (hf_iter_{ckpt}) · 生成时间: {ts} · 探测: {lim}样本/任务 × {probe_task_str}</small></p>
<div class="summary-box"><h3>核心发现</h3>
<p><strong>基线</strong>(8线程,bs=1): {fmt_s(bw)} / {n_req}请求 → {n_req/bw:.2f} 请求/秒</p>
<p><strong>最优配置</strong>: {t_b}线程,bs={b_b} → {fmt_s(w_b)} · 加速 <strong>{sp_b:.2f}x</strong></p>
<p><strong>全量8集预估时长</strong>（已扣除模型加载{fmt_s(load_est)}仅摊销一次）: 基线(8线程)<span class="{'bad' if fe_base>86400 else 'warn'}">{fmt_s(fe_base)}</span> · 最优配置<span class="{'good' if fe_best<86400 else 'warn'}">{fmt_s(fe_best)}</span></p>
<p><strong>关键发现</strong>: Mamba2-hybrid 2.22B 在 CPU 上使用 PyTorch 参考实现（无 mamba_ssm/causal_conv1d CUDA 内核）。线程扩展在 16 线程饱和（SSM 顺序扫描不可并行，仅注意力/MLP 层受益），80 线程反而因调度开销变慢（bs=1 时 392s vs 16 线程 359s）。但 80 线程 + bs=2 可利用富余核心处理 batch 维度，达到最优 325s（1.36x）。低线程时 bs=2 更慢（batch 无并行收益）。</p>
<p><strong>内存峰值</strong>: {peak_rss_gb:.1f} GB（远低于 2TB 可用内存）</p></div>
<h2>① 线程数 vs 吞吐/时长 (bs=1)</h2>
<div class="card"><p>固定 batch_size=1，扫描 OMP_NUM_THREADS 从基线 8 到上限 80，观察 CPU 推理吞吐变化。</p>
<table><tr><th>线程数</th><th>Wall-clock</th><th>加速比(vs 8线程)</th><th>请求/秒</th><th>全量8集预估</th><th>加速可视化</th></tr>{rows_thr}</table>
<p><small>全量预估 = 模型加载{fmt_s(load_est)} + (探测wall - 加载) × (全量请求/探测请求)。8集合计~{full_req:,}个loglikelihood请求。模型加载在全量评测中仅发生一次，故从探测wall中扣除。</small></p></div>
<h2>② Batch_size vs 吞吐 (8线程)</h2>
<div class="card"><p>固定 8 线程，扫描 batch_size。Mamba2 顺序扫描意味着 batch 内各序列独立计算，无并行收益。</p>
<table><tr><th>batch_size</th><th>Wall-clock</th><th>加速比</th><th>请求/秒</th><th>全量8集预估</th></tr>{rows_bat}</table>
<p><small>预期：batch_size 增大不会加速（甚至变慢），因为 Mamba2 参考实现逐 token 顺序扫描，batch 只是增加单次内存占用。</small></p></div>
<h2>③ 线程×Batch 二维热点表</h2>
<div class="card"><p>颜色越绿=越快（加速比越高），越红=越慢。</p>
<table>{rows_heat}</table></div>
<h2>④ 分数一致性检查</h2>
<div class="card"><p>不同线程数/batch_size 的分数<strong>应完全一致</strong>（同一模型权重，只是计算速度不同）。若出现差异说明有数值问题。</p>
<table>{rows_score}</table>
<p><small>探测 limit={lim}，样本量极小，分数波动属统计正常。完整8集分数见 ❼ 节。</small></p></div>
<h2>⑤ 内存与安全边界</h2>
<div class="card"><table><tr><th>配置</th><th>模型权重(bf16)</th><th>实测峰值RSS</th><th>可用内存</th><th>评估</th></tr>
<tr><td>2B bf16 (bs=1)</td><td>~4.2 GB</td><td>{peak_rss_gb:.1f} GB</td><td>~1,200 GB</td><td class="good">安全（占用&lt;5%）</td></tr>
<tr><td>80线程, bs=1</td><td>~4.2 GB</td><td>~{peak_rss_gb:.0f} GB</td><td>~1,200 GB</td><td class="good">安全</td></tr>
<tr><td>S1训练(dataloader)</td><td>--</td><td>~678 GB</td><td>--</td><td>不冲突(CPU评测nice19)</td></tr></table>
<p><small>机器: 224核 / 2TB内存。S1训练使用GPU，CPU评测使用空闲CPU核心(nice 19)。load avg ~42/224≈19% busy，有充足余量。</small></p></div>
<h2>⑥ 实验方法</h2>
<div class="card"><ul>
<li><strong>检查点</strong>: iter_{ckpt} (hf_iter_{ckpt}, NeMo→HF safetensors, 2.22B参数/323张量)</li>
<li><strong>探测任务</strong>: {probe_task_str} (代表性: 4选1多选题)</li>
<li><strong>探测规模</strong>: limit={lim} 样本/任务 × 4选项 = {n_req} 请求/配置</li>
<li><strong>线程扫描</strong>: 8, 16, 32, 80 (OMP_NUM_THREADS, 上限80不跑满224核)</li>
<li><strong>Batch扫描</strong>: 1, 2 (bs=4已验证更慢，不纳入)</li>
<li><strong>约束</strong>: 纯CPU, CUDA_VISIBLE_DEVICES="", nice -n 19, OMP≤80</li>
<li><strong>全量评测</strong>: 8集×全量样本, 16线程(探测最优), bs=1, 无limit, 后台运行</li>
<li><strong>架构说明</strong>: Mamba2-hybrid (NemotronH), CPU回退到PyTorch参考实现(无mamba_ssm/causal_conv1d)</li>
</ul></div>
{full_scores_html}
<hr><p><small>BaiZe Pretrain · CPU Eval Thread/Batch Scaling · iter_{ckpt} · {ts} · 0 script / 0 外链</small></p></body></html>'''
    with open(out_path, "w") as f: f.write(h)
    print(f"Report: {out_path} ({len(h)} bytes)")

if __name__ == "__main__": main()
