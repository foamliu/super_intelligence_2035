#!/usr/bin/env python3
"""
baize_posttrain_grpo_dynamics_sim.py
R59: GRPO Training Dynamics Monte Carlo Simulator

Goes beyond R58's static one-shot pass-rate estimation by modelling the
step-by-step GRPO training process over N steps.  Answers:
  - How does average reward evolve over 500 steps?
  - When does std=0 become critical (-> switch to Dr.GRPO)?
  - How do reward arms R1-R4 compare in expected trajectory?
  - What is the effect of curriculum scheduling (Phase 1->2->3)?
  - What is the probability of reward hacking emergence?
  - What is the effective gradient signal at each step?

Zero GPU -- pure Python 3.8+ Monte Carlo simulation.
"""
import argparse, json, math, os, random, sys
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_RL_JSONL = os.path.join(SCRIPT_DIR, "rl_pyaether_synth_v2.jsonl")
OUTPUT_JSON = os.path.join(SCRIPT_DIR, "grpo_dynamics_sim_results.json")
OUTPUT_HTML_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "..", "reports")
OUTPUT_HTML = os.path.join(OUTPUT_HTML_DIR, "report_posttrain_r59_grpo_dynamics_sim_zh.html")

DEFAULT_GROUP_SIZE = 8
DEFAULT_LR = 1e-6
DEFAULT_KL_COEF = 0.001
DEFAULT_CLIP_RATIO = 0.2
DEFAULT_MAX_STEPS = 500
DEFAULT_MC_RUNS = 50

PHASE1_PROMPTS = 50
PHASE1_STEPS = 10
PHASE2_PROMPTS = 2037
PHASE2_STEPS = 500
PHASE3_EXPAND = 1310

REWARD_ARMS = {
    "R1_binary": {"desc": "binary pass=1/fail=0", "type": "binary"},
    "R2_partial": {"desc": "4-bin partial credit", "type": "partial_4bin"},
    "R3_tool_penalty": {"desc": "R2 + tool call penalty", "type": "partial_4bin", "tool_penalty": 0.05},
    "R4_api_legality": {"desc": "R3 + API legality bonus/penalty", "type": "partial_4bin",
                        "tool_penalty": 0.05, "api_legal_bonus": 0.1, "api_illegal_penalty": -0.2},
}

@dataclass
class Prompt:
    id: str
    difficulty: str
    base_pass_rate: float
    num_apis: int
    assertion_template: str
    techlib_dep: bool
    signal_class: str
    expected_tool_calls: float = 3.0
    api_legality_rate: float = 0.85

@dataclass
class RolloutResult:
    passed: bool
    partial_score: float
    num_tool_calls: int
    api_legal: bool

@dataclass
class GRPOStep:
    step: int
    phase: int
    n_prompts: int
    avg_reward: float
    std_zero_rate: float
    effective_signal: float
    reward_hack_rate: float
    pass_rate: float
    kl_divergence: float
    gradient_norm: float

@dataclass
class SimulationResult:
    run_id: int
    arm_name: str
    steps: List[GRPOStep] = field(default_factory=list)
    final_pass_rate: float = 0.0
    total_std_zero_steps: int = 0
    hack_detected: bool = False
    hack_step: Optional[int] = None
    converged: bool = False
    converge_step: Optional[int] = None


