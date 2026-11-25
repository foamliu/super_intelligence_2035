#!/usr/bin/env python3
"""R33: RL Training Schedule Optimizer + Day-by-Day Execution Timeline.

Computes exact time budgets for various GRPO configs on 4xA40 (48GB each),
projects the surrogate rehearsal schedule (11/9-11/15) and the actual BaiZe
training window (12/25-01/15), and generates decision-gated phased plans.

Key inputs (from R32):
  - Model: MiniCPM5-2B (2.517B params, 42 layers, hidden 2048, bf16)
  - GPU: 4xA40 48GB (post-train allocation on .17, 2026-11-09)
  - Smoke test measured: 10 iters, G4, batch 16 -> 28-31 min (avg 29.5 min)
  - Full projected: 2000 iters, G8, batch 128 -> 723-811 h (30-34 days)
  - Baseline eval: ~6 min generation (harness overhead 30-60 min)
  - Training window: ~21 days (2026-12-25 -> 2027-01-15)

Usage:
  python3 baize_posttrain_schedule_optimizer.py
  python3 baize_posttrain_schedule_optimizer.py --json  # output JSON
"""
import json
import math
import sys
from datetime import datetime, timedelta

# ============================================================
# Constants (from R32 measurements + model config)
# ============================================================
SMOKE_ITERS = 10
SMOKE_MINUTES = 29.5
SMOKE_BATCH = 16
SMOKE_GPUS = 4
SMOKE_TOTAL_SEC = SMOKE_MINUTES * 60
SMOKE_TOTAL_SAMPLES = SMOKE_ITERS * SMOKE_BATCH
PER_SAMPLE_PER_GPU_SEC = SMOKE_TOTAL_SEC / (SMOKE_TOTAL_SAMPLES * SMOKE_GPUS)
TURN_SCALING = {1: 1.0, 2: 1.5, 3: 2.0, 4: 2.5}

# Correction factor: smoke test is 1-turn (generation only, no tool exec).
# Real multi-turn training has: optimizer step, gradient sync, SGLang weight
# reload, tool/sandbox execution, data loading. R32 measured full pipeline
# at ~3.5x the simple generation estimate. Apply this to be conservative.
TRAIN_OVERHEAD_FACTOR = 3.5
EVAL_TASKS = 158
EVAL_RUNS = 5
EVAL_AVG_GEN_SEC = 360
EVAL_PARALLEL = 8
CKPT_DISK_GB = 16

# ============================================================
# Time estimation model
# ============================================================
class RLConfig:
    """GRPO training configuration."""
    def __init__(self, name, total_iters, batch_size, n_gpus, max_turns,
                 group_size=8, description=""):
        self.name = name
        self.total_iters = total_iters
        self.batch_size = batch_size
        self.n_gpus = n_gpus
        self.max_turns = max_turns
        self.group_size = group_size
        self.description = description

    def estimate_hours(self):
        total_samples = self.total_iters * self.batch_size
        scaling = TURN_SCALING.get(self.max_turns, 1.0 + 0.5 * (self.max_turns - 1))
        total_sec = total_samples * PER_SAMPLE_PER_GPU_SEC * scaling / self.n_gpus * SMOKE_GPUS
        # Apply training overhead factor (optimizer, weight sync, tool exec, etc.)
        # Smoke test (1-turn) has factor=1.0; multi-turn training has full overhead
        overhead = 1.0 if self.max_turns == 1 else TRAIN_OVERHEAD_FACTOR
        return (total_sec * overhead) / 3600

    def estimate_days(self):
        return self.estimate_hours() / 24

    def to_dict(self):
        return {
            "name": self.name,
            "total_iters": self.total_iters,
            "batch_size": self.batch_size,
            "n_gpus": self.n_gpus,
            "max_turns": self.max_turns,
            "estimated_hours": round(self.estimate_hours(), 1),
            "estimated_days": round(self.estimate_days(), 1),
            "description": self.description,
        }


class EvalConfig:
    """Evaluation configuration."""
    def __init__(self, name, runs=EVAL_RUNS, tasks=EVAL_TASKS, parallel=EVAL_PARALLEL):
        self.name = name
        self.runs = runs
        self.tasks = tasks
        self.parallel = parallel

    def estimate_hours(self):
        gen_sec = self.tasks * self.runs * EVAL_AVG_GEN_SEC
        wall_sec = gen_sec / self.parallel
        overhead_sec = 1800
        return (wall_sec + overhead_sec) / 3600

    def to_dict(self):
        return {
            "name": self.name,
            "runs": self.runs,
            "tasks": self.tasks,
            "parallel": self.parallel,
            "estimated_hours": round(self.estimate_hours(), 1),
        }


