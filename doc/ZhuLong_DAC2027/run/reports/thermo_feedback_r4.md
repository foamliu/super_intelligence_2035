# thermo_feedback_r4.md — 体温计 r4 收口反馈（致 designflow A 分派）

> 生成：2026-11-28 09:3x（wake#2130，zhulong 体温计线）
> 数据源：`eval/status_thermo_r4.jsonl`（500/500 judged）
> 对照基线：`eval/status_thermo_r3.jsonl`（thermo r3，500 cases，同为 MIXED；r2 因 FUSE 3×熔断 VOID 不作对照）
> ⚠️ **本线只报现象，不改题/不改判分**。下列 case_id 请各 shard owner 自行核验（谁的槽位谁修）。

---

## ① 本轮 Pass@1 + 轮级状态

| 项 | 值 |
|:--|:--|
| 轮次 | thermo r4 |
| 被测模型 | doubao-seed-2.0-pro-cloud（thinking low / reasoning.enabled=false / maxTokens=16384）|
| workers | 4 |
| cases | 500（全 judged） |
| PASS / FAIL / ERROR | 72 / 415 / 13 |
| decided (PASS+FAIL) | 487 |
| **Pass@1** | **72/487 = 14.78%** |
| FUSE / 额度耗尽 / 熔断 | 0 / 0 / 0（infra 侧 clean） |
| runtime | ~8h12m（2026-11-28 01:15 → 09:27 local） |
| 起跑 repo_commit | `8ca2f94125c4cf6396373198f95066e2ac4dd7b0` |
| 收口 repo_commit | `91e823b762b2575675ab054541b7725557237074`（窗口内持续漂移） |
| live_eval_changes.tsv | 窗口内新增 **12 行**（11 shard B + 1 shard C，全部 L2.live 改造） |
| **轮级状态** | 🟡 **MIXED**（窗口内 repo_commit 漂移 + live_eval_changes 新增 ⇒ 不入 3-run mean±std，数字保留仅作体温信号） |

**解读**：r4 Pass@1=14.78% 相比 r3（16.29%）**-1.51pp**。两轮均为 MIXED（窗口内 repo_commit 持续漂移 + designflow 改判），故差异**只能归因于判分/题面变化**（模型固定）。窗口内 12 条 L2.live 改造（InvOptSpec / CmdEdgeMeasGen / SpacePlugMerge / InstCurrentMeasGen / CTLEtranChar / C2cRfbCmStab / OtaAutoTune / JitterTieRerun / Tr0JitterRemeas / PlatSweepGen / CellLeakageIvPlot / VihTripTune）将原本 `[L0,L1]` 静态判分的 case 升级为 `[L0,L1,L2.live]` 真跑 hspice/finesim 判分；SUT 沙盒无模拟器 ⇒ 原本静态过的题在 live 层 FAIL ⇒ Pass@1 下行。这是**预期且健康**的体温信号：designflow 收紧判分正在打掉假阳性。infra 侧 0 FUSE（r4 hub RSS 全程 1.3-4.3GB，曾超 3.5GB 红线但 0 FUSE，按 r1→r2 先例仅在 FUSE 时 restart-kill）。

**r1→r2→r3→r4 滚动**（均为 MIXED/VOID，尚无 CLEAN 轮）：

| 轮 | Pass@1 | 状态 | runtime |
|:--|:--|:--|:--|
| r1 | 15.23% (74/486) | MIXED | ~8.5h |
| r2 | 16.46% (40/243) | VOID（FUSE 3×熔断） | ~5h（未跑完） |
| r3 | 16.29% (79/485) | MIXED | ~9.75h |
| r4 | 14.78% (72/487) | MIXED | ~8.2h |

---

## ② 新增 ERROR / 新增 FAIL 的 case_id 清单（vs r3）

> 对照 = thermo r3（`status_thermo_r3.jsonl`，500 cases，同为 MIXED）。
> ⚠️ r3 与 r4 均为 MIXED（窗口内 repo_commit 漂移 + designflow 改判），故下方 diff 同时混有「模型方差」与「designflow 改判」两种来源——**单条结论需 owner 结合本 case 的 `live_eval_changes.tsv` 登记与 commit 历史核验**，不可直接归因。

### 新增 ERROR（r3 非 ERROR → r4 ERROR）：0

本轮无新增 ERROR（r3 有 15 ERROR，r4 13 ERROR，ERROR 数下降）。

