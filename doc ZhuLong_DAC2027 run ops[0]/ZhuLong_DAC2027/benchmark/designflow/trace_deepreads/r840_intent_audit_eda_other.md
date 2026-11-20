# r840 意图审计 — eda_other 历史存量批 (73 case)

> 2026-11-15 最高优先令续做。本轮审计 eda_other 全部 73 条未审 case（DEBT 指定优先目标）。
> 审完后 eda_other 域 93/93 全审完，pnr_signoff 41/41 全审完（r839）。

## 审计范围

- 本轮：eda_other 域 73 条未审 case（A.jsonl 415 中 eda_other=93, 已审 20, 剩 73）
- 来源：A.jsonl 全量逐条读取 trace_source.real_task_summary + prompt + test_rationale + check
- 判据：① 问的是 trace 用户真实想干的事吗 ② check 超出用户原始意图吗 ③ 被旧配额降级/裁剪过吗

## 判定结果

| 判定 | 数量 |
|:--|--:|
| keep | 73 |
| off_intent | 0 |
| over_constrained | 0 |
| downgraded | 0 |

**全部 keep。** 与 r836(batch2 generic-named 40)/r837(v1-v2 对照 80)/r839(pnr_signoff 32) 一致结论：
**旧配额扭曲是「选题模具」问题，非「已造题内容」问题。** eda_other 域已造题忠实还原用户真实意图。

## 形态分布（观察）

73 条 eda_other case 的真实任务形态分布：
- **produce-task / flow-build**（~45）：写脚本/工具自动化（DelPgLib/FindPcells/BtopPendJobs/CdlTbGen/LsfPrimesimSubmit/V2lvsCdlCheck/QualibTclGen/Tcl2SkillTranspile/VerilogDriveFsmBlockGen/StimulusPatternExtend/TqvVrefreshBuild/SwbProjectCreate/SiliconInstGen/RunsetVer/RunsetVerFind/SPFCoupling/SpfCouplingParser/EmXlsModel/DecoderSchemGen/FloatPinToTop/AutoCellTclFlow/DftTestmaxLaunchFlow/PdkMutateVerify/JobmonitorFeatPatch/QtProUserMigrate/SyncManifestCheck/ViewCopyInstCount/VirtuosoToolLocator/VltRetryWave2/PdkDirSizeScan 等）
- **analysis-Q&A / code-comprehension**（~22）：分析脚本/项目/网表结构（AgentCodeStructAnalyze/AutoTmscanScriptAnalyze/HspiceTbStructAnalyze/SpiceStructAnalyze/CosimFlowAnalyze/LogicCosimProjAnalyze/LowPowerFlowPlanAnalyze/RunRegrArchAnalyze/TbFamilyRoleAnalyze/SimLibGuiAnalyze/NetlistDiffDelayAnalyze/PtempCondUsageAnalyze/CornerStrUndefDiagnose/NetlistCompareReport/ItfCompare/DdjocCircuitPlanReconQA/SignalBusNameCheckExplain 等）
- **debug-Q&A / env-config**（~6）：诊断报错/环境问题（ClineWorkdirDiagnose/InnovusLaunchDiag/CalVcoEnvWorkaround/GitSshCloneDiag/HelperFilesOrganize）
- **doc-search / 知识-Q&A**（~4）：查 API 文档/总结接口（PyAetherCurDesignApi/WvCursorApiGen/VpsInterfaceSummaryQA/ToolRcFormatMapQa）

**这正是 11-15 reaudit 后 eda_other 域应有的真实分布** —— analysis-Q&A/debug-Q&A/doc-search/env-config 全部合法，
与 produce-task 并存。无任何一类被旧规则误杀后强行脚本化。

## §5 produce-task reframe 说明（合法 reframe，非 over_constrained）