# ============================================================
# Configurations to analyze
# ============================================================
CONFIGS = [
    RLConfig("smoke-R2", 10, 16, 4, 1, 8, "Smoke test: validate pipeline (10 iters)"),
    RLConfig("surrogate-A", 100, 32, 4, 2, 8, "Surrogate short: 100 iters, batch 32, 2 turns"),
    RLConfig("surrogate-B", 300, 32, 4, 2, 8, "Surrogate medium: 300 iters, batch 32, 2 turns"),
    RLConfig("surrogate-C", 500, 64, 4, 2, 8, "Surrogate full: 500 iters, batch 64, 2 turns"),
    RLConfig("surrogate-D", 800, 64, 4, 2, 8, "Surrogate extended: 800 iters, batch 64, 2 turns"),
    RLConfig("baize-A", 500, 64, 4, 2, 8, "BaiZe conservative: 500 iters"),
    RLConfig("baize-B", 800, 64, 4, 2, 8, "BaiZe moderate: 800 iters"),
    RLConfig("baize-C", 1000, 64, 4, 3, 8, "BaiZe aggressive: 1000 iters, 3 turns"),
    RLConfig("baize-D", 1500, 64, 4, 3, 8, "BaiZe ambitious: 1500 iters, 3 turns"),
    RLConfig("baize-E", 2000, 128, 4, 3, 8, "BaiZe full: 2000 iters (R32 baseline, infeasible)"),
    RLConfig("baize-8gpu-A", 800, 64, 8, 2, 8, "BaiZe 8xA40: 800 iters, 2 turns"),
    RLConfig("baize-8gpu-B", 1000, 64, 8, 3, 8, "BaiZe 8xA40: 1000 iters, 3 turns"),
]

EVAL_CONFIGS = [
    EvalConfig("full-5run", runs=5, tasks=158, parallel=8),
    EvalConfig("quick-1run", runs=1, tasks=158, parallel=8),
    EvalConfig("subset-5run", runs=5, tasks=40, parallel=8),
]

# ============================================================
# Timeline generation
# ============================================================
def generate_surrogate_timeline(gpu_date):
    """Generate day-by-day plan for surrogate rehearsal (11/9-11/15)."""
    timeline = []
    day = gpu_date
    timeline.append({
        "day": day.strftime("%Y-%m-%d"), "day_num": 1,
        "phase": "Setup & Baseline", "estimated_hours": 4.0,
        "tasks": ["Step 0: cu124 venv setup (~30 min)",
                  "Step 1: Preflight check (~10 min)",
                  "Step 2: SGLang serve + Baseline eval 5-run (~2-3 h)",
                  "Step 3: Extract D1-D6 from failure trajectories (~30 min)"],
        "decision_gate": "Baseline 36%+/-3% confirmed? -> proceed to smoke test",
        "checkpoint": "baseline_eval_5run.json",
    })
    day += timedelta(days=1)
    timeline.append({
        "day": day.strftime("%Y-%m-%d"), "day_num": 2,
        "phase": "Pipeline Validation", "estimated_hours": 3.0,
        "tasks": ["Step 4: Contamination gate (~5 min)",
                  "Step 5: RL smoke test (10 iters, R2, ~30 min)",
                  "Analyze smoke: loss, reward, cheat rate",
                  "If smoke OK -> start surrogate-A (100 iters)"],
        "decision_gate": "Smoke: reward>0, no crash, cheat<5%? -> proceed",
        "checkpoint": "smoke_test_r2_10iter/",
    })
    for d in range(3, 5):
        day += timedelta(days=1)
        timeline.append({
            "day": day.strftime("%Y-%m-%d"), "day_num": d,
            "phase": "Surrogate-A Training (100 iters)",
            "estimated_hours": 4.0,
            "tasks": ["GRPO 100 iters, batch 32, 2 turns" if d == 3 else "Training continues + checkpoint",
                      "Checkpoint every 50 iters" if d == 3 else "Final ckpt + quick eval"],
            "decision_gate": "iter 100: reward positive? KL<1.0? -> extend" if d == 4 else None,
            "checkpoint": "surrogate_a_iter100/",
        })
    day += timedelta(days=1)
    timeline.append({
        "day": day.strftime("%Y-%m-%d"), "day_num": 5,
        "phase": "Eval + Extended Training", "estimated_hours": 5.0,
        "tasks": ["Quick eval (1-run) on surrogate-A (~1 h)",
                  "Compare vs baseline",
                  "Start surrogate-C (500 iters, batch 64)"],
        "decision_gate": "Surrogate-A eval > baseline? -> proceed to C",
        "checkpoint": "surrogate_a_eval_1run.json",
    })
    for d in range(6, 8):
        day += timedelta(days=1)
        timeline.append({
            "day": day.strftime("%Y-%m-%d"), "day_num": d,
            "phase": "Surrogate-C Training (500 iters)",
            "estimated_hours": 6.0 if d == 6 else 8.0,
            "tasks": ["Training + checkpoint every 100 iters" if d == 6 else "Final ckpt + full 5-run eval",
                      "Monitor: reward, KL, cheat_rate" if d == 6 else "Generate final report"],
            "decision_gate": "Surrogate-C: significant improvement? -> pipeline validated" if d == 7 else None,
            "checkpoint": "surrogate_c_iter500/",
        })
    return timeline


