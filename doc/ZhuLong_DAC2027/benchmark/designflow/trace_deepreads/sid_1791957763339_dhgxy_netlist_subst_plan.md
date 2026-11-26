# Deep-read: 1791957763339_dhgxy — netlist cell substitution planner (schematic_netlist)

- **trace**: `1791957763339_dhgxy` · user `e0039602` · host `10.129.8.136` · mc=91 · 74 msgs · 189KB
- **domain**: schematic_netlist (Verilog netlist cell substitution + 4-state equivalence verification)
- **tool profile**: list_allowed_files 1, read_files 2, search_codebase 2, editor 9, run_approved_command 7
- **session path** (remote): `/home/e0039602/.cline/data/sessions/1791957763339_dhgxy/1791957763339_dhgxy.messages.json`
- **workdir** (remote): `/home/e0039602/Documents/netlist_change_copy/` (contains `netlist` + `simlib_base.sv`)

## Real task (user turns, verbatim)
1. `你现在在哪个文件夹下，文件夹当中有哪写文件` — list cwd
2. **(produce turn, A-faithful candidate)** `请修改 netlist 文件。其中有些模块用到的 cell 在 simlib_base.sv 中不存在，无法直接读取，请结合 simlib_base.sv 把它们替换掉。` + detailed constraints:
   - 优先复用 simlib_base.sv 中【自带电源/衬底引脚】的物理单元积木
   - 凡是有"延时/时序/驱动强度"等物理效应的部分，必须用库内物理单元实现，并把 vcc_/vss_/vbulkp_/vbulkn_ 等电源与衬底脚真实接进这些物理单元
   - 凡是对输出没有延时、没有物理影响的纯逻辑输入合并，一律直接用 位与 &（或 |、^ 等）逻辑表达式在这个物理单元的前端拼接完成
   - 🚫 不要用纯行为/无电源脚的 UDP 原语
   - 🚫 尽量不要把每个 NAND 输入都做成独立的 pp/nn 晶体管串并联堆
   - 每个被替换的 cell，先用真值表和器件原理分析，再用 simlib_base.sv 里的物理单元 + & 组合式地复原出逻辑功能
   - 改写时保留原 cell 的所有参数与连接关系（电源脚、衬底脚、端口名都要保留）
   - 输出要求：在对话窗口打印每处被替换的原始行和替换后的行；**无须实际改写 netlist 文件**；最后用真值表穷举（含保持态/上一值）验证替换前后等价
3. `在完成我这个任务过程中，你生成了哪些脚本来辅助` — Q&A (meta)
4. `你是如何扫描netlist文件来判断哪些需要转换呢` — Q&A (method)
5. `simlib_base.sv 里我看到里面只有约 8 行真正是带电源/衬底脚的物理基础单元...` — Q&A (clarify)

> U#2 is the produce turn (提出需求/表达目标). U#3-5 are follow-up Q&A (not used as A-faithful task).

## Real assets
- `netlist` (153 lines, 5 modules from Aether schematic export). **Target module** = first: `IO_rsnand21nand31_DL_ACT_MERGE_READ` (ports Y/R0/R1/S/inh_vcc/inh_vbn/inh_vbp/inh_vss; instances `nand2IOLVx2 I6` + `nand3IOLVx2 I0` forming cross-coupled SR latch Y↔net16). Other 4 modules (T_invLVx1_OSEY1/T_inv_f3NORMSsub/PWY_mxi2_TrimA_cvps/D_latqn_ffRdBlk1) use invDSx1/invenLVSx1/invCS/invhizCS etc — NOT the focus.
- `simlib_base.sv` (71785 bytes, 25 modules). Key physical cell: `inv_base( Y, A, vbulkn_, vbulkp_, vcc_, vss_ )` — single-stage inverter with pp/nn transistors + power/bulk pins. Other power cells: invYx_base, fbenr_base/fbr_base/fbens_base/fbs_base/fbrs_base/fbsr_base, inven_base, invhiz_base, passg_base, dlyrc_base. NO nand2/nand3/nor2/and2 gate cells in lib.

