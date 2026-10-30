#!/usr/bin/env python3
import json, pathlib

BENCH = pathlib.Path("/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow-Aether-Layout.jsonl")
D = pathlib.Path("/nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Aether-008")

prompt = (D / "prompt.txt").read_text()
test = (D / "checker.tcl").read_text()

entry = {
    "task_id": "EDA-Eval-DesignFlow-Aether-Layout-008",
    "prompt": prompt,
    "entry_point": "layout_via_enclosure_audit",
    "test": test,
    "metadata": {
        "task_name": "pyAether layout cellview via-enclosure compliance report audit: parse VIA/SUMMARY lines (via name + cut layer dedup pair, enc_bot/enc_top floats, req minimum-enclosure float, bottom/top/count red herrings), count distinct via types and distinct (name,cut) pairs (last-wins dedup on duplicate pair -- replace not sum/first-wins), classify effective status (case-insensitive explicit; absent -> infer FAIL if enc_bot<req OR enc_top<req else PASS, never WARN/SKIP), enc==req is PASS (inclusive; FAIL only strict <), missing req -> default 0.0, missing enc_bot/enc_top -> default 0.0 (can FAIL if req>0 and included in min), count pass/warn/fail/skip over dedup'd pairs (warn only explicit), compute min_enclosure + worst_via over NON-SKIP lines only (SKIP excluded even if its enclosure is the file min; line enclosure = min(enc_bot,enc_top); no non-SKIP -> min_enclosure=-1.0 worst_via=''), worst_via tie at min_enclosure -> lexicographically smallest via name (lsort -dictionary, numeric-aware so via2<via10), reconcile SUMMARY vias_checked/violations/warns/skipped as int + min_enclosure NUMERICALLY (0.080 == 0.08, NOT string equal) + worst_via as string, absent SUMMARY fields NOT reported, empty list if no SUMMARY, emit single priority-ordered verdict (FAIL if fail_count>0 > INCOMPLETE if mismatched_summary non-empty OR no summary > PASS)",
        "direction": "layout_aether",
        "scenario": "Layout/QA sign-off: given a textual pyAether-emitted via-enclosure compliance report (VIA <name> cut=<L> enc_bot=<float> enc_top=<float> req=<float> status=<S> lines + a SUMMARY line), audit it before tape-out -- classify each (name,cut) via by status, count violations, find the worst (minimum-enclosure) via excluding skipped checks, reconcile the SUMMARY header NUMERICALLY, and emit a pass/incomplete/fail verdict. Waveview-bypass for the aether host sandbox init timeout: this audits a layout WORK PRODUCT (textual via-enclosure report) with pure string + float/integer math on waveview tcl, staying in the layout_aether category without needing the aether host.",
        "layer": "L2",
        "topic": "layout-via-enclosure-audit-status-case-insensitive-last-wins-dedup-on-name-cut-pair-status-absent-infer-FAIL-if-enc-bot-lt-req-OR-enc-top-lt-req-else-PASS-never-WARN-SKIP-enc-equals-req-PASS-inclusive-FAIL-strict-lt-missing-req-default-0-missing-enc-bot-enc-top-default-0-can-FAIL-if-req-gt-0-included-in-min-min-enclosure-worst-via-over-non-SKIP-only-line-enclosure-min-enc-bot-enc-top-SKIP-excluded-even-if-file-min-no-non-SKIP-minus-1-empty-worst-via-tie-lex-smallest-via-dictionary-numeric-aware-via2-lt-via10-summary-numeric-equality-0.080-equals-0.08-absent-fields-not-reported-priority-verdict-fail-gt-incomplete-gt-pass",
        "difficulty": "medium",
        "design": "DERIVED (per 2026-10-29 ephemeral-session strategy: cline sessions cleared, fresh mining dead; aether host run_code init times out so layout_aether cannot be verified on the aether sandbox) from known real pyAether layout / via-enclosure sign-off work patterns (layout_aether 14534 scan hits -- the LARGEST class; calibre 12664 scan hits for DRC/enclosure sign-off; VIA/cut/enclosure are core pyAether layout constructs). Real task: after a pyAether via-enclosure check session, the tool emits a per-(via-type,cut-layer) report with the bottom/top enclosure, the required minimum enclosure, an explicit status (PASS/WARN/FAIL/SKIP), and bottom/top layers + instance count, plus a SUMMARY header; the engineer must audit that report for enclosure compliance (any FAIL is a sign-off blocker), identify skipped checks, find the worst (minimum-enclosure) via, reconcile the SUMMARY, and decide sign-off verdict. 10 real traps: (1) status CASE-INSENSITIVE ('fail'/'FAIL'/'Fail' all match -- naive case-sensitive misses lowercase status); (2) DUPLICATE (name,cut) pair LAST-WINS (later VIA line replaces earlier enc_bot/enc_top/req/status, not summed, not first-wins; counts ONCE in total_lines -- naive first-wins keeps a stale FAIL); (3) status ABSENT -> infer from enclosures vs req: FAIL if (enc_bot<req OR enc_top<req) else PASS (never WARN/SKIP -- naive treats absent status as PASS always); (4) enc == req -> PASS inclusive (FAIL only strict < -- naive >= misclassifies the boundary as a violation); (5) missing req= -> default 0.0 (naive uses a non-zero default -> spurious FAILs); (6) missing enc_bot/enc_top -> default 0.0 (a missing enclosure of 0.0 FAILs if req>0 and is included in min_enclosure as 0.0 -- naive excludes missing-enclosure lines from min); (7) min_enclosure/worst_via over NON-SKIP lines ONLY, line enclosure = min(enc_bot,enc_top) (SKIP excluded even if its enclosure is the file min -- naive takes min over ALL lines and reports the SKIP via as worst); (8) worst_via tie at min_enclosure -> lexicographically SMALLEST via name (lsort -dictionary, numeric-aware so 'via2' < 'via10' -- naive ASCII string compare returns 'via10' on the tie); (9) mismatched_summary: min_enclosure compared NUMERICALLY (expr ==, so '0.080' matches computed 0.08; naive string equal false-mismatches); vias_checked/violations/warns/skipped compared as int; worst_via compared as string; absent SUMMARY fields NOT reported (naive reports absent fields); empty list if no SUMMARY; (10) verdict priority fail_count>0 FAIL (TOP) > mismatched_summary non-empty OR no-summary INCOMPLETE > PASS (naive ignores mismatched_summary and returns PASS when only the SUMMARY is wrong). bottom/top/count are red herrings not used in any output key. All output lists lexicographically sorted (lsort -dictionary). Task layout_via_enclosure_audit(report_text) -> flat dict (10 keys). runtime tcl/waveview (pure string + float/integer math, POSIX classes). WAVEVIEW BYPASS (same strategy as Aether-Layout-002/003/004/005/006/007): audits the textual via-enclosure work product on waveview tcl, making the largest class (layout_aether 14534) verifiable without the aether host. DISTINCT from -002 (placement/overlap), -003 (DRC violation-report), -004 (GDS layer-map usage), -005 (percent below-min DRC compliance), -006 (metal-fill target-meeting) and -007 (antenna per-net max-ratio + non-SKIP worst-net) -- this is a per-(via,cut) enclosure AND-logic (FAIL if EITHER enc < req) + min-enclosure (MIN not MAX) + dictionary numeric-aware tie-break audit, a complementary angle on layout sign-off (via enclosure compliance + skip-exclusion + numeric summary reconciliation).",
        "tcr_refs": [
            "status_case_insensitive_fail_fail_fail_all_match",
            "duplicate_name_cut_pair_last_wins_replaces_not_sums_not_first_wins_counts_once",
            "status_absent_infer_FAIL_if_enc_bot_lt_req_OR_enc_top_lt_req_else_PASS_never_WARN_or_SKIP",
            "enc_equals_req_is_PASS_inclusive_FAIL_only_strict_lt",
            "missing_req_defaults_to_0.0_always_PASS",
            "missing_enc_bot_enc_top_defaults_to_0.0_can_FAIL_if_req_gt_0_included_in_min_enclosure",
            "min_enclosure_worst_via_over_non_SKIP_only_line_enclosure_min_enc_bot_enc_top_SKIP_excluded_even_if_file_min_no_non_SKIP_minus_1_empty",
            "worst_via_tie_at_min_enclosure_lexicographically_smallest_via_name_dictionary_numeric_aware_via2_lt_via10",
            "mismatched_summary_min_enclosure_numeric_equality_0.080_equals_0.08_int_for_counts_string_for_worst_via_absent_fields_not_reported",
            "verdict_priority_fail_count_gt_0_FAIL_gt_mismatched_or_no_summary_INCOMPLETE_gt_PASS"
        ],
        "heavy": False,
        "wall_time_sec": 1.0,
        "status": "ready"
    },
    "mode": "design_flow",
    "runtime": {"lang": "tcl", "host": "waveview"},
    "attachments": [],
    "budget": {"max_turns": 40, "wall_time_sec": 1800}
}

# Ensure no duplicate task_id
existing = [json.loads(l) for l in BENCH.read_text().splitlines() if l.strip()]
assert not any(e["task_id"] == entry["task_id"] for e in existing), "duplicate task_id"
existing.append(entry)
BENCH.write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in existing) + "\n")
print(f"appended {entry['task_id']}; jsonl now {len(existing)} lines")
