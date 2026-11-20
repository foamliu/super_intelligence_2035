#!/usr/bin/env python
"""CPU mini-training validation for Stage-1W SFT (Phase 1 wave RL).

PURPOSE:
  The dry-run test (_dryrun_test.py) verifies data loading and formatting
  WITHOUT loading the model.  The CPU loading verification (§20.18) checks
  that the 2B model loads, but NOT that forward+backward+optimizer work.
  This script fills that gap: it runs 3 REAL training steps (forward pass,
  loss computation, backward pass, gradient clipping, optimizer step) on
  CPU, then saves a checkpoint and verifies it loads back correctly.
  It also runs 1 generation to verify the eval pipeline works.

  If this passes, we have high confidence that when GPU becomes available
  (~Dec 24-25 when pretrain baize2b finishes), the SFT poller will launch
  training successfully without wasting GPU time on debugging.

USAGE:
  cd doc/BaiZe-ISEDA2027/run/vision
  python wave_rl/_cpu_train_validate.py

Author: vision agent.  License: project-internal.
"""

import sys, os, json, time, tempfile, math

import torch
import torch.nn as nn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sft_train_wave import (
    LLM_PATH_2B, DATA_FILE, OUTPUT_DIR,
    WaveSFTDataset, collate_fn, conversation_to_text,
    format_turn, IM_START, IM_END,
)
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model, TaskType, PeftModel


def parse_args():
    import argparse
    p = argparse.ArgumentParser(description="CPU mini-training validation")
    p.add_argument('--model_path', type=str, default=LLM_PATH_2B)
    p.add_argument('--data_file', type=str, default=DATA_FILE)
    p.add_argument('--n_steps', type=int, default=3)
    p.add_argument('--n_samples', type=int, default=3)
    p.add_argument('--seq_len', type=int, default=512,
                   help="Shorter seq_len for CPU speed (production uses 2048)")
    p.add_argument('--lora_r', type=int, default=64)
    p.add_argument('--lora_alpha', type=int, default=128)
    return p.parse_args()


