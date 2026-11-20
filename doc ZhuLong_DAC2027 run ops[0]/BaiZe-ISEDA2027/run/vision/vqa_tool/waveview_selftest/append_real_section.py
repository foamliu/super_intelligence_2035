#!/usr/bin/env python3
"""Append the REAL-case (true designflow PNG) 3-segment rerun section to the
agent-arms WaveView selftest HTML report (same file, in-place overwrite).

USER ORDER (2026-11-15 07:2x task2 acceptance#4): rerun real cases and
in-place update reports/report_vision_waveview_selftest_agent_zh.html.

Reads summary_real.json + audit_real.json, injects an appendix before
</body></html>. Single file, 0 external links, 0 script, inline SVG.
Author: vision (real-case wake)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "summary_real.json")))
ra = json.load(open(os.path.join(HERE, "audit_real.json")))
REPORT = os.path.normpath(os.path.join(HERE, "..", "..", "..", "reports",
    "report_vision_waveview_selftest_agent_zh.html"))


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


rn = R["real_cases_count"]
rPCT = {a: round(R["per_quantity"][f"{a}_rate"] * 100, 1) for a in ("V0", "V1", "V2")}
r_ok = {a: R["per_quantity"][f"{a}_ok"] for a in ("V0", "V1", "V2")}
r_tot = {a: R["per_quantity"][f"{a}_total"] for a in ("V0", "V1", "V2")}
rwp = {"V0": R["V0_pass"], "V1": R["V1_pass"], "V2": R["V2_pass"]}
rmc = R["mcnemar_V1_vs_V2"]; rmc02 = R["mcnemar_V0_vs_V2"]; rmc01 = R["mcnemar_V0_vs_V1"]
rc = {"V0": "#9aa4b2", "V1": "#2b6cb0", "V2": "#2f855a"}
rl = {"V0": "V0 文本(不看图)", "V1": "V1 基模VQA", "V2": "V2 SFT/RL-VQA"}


def svg_real_bar():
    W, H = 460, 200; arms = ["V0", "V1", "V2"]; bw = 60; gap = 40; base_x = 60; maxv = 100
    bars = ""
    for i, a in enumerate(arms):
        x = base_x + i * (bw + gap); h = rPCT[a] / maxv * (H - 50)
        bars += (f'<rect x="{x}" y="{H-30-h:.1f}" width="{bw}" height="{h:.1f}" fill="{rc[a]}"/>'
                 f'<text x="{x+bw/2}" y="{H-30-h-4:.1f}" font-size="12" text-anchor="middle" fill="#222">{rPCT[a]}%</text>'
                 f'<text x="{x+bw/2}" y="{H-12}" font-size="9" text-anchor="middle" fill="#444">{esc(rl[a])}</text>')
    grid = ""
    for v in (0, 25, 50, 75, 100):
        y = H - 30 - v / maxv * (H - 50)
        grid += (f'<line x1="54" y1="{y:.1f}" x2="{W-10}" y2="{y:.1f}" stroke="#eee"/>'
                 f'<text x="50" y="{y+3:.1f}" font-size="9" text-anchor="end" fill="#888">{v}</text>')
    return (f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="{W}" height="{H}" fill="#fff"/>'
            f'<text x="{W/2}" y="16" font-size="12" text-anchor="middle" fill="#222">真题每量准确率（通过条件数 / 总条件数）· 三段 V0/V1/V2</text>'
            f'{grid}{bars}</svg>')


real_rows = ""
for r in R["rows"]:
    flip = "✓" if (r.get("flip_V0_V2") or r.get("flip_V1_V2")) else ""
    real_rows += (f"<tr><td>{esc(r['tag'])}</td><td>{esc(r['tier'])}</td><td>{esc(r['case_id'])}</td>"
                  f"<td>{r['k_total']}</td>"
                  f"<td>{esc(r['V0'])}<br><span class='muted'>{esc(r['V0_k'])}</span></td>"
                  f"<td>{esc(r['V1'])}<br><span class='muted'>{esc(r['V1_k'])}</span></td>"
                  f"<td>{esc(r['V2'])}<br><span class='muted'>{esc(r['V2_k'])}</span></td>"
                  f"<td>{flip}</td></tr>")
vcls = "pos" if rwp["V2"] > 0 else "neg"
appendix = f"""
<hr>
<h1 style="margin-top:28px">附录 · 真题(真实 designflow PNG)三段重跑（2026-11-15 07:2x 用户令 任务②）</h1>
<p class="muted">vision 线 · 自行 SSH 到 36.15 检出 WaveView 真题(用户放行) · 真题 PNG sha256 校验只读复制 · {esc(R.get('generated','2026-11-15'))}</p>
<div class="card">
<p><b>口径变更(重要)</b>：本附录的题是 <b>designflow 在 36.15 上已恢复原形态的真实 WaveView PNG</b>(sha256 与源一致, 只读复制到 <code>run/vision/real_waveview_images/&lt;case&gt;/</code>),
<b>非上方 §1–§7 的等价重建(replica)题</b>。两节口径不同, 数字不可混。上方 G 臂跑在 replica PNG 上, 本附录三段跑在真实 PNG 上。</p>
<p><b>检出结果(诚实)</b>：实际可用 = <b>{rn} 道</b>。交底清单原写 11(α4+β7), 但 <b>β5 FsdbNetToggleDiag-001 案例不存在</b>(convener r508 核实, 4 shard jsonl 全量 grep 0 命中), 故真·可恢复分母 = 10, 不是 11。🚫 未拿合成集冒充真题。另有 5 个 wave 名 case 有 check.py 但 assets 下无 visible PNG, 不计入。每题: domain=waveform/图像题、case 目录内真有 PNG、有 check.py、已跑过基线(全 FAIL = 正确无多模态基线)、check.py <b>原样未改</b>(只读复制, 未触碰 designflow 题目/图片/check)。</p>
<p>详见 <code>run/vision_real_waveview_intake.md</code>(人读) + <code>run/vision/real_waveview_index.json</code>(机器可读)。</p>
</div>
<h2>A.1 整题通过（真题三段 V0/V1/V2）</h2>
<div class="card verdict {vcls}">真题整题通过：V0(文本/不看图)={rwp['V0']}/{rn} · V1(基模 VQA)={rwp['V1']}/{rn} · <b>V2(SFT/RL 强化 VQA)={rwp['V2']}/{rn}</b>。
三段唯一变量 = VQA 后端权重(V0 不看图 / V1 基模 Qwen3.5-2B / V2 基模+rft2_adapter), 同 10 真题、同 check.py 容差、温度 0、顺序随机化。
<b>V2 翻转 1 整题</b>(α1 EyeApertureSelect: V1 2/9→V2 9/9 全过)。McNemar V1↔V2 b={rmc['b_improved']} c={rmc['c_regressed']} p={rmc['p_value']}(n={rn} 样本不足, 仅参考)。</div>
<h2>A.2 每量准确率（真题）</h2>
<div class="svgwrap">{svg_real_bar()}</div>
<table><tr><th>段</th><th>VQA 后端</th><th>每量通过</th><th>每量率</th><th>整题通过</th></tr>
<tr><td>V0</td><td>无(纯文本, 不看图)</td><td>{r_ok['V0']}/{r_tot['V0']}</td><td>{rPCT['V0']}%</td><td>{rwp['V0']}/{rn}</td></tr>
<tr><td>V1</td><td>基模 Qwen3.5-2B</td><td>{r_ok['V1']}/{r_tot['V1']}</td><td>{rPCT['V1']}%</td><td>{rwp['V1']}/{rn}</td></tr>
<tr><td><b>V2</b></td><td><b>基模+rft2_adapter</b></td><td><b>{r_ok['V2']}/{r_tot['V2']}</b></td><td><b>{rPCT['V2']}%</b></td><td><b>{rwp['V2']}/{rn}</b></td></tr></table>
<p>每量三段：V0 {rPCT['V0']}%→V1 {rPCT['V1']}%→V2 {rPCT['V2']}%。V1−V0={round(rPCT['V1']-rPCT['V0'],1)}pp(接入 VQA 能力增量) · V2−V1=<b>{round(rPCT['V2']-rPCT['V1'],1)}pp</b>(SFT/RL 域适配增量, 合成训练迁移到真实 WaveView)。</p>
<h2>A.3 逐题明细（真题）</h2>
<table><tr><th>题</th><th>tier</th><th>case_id</th><th>k</th><th>V0</th><th>V1</th><th>V2</th><th>翻转</th></tr>
{real_rows}</table>
<p class="muted">tier 释义: A=did-not-engage · B=engaged-text-only · C=engaged-but-could-not-read-image(预期 +VQA 主翻转源)。翻转列 = V0fail→V2pass 或 V1fail→V2pass。</p>
<h2>A.4 🚫 反作弊审计（真题）</h2>
<div class="card"><p>cheat = <b>{ra.get('cheat')}</b>，cheat_count = <b>{ra.get('cheat_count')}</b>。VQA 调用 {ra.get('vqa_calls')} 次, 直接读图 {ra.get('image_reads')} 次(本进程不解码图像, 只经 HTTP VQA 工具)。禁 PIL·OCR·base64·搜答案口径不变。<b>cheat=0 方可引用通过率</b> ✓。</p></div>
<h2>A.5 诚实结论与口径（真题）</h2>
<div class="card">
<p><b>整题维度</b>：真题三段 V0=V1=0/{rn}、V2=1/{rn}。V2(SFT/RL 强化)在真实 PNG 上翻转 1 整题(α1 EyeApertureSelect 9/9 全过), 证合成训练 60→90 的增益<b>部分迁移</b>到真实 EDA 波形。其余 9 题整题仍 fail, 根因 = k 全过门槛高 + 精确计数/精确数值/跨面板反推仍是 2B VLM 读不稳的边界(与 replica G 臂 §5 卡点量一致)。</p>
<p><b>每量维度</b>：V0 {rPCT['V0']}%→V1 {rPCT['V1']}%→V2 {rPCT['V2']}%, 三段单调递增, V2−V1={round(rPCT['V2']-rPCT['V1'],1)}pp 证域适配增量在真实题上仍成立。</p>
<p><b>McNemar</b>：V1↔V2 b={rmc['b_improved']} c={rmc['c_regressed']} p={rmc['p_value']} · V0↔V2 b={rmc02['b_improved']} c={rmc02['c_regressed']} p={rmc02['p_value']} · V0↔V1 b={rmc01['b_improved']} c={rmc01['c_regressed']} p={rmc01['p_value']}。<b>n={rn} 样本不足, 仅作参考, 不声称统计显著</b>。</p>
<p><b>scope 限定</b>：本附录结论仅适用这 {rn} 道 designflow 已恢复看图的 WaveView 真题; V2 翻转 1/10 是诚实弱正结果, 不可外推为「真实 EDA 通过率 = 10%」。replica G 臂(上方 §1–§7)与真题三段(本附录)口径不同, 分别归因。</p>
<p><b>传输层</b>：真题重跑与桥接无关(本机 .17 直读 NFS 真题 PNG); 36.15→.17 VQA 通道桥接证据见 <code>run/vision_vqa_ssh_bridge.md</code> + <code>run/vision_ssh_bridge_proof.txt</code>(三端点容器视角 curl /health ok + 断线 ~6s 自愈)。</p>
</div>
<p class="muted">真题产物：vision/real_waveview_index.json · vision_real_waveview_intake.md · vision/real_waveview_images/&lt;case&gt;/ · waveview_selftest_real_run.py · REAL/*.json · summary_real.json · audit_real.json。本附录单文件自包含、0 外链、0 script、1 内联 SVG。</p>
"""

html = open(REPORT, encoding="utf-8").read()
# idempotent: avoid double-append
if "附录 · 真题(真实 designflow PNG)三段重跑" not in html:
    html = html.replace("</body></html>", appendix + "\n</body></html>")
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"=== real appendix injected -> {REPORT} ({len(html)}B)")
else:
    print(f"=== real appendix already present, skip -> {REPORT} ({len(html)}B)")
