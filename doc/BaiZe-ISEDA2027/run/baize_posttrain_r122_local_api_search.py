#!/usr/bin/env python3
"""baize_posttrain_r122_local_api_search.py
R122: Lightweight Local API Search Tool — replaces MCP search_apis / get_api_details / search_apis_by_keyword
with a pure-Python in-memory implementation (no chromadb, no sandbox, no MCP server).

Background (R121 findings):
  - Sandbox 10.129.32.75: all 7 TCP ports FILTERED -> SSH tunnel not feasible
  - Docker available but no permissions -> local Docker deployment blocked
  - MCP server: system Python 3.8 incompatible (dict[str,str] syntax), chromadb not installed
  - Local API KB available: API_INFO_MERGED_V3.json (8463 APIs, 17.3MB)

This tool provides:
  1. search_apis(query, top_k, similarity_threshold) — BM25-like keyword search (replaces vector search)
  2. get_api_details(api_list) — direct lookup from API_INFO_MERGED_V3.json
  3. search_apis_by_keyword(query, top_k) — camelCase token + keyword matching

Usage as RL tool interface:
  from baize_posttrain_r122_local_api_search import LocalAPISearch
  searcher = LocalAPISearch()  # loads from default path
  results = searcher.search_apis('get current design')
  details = searcher.get_api_details(['aeGetCurDesign'])
  kw_results = searcher.search_apis_by_keyword('CV')

Run standalone for smoke test:
  python3 baize_posttrain_r122_local_api_search.py --smoke
  python3 baize_posttrain_r122_local_api_search.py --benchmark
"""

import json
import os
import re
import time
import math
from collections import defaultdict, Counter
from typing import Optional

DEFAULT_API_INFO_PATH = os.path.expanduser('~/code/eda_fastmcp/docs/API_INFO_MERGED_V3.json')
DEFAULT_API_SUMMARY_PATH = os.path.expanduser('~/code/eda_fastmcp/kb/api_summary_v3.json')

_STOPWORDS = frozenset({
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'this', 'that', 'these', 'those', 'it', 'its', 'of', 'to', 'in', 'on',
    'at', 'by', 'for', 'with', 'from', 'as', 'into', 'and', 'or', 'not',
    'but', 'if', 'then', 'else', 'when', 'where', 'which', 'who', 'how',
    'what', 'why', 'will', 'would', 'can', 'could', 'should', 'shall',
    'may', 'might', 'must', 'do', 'does', 'did', 'has', 'have', 'had',
    'get', 'set', 'return', 'returns', 'param', 'parameter', 'parameters',
    'example', 'examples', 'note', 'notes', 'see', 'also',
    'true', 'false', 'none', 'null',
})

_CAMEL_SPLIT_RE = re.compile(
    r'(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|'
    r'(?<=[0-9])(?=[A-Za-z])|(?<=[A-Za-z])(?=[0-9])|'
    r'[._\-]'
)
_WORD_RE = re.compile(r'[a-zA-Z][a-zA-Z0-9_]*')


def _camel_split(name):
    parts = _CAMEL_SPLIT_RE.split(name)
    return [p.lower().strip() for p in parts if p and p.strip()]


def _tokenize_text(text):
    tokens = _WORD_RE.findall(text.lower())
    return [t for t in tokens if t not in _STOPWORDS and len(t) >= 2]


