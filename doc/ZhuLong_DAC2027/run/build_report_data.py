#!/usr/bin/env python3
"""build_report_data.py — Join per-task pass with trace analysis for the A0/A1/A2 report.

Outputs: report_data.json with per-task pass arrays, adoption correlation, context stats.
"""
import json, os, sys
from collections import Counter, defaultdict
from pathlib import Path

RUN_DIR = Path("/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run")
EVAL_BASE = Path("/nasdata/app.e0031982/code/EDA-Eval-Framework/output_evaluation")

# Batch → eval dir mapping
BATCH_MAP = {
    'A0_r1': {'eval_dir': '20261113_0214_app.e0031982', 'batch': '2026_1112_224239'},
    'A0_r2': {'eval_dir': '20261113_0828_app.e0031982', 'batch': '2026_1113_063819'},
    'A0_r3': {'eval_dir': '20261113_1030_app.e0031982', 'batch': '2026_1113_082842'},
    'A1_r1': {'eval_dir': '20261114_1529_app.e0031982', 'batch': '2026_1114_130945'},
    'A1_r2': {'eval_dir': '20261114_1800_app.e0031982', 'batch': '2026_1114_152932'},
    'A1_r3': {'eval_dir': '20261114_2008_app.e0031982', 'batch': '2026_1114_180019'},
    'A2_r1': {'eval_dir': '20261114_2343_app.e0031982', 'batch': '2026_1114_210739'},
    'A2_r2': {'eval_dir': '20261115_0218_app.e0031982', 'batch': '2026_1114_234310'},
    'A2_r3': {'eval_dir': '20261115_0506_app.e0031982', 'batch': '2026_1115_021900'},
}

SUBSET_40 = set(open(RUN_DIR / 'compaction_subset_40.txt').read().strip().split('\n'))

def load_per_task_pass(eval_dir):
    """Load per-task pass from final_report.json, return {task_name: pass(0/1)}."""
    fr = json.load(open(EVAL_BASE / eval_dir / 'final_report.json'))
    dpt = fr.get('details_per_task', {})
    result = {}
    for task, info in dpt.items():
        if task in SUBSET_40:
            # pass = 1 if num_correct > 0
            result[task] = 1 if info.get('num_correct', 0) > 0 else 0
    return result

def load_trace_analysis():
    return json.load(open(RUN_DIR / 'subagent_trace_analysis.json'))

def mcnemar(per_a, per_b):
    """Compute McNemar test. per_a/per_b are {task: pass(0/1)}."""
    b = sum(1 for t in per_a if per_a[t] == 1 and per_b.get(t, 0) == 0)  # A pass, B fail
    c = sum(1 for t in per_a if per_a[t] == 0 and per_b.get(t, 0) == 1)  # A fail, B pass
    n = b + c
    if n == 0:
        return b, c, n, 1.0, 'no_discordants'
    # With continuity correction
    chi2 = (abs(b - c) - 1) ** 2 / n if n > 0 else 0
    # p-value from chi2 distribution (1 df) — use simple approximation
    from math import exp, sqrt, pi
    # Normal approximation of McNemar (sign test)
    # p = 2 * sum(k=0..min(b,c)) C(n,k) * 0.5^n
    # For large n, use normal approx
    if n >= 20:
        z = (abs(b - c) - 1) / sqrt(n)
        # Two-tailed p from normal
        p = 2 * (1 - 0.5 * (1 + __import__('math').erf(z / sqrt(2))))
    else:
        # Exact binomial
        from math import comb
        p = 2 * sum(comb(n, k) * (0.5 ** n) for k in range(min(b, c) + 1))
        p = min(p, 1.0)
    return b, c, n, p, f"{'A>B' if b > c else 'B>A' if c > b else 'tie'}"

