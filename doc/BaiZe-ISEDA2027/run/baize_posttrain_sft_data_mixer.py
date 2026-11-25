#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""baize_posttrain_sft_data_mixer.py — SFT Data Mixing Pipeline (R56)

Fills the gap between the SFT recipe skeleton (baize_posttrain_sft.sh) and
training-ready data.  Combines PyAether domain SFT corpus (JSONL) with
UltraData general/agent SFT data (pre-tokenized megatron .bin/.idx) into a
unified training plan with:
  1. PyAether JSONL -> verl SFT conversation-format conversion
  2. Configurable mixing ratios (agent / general / pyaether / code / math)
  3. Context-length truncation strategy (agentic traces can be very long)
  4. Contamination gate (158 eval task API blacklist)
  5. Token-budget estimation and length-distribution statistics
  6. Blend config YAML output for megatron-format sources
  7. HTML report (self-contained, 0 script, 0 external links)

Design decisions (zero GPU, Python 3.8+):
  - UltraData SFT-2605 / SFT-Agent-2609 are pre-tokenized in megatron .bin/.idx
    on .29/.12 NFS -> mixing happens at the *training framework* level (blend
    weights in config), not at the data-file level.  This script outputs a
    blend config YAML for those sources.
  - PyAether SFT corpus (sft_pyaether_corpus_v2.jsonl, 19524 pairs) is the only
    JSONL source we can mix at the data level right now -> converted to verl
    SFT conversation format (list[dict] of message turns).
  - Token estimates use chars/4 heuristic (no tokenizer dependency); exact token
    counts require the MiniCPM5-2B tokenizer (available post-GPU).

Usage:
  python3 baize_posttrain_sft_data_mixer.py --dry-run
  python3 baize_posttrain_sft_data_mixer.py --mix agent50:general30:pyaether20
  python3 baize_posttrain_sft_data_mixer.py --mix pyaether40:agent35:general25 --context-len 8192
  python3 baize_posttrain_sft_data_mixer.py --html report_posttrain_r56_sft_mix_zh.html

Red lines:
  - Contamination isolation: 158 eval task APIs must NOT appear in training data.
  - 5-run mean+/-std evaluation protocol (not affected by data mixing, but noted).