class _BM25Scorer:
    def __init__(self, docs_tokens, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.N = len(docs_tokens)
        self.doc_lens = [len(d) for d in docs_tokens]
        self.avgdl = sum(self.doc_lens) / self.N if self.N > 0 else 0
        self.inverted = defaultdict(dict)
        for idx, tokens in enumerate(docs_tokens):
            tf = Counter(tokens)
            for token, count in tf.items():
                self.inverted[token][idx] = count
        self.idf = {}
        for token, postings in self.inverted.items():
            df = len(postings)
            self.idf[token] = math.log((self.N - df + 0.5) / (df + 0.5) + 1.0)

    def score(self, query_tokens):
        scores = defaultdict(float)
        for token in query_tokens:
            if token not in self.inverted:
                continue
            idf = self.idf.get(token, 0.0)
            for doc_idx, tf in self.inverted[token].items():
                dl = self.doc_lens[doc_idx]
                denom = tf + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
                scores[doc_idx] += idf * tf * (self.k1 + 1) / denom
        return sorted(scores.items(), key=lambda x: -x[1])


class LocalAPISearch:
    """Lightweight local API search tool — drop-in replacement for MCP search tools."""

    def __init__(self, api_info_path=DEFAULT_API_INFO_PATH, api_summary_path=DEFAULT_API_SUMMARY_PATH):
        t0 = time.time()
        with open(api_info_path) as f:
            self.api_info = json.load(f)
        self.api_keys = list(self.api_info.keys())
        self.N = len(self.api_keys)

        self.name_tokens = []
        for key in self.api_keys:
            short_name = key.replace('pyAether.', '')
            self.name_tokens.append(_camel_split(short_name))

        self.desc_tokens = []
        for i, key in enumerate(self.api_keys):
            entry = self.api_info[key]
            desc = entry.get('api_descriptions', '')
            dtokens = _tokenize_text(desc)
            dtokens.extend(self.name_tokens[i] * 3)
            self.desc_tokens.append(dtokens)

        self.bm25 = _BM25Scorer(self.desc_tokens)

        self.name_index = defaultdict(set)
        for i, tokens in enumerate(self.name_tokens):
            for t in tokens:
                self.name_index[t].add(i)

        self.summary_map = {}
        if api_summary_path and os.path.exists(api_summary_path):
            with open(api_summary_path) as f:
                summary_data = json.load(f)
            for item in summary_data:
                if isinstance(item, list) and len(item) >= 2:
                    full_str, name = item[0], item[1]
                    if ':' in full_str:
                        self.summary_map[name] = full_str.split(':', 1)[1].strip()
                    else:
                        self.summary_map[name] = full_str

        self._load_time = time.time() - t0
        self._index_size_mb = os.path.getsize(api_info_path) / 1024 / 1024

    def _get_short_desc(self, idx):
        key = self.api_keys[idx]
        short_name = key.replace('pyAether.', '')
        desc = self.summary_map.get(short_name, '')
        if not desc:
            full_desc = self.api_info[key].get('api_descriptions', '')
            for line in full_desc.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('`'):
                    desc = line[:200]
                    break
            if not desc:
                desc = full_desc[:200]
        return desc

    def search_apis(self, query, top_k=5, similarity_threshold=0.6, lang='pyAether'):
        query_tokens = _tokenize_text(query)
        query_tokens.extend(_camel_split(query))
        query_tokens = list(set(query_tokens))
        if not query_tokens:
            return []
        results = self.bm25.score(query_tokens)
        if not results:
            return []
        max_score = results[0][1] if results[0][1] > 0 else 1.0
        output = []
        for idx, score in results:
            sim = score / max_score
            if sim < similarity_threshold:
                continue
            short_name = self.api_keys[idx].replace('pyAether.', '')
            output.append({
                'api_name': short_name,
                'description': self._get_short_desc(idx),
                'similarity': round(sim, 4),
            })
            if len(output) >= top_k:
                break
        return output

    def get_api_details(self, api_list, lang='pyAether'):
        output = []
        for name in api_list:
            # Strip pyAether. prefix if present, then try both short and full
            short_name = name.replace('pyAether.', '') if name.startswith('pyAether.') else name
            key = short_name if short_name in self.api_info else name
            if key not in self.api_info:
                found = None
                for k in self.api_info:
                    if k.replace('pyAether.', '').lower() == name.lower():
                        found = k
                        break
                if found:
                    key = found
                else:
                    output.append({
                        'api_name': name, 'api_type': 'unknown',
                        'description': f"API '{name}' not found",
                        'properties': '', 'inheritance_relations': '', 'category': '',
                    })
                    continue
            entry = self.api_info[key]
            short_name = key.replace('pyAether.', '')
            full_desc = entry.get('api_descriptions', '')
            properties = ''
            inheritance = ''
            if entry.get('api_type') == 'class':
                prop_match = re.search(r'(?:Properties|Attributes)\s*\n(.*?)(?:\n\n|\n##|\n#|\Z)', full_desc, re.DOTALL)
                if prop_match:
                    properties = prop_match.group(1).strip()[:500]
                inh_match = re.search(r'(?:inheritance|inherits|base class)[:\s]*(.*?)(?:\n\n|\n#|\Z)', full_desc, re.IGNORECASE | re.DOTALL)
                if inh_match:
                    inheritance = inh_match.group(1).strip()[:300]
            output.append({
                'api_name': short_name,
                'api_type': entry.get('api_type', 'unknown'),
                'description': full_desc[:2000],
                'properties': properties,
                'inheritance_relations': inheritance,
                'category': entry.get('category', ''),
            })
        return output

    def search_apis_by_keyword(self, query, top_k=5, lang='pyAether'):
        query_tokens = _camel_split(query)
        query_lower = query.lower().strip()

        exact_matches = []
        for i, key in enumerate(self.api_keys):
            if key.replace('pyAether.', '').lower() == query_lower:
                exact_matches.append(i)

        if exact_matches:
            results = [(i, 1.0, 'exact_match') for i in exact_matches]
        else:
            name_matches = defaultdict(float)
            for token in query_tokens:
                if token in self.name_index:
                    for idx in self.name_index[token]:
                        name_matches[idx] += 1.0
            if name_matches:
                max_nm = max(name_matches.values())
                for idx in name_matches:
                    name_matches[idx] /= max_nm

            bm25_query = _tokenize_text(query) + query_tokens
            bm25_results = self.bm25.score(bm25_query) if bm25_query else []
            bm25_dict = {idx: score for idx, score in bm25_results}
            if bm25_dict:
                max_bm = max(bm25_dict.values())
                for idx in bm25_dict:
                    bm25_dict[idx] /= max_bm

            all_indices = set(name_matches.keys()) | set(bm25_dict.keys())
            results = []
            for idx in all_indices:
                nm_score = name_matches.get(idx, 0.0)
                bm_score = bm25_dict.get(idx, 0.0)
                combined = nm_score * 0.7 + bm_score * 0.3
                src = 'name_overlap' if nm_score > 0 else 'bm25'
                results.append((idx, combined, src))
            results.sort(key=lambda x: -x[1])

        output = []
        for idx, sim, src in results[:top_k]:
            short_name = self.api_keys[idx].replace('pyAether.', '')
            output.append({
                'api_name': short_name,
                'description': self._get_short_desc(idx),
                'similarity': round(sim, 4),
                'source': src,
                'note': 'keyword match, verify parameter types',
            })
        return output

    def stats(self):
        return {
            'total_apis': self.N,
            'api_info_size_mb': round(self._index_size_mb, 2),
            'load_time_s': round(self._load_time, 3),
            'unique_name_tokens': len(self.name_index),
            'unique_desc_tokens': len(self.bm25.inverted),
            'summaries_loaded': len(self.summary_map),
        }


def _smoke_test():
    print('=' * 70)
    print('R122: Local API Search Tool — Smoke Test')
    print('=' * 70)

    t0 = time.time()
    searcher = LocalAPISearch()
    load_time = time.time() - t0
    stats = searcher.stats()
    print(f"\n[Load] {stats['total_apis']} APIs, {stats['api_info_size_mb']}MB, "
          f"{load_time:.3f}s, {stats['unique_name_tokens']} name tokens, "
          f"{stats['unique_desc_tokens']} desc tokens, {stats['summaries_loaded']} summaries")

    tests = [
        ("search_apis", "get current design", 3, 0.1),
        ("search_apis", "create rectangle shape", 3, 0.1),
        ("search_apis", "add highlight circle in layout", 3, 0.05),
        ("search_apis", "get all instances in current design", 3, 0.05),
        ("search_apis", "create new cell view", 3, 0.05),
        ("search_apis", "save design to disk", 3, 0.05),
        ("search_apis", "query net connectivity", 3, 0.05),
        ("keyword", "CV", 5),
        ("keyword", "dbOpen", 5),
        ("keyword", "aeGetCurDesign", 3),
        ("keyword", "CrtProp", 5),
        ("keyword", "Highlight", 5),
    ]

    pass_count = 0
    total = len(tests) + 2  # +2 for get_api_details tests

    for test in tests:
        if test[0] == 'search_apis':
            _, q, tk, thresh = test
            t1 = time.time()
            results = searcher.search_apis(q, top_k=tk, similarity_threshold=thresh)
            elapsed = (time.time() - t1) * 1000
            print(f"\n[search_apis] '{q}' [{elapsed:.1f}ms] {len(results)} results")
            for r in results:
                print(f"  {r['api_name']} (sim={r['similarity']}): {r['description'][:80]}")
            if results:
                pass_count += 1
        elif test[0] == 'keyword':
            _, q, tk = test
            t1 = time.time()
            results = searcher.search_apis_by_keyword(q, top_k=tk)
            elapsed = (time.time() - t1) * 1000
            print(f"\n[search_by_keyword] '{q}' [{elapsed:.1f}ms] {len(results)} results")
            for r in results:
                print(f"  {r['api_name']} (src={r['source']}, sim={r['similarity']}): {r['description'][:80]}")
            if results:
                pass_count += 1

    # get_api_details tests
    print("\n[get_api_details] ['aeGetCurDesign', 'dbCreateRect', 'nonExistentAPI']")
    t1 = time.time()
    details = searcher.get_api_details(['aeGetCurDesign', 'dbCreateRect', 'nonExistentAPI'])
    elapsed = (time.time() - t1) * 1000
    print(f"  [{elapsed:.1f}ms] {len(details)} results:")
    for d in details:
        print(f"  {d['api_name']} ({d['api_type']}, cat={d['category']}): {d['description'][:100]}...")
    if len(details) == 3:
        pass_count += 1

    # get_api_details with pyAether prefix
    print("\n[get_api_details] ['pyAether.aeGetCurDesign']")
    details2 = searcher.get_api_details(['pyAether.aeGetCurDesign'])
    if details2 and details2[0]['api_type'] != 'unknown':
        print(f"  OK: {details2[0]['api_name']} ({details2[0]['api_type']})")
        pass_count += 1
    else:
        print(f"  FAIL: {details2}")

    print(f"\n{'=' * 70}")
    print(f"Smoke test: {pass_count}/{total} passed")
    print(f"{'=' * 70}")
    return searcher, pass_count, total


def _benchmark():
    import random
    print('=' * 70)
    print('R122: Local API Search Tool — Latency Benchmark')
    print('=' * 70)

    searcher = LocalAPISearch()
    stats = searcher.stats()
    print(f"\nLoaded {stats['total_apis']} APIs in {stats['load_time_s']}s")

    random.seed(42)
    queries = []
    for _ in range(100):
        idx = random.randint(0, searcher.N - 1)
        entry = searcher.api_info[searcher.api_keys[idx]]
        desc = entry.get('api_descriptions', '')
        first_sent = desc.split('.')[0][:100]
        if first_sent:
            queries.append(first_sent)

    latencies = []
    for q in queries:
        t0 = time.time()
        searcher.search_apis(q, top_k=5, similarity_threshold=0.1)
        latencies.append((time.time() - t0) * 1000)
    latencies.sort()
    print(f"\nsearch_apis latency over {len(queries)} queries:")
    print(f"  mean: {sum(latencies)/len(latencies):.2f}ms")
    print(f"  p50:  {latencies[len(latencies)//2]:.2f}ms")
    print(f"  p95:  {latencies[int(len(latencies)*0.95)]:.2f}ms")
    print(f"  p99:  {latencies[int(len(latencies)*0.99)]:.2f}ms")

    latencies2 = []
    for i in range(100):
        idx = random.randint(0, searcher.N - 1)
        name = searcher.api_keys[idx].replace('pyAether.', '')
        t0 = time.time()
        searcher.get_api_details([name])
        latencies2.append((time.time() - t0) * 1000)
    latencies2.sort()
    print(f"\nget_api_details latency over 100 lookups:")
    print(f"  mean: {sum(latencies2)/len(latencies2):.3f}ms")
    print(f"  p99:  {latencies2[int(len(latencies2)*0.99)]:.3f}ms")

    latencies3 = []
    for i in range(100):
        idx = random.randint(0, searcher.N - 1)
        name = searcher.api_keys[idx].replace('pyAether.', '')
        tokens = _camel_split(name)[:2]
        q = ''.join(t.capitalize() for t in tokens) if tokens else name[:10]
        t0 = time.time()
        searcher.search_apis_by_keyword(q, top_k=5)
        latencies3.append((time.time() - t0) * 1000)
    latencies3.sort()
    print(f"\nsearch_apis_by_keyword latency over 100 queries:")
    print(f"  mean: {sum(latencies3)/len(latencies3):.3f}ms")
    print(f"  p99:  {latencies3[int(len(latencies3)*0.99)]:.3f}ms")

    print(f"\n{'=' * 70}")
    print('Benchmark complete')
    print(f"{'=' * 70}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='R122 Local API Search Tool')
    parser.add_argument('--smoke', action='store_true', help='Run smoke test')
    parser.add_argument('--benchmark', action='store_true', help='Run latency benchmark')
    args = parser.parse_args()
    if args.benchmark:
        _benchmark()
    else:
        _smoke_test()
