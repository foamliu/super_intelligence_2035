# trace_deepread: 1794982956287_uzvua (lucaslu @ hfeg0plg88, mc=88, layout_aether)

## trace 现场抓取
- host: hfeg0plg88 (10.129.8.139), user: lucaslu
- session dir: `/home/lucaslu/.cline/data/sessions/1794982956287_uzvua/`
- `1794982956287_uzvua.messages.json` 688KB, 123 msgs (63 user / 60 assistant)
- 顶层结构: dict{version, updated_at, agent, sessionId, messages, system_prompt}

## 用户真实意图（verbatim, U#0 末尾, slash-command skill-creator 上下文之后）
> 「请开发一个脚本用来刷layout 调用关系」

(用户 U#0 顶部是 `/skill-creator` slash-command 注入的 skill-design 元上下文 ~10KB，与本题无关；真实需求在末行。U#34「没有」是对 agent 问"还有别的吗"的简短回答。其余 61 个 user turn 全是 len=0 的工具结果回执——即 user 只在 U#0 提了一次需求，agent 自问自答多轮澄清后产出脚本。)

## agent 澄清回合（assistant text 提炼）
- U#8「在开始设计之前，我需要先理清一些关键信息」→ 平台 = Aether + pyAether Python API
- U#10/U#12「从 top cell 出发，递归展平层次化调用树」「输出控制台树状图 + CSV」「循环引用：不做检测，假设无循环」
- U#18/U#22 查 AskEDA 知识库确认 pyAether API（aeGetCurDesign / getCellView / getInsts / inst.getName/getLibName/getMasterCellName/getViewName）
- U#33 呈现完整设计方案；U#35/U#37 设计获批准，进入实现
- U#39 参考 `~/Desktop/2_script/CXMT_layout_hier_*.il` 命名风格
- U#47~U#103 多轮 write/edit/重写 + py_compile 语法检查（沙盒无 pyAether，运行报 ImportError 是预期）
- U#120/U#122 交付总结

## gold 交付物（trace 末尾用户接受的结果）
`/home/lucaslu/Desktop/2_script/07Python_tools/cxmt_layout_hierarchy.py` (169 行, 5915B, 已 scp 回核验)

API 链路:
1. `ae.aeGetCurDesign()` → cvId (有 `.libName/.cellName/.viewName` 属性)
2. 非 layout view 时 `ae.dbCellViewExist(lib,cell,'layout')` 切到 layout
3. `ae.getCellView(lib,cell,view)` → topCv
4. `_build_hierarchy(cv, visited)` 递归: `cv.getLibName/getCellName/getViewName` + `cv.getInsts()` → 每个 inst `getName/getLibName/getMasterCellName/getViewName` → `ae.getCellView(master_lib,master_cell,master_view)` 递归；visited 字典 {(lib,cell,view):True} 防重展
5. `_print_hierarchy` box-drawing (└──/├──/│) 树打印
6. `_write_csv` 8 列 CSV: `Level,FullPath,Lib,Cell,View,InstanceName,ParentCell,InstanceCount`，文件名 `<topcell>_layout_hierarchy.csv`
7. `_collect_cells` 统计 unique cells；`total_lines-1` = instance rows；`ae.aeMessage` 打印统计 + runtime

## reframe 决策（档 B fixture-driven）
真实 Aether + 用户私有 design 不可沙盒复现 → fixture 驱动:
- **mock pyAether 模块**（visible asset `pyAether_mock.py.txt` = judge 内嵌同源）：由 `hierarchy.json` spec 驱动，提供 `aeGetCurDesign/dbCellViewExist/getCellView` + `MockCV`(getLibName/getCellName/getViewName/getInsts) + `MockInst`(getName/getLibName/getMasterCellName/getViewName) + `aeMessage/aeError`。spec 格式 `{root, cells: {"LIB|CELL|VIEW":[{inst,lib,cell,view},...]}}`。
- **A (visible)**: hierarchy_A.json (MYLIB/TOPCHIP + ANA/ADC + DIG/COUNTER + IO/PADRING + STD/INV,NAND2,DFF; 7 unique, 7 inst rows, depth 2)
- **B (hidden, 嵌 check.py)**: hierarchy_B (LIB_T/TOP + LIB_A/A_CELL + LIB_X/X_CELL + LIB_LEAF/LEAF1,LEAF2,LEAF3 + LIB_B/B_CELL + LIB_C/C_CELL; 8 unique, 9 inst rows, depth 3; LEAF2 在两处出现但都是叶→visited-dedup 不可见，输出确定)
- A/B 名字完全不相交（反硬编）；unique/行数/深度都不同（反硬编计数）
- 候选交付 `cxmt_layout_hierarchy.py`，judge 在 run dir 放 `pyAether.py`(mock) + `hierarchy.json`(B) + 候选脚本，`python cand.py` (cwd=run dir) 运行
- 15 teeth (a-o): exit0 / CSV 存在 / 表头 / 行数=9 / root 行 / u0 行 / q0 行(最深叶) / u2 行(level-1 叶) / Level==dot-count / ParentCell 跨行一致 / (lib,cell,view)∈B 集合 / InstanceCount==实际子行数 / stdout box-drawing+header / unique-cells=8 / instance-rows=9；另 3-seed 确定性

## gold 参考解相对 trace 原始交付的修正
trace 原始 `_write_csv` root 行写法 `f'{"",}'` 是一处 f-string 跨版本 bug：
- py3.7 (.75 沙盒): `f'{"",}'` → 空串（CSV root 行 InstanceName 空，符合直觉）
- py3.10+ (评测主机): `f'{"",}'` → `('',)`（tuple 字面量渲染，CSV root 行 InstanceName = `('',)`，破坏 8 列结构）

参考解 `reference/.../cxmt_layout_hierarchy.py` 改为 `f',{parent_cell}'`（InstanceName 字段直接空），跨版本一致产出 `0,TOP,LIB_T,TOP,layout,,,4`。negative/no_recurse.py 同步修。此修正仅影响 root 行 InstanceName 字段格式，不改递归核心逻辑。

## 自验
- `negative_selftest.py`: ref PASS 15/15 ✓；empty_stub FAIL(b) ✓；print_only FAIL(b) ✓；no_recurse FAIL(d, 行数 5≠9) ✓
- §4.9 三假提交全 FAIL ✓
- build_jsonl.py --shard C: C.jsonl 556→557 ✓
- roundtrip: jsonl test sha == disk check.py sha (04442eb0ff679edd) ✓
- k_rationale == k_check == 15 ✓

## 与现有 C 域 case 的正交性
- 现有 layout_aether case: TapPcellBot-001(SKILL PCELL 开关), MeaCrossSection-001(截面测量), RedundantPinRemoval-001(删冗余 pin), WireWidthSpaceRuler-001(线宽线距标尺)
- 本 case: pyAether **layout hierarchy scraper**（递归调用关系 → tree+CSV），子型首例，与上述正交
- vs AetherHierNavAnalyze-001 (A 线, schematic 层级导航+分类): 本 case 是 **layout** 视角 + **递归全树展平+CSV 导出**，非"当前 edit 层级分类"，正交
