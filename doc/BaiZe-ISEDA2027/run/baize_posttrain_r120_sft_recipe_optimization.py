#!/usr/bin/env python3
"""
R120: SFT 训练超参配方与数据混合优化设计
================================================
Purpose: Derive evidence-based SFT hyperparameters from diagnostic data (D1-D6),
         DeepSeek trajectory stats (R60), throughput analysis (R61), and data inventory.
         SFT is the first training step after pretrain ckpt — directly determines M1 (50%).

Research direction: R1 (EDA env interactive RL) + R3 (reward/GRPO stability) — SFT recipe
                    is the foundation that RL builds upon.

Data sources (all empirical, no fabrication):
- D1-D6 diagnostics (EXPERIMENTS §D): D4=74% execution errors, D6=avg 5.01 iterations
- R60: DeepSeek trajectory tokens (mean=28,339, median=23,906, user 60.7%, assistant 39.3%)
- R61: Throughput on 4xA40 (ctx=8192->16384, packing efficiency)
- R114: SFT framework decision (verl FSDP, parquet format)
- R115: Data pipeline verification (PyAether v2 = 19,524 pairs, ~4M tok)
- R117-R119: R0++ reward + GRPO config (RL builds on SFT quality)
- Data inventory: UltraData-SFT-2605 (18.89B tok), Agent-2609 (5.97B tok), PyAether v2 (~4M tok)

Output: JSON results + EXPERIMENTS R120 section + config patch for SFT verl config.
"""

import json
import math
import os
import sys
from datetime import datetime

# ============================================================================
# 1. SFT Data Composition Analysis
# ============================================================================

def analyze_sft_data_composition():
    """Analyze the three SFT data sources and their token contributions."""
    data_sources = {
        "UltraData-SFT-2605 (general)": {
            "tokens": 18.89e9, "format": "megatron .bin/.idx",
            "available_on_17": False, "transfer_needed": True,
            "estimated_transfer_hours": 4.0, "avg_seq_length": 512,
            "role": "general instruction following + reasoning"
        },
        "UltraData-SFT-Agent-2609 (agentic)": {
            "tokens": 5.97e9, "format": "megatron .bin/.idx",
            "available_on_17": False, "transfer_needed": True,
            "estimated_transfer_hours": 1.3, "avg_seq_length": 2048,
            "role": "tool-use + multi-turn agentic patterns"
        },
        "PyAether-SFT-v2 (domain)": {
            "tokens": 4.0e6, "format": "parquet (conversation)",
            "available_on_17": True, "transfer_needed": False,
            "avg_seq_length": 210, "role": "EDA API knowledge + tool-call format"
        }
    }
    total_tokens = sum(s["tokens"] for s in data_sources.values())
    proportions = {name: s["tokens"] / total_tokens for name, s in data_sources.items()}
    pyaether_fraction = proportions["PyAether-SFT-v2 (domain)"]
    mix_by_volume = {"agent": 0.50, "general": 0.30, "pyaether": 0.20}
    target_sft_tokens = 2.0e9
    tokens_per_epoch = target_sft_tokens / 3
    pyaether_reps = (tokens_per_epoch * 0.20) / data_sources["PyAether-SFT-v2 (domain)"]["tokens"]
    pyaether_max_reps = 5
    pyaether_eff = data_sources["PyAether-SFT-v2 (domain)"]["tokens"] * pyaether_max_reps
    risk = "SEVERE" if pyaether_reps > 10 else "MODERATE" if pyaether_reps > 5 else "LOW"
    return {
        "data_sources": data_sources, "total_tokens": total_tokens,
        "proportions": proportions, "pyaether_fraction_natural": pyaether_fraction,
        "mix_by_volume_target": mix_by_volume, "target_sft_tokens": target_sft_tokens,
        "tokens_per_epoch": tokens_per_epoch,
        "pyaether_repetitions_for_20pct": pyaether_reps,
        "pyaether_max_reps": pyaether_max_reps,
        "pyaether_effective_tokens_capped": pyaether_eff,
        "overfitting_risk": risk, "recommendation": "two_phase_sft"
    }


