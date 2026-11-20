#!/usr/bin/env python3
"""cpu_rl_v5_typecls_experiment.py - CPU RL Waveform Experiment v5: Type Classification.

WHY v5 (DIRECTION CHANGE after 3 rounds with NO improvement, per task rule):
  v2 (discrete GRPO, period):   C=6.2%  < B=9.2%   -- NEGATIVE
  v3 (continuous GRPO, period):  C=25.0% < B=34.0%  -- NEGATIVE
  v4 (RFT, period):              C=34.0% = B=34.0%  -- NULL (no improvement)
  => 3 rounds without improvement => MUST change direction.

ROOT CAUSE ANALYSIS (why v2-v4 failed):
  1. Period REGRESSION (output a precise number) is too hard for a 2B LoRA model on CPU.
     The SFT ceiling is ~34%; neither GRPO nor RFT can push past it.
  2. GRPO has near-zero loss + std=0 advantage (78.7% of groups have identical rewards)
     => no learning signal even with continuous reward.
  3. RFT only reinforces what the model already knows (filters for correct rollouts,
     but the model can't do better than it already does on regression).
  4. The tool-call observation (get_values) only returns summary stats (min/max/mean/std),
     NOT actual sample points => the model CANNOT see the waveform shape.

v5 FIXES (pre-registered 2026-11-07 wake#881):
  1. CHANGE TASK: period regression -> waveform TYPE CLASSIFICATION (4-class:
     sine / square / triangle / sawtooth). Classification (output a label) is
     fundamentally easier than regression (output a precise number).
  2. CHANGE INPUT: Instead of tool-call observations with only summary stats,
     give the model ACTUAL sample points (16 evenly-spaced (t, v) pairs) directly
     in the prompt. The model can SEE the shape and classify it.
  3. KEEP METHOD: RFT (Rejection Sampling FT, aka STaR/ReST) -- proven stable
     in v4 (standard CE loss, no group baseline, no std=0 problem). For classification,
     there will be MORE correct rollouts => more training signal.

PRE-REGISTERED JUDGMENT (written BEFORE running):
  A (base model, fresh LoRA):  ~25% (random chance, 4-class)
  B (SFT on type classification):  >50% (shape recognition is learnable)
  C (RFT on top of B):  >B (more correct rollouts => more training signal)
  D (RFT with RANDOM filter = control):  <= B (random filtering doesn't help)
  SUCCESS: C > B, C > D, McNemar p < 0.05, bootstrap 95% CI on (C-B) excludes 0.

Author: vision wake#881.  License: project-internal.
"""
from __future__ import annotations
import sys, os, json, time, math, random, argparse, re
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model, TaskType, PeftModel

LLM_PATH = "/nas_train/app.e0031982/datasets/baize-vision/out/wave_sft_stage1w/qwen3vl_2b_text_extracted"
WAVEFORM_TYPES = ["sine", "square", "triangle", "sawtooth"]
N_SAMPLE_POINTS = 16
N_PERIODS = 2.0
EVAL_SEED_BASE = 995100
TRAIN_SEED_BASE = 20261107
IM_START = "<|im_start|>"
IM_END = "<|im_end|>"

SYSTEM_PROMPT = (
    "You are a waveform classification expert. You are given evenly-spaced "
    "voltage samples from a periodic electronic waveform. Classify it as "
    "one of: sine, square, triangle, or sawtooth. "
    "Respond with only the waveform type name, nothing else."
)


# ============================================================================ #
#  1. PURE WAVEFORM GENERATORS (programmatic, no ngspice needed)
# ============================================================================ #

def _gen_sine(rng):
    amp = float(rng.uniform(0.5, 5.0)); offset = float(rng.uniform(-2.0, 2.0))
    freq = float(rng.uniform(1.0, 10.0)); phase = float(rng.uniform(0, 2*math.pi))
    noise_std = float(rng.uniform(0.0, 0.03 * amp))
    t = np.linspace(0, N_PERIODS / freq, N_SAMPLE_POINTS, endpoint=False)
    v = offset + amp * np.sin(2 * math.pi * freq * t + phase)
    v += rng.normal(0, noise_std, size=len(t))
    return t, v

