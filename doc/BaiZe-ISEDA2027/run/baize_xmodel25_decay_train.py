#!/usr/bin/env python3
"""
BaiZe 80B Decay Training — Xmodel-2.5 stable末ckpt + BaiZe配比 + Muon
======================================================================
用 Xmodel-2.5 stable 末 ckpt (step 532000) 做 80B token 的 WSD decay,
争取 14 评测集超越 Xmodel-2.5 final (CS8=65.40% / CX=32.90%).

技术路线（2026-10-16 定）：
  - 模型：transformers 加载 Xmodel-2.5 HF ckpt（trust_remote_code + flash_attention_2 + bf16）。
    ⚠️ 必须用 HF：Xmodel 的 μP 前向缩放（embed×12.0 / attn残差×1.4/√48 /
    ffn残差×1.4/√48 / logits×1/6）Megatron-Core 0.16.1 不实现，HF→Megatron 转换会破坏模型。
  - 优化器：megatron.core.optimizer.muon.TensorParallelMuon（NeMo/Megatron 自带，非手写）
    驱动 2D 线性参数；embed/1D/norm 参数走 torch.optim.AdamW。
  - 数据：复用 P-8 decay 配方 SFT 64 : L3 24 : code 8 : math 4，读取 Megatron IndexedDataset
    (.bin/.idx)。BaiZe tokenizer 与 Xmodel tokenizer 在 id 0..128814 完全一致（已实测）；
    仅需把 id>=128815（EOD 129280 + 少量 role marker）重映射到 Xmodel eos_token_id=2，
    并对 eos 位置 mask loss。
"""
import os, sys, math, time, random, argparse, shutil

import numpy as np
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP


def build_optimizers(muon_params, adamw_params, lr, weight_decay, momentum=0.95):
    """Megatron-Core 0.16.1 自带 Muon + AdamW。"""
    from megatron.core.optimizer.muon import TensorParallelMuon

    # Monkey-patch newton_schulz to accept BF16 gradients (convert to FP32 internally,
    # convert result back to original dtype so update step matches param dtype)
    import emerging_optimizers.orthogonalized_optimizers.muon_utils as _muon_utils
    if not getattr(_muon_utils, '_bf16_patched', False):
        _original_ns = _muon_utils.newton_schulz
        def _bf16_compat_ns(x, steps, coefficient_type, use_syrk=True):
            orig_dtype = x.dtype
            if orig_dtype != torch.float32:
                x = x.float()
            out = _original_ns(x, steps, coefficient_type, use_syrk=use_syrk)
            if orig_dtype != torch.float32:
                out = out.to(orig_dtype)
            return out
        _muon_utils.newton_schulz = _bf16_compat_ns
        _muon_utils._bf16_patched = True

    muon_opt = TensorParallelMuon(
        [{'params': muon_params}],
        lr=lr,
        momentum_beta=momentum,
        use_nesterov=True,
        weight_decay=weight_decay,
        use_decoupled_weight_decay=True,
        fp32_matmul_prec="medium",
        coefficient_type="quintic",
        num_ns_steps=5,
        scale_mode="spectral",
        extra_scale_factor=1.0,
        mode="duplicated",  # TP=1, 无 TP 分片
    )
    adamw_opt = torch.optim.AdamW(
        adamw_params, lr=lr, betas=(0.9, 0.95), eps=1e-8, weight_decay=weight_decay
    )
    return muon_opt, adamw_opt


class MegatronDatasetReader:
    """Read Megatron IndexedDataset .bin/.idx files, remap out-of-vocab tokens."""

    def __init__(self, prefix, remap_ge=128815, remap_to=2):
        from megatron.core.datasets.indexed_dataset import IndexedDataset

        self.ds = IndexedDataset(prefix)
        self.remap_ge = remap_ge
        self.remap_to = remap_to
        self.num_docs = len(self.ds)
        try:
            self.total_tokens = int(self.ds.index.sizes.sum())
        except Exception:
            self.total_tokens = self.num_docs * 512

    def get_doc(self, idx):
        doc = np.array(self.ds[idx], dtype=np.int64)
        doc[doc >= self.remap_ge] = self.remap_to
        return doc

    def __len__(self):
        return self.num_docs


