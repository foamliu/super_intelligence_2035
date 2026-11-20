#!/usr/bin/env python3
"""
R142: RL Training Step Budget Allocation & Convergence Projection
=================================================================
Synthesizes R138-R141 into actionable RL training schedule.
Zero GPU — pure simulation/analysis.
"""
import json, math, sys
from pathlib import Path
from dataclasses import dataclass, asdict

# === Constants from prior research ===
GPU_COUNT = 4; GPU_MEM_GB = 46.0
FULL_FT_SPH = 2.5   # R138: S5 config steps/h
LORA_SPH = 3.0      # R138: S4 LoRA steps/h
ROLLOUT_RPH = 666   # R141: rollouts/h
GROUP_SIZE = 8      # R140: G=8
RPS = GROUP_SIZE * 4  # rollouts per step (4 groups)
ROLLOUT_SPH = ROLLOUT_RPH / RPS  # steps/h from rollout side
CKPT_SAVE_MIN = 3.0; CKPT_LOAD_MIN = 3.5; RECOVERY_MIN = 16.0
EVAL_TIME_MIN = 45.0; EVAL_FREQ = 50; CKPT_FREQ = 25
COLLAPSE_PROB = 0.15  # per 100 steps (R139)

CURRICULUM = [
    {"name":"Warmup","steps":50,"levels":["L1"],"replay":0.0,"reward":"R0"},
    {"name":"Foundation","steps":100,"levels":["L1","L2"],"replay":0.0,"reward":"R2+R5"},
    {"name":"Development","steps":150,"levels":["L2","L3"],"replay":0.20,"reward":"R2+R5"},
    {"name":"Refinement","steps":150,"levels":["L3","L4"],"replay":0.25,"reward":"R3+anti-cheat"},
    {"name":"Mastery","steps":100,"levels":["L4","L5"],"replay":0.30,"reward":"R3+R4"},
]
CURR_TOTAL = sum(s["steps"] for s in CURRICULUM)  # 550
MILESTONES = {"baseline":0.36,"M1":0.50,"M2":0.65,"M3":0.75,"M4":0.85}
RL_WINDOW_DAYS = 21

# === Convergence models ===
def sigmoid_c(step, max_gain, midpoint, steepness):
    return max_gain / (1 + math.exp(-steepness * (step - midpoint)))

def log_c(step, max_gain, decay):
    return max_gain * (1 - math.exp(-decay * step))

def power_c(step, max_gain, alpha, beta):
    return max_gain * (step**alpha) / (beta + step**alpha)

def project_trajectory(total_steps, baseline=0.36, target_gain=0.39, model="sigmoid"):
    traj = []
    for s in range(0, total_steps + 1, 5):
        if model == "sigmoid":
            mid = total_steps * 0.40; steep = 8.0 / total_steps
            gain = sigmoid_c(s, target_gain, mid, steep)
        elif model == "logarithmic":
            gain = log_c(s, target_gain, 5.0 / total_steps)
        elif model == "power_law":
            gain = power_c(s, target_gain, 0.7, total_steps * 0.15)
        else: gain = 0
        traj.append({"step": s, "reward": round(baseline + gain, 4), "gain": round(gain, 4)})
    return traj

def project_milestones(traj, milestones=MILESTONES):
    res = []
    for name, target in milestones.items():
        sr = next((p["step"] for p in traj if p["reward"] >= target), None)
        res.append({"milestone": name, "target": target, "step_reached": sr, "reached": sr is not None})
    return res

# === Early stopping criteria ===
@dataclass
class ESCriterion:
    name: str; desc: str; window: int; threshold: float; action: str; severity: str

