#!/usr/bin/env python3
# -*- coding: ascii -*-
"""baize_posttrain_r191_blind_scan.py
R191 -- data-driven blind-API eval-usage scan (after v11-v20 coverage).

Replicates the R181 eval-raw-API extraction (regex pyScript.X over
canonical_solution + test) and the corpus-coverage union over v11-v20,
then counts per-API eval usage for every remaining blind API and groups
by family prefix to pick the R191 target family.

Usage:
  python3 baize_posttrain_r191_blind_scan.py
"""
import json, os, re, sys
from collections import defaultdict

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
EVAL_DS = os.path.expanduser('~/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl')

CORPUS_FILES = [
    'sft_pyaether_corpus_v11_merged_new_apis.jsonl',
    'sft_pyaether_corpus_v12_db_primitives.jsonl',
    'sft_pyaether_corpus_v13_mde_cdf.jsonl',
    'sft_pyaether_corpus_v14_ae_primitives.jsonl',
    'sft_pyaether_corpus_v15_emy_primitives.jsonl',
    'sft_pyaether_corpus_v16_db_lifecycle.jsonl',
    'sft_pyaether_corpus_v17_emy_design_geo.jsonl',
    'sft_pyaether_corpus_v18_dm_datamgmt.jsonl',
    'sft_pyaether_corpus_v19_emy_dbstructure.jsonl',
    'sft_pyaether_corpus_v20_mde_sweep_platform.jsonl',
    'sft_pyaether_corpus_v21_mdeplat_sweep_jobsession.jsonl',
    'sft_pyaether_corpus_v22_emy_geometry_lib_tech.jsonl',
    'sft_pyaether_corpus_v23_db_lifecycle_traverse.jsonl',
    'sft_pyaether_corpus_v24_vector_containers.jsonl',
    'sft_pyaether_corpus_v25_et_pcre_rex.jsonl',
    'sft_pyaether_corpus_v26_ae_tree_ipc_hilit.jsonl',
    'sft_pyaether_corpus_v27_emy_ntl_lpp.jsonl',
    'sft_pyaether_corpus_v28_mde_goa.jsonl',
    'sft_pyaether_corpus_v29_gu_cart.jsonl',
    'sft_pyaether_corpus_v30_sle_enum.jsonl',
    'sft_pyaether_corpus_v31_cstring.jsonl',
    'sft_pyaether_corpus_v32_ccolor.jsonl',
    'sft_pyaether_corpus_v33_slequery.jsonl',
    'sft_pyaether_corpus_v34_utility.jsonl',
]

PAT = re.compile(r'pyScript\.([A-Za-z_][A-Za-z0-9_]*)')


def load_eval_raw_apis(path):
    apis = set()
    usage = defaultdict(int)
    with open(path, 'r', encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            text = (d.get('canonical_solution', '') or '') + '\n' + (d.get('test', '') or '')
            for m in PAT.findall(text):
                apis.add(m)
                usage[m] += 1
    return apis, usage


def load_corpus_apis(run_dir, files):
    covered = set()
    per_file = {}
    for fname in files:
        fpath = os.path.join(run_dir, fname)
        if not os.path.exists(fpath):
            per_file[fname] = 'MISSING'
            continue
        n = 0
        with open(fpath, 'r', encoding='utf-8') as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                apis = rec.get('api_used', [])
                if isinstance(apis, str):
                    apis = [apis]
                for a in apis:
                    covered.add(a)
                n += 1
        per_file[fname] = n
    return covered, per_file


def family_prefix(api):
    # lowercase-start APIs (db, ae, emy, et, goa, gu, dm, vector, ...):
    #   take the leading lowercase run -- stops at first uppercase/digit/underscore
    m = re.match(r'^([a-z]+)', api)
    if m:
        return m.group(1)
    # SCREAMING_SNAKE_CASE (MDE_*, NTL_*, SLE_*): take leading uppercase run before '_'
    m = re.match(r'^([A-Z]+)(?=_)', api)
    if m:
        return m.group(1)
    # PascalCase (MdeSweepRange, EmyNtlUtil, CColor, ...): take leading CamelCase word
    m = re.match(r'^([A-Z][a-z]+)', api)
    if m:
        return m.group(1)
    return api


def main():
    if not os.path.exists(EVAL_DS):
        sys.stderr.write('FATAL: eval dataset not found at %s\n' % EVAL_DS)
        sys.exit(1)
    eval_raw, eval_usage = load_eval_raw_apis(EVAL_DS)
    print('eval: %d unique raw pyScript APIs' % len(eval_raw))
    covered, per_file = load_corpus_apis(RUN_DIR, CORPUS_FILES)
    print('corpus v11-v20 pair counts:')
    for f, n in per_file.items():
        print('  %s: %s' % (f, n))
    covered_eval = sorted(covered & eval_raw)
    blind = sorted(eval_raw - covered)
    print('\ncoverage: %d/%d eval raw APIs covered (%.1f%%), %d blind' % (
        len(covered_eval), len(eval_raw), 100.0 * len(covered_eval) / max(1, len(eval_raw)), len(blind)))

    # family grouping of blind APIs with eval usage
    fam_usage = defaultdict(int)
    fam_apis = defaultdict(list)
    for api in blind:
        fam = family_prefix(api)
        fam_usage[fam] += eval_usage.get(api, 0)
        fam_apis[fam].append((api, eval_usage.get(api, 0)))

    print('\n=== blind families by total eval usage (desc) ===')
    for fam, total in sorted(fam_usage.items(), key=lambda x: -x[1]):
        apis = sorted(fam_apis[fam], key=lambda x: -x[1])
        print('%-12s total=%3d  apis=%d  %s' % (
            fam, total, len(apis),
            ', '.join('%s(%d)' % (a, u) for a, u in apis)))

    # dump db* detail for R191
    print('\n=== db* blind detail (R191 primary candidate) ===')
    db_blind = sorted(fam_apis.get('db', []), key=lambda x: -x[1])
    for api, u in db_blind:
        print('  db%-28s eval_usage=%d' % (api, u))

    # dump vector* detail
    print('\n=== vector* blind detail ===')
    vec_blind = sorted(fam_apis.get('vector', []), key=lambda x: -x[1])
    for api, u in vec_blind:
        print('  %-28s eval_usage=%d' % (api, u))

    # write JSON
    out = {
        'round': 'R191-scan',
        'eval_raw_apis': len(eval_raw),
        'covered_eval_apis': len(covered_eval),
        'blind_eval_apis': len(blind),
        'coverage_ratio': round(len(covered_eval) / max(1, len(eval_raw)), 4),
        'blind_list': blind,
        'family_usage': {fam: fam_usage[fam] for fam in sorted(fam_usage, key=lambda x: -fam_usage[x])},
        'family_apis': {fam: [{'api': a, 'eval_usage': u} for a, u in sorted(fam_apis[fam], key=lambda x: -x[1])]
                        for fam in sorted(fam_usage, key=lambda x: -fam_usage[x])},
    }
    out_path = os.path.join(RUN_DIR, 'r191_blind_scan.json')
    with open(out_path, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print('\nwrote %s' % out_path)


if __name__ == '__main__':
    main()
