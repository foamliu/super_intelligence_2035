# Deepread: r1129 ntu0p — DRAM Sense Margin BL Batch Spec Generator

**Session**: 1795146011560_ntu0p.messages.json
**User**: e0025730 @ hfeg0plg49
**match_count**: 68 (netlist:479; hspice:11; schematic:22; drc:14)
**Domain**: spice_sim
**Date**: 2026-11-24

## Trace Summary (105 msgs)

User e0025730 drives DRAM Sense Margin (SM) full-flow simulation automation via SKILL.md + SM_PARAMS JSON.

### Flow Steps (executed by agent):
1. **Step 0**: Opening confirmation → user confirms
2. **Step 1**: Environment cleanup (07_clear.sh && 06_rm_cell.sh) — exit 1 (no files to delete, normal)
3. **Step 2**: SPF extraction check → user: "是" (already extracted)
4. **Step 3**: SPF sub-file generation (dspf_run.pl -f msax512_O.spf.TYP_98_RCC) — FAILED (No such file), user: skip
5. **Step 4**: Preview SPF products → mismatch.param (512 BL entries, all zeros), dspf_file_temp
6. **Step 5**: Netlist substitution check → user: "否" (not done)
7. **Step 6**: Execute netlist substitution (01_modify_netlist.sh Mat7) → XI_msax512_7 subcircuit name → msax512_spf
8. **Step 7**: Preview netlist → verify line 7121: msax512_spf suffix confirmed
9. **Step 8**: Batch BL test-bench generation (02_test_bench_gen.sh):
   - bla* dirs renamed to blb* (12 dirs: blb2,3,4,5,25b254,255,256,257,blb506,507,508,509)
   - 4 dirs per segment (LEFT: 2-5, CENTER: 254-257, RIGHT: 506-509)
   - toc_*/D*.sp parameters (blblmsaq23, delvtobl, KCT) rewritten per segment
10. **Step 8.1**: Batch path replacement (984 .sp files, sed) — FAILED (sed syntax error), user: skip
11. **Step 9**: LSF batch submission (03_run_jobs_bg.sh) — FAILED (queue fqueueAry permission), user: terminate

### SM_PARAMS (from user prompt):
```json
{
  "PREFIX": "bla", "LEFT_BASE": 2, "CENTER_BASE": 254, "RIGHT_BASE": 506
}
```

### mismatch.param format:
```
.param delvtobl<0>_NsR=0 delvtobl<0>_PsR=0  delvtobl<0>_NsL=0  delvtobl<0>_PsL=0
.param delvtobl<1>_NsR=0 delvtobl<1>_PsR=0  delvtobl<1>_NsL=0  delvtobl<1>_PsL=0
... (512 entries, BL 0-511, all zeros initially)
```

## Reframe

The "produce" aspect is the batch BL test-bench specification generation: given SM_PARAMS and mismatch.param, produce a structured JSON specification of the 12 test-bench directories with their BL indices, segment classification, and mismatch parameters.

## Case: EDA-Eval-DesignFlow-SenseMarginBlBatchSpecProduce-001

- **A** (visible): PREFIX=bla, LEFT_BASE=2, CENTER_BASE=254, RIGHT_BASE=506; mismatch.param all zeros
- **B** (hidden): PREFIX=blb, LEFT_BASE=8, CENTER_BASE=128, RIGHT_BASE=384; mismatch.param non-zero for test-bench BLs (8,9,10,11,128,129,130,131,384,385,386,387)
- **Anti-hardcode**: 5-way difference (PREFIX, 3 bases, param values)
- **check()**: 12 conditions (a-l), ref 12/12 PASS, neg 3/3 FAIL
- **Domain**: spice_sim (DRAM Sense Margin simulation)
- **L1**: pure Python stdlib (re+json), no EDA tool dependency
