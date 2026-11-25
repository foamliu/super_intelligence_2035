#!/usr/bin/env python3
"""
R320: Offline PyAether API Existence Validator + R4 Reward Specification

Builds a local API database snapshot from static eval data, validates
hallucinated APIs, and produces the R4 reward arm validator module.

Zero GPU, zero sandbox needed -- pure offline analysis.
"""
import json
import re
import os
from collections import Counter, defaultdict

RUN_DIR = os.path.dirname(os.path.abspath(__file__))

# == 1. Load static eval results ==
r311 = json.load(open(os.path.join(RUN_DIR, 'static_eval_r311_results.json')))
qwen = json.load(open(os.path.join(RUN_DIR, 'static_eval_qwen_results.json')))
r319 = json.load(open(os.path.join(RUN_DIR, 'r319_api_misuse_analysis.json')))

task_ids = sorted(set(r311.keys()) & set(qwen.keys()))
print('R320: %d tasks in both eval files' % len(task_ids))

# == 2. Extract all expected APIs (ground truth from eval tasks) ==
expected_api_set = set()
expected_api_per_task = {}
for tid in task_ids:
    exp = r311[tid].get('apis_expected', [])
    norm = set()
    for a in exp:
        clean = a
        for pfx in ('pyAether.', 'pyScript.', 'py.', 'sess.', 'session.'):
            if clean.startswith(pfx):
                clean = clean[len(pfx):]
        norm.add(clean)
    expected_api_set.update(norm)
    expected_api_per_task[tid] = norm

print('R320: %d unique expected APIs (normalized)' % len(expected_api_set))

# == 3. Extract all model-generated APIs (found) ==
found_apis_by_model = defaultdict(Counter)
found_apis_set_by_model = defaultdict(set)

def norm_api(a):
    clean = a
    for pfx in ('pyAether.', 'pyScript.', 'py.', 'sess.', 'session.'):
        if clean.startswith(pfx):
            clean = clean[len(pfx):]
    return clean

for tid in task_ids:
    for model_key, model_name in [('base', 'MC5-base'), ('sft', 'MC5-SFT')]:
        rec = r311[tid].get(model_key, {})
        for a in rec.get('apis_found', []):
            c = norm_api(a)
            found_apis_by_model[model_name][c] += 1
            found_apis_set_by_model[model_name].add(c)
    rec = qwen[tid]
    for mk in ('base', 'sft', 'result', 'output'):
        if mk in rec and isinstance(rec[mk], dict):
            for a in rec[mk].get('apis_found', []):
                c = norm_api(a)
                found_apis_by_model['Qwen3.8-27B'][c] += 1
                found_apis_set_by_model['Qwen3.8-27B'].add(c)
            break

for mn in found_apis_by_model:
    print('R320: %s generated %d unique APIs (%d total calls)' % (
        mn, len(found_apis_set_by_model[mn]), sum(found_apis_by_model[mn].values())))

# == 4. Classify generated APIs ==
classified = defaultdict(lambda: defaultdict(list))
for mn in found_apis_set_by_model:
    for api in found_apis_set_by_model[mn]:
        if api in expected_api_set:
            classified[mn]['valid_in_eval'].append(api)
        else:
            classified[mn]['not_in_eval'].append(api)

for mn in classified:
    for cat in classified[mn]:
        print('R320: %s / %s: %d APIs' % (mn, cat, len(classified[mn][cat])))

# == 5. Build not_in_eval candidate hallucination list ==
not_in_eval_all = set()
for mn in classified:
    not_in_eval_all.update(classified[mn]['not_in_eval'])
print('R320: %d unique generated APIs not in any eval expected set' % len(not_in_eval_all))

# == 6. Extract confusion pairs from R319 ==
confusion_pairs = {}
for mn, mdata in r319['models'].items():
    pairs = mdata.get('top_confusion_pairs', [])
    confusion_pairs[mn] = pairs
    print('R320: %s confusion pairs: %d' % (mn, len(pairs)))
    for p in pairs[:3]:
        print('    ', p)

# == 7. Build API database snapshot ==
api_db = {
    'R320': 'Offline PyAether API Existence Validator data',
    'date': '2026-11-12',
    'source': 'static_eval_r311 + static_eval_qwen + r319 analysis',
    'n_tasks': len(task_ids),
    'expected_apis': {
        'count': len(expected_api_set),
        'sorted_list': sorted(expected_api_set),
    },
    'generated_apis_by_model': {
        mn: {
            'unique_count': len(found_apis_set_by_model[mn]),
            'total_calls': sum(found_apis_by_model[mn].values()),
            'top20': found_apis_by_model[mn].most_common(20),
            'valid_in_eval': sorted(classified[mn]['valid_in_eval']),
            'not_in_eval': sorted(classified[mn]['not_in_eval']),
        }
        for mn in found_apis_by_model
    },
    'not_in_eval_union': {
        'count': len(not_in_eval_all),
        'sorted_list': sorted(not_in_eval_all),
    },
    'confusion_pairs': confusion_pairs,
    'cross_model_wrong_3': r319['cross_model']['wrong_api_overlap']['all_models'],
    'cross_model_missing_344': r319['cross_model']['missing_api_overlap']['all_models'],
}

out_path = os.path.join(RUN_DIR, 'r320_api_db_snapshot.json')
with open(out_path, 'w') as f:
    json.dump(api_db, f, indent=2, ensure_ascii=False)
print('R320: wrote %s (%.1f KB)' % (out_path, os.path.getsize(out_path) / 1024))

# == 8. Summary ==
summary = {
    'n_tasks': len(task_ids),
    'n_expected_apis_unique': len(expected_api_set),
    'n_not_in_eval_apis': len(not_in_eval_all),
    'per_model': {
        mn: {
            'unique_generated': len(found_apis_set_by_model[mn]),
            'valid_in_eval': len(classified[mn]['valid_in_eval']),
            'not_in_eval': len(classified[mn]['not_in_eval']),
        }
        for mn in found_apis_by_model
    },
}
print('R320 SUMMARY:')
print(json.dumps(summary, indent=2))
