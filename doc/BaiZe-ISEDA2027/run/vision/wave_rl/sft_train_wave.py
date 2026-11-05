#!/usr/bin/env python
"""Stage-1W SFT Cold-Start Training for Wave RL (Phase 1).

Trains a text-only LLM on multi-turn tool-use trajectories that teach the
model to "read" waveforms via tool calls:
  open(.raw) -> get_signal(name) -> get_values(name) -> submit(type, value)

This is the SFT cold-start step (Stage-1W) before GRPO reinforcement (Stage-2W).
The trajectories are TEXT-ONLY (no images) -- the vision/screenshot component
comes in Phase 2 RL.  Phase 1 focuses on learning the tool-use conversation
pattern and measurement submission format.

Model choice:
  The operator task (2026-11-05) specifies a **2B MLLM**.  The natural candidate
is Qwen3-VL-2B-Instruct, but its architecture (qwen3_vl) is NOT recognized by
transformers 4.56.1.  Rather than upgrading transformers (which risks breaking
the existing MLLM training infra for ArmE-R2), we extract the VL model's TEXT
BACKBONE as a standalone Qwen3ForCausalLM (see extract_qwen3vl_2b_text.py).
The text backbone is a plain Qwen3 decoder (1.72 B params, 28 layers,
hidden=2048) that loads with transformers 4.56.1 -- no upgrade needed.  The
LoRA adapter trained here will transfer to the full Qwen3-VL-2B in Phase 2
(same text-backbone weights) once transformers is upgraded for multimodal RL.
RoPE: the VL backbone uses mRoPE, but tf 4.56.1 falls back to standard RoPE;
empirically coherent for short text-only SFT (verified generation test).
Fallback: --model_path can point to Qwen3-4B-Instruct-2507 if needed.

Hyperparameters (operator instruction 2026-11-05 Phase 1):
  - LoRA: rank=64, alpha=128, dropout=0.05 (same as Stage-1.5/2)
  - LR: 1e-5 (LoRA), cosine decay -> 1e-7, warmup 0.01
  - GBS=8, MBS=1 (9013 trajectories / GBS=8 ~= 1127 steps/epoch;
    2000 steps ~= 1.77 epochs, 3000 steps ~= 2.66 epochs — within "~2000-3000 steps / 2-3 epoch")
  - Data: sft_pilot_balanced.jsonl (9013 trajectories, 17.9 MB, 7 circuit types balanced)

Pre-registered acceptance criteria (Phase 1 step 3):
  - Format correctness >= 90% on held-out synthetic data
  - Submit success rate >= 70% on held-out synthetic data

Usage (8 GPUs):
  cd run/vision
  torchrun --nproc_per_node=8 wave_rl/sft_train_wave.py

Usage (1 GPU):
  CUDA_VISIBLE_DEVICES=0 python wave_rl/sft_train_wave.py

Author: vision wake#611.  License: project-internal.
"""

import sys, os, time, json, math, random, re
from pathlib import Path

import torch
import torch.nn as nn
import torch.distributed as dist
from torch.utils.data import Dataset, DataLoader
from torch.utils.data.distributed import DistributedSampler

from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model, TaskType

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# 2B text backbone extracted from Qwen3-VL-2B-Instruct (see extract_qwen3vl_2b_text.py).
# Aligns with the task's "2B MLLM" spec; LoRA adapter transfers to Phase 2 VL model.
LLM_PATH_2B = "/nas_train/app.e0031982/datasets/baize-vision/out/wave_sft_stage1w/qwen3vl_2b_text_extracted"
LLM_PATH_4B_FALLBACK = "/nas_train/app.e0031982/models/Qwen/Qwen3-4B-Instruct-2507"
LLM_PATH = LLM_PATH_2B
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "sft_pilot_balanced.jsonl")
OUTPUT_DIR = "/nas_train/app.e0031982/datasets/baize-vision/out/wave_sft_stage1w"

# Qwen3 chat-format special tokens (same for Qwen3-4B and Qwen3-VL-2B)
IM_START = "<|im_start|>"
IM_END = "<|im_end|>"
ROLE_SYSTEM = "system"
ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"
# Tool responses are formatted as user messages with a wrapper tag
TOOL_WRAPPER_OPEN = "[Observation]"
TOOL_WRAPPER_CLOSE = "[/Observation]"


