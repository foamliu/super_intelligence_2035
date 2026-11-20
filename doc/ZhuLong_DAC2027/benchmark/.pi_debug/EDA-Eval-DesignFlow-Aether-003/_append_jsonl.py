#!/usr/bin/env python3
import json, pathlib

bench = pathlib.Path("/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow")
jsonl = bench / "EDA-Eval-DesignFlow-Aether-Layout.jsonl"
dbg = pathlib.Path("/nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Aether-003")

prompt = (dbg / "prompt.txt").read_text()
test = (dbg / "checker.tcl").read_text()

entry = {
    "task_id": "EDA-Eval-DesignFlow-Aether-Layout-003",
    "mode": "design_flow",
    "status": "ready",
    "prompt": prompt,
    "entry_point": "layout_drc_audit",
    "attachments": [],
    "test": test,
    "budget": {"max_turns": 40, "wall_time_sec": 1800},
    "runtime": {"lang": "tcl", "host": "waveview"},
    "metadata": {
        "task_name": "pyAether layout cellview DRC violation-report audit: parse RULE/SUMMARY lines, count distinct rules (last-wins dedup on duplicate rule names), sum violations, separate error vs warning counts (severity CASE-INSENSITIVE), count checked rules (zero-count rules still checked), per-layer error dict (err layers only, sorted), detect SUMMARY-vs-computed mismatched fields (absent fields not reported), layers_used sorted, emit single priority-ordered verdict (FAIL>WARN>INCOMPLETE>PASS where INCOMPLETE = no SUMMARY line)",
        "direction": "layout_aether",
        "scenario": "Layout/QA sign-off: given a textual pyAether-emitted DRC violation report (RULE <name> layer=<> count=<> severity=<err|warn> lines + a SUMMARY line), audit it for correctness before tape-out -- aggregate violations by rule/layer, verify the SUMMARY header is internally consistent with the rule list (flag mismatched fields), and emit a pass/warn/fail/incomplete verdict. Waveview-bypass for the aether host sandbox init timeout: this audits a layout WORK PRODUCT (textual DRC report) with pure string + integer math on waveview tcl, staying in the layout_aether category without needing the aether host.",
        "layer": "L2",
        "topic": "layout-drc-report-audit-severity-case-insensitive-last-wins-dedup-zero-count-still-checked-summary-reconciliation-priority-verdict-incomplete-when-no-summary",
        "difficulty": "medium",
        "design": "DERIVED (per 2026-10-29 ephemeral-session strategy: cline sessions cleared, fresh mining dead; aether host run_code init times out so layout_aether cannot be verified on the aether sandbox) from known real pyAether/physical-verify work patterns (layout_aether 14534 scan hits -- the LARGEST class; calibre 12664 / physical_verify 1295 scan hits for DRC-style reporting). Real task: after a pyAether layout session runs DRC, the tool emits a per-rule violation report with a SUMMARY header; the engineer must audit that report for consistency (does SUMMARY match the rule list?) and decide sign-off verdict. 10 real traps: (1) severity CASE-INSENSITIVE (ERR/Err/err all errors -- naive exact-match miscounts); (2) DUPLICATE rule names LAST-WINS (later RULE line replaces earlier count/layer/severity, not summed, not first-wins); (3) duplicate_rule_names still REPORTS names seen >1 time (sorted, dedup) even though only last value is kept; (4) ZERO-count rules still count toward checked_rules (naive skips them); (5) missing SUMMARY -> verdict INCOMPLETE (NOT PASS) and mismatched_summary empty; (6) per_layer_errors ONLY err layers, sorted, warn excluded; (7) mismatched_summary compares computed vs SUMMARY per-field, absent fields NOT reported as mismatched; (8) verdict priority error>0 FAIL > warning>0 WARN > no-summary INCOMPLETE > PASS; (9) layers_used sorted, includes err AND warn layers, dedup; (10) all output lists lexicographically sorted (lsort -dictionary). Task layout_drc_audit(drc_text) -> flat dict (10 keys). runtime tcl/waveview (pure string + integer math, POSIX classes). WAVEVIEW BYPASS (same strategy as Aether-Layout-002): audits the textual DRC work product on waveview tcl, making the largest class (layout_aether 14534) verifiable without the aether host. DISTINCT from Aether-Layout-002 (placement/overlap audit) -- this is a DRC violation-report aggregation + SUMMARY-reconciliation audit.",
        "tcr_refs": [
            "severity_case_insensitive_err_err_err_all_errors",
            "duplicate_rule_names_last_wins_replaces_not_sums_not_first_wins",
            "duplicate_rule_names_still_reports_names_seen_more_than_once_sorted_dedup",
            "zero_count_rules_still_count_toward_checked_rules_do_not_skip",
            "missing_summary_verdict_incomplete_not_pass_mismatched_summary_empty",
            "per_layer_errors_only_err_layers_sorted_warn_excluded",
            "mismatched_summary_compares_computed_vs_summary_per_field_absent_fields_not_reported",
            "verdict_priority_error_fail_warning_warn_no_summary_incomplete_pass",
            "layers_used_sorted_includes_err_and_warn_layers_dedup",
            "all_output_lists_lexicographically_sorted_lsort_dictionary"
        ],
        "heavy": False,
        "wall_time_sec": 1.0,
        "status": "ready"
    }
}

with open(jsonl, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended", entry["task_id"], "to", jsonl)
# verify
n = sum(1 for _ in open(jsonl))
print("Aether-Layout jsonl now has", n, "entries")
