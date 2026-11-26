#!/usr/bin/env python3
"""Print Avg for each ckpt's 8-set results.json (harness-standard metric)."""
import json, os, glob

BASE = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results"
TASKS = ["arc_challenge","arc_easy","boolq","hellaswag","openbookqa","piqa","sciq","winogrande"]
NORM = {"arc_challenge","arc_easy","hellaswag","openbookqa","piqa","sciq"}

for d in sorted(glob.glob(os.path.join(BASE, "gguf_iter_*_fixed_8set"))):
    it = os.path.basename(d).replace("gguf_iter_","").replace("_fixed_8set","")
    rf = os.path.join(d, "results.json")
    if not os.path.isfile(rf):
        print(f"{it}: NO results.json")
        continue
    data = json.load(open(rf))
    vals = []
    for t in TASKS:
        r = data["results"][t]
        v = r.get("acc_norm,none") if t in NORM else None
        if v is None:
            v = r.get("acc,none")
        if v is None:
            v = 0.0
        vals.append(v)
    avg = sum(vals)/len(vals)*100
    print(f"{it}: Avg={avg:.2f}%  " + " ".join(f"{t[:4]}={v*100:.0f}" for t,v in zip(TASKS,vals)))
