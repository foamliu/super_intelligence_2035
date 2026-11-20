#!/usr/bin/env python3
"""Build EdaOther-004 jsonl entry: vsim_pattern_coverage_audit.
Mined from real cliu session 1793078652491_wk3wd (vsim_report_new + pattern.list
A_Summary.rpt flow). Appends one line to EDA-Eval-DesignFlow-EdaOther.jsonl.
"""
import json, pathlib

PROMPT = r"""You are auditing pattern coverage for a DDR DV simulation regression that uses a vsim-style reporting flow. Each simulation run produces an `A_Summary.rpt` file whose layout (mirroring a real CXMT DV session) is:

    Total Pattern : <n>
     Failed Pattern: <n>
    Global_Seed : <n>
    -----------------
    <pattern_name>
    <pattern_name>
    ...

NOTE the colon-spacing ASYMMETRY, which is real and intentional:
- `Total Pattern : <n>`  has a space BEFORE and AFTER the colon.
- ` Failed Pattern: <n>` has a LEADING space, NO space before the colon, space after.
A parser keyed on only one of these forms will miss the other.

You are given TWO text blobs:

1. `reports_text` — one or more `A_Summary.rpt` sections concatenated. Each section
   begins with a header line `=== <simdir> ===` (the simdir encodes a regression name
   and a bytemode, e.g. `basic.x4`, `checkin.x8`, `misc.x16`). After the header come
   the count lines, then a `---...` separator (3+ dashes), then one pattern name per
   line. Sections may be separated by blank lines.

2. `pattern_list_text` — the reference full-set of expected pattern names, one per
   line. It may contain blank lines, `#` comment lines, trailing whitespace, carriage
   returns (`\r`), and DUPLICATE entries (a real reference list had a duplicate).

Implement `vsim_pattern_coverage_audit(reports_text, pattern_list_text)` returning a
FLAT key/value string. Rules (mirror the real DV coverage audit):

1. Section parse:
   - `runs_parsed` = number of `=== <simdir> ===` headers.
   - `total_pattern_reported` = sum of the `Total Pattern` header values across runs.
   - `total_failed_reported` = sum of the `Failed Pattern` header values across runs.
   - `pattern_list_entries` = count of ACTUAL pattern-name lines that appear AFTER the
     `---` separator across all runs (raw, includes duplicates within/across runs).
     This is NOT the header sum: a run may report `Total Pattern : 5` but list only 4
     names (a real data-quality discrepancy); `pattern_list_entries` counts the 4.
   - Header lines (Total/Failed/Global_Seed) BEFORE the separator and the `---`
     separator itself are NOT pattern names and must NOT be counted as such.

2. Bytemode / regression extraction from `<simdir>`:
   - bytemode = the `.xN` token (a dot, literal `x`, then digits) matched anywhere in
     the simdir, e.g. `basic.x4` -> `x4`, `misc.x16` -> `x16`. For `basic.x4.rerun` the
     bytemode is STILL `x4` (the trailing `.rerun` is ignored). For a simdir with no
     `.xN` token (e.g. `nosuffix`), bytemode = `unknown`.
   - regression = the substring of simdir BEFORE the matched `.xN` (e.g. `basic.x4` ->
     `basic`, `basic.x4.rerun` -> `basic`, `nosuffix` -> `nosuffix`).
   - `bytemodes` = sorted unique bytemodes, comma-joined (no spaces).
   - `regressions` = sorted unique regression names, comma-joined (no spaces).

3. Reference list (`pattern_list_text`):
   - Skip blank lines and lines whose first non-space character is `#`.
   - Strip trailing `\r` and surrounding whitespace from each name.
   - `expected_count` = number of UNIQUE non-blank non-comment names (duplicates in the
     reference list are collapsed; a real list had a duplicate).
   - Build the expected SET from these unique names.

4. Ran set:
   - `ran_unique` = number of UNIQUE pattern names appearing in ≥1 run's list (after
     the separator). A pattern appearing twice in one run, or in two runs, counts ONCE
     in `ran_unique` but contributes to `pattern_list_entries` each time.

5. Coverage diff (DIRECTION MATTERS):
   - `missing_patterns` = sorted (ascending) names in the expected set that appear in
     NO run. `missing_count` = its length.
   - `extra_patterns` = sorted names in the ran set that are NOT in the expected set.
     `extra_count` = its length.

6. `coverage_verdict`:
   - `complete` if missing_count == 0 and extra_count == 0
   - `missing` if missing_count > 0 and extra_count == 0
   - `extra` if missing_count == 0 and extra_count > 0
   - `missing_and_extra` if both > 0

Output string format (single line, keys separated by single spaces; `bytemodes` and
`regressions` are single comma-joined tokens; `missing_patterns` / `extra_patterns`
are space-separated name lists terminated by the next key; for an empty list emit the
key immediately followed by the next key with no names):

    runs_parsed <n> total_pattern_reported <n> total_failed_reported <n> pattern_list_entries <n> bytemodes <x..,x..> regressions <r..,r..> ran_unique <n> expected_count <n> missing_count <n> missing_patterns <name...> extra_count <n> extra_patterns <name...> coverage_verdict <complete|missing|extra|missing_and_extra>

Use POSIX character classes only (`[[:space:]]`, `[[:digit:]]`, `[[:alnum:]_]`,
`[0-9]`); do NOT use `\b`, `\s`, `\d`. Sorting is lexicographic ascending (`lsort`).
"""

TEST = pathlib.Path("checker.tcl").read_text()

entry = {
    "task_id": "EDA-Eval-DesignFlow-EdaOther-004",
    "prompt": PROMPT,
    "entry_point": "vsim_pattern_coverage_audit",
    "test": TEST,
    "metadata": {
        "task_name": "vsim A_Summary.rpt pattern-coverage audit: parse multi-run summary reports + reference pattern list, compute bytemode/regression grouping, ran/missing/extra coverage diff with verdict",
        "direction": "eda_other",
        "scenario": "DV regression coverage audit: parse vsim-style A_Summary.rpt sections (Total/Failed Pattern headers + post-separator pattern lists) grouped by simdir bytemode/regression, diff against a reference pattern.list to find missing/extra patterns",
        "layer": "L2",
        "topic": "vsim-pattern-coverage-audit",
        "difficulty": "medium",
        "design": "CXMT DDR DV vsim_report_new + pattern.list A_Summary.rpt coverage flow (mined from real cliu session 1793078652491_wk3wd; pattern.list 170 lines/169 unique with mbist_three_deep duplicate; A_Summary.rpt 'Total Pattern : N' vs ' Failed Pattern: N' colon-spacing asymmetry)",
        "tcr_refs": [
            "colon_spacing_asymmetry_total_vs_failed",
            "reference_list_duplicate_dedup",
            "reference_list_comment_blank_cr_whitespace_skip",
            "missing_vs_extra_direction",
            "bytemode_xN_token_extraction_rerun_suffix",
            "header_count_vs_actual_list_length_mismatch",
            "separator_header_exclusion_from_pattern_names",
            "ran_unique_vs_entries_dup_collapse",
            "coverage_verdict_four_way",
            "posix_char_classes_only"
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

out = pathlib.Path("/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow-EdaOther.jsonl")
with out.open("a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended", entry["task_id"], "to", out)
print("file now has", sum(1 for _ in out.open()), "lines")
