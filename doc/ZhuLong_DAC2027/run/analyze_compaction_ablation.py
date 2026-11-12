#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze_compaction_ablation.py — ZhuLong 压缩机制消融 · 结果分析

从 ablation_compaction_results.json + trace_ablation_compaction/*/  中抽取：
  - 各臂各轮 Pass@1 / 压缩触发率 / 平均压缩率 / 墙钟 / Token
  - 题级配对 (McNemar, 3 轮多数票)
  - 亚组 (压缩触发 / 轨迹长度 / 题类)
  - 成本-收益

用法:
  python3 analyze_compaction_ablation.py [--results <ablation_compaction_results.json>] [--trace <trace_ablation_compaction/>] [--out <analysis.json>]
"""
import argparse, json, os, sys, glob, math
from pathlib import Path
from collections import defaultdict

REPO_RUN = Path(__file__).parent
RESULTS_JSON = REPO_RUN / "ablation_compaction_results.json"
TRACE_BASE = Path("/nasdata/app.e0031982/code/ZhuLong_DAC2027/trace_ablation_compaction")
SUBSET_FILE = REPO_RUN / "compaction_subset_40.txt"

ARMS = ["basic", "agentic"]
ROUNDS = [1, 2, 3]
TAGS = ["C_basic_r1", "C_agentic_r1", "C_agentic_r2", "C_basic_r2", "C_basic_r3", "C_agentic_r3"]


def load_results(path):
    try:
        return json.load(open(path))
    except Exception:
        return {"rounds": []}


def load_subset_tasks():
    """返回 40 题列表 + 原始 trace 工具调用数 (如果有)"""
    tasks = []
    if SUBSET_FILE.exists():
        for line in open(SUBSET_FILE):
            t = line.strip()
            if t:
                tasks.append(t)
    return tasks


def find_compaction_jsons(trace_dir):
    """在 trace_dir 下找所有 compaction.json, 返回 {task: [compaction_data, ...]}"""
    out = defaultdict(list)
    for p in glob.glob(str(trace_dir / "**" / "*.compaction.json"), recursive=True):
        try:
            d = json.load(open(p))
            # task 名从路径推断: .../code/EDA-Eval-PyAether-XXX/ws → EDA-Eval-PyAether-XXX
            # 或从 compaction.json 的 conversation_id 关联
            # 实际从 trace dir 结构: trace_ablation_compaction/C_basic_r1/cli_data/.../sessions/.../xxx.compaction.json
            # 需要从 session meta 关联 task
            out[p].append(d)
        except Exception:
            pass
    return out


def parse_compaction_stats(compaction_path):
    """从单个 compaction.json 抽取压缩统计"""
    try:
        d = json.load(open(compaction_path))
        msgs = d.get("messages", [])
        msg0 = msgs[0] if msgs else {}
        content = msg0.get("content", "")
        txt = content if isinstance(content, str) else (
            content[0].get("text", "") if isinstance(content, list) and content and isinstance(content[0], dict)
            else str(content)
        )
        is_agentic = "Context summary" in txt or "## Goal" in txt
        is_basic = "<user_input" in txt or "你是一位精通" in txt
        strategy = "agentic" if is_agentic else ("basic" if is_basic else "unknown")
        return {
            "strategy_detected": strategy,
            "source_message_count": d.get("source_message_count"),
            "retained_message_count": len(msgs),
            "file_size_bytes": os.path.getsize(compaction_path),
        }
    except Exception as e:
        return {"error": str(e)}


def extract_round_data(results, tag):
    """从 results JSON 中找指定 tag 的轮次数据"""
    for r in results.get("rounds", []):
        summary = r.get("summary", {}) or {}
        if summary.get("tag") == tag or r.get("tag") == tag:
            return r
    return None


def task_level_pass(results, tag):
    """返回 {task_name: pass(0/1)} for a given tag"""
    rd = extract_round_data(results, tag)
    if not rd:
        return {}
    tasks = rd.get("tasks", [])
    out = {}
    for t in tasks:
        name = t.get("task", "")
        # converged=1 or status=completed → pass
        passed = 1 if (t.get("converged") == 1 or t.get("status") == "completed") else 0
        if name:
            out[name] = passed
    return out


def task_level_tokens(results, tag):
    """返回 {task_name: total_tokens} for a given tag"""
    rd = extract_round_data(results, tag)
    if not rd:
        return {}
    out = {}
    for t in rd.get("tasks", []):
        name = t.get("task", "")
        out[name] = t.get("total_tokens", 0)
    return out


def task_level_wall(results, tag):
    """返回 {task_name: wall_sec} for a given tag"""
    rd = extract_round_data(results, tag)
    if not rd:
        return {}
    out = {}
    for t in rd.get("tasks", []):
        name = t.get("task", "")
        out[name] = t.get("wall_sec")
    return out


def majority_vote(passes_list):
    """3 轮多数票: passes_list = [0/1, 0/1, 0/1] → 0 or 1"""
    return 1 if sum(passes_list) >= 2 else 0


def mc_nemar(basic_pass, agentic_pass):
    """McNemar test: basic_pass, agentic_pass = {task: 0/1}"""
    b1a1 = b1a0 = b0a1 = b0a0 = 0
    tasks = set(basic_pass) | set(agentic_pass)
    for t in tasks:
        b = basic_pass.get(t, 0)
        a = agentic_pass.get(t, 0)
        if b == 1 and a == 1: b1a1 += 1
        elif b == 1 and a == 0: b1a0 += 1
        elif b == 0 and a == 1: b0a1 += 1
        else: b0a0 += 1
    # McNemar χ² = (|b1a0 - b0a1| - 1)² / (b1a0 + b0a1)  (with continuity correction)
    discordant = b1a0 + b0a1
    if discordant == 0:
        chisq = 0.0
        p_val = 1.0
    else:
        chisq = (abs(b1a0 - b0a1) - 1) ** 2 / discordant if discordant > 0 else 0
        # 简单 p-value 近似 (χ² df=1)
        p_val = math.exp(-chisq / 2)  # 粗略近似
    return {
        "both_pass": b1a1, "basic_only": b1a0, "agentic_only": b0a1, "both_fail": b0a0,
        "discordant": discordant, "chisq": round(chisq, 3), "p_approx": round(p_val, 4),
        "delta_pp": round((b0a1 - b1a0) / max(len(tasks), 1) * 100, 1),
    }


def bootstrap_ci(basic_pass, agentic_pass, n=10000):
    """Bootstrap CI for ΔPass@1"""
    import random
    tasks = sorted(set(basic_pass) | set(agentic_pass))
    if not tasks:
        return (None, None)
    deltas = []
    for _ in range(n):
        sample = [random.choice(tasks) for _ in tasks]
        b_rate = sum(basic_pass.get(t, 0) for t in sample) / len(sample)
        a_rate = sum(agentic_pass.get(t, 0) for t in sample) / len(sample)
        deltas.append((a_rate - b_rate) * 100)
    deltas.sort()
    lo = deltas[int(0.025 * n)]
    hi = deltas[int(0.975 * n)]
    return round(lo, 1), round(hi, 1)


def count_compaction_triggers(trace_dir, tag):
    """在 trace dir 下数该 tag 的 compaction.json 数量 (≈ 触发压缩的题数)"""
    tag_dir = trace_dir / tag
    if not tag_dir.exists():
        return 0, []
    files = list(tag_dir.rglob("*.compaction.json"))
    return len(files), [str(f) for f in files]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=str(RESULTS_JSON))
    ap.add_argument("--trace", default=str(TRACE_BASE))
    ap.add_argument("--out", default=str(REPO_RUN / "ablation_compaction_analysis.json"))
    args = ap.parse_args()

    results = load_results(args.results)
    trace_dir = Path(args.trace)
    subset_tasks = load_subset_tasks()

    analysis = {
        "meta": {
            "n_tasks": len(subset_tasks),
            "arms": ARMS,
            "rounds": ROUNDS,
            "tags": TAGS,
        },
        "per_round": {},
        "per_arm_summary": {},
        "mcnemar": {},
        "subgroups": {},
    }

    # --- 各轮统计 ---
    for tag in TAGS:
        arm = "basic" if "basic" in tag else "agentic"
        rd = extract_round_data(results, tag)
        if not rd:
            analysis["per_round"][tag] = {"status": "not_found"}
            continue
        summary = rd.get("summary", {}) or {}
        n_comp, comp_files = count_compaction_triggers(trace_dir, tag)
        analysis["per_round"][tag] = {
            "arm": arm,
            "pass_rate_pct": summary.get("pass_rate_pct"),
            "n_tasks": summary.get("n_tasks"),
            "total_tokens": summary.get("total_tokens"),
            "wall_sec_mean": summary.get("wall_sec_mean"),
            "compaction_triggers": n_comp,
            "compaction_trigger_rate": round(n_comp / max(summary.get("n_tasks", 1), 1) * 100, 1),
        }

    # --- 各臂汇总 (3 轮均值) ---
    for arm in ARMS:
        arm_tags = [t for t in TAGS if arm in t]
        passes = {t: task_level_pass(results, t) for t in arm_tags}
        passes_rates = [analysis["per_round"].get(t, {}).get("pass_rate_pct") for t in arm_tags]
        passes_rates = [r for r in passes_rates if r is not None]
        tokens = [analysis["per_round"].get(t, {}).get("total_tokens") for t in arm_tags]
        tokens = [t for t in tokens if t is not None]
        walls = [analysis["per_round"].get(t, {}).get("wall_sec_mean") for t in arm_tags]
        walls = [w for w in walls if w is not None]
        comps = [analysis["per_round"].get(t, {}).get("compaction_triggers") for t in arm_tags]
        comps = [c for c in comps if c is not None]

        analysis["per_arm_summary"][arm] = {
            "pass_rate_mean_pct": round(sum(passes_rates) / len(passes_rates), 1) if passes_rates else None,
            "pass_rate_per_round": passes_rates,
            "total_tokens_sum": sum(tokens) if tokens else None,
            "wall_sec_mean_of_means": round(sum(walls) / len(walls), 1) if walls else None,
            "compaction_triggers_mean": round(sum(comps) / len(comps), 1) if comps else None,
        }

    # --- 题级配对 (3 轮多数票) ---
    for arm in ARMS:
        arm_tags = [t for t in TAGS if arm in t]
        arm_task_pass = {}
        for t in subset_tasks:
            votes = []
            for tag in arm_tags:
                tp = passes.get(tag, {}) if arm == "basic" else passes.get(tag, {})
                # re-fetch
                tp = task_level_pass(results, tag)
                votes.append(tp.get(t, 0))
            arm_task_pass[t] = majority_vote(votes)
        if arm == "basic":
            basic_mv = arm_task_pass
        else:
            agentic_mv = arm_task_pass

    analysis["mcnemar"] = mc_nemar(basic_mv, agentic_mv)
    lo, hi = bootstrap_ci(basic_mv, agentic_mv)
    analysis["mcnemar"]["bootstrap_ci_95"] = [lo, hi]
    analysis["mcnemar"]["basic_pass_rate"] = round(sum(basic_mv.values()) / max(len(basic_mv), 1) * 100, 1)
    analysis["mcnemar"]["agentic_pass_rate"] = round(sum(agentic_mv.values()) / max(len(agentic_mv), 1) * 100, 1)

    # --- 亚组: 压缩触发 ---
    # (需要 per-task compaction trigger 数据; 从 trace dir 抽取)
    # 简化: 用 per-round compaction trigger count 做汇总
    analysis["subgroups"]["compaction_trigger"] = {"note": "per-task trigger data requires trace dir scan; see compaction_triggers per round"}

    # --- 写出 ---
    out_path = Path(args.out)
    out_path.write_text(json.dumps(analysis, ensure_ascii=False, indent=2))
    print(f"analysis written to {out_path}")
    print(f"\n=== Summary ===")
    for arm in ARMS:
        s = analysis["per_arm_summary"].get(arm, {})
        print(f"  {arm}: Pass@1 mean={s.get('pass_rate_mean_pct')}%  compaction triggers mean={s.get('compaction_triggers_mean')}  tokens sum={s.get('total_tokens_sum')}")
    mc = analysis["mcnemar"]
    print(f"  McNemar: Δ={mc.get('delta_pp')}pp  χ²={mc.get('chisq')}  p≈{mc.get('p_approx')}  CI=[{mc.get('bootstrap_ci_95',[None,None])[0]}, {mc.get('bootstrap_ci_95',[None,None])[1]}]")


if __name__ == "__main__":
    main()