EARLY_STOP = [
    ESCriterion("reward_plateau","Mean reward improvement <0.5% over 30 steps",30,0.005,"stop","info"),
    ESCriterion("eval_plateau","Eval Pass@1 improvement <1pp over 2 evals",100,0.01,"stop","info"),
    ESCriterion("reward_hacking","Cheat rate >5% (R135)",10,0.05,"rollback","critical"),
    ESCriterion("kl_divergence","KL >5.0 from ref model (R132)",1,5.0,"rollback","critical"),
    ESCriterion("entropy_collapse","Policy entropy <0.01 (R139 C3)",5,0.01,"warn","warning"),
    ESCriterion("loss_nan","NaN in loss (R139 C4, FATAL)",1,1.0,"stop","critical"),
    ESCriterion("overfitting","Train reward↑ but eval↓ over 2 evals",100,0.0,"stop","warning"),
]

def compute_timeline(total_steps, sph, eval_freq=EVAL_FREQ, ckpt_freq=CKPT_FREQ, collapse_prob=COLLAPSE_PROB):
    """Compute realistic wall-clock with checkpoint/eval/recovery overheads."""
    pure_h = total_steps / sph
    n_ckpts = total_steps // ckpt_freq
    n_evals = total_steps // eval_freq
    n_periods = total_steps // 100
    exp_collapses = n_periods * collapse_prob
    ckpt_h = n_ckpts * CKPT_SAVE_MIN / 60
    eval_h = n_evals * EVAL_TIME_MIN / 60
    recov_h = exp_collapses * RECOVERY_MIN / 60
    warmup_h = 5/60
    overhead = ckpt_h + eval_h + recov_h
    total = pure_h + overhead + warmup_h
    return {
        "pure_training_h": round(pure_h, 2), "checkpoint_h": round(ckpt_h, 2),
        "evaluation_h": round(eval_h, 2), "recovery_h": round(recov_h, 2),
        "warmup_h": round(warmup_h, 3), "total_overhead_h": round(overhead, 2),
        "total_wall_h": round(total, 2), "overhead_pct": round(overhead/total*100, 1),
        "n_checkpoints": n_ckpts, "n_evaluations": n_evals, "expected_collapses": round(exp_collapses, 2),
    }

def allocate_curriculum(budget_steps, stages=CURRICULUM):
    """Scale curriculum to fit budget."""
    scale = budget_steps / CURR_TOTAL
    alloc = []
    for s in stages:
        steps = max(10, int(s["steps"] * scale))
        alloc.append({"name": s["name"], "steps": steps, "levels": s["levels"],
                      "replay_ratio": s["replay"], "reward_config": s["reward"],
                      "rollouts": steps * RPS, "wall_clock_h": round(steps / ROLLOUT_SPH, 2)})
    return alloc, sum(a["steps"] for a in alloc)

