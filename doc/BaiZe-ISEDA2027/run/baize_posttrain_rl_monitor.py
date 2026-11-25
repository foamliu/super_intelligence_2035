#!/usr/bin/env python3
"""baize_posttrain_rl_monitor.py — RL Training Observability & Failure Recovery

R36 (2026-11-08): GRPO training can silently diverge — KL explosion, reward
collapse, entropy collapse, gradient explosion — wasting hours of GPU time.
This script provides:
1. Metric parsing from verl stdout logs.
2. Divergence detection: 7 failure patterns with configurable thresholds.
3. Early stopping: writes STOP signal file after N consecutive critical alerts.
4. Checkpoint advisory: recommends which checkpoint to keep/discard.
5. Recovery procedures: prints actionable commands for each failure mode.

Usage:
    python baize_posttrain_rl_monitor.py --log-dir <path> --save-dir <path>
    python baize_posttrain_rl_monitor.py --log-dir <path> --oneshot
    python baize_posttrain_rl_monitor.py --save-dir <path> --clear-stop

WARNING: Surrogate RL results (MiniCPM5-2B) are NOT transferable to BaiZe.
"""
from __future__ import annotations

import argparse
import json
import logging
import math
import os
import re
import signal
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("rl_monitor")

# ─── Divergence thresholds (R36: calibrated from GRPO literature) ──────────
# Refs: DeepSeek-R1 (arXiv:2501.12948), GRPO (arXiv:2402.03300), sGPO (2606.08854)

THRESHOLDS = {
    "kl_max": 10.0,           # KL > 10 = catastrophic drift from reference
    "reward_floor": 0.01,     # Mean reward ~0 = all rollouts fail, no signal
    "std_floor": 0.01,        # Reward std ~0 = all same, no GRPO advantage
    "entropy_floor": 0.1,     # Entropy < 0.1 = mode collapse
    "grad_max": 100.0,        # Grad norm > 100 = explosion
    "cheat_max": 0.05,        # Cheat rate > 5% = reward hacking (red-line §5.2)
    "alert_consecutive": 3,   # Steps before WARNING fires
    "stop_consecutive": 5,    # Steps before CRITICAL STOP fires
}

RECOVERY_PROCEDURES = {
    "P1_kl_explosion": (
        "KL Divergence Explosion (kl_loss > {kl_max}). "
        "Recovery: increase kl_loss_coef 0.02->0.04, decrease lr 3e-6->1e-6, "
        "decrease ppo_epochs 2->1. If persists: resume from last good checkpoint."
    ),
    "P2_reward_collapse": (
        "Reward Collapse (rewards_mean < {reward_floor}). "
        "Recovery: check sandbox running, switch to R0 skeleton mode, "
        "mix easier L1/L2 tasks, verify reward function not returning 0."
    ),
    "P3_std_collapse": (
        "Reward Std Collapse (rewards_std < {std_floor}). "
        "Recovery: increase group_size 8->16, switch R1->R2, "
        "check filter_groups rate, verify task difficulty distribution."
    ),
    "P4_entropy_collapse": (
        "Policy Entropy Collapse (entropy < {entropy_floor}). "
        "Recovery: increase entropy_coeff 0.001->0.01, increase temperature, "
        "decrease ppo_epochs 2->1."
    ),
    "P5_grad_explosion": (
        "Gradient Explosion (grad_norm > {grad_max}). "
        "Recovery: decrease lr 3e-6->1e-6, decrease grad_clip 1.0->0.5. "
        "If NaN: stop immediately, resume from last good checkpoint."
    ),
    "P6_nan_inf": (
        "NaN/Inf Detected. STOP IMMEDIATELY. "
        "Recovery: resume from last good checkpoint, check fp16 overflow, "
        "empty batch (div by 0), reward function NaN. Add NaN guard."
    ),
    "P7_cheat_spike": (
        "Cheat Rate Spike (cheat_rate > {cheat_max}). Red-line violation. "
        "Recovery: tighten anti-cheat ngram 8->5, switch to R4 arm, "
        "add format constraints, document cheat rate for paper."
    ),
}


@dataclass
class MetricSnapshot:
    """Single training step's metrics."""
    step: int = 0
    timestamp: str = ""
    lm_loss: float = float("nan")
    entropy: float = float("nan")
    grad_norm: float = float("nan")
    clip_ratio: float = float("nan")
    rewards_mean: float = float("nan")
    rewards_std: float = float("nan")
    kl_loss: float = float("nan")
    advantages_mean: float = float("nan")
    advantages_std: float = float("nan")
    step_time: float = float("nan")
    cheat_rate: float = float("nan")

    def has_nan(self) -> bool:
        for v in [self.lm_loss, self.entropy, self.grad_norm, self.clip_ratio,
                  self.rewards_mean, self.rewards_std, self.kl_loss,
                  self.advantages_mean, self.advantages_std]:
            if not math.isfinite(v):
                return True
        return False


