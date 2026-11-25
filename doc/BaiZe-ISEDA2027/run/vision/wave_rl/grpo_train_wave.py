#!/usr/bin/env python
"""Stage-2W GRPO Reinforcement Training for Wave RL (Phase 2).

Group Relative Policy Optimization (no value network, memory-light) that
reinforces the SFT-cold-started policy to measure waveforms accurately via
tool calls: open(.raw) -> get_signal -> get_values -> submit(type, value).

Reward (reuses WaveformGymEnv.compute_reward, plan Stage-2W):
  R_main tiered by rel-err (1.0/0.7/0.4/0.1/0.0); R_evidence +0.3;
  R_dense +0.02/ok-action cap 0.2; R_budget +0.1*(1-wv/MAX); R_anti -2.0.

GRPO: G rollouts/prompt, advantage=(R-mean)/(std+eps), clipped surrogate.
Model: Qwen3-4B-Instruct-2507 + LoRA r=64 (same as Stage-1W SFT).
  trl.GRPOTrainer NOT used (vllm ABI mismatch); self-contained HF generate().
  Vision gap: text-only Qwen3-4B (qwen3_vl unsupported by transformers 4.56);
  get_values obs includes numeric summary so the model can estimate measures.

Usage: torchrun --nproc_per_node=8 wave_rl/grpo_train_wave.py --sft_ckpt_dir P
       python wave_rl/grpo_train_wave.py --smoke_test   (CPU-only)

Author: vision wake#612.  License: project-internal.
"""

import sys, os, time, json, math, random, re, tempfile
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.distributed as dist
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model, TaskType, PeftModel

# --- reuse waveview_gym + gen_sft_trajectories infrastructure ---
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from waveview_gym import (  # noqa: E402
    WaveformGymEnv, generate_circuit, run_ngspice, parse_ngspice_raw,
    detect_signal_type, measure_period, measure_amplitude,
    measure_rise_time, measure_duty_cycle, _CIRCUIT_GENS,
)
from gen_sft_trajectories import (  # noqa: E402
    _gen_diffpair, oracle_measure, _pick_signal, _fmt_val, SYSTEM_PROMPT,
    MEASURE_TARGETS,
)
if "diffpair" not in _CIRCUIT_GENS:
    _CIRCUIT_GENS["diffpair"] = _gen_diffpair

# wake#624 fix: must match SFT's 2B text backbone (LoRA adapter shape must agree).
#   SFT trains LoRA on the 2B text backbone (extract_qwen3vl_2b_text.py output).
#   Loading a 2B-trained adapter into the 4B model would shape-mismatch / garbage.
LLM_PATH_2B = "/nas_train/app.e0031982/datasets/baize-vision/out/wave_sft_stage1w/qwen3vl_2b_text_extracted"
LLM_PATH_4B_FALLBACK = "/nas_train/app.e0031982/models/Qwen/Qwen3-4B-Instruct-2507"
LLM_PATH = LLM_PATH_2B
SFT_CKPT_DIR = "/nas_train/app.e0031982/datasets/baize-vision/out/wave_sft_stage1w"
OUTPUT_DIR = "/nas_train/app.e0031982/datasets/baize-vision/out/wave_grpo_stage2w"

IM_START = "<|im_start|>"
IM_END = "<|im_end|>"
ROLE_SYSTEM, ROLE_USER, ROLE_ASSISTANT = "system", "user", "assistant"
TOOL_WRAPPER_OPEN, TOOL_WRAPPER_CLOSE = "[Observation]", "[/Observation]"


