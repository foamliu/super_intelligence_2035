#!/usr/bin/env python3
"""3-model live generation comparison: MiniCPM5-2B BASE vs SFT vs Qwen3.8-27B.
Extends wake295 2-model comparison by adding Qwen3.8-27B (27B, root SGLang :8099).
Surrogate disclaimer: MiniCPM5-2B is a BaiZe surrogate; results do NOT transfer to BaiZe.
Qwen3.8-27B is a reference model for gap analysis only (not trained by us).
"""
import json, ast, re, sys, time, os, urllib.request, urllib.error

DATASET = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"
BASE_URL = "http://localhost:8098/v1/chat/completions"
SFT_URL  = "http://localhost:8096/v1/chat/completions"
QWEN_URL = "http://localhost:8099/v1/chat/completions"
BASE_MODEL = "minicpm5-2b"
SFT_MODEL  = "minicpm5-sft"
QWEN_MODEL = "qwen3.8-27b"
OUTPUT = "/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/smoke_test_results/three_model_15task_comparison.json"
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

def call_model(url, model, prompt, max_tokens=768, temp=0, disable_thinking=False):
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PREFIX + prompt}
        ],
        "temperature": temp,
        "max_tokens": max_tokens
    }
    if disable_thinking:
        body["chat_template_kwargs"] = {"enable_thinking": False}
    payload = json.dumps(body).encode()
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

def analyze_response(resp, entry_point):
    if "error" in resp:
        return {"error": resp["error"]}
    try:
        content = resp["choices"][0]["message"]["content"]
        finish = resp["choices"][0].get("finish_reason", "?")
    except (KeyError, IndexError):
        return {"error": "malformed response"}
    if not content:
        return {"error": "empty content", "finish_reason": finish}
    code = extract_code(content)
    syntax_ok = False
    try:
        ast.parse(code)
        syntax_ok = True
    except SyntaxError:
        pass
    has_func = bool(re.search(r'^\s*def\s+' + re.escape(entry_point) + r'\s*\(', code, re.MULTILINE))
    has_fence = "```" in content
    apis = re.findall(r'\bpyScript\.\w+', code)
    apis = list(dict.fromkeys(apis))
    thinking = len(content) - len(code)
    thinking_ratio = round(thinking / max(len(content), 1), 3)
    return {
        "content_length": len(content), "code_length": len(code),
        "finish_reason": finish, "syntax_valid": syntax_ok,
        "has_function": has_func, "has_code_fence": has_fence,
        "pyaether_apis": apis, "api_count": len(apis),
        "thinking_ratio": thinking_ratio,
        "code_preview": code[:500] if code else "",
    }

