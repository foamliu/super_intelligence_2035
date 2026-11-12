# Deepread: kdjt3 — result_map catalog entry removal

- **trace**: e0039602 @ hfeg0pkn002 (10.129.2.11, autofs via 10.129.8.234), session `1793927996511_kdjt3.messages.json`, mc55, 200KB, 42 msgs, 1 user turn
- **keywords**: verilog:311;netlist:92;drc:25;lvs:6;systemverilog:1 → clean A-dominant digital
- **project**: verilog_lib_trans_v2 (same as r399/r419/r428, different subtask/deliverable)
- **A-faithful**: user gives correct module template but NOT root cause → produce-task 合格. But deliverable = modified result_map (private 26K-line file at /home/e0039602/Documents/verilog_lib_trans_v2/outputs/) → A-faithful INFEASIBLE → **B档 synthesized**

## User turn (U#0, MSG 0)
"请你阅读 /home/e0039602/Documents/verilog_lib_trans_v2/outputs/result_map_20261104_202610_c0ef.txt 这个文件，其中有一个类别的错误，AF_latqn2_CmFsUnit 这种类型的需要：[pasted CORRECT module template — clk/clk0/clk1 clock-safety, trireg (medium) #(1,1,200) Mid, invhiz_base FbM + passg_base FwdM/FwdM1 + inv_base DrvM, fgc_pwrstate_monitor×3, specify block]"

User does NOT state: (1) what's wrong in result_map, (2) where, (3) what action to take. Agent must infer: result_map has a WRONG AF_latqn2_CmFsUnit entry; the correct form is the pasted template (also in reference file simlib_drcoa_digital_copy.sv); the wrong entry should be removed.

## Agent tool chain (deepseek, 22 tool calls)
1. get_agent_policy_status + list_allowed_files (verilog_lib_trans_v2, outputs, netlist_change)
2. run_commands DISABLED → uses run_approved_command (python-runner profile)
3. editor: _analyze_latqn2.py → 279 modules, 1 AF_latqn2_CmFsUnit
4. editor: _analyze_latqn2b.py → CmFsUnit 4 occ, latqn 23 occ (substring vs header distinction!)
5. editor: _analyze_latqn2c.py → full entry (wrong body: vlgTcap #(.tdecay(300)), trireg #(1,1,100), no clk)
6. editor: _analyze_latqn2d.py → exact line structure: target header idx 1192, prev header 1060, next header 1414
7. editor: _remove_latqn2.py → removes lines 1192-1413 (222 lines), 279→278, WROTE file
8. editor: _verify_removal.py → 0 occ AF_latqn2_CmFsUnit/CmFsUnit/vlgTcap, 278 modules, clean boundary
9. editor: _cleanup_scripts.py → removes all 7 temp scripts

## Key reusable logic (the synthesized tool)
- Parse result_map catalog: entries delimited by `# ---- module: <NAME> (行 X-Y) ----` header lines
- Find target entry by HEADER module name (NOT body substring — CmFsUnit appears 4× in body but only 1 module is the target)
- Remove full block: [target_header_idx, next_header_idx - 1] (EOF for last entry)
- Boundary: keep blank line before target header as separator; no double blanks; no merged headers
- Verify: module count before/after, target occurrences 0 after, non-target modules preserved
- Report: before_count, after_count, removed_count, removed_modules, target_found

## Substring trap (key discriminator)
trace: `CmFsUnit` 4 occurrences in body text, but only 1 module NAMED AF_latqn2_CmFsUnit. A naive substring-remover would over-delete; a header-name-based remover correctly removes only the target. → B hidden input will embed target name as substring in a non-target module's body.

## Wrong-signature (A vs B differ)
- A target wrong body: `vlgTcap #(.tdecay(300)) I17`, `trireg (medium) #(1,1,100) Mid`, no clk/clk0/clk1
- B target wrong body: `keeperTcap #(.tdecay(500)) K9`, `trireg (medium) #(1,1,150) Mid`, no clk-safety → cross-input guard defeats hardcoded_A

## Synthesis plan → ResultMapEntryRemover-001 (digital, L1, spec-driven, B档)
- deliverable = `remove_result_map_entry.py` (pure stdlib, CLI --input/--module/--output/--report)
- A = result_map_A.txt (8 modules, target AF_latqn2_CmFsUnit middle, wrong vlgTcap signature)
- B hidden = result_map_B.txt (9 modules, target B_Module_Delta middle, wrong keeperTcap signature, + substring trap in M6 Epsilon body, + M9 last-entry EOF boundary)
- check.py 15 conditions (a-o): zip/py_compile/exit0/output/report/target-header-removed/target-signature-removed/header-count-8/non-target-preserved/substring-trap-intact/boundary-clean/report-fields/cross-input-guard/not-found-handling/determinism
- independent oracle: line-based `startswith("# ---- module:")` + split (vs ref regex)
- negatives: naive_empty / print_only / core_removed (substring-remover, over-deletes Epsilon) / hardcoded_A
