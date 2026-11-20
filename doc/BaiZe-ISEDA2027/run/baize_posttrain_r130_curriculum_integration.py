#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
R130 (2026-11-10 wake177): GRPO Curriculum Integration with R5 Process Reward

Integrates three prior research outputs into a single executable training schedule:
  - R74: Adaptive curriculum strategy (best of 4 strategies via Monte Carlo)
  - R128: 3,347 verified RL tasks across 5 difficulty levels (L1-L5)
  - R129: R5 process reward (outcome + recovery + progress - efficiency - antigame)

Designs a concrete 5-phase GRPO training schedule with:
  1. Per-phase task sampling, reward config, and GRPO hyperparams
  2. Transition criteria between phases (pass rate, advantage std, step count)
  3. Anti-forgetting replay buffer (epsilon-greedy sampling from prior levels)
  4. Per-phase GRPO signal quality simulation (advantage variance, learnability)
  5. Verl-compatible YAML configuration output
  6. Wall-clock budget estimation (sandbox-bound, not GPU-bound)

Zero GPU. Pure Python 3.8+ stdlib. No external dependencies.
"⚠️ Simulation results are NOT transferable to BaiZe (surrogate analysis).
"""

import json
import math
import random
import sys
import os
from collections import defaultdict

# ═══════════════════════════════════════════════════════════════════════
# 1. Configuration Constants (from R73, R74, R128, R129)
# ═══════════════════════════════════════════════════════════════════════

TASK_COUNTS = {"L1": 1500, "L2": 347, "L3": 800, "L4": 500, "L5": 200}
TOTAL_TASKS = sum(TASK_COUNTS.values())  # 3347

R5_WEIGHTS = {
    "outcome": 0.60, "recovery": 0.20, "progress": 0.10,
    "efficiency": 0.10, "antigame": 1.0,
}

GRPO_BASE = {
    "kl_coeff": 0.04, "clip_range": 0.2, "group_size": 8,
    "lr": 1e-5, "entropy_coeff": 0.001, "max_turns": 10,
    "context_length": 16384,
}

ADAPTIVE_THRESHOLDS = {
    "advance_pass_rate": 0.75, "advance_min_steps": 40,
    "advance_adv_std": 0.05, "stagnation_steps": 30,
    "stagnation_threshold": 0.02, "collapse_entropy": 0.01,
    "divergence_kl": 5.0,
}

INITIAL_PASS_RATES = {
    "L1": 0.65, "L2": 0.45, "L3": 0.25, "L4": 0.12, "L5": 0.05,
}

SANDBOX_TIMING = {
    "search_apis_ms": 20, "get_api_details_ms": 5, "run_code_ms": 500,
    "avg_turns_per_rollout": {"L1": 4, "L2": 6, "L3": 8, "L4": 10, "L5": 12},
}

# ═══════════════════════════════════════════════════════════════════════
# 2. Phase Definitions
# ═══════════════════════════════════════════════════════════════════════

PHASES = [
    {
        "id": 0, "name": "Warmup",
        "description": "L1-only pipeline verification. Binary reward (R0).",
        "levels": ["L1"], "steps": 50, "reward_arm": "R0",
        "r5_enabled": False, "replay_ratio": 0.0,
        "task_sample_strategy": "uniform_within_level",
        "lr_override": 1e-5, "kl_override": 0.04,
        "advance_criteria": {"min_pass_rate": 0.70, "min_steps": 30, "min_adv_std": 0.05},
        "go_no_go": "Pipeline smoke test. GO if advantage std > 0.05 for >= 20 consecutive steps AND sandbox < 2s/call.",
    },
    {
        "id": 1, "name": "Foundation",
        "description": "L1+L2 mixed. Introduce R5 recovery signal.",
        "levels": ["L1", "L2"], "steps": 100, "reward_arm": "R2",
        "r5_enabled": True, "replay_ratio": 0.15,
        "task_sample_strategy": "adaptive",
        "lr_override": 1e-5, "kl_override": 0.04,
        "advance_criteria": {"min_pass_rate": 0.60, "min_steps": 60, "min_adv_std": 0.05},
        "go_no_go": "L2 pass rate > 50% AND R5 recovery signal contributes to >= 30% of non-zero advantages.",
    },
    {
        "id": 2, "name": "Development",
        "description": "L2+L3 with full R5 process reward.",
        "levels": ["L2", "L3"], "steps": 150, "reward_arm": "R2",
        "r5_enabled": True, "replay_ratio": 0.20,
        "task_sample_strategy": "adaptive",
        "lr_override": 8e-6, "kl_override": 0.04,
        "advance_criteria": {"min_pass_rate": 0.50, "min_steps": 80, "min_adv_std": 0.05},
        "go_no_go": "L3 pass rate > 35% AND efficiency penalty triggers on < 10% of rollouts.",
    },
    {
        "id": 3, "name": "Refinement",
        "description": "L3+L4 adaptive curriculum. Full anti-gaming enforcement.",
        "levels": ["L3", "L4"], "steps": 150, "reward_arm": "R3",
        "r5_enabled": True, "replay_ratio": 0.25,
        "task_sample_strategy": "adaptive",
        "lr_override": 5e-6, "kl_override": 0.04,
        "advance_criteria": {"min_pass_rate": 0.40, "min_steps": 80, "min_adv_std": 0.05},
        "go_no_go": "L4 pass rate > 20% AND cheat rate < 5% AND no CRITICAL hack (H2/H3/H4).",
    },
    {
        "id": 4, "name": "Mastery",
        "description": "L4+L5 full difficulty. All R5 components + anti-gaming.",
        "levels": ["L4", "L5"], "steps": 100, "reward_arm": "R3",
        "r5_enabled": True, "replay_ratio": 0.30,
        "task_sample_strategy": "adaptive",
        "lr_override": 3e-6, "kl_override": 0.04,
        "advance_criteria": None,
        "go_no_go": "Final eval on 158-task EDA-Eval-PyAether. GO if Pass@1 >= 65% (M2).",
    },
]

# ═══════════════════════════════════════════════════════════════════════
# 3. R5 Process Reward Simulator (simplified from R129)
# ═══════════════════════════════════════════════════════════════════════

def compute_r5_reward(outcome, n_errors, n_recoveries, has_search, has_detail,
                      has_execution, trivial_error_ratio, n_retries):
    """Compute R5 process reward (from R129 formula)."""
    r_outcome = outcome * R5_WEIGHTS["outcome"]
    recovery_raw = sum(0.15 * (0.85 ** i) for i in range(min(n_recoveries, 10)))
    resilience_bonus = 0.05 if n_recoveries > 0 and outcome > 0 else 0.0
    r_recovery = min(recovery_raw + resilience_bonus, 0.80) * R5_WEIGHTS["recovery"]
    progress = 0.0
    if has_search: progress += 0.05
    if has_detail: progress += 0.05
    if has_execution: progress += 0.05
    if outcome > 0: progress += 0.10
    r_progress = progress * R5_WEIGHTS["progress"]
    eff_pen = min(max(0, (n_errors - 3) * 0.05), 0.30) * R5_WEIGHTS["efficiency"]
    anti_pen = R5_WEIGHTS["antigame"] * 0.10 if trivial_error_ratio > 0.50 else 0.0
    r5 = r_outcome + r_recovery + r_progress - eff_pen - anti_pen
    return max(0.0, min(1.0, r5))


def simulate_rollout(pass_rate, level, r5_enabled, rng):
    """Simulate a single rollout for a task at given difficulty level."""
    passed = 1 if rng.random() < pass_rate else 0
    avg_turns = SANDBOX_TIMING["avg_turns_per_rollout"][level]
    if passed:
        n_errors = rng.randint(1, max(2, avg_turns // 3))
        n_recoveries = n_errors
        trivial_ratio = rng.uniform(0.0, 0.3)
    else:
        n_errors = rng.randint(2, max(4, avg_turns // 2))
        n_recoveries = rng.randint(0, max(1, n_errors - 2))
        trivial_ratio = rng.uniform(0.0, 0.6)
    has_search = rng.random() < 0.7
    has_detail = rng.random() < 0.5
    has_execution = True
    if r5_enabled:
        reward = compute_r5_reward(
            passed, n_errors, n_recoveries, has_search, has_detail,
            has_execution, trivial_ratio, n_errors)
    else:
        reward = float(passed)
    return (reward, passed, n_errors, n_recoveries, has_search,
            has_detail, has_execution, trivial_ratio)


# ═══════════════════════════════════════════════════════════════════════
# 4. GRPO Group Simulation
# ═══════════════════════════════════════════════════════════════════════

def simulate_grpo_group(pass_rate, level, r5_enabled, group_size=8, rng=None):
    """Simulate one GRPO group (G rollouts of same task)."""
    if rng is None: rng = random.Random()
    rewards = []
    n_passed = 0
    total_errors = 0
    total_recoveries = 0
    for _ in range(group_size):
        r, passed, n_err, n_rec, _, _, _, _ = simulate_rollout(
            pass_rate, level, r5_enabled, rng)
        rewards.append(r)
        n_passed += passed
        total_errors += n_err
        total_recoveries += n_rec
    mean_r = sum(rewards) / group_size
    std_r = (sum((r - mean_r) ** 2 for r in rewards) / group_size) ** 0.5
    if std_r > 1e-8:
        advantages = [(r - mean_r) / std_r for r in rewards]
    else:
        advantages = [0.0] * group_size
    n_nonzero_adv = sum(1 for a in advantages if abs(a) > 1e-6)
    signal_rate = n_nonzero_adv / group_size
    distinct_rewards = len(set(round(r, 4) for r in rewards))
    learnable = distinct_rewards >= 2 and std_r > 0.01
    return {
        "rewards": [round(r, 4) for r in rewards],
        "mean_reward": round(mean_r, 4),
        "std_reward": round(std_r, 4),
        "advantages": [round(a, 4) for a in advantages],
        "n_nonzero_advantages": n_nonzero_adv,
        "signal_rate": round(signal_rate, 4),
        "n_passed": n_passed,
        "pass_rate": round(n_passed / group_size, 4),
        "distinct_rewards": distinct_rewards,
        "learnable": learnable,
        "avg_errors": round(total_errors / group_size, 2),
        "avg_recoveries": round(total_recoveries / group_size, 2),
    }

# ═══════════════════════════════════════════════════════════════════════
# 5. Curriculum Phase Simulator
# ═══════════════════════════════════════════════════════════════════════

def simulate_phase(phase, initial_pass_rates, n_sim_groups=50, seed=42):
    """Simulate one curriculum phase with learning dynamics."""
    rng = random.Random(seed + phase["id"])
    levels = phase["levels"]
    replay_ratio = phase["replay_ratio"]
    current_rates = dict(initial_pass_rates)
    ceiling = {"L1": 0.90, "L2": 0.80, "L3": 0.65, "L4": 0.45, "L5": 0.25}
    lr_effect = phase["lr_override"] / 1e-5
    results = {
        "phase_id": phase["id"], "phase_name": phase["name"],
        "steps": phase["steps"], "levels": levels,
        "reward_arm": phase["reward_arm"], "r5_enabled": phase["r5_enabled"],
        "per_step": [], "per_level_summary": {}, "phase_summary": {},
    }
    all_group_results = []
    for step in range(phase["steps"]):
        if phase["task_sample_strategy"] == "adaptive" and len(levels) > 1:
            signals = {lv: current_rates[lv] * (1 - current_rates[lv]) for lv in levels}
            total_sig = sum(signals.values())
            if total_sig > 0:
                r_val = rng.random() * total_sig
                cum = 0
                chosen_level = levels[-1]
                for lv in levels:
                    cum += signals[lv]
                    if r_val <= cum:
                        chosen_level = lv
                        break
            else:
                chosen_level = rng.choice(levels)
        else:
            chosen_level = rng.choice(levels)
        if replay_ratio > 0 and rng.random() < replay_ratio:
            all_levels = ["L1", "L2", "L3", "L4", "L5"]
            prior_levels = [lv for lv in all_levels
                            if lv not in levels and current_rates[lv] < 0.99]
            if prior_levels:
                chosen_level = rng.choice(prior_levels)
        group_result = simulate_grpo_group(
            current_rates[chosen_level], chosen_level,
            phase["r5_enabled"], GRPO_BASE["group_size"], rng)
        group_result["step"] = step
        group_result["level"] = chosen_level
        all_group_results.append(group_result)
        if step % 10 == 0 or step == phase["steps"] - 1:
            results["per_step"].append({
                "step": step, "level": chosen_level,
                "pass_rate": group_result["pass_rate"],
                "mean_reward": group_result["mean_reward"],
                "adv_std": group_result["std_reward"],
                "signal_rate": group_result["signal_rate"],
                "learnable": group_result["learnable"],
            })
        for lv in levels:
            ceil = ceiling[lv]
            improvement = (ceil - current_rates[lv]) * (1 - math.exp(-lr_effect * 0.02))
            current_rates[lv] = min(ceil, current_rates[lv] + improvement)
    for lv in levels:
        lv_groups = [g for g in all_group_results if g["level"] == lv]
        if lv_groups:
            results["per_level_summary"][lv] = {
                "n_groups": len(lv_groups),
                "initial_pass_rate": initial_pass_rates[lv],
                "final_pass_rate": round(current_rates[lv], 4),
                "improvement": round(current_rates[lv] - initial_pass_rates[lv], 4),
                "avg_reward": round(sum(g["mean_reward"] for g in lv_groups) / len(lv_groups), 4),
                "avg_adv_std": round(sum(g["std_reward"] for g in lv_groups) / len(lv_groups), 4),
                "avg_signal_rate": round(sum(g["signal_rate"] for g in lv_groups) / len(lv_groups), 4),
                "learnable_pct": round(sum(1 for g in lv_groups if g["learnable"]) / len(lv_groups), 4),
                "avg_errors": round(sum(g["avg_errors"] for g in lv_groups) / len(lv_groups), 2),
                "avg_recoveries": round(sum(g["avg_recoveries"] for g in lv_groups) / len(lv_groups), 2),
            }
    all_rewards = [g["mean_reward"] for g in all_group_results]
    all_adv_stds = [g["std_reward"] for g in all_group_results]
    all_signals = [g["signal_rate"] for g in all_group_results]
    n_learnable = sum(1 for g in all_group_results if g["learnable"])
    results["phase_summary"] = {
        "total_groups": len(all_group_results),
        "avg_reward": round(sum(all_rewards) / len(all_rewards), 4) if all_rewards else 0,
        "avg_adv_std": round(sum(all_adv_stds) / len(all_adv_stds), 4) if all_adv_stds else 0,
        "avg_signal_rate": round(sum(all_signals) / len(all_signals), 4) if all_signals else 0,
        "learnable_pct": round(n_learnable / len(all_group_results), 4) if all_group_results else 0,
        "pass_rates_after": {lv: round(current_rates[lv], 4) for lv in levels},
    }
    for lv in levels:
        initial_pass_rates[lv] = current_rates[lv]
    return results, initial_pass_rates, all_group_results

# ═══════════════════════════════════════════════════════════════════════
# 6. Wall-Clock Budget Estimation
# ═══════════════════════════════════════════════════════════════════════

def estimate_wall_clock(phase, n_sandbox_parallel=4):
    """Estimate wall-clock time for a phase (sandbox-bound, not GPU-bound)."""
    n_groups = phase["steps"]
    avg_turns_list = [SANDBOX_TIMING["avg_turns_per_rollout"][lv] for lv in phase["levels"]]
    avg_turns = sum(avg_turns_list) / len(avg_turns_list)
    avg_call_time_ms = (
        SANDBOX_TIMING["search_apis_ms"] * 0.3 +
        SANDBOX_TIMING["get_api_details_ms"] * 0.2 +
        SANDBOX_TIMING["run_code_ms"] * 0.5)
    rollout_time_ms = avg_turns * avg_call_time_ms
    group_time_ms = rollout_time_ms * (GRPO_BASE["group_size"] / n_sandbox_parallel)
    total_ms = n_groups * group_time_ms
    total_hours = total_ms / (1000 * 3600)
    return {
        "phase_id": phase["id"], "phase_name": phase["name"],
        "n_groups": n_groups, "avg_turns_per_rollout": round(avg_turns, 1),
        "avg_rollout_time_ms": round(rollout_time_ms, 1),
        "group_time_ms": round(group_time_ms, 1),
        "sandbox_parallelism": n_sandbox_parallel,
        "total_hours": round(total_hours, 2),
        "total_minutes": round(total_ms / 60000, 1),
    }


# ═══════════════════════════════════════════════════════════════════════
# 7. Replay Buffer & Transition Design
# ═══════════════════════════════════════════════════════════════════════

def design_replay_buffer():
    """Design the anti-forgetting replay buffer schedule."""
    replay_design = []
    all_levels = ["L1", "L2", "L3", "L4", "L5"]
    for phase in PHASES:
        current_levels = set(phase["levels"])
        prior_levels = [lv for lv in all_levels
                        if lv not in current_levels
                        and all_levels.index(lv) < max(all_levels.index(l) for l in current_levels)]
        if not prior_levels:
            ratio, source = 0.0, []
        else:
            ratio = phase["replay_ratio"]
            source = prior_levels
        if source and ratio > 0:
            source_counts = {lv: TASK_COUNTS[lv] for lv in source if lv in TASK_COUNTS}
            total_source = sum(source_counts.values())
            source_dist = {lv: round(ratio * c / total_source, 4) for lv, c in source_counts.items()}
        else:
            source_dist = {}
        replay_design.append({
            "phase_id": phase["id"], "phase_name": phase["name"],
            "current_levels": phase["levels"], "replay_ratio": ratio,
            "replay_sources": source, "replay_distribution": source_dist,
            "n_replay_tasks_available": sum(TASK_COUNTS.get(lv, 0) for lv in source),
            "rationale": "No prior levels" if ratio == 0 else
                         f"Prevent forgetting of {'+'.join(source)} while training on {'+'.join(phase['levels'])}",
        })
    return replay_design


def design_transition_criteria():
    """Design criteria for transitioning between curriculum phases."""
    transitions = []
    for i, phase in enumerate(PHASES):
        if phase.get("advance_criteria") is None:
            transitions.append({
                "from_phase": phase["id"], "to_phase": None,
                "criteria": "FINAL PHASE",
                "action": "Run full 158-task eval (5-run) and check M1-M4 milestones",
            })
            continue
        ac = phase["advance_criteria"]
        next_phase = PHASES[i + 1] if i + 1 < len(PHASES) else None
        transitions.append({
            "from_phase": phase["id"], "from_name": phase["name"],
            "to_phase": next_phase["id"] if next_phase else None,
            "to_name": next_phase["name"] if next_phase else "EVAL",
            "criteria": ac,
            "safety_checks": {
                "collapse": f"entropy < {ADAPTIVE_THRESHOLDS['collapse_entropy']} -> STOP",
                "divergence": f"KL > {ADAPTIVE_THRESHOLDS['divergence_kl']} -> lower lr",
                "stagnation": f"{ADAPTIVE_THRESHOLDS['stagnation_steps']} steps <{ADAPTIVE_THRESHOLDS['stagnation_threshold']*100}% improvement -> fallback",
                "cheat": "cheat_rate > 5% -> ALERT; CRITICAL hack -> ABORT",
            },
            "fallback": "Revert to previous phase for 20 steps, then retry",
            "go_no_go": phase["go_no_go"],
        })
    return transitions

# ═══════════════════════════════════════════════════════════════════════
# 8. Verl-Compatible Configuration Generator
# ═══════════════════════════════════════════════════════════════════════

def generate_verl_config():
    """Generate verl-compatible YAML configuration for the full curriculum."""
    lines = [
        "# BaiZe Post-Train GRPO Curriculum Configuration (R130)",
        "# Integrates R74 (Adaptive) + R128 (3347 tasks) + R129 (R5 reward)",
        "# Generated: 2026-11-10 | Surrogate design, not validated on BaiZe",
        "",
        "trainer:",
        "  total_epochs: 1",
        "  save_freq: 50",
        "  project_name: baize_posttrain_rl",
        "",
        "actor:",
        f"  learning_rate: {GRPO_BASE['lr']}",
        f"  kl_coeff: {GRPO_BASE['kl_coeff']}",
        f"  clip_range: {GRPO_BASE['clip_range']}",
        f"  entropy_coeff: {GRPO_BASE['entropy_coeff']}",
        f"  context_length: {GRPO_BASE['context_length']}",
        "",
        "rollout:",
        "  name: sglang",
        "  multi_turn: true",
        "  mode: async",
        f"  group_size: {GRPO_BASE['group_size']}",
        f"  max_turns: {GRPO_BASE['max_turns']}",
        "",
        "reward:",
        "  function: compute_score_with_process  # R129 R5",
        "  outcome_arm: R2",
        "  process_layer: R5",
        "  antigame_enabled: true",
        "  efficiency_penalty: true",
        "  recovery_diminishing: 0.85",
        "",
        "data:",
        "  train_files: rl_pyaether_synth_v2_verified.jsonl  # R128",
        "  contamination_check: true",
        "",
        "curriculum:",
    ]
    for phase in PHASES:
        lines.extend([
            f"  - phase: {phase['id']}",
            f"    name: {phase['name']}",
            f"    levels: {phase['levels']}",
            f"    steps: {phase['steps']}",
            f"    reward_arm: {phase['reward_arm']}",
            f"    r5_enabled: {phase['r5_enabled']}",
            f"    replay_ratio: {phase['replay_ratio']}",
            f"    sampling: {phase['task_sample_strategy']}",
            f"    lr: {phase['lr_override']}",
            f"    kl: {phase['kl_override']}",
        ])
        if phase.get("advance_criteria"):
            ac = phase["advance_criteria"]
            lines.extend([
                "    advance_criteria:",
                f"      min_pass_rate: {ac['min_pass_rate']}",
                f"      min_steps: {ac['min_steps']}",
                f"      min_adv_std: {ac['min_adv_std']}",
            ])
        lines.append("")
    lines.extend([
        "anti_cheat:",
        "  ptu_hook: true  # PreToolUse (R69, R75)",
        "  cheat_rate_report: true",
        "  critical_hack_abort: true  # H2/H3/H4 -> stop",
        "  max_cheat_rate: 0.05",
        "",
        "sandbox:",
        "  type: local  # or ssh_tunnel (R1 Tunnel-SOP)",
        "  parallel: 4",
        "  timeout_per_call: 30",
        "  api_whitelist: true  # PTU-04",
        "  call_ordering: true  # PTU-05",
        "",
        "eval:",
        "  dataset: EDA-Eval-PyAether-v20260311.jsonl  # 158 tasks",
        "  n_runs: 5  # 5-run mean+std",
        "  timeout: 2500",
        "  parallel: 8",
        "  fresh_context: true",
    ])
    return "\n".join(lines)

# ═══════════════════════════════════════════════════════════════════════
# 9. Main Execution
# ═══════════════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="R130: GRPO Curriculum Integration with R5 Process Reward")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--json", type=str, default=None, help="Output JSON report path")
    parser.add_argument("--yaml", action="store_true", help="Print verl YAML config")
    parser.add_argument("--quick", action="store_true", help="Quick mode")
    args = parser.parse_args()

    print("=" * 72)
    print("R130: GRPO Curriculum Integration with R5 Process Reward")
    print("Integrates: R74 (Adaptive) + R128 (3347 tasks) + R129 (R5 reward)")
    print("=" * 72)

    # Simulate all phases
    print("\n[1/5] Simulating 5 curriculum phases...")
    pass_rates = dict(INITIAL_PASS_RATES)
    all_phase_results = []
    all_group_data = []
    n_sim = 10 if args.quick else 50

    for phase in PHASES:
        print(f"\n  Phase {phase['id']}: {phase['name']} "
              f"(levels={phase['levels']}, steps={phase['steps']}, "
              f"R5={'ON' if phase['r5_enabled'] else 'OFF'}, "
              f"replay={phase['replay_ratio']})")
        phase_result, pass_rates, group_data = simulate_phase(
            phase, pass_rates, n_sim_groups=n_sim, seed=42 + phase["id"])
        all_phase_results.append(phase_result)
        all_group_data.extend(group_data)
        ps = phase_result["phase_summary"]
        print(f"    avg_reward={ps['avg_reward']:.4f} "
              f"avg_adv_std={ps['avg_adv_std']:.4f} "
              f"signal_rate={ps['avg_signal_rate']:.4f} "
              f"learnable={ps['learnable_pct']:.1%}")
        for lv, lv_s in phase_result["per_level_summary"].items():
            print(f"    {lv}: pass {lv_s['initial_pass_rate']:.2f}->"
                  f"{lv_s['final_pass_rate']:.2f} "
                  f"(+{lv_s['improvement']:.4f}) "
                  f"learnable={lv_s['learnable_pct']:.1%} "
                  f"avg_err={lv_s['avg_errors']:.1f} "
                  f"avg_rec={lv_s['avg_recoveries']:.1f}")

    # Wall-clock budget
    print("\n[2/5] Wall-clock budget estimation (sandbox-bound)...")
    budget = []
    total_hours = 0
    for phase in PHASES:
        wc = estimate_wall_clock(phase, n_sandbox_parallel=4)
        budget.append(wc)
        total_hours += wc["total_hours"]
        print(f"  Phase {wc['phase_id']} ({wc['phase_name']}): "
              f"{wc['total_hours']:.2f}h ({wc['n_groups']} groups)")
    print(f"  TOTAL: {total_hours:.2f}h ({total_hours/24:.1f} days) with 4 parallel sandboxes")

    # Replay buffer
    print("\n[3/5] Anti-forgetting replay buffer design...")
    replay = design_replay_buffer()
    for rp in replay:
        print(f"  Phase {rp['phase_id']} ({rp['phase_name']}): "
              f"replay={rp['replay_ratio']:.0%} from {rp['replay_sources']}")

    # Transition criteria
    print("\n[4/5] Transition criteria & safety checks...")
    transitions = design_transition_criteria()
    for tr in transitions:
        if tr["to_phase"] is not None:
            print(f"  Phase {tr['from_phase']} ({tr['from_name']}) -> "
                  f"Phase {tr['to_phase']} ({tr['to_name']})")
            print(f"    Criteria: pass>= {tr['criteria']['min_pass_rate']}, "
                  f"steps>= {tr['criteria']['min_steps']}, "
                  f"adv_std> {tr['criteria']['min_adv_std']}")
        else:
            print(f"  Phase {tr['from_phase']}: {tr['criteria']}")

    # Verl config
    print("\n[5/5] Generating verl-compatible configuration...")
    verl_yaml = generate_verl_config()
    if args.yaml:
        print("\n" + verl_yaml)
    else:
        print(f"  Config generated ({len(verl_yaml)} chars). Use --yaml to print.")

    # Summary
    total_steps = sum(p["steps"] for p in PHASES)
    total_groups = len(all_group_data)
    overall_learnable = sum(1 for g in all_group_data if g["learnable"]) / total_groups
    overall_signal = sum(g["signal_rate"] for g in all_group_data) / total_groups

    print(f"\n{'=' * 72}")
    print(f"SUMMARY")
    print(f"{'=' * 72}")
    print(f"  Total curriculum steps: {total_steps}")
    print(f"  Total simulated groups: {total_groups}")
    print(f"  Overall learnable rate: {overall_learnable:.1%}")
    print(f"  Overall signal rate: {overall_signal:.4f}")
    print(f"  Total wall-clock budget: {total_hours:.2f}h ({total_hours/24:.1f} days)")
    print(f"  Replay buffer: max 30% at Phase 4")
    print(f"  R5 process reward: enabled from Phase 1 onwards")
    print(f"  Anti-gaming: full enforcement from Phase 3")
    print(f"  Surrogate simulation, NOT transferable to BaiZe")

    # JSON output
    if args.json:
        report = {
            "r130_metadata": {
                "wake": "wake177", "date": "2026-11-10",
                "description": "GRPO Curriculum Integration with R5 Process Reward",
                "integrates": ["R74", "R128", "R129"],
                "disclaimer": "Surrogate simulation, NOT transferable to BaiZe",
            },
            "phases": all_phase_results,
            "wall_clock_budget": budget,
            "total_wall_clock_hours": round(total_hours, 2),
            "replay_buffer": replay,
            "transition_criteria": transitions,
            "verl_config": verl_yaml,
            "summary": {
                "total_steps": total_steps,
                "total_groups_simulated": total_groups,
                "overall_learnable_rate": round(overall_learnable, 4),
                "overall_signal_rate": round(overall_signal, 4),
                "initial_pass_rates": INITIAL_PASS_RATES,
                "final_pass_rates": pass_rates,
            },
            "key_conclusions": [
                "5-phase curriculum (550 steps) covers L1->L5 progression",
                "R5 process reward enabled from Phase 1 (Foundation)",
                "Adaptive sampling (R74) from Phase 1 onwards",
                "Anti-forgetting replay: 0%->15%->20%->25%->30%",
                f"Wall-clock: ~{total_hours:.1f}h with 4 parallel sandboxes",
                "Transition: pass rate + advantage std + step count",
                "Safety: collapse/divergence/stagnation/cheat detection",
                "Full anti-gaming from Phase 3 (Refinement)",
                "3347 R128-verified tasks across 5 difficulty levels",
                "verl config with SGLang multi-turn + R5 reward",
            ],
        }
        with open(args.json, "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n  JSON report saved: {args.json} ({os.path.getsize(args.json)} bytes)")
    print("\nR130 complete.")


if __name__ == "__main__":
    main()
