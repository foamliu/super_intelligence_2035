#!/usr/bin/env python3
"""trace_prefilter.py — 规则 + 0.8B 两级 trace 预筛

设计:
  候选池降到 mc>=30 (1369 session) 后, 用两级预筛:
  1. 规则层 (快, 0ms): keywords 含 ≥2 个 EDA 工具词 → accept;
     只含 1 个泛词(analog/netlist/cmos/transistor) → 0.8B 复核
  2. 0.8B 层 (~1s): 对规则不确定的, 判 is_design_flow 二分类

  三档输出:
    accept    → 进深读队列 (规则或 0.8B 高置信判 EDA)
    reject    → 标 parked:prefilter_reject (0.8B 高置信判非 EDA)
    uncertain → 进深读队列但标 uncertain (低置信, 大模型复核)

用法:
  # 从 summary.tsv 批量预筛 mc>=30 的 session
  python3 trace_prefilter.py batch --summary <summary.tsv> --min-mc 30

  # 输出 JSONL 到文件 + 打印统计
  python3 trace_prefilter.py batch --summary <summary.tsv> --min-mc 30 --output prefilter_results.jsonl
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER = os.environ.get("LLAMA_SERVER", "http://127.0.0.1:8086")

# ===== 规则层关键词 =====
# 强 EDA 信号 (工具名 / 专属 API), 命中任一即大概率 EDA
EDA_STRONG = re.compile(
    r"virtuoso|innovus|icfb|calibre|spectre|hspice|genus|tempus|voltus|"
    r"dc_shell|pt_shell|icc2|primetime|aether|skipper|waveview|"
    r"tcl_innovus|tcl_waveview|pyaether|pyAether|"
    r"dbOpenCV|dbOpenCellView|dbCreateRect|dbCreatePath|dbCreateInst|"
    r"dbCreateLabel|dbCreatePolygon|dbGet|dbShape|dbSetObjNet|dbMakeBox|"
    r"cellview|oaDesign|oaOpen|ddGetObj|"
    r"lib\.defs|techfile|tech\.lib|gdsii|"
    r"openroad|yosys|"
    r"adexl|maestro|assembler|"
    r"verilog|vhdl|systemverilog|drc|lvs|pex|"
    r"rtl|synthesis|floorplan",
    re.IGNORECASE
)

# 弱/泛词 (单独出现不能确认 EDA, 需 0.8B 复核)
EDA_WEAK = re.compile(r"analog|netlist|cmos|mosfet|transistor|pdk|opamp|bandgap|schematic", re.IGNORECASE)

# 文件格式词 (中等信号, 单独出现需 0.8B 复核)
EDA_FORMAT = re.compile(r"\.gds|\.lef|\.def|\.cdl|\.spi", re.IGNORECASE)


def rule_prefilter(keywords_str):
    """规则层: 返回 (verdict, reason)
    verdict: accept / uncertain / reject
    """
    if not keywords_str or keywords_str.strip() == "":
        return "reject", "empty_keywords"

    # 统计强 EDA 信号词数
    strong_hits = set(m.group().lower() for m in EDA_STRONG.finditer(keywords_str))
    # 统计弱词
    weak_hits = set(m.group().lower() for m in EDA_WEAK.finditer(keywords_str))
    # 统计格式词
    format_hits = set(m.group().lower() for m in EDA_FORMAT.finditer(keywords_str))

    n_strong = len(strong_hits)
    n_weak = len(weak_hits)
    n_format = len(format_hits)

    # 规则 1: ≥2 个不同强 EDA 词 → accept
    if n_strong >= 2:
        return "accept", f"rule: {n_strong} strong EDA keywords: {','.join(sorted(strong_hits)[:5])}"
    # 规则 2: 1 个强 EDA 词 + ≥1 格式词 → accept
    if n_strong >= 1 and n_format >= 1:
        return "accept", f"rule: {n_strong} strong + {n_format} format keywords"
    # 规则 3: ≥3 个不同格式词 → accept (多文件格式 = EDA 流程)
    if n_format >= 3:
        return "accept", f"rule: {n_format} format keywords"
    # 规则 4: 只有弱词 (analog/netlist/cmos 等), 无强词无格式词 → 0.8B 复核
    if n_strong == 0 and n_format == 0 and n_weak >= 1:
        return "uncertain", f"rule: only weak keywords: {','.join(sorted(weak_hits))}"
    # 规则 5: 1 个强词但无格式词 → 可能 EDA, 0.8B 复核
    if n_strong == 1 and n_format == 0:
        return "uncertain", f"rule: 1 strong keyword: {','.join(strong_hits)}"
    # 规则 6: 无任何 EDA 信号 → reject
    if n_strong == 0 and n_weak == 0 and n_format == 0:
        return "reject", "rule: no EDA keywords"
    # 兜底
    return "uncertain", f"rule: mixed ({n_strong}strong,{n_weak}weak,{n_format}format)"


# ===== 0.8B 层 =====
SYSTEM_PROMPT = (
    "You are an EDA (Electronic Design Automation) trace classifier. "
    "Given keyword:count pairs from a coding agent session, decide if this session "
    "involves REAL IC/EDA design work using EDA tools. "
    "Output ONLY JSON (no markdown): "
    '{"is_design_flow": true|false, "confidence": 0.0-1.0, "reason": "one sentence"}\n\n'
    "Key rules:\n"
    "- 'analog' or 'netlist' or 'cmos' alone with high count is NOT enough — "
    "could be general programming or electronics discussion.\n"
    "- Multiple distinct EDA tool names (hspice/calibre/virtuoso/innovus/aether) = strong EDA.\n"
    "- File formats (.gds/.lef/.def/.cdl/.spi) = likely EDA.\n"
    "- synopsys/cadence alone = vendor name, not conclusive.\n"
    "- If unsure, output confidence < 0.6"
)


def call_llama(keywords_str, max_tokens=80, timeout=15):
    """调用 0.8B, 返回 (result_dict, elapsed_sec)"""
    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Keywords from session: {keywords_str}"},
        ],
        "max_tokens": max_tokens,
        "temperature": 0,
        "extra_body": {"enable_thinking": False},
        "chat_template_kwargs": {"enable_thinking": False},
    }
    req = urllib.request.Request(
        f"{SERVER}/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    t0 = time.time()
    resp = urllib.request.urlopen(req, timeout=timeout)
    data = json.loads(resp.read())
    elapsed = time.time() - t0
    content = data["choices"][0]["message"]["content"]
    # 解析 JSON
    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        m = re.search(r"\{[^{}]*\}", content, re.DOTALL)
        if m:
            try:
                result = json.loads(m.group())
            except json.JSONDecodeError:
                result = {"is_design_flow": True, "confidence": 0.5,
                          "reason": f"parse_fail: {content[:60]}"}
        else:
            result = {"is_design_flow": True, "confidence": 0.5,
                      "reason": f"parse_fail: {content[:60]}"}
    return result, elapsed


def prefilter_one(keywords_str):
    """两级预筛单个 session, 返回 {verdict, confidence, reason, layer, elapsed}"""
    # 第一级: 规则
    verdict, reason = rule_prefilter(keywords_str)
    if verdict == "accept":
        return {"verdict": "accept", "confidence": 1.0, "reason": reason,
                "layer": "rule", "elapsed": 0.0}
    if verdict == "reject":
        return {"verdict": "reject", "confidence": 1.0, "reason": reason,
                "layer": "rule", "elapsed": 0.0}
    # 第二级: 0.8B (uncertain 的)
    result, elapsed = call_llama(keywords_str)
    is_df = result.get("is_design_flow")
    conf = float(result.get("confidence", 0.5))
    llm_reason = result.get("reason", "")
    if is_df is True and conf >= 0.7:
        v = "accept"
    elif is_df is False and conf >= 0.7:
        v = "reject"
    else:
        v = "uncertain"
    return {"verdict": v, "confidence": conf, "reason": f"0.8B: {llm_reason}",
            "layer": "llm", "elapsed": elapsed}


def load_summary(summary_path, min_mc=30):
    """读 summary.tsv (或 candidates_mc30.tsv), 返回去重的 session 列表 (mc>=min_mc)
    支持两种格式:
      - summary.tsv: ip\thost\tuser\tsession_file\tmatch_count\tkeywords\ttools
      - candidates_mc30.tsv: ip\tuser\tsession_file\tmatch_count\tkeywords
    """
    sessions = {}
    with open(summary_path) as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if not parts or parts[0] in ("ip", "host"):
                continue  # skip header
            if len(parts) < 5:
                continue
            # 兼容两种格式: 第3列是 user 或 session_file
            if parts[2].endswith(".json") or parts[2].endswith(".messages.json"):
                # candidates 格式: ip, user, session_file, mc, keywords
                ip, user, sf, mc_str, kw = parts[0], parts[1], parts[2], parts[3], parts[4]
                host = ""
            elif len(parts) >= 7:
                # summary 格式: ip, host, user, session_file, mc, keywords, tools
                ip, host, user, sf, mc_str, kw = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
            else:
                continue
            try:
                mc = int(mc_str)
            except ValueError:
                continue
            if mc < min_mc:
                continue
            if sf in sessions:
                if mc > sessions[sf]["mc"]:
                    sessions[sf] = {"ip": ip, "host": host, "user": user,
                                    "session": sf, "mc": mc, "keywords": kw}
            else:
                sessions[sf] = {"ip": ip, "host": host, "user": user,
                                "session": sf, "mc": mc, "keywords": kw}
    return list(sessions.values())


def cmd_batch(args):
    """批量预筛"""
    sessions = load_summary(args.summary, args.min_mc)
    if args.limit:
        sessions = sessions[:args.limit]

    print(f"[prefilter] {len(sessions)} sessions (mc>={args.min_mc})", file=sys.stderr)

    results = []
    rule_accept = rule_reject = llm_calls = 0
    llm_accept = llm_reject = llm_uncertain = 0
    total_llm_time = 0

    for i, s in enumerate(sessions):
        r = prefilter_one(s["keywords"])
        r["session"] = s["session"]
        r["user"] = s["user"]
        r["mc"] = s["mc"]
        results.append(r)

        if r["layer"] == "rule":
            if r["verdict"] == "accept":
                rule_accept += 1
            else:
                rule_reject += 1
        else:
            llm_calls += 1
            total_llm_time += r["elapsed"]
            if r["verdict"] == "accept":
                llm_accept += 1
            elif r["verdict"] == "reject":
                llm_reject += 1
            else:
                llm_uncertain += 1

        if (i + 1) % 100 == 0 or i == 0 or i == len(sessions) - 1:
            mark = {"accept": "✓", "reject": "✗", "uncertain": "?"}[r["verdict"]]
            print(f"  [{i+1}/{len(sessions)}] {mark} mc={s['mc']} "
                  f"{s['session'][:30]} | {r['layer']} | {r['reason'][:50]}",
                  file=sys.stderr)

    total = len(results)
    accept = sum(1 for r in results if r["verdict"] == "accept")
    reject = sum(1 for r in results if r["verdict"] == "reject")
    uncertain = sum(1 for r in results if r["verdict"] == "uncertain")

    print(f"\n=== Summary ===", file=sys.stderr)
    print(f"total: {total}", file=sys.stderr)
    print(f"  rule layer: accept={rule_accept} reject={rule_reject} "
          f"({100*(rule_accept+rule_reject)/max(total,1):.0f}% by rule)",
          file=sys.stderr)
    print(f"  llm layer:  accept={llm_accept} reject={llm_reject} "
          f"uncertain={llm_uncertain} ({llm_calls} calls, {total_llm_time:.1f}s)",
          file=sys.stderr)
    print(f"  final: accept={accept} reject={reject} uncertain={uncertain}",
          file=sys.stderr)

    # 输出 JSONL
    out = args.output or "/dev/stdout"
    with open(out, "w") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    if args.output:
        print(f"\n[written to {args.output}]", file=sys.stderr)


def main():
    p = argparse.ArgumentParser(description="trace prefilter (rule + 0.8B)")
    sub = p.add_subparsers(dest="cmd")

    p_batch = sub.add_parser("batch", help="batch prefilter from summary.tsv")
    p_batch.add_argument("--summary", required=True, help="summary.tsv path")
    p_batch.add_argument("--min-mc", type=int, default=30)
    p_batch.add_argument("--limit", type=int, default=0, help="max sessions (0=all)")
    p_batch.add_argument("--output", help="output JSONL file")

    p_test = sub.add_parser("test", help="test single keywords string")
    p_test.add_argument("keywords", help="keywords string e.g. 'hspice:100;netlist:50'")

    args = p.parse_args()
    if args.cmd == "batch":
        cmd_batch(args)
    elif args.cmd == "test":
        r = prefilter_one(args.keywords)
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        p.print_help()


if __name__ == "__main__":
    main()
