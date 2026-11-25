#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""baize_posttrain_isolation_prereg_analysis.py
Pre-registration analysis for the secI open decision point:
  STRICT isolation   = drop any pair whose emitted text references ANY forbidden
                        (eval-used) API, even as a generic setup helper.
  RELAXED isolation  = only the TARGET API must be held-out (available_for_sft);
                        eval-used APIs are allowed as generic setup helpers
                        (e.g. emyInitAether / dbNewCV) in the doctest.

secI (wake754) shipped STRICT and emitted 664 pairs (77.1% dropped because the
doctest reference doc uses a forbidden API as a setup helper). This script does
NOT change that decision; it quantifies the trade-off so the formal-SFT
pre-registration (secJ) can be written with numbers, not guesses.

Zero GPU / zero ckpt. Does not touch protocol/task/check.py/timeout/-p.
"""
import argparse, json, os, re
from collections import Counter

_WORD = re.compile(r'\b([A-Za-z_][A-Za-z0-9_]*)\b')


def parse_doctest_block(desc):
    out, in_block = [], False
    for ln in (desc or '').splitlines():
        m = re.match(r'^\s*>>>\s?(.*)$', ln)
        if m:
            in_block = True
            out.append(m.group(1))
            continue
        if in_block:
            c = re.match(r'^\s*\.\.\.\s?(.*)$', ln)
            if c:
                out.append(c.group(1))
                continue
            s = ln.strip()
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--audit', default='sft_contamination_isolation_audit.json')
    ap.add_argument('--apiinfo',
                    default='/nas_data/app.e0031982/code/eda_fastmcp/docs/API_INFO_MERGED_V3.json')
    ap.add_argument('--out', default='isolation_prereg_analysis.json')
    args = ap.parse_args()

    audit = json.load(open(args.audit, 'r', encoding='utf-8'))
    available = set(audit['available_for_sft_apis'])
    forbidden = set()
    for item in audit.get('forbidden_api_frequency', []):
        if isinstance(item, dict) and item.get('api'):
            forbidden.add(item['api'])
        elif isinstance(item, str):
            forbidden.add(item)
    forb_n_tasks = {}
    for item in audit.get('forbidden_api_frequency', []):
        if isinstance(item, dict) and item.get('api'):
            forb_n_tasks[item['api']] = item.get('n_tasks', 0)

    apiinfo = json.load(open(args.apiinfo, 'r', encoding='utf-8'))
    heldout = sorted([a for a in available if a in apiinfo
                      and apiinfo[a].get('api_descriptions')])

    strict_pass = 0
    relaxed_pass = 0
    relaxed_only = 0
    helper_freq = Counter()
    helper_n_tasks = {}
    helper_arg_profiles = {}
    cat_strict = Counter()
    cat_relaxed_only = Counter()

    for api in heldout:
        desc = apiinfo[api].get('api_descriptions') or ''
        cat = apiinfo[api].get('category') or 'Unknown'
        code_lines = parse_doctest_block(desc)
        if not code_lines:
            continue
        code = '\n'.join(code_lines)
        words = set(_WORD.findall(code))
        forb_hits = sorted(words & forbidden)
        if not forb_hits:
            strict_pass += 1
            cat_strict[cat] += 1
        relaxed_pass += 1
        if forb_hits:
            relaxed_only += 1
            cat_relaxed_only[cat] += 1
        for fa in forb_hits:
            helper_freq[fa] += 1
            helper_n_tasks[fa] = forb_n_tasks.get(fa, 0)
            tag = 'generic'
            for ln in code_lines:
                if re.search(r'\b' + re.escape(fa) + r'\s*\(', ln):
                    inside = ln.split(fa + '(', 1)[-1]
                    depth, nargs, buf = 0, 0, ''
                    for ch in inside:
                        if ch == '(':
                            depth += 1
                        elif ch == ')':
                            if depth == 0:
                                break
                            depth -= 1
                        elif ch == ',' and depth == 0:
                            nargs += 1
                        elif depth == 0:
                            buf += ch
                    if nargs > 1 or len(buf.strip()) > 12:
                        tag = 'rich'
                    break
            helper_arg_profiles.setdefault(fa, [])
            if tag not in helper_arg_profiles[fa]:
                helper_arg_profiles[fa].append(tag)

    risk_grade = {}
    for fa, cnt in helper_freq.items():
        nt = helper_n_tasks.get(fa, 0)
        rich = 'rich' in helper_arg_profiles.get(fa, [])
        if nt >= 10 and rich:
            risk_grade[fa] = 'HIGH'
        elif nt >= 10 or rich:
            risk_grade[fa] = 'MEDIUM'
        else:
            risk_grade[fa] = 'LOW'

    result = {
        'meta': {
            'purpose': 'Pre-registration trade-off analysis for STRICT vs RELAXED '
                        'isolation (secI open decision). Zero GPU.',
            'red_line': 'Does not change secI STRICT 664-pair shipment. Numbers only, '
                         'to inform the formal-SFT pre-registration (secJ).',
            'strict_definition': 'target API held-out AND no forbidden API anywhere in '
                                 'emitted text (setup helper or otherwise)',
            'relaxed_definition': 'only the TARGET API must be held-out; eval-used APIs '
                                  'allowed as generic setup helpers from reference docs',
        },
        'summary': {
            'n_heldout_with_doctest': strict_pass + relaxed_only,
            'strict_pass': strict_pass,
            'relaxed_pass': relaxed_pass,
            'relaxed_only_extra': relaxed_only,
            'strict_drop_rate_pct': round(100.0 * relaxed_only / max(strict_pass + relaxed_only, 1), 1),
            'relaxed_yield_multiplier_vs_strict': round(relaxed_pass / max(strict_pass, 1), 2),
        },
        'helper_analysis': {
            'n_distinct_forbidden_apis_used_as_helpers': len(helper_freq),
            'top_helpers': [
                {'api': fa, 'n_relaxed_pairs': cnt,
                 'n_eval_tasks_using': helper_n_tasks.get(fa, 0),
                 'arg_shapes': helper_arg_profiles.get(fa, []),
                 'risk_grade': risk_grade.get(fa, 'LOW')}
                for fa, cnt in helper_freq.most_common()
            ],
        },
        'risk_grade_counts': dict(Counter(risk_grade.values())),
        'category_strict_pass_top': dict(cat_strict.most_common(12)),
        'category_relaxed_only_extra_top': dict(cat_relaxed_only.most_common(12)),
        'prereg_recommendation': (
            'If relaxed is chosen, gate must still (a) keep target API held-out, '
            '(b) reject any pair whose doctest reproduces a forbidden *signature* '
            '(def-name + args) verbatim (eval-task entry point), (c) cap helper usage '
            'to generic-init APIs (risk_grade LOW/MEDIUM) and exclude HIGH. The '
            'secH4 signature gate is retained in BOTH modes. Decision is '
            'pre-registered BEFORE any SFT run; not changed afterwards.'
        ),
        'baseline_unchanged': 'A0=43.29%+-3.92% / A1=4.56%+-1.70% / delta=-38.73pp',
    }
    json.dump(result, open(args.out, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)
    print('=== secJ pre-reg isolation trade-off analysis ===')
    for k, v in result['summary'].items():
        print('  %s: %s' % (k, v))
    print('  distinct forbidden helpers:', len(helper_freq))
    print('  risk grades:', dict(Counter(risk_grade.values())))
    print('  ->', args.out)


if __name__ == '__main__':
    main()
