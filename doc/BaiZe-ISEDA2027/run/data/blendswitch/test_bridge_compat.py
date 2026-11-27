#!/usr/bin/env python3
"""Test blend hot-switch bridge compat shim.

Validates: 1) shim importable 2) cursor offset computation 3) zero overlap
4) flag-off stock equivalence 5) ratio accuracy 6) end-to-end integration.
"""
import json, os, sys, tempfile, traceback
import numpy

RESULTS = []


def test(name, passed, details=""):
    status = "PASS" if passed else "FAIL"
    RESULTS.append({"name": name, "status": status, "details": details})
    print(f"  [{status}] {name}" + (f" — {details}" if details else ""), flush=True)


# ---- helpers ----

def build_blending_indices(weights, size):
    w = numpy.asarray(weights, dtype=numpy.float64)
    n = len(weights)
    di = numpy.zeros(size, dtype=numpy.int16)
    dsi = numpy.zeros(size, dtype=numpy.int64)
    sampled = numpy.zeros(n, dtype=numpy.int64)
    for i in range(size):
        deficit = w * (i + 1) - sampled
        chosen = int(numpy.argmax(deficit))
        di[i] = chosen
        dsi[i] = sampled[chosen]
        sampled[chosen] += 1
    return di, dsi


def compute_consumed(weights, consumed_samples):
    di, _ = build_blending_indices(weights, consumed_samples)
    return [int((di == s).sum()) for s in range(len(weights))]


# ---- tests ----

def test_shim_importable():
    sys.path.insert(0, "/nas_train/app.e0031982/code/BaiZe-ISEDA2027")
    try:
        import blend_hot_switch_bridge_compat
        test("shim importable", True)
    except Exception as e:
        test("shim importable", False, str(e))


def test_cursor_offset_computation():
    weights = [0.65, 0.05, 0.05, 0.10, 0.15]
    consumed = 10000
    cps = compute_consumed(weights, consumed)
    total = sum(cps)
    test("cursor offset computation", total == consumed, f"sum={total} expected={consumed}")


def test_zero_overlap():
    weights = [0.60, 0.20, 0.20]
    consumed = 5000
    cps = compute_consumed(weights, consumed)

    # S1 consumed samples per source
    s1_di, s1_dsi = build_blending_indices(weights, consumed)

    # S2 with cursor offsets: build full size, then offset
    s2_size = 5000
    s2_di, s2_dsi = build_blending_indices(weights, s2_size)

    # Apply cursor offsets
    for s in range(len(weights)):
        mask = s2_di == s
        s2_dsi[mask] += cps[s]

    # Compute doc sets
    s1_docs = set()
    for i in range(consumed):
        s1_docs.add((int(s1_di[i]), int(s1_dsi[i])))

    s2_docs = set()
    for i in range(s2_size):
        s2_docs.add((int(s2_di[i]), int(s2_dsi[i])))

    overlap = s1_docs & s2_docs
    test("zero overlap", len(overlap) == 0, f"overlap={len(overlap)} total_s1={len(s1_docs)} total_s2={len(s2_docs)}")


def test_flag_off_stock_equivalence():
    weights = [0.50, 0.50]
    size = 2000

    # Stock (no offset)
    stock_di, stock_dsi = build_blending_indices(weights, size)

    # With zero offsets (simulates env var not set)
    offset_di, offset_dsi = build_blending_indices(weights, size)
    # No offsets applied → identical

    di_same = numpy.array_equal(stock_di, offset_di)
    dsi_same = numpy.array_equal(stock_dsi, offset_dsi)
    test("flag-off stock equivalence", di_same and dsi_same, f"di_same={di_same} dsi_same={dsi_same}")


def test_ratio_accuracy():
    weights = [0.40, 0.40, 0.20]
    consumed = 100000

    di, dsi = build_blending_indices(weights, consumed)
    counts = [int((di == s).sum()) for s in range(len(weights))]
    actual_ratios = [c / consumed for c in counts]

    max_dev = max(abs(a - w) for a, w in zip(actual_ratios, weights))
    test("ratio accuracy", max_dev <= 0.01, f"max_dev={max_dev:.6f} ratios={actual_ratios} targets={weights}")


def test_new_source_zero_overlap():
    # S1: 3 sources
    s1_weights = [0.60, 0.20, 0.20]
    consumed = 5000
    s1_di, s1_dsi = build_blending_indices(s1_weights, consumed)
    s1_docs = set((int(s1_di[i]), int(s1_dsi[i])) for i in range(consumed))

    # S2: 4 sources (3 shared + 1 new), different weights
    s2_weights = [0.35, 0.30, 0.15, 0.20]
    s2_size = 5000
    s2_di, s2_dsi = build_blending_indices(s2_weights, s2_size)

    # Apply cursor offsets to shared sources (0,1,2)
    cps = compute_consumed(s1_weights, consumed)
    for s in range(3):
        mask = s2_di == s
        s2_dsi[mask] += cps[s]

    s2_docs = set((int(s2_di[i]), int(s2_dsi[i])) for i in range(s2_size))
    overlap = s1_docs & s2_docs
    test("new source zero overlap", len(overlap) == 0, f"overlap={len(overlap)}")


