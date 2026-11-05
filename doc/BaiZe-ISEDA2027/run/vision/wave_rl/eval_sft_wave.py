#!/usr/bin/env python
"""eval_sft_wave.py — Standalone evaluation for Stage-1W SFT checkpoints.

Loads a LoRA-adapted model and evaluates on a held-out trajectory set,
reporting the pre-registered acceptance criteria:
  - Format correctness  >= 90%
  - Submit success rate  >= 70%

Also measures numerical accuracy (relative error of submitted values vs GT)
for additional insight beyond the binary pass/fail criteria.

Usage:
  CUDA_VISIBLE_DEVICES=0 python eval_sft_wave.py \\
      --model_path /path/to/Qwen3-4B-Instruct-2507 \\
      --adapter_path /path/to/wave_sft_stage1w/step2000 \\
      --eval_file /path/to/sft_holdout_500.jsonl \\
      --output /path/to/eval_results.json

Author: vision agent.  License: project-internal.
"""

import argparse, json, os, re, sys, time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# Reuse formatting from sft_train_wave.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sft_train_wave import (
    IM_START, IM_END, ROLE_USER, ROLE_ASSISTANT,
    TOOL_WRAPPER_OPEN, TOOL_WRAPPER_CLOSE,
    format_turn, conversation_to_text,
)

VALID_TOOL_PATTERNS = ['open(', 'get_signal(', 'get_values(',
                       'dump_hier(', 'submit(']


def parse_args():
    p = argparse.ArgumentParser(
        description="Standalone evaluation for Stage-1W SFT wave checkpoints")
    p.add_argument('--model_path', type=str, required=True,
                   help="Base LLM path (e.g. Qwen3-4B-Instruct-2507)")
    p.add_argument('--adapter_path', type=str, default=None,
                   help="LoRA adapter directory (if None, evaluate base model)")
    p.add_argument('--eval_file', type=str, required=True,
                   help="Held-out JSONL trajectory file")
    p.add_argument('--output', type=str, default=None,
                   help="Output JSON results file")
    p.add_argument('--device', type=str, default='cuda',
                   help="Device: 'cuda' or 'cpu'")
    p.add_argument('--max_eval', type=int, default=200,
                   help="Max number of trajectories to evaluate")
    p.add_argument('--max_new_tokens', type=int, default=256,
                   help="Max new tokens for generation")
    p.add_argument('--seq_len', type=int, default=2048,
                   help="Max sequence length for tokenization")
    p.add_argument('--target_format', type=float, default=0.90,
                   help="Pre-registered target for format correctness")
    p.add_argument('--target_submit', type=float, default=0.70,
                   help="Pre-registered target for submit success rate")
    p.add_argument('--verbose', action='store_true',
                   help="Print per-sample results")
    return p.parse_args()


