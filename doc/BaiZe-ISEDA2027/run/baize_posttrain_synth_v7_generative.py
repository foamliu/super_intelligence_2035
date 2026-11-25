#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""baize_posttrain_synth_v7_generative.py
R150 -- Generative Code-Example Completion for Missing Eval APIs.

The v6 corpus (R149, 352 pairs) covers only 186/488 eval APIs via authoritative
doctest extraction.  The remaining 302 APIs have no >>> examples in their docs.
Of those 302, 207 have R148 API-ref documentation (signatures, parameters,
returns).  This script uses the already-running MiniCPM5-2B vLLM serve at
localhost:8098 to *generate* a Python code example for each of those 207 APIs,
using the API documentation as context.

Contamination isolation (red line 5.1):
  - Source = API documentation (signatures + params + descriptions)
  - 158 eval tasks = prompt + test_code + canonical_solution
  - We feed ONLY API docs to the model; the 158 task prompts/assertions are
    never sent.  A contamination gate is run separately on the output.

Usage:
  python3 baize_posttrain_synth_v7_generative.py [--dry-run] [--limit N]
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time

import requests

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
EVAL_APIS_PATH = os.path.join(RUN_DIR, "pyAether_eval_488_apis.txt")
V6_CORPUS_PATH = os.path.join(RUN_DIR, "sft_pyaether_corpus_v6_method_examples.jsonl")
STATIC_CORPUS = os.path.join(RUN_DIR, "pyAether_api_ref_488.jsonl")
MCP_CORPUS = os.path.join(RUN_DIR, "pyAether_api_ref_mcp_enriched.jsonl")
OUT_PATH = os.path.join(RUN_DIR, "sft_pyaether_corpus_v7_generative.jsonl")
FAILED_PATH = os.path.join(RUN_DIR, "sft_pyaether_corpus_v7_generative.failed.txt")

VLLM_URL = "http://localhost:8098/v1/chat/completions"
VLLM_MODEL = "minicpm5-2b"

METHOD_HEADER_RE = re.compile(
    r"^(?:\*static\*\s+)?`([A-Za-z_][A-Za-z0-9_]*)`\s*\("
)
CODE_BLOCK_RE = re.compile(r"```(?:python)?\s*\n(.*?)```", re.DOTALL)
def load_eval_apis():
    with open(EVAL_APIS_PATH) as f:
        return set(line.strip() for line in f if line.strip())