@dataclass
class AlertState:
    """Track consecutive alerts for each divergence pattern."""
    counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    fired: Dict[str, bool] = field(default_factory=lambda: defaultdict(bool))
    stop_triggered: bool = False
    alerts_log: List[Dict[str, Any]] = field(default_factory=list)

    def update(self, pattern: str, triggered: bool, step: int,
               value: float, threshold: float) -> Optional[Dict]:
        if triggered:
            self.counts[pattern] += 1
        else:
            self.counts[pattern] = 0
            self.fired[pattern] = False
        n = self.counts[pattern]
        alert = None
        if n >= THRESHOLDS["alert_consecutive"] and not self.fired[pattern]:
            self.fired[pattern] = True
            severity = "WARNING" if n < THRESHOLDS["stop_consecutive"] else "CRITICAL"
            alert = {"type": pattern, "step": step, "value": value,
                     "threshold": threshold, "consecutive": n,
                     "severity": severity, "timestamp": datetime.now().isoformat()}
            self.alerts_log.append(alert)
            if n >= THRESHOLDS["stop_consecutive"] and pattern != "P7_cheat_spike":
                self.stop_triggered = True
        return alert


# ─── Log parsing ────────────────────────────────────────────────────────────

_METRIC_PATTERNS = {
    "step": re.compile(r"step[:\s]+(\d+)"),
    "lm_loss": re.compile(r"(?:actor/)?lm_loss[:\s]+([\d.eE+-]+)"),
    "entropy": re.compile(r"(?:actor/)?entropy[:\s]+([\d.eE+-]+)"),
    "grad_norm": re.compile(r"(?:actor/)?grad_norm[:\s]+([\d.eE+-]+)"),
    "clip_ratio": re.compile(r"(?:actor/)?clip_ratio[:\s]+([\d.eE+-]+)"),
    "rewards_mean": re.compile(r"(?:critic/)?rewards?_?mean[:\s]+([\d.eE+-]+)"),
    "rewards_std": re.compile(r"(?:critic/)?rewards?_?std[:\s]+([\d.eE+-]+)"),
    "kl_loss": re.compile(r"(?:actor/)?kl_loss[:\s]+([\d.eE+-]+)"),
    "advantages_mean": re.compile(r"(?:actor/)?advantages?_?mean[:\s]+([\d.eE+-]+)"),
    "advantages_std": re.compile(r"(?:actor/)?advantages?_?std[:\s]+([\d.eE+-]+)"),
    "step_time": re.compile(r"(?:timing/)?(?:total_)?step_time[:\s]+([\d.eE+-]+)"),
    "cheat_rate": re.compile(r"cheat_rate[:\s]+([\d.eE+-]+)"),
}


def parse_log_line(line: str) -> Optional[MetricSnapshot]:
    """Parse a single verl log line into a MetricSnapshot."""
    snap = MetricSnapshot(timestamp=datetime.now().isoformat())
    m = _METRIC_PATTERNS["step"].search(line)
    if not m:
        return None
    snap.step = int(m.group(1))
    for name, pattern in _METRIC_PATTERNS.items():
        if name == "step":
            continue
        m = pattern.search(line)
        if m:
            try:
                setattr(snap, name, float(m.group(1)))
            except (ValueError, AttributeError):
                pass
    return snap


def parse_log_file(log_path: str, last_step: int = 0) -> List[MetricSnapshot]:
    """Parse a verl log file, returning snapshots for steps > last_step."""
    snapshots = []
    try:
        with open(log_path, "r", errors="replace") as f:
            for line in f:
                snap = parse_log_line(line)
                if snap and snap.step > last_step:
                    snapshots.append(snap)
    except (IOError, OSError) as e:
        logger.warning("Cannot read log file %s: %s", log_path, e)
    return snapshots


def find_latest_log(log_dir: str) -> Optional[str]:
    """Find the most recently modified .log or .out file in log_dir."""
    log_path = Path(log_dir)
    if not log_path.is_dir():
        return None
    candidates = sorted(
        list(log_path.glob("*.log")) + list(log_path.glob("*.out")),
        key=lambda p: p.stat().st_mtime if p.exists() else 0,
        reverse=True,
    )
    return str(candidates[0]) if candidates else None


# ─── Divergence detection ──────────────────────────────────────────────────