def main():
    # 1. Load per-task pass for all arms/rounds
    per_task = {}  # {arm_round: {task: pass}}
    for key, info in BATCH_MAP.items():
        per_task[key] = load_per_task_pass(info['eval_dir'])
        print(f"{key}: {len(per_task[key])} tasks, {sum(per_task[key].values())} pass", file=sys.stderr)

    # 2. Load trace analysis
    trace = load_trace_analysis()

    # 3. Build per-task arrays for each arm (3 rounds × 40 tasks = 120 obs)
    # For McNemar per-round (120 obs)
    def per_round_array(arm):
        """Return list of (task, round, pass) for all 120 obs."""
        arr = []
        for r in [1, 2, 3]:
            pt = per_task[f'{arm}_r{r}']
            for task, p in pt.items():
                arr.append((task, r, p))
        return arr

    # 4. Majority vote (pass if >=2/3 rounds pass)
    def majority_vote(arm):
        votes = {}
        for task in SUBSET_40:
            passes = sum(per_task[f'{arm}_r{r}'].get(task, 0) for r in [1, 2, 3])
            votes[task] = 1 if passes >= 2 else 0
        return votes

    mv = {arm: majority_vote(arm) for arm in ['A0', 'A1', 'A2']}
    for arm in ['A0', 'A1', 'A2']:
        print(f"{arm} majority: {sum(mv[arm].values())}/40 = {sum(mv[arm].values())/40*100:.1f}%", file=sys.stderr)

    # 5. McNemar tests
    mc_results = {}
    # Majority vote
    for (a, b) in [('A0', 'A1'), ('A0', 'A2'), ('A1', 'A2')]:
        b_val, c_val, n, p, direction = mcnemar(mv[a], mv[b])
        mc_results[f'{a}_vs_{b}_majority'] = {'b': b_val, 'c': c_val, 'n': n, 'p': p, 'direction': direction}

    # Per-round (120 obs)
    for (a, b) in [('A0', 'A1'), ('A0', 'A2'), ('A1', 'A2')]:
        pa = {f'{t}_{r}': p for t, r, p in per_round_array(a)}
        pb = {f'{t}_{r}': p for t, r, p in per_round_array(b)}
        b_val, c_val, n, p, direction = mcnemar(pa, pb)
        mc_results[f'{a}_vs_{b}_perround'] = {'b': b_val, 'c': c_val, 'n': n, 'p': p, 'direction': direction}

    # 6. A2 Adoption correlation analysis
    # For each A2 task-round: verdict + adopted + pass
    a2_adopt_data = []
    for r in [1, 2, 3]:
        batch = BATCH_MAP[f'A2_r{r}']['batch']
        pt = per_task[f'A2_r{r}']
        # Get trace data for this batch
        a2_per_task = trace.get('A2_per_task', {})
        for task in SUBSET_40:
            pass_val = pt.get(task, 0)
            # Find trace data
            trace_entry = None
            for tkey, rounds_data in a2_per_task.items():
                if tkey == task:
                    for rd in rounds_data:
                        if rd.get('batch') == batch:
                            trace_entry = rd
                            break
            if trace_entry:
                a2_adopt_data.append({
                    'task': task,
                    'round': r,
                    'pass': pass_val,
                    'verdict': trace_entry['verdict'],
                    'adopted': trace_entry['adopted'],
                    'edits_after': trace_entry['edits_after'],
                    'n_spawn': trace_entry['n_spawn'],
                    'main_n_msgs': trace_entry['main_n_msgs'],
                    'main_peak_ctx': trace_entry['main_peak_ctx'],
                })
            else:
                a2_adopt_data.append({
                    'task': task, 'round': r, 'pass': pass_val,
                    'verdict': 'NO_TRACE', 'adopted': False,
                    'edits_after': 0, 'n_spawn': 0, 'main_n_msgs': 0, 'main_peak_ctx': 0,
                })

    # Aggregate adoption → pass
    adopt_pass = defaultdict(lambda: {'n': 0, 'pass': 0})
    for d in a2_adopt_data:
        key = f"verdict={d['verdict']}_adopted={d['adopted']}"
        adopt_pass[key]['n'] += 1
        adopt_pass[key]['pass'] += d['pass']

    # Simplified: verdict → pass rate
    verdict_pass = defaultdict(lambda: {'n': 0, 'pass': 0})
    for d in a2_adopt_data:
        verdict_pass[d['verdict']]['n'] += 1
        verdict_pass[d['verdict']]['pass'] += d['pass']

    # FAIL adopted vs FAIL not adopted
    fail_adopted = {'n': 0, 'pass': 0}
    fail_not_adopted = {'n': 0, 'pass': 0}
    for d in a2_adopt_data:
        if d['verdict'] == 'FAIL':
            if d['adopted']:
                fail_adopted['n'] += 1
                fail_adopted['pass'] += d['pass']
            else:
                fail_not_adopted['n'] += 1
                fail_not_adopted['pass'] += d['pass']

    # 7. Context dimension analysis
    # A0 peak context from compaction results
    a0_ctx = []
    comp = json.load(open(RUN_DIR / 'ablation_compaction_results.json'))
    for rnd in comp['rounds']:
        if 'basic' in rnd['summary']['tag']:
            for t in rnd.get('tasks', []):
                a0_ctx.append({
                    'task': t['task'],
                    'prompt_tokens': t.get('prompt_tokens', 0),
                    'n_msgs': t.get('n_assistant_msgs', 0),
                    'wall_sec': t.get('wall_sec', 0),
                })

    # A1/A2 peak context from trace analysis
    a1_ctx_by_round = {}
    for batch, rd in trace.get('A1', {}).get('per_round', {}).items():
        a1_ctx_by_round[batch] = {
            'mean_peak_ctx': rd.get('mean_peak_ctx', 0),
            'mean_n_msgs': rd.get('mean_n_msgs', 0),
        }
    a2_ctx_by_round = {}
    for batch, rd in trace.get('A2', {}).get('per_round', {}).items():
        a2_ctx_by_round[batch] = {
            'mean_peak_ctx': rd.get('mean_peak_ctx', 0),
            'mean_n_msgs': rd.get('mean_n_msgs', 0),
        }

    # 8. Spawn distribution for A2 (Q1: spawn count distribution)
    spawn_dist = Counter()
    for d in a2_adopt_data:
        n = d['n_spawn']
        if n == 0:
            spawn_dist['0_spawn'] += 1
        elif n == 1:
            spawn_dist['1_spawn'] += 1
        else:
            spawn_dist[f'{n}_spawn'] += 1

    # 9. Per-task wall_sec and n_msgs distribution (throughput analysis)
    # From cost files
    cost_summary = {}
    for arm in ['A1', 'A2']:
        cost_summary[arm] = {}
        for r in [1, 2, 3]:
            cf = json.load(open(RUN_DIR / f'cost_S_{arm}_r{r}.json'))
            pms = cf.get('per_main_session', [])
            cost_summary[arm][f'r{r}'] = {
                'wall_sec': cf.get('wall_sec', 0),
                'cline_success': cf.get('cline_success', 0),
                'cline_failed': cf.get('cline_failed', 0),
                'timed_out': cf.get('timed_out', 0),
                'completion_rate': cf.get('completion_rate_pct', 0),
                'spawn_calls': cf.get('spawn_calls_total', 0),
                'sub_executed': cf.get('subagent_executed', 0),
                'sub_sessions': cf.get('subagent_sessions_total', 0),
                'sub_mcp_rejected': cf.get('subagent_mcp_rejected_count', 0),
                'tokens_main': cf.get('tokens_main', {}).get('total', 0),
                'tokens_sub': cf.get('tokens_sub', {}).get('total', 0),
                'n_msgs_per_task': [pm.get('n_msgs', 0) for pm in pms],
                'main_in_tok_per_task': [pm.get('main_in_tok', 0) for pm in pms],
            }

    # 10. A0 cost summary
    a0_cost = {}
    for i, tag in enumerate(['C_basic_r1', 'C_basic_r2', 'C_basic_r3']):
        rnd = comp['rounds'][{'C_basic_r1': 0, 'C_basic_r2': 3, 'C_basic_r3': 4}[tag]]
        s = rnd['summary']
        tasks = rnd.get('tasks', [])
        a0_cost[tag] = {
            'pass_rate': s.get('pass_rate_pct', 0),
            'n_tasks': s.get('n_tasks', 40),
            'mean_wall_sec': s.get('wall_sec_per_task_mean', 0),
            'total_tokens': s.get('total_tokens', 0),
            'mean_prompt_tokens': s.get('prompt_tokens_per_task_mean', 0),
            'mean_n_msgs': sum(t.get('n_assistant_msgs', 0) for t in tasks) / len(tasks) if tasks else 0,
            'wall_secs': [t.get('wall_sec', 0) for t in tasks],
            'prompt_tokens': [t.get('prompt_tokens', 0) for t in tasks],
            'n_msgs': [t.get('n_assistant_msgs', 0) for t in tasks],
        }

    # Output
    output = {
        'analysis': 'ZhuLong subagent A0/A1/A2 report data',
        'date': '2026-11-15',
        'per_task_pass': {k: v for k, v in per_task.items()},
        'majority_vote': mv,
        'mcnemar': mc_results,
        'a2_adoption': {
            'verdict_pass': {k: {'n': v['n'], 'pass': v['pass'], 'rate': v['pass']/v['n'] if v['n'] else 0} for k, v in verdict_pass.items()},
            'adopt_pass': {k: {'n': v['n'], 'pass': v['pass'], 'rate': v['pass']/v['n'] if v['n'] else 0} for k, v in adopt_pass.items()},
            'fail_adopted': {'n': fail_adopted['n'], 'pass': fail_adopted['pass'], 'rate': fail_adopted['pass']/fail_adopted['n'] if fail_adopted['n'] else 0},
            'fail_not_adopted': {'n': fail_not_adopted['n'], 'pass': fail_not_adopted['pass'], 'rate': fail_not_adopted['pass']/fail_not_adopted['n'] if fail_not_adopted['n'] else 0},
            'spawn_dist': dict(spawn_dist),
            'per_task': a2_adopt_data,
        },
        'context': {
            'A0': a0_cost,
            'A1': a1_ctx_by_round,
            'A2': a2_ctx_by_round,
        },
        'cost': cost_summary,
        'trace': {
            'A1_verdicts': trace.get('A1', {}),
            'A2_verdicts': trace.get('A2', {}).get('verdict_counts', {}),
            'A2_adopted_counts': trace.get('A2', {}).get('adopted_counts', {}),
        },
    }

    out_file = RUN_DIR / 'report_data.json'
    json.dump(output, open(out_file, 'w'), ensure_ascii=False, indent=2)
    print(f"\nSaved: {out_file}", file=sys.stderr)

    # Print key findings
    print("\n=== KEY FINDINGS ===", file=sys.stderr)
    print(f"McNemar A0vsA2 majority: {mc_results['A0_vs_A2_majority']}", file=sys.stderr)
    print(f"McNemar A0vsA2 per-round: {mc_results['A0_vs_A2_perround']}", file=sys.stderr)
    print(f"\nA2 verdict → pass rate:", file=sys.stderr)
    for k, v in verdict_pass.items():
        print(f"  {k}: {v['pass']}/{v['n']} = {v['pass']/v['n']*100:.1f}%", file=sys.stderr)
    print(f"\nA2 FAIL adopted: {fail_adopted['pass']}/{fail_adopted['n']} = {fail_adopted['pass']/fail_adopted['n']*100:.1f}%" if fail_adopted['n'] else "no data", file=sys.stderr)
    print(f"A2 FAIL not adopted: {fail_not_adopted['pass']}/{fail_not_adopted['n']} = {fail_not_adopted['pass']/fail_not_adopted['n']*100:.1f}%" if fail_not_adopted['n'] else "no data", file=sys.stderr)
    print(f"\nA2 spawn dist: {dict(spawn_dist)}", file=sys.stderr)


if __name__ == '__main__':
    main()
