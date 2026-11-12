#!/usr/bin/env python3
"""
BaiZe 2B L2 MBPP HF Direct Evaluation
Uses sglang env (transformers 5.18.0, pyarrow) — no lm_eval dependency.
Loads MBPP from HF cache arrow file, generates completions, runs tests.
CPU only, nice 19, OMP_NUM_THREADS=4 — must not affect training.
"""
import argparse, json, os, re, subprocess, sys, time
os.environ["CUDA_VISIBLE_DEVICES"] = ""
import pyarrow.ipc as ipc
import torch
torch.set_num_threads(8)
from transformers import AutoModelForCausalLM, AutoTokenizer

MBPP_ARROW = (
    "/nas_train/app.e0031982/hf_cache/google-research-datasets___mbpp/"
    "full/0.0.0/4bb6404fdc6cacfda99d4ac4205087b89d32030c/mbpp-test.arrow"
)


def load_mbpp(limit=None):
    with open(MBPP_ARROW, "rb") as f:
        reader = ipc.open_stream(f)
        table = reader.read_all()
    df = table.to_pylist()
    return df[:limit] if limit else df


def build_prompt(problem):
    text = problem["text"]
    test_list = problem.get("test_list", [])
    tests = "\n".join(test_list) if test_list else ""
    return (
        f"You are an expert Python programmer, and here is your task: {text}\n"
        f"Your code should pass these tests:\n{tests}\n\n[BEGIN]\n"
    )


def extract_code(generated_text):
    code = generated_text
    for stop in ["[END]", "```", "\n\n\n\n"]:
        idx = code.find(stop)
        if idx > 0:
            code = code[:idx]
    code = re.sub(r"^```python\s*\n?", "", code)
    code = re.sub(r"^```\s*\n?", "", code)
    return code.strip()


def run_tests(code, test_list, timeout=10):
    if not test_list:
        return False
    full_code = code + "\n\n" + "\n".join(test_list)
    try:
        result = subprocess.run(
            [sys.executable, "-c", full_code],
            capture_output=True, timeout=timeout, text=True,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, Exception):
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path",
        default="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/hf_iter_160000")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--max_new_tokens", type=int, default=256)
    parser.add_argument("--outdir",
        default="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results/gguf_iter_160000_l2_hf_mbpp_direct")
    args = parser.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Loading MBPP ({args.limit})...")
    problems = load_mbpp(args.limit)
    print(f"  Loaded {len(problems)} problems")
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Loading model from {args.model_path}...")
    tokenizer = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_path, trust_remote_code=True, torch_dtype=torch.bfloat16)
    model.eval()
    print(f"  Model loaded (CPU, bfloat16)")

    results = []
    passed = 0
    total = len(problems)

    for i, problem in enumerate(problems):
        prompt = build_prompt(problem)
        test_list = problem.get("test_list", [])
        task_id = problem.get("task_id", f"MBPP_{i}")
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
        t0 = time.time()
        with torch.no_grad():
            outputs = model.generate(
                **inputs, max_new_tokens=args.max_new_tokens,
                do_sample=False, pad_token_id=tokenizer.eos_token_id)
        gen_time = time.time() - t0
        generated = tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        code = extract_code(generated)
        is_pass = run_tests(code, test_list)
        if is_pass:
            passed += 1
        result = {"task_id": task_id, "pass": is_pass,
                  "gen_time_s": round(gen_time, 2), "code_length": len(code)}
        results.append(result)
        status = "✅ PASS" if is_pass else "❌ FAIL"
        print(f"  [{i+1}/{total}] {task_id} {status} "
              f"({gen_time:.1f}s, {len(code)} chars) | pass@1={passed}/{i+1}={passed/(i+1)*100:.1f}%")

    pass_at_1 = passed / total if total > 0 else 0
    print(f"\n{'='*60}")
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] MBPP pass@1 = {passed}/{total} = {pass_at_1*100:.1f}%")
    print(f"{'='*60}")
    summary = {"model": args.model_path, "task": "mbpp", "limit": args.limit,
               "pass_at_1": pass_at_1, "passed": passed, "total": total,
               "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "details": results}
    outpath = os.path.join(args.outdir, "results.json")
    with open(outpath, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Results saved to {outpath}")


if __name__ == "__main__":
    main()
