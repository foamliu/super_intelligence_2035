# 深读笔记 — trace 1793701477122_z5wxj（alan3zh @ hfeg0pkn001, mc=297, pg_layout）

**会话**：`/home/alan3zh/.cline/data/sessions/1793701477122_z5wxj/`（1.75MB, 190 msgs, agent=lead）
**项目**：test_chip_v1 Innovus APR 全流程（顶层 `hl22_porting_test_chip_v1`，HL22，Innovus 23.35，`apr/` 下 `innovus_fp.tcl`/`innovus_pr.tcl`，`make run` 串 fp→route→check_route）

## 用户真实意图（A-档 seed 原话）
1. `<user_input mode="act">进入./apr/logs查看inv_fp.log，其中有告警：Begin power routing ... **WARN: (IMPSR-1253): Unable to find any standard cell pin connected to the VDD_PM net. 查询问题原因</user_input>`
2. `此次报错>>> innovus floorplan FAILED -- see .../inv_fp.log，而且无route的log`
3. `inv_route.log中有"INFO: INNOVUS PR DONE : hl22_porting_test_chip_v1"的输出，但cmd中还是提示">>> innovus route FAILED"`
4. `使用方案B修改脚本`（PM 域 row band 修复）

## assistant 诊断链（真实工具调用：read_files / editor / run_approved_command(python-runner) / search_codebase / list_allowed_files）
- **inv_fp.log 含 2 段追加 LSF 运行**：行 1~450 = 11/2 旧运行（IMPDB-1216 + assignIoPins 报错 → FP FAILED）；行 ~453+ = 11/3 14:04 新运行（Job 768479），后又被覆盖成单次 Job 816941（448 行）。
- **新 DC 网表 dc_2026-11-02-20.29.45** 已带完整电源意图：2007 实例每个 cell 显式 `.VDD()/.VSS()`；PM 行单元 `PMRowBLK_Blk40xx`(INVD8) 的 `.VDD` 接模块局部 `VDD_PM` 网，经层次端口链到顶层 `VDD_PM`；`PM_VDDI_Inst` 实例化端口名 `.VDD_PM(VDD_PM)`（不是 `.VDD`）。
- **IMPSR-1253 根因**：GNC(globalNetConnect) 找名为 `VDD` 的 pin → VDD_PM 上一个都没连上；VERIFY "1 instTerm(s), 0 leaf std-cell pin(s)"（网表自带层次端口 pin，非 leaf std-cell pin）→ fp 阶段无 leaf 标准单元 pin 直接挂 VDD_PM special net，**属预期**，非新错误。
- **PM 子树**：`PMArrayPart(TOPPMBLK_Blk4129) → PMVDDIMatrixPart(PM_VDDI_Inst) → 21×PMVDDIRowPart(PMColBLK_Blk40xx) → 21×INVD8(PMRowBLK_Blk40xx)`，共 **441** PM leaf，**仅**存在于 PM_VDDI_Inst 子树内（网表级隔离干净）；PM 阵列其余单元 `.VDD(VDD)`。
- **route 阶段（inv_route.log, Job 817683）**：`INNOVUS PR DONE`（行 2091），DEF/GDS/SDF/routed.v 全部导出（DEF 1.09MB 非空），布线 DRC 全 0，GR overflow 0.32%V。6 个 error：4× TCLCMD-917（`get_cells` 模式无匹配，回退 dbGet 成功施加 dont_touch 264+132+441 实例）+ 2× IMPCCOPT-2004（无时钟树，SDC 本无时钟，预期）。
- **真正硬伤（geom.rpt, 34KB）**：**204 个 geometry DRC marker**，其中 **201 个 SHORT**：`SHORT: Special Wire of Net VDD & Pin of Cell TOPPMBLK_Blk4129/PM_VDDI_Inst/.../PMRowBLK_Blk40xx (M1)` —— VDD 的 M1 followpin rail 与 PM 域单元的 VDD pin 直接短路，VDD_PM 隔离被物理破坏。
- **conn.rpt**：verifyConnectivity 唯一问题 = `Net VDD_PM: no routing`（VDD/VSS 全通）。
- **make check_route gate**：`grep -q "PR DONE" inv_route.log && [ $$(grep -c SHORT geom.rpt) -eq 0 ]` → SHORT≠0 故 `>>> innovus route FAILED -- see geom.rpt`（route 已 DONE 但 make 判 FAILED，矛盾）。
- **修复**：改 `innovus_fp.tcl` 为分代网表感知（新网表跳过会落空的 GNC、VERIFY 区分 leaf pin 与层次端口 pin、附 leaf 改接命令）；同步 README + 更新验证器 revision；`_apr_setup_validate.py` ALL CHECKS PASSED（含 441 保护实例计数独立佐证）。方案 B：PM 域行带内 M1 route（followpin 网格按行均匀画，非按 pin 位置，故行带内须 M1 route）。

