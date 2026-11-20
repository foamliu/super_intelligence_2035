import glob,json,os
removed=0; kept=0; per_h={}
for h in ['cline-patched','codex','opencode','claude-code','pi','hermes','deepseek-harness']:
    rc=0
    for f in glob.glob(f'predictions_glm53/{h}__*.json'):
        try:
            d=json.load(open(f))
            mp=''
            if isinstance(d,list):
                for x in d:
                    if isinstance(x,dict) and (x.get('model_patch') or x.get('patch')):
                        mp=x.get('model_patch','') or x.get('patch',''); break
            elif isinstance(d,dict):
                mp=d.get('model_patch','') or d.get('patch','')
            s=mp.strip() if isinstance(mp,str) else ''
            if len(s)<=50:
                os.remove(f); rc+=1; removed+=1
            else:
                kept+=1
        except Exception as e:
            pass
    per_h[h]=rc
print(f'Removed {removed} empty-patch files, kept {kept} real-patch files')
for h,c in per_h.items(): print(f'  {h}: removed {c}')
