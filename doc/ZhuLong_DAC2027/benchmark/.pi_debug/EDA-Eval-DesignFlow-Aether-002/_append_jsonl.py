#!/usr/bin/env python3
import json, sys, pathlib

DBG = pathlib.Path("/nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Aether-002")
JSONL = pathlib.Path("/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow-Aether-Layout.jsonl")

prompt = (DBG / "prompt.txt").read_text()
test = (DBG / "checker.tcl").read_text()

entry = {
    "task_id": "EDA-Eval-DesignFlow-Aether-Layout-002",
    "mode": "design_flow",
    "status": "ready",
    "prompt": prompt,
    "entry_point": "layout_placement_audit",
    "attachments": [],
    "test": test,
    "budget": {"max_turns": 40, "wall_time_sec": 1800},
    "runtime": {"lang": "tcl", "host": "waveview"},
    "metadata": {
        "task_name": "pyAether layout cellview placement-report audit: parse INST/RECT/PIN/REQUIRE lines, count instances/rects/pins, flag duplicate inst names, flag malformed bboxes (zero-area OR inverted: urx<=llx OR ury<=lly), detect overlapping INSTANCE pairs (strict interior bbox intersection only -- touching edges excluded, rects/pins excluded, malformed excluded), report missing required layers (REQUIRE - RECT layers only), report unconnected pins (pin layer not in any RECT), report layers_used (RECT layers only), emit single highest-priority verdict (malformed>overlap>missing_layer>unconnected_pin>clean)",
        "direction": "layout_aether",
        "scenario": "Layout/QA: given a textual pyAether-style cellview placement report (INST/RECT/PIN/REQUIRE lines), audit placement integrity -- duplicate instance names, malformed (zero-area/inverted) bboxes, strict-interior instance overlaps, missing required layers (RECT-presence only), unconnected pins (pin layer not in any RECT), and a single priority-ordered verdict. Waveview-bypass for the aether host sandbox init timeout: this audits a layout WORK PRODUCT (textual placement report) with pure string + bbox math on waveview tcl, staying in the layout_aether category without needing the aether host.",
        "layer": "L2",
        "topic": "layout-placement-audit-strict-interior-overlap-zero-area-malformed-rect-only-layer-presence-inst-vs-inst-overlap-priority-verdict",
        "difficulty": "medium",
        "design": "DERIVED (per 2026-10-29 ephemeral-session strategy: cline sessions cleared, fresh mining dead; aether host run_code init times out so layout_aether cannot be verified on the aether sandbox) from known real pyAether layout work patterns (layout_aether 14534 scan hits -- the LARGEST class; dbCreateInst 925 / dbCreateRect 457 / cellview 9389 scan hits). Real task: after a pyAether session places instances (dbCrtInst) and draws rects (dbCrtRect) and declares pins, audit the resulting placement report for DRC-like integrity before sign-off. 10 real traps: (1) STRICT INTERIOR overlap (touching edge urx==other.llx is NOT overlap); (2) MALFORMED includes ZERO-AREA (urx==llx) not just inverted; (3) layers_used/missing_layers/unconnected_pins key off RECT layers ONLY (INST/PIN layer doesn't count as present); (4) OVERLAP is INST vs INST only (rects/pins excluded -- overlapping rects are normal wiring); (5) MALFORMED instances EXCLUDED from overlap (zero-area inst inside another NOT an overlap pair); (6) VERDICT = single highest-priority category (malformed>overlap>missing_layer>unconnected_pin), not first-detected; (7) overlapping_pairs each unordered pair ONCE, smaller name first, lex sorted, dedup; (8) all output lists lex sorted (lsort -dictionary); (9) duplicate_inst_names counts occurrences>1; (10) REQUIRE-absent => missing_layers empty. Task layout_placement_audit(placement_text) -> flat dict (10 keys). runtime tcl/waveview (pure string + bbox math, POSIX classes). WAVEVIEW BYPASS: Aether-Layout-001 (create inverter layout + export GDS) requires the aether host (pyAether API) and is BLOCKED as draft by the aether sandbox init timeout; THIS task audits the textual placement work product on waveview tcl, making the largest class (layout_aether 14534) verifiable without the aether host. DISTINCT from Aether-Layout-001 (build layout on aether host).",
        "tcr_refs": [
            "strict_interior_bbox_overlap_touching_edge_excluded",
            "malformed_bbox_includes_zero_area_urx_eq_llx_not_just_inverted",
            "layer_presence_keyed_off_rect_layers_only_not_inst_or_pin",
            "overlap_is_inst_vs_inst_only_rects_pins_excluded",
            "malformed_instances_excluded_from_overlap_detection",
            "verdict_single_highest_priority_malformed_overlap_missing_layer_unconnected_pin",
            "overlapping_pairs_unordered_once_smaller_name_first_lex_sorted_dedup",
            "all_output_lists_lexicographically_sorted_lsort_dictionary",
            "duplicate_inst_names_count_occurrences_greater_than_one",
            "missing_layers_empty_when_no_require_line"
        ],
        "heavy": False,
        "wall_time_sec": 1.0,
        "status": "ready"
    }
}

# append
with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended", entry["task_id"], "to", JSONL)
# report counts
import subprocess
out = subprocess.run(["bash","-lc", f"grep -c task_id {JSONL}"], capture_output=True, text=True).stdout.strip()
print("aether-layout jsonl now has", out, "entries")
