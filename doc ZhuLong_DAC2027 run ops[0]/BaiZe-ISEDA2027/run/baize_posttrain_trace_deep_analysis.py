#!/usr/bin/env python3
"""Deep analysis of 3.04% baseline 5-run traces for RCA v2 report."""
import json, os, glob, re, statistics
from collections import Counter

RUN_DIRS = {
    'run1': '~/eda_code_eval/2026_1113_024153/trace',
    'run2': '~/eda_code_eval/2026_1113_062714/trace',
    'run3': '~/eda_code_eval/2026_1113_101852/trace',
    'run4': '~/eda_code_eval/2026_1113_131353/trace',
    'run5': '~/eda_code_eval/2026_1113_163053/trace',
}
MCP = ('pyAether_MCP_server__search_apis',
       'pyAether_MCP_server__search_apis_by_keyword',
       'pyAether_MCP_server__get_api_details',
       'pyAether_MCP_server__run_code')
ERR_PAT = {
    'SyntaxError': re.compile(r'SyntaxError'),
    'non-ASCII': re.compile(r'Code contains non-ASCII|non-ASCII|ASCII'),
    'AttributeError': re.compile(r'AttributeError'),
    'NameError': re.compile(r'NameError'),
    'TypeError': re.compile(r'TypeError'),
    'ImportError': re.compile(r'ImportError|ModuleNotFoundError'),
    'IndexError': re.compile(r'IndexError'),
    'KeyError': re.compile(r'KeyError'),
    'ValueError': re.compile(r'ValueError'),
    'timeout': re.compile(r'timeout|timed out|TimeoutError'),
    'connection': re.compile(r'connection|Connection|ECONNREFUSED'),
}

def toolres_text(b):
    c = b.get('content')
    if isinstance(c, str): return c
    if isinstance(c, list):
        return ' '.join(x.get('text','') for x in c if isinstance(x,dict) and x.get('type')=='text')
    return ''

def scan_run(root):
    tu = Counter(); tu_err = Counter(); rc_err = Counter()
    rc_success=0; rc_total=0; sa_success=0; sa_total=0
    ga_success=0; ga_total=0; kw_success=0; kw_total=0
    submit_calls=0; submit_err=0
    per_task_calls=[]; per_task_mcp=[]; per_task_rc=[]
    tasks_with_any_mcp=0; tasks_with_rc=0
    retrieved_apis=[]; used_in_code=[]
    contradiction_hits=0; contradiction_total=0
    n_tasks=0
    for task in sorted(os.listdir(root)):
        tp=os.path.join(root,task)
        if not os.path.isdir(tp): continue
        n_tasks+=1
        task_tu=0; task_mcp=0; task_rc=0
        for mf in glob.glob(os.path.join(tp,'*.messages.json')):
            try: d=json.load(open(mf))
            except: continue
            msgs=d.get('messages',[]); id2name={}; prev_atxt=''
            for msg in msgs:
                c=msg.get('content')
                if not isinstance(c,list): continue
                for b in c:
                    if not isinstance(b,dict): continue
                    t=b.get('type')
                    if t=='tool_use':
                        nm=b.get('name','?'); tu[nm]+=1; task_tu+=1
                        tid=b.get('id')
                        if tid: id2name[tid]=nm
                        if nm=='pyAether_MCP_server__run_code':
                            task_rc+=1; task_mcp+=1; rc_total+=1
                            code=str(b.get('input',{}).get('code',''))
                            used_in_code.append(code)
                            contradiction_total+=1
                            if re.search(r'internal|infer|reason|verify|assume|might|perhaps|推测|推演|假设', prev_atxt, re.I):
                                contradiction_hits+=1
                        elif nm in MCP:
                            task_mcp+=1
                            if nm.endswith('search_apis'): sa_total+=1
                            elif nm.endswith('search_apis_by_keyword'): kw_total+=1
                            elif nm.endswith('get_api_details'):
                                ga_total+=1
                                aps=b.get('input',{}).get('api_list',[])
                                if isinstance(aps,list): retrieved_apis.extend(aps)
                        elif nm=='submit_and_exit': submit_calls+=1
                    elif t=='tool_result':
                        nm=id2name.get(b.get('tool_use_id'), b.get('name','?'))
                        is_err=b.get('is_error',False); txt=toolres_text(b)
                        if nm=='pyAether_MCP_server__run_code':
                            if is_err:
                                tu_err['run_code']+=1
                                for label,pat in ERR_PAT.items():
                                    if pat.search(txt): rc_err[label]+=1; break
                                else: rc_err['other']+=1
                            else: rc_success+=1
                        elif nm and nm.endswith('search_apis'):
                            if not is_err and 'api_name' in txt: sa_success+=1
                            elif is_err: tu_err['search_apis']+=1
                        elif nm and nm.endswith('get_api_details'):
                            if not is_err and ('api_name' in txt or 'api_type' in txt): ga_success+=1
                            elif is_err: tu_err['get_api_details']+=1
                        elif nm and nm.endswith('search_apis_by_keyword'):
                            if not is_err: kw_success+=1
                            elif is_err: tu_err['keyword']+=1
                        elif nm=='submit_and_exit':
                            if is_err: submit_err+=1
                    elif t=='text' and msg.get('role')=='assistant':
                        prev_atxt=b.get('text','')
        per_task_calls.append(task_tu); per_task_mcp.append(task_mcp); per_task_rc.append(task_rc)
        if task_mcp>0: tasks_with_any_mcp+=1
        if task_rc>0: tasks_with_rc+=1
    retrieved_set=set()
    for a in retrieved_apis:
        if isinstance(a,str): retrieved_set.add(a.split('.')[-1])
    used_tokens=set()
    for code in used_in_code:
        for tok in re.findall(r'[A-Za-z_][A-Za-z0-9_]*', code): used_tokens.add(tok)
    overlap=retrieved_set & used_tokens
    return {
        'n_tasks':n_tasks,'tool_use':dict(tu),'mcp_clean':{k:tu.get(k,0) for k in MCP},
        'tool_result_errors':dict(tu_err),'rc_total':rc_total,'rc_success':rc_success,
        'rc_err_taxonomy':dict(rc_err),'sa_total':sa_total,'sa_success':sa_success,
        'kw_total':kw_total,'kw_success':kw_success,'ga_total':ga_total,'ga_success':ga_success,
        'submit_calls':submit_calls,'submit_err':submit_err,'per_task_calls':per_task_calls,
        'per_task_mcp':per_task_mcp,'per_task_rc':per_task_rc,'tasks_with_any_mcp':tasks_with_any_mcp,
        'tasks_with_rc':tasks_with_rc,'retrieved_apis_count':len(retrieved_set),
        'used_overlap':len(overlap),'overlap_sample':sorted(list(overlap))[:20],
        'contradiction_hits':contradiction_hits,'contradiction_total':contradiction_total,
    }

