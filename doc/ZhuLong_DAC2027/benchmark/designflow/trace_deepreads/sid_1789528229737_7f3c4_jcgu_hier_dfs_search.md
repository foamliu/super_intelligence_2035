# deepread — sid 1789528229737_7f3c4 (jcgu / hfeg0pin003 / mc=175 / layout_aether)

## meta
- host: hfeg0pin003 (10.129.32.236), user: jcgu (NEW — no prior shard-C case)
- 162 msgs, 1.13 MB, cwd /home/jcgu, status (trace 末轮无显式用户接受，但 bug-fix 交付完整+用法)
- model: (cline default)
- tool_use: RAG_MCP_Server__search_apis 32 + editor 25 + RAG_MCP_Server__get_api_details 12 + read_files 7 + list_allowed_files 4 + run_commands 1

## user turns (verbatim)
- UI#0 (idx0): `open my home folder` — generic file-open, 非 design-flow seed
- UI#1 (idx8): `新开一个terminal，打开我的home文件夹` — generic
- UI#2 (idx10): `启动aether` — launch
- UI#3 (idx20): `查看我启动的aether，PID是16135，在aether上创建一个ztest的library，并创建一个test的layout view` — create lib+cellview (delegation seed，但简单创建任务，gold 不丰富)
- UI#5 (idx37): `执行脚本报错 UnicodeDecodeError 'ascii' codec can't decode byte 0xe5` — bug report (root-cause) → hint
- **UI#6 (idx41) / UI#7 (idx81) / UI#8 (idx140) — A-档 seed（逐字原文，提出需求+目标+思路，未给根因/修复）**:
  > 帮我写一个pyaether脚本，在layout中by hierarchy查找某个cell，思路是逐层检查所有的instance，看instance name有没有跟目标cell匹配的，如果查到匹配的，就输出对应的hierarchy路径，直到查到最低层，每遇到instance所属library为TECHLIB时，就停止该路径的查找，而继续其他路径的查找
- **UI#9 (idx156) — root-cause/fix 轮（用户点根因）→ hint，不进 prompt**:
  > 测试了一下，查找的结果不全，比如从level0开始查找，level1中有4个instance下面都有目标cell，而该脚本只查找了其中2个instance，另外2个instance完全没有查找，分析一下是什么原因

## assistant 主线（gold 链）
1. UI#3 create_ztest_lib.py：emyInitAether + aeIpcGetPid 校验 PID 16135 + dbCreateLib(ztest,/home/jcgu) + dbNewCellView(ztest,test,layout) — RAG 查 dbCreateLib/dbNewCellView/aeGetCurDesign/emyInitAether/aeIpcGetPid/aeOpenDesign
2. UI#6-8 三次 refine 同一需求（用户重述加细节）→ assistant 写 search_cell_by_hierarchy.py（试 aeFindHierarchy/dbGetHierTree）→ search_cell_hierarchy_dfs.py（DFS + 全局 visited）→ **find_cell_in_hierarchy.py（最终版，DFS + per-path path_ids 修复）**
3. RAG 查询链（32 次 search_apis + 12 次 get_api_details）：aeFindHierarchy/dbGetHierTree/dbFindInst/aeGetInstHierPath → dbInstanceQuery/emyBaseNameFindInsts → dbOpenCV → emyScalarInst/emyBitInst/emyDesign/emyLib → emyInstGetBaseNameString/emyInstGetBaseName → emyDesignGetLib/emyRefGetMasterName → emyRef/emyDesignGetName → emyDesign.getBlock/getInsts
4. **KEY BUG FIX (idx159)**：assistant 诊断 UI#9 — `_dfs` 用 `seen = set()` 全局共享 `id(design)`，当 level1 的 4 个 instance 中 I0/I2 引用同一 master cellA（id=100）、I1/I3 引用同一 master cellB（id=200）时，I2/I3 的 master 已在 seen 中 → 被错误跳过（漏查 2 条路径）。**修复**：`seen`（全局）→ `path_ids`（当前递归路径上的 visited set，`cur_ids = path_ids | {id(design)}` 拷贝+追加，兄弟间不共享）。循环保护仍有效（cellA→cellB→cellA 第三层 cellA 已在 cur_ids 中跳过）。

