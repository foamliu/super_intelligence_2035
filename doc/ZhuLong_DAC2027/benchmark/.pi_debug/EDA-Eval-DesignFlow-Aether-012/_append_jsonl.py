#!/usr/bin/env python3
"""Append Aether-Layout-012 (PG-MESH strap audit) to the Aether-Layout jsonl."""
import json, pathlib

bench_dir = pathlib.Path("/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow")
jsonl_path = bench_dir / "EDA-Eval-DesignFlow-Aether-Layout.jsonl"
debug_dir = pathlib.Path("/nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Aether-012")

prompt = (debug_dir / "prompt.txt").read_text()
test = (debug_dir / "checker.tcl").read_text()

metadata = {
    "task_name": (
        "pyAether layout cellview PG (power/ground) MESH strap report audit: parse MESH/SUMMARY lines "
        "(ordered (name, layer) key, direction H|V|horizontal|vertical case-insensitive, width real, space real, "
        "vias integer red-herring, status ok|skip|short|open case-insensitive), count distinct (name, layer) keys "
        "(last-wins dedup on duplicate key -- replace direction/width/space/vias/status not sum not first-wins; "
        "(name,layer) is ORDERED key: vdd1-M5 and vdd1-M6 are DIFFERENT keys both counted), classify straps by NAME "
        "(case-insensitive substring: vdd|vcc|power -> power; gnd|vss|ground -> ground; else unknown) INDEPENDENT of "
        "status, count short/open/skip statuses, compute min_width + max_space + worst_*_strap over NON-SKIP only "
        "(short/open/ok are non-skip and INCLUDED; skip excluded even if extreme; -1.0 + empty if no non-skip), "
        "worst_*_strap tie-break lex-smallest via lsort -dictionary (strap2 < strap10 numeric-aware), coverage_pct = "
        "round((power+ground)*100/total) total==0->0, reconcile SUMMARY (total/power/ground/coverage integer ==; "
        "min_width/max_space NUMERIC == so 0.080 matches 0.08; absent fields not reported), emit single priority-"
        "ordered verdict (FAIL if short>0 > REVIEW if open>0 > INCOMPLETE if mismatched or no-summary > PASS)"
    ),
    "direction": "layout_aether",
    "scenario": (
        "Layout/QA power-mesh sign-off: given a textual pyAether-emitted PG-MESH strap report (MESH <name> <layer> "
        "<direction> <width> <space> <vias> <status> lines + a SUMMARY line), audit it before tape-out -- classify "
        "each strap by name (power/ground/unknown), count status flags (short/open/skip), find the min strap width "
        "and max strap space over the non-skipped straps (with the offending strap name, lex tie-break), compute PG "
        "coverage percentage, reconcile the SUMMARY, and emit a fail/review/incomplete/pass verdict. Waveview-bypass "
        "for the aether host sandbox init timeout: this audits a layout WORK PRODUCT (textual PG-mesh report) with "
        "pure string + integer/float math on waveview tcl, staying in the layout_aether category without needing the "
        "aether host."
    ),
    "layer": "L2",
    "topic": (
        "layout-pgmesh-audit-direction-status-case-insensitive-last-wins-dedup-on-ordered-name-layer-key-replace-"
        "not-sum-layer-is-part-of-key-vdd1-M5-and-vdd1-M6-different-keys-status-absent-default-ok-never-inferred-"
        "missing-width-default-0-missing-space-default-0-missing-vias-default-1-vias-red-herring-not-used-for-counts-"
        "name-classification-by-substring-vdd-vcc-power-gnd-vss-ground-case-insensitive-independent-of-status-skip-"
        "vdd1-still-counts-as-power-min-width-max-space-over-non-skip-only-short-open-ok-included-skip-excluded-even-"
        "if-extreme-no-non-skip-minus-1-empty-worst-strap-tie-break-lsort-dictionary-numeric-aware-strap2-lt-strap10-"
        "coverage-pct-round-power-plus-ground-times-100-div-total-total-0-to-0-mismatched-summary-int-for-counts-"
        "numeric-for-min-width-max-space-0.080-eq-0.08-absent-fields-not-reported-empty-list-if-no-summary-verdict-"
        "priority-short-gt0-FAIL-gt-open-gt0-REVIEW-gt-mismatched-or-no-summary-INCOMPLETE-gt-PASS"
    ),
    "difficulty": "medium",
    "design": (
        "DERIVED (per 2026-10-29 ephemeral-session strategy: cline sessions cleared, fresh mining dead; aether host "
        "run_code init times out so layout_aether cannot be verified on the aether sandbox) from known real pyAether "
        "layout / power-mesh (PG mesh) work patterns (layout_aether 14534 scan hits -- the LARGEST class; PG mesh / "
        "strap planning is a core power-delivery sign-off task). Real task: after a pyAether layout session, the PG-"
        "mesh step emits per-strap records with the strap name, metal layer, routing direction (H/V), width, space, "
        "via-array size, and a status (ok/skip/short/open), plus a SUMMARY header; the engineer must audit that "
        "report for power-delivery completeness (any short is a blocker, any open needs review), classify straps as "
        "power/ground/unknown by name, count status flags, find the narrowest strap and the widest gap over the "
        "active (non-skipped) straps, compute PG coverage, reconcile the SUMMARY, and decide sign-off verdict. 10 "
        "real traps: (1) direction & status CASE-INSENSITIVE (HORIZONTAL/horizontal, OK/Ok, SHORT/Short -- naive "
        "case-sensitive misses uppercase); (2) DUPLICATE (name, layer) key LAST-WINS (later MESH line replaces "
        "earlier direction/width/space/vias/status, not summed, not first-wins; counts once -- naive first-wins keeps "
        "a stale ok); (3) (name, layer) is an ORDERED key: 'vdd1 M5' and 'vdd1 M6' are DIFFERENT keys, both counted "
        "-- layer is part of the key (naive keys on name only collapses them); (4) status ABSENT/EMPTY -> default "
        "'ok' (NEVER inferred from width/space -- naive infers skip from width==0); (5) missing width -> 0.0, missing "
        "space -> 0.0, missing vias -> 1; a missing width of 0.0 CAN become the min_width (default-ok non-skip) -- "
        "naive skips defaults; (6) min_width / max_space / worst_*_strap over NON-SKIP keys ONLY: short/open/ok are "
        "all NON-SKIP and INCLUDED, SKIP keys EXCLUDED even if they hold the extreme; if no non-skip -> -1.0 / empty "
        "(naive includes skip or excludes short); (7) worst_*_strap tie-break lex-smallest via lsort -dictionary "
        "(strap2 < strap10, numeric-aware) NOT plain lsort -increasing (naive lex gives strap10 < strap2); (8) "
        "coverage_pct = round((power+ground)*100/total); total==0 -> 0; computed from NAME-classification counts "
        "regardless of status (a SKIP vdd1 still counts in power_straps and total -- naive excludes skip from power "
        "or sums the vias field for total); (9) mismatched_summary: total/power/ground/coverage INTEGER ==, "
        "min_width/max_space NUMERIC == (0.080 == 0.08 -> match NOT a mismatch); ABSENT fields NOT reported; empty "
        "list if no SUMMARY (naive uses string-equal so 0.080 != 0.08 -> false mismatch); (10) verdict priority: "
        "short>0->FAIL > open>0->REVIEW > mismatched/no-summary->INCOMPLETE > PASS (FAIL beats PASS even with "
        "matching summary -- naive puts INCOMPLETE above REVIEW or PASS above FAIL). Task "
        "layout_pgmesh_audit(report_text) -> flat dict (14 keys). runtime tcl/waveview (pure string + "
        "integer/float math, POSIX classes). WAVEVIEW BYPASS (same strategy as Aether-Layout-002..011): audits the "
        "textual PG-mesh work product on waveview tcl, making the largest class (layout_aether 14534) verifiable "
        "without the aether host. DISTINCT from -002 (placement/overlap), -003 (DRC violation-report), -004 (GDS "
        "layer-map usage), -005 (density-fill below-min), -006 (metal-fill target-meeting), -007 (antenna per-net "
        "max-ratio non-SKIP worst-net), -008 (per-(via,cut) enclosure AND-logic min-enclosure), -009 (per-net "
        "routing-completeness status + missing-via + single-segment watchlist), -010 (per-pair PG-short/leak "
        "resistance classification + mixed-type dual-count) and -011 (per-instance ECO change-order action+status "
        "dual-axis + delta-based status inference) -- this is a per-strap power-mesh audit (name-based power/ground "
        "classification independent of status + non-skip min-width/max-space with dictionary-numeric tie-break + "
        "coverage percentage + numeric-vs-integer summary reconciliation), a complementary angle on layout sign-off "
        "(power-delivery / PG mesh planning)."
    ),
    "tcr_refs": [
        "direction_and_status_case_insensitive_HORIZONTAL_horizontal_OK_Ok_SHORT_Short_all_match",
        "duplicate_name_layer_key_last_wins_replaces_direction_width_space_vias_status_not_sums_not_first_wins_counts_once",
        "ordered_key_layer_is_part_of_key_vdd1_M5_and_vdd1_M6_are_different_keys_both_counted_not_normalized",
        "status_absent_or_empty_default_ok_never_inferred_from_width_or_space",
        "missing_width_default_0_missing_space_default_0_missing_vias_default_1_missing_width_can_become_min_width",
        "min_width_max_space_worst_strap_over_non_skip_only_short_open_ok_included_skip_excluded_even_if_extreme_no_non_skip_minus_1_empty",
        "worst_strap_tie_break_lsort_dictionary_numeric_aware_strap2_lt_strap10_not_plain_lsort_increasing",
        "coverage_pct_round_power_plus_ground_times_100_div_total_total_0_to_0_from_name_classification_regardless_of_status",
        "mismatched_summary_int_for_counts_numeric_for_min_width_max_space_0.080_eq_0.08_match_absent_fields_not_reported_empty_list_if_no_summary",
        "verdict_priority_short_gt0_FAIL_gt_open_gt0_REVIEW_gt_mismatched_or_no_summary_INCOMPLETE_gt_PASS_FAIL_beats_PASS_with_matching_summary",
    ],
    "heavy": False,
    "wall_time_sec": 1.0,
    "status": "ready",
}

entry = {
    "task_id": "EDA-Eval-DesignFlow-Aether-Layout-012",
    "prompt": prompt,
    "entry_point": "layout_pgmesh_audit",
    "test": test,
    "metadata": metadata,
    "mode": "design_flow",
    "runtime": {"lang": "tcl", "host": "waveview"},
    "attachments": [],
    "budget": {"max_turns": 40, "wall_time_sec": 1800},
}

with open(jsonl_path, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

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
