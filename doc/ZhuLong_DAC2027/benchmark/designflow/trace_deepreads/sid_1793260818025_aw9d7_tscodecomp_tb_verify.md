# Deep-read: aw9d7 — Ras_Tscodecomp TB Verify

**Session**: 1793260818025_aw9d7 · **User**: dsgao · **Host**: hfhds201 · **Date**: ~2026-10-28
**Domain**: spice_sim · **Track**: A-faithful · **Level**: L1 (portable)

## User verbatim (A-档)
U#0: `/proj/drcpa/V0/workdir/dsgao/simulation/drcpa_work_Ras_Tscodecomp_schematic_ALPS/netlist   xie yi ge tb qu yanzheng zhe ge dian lu yong finesim fangzhen`
(pinyin: 写一个tb去验证这个电路用finesim仿真 = "write a TB to verify this circuit using finesim simulation")

**A-档判定**: CLEAN ✓ — 纯需求轮（给目标+输入网表路径, 未给根因/修复）

## Circuit: Ras_Tscodecomp
3-bit temperature code comparator:
- Inputs: A<2:0> (cm1_ro_TsLT), B<2:0> (cm1_ro_TsHT), C<2:0> (ts reference)
- Outputs: HT, LT, NT (1-of-3 temperature-region decode)
- Logic: X=(A<C), Y=(B<C); HT=X&Y; LT=~(X|Y); NT=X^Y
  - HT = both A,B < C (high temp region)
  - LT = both A,B ≥ C (low temp region)
  - NT = mixed (one <C, one ≥C)

## Assistant work
1. Explored netlist dir, read netlist (21KB real DRAM circuit with ntn_lv/ptn_lv models)
2. Found 10G5 model library (G5_CIP_Model_D5_v0d5_Rev03_t01, SS corner, -40C, pvcc=0.98)
3. Wrote `analyze_ras.py` to derive boolean function: F(A,C)=(A<C)
4. Created 3 testbenches: TM_verify_TsLT_TsHT.sp, TM_verify_SaNPCtrl.sp, TM_verify_Ts2SaNP.sp
5. Ran Finesim (fixed shrink=0.256, LD_LIBRARY_PATH issues)
6. All 3 TBs PASS (0 mismatches over 512 combos)
7. verify_TM.py confirmed HT/LT/NT logic correct

## Testbench structure (TM_verify_TsLT_TsHT.sp, 2764 chars)
- Finesim options: proxd mode, PARHIER=LOCAL, scale=1, measout=1
- Model: G5_CIP SS corner, .temp -40, pvcc=0.98
- Supplies: VCC=0.98, VSS=0, VBN=0, VBP=0.98, VISO=1.4, VWL=3.4
- DUT: XUT instantiates Ras_Tscodecomp with A<2:0>, B<2:0>, C<2:0> → HT/LT/NT
- 9-bit counter: 512 PULSE combinations (A2 period=512*t0, ..., C0 period=2*t0)
- .tran 10p 10240n, .probe v(HT) v(LT) v(NT)

## Gold standard
All 3 TM_verify testbenches PASS Finesim simulation. HT/LT/NT logic verified correct for all 512 input combinations.

## Case design
- **Deliverable**: `outputs/submit.zip` containing a .sp testbench
- **A**: synthetic netlist_A.sp (CMOS gate-level 3-bit comparator, TT/25C, pvcc=1.0)
- **Hidden B**: netlist_B.sp (same logic, SS/-40C, different sizing l=45n vs 60n, pvcc=0.92)
- **Check (k=12)**: parse TB structure + Python logic verification of 512 combos
- **Negatives**: 5 stubs (empty/print_only/hardcode_B/no_dut/core_cut) all FAIL