def parse_args():
    import argparse
    p = argparse.ArgumentParser(
        description="Stage-1W SFT for Wave RL (text-only tool-use)")
    p.add_argument('--model_path', type=str, default=LLM_PATH,
                   help="HF model path (default: 2B text backbone extracted "
                        "from Qwen3-VL-2B-Instruct). Fallback: "
                        "Qwen3-4B-Instruct-2507 (LLM_PATH_4B_FALLBACK).")
    p.add_argument('--data_file', type=str, default=DATA_FILE)
    p.add_argument('--output_dir', type=str, default=OUTPUT_DIR)
    p.add_argument('--lr', type=float, default=1e-5)
    p.add_argument('--min_lr', type=float, default=1e-7)
    p.add_argument('--nsteps', type=int, default=3000)
    p.add_argument('--gbs', type=int, default=8)
    p.add_argument('--mbs', type=int, default=1)
    p.add_argument('--warmup_frac', type=float, default=0.01)
    p.add_argument('--seq_len', type=int, default=2048)
    p.add_argument('--num_workers', type=int, default=4)
    p.add_argument('--save_steps', type=int, default=500)
    p.add_argument('--log_steps', type=int, default=50)
    p.add_argument('--lora_r', type=int, default=64)
    p.add_argument('--lora_alpha', type=int, default=128)
    p.add_argument('--lora_dropout', type=float, default=0.05)
    p.add_argument('--eval_holdout', type=int, default=200)
    p.add_argument('--seed', type=int, default=42)
    return p.parse_args()


# ---------------------------------------------------------------------------
# DDP helpers
# ---------------------------------------------------------------------------
def setup_ddp():
    if 'RANK' in os.environ:
        rank = int(os.environ['RANK'])
        world = int(os.environ['WORLD_SIZE'])
        local = int(os.environ.get('LOCAL_RANK', 0))
        dist.init_process_group(backend='nccl')
        torch.cuda.set_device(local)
    else:
        rank, world, local = 0, 1, 0
        torch.cuda.set_device(0)
    return rank, world, local


def is_main():
    return dist.get_rank() == 0 if dist.is_initialized() else True


def cleanup():
    if dist.is_initialized():
        dist.destroy_process_group()


def print0(*args, **kw):
    if is_main():
        print(*args, **kw, flush=True)


# ---------------------------------------------------------------------------
# Conversation formatting (manual, since jinja2 3.0.3 can't render chat template)
# ---------------------------------------------------------------------------
def format_turn(role, content):
    """Format a single turn as: <|im_start|>role\ncontent<|im_end|>\n"""
    return f"{IM_START}{role}\n{content}{IM_END}\n"


