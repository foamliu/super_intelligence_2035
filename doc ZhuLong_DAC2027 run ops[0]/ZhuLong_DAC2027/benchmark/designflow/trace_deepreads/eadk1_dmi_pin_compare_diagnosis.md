# deepread: eadk1 — DMI pin compare error 根因诊断

- **session**: 1794382021638_eadk1 (alanji / hfeg0plg99 / digital / mc32)
- **trace**: 68 msgs, deepseek-v4-flash, status=failed
- **user 原话 (U#1)**: `/rundata/.../table234_rdc_rff_1.x16/A_Pattern_Sim.v 分析这个pattern为什么会报 DMI pin 比较error .`
- **user 贴出的 error (U#2)**:
  - `at 1723903 ps, DUT_RDQS_c:z, Exp_RDQS_c:11 (11)`
  - `at 1723903 ps, DUT_RDQS_t:z, Exp_RDQS_t:0 (0)`
  - `at 1724970 ps, DUT_DMI  :z, Exp_DM  :0 (0)`
  - `at 1724970 ps, DUT_DQ   :z, Exp_DQ   :101010101010101 (101010101010101)`
- **user (U#3)**: 给出 `A_Compare.rpt` 路径

## trace agent 行为
read_files 读了 A_Pattern_Sim.v / A_Compare.rpt / A_Summary.rpt / compare_tasks.sv / lpddr5_specdef.sv / lpddr5_test.sv / Pattern_tasks.v 等, 追踪 MR13 配置 + compare 逻辑 + RDC/MRR 序列, 最终给出根因分析 (msg65)。

## 从真实文件复核的关键事实 (从 trace tool_results 抽取, /rundata permission denied 不可直读)

### A_Pattern_Sim.v
- j41=1 → `pDMD = 'b0010_0000` (OP_DMD_EN) → MR13[5]=1 DMD enable
- j51=1 → `Load_Mode(.ma(MA_DMICtrl), .op(OP_DMICtrl_Mode2))` → MR13[4]=1 DMI IO Control = Mode2
- j31=0 → `pDBIRD = 'b0000_0000` → DBI-RD OFF
- j21=0 → DBI-WR OFF; j11=0 → RDCFE OFF; j01=0 → RECC OFF
- `compare_enable("all")` (line 40 & 130)
- pattern: `BG_Basic_ACT_WR_RD_RDC_MRR`
- `RDC(.enops(0))` → `PrechargeAll`

### A_Compare.rpt
- `j01:0,j11:0,j21:0,j31:0,j41:1,j51:1 at 1143887 ps`
- `BG_Basic_ACT_WR_RD_RDC_MRR at 1687148 ps`
- error 行同 U#2

### A_Summary.rpt
- `Failed: >>> BG_Basic_ACT_WR_RD_RDC_MRR DQ_Err:1, RDQS_t_Err:1, RDQS_c_Err:1, DM_Err:1`

### lpddr5_specdef.sv (line 579-582)
- `MA_DMICtrl = MR13`, `OP_DMICtrl_BITS = 'b0001_0000`
- `OP_DMICtrl_Mode1 = 'b0000_0000` (default, DMI high-Z in read when DBI-RD off)
- `OP_DMICtrl_Mode2 = 'b0001_0000` (DMI = DM output during read when DBI-RD off)
- `MA_DMD = MR13`, `OP_DMD_EN = 'b0010_0000`

### compare_tasks.sv (dm_compare_report block, line 442-479)
- `dm_genexp[i] = ... gencompare_expdata(.data_type(dm_compare.ignoreval), .dut_data(PDRIVER.DMI[i]), .out_data(dm_out[i]), .exp_data(dm_exp[i]), ...)`
- `dm_err[i] = ((dm_genexp[i]===PDRIVER.DMI[i])?0:1) & dm_compare.compareflag`
- `$fdisplay(fd_compare,"at %0t ps, DUT_DMI  :%0b, Exp_DM  :%0b ...", PDRIVER.DMI, dm_genexp, dm_exp)`
- `compare_enable("all")` → `dm_compare.compareflag = 1'b1` (line 137/142/149)

### lpddr5_test.sv
- RDC task: ACT → WR → RD → RDC → MRR 序列; MRR 只驱动 DQ, 不驱动 DMI

## 根因 (trace agent 结论, 经文件复核结构一致)
在 `DMI IO Control = Mode2` + `DBI-RD = OFF` 配置下:
- 正常 Read: DMI 应输出 DM(=0)
- MRR (Mode Register Read): DUT 只驱动 DQ, DMI 保持高阻 z
- 但 testbench `compare_enable("all")` 开启了 `dm_compare.compareflag`, 期望 DMI = Exp_DM = 0
- → DUT_DMI=z ≠ Exp_DM=0 → DMI compare error
- DQ/RDQS 同为 z 佐证: DUT 在期望的读数据窗口未驱动整条总线 (读窗口对齐问题), 非 DMI 单独功能故障

## 修复建议
1. MRR 前关闭 DMI 比较: `compare_disable("dm"); MRR(...); compare_enable("dm");`
2. 或设 `dm_compare.ignoreval = "ignorez"` 在 MRR 窗口忽略高阻

## case 合成 (r671)
- B 档 (A 档不可行: /rundata permission denied + 9000+行 testbench 不可沙盒复现)
- A: mini `lpddr5_simdir/` 7 文件忠实还原可检测结构
- B 隐藏变体 `lpddr5_simdir_v2/` (base64 内联 check.py): 同诊断结构, 标识符全异 (MR13→MR17, MA_DMICtrl→MA_DMIMode, OP_DMICtrl_Mode2→OP_DMIMode_C, OP_DMD_EN→OP_DMDSBL_EN, dm_compare→dmio_chk, compare_enable→cmp_on, PDRIVER.DMI→XDRV.DMIO, BG_→16B_, DUT_DMI→DUT_DMIO, 时间戳/期望值全异 等 ≥10 维)
- 交付: `analyze_dmi_compare_error(simdir)` 通用函数 → `dmi_pin_compare_diagnosis_report.json`
- check 11 条 a-k; ref PASS + 3 neg FAIL + §4.9 三假 FAIL + negative_selftest 7/7 + e2e jsonl PASS
- A.jsonl 363→364, case_id = EDA-Eval-DesignFlow-DmiPinCompareDiagnose-001
