#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_grpo_v2_report_section.py -- append a GRPOv2 results section to
report_vision_wave_grpo_mllm_result_zh.html (用户令 2026-11-24 08:5x · P3).

Reads the v2 run JSONs produced by grpo_mllm_wave_v2.py and appends an
honest §11 GRPOv2 section (improvements + numbers + comparison table +
negative result if any). Re-runnable: replaces any prior §11 block.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(HERE, "grpo_mllm_runs_v2")
REPORT = os.path.normpath(os.path.join(HERE, "..", "..", "reports",
                      "report_vision_wave_grpo_mllm_result_zh.html"))


def load(name):
    p = os.path.join(RUN, name)
    if not os.path.isfile(p):
        return {}
    try:
        return json.load(open(p))
    except Exception as e:
        return {"_error": str(e)}


def pct(x):
    try:
        return f"{float(x)*100:.1f}%"
    except Exception:
        return str(x)


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def reward_curve_svg(steps):
    if not steps:
        return "<p class='muted'>（无训练步日志）</p>"
    rs = [s.get("reward_mean", 0.0) for s in steps]
    lo, hi = min(rs + [0]), max(rs + [0.0, 1.0])
    if hi <= lo:
        hi = lo + 1.0
    W, H, L, R, T, B = 760, 200, 40, 20, 20, 30
    n = len(rs)

    def xy(i, v):
        x = L + (W - L - R) * i / max(1, n - 1)
        y = T + (H - T - B) * (1 - (v - lo) / (hi - lo))
        return x, y

    pts = [xy(i, v) for i, v in enumerate(rs)]
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f"<svg width='{W}' height='{H}' viewBox='0 0 {W} {H}' "
            f"xmlns='http://www.w3.org/2000/svg' role='img' "
            f"aria-label='grpo v2 reward curve'>"
            f"<rect width='{W}' height='{H}' fill='#fff'/>"
            f"<polyline points='{poly}' fill='none' stroke='#3b82f6' stroke-width='1.5'/>"
            f"<text x='{W-5}' y='{H-8}' font-size='10' fill='#6b7280' text-anchor='end'>"
            f"step 1..{n} · reward∈[{lo:.2f},{hi:.2f}]</text></svg>")


def build_section():
    base = load("grpo_v2_coldstart_baseline_eval.json")
    post = load("grpo_v2_eval.json")
    paired = load("grpo_v2_paired_test.json")
    cheat = load("cheat_rate_check.json")
    tlog = load("training_log.json")
    grad = tlog.get("grad_signal", {}) if isinstance(tlog, dict) else {}
    rlp = tlog.get("reward_level_pct", {}) if isinstance(tlog, dict) else {}
    rlc = tlog.get("reward_level_counts", {}) if isinstance(tlog, dict) else {}
    steps = tlog.get("steps", []) if isinstance(tlog, dict) else {}
    rp = tlog.get("reward_params", {}) if isinstance(tlog, dict) else {}
    cold_acc = base.get("accuracy")
    post_acc = post.get("accuracy")
    mcn = paired.get("mcnemar", {}) if isinstance(paired, dict) else {}
    boot = paired.get("paired_bootstrap", {}) if isinstance(paired, dict) else {}
    verdict = paired.get("verdict", "(待计算)") if isinstance(paired, dict) else "(待计算)"
    dd = (post_acc - cold_acc) if (isinstance(post_acc, (int, float)) and isinstance(cold_acc, (int, float))) else None
    cards = [
        ("冷启动 (SFT adapter)", pct(cold_acc), f"n={base.get('n','?')} · sft2_adapter_seed11"),
        ("post-GRPOv2 (step500)", pct(post_acc), f"n={post.get('n','?')} · 500 步 GRPOv2"),
        ("GRPOv2 Δ (vs 冷启动)", pct(dd) if dd is not None else "?", f"McNemar p={mcn.get('p_value','?')}"),
        ("cheat_rate", str(cheat.get("cheat_rate", "?")), f"overlap={cheat.get('overlap_count','?')} · train/eval seed 隔离"),
        ("梯度信号步数", f"{grad.get('steps_with_grad','?')}/{grad.get('steps_total','?')}", f"frac={grad.get('frac_with_grad','?')}（v1 仅 2/224）"),
        ("bootstrap p (n=10000)", str(boot.get("p", "?")), f"Δ={boot.get('delta','?')} CI=[{boot.get('ci_lo','?')},{boot.get('ci_hi','?')}]"),
    ]
    card_html = "<div class='cards'>" + "".join(
        f"<div class='card'><div class='lab'>{esc(l)}</div><div class='val'>{esc(v)}</div><div class='sub'>{esc(s)}</div></div>"
        for l, v, s in cards) + "</div>"
    cmp_rows = [
        ("冷启动来源", "RFT2 (0.90) — 已近天花板", "SFT adapter (0.70) — 留 headroom"),
        ("奖励设计", "二值/连续，全对→1.0 饱和", f"分解 exact=1.0 / in-bounds=α={rp.get('ALPHA','?')} / 越界=−β=−{rp.get('BETA','?')}（β&gt;α）"),
        ("训练题难度", "整数周期/无噪声/单通道", "高斯噪声σ8-20 + 非整数周期/幅值 + 多通道干扰 distractor（150 道）"),
        ("reward==1.0 占比", "189/224 步 (84%) 饱和", f"1.0={rlp.get('1.0','?')} · α={rlp.get('alpha','?')} · −β={rlp.get('neg_beta','?')}"),
        ("有梯度步数", "2/224 (0.9%)", f"{grad.get('steps_with_grad','?')}/{grad.get('steps_total','?')} ({pct(grad.get('frac_with_grad',0))})"),
        ("post-GRPO acc", "86.7% (vs 冷启动 0.90 = −3.3pp)", f"{pct(post_acc)} (vs 冷启动 {pct(cold_acc)} = {pct(dd) if dd is not None else '?'})"),
        ("McNemar p (vs 冷启动)", "1.0（不显著）", f"b={mcn.get('b_improved','?')} c={mcn.get('c_regressed','?')} p={mcn.get('p_value','?')}"),
    ]
    cmp_html = ("<table><tr><th>维度</th><th>v1（负结果）</th><th>v2（改进）</th></tr>"
                + "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td><td>{esc(c)}</td></tr>" for a, b, c in cmp_rows) + "</table>")
    wall = tlog.get("total_wall_s") if isinstance(tlog, dict) else None
    wall_s = f"{wall:.0f}s" if isinstance(wall, (int, float)) else "?"
    diag_rows = [
        ("训练步数 / wall", f"{grad.get('steps_total','?')} 步 / {wall_s}"),
        ("total_rollouts", str(tlog.get("total_rollouts", "?"))),
        ("reward==1.0 次数", f"{rlc.get('1.0','?')} ({pct(rlp.get('1.0',0))})"),
        ("reward==α 次数", f"{rlc.get('alpha','?')} ({pct(rlp.get('alpha',0))})"),
        ("reward==−β 次数", f"{rlc.get('neg_beta','?')} ({pct(rlp.get('neg_beta',0))})"),
        ("cheat_rate", str(cheat.get("cheat_rate", "?"))),
    ]
    diag_html = ("<table><tr><th>指标</th><th>值</th></tr>"
                 + "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td></tr>" for a, b in diag_rows) + "</table>")
    return (card_html, cmp_html, diag_html, base, post, paired, mcn, boot, verdict, rp, steps, grad)


