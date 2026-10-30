#!/usr/bin/env python3
"""Append Aether-Layout-010 (PG-short audit) to the Aether-Layout jsonl."""
import json, pathlib

bench_dir = pathlib.Path("/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow")
jsonl_path = bench_dir / "EDA-Eval-DesignFlow-Aether-Layout.jsonl"
debug_dir = pathlib.Path("/nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Aether-010")

prompt = (debug_dir / "prompt.txt").read_text()
test = (debug_dir / "checker.tcl").read_text()

metadata = {
    "task_name": (
        "pyAether layout cellview PG (power/ground) short report audit: parse SHORT/SUMMARY lines "
        "(ordered net pair, type power|ground|mixed|signal, resistance real, layer, status short|leak|clean), "
        "count distinct ordered pairs (last-wins dedup on duplicate (net_a,net_b) -- replace type/resistance/layer/status "
        "not sum not first-wins; (a,b) and (b,a) are DIFFERENT pairs not normalized), classify effective status "
        "(case-insensitive explicit; absent/empty -> infer R<1.0=short / 1.0<=R<100.0=leak / R>=100.0=clean never unknown), "
        "count power_count (type contains 'power' OR type=='mixed') and ground_count (type contains 'ground' OR type=='mixed' -- "
        "mixed counts in BOTH), build mixed_pairs list (type=='mixed' all pairs regardless of clean/non-clean, lex-sorted), "
        "compute max_resistance + worst_pair over NON-CLEAN pairs only (clean excluded even if higher R; no non-clean -> -1.0/empty; "
        "tie -> lex smallest 'net_a-net_b' lsort -dictionary numeric-aware via2-vss<via10-vss), layers_affected = union over non-clean "
        "only lex-sorted dedup, reconcile SUMMARY (shorts_checked/shorts/leaks/clean int, max_resistance numeric expr==, worst_pair string; "
        "absent fields not reported), emit single priority-ordered verdict (FAIL if short>0 > REVIEW if leak>0 > INCOMPLETE if mismatched "
        "or no-summary > PASS)"
    ),
    "direction": "layout_aether",
    "scenario": (
        "Layout/QA sign-off: given a textual pyAether-emitted PG (power/ground) short report (SHORT <net_a> <net_b> type=<T> "
        "resistance=<R> layer=<L> status=<S> lines + a SUMMARY line), audit it before tape-out -- classify each net pair by short/leak/clean "
        "status, count power/ground/mixed type involvement (mixed counts in both), find the worst non-clean pair by resistance, identify "
        "affected layers (non-clean only), reconcile the SUMMARY numerically, and emit a fail/review/incomplete/pass verdict. "
        "Waveview-bypass for the aether host sandbox init timeout: this audits a layout WORK PRODUCT (textual PG-short report) with pure "
        "string + float/integer math on waveview tcl, staying in the layout_aether category without needing the aether host."
    ),
    "layer": "L2",
    "topic": (
        "layout-pgshort-audit-status-case-insensitive-last-wins-dedup-on-ordered-pair-replace-not-sum-a-b-and-b-a-are-different-pairs-"
        "not-normalized-status-absent-infer-R-lt-1-short-1-leak-100-clean-never-unknown-R-eq-1-leak-inclusive-R-eq-100-clean-inclusive-"
        "missing-resistance-default-0-short-mixed-counts-in-both-power-and-ground-power-count-and-ground-count-max-resistance-worst-pair-"
        "over-non-clean-only-clean-excluded-no-non-clean-minus-1-empty-worst-pair-tie-lex-smallest-net-a-net-b-dictionary-numeric-aware-"
        "via2-vss-lt-via10-vss-layers-affected-union-over-non-clean-only-lex-sorted-mismatched-summary-int-for-counts-numeric-for-max-"
        "resistance-string-for-worst-pair-absent-fields-not-reported-verdict-priority-short-gt-0-FAIL-gt-leak-gt-0-REVIEW-gt-mismatched-"
        "or-no-summary-INCOMPLETE-gt-PASS"
    ),
    "difficulty": "medium",
    "design": (
        "DERIVED (per 2026-10-29 ephemeral-session strategy: cline sessions cleared, fresh mining dead; aether host run_code init times "
        "out so layout_aether cannot be verified on the aether sandbox) from known real pyAether layout / PG-short sign-off work patterns "
        "(layout_aether 14534 scan hits -- the LARGEST class; calibre 12664 / hspice 10757 scan hits for short/leak extraction checks; "
        "PG connectivity / short detection is a core layout sign-off task). Real task: after a pyAether layout extraction session, the tool "
        "emits a per-pair PG short report with the two net names, the short type (power/ground/mixed/signal), the measured resistance, the "
        "layer, an explicit status (short/leak/clean), plus a SUMMARY header; the engineer must audit that report for PG integrity (any "
        "short is a tape-out blocker, any leak needs review), count power/ground involvement (mixed counts in both), find the worst non-clean "
        "pair, identify affected layers, reconcile the SUMMARY, and decide sign-off verdict. 10 real traps: (1) status CASE-INSENSITIVE "
        "('short'/'SHORT'/'Short' all match -- naive case-sensitive misses uppercase); (2) DUPLICATE ordered pair (net_a,net_b) LAST-WINS "
        "(later SHORT line replaces earlier type/resistance/layer/status, not summed, not first-wins; counts once -- naive first-wins keeps "
        "a stale short); (3) status ABSENT/EMPTY -> infer from resistance: R<1.0->short, 1.0<=R<100.0->leak, R>=100.0->clean (never unknown -- "
        "naive treats absent as clean); (4) R==1.0 -> leak (inclusive lower bound), R==100.0 -> clean (inclusive) -- naive uses strict < for "
        "both boundaries; (5) missing resistance -> default 0.0 -> short (0.0<1.0) -- naive defaults to clean or errors; (6) max_resistance/"
        "worst_pair/layers_affected over NON-CLEAN pairs ONLY (clean excluded even if R is the file max; no non-clean -> -1.0/empty/{} -- "
        "naive takes max over ALL including clean); (7) worst_pair tie at max_resistance -> lexicographically SMALLEST 'net_a-net_b' (lsort "
        "-dictionary numeric-aware so 'via2-vss' < 'via10-vss' -- naive ASCII string compare returns 'via10-vss'); (8) type 'mixed' counts "
        "in BOTH power_count AND ground_count (not exclusive -- naive puts mixed only in a separate bucket); (9) (net_a,net_b) is ORDERED: "
        "(a,b) and (b,a) are DIFFERENT pairs, both counted, not normalized/sorted -- naive normalizes the pair; (10) mismatched_summary: "
        "shorts_checked/shorts/leaks/clean INTEGER equality; max_resistance NUMERIC equality (expr == so 5.0==5 is MATCH not mismatch); "
        "worst_pair STRING equality; ABSENT SUMMARY fields NOT reported; empty list if no SUMMARY; verdict priority: short>0->FAIL > leak>0"
        "->REVIEW > mismatched/no-summary->INCOMPLETE > PASS (REVIEW beats INCOMPLETE even with mismatched -- naive puts INCOMPLETE above "
        "REVIEW). Task layout_pgshort_audit(report_text) -> flat dict (12 keys). runtime tcl/waveview (pure string + float/integer math, "
        "POSIX classes). WAVEVIEW BYPASS (same strategy as Aether-Layout-002..009): audits the textual PG-short work product on waveview tcl, "
        "making the largest class (layout_aether 14534) verifiable without the aether host. DISTINCT from -002 (placement/overlap), -003 "
        "(DRC violation-report), -004 (GDS layer-map usage), -005 (density-fill below-min), -006 (metal-fill target-meeting), -007 (antenna "
        "per-net max-ratio non-SKIP worst-net), -008 (per-(via,cut) enclosure AND-logic min-enclosure) and -009 (per-net routing-completeness "
        "status + missing-via-on-layer-change + single-segment watchlist + non-SKIP max-segment-net) -- this is a per-pair PG-short/leak "
        "resistance classification audit (status inference by resistance threshold + mixed-type dual-count + non-clean max-resistance-worst-"
        "pair + ordered-pair-no-normalization), a complementary angle on layout sign-off (PG connectivity / short-leak compliance)."
    ),
    "tcr_refs": [
        "status_case_insensitive_short_SHORT_Short_all_match",
        "duplicate_ordered_pair_last_wins_replaces_type_resistance_layer_status_not_sums_not_first_wins_counts_once",
        "status_absent_or_empty_infer_from_resistance_R_lt_1_short_1_leak_100_clean_never_unknown",
        "resistance_boundary_R_eq_1_leak_inclusive_R_eq_100_clean_inclusive_strict_thresholds",
        "missing_resistance_default_0_short_0_lt_1",
        "max_resistance_worst_pair_layers_affected_over_non_clean_only_clean_excluded_no_non_clean_minus_1_empty_empty_list",
        "worst_pair_tie_at_max_resistance_lexicographically_smallest_net_a_net_b_dictionary_numeric_aware_via2_vss_lt_via10_vss",
        "type_mixed_counts_in_both_power_count_and_ground_count_not_exclusive",
        "ordered_pair_a_b_and_b_a_are_different_pairs_both_counted_not_normalized_not_sorted",
        "mismatched_summary_int_for_counts_numeric_for_max_resistance_string_for_worst_pair_absent_fields_not_reported_verdict_priority_short_gt_0_FAIL_gt_leak_gt_0_REVIEW_gt_mismatched_or_no_summary_INCOMPLETE_gt_PASS",
    ],
    "heavy": False,
    "wall_time_sec": 1.0,
    "status": "ready",
}

entry = {
    "task_id": "EDA-Eval-DesignFlow-Aether-Layout-010",
    "prompt": prompt,
    "entry_point": "layout_pgshort_audit",
    "test": test,
    "metadata": metadata,
    "mode": "design_flow",
    "runtime": {"lang": "tcl", "host": "waveview"},
    "attachments": [],
    "budget": {"max_turns": 40, "wall_time_sec": 1800},
}

# Verify it's valid JSON
json.dumps(entry)

# Append to jsonl
with open(jsonl_path, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# Verify
lines = open(jsonl_path).readlines()
print(f"Appended. Total lines in jsonl: {len(lines)}")
last = json.loads(lines[-1])
print(f"task_id: {last['task_id']}")
print(f"entry_point: {last['entry_point']}")
print(f"prompt length: {len(last['prompt'])}")
print(f"test length: {len(last['test'])}")
print(f"metadata keys: {sorted(last['metadata'].keys())}")
print(f"runtime: {last['runtime']}")
print(f"mode: {last['mode']}")
