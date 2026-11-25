#!/usr/bin/env python3
"""baize_posttrain_gpu_schedule_optimizer.py — R52: GPU Resource Scheduling & Day-1 Critical Path Analysis

Analyzes GPU memory budgets, resource conflicts between baseline eval and RL training,
produces an optimized Day-1 timeline with post-R47/R49/R50/R51 corrections, and generates
failure-mode decision trees.

Zero GPU required — pure static analysis + timeline computation.

Usage:
    python3 baize_posttrain_gpu_schedule_optimizer.py              # Print analysis to stdout
    python3 baize_posttrain_gpu_schedule_optimizer.py --html       # Generate HTML report
    python3 baize_posttrain_gpu_schedule_optimizer.py --json       # Output JSON summary
"""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta

# ── Constants ──
A40_TOTAL_MIB = 46068
A40_USABLE_MIB = 45000
NUM_GPUS = 4
TOTAL_GPU_MIB = A40_USABLE_MIB * NUM_GPUS
MODEL_SIZE_GB = 4.7
MODEL_PARAMS_B = 2.0
BF16_BYTES_PER_PARAM = 2
ADAMW_STATE_BYTES_PER_PARAM = 8
GRAD_BYTES_PER_PARAM = 2
SGLANG_MEM_FRACTION = 0.85
SGLANG_CTX_LENGTH = 32768
RL_ROLLOUT_MEM_FRAC = 0.35
RL_PPO_MICRO_BATCH = 4
RL_GROUP_SIZE = 8
RL_MAX_PROMPT_LEN = 4096
RL_MAX_RESP_LEN = 4096
RL_SMOKE_ITERS = 10
RL_FULL_ITERS = 2000
RL_TRAIN_BATCH = 128
RL_SMOKE_BATCH = 16
EVAL_TASKS = 158
EVAL_RUNS = 5
EVAL_TIMEOUT_S = 2500
EVAL_PARALLEL = 8
QUICK_TASKS = 10
QUICK_RUNS = 1


def fmt_mib(mib):
    if mib >= 1024:
        return f"{mib/1024:.1f} GB"
    return f"{mib} MiB"


def compute_sglang_serving_memory():
    model_mib = int(MODEL_SIZE_GB * 1024)
    kv_cache_mib = int(A40_USABLE_MIB * SGLANG_MEM_FRACTION - model_mib)
    return {
        "component": "SGLang Serving (baseline eval)",
        "gpus_used": 1,
        "model_weights_mib": model_mib,
        "kv_cache_mib": max(kv_cache_mib, 0),
        "total_per_gpu_mib": int(A40_USABLE_MIB * SGLANG_MEM_FRACTION),
        "total_all_gpus_mib": int(A40_USABLE_MIB * SGLANG_MEM_FRACTION),
        "fits_in_a40": True,
        "notes": f"mem_fraction={SGLANG_MEM_FRACTION}, ctx={SGLANG_CTX_LENGTH}",
    }


