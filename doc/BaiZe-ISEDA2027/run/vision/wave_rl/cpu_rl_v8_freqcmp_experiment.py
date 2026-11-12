#!/usr/bin/env python3
"""cpu_rl_v8_freqcmp_experiment.py - CPU RL Waveform Experiment v8: Frequency Comparison.

WHY v8 (new task dimension, addressing v7 gaps):
  v5-v7 all use 4-class TYPE CLASSIFICATION (sine/square/triangle/sawtooth).
  v5 showed significant improvement (A=16% -> B=37% -> C=53%, p=0.0009).
  v6/v7 explored reward design (continuous, process reward).
  BUT: triangle/sawtooth = 0% across ALL v7 variants. The model only
  distinguishes sine vs square. support@2/@3 = 2.1% (high variance).

  v8 introduces a NEW TASK: FREQUENCY COMPARISON.
  - Given two waveforms (A, B) with 16 sample points each over a FIXED
    1-microsecond window, which has higher frequency?
  - Binary task (A or B), 50% chance baseline.
  - Fixed time window => model must count oscillation cycles from voltage
    samples, cannot cheat by reading the time axis.
  - Mix of same-type and cross-type pairs => tests frequency discrimination,
    not type classification.
  - Complements v5-v7: different dimension of waveform understanding.

PRE-REGISTERED JUDGMENT (written BEFORE running, 2026-11-12):
  A (zero-shot, fresh LoRA):  ~50% (random chance, binary)
  B (SFT on freq comparison):  >60% (frequency discrimination is learnable)
  C (GRPO on top of B):        >B (RL refines frequency discrimination)
  D (GRPO with random reward):  <= B (control, random reward doesn't help)
  SUCCESS: C > B, McNemar p < 0.05, 3 seeds all C > B (same direction)
  FAIL:    C <= B OR p >= 0.05 OR seeds not consistent

Author: vision (v8 new task dimension). License: project-internal.
"""
from __future__ import annotations
import sys, os, json, time, math, random, argparse, re, gc
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model, TaskType, PeftModel

LLM_PATH = "/nas_train/app.e0031982/datasets/baize-vision/out/wave_sft_stage1w/qwen3vl_2b_text_extracted"
WAVEFORM_TYPES = ["sine", "square", "triangle", "sawtooth"]
N_SAMPLE_POINTS = 16
TIME_WINDOW = 1.0
FREQ_MIN = 1.0
FREQ_MAX = 8.0
MIN_FREQ_RATIO = 1.2
EVAL_SEED_BASE = 995200
TRAIN_SEED_BASE = 20261112
IM_START = "<|im_start|>"
IM_END = "<|im_end|>"

SYSTEM_PROMPT = (
    "You are a waveform analysis expert. You are given two waveforms "
    "(A and B), each represented by 16 evenly-spaced voltage samples "
    "over a fixed 1-microsecond time window. Determine which waveform "
    "has a higher oscillation frequency. Respond with only 'A' or 'B'."
)

# ============================================================================
#  1. WAVEFORM GENERATORS (fixed time window)
# ============================================================================

_T_FIXED = np.linspace(0, TIME_WINDOW, N_SAMPLE_POINTS, endpoint=False)


def _gen_sine(rng, freq):
    amp = float(rng.uniform(0.5, 5.0)); off = float(rng.uniform(-2.0, 2.0))
    ph = float(rng.uniform(0, 2 * math.pi))
    ns = float(rng.uniform(0.0, 0.03 * amp))
    v = off + amp * np.sin(2 * math.pi * freq * _T_FIXED + ph)
    v += rng.normal(0, ns, size=len(_T_FIXED))
    return v, {"amp": amp, "offset": off, "freq": freq, "phase": ph, "noise_std": ns}


def _gen_square(rng, freq):
    amp = float(rng.uniform(0.5, 5.0)); off = float(rng.uniform(-2.0, 2.0))
    duty = float(rng.uniform(0.3, 0.7)); ns = float(rng.uniform(0.0, 0.03 * amp))
    pic = (freq * _T_FIXED) % 1.0
    v = np.where(pic < duty, off + amp, off - amp)
    v += rng.normal(0, ns, size=len(_T_FIXED))
    return v, {"amp": amp, "offset": off, "freq": freq, "duty": duty, "noise_std": ns}


