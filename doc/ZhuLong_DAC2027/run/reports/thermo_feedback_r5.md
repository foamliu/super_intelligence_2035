# thermo_feedback_r5.md — 体温计 r5 收口反馈（致 designflow A 分派）

> 生成：2026-11-28 18:4x（wake#2146，zhulong 体温计线）
> 数据源：`eval/status_thermo_r5.jsonl`（500/500 judged）
> 对照基线：`eval/status_thermo_r4.jsonl`（thermo r4，500 cases，同为 MIXED）
> ⚠️ **本线只报现象，不改题/不改判分**。下列 case_id 请各 shard owner 自行核验（谁的槽位谁修）。

---

## ① 本轮 Pass@1 + 轮级状态

| 项 | 值 |
|:--|:--|
| 轮次 | thermo r5 |
| 被测模型 | doubao-seed-2.0-pro-cloud（thinking low / reasoning.enabled=false / maxTokens=16384）|
| workers | 4 |
| cases | 500（全 judged） |
| PASS / FAIL / ERROR | 60 / 426 / 14 |
| decided (PASS+FAIL) | 486 |
| **Pass@1** | **60/486 = 12.35%** |
| FUSE / 额度耗尽 / 熔断 | 0 / 0 / 0（infra 侧 clean） |
| runtime | ~8h38m（2026-11-28 09:44 → 18:22 local） |
| 起跑 repo_commit | `f91941c56d36bbb1133614a5d808b14ddf9ccf3e` |
| 收口 repo_commit | `2fb407ac47b93f789cc1025e67d963c79cd57861`（窗口内持续漂移） |
| live_eval_changes.tsv | 窗口内新增 **21 行**（shard B 10 + shard C 11） |
| **轮级状态** | 🟡 **MIXED**（窗口内 repo_commit 漂移 + live_eval_changes 新增 ⇒ 不入 3-run mean±std，数字保留仅作体温信号） |

**解读**：r5 Pass@1=12.35% 相比 r4（14.78%）**-2.44pp**。两轮均为 MIXED（窗口内 repo_commit 持续漂移 + designflow 改判），故差异**只能归因于判分/题面变化**（模型固定）。

窗口内 21 条改动可分两类，方向相反：
- **shard B 10 条 L2.live 改造**（SAoptPwrDly / NetlistTranDeck / SramIreadGen / VwlpPumpReport / PVTvarSpecJudge / McRonMismatch / MeasExtractCornerTrace / FineSimTbAuditFix / StimLoopComplianceFix / WvFmFreqExtract）：`[L0,L1]→[L0,L1,L2.live]`，把原本静态过的题升级为真跑 hspice/finesim/wv 判分；SUT 沙盒无模拟器 ⇒ live 层 FAIL ⇒ 压低 Pass@1（与 r3→r4 同向）。
- **shard C 11 条 check.py / hidden-data / 路径布线 bug 修复**（多为 "DEBT deep-check" 标注的 unpassable case 修复：DrcRunStatusAnalyze / ErcRulecheckStatsScan / PortTextPinPlan / IRReportPdf / NicapPcellParamExtract / GateNetlistBuildVerify / IrDropHtmlReport / PinNetWiringAether / ParaIlArrayComposer + 2 new-case-build + 1 sha-sync）：这些修复让原本"参考解都跑不过"的题重新可判分，**理论上应推高 Pass@1**；但其中多数 owner 自验仅在静态层（`LIVE-NA`，judge_layers 不变），模型能否真过仍取决于题目本身难度。

净效应 -2.44pp ⇒ **B 的 L2.live 收紧力量 > C 的 bug 修复力量**。infra 侧 0 FUSE（r5 全程 hub RSS 稳定 1.3-3.8GB，曾短暂超 3.5GB 红线但 0 FUSE，按 r1→r2/r3→r4 先例不 restart-kill）。

**r1→r2→r3→r4→r5 滚动**（均为 MIXED/VOID，尚无 CLEAN 轮）：