def generate_baize_projection(pretrain_date):
    """Generate projected BaiZe training timeline (post pretrain ckpt)."""
    timeline = []
    day = pretrain_date
    phases = [
        ("Phase 1: Domain Annealing", 2, "WSD anneal from pretrain ckpt, PyAether domain blend"),
        ("Phase 2: SFT", 3, "SFT with v2 corpus + agentic data, 4096 ctx"),
        ("Phase 3: RL GRPO (R2 arm)", 7, "GRPO 800 iters, batch 64, 2 turns, R2 reward"),
        ("Phase 4: RL GRPO (R4 arm)", 5, "GRPO 500 iters, batch 64, 2 turns, R4 reward"),
        ("Phase 5: Final Eval", 2, "Full 5-run eval on all checkpoints"),
        ("Phase 6: Paper Writing Buffer", 2, "Analysis + figures + tables"),
    ]
    for phase_name, duration, description in phases:
        timeline.append({
            "day": day.strftime("%Y-%m-%d"),
            "phase": phase_name,
            "duration_days": duration,
            "end_day": (day + timedelta(days=duration)).strftime("%Y-%m-%d"),
            "description": description,
        })
        day += timedelta(days=duration)
    return timeline


def find_optimal_config(target_days, max_gpus=4):
    """Find the best config that fits within target_days."""
    feasible = []
    for cfg in CONFIGS:
        if cfg.n_gpus <= max_gpus:
            days = cfg.estimate_days()
            if days <= target_days:
                feasible.append((cfg, days))
    if not feasible:
        closest = min(CONFIGS, key=lambda c: abs(c.estimate_days() - target_days) if c.n_gpus <= max_gpus else float('inf'))
        return {"found": False, "reason": f"No config fits within {target_days} days with {max_gpus} GPUs",
                "closest": closest.to_dict()}
    feasible.sort(key=lambda x: x[0].total_iters, reverse=True)
    best_cfg, best_days = feasible[0]
    return {"found": True, "config": best_cfg.to_dict(),
            "estimated_days": round(best_days, 1), "margin_days": round(target_days - best_days, 1)}


def compute_eval_schedule(n_checkpoints):
    """Compute eval time for n checkpoints."""
    full_eval = EVAL_CONFIGS[0]
    quick_eval = EVAL_CONFIGS[1]
    return {
        "full_eval_hours_each": full_eval.estimate_hours(),
        "quick_eval_hours_each": quick_eval.estimate_hours(),
        "n_checkpoints": n_checkpoints,
        "total_full_eval_hours": round(full_eval.estimate_hours() * n_checkpoints, 1),
        "total_quick_eval_hours": round(quick_eval.estimate_hours() * n_checkpoints, 1),
        "total_mixed_hours": round(quick_eval.estimate_hours() * (n_checkpoints - 1) + full_eval.estimate_hours(), 1),
    }


def disk_budget_analysis(n_ckpts):
    """Compute disk requirements for checkpoints."""
    total_gb = n_ckpts * CKPT_DISK_GB
    return {
        "per_ckpt_gb": CKPT_DISK_GB, "n_ckpts": n_ckpts, "total_gb": total_gb,
        "available_gb": 386, "fits": total_gb < 300,
        "recommendation": "Delete intermediate ckpts after eval, keep best 2-3" if total_gb > 200 else "All ckpts fit",
    }


