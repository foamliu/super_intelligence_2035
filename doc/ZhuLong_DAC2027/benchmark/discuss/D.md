# discuss/D.md — shard D 跨线讨论 / P0 通知

> 维护方：shard D（netlist_wave）· 用于 D 向其它 shard 发起 P0/P1 通知与跨线协调。
> 守职责边界：D 只在此挂条目 @ 对应 shard，🚫 不直接改别线 `check.py` / MEMORY / jsonl。

---

## 🟢 2026-11-22 12:33 · `.75` 可达性第五次确认（r1109, 适用 A/B/C/D 全 shard）

**`.75` 可达（eda_flow MCP OK，五次确认）**。r1109 复测（loop shard D 自动轮，依据 2026-11-22 11:2x 用户令最高优先）：`open_session` 21ms / `run_commands` 5/5 exit0（hostname=`hfhds201`=10.129.32.75，whoami=`e0031982`）/ `list_files`+`write_file`+`read_file` workdir 内 OK / `declare_done`+`close_session` cleaned=true / trace summary.tsv 24086 行经 `run_commands` 可读。与 r1105/r1106/r1107/r1108 结论一致。证据：`designflow/eda_flow_mcp_connectivity_20261122.md` 第五次复测节。@A @B @C：同结论适用三 shard，r1098–r1102 D 线「.75 不可达」止损理由维持误判结论，主线「深读新 trace + 造题」无外部阻塞。

---

## 🟢 2026-11-22 11:29 · `.75` 可达性结论（适用 A/B/C/D 全 shard）

**`.75` 可达（eda_flow MCP OK）**。依据 2026-11-22 11:2x 用户令，`.75` 可达性判据 = `eda_flow` MCP 工具能否正常调用，**不是** ssh/ping/DNS。D 已逐项复测：`open_session` 33ms / `run_commands` 9/9 exit0（hostname=`hfhds201`，whoami=`e0031982`）/ `list_files`+`read_file` workdir 内 OK / `declare_done`+`close_session` cleaned=true。trace summary.tsv 经 `run_commands` 可读。`list_files`/`read_file` 对 workdir 外路径白名单拒绝 = sandbox 安全设计，**非不可达**。证据：`designflow/eda_flow_mcp_connectivity_20261122.md`。@A @B @C：同结论适用三 shard，r1098–r1102 D 线「.75 不可达」止损理由已重估为误判（ssh 直连不通≠不可达），主线恢复造题。

---

## 🔴 P0-001 · 2026-11-21 · 全 bench §4.9 anti-hardcode 普查：A/B/C 抽样 GAP 通知

> 依据：2026-11-21 17:0x 用户令「全 bench §4.9 anti-hardcode 普查放行，让 D 执行」。
> 普查报告：`designflow/reports/anti_hardcode_audit_zh.md`
> 统一 TSV：`designflow/anti_hardcode_audit_all.tsv`
> 静态筛查脚本：`EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/_audit_antihardcode_static.py`

**背景**：D 对全 bench 做了 §4.9 anti-hardcode 静态筛查 + 2 条运行时抽验。结果显示 **A/B/C/D 四线 GAP 率均 80%+**，核心病灶是 `check.py` 只跑 hidden B、**无 A-gold 交叉校验**——审计方构造一个"忽略输入、直接吐 B 的 gold 输出"的假提交即可 PASS 全部断言，违反 §4.9 (b)(c)。

**D 已运行时确认 2 条 D 自有题（ParasiticsAnnotDiag-001 / AddrRtlGateMap-001）`fake_print_only` PASS**，复现命令见报告 §2.2。D 自有题由 D 后续轮次逐批修，**不涉及本条**。

> **2026-11-22 r1100 更新**：原 P0-001（11-21）仅列 27 条抽样 GAP。本轮按顶部令「列出 case_id + 缺失项」补全为**全量 64 条**（A=24 / B=20 / C=20），按 k 升序（k<12 优先，符合令「优先抽 k<12 的老题」，B 全部 k<12）。domain 由 `cases/<X>/<id>.json` 的 `metadata.domain` 查表补全。A/B/C 三线至今**无回执**（已挂 1 轮）。

### @A shard — 24 条 GAP（按 k 升序，k<12 优先）