class BlendedDataset:
    def __init__(self, sources, weights, seq_length, seed=1234, remap_ge=128815, remap_to=2):
        self.seq_length = seq_length
        self.remap_to = remap_to
        self.rng = random.Random(seed)
        total_w = sum(weights)
        self.weights = [w / total_w for w in weights]
        self.datasets = []
        for prefix, _ in sources:
            ds = MegatronDatasetReader(prefix, remap_ge=remap_ge, remap_to=remap_to)
            self.datasets.append(ds)
            print(f"  Loaded {prefix}: {ds.num_docs} docs, {ds.total_tokens / 1e9:.2f}B tokens")
        self.cum_weights = []
        cum = 0.0
        for w in self.weights:
            cum += w
            self.cum_weights.append(cum)

    def _sample_source(self):
        r = self.rng.random()
        for i, cw in enumerate(self.cum_weights):
            if r <= cw:
                return i
        return len(self.datasets) - 1

    def get_batch(self, batch_size):
        sequences = []
        for _ in range(batch_size):
            seq = []
            while len(seq) < self.seq_length:
                src_idx = self._sample_source()
                ds = self.datasets[src_idx]
                doc_idx = self.rng.randint(0, ds.num_docs - 1)
                doc = ds.get_doc(doc_idx)
                seq.extend(doc.tolist())
            sequences.append(seq[: self.seq_length])
        input_ids = torch.tensor(sequences, dtype=torch.long)
        return input_ids


class BlendedDataLoader:
    def __init__(self, sources, weights, seq_length, batch_size, seed=1234):
        self.dataset = BlendedDataset(sources, weights, seq_length, seed)
        self.batch_size = batch_size

    def __iter__(self):
        while True:
            yield self.dataset.get_batch(self.batch_size)


def wsd_lr_schedule(step, warmup_steps, decay_steps, peak_lr, min_lr):
    if step < warmup_steps:
        return peak_lr * step / max(1, warmup_steps)
    decay_step = step - warmup_steps
    if decay_step >= decay_steps:
        return min_lr
    # WSD 指数退火：到 decay_steps 末可降到 ~min_lr（exp(-5)≈0.0067）
    return min_lr + (peak_lr - min_lr) * math.exp(-5.0 * decay_step / decay_steps)


def setup_distributed():
    if 'RANK' in os.environ:
        rank = int(os.environ['RANK'])
        world_size = int(os.environ['WORLD_SIZE'])
        local_rank = int(os.environ.get('LOCAL_RANK', rank))
    else:
        rank = 0
        world_size = 1
        local_rank = int(os.environ.get('CUDA_VISIBLE_DEVICES', '0').split(',')[0])
    if world_size > 1:
        dist.init_process_group(backend='nccl')
    torch.cuda.set_device(local_rank)
    return rank, world_size, local_rank


def get_param_groups(model):
    muon_params, adamw_params = [], []
    for name, param in model.named_parameters():
        if not param.requires_grad:
            continue
        # embed / lm_head / norm / bias / 标量 → AdamW；其余 2D 线性 → Muon
        is_embed = ('embed' in name.lower() or 'lm_head' in name.lower()
                    or 'norm' in name.lower() or 'bias' in name.lower())
        if is_embed or param.ndim < 2:
            adamw_params.append(param)
        else:
            muon_params.append(param)
    return muon_params, adamw_params


def save_hf_checkpoint(model, tokenizer_dir, save_dir, rank):
    if rank != 0:
        return
    os.makedirs(save_dir, exist_ok=True)
    unwrapped = model.module if isinstance(model, DDP) else model
    unwrapped.save_pretrained(save_dir, safe_serialization=False)
    # 复制自定义建模代码 + tokenizer，保证 save_dir 可直接 from_pretrained
    for fname in os.listdir(tokenizer_dir):
        src = os.path.join(tokenizer_dir, fname)
        dst = os.path.join(save_dir, fname)
        if os.path.isfile(src) and not os.path.exists(dst):
            shutil.copy2(src, dst)
    print(f"  ✅ Checkpoint saved to {save_dir}", flush=True)


