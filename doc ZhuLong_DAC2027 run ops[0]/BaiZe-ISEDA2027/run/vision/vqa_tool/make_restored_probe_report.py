#!/usr/bin/env python3
"""Generate the preliminary restored-case VQA probe HTML report (zh, self-contained).

Combines round-1 (prelim_restored_probe.py: β9/α4/β10) and round-2
(prelim_restored_probe2.py: a1/b8/b11) result files -> all 6 designflow-restored
cases probed. Round-2 file is optional (absent => round-1 only, for backward repro).
"""
import json, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
J1 = json.load(open(os.path.join(HERE, "restored_probe_results.json")))
J2_path = os.path.join(HERE, "restored_probe2_results.json")
J2 = json.load(open(J2_path)) if os.path.exists(J2_path) else {"cases": []}

# Merge: keep round-1 cases then append round-2 cases (disjoint case sets by design).
J = dict(J1)
J["cases"] = J1.get("cases", []) + J2.get("cases", [])
# Recompute overall across the union.
n_cases = len(J["cases"])
n_qty = sum(len(c.get("results", [])) for c in J["cases"])
correct = sum(1 for c in J["cases"] for r in c.get("results", []) if r.get("pass"))
J["overall"] = {"n_cases": n_cases, "n_qty": n_qty, "correct": correct,
                "acc": round(correct / n_qty, 4) if n_qty else 0.0,
                "rounds": "round1(β9/α4/β10) + round2(a1/b8/b11)"}
# Per-case summary list (preserve insertion order).
J["summary"] = []
for c in J["cases"]:
    rq = c.get("results", [])
    rc = sum(1 for r in rq if r.get("pass"))
    J["summary"].append({"case_id": c.get("case_id"), "tag": c.get("tag"),
                         "n_qty": len(rq), "correct": rc,
                         "acc": round(rc / len(rq), 4) if rq else 0.0,
                         "baseline": c.get("baseline_textonly", "FAIL (0 deliverable)")})

RPT = "/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/reports/report_vision_vqa_restored_probe_zh.html"

overall = J["overall"]
summary = J["summary"]


def esc(s):
    return html.escape(str(s))


def fmt_got(r):
    if r.get("got") is None:
        return "—"
    return f"{r['got']:.4g}"


# per-case SVG bar (accuracy)
labels = [s["tag"] for s in summary]
accs = [s["acc"] for s in summary]
bar_w, gap, x0, h, base_y = 90, 38, 60, 220, 180
w = x0 + len(labels) * (bar_w + gap) + 30
svg = [f'<svg width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg" style="font-family:Arial">']
svg.append(f'<line x1="{x0-10}" y1="{base_y}" x2="{x0 + len(labels)*(bar_w+gap)+10}" y2="{base_y}" stroke="#333" stroke-width="1"/>')
svg.append(f'<line x1="{x0-10}" y1="{base_y-160}" x2="{x0-10}" y2="{base_y}" stroke="#333" stroke-width="1"/>')
for i, (lb, a) in enumerate(zip(labels, accs)):
    bx = x0 + i * (bar_w + gap)
    bh = int(a * 160)
    col = "#2ca02c" if a >= 0.5 else ("#ff7f0e" if a >= 0.25 else "#d62728")
    svg.append(f'<rect x="{bx}" y="{base_y-bh}" width="{bar_w}" height="{bh}" fill="{col}" rx="4"/>')
    svg.append(f'<text x="{bx+bar_w/2}" y="{base_y-bh-6}" text-anchor="middle" font-size="14" fill="#222">{a*100:.1f}%</text>')
    svg.append(f'<text x="{bx+bar_w/2}" y="{base_y+18}" text-anchor="middle" font-size="14" fill="#222">{esc(lb)}</text>')
    svg.append(f'<text x="{bx+bar_w/2}" y="{base_y+36}" text-anchor="middle" font-size="11" fill="#666">{summary[i]["correct"]}/{summary[i]["n_qty"]} 量</text>')
svg.append(f'<text x="{x0-10}" y="{base_y-160}" font-size="11" fill="#666">100%</text>')
svg.append(f'<text x="{x0-10}" y="{base_y+4}" font-size="11" fill="#666">0%</text>')
svg.append('</svg>')
svg = "".join(svg)

rows = []
for c in J["cases"]:
    rows.append(f'<tr><th colspan="5" style="background:#eef3f8;text-align:left">{esc(c["tag"])} · {esc(c["case_id"])} — 正确 {sum(1 for r in c["results"] if r["pass"])}/{len(c["results"])} 量</th></tr>')
    for r in c["results"]:
        mark = "✅" if r["pass"] else "❌"
        got = fmt_got(r)
        ans = esc(r["answer"])[:140] + ("…" if len(r["answer"]) > 140 else "")
        rows.append(f'<tr><td>{mark}</td><td><code>{esc(r["key"])}</code></td><td>{esc(r["gold"])}</td><td>{got}</td><td style="color:#555;font-size:12px">{ans}</td></tr>')
