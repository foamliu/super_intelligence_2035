#!/usr/bin/env python3
"""baize_posttrain_campaign_projection.py — R65: 72h Surrogate RL Campaign
Step-Level Projection & Adaptive Stopping Boundaries.

Synthesizes R59 (GRPO dynamics MC sim), R61 (rollout throughput), R58 (prompt
pre-screen), and R64 (SFT->RL handoff) into a unified quantitative projection
for the 72-hour surrogate RL campaign starting 2026-11-09.

WARNING: Surrogate RL results (MiniCPM5-2B) are NOT transferable to BaiZe.
"""
from __future__ import annotations
import argparse, json, math, random, sys

# --- Configuration (sourced from R59/R61/R58/R64) ---

R59_ARMS = {
    "R0_skeleton":     {"initial_reward": 0.4500, "gain_200": 0.0050, "std_zero_final": 0.005, "cheat_rate": 0.0},
    "R1_binary":       {"initial_reward": 0.4642, "gain_200": 0.0033, "std_zero_final": 0.011, "cheat_rate": 0.0},
    "R2_partial":      {"initial_reward": 0.5274, "gain_200": -0.0038, "std_zero_final": 0.006, "cheat_rate": 0.0},
    "R3_tool_penalty": {"initial_reward": 0.4980, "gain_200": 0.0134, "std_zero_final": 0.0,   "cheat_rate": 0.0},
}
STEPS_PER_HR = 3.45
SMOKE_MINUTES = 37
TOTAL_PROMPTS = 3347
SIGNAL_PROMPTS = 2037
SFT_TO_RL_LR_RATIO = 0.1
MILESTONES = {
    "baseline": {"pass1": 0.36, "label": "MiniCPM5-2B 零适配起点"},
    "M1": {"pass1": 0.50, "label": "工具协议修好 (D1/D2/D6)"},
    "M2": {"pass1": 0.65, "label": "+ 领域继续预训练 + SFT"},
    "M3": {"pass1": 0.75, "label": "+ RL"},
    "M4": {"pass1": 0.85, "label": "逼近 DeepSeek-V4-Pro"},
}
TOTAL_BUDGET_HR = 72.0
PRE_RL_HR = 7.3
POST_RL_HR = 5.0
RL_BUDGET_HR = TOTAL_BUDGET_HR - PRE_RL_HR - POST_RL_HR
MAX_STEPS = int(RL_BUDGET_HR * STEPS_PER_HR)
TRANSFER_RATIO_INIT = 0.72
TRANSFER_RATIO_ASYMPTOTE = 0.90
TRANSFER_TAU = 120
MC_RUNS = 200
NOISE_STD = 0.008
RANDOM_SEED = 42
CHECKPOINTS = [25, 50, 100, 150, 200]

# --- Core Models ---

def reward_trajectory(arm_key, max_steps, mc_runs, seed):
    """Simulate step-level reward trajectories for one arm."""
    cfg = R59_ARMS[arm_key]
    r0 = cfg["initial_reward"]
    gain = cfg["gain_200"]
    gain_scaled = gain * (max_steps / 200.0) if max_steps != 200 else gain
    tau = 80.0
    noise = NOISE_STD
    rng = random.Random(seed)
    trajectories = []
    for _ in range(mc_runs):
        traj = []
        for t in range(1, max_steps + 1):
            expected = r0 + gain_scaled * (1.0 - math.exp(-t / tau))
            jitter = rng.gauss(0, noise)
            val = max(0.0, min(1.0, expected + jitter))
            traj.append(val)
        trajectories.append(traj)
    return trajectories

def transfer_function(training_reward, step):
    """Map training reward to eval Pass@1."""
    ratio = TRANSFER_RATIO_INIT + (TRANSFER_RATIO_ASYMPTOTE - TRANSFER_RATIO_INIT) * (1.0 - math.exp(-step / TRANSFER_TAU))
    return training_reward * ratio