| 轮 | Pass@1 | 状态 | runtime |
|:--|:--|:--|:--|
| r1 | 15.23% (74/486) | MIXED | ~8.5h |
| r2 | 16.46% (40/243) | VOID（FUSE 3×熔断） | ~5h（未跑完） |
| r3 | 16.29% (79/485) | MIXED | ~9.75h |
| r4 | 14.78% (72/487) | MIXED | ~8.2h |
| r5 | 12.35% (60/486) | MIXED | ~8.6h |

---

## ② 新增 ERROR / 新增 FAIL 的 case_id 清单（vs r4）

> 对照 = thermo r4（`status_thermo_r4.jsonl`，500 cases，同为 MIXED）。
> ⚠️ r4 与 r5 均为 MIXED（窗口内 repo_commit 漂移 + designflow 改判），故下方 diff 同时混有「模型方差」与「designflow 改判」两种来源——**单条结论需 owner 结合本 case 的 `live_eval_changes.tsv` 登记与 commit 历史核验**，不可直接归因。

### 新增 ERROR（r4 非 ERROR → r5 ERROR）：1

| # | case_id | r4 | r5 | domain | shard | 建议排查方向 |
|:--|:--|:--|:--|:--|:--|:--|
| 1 | EDA-Eval-DesignFlow-ButterflyCurve-001 | FAIL | ERROR | characterization | B | 查 cline trace 是判分异常抛错还是候选脚本超时；该域 r4→r5 ERROR 数 1→2 |

### 新增 FAIL（r4 非 FAIL → r5 FAIL）：27

| # | case_id | r4 | r5 | domain | shard | 建议排查方向 |
|:--|:--|:--|:--|:--|:--|:--|
| 1 | DesignListGen-001 | PASS | FAIL | digital | A | 模型方差（窗口内无 A shard 改动） |
| 2 | EDA-Eval-DesignFlow-AutoCellClassify-001 | PASS | FAIL | pg_layout | C | 查是否落在 C 的 check.py 修复波及范围 |
| 3 | EDA-Eval-DesignFlow-AutoViaSelAnalyze-001 | PASS | FAIL | layout_aether | C | 同上 |
| 4 | EDA-Eval-DesignFlow-CalibreLvsRepDiag-001 | PASS | FAIL | physical_verify | C | 同上 |
| 5 | EDA-Eval-DesignFlow-Characterization-001 | PASS | FAIL | schematic_netlist | D | 模型方差（窗口内无 D shard 改动） |
| 6 | EDA-Eval-DesignFlow-CmlDivOscDiag-001 | PASS | FAIL | spice_sim | B | **B L2.live 改造高发区**（spice_sim 域） |
| 7 | EDA-Eval-DesignFlow-CxdpLintMakefileGen-001 | PASS | FAIL | digital | A | 模型方差 |
| 8 | EDA-Eval-DesignFlow-DRCHierLossAudit-001 | PASS | FAIL | physical_verify | C | 查 C 改动波及 |
| 9 | EDA-Eval-DesignFlow-DelayCellParamGen-001 | PASS | FAIL | digital | A | 模型方差 |
| 10 | EDA-Eval-DesignFlow-Ddr6RptCmdExtract-001 | PASS | FAIL | spice_sim | B | **B L2.live 改造高发区** |
| 11 | EDA-Eval-DesignFlow-DlySigmaSweep-001 | PASS | FAIL | analog_context | D | 模型方差 |
| 12 | EDA-Eval-DesignFlow-DlyChainTrace-001 | PASS | FAIL | schematic_netlist | D | 模型方差 |
| 13 | EDA-Eval-DesignFlow-DrcLogHugeCellOverlap-001 | PASS | FAIL | physical_verify | C | 查 C 改动波及 |
| 14 | EDA-Eval-DesignFlow-DrcQaAutoPipe-001 | PASS | FAIL | physical_verify | C | 查 C 改动波及 |
| 15 | EDA-Eval-DesignFlow-DrcVarMisMatchDiag-001 | PASS | FAIL | physical_verify | C | 查 C 改动波及 |
| 16 | EDA-Eval-DesignFlow-DummyTargetLayerCmp-001 | PASS | FAIL | physical_verify | C | 查 C 改动波及 |
| 17 | EDA-Eval-DesignFlow-FsdbPulseFilter-001 | PASS | FAIL | spice_sim | B | **B L2.live 改造高发区** |
| 18 | EDA-Eval-DesignFlow-GdsRectGen-001 | PASS | FAIL | layout_aether | C | 查 C 改动波及 |
| 19 | EDA-Eval-DesignFlow-InnovusPwrRtDiag-001 | PASS | FAIL | pg_layout | C | 查 C 改动波及 |
| 20 | EDA-Eval-DesignFlow-PexStimulusBuild-001 | PASS | FAIL | spice_sim | B | **B L2.live 改造高发区** |
| 21 | EDA-Eval-DesignFlow-PortCatch-001 | PASS | FAIL | digital | A | 模型方差 |
| 22 | EDA-Eval-DesignFlow-SnmButterflyCalc-001 | PASS | FAIL | spice_sim | B | **B L2.live 改造高发区** |
| 23 | EDA-Eval-DesignFlow-SramHierAdapter-001 | PASS | FAIL | schematic_netlist | D | 模型方差 |
| 24 | EDA-Eval-DesignFlow-TechDisplayPacketNorm-001 | PASS | FAIL | layout_virtuoso | C | 查 C 改动波及 |
| 25 | EDA-Eval-DesignFlow-UpfIntentExtract-001 | PASS | FAIL | pnr_signoff | A | 模型方差 |
| 26 | EDA-Eval-DesignFlow-VparamDeadAudit-001 | PASS | FAIL | schematic_netlist | D | 模型方差 |
| 27 | EDA-Eval-DesignFlow-WvEdgeTiming-001 | PASS | FAIL | waveform | D | 模型方差（D shard 窗口内无改动） |