## Real gold output (assistant produced, msg#27)
- **missing_cells** = {nand2IOLVx2, nand3IOLVx2} (set difference: netlist inst cells − lib modules)
- **Substitution 1**: `nand2IOLVx2 I6 (.Y(Y), .vbn(inh_vbn), .vbp(inh_vbp), .vcc(inh_vcc), .vssz(inh_vss), .A(S), .B(net16));` → `inv_base I6 (.Y(Y), .A(S & net16), .vbulkn_(inh_vbn), .vbulkp_(inh_vbp), .vcc_(inh_vcc), .vss_(inh_vss));` (NAND2 = ~(A&B) = inv(A&B), & merges 2 inputs)
- **Substitution 2**: `nand3IOLVx2 I0 (.Y(net16), .vbn(inh_vbn), .vbp(inh_vbp), .vcc(inh_vcc), .vssz(inh_vss), .A(R1), .B(R0), .C(Y));` → `inv_base I0 (.Y(net16), .A(R1 & R0 & Y), .vbulkn_(inh_vbn), .vbulkp_(inh_vbp), .vcc_(inh_vcc), .vss_(inh_vss));` (NAND3 = ~(A&B&C) = inv(A&B&C))
- **Power port map**: vbn→vbulkn_, vbp→vbulkp_, vcc→vcc_, vssz→vss_ (all 4 preserved)
- **Verification**: Part 1 — 4-state (0/1/x) exhaustive per gate (nand2: 9 combos, nand3: 27 combos), orig vs new all match. Part 2 — cross-coupled latch hold-state, 32 states (S,R1,R0 × init Y,net16), steady-state all match.
- Helper scripts (_grep_modules.py, _verify.py, _cleanup*.py) created + cleaned up.

## Extracted verifiable core (case NetlistSubstPlan-001, B-synthesized, L1-boundary)
A-faithful feasible (real netlist + real lib are text, portable) BUT the deliverable per user = a printed report (no file rewrite) + truth-table verification. For design_flow contract (entry_point=outputs/submit.zip), facet = **netlist cell substitution planner script**: `netlist_subst_planner.py --netlist <v> --lib <sv> --outdir <dir>` → `report.json` (missing_cells + available_power_cells + substitutions[original_line/replacement_line/gate_function/logic_expr/port_map] + verification[per_gate 4-state exhaustive + latch hold-state] + summary). check() runs script on hidden B (NOR-based, different lib port names) + B2 (single gate, no latch), verifies 16 conditions a–p. L1 (pure stdlib Python, no live EDA binary).

## Specs
- **A (visible)** `assets/.../netlist_A.v`: real first module IO_rsnand21nand31_DL_ACT_MERGE_READ (nand2IOLVx2 I6 + nand3IOLVx2 I0, SR latch Y/net16, power inh_vcc/inh_vss/inh_vbn/inh_vbp). `simlib_base_A.sv`: real lib (inv_base with vbulkn_/vbulkp_/vcc_/vss_ + 24 other modules).
- **B (hidden)** `hidden/netlist_B.v`: module IO_rsnor2nor3_DL_X (nor2IOLVx2 I3 + nor3IOLVx2 I7, SR latch Q/QB, signals SET/R2/R1, power pw_vdd/pw_gnd/pw_vbn/pw_vbp). `simlib_base_B.sv`: synthesized lib (inv_base with ports Y/A/VBN/VBP/VDD/GSS + switch/nn/pp/alias_short). NOR→inv(|), power map vbn→VBN/vbp→VBP/vcc→VDD/vssz→GSS.
- **B2 (hidden)** `hidden/netlist_B2.v`: module NAND2_SUB_X (single nand2IOLVx2, no latch, no feedback). lib_B2 = lib_B. Tests no-feedback branch (latch_hold.feedback_detected=false).

## Anti-hardcode axes (6)
cell name (nand2/nand3 vs nor2/nor3) / signal name (Y/net16/S/R1/R0 vs Q/QB/SET/R2/R1) / power port convention (vbulkn_/vbulkp_/vcc_/vss_ vs VBN/VBP/VDD/GSS) / gate operator (& vs |) / latch presence (cross-coupled vs single gate) / module name. A-literals banned in script source: nand2IOLVx2/nand3IOLVx2/Y/net16/S/R1/R0/inh_vcc/IO_rsnand21nand31.

## Judge (check.py): 16 conditions a–p
a zip+py_compile / b run B exit0+report.json / c top-level keys / d missing_cells==setdiff / e n_subst==n_missing / f replacement_cell in lib + has power/bulk ports / g logic_expr functional correctness (4-state truth table) / h port_map preserves 4 power nets semantically / i original_line matches netlist / j per_gate all_match / k latch_hold all_match + feedback_detected / l summary.equivalence_holds / m cross-input report_B2≠report_B (module + cells + feedback) / n anti-hardcode no A-literals / o determinism sha256 stable 2x / p neg selftest all FAIL.

## Self-verification
ref PASS 16/16 expected. Negatives (empty/print_fixed/hardcode_a/core_deleted/naive_stub/no_power_map) all FAIL. §4.9 three fakes FAIL. k_rationale=k_check=16≥8 ✓.
