#!/usr/bin/env python3
import json, pathlib

JPATH = pathlib.Path("/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow-Aether-Layout.jsonl")
PROMPT = pathlib.Path("/nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Aether-004/prompt.txt").read_text()
TEST = pathlib.Path("/nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Aether-004/checker.tcl").read_text()

entry = {
    "task_id": "EDA-Eval-DesignFlow-Aether-Layout-004",
    "prompt": PROMPT,
    "entry_point": "layout_gds_layermap_audit",
    "test": TEST,
    "metadata": {
        "task_name": "pyAether layout cellview GDS layer-map usage audit: parse LAYER/SUMMARY lines, count distinct layers (last-wins dedup on duplicate layer names), sum shape counts (missing count= -> 0), bucket layers by purpose CASE-INSENSITIVE (drawing/pin/label), route empty-purpose layers to missing_purpose_layers (no default), detect shared (gdsno,datatype) PAIR duplicates (same gdsno DIFFERENT datatype is NOT a dup; list ALL layers sharing a pair), max-count layer with lex-smallest tie-break, SUMMARY-vs-computed mismatched fields (absent fields not reported), emit single priority-ordered verdict (FAIL for dup > INCOMPLETE for missing-purpose or no-summary > PASS)",
        "direction": "layout_aether",
        "scenario": "Layout/QA sign-off: given a textual pyAether-emitted GDS layer-map usage report (LAYER <name> gdsno=<> datatype=<> purpose=<> count=<> lines + a SUMMARY line), audit it for correctness before tape-out -- aggregate shape counts by layer, verify the layer map has no duplicate (gdsno,datatype) pairs (which would corrupt the GDS stream), verify every declared layer has a purpose, reconcile the SUMMARY header with the layer list, and emit a pass/incomplete/fail verdict. Waveview-bypass for the aether host sandbox init timeout: this audits a layout WORK PRODUCT (textual GDS layer-map report) with pure string + integer math on waveview tcl, staying in the layout_aether category without needing the aether host.",
        "layer": "L2",
        "topic": "layout-gds-layermap-audit-purpose-case-insensitive-last-wins-dedup-shared-pair-dup-datatype-aware-missing-purpose-no-default-max-count-lex-tie-break-summary-reconciliation-priority-verdict",
        "difficulty": "medium",
        "design": "DERIVED (per 2026-10-29 ephemeral-session strategy: cline sessions cleared, fresh mining dead; aether host run_code init times out so layout_aether cannot be verified on the aether sandbox) from known real pyAether layout / GDS-stream work patterns (layout_aether 14534 scan hits -- the LARGEST class; cellview 9389 / dbCreateRect 457 scan hits for layer/map work). Real task: after a pyAether layout session, the tool emits a per-layer GDS layer-map usage report with a SUMMARY header; the engineer must audit that report for GDS-stream correctness (duplicate gdsno+datatype pairs would collide in the GDS file; missing purpose makes a layer un-classifiable) and decide sign-off verdict. 10 real traps: (1) purpose CASE-INSENSITIVE (DRAWING/Drawing/drawing all drawing -- naive exact-match misbuckets); (2) DUPLICATE layer NAMES LAST-WINS (later LAYER line replaces earlier gdsno/datatype/purpose/count, not summed, not first-wins); (3) dup_gdsno = shared (gdsno AND datatype) PAIR -- same gdsno DIFFERENT datatype is NOT a dup (naive gdsno-alone check false-positives); list ALL layers sharing a pair, each name once; (4) missing purpose: a layer with empty purpose= goes to missing_purpose_layers, NOT defaulted to drawing, NOT in drawing/pin/label (naive defaults to drawing); (5) max_shape_layer tie -> lexicographically SMALLEST name wins (naive first-seen returns wrong name); (6) total_shapes sums LAST-WINS distinct counts, not all input LAYER lines (naive sums all); (7) mismatched_summary compares computed vs SUMMARY per-field, absent fields NOT reported (naive trusts SUMMARY or reports all); (8) verdict priority dup_gdsno non-empty FAIL > missing_purpose non-empty INCOMPLETE > no-summary INCOMPLETE > PASS (naive may reverse dup/missing priority or report INCOMPLETE when dup present); (9) all output lists lexicographically sorted (lsort -dictionary); (10) count default 0 when count= field absent. Task layout_gds_layermap_audit(report_text) -> flat dict (11 keys). runtime tcl/waveview (pure string + integer math, POSIX classes). WAVEVIEW BYPASS (same strategy as Aether-Layout-002/003): audits the textual GDS layer-map work product on waveview tcl, making the largest class (layout_aether 14534) verifiable without the aether host. DISTINCT from Aether-Layout-002 (placement/overlap audit) and -003 (DRC violation-report audit) -- this is a GDS layer-map usage + pair-collision + purpose-classification audit.",
        "tcr_refs": [
            "purpose_case_insensitive_drawing_pin_label_all_variants",
            "duplicate_layer_names_last_wins_replaces_not_sums_not_first_wins",
            "dup_gdsno_shared_gdsno_AND_datatype_pair_same_gdsno_different_datatype_not_dup",
            "dup_gdsno_lists_all_layers_sharing_a_pair_each_name_once",
            "missing_purpose_layers_empty_purpose_not_defaulted_to_drawing_not_in_drawing_pin_label",
            "max_shape_layer_tie_break_lexicographically_smallest_name_wins",
            "total_shapes_sums_last_wins_distinct_counts_not_all_input_lines",
            "mismatched_summary_absent_summary_fields_not_reported_empty_if_no_summary",
            "verdict_priority_dup_fail_gt_missing_purpose_incomplete_gt_no_summary_incomplete_gt_pass",
            "all_output_lists_lexicographically_sorted_lsort_dictionary",
            "count_default_zero_when_count_field_absent"
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