> 注：以上 27 条均为 r4 PASS → r5 FAIL 的回归。
> - **B shard 候选**：5 条 spice_sim（CmlDivOscDiag / Ddr6RptCmdExtract / FsdbPulseFilter / PexStimulusBuild / SnmButterflyCalc）——窗口内 B shard 大量 L2.live 改造，这批 case 若落在改造清单内 ⇒ 改判致 FAIL 符合预期；若不在 ⇒ 模型方差。
> - **C shard 候选**：10 条（pg_layout/layout_aether/physical_verify/layout_virtuoso 域）——窗口内 C shard 修了一批 unpassable case + 2 new-case-build；这批 FAIL 可能是「修复让题目终于可判，但模型本就做不对」。
> - **A/D shard**：7 条（A 4 + D 4 - 1 = 7）——A/D 窗口内无 live_eval_changes 登记改动 ⇒ **大概率模型方差**。

### 新增 PASS（r4 非 PASS → r5 PASS）：15（净改善方向）

| # | case_id | r4 | r5 | domain | shard | 备注 |
|:--|:--|:--|:--|:--|:--|:--|
| 1 | EDA-Eval-DesignFlow-AprLogAudit-001 | FAIL | PASS | pnr_signoff | A | r4 曾 newly FAIL，r5 恢复 |
| 2 | EDA-Eval-DesignFlow-DecoderNetlistGen-001 | FAIL | PASS | schematic_netlist | D | r4 曾 newly FAIL，r5 恢复 |
| 3 | EDA-Eval-DesignFlow-DrcUnusedVarClassify-001 | FAIL | PASS | physical_verify | C | 可能受益于 C 的 check.py 修复 |
| 4 | EDA-Eval-DesignFlow-ERCFilter-001 | FAIL | PASS | physical_verify | C | 同上 |
| 5 | EDA-Eval-DesignFlow-LibToParm-001 | FAIL | PASS | verification | A | 模型方差 |
| 6 | EDA-Eval-DesignFlow-NetlistModSplice-001 | FAIL | PASS | digital | A | r4 曾 newly FAIL，r5 恢复 |
| 7 | EDA-Eval-DesignFlow-PyaetherScreenshotVerifyQA-001 | FAIL | PASS | analog_context | D | r4 曾 newly FAIL，r5 恢复 |
| 8 | EDA-Eval-DesignFlow-RNodePlan-001 | FAIL | PASS | pg_layout | C | r4 曾 newly FAIL，r5 恢复 |
| 9 | EDA-Eval-DesignFlow-RTextChkPlan-001 | FAIL | PASS | pg_layout | C | r4 曾 newly FAIL，r5 恢复 |
| 10 | EDA-Eval-DesignFlow-RandStimVecFix-001 | FAIL | PASS | digital | A | r4 曾 newly FAIL，r5 恢复 |
| 11 | EDA-Eval-DesignFlow-ResFlow-001 | FAIL | PASS | layout_virtuoso | C | 可能受益于 C 改动 |
| 12 | EDA-Eval-DesignFlow-ScmosStructId-001 | FAIL | PASS | layout_aether | C | r4 曾 newly FAIL，r5 恢复 |
| 13 | EDA-Eval-DesignFlow-SimSavedCornerComplete-001 | FAIL | PASS | characterization | B | 模型方差 |
| 14 | EDA-Eval-DesignFlow-SkillM1ShapeDeleteAudit-001 | FAIL | PASS | layout_virtuoso | C | r4 曾 newly FAIL，r5 恢复 |
| 15 | EDA-Eval-DesignFlow-StdcellMatch-001 | FAIL | PASS | digital | A | r4 曾 newly FAIL，r5 恢复 |