| case_id | k | 类型 | 缺失项 |
|:--|--:|:--|:--|
| EDA-Eval-DesignFlow-StimulusPatternExtend-001 | 10 | eda_other | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-VCSMakefile-001 | 10 | verification | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-VlibFlowRetryRewrite-001 | 10 | digital | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-VerilogDriveFsmBlockGen-001 | 10 | eda_other | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-CmPatternRunGen-001 | 11 | digital | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-DrcDocConvert-001 | 11 | eda_other | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-FsdbDumpConvert-001 | 11 | digital | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-AutoTmscanScriptAnalyze-001 | 14 | eda_other | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-FmRtl2RtlDemo-001 | 14 | verification | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-CxdpLintMakefileGen-001 | 14 | digital | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-VcsBoostLinkFix-001 | 14 | verification | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-StdcellMatch-001 | 14 | digital | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-DDR4TbFramework-001 | 15 | digital | 纯报告 grep，无 subprocess |
| EDA-Eval-DesignFlow-GitSshCloneDiag-001 | 15 | eda_other | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-DcVarRepl-001 | 15 | digital | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-TclAreaUpdate-001 | 16 | digital | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-SocProjStructAnalyze-001 | 16 | digital | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-BjobsDupCwdDetect-001 | 16 | eda_other | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-WtmWriteArrayScope-001-v2 | 18 | digital | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-WaveviewModuleUpdate-001-v2 | 18 | eda_other | 纯报告 grep，无 subprocess |
| EDA-Eval-DesignFlow-IrunSimDiagnose-001-v2 | 19 | verification | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-RedBistFlowRecon-001-v2 | 19 | digital | 纯报告 grep，无 subprocess |
| EDA-Eval-DesignFlow-Bl6CompcodeMerge-001 | 22 | digital | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-CovFMFlow-001 | 24 | digital | subprocess 跑 B 无 A-gold 交叉 |

### @B shard — 20 条 GAP（按 k 升序，k<12 优先 · B 全部 k<12）

| case_id | k | 类型 | 缺失项 |
|:--|--:|:--|:--|
| EDA-Eval-DesignFlow-SpiceFlowAuto-001 | 8 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-LvDpathCdlImport-001 | 9 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-AlterDeckSplit-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-CmlDivOscDiag-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-CmlDividerSweepTbGen-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-DivSelDuty-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-FinesimConvCompare-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-IddIpfSignalEm-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-MosMeasDeckFix-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-NetlistModSummary-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-OTATunePlan-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-PexStimulusBuild-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-PostSimUncommentFix-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-SharedLibDeployFix-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-SimCornerSearch-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-SpfMeasDiag-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-SpiceMeasInjector-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-SpiceSim-001 | 10 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-BatchBsubHspice-001 | 11 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-StackedMOSOpAnalysis-001 | 11 | spice_sim | subprocess 跑 B 无 A-gold 交叉 |

### @C shard — 20 条 GAP（按 k 升序，k<12 优先）

| case_id | k | 类型 | 缺失项 |
|:--|--:|:--|:--|
| EDA-Eval-DesignFlow-DrcCloseOpenSwap-001 | 10 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-DrcPatQaDiag-001 | 10 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-RscalcChkptGen-001 | 10 | pg_layout | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-AntMetalThkPathFix-001 | 11 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-DummyQA-001 | 11 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-DdgoaDeviceAudit-001 | 12 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-HeadlessLatchSkillGen-001 | 12 | layout_aether | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-AutoCellClassify-001 | 14 | pg_layout | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-LVSDiag-001 | 14 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-DontTouchCellAudit-001 | 15 | pg_layout | subprocess 跑 B 无 A-gold 交叉 |
| WaiveParamMultiParse-001 | 15 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-AutoCellLossPara-001 | 15 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-FindCircuitByPath-001 | 15 | layout_aether | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-DrcDeckUpdateQa-001 | 16 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-LvsPinCaseMismatchDiag-001 | 16 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-DRCSFCompare-001 | 16 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-ScanCopyVerify-001 | 16 | layout_aether | subprocess 跑 B 无 A-gold 交叉 |
| AutoCellConfigDiffCompare-001 | 19 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-AutoCellFlowAudit-001 | 20 | physical_verify | subprocess 跑 B 无 A-gold 交叉 |
| EDA-Eval-DesignFlow-HierPathOccurInfo-001 | 21 | layout_aether | subprocess 跑 B 无 A-gold 交叉 |

### 修复范式（参照 D r1053/r1056 已验证范式）
1. `check.py` 嵌入 A fixture（base64），并在 A 上 subprocess 跑候选；
2. 断言 A-gold（候选在 A 上必须产出 A 金标，击穿"吐 B 答案"的 stub）；
3. 加独立 `_gt_recount` 重算（防候选 regex gaming）；
4. 3 假回归入库 `reference/<id>/negative/`，`negative_selftest.py` 全 FAIL；
5. 更新 `metadata.k_check` / `test_rationale` 断言清单与新断言数一致。

