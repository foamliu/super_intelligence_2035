#!/usr/bin/env python3
"""Generate HTML report for CPU eval thread/batch scaling experiment."""
import json, sys, html
from datetime import datetime

def fmt_s(s):
    if s < 60: return f"{s:.0f}s"
    if s < 3600: return f"{s/60:.1f}min"
    return f"{s/3600:.1f}h"

def main():
    probe_path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/baize_probe_results.json"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "report.html"
    ckpt = sys.argv[3] if len(sys.argv) > 3 else "112000"
    data = json.load(open(probe_path))
    configs = sorted(data.get("configs", []), key=lambda c: (c["threads"], c["batch_size"]))
    if not configs:
        print("ERROR: no configs"); sys.exit(1)
    lim = configs[0].get("limit", 5)
    n_req = lim * 8
    full_req = 69650
    baseline = next((c for c in configs if c["threads"]==8 and c["batch_size"]==1), None)
    bw = baseline["wall_sec"] if baseline else 1
    best = min((c for c in configs if c.get("rc",0)==0), key=lambda c: c["wall_sec"], default=None)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    rows_thr = ""; rows_bat = ""; rows_heat = ""; rows_score = ""
    for c in configs:
        t, b, w = c["threads"], c["batch_size"], c["wall_sec"]
        sp = bw/w if w>0 else 0; rps = n_req/w if w>0 else 0; fe = w*full_req/n_req if n_req>0 else 0
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
    sp_b = bw/w_b if w_b>0 else 0; fe_base = bw*full_req/n_req if n_req>0 else 0; fe_best = w_b*full_req/n_req if n_req>0 else 0
    css = 'body{font-family:-apple-system,"Microsoft YaHei",sans-serif;margin:20px;background:#f5f5f5;color:#333}h1{color:#1a1a2e;border-bottom:3px solid #16213e;padding-bottom:10px}h2{color:#16213e;margin-top:30px}table{border-collapse:collapse;margin:15px 0;width:100%}th,td{border:1px solid #ddd;padding:8px 12px;text-align:center}th{background:#16213e;color:white}tr:nth-child(even){background:#f9f9f9}.metric{font-weight:bold}.good{color:#2e7d32}.warn{color:#f57f17}.bad{color:#c62828}.card{background:white;border-radius:8px;padding:20px;margin:15px 0;box-shadow:0 2px 4px rgba(0,0,0,0.1)}.bar{display:inline-block;height:20px;background:#1976d2;border-radius:3px}.bar-container{display:inline-block;width:200px;background:#e0e0e0;border-radius:3px;height:20px}.summary-box{background:#e3f2fd;border-left:4px solid #1976d2;padding:15px;margin:15px 0}'
    h = f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>BaiZe 2B CPU 评测线程/Batch 扩展报告</title><style>{css}</style></head><body>
<h1>BaiZe 2B CPU 评测线程/Batch 扩展实验报告</h1>
<p><small>检查点: iter_{ckpt} · 生成时间: {ts} · 探测: {lim}/任务 × 2任务</small></p>
<div class="summary-box"><h3>核心发现</h3>
<p><strong>基线</strong>(8线程,bs=1): {fmt_s(bw)} / {n_req}请求</p>
<p><strong>最优</strong>: {t_b}线程,bs={b_b} → {fmt_s(w_b)} · 加速 <strong>{sp_b:.2f}x</strong></p>
<p><strong>全量8集预估</strong>: 基线<span class="{'bad' if fe_base>86400 else 'warn'}">{fmt_s(fe_base)}</span> · 最优<span class="{'good' if fe_best<86400 else 'warn'}">{fmt_s(fe_best)}</span></p>
<p><strong>架构</strong>: Mamba2-hybrid 2.22B · CPU用PyTorch参考实现(无CUDA内核)</p></div>
<h2>① 线程数 vs 吞吐/时长 (bs=1)</h2><div class="card"><table><tr><th>线程</th><th>Wall-clock</th><th>加速比</th><th>请求/秒</th><th>全量预估</th><th>相对加速</th></tr>{rows_thr}</table></div>
<h2>② Batch_size vs 吞吐 (8线程)</h2><div class="card"><table><tr><th>batch</th><th>Wall-clock</th><th>加速比</th><th>请求/秒</th><th>全量预估</th></tr>{rows_bat}</table></div>
<h2>③ 线程×Batch 二维热点表</h2><div class="card"><table>{rows_heat}</table></div>
<h2>④ 分数一致性检查</h2><div class="card"><table>{rows_score}</table><p><small>探测limit={lim}，样本量极小，分数波动正常。完整8集分数需全量评测。</small></p></div>
<h2>⑤ 内存与安全边界</h2><div class="card"><table><tr><th>配置</th><th>权重</th><th>内存峰值</th><th>评估</th></tr><tr><td>2B bf16</td><td>~4.2GB</td><td>~4.2GB</td><td>远低于2TB</td></tr><tr><td>bs=8,80线程</td><td>~4.2GB</td><td>~8-12GB</td><td>安全(1214GB可用)</td></tr></table></div>
<h2>⑥ 实验方法</h2><div class="card"><ul><li>检查点: iter_{ckpt} (NeMo→HF, 2.22B/323tensors)</li><li>探测: openbookqa+arc_challenge, limit={lim}</li><li>线程: 8,16,32,80 · Batch: 1,4,8</li><li>约束: 纯CPU,nice19,OMP≤80</li></ul></div>
<hr><p><small>BaiZe Pretrain · CPU Eval Scaling · iter_{ckpt} · {ts}</small></p></body></html>'''
    with open(out_path, "w") as f: f.write(h)
    print(f"Report: {out_path} ({len(h)} bytes)")

if __name__ == "__main__": main()
