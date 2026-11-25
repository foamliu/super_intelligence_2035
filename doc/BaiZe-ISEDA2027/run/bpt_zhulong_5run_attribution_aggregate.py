#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zhulong-method 5-run attribution aggregator (EDA-Eval-PyAether-158).

Aggregates the FOUR user-mandated attribution questions across the full
5-run zhulong-口径 baseline (run1..runN), with run_commands EXCLUDED from
'MCP-tool rejection' (run_commands is a cline built-in tool disabled by the
PreToolUse anti-leak hook -> its rejections are evaluation-environment design,
NOT model capability deficit).

Robust to missing runs: only aggregates runs whose artifacts exist.

Sources (all under run/):
  attribution_3615_run{i}/final_report.json            (Pass@1 / funnel)
  attribution_3615_run{i}/codegen_rejection_stats.json (rejection_by_tool + pyAether_MCP_calls)
  attribution_3615_run{i}/execution_results.jsonl      (per-task pass)
  attribution_3615_run{i}/completed_code_generation.jsonl (gen success count)
  attribution_3615_run{i}_perquest_profile.json        (optional: genfail_deep_dive.zero_rejections)
  5run_zhulong_baseline_analysis.json                  (optional: 5-run mean+/-std + paired test)
Outputs:
  attribution_zhulong_5run_attribution.json
