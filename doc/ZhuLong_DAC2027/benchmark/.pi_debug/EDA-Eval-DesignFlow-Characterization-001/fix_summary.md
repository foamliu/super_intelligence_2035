# fix_summary.md — drgqx SiliconSmart 表征配置修复记录

corner: tt_25_1017
库: drgqx_cmos_analog / drgqx_cmos_digital / drgqx_cmos_io / drgqx_cmos_stdcells / stdcells_ac

以下逐条列出 error -> 根因 -> 修复，覆盖全部问题类别。

## 1. qualify_library / qualification_lc_shell（权限错误）
- error: lc_shell: Operation not permitted (qualify_library invocation)
- 根因: 表征环境不允许调用 lc_shell 做库资格检查，`set_config_opt qualification_lc_shell` 与
  `qualify_library $lib` 仍被 Tcl 执行。
- 修复: 在 5 个导出脚本（drgqx_cmos_analog.tcl / drgqx_cmos_digital.tcl / drgqx_cmos_io.tcl /
  drgqx_cmos_stdcells.tcl / stdcells_ac.tcl）中把这两行用**行首 `#`** 注释掉。
  注意 Tcl 中 `#` 只有位于命令起始位置（行首，可前导空白）才是注释，行尾 `... # disabled`
  不是注释、命令仍会执行，因此必须采用行首 `#`。

## 2. model 建模范围（SMSC-99）
- error: SMSC-99 — model cannot build verilog model for cells without PEX data
- 根因: `model -create_new_model -verilog all` 会对库内所有 cell 建模，而无 PEX 数据的 cell 无法构建 Verilog 模型。
- 修复: 5 个导出脚本统一改为 `model -create_new_model -timing $cells`，
  只对本次有表征数据的 cell 列表建模（verilog -> timing 建模方式切换，避免 SMSC-99）。

## 3. ffrqIOLVx2_pc60_odt.inst — add_latch 空寄存器名
- error: PARSE — add_latch: bad register name '{}'
- 根因: `add_latch Q {} Ck D -clear {!RN}` 中空 `{}` 被误解析为寄存器名。
- 修复: 删除空 `{}`，改为 `add_latch Q Ck D -clear {!RN}`（add_latch 语法修正）。

## 4. ffrqIOLVx2_pc60_odt.inst — forbidden_state XOR 非法
- error: PARSE — add_forbidden_state: illegal operator '^'
- 根因: Liberty 布尔表达式不支持 XOR 运算符 `^`。
- 修复: `add_forbidden_state { !(Ck ^ CkN) }` 用 `& | !` 等展开，
  等价改写为 `add_forbidden_state { (Ck & CkN) | ((!Ck) & (!CkN)) }`（XNOR 展开，去除非法 `^`）。

## 5. T_CompXor.inst — function XOR 非法
- error: PARSE — add_function Y { A ^ B }: illegal operator '^'
- 根因: Liberty 布尔表达式不支持 XOR 运算符 `^`。
- 修复: 用 `& | !` 等展开：
  `add_function Y { (A & (!B)) | ((!A) & B) }`（异或标准展开，去除非法 `^`）。

## 6. nor3IOLVIOx1_DQS.inst — 网表名漂移
- error: LINK — set_netlist_file: netlist not found 'netlists/nor3IOLVIO_1p6.spf_RC'
- 根因: `set_netlist_file` 与 `cut_netlist` 均引用旧网表名 `nor3IOLVIO_1p6.spf_RC`，
  与真实网表 `nor3IOLVIOx1_DQS.spf_RC` 不一致（netlist 名漂移）。
- 修复: 两处都更正为：
  `set_netlist_file netlists/nor3IOLVIOx1_DQS.spf_RC`
  `cut_netlist       netlists/nor3IOLVIOx1_DQS.spf_RC`

## 7. IO_TX_LOCAL_DCA_DQS.inst — default_input_state 缺失（PARA-7）
- error: PARA-7 — default_input_state undefined
- 根因: cell 控制文件未定义 default_input_state，表征引擎缺省输入电平信息。
- 修复: 增加活跃行：
  `set_config_opt -opcond __default__ -- default_input_state { DP1_per_0 1 DP1_per_1 0 }`

## 8. IO_TX_LOCAL_DCA_DQS.inst — bachIn 表达式含 `<` / `||`
- error: PARSE — bachIn: illegal '<' / '||' in boolean expression
- 根因: `add_function DQ { DP1_per<0> == 0 || DP1_per<1> == 0 }` 使用了
  Liberty 非法的位索引语法 `<0>/<1>` 与 `||` 运算符。
- 修复: 用 `| & !` 改写（无 `<`、无 `||`）：
  `add_function DQ { (!DP1_per_0) | (!DP1_per_1) }`

## 9. configure.tcl — vssFoot 重复定义
- error: PARA — vssFoot duplicate definition
- 根因: 全局 configure.tcl 中 `set_config_opt -param vssFoot {0.0}` 被定义两次。
- 修复: 删除（注释掉）重复的第二个 vssFoot 定义，仅保留一个活跃定义。

## 10. invYx2_CoM.inst — vwlp 供电反相器 pintype 错误
- error: PINTYPE — input pin threshold too low (0.94V default 阈值不足以在 2.75V vwlp 上翻转)
- 根因: `add_pin A default` / `add_pin Y default` 使用默认 pintype（0.94V 阈值），
  在 2.75V vwlp 供电下幅度不足以正确翻转。
- 修复: 改为 `add_pin A vwlp_type` / `add_pin Y vwlp_type`（vwlp pintype，约 VDD/2 参考电压）。