def _gen_square(rng):
    amp = float(rng.uniform(0.5, 5.0)); offset = float(rng.uniform(-2.0, 2.0))
    freq = float(rng.uniform(1.0, 10.0)); duty = float(rng.uniform(0.3, 0.7))
    noise_std = float(rng.uniform(0.0, 0.03 * amp))
    t = np.linspace(0, N_PERIODS / freq, N_SAMPLE_POINTS, endpoint=False)
    phase_in_cycle = (freq * t) % 1.0
    v = np.where(phase_in_cycle < duty, offset + amp, offset - amp)
    v += rng.normal(0, noise_std, size=len(t))
    return t, v

def _gen_triangle(rng):
    amp = float(rng.uniform(0.5, 5.0)); offset = float(rng.uniform(-2.0, 2.0))
    freq = float(rng.uniform(1.0, 10.0)); noise_std = float(rng.uniform(0.0, 0.03 * amp))
    t = np.linspace(0, N_PERIODS / freq, N_SAMPLE_POINTS, endpoint=False)
    phase = (freq * t) % 1.0
    tri = np.where(phase < 0.5, 4.0 * phase - 1.0, 3.0 - 4.0 * phase)
    v = offset + amp * tri
    v += rng.normal(0, noise_std, size=len(t))
    return t, v

def _gen_sawtooth(rng):
    amp = float(rng.uniform(0.5, 5.0)); offset = float(rng.uniform(-2.0, 2.0))
    freq = float(rng.uniform(1.0, 10.0)); noise_std = float(rng.uniform(0.0, 0.03 * amp))
    t = np.linspace(0, N_PERIODS / freq, N_SAMPLE_POINTS, endpoint=False)
    phase = (freq * t) % 1.0
    saw = 2.0 * phase - 1.0
    v = offset + amp * saw
    v += rng.normal(0, noise_std, size=len(t))
    return t, v

_WAVEFORM_GENS = {"sine": _gen_sine, "square": _gen_square,
                  "triangle": _gen_triangle, "sawtooth": _gen_sawtooth}

def gen_waveform(wtype, rng):
    return _WAVEFORM_GENS[wtype](rng)


# ============================================================================ #
#  2. PROMPT FORMATTING (ChatML, matching existing codebase)
# ============================================================================ #

def _fmt_val(v):
    if abs(v) < 1e-4 and v != 0: return f"{v:.2e}"
    return f"{v:.3f}"

def format_samples(t, v):
    pairs = [f"({_fmt_val(ti)}, {_fmt_val(vi)})" for ti, vi in zip(t, v)]
    lines = []
    for i in range(0, len(pairs), 4):
        lines.append(", ".join(pairs[i:i+4]))
    return ",\n".join(lines)

def build_prompt_text(samples_text):
    user_msg = (f"Classify this waveform as sine, square, triangle, or sawtooth.\n"
                f"Sample points (time_us, voltage_V):\n{samples_text}")
    return (f"{IM_START}system\n{SYSTEM_PROMPT}{IM_END}\n"
            f"{IM_START}user\n{user_msg}{IM_END}\n"
            f"{IM_START}assistant\n")

def build_sft_text(samples_text, label):
    return build_prompt_text(samples_text) + f"{label}{IM_END}\n"


# ============================================================================ #
#  3. EVAL / TRAIN DATA GENERATION
# ============================================================================ #

def gen_question(wtype, qid, seed):
    rng = np.random.default_rng(seed)
    t, v = gen_waveform(wtype, rng)
    return {"qid": qid, "task": "type_classification", "waveform_type": wtype,
            "gt_value": wtype, "measure_type": "type_classification",
            "samples_text": format_samples(t, v)}

def build_eval_set(n_per_type=25, seed_base=EVAL_SEED_BASE):
    questions = []; qid = 0
    for wtype in WAVEFORM_TYPES:
        for i in range(n_per_type):
            seed = seed_base + qid * 100 + hash(wtype) % 1000
            q = gen_question(wtype, qid, seed)
            questions.append(q); qid += 1
    return questions

