#!/usr/bin/env python3
"""cpu_rl_v11_regen_experiment.py - Waveform Experiment v11:
   REGRESSION vs GENERATION three-arm comparison (research-daily directive).

WHY v11 (DIRECTION CHANGE after v6-v10 stalled, per task guardrail
   "连续 3 轮无提升必须换方向" + 2026-11-14 research-daily vision item
   "波形任务的「回归 vs 生成」先做三臂小对照"):
   v5 (type CLASSIFICATION, RFT):    C=53% > B=37% > A=16%, p=0.0009  -- SIGNIFICANT (the one success)
   v6 (GRPO typecls):                 no improvement over v5
   v7 (sweep):                        no improvement
   v8 (freqcmp):                      B=45% < chance, broken
   v9 (freqcmp scaled):               n_disc=0, NO CHANGE
   v10 (freqcmp Qwen3.5-2B GPU):      C=51.6% < B=54.9%, NOT SIGNIFICANT (2/6 criteria)
   => 5 rounds (v6-v10) without improvement on the freqcmp direction => MUST change direction.

ROOT CAUSE (why freqcmp stalled):
   Frequency COMPARISON (2-class A/B) saturates near 55%; GRPO cannot push past the
   SFT ceiling because the task has little headroom and the discrete A/B reward gives
   near-zero advantage variance (the original bottleneck diagnosed in gs4/gs8).

NEW DIRECTION (research-daily 2026-11-14 line 181, incorporated per task-book rule
   "若本线建议有相关条目 -> 纳入本轮计划"):
   Go back to the ORIGINAL hard task -- PERIOD REGRESSION (v2-v4 ceiling ~34%) -- and
   test whether GENERATIVE approaches beat DIRECT regression. Three arms, fixed data &
   budget (no GRPO; all arms are SFT, since GRPO repeatedly failed on these tasks):

   Arm 1 "direct"   (直接回归):           SFT to output the period number directly.
   Arm 2 "augment"  (回归 + 生成式增广):   Arm 1 + training data augmented with a denser
                                          grid of synthesized waveforms (the programmatic
                                          generator IS the generative model here).
   Arm 3 "synthesis"(生成后取统计量):       SFT to output a compact generative spec
                                          "type,freq" (analysis-by-synthesis); period is
                                          then computed as 1/freq programmatically.

   NOTE on "diffusion": full diffusion-model training is infeasible on our CPU/single-A40
   budget for a 2B model in a pilot. We use the PROGRAMMATIC waveform generator (a
   parametric generative model) as the principled lightweight proxy for the generative
   component. This is documented honestly; the scientific question (does the generative
   route reduce period error vs direct regression) is preserved.

PRE-REGISTERED JUDGMENT (written BEFORE running, 2026-11-14):
   Arm 1 (direct):    ~30-40%  (known SFT ceiling on period regression, per v2-v4)
   Arm 2 (augment):   > Arm 1  IF generative data augmentation supplies useful period coverage
   Arm 3 (synthesis): > Arm 1  IF decomposing to type+freq (then 1/freq) is an easier
                      representation than regressing the period number directly
   SUCCESS (honoring research-daily criterion): at least one generative arm (2 or 3) beats
                      Arm 1 by >=5pp with McNemar p<0.05, consistent across 3 seeds.
   FAIL / negative result (equally valuable): neither generative arm reduces period error
                      vs Arm 1 => "本期不做生成式路线" -- report why and next step.

MODEL: Qwen3.5-2B (user-specified), LoRA r=16, on GPU 5 (free A40 on .17) or CPU fallback.
Author: vision wake#1180.  License: project-internal.
"""
from __future__ import annotations
import sys, os, json, time, math, random, argparse, re, gc
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model, TaskType, PeftModel

LLM_PATH = "/nas_data/app.e0031982/models/Qwen3.5-2B"
WAVEFORM_TYPES = ["sine", "square", "triangle", "sawtooth"]
N_SAMPLE_POINTS = 16
TIME_WINDOW = 1.0           # microseconds
EVAL_SEED_BASE = 995100
TRAIN_SEED_BASE = 20261114
IM_START = "<|im_start|>"
IM_END = "<|im_end|>"
TOL = 0.15                  # relative-error tolerance for "correct" period

SYSTEM_PROMPT = (
    "You are a signal-analysis expert. You are given 16 evenly-spaced voltage "
    "samples of a single periodic electronic waveform taken over a 1-microsecond "
    "window. Estimate the waveform's fundamental period in microseconds."
)


