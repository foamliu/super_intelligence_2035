#!/usr/bin/env python3
"""
BaiZe 2B L2 MATH HF Direct Evaluation
Evaluates MATH-500 with HF transformers (CPU, bfloat16).
4-shot prompting, extract \\boxed{} answers.
Uses sglang env (transformers 5.18.0, pyarrow). CPU only, nice 19.
"""
import argparse, json, os, re, time
os.environ["CUDA_VISIBLE_DEVICES"] = ""
import pyarrow.ipc as ipc
import torch
torch.set_num_threads(4)
from transformers import AutoModelForCausalLM, AutoTokenizer

MATH500_ARROW = "/nas_train/app.e0031982/hf_cache/HuggingFaceH4___math-500/default/0.0.0/6e4ed1a2a79af7d8630a6b768ec859cb5af4d3be/math-500-test.arrow"

FEW_SHOT = [
    {"problem": "What is $\\sqrt[3]{8}$?", "solution": "We have $\\sqrt[3]{8} = 2$ since $2^3 = 8$. The answer is $\\boxed{2}$."},
    {"problem": "Compute $(-3) + 5$.", "solution": "$(-3) + 5 = 2$. The answer is $\\boxed{2}$."},
    {"problem": "What is $10 - 4 \\times 2$?", "solution": "$4 \\times 2 = 8$. $10 - 8 = 2$. The answer is $\\boxed{2}$."},
    {"problem": "If $f(x) = 2x + 1$, what is $f(3)$?", "solution": "$f(3) = 2(3) + 1 = 7$. The answer is $\\boxed{7}$."},
]

def load_math500(limit=None):
    with open(MATH500_ARROW, "rb") as f:
        reader = ipc.open_stream(f)
        table = reader.read_all()
    rows = table.to_pylist()
    return rows[:limit] if limit else rows

def build_prompt(problem):
    prompt = ""
    for ex in FEW_SHOT:
        prompt += f"Problem: {ex['problem']}\nSolution: {ex['solution']}\n\n"
    prompt += f"Problem: {problem}\nSolution:"
    return prompt

def extract_boxed(text):
    idx = text.rfind("\\boxed{")
    if idx < 0:
        m = re.search(r"answer is\s*:?\s*(.+?)(?:\.|\n|$)", text, re.I)
        if m: return m.group(1).strip().strip(".")
        nums = re.findall(r"-?\d+(?:\.\d+)?", text)
        return nums[-1] if nums else None
    start = idx + len("\\boxed{")
    depth = 1
    end = start
    while end < len(text) and depth > 0:
        if text[end] == '{': depth += 1
        elif text[end] == '}': depth -= 1
        if depth == 0: break
        end += 1
    return text[start:end].strip() if depth == 0 else None

def normalize_answer(ans):
    if ans is None: return None
    ans = str(ans).strip()
    ans = ans.replace("\\,", "").replace("\\ ", "").replace(" ", "")
    ans = ans.replace("\\text{", "").replace("}", "")
    ans = ans.replace("\\left", "").replace("\\right", "")
    ans = ans.replace("\\dfrac", "\\frac")
    try:
        f = float(ans)
        if f == int(f): return str(int(f))
        return str(f)
    except ValueError: pass
    return ans

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model_path", default="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/hf_iter_160000")
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--max_new_tokens", type=int, default=256)
    ap.add_argument("--outdir", default="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results/gguf_iter_160000_l2_hf_math_direct")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    print(f"[{time.strftime('%H:%M:%S')}] MATH-500 HF Direct Eval limit={args.limit}")
    print(f"[{time.strftime('%H:%M:%S')}] Loading model from {args.model_path}...")
    tok = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(args.model_path, trust_remote_code=True, torch_dtype=torch.bfloat16)
    model.eval()
    print(f"  Model loaded (CPU, bfloat16, threads={torch.get_num_threads()})")
    problems = load_math500(args.limit)
    print(f"  Loaded {len(problems)} problems")
    results, correct, no_ans = [], 0, 0
    total = len(problems)
    for i, prob in enumerate(problems):
        q, gt = prob["problem"], prob["answer"]
        prompt = build_prompt(q)
        inp = tok(prompt, return_tensors="pt", truncation=True, max_length=2048)
        t0 = time.time()
        with torch.no_grad():
            out = model.generate(**inp, max_new_tokens=args.max_new_tokens, do_sample=False, pad_token_id=tok.eos_token_id)
        dt = time.time() - t0
        gen = tok.decode(out[0][inp["input_ids"].shape[1]:], skip_special_tokens=True)
        pred = extract_boxed(gen)
        pred_norm = normalize_answer(pred)
        gt_norm = normalize_answer(gt)
        ok = (pred_norm is not None and pred_norm == gt_norm)
        if ok: correct += 1
        if pred is None: no_ans += 1
        results.append({"idx": i, "subject": prob.get("subject", ""), "level": prob.get("level", ""), "gt": gt, "pred": pred, "pred_norm": pred_norm, "ok": ok, "dt": round(dt, 2), "gen": gen[:300]})
        st = "OK" if ok else ("FAIL" if pred is not None else "NOANS")
        print(f"  [{i+1}/{total}] {st} L{prob.get('level','?')} gt={str(gt_norm)[:30]} pred={str(pred_norm)[:30]} ({dt:.1f}s) | acc={correct}/{i+1}={correct/(i+1)*100:.1f}%")
    acc = correct / total if total else 0
    print(f"\n{'='*60}")
    print(f"[{time.strftime('%H:%M:%S')}] MATH-500 acc={correct}/{total}={acc*100:.1f}% (no_ans={no_ans})")
    print(f"{'='*60}")
    summary = {"model": args.model_path, "task": "math-500", "limit": args.limit, "accuracy": acc,
               "correct": correct, "total": total, "no_answer": no_ans, "prompting": "4-shot",
               "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "details": results}
    with open(os.path.join(args.outdir, "results.json"), "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Saved to {args.outdir}/results.json")

if __name__ == "__main__":
    main()
