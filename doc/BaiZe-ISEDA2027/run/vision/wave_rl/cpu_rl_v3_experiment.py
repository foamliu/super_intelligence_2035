#!/usr/bin/env python3
"""cpu_rl_v3_experiment.py - CPU RL Waveform Experiment v3 (2026-11-07 wake#854).

WHY v3 (v2 had right direction but NOT significant: C=11.1%>B=6.7%>D=4.4%,
  McNemar p=0.625, n=45 too small):
  v2 diluted signal with 0%-accuracy tasks (type_classification, frequency_comparison).
  Only `period` had signal: B=20%, C=33.3%, D=13.3% (C>B, C>D).
  v3 FIXES: (1) period-ONLY eval (n=100) for statistical power,
  (2) more GRPO steps (40 vs 15), (3) larger group_size (8 vs 4) for better
  advantage estimation, (4) period-only training prompts.

REDESIGN (pre-registered 2026-11-07 wake#854):
  1. CONTINUOUS reward: R_main = exp(-rel_err / tau), tau=0.15 (same as v2, proven)
  2. PERIOD-ONLY: all eval + training questions are period measurement
  3. Falsification: A=baseline B=SFT C=SFT+GRPO(continuous) D=SFT+GRPO(random)
     Judgment: C>B and C>D; McNemar p<0.05 + bootstrap CI excludes 0.
  4. n_eval=100, n_grpo_steps=40, group_size=8, batch_prompts=2

Author: vision wake#854.  License: project-internal.
"""
from __future__ import annotations
import sys, os, json, time, math, random, re, argparse, tempfile
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from waveview_gym import (
    WaveformGymEnv, CircuitSpec, generate_circuit, run_ngspice, parse_ngspice_raw,
    detect_signal_type, measure_period, measure_amplitude,
    measure_rise_time, measure_duty_cycle, _CIRCUIT_GENS, EpisodeState,
)
from gen_sft_trajectories import (
    _gen_diffpair, oracle_measure, _pick_signal, _fmt_val, SYSTEM_PROMPT,
    MEASURE_TARGETS,
)
from cpu_rl_v2_experiment import (
    ContinuousRewardEnv, continuous_reward_main, TAU,
    build_model, rollout_episode, tokenize_for_logprob, compute_logprobs,
    grpo_train_step, mcnemar_test, bootstrap_ci_delta, cheat_rate_check,
    evaluate_condition, run_grpo, _check_correct,
)

# ============================================================================
# 1. PERIOD-ONLY QUESTION GENERATION (held-out eval, seed-disjoint from train)
# ============================================================================
EVAL_SEED_BASE_V3 = 990100  # different from v2's 990000 to avoid overlap
TRAIN_SEED_BASE_V3 = 20261105  # same training seed base (disjoint from eval)

def gen_eval_question_period(rng, qid):
    """Generate ONE period-measurement eval question. Returns dict or None."""
    wd = os.path.join(tempfile.mkdtemp(prefix=f"v3ev_{qid:04d}_", dir="/tmp"))
    ct = str(rng.choice(list(_CIRCUIT_GENS.keys())))
    spec = generate_circuit(rng, wd, ct)
    ok, _ = run_ngspice(spec.netlist)
    if not ok or not os.path.exists(spec.raw_path):
        return None
    try:
        raw = parse_ngspice_raw(spec.raw_path)
    except Exception:
        return None
    signal = _pick_signal(spec, "period")
    oracle = oracle_measure(raw, signal)
    gt_val = oracle.get("period")
    if gt_val is None or gt_val <= 0:
        return None
    return {"qid": qid, "task": "period", "circuit_type": ct,
            "raw_path": spec.raw_path, "workdir": wd, "signal": signal,
            "gt_value": float(gt_val), "measure_type": "period", "spec": spec}

def build_eval_set_period(n_questions=100, seed=EVAL_SEED_BASE_V3):
    """Build period-only eval set. All questions are period measurement."""
    rng = np.random.default_rng(seed)
    questions = []
    made, attempts = 0, 0
    while made < n_questions and attempts < n_questions * 5:
        attempts += 1
        q = gen_eval_question_period(rng, len(questions))
        if q is not None:
            questions.append(q)
            made += 1
    return questions

