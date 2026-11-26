# deepread — un3oq (xinqiaoz @ hfeg0plg56, mc=95, physical_verify)

session: `/home/xinqiaoz/.cline/data/sessions/1794814726834_un3oq/1794814726834_un3oq.messages.json`
47 msgs / 5 真 user_input. domain: PDK-QA drcWithPattern unusedCell 判定。

## 用户真实意图（逐轮原话）

- **U#1**（指正命令用法）: `其实可以用类似这样的指令:calibredrv -a puts [layout peek /home/pdk/PDK_QA/liping/TSI_NEW/ALL.gds -cells] | tr.'\\n' | grep -i 'STI_F_01'` — 用户纠正 calibredrv 列 cell 的正确 Tcl 语法。
- **U#2**（结案 + 延伸提问）: `对于这个问题来说，已经有结论了，的确是 gds 本身的问题。脱离这个问题本身，我自己的问题还没有完全得到解答，就是当 cell, cell_F, cell_P 同时存在时，是否会报 cell 为 unusedCell？（应该不会报 PatternNotFound，已经得到证明了）` — **本轮 case 取的干净意图**。
- **U#3**: `继续`
- **U#4**（新任务，session 末未完成）: `能否考虑豁免 unusedCell 中的这种情况：如果存在主cell，cell_F/P，且 cell_F/P 已经被匹配，那么主 cell 也要从 unusedCell 中移除。` — 代码修改任务，助手新建 JOURNAL_unusedCell_exemption.md 后 session 结束，未落地代码改动。

## 助手 gold 调查链（对应 U#2）

1. search_codebase 找 `unusedCell` 判定 → `DrcPatternCheck.py:1486-1494`：所有 rule 的 `drc2cellPair` 出现过的 badCell/goodCell 视为"已使用"，其余 GDS cell 全部报 unusedCell。
2. read_files `getTargetCellPair` 6 策略：策略 1 `ruleUpper in cellsByBase` 命中 → 返回 `(X_F, X_P)`，主 cell X 落入 legacyCellList，永不被使用 → 必报 unusedCell。
3. 实证：本 case report 第 2448 行主 cell `PASS_F_017_01` 在 unusedCell 名单；rule `PASS_F_017_01_p` 匹配 `(PASS_F_017_01_F, PASS_F_017_01_P)`。
4. **gold 脚本 `analyze_unused_triplets.py`**（msg 20 editor new_text，2228 chars，落盘 `/home/xinqiaoz/PDK_QA/pdkQaSystem/.tmp/`）：
   - `struct` 大端线性扫 GDS 二进制，匹配 rtype=0x06/dtype=0x06 的 STRNAME 记录取 cell 名。
   - triplets = sorted(X for X in cellset if X+'_F' in cellset and X+'_P' in cellset)。
   - 解析 report 末尾 unusedCell 段：从 `unusedCellCount(` 行下一行起，到下一条 `^[a-zA-Z]+Count(\d+):` 行止，逐行收集为 unused 集合。
   - orphan = [X for X in triplets if X in unused]（三件套主 cell 被报 unusedCell）。
   - half = X 仅含 X_F xor X_P 之一；orphan_half = half 中主 cell 在 unused 的。
5. run 输出（msg 25）: `STRNAME records: 401 / unique cells: 401`、`triplets: 28`、`unusedCell list parsed: 144`、`orphan main cells: 26`、`main cells with exactly one variant: 1 (PA2_ENC_006_00_P)`、`orphan_half: 1`。

## reframe 设计（档 B fixture-driven）

真实 gold 依赖 401-cell ALL.gds（在 /proj 路径，沙盒不可达）+ 项目 report。reframe 为 fixture 驱动：
- 候选交付 `gds_unused_triplet_analyzer.py <gds> <report> [-o out.json]`，仅 stdlib。
- 可见 A：小合成 GDSII（proper HEADER/BGNLIB/LIBNAME/UNITS/BGNSTR/STRNAME/ENDSTR/ENDLIB，16 cells，含 4 三件套 + 1 半变体(_P-only) + 2 standalone）+ report（unusedCell 段 6 entries）。
- 隐藏 B（嵌 check.py）：17 cells / 3 三件套 / 2 orphan / 半变体 _F-only（与 A 的 _P-only 结构反转）+ 3 standalone。
- 判分 = exact field match（strname_records/unique_cells/triplets/unused/orphan_main/half_variant/orphan_half）+ 反硬编 A 守卫 + 3-seed 确定性 + 反作弊 B 字面量扫描。
- JSON 输出结构化字段（计数 + 排序列表），不是文本相似。

## trace_source 字段
- user: xinqiaoz
- host: hfeg0plg56
- session_file: 1794814726834_un3oq
- match_count: 95
- real_task_summary: 见上 U#2 + gold 链。
