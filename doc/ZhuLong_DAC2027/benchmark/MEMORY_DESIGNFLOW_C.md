LITE_FIX: C=137/137 full-L0-L5=111111 (r1191 stalest-latest-ts re-verify 3 cases 15:37Z cohort (oldest non-cross-shard latest-ts) — NetHierTrace-001 REAL P1 CAUGHT+FIXED (r1189 LESSON generalized: 3-of-4 negs collapsed onto cond3 top_module identity check = 2-distinct {cond2,cond3} ONLY <3; negselftest 'ALL NEGATIVES FAIL: True' did NOT catch the shared-contour false-distinct; FIX negative-only: replaced no_traversal.py->NEW core_deleted.py §4.9c derived-from-gold empty-upstream/downstream/boundary fails cond5 + rewrote hardcoded_A.py embeds full correct gold B output + injects stray A-template 'SampTop' token into tree fails cond13 cross-input guard; empty_stub(cond3)/always_print(cond2) unchanged; POST-FIX 4neg ALL-FAIL first-fail {cond2,cond3,cond5,cond13}=4-distinct, §4.9 trio {empty=cond3,print=cond2,core=cond5}=3-distinct no-DEBT; 0 check.py/14 conds/strictness change, check.py git-diff empty) + NicapNetlistPivot-001 0-fix TRUE-GREEN literal-spec (3-distinct {c,f,j}>=3; §4.9 trio {c,c,f}=2-distinct DEBT shared-label cond c=real semantic no-args-CLI check NOT crash, trio-pairwise-distinct pending zhulong/A ruling) + PortPropagate-001 0-fix TRUE-GREEN literal-spec (3-distinct {a,f,g}>=3; §4.9 trio {a,g,g}=2-distinct DEBT shared-label cond g=real semantic no-wire check NOT crash, selftest flags TRIO_PAIRWISE_DISTINCT_REQUIRED=False). All 3 L1 audit OK shapes=['True']x3; L2 real-harness-equivalent stage check()=>True x3 (refzip+helpers+hidden-B in temp judge dir w/ symlink tree); L4 gui-clean (NetHierTrace sole subprocess=python candidate; NicapNetlistPivot/PortPropagate pure-python+mock); L5 hidden-B in assets/.../hidden/ NOT shipped SUT (attachments A-only). 计数口径=latest-by-ts + norm id(剥 EDA-Eval-DesignFlow-) + L0-L5全1 + status in green/p0_fixed/p1_fixed/p3_fixed. C 侧 P0 余 0 · P1 余 0 (本轮修 1) · P3 余 0 · pending 0. cross_shard UNCHANGED: 净 cross-shard P0 = 2 (OpampChar L2-stale-refzip CONFIRMED-by-C r1171 + InvTripDelay full-FAIL; B 未触). md5=f7816ef4137353904e40a1a3b01fb3ae unchanged (500 行). 本 shard Lite=137 unchanged.
WAITING: 0 (r1191 Lite-500-fix 第119轮: stalest-latest-ts defensive re-verify 3 cases 15:37Z cohort (oldest non-cross-shard latest-ts). NetHierTrace-001 REAL P1 false-distinct CAUGHT+FIXED (r1189 LESSON generalized beyond crash-technicalities to ANY shared first-fail contour): prior 4neg = {empty_stub=cond3, always_print=cond2, no_traversal=cond3, hardcoded_A=cond3} = 2-distinct ONLY -- negselftest reported 'ALL NEGATIVES FAIL: True' but 3-of-4 negs collapsed onto cond3 (top_module identity check) so grader only proved teeth on 2 distinct assertions. FIX (negative-only, 0 check.py/14 conds/strictness change, check.py git-diff empty, r1189-consistent): (1) replaced no_traversal.py with NEW core_deleted.py (§4.9c derived-from-gold: correct top_module/module/instance_chain/driver + valid tree markers, but upstream/downstream/boundary_inputs EMPTIED -> passes conds 1-4, fails cond5 'upstream n017<-I77/invGFDx2/Y missing'); (2) rewrote hardcoded_A.py (was cond3 top_module=SampTop; now embeds full correct gold B output + injects stray A-template token 'SampTop' into tree field -> passes conds 1-12 + determinism cond14-not-reached, fails cond13 'A-specific token SampTop leaked into B output' = cross-input guard teeth); empty_stub.py (cond3) + always_print.py (cond2) unchanged; negative_selftest.py NEGATIVES list updated no_traversal->core_deleted. POST-FIX 4neg ALL-FAIL first-fail labels INDEPENDENTLY re-mined via check.py-as-script: {empty_stub=cond3 'top_module=.. expected ColCtrlTop', always_print=cond2 '--out JSON not produced', core_deleted=cond5 'upstream n017<-I77/invGFDx2/Y missing', hardcoded_A=cond13 'A-specific token SampTop leaked'} = 4-distinct>=3; §4.9 trio {empty=cond3,print=cond2,core=cond5}=3-distinct no-DEBT. NicapNetlistPivot-001 0-fix TRUE-GREEN literal-spec: 5neg ALL-FAIL first-fail {empty=condc,print_expected=condc,core_deleted=condf,naive_hardcode=condf,always_pass=condj}={c,f,j}=3-distinct>=3 MET literal; §4.9 trio {c,c,f}=2-distinct DEBT (shared cond c=no-args CLI validation = real semantic NOT crash; trio-pairwise-distinct pending zhulong/A ruling, no preemptive fix). PortPropagate-001 0-fix TRUE-GREEN literal-spec: 5neg ALL-FAIL first-fail {empty_shell=conda,print_only=condg,core_deleted=condg,naive_hardcode_a=condg,omit_path_print=condf}={a,f,g}=3-distinct>=3 MET literal; §4.9 trio {a,g,g}=2-distinct DEBT (shared cond g=no-wire-on-TopB = real semantic NOT crash; selftest flags TRIO_PAIRWISE_DISTINCT_REQUIRED=False). All 3 L0 full-name refdir w/ check.py+ref sol+reference_submit.zip+negative/; L1 audit_check_returns OK shapes=['True']x3; L2 real-harness-equivalent stage (refzip+check.py+helpers+hidden-B in temp judge dir w/ symlink tree matching run_one.sh judge step) check()=>True x3 / PortPropagate check_static()=>(True,'',''); L4 gui-clean (grep wv/verdi/innovus/virtuoso/calibre/vcs/hspice in check.py=0; NetHierTrace sole subprocess=[sys.executable,py,--netlist,...] python candidate; NicapNetlistPivot/PortPropagate pure-python+mock-pyAether); L5 hidden-B (NetHierTrace col_ctrl_netlist.v / NicapNetlistPivot netlists/ / PortPropagate hidden inputs) in assets/.../hidden/ NOT shipped SUT (case JSON attachments A-only; hidden_manifest.json metadata-only standard contract disclosure). NetHierTrace check.py UNCHANGED (git diff empty); negative-only rewrite. md5=f7816ef4 unchanged. C 137/137 真绿 holds. LESSON: r1189 LESSON generalizes -- negselftest 'ALL NEGATIVES FAIL: True' / 'distinct_negatives=N' never sufficient; must INDEPENDENTLY mine first-fail LABELS (re-grep [cond X] / 'FAIL -' format) for EVERY neg set, because N negs can collapse onto <3 distinct first-fail contours even without any crash (here 3 negs shared cond3 identity check = real assertion, not crash, still false-distinct). 11th false-green catch by stalest-latest-ts rotation, 3rd P1-distinctness catch.)
> **轮(r1190) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1191，2026-11-26）。**[摘要: Lite-500-fix 第118轮 · stalest-latest-ts defensive re-verify 3 cases 15:25+15:36Z cohort · DdgoaDeviceAudit-001 REAL P1 CAUGHT+FIXED (r1189 LESSON: fake_empty §4.9a CRASHED check.py at unguarded _load line196 FileNotFoundError on out_A.json BEFORE any _cond — empty-stub rc0 but wrote no file, _cond("a",rc0) passed then _load raised uncaught = no teeth on §4.9a; FIX rewrote fake_empty -> writes valid JSON {} -> fails cleanly cond b type_count None!=30; 0 check.py/27 conds/阈值 change, negative-only) -> 5neg {b,c,d}=3-distinct trio{empty=b,print=d,core=c}=3-distinct no-DEBT. ABMatchPlacementCheck-001 0-fix TRUE-GREEN. ConnChkSummaryGen-001 0-fix TRUE-GREEN. C 137/137 真绿 · cross_shard P0=2 pending B · 原文见 archive]
> **轮(r1189) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1190，2026-11-26）。**[摘要: Lite-500-fix 第117轮 · stalest-latest-ts re-verify 4 cases 14:45Z cohort · 3 0-fix TRUE-GREEN + DrcPairWaiveClassify-001 REAL P1 CAUGHT+FIXED (neg-distinctness false-green: negselftest distinct_negatives=5 counted NAMES not first-fail LABELS; 4 fakes crashed at cond b on file!=stdout formatting technicality = no teeth) -> rewrote 4 negatives surgically -> 5-distinct {c,d,e,j,k} trio{c,k,e}=3-distinct no-DEBT · C 137/137 真绿 · cross_shard P0=2 pending B · 原文见 archive]
> **轮(r1187) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1188，2026-11-26）。**[摘要: Lite-500-fix 第115轮 · stalest-latest-ts re-verify 2 cases 14:35Z cohort · MVValueCmp-001 REAL P0 false-green CAUGHT+FIXED (missing refzip built from drc_value_check.py) + RoutingTrackFinder-001 0-fix TRUE-GREEN + P4 selftest-runner hygiene-fix · C 137/137 真绿 · cross_shard P0=2 pending B · 原文见 archive]
> **轮(r1186) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1187，2026-11-26）。**[摘要: Lite-500-fix 第114轮 · stalest-latest-ts re-verify 2 cases 13:50Z cohort · AutoViaPFAudit-001 + CalibreLvsRepDiag-001 BOTH REAL P0 false-green CAUGHT+FIXED (r1127 FALSE-GREEN: missing refzip; CalibreLvs also rel-path-vs-temp-cwd portability bug) · C 137/137 真绿 · cross_shard P0=2 pending B · 原文见 archive]
> **轮(r1184) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1184，2026-11-26）。**[摘要: Lite-500-fix 第112轮 · stalest-latest-ts defensive re-verify 2 cases 13:30Z cohort (oldest non-cross-shard latest-ts). ALL 2 0-fix TRUE-GREEN L0-L5=111111 · ArgusDeckEquivAudit-001 + AutoCellClassify-001 · NO false-green caught · C 137/137 真绿 · cross_shard P0=2 pending B · 原文见 archive]
> **轮(r1183) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1184，2026-11-26）。**[摘要: Lite-500-fix 第111轮 · stalest-latest-ts defensive re-verify 12 cases (10:46-cohort 1 + 11:54:13-cohort 11) ALL 0-fix TRUE-GREEN L0-L5=111111 · NO false-green caught (1st 0-catch round after 4 consecutive catches) · C 137/137 真绿 · cross_shard P0=2 pending B · 原文见 archive]
> **轮(r1182) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1183，2026-11-26）。**[摘要: Lite-500-fix 第110轮 · stalest-latest-ts defensive re-verify 2 cases 10:39-cohort · ErcSetupGen-001 0-fix TRUE-GREEN + RNodePlan-001 REAL P0 false-green FIX (missing refzip, r1146 direct-check()=>{pass:True} false-green; built refzip from rnode_planner.py; P1 added omit_rtext_placement_gutted §4.9c neg 4neg->5neg 4-distinct) · C 137/137 真绿 · cross_shard P0=2 pending B · 原文见 archive]
> **轮(r1181) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1182，2026-11-26）。**[摘要: Lite-500-fix 第109轮 · stalest-latest-ts defensive re-verify 2 cases · RtextChkPlan-001 REAL P0 FIX (missing refzip, r1139 __main__ self-test false-green) + GdsLayerAreaMeasure-001 REAL P0 FIX (missing refzip, r1104 direct-check false-green, short task_id) · C 137/137 真绿 · cross_shard P0=2 pending B · 原文见 archive]
> **轮(r1180) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1181，2026-11-26）。**[摘要: Lite-500-fix 第108轮 · stalest-latest-ts 22:26-cohort defensive re-verify 2 cases · AdjViaSelect-001 REAL P0+P1 FIX (reference_submit.zip MISSING->built; check.py _run_script exec SUT printed to stdout polluting judge JSON -> contextlib.redirect_stdout/stderr devnull portability fix 15 conds a-o; §4.9 trio print-expected neg added) + AntPatternConfigAudit-001 0-fix TRUE-GREEN · cross_shard UNCHANGED P0=2 pending B · 原文见 archive]
> **轮(r1178) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1179，2026-11-26）。**[摘要: Lite-500-fix 第106轮 · stalest-latest-ts defensive re-verify 1 case ViaFillSvrfGen-001 0-fix TRUE-GREEN (L0-L5=111111, §4.9 trio {d,u,l}=3-distinct no-DEBT) · cross_shard P0=2 pending B · 原文见 archive]
> **轮(r1177) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1178，2026-11-26）。**[摘要: Lite-500-fix 第105轮 · stalest-latest-ts 08:56-cohort defensive re-verify 收尾 3 cases (SchPinAnalyze-001 0-fix TRUE-GREEN + SkillFlowAnalyzer-001 REAL P0 false-green RESOLVED via bench-build fc473c69c refzip regen + VTTFLayerMap-001 0-fix TRUE-GREEN) · cross_shard UNCHANGED P0=2 pending B · 原文见 archive]
> **轮(r1176) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1177，2026-11-26）。**[摘要: Lite-500-fix 第104轮 · stalest-latest-ts 08:56-cohort defensive re-verify · 1 TRUE-GREEN 0-fix (RNodeCovAudit-001) + 1 REAL P1 FIX (RsCalcFlowOrch-001 §4.9c core-deleted neg MISSING -> created neg_core_deleted.py) · cross_shard UNCHANGED P0=2 pending B · 原文见 archive]
> **轮(r1175) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1176，2026-11-26）。**[摘要: Lite-500-fix 第103轮 · stalest-latest-ts 08:56-cohort defensive re-verify 2/2 TRUE-GREEN 0-fix (PFMergeDupAudit-001 + QaCellRuleLabelGen-001) · cross_shard UNCHANGED P0=2 pending B · 原文见 archive]
> **轮(r1174) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1175，2026-11-26）。**[摘要: Lite-500-fix 第102轮 · stalest-latest-ts 09:20-cohort defensive re-verify 2/2 TRUE-GREEN 0-fix (AntPatternConfigAudit-001 + NetDelSaveAudit-001) · cross_shard UNCHANGED P0=2 pending B · 原文见 archive]
> **轮(r1172) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1173，2026-11-26）。**[摘要: Lite-500-fix 第100轮 · oldest-ts 09:10-cohort defensive re-verify 2/2 TRUE-GREEN 0-fix (DrcPatternPkgGen-001 + MVVarNamingAudit-001) · cross_shard UNCHANGED P0=2 pending B · 原文见 archive]
> **轮(r1171) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1172，2026-11-26）。**[摘要: Lite-500-fix 第99轮 · oldest-ts defensive re-verify 2/2 TRUE-GREEN 0-fix (PowerFill-001 @ 03:48 + CentroidPlaceAudit-001 @ 07:45) + read-only cross-shard retest CONFIRMS OpampChar-001 REAL P0 L2-false-negative (stale refzip mtime 2026-10-31 vs check.py r1222; B r1228 误计 green) · InvTripDelay UNCHANGED full-FAIL · cross_shard P0=2 UNCHANGED · 原文见 archive]
> **轮(r1170) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1171，2026-11-26）。**[摘要: Lite-500-fix 第98轮 · 08:56-cohort defensive re-verify 6/6 TRUE-GREEN · 4 cases r1139 false-green (refzip MISSING, bulk-added by shard-A de7da5956) verified real-green · 0-fix · 原文见 archive]
> **轮(r1163-WAITING-DETAIL) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1164，2026-11-25）。**[摘要: Lite-500-fix 第91轮 WAITING 行明细 DummyQA-001 + LVSLogFilter-001 完整 L0-L5 验证明细 (07:10 cohort), 原文见 archive]
> **轮(r1162-WAITING-DETAIL) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1163，2026-11-25）。**[摘要: Lite-500-fix 第90轮 WAITING 行明细 HeadlessLatchSkillGen-001 + StrongARMComp-001 完整 L0-L5 验证明细 (06:15 cohort 收尾), 原文见 archive]156 未触. 📦 体积: TASK≈30KB / MEMORY≈25KB. 下轮维持 WAITING:0, 继续 oldest-ts re-verify (next: 06:59 StarrcReleaseNoteGen / 07:10 DummyQA+LVSLogFilter) + 关注 B cross-shard P0 + 等 zhulong/A 裁定三假-distinct 口径.)
> **轮(r1161-WAITING-DETAIL) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1162，2026-11-25）。**[摘要: Lite-500-fix 第89轮 WAITING 行明细 DrcPatternReportComposer-001 + DrcWaiveDeckGen-001 完整 L0-L5 验证明细, 原文见 archive]


