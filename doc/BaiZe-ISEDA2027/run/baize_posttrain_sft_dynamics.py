#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""baize_posttrain_sft_dynamics.py — SFT Training Dynamics Prediction +
Anneal Blend Sensitivity + SFT→RL Handoff Protocol (R64)

Fills the gap between R6 (SFT high-level design) and R56 (data mixing pipeline)
by predicting concrete training dynamics, analyzing anneal blend sensitivity,
and defining the SFT→RL checkpoint handoff protocol.

Zero GPU, pure Python 3.8+ stdlib. No external dependencies.

Usage:
  python3 baize_posttrain_sft_dynamics.py --dry-run
  python3 baize_posttrain_sft_dynamics.py --html report_posttrain_r64_sft_dynamics_zh.html
  python3 baize_posttrain_sft_dynamics.py --json sft_dynamics.json
"""
import argparse
import json
import math
import os
import sys
import time
from collections import OrderedDict

MODELS = {
    "minicpm5-2b": {
        "name": "MiniCPM5-2B (surrogate for 11/9 rehearsal)",
        "params_B": 2.0, "hidden_dim": 2048, "num_layers": 42, "vocab_size": 73448,
        "is_real_baize": False,
        "note": "替身模型，用于11/9 GPU预演；结果不可迁移到白泽",
    },
    "baize-2b": {
        "name": "BaiZe-2B (real model, ETA pretrain ckpt ~2026-12-25)",
        "params_B": 2.0, "hidden_dim": 2048, "num_layers": 42, "vocab_size": 73448,
        "is_real_baize": True,
        "note": "白泽正式模型，Mamba2架构，从pretrain S1 ckpt resume",
    },
}

GPUS = {
    "a40": {"name": "A40", "memory_GB": 46, "bf16_tflops": 150, "bandwidth_GBps": 696},
    "h100": {"name": "H100", "memory_GB": 80, "bf16_tflops": 989, "bandwidth_GBps": 3350},
}

SFT_DATA = OrderedDict([
    ("general", {"source": "UltraData-SFT-2605", "tokens": 18_890_000_000, "role": "通用能力保持"}),
    ("agent", {"source": "UltraData-SFT-Agent-2609", "tokens": 5_970_000_000, "role": "工具调用能力"}),
    ("pyaether", {"source": "sft_pyaether_corpus_v2.jsonl (R24)", "tokens": 5_000_000, "role": "领域API知识"}),
    ("error_recovery", {"source": "S4 error-recovery subset", "tokens": 870_000, "role": "自纠错闭环"}),
])

ANNEAL_DATA = OrderedDict([
    ("domain", {"source": "PyAether API docs (8463 APIs)", "tokens": 5_000_000, "role": "领域先验注入"}),
    ("web", {"source": "mix_base", "tokens": 100_000_000_000, "role": "通用知识保持"}),
    ("code", {"source": "full_ultradata_code_l3", "tokens": 10_000_000_000, "role": "代码能力"}),
    ("math", {"source": "full_ultradata_math_l3", "tokens": 5_000_000_000, "role": "数学推理"}),
])

SFT_MIXES = OrderedDict([
    ("R6_default", {"general": 35, "agent": 30, "pyaether": 25, "error_recovery": 10,
                    "desc": "R6默认：通用35%+agentic30%+PyAether25%+错误恢复10%", "target": "M1->M2 (65%)"}),
    ("agent_heavy", {"general": 20, "agent": 45, "pyaether": 25, "error_recovery": 10,
                     "desc": "agentic加重：修D1/D2工具调用不足", "target": "M1 (50%) 优先"}),
    ("domain_heavy", {"general": 20, "agent": 25, "pyaether": 45, "error_recovery": 10,
                      "desc": "领域加重：修D4执行报错74%", "target": "M2 (65%) 优先"}),
    ("balanced", {"general": 30, "agent": 30, "pyaether": 25, "error_recovery": 15,
                  "desc": "均衡+错误恢复加重：修D6迭代不足", "target": "M1->M2 均衡"}),
    ("domain_max", {"general": 10, "agent": 20, "pyaether": 60, "error_recovery": 10,
                    "desc": "领域最大化消融", "target": "消融对照"}),
])

ANNEAL_BLENDS = OrderedDict([
    ("default", {"domain": 30, "web": 50, "code": 12, "math": 8,
                 "desc": "默认(anneal.sh占位)：领域30%+web50%+code12%+math8%", "expected_pp": "3-8"}),
    ("domain_heavy", {"domain": 50, "web": 30, "code": 12, "math": 8,
                      "desc": "领域加重：最大化API知识注入", "expected_pp": "5-12"}),
    ("domain_light", {"domain": 15, "web": 60, "code": 15, "math": 10,
                      "desc": "领域减轻：最小化遗忘风险", "expected_pp": "1-4"}),
    ("code_heavy", {"domain": 25, "web": 40, "code": 25, "math": 10,
                    "desc": "代码加重：补D4代码生成能力", "expected_pp": "3-8"}),
    ("no_anneal", {"domain": 0, "web": 60, "code": 25, "math": 15,
                   "desc": "无领域退火(对照组)", "expected_pp": "0 (对照)"}),
])


def estimate_sft_throughput(model_cfg, gpu_cfg, num_gpu, ctx_len, gbs, mbs):
    """Estimate SFT training throughput using a simplified roofline model."""
    params = model_cfg["params_B"] * 1e9
    tokens_per_step = gbs * ctx_len
    flops_per_step = 6 * params * tokens_per_step
    mfu_sft = 0.30  # SFT MFU: 30% of peak bf16 (lower than pretrain)
    total_tflops = gpu_cfg["bf16_tflops"] * num_gpu
    effective_flops_per_sec = total_tflops * mfu_sft * 1e12
    seconds_per_step = flops_per_step / effective_flops_per_sec if effective_flops_per_sec > 0 else float("inf")
    tokens_per_sec = tokens_per_step / seconds_per_step if seconds_per_step > 0 else 0
    steps_per_hour = 3600 / seconds_per_step if seconds_per_step > 0 else 0
    # Memory (bf16 training)
    model_mem_GB = 2 * model_cfg["params_B"]
    grad_mem_GB = 2 * model_cfg["params_B"]
    opt_mem_GB = 8 * model_cfg["params_B"]
    act_mem_GB = (12 * ctx_len * mbs * model_cfg["hidden_dim"] * model_cfg["num_layers"]) / 1e9
    total_mem_GB = model_mem_GB + grad_mem_GB + opt_mem_GB + act_mem_GB
    per_gpu_mem_GB = total_mem_GB / num_gpu
    # LoRA memory
    lora_params = model_cfg["params_B"] * 0.025
    lora_mem_GB = 12 * lora_params
    lora_total_GB = lora_mem_GB + 2 * model_cfg["params_B"] + act_mem_GB
    lora_per_gpu_GB = lora_total_GB / num_gpu
    return {
        "tokens_per_sec": tokens_per_sec,
        "seconds_per_step": seconds_per_step,
        "steps_per_hour": steps_per_hour,
        "tokens_per_step": tokens_per_step,
        "flops_per_step": flops_per_step,
        "mfu": mfu_sft,
        "memory_full": {"total_GB": total_mem_GB, "per_gpu_GB": per_gpu_mem_GB,
                         "fits": per_gpu_mem_GB < gpu_cfg["memory_GB"]},
        "memory_lora": {"total_GB": lora_total_GB, "per_gpu_GB": lora_per_gpu_GB,
                         "fits": lora_per_gpu_GB < gpu_cfg["memory_GB"]},
    }


def predict_training_time(throughput, total_steps, warmup, decay):
    """Predict training time for a given number of steps."""
    sps = throughput["seconds_per_step"]
    total_seconds = total_steps * sps
    total_tokens = total_steps * throughput["tokens_per_step"]
    return {
        "total_steps": total_steps,
        "seconds_per_step": sps,
        "total_seconds": total_seconds,
        "hours": total_seconds / 3600,
        "days": total_seconds / 86400,
        "total_tokens_consumed": total_tokens,
        "total_tokens_B": total_tokens / 1e9,
        "warmup_steps": warmup,
        "decay_steps": decay,
    }


def predict_loss_dynamics(model_cfg, total_tokens, data_tokens, sft_mix):
    """Predict SFT loss dynamics using Chinchilla-style scaling for SFT."""
    general_unique = min(data_tokens["general"] * 0.05, 2e9)
    agent_unique = min(data_tokens["agent"] * 0.3, 2e9)
    pyaether_unique = data_tokens["pyaether"]
    error_unique = data_tokens["error_recovery"]
    total_unique = general_unique + agent_unique + pyaether_unique + error_unique
    epochs = total_tokens / total_unique if total_unique > 0 else 0
    domain_pct = sft_mix.get("pyaether", 0) + sft_mix.get("error_recovery", 0)
    initial_loss = 2.8
    delta_loss = 0.8 * (1 - math.exp(-epochs / 1.5))
    final_loss = initial_loss - delta_loss
    domain_epochs = total_tokens * domain_pct / 100 / max(pyaether_unique + error_unique, 1)
    domain_final_ppl = max(4.5 - 1.2 * (1 - math.exp(-domain_epochs / 1.0)), 1.5)
    pyaether_epochs = total_tokens * domain_pct / 100 / max(pyaether_unique, 1)
    overfitting_risk = "high" if pyaether_epochs > 5 else ("medium" if pyaether_epochs > 3 else "low")
    return {
        "initial_loss": initial_loss, "final_loss": final_loss, "delta_loss": delta_loss,
        "total_unique_tokens": total_unique, "total_unique_B": total_unique / 1e9,
        "epochs": epochs, "domain_final_ppl": domain_final_ppl, "domain_epochs": domain_epochs,
        "pyaether_epochs": pyaether_epochs, "overfitting_risk": overfitting_risk,
    }


def analyze_anneal_blend(blend_name, blend, anneal_data, model_cfg, gpu_cfg, num_gpu):
    """Analyze a domain annealing blend configuration."""
    total_blend_tokens = 8_400_000_000  # 4000 steps * 4096 ctx * 512 GBS
    domain_tokens = total_blend_tokens * blend["domain"] / 100
    domain_unique = anneal_data["domain"]["tokens"]
    domain_coverage = domain_tokens / domain_unique if domain_unique > 0 else 0
    if blend["domain"] > 60:
        forgetting_risk = "high"
    elif blend["domain"] > 40:
        forgetting_risk = "medium"
    elif blend["domain"] > 0:
        forgetting_risk = "low"
    else:
        forgetting_risk = "none"
    anneal_throughput = estimate_sft_throughput(model_cfg, gpu_cfg, num_gpu, 4096, 512, 2)
    anneal_throughput["tokens_per_sec"] *= 1.4
    anneal_throughput["seconds_per_step"] /= 1.4
    anneal_throughput["steps_per_hour"] *= 1.4
    anneal_time = predict_training_time(anneal_throughput, 4000, 200, 400)
    return {
        "blend_name": blend_name, "desc": blend["desc"], "expected_pp": blend["expected_pp"],
        "ratios": blend, "domain_tokens": domain_tokens, "domain_tokens_M": domain_tokens / 1e6,
        "domain_coverage": domain_coverage, "forgetting_risk": forgetting_risk,
        "anneal_time_hours": anneal_time["hours"], "anneal_time_days": anneal_time["days"],
        "tokens_consumed_B": anneal_time["total_tokens_B"],
    }


def design_ablation_matrix():
    """Design the anneal-vs-no-anneal x SFT-mix ablation matrix."""
    full_cells = len(ANNEAL_BLENDS) * len(SFT_MIXES)
    ablations = [
        {"id": "A1", "name": "Baseline (no anneal + R6 default SFT)", "anneal": "no_anneal",
         "sft": "R6_default", "purpose": "下界基线：跳过退火，仅SFT", "expected": "M1 (50%)",
         "gpu_hours": 12, "priority": 1},
        {"id": "A2", "name": "Default anneal + R6 default SFT", "anneal": "default",
         "sft": "R6_default", "purpose": "主线配置：退火30% + SFT默认配比", "expected": "M2 (65%)",
         "gpu_hours": 18, "priority": 1},
        {"id": "A3", "name": "Domain-heavy anneal + R6 default SFT", "anneal": "domain_heavy",
         "sft": "R6_default", "purpose": "退火贡献上限：领域50% vs 30%", "expected": "M2+ (65-70%)",
         "gpu_hours": 18, "priority": 2},
        {"id": "A4", "name": "Default anneal + domain-heavy SFT", "anneal": "default",
         "sft": "domain_heavy", "purpose": "SFT配比贡献：PyAether45% vs 25%", "expected": "M2 (65%)",
         "gpu_hours": 18, "priority": 2},
        {"id": "A5", "name": "Default anneal + agent-heavy SFT", "anneal": "default",
         "sft": "agent_heavy", "purpose": "工具调用修复：agent45% vs 30%", "expected": "M1->M2",
         "gpu_hours": 18, "priority": 3},
        {"id": "A6", "name": "No anneal + domain-heavy SFT", "anneal": "no_anneal",
         "sft": "domain_heavy", "purpose": "退火vs SFT去耦：跳过退火但SFT领域加重", "expected": "M1-M2",
         "gpu_hours": 12, "priority": 3},
    ]
    total_gpu_hours = sum(a["gpu_hours"] for a in ablations)
    priority1_hours = sum(a["gpu_hours"] for a in ablations if a["priority"] == 1)
    priority2_hours = sum(a["gpu_hours"] for a in ablations if a["priority"] == 2)
    return {
        "full_matrix_cells": full_cells, "strategic_subset": len(ablations),
        "ablations": ablations, "total_gpu_hours": total_gpu_hours,
        "priority1_hours": priority1_hours, "priority2_hours": priority2_hours,
    }


def sft_rl_handoff_protocol():
    """Define the SFT->RL checkpoint handoff protocol."""
    return {
        "checkpoint_selection": {
            "criteria": [
                "1. eval Pass@1 >= M1 (50%) on 20-task subset",
                "2. SFT loss收敛(最后200步下降<5%)",
                "3. 无NaN/Inf in training log",
                "4. 工具调用合法率>80%(D1修复验证)",
                "5. 无严重过拟合(eval loss不高于train loss 50%+)",
            ],
            "selection_rule": "满足全部5条标准中选eval Pass@1最高的；相同则选step最小(泛化更好)",
            "save_interval": "每300步存1个ckpt(3000步共10个)",
        },
        "pre_rl_validation_gate": {
            "checks": [
                {"name": "Model load", "method": "SGLang serve SFT ckpt", "pass_criterion": "HTTP 200", "timeout": "5 min"},
                {"name": "Tool call format", "method": "10题tool-use prompt", "pass_criterion": ">=8/10格式合法", "timeout": "10 min"},
                {"name": "API knowledge", "method": "10题API查询", "pass_criterion": ">=7/10 API名正确", "timeout": "10 min"},
                {"name": "No degradation", "method": "20题full eval", "pass_criterion": "Pass@1>=36%", "timeout": "30 min"},
                {"name": "Cheat rate", "method": "PreToolUse hook全20题", "pass_criterion": "cheat_rate<5%(红线)", "timeout": "30 min"},
            ],
            "gate_logic": "全部5项PASS->GO for RL；任一FAIL->回退ckpt或重SFT；Cheat rate FAIL->硬停(红线)",
        },
        "rl_warmstart_config": {
            "lr_recommendation": "RL LR = SFT LR * 0.1 (2e-6 full, 1e-5 LoRA)",
            "kl_init": "0.05", "entropy_init": "0.8",
            "note": "SFT后模型已有工具格式知识，GRPO应重点优化语义正确性而非格式",
        },
    }


def _build_html_rows(cc, aa, ab, ho):
    """Build HTML table rows for the report."""
    def ok(b): return "ok" if b else "fail"
    def rk(r): return "ok" if r in ("low", "none") else ("warn" if r == "medium" else "fail")
    rctx = ""
    for c in cc:
        t, mf, ml = c["throughput"], c["throughput"]["memory_full"], c["throughput"]["memory_lora"]
        rctx += "<tr><td>%d</td><td>%d</td><td>%d</td><td>%s</td><td>%.1f</td><td>%.1f</td><td>%s</td><td>%.1f</td><td>%.1f</td><td class='%s'>%s</td><td class='%s'>%s</td></tr>" % (
            c['ctx_len'], c['gbs'], c['mbs'], format(t['tokens_per_step'], ','), t['seconds_per_step'],
            t['steps_per_hour'], format(t['tokens_per_sec'], ','), mf['per_gpu_GB'], ml['per_gpu_GB'],
            ok(mf['fits']), 'OK' if mf['fits'] else 'NO', ok(ml['fits']), 'OK' if ml['fits'] else 'NO')
    rtm = ""
    for c in cc:
        td, ld = c["time_pred"], c["loss_pred"]
        rtm += "<tr><td>%s</td><td>%d</td><td>%d</td><td>%.1fh</td><td>%.2fB</td><td>%.2fB</td><td>%.2f</td><td class='%s'>%s</td><td>%.2f</td></tr>" % (
            c['label'], c['ctx_len'], td['total_steps'], td['hours'], td['total_tokens_B'],
            ld['total_unique_B'], ld['epochs'], rk(ld['overfitting_risk']), ld['overfitting_risk'], ld['final_loss'])
    rls = ""
    for c in cc:
        ld = c["loss_pred"]
        rls += "<tr><td>%s</td><td>%.2f</td><td>%.2f</td><td>-%.2f</td><td>%.1f</td><td>4.5->%.1f</td><td class='%s'>%s</td></tr>" % (
            c['label'], ld['initial_loss'], ld['final_loss'], ld['delta_loss'],
            ld['pyaether_epochs'], ld['domain_final_ppl'], rk(ld['overfitting_risk']), ld['overfitting_risk'])
    ran = ""
    for a in aa:
        ran += "<tr><td>%s</td><td>%s</td><td>%d%%</td><td>%.1fM</td><td>%.1fx</td><td class='%s'>%s</td><td>%.1fh</td><td>%s</td></tr>" % (
            a['blend_name'], a['desc'], a['ratios']['domain'], a['domain_tokens_M'],
            a['domain_coverage'], rk(a['forgetting_risk']), a['forgetting_risk'], a['anneal_time_hours'], a['expected_pp'])
    rab = ""
    tc = {1: "tag-p1", 2: "tag-p2", 3: "tag-p3"}
    for a in ab["ablations"]:
        rab += "<tr><td><b>%s</b></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%dh</td><td><span class='tag %s'>P%d</span></td></tr>" % (
            a['id'], a['name'], a['anneal'], a['sft'], a['purpose'], a['expected'], a['gpu_hours'], tc.get(a['priority'], ''), a['priority'])
    rgt = ""
    for i, c in enumerate(ho["pre_rl_validation_gate"]["checks"], 1):
        rgt += "<tr><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (i, c['name'], c['method'], c['pass_criterion'], c['timeout'])
    rcs = ""
    for i, c in enumerate(ho["checkpoint_selection"]["criteria"], 1):
        rcs += "<tr><td>%d</td><td>%s</td></tr>" % (i, c)
    return rctx, rtm, rls, ran, rab, rgt, rcs


CSS_STYLE = '<style>body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;max-width:1100px;margin:0 auto;padding:20px;background:#f8f9fa;color:#2c3e50;line-height:1.6}h1{color:#1a1a2e;border-bottom:3px solid #e94560;padding-bottom:10px;font-size:1.5em}h2{color:#16213e;border-left:4px solid #e94560;padding-left:12px;margin-top:30px;font-size:1.25em}h3{color:#0f3460;font-size:1.1em;margin-top:20px}table{border-collapse:collapse;width:100%;margin:12px 0;font-size:0.9em}th,td{border:1px solid #ddd;padding:8px 10px;text-align:left}th{background:#16213e;color:#fff;font-weight:600}tr:nth-child(even){background:#f2f4f8}.ok{color:#27ae60;font-weight:600}.warn{color:#e67e22;font-weight:600}.fail{color:#e74c3c;font-weight:600}.note{background:#fff3cd;border:1px solid #ffeaa7;border-radius:6px;padding:12px;margin:10px 0}.redline{background:#fde8e8;border:1px solid #e74c3c;border-radius:6px;padding:12px;margin:10px 0}.summary-box{background:#e8f5e9;border:2px solid #27ae60;border-radius:8px;padding:16px;margin:15px 0}.metric{display:inline-block;background:#e3f2fd;padding:4px 10px;border-radius:4px;margin:2px;font-size:0.85em}code{background:#f0f0f0;padding:2px 6px;border-radius:3px;font-size:0.9em}.tag{display:inline-block;padding:2px 8px;border-radius:10px;font-size:0.8em;font-weight:600}.tag-p1{background:#e74c3c;color:#fff}.tag-p2{background:#e67e22;color:#fff}.tag-p3{background:#3498db;color:#fff}</style>'


def _html_part1(cc, aa, ab, model, gpu, ng, rctx, rtm, rls, ran, rab):
    p = []
    p.append('<!DOCTYPE html>\n<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">\n<title>R64 SFT动力学+退火配比+SFT->RL交接</title>')
    p.append(CSS_STYLE)
    p.append('</head><body>')
    p.append('<h1>R64：SFT训练动力学预测 + 退火配比敏感性 + SFT->RL交接协议</h1>')
    p.append('<div class="summary-box"><strong>摘要</strong>：填补R6(SFT方案)与R56(数据混合)之间的空白。预测%s在%dx%s(%dGB)上SFT训练动力学，分析5种退火配比，设计6格消融(~%dh)，定义SFT->RL交接(5项验证门)。<br><strong>关键结论</strong>：<span class="metric">ctx16384 SFT ~%.1fh</span><span class="metric">退火30%%覆盖率%.1fx</span><span class="metric">SFT->RL LR*0.1</span><span class="metric">A1+A2 P1 ~%dh</span></div>' % (model['name'], ng, gpu['name'], gpu['memory_GB'], ab['total_gpu_hours'], cc[2]['time_pred']['hours'], aa[0]['domain_coverage'], ab['priority1_hours']))
    p.append('<h2>1. SFT吞吐量估算</h2><p>模型：<strong>%s</strong>(%dB)；硬件：<strong>%dx%s</strong>(%dGB,%dTFLOPS)</p>' % (model['name'], model['params_B'], ng, gpu['name'], gpu['memory_GB'], gpu['bf16_tflops']))
    p.append('<table><tr><th>ctx</th><th>GBS</th><th>MBS</th><th>tok/step</th><th>秒/step</th><th>step/h</th><th>tok/s</th><th>全参GB</th><th>LoRA GB</th><th>全参</th><th>LoRA</th></tr>%s</table>' % rctx)
    p.append('<div class="note">全参ctx=16384需~%.0fGB/卡。A40在ctx&lt;=8192全参可行；ctx=16384需FSDP。LoRA全配置可行。MFU=30%%。</div>' % cc[2]['throughput']['memory_full']['per_gpu_GB'])
    p.append('<h2>2. 训练时间与Token预算</h2><table><tr><th>配置</th><th>ctx</th><th>步数</th><th>时间</th><th>Token</th><th>唯一Tok</th><th>Epochs</th><th>过拟合</th><th>loss</th></tr>%s</table>' % rtm)
    p.append('<div class="note">ctx=8192全参SFT(3000步)~%.1fh；ctx=16384~%.1fh。R60轨迹avg 28K tok，ctx=8192截断98%%。替身用ctx=8192 LoRA；白泽用ctx=16384全参。</div>' % (cc[1]['time_pred']['hours'], cc[2]['time_pred']['hours']))
    p.append('<h2>3. 损失动力学预测</h2><table><tr><th>配置</th><th>初始</th><th>最终</th><th>dL</th><th>PyAether ep</th><th>领域PPL</th><th>过拟合</th></tr>%s</table>' % rls)
    p.append('<div class="note">PyAether~5M token，3000步x16384xGBS128=~6.3B消耗下采样~300+次(25%%配比)。epochs&gt;5->高过拟合。缓解：降配比15-20%%；dropout；早停。</div>')
    p.append('<h2>4. 退火配比敏感性(5种)</h2><table><tr><th>配置</th><th>描述</th><th>领域%%</th><th>领域Tok</th><th>覆盖率</th><th>遗忘</th><th>退火时间</th><th>预期pp</th></tr>%s</table>' % ran)
    p.append('<div class="note">默认30%%->每个API文档%.1f次。50%%覆盖率%.1fx遗忘中等。主线default(30%%)，消融domain_heavy(50%%)。</div>' % (aa[0]['domain_coverage'], aa[1]['domain_coverage']))
    return '\n'.join(p)


def _html_part2(ab, rab, ho, rcs, rgt):
    p = []
    p.append('<h2>5. 消融矩阵(6格战略子集)</h2><div class="redline">所有臂共享污染隔离(158任务黑名单)+反作弊(PreToolUse hook)。评测158x5-runx2500s。</div>')
    p.append('<table><tr><th>ID</th><th>名称</th><th>退火</th><th>SFT</th><th>目的</th><th>预期</th><th>GPU-h</th><th>P</th></tr>%s</table>' % rab)
    p.append('<div class="summary-box">全矩阵%d格不可行(~300h)；6格~%dh。A1vsA2:退火贡献|A2vsA3:退火浓度|A2vsA4:SFT浓度|A1vsA6:退火可否被SFT替代。P1~%dh。</div>' % (ab['full_matrix_cells'], ab['total_gpu_hours'], ab['priority1_hours']))
    p.append('<h2>6. SFT->RL交接协议</h2>')
    p.append('<h3>6.1 检查点选择</h3><table><tr><th>#</th><th>标准</th></tr>%s</table>' % rcs)
    p.append('<p><strong>规则</strong>：%s；<strong>存盘</strong>：%s</p>' % (ho['checkpoint_selection']['selection_rule'], ho['checkpoint_selection']['save_interval']))
    p.append('<h3>6.2 RL前验证门(5项)</h3><table><tr><th>#</th><th>检查项</th><th>方法</th><th>通过标准</th><th>超时</th></tr>%s</table>' % rgt)
    p.append('<div class="redline"><strong>门控</strong>：%s</div>' % ho['pre_rl_validation_gate']['gate_logic'])
    p.append('<h3>6.3 RL热启动</h3><table><tr><th>参数</th><th>推荐</th><th>理由</th></tr>')
    p.append('<tr><td>RL LR</td><td><code>%s</code></td><td>SFT后需更小LR</td></tr>' % ho['rl_warmstart_config']['lr_recommendation'])
    p.append('<tr><td>KL</td><td><code>%s</code></td><td>SFT后KL低</td></tr>' % ho['rl_warmstart_config']['kl_init'])
    p.append('<tr><td>Entropy</td><td><code>%s</code></td><td>SFT降低entropy</td></tr></table>' % ho['rl_warmstart_config']['entropy_init'])
    p.append('<div class="note">%s</div>' % ho['rl_warmstart_config']['note'])
    p.append('<h2>7. 与11/9发射序列</h2>')
    p.append('<div class="note"><strong>11/9替身预演</strong>launch_11_9.sh Steps 0-7<strong>不含SFT</strong>——替身验证RL管线。<br><strong>白泽正式训练</strong>(12/25后)：退火(~6h)->SFT(~12-20h)->交接验证(~1h)->RL(~72h)->Post-RL eval(R63)。消融矩阵主训练后按优先级追加。</div>')
    p.append('<h2>8. 局限性</h2><ul><li>吞吐量MFU=30%%保守；实测+-30%%</li><li>损失动力学用经验公式</li><li>退火覆盖率假设均匀采样</li><li>过拟合基于PyAether~5M；扩展到20M+风险降</li><li>消融GPU-h未含评测(每臂~4-6h)</li><li>交接阈值需11/9实测校正</li><li>替身结果不可迁移白泽</li></ul>')
    p.append('<h2>9. 交付物</h2><table><tr><th>产物</th><th>路径</th></tr><tr><td>脚本</td><td><code>run/baize_posttrain_sft_dynamics.py</code></td></tr><tr><td>HTML</td><td><code>reports/report_posttrain_r64_sft_dynamics_zh.html</code></td></tr><tr><td>JSON</td><td><code>sft_dynamics.json</code></td></tr><tr><td>EXPERIMENTS</td><td><code>R64</code></td></tr></table>')
    p.append('<p style="text-align:center;color:#888;margin-top:30px;font-size:0.85em">R64-2026-11-08 wake112-零GPU-纯Python3.8+stdlib-溯源R6/R56/R60/R61/DATA_MAPPING-无伪造</p>')
    p.append('</body></html>')
    return '\n'.join(p)


def generate_html(results):
    cc = results["ctx_configs"]
    aa = results["anneal_analyses"]
    ab = results["ablation"]
    ho = results["handoff"]
    rctx, rtm, rls, ran, rab, rgt, rcs = _build_html_rows(cc, aa, ab, ho)
    return _html_part1(cc, aa, ab, results["model"], results["gpu"], results["num_gpu"], rctx, rtm, rls, ran, rab) + '\n' + _html_part2(ab, rab, ho, rcs, rgt)


def main():
    parser = argparse.ArgumentParser(description="R64: SFT Dynamics + Anneal Blend + SFT->RL Handoff")
    parser.add_argument("--model", default="baize-2b", choices=list(MODELS.keys()))
    parser.add_argument("--gpu", default="a40", choices=list(GPUS.keys()))
    parser.add_argument("--num-gpu", type=int, default=4)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", default=None)
    parser.add_argument("--html", default=None)
    args = parser.parse_args()
    model_cfg = MODELS[args.model]
    gpu_cfg = GPUS[args.gpu]
    ctx_configs = []
    for ctx_len, gbs, mbs, label in [
        (4096, 128, 2, "ctx4096"), (8192, 128, 1, "ctx8192"), (16384, 128, 1, "ctx16384")]:
        tp = estimate_sft_throughput(model_cfg, gpu_cfg, args.num_gpu, ctx_len, gbs, mbs)
        tm = predict_training_time(tp, 3000, 100, 300)
        ld = predict_loss_dynamics(model_cfg, tm["total_tokens_consumed"],
                                   {k: v["tokens"] for k, v in SFT_DATA.items()}, SFT_MIXES["R6_default"])
        ctx_configs.append({"label": label, "ctx_len": ctx_len, "gbs": gbs, "mbs": mbs,
                            "throughput": tp, "time_pred": tm, "loss_pred": ld})
    anneal_analyses = [analyze_anneal_blend(bn, b, ANNEAL_DATA, model_cfg, gpu_cfg, args.num_gpu)
                       for bn, b in ANNEAL_BLENDS.items()]
    ablation = design_ablation_matrix()
    handoff = sft_rl_handoff_protocol()
    results = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "model": model_cfg,
               "gpu": gpu_cfg, "num_gpu": args.num_gpu, "ctx_configs": ctx_configs,
               "anneal_analyses": anneal_analyses, "ablation": ablation, "handoff": handoff}
    if args.dry_run:
        print("=" * 70)
        print("R64 SFT Dynamics (%s, %dx%s)" % (model_cfg['name'], args.num_gpu, gpu_cfg['name']))
        print("=" * 70)
        for c in ctx_configs:
            t, tp, lp = c["throughput"], c["time_pred"], c["loss_pred"]
            mf, ml = t["memory_full"], t["memory_lora"]
            print("\n%s: %s tok/s, %.1f s/step" % (c['label'], format(t['tokens_per_sec'], ','), t['seconds_per_step']))
            print("  time: %.1fh, %.2fB tok" % (tp['hours'], tp['total_tokens_B']))
            print("  loss: %.2f->%.2f, overfit=%s" % (lp['initial_loss'], lp['final_loss'], lp['overfitting_risk']))
            print("  mem: full=%.1fGB(%s) lora=%.1fGB(%s)" % (mf['per_gpu_GB'], 'OK' if mf['fits'] else 'NO', ml['per_gpu_GB'], 'OK' if ml['fits'] else 'NO'))
        print("\nAnneal blends (%d):" % len(anneal_analyses))
        for a in anneal_analyses:
            print("  %-15s dom=%2d%% cov=%.1fx forget=%8s t=%.1fh" % (a['blend_name'], a['ratios']['domain'], a['domain_coverage'], a['forgetting_risk'], a['anneal_time_hours']))
        print("\nAblation (%d/%d):" % (ablation['strategic_subset'], ablation['full_matrix_cells']))
        for a in ablation["ablations"]:
            print("  %s P%d: %s (%dh)" % (a['id'], a['priority'], a['name'], a['gpu_hours']))
        print("  Total: %dh, P1: %dh" % (ablation['total_gpu_hours'], ablation['priority1_hours']))
        print("\nHandoff: %d criteria, %d gate checks" % (len(handoff['checkpoint_selection']['criteria']), len(handoff['pre_rl_validation_gate']['checks'])))
        print("  RL LR: %s" % handoff['rl_warmstart_config']['lr_recommendation'])
        print("\nOK dry-run complete.")
        return
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        print("JSON: %s" % args.json)
    if args.html:
        os.makedirs(os.path.dirname(args.html) or ".", exist_ok=True)
        with open(args.html, "w", encoding="utf-8") as f:
            f.write(generate_html(results))
        print("HTML: %s (%.1fKB)" % (args.html, os.path.getsize(args.html) / 1024))
    if not args.json and not args.html:
        print("Use --dry-run, --json, or --html")


if __name__ == "__main__":
    main()
