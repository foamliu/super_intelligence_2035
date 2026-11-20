#!/usr/bin/env python3
"""
Extract S1.readback_binary (B) 5-run cost metrics from existing traces (zero GPU).

For each of the 5 fresh batches (2026-10-15~16) that produced the
(B) 5-run Pass@1 = [120,125,123,124,125]/158 = [75.9,79.1,77.8,78.5,79.1]%,
parse ~/eda_code_eval/<batch>/trace/<task>/ for:

  - Mean read-backs   = mean `pyAether_MCP_server__run_code` tool calls per task
  - Code-gen wall-clock per task (sec) = ended_at - started_at (from session .json)
  - timeout count     = stats/timeout file (per batch)
  - Converged (%)     = fraction of tasks with session status == 'completed'
  - gen-fail count    = tasks that did not produce executable code (from final_report
                        generation_statistics.failure)
  - input/output tokens (sum/mean) from session .json metadata.usage

Then aggregate 5-run mean +/- sample std for each metric.

Batches (gen_batch -> regrade dir):
  r1: 2026_1015_093317
  r2: 2026_1015_143848
  r3: 2026_1015_193004
  r4: 2026_1015_233638
  r5: 2026_1016_041955

Run:
  python3 extract_readback_binary_cost_5run.py
"""
import json, os, sys, statistics
from datetime import datetime

EVAL_ROOT = os.path.expanduser('~/eda_code_eval')
OUT_EVAL  = '/nasdata/app.e0031982/code/EDA-Eval-Framework/output_evaluation'

BATCHES = [
    ('r1', '2026_1015_093317'),
    ('r2', '2026_1015_143848'),
    ('r3', '2026_1015_193004'),
    ('r4', '2026_1015_233638'),
    ('r5', '2026_1016_041955'),
]

RUN_CODE_TOOL = 'pyAether_MCP_server__run_code'

def iso_to_dt(s):
    # 2026-10-15T01:33:32.881Z
    if not s: return None
    s = s.replace('Z', '+00:00')
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None