def percentile(values, pct):
    if not values:
        return 0.0
    s = sorted(values)
    k = (len(s) - 1) * pct / 100.0
    f = int(k)
    c = min(f + 1, len(s) - 1)
    if f == c:
        return s[f]
    return s[f] + (s[c] - s[f]) * (k - f)

def compute_confidence_bands(trajectories):
    p5, p25, p50, p75, p95 = [], [], [], [], []
    for si in range(len(trajectories[0])):
        vals = [traj[si] for traj in trajectories]
        p5.append(percentile(vals, 5))
        p25.append(percentile(vals, 25))
        p50.append(percentile(vals, 50))
        p75.append(percentile(vals, 75))
        p95.append(percentile(vals, 95))
    return {"p5": p5, "p25": p25, "p50": p50, "p75": p75, "p95": p95}

def _first_cross(prob_by_step, threshold):
    for step_str in sorted(prob_by_step, key=int):
        if prob_by_step[step_str] >= threshold:
            return int(step_str)
    return -1

def milestone_crossing_probability(trajectories, milestones, max_steps):
    result = {}
    for ms_name, ms_info in milestones.items():
        target = ms_info["pass1"]
        prob_by_step = {}
        for si in range(max_steps):
            step = si + 1
            count_above = 0
            for traj in trajectories:
                eval_pass1 = transfer_function(traj[si], step)
                if eval_pass1 >= target:
                    count_above += 1
            prob_by_step[str(step)] = count_above / len(trajectories)
        result[ms_name] = {"target": target, "label": ms_info["label"],
                           "prob_by_step": prob_by_step,
                           "first_cross_50pct": _first_cross(prob_by_step, 0.50),
                           "first_cross_90pct": _first_cross(prob_by_step, 0.90)}
    return result

def _checkpoint_action(p5, p50, p95, step, p_reach_m1, sufficient):
    if sufficient:
        return "SUFFICIENT: eval Pass@1 P50 >= M1(50%). Can stop early."
    if p_reach_m1 < 0.05:
        return "FUTILE: P(reach M1 by end) < 5%. Stop RL, save ckpt, eval."
    if p_reach_m1 < 0.30:
        return "MARGINAL: P(reach M1)=%.0f%%. Continue but prepare contingency." % (p_reach_m1 * 100)
    if p5 < R59_ARMS["R3_tool_penalty"]["initial_reward"] - 0.02:
        return "DECLINING: P5 below initial. Check reward hacking."
    return "ON TRACK: P(reach M1)=%.0f%%. Continue RL." % (p_reach_m1 * 100)

def adaptive_stopping_boundaries(trajectories, checkpoints, max_steps):
    boundaries = []
    for cp in checkpoints:
        if cp > max_steps:
            continue
        si = cp - 1
        rewards_at_cp = [traj[si] for traj in trajectories]
        p5 = percentile(rewards_at_cp, 5)
        p50 = percentile(rewards_at_cp, 50)
        p95 = percentile(rewards_at_cp, 95)
        m1_target = MILESTONES["M1"]["pass1"]
        count_reach = 0; count_total = 0
        for traj in trajectories:
            r_cp = traj[si]
            if abs(r_cp - p50) < 2 * NOISE_STD:
                count_total += 1
                eval_final = transfer_function(traj[-1], max_steps)
                if eval_final >= m1_target:
                    count_reach += 1
        p_reach_m1 = count_reach / max(count_total, 1)
        futile_thr = R59_ARMS["R3_tool_penalty"]["initial_reward"] - 0.01
        eval_p50 = transfer_function(p50, cp)
        sufficient = eval_p50 >= m1_target
        boundaries.append({
            "step": cp, "wall_clock_hr": round(PRE_RL_HR + cp / STEPS_PER_HR, 1),
            "reward_p5": round(p5, 4), "reward_p50": round(p50, 4),
            "reward_p95": round(p95, 4), "eval_pass1_p50": round(eval_p50, 4),
            "p_reach_m1_by_end": round(p_reach_m1, 3),
            "futile": p5 < futile_thr, "sufficient": sufficient,
            "action": _checkpoint_action(p5, p50, p95, cp, p_reach_m1, sufficient),
        })
    return boundaries