# =========================================================================== #
#  1. PURE WAVEFORM GENERATORS (parametric generative model; single waveform)
# =========================================================================== #
_T_FIXED = np.linspace(0, TIME_WINDOW, N_SAMPLE_POINTS, endpoint=False)


def _gen_sine(rng, freq):
    amp = float(rng.uniform(0.5, 5.0)); off = float(rng.uniform(-2.0, 2.0))
    ph = float(rng.uniform(0, 2 * math.pi)); ns = float(rng.uniform(0.0, 0.03 * amp))
    v = off + amp * np.sin(2 * math.pi * freq * _T_FIXED + ph)
    v += rng.normal(0, ns, size=len(v)); return v


def _gen_square(rng, freq):
    amp = float(rng.uniform(0.5, 5.0)); off = float(rng.uniform(-2.0, 2.0))
    duty = float(rng.uniform(0.3, 0.7)); ns = float(rng.uniform(0.0, 0.03 * amp))
    pic = (freq * _T_FIXED) % 1.0
    v = np.where(pic < duty, off + amp, off - amp)
    v += rng.normal(0, ns, size=len(v)); return v


def _gen_triangle(rng, freq):
    amp = float(rng.uniform(0.5, 5.0)); off = float(rng.uniform(-2.0, 2.0))
    ns = float(rng.uniform(0.0, 0.03 * amp))
    ph = (freq * _T_FIXED) % 1.0
    tri = np.where(ph < 0.5, 4.0 * ph - 1.0, 3.0 - 4.0 * ph)
    v = off + amp * tri
    v += rng.normal(0, ns, size=len(v)); return v


def _gen_sawtooth(rng, freq):
    amp = float(rng.uniform(0.5, 5.0)); off = float(rng.uniform(-2.0, 2.0))
    ns = float(rng.uniform(0.0, 0.03 * amp))
    ph = (freq * _T_FIXED) % 1.0
    v = off + amp * (2.0 * ph - 1.0)
    v += rng.normal(0, ns, size=len(v)); return v


_WAVEFORM_GENS = {"sine": _gen_sine, "square": _gen_square,
                  "triangle": _gen_triangle, "sawtooth": _gen_sawtooth}

FREQ_MIN, FREQ_MAX = 2.0, 20.0   # cycles per microsecond (MHz); period(us)=1/freq


def gen_waveform_v(wtype, rng, freq):
    return _WAVEFORM_GENS[wtype](rng, freq)


def _fmt_val(v):
    return f"{v:.3f}"


def format_samples_v(v):
    return ", ".join(_fmt_val(vi) for vi in v)


# =========================================================================== #
#  2. QUESTION GENERATION (single waveform, period regression)
# =========================================================================== #
def _diff_to_freq_range(difficulty):
    if difficulty == "easy":
        return 2.0, 6.0       # long periods (0.17-0.5 us), easiest to estimate
    if difficulty == "medium":
        return 5.0, 12.0      # mid periods (0.083-0.2 us)
    return 10.0, 20.0         # short periods (0.05-0.1 us), hardest


def gen_single(qid, seed, difficulty=None, wtype=None, freq=None):
    """Generate one single-waveform period-regression question."""
    rng = np.random.default_rng(seed)
    if difficulty is None:
        difficulty = str(rng.choice(["easy", "medium", "hard"]))
    if wtype is None:
        wtype = WAVEFORM_TYPES[int(rng.integers(0, len(WAVEFORM_TYPES)))]
    if freq is None:
        lo, hi = _diff_to_freq_range(difficulty)
        freq = float(rng.uniform(lo, hi))
    v = gen_waveform_v(wtype, rng, freq)
    period = 1.0 / freq
    v_str = format_samples_v(v)
    t_str = ", ".join(_fmt_val(ti) for ti in _T_FIXED)
    return {
        "qid": qid, "task": "period_regression",
        "waveform_type": wtype, "freq": freq, "period": period,
        "difficulty": difficulty, "t_str": t_str, "v_str": v_str,
        "v": v.tolist(),
    }


# =========================================================================== #
#  3. PROMPT FORMATTING  (three arm-specific formats)
# =========================================================================== #
def _header(q):
    return (
        f"A periodic waveform is sampled at 16 evenly-spaced time points over a "
        f"1-microsecond window.\n\n"
        f"Time points (us): {q['t_str']}\n\n"
        f"Voltage samples (V): {q['v_str']}\n\n"
    )


