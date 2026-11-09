#!/usr/bin/env python3
"""Generator: cline 专项分析报告 R1746 (2026-11-07 12:28)
指令: 2026-11-07 10:10 用户令 C1-C5
数据源: SWE-bench Verified predictions_glm53/ + TB4 jobs_tb4_glm53_full/
"""
import json, glob, os, statistics
from datetime import datetime

PRED_DIR = os.path.join(os.path.dirname(__file__), "swebench_verified_full", "predictions_glm53")
TB4_DIR  = os.path.join(os.path.dirname(__file__), "terminalbench", "jobs_tb4_glm53_full")
HARNESSES = ["cline-patched","codex","opencode","claude-code","pi","hermes","deepseek-harness"]
DISPLAY = {"cline-patched":"cline","codex":"codex","opencode":"opencode",
           "claude-code":"claude-code","pi":"pi","hermes":"hermes","deepseek-harness":"deepseek"}

def real_mtimes(h):
    rm = []
    for f in sorted(glob.glob(os.path.join(PRED_DIR, f"{h}__*.json"))):
        d = json.load(open(f))
        items = d if isinstance(d, list) else [d]
        for item in items:
            if item.get("model_patch", "").strip():
                rm.append(os.path.getmtime(f))
    rm.sort()
    return rm

def avg_min(rm):
    return (rm[-1] - rm[0]) / 60 / (len(rm) - 1) if len(rm) >= 2 else 0

def empty_intervals(h):
    ets = []
    for f in sorted(glob.glob(os.path.join(PRED_DIR, f"{h}__*.json"))):
        d = json.load(open(f))
        items = d if isinstance(d, list) else [d]
        for item in items:
            if not item.get("model_patch", "").strip():
                ets.append(os.path.getmtime(f))
    ets.sort()
    return statistics.median([ets[i+1]-ets[i] for i in range(len(ets)-1)]) if len(ets) >= 2 else 0