> **轮(r1149-WAITING-DETAIL) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1150，2026-11-25）。**[摘要: r1149 第77轮 WAITING 行明细 ChkSaveHistDedup-001 + RsCalcShortDiag-001 完整 L0-L5 验证明细, 原文见 archive]
> **轮(r1147-WAITING-DETAIL) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1148，2026-11-25）。**[摘要: r1147 第75轮 WAITING 行明细 RTextChkPlan-001 + SchHierDescentReport-001 完整 L0-L5 验证明细, 原文见 archive]
> **轮(r1010-r1077 及更早, 共 143 条归档指针) 已批量搬迁至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1135，2026-11-25）。**[摘要: 各轮 0-case/1-case judge-contract-fix / spot-check / Lite-fix re-verify 摘要, 原文见 archive]
> **轮(r1096-r1113) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1097-r1114，2026-11-25）。**[摘要: Lite-500-fix 第24-41轮 · 0-fix defensive monitoring + L3-distinctness scan · r1104 6 条假绿→真绿 (3 root shim + EncloseSide1PatternGen runner) · r1107 1 P1 闭合 DrcPcellBatchConvert-v2 · r1113 1 L3-verify hardening DRCHierLossAudit · r1115 2 P1 caught+fixed ERCFilter/FindCircuitByPath · 多轮 2-case fresh spot-check REF PASS+neg all-FAIL-distinct · cross_shard 逐步 RESOLVED · 详见 ARCHIVE 各轮]