def build_prompt_direct(q):
    user = _header(q) + (
        "What is the waveform's fundamental period in microseconds? "
        "Respond with only the numerical value (e.g. 0.250), nothing else.")
    return (f"{IM_START}system\n{SYSTEM_PROMPT}{IM_END}\n"
            f"{IM_START}user\n{user}{IM_END}\n"
            f"{IM_START}assistant\n")


def build_prompt_synthesis(q):
    user = _header(q) + (
        "First identify the waveform, then estimate its fundamental frequency. "
        "Respond with only 'TYPE,FREQ' where TYPE is one of sine/square/triangle/sawtooth "
        "and FREQ is the frequency in MHz (e.g. sine,5.0). Nothing else.")
    return (f"{IM_START}system\n{SYSTEM_PROMPT}{IM_END}\n"
            f"{IM_START}user\n{user}{IM_END}\n"
            f"{IM_START}assistant\n")


def build_sft_text(q, arm):
    if arm in ("direct", "augment"):
        prompt = build_prompt_direct(q)
        target = f"{q['period']:.4f}"
    else:  # synthesis
        prompt = build_prompt_synthesis(q)
        target = f"{q['waveform_type']},{q['freq']:.4f}"
    return prompt + f"{target}{IM_END}\n"


# =========================================================================== #
#  4. EVAL / TRAIN DATA GENERATION
# =========================================================================== #
def build_eval_set(n_per_category=16):
    """3 difficulties x n_per_category held-out questions (disjoint seeds from train)."""
    questions = []; qid = 0
    for difficulty in ["easy", "medium", "hard"]:
        for i in range(n_per_category):
            seed = EVAL_SEED_BASE + qid * 100
            questions.append(gen_single(qid, seed, difficulty=difficulty))
            qid += 1
    return questions


def build_base_train(n=400, seed_base=TRAIN_SEED_BASE):
    """Base training set: balanced across difficulty & type."""
    examples = []; qid = 0
    per_diff = n // 3
    for difficulty in ["easy", "medium", "hard"]:
        for j in range(per_diff):
            seed = seed_base + qid * 100
            q = gen_single(qid, seed, difficulty=difficulty)
            q["sft_direct"] = build_sft_text(q, "direct")
            q["sft_synthesis"] = build_sft_text(q, "synthesis")
            examples.append(q); qid += 1
    random.shuffle(examples)
    return examples


def build_augmented_train(n_extra=400, seed_base=TRAIN_SEED_BASE + 500000):
    """Generative augmentation: a DENSER, broader grid of synthesized periods.

    Same generator, but samples freq on a fine uniform grid across the FULL range
    (2-20 MHz) without the easy/medium/hard bucketing, plus extra coverage at the
    hard (short-period) end where Arm 1 is weakest. This is the 'generative data
    augmentation' arm: the generative model (programmatic generator) supplies
    additional training coverage.
    """
    examples = []; qid = 0
    for j in range(n_extra):
        seed = seed_base + qid * 100
        rng = np.random.default_rng(seed)
        if rng.random() < 0.4:
            freq = float(rng.uniform(12.0, 20.0))
        else:
            freq = float(rng.uniform(FREQ_MIN, FREQ_MAX))
        wtype = WAVEFORM_TYPES[int(rng.integers(0, len(WAVEFORM_TYPES)))]
        q = gen_single(qid, seed, wtype=wtype, freq=freq)
        q["difficulty"] = "aug"
        q["sft_direct"] = build_sft_text(q, "direct")
        examples.append(q); qid += 1
    random.shuffle(examples)
    return examples


# =========================================================================== #
#  5. MODEL LOADING
# =========================================================================== #
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


# =========================================================================== #
#  6. SFT TRAINING (cross-entropy on assistant tokens)
# =========================================================================== #
def compute_assistant_mask(tokenizer, full_text):
    asst_marker = f"{IM_START}assistant\n"
    asst_start = full_text.rfind(asst_marker)
    if asst_start < 0:
        return []
    resp_start = asst_start + len(asst_marker)
    prefix = full_text[:resp_start]
    prefix_ids = tokenizer(prefix, add_special_tokens=False)["input_ids"]
    full_ids = tokenizer(full_text, add_special_tokens=False)["input_ids"]
    n_prefix = len(prefix_ids)
    mask = [False] * n_prefix + [True] * (len(full_ids) - n_prefix)
    return mask[:len(full_ids)]


