# Deepread: focjw — simlib undeclared-net static typo scan

## Trace
- session: `1793868895593_focjw` (e0039602@hfeg0pkn002)
- summary.tsv: mc=298, keywords schematic_netlist-dominant
- file: `.cline/data/sessions/1793868895593_focjw/1793868895593_focjw.messages.json` (1.5MB)
- 201 msgs (111 user / 90 assistant), verilog_lib_trans_v2.2 项目

## User intent & scenario
e0039602 维护 stdcell 网表→SystemVerilog 转换验证流。真实 simlib `simlib_drcoa_digital.sv`（629 module，门级 base 原语搭成，ANSI 端口）。用户在多轮里要求：

- [u0] 改 family recognition 逻辑（tb_family skill 判 stdcell 族）
- [u73] 检查变量名笔误
- [u107] 编译前加 typo-check + regenerate
- [u147] **核心 produce 轮**：扫描 `/rundata/drcoa/V0/simdir/verilog/e0039602/drcoa/verilog.ddr5.drcoa.AI/libs/simlib_drcoa_digital.sv`，629 module 里 247 bad / 674 issue（referenced-but-undeclared net）
- [u188] 最终只保留 family-recognition 改进，drop typo-check 部分

## 选轮合规
- u147 是「提出需求 / 表达目标」轮（扫描 simlib 找笔误），未给根因/未给修复方案 → CLEAN produce-task ✓
- u0/u73/u107 是迭代修正，u188 是范围收窄（drop）

## 可综合子任务
取 u147 的「undeclared-net 静态扫描 + 三分类 + JSON 报告」这一可独立判分子任务。

## 为什么 B-grade synthesized
- 真实 simlib 在用户私有 `/home/e0039602/Documents/verilog_lib_trans_v2.2/` + `/rundata/drcoa/...` NFS 路径，629-module 全量文件不可在沙盒复刻
- xrun 仿真环境 + tb_family skill 不可在沙盒复刻
- → 用合成 A(10 module)/B(14 module) 自包含输入复刻该子任务的判分逻辑

## 合成输入设计
- A `simlib_sample_A.sv`：10 module（nand2x1A..triregx1A，后缀 A），13 issue（typo=5/power_well=4/other=4），gate-level base 原语，ANSI 端口，含 trireg #(1,1,100) (medium) 修饰
- B `hidden/simlib_sample_B.sv`：14 module（and2x1B..clkbufx1B，后缀 B），18 issue（typo=8/power_well=5/other=5），名/数/分布全不同反硬编码
- spotlight：A CLKK→typo closest CLK / B CLKN→typo closest CLK, vddh→power_well, qqq→other

## SUT 契约
`net_typo_scan.py --input <simlib.sv> --outdir <dir>` → `net_typo_report.json`（只读、确定性、6 顶层字段 + per_module）

## 判分
check.py 16 条件 a-p，独立参考实现嵌入，ref PASS 16/16，5 neg 全 FAIL distinct。
