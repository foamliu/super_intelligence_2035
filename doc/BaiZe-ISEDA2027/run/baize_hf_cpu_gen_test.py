#!/usr/bin/env python3
"""Test HF transformers CPU generation for BaiZe 2B (NemotronH) @ 160k.
Purpose: Determine if generation degradation is a llama.cpp bug or model issue.
If HF CPU generation produces coherent text → llama.cpp SSM generation is buggy.
If HF CPU generation also collapses → model issue (needs more training or arch fix).
"""
import torch, os, time, sys
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["OMP_NUM_THREADS"] = "4"

from transformers.models.nemotron_h.modeling_nemotron_h import NemotronHForCausalLM
from transformers.models.nemotron_h.configuration_nemotron_h import NemotronHConfig
from transformers import AutoTokenizer

model_path = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/hf_iter_160000"
print("Loading config...", flush=True)
config = NemotronHConfig.from_pretrained(model_path)
print(f"Config loaded: model_type={config.model_type}, layers={config.num_hidden_layers}", flush=True)

print("Loading model on CPU (float32)...", flush=True)
t0 = time.time()
model = NemotronHForCausalLM.from_pretrained(model_path, config=config, torch_dtype=torch.float32)
model = model.eval()
n_params = sum(p.numel() for p in model.parameters()) / 1e9
print(f"Model loaded in {time.time()-t0:.1f}s, params={n_params:.2f}B", flush=True)

tok = AutoTokenizer.from_pretrained(model_path)

tests = [
    "True or False: (True and False) or (True and True) =",
    "Question: What is 2 + 3? Answer:",
    "The capital of France is",
    "Q: Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May? A:",
]

for prompt in tests:
    inp = tok(prompt, return_tensors="pt")
    print(f"\n--- Test: {prompt[:80]} ---", flush=True)
    t1 = time.time()
    with torch.no_grad():
        out = model.generate(
            **inp, max_new_tokens=50, do_sample=False, temperature=1.0,
            pad_token_id=tok.eos_token_id
        )
    gen_text = tok.decode(out[0][inp["input_ids"].shape[1]:], skip_special_tokens=True)
    elapsed = time.time() - t1
    print(f"Generated ({elapsed:.1f}s): {gen_text[:300]}", flush=True)

# Also test loglikelihood (first token) to compare with llama.cpp
print("\n=== Loglikelihood check (first token) ===", flush=True)
prompt = "The capital of France is"
target = " Paris"
inp = tok(prompt, return_tensors="pt")
target_ids = tok(target, return_tensors="pt")["input_ids"]
with torch.no_grad():
    logits = model(**inp).logits[0, -1, :]
probs = torch.softmax(logits, dim=-1)
for tid in target_ids[0]:
    print(f"  token_id={tid.item()}, token={tok.decode([tid.item()])!r}, prob={probs[tid].item():.4f}, logprob={torch.log(probs[tid]).item():.4f}", flush=True)

print("\n=== CPU HF generation test complete ===", flush=True)