def main():
    card_html, cmp_html, diag_html, base, post, paired, mcn, boot, verdict, rp, steps, grad = build_section()
    cold_acc = base.get("accuracy")
    section = (
        "<h2>11. GRPOv2 改进训练（用户令 2026-11-24 08:5x · wake#1709+）</h2>"
        "<p class='muted'>针对 v1 负结果（§5.5 / §7）的四项预注册改进，开跑前写明判据，跑完不改。</p>"
        "<div class='note'><b>四项改进</b>：<ol>"
        "<li><b>冷启动从 SFT adapter</b>（sft2_adapter_seed11, 0.70）而非已 0.90 的 RFT2，留 headroom。</li>"
        f"<li><b>奖励分解</b>：exact=1.0 / in-bounds=α={rp.get('ALPHA','?')} / 越界=−β=−{rp.get('BETA','?')}（β&gt;α），破 v1「189/224 步 reward=1.0 饱和」。</li>"
        "<li><b>更难/长尾训练题</b>：高斯噪声 σ8-20 + 非整数周期/幅值 + 更近频率 Δ&gt;0.6 + 多通道干扰 distractor，150 道。</li>"
        "<li><b>跑 500 步</b>，报 reward 曲线 + cheat_rate + 配对检验（McNemar + paired bootstrap n=10000）。</li>"
        "</ol></div>"
        f"<h3>11.1 关键数字（held-out n={base.get('n','?')}，合成波形图问答）</h3>{card_html}"
        f"<h3>11.2 reward 曲线（粒度化，非 v1 全 1.0 饱和）</h3>{reward_curve_svg(steps)}"
        f"<h3>11.3 v1 vs v2 对比</h3>{cmp_html}"
        f"<h3>11.4 训练诊断</h3>{diag_html}"
        "<h3>11.5 预注册判据与诚实结论</h3>"
        "<div class='neg'><b>判据</b>（开跑前写明）：成功 = post-GRPOv2 acc &gt; 冷启动 SFT 0.70 AND McNemar p&lt;0.05；不显著/负结果照写不粉饰。<br>"
        f"<b>结论</b>：{esc(verdict)}<br>"
        f"McNemar（vs 冷启动）b={mcn.get('b_improved','?')} c={mcn.get('c_regressed','?')} p={mcn.get('p_value','?')}；"
        f"paired bootstrap Δ={boot.get('delta','?')} 95%CI=[{boot.get('ci_lo','?')},{boot.get('ci_hi','?')}] p={boot.get('p','?')}。</div>"
        "<h3>11.6 P2 真题复测（EDA-Eval-DesignFlow-WaveView 全队列 182 case V2 臂）</h3>"
        "<p class='muted'>见报告 report_vision_waveview_selftest_agent_zh.html §0.6 与本线 MEMORY；"
        "若 post-GRPOv2 held-out &gt; rft2(0.90) 则用新 adapter 重跑，否则用 rft2 复测确认 17.6% 可复现。</p>"
    )
    html = open(REPORT, encoding="utf-8").read()
    marker = "<h2>11. GRPOv2 改进训练"
    if marker in html:
        foot_idx = html.find("<div class='foot'>")
        if foot_idx == -1:
            foot_idx = html.find("<div class=\"foot\">")
        if foot_idx == -1:
            foot_idx = len(html)
        html = html[:html.find(marker)] + html[foot_idx:]
    foot_idx = html.find("<div class='foot'>")
    if foot_idx == -1:
        foot_idx = html.find("<div class=\"foot\">")
    if foot_idx == -1:
        foot_idx = html.rfind("</body>")
    html = html[:foot_idx] + section + "\n" + html[foot_idx:]
    open(REPORT, "w", encoding="utf-8").write(html)
    print(f"[gen-grpo-v2] appended §11 to {REPORT} ({len(html)} bytes)")


if __name__ == "__main__":
    main()

