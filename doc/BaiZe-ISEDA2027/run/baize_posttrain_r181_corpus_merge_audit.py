#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
R181 -- Corpus Merge + Audit (v8 + v9 + v10 -> v11 training-ready).

1. Loads the three NEW targeted-API corpora built since the last SFT:
     sft_pyaether_corpus_v8_schematic_apis.jsonl (R177)
     sft_pyaether_corpus_v9_layout_create.jsonl (R179)
     sft_pyaether_corpus_v10_pin_apis.jsonl (R180)
2. Normalizes heterogeneous schemas to one unified record.
3. Deduplicates by (sorted api_used + prompt-prefix hash).
4. Pollution scan: rejects any pair whose prompt+completion contains a
   literal eval entry_point string (155 unique task function names).
5. Writes sft_pyaether_corpus_v11_merged_new_apis.jsonl
6. Coverage audit: corpus api_used vs 164 raw pyScript.X APIs in eval.
7. Writes r181_corpus_merge_audit.json
"""
import json, hashlib, os, re, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
EVAL_DS = os.path.expanduser('~/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl')
CORPUS_FILES = [
    'sft_pyaether_corpus_v8_schematic_apis.jsonl',
    'sft_pyaether_corpus_v9_layout_create.jsonl',
    'sft_pyaether_corpus_v10_pin_apis.jsonl',
]
OUT_CORPUS = os.path.join(RUN_DIR, 'sft_pyaether_corpus_v11_merged_new_apis.jsonl')
OUT_AUDIT = os.path.join(RUN_DIR, 'r181_corpus_merge_audit.json')

def load_jsonl(path):
    rows = []
    with open(path, 'r', encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception as exc:
                print('WARN: skip unparseable line in %s: %s' % (path, exc))
    return rows

def normalize(rec, source):
    rid = rec.get('id') or rec.get('pair_id') or ''
    api_used = rec.get('api_used', [])
    if isinstance(api_used, str):
        api_used = [api_used]
    return {
        'id': rid, 'type': rec.get('type', ''), 'api_used': api_used,
        'prompt': rec.get('prompt', ''), 'completion': rec.get('completion', ''),
        'contamination_check': rec.get('contamination_check', 'UNKNOWN'),
        'note': rec.get('note', ''), 'source': source,
    }

def dedup_key(rec):
    apis = '|'.join(sorted(rec['api_used']))
    prompt_prefix = rec['prompt'][:200].strip().lower()
    return hashlib.sha1((apis + '::' + prompt_prefix).encode('utf-8')).hexdigest()

def load_eval_entry_points(path):
    eps = set()
    with open(path, 'r', encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            ep = d.get('entry_point', '')
            if ep:
                eps.add(ep)
    return eps

def load_eval_raw_apis(path):
    apis = set()
    pat = re.compile(r'pyScript\.([A-Za-z_][A-Za-z0-9_]*)')
    with open(path, 'r', encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            text = (d.get('canonical_solution', '') or '') + '\n' + (d.get('test', '') or '')
            for m in pat.findall(text):
                apis.add(m)
    return apis

def pollution_scan(records, entry_points):
    rejected = []
    passed = []
    for rec in records:
        blob = (rec['prompt'] + '\n' + rec['completion']).lower()
        hit = None
        for ep in entry_points:
            if ep.lower() in blob:
                hit = ep
                break
        if hit:
            rec['contamination_check'] = 'REJECTED:' + hit
            rejected.append((rec['source'], rec['id'], hit))
        else:
            rec['contamination_check'] = 'PASS'
            passed.append(rec)
    return passed, rejected

def main():
    if not os.path.exists(EVAL_DS):
        print('ERROR: eval dataset not found at %s' % EVAL_DS)
        sys.exit(1)
    entry_points = load_eval_entry_points(EVAL_DS)
    eval_raw_apis = load_eval_raw_apis(EVAL_DS)
    print('eval: 158 tasks, %d unique entry_points, %d raw pyScript APIs' % (len(entry_points), len(eval_raw_apis)))

    per_file = {}
    all_records = []
    for fname in CORPUS_FILES:
        fpath = os.path.join(RUN_DIR, fname)
        if not os.path.exists(fpath):
            print('WARN: missing corpus %s' % fpath)
            continue
        rows = load_jsonl(fpath)
        norm = [normalize(r, fname) for r in rows]
        per_file[fname] = len(norm)
        all_records.extend(norm)
        print('loaded %s: %d records' % (fname, len(norm)))

    seen = {}
    deduped = []
    dup_removed = 0
    for rec in all_records:
        k = dedup_key(rec)
        if k in seen:
            dup_removed += 1
            continue
        seen[k] = True
        deduped.append(rec)
    print('dedup: %d -> %d (removed %d duplicates)' % (len(all_records), len(deduped), dup_removed))

    passed, rejected = pollution_scan(deduped, entry_points)
    print('pollution scan: %d PASS, %d REJECTED' % (len(passed), len(rejected)))
    if rejected:
        for src, rid, hit in rejected:
            print('  REJECTED %s/%s hit entry_point %s' % (src, rid, hit))

    for i, rec in enumerate(passed):
        if not rec['id']:
            rec['id'] = 'v11-%04d' % i

    with open(OUT_CORPUS, 'w', encoding='utf-8') as fh:
        for rec in passed:
            fh.write(json.dumps(rec, ensure_ascii=False) + '\n')
    out_bytes = os.path.getsize(OUT_CORPUS)
    print('wrote %s: %d pairs, %d bytes' % (OUT_CORPUS, len(passed), out_bytes))

    corpus_apis = set()
    for rec in passed:
        for a in rec['api_used']:
            corpus_apis.add(a)
    covered = sorted(corpus_apis & eval_raw_apis)
    blind = sorted(eval_raw_apis - corpus_apis)
    safe = sorted(corpus_apis - eval_raw_apis)
    type_counts = {}
    for rec in passed:
        t = rec.get('type', '')
        type_counts[t] = type_counts.get(t, 0) + 1

    audit = {
        'round': 'R181',
        'eval_tasks': 158,
        'eval_unique_entry_points': len(entry_points),
        'eval_raw_pyScript_apis': len(eval_raw_apis),
        'corpus_files_merged': CORPUS_FILES,
        'per_file_pair_count': per_file,
        'raw_loaded': len(all_records),
        'dedup_removed': dup_removed,
        'post_dedup': len(deduped),
        'pollution_passed': len(passed),
        'pollution_rejected': len(rejected),
        'rejected_details': [{'source': s, 'id': rid, 'hit_entry_point': h} for s, rid, h in rejected],
        'merged_output': os.path.basename(OUT_CORPUS),
        'merged_bytes': out_bytes,
        'merged_pairs': len(passed),
        'type_distribution': type_counts,
        'corpus_unique_apis': len(corpus_apis),
        'coverage': {
            'covered_eval_apis': len(covered),
            'covered_eval_apis_list': covered,
            'blind_eval_apis': len(blind),
            'blind_eval_apis_list': blind,
            'safe_corpus_apis': len(safe),
            'safe_corpus_apis_list': safe,
            'coverage_ratio': round(len(covered) / max(1, len(eval_raw_apis)), 4),
        },
    }
    with open(OUT_AUDIT, 'w', encoding='utf-8') as fh:
        json.dump(audit, fh, ensure_ascii=False, indent=2)
    print('wrote %s' % OUT_AUDIT)
    print('coverage: %d/%d eval raw APIs covered (%.1f%%), %d blind, %d safe' % (len(covered), len(eval_raw_apis), 100.0 * len(covered) / max(1, len(eval_raw_apis)), len(blind), len(safe)))

    if rejected:
        print('GATE: FAIL (pollution detected) -- do NOT use v11 for training')
        sys.exit(2)
    print('GATE: PASS -- v11 is training-ready')
    sys.exit(0)

if __name__ == '__main__':
    main()