def _gen_triangle(rng, freq):
    amp = float(rng.uniform(0.5, 5.0)); off = float(rng.uniform(-2.0, 2.0))
    ns = float(rng.uniform(0.0, 0.03 * amp))
    ph = (freq * _T_FIXED) % 1.0
    tri = np.where(ph < 0.5, 4.0 * ph - 1.0, 3.0 - 4.0 * ph)
    v = off + amp * tri + rng.normal(0, ns, size=len(_T_FIXED))
    return v, {"amp": amp, "offset": off, "freq": freq, "noise_std": ns}


def _gen_sawtooth(rng, freq):
    amp = float(rng.uniform(0.5, 5.0)); off = float(rng.uniform(-2.0, 2.0))
    ns = float(rng.uniform(0.0, 0.03 * amp))
    ph = (freq * _T_FIXED) % 1.0
    v = off + amp * (2.0 * ph - 1.0) + rng.normal(0, ns, size=len(_T_FIXED))
    return v, {"amp": amp, "offset": off, "freq": freq, "noise_std": ns}


_WAVEFORM_GENS = {"sine": _gen_sine, "square": _gen_square,
                  "triangle": _gen_triangle, "sawtooth": _gen_sawtooth}


def gen_waveform_v(wtype, rng, freq):
    return _WAVEFORM_GENS[wtype](rng, freq)

# ============================================================================
#  2. PAIR GENERATION + GATING
# ============================================================================

def _fmt_val(v):
    if abs(v) < 1e-4 and v != 0:
        return f"{v:.2e}"
    return f"{v:.3f}"


def format_samples_v(v):
    return ", ".join(_fmt_val(vi) for vi in v)


def format_pair_samples(v_a, v_b):
    t_str = ", ".join(_fmt_val(ti) for ti in _T_FIXED)
    v_a_str = format_samples_v(v_a)
    v_b_str = format_samples_v(v_b)
    return t_str, v_a_str, v_b_str


def gen_pair(pair_id, seed, same_type=None, difficulty=None):
    """Generate a frequency comparison pair."""
    rng = np.random.default_rng(seed)
    if same_type is None:
        same_type = bool(rng.random() < 0.5)
    if same_type:
        wt_a = WAVEFORM_TYPES[int(rng.integers(0, len(WAVEFORM_TYPES)))]
        wt_b = wt_a
    else:
        idx_a, idx_b = rng.choice(len(WAVEFORM_TYPES), size=2, replace=False)
        wt_a = WAVEFORM_TYPES[int(idx_a)]
        wt_b = WAVEFORM_TYPES[int(idx_b)]
    if difficulty is None:
        difficulty = str(rng.choice(["easy", "medium", "hard"]))
    freq_lo = float(rng.uniform(FREQ_MIN, FREQ_MAX * 0.6))
    if difficulty == "easy":
        ratio = float(rng.uniform(2.0, 4.0))
    elif difficulty == "medium":
        ratio = float(rng.uniform(1.5, 2.0))
    else:
        ratio = float(rng.uniform(MIN_FREQ_RATIO, 1.5))
    freq_hi = min(freq_lo * ratio, FREQ_MAX)
    if freq_hi <= freq_lo * MIN_FREQ_RATIO:
        return None
    if rng.random() < 0.5:
        freq_a, freq_b = freq_hi, freq_lo
        answer = "A"
    else:
        freq_a, freq_b = freq_lo, freq_hi
        answer = "B"
    v_a, params_a = gen_waveform_v(wt_a, rng, freq_a)
    v_b, params_b = gen_waveform_v(wt_b, rng, freq_b)
    ptp_a = float(np.max(v_a) - np.min(v_a))
    ptp_b = float(np.max(v_b) - np.min(v_b))
    if ptp_a < 0.3 * params_a["amp"] or ptp_b < 0.3 * params_b["amp"]:
        return None
    t_str, v_a_str, v_b_str = format_pair_samples(v_a, v_b)
    return {
        "qid": pair_id, "task": "frequency_comparison",
        "waveform_type_a": wt_a, "waveform_type_b": wt_b,
        "freq_a": freq_a, "freq_b": freq_b,
        "freq_ratio": max(freq_a, freq_b) / min(freq_a, freq_b),
        "same_type": same_type, "difficulty": difficulty,
        "gt_value": answer, "t_str": t_str,
        "v_a_str": v_a_str, "v_b_str": v_b_str,
        "v_a": v_a.tolist(), "v_b": v_b.tolist(),
    }


