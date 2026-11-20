# Deepread — iuarg (gracew, LPDDR5 compress 14bit DQ feature)

- **session**: `1794639653207_iuarg.messages.json` (gracew @ hfeg0plg92, mc=32, verilog:255 dominant)
- **fetched from**: 10.129.2.10:/home/gracew/.cline/data/sessions/1794639653207_iuarg/ (subdir layout, 289KB, ALIVE)
- **structure**: 47 msgs, 15 user / 12 assistant, tools: read_files×10, editor×3, run_approved_command×3, list_allowed_files×3, ask_question×1, get_agent_policy_status×1
- **4 real user inputs**:
  1. (R0) `/rundata/ddgoa/V0/simdir/verilog/gracew/verilog.lpddr5.ddgoa.net1105/patterns/proj_function/cmds_testmode/cmds_compress/Compress_task.v 请你阅读这个路径下的代码，并给我增加一个功能让dq可以输出14bit`
  2. (R1) paste of the compdqpin output-loop block (compdqpin==0/1/8/9/80/10/98, `for(j=0;j<10;j=j+2)`) + "这是什么意思"
  3. (R2) "你现在写的compress_task如果我想在其他pattern里面使用14bit应该如何使用"
  4. (R3) "不需要将RDBIT8置为0吗" → agent: NO, keep rd_8bit=1 default; rd_8bit and rd_14bit are mutually exclusive paths.

## Real produce-task (R0, trace-faithful)
`Compress_task.v` is a LPDDR5 compress test-mode testbench. `Read_TM` task pushes compressed
data `comp_dq0..3` (each `reg[9:0]`, 10 bit) onto expected DQ `dq_exp` via 12 `compdqpin`
output loops `for (int j=0; j<10; j=j+2) begin`. User wants a 14-bit DQ output feature.

## Agent deliverable (real)
Agent wrote `add_rd14.py` (Python transformer) applying 6 structural edits + `verify_rd14.py`
(structural self-check, 10 checks ALL PASS) + `diff_rd14.py`. Because `/rundata` is read-only
(`writableRoots=/home/gracew`), agent wrote the patched file to `/home/gracew/Compress_task.v`.
6 edits:
1. widen `comp_dq0..3` `reg[9:0]`→`reg[13:0]`
2. add `bit rd_14bit=0` param after `rd_8bit=1`
3. add `integer dqbits;` decl
4. `dqbits = rd_14bit ? 14 : 10;` after `bl = 16;`
5. guard `comp_dqN[9:8]=2'bzz;` (4 lines) with `if(!rd_14bit) begin...end`
6. 12 loops `j<10`→`j<dqbits`; trailing `5*tCK`→`(dqbits/2)*tCK`

## Case synthesized: EDA-Eval-DesignFlow-CompressRd14bitAdd-001
- domain: **verification** (LPDDR5 verilog testbench), L1 (offline Python text transformation)
- archetype: lpddr5-compress-task-rd14bit-switch-adder
- A档 trace-faithful: real user prompt + real Read_TM signature (from session diff) + real loop bodies (from R1 paste)
- Visible A: `Compress_task_A.v` (12 compdqpin loops, real signature/anchors) + task_brief.md
- Hidden B: `Compress_task_B.v` (9 compdqpin loops, DIFFERENT pin values 2/3/11/82/83/1892/1893/21/77, B_SENTINEL_RD14_B) + hidden_manifest.json (expected_loop_count=9, visible_a_loop_count=12)
- Reference: `add_rd14bit.py` (generalized transformer — count-agnostic loop replacement, works on both A=12 and B=9)
- check.py: 12 independent conditions (a–l): zip valid+script / runs on B exit0 / comp_dq width×4 no-residual / rd_14bit param / dqbits decl / dqbits assign / z-fill guard / loop bounds (B==9, no j<10) / trailing timing / B sentinel preserved / 3-seed determinism / non-hardcoded-A (A==12 vs B==9 differ)
- negatives: naive_empty, print_only, hardcoded_A (12-loop fixed output → fails B's 9-loop check), core_removed (omits loop edit → fails loop condition). selftest: reference 12/12 PASS, 4/4 negatives FAIL.
- Self-verify DONE: reference check.py 12/12 PASS; negative_selftest all FAIL as expected.
