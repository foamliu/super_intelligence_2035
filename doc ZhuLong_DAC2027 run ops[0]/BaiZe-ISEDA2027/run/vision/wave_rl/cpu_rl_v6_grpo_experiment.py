#!/usr/bin/env python3
"""cpu_rl_v6_grpo_experiment.py - CPU RL Waveform Experiment v6: Continuous-Reward GRPO.

WHY v6 (building on v5 success, incorporating research daily 2026-11-09 suggestions):
  v5 (RFT, type classification): A=16% -> B(SFT)=37% -> C(RFT)=53%, p=0.0009 SIGNIFICANT.
  But v5 used binary 0/1 reward (RFT just filters correct/incorrect).
  Research daily (AiXapply 2611.07634) suggests 3 improvements:
    1. 奖励拆两项 α=0.25/β=0.35 — error-type-weighted dense reward (not binary)
    2. 合成数据两道闸 — two-gate data quality control
    3. SFT→GRPO对照臂 — try GRPO now that continuous reward solves std=0

WHY GRPO SHOULD WORK NOW (failed in v2-v3):
  v2-v3 GRPO failed because 78.7% of groups had std=0 (all rollouts got the same
  binary reward for period regression). v6 uses type classification with a CONTINUOUS
  shape-similarity reward: even wrong predictions get different partial credit depending
  on HOW wrong (sine<->triangle is "closer" than sine<->square) -> non-zero group
  variance -> GRPO can learn.

v6 DESIGN (pre-registered 2026-11-09):
  1. CONTINUOUS REWARD (two-component, α=0.25, β=0.35):
     R_exact = 1.0 if exact match, 0.0 otherwise
     R_shape = Pearson correlation between normalized data and predicted type's
               canonical template (ideal waveform, same params, no noise)
     R = (α * R_exact + β * R_shape) / (α + β)
  2. TWO-GATE DATA QUALITY (for training questions):
     Gate 1: amplitude — peak-to-peak > 0.3 * amp (not degenerate)
     Gate 2: shape clarity — true type's canonical corr is highest among all 4 types
  3. GRPO with continuous reward (condition C):
     Start from v5's SFT checkpoint (B=37%), group_size=8, 40 steps, PPO clip=0.2
  4. Random reward control (condition D): same GRPO but reward=random(0,1)

PRE-REGISTERED JUDGMENT (written BEFORE running):
  B (SFT, from v5) = 37.0% (known, reuse checkpoint)
  C (GRPO continuous reward) > B: continuous reward gives non-zero group variance
  D (GRPO random reward) <= B: random reward provides no learning signal
  SUCCESS: C > B, C > D, McNemar C-vs-B p < 0.05, bootstrap 95% CI excludes 0
  Secondary: per-class sine accuracy should improve (was 16% in v5 B, weakest class)

Author: vision wake#951.  License: project-internal.
"""
from __future__ import annotations
import sys, os, json, time, math, random, argparse, re
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model, TaskType, PeftModel

LLM_PATH = "/nas_train/app.e0031982/datasets/baize-vision/out/wave_sft_stage1w/qwen3vl_2b_text_extracted"
V5_SFT_CKPT = "/nas_train/app.e0031982/datasets/baize-vision/out/cpu_rl_v5_typecls/sft_adapter"
V5_EVAL_QUESTIONS = "/nas_train/app.e0031982/datasets/baize-vision/out/cpu_rl_v5_typecls/eval_questions.json"
WAVEFORM_TYPES = ["sine", "square", "triangle", "sawtooth"]
_WT_IDX = {wt: i for i, wt in enumerate(WAVEFORM_TYPES)}  # deterministic type->idx
N_SAMPLE_POINTS = 16
N_PERIODS = 2.0
EVAL_SEED_BASE = 995100
TRAIN_SEED_BASE = 20261109
IM_START = "<|im_start|>"
IM_END = "<|im_end|>"
ALPHA = 0.25
BETA = 0.35

SYSTEM_PROMPT = (
    "You are a waveform classification expert. You are given evenly-spaced "
    "voltage samples from a periodic electronic waveform. Classify it as "
    "one of: sine, square, triangle, or sawtooth. "
    "Respond with only the waveform type name, nothing else."
)

