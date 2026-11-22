#!/usr/bin/env python3
"""Static anti-hardcode audit for shard D cases (r1170).

For each D case with a reference/check.py, compute static indicators:
  k_check         : heuristic count of independent failure conditions in check.py
  has_subprocess  : check.py runs candidate via subprocess/os.system (real execution)
  has_hidden_b    : check.py references hidden/ or a B input path
  only_b          : 'unknown' (static can't reliably determine)
  negative_present: negative/ dir with >=2 files + negative_selftest.py
  print_only_risk : no subprocess AND lots of 'in' string membership checks -> HIGH risk
Output: designflow/anti_hardcode_audit_D.tsv
"""
import json, os, re
from collections import Counter

BENCH = '/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow'
REF   = os.path.join(BENCH, 'reference')
OUT   = '/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/anti_hardcode_audit_D.tsv'

def find_ref_dir(tid, ref_dirs):
    if tid in ref_dirs: return tid
    short = tid.replace('EDA-Eval-DesignFlow-', '')
    if short in ref_dirs: return short
    return None

def count_conditions(src):
    """Count independent failure conditions across common check.py patterns.

    Covers: assert / raise <Err> / if not / cond(...) accumulators /
    conditions.append(...) / return False / "pass": False / failed markers.
    """
    n = 0
    for line in src.splitlines():
        s = line.strip()
        if re.match(r'assert\s', s): n += 1; continue
        if re.match(r'raise\s+(AssertionError|RuntimeError|ValueError|Exception|SystemExit)', s): n += 1; continue
        if re.match(r'if\s+not\s', s): n += 1; continue
        # accumulator patterns: cond('a', ...) / cond("a", ...) / conditions.append(...)
        if re.match(r'cond\s*\(', s): n += 1; continue
        if re.match(r'(conditions|results|checks)\.append\s*\(', s): n += 1; continue
    return n

def parse_k_from_rationale(rationale):
    """Parse stated k from test_rationale: 'N 条断言：...' or count ①②③ markers."""
    if not rationale: return None
    m = re.search(r'(\d+)\s*条断言', rationale)
    if m: return int(m.group(1))
    # count circled-number markers
    circled = re.findall(r'[\u2460-\u2473\u3251-\u325f\u32b1-\u32bf]', rationale)
    if circled: return len(circled)
    return None

def analyze_case(tid, ref_subdir, rationale):
    rdir = os.path.join(REF, ref_subdir)
    check_path = os.path.join(rdir, 'check.py')
    inline = False
    if not os.path.isfile(check_path):
        # check.py may be inline in jsonl `test` field — that's a legitimate design variant
        inline = True
        src = ''
    else:
        with open(check_path, encoding='utf-8', errors='replace') as f:
            src = f.read()
    k_static = count_conditions(src) if src else 0
    k_rationale = parse_k_from_rationale(rationale)
    k_check = max(filter(lambda x: x is not None, [k_rationale, k_static]), default=0)
    has_subprocess = bool(re.search(r'\b(subprocess|os\.system|os\.popen)\b', src)) if src else True
    has_hidden_b = bool(re.search(r'hidden', src, re.I)) if src else True
    only_b = 'unknown'
    # negative detection: negatives may live in negative/ subdir OR as top-level
    # fake_*.py / _neg_*.zip / neg_*.py files; negative_selftest.py may be at top
    # level OR inside negative/. Count all negative artifacts in ref dir recursively (depth<=2).
    neg_artifacts = 0
    neg_selftest = False
    for root, dirs, files in os.walk(rdir):
        depth = root[len(rdir):].count(os.sep)
        if depth > 2:  # don't recurse too deep
            dirs[:] = []
            continue
        for fn in files:
            low = fn.lower()
            if fn == 'negative_selftest.py' or fn.endswith('_selftest.py'):
                neg_selftest = True
            if (re.match(r'(fake_|neg_|_neg_|negative_)', low) or
                'hardcode' in low or 'core_deleted' in low or 'coredeleted' in low or
                'empty_shell' in low or 'emptyshell' in low or 'print_only' in low or
                'printonly' in low or 'stub' in low):
                neg_artifacts += 1
    negative_present = neg_selftest and (neg_artifacts >= 2)
    in_checks = len(re.findall(r'\bin\s+', src)) if src else 0
    print_only_risk = (not has_subprocess) and (in_checks >= k_static * 0.6) and (k_static > 0)
    gaps = []
    if not inline and k_check < 8: gaps.append(f'k<8({k_check})')
    if not inline and not has_subprocess: gaps.append('no-subprocess')
    if not inline and not has_hidden_b: gaps.append('no-hidden-B')
    if not negative_present: gaps.append('no-negative')
    if print_only_risk: gaps.append('print_only-risk')
    verdict = 'GAP' if gaps else 'PASS'
    return {'shard':'D','case_id':tid,'k_check':k_check if not inline else 'inline',
            'anti_hardcode':'y' if (has_subprocess and negative_present) else 'n',
            'only_b':only_b,'print_only':'risk' if print_only_risk else 'ok',
            'core_deleted':'static-skip','hardcode_a':'static-skip',
            'negative_present':'y' if negative_present else 'n',
            'verdict':verdict,'gaps':';'.join(gaps) if gaps else '','ref_dir':ref_subdir}