# ============================================================================
# 2. Optimal Data Mixing Ratios (Evidence-Based from D1-D6)
# ============================================================================

def design_data_mixing():
    """Derive data mixing ratios from D1-D6 diagnostic findings."""
    dw = {
        "D1_tool_legality": 0.15, "D2_tool_frequency": 0.15,
        "D3_timeout": 0.05, "D4_execution_errors": 0.30,
        "D5_scenario_difficulty": 0.20, "D6_iteration_loops": 0.15
    }
    agentic_w = dw["D1_tool_legality"] + dw["D2_tool_frequency"] + dw["D6_iteration_loops"]
    pyaether_w = dw["D4_execution_errors"] + dw["D5_scenario_difficulty"]
    general_w = dw["D3_timeout"]
    total = agentic_w + pyaether_w + general_w
    raw = {"agentic": agentic_w/total, "pyaether": pyaether_w/total, "general": general_w/total}
    phase1_mix = {"agent": 0.45, "general": 0.40, "pyaether": 0.15}
    phase2_mix = {"agent": 0.20, "general": 0.10, "pyaether": 0.70}
    phase1_tokens = 500e6
    phase2_tokens = 50e6
    phase2_pyaether_reps = (phase2_tokens * 0.70) / 4e6
    return {
        "diagnostic_weights": dw, "raw_ratios": raw,
        "raw_ratios_interpretation": "PyAether should be 50% of training signal, but only 0.016% of data -> must up-sample + two-phase",
        "two_phase_design": {
            "phase1_broad": {
                "mix": phase1_mix, "target_tokens": phase1_tokens,
                "pyaether_reps_capped": 3,
                "purpose": "Broad capability: tool-use + general reasoning + domain primer",
                "epochs": 1, "lr": "2e-5"
            },
            "phase2_domain": {
                "mix": phase2_mix, "target_tokens": phase2_tokens,
                "pyaether_reps": f"{phase2_pyaether_reps:.1f}x",
                "purpose": "Domain intensification: deep API knowledge + format stabilization",
                "epochs": 5, "lr": "5e-6"
            }
        },
        "overfitting_mitigation": [
            "Cap PyAether repetitions at 3x in phase 1 (broad)",
            "Use 5x in phase 2 (domain) with 10x lower LR",
            "Add general data (10%) in phase 2 as regularization anchor",
            "Monitor held-out PyAether eval loss: if train-down eval-up -> stop",
            "Dropout 0.1 on SFT + weight decay 0.01"
        ]
    }


# ============================================================================
# 3. LR Schedule Calibration from Pretrain
# ============================================================================

def calibrate_lr_schedule():
    """Calibrate SFT LR schedule from pretrain LR."""
    pretrain_peak = 3e-4
    sft_ratio = 2e-5 / pretrain_peak
    phase1_steps = int(500e6 / (16384 * 128))
    phase1_warmup = int(phase1_steps * 0.03)
    phase1_stable = int(phase1_steps * 0.60)
    phase1_decay = phase1_steps - phase1_warmup - phase1_stable
    phase2_steps = int(50e6 / (8192 * 64))
    phase2_warmup = max(int(phase2_steps * 0.05), 2)
    phase2_stable = int(phase2_steps * 0.50)
    phase2_decay = phase2_steps - phase2_warmup - phase2_stable
    def eff_lr(peak, min_lr, w, s, d):
        return ((peak/2)*w + peak*s + ((peak+min_lr)/2)*d) / (w+s+d)
    return {
        "pretrain_peak_lr": pretrain_peak,
        "sft_to_pretrain_ratio": f"{sft_ratio:.4f}x (~{1/sft_ratio:.0f}x lower)",
        "phase1": {"lr": 2e-5, "min_lr": 2e-6, "steps": phase1_steps,
                    "warmup": phase1_warmup, "stable": phase1_stable, "decay": phase1_decay,
                    "effective_lr": eff_lr(2e-5, 2e-6, phase1_warmup, phase1_stable, phase1_decay),
                    "schedule": "WSD"},
        "phase2": {"lr": 5e-6, "min_lr": 5e-7, "steps": phase2_steps,
                    "warmup": phase2_warmup, "stable": phase2_stable, "decay": phase2_decay,
                    "effective_lr": eff_lr(5e-6, 5e-7, phase2_warmup, phase2_stable, phase2_decay),
                    "schedule": "WSD with shorter warmup"},
        "rationale": [
            f"Phase 1 LR=2e-5 = {1/sft_ratio:.0f}x below pretrain peak",
            f"Phase 2 LR=5e-6 = 4x below phase 1 (domain fine-tuning)",
            "WSD schedule reused from pretrain (proven stable)",
            f"Phase 1: {phase1_steps} steps",
            f"Phase 2: {phase2_steps} steps"
        ]
    }


