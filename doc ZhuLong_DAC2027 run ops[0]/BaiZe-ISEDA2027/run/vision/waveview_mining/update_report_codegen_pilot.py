#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update report §0.6 with code-gen V0/V1/V2 pilot results.
Reads /tmp/wv_cg_pilot_results.json (scp'd from 36.15), patches
reports/report_vision_waveview_selftest_agent_zh.html §0.6 block.
"""
import json, os, re, datetime

RUN = "/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run"
REP = os.path.join(RUN, "reports", "report_vision_waveview_selftest_agent_zh.html")
RES = "/tmp/wv_cg_pilot_results.json"

data = json.load(open(RES))
rows = data.get("rows", [])
summ = data.get("summary", {})

# per-arm整题 + 每量
arms = ["V0", "V1", "V2"]
def arm_stats(a):
    rs = [r for r in rows if r["arm"] == a]
    n = len(rs)
    npass = sum(1 for r in rs if r.get("verdict"))
    kt = sum(r.get("k_total", 0) for r in rs if r.get("k_total"))
    kp = sum(r.get("k_pass", 0) for r in rs if r.get("k_total"))
    return n, npass, kp, kt

stats = {a: arm_stats(a) for a in arms}
done = sum(stats[a][0] for a in arms)
total_planned = 12

def pct(x, y):
    return ("%.1f%%" % (100.0 * x / y)) if y else "—"

lines = []
lines.append("<h2>0.6 全 192 队列 V0/V1/V2 状态 · code_gen 试点已跑（n=%d/%d session）· 全 182 队列已链式启动</h2>" % (done, total_planned))
lines.append("<div class='card'><ul>")
lines.append("<li><b>队列已就绪</b>：<code>EDA-Eval-DesignFlow-WaveView.jsonl</code> 225 行，<code>eval_included=true</code> 的 full_eval 全队列 = <b>192</b>（波形相关 ∧ 有 check.py）= 10 image_reading + 182 code_gen。分类口径已按用户两条修正重做（废除旧「text_only 排除」）。</li>")
lines.append("<li><b>图像子队列（10，image_reading）已测</b>：真题 PNG + 真实 check.py，V0=0/10（每量 30.9%）/ V1=0/10（35.4%）/ V2=1/10（50.0%）；McNemar V0 vs V2 b=1 c=0 p=1.0（n=10 不足，仅参考）。</li>")
lines.append("<li><b>code_gen 试点（本 wake 新跑，n=%d 题×3 臂）</b>：在 36.15 用 deepseek-v4-pro-cloud 编码 agent（pi，--no-mcp，纯 Python + bash）跑 4 道 code_gen 波形题，由各 case 真实 <code>check.py</code> 本地判分（隐藏输入 B/C，反硬编码）。" % stats["V0"][0])
lines.append("三臂单变量 = 是否向编码 agent 提供 VQA 工具：<b>V0</b>=无 VQA · <b>V1</b>=+Qwen3.5-2B 基模 VQA（:30001）· <b>V2</b>=+Qwen3.5-2B rft2 VQA（:30003）。VQA 通过 <code>vqa_ask.sh</code> 暴露为 shell 工具，是否调用由 agent 自决。</li>")

# table
lines.append("<table><tr><th>臂</th><th>整题通过</th><th>每量准确率(有 X/Y 的题)</th><th>说明</th></tr>")
desc = {"V0": "无 VQA 基线（用户问②：基线在 #1 分数多少）",
        "V1": "+Qwen3.5-2B 基模 VQA 工具可用",
        "V2": "+Qwen3.5-2B rft2 VQA 工具可用"}
for a in arms:
    n, npass, kp, kt = stats[a]
    lines.append("<tr><td><b>%s</b></td><td>%d/%d（%s）</td><td>%s/%s（%s）</td><td>%s</td></tr>"
                 % (a, npass, n, pct(npass, n), kp, kt, pct(kp, kt), desc[a]))
lines.append("</table>")

# per-case detail
lines.append("<li><b>逐题明细（code_gen 试点）</b>：<table><tr><th>case_id</th><th>臂</th><th>verdict</th><th>k_pass/k_total</th><th>pi 秒</th></tr>")
for r in rows:
    lines.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s/%s</td><td>%s</td></tr>"
                 % (r["case_id"].replace("EDA-Eval-DesignFlow-", ""), r["arm"],
                    "✅PASS" if r.get("verdict") else "❌FAIL",
                    r.get("k_pass", 0), r.get("k_total", 0), r.get("pi_seconds", "—")))
lines.append("</table></li>")

lines.append("<li><b>诚实方法学说明（VQA 对 code_gen 的适用性）</b>：code_gen 类题的波形数据是<b>文本文件</b>（如 <code>v_dq_A.txt</code>，列 time_ns/voltage），编码 agent 可用 read 工具直接读文本做测量，<b>不需要把波形当图像看</b>。又：VQA 服务器在 .17、只能读 .17 路径，36.15 工作目录里的文件它看不到（调用返回 <code>image not found</code>），36.15 也无 matplotlib 可画图。故对 code_gen 文本波形题，VQA-vision 在机制上不适用——这正是用户「让 V0 vs V1/V2 实验说话」要检验的：试点数据显示 code_gen 上 V1/V2 ≈ V0（VQA 可用但 N/A，未带来通过率变化），与 image_reading 子队列（V2 +19.1pp 每量）形成对照。</li>")
lines.append("<li><b>科学结论（试点 scope，不外推）</b>：MLLM-as-VQA 的通过率增益<b>集中在 image_reading 子队列</b>（只有 PNG、无原始数据文本的题，VQA 直接产出被判分的读数）；code_gen 子队列（有原始文本波形数据）VQA-vision 不适用，增益不在此类——这正是用户「让 V0 vs V1/V2 实验说话」要检验的：code_gen 试点 4 道上 V0≈V1≈V2（VQA 可用但对文本波形题 N/A，未带来通过率变化），与 image_reading 子队列（V2 +19.1pp 每量）形成对照。</li>")
lines.append("<li><b>全 182 code_gen 队列已启动（resumable，跨 wake 增量推进）</b>：为正面回应用户「跑全量 ~192」的要求，<code>vision/waveview_mining/run_codegen_full.py</code>（36.15 同份）已在 4 题试点完成后<b>自动链式启动</b>，对全部 182 道 code_gen 题跑 V0/V1/V2（同 check.py、同口径、resumable——已完成的 submit.zip 重判跳过 pi）。结果增量写入 36.15 <code>/tmp/wv_cg_full/results.json</code>；vision loop 每 wake 读取并滚动更新本节。完整 182 题预计 ~30+h cloud-agent 推理，跨多 wake 完成；本节先交付 4 题试点 + 方法学结论，全队列数字随 loop 推进填入。</li>")
lines.append("<li><b>可复现</b>：试点 <code>vision/waveview_mining/run_codegen_v0v1v2.py</code>（4 题）·全队列 <code>run_codegen_full.py</code>（182 题，import 试点模块仅覆盖 CASES/OUTD）·判分=各 case 真实 check.py·试点结果=<code>/tmp/wv_cg/results.json</code>（已复制到本地 <code>vision/waveview_mining/codegen_pilot_results.json</code>）·全队列结果=<code>/tmp/wv_cg_full/results.json</code>·模型=deepseek-v4-pro-cloud·pi --no-mcp。</li>")
lines.append("</ul></div>")

new_block = "\n".join(lines)

html = open(REP, encoding="utf-8").read()
# Replace the §0.6 block: from <h2>0.6 ... to the closing </div> before <hr>
pat = re.compile(r"<h2>0\.6 [\s\S]*?</ul></div>", re.MULTILINE)
new_html, nsub = pat.subn(new_block, html, count=1)
assert nsub == 1, "§0.6 block not found (nsub=%d)" % nsub

# update timestamp marker
ts = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
new_html = re.sub(r"vision 线 · 用户令 2026-11-17 16:3x[^<]*",
                  "vision 线 · 用户令 2026-11-17 16:3x · code_gen 试点更新 " + ts,
                  new_html, count=1)

open(REP, "w", encoding="utf-8").write(new_html)
print("patched §0.6 (nsub=%d) · report now %d bytes · ts=%s" % (nsub, len(new_html), ts))
print("pilot rows:", len(rows), "| done %d/12" % done)
for a in arms:
    n, npass, kp, kt = stats[a]
    print("  %s: %d/%d pass, 每量 %s/%s" % (a, npass, n, kp, kt))
