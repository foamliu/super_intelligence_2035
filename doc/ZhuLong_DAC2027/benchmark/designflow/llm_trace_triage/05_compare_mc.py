#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""05_compare_mc.py — 把 LLM triage 标签与 mc 粗筛对比，产出新候选池。

用法:
  python3 05_compare_mc.py --labels labels.jsonl --out compare.json \
      [--gold gold.tsv] [--pool-out pool_llm_v1.tsv]

gold.tsv: <sid>\t<0|1>   （agent deepread 后的人工标签，0=非 EDA，1=EDA）

输出:
  - compare.json : 分箱统计 + 金标一致率 + 新候选
  - compare.md   : 人读表
  - pool_llm_v1.tsv : 仅 is_eda=true，按 confidence 降序
"""
import argparse
import json
import os
import sys

BINS = [(1, 40), (40, 100), (100, 300), (300, 10 ** 9)]
BIN_NAMES = ["1-39", "40-99", "100-299", "300+"]


def bin_of(mc):
    for i, (lo, hi) in enumerate(BINS):
        if lo <= mc < hi:
            return i
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--gold", default="")
    ap.add_argument("--pool-out", default="")
    args = ap.parse_args()

    rows = []
    for line in open(args.labels, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        if not d.get("ok") or "label" not in d:
            continue
        rows.append(d)
    if not rows:
        sys.exit("no valid labels")

    stats = []
    for b in range(len(BINS)):
        sub = [r for r in rows if bin_of(int(r.get("mc", 0))) == b]
        n = len(sub)
        pos = sum(1 for r in sub if r["label"]["is_eda_workflow"])
        conf = sum(r["label"]["confidence"] for r in sub) / n if n else 0.0
        stats.append({
            "bin": BIN_NAMES[b], "n": n, "eda_true": pos,
            "eda_rate": round(pos / n, 4) if n else 0.0,
            "mean_conf": round(conf, 4),
        })

    high = [r for r in rows if int(r.get("mc", 0)) >= 100]
    low = [r for r in rows if int(r.get("mc", 0)) < 100]
    high_pos = sum(1 for r in high if r["label"]["is_eda_workflow"])
    low_pos = [r for r in low if r["label"]["is_eda_workflow"]]

    dom = {}
    for r in rows:
        if r["label"]["is_eda_workflow"]:
            dom[r["label"]["domain"]] = dom.get(r["label"]["domain"], 0) + 1

    gold = {}
    if args.gold and os.path.isfile(args.gold):
        for line in open(args.gold, encoding="utf-8"):
            p = line.strip().split("\t")
            if len(p) >= 2 and p[1] in ("0", "1"):
                gold[p[0]] = int(p[1])

    agree = n_gold = 0
    confusion = {"tp": 0, "tn": 0, "fp": 0, "fn": 0}
    gold_rows = []
    for r in rows:
        sid = r["sid"]
        if sid not in gold:
            continue
        pred = 1 if r["label"]["is_eda_workflow"] else 0
        truth = gold[sid]
        n_gold += 1
        agree += 1 if pred == truth else 0
        key = {(1, 1): "tp", (0, 0): "tn", (1, 0): "fp", (0, 1): "fn"}[(pred, truth)]
        confusion[key] += 1
        gold_rows.append({"sid": sid, "mc": r.get("mc"), "pred": pred, "truth": truth,
                          "conf": r["label"]["confidence"], "domain": r["label"]["domain"]})

    pool = sorted(
        [r for r in rows if r["label"]["is_eda_workflow"]],
        key=lambda r: (-r["label"]["confidence"], -int(r.get("mc", 0))),
    )

    result = {
        "n_total": len(rows),
        "bins": stats,
        "mc100": {
            "n": len(high), "eda_true": high_pos,
            "precision": round(high_pos / len(high), 4) if high else None,
        },
        "mc_lt100": {
            "n": len(low), "eda_true": len(low_pos),
            "recovered": [{"sid": r["sid"], "mc": r.get("mc"),
                           "domain": r["label"]["domain"],
                           "task_type": r["label"]["task_type"],
                           "conf": r["label"]["confidence"]} for r in low_pos][:50],
        },
        "domain_dist": dom,
        "gold": {
            "n": n_gold,
            "agreement": round(agree / n_gold, 4) if n_gold else None,
            "confusion": confusion,
            "rows": gold_rows,
        },
        "pool_size": len(pool),
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    md = ["# LLM triage vs mc", "",
          "| mc bin | n | EDA true | rate | mean conf |", "|---|---:|---:|---:|---:|"]
    for s in stats:
        md.append(f"| {s['bin']} | {s['n']} | {s['eda_true']} | {s['eda_rate']:.1%} | {s['mean_conf']:.2f} |")
    md.append("")
    if result["mc100"]["precision"] is not None:
        md.append(f"- mc>=100 precision: **{result['mc100']['precision']:.1%}** "
                  f"({high_pos}/{len(high)})")
    md.append(f"- mc<100 中被找回的 EDA trace: **{len(low_pos)}** 条 "
              f"(共 {len(low)} 条低 mc 样本)")
    if n_gold:
        md.append(f"- 金标一致率: **{result['gold']['agreement']:.1%}** ({agree}/{n_gold}) "
                  f"confusion={confusion}")
    md.append(f"- 新候选池（is_eda=true）: **{len(pool)}** 条")
    md.append("")
    with open(os.path.splitext(args.out)[0] + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")

    if args.pool_out:
        with open(args.pool_out, "w", encoding="utf-8") as f:
            f.write("sid\tmc\tdomain\ttask_type\tconfidence\n")
            for r in pool:
                f.write(f"{r['sid']}\t{r.get('mc')}\t{r['label']['domain']}\t"
                        f"{r['label']['task_type']}\t{r['label']['confidence']:.2f}\n")

    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