def build_sft_dataset(n, seed_base=TRAIN_SEED_BASE):
    examples = []; per_type = n // len(WAVEFORM_TYPES)
    remainder = n % len(WAVEFORM_TYPES)
    for i, wtype in enumerate(WAVEFORM_TYPES):
        count = per_type + (1 if i < remainder else 0)
        for j in range(count):
            seed = seed_base + i * 10000 + j
            r = np.random.default_rng(seed)
            t, v = gen_waveform(wtype, r)
            samples_text = format_samples(t, v)
            examples.append({"waveform_type": wtype, "gt_value": wtype,
                             "samples_text": samples_text,
                             "sft_text": build_sft_text(samples_text, wtype)})
    random.shuffle(examples)
    return examples


# ============================================================================ #
#  4. MODEL LOADING
# ============================================================================ #

def build_model(model_path, device, dtype, lora_r=16, lora_alpha=32, sft_ckpt=None):
    print(f"  Loading base LLM: {model_path}", flush=True)
    llm = AutoModelForCausalLM.from_pretrained(
        model_path, torch_dtype=dtype, device_map={'': device}, trust_remote_code=True)
    if sft_ckpt and os.path.isdir(sft_ckpt):
        print(f"  Loading SFT adapter: {sft_ckpt}", flush=True)
        model = PeftModel.from_pretrained(llm, sft_ckpt, is_trainable=True)
    else:
        lora_config = LoraConfig(task_type=TaskType.CAUSAL_LM, r=lora_r,
            lora_alpha=lora_alpha, lora_dropout=0.05,
            target_modules=["q_proj","k_proj","v_proj","o_proj"])
        model = get_peft_model(llm, lora_config)
    n_train = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"  Trainable params: {n_train/1e6:.1f}M", flush=True)
    return model


# ============================================================================ #
#  5. SFT TRAINING (cross-entropy on assistant tokens)
# ============================================================================ #

def compute_assistant_mask(tokenizer, full_text, label):
    asst_marker = f"{IM_START}assistant\n"
    asst_start = full_text.rfind(asst_marker)
    if asst_start < 0: return []
    resp_start = asst_start + len(asst_marker)
    prefix = full_text[:resp_start]
    prefix_ids = tokenizer(prefix, add_special_tokens=False)["input_ids"]
    full_ids = tokenizer(full_text, add_special_tokens=False)["input_ids"]
    n_prefix = len(prefix_ids)
    mask = [False] * n_prefix + [True] * (len(full_ids) - n_prefix)
    return mask[:len(full_ids)]

def sft_train(model, tokenizer, examples, device, dtype, n_epochs=3,
              batch_size=8, lr=5e-6, label="SFT"):
    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad], lr=lr)
    print(f"  [{label}] Tokenizing {len(examples)} examples...", flush=True)
    tokenized = []
    for ex in examples:
        ids = tokenizer(ex["sft_text"], add_special_tokens=False,
                        return_tensors=None, truncation=True, max_length=1024)["input_ids"]
        mask = compute_assistant_mask(tokenizer, ex["sft_text"], ex["gt_value"])
        if sum(mask) > 0:
            tokenized.append({"input_ids": ids, "assistant_mask": mask})
    print(f"  [{label}] {len(tokenized)} valid, training {n_epochs} epochs", flush=True)
    losses = []; t0 = time.time(); step = 0
    for epoch in range(n_epochs):
        random.shuffle(tokenized)
        for i in range(0, len(tokenized), batch_size):
            batch = tokenized[i:i+batch_size]
            max_len = max(len(b["input_ids"]) for b in batch)
            input_ids = torch.zeros(len(batch), max_len, dtype=torch.long, device=device)
            attn_mask = torch.zeros(len(batch), max_len, dtype=torch.long, device=device)
            asst_mask = torch.zeros(len(batch), max_len, dtype=torch.bool, device=device)
            for j, b in enumerate(batch):
                L = len(b["input_ids"])
                input_ids[j, :L] = torch.tensor(b["input_ids"])
                attn_mask[j, :L] = 1
                am = b["assistant_mask"]
                asst_mask[j, :len(am)] = torch.tensor(am)
            with torch.autocast(device.type, dtype=dtype, enabled=False):
                logits = model(input_ids=input_ids, attention_mask=attn_mask).logits
            log_probs = F.log_softmax(logits[:, :-1, :].float(), dim=-1)
            target_ids = input_ids[:, 1:]
            token_lps = log_probs.gather(2, target_ids.unsqueeze(-1)).squeeze(-1)
            shifted_mask = asst_mask[:, 1:]
            masked_lps = token_lps[shifted_mask]
            if masked_lps.numel() == 0: continue
            loss = -masked_lps.mean()
            optimizer.zero_grad(); loss.backward(); optimizer.step()
            losses.append(float(loss.item())); step += 1
            if step % 20 == 0 or step == 1:
                avg = sum(losses[-20:]) / min(len(losses), 20)
                print(f"    [{label}] ep{epoch+1}/{n_epochs} step{step} "
                      f"loss={loss.item():.4f} avg={avg:.4f} ({time.time()-t0:.0f}s)", flush=True)
    print(f"  [{label}] DONE: {step} steps, final avg={sum(losses[-20:])/min(20,len(losses)):.4f}", flush=True)
    return losses


