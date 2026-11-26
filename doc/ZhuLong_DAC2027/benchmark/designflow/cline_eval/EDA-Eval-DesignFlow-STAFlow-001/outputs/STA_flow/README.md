# PrimeTime STA Flow (STA_flow)

基于 Synopsys PrimeTime 的静态时序分析（STA）流程。参考 feint 参考流
`/apps/imctf/cad/script/digital_flow/feint` 的做法，整理为独立的、可参数化流程：
同一套脚本通过选项传参适配不同的 corner 与 mode。

## 目录结构

```
STA_flow/
├── README.md                  # 本文件
├── setup/
│   └── common_setup.tcl       # 变量中枢：所有默认值，可被 -x 覆盖
├── scr/                       # 流程步骤脚本（按读入顺序编号）
│   ├── sta_main.tcl           # 主控：定位目录 -> source 变量中枢 -> 依序读入步骤
│   ├── 1_setup.tcl            # 环境配置 / 工具选型 / 输出目录 / search_path
│   ├── 2_read_lib.tcl         # 读入子模块 lib 输入件，配置 target/link library
│   ├── 3_read_design.tcl      # 读入网表（verilog）并 link 顶层设计
│   ├── 4_read_constraint.tcl  # 读入时序约束（.sdc/.tcl）
│   ├── 5_read_parasitic.tcl   # 读入寄生参数（SPEF）反标
│   ├── 6_check_design.tcl     # check_constraints / report_design
│   ├── 7_update_timing.tcl    # update_timing -full / check_timing
│   ├── 8_report_timing.tcl    # 主要时序报告（setup/hold/min_max/global）
│   ├── 9_analyze_timing.tcl   # 时钟/覆盖率/约束违反等分析报告
│   └── 10_rpt.tcl             # 汇总 QoR / 生成 .sdc / 保存 session / 退出
├── run/                       # 运行目录：任务运行脚本（cshell）
│   ├── run_sta.csh            # 主运行脚本，支持选项传参
│   └── run_demo.csh           # 一键 demo（自动发现 data/ 下的 demo design）
└── data/                      # 输入（demo design）：lib / netlist / sdc / spef
```

## 输出件层次

运行时在 `<ROOT>/` 下生成：
- `log/`     —— 运行日志（`*.log`、command log）
- `rpt/`     —— 各类报告（`*.rpt`）
- `sdc/`     —— 由 `write_sdc` 生成的派生约束文件（`*.sdc`）
- `session/` —— `save_session` 输出的 pt_shell 交互会话

## 关键 feature

1. **环境配置**：`1_setup.tcl` + `setup/common_setup.tcl` 统一配置目录、
   search_path、全局开关、命令日志。
2. **工具选型**：`run_sta.csh -tool <version>` 选择 PrimeTime 版本，
   默认 `/apps/synopsys/primetime/U-2022.12-SP5`；通过 `module load` 获取 license。
3. **子模块 lib 输入件读入**：`2_read_lib.tcl` 支持 `.lib`（read_lib 编译）与
   `.db`（target/link library）两种库文件。
4. **corner / mode 传参适配**：通过 `-corner` / `-mode`（映射为 Tcl 变量
   `CORNER/PT_CORNER`、`MODE/PT_MODE`）以及 `-x` 后置变量实现。

## 用法

```sh
cd STA_flow/run

# demo：自动发现 ../data 中的设计并跑通
./run_demo.csh

# 指定 corner / mode
./run_demo.csh -corner ss0p72vm40c -mode func

# 通用运行
./run_sta.csh -design <top> -corner <corner> -mode <mode> \
    -lib "<lib files>" -netlist <file> -sdc <file> -spef "<spef files>" \
    -tool <pt version>
```

`run_sta.csh` 选项：

| 选项 | 说明 | 默认 |
| --- | --- | --- |
| -design | 顶层设计名（必填） | - |
| -corner | corner 名（映射 CORNER/PT_CORNER） | tt0p8v25c |
| -mode   | 分析模式（映射 MODE/PT_MODE） | func |
| -tool   | PrimeTime 版本 | U-2022.12-SP5 |
| -lib    | 库输入件（lib/db，空格分隔） | 自动发现 data/*.lib|db |
| -netlist| 网表文件 | 自动发现 data/*.v|vg |
| -sdc    | 约束文件 | 自动发现 data/*.sdc |
| -spef   | 寄生参数文件 | 自动发现 data/*.spef |
| -x      | 透传给 pt_shell -x 的额外 Tcl | - |

## 数据准备

把 demo design 放入 `data/`（也可用 `-lib/-netlist/-sdc/-spef` 显式指定路径）：
- 库：`data/*.lib` 或 `data/*.db`（可放 `data/lib/` 下）
- 网表：`data/<top>.v`（或 `.vg`）
- 约束：`data/<top>.sdc`
- 寄生：`data/*.spef`（可选）

## 环境与 license

- 工具根目录：`/apps/synopsys/primetime`
- 运行脚本优先用 `module load ds/pt/<version>` 获取 license 环境；
  也会直接使用 `/apps/synopsys/primetime/<version>/bin/pt_shell`。
- 若无 module 环境，请自行 export `LM_LICENSE_FILE` / `SNPSLMD_LICENSE_FILE`。

## 参考

- 参考流：`/apps/imctf/cad/script/digital_flow/feint`（`scripts/pt.tcl`、`setup/common_setup.tcl`）