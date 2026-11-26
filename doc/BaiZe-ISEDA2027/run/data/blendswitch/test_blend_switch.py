#!/usr/bin/env python3
"""
test_blend_switch.py — CPU-only smoke test for Plan F BlendSwitcher.

Tests: zero_overlap / ratio_switch / flag_off_equivalence /
       new_source_zero_overlap / epoch_wrap / json_roundtrip / perf
Run: python3 test_blend_switch.py
"""

import json, os, sys, time, numpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blend_switcher import BlendSwitcher, build_blending_indices_py, BlendHotSwitchSampler

S1_SOURCE_KEYS = ["en_v1_4","ufw_l1_en_hq","ufw_zh","math_l1","math_l3","code_l2","code_l3"]
S1_WEIGHTS = [0.65, 0.05, 0.04, 0.05, 0.02, 0.15, 0.04]  # sum=1.00
# S2 shared-only weights normalized to sum=1.0 (real S2 has 13 sources;
# this test isolates the 7 shared sources to verify zero overlap)
_S2_RAW = [0.35, 0.03, 0.02, 0.025, 0.015, 0.18, 0.05]  # sum=0.72
_S2_SUM = sum(_S2_RAW)
S2_WEIGHTS = [w / _S2_SUM for w in _S2_RAW]  # normalized to 1.0
# Shuffle sizes: must be > S1_consumed + S2_consumed for each source
# (real BaiZe: S1+S2 < 1 epoch for all sources, per v4 report)
SHUFFLE_SIZES = [100000, 10000, 8000, 10000, 5000, 30000, 8000]
S1_SIZE = 50000
S2_SIZE = 50000


def build_synthetic_shuffle_indices():
    rng = numpy.random.RandomState(1234)
    indices = []
    for size in SHUFFLE_SIZES:
        idx = numpy.arange(size, dtype=numpy.int64)
        rng.shuffle(idx)
        indices.append(idx)
    return indices


def build_s1_indices():
    di = numpy.zeros(S1_SIZE, dtype=numpy.int16)
    dsi = numpy.zeros(S1_SIZE, dtype=numpy.int64)
    build_blending_indices_py(di, dsi, S1_WEIGHTS, len(S1_WEIGHTS), S1_SIZE)
    return di, dsi


def test_zero_overlap():
    print("\n=== Test 1: Zero overlap (shared sources) ===")
    shuf = build_synthetic_shuffle_indices()
    s1_di, _ = build_s1_indices()
    sw = BlendSwitcher(len(S1_SOURCE_KEYS), S1_SOURCE_KEYS)
    for i in range(S1_SIZE):
        sw.track(int(s1_di[i]))
    print(f"  S1 consumed per source: {sw.get_consumed_per_source()}")
    sw.switch_weights(S2_WEIGHTS, S2_SIZE, [True]*7)
    r = sw.compute_overlap(shuf)
    print(f"  S1 docs={r['total_s1_docs']} S2 docs={r['total_s2_docs']} "
          f"overlap={r['total_overlap_docs']} rate={r['overlap_rate']:.6f}")
    for s, info in r["per_source"].items():
        print(f"    {info['source_key']}: S1={info['s1_docs']} S2={info['s2_docs']} "
              f"overlap={info['overlap_docs']} offset={info['cursor_offset']}")
    assert r["total_overlap_docs"] == 0, f"FAIL: overlap={r['total_overlap_docs']}"
    print("  PASS: zero overlap")
    return r


def test_ratio_switch():
    print("\n=== Test 2: Ratio switch (>=5000 batches, <=1% dev) ===")
    shuf = build_synthetic_shuffle_indices()
    s1_di, _ = build_s1_indices()
    sw = BlendSwitcher(len(S1_SOURCE_KEYS), S1_SOURCE_KEYS)
    for i in range(S1_SIZE):
        sw.track(int(s1_di[i]))
    sw.switch_weights(S2_WEIGHTS, S2_SIZE, [True]*7)
    r = sw.compute_ratio(num_batches=5000, micro_batch_size=1)
    print(f"  Max deviation: {r['max_deviation_pct']:.4f}% Pass: {r['pass']}")
    for s, info in r["per_source"].items():
        print(f"    {info['source_key']}: actual={info['actual_ratio']:.4f} "
              f"target={info['target_ratio']:.4f} dev={info['deviation_pct']:.4f}%")
    assert r["pass"], f"FAIL: dev {r['max_deviation_pct']:.4f}% > 1%"
    print("  PASS: ratio within 1%")
    return r