def sft_train(model, tokenizer, examples, sft_key, device, dtype, n_epochs=5,
              batch_size=8, lr=5e-6, label="SFT"):
    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad], lr=lr)
    print(f"  [{label}] Tokenizing {len(examples)} examples (key={sft_key})...", flush=True)
    tokenized = []
    for ex in examples:
        txt = ex[sft_key]
        ids = tokenizer(txt, add_special_tokens=False, return_tensors=None,
                        truncation=True, max_length=1024)["input_ids"]
        mask = compute_assistant_mask(tokenizer, txt)
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
            if masked_lps.numel() == 0:
                continue
            loss = -masked_lps.mean()
            optimizer.zero_grad(); loss.backward(); optimizer.step()
            losses.append(float(loss.item())); step += 1
            if step % 20 == 0 or step == 1:
                avg = sum(losses[-20:]) / min(len(losses), 20)
                print(f"    [{label}] ep{epoch+1}/{n_epochs} step{step} "
                      f"loss={loss.item():.4f} avg={avg:.4f} ({time.time()-t0:.0f}s)", flush=True)
    print(f"  [{label}] DONE: {step} steps, final avg={sum(losses[-20:])/min(20,len(losses)):.4f}", flush=True)
    return losses


# =========================================================================== #
#  7. ROLLOUT + PARSING + SCORING (period regression)
# =========================================================================== #
_NUM_RE = re.compile(r'[-+]?\d*\.?\d+')
_SYNTH_RE = re.compile(r'([A-Za-z]+)\s*,\s*([-+]?\d*\.?\d+)')


def rollout(model, tokenizer, q, device, dtype, arm, max_new_tokens=16, temperature=0.0):
    prompt = build_prompt_direct(q) if arm in ("direct", "augment") else build_prompt_synthesis(q)
    enc = tokenizer(prompt, add_special_tokens=False, return_tensors='pt', truncation=True, max_length=1024)
    ids = enc['input_ids'].to(device)
    with torch.no_grad():
        out = model.generate(ids, max_new_tokens=max_new_tokens,
                             do_sample=temperature > 0,
                             temperature=max(temperature, 1e-5), top_p=0.95,
                             pad_token_id=tokenizer.pad_token_id if tokenizer.pad_token_id is not None else 0,
                             eos_token_id=tokenizer.convert_tokens_to_ids(IM_END))
    gen = tokenizer.decode(out[0, ids.shape[1]:], skip_special_tokens=True).strip()
    return gen


def parse_period(gen, arm):
    """Parse the model output into a predicted period (us). Returns None if unparseable."""
    if arm in ("direct", "augment"):
        m = _NUM_RE.search(gen)
        if not m:
            return None
        try:
            return float(m.group(0))
        except ValueError:
            return None
    else:  # synthesis: "TYPE,FREQ" -> period = 1/freq
        m = _SYNTH_RE.search(gen)
        if m:
            try:
                freq = float(m.group(2))
            except ValueError:
                return None
        else:
            nums = _NUM_RE.findall(gen)
            if not nums:
                return None
            try:
                freq = float(nums[-1])
            except ValueError:
                return None
        if freq <= 1e-6:
            return None
        return 1.0 / freq


def score_period(q, pred_period):
    """Return (correct, rel_err). correct iff rel_err < TOL."""
    if pred_period is None or pred_period <= 0:
        return False, None
    rel = abs(pred_period - q["period"]) / q["period"]
    return (rel < TOL), float(rel)


# =========================================================================== #
#  8. EVALUATION + STATISTICS
# =========================================================================== #
def evaluate_arm(model, tokenizer, questions, device, dtype, arm, label, max_new_tokens=16):
    results = []; t0 = time.time()
    for i, q in enumerate(questions):
        gen = rollout(model, tokenizer, q, device, dtype, arm, max_new_tokens=max_new_tokens)
        pred = parse_period(gen, arm)
        correct, rel = score_period(q, pred)
        results.append({"qid": q["qid"], "arm": arm, "type": q["waveform_type"],
                        "difficulty": q["difficulty"], "true_period": q["period"],
                        "pred_period": pred, "rel_err": rel, "correct": correct,
                        "raw": gen[:80]})
        if (i + 1) % 12 == 0:
            acc = sum(r["correct"] for r in results) / len(results)
            print(f"    [{label}] {i+1}/{len(questions)} acc={acc:.1%} ({time.time()-t0:.0f}s)", flush=True)
    return results