def parse_batch(batch):
    bdir = os.path.join(EVAL_ROOT, batch)
    tdir = os.path.join(bdir, 'trace')
    if not os.path.isdir(tdir):
        return {'error': f'no trace dir {tdir}'}
    tasks = sorted(os.listdir(tdir))
    n_tasks = len(tasks)
    run_code_counts = []
    wall_secs = []
    statuses = Counter = {}
    statuses = {}
    in_tok = []
    out_tok = []
    all_started = []
    all_ended = []
    missing_msg = 0
    missing_sess = 0
    for t in tasks:
        tdir_t = os.path.join(tdir, t)
        # messages.json (could be api_conversation_history.json or *.messages.json)
        msg_file = os.path.join(tdir_t, 'api_conversation_history.json')
        if not os.path.exists(msg_file):
            # try *.messages.json
            cands = [f for f in os.listdir(tdir_t) if f.endswith('.messages.json')]
            if cands:
                msg_file = os.path.join(tdir_t, cands[0])
            else:
                missing_msg += 1
                continue
        try:
            m = json.load(open(msg_file))
        except Exception:
            missing_msg += 1
            continue
        # count run_code tool_use
        rc = 0
        for x in m.get('messages', []):
            if x.get('role') == 'assistant':
                c = x.get('content')
                if isinstance(c, list):
                    for blk in c:
                        if isinstance(blk, dict) and blk.get('type') == 'tool_use' and \
                           blk.get('name') == RUN_CODE_TOOL:
                            rc += 1
        run_code_counts.append(rc)
        # session .json (small) for status + started/ended + usage
        sess_cands = [f for f in os.listdir(tdir_t) if f.endswith('.json') and not f.endswith('.messages.json')]
        sess = None
        for sf in sess_cands:
            try:
                d = json.load(open(os.path.join(tdir_t, sf)))
                if 'started_at' in d and 'ended_at' in d:
                    sess = d
                    break
            except Exception:
                pass
        if sess is None:
            missing_sess += 1
        else:
            statuses[sess.get('status', 'unknown')] = statuses.get(sess.get('status', 'unknown'), 0) + 1
            s0 = iso_to_dt(sess.get('started_at'))
            s1 = iso_to_dt(sess.get('ended_at'))
            if s0:
                all_started.append(s0)
            if s1:
                all_ended.append(s1)
            if s0 and s1:
                wall_secs.append((s1 - s0).total_seconds())
            u = (sess.get('metadata') or {}).get('usage') or {}
            if u.get('inputTokens') is not None:
                in_tok.append(u['inputTokens'])
            if u.get('outputTokens') is not None:
                out_tok.append(u['outputTokens'])
    # stats/timeout, success, failure
    def read_int(name):
        p = os.path.join(bdir, 'stats', name)
        try:
            return int(open(p).read().strip())
        except Exception:
            return None
    timeout_n = read_int('timeout')
    success_n = read_int('success')
    failure_n = read_int('failure')
    # gen stats from final_report.json (regrade dir matches gen batch)
    # regrade dirs are named YYYYMMDD_HHMM_app.e0031982 ; gen batch is YYYY_MMDD_HHMMSS
    gen_fail = None
    gen_success = None
    gen_timeout = None
    # convert batch 2026_1015_093317 -> 20261015 marker + look for generations_file match
    batch_compact = batch.replace('_', '')[:8]  # 20261015
    for d in os.listdir(OUT_EVAL):
        if not d.startswith(batch_compact):
            continue
        fr = os.path.join(OUT_EVAL, d, 'final_report.json')
        if not os.path.exists(fr):
            continue
        try:
            rj = json.load(open(fr))
        except Exception:
            continue
        gf = rj.get('generations_file', '')
        if batch in gf:
            gs = (rj.get('summary') or {}).get('generation_statistics') or {}
            gen_success = gs.get('success')
            gen_fail = gs.get('failure')
            gen_timeout = gs.get('timeout')
            break
    converged = statuses.get('completed', 0)
    n_status = sum(statuses.values())
    batch_elapsed_sec = None
    batch_elapsed_hour = None
    if all_started and all_ended:
        batch_elapsed_sec = (max(all_ended) - min(all_started)).total_seconds()
        batch_elapsed_hour = batch_elapsed_sec / 3600.0
    return {
        'batch': batch,
        'n_tasks_with_trace': n_tasks,
        'n_with_messages': n_tasks - missing_msg,
        'n_with_session': n_status,
        'run_code_total': sum(run_code_counts),
        'run_code_mean': statistics.mean(run_code_counts) if run_code_counts else None,
        'run_code_median': statistics.median(run_code_counts) if run_code_counts else None,
        'run_code_per_task': run_code_counts,
        'wall_mean_sec': statistics.mean(wall_secs) if wall_secs else None,
        'wall_median_sec': statistics.median(wall_secs) if wall_secs else None,
        'wall_total_sec': sum(wall_secs),
        'wall_mean_min': (statistics.mean(wall_secs)/60.0) if wall_secs else None,
        'batch_elapsed_sec': batch_elapsed_sec,
        'batch_elapsed_hour': batch_elapsed_hour,
        'timeout_stats_file': timeout_n,
        'success_stats_file': success_n,
        'failure_stats_file': failure_n,
        'gen_success': gen_success,
        'gen_fail': gen_fail,
        'gen_timeout': gen_timeout,
        'converged_completed': converged,
        'converged_pct': (100.0*converged/n_status) if n_status else None,
        'statuses': statuses,
        'input_tokens_total': sum(in_tok) if in_tok else None,
        'input_tokens_mean': statistics.mean(in_tok) if in_tok else None,
        'output_tokens_total': sum(out_tok) if out_tok else None,
        'output_tokens_mean': statistics.mean(out_tok) if out_tok else None,
    }

def mean_std(vals):
    if not vals or any(v is None for v in vals):
        present = [v for v in vals if v is not None]
        if not present:
            return None, None
        vals = present
    m = statistics.mean(vals)
    s = statistics.stdev(vals) if len(vals) >= 2 else 0.0
    return m, s

