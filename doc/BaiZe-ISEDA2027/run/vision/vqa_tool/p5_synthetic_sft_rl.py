#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""p5_synthetic_sft_rl.py -- P5 大规模合成波形数据 SFT + GRPO (用户令 2026-11-24 14:3x).

P4 调研通过后执行 P5：
  1. 批量合成 >=1000 波形图 + Q&A 对（8 技能：6 既有 + glitch_detect + multichannel_freq，
     覆盖 周期/幅度/占空比/边沿/毛刺/多通道；含噪声/干扰通道多样化）。
  2. SFT：Qwen3.5-2B 完整 MLLM + LoRA，GPU7，~3000 步。
  3. held-out 合成测试集（seed 隔离）评测 pre-SFT / post-SFT。
  4. 若 post-SFT > pre-SFT：GRPO 500 步（冷启动 SFT adapter，分解奖励，harder 数据）。
  5. 配对检验 McNemar + paired bootstrap；负结果照写。
  6. 反作弊：GT 从波形参数直接计算，train/eval seed 隔离，报 cheat_rate。

预注册判据（开跑前写明，跑完不改）：
  - SFT 有效 = post-SFT acc > pre-SFT acc（held-out n=64）
  - GRPO 成功 = post-GRPO acc > post-SFT acc AND McNemar p<0.05
  - 不显著/负结果照写，不粉饰。

用法（.17 GPU7）：
  PY=/nas_data/app.e0031982/miniforge3/envs/py310/bin/python
  CUDA_VISIBLE_DEVICES=7 $PY p5_synthetic_sft_rl.py --stage data
  CUDA_VISIBLE_DEVICES=7 $PY p5_synthetic_sft_rl.py --stage sft
  CUDA_VISIBLE_DEVICES=7 $PY p5_synthetic_sft_rl.py --stage grpo
  CUDA_VISIBLE_DEVICES=7 $PY p5_synthetic_sft_rl.py --stage all

