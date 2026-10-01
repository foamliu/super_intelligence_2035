#!/usr/bin/env python3
"""check_contamination.py — 训练集侧污染扫描（红线 P0，与黑名单同闸）。

对每一份候选训练文档计算与黑名单的**精确 13-gram 重合率**，超阈值即标记；
被标记文档再与 158 个任务逐一用 MinHash 估计 Jaccard，定位最可能撞源的任务。
本脚本同时用于预训练语料与 SFT 语料（同闸）。

用法：
  python check_contamination.py \\
    --blacklist-dir run/data_pipeline/blacklist \\
    --input <parquet目录 | .jsonl | .txt | 单个.parquet> \\
    --ngram 13 --threshold 0.8 --max-docs 2000 \\
    --out /tmp/contam_smoke.md

输入格式自动探测：
  - 目录且含 *.snappy.parquet / *.parquet  → content 列（L3 通用文本）
  - 单文件 .parquet                           → content 列
  - .jsonl                                   → 字段 --jsonl-field（默认尝试 text/content/prompt）
  - .txt / 其他                              → 整文件为一段文本
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_blacklist import fnv1a_64, shingles, short_shingles, minhash, jaccard_minhash  # noqa: E402


def _read_hash_set(path: Path) -> set:
    hashes = set()
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    hashes.add(int(line, 16))
    return hashes


def load_blacklist(blacklist_dir: str):
    bd = Path(blacklist_dir)
    meta = json.loads((bd / "meta.json").read_text(encoding="utf-8"))
    hashes = _read_hash_set(bd / "ngram_hashes.txt")
    short_hashes = _read_hash_set(bd / "short_ngram_hashes.txt")
    return meta, hashes, short_hashes


def _flatten(v) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    if isinstance(v, list):
        segs = []
        for t in v:
            if isinstance(t, dict):
                segs.append(str(t.get("user") or "") + " " + str(t.get("assistant") or ""))
            else:
                segs.append(str(t))
        return "\n".join(segs)
    return str(v)


def iter_texts(inp: str, max_docs: int, jsonl_field: str):
    """流式产出 (idx, text)。"""
    p = Path(inp)
    count = 0

    if p.is_dir():
        files = sorted(list(p.glob("*.snappy.parquet")) + list(p.glob("*.parquet")))
        import pyarrow.parquet as pq
        for pf in files:
            try:
                parrot = pq.ParquetFile(str(pf))
            except Exception as e:
                yield -1, f"__PARQUET_ERROR__{pf}:{e}"
                continue
            for batch in parrot.iter_batches(batch_size=1024):
                col = None
                if "content" in batch.schema.names:
                    col = "content"
                elif "texts" in batch.schema.names:
                    col = "texts"
                elif "text" in batch.schema.names:
                    col = "text"
                if col is None:
                    break
                for v in batch.column(col).to_pylist():
                    if max_docs is not None and count >= max_docs:
                        return
                    yield count, _flatten(v)
                    count += 1
    elif p.suffix == ".parquet":
        import pyarrow.parquet as pq
        parrot = pq.ParquetFile(str(p))
        for batch in parrot.iter_batches(batch_size=1024):
            col = "content" if "content" in batch.schema.names else (
                "texts" if "texts" in batch.schema.names else "text")
            for v in batch.column(col).to_pylist():
                if max_docs is not None and count >= max_docs:
                    return
                yield count, _flatten(v)
                count += 1
    elif p.suffix == ".jsonl":
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                text = None
                for key in ([jsonl_field] if jsonl_field else ["text", "content", "prompt"]):
                    if key in obj:
                        text = obj[key]
                        break
                if text is None:
                    text = json.dumps(obj, ensure_ascii=False)
                if max_docs is not None and count >= max_docs:
                    return
                yield count, _flatten(text)
                count += 1
    else:
        with open(p, "r", encoding="utf-8") as f:
            if max_docs is not None and count >= max_docs:
                return
            yield count, f.read()
            count += 1

def main() -> int:
    ap = argparse.ArgumentParser(description="训练集侧污染扫描")
    ap.add_argument("--blacklist-dir", required=True)
    ap.add_argument("--input", required=True)
    ap.add_argument("--ngram", type=int, default=13)
    ap.add_argument("--threshold", type=float, default=0.8)
    ap.add_argument("--max-docs", type=int, default=None)
    ap.add_argument("--jsonl-field", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    meta, global_hashes, short_hashes = load_blacklist(args.blacklist_dir)
    tasks = meta["tasks"]
    n_tasks = meta["num_tasks"]
    ngram = args.ngram or meta["ngram"]
    short_ngram = meta.get("short_ngram", 8)

    scanned = 0
    short = 0
    flagged = 0
    hits = []
    for idx, text in iter_texts(args.input, args.max_docs, args.jsonl_field):
        if text.startswith("__PARQUET_ERROR__"):
            continue
        scanned += 1
        sh = shingles(text, ngram)
        doc_flags = False
        main_overlap = total = ratio = short_overlap = 0
        doc_sig = None
        doc_short_sig = None

        if sh:
            doc_hashes = {fnv1a_64(s.encode("utf-8", "ignore")) for s in sh}
            total = len(doc_hashes)
            main_overlap = len(doc_hashes & global_hashes)
            ratio = main_overlap / total
            if ratio >= args.threshold:
                doc_flags = True
                doc_sig = minhash(sh, meta["minhash_k"])
        else:
            short += 1  # 主 n-gram 无法覆盖（文本过短），走短文本兜底

        # 短文本兜底：不管主 tier 是否命中都扫（用于捕捉嵌在长文档中的中文短 prompt）
        doc_short, _ = short_shingles(text, short_ngram)
        if doc_short:
            doc_short_hashes = {fnv1a_64(s.encode("utf-8", "ignore")) for s in doc_short}
            short_overlap = len(doc_short_hashes & short_hashes)
            if short_overlap >= 1:
                doc_flags = True
                doc_short_sig = minhash(doc_short, meta["minhash_k"])

        if doc_flags:
            flagged += 1
            best_tid, best_j = None, 0.0
            for t in tasks:
                j = jaccard_minhash(doc_sig, t["minhash"]) if doc_sig is not None and t["minhash"] else 0.0
                if doc_short_sig is not None and t.get("minhash_short"):
                    j = max(j, jaccard_minhash(doc_short_sig, t["minhash_short"]))
                if j > best_j:
                    best_j, best_tid = j, t["task_id"]
            hits.append({
                "doc_idx": idx,
                "overlap": main_overlap,
                "total": total,
                "ratio": round(ratio, 4),
                "short_overlap": short_overlap,
                "best_task": best_tid,
                "jaccard_est": round(best_j, 4),
            })

    lines = [
        "# 污染扫描结果（自动生成）",
        "",
        f"- 黑名单来源（评测快照并集，任务数 {n_tasks}）：",
    ] + [
        f"  - {s}" for s in (meta.get("eval_jsonls") or [meta["eval_jsonl"]])
    ] + [
        f"- 输入：{args.input}",
        f"- 主阈值：n-gram={ngram}，重合率 ≥ {args.threshold} 判定命中",
        f"- 短文本兜底：n-gram={short_ngram}，重合数 ≥ 1 判定命中（覆盖中文短 prompt 及嵌在长文档中的短串）",
        f"- 扫描文档数：{scanned}（其中主 n-gram 无法覆盖、走兜底的有 {short}）",
        f"- **命中（污染）文档数：{flagged}**",
    ]
    if hits:
        lines.append("")
        lines.append("## 命中明细")
        lines.append("| doc_idx | overlap | total | ratio | short_overlap | best_task | jaccard_est |")
        lines.append("|---:|---:|---:|---:|---:|---|---:|")
        for h in hits:
            lines.append(f"| {h['doc_idx']} | {h['overlap']} | {h['total']} | {h['ratio']} | {h['short_overlap']} | {h['best_task']} | {h['jaccard_est']} |")
        lines.append("")
        lines.append("> ⚠️ 命中文档必须**剔除**并记录，改写也不洗白。")
    text = "\n".join(lines) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"[done] 扫描 {scanned} 文档 / 命中 {flagged}；报告写入 {args.out}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())