def load_model(args):
    """Load base LLM + optional LoRA adapter."""
    device = torch.device(args.device if torch.cuda.is_available() or
                          args.device == 'cpu' else 'cuda')
    dtype = torch.bfloat16 if device.type == 'cuda' else torch.float32
    print(f"Loading base model: {args.model_path}", flush=True)
    llm = AutoModelForCausalLM.from_pretrained(
        args.model_path, torch_dtype=dtype,
        device_map={'': device} if device.type == 'cuda' else None,
        trust_remote_code=True)
    tokenizer = AutoTokenizer.from_pretrained(
        args.model_path, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    if args.adapter_path and os.path.isdir(args.adapter_path):
        print(f"Loading LoRA adapter: {args.adapter_path}", flush=True)
        llm = PeftModel.from_pretrained(llm, args.adapter_path)
        llm = llm.merge_and_unload()
        print("  Adapter merged.", flush=True)
    llm.eval()
    return llm, tokenizer, device, dtype


def load_eval_data(eval_file, max_eval):
    """Load held-out trajectories from JSONL."""
    samples = []
    with open(eval_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                traj = json.loads(line)
                if len(traj.get('conversation', [])) < 2:
                    continue
                samples.append(traj)
                if len(samples) >= max_eval:
                    break
            except json.JSONDecodeError:
                continue
    print(f"Loaded {len(samples)} held-out trajectories", flush=True)
    return samples


def build_prompt(conv, tokenizer):
    """Build prompt text from conversation (everything before first assistant turn)."""
    prompt_msgs = []
    for msg in conv:
        if msg['role'] == 'assistant':
            break
        prompt_msgs.append(msg)
    if not prompt_msgs:
        return None
    prompt_parts = []
    for msg in prompt_msgs:
        if msg['role'] == 'tool':
            wrapped = (f"{TOOL_WRAPPER_OPEN}\n{msg['content']}\n"
                       f"{TOOL_WRAPPER_CLOSE}")
            prompt_parts.append(format_turn(ROLE_USER, wrapped))
        else:
            prompt_parts.append(format_turn(msg['role'], msg['content']))
    prompt_text = "".join(prompt_parts)
    prompt_text += f"{IM_START}{ROLE_ASSISTANT}\n"
    return prompt_text


def extract_submit_value(response):
    """Extract submitted measurement value from model response.

    Looks for: submit(type, 1.23e-6) or submit(period, 1.23)
    Returns (target_type, value) or (None, None).
    """
    m = re.search(r'submit\s*\(\s*(\w+)\s*,\s*([\d.eE+\-]+)\s*\)', response)
    if m:
        try:
            return m.group(1), float(m.group(2))
        except ValueError:
            pass
    return None, None


def evaluate(llm, tokenizer, samples, device, dtype, args):
    """Run evaluation on all samples. Returns detailed results dict."""
    results = []
    format_ok = 0
    submit_ok = 0
    numerical_ok = 0   # rel_err < 1%
    numerical_close = 0  # rel_err < 5%
    total = 0
    rel_errors = []

    for i, traj in enumerate(samples):
        prompt_text = build_prompt(traj['conversation'], tokenizer)
        if prompt_text is None:
            continue
        total += 1
        enc = tokenizer(prompt_text, add_special_tokens=False,
                        return_tensors='pt', truncation=True,
                        max_length=args.seq_len - args.max_new_tokens)
        input_ids = enc['input_ids'].to(device)
        with torch.no_grad():
            out = llm.generate(
                input_ids, max_new_tokens=args.max_new_tokens,
                do_sample=False, temperature=1.0,
                pad_token_id=tokenizer.pad_token_id or 0,
                eos_token_id=tokenizer.eos_token_id)
        response = tokenizer.decode(out[0][input_ids.shape[1]:],
                                    skip_special_tokens=True).strip()
        has_format = any(p in response for p in VALID_TOOL_PATTERNS)
        if has_format:
            format_ok += 1
        has_submit = 'submit(' in response and \
            bool(re.search(r'submit\s*\([^)]*\d', response))
        if has_submit:
            submit_ok += 1
        gt_val = traj.get('gt_value')
        _, submit_val = extract_submit_value(response)
        rel_err = None
        if submit_val is not None and gt_val is not None and gt_val != 0:
            rel_err = abs(submit_val - gt_val) / abs(gt_val)
            rel_errors.append(rel_err)
            if rel_err < 0.01:
                numerical_ok += 1
            if rel_err < 0.05:
                numerical_close += 1
        if args.verbose:
            err_str = f" rel_err={rel_err:.4f}" if rel_err else ""
            print(f"  [{i+1}/{len(samples)}] fmt={has_format} "
                  f"sub={has_submit}{err_str}", flush=True)
        results.append({
            "id": traj.get('id', f'eval_{i}'),
            "circuit_type": traj.get('circuit_type', ''),
            "measure_target": traj.get('measure_target', ''),
            "format_ok": has_format, "submit_ok": has_submit,
            "submit_value": submit_val, "gt_value": gt_val,
            "rel_err": rel_err, "response_preview": response[:200],
        })
    n = max(1, total)
    return {
        "total_evaluated": total,
        "format_correctness": format_ok / n,
        "submit_success_rate": submit_ok / n,
        "numerical_accuracy_lt1pct": numerical_ok / n,
        "numerical_accuracy_lt5pct": numerical_close / n,
        "mean_rel_err": (sum(rel_errors)/len(rel_errors)
                         if rel_errors else None),
        "median_rel_err": (sorted(rel_errors)[len(rel_errors)//2]
                           if rel_errors else None),
        "target_format": args.target_format,
        "target_submit": args.target_submit,
        "pass": (format_ok / n >= args.target_format and
                 submit_ok / n >= args.target_submit),
        "per_sample": results,
    }


def main():
    args = parse_args()
    print("=== Stage-1W SFT Evaluation ===", flush=True)
    print(f"  Model: {args.model_path}", flush=True)
    print(f"  Adapter: {args.adapter_path or '(none — base model)'}", flush=True)
    print(f"  Eval file: {args.eval_file}", flush=True)
    print(f"  Max eval: {args.max_eval}", flush=True)
    print(f"  Device: {args.device}", flush=True)
    llm, tokenizer, device, dtype = load_model(args)
    samples = load_eval_data(args.eval_file, args.max_eval)
    t0 = time.time()
    summary = evaluate(llm, tokenizer, samples, device, dtype, args)
    elapsed = time.time() - t0
    print(f"\n=== Results ({summary['total_evaluated']} samples, "
          f"{elapsed:.1f}s) ===", flush=True)
    print(f"  Format correctness:     {summary['format_correctness']:.1%} "
          f"(target >= {summary['target_format']:.0%})", flush=True)
    print(f"  Submit success rate:     {summary['submit_success_rate']:.1%} "
          f"(target >= {summary['target_submit']:.0%})", flush=True)
    print(f"  Numerical acc (rel<1%):  "
          f"{summary['numerical_accuracy_lt1pct']:.1%}", flush=True)
    print(f"  Numerical acc (rel<5%):  "
          f"{summary['numerical_accuracy_lt5pct']:.1%}", flush=True)
    if summary['mean_rel_err'] is not None:
        print(f"  Mean rel error:          "
              f"{summary['mean_rel_err']:.4f}", flush=True)
    print(f"  PASS: {summary['pass']}", flush=True)
    if args.output:
        os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
        with open(args.output, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        print(f"\n  Results saved to {args.output}", flush=True)


if __name__ == '__main__':
    main()
