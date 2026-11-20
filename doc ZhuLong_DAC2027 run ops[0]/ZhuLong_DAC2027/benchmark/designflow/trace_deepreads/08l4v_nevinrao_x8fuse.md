# deepread — 08l4v nevinrao X8 fuse pattern (r283 fresh-window scan)

## trace
- session: `1794207576508_08l4v` (nevinrao@hfeg0pkn001 / 10.129.2.10)
- size: 1.96MB, 193 msgs, 150 digital markers (verilog/xmsim/rtl/sdc)
- discovery: **fresh-window direct scan** (r283 pivot) — `find /home/*/.cline/data/sessions/ -newermt '2026-11-06 00:00:00'` on active hosts. nevinrao is a verilog test-pattern engineer (LPDDR5 fuse/testmode). This session was NOT in the stale 11/05 scan window's digital pool (shard A had 15 consecutive "pool exhausted" mgmt rounds r268-r282 checking only the 11/05 scan + daily cron log).

## USER#1 (verbatim, A-faithful produce-task)
> 我目前想验证电路X8模式的信号是否有效，思路是通过fuse blownX8使能的相关信号，我验证时候查看有没有正常拉起，你可以参考其他fuse相关的pattern，相关路径为/proj/ddgoa/V0/simdir/verilog/nevin/verilog.lpddr5.ddgoa.20261106/patterns/proj_function/cmds_testmode/cmds_fuse/请你给我一个专门针对cm1_fc_X8<1:0>的pattern，要求无比正确，仿照相关pattern写法

CLEAN A-faithful: user states goal (verify X8 mode via fuse blown), asks for a pattern, points to reference dir, NO root cause / fix given. ✓

## assistant workflow
1. read existing cmds_fuse patterns (TM_fuse_inc.v, TM_inc.v, option_fuse_addr, OptionFuse_random_table) to learn conventions
2. created `/home/nevinrao/TM_X8FuseCheck.v` (golden) — `task TM_X8FuseCheck(integer entry_mode=0, integer nnop=0)`:
   - Enable_TM → Load_TestMode(FSPGMPRO0/1/2, LOADCMEN, TDQEN) → Deselectn → compare_disable
   - blow cm1_fc_X8<0> + <1> via `blownoptionfuse(.entry_mode,.doreadfuse,.contin_parm,.exit_afprog,.fusename,.fusebit,.casesense)` (real-chip) or `force ...fuse_val=1` (RTL-sim `ifndef NOCHIP/`else)
   - randcase optional cm1_sc_DataSCmosX8Ctrl; `if(dutconfig.bytemodemrfuse)` optional cm1_fc_MRConfig
   - BlownFuse(.exit_afprog(1)) → settle `case(`PROJ_NAME)` → Exit_TM → compare_enable
3. user reported compile error `ncvlog *E,NANDFP Named argument not defined`; assistant diagnosed TWO bugs:
   - `.fullmatch(1)` not in formal args → removed
   - `.run` calls `TM_X8FuseCheck(.entry_mode(1),.nnop(TM_CYCLE))` but task lacked `nnop` param → added `integer nnop=0`
4. final golden = on-disk `/home/nevinrao/TM_X8FuseCheck.v` (5433B, readable via ssh as e0031982)

## case build (r283)
- case_id: `EDA-Eval-DesignFlow-X8FusePatternGen-001` (verification, track=A faithful, L1-static)
- deliverable: `gen_fuse_check_pattern.py <spec.json> <output.v>` (generator script — generalizes to hidden B)
- A (SUT sees): spec_a.json (X8, 2 bits, optional DataSCmosX8Ctrl+MRConfig) + ref_pattern_a.v (conventions) + calling_convention_a.run (.nnop) + prompt.txt (USER#1 verbatim) + task_brief.md
- hidden B: spec_b.json (X4, 1 bit, different force path Seg18/ChanEdgeR_7781/EfuseCell_X0Y7, different settle delays, extra `extra` param) + calling_convention_b.run
- check.py: 14 conditions a-n (zip extractable / generator runs on B / task sig entry_mode+extra_params / blownoptionfuse for B target / NO .fullmatch / Enable_TM / Load_TestMode 5 TMs / BlownFuse exit_afprog(1) / Exit_TM / ifndef NOCHIP force path B / randcase / begin=end balance + 1 endtask / Deselectn>=3 + compare_disable+enable / 3-seed deterministic)
- negatives: neg1_noop / neg2_hardcode(X8, fails on X4 B) / neg3_stub / neg4_fullmatch(bug) + fake_empty / fake_print / fake_core
- self-verify: ref PASS 14/14 + 7 negs ALL FAIL (NEG_RC=0) + assertion gate 14==14>=8 PASS
- test_sha8=332a1bbf; appended EDA-Eval-DesignFlow_A.jsonl (181→182); ledger mark 08l4v→case

## why this case works
- fresh-window scan broke the 15-round "pool exhausted" stall (shard A had been checking only the static 11/05 scan + daily cron log, both stale)
- A-faithful: prompt is USER#1 verbatim, no synthesized task rewrite
- anti-hardcoding: deliverable is a generator script tested on hidden B (X4≠X8), so a hardcoded X8 pattern fails (neg2_hardcode FAIL on d/b)
- the .fullmatch bug + .nnop calling-convention are real trace facts encoded as check conditions (e/d/e/c)
