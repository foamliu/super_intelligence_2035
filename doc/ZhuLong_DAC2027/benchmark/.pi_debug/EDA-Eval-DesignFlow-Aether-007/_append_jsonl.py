#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-Aether-Layout-007 to the Aether-Layout jsonl."""
import json, pathlib

ROOT = pathlib.Path("/nasdata/app.e0031982/code/EDA-Flow-Bench")
JSONL = ROOT / "benchmarks/EDA-Eval-DesignFlow/Aether-Layout.jsonl"
JSONL = ROOT / "benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow-Aether-Layout.jsonl"
DBG = ROOT / "agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Aether-007"

prompt = (DBG / "prompt.txt").read_text()
checker = (DBG / "checker.tcl").read_text()

task_id = "EDA-Eval-DesignFlow-Aether-Layout-007"
entry_point = "layout_antenna_audit"

metadata = {
    "task_name": (
        "pyAether layout cellview antenna-rule-check report audit: parse NET/SUMMARY lines "
        "(net/layer pair, ratio/limit floats, status PASS|WARN|FAIL|SKIP, gate_area/diode_area "
        "red herrings), count distinct nets and distinct (net,layer) pairs (last-wins dedup on "
        "duplicate pair -- replace not sum/first-wins), classify effective status "
        "(case-insensitive explicit; absent -> infer FAIL if ratio>limit else PASS, never WARN/SKIP), "
        "ratio==limit is PASS (inclusive; FAIL only strict >), missing limit -> default 400.0, "
        "missing ratio -> default 0.0, count pass/warn/fail/skip over dedup'd pairs (warn only "
        "explicit), compute max_ratio + worst_net over NON-SKIP lines only (SKIP excluded even if "
        "its ratio is the file max; no non-SKIP -> max_ratio=-1.0 worst_net=''), worst_net tie at "
        "max_ratio -> lexicographically smallest net name, reconcile SUMMARY nets_checked/violations/"
        "warns/skipped as int + max_ratio NUMERICALLY (100.0 == 100, NOT string equal) + worst_net as "
        "string, absent SUMMARY fields NOT reported, empty list if no SUMMARY, emit single "
        "priority-ordered verdict (FAIL if fail_count>0 > INCOMPLETE if mismatched_summary non-empty "
        "OR no summary > PASS)"
    ),
    "direction": "layout_aether",
    "scenario": (
        "Layout/QA sign-off: given a textual pyAether-emitted antenna-rule-check report (NET <name> "
        "layer=<L> ratio=<float> limit=<float> status=<S> lines + a SUMMARY line), audit it before "
        "tape-out -- classify each (net,layer) check by status, count violations, find the worst "
        "antenna ratio net (excluding skipped checks), reconcile the SUMMARY header NUMERICALLY, and "
        "emit a pass/incomplete/fail verdict. Waveview-bypass for the aether host sandbox init "
        "timeout: this audits a layout WORK PRODUCT (textual antenna-check report) with pure string + "
        "float/integer math on waveview tcl, staying in the layout_aether category without needing "
        "the aether host."
    ),
    "layer": "L2",
    "topic": (
        "layout-antenna-audit-status-case-insensitive-last-wins-dedup-on-net-layer-pair-"
        "status-absent-infer-FAIL-if-ratio-gt-limit-else-PASS-never-WARN-SKIP-ratio-equals-limit-"
        "PASS-inclusive-FAIL-strict-gt-missing-limit-default-400-missing-ratio-default-0-PASS-"
        "max-ratio-worst-net-over-non-SKIP-only-SKIP-excluded-even-if-file-max-no-non-SKIP-"
        "minus-1-empty-worst-net-tie-lex-smallest-net-summary-numeric-equality-100.0-equals-100-"
        "absent-fields-not-reported-priority-verdict-fail-gt-incomplete-gt-pass"
    ),
    "difficulty": "medium",
    "design": (
        "DERIVED (per 2026-10-29 ephemeral-session strategy: cline sessions cleared, fresh mining "
        "dead; aether host run_code init times out so layout_aether cannot be verified on the aether "
        "sandbox) from known real pyAether layout / antenna-check work patterns (layout_aether 14534 "
        "scan hits -- the LARGEST class; calibre 12664 scan hits for DRC/antenna sign-off). Real task: "
        "after a pyAether antenna-check session, the tool emits a per-(net,layer) report with the "
        "computed antenna ratio, the antenna limit, an explicit status (PASS/WARN/FAIL/SKIP), and "
        "gate/diode areas, plus a SUMMARY header; the engineer must audit that report for antenna "
        "compliance (any FAIL is a sign-off blocker), identify skipped checks, find the worst antenna "
        "ratio net, reconcile the SUMMARY, and decide sign-off verdict. 10 real traps: "
        "(1) status CASE-INSENSITIVE ('fail'/'FAIL'/'Fail' all match -- naive case-sensitive misses "
        "lowercase status); "
        "(2) DUPLICATE (net,layer) pair LAST-WINS (later NET line replaces earlier ratio/limit/status, "
        "not summed, not first-wins; counts ONCE in total_lines -- naive first-wins keeps a stale FAIL); "
        "(3) status ABSENT -> infer from ratio vs limit: FAIL if ratio>limit else PASS (never WARN/SKIP "
        "-- naive treats absent status as PASS always or as SKIP); "
        "(4) ratio == limit -> PASS inclusive (FAIL only strict > -- naive >= misclassifies the "
        "boundary as a violation); "
        "(5) missing limit= -> default 400.0 (naive uses 0.0 -> everything FAILs); "
        "(6) missing ratio= -> default 0.0 (always PASS -- naive excludes the line from max_ratio); "
        "(7) max_ratio/worst_net over NON-SKIP lines ONLY (SKIP excluded even if its ratio is the file "
        "max -- naive takes max over ALL lines and reports the SKIP net as worst); "
        "(8) worst_net tie at max_ratio -> lexicographically SMALLEST net name (lsort -dictionary -- "
        "naive first-seen returns the wrong net on tie); "
        "(9) mismatched_summary: max_ratio compared NUMERICALLY (expr ==, so '100.0' matches computed "
        "100; naive string equal false-mismatches); nets_checked/violations/warns/skipped compared as "
        "int; worst_net compared as string; absent SUMMARY fields NOT reported (naive reports absent "
        "fields); empty list if no SUMMARY; "
        "(10) verdict priority fail_count>0 FAIL (TOP) > mismatched_summary non-empty OR no-summary "
        "INCOMPLETE > PASS (naive ignores mismatched_summary and returns PASS when only the SUMMARY is "
        "wrong). gate_area/diode_area are red herrings not used in any output key. All output lists "
        "lexicographically sorted (lsort -dictionary). Task layout_antenna_audit(report_text) -> flat "
        "dict (10 keys). runtime tcl/waveview (pure string + float/integer math, POSIX classes). "
        "WAVEVIEW BYPASS (same strategy as Aether-Layout-002/003/004/005/006): audits the textual "
        "antenna-check work product on waveview tcl, making the largest class (layout_aether 14534) "
        "verifiable without the aether host. DISTINCT from -002 (placement/overlap), -003 (DRC "
        "violation-report), -004 (GDS layer-map usage), -005 (percent below-min DRC compliance), and "
        "-006 (metal-fill target-meeting + zero-fill-on-met) -- this is a per-(net,layer) antenna "
        "ratio/limit/status classification + non-SKIP worst-net + numeric SUMMARY reconciliation audit, "
        "a complementary angle on layout sign-off (antenna compliance + skip-exclusion + numeric "
        "summary reconciliation)."
    ),
    "tcr_refs": [
        "status_case_insensitive_fail_fail_fail_all_match",
        "duplicate_net_layer_pair_last_wins_replaces_not_sums_not_first_wins_counts_once",
        "status_absent_infer_FAIL_if_ratio_gt_limit_else_PASS_never_WARN_or_SKIP",
        "ratio_equals_limit_is_PASS_inclusive_FAIL_only_strict_gt",
        "missing_limit_defaults_to_400.0_not_0",
        "missing_ratio_defaults_to_0.0_always_PASS_not_excluded_from_max",
        "max_ratio_worst_net_over_non_SKIP_only_SKIP_excluded_even_if_file_max_no_non_SKIP_minus_1_empty",
        "worst_net_tie_at_max_ratio_lexicographically_smallest_net_name_wins",
        "mismatched_summary_max_ratio_numeric_equality_100.0_equals_100_int_for_counts_string_for_worst_net_absent_fields_not_reported",
        "verdict_priority_fail_count_gt_0_FAIL_gt_mismatched_or_no_summary_INCOMPLETE_gt_PASS"
    ],
    "heavy": False,
    "wall_time_sec": 1.0,
    "status": "ready",
}

record = {
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

with JSONL.open("a") as f:
    f.write(json.dumps(record, ensure_ascii=False) + "\n")

# report
n = sum(1 for _ in JSONL.open())
print(f"appended {task_id} -> {JSONL}")
print(f"jsonl now has {n} cases")
