#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B5 per-task profiler for the baseline-nailed user令 (2026-11-20 21:1x).

Produces baseline_<arm>_run<N>_pertask.json (required deliverable E.2).
For each of the 158 EDA-Eval-PyAether tasks records:
  - pass_count / pass_rate (from final_report.json details_per_task)
  - fail_mode FIVE-class (from THIS arm's own data, NOT DeepSeek r83 dist; §B.5)
  - four metrics (§B.5): agent_loop_entry / tool_call_count / error_rate / rag_queried

DATA SOURCE (authoritative, v2 -- fixes v1 interleaving bug):
  The four metrics are read from the per-worker cline SESSION files, NOT from the
  global interleaved codegen.log. With `-p 8` parallel workers the codegen.log is
  interleaved, so v1's "current segment" attribution mis-assigned tool calls
  (724 real tool calls in the log were under-counted to 13). Each cline invocation
  = one task = one session dir under <eval-dir>/cli_data/worker_*/data/sessions/<sid>/:
    <sid>.json          -> cwd (basename = task id), model, exit_code, status, token usage
    <sid>.messages.json -> messages[] with clean tool_use / tool_result blocks per task
  This gives exact per-task tool attribution with no interleaving ambiguity.

  Pass/fail + generation/execution status still come from final_report.json
  (--report). If --report is absent (run in progress) tasks are marked 'pending'
  but the four metrics are still computed from sessions, so the tooling can be
  smoke-tested before the run finishes.

fail_mode five-class (PASS reported separately):
  F1_no_code     : no .py file (gen_fail / no tool engagement)
  F2_tool_format : tool schema rejections exhausted budget -> no code
  F3_timeout     : generation timed out
  F4_api_misuse  : code emitted but TypeError/AttributeError (wrong API/type)
  F5_logic_error : code emitted & executed but assertion/wrong result
"""
import json, os, re, sys, glob, collections, argparse

TASK_RE = re.compile(r'(EDA-Eval-PyAether-\d+)')


def normalize_tool(name):
    return (name or '').replace('pyAether_MCP_server__', '').replace('eda_flow__', '')


def _result_text(block):
    cont = block.get('content')
    parts = []
    if isinstance(cont, list):
        for x in cont:
            if isinstance(x, dict):
                parts.append(str(x.get('text', '')))
                parts.append(str(x.get('value', '')))
            else:
                parts.append(str(x))
    elif isinstance(cont, str):
        parts.append(cont)
    elif cont is not None:
        parts.append(str(cont))
    return '\n'.join(parts)


def reject_reason(text):
    L = text.lower()
    if 'received string' in L and 'expected array' in L: return 'string-not-array'
    if 'expected boolean' in L and ('received string' in L or 'received undefined' in L or 'received null' in L): return 'wrong-type-boolean'
    if 'received undefined' in L or 'received null' in L: return 'missing-required-field'
    if 'unavailable tool' in L: return 'unavailable-tool'
    if 'invalid_type' in L or 'type validation failed' in L: return 'other-type-error'
    if 'rejected before execution' in L or 'was rejected' in L: return 'rejected-other'
    return 'other'


def is_rejected(text):
    L = text.lower()
    return ('rejected before execution' in L or 'was rejected' in L
            or 'type validation failed' in L or 'invalid_type' in L)


def collect_session(sid_dir):
    sid = os.path.basename(sid_dir.rstrip('/'))
    meta_path = os.path.join(sid_dir, sid + '.json')
    msgs_path = os.path.join(sid_dir, sid + '.messages.json')
    if not os.path.exists(meta_path):
        return None
    try:
        with open(meta_path) as f:
            meta = json.load(f)
    except (OSError, ValueError):
        return None
    cwd = meta.get('cwd', '') or ''
    base = os.path.basename(cwd.rstrip('/'))
    m = TASK_RE.search(base)
    if not m:
        return None
    task_id = m.group(1)
    usage = (meta.get('metadata') or {}).get('usage') or {}
    rec = {
        'task_id': task_id, 'session_id': sid, 'model': meta.get('model'),
        'exit_code': meta.get('exit_code'), 'status': meta.get('status'),
        'started_at': meta.get('started_at'), 'ended_at': meta.get('ended_at'),
        'input_tokens': usage.get('inputTokens'), 'output_tokens': usage.get('outputTokens'),
        'cwd': cwd,
    }
    tc = collections.Counter(); rej = 0; rr = collections.Counter()
    submit = rcode = search = editor = run_commands = 0
    n_msgs = 0
    if os.path.exists(msgs_path):
        try:
            with open(msgs_path) as f:
                md = json.load(f)
            msgs = md.get('messages', []) if isinstance(md, dict) else (md if isinstance(md, list) else [])
        except (OSError, ValueError):
            msgs = []
        for msg in msgs:
            if not isinstance(msg, dict):
                continue
            n_msgs += 1
            cont = msg.get('content')
            if not isinstance(cont, list):
                continue
            for b in cont:
                if not isinstance(b, dict):
                    continue
                bt = b.get('type')
                if bt == 'tool_use':
                    nm = normalize_tool(b.get('name', ''))
                    tc[nm] += 1
                    if nm == 'submit_and_exit': submit += 1
                    elif nm == 'run_code': rcode += 1
                    elif nm == 'editor': editor += 1
                    elif nm == 'run_commands': run_commands += 1
                    elif nm in ('search_apis', 'search_apis_by_keyword', 'get_api_details'): search += 1
                elif bt == 'tool_result':
                    txt = _result_text(b)
                    if is_rejected(txt):
                        rej += 1
                        rr[reject_reason(txt)] += 1
    total = sum(tc.values())
    rec.update({
        'tool_calls': dict(tc), 'total_tool_calls': total,
        'submit_calls': submit, 'run_code_calls': rcode, 'editor_calls': editor,
        'run_commands_calls': run_commands, 'search_calls': search,
        'total_rejections': rej, 'reject_reasons': dict(rr),
        'n_messages': n_msgs,
        'agent_loop_entry': bool(search > 0 and (rcode > 0 or editor > 0 or submit > 0)),
        'tool_call_count': total,
        'error_rate': round(rej / total, 4) if total else 0.0,
        'rag_queried': bool(search > 0),
    })
    return rec


def classify_fail(d, p):
    gs = (d.get('generation_statuses') or [None])[0]
    ets = d.get('error_types', [])
    if gs == 'timeout':
        return 'F3_timeout'
    if gs != 'success':
        if p is not None and p.get('total_tool_calls', 0) > 0 and p.get('submit_calls', 0) == 0 and p.get('total_rejections', 0) >= 3:
            return 'F2_tool_format'
        return 'F1_no_code'
    if 'TypeError' in ets or 'AttributeError' in ets:
        return 'F4_api_misuse'
    return 'F5_logic_error'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--eval-dir', required=True,
                    help='eval run dir containing cli_data/worker_*/data/sessions/')
    ap.add_argument('--report', default='', help='final_report.json (pass/fail source); absent => pending mode')
    ap.add_argument('--arm', default='A0_base')
    ap.add_argument('--run', default='1')
    ap.add_argument('--out', default='')
    args = ap.parse_args()
    if not args.out:
        args.out = 'baseline_%s_run%s_pertask.json' % (args.arm, args.run)

    sess_glob = os.path.join(args.eval_dir, 'cli_data', 'worker_*', 'data', 'sessions', '*')
    per_task = {}; n_sessions = 0; n_task_sessions = 0
    models = collections.Counter(); statuses = collections.Counter()
    for sid_dir in sorted(glob.glob(sess_glob)):
        if not os.path.isdir(sid_dir):
            continue
        n_sessions += 1
        rec = collect_session(sid_dir)
        if rec is None:
            continue
        n_task_sessions += 1
        models[rec.get('model') or 'unknown'] += 1
        statuses[rec.get('status') or 'unknown'] += 1
        tid = rec['task_id']
        if tid in per_task:
            old = per_task[tid]
            if old.get('status') == 'completed' and rec.get('status') != 'completed':
                continue
        per_task[tid] = rec

    agg_tool = collections.Counter(); agg_rej = collections.Counter()
    for p in per_task.values():
        for t, c in (p.get('tool_calls') or {}).items(): agg_tool[t] += c
        for r, c in (p.get('reject_reasons') or {}).items(): agg_rej[r] += c

    have_report = bool(args.report); report = {}
    if have_report:
        try:
            with open(args.report) as f: report = json.load(f)
        except (OSError, ValueError) as e:
            print('WARN: could not read report %r: %s' % (args.report, e), file=sys.stderr)
            have_report = False

    fail_mode = collections.Counter(); pass_dist = collections.Counter()
    n_pass = n_fail = n_pending = 0; report_model = None
    if have_report:
        report_model = report.get('model_name')
        details = report.get('details_per_task', {})
        for tid, d in details.items():
            p = per_task.get(tid); pc = d.get('num_correct', 0); pass_dist[pc] += 1
            if pc > 0:
                outcome = 'pass'; n_pass += 1; fm = None
            else:
                outcome = 'fail'; n_fail += 1; fm = classify_fail(d, p); fail_mode[fm] += 1
            if p is not None:
                p.update({'outcome': outcome, 'pass_count': pc, 'pass_rate': d.get('pass_rate'),
                          'fail_mode': fm,
                          'generation_status': (d.get('generation_statuses') or [None])[0],
                          'execution_status': (d.get('execution_statuses') or [None])[0],
                          'error_types': d.get('error_types', [])})
            else:
                per_task[tid] = {'task_id': tid, 'outcome': outcome, 'pass_count': pc,
                    'pass_rate': d.get('pass_rate'), 'fail_mode': fm,
                    'agent_loop_entry': False, 'tool_call_count': 0,
                    'error_rate': 0.0, 'rag_queried': False, 'note': 'no session found'}
        metrics = report.get('metrics', {})
        overall = metrics.get('pass_rate', report.get('pass_rate', report.get('pass@1')))
        n_rep = len(details)
    else:
        for tid, p in per_task.items():
            p['outcome'] = 'pending'; p['fail_mode'] = None; n_pending += 1
        pass_dist = {}; overall = None; n_rep = 0

    seg = list(per_task.values())
    def mean(key):
        vals = []
        for p in seg:
            v = p.get(key)
            if isinstance(v, bool): vals.append(int(v))
            elif isinstance(v, (int, float)): vals.append(v)
        return round(sum(vals) / len(vals), 4) if vals else None

    identity = {
        'session_models_seen': dict(models),
        'report_model_name': report_model,
        'n_sessions_total': n_sessions,
        'n_task_sessions': n_task_sessions,
        'session_statuses': dict(statuses),
        'model_consistent': (len(models) <= 1) and (report_model is None or
                            (models and report_model in models)),
    }

    out = {'arm': args.arm, 'run': args.run, 'eval_dir': args.eval_dir,
        'report_path': args.report if have_report else None, 'report_present': have_report,
        'source': 'baseline-nailed §B.5 per-task profile v2 (per-session, MiniCPM5 own data)',
        'n_tasks_in_sessions': len(per_task), 'n_tasks_in_report': n_rep,
        'n_pass': n_pass, 'n_fail': n_fail, 'n_pending': n_pending, 'overall_pass1': overall,
        'identity_crosscheck': identity,
        'pass_count_distribution': {str(k): v for k, v in sorted(pass_dist.items())},
        'fail_mode_five_class': dict(fail_mode.most_common()),
        'four_metric_means_over_tasks': {'agent_loop_entry_rate': mean('agent_loop_entry'),
            'tool_call_count_mean': mean('tool_call_count'),
            'error_rate_mean': mean('error_rate'),
            'rag_queried_rate': mean('rag_queried')},
        'aggregate_tool_calls': dict(agg_tool.most_common()),
        'aggregate_reject_reasons': dict(agg_rej.most_common()), 'per_task': per_task,
        'fail_mode_legend': {'F1_no_code': 'no .py file (gen_fail / no tool engagement)',
            'F2_tool_format': 'tool schema rejections exhausted budget -> no code',
            'F3_timeout': 'generation timed out',
            'F4_api_misuse': 'code emitted but TypeError/AttributeError (wrong API/type)',
            'F5_logic_error': 'code emitted & executed but assertion/wrong result'}}
    with open(args.out, 'w') as f: json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != 'per_task'}, ensure_ascii=False, indent=1))
    print('WROTE', args.out, file=sys.stderr)


if __name__ == '__main__':
    main()