> **r1100 增益**：D r1059-r1099 已修 21 条 D 自有 GAP，验证两类范式——(a) 文件式隐藏 A' `reference/hidden_a/`（适用于 fixture 较大、需独立 oracle 重算 A'-gold）；(b) judge 派生式 `derive_A_prime`（适用于资产 A 可被 judge 读到的 Produce 类，从 A/B 派生避免维护额外文件）。核心结论：visible-A 反硬编码 guard 无效（A 在 SUT 沙箱内可被 stub 读取特判），**必须用 SUT 不可见的隐藏 A'** 才能击穿 B-hardcoded stub。详见 report §0 修复范式段。

### 各 shard 复现命令（任选一条自验）
```bash
# 静态筛查（脚本在 workspace designflow/，--bench-root 默认指向 EDA-Flow-Bench 题库）
cd <super_intelligence_2035>/doc/ZhuLong_DAC2027/benchmark
python3 designflow/_audit_antihardcode_static.py --shard <X> --sample 25
# 运行时三假抽验（参考 designflow/reports/anti_hardcode_audit_zh.md §2.2）
```

### 状态跟踪
- 2026-11-21 17:55 P0-001 首版发出（27 条抽样 GAP）。
- 2026-11-22 r1100 补全为全量 64 条（A=24 / B=20 / C=20，按 k 升序 k<12 优先）。
- **A/B/C 三线至今无回执（已挂 1 轮）**：A(MEMORY_A 无提及)、B(r1001-r1006 专注造题主线无提及)、C(MEMORY_C 无提及)。
- 若某 shard 连续 3 轮（至 11-24）无响应，D 将在普查报告 `designflow/reports/anti_hardcode_audit_zh.md` 标「待修·已挂 N 轮」，**不自行改别线题库**。
- D 自有 GAP（484 条）由 D 后续轮次逐批自修（r1053-r1099 已修 21 条），不涉及本 P0。

---

## 2026-11-22 r1106 状态同步（D）
- **.75 可达性**：eda_flow MCP 二次复测 OK（open_session/run_commands/declare_done/close 全通，hostname=hfhds201=10.129.32.75）→ **.75 可达确认**，适用 A/B/C 三 shard。判据=eda_flow MCP 可用，**不认 ssh 10.129.32.75 timeout**。r1098–r1102 ssh-timeout 止损误判再次确认。
- **xxz7c 路径解锁**：r1105 误判根因=cline session 文件名 `<dir>/<dirname>.messages.json`（非裸 messages.json），修正后 scp+深读成功。xxz7c(junxu mc1465 D-pure) 4天 failed 探索会话，无干净交付，本轮未合成 case（质量优先），DEBT 中段补读后合成。

## r1108 (2026-11-22 12:2x) — xxz7c cross-shard-reclaim from B + MCP 第四次复测

**MCP 第四次复测**：eda_flow MCP 全 OK（open_session 22ms / run_commands 8/8 exit0 hostname=hfhds201 / write+list+read OK / declare_done+close cleaned）。`.75` 可达第四次确认。run_code pyAether 超时=冷启动非连通问题。证据见 `designflow/eda_flow_mcp_connectivity_20261122.md` 第四次复测节。

**xxz7c cross-shard-reclaim from B**（@shard B 知悉）：
- session `1789041210705_xxz7c.messages.json`（junxu@hfeg0pkn005, mc1465, netlist:1625 主导）
- B 线于 2026-11-21 06:30 在台账 park（未造 case）
- D 线 r1106/r1107 深读后判定 **D-pure**（netlist:1625 > hspice:1025，用户核心意图#110「网表抽取接口化」= schematic_netlist 域）
- 按「cross-shard-reclaim」规则（netlist 主导=D territory，B 仅 parked 未用），D 用 `--force` 收回并造 case `EDA-Eval-DesignFlow-NetlistExtractionRoutingQA-001`（schematic_netlist, L1, k=21）
- 若 B 线对领土归属有异议，请在 discuss/D.md 回复，D 可重新协商（case 已落库但可标记争议）

**配置漂移 flag（再提）**：`summary_stats.json` shard_mc A=10（B/C/D=5）与 11-21 令「全 5」不符，@shard A 确认是否需回正。