def main():
    selected = load_tasks()
    print("3-model comparison: BASE(2B) vs SFT(2B) vs Qwen3.8-27B")
    print("Selected " + str(len(selected)) + " tasks across " + str(len(set(s for s,_ in selected))) + " scenarios")
    for scen, task in selected:
        print("  " + scen + ": " + task['task_id'] + " -> " + task['entry_point'])
    results = []
    for idx, (scen, task) in enumerate(selected):
        tid = task["task_id"]; ep = task["entry_point"]; prompt = task["prompt"]
        print("\n[" + str(idx+1) + "/" + str(len(selected)) + "] " + tid + " (" + scen + ") -> " + ep)
        base_a = sft_a = qwen_a = {"error": "not called"}
        for label, url, model in [("BASE", BASE_URL, BASE_MODEL), ("SFT", SFT_URL, SFT_MODEL), ("QWEN", QWEN_URL, QWEN_MODEL)]:
            print("  " + label + "...", end="", flush=True)
            t0 = time.time()
            resp = call_model(url, model, prompt, disable_thinking=(label == "QWEN"))
            dt = time.time() - t0
            a = analyze_response(resp, ep)
            a["latency_s"] = round(dt, 1)
            print(" " + str(round(dt,1)) + "s", end="", flush=True)
            if "error" not in a:
                print(" syn=" + str(a['syntax_valid']) + " func=" + str(a['has_function']) + " apis=" + str(a['api_count']) + " think=" + str(a['thinking_ratio']) + " finish=" + str(a['finish_reason']))
            else:
                print(" ERROR: " + str(a['error']))
            if label == "BASE":
                base_a = a
            elif label == "SFT":
                sft_a = a
            else:
                qwen_a = a
        result = {"task_id": tid, "scenario": scen, "entry_point": ep, "base": base_a, "sft": sft_a, "qwen": qwen_a}
        results.append(result)
    valid = [r for r in results if "error" not in r["base"] and "error" not in r["sft"] and "error" not in r["qwen"]]
    summary = {"error": "no valid results"}
    if valid:
        def avg(m, key):
            return round(sum(r[m][key] for r in valid) / len(valid), 3)
        summary = {
            "total_tasks": len(valid),
            "base_syntax_valid": sum(1 for r in valid if r["base"]["syntax_valid"]),
            "sft_syntax_valid":  sum(1 for r in valid if r["sft"]["syntax_valid"]),
            "qwen_syntax_valid": sum(1 for r in valid if r["qwen"]["syntax_valid"]),
            "base_has_function": sum(1 for r in valid if r["base"]["has_function"]),
            "sft_has_function":  sum(1 for r in valid if r["sft"]["has_function"]),
            "qwen_has_function": sum(1 for r in valid if r["qwen"]["has_function"]),
            "base_total_apis": sum(r["base"]["api_count"] for r in valid),
            "sft_total_apis":  sum(r["sft"]["api_count"] for r in valid),
            "qwen_total_apis": sum(r["qwen"]["api_count"] for r in valid),
            "base_avg_thinking_ratio": avg("base", "thinking_ratio"),
            "sft_avg_thinking_ratio":  avg("sft", "thinking_ratio"),
            "qwen_avg_thinking_ratio": avg("qwen", "thinking_ratio"),
            "base_total_code_len": sum(r["base"]["code_length"] for r in valid),
            "sft_total_code_len":  sum(r["sft"]["code_length"] for r in valid),
            "qwen_total_code_len": sum(r["qwen"]["code_length"] for r in valid),
            "base_finish_stop": sum(1 for r in valid if r["base"]["finish_reason"] == "stop"),
            "sft_finish_stop":  sum(1 for r in valid if r["sft"]["finish_reason"] == "stop"),
            "qwen_finish_stop": sum(1 for r in valid if r["qwen"]["finish_reason"] == "stop"),
            "base_avg_latency": round(sum(r["base"]["latency_s"] for r in valid) / len(valid), 1),
            "sft_avg_latency":  round(sum(r["sft"]["latency_s"] for r in valid) / len(valid), 1),
            "qwen_avg_latency": round(sum(r["qwen"]["latency_s"] for r in valid) / len(valid), 1),
        }
        per_scen = {}
        for sn in SCENARIO_QUOTAS:
            sv = [r for r in valid if r["scenario"] == sn]
            if not sv: continue
            per_scen[sn] = {
                "n": len(sv),
                "base_syn": sum(1 for r in sv if r["base"]["syntax_valid"]),
                "sft_syn":  sum(1 for r in sv if r["sft"]["syntax_valid"]),
                "qwen_syn": sum(1 for r in sv if r["qwen"]["syntax_valid"]),
                "base_func": sum(1 for r in sv if r["base"]["has_function"]),
                "sft_func":  sum(1 for r in sv if r["sft"]["has_function"]),
                "qwen_func": sum(1 for r in sv if r["qwen"]["has_function"]),
                "base_api": sum(r["base"]["api_count"] for r in sv),
                "sft_api":  sum(r["sft"]["api_count"] for r in sv),
                "qwen_api": sum(r["qwen"]["api_count"] for r in sv),
            }
        summary["per_scenario"] = per_scen
    print("\n===== 3-MODEL AGGREGATE SUMMARY =====")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump({"completed": len(valid), "total": len(selected), "results": results, "summary": summary}, f, indent=2, ensure_ascii=False)
    print("\nResults saved to " + OUTPUT)

if __name__ == "__main__":
    main()