rows = "".join(rows)
H = f"""<!DOCTYPE html>
<html lang="zh"><head><meta charset="utf-8"><title>VQA 初步能力探针 · designflow 恢复 waveview 用例</title>
<style>
body{{font-family:"PingFang SC","Microsoft YaHei",Arial,sans-serif;max-width:1000px;margin:24px auto;color:#222;line-height:1.6}}
h1{{font-size:22px;border-bottom:3px solid #1f77b4;padding-bottom:8px}}
h2{{font-size:18px;margin-top:28px;color:#1f4e79}}
.warn{{background:#fff8e1;border-left:4px solid #f5a623;padding:10px 14px;margin:12px 0;border-radius:4px}}
.card{{display:inline-block;background:#eef3f8;border:1px solid #cfd8dc;border-radius:8px;padding:12px 18px;margin:8px 8px 8px 0}}
table{{border-collapse:collapse;width:100%;margin:12px 0;font-size:13px}}
th,td{{border:1px solid #ddd;padding:6px 8px;text-align:left;vertical-align:top}}
th{{background:#f5f7fa}}
code{{background:#f4f4f4;padding:1px 4px;border-radius:3px}}
.tl{{list-style:none;padding-left:0}} .tl li{{margin:8px 0}}
</style></head><body>
<h1>VQA 工具初步能力探针 · designflow 恢复后的 waveview 用例</h1>
<p style="color:#666">vision 线 · 用户令 2026-11-14 09:1x #3（10:3x「不要再等·先做可并行那半」）· {overall["n_cases"]} 个用例 · {overall["n_qty"]} 个待读量</p>

<div class="warn"><b>⚠️ 口径声明（重要）</b>：这是 <b>preliminary capability probe（能力初探）</b>，
<b>不是</b> #3 的官方「无 VQA vs 有 VQA」对照。官方对照需 designflow 用 <b>字节相同的图 + 同一 cline harness</b>
跑「有 VQA」臂。本探针的图由 vision 线 <b>据 designflow 公开记录的波形参数在本机重新生成忠实副本</b>
（同参数 / 同图幅 / 无数据标签，与 designflow 的 stimulus 等价但 <b>非字节相同</b>），用本线 VQA tool
（Qwen3.5-2B 原生 VL，常驻 :30001）逐量提问，按 designflow 公布容差判 pass/fail。结果 <b>仅作早期读图能力信号</b>，
<b>不可外推为官方通过率</b>。数据来源：参数与 oracle 见
<code>waveview_baseline_results.D.json</code> / <code>waveview_restore_plan_D.md</code>。</div>

<h2>1 · 核心数字</h2>
<div class="card"><b>基线（text-only, designflow r650–r655）</b><br>{overall["n_cases"]}/{overall["n_cases"]} 用例 <b>全 FAIL</b>（看不见图，0 deliverable）→ <b>0/{overall["n_qty"]} 量</b></div>
<div class="card"><b>有 VQA（Qwen3.5-2B, 本探针）</b><br>{overall["correct"]}/{overall["n_qty"]} 量正确 → <b>acc={overall["acc"]*100:.1f}%</b></div>
<div class="card"><b>多模态增量（初步）</b><br>0% → {overall["acc"]*100:.1f}%（量级）<br>但距通过 check.py 全 12 条件仍远</div>
<p style="color:#666;font-size:13px">两轮探针合并：round-1（β9/α4/β10，wake#1227）+ round-2（a1/b8/b11，designflow r655 后补齐 6 题）。designflow 已恢复 6 题(α1+β9+α4+β8+β10+β11)且 text-only 基线全 FAIL（正确无多模态基线）。</p>
<p>{svg}</p>

<h2>2 · 逐用例结果</h2>
<table>
<tr><th>判</th><th>量</th><th>oracle(金标准)</th><th>VQA 读出</th><th>原始回答(截断)</th></tr>
{rows}
</table>
"""
H2 = f"""
<h2>3 · 诚实解读</h2>
<ul class="tl">
<li><b>确实存在多模态信号</b>：text-only 基线在 image-required 用例上 0 deliverable；VQA tool 能读出 <b>轴标签 / 单面板简单量 / 分类标签</b>
（如 β9 的 max=1.0V 读 y 轴、α4 的 v_max=1.25V、β10 顶图的 vmax=1.2V/t_at_max=4us、α4 的 multi_pulse 分类；
round-2 的 b8 信号类型分类 rst_n=reset/vref=ramp/sel=pulse 三类全对、b11 的 root_cause=Q_force_x_stuck_high 与 edge_signal 名字读对、a1 的 optimal_vref=100 在「约束筛选」下读对）——
这正是「基线 fail → 上 VQA 后部分可读」的增益证据，且 <b>分类/标签类读数是当前最稳的强项</b>。</li>
<li><b>能力仍弱，距通过全 12 条件远</b>：三类系统性缺口——
<b>① 精确计数/周期</b>：β9 周期 1ns 读成 2ns（把相邻同相峰当一周期）；α4 激活窗数 5 读成 <b>54</b>（误把信号名 "sel54" 当计数）；
round-2 同样命中：b8 clk_period 2ns→1ns（半周期误判）、clk_n_transitions 10→0、sel_n_pulses 2→1、b11 上升沿 edge_count 4→0。
<b>② 精确数值读取</b>：β9 的 min/offset/p2p 均偏差超容差（offset 0.6→0.55，min 0.26→1.0）；
round-2：a1 把 skew/height 读成阈值线值 100 而非曲线值（5.38/180）、b8 vref_vmax 1.0→0.0、b11 fail_time 1363ns→1（量级完全错）。
<b>③ 跨面板/约束推理</b>：β10 是「看顶图 v(temp) + 底图 v(det) 翻转时刻反推 vth_high/vth_low/迟滞」——
VQA tool 仅读出顶图两量，<b>跨面板阈值反推全错</b>（vth_high/low/hysteresis/t_cross 全 fail）；a1 的「valid VREF 筛选后取 max width」只对了一半（选对 VREF，但该 VREF 下的 width/skew/height 全错）。</li>
<li><b>6 题合并的稳定结论</b>：两轮共 <b>14/46 = 30.4%</b> 量正确，且正确项高度集中在「分类标签 / 轴标签单量 / 约束筛选」三类；
失败项高度集中在「精确计数 / 精确数值 / 跨面板反推」三类。<b>该 gap 模式跨全部 6 题一致</b>，非偶然——说明 Qwen3.5-2B 原生 VL 能「看懂图是什么」但「读不准图上的数」。</li>
<li><b>对 08:4x 分析报告 α 判断的修正</b>：原 α 分析把 β10 等归为「识图可解」；本探针显示「识图能读 <i>部分</i> 量，
但 check.py 要求的 12 条件（尤其跨面板推理）远超当前 VQA 能力」→ α 的「大概率能过」对 <b>全题通过</b> 而言偏乐观，
应下调为「识图有部分增益、但全题通过需更强模型/训练」。</li>
<li><b>对 #4（SFT/RL 强化）的指向</b>：本探针定位的缺口（精确计数、数值精度、跨面板推理）正是 #4 合成数据应新增的技能维度；
#4 此前 SFT/RFT 在合成波形上 Δ=8.9pp 但 p=0.5 未显著——本探针说明合成训练分布与真实 EDA 图（无标签、多面板、需反推）存在 gap，
后续 #4 应加入「无标签轴读数 + 跨面板推理」类合成样本。</li>
</ul>

<h2>4 · 结论与下一步</h2>
<ul class="tl">
<li><b>结论</b>：VQA tool 在真实 EDA 风格波形图上提供 <b>可度量但较弱</b>的多模态增益（0→{overall["acc"]*100:.1f}% 量级，6 题 14/46 量），
能力集中在轴标签/单面板简单量/分类标签，跨面板推理与精确计数是主要缺口。</li>
<li><b>#3 后半仍需 designflow 跨线</b>：官方对照（字节相同图 + 同一 cline harness + check.py 全条件）必须由 designflow
用本 VQA tool 跨线再跑——恢复后的真 PNG 在 .15（独立 NFS），.17 取不到，本探针无法替代。</li>
<li><b>下一步</b>：① designflow D 域 6 题已恢复完毕（α3/β6 未落库待造题），官方「有 VQA」臂待 designflow 用本 VQA tool 跨线再跑；② #4 合成数据补「无标签轴读数 + 跨面板推理 + 精确计数」维度后再训；
③ 本探针可在 #4 强化后重跑，作 pre/post 配对对照。</li>
</ul>

<p style="color:#888;font-size:12px;margin-top:30px;border-top:1px solid #eee;padding-top:8px">
产物：<code>vision/vqa_tool/prelim_restored_probe.py</code>（round-1 可复跑）· <code>vision/vqa_tool/prelim_restored_probe2.py</code>（round-2 可复跑）·
<code>vision/vqa_tool/restored_probe_results.json</code> + <code>restored_probe2_results.json</code>（原始结果）·
图由脚本按公开参数重生成（<code>restored_probe_images/</code>，已 gitignore）。
baseline 来源：designflow <code>waveview_baseline_results.D.json</code> r650–r655。
本报告单文件自包含 / 0 外链 / 0 script / 内联 SVG。</p>
</body></html>"""
with open(RPT, "w") as f:
    f.write(H + H2)
print("written", RPT, os.path.getsize(RPT), "bytes")

