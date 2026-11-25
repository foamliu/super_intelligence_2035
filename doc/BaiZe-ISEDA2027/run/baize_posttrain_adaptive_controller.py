#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
baize_posttrain_adaptive_controller.py
R81 (wake129): GPU-Day Adaptive Training Controller — Unified Decision Engine

Synthesizes R1-R80 into a single real-time decision controller for GPU-day
execution. Prior research produced individual components:
  - R74: curriculum scheduling (progressive difficulty)
  - R75/R76: anti-reward-hacking framework + monitor
  - R80: GRPO collapse detection (7 modes, 3-tier alerts)
  - R59/R73: GRPO dynamics + hyperparameter landscape
  - R79: SFT data mix optimization
  - R77: tokenizer EDA domain coverage

This script integrates them into a unified DecisionEngine that:
  1. Collects training metrics into a unified TrainingState
  2. Runs all detectors in parallel
  3. Produces a single ActionDecision (continue / pause / rollback / switch-arm / stop)
  4. Simulates a full GPU-day timeline with decision points
  5. Outputs HTML report + JSON results

Usage:
  python3 baize_posttrain_adaptive_controller.py                 # Full simulation
  python3 baize_posttrain_adaptive_controller.py --verbose       # With per-step output
  python3 baize_posttrain_adaptive_controller.py --html          # Generate HTML report
  python3 baize_posttrain_adaptive_controller.py --json          # Generate JSON output
  python3 baize_posttrain_adaptive_controller.py --decision-only # Just test decision logic

