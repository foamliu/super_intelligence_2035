#!/usr/bin/env python3
"""HF transformers generation test for BaiZe 2B 160k checkpoint.
Purpose: determine if L2=0% is due to llama.cpp SSM bug or real capability.
If HF generates coherent text where llama.cpp produced repetitive garbage,
the llama.cpp bug is masking model capability.
CPU only, low threads, nice 19 — must not affect training throughput.
"""
import os, sys, time, torch
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["OMP_NUM_THREADS"] = "4"

from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_PATH = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/hf_iter_160000"

print(f"[{time.strftime('%H:%M:%S')}] Loading tokenizer...", flush=True)
tok = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)

print(f"[{time.strftime('%H:%M:%S')}] Loading model (float32, CPU)...", flush=True)
t0 = time.time()
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    dtype=torch.float32,
    trust_remote_code=True,
)
model.eval()
print(f"[{time.strftime('%H:%M:%S')}] Model loaded in {time.time()-t0:.1f}s", flush=True)
print(f"  Model type: {type(model).__name__}", flush=True)
print(f"  Params: {sum(p.numel() for p in model.parameters())/1e9:.2f}B", flush=True)

prompts = [
    # Simple completion
    "The capital of France is",
    # GSM8K-style
    "Question: Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?\nAnswer:",
    # Code generation
    "def fibonacci(n):\n    \"\"\"Return the n-th Fibonacci number.\"\"\"\n",
]

for prompt in prompts:
    print(f"\n{'='*60}", flush=True)
    print(f"PROMPT: {prompt[:100]}", flush=True)
    inputs = tok(prompt, return_tensors="pt")
    print(f"  Input tokens: {inputs.input_ids.shape[1]}", flush=True)
    
    t0 = time.time()
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=100,
            do_sample=False,
            temperature=1.0,
            top_p=1.0,
            pad_token_id=tok.pad_token_id or tok.eos_token_id,
        )
    gen_time = time.time() - t0
    new_tokens = out[0][inputs.input_ids.shape[1]:]
    text = tok.decode(new_tokens, skip_special_tokens=True)
    print(f"  Generated {len(new_tokens)} tokens in {gen_time:.1f}s ({len(new_tokens)/gen_time:.1f} tok/s)", flush=True)
    print(f"  OUTPUT: {text[:300]}", flush=True)
    
    # Check for repetition
    words = text.split()
    if len(words) > 10:
        from collections import Counter
        most_common = Counter(words).most_common(3)
        print(f"  Top 3 words: {most_common}", flush=True)
        max_repeat = most_common[0][1] if most_common else 0
        if max_repeat > len(words) * 0.4:
            print(f"  ⚠️ REPETITIVE: top word appears {max_repeat}/{len(words)} times", flush=True)
        else:
            print(f"  ✅ NOT repetitive", flush=True)

print(f"\n[{time.strftime('%H:%M:%S')}] Done.", flush=True)
