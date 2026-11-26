# 深读笔记 · 2ze9s · Virtuoso 前仿网表定位 Q&A

- session: `1794202630733_2ze9s`（子目录 `1794202630733_2ze9s/` 下）
- user: zhililu @ hfeg0pkn002
- agent: lead (cline)
- mc: 83, domain: spice_sim
- trace: 68535B / 16 msgs / ~5 substantive turns（含 user_input + tool 调用 + 最终回答）
- 旧判: parked (2026-11-10, "consultation not produce-task") → r618 reaudit 复活为可造

## 用户真实意图（原话）
> 「我想更改virtuoso仿真的网表，前仿，路径在哪里，怎么找」

用户想知道 **Virtuoso 前仿真（schematic 级 spectre/hspice 前仿）网表文件的位置 + 如何找到 + 如何修改**。纯知识咨询 Q&A，无文件产物需求。

## 助手实际行为（工具链）
1. 路由到 `eda_agent` skill（SKILL.md，Aether/Virtuoso 平台自动化）
2. `read_file` skill 案例库 → 只有 `case_007_highlight_nets_by_pattern_skill.md`，无前仿网表专项案例
3. `search_codebase` 搜 "netlist"/"前仿"/"simulation.*netlist"/"ADE.*netlist"/"网表" → **全部超时(30s)失败**
4. `list_files` skill/skill/04_case_studies → 仅 case_007；读 02_virtuoso_skills.md / 00_INDEX.md
5. 最终给出**基于 Cadence ADE 标准行为**的结构化知识回答（非脚本/非产物）

## 助手最终回答结构（知识要点）
1. **网表默认路径**：`<工作目录>/simulation/<设计名>/<仿真器>/<运行目录>/`
   - Spectre: `netlist` 或 `input.scs`
   - HSPICE: `netlist.sp` 或 `input.hspice`
2. **GUI 找法**：
   - ADE L: `Setup → Simulation Files/Directory` 看 Netlist 栏
   - ADE XL: Testbench/Test 面板 → Netlist / Run Directory
   - 命令行: `find . -name netlist -o -name input.scs`
3. **修改方式**（4 种，按持久性）：
   - Model Library / Stimulus Files（include 进网表，持久）
   - Netlist Include Files 追加（持久，官方推荐）
   - 直接编辑生成目录网表（临时，下次 Netlist & Run 覆盖）
   - Stimuli 添加激励源
4. **关键警告**：ADE 每次 `Netlist & Run` 自动重新生成网表 → 直接手改会被覆盖 → 持久改走 include 机制

## 造题决策
- **形态**：Q&A/咨询 → 结构化回答（revival series L1 offline）。check 验关键知识点覆盖 + cross-input guard（隐藏 B 不同 ADE/simulator/design）。
- **A 档不可行**：真实 trace 是纯知识 Q&A，无文件产物；用户 Virtuoso ADE 环境在 hfeg0pkn002 工作站，SUT 沙盒无 Cadence/图形界面不可达。故 B 档 synthesized：构造真实风格 ADE CIW 日志 + 设置描述作 doc/。
- **判分有牙**：scenario.* 字段必须从 doc/ 提取（隐藏 B 是不同 ADE 场景），cross-input guard + A-leak guard 防硬编码；真跑候选(subprocess) + 确定性(3 rerun)。
- **18 断言**（a-r），k_check==k_rationale==18 ≥8 ✓。
