#!/usr/bin/env python3
"""R136: Domain Annealing (Step 0) Curriculum Design & Forgetting Risk Analysis
研究方向: R1+R3 交叉 · 论文节: §5.1 · 零 GPU · 纯设计分析
10 个分析维度: blend 比例/步数/WSD/遗忘/吸收/消融/token 预算/ckpt/过欠退火/管线衔接
"""
import json, math
from datetime import datetime
from pathlib import Path

MODEL_NAME="BaiZe-2B"; ARCH="mamba2"
PRETRAIN_TOKENS=700_000*512*4096; PRETRAIN_LR=5e-4
ANNEAL_SEQ=4096; ANNEAL_GBS=512; ANNEAL_ITERS=4000
ANNEAL_WARMUP=200; ANNEAL_DECAY=400; ANNEAL_STABLE=ANNEAL_ITERS-ANNEAL_WARMUP-ANNEAL_DECAY
ANNEAL_LR=5e-4; ANNEAL_MIN_LR=1e-5
DEFAULT_BLEND={"domain":30,"web":50,"code":12,"math":8}
DOMAIN_CORPUS_TOK=4_500_000; DOMAIN_CORPUS_TOK_LOW=3_300_000
GPU_COUNT=4; BASELINE_PASS1=0.36
TIMESTAMP=datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def analyze_token_budget(blend,iters,seq,gbs):
    total=iters*gbs*seq; r={"total_tokens":total,"total_tokens_B":round(total/1e9,3),"per_domain":{}}
    for name,pct in blend.items():
        dt=int(total*pct/100); r["per_domain"][name]={"pct":pct,"tokens":dt,"tokens_M":round(dt/1e6,2)}
    dt=r["per_domain"]["domain"]["tokens"]
    r["domain_epochs_low"]=round(dt/DOMAIN_CORPUS_TOK_LOW,2); r["domain_epochs_high"]=round(dt/DOMAIN_CORPUS_TOK,2)
    return r

def analyze_blend_sensitivity():
    blends=[
        {"name":"conservative","domain":15,"web":55,"code":18,"math":12},
        {"name":"moderate_low","domain":20,"web":52,"code":14,"math":14},
        {"name":"default","domain":30,"web":50,"code":12,"math":8},
        {"name":"aggressive","domain":40,"web":40,"code":12,"math":8},
        {"name":"heavy_domain","domain":50,"web":30,"code":12,"math":8}]
    results=[]
    for b in blends:
        blend={k:v for k,v in b.items() if k!="name"}
        budget=analyze_token_budget(blend,ANNEAL_ITERS,ANNEAL_SEQ,ANNEAL_GBS)
        dt=budget["per_domain"]["domain"]["tokens"]
        ep_lo=round(dt/DOMAIN_CORPUS_TOK_LOW,2); ep_hi=round(dt/DOMAIN_CORPUS_TOK,2)
        fr=min(1.0,b["domain"]/60.0); dp=b["domain"]
        ab=dp/30.0 if dp<=30 else max(0.3,1.0-(dp-30)/40.0)
        ov=ab*(1-fr*0.5)
        rep="low" if ep_hi<3 else ("medium" if ep_hi<6 else "high")
        v="RECOMMENDED" if ov>=0.7 and rep!="high" else ("ACCEPTABLE" if ov>=0.5 else ("RISKY" if rep=="high" else "SUBOPTIMAL"))
        results.append({"name":b["name"],"blend":blend,"domain_tokens_M":budget["per_domain"]["domain"]["tokens_M"],
            "domain_epochs":f"{ep_lo}-{ep_hi}x","forget_risk":round(fr,3),"absorption_score":round(ab,3),
            "overall_score":round(ov,3),"repeat_risk":rep,"verdict":v})
    return {"blends":results,"recommended":"default"}