# ============================================================================ #
#  6. ROLLOUT + REWARD
# ============================================================================ #

_TYPE_RE = re.compile(r'\b(sine|square|triangle|sawtooth)\b', re.IGNORECASE)

def rollout_classify(model, tokenizer, question, device, dtype,
                     max_new_tokens=16, temperature=0.0):
    prompt_text = build_prompt_text(question["samples_text"])
    enc = tokenizer(prompt_text, add_special_tokens=False,
                    return_tensors='pt', truncation=True, max_length=1024)
    input_ids = enc['input_ids'].to(device)
    with torch.no_grad():
        out = model.generate(input_ids, max_new_tokens=max_new_tokens,
            do_sample=temperature > 0, temperature=max(temperature, 1e-5),
            top_p=0.95,
            pad_token_id=tokenizer.pad_token_id if tokenizer.pad_token_id is not None else 0,
            eos_token_id=tokenizer.convert_tokens_to_ids(IM_END))
    new_tokens = out[0, input_ids.shape[1]:]
    gen_text = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
    m = _TYPE_RE.search(gen_text)
    parsed = m.group(1).lower() if m else None
    return parsed, gen_text

def check_correct(question, parsed_type):
    if parsed_type is None: return False
    return parsed_type.lower() == str(question["gt_value"]).lower()

def classification_reward(question, parsed_type):
    return 1.0 if check_correct(question, parsed_type) else 0.0


# ============================================================================ #
#  7. EVALUATION
# ============================================================================ #

def evaluate_condition(model, tokenizer, questions, device, dtype, label,
                       max_new_tokens=16):
    results = []; t0 = time.time()
    for i, q in enumerate(questions):
        parsed, raw = rollout_classify(model, tokenizer, q, device, dtype,
                                       max_new_tokens=max_new_tokens, temperature=0.0)
        correct = check_correct(q, parsed)
        results.append({"qid": q["qid"], "task": q["task"],
                        "waveform_type": q["waveform_type"],
                        "correct": correct, "parsed": parsed,
                        "gt": q["gt_value"], "raw_output": raw[:100]})
        if (i + 1) % 10 == 0:
            acc = sum(r["correct"] for r in results) / len(results)
            print(f"    [{label}] {i+1}/{len(questions)} acc={acc:.1%} ({time.time()-t0:.0f}s)", flush=True)
    return results

def eval_confusion_matrix(results):
    cm = {gt: {pred: 0 for pred in WAVEFORM_TYPES + ["None"]} for gt in WAVEFORM_TYPES}
    for r in results:
        gt = r["waveform_type"]; pred = r["parsed"] if r["parsed"] else "None"
        if pred not in cm[gt]: cm[gt][pred] = 0
        cm[gt][pred] += 1
    per_class = {}
    for gt in WAVEFORM_TYPES:
        total = sum(cm[gt].values())
        per_class[gt] = cm[gt][gt] / total if total > 0 else 0.0
    return {"confusion_matrix": cm, "per_class_accuracy": per_class}


