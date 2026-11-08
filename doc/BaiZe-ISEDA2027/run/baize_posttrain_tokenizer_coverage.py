#!/usr/bin/env python3
"""
baize_posttrain_tokenizer_coverage.py — R77: MiniCPM5-2B Tokenizer Coverage
Analysis for EDA Domain Vocabulary

WHAT IT DOES:
  1. Loads the MiniCPM5-2B tokenizer from /tmp/models/MiniCPM5-2B/
  2. Extracts all 8,463 API names from API_INFO_MERGED_V3.json
  3. Tokenizes each API name and analyzes token count distribution
  4. Compares EDA vocabulary coverage against common English baselines
  5. Identifies poorly-tokenized API names (high subword fragmentation)
  6. Extracts subword decomposition patterns (camelCase splitting behavior)
  7. Analyzes API category names and EDA jargon coverage
  8. Derives implications for domain annealing data requirements
  9. Generates HTML report + JSON output

USAGE:
  python3 baize_posttrain_tokenizer_coverage.py                 # Full analysis
  python3 baize_posttrain_tokenizer_coverage.py --verbose        # Print details
  python3 baize_posttrain_tokenizer_coverage.py --html OUT.html  # Generate HTML
  python3 baize_posttrain_tokenizer_coverage.py --json OUT.json  # Generate JSON
  python3 baize_posttrain_tokenizer_coverage.py --quick          # Skip deep analysis

Author: posttrain wake125 (2026-11-09).  License: project-internal.
⚠️ Surrogate model results are NOT transferable to BaiZe.
"""

import json
import os
import sys
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path

MODEL_DIR = "/tmp/models/MiniCPM5-2B"
API_INFO_PATH = os.path.expanduser("~/code/eda_fastmcp/docs/API_INFO_MERGED_V3.json")
RUN_DIR = Path(__file__).parent.resolve()

ENGLISH_BASELINE = [
    "the", "and", "for", "are", "but", "not", "you", "all", "can", "had",
    "her", "was", "one", "our", "out", "day", "get", "has", "him", "his",
    "how", "man", "new", "now", "old", "see", "two", "way", "who", "boy",
    "did", "its", "let", "put", "say", "she", "too", "use", "table", "chair",
    "computer", "science", "engineering", "design", "layout", "schematic",
    "circuit", "signal", "power", "ground", "voltage", "current", "resistor",
    "capacitor", "transistor", "diode", "logic", "gate", "flip", "flop",
    "register", "buffer", "memory", "clock", "reset", "enable", "disable",
    "input", "output", "port", "pin", "net", "wire", "bus", "path", "route",
    "layer", "metal", "via", "contact", "cell", "instance", "module",
    "block", "array", "matrix", "vector", "scalar", "function", "variable",
    "parameter", "argument", "return", "value", "string", "integer", "float",
    "boolean", "list", "dict", "tuple", "set", "class", "object", "method",
    "attribute", "property", "element", "index", "key", "data", "type",
    "error", "warning", "message", "status", "state", "mode", "phase",
    "step", "stage", "level", "point", "line", "rectangle", "circle",
    "polygon", "region", "area", "boundary", "edge", "corner",
    "center", "width", "height", "length", "size", "scale", "rotate",
    "move", "copy", "delete", "create", "modify", "update", "select",
    "search", "find", "get", "set", "add", "remove", "clear", "check",
]