def time_budget_allocation(max_steps):
    timeline = [
        {"step": "0", "name": "Setup cu124 venv", "start_hr": 0.0, "dur_hr": 0.17, "cumulative_hr": 0.17, "phase": "Pre-RL"},
        {"step": "1", "name": "Preflight check", "start_hr": 0.17, "dur_hr": 0.03, "cumulative_hr": 0.20, "phase": "Pre-RL"},
        {"step": "2", "name": "SGLang serve + Baseline eval (36%, 5-run)", "start_hr": 0.20, "dur_hr": 5.0, "cumulative_hr": 5.20, "phase": "Pre-RL"},
        {"step": "3", "name": "D1-D6 failure trajectory extraction", "start_hr": 5.20, "dur_hr": 0.33, "cumulative_hr": 5.53, "phase": "Pre-RL"},
        {"step": "4", "name": "Contamination gate", "start_hr": 5.53, "dur_hr": 0.08, "cumulative_hr": 5.61, "phase": "Pre-RL"},
        {"step": "5", "name": "RL smoke test (10 iters, R0)", "start_hr": 5.61, "dur_hr": SMOKE_MINUTES / 60.0, "cumulative_hr": 5.61 + SMOKE_MINUTES / 60.0, "phase": "Pre-RL"},
    ]
    rl_start = timeline[-1]["cumulative_hr"]
    rl_end = rl_start + max_steps / STEPS_PER_HR
    timeline.append({"step": "6", "name": "Full RL training (%d steps)" % max_steps, "start_hr": rl_start, "dur_hr": rl_end - rl_start, "cumulative_hr": rl_end, "phase": "RL Training"})
    timeline.append({"step": "7a", "name": "Best checkpoint selection", "start_hr": rl_end, "dur_hr": 0.02, "cumulative_hr": rl_end + 0.02, "phase": "Post-RL"})
    timeline.append({"step": "7b", "name": "158-case 5-run evaluation", "start_hr": rl_end + 0.02, "dur_hr": 4.5, "cumulative_hr": rl_end + 4.52, "phase": "Post-RL"})
    timeline.append({"step": "7c", "name": "McNemar + bootstrap analysis", "start_hr": rl_end + 4.52, "dur_hr": 0.08, "cumulative_hr": rl_end + 4.60, "phase": "Post-RL"})
    timeline.append({"step": "7d", "name": "M1-M4 milestone gate", "start_hr": rl_end + 4.60, "dur_hr": 0.02, "cumulative_hr": rl_end + 4.62, "phase": "Post-RL"})
    return timeline

def campaign_success_criteria():
    return [
        {"id": "S1", "criterion": "Baseline reproduced (36% +/- 3pp)", "measurement": "Step 2 eval Pass@1", "threshold": "33%-39%", "importance": "critical"},
        {"id": "S2", "criterion": "Smoke test passes (>=8/10 steps, no NaN/OOM)", "measurement": "Step 5 day1_diag", "threshold": "verdict=GO or WARN", "importance": "critical"},
        {"id": "S3", "criterion": "RL training completes without abort", "measurement": "Step 6 completion", "threshold": ">=150/200 steps", "importance": "critical"},
        {"id": "S4", "criterion": "RL shows learning signal", "measurement": "Reward trend", "threshold": "Final > initial + 0.005", "importance": "high"},
        {"id": "S5", "criterion": "std=0 rate controlled", "measurement": "Day1_diag classifier", "threshold": "std=0 < 30%", "importance": "high"},
        {"id": "S6", "criterion": "No reward hacking", "measurement": "Cheat rate", "threshold": "cheat < 5% (red-line)", "importance": "critical"},
        {"id": "S7", "criterion": "Post-RL eval improvement", "measurement": "Step 7b vs Step 2", "threshold": "Delta > 0", "importance": "medium"},
        {"id": "S8", "criterion": "Pipeline artifacts reusable", "measurement": "All scripts ran", "threshold": "Steps 0-7d executed", "importance": "high"},
    ]

