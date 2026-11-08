#!/usr/bin/env python3
"""baize_posttrain_gpu_budget_analysis.py — R32: GPU memory budget + GRPO
throughput estimation for MiniCPM5-2B on 4xA40.

R32 (2026-11-08): All previous research validated scripts/configs but nobody
calculated whether 2B + FSDP + SGLang hybrid engine actually fits in A40's
45GB, or estimated how many RL iterations we can run. This script does both.

Model: MiniCPM5-2B (LlamaForCausalLM, 42 layers, hidden=2048, vocab=130560)
GPU:  4x NVIDIA A40 (46068 MiB ~ 45GB each, 696 GB/s bandwidth, 37.4 TF BF16)

Usage:
    python3 baize_posttrain_gpu_budget_analysis.py
    python3 baize_posttrain_gpu_budget_analysis.py --json
"""
from __future__ import annotations
import argparse, json, math, sys
from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass
class ModelConfig:
    hidden_size: int = 2048
    num_layers: int = 42
    num_heads: int = 16
    num_kv_heads: int = 2
    intermediate_size: int = 6144
    vocab_size: int = 130560
    head_dim: int = 128
    dtype_bytes: int = 2  # bf16


@dataclass
class GPUConfig:
    name: str = "A40"
    total_memory_gib: float = 44.93  # 46068 MiB / 1024
    bandwidth_gbps: float = 696.0
    bf16_tflops: float = 37.4
    num_gpus: int = 4


@dataclass
class TrainConfig:
    group_size: int = 8
    train_batch_size: int = 128
    ppo_micro_batch: int = 4
    ppo_max_token_len: int = 16384
    max_prompt_len: int = 4096
    max_response_len: int = 4096
    context_len: int = 8192
    max_turns: int = 3
    sglang_gpu_mem_util: float = 0.50
    sglang_max_seqs: int = 12
    sglang_tp: int = 1
    ppo_epochs: int = 2
    gradient_checkpointing: bool = True
    param_offload: bool = False
    optim_offload: bool = False


SMOKE_OVERRIDES = {
    "group_size": 4, "train_batch_size": 16,
    "sglang_max_seqs": 6, "ppo_micro_batch": 2,
}


def count_params(cfg: ModelConfig) -> Dict[str, float]:
    """Count parameters by component (in millions)."""
    h, n, v, i = cfg.hidden_size, cfg.num_layers, cfg.vocab_size, cfg.intermediate_size
    kv, hd = cfg.num_kv_heads, cfg.head_dim
    q = h * h; k = h * (kv * hd); vv = h * (kv * hd); o = h * h
    attn = q + k + vv + o
    gate = h * i; up = h * i; down = i * h
    mlp = gate + up + down
    per_layer = attn + mlp + 2 * h  # +2 RMSNorm
    embed = v * h; lm_head = v * h; final_norm = h
    total = n * per_layer + embed + lm_head + final_norm
    return {"attn_per_layer_M": attn/1e6, "mlp_per_layer_M": mlp/1e6,
            "per_layer_M": per_layer/1e6, "embedding_M": embed/1e6,
            "lm_head_M": lm_head/1e6, "total_M": total/1e6, "total_B": total/1e9}


def memory_budget(cfg, gpu, train):
    """GPU memory budget for FSDP + SGLang hybrid engine."""
    tp = count_params(cfg)["total_M"] * 1e6
    pb16 = tp * cfg.dtype_bytes; pf32 = tp * 4
    n = gpu.num_gpus
    fsdp_param = pb16 / n
    adam_states = 3 * pf32 / n
    fsdp_persist = fsdp_param + adam_states
    grad_mem = pb16 / n
    act_train = 2.0 * 1024**3
    ref_param = pb16 / n
    ref_act = 1.0 * 1024**3
    train_phase = fsdp_persist + grad_mem + act_train + ref_param + ref_act
    sglang_alloc = train.sglang_gpu_mem_util * gpu.total_memory_gib * 1024**3
    sglang_model = pb16
    kv_per_tok = 2 * cfg.num_kv_heads * cfg.head_dim * cfg.dtype_bytes * cfg.num_layers
    sglang_kv = train.sglang_max_seqs * train.context_len * kv_per_tok
    sglang_actual = sglang_model + sglang_kv
    rollout_phase = fsdp_persist + sglang_actual
    sglang_reserved = sglang_alloc
    avail_for_train = gpu.total_memory_gib * 1024**3 - sglang_reserved
    train_fits = train_phase < avail_for_train
    peak = max(train_phase + sglang_reserved, rollout_phase)
    peak_gib = peak / 1024**3
    util = peak_gib / gpu.total_memory_gib
    return {"total_params_B": tp/1e9, "param_bf16_gib": pb16/1024**3,
            "fsdp_persistent_gib": fsdp_persist/1024**3,
            "fsdp_param_per_gpu_gib": fsdp_param/1024**3,
            "adam_states_per_gpu_gib": adam_states/1024**3,
            "grad_per_gpu_gib": grad_mem/1024**3,
            "activation_train_gib": act_train/1024**3,
            "ref_model_gib": (ref_param+ref_act)/1024**3,
            "train_phase_gib": train_phase/1024**3,
            "sglang_alloc_gib": sglang_alloc/1024**3,
            "sglang_model_gib": sglang_model/1024**3,
            "sglang_kv_gib": sglang_kv/1024**3,
            "sglang_actual_gib": sglang_actual/1024**3,
            "rollout_phase_gib": rollout_phase/1024**3,
            "sglang_reserved_gib": sglang_reserved/1024**3,
            "available_for_training_gib": avail_for_train/1024**3,
            "training_fits": train_fits, "peak_gib": peak_gib,
            "peak_utilization_pct": util*100,
            "headroom_gib": gpu.total_memory_gib - peak_gib,
            "headroom_pct": (1-util)*100}