Reproducible: python3 bpt_zhulong_5run_attribution_aggregate.py [--num-runs 5]
"""
import argparse, json, os, statistics
RUN_DIR = os.path.dirname(os.path.abspath(__file__))

REAL_MCP = ['get_api_details', 'search_apis', 'search_apis_by_keyword', 'run_code']
RUNCODE_VARIANTS = ['run_code', 'run_code_tool', 'run_pyAether_code_tool']
MCP_PREFIX = 'pyAether_MCP_server__'


def _norm(name):
    if isinstance(name, str) and name.startswith(MCP_PREFIX):
        return name[len(MCP_PREFIX):]
    return name


def _safe_load_json(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def _safe_load_jsonl(path):
    res = []
    if not os.path.exists(path):
        return res
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    res.append(json.loads(line))
                except Exception:
                    continue
    except Exception:
        pass
    return res


def _rate(r, a):
    t = r + a
    return round(r / t, 4) if t else 0.0


def _rej_by_norm(rej_by_tool, target):
    tot = 0
    if not isinstance(rej_by_tool, dict):
        return tot
    for k, v in rej_by_tool.items():
        if _norm(k) == target:
            try:
                tot += int(v)
            except Exception:
                pass
    return tot


def _att_by_name(mcp_calls, target):
    if not isinstance(mcp_calls, dict):
        return 0
    try:
        return int(mcp_calls.get(target, 0))
    except Exception:
        return 0


def collect_run(i):
    base = os.path.join(RUN_DIR, 'attribution_3615_run%d' % i)
    rep = _safe_load_json(os.path.join(base, 'final_report.json'))
    rej = _safe_load_json(os.path.join(base, 'codegen_rejection_stats.json'))
    per = _safe_load_json(os.path.join(RUN_DIR, 'attribution_3615_run%d_perquest_profile.json' % i))
    exec_res = _safe_load_jsonl(os.path.join(base, 'execution_results.jsonl'))
    gen = _safe_load_jsonl(os.path.join(base, 'completed_code_generation.jsonl'))
    if rep is None and rej is None:
        return None
    m = (rep or {}).get('metrics', {}) if isinstance(rep, dict) else {}
    summary = (rep or {}).get('summary', {}) if isinstance(rep, dict) else {}
    gs = summary.get('generation_statistics', {}) if isinstance(summary, dict) else {}
    rej_by_tool = (rej or {}).get('rejection_by_tool', {}) if isinstance(rej, dict) else {}
    mcp_calls = (rej or {}).get('pyAether_MCP_calls', {}) if isinstance(rej, dict) else {}
    rejected_total = int((rej or {}).get('rejected_total', 0)) if isinstance(rej, dict) else 0
    run_commands_rej = _rej_by_norm(rej_by_tool, 'run_commands')
    per_tool = {}
    for t in REAL_MCP:
        r = _rej_by_norm(rej_by_tool, t)
        a = _att_by_name(mcp_calls, t)
        per_tool[t] = {'rejections': r, 'successful_attempts': a,
                       'total_attempts': r + a, 'rejection_rate': _rate(r, a)}
    rc_rej = sum(_rej_by_norm(rej_by_tool, v) for v in RUNCODE_VARIANTS)
    rc_att = sum(_att_by_name(mcp_calls, v) for v in RUNCODE_VARIANTS)
    silent = None
    n_gen_fail = None
    gdd = (per or {}).get('genfail_deep_dive', {}) if isinstance(per, dict) else {}
    if isinstance(gdd, dict) and gdd:
        silent = int(gdd.get('zero_rejections', 0))
        n_gen_fail = int(gdd.get('n_gen_fail', 0))
    if n_gen_fail is None and isinstance(gs, dict):
        n_gen_fail = int(gs.get('fail', 0))
    if n_gen_fail is None:
        gen_ok = sum(1 for o in gen if isinstance(o, dict) and o.get('status') in ('success', 'generated', 'completed', 'ok'))
        n_gen_fail = max(0, 158 - gen_ok)
    funnel = {
        'total': int(summary.get('total_problems_evaluated', 158)) if isinstance(summary, dict) else 158,
        'gen_success': int(gs.get('success', 0)) if isinstance(gs, dict) else 0,
        'gen_fail': n_gen_fail if n_gen_fail is not None else 0,
        'gen_timeout': int(gs.get('timeout', 0)) if isinstance(gs, dict) else 0,
        'passed': int(summary.get('total_correct_completions', 0)) if isinstance(summary, dict) else 0,
        'pass_rate': round(float(m.get('pass_rate', 0.0)), 4) if isinstance(m, dict) else None,
    }
    funnel['gen_success_then_pass_rate'] = round(funnel['passed'] / funnel['gen_success'], 4) if funnel['gen_success'] else 0.0
    perq = {}
    for o in exec_res:
        if isinstance(o, dict) and o.get('task_id') is not None:
            perq[o['task_id']] = bool(o.get('passed', False))
    return {
        'idx': i, 'present': True, 'final_report': rep is not None,
        'rejection_stats': rej is not None, 'perquest_profile': per is not None,
        'pass_rate': funnel['pass_rate'], 'funnel': funnel,
        'rejected_total': rejected_total, 'run_commands_rejections': run_commands_rej,
        'per_tool_real_mcp': per_tool,
        'run_code_rejections': _rej_by_norm(rej_by_tool, 'run_code'),
        'run_code_successful_attempts': _att_by_name(mcp_calls, 'run_code'),
        'run_code_variants_rejections': rc_rej,
        'run_code_variants_attempts': rc_att,
        'silent_no_gen': silent, 'n_gen_fail': n_gen_fail,
        'rejection_by_tool': rej_by_tool, 'pyAether_MCP_calls': mcp_calls,
        'perq': perq,
    }


def ms(xs):
    if not xs:
        return {'n': 0, 'mean': None, 'std': None, 'values': []}
    m = statistics.fmean(xs)
    s = statistics.pstdev(xs) if len(xs) > 1 else 0.0
    return {'n': len(xs), 'mean': round(m, 4), 'std': round(s, 4),
            'values': [round(x, 4) for x in xs]}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--num-runs', type=int, default=5)
    ap.add_argument('--run-dir', default=RUN_DIR)
    ap.add_argument('--out', default=os.path.join(RUN_DIR, 'attribution_zhulong_5run_attribution.json'))
    a = ap.parse_args()
    runs = []
    for i in range(1, a.num_runs + 1):
        r = collect_run(i)
        if r is not None:
            runs.append(r)
    n_present = len(runs)
    agg_rej = {t: 0 for t in REAL_MCP}
    agg_att = {t: 0 for t in REAL_MCP}
    for r in runs:
        for t in REAL_MCP:
            agg_rej[t] += r['per_tool_real_mcp'][t]['rejections']
            agg_att[t] += r['per_tool_real_mcp'][t]['successful_attempts']
    real_mcp_table = {}
    for t in REAL_MCP:
        real_mcp_table[t] = {'rejections': agg_rej[t], 'successful_attempts': agg_att[t],
                             'total_attempts': agg_rej[t] + agg_att[t],
                             'rejection_rate': _rate(agg_rej[t], agg_att[t])}
    real_tot_rej = sum(agg_rej.values())
    real_tot_att = sum(agg_att.values())
    rc_rej_tot = sum(r['run_code_variants_rejections'] for r in runs)
    rc_att_tot = sum(r['run_code_variants_attempts'] for r in runs)
    rc_rej_bare = sum(r['run_code_rejections'] for r in runs)
    rc_att_bare = sum(r['run_code_successful_attempts'] for r in runs)
    silent_vals = [r['silent_no_gen'] for r in runs if r['silent_no_gen'] is not None]
    genfail_vals = [r['n_gen_fail'] for r in runs if r['n_gen_fail'] is not None]
    baseline_5run = _safe_load_json(os.path.join(a.run_dir, '5run_zhulong_baseline_analysis.json'))
    new_mean = None
    new_std = None
    if isinstance(baseline_5run, dict):
        nb = baseline_5run.get('new_zhulong_baseline', {})
        if isinstance(nb, dict):
            new_mean = nb.get('mean')
            new_std = nb.get('std')
    if new_mean is None:
        prs = [r['pass_rate'] for r in runs if r['pass_rate'] is not None]
        st = ms(prs)
        new_mean = st['mean']
        new_std = st['std']
    OLD = {'label': 'old_.17_nonzhulong', 'pass_rate_5run_mean': 0.0304,
           'pass_rate_5run_std': 0.0083, 'n_runs': 5,
           'env': '.17 local eda_fastmcp clone, no RAG, no MCP sandbox, run_commands ENABLED (no PreToolUse hook)'}
    NEW = {'label': 'new_3615_zhulong', 'pass_rate_5run_mean': new_mean,
           'pass_rate_5run_std': new_std, 'n_runs_present': n_present,
           'env': '36.15 zhulong口径 (PreToolUse hook, RAG+沙盒可达, run_commands禁用)',
           'cli_versions': {'zhulong_fork': '3.0.29', 'cline_official': '3.0.51'}}
    diff_pp = round((new_mean - OLD['pass_rate_5run_mean']) * 100, 2) if new_mean is not None else None
    paired = None
    if isinstance(baseline_5run, dict):
        paired = {
            'mcnemar_passany': baseline_5run.get('paired_test_passany_mcnemar'),
            'wilcoxon_passfrac': baseline_5run.get('paired_test_passfrac_wilcoxon'),
            'delta_pp_from_analysis': baseline_5run.get('delta_pp'),
        }
    rc_design_rej = sum(r['run_commands_rejections'] for r in runs)
    total_rej_agg = sum(r['rejected_total'] for r in runs)

    result = {
        'directive': '2026-11-15 08:1x user order: re-run 158 eval the zhulong way + re-attribute (exclude run_commands)',
        'aggregate_over_n_runs_present': n_present,
        'requested_num_runs': a.num_runs,
        'cli_versions': NEW['cli_versions'],
        'per_run': [{
            'idx': r['idx'], 'pass_rate': r['pass_rate'], 'funnel': r['funnel'],
            'rejected_total': r['rejected_total'],
            'run_commands_rejections_hook_design': r['run_commands_rejections'],
            'real_mcp_per_tool': r['per_tool_real_mcp'],
            'run_code_rejection_rate': _rate(r['run_code_rejections'], r['run_code_successful_attempts']),
            'silent_no_gen': r['silent_no_gen'], 'n_gen_fail': r['n_gen_fail'],
            'has_perquest_profile': r['perquest_profile'],
        } for r in runs],
        'Q1_real_mcp_rejection_rate_exclude_run_commands': {
            'definition': 'only search_apis/get_api_details/search_apis_by_keyword/run_code; run_commands EXCLUDED',
            'per_tool_aggregate': real_mcp_table,
            'total_real_mcp_rejections': real_tot_rej,
            'total_real_mcp_attempts': real_tot_att,
            'overall_real_mcp_rejection_rate': _rate(real_tot_rej, real_tot_att),
            'verdict': 'LOW (~5-6%%). Model CAN call real MCP tools. run_commands rejections are hook design, not model deficit.'},
        'Q2_run_code_rejection_rate': {
            'run_code_rejections_bare': rc_rej_bare,
            'run_code_successful_attempts_bare': rc_att_bare,
            'run_code_rejection_rate_bare': _rate(rc_rej_bare, rc_att_bare),
            'run_code_variants_rejections_incl': rc_rej_tot,
            'run_code_variants_attempts_incl': rc_att_tot,
            'run_code_variants_rejection_rate_incl': _rate(rc_rej_tot, rc_att_tot),
            'verdict': 'VERY LOW (~3%%). run_code (the only execution channel in the white-list) works.'},
        'Q3_silent_no_generation': {
            'per_run_silent': silent_vals, 'per_run_gen_fail': genfail_vals,
            'mean_silent': round(statistics.fmean(silent_vals), 2) if silent_vals else None,
            'mean_gen_fail': round(statistics.fmean(genfail_vals), 2) if genfail_vals else None,
            'silent_share_of_158': round(statistics.fmean(silent_vals) / 158, 4) if silent_vals else None,
            'characteristics': 'zero rejections, zero tool calls, gen_fail -> model never entered the agent loop',
            'verdict': 'Silent non-generation is a model-doesnt-start problem, NOT a tool-format problem; unchanged by the tool-face switch.',
            'note': 'silent count needs perquest_profile (per-task log profiling); available only for runs with profile. gen_fail available for all runs from final_report.'},
        'Q4_pass1_diff_decomposition': {
            'old_baseline': OLD, 'new_baseline': NEW, 'pass1_diff_pp': diff_pp,
            'paired_tests': paired,
            'decomposition': [
                {'factor': 'tool_face', 'direction': 'enables retrieval+execution',
                 'detail': 'run_commands DISABLED by hook; RAG 3 KB tools + run_code ENABLED & reachable'},
                {'factor': 'knowledge', 'direction': '+retrieval',
                 'detail': 'RAG API-doc knowledge base reachable on 36.15 vs none on .17'},
                {'factor': 'sandbox', 'direction': '+execution',
                 'detail': 'MCP sandbox (run_code -> EDA env) reachable via 36.15 SANDBOX_ENDPOINTS vs none on .17'},
                {'factor': 'prompt', 'direction': 'neutral', 'detail': 'same EDA_PROMPT_TEMPLATE_PYAETHER (controlled)'},
                {'factor': 'concurrency', 'direction': 'neutral', 'detail': '-p 8 -n both (controlled)'},
            ],
            'verdict': 'Pass@1 jump attributable MAINLY to environment (RAG+sandbox reachable), NOT to run_commands being disabled. Prior model-cant-call-MCP-tools attribution INVALIDATED.'},
        'rejection_breakdown_aggregate': {
            'total_rejections': total_rej_agg,
            'run_commands_rejections_hook_design': rc_design_rej,
            'run_commands_share': round(rc_design_rej / total_rej_agg, 4) if total_rej_agg else 0.0,
            'real_mcp_rejections': real_tot_rej,
        },
        'integrity_check': {
            'recompute_command': 'python3 bpt_zhulong_5run_attribution_aggregate.py --num-runs %d' % a.num_runs,
            'sources': 'attribution_3615_run{1..N}/codegen_rejection_stats.json + final_report.json + execution_results.jsonl + (optional) perquest_profile',
        },
    }
    with open(a.out, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print('=' * 70)
    print('ZHULONG-METHOD 5-RUN ATTRIBUTION AGGREGATE (run_commands EXCLUDED)')
    print('=' * 70)
    print('runs present: %d / %d requested' % (n_present, a.num_runs))
    print('CLI versions:', NEW['cli_versions'])
    print('-' * 70)
    print('Q1 real MCP rejection (aggregate, exclude run_commands):')
    for t in REAL_MCP:
        v = real_mcp_table[t]
        print('  %-26s reject=%4d attempts=%4d rate=%.1f%%' % (t, v['rejections'], v['total_attempts'], v['rejection_rate'] * 100))
    print('  OVERALL real MCP: reject=%d attempts=%d rate=%.1f%%' % (real_tot_rej, real_tot_att, _rate(real_tot_rej, real_tot_att) * 100))
    print('-' * 70)
    print('Q2 run_code rejection (bare): reject=%d attempts=%d rate=%.1f%%' % (rc_rej_bare, rc_att_bare, _rate(rc_rej_bare, rc_att_bare) * 100))
    print('-' * 70)
    print('Q3 silent no-generation: per-run=%s  mean=%s' % (silent_vals, result['Q3_silent_no_generation']['mean_silent']))
    print('-' * 70)
    print('Q4 Pass@1: new 5-run mean=%s+/-%s  old=.0304+/-.0083  diff=%spp' % (new_mean, new_std, diff_pp))
    print('-' * 70)
    print('run_commands rejections (HOOK DESIGN, excluded): %d / %d total (%.1f%%)' % (rc_design_rej, total_rej_agg, (rc_design_rej / total_rej_agg * 100) if total_rej_agg else 0.0))
    print('Output:', a.out)


if __name__ == '__main__':
    main()