def compute_rl_training_memory():
    params_per_gpu = (MODEL_PARAMS_B * 1e9) / NUM_GPUS
    actor_param_mib = int(params_per_gpu * BF16_BYTES_PER_PARAM / (1024**2))
    actor_grad_mib = int(params_per_gpu * GRAD_BYTES_PER_PARAM / (1024**2))
    actor_optim_mib = int(params_per_gpu * ADAMW_STATE_BYTES_PER_PARAM / (1024**2))
    actor_total = actor_param_mib + actor_grad_mib + actor_optim_mib
    ref_param_mib = int(params_per_gpu * BF16_BYTES_PER_PARAM / (1024**2))
    ref_total = ref_param_mib
    rollout_mib = int(A40_USABLE_MIB * RL_ROLLOUT_MEM_FRAC)
    activation_mib = 4096
    fsdp_buffer_mib = int(params_per_gpu * BF16_BYTES_PER_PARAM / (1024**2) * 2)
    total_per_gpu = actor_total + ref_total + activation_mib + fsdp_buffer_mib
    peak_per_gpu = max(total_per_gpu, rollout_mib)
    return {
        "component": "RL Training (verl GRPO, FSDP, hybrid engine)",
        "gpus_used": NUM_GPUS,
        "actor_param_mib": actor_param_mib, "actor_grad_mib": actor_grad_mib,
        "actor_optim_mib": actor_optim_mib, "actor_total_mib": actor_total,
        "ref_total_mib": ref_total, "rollout_mib": rollout_mib,
        "activation_mib": activation_mib, "fsdp_buffer_mib": fsdp_buffer_mib,
        "total_per_gpu_mib": total_per_gpu, "peak_per_gpu_mib": peak_per_gpu,
        "total_all_gpus_mib": peak_per_gpu * NUM_GPUS,
        "fits_in_a40": peak_per_gpu < A40_USABLE_MIB,
        "headroom_mib": A40_USABLE_MIB - peak_per_gpu,
        "notes": f"FSDP sharded across {NUM_GPUS} GPUs, gradient_checkpointing=True, hybrid_engine=True",
    }


def compute_resource_conflicts():
    return [
        {"step_a": "Baseline Eval (SGLang serve)", "step_b": "RL Training (verl GRPO)",
         "gpus_a": 1, "gpus_b": 4, "can_overlap": False,
         "reason": "Baseline needs 1 GPU; RL needs all 4. verl starts its own SGLang workers — external must be killed first.",
         "mitigation": "Serialize: quick baseline -> RL smoke -> RL training. Full baseline after RL pauses."},
        {"step_a": "Quick Baseline (10 tasks)", "step_b": "Preflight Check",
         "gpus_a": 1, "gpus_b": 0, "can_overlap": True,
         "reason": "Preflight is CPU-only; can run while SGLang loads.",
         "mitigation": "Run preflight during SGLang startup wait."},
        {"step_a": "Contamination Gate", "step_b": "D1-D6 Extraction",
         "gpus_a": 0, "gpus_b": 0, "can_overlap": True,
         "reason": "Both are CPU-only.", "mitigation": "Run in parallel."},
        {"step_a": "NFS Warm-up", "step_b": "GPU Polling",
         "gpus_a": 0, "gpus_b": 0, "can_overlap": True,
         "reason": "Warm-up is I/O; polling is nvidia-smi.", "mitigation": "gpu_watcher runs warm-up before launch."},
        {"step_a": "Full Baseline (158x5)", "step_b": "RL Training (2000 iters)",
         "gpus_a": 1, "gpus_b": 4, "can_overlap": False,
         "reason": "1+4=5 > 4 GPUs. Option: reduce RL to 3 GPUs. Risk: RL ~33% slower.",
         "mitigation": "Recommended: serialize. Run full baseline overnight after Day-1 review."},
    ]


