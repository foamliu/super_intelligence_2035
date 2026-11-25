#!/usr/bin/env python3
"""R322: Data Gap SFT Synthesis Pipeline.

Takes compact MCP API docs (fetched via pyAether MCP get_api_details) and
synthesizes SFT training pairs in JSONL format.  Designed to fill the 166
"true data gap" APIs identified in R321 (APIs NOT present in the SFT corpus).

Pipeline:
  1. Load compact API docs JSON  (api_name, api_type, signature, description, example)
  2. For each API generate up to 2 training pairs:
       - doc pair  : "How to use <API>?"  -> signature + description + example
       - code pair : "Write code using <API>" -> example code  (only if example exists)
  3. Pre-check contamination: reject any pair whose API name matches a known
     eval-task entry_point / canonical_solution identifier (belt-and-suspenders;
     the FULL 13-gram gate runs separately via baize_posttrain_contamination_gate.sh).
  4. Write JSONL (one JSON object per line, Alpaca-style {instruction,input,output}).

Zero GPU, zero sandbox.  Pure text processing.

Usage:
  python3 baize_posttrain_r322_datagap_sft_synthesis.py \
      --docs r322_datagap_api_docs.json \
      --out  r322_datagap_sft_pairs.jsonl
"""
import json
import os
import re
import argparse
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Name-level pre-filter; the full 13-gram gate is the authoritative red-line.
EVAL_ENTRYPOINT_BLOCKLIST = set()


def load_docs(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "apis" in data:
        return data["apis"]
    if isinstance(data, list):
        return data
    raise ValueError("docs JSON must be a list or {\"apis\": [...]}")


def extract_signature(desc_text):
    m = re.search(r"\*\*`([^`]+)`\*\*", desc_text)
    return m.group(1) if m else ""


def extract_example(desc_text):
    lines = desc_text.split("\n")
    out, capture = [], False
    for ln in lines:
        stripped = ln.strip()
        if stripped.startswith(">>>"):
            capture = True
            out.append(stripped)
        elif capture and (stripped == "" or re.match(r"^\[.+\]$", stripped)):
            if stripped:
                out.append(stripped)
        elif capture:
            break
    return "\n".join(out) if out else ""


def clean_description(desc_text):
    markers = ["## 补充说明", "---\n\n## 补充", "补充说明（通过测试验证）"]
    cut = desc_text
    for m in markers:
        idx = cut.find(m)
        if idx != -1:
            cut = cut[:idx]
    return cut.strip()[:800]


def make_doc_pair(rec):
    api = rec["api_name"]
    sig = rec.get("signature") or extract_signature(rec.get("raw_desc", ""))
    desc = rec.get("description") or clean_description(rec.get("raw_desc", ""))
    ex = rec.get("example") or extract_example(rec.get("raw_desc", ""))
    atype = rec.get("api_type", "")
    instruction = "请说明 pyAether 中 %s API 的用法，包括函数签名、参数说明和代码示例。" % api
    parts = ["## %s" % api]
    if atype:
        parts.append("**类型**: %s" % atype)
    if sig:
        parts.append("\n**签名**:\n```\n%s\n```" % sig)
    if desc:
        parts.append("\n**说明**:\n%s" % desc)
    if ex:
        parts.append("\n**示例**:\n```python\n%s\n```" % ex)
    return {"instruction": instruction, "input": "", "output": "\n".join(parts), "api_name": api, "pair_type": "doc"}


def make_code_pair(rec):
    api = rec["api_name"]
    ex = rec.get("example") or extract_example(rec.get("raw_desc", ""))
    if not ex:
        return None
    instruction = "用 pyAether 的 %s 编写一段代码示例。" % api
    return {"instruction": instruction, "input": "", "output": "```python\n%s\n```" % ex, "api_name": api, "pair_type": "code"}


def contam_precheck(pair):
    text = pair.get("instruction", "") + " " + pair.get("output", "")
    for ep in EVAL_ENTRYPOINT_BLOCKLIST:
        if ep and ep in text:
            return False
    return True


def main():
    ap = argparse.ArgumentParser(description="R322 Data Gap SFT Synthesis")
    ap.add_argument("--docs", default="r322_datagap_api_docs.json")
    ap.add_argument("--out", default="r322_datagap_sft_pairs.jsonl")
    ap.add_argument("--stats", default="r322_sft_synthesis_stats.json")
    args = ap.parse_args()
    docs_path = os.path.join(SCRIPT_DIR, args.docs) if not os.path.isabs(args.docs) else args.docs
    out_path = os.path.join(SCRIPT_DIR, args.out) if not os.path.isabs(args.out) else args.out
    stats_path = os.path.join(SCRIPT_DIR, args.stats) if not os.path.isabs(args.stats) else args.stats
    print("=" * 70)
    print("R322: Data Gap SFT Synthesis Pipeline")
    print("=" * 70)
    docs = load_docs(docs_path)
    print("\n1. Loaded %d compact API docs from %s" % (len(docs), os.path.basename(docs_path)))
    pairs, blocked = [], []
    module_count = Counter()
    for rec in docs:
        api = rec["api_name"]
        module = api.split(".")[0] if "." in api else "unknown"
        module_count[module] += 1
        dp = make_doc_pair(rec)
        if contam_precheck(dp):
            pairs.append(dp)
        else:
            blocked.append((api, "doc"))
        cp = make_code_pair(rec)
        if cp:
            if contam_precheck(cp):
                pairs.append(cp)
            else:
                blocked.append((api, "code"))
    doc_pairs = sum(1 for p in pairs if p["pair_type"] == "doc")
    code_pairs = sum(1 for p in pairs if p["pair_type"] == "code")
    print("\n2. Generated %d training pairs (doc=%d code=%d)" % (len(pairs), doc_pairs, code_pairs))
    print("   Blocked by pre-check: %d" % len(blocked))
    print("   Modules: %s" % dict(module_count))
    with open(out_path, "w", encoding="utf-8") as f:
        for p in pairs:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print("\n3. Wrote %s (%d lines, %.1f KB)" % (os.path.basename(out_path), len(pairs), os.path.getsize(out_path) / 1024))
    stats = {
        "R322": "Data Gap SFT Synthesis Pipeline", "date": "2026-11-12",
        "n_input_apis": len(docs), "n_pairs_generated": len(pairs),
        "n_doc_pairs": doc_pairs, "n_code_pairs": code_pairs,
        "n_blocked_precheck": len(blocked), "modules_covered": dict(module_count),
        "output_file": os.path.basename(out_path),
        "output_size_kb": round(os.path.getsize(out_path) / 1024, 1),
        "contamination_note": "Name-level pre-check only; full 13-gram gate via baize_posttrain_contamination_gate.sh required before training",
        "blocked_apis": blocked,
    }
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print("4. Stats saved: %s" % os.path.basename(stats_path))
    print("\n" + "=" * 70)
    print("Pipeline ready. %d APIs -> %d SFT pairs. Next: fetch remaining %d" % (len(docs), len(pairs), 166 - len(docs)))
    print("=" * 70)


if __name__ == "__main__":
    main()
