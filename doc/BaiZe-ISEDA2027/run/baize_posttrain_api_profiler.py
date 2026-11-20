#!/usr/bin/env python3
"""baize_posttrain_api_profiler.py — Profile unknown-return-type APIs via EDA sandbox.

Usage:
    python3 baize_posttrain_api_profiler.py --dry-run
    python3 baize_posttrain_api_profiler.py --dry-run --max-apis 10
    python3 baize_posttrain_api_profiler.py --sandbox-endpoint http://36.15:port --max-apis 100
    python3 baize_posttrain_api_profiler.py --help

Purpose:
    4367 APIs have 'unknown' return type. This script profiles them by
    calling in the EDA sandbox and inferring return type from actual result.
    Output: run/api_return_types_profiled.jsonl
    Zero GPU: only needs EDA sandbox (36.15 via tunnel).
    Contamination: profiles whitelist APIs only (excludes 488 eval APIs).
"""
import argparse, json, sys, time, re
from pathlib import Path

RUN_DIR = Path(__file__).parent
API_DB_PATH = Path.home() / "code" / "eda_fastmcp" / "docs" / "API_INFO_MERGED_V3.json"
EVAL_DATASET = Path.home() / "code" / "eda_fastmcp" / "pyAether-eval" / "original_dataset" / "EDA-Eval-PyAether-v20260311.jsonl"
OUTPUT_PATH = RUN_DIR / "api_return_types_profiled.jsonl"

TYPE_MAP = {"bool":"bool","int":"int","integer":"int","float":"float","double":"float",
    "str":"str","string":"str","list":"list","array":"list","tuple":"tuple",
    "dict":"dict","map":"dict","object":"object","void":"None","none":"None","null":"None"}

def load_api_db():
    if not API_DB_PATH.exists():
        print(f"ERROR: API DB not found: {API_DB_PATH}", file=sys.stderr); sys.exit(1)
    with open(API_DB_PATH) as f: data = json.load(f)
    apis = list(data.values()) if isinstance(data, dict) and "apis" not in data else (data.get("apis", data) if isinstance(data, dict) else data)
    print(f"Loaded {len(apis)} APIs from {API_DB_PATH}"); return apis

def load_eval_apis():
    blacklist = set()
    if not EVAL_DATASET.exists(): return blacklist
    with open(EVAL_DATASET) as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                task = json.loads(line)
                for api in task.get("metadata", {}).get("apis_used", []): blacklist.add(api.lower())
                for m in re.finditer(r'pyAether\.(\w+)', task.get("prompt", "")):
                    blacklist.add(f"pyaether.{m.group(1).lower()}")
            except json.JSONDecodeError: continue
    print(f"Loaded {len(blacklist)} eval API names (blacklist)"); return blacklist

def filter_unknown_apis(apis, blacklist):
    unknown = []
    for api in apis:
        name = api.get("api_name", ""); atype = api.get("api_type", "")
        if atype not in ("function", "method", "Function", "Method"): continue
        full = f"{api.get('module', 'pyAether')}.{name}".lower()
        if name.lower() in blacklist or full in blacklist: continue
        desc = api.get("api_descriptions", "") or ""
        if re.search(r'\*\*out\*\*\s*type\s*[:=]\s*(\w+)', desc, re.IGNORECASE): continue
        if api.get("return_type", "") and api.get("return_type", "").lower() in TYPE_MAP: continue
        unknown.append(api)
    print(f"Filtered to {len(unknown)} unknown-return APIs"); return unknown

def generate_probe_code(api):
    name = api.get("api_name", "")
    code = f'import pyAether as pyScript\ntry:\n    result = pyScript.{name}()\n    print(f"__PROBE_RESULT__{{type(result).__name__}}__{{repr(result)[:200]}}__")\nexcept Exception as e:\n    print(f"__PROBE_ERROR__{{type(e).__name__}}__{{str(e)[:200]}}__")\n'
    return code, name

