#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""stackv3_l4_filter.py — PC-1: Analyze tokenized stack-v3 shards for L4 filtering."""
from __future__ import annotations
import argparse, json, os, sys, time
from pathlib import Path
from collections import Counter

L4_LANGS = {'Python','C','C++','C Header','Verilog','SystemVerilog','Tcl'}
NON_L4_PRIORITY = {'Makefile','Shell','CMake','Bazel','SKILL','Perl'}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tokenized-dir', default='/nas_user/app.e0031982/datasets/baize-data/tokenized/HuggingFaceCode/stack-v3-train')
    ap.add_argument('--output-dir', default='/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data')
    args = ap.parse_args()
    tok_dir = Path(args.tokenized_dir); out_dir = Path(args.output_dir); out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = tok_dir / 'MANIFEST.json'
    if not manifest_path.exists(): print(f'ERROR: {manifest_path} not found'); sys.exit(1)
    with open(manifest_path) as f: manifest = json.load(f)
    print(f'MANIFEST: {len(manifest.get("shards",[]))} shards, {manifest.get("total_tokens",0):,} tokens')
    json_files = sorted(tok_dir.glob('stackv3_s*.json'))
    print(f'Found {len(json_files)} shard .json files')
    t0 = time.time(); shard_stats = []; total_l4_docs = 0; total_non_l4_docs = 0
    total_l4_tokens_est = 0; total_tokens_actual = 0; total_docs_actual = 0; lang_totals = Counter()
    for i, jf in enumerate(json_files):
        with open(jf) as f: s = json.load(f)
        nt = s.get('num_tokens',0); nd = s.get('num_documents',0); lc = s.get('lang_counts',{})
        shard_name = s.get('shard_name', jf.stem)
        total_tokens_actual += nt; total_docs_actual += nd
        l4_docs = sum(lc.get(l,0) for l in L4_LANGS)
        non_l4_docs = sum(lc.get(l,0) for l in NON_L4_PRIORITY)
        for lang, cnt in lc.items(): lang_totals[lang] += cnt
        total_l4_docs += l4_docs; total_non_l4_docs += non_l4_docs
        l4_ratio = l4_docs / nd if nd > 0 else 0; l4_tokens_est = int(nt * l4_ratio)
        total_l4_tokens_est += l4_tokens_est
        shard_stats.append({'shard_name':shard_name,'shard_file':jf.stem,'num_tokens':nt,'num_documents':nd,'l4_docs':l4_docs,'non_l4_docs':non_l4_docs,'l4_ratio':round(l4_ratio,4),'l4_tokens_est':l4_tokens_est,'lang_counts':lc})
        if (i+1) % 1000 == 0: print(f'  [{i+1}/{len(json_files)}] elapsed={time.time()-t0:.1f}s', flush=True)
    elapsed = time.time() - t0
    l4_doc_pct = total_l4_docs / total_docs_actual * 100 if total_docs_actual > 0 else 0
    l4_token_pct = total_l4_tokens_est / total_tokens_actual * 100 if total_tokens_actual > 0 else 0
    print(f'\n{"="*60}\nPC-1 L4 Filter Analysis ({elapsed:.1f}s)')
    print(f'  Shards: {len(shard_stats)} | Tokens: {total_tokens_actual:,} | Docs: {total_docs_actual:,}')
    print(f'  L4 docs: {total_l4_docs:,} ({l4_doc_pct:.1f}%) | L4 tokens est: {total_l4_tokens_est:,} ({l4_token_pct:.1f}%)')
    print(f'\n  Language breakdown:')
    for lang, cnt in lang_totals.most_common():
        pct = cnt / total_docs_actual * 100; m = 'L4' if lang in L4_LANGS else ('--' if lang in NON_L4_PRIORITY else '??')
        print(f'    [{m}] {lang:20s}: {cnt:>10,} ({pct:5.1f}%)')
    report = {'analysis':'PC-1: stack-v3 L4 filter','timestamp':time.strftime('%Y-%m-%d %H:%M:%S'),'l4_languages':sorted(L4_LANGS),'non_l4_priority':sorted(NON_L4_PRIORITY),'total_shards':len(shard_stats),'total_tokens_actual':total_tokens_actual,'total_docs_actual':total_docs_actual,'total_l4_docs':total_l4_docs,'l4_doc_pct':round(l4_doc_pct,2),'l4_tokens_estimated':total_l4_tokens_est,'l4_token_pct':round(l4_token_pct,2),'lang_totals':dict(lang_totals.most_common()),'shards':shard_stats}
    rp = out_dir / 'stackv3_l4_filter_report.json'
    with open(rp,'w') as f: json.dump(report, f, indent=2, ensure_ascii=False)
    print(f'\n  Report: {rp}')
    tp = out_dir / 'stackv3_l4_shard_whitelist.tsv'
    with open(tp,'w') as f:
        f.write('shard_file\tnum_tokens\tl4_tokens_est\tl4_ratio\tnum_documents\tl4_docs\n')
        for s in sorted(shard_stats, key=lambda x: x['shard_file']):
            f.write(f"{s['shard_file']}\t{s['num_tokens']}\t{s['l4_tokens_est']}\t{s['l4_ratio']}\t{s['num_documents']}\t{s['l4_docs']}\n")
    print(f'  Whitelist: {tp}')
    print(f'\n  Go/No-Go G1: L4 tokens = {total_l4_tokens_est/1e9:.1f}B ({"PASS" if total_l4_tokens_est >= 250e9 else "FAIL"} >= 250B)')

if __name__ == '__main__': main()
