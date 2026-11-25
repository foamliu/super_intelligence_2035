#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""长上下文**数据体检**：这份数据里到底有多少「足够长的文档」？

背景：tokenized shard 是把文档连续拼成 int32 流、文档间用 EOD（本项目 = 129280）分隔。
如果 128K / 1M 的「长序列」其实由几十篇短文拼成，长上下文训练就是伪的（跨文档串味）。
本脚本按 EOD 切分并统计**文档长度分布**与**能覆盖目标上下文的比例**。

用法::

    python check_longctx_data.py \
        --shards "/nas_train/app.e0031982/datasets/baize-data/tokenized/Ultra-FineWeb/ultrafineweb_en_v1_4/*.bin" \
        --eod-id 129280 --targets 32768,131072,1048576 --sample 4

    # 也可传 tokenized 目录（自动取 **/*.bin）
    python check_longctx_data.py --shards .../ultrafineweb_en_v1_4 --sample 8 --json

判据（建议写进报告）：目标长度 T 的「可训练比例」= 属于 ≥T 文档的 token 占比。
  * ≥32K：建议 ≥20%
  * ≥128K：建议 ≥5%
  * ≥1M：通常 <1%，属正常（1M 靠 ABF 外推，不靠长文档）
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

try:
    import numpy as np
except ImportError:  # pragma: no cover
    print("FAIL: 需要 numpy（pip install numpy）", file=sys.stderr)
    sys.exit(2)


def natkey(p: str):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", os.path.basename(p))]


def expand(spec: str):
    if os.path.isdir(spec):
        return sorted(glob.glob(os.path.join(spec, "**", "*.bin"), recursive=True), key=natkey)
    return sorted(glob.glob(spec), key=natkey)


def scan(path: str, eod: int, targets, max_tokens: int, chunk: int = 8_000_000):
    a = np.memmap(path, dtype=np.int32, mode="r")
    n = int(a.size)
    if max_tokens and n > max_tokens:
        n = max_tokens
    stats = {"tokens": n, "docs": 0, "max_doc": 0,
             "ge": {t: {"docs": 0, "tokens": 0} for t in targets}}
    last = -1                      # 上一个 EOD 的位置
    scanned = 0
    for s in range(0, n, chunk):
        blk = np.asarray(a[s:s + min(chunk, n - s)])
        scanned += blk.size
        idx = np.flatnonzero(blk == eod)
        for i in idx:
            pos = s + int(i)
            L = pos - last - 1
            last = pos
            if L <= 0:
                continue
            stats["docs"] += 1
            if L > stats["max_doc"]:
                stats["max_doc"] = L
            for t in targets:
                if L >= t:
                    stats["ge"][t]["docs"] += 1
                    stats["ge"][t]["tokens"] += L
    # 末尾残段（无 EOD 结尾）也算一篇
    tail = scanned - last - 1
    if tail > 0:
        stats["docs"] += 1
        stats["max_doc"] = max(stats["max_doc"], tail)
        for t in targets:
            if tail >= t:
                stats["ge"][t]["docs"] += 1
                stats["ge"][t]["tokens"] += tail
    del a
    return stats


def main() -> None:
    ap = argparse.ArgumentParser(description="长上下文数据体检（文档长度分布）")
    ap.add_argument("--shards", required=True, help="glob 或目录")
    ap.add_argument("--eod-id", type=int, default=129280, help="文档分隔符（tokenizer_eod=129280）")
    ap.add_argument("--targets", default="32768,131072,1048576")
    ap.add_argument("--sample", type=int, default=4, help="最多扫描多少个 shard（按自然序）")
    ap.add_argument("--max-gb", type=float, default=4.0, help="每个 shard 最多读多少 GB（默认 4）")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    files = expand(args.shards)
    if not files:
        print(f"FAIL: 没找到 shard：{args.shards}", file=sys.stderr)
        sys.exit(2)
    sel = files[:args.sample]
    targets = [int(x) for x in args.targets.replace(" ", "").split(",") if x]
    max_tokens = int(args.max_gb * (1024 ** 3) / 4)     # int32

    print(f"# 扫描 {len(sel)}/{len(files)} 个 shard（每片上限 {args.max_gb}GB）")
    print(f"# eod_id={args.eod_id}  targets={targets}")
    out = {"eod_id": args.eod_id, "files": [], "targets": targets}

    agg = {"tokens": 0, "docs": 0, "max_doc": 0,
           "ge": {t: {"docs": 0, "tokens": 0} for t in targets}}
    for f in sel:
        st = scan(f, args.eod_id, targets, max_tokens)
        agg["tokens"] += st["tokens"]
        agg["docs"] += st["docs"]
        agg["max_doc"] = max(agg["max_doc"], st["max_doc"])
        for t in targets:
            agg["ge"][t]["docs"] += st["ge"][t]["docs"]
            agg["ge"][t]["tokens"] += st["ge"][t]["tokens"]
        out["files"].append({"file": f, **{k: st[k] for k in ("tokens", "docs", "max_doc")}})
        print(f"  {os.path.basename(f):<40} tokens={st['tokens']:>12,} docs={st['docs']:>10,} "
              f"max_doc={st['max_doc']:>9,}")

    print()
    print(f"合计：tokens={agg['tokens']:,}  docs={agg['docs']:,}  "
          f"平均文档={agg['tokens'] / max(agg['docs'], 1):.1f} 最长={agg['max_doc']:,}")
    print()
    hdr = f"{'target':>10} {'docs≥T':>12} {'docs%':>7} {'tokens≥T':>16} {'token%':>7} 判据"
    print(hdr)
    print("-" * len(hdr))
    verdicts = {}
    for t in targets:
        d = agg["ge"][t]["docs"]
        tk = agg["ge"][t]["tokens"]
        dp = 100.0 * d / max(agg["docs"], 1)
        tp = 100.0 * tk / max(agg["tokens"], 1)
        need = {32768: 20.0, 131072: 5.0}.get(t, 0.0)
        ok = "OK" if tp >= need else f"LOW(<{need:g}%)"
        if t == 1048576:
            ok = "n/a（1M 靠 ABF 外推，不要求长文档）"
        verdicts[t] = {"token_pct": round(tp, 3), "verdict": ok}
        print(f"{t:>10,} {d:>12,} {dp:>6.2f}% {tk:>16,} {tp:>6.2f}% {ok}")

    print()
    print("# 读法：token% 才是「长上下文训练里真正有多长上下文」的比例；docs% 只看文档数。")
    print("# 若 32K 的 token% <20% ⇒ 建议长上下文阶段改用「长文档优先采样」或补长文档数据源。")
    out["aggregate"] = agg
    out["verdicts"] = verdicts
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