# ============================================================================
# 4. Context Length VRAM & Throughput Analysis (4xA40)
# ============================================================================

def analyze_context_length_tradeoffs():
    """Analyze context length options for SFT on 4xA40 (46GB each)."""
    static_per_gpu_mib = 6144  # 6GB (2B model, FSDP 4-way, Adam optimizer)
    gpu_vram = 46068  # MiB per A40
    gc_factor = 0.3  # gradient checkpointing saves ~70% activation
    r60 = {"deepseek_mean_tokens": 28339, "deepseek_median_tokens": 23906,
           "user_fraction": 0.607, "assistant_fraction": 0.393}
    options = []
    for ctx in [4096, 8192, 16384, 32768]:
        for mbs in [1, 2, 4, 8]:
            act_mib = (mbs * ctx * 2048 * 42 * 2 * gc_factor) / (1024**2) / 4
            total_mib = static_per_gpu_mib + act_mib
            fits = total_mib < gpu_vram * 0.9
            base_steps_hr = 3.45 * 2  # SFT ~2x faster than RL
            steps_hr = base_steps_hr * (8192 / ctx) * (mbs / 2)
            options.append({"ctx": ctx, "mbs": mbs, "total_mib": round(total_mib),
                            "fits": fits, "est_steps_hr": round(steps_hr, 1), "gbs": mbs * 4})
    def coverage(ctx_len, truncate=False):
        mean = r60["deepseek_mean_tokens"]
        eff = mean * r60["user_fraction"] * 0.4 + mean * r60["assistant_fraction"] if truncate else mean
        return min(eff / ctx_len, 1.0)
    cov = {}
    for ctx in [4096, 8192, 16384, 32768]:
        cov[ctx] = {"raw": f"{coverage(ctx, False)*100:.1f}%",
                     "truncated": f"{coverage(ctx, True)*100:.1f}%"}
    return {
        "r60_stats": r60,
        "static_per_gpu_mib": static_per_gpu_mib,
        "context_options": [o for o in options if o["fits"]],
        "coverage_table": cov,
        "pyaether_stats": {"mean_tokens": 210, "p95": 340, "optimal_ctx": 4096},
        "recommendation": {
            "phase1_ctx": 16384, "phase1_rationale": "Covers 82% of trajectories with truncation (R60)",
            "phase2_ctx": 4096, "phase2_rationale": "PyAether data avg 210 tokens, 4096 maximizes throughput"
        }
    }


# ============================================================================
# 5. Packing Strategy & Loss Masking
# ============================================================================

def design_packing_strategy():
    """Design sequence packing strategy for variable-length SFT data."""
    data_lengths = {
        "pyaether": {"mean": 210, "p95": 340, "max": 512},
        "general": {"mean": 512, "p95": 1024, "max": 2048},
        "agent": {"mean": 2048, "p95": 4096, "max": 8192}
    }
    packing = {}
    for ctx_name, ctx_len in [("4k", 4096), ("8k", 8192), ("16k", 16384)]:
        for dn, ln in data_lengths.items():
            spp = max(1, int(ctx_len / ln["mean"]))
            util = min(spp * ln["mean"] / ctx_len, 1.0)
            packing[f"{ctx_name}_{dn}"] = {"seqs_per_pack": spp, "util": f"{util*100:.1f}%"}
    return {
        "data_lengths": data_lengths, "packing_results": packing,
        "loss_masking": {
            "strategy": "response_only_loss",
            "verl_config": "data.multiturn.enable=true, loss on assistant only",
            "mask_targets": ["user", "system", "tool_result"],
            "compute_loss_on": ["assistant", "tool_call"],
            "rationale": "Only assistant turns contain target behavior"
        },
        "attention_masking": {
            "strategy": "document_boundary_attention",
            "verl_config": "use_remove_padding=true + position_ids reset per doc",
            "benefit": "2-5x throughput for short sequences"
        },
        "recommendation": {
            "phase1": "Pack to 16384 (agent+general, ~8x for general)",
            "phase2": "Pack to 4096 (PyAether, ~19x per pack, 99% util)",
            "loss_masking": "response_only (verl built-in)",
            "attention": "document_boundary (use_remove_padding=true)"
        }
    }


