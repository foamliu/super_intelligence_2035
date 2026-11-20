# Deepread: 1793843849886_hsizo (ynbai @ 10.129.32.75, mc=211)

**Session**: 1793843849886_hsizo.messages.json — 325 msgs, host hfeg0pkn047
**Domain**: schematic_netlist (SPICE netlist → finesim_ignore.list generator)
**Pick**: shard D #296, A-faithful, B-grade synthesized, L1

## User turns (verbatim, requirement-expression only)

- **U#0**: 「写一个脚本，输入为netlist，输出为finesim ignore文件，脚本帮忙抓出来 XIctop.XI_Channel.XI_BnkGTopX4_Top.XI_BnkGTopX4_gut.XI_BnkGTop_AC.XI_D_RWCBG 下的所有instance的hierachy，只到下一级，例如 ...XI_D_RWCBG.XI_D_CasBnkGRptLR，输出到 /proj/drvqa/.../finesim_ignore.list 文件中，文件内容为 .option finesim_ignore = "hierachy" 例如 .option finesim_ignore = "...XI_D_RWCBG.XI_D_CasBnkGRptLR" 下一行为下一个instance, netlist文件path为 .../netlist」
- **U#137**: 「脚本内加一行，内部存在一个cell name为AbusEnRdCtrl，它对应到instance hierachy不包含在ignore文件中」(排除规则，提需求)
- U#147/U#177/U#283: 8-file bank-group 扩展 + 嵌入抽网表流程 (后续演化，premise-dependent，不进 A-faithful prompt)

U#0 + U#137 均为「表达目标」轮（非根因/修复）→ A-faithful 合规。取 U#0+U#137 作 prompt。

## Trace agent 实际产物 (gen_ignore.py 算法)

1. 在 netlist 中找实例名 == `XI_D_RWCBG` 的 X 实例（首匹配），收集 `+` 续行，master = 拼接后最后 token
2. 找 `.SUBCKT <master>` 定义行
3. 解析 subcircuit body 在 depth=1：收 X 实例（含 `+` 续行），得 (inst_name, master_cell)；嵌套 .SUBCKT (depth≥2) 跳过
4. 排除 master_cell == `AbusEnRdCtrl` 的实例
5. 输出 `finesim_ignore.list`：每行 `.option finesim_ignore  = "<parent_hier>.<inst>"`，按 inst 名排序

## 合成 (B-grade)

真实 full-chip netlist (/rundata /proj 路径, permission-denied + 不可附加) → B-grade synthesized:
- **A (visible)**: netlist_A.sp — XI_D_RWCBG master=RWCBG_DPMux_A, 5 children (1 AbusEnRdCtrl 排除, 1 续行, 1 嵌套 .SUBCKT) → 4 输出
- **B (hidden)**: target=XI_D_RWCBE, parent=...GE, exclude=BdEnWrCtrl, master=GE_DPMux_B, 6 children → 5 输出
- **B2 (hidden cross-input)**: 同 target/exclude 但 master=GE2_DPMux_B2, 4 children → 3 输出 (反硬编码 master 名/子实例列表)

## case_id: EDA-Eval-DesignFlow-FinesimIgnoreGen-001
- check.py 14 条件 a-n（zip/import, py_compile, B exit0, 行格式, 行数, prefix, 排除, 续行, depth-2 不泄漏, 排序, 目标动态, B2 跨输入, 无硬编码路径+argv, 确定性）
- 自验: ref PASS 14/14; 6 negative 全 FAIL; §4.9 三假 {empty→c, print_only→e, hardcoded_stub→h} distinct=3; k_rationale=k_check=14 GATE PASS
- 教训: (1) 续行实例首行末 token 设为 exclude_cell 名 → no_continuation stub 误排除续行实例 → (h) 拦截; (2) B2 同 target/exclude 但不同 master subckt 名+不同子实例 → 反硬编码 master 名/子实例列表
