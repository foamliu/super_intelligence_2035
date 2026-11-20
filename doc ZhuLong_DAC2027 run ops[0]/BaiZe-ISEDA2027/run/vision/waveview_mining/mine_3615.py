import json, os, re, hashlib
BASE='/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow'
REF=os.path.join(BASE,'reference'); AST=os.path.join(BASE,'assets')
SHARDS=['A','B','C','D']
KWL=['wave','fsdb','vcd','wlf','waveform','waveview','波形','eye','transient','sweep','duty','jitter']
KW_RE={k:re.compile(re.escape(k),re.I) for k in KWL}
TOOL_RE=re.compile(r'\b(vcs|hspice|finesim|finespice|xrun|irun|ncsim|veriloga|ngspice|spectre|verdi|vvp|iverilog)\b',re.I)
CALL_RE=re.compile(r'(?:subprocess\.(?:run|Popen|call|check_call|check_output)|os\.system)\s*\(\s*(.{0,260})',re.S)
RERUN_RE=re.compile(r're-?run|RE-RUNS|TRUE L2 grader|fresh (?:A and B|run)',re.I)
ANSWER_RE=re.compile(r'answer|deliverable is an? answer|read the figure|image-required|wv_summary|答案|读图|读数|anti-hardcode',re.I)

def shadata(p):
    try: return hashlib.sha256(open(p,'rb').read()).hexdigest()
    except: return None
def dirset(p):
    s=set()
    try:
        for n in os.listdir(p):
            if os.path.isdir(os.path.join(p,n)): s.add(n)
    except: pass
    return s
refset=dirset(REF); assetset=dirset(AST)
def find(task_id, sset, base):
    cands=[]
    if task_id:
        cands.append(task_id)
        if task_id.startswith('EDA-Eval-DesignFlow-'): cands.append(task_id[len('EDA-Eval-DesignFlow-'):])
    for c in cands:
        if c in sset: return c, os.path.join(base,c)
    return None,None
def pngs(adir, sub=''):
    out=[]
    d=os.path.join(adir,sub) if adir else ''
    if d and os.path.isdir(d):
        for n in os.listdir(d):
            if os.path.isfile(os.path.join(d,n)) and n.lower().endswith('.png'): out.append(n)
    return sorted(out)
def kw_hits(blob):
    return [k for k in KWL if KW_RE[k].search(blob)]
def classify(src):
    rerun=bool(RERUN_RE.search(src or ''))
    direct_tool=None
    for c in CALL_RE.findall(src or ''):
        if 'sys.executable' in c: continue
        m=TOOL_RE.search(c)
        if m: direct_tool=m.group(0).lower(); break
    if rerun and direct_tool: return 'B','needs-sandbox:'+direct_tool+'+re-run-hidden-B'
    if direct_tool: return 'B','needs-sandbox:'+direct_tool
    if rerun: return 'B','needs-sandbox:re-run-hidden-B'
    return 'A','answer-validation:no-direct-eda-tool'

total=0; recs=[]
for s in SHARDS:
    p=os.path.join(BASE,f'EDA-Eval-DesignFlow_{s}.jsonl')
    with open(p) as f:
        for i,line in enumerate(f,1):
            line=line.strip()
            if not line: continue
            total+=1
            try: o=json.loads(line)
            except: continue
            md=o.get('metadata',{}) or {}
            tid=str(o.get('task_id') or '')
            dom=str(md.get('domain') or '')
            tname=str(md.get('task_name') or '')
            scen=str(md.get('scenario') or '')
            prompt=str(o.get('prompt') or '')
            artifacts=md.get('artifacts') or o.get('expected_artifacts') or []
            blob=' '.join([tid,tname,scen,dom,prompt])
            hits=kw_hits(blob)
            if not (dom.lower()=='waveform' or hits): continue
            rname,rdir=find(tid,refset,REF)
            check_exists=bool(rdir and os.path.isfile(os.path.join(rdir,'check.py')))
            check_path_rel=('reference/'+rname+'/check.py') if check_exists else ''
            check_path_3615=(os.path.join(rdir,'check.py')) if check_exists else ''
            check_sha=shadata(check_path_3615) if check_exists else None
            check_src=''
            if check_exists:
                try: check_src=open(check_path_3615,encoding='utf-8',errors='ignore').read()
                except: pass
            k_asserts=len(re.findall(r'\bassert\b',check_src))
            aname,adir=find(tid,assetset,AST)
            vp=pngs(adir); hp=pngs(adir,'hidden')
            img_sha={fn:shadata(os.path.join(adir,fn)) for fn in vp} if adir else {}
            if vp: fid='synthesized-image-restored'
            elif hp: fid='real-private'
            else: fid='no-visible-image'
            vtype,vreason=(classify(check_src) if check_exists else ('NA','no-check.py'))
            recs.append({'case_id':tid,'case_name':tname or tid,'source_shard':s,'source_pool':s,'pool_line':i,
                'shard_jsonl':f'EDA-Eval-DesignFlow_{s}.jsonl','domain':dom,'requires_image':bool(vp),
                'image_paths':[f'assets/{aname}/{p2}' for p2 in vp] if aname else [],
                'image_sha256':img_sha,'image_count':len(vp),'image_missing':(not bool(vp)),
                'hidden_b_images':[f'assets/{aname}/hidden/{p2}' for p2 in hp] if aname else [],
                'check_path':check_path_rel,'check_path_3615':check_path_3615,'check_exists':check_exists,
                'sha256_check':check_sha,'k_conditions':k_asserts or None,'modified':False,
                'asset_fidelity':fid,'vision_run_type':vtype,'vab_reason':vreason,
                'keyword_hits':hits,'expected_artifacts':artifacts,'answer_validation_signal':bool(ANSWER_RE.search(check_src or '')),
                'has_subprocess':'subprocess' in check_src,'prompt_len':len(prompt)})
out={'base':BASE,'pool_line_counts':{'A':352,'B':390,'C':418,'D':446,'total':1606},
     'total_lines':total,'waveview_candidates':len(recs),'records':recs}
json.dump(out,open('/tmp/wv_mined_v2.json','w'))
j=[r for r in recs if r['check_exists']]
print('POOL',out['pool_line_counts'])
print('CANDIDATES',len(recs),'JUDGEABLE',len(j),'IMG',sum(1 for r in recs if r['image_paths']))
print('V-A',sum(1 for r in j if r['vision_run_type']=='A'),'V-B',sum(1 for r in j if r['vision_run_type']=='B'))
print('V-A img',sum(1 for r in j if r['image_paths'] and r['vision_run_type']=='A'),'V-B img',sum(1 for r in j if r['image_paths'] and r['vision_run_type']=='B'))