# --- 1. WAVEFORM GENERATORS (store params for canonical) --- #
def _gen_sine(rng):
    amp=float(rng.uniform(0.5,5.0)); off=float(rng.uniform(-2.0,2.0))
    freq=float(rng.uniform(1.0,10.0)); ph=float(rng.uniform(0,2*math.pi))
    ns=float(rng.uniform(0.0,0.03*amp))
    t=np.linspace(0,N_PERIODS/freq,N_SAMPLE_POINTS,endpoint=False)
    v=off+amp*np.sin(2*math.pi*freq*t+ph)+rng.normal(0,ns,len(t))
    return t,v,{"amp":amp,"offset":off,"freq":freq,"phase":ph,"noise_std":ns}

def _gen_square(rng):
    amp=float(rng.uniform(0.5,5.0)); off=float(rng.uniform(-2.0,2.0))
    freq=float(rng.uniform(1.0,10.0)); duty=float(rng.uniform(0.3,0.7))
    ns=float(rng.uniform(0.0,0.03*amp))
    t=np.linspace(0,N_PERIODS/freq,N_SAMPLE_POINTS,endpoint=False)
    pic=(freq*t)%1.0; v=np.where(pic<duty,off+amp,off-amp)+rng.normal(0,ns,len(t))
    return t,v,{"amp":amp,"offset":off,"freq":freq,"duty":duty,"noise_std":ns}

def _gen_triangle(rng):
    amp=float(rng.uniform(0.5,5.0)); off=float(rng.uniform(-2.0,2.0))
    freq=float(rng.uniform(1.0,10.0)); ns=float(rng.uniform(0.0,0.03*amp))
    t=np.linspace(0,N_PERIODS/freq,N_SAMPLE_POINTS,endpoint=False)
    ph=(freq*t)%1.0; tri=np.where(ph<0.5,4.0*ph-1.0,3.0-4.0*ph)
    v=off+amp*tri+rng.normal(0,ns,len(t))
    return t,v,{"amp":amp,"offset":off,"freq":freq,"noise_std":ns}

def _gen_sawtooth(rng):
    amp=float(rng.uniform(0.5,5.0)); off=float(rng.uniform(-2.0,2.0))
    freq=float(rng.uniform(1.0,10.0)); ns=float(rng.uniform(0.0,0.03*amp))
    t=np.linspace(0,N_PERIODS/freq,N_SAMPLE_POINTS,endpoint=False)
    ph=(freq*t)%1.0; v=off+amp*(2.0*ph-1.0)+rng.normal(0,ns,len(t))
    return t,v,{"amp":amp,"offset":off,"freq":freq,"noise_std":ns}

_WAVEFORM_GENS={"sine":_gen_sine,"square":_gen_square,"triangle":_gen_triangle,"sawtooth":_gen_sawtooth}
def gen_waveform(wt,rng): return _WAVEFORM_GENS[wt](rng)

# --- 2. CANONICAL TEMPLATES (ideal waveforms, no noise, same params) --- #
def _canon_sine(t,p): return p["offset"]+p["amp"]*np.sin(2*math.pi*p["freq"]*t+p.get("phase",0))
def _canon_square(t,p):
    pic=(p["freq"]*t)%1.0; duty=p.get("duty",0.5)
    return np.where(pic<duty,p["offset"]+p["amp"],p["offset"]-p["amp"])
def _canon_triangle(t,p):
    ph=(p["freq"]*t)%1.0; tri=np.where(ph<0.5,4.0*ph-1.0,3.0-4.0*ph)
    return p["offset"]+p["amp"]*tri
def _canon_sawtooth(t,p):
    ph=(p["freq"]*t)%1.0; return p["offset"]+p["amp"]*(2.0*ph-1.0)
_CANON_GENS={"sine":_canon_sine,"square":_canon_square,"triangle":_canon_triangle,"sawtooth":_canon_sawtooth}
def canonical_template(wt,t,p): 
    g=_CANON_GENS.get(wt); return g(t,p) if g else np.zeros_like(t)

# --- 3. SHAPE SIMILARITY + TWO-GATE + CONTINUOUS REWARD --- #
def _normalize(v):
    v=np.array(v,dtype=np.float64); s=v.std()
    return (v-v.mean())/s if s>=1e-12 else v-v.mean()

