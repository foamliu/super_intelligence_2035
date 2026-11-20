#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""megamath_tokenize.py — PC-2: Tokenize MegaMath Batch1 parquets into mcore .bin/.idx.

Handles 4 subsets with 'text' column: web-pro, text-code-block, qa, translated-code.
Skips megamath-code (metadata-only, no text content).
"""
from __future__ import annotations
import argparse, json, os, sys, time, traceback
from pathlib import Path
from multiprocessing import Pool
import numpy as np

TOKENIZER_DIR = '/nas_train/app.e0031982/code/BaiZe-ISEDA2027/data/tokenizer_eod'
EOD_TOKEN = ''
DTYPE = 'int32'
MAX_TEXT_BYTES = 10_000_000  # 10MB max per document

INPUT_BASE = '/nas_user/app.e0031982/datasets/IFM/MegaMath'
OUTPUT_BASE = '/nas_user/app.e0031982/datasets/baize-data/tokenized/IFM/MegaMath'

SUBSETS = ['megamath-web-pro', 'megamath-text-code-block', 'megamath-qa', 'megamath-translated-code']

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

def write_mcore_bin(tokens, out_prefix):
    """Write .bin/.idx triplet like stackv3_tokenize.py."""
    arr = np.array(tokens, dtype=DTYPE)
    bin_path = out_prefix + '.bin'
    idx_path = out_prefix + '.idx'
    arr.tofile(bin_path)
    # Simple .idx: [num_tokens (int64), num_docs (int64)] — matches stackv3 format
    # Actually stackv3 uses a more complex .idx; let's match it
    # The .idx is a simple offset index: for each doc, (start_offset, length)
    # But we don't track doc boundaries here. Let's write a simple format.
    with open(idx_path, 'w') as f:
        f.write(f'{len(arr)}\n')
    return len(arr)

def process_parquet(args):
    """Tokenize a single parquet file."""
    shard_idx, parquet_path, subset, output_dir = args
    out_prefix = os.path.join(output_dir, subset, f'shard_{shard_idx:05d}')
    json_path = out_prefix + '.json'
    if os.path.exists(json_path):
        try:
            with open(json_path) as f:
                old = json.load(f)
            if old.get('num_tokens', 0) > 0:
                return old
        except:
            pass
    try:
        import pyarrow.parquet as pq
        tok, eod_id = get_tokenizer()
        table = pq.read_table(parquet_path, columns=['text'])
        texts = table.column('text').to_pylist()
        all_tokens = []
        num_docs = 0
        skipped = 0
        for text in texts:
            if text is None:
                skipped += 1; continue
            text = str(text)
            if len(text) > MAX_TEXT_BYTES:
                text = text[:MAX_TEXT_BYTES]
            if len(text.strip()) < 10:
                skipped += 1; continue
            ids = tok.encode(text, add_special_tokens=False)
            ids.append(eod_id)
            all_tokens.extend(ids)
            num_docs += 1
        num_tokens = write_mcore_bin(all_tokens, out_prefix)
        stats = {
            'shard_idx': shard_idx, 'subset': subset, 'parquet_path': str(parquet_path),
            'num_tokens': num_tokens, 'num_documents': num_docs, 'skipped': skipped,
            'time_s': 0,  # will be filled by caller
        }
        with open(json_path, 'w') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        return stats
    except Exception as e:
        stats = {'shard_idx': shard_idx, 'subset': subset, 'parquet_path': str(parquet_path),
                 'error': str(e), 'num_tokens': 0, 'num_documents': 0}
        with open(json_path, 'w') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        return stats

def get_all_parquets():
    """Get all parquet files from all 4 subsets."""
    tasks = []
    for subset in SUBSETS:
        subset_dir = Path(INPUT_BASE) / subset
        if not subset_dir.exists():
            print(f'  SKIP {subset} (not found)'); continue
        parquets = sorted(subset_dir.rglob('*.parquet'))
        for i, pq in enumerate(parquets):
            tasks.append((i, str(pq), subset, OUTPUT_BASE))
        print(f'  {subset}: {len(parquets)} parquet files')
    return tasks

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--output-dir', default=OUTPUT_BASE)
    ap.add_argument('--start', type=int, default=0)
    ap.add_argument('--end', type=int, default=0)
    args = ap.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    for s in SUBSETS:
        os.makedirs(os.path.join(args.output_dir, s), exist_ok=True)
    all_tasks = get_all_parquets()
    total = len(all_tasks)
    print(f'\nTotal parquets to tokenize: {total}')
    if args.end > 0:
        all_tasks = all_tasks[args.start:args.end]
        print(f'  Sliced to [{args.start}:{args.end}] = {len(all_tasks)} files')
    t0 = time.time(); all_stats = []
    if args.workers <= 1:
        for task in all_tasks:
            t1 = time.time()
            stats = process_parquet(task)
            stats['time_s'] = time.time() - t1
            all_stats.append(stats)
            si = stats.get('shard_idx','?'); nt = stats.get('num_tokens',0)
            print(f'  [{si}] {stats.get("subset","")} docs={stats.get("num_documents",0):,} tokens={nt:,} time={stats["time_s"]:.1f}s', flush=True)
    else:
        pool = Pool(args.workers, maxtasksperchild=20)
        try:
            for i, stats in enumerate(pool.imap_unordered(process_parquet, all_tasks)):
                all_stats.append(stats)
                si = stats.get('shard_idx','?'); nt = stats.get('num_tokens',0)
                dt = time.time() - t0; done = i + 1
                eta = (dt / done) * (len(all_tasks) - done) if done > 0 else 0
                status = 'ERR' if stats.get('error') else ('SKIP' if stats.get('skipped',0) > 0 and nt == 0 else 'OK')
                print(f'  [{done}/{len(all_tasks)}] {stats.get("subset","")} shard={si} {status} tokens={nt:,} elapsed={dt:.0f}s ETA={eta:.0f}s', flush=True)
        except (BrokenPipeError, EOFError, ConnectionError) as e:
            print(f'\nWARNING: Pool crashed: {e}'); print(f'  Collected {len(all_stats)} results.')
        finally:
            pool.terminate(); pool.join()
    total_time = time.time() - t0
    total_tokens = sum(s.get('num_tokens',0) for s in all_stats)
    total_docs = sum(s.get('num_documents',0) for s in all_stats)
    n_errors = sum(1 for s in all_stats if s.get('error'))
    print(f'\n{"="*60}\nPC-2 Done: {len(all_stats)} parquets in {total_time:.0f}s')
    print(f'  Docs: {total_docs:,}  Tokens: {total_tokens:,}  Errors: {n_errors}')
    # Write per-subset manifest
    for subset in SUBSETS:
        subset_stats = [s for s in all_stats if s.get('subset') == subset]
        if not subset_stats: continue
        st_tokens = sum(s.get('num_tokens',0) for s in subset_stats)
        st_docs = sum(s.get('num_documents',0) for s in subset_stats)
        print(f'  {subset}: {len(subset_stats)} shards, {st_docs:,} docs, {st_tokens:,} tokens')
    manifest = {
        'tokenized_dir': args.output_dir, 'input_base': INPUT_BASE,
        'tokenizer': 'DeepSeek-V4.1-Flash int32 (tokenizer_eod)',
        'subsets': SUBSETS,
        'total_tokens': total_tokens, 'total_documents': total_docs, 'total_errors': n_errors,
        'shards': sorted(all_stats, key=lambda x: (x.get('subset',''), x.get('shard_idx',0))),
    }
    mp = os.path.join(args.output_dir, 'MANIFEST.json')
    with open(mp, 'w') as f: json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f'  MANIFEST: {mp}')
    fp = os.path.join(args.output_dir, 'failed_shards.txt')
    errors = [s for s in all_stats if s.get('error')]
    if errors:
        with open(fp, 'w') as f:
            for s in errors: f.write(f"{s.get('subset','')}\t{s.get('parquet_path','')}\t{s.get('error','')}\n")
        print(f'  Failed: {fp} ({len(errors)} shards)')
    else:
        print('  No failed shards!')

if __name__ == '__main__': main()
