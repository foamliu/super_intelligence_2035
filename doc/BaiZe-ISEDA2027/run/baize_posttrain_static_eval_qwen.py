#!/usr/bin/env python3
"""baize_posttrain_static_eval_qwen.py
Single-model static evaluation of EDA-Eval-PyAether non-techlib tasks (113 tasks)
against Qwen3.8-27B (root SGLang on :8099, GPU0-3).

Same methodology as baize_posttrain_static_eval_full.py but queries only one
model, to produce a 2-model baseline comparison (MiniCPM5-2B base vs Qwen3.8-27B)
for Phase 1 while the sandbox (Pass@1) is blocked.

Static metrics (no sandbox execution):
  1. API coverage   = correct API names found / expected API count
  2. Syntax valid   = compile() passes after stripping markdown fences / think tags
  3. Code length    = character count of generated code
  4. finish_reason  = stop vs length (truncation)
  5. has_function   = target function name defined in output
  6. all_apis_correct = all expected APIs present in code

NOTE: Querying the SGLang endpoint is read-only inference; does NOT touch GPU
0-3 allocation (no kill/restart/modify of root's service).
"""
import argparse, ast, json, os, re, sys, time
import urllib.request, urllib.error

DATASET = os.path.expanduser(
    "~/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl")

SYSTEM_PROMPT = (
    "You are a Python code generator for EDA (Electronic Design Automation) tasks. "
    "You output ONLY raw, executable Python code. "
    "Do NOT output markdown fences, explanations, reasoning, or comments about the task. "
    "Start your response with 'import pyAether as pyScript' if needed, then write the complete function.")

USER_PREFIX = (
    "Write the complete Python function implementation for the following function signature. "
    "The function uses the pyAether EDA library (imported as pyScript). "
    "Output ONLY the Python code for the complete function (signature + body). "
    "Do NOT output any explanations or markdown formatting. "
    "Start your response with the imports, then the function definition and its full body.\n\n")


def load_nontechlib_tasks(path, max_tasks=None):
    tasks = []
    with open(path) as f:
        for line in f:
            r = json.loads(line)
            m = r.get("metadata", "{}")
            if isinstance(m, str):
                try:
                    m = ast.literal_eval(m)
                except Exception:
                    m = {}
            if m.get("techlib_dependency", False):
                continue
            r["_meta"] = m
            tasks.append(r)
            if max_tasks and len(tasks) >= max_tasks:
                break
    return tasks


def call_api(base_url, model_name, system, user, max_tokens=4096, timeout=180):
    payload = {"model": model_name,
        "messages": [{"role": "system", "content": system},
                      {"role": "user", "content": user}],
        "temperature": 0.0, "max_tokens": max_tokens,
        # Disable Qwen3 reasoning/thinking mode for fair code-generation
        # comparison (MiniCPM5-2B has no reasoning mode). SGLang passes
        # chat_template_kwargs to the template renderer.
        "chat_template_kwargs": {"enable_thinking": False}}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(base_url.rstrip("/") + "/v1/chat/completions",
        data=data, headers={"Content-Type": "application/json"}, method="POST")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            out = json.loads(resp.read().decode("utf-8"))
        dt = time.time() - t0
        choice = out["choices"][0]
        msg = choice["message"]
        content = msg.get("content", "") or ""
        return content, choice.get("finish_reason", "unknown"), dt, None
    except Exception as e:
        return "", "error", time.time() - t0, str(e)


def strip_markdown(text):
    t = text.strip()
    t = re.sub(r"<!think>.*?</think>", "", t, flags=re.DOTALL)
    t = re.sub(r"</?think>", "", t)
    lines = t.split("\n")
    clean_lines = [l for l in lines if not re.match(r"^\s*```", l)]
    t = "\n".join(clean_lines).strip()
    return t

API_RE = re.compile(r"pyScript\.([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)?)")

def api_coverage(code, expected_apis):
    found = set(m.group(1) for m in API_RE.finditer(code))
    expected_names = [a.replace("pyAether.", "").replace("pyScript.", "") for a in expected_apis]
    correct = [n for n in expected_names if n in found]
    missing = [n for n in expected_names if n not in found]
    n_exp = len(expected_names) if expected_names else 1
    return sorted(found), correct, missing, (len(correct) / n_exp if n_exp else 0.0)

def check_syntax(code):
    try:
        compile(code, "<gen>", "exec")
        return True, ""
    except SyntaxError as e:
        return False, str(e)

