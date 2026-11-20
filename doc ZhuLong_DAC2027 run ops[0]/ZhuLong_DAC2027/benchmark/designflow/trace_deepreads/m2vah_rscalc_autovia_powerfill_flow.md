# Trace Deepread — m2vah (e0014566 / hfeg0plg58)

- **session**: `1785810906841_m2vah.messages.json` — 573 msgs, 1.96 MB
- **match_count**: 975 (705 virtuoso / 105 cellview / 51 calibre / 23 skill / 14 dbGet / 10 schematic / 5 pyAether / 4 hspice)
- **tools used**: run_commands×182, read_files×41, editor×38, SandBox_MCP_Server__run_code×23
- **domain**: analog_context (Virtuoso layout resistance-reduction workflow)

## 用户意图演进（user 轮）

1. **msg#0**（核心需求）：分析 2 个 skill（rscalc + autovia），梳理配置文件、合并共有参数到 common.config；构建工作流「算电阻 → 调用版图优化工具 → 降低电阻」迭代直到电阻明显降低；写进 prompt_flow.md；上一步输出=下一步输入；电阻降幅 + 最大迭代次数写进配置文件。
2. msg#38：先分别跑两个工具验证正常。
3. msg#129：把 common.config 里的 powernet 挪到 rscalc.config（不公用）。
4. msg#145：powernet 支持为空 → 自动获取全部 power net，固化逻辑。
5. msg#265：分析 autovia 只发现 1 个 powernet vs rscalc 多个的差异。
6. msg#369：**所有点位**电阻都要优化，不是只优化最大电阻。
7. msg#501：autovia 是否只能低层金属找 via。
8. **msg#525**（扩展）：引入第三个工具 powerfill，放到 autovia 后面，构成 `rscalc → autovia → powerfill → rscalc` 循环迭代；共用参数提到 common.config。

## 金标准（trace 末尾用户接受的结果）

工作目录 `/home/e0014566/test_layout_rscalc_flow_3/`，真实产物：

- **common.config**：共享参数 single source of truth
  - `process = "cxmt10G4plus"`, `project = "train"`, `libName = "austin_rscalc2"`, `cellName = "testa_opt2"`, `viewName = "layout"`
  - 流控键：`targetReduction = 0.5`（要求所有点位电阻降至 baseline 的 50% 以下）, `maxIterations = 5`
  - 明确 `pwrNets/pwrnets` **不**共享（rscalc 用 RTEXT 无 `!`，autovia 用 GDS TEXT 带 `!`）
- **rscalc.config**：仅 RsCalc 专有 — `pwrNets = ""`（空→自动从 RTEXT 检测全部 net）, `metalOption`, `parallel`, `runDir`, `checkPoints = nil`（从 RNODE 自动提取）
- **run_autovia_config.il**：仅 AutoVia 专有 — `pwrnets = ""`（空→从 GDS text 末尾 `!` 检测）, `strminLib`, `coreNum`, `outLibName/outCellName`
- **run_powerfill_config.il**：仅 PowerFill 专有 — `workDir`, `powerName = ""`（空→处理全部 power net）, `runMode`, `speedMode`, `convertToPcell`, `outLibName/outCellName`
- **prompt_flow.md**（265 行）：6 节 — Goal / Configuration files / Resistance metric & convergence / Data flow / Environment / Runbook (Step 0-3)
  - **关键收敛判据**：`R_i(p) <= R_0(p) * (1 - targetReduction)` for **ALL** check points p（worst 点决定收敛，不是只看 max）
  - **数据流**：每 iter = AutoVia → PowerFill → RsCalc；cellName 是单一 chaining point（每 iter 更新 common.config 的 cellName）；唯一 cell 名 `_av<i>` / `_pf<i>` 防覆盖
  - **baseline**：`flow_rscalc_baseline.log` + `baseline_rpoints.csv`（18 check points，key=`net_layer_x_y`，值=电阻）
  - **解析公式**：`find *.rvn | awk -F',' 'NF>=12 && $12!="" {key=$3"_"$4"_"$5"_"$6; print key","$12+0}'`
- **生成器脚本**：`gen_rscalc_agent.py` / `gen_autovia_agent.py` / `gen_powerfill_agent.py` — 读 common.config 映射名字（project→projName, viewName→viewType），再 overlay 工具专有 config；丢弃 FLOW_KEYS（targetReduction/maxIterations 不内联进 SKILL）

## B 档 case 设计（EDA-Eval-DesignFlow-RsCalcFlow-001）

真实 Virtuoso SKILL 无法在 check 沙箱跑 → 提供 `mock_tools.py` 模拟三工具的 I/O 行为（确定性、config 驱动）。候选交付 Python `flow_orchestrator.py` + 4 个 config + `prompt_flow.md` + `sample_run_report.txt`。check 验证：config schema、prompt_flow 关键条款（loop 顺序 / ALL 点位收敛 / 空自动检测）、orchestrator 在 hidden B 上真跑（subprocess）—— 仿真调用序列正确（mock_calls.log）、maxIterations cap、早收敛、电阻单调非增、cell chaining 唯一名、cross-input 反硬编码。

level=L1（Python 编排，但编码的是真实 L2 Virtuoso 工作流）；track=B；domain=analog_context。