def check_divergence(snap: MetricSnapshot, state: AlertState) -> List[Dict]:
    """Check a metric snapshot against all 7 divergence patterns."""
    alerts = []
    checks = [
        ("P1_kl_explosion", math.isfinite(snap.kl_loss),
         snap.kl_loss > THRESHOLDS["kl_max"], snap.kl_loss, THRESHOLDS["kl_max"]),
        ("P2_reward_collapse", math.isfinite(snap.rewards_mean),
         snap.rewards_mean < THRESHOLDS["reward_floor"], snap.rewards_mean, THRESHOLDS["reward_floor"]),
        ("P3_std_collapse", math.isfinite(snap.rewards_std),
         snap.rewards_std < THRESHOLDS["std_floor"], snap.rewards_std, THRESHOLDS["std_floor"]),
        ("P4_entropy_collapse", math.isfinite(snap.entropy),
         snap.entropy < THRESHOLDS["entropy_floor"], snap.entropy, THRESHOLDS["entropy_floor"]),
        ("P5_grad_explosion", math.isfinite(snap.grad_norm),
         snap.grad_norm > THRESHOLDS["grad_max"], snap.grad_norm, THRESHOLDS["grad_max"]),
        ("P7_cheat_spike", math.isfinite(snap.cheat_rate) and snap.cheat_rate >= 0,
         snap.cheat_rate > THRESHOLDS["cheat_max"], snap.cheat_rate, THRESHOLDS["cheat_max"]),
    ]
    for pattern, has_data, triggered, value, threshold in checks:
        if has_data:
            a = state.update(pattern, triggered, snap.step, value, threshold)
            if a:
                alerts.append(a)
    # P6: NaN/Inf — always check
    if snap.has_nan():
        a = state.update("P6_nan_inf", True, snap.step, float("nan"), 0.0)
        if a:
            alerts.append(a)
    return alerts


# ─── Checkpoint advisory ───────────────────────────────────────────────────

def checkpoint_advisory(snapshots: List[MetricSnapshot], save_dir: str) -> Dict:
    """Analyze checkpoint quality based on metric trajectory."""
    if not snapshots:
        return {"error": "no snapshots"}
    best_step, best_reward = 0, -1.0
    for s in snapshots:
        if math.isfinite(s.rewards_mean) and s.rewards_mean > best_reward:
            best_reward = s.rewards_mean
            best_step = s.step
    ckpt_dir = Path(save_dir)
    ckpts = sorted(ckpt_dir.glob("global_step_*"), key=lambda p: p.name)
    ckpt_steps = [int(p.name.replace("global_step_", "")) for p in ckpts
                  if p.name.replace("global_step_", "").isdigit()]
    return {
        "best_step": best_step,
        "best_reward": best_reward,
        "checkpoints_on_disk": ckpt_steps,
        "total_snapshots": len(snapshots),
        "recommendation": (
            f"Best checkpoint: global_step_{best_step} (reward={best_reward:.4f}). "
            f"Keep this + last 2; discard earlier ones to save disk."
            if ckpt_steps else "No checkpoints found on disk yet."
        ),
    }


# ─── Stop signal ───────────────────────────────────────────────────────────

def write_stop_signal(save_dir: str, reason: str) -> str:
    """Write a STOP signal file that the training wrapper can check."""
    signal_path = os.path.join(save_dir, "RL_STOP_SIGNAL")
    with open(signal_path, "w") as f:
        f.write(f"STOP_REASON: {reason}\n")
        f.write(f"TIMESTAMP: {datetime.now().isoformat()}\n")
        f.write(f"PID: {os.getpid()}\n")
    logger.critical("STOP signal written to %s: %s", signal_path, reason)
    return signal_path


def check_stop_signal(save_dir: str) -> Optional[str]:
    """Check if a STOP signal exists and return the reason."""
    signal_path = os.path.join(save_dir, "RL_STOP_SIGNAL")
    if os.path.exists(signal_path):
        with open(signal_path, "r") as f:
            return f.read().strip()
    return None


# ─── Main monitoring loop ──────────────────────────────────────────────────