def shape_correlation(actual_v,wtype,t,params):
    canon=canonical_template(wtype,t,params)
    a,c=_normalize(actual_v),_normalize(canon)
    if np.std(a)<1e-12 or np.std(c)<1e-12: return 0.0
    return float(np.corrcoef(a,c)[0,1])

def two_gate_check(t,v,params,true_type):
    ptp=float(np.max(v)-np.min(v))
    if ptp<0.3*params["amp"]: return False,"gate1_amplitude"
    corrs={wt:shape_correlation(v,wt,t,params) for wt in WAVEFORM_TYPES}
    if max(corrs,key=corrs.get)!=true_type: return False,"gate2_clarity"
    return True,"passed"

def continuous_reward(question,parsed_type):
    if parsed_type is None: return 0.0
    pt=parsed_type.lower(); tt=str(question["gt_value"]).lower()
    t=np.array(question["t"]); v=np.array(question["v"]); params=question["params"]
    r_exact=1.0 if pt==tt else 0.0
    r_shape=max(0.0,shape_correlation(v,pt,t,params))
    return (ALPHA*r_exact+BETA*r_shape)/(ALPHA+BETA)

# --- 4. PROMPT FORMATTING --- #
def _fmt_val(v):
    if abs(v)<1e-4 and v!=0: return f"{v:.2e}"
    return f"{v:.3f}"

def format_samples(t,v):
    pairs=[f"({_fmt_val(ti)}, {_fmt_val(vi)})" for ti,vi in zip(t,v)]
    return ",\n".join(", ".join(pairs[i:i+4]) for i in range(0,len(pairs),4))

def build_prompt_text(samples_text):
    um=f"Classify this waveform as sine, square, triangle, or sawtooth.\nSample points (time_us, voltage_V):\n{samples_text}"
    return f"{IM_START}system\n{SYSTEM_PROMPT}{IM_END}\n{IM_START}user\n{um}{IM_END}\n{IM_START}assistant\n"

def check_correct(q,pt):
    return pt is not None and pt.lower()==str(q["gt_value"]).lower()

# --- 5. DATA GENERATION (with two-gate filtering) --- #
def gen_question(wt,qid,seed):
    rng=np.random.default_rng(seed); t,v,p=gen_waveform(wt,rng)
    return {"qid":qid,"task":"type_classification","waveform_type":wt,"gt_value":wt,
            "measure_type":"type_classification","samples_text":format_samples(t,v),
            "t":t.tolist(),"v":v.tolist(),"params":p}

def gen_question_gated(wt,qid,seed,max_retries=10):
    for att in range(max_retries):
        rng=np.random.default_rng(seed+att*7919); t,v,p=gen_waveform(wt,rng)
        ok,_=two_gate_check(t,v,p,wt)
        if ok:
            return {"qid":qid,"task":"type_classification","waveform_type":wt,"gt_value":wt,
                    "measure_type":"type_classification","samples_text":format_samples(t,v),
                    "t":t.tolist(),"v":v.tolist(),"params":p}
    return None

def build_eval_set(n_per_type=25,use_v5=True):
    if use_v5 and os.path.exists(V5_EVAL_QUESTIONS):
        with open(V5_EVAL_QUESTIONS) as f: v5qs=json.load(f)
        qs=[]
        for q in v5qs:
            wt=q["waveform_type"]; seed=EVAL_SEED_BASE+q["qid"]*100+_WT_IDX.get(wt,0)
            rng=np.random.default_rng(seed); t,v,p=gen_waveform(wt,rng)
            qs.append({"qid":q["qid"],"task":"type_classification","waveform_type":wt,
                       "gt_value":wt,"measure_type":"type_classification",
                       "samples_text":format_samples(t,v),"t":t.tolist(),"v":v.tolist(),"params":p})
        return qs
    qs=[]; qid=0
    for wt in WAVEFORM_TYPES:
        for i in range(n_per_type):
            qs.append(gen_question(wt,qid,EVAL_SEED_BASE+qid*100+_WT_IDX.get(wt,0))); qid+=1
    return qs

