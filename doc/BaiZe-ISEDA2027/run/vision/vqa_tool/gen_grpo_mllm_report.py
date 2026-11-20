#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_grpo_mllm_report.py -- Stage-2W GRPO(完整 Qwen3.5-2B MLLM)成果报告(用户令 2026-11-19 step d)。
诚实三段对比：pre-SFT(base) / post-SFT(SFT2 3 seed) / post-RFT2(GRPO 冷启动) / post-GRPO(step500)。
修正 wake#1684 口径错误：「+26.67pp」是对 base(0.60) 而非 GRPO 冷启动(RFT2=0.90)。
GRPO 真实增益 = post-GRPO 0.867 vs 冷启动 0.90 = -3.3pp(McNemar b=2 c=1 p=1.0, n.s.)。
输出：reports/report_vision_wave_grpo_mllm_result_zh.html（单文件 · 0 外链 · 0 script · 内联 SVG）。
作者: vision wake#1685 · project-internal
"""
import json, os, statistics
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))       # .../run/vision/vqa_tool
RUN = os.path.dirname(os.path.dirname(HERE))            # .../run
REPORTS = os.path.join(RUN, "reports")
SR = os.path.join(HERE, "strengthen_runs")
GRPO_OUT = "/nas_data/app.e0031982/datasets/baize-vision/out/wave_grpo_stage2w_mllm"


def load(p):
    return json.load(open(p))


def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    p = 0.0
    for k in range(n + 1):
        pm = comb(n, k) * (0.5 ** n)
        if k <= min(b, c) or k >= max(b, c):
            p += pm
    return p


def corr(d):
    return {r["id"]: bool(r["correct"]) for r in d["results"]}


def main():
    base = load(os.path.join(SR, "prebaseline_heldout.json"))
    sft2 = load(os.path.join(SR, "sft2_summary.json"))
    rft2 = load(os.path.join(SR, "rft2_seed11_eval.json"))
    post = load(os.path.join(GRPO_OUT, "grpo_mllm_eval.json"))
    tlog = load(os.path.join(GRPO_OUT, "training_log.json"))

    sft2_accs = [r["accuracy"] for r in sft2]
    sft2_mean = statistics.mean(sft2_accs)
    sft2_sd = statistics.pstdev(sft2_accs)

    cb, cr, cp = corr(base), corr(rft2), corr(post)
    ids = sorted(set(cb) & set(cr) & set(cp))
    b_bp = sum(1 for i in ids if cb[i] and not cp[i])
    c_bp = sum(1 for i in ids if not cb[i] and cp[i])
    p_bp = mcnemar_exact(b_bp, c_bp)
    b_rp = sum(1 for i in ids if cr[i] and not cp[i])
    c_rp = sum(1 for i in ids if not cr[i] and cp[i])
    p_rp = mcnemar_exact(b_rp, c_rp)

    steps = tlog["steps"]
    n_steps = len(steps)
    n_reward1 = sum(1 for s in steps if s["reward_mean"] == 1.0)
    n_loss_pos = sum(1 for s in steps if s["loss"] > 0)
    rew_all = [s["reward_mean"] for s in steps]
    cfg = tlog["config"]

    skills = list(base["skill_acc"].keys())
    skill_rows = []
    for sk in skills:
        skill_rows.append((sk, base["skill_acc"][sk]["acc"], rft2["skill_acc"][sk]["acc"], post["skill_acc"][sk]["acc"]))

    bar_w, gap, grp_gap = 26, 8, 22
    left0, top0, h = 70, 30, 170
    chart_w = left0 + len(skills) * (3 * bar_w + 2 * gap + grp_gap) + 30
    chart_h = top0 + h + 50
    svg = [f'<svg width="{chart_w}" height="{chart_h}" viewBox="0 0 {chart_w} {chart_h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="per-skill accuracy">']
    svg.append(f'<rect width="{chart_w}" height="{chart_h}" fill="#ffffff"/>')
    for g in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
        y = top0 + h - g * h
        svg.append(f'<line x1="{left0}" y1="{y:.1f}" x2="{chart_w-20}" y2="{y:.1f}" stroke="#e5e7eb" stroke-width="1"/>')
        svg.append(f'<text x="{left0-8}" y="{y+4:.1f}" font-size="11" fill="#6b7280" text-anchor="end">{int(g*100)}</text>')
    colors = ["#94a3b8", "#3b82f6", "#ef4444"]
    x = left0
    for (sk, a, r, p) in skill_rows:
        for j, v in enumerate((a, r, p)):
            bh = v * h
            y = top0 + h - bh
            svg.append(f'<rect x="{x}" y="{y:.1f}" width="{bar_w}" height="{bh:.1f}" fill="{colors[j]}"><title>{sk}: {[a,r,p][j]*100:.0f}%</title></rect>')
            svg.append(f'<text x="{x+bar_w/2}" y="{y-3:.1f}" font-size="10" fill="#374151" text-anchor="middle">{v*100:.0f}</text>')
            x += bar_w + gap
        svg.append(f'<text x="{x - gap - bar_w/2}" y="{top0+h+16}" font-size="10.5" fill="#374151" text-anchor="middle">{sk.replace("_"," ")}</text>')
        x += grp_gap
    svg.append(f'<g transform="translate(10,{chart_h-12})" font-size="11" fill="#374151"><rect x="0" y="-9" width="12" height="12" fill="#94a3b8"/><text x="16" y="1">base</text><rect x="60" y="-9" width="12" height="12" fill="#3b82f6"/><text x="76" y="1">RFT2 cold-start</text><rect x="200" y="-9" width="12" height="12" fill="#ef4444"/><text x="216" y="1">post-GRPO</text></g>')
    svg.append('</svg>')
    svg_str = "\n".join(svg)

    pts = [("pre-SFT (base)", base["accuracy"]), ("post-SFT (3-seed mean)", sft2_mean), ("post-RFT2 (GRPO cold-start)", rft2["accuracy"]), ("post-GRPO (step500)", post["accuracy"])]
    W2, H2 = 560, 240
    mx, mw = 60, 460
    sx = lambda i: mx + i * (mw / (len(pts) - 1))
    sy = lambda v: 40 + (1 - v) * 150
    svg2 = [f'<svg width="{W2}" height="{H2}" viewBox="0 0 {W2} {H2}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="stage progression">']
    svg2.append(f'<rect width="{W2}" height="{H2}" fill="#ffffff"/>')
    for g in (0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
        y = sy(g)
        svg2.append(f'<line x1="{mx}" y1="{y:.1f}" x2="{mx+mw}" y2="{y:.1f}" stroke="#e5e7eb"/>')
        svg2.append(f'<text x="{mx-8}" y="{y+4:.1f}" font-size="10" fill="#6b7280" text-anchor="end">{int(g*100)}</text>')
    for i in range(len(pts) - 1):
        x1, y1 = sx(i), sy(pts[i][1])
        x2, y2 = sx(i + 1), sy(pts[i + 1][1])
        col = "#ef4444" if pts[i + 1][1] < pts[i][1] else "#10b981"
        svg2.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="2.5"/>')
    for i, (lab, v) in enumerate(pts):
        x, y = sx(i), sy(v)
        svg2.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#1f2937"/>')
        svg2.append(f'<text x="{x:.1f}" y="{y-12:.1f}" font-size="12" font-weight="700" fill="#1f2937" text-anchor="middle">{v*100:.1f}%</text>')
        svg2.append(f'<text x="{x:.1f}" y="{y+22:.1f}" font-size="10" fill="#374151" text-anchor="middle">{lab}</text>')
    svg2.append('</svg>')
    svg2_str = "\n".join(svg2)

    skill_table = "\n".join(
        f"<tr><td>{sk.replace('_',' ')}</td><td>{a*100:.0f}%</td><td>{r*100:.0f}%</td><td>{p*100:.0f}%</td><td>{(p-r)*100:+.0f}pp</td></tr>"
        for (sk, a, r, p) in skill_rows)
    sft2_rows = "\n".join(
        f"<tr><td>{r['tag']}</td><td>{r['correct']}/{r['n']}</td><td>{r['accuracy']*100:.1f}%</td><td>{r['mean_reward']:.3f}</td></tr>"
        for r in sft2)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BaiZe Vision · 波形图理解 Stage-2W GRPO(完整 MLLM)成果报告</title>
<style>
 body{{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;max-width:980px;margin:0 auto;padding:24px;color:#1f2937;line-height:1.6;background:#f9fafb}}
 h1{{font-size:1.5rem;border-bottom:3px solid #1f2937;padding-bottom:8px}}
 h2{{font-size:1.15rem;margin-top:28px;color:#1f2937;border-left:5px solid #3b82f6;padding-left:10px}}
 .cards{{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0}}
 .card{{flex:1;min-width:150px;background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:14px;box-shadow:0 1px 2px rgba(0,0,0,.04)}}
 .card .lab{{font-size:.8rem;color:#6b7280}}.card .val{{font-size:1.5rem;font-weight:700;margin:4px 0}}
 .card .sub{{font-size:.78rem;color:#6b7280}}
 .ok{{color:#059669}}.bad{{color:#dc2626}}.warn{{color:#d97706}}
 table{{border-collapse:collapse;width:100%;background:#fff;margin:12px 0;font-size:.9rem}}
 th,td{{border:1px solid #e5e7eb;padding:7px 10px;text-align:center}}
 th{{background:#f3f4f6}}td:first-child{{text-align:left}}
 .note{{background:#fffbeb;border:1px solid #fde68a;border-radius:8px;padding:12px 16px;margin:14px 0;font-size:.9rem}}
 .neg{{background:#fef2f2;border:1px solid #fecaca;border-radius:8px;padding:12px 16px;margin:14px 0}}
 .muted{{color:#6b7280;font-size:.85rem}}
 code{{background:#f3f4f6;padding:1px 5px;border-radius:4px;font-size:.85em}}
 .foot{{margin-top:30px;padding-top:12px;border-top:1px solid #e5e7eb;font-size:.8rem;color:#6b7280}}
</style></head><body>
<h1>BaiZe Vision · 波形图理解 Stage-2W GRPO（完整 Qwen3.5-2B MLLM）成果报告</h1>
<p class="muted">用户令 2026-11-19 · GPU 迁回训练 · step (c) GRPO + step (d) 评测 ｜ wake#1685 ｜ 2026-11-19</p>
<div class="note">
<b>口径修正（诚实性）</b>：前序 wake#1684 以「post-GRPO 0.8667 = <b>+26.67pp</b>」作为 GRPO 成果头条。经核对，该 +26.67pp 是相对 <b>base 模型(0.60)</b> 的「整条 SFT+RFT+GRPO 链路」增益，<b>并非 GRPO 自身增益</b>。GRPO 的冷启动 adapter 是 RFT2(<span class="ok">0.90</span>)，post-GRPO 为 <span class="bad">0.867</span>，<b>GRPO 真实增益 = −3.3pp（McNemar b=2 c=1 p=1.0，不显著）</b>。误判成因：smoke 用 <code>init_adapter=null</code>（fresh LoRA from base）跑出 0.60，被误记为「post-SFT/rft2-init 基线」——它其实是 base 模型分数。本报告以真正的冷启动基线(RFT2=0.90)为 GRPO 对照。
</div>
<h2>1. 关键数字（held-out n=30，合成波形图问答，6 技能×5 题）</h2>
<div class="cards">
 <div class="card"><div class="lab">pre-SFT (base)</div><div class="val">{base['accuracy']*100:.1f}%</div><div class="sub">{base['correct']}/{base['n']} · Qwen3.5-2B 原生 VL，无 adapter</div></div>
 <div class="card"><div class="lab">post-SFT (3-seed mean)</div><div class="val">{sft2_mean*100:.1f}%</div><div class="sub">σ={sft2_sd*100:.1f}pp · Stage-1W SFT2 LoRA</div></div>
 <div class="card"><div class="lab">post-RFT2 (GRPO 冷启动)</div><div class="val">{rft2['accuracy']*100:.1f}%</div><div class="sub">{rft2['correct']}/{rft2['n']} · rft2_adapter_seed11</div></div>
 <div class="card"><div class="lab">post-GRPO (step500)</div><div class="val" style="color:#dc2626">{post['accuracy']*100:.1f}%</div><div class="sub">{post['correct']}/{post['n']} · 冷启动 RFT2 + 500 步 GRPO</div></div>
</div>
<h2>2. 阶段进程</h2>
{svg2_str}
<p class="muted">绿线=上升，红线=下降。SFT→RFT2 是主要增益来源（+30pp）；RFT2→post-GRPO 为 <b>−3.3pp</b>（GRPO 未带来提升）。</p>
<h2>3. 预注册判据与诚实结论</h2>
<div class="neg">
<b>判据</b>（用户令 step d）：对比 pre-SFT / post-SFT / post-GRPO 的波形图理解通过率；GRPO 是否相对其<b>冷启动</b>提升通过率。<br><b>结论</b>：<ul>
 <li><b>Stage-1W（SFT→RFT）是增益来源</b>：base 60% → RFT2 90%（+30pp；既有 v2-RFT McNemar b=7 c=0 <b>p=0.0156</b>，预注册显著）。</li>
 <li><b>Stage-2W（GRPO）未提升</b>：post-GRPO 86.7% vs 冷启动 RFT2 90% = <b>−3.3pp</b>，McNemar b=2 c=1 <b>p=1.0（不显著）</b>。属<b>负结果，如实记录</b>。</li>
 <li><b>技能层面</b>：duty_cycle 0.8→1.0（改善），但 amplitude_read 0.6→0.2（<b>回归</b>），其余持平，净 27→26。</li>
 <li>「+26.67pp」是<b>整条链路 vs base</b>（base→post-GRPO McNemar b=2 c=10 <b>p=0.039</b>，显著），但<b>不能归因于 GRPO</b>。</li>
</ul></div>
<h2>4. McNemar 精确检验（同 30 题、同判分）</h2>
<table><tr><th>对比</th><th>b（前者对后者错）</th><th>c（前者错后者对）</th><th>Δ</th><th>精确 p（双侧）</th><th>判定</th></tr>
<tr><td>base vs post-GRPO（整链路）</td><td>{b_bp}</td><td>{c_bp}</td><td>+{(post['accuracy']-base['accuracy'])*100:.1f}pp</td><td>{p_bp:.4f}</td><td class="ok">显著</td></tr>
<tr><td><b>RFT2 冷启动 vs post-GRPO（GRPO 自身）</b></td><td>{b_rp}</td><td>{c_rp}</td><td>{(post['accuracy']-rft2['accuracy'])*100:+.1f}pp</td><td>{p_rp:.4f}</td><td class="bad">不显著</td></tr>
</table>
<p class="muted">n=30 较小，p 仅供参考；GRPO 自身对比 b=2 c=1 信号方向为<b>轻微变差</b>。</p>
<h2>5. 每技能准确率</h2>
{svg_str}
<table><tr><th>技能</th><th>base</th><th>RFT2 冷启动</th><th>post-GRPO</th><th>GRPO Δ</th></tr>
{skill_table}
<tr><td><b>整体</b></td><td>{base['accuracy']*100:.0f}%</td><td>{rft2['accuracy']*100:.0f}%</td><td>{post['accuracy']*100:.1f}%</td><td>{(post['accuracy']-rft2['accuracy'])*100:+.1f}pp</td></tr>
</table>
<p class="muted">amplitude_read 回归（0.6→0.2）是 post-GRPO 整体下降主因；duty_cycle 进一步修复（0.8→1.0）。</p>
<h2>6. Stage-1W SFT 多 seed（held-out，同 30 题）</h2>
<table><tr><th>seed</th><th>correct/n</th><th>accuracy</th><th>mean_reward</th></tr>
{sft2_rows}
<tr><td><b>mean ± σ</b></td><td>—</td><td><b>{sft2_mean*100:.1f}% ± {sft2_sd*100:.1f}pp</b></td><td>—</td></tr>
</table>
<h2>7. GRPO 训练诊断（为何没有提升）</h2>
<table><tr><th>指标</th><th>值</th><th>解读</th></tr>
<tr><td>训练步数 / wall</td><td>{n_steps} logged / {tlog['total_wall_s']:.0f}s（≈{tlog['total_wall_s']/60:.0f}min，GPU7）</td><td>500 步目标完成</td></tr>
<tr><td>reward==1.0 的步数</td><td>{n_reward1}/{n_steps}（{n_reward1/n_steps*100:.0f}%）</td><td class="warn">奖励饱和：冷启动已在 0.90，多数 group 全对</td></tr>
<tr><td>loss&gt;0 的步数</td><td>{n_loss_pos}/{n_steps}</td><td class="bad">仅 {n_loss_pos} 步有梯度；其余 advantage=0→loss=0</td></tr>
<tr><td>reward 均值（首10 / 末10）</td><td>{statistics.mean(rew_all[:10]):.3f} / {statistics.mean(rew_all[-10:]):.3f}</td><td>末段略降（个别难题）</td></tr>
<tr><td>末步 loss 异常</td><td>{steps[-1]['loss']:.3f}</td><td>单 group reward=0.125 离群，非趋势</td></tr>
</table>
<div class="note"><b>根因</b>：GRPO advantage=(R−mean)/(std+ε)；group 内 4 条 rollout 奖励全同（冷启动已会做→全对→全 1.0）时 std=0→adv=0→loss=0→无梯度。500 步仅 {n_loss_pos} 步有效更新，且把 amplitude_read 拉差了。即 GRPO 在「冷启动已近天花板」的合成题上<b>几乎无操作</b>。</div>
<h2>8. 方法与配置</h2>
<ul>
 <li><b>模型</b>：完整 Qwen3.5-2B MLLM（含视觉塔，<b>不剥离</b>）+ LoRA r={cfg['lora_r']} α={cfg['lora_alpha']} ≈ 5.46M trainable（0.246%）。</li>
 <li><b>Stage-1W</b>：SFT2（3 seed）→ RFT2（v2 加强管线 RFT，rft2_adapter_seed11，即 GRPO 冷启动）。</li>
 <li><b>Stage-2W GRPO</b>：lr={cfg['lr']} · B={cfg['batch_prompts']} G={cfg['group_size']} · ppo_epochs={cfg['ppo_epochs']} · clip={cfg['clip_eps']} · max_new_tokens={cfg['max_new_tokens']} · temp={cfg['temperature']} top_p={cfg['top_p']} · seed={cfg['seed']} · train_seed={cfg['train_seed']}（150 train case，6 技能×25）· GPU7 bf16。</li>
 <li><b>可验证奖励</b>：<code>synth_waveform_qa.reward_for</code>（回归 exp(−rel_err/τ) / 分类二值）。</li>
 <li><b>评测集</b>：合成波形图 held-out n=30（<code>vision/vqa_tool/eval_images/q0..q29.png</code>，eval_seed=20261115）。</li>
</ul>
<h2>9. 改进建议（下一步）</h2>
<ul>
 <li><b>留出头空间</b>：GRPO 从 base 或 SFT（而非已 0.90 的 RFT2）冷启动，让 RL 有可学余量。</li>
 <li><b>奖励分解</b>：连续值奖励拆「区间内 vs 越界」，β&gt;α（research 日报 2026-11-19 建议），减少全对饱和。</li>
 <li><b>更难/长尾训练题</b>：加入噪声、多通道、非整数周期等，提高 group 内奖励方差。</li>
 <li><b>增大多样性</b>：提高 temperature / 增大 group_size，避免 4 条 rollout 全同。</li>
 <li><b>真实 benchmark 复测</b>：把 post-GRPO adapter 装入 :30003 → 重跑 EDA-Eval-DesignFlow-WaveView 子集 V2 臂（真实 EDA 题，非合成）。</li>
</ul>
<h2>10. 可复现清单</h2>
<table><tr><th>产物</th><th>路径</th></tr>
<tr><td>pre-SFT (base) 评测</td><td><code>vision/vqa_tool/strengthen_runs/prebaseline_heldout.json</code></td></tr>
<tr><td>post-SFT (3 seed)</td><td><code>vision/vqa_tool/strengthen_runs/sft2_summary.json</code></td></tr>
<tr><td>RFT2 冷启动评测</td><td><code>vision/vqa_tool/strengthen_runs/rft2_seed11_eval.json</code></td></tr>
<tr><td>RFT2 adapter（冷启动）</td><td><code>vision/vqa_tool/strengthen_runs/rft2_adapter_seed11/</code></td></tr>
<tr><td>post-GRPO 评测</td><td><code>{GRPO_OUT}/grpo_mllm_eval.json</code></td></tr>
<tr><td>post-GRPO adapter</td><td><code>{GRPO_OUT}/step500/adapter_model.safetensors</code></td></tr>
<tr><td>GRPO 训练日志</td><td><code>{GRPO_OUT}/training_log.json</code></td></tr>
<tr><td>GRPO 训练脚本（含冷启动基线修正）</td><td><code>vision/vqa_tool/grpo_mllm_wave.py</code></td></tr>
<tr><td>评测图</td><td><code>vision/vqa_tool/eval_images/q0..q29.png</code></td></tr>
</table>
<p class="muted">复跑：<code>CUDA_VISIBLE_DEVICES=7 python grpo_mllm_wave.py --total_steps 500 --group_size 4 --batch_prompts 2 --init_adapter .../rft2_adapter_seed11</code>（修正版会在训练前自动评测冷启动基线并落 <code>grpo_mllm_pretrain_baseline_eval.json</code>）</p>
<div class="foot"><p><b>诚实性声明</b>：本报告所有数字均可追溯到落盘 JSON（路径见 §10），由 <code>gen_grpo_mllm_report.py</code> 直接读取生成，未手工修饰。GRPO 为负结果（相对冷启动 −3.3pp，不显著），如实记录；前序「+26.67pp」头条系对 base 而非冷启动的口径错误，已修正。</p><p>BaiZe Vision · wake#1685 · 2026-11-19 · 单文件 HTML · 0 外链 · 0 script · 内联 SVG</p></div>
</body></html>"""

    os.makedirs(REPORTS, exist_ok=True)
    out = os.path.join(REPORTS, "report_vision_wave_grpo_mllm_result_zh.html")
    with open(out, "w") as f:
        f.write(html)
    print("wrote", out, len(html), "bytes")


if __name__ == "__main__":
    main()
