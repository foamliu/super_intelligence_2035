#!/usr/bin/env python
"""WaveQA-RL Evaluation Harness (Phase 2 evaluation groundwork).

Evaluates a trained waveform-RL policy on held-out circuits across three
question types (plan Stage-2W step 2):
  - numerical : measure a value, score by relative-error tier
  - multi_choice : identify signal type (digital/analog)
  - open_ended : free-form "what is the period of signal X"

Also provides regression-guard stubs (MMStar/MMBench drop <= 1pp).

Usage (checkpoint, GPU):
  python waveqa_eval.py --ckpt_dir <path> --n_questions 300
Usage (oracle ceiling, CPU):
  python waveqa_eval.py --oracle --n_questions 50

Author: vision wake#612.  License: project-internal.
"""

import sys, os, json, time, tempfile
from typing import Dict, List
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from waveview_gym import (  # noqa: E402
    WaveformGymEnv, generate_circuit, run_ngspice, parse_ngspice_raw,
    _CIRCUIT_GENS,
)
from gen_sft_trajectories import (  # noqa: E402
    _gen_diffpair, oracle_measure, _pick_signal, _fmt_val, SYSTEM_PROMPT,
    MEASURE_TARGETS,
)
if "diffpair" not in _CIRCUIT_GENS:
    _CIRCUIT_GENS["diffpair"] = _gen_diffpair
from grpo_train_wave import (  # noqa: E402
    rollout_episode,
)


def parse_args():
    import argparse
    p = argparse.ArgumentParser(description="WaveQA-RL evaluation")
    p.add_argument('--ckpt_dir', type=str, default=None)
    p.add_argument('--model_path', type=str,
                   default="/nas_train/app.e0031982/datasets/baize-vision/out/wave_sft_stage1w/qwen3vl_2b_text_extracted",
                   help="Base LLM (wake#624: default 2B text backbone, was 4B).")
    p.add_argument('--n_questions', type=int, default=300)
    p.add_argument('--seed', type=int, default=20261112)
    p.add_argument('--oracle', action='store_true',
                   help="Use oracle (perfect) policy -- ceiling reference.")
    p.add_argument('--output', type=str, default=None)
    p.add_argument('--regression_guard', action='store_true')
    return p.parse_args()


def generate_eval_questions(n, seed):
    rng = np.random.default_rng(seed)
    workdir = tempfile.mkdtemp(prefix="waveqa_", dir="/tmp")
    questions, attempts = [], 0
    types = ["numerical", "multi_choice", "open_ended"]
    while len(questions) < n and attempts < n * 5:
        attempts += 1
        ct = str(rng.choice(list(_CIRCUIT_GENS.keys())))
        target = str(rng.choice(MEASURE_TARGETS))
        qtype = str(rng.choice(types))
        ep_wd = os.path.join(workdir, f"q_{len(questions):04d}")
        os.makedirs(ep_wd, exist_ok=True)
        spec = generate_circuit(rng, ep_wd, ct)
        ok, _ = run_ngspice(spec.netlist)
        if not ok or not os.path.exists(spec.raw_path):
            continue
        try:
            raw = parse_ngspice_raw(spec.raw_path)
        except Exception:
            continue
        signal = _pick_signal(spec, target)
        oracle = oracle_measure(raw, signal)
        if qtype in ("numerical", "open_ended"):
            gt_val = oracle.get(target)
            if gt_val is None or gt_val == 0:
                continue
            questions.append({"id": f"q{len(questions):04d}", "type": qtype,
                "circuit": ct, "target": target, "signal": signal,
                "spec": spec, "raw": raw, "gt_value": float(gt_val),
                "oracle": oracle, "ep_wd": ep_wd})
        else:
            questions.append({"id": f"q{len(questions):04d}", "type": qtype,
                "circuit": ct, "target": target, "signal": signal,
                "spec": spec, "raw": raw, "gt_type": oracle.get("signal_type", "analog"),
                "oracle": oracle, "ep_wd": ep_wd})
    return questions


def score_numerical(pred, gt, tier=(0.01, 0.05, 0.10, 0.25)):
    if pred is None:
        return 0.0, None
    rel = abs(pred - gt) / abs(gt)
    score = (1.0 if rel <= tier[0] else 0.7 if rel <= tier[1] else
             0.4 if rel <= tier[2] else 0.1 if rel <= tier[3] else 0.0)
    return score, rel