def gen_pair_gated(pair_id, seed, same_type=None, difficulty=None, max_retries=10):
    return None

# ============================================================================
#  3. PROMPT FORMATTING
# ============================================================================

def build_prompt_text(pair):
    user_msg = (
        f"Two waveforms are sampled at the same 16 time points "
        f"over a 1-microsecond window.\n\n"
        f"Time points (us): {pair['t_str']}\n\n"
        f"Waveform A voltages (V): {pair['v_a_str']}\n\n"
        f"Waveform B voltages (V): {pair['v_b_str']}\n\n"
        f"Which waveform has a higher oscillation frequency? "
        f"Respond with only 'A' or 'B'."
    )
    return (f"{IM_START}system\n{SYSTEM_PROMPT}{IM_END}\n"
            f"{IM_START}user\n{user_msg}{IM_END}\n"
            f"{IM_START}assistant\n")


def build_sft_text(pair):
    return build_prompt_text(pair) + f"{pair['gt_value']}{IM_END}\n"

# ============================================================================
#  4. EVAL / TRAIN DATA GENERATION
# ============================================================================

def build_eval_set(n_per_category=8):
    """48 pairs: 3 difficulties x 2 type conditions x 8 pairs."""
    questions = []; qid = 0
    for difficulty in ["easy", "medium", "hard"]:
        for same_type in [True, False]:
            for i in range(n_per_category):
                seed = EVAL_SEED_BASE + qid * 100
                p = gen_pair_gated(qid, seed, same_type=same_type, difficulty=difficulty)
                if p is None:
                    p = gen_pair(qid, seed, same_type=same_type, difficulty=difficulty)
                if p:
                    questions.append(p); qid += 1
    return questions


def build_sft_dataset(n=200, seed_base=TRAIN_SEED_BASE):
    examples = []; per = n // 4; qid = 0
    configs = [(True, "easy"), (True, "medium"), (True, "hard"), (False, None)]
    counts = [per] * 3 + [n - 3 * per]
    for (st, diff), cnt in zip(configs, counts):
        for j in range(cnt):
            seed = seed_base + qid * 100
            p = gen_pair_gated(qid, seed, same_type=st, difficulty=diff)
            if p is None:
                p = gen_pair(qid, seed, same_type=st, difficulty=diff)
            if p:
                p["sft_text"] = build_sft_text(p)
                examples.append(p); qid += 1
    random.shuffle(examples)
    return examples


def build_train_set(n=100, seed_base=TRAIN_SEED_BASE + 100000):
    questions = []; qid = 0
    for j in range(n):
        seed = seed_base + qid * 100
        p = gen_pair_gated(qid, seed)
        if p is None:
            p = gen_pair(qid, seed)
        if p:
            questions.append(p); qid += 1
    return questions

# ============================================================================
#  5. MODEL LOADING (same as v5-v7)
# ============================================================================

def build_model(model_path, device, dtype, lora_r=16, lora_alpha=32, sft_ckpt=None):
    print(f"  Loading base LLM: {model_path}", flush=True)
    llm = AutoModelForCausalLM.from_pretrained(
        model_path, torch_dtype=dtype, device_map={'': device}, trust_remote_code=True)
    if sft_ckpt and os.path.isdir(sft_ckpt):
        print(f"  Loading SFT adapter: {sft_ckpt}", flush=True)
        model = PeftModel.from_pretrained(llm, sft_ckpt, is_trainable=True)
    else:
        lc = LoraConfig(task_type=TaskType.CAUSAL_LM, r=lora_r, lora_alpha=lora_alpha,
                        lora_dropout=0.05, target_modules=["q_proj", "k_proj", "v_proj", "o_proj"])
        model = get_peft_model(llm, lc)
    nt = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"  Trainable params: {nt / 1e6:.1f}M (LoRA r={lora_r})", flush=True)
    return model