def pct(a,b): return round(100.0*a/b,2) if b else 0.0

if __name__=='__main__':
    out={}; agg=Counter()
    for name,r in RUN_DIRS.items():
        root=os.path.expanduser(r)
        if not os.path.isdir(root): out[name]={'missing':root}; print(name,'MISSING',root); continue
        res=scan_run(root); out[name]=res
        tc=res['per_task_calls']; mc=res['per_task_mcp']; rc=res['per_task_rc']
        print(f'=== {name} ===')
        print(f'  tasks={res["n_tasks"]} total_tool_use={sum(res["tool_use"].values())} mcp={res["mcp_clean"]}')
        print(f'  sa {res["sa_success"]}/{res["sa_total"]}({pct(res["sa_success"],res["sa_total"])}%) kw {res["kw_success"]}/{res["kw_total"]}({pct(res["kw_success"],res["kw_total"])}%) ga {res["ga_success"]}/{res["ga_total"]}({pct(res["ga_success"],res["ga_total"])}%) rc {res["rc_success"]}/{res["rc_total"]}({pct(res["rc_success"],res["rc_total"])}%)')
        print(f'  rc_err={res["rc_err_taxonomy"]} submit={res["submit_calls"]}/{res["submit_err"]}err({pct(res["submit_err"],res["submit_calls"])}%)')
        print(f'  per_task_calls mean={statistics.mean(tc):.1f} med={statistics.median(tc):.0f} max={max(tc)} min={min(tc)}')
        print(f'  per_task_mcp mean={statistics.mean(mc):.1f} tasks_with_mcp={res["tasks_with_any_mcp"]}/{res["n_tasks"]} per_task_rc mean={statistics.mean(rc):.2f} tasks_with_rc={res["tasks_with_rc"]}/{res["n_tasks"]}')
        print(f'  retrieved={res["retrieved_apis_count"]} overlap={res["used_overlap"]} sample={res["overlap_sample"]} contradiction={res["contradiction_hits"]}/{res["contradiction_total"]}')
        for k in res['mcp_clean']: agg[k]+=res['mcp_clean'][k]
        for k in ['rc_total','rc_success','sa_total','sa_success','kw_total','kw_success','ga_total','ga_success','submit_calls','submit_err','contradiction_hits','contradiction_total']:
            agg[k]+=res[k]
        agg['tasks']+=res['n_tasks']
        agg['tasks_with_any_mcp']+=res['tasks_with_any_mcp']
        agg['tasks_with_rc']+=res['tasks_with_rc']
        for k,v in res['rc_err_taxonomy'].items(): agg['rc_err_'+k]+=v
    allcalls=[]; allmcp=[]; allrc=[]
    for r in out.values():
        allcalls.extend(r.get('per_task_calls',[])); allmcp.extend(r.get('per_task_mcp',[])); allrc.extend(r.get('per_task_rc',[]))
    out['_aggregate']={
        'mcp_clean':{k:agg[k] for k in MCP},'total_mcp':sum(agg[k] for k in MCP),
        'rc_total':agg['rc_total'],'rc_success':agg['rc_success'],
        'sa_total':agg['sa_total'],'sa_success':agg['sa_success'],
        'kw_total':agg['kw_total'],'kw_success':agg['kw_success'],
        'ga_total':agg['ga_total'],'ga_success':agg['ga_success'],
        'submit_calls':agg['submit_calls'],'submit_err':agg['submit_err'],
        'tasks_total':agg['tasks'],'tasks_with_mcp':agg['tasks_with_any_mcp'],'tasks_with_rc':agg['tasks_with_rc'],
        'rc_err_taxonomy':{k.replace('rc_err_',''):agg[k] for k in agg if k.startswith('rc_err_')},
        'per_task_calls_mean':round(statistics.mean(allcalls),1) if allcalls else 0,
        'per_task_calls_median':statistics.median(allcalls) if allcalls else 0,
        'per_task_calls_max':max(allcalls) if allcalls else 0,
        'per_task_calls_p90':sorted(allcalls)[int(0.9*len(allcalls))] if allcalls else 0,
        'per_task_mcp_mean':round(statistics.mean(allmcp),1) if allmcp else 0,
        'per_task_mcp_median':statistics.median(allmcp) if allmcp else 0,
        'per_task_mcp_max':max(allmcp) if allmcp else 0,
        'per_task_rc_mean':round(statistics.mean(allrc),2) if allrc else 0,
        'per_task_rc_median':statistics.median(allrc) if allrc else 0,
        'per_task_rc_max':max(allrc) if allrc else 0,
        'n_tasks_zero_mcp':sum(1 for v in allmcp if v==0),
        'n_tasks_zero_rc':sum(1 for v in allrc if v==0),
        'contradiction_hits':agg['contradiction_hits'],'contradiction_total':agg['contradiction_total'],
    }
    a=out['_aggregate']
    print('\n=== AGGREGATE ===')
    print(f'  total_mcp={a["total_mcp"]} sa={a["mcp_clean"]["pyAether_MCP_server__search_apis"]} kw={a["mcp_clean"]["pyAether_MCP_server__search_apis_by_keyword"]} ga={a["mcp_clean"]["pyAether_MCP_server__get_api_details"]} rc={a["mcp_clean"]["pyAether_MCP_server__run_code"]}')
    print(f'  rc_success={a["rc_success"]}/{a["rc_total"]}({pct(a["rc_success"],a["rc_total"])}%) err={a["rc_err_taxonomy"]}')
    print(f'  submit={a["submit_calls"]} err={a["submit_err"]}({pct(a["submit_err"],a["submit_calls"])}%)')
    print(f'  tasks={a["tasks_total"]} with_mcp={a["tasks_with_mcp"]} with_rc={a["tasks_with_rc"]} zero_mcp={a["n_tasks_zero_mcp"]} zero_rc={a["n_tasks_zero_rc"]}')
    print(f'  per_task_calls mean={a["per_task_calls_mean"]} med={a["per_task_calls_median"]} max={a["per_task_calls_max"]} p90={a["per_task_calls_p90"]}')
    print(f'  per_task_mcp mean={a["per_task_mcp_mean"]} med={a["per_task_mcp_median"]} max={a["per_task_mcp_max"]} per_task_rc mean={a["per_task_rc_mean"]} max={a["per_task_rc_max"]}')
    print(f'  contradiction={a["contradiction_hits"]}/{a["contradiction_total"]}')
    dest='/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/trace_deep_analysis_3p04.json'
    json.dump(out,open(dest,'w'),indent=1,ensure_ascii=False)
    print('saved',dest)
