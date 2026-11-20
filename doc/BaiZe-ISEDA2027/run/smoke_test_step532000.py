#!/usr/bin/env python3
"""Smoke test: verify step_532000 checkpoint loads and produces non-nan logits."""
import sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_PATH = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/xmodel25_history/step_532000"

print(f"Loading model from {MODEL_PATH} ...", flush=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH, dtype=torch.bfloat16, trust_remote_code=True
)
model = model.cuda().eval()
n_params = sum(p.numel() for p in model.parameters()) / 1e9
print(f"OK: {type(model).__name__}, {n_params:.3f}B params", flush=True)

tok = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
print(f"Tokenizer: {type(tok).__name__}, vocab={tok.vocab_size}", flush=True)

# Forward pass smoke test
text = "The capital of France is"
ids = tok(text, return_tensors="pt").to("cuda")
with torch.no_grad():
    out = model(**ids)
logits = out.logits
print(f"Logits shape: {logits.shape}, dtype: {logits.dtype}", flush=True)
print(f"Logits nan: {torch.isnan(logits).any().item()}, inf: {torch.isinf(logits).any().item()}", flush=True)
# Check the predicted next token
pred_id = logits[0, -1].argmax().item()
pred_token = tok.decode([pred_id])
print(f"Predicted next token: '{pred_token}' (id={pred_id})", flush=True)
print("SMOKE TEST PASSED", flush=True)