def main():
    results = []
    print('='*88)
    print('S1.readback_binary (B) 5-run cost extraction from existing traces')
    print('='*88)
    for run, batch in BATCHES:
        r = parse_batch(batch)
        r['run'] = run
        results.append(r)
        print(f"\n--- {run} | batch {batch} ---")
        if 'error' in r:
            print('  ERROR:', r['error']); continue
        print(f"  tasks w/ trace: {r['n_tasks_with_trace']}  (messages: {r['n_with_messages']}, session: {r['n_with_session']})")
        print(f"  run_code total: {r['run_code_total']}  mean: {r['run_code_mean']:.2f}  median: {r['run_code_median']:.1f}")
        print(f"  wall-clock per task: mean={r['wall_mean_sec']:.1f}s ({r['wall_mean_min']:.2f}min)  median={r['wall_median_sec']:.1f}s  total={r['wall_total_sec']:.0f}s ({r['wall_total_sec']/3600:.2f}h)")
        print(f"  batch real-elapsed (parallel): {r['batch_elapsed_sec']:.0f}s = {r['batch_elapsed_hour']:.2f}h")
        print(f"  stats: timeout={r['timeout_stats_file']}  success={r['success_stats_file']}  failure={r['failure_stats_file']}")
        print(f"  gen: success={r['gen_success']}  fail={r['gen_fail']}  timeout={r['gen_timeout']}")
        print(f"  Converged: completed={r['converged_completed']}/{r['n_with_session']} = {r['converged_pct']:.1f}%")
        print(f"  statuses: {r['statuses']}")
        print(f"  tokens: input_mean={r['input_tokens_mean']:.0f}  output_mean={r['output_tokens_mean']:.0f}" if r['input_tokens_mean'] else "  tokens: n/a")

    print('\n' + '='*88)
    print('5-run aggregation (mean +/- sample std)')
    print('='*88)
    pass_counts = [120, 125, 123, 124, 125]
    pass_pcts = [100.0*c/158 for c in pass_counts]
    pm, ps = mean_std(pass_pcts)
    print(f"  Pass@1:   {[f'{p:.1f}%' for p in pass_pcts]}  ->  {pm:.1f} +/- {ps:.1f}%  (correct {[120,125,123,124,125]})")
    rc_means = [r['run_code_mean'] for r in results if r.get('run_code_mean') is not None]
    m, s = mean_std(rc_means)
    print(f"  Mean read-backs (run_code per task): {[f'{v:.2f}' for v in rc_means]}  ->  {m:.2f} +/- {s:.2f}")
    wall_means = [r['wall_mean_sec'] for r in results if r.get('wall_mean_sec') is not None]
    m, s = mean_std(wall_means)
    print(f"  Wall-clock per task (sec): {[f'{v:.1f}' for v in wall_means]}  ->  {m:.1f} +/- {s:.1f}s  ({m/60:.2f}min)")
    # wall-clock in hours (sum of per-task = batch gen wall, but parallel; report mean per task)
    timeouts = [r['timeout_stats_file'] for r in results if r.get('timeout_stats_file') is not None]
    m, s = mean_std([float(t) for t in timeouts])
    print(f"  Timeout count: {timeouts}  ->  {m:.1f} +/- {s:.1f}")
    gen_fails = [r['gen_fail'] for r in results if r.get('gen_fail') is not None]
    if gen_fails:
        m, s = mean_std([float(t) for t in gen_fails])
        print(f"  Gen-fail count: {gen_fails}  ->  {m:.1f} +/- {s:.1f}")
    else:
        print(f"  Gen-fail count: not extracted from final_report (manual: r1=1 failure, r2-r5=0 from stats/failure)")
    convs = [r['converged_pct'] for r in results if r.get('converged_pct') is not None]
    m, s = mean_std(convs)
    print(f"  Converged (%): {[f'{v:.1f}' for v in convs]}  ->  {m:.1f} +/- {s:.1f}%")
    batch_hours = [r['batch_elapsed_hour'] for r in results if r.get('batch_elapsed_hour') is not None]
    m, s = mean_std(batch_hours)
    print(f"  Batch real-elapsed (h, parallel): {[f'{v:.2f}' for v in batch_hours]}  ->  {m:.2f} +/- {s:.2f}h")
    in_tok = [r['input_tokens_mean'] for r in results if r.get('input_tokens_mean') is not None]
    m, s = mean_std(in_tok)
    print(f"  Input tokens mean: {[f'{v:.0f}' for v in in_tok]}  ->  {m:.0f} +/- {s:.0f}")
    out_tok = [r['output_tokens_mean'] for r in results if r.get('output_tokens_mean') is not None]
    m, s = mean_std(out_tok)
    print(f"  Output tokens mean: {[f'{v:.0f}' for v in out_tok]}  ->  {m:.0f} +/- {s:.0f}")

    # save json
    out_path = '/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run/readback_binary_cost_5run.json'
    with open(out_path, 'w') as f:
        # drop the per-task list to keep file small
        for r in results:
            r.pop('run_code_per_task', None)
        json.dump({'batches': results, 'pass_counts': pass_counts,
                   'pass_pcts': pass_pcts}, f, indent=2, default=str)
    print(f"\nSaved JSON: {out_path}")

if __name__ == '__main__':
    main()
