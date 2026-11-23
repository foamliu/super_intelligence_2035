# trace_deepread — r1092 ofbxi (guangmingz @ hfeg0plg97, mc=107)

- **session**: `1795090353918_ofbxi` (157 msgs / 805 KB messages.json)
- **user**: guangmingz (dscqa/V0 project, IO_CABufCore cosim modeling)
- **host**: hfeg0plg97 (10.129.8.97), e0031982 ssh 免密 OK，但 guangmingz 的 /rundata + /proj 仿真目录对 e0031982 **Permission denied**（无法直读真实 cosim env 文件，只能从 trace 消息里取真实数据）
- **keywords**: netlist:544; verilog:143; schematic:142; analog:49; hspice:1

## 真实任务流

guangmingz 在开发 `vam-agent-demo` skill（VAMAgent — Verilog-AMS 建模智能体），路径 `/home/guangmingz/.cline/skills/vam-agent-demo/`。skill 结构：SKILL.md + references/ + scripts/ (create_cosim_block_env.py, extract_cell_ports.py, verify_cosim_block_env.py, validate_model.py) + templates/ (cosim_def.va, cosim_model.va, cosim_timing_param/)。

**fullchip 仿真**: `/rundata/dscqa_sim/V0/simdir/finesim/dscqaF2/MatrixRun/.../TT0.92V25C.X1P6/`（含 si.inp / raw/finesim.fsdb / netlist）。
**DSIM block 环境**: `/rundata/dscqa/V0/simdir/finesim/workdir/guangmingz/simulation/dscqa_io_IO_CABufCore_schematic_ALPS/`（含 input.sp）。
**cosim 输出**: `/rundata/dscqa/V0/simdir/finesim/workdir/guangmingz/simulation/vam_agent.cosim_20261119/`（cosim_model.va + cosim_timing_param/IO_CABufCore/ + IO_CABufCore_TT0.92V25C.cosim/）。

### 关键 user 指令
- U0: 调 vam-agent-demo skill，对 IO_CABufCore 做 Verilog-AMS 建模（提供 fullchip + DSIM block 路径）
- U7: 给 fullchip + DSIM block 两个真实路径
- U30: 更新 [step3] rule11 — 在 cosim block 环境创建模型相关文件，link cosim_timing_param 后**创建 cosim_def.va**（模板 templates/cosim_def.va，按实际 Corner 改参数）
- U83: 新增 [step4] 建模 cell 逻辑功能步骤（cosim_model.va 模板 + 端口规则 rule2-1..2-5 + 逻辑 rule4 + 时序 rule5/6/7）
- U109: 更新 [step4] 规则（extract_cell_ports.py、power inout、$table_model LUT、三元 (A>B)?1:0、时序参数置 0）

### 真实数据（从 trace 消息提取）
- **`.SUBCKT IO_CABufCore` 38 端口**（U28 网表解析输出，fullchip order）：
  `Bias DFEBias En EnN InNeg InPos MR_CaIbCtle<1> MR_CaIbCtle<0> NICBias Out VPwrCaIBH cm1_IO_CAC1<2> cm1_IO_CAC1<1> cm1_IO_CAC1<0> cm1_IO_CAI1<1> cm1_IO_CAI1<0> cm1_IO_CAI2<1> cm1_IO_CAI2<0> cm1_IO_CAI3<1> cm1_IO_CAI3<0> cm1_IO_CAR1<1> cm1_IO_CAR1<0> cm1_IO_CAR2<1> cm1_IO_CAR2<0> cm1_IO_CA_DfeI<2> cm1_IO_CA_DfeI<1> cm1_IO_CA_DfeI<0> cm1_io_CaDfeCtrl cm1_io_CaIbCtleCi<2> cm1_io_CaIbCtleCi<1> cm1_io_CaIbCtleCi<0> cm1_io_CaIbCtleDis off<1> off<0> offn offp vcc! vss!`
- **`.GLOBAL vcc! vss!`**（power 信号，rule2-5 → inout，`!` 去掉）
- **corner `TT0.92V25C`**（fullchip 路径名 + si.inp）→ process=TT, vdd=0.92, temp=25
- **cosim_def.va 模板**（U36）：
  ```
  `define TEMP 25
  `define PVDD 0.92
  `define CORNER "TT"
  ```
- **转换后 38 端口**（U117 final model module header）：`<num>`→`_num`，`vcc!`→`vcc`，`vss!`→`vss`，末两位 power。
- **validate_model.py 输出**（U128）：port count=38 PASS / port order PASS / last two power vcc/vss PASS / no bus <num> PASS / includes PASS / no laplace_nd/ddt PASS / $table_model LUT PASS / (A>B)?1:0 ternary PASS。

### assistant 产物
- `create_cosim_block_env.py` 增 `parse_corner(corner)` → ('TT',0.92,25)；[rule11] 生成 cosim_def.va（按 corner 替换 TEMP/PVDD/CORNER）；[rule12] patch input.sp。
- `gen_cosim_step4.py` / `gen_model_va.py`：生成 cosim_model.va（38 端口 module + $table_model LUT + 三元逻辑 + 注释）+ 4 个 TT_tr0/tf0/dr0/df0.dat 时序文件（值 0e-12）。
- `validate_model.py`：校验全部 rule（port count/order/bus/power/includes/no-disallowed-constructs/timing-LUT/ternary）全 PASS。
- 最后 U146 清理临时脚本，U156 加 [step5] 仿真确认模型逻辑功能正确性。

## reframe（合成目标）
**case = EDA-Eval-DesignFlow-VamCosimPortDeclGen-001**（L1 纯 Python，无 EDA 依赖）：
`vam_cosim_port_decl_gen.py <netlist.sp> <cell> <corner> <template_def.va> <out.json> <out_def.va>`
1. 解析 `.SUBCKT <cell> <ports>` → 端口列表（数量+顺序，rule2-1/2-2）
2. 解析 `.GLOBAL <sigs>` → power 集合
3. 每端口：`<num>`→`_num`（rule2-4）、power `!` 去掉（rule2-5）、标记 is_power
4. 解析 corner `<process><vdd>V<temp>C`（含负温度）→ process/vdd/temp
5. 写 out.json（cell/corner/n_ports/ports[{original,va_name,is_power}]/power_ports/process/vdd/temp）
6. 从模板渲染 out_def.va（替换 `define TEMP/PVDD/CORNER` 三宏）

**A**（真实 IO_CABufCore@TT0.92V25C，38 端口，vcc!/vss!）
**hidden B**（DfeBuffer@SS0.88V-40C，11 端口，vdda!/gnd!，负温度）— 五重 anti-hardcode：①cell 名 ②端口数 11 vs 38 ③bus 索引 ④power vdda/gnd vs vcc/vss ⑤corner SS/0.88/-40 vs TT/0.92/25

**check.py 13 条**：C1 zip+compile+size ｜ C2 B exit0+非空 ｜ C3 顶层键 ｜ C4 n_ports ｜ C5 端口顺序 ｜ C6 无 `<>` ｜ C7 power_ports ｜ C8 is_power ｜ C9 process ｜ C10 vdd ｜ C11 temp(-40) ｜ C12 def.va 三宏 ｜ C13 anti-hardcode + 3-seed 确定性

**自验**：REF 13/13 PASS ✓ ｜ NEG 3/3 FAIL ✓（empty→C1 / print_only→C4,C5,C7,C9,C13 / core_removed→C5,C6,C9,C10,C11,C12）｜ §4.9 三假齐 ✓
