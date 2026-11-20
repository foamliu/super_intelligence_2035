#!/usr/bin/env python3
"""Test if degenerate ckpts (20k/40k/50k) produce NaN/Inf logits for LONGER sequences.

Hypothesis: 1-token "Hello" forward pass is valid, but longer sequences (like
lm_eval sciq prompts ~50-200 tokens) trigger NaN in Mamba2 SSM recurrence.

Tests: progressively longer sequences on normal (10k) vs degenerate (20k) ckpts.
Also tests loglikelihood computation (like lm_eval) to check for NaN in cont. logits.
"""
import sys, os, types, warnings
warnings.filterwarnings("ignore")
for mod_name in ["mamba_ssm", "causal_conv1d"]:
    fake = types.ModuleType(mod_name)
    fake.__file__ = f"<blocked:{mod_name}>"
    fake.__path__ = []
    sys.modules[mod_name] = fake
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ.setdefault("HF_DATASETS_OFFLINE", "1")
os.environ.setdefault("HF_HUB_OFFLINE", "1")

import torch
torch.set_num_threads(8)
from transformers import AutoModelForCausalLM, AutoTokenizer

base = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b"
tok = AutoTokenizer.from_pretrained(base + "/hf_iter_10000")

# Realistic sciq-style prompt (question + 4 choices format like lm_eval)
sciq_prompt = (
    "Question: What is the primary source of energy for Earth's climate system?\n"
    "Answer:"
)
# A longer prompt (~100+ tokens) similar to what lm_eval constructs
long_prompt = (
    "The following are questions about science. Please answer each question with "
    "the correct option.\n\n"
    "Question: What is the primary source of energy for Earth's climate system?\n"
    "A. The Sun\nB. Geothermal heat\nC. Tidal forces\nD. Cosmic rays\n"
    "Answer:"
)

test_prompts = [
    ("short_2tok",   "Hello world"),
    ("sciq_q",       sciq_prompt),
    ("sciq_long",    long_prompt),
]

# Also test with a very long sequence (padding to ~200 tokens)
long_text = " ".join(["The quick brown fox jumps over the lazy dog."] * 15)
test_prompts.append(("200tok", long_text))

# Checkpoints to compare: normal (10k, 30k) vs degenerate (20k, 40k, 50k)
ckpts = [10000, 20000, 40000, 50000]

print("=" * 70, flush=True)
print("LONG SEQUENCE NaN TEST: normal(10k) vs degenerate(20k/40k/50k)", flush=True)
print("=" * 70, flush=True)

for it in ckpts:
    print(f"\n{'='*40}", flush=True)
    print(f"--- iter_{it} ---", flush=True)
    model = AutoModelForCausalLM.from_pretrained(
        base + f"/hf_iter_{it}", dtype=torch.float32, low_cpu_mem_usage=True
    )
    model.eval()

    for name, prompt in test_prompts:
        ids = tok(prompt, return_tensors="pt", add_special_tokens=False)
        n_tok = ids["input_ids"].shape[1]
        with torch.no_grad():
            out = model(**ids)
        logits = out.logits  # [1, seq_len, vocab]
        last_logits = logits[0, -1, :]

        # Check entire sequence for NaN/Inf
        nan_all = torch.isnan(logits).sum().item()
        inf_all = torch.isinf(logits).sum().item()
        nan_last = torch.isnan(last_logits).sum().item()
        inf_last = torch.isinf(last_logits).sum().item()

        status = "OK" if (nan_last == 0 and inf_last == 0) else "CORRUPT"
        print(f"  [{name:10s}] n_tok={n_tok:4d}  last: NaN={nan_last} Inf={inf_last}  "
              f"all: NaN={nan_all} Inf={inf_all}  min={last_logits.min():.3f} "
              f"max={last_logits.max():.3f} std={last_logits.std():.4f}  => {status}",
              flush=True)

        # If corrupt, also check hidden states
        if nan_all > 0 or inf_all > 0:
            # Find first layer with NaN
            print(f"    !! NaN/Inf detected in logits! Checking per-layer...", flush=True)
            # We can't easily get per-layer output without hooks, but we can
            # check if the NaN appears at specific positions
            for pos in [0, n_tok//4, n_tok//2, 3*n_tok//4, n_tok-1]:
                pos_logits = logits[0, pos, :]
                pn = torch.isnan(pos_logits).sum().item()
                pi = torch.isinf(pos_logits).sum().item()
                if pn > 0 or pi > 0:
                    print(f"    pos={pos}: NaN={pn} Inf={pi}", flush=True)

    del model
    import gc; gc.collect()

print("\n" + "=" * 70, flush=True)
print("=== DONE ===", flush=True)