8 条 case 把「Q&A / 不可 headless 跑的 GUI 交互 / 不可复现的远程克隆」reframe 成 produce-task，
这是 §5 既定模式（Q&A 难直接判分时落成可判分脚本），**check 校验的是用户真实想要的知识/产物结构**，
不是超意图加难。逐条核验：

| case | 用户原话意图 | reframe | check 校验对象 | 判定 |
|:--|:--|:--|:--|:--|
| FinesimDcConvCatalogAnalyze-001 | "DC不收敛的原因及解决方案有哪些" | extract_dc_catalog.py 从文档抽取 | catalog 结构化内容 | keep(Q&A→produce-task reframe) |
| ToolRcFormatMapQa-001 | "genus/DC/starRC 吃 TLUPlus 还是 QRC" | analyze_tool_rc_format_mapping.py | 工具↔格式映射表 | keep(Q&A→produce-task reframe) |
| GitSshCloneDiag-001 | "git clone 反复失败" | git_ssh_diag.py 解析 ssh -vvv | 根因分类+修复 | keep(克隆不可复现→诊断脚本 reframe,11-15 合法) |
| SentaurusTcadProjectGenProduce-001 | "生成一个 sentaurus swb project" | swb_gen.py 参数化生成器 | 4 SWB 文件参数化 | keep(静态 4 文件难 hidden-B 反硬编→生成器 reframe) |
| WvDataeyeMeasure-001 | "眼图 VREF 扫描" | gen_wv_eye_pipeline.py | 参数化 TCL 生成 | keep(fsdb 不可 headless→生成器 reframe) |
| WvPropDelayMeasure-001 | "测 tPHL/tPLH" | gen_propdelay_measure.py | 参数化 TCL 生成 | keep(.tr0/license 不可跑→生成器 reframe) |
| JobmonitorFeatPatch-001 | "Qt 3 项功能增强" | gen_jobmonitor_patch.py 通用锚点 | 3 功能增强 | keep(trace patch 应用失败→通用生成器 reframe) |
| WvSineWaveAnalyze-001 | "画正弦波+过零/频率/峰值" | sine_wave_analysis.tcl(B档) | sx_meas_* 调用 | keep(沙箱不可达→B档 synthesized) |

## 3 near-dup 对（flag cross-case dedup，非意图问题）

3 对同 user 同任务不同 session 的 case，**各自忠实于自己的 trace session，非重复造题**，
但任务主题重复，建议后续 cross-case dedup 专门轮处理（不删，仅标记/去重分母）：

| 对 | user | 共同任务 | 区分 |
|:--|:--|:--|:--|
| RunsetVer-001 ≈ RunsetVerFind-001 | hbpeng | RunsetVersionFinder.py 加 LDDB 特殊处理 | session nqgxe(hfeg0pin004 mc460) vs 6vcuk(hfeg0pkn005 mc124) |
| SPFCoupling-001 ≈ SpfCouplingParser-001 | ray1lei | SPF coupling→CSV(SABL 23 列) | session 5pv45(直接脚本) vs bhcla(含 skill 打包 reframe) |
| HspiceTbStructAnalyze-001 ≈ SpiceStructAnalyze-001 | t0002614 | "analyze structure of the netlist" | session u0mwh(mc165) vs y6liq(mc150) |

## 审计进度

| 域 | 已审/总数 | 剩余 |
|:--|:--|:--|
| digital | 32/151 | 119 |
| eda_other | 93/93 | 0 ✅ |
| pnr_signoff | 41/41 | 0 ✅(r839) |
| verification | 31/130 | 99 |
| **合计** | **225/415** | **190** |

下轮优先：verification 历史存量 99（与 digital 119 并列最多，verification 是 A 核域优先）。

## 守纪律

- 只审 A 域 case（eda_other 属 A），未碰别 shard
- 审计结论逐条可溯源到 trace（user/host/session_file/real_task_summary 已入 TSV）
- 未删任何 case / 未改任何 jsonl（审计 = 只读 + 追加 TSV）