def arm_accuracy(results):
    return sum(r["correct"] for r in results) / max(len(results), 1)


def breakdown_by(results, key):
    bd = {}
    for val in sorted(set(r[key] for r in results)):
        sub = [r for r in results if r[key] == val]
        n = len(sub); nc = sum(r["correct"] for r in sub)
        bd[str(val)] = {"n": n, "correct": nc, "accuracy": nc / max(n, 1)}
    return bd


def mean_rel_err(results):
    errs = [r["rel_err"] for r in results if r["rel_err"] is not None]
    return float(np.mean(errs)) if errs else None


def mcnemar_test(a_correct, b_correct):
    n01 = sum(1 for a, b in zip(a_correct, b_correct) if a and not b)
    n10 = sum(1 for a, b in zip(a_correct, b_correct) if not a and b)
    n_disc = n01 + n10
    if n_disc == 0:
        return 0.0, 1.0, 0
    from scipy.stats import binomtest
    p = binomtest(min(n01, n10), n_disc, 0.5).pvalue
    stat = abs(n01 - n10) / max(n_disc, 1)
    return stat, p, n_disc


def bootstrap_ci_delta(a_correct, b_correct, n_boot=10000):
    n = len(a_correct)
    if n == 0:
        return 0.0, 0.0, 0.0
    a = np.array(a_correct, dtype=float); b = np.array(b_correct, dtype=float)
    rng = np.random.default_rng(42)
    deltas = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        deltas.append(b[idx].mean() - a[idx].mean())
    deltas = np.array(deltas)
    point = float(b.mean() - a.mean())
    return point, float(np.percentile(deltas, 2.5)), float(np.percentile(deltas, 97.5))


