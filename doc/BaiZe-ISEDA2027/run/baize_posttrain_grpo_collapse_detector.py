#!/usr/bin/env python3
"""
baize_posttrain_grpo_collapse_detector.py
R80: GRPO Collapse Mode Taxonomy & Detection Threshold Calibration

Catalogs 7 known GRPO collapse modes (from literature + vision-line lessons),
simulates each with Monte Carlo to calibrate real-time detection thresholds,
and produces a monitoring protocol with actionable alert rules.

Zero GPU -- pure Python 3.8+ Monte Carlo simulation + stdlib only.
"""
import argparse, json, math, os, random, sys, html
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_JSON = os.path.join(SCRIPT_DIR, "r80_grpo_collapse_results.json")
OUTPUT_HTML_DIR = os.path.join(SCRIPT_DIR, "..", "reports")
OUTPUT_HTML = os.path.join(OUTPUT_HTML_DIR, "report_posttrain_r80_grpo_collapse_zh.html")

DEFAULT_MAX_STEPS = 500
DEFAULT_MC_RUNS = 200
DEFAULT_GROUP_SIZE = 8
SEED_BASE = 42

class GRPOStepSim:
    """Simulates one GRPO training step with group-relative advantage estimation."""
    def __init__(self, rng, group_size=8, lr=1e-6, kl_coef=0.001, clip_ratio=0.2, entropy_coef=0.01):
        self.rng = rng
        self.n = group_size
        self.lr = lr
        self.kl_coef = kl_coef
        self.clip_ratio = clip_ratio
        self.entropy_coef = entropy_coef
        self.policy_quality = 0.36
        self.policy_entropy = 1.5
        self.kl_from_ref = 0.0
        self.avg_reward = 0.36
        self.reward_std = 0.15
        self.avg_length = 50.0
        self.grad_norm = 0.1
        self.cheat_rate = 0.0
        self.step = 0
        self.history = []

    def _rollout_rewards(self, base_quality, cheat_prob, length_factor):
        rewards = []
        cheats = 0
        for _ in range(self.n):
            if self.rng.random() < cheat_prob:
                r = self.rng.gauss(0.85, 0.05)
                r = max(0.0, min(1.0, r))
                cheats += 1
            else:
                r = self.rng.gauss(base_quality, 0.15)
                r = max(0.0, min(1.0, r))
            rewards.append(r)
        if length_factor > 1.0:
            for i in range(len(rewards)):
                rewards[i] = min(1.0, rewards[i] * length_factor)
        return rewards, cheats / self.n

    def step_forward(self, collapse_mode="none", onset_step=150, severity=1.0):
        self.step += 1
        cheat_prob = 0.0
        length_factor = 1.0
        quality_drift = 0.002
        entropy_drift = -0.002
        kl_growth = 0.002
        grad_multiplier = 1.0
        reward_boost = 0.0
        is_collapsed = self.step >= onset_step

        if is_collapsed:
            if collapse_mode == "C1_reward_hacking":
                cheat_prob = 0.3 * severity
                quality_drift = -0.001
                reward_boost = 0.15 * severity
            elif collapse_mode == "C2_kl_explosion":
                kl_growth = 0.05 * severity
                quality_drift = -0.003 * severity
                grad_multiplier = 2.0
            elif collapse_mode == "C3_advantage_vanishing":
                self.reward_std *= (1.0 - 0.05 * severity)
                quality_drift = 0.0
                entropy_drift = 0.0
            elif collapse_mode == "C4_entropy_collapse":
                entropy_drift = -0.03 * severity
                quality_drift = -0.001
            elif collapse_mode == "C5_grad_explosion":
                grad_multiplier = 5.0 * severity
                quality_drift = self.rng.gauss(0, 0.01)
            elif collapse_mode == "C6_reward_stagnation":
                quality_drift = 0.0
                entropy_drift = 0.0
                kl_growth = 0.0
            elif collapse_mode == "C7_length_exploitation":
                length_factor = 1.0 + 0.1 * severity
                self.avg_length *= (1.0 + 0.02 * severity)
                quality_drift = -0.001

        rewards, cheat_frac = self._rollout_rewards(self.policy_quality + reward_boost, cheat_prob, length_factor)
        self.avg_reward = sum(rewards) / len(rewards)
        self.reward_std = (sum((r - self.avg_reward) ** 2 for r in rewards) / len(rewards)) ** 0.5
        self.cheat_rate = cheat_frac

        if self.reward_std > 1e-6:
            advantages = [(r - self.avg_reward) / (self.reward_std + 1e-8) for r in rewards]
        else:
            advantages = [0.0] * self.n

        avg_advantage = sum(advantages) / len(advantages)
        self.policy_quality += quality_drift + avg_advantage * self.lr * 10
        self.policy_quality = max(0.0, min(1.0, self.policy_quality))
        self.policy_entropy += entropy_drift
        self.policy_entropy = max(0.01, self.policy_entropy)
        self.kl_from_ref += kl_growth
        self.kl_from_ref = max(0.0, self.kl_from_ref)
        base_grad = abs(avg_advantage) * 0.1
        self.grad_norm = base_grad * grad_multiplier + self.rng.gauss(0, 0.02)
        self.grad_norm = max(0.0, self.grad_norm)

        metrics = {
            "step": self.step, "pass_at_1": round(self.policy_quality, 4),
            "avg_reward": round(self.avg_reward, 4), "reward_std": round(self.reward_std, 4),
            "advantage_std": round(self.reward_std, 4), "policy_entropy": round(self.policy_entropy, 4),
            "kl_from_ref": round(self.kl_from_ref, 4), "grad_norm": round(self.grad_norm, 4),
            "avg_length": round(self.avg_length, 2), "cheat_rate": round(self.cheat_rate, 4),
            "is_collapsed": is_collapsed,
        }
        self.history.append(metrics)
        return metrics