def build_train_set(n,gated=True):
    ex=[]; per=n//len(WAVEFORM_TYPES); rem=n%len(WAVEFORM_TYPES)
    npass=nfail=0
    for i,wt in enumerate(WAVEFORM_TYPES):
        cnt=per+(1 if i<rem else 0)
        for j in range(cnt):
            seed=TRAIN_SEED_BASE+i*10000+j
            if gated:
                q=gen_question_gated(wt,len(ex),seed)
                if q: npass+=1
                else: nfail+=1; q=gen_question(wt,len(ex),seed)
            else: q=gen_question(wt,len(ex),seed)
            ex.append(q)
    random.shuffle(ex)
    return ex,{"n_gated_pass":npass,"n_gated_fail":nfail,"gate_pass_rate":npass/max(npass+nfail,1)}

# --- 6. MODEL LOADING --- #
def build_model(model_path,device,dtype,lora_r=16,lora_alpha=32,sft_ckpt=None):
    print(f"  Loading base LLM: {model_path}",flush=True)
    llm=AutoModelForCausalLM.from_pretrained(model_path,torch_dtype=dtype,
        device_map={'':device},trust_remote_code=True)
    if sft_ckpt and os.path.isdir(sft_ckpt):
        print(f"  Loading SFT adapter: {sft_ckpt}",flush=True)
        model=PeftModel.from_pretrained(llm,sft_ckpt,is_trainable=True)
    else:
        lc=LoraConfig(task_type=TaskType.CAUSAL_LM,r=lora_r,lora_alpha=lora_alpha,
            lora_dropout=0.05,target_modules=["q_proj","k_proj","v_proj","o_proj"])
        model=get_peft_model(llm,lc)
    nt=sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"  Trainable params: {nt/1e6:.1f}M",flush=True)
    return model

# --- 7. ROLLOUT --- #
_TYPE_RE=re.compile(r'\b(sine|square|triangle|sawtooth)\b',re.IGNORECASE)
def rollout_classify(model,tokenizer,question,device,dtype,max_new_tokens=16,temperature=0.0):
    pt=build_prompt_text(question["samples_text"])
    enc=tokenizer(pt,add_special_tokens=False,return_tensors='pt',truncation=True,max_length=1024)
    ids=enc['input_ids'].to(device)
    with torch.no_grad():
        out=model.generate(ids,max_new_tokens=max_new_tokens,
            do_sample=temperature>0,temperature=max(temperature,1e-5),top_p=0.95,
            pad_token_id=tokenizer.pad_token_id if tokenizer.pad_token_id is not None else 0,
            eos_token_id=tokenizer.convert_tokens_to_ids(IM_END))
    gen=tokenizer.decode(out[0,ids.shape[1]:],skip_special_tokens=True).strip()
    m=_TYPE_RE.search(gen); return (m.group(1).lower() if m else None),gen

# --- 8. LOGPROB COMPUTATION (for GRPO PPO ratio) --- #
def compute_response_logprobs(model,tokenizer,prompt_text,response_text,device,dtype):
    pe=tokenizer(prompt_text,add_special_tokens=False,return_tensors='pt')
    fe=tokenizer(prompt_text+response_text,add_special_tokens=False,
                 return_tensors='pt',truncation=True,max_length=1024)
    ids=fe['input_ids'].to(device); am=fe['attention_mask'].to(device)
    pl=pe['input_ids'].shape[1]
    logits=model(input_ids=ids,attention_mask=am).logits[:,:-1,:]
    lps=F.log_softmax(logits.float(),dim=-1)
    tids=ids[:,1:]
    tlps=lps.gather(2,tids.unsqueeze(-1)).squeeze(-1)
    return tlps[0,pl-1:]

