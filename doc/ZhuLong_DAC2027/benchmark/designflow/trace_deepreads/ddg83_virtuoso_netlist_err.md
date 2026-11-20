# Deepread — 1793964715214_ddg83 (zhililu@hfhds219)

- mc=46, NMSG=28, NU=17, domain=schematic_netlist
- round #476 → case `EDA-Eval-DesignFlow-NetlistMasterDiag-001`

## 真实任务
Cadence Virtuoso ADE Explorer 跑 netlist，每个 point 都报 `Failed to create point netlist because there are errors during design netlist creation`，用户粘贴了 ADE netlister 的报错日志（Service44.log 的 NewPoint / Failed 事件流）问"这是什么原因"。

## agent 流程（28 msgs / 17 user）
- U0: 粘贴 netlister 报错日志（4 个 point 的 NewPoint + Failed 事件，logFile 指向 Service44.log）
- A1: get_agent_policy_status + list_allowed_files(logs0 目录) + skills(ask-eda 问 netlist 失败一般原因)
- A5/A7/A9/A11: read_files(Service44.log) 多段读 (61-260, 260-424, 304-411)，找到真正的 OSSHNL-366 报错行
- A13: list_allowed_files(workdir) + search_codebase(rmx5ca_dbc/rmx4ca_dbc/TS_RC_1/TS_Aanlog_core)
- A16: read_files(cds.lib) — 本地 cds.lib INCLUDE 共享 cds.lib
- A18: read_files(共享 cds.lib) + list_allowed_files(qi1zhang/T_sensor_dbc) — 发现 T_sensor_dbc 映射到别人(qi1zhang)目录
- A21/A23: list_allowed_files(35HDBC 库) + list_allowed_files(rmx5ca_dbc/rmx4ca_dbc/rm5ca_mxb_dbc 目录) — rmx5ca_dbc/rmx4ca_dbc 全 ENOENT，rm5ca_mxb_dbc 存在
- A27: 给出根因 + 解决方案

## 根因（A27 结论）
- Service44.log 第 337-340 行关键报错：
  - `*WARNING* (DB-270337): dbGetInstHeaderMaster: Failed to open cellview 'rmx5ca_dbc symbol' from library '35HDBC' ... instantiated in cellview 'T_sensor_dbc/TS_RC_1/schematic'`
  - `ERROR (OSSHNL-366): Netlisting failed because the instance 'R33' in cellview 'T_sensor_dbc/TS_RC_1/schematic' is bound to an invalid placed master '35HDBC/rmx5ca_dbc/symbol'. Ensure that the specified placed master exists and is included in the list of reference libraries in the cds.lib file.`
- cds.lib：`INCLUDE /proj/lacaa/TV1_DBC_Virtuoso/cds.lib`；共享里 `DEFINE 35HDBC /proj/lacaa/TV1_DBC_Virtuoso/libs/35HDBC` → 软链 PDK `…/als/lacaa/0.2.9/dbc_vir/35HDBC`
- 库里**不存在** rmx5ca_dbc / rmx4ca_dbc（ENOENT），实际存在的是 rm1ca_dbc / rm2ca_dbc / rm3ca_mxa_dbc / rm4ca_mx_dbc / rm5ca_mxb_dbc 等
- 结论：原理图实例绑定的 master cellview 在当前 PDK 版本(0.2.9/dbc_vir)里已不存在（PDK 升级 cell 被重命名/删除，原理图引用未跟新）→ OSSHNL-366 netlist 失败，每个 corner/point 重复触发
- 解决：打开 schematic 替换失效实例为现存 cell（rm5ca_mxb_dbc / rm4ca_mx_dbc），或切回含旧 cell 的 PDK 版本；注意 T_sensor_dbc 指向别人(qi1zhang)目录需协作

## 合成方案（B-grade synthesized L2）
真实 PDK 库 / cell 名 / Service44.log 私有不可复刻 → B-grade 合成：
- **A（可见）**：合成 netlister_A.log（Virtuoso netlister 日志：4 point 失败 + DB-270337 警告 + OSSHNL-366 报错）+ cds.lib_A（INCLUDE shared_A.cds.lib）+ shared_A.cds.lib（DEFINE LIB_A/DECOY_A）。A 的缺失 master = LIB_A/invA_dbc/symbol，实例 R0，schematic topA/clkdivA/schematic。
- **B（隐藏，判分用）**：不同库/cell/实例/schematic/point 数。B 的缺失 master = RESLIB_B/nandB_dbc/symbol(实例 I2, topB/bufchainB/schematic) + RESLIB_B/norB_dbc/symbol(实例 I5, topB/clkgenB/schematic)；5 point 失败；cds.lib_B INCLUDE shared_B.cds.lib（DEFINE RESLIB_B/ANOTHER_B）。A/B 的 library/cell/instance/schematic/point 数全不同，反硬编码。
- **交付**：`netlist_master_diag.py`（CLI: log + cds.lib → JSON）。解析 OSSHNL-366 抽 instance/instantiated_in/library/cell/view；DB-270337 补充；"Failed to create point netlist" 计 point_failures；cds.lib DEFINE + INCLUDE 递归解析 library_paths；missing_cellviews 按 (lib,cell,view) 去重，OSSHNL-366 为权威源（带 instance）。
- **判分**：check.py 12 条件 a-l（k_check=12，与 test_rationale k=12 对齐）：
  a 跑通B出JSON / b 四顶层键 / c missing_cellviews 五字段 / d B 恰两条缺失 master 全字段对 / e view==symbol / f errors==2 且 code==OSSHNL-366 / g library_paths 含 INCLUDE 递归 RESLIB_B+TOPB / h summary 四计数 / i 反硬编码 A 出 invA_dbc 不泄露 B 名 + LIB_A 解析 / j 3-seed 日志行打乱 (lib,cell,view) 集合一致 / k 确定性 sha256 / l 源码不含 B 专属字面量
- **自验**：ref PASS 12/12 + §4.9 三假(fake_empty→a / fake_print_expected→i / fake_core_deleted→c)全 FAIL + 2 naive(naive_literal→c / naive_substring→d)全 FAIL
- check.py sha 814f1512a6 size 13145 · solution.py sha 025d0518d1 size 7110 · D.jsonl 286→287 · ledger_D case 283→284

## 工具
read_files / list_allowed_files / search_codebase / skills(ask-eda)。纯日志+cds.lib 解析，无 EDA 工具依赖，L2（真实工具沙盒可跑 python）。
