# r981 deepread: 3h7rx — GDDR7 CAOSC test case generation

**session**: 1794893665850_3h7rx (sqgeng@hfeg0plg18, mc=34, systemverilog:50;rtl:40;netlist:23;verilog:19)
**size**: 1.03MB / 159 msgs / 21 user turns
**domain**: A-pure verification (GDDR7 testbench, UVM, SystemVerilog)

## User intent (verbatim, M#63)
> TB 中没有专门的 CAOSC 测试用例，需要通过 Mrs() + Ird() 命令组合来测试 给我协议个样例吧

## Session main line
GDDR7 testbench (gddr7_tb) exploration + CAOSC test generation. User is new to the TB (learning seq_lib/test_lib structure). 21 turns:
- M#0: read ~/Desktop/gddr7_tb/tb (explore)
- M#7: find CAOSC MR23 OP6 related content in tb
- M#35: list more code
- **M#63**: generate CAOSC test sample via Mrs()+Ird() ← core produce-task
- M#81/M#90: don't write in tb path, output to ~/Desktop/gddr7_code
- M#112/M#116: no Chinese/Unicode (gvim不认) → pure ASCII
- M#132/M#134: mask semantics Q&A + count-measurement-order Q&A
- M#136/M#138/M#142: seq_lib learning guide
- M#143-157: vsim -sr testname, seq_lib vs test_lib Q&A

## Trace gold (M#72-M#131)
1. Agent read gddr7_ca_test.sv + gddr7_cmd_test.sv for template structure
2. Read gddr7_modereg_pkg.sv (MR23_reg_t OP6=CAOSC enable), mctl_drv_commom_task.sv (Mrs_drive CA bus construction, op_mark per-bit write mask), gddr7_common_function.sv (set_value IRA0-68 mapping)
3. Generated gddr7_caosc_test.sv (6644 bytes, 160 lines):
   - class gddr7_caosc_test extends gddr7_base_test + uvm_component_utils
   - report_caosc_count(ch): prints IRA40/41/42 (CAOSC_COUNT_VALUE + CAOSC_COUNT_VALID)
   - read_caosc_count(ch): Ird 40/41/42 + Rnop + nopn(20) + report
   - test_basic_caosc: Stage1 Mrs MR23 OP6=CAOSC_DIS, Stage2 Mrs OP6=CAOSC_EN, Stage3 read_caosc_count
   - test_multiple_reads: read count1, nopn(200), read count2, compare count2>count1
   - test_body: config (mr_use_default=1, Set_freq(10000), tolerance=10), Init, run both tests
4. User: output to ~/Desktop/gddr7_code (not tb), pure ASCII (replaced Chinese comments + Unicode dashes ─/═ with ASCII -/->)

## Case reframe (produce-task)
Deliver `gen_gddr7_feature_test.py <spec.json> <output.sv>` — a generator that takes a GDDR7 feature spec JSON and produces the UVM test .sv. A (visible) = CAOSC spec; B (hidden) = ZQC (ZQ Calibration) spec with different MR/IRA/constants/timing/freq. Check runs gen on B and verifies B .sv structure + anti-leak (no CAOSC names) + pure ASCII + determinism.

## API used (from gddr7_base_test)
- Mrs(.ch,.ma,.op,.op_mark) — write mode register (op_mark = per-bit write-enable mask)
- Ird(.ch,.ird_op) — initiate IRA register read (ird_op 0-68)
- Rnop(.ch) — read NOP
- nopn(.ch,.n,.p_cmd) — N NOP cycles
- Init(.ch) — power-up + reset + MR sync
- m_top_cfg.m_mctl_cfg[ch]: mr_use_default, DQ_compare.tolerance, tWCK, tCAOSCINT, tCAOSCO
- m_top_cfg.Set_freq(.freq)

##选料注
- mc≥10池 (shard_mc.A=10 per r959 stop-loss revert), _a_fresh_cands_r973.tsv 38 still-fresh (of 43), A-domain过滤得17, NEW user sqgeng首选 (3h7rx mc=34 systemverilog:50+rtl:40 clean A-pure verification)
- 与历史case无intent-dup (GDDR7 CAOSC test-gen 是新意图, 之前case覆盖LPDDR5/LPDDR6/DDR5/DDR6)
