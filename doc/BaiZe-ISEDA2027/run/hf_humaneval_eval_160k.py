#!/usr/bin/env python3
"""HF transformers HumanEval evaluation (limit=20) on 160k ckpt.
CPU only, OMP_NUM_THREADS=4, nice 19 — must not affect training.
Loads model directly with AutoModelForCausalLM (same as GSM8K HF eval).
Executes generated code in subprocess for safety.
"""
import os, sys, time, json, re, torch, subprocess, tempfile
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["OMP_NUM_THREADS"] = "4"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_CACHE"] = "/nas_train/app.e0031982/hf_cache"
os.environ["HF_HOME"] = "/nas_train/app.e0031982/.cache"

# Use sglang env's native transformers 5.18.0 (has NemotronH built-in, torch 2.9.1)
# No p6_tf5 PYTHONPATH override needed — native is more stable

from transformers import AutoModelForCausalLM, AutoTokenizer

# Limit torch threads to avoid CPU contention with training
torch.set_num_threads(4)

MODEL_PATH = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/hf_iter_160000"
N_SAMPLES = 20
MAX_NEW_TOKENS = 512
OUT_FILE = "/tmp/hf_humaneval_160k_results.json"

def run_code_test(code, test_code, entry_point, timeout=10):
    """Execute generated code + test in a subprocess. Returns (passed, error)."""
    full_code = code + "\n\n" + test_code + f"\n\ncheck({entry_point})\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, dir="/tmp") as f:
        f.write(full_code)
        f.flush()
        fname = f.name
    try:
        result = subprocess.run(
            [sys.executable, fname],
            capture_output=True, text=True, timeout=timeout,
            env={**os.environ, "CUDA_VISIBLE_DEVICES": ""}
        )
        os.unlink(fname)
        if result.returncode == 0:
            return True, ""
        return False, result.stderr[:300]
    except subprocess.TimeoutExpired:
        os.unlink(fname)
        return False, "timeout"
    except Exception as e:
        if os.path.exists(fname):
            os.unlink(fname)
        return False, str(e)[:300]

def extract_completion(prompt, generated_text):
    """Extract the function body from generated text.
    HumanEval prompts end with the function signature; the model should
    generate the body. We take everything until we see a new top-level def/class."""
    # Stop at common stop sequences
    stop_seqs = ["\nclass ", "\ndef ", "\n# ", "\nif __name__", "\nprint("]
    text = generated_text
    min_idx = len(text)
    for s in stop_seqs:
        idx = text.find(s)
        if idx != -1 and idx < min_idx:
            min_idx = idx
    return text[:min_idx]

print(f"[{time.strftime('%H:%M:%S')}] Loading HumanEval problems from JSON...", flush=True)
with open("/tmp/humaneval_20.json") as f:
    problems = json.load(f)
print(f"[{time.strftime('%H:%M:%S')}] Loaded {len(problems)} problems, using first {N_SAMPLES}", flush=True)

print(f"[{time.strftime('%H:%M:%S')}] Loading model (bfloat16, CPU)...", flush=True)
tok = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
t0 = time.time()
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, dtype=torch.bfloat16, trust_remote_code=True)
model.eval()
print(f"[{time.strftime('%H:%M:%S')}] Loaded in {time.time()-t0:.1f}s, {type(model).__name__}", flush=True)

passed = 0
results = []
for i in range(N_SAMPLES):
    problem = problems[i]
    prompt = problem["prompt"]
    test_code = problem["test"]
    entry_point = problem["entry_point"]
    task_id = problem["task_id"]

    inputs = tok(prompt, return_tensors="pt")
    il = inputs.input_ids.shape[1]
    t0 = time.time()
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=MAX_NEW_TOKENS, do_sample=False,
            pad_token_id=tok.pad_token_id or tok.eos_token_id)
    gt = time.time() - t0
    raw_text = tok.decode(out[0][il:], skip_special_tokens=True)
    completion = extract_completion(prompt, raw_text)
    full_code = prompt + completion

    ok, err = run_code_test(full_code, test_code, entry_point)
    if ok:
        passed += 1

    results.append({
        "idx": i, "task_id": task_id, "entry_point": entry_point,
        "ok": ok, "time": round(gt, 1),
        "gen_preview": raw_text[:200],
        "error": err if not ok else ""
    })
    status = "PASS" if ok else "FAIL"
    print(f"[{i+1}/{N_SAMPLES}] {task_id} {status} t={gt:.1f}s | {raw_text[:100]}", flush=True)
    if not ok and err:
        print(f"  error: {err[:150]}", flush=True)

acc = passed / N_SAMPLES
print(f"\nHumanEval HF Results: {passed}/{N_SAMPLES} = {acc*100:.1f}% (pass@1)", flush=True)
with open(OUT_FILE, "w") as f:
    json.dump({"n": N_SAMPLES, "passed": passed, "pass@1": acc,
               "backend": "hf_bf16_cpu", "model": "160k", "results": results}, f, indent=2)
print(f"[{time.strftime('%H:%M:%S')}] Done. Saved to {OUT_FILE}", flush=True)
