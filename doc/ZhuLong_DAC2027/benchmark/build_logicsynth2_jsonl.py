#!/usr/bin/env python3
"""Append LogicSynth-002 (DC WLM multi-bit banking diagnosis) to the LogicSynth jsonl."""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent  # EDA-Flow-Bench repo root
JL = ROOT / "benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow-LogicSynth.jsonl"

prompt = """# Scenario: a digital design team runs Synopsys Design Compiler (DC NXT) logic
# synthesis in WLM (WireLoad Mode) -- i.e. WITHOUT a physical library, so the run
# is NOT topographical. The MB (multi-bit) DFF library (MB2SDF*/MB4SDF*, 2-bit and
# 4-bit cells) IS loaded into target_library, and the synthesis log reports 1128
# candidate multi-bit banks. Yet the final banking report shows 15307 single-bit
# flip-flops, 0 multi-bit flip-flops, banking 0%.
#
# A junior engineer's first instinct is "the MB library wasn't loaded" -- but the
# log clearly shows it WAS loaded. The real root cause is in the flow script:
# the placement-aware banking step is guarded by
#     if {[shell_is_in_topographical_mode]} { identify_register_banks ... }
# and a WLM run never enters topographical mode, so that step is skipped entirely.
#
# You are given a parsed DC log summary as a Tcl dict string with these keys:
#   mb_lib_loaded              (1/0)  -- whether the *_MB_* ccs lib was loaded
#   has_spg                    (1/0)  -- whether compile used -spg (topo mode)
#   banking_gated_behind_topo  (1/0)  -- whether the flow guards banking with
#                                        shell_is_in_topographical_mode
#   num_candidate_banks        (int)  -- candidate banks in *.multibit.components.rpt
#   num_single_bit_ff          (int)  -- single-bit FF count in banking report
#   num_mb_ff                  (int)  -- multi-bit FF count in banking report
#   banking_pct                (float)-- final banking percentage
#   compile_cmd                (str)  -- the compile command used
#
# Implement logicsynth_wlm_multibit_plan(log_summary) that returns a Tcl dict with
# these keys:
#   root_cause            -- a concise English string giving the CORRECT root-cause
#                            diagnosis for why banking is 0%. Must be specific to
#                            the actual cause (see rules below), NOT a generic guess.
#   wlm_can_merge         -- "1" if logical/timing-level multi-bit merging is
#                            possible in this run (MB library loaded AND not in
#                            topographical mode), else "0".
#   enable_script         -- a Tcl command script to ENABLE multi-bit merging in
#                            the CURRENT mode. For a WLM run (has_spg==0) it must
#                            set hdlin_infer_multibit, set_multibit_options, run
#                            compile_ultra (WITHOUT -spg), and report_multibit_banking.
#                            It must NOT use identify_register_banks or -spg (those
#                            are topographical-only and would be wrong in WLM).
#   expected_mb_widths    -- the bit-widths the MB library provides, as a space-
#                            separated string. For this MB lib the answer is "2 4".
#   needs_topo_for_wide_bus -- "1" (wide 32/64-bit bus banking always needs topo).
#
# Diagnosis rules (the test checks these -- a wrong diagnosis fails):
#   * If mb_lib_loaded == 0  -> root cause is "MB library not loaded / missing";
#     wlm_can_merge must be "0".
#   * If has_spg == 1        -> the run IS topographical; identify_register_banks
#     is available. root_cause must mention topographical; wlm_can_merge "0".
#   * If mb_lib_loaded == 1 AND has_spg == 0 AND banking_gated_behind_topo == 1
#     AND num_mb_ff == 0     -> THIS is the real trap: root_cause must mention
#     "topographical" AND "identify_register_banks" (the placement-aware banking
#     was skipped because the flow gates it behind topo mode and this run is WLM).
#     root_cause must NOT claim the library is "not loaded" or "missing" (it IS
#     loaded). wlm_can_merge must be "1". The WLM enable_script must use
#     hdlin_infer_multibit + set_multibit_options + compile_ultra (no -spg) +
#     report_multibit_banking, and must NOT contain identify_register_banks or -spg.
#
# Return the dict via `dict create` so the keys are enumerable with dict get."""