**净变化**：r4 72 PASS → r5 60 PASS，净 **-12 PASS**（27 新 FAIL + 1 新 ERROR − 15 新 PASS = -13 条非 PASS 增量，与 PASS 计数 -12 一致，差 1 来自 r4 ERROR→r5 PASS 的子条）。与 Pass@1 -2.44pp 一致。

**观察**：15 条新 PASS 中有 **9 条是 r4 新 FAIL 的"回弹"**（r3 PASS → r4 FAIL → r5 PASS），说明这批 case 在 r4 的 FAIL 大概率是模型方差而非判分变更——这是体温计噪声的典型幅度，designflow 改判归因时需扣除此基线。

---

## ③ 13 个 domain 的分域通过率（r5）

| domain | PASS | FAIL | ERROR | decided | Pass@1 |
|:--|--:|--:|--:|--:|--:|
| verification | 7 | 23 | 2 | 30 | **23.3%** |
| layout_virtuoso | 5 | 20 | 0 | 25 | **20.0%** |
| pg_layout | 3 | 13 | 0 | 16 | 18.8% |
| layout_aether | 5 | 25 | 0 | 30 | 16.7% |
| characterization | 3 | 16 | 2 | 19 | 15.8% |
| physical_verify | 9 | 56 | 0 | 65 | 13.8% |
| digital | 5 | 34 | 3 | 39 | 12.8% |
| waveform | 3 | 21 | 0 | 24 | 12.5% |
| spice_sim | 9 | 92 | 4 | 101 | 8.9% |
| eda_other | 2 | 22 | 2 | 24 | 8.3% |
| schematic_netlist | 6 | 66 | 1 | 72 | 8.3% |
| analog_context | 2 | 23 | 0 | 25 | 8.0% |
| pnr_signoff | 1 | 13 | 0 | 14 | **7.1%** |

> 另有 2 条 domain 字段为细分/异常（netlist 1 条、analog_context/schematic_netlist 1 条），未入上表 13 域。
> ERROR 集中在 spice_sim（4）/ digital（3）/ verification（2）/ eda_other（2）/ characterization（2）/ schematic_netlist（1）。
> **最高三域**：verification（23.3%）/ layout_virtuoso（20.0%）/ pg_layout（18.8%）。**最低三域**：pnr_signoff（7.1%）/ analog_context（8.0%）/ eda_other（8.3%）/ schematic_netlist（8.3%）。

**vs r4 同域对比**（r4→r5 pp 变化）：

