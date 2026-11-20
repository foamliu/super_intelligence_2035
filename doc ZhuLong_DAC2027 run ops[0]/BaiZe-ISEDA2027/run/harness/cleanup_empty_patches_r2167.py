import json, glob, os
base='/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/predictions_glm53'
deleted=0
from collections import defaultdict
by_h=defaultdict(int)
for f in glob.glob(os.path.join(base,'*.json')):
    name=os.path.basename(f)
    if name.startswith('predictions_'): continue
    h=name.split('__')[0]
    try:
        d=json.load(open(f))
        mp = d[0].get('model_patch','') if isinstance(d,list) and d else d.get('model_patch','') if isinstance(d,dict) else ''
        if not mp.strip():
            os.remove(f)
            deleted+=1
            by_h[h]+=1
    except: pass
print(f'Deleted {deleted} empty-patch files:')
for h in sorted(by_h): print(f'  {h}: {by_h[h]}')