EDA_JARGON = [
    "techlib", "techfile", "PDK", "GDS", "OASIS", "LEF", "DEF", "Liberty",
    "SPICE", "DRC", "LVS", "ERC", "ANT", "DFM", "RCX", "EM", "IR",
    "droop", "floorplan", "placement", "routing", "extraction", "timing",
    "closure", "signoff", "tapeout", "foundry", "wafer", "reticle",
    "lithography", "etch", "deposition", "doping", "implant", "mask",
    "poly", "active", "nwell", "pwell", "diffusion", "metal1", "metal2",
    "via1", "via2", "pad", "bump", "TSV", "RDL", "package",
    "flipchip", "wirebond", "QFN", "BGA", "CSP", "WLP", "IP", "SOC",
    "ASIC", "FPGA", "PLL", "DLL", "ADC", "DAC", "SRAM", "DRAM", "ROM",
    "FIFO", "LIFO", "UART", "SPI", "I2C", "USB", "PCI", "AXI", "AHB",
    "APB", "GPIO", "DMA", "INTC", "TIMER", "WDT", "RTC", "PWM", "CAN",
    "Ethernet", "SERDES", "PHY", "MAC", "DDR", "cache", "TLB",
    "branch", "predictor", "pipeline", "stall", "flush", "hazard",
    "forwarding", "bypass", "renaming", "reorder", "commit", "rollback",
    "speculative", "superscalar", "VLIW", "SIMD", "MIMD",
    "multithreading", "interrupt", "exception", "trap", "fault",
    "latency", "bandwidth", "throughput", "utilization",
]


def load_tokenizer(model_dir):
    """Load tokenizer using transformers."""
    try:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
        return tok
    except Exception as e:
        print(f"ERROR: Cannot load tokenizer from {model_dir}: {e}", file=sys.stderr)
        tok_path = os.path.join(model_dir, "tokenizer.json")
        if os.path.exists(tok_path):
            try:
                from tokenizers import Tokenizer
                tok = Tokenizer.from_file(tok_path)
                print(f"Loaded from {tok_path} (tokenizers lib)", file=sys.stderr)
                return tok
            except Exception as e2:
                print(f"ERROR: Fallback failed: {e2}", file=sys.stderr)
        return None


def load_api_names(api_info_path):
    """Load API names from API_INFO_MERGED_V3.json."""
    with open(api_info_path) as f:
        data = json.load(f)
    if isinstance(data, dict):
        return list(data.keys())
    elif isinstance(data, list):
        names = []
        for item in data:
            if isinstance(item, dict) and "api_name" in item:
                names.append(item["api_name"])
            elif isinstance(item, str):
                names.append(item)
        return names
    return []


def tokenize_text(tokenizer, text):
    """Tokenize text and return token IDs."""
    if hasattr(tokenizer, 'encode'):
        ids = tokenizer.encode(text, add_special_tokens=False)
        return ids if isinstance(ids, list) else list(ids)
    return []


def decode_token(tokenizer, token_id):
    """Decode a single token ID to string."""
    if hasattr(tokenizer, 'convert_ids_to_tokens'):
        return tokenizer.convert_ids_to_tokens([token_id])[0]
    elif hasattr(tokenizer, 'decode'):
        return tokenizer.decode([token_id])
    return f"<id:{token_id}>"


def get_api_prefix(name):
    """Extract prefix (first lowercase run before first uppercase)."""
    m = re.match(r'^([a-z]+)', name)
    return m.group(1) if m else ""


