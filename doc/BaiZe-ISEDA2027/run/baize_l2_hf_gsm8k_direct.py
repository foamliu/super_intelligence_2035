#!/usr/bin/env python3
"""
BaiZe 2B L2 GSM8K HF Direct Evaluation
Uses sglang env (transformers 5.18.0, pyarrow) — no lm_eval/sklearn dependency.
4-shot prompting (standard for GSM8K base model evaluation).
CPU only, nice 19, OMP_NUM_THREADS=4 — must not affect training.
"""
import argparse, json, os, re, sys, time
os.environ["CUDA_VISIBLE_DEVICES"] = ""
import pyarrow.ipc as ipc
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

GSM8K_ARROW = "/nas_train/app.e0031982/hf_cache/openai___gsm8k/main/0.0.0/740312add88f781978c0658806c59bc2815b9866/gsm8k-test.arrow"

FEW_SHOT = [
    {"q":"Janet's ducks lay 16 eggs per day. She eats three for breakfast every morning and bakes muffins for her friends every day with four. She sells the remainder at the farmers' market daily for $2 per fresh duck egg. How much in dollars does she make every day at the farmers' market?","a":"Janet sells 16 - 3 - 4 = 9 duck eggs a day.\nShe makes 9 * 2 = $18 every day at the farmers' market.\n#### 18"},
    {"q":"A robe takes 2 bolts of blue fiber and half that much white fiber. How many bolts in total does it take?","a":"It takes 2/2 = 1 bolt of white fiber.\nSo the total amount of bolts is 2 + 1 = 3 bolts.\n#### 3"},
    {"q":"Josh decides to try flipping a house. He buys a house for $80,000 and then puts in $50,000 in repairs. This increased the value of the house by 150%. How much profit did he make?","a":"The cost of the house and repairs came out to 80,000 + 50,000 = 130,000.\nHe increased the value by 80,000 * 1.5 = 120,000.\nThe new value is 120,000 + 80,000 = 200,000.\nProfit = 200,000 - 130,000 = 70,000.\n#### 70000"},
    {"q":"James decides to run 3 sprints 3 times a week. He runs 60 meters each sprint. How many total meters does he run a week?","a":"He sprints 3 * 3 = 9 times per week.\nSo he runs 9 * 60 = 540 meters per week.\n#### 540"},
]

def build_prompt(q):
    p = ""
    for ex in FEW_SHOT:
        p += f"Question: {ex['q']}\nAnswer: {ex['a']}\n\n"
    p += f"Question: {q}\nAnswer:"
    return p

def load_gsm8k(limit=None):
    with open(GSM8K_ARROW, "rb") as f:
        reader = ipc.open_stream(f)
        table = reader.read_all()
    df = table.to_pylist()
    return df[:limit] if limit else df

def extract_answer(text):
    m = re.search(r"####\s*([\d,]+)", text)
    if m: return int(m.group(1).replace(",", ""))
    m = re.search(r"(?:answer is|equals?)\s*\$?\s*([\d,]+)", text, re.I)
    if m: return int(m.group(1).replace(",", ""))
    nums = re.findall(r"\d+", text)
    return int(nums[-1]) if nums else None

def get_gt(ans):
    m = re.search(r"####\s*([\d,]+)", ans)
    return int(m.group(1).replace(",", "")) if m else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model_path", default="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/hf_iter_160000")
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--max_new_tokens", type=int, default=256)
    ap.add_argument("--outdir", default="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results/gguf_iter_160000_l2_hf_gsm8k_direct")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    print(f"[{time.strftime('%H:%M:%S')}] Loading GSM8K ({args.limit})...")
    problems = load_gsm8k(args.limit)
    print(f"  Loaded {len(problems)} problems")
    print(f"[{time.strftime('%H:%M:%S')}] Loading model...")
    tok = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(args.model_path, trust_remote_code=True, torch_dtype=torch.bfloat16)
    model.eval()
    print("  Model loaded (CPU, bfloat16)")
    results, correct, no_ans = [], 0, 0
    total = len(problems)
    for i, prob in enumerate(problems):
        q, gt = prob["question"], get_gt(prob["answer"])
        prompt = build_prompt(q)
        inp = tok(prompt, return_tensors="pt", truncation=True, max_length=2048)
        t0 = time.time()
        with torch.no_grad():
            out = model.generate(**inp, max_new_tokens=args.max_new_tokens, do_sample=False, pad_token_id=tok.eos_token_id)
        dt = time.time() - t0
        gen = tok.decode(out[0][inp["input_ids"].shape[1]:], skip_special_tokens=True)
        pred = extract_answer(gen)
        ok = (pred is not None and pred == gt)
        if ok: correct += 1
        if pred is None: no_ans += 1
        results.append({"idx": i, "gt": gt, "pred": pred, "ok": ok, "dt": round(dt, 2), "gen": gen[:200]})
        st = "✅" if ok else ("❌" if pred is not None else "⬜")
        print(f"  [{i+1}/{total}] {st} gt={gt} pred={pred} ({dt:.1f}s) | acc={correct}/{i+1}={correct/(i+1)*100:.1f}%")
    acc = correct / total if total else 0
    print(f"\n{'='*60}")
    print(f"[{time.strftime('%H:%M:%S')}] GSM8K acc={correct}/{total}={acc*100:.1f}% (no_ans={no_ans})")
    print(f"{'='*60}")
    summary = {"model": args.model_path, "task": "gsm8k", "limit": args.limit, "accuracy": acc,
               "correct": correct, "total": total, "no_answer": no_ans, "prompting": "4-shot",
               "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "details": results}
    with open(os.path.join(args.outdir, "results.json"), "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Saved to {args.outdir}/results.json")

if __name__ == "__main__":
    main()
