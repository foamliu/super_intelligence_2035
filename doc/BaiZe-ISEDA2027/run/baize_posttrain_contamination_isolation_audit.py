#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""baize_posttrain_contamination_isolation_audit.py
Contamination-isolation audit for SFT/RL training data (red line sec5.1).
158 eval tasks' prompt+signature+assertion MUST NOT enter any training set;
API reference docs may synthesize training pairs but must be isolated by
API name / function signature. Zero GPU / pure CPU file parse.
Does not touch protocol/task/check.py/timeout/-p.
"""
import argparse, json, os, re, sys
from collections import Counter

_ATTR_RE = re.compile(r'\b(?:pyScript|pyAether|pyScriptNS|ns)\s*\.\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(')
_KEY_RE  = re.compile(r'\b(?:pyScript|pyAether|pyScriptNS|ns)\s*\[\s*["\']([A-Za-z_][A-Za-z0-9_]*)["\']\s*\]')
_DEF_RE  = re.compile(r'def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)')

def extract_api_names_from_code(code):
    if not code: return set()
    names = set()
    for m in _ATTR_RE.finditer(code): names.add(m.group(1))
    for m in _KEY_RE.finditer(code): names.add(m.group(1))
    return names

def strip_source_api(source):
    if not source: return None
    return source.split('.')[-1].strip()

def extract_signatures(prompt, entry_point):
    sigs = []
    if not prompt: return sigs
    for m in _DEF_RE.finditer(prompt):
        sigs.append((m.group(1), m.group(2).strip()))
    if entry_point and not any(s[0] == entry_point for s in sigs):
        sigs.append((entry_point, '<entry_point_no_def_found>'))
    return sigs

def load_eval_tasks(path):
    tasks = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line: tasks.append(json.loads(line))
    return tasks

def load_full_pool(path):
    raw = json.load(open(path, 'r', encoding='utf-8'))
    pool = set()
    for item in raw:
        if isinstance(item, (list, tuple)) and len(item) >= 1:
            pool.add(str(item[0]))
        elif isinstance(item, dict):
            n = item.get('name') or item.get('api') or item.get('api_name')
            if n: pool.add(str(n))
        elif isinstance(item, str):
            pool.add(item)
    return pool

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--eval', required=True)
    ap.add_argument('--pool', required=True)
    ap.add_argument('--out', default='sft_contamination_isolation_audit.json')
    ap.add_argument('--md', default='sft_contamination_isolation_audit.md')
    args = ap.parse_args()

    tasks = load_eval_tasks(args.eval)
    full_pool = load_full_pool(args.pool)

    forbidden_api_counter = Counter()
    forbidden_signatures = []
    task_records = []
    source_api_counter = Counter()
    cat_counter = Counter()

    for t in tasks:
        tid = t.get('task_id', '')
        prompt = t.get('prompt', '') or ''
        test = t.get('test', '') or ''
        entry = t.get('entry_point', '') or ''
        meta = t.get('metadata', {}) or {}
        source = strip_source_api(meta.get('source'))
        code = prompt + '\n' + test
        names = extract_api_names_from_code(code)
        if source:
            names.add(source); source_api_counter[source] += 1
        for n in names: forbidden_api_counter[n] += 1
        cat = meta.get('category') or 'Unknown'
        for a in names: cat_counter[cat] += 1
        sigs = extract_signatures(prompt, entry)
        for (dn, al) in sigs: forbidden_signatures.append((tid, dn, al))
        task_records.append({
            'task_id': tid, 'entry_point': entry, 'source_api': source,
            'scenario': meta.get('scenario'), 'category': cat,
            'n_unique_apis_meta': meta.get('num_unique_apis'),
            'n_extracted_apis': len(names), 'extracted_apis': sorted(names),
            'signatures': [{'def': dn, 'args': al} for (dn, al) in sigs],
        })

    forbidden_api_set = set(forbidden_api_counter.keys())
    forbidden_not_in_pool = sorted(forbidden_api_set - full_pool)
    forbidden_in_pool = sorted(forbidden_api_set & full_pool)
    available_for_sft = sorted(full_pool - forbidden_api_set)

    audit = {
        'meta': {
            'purpose': 'Contamination-isolation audit for SFT/RL training data (red line sec5.1).',
            'red_line': '158 eval tasks prompt+signatures+assertion MUST NOT enter any training set; API reference docs may synthesize training pairs but must be isolated by API name / function signature.',
            'eval_dataset': os.path.abspath(args.eval),
            'api_pool_source': os.path.abspath(args.pool),
            'n_eval_tasks': len(tasks), 'n_full_pool_apis': len(full_pool),
            'note': 'Zero GPU / pure CPU file parse. Does not touch protocol/task/check.py/timeout/-p.',
        },
        'summary': {
            'n_forbidden_apis': len(forbidden_api_set),
            'n_forbidden_apis_in_pool': len(forbidden_in_pool),
            'n_forbidden_apis_not_in_pool': len(forbidden_not_in_pool),
            'n_available_for_sft_apis': len(available_for_sft),
            'pct_pool_available_for_sft': round(100.0 * len(available_for_sft) / max(1, len(full_pool)), 2),
            'n_forbidden_signatures': len(forbidden_signatures),
            'n_unique_source_apis': len(source_api_counter),
            'n_eval_tasks': len(tasks),
            'n_full_pool_apis': len(full_pool),
        },
        'forbidden_api_frequency': [{'api': a, 'n_tasks': c} for a, c in forbidden_api_counter.most_common()],
        'forbidden_apis_not_in_pool': forbidden_not_in_pool,
        'available_for_sft_apis': available_for_sft,
        'forbidden_api_category_breakdown': [{'category': c, 'n_api_refs': n} for c, n in cat_counter.most_common()],
        'per_task': task_records,
    }
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(audit, f, ensure_ascii=False, indent=2)

    s = audit['summary']
    md = []
    md.append('# SFT/RL 训练数据污染隔离审计 (Contamination-Isolation Audit)')
    md.append('')
    md.append('> 红线 (§5.1): 158 eval 任务的 prompt + 函数签名 + 断言代码绝对不能进任何训练集;')
    md.append('> 允许用 API 参考文档合成训练对, 但必须按 **API 名 / 函数签名** 隔离。')
    md.append('')
    md.append('## 汇总')
    md.append('')
    md.append('| 项 | 值 |')
    md.append('|:--|--:|')
    md.append(f'| eval 任务数 | {s["n_eval_tasks"]} |')
    md.append(f'| PyAether 全量 API 池 | {s["n_full_pool_apis"]} |')
    md.append(f'| 禁用 API 名 (出现在 eval 任务) | {s["n_forbidden_apis"]} |')
    md.append(f'| 　其中在池内 | {s["n_forbidden_apis_in_pool"]} |')
    md.append(f'| 　其中不在池内 (动态/拼写) | {s["n_forbidden_apis_not_in_pool"]} |')
    md.append(f'| 禁用函数签名数 | {s["n_forbidden_signatures"]} |')
    md.append(f'| **可供 SFT 使用的 API 数 (池 − 禁用)** | **{s["n_available_for_sft_apis"]}** |')
    md.append(f'| 可用 API 占池比例 | {s["pct_pool_available_for_sft"]}% |')
    md.append('')
    md.append('## 禁用 API 频次 Top 30')
    md.append('')
    md.append('| API | 出现任务数 |')
    md.append('|:--|--:|')
    for it in audit['forbidden_api_frequency'][:30]:
        md.append(f'| `{it["api"]}` | {it["n_tasks"]} |')
    md.append('')
    md.append('## 禁用 API 按 eval 类别分布')
    md.append('')
    md.append('| 类别 | API 引用次数 |')
    md.append('|:--|--:|')
    for it in audit['forbidden_api_category_breakdown']:
        md.append(f'| {it["category"]} | {it["n_api_refs"]} |')
    md.append('')
    md.append('## 隔离规则 (预注册 · 先定后用)')
    md.append('')
    md.append('1. **API 名隔离**: held-out SFT/RL 训练任务只能使用 `available_for_sft_apis` 中的 API; 禁止使用 `forbidden_api_frequency` 列出的任一 API。')
    md.append('2. **函数签名隔离**: 训练任务的 `def <name>(<args>)` 不得与 `per_task[*].signatures` 任一条逐字相同。')
    md.append('3. **prompt/断言隔离**: 训练任务的 prompt 文本与断言代码不得复制 158 eval 任务的对应内容。')
    md.append('4. **可合成**: 允许用 API 参考文档 (来自 `available_for_sft_apis`) 合成 doc→code 训练对, 并按上述规则隔离。')
    md.append('5. **复检**: 生成训练集后用本脚本重跑, 确认 `forbidden_api_set ∩ 训练集API = ∅`。')
    md.append('')
    md.append('## 诚实性 / 局限')
    md.append('')
    md.append('- API 名提取基于正则匹配 `pyScript.<Name>(` / `pyAether.<Name>(` / 下标访问; 极少数动态拼接 API 名可能漏提取 (见 `forbidden_apis_not_in_pool`)。')
    md.append('- 全量 API 池来自 `api_summary_api_only.json`; 若池更新需重跑本审计。')
    md.append('- 本审计只做隔离边界界定, 不生成训练数据; 不碰 GPU/协议/题面/check.py/超时/-p。')
    md.append('')
    with open(args.md, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))

    print('=== Contamination-Isolation Audit ===')
    print(f'eval tasks           : {len(tasks)}')
    print(f'full API pool        : {len(full_pool)}')
    print(f'forbidden apis       : {len(forbidden_api_set)} (in_pool={len(forbidden_in_pool)}, not_in_pool={len(forbidden_not_in_pool)})')
    print(f'forbidden signatures : {len(forbidden_signatures)}')
    print(f'AVAILABLE for SFT    : {len(available_for_sft)} ({s["pct_pool_available_for_sft"]}% of pool)')
    print(f'wrote: {args.out}')
    print(f'wrote: {args.md}')

if __name__ == '__main__':
    main()