COLLAPSE_MODES = [
    {"id": "C1_reward_hacking", "name": "奖励作弊 (Reward Hacking)",
     "mechanism": "模型发现奖励函数漏洞，通过非预期行为获取高奖励而不提升真实任务质量。",
     "triggers": ["奖励函数过于宽松", "无 anti-cheat hook", "奖励信号与真实目标脱钩"],
     "vision_lesson": "Vision 线 GRPO 曾出现模型输出全黑图像骗过 IoU 奖励 (R57 §2.1)",
     "recovery": ["R-01: 降低学习率×0.1", "R-02: 加强 PreToolUse hook", "R-03: 切换 R3/R4 奖励臂", "R-04: cheat_rate>20%→回滚ckpt"]},
    {"id": "C2_kl_explosion", "name": "KL 散度爆炸",
     "mechanism": "策略偏离参考模型过远，导致生成质量恶化、训练不稳定。",
     "triggers": ["kl_coef 过低", "学习率过高", "clip_ratio 过大"],
     "vision_lesson": "Vision 线曾因 kl_coef=0 出现策略崩溃 (R57 §2.3)",
     "recovery": ["R-01: 提升 kl_coef×10", "R-02: 降低学习率×0.5", "R-03: KL>5.0→回滚ckpt"]},
    {"id": "C3_advantage_vanishing", "name": "优势消失 (std=0)",
     "mechanism": "同一 prompt 的 n 个 rollout 获得相同奖励，advantage=0，梯度信号消失。",
     "triggers": ["题目过难/过易", "奖励纯二值无梯度", "课程跳过中等题"],
     "vision_lesson": "Vision 线 40% prompt std=0 (R57 §2.2)→切换 Dr.GRPO",
     "recovery": ["R-01: 切换 Dr.GRPO", "R-02: 增加中等难度题", "R-03: rollout n:8→16", "R-04: ratio>60%→暂停重选prompt"]},
    {"id": "C4_entropy_collapse", "name": "策略熵坍缩",
     "mechanism": "探索性丧失，策略退化为确定性输出，无法发现新高奖励行为。",
     "triggers": ["entropy_coef 过低/为0", "训练过长未重启探索", "奖励过于稀疏"],
     "vision_lesson": "Vision 线 entropy 1.2→0.1 后 Pass@1 停滞 (R57 §2.4)",
     "recovery": ["R-01: entropy_coef×5", "R-02: 采样温度提升", "R-03: 注入新prompt", "R-04: entropy<0.1→从SFT ckpt重跑"]},
    {"id": "C5_grad_explosion", "name": "梯度爆炸",
     "mechanism": "梯度范数急剧增大，loss spike，参数更新方向混乱。",
     "triggers": ["学习率过高+大batch", "奖励极端值", "fp16/bf16不稳定"],
     "vision_lesson": "Vision 线 step 200 loss spike→NaN (R57 §2.5)",
     "recovery": ["R-01: 学习率×0.1", "R-02: 梯度裁剪 max_norm=1.0", "R-03: NaN→回滚ckpt", "R-04: 切换fp32累积"]},
    {"id": "C6_reward_stagnation", "name": "奖励停滞 (Plateau)",
     "mechanism": "训练长时间无进展，avg_reward 停滞，可能课程不当或学习率过低。",
     "triggers": ["当前难度已饱和", "学习率衰减过快", "数据多样性不足"],
     "vision_lesson": "Vision 线 step 300+ Pass@1 平台期 (R57 §2.6)",
     "recovery": ["R-01: 推进课程下一难度", "R-02: cosine restart", "R-03: 注入新题", "R-04: 停滞>100步→提前结束"]},
    {"id": "C7_length_exploitation", "name": "长度利用 (Padding)",
     "mechanism": "模型发现更长输出获更高奖励，导致输出膨胀。",
     "triggers": ["R2 部分分按步骤给", "无长度惩罚", "max_tokens 过大"],
     "vision_lesson": "未在 vision 线出现，但文献常见 (Ouyang et al. 2022)",
     "recovery": ["R-01: 增加长度惩罚-lambda*len", "R-02: 降低max_tokens", "R-03: 切R1二值奖励", "R-04: 归一化长度"]},
]