> **轮(r1074) 已收口（2026-11-24）。**[摘要: Lite-500-fix 第2轮 · 9 条 L2 修复 + 13 P0 真因盘点 · 用真实 run_one.sh harness 复验 22 条 P0: 6 条误判(reclassify green, AutoViaSelAnalyze/DrcPatternPkgGen/DummyHeaderQaResolver/RNodePlan/RTextChkPlan/SchHierDescentReport ref PASS) + 3 条修复(DrcPatternReportComposer solution.py→drc_pattern_report.py 重命名匹配 prompt/check + PGAssemblyLVS 建 reference_submit.zip 含 plan_gen.py+plan_A.json + DummyTargetLayerCmp check.py hidden-B/A 输入路径鲁棒解析 hidden/ 子目录+绝对路径) → 9/9 ref PASS + DrcPatternReportComposer negselftest REF PASS+4neg FAIL · 13 条 P0 真因: ChkSaveHistDedup ref 解 crash on B / DummyDeck zip 缺 report_A.json+asset_a 路径 / DummyMeas+GDSBump2 skipper GUI(L4) / GenReleaseNoteMerge+RscalcHandoffDocGen+SyncBatchArchivePlan 无 ASSETS_SRC / LefPostprocessFix hidden/inputs_B 子目录 / LibCellList prompt(gen_lib_cell.py)vscheck(gen_lib_cell_list.py) 名不符 / RsCalcShortDiag assets/CASE/artifacts 子目录被 harness 压平 / SchNetPrefixHilightGen hidden B 路径 / StrongARMComp assets/CASE/inputs 子目录+plan_A.json / VirtuosoLaunchRecipeGen 无 ref 解 · green 90→99 / p0_fixed 22→13 · 体积 MEMORY ~30.5KB · 下一轮: 继续修 13 P0(优先 LibCellList 名不符+LefPostprocessFix/SchNetPrefixHilightGen 路径修+3 条无 ASSETS_SRC 调查), 补 P1 23 条 <3 neg]
> r1075 见上 (Lite-500-fix 第3轮: 7 条 P0→green)










































