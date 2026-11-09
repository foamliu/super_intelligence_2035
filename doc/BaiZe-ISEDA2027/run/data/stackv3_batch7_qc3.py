#!/usr/bin/env python3
"""Batch7 QC v3: sample 200 repos per shard, extract only metadata fields."""
import pyarrow.parquet as pq
import pyarrow as pa
import os, collections, time

DATA_DIR = '/nas_inference/app.e0031982/datasets/HuggingFaceCode/stack-v3-train/data'
sample_shards = [
    'part-04200-eb7ffe4b-e1fe-4e24-b667-41a566eb1bca-c000.snappy.parquet',
    'part-04400-eb7ffe4b-e1fe-4e24-b667-41a566eb1bca-c000.snappy.parquet',
    'part-04599-eb7ffe4b-e1fe-4e24-b667-41a566eb1bca-c000.snappy.parquet',
]
EDA_LANGS = {'Python','C','C++','C++ Header','C Header','Verilog','SystemVerilog',
             'Tcl','Makefile','CMake','Shell','Bazel','MATLAB','VHDL'}
TARGET_LANGS = EDA_LANGS | {'Scala','Rust','Go','Java','JavaScript','TypeScript',
             'C#','PHP','Kotlin','Ruby','Swift','Dart','Lua','R','Julia',
             'Haskell','OCaml','Erlang','Elixir','Clojure'}
N = 200
tf=0; tb=0; tr=0; vf=0; vb=0; bf=0; er=0
lb=collections.Counter(); lf=collections.Counter()
for sn in sample_shards:
    p = os.path.join(DATA_DIR, sn)
    if not os.path.exists(p):
        import glob
        matches = glob.glob(os.path.join(DATA_DIR, sn[:20]+'*'))
        if matches:
            p = matches[0]
            print(f'  using {os.path.basename(p)} for {sn[:15]}')
        else:
            print(f'MISS {sn}'); continue
    t0=time.time(); pf=pq.ParquetFile(p)
    nrg = min(2, pf.num_row_groups)
    tbl = pf.read_row_group(0)
    if nrg > 1 and tbl.num_rows < N:
        tbl2 = pf.read_row_group(1)
        tbl = pa.concat_tables([tbl, tbl2])
    n = min(N, tbl.num_rows); tr += n
    fc = tbl.column('files').slice(0,n).to_pylist()
    nc = tbl.column('num_files').to_pylist()
    for i, fl in enumerate(fc):
        if nc[i]==0 or not fl: er+=1; continue
        for f in fl:
            tf+=1; fb=f.get('size_bytes',0); tb+=fb
            ln=f.get('language','Unknown'); lb[ln]+=fb; lf[ln]+=1
            if f.get('is_vendor',False): vf+=1; vb+=fb
            if fb>1048576: bf+=1
    print(f'{os.path.basename(p)}: {n} repos, {time.time()-t0:.1f}s')
print(f'\n{"="*60}')
print(f'BATCH7 QC (3 shards x {N} repos = {tr} repos)')
print(f'{"="*60}')
print(f'Files: {tf:,}  Bytes: {tb:,} ({tb/1024**2:.1f} MiB)  Avg file: {tb/max(tf,1):.0f}B')
print(f'Empty repos: {er}  Vendor: {vf} ({vf/max(tf,1)*100:.1f}%)  >1MB: {bf} ({bf/max(tf,1)*100:.1f}%)')
print(f'\nTop 15 langs by bytes:')
for ln,b in lb.most_common(15):
    print(f'  {ln:25s}: {b/1024**2:8.1f} MiB  {lf[ln]:>8,} files  ({b/tb*100:5.1f}%)')
eda_b=sum(lb[l] for l in EDA_LANGS); tgt_b=sum(lb[l] for l in TARGET_LANGS)
print(f'\nEDA(14): {eda_b/tb*100:.1f}% bytes  Target(32): {tgt_b/tb*100:.1f}% bytes')
print(f'Token est (bytes/4): {tb/4/1e6:.1f}M tok in {tr} repos')
avg_repos = tr / 3
est_total_repos = avg_repos * 400
est_total_files = tf / tr * est_total_repos
est_total_bytes = tb / tr * est_total_repos
print(f'\nBatch7 extrapolation (400 shards, ~{avg_repos:.0f} repos/shard):')
print(f'  ~{est_total_repos:,.0f} repos  ~{est_total_files:,.0f} files  ~{est_total_bytes/1024**4:.2f} TiB content')
print(f'  ~{est_total_bytes/4/1e9:.1f}B tokens (bytes/4 rough est)')
