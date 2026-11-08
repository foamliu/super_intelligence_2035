#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百四十一轮 · 按线建档（固定做法，见用户令 2026-11-07 10:50 §2/§3.2）。

复用 r139 候选池 `raw/2026-11-08-am-candidates-r139.json`（周末批次未刷新、无需重取），
剔除已收录（SEEN.md）后，按 6 条在研线**当轮阻塞/在做的 2-3 件事**构造关键词表逐篇打分，
输出每条线 top-N，供「对各线的可执行建议」节取证。

用法：`python3 research/raw/line_match_r141.py [topN]`
"""
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
POOL = BASE / "raw" / "2026-11-08-am-candidates-r139.json"
TOPN = int(sys.argv[1]) if len(sys.argv) > 1 else 8

# 阻塞口径（2026-11-09 06:00 各线 MEMORY 顶部实读）
LINES = {
    "pretrain": {
        "why": "v6 全量 eval 8 集收官（Avg6=53.38%，hellaswag 4 chunk 剩 20–67%，chunk1 26.9s/it 为瓶颈、NUMA/同 server 争用）+ 37.40% 异常报告已出结论A（口径问题）",
        "kw": {
            "hellaswag": 6, "cpu": 4, "throughput": 5, "wall-clock": 5, "wall clock": 5,
            "evaluat": 4, "benchmark suite": 4, "numa": 6, "thread": 4, "batch size": 4,
            "kv cache": 4, "long-context": 4, "long context": 4, "quantiz": 4, "mamba": 4,
            "hybrid": 3, "scaling law": 4, "pretrain": 3, "decoding": 3, "speculative": 3,
            "memory bandwidth": 4, "llama.cpp": 6, "gguf": 6, "few-shot": 4, "variance": 3,
            "measurement": 4, "reproduc": 5, "contamination": 3,
        },
    },
    "harness": {
        "why": "SWE-bench predict 5 路 alive 2520/3500（72%）+ TB-2.1 3 harbor；gateway 429 归因、context 压缩、重试与成本",
        "kw": {
            "swe-bench": 8, "terminal-bench": 8, "terminal bench": 8, "agent": 5,
            "tool call": 6, "tool-use": 6, "tool use": 6, "harness": 8, "scaffold": 5,
            "context compaction": 7, "context compress": 6, "context management": 6,
            "rate limit": 5, "retry": 4, "multi-agent": 4, "code agent": 6,
            "software engineering": 5, "repository": 4, "sandbox": 4, "trajectory": 4,
            "cost": 3, "token budget": 4, "resume": 4, "rollout": 3, "patch": 4,
            "docker": 3, "cli": 3, "long-horizon": 5,
        },
    },
    "data": {
        "why": "stack-v3-train 2TB batch4 下载中；代码语料质量筛 + 配比 + 去污染（单集 <1TB 放行）",
        "kw": {
            "data mixture": 8, "data mix": 8, "mixture": 5, "deduplicat": 8,
            "decontaminat": 8, "contamination": 7, "data quality": 7, "code corpus": 8,
            "filtering": 5, "synthetic data": 5, "curriculum": 5, "data selection": 7,
            "tokenizer": 4, "dataset": 4, "data-centric": 5, "quality classifier": 6,
            "pretraining data": 7, "sample efficiency": 4, "annotation": 3,
            "code generation data": 6, "license": 3,
        },
    },
    "zhulong": {
        "why": "cline --thinking 档位 × 思维链语言两轴消融 14/30（A_xhigh_r3 跑中）；报告须含分数 + 成本（墙钟/token）+ 显著性",
        "kw": {
            "thinking budget": 8, "thinking": 6, "reasoning effort": 8,
            "chain-of-thought": 6, "chain of thought": 6, "inference cost": 7,
            "token cost": 7, "cost-aware": 6, "multilingual": 6, "cross-lingual": 6,
            "ablation": 7, "test-time compute": 6, "pass@k": 4, "pass@1": 4, "variance": 4,
            "significance": 5, "confidence interval": 5, "repeated runs": 5,
            "agent evaluation": 6, "evaluation protocol": 6, "budget": 4,
            "temperature": 4, "overthinking": 7, "reasoning length": 6,
        },
    },
    "designflow": {
        "why": "造题 trace 覆盖 25/1001=2.5% + 断言闸门（k_check≥8、rationale 对账）+ L1/L2 判分可验证性",
        "kw": {
            "verifiable": 7, "rubric": 7, "llm-as-judge": 7, "llm as judge": 7, "judge": 5,
            "unit test": 6, "test generation": 7, "specification": 5, "eda": 8, "rtl": 8,
            "verilog": 8, "netlist": 8, "layout": 6, "timing": 5, "formal verification": 7,
            "assertion": 7, "checker": 6, "case generation": 7,
            "benchmark construction": 7, "task synthesis": 6, "grading": 6,
            "circuit": 6, "hardware": 5, "hdl": 6, "dataflow": 5,
        },
    },
    "vision": {
        "why": "阶段2 CPU 试 idea 已交付 v5（A16%→C53%，p=0.0009）；下一步=连续奖励标定 / 换基座 Qwen3.5-2B / LoRA 与课程学习、小样本显著性",
        "kw": {
            "waveform": 9, "signal": 5, "time series": 6, "time-series": 6, "lora": 7,
            "reinforcement learning": 5, "reward": 6, "reward design": 8,
            "small sample": 7, "few-shot": 5, "statistical significan": 7, "mcnemar": 8,
            "bootstrap": 6, "classification": 4, "speech": 5, "audio": 4, "vibration": 6,
            "sensor": 6, "gpu-free": 6, "cpu-only": 7, "cheat": 4, "grpo": 7,
            "curriculum": 5, "distillation": 4,
        },
    },
}


def score(item, kw):
    text = (item["title"] + " " + item["summary"]).lower()
    hits, total = [], 0
    for k, w in kw.items():
        if k in text:
            total += w
            hits.append("%s(%d)" % (k, w))
    return total, hits


def load_seen():
    seen = set()
    for ln in (BASE / "SEEN.md").read_text(encoding="utf-8").splitlines():
        if ln.startswith("|"):
            parts = [p.strip() for p in ln.strip("|").split("|")]
            if len(parts) >= 2 and parts[1].count(".") == 1:
                seen.add(parts[1])
    return seen


def main():
    pool = json.loads(POOL.read_text(encoding="utf-8"))
    seen = load_seen()
    items = [it for it in pool["fresh"] if it["arxiv_id"] not in seen]
    print("POOL fresh=%d  seen_removed=%d  usable=%d  min_published=%s" % (
        pool["n_fresh"], pool["n_fresh"] - len(items), len(items), pool["min_published"]))
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