# ============================================================================
#  6. SFT TRAINING (cross-entropy on assistant tokens)
# ============================================================================

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
            batch = tokenized[i:i + batch_size]
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
            logits = model(input_ids=input_ids, attention_mask=attn_mask).logits
            log_probs = F.log_softmax(logits[:, :-1, :].float(), dim=-1)
            token_lps = log_probs.gather(2, input_ids[:, 1:].unsqueeze(-1)).squeeze(-1)
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

# ============================================================================
#  7. ROLLOUT + REWARD (frequency comparison)
# ============================================================================

_ANSWER_RE = re.compile(r'\b([AB])\b')

def rollout_compare(model, tokenizer, pair, device, dtype,
                    max_new_tokens=8, temperature=0.0):
    prompt_text = build_prompt_text(pair)
    enc = tokenizer(prompt_text, add_special_tokens=False,
                    return_tensors='pt', truncation=True, max_length=1024)
    ids = enc['input_ids'].to(device)
    with torch.no_grad():
        out = model.generate(ids, max_new_tokens=max_new_tokens,
                             do_sample=temperature > 0,
                             temperature=max(temperature, 1e-5), top_p=0.95,
                             pad_token_id=tokenizer.pad_token_id if tokenizer.pad_token_id is not None else 0,
                             eos_token_id=tokenizer.convert_tokens_to_ids(IM_END))
    gen = tokenizer.decode(out[0, ids.shape[1]:], skip_special_tokens=True).strip()
    m = _ANSWER_RE.search(gen)
    parsed = m.group(1).upper() if m else None
    return parsed, gen


def check_correct(pair, parsed):
    if parsed is None: return False
    return parsed.upper() == str(pair["gt_value"]).upper()


def binary_reward(pair, parsed):
    return 1.0 if check_correct(pair, parsed) else 0.0

# ============================================================================
#  8. GRPO TRAINING (outcome-only, binary reward)
# ============================================================================

def compute_response_logprobs(model, tokenizer, prompt_text, response_text, device, dtype):
    pe = tokenizer(prompt_text, add_special_tokens=False, return_tensors='pt')
    fe = tokenizer(prompt_text + response_text, add_special_tokens=False,
                   return_tensors='pt', truncation=True, max_length=1024)
    ids = fe['input_ids'].to(device); am = fe['attention_mask'].to(device)
    pl = pe['input_ids'].shape[1]
    logits = model(input_ids=ids, attention_mask=am).logits[:, :-1, :]
    lps = F.log_softmax(logits.float(), dim=-1)
    tids = ids[:, 1:]
    tlps = lps.gather(2, tids.unsqueeze(-1)).squeeze(-1)
    return tlps[0, pl - 1:]


