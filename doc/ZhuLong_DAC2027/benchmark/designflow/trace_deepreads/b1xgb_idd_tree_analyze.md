# 深读笔记：b1xgb — xiaoyu1d IDD 电流树分析

## trace 概要
- session: `1792042184377_b1xgb`，user=xiaoyu1d，host=hfeahpc501(10.129.33.24)，mc=53
- 规模：844KB / 91 msgs / 2 user turns / 模型 deepseek-v4-flash
- 域：analog_context（IDD 漏电流分析，离线 CSV 解析，无实时 EDA 工具）
- 选中原因：mc=53 + D-dominant(cmos:628/netlist:402/analog:144) + fresh(不在 4-shard 台账) + xiaoyu1d 无既有 D case + 干净 single-produce + 91 msgs 可一轮交付

## 任务原文（2 轮）
- **U#1**：给 idd2n 的 vdd2h/vdd1 两个 CSV 路径（finesim MatrixRun 导出），「分析哪一些比较大，有还能优化的空间吗？……给我做一个表格，把你觉得比较大的，还有能降低电流空间的模块给我列出来」
- **U#2**（澄清）：给 4 个 CSV 路径（idd2n/idd2p × vdd2h/vdd1），「把你认为比较大电流、有较大改善空间的模块列到最左边，中间给出 cell 的路径（哪个模块的子模块），再往右是子模块贡献电流，最右是占顶层模块的比例。只需要关注 4 个顶层模块 `xi_rowred768top_34 / xi_rastoxdecdrv_301 / xi_raschain / xi_ras_vdd2h_0`，cell 路径从这 4 个模块开始，关注子模块电流分别占各自父模块的比例」

## CSV 格式（finesim IDD current 导出）
`idd,instHdl,parentHdl,localName,cellName`
- idd=电流(A,浮点)；instHdl=实例句柄(`_e_NNNN`)；parentHdl=父句柄(根节点的 parent 是名字如 `tlc`)；localName=本地名(`xi0`/`xmmp0`)；cellName=单元类型(`ptn`/`buflx24`/`sealringpath`)
- 样例：`0.021741,_e_1020,tlc,xi0,sealring_metal_cmosip`；`0.010870,_e_1021,_e_1020,xi_sealringpath_0,sealringpath`
- 层次由 instHdl/parentHdl 构成树；根节点 parentHdl 是命名顶层（不在 instHdl 集合中）

## assistant 工具链
- read_files 读 4 个 CSV → 编辑器写 `analyze_target4.py` → run_approved_command 跑 → 输出截断 → 改写 `analyze_target4_v2.py` 聚焦版 → 跑出 4 模块报告表
- 核心机制：解析 CSV → instHdl/parentHdl 建树 → 对每个目标模块遍历子树 → 求子模块电流和 + 占父比例 → 排序出表
- 最终交付：4 个 markdown 表（每模块：子模块 | CellName | 电流 | 占父% | 路径）+ 跨 corner/rail 总电流概览表

## B-grade 合成设计（IddTreeAnalyze-001）
- **A（可见）**：`idd_tree_A.csv` 21 行，3 目标(tA_rowdec/tA_sachn/tA_clkgen)，前缀 hA/tA_/xiA/xmmpA + example_report_A.json
- **B（隐藏）**：`idd_tree_B.csv` 27 行，4 目标(tB_rowred/tB_sachn/tB_zeroleak/tB_leaf)，前缀 hB/tB_/yjB/ymmpB（与 A 完全不相交），植入 4 异常：
  - tB_rowred：单子 yjB_big 贡献 96.86%（叶 ptnB@8mA 异常大）
  - tB_sachn：3 级深子树（yjB_sa1→ymmpB3→yjB_inv/inv2）
  - tB_zeroleak：全零电流分支（测 ratio=0 边界）
  - tB_leaf：目标本身是叶子（测 0 子节点 + largest_leaf 空边界）
- **SUT 交付**：`idd_tree_analyze.py <csv> <targets> <out_json>`，纯 stdlib，禁 numpy/pandas/scipy/subprocess/socket/eval/exec + 禁 B 字面量
- **check.py 15 条件 a-o**：独立 oracle(迭代 bottom-up by depth，与 ref 递归 DFS 结构不同) + 子进程真跑 B + 反硬编码跨输入 C(hC/tC_，SUT 未见过) + 3-seed sha256 + largest_leaf 后代-only + lexicographic cellName 平局
- **维度正交**：vs SpfCapResAnomaly-001(SPF 寄生 cap/res 异常) / PexNodeCapExtract-001(节点电容) / DriverTrace-001(驱动溯源) —— IDD 电流树+子模块占比分析，机制不同

## 自验
- check.py standalone: PASS（ref 跑 B 15/15）
- negative_selftest: ref PASS + neg_empty/neg_print/neg_hardcode_a/neg_core_deleted 全 FAIL
- §4.9 三假(empty/print/core-deleted)全 FAIL；3-seed sha256 一致
- k_rationale = k_check = 15 ≥ 8 ✓
