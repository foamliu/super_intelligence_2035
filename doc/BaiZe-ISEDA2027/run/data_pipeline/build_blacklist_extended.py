#!/usr/bin/env python3
"""build_blacklist_extended.py — 扩展污染黑名单指纹生成器（S2 Go/No-Go #5）。

在 build_blacklist.py（EDA-Eval 536 任务）基础上，并入 5 个公开 benchmark：
  HumanEval / MBPP / GSM8K / MATH / SWE-bench（共 4823 任务），
合计 ~5359 任务，产出 blacklist_extended/ 指纹（仅哈希，绝不含原始评测内容）。

各 benchmark schema 不同，需 field_map 适配到统一禁止字段集
{prompt, entry_point, test, canonical_solution}：
  humaneval : prompt, entry_point, test, canonical_solution   (原生匹配)
  mbpp      : prompt, test_list(->test), code(->canonical_solution)
  gsm8k     : question(->prompt), answer(->canonical_solution)
  math      : problem(->prompt), solution(->canonical_solution)
  swebench  : problem_statement(->prompt), patch(->canonical_solution)
  EDA-Eval  : prompt, entry_point, test, canonical_solution   (原生匹配, 6 快照)

指纹方法与 build_blacklist.py 完全一致（NFKC -> 小写 -> 折叠 -> 字符级 13-gram + MinHash
+ 短 8-gram 兜底），两侧（建黑名单 / 扫描）逻辑对称才能正确匹配。产物落
run/data_pipeline/blacklist_extended/，已列入 .gitignore（可再生，需时重跑）。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

# 复用 build_blacklist.py 的指纹原语（同目录模块，import 不触发其 main）
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_blacklist import (  # noqa: E402
    fnv1a_64, normalize, shingles, short_shingles, minhash,
)

# 统一禁止字段（与 build_blacklist.FORBIDDEN_FIELDS 一致）
CANONICAL_FIELDS = ["prompt", "entry_point", "test", "canonical_solution"]

# 每个 benchmark：{canonical_field: actual_key}；未列出的 canonical 字段视为该源不存在该字段
FIELD_MAPS = {
    "humaneval": {"prompt": "prompt", "entry_point": "entry_point",
                  "test": "test", "canonical_solution": "canonical_solution"},
    "mbpp":      {"prompt": "prompt", "test": "test_list", "canonical_solution": "code"},
    "gsm8k":     {"prompt": "question", "canonical_solution": "answer"},
    "math":      {"prompt": "problem", "canonical_solution": "solution"},
    "swebench":  {"prompt": "problem_statement", "canonical_solution": "patch"},
    "edaeval":   {"prompt": "prompt", "entry_point": "entry_point",
                  "test": "test", "canonical_solution": "canonical_solution"},
}


def _field_value(obj, actual_key):
    """取字段值；list（如 mbpp test_list）拼成多行字符串。"""
    v = obj.get(actual_key)
    if v is None:
        return None
    if isinstance(v, list):
        return "\n".join(str(x) for x in v)
    return str(v)


# benchmark jsonl 文件名 -> (label, field_map key)；用原始（非 _norm）文件
BENCH_FILES = {
    "humaneval.jsonl": ("humaneval", "humaneval"),
    "mbpp.jsonl":      ("mbpp", "mbpp"),
    "gsm8k.jsonl":     ("gsm8k", "gsm8k"),
    "math.jsonl":      ("math", "math"),
    "swebench.jsonl":  ("swebench", "swebench"),
}

# EDA-Eval 6 快照（与 build_blacklist.py 默认一致）
EDAEVAL_FILES = [
    "EDA-Eval-PyAether-v20260311.jsonl",
    "EDA-Eval-PyAether-148.jsonl",
    "EDA-Eval-PyAether-46.jsonl",
    "EDA-Eval-PyAether-Updated102.jsonl",
    "EDA-Eval-PyAether_TEST.jsonl",
    "cuhk_benchmark_cxmt_format.jsonl",
]
def main() -> int:
    ap = argparse.ArgumentParser(description="扩展污染黑名单指纹生成（EDA-Eval + 5 benchmark）")
    ap.add_argument("--benchmark-dir", default="/nas_user/app.e0031982/datasets/benchmarks",
                    help="5 个 benchmark jsonl 所在目录（用原始非 _norm 文件）")
    ap.add_argument("--edaeval-dir",
                    default="/nas_train/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset",
                    help="EDA-Eval 6 快照 jsonl 所在目录")
    ap.add_argument("--out-dir", default="run/data_pipeline/blacklist_extended",
                    help="扩展黑名单输出目录（仅指纹，不含原始内容）")
    ap.add_argument("--ngram", type=int, default=13)
    ap.add_argument("--short-ngram", type=int, default=8)
    ap.add_argument("--minhash-k", type=int, default=128)
    args = ap.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tasks = []
    global_shingles = {}
    global_short_shingles = {}
    n_lines = 0
    per_source_counts = {}

    def process_source(path, label, fmap_key):
        nonlocal n_lines
        fmap = FIELD_MAPS[fmap_key]
        cnt = 0
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                n_lines += 1
                cnt += 1
                obj = json.loads(line)
                tid = f"{label}:{obj.get('task_id', f'unknown-{n_lines}')}"
                fields_present, parts = [], []
                for canon in CANONICAL_FIELDS:
                    actual = fmap.get(canon)
                    if actual is None:
                        continue
                    val = _field_value(obj, actual)
                    if val is None:
                        continue
                    fields_present.append(canon)
                    parts.append(val)
                combined = "\n".join(parts)
                sh = shingles(combined, args.ngram)
                sig = minhash(sh, args.minhash_k)
                sh_short = sh_short_sig = None
                short_ngram_used = 0
                if not sh:
                    sh_short, short_ngram_used = short_shingles(combined, args.short_ngram)
                    sh_short_sig = minhash(sh_short, args.minhash_k) if sh_short else []
                ep_val = ""
                if "entry_point" in fmap:
                    ep_raw = obj.get(fmap["entry_point"])
                    if ep_raw is not None:
                        ep_val = str(ep_raw)
                tasks.append({
                    "task_id": tid, "source": str(path), "source_label": label,
                    "fields": fields_present, "n_shingles": len(sh), "minhash": sig,
                    "short": not bool(sh),
                    "n_short_shingles": len(sh_short) if sh_short is not None else 0,
                    "short_ngram": short_ngram_used, "minhash_short": sh_short_sig or [],
                    "entry_point_sha256": hashlib.sha256(ep_val.encode("utf-8")).hexdigest(),
                })
                for s in sh:
                    global_shingles.setdefault(s, fnv1a_64(s.encode("utf-8", "ignore")))
                if sh_short is not None:
                    for s in sh_short:
                        global_short_shingles.setdefault(s, fnv1a_64(s.encode("utf-8", "ignore")))
        key = f"{label}:{path.name}"
        per_source_counts[key] = cnt

    edaeval_dir = Path(args.edaeval_dir)
    missing_eval = [f for f in EDAEVAL_FILES if not (edaeval_dir / f).exists()]
    if missing_eval:
        print(f"[error] EDA-Eval 快照缺失: {missing_eval}", file=sys.stderr)
        return 1
    for f in EDAEVAL_FILES:
        process_source(edaeval_dir / f, "edaeval", "edaeval")
    bench_dir = Path(args.benchmark_dir)
    missing_bench = [f for f in BENCH_FILES if not (bench_dir / f).exists()]
    if missing_bench:
        print(f"[error] benchmark 缺失: {missing_bench}", file=sys.stderr)
        return 1
    for fname, (label, fmap_key) in BENCH_FILES.items():
        process_source(bench_dir / fname, label, fmap_key)

    hashes = sorted(set(global_shingles.values()))
    hash_path = out / "ngram_hashes.txt"
    with open(hash_path, "w", encoding="utf-8") as f:
        for h in hashes:
            f.write(f"{h:016x}\n")
    short_hashes = sorted(set(global_short_shingles.values()))
    short_hash_path = out / "short_ngram_hashes.txt"
    with open(short_hash_path, "w", encoding="utf-8") as f:
        for h in short_hashes:
            f.write(f"{h:016x}\n")
    ep_path = out / "entry_points.sha256"
    with open(ep_path, "w", encoding="utf-8") as f:
        for t in tasks:
            f.write(f"{t['task_id']}\t{t['entry_point_sha256']}\n")
    n_short_tasks = sum(1 for t in tasks if t["short"])
    meta = {
        "description": "扩展污染黑名单：EDA-Eval(6 快照) + HumanEval/MBPP/GSM8K/MATH/SWE-bench",
        "eval_jsonls": [str(edaeval_dir / f) for f in EDAEVAL_FILES],
        "benchmark_jsonls": [str(bench_dir / f) for f in BENCH_FILES],
        "field_maps": FIELD_MAPS,
        "ngram": args.ngram, "short_ngram": args.short_ngram, "minhash_k": args.minhash_k,
        "normalization": "NFKC -> lowercase -> collapse non Unicode \\w to space -> strip spaces -> char n-gram",
        "forbidden_fields": CANONICAL_FIELDS,
        "note": "仅落盘哈希/MinHash 指纹，绝不含任何评测集原始 prompt/参考解/断言。",
        "num_tasks": len(tasks), "num_lines": n_lines,
        "per_source_counts": per_source_counts,
        "total_distinct_ngrams": len(hashes),
        "total_distinct_short_ngrams": len(short_hashes),
        "num_short_tasks": n_short_tasks, "tasks": tasks,
    }
    meta_path = out / "meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"[done] {len(tasks)} 任务 / {len(hashes)} 去重后 {args.ngram}-gram 哈希；"
          f"短文本兜底 {n_short_tasks} 任务 / {len(short_hashes)} 去重后 {args.short_ngram}-gram 哈希")
    print(f"      分源计数: {per_source_counts}")
    print(f"      产物: {meta_path} / {hash_path}({len(hashes)}) / {short_hash_path}({len(short_hashes)}) / {ep_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

