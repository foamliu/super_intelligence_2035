# Deepread: nmz6w — hairuizh platform inverter mt0 reorganization

**session**: `1793953494729_nmz6w` · **user**: hairuizh · **host**: hfeg0plg52 · **mc**: 1129 · **domain**: characterization
**files**: `.messages.json` (898KB, 212 msgs, 5360 lines, dated 11-10 09:24) + `.messages.archive.json` (2MB, 11-06 16:24)

## 用户意图（逐字）

- **U#1 (idx 0)** — Context summary（续接 session，非自然用户轮）：
  「Build and run platform device-characterization SPICE testbenches (thick & thin inverters, MOS Vtlin) for 5 platforms (G4B_DEJOA, G5_DRCOA, V1_DRGQA, V2B_DRVQA, GL22) and produce reorganized data tables with labeled columns.」+ State 段说明 thick 已完成。

- **U#2 (idx 1)** — **CLEAN produce-task**（本 case 的任务说明来源）：
  「在该文件夹内添加 DRVQA_invs.sp，包含 ptn/ntn，ptn_lv/ntn_lv 两对 inv，并对应的修改 DEJOA_invs.sp, DRCOA_invs.sp, DRGQA_invs.sp，使它们都包含 ptn/ntn，ptn_lv/ntn_lv 两对 inv; GL22_invs.sp 仍然保持原有的五对管子组成的 inv;规则如下 1.可以适当重构该文件夹下所有的文件,使其与之前你生成的 plat_invs_thick/ 具有相同格式」

- **U#3 (idx 123)** — 纠正/修复方向（→ §A-② 排除 A 档，走 B-synthesized）：
  「为什么，GL22 的数据在 0.15u 以上是空的，这点不需要和 thick 保持相同！需要统计所有 length 的数据！另外，每个平台的 Lmin 不相同，要求从各个平台的 Lmin to 200n step5n；各平台的 thin 的 Lmin 如下（real L）：G4B 42n; G5 42n; V1 36n; V2B 36n; GL22 26n」

- **U#4 (idx 193)** — 文件整理（非 produce）：
  「是否查看到 @/home/hairuizhu/Agent.md，现在把你产生的中间文件移动到对应的文件夹中」

## assistant 工具链（关键节点）

| idx | tool | 产物/作用 |
|---|---|---|
| 5 | list_allowed_files | 列 plat_invs_thin/ + plat_invs_thick/ 目录 |
| 9 | read_files | 读 thin/base.sp + thick/base.sp（HSPICE options: .option accurate runlvl=6, MEASFORM=3 MEASFILE=1, .param tperiod=4n）|
| 12-15 | read_files | 读 plat_mos_thin/DEJOA_mos.sp + thick.mt0_reorg.csv（参考格式）|
| 18 | read_files | 读 plat_condtions/G4B_DEJOA_conditions.sp（平台 PVT 条件）|
| 21 | editor | 编辑 plat_invs_thin/DEJOA_invs.sp（改 .param Cthin/Cgatein）|
| 29-43 | editor | 建 dep_base.py/dep_dejoa.py/dep_drcoa.py/dep_drgqa.py/dep_drvqa.py/dep_gl22a.py/dep_gl22b.py — 各平台 inverter .sp 文件的生成脚本 |
| 55-93 | editor + run_approved_command | 建 thin_test_one.sp/run_thin_test.py/run_thin_full.py/launch_thin_bg.py/poll_thin_bg.py — 跑 HSPICE 仿真（/apps/synopsys/SRB/hspice_V-2023.12-SP1-1/hspice/bin/hspice）|
| 103 | editor | struct_thick.py — 分析 thick.mt0_reorg.csv 结构 |
| 107 | editor | **reorg_thin_inv.py**（v1，4632B）— 把 raw thin.mt0.csv 重组织成标注表 |
| 113 | struct_thin.py | 验证输出结构（sections/cond blocks）|
| 124 | editor | patch_thin_lmin.py — 按 U#3 把各平台 Lmin 改成 42/42/36/36/26n |
| 132 | editor | **reorg_thin_inv2.py**（v2 final，4272B）— 重组织脚本终版 |

## reorg_thin_inv2.py 核心逻辑（本 case 金标准）

1. **alter→(plat,pair,cond) 映射**：`cfgs` 列表按 base.sp 的 .alter 顺序重建（DEJOA 交错 / DRCOA·DRGQA·DRVQA 嵌套 / GL22 5 pair × 3 cond）。`cfg2alter` 反查。
2. **解析 mt0.csv**：跳 `lreal,` header 行；`parts[0]=lreal(m)`, `parts[10]=alter`；`tpd=(tpr+tpf)/2`，`iddq/idda=abs(...)`；按 `cfg` 归类到 `rows[cfg][lreal_um]`。
3. **输出分块**：per metric → per condition → per platform；每块表头 `lreal(um)  <pair1>  <pair2>...`；union lreal 升序；缺失留空（lv pair < 150n 空，GL22 各 pair 从 26n 起）。
4. **平台定义**：G4B_DEJOA 42n(ptn/ntn,ptn_lv/ntn_lv) / G5_DRCOA 42n / V1_DRGQA 36n / V2B_DRVQA 36n / GL22 26n(puhvt/nuhvt,phvt/nhvt,prvt/nrvt,plvt/nlvt,pulvt/nulvt)。

## case 设计（EDA-Eval-DesignFlow-Mt0Reorg-001）

- **track**: faithful（U#2 是提出需求的自然用户轮；U#3 给修复方向 → §A-② 排除 A 档 → B-synthesized with trace-faithful prompt）
- **domain**: characterization
- **layer**: L1（纯 stdlib CSV 解析+重组，不调 EDA 工具；但封装真实 HSPICE .mt0 重组流）
- **deliverable**: `mt0_reorg.py` CLI `<mt0.csv> <config.json> <out.csv>`
- **资产 A**: config.json(3平台/2条件/14 alter_mapping) + thin.mt0.csv(384行合成) + example_output_A.csv + task_brief.md
- **隐藏 B1**: 3平台(G5_DRCOA Lmin48n/V2B_DRVQA Lmin40n/GL22 Lmin30n) × 2条件(tt25/ss-40)，GL22 3 pair（反硬编码）
- **隐藏 B2**: 2平台 × 3条件(tt25/ss-40/ff110)，G4B_DEJOA 仅 1 pair（结构差异反硬编码）
- **check.py**: 13 断言(a-m)：zip/compile/B1 exit0/表头/9 metric 段/6 (cond,plat) 块/tpd 对账/abs/idqq 升序/lv 空白/GL22 不截断/B2 exit0+3条件/B1≠B2
- **6 negatives**: naive_empty/hardcoded_a/only_print/empty_shell/ref_core_deleted/no_validate 全 FAIL
- **§4.9 三假**: empty_shell→FAIL / only_print→FAIL / ref_core_deleted→FAIL
- **断言门**: k_rationale=k_check=13 ≥ 8 ✓
- **test 字段**: sha256 eaf96148, 12920B, 与盘上 check.py 字节同步 ✓

## 自验

- ref PASS 13/13（B1 + B2 全通过）
- 6 negatives NEG_RC=0（全 FAIL）
- §4.9 三假全 FAIL
