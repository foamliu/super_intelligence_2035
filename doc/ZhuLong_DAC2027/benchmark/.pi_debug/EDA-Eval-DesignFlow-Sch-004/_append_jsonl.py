#!/usr/bin/env python3
"""Append Schematic-Netlist-004 case to the EDA-Eval-DesignFlow-Schematic-Netlist.jsonl
and write the reference impl to benchmarks/EDA-Eval-DesignFlow/reference/."""
import json, pathlib

BASE = pathlib.Path("/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow")
PROMPT = (pathlib.Path("/nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Sch-004/prompt.txt")).read_text()
CHECKER = (pathlib.Path("/nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Sch-004/checker.tcl")).read_text()
REF = (pathlib.Path("/nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Sch-004/ref_impl.tcl")).read_text()

case = {
    "task_id": "EDA-Eval-DesignFlow-Sch-004",
    "prompt": PROMPT,
    "entry_point": "netlist_fanout_floating_audit",
    "test": CHECKER,
    "metadata": {
        "task_name": ("SPICE netlist emy2netlist net fanout / floating-net / "
                      "power-ground connectivity audit: parse X-subckt "
                      "instantiations (+ continuation join, param exclusion, "
                      "subname=last-non-param-token) + .global declarations "
                      "into a per-net connection-count map, classify "
                      "power/ground (name-rule case-insens + '!' strip + glob, "
                      "SPICE '0' ground, .global declared), detect floating "
                      "(==1 conn, not pg), max-fanout (lex-smallest tie-break), "
                      "verdict clean/floating/sparse_power/both"),
        "direction": "schematic_netlist",
        "scenario": ("Analog/schematic-QA: given an emy2netlist-exported SPICE "
                     "netlist fragment of X-instantiations + .subckt/.ends/"
                     ".global dot-commands + '*' comments, audit net "
                     "connectivity -- per-net connection counts, floating nets "
                     "(1 conn, not power/ground), power/ground classification "
                     "(name rule + SPICE '0' + .global), max fanout with "
                     "lexicographic tie-break, and a clean/floating/sparse_power/"
                     "both verdict combining floating detection with sparse-"
                     "power (a power net with <2 connections)"),
        "layer": "L2",
        "topic": ("netlist-fanout-floating-audit-continuation-join-param-exclusion-"
                  "pg-name-rule-global-decl-dup-node-count-lex-tie-break-sparse-power"),
        "difficulty": "medium",
        "design": ("DERIVED (per 2026-10-29 ephemeral-session strategy: cline "
                   "sessions cleared, fresh mining dead) from known real "
                   "schematic-to-SPICE-netlist export QA patterns "
                   "(schematic_netlist 2362 scan hits / netlist 1047 / cellview "
                   "9389). Real task: after emy2netlist export, audit net "
                   "connectivity before tape-in -- flag floating nets, classify "
                   "power/ground, detect sparse-power (under-connected supply), "
                   "report max fanout. 10 real traps: (1) PARAM EXCLUSION "
                   "(tokens with '=' are not nodes/subname); (2) SUBNAME = LAST "
                   "non-'=' token (excluded from nodes); (3) POWER/GROUND NAME "
                   "RULE (case-insensitive, strip trailing '!', glob "
                   "gnd*/vdd*/vss*/vcc*/avdd*/avss*/dvdd*/dvss*); (4) SPICE '0' "
                   "node is always ground; (5) '.global' declared net is "
                   "power/ground-class even if name doesn't match globs; "
                   "(6) '+' CONTINUATION JOIN; (7) DUPLICATE NODE IN ONE "
                   "INSTANCE counts as 2 connections; (8) COMMENT/BLANK break "
                   "continuation; (9) MAX_FANOUT lex-smallest tie-break; "
                   "(10) LEX SORT output lists; (11) verdict 4-way truth table "
                   "(clean/floating/sparse_power/both). Task "
                   "netlist_fanout_floating_audit(netlist_text) -> flat dict "
                   "(10 keys). runtime tcl/waveview (pure string ops, POSIX "
                   "classes). DISTINCT from Sch-001 (open cellview + query, "
                   "virtuoso skill), Sch-002 (export-header * Library/* Cell/* "
                   "View -> lib_cell.list mapping) and Sch-003 (.subckt/X "
                   "pin-arity consistency audit): THIS = net-level fanout / "
                   "floating / power-ground connectivity audit."),
        "tcr_refs": [
            "param_token_excluded_from_nodes_and_subname",
            "subname_is_last_non_param_token_excluded_from_node_count",
            "power_ground_name_rule_case_insensitive_bang_strip_glob",
            "spice_node_0_always_ground_never_floating",
            "global_declared_net_is_power_ground_class_regardless_of_name",
            "plus_continuation_line_join_before_tokenize",
            "duplicate_node_within_one_instance_counts_as_two_connections",
            "comment_and_blank_lines_skip_and_break_continuation",
            "max_fanout_tie_break_lexicographically_smallest",
            "all_output_lists_lexicographically_sorted",
            "verdict_four_way_truth_table_clean_floating_sparse_power_both"
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

# append to jsonl
jsonl = BASE / "EDA-Eval-DesignFlow-Schematic-Netlist.jsonl"
with open(jsonl, "a") as f:
    f.write(json.dumps(case, ensure_ascii=False) + "\n")

# write reference impl
refpath = BASE / "reference" / "EDA-Eval-DesignFlow-Sch-004_impl.tcl"
refpath.write_text(REF)

# report counts
n = sum(1 for _ in open(jsonl))
print(f"appended {case['task_id']} -> {jsonl.name} (now {n} cases)")
print(f"wrote reference -> {refpath.name}")