def main():
    parser = argparse.ArgumentParser(description="BaiZe 80B Decay — Xmodel-2.5")
    parser.add_argument('--model_path', type=str, required=True)
    parser.add_argument('--tokenizer_dir', type=str, default=None)
    parser.add_argument('--data_dir', type=str, required=True)
    parser.add_argument('--output_dir', type=str, required=True)
    parser.add_argument('--seq_length', type=int, default=3712)
    parser.add_argument('--global_batch_size', type=int, default=960)
    parser.add_argument('--micro_batch_size', type=int, default=2)
    parser.add_argument('--total_steps', type=int, default=22472)
    parser.add_argument('--warmup_steps', type=int, default=100)
    parser.add_argument('--lr', type=float, default=1.67e-3)
    parser.add_argument('--min_lr', type=float, default=1e-5)
    parser.add_argument('--weight_decay', type=float, default=0.01)
    parser.add_argument('--momentum', type=float, default=0.95)
    parser.add_argument('--save_interval', type=int, default=2000)
    parser.add_argument('--log_interval', type=int, default=10)
    parser.add_argument('--smoke_test', action='store_true')
    parser.add_argument('--grad_checkpoint', action='store_true', default=True)
    parser.add_argument('--eos_id', type=int, default=2)  # Xmodel-2.5 eos_token_id=2
    parser.add_argument('--seed', type=int, default=1234)
    args = parser.parse_args()

    if args.tokenizer_dir is None:
        args.tokenizer_dir = args.model_path
    decay_steps = args.total_steps - args.warmup_steps

    rank, world_size, local_rank = setup_distributed()
    device = torch.device(f'cuda:{local_rank}')

    if rank == 0:
        print("=" * 80, flush=True)
        print("BaiZe 80B Decay — Xmodel-2.5 stable末ckpt + Megatron Muon", flush=True)
        print("=" * 80, flush=True)
        print(f"  Model: {args.model_path}", flush=True)
        print(f"  seq={args.seq_length} GBS={args.global_batch_size} MBS={args.micro_batch_size} DP={world_size}",
              flush=True)
        print(f"  Steps: {args.total_steps} (warmup={args.warmup_steps} decay={decay_steps})", flush=True)
        print(f"  LR: {args.lr}→{args.min_lr} | Optimizer: Megatron Muon(2D)+AdamW(embed/1D)", flush=True)
        if args.smoke_test:
            print("  🧪 SMOKE TEST MODE (100 steps)", flush=True)

    # ---------------- 加载 Xmodel-2.5（HF 路线，μP 前向精确） ----------------
    from transformers import AutoModelForCausalLM
    model = AutoModelForCausalLM.from_pretrained(
        args.model_path,
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
        attn_implementation='flash_attention_2',
    )
    model = model.to(device)
    if args.grad_checkpoint:
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant': False})
        model.config.use_cache = False
        model.enable_input_require_grads()
    if world_size > 1:
        model = DDP(model, device_ids=[local_rank], find_unused_parameters=False)

    muon_params, adamw_params = get_param_groups(
        model.module if isinstance(model, DDP) else model
    )
    if rank == 0:
        print(f"  Muon: {sum(p.numel() for p in muon_params)/1e6:.1f}M | "
              f"AdamW: {sum(p.numel() for p in adamw_params)/1e6:.1f}M", flush=True)

    muon_opt, adamw_opt = build_optimizers(
        muon_params, adamw_params, lr=args.lr, weight_decay=args.weight_decay,
        momentum=args.momentum,
    )

    # ---------------- 数据 blend：SFT 64 : L3 24 : code 8 : math 4 ----------------
    DATA = args.data_dir
    sources, weights = [], []
    for s in range(4):
        sources.append((f"{DATA}/mix_sft_tok/mix_sft_train_s{s}", f"sft_s{s}"))
        weights.append(8.0)
    for s in range(4):
        sources.append((f"{DATA}/mix_sft_agent_tok/mix_sft_agent_train_s{s}", f"sft_ag_s{s}"))
        weights.append(8.0)
    for s in range(8):
        sources.append((f"{DATA}/p5b_l3/p5b_l3_train_s{s}", f"l3_s{s}"))
        weights.append(3.0)
    sources.append((f"{DATA}/anneal_code", "anneal_code"))
    weights.append(3.0)
    sources.append((f"{DATA}/r3_sources/r3_ultradata_code", "r3_code"))
    weights.append(5.0)
    sources.append((f"{DATA}/anneal_math2", "anneal_math2"))
    weights.append(3.0)
    sources.append((f"{DATA}/r3_sources/r3_ultradata_math", "r3_math"))
    weights.append(1.0)

    if rank == 0:
        tw = sum(weights)
        print(f"\n📊 Blend: SFT={sum(weights[:8])/tw*100:.0f}% "
              f"L3={sum(weights[8:16])/tw*100:.0f}% Code={sum(weights[16:18])/tw*100:.0f}% "
              f"Math={sum(weights[18:20])/tw*100:.0f}%", flush=True)

    dataloader = BlendedDataLoader(sources, weights, args.seq_length,
                                   args.micro_batch_size, args.seed + rank)

    grad_accum = args.global_batch_size // (args.micro_batch_size * world_size)
    total_steps = 100 if args.smoke_test else args.total_steps
    os.makedirs(args.output_dir, exist_ok=True)
    log_file = os.path.join(args.output_dir, 'train_log.txt')

    if rank == 0:
        print(f"\n🚀 Training: {total_steps} steps, grad_accum={grad_accum}, "
              f"{args.global_batch_size * args.seq_length / 1e6:.2f}M tok/step", flush=True)

    data_iter = iter(dataloader)
    start_time = time.time()

    for step in range(total_steps):
        lr = wsd_lr_schedule(step, args.warmup_steps, decay_steps, args.lr, args.min_lr)
        for pg in muon_opt.param_groups:
            pg['lr'] = lr
        for pg in adamw_opt.param_groups:
            pg['lr'] = lr

        total_loss = 0.0
        muon_opt.zero_grad()
        adamw_opt.zero_grad()
        for _ in range(grad_accum):
            # 取 batch → 因果切分 + mask eos 位置（label=eos 不参与 loss）
            full = next(data_iter).to(device)
            input_ids = full[:, :-1].contiguous()
            labels = full[:, 1:].contiguous()
            labels = labels.masked_fill(labels == args.eos_id, -100)
            outputs = model(input_ids=input_ids, labels=labels)
            loss = outputs.loss / grad_accum
            loss.backward()
            total_loss += loss.item() * grad_accum

        all_params = [p for pg in muon_opt.param_groups for p in pg['params']] + \
                     [p for pg in adamw_opt.param_groups for p in pg['params']]
        torch.nn.utils.clip_grad_norm_(all_params, max_norm=1.0)

        muon_opt.step()
        adamw_opt.step()

        if rank == 0 and (step % args.log_interval == 0 or step < 5 or step == total_steps - 1):
            elapsed = time.time() - start_time
            tok_per_sec = (step + 1) * args.global_batch_size * args.seq_length / max(1, elapsed)
            avg_loss = total_loss / grad_accum
            msg = (f"[step {step:5d}/{total_steps}] loss={avg_loss:.4f} lr={lr:.2e} "
                   f"tok/s={tok_per_sec/1e3:.1f}K elapsed={elapsed/60:.1f}min")
            print(msg, flush=True)
            with open(log_file, 'a') as f:
                f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")

        if rank == 0 and step > 0 and (step + 1) % args.save_interval == 0:
            save_hf_checkpoint(model, args.tokenizer_dir,
                               os.path.join(args.output_dir, f'step_{step + 1}'), rank)

    if rank == 0:
        save_hf_checkpoint(model, args.tokenizer_dir,
                           os.path.join(args.output_dir, 'final'), rank)
        print(f"\n✅ Done! {total_steps} steps in {(time.time()-start_time)/3600:.2f}h", flush=True)
    if world_size > 1:
        dist.barrier()
        dist.destroy_process_group()


if __name__ == '__main__':
    main()