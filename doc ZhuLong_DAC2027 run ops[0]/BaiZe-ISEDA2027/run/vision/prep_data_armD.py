"""prep_data_armD.py — generalized parquet -> WebDataset tar converter for ArmD.

Extends prep_data.py to handle DIFFERENT per-source parquet schemas:
  - MVRL/WebMix-38M   : image struct {bytes,path} + caption(str)
  - VedaLabs/wit_base : image struct {bytes,path} + caption_attribution_description(str)
                        (real WIT caption; many rows are empty/'None' -> filtered out)

Parallel: each worker handles a disjoint subset of parquet files and writes to its
own output subdir (worker_{id}/) so shard indices never collide. The final snapshot
just globs all worker_*/shard-*.tar.

Output wds sample = {'__key__': '<count:09d>', <ext>: image_bytes, 'txt': caption}.
This matches build_mixed_loader's 'txt' branch (CC12M/Amshaker path), so the converted
tars drop straight into the existing ArmC training pipeline with ZERO training-side
code changes.
"""
import argparse
import glob
import os
import sys
import time
from multiprocessing import Process

import pyarrow.parquet as pq
from webdataset import TarWriter


def sniff_ext(b: bytes) -> str:
    if b[:4] == b'\x89PNG':
        return 'png'
    if b[:2] == b'\xff\xd8':
        return 'jpg'
    return 'img'


def _get_image_bytes(row_image):
    """image column is a struct {bytes, path} -> bytes, or already raw bytes."""
    if isinstance(row_image, dict):
        return row_image.get('bytes')
    if isinstance(row_image, (bytes, bytearray)):
        return bytes(row_image)
    return None


def _clean_caption(cap, filter_empty):
    if cap is None:
        return None
    cap = str(cap).strip()
    if not cap:
        return None
    if filter_empty and cap.lower() in ('none', 'nan', 'null'):
        return None
    return cap


def convert_subset(files, out_dir, worker_id, caption_col, filter_empty,
                   shard_size, max_per_worker):
    """Convert a list of parquet files -> worker_{id}/shard-NNNNN.tar."""
    wdir = os.path.join(out_dir, f'worker_{worker_id:03d}')
    os.makedirs(wdir, exist_ok=True)
    count = 0
    shard_idx = 0
    writer = None
    skipped = 0
    t0 = time.time()
    try:
        for fi, fn in enumerate(files):
            try:
                pf = pq.ParquetFile(fn)
            except Exception as e:
                print(f'[w{worker_id}] SKIP unreadable parquet {fn}: {e}', flush=True)
                continue
            for rg in range(pf.num_row_groups):
                try:
                    tbl = pf.read_row_group(rg)
                except Exception as e:
                    print(f'[w{worker_id}] SKIP rg {rg} of {fn}: {e}', flush=True)
                    continue
                cols = tbl.column_names
                if 'image' not in cols or caption_col not in cols:
                    continue
                images = tbl['image'].to_pylist()
                caps = tbl[caption_col].to_pylist()
                for j in range(len(caps)):
                    b = _get_image_bytes(images[j])
                    cap = _clean_caption(caps[j], filter_empty)
                    if not b or not cap:
                        skipped += 1
                        continue
                    if count % shard_size == 0:
                        if writer is not None:
                            writer.close()
                        writer = TarWriter(os.path.join(wdir, f'shard-{shard_idx:05d}.tar'))
                        shard_idx += 1
                    ext = sniff_ext(b)
                    try:
                        writer.write({'__key__': f'{count:09d}', ext: b,
                                      'txt': cap.encode('utf-8')})
                    except Exception:
                        skipped += 1
                        continue
                    count += 1
                    if max_per_worker and count >= max_per_worker:
                        break
            if fi % 10 == 0:
                print(f'[w{worker_id}] {fi+1}/{len(files)} files, {count} pairs, '
                      f'{skipped} skip, {time.time()-t0:.0f}s', flush=True)
            if max_per_worker and count >= max_per_worker:
                break
    finally:
        if writer is not None:
            try:
                writer.close()
            except Exception:
                pass
    print(f'[w{worker_id}] DONE: {count} pairs, {shard_idx} shards, '
          f'{skipped} skip, {time.time()-t0:.0f}s', flush=True)


def _worker(chunk, out_dir, worker_id, caption_col, filter_empty, shard_size, max_per_worker):
    try:
        convert_subset(chunk, out_dir, worker_id, caption_col, filter_empty,
                       shard_size, max_per_worker)
    except Exception as e:
        import traceback
        print(f'[w{worker_id}] FATAL: {e}\n{traceback.format_exc()}', flush=True)
        raise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--caption-col', required=True)
    ap.add_argument('--filter-empty', action='store_true')
    ap.add_argument('--max', type=int, default=0, dest='max_n')
    ap.add_argument('--shard', type=int, default=20000)
    ap.add_argument('--workers', type=int, default=8)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    files = sorted(glob.glob(args.src))
    print(f'[prep_armD] {len(files)} parquet -> {args.out} '
          f'(cap_col={args.caption_col}, filter_empty={args.filter_empty}, '
          f'workers={args.workers}, shard={args.shard})', flush=True)
    if not files:
        print('[prep_armD] NO parquet matched glob; abort', flush=True)
        sys.exit(2)

    w = args.workers
    chunks = [files[i::w] for i in range(w)]
    max_per_worker = args.max_n // w if args.max_n else 0
    procs = []
    for wid, chunk in enumerate(chunks):
        if not chunk:
            continue
        p = Process(target=_worker, args=(chunk, args.out, wid, args.caption_col,
                                          args.filter_empty, args.shard, max_per_worker))
        p.start()
        procs.append(p)
    for p in procs:
        p.join()
    bad = [p for p in procs if p.exitcode != 0]
    import subprocess
    ntars = int(subprocess.check_output(
        ['bash', '-c', f"find '{args.out}' -name 'shard-*.tar' | wc -l"]).strip())
    print(f'[prep_armD] DONE: {ntars} shard tars; {len(bad)} workers failed', flush=True)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
