#!/usr/bin/env python3
"""
BaiZe 2B L2 HumanEval HF Direct Evaluation
Uses sglang env (transformers 5.18.0, pyarrow) — no lm_eval/sklearn dependency.
Loads HumanEval from HF cache arrow file, generates completions, runs tests.
CPU only, nice 19, OMP_NUM_THREADS=4 — must not affect training.

Usage:
  CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=4 nice -n 19 \
    /nas_train/app.e0031982/miniforge3/envs/sglang/bin/python \
    baize_l2_hf_humaneval_direct.py --model_path <path> --limit 50
"""
import argparse
import json
import os
import sys
import subprocess
import tempfile
import time

# Force CPU
os.environ["CUDA_VISIBLE_DEVICES"] = ""

import torch
torch.set_num_threads(8)

import pyarrow as pa
import pyarrow.ipc as ipc
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

HUMANEVAL_ARROW = (
    "/nas_train/app.e0031982/hf_cache/openai___openai_humaneval/"
    "openai_humaneval/0.0.0/"
    "7dce6050a7d6d172f3cc5c32aa97f52fa1a2e544/openai_humaneval-test.arrow"
)


def load_humaneval(limit=None):
    """Load HumanEval problems from HF cache arrow file."""
    with open(HUMANEVAL_ARROW, "rb") as f:
        reader = ipc.open_stream(f)
        table = reader.read_all()
    df = table.to_pylist()
    if limit:
        df = df[:limit]
    return df


def extract_completion(generated_text, prompt):
    """Extract completion from generated text.
    HumanEval format: prompt ends with the function signature.
    Completion is the generated text up to the next function/class definition or end.
    """
    completion = generated_text
    # Try to cut at the next def/class (common stopping pattern)
    for stop in ["\ndef ", "\nclass ", "\n\n\n", "\nif __name__"]:
        idx = completion.find(stop)
        if idx > 0:
            completion = completion[:idx]
    return completion


def run_test(code, test, entry_point, timeout=10):
    """Run a HumanEval test in a subprocess. Returns True if pass."""
    full_code = code + "\n\n" + test + f"\n\ncheck({entry_point})"
    try:
        result = subprocess.run(
            [sys.executable, "-c", full_code],
            capture_output=True,
            timeout=timeout,
            text=True,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model_path",
        default="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/hf_iter_160000",
    )
    parser.add_argument("--limit", type=int, default=50, help="Number of problems to evaluate")
    parser.add_argument("--max_new_tokens", type=int, default=256)
    parser.add_argument(
        "--outdir",
        default="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results/gguf_iter_160000_l2_hf_humaneval_direct",
    )
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Loading HumanEval ({args.limit} problems)...")
    problems = load_humaneval(args.limit)
    print(f"  Loaded {len(problems)} problems")

    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Loading model from {args.model_path}...")
    tokenizer = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_path,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
    )
    model.eval()
    print(f"  Model loaded (CPU, bfloat16)")

    results = []
    passed = 0
    total = len(problems)

    for i, problem in enumerate(problems):
        prompt = problem["prompt"]
        entry_point = problem["entry_point"]
        test = problem["test"]

        # Tokenize prompt
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)

        # Generate
        t0 = time.time()
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=args.max_new_tokens,
                do_sample=False,  # greedy
                pad_token_id=tokenizer.eos_token_id,
            )
        gen_time = time.time() - t0

        # Decode generated text (excluding prompt)
        generated = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        completion = extract_completion(generated, prompt)
        full_code = prompt + completion

        # Run test
        is_pass = run_test(full_code, test, entry_point)
        if is_pass:
            passed += 1

        result = {
            "task_id": problem.get("task_id", f"HumanEval_{i}"),
            "entry_point": entry_point,
            "pass": is_pass,
            "gen_time_s": round(gen_time, 2),
            "completion_length": len(completion),
        }
        results.append(result)

        status = "✅ PASS" if is_pass else "❌ FAIL"
        print(
            f"  [{i+1}/{total}] {result['task_id']} {status} "
            f"({gen_time:.1f}s, {len(completion)} chars) | pass@1={passed}/{i+1}={passed/(i+1)*100:.1f}%"
        )

    pass_at_1 = passed / total if total > 0 else 0
    print(f"\n{'='*60}")
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] HumanEval pass@1 = {passed}/{total} = {pass_at_1*100:.1f}%")
    print(f"{'='*60}")

    # Save results
    summary = {
        "model": args.model_path,
        "task": "humaneval",
        "limit": args.limit,
        "pass_at_1": pass_at_1,
        "passed": passed,
        "total": total,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "details": results,
    }
    outpath = os.path.join(args.outdir, "results.json")
    with open(outpath, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Results saved to {outpath}")


if __name__ == "__main__":
    main()
