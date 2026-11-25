#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
baize_posttrain_harvest_agentic_sft_corpus.py
=============================================
Stage(ii) 主线 SFT 设计预研（零 GPU / 零 ckpt）—— §F5.1 落地。

背景（见 EXPERIMENTS_POSTTRAIN.md §F）：
  A1(SFT v39 step105) 5-run=4.56%±1.70% vs A0(base) 43.29%±3.92%，Δ=−38.73pp
  （McNemar χ²=68.01 p=0.0）⇒ SFT 显著退化。根因 = 旧 SFT 语料
  `sft_pyaether_corpus_v2.jsonl`（19524 条）**全部静态单轮 doc→code 补全对，
  0% agentic 多轮工具调用轨迹**，与 cline 部署环境（search→get_details→
  editor→run_code→fix→submit）根本不兼容 ⇒ 覆盖 base 健康回路。

本脚本（§F5.1 纠偏第一步）：
  从 A0 base 成功 run 的**真实 cline 会话轨迹**收割 agentic 多轮工具调用序列，
  产出**候选 agentic SFT 语料**（`agentic_sft_corpus_candidate.jsonl`），使训练
  分布对齐部署分布。语料形态 = 多轮 {user/assistant/tool} 消息序列，保留
  search_apis/get_api_details 检索前缀（§F5.2 检索保真）。

数据源：
  - baseline_A0_base_5run_summary.json  -> per_task_pass_count_by_run {task:[r1..r5]}
  - baseline_A0_base_run{1..5}_pertask.json -> eval_dir / session_id / 行为指标
  - <eval_dir>/trace/<task_id>/<session_id>.messages.json -> 原始 cline 会话

判据（预注册，先写后跑，跑完不许改）：
  - 只收割 **pass_count >= --min-pass-count** 的题（默认 5 = pass_all 25 题）；
  - 同一题多个 run 都过 ⇒ 取 search_calls 最高（检索保真度最好）的 run；
  - 每题产出 1 条轨迹（去重），记录行为指标 + 行为保真闸门标记（§F5.3）；
  - 行为保真闸门函数 `behavior_gate()` 供 post-SFT eval 复用：search_apis 频次
    < base 50% 或 submit_and_exit > base 200% 即判 fail。

输出：
  - agentic_sft_corpus_candidate.jsonl   每行 1 条 agentic 轨迹
  - agentic_sft_corpus_manifest.json     汇总 + 行为指标分布 + 闸门统计

