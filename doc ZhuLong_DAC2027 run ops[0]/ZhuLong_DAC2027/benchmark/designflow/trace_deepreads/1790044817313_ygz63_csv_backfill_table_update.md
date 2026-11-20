# Deepread · ygz63 · SRAM AutoSim CSV 回填表格更新

**Session**: `1790044817313_ygz63` · **User**: rongjiez @ 10.129.2.14 · **mc**: 23 · **Domain**: schematic_netlist
**Status**: failed · **N_MSGS**: 49 · **Turns**: 1 user turn · **Date**: 2026-10-23

## 真实用户意图（U#0 逐字）

> /home/rongjiez/jira_dev/AICAD-17/SRAMAutoSim/ 是我的代码文件目录，其中 mainwindow 中我的 on_actionCreate_Testbench_triggered() 中通过 fullFlow 脚本对输入的 csvFile 执行，输入的 csvFile 内容为：
> ```
> Instance,Vt,Process,OutputPath,Netlist,Vector
> CXN4S1P24X8M4B2C1R0W0BW0RE0,SVT,FS,/home/rongjiez/jira_dev/AICAD-17/netlist
> ```
> 在 onFullFlowProcFinished 之后同一个文件被更新为：
> ```
> Instance,Vt,Process,OutputPath,Netlist,Vector
> CXN4S1P24X8M4B2C1R0W0BW0RE0,SVT,FS,/home/rongjiez/jira_dev/AICAD-17/netlist,/home/rongjiez/jira_dev/AICAD-17/netlist/CXN4S1P24X8M4B2C1R0W0BW0RE0.netlist,/home/rongjiez/jira_dev/AICAD-17/mem_pre1/vector/CXN4S1P24X8M4B2C1R0W0BW0RE0.vec
> ```
> 并且有输出 log：`[SUCCESS][FLOW.SUMMARY] [full_flow.py:608] CSV backfilled: /home/rongjiez/jira_dev/AICAD-17/mem_pre1/instances.csv (1 instances updated)`
> 我需要你把更新后的 CSV 文件更新到 instance 表格对应的数据显示 Netlist、Vector

## 工具链与产物

- **代码库**: `/home/rongjiez/jira_dev/AICAD-17/SRAMAutoSim/` — Qt C++ SRAM 自动仿真工具
- **关键文件**: `mainwindow.cpp` (2200+ 行), `mainwindow.h`, `instancedata.h`
- **关键函数**:
  - `on_actionCreate_Testbench_triggered()` (line 252): 生成 `instances.csv`（4 列有值 + Netlist/Vector 空），启动 fullFlow 脚本
  - `onFullFlowProcFinished()` (line 1399): fullFlow 完成回调 — **当前只 log，不更新表格**（这是要修的 bug）
  - `loadInstancesFromCSV()`: 从 CSV 加载实例到表格
  - `refreshTable()`: 刷新表格显示
- **表格结构**: 6 列 — Instance(0), Vt(1), Process(2), OutputPath(3), Netlist(4), Vector(5)
- **fullFlow 脚本**: `full_flow.py` — 回填 CSV 的 Netlist/Vector 列（写入 `.netlist` 和 `.vec` 文件路径）

## Agent 解法（regen-from-table-update）

Agent 探索 mainwindow.cpp（分批 read_files 100-2200 行），理解代码结构后设计修改方案：
1. **跟踪 QProcess→csvFile 映射**: 把 `m_fullFlowProcList` 改为 `m_fullFlowProcMap`（QProcess* → csvFile 路径），在启动 fullFlow 时记录对应 CSV
2. **在 onFullFlowProcFinished 中重读 CSV**: 从映射取出 csvFile，调用 `loadInstancesFromCSV()` 重读回填后的 CSV
3. **更新表格**: 对每行按 Instance 匹配，更新 Netlist(4)/Vector(5) 列单元格

**阻碍**: agent-policy-engine 限制可写目录为 `/home/rongjiez/.cline/scripts/data`，无法直接编辑 mainwindow.cpp → agent 把修改方案写入 `onFullFlowProcFinished_changes.md` 文档。session status=failed。

## B-grade 合成设计（CsvBackfillTableUpdate-001）

提取数据流核心：**读回填前 CSV + 回填后 CSV → 按 Instance 匹配 → 生成 JSON 报告（status + netlist/vector + summary）**。放弃 Qt C++ 代码修改（无法在沙盒编译 Qt）、GUI 事件流、QProcess 映射机制（非自包含）。

- **A (visible)**: SRAM SVT/FS rongjiez 风格，6 instances（4 backfilled / 2 pending），路径 `/home/rongjiez/jira_dev/AICAD-17/`
- **B (hidden)**: SRAM LVT/SS dev2 风格，5 instances（3 backfilled / 2 pending），路径 `/home/dev2/jira_dev/AICAD-22/`
- **C (embedded anti-hardcode)**: SRAM HVT/TT dev3 风格，4 instances（2 backfilled / 2 pending），路径 `/home/dev3/jira_dev/AICAD-25/`
- A/B/C instance 前缀(CXN4/CXN5/CXN6)、Vt(SVT/LVT/HVT)、Process(FS/SS/TT)、路径全不相交

**SUT**: `csv_backfill_table_update.py <pre_csv> <post_csv> <output_json>` — 纯 stdlib (csv/json/sys)，禁 numpy/pandas/subprocess 等

**check.py**: 17 条件 a-q 独立 oracle（`report_ref()` 不 import SUT），subprocess 真跑 SUT on B+C，3-seed sha256，§4.9 三假全 FAIL

## 维度正交论证（非 dup）

vs NetlistSvRulesReorg-001(#541, 文本分节重排) / CmpEmPolyThkCalc-001(#540, 多项式 THK 求值) / WvVecCmpXTolAudit-001(#538, 波形向量容差) / SpiceMismatchSweep-001(#537, .param sweep) / SpiceMeasGroupExpand-001(#539, .meas deck 扩写) → 本 case = CSV 双文件 diff + Instance 匹配 + backfill status 分类 + JSON 报告，机制不同 ✓

## 自验结果

- ref PASS 17/17 (score 1.0)
- 3 negatives 全 FAIL (naive_always_backfilled / naive_always_pending / stub_empty)
- §4.9 三假全 FAIL (empty / print_only / core_removed)
- A output 逐字节匹配 oracle，3-seed sha256 stable
- k_rationale = k_check = 17 ✓ (≥8 硬闸门)
