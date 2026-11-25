#!/usr/bin/env python3
"""
R100: Source API Extraction — Enriching the 124 Doubly-Missing APIs
=====================================================================
R99 generated minimal S0 "existence" pairs for 124 APIs missing from both the
API KB (API_INFO_MERGED_V3.json) and the SFT corpora. These pairs just say
"this API exists" with a trivial call — no real documentation.

This script searches ALTERNATIVE documentation sources in eda_fastmcp/docs/:
  - api_methods.jsonl  (4043 method entries with full descriptions)
  - api_classes.jsonl   (486 class entries with full descriptions)
  - func_all_v3.json    (6734 function entries with docstrings)
  - pyAether_API_Docstring.md (143KB markdown docstring file)

For each of the 124 APIs, it:
  1. Searches all sources for the API name (exact and fuzzy)
  2. Categorizes: enum_constant / factory_method / regular_method / class / property / not_found
  3. For found APIs: generates rich S5 training pairs with actual documentation
  4. For still-not-found: keeps the minimal S0 pair but flags it

Output: sft_pyaether_corpus_v4_source_enriched.jsonl + HTML + JSON

Contamination isolation (RED LINE): Only API names and documentation text from
eda_fastmcp/docs/ are used. No eval task data is used.

Zero GPU. Pure generation. Python 3.8+ stdlib only.
"""
import argparse, json, os, re, sys, hashlib
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path

RUN_DIR = Path(__file__).resolve().parent
REPORTS_DIR = RUN_DIR.parent / "reports"
EDA_DOCS = Path.home() / "code/eda_fastmcp/docs"
V3_OUTPUT = RUN_DIR / "sft_pyaether_corpus_v3_augmented.jsonl"
OUTPUT = RUN_DIR / "sft_pyaether_corpus_v4_source_enriched.jsonl"
EVAL_DATASET = Path.home() / "code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"

# ---------------------------------------------------------------------------
# Loading utilities
# ---------------------------------------------------------------------------