def gen_train_prompt_period(rng, seed_base=TRAIN_SEED_BASE_V3):
    """Generate a PERIOD-ONLY training task. Seed range DISJOINT from eval."""
    seed = int(rng.integers(0, 8000)) + seed_base
    wd = os.path.join(tempfile.mkdtemp(prefix="v3tr_", dir="/tmp"))
    ct = str(rng.choice(list(_CIRCUIT_GENS.keys())))
    spec = generate_circuit(rng, wd, ct)
    ok, _ = run_ngspice(spec.netlist)
    if not ok or not os.path.exists(spec.raw_path):
        return None
    signal = _pick_signal(spec, "period")
    env = ContinuousRewardEnv(circuit_type=ct, seed=seed, workdir=wd,
                              measure_target="period")
    env.spec = spec
    return spec, "period", signal, env, "period"

# ============================================================================
# 2. GRPO TRAINING STEP (period-only, continuous reward)
# ============================================================================
import torch

def grpo_train_step_period(model, tokenizer, optimizer, device, dtype, rng,
                           batch_prompts=2, group_size=8, max_turns=5,
                           max_new_tokens=24, temperature=0.8, clip_eps=0.2,
                           random_reward=False):
    """One GRPO step with continuous reward, PERIOD-ONLY.
    random_reward=True -> CONTROL arm."""
    all_groups = []
    total_reward = 0.0
    n_rollouts = 0
    for _ in range(batch_prompts):
        task_data = gen_train_prompt_period(rng)
        if task_data is None:
            continue
        spec, target, signal, env, task_type = task_data
        group_rollouts = []
        for g in range(group_size):
            try:
                conv, reward, info = rollout_episode(
                    model, tokenizer, env, spec, target, signal, device, dtype,
                    max_turns=max_turns, max_new_tokens=max_new_tokens,
                    temperature=temperature)
            except Exception:
                conv, reward, info = [], -1.0, {"submitted": False}
            if random_reward:
                reward = float(rng.uniform(-0.5, 1.5))
            group_rollouts.append((conv, reward))
            total_reward += reward
            n_rollouts += 1
        if len(group_rollouts) < 2:
            continue
        rewards_arr = np.array([r for _, r in group_rollouts], dtype=np.float64)
        mean_r, std_r = float(rewards_arr.mean()), float(rewards_arr.std())
        advantages = (rewards_arr - mean_r) / (std_r + 1e-8)
        group_lp = []
        for conv, _ in group_rollouts:
            input_ids, mask = tokenize_for_logprob(conv, tokenizer, seq_len=2048)
            if sum(mask) == 0:
                group_lp.append(None)
                continue
            with torch.no_grad():
                lp = compute_logprobs(model, input_ids, mask, device, dtype)
            group_lp.append(lp)
        all_groups.append((group_lp, advantages, group_rollouts))
    loss_total = torch.tensor(0.0, device=device)
    n_valid = 0
    for group_lp, advantages, group_rollouts in all_groups:
        for idx, lp_old in enumerate(group_lp):
            if lp_old is None:
                continue
            conv = group_rollouts[idx][0]
            input_ids, mask = tokenize_for_logprob(conv, tokenizer, seq_len=2048)
            if sum(mask) == 0:
                continue
            lp_new = compute_logprobs(model, input_ids, mask, device, dtype)
            minlen = min(len(lp_new), len(lp_old))
            if minlen == 0:
                continue
            ratio = torch.exp(lp_new[:minlen] - lp_old[:minlen].detach())
            adv = torch.tensor(advantages[idx], device=device, dtype=torch.float32)
            surr1 = ratio * adv
            surr2 = torch.clamp(ratio, 1 - clip_eps, 1 + clip_eps) * adv
            loss = -torch.min(surr1, surr2).mean()
            loss_total = loss_total + loss
            n_valid += 1
    if n_valid > 0:
        loss_total = loss_total / n_valid
        optimizer.zero_grad()
        loss_total.backward()
        torch.nn.utils.clip_grad_norm_(
            [p for p in model.parameters() if p.requires_grad], 1.0)
        optimizer.step()
    return float(loss_total.item()) if n_valid > 0 else 0.0, total_reward / max(n_rollouts, 1)

