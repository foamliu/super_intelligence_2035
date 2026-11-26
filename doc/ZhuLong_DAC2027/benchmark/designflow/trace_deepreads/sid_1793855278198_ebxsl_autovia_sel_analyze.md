# Trace deepread — sid `1793855278198_ebxsl`

- host: hfeg0pkn004
- session_file: t0002038 / 1793855278198_ebxsl
- match_count: 379
- domain: layout_aether
- msgs: 349 (2.29 MB)
- shard: C
- round: 172
- case_id: EDA-Eval-DesignFlow-AutoViaSelAnalyze-001
- selected: 2026-11-06

## Task summary (real)

The operator is iterating on a custom Aether layout helper `xyCreateAutoVia.py`
that, given a set of "figures" (path / pathSeg / ArrayInst instances) on two
orthogonal routing layers, must select which endpoints of which figures can be
paired to drop automatic vias.  The bulk of the conversation is debugging the
selection / geometric-reasoning pipeline:

1. classify each figure endpoint by **direction** (H vs V layer, head vs tail),
2. collect candidate endpoints, **sort** along the dominant axis,
3. **normalize** to indices, then form index **pairs**,
4. for each pair compute the **via_loc** (anchor point) and the **h_delta / v_delta**
   vectors that tell the helper how far each endpoint drifts from the anchor.

## Extracted subtask (synthesized benchmark)

We isolate the *offline, deterministic core* of that pipeline:

- input  : a JSON list of figure descriptors (path / pathSeg / ArrayInst),
- output : a JSON report containing
  - the classified endpoints,
  - the sorted & normalized index pairs,
  - per-pair via_loc, h_delta, v_delta,
- the reference solution is pure stdlib (no pyAether) so it can be graded
  off-host.

Visible input A (5 figures, 2 pairs, via_locs `[[55.45, 2.0], [50.0, 1.03]]`)
differs from hidden input B (7 figures incl. an oblique path, a rect, and a
no-selection case as invalids; 2 pairs, via_locs `[[20.0, 5.0], [14.0, 9.0]]`)
in scale, structure and selection space.

## check.py

- 14 conditions (a..n):
  a  submit.zip contains `auto_via_analyze.py` + `py_compile` clean + stdlib only
  b  runnable with `--figures <A> --figures <B>` from a clean cwd
  c  emits a JSON object with `endpoints`, `pairs`, `via`
  d  no leakage of reference / check.py / jsonl / hidden into the SUT workdir
  e  deterministic sha256 across two runs
  f  B — endpoint count correct
  g  B — endpoint direction classification correct
  h  B — index pairs correct (sorted + normalized)
  i  B — via_loc correct for pair 0  (`[20.0, 5.0]`)
  j  B — via_loc correct for pair 1  (`[14.0, 9.0]`)
  k  B — h_delta / v_delta correct for pair 0
  l  B — h_delta / v_delta correct for pair 1
  m  cross-input guard on A — via_locs `[[55.45, 2.0], [50.0, 1.03]]`
  n  handles invalid figures (oblique path / rect / no-selection) gracefully
- self-contained: A & B fixtures embedded as string literals; no path deps.

## self-verify

- ref solution        : CHECK PASS (14/14)
- negative_selftest   : NEG_RC = 0 (all 4 mutants fail)
- §4.9 fakes          : empty / only-print / core-deleted all FAIL
- sha256 deterministic across two runs
- test==disk roundtrip sha = 6d32280221ec

## references

- reference solution : `reference/EDA-Eval-DesignFlow-AutoViaSelAnalyze-001/solution/auto_via_analyze.py`
- grader            : `reference/EDA-Eval-DesignFlow-AutoViaSelAnalyze-001/check.py`
- visible fixture A : `assets/EDA-Eval-DesignFlow-AutoViaSelAnalyze-001/A/selection_A.json`
- hidden fixture B  : `reference/EDA-Eval-DesignFlow-AutoViaSelAnalyze-001/hidden/selection_B.json`