## gold 算法（find_cell_in_hierarchy.py 最终版）
- `find_cell(lib_name, cell_name, view_name="layout", target=None, stop_lib="TECHLIB")` → list of match dict
- `emyInitAether("-adv")` + `ae.dbOpenCV(lib, cell, view, "r")` 开顶层 design
- `_dfs(design, target, stop_lib, path, results, path_ids)`：
  - `path_ids` = 当前递归路径上的 `id(design)` 集合（per-path，兄弟不共享）
  - `if design is None or id(design) in path_ids: return`（cycle 防护）
  - `cur_ids = path_ids | {id(design)}`（拷贝+追加，不影响兄弟）
  - 遍历 `design.instances`：`_inst_name(inst)`（emyInstGetBaseNameString）+ `_master_info(inst)`（inst.getMaster() + emyDesignGetLib + master.cellName）
  - 匹配 `mcell == target` → 记录 {inst, lib, cell, path, depth}
  - `mlib == stop_lib` → continue（不下钻，同级继续）
  - 递归 `master = inst.getMaster()` → `_dfs(master, target, stop_lib, cur_path, results, cur_ids)`
- 真实 pyAether API（gold 用）：emyInitAether / dbOpenCV / emyCdbaNS / emyString / emyInstGetBaseNameString / emyDesignGetLib / inst.getMaster / design.instances / master.cellName

## 真实 pyAether API 表（从 RAG get_api_details 调用记录）
- emyInitAether / aeIpcGetPid / dbCreateLib / dbNewCellView / aeOpenDesign
- dbOpenCV / emyCdbaNS / emyString / emyInstGetBaseNameString / emyInstGetBaseName
- emyDesignGetLib / emyRefGetMasterName / emyDesign / emyLib / emyScalarInst / emyBitInst
- emyDesignGetName / emyRef / dbInstanceQuery / emyBaseNameFindInsts / aeFindHierarchy / dbGetHierTree

## A-档 合规判定
- UI#7 逐字 = 提出需求 + 详细思路（逐层 DFS / instance name 匹配 / 输出 hierarchy 路径 / TECHLIB 停止 / 同级继续），**未给根因 / 未给修复方案** → ✅ A-档 seed 合规
- UI#9 = 用户指出根因（查找结果不全 + 具体现象）→ 🚫 不作 seed（hint，不进 prompt）
- gold 依赖 live Aether（emyInitAether/dbOpenCV/inst.getMaster/OA 库 ztest）→ .75 sandbox 不可达 → A-disqualified → **B-档 synthesized L1-boundary**（捕获可验子任务 = pure-Python hierarchy DFS 算法 + per-path visited 修复 + TECHLIB stop + cycle detection）

## 与既有 layout_aether case 区别
- HierJump-001 / FindCircuitByPath-001 = 按已知 hierarchy **路径字符串**逐级 descend 打开 cellview（path-string → open）
- 本案 = 按目标 **cellName 在整棵 hierarchy 树中搜索**所有匹配路径（search-by-cellname，find all paths）+ per-path visited vs global seen 的算法 bug-fix
- 主题独立：搜索 vs 导航

## case 计划
- ID: EDA-Eval-DesignFlow-HierSearchDFS-001
- domain: layout_aether, A-档 seed (B-档 synthesized L1-boundary)
- 资产: A=inputs/{hierarchy_A.json + task_brief.md + prompt.txt(UI#7 verbatim + 沙盒注)}；hidden B/B2/B3（结构不同，共享 master id 触发 global-seen bug）
- gold: find_cell_in_hierarchy.py（pyAether API + per-path path_ids DFS + JSON 报告 CLI）
- check.py: stub-driver（fake pyAether 缓存 master by (lib,cell) → 同 master 同 id → 击穿 global-seen naive；候选必须用 per-path visited 才能找到全部匹配）+ ≥8 断言
- 关键判分维度：①找到全部 N 条匹配路径（per-path visited 正确性）②TECHLIB stop 不下钻但同级继续 ③cycle 不死循环 ④跨输入 B2 守护 ⑤B3 空 top 守护 ⑥确定性 ⑦真实 pyAether API 名 ⑧JSON 结构
