#!/usr/bin/env python3
"""v3_quick_eval.py - Quick eval of EXISTING v2 GRPO checkpoints on 100 NEW
period-only questions. No new training needed - just scale up eval for power.

Uses v2's saved checkpoints:
  B (SFT):       wave_sft_stage1w/step3000
  C (GRPO treat): cpu_rl_v2/grpo_treatment/step15
  D (GRPO ctrl):  cpu_rl_v2/grpo_control/step15

Author: vision wake#854. License: project-internal.
"""
from __future__ import annotations
import sys, os, json, time, argparse, tempfile
import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cpu_rl_v3_experiment import build_eval_set_period, EVAL_SEED_BASE_V3
from cpu_rl_v2_experiment import (
    build_model, evaluate_condition, _check_correct,
    ContinuousRewardEnv, rollout_episode, mcnemar_test, bootstrap_ci_delta,
)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--model_path', type=str,
        default="/nas_train/app.e0031982/datasets/baize-vision/out/wave_sft_stage1w/qwen3vl_2b_text_extracted")
    p.add_argument('--sft_ckpt', type=str,
        default="/nas_train/app.e0031982/datasets/baize-vision/out/wave_sft_stage1w/step3000")
    p.add_argument('--grpo_treat_ckpt', type=str,
        default="/nas_train/app.e0031982/datasets/baize-vision/out/cpu_rl_v2/grpo_treatment/step15")
    p.add_argument('--grpo_ctrl_ckpt', type=str,
        default="/nas_train/app.e0031982/datasets/baize-vision/out/cpu_rl_v2/grpo_control/step15")
    p.add_argument('--out_dir', type=str,
        default="/nas_train/app.e0031982/datasets/baize-vision/out/cpu_rl_v3_quickeval")
    p.add_argument('--n_eval', type=int, default=100)
    p.add_argument('--max_turns', type=int, default=4)
    p.add_argument('--max_new_tokens', type=int, default=20)
    args = p.parse_args()

    os.environ.setdefault("OMP_NUM_THREADS", "48")
    torch.set_num_threads(48)
    device = torch.device('cpu')
    dtype = torch.float32
    os.makedirs(args.out_dir, exist_ok=True)

    print("=" * 60, flush=True)
    print(f"[v3 Quick Eval] {args.n_eval} period-only questions on EXISTING checkpoints", flush=True)

    eval_path = os.path.join(args.out_dir, "eval_questions.json")
    if not os.path.exists(eval_path):
        print(f"  Building eval set (n={args.n_eval})...", flush=True)
        questions = build_eval_set_period(n_questions=args.n_eval)
        qs_save = [{k: v for k, v in q.items() if k != "spec"} for q in questions]
        with open(eval_path, 'w') as f:
            json.dump(qs_save, f, indent=2, default=str)
    else:
        print(f"  Loading existing eval set...", flush=True)
        questions = build_eval_set_period(n_questions=args.n_eval)
    print(f"  {len(questions)} questions ready", flush=True)

    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    results = {}
    # Eval B (SFT)
    print("\n[Phase B] SFT only", flush=True)
    model_b = build_model(args.model_path, device, dtype, 16, 32, args.sft_ckpt)
    model_b.eval()
    t0 = time.time()
    res_b = evaluate_condition(model_b, tokenizer, questions, device, dtype, "B-sft",
                               max_turns=args.max_turns, max_new_tokens=args.max_new_tokens)
    acc_b = sum(r["correct"] for r in res_b) / len(res_b)
    print(f"  B (SFT): {acc_b:.1%} ({time.time()-t0:.0f}s)", flush=True)
    results["B"] = {"accuracy": acc_b, "results": res_b}
    del model_b

    # Eval C (GRPO treatment)
    print("\n[Phase C] GRPO treatment (v2 step15)", flush=True)
    model_c = build_model(args.model_path, device, dtype, 16, 32, args.grpo_treat_ckpt)
    model_c.eval()
    t0 = time.time()
    res_c = evaluate_condition(model_c, tokenizer, questions, device, dtype, "C-grpo",
                               max_turns=args.max_turns, max_new_tokens=args.max_new_tokens)
    acc_c = sum(r["correct"] for r in res_c) / len(res_c)
    print(f"  C (GRPO treat): {acc_c:.1%} ({time.time()-t0:.0f}s)", flush=True)
    results["C"] = {"accuracy": acc_c, "results": res_c}
    del model_c

    # Eval D (GRPO control)
    print("\n[Phase D] GRPO control (v2 step15)", flush=True)
    model_d = build_model(args.model_path, device, dtype, 16, 32, args.grpo_ctrl_ckpt)
    model_d.eval()
    t0 = time.time()
    res_d = evaluate_condition(model_d, tokenizer, questions, device, dtype, "D-ctrl",
                               max_turns=args.max_turns, max_new_tokens=args.max_new_tokens)
    acc_d = sum(r["correct"] for r in res_d) / len(res_d)
    print(f"  D (GRPO ctrl): {acc_d:.1%} ({time.time()-t0:.0f}s)", flush=True)
    results["D"] = {"accuracy": acc_d, "results": res_d}
    del model_d

    # Stats
    corr_b = [r["correct"] for r in res_b]
    corr_c = [r["correct"] for r in res_c]
    corr_d = [r["correct"] for r in res_d]
    stat_cb, p_cb, ndisc_cb = mcnemar_test(corr_b, corr_c)
    pt_cb, lo_cb, hi_cb = bootstrap_ci_delta(corr_b, corr_c)
    stat_cd, p_cd, ndisc_cd = mcnemar_test(corr_d, corr_c)
    pt_cd, lo_cd, hi_cd = bootstrap_ci_delta(corr_d, corr_c)
    stat_bd, p_bd, ndisc_bd = mcnemar_test(corr_b, corr_d)

    sig_cb = p_cb < 0.05 and lo_cb > 0
    print(f"\n{'='*60}", flush=True)
    print(f"  B (SFT):              {acc_b:.1%} ({sum(corr_b)}/{len(corr_b)})", flush=True)
    print(f"  C (GRPO treatment):   {acc_c:.1%} ({sum(corr_c)}/{len(corr_c)})", flush=True)
    print(f"  D (GRPO control):     {acc_d:.1%} ({sum(corr_d)}/{len(corr_d)})", flush=True)
    print(f"  McNemar C vs B: stat={stat_cb}, p={p_cb:.4f} (n_disc={ndisc_cb})", flush=True)
    print(f"  Bootstrap C-B: {pt_cb:+.1%} CI=[{lo_cb:+.1%},{hi_cb:+.1%}]", flush=True)
    print(f"  McNemar C vs D: stat={stat_cd}, p={p_cd:.4f} (n_disc={ndisc_cd})", flush=True)
    print(f"  Bootstrap C-D: {pt_cd:+.1%} CI=[{lo_cd:+.1%},{hi_cd:+.1%}]", flush=True)
    print(f"  McNemar B vs D: stat={stat_bd}, p={p_bd:.4f} (n_disc={ndisc_bd})", flush=True)
    verdict = "TREATMENT SIGNIFICANT" if sig_cb else (
        "TREATMENT NOT SIGNIFICANT" if acc_c > acc_b else "NO IMPROVEMENT")
    if acc_c > acc_d:
        verdict += " | REWARD-DESIGN DRIVEN (C>D)"
    print(f"  VERDICT: {verdict}", flush=True)

    out = {"config": vars(args),
           "stats": {"accuracy": {"B_sft": acc_b, "C_grpo_treatment": acc_c, "D_grpo_control": acc_d},
                     "mcnemar_C_vs_B": {"stat": stat_cb, "p": p_cb, "n_discordant": ndisc_cb},
                     "bootstrap_C_vs_B": {"point_delta": pt_cb, "ci_lo": lo_cb, "ci_hi": hi_cb},
                     "mcnemar_C_vs_D": {"stat": stat_cd, "p": p_cd, "n_discordant": ndisc_cd},
                     "bootstrap_C_vs_D": {"point_delta": pt_cd, "ci_lo": lo_cd, "ci_hi": hi_cd},
                     "mcnemar_B_vs_D": {"stat": stat_bd, "p": p_bd, "n_discordant": ndisc_bd},
                     "verdict": verdict,
                     "pre_registered_judgment": {"C>B": acc_c > acc_b, "C>D": acc_c > acc_d, "C_vs_B_sig": sig_cb}},
           "results": results}
    out_path = os.path.join(args.out_dir, "quick_eval_results.json")
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\n  Results -> {out_path}", flush=True)

if __name__ == "__main__":
    main()