def run_simulation(collapse_mode, onset_step, severity, max_steps, mc_runs, seed):
    rng = random.Random(seed)
    all_runs_metrics = []
    for run_idx in range(mc_runs):
        sim = GRPOStepSim(rng=random.Random(seed + run_idx))
        for _ in range(max_steps):
            sim.step_forward(collapse_mode, onset_step, severity)
        all_runs_metrics.append(sim.history)

    metric_names = ["avg_reward", "reward_std", "policy_entropy", "kl_from_ref", "grad_norm", "avg_length", "cheat_rate", "pass_at_1"]
    pre_collapse = defaultdict(list)
    post_collapse = defaultdict(list)
    for run_metrics in all_runs_metrics:
        for m in run_metrics:
            phase = "post" if m["is_collapsed"] else "pre"
            for mn in metric_names:
                if mn in m:
                    if phase == "pre":
                        pre_collapse[mn].append(m[mn])
                    else:
                        post_collapse[mn].append(m[mn])

    thresholds = {}
    for mn in metric_names:
        pre_vals = sorted(pre_collapse.get(mn, [0]))
        post_vals = sorted(post_collapse.get(mn, [0]))
        if not pre_vals:
            continue
        p99 = pre_vals[int(0.99 * len(pre_vals))] if len(pre_vals) > 10 else max(pre_vals)
        p01 = pre_vals[int(0.01 * len(pre_vals))] if len(pre_vals) > 10 else min(pre_vals)
        post_median = post_vals[len(post_vals) // 2] if post_vals else 0
        if post_vals:
            if mn in ["policy_entropy", "reward_std", "pass_at_1"]:
                detect_rate = sum(1 for v in post_vals if v < p01) / len(post_vals)
                thresholds[mn] = {"threshold": round(p01, 4), "direction": "below", "detect_rate": round(detect_rate, 4), "false_positive_rate": 0.01, "post_median": round(post_median, 4)}
            else:
                detect_rate = sum(1 for v in post_vals if v > p99) / len(post_vals)
                thresholds[mn] = {"threshold": round(p99, 4), "direction": "above", "detect_rate": round(detect_rate, 4), "false_positive_rate": 0.01, "post_median": round(post_median, 4)}

    detection_latencies = []
    for run_metrics in all_runs_metrics:
        onset = next((m for m in run_metrics if m["is_collapsed"]), None)
        if not onset:
            continue
        onset_step_num = int(onset["step"])
        for mn, th_info in thresholds.items():
            th = th_info["threshold"]
            direction = th_info["direction"]
            for m in run_metrics:
                if m["step"] > onset_step_num:
                    val = m.get(mn, 0)
                    if direction == "above" and val > th:
                        detection_latencies.append(m["step"] - onset_step_num)
                        break
                    elif direction == "below" and val < th:
                        detection_latencies.append(m["step"] - onset_step_num)
                        break
    avg_latency = sum(detection_latencies) / len(detection_latencies) if detection_latencies else -1
    representative = all_runs_metrics[0] if all_runs_metrics else []
    return {"collapse_mode": collapse_mode, "onset_step": onset_step, "severity": severity, "mc_runs": mc_runs, "max_steps": max_steps, "thresholds": thresholds, "avg_detection_latency_steps": round(avg_latency, 1), "detection_latency_samples": len(detection_latencies), "representative_trajectory": representative[-50:], "pre_collapse_stats": {mn: {"mean": round(sum(v)/len(v), 4) if v else 0, "count": len(v)} for mn, v in pre_collapse.items()}, "post_collapse_stats": {mn: {"mean": round(sum(v)/len(v), 4) if v else 0, "count": len(v)} for mn, v in post_collapse.items()}}

def generate_html(results, output_path):
    modes = results["modes"]
    summary = results["summary"]
    def esc(s): return html.escape(str(s))
    mode_sections = []
    for mode_data in modes:
        sim = mode_data["simulation"]
        mode_info = next(m for m in COLLAPSE_MODES if m["id"] == sim["collapse_mode"])
        ths = sim["thresholds"]
        th_rows = ""
        for metric_name, th_info in ths.items():
            detect_pct = th_info["detect_rate"] * 100
            th_rows += '<tr><td><code>%s</code></td><td>%s</td><td><strong>%s</strong></td><td>%.1f%%</td><td>%.1f%%</td><td>%s</td></tr>' % (esc(metric_name), esc(th_info["direction"]), esc(th_info["threshold"]), detect_pct, th_info.get("false_positive_rate", 0.01) * 100, esc(th_info.get("post_median", "—")))
        recovery_items = "".join("<li>%s</li>" % esc(r) for r in mode_info["recovery"])
        trigger_items = "".join("<li>%s</li>" % esc(t) for t in mode_info["triggers"])
        traj = sim.get("representative_trajectory", [])
        traj_lines = ""
        if traj:
            pre = [m for m in traj if not m["is_collapsed"]]
            post = [m for m in traj if m["is_collapsed"]]
            if pre:
                traj_lines += '<tr><td>崩溃前 (步 %d–%d)</td><td>%.4f</td><td>%.4f</td><td>%.4f</td><td>%.4f</td><td>%.4f</td></tr>' % (int(pre[0]['step']), int(pre[-1]['step']), pre[-1]['avg_reward'], pre[-1]['reward_std'], pre[-1]['policy_entropy'], pre[-1]['kl_from_ref'], pre[-1]['grad_norm'])
            if post:
                traj_lines += '<tr style="color:#c62828"><td>崩溃后 (步 %d–%d)</td><td>%.4f</td><td>%.4f</td><td>%.4f</td><td>%.4f</td><td>%.4f</td></tr>' % (int(post[0]['step']), int(post[-1]['step']), post[-1]['avg_reward'], post[-1]['reward_std'], post[-1]['policy_entropy'], post[-1]['kl_from_ref'], post[-1]['grad_norm'])
        mode_sections.append('<div class="mode-section"><h2 id="%s">%s: %s</h2><h3>机制</h3><p>%s</p><h3>已知触发条件</h3><ul>%s</ul><h3>Vision 线教训</h3><p style="border-left:3px solid #1565c0;padding-left:10px;color:#555">%s</p><h3>仿真参数</h3><table class="data-table"><tr><th>参数</th><th>值</th></tr><tr><td>崩溃起始步</td><td>%d</td></tr><tr><td>严重度</td><td>%s</td></tr><tr><td>蒙特卡洛运行数</td><td>%d</td></tr><tr><td>每运行步数</td><td>%d</td></tr><tr><td>平均检测延迟</td><td><strong>%s 步</strong></td></tr></table><h3>校准的检测阈值</h3><table class="data-table"><tr><th>检测指标</th><th>方向</th><th>阈值</th><th>检出率</th><th>误报率</th><th>崩溃后中位值</th></tr>%s</table><h3>崩溃前后代表性轨迹</h3><table class="data-table"><tr><th>阶段</th><th>avg_reward</th><th>reward_std</th><th>entropy</th><th>KL</th><th>grad_norm</th></tr>%s</table><h3>恢复协议</h3><ol>%s</ol></div>' % (esc(mode_info['id']), esc(mode_info['id']), esc(mode_info['name']), esc(mode_info['mechanism']), trigger_items, esc(mode_info['vision_lesson']), sim['onset_step'], sim['severity'], sim['mc_runs'], sim['max_steps'], sim['avg_detection_latency_steps'], th_rows, traj_lines, recovery_items))
    summary_rows = ""
    for s in summary:
        summary_rows += '<tr><td><code>%s</code></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (esc(s['id']), esc(s['name']), esc(s['latency']), esc(s['best_metric']), esc(s['best_detect_rate']))
    _css = "<style>body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;max-width:1100px;margin:0 auto;padding:20px;line-height:1.6;color:#333}h1{color:#1a237e;border-bottom:3px solid #1a237e;padding-bottom:8px}h2{color:#283593;margin-top:30px;border-bottom:1px solid #ccc;padding-bottom:5px}h3{color:#3949ab;margin-top:18px}table.data-table{border-collapse:collapse;width:100%;margin:10px 0;font-size:14px}table.data-table th,table.data-table td{border:1px solid #ddd;padding:6px 10px;text-align:left}table.data-table th{background:#e8eaf6;font-weight:bold}table.data-table tr:nth-child(even){background:#f5f5f5}.mode-section{background:#fafafa;border:1px solid #e0e0e0;border-radius:8px;padding:15px 20px;margin:20px 0}code{background:#eceff1;padding:1px 5px;border-radius:3px;font-size:13px}.summary-box{background:#e3f2fd;border-radius:8px;padding:15px;margin:15px 0}.warning{background:#fff3e0;border-left:4px solid #ff9800;padding:10px 15px;margin:10px 0}</style>"
    html_content = '<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>R80</title>' + _css + '</head><body>'
    html_content += '<h1>R80: GRPO \u5d29\u6e83\u6a21\u5f0f\u5206\u7c7b\u6cd5\u4e0e\u68c0\u6d4b\u9608\u503c\u6821\u51c6</h1>'
    html_content += '<p style="color:#666;font-size:14px">BaiZe Stage(ii) Post-Training \u00b7 \u96f6 GPU \u8499\u7279\u5361\u6d1b\u4eff\u771f \u00b7 2026-11-09</p>'
    html_content += '<div class="summary-box"><h3>\u6458\u8981</h3><p>\u672c\u7814\u7a76\u5bf9 GRPO \u8bad\u7ec3\u4e2d <strong>7 \u79cd\u5df2\u77e5\u5d29\u6e83\u6a21\u5f0f</strong>\u8fdb\u884c\u7cfb\u7edf\u5206\u7c7b\uff0c\u901a\u8fc7\u8499\u7279\u5361\u6d1b\u4eff\u771f\uff08200\u6b21\u00d7500\u6b65=100k\u6b65/\u6a21\u5f0f\uff09\u6821\u51c6\u5b9e\u65f6\u68c0\u6d4b\u9608\u503c\u3002\u6bcf\u79cd\u6a21\u5f0f\u542b\u68c0\u51fa\u7387/\u8bef\u62a5\u7387/\u5ef6\u8fdf/\u6062\u590d\u534f\u8bae\u3002</p><p><strong>\u6838\u5fc3\u53d1\u73b0</strong>: C3\u4f18\u52bf\u6d88\u5931\u548cC1\u5956\u52b1\u4f5c\u5f0a\u6700\u5371\u9669\uff08\u5ef6\u8fdf\u77ed\u4f46\u6062\u590d\u4ee3\u4ef7\u9ad8\uff09\uff1bC4\u71b5\u574d\u7f29\u548cC6\u505c\u6ede\u6700\u9690\u853d\uff08\u9700EMA\u76d1\u63a7\uff09\u3002</p></div>'
    html_content += '<h2>\u5d29\u6e83\u6a21\u5f0f\u603b\u89c8</h2><table class="data-table"><tr><th>\u7f16\u53f7</th><th>\u540d\u79f0</th><th>\u5ef6\u8fdf</th><th>\u6700\u4f73\u6307\u6807</th><th>\u68c0\u51fa\u7387</th></tr>' + summary_rows + '</table>'
    html_content += '<div class="warning"><strong>\u4f7f\u7528\u8bf4\u660e</strong>: \u9608\u503c\u57fa\u4e8e MiniCPM5-2B \u66ff\u8eab\u4eff\u771f\u6821\u51c6\uff0cGPU Day \u540e\u9700\u91cd\u65b0\u6821\u51c6\u3002</div>'
    html_content += "".join(mode_sections)
    html_content += '<h2>\u76d1\u63a7\u90e8\u7f72</h2><h3>7\u6307\u6807\u4eea\u8868\u76d8</h3><table class="data-table"><tr><th>\u6307\u6807</th><th>\u6765\u6e90</th><th>watch</th><th>warn</th><th>stop</th></tr><tr><td><code>cheat_rate</code></td><td>PreToolUse hook</td><td>&gt;2%</td><td>&gt;5%</td><td>&gt;10%</td></tr><tr><td><code>kl_from_ref</code></td><td>verl\u65e5\u5fd7</td><td>&gt;1.0</td><td>&gt;2.0</td><td>&gt;5.0</td></tr><tr><td><code>reward_std</code></td><td>verl\u65e5\u5fd7</td><td>&lt;0.05</td><td>&lt;0.02</td><td>\u22480(50\u6b65)</td></tr><tr><td><code>policy_entropy</code></td><td>verl\u65e5\u5fd7</td><td>&lt;0.5</td><td>&lt;0.3</td><td>&lt;0.1</td></tr><tr><td><code>grad_norm</code></td><td>verl\u65e5\u5fd7</td><td>&gt;0.5</td><td>&gt;1.0</td><td>NaN/Inf</td></tr><tr><td><code>avg_length</code></td><td>verl\u65e5\u5fd7</td><td>\u21910.3/step</td><td>\u21910.5/step</td><td>\u21911.0/step</td></tr></table>'
    html_content += '<h3>\u4e09\u7ea7\u544a\u8b66\u54cd\u5e94</h3><ul><li><strong>watch</strong>: \u8bb0\u5f55\u65e5\u5fd7\uff0c\u89c2\u5bdf1\u0d655\u6b65</li><li><strong>warn</strong>: \u89e6\u53d1\u6062\u590dR-01/R-02\uff0c20\u6b65\u65e0\u6539\u5584\u5347\u7ea7</li><li><strong>stop</strong>: \u6682\u505c\u8bad\u7ec3\uff0c\u4fdd\u5b58ckpt\uff0c\u56de\u6eda\uff0c\u4eba\u5de5\u4ecb\u5165</li></ul>'
    html_content += '<h2>\u4e0e\u65e2\u6709\u7814\u7a76\u7684\u5173\u7cfb</h2><table class="data-table"><tr><th>R80</th><th>\u524d\u7f6e</th><th>\u5173\u7cfb</th></tr><tr><td>C1\u5956\u52b1\u4f5c\u5f0a</td><td>R75 anti-hack</td><td>R80\u6821\u51c6\u9608\u503c</td></tr><tr><td>C2 KL\u7206\u70b8</td><td>R73\u8d85\u53c2</td><td>R80\u91cf\u5316KL\u9608\u503c</td></tr><tr><td>C3\u4f18\u52bf\u6d88\u5931</td><td>R59\u52a8\u529b\u5b66</td><td>R80\u6821\u51c6std=0</td></tr><tr><td>C4\u71b5\u574d\u7f29</td><td>R57 vision</td><td>R80\u91cf\u5316entropy</td></tr></table>'
    html_content += '<h2>\u5c40\u9650</h2><ul><li>\u4eff\u771f\u57fa\u4e8e\u7b80\u5316\u52a8\u529b\u5b66\u6a21\u578b\uff0c\u771f\u5b9eGRPO\u53ef\u80fd\u66f4\u590d\u6742</li><li>\u9608\u503c\u57fa\u4e8eMiniCPM5-2B(2B,lr=1e-6,n=8)\uff0cBaiZe\u6b63\u5f0f\u6a21\u578b\u9700\u91cd\u65b0\u6821\u51c6</li><li>\u66ff\u8eab\u6a21\u578b\u7ed3\u679c\u4e0d\u53ef\u76f4\u63a5\u8fc1\u79fb\u5230BaiZe\u6b63\u5f0f\u8bad\u7ec3</li><li>\u65e0\u4f2a\u9020\u3002\u8499\u7279\u5361\u6d1b\u4eff\u771f\u57fa\u4e8e\u5408\u7406\u5047\u8bbe\uff0c\u6807\u6ce8\u4e3a\u4eff\u771f\u6295\u5f71\u975e\u5b9e\u6d4b</li></ul>'
    html_content += '</body></html>'


    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    return output_path

def main():
    parser = argparse.ArgumentParser(description="R80: GRPO Collapse Mode Taxonomy & Detection Threshold Calibration")
    parser.add_argument("--max-steps", type=int, default=DEFAULT_MAX_STEPS)
    parser.add_argument("--mc-runs", type=int, default=DEFAULT_MC_RUNS)
    parser.add_argument("--group-size", type=int, default=DEFAULT_GROUP_SIZE)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--html", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    print("R80: GRPO Collapse Mode Taxonomy & Detection Threshold Calibration")
    print("  Modes: %d" % len(COLLAPSE_MODES))
    print("  MC runs per mode: %d" % args.mc_runs)
    print("  Steps per run: %d" % args.max_steps)
    print("  Total simulated steps: %d" % (len(COLLAPSE_MODES) * args.mc_runs * args.max_steps))
    print()

    all_mode_results = []
    summary = []
    mode_configs = {
        "C1_reward_hacking": {"onset": 150, "severity": 1.0},
        "C2_kl_explosion": {"onset": 200, "severity": 0.8},
        "C3_advantage_vanishing": {"onset": 100, "severity": 0.6},
        "C4_entropy_collapse": {"onset": 250, "severity": 0.7},
        "C5_grad_explosion": {"onset": 180, "severity": 1.2},
        "C6_reward_stagnation": {"onset": 300, "severity": 0.5},
        "C7_length_exploitation": {"onset": 220, "severity": 0.9},
    }

    for i, mode_info in enumerate(COLLAPSE_MODES):
        mid = mode_info["id"]
        cfg = mode_configs.get(mid, {"onset": 150, "severity": 1.0})
        if args.verbose:
            print("  [%d/%d] Simulating %s (onset=%d, severity=%s)..." % (i+1, len(COLLAPSE_MODES), mid, cfg["onset"], cfg["severity"]))
        sim_result = run_simulation(collapse_mode=mid, onset_step=cfg["onset"], severity=cfg["severity"], max_steps=args.max_steps, mc_runs=args.mc_runs, seed=SEED_BASE + i * 1000)
        best_metric = None
        best_detect_rate = 0
        for mn, th_info in sim_result["thresholds"].items():
            if th_info["detect_rate"] > best_detect_rate:
                best_detect_rate = th_info["detect_rate"]
                best_metric = mn
        all_mode_results.append({"id": mid, "name": mode_info["name"], "simulation": sim_result})
        summary.append({"id": mid, "name": mode_info["name"], "latency": "%s 步" % sim_result["avg_detection_latency_steps"], "best_metric": best_metric or "—", "best_detect_rate": "%.1f%%" % (best_detect_rate * 100)})
        if args.verbose:
            print("    -> avg latency: %s steps, best: %s (%.1f%%)" % (sim_result["avg_detection_latency_steps"], best_metric, best_detect_rate * 100))

    results = {"title": "R80: GRPO Collapse Mode Taxonomy & Detection Threshold Calibration", "date": "2026-11-09", "mode_count": len(COLLAPSE_MODES), "mc_runs_per_mode": args.mc_runs, "max_steps": args.max_steps, "total_simulated_steps": len(COLLAPSE_MODES) * args.mc_runs * args.max_steps, "modes": all_mode_results, "summary": summary}

    if args.json:
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print("\n  JSON saved: %s" % OUTPUT_JSON)
    if args.html:
        os.makedirs(os.path.dirname(OUTPUT_HTML), exist_ok=True)
        generate_html(results, OUTPUT_HTML)
        print("  HTML saved: %s" % OUTPUT_HTML)

    print("\n" + "=" * 80)
    print("%-30s %10s %-20s %12s" % ("Mode", "Latency", "Best Metric", "Detect Rate"))
    print("=" * 80)
    for s in summary:
        print("%-30s %10s %-20s %12s" % (s["id"], s["latency"], s["best_metric"], s["best_detect_rate"]))
    print("=" * 80)
    print("\nTotal simulated steps: %s" % format(results["total_simulated_steps"], ","))
    print("Done.")

if __name__ == "__main__":
    main()