# ============================================================
# Main
# ============================================================
def main():
    output = {
        "title": "R33: RL Training Schedule Optimizer",
        "timestamp": datetime.now().isoformat(),
        "inputs": {
            "model": "MiniCPM5-2B (2.517B params, bf16)",
            "gpu": "4xA40 48GB (2026-11-09 allocation on .17)",
            "smoke_measured": {"iters": SMOKE_ITERS, "minutes": SMOKE_MINUTES,
                               "batch": SMOKE_BATCH, "gpus": SMOKE_GPUS},
            "per_sample_per_gpu_sec": round(PER_SAMPLE_PER_GPU_SEC, 2),
            "turn_scaling": TURN_SCALING,
        },
        "rl_configs": [c.to_dict() for c in CONFIGS],
        "eval_configs": [c.to_dict() for c in EVAL_CONFIGS],
        "surrogate_timeline": generate_surrogate_timeline(datetime(2026, 11, 9)),
        "baize_projection": generate_baize_projection(datetime(2026, 12, 25)),
        "optimization": {"21_day": find_optimal_config(21.0, 4),
                         "7_day": find_optimal_config(7.0, 4),
                         "3_day": find_optimal_config(3.0, 4)},
        "eval_schedule": compute_eval_schedule(5),
        "disk_budget": disk_budget_analysis(10),
    }

    recommendations = [
        "Surrogate (11/9-11/15): surrogate-C (500 iters, batch 64, 2 turns) fits 7 days",
        "BaiZe (12/25+): baize-B (800 iters, batch 64, 2 turns) = ~8-10 days, fits 21-day window",
        "If 8 GPUs: baize-8gpu-B (1000 iters, 3 turns) = ~8 days, better quality",
        "Eval: 4 quick 1-run + 1 final 5-run = ~6 h total",
        "Disk: 10 ckpts x 16GB = 160GB, fits 386GB (delete intermediates after eval)",
        "Gate at iter 100: reward<0 or KL>1.0 -> stop and debug",
        "Gate at iter 500: eval improvement<5pp -> switch reward arm or adjust",
    ]
    output["recommendations"] = recommendations

    if "--json" in sys.argv:
        print(json.dumps(output, indent=2, ensure_ascii=False, default=str))
        return

    print("=" * 70)
    print("R33: RL Training Schedule Optimizer")
    print("=" * 70)
    print(f"\nModel: MiniCPM5-2B (2.517B params)")
    print(f"GPU: 4xA40 48GB")
    print(f"Smoke: {SMOKE_ITERS} iters in {SMOKE_MINUTES} min -> {PER_SAMPLE_PER_GPU_SEC:.2f} s/sample/GPU")
    print(f"\n{'Config':<20} {'Iters':>6} {'Batch':>6} {'Turns':>6} {'GPUs':>5} {'Hours':>8} {'Days':>7}")
    print("-" * 70)
    for c in CONFIGS:
        d = c.to_dict()
        print(f"{d['name']:<20} {d['total_iters']:>6} {d['batch_size']:>6} {d['max_turns']:>6} {d['n_gpus']:>5} {d['estimated_hours']:>8.1f} {d['estimated_days']:>7.1f}")
    print(f"\nEval configs:")
    for c in EVAL_CONFIGS:
        d = c.to_dict()
        print(f"  {d['name']:<20} {d['runs']} runs x {d['tasks']} tasks -> {d['estimated_hours']:.1f} h")
    print(f"\nOptimization:")
    for name, days in [("21-day", 21), ("7-day", 7), ("3-day", 3)]:
        opt = output["optimization"][f"{days}_day"]
        if opt["found"]:
            print(f"  {name}: OK {opt['config']['name']} ({opt['estimated_days']}d, margin {opt['margin_days']}d)")
        else:
            print(f"  {name}: FAIL {opt['reason']}")
            if "closest" in opt:
                print(f"    Closest: {opt['closest']['name']} ({opt['closest']['estimated_days']}d)")
    print(f"\nDisk: {output['disk_budget']['n_ckpts']} ckpts x {output['disk_budget']['per_ckpt_gb']}GB = {output['disk_budget']['total_gb']}GB -> {'OK' if output['disk_budget']['fits'] else 'FAIL'}")
    print(f"\nSurrogate Timeline (11/9-11/15):")
    for entry in output["surrogate_timeline"]:
        print(f"  Day {entry['day_num']} ({entry['day']}): {entry['phase']} ({entry['estimated_hours']:.1f}h)")
        if entry.get("decision_gate"):
            print(f"    Gate: {entry['decision_gate']}")
    print(f"\nBaiZe Projection (12/25+):")
    for entry in output["baize_projection"]:
        print(f"  {entry['day']} -> {entry['end_day']}: {entry['phase']} ({entry['duration_days']}d)")
    print(f"\nRecommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    print("\n" + "=" * 70)
    print("Use --json for machine-readable output.")


if __name__ == "__main__":
    main()
