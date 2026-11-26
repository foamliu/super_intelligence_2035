# Deepread: 1793068260319_c7kk2 (xinweif @ hfeg0pkn005)

## Trace metadata
- **User**: xinweif
- **Host**: hfeg0pkn005 (10.129.2.14)
- **Session**: 1793068260319_c7kk2.messages.json
- **Match count**: 18 (verilog:39, netlist:20, systemverilog:9, cadence:5, synopsys:4, synthesis:1)
- **Digital-dominant**: digi=69, ana=0 (pure digital/verification)
- **Total messages**: 139, **User turns**: 71 (most are tool_result echoes)

## USER#0 (A-faithful prompt — clean, no root cause/fix given)
> 帮我用verilog写一个验证LPDDR5 command bus training功能的测试激励，该发生什么样的测试激励

Translation: "Help me write a Verilog test stimulus to verify LPDDR5 command bus training functionality, what kind of test stimulus should be generated."

**A-faithful assessment**: CLEAN — user asks open question, gives no root cause or fix. Pure task request.

## Trace evolution
1. Assistant searched web/codebase for LPDDR5 CBT spec
2. Created complete CBT verification environment with 5 SystemVerilog files:
   - `lpddr5_cbt_pkg.sv` — Package: CA_WIDTH=7, DQ_WIDTH=16, tCK=625ps, tWCK=312.5ps, CBT state enum, CA training patterns (A: walking-1, B: walking-0, C: checkerboard, D: all-1/all-0)
   - `lpddr5_dram_model.sv` — DRAM behavioral model: MR23 MRS decoding (enter/exit CBT), CA sampling on WCK rising edge, DQ echo pipeline (tCBT_ECHO_DLY=2 WCK cycles)
   - `lpddr5_cbt_controller.sv` — Controller BFM: Full CBT state machine (IDLE→RESET_WAIT→NORMAL_OP→MRS_MR23_ENTER→CBT_WAIT_MODE→SEND_PATTERN→RECEIVE_ECHO→MRS_MR23_EXIT→TRAIN_COMPLETE/TRAIN_FAIL), CA pattern generation, echo comparison with error counting
   - `lpddr5_cbt_test.sv` — Test program: 9 CBT test scenarios (Pattern A/B/C/D, stress-256, sequential), pass/fail reporting
   - `lpddr5_cbt_top.sv` — Top-level: CK/WCK differential clock generation, reset, DRAM+Controller+test instantiation, VCD dump
3. Assistant struggled with file corruption (editor truncation issues) for ~100 messages
4. Later user turns (MSG#134, #136, #138) asked conceptual CBT questions (training when CA sampling wrong, WCK vs CK sampling)

## Real assets (fetched from host)
- Source: `/home/xinweif/lpddr5_cbt/` on hfeg0pkn005
- Files: lpddr5_cbt_pkg.sv (4258B), lpddr5_dram_model.sv (5019B), lpddr5_cbt_controller.sv (7906B), lpddr5_cbt_test.sv (2843B), lpddr5_cbt_top.sv (2777B)
- Fetched via scp (e0031982 has key-based ssh access to hfeg0pkn005)

## Case synthesis
- **Case ID**: EDA-Eval-DesignFlow-Lpddr5CbtTbGen-001
- **Domain**: verification, **Track**: faithful, **Level**: L2-static
- **Deliverable**: Python generator `gen_lpddr5_cbt_tb.py` that reads JSON config and produces 5 .sv files
- **A config**: LPDDR5-6400 x16 (CA_WIDTH=7, DQ_WIDTH=16, tCK=625ps, tWCK=312.5ps, echo_dly=2)
- **B config (hidden)**: LPDDR5-5300 x8 (CA_WIDTH=7, DQ_WIDTH=8, tCK=938ps, tWCK=469ps, echo_dly=3) — differs in DQ_WIDTH, speed grade, echo delay
- **check.py**: 13 conditions (a-m), including anti-hardcode guards (l: A-run, m: no B literals)
- **Negatives**: 4 (empty_shell→c, print_expected→g, core_deleted→e, hardcoded_b→i) — all FAIL distinct
- **§4.9 three fakes**: empty_shell, print_expected, core_deleted — all FAIL
- **Self-verify**: ref PASS 13/13, all 4 negs FAIL, NEG_SELFTEST PASS
- **Gold**: Parameterized Python generator based on real .sv files from trace

## Cross-shard collision check
- Verified c7kk2 NOT in any shard ledger (A/B/C/D) as case/parked before claiming
- Verified case ID `Lpddr5CbtTbGen` unique across all shard jsonls
- No collision with existing cases
