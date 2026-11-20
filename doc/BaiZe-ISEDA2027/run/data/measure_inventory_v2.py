#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""measure_inventory_v2.py — MiniCPM5 数据硬盘实测盘点 (v2, 2026-10-25)
口径: 以下载目录为准, 不自造数据源, 小计脚本求和.
产出: inventory_v2_20261025.tsv (供 gen_tokenized_inventory_report.py 读取)
每行 = 一个磁盘真实目录 (或 baize-data/text 内的一个前缀分组).
token: 已分词源用 .json num_tokens 求和(实测); 未分词源留空(生成器写 未分词).
字节: parquet下载目录与/nas_env目录用 du -sb; baize-data/text各前缀用该前缀文件 stat 求和.
"""
import os, json, glob, subprocess, sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
TSV_OUT = os.path.join(HERE, "inventory_v2_20261025.tsv")
OPENBMB = "/nas_train/app.e0031982/datasets/openbmb"
TEXT_DIR = "/nas_train/app.e0031982/datasets/baize-data/text"
NAS_ENV = "/nas_env/app.e0031982/baize-data"

def du_sb(path):
    try:
        out = subprocess.check_output(["du", "-sb", path], stderr=subprocess.DEVNULL)
        return int(out.split(b"\t")[0])
    except Exception:
        return 0

def count_glob(path, pattern):
    return len(glob.glob(os.path.join(path, pattern), recursive=True))

def fmt_mtime(ts):
    if not ts:
        return "—"
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")

def sum_tokens(path, pattern):
    total = 0; nf = 0
    for jf in glob.glob(os.path.join(path, pattern)):
        try:
            with open(jf) as fh:
                d = json.load(fh)
            total += int(d.get("num_tokens", 0)); nf += 1
        except Exception:
            pass
    return total, nf

def sum_bytes(path, pattern):
    total = 0
    for f in glob.glob(os.path.join(path, pattern)):
        try:
            total += os.path.getsize(f)
        except OSError:
            pass
    return total

def latest_mt(path, pattern):
    latest = 0.0
    for f in glob.glob(os.path.join(path, pattern), recursive=True):
        try:
            m = os.path.getmtime(f)
            if m > latest:
                latest = m
        except OSError:
            pass
    return latest

# SOURCES: (section, name, disk_dir, hf_repo_subdir, kind, prefix)
# kind: parquet / tokdir / tokprefix
SOURCES = [
    ("A", "base-en (ultrafineweb_en)",
     OPENBMB + "/Ultra-FineWeb/data/ultrafineweb_en",
     "openbmb/Ultra-FineWeb/data/ultrafineweb_en", "parquet", None),
    ("A", "en_v1_4 (ultrafineweb_en_v1_4)",
     OPENBMB + "/Ultra-FineWeb/data/ultrafineweb_en_v1_4",
     "openbmb/Ultra-FineWeb/data/ultrafineweb_en_v1_4", "parquet", None),
    ("A", "l1_en_hq (ultrafineweb_l1_en_hq)",
     OPENBMB + "/Ultra-FineWeb/data/ultrafineweb_l1_en_hq",
     "openbmb/Ultra-FineWeb/data/ultrafineweb_l1_en_hq", "parquet", None),
    ("A", "zh (ultrafineweb_zh)",
     OPENBMB + "/Ultra-FineWeb/data/ultrafineweb_zh",
     "openbmb/Ultra-FineWeb/data/ultrafineweb_zh", "parquet", None),
    ("A", "UltraX-Preview",
     OPENBMB + "/UltraX-Preview",
     "openbmb/UltraX-Preview", "parquet", None),
    ("B", "en_v1_4 分词产物 (env14_CC-MAIN-*)",
     TEXT_DIR, "baize-data/text  [env14_*]", "tokprefix", "env14_CC-MAIN-*"),
    ("B", "code 分词产物 (code_s*)",
     TEXT_DIR, "baize-data/text  [code_s*]", "tokprefix", "code_s*"),
    ("B", "l3 分词产物 (l3_s*)",
     TEXT_DIR, "baize-data/text  [l3_s*]", "tokprefix", "l3_s*"),
    ("B", "math 分词产物 (math_s*)",
     TEXT_DIR, "baize-data/text  [math_s*]", "tokprefix", "math_s*"),
    ("C", "UFW-L3 全量 (full_ufw_l3)",
     NAS_ENV + "/full_ufw_l3", "/nas_env/.../full_ufw_l3", "tokdir", None),
    ("C", "Code-L2 全量 (full_ultradata_code_l2)",
     NAS_ENV + "/full_ultradata_code_l2", "/nas_env/.../full_ultradata_code_l2", "tokdir", None),
    ("C", "Code-L3 全量 (full_ultradata_code_l3)",
     NAS_ENV + "/full_ultradata_code_l3", "/nas_env/.../full_ultradata_code_l3", "tokdir", None),
    ("C", "Math-L1 全量 (full_ultradata_math_l1)",
     NAS_ENV + "/full_ultradata_math_l1", "/nas_env/.../full_ultradata_math_l1", "tokdir", None),
    ("C", "Math-L3 全量 (full_ultradata_math_l3)",
     NAS_ENV + "/full_ultradata_math_l3", "/nas_env/.../full_ultradata_math_l3", "tokdir", None),
]

rows = []
for (sec, name, ddir, hf, kind, prefix) in SOURCES:
    exists = os.path.isdir(ddir)
    if kind == "parquet":
        pq = count_glob(ddir, "**/*.parquet") if exists else 0
        inc = count_glob(ddir, "**/*.incomplete") if exists else 0
        bcount = icount = 0
        nbytes = du_sb(ddir) if exists else 0
        tokens = 0; is_tok = "no"
        mt = latest_mt(ddir, "**/*.parquet") if exists else 0.0
        notes = "原始 parquet 下载目录"
    elif kind == "tokdir":
        pq = inc = 0
        bcount = count_glob(ddir, "*.bin")
        icount = count_glob(ddir, "*.idx")
        nbytes = du_sb(ddir) if exists else 0
        tokens, _ = sum_tokens(ddir, "*.json")
        is_tok = "yes" if bcount > 0 else "no"
        mt = latest_mt(ddir, "*.bin") if exists else 0.0
        notes = "全量分词产物(/nas_env, 软链接 BaiZe-ISEDA2027/data/full_*)"
    elif kind == "tokprefix":
        pq = inc = 0
        bpat = prefix + ".bin"; ipat = prefix + ".idx"; jpat = prefix + ".json"
        bcount = count_glob(ddir, bpat)
        icount = count_glob(ddir, ipat)
        nbytes = (sum_bytes(ddir, bpat) + sum_bytes(ddir, ipat) + sum_bytes(ddir, jpat))
        tokens, _ = sum_tokens(ddir, jpat)
        is_tok = "yes" if bcount > 0 else "no"
        mt = latest_mt(ddir, bpat)
        notes = "分词产物(baize-data/text 内按前缀分组)"
    else:
        continue
    rows.append({"section": sec, "source_name": name, "disk_dir": ddir,
        "hf_repo_subdir": hf, "parquet": pq, "incomplete": inc,
        "bin": bcount, "idx": icount, "bytes": nbytes, "tokens": tokens,
        "is_tokenized": is_tok, "latest_mtime": fmt_mtime(mt),
        "exists": "yes" if exists else "no", "notes": notes})

cols = ["section", "source_name", "disk_dir", "hf_repo_subdir", "parquet",
        "incomplete", "bin", "idx", "bytes", "tokens", "is_tokenized",
        "latest_mtime", "exists", "notes"]
with open(TSV_OUT, "w") as f:
    f.write("\t".join(cols) + "\n")
    for r in rows:
        f.write("\t".join(str(r[c]) for c in cols) + "\n")

print("=== inventory_v2 measurement summary ===")
print("TSV:", TSV_OUT)
print("%-2s %-40s %7s %7s %5s %5s %16s %16s %4s" % (
    "S", "source", "parquet", "incomp", "bin", "idx", "bytes", "tokens", "tok"))
for r in rows:
    print("%-2s %-40s %7d %7d %5d %5d %16d %16d %4s" % (
        r["section"], r["source_name"][:40], r["parquet"], r["incomplete"],
        r["bin"], r["idx"], r["bytes"], r["tokens"], r["is_tokenized"]))
def sub(sec):
    sel = [r for r in rows if r["section"] == sec]
    return (sum(r["bytes"] for r in sel), sum(r["tokens"] for r in sel),
            sum(r["bin"] for r in sel), sum(r["idx"] for r in sel),
            sum(r["parquet"] for r in sel), len(sel))
for sec in ("A", "B", "C"):
    b, t, bn, ix, pq, n = sub(sec)
    print("  section %s 小计: %d rows parquet=%d bin=%d idx=%d bytes=%d tokens=%d" % (
        sec, n, pq, bn, ix, b, t))
tot_b = sum(r["bytes"] for r in rows); tot_t = sum(r["tokens"] for r in rows)
tot_bn = sum(r["bin"] for r in rows); tot_ix = sum(r["idx"] for r in rows)
print("  总计: %d rows bin=%d idx=%d bytes=%d tokens=%d" % (
    len(rows), tot_bn, tot_ix, tot_b, tot_t))
print("  bin==idx ?", tot_bn == tot_ix)