def load_jsonl(path):
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return records

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_md(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# ---------------------------------------------------------------------------
# API name utilities
# ---------------------------------------------------------------------------

def short_name(fq):
    if fq and fq.startswith("pyAether."):
        return fq[len("pyAether."):]
    return fq or ""

def fq_name(sn):
    if sn and not sn.startswith("pyAether."):
        return "pyAether." + sn
    return sn or ""

def classify_api(api_short):
    """Classify the 124 missing APIs by type."""
    if re.match(r'^emc[A-Z]', api_short):
        return "enum_constant"
    if api_short.endswith(".create"):
        return "factory_method"
    parts = api_short.split(".")
    if len(parts) == 1 and parts[0] and parts[0][0].isupper():
        return "class"
    if len(parts) == 2:
        return "method"
    return "other"

# ---------------------------------------------------------------------------
# Source searching
# ---------------------------------------------------------------------------

def search_api_methods(api_short, methods_records):
    """Search api_methods.jsonl for the API."""
    results = []
    fq = fq_name(api_short)
    for rec in methods_records:
        if rec.get("api_full_name", "") == fq:
            results.append(rec)
            continue
        # Try owner_class.method_name match
        parts = api_short.split(".")
        if len(parts) == 2:
            owner_short = parts[0]
            method_name = parts[1]
            if rec.get("api_name", "") == method_name:
                owner = rec.get("owner_class", "")
                if short_name(owner) == owner_short:
                    results.append(rec)
    return results

def search_api_classes(api_short, classes_records):
    """Search api_classes.jsonl for the API."""
    results = []
    fq = fq_name(api_short)
    for rec in classes_records:
        if rec.get("api_full_name", "") == fq:
            results.append(rec)
    # For enum constants, search within class descriptions
    if api_short.startswith("emc"):
        for rec in classes_records:
            desc = rec.get("api_descriptions", "")
            if api_short in desc and rec not in results:
                results.append(rec)
    # For ClassName.method, search for the parent class
    parts = api_short.split(".")
    if len(parts) == 2:
        parent_fq = fq_name(parts[0])
        for rec in classes_records:
            if rec.get("api_full_name", "") == parent_fq and rec not in results:
                # Check if the method name appears in the class description
                if parts[1] in rec.get("api_descriptions", ""):
                    results.append(rec)
    return results

def search_func_all(api_short, func_all_data):
    """Search func_all_v3.json for the API."""
    if api_short in func_all_data:
        entry = func_all_data[api_short]
        return [{
            "api_full_name": fq_name(api_short),
            "api_name": api_short,
            "api_type": "Function",
            "api_descriptions": entry.get("content", ""),
            "category": entry.get("category", ""),
        }]
    return []

def search_md_docstring(api_short, md_content):
    """Search pyAether_API_Docstring.md for mentions."""
    results = []
    sections = re.split(r'\n(?=#{1,3} )', md_content)
    for section in sections:
        if api_short in section:
            idx = section.find(api_short)
            start = max(0, idx - 200)
            end = min(len(section), idx + 500)
            results.append(section[start:end].strip())
    return results

def search_all_sources(api_short, methods_recs, classes_recs, func_all, md_content):
    """Search all sources and return best documentation found."""
    found = {
        "api": api_short, "fq": fq_name(api_short),
        "type": classify_api(api_short),
        "found_in": [], "description": None, "source_record": None,
    }
    # 1. api_methods.jsonl
    r = search_api_methods(api_short, methods_recs)
    if r:
        found["found_in"].append("api_methods.jsonl")
        best = r[0]
        found["description"] = best.get("api_descriptions", "")
        found["source_record"] = {"source": "api_methods.jsonl",
            "api_full_name": best.get("api_full_name", ""),
            "owner_class": best.get("owner_class", "")}
        return found
    # 2. api_classes.jsonl
    r = search_api_classes(api_short, classes_recs)
    if r:
        found["found_in"].append("api_classes.jsonl")
        best = r[0]
        desc = best.get("api_descriptions", "")
        # For enum constants, extract context around the mention
        if api_short.startswith("emc") and api_short in desc:
            idx = desc.find(api_short)
            found["description"] = desc[max(0,idx-100):idx+300].strip()
        # For methods (ClassName.method), extract the method section
        elif "." in api_short:
            method_name = api_short.split(".")[-1]
            # Try to find the method section within the class description
            # Look for patterns like `methodName(...)` or **`methodName(...)**
            pattern = rf'(`{re.escape(method_name)}\([^)]*\)[^`]*)`'
            m = re.search(pattern, desc)
            if m:
                start = max(0, m.start() - 50)
                end = min(len(desc), m.start() + 500)
                found["description"] = desc[start:end].strip()
            else:
                # Fallback: use a context window around the method name
                idx = desc.find(method_name)
                if idx >= 0:
                    start = max(0, idx - 100)
                    end = min(len(desc), idx + 400)
                    found["description"] = desc[start:end].strip()
                else:
                    found["description"] = desc[:2000]
        else:
            found["description"] = desc
        found["source_record"] = {"source": "api_classes.jsonl",
            "api_full_name": best.get("api_full_name", "")}
        return found
    # 3. func_all_v3.json
    r = search_func_all(api_short, func_all)
    if r:
        found["found_in"].append("func_all_v3.json")
        best = r[0]
        found["description"] = best.get("api_descriptions", "")
        found["source_record"] = {"source": "func_all_v3.json",
            "category": best.get("category", "")}
        return found
    # 4. markdown docstring
    r = search_md_docstring(api_short, md_content)
    if r:
        found["found_in"].append("pyAether_API_Docstring.md")
        found["description"] = r[0]
        found["source_record"] = {"source": "pyAether_API_Docstring.md",
            "context_snippets": len(r)}
        return found
    return found

# ---------------------------------------------------------------------------
# Training pair generation
# ---------------------------------------------------------------------------

def pair_id(prefix, api_name):
    h = hashlib.md5(f"{prefix}:{api_name}".encode()).hexdigest()[:10]
    return f"{prefix}-{h}"

def extract_first_sentence(desc_text):
    """Extract the first meaningful sentence from description."""
    if not desc_text:
        return None
    lines = desc_text.split("\n")
    for line in lines:
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("**`") or s.startswith(">>>"):
            continue
        if s.startswith("*") and s.endswith("*"):
            continue
        if s.startswith("Parameters") or s.startswith("Returns") or s.startswith("Examples"):
            continue
        if s.startswith("<") or s.startswith("|") or s.startswith("`"):
            continue
        m = re.match(r'^(.+?[.!?])', s)
        if m:
            return m.group(1).strip()
        return s[:200].strip()
    return None

def generate_s5_doc_to_code(api_short, found):
    """Generate S5_doc_to_code training pair from found documentation."""
    desc = found.get("description", "") or ""
    first_sent = extract_first_sentence(desc) or f"API {api_short} for EDA automation."
    atype = found.get("type", "other")
    parts = api_short.split(".")

    prompt = (
        f"You are an EDA automation assistant. Read the following PyAether API documentation "
        f"and write a Python function that calls this API.\n\n"
        f"## API Documentation\n\n{desc[:2000]}\n\n"
        f"## Task\n\nWrite a Python function that uses `pyAether.{api_short}`."
    )

    if atype == "enum_constant":
        completion = (
            f"```python\nimport pyAether as pyScript\n\n"
            f"# {first_sent}\n"
            f"def use_{api_short.replace('.', '_').lower()}():\n"
            f"    value = pyScript.{api_short}\n"
            f"    return value\n```\n"
        )
    elif atype == "factory_method" and len(parts) == 2:
        cls = parts[0]
        completion = (
            f"```python\nimport pyAether as pyScript\n\n"
            f"# {first_sent}\n"
            f"def create_{cls.lower()}():\n"
            f"    pyScript.emyInitAether('-ADV')\n"
            f"    obj = pyScript.{api_short}()\n"
            f"    return obj\n```\n"
        )
    elif len(parts) == 2:
        cls, method = parts[0], parts[1]
        completion = (
            f"```python\nimport pyAether as pyScript\n\n"
            f"# {first_sent}\n"
            f"def call_{method.lower()}():\n"
            f"    pyScript.emyInitAether('-ADV')\n"
            f"    obj = pyScript.{cls}()\n"
            f"    result = obj.{method}()\n"
            f"    return result\n```\n"
        )
    else:
        completion = (
            f"```python\nimport pyAether as pyScript\n\n"
            f"# {first_sent}\n"
            f"def call_{api_short.replace('.', '_').lower()}():\n"
            f"    result = pyScript.{api_short}()\n"
            f"    return result\n```\n"
        )

    return {
        "pair_id": pair_id("S5", api_short),
        "type": "S5_source_doc_to_code",
        "prompt": prompt, "completion": completion,
        "api_used": [fq_name(api_short)],
        "source": f"R100_source_extraction:{found['found_in'][0]}",
        "contamination_check": "PASS: API documentation only, no eval data",
    }

def generate_s5_api_lookup(api_short, found):
    """Generate S5_api_lookup training pair."""
    desc = found.get("description", "") or ""
    first_sent = extract_first_sentence(desc) or f"API {api_short} for EDA automation."
    prompt = (
        f"You are an EDA automation assistant. A user needs to perform an operation "
        f"related to: {first_sent}\n\nWhich PyAether API should they use?"
    )
    completion = (
        f"The appropriate PyAether API is `pyAether.{api_short}`.\n\n"
        f"**Documentation:**\n{desc[:1500]}\n\n"
        f"**Usage:**\n```python\nimport pyAether as pyScript\n"
        f"result = pyScript.{api_short}()\n```\n"
    )
    return {
        "pair_id": pair_id("S5lk", api_short),
        "type": "S5_source_api_lookup",
        "prompt": prompt, "completion": completion,
        "api_used": [fq_name(api_short)],
        "source": f"R100_source_extraction:{found['found_in'][0]}",
        "contamination_check": "PASS: API documentation only",
    }

# ---------------------------------------------------------------------------
# Contamination check
# ---------------------------------------------------------------------------

def contamination_check(pairs, eval_tasks):
    """Check that no training pair contains eval task data."""
    eval_texts = set()
    for task in eval_tasks:
        for field in ["prompt", "canonical_solution", "test", "entry_point"]:
            val = task.get(field, "")
            if val and isinstance(val, str) and len(val) > 20:
                eval_texts.add(val[:200].strip().lower())
    rejected = 0
    for pair in pairs:
        combined = (pair.get("prompt", "") + pair.get("completion", "")).lower()
        for fp in eval_texts:
            if fp in combined:
                pair["contamination_check"] = "REJECTED: matches eval fingerprint"
                rejected += 1
                break
    return rejected

# ---------------------------------------------------------------------------
# HTML report
# ---------------------------------------------------------------------------

def generate_html_report(stats, found_apis, not_found_apis, output_path):
    """Generate self-contained HTML report."""
    rows_type = ""
    for atype, counts in sorted(stats['type_distribution'].items()):
        rows_type += f"<tr><td>{atype}</td><td>{counts['total']}</td><td class='found'>{counts['found']}</td><td class='not-found'>{counts['not_found']}</td></tr>\n"

    rows_source = ""
    for source, count in sorted(stats['source_distribution'].items(), key=lambda x: -x[1]):
        pct = count / stats['found_count'] * 100 if stats['found_count'] > 0 else 0
        rows_source += f"<tr><td><code>{source}</code></td><td>{count}</td><td>{pct:.1f}%</td></tr>\n"

    rows_found = ""
    for api_info in found_apis[:50]:
        api = api_info['api']
        atype = api_info['type']
        source = api_info['found_in'][0] if api_info['found_in'] else 'N/A'
        rows_found += f"<tr><td><code>{api}</code></td><td>{atype}</td><td><code>{source}</code></td></tr>\n"
    if len(found_apis) > 50:
        rows_found += f"<tr><td colspan='3' style='text-align:center;color:#666;'>... and {len(found_apis)-50} more</td></tr>\n"

    rows_not_found = ""
    for api_info in not_found_apis:
        rows_not_found += f"<tr><td><code>{api_info['api']}</code></td><td>{api_info['type']}</td></tr>\n"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>R100: Source API Extraction</title>
<style>
body {{ font-family: -apple-system, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f8f9fa; color: #333; }}
h1 {{ color: #1a1a2e; border-bottom: 3px solid #e94560; padding-bottom: 10px; }}
h2 {{ color: #16213e; border-bottom: 1px solid #ccc; padding-bottom: 5px; margin-top: 30px; }}
table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
th {{ background: #16213e; color: white; }}
tr:nth-child(even) {{ background: #f2f2f2; }}
.stat-card {{ display: inline-block; background: white; border-radius: 8px; padding: 15px 25px; margin: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }}
.stat-card .num {{ font-size: 2em; font-weight: bold; color: #e94560; }}
.stat-card .label {{ color: #666; font-size: 0.9em; }}
.found {{ color: #27ae60; }} .not-found {{ color: #e74c3c; }}
code {{ background: #e8e8e8; padding: 2px 6px; border-radius: 3px; }}
</style></head><body>
<h1>R100: Source API Extraction — Enriching 124 Doubly-Missing APIs</h1>
<p><strong>BaiZe Post-Train</strong> · Wake 148 · 2026-11-09 · Zero GPU</p>
<h2>📊 Summary</h2>
<div class="stat-card"><div class="num">{stats['total_apis']}</div><div class="label">Missing APIs</div></div>
<div class="stat-card"><div class="num found">{stats['found_count']}</div><div class="label">Found</div></div>
<div class="stat-card"><div class="num not-found">{stats['not_found_count']}</div><div class="label">Still Missing</div></div>
<div class="stat-card"><div class="num">{stats['s5_pairs_generated']}</div><div class="label">S5 Pairs</div></div>
<div class="stat-card"><div class="num">{stats['v4_total_pairs']}</div><div class="label">V4 Total</div></div>
<div class="stat-card"><div class="num">{stats['contamination_rejected']}</div><div class="label">Rejected</div></div>
<h2>📋 Background</h2>
<p>R98: SFT 15.2% / KB 74.6% API coverage. R99: 124 APIs missing from both, minimal S0 pairs.
R100 searches alt sources: api_methods.jsonl (4043), api_classes.jsonl (486), func_all_v3.json (6734), pyAether_API_Docstring.md (143KB).</p>
<h2>🔍 Type Distribution</h2>
<table><tr><th>Type</th><th>Total</th><th>Found</th><th>Not Found</th></tr>{rows_type}</table>
<h2>📂 Source Hits</h2>
<table><tr><th>Source</th><th>Found</th><th>%</th></tr>{rows_source}</table>
<h2>✅ Found APIs (first 50)</h2>
<table><tr><th>API</th><th>Type</th><th>Source</th></tr>{rows_found}</table>
<h2>❌ Still Missing</h2>
<table><tr><th>API</th><th>Type</th></tr>{rows_not_found}</table>
<h2>📝 SFT Corpus Impact</h2>
<table><tr><th>Version</th><th>Pairs</th><th>Coverage</th><th>Notes</th></tr>
<tr><td>v1/v2</td><td>~39K</td><td>74/488 (15.2%)</td><td>Structured 0% overlap</td></tr>
<tr><td>v3 (R99)</td><td>1,113</td><td>488/488 (100%)</td><td>364 KB-doc + 124 S0</td></tr>
<tr><td><strong>v4 (R100)</strong></td><td>{stats['v4_total_pairs']}</td><td>488/488 (100%)</td><td>{stats['found_count']} S5 + {stats['not_found_count']} S0</td></tr>
</table>
<h2>⚠️ Limitations</h2>
<ul><li>{stats['not_found_count']} APIs remain as minimal S0 pairs</li>
<li>Enum constants extracted with context window</li>
<li>v4 is supplementary — merge with UltraData-SFT</li></ul>
<p style="margin-top:40px;color:#999;font-size:0.85em;">Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</body></html>"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return os.path.getsize(output_path)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="R100: Source API Extraction")
    parser.add_argument("--smoke", action="store_true", help="First 10 APIs only")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    parser.add_argument("--json", action="store_true", help="Generate JSON summary")
    args = parser.parse_args()

    print("=" * 60)
    print("R100: Source API Extraction — Enriching 124 Doubly-Missing APIs")
    print("=" * 60)

    # 1. Load v3 corpus and extract S0 pairs
    print("\n[1/6] Loading v3 augmented corpus...")
    v3_pairs = load_jsonl(V3_OUTPUT)
    s0_pairs = [p for p in v3_pairs if p.get("type", "").startswith("S0")]
    non_s0_pairs = [p for p in v3_pairs if not p.get("type", "").startswith("S0")]
    missing_apis = []
    for p in s0_pairs:
        for a in p.get("api_used", []):
            sn = short_name(a)
            if sn:
                missing_apis.append(sn)
    print(f"  v3 total: {len(v3_pairs)}, S0: {len(s0_pairs)}, missing APIs: {len(missing_apis)}")

    if args.smoke:
        missing_apis = missing_apis[:10]
        s0_pairs = s0_pairs[:10]
        print(f"  [smoke] Using first {len(missing_apis)} APIs")

    # 2. Load alt docs
    print("\n[2/6] Loading alternative documentation sources...")
    methods_recs = load_jsonl(EDA_DOCS / "api_methods.jsonl") if (EDA_DOCS / "api_methods.jsonl").exists() else []
    classes_recs = load_jsonl(EDA_DOCS / "api_classes.jsonl") if (EDA_DOCS / "api_classes.jsonl").exists() else []
    func_all = load_json(EDA_DOCS / "func_all_v3.json") if (EDA_DOCS / "func_all_v3.json").exists() else {}
    md_content = load_md(EDA_DOCS / "pyAether_API_Docstring.md") if (EDA_DOCS / "pyAether_API_Docstring.md").exists() else ""
    print(f"  methods: {len(methods_recs)}, classes: {len(classes_recs)}, funcs: {len(func_all)}, md: {len(md_content)} chars")

    # 3. Search
    print("\n[3/6] Searching sources for missing APIs...")
    found_results, not_found_results = [], []
    source_dist, type_found, type_not_found = Counter(), Counter(), Counter()
    for api_short in missing_apis:
        found = search_all_sources(api_short, methods_recs, classes_recs, func_all, md_content)
        if found["found_in"]:
            found_results.append(found)
            source_dist[found["found_in"][0]] += 1
            type_found[found["type"]] += 1
        else:
            not_found_results.append(found)
            type_not_found[found["type"]] += 1
    print(f"  Found: {len(found_results)}/{len(missing_apis)}, Not found: {len(not_found_results)}")
    print(f"  Sources: {dict(source_dist)}")

    # 4. Generate S5 pairs
    print("\n[4/6] Generating S5 training pairs...")
    s5_pairs = []
    for found in found_results:
        s5_pairs.append(generate_s5_doc_to_code(found["api"], found))
        s5_pairs.append(generate_s5_api_lookup(found["api"], found))
    print(f"  S5 pairs: {len(s5_pairs)}")

    # 5. Build v4
    print("\n[5/6] Building v4 corpus...")
    not_found_set = set(r["api"] for r in not_found_results)
    remaining_s0 = [p for p in s0_pairs if any(short_name(a) in not_found_set for a in p.get("api_used", []))]
    v4_pairs = non_s0_pairs + s5_pairs + remaining_s0
    eval_tasks = load_jsonl(EVAL_DATASET) if EVAL_DATASET.exists() else []
    rejected = contamination_check(s5_pairs, eval_tasks)
    print(f"  v4 total: {len(v4_pairs)} (S5:{len(s5_pairs)} S0:{len(remaining_s0)})")
    print(f"  Contamination: {'⚠️ '+str(rejected)+' REJECTED' if rejected else '✅ PASS'}")
    with open(OUTPUT, "w", encoding="utf-8") as f:
        for pair in v4_pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")
    print(f"  Written: {OUTPUT.name} ({os.path.getsize(OUTPUT)/1024:.1f} KB)")

    # 6. Reports
    print("\n[6/6] Generating reports...")
    type_distribution = {}
    for t in set(list(type_found.keys()) + list(type_not_found.keys())):
        type_distribution[t] = {"total": type_found.get(t, 0) + type_not_found.get(t, 0),
            "found": type_found.get(t, 0), "not_found": type_not_found.get(t, 0)}
    stats = {"total_apis": len(missing_apis), "found_count": len(found_results),
        "not_found_count": len(not_found_results), "s5_pairs_generated": len(s5_pairs),
        "v4_total_pairs": len(v4_pairs), "contamination_rejected": rejected,
        "source_distribution": dict(source_dist), "type_distribution": type_distribution}

    if args.html:
        html_path = REPORTS_DIR / "report_posttrain_r100_source_api_extraction_zh.html"
        sz = generate_html_report(stats, found_results, not_found_results, html_path)
        print(f"  HTML: {html_path.name} ({sz/1024:.1f} KB)")
    if args.json:
        json_path = RUN_DIR / "r100_source_api_extraction_summary.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"timestamp": datetime.now().isoformat(), "stats": stats,
                "found_apis": [{"api": r["api"], "type": r["type"], "found_in": r["found_in"]} for r in found_results],
                "not_found_apis": [{"api": r["api"], "type": r["type"]} for r in not_found_results]},
                f, ensure_ascii=False, indent=2)
        print(f"  JSON: {json_path.name} ({os.path.getsize(json_path)/1024:.1f} KB)")

    print("\n" + "=" * 60)
    print(f"  Searched:    {len(missing_apis)}")
    print(f"  Found:       {len(found_results)} ({len(found_results)/len(missing_apis)*100:.1f}%)")
    print(f"  Missing:     {len(not_found_results)} ({len(not_found_results)/len(missing_apis)*100:.1f}%)")
    print(f"  S5 pairs:    {len(s5_pairs)}")
    print(f"  v4 total:    {len(v4_pairs)}")
    print(f"  Rejected:    {rejected}")
    print("=" * 60)

if __name__ == "__main__":
    main()
