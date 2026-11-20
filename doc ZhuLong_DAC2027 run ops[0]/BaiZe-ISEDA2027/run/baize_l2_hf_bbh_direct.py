#!/usr/bin/env python3
"""
BaiZe 2B L2 BBH HF Direct Evaluation
Evaluates 3 representative BBH subtasks with HF transformers (CPU, bfloat16).
Subtasks: boolean_expressions, date_understanding, multistep_arithmetic_two.
3-shot CoT prompting, limit per subtask configurable (default 10).
Uses sglang env (transformers 5.18.0, pyarrow). CPU only, nice 19.
"""
import argparse, json, os, re, time
os.environ["CUDA_VISIBLE_DEVICES"] = ""
import pyarrow.ipc as ipc
import torch
torch.set_num_threads(4)
from transformers import AutoModelForCausalLM, AutoTokenizer

BBH_BASE = "/nas_train/app.e0031982/hf_cache/lukaemon___bbh"

FEW_SHOT = {
    "boolean_expressions": [
        {"input": "not ( True ) and ( True ) is", "target": "False",
         "cot": "not ( True ) = False. False and ( True ) = False. So the answer is False."},
        {"input": "True and not not ( not False ) is", "target": "True",
         "cot": "not False = True. not ( True ) = False. not ( False ) = True. True and ( True ) = True. So the answer is True."},
        {"input": "( True or False ) and not ( False ) is", "target": "True",
         "cot": "( True or False ) = True. not ( False ) = True. True and True = True. So the answer is True."},
    ],
    "date_understanding": [
        {"input": "Today is April 4, 2005. What is the date one week from today in MM/DD/YYYY?",
         "target": "04/11/2005", "cot": "Today is 04/04/2005. One week later is 04/11/2005. So the answer is 04/11/2005."},
        {"input": "Today is December 25, 2008. What is the date 10 days ago in MM/DD/YYYY?",
         "target": "12/15/2008", "cot": "Today is 12/25/2008. 10 days ago is 12/15/2008. So the answer is 12/15/2008."},
        {"input": "Yesterday was 12/31/2020. What is today in MM/DD/YYYY?",
         "target": "01/01/2021", "cot": "Yesterday was 12/31/2020. Today is 01/01/2021. So the answer is 01/01/2021."},
    ],
    "multistep_arithmetic_two": [
        {"input": "((-3 + 4) * (2 + 1)) =", "target": "3",
         "cot": "(-3 + 4) = 1. (2 + 1) = 3. 1 * 3 = 3. So the answer is 3."},
        {"input": "((2 * 3) + (4 - 1)) =", "target": "9",
         "cot": "(2 * 3) = 6. (4 - 1) = 3. 6 + 3 = 9. So the answer is 9."},
        {"input": "((5 - 2) * (3 + 2)) =", "target": "15",
         "cot": "(5 - 2) = 3. (3 + 2) = 5. 3 * 5 = 15. So the answer is 15."},
    ],
}

def load_bbh(subtask, limit=None):
    arrow_path = f"{BBH_BASE}/{subtask}/0.0.0/982bb89fd79532a8ac676a61fc42eb1aeec63f99/bbh-test.arrow"
    with open(arrow_path, "rb") as f:
        reader = ipc.open_stream(f)
        table = reader.read_all()
    rows = table.to_pylist()
    return rows[:limit] if limit else rows

def build_prompt(subtask, question):
    examples = FEW_SHOT[subtask]
    prompt = ""
    for ex in examples:
        prompt += f"Q: {ex['input']}\nA: {ex['cot']}\n\n"
    prompt += f"Q: {question}\nA:"
    return prompt

def extract_answer(text, subtask):
    m = re.search(r"answer is\s*:?\s*(.+?)(?:\.|\n|$)", text, re.I)
    if m:
        ans = m.group(1).strip().strip(".")
        if subtask == "boolean_expressions":
            if "true" in ans.lower(): return "True"
            if "false" in ans.lower(): return "False"
        return ans
    if subtask == "boolean_expressions":
        t = text.strip().lower()
        if "true" in t and "false" not in t: return "True"
        if "false" in t and "true" not in t: return "False"
    nums = re.findall(r"-?\d+(?:\.\d+)?", text)
    return nums[-1] if nums else None

