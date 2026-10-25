#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_disk_cleanup_candidates.py — 产出磁盘清理候选清单（运维令 2026-10-25 18:5x ②）.

只做**测量**，不删任何文件。输出 TSV：path / category / 表观字节 / 实占字节 /
inode链接数 / 被tokenized引用 / 判定 / 理由；按实占降序。

候选类别（18:5x ②）：
  ① text/staging_r3/ 剩余纯输入符号链接暂存目录   → 可删
  ② 无 .idx 的孤儿 .bin / .partial / .bak        → 需区分：活跃写入=保留，崩溃残留=可删
  ③ 空目录                                          → 可删
  ④ /tmp/tokenize_untokenized_*.log（保留最新 3 份）→ 其余可删
  ⑤ 已被 tokenized/ 收录且 inode 链接>1 的重复副本  → 可删但实占=0（hardlink）

实占字节口径：hardlink 同 inode 多名 ⇒ 删一个释放 0（除非删最后一个链接）；
              故 link_count>1 的候选实占=0。symlink/普通文件 link_count=1 ⇒ 实占=表观。

不可删（不在候选内）：/nas_env/full_*、tokenized/ 镜像与 INDEX.tsv、DATA_LEDGER.md、
                      /nas_inference 下载 parquet、任何 .json manifest。
