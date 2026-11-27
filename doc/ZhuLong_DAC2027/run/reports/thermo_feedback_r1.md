# thermo_feedback_r1.md — 体温计 r1 收口反馈（致 designflow A 分派）

> 生成：2026-11-27 09:1x（wake#2089，zhulong 体温计线）
> 数据源：`eval/status_thermo_r1.jsonl`（500/500 judged）
> 对照基线：`eval/status_doubao_pro_rerun2_r3.jsonl`（rerun#2 r3'，500 cases，同为 MIXED）
> ⚠️ **本线只报现象，不改题/不改判分**。下列 case_id 请各 shard owner 自行核验（谁的槽位谁修）。

---

## ① 本轮 Pass@1 + 轮级状态

| 项 | 值 |
|:--|:--|
| 轮次 | thermo r1 |
| 被测模型 | doubao-seed-2.0-pro-cloud（thinking low / reasoning.enabled=false / maxTokens=16384）|
| workers | 4 |
| cases | 500（全 judged） |
| PASS / FAIL / ERROR | 74 / 412 / 14 |
| decided (PASS+FAIL) | 486 |
| **Pass@1** | **74/486 = 15.23%** |
| FUSE / 额度耗尽 / 熔断 | 0 / 0 / 0（infra 侧 clean） |
| runtime | ~8.5h（00:36 → 09:06） |
| 起跑 repo_commit | `e7a9b669c3c0a15e5230895a1e15f32ef7dd0075` |
| 收口 repo_commit | `a8fc224cd7787e98cd013d746e1da6c5235884e9`（窗口内 25+ commit·漂移） |
| live_eval_changes.tsv | 起跑 38 行 → 收口 42 行（**+4**，窗口内 07:10/07:50/08:20/08:30/09:10 共 5 条 designflow 改判登记） |
| **轮级状态** | 🟡 **MIXED**（窗口内 repo_commit 漂移 + live_eval_changes +4 ⇒ 不入 3-run mean±std，数字保留仅作体温信号） |

**解读**：r1 是体温计首轮，MIXED 是预期状态（designflow 在窗口内持续提交 L2.live 改造，shard B 第 17–21 条）。Pass@1=15.23% 相比 rerun#2 三轮（r1'=13.81% / r2'=14.40% / r3'=16.26%）落在同一区间，**无异常跳变**。infra 侧 0 FUSE 健康。体温计已起 r2（repo_commit=`2771644fb`…）。

---

## ② 新增 ERROR / 新增 FAIL 的 case_id 清单（vs r3'）

> 对照 = rerun#2 r3'（`status_doubao_pro_rerun2_r3.jsonl`，500 cases，同为 MIXED）。
> ⚠️ r3' 本身也是 MIXED（窗口内 repo_commit 漂移），故下方 diff 同时混有「模型方差」与「designflow 改判」两种来源——**单条结论需 owner 结合本 case 的 `live_eval_changes.tsv` 登记与 commit 历史核验**，不可直接归因。

### 新增 ERROR（r3' 非 ERROR → r1 ERROR）：2
| case_id | r3' | r1 | 建议排查方向 |
|:--|:--|:--|:--|
| EDA-Eval-DesignFlow-GrDecPwrVerifTb-001 | FAIL | ERROR | early exit；查 cline 是否中途 abort / harness 是否抛异常 |
| EDA-Eval-DesignFlow-PkgVarPassDutTb-001-v2 | FAIL | ERROR | early exit；同上 |

### 全部 14 个 ERROR（r1，均为 reason=early exit / fail_stage=None）
> 这些是 cline 中途退出（未产出有效交付件），多属 harness/模型侧，但 owner 可核验是否近期 check.py 改动导致判分器异常退出：
```
EDA-Eval-DesignFlow-ButterflyCurve-001
EDA-Eval-DesignFlow-GrDecPwrVerifTb-001
EDA-Eval-DesignFlow-ModuleFuncCatalog-001
EDA-Eval-DesignFlow-OtaAcReport-001
EDA-Eval-DesignFlow-PkgVarPassDutTb-001-v2
EDA-Eval-DesignFlow-RefModelBugFix-001
EDA-Eval-DesignFlow-RefreshRunAnalyze-001-v2
EDA-Eval-DesignFlow-RunRegrSubmit-001-v2
EDA-Eval-DesignFlow-SpfAutosimSetup-001
EDA-Eval-DesignFlow-TbFamilyRoleAnalyze-001
EDA-Eval-DesignFlow-TscodecompTbVerify-001
EDA-Eval-DesignFlow-VlshftParamOpt-001
EDA-Eval-DesignFlow-WtmWriteArrayScope-001-v2
EDA-Eval-DesignFlow-WvPropDelayMeasure-001
```

