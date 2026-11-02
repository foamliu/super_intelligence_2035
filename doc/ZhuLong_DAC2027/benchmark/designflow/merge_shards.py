#!/usr/bin/env python3
"""merge_shards.py — 合并 4 个 shard jsonl → 主 jsonl + regen 日报

用法：python3 designflow/merge_shards.py
做两件事：
  1. 把 EDA-Eval-DesignFlow_{A,B,C,D}.jsonl 合并到 EDA-Eval-DesignFlow.jsonl（按 task_id 去重，按 domain 排序）
  2. 调 gen_daily_report.py 重新生成日报
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
                cases[d["task_id"]] = (line, d)
                n += 1
        print("  shard %s: %d cases" % (sid, n))

    # sort by domain then task_id
    sorted_items = sorted(cases.values(), key=lambda x: (x[1].get("metadata", {}).get("domain", ""), x[1]["task_id"]))
    with open(MAIN_JSONL, "w", encoding="utf-8") as f:
        for line, _ in sorted_items:
            f.write(line)
    print("  → merged %d cases → %s" % (len(sorted_items), MAIN_JSONL))


def regen_report():
    report_py = os.path.join(HERE, "gen_daily_report.py")
    if not os.path.exists(report_py):
        print("  gen_daily_report.py not found, skip report")
        return
    r = subprocess.run([sys.executable, report_py], capture_output=True, text=True, cwd=HERE)
    if r.returncode == 0:
        print("  → report regenerated")
    else:
        print("  ⚠ report gen failed: %s" % r.stderr[:200])


def main():
    print("=== merge 4 shard jsonl → main ===")
    merge()
    print("\n=== regen daily report ===")
    regen_report()
    print("\n✅ merge done")


if __name__ == "__main__":
    main()
