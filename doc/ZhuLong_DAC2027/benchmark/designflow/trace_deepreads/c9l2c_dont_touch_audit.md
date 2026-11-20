# Deepread — c9l2c · pg_layout dont_touch cell audit

- session_file: `1795143959958_c9l2c`
- user/host: `alan3zh@hfeg0pkn002`
- match_count: 3309 (pg_layout: 1309 dont_touch + power 相关 keyword 高密)
- domain: pg_layout
- trace 规模: 6 messages / 4 user turns / agent 未完成（trace 在助手第一次提问后中断）
- case_id: `EDA-Eval-DesignFlow-DontTouchCellAudit-001`（shard C, r885, track B, tier L1-static-parse）

## 用户真实任务（U#0 原话）

> 读取 ./rtl_power/ 下的 hl22_porting_test_chip_v1.v 和 hl22_porting_test_chip_v1_dont_touch.tcl，对比出 dont_touch 文件中多余的 cell 名，以及总结 dont_touch 中没有遗漏的 cell 名，仅列表输出

意图核心：
1. 解析 .v 收集所有层级实例路径（parent/inst 形式，含中间节点与叶子）
2. 解析 .tcl 收集所有 `set_dont_touch [get_cells <path>] true` 路径
3. 集合差：only_in_tcl（tcl 多余 ghost 路径）+ only_in_v（.v 有但 tcl 漏标的实例）
4. 仅列表输出

## 真实输入文件（.75 上确认存在）

`10.129.2.11:/home/alan3zh/workspace/test_chip/test_chip_v1_svt/power/rtl_power/`

- `hl22_porting_test_chip_v1.v` — 120KB / 2805 行 / 13 个 module / 顶层 `hl22_porting_test_chip_v1`
  - 实例风格：`ModuleType instName (`（如 `TOPTMINVRINGBLK_Blk4120 u_TPTR(...)`、`RingCell u_RingCell_Blk393(...)`）
  - 层级路径示例：`u_TPTR/RingCell_Blk393`、`u_TPTR/LoadBlk_Blk434/LoadCellInst_Blk426`
- `hl22_porting_test_chip_v1_dont_touch.tcl` — 114KB / 1310 行 / 1309 unique `set_dont_touch [get_cells <path>] true`
  - 每行一条路径，路径前缀不含顶层 inst（直接从子 inst 开始，例如 `TOPTMINVRINGBLK_Blk4120/...`）

## 既有 gold parser（.75 上现成）

`/home/alan3zh/workspace/test_chip/test_chip_v1_svt/power/rtl_power/extract_v_names.py` — 用户原 trace 中助手曾尝试调用但 trace 中断；逻辑：strip 注释 → 正则 `^\s*(\w+)\s+(\w+)\s*\(` 抓实例 → 过滤 Verilog 关键字 → DFS 收集层级路径。gold 输出 `compare_report.txt`（仅列表，含 common / only_in_tcl / only_in_v 三段）。

## reframe 选择（档 B, L1-static-parse）

真实 gold 是离线静态解析脚本（无 EDA 工具依赖、无 .oa / db 读写），grounding 几乎零损耗：
- 保留：.v module/instance 解析、.tcl get_cells 路径提取、DFS 层级路径收集、集合差、JSON 输出
- 改动：将"仅列表文本输出"统一为结构化 JSON schema（便于判分 exact-match），并增 top_module 字段
- 不可沙盒化的部分：无（本任务天然 offline）

## 隐藏 fixture B（嵌 check.py，与 A 全异）

合成小网表 `chip_top`（3 个子模块 blk_a/blk_b/blk_c，INV/NAND2/BUF/NOR2/XOR2 叶单元）：
- B .v DFS 收集 12 条层级实例路径（3 个一级 inst + 9 个叶子）
- B .tcl 15 条 get_cells 路径（9 真实 + 6 ghost：i_GHOST0/1/2/3、u_blk_d、u_blk_x）
- common=9、only_in_tcl=6（ghost）、only_in_v=3（.v 有但 tcl 漏标：i_nand2、i_buf2、i_xor1）

## 跨输入守卫 B2

`wrap` 顶层 / `core_x`+`core_y` 子模块 / u_x+u_y 一级 inst / p0/p1/q0/q1/q2 叶单元：
- B2 .v 7 条 v 路径、.tcl 5 条 tcl 路径
- only_in_tcl={u_x/p_GHOST, u_z}、only_in_v={u_x/p0, u_x/p1, u_y/q1, u_y/q2}
- 击败硬编码 B 答案（硬编 B 的候选在 B2 上 v_instances=12≠7 直接 fail）

## 判分（15 条独立可失败条件 a-o）

a exit0 / b 合法 JSON+必需键 / c top_module==chip_top / d v_instances==12 / e tcl_paths==15 / f common==9 / g only_in_tcl==6 / h only_in_v==3 / i only_in_tcl 集合 exact / j only_in_v 集合 exact / k common 集合 exact / l 不相交不变量 / m tcl 集守恒 / n v 集守恒 / o B2 跨输入守卫

§4.9 三假：empty_stub→b（缺 counts 子键）、print_only→o（B2 v=12≠7）、core_deleted→d（v=0≠12），全 FAIL distinct，NEG_RC=0。

## 自验

- ref solve `dont_touch_audit.py` 打包 `reference_submit.zip` 跑 check.py → **PASS 15/15**
- `negative_selftest.py`：ref PASS + 3 neg 全 FAIL distinct
- roundtrip：jsonl test field sha256 == disk check.py sha256 ✓
- k_rationale == k_check == 15 ≥ 8 闸门 ✓

## 意图审计

keep：alan3zh 真实意图（.v vs dont_touch.tcl 对比、列出多余与遗漏 cell、仅列表输出）完整保留。reframe 仅将文本列表输出统一为 JSON schema（便于 exact-match 判分），逻辑零加难、零删减，纯 grounding。U#0 用户原话入 prompt。pg_layout 域 L1-static-parse 子型（与 LayoutHierScrapeDiag 层级解析、AetherSePermAudit SE 审计正交：本例=tcl dont_touch 路径 vs .v 层级实例路径的集合差审计）。2026-11-21 reaudit 后 produce-task 合法。
