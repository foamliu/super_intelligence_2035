# thermo_feedback_r3.md — 体温计 r3 收口反馈（致 designflow A 分派）

> 生成：2026-11-28 01:1x（wake#2116，zhulong 体温计线）
> 数据源：`eval/status_thermo_r3.jsonl`（500/500 judged）
> 对照基线：`eval/status_thermo_r1.jsonl`（thermo r1，500 cases，同为 MIXED；r2 因 FUSE 3×熔断 VOID 不作对照）
> ⚠️ **本线只报现象，不改题/不改判分**。下列 case_id 请各 shard owner 自行核验（谁的槽位谁修）。

---

## ① 本轮 Pass@1 + 轮级状态

| 项 | 值 |
|:--|:--|
| 轮次 | thermo r3 |
| 被测模型 | doubao-seed-2.0-pro-cloud（thinking low / reasoning.enabled=false / maxTokens=16384）|
| workers | 4 |
| cases | 500（全 judged） |
| PASS / FAIL / ERROR | 79 / 406 / 15 |
| decided (PASS+FAIL) | 485 |
| **Pass@1** | **79/485 = 16.29%** |
| FUSE / 额度耗尽 / 熔断 | 0 / 0 / 0（infra 侧 clean） |
| runtime | ~9.75h（15:21 → 01:04 Nov 28） |
| 起跑 repo_commit | `924a14db401757032e5da2660ccc212f0559ec87` |
| 收口 repo_commit | `22341096e078d2b202f8171208c23af32bb3860f`（窗口内 30+ commit·漂移） |
| live_eval_changes.tsv | 窗口内持续新增（designflow L2.live 改造登记，末行 ts=2026-11-27T20:35 落 r3 窗口内） |
| **轮级状态** | 🟡 **MIXED**（窗口内 repo_commit 漂移 + live_eval_changes 新增 ⇒ 不入 3-run mean±std，数字保留仅作体温信号） |

**解读**：r3 Pass@1=16.29% 相比 r1（15.23%）+1.06pp，相比 rerun#2 三轮（13.81%/14.40%/16.26%）落在同一区间，**无异常跳变**。infra 侧 0 FUSE 健康（r2 曾 FUSE 3×熔断 VOID，r3 hub RSS 全程 <2.5GB 稳定）。r3 窗口内 designflow 持续提交 L2.live 改造（repo_commit 漂移 30+ 次），MIXED 是预期状态。体温计已起 r4（repo_commit=`8ca2f9412`…）。

---

## ② 新增 ERROR / 新增 FAIL 的 case_id 清单（vs r1）

> 对照 = thermo r1（`status_thermo_r1.jsonl`，500 cases，同为 MIXED）。
> ⚠️ r1 与 r3 均为 MIXED（窗口内 repo_commit 漂移 + designflow 改判），故下方 diff 同时混有「模型方差」与「designflow 改判」两种来源——**单条结论需 owner 结合本 case 的 `live_eval_changes.tsv` 登记与 commit 历史核验**，不可直接归因。

### 新增 ERROR（r1 非 ERROR → r3 ERROR）：2
| case_id | r1 | r3 | 建议排查方向 |
|:--|:--|:--|:--|
| EDA-Eval-DesignFlow-LisMeasExtract-001 | FAIL | ERROR | early exit；查 cline 是否中途 abort / harness 是否抛异常 / L2.live 实跑是否超时 |
| EDA-Eval-DesignFlow-StrongarmFomSweep-001 | FAIL | ERROR | early exit；查 spice 实跑是否超时 / check_live 异常退出路径 |

### 新增 FAIL（r1 非 FAIL → r3 FAIL）：13（回归）
| case_id | r1 | r3 | 建议排查方向 |
|:--|:--|:--|:--|
| EDA-Eval-DesignFlow-ERCFilter-001 | PASS | FAIL | 查是否 L2.live 加严后静态 PASS 转 live FAIL（可能为正常加严，非回归） |
| EDA-Eval-DesignFlow-GpioPortRefactor-001 | PASS | FAIL | 同上，结合 live_eval_changes.tsv 核验 |
| EDA-Eval-DesignFlow-LibToParm-001 | PASS | FAIL | 同上 |
| EDA-Eval-DesignFlow-ModelLibVerDiff-001 | PASS | FAIL | 同上 |
| EDA-Eval-DesignFlow-NetlistModSummary-001 | PASS | FAIL | 同上 |
| EDA-Eval-DesignFlow-PortCatch-001 | PASS | FAIL | 同上 |
| EDA-Eval-DesignFlow-ScmosStructFind-001 | PASS | FAIL | 同上 |
| EDA-Eval-DesignFlow-SignalRunXref-001 | PASS | FAIL | 同上 |
| EDA-Eval-DesignFlow-SimSavedCornerComplete-001 | PASS | FAIL | 同上 |
| EDA-Eval-DesignFlow-SpiceClosureExtract-001 | PASS | FAIL | 同上 |
| EDA-Eval-DesignFlow-SramHierAdapter-001 | PASS | FAIL | 同上 |
| EDA-Eval-DesignFlow-TrimMarginSpec-001 | PASS | FAIL | 同上 |
| GdsLayerAreaMeasure-001 | PASS | FAIL | 同上 |

