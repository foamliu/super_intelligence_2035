#!/usr/bin/env python3
"""Categorize ALL 97 fix1 STILL_NOT_APPLIED entries by exact failure reason."""
import json, ast, os, re
from collections import Counter

HARNESS_DIR = os.path.dirname(os.path.abspath(__file__))
FIX1_JSON = os.path.join(HARNESS_DIR, 'kimi_pilot_results.fix1.json')

with open(FIX1_JSON) as f:
    data = json.load(f)

na_entries = []
for e in data:
    try:
        ne = ast.literal_eval(e['new_eval']) if isinstance(e['new_eval'], str) else e['new_eval']
    except Exception:
        ne = {}
    if not ne.get('patch_applied', False) and not ne.get('resolved', False):
        na_entries.append(e)

print(f"Total STILL_NOT_APPLIED: {len(na_entries)}")
print()

categories = Counter()
repo_cat = {}
details = []

for e in na_entries:
    repo = e['repo']
    inst = e['instance_id']
    hrn = e['harness']
    log_dir = e['log_dir']
    
    test_output_path = os.path.join(log_dir, 'test_output.txt')
    report_path = os.path.join(log_dir, 'report.json')
    
    cat = 'unknown'
    reason = ''
    
    if os.path.isfile(report_path):
        try:
            with open(report_path) as rf:
                rpt = json.load(rf)
            inst_key = list(rpt.keys())[0] if rpt else None
            if inst_key:
                reason = rpt[inst_key].get('infra_failure_reason', '')
        except Exception:
            pass
    
    content = ''
    if os.path.isfile(test_output_path):
        try:
            with open(test_output_path, 'r', errors='replace') as tf:
                content = tf.read()
        except Exception:
            pass
    
    if 'Python 3.9 or above is required' in content or 'You are using Python 3.8' in content:
        cat = 'py_version_38_needs_39'
    elif 'Scikit-learn requires Python 3.8' in content or 'current Python version is 3.6' in content:
        cat = 'py_version_36_needs_38'
    elif 'cannot import name' in content and 'url_quote' in content:
        cat = 'werkzeug_version'
    elif 'cannot import name' in content and 'resources' in content:
        cat = 'py_version_36_needs_38'
    elif 'pathspec' in content and 'did not match' in content:
        cat = 'git_checkout_fail'
    elif 'already exists in working directory' in content:
        cat = 'git_apply_conflict'
    elif content.strip() == '':
        cat = 'no_log'
    else:
        pip_fail = re.search(r'(pip install.*error|error:.*subprocess|RuntimeError.*requires)', content)
        if pip_fail:
            cat = 'pip_install_fail'
        else:
            test_section = content[content.find('>>>>> Start Test Output'):]
            if test_section and 'SWEBENCH_TEST_EXIT_CODE' in test_section:
                cat = 'test_fail_not_infra'
            else:
                cat = 'other'
    
    categories[cat] += 1
    if repo not in repo_cat:
        repo_cat[repo] = Counter()
    repo_cat[repo][cat] += 1
    details.append((hrn, inst, repo, cat, reason))

print("=== Category distribution ===")
for k, v in sorted(categories.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

print("\n=== By repo x category ===")
for repo in sorted(repo_cat.keys()):
    print(f"  {repo}:")
    for cat, cnt in sorted(repo_cat[repo].items(), key=lambda x: -x[1]):
        print(f"    {cat}: {cnt}")

print("\n=== Sample details (first 20) ===")
for hrn, inst, repo, cat, reason in details[:20]:
    print(f"  {hrn}|{inst} -> {cat}" + (f" ({reason})" if reason else ""))
