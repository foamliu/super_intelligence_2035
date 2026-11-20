# 深读笔记 — 1793932002608_suauw (jiangbaol @ hfeg0pkn002, 113 msgs, spice_sim)

## trace_source
- session: `1793932002608_suauw.messages.json`
- user: jiangbaol, host: hfeg0pkn002 (10.129.2.11)
- mtime: 2026-11-06 (NEW — 写入于 11-05 19:28 重扫快照之后，本轮 11-06 定向重扫发现)
- 体积: 273KB / 113 msgs / agent=lead
- 发现路径: 本轮经 .75 run_commands 对 fresh summary.tsv 的 42 个 host 定向重扫（threshold=2026-11-05 19:28:00）→ 111 NEW sessions → 按 spice 候选用户（jiangbaol）筛出

## 用户意图轮（A-档候选，逐字原文）

### U#11（★ 选定 A-档任务说明 — 纯需求轮，未给根因/未给修复）
> `/proj/dscqa/V0_LP6/workdir/jiangbaol/simulation/004_slicer/Slicer_testbench/strongarm/004_onlySlicer_delay_dejoa_test_cm.sp`
> 该.sp已添加了共模电流与共模电压，在此基础上添加差模电流及差模电压

- 上下文: U#0 是一个 context-summary（含 DSML tool_calls 交接，非自然需求轮，不用）；A#2-A#10 assistant 已为另一个 deck（decqa_doubletail）加了 CM/DM 测量并交付；U#11 是用户针对 **strongarm** testbench 的 `_test_cm.sp`（已有共模）提出 **加差模** 的新需求。
- ✅ 符合 A-档选轮规则: 用户表达目标（加差模 I/V），未指出根因、未给修复方案。

### U#33（次候选 — 加参数化输出电容）
> 帮我在这个.sp中比较器out_stg1两端添加电容，value设置为参数，在.paramter中定义该值，生成的结果以新.sp形式呈现

### U#57（次候选 — delvto 阈值调整，但 session 在 ask_question 后结束=incomplete）
> 将block：DqIb_strongarm_pmos中M17,MP0，MN23，MN5阈值电压降低0.1mV，其他晶体管阈值电压不变，给出实现方法，并验证

## assistant 工具链（对应 U#11 的合成路径）
1. A#12 `read_files` 读 `_test_cm.sp`（strongarm，已有共模 I/V 测量）
2. A#14-A#18 `editor` 写 `add_dm.sh`（bash 脚本: 拷贝源 .sp → 在 `out_cm_avg` measure 后插入 5 条差模 probe+measure）
3. A#18 `run_approved_command` (shell-runner) 执行 `add_dm.sh` → 生成 `004_onlySlicer_delay_dejoa_test_cmdm.sp`（288→302 行，+14 行）
4. A#20-A#28 `read_files` 验证生成文件
5. A#22 修正: 原 CM 文件用 `.d` 语法，用户之前纠正过应使用 `.mp1`(PMOS)/`.mn1`(NMOS) → 重生成用正确语法
6. A#30 交付总结；U#31 用户回「compact」(=接受/确认) → 进入下一需求 U#33

## 金标准（用户实际接受的产物 — A#28/A#30）
- 文件: `004_onlySlicer_delay_dejoa_test_cmdm.sp`（由 `_test_cm.sp` 288 行 → 302 行生成）
- 位置: `/rundata/dscqa/V0_LP6/simdir/finesim/workdir/jiangbaol/simulation/004_slicer/Slicer_testbench/strongarm/`
- 新增 5 条差模 probe+measure（位于 `.meas tran out_cm_avg` 之后、原 `Cur_slicer_avg` 之前）:

| 测量名 | 表达式 |
|:-------|:-------|
| `inp_cur_dm`  | `i(xmmp16.mp1) − i(xmmn2.mn1)` |
| `pmos_cur_dm` | `i(xmmp0.mp1) ...` |
| (其余 3 条 DM 电压/电流，.mp1/.mn1 语法) | |

- 关键语法约束: 用 `.mp1`/`.mn1`（PMOS/NMOS 内部子电路实例），非 `.d`
- 源 .sp 引用真实 PDK: `/proj/shdc/models/G4B/model_local/G4B_CIP_Model_L6_v0d5_t07/`、`/proj/dscqa/V0_LP6/...`（合成时需 stub 化或 fetch 真实 netlist）

## case 合成规划（DEBT:1 → 下一轮第一件事合成）
- case_id: `EDA-Eval-DesignFlow-SlicerDmMeasAdd-001`（spice_sim, A-档 trace-faithful, L2）
- 任务说明 = U#11 verbatim
- 交付: 通用 `add_dm_meas.py <src_cm.sp> <out_dir>` 读已有共模 .sp → 在 CM measure 段后插入 5 条差模 probe+measure（.mp1/.mn1 语法）→ 写新 _cmdm.sp → 打包 submit.zip
- A/B 切分: A=strongarm slicer testbench stub（含 CM measure）；hidden B=doubletail slicer stub（不同器件命名/拓扑，DM 表达式不同）
- L2: check.py 重写 .inc→stub 跑 hspice/finesim，断言 "job concluded" + DM measure 名齐全 + 表达式含 `.mp1`/`.mn1` + 跨输入 DM≠CM
- k≥8 断言: zip+py_compile / --help / DM measure 名 5 条齐全 / 语法 .mp1/.mn1 非 .d / 插入位置在 CM 后 / 新文件行数>源 / .meas tran 形式 / L2 hspice concluded / 跨输入 B≠A
- reference: `add_dm_meas_ref.py` + `check.py` + `negative/`(5 stub) + `negative_selftest.py`

## 备注
- session 后续 (U#33/U#57) 为同会话多需求，可另作 case 但本轮只取 U#11（最先且最干净）
- trace 真实产物在 .75 的 /rundata 与 /proj 路径下，合成时需 scp 源 .sp 或自建 stub
- 本轮因 11-05 19:2x 重扫令的定向重扫（42 host / 111 NEW）消耗预算，合成留 DEBT:1 下一轮
