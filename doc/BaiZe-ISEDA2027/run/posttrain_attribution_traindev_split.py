#!/usr/bin/env python3
# posttrain_attribution_traindev_split.py
# Task B (POSTTRAIN_ENV_ATTRIBUTION_SPEC.md §3 step 4): 158 题 -> 79 train / 79 dev 分层拆分.
# 分层变量 = scenario(域) × difficulty_bucket(难度, 由 num_unique_apis + lines_of_code 导出).
# 种子固定 (seed=20261114) -> 可复算. 补丁在 dev 上选 (3 seed), test=全 158 仅最后验一次.
#
# 纪律: 本脚本只读 attribution_158_metadata.json (task_id + scenario + category +
#        num_unique_apis + lines_of_code; 不含 prompt/函数签名/断言 -> 无污染).
#        不改 benchmark / 不挑题 / 不删失败样本.
#
# 用法:
#   python3 posttrain_attribution_traindev_split.py
#       [--meta attribution_158_metadata.json] [--out attribution_traindev_split.json]
#       [--seed 20261114] [--ratio 0.5]
import argparse, json, os, random
from collections import defaultdict, Counter

def difficulty_bucket(t):
    """难度分桶 (proxy, 由元数据导出, 不看题面).
    easy  : num_unique_apis<=2 且 lines_of_code<=3
    medium: 其余 且 (num_unique_apis<=4 且 lines_of_code<=15)
    hard  : 其余
    """
    n = t.get("num_unique_apis", 0)
    loc = t.get("lines_of_code", 0)
    if n <= 2 and loc <= 3:
        return "easy"
    if n <= 4 and loc <= 15:
        return "medium"
    return "hard"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta", default="attribution_158_metadata.json")
    ap.add_argument("--out", default="attribution_traindev_split.json")
    ap.add_argument("--seed", type=int, default=20261114)
    ap.add_argument("--ratio", type=float, default=0.5)
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    meta_path = args.meta if os.path.isabs(args.meta) else os.path.join(here, args.meta)
    out_path = args.out if os.path.isabs(args.out) else os.path.join(here, args.out)

    tasks = json.load(open(meta_path, encoding="utf-8"))
    assert len(tasks) == 158, f"期望 158 题, 实际 {len(tasks)}"

    # 分层键 = scenario × difficulty_bucket
    strata = defaultdict(list)
    for t in tasks:
        t = dict(t)
        t["difficulty_bucket"] = difficulty_bucket(t)
        strata[(t["scenario"], t["difficulty_bucket"])].append(t)

    rng = random.Random(args.seed)
    train, dev = [], []
    strata_summary = []
    # 按 key 排序保证遍历顺序确定 (再叠加 rng 已固定)
    for key in sorted(strata.keys()):
        items = sorted(strata[key], key=lambda x: x["task_id"])
        rng.shuffle(items)
        n = len(items)
        n_dev = int(round(n * args.ratio))
        # 保证 train/dev 各至少能放进; 158 题偶数, ratio=0.5 -> 79/79
        n_dev = max(0, min(n, n_dev))
        d = items[:n_dev]
        tr = items[n_dev:]
        dev.extend(d)
        train.extend(tr)
        strata_summary.append({
            "scenario": key[0], "difficulty": key[1],
            "total": n, "train": len(tr), "dev": len(d),
        })

    # 校正到精确 79/79 (若 round 导致偏差)
    def fix(target, big, small):
        while len(big) > target:
            x = big.pop()
            small.append(x)
        big.sort(key=lambda x: x["task_id"]); small.sort(key=lambda x: x["task_id"])
    # train+dev=158, 目标各 79
    if len(dev) != 79:
        if len(dev) > 79:
            fix(79, dev, train)
        else:
            fix(79, train, dev)

    def ids(xs): return [x["task_id"] for x in xs]
    result = {
        "meta": {
            "task": "posttrain attribution Task B train/dev split (spec §3 step 4)",
            "seed": args.seed,
            "ratio": args.ratio,
            "total": 158,
            "n_train": len(train), "n_dev": len(dev),
            "stratify": "scenario x difficulty_bucket",
            "difficulty_rule": "easy: apis<=2 & loc<=3; medium: apis<=4 & loc<=15; hard: else",
            "source_meta": "attribution_158_metadata.json (task_id+scenario+category+num_unique_apis+lines_of_code; no prompt/signature/assert -> no contamination)",
            "discipline": "patch selected on dev (3 seed), test=full 158 only final 5-run + McNemar; one patch at a time",
        },
        "train_ids": ids(train),
        "dev_ids": ids(dev),
        "strata_summary": strata_summary,
        "scenario_dist": {
            "train": dict(Counter(t["scenario"] for t in train)),
            "dev": dict(Counter(t["scenario"] for t in dev)),
        },
        "difficulty_dist": {
            "train": dict(Counter(t["difficulty_bucket"] for t in train)),
            "dev": dict(Counter(t["difficulty_bucket"] for t in dev)),
        },
    }
    json.dump(result, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"wrote {out_path}: train={len(train)} dev={len(dev)} (seed={args.seed})")
    print("scenario train:", result["scenario_dist"]["train"])
    print("scenario dev  :", result["scenario_dist"]["dev"])
    print("difficulty train:", result["difficulty_dist"]["train"])
    print("difficulty dev  :", result["difficulty_dist"]["dev"])

if __name__ == "__main__":
    main()