def parse_args():
    import argparse
    p = argparse.ArgumentParser(description="Stage-2W GRPO for Wave RL")
    p.add_argument('--model_path', type=str, default=LLM_PATH,
                   help="Base LLM path (default: 2B text backbone extracted from "
                        "Qwen3-VL-2B; use LLM_PATH_4B_FALLBACK for 4B if needed).")
    p.add_argument('--sft_ckpt_dir', type=str, default=SFT_CKPT_DIR,
                   help="SFT output dir; will scan for latest step{N}/ with "
                        "adapter_config.json (wake#624 fix).")
    p.add_argument('--output_dir', type=str, default=OUTPUT_DIR)
    p.add_argument('--lora_r', type=int, default=64)
    p.add_argument('--lora_alpha', type=int, default=128)
    p.add_argument('--lora_dropout', type=float, default=0.05)
    p.add_argument('--lr', type=float, default=1e-6, help="RL LR (lower than SFT).")
    p.add_argument('--min_lr', type=float, default=1e-8)
    p.add_argument('--warmup_frac', type=float, default=0.02)
    p.add_argument('--total_steps', type=int, default=500)
    p.add_argument('--batch_prompts', type=int, default=4, help="Prompts/step (B).")
    p.add_argument('--group_size', type=int, default=8, help="Rollouts/prompt (G).")
    p.add_argument('--ppo_epochs', type=int, default=1)
    p.add_argument('--clip_eps', type=float, default=0.2)
    p.add_argument('--beta_kl', type=float, default=0.0, help="KL coef (0=clip-only).")
    p.add_argument('--max_turns', type=int, default=8)
    p.add_argument('--max_new_tokens', type=int, default=48)
    p.add_argument('--temperature', type=float, default=0.8)
    p.add_argument('--seq_len', type=int, default=2048)
    p.add_argument('--log_steps', type=int, default=10)
    p.add_argument('--save_steps', type=int, default=100)
    p.add_argument('--seed', type=int, default=20261105)
    p.add_argument('--smoke_test', action='store_true',
                   help="CPU-only smoke test (no model).")
    p.add_argument('--device', type=str, default='auto', choices=['auto', 'cpu', 'cuda'],
                   help="Force device: 'cpu' for CPU-only even if CUDA is available "
                        "(wake#827: GPU occupied by pretrain, train on CPU).")
    return p.parse_args()


def setup_ddp(force_cpu=False):
    # wake#827: when --device cpu, skip NCCL/CUDA entirely (GPUs busy w/ pretrain)
    if force_cpu:
        return 0, 0, 1
    if 'RANK' in os.environ:
        dist.init_process_group('nccl')
        rank = int(os.environ['RANK'])
        local_rank = int(os.environ.get('LOCAL_RANK', 0))
        world = int(os.environ.get('WORLD_SIZE', 1))
        torch.cuda.set_device(local_rank)
        return rank, local_rank, world
    return 0, 0, 1


def is_main():
    return not dist.is_initialized() or dist.get_rank() == 0


def cleanup():
    if dist.is_initialized():
        dist.destroy_process_group()


def print0(*args, **kw):
    if is_main():
        print(*args, **kw, flush=True)



# ---------------------------------------------------------------------------
# Conversation formatting (identical to sft_train_wave.py)
# ---------------------------------------------------------------------------
def format_turn(role, content):
    return f"{IM_START}{role}\n{content}{IM_END}\n"


def conversation_to_text(conversation):
    """Convert conversation -> full text + list of (start,end) assistant spans."""
    parts, char_pos, assistant_spans = [], 0, []
    for msg in conversation:
        role = msg['role']
        if role == 'tool':
            wrapped = (f"{TOOL_WRAPPER_OPEN}\n{msg['content']}\n"
                       f"{TOOL_WRAPPER_CLOSE}")
            turn_text = format_turn(ROLE_USER, wrapped)
        else:
            turn_text = format_turn(role, msg['content'])
        if role == 'assistant':
            start = char_pos + len(f"{IM_START}{ROLE_ASSISTANT}\n")
            end = char_pos + len(turn_text) - len(f"{IM_END}\n")
            assistant_spans.append((start, end))
        parts.append(turn_text)
        char_pos += len(turn_text)
    return "".join(parts), assistant_spans


# ---------------------------------------------------------------------------
# Tool-call parsing + observation formatting
# ---------------------------------------------------------------------------
_TOOL_RE = re.compile(
    r'^\s*(open|get_signal|get_type|get_bits|get_values|dump_hier|submit)'
    r'\s*\((.*)\)\s*$', re.IGNORECASE)