# --- HTML Report ---

def generate_html(arm_key, bands, milestones_prob, boundaries, timeline, success_criteria, max_steps):
    cfg = R59_ARMS[arm_key]
    final_eval_p50 = transfer_function(bands["p50"][-1], max_steps)
    band_rows = ""
    for i in range(0, max_steps, max(1, max_steps // 20)):
        step = i + 1
        band_rows += "<tr><td>%d</td><td>%.4f</td><td>%.4f</td><td><b>%.4f</b></td><td>%.4f</td><td>%.4f</td><td>%.4f</td></tr>" % (
            step, bands['p5'][i], bands['p25'][i], bands['p50'][i], bands['p75'][i], bands['p95'][i],
            transfer_function(bands['p50'][i], step))
    ms_rows = ""
    for ms_name in ["baseline", "M1", "M2", "M3", "M4"]:
        ms = MILESTONES[ms_name]; prob = milestones_prob.get(ms_name, {})
        c50 = prob.get("first_cross_50pct", -1); c90 = prob.get("first_cross_90pct", -1)
        fp = prob.get("prob_by_step", {}).get(str(max_steps), 0.0)
        ms_rows += "<tr><td>%s</td><td>%.0f%%</td><td>%s</td><td>%s</td><td>%s</td><td>%.1f%%</td></tr>" % (
            ms_name, ms['pass1']*100, ms['label'], str(c50) if c50 > 0 else 'N/A',
            str(c90) if c90 > 0 else 'N/A', fp*100)
    cp_rows = ""
    for b in boundaries:
        col = "green" if "SUFFICIENT" in b["action"] else ("red" if "FUTILE" in b["action"] else ("orange" if "MARGINAL" in b["action"] or "DECLINING" in b["action"] else "#4a90d9"))
        cp_rows += "<tr style='background:%s15'><td>%d</td><td>%.1fh</td><td>%.4f</td><td>%.4f</td><td>%.4f</td><td>%.1f%%</td><td>%.0f%%</td><td style='font-size:0.85em'>%s</td></tr>" % (
            col, b['step'], b['wall_clock_hr'], b['reward_p5'], b['reward_p50'], b['reward_p95'],
            b['eval_pass1_p50']*100, b['p_reach_m1_by_end']*100, b['action'])
    tl_rows = ""
    for t in timeline:
        pc = {"Pre-RL": "#e3f2fd", "RL Training": "#e8f5e9", "Post-RL": "#fff3e0"}.get(t["phase"], "#fafafa")
        tl_rows += "<tr style='background:%s'><td>%s</td><td>%s</td><td>%.1fh</td><td>%.1fh</td><td>%.1fh</td><td>%s</td></tr>" % (
            pc, t['step'], t['name'], t['start_hr'], t['dur_hr'], t['cumulative_hr'], t['phase'])
    sc_rows = ""
    for sc in success_criteria:
        ic = {"critical": "#ffebee", "high": "#fff8e1", "medium": "#e8f5e9"}.get(sc["importance"], "#fafafa")
        sc_rows += "<tr style='background:%s'><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
            ic, sc['id'], sc['criterion'], sc['measurement'], sc['threshold'], sc['importance'])
    arm_rows = ""
    for ak, av in R59_ARMS.items():
        arm_rows += "<tr><td>%s</td><td>%.4f</td><td>%+.4f</td><td>%.1f%%</td><td>%.1f%%</td><td>%s</td></tr>" % (
            ak, av['initial_reward'], av['gain_200'], av['std_zero_final']*100, av['cheat_rate']*100,
            'optimal' if ak == arm_key else '')
    total_time = timeline[-1]["cumulative_hr"]
    within = "within budget" if total_time <= 72 else "OVER budget"
    return _html_template(arm_key, max_steps, MC_RUNS, RL_BUDGET_HR, STEPS_PER_HR, final_eval_p50,
                          cfg, bands, arm_rows, band_rows, ms_rows, cp_rows, tl_rows, sc_rows,
                          total_time, within)

def _html_template(arm_key, max_steps, mc_runs, rl_budget, sph, final_eval, cfg, bands,
                   arm_rows, band_rows, ms_rows, cp_rows, tl_rows, sc_rows, total_time, within):
    return """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>R65: 72h Surrogate RL Campaign Projection</title>
<style>
body{font-family:-apple-system,sans-serif;margin:2em;background:#f5f5f5;color:#333;line-height:1.6}
h1{color:#1a237e;border-bottom:3px solid #1a237e;padding-bottom:.3em}
h2{color:#283593;margin-top:1.5em;border-left:4px solid #283593;padding-left:.5em}
table{border-collapse:collapse;width:100%%;margin:1em 0;background:white;box-shadow:0 1px 3px rgba(0,0,0,.1)}
th,td{border:1px solid #ddd;padding:.5em .7em;text-align:left;font-size:.9em}
th{background:#1a237e;color:white}
tr:nth-child(even){background:#f9f9f9}
.box{background:white;padding:1em 1.5em;border-radius:8px;margin:1em 0;box-shadow:0 2px 6px rgba(0,0,0,.1);border-left:5px solid #1a237e}
.warn{background:#fff3e0;border-left:5px solid #ff6f00;padding:1em;border-radius:4px;margin:1em 0}
.red{background:#ffebee;border-left:5px solid #c62828;padding:1em;border-radius:4px;margin:1em 0}
code{background:#e8eaf6;padding:.1em .3em;border-radius:3px}
.m{display:inline-block;background:#e3f2fd;padding:.2em .6em;border-radius:12px;margin:.2em;font-size:.85em}
.foot{margin-top:2em;padding:1em;background:#eceff1;border-radius:4px;font-size:.85em;color:#555}
</style></head><body>
<h1>R65: 72h 替身 RL 活动投影与自适应停止边界</h1>
<div class="box">
<p><b>目标</b>：综合 R59/R61/R58/R64，为 11/9 GPU 到位后 72h 替身 RL 活动提供定量投影+自适应停止边界。</p>
<p><b>最优臂</b>：<code>R3_tool_penalty</code>（R59: +0.0134/200步, std=0=0%%）</p>
<p><span class="m">步数: %d</span><span class="m">RL: %.1fh</span><span class="m">%.2f st/hr</span><span class="m">Pass@1 P50: %.1f%%</span><span class="m">MC: %d</span></p>
</div>
<div class="warn"><b>替身预演不可迁移 BaiZe。</b>投影基于 R59 估计；11/9 实测替换假设。</div>
<h2>1. 奖励臂对比 (R59)</h2>
<table><tr><th>臂</th><th>初始</th><th>增益</th><th>std=0</th><th>作弊</th><th>判读</th></tr>%s</table>
<h2>2. 逐步奖励投影 (%s, %d MC)</h2>
<table><tr><th>Step</th><th>P5</th><th>P25</th><th>P50</th><th>P75</th><th>P95</th><th>Eval</th></tr>%s</table>
<p>初始 %.4f -> P50 %.4f (+%.4f). Eval Pass@1 = %.1f%%.</p>
<h2>3. Transfer Function</h2>
<div class="box"><p><code>eval = train * ratio(step)</code>, ratio: %.2f->%.2f, tau=%d. 200步 ratio=%.3f.</p></div>
<h2>4. 里程碑跨越概率</h2>
<table><tr><th>里程碑</th><th>目标</th><th>含义</th><th>P>=50%%</th><th>P>=90%%</th><th>Step %d</th></tr>%s</table>
<p>200步内 M1(50%%) 跨越概率取决于 transfer 乐观程度。与 R59 一致：200步不足以收敛。</p>
<h2>5. 自适应停止边界</h2>
<table><tr><th>Step</th><th>墙钟</th><th>P5</th><th>P50</th><th>P95</th><th>Eval</th><th>P(M1)</th><th>动作</th></tr>%s</table>
<div class="box"><p><b>SUFFICIENT</b>: Eval>=50%%->停. <b>ON TRACK</b>: P(M1)>=30%%->继续. <b>FUTILE</b>: P(M1)<5%%->停. <b>DECLINING</b>: P5低->查作弊.</p>
<p>安全(R62): NaN->ABORT, OOM->ABORT, std=0>80%%->DEBUG, cheat>15%%->DEBUG.</p></div>
<h2>6. 72h 时间预算</h2>
<table><tr><th>Step</th><th>任务</th><th>起始</th><th>耗时</th><th>累计</th><th>阶段</th></tr>%s</table>
<p>总: %.1fh / 72h -> %s.</p>
<h2>7. 活动成功标准</h2>
<table><tr><th>ID</th><th>标准</th><th>测量</th><th>阈值</th><th>重要性</th></tr>%s</table>
<p><b>最低</b>: S1+S2+S3+S6+S8. <b>理想</b>: +S4+S5+S7.</p>
<h2>8. 前序关联</h2>
<table><tr><th>来源</th><th>贡献</th><th>用途</th></tr>
<tr><td>R58</td><td>3347 prompt, 2037 SIGNAL</td><td>训练池</td></tr>
<tr><td>R59</td><td>GRPO MC, R3最优</td><td>轨迹参数</td></tr>
<tr><td>R60</td><td>ctx>=16384</td><td>配置</td></tr>
<tr><td>R61</td><td>3.45 st/hr</td><td>步->时间</td></tr>
<tr><td>R62</td><td>12-check诊断</td><td>安全</td></tr>
<tr><td>R63</td><td>Post-RL+guardian</td><td>Step7</td></tr>
<tr><td>R64</td><td>SFT->RL交接</td><td>热启动</td></tr>
<tr><td>R57</td><td>Vision std=0 78.7%%</td><td>监控</td></tr></table>
<div class="red"><b>红线</b>: 158任务禁入训练集 | anti-cheat全程 | 5-run mean+-std | 评测冻结 | M1-M4先定后测.</div>
<div class="foot"><p>溯源: R59/R61/R58/R64/R57/R62/R63 + §5.1/§5.2/§4. 无伪造. 2026-11-08 wake113 R65. 替身不可迁移BaiZe.</p></div>
</body></html>""" % (
        max_steps, rl_budget, sph, final_eval*100, mc_runs,
        arm_rows,
        arm_key, mc_runs, band_rows,
        cfg['initial_reward'], bands['p50'][-1], bands['p50'][-1]-cfg['initial_reward'], final_eval*100,
        TRANSFER_RATIO_INIT, TRANSFER_RATIO_ASYMPTOTE, TRANSFER_TAU,
        TRANSFER_RATIO_INIT + (TRANSFER_RATIO_ASYMPTOTE-TRANSFER_RATIO_INIT)*(1-math.exp(-max_steps/TRANSFER_TAU)),
        max_steps, ms_rows,
        cp_rows,
        tl_rows, total_time, within,
        sc_rows)

# --- Main ---

def main():
    parser = argparse.ArgumentParser(description="R65 Campaign Projection")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--mc-runs", type=int, default=MC_RUNS)
    parser.add_argument("--max-steps", type=int, default=MAX_STEPS)
    parser.add_argument("--arm", default="R3_tool_penalty")
    parser.add_argument("--html", default="")
    parser.add_argument("--json", default="")
    parser.add_argument("--seed", type=int, default=RANDOM_SEED)
    args = parser.parse_args()

    print("=" * 50)
    print("R65: 72h Surrogate RL Campaign Projection")
    print("=" * 50)
    print("  Arm       : %s" % args.arm)
    print("  MC runs   : %d" % args.mc_runs)
    print("  Max steps : %d" % args.max_steps)
    print("  Steps/hr  : %.2f" % STEPS_PER_HR)
    print("  RL budget : %.1fh" % RL_BUDGET_HR)
    print("  Pre-RL    : %.1fh" % PRE_RL_HR)
    print("  Post-RL   : %.1fh" % POST_RL_HR)
    total_est = PRE_RL_HR + args.max_steps / STEPS_PER_HR + POST_RL_HR
    print("  Total     : %.1fh / 72h" % total_est)

    if args.dry_run:
        print("\n[dry-run] Config printed. No simulation.")
        return 0

    print("\n[1/6] Simulating %d MC trajectories for %s..." % (args.mc_runs, args.arm))
    trajectories = reward_trajectory(args.arm, args.max_steps, args.mc_runs, args.seed)
    bands = compute_confidence_bands(trajectories)
    print("  P50 step 1: %.4f" % bands['p50'][0])
    print("  P50 step %d: %.4f" % (args.max_steps, bands['p50'][-1]))
    final_eval = transfer_function(bands['p50'][-1], args.max_steps)
    print("  Eval Pass@1 P50 final: %.1f%%" % (final_eval * 100))

    print("\n[2/6] Milestone crossing probabilities...")
    ms_prob = milestone_crossing_probability(trajectories, MILESTONES, args.max_steps)
    for ms_name in ["M1", "M2", "M3", "M4"]:
        ms = ms_prob[ms_name]
        fp = ms["prob_by_step"].get(str(args.max_steps), 0.0)
        c50 = ms["first_cross_50pct"]
        print("  %s (%.0f%%): P=%s, first50%%=%s" % (ms_name, ms['target']*100, "%.1f%%" % (fp*100), str(c50) if c50 > 0 else 'N/A'))

    print("\n[3/6] Adaptive stopping boundaries...")
    boundaries = adaptive_stopping_boundaries(trajectories, CHECKPOINTS, args.max_steps)
    for b in boundaries:
        print("  Step %d (%.1fh): P50=%.4f eval=%.1f%% P(M1)=%.0f%%" % (
            b['step'], b['wall_clock_hr'], b['reward_p50'], b['eval_pass1_p50']*100, b['p_reach_m1_by_end']*100))

    print("\n[4/6] Time budget allocation...")
    timeline = time_budget_allocation(args.max_steps)
    total_time = timeline[-1]["cumulative_hr"]
    print("  Total: %.1fh / 72h -> %s" % (total_time, "OK" if total_time <= 72 else "OVER"))

    print("\n[5/6] Success criteria...")
    sc = campaign_success_criteria()
    print("  %d criteria (%d critical)" % (len(sc), sum(1 for s in sc if s['importance'] == 'critical')))

    print("\n[6/6] Generating outputs...")
    result = {
        "r65": {
            "arm": args.arm, "mc_runs": args.mc_runs, "max_steps": args.max_steps,
            "steps_per_hr": STEPS_PER_HR, "rl_budget_hr": round(RL_BUDGET_HR, 1),
            "total_campaign_hr": round(total_time, 1), "within_budget": total_time <= 72,
            "final_eval_pass1_p50": round(final_eval, 4),
            "confidence_bands": {"p5": [round(v,4) for v in bands["p5"]], "p50": [round(v,4) for v in bands["p50"]], "p95": [round(v,4) for v in bands["p95"]]},
            "milestone_probabilities": {ms_name: {"target": ms["target"], "final_probability": ms["prob_by_step"].get(str(args.max_steps), 0.0), "first_cross_50pct": ms["first_cross_50pct"]} for ms_name, ms in ms_prob.items()},
            "adaptive_boundaries": boundaries, "timeline": timeline, "success_criteria": sc,
        }
    }
    if args.json:
        with open(args.json, "w") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print("  JSON: %s" % args.json)
    html = generate_html(args.arm, bands, ms_prob, boundaries, timeline, sc, args.max_steps)
    html_path = args.html if args.html else "/tmp/r65_campaign_projection.html"
    with open(html_path, "w") as f:
        f.write(html)
    print("  HTML: %s (%d bytes)" % (html_path, len(html)))
    print("\nR65 complete. Final eval Pass@1 P50: %.1f%%" % (final_eval * 100))
    return 0

if __name__ == "__main__":
    sys.exit(main())