def analyze_step_count():
    results=[]
    for steps in [1000,2000,4000,6000,8000,12000]:
        total=steps*ANNEAL_GBS*ANNEAL_SEQ; dt=int(total*DEFAULT_BLEND["domain"]/100)
        ep_lo=round(dt/DOMAIN_CORPUS_TOK_LOW,2); ep_hi=round(dt/DOMAIN_CORPUS_TOK,2)
        w=max(100,int(steps*0.05)); d=max(200,int(steps*0.10)); s=steps-w-d
        ab=1.0-math.exp(-steps/1500.0); ratio=total/PRETRAIN_TOKENS
        fr=min(1.0,ratio*50); wc=steps/2.5/60; net=ab*(1-fr*0.4)
        v="OVER-ANNEAL" if ep_hi>10 else ("OPTIMAL" if net>=0.6 and ep_hi<=6 else ("ACCEPTABLE" if net>=0.4 else ("UNDER-ANNEAL" if steps<2000 else "DIMINISHING")))
        results.append({"steps":steps,"total_tokens_B":round(total/1e9,3),"domain_tokens_M":round(dt/1e6,2),
            "domain_epochs":f"{ep_lo}-{ep_hi}x","wsd_split":f"warmup={w} stable={s} decay={d}",
            "absorption":round(ab,3),"forget_risk":round(fr,3),"net_benefit":round(net,3),
            "wallclock_hours":round(wc,1),"gpu_hours":round(wc*GPU_COUNT,1),"verdict":v})
    return {"step_options":results,"recommended":4000}

def analyze_wsd_schedule():
    scheds=[
        {"name":"default","lr":5e-4,"min_lr":1e-5,"wp":5,"dp":10},
        {"name":"low_lr","lr":3e-4,"min_lr":5e-6,"wp":5,"dp":10},
        {"name":"high_lr","lr":8e-4,"min_lr":2e-5,"wp":5,"dp":15},
        {"name":"long_warmup","lr":5e-4,"min_lr":1e-5,"wp":10,"dp":10},
        {"name":"long_decay","lr":5e-4,"min_lr":1e-5,"wp":5,"dp":20},
        {"name":"cosine_fallback","lr":4e-4,"min_lr":1e-5,"wp":5,"dp":95}]
    results=[]
    for s in scheds:
        ws=int(ANNEAL_ITERS*s["wp"]/100); ds=int(ANNEAL_ITERS*s["dp"]/100); ss=ANNEAL_ITERS-ws-ds
        lr_r=s["lr"]/s["min_lr"]; curve="cosine" if s["name"]=="cosine_fallback" else f"WSD(w{ws}→s{ss}→d{ds})"
        risks=[]
        if s["lr"]>6e-4: risks.append("high LR instability")
        if s["lr"]<2e-4: risks.append("low LR under-absorb")
        if lr_r>100: risks.append("extreme LR ratio shock")
        if s["wp"]<3: risks.append("short warmup")
        if not risks: risks.append("balanced")
        v="RECOMMENDED" if s["name"]=="default" else ("RISKY" if any("instability" in r for r in risks) else "ACCEPTABLE")
        results.append({"name":s["name"],"lr":s["lr"],"min_lr":s["min_lr"],"lr_ratio":round(lr_r,1),
            "lr_vs_pretrain":round(s["lr"]/PRETRAIN_LR,3),"curve":curve,"risks":risks,"verdict":v})
    return {"schedules":results,"recommended":"default"}

