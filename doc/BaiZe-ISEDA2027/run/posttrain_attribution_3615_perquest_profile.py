#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Per-question profiling + RCA-v2 six-type classification for 36.15 run1.
# Advances POSTTRAIN_ENV_ATTRIBUTION_SPEC.md Task B steps 1-2 beyond wake499 funnel.
import json, re, sys, collections, argparse
ANSI = re.compile(r'\x1b\[[0-9;]*m')
def strip(s): return ANSI.sub('', s)
FUNC_OPEN = re.compile(r'<function name="([a-zA-Z_][a-zA-Z0-9_]*)">')
REJECT = re.compile(r"Tool call (\S+) was rejected before execution")
TASK_START = re.compile(r'=== \[worker-\d+\] .*?(EDA-Eval-PyAether-\d+)')
def reject_reason(line):
    L = strip(line)
    if 'received string' in L and 'expected array' in L: return 'string-not-array'
    if 'expected boolean' in L and ('received string' in L or 'received undefined' in L or 'received null' in L): return 'wrong-type-boolean'
    if 'received undefined' in L or 'received null' in L: return 'missing-required-field'
    if 'unavailable tool' in L: return 'unavailable-tool'
    if 'invalid_type' in L or 'Type validation failed' in L: return 'other-type-error'
    return 'other'
def normalize_tool(name):
    return name.replace('pyAether_MCP_server__','').replace('eda_flow__','')
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--log', default='/tmp/posttrain_baseline_3615/run1/codegen.log')
    ap.add_argument('--report', default='/tmp/posttrain_baseline_3615/run1/final_report.json')
    ap.add_argument('--out', default='attribution_3615_run1_perquest_profile.json')
    args = ap.parse_args()
    with open(args.report) as f: report = json.load(f)
    details = report['details_per_task']
    buf = collections.defaultdict(list); cur = None
    with open(args.log, errors='replace') as f:
        for raw in f:
            line = strip(raw)
            m = TASK_START.search(line)
            if m: cur = m.group(1); buf[cur] = []; continue
            if cur is not None: buf[cur].append(line)
    per_task = {}; agg_tool = collections.Counter(); agg_rr = collections.Counter(); agg_rt = collections.Counter()
    for tid, lines in buf.items():
        tc = collections.Counter(); rej = 0; rrs = collections.Counter(); rts = collections.Counter()
        submit = rcode = search = 0
        for ln in lines:
            for m in FUNC_OPEN.finditer(ln): tc[normalize_tool(m.group(1))] += 1
            if 'was rejected before execution' in ln:
                rej += 1; rrs[reject_reason(ln)] += 1
                mr = REJECT.search(ln)
                if mr: rts[normalize_tool(mr.group(1))] += 1
            if '<function name="submit_and_exit">' in ln: submit += 1
            if '<function name="pyAether_MCP_server__run_code">' in ln or '<function name="eda_flow__run_code">' in ln: rcode += 1
            if '<function name="pyAether_MCP_server__search_apis"' in ln or '<function name="pyAether_MCP_server__search_apis_by_keyword"' in ln: search += 1
        for t,c in tc.items(): agg_tool[t] += c
        for r,c in rrs.items(): agg_rr[r] += c
        for t,c in rts.items(): agg_rt[t] += c
        per_task[tid] = {'n_log_lines': len(lines), 'tool_calls': dict(tc), 'total_tool_calls': sum(tc.values()), 'total_rejections': rej, 'reject_reasons': dict(rrs), 'reject_tools': dict(rts), 'submit_calls': submit, 'run_code_calls': rcode, 'search_calls': search}
    TYPE_MAP = {'gen_fail':'T6_tool_format_genfail','gen_timeout':'T5_timeout','assertion':'T4_assertion_insufficient','typeerr':'T3_api_misuse','pass':'PASS'}
    classification = collections.Counter(); per_outcome = {}
    for tid, d in details.items():
        gs = d['generation_statuses'][0]; ets = d.get('error_types', [])
        if d['num_correct'] > 0: outcome = 'pass'
        elif gs == 'timeout': outcome = 'gen_timeout'
        elif gs != 'success': outcome = 'gen_fail'
        elif 'AssertionError' in ets: outcome = 'assertion'
        elif 'TypeError' in ets: outcome = 'typeerr'
        else: outcome = 'gen_fail'
        per_outcome[tid] = outcome
        classification[TYPE_MAP.get(outcome,'T_other')] += 1
        if tid in per_task:
            per_task[tid]['outcome'] = outcome; per_task[tid]['generation_status'] = gs
            per_task[tid]['execution_status'] = d['execution_statuses'][0]
            per_task[tid]['error_types'] = ets; per_task[tid]['pass_rate'] = d['pass_rate']
    gfrd = collections.Counter(); gf_search = gf_rcode = gf_zero = gf_nolog = 0
    for tid, d in details.items():
        if per_outcome.get(tid) != 'gen_fail': continue
        p = per_task.get(tid)
        if p is None: gf_nolog += 1; continue
        if p['search_calls'] > 0: gf_search += 1
        if p['run_code_calls'] > 0: gf_rcode += 1
        if p['total_rejections'] == 0: gf_zero += 1
        r = p['total_rejections']
        gfrd['0' if r==0 else '1-2' if r<=2 else '3-5' if r<=5 else '6-10' if r<=10 else '11+'] += 1
    out = {'source':'36.15 run1: codegen.log + final_report.json','log_path':args.log,'report_path':args.report,'n_tasks_in_report':len(details),'n_tasks_in_log':len(buf),'aggregate_tool_calls':dict(agg_tool.most_common()),'aggregate_reject_reasons':dict(agg_rr.most_common()),'aggregate_reject_tools':dict(agg_rt.most_common()),'classification_RCA_v2_sixtype':dict(classification),'genfail_deep_dive':{'n_gen_fail':sum(1 for t,o in per_outcome.items() if o=='gen_fail'),'rejection_count_distribution':dict(gfrd),'used_search_apis':gf_search,'used_run_code':gf_rcode,'zero_rejections':gf_zero,'no_log_segment':gf_nolog},'per_task':per_task,'note':'T6_tool_format_genfail = dominant 36.15 failure: model attempted tools but schema rejections (string-not-array / wrong-type / missing-field / unavailable-tool) exhausted budget -> no code file -> Generation fail. Distinct from .17 head failure (degenerate pass 60.63%).'}
    with open(args.out,'w') as f: json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps({k:v for k,v in out.items() if k!='per_task'}, ensure_ascii=False, indent=1))
    print('WROTE', args.out, file=sys.stderr)
if __name__ == '__main__': main()