def conversation_to_text(conversation):
    """Convert a multi-turn conversation list to formatted text + loss mask spans.

    Returns:
        full_text: str -- the formatted conversation
        assistant_spans: list of (start_char, end_char) -- char ranges where
                         loss should be computed (assistant content only)
    """
    parts = []
    assistant_spans = []
    char_pos = 0
    for msg in conversation:
        role = msg['role']
        content = msg['content']
        if role == 'tool':
            # Wrap tool/observation responses as user messages with a tag
            wrapped = f"{TOOL_WRAPPER_OPEN}\n{content}\n{TOOL_WRAPPER_CLOSE}"
            turn_text = format_turn(ROLE_USER, wrapped)
            parts.append(turn_text)
            char_pos += len(turn_text)
        elif role == 'assistant':
            prefix = f"{IM_START}{ROLE_ASSISTANT}\n"
            suffix = f"{IM_END}\n"
            turn_text = prefix + content + suffix
            parts.append(turn_text)
            # Loss span covers content + IM_END + newline
            span_start = char_pos + len(prefix)
            span_end = char_pos + len(prefix) + len(content) + len(IM_END) + 1
            assistant_spans.append((span_start, span_end))
            char_pos += len(turn_text)
        else:
            turn_text = format_turn(role, content)
            parts.append(turn_text)
            char_pos += len(turn_text)
    return "".join(parts), assistant_spans


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------
class WaveSFTDataset(Dataset):
    """Loads JSONL trajectories and tokenizes them with loss masking.

    Each JSONL line has a 'conversation' field: list of {role, content} dicts.
    Roles: system, user, assistant, tool.
    Loss is computed only on assistant content tokens (+ EOS).
    """

    def __init__(self, data_file, tokenizer, seq_len=2048, indices=None):
        self.tokenizer = tokenizer
        self.seq_len = seq_len
        self.samples = []
        with open(data_file, 'r') as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                if indices is not None and i not in indices:
                    continue
                try:
                    traj = json.loads(line)
                    conv = traj.get('conversation', [])
                    if len(conv) < 2:
                        continue
                    self.samples.append(traj)
                except json.JSONDecodeError:
                    continue
        print0(f"[Dataset] Loaded {len(self.samples)} trajectories")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        traj = self.samples[idx]
        conv = traj['conversation']
        full_text, assistant_spans = conversation_to_text(conv)

        # Tokenize with offset mapping for loss masking
        enc = self.tokenizer(
            full_text, add_special_tokens=False,
            truncation=True, max_length=self.seq_len,
            return_offsets_mapping=True, return_tensors=None)
        input_ids = enc['input_ids']
        offsets = enc['offset_mapping']

        labels = [-100] * len(input_ids)
        for span_start, span_end in assistant_spans:
            for tok_idx, (tok_start, tok_end) in enumerate(offsets):
                if tok_start >= span_end:
                    break
                if tok_end <= span_start:
                    continue
                if tok_idx < len(labels):
                    labels[tok_idx] = input_ids[tok_idx]

        input_ids = input_ids[:self.seq_len]
        labels = labels[:self.seq_len]
        return {'input_ids': input_ids, 'labels': labels}


def collate_fn(batch, tokenizer, seq_len):
    """Pad batch to uniform length."""
    input_ids_list = [b['input_ids'] for b in batch]
    labels_list = [b['labels'] for b in batch]
    pad_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else 0
    max_len = min(max(len(ids) for ids in input_ids_list), seq_len)
    padded_ids, padded_labels, attention_mask = [], [], []
    for ids, labels in zip(input_ids_list, labels_list):
        pad_len = max_len - len(ids)
        padded_ids.append(ids + [pad_id] * pad_len)
        padded_labels.append(labels + [-100] * pad_len)
        attention_mask.append([1] * len(ids) + [0] * pad_len)
    return {
        'input_ids': torch.tensor(padded_ids, dtype=torch.long),
        'attention_mask': torch.tensor(attention_mask, dtype=torch.long),
        'labels': torch.tensor(padded_labels, dtype=torch.long),
    }


# ---------------------------------------------------------------------------
# Model setup
# ---------------------------------------------------------------------------
def build_model(args, device, dtype):
    """Load LLM + apply LoRA (fresh, not from a previous stage)."""
    print0(f"Loading LLM: {args.model_path}")
    llm = AutoModelForCausalLM.from_pretrained(
        args.model_path, torch_dtype=dtype,
        device_map={'': device}, trust_remote_code=True)
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=args.lora_r, lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
    )
    llm = get_peft_model(llm, lora_config)
    llm.print_trainable_parameters()
    return llm


def get_lr(step, nsteps, lr, min_lr, warmup_frac):
    warmup_steps = max(1, int(nsteps * warmup_frac))
    if step < warmup_steps:
        return lr * step / warmup_steps
    progress = (step - warmup_steps) / max(1, nsteps - warmup_steps)
    return min_lr + 0.5 * (lr - min_lr) * (1 + math.cos(
        math.pi * min(1.0, progress)))


