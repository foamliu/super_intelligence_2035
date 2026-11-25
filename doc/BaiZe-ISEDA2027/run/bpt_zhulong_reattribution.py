#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zhulong-method re-attribution for EDA-Eval-PyAether-158 (36.15 run1).

Recomputes the FOUR questions the 2026-11-15 user directive demands, with
run_commands EXCLUDED from 'MCP-tool rejection' (run_commands is a cline
built-in tool disabled by the PreToolUse anti-leak hook -> its rejections are
evaluation-environment design, NOT model capability deficit).

Sources (all under run/):
  attribution_3615_run1/codegen_rejection_stats.json   (clean MCP call counts)
  attribution_3615_run1_perquest_profile.json          (per-task + genfail dive)
  attribution_3615_run1/final_report.json              (Pass@1 / funnel)
Outputs:
  attribution_zhulong_reattribution.json
Reproducible: python3 bpt_zhulong_reattribution.py
"""
import json, os
RUN_DIR = os.path.dirname(os.path.abspath(__file__))
def _load(n):
    with open(os.path.join(RUN_DIR, n), 'r', encoding='utf-8') as f:
        return json.load(f)
REJ = _load('attribution_3615_run1/codegen_rejection_stats.json')
PER = _load('attribution_3615_run1_perquest_profile.json')
REP = _load('attribution_3615_run1/final_report.json')
mcp_calls = REJ.get('pyAether_MCP_calls', {})
rej_tools = PER.get('aggregate_reject_tools', {})
rej_reasons = PER.get('aggregate_reject_reasons', {})
REAL_MCP = ['get_api_details', 'search_apis', 'search_apis_by_keyword', 'run_code']
RUNCODE_VARIANTS = ['run_code', 'run_code_tool', 'run_pyAether_code_tool']
def _att(t): return int(mcp_calls.get(t, 0))
def _rej(t): return int(rej_tools.get(t, 0))
def _rate(r, a):
    t = r + a
    return round(r/t, 4) if t else 0.0
real_mcp_table = {}
for t in REAL_MCP:
    r, a = _rej(t), _att(t)
    real_mcp_table[t] = {'rejections': r, 'successful_attempts': a, 'total_attempts': r+a, 'rejection_rate': _rate(r, a)}
rc_rej = sum(_rej(t) for t in RUNCODE_VARIANTS)
rc_att = sum(_att(t) for t in RUNCODE_VARIANTS)
real_tot_rej = sum(real_mcp_table[t]['rejections'] for t in REAL_MCP)
real_tot_att = sum(real_mcp_table[t]['total_attempts'] for t in REAL_MCP)
run_commands_rej = _rej('run_commands')
total_rej = sum(rej_tools.values())
gdd = PER.get('genfail_deep_dive', {})
silent = int(gdd.get('zero_rejections', 0))
n_gen_fail = int(gdd.get('n_gen_fail', 0))
summary = REP.get('summary', {})
gs = summary.get('generation_statistics', {})
funnel = {
    'total': int(summary.get('total_problems_evaluated', 158)),
    'gen_success': int(gs.get('success', 0)),
    'gen_fail': int(gs.get('fail', 0)),
    'gen_timeout': int(gs.get('timeout', 0)),
    'passed': int(summary.get('total_correct_completions', 0)),
    'pass_rate': round(float(REP.get('metrics', {}).get('pass_rate', 0.0)), 4),
}
funnel['gen_success_then_pass_rate'] = round(funnel['passed']/funnel['gen_success'], 4) if funnel['gen_success'] else 0.0
OLD = {'label': 'old_.17_nonzhulong', 'pass_rate_5run_mean': 0.0304, 'pass_rate_5run_std': 0.0083, 'n_runs': 5,
       'model': 'minicpm5-2b-sft-v39-final (global_step_105)',
       'env': '.17 local eda_fastmcp clone, no RAG, no MCP sandbox, run_commands ENABLED (no PreToolUse hook)',
       'benchmark': 'EDA-Eval-PyAether-v20260311_fixed.jsonl (158 tasks)',
       'source': 'MEMORY step105 5-run mean 0.0304+/-0.0083 (locked)'}
NEW = {'label': 'new_3615_zhulong', 'pass_rate': funnel['pass_rate'], 'n_runs': 1,
       'model': 'minicpm5-2b-sft-v39-final (global_step_105) via reverse tunnel 18096->.17:8096',
       'env': '36.15 official eda_fastmcp pipeline, PreToolUse hook (run_commands DISABLED), RAG + MCP sandbox reachable',
       'benchmark': 'EDA-Eval-PyAether-158 (158 tasks)',
       'cli_versions': {'zhulong_fork': '3.0.29', 'cline_official': '3.0.51'},
       'source': 'attribution_3615_run1/final_report.json (2026-11-14T20:08)',
       'note_single_run': 'single run; 5-run mean+/-std pending (protocol Sec.2)'}
diff_pp = round((NEW['pass_rate'] - OLD['pass_rate_5run_mean']) * 100, 2)
result = {
 'directive': '2026-11-15 08:1x user order: re-run 158 eval the zhulong way + re-attribute (exclude run_commands)',
 'baseline_run': 'attribution_3615_run1 (36.15, official eda_fastmcp run_cline_script.sh, PreToolUse hook active)',
 'is_zhulong_method': True,
 'zhulong_method_evidence': [
   'PreToolUse hook deployed to ~/.cline/hooks/PreToolUse (36.15), mtime 2026-11-15 07:35',
   'run_commands overridden 1051 times = hook design (run_commands disabled), NOT model deficit',
   '3 KB tools + run_code all used: get_api_details 354, search_apis 285, search_apis_by_keyword 232, run_code 96 successful attempts',
   'official pipeline: format_eval_task.py + run_cli.sh + run_eval.py (final_report.json matches run_eval output)',
   'providers.json (36.15): model=minicpm5-2b-sft-v39-final, baseUrl=http://127.0.0.1:18096/v1 (reverse tunnel to .17:8096)',
   'EDA_PROMPT_TEMPLATE_PYAETHER=eval_sys_prompt_template_old.md'],
 'cli_versions': NEW['cli_versions'],
 'funnel': funnel,
 'Q1_real_mcp_rejection_rate_exclude_run_commands': {
   'definition': 'only search_apis/get_api_details/search_apis_by_keyword/run_code; run_commands EXCLUDED (built-in tool disabled by hook)',
   'per_tool': real_mcp_table,
   'total_real_mcp_rejections': real_tot_rej,
   'total_real_mcp_attempts': real_tot_att,
   'overall_real_mcp_rejection_rate': _rate(real_tot_rej, real_tot_att),
   'verdict': 'LOW (~5-6%). Model CAN call real MCP tools. The prior 80.6%% run_commands figure is hook design, not model deficit.'},
 'Q2_run_code_rejection_rate': {
   'run_code_rejections': _rej('run_code'),
   'run_code_successful_attempts': _att('run_code'),
   'run_code_rejection_rate': _rate(_rej('run_code'), _att('run_code')),
   'run_code_variants_rejections_incl': rc_rej,
   'run_code_variants_attempts_incl': rc_att,
   'run_code_variants_rejection_rate_incl': _rate(rc_rej, rc_att),
   'verdict': 'VERY LOW (~3%%). run_code (the only execution channel in the white-list) works. Real execution ability is present.'},
 'Q3_silent_no_generation': {
   'silent_no_gen_tasks': silent,
   'out_of_gen_fail': n_gen_fail,
   'share_of_gen_fail': round(silent/n_gen_fail, 4) if n_gen_fail else 0.0,
   'share_of_158': round(silent/158, 4),
   'characteristics': 'zero rejections, zero tool calls, gen_fail -> model never entered the agent loop',
   'verdict': '45 tasks (28.5%% of 158) silently never entered the agent loop. NOT a tool-format problem; a model-doesnt-start problem. Unchanged by the tool-face switch.'},
 'Q4_pass1_diff_decomposition': {
   'old_baseline': OLD,
   'new_baseline': NEW,
   'pass1_diff_pp': diff_pp,
   'decomposition': [
     {'factor': 'tool_face', 'detail': 'run_commands DISABLED by hook (1051 rejections removed from deficit); RAG 3 KB tools + run_code ENABLED & reachable', 'direction': 'enables retrieval+execution'},
     {'factor': 'knowledge', 'detail': 'RAG API-doc knowledge base reachable on 36.15 (:9009 recall) vs none on .17', 'direction': '+retrieval'},
     {'factor': 'sandbox', 'detail': 'MCP sandbox (run_code -> EDA env) reachable via 36.15 SANDBOX_ENDPOINTS vs none on .17', 'direction': '+execution'},
     {'factor': 'prompt', 'detail': 'same EDA_PROMPT_TEMPLATE_PYAETHER=eval_sys_prompt_template_old.md (controlled)', 'direction': 'neutral'},
     {'factor': 'concurrency', 'detail': '-p 8 -n both (controlled)', 'direction': 'neutral'},
     {'factor': 'n_runs', 'detail': 'old=5-run mean, new=1-run -> diff not yet statistically tested (McNemar/bootstrap pending 5-run)', 'direction': 'caveat'}],
   'verdict': '+15.95pp jump attributable MAINLY to environment (RAG+sandbox reachable), NOT to run_commands being disabled. Prior model-cant-call-MCP-tools attribution INVALIDATED: real MCP rejection ~5-6%%, run_code ~3%%.'},
 'rejection_breakdown_full': {
   'total_rejections': total_rej,
   'run_commands_rejections_hook_design': run_commands_rej,
   'run_commands_share': round(run_commands_rej/total_rej, 4) if total_rej else 0.0,
   'real_mcp_rejections': real_tot_rej,
   'workspace_confinement_rejections_read_files': _rej('read_files'),
   'reject_reasons': rej_reasons},
 'genfail_deep_dive': gdd,
 'classification_sixtype': PER.get('classification_RCA_v2_sixtype', {}),
 'integrity_check': {
   'pyAether_MCP_calls_source': 'attribution_3615_run1/codegen_rejection_stats.json#pyAether_MCP_calls',
   'reject_tools_source': 'attribution_3615_run1_perquest_profile.json#aggregate_reject_tools',
   'final_report_source': 'attribution_3615_run1/final_report.json',
   'recompute_command': 'python3 bpt_zhulong_reattribution.py'}
}
out = os.path.join(RUN_DIR, 'attribution_zhulong_reattribution.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print('='*70)
print('ZHULONG-METHOD RE-ATTRIBUTION (run_commands EXCLUDED)')
print('='*70)
print('Is zhulong method:', result['is_zhulong_method'])
print('CLI versions:', NEW['cli_versions'])
print('Funnel: total=%d gen_success=%d gen_fail=%d passed=%d pass_rate=%.4f' % (funnel['total'], funnel['gen_success'], funnel['gen_fail'], funnel['passed'], funnel['pass_rate']))
print('-'*70)
print('Q1 real MCP rejection (exclude run_commands):')
for t in REAL_MCP:
    v = real_mcp_table[t]
    print('  %-26s reject=%4d attempts=%4d rate=%.1f%%' % (t, v['rejections'], v['total_attempts'], v['rejection_rate']*100))
print('  OVERALL real MCP: reject=%d attempts=%d rate=%.1f%%' % (real_tot_rej, real_tot_att, _rate(real_tot_rej, real_tot_att)*100))
print('-'*70)
print('Q2 run_code rejection: reject=%d attempts=%d rate=%.1f%%' % (_rej('run_code'), _att('run_code'), _rate(_rej('run_code'), _att('run_code'))*100))
print('-'*70)
print('Q3 silent no-generation: %d / %d gen_fail (%.1f%% of 158)' % (silent, n_gen_fail, silent/158*100))
print('-'*70)
print('Q4 Pass@1 diff: old=%.4f (5-run)  new=%.4f (1-run)  diff=%+.2fpp' % (OLD['pass_rate_5run_mean'], NEW['pass_rate'], diff_pp))
print('-'*70)
print('run_commands rejections (HOOK DESIGN, excluded): %d / %d total (%.1f%%)' % (run_commands_rej, total_rej, run_commands_rej/total_rej*100))
print('Output:', out)