def load_prompts(jsonl_path: str) -> List[Prompt]:
    """Load RL prompts from JSONL or fall back to synthetic generation."""
    prompts: List[Prompt] = []
    if os.path.exists(jsonl_path):
        try:
            with open(jsonl_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    rec = json.loads(line)
                    diff = rec.get("difficulty_level", rec.get("difficulty", "L2"))
                    if isinstance(diff, (int, float)):
                        diff = f"L{int(diff)}"
                    apis = rec.get("num_unique_apis", rec.get("num_apis", 3))
                    template = rec.get("assertion_template", rec.get("template", "T1"))
                    techlib = rec.get("techlib_dependency", False)
                    signal = rec.get("signal_class", "SIGNAL")
                    diff_pass = {"L1": 0.71, "L2": 0.46, "L3": 0.31, "L4": 0.21, "L5": 0.11}
                    base_pr = diff_pass.get(diff, 0.36)
                    prompts.append(Prompt(
                        id=rec.get("id", f"p{len(prompts)}"), difficulty=diff,
                        base_pass_rate=base_pr, num_apis=int(apis) if apis else 3,
                        assertion_template=str(template), techlib_dep=bool(techlib),
                        signal_class=signal,
                        expected_tool_calls=3.0 + int(apis) * 0.5 if apis else 3.0,
                        api_legality_rate=0.85))
        except Exception as e:
            print(f"  WARN: Failed to load {jsonl_path}: {e}", file=sys.stderr)

    if not prompts:
        print("  INFO: Using synthetic prompt pool (R58 distribution)", file=sys.stderr)
        diff_specs = [("L1", 1500, 0.71), ("L2", 347, 0.46), ("L3", 800, 0.31),
                      ("L4", 500, 0.21), ("L5", 200, 0.11)]
        pid = 0
        for diff, count, base_pr in diff_specs:
            for _ in range(count):
                p_all_pass = base_pr ** DEFAULT_GROUP_SIZE
                p_all_fail = (1 - base_pr) ** DEFAULT_GROUP_SIZE
                if p_all_pass > 0.30:
                    sig = "TOO_EASY"
                elif p_all_fail > 0.30:
                    sig = "TOO_HARD"
                else:
                    sig = "SIGNAL"
                prompts.append(Prompt(
                    id=f"syn_{pid}", difficulty=diff, base_pass_rate=base_pr,
                    num_apis=random.randint(1, 8), assertion_template=f"T{random.randint(1,5)}",
                    techlib_dep=random.random() > 0.7, signal_class=sig,
                    expected_tool_calls=3.0 + random.uniform(0, 4),
                    api_legality_rate=0.75 + random.uniform(0, 0.2)))
                pid += 1
    return prompts


def simulate_rollout(prompt: Prompt, model_pass_rate: float,
                     arm_config: Dict[str, Any], rng: random.Random) -> RolloutResult:
    """Simulate a single rollout for a prompt under current model state."""
    p = max(0.01, min(0.99, model_pass_rate))
    passed = rng.random() < p
    if passed:
        partial = 0.9 + rng.uniform(0, 0.1)
    else:
        base_partial = 0.1 + rng.uniform(0, 0.3)
        if prompt.techlib_dep:
            base_partial *= 0.7
        partial = min(0.75, base_partial)
    n_tools = max(1, int(rng.gauss(prompt.expected_tool_calls, 1.5)))
    api_legal = rng.random() < prompt.api_legality_rate
    return RolloutResult(passed=passed, partial_score=partial,
                          num_tool_calls=n_tools, api_legal=api_legal)


def compute_reward(rollout: RolloutResult, prompt: Prompt,
                   arm_config: Dict[str, Any]) -> float:
    """Compute reward under the specified arm."""
    arm_type = arm_config["type"]
    if arm_type == "binary":
        return 1.0 if rollout.passed else 0.0
    if rollout.passed:
        reward = 1.0
    else:
        if rollout.partial_score >= 0.75:
            reward = 0.75
        elif rollout.partial_score >= 0.5:
            reward = 0.5
        elif rollout.partial_score >= 0.25:
            reward = 0.25
        else:
            reward = 0.0
    if "tool_penalty" in arm_config:
        excess = max(0, rollout.num_tool_calls - int(prompt.expected_tool_calls))
        reward -= arm_config["tool_penalty"] * excess
        reward = max(0.0, reward)
    if "api_legal_bonus" in arm_config:
        if rollout.api_legal:
            reward += arm_config["api_legal_bonus"]
        else:
            reward += arm_config["api_illegal_penalty"]
        reward = max(0.0, min(1.0, reward))
    return reward


def simulate_grpo_step(prompts, model_state, group_size, arm_config, lr, kl_coef,
                       clip_ratio, step_num, phase, rng):
    """Simulate one GRPO training step. Returns step record + updated model state."""
    n_prompts = len(prompts)
    all_rewards, std_zero_count = [], 0
    total_advantage_mag, hack_count, pass_count, total_rollouts = 0.0, 0, 0, 0
    kl_accum, grad_norm_accum = 0.0, 0.0
    new_state = dict(model_state)

    for prompt in prompts:
        rollouts, rewards = [], []
        for _ in range(group_size):
            r = simulate_rollout(prompt, model_state.get(prompt.id, prompt.base_pass_rate),
                                 arm_config, rng)
            rollouts.append(r)
            rewards.append(compute_reward(r, prompt, arm_config))
        all_rewards.extend(rewards)
        total_rollouts += group_size
        mean_r = sum(rewards) / group_size
        var_r = sum((r - mean_r) ** 2 for r in rewards) / group_size
        std_r = math.sqrt(var_r)
        if std_r < 1e-8:
            std_zero_count += 1
            continue
        eps = 1e-4
        advantages = [(r - mean_r) / (std_r + eps) for r in rewards]
        avg_adv = sum(abs(a) for a in advantages) / group_size
        total_advantage_mag += avg_adv
        grad_norm_accum += avg_adv * std_r
        old_pr = model_state.get(prompt.id, prompt.base_pass_rate)
        new_pr_est = old_pr + lr * avg_adv * (0.5 if mean_r > old_pr else -0.3)
        kl = 0.5 * (new_pr_est - old_pr) ** 2 / max(old_pr * (1 - old_pr), 1e-6)
        kl_accum += kl
        pass_rate_group = sum(1 for r in rollouts if r.passed) / group_size
        if mean_r > 0.7 and pass_rate_group < 0.3:
            hack_count += 1
        pass_count += sum(1 for r in rollouts if r.passed)
        update = lr * avg_adv * (mean_r - old_pr) * 10
        update = max(-clip_ratio, min(clip_ratio, update))
        new_pr = max(0.01, min(0.99, old_pr + update))
        new_state[prompt.id] = new_pr

    avg_reward = sum(all_rewards) / max(len(all_rewards), 1)
    std_zero_rate = std_zero_count / max(n_prompts, 1)
    effective_signal = total_advantage_mag / max(n_prompts - std_zero_count, 1)
    hack_rate = hack_count / max(n_prompts, 1)
    overall_pass = pass_count / max(total_rollouts, 1)
    avg_kl = kl_accum / max(n_prompts, 1)
    grad_norm = grad_norm_accum / max(n_prompts, 1)
    step = GRPOStep(step=step_num, phase=phase, n_prompts=n_prompts,
                    avg_reward=avg_reward, std_zero_rate=std_zero_rate,
                    effective_signal=effective_signal, reward_hack_rate=hack_rate,
                    pass_rate=overall_pass, kl_divergence=avg_kl, gradient_norm=grad_norm)
    return step, new_state


def run_simulation(prompts, arm_name, arm_config, run_id, max_steps=DEFAULT_MAX_STEPS,
                   group_size=DEFAULT_GROUP_SIZE, lr=DEFAULT_LR, kl_coef=DEFAULT_KL_COEF,
                   clip_ratio=DEFAULT_CLIP_RATIO, rng=None, max_prompts_per_step=200):
    """Run one full GRPO training simulation.
    max_prompts_per_step: subsample prompts per step for speed (extrapolate metrics)."""
    if rng is None:
        rng = random.Random(run_id * 42 + hash(arm_name) % 10000)
    result = SimulationResult(run_id=run_id, arm_name=arm_name)
    model_state = {}
    for p in prompts:
        init_pr = p.base_pass_rate + rng.gauss(0, 0.05)
        model_state[p.id] = max(0.01, min(0.99, init_pr))
    signal_prompts = [p for p in prompts if p.signal_class == "SIGNAL"]
    all_prompts = prompts

    for step_num in range(1, max_steps + 1):
        if step_num <= PHASE1_STEPS:
            phase = 1
            active = sorted(signal_prompts, key=lambda p: -p.base_pass_rate)[:PHASE1_PROMPTS]
        elif step_num <= PHASE2_STEPS:
            phase = 2
            active = signal_prompts if signal_prompts else all_prompts[:100]
        else:
            phase = 3
            active = all_prompts[:PHASE2_PROMPTS + PHASE3_EXPAND]
        if not active:
            active = signal_prompts[:50] if signal_prompts else all_prompts[:50]
        # Subsample for speed if too many prompts
        if len(active) > max_prompts_per_step:
            active = rng.sample(active, max_prompts_per_step)
        step_record, model_state = simulate_grpo_step(
            active, model_state, group_size, arm_config, lr, kl_coef,
            clip_ratio, step_num, phase, rng)
        result.steps.append(step_record)
        if step_record.reward_hack_rate > 0.15 and not result.hack_detected:
            result.hack_detected = True
            result.hack_step = step_num
        if len(result.steps) >= 20:
            recent = result.steps[-10:]
            pr_std = math.sqrt(sum((s.pass_rate - sum(x.pass_rate for x in recent) / 10) ** 2
                                   for s in recent) / 10)
            if pr_std < 0.005 and not result.converged:
                result.converged = True
                result.converge_step = step_num
        if step_record.std_zero_rate > 0.6:
            result.total_std_zero_steps += 1
    if result.steps:
        result.final_pass_rate = result.steps[-1].pass_rate
    return result


def aggregate_results(results):
    """Aggregate Monte Carlo results across runs and arms."""
    by_arm = defaultdict(list)
    for r in results:
        by_arm[r.arm_name].append(r)
    summary = {}
    for arm_name, arm_results in by_arm.items():
        n_runs = len(arm_results)
        if n_runs == 0:
            continue
        max_len = max(len(r.steps) for r in arm_results)
        step_metrics = []
        for s in range(max_len):
            sr, ss0, ssig, sp, sh, skl, sg = [], [], [], [], [], [], []
            for r in arm_results:
                if s < len(r.steps):
                    st = r.steps[s]
                    sr.append(st.avg_reward); ss0.append(st.std_zero_rate)
                    ssig.append(st.effective_signal); sp.append(st.pass_rate)
                    sh.append(st.reward_hack_rate); skl.append(st.kl_divergence)
                    sg.append(st.gradient_norm)
            if sr:
                def stats(vals):
                    n = len(vals); m = sum(vals) / n
                    sd = math.sqrt(sum((v - m) ** 2 for v in vals) / n) if n > 1 else 0
                    return {"mean": round(m, 6), "std": round(sd, 6),
                            "min": round(min(vals), 6), "max": round(max(vals), 6)}
                step_metrics.append({"step": s + 1, "avg_reward": stats(sr),
                    "std_zero_rate": stats(ss0), "effective_signal": stats(ssig),
                    "pass_rate": stats(sp), "reward_hack_rate": stats(sh),
                    "kl_divergence": stats(skl), "gradient_norm": stats(sg)})
        final_passes = [r.final_pass_rate for r in arm_results]
        hack_detections = sum(1 for r in arm_results if r.hack_detected)
        convergences = sum(1 for r in arm_results if r.converged)
        std0_critical = sum(r.total_std_zero_steps for r in arm_results) / n_runs
        first_dr = None
        for i in range(2, len(step_metrics)):
            if (step_metrics[i]["std_zero_rate"]["mean"] > 0.6 and
                step_metrics[i-1]["std_zero_rate"]["mean"] > 0.6 and
                step_metrics[i-2]["std_zero_rate"]["mean"] > 0.6):
                first_dr = i + 1; break
        ir = step_metrics[0]["avg_reward"]["mean"] if step_metrics else 0
        fr = step_metrics[-1]["avg_reward"]["mean"] if step_metrics else 0
        ipr = step_metrics[0]["pass_rate"]["mean"] if step_metrics else 0
        fpr = step_metrics[-1]["pass_rate"]["mean"] if step_metrics else 0
        summary[arm_name] = {"n_runs": n_runs, "initial_reward": round(ir, 4),
            "final_reward": round(fr, 4), "reward_gain": round(fr - ir, 4),
            "initial_pass_rate": round(ipr, 4), "final_pass_rate": round(fpr, 4),
            "pass_rate_gain_pp": round((fpr - ipr) * 100, 2),
            "final_std_zero_rate": round(step_metrics[-1]["std_zero_rate"]["mean"], 4) if step_metrics else 0,
            "first_dr_grpo_step": first_dr,
            "hack_detection_rate": round(hack_detections / n_runs, 4),
            "convergence_rate": round(convergences / n_runs, 4),
            "avg_std0_critical_steps": round(std0_critical, 1),
            "max_reward": round(max(final_passes), 4),
            "min_reward": round(min(final_passes), 4),
            "step_metrics": step_metrics}
    return summary


def ascii_chart(values, max_val=1.0, height=10):
    if not values:
        return ""
    lines = []
    n = len(values)
    for h in range(height, 0, -1):
        threshold = h / height * max_val
        line = f"{threshold:5.2f} |"
        for v in values:
            line += "#" if v >= threshold else " "
        lines.append(line)
    lines.append("      " + "-" * n)
    return "\n".join(lines)


def generate_html(summary, config):
    arms = sorted(summary.keys())
    cmp_rows = ""
    for arm in arms:
        s = summary[arm]
        dr = f"Step {s['first_dr_grpo_step']}" if s['first_dr_grpo_step'] else "N/A"
        gc = "green" if s['reward_gain'] > 0.05 else "orange"
        sc = "red" if s['final_std_zero_rate'] > 0.5 else "green"
        hc = "red" if s['hack_detection_rate'] > 0.2 else "green"
        cmp_rows += (f"<tr><td>{arm}</td><td>{s['initial_reward']:.4f}</td>"
            f"<td>{s['final_reward']:.4f}</td><td style='color:{gc}'>+{s['reward_gain']:.4f}</td>"
            f"<td>{s['initial_pass_rate']:.1%}->{s['final_pass_rate']:.1%}</td>"
            f"<td style='color:{sc}'>{s['final_std_zero_rate']:.1%}</td>"
            f"<td>{dr}</td><td style='color:{hc}'>{s['hack_detection_rate']:.1%}</td>"
            f"<td>{s['convergence_rate']:.1%}</td></tr>")
    traj = ""
    for arm in arms:
        s = summary[arm]; sm = s["step_metrics"]
        if not sm: continue
        pr = [m["pass_rate"]["mean"] for m in sm[:100]]
        rw = [m["avg_reward"]["mean"] for m in sm[:100]]
        s0 = [m["std_zero_rate"]["mean"] for m in sm[:100]]
        traj += f"<h3>{arm}</h3><p>Pass:</p><pre>{ascii_chart(pr)}</pre>"
        traj += f"<p>std=0:</p><pre>{ascii_chart(s0)}</pre>"
        traj += f"<p>Reward:</p><pre>{ascii_chart(rw)}</pre><hr>"
    findings = []
    if arms:
        best = max(arms, key=lambda a: summary[a]["reward_gain"])
        findings.append(f"Best gain: {best} (+{summary[best]['reward_gain']:.4f})")
        st = min(arms, key=lambda a: summary[a]["final_std_zero_rate"])
        findings.append(f"Most stable: {st} ({summary[st]['final_std_zero_rate']:.1%})")
        ha = [a for a in arms if summary[a]["hack_detection_rate"] > 0.2]
        findings.append(f"Hack>20%: {', '.join(ha) if ha else 'NONE'}")
        da = [a for a in arms if summary[a]["first_dr_grpo_step"]]
        if da:
            e = min(da, key=lambda a: summary[a]["first_dr_grpo_step"])
            findings.append(f"Dr.GRPO: {e} Step {summary[e]['first_dr_grpo_step']}")
        else:
            findings.append("No Dr.GRPO trigger (OK)")
        vc = ", ".join(f"{a}={summary[a]['final_std_zero_rate']:.1%}" for a in arms)
        findings.append(f"Vision 78.7% vs BaiZe: {vc} -> 36%>>9.2%")
    fh = "".join(f"<div class='ok'>- {f}</div>" for f in findings)
    s0r = ""
    for arm in arms:
        s = summary[arm]; dr = s["first_dr_grpo_step"]
        a = "HIGH:Dr.GRPO" if s["final_std_zero_rate"]>0.6 else ("MED:G=12" if s["final_std_zero_rate"]>0.4 else "LOW:ok")
        s0r += f"<tr><td>{arm}</td><td>{s['final_std_zero_rate']:.1%}</td><td>{s['avg_std0_critical_steps']:.1f}</td><td>{f'S{dr}' if dr else 'N/A'}</td><td>{a}</td></tr>"
    hrr = ""
    for arm in arms:
        s = summary[arm]; hr = s["hack_detection_rate"]
        r = "HIGH" if hr>0.3 else ("MED" if hr>0.1 else "LOW")
        m = "Hook+audit" if hr>0.3 else ("Monitor" if hr>0.1 else "Routine")
        hrr += f"<tr><td>{arm}</td><td>{hr:.1%}</td><td>{r}</td><td>{m}</td></tr>"
    cr = ""
    for arm in arms:
        s = summary[arm]; sm = s["step_metrics"]
        p1 = sm[9]["pass_rate"]["mean"] if len(sm)>9 else 0
        p250 = sm[249]["pass_rate"]["mean"] if len(sm)>249 else 0
        p500 = sm[-1]["pass_rate"]["mean"] if sm else 0
        cr += f"<tr><td>{arm}</td><td>{p1:.1%}</td><td>{p250:.1%}</td><td>{p500:.1%}</td><td>+{s['pass_rate_gain_pp']:.1f}pp</td></tr>"
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>R59 GRPO Dynamics</title>
<style>
body{{font-family:'Microsoft YaHei',sans-serif;max-width:1200px;margin:0 auto;padding:20px;background:#f5f5f5;color:#333;line-height:1.6}}
h1{{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px}}
h2{{color:#2c3e50;border-bottom:1px solid #bdc3c7;padding-bottom:5px;margin-top:30px}}
table{{border-collapse:collapse;width:100%;margin:15px 0}}
th,td{{border:1px solid #ddd;padding:8px 12px;text-align:center}}
th{{background:#2c3e50;color:white}}tr:nth-child(even){{background:#ecf0f1}}
pre{{background:#2c3e50;color:#2ecc71;padding:15px;border-radius:5px;overflow-x:auto;font-size:11px}}
.note{{background:#fef9e7;border-left:4px solid #f39c12;padding:10px 15px;margin:15px 0}}
.warn{{background:#fdedec;border-left:4px solid #e74c3c;padding:10px 15px;margin:15px 0}}
.ok{{background:#eafaf1;border-left:4px solid #27ae60;padding:10px 15px;margin:15px 0}}
code{{background:#ecf0f1;padding:2px 6px;border-radius:3px}}
</style></head><body>
<h1>R59: GRPO 训练动力学蒙特卡洛模拟器</h1>
<p>2026-11-08 wake107 | 零GPU | Python 3.8+</p>
<div class="note"><b>局限</b>: 简化模型。相对比较有参考价值。11/9后用实测替换。</div>
<h2>1. 配置</h2>
<table><tr><th>参数</th><th>值</th></tr>
<tr><td>MC/arm</td><td>{config['mc_runs']}</td></tr>
<tr><td>Steps</td><td>{config['max_steps']}</td></tr>
<tr><td>G</td><td>{config['group_size']}</td></tr>
<tr><td>Arms</td><td>{len(arms)}</td></tr></table>
<h2>2. 四臂对比</h2>
<table><tr><th>臂</th><th>初始</th><th>最终</th><th>增益</th><th>通过率</th><th>std=0</th><th>Dr.GRPO</th><th>作弊</th><th>收敛</th></tr>
{cmp_rows}</table>
<h2>3. 发现</h2>{fh}
<h2>4. 轨迹</h2>{traj}
<h2>5. std=0临界</h2>
<table><tr><th>臂</th><th>std=0</th><th>临界步</th><th>触发</th><th>建议</th></tr>{s0r}</table>
<h2>6. 作弊</h2>
<table><tr><th>臂</th><th>作弊率</th><th>风险</th><th>缓解</th></tr>{hrr}</table>
<h2>7. 课程</h2>
<table><tr><th>臂</th><th>P1</th><th>P2中</th><th>P2末</th><th>增益</th></tr>{cr}</table>
<h2>8. 11/9建议</h2>
<div class="ok"><ol><li>起步R2</li><li>Phase1 50px10s</li><li>Phase2 2037x500 Step200查std=0</li><li>3步std=0>60%->Dr.GRPO</li><li>Step100 cheat>15%暂停</li><li>Step500 +3pp->继续</li></ol></div>
<div class="warn">11/9后用实测替换。核心=相对比较。</div>
<p style="text-align:center;color:#7f8c8d;margin-top:40px">R59 2026-11-08</p>
</body></html>"""


def main():
    parser = argparse.ArgumentParser(description="R59 GRPO Dynamics MC Simulator")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--mc-runs", type=int, default=DEFAULT_MC_RUNS)
    parser.add_argument("--max-steps", type=int, default=DEFAULT_MAX_STEPS)
    parser.add_argument("--group-size", type=int, default=DEFAULT_GROUP_SIZE)
    parser.add_argument("--lr", type=float, default=DEFAULT_LR)
    parser.add_argument("--kl-coef", type=float, default=DEFAULT_KL_COEF)
    parser.add_argument("--clip-ratio", type=float, default=DEFAULT_CLIP_RATIO)
    parser.add_argument("--html", action="store_true", default=True)
    parser.add_argument("--no-html", dest="html", action="store_false")
    parser.add_argument("--rl-jsonl", type=str, default=DEFAULT_RL_JSONL)
    parser.add_argument("--max-prompts", type=int, default=200,
                        help="Max prompts per step (subsampling for speed)")
    args = parser.parse_args()
    mc_runs = 5 if args.dry_run else args.mc_runs
    max_steps = 50 if args.dry_run else args.max_steps
    print("=" * 60)
    print("R59: GRPO Training Dynamics Monte Carlo Simulator")
    print("=" * 60)
    print(f"  MC/arm: {mc_runs}  Steps: {max_steps}  G: {args.group_size}")
    print(f"  Arms: {list(REWARD_ARMS.keys())}")

    print("\n[1/4] Loading prompts...")
    prompts = load_prompts(args.rl_jsonl)
    sig = sum(1 for p in prompts if p.signal_class == "SIGNAL")
    print(f"  Loaded {len(prompts)} ({sig} SIGNAL)")
    if not prompts:
        print("  ERROR!", file=sys.stderr); sys.exit(1)

    print(f"\n[2/4] {mc_runs}x{len(REWARD_ARMS)} sims...")
    all_r = []
    total = mc_runs * len(REWARD_ARMS)
    done = 0
    for an, ac in REWARD_ARMS.items():
        print(f"\n  {an}:")
        for rid in range(mc_runs):
            r = run_simulation(prompts, an, ac, rid, max_steps=max_steps,
                               group_size=args.group_size, lr=args.lr,
                               kl_coef=args.kl_coef, clip_ratio=args.clip_ratio,
                               max_prompts_per_step=args.max_prompts)
            all_r.append(r)
            done += 1
            if done % 10 == 0 or done == total:
                print(f"    [{done}/{total}] {an} r{rid} pass={r.final_pass_rate:.3f} "
                      f"std0={r.total_std_zero_steps} hack={'Y' if r.hack_detected else 'N'}")

    print("\n[3/4] Aggregating...")
    summary = aggregate_results(all_r)
    cfg = {"mc_runs": mc_runs, "max_steps": max_steps, "group_size": args.group_size,
           "lr": args.lr, "kl_coef": args.kl_coef, "clip_ratio": args.clip_ratio}
    print("\n  Arm                  Init    Final   Gain    S0     Hack")
    print("  " + "-" * 60)
    for a in sorted(summary.keys()):
        s = summary[a]
        print(f"  {a:<20} {s['initial_reward']:.4f}  {s['final_reward']:.4f}  "
              f"+{s['reward_gain']:.4f}  {s['final_std_zero_rate']:.1%}  {s['hack_detection_rate']:.1%}")

    print("\n[4/4] Saving...")
    out = {"r59": {"date": "2026-11-08", "wake": 107, "config": cfg,
                   "n_prompts": len(prompts), "n_signal": sig,
                   "arms": list(REWARD_ARMS.keys()), "summary": summary}}
    jp = os.path.join(SCRIPT_DIR, "grpo_dynamics_sim_results.json")
    with open(jp, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"  JSON: {jp} ({os.path.getsize(jp)} B)")
    if args.html:
        os.makedirs(OUTPUT_HTML_DIR, exist_ok=True)
        with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
            f.write(generate_html(summary, cfg))
        print(f"  HTML: {OUTPUT_HTML} ({os.path.getsize(OUTPUT_HTML)} B)")
    print(f"\nDone. {total} sims.")
    if summary:
        bg = max(summary.keys(), key=lambda a: summary[a]["reward_gain"])
        ms = min(summary.keys(), key=lambda a: summary[a]["final_std_zero_rate"])
        print(f"  Best gain: {bg}  Most stable: {ms}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
