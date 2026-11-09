#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
baize_posttrain_r138_gpu_memory_budget.py
==========================================
R138: verl Hybrid Engine GPU Memory Budgeting & Resource Partitioning for 4xA40

Analyzes how to partition 4xA40 (46GB each = 184GB total) for verl's hybrid
engine mode (actor FSDP + reference model + SGLang rollout colocated on same GPUs).

Zero GPU -- pure memory modeling based on known model architecture and
verl/FSDP/SGLang memory mechanics.

References: R119, R132, R134, R135, v3 verl config.
Surrogate analysis results are NOT transferable to BaiZe.
"""
import json, math, os, sys
from datetime import datetime
from pathlib import Path

# === Constants — MiniCPM5-2B architecture ===
MODEL_NAME = "MiniCPM5-2B"
NUM_PARAMS_B = 2.0
NUM_LAYERS = 42
HIDDEN_DIM = 2048
NUM_HEADS = 32
HEAD_DIM = 64
VOCAB_SIZE = 73000
MAX_CTX = 16384
GPU_NAME = "A40"
GPU_MEM_GB = 46.0
GPU_MEM_BYTES = int(GPU_MEM_GB * 1024**3)
NUM_GPUS = 4
TOTAL_VRAM_GB = GPU_MEM_GB * NUM_GPUS
TFLOPS_BF16 = 150.0
MEM_BW_GB_S = 696.0
BYTES_BF16 = 2
BYTES_FP32 = 4
BYTES_BF16_GRAD = 2
BYTES_FP32_OPTIM = 8
NUM_KV_HEADS = 8
BYTES_KV_PER_TOKEN = 2 * NUM_LAYERS * 2 * HEAD_DIM * NUM_KV_HEADS * BYTES_BF16

# === Memory estimation functions ===
def model_weights_mem(params_b, precision_bytes, num_gpus=1, fsdp_shard=False):
    total = params_b * 1e9 * precision_bytes
    if fsdp_shard: total = total / num_gpus
    return total / 1e9

def optimizer_mem(params_b, num_gpus=1, fsdp_shard=False):
    total = params_b * 1e9 * (BYTES_FP32_OPTIM + BYTES_FP32)
    if fsdp_shard: total = total / num_gpus
    return total / 1e9

def gradient_mem(params_b, num_gpus=1, fsdp_shard=False):
    total = params_b * 1e9 * BYTES_BF16_GRAD
    if fsdp_shard: total = total / num_gpus
    return total / 1e9

def activation_mem(batch_size, seq_len, hidden_dim, num_layers, num_gpus=1, gradient_checkpointing=True):
    per_layer_bytes = batch_size * seq_len * hidden_dim * 10 * BYTES_BF16
    if gradient_checkpointing:
        n_stored = num_layers
        total = per_layer_bytes * n_stored
    else:
        total = per_layer_bytes * num_layers
    return total / 1e9 / num_gpus

def kv_cache_mem(num_tokens, bytes_per_token=BYTES_KV_PER_TOKEN):
    return num_tokens * bytes_per_token / 1e9

def sglang_overhead_mem(): return 1.5
def cuda_context_mem(): return 0.8
def nccl_buffer_mem(): return 0.3

# === Component memory budgets ===
def actor_memory_full_ft(num_gpus=4, batch_size=4, seq_len=16384, gradient_checkpointing=True):
    weights = model_weights_mem(NUM_PARAMS_B, BYTES_BF16, num_gpus, fsdp_shard=True)
    optim = optimizer_mem(NUM_PARAMS_B, num_gpus, fsdp_shard=True)
    grad = gradient_mem(NUM_PARAMS_B, num_gpus, fsdp_shard=True)
    act = activation_mem(batch_size, seq_len, HIDDEN_DIM, NUM_LAYERS, num_gpus, gradient_checkpointing)
    ctx = cuda_context_mem()
    nccl = nccl_buffer_mem()
    total = weights + optim + grad + act + ctx + nccl
    return {"component":"actor_full_ft","weights_GiB":weights,"optimizer_GiB":optim,
            "gradients_GiB":grad,"activations_GiB":act,"cuda_ctx_GiB":ctx,"nccl_GiB":nccl,
            "total_GiB":total,
            "breakdown":f"weights={weights:.2f}+optim={optim:.2f}+grad={grad:.2f}+act={act:.2f}+ctx={ctx:.2f}+nccl={nccl:.2f}"}

def actor_memory_lora(num_gpus=4, batch_size=4, seq_len=16384, lora_r=64, gradient_checkpointing=True):
    weights = model_weights_mem(NUM_PARAMS_B, BYTES_BF16, num_gpus, fsdp_shard=True)
    lora_params_b = NUM_PARAMS_B * 0.01
    lora_weights = model_weights_mem(lora_params_b, BYTES_BF16, 1, fsdp_shard=False)
    lora_optim = optimizer_mem(lora_params_b, 1, fsdp_shard=False)
    lora_grad = gradient_mem(lora_params_b, 1, fsdp_shard=False)
    act = activation_mem(batch_size, seq_len, HIDDEN_DIM, NUM_LAYERS, num_gpus, gradient_checkpointing)
    ctx = cuda_context_mem()
    nccl = nccl_buffer_mem()
    total = weights + lora_weights + lora_optim + lora_grad + act + ctx + nccl
    return {"component":"actor_lora","base_weights_GiB":weights,"lora_weights_GiB":lora_weights,
            "lora_optimizer_GiB":lora_optim,"lora_gradients_GiB":lora_grad,"activations_GiB":act,
            "cuda_ctx_GiB":ctx,"nccl_GiB":nccl,"total_GiB":total,
            "breakdown":f"base={weights:.2f}+lora_w={lora_weights:.2f}+lora_opt={lora_optim:.2f}+lora_grad={lora_grad:.2f}+act={act:.2f}+ctx={ctx:.2f}+nccl={nccl:.2f}"}

def ref_model_memory(num_gpus=4, seq_len=16384):
    weights = model_weights_mem(NUM_PARAMS_B, BYTES_BF16, num_gpus, fsdp_shard=True)
    act = activation_mem(1, seq_len, HIDDEN_DIM, NUM_LAYERS, num_gpus, gradient_checkpointing=True)
    ctx = cuda_context_mem() * 0.5
    nccl = nccl_buffer_mem() * 0.5
    total = weights + act + ctx + nccl
    return {"component":"ref_model","weights_GiB":weights,"activations_GiB":act,
            "cuda_ctx_GiB":ctx,"nccl_GiB":nccl,"total_GiB":total,
            "breakdown":f"weights={weights:.2f}+act={act:.2f}+ctx={ctx:.2f}+nccl={nccl:.2f}"}

def sglang_rollout_memory(gpu_mem_util, num_gpus=4, batch_size=24, seq_len=16384):
    available = GPU_MEM_GB * gpu_mem_util
    weights = model_weights_mem(NUM_PARAMS_B, BYTES_BF16, 1, fsdp_shard=False)
    overhead = sglang_overhead_mem()
    ctx = cuda_context_mem()
    kv_budget = available - weights - overhead - ctx
    if kv_budget < 0:
        kv_budget = 0; max_tokens = 0
    else:
        max_tokens = int(kv_budget * 1e9 / BYTES_KV_PER_TOKEN)
    concurrent_tokens = batch_size * seq_len
    kv_needed = kv_cache_mem(concurrent_tokens)
    return {"component":"sglang_rollout","gpu_mem_utilization":gpu_mem_util,
            "available_GiB":available,"weights_GiB":weights,"overhead_GiB":overhead,
            "cuda_ctx_GiB":ctx,"kv_budget_GiB":kv_budget,"max_kv_tokens":max_tokens,
            "concurrent_tokens":concurrent_tokens,"kv_needed_GiB":kv_needed,
            "kv_fits":kv_needed<=kv_budget,"total_GiB":available,
            "breakdown":f"avail={available:.2f}=weights={weights:.2f}+overhead={overhead:.2f}+ctx={ctx:.2f}+kv={kv_budget:.2f}"}

# === Hybrid engine colocation analysis ===
def hybrid_engine_budget(actor_mode="full_ft", gpu_mem_util=0.50, actor_batch=4, seq_len=16384, num_gpus=4):
    sglang = sglang_rollout_memory(gpu_mem_util, num_gpus, batch_size=24, seq_len=seq_len)
    if actor_mode == "full_ft":
        actor = actor_memory_full_ft(num_gpus, actor_batch, seq_len)
    else:
        actor = actor_memory_lora(num_gpus, actor_batch, seq_len)
    ref = ref_model_memory(num_gpus, seq_len)
    sglang_weights_resident = sglang["weights_GiB"]
    training_available = GPU_MEM_GB - sglang_weights_resident - sglang["overhead_GiB"] - cuda_context_mem()
    training_needed = actor["total_GiB"] + ref["total_GiB"]
    training_available_best = GPU_MEM_GB - cuda_context_mem() - nccl_buffer_mem()
    rollout_available = GPU_MEM_GB * gpu_mem_util
    oom_risk_worst = training_needed > training_available
    oom_risk_best = training_needed > training_available_best
    sglang_load_ok = sglang["weights_GiB"] + sglang["overhead_GiB"] + cuda_context_mem() <= rollout_available
    return {"actor_mode":actor_mode,"gpu_mem_util":gpu_mem_util,"seq_len":seq_len,
            "actor_batch_per_gpu":actor_batch,"num_gpus":num_gpus,
            "phase1_rollout":{"sglang_available_GiB":rollout_available,"sglang_weights_GiB":sglang["weights_GiB"],
                "sglang_kv_budget_GiB":sglang["kv_budget_GiB"],"sglang_max_kv_tokens":sglang["max_kv_tokens"],
                "sglang_concurrent_tokens":sglang["concurrent_tokens"],"sglang_kv_fits":sglang["kv_fits"],"sglang_load_ok":sglang_load_ok},
            "phase2_training_worst":{"available_GiB":training_available,"needed_GiB":training_needed,
                "actor_GiB":actor["total_GiB"],"ref_GiB":ref["total_GiB"],"oom":oom_risk_worst,
                "headroom_GiB":training_available - training_needed},
            "phase2_training_best":{"available_GiB":training_available_best,"needed_GiB":training_needed,
                "oom":oom_risk_best,"headroom_GiB":training_available_best - training_needed},
            "actor_detail":actor,"ref_detail":ref,"sglang_detail":sglang}

def analyze_strategies():
    strategies = []
    strategies.append(("S1_hybrid_050_full", hybrid_engine_budget("full_ft",0.50,4,16384)))
    strategies.append(("S2_hybrid_040_full", hybrid_engine_budget("full_ft",0.40,4,16384)))
    strategies.append(("S3_hybrid_050_lora", hybrid_engine_budget("lora",0.50,4,16384)))
    strategies.append(("S4_hybrid_060_lora", hybrid_engine_budget("lora",0.60,4,16384)))
    strategies.append(("S5_hybrid_050_full_8k", hybrid_engine_budget("full_ft",0.50,4,8192)))
    strategies.append(("S6_hybrid_045_full_mb2", hybrid_engine_budget("full_ft",0.45,2,16384)))
    strategies.append(("S7_hybrid_055_full_8k", hybrid_engine_budget("full_ft",0.55,4,8192)))
    da = actor_memory_full_ft(num_gpus=2, batch_size=4, seq_len=16384)
    ds = sglang_rollout_memory(0.85, num_gpus=2, batch_size=24, seq_len=16384)
    strategies.append(("S8_dedicated_2_2", {"actor_mode":"full_ft_dedicated","gpu_mem_util":"dedicated",
        "actor_detail":da,"sglang_detail":ds,"seq_len":16384,
        "phase2_training_worst":{"available_GiB":GPU_MEM_GB,"needed_GiB":da["total_GiB"],
            "oom":da["total_GiB"]>GPU_MEM_GB,"headroom_GiB":GPU_MEM_GB-da["total_GiB"]},
        "phase1_rollout":{"sglang_available_GiB":GPU_MEM_GB*0.85,"sglang_max_kv_tokens":ds["max_kv_tokens"],
            "sglang_concurrent_tokens":ds["concurrent_tokens"],"sglang_kv_fits":ds["kv_fits"],
            "sglang_load_ok":ds["weights_GiB"]<GPU_MEM_GB*0.85}}))
    return strategies

def estimate_throughput(strategy_name, budget, num_gpus=4):
    seq_len = budget.get("seq_len", 16384)
    actor_batch = budget.get("actor_batch_per_gpu", 4)
    gpu_mem_util = budget.get("gpu_mem_util", 0.50)
    if not isinstance(gpu_mem_util, (int, float)):
        gpu_mem_util = 0.85
    tokens_per_step = actor_batch * num_gpus * seq_len
    flops_per_step = 6 * NUM_PARAMS_B * 1e9 * tokens_per_step * 2
    total_tflops = TFLOPS_BF16 * num_gpus
    mfu = 0.35
    effective_tflops = total_tflops * mfu
    train_time_s = flops_per_step / (effective_tflops * 1e12)
    n_rollouts = 128 * 8
    rollout_tokens = n_rollouts * 8192
    sglang_toks_per_s = 3000 * num_gpus * gpu_mem_util
    rollout_time_s = rollout_tokens / sglang_toks_per_s if sglang_toks_per_s > 0 else float('inf')
    total_step_time = train_time_s + rollout_time_s
    steps_per_hour = 3600 / total_step_time if total_step_time > 0 else 0
    total_hours = 2000 / steps_per_hour if steps_per_hour > 0 else float('inf')
    return {"strategy":strategy_name,"tokens_per_training_step":tokens_per_step,
            "train_time_per_step_s":round(train_time_s,2),"rollout_time_per_step_s":round(rollout_time_s,2),
            "total_step_time_s":round(total_step_time,2),"steps_per_hour":round(steps_per_hour,1),
            "total_2000_steps_hours":round(total_hours,1),"n_rollouts_per_step":n_rollouts,
            "rollout_tokens_per_step":rollout_tokens,"sglang_throughput_toks_s":round(sglang_toks_per_s,0)}

def oom_risk_matrix():
    results = []
    for mode in ["full_ft","lora"]:
        for util in [0.35,0.40,0.45,0.50,0.55,0.60,0.65,0.70]:
            for ctx in [8192,16384]:
                for mb in [2,4,8]:
                    budget = hybrid_engine_budget(mode,util,mb,ctx)
                    worst = budget["phase2_training_worst"]
                    rollout = budget["phase1_rollout"]
                    risk = "OK"
                    if worst["oom"] and not rollout["sglang_load_ok"]: risk = "OOM_BOTH"
                    elif worst["oom"]: risk = "OOM_TRAIN"
                    elif not rollout["sglang_load_ok"]: risk = "OOM_ROLLOUT"
                    results.append({"mode":mode,"gpu_mem_util":util,"ctx":ctx,"micro_batch":mb,
                        "train_needed_GiB":round(worst["needed_GiB"],2),"train_avail_GiB":round(worst["available_GiB"],2),
                        "headroom_GiB":round(worst["headroom_GiB"],2),"kv_max_tokens":rollout["sglang_max_kv_tokens"],
                        "kv_fits":rollout["sglang_kv_fits"],"sglang_load_ok":rollout["sglang_load_ok"],"risk":risk})
    return results

def monitoring_thresholds():
    return {"FROZEN_date":"2026-11-10","metrics":{
        "gpu_mem_utilization_pct":{"warning":90,"critical":95,"action":"reduce batch or gpu_mem_util","check_freq":"every 50 steps"},
        "gpu_mem_fragmentation_pct":{"warning":30,"critical":50,"action":"torch.cuda.empty_cache() + reduce micro_batch","check_freq":"every 100 steps"},
        "sglang_kv_cache_usage_pct":{"warning":85,"critical":95,"action":"reduce max_num_seqs or max_num_batched_tokens","check_freq":"every rollout"},
        "actor_grad_norm":{"warning":5.0,"critical":10.0,"action":"grad_clip=1.0; if persistent reduce lr","check_freq":"every step"},
        "rollout_timeout_rate":{"warning":0.10,"critical":0.25,"action":"reduce max_num_seqs or n","check_freq":"every rollout"},
        "oom_count":{"warning":1,"critical":3,"action":"auto-restart with reduced batch; 3rd OOM -> halt","check_freq":"continuous"}},
        "oom_recovery_protocol":{
            "step_1":"OOM #1: reduce ppo_micro_batch_size_per_gpu 50%, restart from ckpt",
            "step_2":"OOM #2: reduce max_response_length 8192->4096, restart",
            "step_3":"OOM #3: reduce gpu_memory_utilization 0.50->0.40, restart",
            "step_4":"OOM #4: halt, dump GPU memory report, alert operator",
            "checkpoint_freq":"save_freq=200 -> max 200 steps lost",
            "auto_resume":"resume_mode=auto in v3 config"},
        "pre_registered_decision":"S1 OOM -> S5 (8K) -> S6 (mb=2) -> S3 (LoRA) -> S8 (dedicated)"}

def decision_tree():
    return {"primary":"S1: hybrid, util=0.50, full_ft, mb=4, ctx=16384",
            "fallback_1":"S5: hybrid, util=0.50, full_ft, mb=4, ctx=8192",
            "fallback_2":"S6: hybrid, util=0.45, full_ft, mb=2, ctx=16384",
            "fallback_3":"S3: hybrid, util=0.50, lora_r64, mb=4, ctx=16384",
            "fallback_4":"S8: dedicated 2+2 (2 GPU actor FSDP + 2 GPU SGLang TP=2)",
            "trigger":"OOM -> wait 60s -> retry -> OOM again -> escalate",
            "note":"Pre-registered; no ad-hoc tuning during training"}

# === Main ===
def main():
    sep = "=" * 80
    print(sep)
    print(f"R138: verl Hybrid Engine GPU Memory Budget for {MODEL_NAME} on {NUM_GPUS}x{GPU_NAME}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Total VRAM: {TOTAL_VRAM_GB:.0f} GB ({GPU_MEM_GB:.0f} GB x {NUM_GPUS} GPUs)")
    print(f"KV cache: {BYTES_KV_PER_TOKEN/1024:.1f} KB/token (layers={NUM_LAYERS}, kv_heads={NUM_KV_HEADS})")
    print(sep)
    # 1. Component memory
    print(f"\n{sep}\n1. Component Memory Breakdown (per GPU, FSDP x4)\n{sep}")
    print("\n--- Actor (Full FT, grad_ckpt=True) ---")
    for mb in [2,4,8]:
        for ctx in [8192,16384]:
            a = actor_memory_full_ft(4,mb,ctx)
            print(f"  mb={mb} ctx={ctx:>5}: {a['total_GiB']:.2f} GiB  ({a['breakdown']})")
    print("\n--- Actor (LoRA r=64) ---")
    for mb in [2,4,8]:
        for ctx in [8192,16384]:
            a = actor_memory_lora(4,mb,ctx)
            print(f"  mb={mb} ctx={ctx:>5}: {a['total_GiB']:.2f} GiB  ({a['breakdown']})")
    print("\n--- Reference Model (frozen) ---")
    r = ref_model_memory(4,16384)
    print(f"  ctx=16384: {r['total_GiB']:.2f} GiB  ({r['breakdown']})")
    r8 = ref_model_memory(4,8192)
    print(f"  ctx= 8192: {r8['total_GiB']:.2f} GiB  ({r8['breakdown']})")
    print("\n--- SGLang Rollout ---")
    for util in [0.35,0.40,0.45,0.50,0.55,0.60,0.65,0.70]:
        s = sglang_rollout_memory(util,4,24,16384)
        print(f"  util={util:.2f}: avail={s['available_GiB']:.1f}GB, w={s['weights_GiB']:.1f}GB, "
              f"kv={s['kv_budget_GiB']:.1f}GB, max_tok={s['max_kv_tokens']:,}, fits={s['kv_fits']}")
    # 2. Strategy comparison
    print(f"\n{sep}\n2. Strategy Comparison\n{sep}")
    strategies = analyze_strategies()
    strategy_results = {}
    for name, budget in strategies:
        print(f"\n--- {name} ---")
        w = budget.get("phase2_training_worst",{})
        r1 = budget.get("phase1_rollout",{})
        print(f"  Rollout: avail={r1.get('sglang_available_GiB',0):.1f}GB, kv_fits={r1.get('sglang_kv_fits','?')}, load_ok={r1.get('sglang_load_ok','?')}")
        print(f"  Train: need={w.get('needed_GiB',0):.2f}GB, avail={w.get('available_GiB',0):.2f}GB, head={w.get('headroom_GiB',0):.2f}GB, OOM={w.get('oom','?')}")
        tp = estimate_throughput(name, budget)
        print(f"  Throughput: {tp['steps_per_hour']:.1f} steps/h, 2000 steps in {tp['total_2000_steps_hours']:.1f}h")
        strategy_results[name] = {"budget":{k:v for k,v in budget.items() if isinstance(v,(str,int,float,bool,dict))},"throughput":tp}
    # 3. OOM risk matrix
    print(f"\n{sep}\n3. OOM Risk Matrix\n{sep}")
    print(f"{'Mode':<10} {'Util':>5} {'Ctx':>6} {'MB':>3} {'Need':>7} {'Avail':>7} {'Head':>7} {'KV Tok':>10} {'Risk':>12}")
    print("-"*80)
    oom_results = oom_risk_matrix()
    ok_count = sum(1 for r in oom_results if r["risk"]=="OK")
    for r in oom_results:
        print(f"{r['mode']:<10} {r['gpu_mem_util']:>5.2f} {r['ctx']:>6} {r['micro_batch']:>3} "
              f"{r['train_needed_GiB']:>7.2f} {r['train_avail_GiB']:>7.2f} {r['headroom_GiB']:>7.2f} "
              f"{r['kv_max_tokens']:>10,} {r['risk']:>12}")
    print(f"\nOK: {ok_count}/{len(oom_results)}, OOM: {len(oom_results)-ok_count}/{len(oom_results)}")
    # 4. Recommended
    print(f"\n{sep}\n4. Recommended Configuration\n{sep}")
    best_name, best_tp = None, 0
    for name, res in strategy_results.items():
        b = res["budget"]
        if "phase2_training_worst" in b and not b["phase2_training_worst"]["oom"]:
            if res["throughput"]["steps_per_hour"] > best_tp:
                best_tp = res["throughput"]["steps_per_hour"]; best_name = name
    if best_name:
        print(f"  Best: {best_name} ({best_tp:.1f} steps/h, {strategy_results[best_name]['throughput']['total_2000_steps_hours']:.1f}h)")
    # 5. Monitoring
    print(f"\n{sep}\n5. Pre-registered Monitoring (FROZEN 2026-11-10)\n{sep}")
    mon = monitoring_thresholds()
    for m, c in mon["metrics"].items():
        print(f"  {m}: warn={c['warning']} crit={c['critical']} -> {c['action']}")
    print(f"  OOM: {mon['oom_recovery_protocol']['step_1']}")
    print(f"  -> {mon['oom_recovery_protocol']['step_2']}")
    print(f"  -> {mon['oom_recovery_protocol']['step_3']}")
    print(f"  -> {mon['oom_recovery_protocol']['step_4']}")
    # 6. Decision tree
    print(f"\n{sep}\n6. Fallback Decision Tree\n{sep}")
    dt = decision_tree()
    for k,v in dt.items(): print(f"  {k}: {v}")
    # 7. KV cache
    print(f"\n{sep}\n7. KV Cache Analysis\n{sep}")
    print(f"  Bytes/token: {BYTES_KV_PER_TOKEN:,} ({BYTES_KV_PER_TOKEN/1024:.1f} KB)")
    print(f"  16K seq: {kv_cache_mem(16384):.2f} GB, 8K seq: {kv_cache_mem(8192):.2f} GB")
    print(f"  24x16K: {kv_cache_mem(24*16384):.1f} GB, 24x8K: {kv_cache_mem(24*8192):.1f} GB")
    for util in [0.40,0.45,0.50,0.55,0.60]:
        s = sglang_rollout_memory(util,4,24,16384)
        max16k = s["max_kv_tokens"]//16384 if s["max_kv_tokens"]>0 else 0
        max8k = s["max_kv_tokens"]//8192 if s["max_kv_tokens"]>0 else 0
        print(f"  util={util:.2f}: {s['max_kv_tokens']:,} tokens -> {max16k}x16K or {max8k}x8K concurrent")
    # 8. Summary
    print(f"\n{sep}\n8. Summary & Key Findings\n{sep}")
    s1 = hybrid_engine_budget("full_ft",0.50,4,16384)
    s5 = hybrid_engine_budget("full_ft",0.50,4,8192)
    s3 = hybrid_engine_budget("lora",0.50,4,16384)
    s6 = hybrid_engine_budget("full_ft",0.45,2,16384)
    findings = [
        f"Weights: {model_weights_mem(NUM_PARAMS_B,BYTES_BF16,1):.2f}GB bf16, FSDP/4: {model_weights_mem(NUM_PARAMS_B,BYTES_BF16,4,True):.2f}GB/GPU",
        f"Full FT(mb=4,16K): {actor_memory_full_ft(4,4,16384)['total_GiB']:.2f}GB/GPU",
        f"LoRA(mb=4,16K): {actor_memory_lora(4,4,16384)['total_GiB']:.2f}GB/GPU",
        f"S1(0.50,full,16K): headroom={s1['phase2_training_worst']['headroom_GiB']:.2f}GB OOM={s1['phase2_training_worst']['oom']}",
        f"S5(0.50,full,8K): headroom={s5['phase2_training_worst']['headroom_GiB']:.2f}GB OOM={s5['phase2_training_worst']['oom']}",
        f"S3(0.50,lora,16K): headroom={s3['phase2_training_worst']['headroom_GiB']:.2f}GB OOM={s3['phase2_training_worst']['oom']}",
        f"S6(0.45,full,mb2): headroom={s6['phase2_training_worst']['headroom_GiB']:.2f}GB OOM={s6['phase2_training_worst']['oom']}",
        f"OOM matrix: {ok_count}/{len(oom_results)} OK",
        f"KV: {BYTES_KV_PER_TOKEN/1024:.1f}KB/tok, 24x16K={kv_cache_mem(24*16384):.1f}GB",
        f"Primary: S1 -> S5(8K) -> S6(mb=2) -> S3(LoRA) -> S8(dedicated)",
        f"4-step OOM recovery pre-registered",
    ]
    for f_ in findings: print(f"  - {f_}")
    # Save JSON
    report = {"round":"R138","date":datetime.now().strftime('%Y-%m-%d %H:%M'),
              "model":MODEL_NAME,"gpu":f"{NUM_GPUS}x{GPU_NAME} ({GPU_MEM_GB:.0f}GB each)",
              "total_vram_gb":TOTAL_VRAM_GB,"kv_bytes_per_token":BYTES_KV_PER_TOKEN,
              "strategies":strategy_results,"oom_risk_matrix":oom_results,
              "oom_summary":{"ok":ok_count,"oom":len(oom_results)-ok_count,"total":len(oom_results)},
              "monitoring_thresholds":mon,"decision_tree":dt,"key_findings":findings,
              "recommended_primary":"S1_hybrid_050_full",
              "recommended_fallbacks":["S5 (ctx=8192)","S6 (mb=2,util=0.45)","S3 (LoRA)","S8 (dedicated 2+2)"]}
    report_path = Path(__file__).parent / "r138_gpu_memory_budget_report.json"
    with open(report_path,"w") as f: json.dump(report,f,indent=2,ensure_ascii=False,default=str)
    print(f"\n  Report: {report_path} ({report_path.stat().st_size/1024:.1f} KB)")
    print(f"\n{sep}\nR138 COMPLETE\n{sep}")
    print("Surrogate results NOT transferable to BaiZe.")

if __name__ == "__main__":
    main()
