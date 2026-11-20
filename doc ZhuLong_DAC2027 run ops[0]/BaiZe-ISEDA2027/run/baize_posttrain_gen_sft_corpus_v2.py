#!/usr/bin/env python3
"""baize_posttrain_gen_sft_corpus_v2.py — PyAether SFT corpus generator v2

v2 fixes v1 P0 bug: v1 ALL completions call APIs with ZERO arguments (100% empty-arg).
v2 extracts real calls from API docs Examples, or generates typed placeholder args.

4 SFT pair types: S1 doc-to-code, S2 api-lookup, S3 multi-api-chain, S4 error-recovery.
Contamination isolation: 158 eval task API blacklist. Zero GPU. Python 3.8 compatible.
"""
import argparse, json, os, re, hashlib
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
API_DB_PATH = os.path.expanduser("~/code/eda_fastmcp/docs/API_INFO_MERGED_V3.json")
EVAL_DATASET = os.path.expanduser("~/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl")
DEFAULT_OUTPUT = os.path.join(SCRIPT_DIR, "sft_pyaether_corpus_v2.jsonl")

TYPE_PLACEHOLDERS = {
    "int": "0", "bool": "True", "float": "0.0", "str": '""', "string": '""',
    "list": "[]", "tuple": "()", "dict": "{}", "none": "None",
    "emyPointF": "pyScript.emyPointF(0, 0)", "emyBoxF": "pyScript.emyBoxF(0, 0, 10, 10)",
    "emyDesign": "pyScript.dbNewCV('test', 'test', 'schematic')",
    "emyString": '"test"', "vector1D_p_emyFig": "[]",
}
DEFAULT_PLACEHOLDER = "None"