> > **轮(r1017) 已归档至 MEMORY_C_archive.md（归档批次 r1020，2026-11-23）。**[摘要: see archive]
> > **轮(r1016) 已归档至 MEMORY_C_archive.md（归档批次 r1020，2026-11-23）。**[摘要: see archive]

> > **轮(r1013) 已归档至 MEMORY_C_archive.md（归档批次 r1020，2026-11-23）。**[摘要: see archive]

> > **轮(r1012) 已归档至 MEMORY_C_archive.md（归档批次 r1020，2026-11-23）。**[摘要: see archive]

































































> 轮(887) 已归档至 MEMORY_C_archive.md（归档批次 r888，2026-11-21）。[摘要: 1 new case 6j856 · physical_verify + 档 B reframe StarRC RCC 存储生命周期分析器 StarRcRccStorageLifecycle-001 落库 · k=16 · ref PASS 16/16 + 5 neg FAIL distinct + §4.9(a)(b)(c) + roundtrip sha256 4c128b66 ✓ · C.jsonl 561→562 · discuss mandatory r887 清付(r886 顺延) 3 观点回应 D r1033]

> 轮(886) 已归档至 MEMORY_C_archive.md（归档批次 r887 第二轮，2026-11-21）。[摘要: 0-case · 🚨 cross-shard collision blocker (33zw1 已被 shard D 建为 NetPathHL-001) → 全量回滚 C.jsonl 562→561；fresh C-domain triage 7ypz6/0dml6/1s79t/6f9zc 均非 C-domain；discuss mandatory r886 顺延 r887；33zw1 collision 教训：选料前必先 `grep <sid> trace_ledger_{A,B,C,D}.tsv` 跨 shard 去重]