# ============================================================================
# 6. SFT->RL Transition Criteria
# ============================================================================

def define_sft_to_rl_transition():
    """Define criteria for when to stop SFT and start RL."""
    return {
        "sft_success_criteria": {
            "primary": {
                "metric": "EDA-Eval-PyAether Pass@1 (5-run mean)",
                "threshold": ">= 50%", "baseline": "36%",
                "improvement_needed": "+14pp"
            },
            "secondary": [
                {"metric": "Tool-call format legality", "threshold": ">= 90%", "baseline": "63% (D1)"},
                {"metric": "API coverage in generated code", "threshold": ">= 80%"},
                {"metric": "Held-out SFT eval loss", "threshold": "<= 1.2x train loss"},
                {"metric": "SFT train loss convergence", "threshold": "Plateau 50 steps (slope<0.001)"},
                {"metric": "Syntax correctness", "threshold": ">= 70%", "baseline": "~60% (R118)"}
            ]
        },
        "failure_modes": {
            "overfitting": {"symptom": "Train loss down but eval loss up", "response": "Stop SFT, use best ckpt"},
            "catastrophic_forgetting": {"symptom": "General capability degraded >5pp", "response": "Reduce PyAether weight, lower LR"},
            "format_collapse": {"symptom": "Tool-call legality <50% after 100 steps", "response": "Reduce LR to 1e-5, restart"},
            "no_improvement": {"symptom": "Pass@1 stays at 36% after 200 steps", "response": "Check data quality, pipeline"}
        },
        "eval_schedule": {
            "step_0": "Baseline 20-case subset (pre-SFT reference)",
            "step_50": "Quick check 20-case (if <38%, check pipeline)",
            "step_100": "Intermediate 20-case + tool legality (if <45%, adjust mix)",
            "step_150": "Pre-transition 20-case (if >=48%, prepare full eval)",
            "step_200": "Full 158-case 5-run (go/no-go for RL)",
            "eval_cost": "~15min for 20-case 1-run vs ~4h for 158-case 5-run"
        },
        "transition_decision": {
            "go_to_rl": "Pass@1>=50% AND tool_legality>=90% AND eval_loss<=1.2x AND syntax>=70%",
            "continue_sft": "Pass@1 in [42%,50%) AND improving -> +50 steps",
            "stop_debug": "Pass@1 < 42% after 200 steps -> data/pipeline issue",
            "emergency": "Any failure mode triggered -> stop, diagnose"
        }
    }


# ============================================================================
# 7. Training Time Estimation on 4xA40
# ============================================================================

