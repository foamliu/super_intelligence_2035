#!/usr/bin/env python3
"""R323: Fetch data-gap API docs from local pyAether KB (zero GPU, zero sandbox).

Extracts compact API docs for the 158 remaining data-gap APIs (166 total - 8 PoC)
from the local eda_fastmcp knowledge base at:
  /home/app.e0031982/code/eda_fastmcp/docs/API_INFO_MERGED_V3.json

APIs not found in the local KB are reported as "needs_mcp" for subsequent
fetching via pyAether MCP get_api_details.

Output: r323_datagap_api_docs_local.json  (compact docs for local-found APIs)
        r323_datagap_needs_mcp.txt        (list of APIs needing MCP fetch)

Usage:
  python3 baize_posttrain_r323_datagap_fetch_local.py
"""
import json
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KB_PATH = "/home/app.e0031982/code/eda_fastmcp/docs/API_INFO_MERGED_V3.json"
R321_PATH = os.path.join(SCRIPT_DIR, "r321_missing_api_coverage.json")
R322_POC_PATH = os.path.join(SCRIPT_DIR, "r322_datagap_api_docs.json")
OUT_DOCS = os.path.join(SCRIPT_DIR, "r323_datagap_api_docs_local.json")
OUT_NEEDS_MCP = os.path.join(SCRIPT_DIR, "r323_datagap_needs_mcp.txt")


def extract_signature(desc_text):
    """Extract function signature from raw description text."""
    m = re.search(r"\*\*`([^`]+)`\*\*", desc_text)
    return m.group(1) if m else ""


def extract_example(desc_text):
    """Extract >>> example lines from raw description text."""
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
    """Cut at supplementary notes markers, truncate to 800 chars."""
    markers = ["## 补充说明", "---\n\n## 补充", "补充说明（通过测试验证）",
               "## 测试经验总结", "## 测试验证结果"]
    cut = desc_text
    for m in markers:
        idx = cut.find(m)
        if idx != -1:
            cut = cut[:idx]
    return cut.strip()[:800]


def main():
    print("=" * 70)
    print("R323: Data Gap API Docs - Local KB Extraction")
    print("=" * 70)

    # Load data gap APIs
    r321 = json.load(open(R321_PATH, encoding="utf-8"))
    poc = json.load(open(R322_POC_PATH, encoding="utf-8"))["apis"]
    done = set(r["api_name"] for r in poc)
    remaining = [a for a in r321["not_covered_apis"] if a not in done]
    print("\n1. Data gap APIs: %d total, %d PoC done, %d remaining" %
          (len(r321["not_covered_apis"]), len(done), len(remaining)))

    # Load local KB
    print("\n2. Loading local KB: %s" % KB_PATH)
    kb = json.load(open(KB_PATH, encoding="utf-8"))
    print("   KB has %d API entries" % len(kb))

    # Extract docs for local-found APIs
    docs = []
    needs_mcp = []
    for api in remaining:
        rec = kb.get(api)
        if rec is None:
            needs_mcp.append(api)
            continue
        raw_desc = rec.get("api_descriptions", "")
        sig = extract_signature(raw_desc)
        desc = clean_description(raw_desc)
        ex = extract_example(raw_desc)
        docs.append({
            "api_name": api,
            "api_type": rec.get("api_type", ""),
            "signature": sig,
            "description": desc,
            "example": ex,
            "raw_desc": raw_desc[:2000],
            "source": "local_kb"
        })

    print("\n3. Local KB found: %d / %d" % (len(docs), len(remaining)))
    print("   Needs MCP fetch: %d" % len(needs_mcp))

    # Write outputs
    out_data = {
        "R323_source": "local_kb_extraction",
        "description": "Compact API docs extracted from API_INFO_MERGED_V3.json for data-gap APIs",
        "n_local_found": len(docs),
        "n_needs_mcp": len(needs_mcp),
        "apis": docs
    }
    with open(OUT_DOCS, "w", encoding="utf-8") as f:
        json.dump(out_data, f, ensure_ascii=False, indent=2)
    print("\n4. Wrote %s (%d APIs, %.1f KB)" %
          (os.path.basename(OUT_DOCS), len(docs), os.path.getsize(OUT_DOCS) / 1024))

    with open(OUT_NEEDS_MCP, "w", encoding="utf-8") as f:
        for api in needs_mcp:
            f.write(api + "\n")
    print("   Wrote %s (%d APIs needing MCP)" %
          (os.path.basename(OUT_NEEDS_MCP), len(needs_mcp)))

    # Summary by module
    from collections import Counter
    mod_count = Counter(d["api_name"].split(".")[0] if "." in d["api_name"] else "unknown" for d in docs)
    print("\n5. Local-found by module:")
    for mod, cnt in mod_count.most_common(15):
        print("   %s: %d" % (mod, cnt))

    print("\n" + "=" * 70)
    print("Next: fetch %d APIs via MCP, merge with %d local, run synthesis" %
          (len(needs_mcp), len(docs)))
    print("=" * 70)


if __name__ == "__main__":
    main()