def normalize_answer(ans, subtask):
    if ans is None: return None
    ans = str(ans).strip().strip(".")
    if subtask == "boolean_expressions":
        if "true" in ans.lower(): return "True"
        if "false" in ans.lower(): return "False"
    if subtask == "multistep_arithmetic_two":
        try: return str(int(float(ans)))
        except (ValueError, TypeError): return ans
    return ans

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model_path", default="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/hf_iter_160000")
    ap.add_argument("--subtasks", default="boolean_expressions,date_understanding,multistep_arithmetic_two")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--max_new_tokens", type=int, default=128)
    ap.add_argument("--outdir", default="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results/gguf_iter_160000_l2_hf_bbh_direct")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    subtasks = args.subtasks.split(",")
    print(f"[{time.strftime('%H:%M:%S')}] BBH HF Direct Eval subtasks={subtasks} limit={args.limit}")
    print(f"[{time.strftime('%H:%M:%S')}] Loading model from {args.model_path}...")
    tok = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(args.model_path, trust_remote_code=True, torch_dtype=torch.bfloat16)
    model.eval()
    print(f"  Model loaded (CPU, bfloat16, threads={torch.get_num_threads()})")
    all_results = {}
    for subtask in subtasks:
        print(f"\n[{time.strftime('%H:%M:%S')}] === Subtask: {subtask} ===")
        problems = load_bbh(subtask, args.limit)
        print(f"  Loaded {len(problems)} problems")
        results, correct = [], 0
        total = len(problems)
        for i, prob in enumerate(problems):
            q, gt = prob["input"], prob["target"]
            prompt = build_prompt(subtask, q)
            inp = tok(prompt, return_tensors="pt", truncation=True, max_length=2048)
            t0 = time.time()
            with torch.no_grad():
                out = model.generate(**inp, max_new_tokens=args.max_new_tokens, do_sample=False, pad_token_id=tok.eos_token_id)
            dt = time.time() - t0
            gen = tok.decode(out[0][inp["input_ids"].shape[1]:], skip_special_tokens=True)
            pred = extract_answer(gen, subtask)
            pred_norm = normalize_answer(pred, subtask)
            gt_norm = normalize_answer(gt, subtask)
            ok = (pred_norm is not None and pred_norm == gt_norm)
            if ok: correct += 1
            results.append({"idx": i, "input": q[:200], "gt": gt, "pred": pred, "pred_norm": pred_norm, "ok": ok, "dt": round(dt, 2), "gen": gen[:200]})
            st = "OK" if ok else "FAIL"
            print(f"  [{i+1}/{total}] {st} gt={gt} pred={pred_norm} ({dt:.1f}s) | acc={correct}/{i+1}={correct/(i+1)*100:.1f}%")
        acc = correct / total if total else 0
        print(f"  [{time.strftime('%H:%M:%S')}] {subtask} acc={correct}/{total}={acc*100:.1f}%")
        all_results[subtask] = {"accuracy": acc, "correct": correct, "total": total, "limit": args.limit, "details": results}
    total_correct = sum(r["correct"] for r in all_results.values())
    total_problems = sum(r["total"] for r in all_results.values())
    overall_acc = total_correct / total_problems if total_problems else 0
    print(f"\n{'='*60}")
    print(f"[{time.strftime('%H:%M:%S')}] BBH Overall acc={total_correct}/{total_problems}={overall_acc*100:.1f}%")
    for st, r in all_results.items():
        print(f"  {st}: {r['correct']}/{r['total']}={r['accuracy']*100:.1f}%")
    print(f"{'='*60}")
    summary = {"model": args.model_path, "task": "bbh", "subtasks": subtasks, "limit": args.limit,
               "overall_accuracy": overall_acc,
               "per_subtask": {st: {"accuracy": r["accuracy"], "correct": r["correct"], "total": r["total"]} for st, r in all_results.items()},
               "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "full_details": all_results}
    with open(os.path.join(args.outdir, "results.json"), "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Saved to {args.outdir}/results.json")

if __name__ == "__main__":
    main()
