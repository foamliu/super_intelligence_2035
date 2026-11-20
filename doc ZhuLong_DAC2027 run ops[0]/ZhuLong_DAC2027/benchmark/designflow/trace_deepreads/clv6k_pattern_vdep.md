# clv6k — verilog pattern `include 依赖解析

- **session**: 1789955434443_clv6k · user t0002470 @ 10.129.2.13 · mc=59 · domain schematic_netlist
- **真实路径**: /proj/drcoa/V0/simdir/verilog/ydhe/verilog.ddr5.drcpa.aicov/AI_cov3 等多 AI_cov* 目录
- **cline 存储（目录式）**: /home/t0002470/.cline/data/sessions/1789955434443_clv6k/1789955434443_clv6k.messages.json (1.63MB)
- **产物**: /home/t0002470/.cline/scripts/data/analyze_pattern_v_deps.py (18KB)

## 用户轮（逐字，A-faithful 提需求；U#6 为修正非根因）
- U#0: /proj/drcoa/V0/simdir/verilog/ydhe/verilog.ddr5.drcpa.aicov/AI_cov3 我如何获取我在这里打了那些pattern？
- U#1: 我想知道每一个pattern都打了那些指令序列，你可以看到每一个pattern下都有inc，他include了很多其他位置的pattern
- U#2: **我需要你写一个程序，获取该目录下所有pattern分别引用了那些.v**
- U#3: 我希望查看制定目录下的AI_*的所有内容
- U#4: 我需要详细的信息，你应该修改你之前的代码让他能够去多个目录查看
- U#5: 输出结果会保存到某个目录吗
- U#6: 我发现 Pattern_tasks.v 并不是对应的pattern而是对应路径下的对应名字的.v文件。例如对于 .../AI_cov19/Golden008_Dualbank_Wr_MPC_RPre_1_RPst_1P5_WPre_2_WPst_0P5_CRC_00_1_ROffset_3_tCH_50_BC8_OTF_4b4g_Bc5_5600_TT.x16 它对应的是 Golden008_Dualbank_Wr_MPC.v
- U#7: (粘贴 agent 输出样例) Calls task: Perbank003_SRA_SCA, Task file: Perbank003_SRA_SCA.v, .inc refs: - AddressParameter.v (/full/.../Include/AddressParameter.v) - Basic.v ... - DataPattern.v ...

## agent 产物逻辑（analyze_pattern_v_deps.py）
- 扫描 AI_cov* 目录；`get_pattern_class(dirname)` 用 `_RPre_/_RPst_/_tCH_/_WPre_` 截断得任务名
- 每目录：找 `.inc` 文件 → `INC_RE = `include "X.v"` 直接引用；找 `<PatternClass>.v` → 直接 `include 引用；读 `A_Pattern_Sim.v` → `TASK_RE` 正则识别调用的任务名 + `include 引用
- `find_v_references_in_file` **非递归**：仅相对包含文件所在目录拼接解析（不校验存在），合并 .inc/task.v/A_Pattern_Sim.v 的直接引用去重
- 按 `/kw/` 目录关键词分类（CATEGORIES），输出跨目录汇总 + 分类矩阵 + 每pattern明细
- 用户 U#6 修正了「Pattern_tasks.v 对应」→ 实为 `<PatternClass>.v`

## 本轮合成决策（B 档 synthesized）
- 取 U#2 的核心需求「写程序获取所有 pattern 引用的 .v」+ U#6 的任务名→.v 映射澄清，合成一个**递归** `include 依赖解析器（比真金标准更严格：递归 + 跨目录解析 + 环检测 + 去重），提升可验条件数到 16。
- 不用 A 档逐字（U#2 单句欠规格、U#6 偏修正轮）；B 档把真实结构（DDR5 pattern 目录、_RPre_ 后缀、Include/ 子目录、`include 环）写成自然语言 spec，服务用户「理解每个 pattern 引用了哪些 .v」的真实目标。
- 反硬编码三轴：A/B 目录名 + .v basename 完全不相交；B 含 3-环、Include/ 子目录、空任务文件等 A 没有的结构。

## 案件
- case_id: EDA-Eval-DesignFlow-PatternVDepResolver-001
- domain: schematic_netlist · track: synthesized(B) · L1 真跑候选 (python3 subprocess on hidden B)
- 16 条件 a-p：见 reference/.../check.py CONDITIONS
- 自验：ref PASS 16/16 · 3 negatives 全 FAIL · §4.9 三假(empty/print_expected/ref_core_deleted) 全 FAIL · 确定性 3 次重跑一致