def run_analysis(quick=False):
    """Run the full tokenizer coverage analysis."""
    print("=== R77: MiniCPM5-2B Tokenizer Coverage Analysis ===\n")

    print("[1/8] Loading tokenizer...")
    tokenizer = load_tokenizer(MODEL_DIR)
    if tokenizer is None:
        print("FATAL: Cannot load tokenizer.")
        return None
    vocab_size = len(tokenizer) if hasattr(tokenizer, '__len__') else 0
    print(f"  Vocab size: {vocab_size}")

    print("[2/8] Loading API names...")
    api_names = load_api_names(API_INFO_PATH)
    print(f"  Loaded {len(api_names)} API names")
    if not api_names:
        return None

    print("[3/8] Tokenizing API names...")
    api_token_counts = {}
    api_decompositions = {}
    for name in api_names:
        ids = tokenize_text(tokenizer, name)
        api_token_counts[name] = len(ids)
        if not quick:
            api_decompositions[name] = [decode_token(tokenizer, t) for t in ids]

    print("[4/8] Computing statistics...")
    counts = list(api_token_counts.values())
    total = len(counts)
    stats = {
        "total_apis": total, "vocab_size": vocab_size,
        "mean_tokens_per_api": round(statistics.mean(counts), 2),
        "median_tokens_per_api": statistics.median(counts),
        "stdev_tokens_per_api": round(statistics.stdev(counts), 2) if len(counts) > 1 else 0,
        "min_tokens": min(counts), "max_tokens": max(counts),
        "single_token_apis": sum(1 for c in counts if c == 1),
        "two_token_apis": sum(1 for c in counts if c == 2),
        "three_token_apis": sum(1 for c in counts if c == 3),
        "four_plus_token_apis": sum(1 for c in counts if c >= 4),
    }
    for k in ["single_token", "two_token", "three_token", "four_plus"]:
        actual_key = k + "_token_apis" if k == "four_plus" else k + "_apis"
        stats[k + "_pct"] = round(stats[actual_key] / total * 100, 1)

    dist_buckets = Counter()
    for c in counts:
        if c <= 4:
            dist_buckets[str(c)] += 1
        elif c <= 6:
            dist_buckets["5-6"] += 1
        elif c <= 10:
            dist_buckets["7-10"] += 1
        else:
            dist_buckets["11+"] += 1
    stats["distribution"] = dict(dist_buckets)

    print("[5/8] Worst-case APIs...")
    sorted_apis = sorted(api_token_counts.items(), key=lambda x: x[1], reverse=True)
    worst_20 = sorted_apis[:20]
    single_examples = [n for n, c in sorted_apis if c == 1][:20]
    worst_examples = [(n, c, api_decompositions.get(n, [])) for n, c in worst_20]

    print("[6/8] English baseline...")
    eng_counts = {}
    for w in ENGLISH_BASELINE:
        eng_counts[w] = len(tokenize_text(tokenizer, w))
    ec = list(eng_counts.values())
    eng_stats = {
        "total_words": len(ec),
        "mean_tokens": round(statistics.mean(ec), 2),
        "median_tokens": statistics.median(ec),
        "single_token_pct": round(sum(1 for c in ec if c == 1) / len(ec) * 100, 1),
    }

    print("[7/8] EDA jargon...")
    jargon_counts = {}
    for t in EDA_JARGON:
        jargon_counts[t] = len(tokenize_text(tokenizer, t))
    jc = list(jargon_counts.values())
    jargon_stats = {
        "total_terms": len(jc),
        "mean_tokens": round(statistics.mean(jc), 2),
        "median_tokens": statistics.median(jc),
        "single_token_pct": round(sum(1 for c in jc if c == 1) / len(jc) * 100, 1),
    }

    print("[8/8] Prefix analysis...")
    prefix_stats = defaultdict(lambda: {"count": 0, "total_tokens": 0})
    for name in api_names:
        pfx = get_api_prefix(name)
        if pfx:
            prefix_stats[pfx]["count"] += 1
            prefix_stats[pfx]["total_tokens"] += api_token_counts[name]
    top_prefixes = sorted(prefix_stats.items(), key=lambda x: x[1]["count"], reverse=True)[:30]
    prefix_analysis = [
        {"prefix": p, "api_count": d["count"],
         "avg_tokens_per_api": round(d["total_tokens"] / d["count"], 2)}
        for p, d in top_prefixes
    ]

    top_subwords = []
    if not quick:
        sw_counter = Counter()
        for name, toks in api_decompositions.items():
            for t in toks:
                sw_counter[t] += 1
        top_subwords = [{"token": t, "count": c} for t, c in sw_counter.most_common(50)]

    frag_ratio = stats["mean_tokens_per_api"] / eng_stats["mean_tokens"] if eng_stats["mean_tokens"] > 0 else 0
    if frag_ratio > 3.0:
        verdict, mult = "SEVERE fragmentation — annealing needs significantly more data", 3.0
    elif frag_ratio > 2.0:
        verdict, mult = "HIGH fragmentation — annealing needs ~2x more data", 2.0
    elif frag_ratio > 1.5:
        verdict, mult = "MODERATE fragmentation — annealing needs ~1.5x more data", 1.5
    else:
        verdict, mult = "LOW fragmentation — annealing can proceed with baseline estimates", 1.0

    results = {
        "section": "R77", "title": "MiniCPM5-2B Tokenizer Coverage Analysis",
        "date": "2026-11-09", "wake": 125, "model": "MiniCPM5-2B",
        "model_dir": MODEL_DIR, "vocab_size": vocab_size,
        "api_stats": stats, "english_baseline": eng_stats,
        "eda_jargon": jargon_stats, "fragmentation_ratio": round(frag_ratio, 3),
        "annealing_verdict": verdict, "annealing_data_multiplier": mult,
        "worst_20_apis": [{"name": n, "token_count": c, "decomposition": d} for n, c, d in worst_examples],
        "single_token_examples": single_examples,
        "top_prefixes": prefix_analysis, "top_subwords": top_subwords,
        "distribution": dict(dist_buckets),
    }

    print(f"\n{'='*60}\nSUMMARY\n{'='*60}")
    print(f"Vocab size:        {vocab_size:,}")
    print(f"Total APIs:        {total:,}")
    print(f"Mean tokens/API:   {stats['mean_tokens_per_api']}")
    print(f"Median:            {stats['median_tokens_per_api']}")
    print(f"Min/Max:           {stats['min_tokens']}/{stats['max_tokens']}")
    print(f"Single-token:      {stats['single_token_apis']} ({stats['single_token_pct']}%)")
    print(f"4+ tokens:         {stats['four_plus_token_apis']} ({stats['four_plus_pct']}%)")
    print(f"English mean:      {eng_stats['mean_tokens']}")
    print(f"EDA jargon mean:   {jargon_stats['mean_tokens']}")
    print(f"Frag ratio:        {frag_ratio:.2f}x")
    print(f"Verdict:           {verdict}")
    print(f"\nTop 10 worst APIs:")
    for item in results["worst_20_apis"][:10]:
        print(f"  {item['name']:40s} -> {item['token_count']} tokens: {item['decomposition']}")
    print(f"\nTop 10 single-token APIs:")
    for n in single_examples[:10]:
        print(f"  {n}")
    print(f"\nTop 10 prefixes:")
    for p in prefix_analysis[:10]:
        print(f"  '{p['prefix']:10s}' {p['api_count']:5d} APIs, avg {p['avg_tokens_per_api']} tokens")

    return results


