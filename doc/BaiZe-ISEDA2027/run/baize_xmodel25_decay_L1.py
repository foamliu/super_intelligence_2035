#!/usr/bin/env python3
"""
BaiZe 80B Decay Training v2 — profiling + speed improvements
=============================================================
v2 changes vs v1 (baize_xmodel25_decay_train.py):
  1. Segmented timing: t_data / t_fwd_bwd / t_opt per step (printed every 5 steps)
  2. --profile_steps N: run only N steps then exit (for profiling)
  3. --fast_data: use torch.utils.data.DataLoader(num_workers=8, pin_memory=True,
     prefetch_factor=4, persistent_workers=True) + np.concatenate + non_blocking H2D
  4. --grad_checkpoint default changed to False (was True in v1)
  5. --adamw_fused: use fused AdamW (torch.optim.AdamW(fused=True))
Everything else (model loading, Muon optimizer, data blend, WSD schedule, checkpoint
saving) is identical to v1 — recipe-neutral, no change to training semantics.
"""
import os, sys, math, time, random, argparse, shutil
from contextlib import nullcontext as _null_ctx

import numpy as np
import torch
import torch.nn.functional as F
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP


def build_optimizers(muon_params, adamw_params, lr, weight_decay, momentum=0.95,
                     adamw_fused=False):
    """Megatron-Core 0.16.1 Muon + AdamW."""
    from megatron.core.optimizer.muon import TensorParallelMuon

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

    # --- Fix: emerging_optimizers 0.5.0a0 renamed 'mode' → 'tp_mode' in
    # newton_schulz_tp(), but Megatron's muon.py still passes 'mode'.
    # Patch: wrap newton_schulz_tp to accept 'mode' as alias for 'tp_mode'.
    # Also patch in megatron.core.optimizer.muon namespace (imported at module level).
    if not getattr(_muon_utils, '_tp_mode_patched', False):
        _orig_ns_tp = _muon_utils.newton_schulz_tp

        def _mode_compat_ns_tp(x, steps, coefficient_type, tp_group,
                               partition_dim=None, mode='duplicated', **kwargs):
            return _orig_ns_tp(x, steps, coefficient_type, tp_group,
                               partition_dim=partition_dim, tp_mode=mode, **kwargs)

        _muon_utils.newton_schulz_tp = _mode_compat_ns_tp
        _muon_utils._tp_mode_patched = True
        import megatron.core.optimizer.muon as _muon_mod
        _muon_mod.newton_schulz_tp = _mode_compat_ns_tp

    # --- Fix: emerging_optimizers 0.5.0a0 (installed at /tmp/Emerging-Optimizers/
    # on .12) made 'nesterov' a required keyword-only arg in
    # OrthogonalizedOptimizer.__init__, but Megatron's TensorParallelMuon passes
    # 'use_nesterov' (→ **kwargs) instead.  On .29 the package isn't installed
    # (OrthogonalizedOptimizer=object fallback, no issue).
    # Patch: make nesterov default to True, extract from use_nesterov if present.
    try:
        from emerging_optimizers.orthogonalized_optimizers import (
            OrthogonalizedOptimizer as _OrthoOpt,
        )
        if _OrthoOpt is not object and not getattr(_OrthoOpt, '_nesterov_patched', False):
            _orig_ortho_init = _OrthoOpt.__init__

            def _nesterov_compat_init(self, *args, nesterov=True, **kwargs):
                if 'use_nesterov' in kwargs:
                    nesterov = kwargs.pop('use_nesterov')
                return _orig_ortho_init(self, *args, nesterov=nesterov, **kwargs)

            _OrthoOpt.__init__ = _nesterov_compat_init
            _OrthoOpt._nesterov_patched = True
    except ImportError:
        pass

    muon_opt = TensorParallelMuon(
        [{'params': muon_params}],
        lr=lr, momentum_beta=momentum, use_nesterov=True,
        weight_decay=weight_decay, use_decoupled_weight_decay=True,
        fp32_matmul_prec="medium", coefficient_type="quintic",
        num_ns_steps=5, scale_mode="spectral",
        extra_scale_factor=1.0, mode="duplicated",
    )
    adamw_opt = torch.optim.AdamW(
        adamw_params, lr=lr, betas=(0.9, 0.95), eps=1e-8,
        weight_decay=weight_decay, fused=adamw_fused,
    )
    return muon_opt, adamw_opt