作者: vision wake#1715 · project-internal
"""
import argparse, json, math, os, re, sys, time
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.environ.get("QWEN35_VQA_MODEL", "/nas_data/app.e0031982/models/Qwen3.5-2B")
OUT_DIR = os.path.join(HERE, "p5_runs")
os.makedirs(OUT_DIR, exist_ok=True)

from sft_rl_strengthen import (  # noqa: E402
    load_model_for_train, build_lora, sft_inputs, gen_answer, mcnemar_exact,
)
from synth_waveform_qa import (  # noqa: E402
    make_case, make_sft_record, parse_answer, is_correct,
    SKILLS, WAVEFORM_TYPES,
)
from baseline_waveform_vqa import (  # noqa: E402
    new_canvas, draw_signal,
)
from grpo_mllm_wave_v2 import (  # noqa: E402
    _add_noise, _add_distractor_channel, _render_wave, reward_for_v2,
    prompt_inputs, sample_one, completion_logprobs, grpo_update,
    paired_bootstrap, mcnemar_from_items, ALPHA, BETA,
)

# ---- P5 配置 ----
P5_SKILLS = list(SKILLS) + ["glitch_detect", "multichannel_freq"]
TRAIN_SEED = 20261124
EVAL_SEED = 20261125
N_PER_SKILL_TRAIN = 130   # 130 * 8 = 1040 >= 1000
N_PER_SKILL_EVAL = 8      # 8 * 8 = 64 held-out

# ============================ 新增技能渲染 ============================ #
def glitch_image(path, wtype, cycles, has_glitch, rng, amp_div=3.0):
    """渲染一个波形，可选注入一个毛刺（短暂尖峰偏离主信号）。"""
    _render_wave(path, wtype, cycles, amp_div=amp_div)
    if has_glitch:
        img = Image.open(path).convert("RGB")
        d = ImageDraw.Draw(img)
        x0, x1, mid = 40, 465, 130
        gx = int(rng.integers(x0 + 30, x1 - 30))
        spike_h = int(rng.integers(25, 55))
        spike_y = mid - amp_div * 40 - spike_h
        gw = 2
        d.line([(gx, mid), (gx, spike_y)], fill="blue", width=gw)
        d.line([(gx, spike_y), (gx + gw, spike_y)], fill="blue", width=gw)
        d.line([(gx + gw, spike_y), (gx + gw, mid)], fill="blue", width=gw)
        img.save(path)


def three_sine_image(path, ca, cb, cc, amp_div=1.7):
    """三通道正弦波 A(blue,top) B(green,middle) C(red,bottom)。"""
    img, d = new_canvas()
    x0, x1 = 40, 465
    pa = [(x, 60 - amp_div * 40 * np.sin(2 * np.pi * ca * (x - x0) / (x1 - x0))) for x in range(x0, x1)]
    pb = [(x, 130 - amp_div * 40 * np.sin(2 * np.pi * cb * (x - x0) / (x1 - x0))) for x in range(x0, x1)]
    pc = [(x, 200 - amp_div * 40 * np.sin(2 * np.pi * cc * (x - x0) / (x1 - x0))) for x in range(x0, x1)]
    draw_signal(d, pa, color="blue")
    draw_signal(d, pb, color="green")
    draw_signal(d, pc, color="red")
    d.text((x0 + 5, 30), "A (blue)", fill="blue")
    d.text((x0 + 5, 100), "B (green)", fill="green")
    d.text((x0 + 5, 170), "C (red)", fill="red")
    img.save(path)


def make_case_p5(skill, rng, img_dir, qid, noisy=True):
    """造一道 P5 题（8 技能）。既有 6 技能复用 make_case，可选加噪声/干扰。"""
    os.makedirs(img_dir, exist_ok=True)
    p = os.path.join(img_dir, f"q{qid}.png")
    if skill in SKILLS:
        case = make_case(skill, rng, img_dir, qid)
        if noisy:
            r = float(rng.random())
            if r < 0.45:
                _add_noise(case["image"], rng, sigma=float(rng.uniform(6.0, 16.0)))
            elif r < 0.60:
                _add_distractor_channel(case["image"], rng)
        case["source"] = "p5_synth"
        return case
    if skill == "glitch_detect":
        wt = WAVEFORM_TYPES[int(rng.integers(0, len(WAVEFORM_TYPES)))]
        cyc = int(rng.integers(2, 6))
        has_glitch = bool(rng.integers(0, 2))
        glitch_image(p, wt, cyc, has_glitch, rng)
        if noisy and bool(rng.integers(0, 2)):
            _add_noise(p, rng, sigma=float(rng.uniform(6.0, 14.0)))
        return {"id": f"q{qid}", "skill": skill, "image": p, "wtype": wt,
                "has_glitch": has_glitch,
                "question": "Does this waveform contain a glitch "
                            "(a brief unexpected spike that deviates from the "
                            "main signal)? Answer 'yes' or 'no'.",
                "gt": "yes" if has_glitch else "no", "kind": "yesno",
                "source": "p5_synth"}
    if skill == "multichannel_freq":
        cas = [float(rng.uniform(2.0, 6.0)) for _ in range(3)]
        order = np.argsort(cas)[::-1]
        if abs(cas[order[0]] - cas[order[1]]) < 0.6:
            cas[order[0]] = cas[order[1]] + 0.8
        three_sine_image(p, cas[0], cas[1], cas[2])
        if noisy and bool(rng.integers(0, 2)):
            _add_noise(p, rng, sigma=float(rng.uniform(6.0, 14.0)))
        labels = ["A", "B", "C"]
        gt = labels[int(np.argmax(cas))]
        return {"id": f"q{qid}", "skill": skill, "image": p, "cycles": cas,
                "question": "Three signals A (blue, top), B (green, middle), "
                            "and C (red, bottom) are shown. Which signal has the "
                            "HIGHER frequency? Answer A, B, or C.",
                "gt": gt, "kind": "abc", "source": "p5_synth"}
    raise ValueError(skill)

# ============================ 答案抽取 / 评分（P5 扩展） ============================ #
def parse_answer_p5(kind, answer):
    if kind == "yesno":
        low = answer.strip().lower()
        if "yes" in low:
            return "yes"
        if "no" in low:
            return "no"
        return ""
    if kind == "abc":
        m = re.findall(r"\b([ABCabc])\b", answer)
        return m[-1].upper() if m else ""
    return parse_answer(kind, answer)


def is_correct_p5(skill, kind, pred, gt, gt_num=None):
    if kind == "yesno":
        p = str(pred).strip().lower()
        return p in ("yes", "no") and p == str(gt).strip().lower()
    if kind == "abc":
        return str(pred).strip().upper() == str(gt).strip().upper()
    return is_correct(skill, kind, pred, gt, gt_num)


def reward_for_p5(skill, kind, pred, gt, gt_num=None):
    if kind in ("number", "percent"):
        return reward_for_v2(skill, kind, pred, gt, gt_num)
    return 1.0 if is_correct_p5(skill, kind, pred, gt, gt_num) else -BETA


def score_case_p5(c, answer):
    pred = parse_answer_p5(c["kind"], answer)
    ok = is_correct_p5(c["skill"], c["kind"], pred, c["gt"], c.get("gt_num"))
    rew = reward_for_p5(c["skill"], c["kind"], pred, c["gt"], c.get("gt_num"))
    return pred, ok, rew


# ============================ 数据集生成 ============================ #
def generate_p5_dataset():
    train_img = os.path.join(OUT_DIR, "p5_train_images")
    eval_img = os.path.join(OUT_DIR, "p5_eval_images")
    rng = np.random.default_rng(TRAIN_SEED)
    records, counts, qid = [], {s: 0 for s in P5_SKILLS}, 0
    for skill in P5_SKILLS:
        for _ in range(N_PER_SKILL_TRAIN):
            case = make_case_p5(skill, rng, train_img, qid, noisy=True)
            records.append(make_sft_record(case))
            counts[skill] += 1
            qid += 1
    sft_path = os.path.join(OUT_DIR, "sft_p5.jsonl")
    with open(sft_path, "w") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    rng2 = np.random.default_rng(EVAL_SEED)
    eval_cases, eqid = [], 0
    for skill in P5_SKILLS:
        for _ in range(N_PER_SKILL_EVAL):
            eval_cases.append(make_case_p5(skill, rng2, eval_img, eqid, noisy=False))
            eqid += 1
    eval_path = os.path.join(OUT_DIR, "eval_p5_cases.json")
    json.dump(eval_cases, open(eval_path, "w"), ensure_ascii=False, indent=2)
    train_imgs = set(os.path.abspath(r["image"]) for r in records)
    eval_imgs = set(os.path.abspath(c["image"]) for c in eval_cases)
    overlap = train_imgs & eval_imgs
    cheat = {"cheat_rate": round(len(overlap) / max(1, len(eval_imgs)), 4),
             "overlap_count": len(overlap),
             "train_seed": TRAIN_SEED, "eval_seed": EVAL_SEED,
             "note": "GT from waveform params; train/eval seed isolated."}
    meta = {"train_seed": TRAIN_SEED, "eval_seed": EVAL_SEED,
            "n_per_skill_train": N_PER_SKILL_TRAIN,
            "n_per_skill_eval": N_PER_SKILL_EVAL,
            "train_total": len(records), "eval_total": len(eval_cases),
            "counts": counts, "skills": P5_SKILLS, "cheat_check": cheat,
            "diversity": "8 skills; noise 6-16 on ~45%; distractor ~15%; 4 wf types"}
    json.dump(meta, open(os.path.join(OUT_DIR, "dataset_meta_p5.json"), "w"),
              ensure_ascii=False, indent=2)
    print(f"[p5-data] train={len(records)} -> {sft_path}", flush=True)
    print(f"[p5-data] eval={len(eval_cases)} -> {eval_path}", flush=True)
    print(f"[p5-data] cheat_rate={cheat['cheat_rate']} overlap={cheat['overlap_count']}", flush=True)
    print(f"[p5-data] counts={counts}", flush=True)
    return sft_path, eval_cases, meta


def load_eval_cases():
    p = os.path.join(OUT_DIR, "eval_p5_cases.json")
    if not os.path.isfile(p):
        _, cases, _ = generate_p5_dataset()
        return cases
    return json.load(open(p))


def eval_p5(model, processor, device, tag, eval_cases):
    results = []
    for c in eval_cases:
        t0 = time.time()
        try:
            ans = gen_answer(model, processor, c["image"], c["question"], device)
        except Exception as e:
            ans = "ERR:" + str(e)
        pred, ok, rew = score_case_p5(c, ans)
        results.append({"id": c["id"], "skill": c["skill"], "gt": c["gt"],
                        "answer": ans, "pred": pred, "correct": ok,
                        "reward": round(rew, 4), "latency_s": round(time.time() - t0, 2)})
        print(f"[eval {tag}] {c['id']} {c['skill']} gt={c['gt']} pred={pred} correct={ok}", flush=True)
    by_skill = {}
    for s in P5_SKILLS:
        rs = [r for r in results if r["skill"] == s]
        by_skill[s] = {"n": len(rs), "correct": sum(r["correct"] for r in rs),
                       "acc": round(sum(r["correct"] for r in rs) / max(1, len(rs)), 4)}
    summary = {"tag": tag, "n": len(results),
               "correct": sum(r["correct"] for r in results),
               "accuracy": round(sum(r["correct"] for r in results) / max(1, len(results)), 4),
               "skill_acc": by_skill, "results": results,
               "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
    out = os.path.join(OUT_DIR, f"{tag}_eval.json")
    json.dump(summary, open(out, "w"), ensure_ascii=False, indent=2)
    print(f"=== EVAL {tag} acc={summary['accuracy']} (n={summary['n']}) -> {out}", flush=True)
    return summary

# ============================ SFT 训练 ============================ #
def train_sft_p5(seed, epochs, records, device="cuda", max_steps=None, tag_prefix="sft_p5"):
    import torch
    print(f"\n===== P5 SFT seed={seed} epochs={epochs} n_records={len(records)} =====", flush=True)
    model, processor = load_model_for_train(device)
    model = build_lora(model, seed)
    model.train()
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=1e-4)
    rng = np.random.default_rng(seed)
    step, t_start, losses = 0, time.time(), []
    for ep in range(epochs):
        order = rng.permutation(len(records))
        for idx in order:
            rec = records[int(idx)]
            try:
                inputs = sft_inputs(processor, rec["image"],
                                    rec["messages"][0]["content"][1]["text"],
                                    rec["messages"][1]["content"])
            except Exception as e:
                print(f"[train] skip {rec.get('id')}: {e}", flush=True)
                continue
            inputs = {k: v.to(device) for k, v in inputs.items()}
            opt.zero_grad()
            out = model(**inputs)
            loss = out.loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad], 1.0)
            opt.step()
            step += 1
            losses.append(float(loss.item()))
            if step % 25 == 0 or step == 1:
                el = time.time() - t_start
                print(f"[p5-train seed={seed}] ep{ep} step={step} loss={loss.item():.4f} avg25={np.mean(losses[-25:]):.4f} {el/max(1,step):.2f}s/step", flush=True)
            if max_steps and step >= max_steps:
                break
        if max_steps and step >= max_steps:
            break
    adapter_dir = os.path.join(OUT_DIR, f"{tag_prefix}_adapter_seed{seed}")
    model.save_pretrained(adapter_dir)
    print(f"[p5-train] saved adapter -> {adapter_dir} (steps={step})", flush=True)
    json.dump({"seed": seed, "epochs": epochs, "steps": step, "n_records": len(records),
               "final_loss_avg25": round(float(np.mean(losses[-25:])), 4),
               "adapter_dir": adapter_dir, "wall_s": round(time.time() - t_start, 1)},
              open(os.path.join(OUT_DIR, f"{tag_prefix}_train_meta.json"), "w"),
              ensure_ascii=False, indent=2)
    return model, processor, adapter_dir, step


def stage_sft(args):
    import torch
    device = args.device
    eval_cases = load_eval_cases()
    sft_path = os.path.join(OUT_DIR, "sft_p5.jsonl")
    if not os.path.isfile(sft_path):
        generate_p5_dataset()
    records = [json.loads(l) for l in open(sft_path) if l.strip()]
    print(f"[p5-sft] {len(records)} train records, eval n={len(eval_cases)}", flush=True)
    model, processor = load_model_for_train(device)
    model.eval()
    pre = eval_p5(model, processor, device, "p5_pre_sft", eval_cases)
    json.dump(pre, open(os.path.join(OUT_DIR, "p5_pre_sft_eval.json"), "w"), ensure_ascii=False, indent=2)
    del model
    torch.cuda.empty_cache()
    model, processor, adapter_dir, nsteps = train_sft_p5(args.seed, args.epochs, records, device=device, max_steps=args.max_steps)
    post = eval_p5(model, processor, device, "p5_post_sft", eval_cases)
    json.dump(post, open(os.path.join(OUT_DIR, "p5_post_sft_eval.json"), "w"), ensure_ascii=False, indent=2)
    mcn = mcnemar_from_items(pre["results"], post["results"])
    bc = [1 if r["correct"] else 0 for r in pre["results"]]
    pc = [1 if r["correct"] else 0 for r in post["results"]]
    boot = paired_bootstrap(bc, pc, n_boot=10000, seed=args.seed)
    sft_paired = {"pre_sft_acc": pre["accuracy"], "post_sft_acc": post["accuracy"],
                  "delta_acc": round(post["accuracy"] - pre["accuracy"], 4),
                  "sft_steps": nsteps, "adapter_dir": adapter_dir,
                  "mcnemar": mcn, "paired_bootstrap": boot,
                  "sft_effective": post["accuracy"] > pre["accuracy"],
                  "preregistered": "SFT effective = post-SFT acc > pre-SFT acc"}
    json.dump(sft_paired, open(os.path.join(OUT_DIR, "p5_sft_paired_test.json"), "w"), ensure_ascii=False, indent=2)
    print(f"[p5-sft] pre={pre['accuracy']} post={post['accuracy']} delta={sft_paired['delta_acc']} McNemar b={mcn['b_improved']} c={mcn['c_regressed']} p={mcn['p_value']} effective={sft_paired['sft_effective']}", flush=True)
    del model
    torch.cuda.empty_cache()
    return sft_paired, adapter_dir

# ============================ GRPO 训练（P5） ============================ #
def build_train_cases_p5(seed, n_per_skill=20, img_subdir="grpo_p5_train_images"):
    img_dir = os.path.join(OUT_DIR, img_subdir)
    os.makedirs(img_dir, exist_ok=True)
    rng = np.random.default_rng(seed)
    cases, qid = [], 0
    for skill in P5_SKILLS:
        for _ in range(n_per_skill):
            cases.append(make_case_p5(skill, rng, img_dir, qid, noisy=True))
            qid += 1
    return cases


def _verdict_p5(base_acc, post_acc, p):
    if post_acc > base_acc and p < 0.05:
        return "SIGNIFICANT (post-GRPO > post-SFT AND p<0.05)"
    elif post_acc > base_acc:
        return f"improved not significant (delta={(post_acc-base_acc)*100:.1f}pp p={p})"
    elif post_acc == base_acc:
        return f"tie (delta=0 p={p})"
    else:
        return f"NEGATIVE (delta={(post_acc-base_acc)*100:.1f}pp p={p}) GRPO no gain"


def run_grpo_p5(args, init_adapter, eval_cases):
    import torch
    device = args.device
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    model, processor = load_model_for_train(device)
    if init_adapter and os.path.isdir(init_adapter):
        from peft import PeftModel
        print(f"[grpo-p5] cold-start from SFT adapter: {init_adapter}", flush=True)
        model = PeftModel.from_pretrained(model, init_adapter, is_trainable=True)
    else:
        model = build_lora(model, args.seed)
    model.print_trainable_parameters()
    model.eval()
    base_eval = eval_p5(model, processor, device, "grpo_p5_coldstart", eval_cases)
    base_eval["adapter_dir"] = init_adapter or "(fresh LoRA)"
    json.dump(base_eval, open(os.path.join(OUT_DIR, "grpo_p5_coldstart_eval.json"), "w"), ensure_ascii=False, indent=2)
    model.train()
    trainable = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(trainable, lr=args.lr, weight_decay=0.0)
    cases = build_train_cases_p5(args.train_seed)
    tr_imgs = set(os.path.abspath(c["image"]) for c in cases)
    ev_imgs = set(os.path.abspath(c["image"]) for c in eval_cases)
    cheat = {"cheat_rate": round(len(tr_imgs & ev_imgs) / max(1, len(ev_imgs)), 4),
             "overlap_count": len(tr_imgs & ev_imgs), "train_seed": args.train_seed, "eval_seed": EVAL_SEED}
    json.dump(cheat, open(os.path.join(OUT_DIR, "grpo_p5_cheat_check.json"), "w"), ensure_ascii=False, indent=2)
    print(f"[grpo-p5] {len(cases)} hard cases | cheat={cheat['cheat_rate']} | B={args.batch_prompts} G={args.group_size} steps={args.total_steps}", flush=True)
    rng = np.random.default_rng(args.seed)
    step, t0 = 0, time.time()
    log_reward, log_count = 0.0, 0
    train_log, n_grad = [], 0
    rew_levels = {"1.0": 0, "alpha": 0, "neg_beta": 0, "other": 0}
    total_rollouts = 0
    while step < args.total_steps:
        idxs = rng.choice(len(cases), size=args.batch_prompts, replace=False)
        all_rollouts, group_rewards = [], []
        for ci in idxs:
            c = cases[int(ci)]
            group = []
            for _ in range(args.group_size):
                try:
                    full_ids, plen, gen_text, img_inputs = sample_one(model, processor, c["image"], c["question"], device, args.max_new_tokens, args.temperature, args.top_p)
                    pred = parse_answer_p5(c["kind"], gen_text)
                    rew = reward_for_p5(c["skill"], c["kind"], pred, c["gt"], c.get("gt_num"))
                except Exception as e:
                    gen_text, rew, pred = ("ERR:" + str(e), -BETA, "")
                    full_ids, plen, img_inputs = None, 0, None
                group.append({"full_ids": full_ids, "prompt_len": plen, "img_inputs": img_inputs, "reward": float(rew), "gen_text": gen_text, "pred": pred})
                if abs(rew - 1.0) < 1e-6:
                    rew_levels["1.0"] += 1
                elif abs(rew - ALPHA) < 1e-6:
                    rew_levels["alpha"] += 1
                elif abs(rew + BETA) < 1e-6:
                    rew_levels["neg_beta"] += 1
                else:
                    rew_levels["other"] += 1
                total_rollouts += 1
            rewards = np.array([g["reward"] for g in group], dtype=np.float64)
            mean, std = float(rewards.mean()), float(rewards.std())
            advs = (rewards - mean) / (std + 1e-4) if std > 1e-6 else np.zeros_like(rewards)
            if std > 1e-6:
                n_grad += 1
            for g, adv in zip(group, advs):
                if g["full_ids"] is None:
                    continue
                with torch.no_grad():
                    old_lp = completion_logprobs(model, g["full_ids"], g["prompt_len"], g["img_inputs"], device)
                g["old_logprob"] = old_lp
                g["adv"] = float(adv)
                all_rollouts.append(g)
            group_rewards.append(float(np.mean(rewards)))
        if not all_rollouts:
            step += 1
            continue
        loss_val, n_tok = grpo_update(model, all_rollouts, optimizer, args.clip_eps, device, args.ppo_epochs)
        step += 1
        mean_r = float(np.mean(group_rewards))
        log_reward += mean_r
        log_count += 1
        train_log.append({"step": step, "loss": round(loss_val, 6), "reward_mean": round(mean_r, 4), "n_rollouts": len(all_rollouts), "n_tokens": n_tok})
        if step % args.log_steps == 0 or step == 1:
            el = time.time() - t0
            sps = step / el
            eta = (args.total_steps - step) / max(0.1, sps)
            print(f"  step {step}/{args.total_steps} | loss {loss_val:.4f} | reward {log_reward/max(1,log_count):.3f} | grad {n_grad}/{step} | {sps:.2f} step/s | ETA {eta/60:.1f}min", flush=True)
            log_reward, log_count = 0.0, 0
        if step % args.save_steps == 0:
            ckpt = os.path.join(OUT_DIR, f"grpo_p5/step{step}")
            model.save_pretrained(ckpt)
            print(f"  saved -> {ckpt}", flush=True)
    final_ckpt = os.path.join(OUT_DIR, f"grpo_p5/step{args.total_steps}")
    model.save_pretrained(final_ckpt)
    summary_cfg = {"config": vars(args), "reward_params": {"ALPHA": ALPHA, "BETA": BETA}, "cheat_check": cheat, "grad_signal": {"steps_with_grad": n_grad, "steps_total": step, "frac": round(n_grad / max(1, step), 4)}, "reward_level_counts": rew_levels, "total_rollouts": total_rollouts, "reward_level_pct": {k: round(v / max(1, total_rollouts), 4) for k, v in rew_levels.items()}, "steps": train_log, "total_wall_s": time.time() - t0}
    json.dump(summary_cfg, open(os.path.join(OUT_DIR, "grpo_p5_training_log.json"), "w"), ensure_ascii=False, indent=2)
    print(f"[grpo-p5] grad signal {n_grad}/{step} ({n_grad/max(1,step)*100:.1f}%)", flush=True)
    model.eval()
    post_eval = eval_p5(model, processor, device, "grpo_p5_final", eval_cases)
    post_eval["adapter_dir"] = final_ckpt
    json.dump(post_eval, open(os.path.join(OUT_DIR, "grpo_p5_final_eval.json"), "w"), ensure_ascii=False, indent=2)
    mcn = mcnemar_from_items(base_eval["results"], post_eval["results"])
    bc = [1 if r["correct"] else 0 for r in base_eval["results"]]
    pc = [1 if r["correct"] else 0 for r in post_eval["results"]]
    boot = paired_bootstrap(bc, pc, n_boot=10000, seed=args.seed)
    paired = {"coldstart_acc": base_eval["accuracy"], "post_grpo_acc": post_eval["accuracy"], "delta_acc": round(post_eval["accuracy"] - base_eval["accuracy"], 4), "mcnemar": mcn, "paired_bootstrap": boot, "verdict": _verdict_p5(base_eval["accuracy"], post_eval["accuracy"], mcn["p_value"])}
    json.dump(paired, open(os.path.join(OUT_DIR, "grpo_p5_paired_test.json"), "w"), ensure_ascii=False, indent=2)
    print(f"[grpo-p5] PAIRED coldstart={base_eval['accuracy']} post={post_eval['accuracy']} delta={paired['delta_acc']} McNemar b={mcn['b_improved']} c={mcn['c_regressed']} p={mcn['p_value']} -> {paired['verdict']}", flush=True)
    del model
    torch.cuda.empty_cache()
    return paired, post_eval

# ============================ 汇总 / 主流程 ============================ #
def write_final_report(args, sft_paired, grpo_paired, pre_eval, post_sft_eval, grpo_eval):
    n = len(load_eval_cases())
    report = {"task": "P5 synthetic waveform data SFT + GRPO", "wake": "wake#1715",
              "date": time.strftime("%Y-%m-%d"), "model": "Qwen3.5-2B (native VL) + LoRA",
              "gpu": "GPU7 (.17)", "train_total": N_PER_SKILL_TRAIN * len(P5_SKILLS),
              "eval_n": n, "skills": P5_SKILLS,
              "stages": {"pre_sft": {"acc": pre_eval["accuracy"], "correct": pre_eval["correct"], "skill_acc": pre_eval["skill_acc"]},
                         "post_sft": {"acc": post_sft_eval["accuracy"], "correct": post_sft_eval["correct"], "skill_acc": post_sft_eval["skill_acc"], "sft_paired": sft_paired},
                         "post_grpo": {"acc": grpo_eval["accuracy"], "correct": grpo_eval["correct"], "skill_acc": grpo_eval["skill_acc"], "grpo_paired": grpo_paired}},
              "preregistered_criteria": {"sft_effective": "post-SFT acc > pre-SFT acc", "grpo_success": "post-GRPO acc > post-SFT acc AND McNemar p<0.05", "negative_reported_honestly": True},
              "cheat_rate": "train/eval seed isolated (20261124 vs 20261125); GT from params"}
    json.dump(report, open(os.path.join(OUT_DIR, "p5_results.json"), "w"), ensure_ascii=False, indent=2)
    print(f"[p5] final report -> {os.path.join(OUT_DIR, 'p5_results.json')}", flush=True)


def parse_args():
    ap = argparse.ArgumentParser(description="P5 synthetic waveform SFT + GRPO")
    ap.add_argument("--stage", default="all", choices=["data", "sft", "grpo", "all"])
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--max_steps", type=int, default=3120)
    ap.add_argument("--lr", type=float, default=1e-5)
    ap.add_argument("--total_steps", type=int, default=500)
    ap.add_argument("--batch_prompts", type=int, default=2)
    ap.add_argument("--group_size", type=int, default=4)
    ap.add_argument("--ppo_epochs", type=int, default=1)
    ap.add_argument("--clip_eps", type=float, default=0.2)
    ap.add_argument("--max_new_tokens", type=int, default=64)
    ap.add_argument("--temperature", type=float, default=0.8)
    ap.add_argument("--top_p", type=float, default=0.95)
    ap.add_argument("--log_steps", type=int, default=10)
    ap.add_argument("--save_steps", type=int, default=100)
    ap.add_argument("--train_seed", type=int, default=20261124)
    ap.add_argument("--init_adapter", default=None)
    return ap.parse_args()


def main():
    args = parse_args()
    if args.stage == "data":
        generate_p5_dataset()
        return
    if args.stage == "sft":
        stage_sft(args)
        return
    if args.stage == "grpo":
        adapter = args.init_adapter or os.path.join(OUT_DIR, "sft_p5_adapter_seed11")
        run_grpo_p5(args, adapter, load_eval_cases())
        return
    if args.stage == "all":
        generate_p5_dataset()
        sft_paired, adapter_dir = stage_sft(args)
        grpo_paired, grpo_eval = run_grpo_p5(args, adapter_dir, load_eval_cases())
        pre = json.load(open(os.path.join(OUT_DIR, "p5_pre_sft_eval.json")))
        post_sft = json.load(open(os.path.join(OUT_DIR, "p5_post_sft_eval.json")))
        write_final_report(args, sft_paired, grpo_paired, pre, post_sft, grpo_eval)
        return


if __name__ == "__main__":
    sys.exit(main())
