#!/usr/bin/env python3
"""R321: Missing API Coverage Analysis.
Cross-reference the 344 cross-model missing APIs (R320) against the SFT
corpus to determine if the gap is a data coverage issue or learning failure.
Does NOT require sandbox or GPU.
"""
import json, sys, os, argparse
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def load_missing_apis():
    path = os.path.join(SCRIPT_DIR, "r320_api_db_snapshot.json")
    with open(path) as f:
        d = json.load(f)
    missing = d["cross_model_missing_344"]
    expected = set(d["expected_apis"]["sorted_list"])
    return missing, expected

def load_corpus_text(parquet_path):
    import pyarrow.parquet as pq
    table = pq.read_table(parquet_path)
    df = table.to_pandas()
    texts = []
    for col in df.columns:
        if df[col].dtype == object:
            texts.extend(df[col].dropna().astype(str).tolist())
    return "\n".join(texts), len(df), list(df.columns)

def analyze_coverage(missing_apis, corpus_text):
    covered, not_covered = [], []
    for api in missing_apis:
        if api in corpus_text:
            covered.append(api)
        else:
            not_covered.append(api)
    return covered, not_covered

def analyze_by_module(missing_apis):
    modules = Counter()
    for api in missing_apis:
        parts = api.split(".")
        modules[parts[0] if len(parts) > 1 else "unknown"] += 1
    return modules

def main():
    parser = argparse.ArgumentParser(description="R321 Missing API Coverage")
    parser.add_argument("--corpus", default="sft_pyaether_corpus_v11_v36_merged.parquet")
    parser.add_argument("--corpus2", default="sft_pyaether_corpus_v11_v37_merged.parquet")
    args = parser.parse_args()

    print("=" * 70)
    print("R321: Missing API Coverage Analysis")
    print("=" * 70)

    missing_apis, expected_apis = load_missing_apis()
    print(f"\n1. Missing APIs (R320): {len(missing_apis)}")
    print(f"   Total expected APIs: {len(expected_apis)}")
    print(f"   Missing rate: {len(missing_apis)/len(expected_apis)*100:.1f}%")

    modules = analyze_by_module(missing_apis)
    print(f"\n2. Missing APIs by module (top 15):")
    for mod, count in modules.most_common(15):
        print(f"   {mod:40s} {count:4d}")

    corpus_path = os.path.join(SCRIPT_DIR, args.corpus)
    print(f"\n3. Loading corpus: {args.corpus}")
    corpus_text, n_rows, cols = load_corpus_text(corpus_path)
    print(f"   Rows: {n_rows}, Cols: {cols}")
    print(f"   Total text: {len(corpus_text):,} chars")

    covered, not_covered = analyze_coverage(missing_apis, corpus_text)
    pct_c = len(covered)/len(missing_apis)*100
    pct_nc = len(not_covered)/len(missing_apis)*100
    print(f"\n4. Coverage in {args.corpus}:")
    print(f"   Covered:     {len(covered):4d} / {len(missing_apis)} ({pct_c:.1f}%)")
    print(f"   NOT covered: {len(not_covered):4d} / {len(missing_apis)} ({pct_nc:.1f}%)")

    results = {
        "R321": "Missing API Coverage Analysis",
        "date": "2026-11-12",
        "corpus": args.corpus,
        "n_missing": len(missing_apis),
        "n_expected": len(expected_apis),
        "covered": len(covered),
        "not_covered": len(not_covered),
        "covered_pct": round(pct_c, 1),
        "not_covered_pct": round(pct_nc, 1),
        "covered_apis": sorted(covered),
        "not_covered_apis": sorted(not_covered),
        "modules": dict(modules.most_common()),
    }

    if args.corpus2 and os.path.exists(os.path.join(SCRIPT_DIR, args.corpus2)):
        c2_path = os.path.join(SCRIPT_DIR, args.corpus2)
        print(f"\n5. Loading corpus2: {args.corpus2}")
        c2_text, n2, _ = load_corpus_text(c2_path)
        print(f"   Rows: {n2}, Text: {len(c2_text):,} chars")
        cov2, ncov2 = analyze_coverage(missing_apis, c2_text)
        print(f"   Covered in v37: {len(cov2):4d} ({len(cov2)/len(missing_apis)*100:.1f}%)")
        newly = sorted(set(cov2) - set(covered))
        still = sorted(set(ncov2))
        print(f"   Newly covered vs v36: {len(newly)}")
        print(f"   Still missing: {len(still)}")
        results["corpus2"] = args.corpus2
        results["covered2"] = len(cov2)
        results["newly_covered_v37"] = newly
        results["still_missing_v37"] = still

    print(f"\n6. Top 20 NOT-covered (true data gaps):")
    for api in not_covered[:20]:
        print(f"   {api}")

    print(f"\n7. Top 20 covered but not used (learning failures):")
    for api in covered[:20]:
        print(f"   {api}")

    out_path = os.path.join(SCRIPT_DIR, "r321_missing_api_coverage.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n8. Results saved: {out_path}")

    print(f"\n{'='*70}")
    print(f"KEY CONCLUSION:")
    print(f"  Of {len(missing_apis)} missing APIs:")
    print(f"  - {len(covered)} ({pct_c:.1f}%) ARE in training corpus = learning failure")
    print(f"  - {len(not_covered)} ({pct_nc:.1f}%) NOT in training corpus = true data gap")
    print(f"  Next SFT: augment data gap APIs + increase freq for learning failures")
    print(f"  RL: reinforce API usage patterns for covered-but-unused APIs")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