# --- 9. GRPO TRAINING STEP (continuous reward, classification) --- #
def grpo_train_step(model,tokenizer,optimizer,device,dtype,train_qs,
                    batch_prompts=2,group_size=8,max_new_tokens=16,
                    temperature=0.8,clip_eps=0.2,random_reward=False,rng=None):
    if rng is None: rng=np.random.default_rng()
    all_groups=[]; total_r=0.0; n_roll=0; total_std=0.0; n_nz=0
    for _ in range(batch_prompts):
        q=train_qs[int(rng.integers(0,len(train_qs)))]
        pt=build_prompt_text(q["samples_text"]); gr=[]
        for g in range(group_size):
            parsed,raw=rollout_classify(model,tokenizer,q,device,dtype,
                max_new_tokens=max_new_tokens,temperature=temperature)
            r=float(rng.uniform(0,1)) if random_reward else continuous_reward(q,parsed)
            resp=raw.strip() or (parsed or "unknown")
            if IM_END not in resp: resp=resp+IM_END
            gr.append({"response":resp,"reward":r,"parsed":parsed,"correct":check_correct(q,parsed)})
            total_r+=r; n_roll+=1
        if len(gr)<2: continue
        ra=np.array([x["reward"] for x in gr],dtype=np.float64)
        mr,sr=float(ra.mean()),float(ra.std())
        if sr>1e-8: n_nz+=1
        total_std+=sr
        adv=(ra-mr)/(sr+1e-8)
        old_lps=[]
        for x in gr:
            with torch.no_grad():
                lp=compute_response_logprobs(model,tokenizer,pt,x["response"],device,dtype)
            old_lps.append(lp.detach())
        all_groups.append((old_lps,adv,gr,pt))
    loss_total=torch.tensor(0.0,device=device); n_valid=0
    for old_lps,adv,gr,pt in all_groups:
        for idx,olp in enumerate(old_lps):
            if olp is None or len(olp)==0: continue
            nlp=compute_response_logprobs(model,tokenizer,pt,gr[idx]["response"],device,dtype)
            ml=min(len(nlp),len(olp))
            if ml==0: continue
            ratio=torch.exp(nlp[:ml]-olp[:ml])
            a=torch.tensor(adv[idx],device=device,dtype=torch.float32)
            loss=-torch.min(ratio*a,torch.clamp(ratio,1-clip_eps,1+clip_eps)*a).mean()
            loss_total=loss_total+loss; n_valid+=1
    if n_valid>0:
        loss_total=loss_total/n_valid
        optimizer.zero_grad(); loss_total.backward()
        torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad],1.0)
        optimizer.step()
    return (float(loss_total.item()) if n_valid>0 else 0.0,
            total_r/max(n_roll,1), total_std/max(len(all_groups),1), n_nz/max(len(all_groups),1))

def run_grpo(model,tokenizer,device,dtype,train_qs,n_steps,random_reward,label,
             out_dir,lr=1e-6,batch_prompts=2,group_size=8,max_new_tokens=16,
             temperature=0.8,clip_eps=0.2,seed=42):
    opt=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=lr)
    rng=np.random.default_rng(seed)
    losses=[];rewards=[];stds=[];nz_fracs=[];t0=time.time()
    for step in range(n_steps):
        loss,ar,astd,nzf=grpo_train_step(model,tokenizer,opt,device,dtype,train_qs,
            batch_prompts=batch_prompts,group_size=group_size,
            max_new_tokens=max_new_tokens,temperature=temperature,
            clip_eps=clip_eps,random_reward=random_reward,rng=rng)
        losses.append(loss);rewards.append(ar);stds.append(astd);nz_fracs.append(nzf)
        if (step+1)%5==0 or step==0:
            el=time.time()-t0; eta=el/(step+1)*(n_steps-step-1)
            print(f"    [{label}] step {step+1}/{n_steps} loss={loss:.6f} avgR={ar:.4f} "
                  f"std={astd:.4f} nzstd={nzf:.1%} ({el:.0f}s,ETA {eta:.0f}s)",flush=True)
        if (step+1)%20==0: model.save_pretrained(os.path.join(out_dir,f"step{step+1}"))
    model.save_pretrained(os.path.join(out_dir,f"step{n_steps}"))
    return losses,rewards,stds,nz_fracs

# --- 10. EVALUATION --- #
def evaluate_condition(model,tokenizer,qs,device,dtype,label,max_new_tokens=16):
    results=[];t0=time.time()
    for i,q in enumerate(qs):
        parsed,raw=rollout_classify(model,tokenizer,q,device,dtype,
            max_new_tokens=max_new_tokens,temperature=0.0)
        results.append({"qid":q["qid"],"task":q["task"],"waveform_type":q["waveform_type"],
            "correct":check_correct(q,parsed),"parsed":parsed,"gt":q["gt_value"],"raw_output":raw[:100]})
        if (i+1)%10==0:
            acc=sum(r["correct"] for r in results)/len(results)
            print(f"    [{label}] {i+1}/{len(qs)} acc={acc:.1%} ({time.time()-t0:.0f}s)",flush=True)
    return results

