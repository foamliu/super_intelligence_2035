#!/usr/bin/env python3
"""baize_posttrain_rl_grpo_loop.py — Self-written single-process GRPO rollout
loop for BaiZe Stage(ii) surrogate RL on MiniCPM5-2B / SFT step105.

WHY THIS FILE EXISTS (R412, 2026-11-13):
  verl 0.4.0 GRPO is conclusively BLOCKED on this host (wake409/410/411):
  verl's list_named_actors() cannot see the already-created register_center
  named Ray actor -> TaskRunner and WorkerDict wait on each other forever (RSS
  frozen ~682MB, GPU 0 MiB, wchan hrtimer_nanosleep). 1-GPU / 2-GPU / NCCL-fix
  all reproduce the same signature. Root cause is a verl 0.4.0 + local Ray
  named-actor visibility incompatibility (needs root to pin the exact line). Per
  the 2026-11-13 user order, RL must NOT wait for the BaiZe base model any
  longer -- it starts directly on MiniCPM5-2B (+SFT v39 step105). The unblocking
  action is therefore to LEAVE verl/Ray entirely and run GRPO in a single
  process with pure HF + torch: no Ray, no colocated workers, no named-actor
  handshake.

ARCHITECTURE (standard GRPO, single GPU, no Ray):
  1. Load policy (= SFT step105) and a frozen reference copy in bf16.
  2. Each step: sample B prompts, generate G completions each with
     model.generate(do_sample=True).
  3. Decode completions; score with the existing
     baize_posttrain_reward_functions.compute_score (R0 static analysis
     auto-fallback when sandbox results are absent -> differentiated signal
     even without the EDA sandbox; arms R1-R4 light up once sandbox exec
     results are injected into extra_info).
  4. GRPO advantage per group: A_i = (r_i - mean_g) / (std_g + eps).
  5. PPO-clipped policy loss over K mini-epochs + KL(policy || ref) penalty.
  6. AdamW step; checkpoint every --save-freq.

MEMORY (single A40, 48GB):
  policy 2B bf16 ~4GB + ref 2B bf16 ~4GB + AdamW states(bf16) ~8GB + grads
  ~4GB + activations (gradient checkpointing) + generation KV cache. Fits with
  the smoke defaults (B=2, G=4, ctx 512/256). If OOM, lower --group-size /
  --max-response-len / keep --grad-checkpointing (default on).

RED LINES (BAIZE_POSTTRAIN_TASK.md):
  - Contamination: rl_pyaether_synth_v2.parquet (3347 synthetic) must NOT
    overlap the 158 eval tasks. --contam-check runs the gate before launch.
  - Anti-cheat: compute_score already calls update_cheat_rate(); this script
    saves cheat_rate.json every save window and reports it.
  - 5-run mean+-std reporting is an EVAL concern, not a training concern.
  - Results MUST be labelled "替身预演，收益不可迁移到 BaiZe".

Usage:
  python baize_posttrain_rl_grpo_loop.py --dry-run
  python baize_posttrain_rl_grpo_loop.py --contam-check
  python baize_posttrain_rl_grpo_loop.py --smoke
  python baize_posttrain_rl_grpo_loop.py --reward-arm R0 --total-steps 200
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import logging
import os
import random
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch

logger = logging.getLogger("grpo_loop")

DATA_SOURCE = "pyaether_synth_v2"
EPS_ADV = 1e-4


@dataclass
class Cfg:
    sft_ckpt: str = ""
    rl_data: str = ""
    reward_fn_path: str = ""
    api_database: str = ""
    output_dir: str = ""
    reward_arm: str = "R0"
    auto_fallback: bool = True
    group_size: int = 4
    batch_prompts: int = 2
    total_steps: int = 200
    save_freq: int = 50
    log_freq: int = 1
    lr: float = 3.0e-6
    kl_coef: float = 0.02
    clip_ratio: float = 0.2
    temperature: float = 0.7
    top_p: float = 0.95
    max_prompt_len: int = 512
    max_response_len: int = 384
    ppo_epochs: int = 1
    grad_checkpointing: bool = True
    seed: int = 42
    smoke: bool = False
    dry_run: bool = False
    contam_check: bool = False
    max_grad_norm: float = 1.0
    bf16: bool = True
    device: str = "cuda"

    def smoke_defaults(self) -> None:
        if self.smoke:
            self.total_steps = 3
            self.save_freq = 3
            self.batch_prompts = 2
            self.group_size = 4
            self.max_prompt_len = 512
            self.max_response_len = 256
            self.ppo_epochs = 1
            self.kl_coef = 0.0


def load_reward_module(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError("reward fn not found: " + path)
    spec = importlib.util.spec_from_file_location("baize_reward", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_rl_data(path: str) -> List[Dict[str, Any]]:
    import pyarrow.parquet as pq
    tab = pq.read_table(path)
    rows = tab.to_pylist()
    out = []
    for r in rows:
        prompt = r.get("prompt")
        rm = r.get("reward_model", {})
        if isinstance(prompt, list) and prompt:
            out.append({"prompt": prompt, "reward_model": rm or {}})
    return out


def contam_gate(rows: List[Dict[str, Any]], eval_jsonl: str) -> None:
    """Red-line 5.1: ensure no RL prompt overlaps the 158 eval tasks."""
    if not os.path.exists(eval_jsonl):
        logger.warning("contam gate: eval set %s not found, SKIP", eval_jsonl)
        return

    def norm(s: str) -> str:
        return "".join(s.split()).lower()

    eval_prompts = set()
    with open(eval_jsonl, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            p = obj.get("prompt") or obj.get("input") or obj.get("question") or ""
            if isinstance(p, list):
                p = " ".join(m.get("content", "") for m in p if isinstance(m, dict))
            eval_prompts.add(norm(str(p)))
    rl_norm = set()
    for r in rows:
        first = ""
        for m in r["prompt"]:
            if isinstance(m, dict) and m.get("role") == "user":
                first = str(m.get("content", ""))
                break
        rl_norm.add(norm(first))
    overlap = rl_norm & eval_prompts
    if overlap:
        raise RuntimeError(
            "CONTAM GATE FAILED: %d RL prompts overlap the 158 eval tasks. "
            "Red-line violation. samples=%s" % (len(overlap), list(overlap)[:3]))
    logger.info("contam gate PASS: 0/%d RL prompts overlap 158 eval tasks",
                len(rl_norm))


def build_prompt_ids(tokenizer, messages: List[Dict[str, str]],
                     max_len: int) -> torch.Tensor:
    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True)
    ids = tokenizer.encode(text, add_special_tokens=False)
    if len(ids) > max_len:
        ids = ids[-max_len:]
    return torch.tensor(ids, dtype=torch.long)


@torch.no_grad()
def generate_group(model, tokenizer, prompt_ids: torch.Tensor, g: int,
                   max_resp: int, temperature: float, top_p: float,
                   device: str) -> torch.Tensor:
    """Generate G completions for one prompt; return full ids (G, P+R)."""
    pad_id = tokenizer.pad_token_id
    eos_list = tokenizer.eos_token_id
    eos_ids = set(eos_list if isinstance(eos_list, list) else [eos_list])
    p = prompt_ids.to(device)
    batch = p.unsqueeze(0).expand(g, -1).contiguous()
    attn = torch.ones_like(batch)
    model.eval()
    out = model.generate(
        input_ids=batch, attention_mask=attn, max_new_tokens=max_resp,
        do_sample=True, temperature=temperature, top_p=top_p,
        pad_token_id=pad_id, eos_token_id=list(eos_ids) if eos_ids else None)
    return out


def _logprobs_from_logits(model, full_ids: torch.Tensor, attn_mask: torch.Tensor,
                          loss_mask: torch.Tensor, device: str,
                          grad: bool = False) -> torch.Tensor:
    """Per-token logprob of each response token. Returns (G, L-1) masked logprobs.

    attn_mask: 1 for all REAL tokens (prompt+response, excl pad) -> passed to
               the model so it attends correctly to the prompt.
    loss_mask: 1 for RESPONSE tokens only -> selects which token logprobs enter
               the GRPO loss/advantage.
    logprob of token t = log_softmax(logits[t-1])[token[t]].
    """
    full_ids = full_ids.to(device)
    attn_mask = attn_mask.to(device)
    loss_mask = loss_mask.to(device)
    ctx = torch.enable_grad() if grad else torch.no_grad()
    with ctx:
        logits = model(full_ids, attention_mask=attn_mask).logits[:, :-1, :]
    targets = full_ids[:, 1:]
    logp = torch.log_softmax(logits.float(), dim=-1)
    tok_logp = torch.gather(logp, 2, targets.unsqueeze(-1)).squeeze(-1)
    m = loss_mask[:, 1:].float()
    return tok_logp * m


def masked_mean(x: torch.Tensor, mask: torch.Tensor, eps: float = 1e-8) -> torch.Tensor:
    return (x * mask).sum() / (mask.sum() + eps)


def run_smoke_or_train(cfg: Cfg) -> None:
    from transformers import AutoModelForCausalLM, AutoTokenizer

    os.makedirs(cfg.output_dir, exist_ok=True)
    torch.manual_seed(cfg.seed)
    random.seed(cfg.seed)
    np.random.seed(cfg.seed)

    logger.info("loading tokenizer from %s", cfg.sft_ckpt)
    tokenizer = AutoTokenizer.from_pretrained(cfg.sft_ckpt, trust_remote_code=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    pad_id = tokenizer.pad_token_id
    eos_list = tokenizer.eos_token_id
    eos_ids = set(eos_list if isinstance(eos_list, list) else [eos_list])

    dtype = torch.bfloat16 if cfg.bf16 else torch.float32
    logger.info("loading policy model (%s) on %s", dtype, cfg.device)
    policy = AutoModelForCausalLM.from_pretrained(
        cfg.sft_ckpt, torch_dtype=dtype, attn_implementation="sdpa",
        trust_remote_code=True).to(cfg.device)
    if cfg.grad_checkpointing:
        policy.gradient_checkpointing_enable()
        policy.config.use_cache = False

    logger.info("loading frozen reference model")
    ref = AutoModelForCausalLM.from_pretrained(
        cfg.sft_ckpt, torch_dtype=dtype, attn_implementation="sdpa",
        trust_remote_code=True).to(cfg.device)
    ref.eval()
    for pp in ref.parameters():
        pp.requires_grad_(False)

    policy.train()
    optim = torch.optim.AdamW(policy.parameters(), lr=cfg.lr,
                              betas=(0.9, 0.95), eps=1e-8, weight_decay=0.0)

    rmod = load_reward_module(cfg.reward_fn_path)
    compute_score = rmod.compute_score
    rows = load_rl_data(cfg.rl_data)
    logger.info("loaded %d RL prompts", len(rows))

    metrics_log: List[Dict[str, Any]] = []
    global_step = 0

    def sample_prompts(n: int) -> List[Dict[str, Any]]:
        return random.sample(rows, min(n, len(rows)))

    for step in range(1, cfg.total_steps + 1):
        t0 = time.time()
        prompts = sample_prompts(cfg.batch_prompts)
        prompt_ids_list = [build_prompt_ids(tokenizer, pr["prompt"],
                                            cfg.max_prompt_len) for pr in prompts]
        prompt_lens = [p.numel() for p in prompt_ids_list]

        all_full: List[torch.Tensor] = []
        all_rewards: List[float] = []
        group_ids: List[int] = []
        for pi, (pr, pids) in enumerate(zip(prompts, prompt_ids_list)):
            full = generate_group(policy, tokenizer, pids, cfg.group_size,
                                  cfg.max_response_len, cfg.temperature,
                                  cfg.top_p, cfg.device)
            rm = pr.get("reward_model", {})
            gt = rm.get("canonical_solution", "") or rm.get("test_code", "")
            for gi in range(full.shape[0]):
                resp = full[gi, pids.numel():]
                t_ids = resp.tolist()
                stop = len(t_ids)
                for k, tk in enumerate(t_ids):
                    if tk == pad_id or tk in eos_ids:
                        stop = k + 1
                        break
                text = tokenizer.decode(t_ids[:stop], skip_special_tokens=True)
                score = compute_score(DATA_SOURCE, text, gt, rm, arm=cfg.reward_arm,
                                      api_database=cfg.api_database,
                                      auto_fallback=cfg.auto_fallback,
                                      step=global_step)
                all_full.append(full[gi].clone())
                all_rewards.append(float(score))
                group_ids.append(pi)

        Gtot = len(all_full)
        L = max(t.numel() for t in all_full)
        full_batch = torch.full((Gtot, L), pad_id, dtype=torch.long)
        # loss_mask: 1 for RESPONSE tokens only (GRPO loss selection)
        loss_mask = torch.zeros((Gtot, L), dtype=torch.long)
        # attn_mask: 1 for all REAL tokens (prompt+response, excl pad) -> model
        # attends to the prompt; pad positions are masked.
        attn_mask = torch.zeros((Gtot, L), dtype=torch.long)
        for i in range(Gtot):
            g = group_ids[i]
            plen = prompt_lens[g]
            seq = all_full[i]
            slen = seq.numel()
            full_batch[i, :slen] = seq
            # real tokens = prompt (0..plen) + response up to first pad/eos
            resp = seq[plen:]
            stop = resp.numel()
            for j in range(resp.numel()):
                if resp[j].item() == pad_id or resp[j].item() in eos_ids:
                    stop = j + 1
                    break
            real_len = plen + stop
            attn_mask[i, :real_len] = 1
            loss_mask[i, plen:real_len] = 1

        with torch.no_grad():
            old_logp = _logprobs_from_logits(policy, full_batch, attn_mask,
                                             loss_mask, cfg.device, grad=False)
            ref_logp = _logprobs_from_logits(ref, full_batch, attn_mask,
                                             loss_mask, cfg.device, grad=False)

        rewards = torch.tensor(all_rewards, dtype=torch.float32, device=cfg.device)
        adv = torch.zeros_like(rewards)
        for g in range(len(prompts)):
            idx = [i for i, gid in enumerate(group_ids) if gid == g]
            if not idx:
                continue
            r = rewards[idx]
            adv[idx] = (r - r.mean()) / (r.std(unbiased=False) + EPS_ADV)

        full_batch_dev = full_batch.to(cfg.device)
        attn_mask_dev = attn_mask.to(cfg.device)
        loss_mask_dev = loss_mask.to(cfg.device)
        upd_info: Dict[str, Any] = {}
        # restore training mode (generate_group sets eval)
        policy.train()
        for epoch in range(cfg.ppo_epochs):
            logits = policy(full_batch_dev, attention_mask=attn_mask_dev).logits[:, :-1, :]
            targets = full_batch_dev[:, 1:]
            logp = torch.log_softmax(logits.float(), dim=-1)
            new_tok = torch.gather(logp, 2, targets.unsqueeze(-1)).squeeze(-1)
            m = loss_mask_dev[:, 1:].float()
            new_logp = new_tok * m
            ratio = torch.exp(new_logp - old_logp)
            adv_b = adv.unsqueeze(1).expand_as(new_logp)
            surr1 = ratio * adv_b
            surr2 = torch.clamp(ratio, 1.0 - cfg.clip_ratio,
                                1.0 + cfg.clip_ratio) * adv_b
            policy_loss = -masked_mean(torch.min(surr1, surr2), m)
            kl_loss = masked_mean(new_logp - ref_logp, m)
            loss = policy_loss + cfg.kl_coef * kl_loss
            optim.zero_grad(set_to_none=True)
            loss.backward()
            gn = torch.nn.utils.clip_grad_norm_(policy.parameters(),
                                                cfg.max_grad_norm)
            optim.step()
            upd_info = {
                "policy_loss": float(policy_loss.detach().item()),
                "kl_loss": float(kl_loss.detach().item()),
                "grad_norm": float(gn.item()),
                "mean_ratio": float(masked_mean(ratio.detach(), m).item()),
            }

        global_step += 1
        rarr = rewards.detach().cpu().numpy()
        dt = time.time() - t0
        upd_info.update({
            "step": global_step, "rewards_mean": float(rarr.mean()),
            "rewards_std": float(rarr.std()), "rewards_min": float(rarr.min()),
            "rewards_max": float(rarr.max()),
            "frac_nonzero_reward": float((rarr > 0).mean()),
            "frac_positive_adv": float((adv.detach().cpu().numpy() > 0).mean()),
            "wall_sec": round(dt, 1),
        })
        if step % cfg.log_freq == 0:
            logger.info("step %d/%d reward=%.4f+-%.4f nz=%.2f posadv=%.2f "
                        "ploss=%.4f kl=%.5f ratio=%.3f gn=%.2f %.1fs",
                        global_step, cfg.total_steps, upd_info["rewards_mean"],
                        upd_info["rewards_std"], upd_info["frac_nonzero_reward"],
                        upd_info["frac_positive_adv"], upd_info["policy_loss"],
                        upd_info["kl_loss"], upd_info["mean_ratio"],
                        upd_info["grad_norm"], dt)
        metrics_log.append(upd_info)

        if global_step % cfg.save_freq == 0 or global_step == cfg.total_steps:
            ck_dir = os.path.join(cfg.output_dir, "global_step_%d" % global_step)
            os.makedirs(ck_dir, exist_ok=True)
            policy.save_pretrained(ck_dir, safe_serialization=True)
            tokenizer.save_pretrained(ck_dir)
            with open(os.path.join(ck_dir, "optimizer.pt"), "wb") as f:
                torch.save(optim.state_dict(), f)
            try:
                cr = rmod.get_cheat_rate_report()
                with open(os.path.join(cfg.output_dir, "cheat_rate.json"),
                          "w") as f:
                    json.dump(cr, f, indent=2)
                logger.info("cheat_rate: total=%s cheat=%s rate=%s",
                            cr.get("total_rollouts"), cr.get("cheat_detected"),
                            cr.get("cheat_rate"))
            except Exception as e:
                logger.warning("cheat report failed: %s", e)
            logger.info("checkpoint saved -> %s", ck_dir)

    with open(os.path.join(cfg.output_dir, "metrics.jsonl"), "w") as f:
        for mm in metrics_log:
            f.write(json.dumps(mm) + "\n")
    logger.info("DONE. surrogate pre-experiment, gains NOT transferable to BaiZe. "
                "metrics -> %s/metrics.jsonl", cfg.output_dir)


def parse_args() -> Cfg:
    ap = argparse.ArgumentParser(description="Single-process GRPO loop (no Ray/verl)")
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--sft-ckpt", default=os.environ.get(
        "SFT_CKPT",
        os.path.join(here, "sft_surrogate_runs",
                     "minicpm5_agentic_v39_pretok", "global_step_105")))
    ap.add_argument("--rl-data", default=os.path.join(here, "rl_pyaether_synth_v2.parquet"))
    ap.add_argument("--reward-fn-path",
                    default=os.path.join(here, "baize_posttrain_reward_functions.py"))
    ap.add_argument("--api-database", default=os.path.expanduser(
        "~/code/eda_fastmcp/docs/API_INFO_MERGED_V3.json"))
    ap.add_argument("--output-dir", default=os.path.join(
        here, "rl_surrogate_runs", "minicpm5_grpo_loop_v1"))
    ap.add_argument("--reward-arm", default="R0")
    ap.add_argument("--no-auto-fallback", action="store_true")
    ap.add_argument("--group-size", type=int, default=4)
    ap.add_argument("--batch-prompts", type=int, default=2)
    ap.add_argument("--total-steps", type=int, default=200)
    ap.add_argument("--save-freq", type=int, default=50)
    ap.add_argument("--log-freq", type=int, default=1)
    ap.add_argument("--lr", type=float, default=3.0e-6)
    ap.add_argument("--kl-coef", type=float, default=0.02)
    ap.add_argument("--clip-ratio", type=float, default=0.2)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--top-p", type=float, default=0.95)
    ap.add_argument("--max-prompt-len", type=int, default=512)
    ap.add_argument("--max-response-len", type=int, default=384)
    ap.add_argument("--ppo-epochs", type=int, default=1)
    ap.add_argument("--no-grad-checkpointing", action="store_true")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--contam-check", action="store_true")
    args = ap.parse_args()
    cfg = Cfg(
        sft_ckpt=args.sft_ckpt, rl_data=args.rl_data,
        reward_fn_path=args.reward_fn_path, api_database=args.api_database,
        output_dir=args.output_dir, reward_arm=args.reward_arm,
        auto_fallback=not args.no_auto_fallback, group_size=args.group_size,
        batch_prompts=args.batch_prompts, total_steps=args.total_steps,
        save_freq=args.save_freq, log_freq=args.log_freq, lr=args.lr,
        kl_coef=args.kl_coef, clip_ratio=args.clip_ratio,
        temperature=args.temperature, top_p=args.top_p,
        max_prompt_len=args.max_prompt_len,
        max_response_len=args.max_response_len, ppo_epochs=args.ppo_epochs,
        grad_checkpointing=not args.no_grad_checkpointing, seed=args.seed,
        smoke=args.smoke, dry_run=args.dry_run, contam_check=args.contam_check)
    cfg.smoke_defaults()
    return cfg


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S")
    cfg = parse_args()

    if cfg.dry_run:
        logger.info("DRY-RUN recipe:")
        for k, v in cfg.__dict__.items():
            logger.info("  %s = %s", k, v)
        rows = load_rl_data(cfg.rl_data)
        logger.info("  RL prompts loaded = %d", len(rows))
        logger.info("  reward module = %s", load_reward_module(cfg.reward_fn_path))
        logger.info("DRY-RUN OK (no model loaded, no GPU)")
        return

    if cfg.contam_check:
        rows = load_rl_data(cfg.rl_data)
        eval_jsonl = os.path.expanduser(
            "~/code/eda_fastmcp/pyAether-eval/original_dataset/"
            "EDA-Eval-PyAether-v20260311.jsonl")
        contam_gate(rows, eval_jsonl)
        logger.info("contam check DONE (PASS)")
        if not cfg.smoke:
            logger.info("contam-check only; exiting (pass --smoke to also train)")
            return

    run_smoke_or_train(cfg)


if __name__ == "__main__":
    main()