class MegatronDatasetReader:
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
        """Original slow batch: .tolist() + list.extend."""
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
        return torch.tensor(sequences, dtype=torch.long)

    def get_sequence_np(self):
        """Single sequence via np.concatenate (fast)."""
        chunks = []
        total_len = 0
        while total_len < self.seq_length:
            src_idx = self._sample_source()
            ds = self.datasets[src_idx]
            doc_idx = self.rng.randint(0, ds.num_docs - 1)
            doc = ds.get_doc(doc_idx)
            chunks.append(doc)
            total_len += len(doc)
        return np.concatenate(chunks)[:self.seq_length]

    def get_batch_fast(self, batch_size):
        """Fast batch: np.concatenate + torch.from_numpy."""
        sequences = [self.get_sequence_np() for _ in range(batch_size)]
        return torch.from_numpy(np.stack(sequences).astype(np.int64))

    def __len__(self):
        return 10_000_000

    def __getitem__(self, idx):
        return torch.from_numpy(self.get_sequence_np().astype(np.int64))


class BlendedDataLoader:
    """Original single-process dataloader."""
    def __init__(self, sources, weights, seq_length, batch_size, seed=1234, fast=False):
        self.dataset = BlendedDataset(sources, weights, seq_length, seed)
        self.batch_size = batch_size
        self.fast = fast

    def __iter__(self):
        if self.fast:
            while True:
                yield self.dataset.get_batch_fast(self.batch_size)
        else:
            while True:
                yield self.dataset.get_batch(self.batch_size)


class WorkerDataLoader:
    """torch.utils.data.DataLoader with workers, pin_memory, prefetch."""
    def __init__(self, sources, weights, seq_length, batch_size, seed=1234, num_workers=8):
        self.dataset = BlendedDataset(sources, weights, seq_length, seed)
        self.dataloader = torch.utils.data.DataLoader(
            self.dataset, batch_size=batch_size, shuffle=False,
            num_workers=num_workers, pin_memory=True, prefetch_factor=4,
            persistent_workers=True, worker_init_fn=self._worker_init,
        )

    @staticmethod
    def _worker_init(worker_id):
        worker_info = torch.utils.data.get_worker_info()
        if worker_info is not None:
            worker_info.dataset.rng = random.Random(worker_info.seed % (2**32))

    def __iter__(self):
        return iter(self.dataloader)


def wsd_lr_schedule(step, warmup_steps, decay_steps, peak_lr, min_lr):
    if step < warmup_steps:
        return peak_lr * step / max(1, warmup_steps)
    decay_step = step - warmup_steps
    if decay_step >= decay_steps:
        return min_lr
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
    m = model.module if isinstance(model, DDP) else model
    # Unwrap torch.compile() wrapper on the outer model (OptimizedModule has _orig_mod)
    if hasattr(m, '_orig_mod'):
        m = m._orig_mod
    # Handle inner compiled submodules: when --chunked_ce is used, only
    # m.model (the transformer body) is compiled via torch.compile().
    # accelerate's extract_model_from_parallel() has a bug: has_compiled_regions()
    # returns True but it does model.__dict__["_orig_mod"] on the OUTER model,
    # which doesn't have that key → KeyError.  Fix: temporarily swap compiled
    # children with their _orig_mod before calling save_pretrained, then restore.
    _swapped = {}
    for name, child in m.named_children():
        if hasattr(child, '_orig_mod'):
            _swapped[name] = child
            setattr(m, name, child._orig_mod)
    try:
        m.save_pretrained(save_dir, safe_serialization=True)
    finally:
        for name, child in _swapped.items():
            setattr(m, name, child)
    for fn in os.listdir(tokenizer_dir):
        if fn.endswith(('.json', '.txt', '.model', '.py', '.pyc')) or 'token' in fn.lower():
            src = os.path.join(tokenizer_dir, fn)
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(save_dir, fn))
    print(f"  Saved checkpoint to {save_dir}", flush=True)