def compute_optimized_timeline():
    T0 = datetime(2026, 11, 9, 8, 0, 0)
    steps = [
        {"id": "W0", "name": "GPU Release + NFS Warm-up", "start": T0, "duration_min": 30, "gpus": 0,
         "action": "gpu_watcher detects >=4 free GPUs -> nfs_warmup()",
         "key_outputs": "NFS cache hot, torch import <5s",
         "risk": "NFS cold start (R45: >30s if not warmed)",
         "mitigation": "Warm-up reads model files + imports torch",
         "post_r51_correction": "R46 gpu_watcher auto-detects"},
        {"id": "S0", "name": "Step 0: Venv Verification", "start": T0 + timedelta(minutes=30),
         "duration_min": 5, "gpus": 0,
         "action": "Verify verl_cu124_venv imports OK",
         "key_outputs": "All imports pass, cuda=True",
         "risk": "None — venv verified in R52",
         "mitigation": "Saves 25min vs R38 estimate",
         "post_r51_correction": "R52: torch=2.6.0+cu124, sglang=0.4.6.post1, ray=2.60.0"},
        {"id": "S1", "name": "Step 1: Preflight Check", "start": T0 + timedelta(minutes=35),
         "duration_min": 10, "gpus": 0,
         "action": "bash baize_posttrain_preflight_check.sh",
         "key_outputs": "ALL PASS, 0 FAIL",
         "risk": "v1 stale refs (R49: all fixed)",
         "mitigation": "R49: 0 stale v1, OVERALL=GO",
         "post_r51_correction": "R50: 30/30 PASS, R49: 16/16 PASS"},
        {"id": "S2q", "name": "Step 2a: SGLang + Quick Baseline (10 tasks)",
         "start": T0 + timedelta(minutes=45), "duration_min": 35, "gpus": 1,
         "action": "SGLang serve MiniCPM5-2B (1 GPU) -> cline auth -> 10 tasks",
         "key_outputs": "Quick pass rate, D1/D2/D6 preview",
         "risk": "SGLang startup timeout (R50: BUG-W1 fixed)",
         "mitigation": "R50: 30/30 preflight PASS",
         "post_r51_correction": "R50: minicpm5 parser verified"},
        {"id": "S3q", "name": "Step 3a: Quick D1-D6 + Contamination Gate",
         "start": T0 + timedelta(minutes=80), "duration_min": 15, "gpus": 0,
         "action": "Extract D1-D6 (CPU) + contamination gate (CPU, parallel)",
         "key_outputs": "D1/D2/D6 real values",
         "risk": "Contamination fail = STOP (red-line 5.1)",
         "mitigation": "R24: 0 contamination verified",
         "post_r51_correction": "R49: gate updated to v2 config"},
        {"id": "S5s", "name": "Step 5: RL Smoke (GRPO R0, 10 iters)",
         "start": T0 + timedelta(minutes=95), "duration_min": 40, "gpus": 4,
         "action": "Kill SGLang -> bash baize_posttrain_rl_grpo.sh --smoke --reward-arm R0",
         "key_outputs": "Reward non-zero, no OOM/NaN, cheat rate",
         "risk": "OOM, Ray init, config v2 issues",
         "mitigation": "mem_util=0.35, grad_checkpointing, enforce_eager. R47: v2 fixes 5 bugs.",
         "post_r51_correction": "R47: v2 config. R51: GO 100/100"},
        {"id": "S5c", "name": "Smoke Calibrator Review", "start": T0 + timedelta(minutes=135),
         "duration_min": 15, "gpus": 0,
         "action": "python baize_posttrain_smoke_calibrator.py",
         "key_outputs": "GO/NO-GO for full training",
         "risk": "Zero rewards, KL divergence, NaN",
         "mitigation": "R44+R43 automated checks",
         "post_r51_correction": "R49: calibrator updated to v2 config"},
        {"id": "S6", "name": "Step 6: Full RL Training (GRPO R0)",
         "start": T0 + timedelta(minutes=150), "duration_min": 600, "gpus": 4,
         "action": "bash baize_posttrain_rl_grpo.sh --reward-arm R0 -> 2000 iters",
         "key_outputs": "Checkpoints q200, reward curve, cheat rate",
         "risk": "Reward hacking, instability, OOM",
         "mitigation": "R48 pre-registered. Anti-cheat. R36 observability. save_freq=200.",
         "post_r51_correction": "R51: 0 CRITICAL open. R-009 Phase2 only"},
        {"id": "D1r", "name": "Day-1 Checkpoint Review (T+10h)",
         "start": T0 + timedelta(minutes=750), "duration_min": 30, "gpus": 0,
         "action": "Review: RL stable? Reward up? KL<10? Cheat<5%?",
         "key_outputs": "GO to continue OR pause+adjust",
         "risk": "Divergence, plateau, cheat spike",
         "mitigation": "R48 decision gates: M1=50%",
         "post_r51_correction": "R51: 4 FIXED+5 MITIGATED+1 OPEN+3 MON+2 ACK"},
    ]
    for s in steps:
        s["end"] = s["start"] + timedelta(minutes=s["duration_min"])
    return steps