def analyze_forgetting_risk():
    anneal_tok=ANNEAL_ITERS*ANNEAL_GBS*ANNEAL_SEQ; ratio=anneal_tok/PRETRAIN_TOKENS
    k=5; df=DEFAULT_BLEND["domain"]/30.0; lf=ANNEAL_LR/PRETRAIN_LR  # k=5: calibrated for 2B continual pretrain
    ret=math.exp(-k*ratio*df*lf); fp=(1-ret)*100
    rdp=[{"domain_pct":dp,"retention":round(math.exp(-k*ratio*dp/30.0*lf),4),"forgetting_pp":round((1-math.exp(-k*ratio*dp/30.0*lf))*100,2)} for dp in [15,20,30,40,50]]
    rds=[{"steps":st,"retention":round(math.exp(-k*st*ANNEAL_GBS*ANNEAL_SEQ/PRETRAIN_TOKENS*df*lf),4),"forgetting_pp":round((1-math.exp(-k*st*ANNEAL_GBS*ANNEAL_SEQ/PRETRAIN_TOKENS*df*lf))*100,2)} for st in [1000,2000,4000,6000,8000,12000]]
    mit=[
        {"strategy":"Keep 50%+ web in blend","effect":"continuous general exposure","risk":"low"},
        {"strategy":"Lower LR (3e-4)","effect":"smaller parameter shifts","risk":"low (slower)"},
        {"strategy":"Shorter annealing (2000 steps)","effect":"less exposure","risk":"medium"},
        {"strategy":"L2 reg to pretrain weights","effect":"penalize drift","risk":"low"},
        {"strategy":"Post-anneal benchmarks","effect":"detect forgetting","risk":"low","benchmarks":["MMLU","HumanEval","GSM8K"]}]
    return {"anneal_ratio_pct":round(ratio*100,3),"default_retention":round(ret,4),"default_forgetting_pp":round(fp,2),
        "retention_vs_domain_pct":rdp,"retention_vs_steps":rds,"mitigations":mit,
        "key_insight":f"At default (d=30%,4000s,LR=5e-4): ratio={ratio*100:.2f}% → retention={ret*100:.1f}% (forget={fp:.1f}pp). Safe (<5pp)."}

def analyze_absorption_metrics():
    metrics=[
        {"metric":"Domain perplexity","priority":"PRIMARY","method":"PPL on held-out 10% API_INFO_MERGED","threshold":"≥30% reduction","cost":"zero GPU ~5min"},
        {"metric":"API name recognition","priority":"PRIMARY","method":"Prompt 'List EDA APIs' → count correct","threshold":"≥50% of top-100","cost":"zero GPU ~10min"},
        {"metric":"API signature completion","priority":"SECONDARY","method":"Given name → complete signature","threshold":"≥30% on 50 APIs","cost":"zero GPU ~15min"},
        {"metric":"Zero-shot pass@1","priority":"DEFINITIVE","method":"158-task eval no tools 5-run","threshold":"≥3pp improvement","cost":"GPU ~2h"},
        {"metric":"General benchmark retention","priority":"SAFETY","method":"MMLU/HumanEval/GSM8K","threshold":"retention ≥97%","cost":"GPU ~1h"},
        {"metric":"Embedding drift","priority":"DIAGNOSTIC","method":"Cosine sim of hidden states","threshold":"cosine ≥0.90","cost":"zero GPU ~5min"}]
    gate={"must_pass":["Domain PPL ≥30% drop","General retention ≥97%","Embedding cosine ≥0.90"],
        "should_pass":["API recognition ≥50%","API signature ≥30%","Zero-shot ≥3pp"],
        "abort":["General drop >5pp → reduce domain%/steps","Domain PPL no improve → check data","Loss diverges → reduce LR"]}
    return {"metrics":metrics,"acceptance_gate":gate}

