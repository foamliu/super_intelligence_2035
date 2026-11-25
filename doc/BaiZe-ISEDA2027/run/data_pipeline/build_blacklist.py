#!/usr/bin/env python3
"""build_blacklist.py — 污染隔离黑名单指纹生成器（红线 P0）。

只读评测集 `EDA-Eval-PyAether-v20260311.jsonl`，产出**内容安全**的黑名单指纹
（哈希 / MinHash 签名），**绝不落盘任何评测集的原始 prompt / 函数名 / 参考解 / 断言**。
因此黑名单产物可安全 `git add`（脚本目录），用于训练集侧扫描的同闸比对。

指纹方法（可复现，阈值见 CONTAMINATION_CHECK.md）：
  1. 逐任务拼接"禁止入训练集"的字段：prompt + entry_point + test
     （canonical_solution 若存在也一并纳入；本版本 jsonl 无该字段）。
     注意：metadata.source（如 pyAether.xxx）是"来源 API 名"，属 API 参考文档侧，
     允许入训练集，因此**不**纳入黑名单。
  2. normalize(text)：小写；把连续非 [a-z0-9_] 字符映射为单个空格。
  3. 去掉空格后做**字符级 13-gram** 切分（shingle），每个任务 = 一个 shingle 集合。
  4. MinHash(k=128, 64-bit 双哈希, 确定性 FNV-1a) 得到每任务压缩签名（Jaccard 估计器）。
  5. 全量去重后的 13-gram 用 FNV-1a 64-bit 哈希，落盘为精确命中集合。

产物（默认输出到 run/data_pipeline/blacklist/）：
  - meta.json              每任务 {task_id, n_shingles, minhash[128], entry_point_sha256, fields}
  - ngram_hashes.txt       全局去重 13-gram 的 64-bit hex（每行一个，排序）
  - entry_points.sha256    entry_point 的 sha256（额外标识符信号，二次校验函数名）

用法：
  python build_blacklist.py \
    --eval-jsonl /nas_train/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl \
    --out-dir run/data_pipeline/blacklist
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

MASK64 = (1 << 64) - 1
FNV_OFFSET = 0xCBF29CE484222325
FNV_PRIME = 0x100000001B3

# 敏感字段（禁止入训练集）；canonical_solution 若存在也纳入
FORBIDDEN_FIELDS = ["prompt", "entry_point", "test", "canonical_solution"]


def fnv1a_64(data: bytes, seed: int = FNV_OFFSET) -> int:
    """确定性 FNV-1a 64-bit 哈希（跨进程/跨机器可复现，不依赖 PYTHONHASHSEED）。"""
    h = seed
    for b in data:
        h ^= b
        h = (h * FNV_PRIME) & MASK64
    return h


def normalize(text: str) -> str:
    """NFKC 兼容归一化 + 小写 + 把非 Unicode 单词字符折叠为单个空格。

    关键修正（2026-10-01）：旧实现 `[^a-z0-9_]` 会把**所有非 ASCII 字符**
    （含 CJK 汉字）当空格丢弃，导致中文评测 prompt 完全丧失指纹（cuhk 80 任务
    因此有 59 条被误判为"过短跳过"）。现先做 NFKC，把 Kangxi 部首兼容字符
    （如 ⼀ U+2F00 → 一 U+4E00）映射回标准 CJK，再用 Unicode `\\w` 保留全部
    文字/数字/下划线。对纯 ASCII 英文文本行为与旧版一致（无回归）。
    """
    if not text:
        return ""
    t = unicodedata.normalize("NFKC", text).lower()
    return " ".join(re.sub(r"[^\w]+", " ", t, flags=re.UNICODE).split())


def shingles(text: str, n: int = 13):
    """返回规范化文本（去空格后）的字符级 n-gram 集合。"""
    s = normalize(text).replace(" ", "")
    if len(s) < n:
        return set()
    return {s[i:i + n] for i in range(len(s) - n + 1)}


def short_shingles(text: str, n: int = 8):
    """短字符串兜底指纹：当主 n-gram 无法切分（文本过短）时，用更短的 n 切分。

    返回 (shingle 集合, 实际使用的 n)。若规范化文本仍不足 n，则返回整个
    归一化字符串作为单 token（整串精确匹配，实际 n = 字符串长度）。
    注意建黑名单侧与扫描侧各自调用本函数，两侧逻辑对称，才能正确匹配。
    """
    s = normalize(text).replace(" ", "")
    if not s:
        return set(), 0
    if len(s) < n:
        return {s}, len(s)
    return {s[i:i + n] for i in range(len(s) - n + 1)}, n


def minhash(shingle_set, k: int = 128):
    """确定性 MinHash 签名：对每个 shingle 用两个 64-bit 独立哈希做 (h1 + i*h2) mod 2^64。"""
    vec = [MASK64] * k
    seed2 = 0x84222325CBF29CE4  # FNV offset 的反序，作为第二独立哈希种子
    for s in shingle_set:
        b = s.encode("utf-8", "ignore")
        h1 = fnv1a_64(b, FNV_OFFSET)
        h2 = fnv1a_64(b, seed2)
        for i in range(k):
            hval = (h1 + i * h2) & MASK64
            if hval < vec[i]:
                vec[i] = hval
    return vec


def jaccard_minhash(sig_a, sig_b) -> float:
    """MinHash 签名估计 Jaccard。"""
    if not sig_a or not sig_b:
        return 0.0
    k = len(sig_a)
    agree = sum(1 for a, b in zip(sig_a, sig_b) if a == b)
    return agree / k


def main() -> int:
    ap = argparse.ArgumentParser(description="EDA-Eval-PyAether 黑名单指纹生成")
    ap.add_argument("--eval-jsonl", nargs="+", required=True, help="评测集 jsonl（只读，可多文件求并集黑名单）")
    ap.add_argument("--out-dir", required=True, help="黑名单输出目录（落盘指纹，不含原始内容）")
    ap.add_argument("--ngram", type=int, default=13)
    ap.add_argument("--short-ngram", type=int, default=8, help="短文本兜底 n-gram（默认 8）")
    ap.add_argument("--minhash-k", type=int, default=128)
    args = ap.parse_args()

    srcs = [Path(p) for p in args.eval_jsonl]
    missing = [str(s) for s in srcs if not s.exists()]
    if missing:
        print(f"[error] 评测集不存在: {missing}", file=sys.stderr)
        return 1

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    tasks = []
    global_shingles = {}  # shingle -> fnv hash，全局去重（取并集）
    global_short_shingles = {}  # 短文本兜底 shingle -> fnv hash（仅主 n-gram 无法切分的任务）
    n_lines = 0
    for src in srcs:
        stem = src.stem
        with open(src, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                n_lines += 1
                obj = json.loads(line)
                # task_id 带来源文件名前缀，避免多快照 task_id 重名冲突
                tid = f"{stem}:{obj.get('task_id', f'unknown-{n_lines}')}"
                fields_present = [k for k in FORBIDDEN_FIELDS if obj.get(k)]
                # 拼接禁止字段内容
                parts = [str(obj[k]) for k in FORBIDDEN_FIELDS if obj.get(k) is not None]
                combined = "\n".join(parts)
                sh = shingles(combined, args.ngram)
                sig = minhash(sh, args.minhash_k)
                # 短文本兜底：仅当主 n-gram 无法指纹（文本过短）时生成短 shingle
                sh_short = sh_short_sig = None
                short_ngram_used = 0
                if not sh:
                    sh_short, short_ngram_used = short_shingles(combined, args.short_ngram)
                    sh_short_sig = minhash(sh_short, args.minhash_k) if sh_short else []
                ep = str(obj.get("entry_point", ""))
                tasks.append({
                    "task_id": tid,
                    "source": str(src),
                    "fields": fields_present,
                    "n_shingles": len(sh),
                    "minhash": sig,
                    "short": not bool(sh),
                    "n_short_shingles": len(sh_short) if sh_short is not None else 0,
                    "short_ngram": short_ngram_used,
                    "minhash_short": sh_short_sig or [],
                    "entry_point_sha256": hashlib.sha256(ep.encode("utf-8")).hexdigest(),
                })
                for s in sh:
                    global_shingles.setdefault(s, fnv1a_64(s.encode("utf-8", "ignore")))
                if sh_short is not None:
                    for s in sh_short:
                        global_short_shingles.setdefault(s, fnv1a_64(s.encode("utf-8", "ignore")))

    # 写 ngram_hashes.txt（排序去重后只存 64-bit hex）
    hashes = sorted(set(global_shingles.values()))
    hash_path = out / "ngram_hashes.txt"
    with open(hash_path, "w", encoding="utf-8") as f:
        for h in hashes:
            f.write(f"{h:016x}\n")

    # 写 short_ngram_hashes.txt（短文本兜底指纹，排序去重后 64-bit hex）
    short_hashes = sorted(set(global_short_shingles.values()))
    short_hash_path = out / "short_ngram_hashes.txt"
    with open(short_hash_path, "w", encoding="utf-8") as f:
        for h in short_hashes:
            f.write(f"{h:016x}\n")

    # 写 entry_points.sha256（函数名指纹，二次校验）
    ep_path = out / "entry_points.sha256"
    with open(ep_path, "w", encoding="utf-8") as f:
        for t in tasks:
            f.write(f"{t['task_id']}\t{t['entry_point_sha256']}\n")

    n_short_tasks = sum(1 for t in tasks if t["short"])

    # 写 meta.json
    meta = {
        "eval_jsonl": str(srcs[0]),
        "eval_jsonls": [str(s) for s in srcs],
        "ngram": args.ngram,
        "short_ngram": args.short_ngram,
        "minhash_k": args.minhash_k,
        "normalization": "NFKC -> lowercase -> collapse non Unicode \\w to space -> strip spaces -> char n-gram",
        "forbidden_fields": FORBIDDEN_FIELDS,
        "note": "metadata.source 属 API 参考文档侧（允许入训练集），未纳入黑名单",
        "num_tasks": len(tasks),
        "num_lines": n_lines,
        "total_distinct_ngrams": len(hashes),
        "total_distinct_short_ngrams": len(short_hashes),
        "num_short_tasks": n_short_tasks,
        "tasks": tasks,
    }
    meta_path = out / "meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"[done] {len(tasks)} 任务 / {len(global_shingles)} 去重前 shingle / "
          f"{len(hashes)} 去重后 {args.ngram}-gram 哈希；"
          f"短文本兜底 {n_short_tasks} 任务 / {len(short_hashes)} 去重后 {args.short_ngram}-gram 哈希")
    print(f"      产物: {meta_path}")
    print(f"      产物: {hash_path} ({len(hashes)} 行)")
    print(f"      产物: {short_hash_path} ({len(short_hashes)} 行)")
    print(f"      产物: {ep_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())