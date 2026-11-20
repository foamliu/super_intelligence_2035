#!/usr/bin/env python3
"""Final comprehensive static analysis of EDA-Eval-PyAether 113-task results.
Compares Base (MiniCPM5-2B) vs SFT (minicpm5-sft global_step_70).
"""
import json, re, os
from collections import defaultdict
from statistics import mean

HERE = os.path.dirname(os.path.abspath(__file__))
RESULT_FILE = os.path.join(HERE, "eda_eval_static_full_wake287.json")
OUTPUT_FILE = os.path.join(HERE, "eda_eval_static_final_summary.json")

def strip_think_and_fence(code):
    if not code:
        return ""
    code = re.sub(r'<think>.*?</think>', '', code, flags=re.DOTALL)
    code = re.sub(r'<think>.*', '', code, flags=re.DOTALL)
    lines = code.split('\n')
    cleaned = []
    in_fence = False
    for line in lines:
        s = line.strip()
        if s.startswith('```'):
            in_fence = not in_fence
            continue
        if not in_fence:
            cleaned.append(line)
    return '\n'.join(cleaned).strip()

def extract_code(raw):
    if not raw:
        return ""
    code = strip_think_and_fence(raw)
    lines = code.split('\n')
    func_start = None
    for i, line in enumerate(lines):
        if line.strip().startswith('def '):
            func_start = i
            break
    if func_start is not None:
        result_lines = lines[func_start:]
        while result_lines and result_lines[-1].strip() == '':
            result_lines.pop()
        return '\n'.join(result_lines)
    return code

def check_syntax(code):
    if not code or len(code.strip()) < 5:
        return False, "empty"
    try:
        compile(code, '<check>', 'exec')
        return True, "ok"
    except SyntaxError as e:
        return False, f"line {e.lineno}: {e.msg}"

def has_function_def(code):
    return bool(re.search(r'^\s*def\s+\w+\s*\(', code, re.MULTILINE))

def extract_api_calls(code):
    if not code:
        return set()
    return set(re.findall(r'(?:pyAether|pyScript)\.([a-zA-Z_]\w*)', code))