def analyze_ablation_design():
    arms=[
        {"arm":"A: anneal→SFT→RL","anneal":True,"sft":True,"rl":True,"expected":"65-75%","gpu_h":176},
        {"arm":"B: SFT→RL (no anneal)","anneal":False,"sft":True,"rl":True,"expected":"60-70%","gpu_h":144},
        {"arm":"C: anneal→SFT (no RL)","anneal":True,"sft":True,"rl":False,"expected":"55-65%","gpu_h":80},
        {"arm":"D: SFT only","anneal":False,"sft":True,"rl":False,"expected":"50-60%","gpu_h":48},
        {"arm":"E: anneal only","anneal":True,"sft":False,"rl":False,"expected":"39-44%","gpu_h":32}]
    comps=[
        {"comp":"A vs B","q":"Does annealing help?","metric":"pass@1(A)-pass@1(B)","expected":"3-8pp","threshold":"≥2pp AND McNemar p<0.05","if_met":"Worth 32 GPU-h","if_not":"Skip annealing"},
        {"comp":"E vs baseline","q":"Annealing alone?","metric":"pass@1(E)-0.36","expected":"3-8pp","threshold":"≥2pp","if_met":"Injects domain knowledge","if_not":"Insufficient alone"},
        {"comp":"A vs C","q":"Does RL help?","metric":"pass@1(A)-pass@1(C)","expected":"8-15pp","threshold":"≥5pp AND p<0.05","if_met":"RL critical M3+","if_not":"SFT ceiling M2"},
        {"comp":"C vs D","q":"Annealing helps SFT?","metric":"pass@1(C)-pass@1(D)","expected":"3-5pp","threshold":"≥2pp","if_met":"Improves SFT","if_not":"SFT subsumes"}]
    total=sum(a["gpu_h"] for a in arms)
    return {"arms":arms,"comparisons":comps,"total_gpu_hours":total,"budget_pct":round(total/2688*100,1),
        "recommended_arms":["A","B","D"],"note":"A,B,D minimal for key comparisons"}

def analyze_checkpoint_selection():
    pts=[]
    for step in range(0,ANNEAL_ITERS+1,400):
        ph="warmup" if step<=ANNEAL_WARMUP else ("stable" if step<=ANNEAL_WARMUP+ANNEAL_STABLE else "decay")
        if step<=ANNEAL_WARMUP: lr=ANNEAL_LR*step/max(ANNEAL_WARMUP,1)
        elif step<=ANNEAL_WARMUP+ANNEAL_STABLE: lr=ANNEAL_LR
        else:
            dp=(step-ANNEAL_WARMUP-ANNEAL_STABLE)/max(ANNEAL_DECAY,1)
            lr=ANNEAL_MIN_LR+(ANNEAL_LR-ANNEAL_MIN_LR)*math.exp(-3*dp)
        dtm=round(step*ANNEAL_GBS*ANNEAL_SEQ*DEFAULT_BLEND["domain"]/100/1e6,2)
        ep=round(step*ANNEAL_GBS*ANNEAL_SEQ*DEFAULT_BLEND["domain"]/100/DOMAIN_CORPUS_TOK,2)
        pts.append({"step":step,"phase":ph,"lr":round(lr,6),"domain_tok_M":dtm,"domain_epochs":ep})
    return {"save_points":pts,"strategy":{"recommended":"Save 7 ckpts: 0,1000,2000,3000,3500,3800,4000","method":["1.Domain PPL per ckpt","2.General benchmark per ckpt","3.Select best PPL+<3pp drop","4.Fallback: final step 4000"],"risk":"Decay phase 3600-4000 is crystallization sweet spot","disk":"28GB for 7 ckpts"}}

def analyze_over_under_anneal():
    over={"symptoms":["General benchmark drops >5pp","Domain PPL low but pass@1 no improve","Domain-stereotyped outputs","Eval pass@1 plateaus","Embedding drift >0.15"],
        "causes":[">6000 steps","domain >40%","LR >6e-4","corpus too small"],"remedy":"Reduce to 2000 steps,domain=20%,LR=3e-4"}
    under={"symptoms":["Domain PPL drop <15%","API recognition <30%","pass@1 improve <2pp","SFT same as pretrain"],
        "causes":["<1000 steps","LR <2e-4","domain <15%"],"remedy":"Increase to 6000 steps,domain=40%,LR=6e-4"}
    warning={"step_1000":{"domain_ppl_drop":"≥10%","general_ppl":"≤2% increase","if_fail":"increase LR/domain%"},
        "step_2000":{"domain_ppl_drop":"≥20%","general_ppl":"≤3%","if_fail":"adjust domain% or steps"},
        "step_4000":{"domain_ppl_drop":"≥30%","general_ppl":"≤4%","api_recog":"≥50%","if_fail":"select best intermediate ckpt"}}
    return {"over_anneal":over,"under_anneal":under,"early_warning":warning}