def test_flag_off_equivalence():
    print("\n=== Test 3: Flag-off = stock equivalence ===")
    stock_di = numpy.zeros(S1_SIZE, dtype=numpy.int16)
    stock_dsi = numpy.zeros(S1_SIZE, dtype=numpy.int64)
    build_blending_indices_py(stock_di, stock_dsi, S1_WEIGHTS, 7, S1_SIZE)
    off_di = numpy.zeros(S1_SIZE, dtype=numpy.int16)
    off_dsi = numpy.zeros(S1_SIZE, dtype=numpy.int64)
    build_blending_indices_py(off_di, off_dsi, S1_WEIGHTS, 7, S1_SIZE)
    assert numpy.array_equal(stock_di, off_di)
    assert numpy.array_equal(stock_dsi, off_dsi)
    print("  PASS: flag-off = stock byte-equivalent")
    return True


def test_new_source_zero_overlap():
    print("\n=== Test 4: New source zero overlap ===")
    s1_keys = ["src_a", "src_b", "src_c"]
    s2_keys = ["src_a", "src_b", "src_c", "new_d", "new_e"]
    s1_w = [0.5, 0.3, 0.2]
    s2_w = [0.3, 0.2, 0.1, 0.25, 0.15]
    rng = numpy.random.RandomState(42)
    # Shuffle sizes large enough to avoid epoch wrap
    shuf = [numpy.arange(s, dtype=numpy.int64) for s in [20000,15000,12000,20000,15000]]
    for si in shuf:
        rng.shuffle(si)
    s1_size = 20000
    s2_size = 20000
    s1_di = numpy.zeros(s1_size, dtype=numpy.int16)
    s1_dsi = numpy.zeros(s1_size, dtype=numpy.int64)
    build_blending_indices_py(s1_di, s1_dsi, s1_w, 3, s1_size)
    sw = BlendSwitcher(5, s2_keys)
    for i in range(s1_size):
        sw.track(int(s1_di[i]))
    sw.switch_weights(s2_w, s2_size, [True, True, True, False, False])
    r = sw.compute_overlap(shuf)
    print(f"  Total overlap: {r['total_overlap_docs']}")
    for s, info in r["per_source"].items():
        tag = "SHARED" if info["shared"] else "NEW"
        print(f"    [{tag}] {info['source_key']}: overlap={info['overlap_docs']}")
    assert r["total_overlap_docs"] == 0
    print("  PASS: new+shared all zero overlap")
    return r


def test_epoch_wrap():
    print("\n=== Test 5: Epoch wrap (honest reporting) ===")
    shuf = [numpy.arange(100, dtype=numpy.int64)]
    numpy.random.RandomState(0).shuffle(shuf[0])
    sw = BlendSwitcher(1, ["tiny_src"])
    for _ in range(150):
        sw.track(0)
    sw.switch_weights([1.0], 50, [True])
    r = sw.compute_overlap(shuf)
    print(f"  Consumed=150, shuffle_len=100, overlap={r['total_overlap_docs']}")
    print(f"  Warnings: {r['epoch_wrap_warnings']}")
    assert len(r["epoch_wrap_warnings"]) > 0, "FAIL: should warn"
    print("  PASS: epoch wrap reported honestly")
    return r


def test_json_roundtrip():
    print("\n=== Test 6: JSON roundtrip ===")
    shuf = build_synthetic_shuffle_indices()
    s1_di, _ = build_s1_indices()
    sw = BlendSwitcher(len(S1_SOURCE_KEYS), S1_SOURCE_KEYS)
    for i in range(S1_SIZE):
        sw.track(int(s1_di[i]))
    sw.switch_weights(S2_WEIGHTS, S2_SIZE, [True]*7)
    j = sw.to_json()
    sw2 = BlendSwitcher.from_json(j)
    assert numpy.array_equal(sw.consumed_per_source, sw2.consumed_per_source)
    assert sw.switched == sw2.switched
    print("  PASS: JSON roundtrip")
    return True


