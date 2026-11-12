#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""stackv3_tokenize.py — Tokenize stack-v3-train parquet shards into mcore .bin/.idx.

Reads the nested `files` column from HuggingFaceCode/stack-v3-train parquet shards,
applies language priority + quality filters, tokenizes each file's content with
DeepSeek-V4.1-Flash tokenizer (+ EOD), outputs mcore .bin/.idx/.json triplets.
"""
from __future__ import annotations
import argparse, json, os, re, sys, time, traceback
from pathlib import Path
from collections import Counter
from multiprocessing import Pool
import numpy as np

PARQUET_DIR = "/nas_inference/app.e0031982/datasets/HuggingFaceCode/stack-v3-train/data"
OUTPUT_DIR = "/nas_train/app.e0031982/datasets/baize-data/tokenized/HuggingFaceCode/stack-v3-train"
TOKENIZER_DIR = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/data/tokenizer_eod"
EOD_TOKEN = ""
DTYPE = "int32"
MAX_FILE_BYTES = 1_048_576

PRIORITY_LANGS = {
    'Python', 'C', 'C++', 'C Header', 'Verilog', 'SystemVerilog',
    'Tcl', 'Makefile', 'Shell', 'CMake', 'Bazel', 'SKILL', 'Perl',
}
EXT_LANG_MAP = {
    '.py': 'Python', '.c': 'C', '.h': 'C Header', '.cpp': 'C++', '.cc': 'C++',
    '.cxx': 'C++', '.hpp': 'C++', '.hh': 'C++',
    '.v': 'Verilog', '.sv': 'SystemVerilog', '.vh': 'Verilog', '.svh': 'SystemVerilog',
    '.tcl': 'Tcl', '.sdc': 'Tcl', '.xdc': 'Tcl',
    '.mk': 'Makefile', '.sh': 'Shell', '.bash': 'Shell',
    '.cmake': 'CMake', '.bazel': 'Bazel', '.bzl': 'Bazel',
    '.il': 'SKILL', '.pl': 'Perl', '.pm': 'Perl',
}
MINIFIED_PATTERNS = [re.compile(r'\.min\.', re.I), re.compile(r'\.bundle\.', re.I), re.compile(r'\.pack\.', re.I)]
GENERATED_PATTERNS = [re.compile(r'/generated/', re.I), re.compile(r'/auto_generated/', re.I),
    re.compile(r'/__pycache__/', re.I), re.compile(r'\.pyc$', re.I)]
TEST_PATTERNS = [re.compile(r'/test/', re.I), re.compile(r'/tests/', re.I),
    re.compile(r'/__tests__/', re.I), re.compile(r'/spec/', re.I),
    re.compile(r'\.test\.', re.I), re.compile(r'\.spec\.', re.I), re.compile(r'/fixtures/', re.I)]
CONFIG_EXTS = {'.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.env', '.lock', '.map'}

_TOKENIZER = None
_EOD_ID = None


def get_tokenizer():
    global _TOKENIZER, _EOD_ID
    if _TOKENIZER is None:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(TOKENIZER_DIR)
        _EOD_ID = tok.eos_token_id
        _TOKENIZER = tok
    return _TOKENIZER, _EOD_ID


def should_skip(file_path, language, size_bytes, is_vendor):
    if is_vendor:
        return True, 'vendor'
    if size_bytes <= 0 or size_bytes > MAX_FILE_BYTES:
        return True, 'size'
    ext = os.path.splitext(file_path)[1].lower()
    lang = language or 'Unknown'
    if lang not in PRIORITY_LANGS and ext not in EXT_LANG_MAP:
        return True, 'lang'
    for pat in MINIFIED_PATTERNS:
        if pat.search(file_path):
            return True, 'minified'
    for pat in GENERATED_PATTERNS:
        if pat.search(file_path):
            return True, 'generated'
    for pat in TEST_PATTERNS:
        if pat.search(file_path):
            return True, 'test'
    if ext in CONFIG_EXTS:
        return True, 'config'
    return False, ''


def get_all_parquets():
    return sorted(Path(PARQUET_DIR).glob("*.parquet"))


def process_shard(args):
    shard_idx, shard_path, output_prefix = args
    import pyarrow.parquet as pq
    shard_name = Path(shard_path).stem
    out_prefix = os.path.join(output_prefix, f"stackv3_s{shard_idx:05d}")
    bin_path = f"{out_prefix}.bin"
    idx_path = f"{out_prefix}.idx"
    json_path = f"{out_prefix}.json"

    if os.path.exists(json_path):
        try:
            with open(json_path) as f:
                meta = json.load(f)
            if meta.get('num_tokens', 0) > 0 and os.path.exists(bin_path) and os.path.exists(idx_path):
                return {'shard_idx': shard_idx, 'skipped': True, **meta}
        except Exception:
            pass

    t0 = time.time()
    tokenizer, eod_id = get_tokenizer()
    from megatron.core.datasets.indexed_dataset import IndexedDatasetBuilder
    import torch
    dtype = getattr(np, DTYPE)

    builder = IndexedDatasetBuilder(bin_path=bin_path, dtype=dtype)
    n_docs = 0
    n_tokens = 0
    skip_reasons = Counter()
    lang_counts = Counter()

    try:
        pf = pq.ParquetFile(str(shard_path))
        # Read row-group by row-group to avoid ArrowNotImplementedError
        # on nested columns with chunked arrays — use combine_chunks() to
        # merge chunked arrays before to_pylist()
        files_col = []
        for rg_idx in range(pf.num_row_groups):
            tbl = pf.read_row_group(rg_idx, columns=["repo_path", "files"])
            col = tbl.column("files")
            if hasattr(col, 'combine_chunks'):
                col = col.combine_chunks()
            files_col.extend(col.to_pylist())
        for repo_files in files_col:
            if not repo_files:
                continue
            for f in repo_files:
                fp = f.get("file_path", "") or ""
                ln = f.get("language", "Unknown") or "Unknown"
                fb = f.get("size_bytes", 0) or 0
                is_vendor = f.get("is_vendor", False)
                content = f.get("content", "") or ""
                skip, reason = should_skip(fp, ln, fb, is_vendor)
                if skip:
                    skip_reasons[reason] += 1
                    continue
                if not content:
                    skip_reasons['empty'] += 1
                    continue
                ids = tokenizer(content, add_special_tokens=False, truncation=False)["input_ids"]
                ids = ids + [eod_id]
                builder.add_item(torch.tensor(ids, dtype=torch.long))
                builder.end_document()
                n_docs += 1
                n_tokens += len(ids)
                eff_lang = ln if ln in PRIORITY_LANGS else EXT_LANG_MAP.get(os.path.splitext(fp)[1].lower(), 'Unknown')
                lang_counts[eff_lang] += 1
        builder.finalize(idx_path=idx_path)
    except Exception as e:
        traceback.print_exc()
        return {'shard_idx': shard_idx, 'error': str(e), 'num_tokens': n_tokens}

    dt = time.time() - t0
    meta = {
        'shard_idx': shard_idx, 'shard_name': shard_name, 'shard_path': str(shard_path),
        'num_documents': n_docs, 'num_tokens': n_tokens, 'dtype': DTYPE, 'eod_id': eod_id,
        'vocab_size': 129281, 'padded_vocab_size': 129408, 'tokenizer': TOKENIZER_DIR,
        'skip_reasons': dict(skip_reasons), 'lang_counts': dict(lang_counts.most_common(20)),
        'time_s': round(dt, 1),
    }
    with open(json_path, 'w') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    return {'shard_idx': shard_idx, 'skipped': False, **meta}


def main():
    ap = argparse.ArgumentParser(description='Tokenize stack-v3-train -> mcore .bin/.idx')
    ap.add_argument('--shards', default='all', help='all | N (first N shards)')
    ap.add_argument('--shard-start', type=int, default=0)
    ap.add_argument('--shard-end', type=int, default=None)
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--output-dir', default=OUTPUT_DIR)
    ap.add_argument('--shard-list', default=None)
    args = ap.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    if args.shard_list:
        with open(args.shard_list) as f:
            all_parquets = [Path(l.strip()) for l in f if l.strip()]
    else:
        all_parquets = get_all_parquets()
    start = args.shard_start
    end = args.shard_end or (int(args.shards) if args.shards.isdigit() else len(all_parquets))
    if args.shards == 'all':
        end = len(all_parquets)
    shard_list = all_parquets[start:end]
    total = len(shard_list)
    print(f"Total parquets: {len(all_parquets)}, processing {total} [{start}:{end}], workers={args.workers}")
    tasks = [(start + i, str(sp), args.output_dir) for i, sp in enumerate(shard_list)]
    t0 = time.time()
    all_stats = []
    if args.workers <= 1:
        for task in tasks:
            stats = process_shard(task)
            all_stats.append(stats)
            si = stats['shard_idx']; nt = stats.get('num_tokens', 0)
            print(f"  [{si}] docs={stats.get('num_documents',0):,} tokens={nt:,} time={stats.get('time_s',0)}s", flush=True)
    else:
        with Pool(args.workers) as pool:
            for i, stats in enumerate(pool.imap_unordered(process_shard, tasks)):
                all_stats.append(stats)
                si = stats.get('shard_idx', '?'); nt = stats.get('num_tokens', 0)
                dt = time.time() - t0; done = i + 1
                eta = (dt / done) * (total - done) if done > 0 else 0
                status = 'SKIP' if stats.get('skipped') else ('ERR' if stats.get('error') else 'OK')
                print(f"  [{done}/{total}] shard={si} {status} tokens={nt:,} elapsed={dt:.0f}s ETA={eta:.0f}s", flush=True)
    total_time = time.time() - t0
    total_tokens = sum(s.get('num_tokens', 0) for s in all_stats)
    total_docs = sum(s.get('num_documents', 0) for s in all_stats)
    n_errors = sum(1 for s in all_stats if s.get('error'))
    n_skipped = sum(1 for s in all_stats if s.get('skipped'))
    print(f"\n{'='*60}\nDone: {total} shards in {total_time:.0f}s\n  Docs: {total_docs:,}  Tokens: {total_tokens:,}\n  Errors: {n_errors}  Skipped: {n_skipped}")
    manifest_path = os.path.join(args.output_dir, "MANIFEST.json")
    manifest = {
        "tokenized_dir": args.output_dir, "download_dir": PARQUET_DIR,
        "hf_repo": "HuggingFaceCode/stack-v3-train",
        "tokenizer": "DeepSeek-V4.1-Flash int32 (tokenizer_eod, vocab=129281, pad=129408)",
        "shards": [{"name": f"stackv3_s{s.get('shard_idx',0):05d}",
                     "tokens": s.get('num_tokens',0), "num_documents": s.get('num_documents',0),
                     "shard_name": s.get('shard_name','')}
                    for s in sorted(all_stats, key=lambda x: x.get('shard_idx',0))],
        "total_tokens": total_tokens, "total_documents": total_docs,
    }
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"  MANIFEST: {manifest_path}")


if __name__ == '__main__':
    main()