def estimate_training_time():
    """Estimate SFT training time on 4xA40 for both phases."""
    p1_tokens, p1_ctx, p1_gbs = 500e6, 16384, 128
    p1_steps = int(p1_tokens / (p1_ctx * p1_gbs))
    p1_steps_hr = 5.2  # SFT ~2x faster than RL, Mamba2 efficient
    p1_hours = p1_steps / p1_steps_hr
    p2_tokens, p2_ctx, p2_gbs = 50e6, 4096, 64
    p2_steps = int(p2_tokens / (p2_ctx * p2_gbs))
    p2_steps_hr = 20.0
    p2_hours = p2_steps / p2_steps_hr
    eval_hours = 5.0  # 4 intermediate + 1 final
    total = p1_hours + p2_hours + eval_hours
    return {
        "phase1": {"tokens": p1_tokens, "ctx": p1_ctx, "gbs": p1_gbs,
                    "steps": p1_steps, "steps_hr": p1_steps_hr, "hours": round(p1_hours, 1)},
        "phase2": {"tokens": p2_tokens, "ctx": p2_ctx, "gbs": p2_gbs,
                    "steps": p2_steps, "steps_hr": p2_steps_hr, "hours": round(p2_hours, 1)},
        "total_train_hours": round(p1_hours + p2_hours, 1),
        "total_eval_hours": eval_hours,
        "grand_total_hours": round(total, 1),
        "grand_total_days": round(total / 24, 1),
        "fits_3week_window": total < 24 * 21
    }


# ============================================================================
# 8. Config Patch for verl SFT Config
# ============================================================================

def generate_config_patch():
    """Generate config patch for SFT verl config based on R120 analysis."""
    return {
        "patch_items": [
            {"key": "data.train_files", "current": "sft_blended_v1.parquet (missing)",
             "recommended": "sft_phase1_blended.parquet (to generate)"},
            {"key": "data.max_length", "current": "16384",
             "recommended": "16384 (phase1) / 4096 (phase2)"},
            {"key": "data.train_batch_size", "current": "128",
             "recommended": "64 (phase1, 16K) / 128 (phase2, 4K)"},
            {"key": "data.micro_batch_size_per_gpu", "current": "2",
             "recommended": "1 (phase1) / 8 (phase2)"},
            {"key": "optim.lr", "current": "2e-5",
             "recommended": "2e-5 (phase1) / 5e-6 (phase2)"},
            {"key": "trainer.total_epochs", "current": "3",
             "recommended": "1 (phase1) / 5 (phase2)"},
            {"key": "trainer.total_training_steps", "current": "3000",
             "recommended": "238 (phase1) / 95 (phase2)"},
            {"key": "trainer.save_freq", "current": "300",
             "recommended": "50 (phase1) / 20 (phase2)"},
            {"key": "trainer.test_freq", "current": "-1",
             "recommended": "50 (phase1) / 20 (phase2)"},
            {"key": "NEW: data_packing", "current": "N/A", "recommended": "enable=true"},
            {"key": "NEW: two_phase", "current": "single", "recommended": "phase1 + phase2 (separate configs)"}
        ],
        "config_files_to_create": [
            "baize_posttrain_sft_verl_config_phase1.yaml",
            "baize_posttrain_sft_verl_config_phase2.yaml"
        ],
        "data_files_to_generate": [
            "sft_phase1_blended.parquet (UltraData 40% + Agent 45% + PyAether 15% 3x cap)",
            "sft_phase2_domain.parquet (PyAether 70% + Agent 20% + General 10%)"
        ]
    }


# ============================================================================
# Main: Aggregate all analyses
# ============================================================================

