#!/usr/bin/env python3
"""Quick GSM8K evaluation with HF transformers (10 samples, hardcoded).
CPU only, low threads, nice 19 — must not affect training."""
import os, sys, time, json, re, torch
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["OMP_NUM_THREADS"] = "4"
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_PATH = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/hf_iter_160000"
N_SAMPLES = 10
MAX_NEW_TOKENS = 256

GSM8K = [
    {"q":"Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?","a":"#### 72"},
    {"q":"Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. How much did she earn?","a":"#### 10"},
    {"q":"Betty is saving money for a new wallet which costs $100. Betty has only half of the money she needs. Her parents decided to give her $15 for that purpose, and her grandparents twice as much as her parents. How much more money does Betty need?","a":"#### 5"},
    {"q":"Julie is reading a 120-page book. Yesterday, she was able to read 12 pages and today, she read twice as many pages as yesterday. If she wants to read half of the remaining pages tomorrow, how many pages will she read tomorrow?","a":"#### 42"},
    {"q":"James writes a 3-page letter to 2 different friends twice a week. How many pages does he write a year?","a":"#### 624"},
    {"q":"Mark has a garden with flowers. A tenth of the plants were yellow, two-thirds were orange and the rest were red. If there are 90 plants in total, how many red flowers does Mark have?","a":"#### 21"},
    {"q":"During one day, there are 4 boat trips through the lake. The first boat had 7 people, the second 10, the third 9, and the fourth 11. How many more people can fit in total?","a":"#### 3"},
    {"q":"Toulouse has twice as many sheep as Charleston. Charleston has 4 times as many sheep as Seattle. How many sheep do they have together if Seattle has 20 sheep?","a":"#### 260"},
    {"q":"A new program had 60 downloads in the first month. The second month had three times as many, then reduced by 30% in the third month. How many downloads total over three months?","a":"#### 366"},
    {"q":"Toula bought 3 dozen donuts at $68/dozen, 2 dozen mini croissants at $55/dozen, and 6 dozen mini cupcakes at $16/dozen. What was the total cost?","a":"#### 410"},
]

def extract_num(text):
    m = re.findall(r'[-+]?\d+', text)
    return m[-1] if m else None

def extract_gold(s):
    m = re.findall(r'[-+]?\d+', s)
    return m[-1] if m else None

print(f"[{time.strftime('%H:%M:%S')}] Loading model (bfloat16, CPU)...", flush=True)
tok = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
t0 = time.time()
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, dtype=torch.bfloat16, trust_remote_code=True)
model.eval()
print(f"[{time.strftime('%H:%M:%S')}] Loaded in {time.time()-t0:.1f}s, {type(model).__name__}", flush=True)

correct = 0
results = []
for i in range(N_SAMPLES):
    gold = extract_gold(GSM8K[i]["a"])
    prompt = f"Question: {GSM8K[i]['q']}\nAnswer:"
    inputs = tok(prompt, return_tensors="pt")
    il = inputs.input_ids.shape[1]
    t0 = time.time()
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=MAX_NEW_TOKENS, do_sample=False,
            pad_token_id=tok.pad_token_id or tok.eos_token_id)
    gt = time.time() - t0
    text = tok.decode(out[0][il:], skip_special_tokens=True)
    pred = extract_num(text)
    ok = pred == gold if pred and gold else False
    if ok: correct += 1
    results.append({"idx":i,"gold":gold,"pred":pred,"ok":ok,"time":round(gt,1),"out":text[:200]})
    print(f"[{i+1}/{N_SAMPLES}] gold={gold} pred={pred} ok={ok} t={gt:.1f}s | {text[:120]}", flush=True)

print(f"\nGSM8K HF Results: {correct}/{N_SAMPLES} = {correct/N_SAMPLES*100:.1f}%", flush=True)
with open("/tmp/hf_gsm8k_160k_results.json","w") as f:
    json.dump({"n":N_SAMPLES,"correct":correct,"acc":correct/N_SAMPLES,"backend":"hf_bf16_cpu","results":results},f,indent=2)
print(f"[{time.strftime('%H:%M:%S')}] Done. Saved to /tmp/hf_gsm8k_160k_results.json", flush=True)