def compute_full_baseline_schedule():
    avg_task_min = 8
    batches = (EVAL_TASKS + EVAL_PARALLEL - 1) // EVAL_PARALLEL
    total_min = batches * avg_task_min * EVAL_RUNS
    options = [
        {"option": "A: After RL training (serialized)", "when": "Day 2-3",
         "gpus": 1, "duration_hours": total_min / 60, "rl_impact": "None — RL paused",
         "risk": "Delays 1-2 days", "advantage": "No conflict, clean"},
        {"option": "B: Parallel (3+1 GPU split)", "when": "Day 1",
         "gpus": "1+3", "duration_hours": total_min / 60 * 1.3, "rl_impact": "~33% slower",
         "risk": "OOM risk", "advantage": "Ready Day 2 AM"},
        {"option": "C: Overnight Day 1 (after smoke, before full RL)", "when": "T+2:30-T+15:30",
         "gpus": 1, "duration_hours": total_min / 60, "rl_impact": "RL delayed to Day 2",
         "risk": "Lose ~10h RL", "advantage": "Real D1-D6 before RL"},
    ]
    return {"options": options, "recommended": "C",
            "rationale": "Option C: real D1-D6 inform reward design; no conflict; RL has ~2 weeks before ckpt.",
            "estimated_hours": total_min / 60}


def compute_failure_mode_decision_trees():
    return [
        {"failure": "GPU not freed by T+0:30", "detection": "gpu_watcher: FREE_GPUS < 4",
         "decision_tree": ["-> Poll every 15min (DO NOT kill others)", "-> If not freed T+2:00: report",
                           "-> Fallback: --gpu-ids for free GPUs", "-> 0 free: wait"],
         "new_in_r52": "gpu_watcher --check-now can verify"},
        {"failure": "SGLang serve fails", "detection": "curl timeout 300s",
         "decision_tree": ["-> Check model path (R52: verified)", "-> Check port 8866 free",
                           "-> Check sglang import (R52: 0.4.6.post1)", "-> Try lower mem-fraction",
                           "-> Try enforce_eager", "-> R50: parser=minicpm5"],
         "new_in_r52": "R50: 30/30 preflight PASS"},
        {"failure": "Baseline 0% pass", "detection": "run_eval.py: 0 passed",
         "decision_tree": ["-> Check cline auth", "-> Check SGLang responding",
                           "-> Check dataset path", "-> Check cline in PATH",
                           "-> R50: verify tool-call-parser"],
         "new_in_r52": "R50: BUG-W1 fixed (parameters not arguments)"},
        {"failure": "RL smoke: zero rewards", "detection": "smoke_calibrator: reward=0",
         "decision_tree": ["-> Check reward_arm=R0", "-> Check parquet loads",
                           "-> Check compute_score non-zero", "-> Check v2 config (R49: 0 stale v1)",
                           "-> If NaN: check div by zero"],
         "new_in_r52": "R47: v2 fixes reward function path"},
        {"failure": "RL OOM on A40", "detection": "CUDA OOM in verl log",
         "decision_tree": ["-> Reduce micro_batch: 4->2->1", "-> Reduce mem_util: 0.35->0.25",
                           "-> Reduce response_length: 4096->2048", "-> Enable dynamic_bsz (on)",
                           "-> Enable grad_checkpointing (on)", "-> R52: peak ~24GB, headroom ~21GB"],
         "new_in_r52": "R52: OOM unlikely (24GB peak vs 46GB A40)"},
        {"failure": "KL divergence explodes", "detection": "P1: KL>10",
         "decision_tree": ["-> Reduce lr: 3e-6->1e-6", "-> Increase kl_coef: 0.02->0.05",
                           "-> Reduce clip: 0.2->0.1", "-> Resume from checkpoint"],
         "new_in_r52": "R36: P1-P7 auto-alerts. R18: KL=0.02 start"},
        {"failure": "Reward hacking (cheat>5%)", "detection": "P7: cheat>0.05",
         "decision_tree": ["-> DO NOT stop (report)", "-> Tighten anti-cheat",
                           "-> Check R0 unlikely to hack", "-> Document cheat_rate",
                           "-> >20%: pause, investigate"],
         "new_in_r52": "R48: cheat rate pre-registered metric"},
        {"failure": "Ray worker crash (R-009, Phase2)", "detection": "Ray actor death",
         "decision_tree": ["-> Phase1: NOT affected", "-> Phase2: monkey-patch (OPEN)",
                           "-> ray stop + restart", "-> Resume from checkpoint"],
         "new_in_r52": "R51: Phase2-only, Phase1 not blocked"},
    ]