def main():
    args = parse_args()
    device = torch.device('cpu')
    dtype = torch.bfloat16

    print("=" * 60, flush=True)
    print("CPU Mini-Training Validation for Stage-1W SFT", flush=True)
    print("=" * 60, flush=True)
    print(f"  Model: {args.model_path}", flush=True)
    print(f"  Steps: {args.n_steps} | Samples: {args.n_samples}", flush=True)
    print(f"  Seq len: {args.seq_len} | dtype: {dtype}", flush=True)
    print(flush=True)

    results = {}

    # Step 1: Tokenizer
    print("[1/7] Loading tokenizer...", end=' ', flush=True)
    tokenizer = AutoTokenizer.from_pretrained(
        args.model_path, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    print(f"OK (vocab={len(tokenizer)})", flush=True)
    results['tokenizer'] = 'OK'

    # Step 2: Dataset
    print(f"[2/7] Loading dataset ({args.n_samples} samples)...", end=' ', flush=True)
    indices = set(range(args.n_samples))
    dataset = WaveSFTDataset(args.data_file, tokenizer,
                             seq_len=args.seq_len, indices=indices)
    print(f"OK ({len(dataset)} samples)", flush=True)
    results['dataset'] = f'{len(dataset)} samples'

    # Step 3: Load model on CPU
    print("[3/7] Loading 2B model on CPU (bfloat16)...", flush=True)
    t0 = time.time()
    llm = AutoModelForCausalLM.from_pretrained(
        args.model_path, torch_dtype=dtype, trust_remote_code=True)
    print(f"  Loaded in {time.time()-t0:.1f}s "
          f"(params={sum(p.numel() for p in llm.parameters())/1e9:.2f}B)",
          flush=True)
    results['model_load'] = f'{time.time()-t0:.1f}s'

    # Step 4: Apply LoRA
    print("[4/7] Applying LoRA...", end=' ', flush=True)
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=args.lora_r, lora_alpha=args.lora_alpha, lora_dropout=0.05,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
    )
    llm = get_peft_model(llm, lora_config)
    trainable = [p for p in llm.parameters() if p.requires_grad]
    n_trainable = sum(p.numel() for p in trainable)
    print(f"OK ({n_trainable/1e6:.1f}M trainable)", flush=True)
    results['lora_trainable_params'] = f'{n_trainable/1e6:.1f}M'

    # Step 5: Training loop
    print(f"\n[5/7] Running {args.n_steps} training steps on CPU...", flush=True)
    optimizer = torch.optim.AdamW(trainable, lr=1e-5, weight_decay=0.01)
    llm.train()
    losses = []
    t0 = time.time()
    for step in range(args.n_steps):
        idx = step % len(dataset)
        sample = dataset[idx]
        input_ids = torch.tensor([sample['input_ids']], dtype=torch.long)
        attention_mask = torch.ones_like(input_ids)
        labels = torch.tensor([sample['labels']], dtype=torch.long)
        with torch.amp.autocast('cpu', dtype=dtype):
            outputs = llm(input_ids=input_ids,
                          attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
        loss.backward()
        grad_norm = torch.nn.utils.clip_grad_norm_(trainable, 1.0)
        optimizer.step()
        optimizer.zero_grad()
        losses.append(loss.item())
        print(f"  step {step+1}/{args.n_steps} | loss={loss.item():.4f} | "
              f"grad_norm={grad_norm:.4f} | {time.time()-t0:.1f}s", flush=True)
    results['train_losses'] = losses
    results['train_time'] = f'{time.time()-t0:.1f}s'
    all_finite = all(not (math.isnan(l) or math.isinf(l)) for l in losses)
    results['train_pass'] = all_finite
    print(f"  {'✅ Training loop PASS' if all_finite else '❌ FAIL: NaN/Inf loss'}",
          flush=True)

    # Step 6: Save + reload checkpoint
    print(f"\n[6/7] Save + reload checkpoint...", flush=True)
    with tempfile.TemporaryDirectory() as ckpt_dir:
        llm.save_pretrained(ckpt_dir)
        tokenizer.save_pretrained(ckpt_dir)
        ckpt_size = sum(
            os.path.getsize(os.path.join(ckpt_dir, f))
            for f in os.listdir(ckpt_dir))
        print(f"  Saved: {ckpt_size/1e6:.1f} MB", flush=True)
        ac_path = os.path.join(ckpt_dir, "adapter_config.json")
        if os.path.exists(ac_path):
            with open(ac_path) as f:
                ac = json.load(f)
            print(f"  adapter_config: r={ac.get('r')}, "
                  f"alpha={ac.get('lora_alpha')}", flush=True)
            results['checkpoint_save'] = 'OK'
        else:
            print("  ❌ FAIL: adapter_config.json missing!", flush=True)
            results['checkpoint_save'] = 'FAIL'
        base = AutoModelForCausalLM.from_pretrained(
            args.model_path, torch_dtype=dtype, trust_remote_code=True)
        reloaded = PeftModel.from_pretrained(base, ckpt_dir)
        print(f"  Reloaded OK", flush=True)
        results['checkpoint_reload'] = 'OK'
        del base, reloaded

    # Step 7: Generation test
    print(f"\n[7/7] Generation test (1 sample)...", flush=True)
    llm.eval()
    traj = dataset.samples[0]
    conv = traj['conversation']
    prompt_msgs = []
    for msg in conv:
        if msg['role'] == 'assistant':
            break
        prompt_msgs.append(msg)
    prompt_text, _ = conversation_to_text(prompt_msgs)
    prompt_text += f"{IM_START}assistant\n"
    inputs = tokenizer(prompt_text, return_tensors='pt',
                       truncation=True, max_length=args.seq_len)
    t0 = time.time()
    with torch.no_grad():
        with torch.amp.autocast('cpu', dtype=dtype):
            gen_ids = llm.generate(
                **inputs, max_new_tokens=64, do_sample=False,
                pad_token_id=tokenizer.pad_token_id)
    gen_text = tokenizer.decode(
        gen_ids[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
    n_gen = len(gen_ids[0]) - inputs['input_ids'].shape[1]
    print(f"  Generated {n_gen} tokens in {time.time()-t0:.1f}s", flush=True)
    print(f"  Preview: {gen_text[:200]}", flush=True)
    results['generation'] = gen_text[:200]
    results['gen_time'] = f'{time.time()-t0:.1f}s'

    # Summary
    print(f"\n{'=' * 60}", flush=True)
    print("VALIDATION SUMMARY", flush=True)
    print(f"{'=' * 60}", flush=True)
    all_pass = (results.get('train_pass') and
                results.get('checkpoint_save') == 'OK' and
                results.get('checkpoint_reload') == 'OK')
    for k, v in results.items():
        print(f"  {k}: {v}", flush=True)
    print(f"\n  Overall: {'✅ ALL PASS' if all_pass else '❌ FAIL'}", flush=True)
    out_path = os.path.join(os.path.dirname(__file__),
                            '_cpu_train_validate_result.json')
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"  Results saved to {out_path}", flush=True)
    return 0 if all_pass else 1


if __name__ == '__main__':
    sys.exit(main())
