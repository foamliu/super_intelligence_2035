#!/usr/bin/env python3
"""R323: Merge all data-gap API docs and synthesize full SFT v38 pairs.
Sources: PoC(8) + local_kb(104) + mcp(18) + stubs(36) = 166 data gap APIs.
Zero GPU, zero sandbox. Pure text processing.
"""
import json, os, re
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
R321_PATH = os.path.join(SCRIPT_DIR, "r321_missing_api_coverage.json")
R322_POC_PATH = os.path.join(SCRIPT_DIR, "r322_datagap_api_docs.json")
LOCAL_PATH = os.path.join(SCRIPT_DIR, "r323_datagap_api_docs_local.json")
MCP_PATH = os.path.join(SCRIPT_DIR, "r323_mcp_api_docs.json")
STUB_PATH = os.path.join(SCRIPT_DIR, "r323_stub_api_docs.json")
OUT_DOCS = os.path.join(SCRIPT_DIR, "r323_datagap_api_docs_full.json")
OUT_PAIRS = os.path.join(SCRIPT_DIR, "r323_datagap_sft_pairs.jsonl")
OUT_STATS = os.path.join(SCRIPT_DIR, "r323_sft_synthesis_stats.json")

def extract_signature(t):
    m = re.search(r"\*\*`([^`]+)`\*\*", t)
    return m.group(1) if m else ""

def extract_example(t):
    lines = t.split("\n"); out = []; cap = False
    for ln in lines:
        s = ln.strip()
        if s.startswith(">>>"): cap = True; out.append(s)
        elif cap and (s == "" or re.match(r"^\[.+\]$", s)):
            if s: out.append(s)
        elif cap: break
    return "\n".join(out) if out else ""

def clean_desc(t):
    for m in ["## \u8865\u5145\u8bf4\u660e", "---\n\n## \u8865\u5145", "\u8865\u5145\u8bf4\u660e\uff08\u901a\u8fc7\u6d4b\u8bd5\u9a8c\u8bc1\uff09", "## \u6d4b\u8bd5\u7ecf\u9a8c\u603b\u7ed3", "## \u6d4b\u8bd5\u9a8c\u8bc1\u7ed3\u679c"]:
        idx = t.find(m)
        if idx != -1: t = t[:idx]
    return t.strip()[:800]

def make_doc_pair(rec):
    api = rec["api_name"]
    sig = rec.get("signature") or extract_signature(rec.get("raw_desc", ""))
    desc = rec.get("description") or clean_desc(rec.get("raw_desc", ""))
    ex = rec.get("example") or extract_example(rec.get("raw_desc", ""))
    at = rec.get("api_type", "")
    inst = "\u8bf7\u8bf4\u660e pyAether \u4e2d %s API \u7684\u7528\u6cd5\uff0c\u5305\u62ec\u51fd\u6570\u7b7e\u540d\u3001\u53c2\u6570\u8bf4\u660e\u548c\u4ee3\u7801\u793a\u4f8b\u3002" % api
    parts = ["## %s" % api]
    if at: parts.append("**\u7c7b\u578b**: %s" % at)
    if sig: parts.append("\n**\u7b7e\u540d**:\n```\n%s\n```" % sig)
    if desc: parts.append("\n**\u8bf4\u660e**:\n%s" % desc)
    if ex: parts.append("\n**\u793a\u4f8b**:\n```python\n%s\n```" % ex)
    return {"instruction": inst, "input": "", "output": "\n".join(parts), "api_name": api, "pair_type": "doc"}

def make_code_pair(rec):
    api = rec["api_name"]
    ex = rec.get("example") or extract_example(rec.get("raw_desc", ""))
    if not ex: return None
    return {"instruction": "\u7528 pyAether \u7684 %s \u7f16\u5199\u4e00\u6bb5\u4ee3\u7801\u793a\u4f8b\u3002" % api, "input": "", "output": "```python\n%s\n```" % ex, "api_name": api, "pair_type": "code"}

