#!/usr/bin/env python3
"""Count ACTUAL tool_use blocks (not string occurrences) in cline traces.
Used for 3.04% baseline A/B adjudication (user order 2026-11-14 16:1x).
Scans the 5 real step105 baseline trace dirs + the 194219 dir wake481 cited.
"""
import json, os, glob, sys
from collections import Counter

RUN_DIRS = {
  'run1': '~/eda_code_eval/2026_1113_024153/trace',
  'run2': '~/eda_code_eval/2026_1113_062714/trace',
  'run3': '~/eda_code_eval/2026_1113_101852/trace',
  'run4': '~/eda_code_eval/2026_1113_131353/trace',
  'run5': '~/eda_code_eval/2026_1113_163053/trace',
  'X_194219_wake481cited': '~/eda_code_eval/2026_1113_194219/trace',
}
CLEAN = ('pyAether_MCP_server__search_apis','pyAether_MCP_server__search_apis_by_keyword',
         'pyAether_MCP_server__get_api_details','pyAether_MCP_server__run_code')

def scan(root):
    tu=Counter(); nres=0; nerr=0; tasks=0; sessions=0
    for task in sorted(os.listdir(root)):
        tp=os.path.join(root,task)
        if not os.path.isdir(tp): continue
        tasks+=1
        for mf in glob.glob(os.path.join(tp,'*.messages.json')):
            sessions+=1
            try: d=json.load(open(mf))
            except: continue
            for msg in d.get('messages',[]):
                c=msg.get('content')
                if not isinstance(c,list): continue
                for b in c:
                    if not isinstance(b,dict): continue
                    if b.get('type')=='tool_use': tu[b.get('name','?')]+=1
                    elif b.get('type')=='tool_result':
                        nres+=1
                        if b.get('is_error'): nerr+=1
    return tu,tasks,sessions,nres,nerr

if __name__=='__main__':
    out={}
    for name,r in RUN_DIRS.items():
        root=os.path.expanduser(r)
        if not os.path.isdir(root): out[name]={'missing':root}; print(name,'MISSING',root); continue
        tu,tasks,sessions,nres,nerr=scan(root)
        clean={k:tu.get(k,0) for k in CLEAN}
        out[name]={'tasks':tasks,'sessions':sessions,'clean_mcp':clean,
                   'total_tool_use':sum(tu.values()),'tool_result':nres,'is_error':nerr,
                   'top10':tu.most_common(10)}
        print(f'=== {name} ({root}) ===')
        print(f'  tasks={tasks} sessions={sessions} clean_mcp={clean} total_tool_use={sum(tu.values())} tool_result={nres} is_error={nerr}')
    json.dump(out,open('/tmp/posttrain_trace_toolcount.json','w'),indent=1,ensure_ascii=False)
    print('saved /tmp/posttrain_trace_toolcount.json')