def parse_tool_call(text):
    """Parse a model-generated tool-call string -> (action, kwargs) or None."""
    text = text.strip()
    m = _TOOL_RE.match(text)
    if not m:
        m2 = re.search(
            r'(open|get_signal|get_type|get_bits|get_values|dump_hier|submit)'
            r'\s*\(([^)]*)\)', text, re.IGNORECASE)
        if not m2:
            return None
        action, args_str = m2.group(1).lower(), m2.group(2)
    else:
        action, args_str = m.group(1).lower(), m.group(2)
    args = [a.strip().strip("'\"") for a in args_str.split(',')] if args_str.strip() else []
    kw = {}
    if action == 'open':
        kw['file'] = args[0] if args else ''
    elif action in ('get_signal', 'get_values', 'get_type', 'get_bits'):
        kw['signal_name'] = args[0] if args else ''
    elif action == 'submit':
        if len(args) >= 2:
            kw['measure_type'] = args[0]
            try:
                kw['value'] = float(args[1])
            except ValueError:
                kw['value'] = None
        elif len(args) == 1:
            kw['measure_type'] = ''
            try:
                kw['value'] = float(args[0])
            except ValueError:
                kw['value'] = None
    return action, kw


def _numeric_summary(values):
    v = np.asarray(values, dtype=np.float64)
    if len(v) == 0:
        return "empty"
    return (f"min={_fmt_val(float(v.min()))}, max={_fmt_val(float(v.max()))}, "
            f"mean={_fmt_val(float(v.mean()))}, std={_fmt_val(float(v.std()))}, "
            f"n={len(v)}")


def format_observation(action, info, env, spec):
    """Format env step info -> tool-response text (SFT-consistent + summary)."""
    result = info.get('result', 'ok')
    fname = os.path.basename(spec.raw_path)
    if action == 'open':
        if result == 'ok':
            return (f"Opened {fname}: {info.get('n_points','?')} time points, "
                    f"{info.get('n_signals','?')} signals available.")
        return f"Error opening {fname}: {result}."
    if action == 'get_signal':
        sn = info.get('signal_name', '')
        if result == 'ok':
            return (f"Signal {sn}: type={info.get('type','?')}, "
                    f"{info.get('nsamples','?')} samples loaded.")
        if result == 'signal_not_found':
            return (f"Error: signal {sn} not found. "
                    f"Use dump_hier() to list available signals.")
        return f"Error: {result} (file not open?)."
    if action == 'get_type':
        if result == 'ok':
            return f"Signal type: {info.get('type','?')}."
        return f"Error: {result}."
    if action == 'get_bits':
        if result == 'ok':
            return f"Signal bits: {info.get('bits','?')}."
        return f"Error: {result}."
    if action == 'get_values':
        sn = info.get('signal_name', '')
        if result == 'ok':
            vals = info.get('values')
            summary = _numeric_summary(vals) if vals is not None else "n/a"
            t_range = info.get('t_range')
            tr = (f"t_range=[{_fmt_val(t_range[0])}, {_fmt_val(t_range[1])}]"
                  if t_range else "t_range=n/a")
            return (f"Retrieved {info.get('nsamples','?')} time-value pairs "
                    f"for {sn}. {tr}. Summary: {summary}.")
        return f"Error: {result} (signal not loaded?)."
    if action == 'dump_hier':
        if result == 'ok':
            return f"Available signals: {', '.join(info.get('available', []))}."
        return f"Error: {result} (file not open?)."
    if action == 'submit':
        if result in ('ok', 'submitted'):
            sv = info.get('submitted_value')
            re_ = info.get('rel_err')
            if re_ is not None:
                tag = "PASS" if re_ <= 0.05 else "FAIL"
                return (f"Submitted {info.get('measure_type','?')}="
                        f"{_fmt_val(sv)}. Relative error: {re_*100:.3f}%. {tag}.")
            return f"Submitted {info.get('measure_type','?')}={_fmt_val(sv)}."
        return f"Error submitting: {result}."
    return f"Unknown action {action}: {result}."


