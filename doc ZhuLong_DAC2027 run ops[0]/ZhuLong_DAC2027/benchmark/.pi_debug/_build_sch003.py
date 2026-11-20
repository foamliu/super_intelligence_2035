#!/usr/bin/env python3
import json, pathlib

prompt = """# Scenario: a schematic-QA engineer receives an emy2netlist-exported SPICE
# netlist containing a mix of `.subckt` definitions and `X...` sub-circuit
# instantiations. Before tape-in they must audit every `X` instantiation for
# pin-arity consistency: each instantiation must connect exactly as many
# positional nodes as its referenced sub-circuit declares ports. The deliverable
# is a flat report dict capturing defined sub-circuits, scanned instances,
# arity matches / mismatches, instantiations of unknown (never-defined)
# sub-circuits, malformed instances, and an overall verdict.
#
# You are given ONE multi-line string `netlist_text` -- a fragment of a SPICE
# netlist. Implement the proc `spice_subckt_pin_arity_audit(netlist_text)` that
# returns a flat Tcl dict with EXACTLY these 8 keys in this order:
#     total_subckts_defined subckts_defined instances_scanned
#     arity_matches arity_mismatches unknown_subckt_instances
# malformed_instances verdict
#
# ---- LOGICAL-LINE BUILDING ----
# The raw text is a sequence of physical lines. Build "logical lines" first:
#   - Drop CR (`\\r`). Trim each physical line of leading/trailing whitespace.
#   - A line whose first character is `*` is a COMMENT: it is discarded, AND it
#     also terminates any pending continuation (flushes the in-progress logical
#     line, then discards the comment).
#   - A blank line is discarded AND terminates any pending continuation
#     (flushes the in-progress logical line).
#   - A line whose first character is `+` is a CONTINUATION: the text after the
#     `+` (trimmed) is appended (with a single space) to the in-progress logical
#     line. A `+` line with no in-progress line is a dangling continuation and is
#     discarded.
#   - Any other line FLUSHES the previous in-progress logical line (if any) and
#     becomes the new in-progress one. At EOF, flush the last in-progress line.
#
# ---- SUBCKT DEFINITIONS ----
# A logical line whose first token (case-insensitive) is `.subckt` declares a
# sub-circuit. Token 1 is the NAME. The PORT list = every token after the NAME
# on that (already-continuation-joined) header line that does NOT contain a `=`
# sign. port_count = number of such port tokens. Tokens with `=` on the header
# are parameter defaults and are NOT ports.
#   - LAST-WINS: if a NAME is defined more than once, the LATER definition's
#     port_count FULLY REPLACES the earlier one (do not merge, do not keep first).
#   - `.ends` / `.ends NAME` lines are simply discarded (they start with `.` and
#     are not instances); they do not affect port_count.
#   - Other `.`-directives (`.param`, `.lib`, `.op`, ...) are ignored.
#
# ---- X INSTANTIATIONS ----
# A logical line whose first token starts with `X` or `x` (the instance name)
# is a sub-circuit instantiation. Tokenize the (continuation-joined) line on
# whitespace. From the tokens AFTER the instance name:
#   - A NODE is a token that does NOT contain `=`.
#   - A PARAM is a token that DOES contain `=`.
#   - The SUBCKT NAME referenced = the LAST node token (the rightmost non-`=`
#     token). The PINS = all node tokens EXCEPT that last one.
#     pin_count = (number of node tokens) - 1.
#   - If there are ZERO node tokens after the instance name (e.g.
#     `X1 w=1u l=1u` -- only params), the instance is MALFORMED: increment
#     malformed_instances and do NOT classify it as match/mismatch/unknown.
#   - If there is exactly ONE node token, subckt name = that token, pin_count = 0.
# Audit each (non-malformed) instance:
#   - If the referenced subckt NAME is in the defined set: compare pin_count to
#     that subckt's port_count. Equal -> append "<inst> <sub>" to arity_matches.
#     Not equal -> append "<inst> <sub> <expected_ports> <actual_pins>" to
#     arity_mismatches.
#   - If the referenced subckt NAME is NOT defined: append "<inst> <sub>" to
#     unknown_subckt_instances. (Do NOT treat unknown as a 0-port mismatch.)
#
# ---- OUTPUT DICT ----
#   total_subckts_defined      : int, count of UNIQUE defined subckt names.
#   subckts_defined            : list of unique defined names, LEXICOGRAPHICALLY
#                                sorted (lsort ascending).
#   instances_scanned          : int, total X instances seen (including
#                                malformed and unknown-referencing ones).
#   arity_matches              : list of "<inst> <sub>", LEXICOGRAPHICALLY sorted.
#   arity_mismatches           : list of "<inst> <sub> <expected> <actual>",
#                                LEXICOGRAPHICALLY sorted.
#   unknown_subckt_instances   : list of "<inst> <sub>", LEXICOGRAPHICALLY sorted.
#   malformed_instances        : int.
#   verdict                    : "pass" iff arity_mismatches is empty AND
#                                unknown_subckt_instances is empty AND
#                                malformed_instances == 0; else "fail".
#
# ---- REAL TRAPS (a naive implementation fails these; the checker asserts the
#       CORRECT behavior) ----
# (1) PARAM EXCLUSION: tokens with `=` (params) are NOT pins and are NOT the
#     subckt name. `X1 a b INV w=1u l=1u` -> pins = [a b] (count 2), sub = INV.
#     Naive "count all middle tokens" -> 4 pins -> false mismatch.
# (2) LAST-WINS REDEFINITION: a repeated `.subckt NAME` REPLACES port_count.
#     `.subckt INV a b` then `.subckt INV a b c` -> port_count(INV)=3.
#     Naive "first definition wins" -> 2 -> false match.
# (3) CONTINUATION JOIN: an instance (or subckt header) split across `+` lines
#     must be joined before tokenizing. `X1 a b\\n+ c d MUX4` -> one instance,
#     nodes [a b c d MUX4], sub=MUX4, pins=4. Naive per-line -> line1 `X1 a b`
#     -> sub=b (unknown) -> wrong.
# (4) UNKNOWN != MISMATCH: an instantiation of an undefined subckt goes to
#     unknown_subckt_instances, NOT to arity_mismatches (you cannot compare
#     arity against an undefined port_count). Naive "compare to 0 ports" ->
#     false mismatch.
# (5) COMMENT / BLANK LINES: `*`-comment and blank lines are skipped (and they
#     terminate a pending continuation). Naive "treat * line as instance" ->
#     garbage.
# (6) MALFORMED: an `X` instance with no node token (only params) is malformed,
#     counted in malformed_instances, NOT classified as unknown/mismatch. Naive
#     "last token = subckt regardless of `=`" -> treats a param as the subckt
#     name -> false unknown entry.
# (7) LEXICOGRAPHIC SORT: every output list is sorted ascending (lsort) for
#     determinism. Naive insertion-order emission -> wrong expected list.
#
# ---- IMPLEMENTATION NOTES ----
# Use Tcl `split` on newline, `string map` to drop `\\r`, `string trim`,
# `regexp --` with POSIX classes only (e.g. [[:space:]] -- do NOT rely on
# `\\s`/`\\d`/`\\w`/`\\b` Perl classes), `string match *=* $tok` to detect
# params, `dict create` to build the returned dict in the EXACT key order, and
# `lsort` to sort all list-valued keys. Keep the solution minimal and pure
# string analysis (no external files)."""