def generate_html(results, output_path):
    """Generate self-contained HTML report."""
    s = results["api_stats"]
    e = results["english_baseline"]
    j = results["eda_jargon"]
    css_class = "severe" if results["annealing_data_multiplier"] >= 3 else \
                "high" if results["annealing_data_multiplier"] >= 2 else \
                "moderate" if results["annealing_data_multiplier"] >= 1.5 else "low"

    worst_rows = ""
    for item in results["worst_20_apis"][:15]:
        decomp_str = " | ".join(str(x) for x in item["decomposition"]) if item["decomposition"] else ""
        worst_rows += f'\n        <tr><td><code>{item["name"]}</code></td><td>{item["token_count"]}</td><td><small>{decomp_str}</small></td></tr>'

    prefix_rows = ""
    for p in results["top_prefixes"][:20]:
        prefix_rows += f'\n        <tr><td><code>{p["prefix"]}</code></td><td>{p["api_count"]}</td><td>{p["avg_tokens_per_api"]:.1f}</td></tr>'

    dist_rows = ""
    for bucket in ["1", "2", "3", "4", "5-6", "7-10", "11+"]:
        count = results["distribution"].get(bucket, 0)
        pct = count / s["total_apis"] * 100
        dist_rows += f'\n        <tr><td>{bucket} tokens</td><td>{count}</td><td>{pct:.1f}%</td><td><div class="bar" style="width:{min(pct,100)}%"></div></td></tr>'

    subword_rows = ""
    if results.get("top_subwords"):
        for sw in results["top_subwords"][:20]:
            subword_rows += f'\n            <tr><td><code>{sw["token"]}</code></td><td>{sw["count"]}</td></tr>'

    single_list = "".join(f"<li><code>{n}</code></li>" for n in results["single_token_examples"][:20])

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>R77: MiniCPM5-2B 分词器 EDA 领域词汇覆盖分析</title>
<style>
body {{ font-family: -apple-system, "Segoe UI", Roboto, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; background: #f8f9fa; color: #333; }}
h1 {{ color: #1a237e; border-bottom: 3px solid #1a237e; padding-bottom: 10px; }}
h2 {{ color: #283593; margin-top: 30px; border-left: 4px solid #5c6bc0; padding-left: 10px; }}
table {{ border-collapse: collapse; width: 100%; margin: 10px 0; background: white; }}
th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
th {{ background: #e8eaf6; font-weight: 600; }}
tr:nth-child(even) {{ background: #f5f5f5; }}
.kpi {{ display: inline-block; background: #e3f2fd; border-radius: 8px; padding: 10px 20px; margin: 5px; min-width: 120px; }}
.kpi .num {{ font-size: 1.8em; font-weight: bold; color: #1565c0; }}
.kpi .label {{ font-size: 0.8em; color: #666; }}
.verdict {{ padding: 15px 20px; border-radius: 8px; margin: 15px 0; font-weight: 500; }}
.verdict.severe {{ background: #ffebee; border-left: 5px solid #c62828; color: #b71c1c; }}
.verdict.high {{ background: #fff3e0; border-left: 5px solid #e65100; color: #bf360c; }}
.verdict.moderate {{ background: #fffde7; border-left: 5px solid #f9a825; color: #f57f17; }}
.verdict.low {{ background: #e8f5e9; border-left: 5px solid #2e7d32; color: #1b5e20; }}
.bar {{ background: #5c6bc0; height: 20px; border-radius: 3px; min-width: 2px; }}
code {{ background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }}
.note {{ background: #e3f2fd; padding: 10px 15px; border-radius: 5px; margin: 10px 0; font-size: 0.9em; }}
.footer {{ margin-top: 40px; padding-top: 15px; border-top: 1px solid #ddd; font-size: 0.8em; color: #999; }}
</style>
</head>
<body>
<h1>R77: MiniCPM5-2B 分词器 EDA 领域词汇覆盖分析</h1>
<p>2026-11-09 · wake125 · 零 GPU · 纯分析</p>
<div class="note">⚠️ 替身模型（MiniCPM5-2B）分析结果不可迁移到 BaiZe 正式训练。</div>
<h2>1. 摘要</h2>
<p>分析 MiniCPM5-2B 分词器对 <b>{s['total_apis']:,}</b> 个 PyAether API 名称的覆盖。
词汇表大小 <b>{results['vocab_size']:,}</b>，API 平均 <b>{s['mean_tokens_per_api']}</b> tokens，
英文基线 <b>{e['mean_tokens']}</b> tokens，碎片化比率 <b>{results['fragmentation_ratio']}x</b>。</p>
<div class="kpi"><div class="num">{results['vocab_size']:,}</div><div class="label">词汇表</div></div>
<div class="kpi"><div class="num">{s['total_apis']:,}</div><div class="label">API 总数</div></div>
<div class="kpi"><div class="num">{s['mean_tokens_per_api']}</div><div class="label">平均 tokens/API</div></div>
<div class="kpi"><div class="num">{s['single_token_pct']}%</div><div class="label">单 token 覆盖率</div></div>
<div class="kpi"><div class="num">{results['fragmentation_ratio']}x</div><div class="label">碎片化比率</div></div>
<h2>2. 领域退火影响判定</h2>
<div class="verdict {css_class}">
<b>{results['annealing_verdict']}</b><br>建议数据量乘数：<b>{results['annealing_data_multiplier']}x</b>
</div>
<h2>3. 分词统计详情</h2>
<table>
<tr><th>统计项</th><th>EDA API</th><th>英文基线</th><th>EDA 术语</th></tr>
<tr><td>总数</td><td>{s['total_apis']:,}</td><td>{e['total_words']}</td><td>{j['total_terms']}</td></tr>
<tr><td>平均 tokens/词</td><td>{s['mean_tokens_per_api']}</td><td>{e['mean_tokens']}</td><td>{j['mean_tokens']}</td></tr>
<tr><td>中位数</td><td>{s['median_tokens_per_api']}</td><td>{e['median_tokens']}</td><td>{j['median_tokens']}</td></tr>
<tr><td>最小/最大</td><td>{s['min_tokens']}/{s['max_tokens']}</td><td>—</td><td>—</td></tr>
<tr><td>单 token 占比</td><td>{s['single_token_pct']}%</td><td>{e['single_token_pct']}%</td><td>{j['single_token_pct']}%</td></tr>
<tr><td>4+ tokens 占比</td><td>{s['four_plus_pct']}%</td><td>—</td><td>—</td></tr>
</table>
<h2>4. Token 分布</h2>
<table><tr><th>桶</th><th>数量</th><th>占比</th><th>可视化</th></tr>{dist_rows}</table>
<h2>5. 最差覆盖 API</h2>
<table><tr><th>API 名称</th><th>Token 数</th><th>子词分解</th></tr>{worst_rows}</table>
<h2>6. API 前缀分析</h2>
<table><tr><th>前缀</th><th>API 数量</th><th>平均 tokens/API</th></tr>{prefix_rows}</table>
<h2>7. 高频子词 Token</h2>
{"<table><tr><th>子词</th><th>出现次数</th></tr>" + subword_rows + "</table>" if subword_rows else "<p>（quick 模式跳过）</p>"}
<h2>8. 单 Token 覆盖 API</h2>
<ul>{single_list}</ul>
<h2>9. 领域退火建议</h2>
<ol>
<li><b>数据量调整</b>：碎片化 {results['fragmentation_ratio']}x → 语料量 ×{results['annealing_data_multiplier']}</li>
<li><b>退火步数</b>：基线 5000 步 → 调整为 {int(5000 * results['annealing_data_multiplier'])} 步</li>
<li><b>PyAether 语料占比</b>：从 25% 提高到 30%（补偿碎片化）</li>
<li><b>4+ token API</b>：{s['four_plus_token_apis']} 个（{s['four_plus_pct']}%）学习成本最高，SFT 数据重点覆盖</li>
<li><b>camelCase 模式</b>：退火语料应含完整 API 调用上下文，非孤立 API 名</li>
</ol>
<div class="footer"><p>R77 (2026-11-09) · Tokenizer Coverage · ⚠️ 替身模型结果不可迁移到 BaiZe</p></div>
</body></html>"""

    with open(output_path, "w") as f:
        f.write(html)
    print(f"HTML report: {output_path}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="R77: Tokenizer Coverage Analysis")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--html", type=str, default=None)
    parser.add_argument("--json", type=str, default=None)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    results = run_analysis(quick=args.quick)
    if results is None:
        sys.exit(1)

    if args.json:
        with open(args.json, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        print(f"JSON: {args.json}")

    if args.html:
        generate_html(results, args.html)

    print("\n=== R77 Complete ===")


if __name__ == "__main__":
    main()