def analyze():
    with open(RESULT_FILE) as f:
        data = json.load(f)
    total = len(data)
    if total == 0:
        print("ERROR: No results found"); return
    results = []
    for task_id, td in data.items():
        meta = td.get('metadata', {})
        scenario = meta.get('scenario', 'Unknown')
        category = meta.get('category', 'Unknown')
        apis_expected = td.get('apis_expected', [])
        expected_api_names = set(p.split('.')[-1] for p in apis_expected if '.' in p)
        base_raw = td.get('base', {})
        sft_raw = td.get('sft', {})
        base_code = extract_code(base_raw.get('code', ''))
        sft_code = extract_code(sft_raw.get('code', ''))
        bs_ok, bs_err = check_syntax(base_code)
        ss_ok, ss_err = check_syntax(sft_code)
        base_apis = extract_api_calls(base_code)
        sft_apis = extract_api_calls(sft_code)
        base_api_cov = len(base_apis & expected_api_names) / max(len(expected_api_names), 1)
        sft_api_cov = len(sft_apis & expected_api_names) / max(len(expected_api_names), 1)
        sft_builtin = bool(re.search(r'\b(import|from)\s+(os|sys|time|re|json|math|datetime|pathlib|collections)\b', sft_code))
        base_builtin = bool(re.search(r'\b(import|from)\s+(os|sys|time|re|json|math|datetime|pathlib|collections)\b', base_code))
        base_trunc = base_raw.get('finish_reason', '') != 'stop' if isinstance(base_raw, dict) else True
        sft_trunc = sft_raw.get('finish_reason', '') != 'stop' if isinstance(sft_raw, dict) else True
        results.append({
            'task_id': task_id, 'scenario': scenario, 'category': category,
            'base_syntax': bs_ok, 'sft_syntax': ss_ok,
            'base_has_func': has_function_def(base_code), 'sft_has_func': has_function_def(sft_code),
            'base_truncated': base_trunc, 'sft_truncated': sft_trunc,
            'base_code_len': len(base_code), 'sft_code_len': len(sft_code),
            'base_time': base_raw.get('time_sec', 0) if isinstance(base_raw, dict) else 0,
            'sft_time': sft_raw.get('time_sec', 0) if isinstance(sft_raw, dict) else 0,
            'base_api_coverage': base_api_cov, 'sft_api_coverage': sft_api_cov,
            'sft_uses_builtin': sft_builtin, 'base_uses_builtin': base_builtin,
        })
    n = len(results)
    bsn = sum(1 for r in results if r['base_syntax'])
    ssn = sum(1 for r in results if r['sft_syntax'])
    bfn = sum(1 for r in results if r['base_has_func'])
    sfn = sum(1 for r in results if r['sft_has_func'])
    btn = sum(1 for r in results if r['base_truncated'])
    stn = sum(1 for r in results if r['sft_truncated'])
    blens = [r['base_code_len'] for r in results if r['base_code_len'] > 0]
    slens = [r['sft_code_len'] for r in results if r['sft_code_len'] > 0]
    btimes = [r['base_time'] for r in results if r['base_time'] > 0]
    stimes = [r['sft_time'] for r in results if r['sft_time'] > 0]
    bcovs = [r['base_api_coverage'] for r in results]
    scovs = [r['sft_api_coverage'] for r in results]
    sbn = sum(1 for r in results if r['sft_uses_builtin'])
    bbn = sum(1 for r in results if r['base_uses_builtin'])
    scenarios = defaultdict(list)
    categories = defaultdict(list)
    for r in results:
        scenarios[r['scenario']].append(r)
        categories[r['category']].append(r)
    summary = {
        'total_tasks': n,
        'overall': {
            'base_syntax_rate': bsn/n, 'sft_syntax_rate': ssn/n, 'syntax_diff': (ssn-bsn)/n,
            'base_func_rate': bfn/n, 'sft_func_rate': sfn/n,
            'base_truncation_rate': btn/n, 'sft_truncation_rate': stn/n, 'truncation_ratio': btn/max(stn,1),
            'base_code_len_mean': mean(blens) if blens else 0, 'sft_code_len_mean': mean(slens) if slens else 0,
            'code_len_ratio': mean(blens)/max(mean(slens),1) if slens else 0,
            'base_time_mean': mean(btimes) if btimes else 0, 'sft_time_mean': mean(stimes) if stimes else 0,
            'time_ratio': mean(btimes)/max(mean(stimes),1) if stimes else 0,
            'base_api_coverage_mean': mean(bcovs), 'sft_api_coverage_mean': mean(scovs),
            'api_coverage_diff': mean(scovs)-mean(bcovs),
            'sft_uses_builtin_count': sbn, 'base_uses_builtin_count': bbn,
        },
        'per_scenario': {}, 'per_category': {},
    }
    for sc, sub in sorted(scenarios.items()):
        sn = len(sub)
        summary['per_scenario'][sc] = {
            'n': sn,
            'base_syntax': sum(1 for r in sub if r['base_syntax'])/sn,
            'sft_syntax': sum(1 for r in sub if r['sft_syntax'])/sn,
            'syntax_diff': (sum(1 for r in sub if r['sft_syntax'])-sum(1 for r in sub if r['base_syntax']))/sn,
            'base_truncation': sum(1 for r in sub if r['base_truncated'])/sn,
            'sft_truncation': sum(1 for r in sub if r['sft_truncated'])/sn,
            'base_api_coverage': mean([r['base_api_coverage'] for r in sub]),
            'sft_api_coverage': mean([r['sft_api_coverage'] for r in sub]),
        }
    for cat, sub in sorted(categories.items()):
        sn = len(sub)
        summary['per_category'][cat] = {
            'n': sn,
            'base_syntax': sum(1 for r in sub if r['base_syntax'])/sn,
            'sft_syntax': sum(1 for r in sub if r['sft_syntax'])/sn,
            'syntax_diff': (sum(1 for r in sub if r['sft_syntax'])-sum(1 for r in sub if r['base_syntax']))/sn,
            'base_api_coverage': mean([r['base_api_coverage'] for r in sub]),
            'sft_api_coverage': mean([r['sft_api_coverage'] for r in sub]),
        }
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    o = summary['overall']
    print(f"=== FINAL STATIC ANALYSIS: {n}/113 tasks ===")
    print()
    print(f"[OVERALL]")
    print(f"  Syntax valid:      Base {bsn}/{n} ({o['base_syntax_rate']*100:.1f}%)  SFT {ssn}/{n} ({o['sft_syntax_rate']*100:.1f}%)  diff {o['syntax_diff']*100:+.1f}pp")
    print(f"  Has function:      Base {bfn}/{n} ({o['base_func_rate']*100:.1f}%)  SFT {sfn}/{n} ({o['sft_func_rate']*100:.1f}%)")
    print(f"  Truncated:         Base {btn}/{n} ({o['base_truncation_rate']*100:.1f}%)  SFT {stn}/{n} ({o['sft_truncation_rate']*100:.1f}%)  ratio {o['truncation_ratio']:.1f}x")
    print(f"  Code length (mean):Base {o['base_code_len_mean']:.0f}ch  SFT {o['sft_code_len_mean']:.0f}ch  ratio {o['code_len_ratio']:.1f}x (Base longer)")
    print(f"  Time (mean):       Base {o['base_time_mean']:.1f}s  SFT {o['sft_time_mean']:.1f}s  ratio {o['time_ratio']:.1f}x (Base slower)")
    print(f"  API coverage:      Base {o['base_api_coverage_mean']:.3f}  SFT {o['sft_api_coverage_mean']:.3f}  diff {o['api_coverage_diff']:+.3f}")
    print(f"  Uses Python builtins: Base {bbn}  SFT {sbn} (SFT substituting pyAether with builtins)")
    print()
    print(f"[PER-SCENARIO]")
    for sc, sv in summary['per_scenario'].items():
        print(f"  {sc:20s} n={sv['n']:3d}  syntax {sv['base_syntax']*100:5.1f}%->{sv['sft_syntax']*100:5.1f}% ({sv['syntax_diff']*100:+5.1f}pp)  trunc {sv['base_truncation']*100:5.1f}%->{sv['sft_truncation']*100:5.1f}%  api {sv['base_api_coverage']:.3f}->{sv['sft_api_coverage']:.3f}")
    print()
    print(f"[PER-CATEGORY]")
    for cat, cv in summary['per_category'].items():
        print(f"  {cat:30s} n={cv['n']:3d}  syntax {cv['base_syntax']*100:5.1f}%->{cv['sft_syntax']*100:5.1f}% ({cv['syntax_diff']*100:+5.1f}pp)  api {cv['base_api_coverage']:.3f}->{cv['sft_api_coverage']:.3f}")
    print()
    print(f"Summary saved to: {OUTPUT_FILE}")

if __name__ == '__main__':
    analyze()