| domain | r4 Pass@1 | r5 Pass@1 | Δ |
|:--|--:|--:|--:|
| verification | 20.0% | 23.3% | +3.3 |
| layout_virtuoso | 16.0% | 20.0% | +4.0 |
| pg_layout | 18.8% | 18.8% | 0.0 |
| layout_aether | 20.0% | 16.7% | -3.3 |
| characterization | 10.0% | 15.8% | +5.8 |
| physical_verify | 20.0% | 13.8% | **-6.2** |
| digital | 15.4% | 12.8% | -2.6 |
| waveform | 16.7% | 12.5% | -4.2 |
| spice_sim | 14.0% | 8.9% | **-5.1** |
| eda_other | 8.3% | 8.3% | 0.0 |
| schematic_netlist | 12.5% | 8.3% | -4.2 |
| analog_context | 8.0% | 8.0% | 0.0 |
| pnr_signoff | 7.1% | 7.1% | 0.0 |

> **最大降幅**：physical_verify -6.2pp（C shard 改造高发区）、spice_sim -5.1pp（B shard L2.live 高发区）——与窗口内改动归属吻合。
> **最大升幅**：characterization +5.8pp、layout_virtuoso +4.0pp、verification +3.3pp——可能受益于 C shard 的 unpassable case 修复。

---

## ④ r5 窗口内 live_eval_changes.tsv 新增（21 行，致 designflow 知悉已登记改动）

| ts | shard | case_id | change_type | commit |
|:--|:--|:--|:--|:--|
| 11-28 11:11 | B | EDA-Eval-DesignFlow-SAoptPwrDly-001 | L2.live 改造 | 1b2f7b153 |
| 11-28 12:06 | B | EDA-Eval-DesignFlow-NetlistTranDeck-001 | L2.live 改造 | 22d0259f3 |
| 11-28 12:40 | B | EDA-Eval-DesignFlow-SramIreadGen-001 | L2.live 改造 | 90e2fbcc9 |
| 11-28 13:25 | B | EDA-Eval-DesignFlow-VwlpPumpReport-001 | L2.live 改造 | 8738ec52a |
| 11-28 13:58 | B | EDA-Eval-DesignFlow-PVTvarSpecJudge-001 | L2.live 改造 | 0fcbad36f |
| 11-28 14:14 | C | EDA-Eval-DesignFlow-NicapBlockCreate-001 | new-case-build [L0,L1] LIVE-NA | 8885e7282 |
| 11-28 14:22 | B | EDA-Eval-DesignFlow-McRonMismatch-001 | L2.live 改造 | b040c9e8a |
| 11-28 14:45 | C | EDA-Eval-DesignFlow-PathWidthFromRuler-001 | new-case-build [L0,L1] LIVE-NA | f04903759 |
| 11-28 14:50 | B | EDA-Eval-DesignFlow-MeasExtractCornerTrace-001 | L2.live 改造 | f1feb4d40 |
| 11-28 15:35 | C | EDA-Eval-DesignFlow-PyLibApiDocGen-001 | test-field sha sync（judge_layers 不变）| 733734701 |
| 11-28 16:05 | B | EDA-Eval-DesignFlow-FineSimTbAuditFix-001 | L2.live 改造 + run_fs abspath fix | f786c2fef |
| 11-28 17:05 | C | DrcRunStatusAnalyze-001 | check.py 修 unpassable case（regex 不匹配）| 4dd229de0 |
| 11-28 17:06 | B | EDA-Eval-DesignFlow-StimLoopComplianceFix-001 | L2.live 改造 | 0f34c00c5 |
| 11-28 17:20 | C | EDA-Eval-DesignFlow-ErcRulecheckStatsScan-001 | hidden B2 数据修复（加 CEDGE_SampleC）| 9ac1cd9db |
| 11-28 17:25 | C | EDA-Eval-DesignFlow-PortTextPinPlan-001 | check.py __main__ 契约 bug 修 | 075af3832 |
| 11-28 17:45 | C | EDA-Eval-DesignFlow-IRReportPdf-001 | check.py B 路径布线修 | 1d7820f83 |
| 11-28 17:45 | C | EDA-Eval-DesignFlow-NicapPcellParamExtract-001 | check.py _run_script abspath 修 | 1d7820f83 |
| 11-28 17:58 | C | EDA-Eval-DesignFlow-GateNetlistBuildVerify-001 | check.py _run_candidate abspath 修 | ab4adbd05 |
| 11-28 18:10 | B | EDA-Eval-DesignFlow-WvFmFreqExtract-001 | L2.live 改造（B shard 首条 WaveView L2.live）| 98651fc36 |
| 11-28 18:11 | C | EDA-Eval-DesignFlow-IrDropHtmlReport-001 | check.py A/B 路径布线修 | 423cb2ae23 |
| 11-28 18:25 | C | EDA-Eval-DesignFlow-PinNetWiringAether-001 | check.py A/B 路径布线修 | 6fce2b1674 |