def grpo_train_step(model, tokenizer, optimizer, device, dtype, train_qs,
                    batch_prompts=2, group_size=4, max_new_tokens=8,
                    temperature=0.8, clip_eps=0.2, random_reward=False, rng=None):
    if rng is None: rng = np.random.default_rng()
    all_groups = []; total_r = 0.0; n_roll = 0; total_std = 0.0; n_nz = 0
    for _ in range(batch_prompts):
        q = train_qs[int(rng.integers(0, len(train_qs)))]
        pt = build_prompt_text(q); gr = []
        for g in range(group_size):
            parsed, raw = rollout_compare(model, tokenizer, q, device, dtype,
                                          max_new_tokens=max_new_tokens, temperature=temperature)
            r = float(rng.uniform(0, 1)) if random_reward else binary_reward(q, parsed)
            resp = raw.strip() or (parsed or "X")
            if IM_END not in resp: resp = resp + IM_END
            gr.append({"response": resp, "reward": r, "parsed": parsed,
                       "correct": check_correct(q, parsed)})
            total_r += r; n_roll += 1
        if len(gr) < 2: continue
        ra = np.array([x["reward"] for x in gr], dtype=np.float64)
        mr, sr = float(ra.mean()), float(ra.std())
        if sr > 1e-8: n_nz += 1
        total_std += sr
        adv = (ra - mr) / (sr + 1e-8)
        old_lps = []
        for x in gr:
            with torch.no_grad():
                lp = compute_response_logprobs(model, tokenizer, pt, x["response"], device, dtype)
            old_lps.append(lp.detach())
        all_groups.append((old_lps, adv, gr, pt))
    loss_total = torch.tensor(0.0, device=device); n_valid = 0
    for old_lps, adv, gr, pt in all_groups:
        for idx, olp in enumerate(old_lps):
            if olp is None or len(olp) == 0: continue
            nlp = compute_response_logprobs(model, tokenizer, pt, gr[idx]["response"], device, dtype)
            ml = min(len(nlp), len(olp))
            if ml == 0: continue
            ratio = torch.exp(nlp[:ml] - olp[:ml])
            a = torch.tensor(adv[idx], device=device, dtype=torch.float32)
            loss = -torch.min(ratio * a, torch.clamp(ratio, 1-clip_eps, 1+clip_eps) * a).mean()
            loss_total = loss_total + loss; n_valid += 1
    if n_valid > 0:
        loss_total = loss_total / n_valid
        optimizer.zero_grad(); loss_total.backward()
        torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad], 1.0)
        optimizer.step()
    return (float(loss_total.item()) if n_valid > 0 else 0.0,
            total_r / max(n_roll, 1), total_std / max(len(all_groups), 1),
            n_nz / max(len(all_groups), 1))


def run_grpo(model, tokenizer, device, dtype, train_qs, n_steps, label,
             out_dir, lr=1e-6, batch_prompts=2, group_size=4,
             max_new_tokens=8, temperature=0.8, clip_eps=0.2, seed=42,
             random_reward=False):
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=lr)
    rng = np.random.default_rng(seed)
    losses = []; rewards = []; stds = []; nz_fracs = []; t0 = time.time()
    for step in range(n_steps):
        loss, ar, astd, nzf = grpo_train_step(
            model, tokenizer, opt, device, dtype, train_qs,
            batch_prompts=batch_prompts, group_size=group_size,
            max_new_tokens=max_new_tokens, temperature=temperature,
            clip_eps=clip_eps, random_reward=random_reward, rng=rng)
        losses.append(loss); rewards.append(ar); stds.append(astd); nz_fracs.append(nzf)
        if step % 3 == 0 or step == n_steps - 1:
            print(f"    [{label}] step{step+1}/{n_steps} loss={loss:.4f} "
                  f"reward={ar:.3f} std={astd:.3f} nz_std={nzf:.0%} ({time.time()-t0:.0f}s)", flush=True)
    return losses, rewards, stds, nz_fracs

# ============================================================================
#  9. EVALUATION + STATISTICS
# ============================================================================

def evaluate_condition(model, tokenizer, questions, device, dtype, label,
                       max_new_tokens=8):
    results = []; t0 = time.time()
    for i, q in enumerate(questions):
        parsed, raw = rollout_compare(model, tokenizer, q, device, dtype,
                                      max_new_tokens=max_new_tokens, temperature=0.0)
        correct = check_correct(q, parsed)
        results.append({"qid": q["qid"], "task": q["task"],
                        "waveform_type_a": q["waveform_type_a"],
                        "waveform_type_b": q["waveform_type_b"],
                        "same_type": q["same_type"], "difficulty": q["difficulty"],
                        "freq_ratio": q["freq_ratio"], "correct": correct,
                        "parsed": parsed, "gt": q["gt_value"], "raw_output": raw[:100]})
        if (i + 1) % 12 == 0:
            acc = sum(r["correct"] for r in results) / len(results)
            print(f"    [{label}] {i+1}/{len(questions)} acc={acc:.1%} ({time.time()-t0:.0f}s)", flush=True)
    return results


def eval_breakdown(results):
    breakdown = {}
    for key in ["difficulty", "same_type"]:
        breakdown[key] = {}
        for val in set(r[key] for r in results):
            subset = [r for r in results if r[key] == val]
            n = len(subset); nc = sum(r["correct"] for r in subset)
            breakdown[key][str(val)] = {"n": n, "correct": nc, "accuracy": nc / max(n, 1)}
    breakdown["answer"] = {}
    for ans in ["A", "B"]:
        subset = [r for r in results if r["gt"] == ans]
        n = len(subset); nc = sum(r["correct"] for r in subset)
        breakdown["answer"][ans] = {"n": n, "correct": nc, "accuracy": nc / max(n, 1)}
    return breakdown


