#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""grpo_mllm_wave_v2.py -- Stage-2W GRPOv2 on the FULL Qwen3.5-2B MLLM
(用户令 2026-11-24 08:5x · 放行 GRPO 改进).

v1 (grpo_mllm_wave.py) 负结果诊断（report §5.5）：
  * 224 步中 189 步 reward=1.0（饱和），仅 2/224 步 group_std>0 有梯度；
  * 冷启动挂 rft2_adapter_seed11(held-out 0.90) → 策略已近最优，无 headroom；
  * 训练题太易（整数周期/无噪声/单通道）→ group 奖励方差近零；
  * 二值/连续奖励在「全对」时塌缩到 1.0，无区分度。

v2 四项改进（预注册，开跑前写明，跑完不改判据）：
  1. 冷启动从 SFT adapter（sft2_adapter_seed11, 0.70）而非 RFT2(0.90)，留 headroom。
  2. 奖励分解：exact=1.0 | in-bounds=α=0.3 | out-of-bounds=-β=-0.5（β>α）。
  3. 更难/长尾训练题：噪声 + 非整数周期/幅值 + 更近频率 + 多通道干扰。
  4. 跑 ≥500 步，报 reward 曲线 + cheat_rate + 配对检验（McNemar + bootstrap）。

判据（预注册）：post-GRPO vs 冷启动 SFT 基线，held-out 30 题（seed=20261115，
与训练 seed 隔离 → cheat_rate=0）：成功 = post-GRPO acc > 冷启动 AND McNemar p<0.05；
不显著/负结果照写。

用法（.17 GPU7，单卡 2B LoRA，不扰 GPU6 VQA 服务）：
  PY=/nas_data/app.e0031982/miniforge3/envs/py310/bin/python
  CUDA_VISIBLE_DEVICES=7 $PY grpo_mllm_wave_v2.py --smoke_test
  CUDA_VISIBLE_DEVICES=7 $PY grpo_mllm_wave_v2.py --total_steps 500 --group_size 4 --batch_prompts 2

