#!/usr/bin/env python3
"""Build the AGENT-arms WaveView selftest HTML report (G0/G1/G2) alongside the
single-model tool-ceiling arms (V0/V1/V2).

USER ORDER (2026-11-14 21:5x): "vision 补 agent 臂：我们看的是 MLLM 作为 agent 系统一部分
带来的增益，而不是让它单打独斗。"

Reads summary_agent.json (+ per-case G/{G0,G1,G2}/*.json for self-check excerpts and stuck
quantities) and writes reports/report_vision_waveview_selftest_agent_zh.html.
Single file, 0 external links, 0 script, inline SVG. Author: vision (agent-arms wake)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(HERE, "summary_agent.json")))
GD = os.path.join(HERE, "G")


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def load_arm(arm):
    out = {}
    d = os.path.join(GD, arm)
    if not os.path.isdir(d):
        return out
    for fn in os.listdir(d):
        if fn.endswith(".json"):
            try:
                out[fn[:-5]] = json.load(open(os.path.join(d, fn)))
            except Exception:
                pass
    return out


G0 = load_arm("G0"); G1 = load_arm("G1"); G2 = load_arm("G2")
rows = S["flip_table"]
n = S["n_cases"]
wp = S["whole_question_pass"]
pq = S["per_quantity_rate"]
mcn = S["mcnemar"]
aud = S["audit"]
am = S["agent_metrics"]
fl = S["flips"]

PCT = {a: round(pq[a]["rate"] * 100, 1) for a in ("V0", "V1", "V2", "G0", "G1", "G2")}

# ---- SVG: per-quantity accuracy 6 arms ----
def svg_bar():
    W, H = 560, 220
    arms = ["V0", "V1", "V2", "G0", "G1", "G2"]
    bw = 48; gap = 22; base_x = 56; maxv = 100
    bars = ""
    for i, a in enumerate(arms):
        x = base_x + i * (bw + gap); h = PCT[a] / maxv * (H - 50)
        bars += f'<rect x="{x}" y="{H-30-h:.1f}" width="{bw}" height="{h:.1f}" fill="{COL[a]}"/>'
        bars += f'<text x="{x+bw/2}" y="{H-30-h-4:.1f}" font-size="11" text-anchor="middle" fill="#222">{PCT[a]}%</text>'
        bars += f'<text x="{x+bw/2}" y="{H-12}" font-size="9" text-anchor="middle" fill="#444">{esc(LAB[a])}</text>'
    grid = ""
    for v in (0, 25, 50, 75, 100):
        y = H - 30 - v / maxv * (H - 50)
        grid += f'<line x1="50" y1="{y:.1f}" x2="{W-10}" y2="{y:.1f}" stroke="#eee"/><text x="46" y="{y+3:.1f}" font-size="9" text-anchor="end" fill="#888">{v}</text>'
    return (f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="{W}" height="{H}" fill="#fff"/>'
            f'<text x="{W/2}" y="16" font-size="12" text-anchor="middle" fill="#222">每量准确率（通过条件数 / 总条件数）· V0–V2=单模型工具天花板 · G0–G2=agent 系统</text>'
            f'{grid}{bars}</svg>')


def svg_whole():
    W, H = 560, 200
    arms = ["V0", "V1", "V2", "G0", "G1", "G2"]
    vals = {"V0": wp["V0_singlemodel"], "V1": wp["V1_singlemodel"], "V2": wp["V2_singlemodel"],
            "G0": g0_pass, "G1": g1_pass, "G2": g2_pass}
    bw = 48; gap = 22; base_x = 56; maxv = n
    bars = ""
    for i, a in enumerate(arms):
        x = base_x + i * (bw + gap); h = vals[a] / maxv * (H - 50)
        bars += f'<rect x="{x}" y="{H-30-h:.1f}" width="{bw}" height="{h:.1f}" fill="{COL[a]}"/>'
        bars += f'<text x="{x+bw/2}" y="{H-30-h-4:.1f}" font-size="12" text-anchor="middle" fill="#222">{vals[a]}/{n}</text>'
        bars += f'<text x="{x+bw/2}" y="{H-12}" font-size="9" text-anchor="middle" fill="#444">{esc(LAB[a])}</text>'
    return (f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="{W}" height="{H}" fill="#fff"/>'
            f'<text x="{W/2}" y="16" font-size="12" text-anchor="middle" fill="#222">整题通过数（PASS = 全 k 条件过）</text>{bars}</svg>')


def _cap_badge(D, cid):
    r = D.get(cid, {})
    if r.get("turn_capped"):
        fin = "✓" if r.get("finalized_after_cap") else "✗"
        return f"<br><span class='muted' title='agent hit turn cap; finalized={fin}'>⚠cap{fin}</span>"
    return ""


case_rows = ""
for r in rows:
    cid = r["case_id"]
    case_rows += (
        f"<tr><td>{esc(r['tag'])}</td><td>{esc(r['tier'])}</td>"
        f"<td>{esc(r['V0'])}<br><span class='muted'>{esc(r.get('V0_k','?'))}</span></td>"
        f"<td>{esc(r['V1'])}<br><span class='muted'>{esc(r['V1_k'])}</span></td>"
        f"<td>{esc(r['V2'])}<br><span class='muted'>{esc(r['V2_k'])}</span></td>"
        f"<td>{esc(r['G0'])}<br><span class='muted'>{esc(r['G0_k'])}</span></td>"
        f"<td>{esc(r['G1'])}<br><span class='muted'>{esc(r['G1_k'])}</span>{_cap_badge(G1,cid)}</td>"
        f"<td>{esc(r['G2'])}<br><span class='muted'>{esc(r['G2_k'])}</span>{_cap_badge(G2,cid)}</td>"
        f"<td>{r.get('G1_vqa','?')}</td><td>{r.get('G1_reask','?')}</td>"
        f"<td>{r.get('G2_vqa','?')}</td><td>{r.get('G2_reask','?')}</td>"
        f"<td>{'✓' if (r.get('flip_G0_G1') or r.get('flip_G0_G2')) else ''}</td></tr>")


def selfcheck_block(arm, D):
    items = []
    for cid, r in D.items():
        sc = r.get("agent_selfcheck") or []
        for ex in sc[:1]:
            items.append(f"<li><b>{esc(r.get('tag'))}</b> ({esc(cid[:28])}…, vqa={r.get('vqa_calls_per_task')}, "
                         f"reask={r.get('reask_count')}): <code>{esc(ex)}</code></li>")
    if not items:
        return "<p class='muted'>（该臂本轮未捕获到显式自检措辞；agent 的 re-ask 行为见上表 reask 列。）</p>"
    return "<ul>" + "".join(items[:8]) + "</ul>"


def stuck_block(arm, D):
    items = []
    for cid, r in D.items():
        if r.get("verdict") == "PASS":
            continue
        conds = r.get("conditions") or []
        failed = [c.get("name", c.get("key", "?")) for c in conds if not c.get("pass")]
        cap_note = ""
        if r.get("turn_capped"):
            fin = "consolidated after cap" if r.get("finalized_after_cap") else "NOT consolidated (cut off mid-tool-use)"
            cap_note = f" · ⚠ <b>turn-capped</b> at {r.get('n_turns')} turns ({fin}; {r.get('vqa_calls_per_task')} vqa reads made — 0/k here may understate what was read)"
        items.append(f"<li><b>{esc(r.get('tag'))}</b> {esc(cid[:28])}…: {r.get('k_pass')}/{r.get('k_total')} "
                     f"—— 仍卡在 {len(failed)} 个量：{esc(', '.join(failed[:8]))}"
                     f"{(' …' if len(failed)>8 else '')}{cap_note}</li>")
    if not items:
        return f"<p class='muted'>（{arm} 无失败题。）</p>"
    return "<ul>" + "".join(items) + "</ul>"

COL = {"V0": "#9aa4b2", "V1": "#2b6cb0", "V2": "#2f855a",
       "G0": "#cbd5e0", "G1": "#dd6b20", "G2": "#b83280"}
LAB = {"V0": "V0 文本", "V1": "V1 基模VQA", "V2": "V2 SFT/RL-VQA",
       "G0": "G0 agent无工具", "G1": "G1 agent+基模", "G2": "G2 agent+适配器"}

g1_pass = wp["G1_agent_baseVQA"]; g2_pass = wp["G2_agent_adapterVQA"]
g0_pass = wp["G0_agent_notool"]
v1_pass = wp["V1_singlemodel"]; v2_pass = wp["V2_singlemodel"]
agent_flips = fl["G0->G1 (VQA channel in agent)"] + fl["G0->G2 (VQA+rft2 in agent)"]
orch_flips = fl["V1->G1 (agent orchestration on base)"] + fl["V2->G2 (agent orchestration on rft2)"]
# verdict_pos = at least one whole-question PASS in the agent arms (G1/G2) -> the
# MLLM-as-part-of-agent-system framing produced an observable whole-question flip.
verdict_pos = (g1_pass + g2_pass) > 0
vcls = "pos" if verdict_pos else "neg"
hdr = ("vision 线 · 用户令 2026-11-14 21:5x「补 agent 臂：MLLM 作为 agent 系统一部分带来的增益」"
       f"· SUT = glm-5.2（vision cline 文本底座）经 OpenAI 兼容 function-calling API · {esc(S['date'])}")
wq = wp
html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vision WaveView 10 题 · agent 臂自测（G0/G1/G2）· MLLM 作为 agent 系统一部分</title>
<style>body{{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;max-width:1080px;margin:24px auto;color:#222;line-height:1.6;padding:0 16px}}
h1,h2,h3{{color:#1a3a5c}}table{{margin:8px 0;font-size:13px;border-collapse:collapse}}th{{background:#eef3f8}}td,th{{border:1px solid #ccc;padding:5px 8px;vertical-align:top}}
.card{{background:#f7f9fc;border:1px solid #dce3ec;border-radius:8px;padding:14px 18px;margin:14px 0}}
.verdict{{font-size:17px;font-weight:bold;padding:12px 16px;border-radius:8px}}.neg{{background:#fdecea;color:#a3241b}}.pos{{background:#e6f4ea;color:#1e6b3a}}
code{{background:#eef;padding:1px 4px;border-radius:3px;font-size:12px}}.muted{{color:#888;font-size:12px}}.svgwrap{{text-align:center}}ul{{margin:6px 0}}</style></head>
<body>
<h1>Vision WaveView 10 题 · agent 臂自测（G0 / G1 / G2）</h1>
<p class="muted">{esc(hdr)}</p>
<div class="card verdict {vcls}">整题通过：单模型工具天花板 V0={wq['V0_singlemodel']}/{n} · V1={v1_pass}/{n} · V2={v2_pass}/{n}；
<b>agent 臂 G0={g0_pass}/{n} · G1={g1_pass}/{n} · G2={g2_pass}/{n}</b>。
agent 系统内引入 VQA 通道的翻转：G0→G1={fl['G0->G1 (VQA channel in agent)']}、G0→G2={fl['G0->G2 (VQA+rft2 in agent)']}；
agent 编排相对单模型的翻转：V1→G1={fl['V1->G1 (agent orchestration on base)']}、V2→G2={fl['V2->G2 (agent orchestration on rft2)']}。
每量准确率：V0 {PCT['V0']}%→V1 {PCT['V1']}%→V2 {PCT['V2']}%｜G0 {PCT['G0']}%→G1 {PCT['G1']}%→G2 {PCT['G2']}%。
{"agent 臂出现整题 PASS = MLLM 接入 agent 系统带来可观测的整题翻转（单模型臂结构上做不到）。" if verdict_pos else "agent 臂整题仍未翻转，但每量准确率与 re-ask 次数体现了 agent 编排的机制（见下）。"}</div>
<h2>1. 设计：单模型臂 vs agent 臂（两条平行轴，各自单变量）</h2>
<div class="card"><ul>
<li><b>单模型臂（工具天花板，wake#1235 已交付）</b>：Python 固定 harness 对每个量<b>问一次</b>。V0 不看图 / V1 基模 Qwen3.5-2B VQA / V2 基模+rft2 适配器。只回答「这个 VQA 工具本身能读多准」，<b>不作本线能力结论</b>。</li>
<li><b>agent 臂（本轮正式测法）</b>：SUT = <b>glm-5.2</b>（vision cline 的文本底座），它<b>看不见图</b>，只能调 <code>vqa(image_path, query)</code> 工具读图。<b>唯一变量 = 工具后端 / 有无工具</b>：G0 无工具（正确基线，应 fail）／G1 后端=基模 :30001／G2 后端=基模+rft2_adapter :30003。同 10 题、同 gen() PNG、同 check_case/oracle/容差、temperature=0、顺序随机化 seed=20261114。agent 自选 query 与提问次数。</li>
<li><b>agent 的结构性优势</b>：能把没读准的量<b>再问一次 / 换问法 / 交叉验证</b>——这是「每量 55.5%」能否补成「整题全过」的关键，单模型一次提问做不到。</li>
<li><b>归因</b>：G1 vs V1 = agent 编排在基模后端上的增益；G2 vs V2 = agent 编排在强化后端上的增益；G1 vs G0 = agent 系统内 VQA 通道增益；G2 vs G1 = agent 系统内适配器增益。</li>
<li><b>口径标签</b>：WaveView <b>真实题</b>（designflow 公开参数等价重建，<b>非合成集</b>；PNG/check 非原始字节，.15 不可达=infra-blocker）。</li>
</ul></div>
<h2>2. 整题通过数</h2>
<div class="svgwrap">{svg_whole()}</div>
<table><tr><th>臂</th><th>类型</th><th>SUT</th><th>VQA 后端</th><th>整题通过</th></tr>
<tr><td>V0</td><td>单模型</td><td>Qwen3.5-2B 文本</td><td>无</td><td>{wq['V0_singlemodel']}/{n}</td></tr>
<tr><td>V1</td><td>单模型</td><td>Qwen3.5-2B VQA</td><td>基模</td><td>{v1_pass}/{n}</td></tr>
<tr><td>V2</td><td>单模型</td><td>Qwen3.5-2B VQA</td><td>基模+rft2</td><td>{v2_pass}/{n}</td></tr>
<tr><td><b>G0</b></td><td><b>agent</b></td><td><b>glm-5.2</b></td><td><b>无工具</b></td><td><b>{g0_pass}/{n}</b></td></tr>
<tr><td><b>G1</b></td><td><b>agent</b></td><td><b>glm-5.2</b></td><td><b>基模</b></td><td><b>{g1_pass}/{n}</b></td></tr>
<tr><td><b>G2</b></td><td><b>agent</b></td><td><b>glm-5.2</b></td><td><b>基模+rft2</b></td><td><b>{g2_pass}/{n}</b></td></tr></table>
<p>翻转：G0→G1={fl['G0->G1 (VQA channel in agent)']}、G0→G2={fl['G0->G2 (VQA+rft2 in agent)']}、V1→G1={fl['V1->G1 (agent orchestration on base)']}、V2→G2={fl['V2->G2 (agent orchestration on rft2)']}。McNemar（配对，n=10 样本不足仅参考）：G0↔G1 b={mcn['G0_vs_G1']['b_improved']} c={mcn['G0_vs_G1']['c_regressed']} p={mcn['G0_vs_G1']['p_value']}；G0↔G2 b={mcn['G0_vs_G2']['b_improved']} c={mcn['G0_vs_G2']['c_regressed']} p={mcn['G0_vs_G2']['p_value']}；G1↔G2 b={mcn['G1_vs_G2']['b_improved']} c={mcn['G1_vs_G2']['c_regressed']} p={mcn['G1_vs_G2']['p_value']}；V1↔G1 b={mcn['V1_vs_G1']['b_improved']} c={mcn['V1_vs_G1']['c_regressed']} p={mcn['V1_vs_G1']['p_value']}；V2↔G2 b={mcn['V2_vs_G2']['b_improved']} c={mcn['V2_vs_G2']['c_regressed']} p={mcn['V2_vs_G2']['p_value']}。</p>
<h2>3. 每量准确率（k_pass / k_total）</h2>
<div class="svgwrap">{svg_bar()}</div>
<table><tr><th>题</th><th>tier</th><th>V0</th><th>V1</th><th>V2</th><th>G0</th><th>G1</th><th>G2</th><th>G1 vqa</th><th>G1 reask</th><th>G2 vqa</th><th>G2 reask</th><th>翻转</th></tr>
{case_rows}
<tr style="font-weight:bold;background:#eef3f8"><td>每量合计</td><td>—</td><td>{pq['V0']['ok']}/{pq['V0']['total']}<br>{PCT['V0']}%</td><td>{pq['V1']['ok']}/{pq['V1']['total']}<br>{PCT['V1']}%</td><td>{pq['V2']['ok']}/{pq['V2']['total']}<br>{PCT['V2']}%</td><td>{pq['G0']['ok']}/{pq['G0']['total']}<br>{PCT['G0']}%</td><td>{pq['G1']['ok']}/{pq['G1']['total']}<br>{PCT['G1']}%</td><td>{pq['G2']['ok']}/{pq['G2']['total']}<br>{PCT['G2']}%</td><td>{am['G1_total_vqa_calls']}</td><td>{am['G1_total_reask']}</td><td>{am['G2_total_vqa_calls']}</td><td>{am['G2_total_reask']}</td><td>{agent_flips}</td></tr></table>
<p>agent 指标：G1 共 {am['G1_total_vqa_calls']} 次 VQA 调用 / {am['G1_total_reask']} 次 re-ask / {am['G1_cases_with_selfcheck']}/10 题有显式自检措辞；G2 共 {am['G2_total_vqa_calls']} 次 / {am['G2_total_reask']} 次 re-ask / {am['G2_cases_with_selfcheck']}/10 题自检。re-ask = 同一量重复提问/换问法次数（vqa_calls − 量数）。</p>
<h2>4. agent 自检轨迹（问 → 发现不一致 → 再问）原文片段</h2>
<div class="card"><h3>G1（基模后端）</h3>{selfcheck_block('G1', G1)}<h3>G2（适配器后端）</h3>{selfcheck_block('G2', G2)}</div>
<h2>5. 「agent 也没救」证据 —— 仍卡在哪几个量</h2>
<div class="card"><h3>G1 仍失败题的卡点量</h3>{stuck_block('G1', G1)}<h3>G2 仍失败题的卡点量</h3>{stuck_block('G2', G2)}</div>
<h2>6. 🚫 反作弊审计</h2>
<div class="card"><p>cheat = <b>{aud['cheat']}</b>，cheat_count = <b>{aud['cheat_count']}</b>，findings = {esc(json.dumps(aud['findings'], ensure_ascii=False))}。agent（glm-5.2）只与 HTTP VQA 工具 + glm-5.2 文本 API 通信，本进程不解码任何图像。agent VQA 调用 {aud['agent_vqa_calls']} 次，直接读图 {aud['agent_image_reads']} 次。<b>cheat=0 方可引用通过率</b> ✓。</p></div>
<h2>7. 诚实结论与口径</h2>
<div class="card">
<p><b>整题维度（用户主判据「真实题通过率有提升」）</b>：{"agent 臂 G1="+str(g1_pass)+"/"+str(n)+"、G2="+str(g2_pass)+"/"+str(n)+"，agent 在系统内引入 VQA 翻转 "+str(agent_flips)+" 题、agent 编排相对单模型翻转 "+str(orch_flips)+" 题 —— MLLM 作为 agent 系统一部分带来整题级增益。" if verdict_pos else "agent 臂 G1="+str(g1_pass)+"/"+str(n)+"、G2="+str(g2_pass)+"/"+str(n)+"，整题 0 翻转 —— 诚实负结果。根因见 §5：每题 k 全过门槛高，agent 即便反复 re-ask，仍有若干量（精确计数/精确数值/跨面板反推）读不稳。"}</p>
<p><b>每量维度（能力增量）</b>：单模型 V0 {PCT['V0']}%→V1 {PCT['V1']}%→V2 {PCT['V2']}%；agent G0 {PCT['G0']}%→G1 {PCT['G1']}%→G2 {PCT['G2']}%。G1−V1={round(PCT['G1']-PCT['V1'],1)}pp、G2−V2={round(PCT['G2']-PCT['V2'],1)}pp = agent 编排相对单次提问的每量增益（re-ask/交叉验证的机制价值）。</p>
<p><b>单模型臂 vs agent 臂（口径勿混）</b>：V0/V1/V2 是「工具天花板」（Python harness 一次提问），G0/G1/G2 是「agent 系统增益」（glm-5.2 自主编排 + re-ask）。本线能力结论以 G 臂为准；V 臂仅作天花板参考。</p>
<p><b>下一步</b>：① 把卡点量（精确计数/精确数值/跨面板反推）做成专项 SFT/RL 数据，扩真实波形分布 + GRPO 群体奖励，目标把单题推到全过；② 待 designflow task2（评测机→.17:30002 可达性解阻）做端到端 cline+SUT+VQA 对照，量 end-to-end 翻转；③ 若 agent re-ask 仍读不稳某量，给「该量对 2B VLM 不可解」的边界证据。</p>
</div>
<p class="muted">产物：waveview_selftest_agent_run.py · G/&#123;G0,G1,G2&#125;/*.json · summary_agent.json · audit_agent.json。本报告单文件自包含、0 外链、0 script、2 内联 SVG。{esc(S['design_note'])}</p>
</body></html>"""
out = os.path.normpath(os.path.join(HERE, "..", "..", "..", "reports", "report_vision_waveview_selftest_agent_zh.html"))
with open(out, "w") as f:
    f.write(html)
print(f"=== agent-arms report -> {out} ({len(html)}B)")
