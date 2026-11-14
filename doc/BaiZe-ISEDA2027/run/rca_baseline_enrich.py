#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, glob, re, sys, collections
from datetime import datetime

EVAL_DIR = os.path.expanduser('~/eda_code_eval')
BATCH = {1:'2026_1113_024153',2:'2026_1113_062714',3:'2026_1113_101852',4:'2026_1113_131353',5:'2026_1113_163053'}
BASE = '/tmp/posttrain_5run_eval/step105'

data = json.load(open('/tmp/rca_baseline_data.json'))
tasks = data['tasks']

def iso(s):
    try: return datetime.fromisoformat(s.replace('Z','+00:00'))
    except Exception: return None

gen_text = {}
for i in range(1,6):
    fp = f'{BASE}/run{i}/completed_code_generation.jsonl'
    if not os.path.exists(fp): continue
    for line in open(fp):
        r = json.loads(line)
        gen_text[(r['task_id'], i)] = (r.get('completion',''), r.get('status',''))

def gen_fail_subtype(comp):
    c = (comp or '').strip()
    if c == 'pass': return 'degenerate_pass'
    if len(c) == 0: return 'empty'
    if len(c) < 40: return 'stub_short'
    return 'has_code'

trace_info = {}
for i in range(1,6):
    b = BATCH[i]
    tdir = f'{EVAL_DIR}/{b}/trace'
    if not os.path.isdir(tdir):
        print(f'NO trace dir run{i}: {tdir}', file=sys.stderr); continue
    for task in os.listdir(tdir):
        tp = f'{tdir}/{task}'
        if not os.path.isdir(tp): continue
        sess = [f for f in os.listdir(tp) if f.endswith('.json') and f!='api_conversation_history.json']
        n_iter = len(sess)
        wall=0.0; tot=0; smin=None; emax=None
        for sf in sess:
            try: d=json.load(open(f'{tp}/{sf}'))
            except Exception: continue
            s=iso(d.get('started_at')); e=iso(d.get('ended_at'))
            if s and e:
                wall += (e-s).total_seconds()
                if smin is None or s<smin: smin=s
                if emax is None or e>emax: emax=e
        for sf in sess:
            mf=f"{tp}/{sf.replace('.json','.messages.json')}"
            if not os.path.exists(mf): continue
            try: msgs=json.load(open(mf))
            except Exception: continue
            if isinstance(msgs,list):
                for m in msgs:
                    u=m.get('usage') or {}
                    tot += (u.get('prompt_tokens',0) or 0)+(u.get('completion_tokens',0) or 0)
        wt=(emax-smin).total_seconds() if (smin and emax) else wall
        trace_info[(task,i)]={'iterations':n_iter,'wall_s':round(wt,1),'sum_session_s':round(wall,1),'tokens':tot}
print(f'trace_info entries: {len(trace_info)}', file=sys.stderr)

def classify(runrec, subtype):
    gs=runrec['gen']; xs=runrec['exec']; et=runrec['error_types']; passed=runrec['passed']
    if passed: return 'PASS'
    if gs=='timeout': return 'C6_timeout'
    if gs=='fail':
        if subtype=='degenerate_pass': return 'C5_degenerate_pass'
        if subtype in ('empty','stub_short'): return 'C4_no_output'
        return 'C4_gen_fail_other'
    if et and et[0] in ('ModuleNotFoundError','ImportError'): return 'C1_env_import'
    if et and et[0] in ('SyntaxError','IndentationError'): return 'C3_code_syntax'
    if et and et[0] in ('AttributeError','TypeError','NameError','KeyError','ValueError'): return 'C3_code_runtime'
    if et and et[0]=='AssertionError': return 'C3_code_assert'
    if et and et[0]=='Unknown Failure': return 'C7_other'
    return 'C3_code_other'

cat_name={
 'PASS':'通过','C1_env_import':'①环境/依赖','C2_tool_protocol':'②工具调用/协议',
 'C3_code_syntax':'③代码-语法','C3_code_runtime':'③代码-运行时语义','C3_code_assert':'③代码-断言/逻辑','C3_code_other':'③代码-其它',
 'C4_no_output':'④输出格式-无有效代码','C4_gen_fail_other':'④输出格式-产物被拒',
 'C5_degenerate_pass':'⑤推理/放弃-degenerate','C6_timeout':'⑥超时/预算','C7_other':'⑦其它'}

per_run_cat=collections.Counter(); per_task_cat={}
for tid,rec in tasks.items():
    for runrec in rec['runs']:
        i=runrec['run']; comp,st=gen_text.get((tid,i),('',''))
        subtype=gen_fail_subtype(comp) if runrec['gen']=='fail' else None
        runrec['completion_status']=st; runrec['gen_fail_subtype']=subtype
        ti=trace_info.get((tid,i),{})
        runrec['iterations']=ti.get('iterations',0); runrec['wall_s']=ti.get('wall_s',0); runrec['tokens']=ti.get('tokens',0)
        cat=classify(runrec,subtype); runrec['cat']=cat; runrec['cat_name']=cat_name[cat]
        per_run_cat[cat]+=1
    cats=[r['cat'] for r in rec['runs']]; nonpass=[c for c in cats if c!='PASS']
    if rec['pass_count']==5: per_task_cat[tid]='PASS'
    elif nonpass: per_task_cat[tid]=collections.Counter(nonpass).most_common(1)[0][0]
    else: per_task_cat[tid]='PASS'
    rec['task_cat']=per_task_cat[tid]; rec['task_cat_name']=cat_name.get(per_task_cat[tid],'?')

print('=== per (task,run) category (790) ===', file=sys.stderr)
for k,v in per_run_cat.most_common(): print(f'  {v:4d}  {k} {cat_name.get(k,k)}', file=sys.stderr)

deg=collections.Counter()
for (tid,i),(comp,st) in gen_text.items():
    if st=='fail': deg[gen_fail_subtype(comp)]+=1
print('=== gen=fail subtype ===', file=sys.stderr)
for k,v in deg.most_common(): print(f'  {v:4d}  {k}', file=sys.stderr)

data['per_run_cat']=dict(per_run_cat); data['cat_name']=cat_name
json.dump(data, open('/tmp/rca_baseline_enriched.json','w'), ensure_ascii=False, indent=1)
print('WROTE /tmp/rca_baseline_enriched.json', file=sys.stderr)
