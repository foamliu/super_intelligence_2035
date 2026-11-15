#!/usr/bin/env python3
# bpt_zhulong_baseline_5run_analysis.py
# zhulong 口径 5-run 基线分析：mean±std + 与旧 .17 5-run(step105) 配对检验
import argparse, json, glob, os, statistics, datetime
RUN_DIR_DEFAULT = "/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run"
OLD_5RUN_DIR = "/tmp/posttrain_5run_eval/step105"

def load_perq(path):
    res = {}
    if not os.path.exists(path): return res
    with open(path) as f:
        for line in f:
            line=line.strip()
            if not line: continue
            try:
                o=json.loads(line); tid=o.get("task_id")
                if tid is not None: res[tid]=bool(o.get("passed",False))
            except Exception: continue
    return res

def load_perq_fr(path):
    res={}
    if not os.path.exists(path): return res
    try: d=json.load(open(path))
    except Exception: return res
    # 优先 details_per_task (run_eval 输出): {task_id: {num_correct,pass_rate,...}}
    dpt=d.get("details_per_task")
    if isinstance(dpt,dict):
        for tid,o in dpt.items():
            if isinstance(o,dict):
                res[tid]= bool(o.get("num_correct",0)>0) or (o.get("pass_rate",0)>0)
        if res: return res
    for key in ("execution_results","results","per_task","task_results"):
        arr=d.get(key)
        if isinstance(arr,list):
            for o in arr:
                if isinstance(o,dict) and o.get("task_id") is not None:
                    res[o["task_id"]]=bool(o.get("passed",o.get("status")=="passed"))
        elif isinstance(arr,dict):
            for tid,o in arr.items():
                if isinstance(o,dict): res[tid]=bool(o.get("passed",o.get("status")=="passed"))
    return res

def get_pass_rate(fr):
    if not os.path.exists(fr): return None
    try: d=json.load(open(fr))
    except Exception: return None
    m=d.get("metrics")
    if isinstance(m,dict) and m.get("pass_rate") is not None: return m["pass_rate"]
    return d.get("pass_rate", d.get("passRate"))

def collect_new(run_dir, num_runs):
    runs=[]
    for i in range(1,num_runs+1):
        d=os.path.join(run_dir,f"attribution_3615_run{i}"); fr=os.path.join(d,"final_report.json")
        pr=get_pass_rate(fr)
        perq=load_perq(os.path.join(d,"execution_results.jsonl")) or load_perq_fr(fr)
        runs.append({"idx":i,"pass_rate":pr,"perq":perq,"dir":d})
    return runs

def collect_old(old_dir):
    runs=[]
    if not os.path.isdir(old_dir): return runs
    for r in sorted(glob.glob(os.path.join(old_dir,"run*"))):
        fr=os.path.join(r,"final_report.json")
        runs.append({"dir":r,"pass_rate":get_pass_rate(fr),"perq":load_perq_fr(fr)})
    return runs

def ms(xs):
    if not xs: return {"n":0,"mean":None,"std":None}
    m=statistics.fmean(xs); s=statistics.pstdev(xs) if len(xs)>1 else 0.0
    return {"n":len(xs),"mean":round(m,4),"std":round(s,4),"values":[round(x,4) for x in xs]}

def perq_frac(runs):
    cnt={}; cover={}
    for r in runs:
        for tid,p in r["perq"].items():
            cnt[tid]=cnt.get(tid,0)+(1 if p else 0); cover[tid]=cover.get(tid,0)+1
    return {tid:round(cnt[tid]/cover[tid],4) for tid in cnt}, cover

def mcnemar(a,b):
    n11=n00=n10=n01=0
    for k in set(a)|set(b):
        pa=a.get(k,False); pb=b.get(k,False)
        if pa and pb: n11+=1
        elif (not pa) and (not pb): n00+=1
        elif pa and (not pb): n10+=1
        else: n01+=1
    chi2=( (abs(n10-n01)-1)**2/(n10+n01) ) if (n10+n01)>0 else 0.0
    return {"n11_both_pass":n11,"n00_both_fail":n00,"n10_new_only":n10,"n01_old_only":n01,
            "chi2_corrected":round(chi2,4),"discordant":n10+n01}

def wilcoxon(fa,fb):
    ks=[k for k in set(fa)&set(fb) if (fa[k]-fb[k])!=0]
    if not ks: return {"n_nonzero":0}
    try:
        from scipy.stats import wilcoxon
        w=wilcoxon([fa[k] for k in ks],[fb[k] for k in ks])
        return {"W":float(w.statistic),"p":float(w.pvalue),"n_nonzero":len(ks)}
    except Exception as e:
        return {"n_nonzero":len(ks),"error":str(e)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--run-dir",default=RUN_DIR_DEFAULT)
    ap.add_argument("--num-runs",type=int,default=5)
    ap.add_argument("--out",required=True)
    ap.add_argument("--old-dir",default=OLD_5RUN_DIR)
    a=ap.parse_args()
    new=collect_new(a.run_dir,a.num_runs); old=collect_old(a.old_dir)
    new_prs=[r["pass_rate"] for r in new if r["pass_rate"] is not None]
    old_prs=[r["pass_rate"] for r in old if r["pass_rate"] is not None]
    new_frac,new_cover=perq_frac(new); old_frac,old_cover=perq_frac(old)
    new_any={tid:any(r["perq"].get(tid,False) for r in new) for tid in new_cover}
    old_any={tid:any(r["perq"].get(tid,False) for r in old) for tid in old_cover}
    mc=mcnemar(new_any,old_any) if (new_any and old_any) else {"note":"per-question data insufficient"}
    wx=wilcoxon(new_frac,old_frac) if (new_frac and old_frac) else {"note":"insufficient"}
    nm=ms(new_prs); om=ms(old_prs)
    out={"generated_at":datetime.datetime.now().isoformat(timespec="seconds"),
      "protocol":"EDA-Eval-PyAether-158, Pass@1, 5-run mean±std, -p 8 -n",
      "new_zhulong_baseline":{**nm,
        "env":"36.15 zhulong口径 (PreToolUse hook, RAG+沙盒可达, run_commands禁用)",
        "cli_agent":"zhulong fork 3.0.29","model":"minicpm5-2b-sft-v39-final(step105) via 18096->.17:8096"},
      "old_17_baseline":{**om,"env":".17 非zhulong (无RAG/无沙盒, run_commands启用)","source":a.old_dir},
      "delta_pp":round((nm["mean"]-om["mean"])*100,2) if (nm["mean"] is not None and om["mean"] is not None) else None,
      "paired_test_passany_mcnemar":mc,"paired_test_passfrac_wilcoxon":wx,
      "note":"5-run检验补齐；McNemar用pass@any二值；Wilcoxon用每题pass-fraction配对；scipy不可用则只报n。"}
    with open(a.out,"w") as f: json.dump(out,f,ensure_ascii=False,indent=2)
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