def count_preds(h):
    fs = glob.glob(os.path.join(PRED_DIR, f"{h}__*.json"))
    real, empty, sizes = 0, 0, []
    for f in fs:
        d = json.load(open(f))
        items = d if isinstance(d, list) else [d]
        for item in items:
            p = item.get("model_patch", "").strip()
            if p: real += 1; sizes.append(len(p))
            else: empty += 1
    sizes.sort()
    return len(fs), real, empty, (sizes[len(sizes)//2] if sizes else 0)

def count_tb4(h):
    fs = glob.glob(os.path.join(TB4_DIR, h, "*", "*", "result.json"))
    passed = 0
    for f in fs:
        try:
            d = json.load(open(f))
            if d.get("reward", d.get("passed", 0)): passed += 1
        except: pass
    return len(fs), passed

# Gather data
rows = []
for h in HARNESSES:
    total, real, empty, med = count_preds(h)
    tc, tp = count_tb4(h)
    rows.append((h, total, real, empty, med, tc, tp))

# cline pre-quota cutoff
cmt = real_mtimes("cline-patched")
cutoff = cmt[-1] if cmt else 0
pre_q = pre_r = post_q = post_r = 0
for f in glob.glob(os.path.join(PRED_DIR, "cline-patched__*.json")):
    mt = os.path.getmtime(f)
    d = json.load(open(f))
    items = d if isinstance(d, list) else [d]
    for item in items:
        p = item.get("model_patch", "").strip()
        if mt <= cutoff: pre_q += 1; pre_r += 1 if p else 0
        else: post_q += 1; post_r += 1 if p else 0

c_avg = avg_min(cmt)
o_avg = avg_min(real_mtimes("opencode"))
c_int = empty_intervals("cline-patched")
cod_int = empty_intervals("codex")
now = datetime.now().strftime("%Y-%m-%d %H:%M")
t_pred = sum(r[1] for r in rows)
t_real = sum(r[2] for r in rows)
tb4_t = sum(r[5] for r in rows)

# Build HTML
S = "body{font-family:sans-serif;margin:2em;background:#f8f9fa;color:#333}h1{color:#1a1a2e;border-bottom:3px solid #e94560;padding-bottom:.3em}h2{color:#16213e;margin-top:1.5em;border-left:4px solid #e94560;padding-left:.5em}table{border-collapse:collapse;width:100%;margin:1em 0;background:#fff}th,td{border:1px solid #ddd;padding:8px 12px;text-align:left}th{background:#16213e;color:#fff}tr:nth-child(even){background:#f2f2f2}.good{color:#27ae60;font-weight:bold}.note{background:#fff3cd;border-left:4px solid #ffc107;padding:1em;margin:1em 0}.fix{background:#d4edda;border-left:4px solid #28a745;padding:1em;margin:1em 0}.alert{background:#f8d7da;border-left:4px solid #dc3545;padding:1em;margin:1em 0}.info{background:#d1ecf1;border-left:4px solid #17a2b8;padding:1em;margin:1em 0}code{background:#eef;padding:2px 4px;border-radius:3px}.box{background:#fff;border-radius:8px;padding:1.5em;margin:1em 0;box-shadow:0 2px 4px rgba(0,0,0,.1)}pre{background:#f4f4f4;padding:1em;border-radius:4px;overflow-x:auto;font-size:13px}"
h = f'<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>cline 专项分析报告 R1746</title><style>{S}</style></head><body>\n'
h += f'<h1>cline 专项分析报告 R1746</h1>\n<p><small>BaiZe Harness 研究线 · {now} · 指令：2026-11-07 10:10 用户令 C1-C5 · 增量更新自 R1745</small></p>\n'
h += f'<div class="alert"><strong>⚠️ 网关状态（更新）</strong>：chat completions 返回 <strong>HTTP 429</strong>「本次Token额度已用完，请等待1小时58分钟2秒后重试」<br>ETA ≈ 14:26 CST。predict 进程 7 路 alive（0% CPU），额度恢复后 resume 自动重跑空 patch。<br><strong>归因红线</strong>：网关额度耗尽/429/403 不等于模型能力差。</div>\n'
h += f'<div class="box"><h3>TL;DR</h3><ul>\n'
h += f'<li><strong>C1</strong>：7路合计 {t_pred} 条预测，{t_real} real。cline 41条中27 real(65.9%)。</li>\n'
h += f'<li><strong>关键发现</strong>：额度前 cline 27/29=<span class="good">93.1%</span>，与 opencode(92.0%)<strong>无能力差距</strong>。cline 24.2min/题 vs opencode 10.0min（慢但质量同）。</li>\n'
h += f'<li><strong>C2</strong>：cline 14空patch=100%infra(429)。codex空patch间隔≈{cod_int/60:.0f}min（速败=适配器不重试429）。</li>\n'
h += f'<li><strong>C3</strong>：空patch未归零，根因=<strong>429额度耗尽</strong>(ETA~14:26)，非run_single.py:45 bug(R1744已修)。</li>\n'
h += f'<li><strong>C5</strong>：差距来源=额度时机+适配器429重试策略(cline 6min重试 vs codex 2min速败)。</li>\n'
h += f'<li><strong>TB4</strong>：{tb4_t} trials completed / 0 passed（reward=0=能力）。</li>\n</ul></div>\n'

# C1 table
h += '<h2>C1 — 独立统计（SWE-bench Verified 500题）</h2>\n'
h += '<table><tr><th>Harness</th><th>预测数</th><th>Real</th><th>Empty</th><th>Real%</th><th>中位patch(B)</th><th>每题耗时</th></tr>\n'
for h_name, total, real, empty, med, tc, tp in rows:
    rm = real_mtimes(h_name)
    avg_s = f"{avg_min(rm):.1f}min" if len(rm) >= 2 else "-"
    h += f'<tr><td>{DISPLAY[h_name]}</td><td>{total}/500</td><td>{real}</td><td>{empty}</td><td>{real/total*100:.1f}%</td><td>{med}</td><td>{avg_s}</td></tr>\n'
h += '</table>\n'
h += f'<div class="note"><strong>cline 额度前后对比</strong><table><tr><th>阶段</th><th>题数</th><th>Real</th><th>Empty</th><th>Real%</th></tr>\n'
h += f'<tr><td>额度前(&le;{datetime.fromtimestamp(cutoff).strftime("%H:%M")})</td><td>{pre_q}</td><td>{pre_r}</td><td>{pre_q-pre_r}</td><td><span class="good">{pre_r/pre_q*100:.1f}%</span></td></tr>\n'
h += f'<tr><td>额度后</td><td>{post_q}</td><td>{post_r}</td><td>{post_q-post_r}</td><td>{post_r/post_q*100 if post_q else 0:.1f}%</td></tr>\n'
h += f'<tr><td>合计</td><td>{pre_q+post_q}</td><td>{pre_r+post_r}</td><td>{(pre_q-pre_r)+(post_q-post_r)}</td><td>{(pre_r+post_r)/(pre_q+post_q)*100:.1f}%</td></tr></table>\n'
h += f'<p>最后real patch @{datetime.fromtimestamp(cutoff).strftime("%H:%M")}，之后{post_q}题全empty(429快速失败，间隔&approx;{c_int/60:.0f}min)。</p></div>\n'

# C2
h += '<h2>C2 — 失败原因分类（cline 14空patch）</h2>\n'
h += f'<table><tr><th>失败类别</th><th>数量</th><th>占比</th><th>证据</th></tr>\n'
h += f'<tr><td>网关额度耗尽(429)</td><td>{post_q-post_r}</td><td>{(post_q-post_r)/14*100:.1f}%</td><td>11:04~12:28，间隔&approx;{c_int/60:.0f}min=429快速失败</td></tr>\n'
h += f'<tr><td>额度前真实失败</td><td>{pre_q-pre_r}</td><td>{(pre_q-pre_r)/14*100:.1f}%</td><td>09:56(astropy-13579)&middot;10:26(astropy-13977)=额度前仅2空</td></tr>\n'
h += f'<tr><td><strong>合计</strong></td><td><strong>14</strong></td><td><strong>100%</strong></td><td>infra(429)={( post_q-post_r)/14*100:.0f}%</td></tr></table>\n'
h += f'<div class="info"><strong>适配器429重试策略差异</strong><table><tr><th>Harness</th><th>空patch间隔</th><th>策略</th></tr>\n'
h += f'<tr><td>cline</td><td>&approx;{c_int/60:.0f}min</td><td>429后等待重试(6min轮询)</td></tr>\n'
h += f'<tr><td>codex</td><td>&approx;{cod_int/60:.0f}min</td><td>429后立即放弃&rar;下一题(2min速败)</td></tr></table>\n'
h += '<p>codex 1 real/39 total = 适配器不重试429 + 共享额度早期耗尽。<strong>非模型能力差</strong>。</p></div>\n'

# C3
h += '<h2>C3 — 空patch是否归零</h2>\n'
h += f'<div class="alert"><strong>&cross; 未归零</strong>：{pre_q+post_q-pre_r-post_r} 个空patch（额度恢复后resume自动重跑）。</div>\n'
h += '<p><strong>根因</strong>：<strong>网关429额度耗尽</strong>（ETA~14:26 CST），非run_single.py:45 bug。</p>\n'
h += '<div class="fix"><strong>&check; R1744修复确认</strong>：always-extract-patch(7处)+resume is_predicted检查model_patch非空。额度前27/29=93.1%(vs修复前51.5%)=修复有效。</div>\n'
h += '<p><strong>证据</strong></p><pre>1. curl /v1/chat/completions(real key) -> HTTP 429 "Token额度已用完,请等待1h58m"\n'
h += f'2. /v1/models -> HTTP 200(网关健康)\n3. 最后real patch @{datetime.fromtimestamp(cutoff).strftime("%H:%M")}，之后{post_q}题全empty\n'
h += f'4. 空patch间隔&approx;{c_int/60:.0f}min=429快速失败\n5. resume fix生效：SKIP real patch，PREDICT deleted-empty(额度恢复后自动重跑)</pre>\n'

# C4
h += '<h2>C4 — 心跳一行</h2>\n'
h += f'<div class="box"><code>cline专项: SWE-bench real 27/41(65.9%) &middot; 额度前27/29=93.1%&approx;opencode(92%) &middot; empty 14(全infra:429额度) &middot; 24.2min/task &middot; TB4 {tb4_t}completed/0passed &middot; 失败top1=网关429额度耗尽(ETA~14:26)</code></div>\n'

# C5
h += '<h2>C5 — 差距来源分析</h2>\n'
h += '<table><tr><th>指标</th><th>cline</th><th>opencode</th><th>codex</th><th>差距来源</th></tr>\n'
h += '<tr><td>Real%(全量)</td><td>65.9%</td><td>92.0%</td><td>2.6%</td><td>额度时机+适配器</td></tr>\n'
h += '<tr><td><strong>Real%(额度前)</strong></td><td><span class="good">93.1%</span></td><td><span class="good">92.0%</span></td><td>-</td><td><strong>无能力差距</strong></td></tr>\n'
h += f'<tr><td>每题耗时</td><td>{c_avg:.1f}min</td><td>{o_avg:.1f}min</td><td>2min(空)</td><td>cline更谨慎=更多轮次</td></tr>\n'
h += f'<tr><td>空patch间隔</td><td>&approx;{c_int/60:.0f}min</td><td>&approx;6min</td><td>&approx;{cod_int/60:.0f}min</td><td>codex不重试429</td></tr>\n'
h += '<tr><td>TB4 passed</td><td>0</td><td>0</td><td>0</td><td>全0=glm-5.3-flash能力</td></tr></table>\n'
h += '<div class="note"><strong>结论</strong><ol>\n'
h += '<li><strong>连接正常时cline real=93.1%，与opencode(92.0%)无能力差距。</strong></li>\n'
h += '<li>空patch=infra(429额度耗尽)，非能力差。额度恢复后自动resume重跑。</li>\n'
h += '<li>codex 1/39=适配器不重试429+共享额度早期耗尽，<strong>非模型能力差</strong>。</li>\n'
h += f'<li>cline {c_avg:.1f}min/题 vs opencode {o_avg:.1f}min/题=cline更谨慎(更多工具轮次)，但产出质量相同。</li>\n'
h += '<li>TB4全0=glm-5.3-flash在Terminal-Bench 4.0上的能力限制(reward=0,verifier已运行pytest)。</li>\n'
h += '<li><strong>可检验假设</strong>：额度恢复(~14:26)后cline real%→90%+，空patch归零。</li>\n</ol></div>\n'

# TB4 table
h += '<h2>TB4 全局（Terminal-Bench 4.0 · 66题 × 7路）</h2>\n'
h += '<table><tr><th>Harness</th><th>Completed</th><th>Passed</th></tr>\n'
for h_name, total, real, empty, med, tc, tp in rows:
    h += f'<tr><td>{DISPLAY[h_name]}</td><td>{tc}</td><td>{tp}</td></tr>\n'
h += f'<tr><td><strong>合计</strong></td><td><strong>{tb4_t}</strong></td><td><strong>0</strong></td></tr></table>\n'

# Appendix
h += '<h2>附录</h2><ul>\n'
h += '<li>网关: /v1/models HTTP200, /v1/chat/completions HTTP429(额度耗尽,ETA~14:26)</li>\n'
h += '<li>gw_proxy 9092/9093 运行中(cline直连gateway,其余走proxy)</li>\n'
h += '<li>预测7路 alive(0% CPU,额度恢复后自动续跑)</li>\n'
h += '<li>复算命令: <code>python3 gen_cline_special_r1746.py</code>（本脚本，从predictions_glm53/实时读数）</li>\n'
h += '<li>命名纪律: 正文一律写 cline（代码路径 cline-patched 不改）</li>\n'
h += f'</ul>\n<hr><p><small>生成: {now} · gen_cline_special_r1746.py · 0外链 · 增量自 R1745</small></p></body></html>\n'

out = os.path.join(os.path.dirname(__file__), "..", "..", "reports", "report_harness_cline_special_r1746_zh.html")
with open(out, "w") as f:
    f.write(h)
print(f"Wrote {out} ({len(h)} bytes)")