## 用户接受结果
fp 阶段 `INNOVUS FP DONE` + 新版 VERIFY 输出（`1 instTerm(s), 0 leaf std-cell pin(s)` + IMPSR-1253 预期说明）+ 假 "OK" GNC VDD_PM 行消失；验证器 ALL CHECKS PASSED；诊断结论闭环（IMPSR-1253 预期 + 真硬伤 = VDD M1 followpin SHORT 破坏 VDD_PM 隔离）。

## 合成（B-档 synthesized, L1-boundary）
**case_id**：`EDA-Eval-DesignFlow-InnovusPwrRtDiag-001`（pg_layout）
**SUT 写** `pwr_rt_diag.py`（CLI `python3 pwr_rt_diag.py <manifest.json> <report.json>`，stdlib only），解析 manifest.bundle 内嵌的 inv_fp_log/inv_route_log/geom_rpt/conn_rpt/makefile/make_run_log，输出结构化诊断 JSON。
**A_run**=真实 trace grounded（test_chip_v1, 2 LSF 段, IMPSR-1253 VDD_PM, 3 DMMMC-271, 4 TCLCMD-917, 204 marker/201 SHORT VDD@M1, conn VDD_PM no routing, make FAILED, root=M1_FOLLOWPIN_SHORT_TO_PM_DOMAIN）。
**隐藏 B**=全重参数化（test_chip_v2, 3 LSF 段, VDD_MEAS, 2 IMPSR, 4 DMMMC, 5 TCLCMD, 180 marker/178 SHORT, make FAILED）击穿硬编码 A。
**B2 guard**=fp FAILED（最新段 FAILED, 无 route, 无 SHORT, root=FP_FAILED）杀 always-true fp_done / always-short。
**B3 guard**=route DONE + 0 SHORT + VDD_MEAS no routing + make PASS（root=PM_NET_NO_ROUTING_ONLY）杀 always-FAILED make / always-short。
**17 条断言 ①–⑰ a–p + a2**：(a)结构19键 (b)fp_done==B&==B2 (c)fp_run_count (d)route_done (e)make_verdict==B&B2&B3 (f)mismatch==B&B2&B3 (g)impsr1253_count (h)impsr1253_nets==B&A[反硬编码] (i)impsr1253_expected (j)dmmmc271_count (k)tclcmd917_count (l)drc_marker_count (m)short_net_counts==B&A[反硬编码] (n)short_layers (o)conn_no_routing==B&A[反硬编码] (p)root_cause==B&B2&B3 (a2)3-seed sha256 确定性。
**self-verify**：本机 Python 3 — golden submit.zip→disk check.py CHECK PASS 17/17；5 negative[empty_shell/print_expected/core_deleted/naive_hardcode_a/stub_no_empty]全 FAIL（negative_selftest ALL_NEG_FAIL=True）；3-seed determinism STABLE；E2E jsonl test check PASS。jsonl C 追加 1 行。ledger z5wxj 已 mark case+pg_layout。

## DISTINCT（与现有 shard C pg_layout case 不重叠）
InnovusDbAudit（db 审计）/ InnovusViaCutDiag（via cut 宽线打孔）/ PwrGlobalsGen（power.globals 配置生成）/ PwrFlowCfgGen / PwrFillAgentGen 等 —— 本案首次 ground on **Innovus APR 多日志交叉根因诊断**（IMPSR-1253 power routing warning + route DONE vs make FAILED 矛盾 + geom.rpt VDD M1 followpin SHORT 破坏 PM 域隔离），与 db 审计/via cut/配置生成互补不重叠。