# === Main ===
def main():
    print("=" * 80)
    print("R142: RL Training Step Budget Allocation & Convergence Projection")
    print("=" * 80)
    R = {}

    # [1] Throughput reconciliation
    print("\n[1] Throughput Reconciliation (R138 vs R140 vs R141)")
    print("-" * 50)
    eff_ft = min(FULL_FT_SPH, ROLLOUT_SPH)
    eff_lora = min(LORA_SPH, ROLLOUT_SPH)
    bottleneck = "R138 training compute (Full FT)" if FULL_FT_SPH < ROLLOUT_SPH else "R141 rollout"
    print(f"  R138 Full FT: {FULL_FT_SPH:.1f} steps/h | R141 rollout: {ROLLOUT_SPH:.1f} steps/h | R140 budget: 78.4h")
    print(f"  Bottleneck: {bottleneck}")
    print(f"  Effective: Full FT={eff_ft:.1f} steps/h, LoRA={eff_lora:.1f} steps/h")
    print(f"  Rollout headroom: {ROLLOUT_SPH/FULL_FT_SPH:.1f}× (rollout NOT the bottleneck)")
    R["throughput"] = {"r138_ft": FULL_FT_SPH, "r141_rollout": round(ROLLOUT_SPH, 2),
                       "effective_ft": eff_ft, "effective_lora": eff_lora,
                       "bottleneck": bottleneck, "rollout_headroom": round(ROLLOUT_SPH/FULL_FT_SPH, 1)}

    # [2] Step budget for 21-day window
    print("\n[2] Step Budget for 21-Day RL Window")
    print("-" * 50)
    avail_h = RL_WINDOW_DAYS * 24  # 504h
    rl_h = avail_h * 0.70  # 352.8h after SFT/eval/debug reserve
    pure_h = rl_h * 0.85  # 299.9h after overhead reserve
    max_ft = int(pure_h * eff_ft)
    max_lora = int(pure_h * eff_lora)
    print(f"  Window: {RL_WINDOW_DAYS}d={avail_h}h → RL alloc(70%)={rl_h:.0f}h → pure(85%)={pure_h:.0f}h")
    print(f"  Max steps: Full FT={max_ft}, LoRA={max_lora}")
    print(f"  Curriculum needs: {CURR_TOTAL} steps")
    print(f"  Full FT feasible: {'YES' if max_ft >= CURR_TOTAL else 'NO'} | LoRA: {'YES' if max_lora >= CURR_TOTAL else 'NO'}")
    R["step_budget"] = {"window_h": avail_h, "rl_h": round(rl_h, 1), "pure_h": round(pure_h, 1),
                        "max_ft": max_ft, "max_lora": max_lora, "curriculum": CURR_TOTAL,
                        "feasible_ft": max_ft >= CURR_TOTAL, "feasible_lora": max_lora >= CURR_TOTAL}

    # [3] Convergence projection (3 models, 750 steps)
    print("\n[3] Convergence Projection (750 steps, 3 models)")
    print("-" * 50)
    proj_steps = 750; target_gain = 0.39
    models = {}
    for mn in ["sigmoid", "logarithmic", "power_law"]:
        t = project_trajectory(proj_steps, target_gain=target_gain, model=mn)
        ms = project_milestones(t)
        models[mn] = {"final": t[-1]["reward"], "milestones": ms}
        print(f"\n  {mn}: final={t[-1]['reward']:.1%}")
        for m in ms:
            st = f"step {m['step_reached']}" if m['reached'] else "NOT REACHED"
            print(f"    {m['milestone']}: {m['target']:.0%} → {st}")
    R["convergence"] = {"steps": proj_steps, "baseline": 0.36, "target": 0.75,
                        "models": {k: {"final_reward": v["final"], "milestones": v["milestones"]} for k, v in models.items()}}

    # [4] Timeline with overheads (750 steps, Full FT)
    print("\n[4] Detailed Timeline (750 steps, Full FT)")
    print("-" * 50)
    tl = compute_timeline(750, eff_ft)
    print(f"  Pure training: {tl['pure_training_h']:.1f}h ({tl['pure_training_h']/24:.1f}d)")
    print(f"  Checkpoints:   {tl['checkpoint_h']:.1f}h ({tl['n_checkpoints']} saves)")
    print(f"  Evaluations:   {tl['evaluation_h']:.1f}h ({tl['n_evaluations']} runs)")
    print(f"  Recovery:      {tl['recovery_h']:.1f}h ({tl['expected_collapses']} expected collapses)")
    print(f"  TOTAL:         {tl['total_wall_h']:.1f}h ({tl['total_wall_h']/24:.1f}d)")
    print(f"  Overhead:      {tl['overhead_pct']:.1f}%")
    R["timeline"] = tl

    # [5] Curriculum allocation (750 steps)
    print("\n[5] Curriculum Allocation (budget=750)")
    print("-" * 50)
    alloc, total_a = allocate_curriculum(750)
    cum = 0
    for a in alloc:
        cum += a["steps"]
        print(f"  {a['name']:12s}: {a['steps']:4d} steps | {','.join(a['levels']):12s} | replay={a['replay_ratio']:.0%} | {a['rollouts']:5d} R | cum={cum}")
    print(f"  {'TOTAL':12s}: {total_a:4d} steps")
    R["curriculum"] = {"total": total_a, "stages": alloc}

    # [6] Early stopping criteria
    print("\n[6] Early Stopping Criteria (7 rules)")
    print("-" * 50)
    for c in EARLY_STOP:
        print(f"  [{c.severity:8s}] {c.name:20s} | window={c.window:3d} | thresh={c.threshold} | {c.action}")
    R["early_stopping"] = [asdict(c) for c in EARLY_STOP]

    # [7] ISEDA deadline fit
    print("\n[7] ISEDA Deadline Fit")
    print("-" * 50)
    sft_d = 5; rl_d = tl['total_wall_h'] / 24; eval_d = 3; paper_d = 7
    total_d = sft_d + rl_d + eval_d + paper_d
    avail_d = 37  # 12/26 → 01/31
    fits = total_d <= avail_d
    print(f"  SFT={sft_d}d + RL={rl_d:.1f}d + Eval={eval_d}d + Paper={paper_d}d = {total_d:.1f}d")
    print(f"  Available: {avail_d}d | Fits: {'YES' if fits else 'NO'} | Slack: {avail_d-total_d:.1f}d")
    R["deadline"] = {"sft_d": sft_d, "rl_d": round(rl_d, 1), "eval_d": eval_d, "paper_d": paper_d,
                     "total_d": round(total_d, 1), "avail_d": avail_d, "fits": fits, "slack_d": round(avail_d-total_d, 1)}

    # [8] Sensitivity: steps vs final reward (sigmoid)
    print("\n[8] Sensitivity — Steps vs Final Reward (sigmoid)")
    print("-" * 50)
    sens = {}
    for n in [300, 500, 550, 750, 1000, 1500, 2000]:
        t = project_trajectory(n, model="sigmoid")
        final = t[-1]["reward"]
        wh = n / eff_ft
        m3 = any(p["reward"] >= 0.75 for p in t)
        print(f"  {n:5d} steps → {final:.1%} | {wh:.1f}h ({wh/24:.1f}d) | M3(75%)={'Y' if m3 else 'N'}")
        sens[str(n)] = {"final": final, "wall_h": round(wh, 1), "m3_reached": m3}
    R["sensitivity"] = sens

    # [9] Recommendations
    print("\n[9] Key Recommendations")
    print("-" * 50)
    m3_step = next((m["step_reached"] for m in models["sigmoid"]["milestones"] if m["milestone"] == "M3"), None)
    recs = [
        f"1. Full FT (S5) primary — {eff_ft:.1f} steps/h, 750 steps in {tl['total_wall_h']:.0f}h",
        f"2. LoRA fallback — {eff_lora:.1f} steps/h, 20% faster but may limit M4 ceiling",
        f"3. 750 steps recommended (1.36x R130's 550) — depth vs deadline balance",
        f"4. Overhead={tl['overhead_pct']:.0f}% — eval={tl['evaluation_h']:.1f}h + ckpt={tl['checkpoint_h']:.1f}h + recovery={tl['recovery_h']:.1f}h",
        f"5. Sigmoid model: M3(75%) at step ~{m3_step}",
        f"6. Early stop: reward_plateau + eval_plateau + overfitting → stop; KL>5 or cheat>5% → rollback",
        f"7. Eval every 50 steps ({tl['n_evaluations']} runs) — milestone tracking critical",
        f"8. Checkpoint every 25 steps ({tl['n_checkpoints']} saves) — enables rollback",
        f"9. Expected {tl['expected_collapses']:.1f} collapses → {tl['recovery_h']:.1f}h recovery",
        f"10. ISEDA fit: {'YES' if fits else 'NO'} (slack={avail_d-total_d:.1f}d)",
    ]
    for r in recs: print(f"  {r}")
    R["recommendations"] = recs

    # Save report
    rp = Path(__file__).parent / "r142_rl_budget_convergence_report.json"
    with open(rp, "w") as f: json.dump(R, f, indent=2, ensure_ascii=False)
    print(f"\nReport: {rp} ({rp.stat().st_size/1024:.1f} KB)")
    print("=" * 80)
    print("R142 Complete")
    print("=" * 80)

if __name__ == "__main__":
    main()