def throughput_estimate(cfg, gpu, train, mode="train"):
    """Estimate GRPO iteration throughput on 4xA40."""
    tp = count_params(cfg)["total_M"] * 1e6
    n_seqs = train.train_batch_size
    n_turns = train.max_turns
    tps_gen = n_seqs * n_turns * train.max_response_len
    sglang_tps_cons = 5000; sglang_tps_opt = 10000
    rollout_cons = tps_gen / sglang_tps_cons; rollout_opt = tps_gen / sglang_tps_opt
    tool_oh = n_seqs * n_turns * 0.5
    rollout_total_cons = rollout_cons + tool_oh
    rollout_total_opt = rollout_opt + tool_oh
    total_train_tokens = n_seqs * train.context_len
    flops_per_tok = 6 * tp * train.ppo_epochs
    total_flops = flops_per_tok * total_train_tokens
    avail_flops = gpu.bf16_tflops * 1e12 * gpu.num_gpus
    train_low = total_flops / (avail_flops * 0.25)
    train_high = total_flops / (avail_flops * 0.35)
    ref_flops = 2 * tp * total_train_tokens
    ref_time = ref_flops / (avail_flops * 0.35)
    train_total = train_low + ref_time + 5
    iter_cons = rollout_total_cons + train_total
    iter_opt = rollout_total_opt + train_total
    return {"mode": mode, "n_seqs": n_seqs, "n_turns": n_turns,
            "total_gen_tokens": tps_gen,
            "sglang_tps_cons": sglang_tps_cons, "sglang_tps_opt": sglang_tps_opt,
            "rollout_cons_s": rollout_total_cons, "rollout_opt_s": rollout_total_opt,
            "train_s": train_total, "iter_cons_s": iter_cons, "iter_opt_s": iter_opt,
            "iter_cons_min": iter_cons/60, "iter_opt_min": iter_opt/60,
            "smoke_cons_min": (iter_cons*10)/60, "smoke_opt_min": (iter_opt*10)/60,
            "full_cons_h": (iter_cons*2000)/3600, "full_opt_h": (iter_opt*2000)/3600,
            "total_flops": total_flops, "train_tokens": total_train_tokens}


def baseline_eval_estimate(cfg, gpu):
    """Estimate baseline eval (158 tasks x 5 runs) with SGLang."""
    n_tasks, n_runs, timeout = 158, 5, 2500
    sglang_tps = 3000
    avg_tokens = 10000
    parallel = 8
    n_batches = math.ceil(n_tasks / parallel)
    time_per_batch = min(avg_tokens / sglang_tps, timeout)
    per_run = n_batches * time_per_batch
    total = per_run * n_runs
    return {"n_tasks": n_tasks, "n_runs": n_runs, "parallel": parallel,
            "n_batches": n_batches, "avg_tokens": avg_tokens,
            "sglang_tps": sglang_tps, "time_per_batch_s": time_per_batch,
            "per_run_s": per_run, "per_run_min": per_run/60,
            "total_s": total, "total_min": total/60, "total_h": total/3600}


def fmt_s(gib):
    return f"{gib:.2f} GiB" if gib >= 1 else f"{gib*1024:.1f} MiB"

def fmt_t(s):
    if s < 60: return f"{s:.1f}s"
    if s < 3600: return f"{s/60:.1f}min"
    return f"{s/3600:.1f}h"