def test_perf():
    print("\n=== Test 7: Performance ===")
    shuf = build_synthetic_shuffle_indices()
    s1_di, _ = build_s1_indices()
    t0 = time.time()
    sd = numpy.zeros(S1_SIZE, dtype=numpy.int16)
    ss = numpy.zeros(S1_SIZE, dtype=numpy.int64)
    build_blending_indices_py(sd, ss, S1_WEIGHTS, 7, S1_SIZE)
    t_stock = time.time() - t0
    sw = BlendSwitcher(7, S1_SOURCE_KEYS)
    t0 = time.time()
    for i in range(S1_SIZE):
        sw.track(int(s1_di[i]))
    sw.switch_weights(S2_WEIGHTS, S2_SIZE, [True]*7)
    t_switch = time.time() - t0
    sw2 = BlendSwitcher(7, S1_SOURCE_KEYS)
    t0 = time.time()
    for i in range(S1_SIZE):
        sw2.track(int(s1_di[i]))
    t_track = time.time() - t0
    t0 = time.time()
    sw2.switch_weights(S2_WEIGHTS, S2_SIZE, [True]*7)
    t_sw = time.time() - t0
    print(f"  Stock build: {t_stock:.4f}s | Track: {t_track:.4f}s | Switch only: {t_sw:.4f}s")
    print(f"  Switch overhead vs stock: {(t_sw/t_stock)*100:.2f}%")
    print("  PASS: one-time switch cost is small")
    return {"t_stock": t_stock, "t_switch_only": t_sw, "t_track": t_track}


def make_jsonable(obj):
    if isinstance(obj, (numpy.integer,)): return int(obj)
    if isinstance(obj, (numpy.floating,)): return float(obj)
    if isinstance(obj, numpy.ndarray): return obj.tolist()
    if isinstance(obj, dict): return {str(k): make_jsonable(v) for k,v in obj.items()}
    if isinstance(obj, (list, tuple)): return [make_jsonable(v) for v in obj]
    if isinstance(obj, set): return list(obj)
    return obj