作者: vision wake#1709 · project-internal
"""
import argparse, json, math, os, sys, time
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.environ.get("QWEN35_VQA_MODEL", "/nas_data/app.e0031982/models/Qwen3.5-2B")
OUT_DIR = os.path.join(HERE, "grpo_mllm_runs_v2")
os.makedirs(OUT_DIR, exist_ok=True)

from sft_rl_strengthen import (  # noqa: E402
    load_model_for_train, build_lora, gen_answer, eval_on_heldout,
    make_eval_set, mcnemar_exact,
)
from synth_waveform_qa import (  # noqa: E402
    make_case, parse_answer, is_correct, SKILLS, WAVEFORM_TYPES,
)
from baseline_waveform_vqa import (  # noqa: E402
    new_canvas, draw_signal, two_sine_image, rise_edge_image,
)

# ---- v2 奖励分解参数（预注册） ----
ALPHA = 0.3          # in-bounds 区间内部分分（β>α）
BETA = 0.5           # out-of-bounds 越界惩罚幅度（BETA > ALPHA）
REG_EXACT_REL = 0.02  # exact: rel_err < 2%
REG_TOL_REL = 0.15    # in-bounds: rel_err < 15%（与 v1 TAU 对齐）


def reward_for_v2(skill, kind, pred, gt, gt_num=None):
    """分段奖励：exact=1.0 / in-bounds=α / out-of-bounds=-β（β>α）。"""
    if kind in ("number", "percent"):
        try:
            p = float(pred)
        except (TypeError, ValueError):
            return -BETA
        if gt_num is None or gt_num == 0:
            return 1.0 if abs(p) < 1e-6 else -BETA
        rel = abs(p - float(gt_num)) / abs(float(gt_num))
        if rel < REG_EXACT_REL:
            return 1.0
        elif rel < REG_TOL_REL:
            return ALPHA
        else:
            return -BETA
    return 1.0 if is_correct(skill, kind, pred, gt, gt_num) else -BETA


def _add_noise(path, rng, sigma=14.0):
    img = Image.open(path).convert("RGB")
    arr = np.asarray(img).astype(np.float32)
    noise = rng.normal(0.0, sigma, arr.shape).astype(np.float32)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    Image.fromarray(arr).save(path)


def _add_distractor_channel(path, rng):
    img = Image.open(path).convert("RGB")
    d = ImageDraw.Draw(img)
    x0, x1 = 40, 465
    cyc = float(rng.uniform(6.0, 9.0))
    amp = float(rng.uniform(0.6, 1.0))
    mid = 130
    pts = [(x, mid - amp * 40 * np.sin(2 * np.pi * cyc * (x - x0) / (x1 - x0)))
           for x in range(x0, x1)]
    for i in range(len(pts) - 1):
        d.line([pts[i], pts[i + 1]], fill=(200, 200, 160), width=1)
    img.save(path)


def _render_wave(path, wtype, cycles, amp_div=3.0, duty=0.5):
    img, d = new_canvas()
    x0, x1, mid = 40, 465, 130
    if wtype == "sine":
        pts = [(x, mid - amp_div * 40 * np.sin(2 * np.pi * cycles * (x - x0) / (x1 - x0)))
               for x in range(x0, x1)]
        draw_signal(d, pts)
    elif wtype == "square":
        n = 1200
        prev = None
        for i in range(n):
            t = (i / n) * cycles
            phase = t - int(t)
            y = mid - amp_div * 40 if phase < duty else mid + amp_div * 40
            x = x0 + (x1 - x0) * i / n
            if prev is not None:
                d.line([prev, (x, y)], fill="blue", width=2)
            prev = (x, y)
    elif wtype == "triangle":
        pts = []
        for x in range(x0, x1):
            t = (x - x0) / (x1 - x0)
            ph = (cycles * t) % 1.0
            y = mid - amp_div * 40 * (4.0 * ph - 1.0 if ph < 0.5 else 3.0 - 4.0 * ph)
            pts.append((x, y))
        draw_signal(d, pts)
    elif wtype == "sawtooth":
        pts = []
        for x in range(x0, x1):
            t = (x - x0) / (x1 - x0)
            y = mid - amp_div * 40 * (2.0 * ((cycles * t) % 1.0) - 1.0)
            pts.append((x, y))
        draw_signal(d, pts)
    else:
        raise ValueError(wtype)
    img.save(path)


def make_case_hard(skill, rng, img_dir, qid):
    """造一道【更难】训练题：噪声 + 非整数周期/幅值 + 多通道干扰。"""
    os.makedirs(img_dir, exist_ok=True)
    p = os.path.join(img_dir, f"q{qid}.png")
    noise_sigma = float(rng.uniform(8.0, 20.0))
    add_distractor = bool(rng.integers(0, 2))
    if skill == "type_classification":
        wt = WAVEFORM_TYPES[int(rng.integers(0, len(WAVEFORM_TYPES)))]
        cyc = float(rng.uniform(2.3, 5.8))
        _render_wave(p, wt, cyc)
        if add_distractor:
            _add_distractor_channel(p, rng)
        _add_noise(p, rng, noise_sigma)
        return {"id": f"q{qid}", "skill": skill, "image": p, "wtype": wt,
                "question": "Which waveform type is this: sine, square, "
                            "triangle, or sawtooth? Answer with the single type name.",
                "gt": wt, "kind": "word_type"}
    if skill == "cycle_count":
        wt = WAVEFORM_TYPES[int(rng.integers(0, len(WAVEFORM_TYPES)))]
        cyc = float(rng.uniform(2.3, 5.8))
        _render_wave(p, wt, cyc)
        if add_distractor:
            _add_distractor_channel(p, rng)
        _add_noise(p, rng, noise_sigma)
        complete = int(math.floor(cyc))
        return {"id": f"q{qid}", "skill": skill, "image": p, "wtype": wt,
                "question": "How many complete waveform cycles are shown? "
                            "Answer with just a number.",
                "gt": str(complete), "kind": "number", "gt_num": float(complete)}
    if skill == "amplitude_read":
        wt = WAVEFORM_TYPES[int(rng.integers(0, len(WAVEFORM_TYPES)))]
        cyc = float(rng.uniform(2.3, 5.8))
        amp = float(rng.uniform(2.2, 3.6))
        _render_wave(p, wt, cyc, amp_div=amp)
        if add_distractor:
            _add_distractor_channel(p, rng)
        _add_noise(p, rng, noise_sigma)
        pp = 2.0 * amp
        gt_pp = round(pp)
        return {"id": f"q{qid}", "skill": skill, "image": p, "wtype": wt,
                "question": "What is the peak-to-peak amplitude of this waveform, "
                            "in vertical grid divisions (each grid square = 1 division)? "
                            "Answer with a number.",
                "gt": str(gt_pp), "kind": "number", "gt_num": float(gt_pp)}
    if skill == "freq_comparison":
        ca = float(rng.uniform(2.3, 5.8))
        cb = float(rng.uniform(2.3, 5.8))
        while abs(ca - cb) < 0.6:
            cb = float(rng.uniform(2.3, 5.8))
        two_sine_image(p, ca, cb)
        _add_noise(p, rng, noise_sigma)
        gt = "A" if ca > cb else "B"
        return {"id": f"q{qid}", "skill": skill, "image": p,
                "question": "Signal A (blue, top) and signal B (red, bottom) are shown. "
                            "Which signal has the HIGHER frequency? Answer A or B.",
                "gt": gt, "kind": "ab"}
    if skill == "duty_cycle":
        duty = float(rng.choice([0.25, 0.33, 0.5, 0.67, 0.75]))
        cyc = float(rng.uniform(2.3, 5.8))
        _render_wave(p, "square", cyc, duty=duty)
        if add_distractor:
            _add_distractor_channel(p, rng)
        _add_noise(p, rng, noise_sigma)
        return {"id": f"q{qid}", "skill": skill, "image": p,
                "question": "What is the duty cycle of this square wave "
                            "(high-time / period)? Answer as a percentage.",
                "gt": f"{int(round(duty * 100))}", "kind": "percent",
                "gt_num": float(duty * 100)}
    if skill == "rise_edge":
        slow = bool(rng.integers(0, 2))
        rise_edge_image(p, slow=slow)
        _add_noise(p, rng, noise_sigma)
        return {"id": f"q{qid}", "skill": skill, "image": p,
                "question": "Is the rising edge of this signal sharp "
                            "(near-vertical) or gradual (sloped)? "
                            "Answer 'sharp' or 'gradual'.",
                "gt": "gradual" if slow else "sharp", "kind": "word_rise"}
    raise ValueError(skill)


def build_train_cases_v2(seed, n_per_skill=25, img_subdir="grpo_v2_train_images"):
    img_dir = os.path.join(OUT_DIR, img_subdir)
    os.makedirs(img_dir, exist_ok=True)
    rng = np.random.default_rng(seed)
    cases, qid = [], 0
    for skill in SKILLS:
        for _ in range(n_per_skill):
            cases.append(make_case_hard(skill, rng, img_dir, qid))
            qid += 1
    return cases


def cheat_rate_check(train_cases, eval_cases):
    tr = set(os.path.abspath(c["image"]) for c in train_cases)
    ev = set(os.path.abspath(c["image"]) for c in eval_cases)
    overlap = tr & ev
    return {"cheat_rate": round(len(overlap) / max(1, len(ev)), 4),
            "overlap_count": len(overlap), "train_seed_isolated": True,
            "note": "train seed (20261124-derivative) != eval seed (20261115); "
                    "hard-case images live in a separate dir."}


def prompt_inputs(processor, image_path, question, device):
    img = Image.open(image_path).convert("RGB")
    msgs = [{"role": "user", "content": [
        {"type": "image", "image": img},
        {"type": "text", "text": question}]}]
    text = processor.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    inputs = processor(text=[text], images=[img], return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    return inputs, img


def sample_one(model, processor, image_path, question, device,
               max_new_tokens, temperature, top_p):
    import torch
    inputs, img = prompt_inputs(processor, image_path, question, device)
    prompt_len = int(inputs["input_ids"].shape[1])
    do_sample = float(temperature) > 0
    kw = dict(max_new_tokens=int(max_new_tokens), do_sample=do_sample)
    if do_sample:
        kw["temperature"] = float(temperature)
        kw["top_p"] = float(top_p)
    with torch.no_grad():
        out = model.generate(**inputs, **kw)
    full_ids = out[0]
    gen_ids = full_ids[prompt_len:]
    gen_text = processor.decode(gen_ids, skip_special_tokens=True).strip()
    img_inputs = {k: v for k, v in inputs.items()
                  if k not in ("input_ids", "attention_mask")}
    return full_ids, prompt_len, gen_text, img_inputs


def completion_logprobs(model, full_ids, prompt_len, img_inputs, device):
    import torch
    import torch.nn.functional as F
    ids = full_ids.unsqueeze(0).to(device)
    attn = torch.ones_like(ids)
    fwd_kw = {"input_ids": ids, "attention_mask": attn}
    T = ids.shape[1]
    if img_inputs:
        for k, v in img_inputs.items():
            if v is None:
                continue
            if k == "mm_token_type_ids":
                tt = v.to(device)
                if tt.shape[1] < T:
                    pad = torch.zeros(tt.shape[0], T - tt.shape[1],
                                      dtype=tt.dtype, device=device)
                    tt = torch.cat([tt, pad], dim=1)
                elif tt.shape[1] > T:
                    tt = tt[:, :T]
                fwd_kw[k] = tt
            else:
                fwd_kw[k] = v.to(device)
    logits = model(**fwd_kw).logits
    log_probs = F.log_softmax(logits[:, :-1, :].float(), dim=-1)
    target = ids[:, 1:]
    token_lps = log_probs.gather(2, target.unsqueeze(-1)).squeeze(-1)
    return token_lps[0, prompt_len - 1: ids.shape[1] - 1]


def grpo_update(model, rollouts, optimizer, clip_eps, device, ppo_epochs=1):
    import torch
    step_loss = 0.0
    total_tokens = 0
    for _ in range(ppo_epochs):
        for r in rollouts:
            new_lp = completion_logprobs(model, r["full_ids"], r["prompt_len"],
                                         r["img_inputs"], device)
            old_lp = r["old_logprob"].detach()
            adv = torch.tensor(r["adv"], dtype=new_lp.dtype, device=new_lp.device)
            ratio = torch.exp(new_lp - old_lp)
            surr1 = adv * ratio
            surr2 = adv * torch.clamp(ratio, 1.0 - clip_eps, 1.0 + clip_eps)
            loss = -torch.min(surr1, surr2).sum()
            if new_lp.numel() == 0:
                continue
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(
                [p for p in model.parameters() if p.requires_grad], 1.0)
            optimizer.step()
            step_loss += float(loss.detach().item())
            total_tokens += new_lp.numel()
    return step_loss / max(1, len(rollouts)), total_tokens


def paired_bootstrap(items_a, items_b, n_boot=10000, seed=0):
    rng = np.random.default_rng(seed)
    n = len(items_a)
    if n == 0:
        return {"delta": 0.0, "ci_lo": 0.0, "ci_hi": 0.0, "p": 1.0, "n_boot": n_boot}
    a = np.array(items_a, dtype=float)
    b = np.array(items_b, dtype=float)
    obs_delta = float(b.mean() - a.mean())
    diffs = b - a
    boots = np.array([rng.choice(diffs, size=n, replace=True).mean()
                      for _ in range(n_boot)])
    ci_lo = float(np.percentile(boots, 2.5))
    ci_hi = float(np.percentile(boots, 97.5))
    if obs_delta >= 0:
        p = float((boots <= 0).mean())
    else:
        p = float((boots >= 0).mean())
    p = min(1.0, 2 * p)
    return {"delta": round(obs_delta, 4), "ci_lo": round(ci_lo, 4),
            "ci_hi": round(ci_hi, 4), "p": round(p, 4), "n_boot": n_boot}


def mcnemar_from_items(base_items, post_items):
    bm = {r["id"]: r["correct"] for r in base_items}
    pm = {r["id"]: r["correct"] for r in post_items}
    b = c = 0
    for qid in bm:
        before = bm[qid]
        after = pm.get(qid, before)
        if (not before) and after:
            b += 1
        elif before and (not after):
            c += 1
    p, bb, cc = mcnemar_exact(b, c)
    return {"b_improved": bb, "c_regressed": cc, "p_value": round(p, 5),
            "n_discordant": b + c}


def _verdict(base_acc, post_acc, p):
    if post_acc > base_acc and p < 0.05:
        return "✅ 显著提升（post-GRPO > 冷启动 AND McNemar p<0.05）"
    elif post_acc > base_acc:
        return f"🟡 有提升但未达显著（Δ={(post_acc-base_acc)*100:.1f}pp / p={p}）"
    elif post_acc == base_acc:
        return f"⚪ 持平（Δ=0 / p={p}）"
    else:
        return f"🔴 负结果（Δ={(post_acc-base_acc)*100:.1f}pp / p={p}）— GRPO 未带来增益"


def run_train(args):
    import torch
    device = args.device
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    model, processor = load_model_for_train(device)
    if args.init_adapter and os.path.isdir(args.init_adapter):
        from peft import PeftModel
        print(f"[grpo-v2] cold-start from SFT adapter: {args.init_adapter}", flush=True)
        model = PeftModel.from_pretrained(model, args.init_adapter, is_trainable=True)
    else:
        model = build_lora(model, args.seed, rank=args.lora_r,
                           alpha=args.lora_alpha, dropout=args.lora_dropout)
    model.print_trainable_parameters()

    model.eval()
    base_eval = eval_on_heldout(model, processor, device, "grpo_v2_coldstart_baseline")
    base_eval["adapter_dir"] = args.init_adapter or "(fresh LoRA, no cold-start)"
    base_eval["note"] = ("cold-start SFT adapter evaluated BEFORE any GRPO step; "
                         "this is the GRPOv2 baseline (post-GRPO compared against THIS).")
    json.dump(base_eval,
              open(os.path.join(args.output_dir, "grpo_v2_coldstart_baseline_eval.json"), "w"),
              ensure_ascii=False, indent=2)
    print(f"[grpo-v2] cold-start held-out baseline acc={base_eval['accuracy']} "
          f"(n={base_eval['n']}) -> grpo_v2_coldstart_baseline_eval.json", flush=True)
    model.train()
    trainable = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(trainable, lr=args.lr, weight_decay=0.0)

    cases = build_train_cases_v2(args.train_seed)
    eval_cases = make_eval_set()
    cheat = cheat_rate_check(cases, eval_cases)
    json.dump(cheat, open(os.path.join(args.output_dir, "cheat_rate_check.json"), "w"),
              ensure_ascii=False, indent=2)
    print(f"[grpo-v2] cheat_rate={cheat['cheat_rate']} (overlap={cheat['overlap_count']}) "
          f"| {len(cases)} hard train cases | B={args.batch_prompts} G={args.group_size} "
          f"steps={args.total_steps} lr={args.lr} device={device}", flush=True)

    rng = np.random.default_rng(args.seed)
    os.makedirs(args.output_dir, exist_ok=True)
    step, t0 = 0, time.time()
    log_reward, log_count = 0.0, 0
    train_log = []
    n_steps_with_grad = 0
    reward_level_counts = {"1.0": 0, "alpha": 0, "neg_beta": 0, "other": 0}
    total_rollouts = 0
    while step < args.total_steps:
        idxs = rng.choice(len(cases), size=args.batch_prompts, replace=False)
        all_rollouts, group_rewards = [], []
        for ci in idxs:
            c = cases[int(ci)]
            group = []
            for _ in range(args.group_size):
                try:
                    full_ids, plen, gen_text, img_inputs = sample_one(
                        model, processor, c["image"], c["question"], device,
                        args.max_new_tokens, args.temperature, args.top_p)
                    pred = parse_answer(c["kind"], gen_text)
                    rew = reward_for_v2(c["skill"], c["kind"], pred, c["gt"], c.get("gt_num"))
                except Exception as e:
                    gen_text, rew, pred = ("ERR:" + str(e), -BETA, "")
                    full_ids, plen, img_inputs = None, 0, None
                group.append({"full_ids": full_ids, "prompt_len": plen,
                              "img_inputs": img_inputs, "reward": float(rew),
                              "gen_text": gen_text, "pred": pred})
                if abs(rew - 1.0) < 1e-6:
                    reward_level_counts["1.0"] += 1
                elif abs(rew - ALPHA) < 1e-6:
                    reward_level_counts["alpha"] += 1
                elif abs(rew + BETA) < 1e-6:
                    reward_level_counts["neg_beta"] += 1
                else:
                    reward_level_counts["other"] += 1
                total_rollouts += 1
            rewards = np.array([g["reward"] for g in group], dtype=np.float64)
            mean, std = float(rewards.mean()), float(rewards.std())
            advs = (rewards - mean) / (std + 1e-4) if std > 1e-6 else np.zeros_like(rewards)
            if std > 1e-6:
                n_steps_with_grad += 1
            for g, adv in zip(group, advs):
                if g["full_ids"] is None:
                    continue
                with torch.no_grad():
                    old_lp = completion_logprobs(model, g["full_ids"], g["prompt_len"],
                                                 g["img_inputs"], device)
                g["old_logprob"] = old_lp
                g["adv"] = float(adv)
                all_rollouts.append(g)
            group_rewards.append(float(np.mean(rewards)))
        if not all_rollouts:
            step += 1
            continue
        loss_val, n_tok = grpo_update(model, all_rollouts, optimizer,
                                      args.clip_eps, device, args.ppo_epochs)
        step += 1
        mean_r = float(np.mean(group_rewards))
        log_reward += mean_r
        log_count += 1
        train_log.append({"step": step, "loss": round(loss_val, 6),
                          "reward_mean": round(mean_r, 4),
                          "n_rollouts": len(all_rollouts), "n_tokens": n_tok})
        if step % args.log_steps == 0 or step == 1:
            el = time.time() - t0
            sps = step / el
            eta = (args.total_steps - step) / max(0.1, sps)
            print(f"  step {step}/{args.total_steps} | loss {loss_val:.4f} | "
                  f"reward {log_reward/max(1,log_count):.3f} | rollouts {len(all_rollouts)} | "
                  f"grad_steps {n_steps_with_grad}/{step} | {sps:.2f} step/s | ETA {eta/60:.1f} min",
                  flush=True)
            log_reward, log_count = 0.0, 0
        if step % args.save_steps == 0:
            ckpt = os.path.join(args.output_dir, f"step{step}")
            model.save_pretrained(ckpt)
            print(f"  saved adapter -> {ckpt}", flush=True)
    final_ckpt = os.path.join(args.output_dir, f"step{args.total_steps}")
    model.save_pretrained(final_ckpt)
    summary_cfg = {"config": vars(args),
                   "reward_params": {"ALPHA": ALPHA, "BETA": BETA,
                                     "REG_EXACT_REL": REG_EXACT_REL,
                                     "REG_TOL_REL": REG_TOL_REL},
                   "cheat_rate_check": cheat,
                   "grad_signal": {"steps_with_grad": n_steps_with_grad,
                                    "steps_total": step,
                                    "frac_with_grad": round(n_steps_with_grad / max(1, step), 4)},
                   "reward_level_counts": reward_level_counts,
                   "total_rollouts": total_rollouts,
                   "reward_level_pct": {k: round(v / max(1, total_rollouts), 4)
                                         for k, v in reward_level_counts.items()},
                   "steps": train_log, "total_wall_s": time.time() - t0}
    json.dump(summary_cfg,
              open(os.path.join(args.output_dir, "training_log.json"), "w"),
              ensure_ascii=False, indent=2)
    print(f"[grpo-v2] saved final adapter -> {final_ckpt}", flush=True)
    print(f"[grpo-v2] grad signal: {n_steps_with_grad}/{step} steps had group_std>0 "
          f"({n_steps_with_grad/max(1,step)*100:.1f}%)", flush=True)
    print(f"[grpo-v2] reward levels: {reward_level_counts} "
          f"(pct={summary_cfg['reward_level_pct']})", flush=True)

    model.eval()
    post_eval = eval_on_heldout(model, processor, device, "grpo_v2_final")
    post_eval["adapter_dir"] = final_ckpt
    json.dump(post_eval, open(os.path.join(args.output_dir, "grpo_v2_eval.json"), "w"),
              ensure_ascii=False, indent=2)
    print(f"[grpo-v2] post-GRPO held-out acc={post_eval['accuracy']} "
          f"-> grpo_v2_eval.json", flush=True)

    mcn = mcnemar_from_items(base_eval["results"], post_eval["results"])
    base_correct = [1 if r["correct"] else 0 for r in base_eval["results"]]
    post_correct = [1 if r["correct"] else 0 for r in post_eval["results"]]
    boot = paired_bootstrap(base_correct, post_correct, n_boot=10000, seed=args.seed)
    paired = {"coldstart_acc": base_eval["accuracy"],
              "post_grpo_acc": post_eval["accuracy"],
              "delta_acc": round(post_eval["accuracy"] - base_eval["accuracy"], 4),
              "mcnemar": mcn, "paired_bootstrap": boot,
              "preregistered_criteria": "success = post-GRPO acc > coldstart acc AND McNemar p<0.05; "
                                        "negative/insignificant reported honestly.",
              "verdict": _verdict(base_eval["accuracy"], post_eval["accuracy"], mcn["p_value"])}
    json.dump(paired, open(os.path.join(args.output_dir, "grpo_v2_paired_test.json"), "w"),
              ensure_ascii=False, indent=2)
    print(f"[grpo-v2] PAIRED: coldstart={base_eval['accuracy']} post-GRPO={post_eval['accuracy']} "
          f"Δ={paired['delta_acc']} McNemar b={mcn['b_improved']} c={mcn['c_regressed']} "
          f"p={mcn['p_value']} bootstrap p={boot['p']} -> {paired['verdict']}", flush=True)
    del model
    torch.cuda.empty_cache()


def smoke_test(args):
    args.total_steps = 2
    args.batch_prompts = 2
    args.group_size = 4
    args.max_new_tokens = 40
    args.save_steps = 2
    args.log_steps = 1
    args.output_dir = os.path.join(OUT_DIR, "smoke")
    os.makedirs(args.output_dir, exist_ok=True)
    print("=== GRPOv2-MLLM smoke (full Qwen3.5-2B MLLM, GPU) ===", flush=True)
    run_train(args)
    adapter = os.path.join(args.output_dir, "step2", "adapter_config.json")
    eval_json = os.path.join(args.output_dir, "grpo_v2_eval.json")
    ok = os.path.isfile(adapter) and os.path.isfile(eval_json)
    print(f"  adapter_config.json exists: {os.path.isfile(adapter)}", flush=True)
    print(f"  grpo_v2_eval.json exists: {os.path.isfile(eval_json)}", flush=True)
    if ok:
        ev = json.load(open(eval_json))
        print(f"  held-out accuracy: {ev['accuracy']} (n={ev['n']})", flush=True)
    print(f"=== smoke {'PASS' if ok else 'FAIL'} ===", flush=True)
    return 0 if ok else 1


def parse_args():
    ap = argparse.ArgumentParser(description="Stage-2W GRPOv2 on full Qwen3.5-2B MLLM")
    ap.add_argument("--model_path", default=MODEL_PATH)
    ap.add_argument("--output_dir", default=OUT_DIR)
    ap.add_argument("--init_adapter", default=None,
                    help="冷启动 SFT adapter（默认 sft2_adapter_seed11，0.70，留 headroom）")
    ap.add_argument("--lora_r", type=int, default=8)
    ap.add_argument("--lora_alpha", type=int, default=16)
    ap.add_argument("--lora_dropout", type=float, default=0.05)
    ap.add_argument("--lr", type=float, default=1e-5)
    ap.add_argument("--total_steps", type=int, default=500)
    ap.add_argument("--batch_prompts", type=int, default=2)
    ap.add_argument("--group_size", type=int, default=4)
    ap.add_argument("--ppo_epochs", type=int, default=1)
    ap.add_argument("--clip_eps", type=float, default=0.2)
    ap.add_argument("--max_new_tokens", type=int, default=64)
    ap.add_argument("--temperature", type=float, default=0.8)
    ap.add_argument("--top_p", type=float, default=0.95)
    ap.add_argument("--seed", type=int, default=20261124)
    ap.add_argument("--log_steps", type=int, default=10)
    ap.add_argument("--save_steps", type=int, default=100)
    ap.add_argument("--train_seed", type=int, default=20261124)
    ap.add_argument("--smoke_test", action="store_true")
    ap.add_argument("--device", default="cuda", choices=["cuda", "cpu"])
    return ap.parse_args()


def main():
    args = parse_args()
    if args.smoke_test:
        return smoke_test(args)
    if args.init_adapter is None:
        args.init_adapter = os.path.join(HERE, "strengthen_runs", "sft2_adapter_seed11")
    run_train(args)


if __name__ == "__main__":
    sys.exit(main())