def load_v6_apis():
    apis = set()
    if not os.path.isfile(V6_CORPUS_PATH):
        return apis
    with open(V6_CORPUS_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            apis.add(d.get("api_used", ""))
    return apis


def load_ref_corpus():
    refs = {}
    for path in [STATIC_CORPUS, MCP_CORPUS]:
        if not os.path.isfile(path):
            continue
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                refs[d["api_name"]] = d
    return refs





def extract_method_doc(desc_text, method_name):
    """Extract a single method's documentation block from a class
    api_descriptions text.  Returns the block text, or None if not found."""
    lines = desc_text.split("\n")
    current_name = None
    current_lines = []
    for line in lines:
        m = METHOD_HEADER_RE.match(line)
        if m:
            if current_name == method_name:
                return "\n".join(current_lines)
            current_name = m.group(1)
            current_lines = [line]
        else:
            if current_name is not None:
                current_lines.append(line)
    if current_name == method_name:
        return "\n".join(current_lines)
    return None

def build_doc_for_api(api_name, ref_corpus):
    """Build a documentation string for an API name.
    For class-level APIs return the full description (truncated).
    For method-level APIs extract just that method's block.
    Returns (doc_text, method_name_or_None) or (None, None)."""
    if api_name in ref_corpus:
        entry = ref_corpus[api_name]
        desc = entry.get("api_descriptions", "")
        if not desc:
            return None, None
        return desc[:3000], None
    parts = api_name.rsplit(".", 1)
    if len(parts) == 2:
        class_name, method_name = parts
        if class_name in ref_corpus:
            desc = ref_corpus[class_name].get("api_descriptions", "")
            if not desc:
                return None, None
            block = extract_method_doc(desc, method_name)
            if block:
                return block[:3000], method_name
            return desc[:2000], None
    return None, None


def build_prompt(api_name, doc_text, method_name):
    """Build the instruction prompt (same style as v6)."""
    method_spec = ""
    if method_name:
        method_spec = " method `{}`".format(method_name)
    prompt = (
        "You are an EDA automation assistant. Read the following PyAether API "
        "documentation and write Python code that correctly uses this API.\n\n"
        "## API Documentation\n\n{}\n\n"
        "## Task\n\n"
        "Write Python code that calls `{}`{} following the documentation above. "
        "Use the documented parameter types and return value correctly. "
        "Output ONLY a Python code block (```python ... ```) with no explanation."
    ).format(doc_text, api_name, method_spec)
    return prompt


def query_model(prompt, max_tokens=400, temperature=0.2, timeout=60):
    """Query the vLLM OpenAI-compatible endpoint with a code-only system msg."""
    payload = {
        "model": VLLM_MODEL,
        "messages": [
            {"role": "system", "content": "You are a Python code generator. "
             "Output ONLY a single Python code block using ```python ... ```. "
             "No reasoning, no explanation, no text outside the code block. "
             "Always start with 'import pyAether' and write real executable code."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    try:
        resp = requests.post(VLLM_URL, json=payload, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception:
        return None


def _clean_doctest(code):
    """Strip >>> and ... prefixes from doctest-style code lines."""
    cleaned = []
    for line in code.split("\n"):
        stripped = line.lstrip()
        if stripped.startswith(">>> "):
            cleaned.append(stripped[4:])
        elif stripped.startswith("... "):
            cleaned.append("    " + stripped[4:])
        elif stripped.startswith(">>>"):
            cleaned.append(stripped[3:])
        else:
            cleaned.append(line)
    return "\n".join(cleaned)


def extract_code(response):
    """Extract Python code from the model response.
    Strictly requires 'pyAether' or 'import' in the result."""
    if not response:
        return None
    blocks = CODE_BLOCK_RE.findall(response)
    candidates = []
    for block in blocks:
        cleaned = _clean_doctest(block.strip())
        if "pyAether" in cleaned or "import" in cleaned:
            candidates.append(cleaned)
    if candidates:
        return max(candidates, key=len)
    # Fallback: scan for lines that look like code with pyAether calls.
    # Only keep import lines and pyAether lines that have code structure
    # (paren or assignment), to avoid keeping prose that mentions pyAether.
    lines = []
    for line in response.split("\n"):
        stripped = line.strip()
        if stripped.startswith(">>> "):
            stripped = stripped[4:]
        if not stripped:
            continue
        if stripped.startswith("import ") or stripped.startswith("from "):
            lines.append(stripped)
            continue
        if "pyAether" in stripped and ("(" in stripped or "=" in stripped):
            lines.append(stripped)
    if lines and any("pyAether" in l for l in lines):
        return "\n".join(lines)
    return None


def wrap_as_function(code, api_name, method_name):
    """Wrap generated code in a function for clean training format."""
    code = _clean_doctest(code)
    func_name = "use_{}".format(
        method_name or api_name.replace(".", "_").replace("pyAether_", "")
    )
    import_lines = []
    body_lines = []
    for line in code.split("\n"):
        if line.strip().startswith("import ") or line.strip().startswith("from "):
            import_lines.append(line)
        elif line.strip():
            body_lines.append(line)
    wrapped = "\n".join(import_lines) + "\n"
    wrapped += "def {}():\n".format(func_name)
    for bl in body_lines:
        if bl.strip():
            wrapped += "    {}\n".format(bl)
    if not body_lines:
        wrapped += "    pass\n"
    return wrapped

def has_real_api_call(wrapped_code):
    """Check if wrapped code has actual pyAether API calls (not reasoning/prose).

    R151 fix: the old check rejected the ENTIRE block if any line contained a
    reasoning keyword (reasoning_lines == 0 requirement), causing false
    rejections when the small model emitted prose alongside/inside the code.
    Now we look for at least one line referencing pyAether.X (or its import
    alias) with code structure (a paren or assignment), ignoring prose lines.
    """
    call_re = re.compile(r'\b(?:pyAether|pyScript|pa|ae)\s*\.\s*[A-Za-z_][A-Za-z0-9_]*')
    for line in wrapped_code.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(("def ", "import ", "from ", "#", '"""', "'''")):
            continue
        if not call_re.search(stripped):
            continue
        # Line references an API -- accept if it looks like code (paren/assign),
        # distinguishing from prose mentions like "we need to call pyAether.X".
        if "(" in stripped or "=" in stripped:
            return True
    return False


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="Print stats only, do not query model or write output")
    ap.add_argument("--limit", type=int, default=0,
                    help="Max APIs to process (0 = all 207)")
    ap.add_argument("--out", default=OUT_PATH, help="Output JSONL path")
    ap.add_argument("--delay", type=float, default=0.5,
                    help="Delay between API calls in seconds")
    args = ap.parse_args()

    print("[R150] loading eval APIs ...")
    eval_apis = load_eval_apis()
    print("[R150]   eval APIs: {}".format(len(eval_apis)))
    v6_apis = load_v6_apis()
    print("[R150]   v6 covered: {}".format(len(v6_apis)))
    ref_corpus = load_ref_corpus()
    print("[R150]   R148 ref entries: {}".format(len(ref_corpus)))

    missing = eval_apis - v6_apis
    has_doc = sorted(missing & set(ref_corpus.keys()))
    no_doc = sorted(missing - set(ref_corpus.keys()))
    print("[R150]   missing total: {}".format(len(missing)))
    print("[R150]     with doc (generative): {}".format(len(has_doc)))
    print("[R150]     no doc (skip): {}".format(len(no_doc)))

    if args.limit > 0:
        has_doc = has_doc[:args.limit]
        print("[R150]   --limit: processing {}".format(len(has_doc)))

    if args.dry_run:
        print("[R150] --dry-run: not querying model or writing output")
        for a in has_doc[:5]:
            doc, method = build_doc_for_api(a, ref_corpus)
            print("  {} (method={}, doc_len={})".format(
                a, method, len(doc) if doc else 0))
        return

    pairs = []
    failed = []
    seen_hashes = set()

    for i, api_name in enumerate(has_doc):
        doc_text, method_name = build_doc_for_api(api_name, ref_corpus)
        if not doc_text:
            failed.append((api_name, "no_doc_extracted"))
            continue
        prompt = build_prompt(api_name, doc_text, method_name)
        if i > 0:
            time.sleep(args.delay)
        response = query_model(prompt)
        if not response:
            failed.append((api_name, "model_no_response"))
            continue
        code = extract_code(response)
        if not code or len(code) < 15:
            failed.append((api_name, "no_code_extracted"))
            continue
        code_hash = hashlib.md5(code.encode()).hexdigest()
        dedup_key = (api_name, method_name or "__class__", code_hash)
        if dedup_key in seen_hashes:
            continue
        seen_hashes.add(dedup_key)
        wrapped = wrap_as_function(code, api_name, method_name)
        if not has_real_api_call(wrapped):
            failed.append((api_name, "no_real_api_call"))
            continue
        pair = {
            "pair_id": "R150-{}".format(code_hash[:10]),
            "type": "R150_generative_example",
            "prompt": prompt,
            "completion": "```python\n{}\n```".format(wrapped),
            "api_used": api_name,
            "method": method_name or "",
            "source": "R148_doc_generative",
            "model": VLLM_MODEL,
            "contamination_check": "pending",
        }
        pairs.append(pair)
        if (i + 1) % 20 == 0:
            print("[R150]   {}/{} done, {} pairs so far".format(
                i + 1, len(has_doc), len(pairs)))

    print("[R150] generation complete: {} pairs, {} failed".format(
        len(pairs), len(failed)))
    by_reason = {}
    for _, reason in failed:
        by_reason[reason] = by_reason.get(reason, 0) + 1
    for r, c in sorted(by_reason.items()):
        print("  failed {}: {}".format(r, c))
    apis_covered = set(p["api_used"] for p in pairs)
    print("[R150] unique APIs covered by v7: {}".format(len(apis_covered)))
    combined = v6_apis | apis_covered
    print("[R150] combined v6+v7 coverage: {} / 488 ({:.1f}%)".format(
        len(combined), 100.0 * len(combined) / 488))

    with open(args.out, "w") as f:
        for p in pairs:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    sz = os.path.getsize(args.out)
    print("[R150] wrote {} ({} bytes, {} pairs)".format(
        args.out, sz, len(pairs)))
    with open(FAILED_PATH, "w") as f:
        for api, reason in failed:
            f.write("{}\t{}\n".format(api, reason))
    print("[R150] wrote {} ({} failures)".format(FAILED_PATH, len(failed)))


if __name__ == "__main__":
    main()

