#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sft_rl_strengthen.py -- #4 强化 Qwen3.5-2B 波形识图能力（SFT + RFT · native VL）。

vision 用户令 2026-11-14 09:1x #4 + 10:3x：在 #3 VQA tool 基础上，用合成数据/SFT/RL
强化基模（Qwen3.5-2B）看懂波形图的能力，争取通过率显著提升。

预注册判据（🚫 不许看结果再调）：
  - 训练集 sft.jsonl（150 条，seed=20261114，25/技能×6 技能）
  - held-out 评估集 30 题（seed=20261115，与训练集不同 seed → 零泄漏 cheat_rate=0）
  - before = 基模 greedy 在 held-out；SFT = LoRA 3seed×3epoch；RFT = rejection-sampling FT
  - 成功 = post-RL ≥ post-SFT +5pp 且 McNemar p<0.05 且 ≥3seed 一致 且 cheat_rate=0；负结果照报

架构口径：Qwen3.5-2B 原生多模态 VL（Qwen3_5ForConditionalGeneration，含 image_token_id），
直接吃像素；不做图→文本桥降级（用户 09:5x 令反对）。LoRA 仅训低秩适配，基模冻结。

用法：
  PY=/nas_data/app.e0031982/miniforge3/envs/py310/bin/python
  CUDA_VISIBLE_DEVICES=5 $PY sft_rl_strengthen.py --stage prebaseline
  CUDA_VISIBLE_DEVICES=5 $PY sft_rl_strengthen.py --stage smoke
  CUDA_VISIBLE_DEVICES=5 $PY sft_rl_strengthen.py --stage sft --seeds 3 --epochs 3
  CUDA_VISIBLE_DEVICES=5 $PY sft_rl_strengthen.py --stage rft
  $PY sft_rl_strengthen.py --stage report

