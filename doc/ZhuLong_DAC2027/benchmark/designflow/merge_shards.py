#!/usr/bin/env python3
"""merge_shards.py — 合并 4 个 shard jsonl → 主 jsonl

用法：python3 designflow/merge_shards.py
只做一件事：
  1. 把 EDA-Eval-DesignFlow_{A,B,C,D}.jsonl 合并到 EDA-Eval-DesignFlow.jsonl（按 task_id 去重，按 domain 排序）

🔴 2026-11-15 用户令：**不再自动生成日报**（原第 2 步已停用，理由见 regen_report 的 docstring）。
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.join(HERE, "..")
REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench"
JSONL_DIR = os.path.join(REPO, "benchmarks", "EDA-Eval-DesignFlow")
MAIN_JSONL = os.path.join(JSONL_DIR, "EDA-Eval-DesignFlow.jsonl")
SHARDS = ["A", "B", "C", "D"]


def merge():
    cases = {}  # task_id -> json line (dedup, last wins)
    for sid in SHARDS:
        path = os.path.join(JSONL_DIR, "EDA-Eval-DesignFlow_%s.jsonl" % sid)
        if not os.path.exists(path):
            print("  shard %s: not found, skip" % sid)
            continue
        n = 0
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                d = json.loads(line)
                tid = d.get("task_id") or d.get("id")
                if not tid:
                    print("  ⚠ skip line %d in shard %s: no task_id/id (keys=%s)" % (n+1, sid, list(d.keys())[:6]))
                    continue
                cases[tid] = (line, d)
                n += 1
        print("  shard %s: %d cases" % (sid, n))

    # sort by domain then task_id
    sorted_items = sorted(cases.values(), key=lambda x: (x[1].get("metadata", {}).get("domain", ""), x[1].get("task_id") or x[1].get("id","")))
    with open(MAIN_JSONL, "w", encoding="utf-8") as f:
        for line, _ in sorted_items:
            f.write(line)
    print("  → merged %d cases → %s" % (len(sorted_items), MAIN_JSONL))


def regen_report():
    """🔴 2026-11-15 用户令：**已停用自动日报**。

    用户原话：「report_benchmark_11_15.html 是谁写的，不是说不用写日报了吗。很费token。
    以后我会按需请相关agent出报告。」

    历史：日报由本函数在每次 merge_shards 后自动调用 gen_daily_report.py 重写
    （单文件达 3MB，且各 shard 每 ~25 分钟 commit 一次 ⇒ 反复重写+反复提交，token 与仓库双浪费）。
    脚本保留在原位（历史档，需要时手动 `python3 designflow/gen_daily_report.py` 仍可用），
    但**不再自动调用**。如需恢复，须有用户明确指令。
    """
    print("  ⏭  日报自动生成已停用（2026-11-15 用户令）· 需要时手动跑 gen_daily_report.py")
    return


def main():
    print("=== merge 4 shard jsonl → main ===")
    merge()
    print("\n=== regen daily report ===")
    regen_report()
    print("\n✅ merge done")


if __name__ == "__main__":
    main()