def save_checkpoint(llm, tokenizer, output_dir, step, rank=0):
    if rank != 0:
        return
    ckpt_dir = os.path.join(output_dir, f"step{step}")
    os.makedirs(ckpt_dir, exist_ok=True)
    llm_module = llm.module if hasattr(llm, 'module') else llm
    llm_module.save_pretrained(ckpt_dir)
    tokenizer.save_pretrained(ckpt_dir)
    meta = {"step": step, "saved_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    with open(os.path.join(ckpt_dir, "training_meta.json"), 'w') as f:
        json.dump(meta, f, indent=2)
    print0(f"  Saved checkpoint to {ckpt_dir}/")


# ---------------------------------------------------------------------------
# Evaluation (format correctness + submit success on held-out data)
# ---------------------------------------------------------------------------
def evaluate_format_and_submit(llm, tokenizer, eval_dataset, device, dtype,
                               max_eval=50):
    """Check if the model generates valid tool-call format and submits."""
    llm.eval()
    format_ok = 0
    submit_ok = 0
    total = min(max_eval, len(eval_dataset))
    valid_tool_patterns = ['open(', 'get_signal(', 'get_values(',
                           'dump_hier(', 'submit(']
    for i in range(total):
        traj = eval_dataset.samples[i]
        conv = traj['conversation']
        prompt_msgs = []
        for msg in conv:
            if msg['role'] == 'assistant':
                break
            prompt_msgs.append(msg)
        if not prompt_msgs:
            continue
        prompt_parts = []
        for msg in prompt_msgs:
            if msg['role'] == 'tool':
                wrapped = (f"{TOOL_WRAPPER_OPEN}\n{msg['content']}\n"
                           f"{TOOL_WRAPPER_CLOSE}")
                prompt_parts.append(format_turn(ROLE_USER, wrapped))
            else:
                prompt_parts.append(format_turn(msg['role'], msg['content']))
        prompt_text = "".join(prompt_parts)
        prompt_text += f"{IM_START}{ROLE_ASSISTANT}\n"
        enc = tokenizer(prompt_text, add_special_tokens=False,
                        return_tensors='pt', truncation=True, max_length=1800)
        input_ids = enc['input_ids'].to(device)
        with torch.no_grad():
            out = llm.generate(
                input_ids, max_new_tokens=256, do_sample=False,
                temperature=1.0, pad_token_id=tokenizer.pad_token_id or 0,
                eos_token_id=tokenizer.eos_token_id)
        response = tokenizer.decode(out[0][input_ids.shape[1]:],
                                    skip_special_tokens=True).strip()
        if any(p in response for p in valid_tool_patterns):
            format_ok += 1
        if 'submit(' in response and re.search(r'submit\s*\([^)]*\d', response):
            submit_ok += 1
    llm.train()
    fmt_rate = format_ok / total if total > 0 else 0.0
    sub_rate = submit_ok / total if total > 0 else 0.0
    return fmt_rate, sub_rate, total


# ---------------------------------------------------------------------------
# Main training loop
# ---------------------------------------------------------------------------
def main():
    args = parse_args()
    rank, world, local = setup_ddp()
    device = torch.device(f'cuda:{local}')
    dtype = torch.bfloat16
    os.makedirs(args.output_dir, exist_ok=True)

    # ---- tokenizer ----
    print0(f"Loading tokenizer from {args.model_path}")
    tokenizer = AutoTokenizer.from_pretrained(
        args.model_path, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # ---- data: split into train / eval holdout ----
    random.seed(args.seed)
    with open(args.data_file, 'r') as f:
        total_lines = sum(1 for line in f if line.strip())
    all_indices = set(range(total_lines))
    holdout_indices = set(random.sample(
        range(total_lines), min(args.eval_holdout, total_lines // 10)))
    train_indices = all_indices - holdout_indices

    train_ds = WaveSFTDataset(
        args.data_file, tokenizer, seq_len=args.seq_len, indices=train_indices)
    eval_ds = WaveSFTDataset(
        args.data_file, tokenizer, seq_len=args.seq_len, indices=holdout_indices)
    print0(f"Train: {len(train_ds)} | Eval holdout: {len(eval_ds)}")

    sampler = DistributedSampler(
        train_ds, num_replicas=world, rank=rank, shuffle=True,
        seed=args.seed) if world > 1 else None
    loader = DataLoader(
        train_ds, batch_size=args.mbs, sampler=sampler,
        shuffle=(sampler is None), num_workers=args.num_workers,
        collate_fn=lambda b: collate_fn(b, tokenizer, args.seq_len),
        pin_memory=True, drop_last=True)

    # ---- model ----
    llm = build_model(args, device, dtype)
    llm.train()

    # ---- optimizer ----
    trainable = [p for p in llm.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(trainable, lr=args.lr, weight_decay=0.01,
                                  betas=(0.9, 0.999), eps=1e-8)

    accum_steps = max(1, args.gbs // (args.mbs * world))
    total_steps = args.nsteps
    print0(f"\n=== Stage-1W SFT Training ===")
    print0(f"  Model: {args.model_path}")
    print0(f"  Data: {len(train_ds)} train trajectories")
    print0(f"  LoRA: r={args.lora_r}, alpha={args.lora_alpha}, "
           f"dropout={args.lora_dropout}")
    print0(f"  LR: {args.lr} -> {args.min_lr} (cosine, warmup {args.warmup_frac})")
    print0(f"  Steps: {total_steps}, GBS={args.gbs}, MBS={args.mbs}, "
           f"accum={accum_steps}")
    print0(f"  Seq len: {args.seq_len}")
    print0(f"  Output: {args.output_dir}")
    print0(f"  World: {world} GPU(s)\n")

    step = 0
    epoch = 0
    t0 = time.time()
    log_loss = 0.0
    log_count = 0
    lr_now = args.lr

    while step < total_steps:
        if sampler is not None:
            sampler.set_epoch(epoch)
        for batch in loader:
            if step >= total_steps:
                break
            input_ids = batch['input_ids'].to(device, non_blocking=True)
            attention_mask = batch['attention_mask'].to(device, non_blocking=True)
            labels = batch['labels'].to(device, non_blocking=True)
            with torch.amp.autocast('cuda', dtype=dtype):
                outputs = llm(input_ids=input_ids,
                              attention_mask=attention_mask,
                              labels=labels)
                loss = outputs.loss / accum_steps
            loss.backward()
            log_loss += loss.item() * accum_steps
            log_count += 1
            if (step + 1) % accum_steps == 0:
                lr_now = get_lr(step, total_steps, args.lr, args.min_lr,
                                args.warmup_frac)
                for pg in optimizer.param_groups:
                    pg['lr'] = lr_now
                torch.nn.utils.clip_grad_norm_(trainable, 1.0)
                optimizer.step()
                optimizer.zero_grad()
            if (step + 1) % args.log_steps == 0 and is_main():
                avg_loss = log_loss / max(1, log_count)
                elapsed = time.time() - t0
                sps = (step + 1) / elapsed
                eta = (total_steps - step - 1) / max(0.1, sps)
                print0(f"  step {step+1}/{total_steps} | loss {avg_loss:.4f} | "
                       f"lr {lr_now:.2e} | {sps:.2f} step/s | "
                       f"ETA {eta/60:.1f} min")
                log_loss = 0.0
                log_count = 0
            if (step + 1) % args.save_steps == 0:
                save_checkpoint(llm, tokenizer, args.output_dir, step + 1, rank)
                if is_main():
                    fmt, sub, n = evaluate_format_and_submit(
                        llm, tokenizer, eval_ds, device, dtype, max_eval=30)
                    print0(f"  [Eval@step{step+1}] format={fmt:.1%} "
                           f"submit={sub:.1%} (n={n}) "
                           f"[target: fmt>=90%, submit>=70%]")
            step += 1
        epoch += 1

    # ---- final checkpoint + eval ----
    save_checkpoint(llm, tokenizer, args.output_dir, total_steps, rank)
    if is_main():
        fmt, sub, n = evaluate_format_and_submit(
            llm, tokenizer, eval_ds, device, dtype, max_eval=50)
        print0(f"\n=== Final Eval ===")
        print0(f"  Format correctness: {fmt:.1%} (target >=90%)")
        print0(f"  Submit success rate: {sub:.1%} (target >=70%)")
        print0(f"  Eval samples: {n}")
        eval_path = os.path.join(args.output_dir, "eval_results.json")
        with open(eval_path, 'w') as f:
            json.dump({
                "format_correctness": fmt,
                "submit_success_rate": sub,
                "eval_samples": n,
                "step": total_steps,
                "target_format": 0.90,
                "target_submit": 0.70,
                "pass": fmt >= 0.90 and sub >= 0.70,
            }, f, indent=2)
        print0(f"  Eval results saved to {eval_path}")
    print0(f"\n=== Training complete ({time.time()-t0:.1f}s) ===")
    cleanup()


if __name__ == '__main__':
    main()
