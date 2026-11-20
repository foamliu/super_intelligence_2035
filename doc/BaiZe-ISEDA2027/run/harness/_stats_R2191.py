#!/usr/bin/env python3
import json, glob
PRED = "predictions_glm53"
EVAL = "reports"
H = ["cline-patched","codex","opencode","claude-code","pi","hermes","deepseek-harness"]
DISP = {"cline-patched":"cline","deepseek-harness":"deepseek"}

def get_patch(f):
    d = json.load(open(f))
    if isinstance(d, list) and d: return (d[0].get("model_patch","") or "").strip()
    if isinstance(d, dict): return (d.get("model_patch","") or "").strip()
    return ""

total_files = total_real = total_resolved = 0
for h in H:
    fs = glob.glob(f"{PRED}/{h}__*.json")
    r = sum(1 for f in fs if get_patch(f))
    e = json.load(open(f"{EVAL}/eval_glm53_{h}.json"))
    rr = len(e.get("resolved",[]))
    fa = len(e.get("failed",[]))
    ir = len(e.get("infra_or_quota",[]))
    total_files += len(fs); total_real += r; total_resolved += rr
    print(f"{DISP.get(h,h)}: files={len(fs)} real={r} eval_n={e.get('n',0)} resolved={rr} failed={fa} infra={ir}")
print(f"TOTAL: files={total_files} real={total_real} resolved={total_resolved}")

# cline detail
fs = glob.glob(f"{PRED}/cline-patched__*.json")
real = sum(1 for f in fs if get_patch(f))
empty = len(fs) - real
e = json.load(open(f"{EVAL}/eval_glm53_cline-patched.json"))
print(f"CLINE_C4: files={len(fs)} real={real} empty={empty} resolved={len(e.get('resolved',[]))} failed={len(e.get('failed',[]))} infra={len(e.get('infra_or_quota',[]))}")