def eval_confusion_matrix(results):
    cm={gt:{pred:0 for pred in WAVEFORM_TYPES+["None"]} for gt in WAVEFORM_TYPES}
    for r in results:
        gt=r["waveform_type"];pred=r["parsed"] if r["parsed"] else "None"
        if pred not in cm[gt]: cm[gt][pred]=0
        cm[gt][pred]+=1
    pc={gt:(cm[gt][gt]/sum(cm[gt].values()) if sum(cm[gt].values())>0 else 0.0) for gt in WAVEFORM_TYPES}
    return {"confusion_matrix":cm,"per_class_accuracy":pc}

# --- 11. STATISTICS --- #
def mcnemar_test(ca,cb):
    a=np.array(ca,dtype=bool);b=np.array(cb,dtype=bool)
    n01=int(np.sum(~a&b));n10=int(np.sum(a&~b));nd=n01+n10
    if nd==0: return 0.0,1.0,0
    if nd<25:
        from scipy.stats import binom
        p=2*min(binom.cdf(min(n01,n10),nd,0.5),1-binom.cdf(min(n01,n10)-1,nd,0.5))
        return min(n01,n10),float(p),nd
    stat=(abs(n01-n10)-1)**2/(n01+n10)
    from scipy.stats import chi2
    return float(stat),float(1-chi2.cdf(stat,1)),nd

def bootstrap_ci_delta(ca,cb,n_boot=10000,seed=42):
    rng=np.random.default_rng(seed)
    a=np.array(ca,dtype=bool);b=np.array(cb,dtype=bool);n=len(a)
    deltas=[b[rng.integers(0,n,n)].mean()-a[rng.integers(0,n,n)].mean() for _ in range(n_boot)]
    deltas=np.array(deltas)
    return float(b.mean()-a.mean()),float(np.percentile(deltas,2.5)),float(np.percentile(deltas,97.5))

