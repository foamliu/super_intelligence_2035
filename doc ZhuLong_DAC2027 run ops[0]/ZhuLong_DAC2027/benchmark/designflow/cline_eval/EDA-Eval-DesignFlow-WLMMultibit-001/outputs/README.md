# wlm_multibit.tcl — 无物理库 WLM 模式下开启多 bit（Multi-Bit）综合脚本

## 1. 概述

本工程交付一份可复用的 **Design Compiler（dc_shell）Tcl 脚本** `wlm_multibit.tcl`，
用于在 **无物理库（non-topographical）** 的 **Wire-Load-Model（WLM）** 模式下，
对设计 `pa_cpu_merged_top` 打开 **多 bit（multi-bit）单元推断与优化**。

- **无物理库**：不使用 Milkyway 物理库、不使用 TLU+ 寄生文件、不做布图规划；
  线延时统一由 **wire load model（WLM）** 估算。
- **多 bit（multi-bit）**：在综合时把多位寄存器自动打包到 `MB2SDF*` / `MB4SDF*`
  等多 bit 库单元上，从而减小触发器数量、面积与时钟树负载。

交付文件（打包进 `outputs/submit.zip`）：

```text
wlm_multibit.tcl   可复用的 DC 综合脚本
README.md          本说明文档
```

## 2. 依赖与输入

脚本通过 `source common_setup.tcl` 取得以下工程变量
（`assets/common_setup.tcl` 提供）：

| 变量名              | 示例值 / 含义                                             |
| ------------------- | --------------------------------------------------------- |
| `$DESIGN_NAME`      | `pa_cpu_merged_top` —— 顶层设计名                          |
| `$MB_LIB_PREFIX`    | `DBCP51H180L6W25T5_MB_SVT` —— 多 bit 库名前缀              |
| `$MB_CELL_PATTERN`  | `{MB[24]SDF*}` —— 多 bit 单元命名模板（MB2SDF*/MB4SDF*）    |
| `$OPT_MODE`         | `timing_only` —— 多 bit 优化模式                           |
| `$CRITICAL_RANGE`   | `0.1` —— 多 bit 时序优化 critical range                   |
| `$REPORTS_DIR`      | `reports` —— 报告输出目录                                  |

另需在运行目录准备：

- 设计网表文件 `${DESIGN_NAME}.v`（Verilog）
- 时序约束文件 `${DESIGN_NAME}.sdc`（选填）
- 逻辑库 `.db` 文件（脚本默认从 `./db` 目录读取）：
  - 单 bit 库 `${MB_LIB_PREFIX}` 去掉 `_MB` 后的名称（如 `DBCP51H180L6W25T5_SVT.db`）
  - 多 bit 库 `${MB_LIB_PREFIX}.db`（如 `DBCP51H180L6W25T5_MB_SVT.db`）

## 3. 脚本流程

1. **source common_setup.tcl** 取得全部工程变量。
2. **逻辑库设置**：由 `$MB_LIB_PREFIX` 推导单 bit 库名，与多 bit 库一起
   放入 `target_library` / `link_library`。
3. **WLM 设置（无物理库）**：
   - `set auto_wire_load_selection true` —— 按面积自动选取 WLM；
   - `set_wire_load_mode top` —— 使用顶层 WLM 计算所有线网电容。
4. **读入设计**：`read_file` → `current_design` → `link` → `uniquify`；
   如存在 `${DESIGN_NAME}.sdc` 则 `read_sdc`。
5. **开启多 bit**：
   - 用 `$MB_LIB_PREFIX` + `$MB_CELL_PATTERN` 扫描并校验多 bit 库单元；
   - `set hdlin_infer_multibit default_all` —— 从 HDL 总线寄存器推断多 bit 元件；
   - `set seqmap_prefer_registers_with_multibit_equivalent true` —— 优先映射到
     具有多 bit 等价单元的寄存器，提升打包率；
   - `set_multibit_options -mode $OPT_MODE`（`timing_only`）与
     `set_multibit_options -critical_range $CRITICAL_RANGE`。
6. **综合**：`compile_ultra`。
7. **报告**：输出到 `$REPORTS_DIR/`，含 `compile_options`、`multibit`、`qor`、
   `timing`、`area`、`power`、`check_design`。
8. **写网表**：`${DESIGN_NAME}.multibit.vg` 与 `${DESIGN_NAME}.ddc`。

## 4. 使用方式

```bash
dc_shell -f wlm_multibit.tcl | tee run.log
```

或交互式：

```tcl
source wlm_multibit.tcl
```

## 5. 关键命令说明

| 命令 | 作用 |
| ---- | ---- |
| `set_wire_load_mode top` | 指定 WLM 使用方式，体现“无物理库” |
| `set auto_wire_load_selection true` | 自动选 WLM，非 topographical 模式默认即开启 |
| `set_multibit_options -mode ${OPT_MODE}` | 设置多 bit 优化模式（`timing_only` 只在不伤时序时用多 bit） |
| `set_multibit_options -critical_range ${CRITICAL_RANGE}` | 多 bit 时序 rework 的 critical range |
| `hdlin_infer_multibit default_all` | 允许从 HDL 总线寄存器推断多 bit 元件 |
| `seqmap_prefer_registers_with_multibit_equivalent true` | 提高多 bit 打包率 |
| `compile_ultra` | 超强综合（非 SPG，纯 WLM 流程） |
| `report_multibit` | 报告多 bit 元件信息 |