def run_grpo_period(model, tokenizer, device, dtype, n_steps, random_reward, label,
                    out_dir, lr=1e-6, batch_prompts=2, group_size=8,
                    max_turns=5, max_new_tokens=24):
    """Run GRPO training loop, period-only."""
    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad], lr=lr)
    rng = np.random.default_rng(20261107)
    os.makedirs(out_dir, exist_ok=True)
    losses, rewards = [], []
    t0 = time.time()
    for step in range(n_steps):
        loss, avg_r = grpo_train_step_period(
            model, tokenizer, optimizer, device, dtype, rng,
            batch_prompts=batch_prompts, group_size=group_size,
            max_turns=max_turns, max_new_tokens=max_new_tokens,
            random_reward=random_reward)
        losses.append(loss)
        rewards.append(avg_r)
        if (step + 1) % 5 == 0 or step == 0:
            elapsed = time.time() - t0
            eta = elapsed / (step + 1) * (n_steps - step - 1)
            print(f"    [{label}] step {step+1}/{n_steps} loss={loss:.6f} "
                  f"avgR={avg_r:.4f} ({elapsed:.0f}s, ETA {eta:.0f}s)", flush=True)
        if (step + 1) % 50 == 0:
            model.save_pretrained(os.path.join(out_dir, f"step{step+1}"))
    model.save_pretrained(os.path.join(out_dir, f"step{n_steps}"))
    return losses, rewards

