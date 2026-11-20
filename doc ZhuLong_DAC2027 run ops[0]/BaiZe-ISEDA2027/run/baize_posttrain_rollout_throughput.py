#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""baize_posttrain_rollout_throughput.py — R61: RL Rollout Throughput Projection

Projects GRPO rollout throughput under different context window configs
on 4×A40 48GB with MiniCPM5-2B (2B params). Uses R60 measured trace data.
"""
import argparse, json, math, sys
from datetime import timedelta

# Model & Hardware Constants
MODEL_PARAMS_B = 2.0
MODEL_LAYERS = 42
MODEL_HIDDEN = 2048
A40_MEM_GB = 48.0
SGLANG_OVERHEAD_GB = 2.0
PYTORCH_OVERHEAD_GB = 1.5

# R60 measured (103 DeepSeek traces)
R60_MEAN_TOK = 28339
R60_MEDIAN_TOK = 23906
R60_P90_TOK = 44996
R60_USER_FRAC = 0.607
R60_ASSISTANT_FRAC = 0.393
R60_MEAN_TURNS = 5.01

# SGLang throughput estimates for 2B on A40
SGLANG_PREFILL_TPS = 3500
SGLANG_DECODE_TPS_PER_SEQ = 200
SGLANG_BATCH_DECODE_TPS = 1500

def compute_kv_cache_gb(ctx_len, num_layers, batch_size, kv_heads=32, head_dim=64, prec=2):
    kv_per_token = 2 * num_layers * kv_heads * head_dim * prec
    return kv_per_token * batch_size * ctx_len / (1024**3)

def compute_model_weights_gb(params_b, prec=2):
    return params_b * prec

def compute_optimizer_states_gb(params_b):
    return params_b * 14  # FSDP fp32 Adam + bf16 grad

def compute_total_memory_gb(ctx_len, batch_size, gpu_mem_util, num_gpus=4):
    model_w = compute_model_weights_gb(MODEL_PARAMS_B)
    model_per_gpu = model_w / num_gpus
    optim_per_gpu = compute_optimizer_states_gb(MODEL_PARAMS_B) / num_gpus
    sglang_budget = A40_MEM_GB * gpu_mem_util
    sglang_model = model_w
    sglang_kv = sglang_budget - sglang_model - SGLANG_OVERHEAD_GB
    train_per_gpu = model_per_gpu + optim_per_gpu + PYTORCH_OVERHEAD_GB
    kv_per_seq = compute_kv_cache_gb(ctx_len, MODEL_LAYERS, 1)
    max_concurrent = int(sglang_kv / kv_per_seq) if kv_per_seq > 0 else 0
    return {
        "ctx_len": ctx_len, "batch_size": batch_size, "num_gpus": num_gpus,
        "gpu_mem_util": gpu_mem_util, "model_weights_gb": round(model_w, 2),
        "model_per_gpu_fsdp": round(model_per_gpu, 2),
        "optimizer_per_gpu": round(optim_per_gpu, 2),
        "train_per_gpu": round(train_per_gpu, 2),
        "sglang_budget_gb": round(sglang_budget, 2),
        "sglang_model_gb": round(sglang_model, 2),
        "sglang_kv_budget_gb": round(sglang_kv, 2),
        "kv_per_seq_gb": round(kv_per_seq, 5),
        "max_concurrent_seqs": max_concurrent,
        "remaining_per_gpu": round(A40_MEM_GB - train_per_gpu - sglang_budget, 2),
    }

def estimate_rollout_time_s(ctx_len, mean_tokens, num_turns, max_concurrent, num_gpus, group_size=8):
    tokens_per_turn = mean_tokens / num_turns
    gen_tokens_per_turn = tokens_per_turn * R60_ASSISTANT_FRAC
    prefill_tokens_per_turn = tokens_per_turn * R60_USER_FRAC
    incremental_prefill = prefill_tokens_per_turn * num_turns
    effective_decode_tps = min(SGLANG_BATCH_DECODE_TPS * num_gpus, group_size * SGLANG_DECODE_TPS_PER_SEQ)
    total_gen_tokens = gen_tokens_per_turn * num_turns
    decode_time_s = total_gen_tokens / effective_decode_tps
    prefill_tps_total = SGLANG_PREFILL_TPS * num_gpus
    prefill_time_s = incremental_prefill / prefill_tps_total
    tool_calls_per_turn = 2
    tool_latency_per_call = 1.5
    tool_time_s = num_turns * tool_calls_per_turn * tool_latency_per_call
    total_time = prefill_time_s + decode_time_s + tool_time_s
    return {
        "tokens_per_turn": round(tokens_per_turn, 0),
        "total_gen_tokens": round(total_gen_tokens, 0),
        "incremental_prefill_tokens": round(incremental_prefill, 0),
        "prefill_time_s": round(prefill_time_s, 2),
        "decode_time_s": round(decode_time_s, 2),
        "tool_time_s": round(tool_time_s, 2),
        "total_rollout_time_s": round(total_time, 2),
        "effective_decode_tps": round(effective_decode_tps, 0),
    }

def project_training_timeline(ctx_len, batch_size, group_size, num_gpus, total_steps, gpu_mem_util, hybrid=False):
    mem = compute_total_memory_gb(ctx_len, batch_size, gpu_mem_util, num_gpus)
    # In hybrid engine mode, training memory is offloaded during rollout
    # SGLang can use almost all GPU memory (util applies to full 48GB)
    if hybrid:
        sglang_total = A40_MEM_GB * gpu_mem_util  # e.g., 0.85 × 48 = 40.8GB
        sglang_model = compute_model_weights_gb(MODEL_PARAMS_B)  # 4GB
        sglang_kv = sglang_total - sglang_model - SGLANG_OVERHEAD_GB
        kv_per_seq = compute_kv_cache_gb(ctx_len, MODEL_LAYERS, 1)
        max_concurrent = int(sglang_kv / kv_per_seq) if kv_per_seq > 0 else 0
        mem["sglang_budget_gb"] = round(sglang_total, 2)
        mem["sglang_kv_budget_gb"] = round(sglang_kv, 2)
        mem["max_concurrent_seqs"] = max_concurrent
        mem["hybrid_mode"] = True
        mem["note"] = "Training offloaded during rollout; SGLang uses full budget"
    else:
        mem["hybrid_mode"] = False
        mem["note"] = "Training + SGLang coexist; shared GPU memory"
    rollouts_per_step = batch_size * group_size
    max_concurrent = mem["max_concurrent_seqs"]
    total_concurrent = max_concurrent * num_gpus
    rollout_est = estimate_rollout_time_s(ctx_len, R60_MEAN_TOK, R60_MEAN_TURNS, max_concurrent, num_gpus, group_size)
    prompts_per_wave = total_concurrent // group_size if group_size > 0 else 0
    if prompts_per_wave > 0:
        waves_per_step = math.ceil(batch_size / prompts_per_wave)
        time_per_step = waves_per_step * rollout_est["total_rollout_time_s"]
    else:
        waves_per_step = float('inf')
        time_per_step = float('inf')
    train_update_time_s = 45
    total_step_time = time_per_step + train_update_time_s
    steps_per_hour = 3600 / total_step_time if total_step_time > 0 else 0
    total_time_h = total_steps * total_step_time / 3600
    return {
        "context_config": mem, "rollout_est": rollout_est,
        "rollouts_per_step": rollouts_per_step,
        "max_concurrent_per_gpu": max_concurrent,
        "total_concurrent": total_concurrent,
        "prompts_per_wave": prompts_per_wave,
        "waves_per_step": waves_per_step if prompts_per_wave > 0 else 0,
        "time_per_step_s": round(total_step_time, 1) if prompts_per_wave > 0 else 0,
        "rollout_time_per_step_s": round(time_per_step, 1) if prompts_per_wave > 0 else 0,
        "train_update_time_s": train_update_time_s,
        "steps_per_hour": round(steps_per_hour, 2) if prompts_per_wave > 0 else 0,
        "steps_per_day": round(steps_per_hour * 24, 1) if prompts_per_wave > 0 else 0,
        "total_steps": total_steps,
        "total_time_hours": round(total_time_h, 1) if prompts_per_wave > 0 else 0,
        "total_time_str": str(timedelta(seconds=int(total_step_time * total_steps))) if prompts_per_wave > 0 else "N/A",
        "feasible_72h": total_time_h <= 72 if prompts_per_wave > 0 else False,
    }

CONFIGS = [
    ("OLD 8K (current)", 8192, 128, 8, 4, 0.35, 500, False),
    ("R60 32K non-hybrid", 32768, 128, 8, 4, 0.50, 500, False),
    ("R60 32K hybrid (train offload)", 32768, 128, 8, 4, 0.85, 500, True),
    ("R60 16K hybrid", 16384, 128, 8, 4, 0.85, 500, True),
    ("R60 32K hybrid + bs=64", 32768, 64, 8, 4, 0.85, 500, True),
    ("R60 32K hybrid + G=4", 32768, 128, 4, 4, 0.85, 500, True),
    ("R60 16K non-hybrid", 16384, 128, 8, 4, 0.45, 500, False),
    ("Smoke 32K hybrid", 32768, 16, 4, 4, 0.85, 10, True),
]

def safe_serialize(obj):
    if isinstance(obj, dict):
        return {k: safe_serialize(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [safe_serialize(x) for x in obj]
    elif isinstance(obj, float):
        if math.isinf(obj) or math.isnan(obj):
            return None
        return obj
    return obj

def run_projection(smoke=False, custom_ctx=None, custom_gpus=None, custom_batch=None, custom_group=None):
    if custom_ctx or custom_gpus or custom_batch or custom_group:
        configs = [("CUSTOM", custom_ctx or 32768, custom_batch or 128, custom_group or 8, custom_gpus or 4, 0.85, 500, True)]
    elif smoke:
        configs = [("SMOKE", 32768, 16, 4, 4, 0.85, 10, True)]
    else:
        configs = CONFIGS

    print("=" * 80)
    print("R61: RL Rollout Throughput Projection")
    print(f"  Model: MiniCPM5-2B ({MODEL_PARAMS_B}B params, {MODEL_LAYERS} layers)")
    print(f"  Hardware: 4xA40 {A40_MEM_GB}GB (CUDA 12.4, SGLang 0.4.6)")
    print(f"  R60 data: mean={R60_MEAN_TOK} tok, median={R60_MEDIAN_TOK}, turns={R60_MEAN_TURNS}")
    print("=" * 80)

    results = []
    for name, ctx, bs, gs, ng, util, steps, hybrid in configs:
        print(f"\n--- {name} (ctx={ctx}, bs={bs}, G={gs}, GPUs={ng}, util={util}, hybrid={hybrid}) ---")
        proj = project_training_timeline(ctx, bs, gs, ng, steps, util, hybrid)
        mem = proj["context_config"]
        rol = proj["rollout_est"]
        print(f"  Memory/GPU: model={mem['model_per_gpu_fsdp']}GB optim={mem['optimizer_per_gpu']}GB train={mem['train_per_gpu']}GB sglang={mem['sglang_budget_gb']}GB rem={mem['remaining_per_gpu']}GB")
        print(f"  KV: budget={mem['sglang_kv_budget_gb']}GB per_seq={mem['kv_per_seq_gb']}GB max_concurrent={mem['max_concurrent_seqs']}")
        print(f"  Rollout: gen={rol['total_gen_tokens']}tok prefill={rol['prefill_time_s']}s decode={rol['decode_time_s']}s tool={rol['tool_time_s']}s total={rol['total_rollout_time_s']}s")
        print(f"  Timeline: rollouts/step={proj['rollouts_per_step']} concurrent={proj['total_concurrent']} waves={proj['waves_per_step']} s/step={proj['time_per_step_s']} st/hr={proj['steps_per_hour']} total={proj['total_time_str']} 72h={'Y' if proj['feasible_72h'] else 'N'}")
        results.append({"name": name, "ctx_len": ctx, "batch_size": bs, "group_size": gs, "hybrid": hybrid, **proj})

    print("\n" + "=" * 80)
    print(f"{'Config':<28} {'Ctx':>6} {'Bs':>4} {'G':>3} {'s/step':>8} {'st/hr':>7} {'Total':>12} {'72h':>4}")
    print("-" * 80)
    for r in results:
        print(f"{r['name']:<28} {r['ctx_len']:>6} {r['batch_size']:>4} {r['group_size']:>3} {r['time_per_step_s']:>8.1f} {r['steps_per_hour']:>7.2f} {r['total_time_str']:>12} {'Y' if r['feasible_72h'] else 'N':>4}")

    output = safe_serialize({"R61": "RL Rollout Throughput Projection", "configs": results})
    out_file = "/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/r61_rollout_throughput.json"
    with open(out_file, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nJSON saved: {out_file}")
    return output

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="R61: RL Rollout Throughput Projection")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--ctx", type=int)
    parser.add_argument("--gpus", type=int)
    parser.add_argument("--batch", type=int)
    parser.add_argument("--group", type=int)
    args = parser.parse_args()
    run_projection(smoke=args.smoke, custom_ctx=args.ctx, custom_gpus=args.gpus, custom_batch=args.batch, custom_group=args.group)