### 新增 PASS（r1 FAIL/ERROR → r3 PASS）：18（改善）
EDA-Eval-DesignFlow-Backannot-001 / ClosureDeckBuilder-001 / DecoderNetlistGen-001 / DrcLogHugeCellOverlap-001 / DummyTargetLayerCmp-001 / FsdbPulseFilter-001 / InnovusProjLogDiag-001 / InnovusPwrRtDiag-001 / MinpulseRewriteRun-001 / NetlistExtractSkill-001 / NetlistModSplice-001 / RTextChkPlan-001 / RandStimVecFix-001 / StdcellFamilyRefMatch-001 / SubcktExtract-001 / WaveSig-001 / WvEdgeTiming-001 / SshTestProfileBuilder-001

**净变化**：PASS 74→79（+5），其中新增 PASS 18、新增 FAIL 13、新增 ERROR 2、新增「ERROR→FAIL」等互转若干。整体 +1.06pp，符合 designflow 持续改造下的正常波动。

---

## ③ 13 个 domain 的分域通过率（r3）

> domain 取 `metadata.domain` 顶层（split on `/`），经 `cases/*/*.json` 映射。

| domain | PASS | FAIL | ERROR | decided | Pass@1% |
|:--|--:|--:|--:|--:|--:|
| analog_context | 4 | 22 | 0 | 26 | 15.4 |
| characterization | 2 | 18 | 2 | 20 | 10.0 |
| digital | 7 | 32 | 3 | 39 | 17.9 |
| eda_other | 2 | 22 | 2 | 24 | 8.3 |
| layout_aether | 5 | 25 | 0 | 30 | 16.7 |
| layout_virtuoso | 5 | 20 | 0 | 25 | 20.0 |
| pg_layout | 7 | 9 | 0 | 16 | 43.8 |
| physical_verify | 13 | 53 | 0 | 66 | 19.7 |
| pnr_signoff | 2 | 12 | 0 | 14 | 14.3 |
| schematic_netlist | 11 | 56 | 1 | 67 | 16.4 |
| spice_sim | 11 | 92 | 5 | 103 | 10.7 |
| verification | 6 | 24 | 2 | 30 | 20.0 |
| waveform | 4 | 20 | 0 | 24 | 16.7 |
| netlist | 0 | 1 | 0 | 1 | 0.0 |
| **TOTAL** | **79** | **406** | **15** | **485** | **16.29** |

**观察（r3 vs r1）**：
- 通过率最高：pg_layout 43.8%（r1 25.0%→r3 43.8%，+18.8pp 显著上升，r1 该域 4 PASS→r3 7 PASS）/ verification 20.0% / layout_virtuoso 20.0%。
- 通过率最低：eda_other 8.3%（r1 9.5%→8.3%）/ spice_sim 10.7%（r1 9.6%→10.7%，104 题最大域，shard B 持续加 L2.live 实跑断言承压）/ characterization 10.0%（r1 20.0%→10.0%，-10pp 下降，2 条转 ERROR/FAIL，建议 shard owner 抽查）。
- ERROR 集中在 spice_sim(5) / digital(3) / characterization(2) / verification(2)——多为 early exit，建议 owner 抽查这些域的 check.py 是否在 L2.live 改造后存在异常退出路径。

---

## ④ 下一步（zhulong 侧）
- r3 收口即起 r4（repo_commit=`8ca2f94125c4cf6396373198f95066e2ac4dd7b0`，已记 `eval/status_thermo_r4.repo_commit`）。
- r4 起跑前已做：hub health=healthy（port 25463·PID 3838918·RSS 2.0GB·r3 全程 0 FUSE 无 bloat 故未 kill-restart）+ strict canary 两证（curl /cloud/v1/models http=200 + 单 case DrcDensityParseJudge-001 真跑 verdict=PASS dur=124s）+ 身份四证（doubao-seed-2.0-pro-cloud / cloud-v1 / key末12=4f1425cdc15f / maxTokens=16384+reasoning=false）。
- 体温计连续循环，🚫 自停/降频/减题，仅用户令停。
- 本反馈供 designflow A 分派；**本线不改题/不改判分**。
