#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
baize_posttrain_sft_surrogate.py - Phase 2: MiniCPM5-2B surrogate SFT training.
Uses HuggingFace transformers Trainer (no TRL dependency) to full-fine-tune
MiniCPM5-2B on the PyAether SFT corpus (prompt/completion JSONL).
⚠️ SURROGATE experiment - gains NOT transferable to BaiZe.
"""
import argparse, json, os, sys, logging
from pathlib import Path
import torch
from torch.utils.data import Dataset
from transformers import (
    AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments, set_seed,
)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class SFTDataset(Dataset):
    """JSONL with 'prompt'/'completion' -> ChatML, loss masked on prompt only."""
    def __init__(self, data_path, tokenizer, max_len=2048, quality_filter=None, max_samples=None):
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.examples = []
        with open(data_path, "r", encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line.strip())
                if quality_filter and rec.get("quality_tier") not in quality_filter:
                    continue
                self.examples.append(rec)
        if max_samples:
            self.examples = self.examples[:max_samples]
        logger.info("Loaded %d examples (filter=%s)", len(self.examples), quality_filter)

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        rec = self.examples[idx]
        prompt_text = (
            "<|im_start|>system\nYou are an EDA automation assistant skilled in pyAether APIs.<|im_end|>\n"
            "<|im_start|>user\n" + rec["prompt"] + "<|im_end|>\n"
            "<|im_start|>assistant\n"
        )
        response_text = rec["completion"] + "<|im_end|>"
        prompt_ids = self.tokenizer.encode(prompt_text, add_special_tokens=False)
        response_ids = self.tokenizer.encode(response_text, add_special_tokens=False)
        input_ids = [self.tokenizer.bos_token_id] + prompt_ids + response_ids
        labels = [-100] * (1 + len(prompt_ids)) + response_ids
        if len(input_ids) > self.max_len:
            overflow = len(input_ids) - self.max_len
            input_ids = input_ids[overflow:]
            labels = labels[overflow:]
        pad_len = self.max_len - len(input_ids)
        pad_id = self.tokenizer.pad_token_id
        input_ids = input_ids + [pad_id] * pad_len
        labels = labels + [-100] * pad_len
        attention_mask = [1] * (self.max_len - pad_len) + [0] * pad_len
        return {
            "input_ids": torch.tensor(input_ids, dtype=torch.long),
            "labels": torch.tensor(labels, dtype=torch.long),
            "attention_mask": torch.tensor(attention_mask, dtype=torch.long),
        }


def main():
    parser = argparse.ArgumentParser(description="MiniCPM5-2B surrogate SFT")
    parser.add_argument("--model_path", type=str, default="/nas_data/app.e0031982/models/MiniCPM5-2B")
    parser.add_argument("--data_path", type=str, required=True)
    parser.add_argument("--output_dir", type=str, default="/tmp/sft_surrogate_out")
    parser.add_argument("--max_len", type=int, default=2048)
    parser.add_argument("--per_device_batch_size", type=int, default=1)
    parser.add_argument("--grad_accum", type=int, default=16)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--warmup_steps", type=int, default=50)
    parser.add_argument("--num_epochs", type=float, default=3.0)
    parser.add_argument("--save_steps", type=int, default=500)
    parser.add_argument("--logging_steps", type=int, default=10)
    parser.add_argument("--quality_filter", type=str, default="high,medium")
    parser.add_argument("--max_samples", type=int, default=None)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    set_seed(args.seed)
    if args.smoke:
        args.max_samples = 20
        args.num_epochs = 1.0
        args.warmup_steps = 1
        args.save_steps = 9999
        args.logging_steps = 1
        args.grad_accum = 1
        args.output_dir = args.output_dir + "_smoke"
        logger.info("SMOKE TEST MODE")
    logger.info("=" * 60)
    logger.info("Phase 2: MiniCPM5-2B SURROGATE SFT")
    logger.info("  model=%s data=%s out=%s", args.model_path, args.data_path, args.output_dir)
    logger.info("  max_len=%d batch=%dx%d lr=%s epochs=%s", args.max_len, args.per_device_batch_size, args.grad_accum, args.lr, args.num_epochs)
    logger.info("  GPUs=%s  SURROGATE: gains NOT transferable to BaiZe", os.environ.get("CUDA_VISIBLE_DEVICES", "all"))
    logger.info("=" * 60)
    logger.info("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    logger.info("Loading model (bf16)...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model_path, torch_dtype=torch.bfloat16, trust_remote_code=True,
        attn_implementation="eager",
    )
    model.config.use_cache = False
    if hasattr(model, "gradient_checkpointing_enable"):
        model.gradient_checkpointing_enable()
    n_params = sum(p.numel() for p in model.parameters())
    logger.info("Model: %.2fB params", n_params / 1e9)
    quality_filter = set(args.quality_filter.split(",")) if args.quality_filter != "all" else None
    dataset = SFTDataset(args.data_path, tokenizer, max_len=args.max_len, quality_filter=quality_filter, max_samples=args.max_samples)
    training_args = TrainingArguments(
        output_dir=args.output_dir, num_train_epochs=args.num_epochs,
        per_device_train_batch_size=args.per_device_batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr, warmup_steps=args.warmup_steps,
        lr_scheduler_type="cosine", logging_steps=args.logging_steps,
        save_steps=args.save_steps, save_total_limit=3, bf16=True,
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        report_to="none", seed=args.seed, dataloader_num_workers=2,
        remove_unused_columns=False, optim="adamw_torch",
        max_grad_norm=1.0, weight_decay=0.01,
    )
    trainer = Trainer(model=model, args=training_args, train_dataset=dataset, tokenizer=tokenizer)
    logger.info("Starting training...")
    train_result = trainer.train()
    if not args.smoke:
        trainer.save_model(args.output_dir)
        tokenizer.save_pretrained(args.output_dir)
        trainer.log_metrics("train", train_result.metrics)
        trainer.save_metrics("train", train_result.metrics)
        trainer.save_state()
        logger.info("Model saved to %s", args.output_dir)
    logger.info("=" * 60)
    logger.info("SFT done: steps=%d loss=%.4f", train_result.global_step, train_result.training_loss)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