# =========================================================================== #
#  9. MAIN
# =========================================================================== #
def main():
    parser = argparse.ArgumentParser(description="v11 regression-vs-generation three-arm experiment")
    parser.add_argument('--model_path', default=LLM_PATH)
    parser.add_argument('--out_dir', required=True)
    parser.add_argument('--mode', default='standard', choices=['standard', 'smoke'])
    parser.add_argument('--seed', type=int, default=20261114)
    parser.add_argument('--n_base', type=int, default=400, help="base train examples per arm")
    parser.add_argument('--n_aug', type=int, default=400, help="extra augmented examples for arm2")
    parser.add_argument('--sft_epochs', type=int, default=5)
    parser.add_argument('--n_eval_per_cat', type=int, default=16)
    parser.add_argument('--lr', type=float, default=5e-6)
    parser.add_argument('--batch_size', type=int, default=8)
    parser.add_argument('--max_new_tokens', type=int, default=16)
    parser.add_argument('--lora_r', type=int, default=16)
    parser.add_argument('--arms', default='direct,augment,synthesis')
    args = parser.parse_args()

    if args.mode == 'smoke':
        args.n_eval_per_cat = 4; args.n_base = 24; args.n_aug = 24
        args.sft_epochs = 2; args.batch_size = 4
        print("=" * 60, "\n  SMOKE TEST MODE\n", "=" * 60, flush=True)

    arms = [a.strip() for a in args.arms.split(',') if a.strip()]

    os.environ.setdefault("OMP_NUM_THREADS", "16"); torch.set_num_threads(16)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
    os.makedirs(args.out_dir, exist_ok=True)
    random.seed(args.seed); np.random.seed(args.seed)
    print(f"  device={device}, dtype={dtype}, mode={args.mode}, seed={args.seed}, arms={arms}", flush=True)

    print("=" * 60, "\n[Phase 0] Building eval set", flush=True)
    eval_qs = build_eval_set(n_per_category=args.n_eval_per_cat)
    with open(os.path.join(args.out_dir, "eval_questions.json"), 'w') as f:
        json.dump([{k: v for k, v in q.items() if k != "v"} for q in eval_qs],
                  f, indent=2, default=str)
    print(f"  {len(eval_qs)} eval questions", flush=True)

    base_train = build_base_train(n=args.n_base)
    aug_extra = build_augmented_train(n_extra=args.n_aug)
    augment_train = base_train + aug_extra
    print(f"  base train={len(base_train)}, augment train={len(base_train)}+{len(aug_extra)}={len(augment_train)}", flush=True)

    tokenizer = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    arm_results = {}; arm_acc = {}; arm_mre = {}; arm_bd = {}; arm_losses = {}

    for arm in arms:
        print("=" * 60, f"\n[Arm: {arm}] Training + Eval", flush=True)
        if arm == "direct":
            train_ex, sft_key = base_train, "sft_direct"
        elif arm == "augment":
            train_ex, sft_key = augment_train, "sft_direct"
        else:  # synthesis
            train_ex, sft_key = base_train, "sft_synthesis"
        model = build_model(args.model_path, device, dtype, lora_r=args.lora_r)
        losses = sft_train(model, tokenizer, train_ex, sft_key, device, dtype,
                           n_epochs=args.sft_epochs, batch_size=args.batch_size,
                           lr=args.lr, label=f"SFT-{arm}")
        res = evaluate_arm(model, tokenizer, eval_qs, device, dtype, arm,
                           f"eval-{arm}", args.max_new_tokens)
        acc = arm_accuracy(res); mre = mean_rel_err(res)
        arm_results[arm] = res; arm_acc[arm] = acc; arm_mre[arm] = mre
        arm_bd[arm] = {"difficulty": breakdown_by(res, "difficulty"),
                       "type": breakdown_by(res, "type")}
        arm_losses[arm] = losses
        mre_str = f"{mre:.3f}" if mre is not None else "n/a"
        print(f"  Arm '{arm}': acc={acc:.1%}  mean_rel_err={mre_str}", flush=True)
        del model; gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    print("=" * 60, "\n[Statistics] generative arms vs direct (Arm 1)", flush=True)
    stats = {"mode": args.mode, "seed": args.seed, "arms": arms,
             "tol": TOL, "accuracy": arm_acc, "mean_rel_err": arm_mre,
             "breakdown": arm_bd, "lora_config": {"r": args.lora_r, "alpha": args.lora_r * 2},
             "cheat_rate": {"train_seed": f"{TRAIN_SEED_BASE}+", "eval_seed": f"{EVAL_SEED_BASE}+",
                            "overlap": 0, "note": "disjoint RNG seeds -> no leakage"}}
    direct_correct = [r["correct"] for r in arm_results.get("direct", [])]
    for arm in arms:
        if arm == "direct" or arm not in arm_results:
            continue
        ac = [r["correct"] for r in arm_results[arm]]
        if len(ac) == len(direct_correct) and direct_correct:
            s, p, nd = mcnemar_test(direct_correct, ac)
            pt, lo, hi = bootstrap_ci_delta(direct_correct, ac)
            stats[f"mcnemar_{arm}_vs_direct"] = {"stat": s, "p": p, "n_discordant": nd}
            stats[f"bootstrap_{arm}_vs_direct"] = {"point_delta": pt, "ci_lo": lo, "ci_hi": hi}
            print(f"  {arm} vs direct: acc {arm_acc[arm]:.1%} vs {arm_acc['direct']:.1%} | "
                  f"McNemar p={p:.4f} n_disc={nd} | boot delta={pt:+.1%} CI=[{lo:+.1%},{hi:+.1%}]", flush=True)

    verdict = "PENDING"
    if "direct" in arm_acc:
        best_gen, best_gain = None, 0.0
        for arm in arms:
            if arm == "direct":
                continue
            gain = arm_acc.get(arm, 0) - arm_acc["direct"]
            mc = stats.get(f"mcnemar_{arm}_vs_direct", {})
            sig = bool(mc) and mc.get("p", 1) < 0.05
            if gain >= 0.05 and sig and gain > best_gain:
                best_gen, best_gain = arm, gain
        verdict = f"GENERATIVE WINS ({best_gen}, +{best_gain:.1%})" if best_gen else \
                  "NO GENERATIVE ADVANTAGE (negative result: do not pursue generative route this period)"
    stats["verdict"] = verdict

    print(f"\n{'='*60}\n  v11 RESULTS SUMMARY (mode={args.mode}, seed={args.seed})", flush=True)
    for arm in arms:
        mre_str = f"{arm_mre[arm]:.3f}" if arm_mre[arm] is not None else "n/a"
        print(f"  Arm {arm:<10}: acc={arm_acc[arm]:.1%}  mre={mre_str}", flush=True)
    print(f"  VERDICT: {verdict}", flush=True)

    out = {"config": vars(args), "stats": stats, "results": arm_results, "training": arm_losses}
    out_path = os.path.join(args.out_dir, "experiment_results.json")
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\n  Full results -> {out_path}", flush=True)


if __name__ == "__main__":
    main()