test = """set cA {.subckt INV a b
.ends
X1 net1 net2 INV
X2 p q INV}
    set dA [$candidate $cA]
    assert {[dget $dA total_subckts_defined] == 1} "A total=1"
    assert {[j $dA subckts_defined] eq "INV"} "A subckts_defined"
    assert {[dget $dA instances_scanned] == 2} "A instances=2"
    assert {[llength [llist $dA arity_matches]] == 2} "A 2 matches"
    assert {[j $dA arity_matches] eq "X1 INV|X2 INV"} "A matches sorted"
    assert {[llength [llist $dA arity_mismatches]] == 0} "A no mismatches"
    assert {[llength [llist $dA unknown_subckt_instances]] == 0} "A no unknown"
    assert {[dget $dA malformed_instances] == 0} "A no malformed"
    assert {[string equal [dget $dA verdict] "pass"]} "A verdict pass"

    set cB {.subckt INV a b
.ends
X1 a b INV w=1u l=1u}
    set dB [$candidate $cB]
    assert {[llength [llist $dB arity_matches]] == 1} "B 1 match (params excluded)"
    assert {[j $dB arity_matches] eq "X1 INV"} "B match X1 INV"
    assert {[llength [llist $dB arity_mismatches]] == 0} "B no mismatch (naive counts 4 pins -> wrong)"
    assert {[string equal [dget $dB verdict] "pass"]} "B verdict pass"

    set cC {.subckt INV a b
.ends
.subckt INV a b c
.ends
X1 x y INV}
    set dC [$candidate $cC]
    assert {[dget $dC total_subckts_defined] == 1} "C total=1 (unique, redefined)"
    assert {[llength [llist $dC arity_mismatches]] == 1} "C 1 mismatch (last-wins 3 ports)"
    assert {[j $dC arity_mismatches] eq "X1 INV 3 2"} "C mismatch X1 INV 3 2"
    assert {[llength [llist $dC arity_matches]] == 0} "C no match (naive first-def -> match WRONG)"
    assert {[string equal [dget $dC verdict] "fail"]} "C verdict fail"

    set cD {.subckt MUX4 a b c d
.ends
X1 a b
+ c d MUX4}
    set dD [$candidate $cD]
    assert {[dget $dD instances_scanned] == 1} "D 1 instance (continuation joined)"
    assert {[llength [llist $dD arity_matches]] == 1} "D 1 match after join"
    assert {[j $dD arity_matches] eq "X1 MUX4"} "D match X1 MUX4"
    assert {[llength [llist $dD unknown_subckt_instances]] == 0} "D no unknown (naive per-line -> unknown b WRONG)"
    assert {[string equal [dget $dD verdict] "pass"]} "D verdict pass"

    set cE {.subckt INV a b
.ends
X1 a b GHOST}
    set dE [$candidate $cE]
    assert {[llength [llist $dE unknown_subckt_instances]] == 1} "E 1 unknown"
    assert {[j $dE unknown_subckt_instances] eq "X1 GHOST"} "E unknown X1 GHOST"
    assert {[llength [llist $dE arity_mismatches]] == 0} "E no mismatch (naive 0-port compare -> mismatch WRONG)"
    assert {[string equal [dget $dE verdict] "fail"]} "E verdict fail"

    set cF {* header comment line skipped
.subckt INV a b
.ends
Xz a b INV
X1 w=1u l=1u
Xa a b INV}
    set dF [$candidate $cF]
    assert {[dget $dF instances_scanned] == 3} "F 3 instances scanned"
    assert {[dget $dF malformed_instances] == 1} "F 1 malformed (all-param instance)"
    assert {[llength [llist $dF arity_matches]] == 2} "F 2 matches"
    assert {[j $dF arity_matches] eq "Xa INV|Xz INV"} "F matches lexicographically sorted (Xa before Xz)"
    assert {[llength [llist $dF unknown_subckt_instances]] == 0} "F no unknown (naive last-token-as-subckt -> unknown l=1u WRONG)"
    assert {[string equal [dget $dF verdict] "fail"]} "F verdict fail (malformed>0)"

    return "ALL_ASSERTS_PASS"
}"""