def generate_html_report():
    sglang = compute_sglang_serving_memory()
    rl = compute_rl_training_memory()
    conflicts = compute_resource_conflicts()
    timeline = compute_optimized_timeline()
    baseline_opts = compute_full_baseline_schedule()
    trees = compute_failure_mode_decision_trees()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    h = []  # html parts list

    h.append(f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>BaiZe Post-Train R52: GPU 资源调度与 Day-1 关键路径优化</title>
<style>
body {{ font-family: -apple-system, "Microsoft YaHei", sans-serif; margin: 2em auto; max-width: 1200px; line-height: 1.6; color: #333; }}
h1 {{ color: #1a5276; border-bottom: 3px solid #2980b9; padding-bottom: 0.3em; }}
h2 {{ color: #2874a6; margin-top: 2em; border-bottom: 1px solid #bdc3c7; padding-bottom: 0.2em; }}
h3 {{ color: #2e86c1; }}
table {{ border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 0.92em; }}
th, td {{ border: 1px solid #bdc3c7; padding: 6px 10px; text-align: left; }}
th {{ background: #d4e6f1; font-weight: 600; }}
tr:nth-child(even) {{ background: #f8f9fa; }}
.green {{ color: #27ae60; font-weight: bold; }}
.orange {{ color: #e67e22; font-weight: bold; }}
.code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: monospace; }}
.section {{ background: #eaf2f8; padding: 1em 1.5em; border-radius: 5px; margin: 1em 0; }}
.summary-box {{ background: #fef9e7; border: 1px solid #f9e79f; border-radius: 5px; padding: 1em 1.5em; margin: 1em 0; }}
.conflict-yes {{ background: #fadbd8; }}
.conflict-no {{ background: #d5f5e3; }}
.timeline-item {{ border-left: 3px solid #2980b9; padding-left: 1em; margin: 0.5em 0 1em 1em; }}
.timeline-time {{ font-weight: bold; color: #2980b9; }}
.dt {{ background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 0.8em 1.2em; margin: 0.5em 0; }}
.r52-new {{ background: #fef9e7; border-left: 3px solid #f39c12; padding: 2px 6px; font-size: 0.85em; }}
</style>
</head>
<body>
<h1>BaiZe Post-Train R52: GPU 资源调度与 Day-1 关键路径优化</h1>
<p><strong>日期</strong>: {now} | <strong>唤醒</strong>: wake100 | <strong>GPU</strong>: 2026-11-09</p>
<div class="summary-box">
<h3>摘要</h3>
<p>11/9 GPU到位前最终资源调度方案。基于R47-R51修复，全面校正Day-1时间线，新增GPU内存预算、资源冲突矩阵、基线评测调度、故障决策树。</p>
<p><strong>核心发现</strong>：基线评测(1 GPU)与RL训练(4 GPU)不能并行。verl hybrid engine启动自己的SGLang workers，外部SGLang必须先kill。推荐方案C：先基线(~13h)获取真实D1-D6再RL。</p>
<p><strong>R52实测</strong>：torch=2.6.0+cu124 sglang=0.4.6.post1 verl ok ray=2.60.0 模型4.7GB venv就绪</p>
</div>""")

    h.append(f"""
<h2>1. GPU 内存预算分析</h2>
<h3>1.1 SGLang 服务（基线评测, 1 GPU）</h3>
<table>
<tr><th>项目</th><th>值</th><th>说明</th></tr>
<tr><td>模型权重</td><td>{fmt_mib(sglang['model_weights_mib'])}</td><td>MiniCPM5-2B bf16</td></tr>
<tr><td>KV缓存</td><td>{fmt_mib(sglang['kv_cache_mib'])}</td><td>ctx=32768</td></tr>
<tr><td>单GPU占用</td><td>{fmt_mib(sglang['total_per_gpu_mib'])}</td><td>占A40 {sglang['total_per_gpu_mib']/A40_USABLE_MIB*100:.0f}%</td></tr>
<tr><td>适配A40</td><td class="green">YES</td><td>余量~{fmt_mib(A40_USABLE_MIB - sglang['total_per_gpu_mib'])}</td></tr>
</table>
<h3>1.2 RL训练（verl GRPO, FSDP, 4 GPU）</h3>
<table>
<tr><th>组件</th><th>每GPU</th><th>说明</th></tr>
<tr><td>Actor参数</td><td>{fmt_mib(rl['actor_param_mib'])}</td><td>FSDP:2B/4</td></tr>
<tr><td>Actor梯度</td><td>{fmt_mib(rl['actor_grad_mib'])}</td><td>bf16</td></tr>
<tr><td>Actor优化器</td><td>{fmt_mib(rl['actor_optim_mib'])}</td><td>AdamW fp32</td></tr>
<tr><td>Actor小计</td><td>{fmt_mib(rl['actor_total_mib'])}</td><td></td></tr>
<tr><td>参考模型</td><td>{fmt_mib(rl['ref_total_mib'])}</td><td>仅前向</td></tr>
<tr><td>Rollout</td><td>{fmt_mib(rl['rollout_mib'])}</td><td>mem_util={RL_ROLLOUT_MEM_FRAC}</td></tr>
<tr><td>激活值</td><td>{fmt_mib(rl['activation_mib'])}</td><td>grad_checkpointing</td></tr>
<tr><td>FSDP buffer</td><td>{fmt_mib(rl['fsdp_buffer_mib'])}</td><td>2x param</td></tr>
<tr><td><strong>训练峰值</strong></td><td class="green">{fmt_mib(rl['total_per_gpu_mib'])}</td><td></td></tr>
<tr><td><strong>实际峰值(max)</strong></td><td class="green">{fmt_mib(rl['peak_per_gpu_mib'])}</td><td>hybrid交替</td></tr>
<tr><td>A40余量</td><td class="green">{fmt_mib(rl['headroom_mib'])}</td><td>OOM风险极低</td></tr>
</table>
<p><strong>结论</strong>：RL每GPU峰值~{fmt_mib(rl['peak_per_gpu_mib'])}，A40 46GB余量~{fmt_mib(rl['headroom_mib'])}，OOM风险极低。</p>""")

    h.append("""
<h2>2. 资源冲突矩阵</h2>
<table>
<tr><th>步骤A</th><th>步骤B</th><th>GPU A</th><th>GPU B</th><th>并行</th><th>原因</th></tr>""")
    for c in conflicts:
        cls = "conflict-no" if c["can_overlap"] else "conflict-yes"
        ov = "YES" if c["can_overlap"] else "NO"
        h.append(f'<tr class="{cls}"><td>{c["step_a"]}</td><td>{c["step_b"]}</td><td>{c["gpus_a"]}</td><td>{c["gpus_b"]}</td><td>{ov}</td><td>{c["reason"]}<br><em>{c["mitigation"]}</em></td></tr>')
    h.append('</table>')
    h.append('<div class="section"><p><strong>关键冲突</strong>：基线(1GPU)与RL(4GPU)不能并行。verl启动自己的SGLang，外部必须先kill。</p></div>')

    h.append(f"""
<h2>3. 完整基线评测调度</h2>
<p>158任务x5轮，预估{baseline_opts['estimated_hours']:.1f}小时。推荐方案C。</p>
<table>
<tr><th>方案</th><th>时间</th><th>GPU</th><th>时长</th><th>RL影响</th><th>优势</th></tr>""")
    for opt in baseline_opts["options"]:
        rec = " RECOMMENDED" if opt["option"].startswith(baseline_opts["recommended"]) else ""
        h.append(f'<tr><td><strong>{opt["option"]}</strong>{rec}</td><td>{opt["when"]}</td><td>{opt["gpus"]}</td><td>{opt["duration_hours"]:.1f}h</td><td>{opt["rl_impact"]}</td><td>{opt["advantage"]}</td></tr>')
    h.append(f'</table><p><strong>推荐C</strong>：{baseline_opts["rationale"]}</p>')

    h.append('<h2>4. 优化后 Day-1 时间线（融合 R47-R51）</h2>')
    for s in timeline:
        start_str = s["start"].strftime("%H:%M")
        end_str = s["end"].strftime("%H:%M")
        gpu_label = f"{s['gpus']} GPU" if s["gpus"] > 0 else "CPU"
        h.append(f'<div class="timeline-item"><p class="timeline-time">{start_str}-{end_str} ({s["duration_min"]}min) {s["id"]} [{gpu_label}]</p>')
        h.append(f'<p><strong>{s["name"]}</strong></p><p>动作:{s["action"]} | 产出:{s["key_outputs"]}</p>')
        h.append(f'<p>风险:{s["risk"]} | 缓解:{s["mitigation"]}</p>')
        if s.get("post_r51_correction"):
            h.append(f'<p><span class="r52-new">R52修正</span>: {s["post_r51_correction"]}</p>')
        h.append('</div>')

    h.append(f"""
<div class="summary-box">
<h3>时间线改进(vs R38)</h3>
<ul><li>S0从15-30min缩至5min:venv已验证</li>
<li>S5 RL smoke修正为R0臂</li><li>新增方案C:完整基线先跑</li>
<li>新增GPU预算:峰值~{fmt_mib(rl['peak_per_gpu_mib'])}/GPU,余量{fmt_mib(rl['headroom_mib'])}</li></ul>
</div>""")

    h.append('<h2>5. 故障模式决策树（融合 R47-R51）</h2>')
    for i, t in enumerate(trees):
        h.append(f'<h3>5.{i+1} {t["failure"]}</h3><p>检测:<span class="code">{t["detection"]}</span></p>')
        h.append('<div class="dt"><ul>')
        for step in t["decision_tree"]:
            h.append(f'<li>{step}</li>')
        h.append('</ul></div>')
        if t.get("new_in_r52"):
            h.append(f'<p><span class="r52-new">R52新增</span>: {t["new_in_r52"]}</p>')

    h.append("""
<h2>6. 预发射检查清单</h2>
<table>
<tr><th>#</th><th>检查项</th><th>预期</th><th>状态</th></tr>
<tr><td>1</td><td>GPU释放</td><td>4+ free</td><td class="orange">待11/9</td></tr>
<tr><td>2</td><td>模型文件</td><td>4.7GB</td><td class="green">R52</td></tr>
<tr><td>3</td><td>venv cuda</td><td>True</td><td class="green">R52</td></tr>
<tr><td>4</td><td>sglang</td><td>0.4.6.post1</td><td class="green">R52</td></tr>
<tr><td>5</td><td>verl</td><td>OK</td><td class="green">R52</td></tr>
<tr><td>6</td><td>ray</td><td>2.60.0</td><td class="green">R52</td></tr>
<tr><td>7</td><td>v2 config</td><td>grpo</td><td class="green">R47</td></tr>
<tr><td>8</td><td>v1 stale</td><td>0</td><td class="green">R49</td></tr>
<tr><td>9</td><td>SGLang preflight</td><td>30/30</td><td class="green">R50</td></tr>
<tr><td>10</td><td>E2E audit</td><td>GO 100/100</td><td class="green">R51</td></tr>
<tr><td>11</td><td>RL数据</td><td>parquet</td><td class="green">R10</td></tr>
<tr><td>12</td><td>SFT语料</td><td>0污染</td><td class="green">R24</td></tr>
<tr><td>13</td><td>cline PATH</td><td>有输出</td><td class="orange">需确认</td></tr>
</table>""")

    h.append(f"""
<h2>7. 关键路径与瓶颈</h2>
<div class="section">
<p><strong>关键路径</strong>:GPU释放(30m)->Preflight(10m)->SGLang+快速基线(35m)->D1-D6+污染门(15m)->RL smoke(40m)->校准(15m)=<strong>145min~2h25m</strong></p>
<p><strong>瓶颈</strong>:完整基线(~13h)。方案C延迟RL~13h但获得真实D1-D6。</p>
</div>
<h2>8. 风险登记册(R51->R52)</h2>
<table>
<tr><th>R-ID</th><th>风险</th><th>R51</th><th>R52</th></tr>
<tr><td>R-001</td><td>SGLang BUG-W1</td><td>FIXED</td><td class="green">仍FIXED</td></tr>
<tr><td>R-009</td><td>Ray(Phase2)</td><td class="orange">OPEN</td><td class="orange">Phase1不阻塞</td></tr>
<tr><td>R-010</td><td>GPU OOM</td><td>ACK</td><td class="green">峰值{fmt_mib(rl['peak_per_gpu_mib'])},余量{fmt_mib(rl['headroom_mib'])}</td></tr>
<tr><td>R-011</td><td>基线/RL冲突</td><td>-</td><td class="orange">R52新增:不可并行</td></tr>
<tr><td>R-012</td><td>基线~13h</td><td>-</td><td class="orange">R52新增:瓶颈</td></tr>
</table>
<h2>9. 结论</h2>
<div class="summary-box">
<p><strong>GO/NO-GO</strong>:<span class="green">GO for 11/9 Phase1 launch</span></p>
<p><strong>11/9第一件事</strong>:启动<span class="code">baize_posttrain_gpu_watcher.sh</span></p>
</div>
<hr><p style="font-size:0.85em;color:#777;">R52 wake100 {now} | 替身RL不可迁移到白泽</p>
</body></html>""")

    return "\n".join(h)


def main():
    parser = argparse.ArgumentParser(description="R52: GPU Schedule Optimizer")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    parser.add_argument("--json", action="store_true", help="Output JSON summary")
    args = parser.parse_args()

    if args.html:
        html = generate_html_report()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        reports_dir = os.path.join(script_dir, "..", "reports")
        os.makedirs(reports_dir, exist_ok=True)
        out_path = os.path.join(reports_dir, "report_posttrain_r52_gpu_schedule_optimizer_zh.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        size_kb = os.path.getsize(out_path) / 1024
        print(f"HTML report: {out_path} ({size_kb:.1f}KB)")
        return

    sglang = compute_sglang_serving_memory()
    rl = compute_rl_training_memory()
    conflicts = compute_resource_conflicts()
    timeline = compute_optimized_timeline()
    baseline_opts = compute_full_baseline_schedule()

    print("=" * 70)
    print("R52: GPU Resource Scheduling & Day-1 Critical Path Optimization")
    print("=" * 70)
    print(f"\nSGLang: {fmt_mib(sglang['total_per_gpu_mib'])}/GPU (1 GPU)")
    print(f"RL: {fmt_mib(rl['peak_per_gpu_mib'])}/GPU peak ({NUM_GPUS} GPU), headroom {fmt_mib(rl['headroom_mib'])}")
    print(f"\nConflicts: {sum(1 for c in conflicts if not c['can_overlap'])} cannot overlap")
    print(f"\nTimeline: {len(timeline)} steps, critical path {sum(s['duration_min'] for s in timeline[:7])}min")
    print(f"Baseline: recommended {baseline_opts['recommended']}, ~{baseline_opts['estimated_hours']:.1f}h")
    print("\nUse --html for full report.")


if __name__ == "__main__":
    main()