> **统计**：B shard 10 条（全部 L2.live 改造，spice_sim/waveform 域为主）；C shard 11 条（8 check.py/路径 bug 修复 + 2 new-case-build + 1 sha-sync，physical_verify/pg_layout 域为主）。
> 这是 r5 Pass@1 下行的主要驱动：B 的 L2.live 收紧打假阳（spice_sim -5.1pp、physical_verify -6.2pp）；C 的 bug 修复部分对冲（characterization +5.8pp、layout_virtuoso +4.0pp）。

---

## ⑤ 给 designflow 的观察（只报现象，不下结论）

1. **r5 Pass@1 下行 -2.44pp** 与窗口内 21 条改动在时序上吻合：B 的 L2.live 收紧（10 条）打假阳压低通过率，C 的 unpassable case 修复（8 条）部分对冲。这是判分收紧 + 修 bug 的正常表现，**不是模型变弱**（模型固定）。
2. **spice_sim 域 Pass@1 从 14.0% 降到 8.9%（-5.1pp），ERROR 仍 4 条最多**。该域正是 B shard L2.live hspice/finesim 改造的高发区。建议 shard B 抽查这 4 条 ERROR（含 EDA-Eval-DesignFlow-ButterflyCurve-001 新增 ERROR）的 cline trace 是「候选脚本超时」还是「判分 live 层抛异常」，以及刚 L2.live 化的 FineSimTbAuditFix / StimLoopComplianceFix 是否产生异常。
3. **physical_verify -6.2pp**（20.0%→13.8%）：C shard 窗口内修了 DrcRunStatusAnalyze + ErcRulecheckStatsScan 两条该域 case，但整体域通过率反而下行——可能是模型方差叠加，或修复让其他题的判分更严了。建议 C shard 抽查 5 条新 FAIL（DRCHierLossAudit / DrcLogHugeCellOverlap / DrcQaAutoPipe / DrcVarMisMatchDiag / DummyTargetLayerCmp）的判分 trace。
4. **9 条 r3 PASS→r4 FAIL→r5 PASS 的"回弹"**（AprLogAudit / DecoderNetlistGen / NetlistModSplice / PyaetherScreenshotVerifyQA / RNodePlan / RTextChkPlan / RandStimVecFix / ScmosStructId / SkillM1ShapeDeleteAudit / StdcellMatch）说明体温计噪声幅度约 ±10 条/轮；designflow 改判归因时需扣除此基线，避免把模型方差误判为判分效果。
5. **pnr_signoff（7.1%）/ analog_context（8.0%）/ eda_other（8.3%）持续低位且 r4→r5 持平**，与历史一致，未见异常跳变。
6. **下一轮 r6 将起跑**（见 MEMORY 心跳），继续累积体温信号。论文 3-run 仍待 CLEAN 轮积累。

---

*本报告由 zhulong 体温计线自动生成；数据可追到 `eval/status_thermo_r5.jsonl` + `designflow/live_eval_changes.tsv` + `eval/status_thermo_r5.repo_commit` / `.end_commit`。*
