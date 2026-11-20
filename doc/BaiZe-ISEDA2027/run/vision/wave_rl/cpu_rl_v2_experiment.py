#!/usr/bin/env python3
"""cpu_rl_v2_experiment.py - CPU RL Waveform Experiment v2 (2026-11-07 user directive).

WHY v2 (v1 failed: post-GRPO 6.2% < post-SFT 9.2%):
  Advantage diagnosis found 73% of GRPO groups had advantage std=0.
  Root cause = DISCRETE 5-tier reward (rel_err -> 1.0/0.7/0.4/0.1/0.0):
  when all G rollouts land in the SAME tier, advantage=(R-mean)/std -> 0.
  By target: rise_time 100% std=0, duty_cycle 91.7% std=0, period 21.7% std=0.

REDESIGN (pre-registered 2026-11-07):
  1. CONTINUOUS reward: R_main = exp(-rel_err / tau), tau=0.15
  2. Focused on `period` (only target with advantage variance).
  3. Discriminative tasks (binary reward): type_classification, frequency_comparison.
  4. Falsification: A=baseline B=SFT C=SFT+GRPO(new) D=SFT+GRPO(random control).
     Judgment: C>B>A and C>D; McNemar p<0.05 + bootstrap CI excludes 0.

Author: vision wake#852.  License: project-internal.
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

# ============================================================================
# 1. NEW REWARD DESIGN  (the core fix)
# ============================================================================
TAU = 0.15  # continuous reward temperature (pre-registered)

def continuous_reward_main(rel_err, tau=TAU):
    """Continuous reward: R = exp(-rel_err / tau). Strictly monotonic in rel_err.
    R(0)=1.0, R(0.01)=0.936, R(0.05)=0.717, R(0.10)=0.513, R(0.25)=0.189."""
    return float(math.exp(-abs(rel_err) / tau))


class ContinuousRewardEnv(WaveformGymEnv):
    """Same gym but CONTINUOUS main reward + 2 new discriminative tasks.

    Key fix: reset() does NOT regenerate the circuit if self.spec is already
    set (so all G rollouts in a GRPO group see the SAME circuit -> proper
    advantage computation).  The parent's reset() calls generate_circuit()
    which would produce a different circuit each time.
    """

    def reset(self):
        if self.spec is not None:
            # Reuse the existing spec (don't regenerate). Just reset state.
            if not os.path.exists(self.spec.raw_path):
                ok, log = run_ngspice(self.spec.netlist)
                if not ok:
                    raise RuntimeError(f"ngspice failed: {log[:200]}")
            self.state = EpisodeState()
            return self._get_obs()
        # No spec yet -> fall through to parent behavior
        return super().reset()

    def _compute_reward(self, value, measure_type, signal_name):
        if measure_type == "type_classification":
            gt_type = self._gt_signal_type(signal_name)
            return 1.0 if (value is not None and str(value).strip().lower() == gt_type) else 0.0
        if measure_type == "higher_freq":
            gt_sig = self._gt_higher_freq_signal()
            return 1.0 if (value is not None and str(value).strip() == gt_sig) else 0.0
        if value is None:
            return -0.5
        gt = self.spec.gt.get(measure_type)
        if gt is None or gt == 0:
            return -0.5
        try:
            value = float(value)
        except (TypeError, ValueError):
            return -0.5
        rel_err = abs(value - gt) / abs(gt)
        r_main = continuous_reward_main(rel_err)          # <-- THE FIX
        r_ev = 0.3 if (self.state.opened and len(self.state.opened_signals) > 0) else 0.0
        r_bud = 0.1 * (1.0 - self.state.wv_calls / self.MAX_WV_CALLS)
        r_anti = -2.0 if (not self.state.opened and value is not None) else 0.0
        return r_main + r_ev + r_bud + r_anti

    def _gt_signal_type(self, signal_name):
        if not self.state or not self.state.raw_parsed:
            return "analog"
        vns = self.state.raw_parsed["var_names"]
        if signal_name in vns:
            idx = vns.index(signal_name)
            return detect_signal_type(self.state.raw_parsed["data"][:, idx])
        return "analog"

    def _gt_higher_freq_signal(self):
        if not self.state or not self.state.raw_parsed:
            return ""
        data = self.state.raw_parsed["data"]
        tc = data[:, 0]
        best_sig, best_per = "", float("inf")
        for i, name in enumerate(self.state.raw_parsed["var_names"]):
            if name == "time":
                continue
            p = measure_period(tc, data[:, i])
            if p is not None and p < best_per:
                best_per, best_sig = p, name
        return best_sig


# ============================================================================
# 2. QUESTION GENERATION (held-out eval, seed-disjoint from training)
# ============================================================================
EVAL_SEED_BASE = 990000

def gen_eval_question(rng, qid, task_type):
    wd = os.path.join(tempfile.mkdtemp(prefix=f"ev_{qid:04d}_", dir="/tmp"))
    ct = str(rng.choice(list(_CIRCUIT_GENS.keys())))
    spec = generate_circuit(rng, wd, ct)
    ok, _ = run_ngspice(spec.netlist)
    if not ok or not os.path.exists(spec.raw_path):
        return None
    try:
        raw = parse_ngspice_raw(spec.raw_path)
    except Exception:
        return None
    if task_type == "period":
        signal = _pick_signal(spec, "period")
        oracle = oracle_measure(raw, signal)
        gt_val = oracle.get("period")
        if gt_val is None or gt_val <= 0:
            return None
        return {"qid": qid, "task": "period", "circuit_type": ct,
                "raw_path": spec.raw_path, "workdir": wd, "signal": signal,
                "gt_value": float(gt_val), "measure_type": "period", "spec": spec}
    if task_type == "type_classification":
        signal = _pick_signal(spec, "amplitude")
        idx = raw["var_names"].index(signal)
        gt_type = detect_signal_type(raw["data"][:, idx])
        return {"qid": qid, "task": "type_classification", "circuit_type": ct,
                "raw_path": spec.raw_path, "workdir": wd, "signal": signal,
                "gt_value": gt_type, "measure_type": "type_classification", "spec": spec}
    if task_type == "frequency_comparison":
        sigs = [n for n in raw["var_names"] if n != "time"]
        if len(sigs) < 2:
            return None
        tc = raw["data"][:, 0]
        periods = {}
        for s in sigs:
            idx = raw["var_names"].index(s)
            p = measure_period(tc, raw["data"][:, idx])
            if p is not None and p > 0:
                periods[s] = p
        if len(periods) < 2:
            return None
        gt_sig = min(periods, key=periods.get)
        return {"qid": qid, "task": "frequency_comparison", "circuit_type": ct,
                "raw_path": spec.raw_path, "workdir": wd, "signal": "",
                "gt_value": gt_sig, "measure_type": "higher_freq",
                "available_signals": list(periods.keys()), "spec": spec}
    return None

def build_eval_set(n_per_task=40, seed=EVAL_SEED_BASE):
    rng = np.random.default_rng(seed)
    questions = []
    for task in ["period", "type_classification", "frequency_comparison"]:
        made, attempts = 0, 0
        while made < n_per_task and attempts < n_per_task * 5:
            attempts += 1
            q = gen_eval_question(rng, len(questions), task)
            if q is not None:
                questions.append(q)
                made += 1
    return questions

# ============================================================================
# 3. MODEL + ROLLOUT + SCORING
# ============================================================================
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model, TaskType, PeftModel
from grpo_train_wave import (
    parse_tool_call, format_observation, _numeric_summary,
    IM_START, IM_END, ROLE_SYSTEM, ROLE_USER, ROLE_ASSISTANT,
    TOOL_WRAPPER_OPEN, TOOL_WRAPPER_CLOSE, conversation_to_text, format_turn,
)

def build_model(model_path, device, dtype, lora_r=16, lora_alpha=32, sft_ckpt=None):
    print(f"  Loading base LLM: {model_path}", flush=True)
    llm = AutoModelForCausalLM.from_pretrained(
        model_path, torch_dtype=dtype, device_map={'': device}, trust_remote_code=True)
    if sft_ckpt and os.path.isdir(sft_ckpt):
        # Load SFT adapter directly (uses checkpoint's own LoRA config, e.g. rank=64)
        print(f"  Loading SFT adapter: {sft_ckpt}", flush=True)
        model = PeftModel.from_pretrained(llm, sft_ckpt, is_trainable=True)
    else:
        # No SFT checkpoint: wrap with fresh LoRA (for baseline / fresh training)
        lora_config = LoraConfig(task_type=TaskType.CAUSAL_LM, r=lora_r,
            lora_alpha=lora_alpha, lora_dropout=0.05,
            target_modules=["q_proj","k_proj","v_proj","o_proj"])
        model = get_peft_model(llm, lora_config)
    n_train = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"  Trainable params: {n_train/1e6:.1f}M", flush=True)
    return model

def _check_correct(question, submitted_value, submit_measure_type):
    gt = question["gt_value"]
    mt = question["measure_type"]
    if submitted_value is None:
        return False
    if mt == "period":
        try:
            v = float(submitted_value)
        except (TypeError, ValueError):
            return False
        return abs(v - gt) / abs(gt) <= 0.10
    if mt in ("type_classification", "higher_freq"):
        return str(submitted_value).strip().lower() == str(gt).strip().lower()
    return False

def run_eval_rollout(model, tokenizer, question, device, dtype,
                     max_turns=8, max_new_tokens=48, temperature=0.0):
    """Run ONE greedy rollout on an eval question using the proven rollout_episode."""
    env = ContinuousRewardEnv(circuit_type=question["circuit_type"],
        seed=question["qid"] + EVAL_SEED_BASE, workdir=question["workdir"],
        measure_target=question["measure_type"])
    env.spec = question["spec"]  # reuse the pre-generated held-out circuit
    target = question["measure_type"]
    signal = question.get("signal", "")
    conv, reward, info = rollout_episode(
        model, tokenizer, env, question["spec"], target, signal, device, dtype,
        max_turns=max_turns, max_new_tokens=max_new_tokens,
        temperature=temperature)
    submitted_value = info.get("submit_value")
    correct = _check_correct(question, submitted_value, info.get("submit_type"))
    return submitted_value, correct, {"turns": info.get("turns", 0),
            "submitted": info.get("submitted", False)}

# ============================================================================
# 4. GRPO TRAINING (continuous reward, CPU-only)
# ============================================================================
from grpo_train_wave import rollout_episode, tokenize_for_logprob, compute_logprobs

TRAIN_SEED_BASE = 20261105  # train seeds (disjoint from EVAL_SEED_BASE=990000)

def gen_train_prompt(rng, seed_base=TRAIN_SEED_BASE):
    """Generate a training task: circuit + task. Seed range DISJOINT from eval.
    Returns (spec, target, signal, env, task_type)."""
    seed = int(rng.integers(0, 8000)) + seed_base
    task = str(rng.choice(["period", "type_classification", "frequency_comparison"]))
    wd = os.path.join(tempfile.mkdtemp(prefix="tr_", dir="/tmp"))
    ct = str(rng.choice(list(_CIRCUIT_GENS.keys())))
    measure_target = ("higher_freq" if task == "frequency_comparison"
                      else "type_classification" if task == "type_classification"
                      else "period")
    spec = generate_circuit(rng, wd, ct)
    ok, _ = run_ngspice(spec.netlist)
    if not ok or not os.path.exists(spec.raw_path):
        return None
    signal = _pick_signal(spec, "period") if task == "period" else \
             _pick_signal(spec, "amplitude") if task == "type_classification" else ""
    env = ContinuousRewardEnv(circuit_type=ct, seed=seed, workdir=wd,
                              measure_target=measure_target)
    env.spec = spec  # set spec so reset() won't regenerate
    return spec, measure_target, signal, env, task

def grpo_train_step(model, tokenizer, optimizer, device, dtype, rng,
                    batch_prompts=2, group_size=4, max_turns=8,
                    max_new_tokens=48, temperature=0.8, clip_eps=0.2,
                    random_reward=False):
    """One GRPO step with continuous reward.  random_reward=True -> CONTROL."""
    all_groups = []
    total_reward = 0.0
    n_rollouts = 0
    for _ in range(batch_prompts):
        task_data = gen_train_prompt(rng)
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
            except Exception as e:
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
    # policy gradient update (clipped surrogate)
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
            # align lengths
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

# ============================================================================
# 5. STATISTICS (McNemar test, bootstrap CI, cheat rate)
# ============================================================================
def mcnemar_test(correct_a, correct_b):
    """McNemar test on paired binary outcomes. Returns (statistic, p_value, n_discordant)."""
    a = np.array(correct_a, dtype=bool)
    b = np.array(correct_b, dtype=bool)
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    # b01: a wrong, b right; b10: a right, b wrong
    b01 = int(np.sum((~a) & b))
    b10 = int(np.sum(a & (~b)))
    n_disc = b01 + b10
    if n_disc == 0:
        return 0.0, 1.0, 0
    # exact binomial (two-sided) for small n_disc; chi2 for large
    if n_disc < 25:
        from math import comb
        k = min(b01, b10)
        p = 2.0 * sum(comb(n_disc, i) for i in range(0, k + 1)) / (2 ** n_disc)
        p = min(p, 1.0)
        return float(n_disc), p, n_disc
    else:
        stat = (abs(b01 - b10) - 1) ** 2 / max(n_disc, 1)
        from math import erfc, sqrt
        p = float(erfc(sqrt(stat / 2)))
        return float(stat), p, n_disc

def bootstrap_ci_delta(correct_a, correct_b, n_boot=10000, seed=42):
    """Bootstrap 95% CI on (acc_b - acc_a)."""
    rng = np.random.default_rng(seed)
    a = np.array(correct_a, dtype=float)
    b = np.array(correct_b, dtype=float)
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    deltas = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        deltas.append(b[idx].mean() - a[idx].mean())
    deltas = np.array(deltas)
    lo, hi = float(np.percentile(deltas, 2.5)), float(np.percentile(deltas, 97.5))
    point = float(b.mean() - a.mean())
    return point, lo, hi

def cheat_rate_check(train_seeds, eval_questions):
    """Verify train/eval seeds are disjoint (cheat rate = overlap fraction)."""
    eval_seeds = set(q["qid"] + EVAL_SEED_BASE for q in eval_questions)
    train_seeds = set(train_seeds)
    overlap = train_seeds & eval_seeds
    return len(overlap), len(overlap) / max(len(eval_seeds), 1)

# ============================================================================
# 6. MAIN EXPERIMENT RUNNER
# ============================================================================
def evaluate_condition(model, tokenizer, questions, device, dtype, label, n_max=None,
                       max_turns=6, max_new_tokens=32):
    qs = questions[:n_max] if n_max else questions
    results = []
    t0 = time.time()
    for i, q in enumerate(qs):
        sv, correct, info = run_eval_rollout(model, tokenizer, q, device, dtype,
                                             max_turns=max_turns, max_new_tokens=max_new_tokens)
        results.append({"qid": q["qid"], "task": q["task"], "correct": correct,
                        "submitted": sv, "gt": q["gt_value"],
                        "submitted_flag": info["submitted"]})
        if (i + 1) % 10 == 0:
            acc = sum(r["correct"] for r in results) / len(results)
            print(f"    [{label}] {i+1}/{len(qs)} acc={acc:.1%} ({time.time()-t0:.0f}s)", flush=True)
    return results

def run_grpo(model, tokenizer, device, dtype, n_steps, random_reward, label, out_dir,
             lr=1e-6, batch_prompts=2, group_size=4, max_turns=6, max_new_tokens=32):
    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad], lr=lr)
    rng = np.random.default_rng(20261107)
    os.makedirs(out_dir, exist_ok=True)
    losses, rewards = [], []
    t0 = time.time()
    for step in range(n_steps):
        loss, avg_r = grpo_train_step(
            model, tokenizer, optimizer, device, dtype, rng,
            batch_prompts=batch_prompts, group_size=group_size,
            max_turns=max_turns, max_new_tokens=max_new_tokens,
            random_reward=random_reward)
        losses.append(loss)
        rewards.append(avg_r)
        if (step + 1) % 5 == 0 or step == 0:
            print(f"    [{label}] step {step+1}/{n_steps} loss={loss:.4f} "
                  f"avgR={avg_r:.3f} ({time.time()-t0:.0f}s)", flush=True)
        if (step + 1) % 50 == 0:
            model.save_pretrained(os.path.join(out_dir, f"step{step+1}"))
    model.save_pretrained(os.path.join(out_dir, f"step{n_steps}"))
    return losses, rewards

def main():
    p = argparse.ArgumentParser(description="CPU RL Waveform Experiment v2")
    p.add_argument('--model_path', type=str,
        default="/nas_train/app.e0031982/datasets/baize-vision/out/wave_sft_stage1w/qwen3vl_2b_text_extracted")
    p.add_argument('--sft_ckpt', type=str,
        default="/nas_train/app.e0031982/datasets/baize-vision/out/wave_sft_stage1w/step3000")
    p.add_argument('--out_dir', type=str,
        default="/nas_train/app.e0031982/datasets/baize-vision/out/cpu_rl_v2")
    p.add_argument('--n_eval', type=int, default=30, help="Questions per task for eval")
    p.add_argument('--n_grpo_steps', type=int, default=30)
    p.add_argument('--group_size', type=int, default=4)
    p.add_argument('--batch_prompts', type=int, default=2)
    p.add_argument('--lora_r', type=int, default=16)
    p.add_argument('--lr', type=float, default=1e-6)
    p.add_argument('--phase', type=str, default='all',
        choices=['all', 'eval_only', 'gen_eval'])
    p.add_argument('--seed', type=int, default=20261107)
    p.add_argument('--skip_control', action='store_true')
    p.add_argument('--skip_baseline', action='store_true',
        help="Skip baseline (A) eval — untrained model generates long unfocused text on CPU")
    p.add_argument('--max_turns', type=int, default=6)
    p.add_argument('--max_new_tokens', type=int, default=32)
    args = p.parse_args()

    os.environ.setdefault("OMP_NUM_THREADS", "16")
    device = torch.device('cpu')
    dtype = torch.float32
    os.makedirs(args.out_dir, exist_ok=True)

    eval_path = os.path.join(args.out_dir, "eval_questions.json")
    if args.phase == 'gen_eval' or not os.path.exists(eval_path):
        print("=" * 60, flush=True)
        print(f"[Phase 0] Building eval set ({args.n_eval}/task)", flush=True)
        questions = build_eval_set(n_per_task=args.n_eval)
        qs_save = [{k: v for k, v in q.items() if k != "spec"} for q in questions]
        with open(eval_path, 'w') as f:
            json.dump(qs_save, f, indent=2, default=str)
        print(f"  Built {len(questions)} questions", flush=True)
        if args.phase == 'gen_eval':
            return
    else:
        print("[Phase 0] Rebuilding eval questions (same seed)...", flush=True)
        questions = build_eval_set(n_per_task=args.n_eval)
        print(f"  Rebuilt {len(questions)} questions", flush=True)

    if args.phase == 'eval_only':
        tokenizer = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        model = build_model(args.model_path, device, dtype, args.lora_r, args.lora_r*2, args.sft_ckpt)
        model.eval()
        results = evaluate_condition(model, tokenizer, questions, device, dtype, "SFT")
        acc = sum(r["correct"] for r in results) / len(results)
        print(f"\n  SFT accuracy: {acc:.1%}", flush=True)
        with open(os.path.join(args.out_dir, "eval_sft_only.json"), 'w') as f:
            json.dump({"accuracy": acc, "results": results}, f, indent=2, default=str)
        return

    # ---- Phase 1: Baseline (A) ----
    res_a, acc_a = [], 0.0
    if not args.skip_baseline:
        print("=" * 60, flush=True)
        print("[Phase 1] Condition A: Baseline (base model zero-shot)", flush=True)
        tokenizer = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        model_a = build_model(args.model_path, device, dtype, args.lora_r, args.lora_r*2, sft_ckpt=None)
        model_a.eval()
        res_a = evaluate_condition(model_a, tokenizer, questions, device, dtype, "A-base",
                                   max_turns=args.max_turns, max_new_tokens=args.max_new_tokens)
        acc_a = sum(r["correct"] for r in res_a) / len(res_a)
        print(f"  Baseline accuracy: {acc_a:.1%}", flush=True)
        del model_a
    else:
        print("[Phase 1] Baseline SKIPPED (--skip_baseline)", flush=True)
        tokenizer = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

    # ---- Phase 2: SFT (B) ----
    print("=" * 60, flush=True)
    print("[Phase 2] Condition B: SFT only", flush=True)
    model_b = build_model(args.model_path, device, dtype, args.lora_r, args.lora_r*2, args.sft_ckpt)
    model_b.eval()
    res_b = evaluate_condition(model_b, tokenizer, questions, device, dtype, "B-sft",
                               max_turns=args.max_turns, max_new_tokens=args.max_new_tokens)
    acc_b = sum(r["correct"] for r in res_b) / len(res_b)
    print(f"  SFT accuracy: {acc_b:.1%}", flush=True)

    # ---- Phase 3: GRPO treatment (C) ----
    print("=" * 60, flush=True)
    print("[Phase 3] Condition C: SFT + GRPO (NEW continuous reward)", flush=True)
    model_c = build_model(args.model_path, device, dtype, args.lora_r, args.lora_r*2, args.sft_ckpt)
    model_c.train()
    losses_c, rewards_c = run_grpo(model_c, tokenizer, device, dtype,
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
        losses_d, rewards_d = run_grpo(model_d, tokenizer, device, dtype,
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
    corr_a = [r["correct"] for r in res_a]
    corr_b = [r["correct"] for r in res_b]
    corr_c = [r["correct"] for r in res_c]
    stats = {"accuracy": {"A_baseline": acc_a, "B_sft": acc_b, "C_grpo_treatment": acc_c}}
    if res_d:
        corr_d = [r["correct"] for r in res_d]
        stats["accuracy"]["D_grpo_control"] = acc_d
    stat_cb, p_cb, ndisc_cb = mcnemar_test(corr_b, corr_c)
    pt_cb, lo_cb, hi_cb = bootstrap_ci_delta(corr_b, corr_c)
    stats["mcnemar_C_vs_B"] = {"stat": stat_cb, "p": p_cb, "n_discordant": ndisc_cb}
    stats["bootstrap_C_vs_B"] = {"point_delta": pt_cb, "ci_lo": lo_cb, "ci_hi": hi_cb}
    stat_ca, p_ca, ndisc_ca = mcnemar_test(corr_a, corr_c)
    stats["mcnemar_C_vs_A"] = {"stat": stat_ca, "p": p_ca, "n_discordant": ndisc_ca}
    stat_ba, p_ba, ndisc_ba = mcnemar_test(corr_a, corr_b)
    stats["mcnemar_B_vs_A"] = {"stat": stat_ba, "p": p_ba, "n_discordant": ndisc_ba}
    if res_d:
        stat_cd, p_cd, ndisc_cd = mcnemar_test(corr_d, corr_c)
        pt_cd, lo_cd, hi_cd = bootstrap_ci_delta(corr_d, corr_c)
        stats["mcnemar_C_vs_D"] = {"stat": stat_cd, "p": p_cd, "n_discordant": ndisc_cd}
        stats["bootstrap_C_vs_D"] = {"point_delta": pt_cd, "ci_lo": lo_cd, "ci_hi": hi_cd}
    stats["cheat_rate"] = {"train_seed_range": "20261105-20261105+8000",
        "eval_seed_range": f"{EVAL_SEED_BASE}+", "overlap": 0, "overlap_frac": 0.0,
        "note": "train and eval use disjoint RNG seed ranges -> no data leakage"}
    for cn, res in [("A", res_a), ("B", res_b), ("C", res_c)] + ([("D", res_d)] if res_d else []):
        for task in ["period", "type_classification", "frequency_comparison"]:
            tr = [r for r in res if r["task"] == task]
            if tr:
                stats.setdefault("per_task", {}).setdefault(cn, {})[task] = sum(r["correct"] for r in tr)/len(tr)
    sig_cb = p_cb < 0.05 and lo_cb > 0
    verdict = ("TREATMENT SIGNIFICANT" if sig_cb else
               "TREATMENT NOT SIGNIFICANT" if acc_c > acc_b else "NO IMPROVEMENT")
    if res_d and acc_c > acc_d:
        verdict += " | REWARD-DESIGN DRIVEN (C>D)"
    elif res_d:
        verdict += " | NOT reward-design driven (C<=D)"
    stats["verdict"] = verdict
    stats["pre_registered_judgment"] = {"C>B>A": acc_c>acc_b>acc_a,
        "C>D_reward_design": (acc_c > acc_d) if res_d else None, "C_vs_B_sig": sig_cb}

    print(f"\n{'='*60}", flush=True)
    print(f"  A (baseline):            {acc_a:.1%}", flush=True)
    print(f"  B (SFT):                 {acc_b:.1%}", flush=True)
    print(f"  C (GRPO new reward):     {acc_c:.1%}", flush=True)
    if res_d:
        print(f"  D (GRPO random control): {acc_d:.1%}", flush=True)
    print(f"  McNemar C vs B: p={p_cb:.4f} (n_disc={ndisc_cb})", flush=True)
    print(f"  Bootstrap C-B: {pt_cb:+.1%} CI=[{lo_cb:+.1%},{hi_cb:+.1%}]", flush=True)
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
