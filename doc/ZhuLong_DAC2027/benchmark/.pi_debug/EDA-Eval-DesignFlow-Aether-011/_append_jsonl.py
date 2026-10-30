#!/usr/bin/env python3
"""Append Aether-Layout-011 (ECO audit) to the Aether-Layout jsonl."""
import json, pathlib

bench_dir = pathlib.Path("/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow")
jsonl_path = bench_dir / "EDA-Eval-DesignFlow-Aether-Layout.jsonl"
debug_dir = pathlib.Path("/nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Aether-011")

prompt = (debug_dir / "prompt.txt").read_text()
test = (debug_dir / "checker.tcl").read_text()

metadata = {
    "task_name": (
        "pyAether layout cellview ECO (Engineering Change Order) report audit: parse ECO/SUMMARY lines "
        "(ordered (action, inst_name) key, action add|delete|modify|swap case-insensitive, cell, status "
        "applied|pending|rejected|skipped case-insensitive, delta real), count distinct (action, inst_name) keys "
        "(last-wins dedup on duplicate key -- replace cell/status/delta not sum not first-wins; (action,inst) is "
        "ORDERED key: add-u1 and modify-u1 are DIFFERENT keys both counted not normalized), classify effective "
        "status (case-insensitive explicit; absent/empty -> infer from delta: >0 applied / ==0 skipped / <0 pending "
        "never unknown), count add/delete/modify/swap actions + applied/pending/rejected/skipped statuses, build "
        "cells_affected (union over ALL keys regardless of status, dedup lex-sorted, empty/absent cell NOT added), "
        "reconcile SUMMARY (total/add/delete/modify/swap/applied/pending/rejected/skipped all integer ==; absent "
        "fields not reported), emit single priority-ordered verdict (FAIL if rejected>0 > REVIEW if pending>0 > "
        "INCOMPLETE if mismatched or no-summary > PASS)"
    ),
    "direction": "layout_aether",
    "scenario": (
        "Layout/QA ECO turn: given a textual pyAether-emitted ECO (Engineering Change Order) report (ECO <action> "
        "<inst_name> cell=<C> status=<S> delta=<D> lines + a SUMMARY line), audit it before tape-out -- classify "
        "each ECO entry by action (add/delete/modify/swap) and status (applied/pending/rejected/skipped), infer "
        "status from delta when absent, count per-action and per-status totals, collect affected cells, reconcile "
        "the SUMMARY integer counts, and emit a fail/review/incomplete/pass verdict. Waveview-bypass for the aether "
        "host sandbox init timeout: this audits a layout WORK PRODUCT (textual ECO report) with pure string + "
        "integer/float math on waveview tcl, staying in the layout_aether category without needing the aether host."
    ),
    "layer": "L2",
    "topic": (
        "layout-eco-audit-action-case-insensitive-status-case-insensitive-last-wins-dedup-on-ordered-action-inst-key-"
        "replace-not-sum-action-is-part-of-key-add-u1-and-modify-u1-different-keys-status-absent-infer-delta-gt0-"
        "applied-eq0-skipped-lt0-pending-never-unknown-delta-eq0-skipped-inclusive-missing-delta-default-0-skipped-"
        "cells-affected-union-over-all-keys-regardless-of-status-dedup-lex-sorted-empty-cell-not-added-mismatched-"
        "summary-int-for-all-counts-absent-fields-not-reported-empty-list-if-no-summary-verdict-priority-rejected-gt0-"
        "FAIL-gt-pending-gt0-REVIEW-gt-mismatched-or-no-summary-INCOMPLETE-gt-PASS"
    ),
    "difficulty": "medium",
    "design": (
        "DERIVED (per 2026-10-29 ephemeral-session strategy: cline sessions cleared, fresh mining dead; aether host "
        "run_code init times out so layout_aether cannot be verified on the aether sandbox) from known real pyAether "
        "layout / ECO (Engineering Change Order) work patterns (layout_aether 14534 scan hits -- the LARGEST class; "
        "ECO / instance add/delete/modify/swap is a core late-stage layout change task). Real task: after a pyAether "
        "layout session, an ECO turn emits per-instance change records with the action (add/delete/modify/swap), the "
        "instance name, the cell/master, an explicit status (applied/pending/rejected/skipped), a delta magnitude, "
        "plus a SUMMARY header; the engineer must audit that report for ECO completeness (any rejected is a blocker, "
        "any pending needs review), count per-action and per-status totals, collect affected cells, reconcile the "
        "SUMMARY, and decide sign-off verdict. 10 real traps: (1) action CASE-INSENSITIVE ('add'/'ADD'/'Add' all "
        "match -- naive case-sensitive misses uppercase); (2) status CASE-INSENSITIVE ('applied'/'APPLIED'/'Applied' "
        "all match); (3) DUPLICATE (action, inst_name) key LAST-WINS (later ECO line replaces earlier cell/status/"
        "delta, not summed, not first-wins; counts once -- naive first-wins keeps a stale applied); (4) (action, "
        "inst_name) is an ORDERED key: 'add u1' and 'modify u1' are DIFFERENT keys, both counted -- action is part "
        "of the key (naive keys on inst_name only collapses them); (5) status ABSENT/EMPTY -> infer from delta: "
        ">0->applied, ==0->skipped, <0->pending (never unknown -- naive treats absent as skipped); (6) delta==0.0 "
        "-> skipped (inclusive); delta>0 -> applied; delta<0 -> pending (delta=0.001 applied, -0.001 pending -- "
        "naive uses sign-int only); (7) missing delta -> default 0.0 -> skipped (0.0==0.0 -- naive errors or defaults "
        "to applied); (8) cells_affected = UNION over ALL keys regardless of status, deduplicated, lex-sorted; "
        "empty/absent cell values NOT added (naive adds empty strings or only non-clean); (9) mismatched_summary: "
        "all nine count fields INTEGER ==; ABSENT fields NOT reported (not mismatched); empty list if no SUMMARY; "
        "(10) verdict priority: rejected>0->FAIL > pending>0->REVIEW > mismatched/no-summary->INCOMPLETE > PASS "
        "(REVIEW beats INCOMPLETE even with mismatched -- naive puts INCOMPLETE above REVIEW). Task "
        "layout_eco_audit(report_text) -> flat dict (12 keys). runtime tcl/waveview (pure string + integer/float "
        "math, POSIX classes). WAVEVIEW BYPASS (same strategy as Aether-Layout-002..010): audits the textual ECO "
        "work product on waveview tcl, making the largest class (layout_aether 14534) verifiable without the aether "
        "host. DISTINCT from -002 (placement/overlap), -003 (DRC violation-report), -004 (GDS layer-map usage), "
        "-005 (density-fill below-min), -006 (metal-fill target-meeting), -007 (antenna per-net max-ratio non-SKIP "
        "worst-net), -008 (per-(via,cut) enclosure AND-logic min-enclosure), -009 (per-net routing-completeness "
        "status + missing-via + single-segment watchlist) and -010 (per-pair PG-short/leak resistance classification "
        "+ mixed-type dual-count) -- this is a per-instance ECO change-order audit (action+status dual-axis counting "
        "+ delta-based status inference + ordered (action,inst) key + cells-affected union), a complementary angle "
        "on layout sign-off (ECO / late-stage change management)."
    ),
    "tcr_refs": [
        "action_case_insensitive_add_ADD_Add_all_match",
        "status_case_insensitive_applied_APPLIED_Applied_all_match",
        "duplicate_action_inst_name_key_last_wins_replaces_cell_status_delta_not_sums_not_first_wins_counts_once",
        "ordered_key_action_is_part_of_key_add_u1_and_modify_u1_are_different_keys_both_counted_not_normalized",
        "status_absent_or_empty_infer_from_delta_gt0_applied_eq0_skipped_lt0_pending_never_unknown",
        "delta_boundary_delta_eq0_skipped_inclusive_delta_gt0_applied_delta_lt0_pending",
        "missing_delta_default_0_skipped_0_eq_0",
        "cells_affected_union_over_all_keys_regardless_of_status_dedup_lex_sorted_empty_cell_not_added",
        "mismatched_summary_int_for_all_count_fields_absent_fields_not_reported_empty_list_if_no_summary",
        "verdict_priority_rejected_gt0_FAIL_gt_pending_gt0_REVIEW_gt_mismatched_or_no_summary_INCOMPLETE_gt_PASS",
    ],
    "heavy": False,
    "wall_time_sec": 1.0,
    "status": "ready",
}

entry = {
    "task_id": "EDA-Eval-DesignFlow-Aether-Layout-011",
    "prompt": prompt,
    "entry_point": "layout_eco_audit",
    "test": test,
    "metadata": metadata,
    "mode": "design_flow",
    "runtime": {"lang": "tcl", "host": "waveview"},
    "attachments": [],
    "budget": {"max_turns": 40, "wall_time_sec": 1800},
}

json.dumps(entry)

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