def run_monitor(log_dir: str, save_dir: str, poll_interval: int = 30,
                oneshot: bool = False, output_file: Optional[str] = None):
    """Main monitoring loop — parses logs, detects divergence, alerts."""
    state = AlertState()
    all_snapshots: List[MetricSnapshot] = []
    last_step = 0

    print(f"{'='*60}")
    print(f"  RL Training Monitor (R36)")
    print(f"  Log dir   : {log_dir}")
    print(f"  Save dir  : {save_dir}")
    print(f"  Mode      : {'ONESHOT' if oneshot else 'CONTINUOUS'}")
    print(f"{'='*60}")

    existing_stop = check_stop_signal(save_dir)
    if existing_stop:
        print(f"\n  EXISTING STOP SIGNAL:\n{existing_stop}")
        if oneshot:
            return

    while True:
        log_file = find_latest_log(log_dir)
        if not log_file:
            if oneshot:
                print(f"No log file in {log_dir}")
                return
            time.sleep(poll_interval)
            continue

        new_snaps = parse_log_file(log_file, last_step)
        if not new_snaps:
            if oneshot:
                print(f"No new snapshots (last_step={last_step}).")
                break
            time.sleep(poll_interval)
            continue

        for snap in new_snaps:
            last_step = max(last_step, snap.step)
            all_snapshots.append(snap)
            alerts = check_divergence(snap, state)

            for alert in alerts:
                severity = alert["severity"]
                pattern = alert["type"]
                msg = (f"[{alert['timestamp']}] {severity} step={alert['step']} "
                       f"{pattern}: value={alert['value']:.4f} "
                       f"threshold={alert['threshold']:.4f} "
                       f"consecutive={alert['consecutive']}")
                print(msg)
                if severity == "CRITICAL":
                    logger.critical(msg)
                    if pattern in RECOVERY_PROCEDURES:
                        proc = RECOVERY_PROCEDURES[pattern].format(**THRESHOLDS)
                        print(f"  RECOVERY: {proc}")
                    if state.stop_triggered:
                        write_stop_signal(save_dir, f"{pattern} at step {snap.step}")
                else:
                    logger.warning(msg)

            if snap.step % 50 == 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"step={snap.step} reward={snap.rewards_mean:.4f} "
                      f"std={snap.rewards_std:.4f} ent={snap.entropy:.3f} "
                      f"kl={snap.kl_loss:.4f} grad={snap.grad_norm:.2f} "
                      f"alerts={sum(state.fired.values())}")

        if oneshot:
            break

        if output_file:
            try:
                state_data = {
                    "last_step": last_step,
                    "total_snapshots": len(all_snapshots),
                    "active_alerts": {k: v for k, v in state.counts.items() if v > 0},
                    "fired_alerts": {k: v for k, v in state.fired.items() if v},
                    "stop_triggered": state.stop_triggered,
                    "alerts_log": state.alerts_log[-20:],
                }
                with open(output_file, "w") as f:
                    json.dump(state_data, f, indent=2)
            except (IOError, OSError):
                pass

        time.sleep(poll_interval)

    # Final summary
    print(f"\n{'='*60}")
    print(f"  MONITORING SUMMARY")
    print(f"{'='*60}")
    print(f"  Total snapshots : {len(all_snapshots)}")
    if all_snapshots:
        print(f"  Steps covered   : {all_snapshots[0].step}-{all_snapshots[-1].step}")
    print(f"  Alerts fired    : {len(state.alerts_log)}")
    print(f"  Stop triggered  : {state.stop_triggered}")
    if all_snapshots:
        advisory = checkpoint_advisory(all_snapshots, save_dir)
        print(f"\n  Checkpoint Advisory:")
        for k, v in advisory.items():
            print(f"    {k}: {v}")
    if state.alerts_log:
        print(f"\n  Alert Log (last {min(20, len(state.alerts_log))}):")
        for a in state.alerts_log[-20:]:
            print(f"    [{a['severity']}] step={a['step']} {a['type']} "
                  f"value={a['value']:.4f}")


def main():
    """CLI entry point."""
    import argparse as ap
    parser = ap.ArgumentParser(
        description="RL Training Monitor — GRPO divergence detection & early stopping")
    parser.add_argument("--log-dir", required=True, help="Directory with verl logs")
    parser.add_argument("--save-dir", required=True, help="Directory with checkpoints")
    parser.add_argument("--poll-interval", type=int, default=30, help="Seconds between polls")
    parser.add_argument("--oneshot", action="store_true", help="Run once and exit")
    parser.add_argument("--output", default=None, help="Write state JSON to this file")
    parser.add_argument("--clear-stop", action="store_true", help="Clear STOP signal and exit")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    if args.clear_stop:
        sp = os.path.join(args.save_dir, "RL_STOP_SIGNAL")
        if os.path.exists(sp):
            os.remove(sp)
            print(f"Cleared STOP signal: {sp}")
        else:
            print("No STOP signal found.")
        return

    def _sig(signum, frame):
        print("\n[monitor] Exiting...")
        sys.exit(0)
    signal.signal(signal.SIGTERM, _sig)
    signal.signal(signal.SIGINT, _sig)

    run_monitor(
        log_dir=args.log_dir, save_dir=args.save_dir,
        poll_interval=args.poll_interval, oneshot=args.oneshot,
        output_file=args.output,
    )


if __name__ == "__main__":
    main()