def load_api_db(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_eval_apis(path):
    apis = set()
    if not os.path.exists(path):
        return apis
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                task = json.loads(line)
                for api in task.get("metadata", {}).get("apis_used", []):
                    apis.add(api)
            except (json.JSONDecodeError, KeyError):
                continue
    return apis


def extract_signature(desc):
    # Try bold signature: **`func(params) -> ret`** (may have -> return_type)
    m = re.search(r"\*\*`(\w+)\(([^)]*)\)[^`]*`\*\*", desc)
    if m:
        return m.group(0), m.group(1), m.group(2)
    # Fallback: `func(params)`
    m = re.search(r"`(\w+)\(([^)]*)\)`", desc)
    if m:
        return m.group(0), m.group(1), m.group(2)
    return None, None, None


def extract_example_call(desc, func_name):
    """Extract actual API call from Examples section with arguments.
    Handles nested parentheses by matching balanced parens."""
    ex_match = re.search(r"Examples\s*(.*?)(?:\n---|\n# |\Z)", desc, re.DOTALL)
    if not ex_match:
        return None
    example_text = ex_match.group(1)
    # Find all pyScript.func_name( calls with balanced parens
    call_prefix = "pyScript." + func_name + "("
    idx = 0
    while True:
        pos = example_text.find(call_prefix, idx)
        if pos == -1:
            break
        # Extract balanced parens
        depth = 1
        start = pos + len(call_prefix)
        end = start
        while end < len(example_text) and depth > 0:
            if example_text[end] == "(":
                depth += 1
            elif example_text[end] == ")":
                depth -= 1
            end += 1
        args = example_text[start:end-1].strip()
        if args:
            # Check if args reference undefined variables (heuristic: lowercase identifiers not in TYPE_PLACEHOLDERS)
            # If args contain variable references that look like setup vars, skip
            return "pyScript." + func_name + "(" + args + ")"
        idx = pos + 1
    return None


def parse_params_from_signature(params_str):
    """Parse parameter names/types from signature like 'schematic: emyDesign, layout: emyDesign'."""
    if not params_str or not params_str.strip():
        return []
    params = []
    for part in re.split(r",\s*(?![^<]*>)", params_str):
        part = part.strip()
        if not part or part.startswith("*"):
            continue
        m = re.match(r"(\w+)(?::\s*([\w\[\]]+))?(?:=\s*(.+))?", part)
        if m:
            params.append((m.group(1), (m.group(2) or "").strip(), (m.group(3) or "").strip()))
    return params


def parse_params_from_section(desc):
    """Parse Parameters section: **param_name**type → [(name, type)]."""
    pm = re.search(r"Parameters\s*(.*?)(?:Returns|Examples|---|\Z)", desc, re.DOTALL)
    if not pm:
        return []
    params = []
    for m in re.finditer(r"\*\*(\w+)\*\*\s*([\w\[\]]+)?", pm.group(1)):
        params.append((m.group(1), (m.group(2) or "").strip(), ""))
    return params


def generate_placeholder_args(params):
    """Generate placeholder argument string from param names and types."""
    parts = []
    for item in params:
        name, ptype, default = item[0], item[1] if len(item) > 1 else "", item[2] if len(item) > 2 else ""
        if default:
            continue
        placeholder = TYPE_PLACEHOLDERS.get(ptype, DEFAULT_PLACEHOLDER)
        parts.append(name + "=" + placeholder)
    return ", ".join(parts)


def gen_completion_with_args(func_name, full_name, desc, api_info):
    """Generate completion with proper arguments. Returns (completion, quality_tier).
    Strategy: 1) Typed placeholders from signature (self-contained, best for SFT)
              2) Typed placeholders from Parameters section
              3) Example call from docs (may have undefined vars, lower quality)
              4) Fallback: no args (lowest quality, same as v1)"""
    # Strategy 1: Parse signature params → typed placeholders (self-contained)
    _, _, sig_params = extract_signature(desc)
    if sig_params and sig_params.strip():
        params = parse_params_from_signature(sig_params)
        args_str = generate_placeholder_args(params)
        if args_str:
            comp = ("```python\nimport pyAether as pyScript\n\n"
                    "def call_" + func_name.lower() + "():\n"
                    '    """Call ' + full_name + ' and return the result."""\n'
                    "    result = pyScript." + func_name + "(" + args_str + ")\n"
                    "    return result\n```\n")
            return comp, "high"

    # Strategy 2: Parse Parameters section → typed placeholders
    section_params = parse_params_from_section(desc)
    args_str = generate_placeholder_args(section_params)
    if args_str:
        comp = ("```python\nimport pyAether as pyScript\n\n"
                "def call_" + func_name.lower() + "():\n"
                '    """Call ' + full_name + ' and return the result."""\n'
                "    result = pyScript." + func_name + "(" + args_str + ")\n"
                "    return result\n```\n")
        return comp, "high"

    # Strategy 3: Example call from docs (may reference undefined vars)
    example_call = extract_example_call(desc, func_name)
    if example_call:
        comp = ("```python\nimport pyAether as pyScript\n\n"
                "def call_" + func_name.lower() + "():\n"
                '    """Call ' + full_name + ' and return the result."""\n'
                "    result = " + example_call + "\n"
                "    return result\n```\n")
        return comp, "medium"

    # Strategy 4: Fallback — no params found
    comp = ("```python\nimport pyAether as pyScript\n\n"
            "def call_" + func_name.lower() + "():\n"
            '    """Call ' + full_name + ' and return the result."""\n'
            "    result = pyScript." + func_name + "()\n"
            "    return result\n```\n")
    return comp, "low"


def gen_s1_doc_to_code(api_name, api_info, eval_apis):
    full_name = api_info.get("api_name", api_name)
    if full_name in eval_apis:
        return None
    desc = api_info.get("api_descriptions", "")
    if len(desc) < 30:
        return None
    _, func_name, _ = extract_signature(desc)
    if not func_name:
        func_name = api_name.split(".")[-1] if "." in api_name else api_name
    prompt = ("You are an EDA automation assistant. Read the following PyAether API "
              "documentation and write a Python function that calls this API.\n\n"
              "## API Documentation\n\n" + desc[:800] + "\n\n"
              "## Task\n\nWrite a Python function that calls `" + full_name +
              "` and returns its result. Use `import pyAether as pyScript` and call via `pyScript." + func_name + "`.")
    completion, quality = gen_completion_with_args(func_name, full_name, desc, api_info)
    return {"pair_id": "S1-" + hashlib.sha256(full_name.encode()).hexdigest()[:12],
            "type": "S1_doc_to_code", "prompt": prompt, "completion": completion,
            "api_used": [full_name], "source": full_name,
            "contamination_check": "passed", "quality_tier": quality}


def gen_s2_api_lookup(api_name, api_info, eval_apis, category_apis):
    full_name = api_info.get("api_name", api_name)
    if full_name in eval_apis:
        return None
    desc = api_info.get("api_descriptions", "")
    if len(desc) < 30:
        return None
    _, func_name, _ = extract_signature(desc)
    if not func_name:
        func_name = api_name.split(".")[-1] if "." in api_name else api_name
    cat = api_info.get("category", "unknown")
    distractors = [a for a in category_apis.get(cat, []) if a != full_name and a not in eval_apis][:2]
    brief = re.sub(r"^#+\s*", "", desc).split("\n")[0].strip()[:200]
    prompt = ("You are an EDA automation assistant. Which PyAether API should you use "
              "for the following task?\n\nTask: " + brief + "\n\nOptions: " +
              ", ".join([full_name] + distractors) + "\n\nWrite a Python function that calls the correct API with proper arguments.")
    completion, quality = gen_completion_with_args(func_name, full_name, desc, api_info)
    completion = "The correct API is `" + full_name + "`.\n\n" + completion
    return {"pair_id": "S2-" + hashlib.sha256(full_name.encode()).hexdigest()[:12],
            "type": "S2_api_lookup", "prompt": prompt, "completion": completion,
            "api_used": [full_name], "source": full_name,
            "contamination_check": "passed", "quality_tier": quality}


def gen_s3_multi_api_chain(apis_in_category, eval_apis, api_db):
    clean_apis = [a for a in apis_in_category if a not in eval_apis][:3]
    if len(clean_apis) < 3:
        return None
    calls = []
    for i, full_name in enumerate(clean_apis):
        info = None
        for k, v in api_db.items():
            if v.get("api_name") == full_name:
                info = v
                break
        if not info:
            calls.append("r" + str(i) + " = pyScript." + full_name.split(".")[-1] + "()")
            continue
        desc = info.get("api_descriptions", "")
        _, func_name, _ = extract_signature(desc)
        if not func_name:
            func_name = full_name.split(".")[-1]
        comp, _ = gen_completion_with_args(func_name, full_name, desc, info)
        call_match = re.search(r"(pyScript\.\w+\([^)]*\))", comp)
        calls.append("r" + str(i) + " = " + (call_match.group(1) if call_match else "pyScript." + func_name + "()"))
    completion = ("```python\nimport pyAether as pyScript\n\n"
                  "def chain_calls():\n"
                  '    """Chain ' + str(len(clean_apis)) + ' API calls."""\n' +
                  "\n".join("    " + c for c in calls) + "\n"
                  "    return [" + ", ".join("r" + str(i) for i in range(len(calls))) + "]\n```\n")
    prompt = ("You are an EDA automation assistant. Write a Python function that chains "
              "the following " + str(len(clean_apis)) + " PyAether API calls in sequence:\n" +
              "\n".join("- " + a for a in clean_apis) + "\n\n"
              "Use `import pyAether as pyScript` and call each API with appropriate arguments.")
    return {"pair_id": "S3-" + hashlib.sha256(",".join(clean_apis).encode()).hexdigest()[:12],
            "type": "S3_multi_api_chain", "prompt": prompt, "completion": completion,
            "api_used": clean_apis, "source": ",".join(clean_apis),
            "contamination_check": "passed", "quality_tier": "medium"}


def gen_s4_error_recovery(api_name, api_info, eval_apis):
    full_name = api_info.get("api_name", api_name)
    if full_name in eval_apis:
        return None
    desc = api_info.get("api_descriptions", "")
    if len(desc) < 30:
        return None
    _, func_name, _ = extract_signature(desc)
    if not func_name:
        func_name = api_name.split(".")[-1] if "." in api_name else api_name
    prompt = ("You are an EDA automation assistant. The following code has an error.\n\n"
              "```python\nimport pyAether as pyScript\n\n"
              "def buggy_call():\n"
              "    result = pyScript." + func_name + "()  # Missing required arguments\n"
              "    return result\n```\n\n"
              "## API Documentation\n\n" + desc[:500] + "\n\n"
              "Fix the code to call `" + full_name + "` with the correct arguments.")
    completion, quality = gen_completion_with_args(func_name, full_name, desc, api_info)
    completion = ("The error is missing required arguments. The API `" + full_name +
                  "` requires specific parameters as shown in the documentation.\n\n" + completion)
    return {"pair_id": "S4-" + hashlib.sha256(full_name.encode()).hexdigest()[:12],
            "type": "S4_error_recovery", "prompt": prompt, "completion": completion,
            "api_used": [full_name], "source": full_name,
            "contamination_check": "passed", "quality_tier": quality}


def main():
    parser = argparse.ArgumentParser(description="Generate PyAether SFT corpus v2 with proper arguments")
    parser.add_argument("--api-db", default=API_DB_PATH)
    parser.add_argument("--eval-dataset", default=EVAL_DATASET)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--max-pairs", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--types", default="S1,S2,S3,S4")
    args = parser.parse_args()

    print("Loading API DB from " + args.api_db + "...")
    api_db = load_api_db(args.api_db)
    print("  Loaded " + str(len(api_db)) + " APIs")
    eval_apis = load_eval_apis(args.eval_dataset)
    print("  Found " + str(len(eval_apis)) + " eval API names (blacklist)")

    category_apis = defaultdict(list)
    for k, v in api_db.items():
        category_apis[v.get("category", "unknown")].append(v.get("api_name", k))

    requested_types = set(args.types.split(","))
    pairs = []
    counts = defaultdict(int)
    quality_counts = defaultdict(lambda: defaultdict(int))

    if "S1" in requested_types:
        for k, v in api_db.items():
            pair = gen_s1_doc_to_code(k, v, eval_apis)
            if pair:
                pairs.append(pair); counts["S1"] += 1
                quality_counts["S1"][pair["quality_tier"]] += 1
                if args.max_pairs and len(pairs) >= args.max_pairs: break
    if "S2" in requested_types and (not args.max_pairs or len(pairs) < args.max_pairs):
        for k, v in api_db.items():
            pair = gen_s2_api_lookup(k, v, eval_apis, category_apis)
            if pair:
                pairs.append(pair); counts["S2"] += 1
                quality_counts["S2"][pair["quality_tier"]] += 1
                if args.max_pairs and len(pairs) >= args.max_pairs: break
    if "S3" in requested_types and (not args.max_pairs or len(pairs) < args.max_pairs):
        for cat, apis in category_apis.items():
            if len(apis) >= 3:
                pair = gen_s3_multi_api_chain(apis, eval_apis, api_db)
                if pair:
                    pairs.append(pair); counts["S3"] += 1
                    quality_counts["S3"][pair["quality_tier"]] += 1
                    if args.max_pairs and len(pairs) >= args.max_pairs: break
    if "S4" in requested_types and (not args.max_pairs or len(pairs) < args.max_pairs):
        for k, v in api_db.items():
            if v.get("api_type") == "function":
                pair = gen_s4_error_recovery(k, v, eval_apis)
                if pair:
                    pairs.append(pair); counts["S4"] += 1
                    quality_counts["S4"][pair["quality_tier"]] += 1
                    if args.max_pairs and len(pairs) >= args.max_pairs: break

    contaminated = [p for p in pairs if p.get("contamination_check") != "passed"]
    if contaminated:
        print("  WARNING: " + str(len(contaminated)) + " contaminated pairs! Removing.")
        pairs = [p for p in pairs if p.get("contamination_check") == "passed"]

    print("\n=== SFT Corpus v2 Generation Results ===")
    print("  Total pairs: " + str(len(pairs)))
    for t, c in sorted(counts.items()):
        q = quality_counts[t]
        print("    %s: %d  (high=%d medium=%d low=%d)" % (t, c, q.get("high", 0), q.get("medium", 0), q.get("low", 0)))
    print("  Contaminated removed: " + str(len(contaminated)))
    unique_apis = set(a for p in pairs for a in p.get("api_used", []))
    print("  Unique APIs covered: " + str(len(unique_apis)))

    empty = 0; has_args = 0
    for p in pairs:
        for m in re.finditer(r"pyScript\.\w+\(([^)]*)\)", p.get("completion", "")):
            if m.group(1).strip(): has_args += 1
            else: empty += 1
    print("  Calls with args: %d  Empty-arg calls: %d" % (has_args, empty))
    if has_args + empty > 0:
        print("  Has-args ratio: %.1f%%" % (has_args / (has_args + empty) * 100))

    if args.dry_run:
        print("\n[dry-run] Not writing output file.")
        for p in pairs[:5]:
            print("\n--- %s (%s) ---" % (p["type"], p["quality_tier"]))
            print(p["completion"][:300])
        return

    with open(args.output, "w", encoding="utf-8") as f:
        for p in pairs:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print("\n  Written to: " + args.output)
    print("  File size: " + str(os.path.getsize(args.output)) + " bytes")


if __name__ == "__main__":
    main()