"""
import os, sys, csv, subprocess, glob

TEXT = "/nas_train/app.e0031982/datasets/baize-data/text"
STAGING_R3 = os.path.join(TEXT, "staging_r3")
TOKENIZED = "/nas_train/app.e0031982/datasets/baize-data/tokenized"
TMP_LOG_GLOB = "/tmp/tokenize_untokenized_*.log"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "disk_cleanup_candidates_20261025.tsv")


def active_output_prefixes():
    """从 ps 抓正在跑的 preprocess_data 的 --output-prefix 集合（活跃写入，不可删）。"""
    active = set()
    try:
        out = subprocess.check_output(["ps", "-eo", "args="], text=True)
    except Exception:
        return active
    for line in out.splitlines():
        if "preprocess_data" not in line:
            continue
        parts = line.split()
        for i, p in enumerate(parts):
            if p == "--output-prefix" and i + 1 < len(parts):
                active.add(parts[i + 1])
    return active


def du_bytes(path):
    try:
        return int(subprocess.check_output(["du", "-sb", path], stderr=subprocess.DEVNULL, text=True).split()[0])
    except Exception:
        return 0


def stat_links(path):
    try:
        s = os.stat(path, follow_symlinks=False)
        return s.st_nlink, s.st_size
    except Exception:
        return 0, 0


def is_tokenized_ref(path):
    """该文件是否被 tokenized/ 镜像引用（samefile）。"""
    try:
        r = subprocess.run(["find", TOKENIZED, "-samefile", path],
                           capture_output=True, text=True, timeout=120)
        return bool(r.stdout.strip())
    except Exception:
        return False


def real_occupiable(apparent, link_count, tokenized_ref):
    """实占：link_count>1 且被 tokenized 引用 ⇒ 删此名释放 0（同名 inode 仍被镜像持有）。"""
    if link_count > 1 and tokenized_ref:
        return 0
    if link_count > 1:
        return apparent // link_count
    return apparent


def main():
    active = active_output_prefixes()
    print(f"[info] 活跃 preprocess_data output-prefix 数: {len(active)}")
    rows = []

    # ① staging_r3 剩余目录（纯符号链接暂存）
    if os.path.isdir(STAGING_R3):
        for name in sorted(os.listdir(STAGING_R3)):
            d = os.path.join(STAGING_R3, name)
            if not os.path.isdir(d):
                continue
            app = du_bytes(d)
            try:
                nlink = int(subprocess.check_output(
                    ["find", d, "-type", "l"], stderr=subprocess.DEVNULL, text=True).count("\n"))
            except Exception:
                nlink = 0
            rows.append({"path": d, "category": "①staging_r3暂存",
                         "apparent": app, "real": app, "inode_links": 1,
                         "tokenized_ref": "N", "verdict": "可删",
                         "reason": f"纯输入符号链接暂存({nlink} symlinks)，已被 full_*/env14 覆盖或不可映射"})

    # ② 无 .idx 的孤儿 .bin（区分活跃 vs 崩溃残留）+ .partial + .bak
    for b in sorted(glob.glob(os.path.join(TEXT, "*.bin"))):
        base = b[:-4]
        if os.path.exists(base + ".idx"):
            continue
        app = os.path.getsize(b) if os.path.exists(b) else 0
        link_count, _ = stat_links(b)
        tok_ref = "Y" if link_count > 1 and is_tokenized_ref(b) else "N"
        real = real_occupiable(app, link_count, tok_ref == "Y")
        if b in active or any(b.startswith(p) for p in active):
            verdict, reason = "保留", "活跃分词写入中（preprocess_data --output-prefix 命中），.idx 待完成后写出"
        else:
            verdict, reason = "可删", "无 .idx 且无活跃写入 ⇒ 崩溃残留孤儿 .bin"
        rows.append({"path": b, "category": "②孤儿.bin", "apparent": app, "real": real,
                     "inode_links": link_count, "tokenized_ref": tok_ref,
                     "verdict": verdict, "reason": reason})

    for pat in ("*.partial", "*.bak"):
        for f in sorted(glob.glob(os.path.join(TEXT, pat))):
            app = os.path.getsize(f) if os.path.exists(f) else 0
            rows.append({"path": f, "category": "②partial/bak", "apparent": app, "real": app,
                         "inode_links": 1, "tokenized_ref": "N", "verdict": "可删",
                         "reason": "分词崩溃/备份残留"})

    # ③ 空目录
    for d in [STAGING_R3, TEXT]:
        if not os.path.isdir(d):
            continue
        try:
            empty = subprocess.check_output(["find", d, "-maxdepth", "1", "-type", "d", "-empty"],
                                            stderr=subprocess.DEVNULL, text=True).strip().splitlines()
        except Exception:
            empty = []
        for e in empty:
            rows.append({"path": e, "category": "③空目录", "apparent": 0, "real": 0,
                         "inode_links": 1, "tokenized_ref": "N", "verdict": "可删", "reason": "空目录"})

    # ④ /tmp 日志（保留最新 3 份）
    logs = sorted(glob.glob(TMP_LOG_GLOB), key=os.path.getmtime, reverse=True)
    for f in logs[3:]:
        app = os.path.getsize(f)
        rows.append({"path": f, "category": "④/tmp旧日志", "apparent": app, "real": app,
                     "inode_links": 1, "tokenized_ref": "N", "verdict": "可删",
                     "reason": "保留最新3份之外的旧分词日志"})

    # ⑤ 已被 tokenized/ 收录且 inode 链接>1 的重复副本（env14_* in text/）
    for b in sorted(glob.glob(os.path.join(TEXT, "env14_*.bin"))):
        base = b[:-4]
        if not os.path.exists(base + ".idx"):
            continue
        link_count, app = stat_links(b)
        if link_count <= 1:
            continue
        tok_ref = "Y" if is_tokenized_ref(b) else "N"
        real = 0 if tok_ref == "Y" else app // link_count
        rows.append({"path": b, "category": "⑤hardlink重复", "apparent": app, "real": real,
                     "inode_links": link_count, "tokenized_ref": tok_ref,
                     "verdict": "可删" if tok_ref == "Y" else "待定",
                     "reason": "已 hardlink 进 tokenized/ 镜像，删此名释放0字节（tidy）" if tok_ref == "Y"
                               else "link>1 但未确认 tokenized 引用"})

    rows.sort(key=lambda r: r["real"], reverse=True)

    cols = ["path", "category", "apparent_bytes", "real_bytes", "inode_links",
            "tokenized_ref", "verdict", "reason"]
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow({"path": r["path"], "category": r["category"],
                        "apparent_bytes": r["apparent"], "real_bytes": r["real"],
                        "inode_links": r["inode_links"], "tokenized_ref": r["tokenized_ref"],
                        "verdict": r["verdict"], "reason": r["reason"]})

    n = len(rows)
    n_del = sum(1 for r in rows if r["verdict"] == "可删")
    n_keep = sum(1 for r in rows if r["verdict"] == "保留")
    sum_app_del = sum(r["apparent"] for r in rows if r["verdict"] == "可删")
    sum_real_del = sum(r["real"] for r in rows if r["verdict"] == "可删")
    print(f"[ok] wrote {OUT} ({n} rows)")
    print(f"  可删: {n_del}  保留(活跃): {n_keep}  待定: {n - n_del - n_keep}")
    print(f"  可删表观合计: {sum_app_del:,} B ({sum_app_del/1024**3:.4f} GB)")
    print(f"  可删实占合计: {sum_real_del:,} B ({sum_real_del/1024**3:.4f} GB)  ← 真实释放量")
    if n_keep:
        print(f"  ⚠️ {n_keep} 个孤儿 .bin 是活跃分词输出（非崩溃残留），已判保留")


if __name__ == "__main__":
    main()
