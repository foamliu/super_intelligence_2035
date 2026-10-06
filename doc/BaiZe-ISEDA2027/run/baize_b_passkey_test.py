#!/usr/bin/env python3
"""B: Passkey retrieval test at 4K and 8K context.
Tests whether the model can retrieve a passkey buried in a long prompt.
B1 showed 0% at all lengths — this confirms/denies for 8K specifically.
"""
import argparse, json, os, sys, time
import torch
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

def make_passkey_prompt(tok, target_tokens, passkey="42"):
    """Build a prompt with a passkey buried in filler text."""
    filler = ("The quick brown fox jumps over the lazy dog. "
              "The ancient oak tree stands tall in the forest. "
              "Birds sing melodiously in the early morning light. ")
    # Encode filler to get token count
    filler_ids = tok.encode(filler, add_special_tokens=False)

    # Build: system_prefix + filler + passkey + filler + question
    prefix = f"The pass key is {passkey}. Remember it.\n"
    prefix_ids = tok.encode(prefix, add_special_tokens=False)

    question = f"\nWhat is the pass key? The pass key is"
    question_ids = tok.encode(question, add_special_tokens=False)

    # Fill with filler to reach target length
    target_filler = target_tokens - len(prefix_ids) - len(question_ids) - 10
    full_filler = []
    while len(full_filler) < target_filler:
        full_filler.extend(filler_ids)

    # Put passkey in the middle
    half = target_filler // 2
    all_ids = prefix_ids + full_filler[:half] + full_filler[half:target_filler] + question_ids

    prompt = tok.decode(all_ids, skip_special_tokens=True)
    actual_len = len(tok.encode(prompt, add_special_tokens=False))
    return prompt, actual_len

def test_passkey(model, tok, target_tokens, n_trials=5):
    correct = 0
    for i in range(n_trials):
        passkey = str(100 + i * 7)  # vary passkey
        prompt, actual_len = make_passkey_prompt(tok, target_tokens, passkey)
        inputs = tok(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            out = model.generate(**inputs, max_new_tokens=10, do_sample=False)
        response = tok.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        # Check if passkey is in the response
        if passkey in response.strip():
            correct += 1
    return correct / n_trials, actual_len

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-path", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--contexts", type=int, nargs="+", default=[4096, 8192])
    ap.add_argument("--trials", type=int, default=5)
    args = ap.parse_args()

    print(f"Loading model from {args.model_path}...")
    config = AutoConfig.from_pretrained(args.model_path, trust_remote_code=True)
    print(f"  max_pos={config.max_position_embeddings}, rope_theta={getattr(config, 'rope_theta', '?')}")
    model = AutoModelForCausalLM.from_pretrained(
        args.model_path, config=config, dtype=torch.bfloat16,
        trust_remote_code=True, low_cpu_mem_usage=True)
    model = model.cuda().eval()
    tok = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)

    results = []
    for ctx in args.contexts:
        acc, actual_len = test_passkey(model, tok, ctx, args.trials)
        r = {"context": ctx, "actual_tokens": actual_len, "passkey_acc": acc, "trials": args.trials}
        print(f"  ctx={ctx} (actual={actual_len}): passkey_acc={acc:.2f} ({int(acc*args.trials)}/{args.trials})")
        results.append(r)

    output = {"experiment": "B_passkey", "model_path": args.model_path,
              "config": {"max_pos": config.max_position_embeddings,
                         "rope_theta": getattr(config, "rope_theta", None)},
              "results": results}
    with open(args.output, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Saved to {args.output}")

    del model
    torch.cuda.empty_cache()

if __name__ == "__main__":
    main()