def run_oracle_policy(q):
    env = WaveformGymEnv(circuit_type=q["circuit"],
                         measure_target=q["target"], workdir=q["ep_wd"])
    env.spec = q["spec"]; env.reset()
    if q["type"] in ("numerical", "open_ended"):
        return q["gt_value"], q["gt_value"]
    return q["gt_type"], q["gt_type"]


def run_model_policy(q, model, tokenizer, device, dtype):
    env = WaveformGymEnv(circuit_type=q["circuit"],
                         measure_target=q["target"], workdir=q["ep_wd"])
    env.spec = q["spec"]
    conv, reward, info = rollout_episode(
        model, tokenizer, env, q["spec"], q["target"], q["signal"],
        device, dtype, max_turns=8, max_new_tokens=48,
        temperature=0.0, seq_len=2048)
    if q["type"] in ("numerical", "open_ended"):
        return info.get("submit_value"), q["gt_value"]
    return info.get("submit_type", ""), q["gt_type"]


def evaluate(args):
    questions = generate_eval_questions(args.n_questions, args.seed)
    print(f"Generated {len(questions)} eval questions "
          f"(seed={args.seed}, oracle={args.oracle})")
    if not questions:
        print("No questions generated (ngspice failures?).")
        return
    by_type = {}
    for q in questions:
        by_type.setdefault(q["type"], []).append(q)
    results = {"numerical": [], "multi_choice": [], "open_ended": []}

    if args.oracle:
        for qt, qs in by_type.items():
            for q in qs:
                pred, gt = run_oracle_policy(q)
                if qt in ("numerical", "open_ended"):
                    score, rel = score_numerical(pred, gt)
                else:
                    score, rel = (1.0 if pred == gt else 0.0), None
                results[qt].append({"id": q["id"], "pred": pred,
                                    "gt": gt, "score": score, "rel_err": rel})
    else:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import PeftModel
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
        llm = AutoModelForCausalLM.from_pretrained(
            args.model_path, torch_dtype=dtype, device_map={'': device},
            trust_remote_code=True)
        if args.ckpt_dir and os.path.exists(
                os.path.join(args.ckpt_dir, "adapter_config.json")):
            llm = PeftModel.from_pretrained(llm, args.ckpt_dir)
        tokenizer = AutoTokenizer.from_pretrained(
            args.model_path, trust_remote_code=True)
        for qt, qs in by_type.items():
            for q in qs:
                pred, gt = run_model_policy(q, llm, tokenizer, device, dtype)
                if qt in ("numerical", "open_ended"):
                    score, rel = score_numerical(pred, gt)
                else:
                    score, rel = (1.0 if pred == gt else 0.0), None
                results[qt].append({"id": q["id"], "pred": pred,
                                    "gt": gt, "score": score, "rel_err": rel})

    summary = {}
    for qt, rs in results.items():
        if not rs:
            continue
        scores = [r["score"] for r in rs]
        summary[qt] = {"n": len(rs), "mean_score": float(np.mean(scores)),
            "pass_rate_le5pct": float(np.mean([s >= 0.7 for s in scores])),
            "pass_rate_le1pct": float(np.mean([s >= 1.0 for s in scores]))}
    summary["overall_n"] = sum(len(rs) for rs in results.values())
    summary["overall_mean"] = float(np.mean(
        [r["score"] for rs in results.values() for r in rs])) if summary["overall_n"] else 0.0
    if args.regression_guard:
        summary["regression_guard"] = {
            "MMStar_threshold_pp": 1.0, "MMBench_threshold_pp": 1.0,
            "status": "stub -- run lm-eval separately on GPU"}

    print(f"\n=== WaveQA-RL Results ({'oracle' if args.oracle else 'model'}) ===")
    for qt, s in summary.items():
        if isinstance(s, dict) and "n" in s:
            print(f"  {qt}: n={s['n']} mean={s['mean_score']:.3f} "
                  f"<=5%={s['pass_rate_le5pct']:.1%} <=1%={s['pass_rate_le1pct']:.1%}")
    print(f"  Overall: n={summary['overall_n']} mean={summary['overall_mean']:.3f}")
    if args.output:
        with open(args.output, 'w') as f:
            json.dump({"summary": summary, "results": results}, f, indent=2, default=str)
        print(f"  Saved to {args.output}")
    return summary


if __name__ == '__main__':
    evaluate(parse_args())