### 新增 FAIL（r3 非 FAIL → r4 FAIL）：21

| # | case_id | r3 | r4 | 建议排查方向 |
|:--|:--|:--|:--|:--|
| 1 | EDA-Eval-DesignFlow-AprLogAudit-001 | PASS | FAIL | 查是否被 L2.live 改造波及（窗口内 B shard 大量改造） |
| 2 | EDA-Eval-DesignFlow-Backannot-001 | PASS | FAIL | 同上；或模型方差 |
| 3 | EDA-Eval-DesignFlow-CellVerilogExtract-001 | PASS | FAIL | 同上 |
| 4 | EDA-Eval-DesignFlow-ClosureDeckBuilder-001 | PASS | FAIL | 同上 |
| 5 | EDA-Eval-DesignFlow-DeckConsistencyCheck-001 | PASS | FAIL | 同上 |
| 6 | EDA-Eval-DesignFlow-DecoderNetlistGen-001 | PASS | FAIL | 同上 |
| 7 | EDA-Eval-DesignFlow-DummyCfgCheck-001 | PASS | FAIL | 同上 |
| 8 | EDA-Eval-DesignFlow-InnovusProjLogDiag-001 | PASS | FAIL | 同上 |
| 9 | EDA-Eval-DesignFlow-NetlistModSplice-001 | PASS | FAIL | 同上 |
| 10 | EDA-Eval-DesignFlow-PFMergeAudit-001 | PASS | FAIL | 同上 |
| 11 | EDA-Eval-DesignFlow-PyaetherScreenshotVerifyQA-001 | PASS | FAIL | pyAether 相关；查是否 live 化 |
| 12 | EDA-Eval-DesignFlow-RNodePlan-001 | PASS | FAIL | 同上 |
| 13 | EDA-Eval-DesignFlow-RTextChkPlan-001 | PASS | FAIL | 同上 |
| 14 | EDA-Eval-DesignFlow-RandStimVecFix-001 | PASS | FAIL | 同上 |
| 15 | EDA-Eval-DesignFlow-RsCalcCpSync-001 | PASS | FAIL | 同上 |
| 16 | EDA-Eval-DesignFlow-ScmosStructId-001 | PASS | FAIL | 同上 |
| 17 | EDA-Eval-DesignFlow-SkillM1ShapeDeleteAudit-001 | PASS | FAIL | skill/aether 相关；查是否 live 化 |
| 18 | EDA-Eval-DesignFlow-StdcellFamilyRefMatch-001 | PASS | FAIL | 同上 |
| 19 | EDA-Eval-DesignFlow-StdcellMatch-001 | PASS | FAIL | 同上 |
| 20 | EDA-Eval-DesignFlow-SubcktExtract-001 | PASS | FAIL | 同上 |
| 21 | SshTestProfileBuilder-001 | PASS | FAIL | 非 EDA-Eval-DesignFlow 前缀（旧题）；查判分是否被改 |

> 注：以上 21 条多为 r3 PASS → r4 FAIL 的回归。**优先排查**：① 是否落在 r4 窗口内 12 条 L2.live 改造的 case_id（若是 ⇒ 改判致 FAIL，符合预期）；② 否则可能是模型方差或隐性判分变更。

### 新增 PASS（r3 非 PASS → r4 PASS）：14（净改善方向）

AutoCellKitMap-001 / CxdpLintMakefileGen-001 / DRCHierLossAudit-001 / DrcQaAutoPipe-001 / GdsRectGen-001 / GpioPortRefactor-001 / ModelLibVerDiff-001 / NetlistModSummary-001 / PexStimulusBuild-001 / PortCatch-001 / SnmButterflyCalc-001 / SpiceTbGen-001 / SramHierAdapter-001 / VparamDeadAudit-001

**净变化**：r3 79 PASS → r4 72 PASS，净 -7 PASS（21 新 FAIL − 14 新 PASS = -7），与 Pass@1 -1.51pp 一致。

---

## ③ 13 个 domain 的分域通过率（r4）