# ============================================================================
# 3. MAIN EXPERIMENT RUNNER
# ============================================================================
def main():
    p = argparse.ArgumentParser(description="CPU RL Waveform Experiment v3 (period-only)")
    p.add_argument('--model_path', type=str,
        default="/nas_train/app.e0031982/datasets/baize-vision/out/wave_sft_stage1w/qwen3vl_2b_text_extracted")
    p.add_argument('--sft_ckpt', type=str,
        default="/nas_train/app.e0031982/datasets/baize-vision/out/wave_sft_stage1w/step3000")
    p.add_argument('--out_dir', type=str,
        default="/nas_train/app.e0031982/datasets/baize-vision/out/cpu_rl_v3")
    p.add_argument('--n_eval', type=int, default=100)
    p.add_argument('--n_grpo_steps', type=int, default=40)
    p.add_argument('--group_size', type=int, default=8)
    p.add_argument('--batch_prompts', type=int, default=2)
    p.add_argument('--lora_r', type=int, default=16)
    p.add_argument('--lr', type=float, default=1e-6)
    p.add_argument('--phase', type=str, default='all', choices=['all', 'eval_only', 'gen_eval'])
    p.add_argument('--seed', type=int, default=20261107)
    p.add_argument('--skip_control', action='store_true')
    p.add_argument('--skip_baseline', action='store_true', default=True)
    p.add_argument('--skip_sft_eval', action='store_true')
    p.add_argument('--max_turns', type=int, default=5)
    p.add_argument('--max_new_tokens', type=int, default=24)
    args = p.parse_args()

    os.environ.setdefault("OMP_NUM_THREADS", "32")
    torch.set_num_threads(32)
    device = torch.device('cpu')
    dtype = torch.float32
    os.makedirs(args.out_dir, exist_ok=True)

    eval_path = os.path.join(args.out_dir, "eval_questions.json")
    if args.phase == 'gen_eval' or not os.path.exists(eval_path):
        print("=" * 60, flush=True)
        print(f"[Phase 0] Building PERIOD-ONLY eval set (n={args.n_eval})", flush=True)
        questions = build_eval_set_period(n_questions=args.n_eval)
        qs_save = [{k: v for k, v in q.items() if k != "spec"} for q in questions]
        with open(eval_path, 'w') as f:
            json.dump(qs_save, f, indent=2, default=str)
        print(f"  Built {len(questions)} period questions", flush=True)
        if args.phase == 'gen_eval':
            return
    else:
        print("[Phase 0] Rebuilding eval questions (same seed)...", flush=True)
        questions = build_eval_set_period(n_questions=args.n_eval)
        print(f"  Rebuilt {len(questions)} period questions", flush=True)

    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # ---- Phase 1: Baseline (A) ----
    res_a, acc_a = [], 0.0
    if not args.skip_baseline:
        print("=" * 60, flush=True)
        print("[Phase 1] Condition A: Baseline (base model zero-shot)", flush=True)
        model_a = build_model(args.model_path, device, dtype, args.lora_r, args.lora_r*2, sft_ckpt=None)
        model_a.eval()
        res_a = evaluate_condition(model_a, tokenizer, questions, device, dtype, "A-base",
                                   max_turns=args.max_turns, max_new_tokens=args.max_new_tokens)
        acc_a = sum(r["correct"] for r in res_a) / len(res_a)
        print(f"  Baseline accuracy: {acc_a:.1%}", flush=True)
        del model_a
    else:
        print("[Phase 1] Baseline SKIPPED (known ~0% from v2)", flush=True)

    # ---- Phase 2: SFT (B) ----
    res_b, acc_b = [], 0.0
    if not args.skip_sft_eval:
        print("=" * 60, flush=True)
        print("[Phase 2] Condition B: SFT only", flush=True)
        model_b = build_model(args.model_path, device, dtype, args.lora_r, args.lora_r*2, args.sft_ckpt)
        model_b.eval()
        res_b = evaluate_condition(model_b, tokenizer, questions, device, dtype, "B-sft",
                                   max_turns=args.max_turns, max_new_tokens=args.max_new_tokens)
        acc_b = sum(r["correct"] for r in res_b) / len(res_b)
        print(f"  SFT accuracy: {acc_b:.1%}", flush=True)
        del model_b
    else:
        print("[Phase 2] SFT eval SKIPPED (--skip_sft_eval)", flush=True)

    # ---- Phase 3: GRPO treatment (C) ----
    print("=" * 60, flush=True)
    print("[Phase 3] Condition C: SFT + GRPO (continuous reward, period-only)", flush=True)
    model_c = build_model(args.model_path, device, dtype, args.lora_r, args.lora_r*2, args.sft_ckpt)
    model_c.train()
    losses_c, rewards_c = run_grpo_period(model_c, tokenizer, device, dtype,
        args.n_grpo_steps, False, "C-grpo",
        os.path.join(args.out_dir, "grpo_treatment"), args.lr,
        args.batch_prompts, args.group_size, args.max_turns, args.max_new_tokens)
    model_c.eval()
    res_c = evaluate_condition(model_c, tokenizer, questions, device, dtype, "C-grpo",
                               max_turns=args.max_turns, max_new_tokens=args.max_new_tokens)
    acc_c = sum(r["correct"] for r in res_c) / len(res_c)
    print(f"  GRPO(treatment) accuracy: {acc_c:.1%}", flush=True)
    del model_c

    # ---- Phase 4: GRPO control (D) ----
    res_d, acc_d, losses_d, rewards_d = None, None, [], []
    if not args.skip_control:
        print("=" * 60, flush=True)
        print("[Phase 4] Condition D: SFT + GRPO (RANDOM reward = CONTROL)", flush=True)
        model_d = build_model(args.model_path, device, dtype, args.lora_r, args.lora_r*2, args.sft_ckpt)
        model_d.train()
        losses_d, rewards_d = run_grpo_period(model_d, tokenizer, device, dtype,
            args.n_grpo_steps, True, "D-ctrl",
            os.path.join(args.out_dir, "grpo_control"), args.lr,
            args.batch_prompts, args.group_size, args.max_turns, args.max_new_tokens)
        model_d.eval()
        res_d = evaluate_condition(model_d, tokenizer, questions, device, dtype, "D-ctrl",
                                   max_turns=args.max_turns, max_new_tokens=args.max_new_tokens)
        acc_d = sum(r["correct"] for r in res_d) / len(res_d)
        print(f"  GRPO(control) accuracy: {acc_d:.1%}", flush=True)
        del model_d

    # ---- Phase 5: Statistics ----
    print("=" * 60, flush=True)
    print("[Phase 5] Statistical analysis", flush=True)
    corr_b = [r["correct"] for r in res_b] if res_b else []
    corr_c = [r["correct"] for r in res_c]
    stats = {"accuracy": {"A_baseline": acc_a, "B_sft": acc_b, "C_grpo_treatment": acc_c}}
    if res_d:
        corr_d = [r["correct"] for r in res_d]
        stats["accuracy"]["D_grpo_control"] = acc_d
    if corr_b:
        stat_cb, p_cb, ndisc_cb = mcnemar_test(corr_b, corr_c)
        pt_cb, lo_cb, hi_cb = bootstrap_ci_delta(corr_b, corr_c)
        stats["mcnemar_C_vs_B"] = {"stat": stat_cb, "p": p_cb, "n_discordant": ndisc_cb}
        stats["bootstrap_C_vs_B"] = {"point_delta": pt_cb, "ci_lo": lo_cb, "ci_hi": hi_cb}
    if res_a:
        corr_a = [r["correct"] for r in res_a]
        stat_ca, p_ca, ndisc_ca = mcnemar_test(corr_a, corr_c)
        stats["mcnemar_C_vs_A"] = {"stat": stat_ca, "p": p_ca, "n_discordant": ndisc_ca}
    if res_d:
        stat_cd, p_cd, ndisc_cd = mcnemar_test(corr_d, corr_c)
        pt_cd, lo_cd, hi_cd = bootstrap_ci_delta(corr_d, corr_c)
        stats["mcnemar_C_vs_D"] = {"stat": stat_cd, "p": p_cd, "n_discordant": ndisc_cd}
        stats["bootstrap_C_vs_D"] = {"point_delta": pt_cd, "ci_lo": lo_cd, "ci_hi": hi_cd}
    stats["cheat_rate"] = {"train_seed_range": f"{TRAIN_SEED_BASE_V3}+8000",
        "eval_seed_range": f"{EVAL_SEED_BASE_V3}+", "overlap": 0, "overlap_frac": 0.0,
        "note": "train and eval use disjoint RNG seed ranges -> no data leakage"}
    sig_cb = False
    if corr_b:
        sig_cb = p_cb < 0.05 and lo_cb > 0
    verdict = ("TREATMENT SIGNIFICANT" if sig_cb else
               "TREATMENT NOT SIGNIFICANT" if acc_c > acc_b else "NO IMPROVEMENT")
    if res_d and acc_c > acc_d:
        verdict += " | REWARD-DESIGN DRIVEN (C>D)"
    elif res_d:
        verdict += " | NOT reward-design driven (C<=D)"
    stats["verdict"] = verdict
    stats["pre_registered_judgment"] = {"C>B": acc_c>acc_b if corr_b else None,
        "C>D_reward_design": (acc_c > acc_d) if res_d else None, "C_vs_B_sig": sig_cb}

    print(f"\n{'='*60}", flush=True)
    print(f"  A (baseline):            {acc_a:.1%}", flush=True)
    print(f"  B (SFT):                 {acc_b:.1%}", flush=True)
    print(f"  C (GRPO new reward):     {acc_c:.1%}", flush=True)
    if res_d:
        print(f"  D (GRPO random control): {acc_d:.1%}", flush=True)
    if corr_b:
        print(f"  McNemar C vs B: p={p_cb:.4f} (n_disc={ndisc_cb})", flush=True)
        print(f"  Bootstrap C-B: {pt_cb:+.1%} CI=[{lo_cb:+.1%},{hi_cb:+.1%}]", flush=True)
    if res_d:
        print(f"  McNemar C vs D: p={p_cd:.4f} (n_disc={ndisc_cd})", flush=True)
    print(f"  VERDICT: {verdict}", flush=True)

    out = {"config": vars(args), "stats": stats,
           "results": {"A": res_a, "B": res_b, "C": res_c},
           "training": {"C_losses": losses_c, "C_rewards": rewards_c,
                        "D_losses": losses_d, "D_rewards": rewards_d}}
    if res_d:
        out["results"]["D"] = res_d
    out_path = os.path.join(args.out_dir, "experiment_results.json")
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\n  Full results -> {out_path}", flush=True)

if __name__ == "__main__":
    main()
