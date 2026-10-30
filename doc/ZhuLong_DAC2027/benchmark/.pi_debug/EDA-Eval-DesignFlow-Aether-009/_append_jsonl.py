#!/usr/bin/env python3
"""Append Aether-Layout-009 (routing-connectivity audit) to the Aether-Layout jsonl."""
import json, pathlib

HERE = pathlib.Path(__file__).parent
BENCH = pathlib.Path("/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow")
JSONL = BENCH / "EDA-Eval-DesignFlow-Aether-Layout.jsonl"

prompt = (HERE / "prompt.txt").read_text()
checker = (HERE / "checker.tcl").read_text()

task_id = "EDA-Eval-DesignFlow-Aether-Layout-009"
entry_point = "layout_routing_audit"

metadata = {
    "task_name": (
        "pyAether layout cellview routing-connectivity / open-net report audit: parse NET/SUMMARY lines "
        "(net name, segments int, vias int, comma-separated layers, status routed|partial|unrouted|skipped), "
        "count distinct nets (last-wins dedup on duplicate net name -- replace segments/vias/layers/status not sum not first-wins), "
        "classify effective status (case-insensitive explicit; absent -> infer 0=UNROUTED / 1=PARTIAL / >=2=ROUTED never SKIPPED), "
        "build single_segment_nets watchlist (segments==1 regardless of status), build missing_via_nets (layer_count>=2 AND vias==0; single-layer 0-via fine), "
        "compute max_segments + max_segment_net over NON-SKIP nets only (SKIP excluded even if file max; no non-skip -> -1/empty; tie -> lex smallest net lsort -dictionary numeric-aware), "
        "layers_used = union over all nets lex-sorted dedup, reconcile SUMMARY (nets_checked/routed/unrouted/missing_vias int, max_segments numeric, max_segment_net string; absent fields not reported), "
        "emit single priority-ordered verdict (FAIL if unrouted>0 OR missing_via non-empty > INCOMPLETE if mismatched or no-summary > PASS; partial/single_segment are watchlists NOT FAIL triggers)"
    ),
    "direction": "layout_aether",
    "scenario": (
        "Layout/QA sign-off: given a textual pyAether-emitted routing-connectivity report (NET <name> segments=<N> vias=<N> layers=<L1,L2,...> status=<S> lines + a SUMMARY line), "
        "audit it before tape-out -- classify each net by routing status, flag single-segment (possibly dangling) nets, flag multi-layer nets missing vias (layer change requires a via), "
        "find the max-segment net excluding skipped checks, reconcile the SUMMARY numerically, and emit a pass/incomplete/fail verdict. "
        "Waveview-bypass for the aether host sandbox init timeout: this audits a layout WORK PRODUCT (textual routing report) with pure string + integer math on waveview tcl, "
        "staying in the layout_aether category without needing the aether host."
    ),
    "layer": "L2",
    "topic": (
        "layout-routing-audit-status-case-insensitive-last-wins-dedup-on-net-name-status-absent-infer-from-segments-0-unrouted-1-partial-ge2-routed-never-skipped-"
        "missing-via-layer-count-ge2-and-vias-eq0-single-layer-0-via-fine-layers-dedup-empty-handling-M1-M2-M1-to-2-layers-layers-empty-to-0-"
        "single-segment-watchlist-segments-eq1-regardless-of-status-not-a-fail-trigger-max-segments-max-segment-net-over-non-skip-only-skip-excluded-no-non-skip-minus-1-empty-"
        "max-segment-net-tie-lex-smallest-net-dictionary-numeric-aware-via2-lt-via10-layers-used-union-over-all-nets-lex-sorted-"
        "mismatched-summary-int-equality-for-counts-numeric-for-max-segments-string-for-max-segment-net-absent-fields-not-reported-"
        "verdict-priority-unrouted-gt0-OR-missing-via-nonempty-FAIL-gt-mismatched-or-no-summary-INCOMPLETE-gt-PASS-partial-and-single-segment-are-watchlists-not-fail-triggers"
    ),
    "difficulty": "medium",
    "design": (
        "DERIVED (per 2026-10-29 ephemeral-session strategy: cline sessions cleared, fresh mining dead; aether host run_code init times out so layout_aether cannot be verified on the aether sandbox) "
        "from known real pyAether layout / routing-connectivity sign-off work patterns (layout_aether 14534 scan hits -- the LARGEST class; cellview 9389 / dbGet 2597 scan hits for net/instance connectivity; "
        "routing completion / open-net / missing-via checks are core pyAether layout sign-off tasks). Real task: after a pyAether routing session, the tool emits a per-net routing report with the segment count, "
        "via count, the list of layers the net traverses, an explicit routing status (routed/partial/unrouted/skipped), plus a SUMMARY header; the engineer must audit that report for routing completeness "
        "(any unrouted net or any multi-layer net with zero vias is a sign-off blocker), identify single-segment (possibly dangling) nets as a watchlist, find the max-segment net excluding skipped checks, "
        "reconcile the SUMMARY, and decide sign-off verdict. 10 real traps: (1) status CASE-INSENSITIVE ('routed'/'ROUTED'/'Routed' all match -- naive case-sensitive misses lowercase status); "
        "(2) DUPLICATE net name LAST-WINS (later NET line replaces earlier segments/vias/layers/status, not summed, not first-wins; counts once -- naive first-wins keeps a stale unrouted); "
        "(3) status ABSENT -> infer from segments: 0->UNROUTED, 1->PARTIAL, >=2->ROUTED (never SKIPPED -- naive treats absent as always ROUTED); "
        "(4) missing_via = layer_count>=2 AND vias==0 (a net spanning multiple layers needs a via; a single-layer net with 0 vias is FINE -- naive flags all 0-via nets or ignores layer count); "
        "(5) layers list dedup + empty handling ('M1,M2,M1'->2 distinct; 'layers=' empty -> 0 layers; layers_used is the union over ALL nets -- naive counts raw comma-split with dups or treats empty string as a layer); "
        "(6) single_segment_nets = segments==1 REGARDLESS of status (a watchlist; a net with status=routed but segments==1 is STILL listed and is NOT a FAIL trigger -- naive only lists when status=partial and wrongly FAILs on it); "
        "(7) max_segments/max_segment_net over NON-SKIP nets ONLY (SKIP excluded even if its segment count is the file max; no non-skip -> -1/empty -- naive takes max over ALL incl SKIP); "
        "(8) max_segment_net tie at max_segments -> lexicographically SMALLEST net name (lsort -dictionary numeric-aware so 'via2' < 'via10' -- naive ASCII string compare returns 'via10' on the tie); "
        "(9) mismatched_summary: nets_checked/routed/unrouted/missing_vias INTEGER equality; max_segments NUMERIC equality (expr ==); max_segment_net STRING equality; ABSENT SUMMARY fields NOT reported (naive reports absent fields); empty list if no SUMMARY; "
        "(10) verdict priority: unrouted>0 OR missing_via non-empty -> FAIL (TOP) > mismatched non-empty OR no-summary -> INCOMPLETE > PASS (partial_count and single_segment are watchlists NOT FAIL triggers -- naive treats them as blockers). "
        "Task layout_routing_audit(routing_text) -> flat dict (12 keys). runtime tcl/waveview (pure string + integer math, POSIX classes). "
        "WAVEVIEW BYPASS (same strategy as Aether-Layout-002/003/004/005/006/007/008): audits the textual routing work product on waveview tcl, making the largest class (layout_aether 14534) verifiable without the aether host. "
        "DISTINCT from -002 (placement/overlap), -003 (DRC violation-report), -004 (GDS layer-map usage), -005 (density-fill below-min), -006 (metal-fill target-meeting), -007 (antenna per-net max-ratio non-SKIP worst-net) and -008 (per-(via,cut) enclosure AND-logic min-enclosure) -- "
        "this is a per-net routing-completeness audit (status classification by segments + missing-via-on-layer-change + single-segment watchlist + non-SKIP max-segment-net), a complementary angle on layout sign-off (routing connectivity / open-net / missing-via compliance)."
    ),
    "tcr_refs": [
        "status_case_insensitive_routed_ROUTED_Routed_all_match",
        "duplicate_net_name_last_wins_replaces_segments_vias_layers_status_not_sums_not_first_wins_counts_once",
        "status_absent_infer_from_segments_0_UNROUTED_1_PARTIAL_ge2_ROUTED_never_SKIPPED",
        "missing_via_layer_count_ge2_AND_vias_eq0_single_layer_0_via_is_fine_not_listed",
        "layers_list_dedup_M1_M2_M1_to_2_distinct_layers_empty_to_0_layers_used_union_over_all_nets",
        "single_segment_nets_segments_eq1_regardless_of_status_watchlist_not_a_fail_trigger",
        "max_segments_max_segment_net_over_non_SKIP_only_SKIP_excluded_even_if_file_max_no_non_skip_minus_1_empty",
        "max_segment_net_tie_at_max_segments_lexicographically_smallest_net_dictionary_numeric_aware_via2_lt_via10",
        "mismatched_summary_int_equality_for_counts_numeric_for_max_segments_string_for_max_segment_net_absent_fields_not_reported_empty_if_no_summary",
        "verdict_priority_unrouted_gt0_OR_missing_via_nonempty_FAIL_gt_mismatched_or_no_summary_INCOMPLETE_gt_PASS_partial_and_single_segment_are_watchlists_not_fail_triggers",
    ],
    "heavy": False,
    "wall_time_sec": 1.0,
    "status": "ready",
}

entry = {
    "task_id": task_id,
    "prompt": prompt,
    "entry_point": entry_point,
    "test": checker,
    "metadata": metadata,
    "mode": "design_flow",
    "runtime": {"lang": "tcl", "host": "waveview"},
    "attachments": [],
    "budget": {"max_turns": 40, "wall_time_sec": 1800},
}

# append
with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended", task_id, "to", JSONL)
# verify
with open(JSONL) as f:
    n = sum(1 for _ in f)
print("jsonl now has", n, "lines")
