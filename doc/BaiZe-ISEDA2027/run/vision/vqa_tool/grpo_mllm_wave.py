#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""grpo_mllm_wave.py -- Stage-2W GRPO on the FULL Qwen3.5-2B MLLM (用户令 2026-11-19 Option B step c).

背景：2026-11-19 用户令把 vision 训练迁回 GPU，并「修正 Option B」——Qwen3.5-2B 是原生
多模态 MLLM，直接对完整模型（含视觉塔）做 LoRA 微调，**不剥离视觉塔**。step (b) SFT 已由
v2 加强管线（sft_rl_strengthen_v2.py → strengthen_runs/rft2_adapter_seed11，pre 60%→v2-RFT
90%，McNemar b=7/c=0/p=0.0156）完成并在 :30003 服务、WaveView 全队列 V2 vs V0 p=0.008 验证。

本脚本补齐 step (c) 缺口：在完整 MLLM 上做 **GRPO**（Group Relative Policy Optimization，
无价值网络、显存轻）。与旧 grpo_train_wave.py 的区别：
  * 旧脚本面向 .12 文本骨干（剥离视觉塔的 Qwen3-VL-2B text-only + tool-call rollout）；
  * 本脚本面向 .17 完整 Qwen3.5-2B MLLM，**直接吃像素**，rollout = 图像+问题 → 生成答案，
    可验证奖励 = synth_waveform_qa.reward_for（回归 exp(-rel_err/τ) / 分类二值）。

GRPO：每 prompt 采样 G 条，advantage=(R-mean)/(std+eps)，PPO clipped surrogate（仅监督
assistant 生成 token）。冷启动可选挂 v2 SFT/RFT adapter（is_trainable=True）。

用法（.17 GPU 7，单卡 2B LoRA 足够，不扰 GPU6 上的 VQA 服务）：
  PY=/nas_data/app.e0031982/miniforge3/envs/py310/bin/python
  CUDA_VISIBLE_DEVICES=7 $PY grpo_mllm_wave.py --smoke_test
  CUDA_VISIBLE_DEVICES=7 $PY grpo_mllm_wave.py --total_steps 500 --group_size 4 --batch_prompts 2

