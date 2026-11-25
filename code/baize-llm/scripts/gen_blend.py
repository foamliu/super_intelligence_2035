#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""由 tokenized 目录 + 配比表生成 Megatron `--train-data-path` 串。

用法::

    python gen_blend.py --tsv configs/blend_s1.tsv --tok-root <tokenized>
    python gen_blend.py --tsv configs/blend_s1.tsv --tok-root <tokenized> --verify \
        --total-tokens 1468006400000
    python gen_blend.py --tsv configs/blend_s1.tsv --tok-root <tokenized> --json

规则：
  * 每个源的全部 shard 均分该源 prop：w_shard = prop / n_shards（浮点，6 位小数）。
  * 权重总和必须 = 1.000000（容差 1e-6），否则报错（避免静默改变配比）。
  * shard 必须 .bin/.idx 成对；缺任何一个 ⇒ 直接失败（数据不完整不允许开跑）。
  * --verify：用 .bin 字节 / 4 反算 token 数（int32 存 token），打印 epochs 并与
    tsv 的 epochs 列对账（偏差 >10% 告警，不改权重）。

退出码：0=OK / 1=参数或权重错误 / 2=数据缺失（阻塞，例如 SFT 未分词）。
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

WEIGHT_TOL = 1e-6


def die(msg: str, code: int = 1) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(code)


def natkey(p: str):
    """自然排序：xxx_s2 < xxx_s10。"""
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", os.path.basename(p))]


def load_spec(tsv: str):
    rows = []
    with open(tsv, encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            parts = [p.strip() for p in s.split("\t")]
            if len(parts) < 3:
                die(f"{tsv}:{ln} 列数不足（需要 key/subdir/prop[/epochs]）")
            epochs = float(parts[3]) if len(parts) >= 4 and parts[3] not in ("-", "") else None
            rows.append({"key": parts[0], "subdir": parts[1],
                         "prop": float(parts[2]), "epochs": epochs})
    if not rows:
        die(f"{tsv} 为空")
    total = sum(r["prop"] for r in rows)
    if abs(total - 1.0) > WEIGHT_TOL:
        die(f"prop 之和 = {total:.6f} != 1.000000（{tsv}）")
    return rows


def discover(d: str, exclude=frozenset()):
    bins = sorted(glob.glob(os.path.join(d, "*.bin")), key=natkey)
    if exclude:
        kept, skipped = [], []
        for b in bins:
            name = os.path.basename(b)[:-4]            # strip ".bin"
            if any(name == e or name.startswith(e) for e in exclude):
                skipped.append(name)
            else:
                kept.append(b)
        if skipped:
            print(f"# EXCLUDE: {d} 跳过 {len(skipped)} 片坏 shard："
                  f"{', '.join(skipped)}", file=sys.stderr)
        bins = kept
    for b in bins:
        if not os.path.isfile(b[:-4] + ".idx"):
            die(f"shard 不完整：{b} 缺 .idx", 2)
    return bins


def fmt_size(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.2f}{unit}"
        n /= 1024.0


def main() -> None:
    ap = argparse.ArgumentParser(description="生成 BaiZe-2B 预训练数据 blend")
    ap.add_argument("--tsv", required=True, help="配比表（configs/blend_*.tsv）")
    ap.add_argument("--tok-root", required=True, help="tokenized 根目录")
    ap.add_argument("--verify", action="store_true", help="反算 token/epochs 并打印")
    ap.add_argument("--total-tokens", type=int, default=0,
                    help="本阶段总 token（epochs 对账用；不传则跳过 epochs）")
    ap.add_argument("--json", action="store_true", help="输出结构化 JSON")
    ap.add_argument("--quiet", action="store_true", help="只输出最终 blend 串")
    ap.add_argument("--exclude", default="",
                    help="逗号分隔的 shard 名（去 .bin 后缀），跳过坏片；"
                         "权重自动在源内重摊（w=prop/n_kept）。"
                         "如 --exclude env14_CC-MAIN-2023-23")
    args = ap.parse_args()

    exclude = frozenset(e.strip() for e in args.exclude.split(",")
                        if e.strip()) if args.exclude else frozenset()

    rows = load_spec(args.tsv)
    pairs, stats, missing = [], [], []

    for r in rows:
        d = os.path.join(args.tok_root, r["subdir"])
        bins = discover(d, exclude) if os.path.isdir(d) else []
        if not bins:
            missing.append(f"{r['key']} ({d})")
            continue
        w = r["prop"] / len(bins)
        pairs.extend((w, b[:-4]) for b in bins)
        stats.append({
            "key": r["key"], "dir": d, "shards": len(bins), "prop": r["prop"],
            "w_per_shard": w, "tokens": sum(os.path.getsize(b) for b in bins) // 4,
            "target_epochs": r["epochs"],
        })

    if missing:
        print("BLOCKED: 以下数据源在 tokenized 镜像中找不到 shard：", file=sys.stderr)
        for m in missing:
            print(f"  - {m}", file=sys.stderr)
        print("  未分词的数据不能进 blend（不要伪造镜像完整）。", file=sys.stderr)
        if args.json:
            print(json.dumps({"blocked": True, "missing": missing, "sources": stats},
                             ensure_ascii=False, indent=2))
        sys.exit(2)

    wsum = sum(w for w, _ in pairs)
    if abs(wsum - 1.0) > 1e-4:
        die(f"shard 权重和 = {wsum:.8f}，偏离 1.0 过多")

    if args.verify and not args.json:
        print(f"{'key':<16} {'shards':>6} {'prop':>6} {'w/shard':>10} "
              f"{'tokens(B)':>12} {'epochs':>10} {'target':>8} {'dev':>10}", file=sys.stderr)
        for s in stats:
            ep = tgt = dev = "-"
            if args.total_tokens and s["tokens"]:
                e = s["prop"] * args.total_tokens / s["tokens"]
                ep = f"{e:.2f}"
                tgt = f"{s['target_epochs']:.2f}" if s["target_epochs"] is not None else "-"
                if s["target_epochs"]:
                    d = (e - s["target_epochs"]) / s["target_epochs"]
                    dev = f"{d * 100:+.1f}%"
            print(f"{s['key']:<16} {s['shards']:>6} {s['prop']:>6.2f} "
                  f"{s['w_per_shard']:>10.6f} {s['tokens'] / 1e9:>12.1f} "
                  f"{ep:>10} {tgt:>8} {dev:>10}", file=sys.stderr)
        print(f"# total_tokens={args.total_tokens:,}", file=sys.stderr)

    blend = " ".join(f"{w:.6f} {p}" for w, p in pairs)

    if args.json:
        print(json.dumps({"blocked": False, "shards_total": len(pairs),
                          "weight_sum": round(wsum, 8), "sources": stats,
                          "train_data_path": blend}, ensure_ascii=False, indent=2))
        return

    if not args.quiet:
        tok = sum(s["tokens"] for s in stats)
        print(f"# shards={len(pairs)} weight_sum={wsum:.6f} "
              f"source_tokens={tok:,} ({fmt_size(tok * 4)})", file=sys.stderr)
    print(blend)


if __name__ == "__main__":
    main()
