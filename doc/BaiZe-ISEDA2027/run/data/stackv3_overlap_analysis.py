#!/usr/bin/env python3
"""2TB ROI: repo-level overlap between stack-v3-train (downloaded 4600 shards)
and UltraData-Code L2/L3.

Methodology:
- Sample repo_path from stack-v3-train (20 shards spread across batch1-7)
- Collect ALL repo_name from UltraData-Code L2 (11 lang dirs) + L3 (11 lang dirs)
  by sampling first parquet of each lang dir (enough for ~10K repos)
- Normalize both to lowercase org/repo
- Compute set intersection = overlap rate
- This is a repo-level proxy for content overlap (same repo => high n-gram overlap)
"""
import pyarrow.parquet as pq
import os, glob, collections, time

PY = '/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3'

# ---- 1. Collect UltraData-Code repo_names ----
L2_BASE = '/nas_inference/app.e0031982/datasets/openbmb/UltraData-Code/data/UltraData-Code-L2'
L3_BASE = '/nas_inference/app.e0031982/datasets/openbmb/UltraData-Code/data/UltraData-Code-L3'

udc_repos = set()
t0 = time.time()
for base, label in [(L2_BASE, 'L2'), (L3_BASE, 'L3')]:
    if not os.path.isdir(base):
        print(f'{label}: dir not found, skip')
        continue
    for lang_dir in sorted(os.listdir(base)):
        lang_path = os.path.join(base, lang_dir)
        if not os.path.isdir(lang_path):
            continue
        parquets = sorted(glob.glob(os.path.join(lang_path, '*.parquet')))
        # sample up to 2 parquet files per lang dir, read only repo_name column
        sample_pqs = parquets[:2]
        for pq_file in sample_pqs:
            try:
                pf = pq.ParquetFile(pq_file)
                tbl = pf.read(columns=['repo_name'])
                names = tbl.column('repo_name').to_pylist()
                for n in names:
                    if n:
                        udc_repos.add(n.strip().lower())
            except Exception as e:
                print(f'  {label}/{lang_dir}: error {e}')
print(f'UltraData-Code: {len(udc_repos)} unique repos (sampled, {time.time()-t0:.1f}s)')

# ---- 2. Sample stack-v3-train repo_paths ----
STACK_DIR = '/nas_inference/app.e0031982/datasets/HuggingFaceCode/stack-v3-train/data'
all_parquets = sorted(glob.glob(os.path.join(STACK_DIR, '*.parquet')))
print(f'stack-v3-train: {len(all_parquets)} total parquet files')

# sample 20 shards spread across the 4600
sample_indices = [0, 460, 920, 1380, 1840, 2300, 2760, 3220, 3680, 4140]
sample_indices = [i for i in sample_indices if i < len(all_parquets)]

stack_repos = set()
stack_repo_list = []
t0 = time.time()
for idx in sample_indices:
    pq_file = all_parquets[idx]
    try:
        pf = pq.ParquetFile(pq_file)
        # read only repo_path column (avoid loading heavy 'files' content)
        tbl = pf.read(columns=['repo_path'])
        rps = tbl.column('repo_path').to_pylist()
        for rp in rps:
            if rp:
                rl = rp.strip().lower()
                stack_repos.add(rl)
                stack_repo_list.append(rl)
    except Exception as e:
        print(f'  shard {idx}: error {e}')

print(f'stack-v3-train: {len(stack_repos)} unique repos from {len(sample_indices)} shards ({time.time()-t0:.1f}s)')
print(f'  (total repo rows sampled: {len(stack_repo_list)})')

# ---- 3. Compute overlap ----
overlap = stack_repos & udc_repos
overlap_rate = len(overlap) / len(stack_repos) * 100 if stack_repos else 0
print(f'\n{"="*60}')
print(f'REPO-LEVEL OVERLAP ANALYSIS')
print(f'{"="*60}')
print(f'UltraData-Code (L2+L3 sampled): {len(udc_repos):,} unique repos')
print(f'stack-v3-train (20 shards):     {len(stack_repos):,} unique repos')
print(f'Overlap (intersection):         {len(overlap):,} repos')
print(f'Overlap rate (stack→UDC):       {overlap_rate:.1f}%')
print(f'Unique to stack-v3:             {len(stack_repos)-len(overlap):,} repos ({100-overlap_rate:.1f}%)')

# ---- 4. Extrapolation ----
# stack-v3-train has ~200 repos/shard × 4600 shards ≈ 920K repos (downloaded portion)
# Full dataset: 173M repos
est_total_stack_repos = len(stack_repos) / len(sample_indices) * len(all_parquets)
print(f'\nExtrapolation:')
print(f'  stack-v3-train downloaded (~4600 shards): ~{est_total_stack_repos:,.0f} unique repos est')
print(f'  UltraData-Code L2+L3: ~550B tokens (known)')
print(f'  stack-v3-train 2TB: ~2,025B tokens est (ratio-based)')
print(f'  Overlap rate {overlap_rate:.1f}% → ~{overlap_rate/100*est_total_stack_repos:,.0f} repos shared with UDC')
print(f'  → ~{100-overlap_rate:.1f}% of stack-v3 content is NEW (not in UDC)')

# sample some overlapping repos for evidence
sample_overlap = list(overlap)[:10]
print(f'\nSample overlapping repos (first 10): {sample_overlap}')
sample_unique = list(stack_repos - udc_repos)[:10]
print(f'Sample unique-to-stack repos (first 10): {sample_unique}')
