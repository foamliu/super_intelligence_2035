#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百三十九轮 · 按线建档（2026-11-08 起固定做法，见用户令 2026-11-07 10:50 §2/§3.2）。

读取候选池 `raw/2026-11-08-am-candidates-r139.json`，按 6 条在研线（pretrain / vision /
harness / data / zhulong / designflow）各自的**当前阻塞与在做的 2-3 件事**构造关键词表，
逐篇打分并输出每条线 top-N 候选，供「对各线的可执行建议」节直接取证。

用法：`python3 research/raw/line_match_r139.py [topN]`
"""
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
POOL = BASE / "raw" / "2026-11-08-am-candidates-r139.json"
TOPN = int(sys.argv[1]) if len(sys.argv) > 1 else 8

# 每条线 = (当前阻塞/在做什么 → 关键词, 权重)。命中权重高 = 更可能给出可落地建议。
LINES = {
    "pretrain": {
        "why": "CPU 6-chunk hellaswag 评测墙钟 + NUMA/HT 争用 + chunk 进度聚合（7/8 完成，ETA Nov9 07:00）",
        "kw": {
            "hellaswag": 6, "cpu": 4, "throughput": 5, "wall-clock": 5, "evaluat": 4,
            "benchmark suite": 4, "numa": 6, "thread": 4, "batch size": 4, "kv cache": 4,
            "long-context": 4, "long context": 4, "quantiz": 4, "mamba": 4, "hybrid": 3,
            "scaling law": 4, "pretrain": 3, "decoding": 3, "speculative": 3,
            "memory bandwidth": 4, "flag": 3, "framework": 3, "llama.cpp": 6, "gguf": 6,
        },
    },
    "harness": {
        "why": "SWE-bench predict 978/3500 + TB-2.1 7 路并行；gateway 429 归因；context 压缩与工具调用",
        "kw": {
            "swe-bench": 8, "terminal-bench": 8, "agent": 5, "tool call": 6, "tool-use": 6,
            "tool use": 6, "harness": 8, "scaffold": 5, "context compaction": 7,
            "context compress": 6, "context management": 6, "rate limit": 5, "retry": 4,
            "multi-agent": 4, "code agent": 6, "software engineering": 5, "repository": 4,
            "docker": 3, "sandbox": 4, "trajectory": 4, "cost": 3, "token budget": 4,
            "resume": 4, "rollout": 3,
        },
    },
    "data": {
        "why": "代码语料 ROI 下载 + 数据配比/去污染 + stack-v3 待批（单集 <1TB 放行）",
        "kw": {
            "data mixture": 8, "data mix": 8, "mixture": 5, "deduplicat": 8, "decontaminat": 8,
            "contamination": 7, "data quality": 7, "code corpus": 8, "filtering": 5,
            "synthetic data": 5, "curriculum": 5, "data selection": 7, "tokenizer": 4,
            "dataset": 4, "data-centric": 5, "quality classifier": 6, "pretraining data": 7,
            "scaling": 3, "sample efficiency": 4, "annotation": 3,
        },
    },
    "zhulong": {
        "why": "cline --thinking 档位 × 思维链语言两轴消融（A_medium_r2 跑中，23 轮剩余，~1.9 天）",
        "kw": {
            "thinking budget": 8, "thinking": 6, "reasoning effort": 8, "chain-of-thought": 6,
            "chain of thought": 6, "inference cost": 7, "token cost": 7, "cost-aware": 6,
            "multilingual": 6, "language": 5, "cross-lingual": 6, "ablation": 7,
            "test-time compute": 6, "pass@k": 4, "variance": 4, "significance": 5,
            "confidence interval": 5, "repeated runs": 5, "agent evaluation": 6,
            "evaluation protocol": 6, "budget": 4, "temperature": 4,
        },
    },
    "designflow": {
        "why": "造题（30/1001 trace 覆盖）+ 断言闸门（k_rationale vs k_check≥8）+ 可验证判分",
        "kw": {
            "verifiable": 7, "rubric": 7, "llm-as-judge": 7, "llm as judge": 7, "judge": 5,
            "unit test": 6, "test generation": 7, "spec": 4, "specification": 5,
            "eda": 8, "rtl": 8, "verilog": 8, "netlist": 8, "layout": 6, "timing": 5,
            "formal verification": 7, "assertion": 7, "checker": 6, "case generation": 7,
            "benchmark construction": 7, "task synthesis": 6, "grading": 6, "consistency": 4,
        },
    },
    "vision": {
        "why": "波形 RL 奖励设计（v5 A16%→B37%→C53%，McNemar p=0.0009 已达标）+ CPU 小样本显著性",
        "kw": {
            "waveform": 9, "signal": 5, "time series": 6, "time-series": 6, "lora": 7,
            "reinforcement learning": 5, "reward": 6, "reward design": 8, "small sample": 7,
            "few-shot": 5, "statistical significan": 7, "mcnemar": 8, "bootstrap": 6,
            "classification": 4, "speech": 5, "audio": 4, "vibration": 6, "sensor": 6,
            "gpu-free": 6, "cpu-only": 7, "cheat": 4,
        },
    },
}


def score(item, kw):
    text = (item["title"] + " " + item["summary"]).lower()
    hits = []
    total = 0
    for k, w in kw.items():
        if k in text:
            total += w
            hits.append("%s(%d)" % (k, w))
    return total, hits


def main():
    pool = json.loads(POOL.read_text(encoding="utf-8"))
    items = pool["fresh"]
    print("POOL fresh=%d  generated=%s  min_published=%s" % (
        pool["n_fresh"], pool["generated"], pool["min_published"]))
    for line, cfg in LINES.items():
        scored = []
        for it in items:
            s, hits = score(it, cfg["kw"])
            if s >= 8:
                scored.append((s, it, hits))
        scored.sort(key=lambda x: (-x[0], x[1]["published"]))
        print("\n" + "=" * 100)
        print("### %s  (匹配 %d 篇)  —— 当前重点：%s" % (line, len(scored), cfg["why"]))
        for s, it, hits in scored[:TOPN]:
            print("  [%3d] %s  %s  %s" % (s, it["arxiv_id"], it["published"][:10], it["category"]))
            print("        %s" % it["title"][:150])
            print("        hits: %s" % ", ".join(hits))
            print("        inst: %s" % (it["authors"][0] if it["authors"] else "-"))


if __name__ == "__main__":
    main()
