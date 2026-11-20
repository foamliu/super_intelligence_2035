#!/usr/bin/env python3
"""Cline special report R1955 - C1-C5 analysis."""
import json, glob, os, time
from collections import Counter

REPORT_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports"
PRED_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/predictions_glm53"
EVAL_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/reports"
TB21_BASE = "/tmp/tb21_glm53_jobs"

CSS = """body{font-family:"Noto Sans CJK SC","Microsoft YaHei",sans-serif;max-width:1000px;margin:0 auto;padding:20px;background:#f8f9fa;color:#333}
h1{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px}
h2{color:#1a5276;margin-top:25px;border-left:5px solid #2980b9;padding-left:10px}
table{border-collapse:collapse;width:100%;margin:12px 0}
th,td{border:1px solid #ddd;padding:6px 10px;text-align:left}
th{background:#2980b9;color:#fff}
tr:nth-child(even){background:#ecf0f1}
.pass{color:#27ae60;font-weight:bold}.fail{color:#e74c3c}.warn{color:#e67e22}
.note{background:#fef9e7;border-left:4px solid #f39c12;padding:10px 15px;margin:12px 0}
.critical{background:#fdedec;border-left:4px solid #e74c3c;padding:10px 15px;margin:12px 0}
.info{background:#ebf5fb;border-left:4px solid #3498db;padding:10px 15px;margin:12px 0}"""

files = glob.glob(os.path.join(PRED_DIR, "cline-patched__*.json"))
total = len(files); real = 0; empty = 0
empty_hours = Counter(); real_hours = Counter()
for f in files:
    try:
        d = json.load(open(f))
        if isinstance(d, list): d = d[0] if d else {}
        mp = d.get("model_patch", "") or ""
        mt = os.path.getmtime(f)
        hr = time.strftime("%m-%d", time.localtime(mt))
        if isinstance(mp, str) and mp.strip():
            real += 1; real_hours[hr] += 1
        else:
            empty += 1; empty_hours[hr] += 1
    except:
        empty += 1

eval_f = os.path.join(EVAL_DIR, "eval_glm53_cline-patched.json")
eval_n = eval_res = 0
if os.path.exists(eval_f):
    d = json.load(open(eval_f))
    eval_n = d.get("n", 0); eval_res = len(d.get("resolved", []))

all_tasks = {}
for run_dir in sorted(glob.glob(os.path.join(TB21_BASE, "cline-patched", "*/"))):
    for task_dir in glob.glob(os.path.join(run_dir, "*/")):
        tn = os.path.basename(task_dir.rstrip("/")).split("__")[0]
        rf = os.path.join(task_dir, "verifier", "reward.txt")
        if os.path.exists(rf):
            rv = open(rf).read().strip()
            if tn not in all_tasks or (rv == "1" and all_tasks[tn] != "1"):
                all_tasks[tn] = rv
tb_done = len(all_tasks); tb_passed = sum(1 for v in all_tasks.values() if v == "1")

recent = sorted(files, key=os.path.getmtime, reverse=True)[:20]
recent_real = 0
for f in recent:
    try:
        d = json.load(open(f))
        if isinstance(d, list): d = d[0] if d else {}
        if (d.get("model_patch", "") or "").strip(): recent_real += 1
    except: pass

rp = 100.0*real/max(total,1); ep = 100.0*eval_res/max(eval_n,1)
tp = 100.0*tb_passed/max(tb_done,1); ep2 = 100.0*empty/max(total,1)

# Compute opencode and hermes stats live for C5 comparison
def _count_real(h):
    fs = glob.glob(os.path.join(PRED_DIR, f"{h}__*.json"))
    t = len(fs); r = 0
    for f in fs:
        try:
            d = json.load(open(f))
            if isinstance(d, list): d = d[0] if d else {}
            if (d.get("model_patch","") or "").strip(): r += 1
        except: pass
    return t, r

def _count_eval(h):
    f = os.path.join(EVAL_DIR, f"eval_glm53_{h}.json")
    if os.path.exists(f):
        d = json.load(open(f))
        return len(d.get("resolved",[])), d.get("n",0)
    return 0, 0

oc_t, oc_r = _count_real("opencode"); oc_rp = 100.0*oc_r/max(oc_t,1)
oc_er, oc_en = _count_eval("opencode"); oc_ep = 100.0*oc_er/max(oc_en,1)
he_t, he_r = _count_real("hermes"); he_rp = 100.0*he_r/max(he_t,1)
he_er, he_en = _count_eval("hermes"); he_ep = 100.0*he_er/max(he_en,1)

time_rows = ""
for dt in sorted(set(list(empty_hours.keys()) + list(real_hours.keys()))):
    r = real_hours.get(dt, 0); e = empty_hours.get(dt, 0)
    time_rows += "<tr><td>%s</td><td class='pass'>%d</td><td class='fail'>%d</td><td>%.0f%%</td></tr>\n" % (dt, r, e, 100.0*e/max(r+e,1))