def chunked_cross_entropy(hidden, lm_head, labels, chunk_size=256, logit_scale=1.0):
    """Compute cross-entropy in seq-dimension chunks to avoid materializing full [B,S,V] logits.

    Numerically equivalent to F.cross_entropy(logits, labels, ignore_index=-100, reduction='mean')
    where logits = lm_head(hidden) * logit_scale.

    logit_scale replicates the μP output scaling applied inside the HF model's forward
    (logits *= mup_output_scale / mup_width_multiplier).  Must be passed by the caller
    because chunked CE calls lm_head directly, bypassing the HF forward.

    Uses reduction='sum' per chunk, accumulates, then divides by total valid token count
    (per operator instruction: avoid mean-then-average denominator bias).
    """
    W = lm_head.weight  # [V, H]
    bias = getattr(lm_head, 'bias', None)
    seq_len = hidden.shape[1]
    total_loss = torch.zeros((), device=hidden.device, dtype=torch.float32)
    total_valid = torch.zeros((), device=hidden.device, dtype=torch.long)
    for s in range(0, seq_len, chunk_size):
        e = min(s + chunk_size, seq_len)
        h = hidden[:, s:e]               # [B, chunk, H]
        l = labels[:, s:e]               # [B, chunk]
        if bias is not None:
            lg = F.linear(h, W, bias)    # [B, chunk, V]
        else:
            lg = F.linear(h, W)          # [B, chunk, V]
        if logit_scale != 1.0:
            lg = lg * logit_scale
        loss_chunk = F.cross_entropy(
            lg.float().reshape(-1, lg.size(-1)),  # [B*chunk, V]
            l.reshape(-1),                         # [B*chunk]
            ignore_index=-100, reduction='sum')
        valid_chunk = (l != -100).sum()
        total_loss = total_loss + loss_chunk
        total_valid = total_valid + valid_chunk
    return total_loss / total_valid.clamp(min=1)