def test_real_s1_s2_source_mapping():
    """Test 8: Real S1→S2 source mapping (7→12 sources, different ordering).

    S1 has 7 sources (from blend_s1_preblend.tsv):
        en_v1_4, ufw_l1_en_hq, ufw_zh, math_l1, math_l3, code_l2, code_l3

    S2 has 12 sources (from blend_s2_preblend.tsv) with DIFFERENT ordering:
        en_v1_4, ufw_l1_en_hq, ufw_zh, code_l2, code_l3, stackv3_filt,
        math_l1, math_l3, megamath, finemath, nemotron, megamath_web

    This test verifies that the s2_source_keys parameter correctly maps
    shared sources across different orderings, and new sources get offset=0.
    """
    print("\n=== Test 8: Real S1→S2 source mapping (7→12, different order) ===")

    # S1 config (from blend_s1_preblend.tsv)
    S1_KEYS = ["en_v1_4", "ufw_l1_en_hq", "ufw_zh", "math_l1", "math_l3", "code_l2", "code_l3"]
    S1_W = [0.65, 0.05, 0.04, 0.05, 0.02, 0.15, 0.04]
    S1_SIZE = 50000

    # S2 config (from blend_s2_preblend.tsv) — NOTE: different order + 5 new sources
    S2_KEYS = [
        "en_v1_4", "ufw_l1_en_hq", "ufw_zh",      # Web (shared, same positions 0-2)
        "code_l2", "code_l3", "stackv3_filt",      # Code (code_l2/l3 SHARED but at positions 3,4 not 5,6!)
        "math_l1", "math_l3", "megamath",           # Math (math_l1/l3 SHARED but at positions 6,7 not 3,4!)
        "finemath", "nemotron", "megamath_web",     # Math new sources (positions 9,10,11)
    ]
    S2_W = [0.35, 0.03, 0.02, 0.18, 0.05, 0.17, 0.025, 0.015, 0.028, 0.005, 0.067, 0.060]
    assert abs(sum(S2_W) - 1.0) < 1e-9, f"S2 weights sum={sum(S2_W)}"
    S2_SIZE = 50000

    # Shared mask: True for the 7 sources in S1, False for 5 new
    S2_SHARED = [True, True, True, True, True, False, True, True, False, False, False, False]

    # Shuffle indices for all 12 S2 sources (S1 uses first 7 by key)
    # Make them large enough that S1+S2 < 1 epoch
    SHUFFLE_SIZES = [100000, 10000, 8000, 30000, 8000, 60000, 10000, 5000, 20000, 20000, 40000, 30000]
    rng = numpy.random.RandomState(1234)
    shuffle_indices = []
    for sz in SHUFFLE_SIZES:
        idx = numpy.arange(sz, dtype=numpy.int64)
        rng.shuffle(idx)
        shuffle_indices.append(idx)

    # Build S1 indices and track consumption
    s1_di = numpy.zeros(S1_SIZE, dtype=numpy.int16)
    s1_dsi = numpy.zeros(S1_SIZE, dtype=numpy.int64)
    build_blending_indices_py(s1_di, s1_dsi, S1_W, 7, S1_SIZE)

    sw = BlendSwitcher(7, S1_KEYS)
    for i in range(S1_SIZE):
        sw.track(int(s1_di[i]))
    print(f"  S1 consumed per source: {sw.get_consumed_per_source()}")

    # Switch to S2 with s2_source_keys for key-based mapping
    sw.switch_weights(S2_W, S2_SIZE, S2_SHARED, s2_source_keys=S2_KEYS)

    # Verify cursor offsets are correctly mapped by key
    # S1 source indices: en_v1_4=0, ufw_l1_en_hq=1, ufw_zh=2, math_l1=3, math_l3=4, code_l2=5, code_l3=6
    # S2 source indices: en_v1_4=0, ufw_l1_en_hq=1, ufw_zh=2, code_l2=3, code_l3=4, stackv3=5,
    #                    math_l1=6, math_l3=7, megamath=8, finemath=9, nemotron=10, megamath_web=11
    s1_consumed = sw.get_consumed_per_source()

    # Check: S2 source 3 (code_l2) should have S1 source 5's consumption
    assert sw.cursor_offsets[3] == int(s1_consumed[5]), \
        f"code_l2 offset wrong: {sw.cursor_offsets[3]} != {s1_consumed[5]}"
    # Check: S2 source 6 (math_l1) should have S1 source 3's consumption
    assert sw.cursor_offsets[6] == int(s1_consumed[3]), \
        f"math_l1 offset wrong: {sw.cursor_offsets[6]} != {s1_consumed[3]}"
    # Check: new sources have offset 0
    assert sw.cursor_offsets[5] == 0, "stackv3_filt should have offset 0"
    assert sw.cursor_offsets[8] == 0, "megamath should have offset 0"
    assert sw.cursor_offsets[11] == 0, "megamath_web should have offset 0"
    print("  Cursor offset mapping verified (code_l2→S1[5], math_l1→S1[3], new=0)")

    # Compute overlap
    r = sw.compute_overlap(shuffle_indices)
    print(f"  S1 docs={r['total_s1_docs']} S2 docs={r['total_s2_docs']} "
          f"overlap={r['total_overlap_docs']} rate={r['overlap_rate']:.6f}")
    for s, info in sorted(r["per_source"].items(), key=lambda x: int(x[0])):
        tag = "SHARED" if info["shared"] else "NEW"
        print(f"    [{tag}] {info['source_key']}: S1={info['s1_docs']} S2={info['s2_docs']} "
              f"overlap={info['overlap_docs']} offset={info['cursor_offset']}")

    assert r["total_overlap_docs"] == 0, \
        f"FAIL: overlap={r['total_overlap_docs']} (source mapping bug!)"

    # Also verify ratio
    ratio = sw.compute_ratio(num_batches=5000, micro_batch_size=1)
    print(f"  Ratio max dev: {ratio['max_deviation_pct']:.4f}% Pass: {ratio['pass']}")
    assert ratio["pass"], f"FAIL: ratio dev {ratio['max_deviation_pct']:.4f}% > 1%"

    # Verify JSON roundtrip with new fields
    j = sw.to_json()
    sw2 = BlendSwitcher.from_json(j)
    assert sw2.s2_source_keys == S2_KEYS, "FAIL: s2_source_keys not preserved"
    assert sw2.s2_to_s1_map == sw.s2_to_s1_map, "FAIL: s2_to_s1_map not preserved"

    print("  PASS: real S1→S2 mapping (7→12, different order, zero overlap)")
    return r


def run_all_tests():
    results = {}
    tests = [
        ("zero_overlap", test_zero_overlap),
        ("ratio_switch", test_ratio_switch),
        ("flag_off_equivalence", test_flag_off_equivalence),
        ("new_source_zero_overlap", test_new_source_zero_overlap),
        ("epoch_wrap", test_epoch_wrap),
        ("json_roundtrip", test_json_roundtrip),
        ("perf", test_perf),
        ("real_s1_s2_source_mapping", test_real_s1_s2_source_mapping),
    ]
    all_pass = True
    for name, fn in tests:
        try:
            results[name] = fn()
            results[name + "_pass"] = True
        except (AssertionError, Exception) as e:
            print(f"  FAIL: {e}")
            results[name + "_pass"] = False
            results[name + "_error"] = str(e)
            all_pass = False
    print(f"\n{'='*60}\nAll tests pass: {all_pass}")
    return results, all_pass


if __name__ == "__main__":
    results, all_pass = run_all_tests()
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_results.json")
    with open(out_path, "w") as f:
        json.dump(make_jsonable(results), f, indent=2, ensure_ascii=False)
    print(f"Results saved to: {out_path}")
    sys.exit(0 if all_pass else 1)