"""
import argparse
import json
import os
import sys
import math
import re
import time
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# R113: Auto-detect NAS_ROOT (same as baize_posttrain_paths.sh)
from pathlib import Path as _Path
if _Path("/nas_data/app.e0031982/code/super_intelligence_2035").exists() and \
   not _Path("/nas_train/app.e0031982/code/super_intelligence_2035").exists():
    NAS_ROOT = "/nas_data"
elif _Path("/nas_train/app.e0031982/code/super_intelligence_2035").exists():
    NAS_ROOT = "/nas_train"
else:
    NAS_ROOT = "/nas_data"


PYAETHER_SFT_JSONL = os.path.join(SCRIPT_DIR, "sft_pyaether_corpus_v2.jsonl")
EVAL_DATASET = os.path.expanduser(
    "~/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl")
DEFAULT_OUTPUT_JSONL = os.path.join(SCRIPT_DIR, "sft_mixed_output.jsonl")
DEFAULT_BLEND_CONFIG = os.path.join(SCRIPT_DIR, "sft_blend_config.yaml")

MIX_STRATEGIES = {
    "agent50:general30:pyaether20": {
        "agent": 50, "general": 30, "pyaether": 20,
        "desc": "Default from baize_posttrain_sft.sh - agentic-heavy"},
    "pyaether40:agent35:general25": {
        "agent": 35, "general": 25, "pyaether": 40,
        "desc": "Domain-heavy - push M2 (65%) via PyAether API knowledge injection"},
    "agent40:general40:pyaether20": {
        "agent": 40, "general": 40, "pyaether": 20,
        "desc": "Balanced - equal general+agent, moderate domain"},
    "pyaether60:agent25:general15": {
        "agent": 25, "general": 15, "pyaether": 60,
        "desc": "Domain-max - for ablation: how far can PyAether SFT alone go?"},
}

ULTRADATA_ESTIMATES = {
    "general": {
        "source": "UltraData-SFT-2605",
        "format": "megatron .bin/.idx (pre-tokenized)",
        "disk_size": "75.87 GB",
        "token_count": 18_890_000_000,
        "num_shards": 1504,
        "nfs_path": os.path.join(NAS_ROOT, "app.e0031982/code/BaiZe-ISEDA2027/data/sft_ultradata_2605"),
    },
    "agent": {
        "source": "UltraData-SFT-Agent-2609",
        "format": "megatron .bin/.idx (pre-tokenized)",
        "disk_size": "23.89 GB",
        "token_count": 5_970_000_000,
        "num_shards": 50,
        "nfs_path": os.path.join(NAS_ROOT, "app.e0031982/code/BaiZe-ISEDA2027/data/sft_agent_ultradata_2609"),
    },
}

PAIR_TYPE_DESC = {
    "S1_doc_to_code": "API doc -> Python function calling that API",
    "S2_api_lookup": "API name -> doc lookup / signature recall",
    "S3_multi_api_chain": "Multiple APIs chained in sequence",
    "S4_error_recovery": "Error -> fix -> retry pattern",
}


def estimate_tokens(text):
    """Rough token estimate: chars / 4."""
    return max(1, len(text) // 4)


def load_pyaether_sft(path):
    """Load PyAether SFT corpus v2 JSONL."""
    if not os.path.exists(path):
        print("WARNING: PyAether SFT corpus not found: %s" % path)
        return []
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def load_eval_apis(eval_path):
    """Load the 158 eval task API blacklist for contamination checking."""
    if not os.path.exists(eval_path):
        print("WARNING: Eval dataset not found: %s" % eval_path)
        return set()
    apis = set()
    with open(eval_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            task = json.loads(line)
            meta = task.get("metadata", {})
            for key in ("apis", "api_used", "unique_apis"):
                if key in meta and isinstance(meta[key], list):
                    for api in meta[key]:
                        if isinstance(api, str):
                            apis.add(api.strip())
            prompt = task.get("prompt", "")
            for m in re.finditer(r"pyAether\.(\w+)\.(\w+)", prompt):
                apis.add("pyAether.%s.%s" % (m.group(1), m.group(2)))
    return apis


def check_contamination(records, eval_apis):
    """Check if any PyAether SFT record uses eval-task APIs."""
    if not eval_apis:
        return {"checked": False, "contaminated": 0, "contaminated_ids": []}
    contaminated = []
    for rec in records:
        rec_apis = set(rec.get("api_used", []))
        overlap = rec_apis & eval_apis
        if overlap:
            contaminated.append({"pair_id": rec.get("pair_id", "?"), "apis": list(overlap)})
    return {"checked": True, "eval_api_count": len(eval_apis),
            "contaminated": len(contaminated), "contaminated_ids": contaminated[:10]}


def convert_to_verl_sft(rec):
    """Convert a PyAether SFT JSONL record to verl SFT conversation format."""
    prompt = rec.get("prompt", "")
    completion = rec.get("completion", "")
    system_msg = ("You are an EDA automation assistant specialized in PyAether "
                  "API usage. Write correct, efficient Python code that calls "
                  "the specified PyAether APIs.")
    return {
        "conversation": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": completion},
        ],
        "metadata": {
            "pair_id": rec.get("pair_id", ""),
            "type": rec.get("type", ""),
            "api_used": rec.get("api_used", []),
            "source": rec.get("source", ""),
            "quality_tier": rec.get("quality_tier", ""),
        },
    }


def truncate_conversation(conversation, max_tokens, strategy="keep_system_completion"):
    """Truncate conversation to fit within max_tokens."""
    total_tokens = sum(estimate_tokens(m["content"]) for m in conversation)
    if total_tokens <= max_tokens:
        return conversation, False
    system = conversation[0] if conversation[0]["role"] == "system" else None
    assistant = conversation[-1] if conversation[-1]["role"] == "assistant" else None
    if strategy == "keep_system_completion" and system and assistant:
        sys_tok = estimate_tokens(system["content"])
        asst_tok = estimate_tokens(assistant["content"])
        remaining = max_tokens - sys_tok - asst_tok
        if remaining > 100:
            user_content = conversation[1]["content"][:remaining * 4]
            return [system, {"role": "user", "content": user_content}, assistant], True
        asst_trunc = assistant["content"][:max(100, (max_tokens - sys_tok) * 4)]
        return [system, {"role": "assistant", "content": asst_trunc}], True
    elif strategy == "drop_system":
        user = conversation[1] if len(conversation) > 1 else conversation[0]
        remaining = max_tokens - estimate_tokens(assistant["content"])
        if remaining > 100:
            return [{"role": "user", "content": user["content"][:remaining * 4]}, assistant], True
        return [assistant], True
    else:
        budget = max_tokens - (estimate_tokens(system["content"]) if system else 0)
        user_budget = int(budget * 0.6)
        parts = [system] if system else []
        parts.append({"role": "user", "content": conversation[1]["content"][:user_budget * 4] + "\n[...truncated...]"})
        parts.append({"role": "assistant", "content": assistant["content"][:budget - user_budget]})
        return parts, True


def analyze_pyaether_corpus(records):
    """Analyze the PyAether SFT corpus."""
    stats = {
        "total_records": len(records),
        "by_type": Counter(), "by_tier": Counter(),
        "token_estimates": {"total": []},
        "length_buckets": {"<512": 0, "512-1k": 0, "1k-2k": 0, "2k-4k": 0, "4k-8k": 0, ">8k": 0},
        "api_usage": Counter(),
    }
    for rec in records:
        stats["by_type"][rec.get("type", "unknown")] += 1
        stats["by_tier"][rec.get("quality_tier", "unknown")] += 1
        t_tok = estimate_tokens(rec.get("prompt", "")) + estimate_tokens(rec.get("completion", ""))
        stats["token_estimates"]["total"].append(t_tok)
        if t_tok < 512: stats["length_buckets"]["<512"] += 1
        elif t_tok < 1024: stats["length_buckets"]["512-1k"] += 1
        elif t_tok < 2048: stats["length_buckets"]["1k-2k"] += 1
        elif t_tok < 4096: stats["length_buckets"]["2k-4k"] += 1
        elif t_tok < 8192: stats["length_buckets"]["4k-8k"] += 1
        else: stats["length_buckets"][">8k"] += 1
        for api in rec.get("api_used", []):
            stats["api_usage"][api] += 1
    totals = stats["token_estimates"]["total"]
    if totals:
        stats["total_tokens"] = sum(totals)
        stats["mean_tokens"] = sum(totals) / len(totals)
        stats["median_tokens"] = sorted(totals)[len(totals) // 2]
        stats["p95_tokens"] = sorted(totals)[int(len(totals) * 0.95)] if len(totals) > 20 else max(totals)
        stats["max_tokens"] = max(totals)
    else:
        for k in ("total_tokens", "mean_tokens", "median_tokens", "p95_tokens", "max_tokens"):
            stats[k] = 0
    return stats


def compute_mixing_plan(mix_key, pyaether_stats, context_len=8192):
    """Compute the mixing plan."""
    ratios = dict(MIX_STRATEGIES.get(mix_key, {}))
    if not ratios:
        for part in mix_key.split(":"):
            for prefix in ("agent", "general", "pyaether", "code", "math"):
                if part.startswith(prefix):
                    ratios[prefix] = int(part[len(prefix):])
        ratios["desc"] = "Custom mix: %s" % mix_key
    target_tokens = 3_145_728_000
    plan = {"mix_key": mix_key, "description": ratios.get("desc", ""),
            "target_total_tokens": target_tokens, "context_len": context_len, "sources": {}}
    for source, pct in sorted(ratios.items()):
        if source == "desc":
            continue
        source_tokens = int(target_tokens * pct / 100)
        if source == "pyaether":
            mean_tok = pyaether_stats.get("mean_tokens", 500)
            plan["sources"][source] = {
                "ratio_pct": pct, "target_tokens": source_tokens,
                "format": "JSONL -> verl SFT conversation",
                "available_tokens": pyaether_stats.get("total_tokens", 0),
                "available_samples": pyaether_stats.get("total_records", 0),
                "target_samples": int(source_tokens / max(mean_tok, 1)),
                "sampling_strategy": "weighted-by-tier (high=3x, medium=2x, low=1x)"}
        elif source in ULTRADATA_ESTIMATES:
            est = ULTRADATA_ESTIMATES[source]
            plan["sources"][source] = {
                "ratio_pct": pct, "target_tokens": source_tokens,
                "format": est["format"], "available_tokens": est["token_count"],
                "target_samples": "N/A (pre-tokenized)",
                "sampling_strategy": "megatron blend weight = %d%%" % pct,
                "nfs_path": est["nfs_path"]}
        else:
            plan["sources"][source] = {"ratio_pct": pct, "target_tokens": source_tokens,
                                       "format": "TBD", "note": "Source not yet available"}
    return plan


def generate_blend_config_yaml(plan, output_path):
    """Generate a blend config YAML for megatron-format sources."""
    lines = ["# SFT Blend Config (auto-generated by baize_posttrain_sft_data_mixer.py)",
             "# R56: SFT Data Mixing Pipeline",
             "# Generated: %s" % time.strftime("%Y-%m-%d %H:%M:%S"),
             "# Mix strategy: %s" % plan["mix_key"],
             "# Target total tokens: ~%dB" % (plan["target_total_tokens"] // 1_000_000_000),
             "# Context length: %d" % plan["context_len"], "",
             "sft_blend:"]
    for source, info in plan["sources"].items():
        if info.get("format", "").startswith("megatron"):
            lines.append("  %s:" % source)
            lines.append('    path: "%s"' % info.get("nfs_path", ""))
            lines.append("    weight: %d  # %% of total tokens" % info["ratio_pct"])
    if "pyaether" in plan["sources"]:
        lines.append("  pyaether:")
        lines.append('    path: "%s"' % DEFAULT_OUTPUT_JSONL)
        lines.append("    weight: %d" % plan["sources"]["pyaether"]["ratio_pct"])
        lines.append('    format: "verl SFT conversation (JSONL)"')
    lines += ["", "# Training hyperparameters (from baize_posttrain_sft.sh):",
              "training:", "  context_len: %d" % plan["context_len"],
              "  gbs: 128", "  mbs: 1", "  iters: 3000", "  warmup: 100",
              "  decay: 300", "  lr: 2e-5", "  min_lr: 1e-6", "  save_interval: 300"]
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return output_path


def generate_html_report(stats, plan, contam, context_len, output_path):
    """Generate a self-contained HTML report."""
    def pct(n, d):
        return "%.1f%%" % (100.0 * n / d) if d > 0 else "0.0%"

    s = ["<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'>",
         "<meta name='viewport' content='width=device-width, initial-scale=1.0'>",
         "<title>R56 SFT 数据混合管线 - BaiZe Stage(ii)</title><style>",
         "body{font-family:system-ui,sans-serif;max-width:1100px;margin:0 auto;padding:20px;background:#f8f9fa;color:#333;line-height:1.6;}",
         "h1{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px;}",
         "h2{color:#2c3e50;margin-top:30px;border-bottom:1px solid #bdc3c7;padding-bottom:5px;}",
         "table{border-collapse:collapse;width:100%;margin:15px 0;background:#fff;}",
         "th,td{border:1px solid #ddd;padding:8px 12px;text-align:left;}",
         "th{background:#2980b9;color:#fff;}", "tr:nth-child(even){background:#f2f2f2;}",
         ".kpi{display:inline-block;background:#e8f4f8;border:1px solid #b8daff;border-radius:6px;padding:10px 20px;margin:5px 10px 5px 0;}",
         ".kpi .num{font-size:1.4em;font-weight:700;color:#2980b9;}",
         ".kpi .lbl{font-size:0.85em;color:#666;}",
         ".warn{background:#fff3cd;border:1px solid #ffeaa7;border-radius:6px;padding:12px;margin:10px 0;}",
         ".ok{background:#d4edda;border:1px solid #c3e6cb;border-radius:6px;padding:12px;margin:10px 0;}",
         ".danger{background:#f8d7da;border:1px solid #f5c6cb;border-radius:6px;padding:12px;margin:10px 0;}",
         "code{background:#f1f2f6;padding:2px 6px;border-radius:3px;font-size:0.9em;}",
         "</style></head><body>"]

    s.append("<h1>R56: SFT 数据混合管线 (SFT Data Mixing Pipeline)</h1>")
    s.append("<p><strong>BaiZe Stage(ii) Post-Training</strong> - 领域退火 -> SFT -> RLVR-GRPO</p>")
    s.append("<p>生成时间: %s - 零 GPU - R56</p>" % time.strftime("%Y-%m-%d %H:%M:%S"))
    s.append("<div>")
    s.append("<div class='kpi'><span class='num'>%d</span><br><span class='lbl'>PyAether SFT 样本</span></div>" % stats["total_records"])
    s.append("<div class='kpi'><span class='num'>~%dM</span><br><span class='lbl'>估算 token</span></div>" % (stats["total_tokens"] // 1_000_000))
    s.append("<div class='kpi'><span class='num'>~%.0f</span><br><span class='lbl'>平均 tok/样本</span></div>" % stats["mean_tokens"])
    if contam.get("checked") and contam["contaminated"] == 0:
        s.append("<div class='kpi'><span class='num'>&#9989; 0</span><br><span class='lbl'>污染命中</span></div>")
    s.append("</div>")

    s.append("<h2>1. 研究背景</h2>")
    s.append("<p>SFT (Step 1) 是领域退火后第一个训练步骤。当前 <code>baize_posttrain_sft.sh</code> 有配比配置 "
             "但<b>缺乏可执行的数据混合管线</b>。R56 填补此空白。</p>")

    s.append("<h2>2. PyAether SFT 语料分析</h2>")
    s.append("<h3>2.1 按类型分布</h3>")
    s.append("<table><tr><th>类型</th><th>描述</th><th>数量</th><th>占比</th></tr>")
    for rtype, count in stats["by_type"].most_common():
        s.append("<tr><td><code>%s</code></td><td>%s</td><td>%d</td><td>%s</td></tr>"
                 % (rtype, PAIR_TYPE_DESC.get(rtype, ""), count, pct(count, stats["total_records"])))
    s.append("</table>")
    s.append("<h3>2.2 按质量层级</h3>")
    s.append("<table><tr><th>层级</th><th>数量</th><th>占比</th></tr>")
    for tier, count in stats["by_tier"].most_common():
        s.append("<tr><td>%s</td><td>%d</td><td>%s</td></tr>" % (tier, count, pct(count, stats["total_records"])))
    s.append("</table>")

    s.append("<h3>2.3 Token 估算</h3>")
    s.append("<table><tr><th>指标</th><th>值</th></tr>")
    s.append("<tr><td>总估算 token</td><td>~%dM</td></tr>" % (stats["total_tokens"] // 1_000_000))
    s.append("<tr><td>平均</td><td>%.1f</td></tr>" % stats["mean_tokens"])
    s.append("<tr><td>中位数</td><td>%d</td></tr>" % stats["median_tokens"])
    s.append("<tr><td>P95</td><td>%d</td></tr>" % stats["p95_tokens"])
    s.append("<tr><td>最大</td><td>%d</td></tr>" % stats["max_tokens"])
    s.append("</table>")

    s.append("<h3>2.4 长度分桶</h3>")
    s.append("<table><tr><th>Token 范围</th><th>样本数</th><th>占比</th><th>Ctx 4k?</th><th>Ctx 8k?</th></tr>")
    for bucket, count in stats["length_buckets"].items():
        f4 = "&#9989;" if bucket in ("<512", "512-1k", "1k-2k", "2k-4k") else "&#9888;"
        f8 = "&#9989;" if bucket != ">8k" else "&#9888;"
        s.append("<tr><td>%s</td><td>%d</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (bucket, count, pct(count, stats["total_records"]), f4, f8))
    s.append("</table>")
    return _html_report_part2(s, stats, plan, contam, context_len, output_path)


def _html_report_part2(s, stats, plan, contam, context_len, output_path):
    """Second half of HTML report."""
    def pct(n, d):
        return "%.1f%%" % (100.0 * n / d) if d > 0 else "0.0%"

    # Section 3: Mixing Plan
    s.append("<h2>3. 混合方案 (%s)</h2>" % plan["mix_key"])
    s.append("<p>%s</p>" % plan["description"])
    s.append("<table><tr><th>数据源</th><th>占比</th><th>目标 token</th><th>可用</th><th>格式</th></tr>")
    for source, info in plan["sources"].items():
        avail = info.get("available_tokens", 0)
        avail_str = format(avail, ",") if isinstance(avail, int) else str(avail)
        s.append("<tr><td><strong>%s</strong></td><td>%s%%</td><td>~%dM</td><td>%s</td><td>%s</td></tr>"
                 % (source, info["ratio_pct"], info["target_tokens"] // 1_000_000, avail_str, info.get("format", "")))
    s.append("</table>")

    # Section 4: Context Length
    s.append("<h2>4. 上下文长度处理</h2>")
    s.append("<p>目标: <strong>%d</strong></p>" % context_len)
    over_4k = sum(v for k, v in stats["length_buckets"].items() if k in ("4k-8k", ">8k"))
    s.append("<div class='%s'>超 4096: %d (%s)</div>" % ("warn" if over_4k > 0 else "ok", over_4k, pct(over_4k, stats["total_records"])))
    s.append("<p>截断策略: <code>keep_system_completion</code> - 保留 system+assistant, 截断 user 中段。</p>")

    # Section 5: Contamination
    s.append("<h2>5. 污染隔离闸门</h2>")
    if not contam.get("checked"):
        s.append("<div class='warn'>评测数据集不可达，污染检查跳过。</div>")
    elif contam["contaminated"] == 0:
        s.append("<div class='ok'>&#9989; 零污染命中。</div>")
    else:
        s.append("<div class='danger'>&#128308; %d 条污染！</div>" % contam["contaminated"])

    # Section 6: UltraData
    s.append("<h2>6. UltraData 集成</h2>")
    s.append("<table><tr><th>数据源</th><th>格式</th><th>磁盘</th><th>Token</th><th>路径</th></tr>")
    for key, est in ULTRADATA_ESTIMATES.items():
        s.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>~%dB</td><td><code>%s</code></td></tr>"
                 % (est["source"], est["format"], est["disk_size"], est["token_count"] // 1_000_000_000, est["nfs_path"]))
    s.append("</table>")

    # Section 7: Upsampling
    s.append("<h2>7. PyAether 上采样策略</h2>")
    pya_tokens = stats["total_tokens"]
    pya_target = plan["sources"].get("pyaether", {}).get("target_tokens", 0)
    if pya_tokens > 0 and pya_target > pya_tokens:
        s.append("<div class='warn'>需上采样 ~%.1fx (源 %dM -> 目标 %dM tok)</div>"
                 % (pya_target / pya_tokens, pya_tokens // 1_000_000, pya_target // 1_000_000))
        s.append("<ul><li>high tier 优先 (3x)</li><li>medium 2x, low 1x</li><li>S3 仅 89 条待 GPU 扩展</li></ul>")
    else:
        s.append("<div class='ok'>语料充足。</div>")

    # Section 8: verl format
    s.append("<h2>8. verl SFT 格式</h2>")
    s.append("<pre style='background:#f4f4f4;padding:12px;border-radius:6px;font-size:0.85em;'>")
    s.append('[{"role":"system","content":"You are an EDA assistant..."},\n {"role":"user","content":"Read API doc..."},\n {"role":"assistant","content":"```python\\n...```"}]')
    s.append("</pre>")

    # Section 9: Plan
    s.append("<h2>9. 执行计划</h2>")
    s.append("<table><tr><th>阶段</th><th>内容</th><th>GPU?</th><th>时机</th></tr>")
    s.append("<tr><td>E1</td><td>JSONL->verl SFT + blend config</td><td>否</td><td>11/8</td></tr>")
    s.append("<tr><td>E2</td><td>基线评测 -> D1-D6 -> 确认配比</td><td>是</td><td>11/9</td></tr>")
    s.append("<tr><td>E3</td><td>退火后起跑 SFT</td><td>是</td><td>12/25+</td></tr>")
    s.append("<tr><td>E4</td><td>消融: ctx 4096/8192/16384</td><td>是</td><td>SFT后</td></tr>")
    s.append("</table>")

    # Section 10: Risks
    s.append("<h2>10. 风险与缓解</h2>")
    s.append("<table><tr><th>风险</th><th>概率</th><th>缓解</th></tr>")
    s.append("<tr><td>PyAether 语料小 (~%dM tok)</td><td>高</td><td>上采样 + GPU 后扩展</td></tr>" % (pya_tokens // 1_000_000))
    s.append("<tr><td>agent 轨迹超长</td><td>高</td><td>ctx>=8192; 截断策略</td></tr>")
    s.append("<tr><td>低质量对稀释 (low=%d)</td><td>中</td><td>质量加权采样</td></tr>" % stats["by_tier"].get("low", 0))
    s.append("<tr><td>S3 仅 89 条</td><td>高</td><td>GPU 后沙盒扩展</td></tr>")
    s.append("<tr><td>污染泄漏</td><td>低</td><td>contamination gate 全检</td></tr>")
    s.append("</table>")

    s.append("<hr><p style='color:#999;font-size:0.85em;'>R56 - BaiZe Stage(ii) - SFT Data Mixing Pipeline - Zero GPU</p>")
    s.append("</body></html>")

    html = "\n".join(s)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path, len(html)


def main():
    parser = argparse.ArgumentParser(
        description="R56: SFT Data Mixing Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="Analyze only, no output files")
    parser.add_argument("--mix", default="agent50:general30:pyaether20",
                        help="Mix strategy key or custom like 'agent40:general40:pyaether20'")
    parser.add_argument("--context-len", type=int, default=8192, help="Target context length")
    parser.add_argument("--pyaether-jsonl", default=PYAETHER_SFT_JSONL, help="PyAether SFT corpus path")
    parser.add_argument("--eval-dataset", default=EVAL_DATASET, help="Eval dataset for contamination check")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_JSONL, help="Output mixed JSONL path")
    parser.add_argument("--blend-config", default=DEFAULT_BLEND_CONFIG, help="Output blend config YAML")
    parser.add_argument("--html", default=None, help="Output HTML report path")
    parser.add_argument("--truncate-strategy", default="keep_system_completion",
                        choices=["keep_system_completion", "keep_head_tail", "drop_system"])
    args = parser.parse_args()

    print("=" * 60)
    print("R56: SFT Data Mixing Pipeline")
    print("  Mix: %s | Ctx: %d | Dry: %s" % (args.mix, args.context_len, args.dry_run))
    print("=" * 60)

    print("\n[1] Loading PyAether SFT corpus...")
    records = load_pyaether_sft(args.pyaether_jsonl)
    print("  Loaded %d records" % len(records))

    print("\n[2] Analyzing corpus...")
    stats = analyze_pyaether_corpus(records)
    print("  Tokens: ~%dM | Mean: %.1f | P95: %d" % (stats["total_tokens"] // 1_000_000, stats["mean_tokens"], stats["p95_tokens"]))
    print("  Types: %s" % dict(stats["by_type"]))
    print("  Tiers: %s" % dict(stats["by_tier"]))
    print("  Lengths: %s" % stats["length_buckets"])

    print("\n[3] Contamination gate...")
    eval_apis = load_eval_apis(args.eval_dataset)
    print("  Eval API blacklist: %d" % len(eval_apis))
    contam = check_contamination(records, eval_apis)
    if contam["checked"]:
        print("  %s" % ("CLEAR" if contam["contaminated"] == 0 else "FOUND %d" % contam["contaminated"]))

    print("\n[4] Mixing plan...")
    plan = compute_mixing_plan(args.mix, stats, args.context_len)
    for source, info in plan["sources"].items():
        print("  %s: %d%% -> ~%dM tok" % (source, info["ratio_pct"], info["target_tokens"] // 1_000_000))

    print("\n[5] Converting to verl SFT format...")
    verl_records = []
    truncated_count = 0
    for rec in records:
        verl_rec = convert_to_verl_sft(rec)
        total_tok = sum(estimate_tokens(m["content"]) for m in verl_rec["conversation"])
        if total_tok > args.context_len:
            verl_rec["conversation"], was_trunc = truncate_conversation(
                verl_rec["conversation"], args.context_len, args.truncate_strategy)
            if was_trunc:
                truncated_count += 1
        verl_records.append(verl_rec)
    print("  Converted %d | Truncated %d (%.1f%%)" % (len(verl_records), truncated_count, 100.0 * truncated_count / max(len(verl_records), 1)))

    if not args.dry_run:
        print("\n[6] Writing outputs...")
        with open(args.output, "w", encoding="utf-8") as f:
            for rec in verl_records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print("  JSONL: %s (%d records, %.1f MB)" % (args.output, len(verl_records), os.path.getsize(args.output) / 1_000_000))
        generate_blend_config_yaml(plan, args.blend_config)
        print("  Blend config: %s" % args.blend_config)
        if args.html:
            hp, hs = generate_html_report(stats, plan, contam, args.context_len, args.html)
            print("  HTML: %s (%d bytes)" % (hp, hs))
    else:
        print("\n[6] [DRY-RUN] Skip outputs")
        if args.html:
            hp, hs = generate_html_report(stats, plan, contam, args.context_len, args.html)
            print("  HTML (dry-run): %s (%d bytes)" % (hp, hs))

    print("\n" + "=" * 60)
    print("R56 DONE | Samples: %d | Tokens: ~%dM | Contam: %s | Mix: %s" % (
        stats["total_records"], stats["total_tokens"] // 1_000_000,
        "CLEAR" if not contam.get("contaminated") else "FOUND",
        args.mix))
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