def main():
    parser = argparse.ArgumentParser()
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
    parser.add_argument('--grad_checkpoint', action='store_true', default=False)
    parser.add_argument('--fast_data', action='store_true', default=False)
    parser.add_argument('--adamw_fused', action='store_true', default=False)
    parser.add_argument('--profile_steps', type=int, default=0)
    parser.add_argument('--num_workers', type=int, default=8)
    parser.add_argument('--eos_id', type=int, default=2)
    parser.add_argument('--seed', type=int, default=1234)
    # v2 perf optimizations
    parser.add_argument('--compile_model', action='store_true', default=False,
                        help='Use torch.compile() on the model (kernel fusion + CUDA graphs)')
    parser.add_argument('--compile_mode', type=str, default='reduce-overhead',
                        choices=['reduce-overhead', 'default'],
                        help='torch.compile mode: reduce-overhead (CUDA graphs) or default (kernel fusion only)')
    parser.add_argument('--no_ddp_no_sync', action='store_true', default=False,
                        help='Disable DDP no_sync() for grad accumulation (for A/B testing)')
    parser.add_argument('--no_ddp_static_graph', action='store_true', default=False,
                        help='Disable DDP static_graph (for A/B testing)')
    parser.add_argument('--chunked_ce', action='store_true', default=False,
                        help='Use chunked cross-entropy to avoid materializing full logits [B,S,V]')
    parser.add_argument('--ce_chunk_size', type=int, default=256,
                        help='Chunk size (in seq dimension) for chunked CE')
    parser.add_argument('--resume', type=str, default=None,
                        help='Path to a HF checkpoint directory to resume from '
                             '(loads weights + sets start_step from dir name e.g. step_2000)')
    parser.add_argument('--verify_save_step', type=int, default=0,
                        help='If >0, save a test checkpoint at this step to verify '
                             'save_pretrained works with torch.compile, then continue training')
    args = parser.parse_args()

    if args.tokenizer_dir is None:
        args.tokenizer_dir = args.model_path
    decay_steps = args.total_steps - args.warmup_steps

    rank, world_size, local_rank = setup_distributed()
    device = torch.device(f'cuda:{local_rank}')

    if rank == 0:
        print("=" * 80, flush=True)
        print("BaiZe 80B Decay v2 — Xmodel-2.5 + Megatron Muon + profiling", flush=True)
        print("=" * 80, flush=True)
        print(f"  seq={args.seq_length} GBS={args.global_batch_size} MBS={args.micro_batch_size} DP={world_size}", flush=True)
        print(f"  Steps: {args.total_steps} (warmup={args.warmup_steps} decay={decay_steps})", flush=True)
        print(f"  v2: gc={args.grad_checkpoint} fast_data={args.fast_data} fused={args.adamw_fused} profile={args.profile_steps}", flush=True)

    # Resume support: if --resume is given, load from that checkpoint instead
    # of the original model_path.  Extract start_step from the directory name
    # (e.g. .../step_2000 → 2000) so the LR schedule and step counter continue
    # from the right point.  Optimizer state is NOT restored (Muon/AdamW restart
    # from scratch — minor transient, acceptable for decay-phase resume).
    start_step = 0
    load_path = args.resume if args.resume else args.model_path
    if args.resume:
        resume_dir_name = os.path.basename(args.resume.rstrip('/'))
        if resume_dir_name.startswith('step_'):
            start_step = int(resume_dir_name.split('_')[1])
        if rank == 0:
            print(f"  RESUME: loading from {args.resume}, start_step={start_step}", flush=True)

    from transformers import AutoModelForCausalLM
    model = AutoModelForCausalLM.from_pretrained(
        load_path, torch_dtype=torch.bfloat16,
        trust_remote_code=True, attn_implementation='flash_attention_2',
    )
    model = model.to(device)
    # Store raw model reference for chunked CE (before compile/DDP wrapping).
    # chunked CE calls raw_model.model(input_ids) + raw_model.lm_head directly,
    # bypassing compile/DDP forward — DDP gradient hooks still fire on backward.
    raw_model = model
    if args.chunked_ce:
        # Ensure use_cache=False for chunked CE path (base model called directly)
        raw_model.config.use_cache = False
        if hasattr(raw_model, 'model') and hasattr(raw_model.model, 'config'):
            raw_model.model.config.use_cache = False
        # μP logit scale: HF forward applies logits *= mup_output_scale / mup_width_multiplier
        # Chunked CE bypasses HF forward, so we must replicate this scaling.
        if getattr(raw_model.config, 'use_mup', False):
            mup_scale = raw_model.config.mup_output_scale / raw_model.config.mup_width_multiplier
        else:
            mup_scale = 1.0
        if rank == 0:
            print(f"  chunked_ce: ENABLED (chunk_size={args.ce_chunk_size}, mup_scale={mup_scale:.6f})", flush=True)
    if args.grad_checkpoint:
        if rank == 0:
            print("  gradient_checkpointing: ENABLED", flush=True)
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant': False})
        model.config.use_cache = False
        model.enable_input_require_grads()
    else:
        if rank == 0:
            print("  gradient_checkpointing: DISABLED (v2 default)", flush=True)

    if args.compile_model and not args.chunked_ce:
        if rank == 0:
            print(f"  torch.compile: ENABLED (mode={args.compile_mode})", flush=True)
        model = torch.compile(model, mode=args.compile_mode)
    elif args.compile_model and args.chunked_ce:
        # Compile just the base model (transformer layers) for chunked CE path.
        # The base model is called once with full seq; chunked CE loops over
        # the output hidden states in Python — no dynamic control flow inside compile.
        if rank == 0:
            print(f"  torch.compile(base_model): ENABLED (mode={args.compile_mode})", flush=True)
        raw_model.model = torch.compile(raw_model.model, mode=args.compile_mode)

    if world_size > 1:
        ddp_kwargs = dict(device_ids=[local_rank], find_unused_parameters=False)
        # static_graph=True is incompatible with no_sync() (causes expect_autograd_hooks_ assert)
        # Only enable static_graph when no_sync is disabled
        if not args.no_ddp_static_graph and args.no_ddp_no_sync:
            ddp_kwargs['static_graph'] = True
            if rank == 0:
                print("  DDP: static_graph=True (no_sync disabled)", flush=True)
        ddp_kwargs['gradient_as_bucket_view'] = True
        model = DDP(model, **ddp_kwargs)

    muon_params, adamw_params = get_param_groups(
        model.module if isinstance(model, DDP) else model)
    if rank == 0:
        print(f"  Muon: {sum(p.numel() for p in muon_params)/1e6:.1f}M | AdamW: {sum(p.numel() for p in adamw_params)/1e6:.1f}M", flush=True)

    muon_opt, adamw_opt = build_optimizers(
        muon_params, adamw_params, lr=args.lr, weight_decay=args.weight_decay,
        momentum=args.momentum, adamw_fused=args.adamw_fused)

    DATA = args.data_dir
    sources, weights = [], []
    for s in range(4):
        sources.append((f"{DATA}/mix_sft_tok/mix_sft_train_s{s}", f"sft_s{s}"))
        weights.append(10.0)
    for s in range(4):
        sources.append((f"{DATA}/mix_sft_agent_tok/mix_sft_agent_train_s{s}", f"sft_agent_s{s}"))
        weights.append(6.0)
    for s in range(8):
        sources.append((f"{DATA}/p5b_l3/p5b_l3_train_s{s}", f"l3_s{s}"))
        weights.append(3.0)
    sources.append((f"{DATA}/anneal_code", "anneal_code"))
    weights.append(5.0)
    sources.append((f"{DATA}/r3_sources/r3_ultradata_code", "r3_code"))
    weights.append(5.0)
    sources.append((f"{DATA}/anneal_math2", "anneal_math2"))
    weights.append(3.0)
    sources.append((f"{DATA}/r3_sources/r3_ultradata_math", "r3_math"))
    weights.append(1.0)

    if rank == 0:
        tw = sum(weights)
        print(f"\n  Blend: SFT={sum(weights[:8])/tw*100:.0f}% L3={sum(weights[8:16])/tw*100:.0f}% Code={sum(weights[16:18])/tw*100:.0f}% Math={sum(weights[18:20])/tw*100:.0f}%", flush=True)

    if args.fast_data and world_size > 1:
        dataloader = WorkerDataLoader(sources, weights, args.seq_length,
                                       args.micro_batch_size, args.seed + rank,
                                       num_workers=args.num_workers)
    else:
        dataloader = BlendedDataLoader(sources, weights, args.seq_length,
                                       args.micro_batch_size, args.seed + rank,
                                       fast=args.fast_data)

    grad_accum = args.global_batch_size // (args.micro_batch_size * world_size)

    if args.profile_steps > 0:
        total_steps = args.profile_steps
    elif args.smoke_test:
        total_steps = 100
    else:
        total_steps = args.total_steps

    os.makedirs(args.output_dir, exist_ok=True)
    log_file = os.path.join(args.output_dir, 'train_log.txt')
    timing_file = os.path.join(args.output_dir, 'timing_log.txt')

    if rank == 0:
        print(f"\n  Training: {total_steps} steps, grad_accum={grad_accum}, {args.global_batch_size * args.seq_length / 1e6:.2f}M tok/step", flush=True)

    data_iter = iter(dataloader)
    start_time = time.time()

    t_data_acc = 0.0
    t_fwd_bwd_acc = 0.0
    t_opt_acc = 0.0
    timing_step_count = 0

    for step in range(start_step, total_steps):
        lr = wsd_lr_schedule(step, args.warmup_steps, decay_steps, args.lr, args.min_lr)
        for pg in muon_opt.param_groups:
            pg['lr'] = lr
        for pg in adamw_opt.param_groups:
            pg['lr'] = lr

        total_loss = 0.0
        torch.cuda.synchronize()
        t_zg0 = time.time()
        muon_opt.zero_grad()
        adamw_opt.zero_grad()
        torch.cuda.synchronize()
        t_zg = time.time() - t_zg0

        for micro_idx in range(grad_accum):
            t_d0 = time.time()
            if args.fast_data:
                full = next(data_iter).to(device, non_blocking=True)
            else:
                full = next(data_iter).to(device)
            input_ids = full[:, :-1].contiguous()
            labels = full[:, 1:].contiguous()
            labels = labels.masked_fill(labels == args.eos_id, -100)
            torch.cuda.synchronize()
            t_d1 = time.time()

            # DDP no_sync: skip gradient all-reduce on all micro-steps except the last
            # This eliminates (grad_accum - 1) × all_reduce operations per optimizer step
            sync_ctx = model.no_sync() if (world_size > 1 and not args.no_ddp_no_sync
                                           and micro_idx < grad_accum - 1) else _null_ctx()
            # Mark CUDA graph step boundary for torch.compile reduce-overhead mode
            if args.compile_model:
                torch.compiler.cudagraph_mark_step_begin()
            with sync_ctx:
                if args.chunked_ce:
                    # Chunked CE: get hidden states from base model, compute CE in seq chunks
                    # Bypasses compile/DDP forward — DDP gradient hooks fire on backward
                    # use_cache=False is critical: otherwise KV cache is allocated for all layers
                    hidden = raw_model.model(input_ids=input_ids, use_cache=False).last_hidden_state
                    # FIX (L1): double-shift bug — data is already pre-shifted
                    # (input_ids=full[:,:-1], labels=full[:,1:]), so hidden[i] already
                    # predicts full[i+1] = labels[i].  NO additional shift needed.
                    # Previously did hidden[:,:-1] + labels[:,1:] → predicted full[i+2] (double shift).
                    loss = chunked_cross_entropy(hidden, raw_model.lm_head,
                                                 labels, args.ce_chunk_size,
                                                 logit_scale=mup_scale)
                    loss = loss / grad_accum
                    loss.backward()
                else:
                    # FIX (L1): double-shift bug — HF model's forward does its own
                    # internal shift (shift_logits=logits[:,:-1], shift_labels=labels[:,1:]).
                    # Previously passed labels=full[:,1:] which HF shifts again → double shift.
                    # Fix: pass labels=full[:,:-1] (=input_ids) so HF shift → full[:,1:-1] = single shift.
                    labels_hf = input_ids.clone()
                    labels_hf = labels_hf.masked_fill(labels_hf == args.eos_id, -100)
                    outputs = model(input_ids=input_ids, labels=labels_hf)
                    loss = outputs.loss / grad_accum
                    loss.backward()
            torch.cuda.synchronize()
            t_fb1 = time.time()

            total_loss += loss.item() * grad_accum
            t_data_acc += (t_d1 - t_d0)
            t_fwd_bwd_acc += (t_fb1 - t_d1)

        torch.cuda.synchronize()
        t_o0 = time.time()
        all_params = [p for pg in muon_opt.param_groups for p in pg['params']] + \
                     [p for pg in adamw_opt.param_groups for p in pg['params']]
        torch.nn.utils.clip_grad_norm_(all_params, max_norm=1.0)
        muon_opt.step()
        adamw_opt.step()
        torch.cuda.synchronize()
        t_o1 = time.time()
        t_opt_acc += (t_o1 - t_o0) + t_zg
        timing_step_count += 1

        if rank == 0 and (step % args.log_interval == 0 or step < 5 or step == total_steps - 1):
            elapsed = time.time() - start_time
            tok_per_sec = (step + 1) * args.global_batch_size * args.seq_length / max(1, elapsed)
            avg_loss = total_loss / grad_accum
            msg = (f"[step {step:5d}/{total_steps}] loss={avg_loss:.4f} lr={lr:.2e} "
                   f"tok/s={tok_per_sec/1e3:.1f}K elapsed={elapsed/60:.1f}min")
            print(msg, flush=True)
            with open(log_file, 'a') as f:
                f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")

        if rank == 0 and (step % 5 == 4 or step == total_steps - 1) and timing_step_count > 0:
            n = timing_step_count
            n_micro = n * grad_accum
            t_data_avg = t_data_acc / n_micro * 1000
            t_fwd_bwd_avg = t_fwd_bwd_acc / n_micro * 1000
            t_opt_avg = t_opt_acc / n * 1000
            t_total = (t_data_acc + t_fwd_bwd_acc + t_opt_acc) / n * 1000
            pct_data = t_data_acc / (t_data_acc + t_fwd_bwd_acc + t_opt_acc) * 100
            pct_fb = t_fwd_bwd_acc / (t_data_acc + t_fwd_bwd_acc + t_opt_acc) * 100
            pct_opt = t_opt_acc / (t_data_acc + t_fwd_bwd_acc + t_opt_acc) * 100
            tmsg = (f"[timing step {step:5d}] t_data={t_data_avg:.1f}ms/micro "
                    f"t_fwd_bwd={t_fwd_bwd_avg:.1f}ms/micro "
                    f"t_opt={t_opt_avg:.1f}ms/step "
                    f"t_total={t_total:.1f}ms/step "
                    f"pct: data={pct_data:.0f}% fwd_bwd={pct_fb:.0f}% opt={pct_opt:.0f}%")
            print(tmsg, flush=True)
            with open(timing_file, 'a') as f:
                f.write(f"{time.strftime('%H:%M:%S')} {tmsg}\n")
            t_data_acc = 0.0
            t_fwd_bwd_acc = 0.0
            t_opt_acc = 0.0
            timing_step_count = 0

        # Early verify save: quickly confirm save_pretrained works with compile
        if rank == 0 and args.verify_save_step > 0 and step == args.verify_save_step:
            save_hf_checkpoint(model, args.tokenizer_dir,
                               os.path.join(args.output_dir, f'verify_save_{step}'), rank)
            print(f"  ✅ VERIFY SAVE at step {step} succeeded — checkpoint save bug fixed!", flush=True)

        if rank == 0 and args.profile_steps == 0 and not args.smoke_test \
           and step > 0 and (step + 1) % args.save_interval == 0:
            save_hf_checkpoint(model, args.tokenizer_dir,
                               os.path.join(args.output_dir, f'step_{step + 1}'), rank)

    if rank == 0 and args.profile_steps == 0:
        if not args.smoke_test:
            save_hf_checkpoint(model, args.tokenizer_dir,
                               os.path.join(args.output_dir, 'final'), rank)
        elapsed = time.time() - start_time
        print(f"\n  Done! {total_steps} steps in {elapsed/3600:.2f}h", flush=True)

    if world_size > 1:
        dist.barrier()
        dist.destroy_process_group()


if __name__ == '__main__':
    main()
