"""Extract a fixed unified image-caption subset from LLaVA-OneVision parquet
into WebDataset tar shards (reused by all four vision architectures).

parquet schema: id(str), image{bytes,path}, caption(str). image.bytes is PNG/JPEG.
"""
import argparse
import glob
import os

import pyarrow.parquet as pq
from webdataset import TarWriter


def sniff_ext(b):
    if b[:4] == b'\x89PNG':
        return 'png'
    if b[:2] == b'\xff\xd8':
        return 'jpg'
    return 'img'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True, help='parquet glob')
    ap.add_argument('--out', required=True, help='output dir for shards')
    ap.add_argument('--max', type=int, default=500000, dest='max_n')
    ap.add_argument('--shard', type=int, default=20000, help='pairs per shard')
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    files = sorted(glob.glob(args.src))
    print(f"[prep] {len(files)} parquet files -> {args.out} (max {args.max_n} pairs)")

    count = 0
    shard_idx = 0
    writer = None
    try:
        for fn in files:
            pf = pq.ParquetFile(fn)
            for i in range(pf.num_row_groups):
                tbl = pf.read_row_group(i)
                ids = tbl['id'].to_pylist()
                imgs = tbl['image'].to_pylist()     # list of dicts {bytes, path}
                caps = tbl['caption'].to_pylist()
                for j in range(len(ids)):
                    if count % args.shard == 0:
                        if writer is not None:
                            writer.close()
                        writer = TarWriter(os.path.join(args.out, f'shard-{shard_idx:05d}.tar'))
                        shard_idx += 1
                    b = imgs[j]['bytes']
                    ext = sniff_ext(b)
                    key = f'{count:09d}'
                    writer.write({'__key__': key, ext: b,
                                  'txt': (caps[j] or '').encode('utf-8')})
                    count += 1
                    if count >= args.max_n:
                        writer.close()
                        print(f'[prep] done: {count} pairs in {shard_idx} shards')
                        return
    finally:
        if writer is not None:
            try:
                writer.close()
            except Exception:
                pass
    print(f'[prep] done: {count} pairs in {shard_idx} shards')


if __name__ == '__main__':
    main()