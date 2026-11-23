#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""baize_posttrain_heldout_sft_synthesizer.py
Held-out (contamination-isolated) SFT corpus synthesizer for the corrected SFT
that fixes the secF root cause (A1 SFT corpus = static single-turn doc->code,
0% agentic trajectories -> covered the base healthy loop and caused catastrophic
degradation A0 43.29% -> A1 4.56%, McNemar chi2=68.01 p=0.0).

This step (secI) builds the foundation of the corrected SFT corpus, zero GPU:
  1. load available_for_sft_apis (3930) from secH contamination-isolation audit;
  2. load API_INFO_MERGED_V3.json reference docs (8463 APIs, doctest examples);
  3. intersect -> held-out APIs that have rich reference docs;
  4. for each, synthesize TWO artifacts:
       (a) held-out task definition (prompt skeleton + entry_point) -- the
           non-eval task pool that secG6.1 will run base+cline on to harvest
           real agentic trajectories (待 pretrain ckpt / or base 预演);
       (b) doc->code SFT pair from the doctest example, form-aligned to the
           secG3 healthy agentic template (search -> get_api_details -> editor
           -> run_code -> submit_and_exit, single submit) so the SFT model
           learns the healthy loop instead of collapsing to F1_no_code.
  5. secH4 re-check gate: forbidden_api_set intersection training == empty and
     no forbidden signature leak; any hit -> drop pair + log.