> 轮(885) 已归档至 MEMORY_C_archive.md（归档批次 r887 第二轮，2026-11-21）。[摘要: 1 new case c9l2c · pg_layout + 档 B reframe dont_touch cell audit 静态解析器 DontTouchCellAudit-001 落库 · k=15 · ref PASS + 3 neg FAIL distinct · roundtrip sha256 39ba238e ✓ · C 域 pg_layout dont_touch 路径审计 reframe 子型首例]

> r884 及更早共 85 轮已归档至 MEMORY_C_archive.md（归档批次 r807-r884, 2026-11-19~21）。详情见归档。各轮摘要可在 archive 文件 grep 查询。

r874-superseded: (r874 1-case dbl7u · StarRcCcoDupDirFix-001 physical_verify 档 B reframe k=15 落库 · starRC cco 耦合电容提取脚本重复目录修复 fixture-driven judge · 15 teeth(a-o) · 自验 ref solve.py PASS 15/15 + 4 neg FAIL distinct(a/f/c/e) + §4.9 三假全 FAIL · C.jsonl 554→555 · build_jsonl.py --shard C 正规建 · roundtrip jsonl==disk check.py sha16 a5e339e95a3fa750 ✓ · JUDGE-tree 独立 dir PASS · 与 SpfLayerCoupleCapAnalyze/LvsSvdbRepDirStat 正交

> r871 (1-case snapshot superseded by r872 above · LvsPinCaseMismatchDiag-001 · 详情见下方 r871 流水行)
> r870 (1-case snapshot superseded by r871 above · GdsDirCmpDeepDive-001 · 详情见下方 r870 流水行)

> 历史 r757-r805 已归档至 MEMORY_C_archive.md（归档批次 r809 (2026-11-19) 归入 r804+r805；归档批次 r807 (2026-11-19) 归入 r802+r803；归档批次 r806 (2026-11-19) 归入 r801；归档批次 r805 (2026-11-19) 归入 r799；归档批次 r801 (2026-11-19) 归入 r794；前批 r797 (2026-11-19) 归入 r789-r793；前批 r796 归 r787+r788；前批 r792 归 r785+r786；前批 r790 归 r783；前批 r789 归 r781；前批 r788 归 r780+r782；前批 r783 归 r777；前批 r782 归 r776；前批 r781 归 r774+r775；前批 r780 归 r770；前批 r779 归 r773；前批 r778 归 r771+r772；前批 r771 归 r762-r766；前批 r765 归 r758-r761；再前批 r761 归 r757）。本文件保留最近 4 轮（r804-r807；r806 双 case 2 行；下轮 r808 若超 32KB 归档 r804）。


