#!/usr/bin/env python3
"""R302: Analyze available cline trace data from 11-10 generation runs."""
import json, os, sys
from collections import Counter

EVAL_ROOT = os.path.expanduser('~/eda_code_eval')
RUN_DIRS = ['2026_1110_094456', '2026_1110_094902', '2026_1110_095714']

def load_trace(run_dir, task_id='EDA-Eval-PyAether-001'):
    p = os.path.join(EVAL_ROOT, run_dir, 'trace', task_id, 'api_conversation_history.json')
    if not os.path.exists(p): return None
    with open(p, 'r', encoding='utf-8') as f: return json.load(f)

def analyze_trace(trace, run_dir):
    if trace is None: return {'run_dir': run_dir, 'error': 'no trace file'}
    msgs = trace.get('messages', [])
    r = {'run_dir': run_dir, 'session_id': trace.get('sessionId',''), 'msg_count': len(msgs),
         'assistant_msgs': 0, 'tool_use_count': 0, 'tool_result_count': 0,
         'tool_names': Counter(), 'finish_reasons': Counter(),
         'generated_code_snippet': '', 'total_tokens_in': 0, 'total_tokens_out': 0}
    for m in msgs:
        role = m.get('role','')
        content = m.get('content','')
        if role == 'assistant':
            r['assistant_msgs'] += 1
            if isinstance(content, list):
                for b in content:
                    if isinstance(b, dict):
                        if b.get('type') == 'tool_use':
                            r['tool_use_count'] += 1
                            r['tool_names'][b.get('name','unknown')] += 1
                        elif b.get('type') == 'text':
                            t = b.get('text','')
                            if not r['generated_code_snippet'] and ('def ' in t or 'import ' in t):
                                r['generated_code_snippet'] = t[:800]
            elif isinstance(content, str):
                if 'tool_use' in content: r['tool_use_count'] += 1
                if not r['generated_code_snippet'] and ('def ' in content or 'import ' in content):
                    r['generated_code_snippet'] = content[:800]
        if role == 'tool':
            r['tool_result_count'] += 1
        stop = m.get('stop_reason', m.get('finish_reason',''))
        if stop: r['finish_reasons'][stop] += 1
        usage = m.get('usage',{})
        if usage:
            r['total_tokens_in'] += usage.get('input_tokens', usage.get('prompt_tokens',0))
            r['total_tokens_out'] += usage.get('output_tokens', usage.get('completion_tokens',0))
    return r

def main():
    print('=' * 70)
    print('R302: Trace Analysis of 11-10 Generation Runs (MiniCPM5-2B)')
    print('=' * 70)
    all_results = []
    for run_dir in RUN_DIRS:
        print('\n--- Run: {} ---'.format(run_dir))
        trace = load_trace(run_dir)
        a = analyze_trace(trace, run_dir)
        if 'error' in a:
            print('  ERROR: {}'.format(a['error']))
            all_results.append(a); continue
        print('  session_id: {}'.format(a['session_id']))
        print('  messages: {}'.format(a['msg_count']))
        print('  assistant_msgs: {}'.format(a['assistant_msgs']))
        print('  tool_use_count: {}'.format(a['tool_use_count']))
        print('  tool_result_count: {}'.format(a['tool_result_count']))
        print('  tool_names: {}'.format(dict(a['tool_names'])))
        print('  finish_reasons: {}'.format(dict(a['finish_reasons'])))
        print('  tokens_in: {}  tokens_out: {}'.format(a['total_tokens_in'], a['total_tokens_out']))
        if a['generated_code_snippet']:
            print('  generated_code (first 400 chars):')
            for line in a['generated_code_snippet'][:400].split('\n'):
                print('    {}'.format(line))
        all_results.append(a)
    print('\n' + '=' * 70)
    print('CROSS-RUN SUMMARY (3 runs, task 001 only)')
    print('=' * 70)
    valid = [r for r in all_results if 'error' not in r]
    if valid:
        avg_tool = sum(r['tool_use_count'] for r in valid) / len(valid)
        avg_msgs = sum(r['msg_count'] for r in valid) / len(valid)
        avg_iter = sum(r['assistant_msgs'] for r in valid) / len(valid)
        all_tn = Counter()
        for r in valid: all_tn.update(r['tool_names'])
        legal = sum(1 for r in valid if r['tool_use_count'] > 0 and r['tool_result_count'] > 0)
        print('  runs with trace: {}/3'.format(len(valid)))
        print('  avg messages: {:.1f}'.format(avg_msgs))
        print('  avg tool_use: {:.1f}'.format(avg_tool))
        print('  avg assistant turns (D6 proxy): {:.1f}'.format(avg_iter))
        print('  tool names: {}'.format(dict(all_tn)))
        print('  D1 proxy (legal format): {}/{} runs have paired tool_use+result'.format(legal, len(valid)))
        print('  D2 proxy (tool freq): avg {:.1f} calls/task'.format(avg_tool))
    else:
        print('  No valid traces found')
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'r302_trace_analysis.json')
    ser = []
    for r in all_results:
        sr = dict(r)
        if isinstance(sr.get('tool_names'), Counter): sr['tool_names'] = dict(sr['tool_names'])
        if isinstance(sr.get('finish_reasons'), Counter): sr['finish_reasons'] = dict(sr['finish_reasons'])
        ser.append(sr)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(ser, f, ensure_ascii=False, indent=2)
    print('\n  JSON saved: {}'.format(out))

if __name__ == '__main__':
    main()