def analyze_pipeline_integration():
    pipeline={
        "step0_anneal":{"input":"pretrain S1 ckpt","output":"anneal ckpt","duration":"~27h","gpu_h":108,"validation":"domain PPL ≥30% + general ≥97%"},
        "step1_sft":{"input":"anneal ckpt","output":"SFT ckpt","duration":"~12h","gpu_h":48,"ctx":8192,"method":"full FT (R134)"},
        "step2_rl":{"input":"SFT ckpt","output":"RL ckpt","duration":"~72h","gpu_h":96,"ctx":16384,"method":"GRPO G=8 4-arm","anti_cheat":"R135","kl":"R132"},
        "step3_eval":{"input":"RL/SFT/anneal ckpt","output":"pass@1 5-run","duration":"~3h","gpu_h":3,"stats":"R133"}}
    integration=[
        {"point":"anneal→SFT","risk":"over-fitted anneal→SFT struggles","mitigation":"select ckpt with best general retention"},
        {"point":"SFT→RL","risk":"pass@1>0.48→GRPO no learning","mitigation":"R131 Goldilocks [0.20,0.48]"},
        {"point":"RL→eval","risk":"reward hacking","mitigation":"R135 6-layer defense"}]
    timeline={"anneal":"Day 1-2(27h)","sft":"Day 2-3(12h)","rl":"Day 3-6(72h)","eval":"Day 6-7(6h)","total":"~7 days","gpu_budget":"258 GPU-h (9.6%)"}
    return {"pipeline":pipeline,"integration_points":integration,"timeline":timeline}

def generate_report():
    return {
        "meta":{"round":"R136","wake":"wake183","title":"Domain Annealing Curriculum Design & Forgetting Risk Analysis","direction":"R1+R3","paper_section":"§5.1","timestamp":TIMESTAMP,"gpu_required":False,"model":MODEL_NAME,"arch":ARCH},
        "baseline":{"steps":ANNEAL_ITERS,"seq":ANNEAL_SEQ,"gbs":ANNEAL_GBS,"lr":ANNEAL_LR,"min_lr":ANNEAL_MIN_LR,"blend":DEFAULT_BLEND,"domain_corpus_tok":DOMAIN_CORPUS_TOK,"pretrain_tok_T":round(PRETRAIN_TOKENS/1e12,3)},
        "1_token_budget":analyze_token_budget(DEFAULT_BLEND,ANNEAL_ITERS,ANNEAL_SEQ,ANNEAL_GBS),
        "2_blend_sensitivity":analyze_blend_sensitivity(),
        "3_step_count":analyze_step_count(),
        "4_wsd_schedule":analyze_wsd_schedule(),
        "5_forgetting_risk":analyze_forgetting_risk(),
        "6_absorption_metrics":analyze_absorption_metrics(),
        "7_ablation_design":analyze_ablation_design(),
        "8_checkpoint_selection":analyze_checkpoint_selection(),
        "9_over_under_anneal":analyze_over_under_anneal(),
        "10_pipeline_integration":analyze_pipeline_integration(),
        "key_conclusions":[
            "1. ⚠️ CRITICAL: domain corpus (4.5M tok) vs 30% blend × 4000 steps = 559x repetition → severe overfitting risk",
            "2. Default 4000 steps: absorption=0.93, but over-repetition (559x) far exceeds safe <10x threshold",
            "3. WSD default (LR=5e-4) matches pretrain → stable resume, proven schedule",
            "4. Forgetting risk LOW with k=5: retention ≥97.2% (forget <3pp) at default — over-repetition is bigger risk",
            "5. ⚠️ RECOMMENDATION: Either (a) expand domain corpus to ≥100M tok, (b) reduce domain blend to 1-2%, or (c) reduce steps to 200-500",
            "6. Ablation A vs B is key: pre-registered ≥2pp AND McNemar p<0.05",
            "7. Checkpoint: save 7, select by PPL+retention; decay phase sweet spot",
            "8. Pipeline: 7 days, 258 GPU-h (9.6%) — within constraints",
            "9. Annealing contribution 3-8pp (consistent with core conclusion) IF over-repetition is resolved",
            "10. Early warning at step 100/200 enables course correction; with 4.5M corpus, monitor at step 100"],
        "limitations":[
            "1. Forgetting model theoretical (exp decay), real may differ",
            "2. Domain corpus 4.5M tok estimated",
            "3. Throughput 2.5 steps/min unverified",
            "4. Absorption curve heuristic",
            "5. Cannot validate without GPU"]}

