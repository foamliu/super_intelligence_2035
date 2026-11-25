#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""baize_posttrain_synth_v6_method_examples.py
R149 -- Method-Level Authoritative-Example Extraction from R148 API Ref Corpus.

The v5 corpus (1193 pairs) covers all 488 eval APIs but its completions are
shallow LLM-generated stubs. The R148 API ref corpus (400 entries) embeds
authoritative >>> import pyAether example code blocks inside each method's
documentation. This script parses those method blocks and extracts the
documented example as the completion, producing high-quality doc-to-code
training pairs where the target is ground-truth API usage.

Contamination isolation (red line 5.1):
  - Source = API documentation (signatures + params + examples)
  - 158 eval tasks = prompt + test_code + canonical_solution
  - API docs != task solutions; we extract ONLY documented >>> examples.

Usage:
  python3 baize_posttrain_synth_v6_method_examples.py [--dry-run] [--limit N]
"""
import argparse
import hashlib
import json
import os
import re
import sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_CORPUS = os.path.join(RUN_DIR, "pyAether_api_ref_488.jsonl")
MCP_CORPUS = os.path.join(RUN_DIR, "pyAether_api_ref_mcp_enriched.jsonl")
OUT_PATH = os.path.join(RUN_DIR, "sft_pyaether_corpus_v6_method_examples.jsonl")

# A method block header: *static* `name`(...)  or  `name`(...)
METHOD_HEADER_RE = re.compile(
    r"^(?:\*static\*\s+)?`([A-Za-z_][A-Za-z0-9_]*)`\s*\("
)
# Bold signature line: **`signature`** description
BOLD_SIG_RE = re.compile(r"^\*\*`([^`]+)`\*\*\s*(.*)")
# Examples section marker
EXAMPLES_RE = re.compile(r"^Examples\s*$", re.MULTILINE)
# A >>> example line (indented then >>> prompt)
DOCTEST_LINE_RE = re.compile(r"^ {0,8}>>> ?(.*)$")


def _has_doctest(text):
    return bool(DOCTEST_LINE_RE.search(text))


def split_method_blocks(desc_text):
    """Split a class api_descriptions into per-method text blocks."""
    lines = desc_text.split("\n")
    blocks = []
    current_name = None
    current_lines = []
    preamble_lines = []

    for line in lines:
        m = METHOD_HEADER_RE.match(line)
        if m:
            if current_name is not None:
                blocks.append({"method_name": current_name,
                               "block_text": "\n".join(current_lines)})
            else:
                preamble_lines.extend(current_lines)
            current_name = m.group(1)
            current_lines = [line]
        else:
            if current_name is not None:
                current_lines.append(line)
            else:
                preamble_lines.append(line)

    if current_name is not None:
        blocks.append({"method_name": current_name,
                       "block_text": "\n".join(current_lines)})

    preamble_text = "\n".join(preamble_lines).strip()
    if preamble_text and _has_doctest(preamble_text):
        blocks.insert(0, {"method_name": "__init__",
                          "block_text": preamble_text})
    return blocks


def extract_doctest_code(block_text):
    """Extract >>> example lines from a method block, return cleaned code."""
    lines = block_text.split("\n")
    code_lines = []
    in_examples = False
    for line in lines:
        if EXAMPLES_RE.match(line):
            in_examples = True
            continue
        if in_examples:
            m = DOCTEST_LINE_RE.match(line)
            if m:
                code_lines.append(m.group(1))
            elif line.strip() == "" and code_lines:
                continue
            elif line.strip() and not line.startswith(" " * 4):
                break
    return "\n".join(code_lines).strip()


def extract_method_doc(block_text):
    """Extract method doc (signature+params+returns), strip Examples section."""
    m = EXAMPLES_RE.search(block_text)
    if m:
        return block_text[: m.start()].strip()
    return block_text.strip()


def wrap_as_function(code):
    """Ensure import line present; keep code as-is (module-level examples)."""
    if "import pyAether" not in code:
        code = "import pyAether\n" + code
    return code


def build_pair(api_name, method_name, method_doc, example_code, source):
    """Build one training pair dict (v5-compatible schema)."""
    short_name = api_name.replace("pyAether.", "")
    full_method = (short_name + "." + method_name
                   if method_name != "__init__" else short_name)
    prompt = (
        "You are an EDA automation assistant. Read the following PyAether "
        "API documentation and write Python code that correctly uses this "
        "API.\n\n## API Documentation\n\n{}\n\n## Task\n\nWrite Python code "
        "that calls `{}` following the documentation above. Use the "
        "documented parameter types and return value correctly."
    ).format(method_doc, full_method)
    completion = "```python\n{}\n```\n".format(example_code)
    pair_id_raw = "{}|{}|{}".format(api_name, method_name, example_code[:80])
    pair_id = "R149-" + hashlib.md5(pair_id_raw.encode()).hexdigest()[:10]
    return {
        "pair_id": pair_id,
        "type": "R149_method_example",
        "prompt": prompt,
        "completion": completion,
        "api_used": api_name,
        "method": method_name,
        "source": source,
        "contamination_check": "pending",
    }


def process_corpus(path, source_label, limit, seen_hashes):
    """Process one corpus file, yield training pairs."""
    pairs = []
    if not os.path.isfile(path):
        return pairs
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            api_name = entry.get("api_name", "")
            desc = entry.get("api_descriptions", "")
            if not desc:
                continue
            for blk in split_method_blocks(desc):
                code = extract_doctest_code(blk["block_text"])
                if not code or len(code) < 15:
                    continue
                code_hash = hashlib.md5(code.encode()).hexdigest()
                dedup_key = (api_name, blk["method_name"], code_hash)
                if dedup_key in seen_hashes:
                    continue
                seen_hashes.add(dedup_key)
                method_doc = extract_method_doc(blk["block_text"])
                if len(method_doc) < 20:
                    method_doc = "API: {}\nMethod: {}".format(
                        api_name, blk["method_name"])
                wrapped = wrap_as_function(code)
                pairs.append(build_pair(
                    api_name, blk["method_name"], method_doc, wrapped,
                    source_label))
                if limit and len(pairs) >= limit:
                    return pairs
    return pairs


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="Print stats only, do not write output")
    ap.add_argument("--limit", type=int, default=0,
                    help="Max pairs to generate (0 = unlimited)")
    ap.add_argument("--out", default=OUT_PATH, help="Output JSONL path")
    args = ap.parse_args()

    seen = set()
    all_pairs = []
    static_pairs = process_corpus(
        STATIC_CORPUS, "R148_static_json", args.limit, seen)
    all_pairs.extend(static_pairs)
    print("[R149] static corpus: {} pairs".format(len(static_pairs)))
    remaining = args.limit - len(all_pairs) if args.limit else 0
    mcp_pairs = process_corpus(
        MCP_CORPUS, "R148_mcp_enriched", remaining, seen)
    all_pairs.extend(mcp_pairs)
    print("[R149] mcp enriched:   {} pairs".format(len(mcp_pairs)))
    print("[R149] total unique pairs: {}".format(len(all_pairs)))

    by_source = {}
    for p in all_pairs:
        by_source[p["source"]] = by_source.get(p["source"], 0) + 1
    for s, c in sorted(by_source.items()):
        print("  {}: {}".format(s, c))
    apis = set(p["api_used"] for p in all_pairs)
    print("[R149] unique APIs with examples: {} / 488 eval APIs".format(
        len(apis)))

    if args.dry_run:
        print("[R149] --dry-run: not writing output file")
        if all_pairs:
            s = all_pairs[0]
            print("\n--- SAMPLE PAIR ---")
            print("pair_id:", s["pair_id"])
            print("api:", s["api_used"], "method:", s["method"])
            print("prompt (first 400):", s["prompt"][:400])
            print("completion (first 400):", s["completion"][:400])
        return

    with open(args.out, "w") as f:
        for p in all_pairs:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    sz = os.path.getsize(args.out)
    print("[R149] wrote {} ({} bytes, {} pairs)".format(
        args.out, sz, len(all_pairs)))


if __name__ == "__main__":
    main()