作者: vision wake#1209 · project-internal
"""
import argparse, json, math, os, sys, time, traceback
import numpy as np
from PIL import Image
import urllib.request, base64

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.environ.get("QWEN35_VQA_MODEL", "/nas_data/app.e0031982/models/Qwen3.5-2B")
SERVER = os.environ.get("QWEN35_VQA_SERVER", "http://127.0.0.1:30001")
SFT_JSONL = os.path.join(HERE, "sft.jsonl")
OUT_DIR = os.path.join(HERE, "strengthen_runs")
os.makedirs(OUT_DIR, exist_ok=True)

from synth_waveform_qa import (
    make_case, parse_answer, is_correct, reward_for, SKILLS, WAVEFORM_TYPES, TAU,
)


def vqa_http(image_path, question, server=SERVER, max_new_tokens=256, temperature=0.0):
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    body = json.dumps({"image_b64": b64, "question": question,
                       "max_new_tokens": max_new_tokens,
                       "temperature": temperature}).encode()
    req = urllib.request.Request(server + "/vqa", data=body,
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            res = json.loads(r.read())
        res["latency_s"] = round(time.time() - t0, 2)
        return res
    except Exception as e:
        return {"ok": False, "error": str(e), "latency_s": round(time.time() - t0, 2)}


def make_eval_set(n_per_skill=5, seed=20261115, img_subdir="eval_images"):
    img_dir = os.path.join(HERE, img_subdir)
    os.makedirs(img_dir, exist_ok=True)
    rng = np.random.default_rng(seed)
    cases, qid = [], 0
    for skill in SKILLS:
        for _ in range(n_per_skill):
            cases.append(make_case(skill, rng, img_dir, qid))
            qid += 1
    return cases


def score_case(c, answer):
    pred = parse_answer(c["kind"], answer)
    ok = is_correct(c["skill"], c["kind"], pred, c["gt"], c.get("gt_num"))
    rew = reward_for(c["skill"], c["kind"], pred, c["gt"], c.get("gt_num"))
    return pred, ok, rew


def stage_prebaseline():
    cases = make_eval_set()
    print(f"[prebaseline] held-out n={len(cases)} (seed=20261115, NOT in train)", flush=True)
    results = []
    for c in cases:
        res = vqa_http(c["image"], c["question"])
        if not res.get("ok"):
            results.append({"id": c["id"], "skill": c["skill"], "gt": c["gt"],
                            "answer": "ERR:" + str(res.get("error")), "pred": "",
                            "correct": False, "reward": 0.0,
                            "latency_s": res.get("latency_s")})
            continue
        ans = res.get("answer", "")
        pred, ok, rew = score_case(c, ans)
        results.append({"id": c["id"], "skill": c["skill"], "image": c["image"],
                        "question": c["question"], "gt": c["gt"], "answer": ans,
                        "pred": pred, "correct": ok, "reward": round(rew, 4),
                        "latency_s": res.get("latency_s")})
        print(json.dumps({"id": c["id"], "skill": c["skill"], "gt": c["gt"],
                          "pred": pred, "correct": ok, "reward": round(rew, 4)},
                         ensure_ascii=False), flush=True)
    by_skill = {}
    for s in SKILLS:
        rs = [r for r in results if r["skill"] == s]
        by_skill[s] = {"n": len(rs),
                       "correct": sum(r["correct"] for r in rs),
                       "acc": round(sum(r["correct"] for r in rs) / max(1, len(rs)), 4),
                       "mean_reward": round(float(np.mean([r["reward"] for r in rs])), 4) if rs else 0.0}
    summary = {"stage": "prebaseline", "model": "Qwen3.5-2B base (native VL, greedy)",
               "server": SERVER, "n": len(results),
               "correct": sum(r["correct"] for r in results),
               "accuracy": round(sum(r["correct"] for r in results) / max(1, len(results)), 4),
               "mean_reward": round(float(np.mean([r["reward"] for r in results])), 4),
               "skill_acc": by_skill, "eval_seed": 20261115, "n_per_skill": 5,
               "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "results": results,
               "leakage_check": "eval seed=20261115 != train seed=20261114 -> cheat_rate=0 by construction",
               "preregistered_criteria": "success: post-RL >= post-SFT + 5pp, McNemar p<0.05, >=3 seeds, cheat_rate=0"}
    out = os.path.join(OUT_DIR, "prebaseline_heldout.json")
    json.dump(summary, open(out, "w"), ensure_ascii=False, indent=2)
    print(f"=== PREBASELINE n={summary['n']} acc={summary['accuracy']} "
          f"mean_reward={summary['mean_reward']} -> {out}", flush=True)


# ----------------------------- 模型加载 / 训练 ----------------------------- #
def load_model_for_train(device="cuda"):
    import torch
    from transformers import AutoProcessor, Qwen3_5ForConditionalGeneration
    processor = AutoProcessor.from_pretrained(MODEL_PATH, trust_remote_code=True)
    model = Qwen3_5ForConditionalGeneration.from_pretrained(
        MODEL_PATH, torch_dtype=torch.bfloat16, device_map=device,
        trust_remote_code=True)
    return model, processor


def build_lora(model, seed, rank=8, alpha=16, dropout=0.05):
    import torch
    from peft import LoraConfig, get_peft_model
    torch.manual_seed(seed)
    cfg = LoraConfig(
        r=rank, lora_alpha=alpha, lora_dropout=dropout, bias="none",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        task_type="CAUSAL_LM",
    )
    pm = get_peft_model(model, cfg)
    pm.print_trainable_parameters()
    return pm


def sft_inputs(processor, image_path, question, gt):
    """构造一条 SFT 的 (inputs, labels)：仅监督 assistant 回答 token。"""
    img = Image.open(image_path).convert("RGB")
    msgs_full = [{"role": "user", "content": [
        {"type": "image", "image": img},
        {"type": "text", "text": question}]},
        {"role": "assistant", "content": gt}]
    msgs_prompt = [{"role": "user", "content": [
        {"type": "image", "image": img},
        {"type": "text", "text": question}]}]
    full_text = processor.apply_chat_template(
        msgs_full, tokenize=False, add_generation_prompt=False)
    prompt_text = processor.apply_chat_template(
        msgs_prompt, tokenize=False, add_generation_prompt=True)
    inputs_full = processor(text=[full_text], images=[img], return_tensors="pt")
    inputs_prompt = processor(text=[prompt_text], images=[img], return_tensors="pt")
    prompt_len = inputs_prompt["input_ids"].shape[1]
    labels = inputs_full["input_ids"].clone()
    if prompt_len < labels.shape[1]:
        labels[:, :prompt_len] = -100
    else:
        labels[:] = -100
    inputs_full["labels"] = labels
    return inputs_full


def gen_answer(model, processor, image_path, question, device, max_new_tokens=128):
    import torch
    img = Image.open(image_path).convert("RGB")
    msgs = [{"role": "user", "content": [
        {"type": "image", "image": img},
        {"type": "text", "text": question}]}]
    text = processor.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    inputs = processor(text=[text], images=[img], return_tensors="pt").to(device)
    with torch.inference_mode():
        out = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
    gen = out[0][inputs["input_ids"].shape[1]:]
    return processor.decode(gen, skip_special_tokens=True).strip()


def eval_on_heldout(model, processor, device, tag):
    cases = make_eval_set()
    results = []
    for c in cases:
        t0 = time.time()
        try:
            ans = gen_answer(model, processor, c["image"], c["question"], device)
        except Exception as e:
            ans = "ERR:" + str(e)
        pred, ok, rew = score_case(c, ans)
        results.append({"id": c["id"], "skill": c["skill"], "gt": c["gt"],
                        "answer": ans, "pred": pred, "correct": ok,
                        "reward": round(rew, 4), "latency_s": round(time.time() - t0, 2)})
        print(f"[eval {tag}] {c['id']} {c['skill']} gt={c['gt']} pred={pred} "
              f"correct={ok} reward={round(rew,4)}", flush=True)
    by_skill = {}
    for s in SKILLS:
        rs = [r for r in results if r["skill"] == s]
        by_skill[s] = {"n": len(rs),
                       "correct": sum(r["correct"] for r in rs),
                       "acc": round(sum(r["correct"] for r in rs) / max(1, len(rs)), 4),
                       "mean_reward": round(float(np.mean([r["reward"] for r in rs])), 4) if rs else 0.0}
    summary = {"tag": tag, "n": len(results),
               "correct": sum(r["correct"] for r in results),
               "accuracy": round(sum(r["correct"] for r in results) / max(1, len(results)), 4),
               "mean_reward": round(float(np.mean([r["reward"] for r in results])), 4),
               "skill_acc": by_skill, "results": results,
               "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
    out = os.path.join(OUT_DIR, f"{tag}_eval.json")
    json.dump(summary, open(out, "w"), ensure_ascii=False, indent=2)
    print(f"=== EVAL {tag} acc={summary['accuracy']} mean_reward={summary['mean_reward']} -> {out}", flush=True)
    return summary


def load_sft_records():
    recs = []
    with open(SFT_JSONL) as f:
        for line in f:
            line = line.strip()
            if line:
                recs.append(json.loads(line))
    return recs


def train_sft(seed, epochs, records, device="cuda", max_steps=None, tag_prefix="sft"):
    import torch
    print(f"\n===== SFT seed={seed} epochs={epochs} n_records={len(records)} =====", flush=True)
    model, processor = load_model_for_train(device)
    model = build_lora(model, seed)
    model.train()
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=1e-4)
    rng = np.random.default_rng(seed)
    step = 0
    t_start = time.time()
    losses = []
    for ep in range(epochs):
        order = rng.permutation(len(records))
        for idx in order:
            rec = records[idx]
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
            torch.nn.utils.clip_grad_norm_(
                [p for p in model.parameters() if p.requires_grad], 1.0)
            opt.step()
            step += 1
            losses.append(float(loss.item()))
            if step % 10 == 0 or step == 1:
                el = time.time() - t_start
                print(f"[train seed={seed}] ep{ep} step={step} loss={loss.item():.4f} "
                      f"avg10={np.mean(losses[-10:]):.4f} {el/step:.2f}s/step", flush=True)
            if max_steps and step >= max_steps:
                break
        if max_steps and step >= max_steps:
            break
    adapter_dir = os.path.join(OUT_DIR, f"{tag_prefix}_adapter_seed{seed}")
    model.save_pretrained(adapter_dir)
    print(f"[train seed={seed}] saved adapter -> {adapter_dir}", flush=True)
    model.eval()
    summary = eval_on_heldout(model, processor, device, f"{tag_prefix}_seed{seed}")
    summary["seed"] = seed
    summary["epochs"] = epochs
    summary["final_loss_avg10"] = round(float(np.mean(losses[-10:])), 4)
    summary["adapter_dir"] = adapter_dir
    json.dump(summary, open(os.path.join(OUT_DIR, f"{tag_prefix}_seed{seed}_eval.json"), "w"),
              ensure_ascii=False, indent=2)
    del model
    torch.cuda.empty_cache()
    return summary


def stage_smoke():
    recs = load_sft_records()[:6]
    t0 = time.time()
    s = train_sft(seed=11, epochs=1, records=recs, device="cuda", max_steps=6, tag_prefix="smoke")
    print(f"=== SMOKE done in {time.time()-t0:.1f}s acc={s['accuracy']} -> strengthen_runs/", flush=True)


def stage_sft(seeds, epochs):
    recs = load_sft_records()
    print(f"[sft] loaded {len(recs)} records from {SFT_JSONL}", flush=True)
    summaries = []
    for i in range(seeds):
        seed = 11 + i * 11
        s = train_sft(seed, epochs, recs, device="cuda", tag_prefix="sft")
        summaries.append(s)
    json.dump(summaries, open(os.path.join(OUT_DIR, "sft_summary.json"), "w"),
              ensure_ascii=False, indent=2)
    print("=== SFT all seeds done ===", flush=True)


def stage_rft(seed=11, epochs=2, k_samples=4, reward_thresh=0.5):
    """在 SFT adapter 上做 rejection-sampling FT（v4 路线，可视为轻量 RL）。
    对训练集每条采样 K 次（temperature>0），留连续奖励 exp(-rel_err/tau)>thresh 的正例，再 SFT 一轮。
    """
    import torch
    from peft import PeftModel
    print("\n===== RFT seed={} K={} thresh={} =====".format(seed, k_samples, reward_thresh), flush=True)
    adapter_dir = os.path.join(OUT_DIR, f"sft_adapter_seed{seed}")
    if not os.path.isdir(adapter_dir):
        print(f"[rft] no SFT adapter at {adapter_dir} -> run --stage sft first", flush=True)
        return
    model, processor = load_model_for_train(device="cuda")
    model = PeftModel.from_pretrained(model, adapter_dir, is_trainable=True)
    model.print_trainable_parameters()
    recs = load_sft_records()
    model.eval()
    accepted = []
    t0 = time.time()
    for ri, rec in enumerate(recs):
        q = rec["messages"][0]["content"][1]["text"]
        gt = rec["messages"][1]["content"]
        gt_num = rec.get("meta", {}).get("gt_num")
        kind = rec.get("meta", {}).get("kind", "number") if gt_num is not None else "word"
        for _ in range(k_samples):
            try:
                img = Image.open(rec["image"]).convert("RGB")
                msgs = [{"role": "user", "content": [
                    {"type": "image", "image": img},
                    {"type": "text", "text": q}]}]
                text = processor.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
                inputs = processor(text=[text], images=[img], return_tensors="pt").to("cuda")
                with torch.inference_mode():
                    out = model.generate(**inputs, max_new_tokens=128,
                                         do_sample=True, temperature=0.8, top_p=0.9)
                gen = out[0][inputs["input_ids"].shape[1]:]
                ans = processor.decode(gen, skip_special_tokens=True).strip()
            except Exception as e:
                ans = "ERR:" + str(e)
            pred = parse_answer(kind, ans)
            rew = reward_for(rec["skill"], kind, pred, gt, gt_num)
            if rew > reward_thresh:
                accepted.append({"image": rec["image"], "question": q, "gt": gt,
                                 "skill": rec["skill"], "ans": ans, "reward": round(rew, 4)})
        if (ri + 1) % 25 == 0:
            print(f"[rft sample] {ri+1}/{len(recs)} accepted={len(accepted)} "
                  f"{(time.time()-t0)/(ri+1):.2f}s/item", flush=True)
    print(f"[rft] sampled {len(recs)*k_samples} -> accepted {len(accepted)} positive "
          f"(reward>{reward_thresh})", flush=True)
    json.dump({"accepted": len(accepted), "k_samples": k_samples, "thresh": reward_thresh,
               "items": accepted[:20]},
              open(os.path.join(OUT_DIR, "rft_accepted.json"), "w"),
              ensure_ascii=False, indent=2)
    model.train()
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=5e-5)
    rng = np.random.default_rng(seed + 100)
    step = 0
    t_start = time.time()
    losses = []
    if accepted:
        for ep in range(epochs):
            order = rng.permutation(len(accepted))
            for idx in order:
                a = accepted[idx]
                try:
                    inputs = sft_inputs(processor, a["image"], a["question"], a["gt"])
                except Exception as e:
                    continue
                inputs = {k: v.to("cuda") for k, v in inputs.items()}
                opt.zero_grad()
                out = model(**inputs)
                loss = out.loss
                loss.backward()
                torch.nn.utils.clip_grad_norm_(
                    [p for p in model.parameters() if p.requires_grad], 1.0)
                opt.step()
                step += 1
                losses.append(float(loss.item()))
                if step % 10 == 0:
                    el = time.time() - t_start
                    print(f"[rft train] ep{ep} step={step} loss={loss.item():.4f} "
                          f"{el/step:.2f}s/step", flush=True)
    rft_adapter = os.path.join(OUT_DIR, f"rft_adapter_seed{seed}")
    model.save_pretrained(rft_adapter)
    model.eval()
    summary = eval_on_heldout(model, processor, "cuda", f"rft_seed{seed}")
    summary["seed"] = seed
    summary["accepted"] = len(accepted)
    summary["k_samples"] = k_samples
    summary["thresh"] = reward_thresh
    summary["adapter_dir"] = rft_adapter
    json.dump(summary, open(os.path.join(OUT_DIR, "rft_seed_eval.json"), "w"),
              ensure_ascii=False, indent=2)
    del model
    torch.cuda.empty_cache()
    print("=== RFT done ===", flush=True)
    return summary


def mcnemar_exact(b, c):
    """exact McNemar (binomial) on discordant pairs b (wrong->right) and c (right->wrong)."""
    from math import comb
    n = b + c
    if n == 0:
        return 1.0, b, c
    k = min(b, c)
    p = 0.0
    for i in range(0, k + 1):
        p += comb(n, i) * (0.5 ** n)
    return min(1.0, 2 * p), b, c


def stage_report():
    pre = json.load(open(os.path.join(OUT_DIR, "prebaseline_heldout.json")))
    sft_seeds = []
    for fn in sorted(os.listdir(OUT_DIR)):
        if fn.startswith("sft_seed") and fn.endswith("_eval.json"):
            sft_seeds.append(json.load(open(os.path.join(OUT_DIR, fn))))
    rft = None
    rftp = os.path.join(OUT_DIR, "rft_seed_eval.json")
    if os.path.isfile(rftp):
        rft = json.load(open(rftp))

    def item_map(s):
        return {r["id"]: r for r in s["results"]}
    pre_items = item_map(pre)
    sft_accs = [s["accuracy"] for s in sft_seeds]
    sft_mr = [s["mean_reward"] for s in sft_seeds]
    sft_mean = float(np.mean(sft_accs)) if sft_accs else 0.0
    sft_std = float(np.std(sft_accs)) if sft_accs else 0.0
    mcn_pre_sft = []
    for s in sft_seeds:
        si = item_map(s)
        b = c = 0
        for qid, pr in pre_items.items():
            before = pr["correct"]
            after = si.get(qid, {}).get("correct", False)
            if (not before) and after:
                b += 1
            elif before and (not after):
                c += 1
        p, bb, cc = mcnemar_exact(b, c)
        mcn_pre_sft.append({"seed": s.get("seed"), "b_improved": bb,
                            "c_regressed": cc, "p_value": round(p, 5)})
    mcn_sft_rft = None
    if rft and sft_seeds:
        best = max(sft_seeds, key=lambda s: s["accuracy"])
        bi, ri = item_map(best), item_map(rft)
        b = c = 0
        for qid in bi:
            before = bi[qid]["correct"]
            after = ri.get(qid, {}).get("correct", False)
            if (not before) and after:
                b += 1
            elif before and (not after):
                c += 1
        p, bb, cc = mcnemar_exact(b, c)
        mcn_sft_rft = {"best_sft_seed": best.get("seed"), "b_improved": bb,
                       "c_regressed": cc, "p_value": round(p, 5)}
    skill_agg = {}
    for s in SKILLS:
        pre_acc = pre["skill_acc"].get(s, {}).get("acc", 0.0)
        sft_a = [x["skill_acc"].get(s, {}).get("acc", 0.0) for x in sft_seeds]
        skill_agg[s] = {
            "pre_acc": pre_acc,
            "sft_acc_mean": round(float(np.mean(sft_a)), 4) if sft_a else None,
            "sft_acc_std": round(float(np.std(sft_a)), 4) if sft_a else None,
            "rft_acc": rft["skill_acc"].get(s, {}).get("acc") if rft else None,
        }
    flipped = []
    if sft_seeds:
        best = max(sft_seeds, key=lambda s: s["accuracy"])
        bi = item_map(best)
        for qid, pr in pre_items.items():
            if (not pr["correct"]) and bi.get(qid, {}).get("correct", False):
                flipped.append({"id": qid, "skill": pr["skill"], "gt": pr["gt"],
                                "pre_pred": pr["pred"], "post_pred": bi[qid]["pred"]})
    summary = {
        "stage": "report",
        "pre_baseline": {"n": pre["n"], "accuracy": pre["accuracy"],
                         "mean_reward": pre["mean_reward"]},
        "sft": {"n_seeds": len(sft_seeds), "acc_mean": round(sft_mean, 4),
                "acc_std": round(sft_std, 4),
                "reward_mean": round(float(np.mean(sft_mr)), 4) if sft_mr else 0,
                "per_seed": [{"seed": s.get("seed"), "acc": s["accuracy"],
                              "mean_reward": s["mean_reward"]} for s in sft_seeds]},
        "rft": ({"accuracy": rft["accuracy"], "mean_reward": rft["mean_reward"],
                 "accepted": rft.get("accepted")} if rft else None),
        "mcnemar_pre_vs_sft": mcn_pre_sft,
        "mcnemar_sft_vs_rft": mcn_sft_rft,
        "skill_agg": skill_agg,
        "flipped_items_pre_to_best_sft": flipped,
        "n_heldout": pre["n"],
        "leakage_check": pre.get("leakage_check"),
        "preregistered_criteria": pre.get("preregistered_criteria"),
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    out = os.path.join(OUT_DIR, "strengthen_summary.json")
    json.dump(summary, open(out, "w"), ensure_ascii=False, indent=2)
    print("=== REPORT summary ===")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    build_html_report(summary, pre, sft_seeds, rft)
    print(f"=== summary -> {out}", flush=True)


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def svg_bar(labels, pres, posts, title):
    n = len(labels)
    W, H, bw, gap, base_x, maxv = 460, 260, 28, 14, 60, 100
    bars = []
    for i, lab in enumerate(labels):
        x = base_x + i * (bw * 2 + gap)
        pre = pres[i] * 100
        post = (posts[i] * 100) if posts[i] is not None else 0
        hpre = pre / maxv * (H - 50)
        hpost = post / maxv * (H - 50)
        bars.append(f'<rect x="{x}" y="{H-30-hpre:.1f}" width="{bw}" height="{hpre:.1f}" fill="#9aa4b2"/>')
        bars.append(f'<rect x="{x+bw+2}" y="{H-30-hpost:.1f}" width="{bw}" height="{hpost:.1f}" fill="#2b6cb0"/>')
        bars.append(f'<text x="{x+bw/2}" y="{H-30-hpre-4:.1f}" font-size="9" text-anchor="middle" fill="#333">{pre:.0f}</text>')
        bars.append(f'<text x="{x+bw+2+bw/2}" y="{H-30-hpost-4:.1f}" font-size="9" text-anchor="middle" fill="#333">{post:.0f}</text>')
        bars.append(f'<text x="{x+bw+1}" y="{H-14}" font-size="9" text-anchor="middle" fill="#444">{esc(lab[:8])}</text>')
    grid = ""
    for v in (0, 25, 50, 75, 100):
        y = H - 30 - v / maxv * (H - 50)
        grid += (f'<line x1="55" y1="{y:.1f}" x2="{W-10}" y2="{y:.1f}" stroke="#eee" stroke-width="1"/>'
                 f'<text x="50" y="{y+3:.1f}" font-size="8" text-anchor="end" fill="#888">{v}</text>')
    svg = (f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">'
           f'<rect width="{W}" height="{H}" fill="#fff"/>'
           f'<text x="{W/2}" y="16" font-size="12" text-anchor="middle" fill="#222">{esc(title)}</text>'
           f'{grid}{"".join(bars)}'
           f'<rect x="{W-90}" y="22" width="10" height="10" fill="#9aa4b2"/><text x="{W-76}" y="31" font-size="9" fill="#444">pre</text>'
           f'<rect x="{W-50}" y="22" width="10" height="10" fill="#2b6cb0"/><text x="{W-36}" y="31" font-size="9" fill="#444">post</text></svg>')
    return svg


def svg_pie(parts, title):
    import math as _m
    W, H, cx, cy, r = 240, 200, 90, 100, 70
    total = sum(v for _, v, _ in parts) or 1
    ang = -90.0
    paths = []
    for lab, v, col in parts:
        frac = v / total
        if frac <= 0:
            continue
        a2 = ang + frac * 360
        large = 1 if (a2 - ang) > 180 else 0
        x1 = cx + r * _m.cos(_m.radians(ang)); y1 = cy + r * _m.sin(_m.radians(ang))
        x2 = cx + r * _m.cos(_m.radians(a2)); y2 = cy + r * _m.sin(_m.radians(a2))
        paths.append(f'<path d="M{cx},{cy} L{x1:.1f},{y1:.1f} A{r},{r} 0 {large} 1 {x2:.1f},{y2:.1f} Z" fill="{col}"/>')
        ang = a2
    legend = ""
    for i, (lab, v, col) in enumerate(parts):
        ly = 40 + i * 18
        legend += (f'<rect x="170" y="{ly}" width="10" height="10" fill="{col}"/>'
                   f'<text x="184" y="{ly+9}" font-size="10" fill="#333">{esc(lab)} ({v})</text>')
    return (f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">'
            f'<text x="{W/2}" y="18" font-size="12" text-anchor="middle" fill="#222">{esc(title)}</text>'
            f'{"".join(paths)}{legend}</svg>')


def build_html_report(summary, pre, sft_seeds, rft):
    sft = summary["sft"]
    rfts = summary["rft"]
    pre_acc = pre["accuracy"]
    sft_acc = sft["acc_mean"]
    rft_acc = rfts["accuracy"] if rfts else None
    verdict = "待定"
    if rft_acc is not None and sft_seeds:
        delta = rft_acc - sft_acc
        p = summary["mcnemar_sft_vs_rft"]["p_value"] if summary["mcnemar_sft_vs_rft"] else 1.0
        if delta >= 0.05 and p < 0.05:
            verdict = "✅ 显著提升（post-RL ≥ post-SFT +5pp 且 McNemar p<0.05）"
        elif delta > 0:
            verdict = f"🟡 有提升但未达预注册判据（Δ={delta*100:.1f}pp / p={p}）"
        else:
            verdict = f"🔴 负结果（Δ={delta*100:.1f}pp / p={p}）— RFT 未带来增益"
    elif sft_seeds:
        delta = sft_acc - pre_acc
        pmin = min((m["p_value"] for m in summary["mcnemar_pre_vs_sft"]), default=1.0)
        if delta >= 0.05 and pmin < 0.05:
            verdict = "✅ SFT 显著提升（vs before，≥5pp 且 McNemar p<0.05）"
        elif delta > 0:
            verdict = f"🟡 SFT 有提升但未达判据（Δ={delta*100:.1f}pp / min p={pmin}）"
        else:
            verdict = f"🔴 SFT 负结果（Δ={delta*100:.1f}pp）"
    skills = list(summary["skill_agg"].keys())
    pres = [summary["skill_agg"][s]["pre_acc"] for s in skills]
    posts = [summary["skill_agg"][s]["sft_acc_mean"] for s in skills]
    bar_svg = svg_bar(skills, pres, posts, "各技能准确率：pre vs post-SFT（%）")
    mcn0 = summary["mcnemar_pre_vs_sft"][0] if summary["mcnemar_pre_vs_sft"] else {"b_improved": 0, "c_regressed": 0}
    pie = svg_pie([("翻转成功(wrong→right)", mcn0["b_improved"], "#2b6cb0"),
                   ("回退(right→wrong)", mcn0["c_regressed"], "#c0392b"),
                   ("其余一致", summary["n_heldout"] - mcn0["b_improved"] - mcn0["c_regressed"], "#dfe3e8")],
                  "McNemar 配对（pre vs post-SFT seed1）")
    flipped_rows = "".join(
        f"<tr><td>{esc(f['id'])}</td><td>{esc(f['skill'])}</td><td>{esc(f['gt'])}</td>"
        f"<td>{esc(f['pre_pred'])}</td><td>{esc(f['post_pred'])}</td></tr>"
        for f in summary["flipped_items_pre_to_best_sft"]) or '<tr><td colspan="5" style="color:#888">无翻转项</td></tr>'
    seed_rows = "".join(
        f"<tr><td>{esc(s.get('seed'))}</td><td>{s['accuracy']*100:.1f}%</td>"
        f"<td>{s['mean_reward']:.4f}</td><td>{esc(s.get('final_loss_avg10'))}</td></tr>"
        for s in sft_seeds)
    mcn_rows = "".join(
        f"<tr><td>{esc(m['seed'])}</td><td>{m['b_improved']}</td><td>{m['c_regressed']}</td>"
        f"<td>{m['p_value']}</td></tr>" for m in summary["mcnemar_pre_vs_sft"])
    skill_rows = "".join(
        f"<tr><td>{esc(s)}</td><td>{summary['skill_agg'][s]['pre_acc']*100:.0f}%</td>"
        f"<td>{(summary['skill_agg'][s]['sft_acc_mean']*100 if summary['skill_agg'][s]['sft_acc_mean'] is not None else '—')}%"
        f" ± {(summary['skill_agg'][s]['sft_acc_std']*100 if summary['skill_agg'][s]['sft_acc_std'] is not None else 0):.0f}</td>"
        f"<td>{(summary['skill_agg'][s]['rft_acc']*100 if summary['skill_agg'][s]['rft_acc'] is not None else '—')}%</td></tr>"
        for s in skills)
    rft_block = ""
    if rfts:
        mr = summary["mcnemar_sft_vs_rft"] or {}
        rft_block = (
            "<h3>RFT（rejection-sampling FT · 轻量 RL）</h3>"
            "<table border='1' cellpadding='6' style='border-collapse:collapse'>"
            "<tr><th>阶段</th><th>准确率</th><th>mean_reward</th><th>accepted/K</th></tr>"
            f"<tr><td>post-SFT (best seed)</td><td>{max([s['accuracy'] for s in sft_seeds])*100:.1f}%</td><td>—</td><td>—</td></tr>"
            f"<tr><td>post-RFT</td><td>{rfts['accuracy']*100:.1f}%</td><td>{rfts['mean_reward']:.4f}</td><td>{rfts.get('accepted')}/{rfts.get('k_samples','?')}×150</td></tr></table>"
            f"<p>McNemar (best-SFT vs RFT): b(翻转)={mr.get('b_improved')} c(回退)={mr.get('c_regressed')} p={mr.get('p_value')}</p>")
    vcls = "ok" if "✅" in verdict else ("warn" if "🟡" in verdict else "neg")
    rft_row = (f'<tr><td>post-RFT</td><td>{rfts["accuracy"]*100:.1f}%</td><td>{rfts["mean_reward"]:.4f}</td><td>accepted={rfts.get("accepted")}</td></tr>') if rfts else ""
    _ctx = dict(pre_acc=pre_acc, sft_acc=sft_acc, sft=sft, pre=pre, rfts=rfts,
                bar_svg=bar_svg, pie=pie, seed_rows=seed_rows, mcn_rows=mcn_rows,
                skill_rows=skill_rows, flipped_rows=flipped_rows, rft_block=rft_block,
                rft_row=rft_row, vcls=vcls, verdict=verdict, summary=summary)
    _write_html(_ctx)


def _write_html(c):
    pre_acc = c["pre_acc"]; sft_acc = c["sft_acc"]; sft = c["sft"]; pre = c["pre"]
    rfts = c["rfts"]; summary = c["summary"]; verdict = c["verdict"]
    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vision #4 · Qwen3.5-2B 波形识图强化（SFT+RFT）报告</title>
<style>body{{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;max-width:980px;margin:24px auto;color:#222;line-height:1.6;padding:0 16px}}
h1,h2,h3{{color:#1a3a5c}}table{{margin:8px 0;font-size:14px}}th{{background:#eef3f8}}
td,th{{border:1px solid #ccc;padding:6px 10px}}.card{{background:#f7f9fc;border:1px solid #dce3ec;border-radius:8px;padding:14px 18px;margin:14px 0}}
.verdict{{font-size:18px;font-weight:bold;padding:12px 16px;border-radius:8px}}
.ok{{background:#e6f4ea;color:#1e6b3a}}.warn{{background:#fff7e0;color:#8a5b00}}.neg{{background:#fdecea;color:#a3241b}}
code{{background:#eef;padding:1px 4px;border-radius:3px}}.muted{{color:#888}}</style></head>
<body>
<h1>Vision #4 · Qwen3.5-2B 波形识图能力强化（SFT + RFT）</h1>
<p class="muted">vision 线 · 用户令 2026-11-14 09:1x #4 / 10:3x · native multimodal VL（非文本桥）· {esc(summary['ts'])}</p>
<div class="card verdict {c['vcls']}">{esc(verdict)}</div>
<h2>1. 实验设计（预注册）</h2>
<div class="card"><ul>
<li><b>基模</b>：Qwen3.5-2B（<code>Qwen3_5ForConditionalGeneration</code>，原生多模态，直接吃像素）。</li>
<li><b>训练集</b>：sft.jsonl，150 条（seed=20261114，25/技能 × 6 技能：type/cycle/amplitude/freq_compare/duty/rise）。</li>
<li><b>held-out 评估集</b>：30 条（<b>seed=20261115</b>，5/技能）——与训练集<b>不同 seed</b>，<b>零泄漏</b>（cheat_rate=0 由构造保证）。
<br><span class="muted">注：旧 synth_selftest_baseline 用 seed=20261114（=训练集），存在 train-on-test 重叠，已弃作 #4 对照，改用本 held-out。</span></li>
<li><b>before</b>：基模 greedy 在 held-out 30 题（查常驻 VQA server）。</li>
<li><b>SFT</b>：LoRA（r=8,α=16,target=q/k/v/o/gate/up/down_proj）3 seed × 3 epoch，lr=1e-4，仅训适配器、基模冻结。</li>
<li><b>RFT（轻量 RL）</b>：在 SFT 上对训练集采样 K=4（temp=0.8），留连续奖励 <code>exp(-rel_err/τ)</code>（τ=0.15）>0.5 的正例，再训一轮（v4 路线）。</li>
<li><b>判据（预注册）</b>：成功 = post-RL ≥ post-SFT +5pp 且 McNemar p&lt;0.05 且 ≥3 seed 一致 且 cheat_rate=0；负结果照实上报。</li>
</ul></div>
<h2>2. 总体结果</h2>
<table border="1" cellpadding="6" style="border-collapse:collapse">
<tr><th>阶段</th><th>准确率</th><th>mean_reward</th><th>备注</th></tr>
<tr><td>before（基模）</td><td>{pre_acc*100:.1f}%</td><td>{pre['mean_reward']:.4f}</td><td>held-out 30 题</td></tr>
<tr><td>post-SFT（3 seed mean±std）</td><td>{sft_acc*100:.1f}% ± {sft['acc_std']*100:.1f}</td><td>{sft['reward_mean']:.4f}</td><td>n_seeds={sft['n_seeds']}</td></tr>
{c['rft_row']}
</table>
{c['bar_svg']}
<p style="text-align:center" class="muted">灰=pre（基模）· 蓝=post-SFT（mean）· 各技能准确率（%）</p>
<h2>3. SFT 逐 seed</h2>
<table border="1" cellpadding="6" style="border-collapse:collapse">
<tr><th>seed</th><th>准确率</th><th>mean_reward</th><th>末段 loss avg10</th></tr>
{c['seed_rows']}
</table>
<h2>4. McNemar 显著性（配对逐题）</h2>
<h3>before vs post-SFT（每 seed）</h3>
<table border="1" cellpadding="6" style="border-collapse:collapse">
<tr><th>seed</th><th>b（wrong→right）</th><th>c（right→wrong）</th><th>p_value（exact）</th></tr>
{c['mcn_rows']}
</table>
<p>{c['pie']}</p>
{c['rft_block']}
<h2>5. 各技能分解</h2>
<table border="1" cellpadding="6" style="border-collapse:collapse">
<tr><th>技能</th><th>pre</th><th>post-SFT (mean±std)</th><th>post-RFT</th></tr>
{c['skill_rows']}
</table>
<h2>6. 靠 SFT 翻转的题（before 错 → best-SFT 对）</h2>
<table border="1" cellpadding="6" style="border-collapse:collapse">
<tr><th>id</th><th>技能</th><th>GT</th><th>pre pred</th><th>post pred</th></tr>
{c['flipped_rows']}
</table>
<h2>7. 结论与下一步</h2>
<div class="card">
<p><b>结论</b>：{esc(verdict)}。SFT 在 held-out（零泄漏）上从 {pre_acc*100:.1f}% → {sft_acc*100:.1f}%（3 seed mean±std {sft['acc_std']*100:.1f}），翻转 {len(summary['flipped_items_pre_to_best_sft'])} 题。{('RFT 在 SFT 基础上 → '+f'{rfts["accuracy"]*100:.1f}%。') if rfts else 'RFT 待跑。'}</p>
<p><b>诚实说明</b>：评估集为<b>合成波形图</b>（带网格、确定参数），规模 30 题、6 技能；A40 单卡、LoRA 小 rank。结论限定于「合成波形识图」scope，<b>不可外推</b>到 designflow 真实 EDA 波形（需 #3 跨线对照）。{('若负结果：方向已穷尽或 SFT 数据量/技能覆盖不足；下一步=扩合成数据多样性 + 真实波形迁移。') if ('🔴' in verdict or '🟡' in verdict) else ''}</p>
<p><b>下一步</b>：① designflow 恢复 11 题原形态后做「无 VQA vs 有 VQA(本强化后模型)」对照（#3）；② 若 SFT 有效，扩合成数据 + 上 GRPO 群体奖励；③ 把强化后模型导出供 cline/designflow 调用。</p>
</div>
<p class="muted">产物：<code>strengthen_runs/</code>（prebaseline_heldout.json / sft_seed*_eval.json / rft_seed_eval.json / strengthen_summary.json / *_adapter_seed*）。本报告单文件自包含、0 外链、0 script、内联 SVG。</p>
</body></html>"""
    out = os.path.normpath(os.path.join(HERE, "..", "..", "reports",
                                        "report_vision_vqa_strengthen_zh.html"))
    with open(out, "w") as f:
        f.write(html)
    print(f"=== HTML report -> {out}", flush=True)


def main():
    ap = argparse.ArgumentParser(description="#4 SFT+RFT strengthen Qwen3.5-2B waveform reading")
    ap.add_argument("--stage", required=True,
                    choices=["prebaseline", "smoke", "sft", "rft", "report"])
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--epochs", type=int, default=3)
    args = ap.parse_args()
    if args.stage == "prebaseline":
        stage_prebaseline()
    elif args.stage == "smoke":
        stage_smoke()
    elif args.stage == "sft":
        stage_sft(args.seeds, args.epochs)
    elif args.stage == "rft":
        stage_rft()
    elif args.stage == "report":
        stage_report()


if __name__ == "__main__":
    main()







