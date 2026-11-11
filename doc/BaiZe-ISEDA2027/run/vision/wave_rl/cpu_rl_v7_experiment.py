#!/usr/bin/env python3
"""cpu_rl_v7_experiment.py - CPU RL Waveform Experiment v7: Two-direction sweep.

WHY v7 (building on v6, incorporating research daily 2026-11-11 suggestions):
  v6 (GRPO continuous reward): B=35% -> C=40% -> D=36%, p=0.267 NOT significant.
  BUT: nonzero-std = 93.75% (v2-v3 was <22%) => continuous reward SOLVED the
  variance problem. The accuracy gain just wasn't large enough to be significant.

  Research daily 2026-11-11 (arXiv 2611.12728) suggests two improvements:
    A. v7 Process Reward: R = R_outcome + lambda*R_process
       - outcome = continuous shape-similarity (from v6)
       - process = information gain from two-phase prediction:
         Phase 1: model sees first 8/16 sample points -> initial prediction (entropy H1)
         Phase 2: model sees all 16 sample points -> final prediction (entropy H2)
         R_process = (H1 - H2) * sign(correct)
       - lambda sweep {0.03, 0.1, 0.2} x 3 seeds
    B. v7b LoRA Capacity Probe: r in {8, 16, 32} x 3 seeds
       - Same v6 GRPO (continuous reward, outcome-only) but different LoRA rank
       - Purpose: disentangle capacity insufficient from reward design ineffective

PRE-REGISTERED JUDGMENT (written BEFORE running, 2026-11-11):
  Baseline = v6 C (outcome-only GRPO, 40%, seed 20261109)
  v7: For each lambda: 3 seeds, report mean+/-sd + support@k
    PASS: mean improvement > 1 sd AND 3 seeds same direction (all positive)
  v7b: For each r: 3 seeds, report mean+/-sd + support@k
    If r=32 shows no improvement over r=16 -> capacity NOT the bottleneck

Author: vision (research daily execution). License: project-internal.
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
_WT_IDX = {wt: i for i, wt in enumerate(WAVEFORM_TYPES)}
N_SAMPLE_POINTS = 16
N_PERIODS = 2.0
EVAL_SEED_BASE = 995100
TRAIN_SEED_BASE = 20261111
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

# ============================================================================ #
#  1. WAVEFORM GENERATORS + CANONICAL TEMPLATES (same as v6)
# ============================================================================ #
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

# ============================================================================ #
#  2. SHAPE SIMILARITY + TWO-GATE + CONTINUOUS REWARD (same as v6)
# ============================================================================ #
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

# ============================================================================ #
#  3. PROMPT FORMATTING (same as v6)
# ============================================================================ #
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

# ============================================================================ #
#  4. DATA GENERATION (same as v6)
# ============================================================================ #
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

def build_eval_set(n_per_type=12,use_v5=True):
    if use_v5 and os.path.exists(V5_EVAL_QUESTIONS):
        with open(V5_EVAL_QUESTIONS) as f: v5qs=json.load(f)
        qs=[]
        for q in v5qs:
            wt=q["waveform_type"]; seed=EVAL_SEED_BASE+q["qid"]*100+_WT_IDX.get(wt,0)
            rng=np.random.default_rng(seed); t,v,p=gen_waveform(wt,rng)
            qs.append({"qid":q["qid"],"task":"type_classification","waveform_type":wt,
                       "gt_value":wt,"measure_type":"type_classification",
                       "samples_text":format_samples(t,v),"t":t.tolist(),"v":v.tolist(),"params":p})
        return qs[:n_per_type*len(WAVEFORM_TYPES)]
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

# ============================================================================ #
#  5. MODEL LOADING
# ============================================================================ #
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
    print(f"  Trainable params: {nt/1e6:.1f}M (LoRA r={lora_r})",flush=True)
    return model

def build_model_with_r(model_path,device,dtype,lora_r,sft_ckpt=None):
    """Build model with a SPECIFIC LoRA rank.
    If r=16 and SFT exists: load SFT directly.
    If r!=16 and SFT exists: merge SFT into base, then apply fresh LoRA with target r.
    If no SFT: fresh LoRA with target r."""
    lora_alpha=lora_r*2
    if lora_r==16 and sft_ckpt and os.path.isdir(sft_ckpt):
        return build_model(model_path,device,dtype,lora_r=16,sft_ckpt=sft_ckpt)
    if sft_ckpt and os.path.isdir(sft_ckpt):
        print(f"  Loading base LLM: {model_path}",flush=True)
        llm=AutoModelForCausalLM.from_pretrained(model_path,torch_dtype=dtype,
            device_map={'':device},trust_remote_code=True)
        print(f"  Loading SFT adapter (r=16) and merging: {sft_ckpt}",flush=True)
        peft_model=PeftModel.from_pretrained(llm,sft_ckpt,is_trainable=False)
        merged=peft_model.merge_and_unload()
        print(f"  Applying fresh LoRA with r={lora_r}",flush=True)
        lc=LoraConfig(task_type=TaskType.CAUSAL_LM,r=lora_r,lora_alpha=lora_alpha,
            lora_dropout=0.05,target_modules=["q_proj","k_proj","v_proj","o_proj"])
        model=get_peft_model(merged,lc)
    else:
        print(f"  Loading base LLM: {model_path} (fresh LoRA r={lora_r})",flush=True)
        llm=AutoModelForCausalLM.from_pretrained(model_path,torch_dtype=dtype,
            device_map={'':device},trust_remote_code=True)
        lc=LoraConfig(task_type=TaskType.CAUSAL_LM,r=lora_r,lora_alpha=lora_alpha,
            lora_dropout=0.05,target_modules=["q_proj","k_proj","v_proj","o_proj"])
        model=get_peft_model(llm,lc)
    nt=sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"  Trainable params: {nt/1e6:.1f}M (LoRA r={lora_r}, alpha={lora_alpha})",flush=True)
    return model

# ============================================================================ #
#  6. ROLLOUT (standard + two-phase) + TYPE ENTROPY
# ============================================================================ #
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

def _get_type_token_ids(tokenizer):
    """Get the first token ID for each waveform type word."""
    ids={}
    for wt in WAVEFORM_TYPES:
        for variant in [f" {wt}",f"{wt}",f" {wt}\n",f" {wt} "]:
            toks=tokenizer.encode(variant,add_special_tokens=False)
            if toks:
                ids[wt]=toks[0]; break
    return ids

def compute_type_entropy(model,tokenizer,prompt_text,type_token_ids,device,dtype):
    """Compute entropy over the 4 type tokens at the first generation position."""
    enc=tokenizer(prompt_text,add_special_tokens=False,return_tensors='pt',truncation=True,max_length=1024)
    ids=enc['input_ids'].to(device)
    with torch.no_grad():
        logits=model(input_ids=ids).logits[0,-1,:].float()
    type_logits=[]
    for wt in WAVEFORM_TYPES:
        tid=type_token_ids.get(wt)
        type_logits.append(logits[tid].item() if tid is not None else 0.0)
    probs=F.softmax(torch.tensor(type_logits),dim=0)
    entropy=float(-(probs*torch.log(probs+1e-10)).sum().item())
    return entropy,float(probs.max().item()),probs.tolist()

def rollout_two_phase(model,tokenizer,question,device,dtype,type_token_ids,
                      max_new_tokens=16,temperature=0.8):
    """Two-phase rollout for process reward.
    Phase 1: first 8/16 sample points -> initial prediction + entropy H1
    Phase 2: all 16 sample points -> final prediction + entropy H2"""
    t=np.array(question["t"]); v=np.array(question["v"])
    half=N_SAMPLE_POINTS//2
    samples_p1=format_samples(t[:half],v[:half])
    prompt_p1=build_prompt_text(samples_p1)
    with torch.no_grad():
        enc1=tokenizer(prompt_p1,add_special_tokens=False,return_tensors='pt',truncation=True,max_length=1024)
        ids1=enc1['input_ids'].to(device)
        out1=model.generate(ids1,max_new_tokens=max_new_tokens,
            do_sample=temperature>0,temperature=max(temperature,1e-5),top_p=0.95,
            pad_token_id=tokenizer.pad_token_id if tokenizer.pad_token_id is not None else 0,
            eos_token_id=tokenizer.convert_tokens_to_ids(IM_END))
    gen1=tokenizer.decode(out1[0,ids1.shape[1]:],skip_special_tokens=True).strip()
    m1=_TYPE_RE.search(gen1)
    parsed1=m1.group(1).lower() if m1 else None
    H1,_,_=compute_type_entropy(model,tokenizer,prompt_p1,type_token_ids,device,dtype)
    parsed2,gen2=rollout_classify(model,tokenizer,question,device,dtype,
        max_new_tokens=max_new_tokens,temperature=temperature)
    prompt_p2=build_prompt_text(question["samples_text"])
    H2,_,_=compute_type_entropy(model,tokenizer,prompt_p2,type_token_ids,device,dtype)
    correct=check_correct(question,parsed2)
    return parsed2,gen2,H1,H2,correct

def process_reward(question,parsed_type,H1,H2,correct,lambda_process):
    """R = R_outcome + lambda * R_process"""
    r_outcome=continuous_reward(question,parsed_type)
    info_gain=H1-H2
    sign=1.0 if correct else -1.0
    r_process=info_gain*sign
    return r_outcome+lambda_process*r_process, r_outcome, r_process

# ============================================================================ #
#  7. LOGPROB COMPUTATION (for GRPO PPO ratio)
# ============================================================================ #
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

# ============================================================================ #
#  8. GRPO TRAINING (outcome-only and process-reward variants)
# ============================================================================ #
def grpo_train_step_outcome(model,tokenizer,optimizer,device,dtype,train_qs,
                     batch_prompts=2,group_size=4,max_new_tokens=16,
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

def grpo_train_step_process(model,tokenizer,optimizer,device,dtype,train_qs,type_token_ids,
                     lambda_process=0.1,batch_prompts=2,group_size=4,max_new_tokens=16,
                     temperature=0.8,clip_eps=0.2,rng=None):
    if rng is None: rng=np.random.default_rng()
    all_groups=[]; total_r=0.0; n_roll=0; total_std=0.0; n_nz=0
    total_r_out=0.0; total_r_proc=0.0
    for _ in range(batch_prompts):
        q=train_qs[int(rng.integers(0,len(train_qs)))]
        pt=build_prompt_text(q["samples_text"]); gr=[]
        for g in range(group_size):
            parsed,raw,H1,H2,correct=rollout_two_phase(model,tokenizer,q,device,dtype,
                type_token_ids,max_new_tokens=max_new_tokens,temperature=temperature)
            r,r_out,r_proc=process_reward(q,parsed,H1,H2,correct,lambda_process)
            resp=raw.strip() or (parsed or "unknown")
            if IM_END not in resp: resp=resp+IM_END
            gr.append({"response":resp,"reward":r,"parsed":parsed,"correct":correct})
            total_r+=r; total_r_out+=r_out; total_r_proc+=r_proc; n_roll+=1
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
            total_r/max(n_roll,1), total_std/max(len(all_groups),1), n_nz/max(len(all_groups),1),
            total_r_out/max(n_roll,1), total_r_proc/max(n_roll,1))

def run_grpo(model,tokenizer,device,dtype,train_qs,n_steps,label,
             out_dir,mode="outcome",type_token_ids=None,lambda_process=0.1,
             lr=1e-6,batch_prompts=2,group_size=4,max_new_tokens=16,
             temperature=0.8,clip_eps=0.2,seed=42):
    opt=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=lr)
    rng=np.random.default_rng(seed)
    losses=[];rewards=[];stds=[];nz_fracs=[];r_outs=[];r_procs=[];t0=time.time()
    for step in range(n_steps):
        if mode=="process":
            loss,ar,astd,nzf,ar_out,ar_proc=grpo_train_step_process(
                model,tokenizer,opt,device,dtype,train_qs,type_token_ids,
                lambda_process=lambda_process,batch_prompts=batch_prompts,
                group_size=group_size,max_new_tokens=max_new_tokens,
                temperature=temperature,clip_eps=clip_eps,rng=rng)
            r_outs.append(ar_out); r_procs.append(ar_proc)
        else:
            loss,ar,astd,nzf=grpo_train_step_outcome(
                model,tokenizer,opt,device,dtype,train_qs,
                batch_prompts=batch_prompts,group_size=group_size,
                max_new_tokens=max_new_tokens,temperature=temperature,
                clip_eps=clip_eps,random_reward=False,rng=rng)
        losses.append(loss);rewards.append(ar);stds.append(astd);nz_fracs.append(nzf)
        if (step+1)%5==0 or step==0:
            el=time.time()-t0; eta=el/(step+1)*(n_steps-step-1)
            extra=f" r_out={np.mean(r_outs[-5:]):.3f} r_proc={np.mean(r_procs[-5:]):.3f}" if mode=="process" and r_outs else ""
            print(f"    [{label}] step {step+1}/{n_steps} loss={loss:.4f} r={ar:.3f} "
                  f"std={astd:.3f} nz={nzf:.0%} {extra} ({el:.0f}s ETA {eta:.0f}s)",flush=True)
    model.save_pretrained(os.path.join(out_dir,f"step{n_steps}"))
    return losses,rewards,stds,nz_fracs,r_outs,r_procs

# ============================================================================ #
#  9. EVALUATION + STATISTICS
# ============================================================================ #
def evaluate_condition(model,tokenizer,qs,device,dtype,label,max_new_tokens=16):
    results=[];t0=time.time()
    for i,q in enumerate(qs):
        parsed,raw=rollout_classify(model,tokenizer,q,device,dtype,
            max_new_tokens=max_new_tokens,temperature=0.0)
        results.append({"qid":q["qid"],"task":q["task"],"waveform_type":q["waveform_type"],
            "correct":check_correct(q,parsed),"parsed":parsed,"gt":q["gt_value"],"raw_output":raw[:100]})
        if (i+1)%12==0:
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

# ============================================================================ #
#  10. MAIN
# ============================================================================ #
def main():
    p=argparse.ArgumentParser(description="CPU RL v7: Process Reward + LoRA Probe")
    p.add_argument('--mode',type=str,default='process_reward',
                   choices=['process_reward','lora_probe','smoke'])
    p.add_argument('--model_path',type=str,default=LLM_PATH)
    p.add_argument('--sft_ckpt',type=str,default=V5_SFT_CKPT)
    p.add_argument('--out_dir',type=str,required=True)
    p.add_argument('--n_eval_per_type',type=int,default=12)
    p.add_argument('--n_grpo_steps',type=int,default=15)
    p.add_argument('--group_size',type=int,default=4)
    p.add_argument('--batch_prompts',type=int,default=2)
    p.add_argument('--n_train',type=int,default=100)
    p.add_argument('--lora_r',type=int,default=16)
    p.add_argument('--lambda_process',type=float,default=0.1)
    p.add_argument('--lr',type=float,default=1e-6)
    p.add_argument('--max_new_tokens',type=int,default=16)
    p.add_argument('--temperature',type=float,default=0.8)
    p.add_argument('--clip_eps',type=float,default=0.2)
    p.add_argument('--seed',type=int,default=20261111)
    p.add_argument('--use_v5_eval',action='store_true',default=True)
    p.add_argument('--skip_baseline_eval',action='store_true')
    args=p.parse_args()

    if args.mode=='smoke':
        args.n_eval_per_type=3;args.n_grpo_steps=2;args.n_train=12
        args.group_size=2;args.batch_prompts=1
        print("="*60,"\n  SMOKE TEST MODE\n","="*60,flush=True)

    os.environ.setdefault("OMP_NUM_THREADS","16");torch.set_num_threads(16)
    device=torch.device('cpu');dtype=torch.float32
    os.makedirs(args.out_dir,exist_ok=True)
    random.seed(args.seed);np.random.seed(args.seed)
    print(f"  CPU threads=16, mode={args.mode}, seed={args.seed}",flush=True)
    if args.mode=='process_reward':
        print(f"  lambda_process={args.lambda_process}",flush=True)
    if args.mode=='lora_probe':
        print(f"  lora_r={args.lora_r}",flush=True)

    print("="*60,"\n[Phase 0] Building eval set",flush=True)
    eval_qs=build_eval_set(n_per_type=args.n_eval_per_type,use_v5=args.use_v5_eval)
    with open(os.path.join(args.out_dir,"eval_questions.json"),'w') as f:
        json.dump([{k:v for k,v in q.items() if k not in("t","v","params")} for q in eval_qs],
                  f,indent=2,default=str)
    print(f"  {len(eval_qs)} eval questions",flush=True)

    print("="*60,"\n[Phase 1] Building TWO-GATE training set",flush=True)
    train_qs,gate_stats=build_train_set(args.n_train,gated=True)
    print(f"  {len(train_qs)} train Qs, gate pass: {gate_stats['gate_pass_rate']:.1%}",flush=True)

    tokenizer=AutoTokenizer.from_pretrained(args.model_path,trust_remote_code=True)
    if tokenizer.pad_token is None: tokenizer.pad_token=tokenizer.eos_token
    type_token_ids=_get_type_token_ids(tokenizer)
    print(f"  Type token IDs: {type_token_ids}",flush=True)

    res_b=None;acc_b=None;cm_b=None
    if not args.skip_baseline_eval:
        print("="*60,"\n[Phase 2] Eval B (SFT from v5)",flush=True)
        model_b=build_model(args.model_path,device,dtype,lora_r=16,sft_ckpt=args.sft_ckpt)
        res_b=evaluate_condition(model_b,tokenizer,eval_qs,device,dtype,"B-sft",args.max_new_tokens)
        acc_b=sum(r["correct"] for r in res_b)/len(res_b)
        cm_b=eval_confusion_matrix(res_b)
        print(f"  B={acc_b:.1%} per-class={cm_b['per_class_accuracy']}",flush=True)
        del model_b; import gc; gc.collect()
    else:
        print("="*60,"\n[Phase 2] Skipping B eval (reuse v6 B=35%)",flush=True)
        acc_b=0.35

    mode_str="process" if args.mode=="process_reward" else "outcome"
    print("="*60,f"\n[Phase 3] GRPO training (mode={mode_str}, seed={args.seed})",flush=True)
    if args.mode=='lora_probe':
        model_c=build_model_with_r(args.model_path,device,dtype,lora_r=args.lora_r,sft_ckpt=args.sft_ckpt)
    else:
        model_c=build_model(args.model_path,device,dtype,lora_r=16,sft_ckpt=args.sft_ckpt)
    ckpt_c=os.path.join(args.out_dir,"grpo_c");os.makedirs(ckpt_c,exist_ok=True)
    losses_c,rewards_c,stds_c,nzf_c,r_outs_c,r_procs_c=run_grpo(
        model_c,tokenizer,device,dtype,train_qs,args.n_grpo_steps,
        label=f"GRPO-C ({mode_str})",out_dir=ckpt_c,mode=mode_str,
        type_token_ids=type_token_ids,lambda_process=args.lambda_process,
        lr=args.lr,batch_prompts=args.batch_prompts,group_size=args.group_size,
        max_new_tokens=args.max_new_tokens,temperature=args.temperature,
        clip_eps=args.clip_eps,seed=args.seed)

    print("="*60,"\n[Phase 4] Eval C (after GRPO)",flush=True)
    res_c=evaluate_condition(model_c,tokenizer,eval_qs,device,dtype,"C-grpo",args.max_new_tokens)
    acc_c=sum(r["correct"] for r in res_c)/len(res_c)
    cm_c=eval_confusion_matrix(res_c)
    print(f"  C={acc_c:.1%} per-class={cm_c['per_class_accuracy']}",flush=True)
    del model_c; import gc; gc.collect()

    print("="*60,"\n[Phase 5] Statistics",flush=True)
    stats={"mode":args.mode,"seed":args.seed,
           "accuracy":{"B_sft":acc_b,"C_grpo":acc_c},
           "C_confusion_matrix":cm_c,
           "reward_config":{"alpha":ALPHA,"beta":BETA,
                            "lambda_process":args.lambda_process if args.mode=="process_reward" else 0.0},
           "lora_config":{"r":args.lora_r,"alpha":args.lora_r*2},
           "gate_stats":gate_stats,
           "grpo_stats":{"C_avg_std":float(np.mean(stds_c)),
                         "C_nonzero_std_frac":float(np.mean(nzf_c)),
                         "C_avg_reward_last5":float(np.mean(rewards_c[-5:]))}}
    if args.mode=="process_reward" and r_outs_c:
        stats["grpo_stats"]["C_avg_r_outcome_last5"]=float(np.mean(r_outs_c[-5:]))
        stats["grpo_stats"]["C_avg_r_process_last5"]=float(np.mean(r_procs_c[-5:]))

    if res_b:
        cb=[r["correct"] for r in res_b];cc=[r["correct"] for r in res_c]
        scb,pcb,ncb=mcnemar_test(cb,cc)
        ptcb,locb,hicb=bootstrap_ci_delta(cb,cc)
        stats["mcnemar_C_vs_B"]={"stat":scb,"p":pcb,"n_discordant":ncb}
        stats["bootstrap_C_vs_B"]={"point_delta":ptcb,"ci_lo":locb,"ci_hi":hicb}
        stats["B_confusion_matrix"]=cm_b
    else:
        stats["note"]="B baseline reused from v6 (35%), no per-sample comparison"

    stats["cheat_rate"]={"train_seed":f"{TRAIN_SEED_BASE}+","eval_seed":f"{EVAL_SEED_BASE}+",
                         "overlap":0,"note":"disjoint RNG seeds -> no leakage"}

    if res_b:
        sig=pcb<0.05 and locb>0
        verdict=("TREATMENT SIGNIFICANT" if sig else
                 "TREATMENT NOT SIGNIFICANT" if acc_c>acc_b else "NO IMPROVEMENT")
    else:
        verdict="IMPROVEMENT" if acc_c>acc_b else ("NO IMPROVEMENT" if acc_c<acc_b else "NO CHANGE")
    stats["verdict"]=verdict

    print(f"\n{'='*60}\n  RESULTS SUMMARY (v7: {args.mode}, seed={args.seed})",flush=True)
    print(f"  B (SFT v5):        {acc_b:.1%}",flush=True)
    print(f"  C (GRPO {mode_str}):  {acc_c:.1%}",flush=True)
    if res_b:
        print(f"  McNemar C-vs-B: p={pcb:.4f} (n_disc={ncb})",flush=True)
        print(f"  Bootstrap C-B: {ptcb:+.1%} CI=[{locb:+.1%},{hicb:+.1%}]",flush=True)
    print(f"  GRPO nonzero-std: {np.mean(nzf_c):.1%}",flush=True)
    if args.mode=="process_reward" and r_outs_c:
        print(f"  Avg R_outcome (last5): {np.mean(r_outs_c[-5:]):.4f}",flush=True)
        print(f"  Avg R_process (last5): {np.mean(r_procs_c[-5:]):.4f}",flush=True)
    print(f"  VERDICT: {verdict}",flush=True)

    out={"config":vars(args),"stats":stats,"results":{"B":res_b,"C":res_c},
         "training":{"C_losses":losses_c,"C_rewards":rewards_c,"C_stds":stds_c,"C_nz_std":nzf_c}}
    if r_outs_c: out["training"]["C_r_outcomes"]=r_outs_c
    if r_procs_c: out["training"]["C_r_processes"]=r_procs_c
    out_path=os.path.join(args.out_dir,"experiment_results.json")
    with open(out_path,'w') as f: json.dump(out,f,indent=2,default=str)
    print(f"\n  Full results -> {out_path}",flush=True)

if __name__=="__main__": main()