def mcnemar_test(b_correct, c_correct):
    n01 = sum(1 for b, c in zip(b_correct, c_correct) if b and not c)
    n10 = sum(1 for b, c in zip(b_correct, c_correct) if not b and c)
    n_disc = n01 + n10
    if n_disc == 0: return 0.0, 1.0, 0
    from scipy.stats import binomtest
    p = binomtest(min(n01, n10), n_disc, 0.5).pvalue
    stat = abs(n01 - n10) / max(n_disc, 1)
    return stat, p, n_disc


def bootstrap_ci_delta(b_correct, c_correct, n_boot=10000):
    n = len(b_correct)
    if n == 0: return 0.0, 0.0, 0.0
    b = np.array(b_correct, dtype=float); c = np.array(c_correct, dtype=float)
    rng = np.random.default_rng(42)
    deltas = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        deltas.append(c[idx].mean() - b[idx].mean())
    deltas = np.array(deltas)
    point = float(c.mean() - b.mean())
    return point, float(np.percentile(deltas, 2.5)), float(np.percentile(deltas, 97.5))

# ============================================================================
#  10. MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="v8 frequency comparison experiment")
    parser.add_argument('--model_path', default=LLM_PATH)
    parser.add_argument('--sft_ckpt', default=None, help="Path to existing SFT adapter")
    parser.add_argument('--out_dir', required=True)
    parser.add_argument('--mode', default='standard', choices=['standard', 'smoke', 'control'])
    parser.add_argument('--seed', type=int, default=20261112)
    parser.add_argument('--n_sft', type=int, default=200)
    parser.add_argument('--sft_epochs', type=int, default=3)
    parser.add_argument('--n_grpo_steps', type=int, default=15)
    parser.add_argument('--n_train', type=int, default=100)
    parser.add_argument('--n_eval', type=int, default=48)
    parser.add_argument('--group_size', type=int, default=4)
    parser.add_argument('--batch_prompts', type=int, default=2)
    parser.add_argument('--lr', type=float, default=5e-6)
    parser.add_argument('--grpo_lr', type=float, default=1e-6)
    parser.add_argument('--max_new_tokens', type=int, default=8)
    parser.add_argument('--temperature', type=float, default=0.8)
    parser.add_argument('--clip_eps', type=float, default=0.2)
    parser.add_argument('--lora_r', type=int, default=16)
    parser.add_argument('--skip_baseline_eval', action='store_true')
    parser.add_argument('--skip_sft', action='store_true')
    args = parser.parse_args()

    if args.mode == 'smoke':
        args.n_eval = 12; args.n_grpo_steps = 2; args.n_train = 12
        args.n_sft = 24; args.group_size = 2; args.batch_prompts = 1
        print("=" * 60, "\n  SMOKE TEST MODE\n", "=" * 60, flush=True)
    if args.mode == 'control':
        print("  CONTROL MODE: random reward GRPO", flush=True)

    os.environ.setdefault("OMP_NUM_THREADS", "16"); torch.set_num_threads(16)
    device = torch.device('cpu'); dtype = torch.float32
    os.makedirs(args.out_dir, exist_ok=True)
    random.seed(args.seed); np.random.seed(args.seed)
    print(f"  CPU threads=16, mode={args.mode}, seed={args.seed}", flush=True)

    # Phase 0: Build eval set
    print("=" * 60, "\n[Phase 0] Building eval set", flush=True)
    eval_qs = build_eval_set(n_per_category=args.n_eval // 6)
    with open(os.path.join(args.out_dir, "eval_questions.json"), 'w') as f:
        json.dump([{k: v for k, v in q.items() if k not in ("v_a", "v_b")} for q in eval_qs],
                  f, indent=2, default=str)
    print(f"  {len(eval_qs)} eval pairs", flush=True)

    # Phase 1: SFT (if not skipping)
    sft_ckpt_path = args.sft_ckpt
    if not args.skip_sft and not (sft_ckpt_path and os.path.isdir(sft_ckpt_path)):
        print("=" * 60, "\n[Phase 1] SFT training (frequency comparison)", flush=True)
        sft_examples = build_sft_dataset(args.n_sft)
        print(f"  {len(sft_examples)} SFT examples", flush=True)
        model_sft = build_model(args.model_path, device, dtype, lora_r=args.lora_r)
        tokenizer = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
        if tokenizer.pad_token is None: tokenizer.pad_token = tokenizer.eos_token
        losses_sft = sft_train(model_sft, tokenizer, sft_examples, device, dtype,
                               n_epochs=args.sft_epochs, lr=args.lr, label="SFT-v8")
        sft_save = os.path.join(args.out_dir, "sft_adapter")
        model_sft.save_pretrained(sft_save)
        print(f"  SFT adapter saved to {sft_save}", flush=True)
        sft_ckpt_path = sft_save
        del model_sft; gc.collect()
    else:
        print("=" * 60, "\n[Phase 1] SFT SKIPPED (using existing adapter)", flush=True)
        tokenizer = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
        if tokenizer.pad_token is None: tokenizer.pad_token = tokenizer.eos_token

    # Phase 2: Eval A (zero-shot) + B (SFT)
    res_a = None; res_b = None; acc_a = None; acc_b = None
    bd_a = None; bd_b = None
    if not args.skip_baseline_eval:
        print("=" * 60, "\n[Phase 2] Eval A (zero-shot) + B (SFT)", flush=True)
        print("  Evaluating A (zero-shot, fresh LoRA)...", flush=True)
        model_a = build_model(args.model_path, device, dtype, lora_r=args.lora_r)
        res_a = evaluate_condition(model_a, tokenizer, eval_qs, device, dtype, "A-base", args.max_new_tokens)
        acc_a = sum(r["correct"] for r in res_a) / len(res_a)
        bd_a = eval_breakdown(res_a)
        print(f"  A (zero-shot) accuracy: {acc_a:.1%}", flush=True)
        del model_a; gc.collect()
        print("  Evaluating B (SFT)...", flush=True)
        model_b = build_model(args.model_path, device, dtype, lora_r=args.lora_r, sft_ckpt=sft_ckpt_path)
        res_b = evaluate_condition(model_b, tokenizer, eval_qs, device, dtype, "B-sft", args.max_new_tokens)
        acc_b = sum(r["correct"] for r in res_b) / len(res_b)
        bd_b = eval_breakdown(res_b)
        print(f"  B (SFT) accuracy: {acc_b:.1%}", flush=True)
        del model_b; gc.collect()
    else:
        print("=" * 60, "\n[Phase 2] Skipping A+B eval (reuse from first seed)", flush=True)

    # Phase 3: GRPO training
    random_reward = (args.mode == 'control')
    mode_str = "control (random reward)" if random_reward else "standard"
    print("=" * 60, f"\n[Phase 3] GRPO training (mode={mode_str}, seed={args.seed})", flush=True)
    train_qs = build_train_set(args.n_train)
    print(f"  {len(train_qs)} training pairs", flush=True)
    model_c = build_model(args.model_path, device, dtype, lora_r=args.lora_r, sft_ckpt=sft_ckpt_path)
    ckpt_c = os.path.join(args.out_dir, "grpo_c"); os.makedirs(ckpt_c, exist_ok=True)
    losses_c, rewards_c, stds_c, nzf_c = run_grpo(
        model_c, tokenizer, device, dtype, train_qs, args.n_grpo_steps,
        label=f"GRPO-C ({mode_str})", out_dir=ckpt_c, lr=args.grpo_lr,
        batch_prompts=args.batch_prompts, group_size=args.group_size,
        max_new_tokens=args.max_new_tokens, temperature=args.temperature,
        clip_eps=args.clip_eps, seed=args.seed, random_reward=random_reward)

    # Phase 4: Eval C
    print("=" * 60, "\n[Phase 4] Eval C (after GRPO)", flush=True)
    res_c = evaluate_condition(model_c, tokenizer, eval_qs, device, dtype, "C-grpo", args.max_new_tokens)
    acc_c = sum(r["correct"] for r in res_c) / len(res_c)
    bd_c = eval_breakdown(res_c)
    print(f"  C (GRPO) accuracy: {acc_c:.1%}", flush=True)
    del model_c; gc.collect()

    # Phase 5: Statistics
    print("=" * 60, "\n[Phase 5] Statistics", flush=True)
    stats = {"mode": args.mode, "seed": args.seed,
             "accuracy": {"A_base": acc_a, "B_sft": acc_b, "C_grpo": acc_c},
             "breakdown": {"A": bd_a, "B": bd_b, "C": bd_c},
             "lora_config": {"r": args.lora_r, "alpha": args.lora_r * 2},
             "grpo_stats": {"C_avg_std": float(np.mean(stds_c)),
                            "C_nonzero_std_frac": float(np.mean(nzf_c)),
                            "C_avg_reward_last5": float(np.mean(rewards_c[-5:])) if rewards_c else 0.0}}
    if res_b and res_c:
        cb = [r["correct"] for r in res_b]; cc = [r["correct"] for r in res_c]
        scb, pcb, ncb = mcnemar_test(cb, cc)
        ptcb, locb, hicb = bootstrap_ci_delta(cb, cc)
        stats["mcnemar_C_vs_B"] = {"stat": scb, "p": pcb, "n_discordant": ncb}
        stats["bootstrap_C_vs_B"] = {"point_delta": ptcb, "ci_lo": locb, "ci_hi": hicb}
    if res_a and res_b:
        ca = [r["correct"] for r in res_a]; cb2 = [r["correct"] for r in res_b]
        sca, pca, nca = mcnemar_test(ca, cb2)
        stats["mcnemar_B_vs_A"] = {"stat": sca, "p": pca, "n_discordant": nca}
    stats["cheat_rate"] = {"train_seed": f"{TRAIN_SEED_BASE}+", "eval_seed": f"{EVAL_SEED_BASE}+",
                           "overlap": 0, "note": "disjoint RNG seeds -> no leakage"}
    if acc_b is not None and acc_c is not None:
        if acc_c > acc_b:
            sig = "mcnemar_C_vs_B" in stats and stats["mcnemar_C_vs_B"]["p"] < 0.05
            verdict = "TREATMENT SIGNIFICANT" if sig else "IMPROVEMENT (not significant)"
        elif acc_c < acc_b: verdict = "NO IMPROVEMENT"
        else: verdict = "NO CHANGE"
    else: verdict = "PARTIAL (missing baseline)"
    stats["verdict"] = verdict

    print(f"\n{'=' * 60}\n  RESULTS SUMMARY (v8: {args.mode}, seed={args.seed})", flush=True)
    if acc_a is not None: print(f"  A (zero-shot):     {acc_a:.1%}", flush=True)
    if acc_b is not None: print(f"  B (SFT):           {acc_b:.1%}", flush=True)
    print(f"  C (GRPO):          {acc_c:.1%}", flush=True)
    if "mcnemar_C_vs_B" in stats:
        print(f"  McNemar C-vs-B: p={stats['mcnemar_C_vs_B']['p']:.4f} (n_disc={stats['mcnemar_C_vs_B']['n_discordant']})", flush=True)
        print(f"  Bootstrap C-B: {stats['bootstrap_C_vs_B']['point_delta']:+.1%} CI=[{stats['bootstrap_C_vs_B']['ci_lo']:+.1%},{stats['bootstrap_C_vs_B']['ci_hi']:+.1%}]", flush=True)
    print(f"  GRPO nonzero-std: {np.mean(nzf_c):.1%}", flush=True)
    print(f"  VERDICT: {verdict}", flush=True)

    out = {"config": vars(args), "stats": stats,
           "results": {"A": res_a, "B": res_b, "C": res_c},
           "training": {"C_losses": losses_c, "C_rewards": rewards_c, "C_stds": stds_c, "C_nz_std": nzf_c}}
    out_path = os.path.join(args.out_dir, "experiment_results.json")
    with open(out_path, 'w') as f: json.dump(out, f, indent=2, default=str)
    print(f"\n  Full results -> {out_path}", flush=True)

if __name__ == "__main__":
    main()
