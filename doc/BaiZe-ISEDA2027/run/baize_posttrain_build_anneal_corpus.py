#!/usr/bin/env python3
"""baize_posttrain_build_anneal_corpus.py — Build PyAether domain annealing corpus (R153).

Flattens the R148 API-reference JSONL corpus (pyAether_api_ref_488.jsonl +
pyAether_api_ref_mcp_enriched.jsonl) into a plain-text annealing corpus
(one JSONL doc per API, field "text"), suitable for the domain annealing
blend (domain30:web50:code12:math8) in baize_posttrain_anneal.sh.

This is the SOURCE material; tokenization to mcore .bin/.idx (the DOMAIN_DATA
path the anneal script consumes) is a data-line task, requested post-build.

Red line (total outline 5.1): corpus = API reference docs
(signatures / params / returns / usage examples) ONLY; the 158 eval-task
prompts / entry_points / assertions / canonical solutions NEVER enter.
Verified by baize_posttrain_contamination_gate.sh post-build (expect PASS:
API docs are the tasks' "source material", not their solutions).

Usage:
    python3 baize_posttrain_build_anneal_corpus.py
    python3 baize_posttrain_build_anneal_corpus.py --help
"""
import argparse
import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
STATIC_JSONL = SCRIPT_DIR / "pyAether_api_ref_488.jsonl"
MCP_JSONL = SCRIPT_DIR / "pyAether_api_ref_mcp_enriched.jsonl"
OUT_JSONL = SCRIPT_DIR / "pyAether_api_anneal_corpus.jsonl"

# token estimate divisor (consistent with prior wakes: chars / 3.7)
CHARS_PER_TOK = 3.7


def load_jsonl(path):
    entries = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
    return entries


def build_doc(entry, source_tag):
    """Render one API entry as a self-contained plain-text doc block."""
    api_name = entry.get("api_name", "")
    api_type = entry.get("api_type", "")
    desc = entry.get("api_descriptions", "")
    category = entry.get("category", "")
    header = [
        "# PyAether API Reference: " + api_name,
        "api_name: " + api_name,
        "api_type: " + api_type,
    ]
    if category:
        header.append("category: " + str(category))
    header.append("source: " + source_tag)
    header.append("")
    return "\n".join(header) + (desc or "")


def main():
    ap = argparse.ArgumentParser(description="Build PyAether domain annealing corpus from R148 API-ref JSONL.")
    ap.add_argument("--static", default=str(STATIC_JSONL), help="static API-ref JSONL (pyAether_api_ref_488.jsonl)")
    ap.add_argument("--mcp", default=str(MCP_JSONL), help="MCP-enriched API-ref JSONL (pyAether_api_ref_mcp_enriched.jsonl)")
    ap.add_argument("--out", default=str(OUT_JSONL), help="output anneal corpus JSONL (one doc per API, field=text)")
    ap.add_argument("--chars-per-tok", type=float, default=CHARS_PER_TOK, help="chars-per-token estimate for ~token count")
    args = ap.parse_args()

    static_entries = load_jsonl(Path(args.static))
    mcp_entries = load_jsonl(Path(args.mcp))

    seen = set()
    docs = []
    for e in static_entries:
        nm = e.get("api_name", "")
        if not nm or nm in seen:
            continue
        seen.add(nm)
        docs.append({
            "text": build_doc(e, "R148-static(API_INFO_MERGED_V3.json)"),
            "api_name": nm,
            "api_type": e.get("api_type", ""),
            "category": e.get("category", ""),
            "source": "R148-static",
        })
    static_kept = len(docs)
    mcp_added = 0
    for e in mcp_entries:
        nm = e.get("api_name", "")
        if not nm or nm in seen:
            continue
        seen.add(nm)
        docs.append({
            "text": build_doc(e, "R148-mcp(get_api_details)"),
            "api_name": nm,
            "api_type": e.get("api_type", ""),
            "category": e.get("category", ""),
            "source": "R148-mcp",
        })
        mcp_added += 1

    with open(args.out, "w", encoding="utf-8") as f:
        for d in docs:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    total_chars = sum(len(d["text"]) for d in docs)
    total_bytes = os.path.getsize(args.out)
    est_tok = total_chars / args.chars_per_tok
    print("===== R153 Anneal Corpus Build =====")
    print("static_entries  :", len(static_entries))
    print("mcp_entries     :", len(mcp_entries))
    print("dedup docs      :", len(docs), "(static kept " + str(static_kept) + " + mcp-only " + str(mcp_added) + ")")
    print("total_chars     :", total_chars)
    print("~tokens         : %.1fK" % (est_tok / 1000.0))
    print("out_bytes       :", total_bytes, "(%.2f MB)" % (total_bytes / 1048576.0))
    print("out             :", args.out)
    print("field           : text (one doc per API; check_contamination.py scans per-doc)")
    print("next            : bash baize_posttrain_contamination_gate.sh --anneal-corpus <out> --out /tmp/r.md")
    print("=====================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