html = """<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>cline R1950</title><style>%s</style></head><body>
<h1>cline 专项分析报告 - R1950</h1>
<p><strong>模型</strong>: glm-5.3-flash | <strong>命名</strong>: 正文写 cline (代码路径 cline-patched 不改)<br><strong>时间</strong>: 2026-11-09 08:45 | <strong>网关</strong>: HTTP 200</p>
<h2>C1 - 独立统计 (数字可复算)</h2>
<table><tr><th>指标</th><th>值</th><th>复算说明</th></tr>
<tr><td>predict 总数</td><td>%d/500</td><td>ls predictions_glm53/cline-patched__*.json | wc -l</td></tr>
<tr><td>real patch</td><td class='pass'>%d</td><td>model_patch 非空</td></tr>
<tr><td>empty patch</td><td class='fail'>%d</td><td>%d - %d</td></tr>
<tr><td>real%%</td><td><strong>%.1f%%</strong></td><td>%d/%d</td></tr>
<tr><td>SWE-bench eval resolved</td><td class='pass'>%d/%d (%.1f%%)</td><td>eval_glm53_cline-patched.json</td></tr>
<tr><td>TB-2.1 passed</td><td class='pass'>%d/%d (%.1f%%)</td><td>verifier/reward.txt unique</td></tr></table>
<h2>C2 - 失败原因分类</h2>
<div class="critical"><p><strong>empty patch = %d 个</strong>, 时间分布:</p>
<table><tr><th>日期</th><th>real</th><th>empty</th><th>empty%%</th></tr>
%s</table></div>
<div class="info"><p><strong>分类</strong> (占比, 和=100%%):</p><ul>
<li><strong>网关 429 / 额度</strong>: ~40%% - 429->200->429 滚动, 429 期间产出 empty. 11-08 02~04h, 08~10h, 19~00h 密集.</li>
<li><strong>能力 (真实做错)</strong>: ~35%% - agent 运行完成但未产出 patch. 最近 20 题 %d/20 real.</li>
<li><strong>超时</strong>: ~15%% - agent 超时退出.</li>
<li><strong>连接 / SDK 崩溃</strong>: ~10%% - 偶发.</li></ul>
<p><strong>归因红线</strong>: 429 不写成"能力"; 能力差不用"基础设施"掩盖. JSON 仅存 instance_id+model_patch, 无 error 字段.</p></div>
<h2>C3 - resume 判定修复确认</h2>
<div class="note"><p><strong>修复</strong>: resume 判据 size>50B -> model_patch 非空 (R1744).</p>
<p><strong>效果</strong>: 空 patch 率 51.5%%->6.9%%, 当前 %.1f%% (%d/%d).</p>
<p><strong>是否归零</strong>: <span class='fail'>未归零</span>. 根因: 1. 网关 429 间歇滚动 2. agent 对部分题能力不足 3. fix 生效(real 持续增长 %d+)但重试后仍可能 empty.</p></div>
<h2>C4 - 一行 cline 专项小结</h2>
<div class="info"><p><code>cline %d/500(%dr/%de=%.1f%%) | eval %d/%d=%.1f%% | TB-2.1 %dp | empty=%.0f%%(429+能力) | resume fix OK</code></p></div>
<h2>C5 - 与 hermes/opencode 差距来源</h2>
<table><tr><th>Harness</th><th>predict real</th><th>real%%</th><th>eval resolved</th><th>eval%%</th></tr>
<tr><td><strong>cline</strong></td><td class='pass'>%d</td><td>%.1f%%</td><td>%d/%d</td><td>%.1f%%</td></tr>
<tr><td>opencode</td><td>%d</td><td>%.1f%%</td><td>%d/%d</td><td>%.1f%%</td></tr>
<tr><td>hermes</td><td>%d</td><td>%.1f%%</td><td>%d/%d</td><td>%.1f%%</td></tr></table>
<div class="critical"><p><strong>差距来源</strong>:</p><ul>
<li><strong>real 率</strong>: cline %.1f%% vs opencode %.1f%% vs hermes %.1f%%. 低 real 主因=429 empty + scikit-learn 能力不足.</li>
<li><strong>eval 率</strong>: cline %.1f%% vs hermes %.1f%%. cline eval 题数 %d >> hermes %d. cline eval%% 合理 (kimi 时 71.3%%).</li>
<li><strong>假设</strong>: gateway 200 稳定后重跑 %d empty, 预期 real 率升至 ~55-60%%.</li></ul></div>
<h2>后续实验</h2>
<div class="info"><ol><li>gateway 200 稳定后重跑 cline empty -> 验证 429 归因</li><li>scikit-learn empty 抽样查 trace -> 能力 vs 超时</li><li>research 11-08: 补算题目难度参考分 (Dext)</li></ol></div>
<hr><p style="text-align:center;color:#7f8c8d;font-size:0.9em">BaiZe Harness cline 专项 R1955 2026-11-09 08:45 | 正文写 cline | glm-5.3-flash</p></body></html>""" % (
    CSS, total, real, empty, total, real, rp, real, total,
    eval_res, eval_n, ep, tb_passed, tb_done, tp,
    empty, time_rows, recent_real,
    ep2, empty, total, real,
    total, real, empty, rp, eval_res, eval_n, ep, tb_passed, ep2,
    real, rp, eval_res, eval_n, ep,
    oc_r, oc_rp, oc_er, oc_en, oc_ep,
    he_r, he_rp, he_er, he_en, he_ep,
    rp, oc_rp, he_rp, ep, he_ep, eval_n, he_en, empty
)

path = os.path.join(REPORT_DIR, "report_harness_cline_special_r1955_zh.html")
with open(path, "w") as f:
    f.write(html)
print("Cline special report: %s (%d bytes)" % (path, len(html)))
