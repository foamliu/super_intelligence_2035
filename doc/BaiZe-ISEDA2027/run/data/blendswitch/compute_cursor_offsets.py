#!/usr/bin/env python3
"""Compute per-source cursor offsets for S1->S2 blend cold switch (Bridge Edition).

Computes how many samples each source contributed during S1 training up to a
given step, using the same Bresenham algorithm as Megatron's BlendedDataset.
Output JSON is consumed by blend_hot_switch_bridge_compat.py via
BLEND_CURSOR_OFFSETS_JSON env var.

Usage:
  python compute_cursor_offsets.py \
    --s1-tsv /path/to/blend_s1_preblend.tsv \
    --s2-config /path/to/s2_blend_switch_config.json \
    --switch-step 350000 --global-batch-size 256 \
    --output /path/to/cursor_offsets.json
"""
from __future__ import annotations
import argparse, json, os, sys
import numpy

def parse_blend_tsv(tsv_path):
    sources = []
    with open(tsv_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue
            parts = line.split("\t")
            if len(parts) < 3: continue
            sources.append((parts[0].strip(), parts[1].strip(), float(parts[2].strip())))
    return sources

def compute_consumed_per_source_vectorized(weights, consumed_samples):
    """Vectorized Bresenham: compute per-source counts for n samples.
    
    Megatron's build_blending_indices uses a Bresenham-like deficit algorithm:
    at each step i, pick source s with max deficit = w[s]*(i+1) - sampled[s].
    
    This is equivalent to: for each source s, count = floor(w[s] * n) with
    adjustment for fractional remainders. The exact count can be computed as:
    count[s] = number of i in [0, n) where s = argmax(w[j]*(i+1) - sampled[j]).
    
    For the Bresenham algorithm, the per-source count after n steps is:
    count[s] = round(w[s] * n) with special handling for ties.
    
    Actually, the exact algorithm is: at step i, deficit[s] = w[s]*(i+1) - sampled[s].
    The chosen source increments sampled[chosen] by 1. So after all n steps,
    sampled[s] = number of times s was chosen.
    
    For the standard Bresenham, the counts are: count[s] = floor(w[s]*n) or ceil,
    with the fractional parts determining which sources get the extra +1.
    
    A simpler exact approach: count[s] = number of integers k in [1, n] where
    k/n falls in the cumulative weight interval for source s.
    
    Actually, let's use the math: the Bresenham picks source s at step i if
    w[s]*(i+1) - sampled[s] is the maximum. After n steps, count[s] = floor(w[s]*n)
    adjusted by the fractional remainders.
    
    For exactness, let's use a chunked approach: process in chunks of 1M.
    """
    w = numpy.asarray(weights, dtype=numpy.float64)
    n_sources = len(weights)
    n = consumed_samples
    
    # Process in chunks to avoid O(n) Python loop but stay memory-safe
    chunk = min(2_000_000, n)
    sampled = numpy.zeros(n_sources, dtype=numpy.int64)
    counts = numpy.zeros(n_sources, dtype=numpy.int64)
    
    for start in range(0, n, chunk):
        end = min(start + chunk, n)
        size = end - start
        # For each position in chunk, compute deficit for all sources
        # deficit[s, j] = w[s] * (start + j + 1) - sampled[s] - (counts so far for s in this chunk)
        # This is still O(n*s) per chunk
        # 
        # Better: use the vectorized Bresenham
        indices = numpy.arange(start + 1, end + 1, dtype=numpy.int64)  # shape (size,)
        # For each source, deficit = w[s] * indices - sampled[s] - local_count[s]
        # We need to process sequentially because sampled changes
        # 
        # Alternative: batch process where we compute which source wins at each step
        # using the fact that the Bresenham is deterministic
        #
        # Actually the simplest correct vectorized approach:
        # For each step i, deficit[s] = w[s] * (i+1) - count_s_up_to[i]
        # This is inherently sequential. But we can use a different formulation.
        #
        # The Bresenham weighted interleaving is equivalent to:
        # At step i (0-indexed), choose source s = argmax_j(w[j]*(i+1) - count_j)
        # 
        # A known result: for rational weights w[j] = p[j]/q (common denominator),
        # the pattern repeats with period q. But for our case, let's just use
        # the chunked loop.
        
        for i in range(size):
            global_i = start + i
            deficit = w * (global_i + 1) - sampled
            chosen = int(numpy.argmax(deficit))
            sampled[chosen] += 1
            counts[chosen] += 1
        
        if start % 10_000_000 == 0 and start > 0:
            print(f"  progress: {start}/{n} ({100*start/n:.1f}%)", flush=True)
    
    return counts.tolist()


def compute_consumed_fast(weights, consumed_samples):
    """Fast approximate per-source count using mathematical formula.
    
    The Bresenham algorithm produces counts very close to w[s]*n.
    The exact count differs by at most 1 from round(w[s]*n).
    We compute the exact counts by processing the fractional remainders.
    """
    w = numpy.asarray(weights, dtype=numpy.float64)
    n = consumed_samples
    n_sources = len(weights)
    
    # Base counts: floor(w[s] * n)
    base = numpy.floor(w * n).astype(numpy.int64)
    remainder = w * n - base  # fractional part
    total_base = int(base.sum())
    leftover = n - total_base  # number of sources that need +1
    
    if leftover == 0:
        return base.tolist()
    
    # Distribute leftover among sources with highest remainders
    # This matches the Bresenham algorithm's behavior
    order = numpy.argsort(-remainder)
    result = base.copy()
    for i in range(leftover):
        result[order[i]] += 1
    
    return result.tolist()


def verify_fast_against_exact(weights, n_test=10000):
    """Verify fast formula matches exact Bresenham for small n."""
    w = numpy.asarray(weights, dtype=numpy.float64)
    n = n_test
    n_sources = len(weights)
    
    # Exact
    sampled = numpy.zeros(n_sources, dtype=numpy.int64)
    exact_counts = numpy.zeros(n_sources, dtype=numpy.int64)
    for i in range(n):
        deficit = w * (i + 1) - sampled
        chosen = int(numpy.argmax(deficit))
        sampled[chosen] += 1
        exact_counts[chosen] += 1
    
    # Fast
    fast_counts = compute_consumed_fast(weights, n)
    
    match = numpy.array_equal(exact_counts, fast_counts)
    return match, exact_counts.tolist(), fast_counts


def main():
    p = argparse.ArgumentParser(description="Compute cursor offsets for S1->S2 cold switch")
    p.add_argument("--s1-tsv", required=True)
    p.add_argument("--s2-config", required=True)
    p.add_argument("--switch-step", type=int, default=350000)
    p.add_argument("--global-batch-size", type=int, default=256)
    p.add_argument("--output", required=True)
    p.add_argument("--method", choices=["fast", "exact"], default="fast",
                   help="fast=mathematical formula (default), exact=sequential Bresenham")
    args = p.parse_args()

    s1_sources = parse_blend_tsv(args.s1_tsv)
    s1_keys = [s[0] for s in s1_sources]
    s1_weights = [s[2] for s in s1_sources]
    print(f"S1 sources ({len(s1_sources)}):", flush=True)
    for i, (k, _, w) in enumerate(s1_sources):
        print(f"  [{i}] {k} weight={w}", flush=True)

    with open(args.s2_config, "r") as f:
        s2_cfg = json.load(f)
    s2_keys = s2_cfg["s2_source_keys"]
    shared_mask = s2_cfg["shared_source_mask"]

    consumed = args.switch_step * args.global_batch_size
    print(f"\nSwitch step={args.switch_step} GBS={args.global_batch_size} consumed={consumed}", flush=True)

    # Verify fast method against exact for small sample
    match, exact_small, fast_small = verify_fast_against_exact(s1_weights, 10000)
    print(f"Fast vs exact verification (n=10000): match={match}", flush=True)
    if not match:
        print(f"  exact={exact_small} fast={fast_small}", flush=True)
        print("  WARNING: fast method differs, falling back to exact", flush=True)
        args.method = "exact"

    if args.method == "fast":
        print(f"Using fast method for {consumed} samples...", flush=True)
        cps = compute_consumed_fast(s1_weights, consumed)
    else:
        print(f"Using exact Bresenham for {consumed} samples (may be slow)...", flush=True)
        cps = compute_consumed_per_source_vectorized(s1_weights, consumed)

    for i, c in enumerate(cps):
        print(f"  S1 source [{i}] {s1_keys[i]}: {c} samples ({100*c/consumed:.2f}%)", flush=True)

    s1_key_to_idx = {k: i for i, k in enumerate(s1_keys)}
    s2_offsets = []
    for s2_idx, s2_key in enumerate(s2_keys):
        is_shared = shared_mask[s2_idx] if s2_idx < len(shared_mask) else False
        if is_shared and s2_key in s1_key_to_idx:
            offset = cps[s1_key_to_idx[s2_key]]
        else:
            offset = 0
        s2_offsets.append(offset)
        print(f"  S2 source [{s2_idx}] {s2_key}: {'SHARED' if is_shared else 'NEW'} offset={offset}", flush=True)

    out = {
        "description": f"S1 per-source consumption at step {args.switch_step} ({consumed} samples)",
        "consumed_per_source": s2_offsets,
        "shared_source_mask": shared_mask,
        "s2_source_keys": s2_keys,
        "s1_source_keys": s1_keys,
        "s1_weights": s1_weights,
        "switch_step": args.switch_step,
        "global_batch_size": args.global_batch_size,
        "total_consumed_samples": consumed,
        "s1_consumed_per_source_original": cps,
        "method": args.method,
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nCursor offsets written to: {args.output}", flush=True)
    print(f"S2 cursor offsets: {s2_offsets}", flush=True)

if __name__ == "__main__":
    main()