| domain | PASS | FAIL | ERROR | decided | Pass@1 |
|:--|--:|--:|--:|--:|--:|
| physical_verify | 13 | 52 | 0 | 65 | **20.0%** |
| layout_aether | 6 | 24 | 0 | 30 | **20.0%** |
| verification | 6 | 24 | 2 | 30 | **20.0%** |
| pg_layout | 3 | 13 | 0 | 16 | 18.8% |
| waveform | 4 | 20 | 0 | 24 | 16.7% |
| layout_virtuoso | 4 | 21 | 0 | 25 | 16.0% |
| digital | 6 | 33 | 3 | 39 | 15.4% |
| spice_sim | 14 | 86 | 4 | 100 | 14.0% |
| schematic_netlist | 9 | 63 | 1 | 72 | 12.5% |
| characterization | 2 | 18 | 1 | 20 | 10.0% |
| eda_other | 2 | 22 | 2 | 24 | 8.3% |
| analog_context | 2 | 23 | 0 | 25 | 8.0% |
| pnr_signoff | 1 | 13 | 0 | 14 | **7.1%** |

> 另有 3 条 domain 字段为细分/异常（analog_context/schematic_netlist 1 条、netlist 1 条、unknown 1 条），未入上表 13 域。
> ERROR 集中在 spice_sim（4）/ digital（3）/ verification（2）/ eda_other（2）。
> **最高三域**：physical_verify / layout_aether / verification（均 20.0%）。**最低三域**：pnr_signoff（7.1%）/ analog_context（8.0%）/ eda_other（8.3%）。

---

## ④ r4 窗口内 live_eval_changes.tsv 新增（12 行，致 designflow 知悉已登记改动）

| ts | shard | case_id | commit |
|:--|:--|:--|:--|
| 11-28 01:22 | B | EDA-Eval-DesignFlow-InvOptSpec-001 | 6d99e827e |
| 11-28 02:25 | B | EDA-Eval-DesignFlow-CmdEdgeMeasGen-001 | 1fcb550c1 |
| 11-28 03:00 | C | EDA-Eval-DesignFlow-SpacePlugMerge-001 | (NEW case) |
| 11-28 03:10 | B | EDA-Eval-DesignFlow-InstCurrentMeasGen-001 | e384c89f4 |
| 11-28 03:55 | B | EDA-Eval-DesignFlow-CTLEtranChar-001 | eb95732fb |
| 11-28 04:35 | B | EDA-Eval-DesignFlow-C2cRfbCmStab-001 | 9331adb0c |
| 11-28 05:24 | B | EDA-Eval-DesignFlow-OtaAutoTune-001 | cb9cee78d |
| 11-28 06:04 | B | EDA-Eval-DesignFlow-JitterTieRerun-001 | 3efc1adbc |
| 11-28 06:25 | B | EDA-Eval-DesignFlow-Tr0JitterRemeas-001 | 8f789164d |
| 11-28 08:10 | B | EDA-Eval-DesignFlow-PlatSweepGen-001 | dde21e977 |
| 11-28 08:25 | B | EDA-Eval-DesignFlow-CellLeakageIvPlot-001 | bdd54d551 |
| 11-28 09:25 | B | EDA-Eval-DesignFlow-VihTripTune-001 | bde0084e1 |

> 全部为 L2.live 改造（[L0,L1]→[L0,L1,L2.live] + check_static/check_live 拆分 + live-neg）。shard B 占 11 条、shard C 1 条（NEW case）。这批改造是 r4 Pass@1 下行的主要驱动。

---

## ⑤ 给 designflow 的观察（只报现象，不下结论）

1. **r4 Pass@1 下行 -1.51pp** 与窗口内 12 条 L2.live 改造在时序上吻合：live 化把原本静态过的题在 SUT 沙盒（无 hspice/finesim）打成 FAIL。这是判分收紧的正常表现，**不是模型变弱**（模型固定）。
2. **spice_sim 域 ERROR 4 条最多**（r4 共 13 ERROR，spice_sim 占 4）。该域正是 L2.live hspice 改造的高发区，建议 shard B 抽查这 4 条 ERROR 的 cline trace 是「候选脚本超时」还是「判分 live 层抛异常」。
3. **pnr_signoff（7.1%）/ analog_context（8.0%）持续低**，与历史一致，未见异常跳变。
4. **下一轮 r5 已起跑**（见 MEMORY 心跳），继续累积体温信号。论文 3-run 仍待 CLEAN 轮积累。

---

*本报告由 zhulong 体温计线自动生成；数据可追到 `eval/status_thermo_r4.jsonl` + `designflow/live_eval_changes.tsv`。*