Red line sec5.1: only API reference docs are used to synthesize training pairs;
the 158 eval tasks' prompt/signature/assertion never enter training. This script
does NOT touch protocol/task/check.py/timeout/-p and uses zero GPU.
"""
import argparse, json, os, re, sys
from collections import Counter

_DEF_RE = re.compile(r'def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)')
_DOCTEST_LINE = re.compile(r'^\s*>>>\s?(.*)$')
_CONT_LINE = re.compile(r'^\s*\.\.\.\s?(.*)$')
_SIG_RE = re.compile(r'`([A-Za-z_][A-Za-z0-9_]*)\s*\(([^`]*)\)`')
def first_sentence(desc):
    if not desc:
        return ''
    for line in desc.splitlines():
        s = line.strip().strip('`').strip()
        if s and not s.startswith('#') and not s.startswith('`'):
            return s.rstrip('.') + '.'
    return ''


def parse_doctest_block(desc):
    """Return list of code lines (joined) from the first >>> example block."""
    if not desc:
        return []
    lines = desc.splitlines()
    out, in_block = [], False
    for ln in lines:
        m = _DOCTEST_LINE.match(ln)
        if m:
            in_block = True
            out.append(m.group(1))
            continue
        if in_block:
            c = _CONT_LINE.match(ln)
            if c:
                out.append(c.group(1))
                continue
            stripped = ln.strip()
            if stripped == '' or stripped.startswith('#'):
                break
            break
    return out


def extract_signature(desc, api):
    if not desc:
        return 'pyScript.%s(...)' % api
    m = _SIG_RE.search(desc)
    if m:
        return 'pyScript.%s(%s)' % (m.group(1), m.group(2))
    m2 = re.search(r'\*\*`' + re.escape(api) + r'\(([^)]*)\)`\*\*', desc)
    if m2:
        return 'pyScript.%s(%s)' % (api, m2.group(1))
    return 'pyScript.%s(...)' % api


def build_agentic_skeleton(api, sig, refdoc, code_lines):
    """secG3 healthy template: search -> get_api_details -> editor -> run_code
    -> submit_and_exit (single submit). doc->code pair is the editor/run_code content."""
    code = '\n'.join(code_lines)
    ref = (refdoc or '')[:1200]
    return [
        {"role": "assistant", "tool": "search_apis",
         "args": {"query": api}, "note": "retrieve the target API"},
        {"role": "tool_result", "content": "found api: %s" % api},
        {"role": "assistant", "tool": "get_api_details",
         "args": {"api_list": [api]}},
        {"role": "tool_result", "content": ref},
        {"role": "assistant", "tool": "editor", "content": code},
        {"role": "assistant", "tool": "run_code", "content": code},
        {"role": "assistant", "tool": "submit_and_exit",
         "note": "single clean submit (vs A1 +451% submit storm)"},
    ]


def contamination_check(helper_text, helper_forbidden_set, sig_text, forbidden_sigs):
    """secH4 gate (two-scope, matches secJ pre-reg analysis).
    - helper_text (doctest CODE only): scan for eval-used APIs that are STILL
      forbidden as helpers under the active mode (STRICT=all 111; TIERED=only the
      HIGH-risk excluded_helpers, e.g. dbNewCV/dbCreateLib). Code-only scope matches
      the secJ analysis (helper usage is about the code the model learns to produce).
    - sig_text (full emitted text): scan for forbidden def-signatures from the 158
      eval tasks (entry-point leakage). The signature gate is ALWAYS enforced in
      every mode (secH4 retained in ALL modes per sft_isolation_prereg_decision).
    The TARGET API is guaranteed held-out upstream (we only iterate over
    available_for_sft_apis)."""
    hits_api = sorted([a for a in helper_forbidden_set
                       if re.search(r'\b' + re.escape(a) + r'\b', helper_text or '')])
    hits_sig = []
    for (dn, al) in forbidden_sigs:
        if dn and re.search(r'\bdef\s+' + re.escape(dn) + r'\s*\(', sig_text or ''):
            hits_sig.append(dn)
    return hits_api, sorted(set(hits_sig))


def detect_eval_helpers(text, full_forbidden_set, helper_risk):
    """Transparency log: which eval-used APIs appear as helpers in this pair, and
    their pre-registered risk grade (LOW/MEDIUM/HIGH). Does NOT gate; used only to
    annotate each emitted pair and the manifest so the TIERED helper allowance is
    auditable per pair."""
    seen = {}
    for a in full_forbidden_set:
        if re.search(r'\b' + re.escape(a) + r'\b', text or ''):
            seen[a] = helper_risk.get(a, 'UNKNOWN')
    return seen


def load_helper_risk(analysis_path):
    """Load {api: risk_grade} from isolation_prereg_analysis.json helper_analysis.top_helpers."""
    risk = {}
    try:
        d = json.load(open(analysis_path, 'r', encoding='utf-8'))
        for h in d.get('helper_analysis', {}).get('top_helpers', []):
            if isinstance(h, dict) and h.get('api'):
                risk[h['api']] = h.get('risk_grade', 'UNKNOWN')
    except Exception:
        pass
    return risk


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--audit', default='sft_contamination_isolation_audit.json',
                    help='secH audit json (provides available_for_sft_apis + forbidden sets)')
    ap.add_argument('--apiinfo', default='/nas_data/app.e0031982/code/eda_fastmcp/docs/API_INFO_MERGED_V3.json')
    ap.add_argument('--out', default='heldout_sft_corpus_synthesized.jsonl',
                    help='output jsonl (default STRICT wake754 historical file; for a fresh '
                         'code-only-scope strict run, pass --out heldout_sft_corpus_strict.jsonl)')
    ap.add_argument('--manifest', default='heldout_sft_corpus_manifest.json')
    ap.add_argument('--limit', type=int, default=100000, help='max pairs to emit')
    ap.add_argument('--full-stats', action='store_true', help='also scan full pool for doctest stats')
    ap.add_argument('--mode', choices=['strict', 'tiered'], default='strict',
                    help='isolation mode. strict=STRICT (no forbidden API anywhere as helper, '
                         'wake754 664-pair shipment). tiered=TIERED (secJ frozen pre-reg: allow '
                         'LOW/MED eval-used APIs as helpers, exclude HIGH-risk excluded_helpers '
                         '[dbNewCV,dbCreateLib]; secH4 signature gate retained).')
    ap.add_argument('--prereg-decision', default='sft_isolation_prereg_decision.json',
                    help='secJ frozen pre-reg decision json (provides excluded_helpers for tiered)')
    ap.add_argument('--prereg-analysis', default='isolation_prereg_analysis.json',
                    help='secJ analysis json (provides helper risk grades for transparency)')
    args = ap.parse_args()

    if args.mode == 'tiered':
        if not args.out.endswith('_tiered.jsonl') and args.out == 'heldout_sft_corpus_synthesized.jsonl':
            args.out = 'heldout_sft_corpus_tiered.jsonl'
        if args.manifest == 'heldout_sft_corpus_manifest.json':
            args.manifest = 'heldout_sft_corpus_tiered_manifest.json'

    audit = json.load(open(args.audit, 'r', encoding='utf-8'))
    available = set(audit['available_for_sft_apis'])
    full_forbidden_api_set = set()
    for item in audit.get('forbidden_api_frequency', []):
        if isinstance(item, dict) and item.get('api'):
            full_forbidden_api_set.add(item['api'])
        elif isinstance(item, str):
            full_forbidden_api_set.add(item)
    forbidden_sigs = []
    for t in audit.get('per_task', []):
        for s in t.get('signatures', []):
            forbidden_sigs.append((s.get('def', ''), s.get('args', '')))

    # Build the helper-forbidden set per isolation mode.
    excluded_helpers = []
    if args.mode == 'tiered':
        dec = json.load(open(args.prereg_decision, 'r', encoding='utf-8'))
        excluded_helpers = sorted(dec.get('rule', {}).get('excluded_helpers', []))
        helper_forbidden_set = set(excluded_helpers)  # only HIGH-risk excluded helpers forbidden
    else:
        helper_forbidden_set = set(full_forbidden_api_set)  # STRICT: all eval-used APIs forbidden as helpers
    helper_risk = load_helper_risk(args.prereg_analysis) if args.mode == 'tiered' else {}

    apiinfo = json.load(open(args.apiinfo, 'r', encoding='utf-8'))
    heldout_apis = sorted([a for a in available if a in apiinfo and apiinfo[a].get('api_descriptions')])

    cat_counter = Counter()
    type_counter = Counter()
    has_doctest = 0
    emitted = []
    dropped_gate = 0
    dropped_by_helper_api = 0
    dropped_by_sig = 0
    pairs_with_allowed_helper = 0
    helper_use_counter = Counter()

    for api in heldout_apis:
        info = apiinfo[api]
        cat = info.get('category') or 'Unknown'
        cat_counter[cat] += 1
        type_counter[info.get('api_type') or 'Unknown'] += 1
        desc = info.get('api_descriptions') or ''
        code_lines = parse_doctest_block(desc)
        if not code_lines:
            continue
        has_doctest += 1
        sig = extract_signature(desc, api)
        oneliner = first_sentence(desc)
        instruction = ('Write a pyAether script using the API `%s` (%s). '
                       'Signature: %s. Follow the healthy loop: search the API, '
                       'fetch its details, write the code, run it, then submit once.'
                       % (api, oneliner, sig))
        skeleton = build_agentic_skeleton(api, sig, desc, code_lines)
        code_text = '\n'.join(code_lines)
        full_text = instruction + '\n' + code_text + '\n' + sig
        hits_api, hits_sig = contamination_check(code_text, helper_forbidden_set, full_text, forbidden_sigs)
        if hits_api or hits_sig:
            dropped_gate += 1
            if hits_api:
                dropped_by_helper_api += 1
            if hits_sig:
                dropped_by_sig += 1
            continue
        # transparency: which eval-used APIs appear as helpers (allowed under TIERED)
        eval_helpers = detect_eval_helpers(code_text, full_forbidden_api_set, helper_risk) if args.mode == 'tiered' else {}
        if eval_helpers:
            pairs_with_allowed_helper += 1
            for h in eval_helpers:
                helper_use_counter[h] += 1
        rec = {
            'id': 'sft_heldout_%s' % api,
            'api': api,
            'category': cat,
            'api_type': info.get('api_type'),
            'available_for_sft': True,
            'instruction': instruction,
            'signature': sig,
            'one_line_desc': oneliner,
            'doctest_code': '\n'.join(code_lines),
            'agentic_trajectory_skeleton': skeleton,
            'reference_doc_excerpt': desc[:1600],
            'contamination_gate': {
                'mode': args.mode,
                'excluded_helpers': excluded_helpers,
                'forbidden_api_hit': [], 'forbidden_sig_hit': [], 'pass': True,
                'allowed_eval_helpers': eval_helpers,
            },
        }
        emitted.append(rec)
        if len(emitted) >= args.limit:
            break

    with open(args.out, 'w', encoding='utf-8') as f:
        for r in emitted:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

    n_heldout_with_doctest = has_doctest
    if args.full_stats:
        n_heldout_with_doctest = sum(
            1 for a in heldout_apis
            if parse_doctest_block(apiinfo[a].get('api_descriptions') or ''))

    manifest = {
        'meta': {
            'purpose': 'Held-out (contamination-isolated) SFT corpus synthesizer (secI/secJ). '
                        'Fixes secF root cause: corrected SFT corpus must contain agentic-form '
                        'trajectories, not only static single-turn doc->code.',
            'mode': args.mode,
            'mode_rule': ('STRICT: no eval-used API anywhere as helper (wake754 664-pair shipment).'
                          if args.mode == 'strict' else
                          'TIERED (secJ frozen pre-reg): target API held-out; LOW/MED eval-used APIs '
                          'allowed as helpers; HIGH-risk excluded_helpers %s forbidden; secH4 signature '
                          'gate retained in ALL modes.' % (excluded_helpers or [])),
            'red_line': 'Only API reference docs used; 158 eval prompt/signature/assertion '
                         'never enter training (sec5.1). secH4 re-check gate enforced.',
            'audit_source': os.path.abspath(args.audit),
            'apiinfo_source': os.path.abspath(args.apiinfo),
            'prereg_decision': (os.path.abspath(args.prereg_decision) if args.mode == 'tiered' else None),
            'zero_gpu': True,
            'no_protocol_change': True,
        },
        'summary': {
            'mode': args.mode,
            'n_available_for_sft_apis': len(available),
            'n_forbidden_apis': len(full_forbidden_api_set),
            'n_forbidden_signatures': len(forbidden_sigs),
            'n_heldout_apis_with_refdoc': len(heldout_apis),
            'n_heldout_apis_with_doctest': n_heldout_with_doctest,
            'n_emitted_pairs': len(emitted),
            'n_dropped_by_gate': dropped_gate,
            'n_dropped_by_helper_api': dropped_by_helper_api,
            'n_dropped_by_sig': dropped_by_sig,
            'n_pairs_with_allowed_helper': pairs_with_allowed_helper,
            'emit_limit': args.limit,
        },
        'category_distribution': dict(cat_counter.most_common()),
        'api_type_distribution': dict(type_counter.most_common()),
        'tiered_helper_usage': (dict(helper_use_counter.most_common()) if args.mode == 'tiered' else {}),
        'form_alignment': {
            'template': 'search_apis -> get_api_details -> editor -> run_code -> submit_and_exit',
            'submit_count_per_pair': 1,
            'rationale': 'secG3 healthy template (A0 pass_all 25 trajectories): submit mean=1.00 '
                         'vs A1 +451% storm; search_apis 7.32 vs A1 -82%; retrieval-before-code 96%.',
            'note': 'Skeleton pairs here are doc->code SFT positives; real agentic trajectories '
                    'on these held-out tasks are harvested later (secG6.1, base+cline, pretrain ckpt).',
        },
        'contamination_gate': {
            'rule': ('STRICT: forbidden_api_set intersection emitted_text == empty'
                     if args.mode == 'strict' else
                     'TIERED: excluded_helpers intersection emitted_text == empty AND no forbidden def-signature'),
            'excluded_helpers': excluded_helpers,
            'signature_gate_retained': True,
            'n_dropped': dropped_gate,
            'n_dropped_by_helper_api': dropped_by_helper_api,
            'n_dropped_by_sig': dropped_by_sig,
            'status': 'PASS' if dropped_gate == 0 else 'SOME_DROPPED',
        },
        'baseline_unchanged': 'A0=43.29%+-3.92% / A1=4.56%+-1.70% / delta=-38.73pp',
        'outputs': [os.path.abspath(args.out)],
    }
    json.dump(manifest, open(args.manifest, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    print('=== secI held-out SFT synthesizer ===')
    for k, v in manifest['summary'].items():
        print('  %s: %s' % (k, v))
    print('  gate status:', manifest['contamination_gate']['status'])
    print('  emitted ->', args.out)
    print('  manifest ->', args.manifest)


if __name__ == '__main__':
    main()