不碰 GPU / 协议 / 题面 / check.py / 超时 / -p；纯 CPU 从落盘 JSON+trace 自算。
"""
import argparse
import json
import os
import sys
from collections import Counter, defaultdict

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
_MCP_PREFIX = "pyAether_MCP_server__"


def normalize_tool_name(name):
    if not name:
        return "unknown"
    if name.startswith(_MCP_PREFIX):
        name = name[len(_MCP_PREFIX):]
    mapping = {
        "search_apis": "search_apis",
        "search_apis_by_keyword": "search_apis_by_keyword",
        "get_api_details": "get_api_details",
        "run_code": "run_code",
        "submit_and_exit": "submit_and_exit",
        "editor": "editor",
        "read_files": "read_files",
        "run_commands": "run_commands",
    }
    return mapping.get(name, name)


def load_pertask_runs(n_runs=5):
    runs = {}
    idx = {}
    for n in range(1, n_runs + 1):
        p = os.path.join(RUN_DIR, "baseline_A0_base_run%d_pertask.json" % n)
        if not os.path.exists(p):
            print("WARN: missing %s" % p, file=sys.stderr)
            continue
        d = json.load(open(p))
        runs[n] = d
        for tid, t in d.get("per_task", {}).items():
            idx[(n, tid)] = t
    return runs, idx


def behavior_gate(metrics, base_ref):
    """§F5.3 行为保真闸门。base_ref = A0 base 每题中位行为参考。"""
    reasons = []
    s = metrics.get("search_apis", 0)
    sub = metrics.get("submit_and_exit", 0)
    bsearch = base_ref.get("search_apis", 0)
    bsubmit = base_ref.get("submit_and_exit", 0)
    if bsearch > 0 and s < bsearch * 0.5:
        reasons.append("search_apis %d < base*0.5(%.1f)" % (s, bsearch * 0.5))
    if bsubmit > 0 and sub > bsubmit * 2.0:
        reasons.append("submit_and_exit %d > base*2.0(%.1f)" % (sub, bsubmit * 2.0))
    if sub > 5:
        reasons.append("submit_storm %d>5" % sub)
    return ("fail" if reasons else "pass", "; ".join(reasons) if reasons else "ok")


def extract_trajectory(trace_path):
    if not os.path.exists(trace_path):
        return None
    d = json.load(open(trace_path))
    msgs = d.get("messages", [])
    conv = []
    counts = Counter()
    for m in msgs:
        role = m.get("role")
        c = m.get("content")
        blocks = c if isinstance(c, list) else None
        if blocks is None:
            blocks = [{"type": "text", "text": str(c) if c is not None else ""}]
        if role == "assistant":
            for b in blocks:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    counts[normalize_tool_name(b.get("name"))] += 1
        conv.append({"role": role, "content_blocks": blocks})
    return d.get("system_prompt", ""), conv, dict(counts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-pass-count", type=int, default=5,
                    help="只收割 5-run pass_count >= 此值的题（默认 5=pass_all 25 题）")
    ap.add_argument("--n-runs", type=int, default=5)
    ap.add_argument("--out-corpus", default=os.path.join(
        RUN_DIR, "agentic_sft_corpus_candidate.jsonl"))
    ap.add_argument("--out-manifest", default=os.path.join(
        RUN_DIR, "agentic_sft_corpus_manifest.json"))
    args = ap.parse_args()

    summary = json.load(open(os.path.join(
        RUN_DIR, "baseline_A0_base_5run_summary.json")))
    pc_by_run = summary["per_task_pass_count_by_run"]
    runs, idx = load_pertask_runs(args.n_runs)

    per_task_search = defaultdict(list)
    per_task_submit = defaultdict(list)
    for (n, tid), t in idx.items():
        tc = t.get("tool_calls", {})
        per_task_search[tid].append(tc.get("search_apis", 0) +
                                    tc.get("search_apis_by_keyword", 0))
        per_task_submit[tid].append(tc.get("submit_and_exit", 0))

    def median(xs):
        xs = sorted(xs)
        return xs[len(xs) // 2] if xs else 0

    base_ref = {tid: {"search_apis": median(per_task_search[tid]),
                      "submit_and_exit": median(per_task_submit[tid])}
                for tid in pc_by_run}

    records = []
    gate_stats = Counter()
    skipped = Counter()
    for tid, pclist in pc_by_run.items():
        if not isinstance(pclist, (list, tuple)):
            continue
        pass_count = sum(pclist)
        if pass_count < args.min_pass_count:
            continue
        cands = []
        for n in range(1, args.n_runs + 1):
            passed = bool(pclist[n - 1]) if n - 1 < len(pclist) else False
            if not passed:
                continue
            t = idx.get((n, tid))
            if not t:
                continue
            ed = runs[n].get("eval_dir") if n in runs else None
            cands.append((n, t, ed))
        if not cands:
            skipped["no_passing_run"] += 1
            continue
        cands.sort(key=lambda x: x[1].get("search_calls", 0), reverse=True)
        n, t, ed = cands[0]
        if not ed:
            skipped["no_eval_dir"] += 1
            continue
        sid = t.get("session_id")
        trace_path = os.path.join(ed, "trace", tid, "%s.messages.json" % sid)
        ext = extract_trajectory(trace_path)
        if ext is None:
            skipped["trace_missing"] += 1
            continue
        system_prompt, conv, tool_counts = ext
        metrics = {
            "search_apis": tool_counts.get("search_apis", 0),
            "search_apis_by_keyword": tool_counts.get("search_apis_by_keyword", 0),
            "get_api_details": tool_counts.get("get_api_details", 0),
            "run_code": tool_counts.get("run_code", 0),
            "editor": tool_counts.get("editor", 0),
            "read_files": tool_counts.get("read_files", 0),
            "run_commands": tool_counts.get("run_commands", 0),
            "submit_and_exit": tool_counts.get("submit_and_exit", 0),
            "total_tool_calls": sum(tool_counts.values()),
        }
        verdict, reason = behavior_gate(metrics, base_ref[tid])
        gate_stats[verdict] += 1
        rec = {
            "task_id": tid,
            "arm": "A0_base",
            "run": n,
            "session_id": sid,
            "pass_count_5run": pass_count,
            "outcome": t.get("outcome"),
            "system_prompt": system_prompt,
            "conversation": conv,
            "n_messages": len(conv),
            "behavior_metrics": metrics,
            "behavior_gate": verdict,
            "behavior_gate_reason": reason,
            "source_trace": trace_path,
            # 🔴 污染隔离红线（§5.1）：本轨迹来自 158 eval 任务之一，含其
            # prompt/函数签名/断言代码 ⇒ 不可直接用作「评测模型」的 SFT 训练数据。
            "contamination": {
                "eval_task_in_training": True,
                "red_line": "158 任务 prompt+签名+断言不可入训练集(§5.1); 本轨迹含 eval task 内容",
                "legitimate_use": "behavior/format 模板(健康 agentic 回路) + behavior_gate() 参考指标; "
                                  "正式 SFT 须在非 eval 的 held-out PyAether 任务上生成同形态 agentic 轨迹",
            },
        }
        records.append(rec)

    with open(args.out_corpus, "w") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    def dist(key):
        c = Counter(r["behavior_metrics"][key] for r in records)
        return dict(sorted(c.items()))

    manifest = {
        "arm": "A0_base",
        "source": "EXPERIMENTS_POSTTRAIN.md §F5.1 agentic trajectory harvest (zero GPU)",
        "min_pass_count": args.min_pass_count,
        "n_records": len(records),
        "skipped": dict(skipped),
        "gate_stats": dict(gate_stats),
        "behavior_metric_distributions": {
            k: dist(k) for k in ["search_apis", "get_api_details", "run_code",
                                 "submit_and_exit", "editor", "total_tool_calls"]
        },
        "pass_count_of_harvested": dict(Counter(r["pass_count_5run"] for r in records)),
        "n_messages_stats": {
            "min": min((r["n_messages"] for r in records), default=0),
            "max": max((r["n_messages"] for r in records), default=0),
            "mean": round(sum(r["n_messages"] for r in records) / len(records), 1) if records else 0,
        },
        "corpus_path": args.out_corpus,
        "contamination_warning": "🔴 红线(§5.1)：本语料 25 条轨迹全部来自 158 eval 任务的成功 run，"
                "含其 prompt/函数签名/断言代码 ⇒ 不可直接用作「将在 158 题上评测的模型」的 SFT 训练数据，"
                "否则评测 Δ 不可解释（train-on-test 污染）。",
        "correct_usage": [
            "作为 behavior/format 模板：量化健康 agentic 回路结构（search→get_details→editor→run_code→fix→submit，"
            "单次 submit，检索前缀保真），定义正式 SFT 的目标分布",
            "behavior_gate() 函数供 post-SFT eval 复用（§F5.3）：search_apis<base*0.5 或 submit>base*2.0 即判 SFT 失败",
            "正式 SFT 训练数据须在非 eval 的 held-out PyAether 任务（如 2k-5k 合成题池，API 名/签名隔离）上"
            "生成同形态 agentic 轨迹，本语料仅作行为模板而非训练样本",
        ],
        "note": "候选 agentic SFT 语料（多轮工具调用轨迹），对齐 cline 部署分布；"
                "正式 SFT 待 pretrain ckpt ETA≈2026-12-25；行为保真闸门 behavior_gate() "
                "供 post-SFT eval 复用（§F5.3）。",
        "caveat": "本语料仅来自 A0 base 成功 run；正式 SFT 须设保留率下限 + 行为保真闸门，"
                  "预注册 Δ>0 且 CI 下界>0 才算正向（§F5.5）。",
    }
    json.dump(manifest, open(args.out_manifest, "w"), ensure_ascii=False, indent=2)

    print("HARVEST_DONE n_records=%d gate_pass=%d gate_fail=%d skipped=%s"
          % (len(records), gate_stats["pass"], gate_stats["fail"], dict(skipped)))
    print("corpus: %s" % args.out_corpus)
    print("manifest: %s" % args.out_manifest)
    if records:
        bm = manifest["behavior_metric_distributions"]
        print("search_apis dist:", bm["search_apis"])
        print("submit_and_exit dist:", bm["submit_and_exit"])
        print("n_messages stats:", manifest["n_messages_stats"])


if __name__ == "__main__":
    main()

