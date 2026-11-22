# r1014 Deepread: czfpa — RTL Functional Analysis

**Session**: 1795069783165_czfpa  
**User**: wade1zh @ hfeg0pkn003 (10.129.2.12)  
**mc**: 6, keywords: verilog:8;rtl:5  
**Domain**: digital (A-pure)  
**Trace**: 4 msgs / 2 user / 2 asst / 1 tool_use (very short session)

## User Intent (verbatim)
U#1: `/rundata/lacaa/TV1_TestChips/CXTV1_DBC_CH252_6T/workdir/SoC_wade/src_rtl/CXTV1_ALS_CH252_6T_DBC_testchip.v Analyze the function of this code`

## Session Flow
1. User asks to analyze the function of a Verilog RTL file
2. Agent reads the file via `read_files` tool (CXTV1_ALS_CH252_6T_DBC_testchip.v, 435 lines)
3. Agent produces a prose markdown functional analysis covering:
   - Module structure overview (testchip top-level pad routing + macro array control)
   - Signal port classification (GPIO PAD / Probe PAD, JTAG, address bus, data bus)
   - Two physical interfaces (Bump PAD for package, Probe PAD for CP test)
   - PAD MUX logic (PTRUD4D + TDV + MUX2D1 cells, PAD_GPIO_BYPASS_EN selection)
   - 30x ALS_Macro9M_wrap SRAM macro instances (generate loop)
   - 30-to-1 output MUX (top_msel select)

## Trace Gold
The assistant's prose analysis (msg[3]) is a structured markdown report with:
- Module structure overview (ASCII art diagram)
- Signal port classification tables (Bump PAD vs Probe PAD)
- Main signal groups (JTAG, address, data, control)
- Cell instantiation summary
- Functional sections (GPIO design, Macro sel decode, SRAM instance, output sel)

## Case Reframe
Per 11-15 order, "Analyze the function of this code" is a legitimate analysis-Q&A user intent.
Reframed as a produce-task: "analyze RTL → structured JSON functional report" where the solver
is a Python script that parses any Verilog RTL file and extracts structured info.

**Deliverable**: `analyze_rtl.py <rtl_file> <output_json>` producing JSON with:
- module_name, port_count, ports_by_direction, port_groups, port_group_names
- cell_types (name+count), cell_type_count, total_instances, instantiated_modules
- generate_blocks (label+loop_count), generate_block_count, generate_loop_total
- functional_sections, functional_section_count
- key_assignments, assignment_count, summary

## A Fixture (rtl_A.v)
Real trace file, trimmed to ~170 lines keeping all key structural elements:
- Module: CXTV1_ALS_CH252_6T_DBC_testchip
- 48 ports (42 input / 5 output / 1 inout), groups: GPIO (23) + PAD (25)
- 7 cell types: PTRUD4D_DBC_SV_X(8), TDV_DOWN(8), MUX2D1DBCP51H180L6W25T5LVT(7), BUFFD8DBCP51H180L6W25T5LVT(2), INVD2DBCP51H180L6W25T5LVT(1), TDV_UP(1), ALS_Macro9M_wrap(1)
- 6 generate blocks: gpio_macro_addr_pad(16), gpio_soc_data_inout(144), gpio_soc_Dummy_Output(10), gpio_soc_Dummy_Input(10), gen_ceb(30), macro9m_inst(30)
- 4 functional sections, 3 assign statements

## Hidden B (rtl_B.v)
Synthesized DDR5 PHY top module with completely different structure:
- Module: DDR5_PHY_TOP_wrap
- 24 ports (9 input / 12 output / 3 inout), groups: PHY (12) + MEM (9) + ZQ (3)
- 7 cell types: CLK_PLL(1), CLK_DIV2(1), DIFF_BUFFER(2), LEVEL_SHIFTER(2), DQ_DRIVER(1), DQS_GATE(1), ZQ_CALIB(1)
- 4 generate blocks: dq_lane(8), dqs_lane(4), zq_calib(1), ca_lane(2)
- 5 functional sections, 20 assign statements
- All concrete values differ from A (module name, port names, cell types, generate labels, section titles)

## Anti-Hardcode Anchors (B-specific, not in A)
- module_name: DDR5_PHY_TOP_wrap (vs CXTV1_ALS_CH252_6T_DBC_testchip)
- port_groups: PHY/MEM/ZQ (vs GPIO/PAD)
- cells: CLK_PLL, DQ_DRIVER, ZQ_CALIB, DIFF_BUFFER, LEVEL_SHIFTER, DQS_GATE, CLK_DIV2 (vs PTRUD4D_DBC_SV_X, TDV_DOWN, MUX2D1...)
- generate: dq_lane(8), dqs_lane(4), ca_lane(2), zq_calib(1) (vs gpio_macro_addr_pad(16), macro9m_inst(30)...)
- sections: "1. Clock generation", "2. Address/command path" (vs "1. GPIO design", "1. Macro sel decode")

## Verification
- ref PASS 27/27 (negative_selftest SELFTEST PASS)
- 3 negs FAIL: neg_empty (no output), neg_print_only (hardcodes A values, B mismatches), neg_core_deleted (skeleton returns 0/empty)
- §4.9 three-fake FAIL ✓
- E2E (check.py extracted from jsonl test field) ref PASS + 3 negs FAIL ✓
- A.jsonl 469 → 470

## Selection Notes
- r1014 fresh pool: 645 dedup A-domain candidates → 21 fresh (4-shard ledger diff, 4206 sids)
- Peeked 4 clean A-pure low-mc candidates: ts189(env-config park), mkis4(verilog-A analog B/D park), j3gn0(TB explain+diagram subjective park), czfpa(RTL analyze selected)
- czfpa is the cleanest: A-pure digital, real trace, "Analyze the function of this code" is a legitimate analysis-Q&A → produce-task reframe
- stop-loss: consecutive_zero_case_rounds = 0 (r1013 succeeded → r1014 succeeded)
