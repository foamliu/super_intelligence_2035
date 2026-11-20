# Deep-read: 1793771550244_nlf6u (SramTailorPlanClassify-001)

**trace_source**: e0044979 @ hfeg0pkn001, session 1793771550244_nlf6u.messages.json
- summary.tsv mc=146, keywords: schematic:498/netlist:129/spectre:52/hspice:22/.def:9/synopsys:8/transistor:3/pdk:2
- file: 1.9MB, 236 msgs (no separate .archive.json — the .messages.json IS the full session)
- prior park (2026-11-08 21:5x): "FineSim detect_prep log debug, U#=cat log + testbench-needs-.include root-cause; 暂缓 archive 待查"

## Re-peel trigger
The prior park note explicitly said "archive 待查" (archive to be checked) but the
session is a single 1.9MB .messages.json with no separate archive. Deep peek of
the full 236-msg session was never done — only a shallow U#=cat-log peek.

## User turns (real text only, 13 of 236 msgs)
- **U#1** (ts=1793771550698): "检查这个目录下面： /rundata/.../SRAM_tailor/.../  我跑脚本裁剪电路，但是碰到这个错误：cat .../detect_prep_..._FS.log  ERROR: detect: testbench needs exactly one direct .include defining the conly top 'CXN4HC2PS1024X72M4B4C1R1W1BW1RE1_FS'; found 0" — **debug-paste** (pastes error log)
- **U#2** (ts=1793775419962): "Check the tailor plan at: .../tailor/plan.log  row actions: full_rc 10 rows / 296 cells; conly 38 rows / 2072 cells; prune 976 rows / 73408 cells  cell actions: conly 2072; full_rc 73704; prune 0  ...  You need to read the Python script to understand how tailor plan to work. And check whether cell still keep full_rc" — **CLEAN produce-task** (asks to analyze plan + verify cell classification; does NOT give root cause or fix)
- **U#3** (ts=1793776917147): "In XA toggle report, I didn't see too many BL/BLB with actities. .../xa.toggle  Please check whether the list match" — diagnostic check
- **U#4** (ts=1793781205211): "Check the new toggle report ... I changed the window for XA toggle check, BL/BLB should have no activity. But still got no prune cell." — diagnostic
- **U#5**: "I copied to: .../CXN4HC2PS1024X72M4B4C1R1W1BW1RE1_FS.new"
- **U#6** (ts=1793781923372): "Fix the code with Option A, I've backup the code" — **gives fix direction** → §A-② 排除 A 档
- U#7-U#12: "continue" / "/models" (no content)
- **U#13**: "where is the file 'plan_iface.py' you have modified?"

## Assistant work
- Read detect_prep log, plan.log, map.log, design.json, xa.toggle (272229 nodes), detect.log, output_bindings.json
- Read dspf-tool Python: cli.py, detect.py, detect_bundle.py, probe.py, plan_iface.py, detect_plan.py
- Root cause: 73408 cells all rescued from prune→full_rc because `mapping_not_verified` blocks pruning; `unverified_cells = set(unverified_status) | {cid from device_map WHERE status!='verified'}`
- **Fix (Option A)**: modify plan_iface.py line ~91 — add `AND status NOT IN ('pin_mismatch:S','pin_mismatch:B')` to the device_map query, since 8T bitcell source/bulk nets naturally differ between split (global supply) and conly (instance-prefixed terminal) views
- Produced: find_error.py, analyze_toggle.sh, sed_fix.sed, apply_patch.sh, apply_sed.sh, fix_plan_iface.py, repair.sh (multiple fix-application scripts)

## A档 vs B档 determination
- U#2 = CLEAN produce-task (analyze tailor plan, check cell full_rc status) ✓
- U#6 = "Fix the code with Option A" — user gives fix direction → §A-② 排除 A 档
- → **B-synthesized**

## Case synthesis (EDA-Eval-DesignFlow-SramTailorPlanClassify-001)
- **Domain**: spice_sim (FineSim SRAM tailor plan classification)
- **Layer**: L1 (offline Python: parse TSV/JSON, apply classification rules, write JSON)
- **Deliverable**: sram_tailor_plan_classify.py (CLI: 4 args, stdlib only)
- **Logic**: cell is unverified_blocking iff cell_map or device_map status ≠ verified AND ∉ acceptable_mismatches; row_action=prune + blocking → full_rc (rescued); else keep row_action
- **Assets A**: cell_map.tsv (50 cells), device_map.tsv, rules.json (accept S+B), task_brief.md
- **Hidden B1**: 80 cells, same rules (accept S+B) — generalized counts
- **Hidden B2**: 60 cells, rules accept ONLY pin_mismatch:S (reverse-hardcoding guard; pin_mismatch:B now blocks)
- **Reference**: sram_tailor_plan_classify_ref.py
- **check.py**: 14 conditions (a-n); subprocess-runs candidate on B1+B2; asserts total_cells / final_counts / rescued / blocking / prunable counts; cross-dataset independence
- **Negatives (6)**: naive_empty, hardcoded_a, ref_core_deleted (no exception), only_print, empty_shell (all-prune), no_validate (ignores rules) — all FAIL
- **§4.9 three-fake**: empty_shell→FAIL(e), only_print→FAIL(c), ref_core_deleted→FAIL(e) — all FAIL ✓
- **Assertion gate**: k_rationale=14 == k_check=14 ≥ 8 ✓

## Self-verification
- ref PASS 14/14 (self-test via check.py __main__)
- 6 negatives FAIL (negative_selftest NEG_RC=0)
- §4.9 three-fake all FAIL
- test field in jsonl == check.py on disk (byte-identical)

## Distinction from existing cases
- DspfCapExtractValidate-001 (ckhfh): DSPF parasitic cap extraction + charge-conservation validation (parse .spf geometry). This case = cell-action classification from cell_map/device_map status (parse status tables, apply acceptable-mismatch rule). Different input format, different logic, no overlap.
- NetlistStaticCheck-001 (nj8q4): netlist structural check. This case = tailor plan cell classification. Different domain angle.