def main():
    ref_dirs = set(os.listdir(REF))
    cases = []
    with open(os.path.join(BENCH, 'EDA-Eval-DesignFlow_D.jsonl')) as f:
        for l in f:
            if not l.strip(): continue
            c = json.loads(l)
            cases.append((c.get('task_id',''),
                          (c.get('metadata') or {}).get('test_rationale',''),
                          c.get('test','')))
    rows = []
    for tid, rationale, test_src in cases:
        rd = find_ref_dir(tid, ref_dirs)
        if not rd:
            # no reference dir — check.py is inline in jsonl `test`. Analyze it inline.
            k_rationale = parse_k_from_rationale(rationale)
            k_static = count_conditions(test_src) if test_src else 0
            k_check = max(filter(lambda x: x is not None, [k_rationale, k_static]), default=0)
            has_subprocess = bool(re.search(r'\b(subprocess|os\.system|os\.popen)\b', test_src)) if test_src else False
            has_hidden_b = bool(re.search(r'hidden', test_src, re.I)) if test_src else False
            # negatives for inline cases: may be attached as assets/<id>/negative/ ...
            # we cannot easily see them from here; mark unknown and do NOT flag no-negative
            # for inline cases (they often ship negatives in assets/).
            gaps = []
            if k_check < 8: gaps.append(f'k<8({k_check})')
            if not has_subprocess: gaps.append('no-subprocess')
            if not has_hidden_b: gaps.append('no-hidden-B')
            verdict = 'GAP' if gaps else 'PASS(inline)'
            rows.append({'shard':'D','case_id':tid,'k_check':k_check,
                         'anti_hardcode':'y' if has_subprocess else 'n',
                         'only_b':'unknown','print_only':'n/a',
                         'core_deleted':'static-skip','hardcode_a':'static-skip',
                         'negative_present':'inline','verdict':verdict,
                         'gaps':';'.join(gaps) if gaps else '','ref_dir':'(inline)'})
            continue
        r = analyze_case(tid, rd, rationale)
        if r: rows.append(r)
    cols = ['shard','case_id','k_check','anti_hardcode','only_b','print_only',
            'core_deleted','hardcode_a','negative_present','verdict','gaps','ref_dir']
    with open(OUT, 'w') as f:
        f.write('\t'.join(cols) + '\n')
        for r in rows:
            f.write('\t'.join(str(r.get(c,'')) for c in cols) + '\n')
    n = len(rows); gaps = [r for r in rows if r['verdict']=='GAP']
    print(f'TOTAL: {n}  PASS: {n-len(gaps)}  GAP: {len(gaps)}')
    all_gaps = []
    for r in gaps: all_gaps.extend(r['gaps'].split(';') if r['gaps'] else [])
    print('GAP reasons:', Counter(all_gaps).most_common())
    print('\nTop 20 GAP (k asc, prefer low k):')
    gs = sorted(gaps, key=lambda r: (int(r['k_check']) if str(r['k_check']).isdigit() else 9999, r['case_id']))
    for r in gs[:20]: print(f"  {r['case_id']:48} k={str(r['k_check']):>4} gaps={r['gaps']}")

if __name__ == '__main__':
    main()