# ============================================================================ #
#  8. RFT (Rejection Sampling Fine-Tuning)
# ============================================================================ #

def collect_rollouts_rft(model, tokenizer, train_questions, device, dtype,
                         k=3, temperature=0.8, label="RFT-collect"):
    all_rollouts = []; t0 = time.time()
    for i, q in enumerate(train_questions):
        for _ in range(k):
            parsed, raw = rollout_classify(model, tokenizer, q, device, dtype,
                                           max_new_tokens=16, temperature=temperature)
            reward = classification_reward(q, parsed)
            all_rollouts.append({"qid": q["qid"], "waveform_type": q["waveform_type"],
                                 "samples_text": q["samples_text"], "gt_value": q["gt_value"],
                                 "parsed": parsed, "raw": raw, "reward": reward,
                                 "correct": reward > 0.5})
        if (i + 1) % 50 == 0:
            n_correct = sum(r["correct"] for r in all_rollouts)
            print(f"    [{label}] {i+1}/{len(train_questions)} Q, {len(all_rollouts)} rollouts, "
                  f"{n_correct} correct ({n_correct/len(all_rollouts):.1%}) ({time.time()-t0:.0f}s)", flush=True)
    return all_rollouts

def filter_and_build_sft(rollouts, random_filter=False, rng_seed=42):
    rng = np.random.default_rng(rng_seed)
    if random_filter:
        n_correct = sum(1 for r in rollouts if r["correct"])
        selected = list(rng.choice(len(rollouts), size=min(n_correct, len(rollouts)), replace=False))
        selected_rollouts = [rollouts[int(i)] for i in selected]
    else:
        selected_rollouts = [r for r in rollouts if r["correct"]]
    examples = []
    for r in selected_rollouts:
        label_text = r["parsed"] if r["parsed"] else r["gt_value"]
        examples.append({"waveform_type": r["waveform_type"], "gt_value": r["gt_value"],
                         "samples_text": r["samples_text"],
                         "sft_text": build_sft_text(r["samples_text"], label_text)})
    return examples


# ============================================================================ #
#  9. STATISTICS
# ============================================================================ #

def mcnemar_test(correct_a, correct_b):
    a = np.array(correct_a, dtype=bool); b = np.array(correct_b, dtype=bool)
    n = min(len(a), len(b)); a, b = a[:n], b[:n]
    b01 = int(np.sum((~a) & b)); b10 = int(np.sum(a & (~b))); n_disc = b01 + b10
    if n_disc == 0: return 0.0, 1.0, 0
    if n_disc < 25:
        from math import comb; k = min(b01, b10)
        p = 2.0 * sum(comb(n_disc, i) for i in range(0, k + 1)) / (2 ** n_disc)
        return float(n_disc), min(p, 1.0), n_disc
    else:
        stat = (abs(b01 - b10) - 1) ** 2 / max(n_disc, 1)
        from math import erfc, sqrt; p = float(erfc(sqrt(stat / 2)))
        return float(stat), p, n_disc

def bootstrap_ci_delta(correct_a, correct_b, n_boot=10000, seed=42):
    rng = np.random.default_rng(seed)
    a = np.array(correct_a, dtype=float); b = np.array(correct_b, dtype=float)
    n = min(len(a), len(b)); a, b = a[:n], b[:n]
    deltas = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        deltas.append(b[idx].mean() - a[idx].mean())
    deltas = np.array(deltas)
    return float(b.mean()-a.mean()), float(np.percentile(deltas, 2.5)), float(np.percentile(deltas, 97.5))


# ============================================================================ #
#  10. MAIN EXPERIMENT
# ============================================================================ #