def main():
    print("=" * 70); print("R323: Full Data Gap SFT Synthesis (166 APIs)"); print("=" * 70)
    r321 = json.load(open(R321_PATH, encoding="utf-8"))
    all_apis = r321["not_covered_apis"]
    print("\n1. Total data gap APIs: %d" % len(all_apis))
    poc = json.load(open(R322_POC_PATH, encoding="utf-8"))["apis"]
    local = json.load(open(LOCAL_PATH, encoding="utf-8"))["apis"]
    mcp_raw = json.load(open(MCP_PATH, encoding="utf-8"))
    stubs_raw = json.load(open(STUB_PATH, encoding="utf-8"))
    mcp_docs = [{"api_name": k, "api_type": v["api_type"], "signature": extract_signature(v["raw_desc"]),
                 "description": clean_desc(v["raw_desc"]), "example": extract_example(v["raw_desc"]),
                 "raw_desc": v["raw_desc"], "source": "mcp"} for k, v in mcp_raw.items()]
    stub_docs = [{"api_name": k, "api_type": "enum" if k.startswith("emc") else "callback" if "CallBack" in k else "method",
                  "signature": "", "description": v, "example": "", "raw_desc": v, "source": "stub"} for k, v in stubs_raw.items()]
    print("   PoC(R322): %d | Local KB: %d | MCP: %d | Stubs: %d" % (len(poc), len(local), len(mcp_docs), len(stub_docs)))
    all_docs = {}
    for rec in poc + local + mcp_docs + stub_docs:
        if rec["api_name"] not in all_docs: all_docs[rec["api_name"]] = rec
    covered = set(all_docs.keys())
    missing = [a for a in all_apis if a not in covered]
    print("\n2. Merged: %d unique | Coverage: %d/%d (%.1f%%)" % (len(all_docs), len(covered & set(all_apis)), len(all_apis), 100.0 * len(covered & set(all_apis)) / len(all_apis)))
    if missing: print("   Missing: %d - %s" % (len(missing), missing[:15]))
    docs_list = [all_docs[a] for a in all_apis if a in all_docs]
    out_data = {"R323_source": "merged_full", "n_total_data_gap": len(all_apis), "n_covered": len(docs_list), "n_missing": len(missing), "apis": docs_list}
    with open(OUT_DOCS, "w", encoding="utf-8") as f: json.dump(out_data, f, ensure_ascii=False, indent=2)
    print("\n3. Wrote %s (%d APIs, %.1f KB)" % (os.path.basename(OUT_DOCS), len(docs_list), os.path.getsize(OUT_DOCS) / 1024))
    print("\n4. Synthesizing SFT pairs...")
    pairs = []
    for rec in docs_list:
        dp = make_doc_pair(rec)
        if dp: pairs.append(dp)
        cp = make_code_pair(rec)
        if cp: pairs.append(cp)
    doc_pairs = sum(1 for p in pairs if p["pair_type"] == "doc")
    code_pairs = sum(1 for p in pairs if p["pair_type"] == "code")
    mod_count = Counter(d["api_name"].split(".")[0] if "." in d["api_name"] else "unknown" for d in docs_list)
    src_count = Counter(rec.get("source", "unknown") for rec in docs_list)
    with open(OUT_PAIRS, "w", encoding="utf-8") as f:
        for p in pairs: f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print("   Generated %d pairs (doc=%d code=%d, %.1f KB)" % (len(pairs), doc_pairs, code_pairs, os.path.getsize(OUT_PAIRS) / 1024))
    stats = {"R323": "Full Data Gap SFT Synthesis", "date": "2026-11-12", "n_input_apis": len(docs_list),
             "n_total_data_gap": len(all_apis), "n_missing": len(missing), "n_pairs_generated": len(pairs),
             "n_doc_pairs": doc_pairs, "n_code_pairs": code_pairs, "sources": dict(src_count),
             "modules_covered": dict(mod_count.most_common(20)), "output_file": os.path.basename(OUT_PAIRS),
             "output_size_kb": round(os.path.getsize(OUT_PAIRS) / 1024, 1),
             "contamination_note": "Name-level pre-check only; full 13-gram gate required before training"}
    with open(OUT_STATS, "w", encoding="utf-8") as f: json.dump(stats, f, indent=2, ensure_ascii=False)
    print("   Stats: %s" % os.path.basename(OUT_STATS))
    print("\n" + "=" * 70)
    print("DONE: %d APIs -> %d SFT pairs. Coverage: %d/%d" % (len(docs_list), len(pairs), len(docs_list), len(all_apis)))
    print("=" * 70)

if __name__ == "__main__":
    main()