test = '''# assert shim: the runtime Tcl has no native 'assert' command.
proc assert {cond msg} {
    set ok [uplevel 1 [list expr $cond]]
    if {!$ok} { error "ASSERT FAIL: $cond -- $msg" }
}
proc contains {haystack needle} { return [expr {[string first $needle $haystack] >= 0}] }
proc notcontains {haystack needle} { return [expr {[string first $needle $haystack] < 0}] }

proc check {candidate} {
    # Case A: REAL session -- WLM, MB loaded, topo-gated banking skipped -> 0%
    set sumA "mb_lib_loaded 1 has_spg 0 banking_gated_behind_topo 1 num_candidate_banks 1128 num_single_bit_ff 15307 num_mb_ff 0 banking_pct 0.0 compile_cmd {compile_ultra -gate_clock -scan}"
    set dA [$candidate $sumA]
    set rcA [dict get $dA root_cause]
    set esA [dict get $dA enable_script]
    set wmA [dict get $dA wlm_can_merge]
    set ewA [dict get $dA expected_mb_widths]
    set ntA [dict get $dA needs_topo_for_wide_bus]
    assert {[string length $rcA] > 0} "A: root_cause empty"
    assert {[contains $rcA "topographical"]} "A: root_cause must mention topographical mode (real cause)"
    assert {[contains $rcA "identify_register_banks"]} "A: root_cause must mention identify_register_banks"
    assert {[notcontains $rcA "not loaded"]} "A: root_cause must NOT claim library not loaded (it IS loaded)"
    assert {[notcontains $rcA "missing"]} "A: root_cause must NOT claim library missing"
    assert {[string equal $wmA "1"]} "A: wlm_can_merge must be 1 (MB loaded + WLM)"
    assert {[string equal $ewA "2 4"]} "A: expected_mb_widths must be 2 4"
    assert {[string equal $ntA "1"]} "A: needs_topo_for_wide_bus must be 1"
    assert {[contains $esA "hdlin_infer_multibit"]} "A: enable_script must set hdlin_infer_multibit"
    assert {[contains $esA "set_multibit_options"]} "A: enable_script must set set_multibit_options"
    assert {[contains $esA "compile_ultra"]} "A: enable_script must run compile_ultra"
    assert {[contains $esA "report_multibit_banking"]} "A: enable_script must report_multibit_banking"
    assert {[notcontains $esA "identify_register_banks"]} "A: WLM enable_script must NOT use identify_register_banks (topo-only)"
    assert {[notcontains $esA "-spg"]} "A: WLM enable_script must NOT use -spg (topo-only flag)"

    # Case B: counter -- MB library NOT loaded -> must say library not loaded
    set sumB "mb_lib_loaded 0 has_spg 0 banking_gated_behind_topo 1 num_candidate_banks 0 num_single_bit_ff 5000 num_mb_ff 0 banking_pct 0.0 compile_cmd {compile_ultra -gate_clock -scan}"
    set dB [$candidate $sumB]
    set rcB [dict get $dB root_cause]
    set wmB [dict get $dB wlm_can_merge]
    assert {[contains $rcB "library"]} "B: root_cause must mention library"
    assert {[contains $rcB "not loaded"]} "B: root_cause must say library not loaded"
    assert {[string equal $wmB "0"]} "B: wlm_can_merge must be 0 (MB not loaded)"

    # Case C: topo mode (has_spg==1) -> identify_register_banks available, not WLM
    set sumC "mb_lib_loaded 1 has_spg 1 banking_gated_behind_topo 1 num_candidate_banks 100 num_single_bit_ff 8000 num_mb_ff 0 banking_pct 0.0 compile_cmd {compile_ultra -gate_clock -scan -spg}"
    set dC [$candidate $sumC]
    set rcC [dict get $dC root_cause]
    set wmC [dict get $dC wlm_can_merge]
    assert {[contains $rcC "topographical"]} "C: root_cause must mention topographical"
    assert {[string equal $wmC "0"]} "C: wlm_can_merge must be 0 (topo mode, not WLM)"

    return "CHECK_PASS"
}'''

entry = {
    "task_id": "EDA-Eval-DesignFlow-LogicSynth-002",
    "prompt": prompt,
    "entry_point": "logicsynth_wlm_multibit_plan",
    "test": test,
    "metadata": {
        "task_name": "diagnose DC NXT WLM-mode 0% multi-bit banking + emit WLM enablement script",
        "direction": "logic_synth",
        "scenario": "Design Compiler WLM (non-topographical) synthesis multi-bit banking failure root-cause + fix",
        "layer": "L2",
        "topic": "wlm-multibit-banking-diagnosis",
        "difficulty": "medium",
        "design": "DC NXT hplp flow, MB lib (MB2SDF/MB4SDF) loaded, WLM compile_ultra (no -spg), banking 0% with 1128 candidates",
        "tcr_refs": [
            "root_cause_diagnosis",
            "topographical_vs_wlm_mode",
            "identify_register_banks_topo_gate",
            "hdlin_infer_multibit",
            "set_multibit_options",
            "compile_ultra_spg_flag",
            "mb_library_loaded_check"
        ],
        "heavy": False,
        "wall_time_sec": 1.0
    },
    "mode": "design_flow",
    "runtime": {"lang": "tcl", "host": "waveview"},
    "attachments": [
        {
            "name": "dc_log_summary.txt",
            "source": "EDA-Eval-DesignFlow-LogicSynth-002/dc_log_summary.txt",
            "desc": "parsed DC NXT synthesis log summary (desensitized) for the real WLM 0%-banking case: MB lib loaded, 1128 candidate banks, 15307 single-bit FF, 0 MB FF, compile_ultra without -spg, banking gated behind shell_is_in_topographical_mode"
        }
    ],
    "budget": {"max_turns": 40, "wall_time_sec": 1800}
}

# append
lines = JL.read_text().splitlines() if JL.exists() else []
# de-dup guard
existing_ids = set()
for ln in lines:
    ln = ln.strip()
    if not ln:
        continue
    try:
        existing_ids.add(json.loads(ln)["task_id"])
    except Exception:
        pass
if entry["task_id"] in existing_ids:
    print(f"SKIP: {entry['task_id']} already in {JL.name}")
else:
    with open(JL, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"APPENDED: {entry['task_id']} -> {JL}")

# verify parse
n = 0
for ln in JL.read_text().splitlines():
    if ln.strip():
        json.loads(ln); n += 1
print(f"total entries in {JL.name}: {n}")