full_test = """proc assert {cond msg} {
    set ok [uplevel 1 [list expr $cond]]
    if {!$ok} { error "ASSERT FAIL: $cond -- $msg" }
}
proc dget {d k} { return [dict get $d $k] }
proc llist {d k} { return [dict get $d $k] }
proc j {d k} { return [join [dict get $d $k] "|"] }

proc check {candidate} {
""" + test

entry = {
    "task_id": "EDA-Eval-DesignFlow-Sch-003",
    "prompt": prompt,
    "entry_point": "spice_subckt_pin_arity_audit",
    "test": full_test,
    "metadata": {
        "task_name": "SPICE netlist emy2netlist subckt instantiation pin-arity audit: parse .subckt port headers (LAST-WINS redefinition + header continuation) + X instantiations (param-exclusion + continuation-join + subckt-name=last-non-= node) -> match/mismatch/unknown/malformed classification + lexicographic sort",
        "direction": "schematic_netlist",
        "scenario": "Analog/schematic-QA: given an emy2netlist-exported SPICE netlist fragment of .subckt definitions and X instantiations, audit every X instantiation's positional pin count against its referenced subckt's declared port count, separating arity matches / arity mismatches / unknown-subckt instantiations / malformed (param-only) instances, with LAST-WINS redefinition, '+'-continuation joining and lexicographically sorted reports",
        "layer": "L2",
        "topic": "netlist-subckt-pin-arity-audit-last-wins-redef-continuation-join-param-exclusion",
        "difficulty": "medium",
        "design": "DERIVED (per 2026-10-29 ephemeral-session strategy: cline sessions cleared, fresh mining dead) from known real schematic-to-SPICE-netlist export QA patterns (schematic_netlist 2362 scan hits / netlist 1047 / cellview 9389). Real task: after emy2netlist export, audit every X sub-circuit instantiation for pin-arity consistency against .subckt port declarations before tape-in. 7 real traps: (1) PARAM EXCLUSION (tokens with '=' are not pins nor the subckt name); (2) LAST-WINS .subckt redefinition (later def replaces port_count); (3) '+' CONTINUATION JOIN (instance/header split across lines must be joined before tokenizing); (4) UNKNOWN != MISMATCH (undefined subckt -> unknown list, not 0-port mismatch); (5) comment/blank lines skipped and break continuation; (6) MALFORMED (X instance with only params, no node -> malformed, not unknown); (7) LEXICOGRAPHIC SORT of all output lists. Task spice_subckt_pin_arity_audit(netlist_text) -> flat dict (8 keys). runtime tcl/waveview (pure string ops, POSIX classes). DISTINCT from Sch-001 (open cellview + query, virtuoso skill) and Sch-002 (emy2netlist export-header * Library/* Cell/* View -> lib_cell.list mapping): THIS = netlist-body .subckt/X pin-arity consistency audit.",
        "tcr_refs": [
            "param_token_excluded_from_pin_count_and_subckt_name",
            "subckt_redefinition_last_wins_port_count",
            "plus_continuation_line_join_before_tokenize",
            "unknown_subckt_not_treated_as_zero_port_mismatch",
            "comment_and_blank_lines_skip_and_break_continuation",
            "malformed_param_only_instance_counted_separately",
            "all_output_lists_lexicographically_sorted",
            "dict_create_flat_eight_keys_in_order"
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

out = pathlib.Path("/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow-Schematic-Netlist.jsonl")
lines = out.read_text().splitlines()
# dedup by task_id
keep = [l for l in lines if json.loads(l)["task_id"] != entry["task_id"]]
keep.append(json.dumps(entry, ensure_ascii=False))
out.write_text("\n".join(keep) + "\n")
print("written:", out, "lines:", len(keep))
for l in keep:
    print("  ", json.loads(l)["task_id"])
