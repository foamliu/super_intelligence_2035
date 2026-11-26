# 任务说明 — PrimeTime 寄生参数反标失败诊断（DRAM STA signoff）

> 真实 trace 来源：DRAM 时序/寄生工程师在 PIM LPDDR6 双芯（Logic Die + DRAM Die）验证平台上做 PrimeTime `read_parasitics` 反标失败诊断。本附件为其脱敏合成数据。

## 背景

设计 `DRAMTOP` 在 PrimeTime（Synopsys，U-2022.12-SP5）里做 STA signoff。反标（read_parasitics）跑完后报告 **9,660 条 net 未反标**（占 1,041,009 总 net 的 0.93%）。需要诊断未反标的根因、区分关键/非关键失败、给出可执行的 CDL ignore 方案。

## PrimeTime 反标 5 个必备输入

1. Gate-level netlist（Verilog，Cadence Virtuoso ADE SI Verilog Netlister 生成）
2. Libraries (.db)
3. Net Parasitics（SPEF，IEEE 1481-1999，Synopsys StarRC 生成，`.cvps` 工艺角点压缩）
4. Design Constraints（SDC）
5. OCV related files（`set_timing_derate 0.95` 等）

## 反标匹配机制（重要提示）

PrimeTime 执行 `read_parasitics` 时，对 SPEF 中每条 net/pin：
1. 在 Verilog 网表中**搜索同名 net**；
2. 验证该 pin 确实连接到该 net；
3. 找不到对应 net → 记 `PARA-124`（Cannot find net）；
4. pin 不连接到该 net → 记 `PARA-044`（Invalid capacitor，pin 未连接到 net）；
5. 耦合电容至少一个节点不在当前 net 上 → 记 `PARA-043`（Invalid coupling capacitor）；
6. 命中上述任一 → 该 net **未反标**。

## 已知跨厂家现象（线索，不是结论，需在你的诊断里证实）

- SPEF 由 **Synopsys StarRC**（R-2020.09-SP5-4）生成；
- Verilog 网表由 **Cadence SI Netlister** 生成；
- 两者 hierarchy 提取策略不同：StarRC 会 **merge 掉一些不重要的中间节点**（trivial 节点），Cadence 网表保留**完整层级** → 名称对不上 → 反标失败。
- 这类因 merge trivial 节点导致的失败**不是 critical 路径**，可在 CDL 中加 ignore 规则过滤。

## 附件清单

- `parasitics_command.log` — PT 反标命令日志节选（含反标汇总表 + PARA error 样例 + DES024 100 条/类上限）
- `dramtop.spef` — DRAMTOP SPEF 片段（头 + 若干 *D_NET 块含 *CONN/*CAP/*RES/*END）
- `dramtop_netlist.v` — Verilog 网表片段（含 mx4Lx2/invLx1 等实例层级）
- `calibre_lvs.rule` — Calibre LVS rule 片段（含 LVS PREFER NETS FILTER + net 映射格式说明）
- `sdf_interconnect.sdf` — SDF INTERCONNECT 段片段
- `task_brief.md` — 本文件

## 交付要求

产出反标失败诊断交付件，打包成 `outputs/submit.zip`，含 **4 个文件**：

1. `annot_diag_report.md` — 诊断报告：
   - 分类 9,660 条未反标 net（按 PARA-043 / PARA-044 / PARA-124 三类分别给计数与样例）；
   - **反标汇总表**（Total / RC network / Not Annotated，含 Internal / Boundary / TOTAL）；
   - 根因分析（需明确指出跨 EDA 厂家 hierarchy 策略差异：StarRC merge trivial 节点 vs Cadence SI 保留完整层级）；
   - 反标匹配机制说明。
2. `hierarchy_compare.tsv` — 跨厂家 mismatch 类的层级对照表：
   - 至少 5 行，每行含 `error_type` + `net` + `netlist_hierarchy` + `spef_hierarchy`（netlist 完整层级 vs SPEF merge 后层级）。
3. `noncritical_ignore_list.txt` — 非关键（merge trivial 节点）net 的 CDL ignore 条目：
   - 每行格式 `CellName#OldNetName#NewNetName`（`#` 分隔三段，CellName 为上层 cell，OldNetName 为网表里的 net，NewNetName 为 SPEF 里 merge 后的 net）；
   - 至少 5 条。
4. `critical_fails.tsv` — 关键失败（需真实修复，非 merge 导致）清单：
   - **非空**（不能把全部 9,660 都归为 noncritical），含 `error_type` + `net` + `reason` 列；
   - 与 `noncritical_ignore_list.txt` 里的 net **不能重叠**。

## 约束

- 不改附件文件；
- 所有结论须能在附件里找到证据（不要凭空编数据）；
- 交付件是纯文本分析产物，**不需要跑 PrimeTime/StarRC**（这是离线日志诊断任务）。
