#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""baize_posttrain_r134_sft_ablation_design.py — R134: SFT Ablation Design:
LoRA vs Full Fine-Tuning, Data Mix Factorial, Context Length Trade-offs for 4×A40.

Task book P2 step 1 lists "LoRA vs 全参" and "上下文长度 4096 vs 8192 vs 16384"
as open questions. R32 covered GPU memory for full FT; R64 covered SFT dynamics.
This round fills the gap with a concrete ablation design.

Zero GPU, pure Python 3.8+ stdlib. No external dependencies.
"""
from __future__ import annotations
import argparse, json, math, sys
from collections import OrderedDict
from typing import Any, Dict, List, Tuple

MODEL = {
    "name": "MiniCPM5-2B / BaiZe-2B (surrogate)",
    "params_B": 2.0, "hidden_dim": 2048, "num_layers": 42,
    "num_heads": 16, "num_kv_heads": 2, "head_dim": 128,
    "intermediate_size": 6144, "vocab_size": 130560,
    "dtype_bytes": 2,
    "note": "surrogate analysis, not transferable to BaiZe production",
}
GPU = {
    "name": "NVIDIA A40", "total_memory_GiB": 44.93,
    "usable_memory_GiB": 42.0, "bandwidth_Gbps": 696.0,
    "bf16_tflops": 37.4, "num_gpus": 4,
}

# ═══════════════════════════════════════════════════════════════
# 1. Memory Analysis: Full FT vs LoRA
# ═══════════════════════════════════════════════════════════════

def compute_full_ft_memory(params_B, num_gpus, ctx_len, mbs,
                            gradient_checkpointing=True):
    """Compute memory breakdown for full fine-tuning with FSDP."""
    P = params_B * 1e9
    model_per_gpu = (P * 2) / num_gpus / 1e9
    grad_per_gpu = (P * 2) / num_gpus / 1e9
    opt_per_gpu = (P * 8) / num_gpus / 1e9
    h = MODEL["hidden_dim"]; n = MODEL["num_layers"]; dtype = MODEL["dtype_bytes"]
    act_per_layer = 4 * h * ctx_len * mbs * dtype
    effective_layers = int(math.sqrt(n)) if gradient_checkpointing else n
    activation_per_gpu = (act_per_layer * effective_layers) / 1e9
    allgather_buffer = model_per_gpu * 1.5
    total = model_per_gpu + grad_per_gpu + opt_per_gpu + activation_per_gpu + allgather_buffer
    return {
        "mode": "full_ft_fsdp",
        "model_per_gpu_GiB": round(model_per_gpu, 2),
        "grad_per_gpu_GiB": round(grad_per_gpu, 2),
        "opt_per_gpu_GiB": round(opt_per_gpu, 2),
        "activation_per_gpu_GiB": round(activation_per_gpu, 2),
        "allgather_buffer_GiB": round(allgather_buffer, 2),
        "total_per_gpu_GiB": round(total, 2),
        "fits": total <= GPU["usable_memory_GiB"],
        "headroom_GiB": round(GPU["usable_memory_GiB"] - total, 2),
        "gradient_checkpointing": gradient_checkpointing,
        "ctx_len": ctx_len, "mbs": mbs,
    }

def compute_lora_memory(params_B, num_gpus, ctx_len, mbs,
                         lora_rank=64, gradient_checkpointing=True):
    """Compute memory breakdown for LoRA fine-tuning (DDP)."""
    P = params_B * 1e9
    h = MODEL["hidden_dim"]; n = MODEL["num_layers"]
    kv = MODEL["num_kv_heads"]; hd = MODEL["head_dim"]
    inter = MODEL["intermediate_size"]; dtype = MODEL["dtype_bytes"]
    model_per_gpu = (P * 2) / 1e9  # full model on each GPU (DDP)
    # LoRA params: rank * (in_features + out_features) per module, NOT 2*rank*in*out
    module_in_out = [
        (h, h),           # q_proj
        (h, kv * hd),     # k_proj
        (h, kv * hd),     # v_proj
        (h, h),           # o_proj
        (h, inter),       # gate_proj
        (h, inter),       # up_proj
        (inter, h),       # down_proj
    ]
    per_layer_lora = sum(lora_rank * (inp + out) for inp, out in module_in_out)
    total_lora_params = per_layer_lora * n
    lora_params_M = total_lora_params / 1e6
    lora_grad_per_gpu = (total_lora_params * 2) / 1e9
    lora_opt_per_gpu = (total_lora_params * 8) / 1e9
    act_per_layer = 4 * h * ctx_len * mbs * dtype
    effective_layers = int(math.sqrt(n)) if gradient_checkpointing else n
    activation_per_gpu = (act_per_layer * effective_layers) / 1e9
    sync_buffer = lora_grad_per_gpu * 0.1
    total = model_per_gpu + lora_grad_per_gpu + lora_opt_per_gpu + activation_per_gpu + sync_buffer
    return {
        "mode": "lora_r%d_ddp" % lora_rank,
        "model_per_gpu_GiB": round(model_per_gpu, 2),
        "lora_params_M": round(lora_params_M, 1),
        "lora_param_pct": round(lora_params_M / (params_B * 1000) * 100, 3),
        "lora_grad_per_gpu_GiB": round(lora_grad_per_gpu, 4),
        "lora_opt_per_gpu_GiB": round(lora_opt_per_gpu, 4),
        "activation_per_gpu_GiB": round(activation_per_gpu, 2),
        "sync_buffer_GiB": round(sync_buffer, 4),
        "total_per_gpu_GiB": round(total, 2),
        "fits": total <= GPU["usable_memory_GiB"],
        "headroom_GiB": round(GPU["usable_memory_GiB"] - total, 2),
        "gradient_checkpointing": gradient_checkpointing,
        "ctx_len": ctx_len, "mbs": mbs, "lora_rank": lora_rank,
    }

def find_max_mbs(memory_func, params_B, num_gpus, ctx_len, max_mbs=64, **kwargs):
    """Find the maximum micro-batch size that fits in GPU memory."""
    for mbs in range(max_mbs, 0, -1):
        result = memory_func(params_B, num_gpus, ctx_len, mbs, **kwargs)
        if result["fits"]:
            return mbs
    return 0

# ═══════════════════════════════════════════════════════════════
# 2. LoRA Configuration Analysis
# ═══════════════════════════════════════════════════════════════

def analyze_lora_configs():
    """Analyze different LoRA ranks and target module strategies."""
    configs = []
    ranks = [8, 16, 32, 64, 128]
    target_strategies = {
        "attn_only": ["q_proj", "k_proj", "v_proj", "o_proj"],
        "attn_mlp": ["q_proj", "k_proj", "v_proj", "o_proj",
                     "gate_proj", "up_proj", "down_proj"],
        "mlp_only": ["gate_proj", "up_proj", "down_proj"],
    }
    h = MODEL["hidden_dim"]; n = MODEL["num_layers"]
    kv = MODEL["num_kv_heads"]; hd = MODEL["head_dim"]
    inter = MODEL["intermediate_size"]
    module_in_out = {
        "q_proj": (h, h), "k_proj": (h, kv * hd), "v_proj": (h, kv * hd),
        "o_proj": (h, h), "gate_proj": (h, inter), "up_proj": (h, inter),
        "down_proj": (inter, h),
    }
    for rank in ranks:
        for strat_name, modules in target_strategies.items():
            # LoRA params per module = rank * (in + out), A=rank×in, B=out×rank
            per_layer = sum(rank * (module_in_out[m][0] + module_in_out[m][1]) for m in modules)
            total_params = per_layer * n
            total_M = total_params / 1e6
            pct = total_M / (MODEL["params_B"] * 1000) * 100
            if rank <= 16:
                quality = "format/style learning; may miss deep knowledge"
            elif rank <= 64:
                quality = "balanced; good for domain knowledge + tool format"
            else:
                quality = "approaching full FT; diminishing returns"
            alpha = rank * 2
            configs.append({
                "rank": rank, "alpha": alpha,
                "target_strategy": strat_name, "modules": modules,
                "lora_params_M": round(total_M, 1),
                "param_pct": round(pct, 3),
                "quality_estimate": quality,
                "recommended": rank == 64 and strat_name == "attn_mlp",
            })
    return configs


# ═══════════════════════════════════════════════════════════════
# 3. Context Length Trade-off Analysis
# ═══════════════════════════════════════════════════════════════

def analyze_context_length_tradeoffs():
    """Analyze memory and throughput impact of different context lengths."""
    results = []
    ctx_lens = [4096, 8192, 16384]
    for ctx_len in ctx_lens:
        full_ft_mbs = find_max_mbs(compute_full_ft_memory, MODEL["params_B"],
                                    GPU["num_gpus"], ctx_len)
        full_ft_mem = compute_full_ft_memory(MODEL["params_B"], GPU["num_gpus"],
                                              ctx_len, max(full_ft_mbs, 1))
        lora_mbs = find_max_mbs(compute_lora_memory, MODEL["params_B"],
                                 GPU["num_gpus"], ctx_len, lora_rank=64)
        lora_mem = compute_lora_memory(MODEL["params_B"], GPU["num_gpus"],
                                        ctx_len, max(lora_mbs, 1), lora_rank=64)
        P = MODEL["params_B"] * 1e9
        gbs = 32
        tokens_per_step = gbs * ctx_len
        flops_per_step = 6 * P * tokens_per_step * 1.5
        total_tflops = GPU["bf16_tflops"] * GPU["num_gpus"]
        mfu = 0.25
        effective_flops = total_tflops * mfu * 1e12
        seconds_per_step = flops_per_step / effective_flops
        tokens_per_sec = tokens_per_step / seconds_per_step
        if ctx_len == 4096:
            coverage = 0.80
            truncation_note = "20% of multi-turn trajectories truncated; loses error-recovery tails"
        elif ctx_len == 8192:
            coverage = 0.95
            truncation_note = "5% truncated; acceptable for most agentic trajectories"
        else:
            coverage = 0.99
            truncation_note = "1% truncated; near-complete coverage but 4× memory vs 4K"
        results.append({
            "ctx_len": ctx_len,
            "sft_pair_coverage": coverage,
            "truncation_note": truncation_note,
            "full_ft_max_mbs": full_ft_mbs,
            "full_ft_total_GiB": full_ft_mem["total_per_gpu_GiB"],
            "full_ft_fits": full_ft_mem["fits"],
            "lora_max_mbs": lora_mbs,
            "lora_total_GiB": lora_mem["total_per_gpu_GiB"],
            "lora_fits": lora_mem["fits"],
            "throughput_tokens_per_sec": round(tokens_per_sec, 0),
            "seconds_per_step": round(seconds_per_step, 1),
            "steps_per_hour": round(3600 / seconds_per_step, 1),
            "gbs": gbs, "tokens_per_step": tokens_per_step,
        })
    return results

# ═══════════════════════════════════════════════════════════════
# 4. Fractional Factorial Ablation Design
# ═══════════════════════════════════════════════════════════════

def design_ablation_matrix():
    """Design a fractional factorial ablation study."""
    factors = {
        "data_mix": {
            "levels": ["agent_heavy", "balanced", "domain_heavy"],
            "description": "R64 defined 5 mixes; select 3 most promising",
            "main_effect_hypothesis": "agent_heavy→M1 faster; domain_heavy→M2 better",
        },
        "ft_method": {
            "levels": ["lora_r64", "full_ft"],
            "description": "LoRA r=64 attn+mlp vs full fine-tuning",
            "main_effect_hypothesis": "full FT ≥ LoRA by 2-5pp; LoRA 2× faster",
        },
        "ctx_len": {
            "levels": [4096, 8192, 16384],
            "description": "Context window for SFT training",
            "main_effect_hypothesis": "8K optimal; 4K loses recovery; 16K wastes memory",
        },
    }
    full_runs = 3 * 2 * 3  # = 18
    fractional_runs = [
        ("agent_heavy", "lora_r64", 4096,
         "Cheapest run: LoRA+short ctx+agent focus→M1 quick check"),
        ("agent_heavy", "full_ft", 8192,
         "Main candidate for M1: full FT+8K+agent heavy"),
        ("balanced", "lora_r64", 8192,
         "LoRA+8K+balanced→LoRA quality ceiling"),
        ("balanced", "full_ft", 8192,
         "Full FT+8K+balanced→main SFT candidate for M1→M2"),
        ("domain_heavy", "full_ft", 8192,
         "Full FT+8K+domain heavy→M2 optimization"),
        ("domain_heavy", "lora_r64", 16384,
         "LoRA+16K+domain heavy→long trajectory domain test"),
        ("balanced", "full_ft", 4096,
         "Full FT+4K+balanced→ctx length ablation anchor"),
        ("domain_heavy", "full_ft", 16384,
         "Full FT+16K+domain heavy→max quality ceiling test"),
    ]
    time_estimates = {
        ("lora_r64", 4096): 1.5, ("lora_r64", 8192): 2.0, ("lora_r64", 16384): 3.0,
        ("full_ft", 4096): 3.0, ("full_ft", 8192): 4.0, ("full_ft", 16384): 6.0,
    }
    total_hours = 0
    runs_detail = []
    for i, (mix, ft, ctx, rationale) in enumerate(fractional_runs):
        sft_hours = time_estimates.get((ft, ctx), 4.0)
        eval_hours = 0.7
        total = sft_hours + eval_hours
        total_hours += total
        runs_detail.append({
            "run_id": "A%d" % (i+1),
            "data_mix": mix, "ft_method": ft, "ctx_len": ctx,
            "sft_hours": sft_hours, "eval_hours": eval_hours,
            "total_hours": total, "rationale": rationale,
            "gpu_hours": total * GPU["num_gpus"],
        })
    return {
        "factors": factors,
        "full_factorial_runs": full_runs,
        "fractional_runs": len(fractional_runs),
        "reduction_pct": round((1 - len(fractional_runs) / full_runs) * 100, 1),
        "runs": runs_detail,
        "total_wallclock_hours": round(total_hours, 1),
        "total_gpu_hours": round(total_hours * GPU["num_gpus"], 1),
        "design_type": "Strategic fractional (main effects + key interactions)",
        "statistical_note": "Main effects estimable; 2-factor interactions aliased. "
                            "Use R133 McNemar paired test between run pairs.",
    }


# ═══════════════════════════════════════════════════════════════
# 5. GPU Time Budget Allocation
# ═══════════════════════════════════════════════════════════════

def compute_gpu_budget():
    """Compute GPU time budget allocation."""
    main_training_gpu_h = 194
    available_gpu_h = GPU["num_gpus"] * 24 * 28
    ablation = design_ablation_matrix()
    ablation_gpu_h = ablation["total_gpu_hours"]
    contingency_gpu_h = (main_training_gpu_h + ablation_gpu_h) * 0.20
    reward_ablation_gpu_h = 12
    total_planned = main_training_gpu_h + ablation_gpu_h + reward_ablation_gpu_h + contingency_gpu_h
    remaining = available_gpu_h - total_planned
    return {
        "available_gpu_hours": available_gpu_h,
        "allocation": OrderedDict([
            ("main_training", {
                "gpu_hours": main_training_gpu_h,
                "pct": round(main_training_gpu_h / available_gpu_h * 100, 1),
                "description": "Annealing(32)+SFT(48)+RL(96)+eval(3)+baseline(3)+reward_abl(12)",
            }),
            ("sft_ablation", {
                "gpu_hours": ablation_gpu_h,
                "pct": round(ablation_gpu_h / available_gpu_h * 100, 1),
                "description": "%d fractional factorial SFT runs" % ablation["fractional_runs"],
                "wallclock_hours": ablation["total_wallclock_hours"],
            }),
            ("contingency", {
                "gpu_hours": round(contingency_gpu_h, 0),
                "pct": round(contingency_gpu_h / available_gpu_h * 100, 1),
                "description": "20% buffer for re-runs, debugging, failed runs",
            }),
        ]),
        "total_planned_gpu_hours": round(total_planned, 0),
        "remaining_gpu_hours": round(remaining, 0),
        "utilization_pct": round(total_planned / available_gpu_h * 100, 1),
        "verdict": "budget ample" if remaining > 0 else "BUDGET EXCEEDED",
    }

# ═══════════════════════════════════════════════════════════════
# 6. Pre-registered Ablation Decision Rules
# ═══════════════════════════════════════════════════════════════

def preregistered_decision_rules():
    """Pre-registered decision rules for ablation analysis (FROZEN 2026-11-10)."""
    return [
        {"rule_id": "AB-1",
         "question": "LoRA vs Full FT: Is full FT significantly better?",
         "comparison": "A2/A4 (full FT) vs A1/A3 (LoRA), same data_mix & ctx_len",
         "metric": "158-task Pass@1 (5-run mean)",
         "threshold": "Full FT - LoRA >= 3pp AND McNemar p < 0.05",
         "if_met": "Use full FT for main training",
         "if_not_met": "Use LoRA (saves ~50% GPU time for additional RL)",
         "preregistered_date": "2026-11-10"},
        {"rule_id": "AB-2",
         "question": "Context length: Is 8K significantly better than 4K?",
         "comparison": "A4 (8K) vs A7 (4K), same data_mix & ft_method",
         "metric": "158-task Pass@1 (5-run mean)",
         "threshold": "8K - 4K >= 2pp AND McNemar p < 0.05",
         "if_met": "Use 8K for main SFT",
         "if_not_met": "Use 4K (faster, more steps in same time)",
         "preregistered_date": "2026-11-10"},
        {"rule_id": "AB-3",
         "question": "Context length: Is 16K significantly better than 8K?",
         "comparison": "A8 (16K) vs A5 (8K), same data_mix & ft_method",
         "metric": "158-task Pass@1 (5-run mean)",
         "threshold": "16K - 8K >= 2pp AND McNemar p < 0.05",
         "if_met": "Consider 16K if memory allows for RL phase",
         "if_not_met": "Use 8K (16K not worth 4× memory cost)",
         "preregistered_date": "2026-11-10"},
        {"rule_id": "AB-4",
         "question": "Data mix: agent_heavy vs balanced for M1 (50%)?",
         "comparison": "A2 (agent_heavy,full FT,8K) vs A4 (balanced,full FT,8K)",
         "metric": "158-task Pass@1 (5-run mean)",
         "threshold": "agent_heavy - balanced >= 2pp for M1 target",
         "if_met": "Use agent_heavy for M1; switch to balanced/domain for M2",
         "if_not_met": "Use balanced (more general, better for M1→M2 path)",
         "preregistered_date": "2026-11-10"},
        {"rule_id": "AB-5",
         "question": "Data mix: domain_heavy vs balanced for M2 (65%)?",
         "comparison": "A5 (domain_heavy,full FT,8K) vs A4 (balanced,full FT,8K)",
         "metric": "158-task Pass@1 (5-run mean)",
         "threshold": "domain_heavy - balanced >= 3pp AND McNemar p < 0.05",
         "if_met": "Use domain_heavy for M2",
         "if_not_met": "Use balanced (domain_heavy may cause forgetting)",
         "preregistered_date": "2026-11-10"},
        {"rule_id": "AB-6",
         "question": "Interaction: Does LoRA benefit more from longer context?",
         "comparison": "A6-A3 (LoRA 16K-8K) vs A8-A5 (full 16K-8K)",
         "metric": "dd Pass@1 (interaction effect)",
         "threshold": "|interaction| >= 2pp",
         "if_met": "Report interaction; adjust LoRA ctx recommendation",
         "if_not_met": "No significant interaction; treat factors independently",
         "preregistered_date": "2026-11-10"},
    ]


# ═══════════════════════════════════════════════════════════════
# 7. Verl/Transformers Integration Notes
# ═══════════════════════════════════════════════════════════════

def verl_integration_notes():
    """Notes on how LoRA/full FT integrates with verl."""
    return {
        "sft_lora": {
            "framework": "transformers + peft",
            "config": "LoraConfig(r=64, lora_alpha=128, target_modules=[...], lora_dropout=0.05)",
            "training": "Standard HF Trainer with peft adapter",
            "merge": "merge_and_unload() before RL; or keep adapter for RL",
            "advantage": "Fast, low memory, easy to iterate on data mixes",
            "risk": "May underperform full FT for deep knowledge injection (D4)",
        },
        "sft_full_ft": {
            "framework": "transformers + FSDP",
            "config": "FSDP(sharding_strategy=FULL_SHARD, mixed_precision=bf16)",
            "training": "HF Trainer with FSDP config",
            "advantage": "Full capacity for domain knowledge; best quality ceiling",
            "risk": "Slower, more memory, harder to iterate",
        },
        "rl_from_lora": {
            "approach": "Merge LoRA→full model→verl SGLang serve for rollout",
            "note": "verl does not natively support LoRA during RL rollout. Must merge first.",
            "merge_cost": "~2min for 2B model (in-memory merge)",
        },
        "rl_from_full_ft": {
            "approach": "Direct ckpt→verl SGLang serve",
            "note": "Native path; no merge needed",
        },
        "recommendation": (
            "Run ablation first (AB-1 rule). If LoRA within 3pp of full FT, "
            "use LoRA for rapid data mix iteration, then full FT on best mix. "
            "Saves ~50% SFT GPU time for additional RL steps."
        ),
    }

# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="R134: SFT Ablation Design")
    parser.add_argument("--json", type=str, default=None, help="Output JSON report path")
    args = parser.parse_args()
    ctx_lens = [4096, 8192, 16384]

    print("=" * 70)
    print("R134: SFT Ablation Design -- LoRA vs Full FT, Data Mix, Context Length")
    print("Model: %s | GPU: %dx %s" % (MODEL["name"], GPU["num_gpus"], GPU["name"]))
    print("Date: 2026-11-10 | Pre-registration: FROZEN")
    print("=" * 70)

    # 1. Memory Analysis
    print("\n[1] Memory Analysis: Full FT vs LoRA (4xA40, 42GB usable/GPU)")
    print("-" * 60)
    print("\nFull FT (FSDP, gradient checkpointing):")
    for ctx in ctx_lens:
        mbs = find_max_mbs(compute_full_ft_memory, MODEL["params_B"], GPU["num_gpus"], ctx)
        mem = compute_full_ft_memory(MODEL["params_B"], GPU["num_gpus"], ctx, max(mbs, 1))
        print("  ctx=%5d: max_mbs=%2d | total=%.1f GiB | fits=%s | headroom=%.1f GiB"
              % (ctx, mbs, mem["total_per_gpu_GiB"], mem["fits"], mem["headroom_GiB"]))
    print("\nLoRA r=64 (DDP, gradient checkpointing):")
    for ctx in ctx_lens:
        mbs = find_max_mbs(compute_lora_memory, MODEL["params_B"], GPU["num_gpus"], ctx, lora_rank=64)
        mem = compute_lora_memory(MODEL["params_B"], GPU["num_gpus"], ctx, max(mbs, 1), lora_rank=64)
        print("  ctx=%5d: max_mbs=%2d | total=%.1f GiB | fits=%s | headroom=%.1f | lora=%.1fM (%.3f%%)"
              % (ctx, mbs, mem["total_per_gpu_GiB"], mem["fits"], mem["headroom_GiB"],
                 mem["lora_params_M"], mem["lora_param_pct"]))


    # 2-3. LoRA Config & Context Length
    print("\n[2] LoRA Configuration Analysis")
    print("-" * 60)
    lora_configs = analyze_lora_configs()
    for c in lora_configs:
        marker = " * RECOMMENDED" if c["recommended"] else ""
        print("  r=%3d a=%3d | %-10s | params=%7.1fM (%.3f%%) | %s%s"
              % (c["rank"], c["alpha"], c["target_strategy"],
                 c["lora_params_M"], c["param_pct"], c["quality_estimate"], marker))

    print("\n[3] Context Length Trade-offs")
    print("-" * 60)
    ctx_results = analyze_context_length_tradeoffs()
    for r in ctx_results:
        print("  ctx=%5d | cov=%.0f%% | FT_mbs=%2d(%.1fGiB,%s) | LoRA_mbs=%2d(%.1fGiB,%s) | %.0f tok/s"
              % (r["ctx_len"], r["sft_pair_coverage"] * 100,
                 r["full_ft_max_mbs"], r["full_ft_total_GiB"], r["full_ft_fits"],
                 r["lora_max_mbs"], r["lora_total_GiB"], r["lora_fits"],
                 r["throughput_tokens_per_sec"]))
        print("         truncation: %s" % r["truncation_note"])

    # 4-5. Ablation Matrix & GPU Budget
    print("\n[4] Fractional Factorial Ablation Design")
    print("-" * 60)
    ablation = design_ablation_matrix()
    print("  Full factorial: %d runs | Fractional: %d runs (%.0f%% reduction)"
          % (ablation["full_factorial_runs"], ablation["fractional_runs"], ablation["reduction_pct"]))
    for run in ablation["runs"]:
        print("  %s: %-14s %-10s ctx=%5d | %.1fh+%.1fh=%.1fh (%.0f GPU-h) | %s"
              % (run["run_id"], run["data_mix"], run["ft_method"], run["ctx_len"],
                 run["sft_hours"], run["eval_hours"], run["total_hours"],
                 run["gpu_hours"], run["rationale"][:50]))
    print("  Total: %.1f wallclock hours = %.0f GPU-hours" %
          (ablation["total_wallclock_hours"], ablation["total_gpu_hours"]))

    print("\n[5] GPU Time Budget Allocation")
    print("-" * 60)
    budget = compute_gpu_budget()
    print("  Available: %d GPU-hours (4xA40 x 24h x 28d)" % budget["available_gpu_hours"])
    for cat, info in budget["allocation"].items():
        print("  %-16s: %5.0f GPU-h (%4.1f%%) | %s" %
              (cat, info["gpu_hours"], info["pct"], info["description"][:60]))
    print("  Total: %.0f GPU-h | Remaining: %.0f | Util: %.1f%% | %s" %
          (budget["total_planned_gpu_hours"], budget["remaining_gpu_hours"],
           budget["utilization_pct"], budget["verdict"]))

    # 6-7. Decision Rules & Verl Integration
    print("\n[6] Pre-registered Ablation Decision Rules (FROZEN 2026-11-10)")
    print("-" * 60)
    rules = preregistered_decision_rules()
    for rule in rules:
        print("  %s: %s" % (rule["rule_id"], rule["question"]))
        print("         compare: %s | threshold: %s" % (rule["comparison"], rule["threshold"]))
        print("         if met -> %s" % rule["if_met"])
        print("         if not -> %s" % rule["if_not_met"])

    print("\n[7] Verl/Transformers Integration Notes")
    print("-" * 60)
    verl_notes = verl_integration_notes()
    for key, info in verl_notes.items():
        if isinstance(info, dict):
            print("  %s:" % key)
            for k, v in info.items():
                print("    %s: %s" % (k, str(v)[:70]))
        else:
            print("  %s: %s" % (key, str(info)[:70]))

    print("\n" + "=" * 70)
    print("SUMMARY: Full FT fits 4xA40@8K(mbs=42,41.3GiB); LoRA r=64 fits@8K(mbs=45,41.3GiB);")
    print("  8K covers 95% SFT; 8-run fractional factorial; budget 404/2688=15.0%")
    print("  6 pre-registered decision rules (AB-1..AB-6) FROZEN 2026-11-10")
    print("=" * 70)

    if args.json:
        report = {
            "round": "R134", "date": "2026-11-10",
            "model": MODEL, "gpu": GPU,
            "lora_configs": lora_configs,
            "ctx_length_tradeoffs": ctx_results,
            "ablation_design": ablation,
            "gpu_budget": budget,
            "decision_rules": rules,
            "verl_integration": verl_notes,
        }
        with open(args.json, "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print("JSON report written to: %s" % args.json)
    print("\nR134 analysis complete.")


if __name__ == "__main__":
    main()
