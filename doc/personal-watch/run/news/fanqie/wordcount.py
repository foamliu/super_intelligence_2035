#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""wordcount.py — 42 章字数核算 + 章节/配图清单（可复现，零依赖）。

口径（两种，均不含空白）：
  cjk      = 中文字符数（[\\u4e00-\\u9fff]，不含标点/数字/字母）
  nonspace = 非空白字符数（含标点、数字、字母；≈ 番茄后台常见「字数」口径）
  raw      = 文件总字节解码后的全部字符数（含 Markdown 标记、换行）

用法：
  python3 wordcount.py                 # 打印全表
  python3 wordcount.py --csv out.csv   # 同时导出 CSV
"""
import csv
import glob
import os
import re
import sys

ROOT = os.environ.get("CHAPTERS_DIR", "/home/liuyang/super_intelligence_2035/chapters_v1_1")
IMG = os.environ.get("IMAGES_DIR", "/home/liuyang/super_intelligence_2035/images")


def stats(path):
    t = open(path, encoding="utf-8").read()
    cjk = len(re.findall(r"[\u4e00-\u9fff]", t))
    ns = len(re.sub(r"\s", "", t))
    title = t.lstrip().splitlines()[0].strip() if t.strip() else ""
    return cjk, ns, len(t), title


def main():
    argv = sys.argv[1:]
    files = sorted(glob.glob(os.path.join(ROOT, "[0-9][0-9]-*.md")))
    if len(files) != 42:
        print("WARN: 章数 = %d（期望 42）" % len(files))
    imgs = set(os.listdir(IMG)) if os.path.isdir(IMG) else set()
    rows = []
    tc = tn = 0
    for f in files:
        b = os.path.basename(f)[:-3]
        cjk, ns, raw, title = stats(f)
        tc += cjk
        tn += ns
        img = b + ".jpg" if b + ".jpg" in imgs else (b + ".png" if b + ".png" in imgs else "")
        rows.append([b, title, cjk, ns, raw, img])
    print("%-34s %-14s %7s %8s %7s  %s" % ("file", "title", "cjk", "nonspace", "raw", "image"))
    for r in rows:
        print("%-34s %-14s %7d %8d %7d  %s" % (r[0], r[1][:12], r[2], r[3], r[4], r[5] or "(none)"))
    print("TOTAL chapters=%d  cjk=%d  nonspace=%d" % (len(rows), tc, tn))
    print("SHORTEST 5:", [(r[0], r[2]) for r in sorted(rows, key=lambda x: x[2])[:5]])
    if "--csv" in argv:
        out = argv[argv.index("--csv") + 1]
        with open(out, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["file", "title", "cjk", "nonspace", "raw", "image"])
            w.writerows(rows)
        print("csv ->", out)


if __name__ == "__main__":
    main()
