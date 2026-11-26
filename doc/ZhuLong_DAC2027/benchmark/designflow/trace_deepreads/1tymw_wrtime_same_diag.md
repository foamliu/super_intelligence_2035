# Deepread: 1tymw (t0002616@hfeg0plg101, mc40, schematic_netlist)

**Session**: 1794208561548_1tymw (10.129.8.233), 24 msgs, 1.27MB
**User**: t0002616
**Date**: 2026-11-09
**Domain**: schematic_netlist (SPICE deck analysis)

## User intent (逐字原话)
USER#0 (MSG0): `为什么fast和fastest后缀的两个.sp文件算出的wr_time是一样的`
- Attached: SAtest_wiArray_fast.sp (6493B, 144 lines) + SAtest_wiArray_fastest.sp (6620B, 147 lines)
- Also in uploads: netlist (1.1MB), wr_data_mid1.sp, wr_data_all1.sp, ideal_stimulus.sp, pattern_power.sp, EDR_261103.inc

## Assistant diagnosis (MSG23 final, 逐字原文要点)
### 结论
两个 .sp 除了**一行 include 的写数据文件不同**外，其余完全一样；WR_time 只盯**固定一个 cell** 的写 1 翻转，这个 cell 在两个文件里收到的写激励**完全相同**，所以 WR_time 一样。

### 证据
1. **功能差异只有一处**：逐行 diff，除去注释（`*.` 开头），唯一生效差异：
   - `.inc '.../wr_data_mid1.sp'` (fast: Mid write 1, Other 0 — 只有 bit3 写 1)
   - `.inc '.../wr_data_all1.sp'` (fastest: All 0 write 1 — 全部写成 1)
   - `*.lib tt/ss` 行是注释（`*` 前缀），不生效。`.alter` 块两文件都有 tt/ss/ff。

2. **WR_time 测固定 cell**：
   - `.meas tran WR_time trig v(mat0_bla_tar<19>,mat0_blb_tar<19>) val='0' ... targ v(xi0.xi_mat0.xi_submatsldl_first.xi_kcellx32mdl_m_4.cc32)='pvblh*0.95' ...`
   - 被测 cell: `xi_kcellx32mdl_m_4.cc32` (mid 块)
   - 初始值: 0 (`.IC V(CC32)=KCTDD`, `.param KCTDD='0'`)
   - 测的是它被写成 1、节点充到 pvblh*0.95 的时间

3. **为什么相同**：
   - mid1: `mat0_yio<3>`=1, 其余 yio=0
   - all1: 所有 `mat0_yio<k>`=1 (包括 yio<3>)
   - 被测 cc32 从 0→1 翻转 → 它所在列**必然是写 1 的列 (yio<3>)**
   - yio<3> 在 mid1 和 all1 里**都是写 1，波形完全一样**
   - 区别只发生在**其它列** (mid1 写 0、all1 写 1)，这些独立 bitcell 不影响被测 cc32

### 建议
- fast/fastest 不是不同 corner，只是写数据花样不同
- 想看 corner 差异应改 `.alter` 的 `.lib`，不是改 `wr_data`
- 想观察 mid1/all1 差异应看被不同写的列的测量

## wr_data 文件差异
- **wr_data_mid1.sp** (19 lines): "Mid write 1 Other 0" — yio<3> (mat0+mat1) writes 1 (pvblh→pvss→pvblh), yio<0,1,2,4,5,6,7> write 0 (stay pvblh)
- **wr_data_all1.sp** (20 lines): "All 0 write 1" — ALL yio<0-7> (mat0+mat1) write 1 (pvblh→pvss→pvblh)

## Case design (套 #254 v2 deck-grounded debug→diagnosis reframe, 同族 9imo1/7sgr2)
- **Reframe**: deck-grounded wr_time-same root-cause diagnosis tool (读两 .sp deck + wr_data + cell_map + question → 结构化 JSON 诊断)
- **Data-driven 2×2+degenerate**:
  - A (real): comment-diff (*.lib) + stimulus identical → "same because stimulus identical, comment inactive"
  - B1: functional timing-param diff + stimulus identical → "should differ due to timing param"
  - B2: comment-diff (*.lib) + stimulus DIFFERS → "should differ due to stimulus diff"
  - B3: identical files → "no difference to explain"
- **check.py 15 cond a-o**: zip/py_compile/B1 exit+keys/B1 functional-diff-id/B1 conclusion/B1 grounding/B2 exit+keys/B2 functional-diff-id/B2 conclusion/B2 stimulus-diff-id/anti-hardcode/B3 graceful/B3 grounding/question-verbatim/3-seed-determinism