# --- 12. MAIN --- #
def main():
    p=argparse.ArgumentParser(description="CPU RL v6: GRPO + Continuous Reward")
    p.add_argument('--model_path',type=str,default=LLM_PATH)
    p.add_argument('--sft_ckpt',type=str,default=V5_SFT_CKPT)
    p.add_argument('--out_dir',type=str,
        default="/nas_train/app.e0031982/datasets/baize-vision/out/cpu_rl_v6_grpo")
    p.add_argument('--n_eval_per_type',type=int,default=25)
    p.add_argument('--n_grpo_steps',type=int,default=40)
    p.add_argument('--group_size',type=int,default=8)
    p.add_argument('--batch_prompts',type=int,default=2)
    p.add_argument('--n_train',type=int,default=200)
    p.add_argument('--lora_r',type=int,default=16)
    p.add_argument('--lr',type=float,default=1e-6)
    p.add_argument('--max_new_tokens',type=int,default=16)
    p.add_argument('--temperature',type=float,default=0.8)
    p.add_argument('--clip_eps',type=float,default=0.2)
    p.add_argument('--seed',type=int,default=20261109)
    p.add_argument('--use_v5_eval',action='store_true',default=True)
    p.add_argument('--skip_control',action='store_true')
    p.add_argument('--smoke',action='store_true')
    args=p.parse_args()
    if args.smoke:
        args.n_eval_per_type=5;args.n_grpo_steps=3;args.n_train=20
        args.group_size=4;args.batch_prompts=1
        print("="*60,"\n  SMOKE TEST MODE\n","="*60,flush=True)
    os.environ.setdefault("OMP_NUM_THREADS","16");torch.set_num_threads(16)
    device=torch.device('cpu');dtype=torch.float32
    os.makedirs(args.out_dir,exist_ok=True)
    random.seed(args.seed);np.random.seed(args.seed)

    # Phase 0: Eval set (same as v5 for direct comparison)
    print("="*60,"\n[Phase 0] Building eval set",flush=True)
    eval_qs=build_eval_set(n_per_type=args.n_eval_per_type,use_v5=args.use_v5_eval)
    with open(os.path.join(args.out_dir,"eval_questions.json"),'w') as f:
        json.dump([{k:v for k,v in q.items() if k not in("t","v","params")} for q in eval_qs],
                  f,indent=2,default=str)
    print(f"  {len(eval_qs)} eval questions",flush=True)

    # Phase 1: Gated training set
    print("="*60,"\n[Phase 1] Building TWO-GATE training set",flush=True)
    train_qs,gate_stats=build_train_set(args.n_train,gated=True)
    print(f"  {len(train_qs)} train Qs, gate pass: {gate_stats['gate_pass_rate']:.1%}",flush=True)

    tokenizer=AutoTokenizer.from_pretrained(args.model_path,trust_remote_code=True)
    if tokenizer.pad_token is None: tokenizer.pad_token=tokenizer.eos_token

    # Phase 2: Eval B (SFT from v5)
    print("="*60,"\n[Phase 2] Eval B (SFT from v5)",flush=True)
    model_b=build_model(args.model_path,device,dtype,lora_r=args.lora_r,sft_ckpt=args.sft_ckpt)
    res_b=evaluate_condition(model_b,tokenizer,eval_qs,device,dtype,"B-sft",args.max_new_tokens)
    acc_b=sum(r["correct"] for r in res_b)/len(res_b)
    cm_b=eval_confusion_matrix(res_b)
    print(f"  B={acc_b:.1%} per-class={cm_b['per_class_accuracy']}",flush=True)

    # Phase 3: GRPO with continuous reward (Condition C)
    print("="*60,"\n[Phase 3] GRPO-C (continuous reward treatment)",flush=True)
    print(f"  Reward: α={ALPHA}*R_exact + β={BETA}*R_shape",flush=True)
    model_c=build_model(args.model_path,device,dtype,lora_r=args.lora_r,sft_ckpt=args.sft_ckpt)
    ckpt_c=os.path.join(args.out_dir,"grpo_c");os.makedirs(ckpt_c,exist_ok=True)
    losses_c,rewards_c,stds_c,nzf_c=run_grpo(model_c,tokenizer,device,dtype,train_qs,
        args.n_grpo_steps,random_reward=False,label="GRPO-C",out_dir=ckpt_c,lr=args.lr,
        batch_prompts=args.batch_prompts,group_size=args.group_size,
        max_new_tokens=args.max_new_tokens,temperature=args.temperature,
        clip_eps=args.clip_eps,seed=args.seed)
    print(f"  GRPO-C done. avgR={rewards_c[-1]:.4f} std={stds_c[-1]:.4f} nzstd={nzf_c[-1]:.1%}",flush=True)
    res_c=evaluate_condition(model_c,tokenizer,eval_qs,device,dtype,"C-grpo",args.max_new_tokens)
    acc_c=sum(r["correct"] for r in res_c)/len(res_c)
    cm_c=eval_confusion_matrix(res_c)
    print(f"  C={acc_c:.1%} per-class={cm_c['per_class_accuracy']}",flush=True)
    del model_c

    # Phase 4: GRPO random reward (Condition D = CONTROL)
    res_d=[];acc_d=0.0;losses_d=[];rewards_d=[]
    if not args.skip_control:
        print("="*60,"\n[Phase 4] GRPO-D (random reward = CONTROL)",flush=True)
        model_d=build_model(args.model_path,device,dtype,lora_r=args.lora_r,sft_ckpt=args.sft_ckpt)
        ckpt_d=os.path.join(args.out_dir,"grpo_d");os.makedirs(ckpt_d,exist_ok=True)
        losses_d,rewards_d,_,_=run_grpo(model_d,tokenizer,device,dtype,train_qs,
            args.n_grpo_steps,random_reward=True,label="GRPO-D",out_dir=ckpt_d,lr=args.lr,
            batch_prompts=args.batch_prompts,group_size=args.group_size,
            max_new_tokens=args.max_new_tokens,temperature=args.temperature,
            clip_eps=args.clip_eps,seed=args.seed+1)
        res_d=evaluate_condition(model_d,tokenizer,eval_qs,device,dtype,"D-ctrl",args.max_new_tokens)
        acc_d=sum(r["correct"] for r in res_d)/len(res_d)
        print(f"  D={acc_d:.1%}",flush=True)
        del model_d

    # Phase 5: Statistics
    print("="*60,"\n[Phase 5] Statistics",flush=True)
    cb=[r["correct"] for r in res_b];cc=[r["correct"] for r in res_c]
    stats={"accuracy":{"B_sft":acc_b,"C_grpo_treatment":acc_c},
           "B_confusion_matrix":cm_b,"C_confusion_matrix":cm_c,
           "reward_config":{"alpha":ALPHA,"beta":BETA},
           "gate_stats":gate_stats,
           "grpo_stats":{"C_avg_std":float(np.mean(stds_c)),
                         "C_nonzero_std_frac":float(np.mean(nzf_c)),
                         "C_avg_reward_last10":float(np.mean(rewards_c[-10:]))}}
    if res_d:
        stats["accuracy"]["D_grpo_control"]=acc_d
    scb,pcb,ncb=mcnemar_test(cb,cc)
    ptcb,locb,hicb=bootstrap_ci_delta(cb,cc)
    stats["mcnemar_C_vs_B"]={"stat":scb,"p":pcb,"n_discordant":ncb}
    stats["bootstrap_C_vs_B"]={"point_delta":ptcb,"ci_lo":locb,"ci_hi":hicb}
    if res_d:
        cd=[r["correct"] for r in res_d]
        scd,pcd,ncd=mcnemar_test(cd,cc)
        ptcd,locd,hicd=bootstrap_ci_delta(cd,cc)
        stats["mcnemar_C_vs_D"]={"stat":scd,"p":pcd,"n_discordant":ncd}
        stats["bootstrap_C_vs_D"]={"point_delta":ptcd,"ci_lo":locd,"ci_hi":hicd}
    stats["cheat_rate"]={"train_seed":f"{TRAIN_SEED_BASE}+","eval_seed":f"{EVAL_SEED_BASE}+",
                         "overlap":0,"note":"disjoint RNG seeds -> no leakage"}
    sig=pcb<0.05 and locb>0
    verdict=("TREATMENT SIGNIFICANT" if sig else
             "TREATMENT NOT SIGNIFICANT" if acc_c>acc_b else "NO IMPROVEMENT")
    if res_d and acc_c>acc_d: verdict+=" | REWARD-DESIGN DRIVEN (C>D)"
    elif res_d: verdict+=" | NOT reward-design driven (C<=D)"
    stats["verdict"]=verdict

    print(f"\n{'='*60}\n  RESULTS SUMMARY (v6: GRPO + Continuous Reward)",flush=True)
    print(f"  B (SFT v5):        {acc_b:.1%}",flush=True)
    print(f"  C (GRPO cont):     {acc_c:.1%}",flush=True)
    if res_d: print(f"  D (GRPO random):   {acc_d:.1%}",flush=True)
    print(f"  B per-class: {cm_b['per_class_accuracy']}",flush=True)
    print(f"  C per-class: {cm_c['per_class_accuracy']}",flush=True)
    print(f"  McNemar C-vs-B: p={pcb:.4f} (n_disc={ncb})",flush=True)
    print(f"  Bootstrap C-B: {ptcb:+.1%} CI=[{locb:+.1%},{hicb:+.1%}]",flush=True)
    if res_d: print(f"  McNemar C-vs-D: p={pcd:.4f}",flush=True)
    print(f"  GRPO nonzero-std: {np.mean(nzf_c):.1%} (v2-v3 was <22%)",flush=True)
    print(f"  VERDICT: {verdict}",flush=True)

    out={"config":vars(args),"stats":stats,"results":{"B":res_b,"C":res_c},
         "training":{"C_losses":losses_c,"C_rewards":rewards_c,"C_stds":stds_c,"C_nz_std":nzf_c}}
    if res_d:
        out["results"]["D"]=res_d;out["training"]["D_losses"]=losses_d;out["training"]["D_rewards"]=rewards_d
    out_path=os.path.join(args.out_dir,"experiment_results.json")
    with open(out_path,'w') as f: json.dump(out,f,indent=2,default=str)
    print(f"\n  Full results -> {out_path}",flush=True)

if __name__=="__main__": main()