def infer_return_type(output):
    m = re.search(r'__PROBE_RESULT__(\w+)__(.*)__', output)
    if m:
        tn = m.group(1).lower()
        for k, v in TYPE_MAP.items():
            if tn == k: return v
        if tn in ("nonetype", "none"): return "None"
        return "object"
    m = re.search(r'__PROBE_ERROR__(\w+)__(.*)__', output)
    if m: return "error:" + m.group(1)
    return "unknown"

def execute_in_sandbox(code, endpoint, timeout=30):
    if endpoint.startswith("mock://"): return "__PROBE_ERROR__NotImplementedError__Mock sandbox__"
    try:
        import urllib.request
        payload = json.dumps({"code": code, "host": "pyAether"}).encode()
        req = urllib.request.Request(f"{endpoint}/run_code", data=payload, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            r = json.loads(resp.read().decode()); return r.get("print_log", "") + r.get("response", "")
    except Exception as e: return f"__PROBE_ERROR__{type(e).__name__}__{str(e)[:200]}__"

def main():
    parser = argparse.ArgumentParser(description="Profile unknown-return-type APIs via EDA sandbox")
    parser.add_argument("--dry-run", action="store_true", help="Print plan without executing")
    parser.add_argument("--max-apis", type=int, default=0, help="Max APIs to profile (0=all)")
    parser.add_argument("--sandbox-endpoint", default="mock://sandbox", help="Sandbox URL or mock://")
    parser.add_argument("--output", default=str(OUTPUT_PATH), help="Output JSONL path")
    parser.add_argument("--timeout", type=int, default=30, help="Per-API timeout seconds")
    args = parser.parse_args()

    print("=" * 60)
    print("BaiZe Post-Train API Profiler")
    print(f"  API DB: {API_DB_PATH}\n  Output: {args.output}\n  Sandbox: {args.sandbox_endpoint}")
    print(f"  Max: {args.max_apis if args.max_apis > 0 else 'all'}\n  Mode: {'DRY-RUN' if args.dry_run else 'EXECUTE'}")
    print("=" * 60)

    apis = load_api_db()
    blacklist = load_eval_apis()
    unknown = filter_unknown_apis(apis, blacklist)
    if args.max_apis > 0: unknown = unknown[:args.max_apis]; print(f"Limited to {len(unknown)} APIs")

    if args.dry_run:
        print(f"\n[DRY-RUN] Would profile {len(unknown)} unknown-return APIs")
        for api in unknown[:5]:
            _, name = generate_probe_code(api)
            print(f"  - {name} (module={api.get('module', 'pyAether')})")
        print("[DRY-RUN] Use --sandbox-endpoint http://... to execute."); return

    profiled, errors, start = 0, 0, time.time()
    with open(args.output, "w") as out_f:
        for i, api in enumerate(unknown):
            code, name = generate_probe_code(api)
            output = execute_in_sandbox(code, args.sandbox_endpoint, args.timeout)
            ret_type = infer_return_type(output)
            rec = {"api_name": name, "module": api.get("module", "pyAether"),
                   "return_type": ret_type, "profiled": ret_type not in ("unknown",),
                   "probe_output": output[:500]}
            out_f.write(json.dumps(rec) + "\n"); out_f.flush()
            if rec["profiled"]: profiled += 1
            else: errors += 1
            if (i + 1) % 100 == 0:
                el = time.time() - start; rate = (i + 1) / el
                print(f"  [{i+1}/{len(unknown)}] profiled={profiled} errors={errors} rate={rate:.1f}/s ETA={(len(unknown)-i-1)/rate/60:.1f}min")

    el = time.time() - start
    print(f"\nDone: {len(unknown)} APIs in {el/60:.1f} min | profiled={profiled} errors={errors}")
    print(f"Output: {args.output}")

if __name__ == "__main__": main()

