#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""02_make_sample.py — 从 summary.tsv 分层抽样，生成 triage 输入。

用法:
  python3 02_make_sample.py --summary summary.tsv [--texts DIR] \
      [--per-bin 25] [--out triage_input.jsonl] [--seed 13]

summary.tsv 列（现有扫描产物）:
  ip host user session_file match_count keywords tools

texts 目录: <session_file>.txt（由 01_condense_session.py 生成）
缺失文本的样本会标 needs_fetch=true，由 agent 去 open_session 补齐。
"""
import argparse
import hashlib
import json
import os
import random
import sys

BINS = [(1, 40), (40, 100), (100, 300), (300, 10 ** 9)]


def sid_of(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:12]


def bin_of(mc):
    for i, (lo, hi) in enumerate(BINS):
        if lo <= mc < hi:
            return i
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", required=True)
    ap.add_argument("--texts", default="")
    ap.add_argument("--per-bin", type=int, default=25)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=13)
    args = ap.parse_args()

    rows, seen = [], set()
    with open(args.summary, encoding="utf-8", errors="ignore") as f:
        header = f.readline().rstrip("\n").split("\t")
        idx = {k: i for i, k in enumerate(header)}
        need = ["host", "user", "session_file", "match_count"]
        for k in need:
            if k not in idx:
                sys.exit(f"缺列 {k}，实际表头: {header}")
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < len(header):
                p += [""] * (len(header) - len(p))
            sf = p[idx["session_file"]]
            if not sf or sf in seen:
                continue
            seen.add(sf)
            try:
                mc = int(float(p[idx["match_count"]] or 0))
            except ValueError:
                mc = 0
            rows.append({
                "sid": sid_of(sf),
                "session_file": sf,
                "host": p[idx["host"]],
                "user": p[idx["user"]],
                "mc": mc,
                "keywords": p[idx["keywords"]] if "keywords" in idx else "",
                "tools": p[idx["tools"]] if "tools" in idx else "",
                "bin": bin_of(mc),
            })

    rng = random.Random(args.seed)
    picked = []
    for b in range(len(BINS)):
        pool = [r for r in rows if r["bin"] == b]
        rng.shuffle(pool)
        picked.extend(pool[: args.per_bin])
        print(f"[sample] bin{b} {BINS[b]}: pool={len(pool)} picked={min(len(pool), args.per_bin)}")

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        for r in picked:
            txt = ""
            if args.texts:
                p = os.path.join(args.texts, r["session_file"] + ".txt")
                if os.path.isfile(p):
                    txt = open(p, encoding="utf-8", errors="ignore").read()
            r["text"] = txt
            r["needs_fetch"] = not bool(txt)
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    miss = sum(1 for r in picked if not r["text"])
    print(f"[sample] wrote {len(picked)} rows -> {args.out}  (needs_fetch={miss})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
