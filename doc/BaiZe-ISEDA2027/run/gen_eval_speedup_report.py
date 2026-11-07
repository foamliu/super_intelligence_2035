#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_eval_speedup_report.py — 生成 CPU eval 提速报告 (中文 HTML)

用法: python3 gen_eval_speedup_report.py
产出: doc/BaiZe-ISEDA2027/reports/report_pretrain_cpu_eval_speedup_zh.html
"""
import json, os, sys, time, html, math

REPORT_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports"
OUTPUT = os.path.join(REPORT_DIR, "report_pretrain_cpu_eval_speedup_zh.html")

TASKS = ["arc_challenge","arc_easy","boolq","hellaswag","openbookqa","piqa","sciq","winogrande"]
TASK_DOCS = {"arc_challenge":1172,"arc_easy":2376,"boolq":3270,"hellaswag":10042,"openbookqa":500,"piqa":1838,"sciq":1000,"winogrande":1267}

THREAD_SCALING = [
    ("8线程 bs1", 8, 1, 443, "基线"),
    ("16线程 bs1", 16, 1, 359, "1.23x 饱和点"),
    ("32线程 bs1", 32, 1, 364, "无提升"),
    ("80线程 bs1", 80, 1, 392, "反而更慢"),
    ("80线程 bs2", 80, 2, 325, "1.36x 最优"),
]

PRECISION_10K = [
    ("arc_challenge", 0.29, 0.27, 0.26, 0.26),
    ("arc_easy",      0.49, 0.49, 0.47, 0.47),
    ("boolq",         0.61, 0.62, None, None),
    ("hellaswag",     0.36, 0.35, 0.45, 0.45),
    ("openbookqa",    0.20, 0.21, 0.35, 0.35),
    ("piqa",          0.72, 0.72, 0.73, 0.73),
    ("sciq",          0.79, 0.79, 0.71, 0.70),
    ("winogrande",    0.54, 0.54, None, None),
]

def esc(s):
    return html.escape(str(s))

def gen():
    os.makedirs(REPORT_DIR, exist_ok=True)
    p = []
    p.append("<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'>")
    p.append("<meta name='viewport' content='width=device-width,initial-scale=1'>")
    p.append("<title>BaiZe 2B CPU 评测提速报告</title>")
    p.append("<style>")
    p.append("body{font-family:system-ui,sans-serif;max-width:960px;margin:0 auto;padding:20px;line-height:1.6;color:#333}")
    p.append("h1{color:#1a5276;border-bottom:3px solid #1a5276;padding-bottom:10px}")
    p.append("h2{color:#2874a6;margin-top:30px;border-left:4px solid #2874a6;padding-left:10px}")
    p.append("table{border-collapse:collapse;width:100%;margin:15px 0;font-size:14px}")
    p.append("th,td{border:1px solid #ddd;padding:8px 12px;text-align:center}")
    p.append("th{background:#eaf2f8;font-weight:600}")
    p.append("tr:nth-child(even){background:#f8f9fa}")
    p.append(".good{color:#27ae60;font-weight:600}")
    p.append(".bad{color:#e74c3c;font-weight:600}")
    p.append(".key{background:#e8f8f5;border-left:4px solid #1abc9c;padding:10px 15px;margin:15px 0}")
    p.append(".note{background:#fef9e7;border-left:4px solid #f39c12;padding:10px 15px;margin:15px 0}")
    p.append(".summary{background:#eaf2f8;border-radius:8px;padding:15px 20px;margin:20px 0}")
    p.append("code{background:#f4f6f7;padding:2px 6px;border-radius:3px}")
    p.append("</style></head><body>")
    p.append("<h1>BaiZe 2B CPU 评测提速报告</h1>")
    p.append(f"<p style='color:#7f8c8d'>生成时间：{time.strftime('%Y-%m-%d %H:%M')}</p>")
    return p

def body_sections():
    p = []
    # 一、背景
    p.append("<h2>一、背景与问题</h2>")
    p.append("<p>用户提问：「pretrain 全量 eval 需要时间这么久吗？已经使用 llama.cpp 了吗？线程并发多一点有帮助吗」</p>")
    p.append("<p><b>现状</b>：iter_112000 的 8 集全量评测（21,465 题 / 73,106 次 loglikelihood 请求）")
    p.append("在 HF float32 单进程 16 线程下预估需要 <b>22.5 天</b>。</p>")
    p.append("<div class='key'><b>核心发现</b>：<br>")
    p.append("1. <b>线程已饱和</b>：Mamba2-hybrid 的 SSM 顺序扫描不可并行，16 线程已达瓶颈<br>")
    p.append("2. <b>llama.cpp 后端可用</b>：_fixed_ GGUF 转换器精度回归通过（Δacc ≤ 0.02）<br>")
    p.append("3. <b>任务级并行</b>：8 个任务拆成多进程，零技术风险<br>")
    p.append("4. <b>综合提速</b>：llama.cpp + 多服务器 → 预估 22.5 天 → ~5-20 小时</div>")

    # 二、线程饱和
    p.append("<h2>二、线程饱和分析（#1570 探测矩阵）</h2>")
    p.append("<table><tr><th>配置</th><th>线程</th><th>Batch</th><th>耗时(s)</th><th>加速</th><th>备注</th></tr>")
    bl = 443
    for name, t, b, sec, note in THREAD_SCALING:
        sp = bl / sec
        cls = "good" if sp > 1.2 else ("bad" if sp < 0.95 else "")
        p.append(f"<tr><td>{esc(name)}</td><td>{t}</td><td>{b}</td><td>{sec}</td><td class='{cls}'>{sp:.2f}x</td><td>{esc(note)}</td></tr>")
    p.append("</table>")
    p.append("<div class='note'><b>根因</b>：BaiZe 2B 使用 Mamba2-hybrid 架构，SSM 层的顺序扫描本质上不可并行。")
    p.append("增加线程只能加速 Attention 层，SSM 层成为瓶颈后继续加线程无益。</div>")

    # 三、精度回归
    p.append("<h2>三、llama.cpp 精度回归验证</h2>")
    p.append("<p>iter_10000 检查点，<code>_fixed_</code> GGUF 转换器 vs HF float32（limit=100）：</p>")
    p.append("<table><tr><th>任务</th><th>HF acc</th><th>GGUF acc</th><th>Δacc</th><th>HF norm</th><th>GGUF norm</th><th>Δnorm</th></tr>")
    mx = 0
    for task, ha, ga, hn, gn in PRECISION_10K:
        da = ha - ga
        mx = max(mx, abs(da))
        cls = "good" if abs(da) <= 0.02 else "bad"
        hns = f"{hn:.2f}" if hn is not None else "N/A"
        gns = f"{gn:.2f}" if gn is not None else "N/A"
        dn = f"{hn-gn:+.2f}" if hn is not None and gn is not None else "N/A"
        p.append(f"<tr><td>{esc(task)}</td><td>{ha:.2f}</td><td>{ga:.2f}</td><td class='{cls}'>{da:+.2f}</td><td>{hns}</td><td>{gns}</td><td>{dn}</td></tr>")
    p.append("</table>")
    vc = "good" if mx <= 0.03 else "bad"
    p.append(f"<div class='key'><b>精度判定</b>：最大 Δacc = {mx:.2f}（n=100, stderr≈0.045）→ <span class='{vc}'>PASS</span></div>")

    # 三b、GGUF 跨 checkpoint 一致性（converter 验证）
    p.append("<h2>三b、GGUF 跨 checkpoint 一致性验证</h2>")
    p.append("<p>同一 <code>_fixed_</code> 转换器在 10 个 checkpoint（10k–100k）上均产出有效结果，")
    p.append("无 NaN，分数随训练单调上升 → 转换器对所有同架构 ckpt 一致。</p>")
    p.append("<table><tr><th>checkpoint</th><th>arc_chal</th><th>arc_easy</th><th>boolq</th><th>hellaswag</th><th>openbookqa</th><th>piqa</th><th>sciq</th><th>winogrande</th><th>raw Avg</th></tr>")
    gguf_trend = [
        ("iter_10k",  0.27, 0.49, 0.62, 0.35, 0.21, 0.72, 0.79, 0.54),
        ("iter_100k", 0.30, 0.57, 0.67, 0.41, 0.21, 0.74, 0.88, 0.60),
    ]
    for row in gguf_trend:
        vals = row[1:]
        avg = sum(vals) / len(vals)
        p.append(f"<tr><td><b>{row[0]}</b></td>" + "".join(f"<td>{v:.2f}</td>" for v in vals) + f"<td><b>{avg:.4f}</b></td></tr>")
    p.append("</table>")
    p.append("<div class='note'><b>iter_112000 精度回归</b>：正在运行中（GGUF --limit 100, llama-server 64 线程）。")
    p.append("预计 ~20 分钟内完成。完成后将与上述趋势比对 + 检查 NaN。</div>")

    # 四、提速方案
    p.append("<h2>四、提速方案</h2>")
    p.append("<h3>方案 A：llama.cpp 后端</h3>")
    p.append("<p>llama-server 加载 f16 GGUF，HTTP /completion 提供 loglikelihood 打分。</p>")
    p.append("<ul><li>转换：323 tensors, 4.2GB f16 GGUF</li>")
    p.append("<li>服务：<code>llama-server --parallel 8 -t 64 --cache-prompt</code></li>")
    p.append("<li>吞吐：~1 it/s（8 并发 slot, 64 线程）</li>")
    p.append("<li>预估全量：73,106 / 1.0 ≈ 20 小时</li></ul>")
    p.append("<h3>方案 B：HF 任务级多进程并行（零风险备选）</h3>")
    p.append("<p>8 任务拆成 11 进程（hellaswag 4 片 + 7 任务），每进程 16 线程 = 176 核。</p>")
    p.append("<p>预估总耗时：木桶效应 → hellaswag 最慢 ≈ 2.1 天</p>")
    p.append("<h3>方案 C：llama.cpp 多服务器实例（推荐）</h3>")
    p.append("<p>多个 llama-server 实例（不同端口），每个处理不同任务子集。</p>")
    p.append("<table><tr><th>配置</th><th>服务器数</th><th>每服务器线程</th><th>总并发</th><th>预估耗时</th></tr>")
    p.append("<tr><td>1 server</td><td>1</td><td>64</td><td>8</td><td>~20h</td></tr>")
    p.append("<tr><td>4 servers</td><td>4</td><td>56</td><td>32</td><td>~5h</td></tr>")
    p.append("</table>")

    # 五、提速对照表
    p.append("<h2>五、提速对照表</h2>")
    p.append("<table><tr><th>方案</th><th>加速</th><th>22.5 天 →</th><th>风险</th><th>精度</th></tr>")
    p.append("<tr><td>现状 HF 单进程 16 线程</td><td>1x</td><td>22.5 天</td><td>-</td><td>基线</td></tr>")
    p.append("<tr><td>HF 任务级 11 进程</td><td>~11x</td><td class='good'>~2.1 天</td><td class='good'>零</td><td>一致</td></tr>")
    p.append("<tr><td>llama.cpp 1 服务器</td><td>~26x</td><td class='good'>~20h</td><td>低</td><td class='good'>Δ≤0.02</td></tr>")
    p.append("<tr><td>llama.cpp 4 服务器</td><td>~100x</td><td class='good'>~5h</td><td>低</td><td class='good'>Δ≤0.02</td></tr>")
    p.append("</table>")

    # 六、交付物
    p.append("<h2>六、交付物清单</h2>")
    p.append("<ul>")
    p.append("<li><code>cpu_lmeval_run.py</code> — 新增 --samples 支持文档分片</li>")
    p.append("<li><code>baize_cpu_lmeval.sh</code> — 新增 --samples 透传</li>")
    p.append("<li><code>baize_cpu_lmeval_parallel.sh</code> — 11 进程并行编排</li>")
    p.append("<li><code>merge_parallel_results.py</code> — 分片结果合并</li>")
    p.append("<li><code>gen_eval_speedup_report.py</code> — 本报告生成器</li>")
    p.append("<li>GGUF 模型：bz2b-112000-f16.gguf（4.2GB, 323 tensors）</li>")
    p.append("</ul>")

    # 七、结论
    p.append("<h2>七、结论</h2>")
    p.append("<div class='summary'>")
    p.append("<p><b>回答用户三个问题</b>：</p>")
    p.append("<p><b>1.「需要时间这么久吗？」</b><br>")
    p.append("不需要。通过 llama.cpp + 多服务器并行，22.5 天 → <b>5-20 小时</b>。</p>")
    p.append("<p><b>2.「已经使用 llama.cpp 了吗？」</b><br>")
    p.append("已切回。GGUF 转换成功（4.2GB f16），iter_10000 精度回归通过（Δacc ≤ 0.02）。")
    p.append("iter_112000 精度回归运行中（~41%），通过后将启动全量 GGUF eval（4 服务器并行，预估 ~5h）。</p>")
    p.append("<p><b>3.「线程并发多一点有帮助吗？」</b><br>")
    p.append("单进程内加线程<b>没有帮助</b>（16 线程已饱和，SSM 不可并行）。")
    p.append("但<b>多进程/多服务器并行</b>有帮助——每个独立进程有自己的 SSM 扫描序列。</p>")
    p.append("</div>")
    p.append("</body></html>")
    return p

if __name__ == "__main__":
    parts = gen() + body_sections()
    with open(OUTPUT, "w") as f:
        f.write("\n".join(parts))
    print(f"Report: {OUTPUT} ({os.path.getsize(OUTPUT)} bytes)")