Zero dependencies. Python 3.8+ stdlib only.
"""
import argparse
import json
import math
import os
import random
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── R80 Collapse Detection Thresholds (calibrated from 700k-step MC) ───
COLLAPSE_THRESHOLDS = {
    "C1_cheat":        {"cheat_rate":    (0.02, 0.05, 0.10, "gt")},
    "C2_kl_explode":   {"kl_from_ref":   (1.0,  2.0,  5.0,  "gt")},
    "C3_adv_vanish":   {"reward_std":    (0.05, 0.02, 0.001, "lt")},
    "C4_entropy_collapse": {"policy_entropy": (0.5, 0.3, 0.1, "lt")},
    "C5_grad_explode": {"grad_norm":     (0.5,  1.0,  None, "gt")},
    "C6_reward_stall": {"avg_reward_delta_50": (0.001, 0.0005, 0.0, "lt")},
    "C7_length_hack":  {"avg_length_delta": (0.3, 0.5, 1.0, "gt")},
}

# ─── R75 Anti-Hack Detection Metrics ───
ANTIHACK_CHECKS = {
    "H1_api_fabrication":  {"metric": "fabricated_api_rate", "watch": 0.02, "warn": 0.05, "stop": 0.10},
    "H2_assertion_bypass":  {"metric": "bypass_assert_rate", "watch": 0.01, "warn": 0.03, "stop": 0.08},
    "H3_empty_solution":    {"metric": "empty_solution_rate", "watch": 0.05, "warn": 0.10, "stop": 0.20},
    "H4_format_gaming":     {"metric": "format_only_rate", "watch": 0.03, "warn": 0.08, "stop": 0.15},
    "H5_repetition":        {"metric": "repetition_rate", "watch": 0.10, "warn": 0.15, "stop": 0.25},
    "H6_output_degen":      {"metric": "filler_ratio", "watch": 0.15, "warn": 0.25, "stop": 0.40},
}

# ─── R74 Curriculum Phases ───
CURRICULUM_PHASES = [
    {"name": "warmup",    "steps": (0, 200),     "difficulty": "L1-L2", "task_ratio": [0.6, 0.3, 0.1, 0.0, 0.0]},
    {"name": "basic",     "steps": (200, 600),   "difficulty": "L2-L3", "task_ratio": [0.2, 0.4, 0.3, 0.1, 0.0]},
    {"name": "core",      "steps": (600, 1200),  "difficulty": "L3-L4", "task_ratio": [0.1, 0.2, 0.4, 0.2, 0.1]},
    {"name": "advanced",  "steps": (1200, 1800), "difficulty": "L4-L5", "task_ratio": [0.0, 0.1, 0.3, 0.4, 0.2]},
    {"name": "challenge", "steps": (1800, 2000), "difficulty": "L4-L5", "task_ratio": [0.0, 0.0, 0.2, 0.4, 0.4]},
]

# ─── R59/R73 Arm Configurations ───
ARM_CONFIGS = {
    "R0_baseline":       {"initial_reward": 0.40, "gain_per_200": 0.001, "cheat_risk": 0.00, "stability": "stable"},
    "R1_binary":         {"initial_reward": 0.46, "gain_per_200": 0.003, "cheat_risk": 0.02, "stability": "stable"},
    "R2_partial":        {"initial_reward": 0.53, "gain_per_200": -0.004, "cheat_risk": 0.01, "stability": "risky"},
    "R3_tool_penalty":   {"initial_reward": 0.50, "gain_per_200": 0.013, "cheat_risk": 0.00, "stability": "best"},
    "R4_api_legality":   {"initial_reward": 0.48, "gain_per_200": 0.011, "cheat_risk": 0.00, "stability": "good"},
}

# ─── R79 SFT Mix Optimal Config ───
SFT_OPTIMAL = {
    "mix": {"agentic": 0.29, "pyaether_api": 0.27, "pyaether_sft": 0.20, "code": 0.14, "general": 0.05, "math": 0.05},
    "budget_tokens": 2e9, "context_length": 16384,
    "projected_pass1": 0.637, "p_m1": 1.0, "p_m2": 0.0,
}


# ═══ Data Structures ═══

@dataclass
class TrainingState:
    """Unified training state — all metrics in one place."""
    step: int = 0
    phase: str = "warmup"
    arm: str = "R3_tool_penalty"
    avg_reward: float = 0.50
    reward_std: float = 0.15
    reward_delta_50: float = 0.005
    policy_entropy: float = 2.0
    kl_from_ref: float = 0.1
    grad_norm: float = 0.02
    avg_length: int = 20
    avg_length_delta: float = 0.0
    tool_call_count: int = 5
    cheat_rate: float = 0.0
    fabricated_api_rate: float = 0.0
    bypass_assert_rate: float = 0.0
    empty_solution_rate: float = 0.0
    format_only_rate: float = 0.0
    repetition_rate: float = 0.0
    filler_ratio: float = 0.0
    difficulty_level: str = "L1-L2"
    pass_rate: float = 0.36
    gpu_count: int = 4
    elapsed_seconds: float = 0.0


@dataclass
class Alert:
    detector: str
    mode: str
    metric: str
    value: float
    threshold: float
    level: str  # 'watch', 'warn', 'stop'
    message: str


@dataclass
class ActionDecision:
    action: str  # 'continue', 'pause', 'rollback', 'switch_arm', 'stop', 'advance_curriculum'
    reason: str
    alerts: List[Alert] = field(default_factory=list)
    params: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0


# ═══ Detectors ═══

class CollapseDetector:
    """R80: GRPO collapse mode detection with 3-tier alerts."""
    def check(self, state):
        alerts = []
        metric_map = {
            "cheat_rate": state.cheat_rate, "kl_from_ref": state.kl_from_ref,
            "reward_std": state.reward_std, "policy_entropy": state.policy_entropy,
            "grad_norm": state.grad_norm, "avg_reward_delta_50": state.reward_delta_50,
            "avg_length_delta": state.avg_length_delta,
        }
        for mode, thresholds in COLLAPSE_THRESHOLDS.items():
            for metric_name, (watch, warn, stop, direction) in thresholds.items():
                val = metric_map.get(metric_name)
                if val is None:
                    continue
                if stop is not None:
                    if direction == "gt" and val > stop:
                        alerts.append(Alert("Collapse", mode, metric_name, val, stop, "stop",
                            "STOP: %s %s=%.4f > %.4f" % (mode, metric_name, val, stop))); continue
                    if direction == "lt" and val < stop:
                        alerts.append(Alert("Collapse", mode, metric_name, val, stop, "stop",
                            "STOP: %s %s=%.4f < %.4f" % (mode, metric_name, val, stop))); continue
                if warn is not None:
                    if direction == "gt" and val > warn:
                        alerts.append(Alert("Collapse", mode, metric_name, val, warn, "warn",
                            "WARN: %s %s=%.4f > %.4f" % (mode, metric_name, val, warn))); continue
                    if direction == "lt" and val < warn:
                        alerts.append(Alert("Collapse", mode, metric_name, val, warn, "warn",
                            "WARN: %s %s=%.4f < %.4f" % (mode, metric_name, val, warn))); continue
                if watch is not None:
                    if direction == "gt" and val > watch:
                        alerts.append(Alert("Collapse", mode, metric_name, val, watch, "watch",
                            "WATCH: %s %s=%.4f > %.4f" % (mode, metric_name, val, watch)))
                    if direction == "lt" and val < watch:
                        alerts.append(Alert("Collapse", mode, metric_name, val, watch, "watch",
                            "WATCH: %s %s=%.4f < %.4f" % (mode, metric_name, val, watch)))
        return alerts


class AntiHackMonitor:
    """R75/R76: Anti-reward-hacking detection."""
    def check(self, state):
        alerts = []
        metric_map = {
            "fabricated_api_rate": state.fabricated_api_rate,
            "bypass_assert_rate": state.bypass_assert_rate,
            "empty_solution_rate": state.empty_solution_rate,
            "format_only_rate": state.format_only_rate,
            "repetition_rate": state.repetition_rate,
            "filler_ratio": state.filler_ratio,
        }
        for hack_id, cfg in ANTIHACK_CHECKS.items():
            val = metric_map.get(cfg["metric"], 0.0)
            if val > cfg["stop"]:
                alerts.append(Alert("AntiHack", hack_id, cfg["metric"], val, cfg["stop"], "stop",
                    "STOP: %s %.4f > %.4f" % (hack_id, val, cfg["stop"])))
            elif val > cfg["warn"]:
                alerts.append(Alert("AntiHack", hack_id, cfg["metric"], val, cfg["warn"], "warn",
                    "WARN: %s %.4f > %.4f" % (hack_id, val, cfg["warn"])))
            elif val > cfg["watch"]:
                alerts.append(Alert("AntiHack", hack_id, cfg["metric"], val, cfg["watch"], "watch",
                    "WATCH: %s %.4f > %.4f" % (hack_id, val, cfg["watch"])))
        return alerts


class CurriculumScheduler:
    """R74: Progressive difficulty curriculum."""
    def get_phase(self, step):
        for phase in CURRICULUM_PHASES:
            lo, hi = phase["steps"]
            if lo <= step < hi:
                return phase
        return CURRICULUM_PHASES[-1]

    def should_advance(self, state):
        phase = self.get_phase(state.step)
        thresholds = {"warmup": 0.70, "basic": 0.60, "core": 0.50, "advanced": 0.40, "challenge": 0.30}
        return state.pass_rate > thresholds.get(phase["name"], 0.50)


class ArmSwitcher:
    """R59/R73: Reward arm switching logic."""
    def should_switch(self, state, current_arm):
        if state.reward_std < 0.05 and state.step > 100 and current_arm != "R1_binary":
            return True, "R1_binary", "reward_std<0.05 (advantage vanishing) -> R1 binary"
        if state.avg_length_delta > 0.5 and state.step > 50 and current_arm != "R1_binary":
            return True, "R1_binary", "length exploitation -> R1 binary (no length incentive)"
        if state.cheat_rate > 0.05 and state.step > 100 and current_arm != "R4_api_legality":
            return True, "R4_api_legality", "cheat_rate>5%% -> R4 (API legality)"
        if current_arm == "R2_partial" and state.reward_delta_50 < 0 and state.step > 200:
            return True, "R3_tool_penalty", "R2 negative gain -> R3 (best stability)"
        return False, current_arm, "no switch needed"


# ═══ Decision Engine ═══

class DecisionEngine:
    """Unified decision engine combining all detectors."""
    def __init__(self):
        self.collapse = CollapseDetector()
        self.antihack = AntiHackMonitor()
        self.curriculum = CurriculumScheduler()
        self.arm_switcher = ArmSwitcher()

    def decide(self, state):
        all_alerts = []
        all_alerts.extend(self.collapse.check(state))
        all_alerts.extend(self.antihack.check(state))

        # P1: STOP
        stop_alerts = [a for a in all_alerts if a.level == "stop"]
        if stop_alerts:
            return ActionDecision("stop", "STOP: %s" % stop_alerts[0].message, all_alerts, confidence=0.99)

        # P2: ROLLBACK (KL or grad explosion at warn)
        rollback_modes = {"C2_kl_explode", "C5_grad_explode"}
        warn_collapse = [a for a in all_alerts if a.level == "warn" and a.mode in rollback_modes]
        if warn_collapse:
            return ActionDecision("rollback", "Severe instability: %s -> rollback" % warn_collapse[0].message,
                                  all_alerts, {"target_checkpoint": "last_stable"}, 0.90)

        # P3: SWITCH ARM
        should_switch, new_arm, switch_reason = self.arm_switcher.should_switch(state, state.arm)
        if should_switch:
            return ActionDecision("switch_arm", switch_reason, all_alerts, {"new_arm": new_arm}, 0.85)

        # P4: ADVANCE CURRICULUM
        if self.curriculum.should_advance(state):
            phase = self.curriculum.get_phase(state.step)
            next_idx = min(CURRICULUM_PHASES.index(phase) + 1, len(CURRICULUM_PHASES) - 1)
            next_phase = CURRICULUM_PHASES[next_idx]
            return ActionDecision("advance_curriculum",
                "pass_rate=%.1f%% exceeds %s threshold -> %s" % (state.pass_rate * 100, phase["name"], next_phase["name"]),
                all_alerts, {"new_phase": next_phase["name"]}, 0.80)

        # P5: PAUSE (3+ warns)
        warn_alerts = [a for a in all_alerts if a.level == "warn"]
        if len(warn_alerts) >= 3:
            return ActionDecision("pause", "Multiple warnings (%d) -> pause" % len(warn_alerts), all_alerts, confidence=0.75)

        # Default: CONTINUE
        watch_count = len([a for a in all_alerts if a.level == "watch"])
        return ActionDecision("continue", "All checks passed (%d watch)" % watch_count, all_alerts, confidence=0.95)


# ═══ GPU-Day Simulator ═══

class GPUDaySimulator:
    """Simulates a full GPU-day execution with decision points."""
    def __init__(self, seed=42):
        self.rng = random.Random(seed)
        self.engine = DecisionEngine()
        self.results = []

    def _simulate_step(self, step, arm, phase_name, base_pass):
        arm_cfg = ARM_CONFIGS.get(arm, ARM_CONFIGS["R3_tool_penalty"])
        gain = arm_cfg["gain_per_200"] * (step / 200.0)
        noise = self.rng.gauss(0, 0.01)
        avg_reward = max(0.0, min(1.0, arm_cfg["initial_reward"] + gain + noise))
        reward_std = max(0.01, 0.15 * math.exp(-step / 800.0) + self.rng.gauss(0, 0.005))
        policy_entropy = max(0.1, 2.0 * math.exp(-step / 1500.0) + self.rng.gauss(0, 0.05))
        kl_from_ref = 0.05 + 0.003 * step / 100.0 + abs(self.rng.gauss(0, 0.01))
        grad_norm = max(0.001, 0.02 + abs(self.rng.gauss(0, 0.005)))
        avg_length = int(20 + step * 0.005 + self.rng.gauss(0, 2))
        avg_length_delta = 0.001 * step / 100.0 + self.rng.gauss(0, 0.05)
        pass_rate = min(0.85, base_pass + gain * 0.5 + self.rng.gauss(0, 0.02))
        cheat_rate = arm_cfg["cheat_risk"] * (1 + step / 2000.0) + abs(self.rng.gauss(0, 0.002))
        fab_rate = max(0.0, self.rng.gauss(0.005, 0.003) + cheat_rate * 0.3)
        bypass_rate = max(0.0, self.rng.gauss(0.003, 0.002))
        empty_rate = max(0.0, self.rng.gauss(0.02, 0.01))
        format_rate = max(0.0, self.rng.gauss(0.01, 0.005))
        rep_rate = max(0.0, self.rng.gauss(0.05, 0.02) + step / 5000.0)
        filler = max(0.0, self.rng.gauss(0.08, 0.03) + step / 8000.0)
        reward_delta = gain / 200.0 if step > 50 else 0.005
        return TrainingState(
            step=step, phase=phase_name, arm=arm,
            avg_reward=avg_reward, reward_std=reward_std, reward_delta_50=reward_delta,
            policy_entropy=policy_entropy, kl_from_ref=kl_from_ref, grad_norm=grad_norm,
            avg_length=avg_length, avg_length_delta=avg_length_delta,
            tool_call_count=int(5 + step / 200.0), cheat_rate=cheat_rate,
            fabricated_api_rate=fab_rate, bypass_assert_rate=bypass_rate,
            empty_solution_rate=empty_rate, format_only_rate=format_rate,
            repetition_rate=rep_rate, filler_ratio=filler, pass_rate=pass_rate,
            elapsed_seconds=step * 90.0)

    def simulate_gpu_day(self, max_steps=2000, base_pass=0.36, verbose=False):
        current_arm = "R3_tool_penalty"
        decisions_log = []
        check_points = set()
        for s in range(0, min(500, max_steps + 1), 50):
            check_points.add(s)
        for s in range(500, max_steps + 1, 100):
            check_points.add(s)
        check_points.add(0)
        check_points.add(max_steps)
        for step in sorted(check_points):
            phase = self.engine.curriculum.get_phase(step)
            state = self._simulate_step(step, current_arm, phase["name"], base_pass)
            state.arm = current_arm
            decision = self.engine.decide(state)
            al = {"watch": 0, "warn": 0, "stop": 0}
            for a in decision.alerts:
                al[a.level] = al.get(a.level, 0) + 1
            decisions_log.append({
                "step": step, "phase": phase["name"], "arm": current_arm,
                "avg_reward": round(state.avg_reward, 4), "reward_std": round(state.reward_std, 4),
                "policy_entropy": round(state.policy_entropy, 4), "kl_from_ref": round(state.kl_from_ref, 4),
                "pass_rate": round(state.pass_rate, 4), "cheat_rate": round(state.cheat_rate, 4),
                "avg_length": state.avg_length, "action": decision.action, "reason": decision.reason,
                "n_alerts": len(decision.alerts), "alert_levels": al})
            if decision.action == "switch_arm":
                current_arm = decision.params.get("new_arm", current_arm)
            if decision.action == "stop":
                if verbose:
                    print("[step %d] STOP: %s" % (step, decision.reason))
                break
            if verbose and step % 200 == 0:
                print("[step %d] %s arm=%s reward=%.3f pass=%.1f%% action=%s" % (
                    step, phase["name"], current_arm, state.avg_reward, state.pass_rate * 100, decision.action))
        self.results = decisions_log
        return decisions_log

    def summarize(self):
        if not self.results:
            return {}
        actions = {}
        for r in self.results:
            actions[r["action"]] = actions.get(r["action"], 0) + 1
        final = self.results[-1] if self.results else {}
        milestones = {}
        for target, label in [(0.50, "M1"), (0.65, "M2"), (0.75, "M3"), (0.85, "M4")]:
            reached = None
            for r in self.results:
                if r["pass_rate"] >= target:
                    reached = r["step"]
                    break
            milestones[label] = {"target": target, "reached_step": reached}
        arms_used = list(set(r["arm"] for r in self.results))
        return {
            "total_checkpoints": len(self.results), "action_distribution": actions,
            "final_pass_rate": final.get("pass_rate", 0), "final_step": final.get("step", 0),
            "final_arm": final.get("arm", ""), "milestones": milestones, "arms_used": arms_used,
            "total_stops": actions.get("stop", 0), "total_rollbacks": actions.get("rollback", 0),
            "total_switches": actions.get("switch_arm", 0), "total_curriculum_advances": actions.get("advance_curriculum", 0)}


# ═══ GPU-Day Step Plan ═══

GPU_DAY_STEPS = [
    {"step": 0, "name": "NFS Warm-up", "duration_min": 10,
     "action": "Pre-cache model files, venv packages, data on NFS",
     "go": ["model_dir exists", "venv python works", "torch.cuda.is_available()=True"],
     "script": "baize_posttrain_gpu_watcher.sh --warmup-only", "risk": "R1 NFS cold start", "source": "R45/R62"},
    {"step": 1, "name": "SGLang Serve MiniCPM5-2B", "duration_min": 5,
     "action": "Launch SGLang server with tensor parallel on 4xA40",
     "go": ["server responds /v1/models", "throughput >10 req/s"],
     "script": "baize_posttrain_launch_11_9.sh --step 1", "risk": "R2 SGLang occupies GPUs", "source": "R67/R69"},
    {"step": 2, "name": "Baseline 36% Reproduction (5-run)", "duration_min": 900,
     "action": "Run EDA-Eval-PyAether 158 tasks x 5 runs",
     "go": ["5-run mean in [30%%, 42%%]", "std < 5pp", "no contamination"],
     "script": "baize_posttrain_eval.sh --runs 5", "risk": "Protocol mismatch", "source": "R55"},
    {"step": 3, "name": "D1-D6 Extraction + Failure Trajectory", "duration_min": 15,
     "action": "Extract D1-D6 from baseline traces, classify failure modes",
     "go": ["D1-D6 all computed", "failure taxonomy populated"],
     "script": "baize_posttrain_baseline_d1d6_analyzer.py", "risk": "Field missing", "source": "R55/R4"},
    {"step": 4, "name": "Contamination Gate", "duration_min": 2,
     "action": "Verify no overlap between training data and eval set",
     "go": ["0 n-gram hits", "0 MinHash hits"],
     "script": "baize_posttrain_contamination_gate.sh", "risk": "False positive", "source": "R2/E1"},
    {"step": 5, "name": "RL Smoke Test (10 iters)", "duration_min": 30,
     "action": "Run 10 GRPO iterations with R3 arm on 4xA40",
     "go": ["reward > 0", "no crash", "cheat_rate < 5%%", "entropy > 0.5"],
     "script": "baize_posttrain_rl_grpo.sh --reward-arm R3 --max-iters 10", "risk": "R6 reward zero/R7 OOM", "source": "R59/R73/R80"},
    {"step": 6, "name": "Full RL Training (2000 iters)", "duration_min": 18000,
     "action": "Full GRPO training with adaptive controller monitoring",
     "go": ["pass_rate trending up", "no stop-level alerts", "M1 (50%%) reached"],
     "script": "baize_posttrain_rl_grpo.sh --reward-arm R3 --max-iters 2000", "risk": "All R80 collapse modes", "source": "R74/R80/R81"},
]


# ═══ HTML Report Generation ═══

def generate_html(sim_results, summary, output_path):
    h = []
    h.append("<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'>")
    h.append("<meta name='viewport' content='width=device-width,initial-scale=1.0'>")
    h.append("<title>R81 GPU-Day Adaptive Training Controller</title><style>")
    h.append("body{font-family:system-ui,sans-serif;max-width:1200px;margin:0 auto;padding:20px;background:#f8f9fa;color:#212529}")
    h.append("h1{color:#1a237e;border-bottom:3px solid #1a237e;padding-bottom:10px}")
    h.append("h2{color:#283593;margin-top:30px;border-left:4px solid #5c6bc0;padding-left:10px}")
    h.append("table{border-collapse:collapse;width:100%;margin:10px 0;background:white}")
    h.append("th,td{border:1px solid #dee2e6;padding:8px 12px;text-align:left}")
    h.append("th{background:#e8eaf6;font-weight:600}")
    h.append(".continue{color:#2e7d32;font-weight:bold}.pause{color:#f57f17;font-weight:bold}")
    h.append(".rollback{color:#e65100;font-weight:bold}.switch_arm{color:#6a1b9a;font-weight:bold}")
    h.append(".stop{color:#c62828;font-weight:bold}.advance_curriculum{color:#0277bd;font-weight:bold}")
    h.append(".summary-box{background:white;border-radius:8px;padding:15px;margin:10px 0;box-shadow:0 2px 4px rgba(0,0,0,0.1)}")
    h.append(".metric{display:inline-block;margin:5px 10px;padding:5px 10px;background:#e3f2fd;border-radius:4px}")
    h.append("code{background:#f5f5f5;padding:2px 6px;border-radius:3px;font-family:monospace}")
    h.append(".note{background:#fff3e0;border-left:4px solid #ff9800;padding:10px;margin:10px 0}")
    h.append("</style></head><body>")
    h.append("<h1>R81: GPU-Day Adaptive Training Controller</h1>")
    h.append("<p><b>wake129</b> | 2026-11-09 | Synthesizes R1-R80 into real-time decision engine</p>")
    h.append("<p><b>WARNING</b>: Surrogate model (MiniCPM5-2B) results NOT transferable to BaiZe.</p>")
    h.append("<h2>1. Architecture</h2>")
    h.append("<table><tr><th>Component</th><th>Source</th><th>Role</th></tr>")
    h.append("<tr><td>CollapseDetector</td><td>R80</td><td>7 modes, 3-tier alerts, entropy&lt;0.1=stop</td></tr>")
    h.append("<tr><td>AntiHackMonitor</td><td>R75/R76</td><td>6 hack patterns, cheat&gt;10%=stop</td></tr>")
    h.append("<tr><td>CurriculumScheduler</td><td>R74</td><td>5-phase difficulty progression</td></tr>")
    h.append("<tr><td>ArmSwitcher</td><td>R59/R73</td><td>5 arms, auto-switch on instability</td></tr>")
    h.append("<tr><td>DecisionEngine</td><td>R81</td><td>Priority: stop&gt;rollback&gt;switch&gt;advance&gt;pause&gt;continue</td></tr>")
    h.append("</table>")
    h.append("<h2>2. Decision Priority</h2>")
    h.append("<table><tr><th>#</th><th>Action</th><th>Trigger</th><th>Conf</th></tr>")
    h.append("<tr><td>1</td><td class='stop'>STOP</td><td>Stop-level alert</td><td>0.99</td></tr>")
    h.append("<tr><td>2</td><td class='rollback'>ROLLBACK</td><td>KL/grad explosion warn</td><td>0.90</td></tr>")
    h.append("<tr><td>3</td><td class='switch_arm'>SWITCH ARM</td><td>Advantage vanish/cheat</td><td>0.85</td></tr>")
    h.append("<tr><td>4</td><td class='advance_curriculum'>ADVANCE</td><td>Pass rate threshold</td><td>0.80</td></tr>")
    h.append("<tr><td>5</td><td class='pause'>PAUSE</td><td>3+ warnings</td><td>0.75</td></tr>")
    h.append("<tr><td>6</td><td class='continue'>CONTINUE</td><td>All passed</td><td>0.95</td></tr>")
    h.append("</table>")
    h.append("<h2>3. GPU-Day Execution Plan</h2>")
    h.append("<table><tr><th>Step</th><th>Name</th><th>Min</th><th>Go Criteria</th><th>Script</th></tr>")
    for s in GPU_DAY_STEPS:
        h.append("<tr><td>%d</td><td>%s</td><td>%d</td><td>%s</td><td><code>%s</code></td></tr>" % (
            s["step"], s["name"], s["duration_min"], "<br>".join(s["go"]), s["script"]))
    h.append("</table>")
    total_min = sum(s["duration_min"] for s in GPU_DAY_STEPS)
    h.append("<p><b>Total</b>: %d min (%.1f h / %.1f days)</p>" % (total_min, total_min / 60.0, total_min / 1440.0))
    h.append("<h2>4. Simulation Results</h2><div class='summary-box'>")
    h.append("<p><span class='metric'>Checkpoints: %d</span>" % summary.get("total_checkpoints", 0))
    h.append("<span class='metric'>Final Pass@1: %.1f%%</span>" % (summary.get("final_pass_rate", 0) * 100))
    h.append("<span class='metric'>Arms: %s</span></p>" % ", ".join(summary.get("arms_used", [])))
    h.append("<table><tr><th>Action</th><th>Count</th></tr>")
    for a, c in sorted(summary.get("action_distribution", {}).items()):
        h.append("<tr><td class='%s'>%s</td><td>%d</td></tr>" % (a, a, c))
    h.append("</table>")
    h.append("<table><tr><th>Milestone</th><th>Target</th><th>Step</th><th>Status</th></tr>")
    for label, info in summary.get("milestones", {}).items():
        st = "REACHED" if info["reached_step"] is not None else "NOT REACHED"
        ss = str(info["reached_step"]) if info["reached_step"] is not None else "-"
        h.append("<tr><td>%s</td><td>%.0f%%</td><td>%s</td><td>%s</td></tr>" % (label, info["target"] * 100, ss, st))
    h.append("</table></div>")
    h.append("<h2>5. Decision Log (sampled)</h2>")
    h.append("<table><tr><th>Step</th><th>Phase</th><th>Arm</th><th>Reward</th><th>Pass@1</th><th>Entropy</th><th>KL</th><th>Action</th></tr>")
    sample = sim_results[:30] + sim_results[-10:] if len(sim_results) > 40 else sim_results
    for r in sample:
        h.append("<tr><td>%d</td><td>%s</td><td>%s</td><td>%.3f</td><td>%.1f%%</td><td>%.3f</td><td>%.3f</td><td class='%s'>%s</td></tr>" % (
            r["step"], r["phase"], r["arm"], r["avg_reward"], r["pass_rate"] * 100,
            r["policy_entropy"], r["kl_from_ref"], r["action"], r["action"]))
    h.append("</table>")
    h.append("<h2>6. Integration Map (R1-R80 -&gt; R81)</h2>")
    h.append("<table><tr><th>Research</th><th>Component</th><th>How Used</th></tr>")
    h.append("<tr><td>R74</td><td>CurriculumScheduler</td><td>5-phase difficulty, pass-rate thresholds</td></tr>")
    h.append("<tr><td>R75/R76</td><td>AntiHackMonitor</td><td>6 hack metrics, 3-tier thresholds</td></tr>")
    h.append("<tr><td>R80</td><td>CollapseDetector</td><td>7 modes, 700k MC calibrated thresholds</td></tr>")
    h.append("<tr><td>R59/R73</td><td>ArmSwitcher</td><td>5 arms, auto-switch on instability</td></tr>")
    h.append("<tr><td>R79</td><td>SFT mix</td><td>Optimal mix feeds initial ckpt quality</td></tr>")
    h.append("<tr><td>R77</td><td>Tokenizer</td><td>Domain annealing necessity (5.2x)</td></tr>")
    h.append("</table>")
    h.append("<h2>7. Limitations</h2><div class='note'><ul>")
    h.append("<li>Simulation uses simplified dynamics; real GRPO may differ</li>")
    h.append("<li>Thresholds for MiniCPM5-2B; BaiZe needs recalibration</li>")
    h.append("<li>Surrogate results NOT transferable to BaiZe</li>")
    h.append("<li>Real-time metric pipeline not yet tested E2E</li>")
    h.append("<li>No fabrication: all thresholds from prior R-sections</li>")
    h.append("</ul></div></body></html>")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(h))
    return os.path.getsize(output_path)


# ═══ Main ═══

def main():
    parser = argparse.ArgumentParser(description="R81: GPU-Day Adaptive Training Controller")
    parser.add_argument("--verbose", action="store_true", help="Print per-step output")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    parser.add_argument("--json", action="store_true", help="Generate JSON output")
    parser.add_argument("--decision-only", action="store_true", help="Test decision logic only")
    parser.add_argument("--max-steps", type=int, default=2000, help="Max RL steps")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    if args.decision_only:
        engine = DecisionEngine()
        test_cases = [
            ("normal", TrainingState(step=100, avg_reward=0.55, reward_std=0.12, policy_entropy=1.8, kl_from_ref=0.15, cheat_rate=0.01)),
            ("cheat_high", TrainingState(step=150, cheat_rate=0.08, avg_reward=0.70, policy_entropy=1.5)),
            ("entropy_collapse", TrainingState(step=300, policy_entropy=0.08, reward_std=0.15, kl_from_ref=0.3)),
            ("kl_explode", TrainingState(step=200, kl_from_ref=3.0, policy_entropy=1.0, reward_std=0.1)),
            ("adv_vanish", TrainingState(step=250, reward_std=0.01, policy_entropy=1.2, kl_from_ref=0.2)),
            ("length_hack", TrainingState(step=100, avg_length_delta=0.8, policy_entropy=1.5, reward_std=0.1)),
            ("multi_warn", TrainingState(step=200, policy_entropy=0.4, cheat_rate=0.03, reward_std=0.03, kl_from_ref=1.5)),
            ("ready_advance", TrainingState(step=250, pass_rate=0.72, policy_entropy=1.8, reward_std=0.15, kl_from_ref=0.2, cheat_rate=0.01)),
        ]
        print("=== Decision Logic Test ===")
        for name, state in test_cases:
            d = engine.decide(state)
            print("%-15s -> action=%-20s reason=%s" % (name, d.action, d.reason[:80]))
        return 0

    sim = GPUDaySimulator(seed=args.seed)
    results = sim.simulate_gpu_day(max_steps=args.max_steps, base_pass=0.36, verbose=args.verbose)
    summary = sim.summarize()

    print("=== R81 GPU-Day Adaptive Controller ===")
    print("Checkpoints: %d" % summary.get("total_checkpoints", 0))
    print("Final Pass@1: %.1f%%" % (summary.get("final_pass_rate", 0) * 100))
    print("Action distribution:")
    for a, c in sorted(summary.get("action_distribution", {}).items()):
        print("  %-20s: %d" % (a, c))
    print("Milestones:")
    for label, info in summary.get("milestones", {}).items():
        status = "REACHED @ step %d" % info["reached_step"] if info["reached_step"] is not None else "NOT REACHED"
        print("  %s (%.0f%%): %s" % (label, info["target"] * 100, status))

    if args.json:
        json_path = os.path.join(SCRIPT_DIR, "r81_adaptive_controller.json")
        output = {"summary": summary, "decisions": results, "gpu_day_steps": GPU_DAY_STEPS,
                  "thresholds": {"collapse": COLLAPSE_THRESHOLDS, "antihack": ANTIHACK_CHECKS},
                  "curriculum_phases": CURRICULUM_PHASES, "arm_configs": ARM_CONFIGS}
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print("JSON: %s (%d bytes)" % (json_path, os.path.getsize(json_path)))

    if args.html:
        reports_dir = os.path.join(os.path.dirname(SCRIPT_DIR), "reports")
        html_path = os.path.join(reports_dir, "report_posttrain_r81_adaptive_controller_zh.html")
        size = generate_html(results, summary, html_path)
        print("HTML: %s (%d bytes)" % (html_path, size))

    return 0

if __name__ == "__main__":
    sys.exit(main())