def main():
    p = argparse.ArgumentParser(description="CPU RL v5: Waveform Type Classification")
    p.add_argument('--model_path', type=str, default=LLM_PATH)
    p.add_argument('--out_dir', type=str,
        default="/nas_train/app.e0031982/datasets/baize-vision/out/cpu_rl_v5_typecls")
    p.add_argument('--n_eval_per_type', type=int, default=25)
    p.add_argument('--n_sft', type=int, default=400)
    p.add_argument('--n_rft_train', type=int, default=200)
    p.add_argument('--rft_k', type=int, default=3)
    p.add_argument('--sft_epochs', type=int, default=3)
    p.add_argument('--rft_epochs', type=int, default=3)
    p.add_argument('--batch_size', type=int, default=8)
    p.add_argument('--lr', type=float, default=5e-6)
    p.add_argument('--lora_r', type=int, default=16)
    p.add_argument('--max_new_tokens', type=int, default=16)
    p.add_argument('--skip_baseline', action='store_true')
    p.add_argument('--skip_control', action='store_true')
    p.add_argument('--smoke', action='store_true')
    args = p.parse_args()

    os.environ.setdefault("OMP_NUM_THREADS", "16")
    device = torch.device('cpu'); dtype = torch.float32
    os.makedirs(args.out_dir, exist_ok=True)

    if args.smoke:
        args.n_eval_per_type = 5; args.n_sft = 20; args.n_rft_train = 10
        args.rft_k = 2; args.sft_epochs = 1; args.rft_epochs = 1
        print("=== SMOKE TEST MODE (tiny n) ===", flush=True)

    # Phase 0: Eval set
    print("=" * 60, flush=True)
    print("[Phase 0] Building eval set", flush=True)
    eval_questions = build_eval_set(n_per_type=args.n_eval_per_type)
    print(f"  {len(eval_questions)} eval questions ({args.n_eval_per_type}/type)", flush=True)
    with open(os.path.join(args.out_dir, "eval_questions.json"), 'w') as f:
        json.dump(eval_questions, f, indent=2, default=str)

    # Phase 1: SFT data
    print("=" * 60, flush=True)
    print("[Phase 1] Building SFT training data", flush=True)
    sft_examples = build_sft_dataset(args.n_sft)
    type_counts = {}
    for ex in sft_examples:
        type_counts[ex["waveform_type"]] = type_counts.get(ex["waveform_type"], 0) + 1
    print(f"  {len(sft_examples)} SFT examples, balance: {type_counts}", flush=True)

    # Phase 2: SFT Training (Condition B)
    print("=" * 60, flush=True)
    print("[Phase 2] SFT training (Condition B)", flush=True)
    model_b = build_model(args.model_path, device, dtype, lora_r=args.lora_r)
    tokenizer = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    losses_b = sft_train(model_b, tokenizer, sft_examples, device, dtype,
                         n_epochs=args.sft_epochs, batch_size=args.batch_size,
                         lr=args.lr, label="SFT-B")
    sft_save = os.path.join(args.out_dir, "sft_adapter")
    model_b.save_pretrained(sft_save)
    print(f"  SFT adapter saved to {sft_save}", flush=True)

    # Phase 3: Eval A (baseline) + B (SFT)
    print("=" * 60, flush=True)
    print("[Phase 3] Evaluation: A (baseline) + B (SFT)", flush=True)
    res_a = []; acc_a = 0.0
    if not args.skip_baseline:
        print("  Evaluating A (baseline, fresh LoRA)...", flush=True)
        model_a = build_model(args.model_path, device, dtype, lora_r=args.lora_r)
        res_a = evaluate_condition(model_a, tokenizer, eval_questions, device, dtype,
                                   "A-base", max_new_tokens=args.max_new_tokens)
        acc_a = sum(r["correct"] for r in res_a) / len(res_a)
        print(f"  A (baseline) accuracy: {acc_a:.1%}", flush=True)
        del model_a
    else:
        print("  A (baseline) SKIPPED", flush=True)

    print("  Evaluating B (SFT)...", flush=True)
    res_b = evaluate_condition(model_b, tokenizer, eval_questions, device, dtype,
                               "B-sft", max_new_tokens=args.max_new_tokens)
    acc_b = sum(r["correct"] for r in res_b) / len(res_b)
    print(f"  B (SFT) accuracy: {acc_b:.1%}", flush=True)
    cm_b = eval_confusion_matrix(res_b)
    print(f"  B per-class: {cm_b['per_class_accuracy']}", flush=True)

    # Phase 4: RFT
    print("=" * 60, flush=True)
    print("[Phase 4] RFT: Condition C (treatment) + D (control)", flush=True)
    rft_examples = build_sft_dataset(args.n_rft_train, seed_base=TRAIN_SEED_BASE + 50000)
    rft_questions = [{"qid": 10000+i, "task": "type_classification",
                      "waveform_type": ex["waveform_type"], "gt_value": ex["gt_value"],
                      "samples_text": ex["samples_text"]} for i, ex in enumerate(rft_examples)]
    print(f"  Collecting {args.rft_k} rollouts/Q ({len(rft_questions)} Q)...", flush=True)
    all_rollouts = collect_rollouts_rft(model_b, tokenizer, rft_questions, device, dtype,
                                        k=args.rft_k, temperature=0.8, label="RFT-collect")
    n_correct = sum(r["correct"] for r in all_rollouts)
    print(f"  {len(all_rollouts)} rollouts, {n_correct} correct ({n_correct/len(all_rollouts):.1%})", flush=True)
    del model_b

    # Condition C: RFT correct-filter
    print("  Training C (RFT, correct filter)...", flush=True)
    train_c = filter_and_build_sft(all_rollouts, random_filter=False)
    print(f"  C training examples: {len(train_c)}", flush=True)
    model_c = build_model(args.model_path, device, dtype, lora_r=args.lora_r, sft_ckpt=sft_save)
    losses_c = sft_train(model_c, tokenizer, train_c, device, dtype,
                         n_epochs=args.rft_epochs, batch_size=args.batch_size,
                         lr=args.lr, label="RFT-C")
    res_c = evaluate_condition(model_c, tokenizer, eval_questions, device, dtype,
                               "C-rft", max_new_tokens=args.max_new_tokens)
    acc_c = sum(r["correct"] for r in res_c) / len(res_c)
    print(f"  C (RFT treatment) accuracy: {acc_c:.1%}", flush=True)
    del model_c

    # Condition D: RFT random-filter (CONTROL)
    res_d = []; acc_d = 0.0; losses_d = []
    if not args.skip_control:
        print("  Training D (RFT, random filter = CONTROL)...", flush=True)
        train_d = filter_and_build_sft(all_rollouts, random_filter=True, rng_seed=12345)
        print(f"  D training examples: {len(train_d)}", flush=True)
        model_d = build_model(args.model_path, device, dtype, lora_r=args.lora_r, sft_ckpt=sft_save)
        losses_d = sft_train(model_d, tokenizer, train_d, device, dtype,
                             n_epochs=args.rft_epochs, batch_size=args.batch_size,
                             lr=args.lr, label="RFT-D")
        res_d = evaluate_condition(model_d, tokenizer, eval_questions, device, dtype,
                                   "D-ctrl", max_new_tokens=args.max_new_tokens)
        acc_d = sum(r["correct"] for r in res_d) / len(res_d)
        print(f"  D (RFT control) accuracy: {acc_d:.1%}", flush=True)
        del model_d
    else:
        print("  D (control) SKIPPED", flush=True)

    # Phase 5: Statistics
    print("=" * 60, flush=True)
    print("[Phase 5] Statistical analysis", flush=True)
    corr_b = [r["correct"] for r in res_b]; corr_c = [r["correct"] for r in res_c]
    stats = {"accuracy": {"A_baseline": acc_a, "B_sft": acc_b, "C_rft_treatment": acc_c},
             "B_confusion_matrix": cm_b}
    if res_d:
        corr_d = [r["correct"] for r in res_d]; stats["accuracy"]["D_rft_control"] = acc_d
    if res_a:
        corr_a = [r["correct"] for r in res_a]

    stat_cb, p_cb, ndisc_cb = mcnemar_test(corr_b, corr_c)
    pt_cb, lo_cb, hi_cb = bootstrap_ci_delta(corr_b, corr_c)
    stats["mcnemar_C_vs_B"] = {"stat": stat_cb, "p": p_cb, "n_discordant": ndisc_cb}
    stats["bootstrap_C_vs_B"] = {"point_delta": pt_cb, "ci_lo": lo_cb, "ci_hi": hi_cb}
    if res_d:
        stat_cd, p_cd, ndisc_cd = mcnemar_test(corr_d, corr_c)
        pt_cd, lo_cd, hi_cd = bootstrap_ci_delta(corr_d, corr_c)
        stats["mcnemar_C_vs_D"] = {"stat": stat_cd, "p": p_cd, "n_discordant": ndisc_cd}
        stats["bootstrap_C_vs_D"] = {"point_delta": pt_cd, "ci_lo": lo_cd, "ci_hi": hi_cd}
    if res_a:
        stat_ba, p_ba, ndisc_ba = mcnemar_test(corr_a, corr_b)
        pt_ba, lo_ba, hi_ba = bootstrap_ci_delta(corr_a, corr_b)
        stats["mcnemar_B_vs_A"] = {"stat": stat_ba, "p": p_ba, "n_discordant": ndisc_ba}
        stats["bootstrap_B_vs_A"] = {"point_delta": pt_ba, "ci_lo": lo_ba, "ci_hi": hi_ba}
    stats["cheat_rate"] = {"train_seed_range": f"{TRAIN_SEED_BASE}+{args.n_sft}",
        "eval_seed_range": f"{EVAL_SEED_BASE}+", "overlap": 0, "overlap_frac": 0.0,
        "note": "train/eval use disjoint RNG seed ranges -> no data leakage"}
    stats["collection_stats"] = {"n_total_rollouts": len(all_rollouts),
        "n_successful": n_correct, "success_rate": n_correct / max(len(all_rollouts), 1)}

    sig_cb = p_cb < 0.05 and lo_cb > 0
    verdict = ("TREATMENT SIGNIFICANT" if sig_cb else
               "TREATMENT NOT SIGNIFICANT" if acc_c > acc_b else "NO IMPROVEMENT")
    if res_d and acc_c > acc_d: verdict += " | REWARD-DESIGN DRIVEN (C>D)"
    elif res_d: verdict += " | NOT reward-design driven (C<=D)"
    stats["verdict"] = verdict
    stats["pre_registered_judgment"] = {"C>B": acc_c > acc_b,
        "C>D_reward_design": (acc_c > acc_d) if res_d else None,
        "C_vs_B_sig": sig_cb, "B>A": acc_b > acc_a if res_a else None}

    print(f"\n{'='*60}", flush=True)
    print(f"  RESULTS SUMMARY (v5: Waveform Type Classification)", flush=True)
    if res_a: print(f"  A (baseline):              {acc_a:.1%}", flush=True)
    print(f"  B (SFT):                   {acc_b:.1%}", flush=True)
    print(f"  C (RFT treatment):         {acc_c:.1%}", flush=True)
    if res_d: print(f"  D (RFT random control):    {acc_d:.1%}", flush=True)
    print(f"  B per-class: {cm_b['per_class_accuracy']}", flush=True)
    print(f"  McNemar C vs B: p={p_cb:.4f} (n_disc={ndisc_cb})", flush=True)
    print(f"  Bootstrap C-B: {pt_cb:+.1%} CI=[{lo_cb:+.1%},{hi_cb:+.1%}]", flush=True)
    if res_d: print(f"  McNemar C vs D: p={p_cd:.4f} (n_disc={ndisc_cd})", flush=True)
    print(f"  VERDICT: {verdict}", flush=True)

    out = {"config": vars(args), "stats": stats,
           "results": {"A": res_a, "B": res_b, "C": res_c},
           "training": {"B_losses": losses_b, "C_losses": losses_c}}
    if res_d:
        out["results"]["D"] = res_d; out["training"]["D_losses"] = losses_d
    out_path = os.path.join(args.out_dir, "experiment_results.json")
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\n  Full results -> {out_path}", flush=True)

if __name__ == "__main__":
    main()
