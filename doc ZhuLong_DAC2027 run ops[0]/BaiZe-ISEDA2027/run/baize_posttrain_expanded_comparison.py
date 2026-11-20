#!/usr/bin/env python3
"""Expanded BASE vs SFT live generation comparison on 15 diverse tasks.
Scales from wake293 3-task smoke to 15 tasks across 4 scenarios.
Surrogate disclaimer: MiniCPM5-2B is a BaiZe surrogate; results do NOT transfer to BaiZe.
"""
import json, ast, re, sys, time, os, urllib.request, urllib.error

DATASET = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"
BASE_URL = "http://localhost:8098/v1/chat/completions"
SFT_URL  = "http://localhost:8096/v1/chat/completions"
BASE_MODEL = "minicpm5-2b"
SFT_MODEL  = "minicpm5-sft"
OUTPUT = "/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/smoke_test_results/expanded_base_vs_sft_15task.json"
SCENARIO_QUOTAS = {"Schematic": 5, "Layout": 4, "Design Management": 3, "Others": 3}

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

def load_tasks():
    tasks_by_scen = {}
    with open(DATASET) as f:
        for line in f:
            r = json.loads(line)
            m = r.get("metadata", "{}")
            if isinstance(m, str):
                try: m = ast.literal_eval(m)
                except: m = {}
            if m.get("techlib_dependency", False):
                continue
            s = m.get("scenario", "N/A")
            tasks_by_scen.setdefault(s, []).append(r)
    selected = []
    for scen, quota in SCENARIO_QUOTAS.items():
        pool = tasks_by_scen.get(scen, [])
        step = max(1, len(pool) // quota)
        picked = 0
        for i in range(0, len(pool), step):
            if picked >= quota:
                break
            selected.append((scen, pool[i]))
            picked += 1
    return selected

def call_model(url, model, prompt, max_tokens=2048, temp=0):
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PREFIX + prompt}
        ],
        "temperature": temp,
        "max_tokens": max_tokens
    }).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

def extract_code(text):
    m = re.search(r'```(?:python)?\s*\n(.*?)```', text, re.DOTALL)
    if m:
        return m.group(1).strip()
    lines = text.split('\n')
    code_lines = []
    in_code = False
    for line in lines:
        if not in_code and (line.startswith('import ') or line.startswith('from ') or line.startswith('def ')):
            in_code = True
        if in_code:
            code_lines.append(line)
    return '\n'.join(code_lines).strip() if code_lines else text.strip()

def count_pyaether_apis(code):
    patterns = [r'\bpyScript\.\w+', r'\bpyAether\.\w+', r'\bdb\w+', r'\bemy\w+', r'\bMde\w+']
    apis = set()
    for p in patterns:
        apis.update(re.findall(p, code))
    return sorted(apis)

def check_syntax(code):
    try:
        compile(code, '<generated>', 'exec')
        return True
    except SyntaxError:
        return False

def has_function(code, func_name):
    return bool(re.search(r'def\s+' + re.escape(func_name) + r'\s*\(', code))

def analyze_response(resp, entry_point):
    if "error" in resp:
        return {"error": resp["error"]}
    choice = resp.get("choices", [{}])[0]
    content = choice.get("message", {}).get("content", "")
    finish = choice.get("finish_reason", "unknown")
    code = extract_code(content)
    apis = count_pyaether_apis(code)
    syntax_ok = check_syntax(code) if code else False
    has_func = has_function(code, entry_point) if code else False
    has_fence = bool(re.search(r'```', content))
    first_code = content.find('import ') if 'import ' in content else content.find('def ')
    if first_code < 0:
        first_code = content.find('```')
    thinking_chars = first_code if first_code > 0 else len(content)
    thinking_ratio = thinking_chars / max(len(content), 1)
    return {
        "content_length": len(content), "code_length": len(code),
        "finish_reason": finish, "syntax_valid": syntax_ok,
        "has_function": has_func, "has_code_fence": has_fence,
        "pyaether_apis": apis, "api_count": len(apis),
        "thinking_ratio": round(thinking_ratio, 3),
        "code_preview": code[:500] if code else "",
    }

def main():
    selected = load_tasks()
    print(f"Selected {len(selected)} tasks across {len(set(s for s,_ in selected))} scenarios")
    for scen, task in selected:
        print(f"  {scen}: {task['task_id']} -> {task['entry_point']}")
    results = []
    for idx, (scen, task) in enumerate(selected):
        tid = task["task_id"]; ep = task["entry_point"]; prompt = task["prompt"]
        print(f"\n[{idx+1}/{len(selected)}] {tid} ({scen}) -> {ep}")
        print(f"  BASE...", end="", flush=True)
        t0 = time.time()
        base_resp = call_model(BASE_URL, BASE_MODEL, prompt)
        print(f" {time.time()-t0:.1f}s", end="", flush=True)
        base_a = analyze_response(base_resp, ep)
        print(f"  SFT...", end="", flush=True)
        t0 = time.time()
        sft_resp = call_model(SFT_URL, SFT_MODEL, prompt)
        print(f" {time.time()-t0:.1f}s", flush=True)
        sft_a = analyze_response(sft_resp, ep)
        result = {"task_id": tid, "scenario": scen, "entry_point": ep, "base": base_a, "sft": sft_a}
        results.append(result)
        if "error" not in base_a and "error" not in sft_a:
            print(f"  BASE: syntax={base_a['syntax_valid']}, func={base_a['has_function']}, apis={base_a['api_count']}, think={base_a['thinking_ratio']}")
            print(f"  SFT:  syntax={sft_a['syntax_valid']}, func={sft_a['has_function']}, apis={sft_a['api_count']}, think={sft_a['thinking_ratio']}")
    valid = [r for r in results if "error" not in r["base"] and "error" not in r["sft"]]
    if valid:
        summary = {
            "total_tasks": len(valid),
            "base_syntax_valid": sum(1 for r in valid if r["base"]["syntax_valid"]),
            "sft_syntax_valid": sum(1 for r in valid if r["sft"]["syntax_valid"]),
            "base_has_function": sum(1 for r in valid if r["base"]["has_function"]),
            "sft_has_function": sum(1 for r in valid if r["sft"]["has_function"]),
            "base_total_apis": sum(r["base"]["api_count"] for r in valid),
            "sft_total_apis": sum(r["sft"]["api_count"] for r in valid),
            "base_avg_thinking_ratio": round(sum(r["base"]["thinking_ratio"] for r in valid)/len(valid), 3),
            "sft_avg_thinking_ratio": round(sum(r["sft"]["thinking_ratio"] for r in valid)/len(valid), 3),
            "base_code_fence": sum(1 for r in valid if r["base"]["has_code_fence"]),
            "sft_code_fence": sum(1 for r in valid if r["sft"]["has_code_fence"]),
            "base_total_code_len": sum(r["base"]["code_length"] for r in valid),
            "sft_total_code_len": sum(r["sft"]["code_length"] for r in valid),
            "base_finish_stop": sum(1 for r in valid if r["base"]["finish_reason"] == "stop"),
            "sft_finish_stop": sum(1 for r in valid if r["sft"]["finish_reason"] == "stop"),
        }
        print("\n===== AGGREGATE SUMMARY =====")
        print(json.dumps(summary, indent=2))
    else:
        summary = {"error": "no valid results"}
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump({"summary": summary, "results": results}, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {OUTPUT}")

if __name__ == "__main__":
    main()
