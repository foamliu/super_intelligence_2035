#!/usr/bin/env python3
import json, pathlib

JPATH = pathlib.Path("/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow-Aether-Layout.jsonl")
PROMPT = pathlib.Path("/nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Aether-006/prompt.txt").read_text()
TEST = pathlib.Path("/nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Aether-006/checker.tcl").read_text()

entry = {
    "task_id": "EDA-Eval-DesignFlow-Aether-Layout-006",
    "prompt": PROMPT,
    "entry_point": "layout_metalfill_target_audit",
    "test": TEST,
    "metadata": {
        "task_name": "pyAether layout cellview metal-fill target-meeting audit: parse LAYER/SUMMARY lines (target/actual density floats + fill_count int), count distinct layers (last-wins dedup on duplicate layer names), sum fill_count (missing fill_count= -> 0), classify underfill (strict <) vs met (actual >= target inclusive) vs missing_target (no target= field -- excluded from underfill AND met), flag zero_fill_met (met layers whose fill_count == 0, including missing fill_count= defaulted to 0), compute min/max density layer over ALL distinct layers using actual default 0.0 when absent (lex-smallest tie-break), reconcile SUMMARY min/max density NUMERICALLY (72.30 == 72.3 -- NOT string equality) and total_layers/total_fill as int, absent SUMMARY fields NOT reported, empty if no SUMMARY; empty report -> any provided min/max mismatched but total_layers=total_fill=0 must match, emit single priority-ordered verdict (FAIL for underfill > INCOMPLETE for missing_target or no-summary > PASS; mismatched_summary does NOT affect verdict)",
        "direction": "layout_aether",
        "scenario": "Layout/QA sign-off: given a textual pyAether-emitted metal-fill target-meeting report (LAYER <name> target=<float> actual=<float> fill_count=<N> lines + a SUMMARY line), audit it before tape-out -- check each metal layer's actual fill density against its target requirement, find layers that cannot be assessed (missing target), flag met layers with ZERO fill (a compliance red flag -- target met but no fill shapes inserted, suspicious), aggregate total fill shapes, reconcile the SUMMARY header NUMERICALLY, and emit a pass/incomplete/fail verdict. Waveview-bypass for the aether host sandbox init timeout: this audits a layout WORK PRODUCT (textual metal-fill target-meeting report) with pure string + float/integer math on waveview tcl, staying in the layout_aether category without needing the aether host.",
        "layer": "L2",
        "topic": "layout-metalfill-target-audit-strict-lt-underfill-met-inclusive-missing-target-excluded-from-buckets-zero-fill-on-met-includes-missing-fill-count-defaulted-0-actual-default-0.0-when-absent-min-max-density-lex-smallest-tie-break-summary-numeric-equality-72.30-equals-72.3-absent-fields-not-reported-priority-verdict",
        "difficulty": "medium",
        "design": "DERIVED (per 2026-10-29 ephemeral-session strategy: cline sessions cleared, fresh mining dead; aether host run_code init times out so layout_aether cannot be verified on the aether sandbox) from known real pyAether layout / metal-fill work patterns (layout_aether 14534 scan hits -- the LARGEST class; calibre 12664 / hspice 10757 scan hits for density sign-off). Real task: after a pyAether metal-fill session, the tool emits a per-layer fill-target report with target/actual density (floats, no percent suffix) and a fill-shape count plus a SUMMARY header; the engineer must audit that report for fill-target correctness (any layer strictly below its target is a fill FAIL), identify layers that cannot be assessed (missing target), flag met layers suspiciously having ZERO fill shapes, and decide sign-off verdict. 10 real traps: (1) DUPLICATE layer NAMES LAST-WINS (later LAYER line replaces earlier target/actual/fill_count, not summed, not first-wins); (2) total_fill sums LAST-WINS distinct fill_count (missing fill_count= -> 0), NOT all input LAYER lines (naive sums all -> wrong); (3) missing actual= -> actual defaults to 0.0 (layer still counts for total_layers and min/max; 0.0 used for underfill compare -- naive skips the layer entirely, getting min/max and underfill wrong); (4) underfill is STRICT < (actual == target is MET, NOT below -- naive <= misclassifies the boundary as a violation); (5) missing target= -> layer goes to missing_target_layers, NOT underfill, NOT met (naive puts it in met or underfill); (6) met = actual >= target INCLUSIVE; zero_fill_met = met layers whose fill_count == 0, INCLUDING layers with missing fill_count= (defaulted to 0 -- naive treats missing fill_count as '' and never flags); (7) min/max density tie -> lexicographically SMALLEST name wins (lsort -dictionary -- naive first-seen returns wrong name on tie); (8) mismatched_summary: min_density/max_density compared NUMERICALLY (expr ==, so '72.30' matches computed '72.3'; naive string equal false-mismatches); total_layers/total_fill compared as int; absent SUMMARY fields NOT reported (naive trusts SUMMARY or reports absent fields); empty if no SUMMARY; if no layers, any provided min/max is mismatched but total_layers=total_fill=0 must match or also be reported; (9) verdict priority underfill non-empty FAIL (TOP) > missing_target non-empty OR no-summary INCOMPLETE > PASS; mismatched_summary does NOT affect verdict (naive may reverse priority or let mismatch flip verdict); (10) all output lists lexicographically sorted (lsort -dictionary). Task layout_metalfill_target_audit(report_text) -> flat dict (10 keys). runtime tcl/waveview (pure string + float/integer math, POSIX classes). WAVEVIEW BYPASS (same strategy as Aether-Layout-002/003/004/005): audits the textual metal-fill target-meeting work product on waveview tcl, making the largest class (layout_aether 14534) verifiable without the aether host. DISTINCT from Aether-Layout-002 (placement/overlap audit), -003 (DRC violation-report audit), -004 (GDS layer-map usage audit), and -005 (percent-based below-min DRC compliance with min_density=%/target_density=%/actual_density=%/fill_shapes=N) -- this is a target/actual float + fill_count int 'did we meet the fill target / zero-fill-on-met' audit, a complementary angle on metal-fill sign-off (target-meeting + zero-fill red flag + numeric SUMMARY reconciliation, vs -005's percent-strip below-min DRC compliance).",
        "tcr_refs": [
            "duplicate_layer_names_last_wins_replaces_not_sums_not_first_wins",
            "total_fill_sums_last_wins_distinct_fill_count_missing_defaults_0_not_all_input_lines",
            "missing_actual_defaults_to_0.0_layer_still_counts_for_total_layers_and_min_max",
            "underfill_strict_lt_actual_equals_target_is_met_not_below",
            "missing_target_layer_goes_to_missing_target_layers_not_underfill_not_met",
            "met_actual_ge_target_inclusive_zero_fill_met_includes_missing_fill_count_defaulted_0",
            "min_max_density_tie_break_lexicographically_smallest_name_wins",
            "mismatched_summary_min_max_density_numeric_equality_72.30_equals_72.3_not_string_equal_absent_fields_not_reported",
            "verdict_priority_underfill_fail_top_gt_missing_target_or_no_summary_incomplete_gt_pass_mismatched_no_effect",
            "all_output_lists_lexicographically_sorted_lsort_dictionary"
        ],
        "heavy": False,
        "wall_time_sec": 1.0,
        "status": "ready"
    },
    "mode": "design_flow",
    "runtime": {"lang": "tcl", "host": "waveview"},
    "attachments": [],
    "budget": {"max_turns": 40, "wall_time_sec": 1800},
    "status": "ready"
}

# append only if not already present
existing = [json.loads(l) for l in JPATH.read_text().splitlines() if l.strip()]
if any(e["task_id"] == entry["task_id"] for e in existing):
    print("already present, skipping append")
else:
    with open(JPATH, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print("appended", entry["task_id"])
print("total lines now:", len([l for l in JPATH.read_text().splitlines() if l.strip()]))