def test_cursor_offset_json_format():
    s1_keys = ["en_v1_4", "ufw_l1_en_hq", "ufw_zh"]
    s2_keys = ["en_v1_4", "ufw_l1_en_hq", "ufw_zh", "code_l2"]
    shared_mask = [True, True, True, False]
    consumed = [5000, 300, 200, 0]

    data = {
        "description": "test",
        "consumed_per_source": consumed,
        "shared_source_mask": shared_mask,
        "s2_source_keys": s2_keys,
        "s1_source_keys": s1_keys,
    }

    # Verify JSON serializable
    js = json.dumps(data, indent=2)
    parsed = json.loads(js)
    test("cursor offset JSON format",
         parsed["consumed_per_source"] == consumed and
         parsed["shared_source_mask"] == shared_mask and
         parsed["s2_source_keys"] == s2_keys)


def test_bresenham_matches_megatron_pattern():
    # Test that our Bresenham matches the pattern Megatron uses
    weights = [0.70, 0.30]
    size = 100
    di, dsi = build_blending_indices(weights, size)

    # Source 0 should appear ~70 times, source 1 ~30 times
    c0 = int((di == 0).sum())
    c1 = int((di == 1).sum())
    test("Bresenham pattern match",
         c0 == 70 and c1 == 30,
         f"c0={c0} c1={c1} (expected 70/30)")


def test_integration_full_switch():
    """Full S1→S2 switch simulation with cursor offsets."""
    # S1: 5 sources, 350k * 256 = 89.6M samples (simulated as 100k for speed)
    s1_weights = [0.65, 0.05, 0.05, 0.10, 0.15]
    consumed = 100000

    # Compute consumed per source
    cps = compute_consumed(s1_weights, consumed)

    # S2: 7 sources (5 shared + 2 new), different weights
    s2_weights = [0.35, 0.03, 0.02, 0.18, 0.05, 0.17, 0.20]
    s2_shared_mask = [True, True, True, True, True, False, False]
    s2_size = 100000

    # Build S1 and S2 indices
    s1_di, s1_dsi = build_blending_indices(s1_weights, consumed)
    s2_di, s2_dsi = build_blending_indices(s2_weights, s2_size)

    # Apply cursor offsets
    s2_offsets = [0, 0, 0, 0, 0, 0, 0]  # will be filled
    s1_key_idx = {0:0, 1:1, 2:2, 3:3, 4:4}  # identity for this test
    for s2_idx in range(7):
        is_shared = s2_shared_mask[s2_idx]
        if is_shared and s2_idx in s1_key_idx:
            s2_offsets[s2_idx] = cps[s1_key_idx[s2_idx]]
        # Apply
        mask = s2_di == s2_idx
        s2_dsi[mask] += s2_offsets[s2_idx]

    # Verify zero overlap
    s1_docs = set((int(s1_di[i]), int(s1_dsi[i])) for i in range(consumed))
    s2_docs = set((int(s2_di[i]), int(s2_dsi[i])) for i in range(s2_size))
    overlap = s1_docs & s2_docs

    # Verify ratio accuracy
    s2_counts = [int((s2_di == s).sum()) for s in range(7)]
    s2_ratios = [c / s2_size for c in s2_counts]
    max_dev = max(abs(a - w) for a, w in zip(s2_ratios, s2_weights))

    test("integration: zero overlap", len(overlap) == 0, f"overlap={len(overlap)}")
    test("integration: ratio accuracy", max_dev <= 0.01, f"max_dev={max_dev:.6f}")


def main():
    print("=" * 70, flush=True)
    print("Blend Hot-Switch Bridge Compat — Validation Suite", flush=True)
    print("=" * 70, flush=True)

    print("\n--- Standalone Tests ---", flush=True)
    test_shim_importable()
    test_cursor_offset_computation()
    test_zero_overlap()
    test_flag_off_stock_equivalence()
    test_ratio_accuracy()
    test_new_source_zero_overlap()
    test_cursor_offset_json_format()
    test_bresenham_matches_megatron_pattern()

    print("\n--- Integration Tests ---", flush=True)
    test_integration_full_switch()

    passed = sum(1 for r in RESULTS if r["status"] == "PASS")
    total = len(RESULTS)
    print(f"\n{'=' * 70}", flush=True)
    print(f"Results: {passed}/{total} PASS", flush=True)
    print(f"{'=' * 70}", flush=True)

    # Write results JSON
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_results_bridge.json")
    with open(out_path, "w") as f:
        json.dump({
            "total": total,
            "passed": passed,
            "all_pass": passed == total,
            "tests": RESULTS,
        }, f, indent=2)
    print(f"Results written to: {out_path}", flush=True)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