def has_function_def(code, entry_point):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return bool(re.search(r"def\s+%s\s*\(" % re.escape(entry_point), code))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == entry_point:
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8099")
    ap.add_argument("--model", default="qwen3.8-27b")
    ap.add_argument("--out", default="static_eval_qwen_results.json")
    ap.add_argument("--max-tasks", type=int, default=None)
    ap.add_argument("--max-tokens", type=int, default=4096)
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()

    tasks = load_nontechlib_tasks(DATASET, args.max_tasks)
    print("Loaded %d non-techlib tasks" % len(tasks))
    print("Model: %s @ %s  max_tokens=%d" % (args.model, args.url, args.max_tokens))

    existing = {}
    if args.resume and os.path.exists(args.out):
        try:
            existing = json.load(open(args.out))
            print("Resuming: %d tasks already done" % len(existing))
        except Exception:
            existing = {}

    results = dict(existing)
    total = len(tasks)

    for i, task in enumerate(tasks):
        tid = task["task_id"]
        if tid in results:
            continue
        meta = task["_meta"]
        prompt_text = task["prompt"]
        entry_point = task["entry_point"]
        expected_apis = meta.get("apis_used", [])
        user_msg = USER_PREFIX + prompt_text

        sys.stdout.write("\r[%d/%d] %s ... " % (i + 1, total, tid))
        sys.stdout.flush()

        code, finish, dt, err = call_api(
            args.url, args.model, SYSTEM_PROMPT, user_msg, max_tokens=args.max_tokens)

        stripped = strip_markdown(code)
        syn_ok, syn_err = check_syntax(stripped)
        found, correct, missing, cov = api_coverage(code, expected_apis)
        all_correct = (len(missing) == 0 and len(expected_apis) > 0)

        results[tid] = {
            "metadata": meta, "entry_point": entry_point,
            "apis_expected": expected_apis,
            "canonical_solution": task["canonical_solution"],
            "qwen": {
                "code": code, "stripped_code": stripped,
                "finish_reason": finish, "error": err,
                "time_sec": round(dt, 2), "code_len": len(code),
                "stripped_len": len(stripped),
                "apis_found": found, "apis_correct": correct,
                "apis_missing": missing,
                "api_coverage": round(cov, 4),
                "all_apis_correct": all_correct,
                "syntax_error": syn_err if not syn_ok else "",
                "has_function": has_function_def(stripped, entry_point),
            }
        }

        if (i + 1) % 10 == 0:
            with open(args.out, "w") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            sys.stdout.write("checkpoint(%d) " % len(results))
            sys.stdout.flush()

    with open(args.out, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("\nDone. %d tasks saved to %s" % (len(results), args.out))

    n = len(results)
    if n == 0:
        return
    q = [r["qwen"] for r in results.values()]
    q_syn = sum(1 for x in q if not x["syntax_error"])
    q_cov = sum(x["api_coverage"] for x in q) / n
    q_len = sum(x["code_len"] for x in q) / n
    q_stop = sum(1 for x in q if x["finish_reason"] == "stop")
    q_lf = sum(1 for x in q if x["finish_reason"] == "length")
    q_fn = sum(1 for x in q if x["has_function"])
    q_all = sum(1 for x in q if x["all_apis_correct"])
    q_err = sum(1 for x in q if x["finish_reason"] == "error")
    print("\n=== Qwen3.8-27B SUMMARY (%d non-techlib tasks) ===" % n)
    print("Syntax valid        | %d/%d (%.1f%%)" % (q_syn, n, 100 * q_syn / n))
    print("API coverage (mean) | %.3f" % q_cov)
    print("All APIs correct    | %d/%d (%.1f%%)" % (q_all, n, 100 * q_all / n))
    print("Code length (mean)  | %.0f" % q_len)
    print("finish=stop         | %d/%d (%.1f%%)" % (q_stop, n, 100 * q_stop / n))
    print("finish=length       | %d/%d (%.1f%%)" % (q_lf, n, 100 * q_lf / n))
    print("has_function        | %d/%d (%.1f%%)" % (q_fn, n, 100 * q_fn / n))
    print("errors              | %d/%d (%.1f%%)" % (q_err, n, 100 * q_err / n))

    sc = {}
    for r in results.values():
        s = r["metadata"].get("scenario", "?")
        sc.setdefault(s, {"n": 0, "syn": 0, "cov": 0.0, "all": 0})
        sc[s]["n"] += 1
        sc[s]["syn"] += 0 if r["qwen"]["syntax_error"] else 1
        sc[s]["cov"] += r["qwen"]["api_coverage"]
        sc[s]["all"] += 1 if r["qwen"]["all_apis_correct"] else 0
    print("\n--- per-scenario ---")
    for s in sorted(sc):
        d = sc[s]
        print("%s (n=%d): syn %.0f%%  cov %.3f  all_correct %.0f%%" % (
            s, d["n"], 100 * d["syn"] / d["n"], d["cov"] / d["n"], 100 * d["all"] / d["n"]))


if __name__ == "__main__":
    main()