### 新增 FAIL（r3' PASS → r1 FAIL）：19（回归方向，请 owner 优先核验）
```
EDA-Eval-DesignFlow-AutoViaPFAudit-001
EDA-Eval-DesignFlow-Backannot-001
EDA-Eval-DesignFlow-CdlBulkSanitize-001
EDA-Eval-DesignFlow-CrEdgeAlignFix-001
EDA-Eval-DesignFlow-DecoderNetlistGen-001
EDA-Eval-DesignFlow-DummyTargetLayerCmp-001
EDA-Eval-DesignFlow-FsdbPulseFilter-001
EDA-Eval-DesignFlow-InnovusProjLogDiag-001
EDA-Eval-DesignFlow-InnovusPwrRtDiag-001
EDA-Eval-DesignFlow-LefPostprocessFix-001
EDA-Eval-DesignFlow-MVVarNamingAudit-001
EDA-Eval-DesignFlow-NetlistModSplice-001
EDA-Eval-DesignFlow-PexStimulusBuild-001
EDA-Eval-DesignFlow-RTextChkPlan-001
EDA-Eval-DesignFlow-RandStimVecFix-001
EDA-Eval-DesignFlow-ResFlow-001
EDA-Eval-DesignFlow-SpiceSim-001
EDA-Eval-DesignFlow-SpiceTbGen-001
EDA-Eval-DesignFlow-TempSelWaveform-001
```

### 新增 PASS（r3' FAIL → r1 PASS）：14（改善方向，供参考）
```
EDA-Eval-DesignFlow-CalibreLvsRepDiag-001
EDA-Eval-DesignFlow-CombCellNetlistSyn-001
EDA-Eval-DesignFlow-DeckConsistencyCheck-001
EDA-Eval-DesignFlow-DummyCfgCheck-001
EDA-Eval-DesignFlow-FinesimIgnoreGen-001
EDA-Eval-DesignFlow-GpioPortRefactor-001
EDA-Eval-DesignFlow-LibToParm-001
EDA-Eval-DesignFlow-Lpddr5CovTermitFix-001
EDA-Eval-DesignFlow-NetlistChk-001
EDA-Eval-DesignFlow-PFMergeAudit-001
EDA-Eval-DesignFlow-PortCatch-001
EDA-Eval-DesignFlow-SignalRunXref-001
EDA-Eval-DesignFlow-SpiceClosureExtract-001
GdsLayerAreaMeasure-001
```

**净效应**：19 回归 − 14 改善 = 净 −5（PASS 数 r3'=79 → r1=74，−5）。在模型固定 + 双方均 MIXED 的前提下，净 −5 主要由 designflow 窗口内改判（+4 行 live_eval_changes，多为 shard B 加 L2.live 实跑断言）驱动——**符合预期**：加严判分（L2.live 实跑）会先把一批原本静态通过的 case 压回 FAIL，等候选/资产就绪后会回升。这不是模型变弱。

---

## ③ 13 个 domain 的分域通过率（r1）

> domain 取 `metadata.domain` 顶层（split on `/`）。9 条 task_id 未在主 jsonl 映射到 domain（多为 `-v2` 变体），归入 unknown。

| domain | PASS | FAIL | ERROR | decided | Pass@1% |
|:--|--:|--:|--:|--:|--:|
| analog_context | 4 | 22 | 0 | 26 | 15.4 |
| characterization | 4 | 16 | 2 | 20 | 20.0 |
| digital | 7 | 30 | 3 | 37 | 18.9 |
| eda_other | 2 | 19 | 2 | 21 | 9.5 |
| layout_aether | 5 | 25 | 0 | 30 | 16.7 |
| layout_virtuoso | 4 | 21 | 0 | 25 | 16.0 |
| pg_layout | 4 | 12 | 0 | 16 | 25.0 |
| physical_verify | 12 | 54 | 0 | 66 | 18.2 |
| pnr_signoff | 2 | 13 | 0 | 15 | 13.3 |
| schematic_netlist | 11 | 54 | 1 | 65 | 16.9 |
| spice_sim | 10 | 94 | 4 | 104 | 9.6 |
| verification | 6 | 21 | 2 | 27 | 22.2 |
| waveform | 3 | 21 | 0 | 24 | 12.5 |
| netlist | 0 | 1 | 0 | 1 | 0.0 |
| unknown (-v2 等) | 0 | 9 | 0 | 9 | 0.0 |
| **TOTAL** | **74** | **412** | **14** | **486** | **15.23** |

**观察**：
- 通过率最高：pg_layout 25.0% / verification 22.2% / characterization 20.0%。
- 通过率最低：spice_sim 9.6%（104 题最大域，且 shard B 正在批量加 L2.live 实跑断言，预期短期承压）/ eda_other 9.5% / waveform 12.5%。
- ERROR 集中在 spice_sim(4) / digital(3) / characterization(2) / verification(2)——多为 early exit，建议 owner 抽查这些域的 check.py 是否在 L2.live 改造后存在异常退出路径。

---

## ④ 下一步（zhulong 侧）
- r1 收口即起 r2（repo_commit=`2771644fb6078dbc6e7a14ba8bc7f29a0c1fee51`，已记 `eval/status_thermo_r2.repo_commit`）。
- r2 起跑前已做：hub health=healthy（port 25463·coreVersion 0.0.71·r1 全程 0 FUSE 无 bloat 故未 kill-restart）+ strict canary 两证（curl /cloud/v1/models http=200 + 单 case DrcDensityParseJudge-001 真跑）+ 身份四证（doubao-seed-2.0-pro-cloud / cloud-v1 / key末8=25cdc15f / maxTokens=16384+reasoning=false）。
- 体温计连续循环，🚫 自停/降频/减题，仅用户令停。
- 本反馈供 designflow A 分派；**本线不改题/不改判分**。