作者: vision wake#1683 · project-internal
"""
import argparse, json, math, os, sys, time
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.environ.get("QWEN35_VQA_MODEL", "/nas_data/app.e0031982/models/Qwen3.5-2B")
OUT_DIR = os.path.join(HERE, "grpo_mllm_runs")
os.makedirs(OUT_DIR, exist_ok=True)

# 复用 v2 加强管线的「完整 MLLM 加载 / LoRA / 多模态 inputs」与「合成波形奖励」基础设施
from sft_rl_strengthen import (  # noqa: E402
    load_model_for_train, build_lora, gen_answer, eval_on_heldout,
    make_eval_set, mcnemar_exact,
)
from synth_waveform_qa import (  # noqa: E402
    make_case, parse_answer, reward_for, is_correct, SKILLS,
)


def parse_args():
    ap = argparse.ArgumentParser(description="Stage-2W GRPO on full Qwen3.5-2B MLLM")
    ap.add_argument("--model_path", default=MODEL_PATH)
    ap.add_argument("--output_dir", default=OUT_DIR)
    ap.add_argument("--init_adapter", default=None,
                    help="冷启动 adapter（如 strengthen_runs/rft2_adapter_seed11）；不传则 fresh LoRA")
    ap.add_argument("--lora_r", type=int, default=8)
    ap.add_argument("--lora_alpha", type=int, default=16)
    ap.add_argument("--lora_dropout", type=float, default=0.05)
    ap.add_argument("--lr", type=float, default=1e-5, help="RL LR (低于 SFT)")
    ap.add_argument("--total_steps", type=int, default=500)
    ap.add_argument("--batch_prompts", type=int, default=2, help="每步 prompt 数 (B)")
    ap.add_argument("--group_size", type=int, default=4, help="每 prompt 采样数 (G)")
    ap.add_argument("--ppo_epochs", type=int, default=1)
    ap.add_argument("--clip_eps", type=float, default=0.2)
    ap.add_argument("--max_new_tokens", type=int, default=64)
    ap.add_argument("--temperature", type=float, default=0.8)
    ap.add_argument("--top_p", type=float, default=0.95)
    ap.add_argument("--seed", type=int, default=20261119)
    ap.add_argument("--log_steps", type=int, default=10)
    ap.add_argument("--save_steps", type=int, default=100)
    ap.add_argument("--train_seed", type=int, default=20261114,
                    help="训练 case 采样 seed（与 v2 SFT 同 seed）")
    ap.add_argument("--smoke_test", action="store_true")
    ap.add_argument("--device", default="cuda", choices=["cuda", "cpu"])
    return ap.parse_args()


def build_train_cases(seed, n_per_skill=25, img_subdir="grpo_train_images"):
    """生成训练 case（同 v2 SFT 的合成分布；seed=20261114）。"""
    img_dir = os.path.join(OUT_DIR, img_subdir)
    os.makedirs(img_dir, exist_ok=True)
    rng = np.random.default_rng(seed)
    cases, qid = [], 0
    for skill in SKILLS:
        for _ in range(n_per_skill):
            cases.append(make_case(skill, rng, img_dir, qid))
            qid += 1
    return cases


def prompt_inputs(processor, image_path, question, device):
    """构造 generation prompt 的多模态 inputs（add_generation_prompt=True）。"""
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
    """采样一条 completion。返回 (full_ids[1,T], prompt_len, gen_text, img_inputs)。

    img_inputs = processor 输出中除 input_ids/attention_mask 外的全部多模态张量
    （pixel_values / image_grid_thw / mm_token_type_ids …），供 completion_logprobs
    重做前向时一并喂回视觉塔。Qwen3.5 forward 需三者齐全——缺 image_grid_thw 会使
    get_image_features 里 grid_thw=None 报 'NoneType has no attribute device'。
    """
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
    full_ids = out[0]                      # [T]  (prompt + generated)
    gen_ids = full_ids[prompt_len:]
    gen_text = processor.decode(gen_ids, skip_special_tokens=True).strip()
    img_inputs = {k: v for k, v in inputs.items()
                  if k not in ("input_ids", "attention_mask")}
    return full_ids, prompt_len, gen_text, img_inputs


def completion_logprobs(model, full_ids, prompt_len, img_inputs, device):
    """计算 completion token 的 per-token logprob（当前策略，带 grad）。

    img_inputs 为 sample_one 保留的多模态张量；其中 mm_token_type_ids 是 prompt
    长度，需补 0（text 类型）到 full_ids 长度，否则 M-RoPE get_rope_index 会因
    长度不匹配报错。
    """
    import torch
    import torch.nn.functional as F
    ids = full_ids.unsqueeze(0).to(device)            # [1, T]
    attn = torch.ones_like(ids)
    fwd_kw = {"input_ids": ids, "attention_mask": attn}
    T = ids.shape[1]
    if img_inputs:
        for k, v in img_inputs.items():
            if v is None:
                continue
            if k == "mm_token_type_ids":
                tt = v.to(device)
                if tt.shape[1] < T:                    # prompt 长度 -> 补 generated 段(text=0)
                    pad = torch.zeros(tt.shape[0], T - tt.shape[1],
                                      dtype=tt.dtype, device=device)
                    tt = torch.cat([tt, pad], dim=1)
                elif tt.shape[1] > T:
                    tt = tt[:, :T]
                fwd_kw[k] = tt
            else:
                fwd_kw[k] = v.to(device)
    logits = model(**fwd_kw).logits                    # [1, T, V]
    log_probs = F.log_softmax(logits[:, :-1, :].float(), dim=-1)  # [1, T-1, V]
    target = ids[:, 1:]                                # [1, T-1]
    token_lps = log_probs.gather(2, target.unsqueeze(-1)).squeeze(-1)  # [1, T-1]
    # completion token 位于 positions prompt_len..T-1，由 logit positions prompt_len-1..T-2 预测
    return token_lps[0, prompt_len - 1: ids.shape[1] - 1]


def grpo_update(model, rollouts, optimizer, clip_eps, device, ppo_epochs=1):
    """rollouts: list of dict(full_ids, prompt_len, pixel_values, old_logprob(tensor), adv)。"""
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


def run_train(args):
    import torch
    device = args.device
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    model, processor = load_model_for_train(device)
    if args.init_adapter and os.path.isdir(args.init_adapter):
        from peft import PeftModel
        print(f"[grpo-mllm] cold-start from adapter: {args.init_adapter}", flush=True)
        model = PeftModel.from_pretrained(model, args.init_adapter, is_trainable=True)
    else:
        model = build_lora(model, args.seed, rank=args.lora_r,
                           alpha=args.lora_alpha, dropout=args.lora_dropout)
    model.print_trainable_parameters()

    # --- cold-start 基线评测（训练前，同一 adapter/模型，apples-to-apples）---
    # 修正 wake#1684 的坑：smoke 用 init_adapter=null(fresh LoRA from base) 跑出的
    # 0.60 被误记为「post-SFT/rft2-init 基线」，而真正的 rft2 冷启动基线=0.90。
    # 此处显式评测「刚加载、尚未训练」的冷启动 adapter，存为独立 baseline 文件，
    # 使 GRPO 的增益对比的是真正的冷启动基线，而非 base 模型。
    model.eval()
    try:
        _base_eval = eval_on_heldout(model, processor, device, "grpo_mllm_pretrain_baseline")
        _base_eval["adapter_dir"] = args.init_adapter or "(fresh LoRA, no cold-start)"
        _base_eval["note"] = ("cold-start adapter evaluated BEFORE any GRPO step; "
                              "this is the correct GRPO baseline (not the base model).")
        json.dump(_base_eval,
                  open(os.path.join(args.output_dir, "grpo_mllm_pretrain_baseline_eval.json"), "w"),
                  ensure_ascii=False, indent=2)
        print(f"[grpo-mllm] cold-start held-out baseline acc={_base_eval['accuracy']} "
              f"(n={_base_eval['n']}) -> {args.output_dir}/grpo_mllm_pretrain_baseline_eval.json",
              flush=True)
    except Exception as e:
        print(f"[grpo-mllm] cold-start baseline eval skipped: {e}", flush=True)
    model.train()
    trainable = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(trainable, lr=args.lr, weight_decay=0.0)

    cases = build_train_cases(args.train_seed)
    rng = np.random.default_rng(args.seed)
    print(f"[grpo-mllm] {len(cases)} train cases | B={args.batch_prompts} G={args.group_size} "
          f"steps={args.total_steps} lr={args.lr} device={device}", flush=True)

    os.makedirs(args.output_dir, exist_ok=True)
    step, t0 = 0, time.time()
    log_reward, log_count = 0.0, 0
    train_log = []
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
                    rew = reward_for(c["skill"], c["kind"], pred, c["gt"], c.get("gt_num"))
                except Exception as e:
                    gen_text, rew, pred, full_ids, plen, img_inputs = ("ERR:" + str(e), 0.0, "", None, 0, None)
                group.append({"full_ids": full_ids, "prompt_len": plen,
                              "img_inputs": img_inputs, "reward": float(rew),
                              "gen_text": gen_text, "pred": pred})
            rewards = np.array([g["reward"] for g in group], dtype=np.float64)
            mean, std = float(rewards.mean()), float(rewards.std())
            advs = (rewards - mean) / (std + 1e-4) if std > 1e-6 else np.zeros_like(rewards)
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
                  f"{sps:.2f} step/s | ETA {eta/60:.1f} min", flush=True)
            log_reward, log_count = 0.0, 0
        if step % args.save_steps == 0:
            ckpt = os.path.join(args.output_dir, f"step{step}")
            model.save_pretrained(ckpt)
            print(f"  saved adapter -> {ckpt}", flush=True)
    final_ckpt = os.path.join(args.output_dir, f"step{args.total_steps}")
    model.save_pretrained(final_ckpt)
    json.dump({"config": vars(args), "steps": train_log, "total_wall_s": time.time() - t0},
              open(os.path.join(args.output_dir, "training_log.json"), "w"),
              ensure_ascii=False, indent=2)
    print(f"[grpo-mllm] saved final adapter -> {final_ckpt}", flush=True)
    model.eval()
    summary = eval_on_heldout(model, processor, device, "grpo_mllm_final")
    summary["adapter_dir"] = final_ckpt
    json.dump(summary, open(os.path.join(args.output_dir, "grpo_mllm_eval.json"), "w"),
              ensure_ascii=False, indent=2)
    print(f"[grpo-mllm] held-out acc={summary['accuracy']} -> {args.output_dir}/grpo_mllm_eval.json", flush=True)
    del model
    torch.cuda.empty_cache()


def smoke_test(args):
    """极小配置端到端冒烟：2 prompt × G=4 × 2 步，验证 sample→reward→adv→loss→backward→save 全链路。"""
    args.total_steps = 2
    args.batch_prompts = 2
    args.group_size = 4
    args.max_new_tokens = 40
    args.save_steps = 2
    args.log_steps = 1
    args.output_dir = os.path.join(OUT_DIR, "smoke")
    os.makedirs(args.output_dir, exist_ok=True)
    print("=== GRPO-MLLM smoke (full Qwen3.5-2B MLLM, GPU) ===", flush=True)
    run_train(args)
    adapter = os.path.join(args.output_dir, "step2", "adapter_config.json")
    eval_json = os.path.join(args.output_dir, "grpo_mllm_eval.json")
    ok = os.path.isfile(adapter) and os.path.isfile(eval_json)
    print(f"  adapter_config.json exists: {os.path.isfile(adapter)}", flush=True)
    print(f"  grpo_mllm_eval.json exists: {os.path.isfile(eval_json)}", flush=True)
    if ok:
        ev = json.load(open(eval_json))
        print(f"  held-out accuracy: {ev['accuracy']} (n={ev['n']})", flush=True)
    print(f"=== smoke {'PASS' if ok else 'FAIL'} ===", flush=True)
    return 0 if ok else 1


def main():
    args = parse_args()
    if args.smoke_test:
        return smoke_test(args)
    run_train(args)


if __name__ == "__main__":
    sys.exit(main())