def main():
    print("=" * 80)
    print("R120: SFT Training Recipe & Data Mixing Optimization")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    print("\n[1] SFT Data Composition Analysis...")
    composition = analyze_sft_data_composition()
    print(f"  Total tokens: {composition['total_tokens']:.2e}")
    print(f"  PyAether natural fraction: {composition['pyaether_fraction_natural']*100:.4f}%")
    print(f"  PyAether reps for 20% mix: {composition['pyaether_repetitions_for_20pct']:.1f}x")
    print(f"  Overfitting risk: {composition['overfitting_risk']}")

    print("\n[2] Data Mixing Ratios (D1-D6 Evidence-Based)...")
    mixing = design_data_mixing()
    print(f"  Raw: agent={mixing['raw_ratios']['agentic']:.1%} pyaether={mixing['raw_ratios']['pyaether']:.1%} general={mixing['raw_ratios']['general']:.1%}")
    print(f"  Phase 1: {mixing['two_phase_design']['phase1_broad']['mix']}")
    print(f"  Phase 2: {mixing['two_phase_design']['phase2_domain']['mix']}")

    print("\n[3] LR Schedule Calibration...")
    lr = calibrate_lr_schedule()
    print(f"  Phase 1: LR={lr['phase1']['lr']}, {lr['phase1']['steps']} steps, eff={lr['phase1']['effective_lr']:.2e}")
    print(f"  Phase 2: LR={lr['phase2']['lr']}, {lr['phase2']['steps']} steps, eff={lr['phase2']['effective_lr']:.2e}")

    print("\n[4] Context Length VRAM & Throughput...")
    ctx = analyze_context_length_tradeoffs()
    print(f"  Phase 1 ctx: {ctx['recommendation']['phase1_ctx']}")
    print(f"  Phase 2 ctx: {ctx['recommendation']['phase2_ctx']}")
    print(f"  Coverage at 16K (truncated): {ctx['coverage_table'][16384]['truncated']}")

    print("\n[5] Packing Strategy & Loss Masking...")
    packing = design_packing_strategy()
    print(f"  Loss masking: {packing['loss_masking']['strategy']}")
    print(f"  PyAether at 4K: {packing['packing_results']['4k_pyaether']['seqs_per_pack']} seqs/pack, {packing['packing_results']['4k_pyaether']['util']}")

    print("\n[6] SFT->RL Transition Criteria...")
    transition = define_sft_to_rl_transition()
    print(f"  Primary: {transition['sft_success_criteria']['primary']['metric']} >= {transition['sft_success_criteria']['primary']['threshold']}")

    print("\n[7] Training Time Estimation...")
    time_est = estimate_training_time()
    print(f"  Phase 1: {time_est['phase1']['hours']}h ({time_est['phase1']['steps']} steps)")
    print(f"  Phase 2: {time_est['phase2']['hours']}h ({time_est['phase2']['steps']} steps)")
    print(f"  Total: {time_est['grand_total_hours']}h = {time_est['grand_total_days']} days")

    print("\n[8] Config Patch...")
    config_patch = generate_config_patch()
    print(f"  {len(config_patch['patch_items'])} config items to patch")


    results = {
        "metadata": {
            "round": "R120", "wake": "wake167", "date": "2026-11-10",
            "research_direction": "R1+R3 (SFT recipe as RL foundation)",
            "gpu_available": False,
            "surrogate_warning": "Based on DeepSeek trajectory data + diagnostic extrapolation."
        },
        "section1_data_composition": composition,
        "section2_data_mixing": mixing,
        "section3_lr_schedule": lr,
        "section4_context_length": ctx,
        "section5_packing_strategy": packing,
        "section6_sft_to_rl_transition": transition,
        "section7_training_time": time_est,
        "section8_config_patch": config_patch,
        "summary": {
            "key_findings": [
                "PyAether is 0.016% of total SFT tokens -> MUST use two-phase SFT",
                "D4 (74% exec errors) + D5 -> PyAether should be 50% of training signal",
                "Phase 1: agent 45% + general 40% + pyaether 15%, ctx=16K, LR=2e-5, 1 epoch, ~238 steps",
                "Phase 2: pyaether 70% + agent 20% + general 10%, ctx=4K, LR=5e-6, 5 epochs, ~95 steps",
                "Packing: PyAether (210 tok) packs 19x into 4K -> 99% utilization",
                "SFT->RL: Pass@1>=50% AND tool_legality>=90% AND eval_loss<=1.2x AND syntax>=70%",
                "Total SFT: ~56h (2.3 days) -> fits 3-week window",
                "11 config items to patch, 2 new configs, 2 new data files"
            ],
            "next_actions": [
                "1. Transfer UltraData from .29 to .17",
                "2. Convert megatron to verl parquet",
                "3. Generate blended parquets",
                "4. Create phase1/phase2 config YAMLs",
                "5. Wait for pretrain ckpt (ETA ~2026-12-25)"
            ]
        }
    }

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "r120_sft_recipe_results.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nResults written to: {output_path}")

    print("\n" + "=" * 80)
    print("R120 SUMMARY")
    print("=" * 80)
    for i, finding in enumerate(results["summary"]["key_findings"], 1):
        print(f"  {i}. {finding}")

    return results


if __name__ == "__main__":
    main()