def build_prompt(spec, target, signal):
    fname = os.path.basename(spec.raw_path)
    user = (f"Open the simulation file {fname} and measure the {target} "
            f"of signal {signal}.")
    return ({"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user})



# ---------------------------------------------------------------------------
# Rollout: multi-turn generation + env interaction
# ---------------------------------------------------------------------------
def rollout_episode(model, tokenizer, env, spec, target, signal, device, dtype,
                    max_turns=8, max_new_tokens=48, temperature=0.8, seq_len=2048):
    """Generate one full episode. Returns (conversation, reward, info_dict)."""
    system_msg, user_msg = build_prompt(spec, target, signal)
    conversation = [system_msg, user_msg]
    env.reset()
    reward, done, submit_info = 0.0, False, {}

    for turn in range(max_turns):
        prompt_msgs = []
        for msg in conversation:
            if msg['role'] == 'tool':
                wrapped = (f"{TOOL_WRAPPER_OPEN}\n{msg['content']}\n"
                           f"{TOOL_WRAPPER_CLOSE}")
                prompt_msgs.append({"role": "user", "content": wrapped})
            else:
                prompt_msgs.append(msg)
        prompt_parts = [format_turn(m['role'], m['content']) for m in prompt_msgs]
        prompt_text = "".join(prompt_parts) + f"{IM_START}{ROLE_ASSISTANT}\n"
        enc = tokenizer(prompt_text, add_special_tokens=False,
                        return_tensors='pt', truncation=True,
                        max_length=seq_len - max_new_tokens - 4)
        input_ids = enc['input_ids'].to(device)
        with torch.no_grad():
            out = model.generate(
                input_ids, max_new_tokens=max_new_tokens,
                do_sample=temperature > 0, temperature=max(temperature, 1e-5),
                top_p=0.95,
                pad_token_id=tokenizer.pad_token_id if tokenizer.pad_token_id is not None else 0,
                eos_token_id=tokenizer.convert_tokens_to_ids(IM_END))
        new_tokens = out[0, input_ids.shape[1]:]
        gen_text = tokenizer.decode(new_tokens, skip_special_tokens=False)
        gen_text = gen_text.replace(IM_END, "").strip()
        if not gen_text:
            gen_text = "dump_hier()"
        conversation.append({"role": "assistant", "content": gen_text})

        parsed = parse_tool_call(gen_text)
        if parsed is None:
            obs = ("Error: unrecognized action. "
                   "Use open/get_signal/get_values/dump_hier/submit.")
            conversation.append({"role": "tool", "content": obs})
            continue
        action, kw = parsed
        _, obs_reward, obs_done, obs_info = env.step(action, **kw)
        if action == 'get_values' and obs_info.get('result') == 'ok':
            sn = kw.get('signal_name', '')
            sig = env.state.opened_signals.get(sn)
            if sig and env.state.raw_parsed is not None:
                obs_info['values'] = sig.get('values')
                t = env.state.raw_parsed['data'][:, 0]
                obs_info['t_range'] = (float(t[0]), float(t[-1]))
                obs_info['nsamples'] = sig.get('nsamples', len(sig.get('values', [])))
        if action in ('get_signal', 'get_values'):
            obs_info['signal_name'] = kw.get('signal_name', '')
        if action == 'submit':
            obs_info['measure_type'] = kw.get('measure_type', '')
            obs_info['signal_name'] = kw.get('signal_name', '')
        obs_text = format_observation(action, obs_info, env, spec)
        conversation.append({"role": "tool", "content": obs_text})
        reward += obs_reward
        if obs_done or action == 'submit':
            done = True
            submit_info = obs_info
            break

    info = {
        "reward": reward,
        "turns": len([m for m in conversation if m['role'] == 'assistant']),
        "submitted": env.state.submitted if env.state else False,
        "submit_value": env.state.submit_value if env.state else None,
        "submit_type": env.state.submit_measure_type if env.state else None,
        "gt": env.spec.gt if env.spec else {},
        "wv_calls": env.state.wv_calls if env.state else 0,
    }
    return conversation, reward, info


# ---------------------------------------------------------------------------
# Tokenization + log-prob computation
# ---------------------------------------------------------------------------
def tokenize_for_logprob(conversation, tokenizer, seq_len=2048):
    full_text, assistant_spans = conversation_to_text(conversation)
    enc = tokenizer(full_text, add_special_tokens=False,
                    truncation=True, max_length=seq_len,
                    return_offsets_mapping=True, return_tensors=None)
    input_ids = enc['input_ids']
    offsets = enc['offset_mapping']
    mask = [False] * len(input_ids)
    for span_start, span_end in assistant_spans:
        for tok_idx, (tok_start, tok_end) in enumerate(offsets):
            if tok_start >= span_end:
                break
            if tok_end <= span_start:
                continue
            if tok_idx < len(mask):
                mask[tok_idx] = True
    return input_ids[:seq_len], mask[:seq_len]


def compute_logprobs(model, input_ids, assistant_mask, device, dtype):
    ids = torch.tensor([input_ids], dtype=torch.long, device=device)
    attn = torch.ones_like(ids)
    # wake#827: use device.type for autocast context (was hardcoded 'cuda')
    use_autocast = device.type == 'cuda'
    with torch.autocast(device.type, dtype=dtype, enabled=use_autocast):
        logits = model(input_ids=ids, attention_mask=attn).logits
    log_probs = F.log_softmax(logits[:, :-1, :].float(), dim=-1)
    target_ids = ids[:, 1:]
    token_lps = log_probs.gather(2, target_ids.unsqueeze(-1)).squeeze(-1)
    shifted_mask = torch.tensor(assistant_mask[1:], dtype=torch.bool, device=device)
    return token_lps[0][shifted_mask]



# ---------------------------------------------------------------------------
# Model setup
# ---------------------------------------------------------------------------
def build_model(args, device, dtype):
    print0(f"Loading base LLM: {args.model_path}")
    llm = AutoModelForCausalLM.from_pretrained(
        args.model_path, torch_dtype=dtype,
        device_map={'': device}, trust_remote_code=True)
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=args.lora_r, lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"])
    # wake#624 fix: SFT saves final checkpoint as step{total_steps} (e.g. step3000),
    #   NOT step2000/final.  Scan for the *highest-numbered* step dir with an
    #   adapter_config.json, falling back to the root dir or "final".
    sft_dir = args.sft_ckpt_dir
    sft_adapter = None
    import glob as _glob
    _step_dirs = []
    for _d in _glob.glob(os.path.join(sft_dir, "step*")):
        _num = os.path.basename(_d).replace("step", "")
        if _num.isdigit():
            _step_dirs.append((int(_num), _d))
    _step_dirs.sort(key=lambda x: x[0], reverse=True)  # highest step first
    _candidates = ([_d for _, _d in _step_dirs] +
                   [sft_dir, os.path.join(sft_dir, "final")])
    for sub in _candidates:
        if os.path.isdir(sub) and os.path.exists(os.path.join(sub, "adapter_config.json")):
            sft_adapter = sub
            break
    if sft_adapter:
        print0(f"Loading SFT LoRA adapter from {sft_adapter}")
        llm = PeftModel.from_pretrained(llm, sft_adapter, is_trainable=True)
    else:
        print0(f"No SFT adapter found under {sft_dir}; using fresh LoRA.")
        llm = get_peft_model(llm, lora_config)
    llm.print_trainable_parameters()
    tokenizer = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    return llm, tokenizer


def save_checkpoint(llm, tokenizer, output_dir, step, rank=0):
    if rank != 0:
        return
    ckpt_dir = os.path.join(output_dir, f"step{step}")
    os.makedirs(ckpt_dir, exist_ok=True)
    llm_module = llm.module if hasattr(llm, 'module') else llm
    llm_module.save_pretrained(ckpt_dir)
    tokenizer.save_pretrained(ckpt_dir)
    meta = {"step": step, "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "stage": "grpo_stage2w"}
    with open(os.path.join(ckpt_dir, "training_meta.json"), 'w') as f:
        json.dump(meta, f, indent=2)
    print0(f"  Saved GRPO checkpoint to {ckpt_dir}/")


def get_lr(step, nsteps, lr, min_lr, warmup_frac):
    warmup_steps = max(1, int(nsteps * warmup_frac))
    if step < warmup_steps:
        return lr * step / warmup_steps
    progress = (step - warmup_steps) / max(1, nsteps - warmup_steps)
    return min_lr + 0.5 * (lr - min_lr) * (1 + math.cos(
        math.pi * min(1.0, progress)))


# ---------------------------------------------------------------------------
# GRPO loss
# ---------------------------------------------------------------------------
def grpo_loss(new_logprobs_list, old_logprobs_list, advantages_list,
              clip_eps=0.2, beta=0.0):
    total_loss = 0.0
    total_tokens = 0
    for new_lp, old_lp, adv in zip(new_logprobs_list, old_logprobs_list,
                                   advantages_list):
        if new_lp.numel() == 0:
            continue
        adv_t = torch.tensor(adv, dtype=new_lp.dtype, device=new_lp.device)
        ratio = torch.exp(new_lp - old_lp.detach())
        surr1 = adv_t * ratio
        surr2 = adv_t * torch.clamp(ratio, 1.0 - clip_eps, 1.0 + clip_eps)
        total_loss = total_loss + (-torch.min(surr1, surr2).sum())
        total_tokens += new_lp.numel()
    if total_tokens == 0:
        return None
    return total_loss / total_tokens


# ---------------------------------------------------------------------------
# Task sampler
# ---------------------------------------------------------------------------
class TaskSampler:
    def __init__(self, seed=20261105, workdir=None):
        self.rng = np.random.default_rng(seed)
        self.workdir = workdir or tempfile.mkdtemp(prefix="wave_grpo_", dir="/tmp")
        os.makedirs(self.workdir, exist_ok=True)
        self.circuit_types = list(_CIRCUIT_GENS.keys())
        self.targets = list(MEASURE_TARGETS)

    def sample(self):
        ct = str(self.rng.choice(self.circuit_types))
        target = str(self.rng.choice(self.targets))
        ep_wd = os.path.join(self.workdir, f"grpo_{int(self.rng.integers(0, 1e9))}")
        os.makedirs(ep_wd, exist_ok=True)
        spec = generate_circuit(self.rng, ep_wd, ct)
        ok, log = run_ngspice(spec.netlist)
        if not ok or not os.path.exists(spec.raw_path):
            return None
        signal = _pick_signal(spec, target)
        return spec, target, signal, ep_wd



# ---------------------------------------------------------------------------
# Main training loop
# ---------------------------------------------------------------------------
def main():
    args = parse_args()
    if args.smoke_test:
        return smoke_test()
    force_cpu = args.device == 'cpu'
    rank, local_rank, world = setup_ddp(force_cpu=force_cpu)
    if force_cpu:
        device = torch.device('cpu')
        dtype = torch.float32
    else:
        device = torch.device(f'cuda:{local_rank}' if torch.cuda.is_available() else 'cpu')
        dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
    os.makedirs(args.output_dir, exist_ok=True)
    torch.manual_seed(args.seed + rank)
    np.random.seed(args.seed + rank)
    random.seed(args.seed + rank)
    llm, tokenizer = build_model(args, device, dtype)
    llm.train()
    trainable = [p for p in llm.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(trainable, lr=args.lr, weight_decay=0.0)
    sampler_tasks = TaskSampler(seed=args.seed + rank)
    print0(f"\n=== Stage-2W GRPO Training ===")
    print0(f"  B={args.batch_prompts} G={args.group_size} "
          f"steps={args.total_steps} ppo_epochs={args.ppo_epochs}")
    print0(f"  clip={args.clip_eps} beta={args.beta_kl} lr={args.lr}")
    print0(f"  World: {world} device={device} dtype={dtype}\n")
    step, t0 = 0, time.time()
    log_reward, log_count, log_submit = 0.0, 0, 0
    train_log = []  # wake#827: per-step log for loss/reward curve (P1 requirement)
    while step < args.total_steps:
        all_rollouts, prompts_done = [], 0
        while prompts_done < args.batch_prompts:
            task = sampler_tasks.sample()
            if task is None:
                continue
            spec, target, signal, ep_wd = task
            env = WaveformGymEnv(circuit_type=spec.circuit_type,
                                 measure_target=target, workdir=ep_wd)
            env.spec = spec
            group_conv, group_reward, group_info = [], [], []
            for g in range(args.group_size):
                try:
                    conv, rew, info = rollout_episode(
                        llm, tokenizer, env, spec, target, signal, device, dtype,
                        max_turns=args.max_turns, max_new_tokens=args.max_new_tokens,
                        temperature=args.temperature, seq_len=args.seq_len)
                except Exception:
                    conv, rew, info = [], -1.0, {"submitted": False}
                group_conv.append(conv)
                group_reward.append(rew)
                group_info.append(info)
            rewards = np.array(group_reward, dtype=np.float64)
            advs = (rewards - rewards.mean()) / (rewards.std() + 1e-4)
            for conv, rew, adv, info in zip(group_conv, group_reward, advs, group_info):
                if len(conv) > 0:
                    all_rollouts.append((conv, float(adv), info, rew))
            prompts_done += 1
        old_logprobs_list, valid_rollouts = [], []
        for conv, adv, info, rew in all_rollouts:
            input_ids, amask = tokenize_for_logprob(conv, tokenizer, args.seq_len)
            if sum(amask) == 0:
                continue
            with torch.no_grad():
                old_lp = compute_logprobs(llm, input_ids, amask, device, dtype)
            old_logprobs_list.append(old_lp)
            valid_rollouts.append((conv, adv, info, rew, input_ids, amask))
        if len(valid_rollouts) == 0:
            print0(f"  step {step+1}: no valid rollouts, skipping")
            step += 1
            continue
        advantages_list = [v[1] for v in valid_rollouts]
        lr_now = args.lr
        step_loss = 0.0
        for pe in range(args.ppo_epochs):
            new_logprobs_list = []
            for conv, adv, info, rew, iids, amask in valid_rollouts:
                new_logprobs_list.append(
                    compute_logprobs(llm, iids, amask, device, dtype))
            loss = grpo_loss(new_logprobs_list, old_logprobs_list,
                             advantages_list, clip_eps=args.clip_eps,
                             beta=args.beta_kl)
            if loss is None:
                break
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(trainable, 1.0)
            lr_now = get_lr(step, args.total_steps, args.lr, args.min_lr,
                            args.warmup_frac)
            for pg in optimizer.param_groups:
                pg['lr'] = lr_now
            optimizer.step()
            step_loss = float(loss.detach().cpu().item())
        rewards = [v[3] for v in valid_rollouts]
        submitted = sum(1 for v in valid_rollouts if v[2].get('submitted'))
        log_reward += float(np.mean(rewards))
        log_submit += submitted
        log_count += 1
        step_wall = time.time() - t0
        train_log.append({"step": step + 1, "loss": step_loss,
                          "reward_mean": float(np.mean(rewards)),
                          "submit_pct": submitted / max(1, len(rewards)) * 100,
                          "lr": lr_now, "wall_s": step_wall})
        if (step + 1) % args.log_steps == 0 and is_main():
            avg_r = log_reward / max(1, log_count)
            avg_sub = (log_submit / max(1, log_count * args.group_size *
                       args.batch_prompts)) * 100
            elapsed = time.time() - t0
            sps = (step + 1) / elapsed
            eta = (args.total_steps - step - 1) / max(0.1, sps)
            print0(f"  step {step+1}/{args.total_steps} | loss {step_loss:.4f} | "
                   f"reward {avg_r:.3f} | submit {avg_sub:.0f}% | lr {lr_now:.2e} | "
                   f"{sps:.2f} step/s | ETA {eta/60:.1f} min")
            log_reward, log_count, log_submit = 0.0, 0, 0
        if (step + 1) % args.save_steps == 0:
            save_checkpoint(llm, tokenizer, args.output_dir, step + 1, rank)
        step += 1
    save_checkpoint(llm, tokenizer, args.output_dir, args.total_steps, rank)
    # wake#827: save structured training log for loss/reward curve (P1 requirement)
    if is_main() and train_log:
        log_path = os.path.join(args.output_dir, "training_log.json")
        with open(log_path, 'w') as f:
            json.dump({"config": {"batch_prompts": args.batch_prompts,
                        "group_size": args.group_size, "total_steps": args.total_steps,
                        "lr": args.lr, "device": str(device),
                        "max_turns": args.max_turns, "max_new_tokens": args.max_new_tokens,
                        "seq_len": args.seq_len, "clip_eps": args.clip_eps},
                       "steps": train_log,
                       "total_wall_s": time.time() - t0}, f, indent=2)
        print0(f"  Training log saved to {log_path}")
    print0(f"\n=== GRPO complete ({time.time()-t0:.1f}s) ===")
    cleanup()



# ---------------------------------------------------------------------------
# CPU-only smoke test (no GPU, no model)
# ---------------------------------------------------------------------------
def smoke_test():
    print("=== GRPO smoke test (CPU-only, no model) ===")
    sampler = TaskSampler(seed=42)
    ok, fail = 0, 0
    rewards = []
    for i in range(6):
        task = sampler.sample()
        if task is None:
            fail += 1
            continue
        spec, target, signal, ep_wd = task
        env = WaveformGymEnv(circuit_type=spec.circuit_type,
                             measure_target=target, workdir=ep_wd)
        env.spec = spec
        env.reset()
        fname = os.path.basename(spec.raw_path)
        conv = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Open the simulation file {fname} and measure the {target} of signal {signal}."},
        ]
        total_r = 0.0
        for act, kw in [("open", {}), ("get_signal", {"signal_name": signal}),
                        ("get_values", {"signal_name": signal})]:
            _, r, done, info = env.step(act, **kw)
            label = signal if act != 'open' else fname
            conv.append({"role": "assistant", "content": f"{act}({label})"})
            if act == 'get_values' and info.get('result') == 'ok':
                sig = env.state.opened_signals.get(signal)
                if sig and env.state.raw_parsed is not None:
                    info['values'] = sig.get('values')
                    t = env.state.raw_parsed['data'][:, 0]
                    info['t_range'] = (float(t[0]), float(t[-1]))
                    info['nsamples'] = sig.get('nsamples')
            if act in ('get_signal', 'get_values'):
                info['signal_name'] = signal
            conv.append({"role": "tool", "content": format_observation(act, info, env, spec)})
            total_r += r
            if done:
                break
        oracle = oracle_measure(env.state.raw_parsed, signal)
        gt_val = oracle.get(target)
        if gt_val is not None:
            _, r, done, info = env.step("submit", value=float(gt_val),
                                        measure_type=target, signal_name=signal)
            info['measure_type'] = target
            conv.append({"role": "assistant", "content": f"submit({target}, {_fmt_val(gt_val)})"})
            conv.append({"role": "tool", "content": format_observation("submit", info, env, spec)})
            total_r += r
        rewards.append(total_r)
        for tc in ["open(rc.raw)", "get_signal(v(out))",
                   "submit(amplitude, 2.724243)", "dump_hier()", "get_values(v(in))"]:
            if parse_tool_call(tc) is None:
                print(f"  [FAIL] parse '{tc}' -> None")
                fail += 1
        text, spans = conversation_to_text(conv)
        if len(spans) == 0:
            print("  [FAIL] no assistant spans")
            fail += 1
        ok += 1
    r_arr = np.array(rewards, dtype=np.float64)
    advs = (r_arr - r_arr.mean()) / (r_arr.std() + 1e-4)
    print(f"  Oracle rollouts: {ok} ok, {fail} fail")
    print(f"  Rewards: {[f'{r:.3f}' for r in rewards]}")
    print(f"  Advantages: {[f'{a:.3f}' for a in advs]}")
    nlp = torch.tensor([-0.5, -0.3, -0.2], dtype=torch.float32)
    olp = torch.tensor([-0.4, -0.35, -0.25], dtype=torch.float32)
    loss = grpo_loss([nlp], [olp], [1.0], clip_eps=0.2)
    print(f"  grpo_loss dummy: {float(loss):.4f} (OK)")
    status = "PASS" if fail == 0 and ok > 0 else "FAIL"
    print(f"=== Smoke test: {status} ===")
    return 0 if status == "PASS" else 1


if __name__ == '__main__':
    sys.exit(main())