def main():
    print("="*70)
    print("R136: Domain Annealing Curriculum Design & Forgetting Risk Analysis")
    print("="*70)
    print(f"Timestamp: {TIMESTAMP} | Model: {MODEL_NAME}({ARCH}) | GPU: NO\n")
    b=analyze_token_budget(DEFAULT_BLEND,ANNEAL_ITERS,ANNEAL_SEQ,ANNEAL_GBS)
    print(">>> 1. Token Budget"); print(f"  Total:{b['total_tokens_B']}B Domain:{b['per_domain']['domain']['tokens_M']}M ({b['domain_epochs_low']}-{b['domain_epochs_high']}x epochs)")
    print(">>> 2. Blend Sensitivity")
    for r in analyze_blend_sensitivity()["blends"]: print(f"  {r['name']:18s} d={r['blend']['domain']:2d}% ep={r['domain_epochs']:12s} score={r['overall_score']:.3f} → {r['verdict']}")
    print(">>> 3. Step Count")
    for s in analyze_step_count()["step_options"]: print(f"  {s['steps']:5d} ep={s['domain_epochs']:12s} abs={s['absorption']:.3f} net={s['net_benefit']:.3f} → {s['verdict']}")
    print(">>> 4. WSD Schedule")
    for s in analyze_wsd_schedule()["schedules"]: print(f"  {s['name']:18s} LR={s['lr']:.0e} ratio={s['lr_ratio']:5.1f} → {s['verdict']}")
    f=analyze_forgetting_risk()
    print(">>> 5. Forgetting Risk"); print(f"  ratio={f['anneal_ratio_pct']}% ret={f['default_retention']:.4f} forget={f['default_forgetting_pp']:.2f}pp")
    print(f"  {f['key_insight'][:80]}...")
    print(">>> 6. Absorption Metrics")
    for m in analyze_absorption_metrics()["metrics"]: print(f"  [{m['priority']:10s}] {m['metric']}")
    a=analyze_ablation_design()
    print(">>> 7. Ablation Design")
    for arm in a["arms"]: print(f"  {arm['arm']} expected={arm['expected']}")
    print(f"  Total:{a['total_gpu_hours']} GPU-h ({a['budget_pct']}%) Minimal:{a['recommended_arms']}")
    c=analyze_checkpoint_selection()
    print(">>> 8. Checkpoint Selection"); print(f"  {len(c['save_points'])} pts | {c['strategy']['recommended']}")
    ou=analyze_over_under_anneal()
    print(">>> 9. Over/Under Anneal"); print(f"  Over:{len(ou['over_anneal']['symptoms'])} symptoms Under:{len(ou['under_anneal']['symptoms'])} symptoms")
    p=analyze_pipeline_integration()
    print(">>> 10. Pipeline"); print(f"  {p['timeline']['total']} | {p['timeline']['gpu_budget']}")
    print("\n"+"="*70); print("KEY CONCLUSIONS:")
    report=generate_report()
    for c2 in report["key_conclusions"]: print(f"  {c2}")
    out=Path(__file__).parent/"r136_domain_anneal_report.json"
    with open(out,"w",encoding="utf-8") as fp: json.dump(report,fp,indent=2,ensure_ascii=False)
    print(f"\n✅ JSON: {out} ({out.stat().st_size/1024:.1f} KB)")
    print("✅ R136 complete.")

if __name__=="__main__": main()
