# 深读笔记 — sid 1787318451519_5hrad (e0014566 / hfeg0pkn001 / mc=327)

- **域**：pg_layout（autovia + powerfill 自动生成 cell 识别与移除）
- **A-档 seed**：UI#0 逐字「请你识别到 Library: auto_austin_case1, cell: BCenterCA_rscalc, 中 layout 的布局，识别出 autovia 和 powerfill 生成的 cell, 并把这些 cell 去除。」= 提出需求/目标，未给根因或修复 → A-档 seed 合规 ✓
- **唯一 user text turn**（共 1 条；其余 145 user 消息为 tool_result）
- **agent 工具调用**（145 次）：run_commands 69 / RAG search_apis 24 / SandBox run_code 18 / editor 14 / read_files 12 / get_api_details 8
- **trace 路径**：`/home/e0014566/.cline/data/sessions/1787318451519_5hrad/1787318451519_5hrad.messages.json`（939KB / 266 msgs / agent=lead / model glm-5.1-cloud）

## agent 排查链
1. SandBox pyAether：`aeOpenDesign("auto_austin_case1","BCenterCA_rscalc","layout","edit")` + `aeGetCurDesign` → 打开版图
2. SandBox SKILL：`dbOpenCellViewByType` 枚举顶层 instances（234 个实例 / 77 unique lib-cell 对），按命名候选扫描 autovia/powerfill
3. SKILL 深检候选 cell：`BCenterCA_vddqca_improve` / `BCenterCA_PCUCT_20250715_auto_pc` / `BCenterCA_20250619_VIA_TOP` / `signal_power_fill_gut` / `BCenterCA_auto_pgdm` 等（shapes/vias/insts 统计）
4. editor 写 SKILL 脚本 `remove_autovia_powerfill_BCenterCA.il`（9 次编辑拼装）
5. run_commands：反复在 `/proj/train/V0_Austin/workdir/e0014566/` 用 `virtuoso -nograph -replay run_remove.cmd` 跑 SKILL，遭遇 LD_LIBRARY_PATH / OA_HOME / libstdc++ / CDS_LIC_FILE 环境问题，多次重试（设 OA_HOME=/apps/cdsmgr/CRB/IC617ISR23/oa_v22.50.095 + lib-stdcxx bundle）
6. 最终跑通 `remove_run3.log`：8 个实例 dbDeleteObject + dbSave，verify 234→226

## gold（agent 交付的真实产物）
- SKILL 脚本 `remove_autovia_powerfill_BCenterCA.il`，核心谓词 `RL_IsAutoViaOrPowerFill(cellName)`：
  - **case-sensitive** `rexMatchp`：
    - `VIA`（大写）→ autovia
    - `_fill`（小写下划线）/ `improve` / `auto_pc` / `auto_pgdm` → powerfill
  - **不匹配**（标准 cell，保留）：`AutoCap`（大写 A，非 `auto_pc`）/ `FILL`（大写，非 `_fill`）/ 小写 `via`（非大写 `VIA`）
- 识别 8 个自动生成 cell：
  | # | inst | lib/cell | 类型 | 命中 |
  |---|---|---|---|---|
  | 1 | I35 | zlib/BCenterCA_20250619_VIA_TOP | autovia | `VIA` |
  | 2 | I_BCenterCA_vddqca_improve_438 | zlib/BCenterCA_vddqca_improve | powerfill | `improve` |
  | 3 | I_signal_power_fill_gut_435 | zlib/signal_power_fill_gut | powerfill | `_fill` |
  | 4 | I_BCenterCA_PWR_improve_433 | zlib/BCenterCA_PWR_improve | powerfill | `improve` |
  | 5 | I39 | zlib/BCenterCA_PCUCT_20250715_auto_pc | powerfill | `auto_pc` |
  | 6 | I36 | zlib/BCenterCA_PCUCT_20250703_auto_pc | powerfill | `auto_pc` |
  | 7 | I33 | zlib/BCenterCA_PCUCT_20250619_auto_pc | powerfill | `auto_pc` |
  | 8 | I411 | zlib/BCenterCA_auto_pgdm | powerfill | `auto_pgdm` |
- 移除后 234→226（删 8），verify 0 autovia/powerfill 残留

## A-档 disqualified → B-档 synthesized L1-boundary
- gold 依赖 live Virtuoso（IC617ISR23）+ OA 22.50 + 私有 `auto_austin_case1` 库（`/proj/train/V0_Austin`，e0031982 无权）→ 不可沙盒复现 → A-档 disqualified
- 合成锚点：**case-sensitive 命名规则分类器**（离线 Python 解析实例 inventory 文本，按大小写敏感子串匹配分类 autovia/powerfill/standard，输出 JSON 移除报告）
- 与既有 case 区别：
  - AutoCellFlowValidate-001 = AutoCell TCL flow 8-文件依赖结构校验
  - PFMergeAudit-001 = layout figure merge 完整性审计（pin/net 关联丢失）
  - RNodeCovAudit-001 = RsCalc RTEXT/RNODE 探针覆盖审计
  - 本案 = **autovia/powerfill 自动 cell 命名分类 + 移除报告**（case-sensitive 子串匹配，区分自动生成 vs 标准 cell），主题/断言独立

## 合成设计要点
- **判分核心 = case-sensitivity**：大写 `VIA` vs 小写 `via`；`_fill` vs `FILL`；`auto_pc`/`auto_pgdm` vs `AutoCap`/`autopc`（无下划线）；`improve` vs `Improve`（大写 I）
- naive `cell.lower()` 会误判 decoy → FAIL（关键 discriminating 条件）
- A/B/B2/B3 inventory 规模/命名/计数全不同；B2 to_remove≠B 防硬编码计数；B3 全清 verdict=CLEAN 防 always-FAIL
