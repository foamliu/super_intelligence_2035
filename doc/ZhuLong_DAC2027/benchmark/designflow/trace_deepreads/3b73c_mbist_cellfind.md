# deepread: 1793865643606_3b73c (MBIST cell-find, schematic_netlist)

- **trace**: 1793865643606_3b73c / m1wang / hfeg0pkn002(10.129.2.11) / mc=251 / schematic_netlist
- **single-turn**: 218 msgs, 1 user message, no follow-up acceptance (session ended mid-generation of aux scripts)
- **user U#0 原文**: "你是一个数字电路设计工程师，你现在的项目是长鑫存储的DEJOA项目，研究DDR5的电路，你负责的模块是MBIST，即内存内建自测试，请根据Virtuoso环境的DEJOA项目电路，从TOP层出发，查找该电路中名称中带有MBIST的所有cell,并可视化显示出其在电路中的分布，方便你日常查找CM电路模块的路径"
- **tool_use freq**: RAG_MCP_Server__search_apis×49 / editor×34 / run_approved_command×19 / read_files×12 / RAG_get_api_details×7 / SandBox_run_code×2

## 真实意图
从 TOP 层 schematic 出发，递归遍历层级，找出所有 master cell 名 case-insensitive 含 "MBIST" 的 instance，记录层级路径，产出分布报告 + 可视化树，供日常查找 CM 电路模块路径。

## assistant 路径
1. 大量 RAG 搜 pyAether API（emyBaseNameFindInsts / dbFindInst / aeGetInstHier / emyRefGetMasterName / dbTraverseDesignWithCB 等）。
2. run_approved_command 探查项目文件系统（/proj/dejoa/V0/libs/TECHLIB；PROJ_NAME=dejoa），发现 DRCPA 既有模板 `find_cm_cells.py`(filesystem scan + tree/distribution print) + `generate_CM_Table.il`。
3. **交付物** `find_mbist.il`（SKILL, 4130 bytes, 96 lines, sha256 cc5064fd...）—— 被 assistant read_files 回读确认 "clean and correct"。核心 `findMBIST` procedure：
   - `dbOpenCellViewByType(lib cell view "sche" 'r)` 开 TOP
   - 递归 `_trv(cv path indent)`：`inst~>master~>cellName`，`rexMatchp("[Mm][Bb][Ii][Ss][Tt]", cn)` case-insensitive 匹配 → 记录 `(inst~>name cn ln fp)`（fp=full path），printf 路径表
   - 跳过 primitive lib（basic/analogLib/ahdlLib/philLib/primitives）
   - 汇总 `length(mbistList)` + 写 `mbist_instances.txt`（# / Instance / Master / Path 表）
   - `findMBISTInteractive()` 用 `geGetEditCellView()` 取当前窗口
4. 欲另写 find_mbist.py(pyAether+filesystem+HTML) / find_mbist.sh，但反复撞 editor 6000 字符上限，session 在 gen_more.py editor 失败处中断。

## A-faithful 判定：不可行
- 交付物 find_mbist.il 是 **live-Virtuoso SKILL**（dbOpenCellViewByType / cv~>instances / rexMatchp），依赖 live OA db，不可附加到离线 test。
- 无 user-accepted 离线产物（mbist_instances.txt 是 SKILL 运行时产物，非便携输入）。

## B 档 synthesized（#338 合成 plan）
取 trace 可移植 facet = **层级遍历 + 名称模式匹配 + 分布报告**，降级为离线 text-in→structured-out：
- **gen_mbist_cell_find.py --spec <hier.json> --outdir <dir>**：读层级 instance tree JSON(top/lib/pattern/tree)，递归遍历，收集 master cell 名 case-insensitive contains pattern 的 instance（path/inst/master/parent/depth），产 cells.json(n_matches/matches/by_master/by_parent/by_depth) + distribution.md(by-master 表/by-parent 表/by-depth 表/hierarchy tree/summary)。
- **A**(spec_A.json): pattern=MBIST, top=DEJOA_TOP, 6 matches, masters={MBIST_CTRL,MBIST_DECODER,MBIST_RA,MBIST_WRAPPER,MBIST_CORE,MBIST_MONITOR}
- **hidden B**(spec_B.json): pattern=DFT, top=DDR5_TOP, 7 matches, masters={DFT_WRAPPER,DFT_MUX,DFT_CHAIN×2,DFT_COMPACTOR,DFT_SEL,DFT_ISOCELL}（与 A 全不相交，n_matches 7≠6）
- **hidden B2**(spec_B2.json): pattern=SCAN, top=PHY_TOP, 3 matches, masters={SCAN_EN,SCAN_MUX,SCAN_CHAIN}（与 A/B 全不相交，n_matches 3≠6≠7）
- **反硬编码轴**: pattern A/B/B2 = MBIST/DFT/SCAN 不同(硬编 MBIST 者 d FAIL)；top 不同(硬编 DEJOA_TOP 者 m FAIL)；masters 全不相交(硬编 A masters 者 g FAIL)；n_matches 6/7/3 三不同(硬编常量者 e/n FAIL)；B 有 DFT_CHAIN×2 测 by_master 计数。
- **check 16 条件 a-p**: a(zip 无泄漏)+b(py_compile)+c(B-run exit0+cells.json+distribution.md 非空)+d(pattern==B)+e(n_matches==独立B)+f(matches 五键+len==n_matches)+g(by_master==独立B)+h(by_parent==独立B)+i(by_depth==独立B)+j(md 含 pattern+top+total)+k(md by-master 表含每 B master)+l(md hierarchy tree 段含 B path)+m(反硬编码:源码无 A 字面量 DEJOA_TOP/MBIST_CTRL 等 + A-run n_matches==独立A)+n(跨输入 B2 pattern+n_matches + 确定性 3x sha256)+o(matches master 全 case-ins contains pattern)+p(by_master/by_parent count 之和==n_matches)。
- **negatives**: naive_empty_shell(→c) / hardcode_a(→d/e/g/m) / hardcode_b(→m) / print_expected(→c) / drop_by_parent(→h) / ref_core_deleted(→f/l) / no_match_rule(→o)。§4.9 三假=empty+print_expected+ref_core_deleted。
- **断言闸门** k_rationale=k_check=16。

## 真实 spec/拓扑要点（供 prompt 背景）
- DEJOA = 长鑫存储 DDR5 项目；MBIST = Memory Built-In Self Test（内存内建自测试）
- SKILL 匹配正则 `[Mm][Bb][Ii][Ss][Tt]`（case-insensitive contains）
- 跳过 primitive lib：basic/analogLib/ahdlLib/philLib/primitives
- DRCPA 既有同类工具 find_cm_cells.py（CM = Chip/Test Mode cell，filesystem scan + tree + distribution）
