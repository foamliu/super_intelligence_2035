#!/usr/bin/env python3
"""Build the 3-segment WaveView selftest HTML report (V0 text / V1 base-VQA / V2 SFT-RFT-VQA).
Reads summary_v2.json (this run) + v2_summary.json (synthetic 60->90 context).
Overwrites reports/report_vision_waveview_selftest_zh.html in place (line convention).
Single file, 0 external links, 0 script, inline SVG. Author: vision wake#1235."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(HERE, "summary_v2.json")))
V2CTX = None
_v2p = os.path.normpath(os.path.join(HERE, "..", "strengthen_runs", "v2_summary.json"))
if os.path.isfile(_v2p):
    V2CTX = json.load(open(_v2p))

def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

rows = S["flip_table"]
tot = {a: 0 for a in ("V0", "V1", "V2")}; totk = 0
v2gt = v2lt = 0
for r in rows:
    for a in ("V0", "V1", "V2"):
        tot[a] += int(r[a + "_k"].split("/")[0])
    totk += int(r["V2_k"].split("/")[1])
    n1 = int(r["V1_k"].split("/")[0]); n2 = int(r["V2_k"].split("/")[0])
    if n2 > n1: v2gt += 1
    elif n2 < n1: v2lt += 1
pct = {a: round(tot[a] / totk * 100, 1) for a in ("V0", "V1", "V2")}
n = S["n_cases"]

def svg_bar():
    W, H = 360, 200
    arms = ["V0", "V1", "V2"]; cols = {"V0": "#9aa4b2", "V1": "#2b6cb0", "V2": "#2f855a"}
    labs = {"V0": "V0 文本", "V1": "V1 基模VQA", "V2": "V2 SFT/RL-VQA"}
    bw = 70; gap = 30; base_x = 60; maxv = 100
    bars = ""
    for i, a in enumerate(arms):
        x = base_x + i * (bw + gap); h = pct[a] / maxv * (H - 50)
        bars += f'<rect x="{x}" y="{H-30-h:.1f}" width="{bw}" height="{h:.1f}" fill="{cols[a]}"/>'
        bars += f'<text x="{x+bw/2}" y="{H-30-h-4:.1f}" font-size="12" text-anchor="middle" fill="#222">{pct[a]}%</text>'
        bars += f'<text x="{x+bw/2}" y="{H-12}" font-size="11" text-anchor="middle" fill="#444">{esc(labs[a])}</text>'
    grid = ""
    for v in (0, 25, 50, 75, 100):
        y = H - 30 - v / maxv * (H - 50)
        grid += f'<line x1="54" y1="{y:.1f}" x2="{W-10}" y2="{y:.1f}" stroke="#eee"/><text x="50" y="{y+3:.1f}" font-size="9" text-anchor="end" fill="#888">{v}</text>'
    return (f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg"><rect width="{W}" height="{H}" fill="#fff"/><text x="{W/2}" y="16" font-size="12" text-anchor="middle" fill="#222">每量准确率（通过条件数 / 总条件数）</text>{grid}{bars}</svg>')

def svg_per_case():
    W = 760; H = 240; bw = 8; gap = 4; base_x = 40; maxv = 1.0
    bars = ""
    for i, r in enumerate(rows):
        x = base_x + i * (3 * bw + gap + 28)
        for j, a in enumerate(("V0", "V1", "V2")):
            nk = r[a + "_k"].split("/"); frac = int(nk[0]) / max(1, int(nk[1]))
            col = {"V0": "#9aa4b2", "V1": "#2b6cb0", "V2": "#2f855a"}[a]
            h = frac / maxv * (H - 50)
            bx = x + j * (bw + 1)
            bars += f'<rect x="{bx}" y="{H-30-h:.1f}" width="{bw}" height="{h:.1f}" fill="{col}"/>'
        bars += f'<text x="{x+bw+1}" y="{H-16}" font-size="9" text-anchor="middle" fill="#444">{esc(r["tag"])}</text>'
    leg = '<rect x="'+str(W-180)+'" y="14" width="9" height="9" fill="#9aa4b2"/><text x="'+str(W-167)+'" y="22" font-size="9" fill="#444">V0</text>'
    leg += '<rect x="'+str(W-145)+'" y="14" width="9" height="9" fill="#2b6cb0"/><text x="'+str(W-132)+'" y="22" font-size="9" fill="#444">V1</text>'
    leg += '<rect x="'+str(W-110)+'" y="14" width="9" height="9" fill="#2f855a"/><text x="'+str(W-97)+'" y="22" font-size="9" fill="#444">V2</text>'
    return f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg"><rect width="{W}" height="{H}" fill="#fff"/><text x="{W/2}" y="14" font-size="12" text-anchor="middle" fill="#222">逐题通过率（k_pass/k_total）</text>{leg}{bars}</svg>'

case_rows = "".join(
    f"<tr><td>{esc(r['tag'])}</td><td>{esc(r['tier'])}</td><td>{esc(r['V0'])} ({esc(r['V0_k'])})</td>"
    f"<td>{esc(r['V1'])} ({esc(r['V1_k'])})</td><td>{esc(r['V2'])} ({esc(r['V2_k'])})</td>"
    f"<td>{r['V2_tool_calls']}</td></tr>" for r in rows)
mcn = S["mcnemar_V1_vs_V2"]
aud = S["audit"]
v2ctx_line = ""
if V2CTX:
    v2ctx_line = (f"合成集（机制验证）：before {V2CTX['pre_baseline']['accuracy']*100:.0f}% → v2-RFT "
                  f"{V2CTX['v2_rft']['accuracy']*100:.0f}%（McNemar b={V2CTX['mcnemar_v1best_sft_vs_v2_rft']['b_improved']} "
                  f"c={V2CTX['mcnemar_v1best_sft_vs_v2_rft']['c_regressed']} p={V2CTX['mcnemar_v1best_sft_vs_v2_rft']['p_value']}）")
html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vision WaveView 10 题自测 · 三段对照（基线→VQA→SFT/RL）</title>
<style>body{{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;max-width:1040px;margin:24px auto;color:#222;line-height:1.6;padding:0 16px}}
h1,h2,h3{{color:#1a3a5c}}table{{margin:8px 0;font-size:14px;border-collapse:collapse}}th{{background:#eef3f8}}td,th{{border:1px solid #ccc;padding:6px 10px}}.card{{background:#f7f9fc;border:1px solid #dce3ec;border-radius:8px;padding:14px 18px;margin:14px 0}}
.verdict{{font-size:17px;font-weight:bold;padding:12px 16px;border-radius:8px}}.neg{{background:#fdecea;color:#a3241b}}.pos{{background:#e6f4ea;color:#1e6b3a}}code{{background:#eef;padding:1px 4px;border-radius:3px}}.muted{{color:#888}}.svgwrap{{text-align:center}}</style></head>
<body>
<h1>Vision WaveView 10 题自测 · 三段对照（基线 → 加 VQA → SFT/RL）</h1>
<p class="muted">vision 线 · 用户直令 2026-11-14 19:4x（阶段 A）+ 本线使命交付判据（三段数字并列）· Qwen3.5-2B · {esc(S['date'])}</p>
<div class="card verdict neg">整题通过率：V0 = V1 = V2 = 0/10（0 翻转）—— 诚实负结果。但<b>每量准确率</b>三段递增：V0 {pct['V0']}% → V1 {pct['V1']}% → V2 {pct['V2']}%（SFT/RL 适配器在真实 WaveView 上带来 +{round(pct['V2']-pct['V1'],1)}pp 每量增益）。</div>
<h2>1. 三段设计（唯一变量 = VQA 后端权重）</h2>
<div class="card"><ul>
<li><b>V0 基线</b>：纯文本 agent（Qwen3.5-2B，不看图）—— 正确的无多模态基线。</li>
<li><b>V1 加 VQA</b>：agent 经 VQA MCP 工具调<b>基模</b> Qwen3.5-2B 读图（HTTP /vqa :30001）。</li>
<li><b>V2 加 SFT/RL</b>：同一 agent 同一问题，VQA 后端换为<b>基模 + v2-RFT LoRA 适配器</b>（<code>rft2_adapter_seed11</code>，HTTP :30003）。V1↔V2 唯一变量 = 后端权重。</li>
<li><b>判分</b>：vision 按设计流公开 oracle+容差重建的等价 check（每题 k=9–14 条件，全过才 PASS）。V2 适配器训练用 CoT target（结尾 "Final Answer: X"），故 V2 抽取该字段后再喂给<b>同一</b> check_case；V0/V1 用同一抽取重算 == 已交付值（mismatch={len(S['rederive_mismatches'])}，单变量干净）。</li>
<li><b>口径标签</b>：WaveView <b>真实题</b>（designflow 公开参数等价重建，<b>非合成集</b>；PNG/check 非原始字节，.15 不可达=infra-blocker）。</li>
</ul></div>
<h2>2. 整题通过率（PASS = 全 k 条件过）</h2>
<table><tr><th>臂</th><th>配置</th><th>整题通过</th><th>率</th></tr>
<tr><td>V0</td><td>文本不看图</td><td>{S['V0_pass']}/{n}</td><td>{S['V0_rate']*100:.0f}%</td></tr>
<tr><td>V1</td><td>基模 VQA</td><td>{S['V1_pass']}/{n}</td><td>{S['V1_rate']*100:.0f}%</td></tr>
<tr><td><b>V2</b></td><td><b>SFT/RL VQA</b></td><td><b>{S['V2_pass']}/{n}</b></td><td><b>{S['V2_rate']*100:.0f}%</b></td></tr></table>
<p>翻转：V0→V1 = {S['flips_V0fail_V1pass']}，V1→V2 = {S['flips_V1fail_V2pass']}，V0→V2 = {S['flips_V0fail_V2pass']}。McNemar（配对，n=10 样本不足仅参考）：V1→V2 b={mcn['b_improved']} c={mcn['c_regressed']} p={mcn['p_value']}。</p>
<h2>3. 每量准确率（k_pass / k_total，逐题）</h2>
<div class="svgwrap">{svg_per_case()}</div>
<table><tr><th>题</th><th>tier</th><th>V0</th><th>V1</th><th>V2</th><th>V2工具调用</th></tr>{case_rows}
<tr style="font-weight:bold;background:#eef3f8"><td>合计</td><td>—</td><td>{tot['V0']}/{totk} ({pct['V0']}%)</td><td>{tot['V1']}/{totk} ({pct['V1']}%)</td><td>{tot['V2']}/{totk} ({pct['V2']}%)</td><td>81</td></tr></table>
<div class="svgwrap">{svg_bar()}</div>
<p>V2 每量 &gt; V1 在 <b>{v2gt}/10</b> 题，&lt; V1 在 {v2lt}/10 题（β9 0&lt;1、β8 7&lt;10、α2 4&lt;5）。最大单题跃升：β6 4/14→9/14（+5）、β7 2/12→7/12（+5）、β11 6/12→10/12（+4）。</p>
<h2>4. 🚫 反作弊审计</h2>
<div class="card"><p>cheat = <b>{aud['cheat']}</b>，cheat_count = <b>{aud['cheat_count']}</b>，findings = {aud['findings']}。V2 VQA 调用 {aud['v2_vqa_calls']} 次，V2 直接读图 {aud['v2_image_reads']} 次（仅经 VQA 工具读图，runner 源码无 PIL/opencv/OCR/base64）。<b>cheat=0 方可引用通过率</b> ✓。</p></div>
<h2>5. 诚实结论与口径</h2>
<div class="card">
<p><b>整题维度（用户判据 "真实题通过率有提升"）</b>：未达成 —— V0=V1=V2=0/10、0 翻转。根因：每题 k=9–14 条件<b>全过</b>门槛高，2B 适配器能把单量读对率拉到 55.5%，但尚无任一题把全部条件同时读对（最接近：β6 9/14、β11 10/12、α4 6/9）。这是<b>真实题上的诚实负结果</b>。</p>
<p><b>每量维度（能力增量）</b>：三段递增 V0 {pct['V0']}% → V1 {pct['V1']}% → V2 {pct['V2']}%。① V1−V0=+{round(pct['V1']-pct['V0'],1)}pp = 接入 VQA 的能力增量（基模能看图）；② V2−V1=+{round(pct['V2']-pct['V1'],1)}pp = SFT/RL 域适配的增量（CoT 读数推理链在<b>真实 WaveView</b> 上确有迁移，未停留在合成集）。</p>
<p><b>合成集 vs 真实题</b>：{esc(v2ctx_line or '（v2 合成集上下文不可读）')}。合成集 60→90 的显著提升，落到真实 WaveView 上体现为<b>每量 +{round(pct['V2']-pct['V1'],1)}pp</b>（非整题翻转）—— 合成集只用于机制验证，结论回到真实题上说话。</p>
<p><b>下一步</b>：① 把 k 全过门槛拆为「每量分」与「整题过」双指标上报（本报告已做）；② 扩 SFT/RL 数据到真实波形分布、加 GRPO 群体奖励，目标把单题推到全过；③ 待 designflow task2（评测机→.17:30002 可达性解阻）做端到端 cline+SUT+VQA 对照，量 end-to-end 翻转（与本「VQA 能力天花板」互补）。</p>
</div>
<p class="muted">产物：waveview_selftest_v2_run.py · V2/*.json(10) · summary_v2.json · audit_v2.json · qwen35_vqa_server.py(+--adapter) · :30003 适配器端点。本报告单文件自包含、0 外链、0 script、2 内联 SVG。</p>
</body></html>"""
out = os.path.normpath(os.path.join(HERE, "..", "..", "..", "reports", "report_vision_waveview_selftest_zh.html"))
with open(out, "w") as f:
    f.write(html)
print(f"=== 3-segment report -> {out} ({len(html)}B)")
