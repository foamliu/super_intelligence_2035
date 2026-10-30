import json

prompt = """# Scenario: a physical-verification team runs Calibre LVS (layout-vs-schematic)
# and the tool emits a summary report. The QA must audit the report, decide
# whether LVS is CLEAN or has ERRORS, and emit the signed count deltas.
#
# You are given ONE multi-line string `lvs_report_text`. It may contain one or
# more comparison blocks (a re-run appends a second block). Recognized lines
# (keywords are case-sensitive, but INTERNAL whitespace may vary -- e.g.
# "LAYOUT  CELL  NAME  =  TOP" is the same line as "LAYOUT CELL NAME = TOP"):
#   LAYOUT CELL NAME = <name>
#   SOURCE CELL NAME = <name>
#   # of NETS    in layout = <int>
#   # of NETS    in source = <int>
#   # of DEVICES in layout = <int>
#   # of DEVICES in source = <int>
#   # of PORTS   in layout = <int>
#   # of PORTS   in source = <int>
#   ERROR: <text>
#   WARNING: <text>
# Any line that does not match one of the above forms is ignored.
#
# Audit rules (read carefully -- several are non-obvious):
#   1. Per-cell COUNT lines (NETS / DEVICES / PORTS, layout vs source) use
#      LAST-WINS: if the same count is reported again in a later block, the
#      LATER value is authoritative (a re-run supersedes the earlier one).
#   2. ERROR: lines ACCUMULATE across ALL blocks -- every error from every
#      block must be reviewed, even from earlier runs. ERROR lines do NOT use
#      last-wins.
#   3. WARNING: lines are BENIGN. They are counted separately (`warning_lines`)
#      but they NEVER make LVS fail and they are NOT counted as errors.
#   4. Internal whitespace in a recognized line may be collapsed; you MUST
#      normalize runs of whitespace before matching (the leading keyword and
#      the " = " separator still apply after collapse).
#   5. `cell_name_match` is true (1) iff the LAST `LAYOUT CELL NAME` and the
#      LAST `SOURCE CELL NAME` are equal AND non-empty; otherwise 0.
#   6. Each `*_delta` is SIGNED: layout - source (NOT absolute value). A
#      negative delta means source has more; a positive delta means layout
#      has more.
#   7. Each `*_match` is true (1) iff the corresponding signed delta == 0.
#   8. `lvs_verdict` is "clean" iff ALL of: nets_match, devices_match,
#      ports_match, cell_name_match, AND error_lines == 0. Otherwise "errors".
#      (So a zero-delta run that still has ERROR: lines is NOT clean.)
#
# Return a dict with EXACTLY these 12 keys (booleans as 0/1, ints as decimal
# strings, verdict as "clean"/"errors"):
#   layout_cell  source_cell  cell_name_match
#   nets_delta   devices_delta   ports_delta
#   nets_match   devices_match   ports_match
#   error_lines  warning_lines
#   lvs_verdict
#
# Implement exactly:  proc lvs_summary_audit {lvs_report_text} { ... }
# Do NOT change the proc name or the number/order of returned keys."""

with open("/nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-PV-005/test.tcl") as f:
    test_raw = f.read()
test = test_raw.replace("source ref.tcl\nputs [check lvs_summary_audit]\n", "").rstrip()

entry = {
    "task_id": "EDA-Eval-DesignFlow-PV-005",
    "prompt": prompt,
    "entry_point": "lvs_summary_audit",
    "test": test,
    "metadata": {
        "task_name": "Calibre LVS summary audit: last-wins counts + accumulated ERROR lines + whitespace-collapse + signed deltas + cell-name match + ERROR-vs-WARNING + clean/errors verdict",
        "direction": "physical_verify",
        "scenario": "PV signoff QA: audit a Calibre LVS summary report (possibly multi-block / re-run) and report signed NETS/DEVICES/PORTS deltas, cell-name match, ERROR/WARNING line tallies, and a clean/errors verdict",
        "layer": "L2",
        "topic": "calibre-lvs-summary-audit-lastwins-counts-accumulate-errors",
        "difficulty": "medium",
        "design": "Calibre LVS summary audit (per-cell counts LAST-WINS across re-run blocks, ERROR lines ACCUMULATE across all blocks, WARNING benign, internal-whitespace collapse required, signed layout-source deltas, cell-name match requires non-empty equality, verdict clean iff all matches + cell match + zero ERROR lines); derived from real mined physical-verification session patterns (calibre 12664 / physical_verify 1295 scan hits) per 2026-10-29 ephemeral-session strategy correction",
        "tcr_refs": [
            "counts_last_wins_across_rerun_blocks",
            "error_lines_accumulate_across_all_blocks_not_last_wins",
            "warning_lines_benign_not_counted_as_errors",
            "internal_whitespace_collapse_before_keyword_match",
            "signed_delta_layout_minus_source_not_abs",
            "cell_name_match_requires_nonempty_equality_of_last_values",
            "verdict_clean_requires_all_match_and_cell_match_and_zero_errors",
            "dict_create_flat_12_key_emission"
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

line = json.dumps(entry, ensure_ascii=False)
json.loads(line)
path = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow-PhysicalVerify.jsonl"
with open(path, "a") as f:
    f.write(line + "\n")
with open(path) as f:
    n = sum(1 for _ in f if _.strip())
print("appended OK; bytes:", len(line))
print("PhysicalVerify.jsonl now has", n, "lines")