def print_report(cfg, gpu, train, smoke_train):
    sep = "=" * 72; dash = "-" * 72
    print(sep)
    print("R32: GPU Memory Budget + GRPO Throughput Estimation")
    print("     MiniCPM5-2B on 4x NVIDIA A40 (verl hybrid engine)")
    print(sep)
    params = count_params(cfg)
    print(f"\n{dash}\n1. MODEL PARAMETERS\n{dash}")
    print(f"  Layers: {cfg.num_layers} | Hidden: {cfg.hidden_size} | Heads: {cfg.num_heads} | KV: {cfg.num_kv_heads}")
    print(f"  Vocab: {cfg.vocab_size} | Total params: {params['total_B']:.3f}B ({params['total_M']:.1f}M)")
    print(f"  Embedding: {params['embedding_M']:.1f}M | LM head: {params['lm_head_M']:.1f}M | Per-layer: {params['per_layer_M']:.1f}M")
    print(f"  bf16 size: {fmt_s(params['total_M']*1e6*2/1024**3)}")
    mem = memory_budget(cfg, gpu, train)
    print(f"\n{dash}\n2. GPU MEMORY BUDGET (per A40, {gpu.total_memory_gib:.2f} GiB)\n{dash}")
    print(f"\n  FSDP Persistent: sharded params {fmt_s(mem['fsdp_param_per_gpu_gib'])} + Adam {fmt_s(mem['adam_states_per_gpu_gib'])} = {fmt_s(mem['fsdp_persistent_gib'])}")
    print(f"  Training Phase: grad {fmt_s(mem['grad_per_gpu_gib'])} + act {fmt_s(mem['activation_train_gib'])} + ref {fmt_s(mem['ref_model_gib'])} = {fmt_s(mem['train_phase_gib'])}")
    print(f"  SGLang Rollout: model {fmt_s(mem['sglang_model_gib'])} + KV {fmt_s(mem['sglang_kv_gib'])} = {fmt_s(mem['sglang_actual_gib'])} (reserved {fmt_s(mem['sglang_reserved_gib'])})")
    print(f"  Peak: {fmt_s(mem['peak_gib'])} ({mem['peak_utilization_pct']:.1f}%) | Headroom: {fmt_s(mem['headroom_gib'])} ({mem['headroom_pct']:.1f}%)")
    print(f"  Training fits in remaining: {'YES' if mem['training_fits'] else 'NO'}")
    thr = throughput_estimate(cfg, gpu, train, "train")
    print(f"\n{dash}\n3. GRPO THROUGHPUT (full: G=8, batch=128)\n{dash}")
    print(f"  Seqs/iter: {thr['n_seqs']} | Turns: {thr['n_turns']} | Gen tokens: {thr['total_gen_tokens']:,}")
    print(f"  Per-iter: {fmt_t(thr['iter_cons_s'])} - {fmt_t(thr['iter_opt_s'])}")
    print(f"  Smoke(10): {fmt_t(thr['smoke_opt_min']*60)} - {fmt_t(thr['smoke_cons_min']*60)}")
    print(f"  Full(2000): {thr['full_opt_h']:.1f}h - {thr['full_cons_h']:.1f}h ({thr['full_opt_h']/24:.1f}-{thr['full_cons_h']/24:.1f} days)")
    thr_s = throughput_estimate(cfg, gpu, smoke_train, "smoke")
    print(f"\n{dash}\n4. SMOKE TEST (G=4, batch=16)\n{dash}")
    print(f"  Per-iter: {fmt_t(thr_s['iter_cons_s'])} - {fmt_t(thr_s['iter_opt_s'])} | 10-iter: {fmt_t(thr_s['smoke_opt_min']*60)}-{fmt_t(thr_s['smoke_cons_min']*60)}")
    ev = baseline_eval_estimate(cfg, gpu)
    print(f"\n{dash}\n5. BASELINE EVAL (158 tasks x 5 runs)\n{dash}")
    print(f"  Per run: {fmt_t(ev['per_run_s'])} | Total(5): {fmt_t(ev['total_s'])} ({ev['total_min']:.0f} min)")
    print(f"\n{dash}\n6. CONCLUSIONS\n{dash}")
    print(f"  [OK] Memory fits ({mem['peak_utilization_pct']:.1f}% peak, {fmt_s(mem['headroom_gib'])} headroom)")
    print(f"  [OK] No offload needed | [WARN] gpu_mem_util=0.50 conservative -> 0.60 OK")
    print(f"  [OK] Smoke: {fmt_t(thr_s['smoke_opt_min']*60)}-{fmt_t(thr_s['smoke_cons_min']*60)} fits 20-40min plan")
    print(f"  [WARN] Full RL: {thr['full_opt_h']:.0f}-{thr['full_cons_h']:.0f}h (~{thr['full_opt_h']/24:.0f}-{thr['full_cons_h']/24:.0f} days) - plan carefully")
    print(f"  [OK] Baseline eval: ~{ev['total_min']:.0f}min fits 30-60min slot")
    print(f"  [INFO] R0 fallback: smoke validates chain, NOT RL effectiveness")
    print(f"\n{sep}\nWARNING: Surrogate RL results are NOT transferable to BaiZe.\n{sep}")


def main():
    parser = argparse.ArgumentParser(description="R32 GPU budget analysis")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()
    cfg = ModelConfig(); gpu = GPUConfig(); train = TrainConfig()
    smoke_train = TrainConfig()
    for k, v in SMOKE_OVERRIDES.items():
        setattr(smoke_train, k, v)
    if args.json:
        result = {"model": asdict(cfg), "gpu": asdict(gpu), "train": asdict(train),
                  "params": count_params(cfg), "memory": memory_budget(cfg, gpu, train),
                  "throughput_train": throughput_estimate(cfg, gpu, train, "train"),
                  "throughput_smoke": throughput_estimate(cfg, gpu, smoke_train, "smoke"),
                  "baseline_eval": baseline_eval_estimate(cfg, gpu)}
        print(json.dumps(result, indent=2))
    else:
        print_report(cfg, gpu, train, smoke_train)


if __name__ == "__main__":
    main()
