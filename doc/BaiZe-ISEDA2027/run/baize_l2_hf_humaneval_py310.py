#!/usr/bin/env python3
"""
BaiZe 2B L2 HumanEval HF Direct Evaluation (py310 + p6_tf5 + sklearn fix)
Fixes sklearn/numpy binary incompatibility by removing /dev/shm from sys.path.
CPU only, nice 19 — must not affect training.
"""
import argparse, json, os, sys, subprocess, time

# === Fix sklearn pollution BEFORE any other imports ===
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["OMP_NUM_THREADS"] = "8"
# Remove /dev/shm paths from sys.path to avoid broken sklearn
sys.path = [p for p in sys.path if "/dev/shm" not in p]

import torch
torch.set_num_threads(8)
# Add p6_tf5 (transformers 5.17.0) to path
sys.path.insert(0, "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5")
from transformers import AutoModelForCausalLM, AutoTokenizer
import pyarrow.ipc as ipc

HUMANEVAL_ARROW = (
    "/nas_train/app.e0031982/hf_cache/openai___openai_humaneval/"
    "openai_humaneval/0.0.0/"
    "7dce6050a7d6d172f3cc5c32aa97f52fa1a2e544/openai_humaneval-test.arrow"
)


def load_humaneval(limit=None):
    with open(HUMANEVAL_ARROW, "rb") as f:
        reader = ipc.open_stream(f)
        table = reader.read_all()
    df = table.to_pylist()
    return df[:limit] if limit else df


def extract_completion(gen, prompt):
    for stop in ["\ndef ", "\nclass ", "\n\n\n", "\nif __name__"]:
        idx = gen.find(stop)
        if idx > 0:
            gen = gen[:idx]
    return gen


def run_test(code, test, entry_point, timeout=10):
    full = code + "\n\n" + test + f"\n\ncheck({entry_point})"
    try:
        r = subprocess.run([sys.executable, "-c", full], capture_output=True, timeout=timeout, text=True)
        return r.returncode == 0
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model_path", default="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/hf_iter_160000")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--max_new_tokens", type=int, default=128)
    ap.add_argument("--outdir", default="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results/gguf_iter_160000_l2_hf_humaneval_py310")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    print(f"[{time.strftime('%H:%M:%S')}] Loading HumanEval ({args.limit})...")
    problems = load_humaneval(args.limit)
    print(f"  Loaded {len(problems)} problems")

    print(f"[{time.strftime('%H:%M:%S')}] Loading model (py310+p6_tf5, 8 threads)...")
    tok = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(args.model_path, trust_remote_code=True, torch_dtype=torch.bfloat16)
    model.eval()
    print("  Model loaded")

    results, passed = [], 0
    total = len(problems)
    for i, prob in enumerate(problems):
        prompt = prob["prompt"]
        inp = tok(prompt, return_tensors="pt", truncation=True, max_length=2048)
        t0 = time.time()
        with torch.no_grad():
            out = model.generate(**inp, max_new_tokens=args.max_new_tokens, do_sample=False, pad_token_id=tok.eos_token_id)
        dt = time.time() - t0
        gen = tok.decode(out[0][inp["input_ids"].shape[1]:], skip_special_tokens=True)
        comp = extract_completion(gen, prompt)
        ok = run_test(prompt + comp, prob["test"], prob["entry_point"])
        if ok: passed += 1
        results.append({"task_id": prob.get("task_id", f"HE_{i}"), "pass": ok, "dt": round(dt, 2), "comp_len": len(comp)})
        st = "✅" if ok else "❌"
        print(f"  [{i+1}/{total}] {results[-1]['task_id']} {st} ({dt:.1f}s, {len(comp)}ch) | pass@1={passed}/{i+1}={passed/(i+1)*100:.1f}%")

    p1 = passed / total if total else 0
    print(f"\n{'='*60}")
    print(f"[{time.strftime('%H:%M:%S')}] HumanEval pass@1 = {passed}/{total} = {p1*100:.1f}%")
    print(f"{'='*60}")
    summary = {"model": args.model_path, "task": "humaneval", "limit": args.limit, "pass_at_1": p1,
               "passed": passed, "total": total, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "details": results}
    with open(os.path.join(args.outdir, "results.json"), "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Saved to {args.outdir}/results.json")

if __name__ == "__main__":
    main()
