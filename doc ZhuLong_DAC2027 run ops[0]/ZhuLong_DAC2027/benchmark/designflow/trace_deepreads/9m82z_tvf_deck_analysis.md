# trace_deepread — 9m82z · Calibre TVF DRC deck 分析 (ellawu @ 10.129.2.14)

**session**: `1791889999605_9m82z` · **user**: ellawu · **host**: 10.129.2.14 (hfeg0pkn005) · **agent**: lead (deepseek-v4-flash) · **cwd**: /home/ellawu
**time**: 2026-10-13 11:13 → 2026-10-16 01:21 (UTC) · **status**: failed (terminal_marker=failed_external_process_exit) · **mc**: 26 (keywords: drc×1617 calibre×32 .gds×15 → physical_verify heavy)
**size**: 44 msgs (23 user / 21 assistant) · 798KB messages.json · attachment `G5_AA_PG_dummy_fill_for_Logic.rule` (2106 行, 209KB, CXMT G5 工艺 AA/PG dummy fill Calibre TVF deck)

## 用户真实意图（4 个 user 轮，均为「提出需求」类）
- U#0 (msg[0]): **「分析一下这个脚本」** + 附件 `G5_AA_PG_dummy_fill_for_Logic.rule`
- U#1 (msg[8]): **「解释每一句」**
- U#2 (msg[12]): **「画一个关于源漏级栅级的结构示意图」**
- U#3 (msg[43]): **「整理框架」** ← 末轮，session 在此后 failed_external_process_exit，助手未交付该轮响应

按 2026-11-15 §二 reaudit：analysis-Q&A / explain 类全部恢复为可造。本 session 是典型的「分析/解释真实 EDA 脚本」任务，属合法 user 意图。

## 助手实际交付（trace 内真实产物，构成 gold 候选）
1. **msg[7] 全面分析报告**（9098 字 markdown）：结构总览表（7 段行号范围）、层派生分解（NW/PW/DIF/PSD/NSD/PG_MOS/SUB/PACT/NACT/GATE...）、关键设计规则常量表（PG_Dummy_Vert_Width=0.211 等 15 参数）、填充区域计算（insert_1/2/3/4/more_PGDummy_Space_Region 公式 + 计算值 1.257/1.702/2.147/2.592/3.716）、HORI/VERT PG Dummy 插入逻辑、阻塞层、特殊区域（SUB1_1~4/ZigZag/ESD/Efuse）。
2. **msg[11] 逐行解释**（32372 字）：按区块逐句解释每条活跃语句（TVF 声明/VERBATIM 版本史/DRC 环境/LAYER MAP/层派生/Tcl set/SETLAYER/DFM/OUTPUT）。
3. **msg[41] MOS 结构示意图**（SVG `mos_structure_diagram.svg`）：matplotlib 沙盒不可用后改手写 SVG，含 NMOS/PMOS AA、PG_DUMMY、间距标注 0.078、legend。
4. U#3「整理框架」未交付（session 在响应前 failed）。

## .rule deck 结构（分析对象，2106 行）
- **TVF 头** (1-3): `#! tvf` + `namespace import tvf::*`
- **VERBATIM 版本史** (4-67): 26 个版本 v1.0(2023/09/04 IceyMa)→v5.5(2026/08/08 cedard)，作者 IceyMa/hana.song/cedard
- **DRC 环境** (68-110): LAYOUT PATH "AAAAA.gds", PRIMARY "AAAAA", SYSTEM GDSII, RESOLUTION 1, PRECISION 10000, UNIT LENGTH U, DRC RESULTS/SUMMARY/MAXIMUM RESULTS ALL/MAXIMUM VERTEX 199/KEEP EMPTY YES, FLAG ACUTE/OFFGRID/SKEW, #DEFINE, INCLUDE calibre.layer, LAYER MAP 235 DATATYPE 250 20000, LAYER PR_BOUNDARY 20000
- **层派生** (119-189): 48 个 `NAME = OP ...` (COPY/OR/AND/NOT/SIZE/INTERACT/COINCIDENT) — PRB_RANGE/CHIP/SA/SWD/SWC/CORE/ARRAY/PERI/BULK/NW/PW/DIF/PSD/NSD/PDIF/NDIF/PG_MOS/PG_HH/SUB/PACT/NACT/PTR/NTR/GATE...
- **Tcl 参数** (212-269): 39 `set` (37 去重后) — PG_Dummy_Vert_Width=0.211/Hori_Width=0.192/MinSpace=0.234/MinLength=0.675/AT4_PG_Dummy_Space=0.078/STDCELL_Height=7.09 + insert_1/2/3/4/more [expr ...]
- **DRC SELECT CHECK** (1525-2046): 33 块（BLK_poly/PG_POLY/.../PGDummy_FILL_REGION...）
- **OUTPUT 块** (2080-2089): 活跃 `DFM RDB GDS "AA_PG_DUM_Logic.gds"` + `PGDummy_FILL_REGION 30 4` + `PROPERTIES APPEND _auto_pgdm`（另有 3 个 `#if $env(Run_Type)` 注释掉的替代 OUTPUT 块）
- **统计**: total=2106, active=973, commented=859, blank=274

## 档 B reframe（A 档 gold = free-text markdown 分析报告，无 ≥8 独立硬断言牙 → 档 B）
**reframe = `tvf_deck_analyze.py`**：纯 stdlib，CLI `python3 tvf_deck_analyze.py <deck> <out_json>`，把助手在 trace 中真实做的「读 deck + 抽结构」抽离成可离线复刻的结构化 JSON 报告工具，9 个顶层键：tvf_header / version_history / drc_environment / layer_derivations / tcl_params / drc_select_checks / output_block / layer_map / statistics。输出 sort_keys 确定性 JSON。
**visible A** = 真实 G5 deck 的忠实结构摘录（288 行，verbatim 行 1-110/119-189/212-269/1525/1545/2080-2106，全产物 2106 行原档保留在本深读笔记 + .75 沙盒已验证 ref analyzer 跑全档通过）。
**hidden B** = 合成 ST22 工艺 deck（139 行，完全不同：BBBBB.gds/PRECISION=1000(反 A 10000)/RESOLUTION=10(反 A 1)/v0.9-v3.2 alice/bob/carol/dave/LAYER MAP 240...30000/层名 FIN/WELL/GATEPOLY/gds=ST22_PG_DUM_Peri.gds）。
**check.py** 在隐藏 B 上跑 SUT 脚本，16 条独立断言（a-p）：zip 合法+py_compile / B exit0+合法JSON / 9 顶层键 / tvf_header / version_history 8 条首末 / drc_env 4 键 / layer_deriv 23 含 FIN+GATEPOLY / tcl_params 20 含 DUMMY_VERT_WIDTH+is_expr+GRID / drc_sel 10 首块 / output_block gds+layers+properties / layer_map / statistics 4 值+和守恒 / 反硬编码(不得=A 的 10000/1/AA_PG_DUM_Logic.gds/235...20000) / 确定性 2x byte-identical / 错误处理缺失文件非零退出。

## 自验
- ref PASS 16/16 (a-p) on hidden B
- 3 negative 全 FAIL (empty→a / print_only→f / hardcode_a→f)，§4.9 (a)(b)(c) 三假全 FAIL
- ref analyzer 跑真实全档 A 通过 (26 versions, gds=AA_PG_DUM_Logic.gds, total=2106)
- 确定性 2x byte-identical
