#!/usr/bin/env python3
"""baize_posttrain_static_eval_full.py
Full-scale static evaluation of EDA-Eval-PyAether non-techlib tasks (113 tasks)
across two models: Base (minicpm5-2b) and SFT (minicpm5-sft global_step_70).

Methodology (scaled from wake286 mini-eval of 10 tasks):
  - For each non-techlib task, send the function signature+docstring to both
    models with a code-generation system prompt.
  - temp=0 (deterministic), max_tokens=2048.
  - Static metrics only (no sandbox execution):
      1. API coverage  = correct API names found / expected API count
      2. Syntax valid  = compile() passes after stripping markdown fences
      3. Code length   = character count of generated code
      4. finish_reason = stop vs length (truncation)
      5. has_function  = target function name defined in output

Surrogate disclaimer: MiniCPM5-2B is a BaiZe surrogate; results do NOT
transfer to BaiZe. This only validates the SFT recipe pipeline.
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

def call_vllm(base_url, model_name, system, user, max_tokens=2048, timeout=120):
    payload = {"model": model_name,
        "messages": [{"role": "system", "content": system},
                      {"role": "user", "content": user}],
        "temperature": 0.0, "max_tokens": max_tokens}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(base_url.rstrip("/") + "/v1/chat/completions",
        data=data, headers={"Content-Type": "application/json"}, method="POST")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            out = json.loads(resp.read().decode("utf-8"))
        dt = time.time() - t0
        choice = out["choices"][0]
        return choice["message"]["content"], choice.get("finish_reason", "unknown"), dt, None
    except Exception as e:
        return "", "error", time.time() - t0, str(e)

def strip_markdown(text):
    """Remove MiniCPM5 <think>...</think> tags, markdown fence markers, and strip whitespace.
    Handles unpaired fences, multiple fences, and empty think tags robustly."""
    t = text.strip()
    # Remove <think>...</think> blocks (including empty: <think>\n\n</think>)
    t = re.sub(r"<think>.*?</think>", "", t, flags=re.DOTALL)
    # Remove orphan <think> or </think> tags (unpaired)
    t = re.sub(r"</?think>", "", t)
    # Remove any line that is just a fence marker (``` or ```python etc.)
    lines = t.split("\n")
    clean_lines = [l for l in lines if not re.match(r"^\s*```", l)]
    t = "\n".join(clean_lines).strip()
    return t

API_RE = re.compile(r"pyScript\.([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)?)")

def extract_apis(code):
    return sorted(set(m.group(1) for m in API_RE.finditer(code)))

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
    ap.add_argument("--base-url", default="http://localhost:8098")
    ap.add_argument("--base-model", default="minicpm5-2b")
    ap.add_argument("--sft-url", default="http://localhost:8096")
    ap.add_argument("--sft-model", default="minicpm5-sft")
    ap.add_argument("--out", default="eda_eval_static_full_wake287.json")
    ap.add_argument("--max-tasks", type=int, default=None)
    ap.add_argument("--max-tokens", type=int, default=2048)
    ap.add_argument("--resume", action="store_true", help="resume from existing output")
    args = ap.parse_args()

    tasks = load_nontechlib_tasks(DATASET, args.max_tasks)
    print("Loaded %d non-techlib tasks" % len(tasks))

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

        b_code, b_finish, b_dt, b_err = call_vllm(
            args.base_url, args.base_model, SYSTEM_PROMPT, user_msg, max_tokens=args.max_tokens)
        s_code, s_finish, s_dt, s_err = call_vllm(
            args.sft_url, args.sft_model, SYSTEM_PROMPT, user_msg, max_tokens=args.max_tokens)

        def analyze(code, finish, dt, err):
            stripped = strip_markdown(code)
            syn_ok, syn_err = check_syntax(stripped)
            found, correct, missing, cov = api_coverage(code, expected_apis)
            return {"code": code, "stripped_code": stripped, "finish_reason": finish,
                "error": err, "time_sec": round(dt, 2), "code_len": len(code),
                "stripped_len": len(stripped), "apis_found": found,
                "apis_correct": correct, "apis_missing": missing,
                "api_coverage": round(cov, 4),
                "syntax_error": syn_err if not syn_ok else "",
                "has_function": has_function_def(stripped, entry_point)}

        results[tid] = {"metadata": meta, "entry_point": entry_point,
            "apis_expected": expected_apis, "canonical_solution": task["canonical_solution"],
            "base": analyze(b_code, b_finish, b_dt, b_err),
            "sft": analyze(s_code, s_finish, s_dt, s_err)}

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
    b_syn = sum(1 for r in results.values() if not r["base"]["syntax_error"])
    s_syn = sum(1 for r in results.values() if not r["sft"]["syntax_error"])
    b_cov = sum(r["base"]["api_coverage"] for r in results.values()) / n
    s_cov = sum(r["sft"]["api_coverage"] for r in results.values()) / n
    b_len = sum(r["base"]["code_len"] for r in results.values()) / n
    s_len = sum(r["sft"]["code_len"] for r in results.values()) / n
    b_stop = sum(1 for r in results.values() if r["base"]["finish_reason"] == "stop")
    s_stop = sum(1 for r in results.values() if r["sft"]["finish_reason"] == "stop")
    b_lf = sum(1 for r in results.values() if r["base"]["finish_reason"] == "length")
    s_lf = sum(1 for r in results.values() if r["sft"]["finish_reason"] == "length")
    b_fn = sum(1 for r in results.values() if r["base"]["has_function"])
    s_fn = sum(1 for r in results.values() if r["sft"]["has_function"])
    print("\n=== SUMMARY (%d non-techlib tasks) ===" % n)
    print("Metric              | Base          | SFT           | Delta")
    print("Syntax valid        | %d/%d (%.1f%%)  | %d/%d (%.1f%%)  | %+.1fpp" % (
        b_syn, n, 100*b_syn/n, s_syn, n, 100*s_syn/n, 100*(s_syn-b_syn)/n))
    print("API coverage (mean) | %.3f          | %.3f          | %+.3f" % (b_cov, s_cov, s_cov-b_cov))
    print("Code length (mean)  | %.0f          | %.0f          | %.1fx" % (b_len, s_len, b_len/s_len if s_len else 0))
    print("finish=stop         | %d/%d (%.1f%%)  | %d/%d (%.1f%%)  | %+.1fpp" % (
        b_stop, n, 100*b_stop/n, s_stop, n, 100*s_stop/n, 100*(s_stop-b_stop)/n))
    print("finish=length       | %d/%d (%.1f%%)  | %d/%d (%.1f%%)  | %+.1fpp" % (
        b_lf, n, 100*b_lf/n, s_lf, n, 100*s_lf/n, 100*(s_lf-b_lf)/n))
    print("has_function        | %d/%d (%.1f%%)  | %d/%d (%.1f%%)  | %+.1fpp" % (
        b_fn, n, 100*b_fn/n, s_fn, n, 100*s_fn/n, 100*(s_fn-b_fn)/n))
    # per-scenario breakdown
    sc = {}
    for r in results.values():
        s = r["metadata"].get("scenario", "?")
        sc.setdefault(s, {"b_syn": 0, "s_syn": 0, "n": 0, "b_cov": 0.0, "s_cov": 0.0})
        sc[s]["n"] += 1
        sc[s]["b_syn"] += 0 if r["base"]["syntax_error"] else 1
        sc[s]["s_syn"] += 0 if r["sft"]["syntax_error"] else 1
        sc[s]["b_cov"] += r["base"]["api_coverage"]
        sc[s]["s_cov"] += r["sft"]["api_coverage"]
    print("\n--- per-scenario ---")
    for s in sorted(sc):
        d = sc[s]
        print("%s (n=%d): syn B%.0f%%/S%.0f%%  cov B%.3f/S%.3f" % (
            s, d["n"], 100*d["b_syn"]/d["n"], 100*d["s_syn"]/d["n"],
            d["b_cov"]/d["n"], d["s_cov"]/d["n"]))

if __name__ == "__main__":
    main()
