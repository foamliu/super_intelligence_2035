WAITING: 0
LIVE: B review=126/126 · REQ=29(done 29) · OPT=19(concluded 19/19, 0 reformed) · NA=76 · L2.live 0→29 · 收口ready(待A汇总, 不设等待§1.1)
→ r1331 Lite-500 live-eval 收口轮(只读结账): B shard 三项收口判据全满足(REQ 29/29 reformed §5全绿 + OPT 19/19 concluded + NA 76/76 有依据 + cross_shard 2 走原流程). 零 check.py/cases/judge_layers/live_eval_changes.tsv 改动(REQ 改造 r1330 已全落盘). 全量对账 live_eval_review_B.tsv 126 行: verdict REQ(done)27+REQ1+DONE1=29/OPT19/NA76/cross2, 全部 live_reason 填满, REQ+OPT 全部 check_live 填满, NA 全部 reason 填满. OPT 19 结论分两类: Type B 11条(候选跑 PROVIDED deck, Q2不成立, mock==real) + faithful-physics-solver/syntax-validator 8条(mock 非 GT-replay, bit-exact real 或同 conclude garbage, 零物理增益). 与旧P4差异: 旧P4 T1=0/T2=1/T3=129 关键词扫, 本轮 REQ29/OPT19/NA76 桩体检+实证, 6条 R1 generic REQ boilerplate 误分类清零(r1290/r1302/r1303/r1315/r1325/r1326 降 REQ→OPT). 报 A 汇总: live_eval_changes.tsv B 29行(jl [L0,L1]→[L0,L1,L2.live], commit 范围 r1294-r1330, HEAD=924a14db4). 详见 designflow/contract_reform_B.md「Live-eval 收口(r1331)」节. DEBT:0. WAITING:0(不设等待§1.1, 随时可改判分只需登记).
→ r1330 已归档（11-27 r1330 Lite-500 live-eval R3 改造#29(末条REQ收口): SlicerFbTimeOpt-001 hspice-mock GT-replay-by-.param-signature Type A; 详见 designflow/contract_reform_B.md「r1330」节 / designflow/live_eval_changes.tsv / git 历史）
→ r1329 已归档（11-27 r1329 Lite-500 live-eval R3 改造: SpiceTbGen-001 hspice-mock deck-driven RANGE-SYNTHESIZER Type A; 详见 designflow/contract_reform_B.md「R2/R3 改造进度」节 / designflow/live_eval_changes.tsv / git 历史）
→ r1328 已归档（11-27 r1328 Lite-500 live-eval R3 改造: StdLibCharTmpl-001 hspice-mock deck-driven GT-replay-by-corner-signature Type A; 详见 designflow/contract_reform_B.md「R2/R3 改造进度」节 / designflow/live_eval_changes.tsv / git 历史）
→ r1327 已归档（11-27 r1327 Lite-500 live-eval R2 桩体检#6 只读: 3 条未改造 REQ(SlicerFbTimeOpt/SpiceTbGen/StdLibCharTmpl) full-mock-body 确认 REQ, 误分类悬念证伪; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1326 已归档（11-27 r1326 Lite-500 live-eval R2 桩体检#5 只读: VlshftParamOpt-001 DOWNGRADE REQ→OPT; 详见 designflow/contract_reform_B.md / git 历史）
→ r1325 已归档（11-27 r1325 Lite-500 live-eval R2 桩体检#4 只读: Vcc2scActDeckGen-001 DOWNGRADE REQ→OPT; 详见 designflow/contract_reform_B.md / git 历史）
→ r1324 已归档（11-27 r1324 Lite-500 live-eval R2 改造#26: FineSimWorkflowRunner-001 finesim-mock GT-replay-by-measure-name-tokens Type A; 详见 designflow/contract_reform_B.md / live_eval_changes.tsv / git 历史）
→ r1323 已归档（11-27 r1323 Lite-500 live-eval R2 改造#25: Vcc2scTranGen-001 hspice-mock GT-replay-by-signature Type A; 详见 designflow/contract_reform_B.md / live_eval_changes.tsv / git 历史）
→ r1322 已归档（11-27 r1322 Lite-500 live-eval R2 改造#24: FineSimModelScopeFix-001 finesim-mock GT-replay-by-vdd Type A; 详见 designflow/contract_reform_B.md / live_eval_changes.tsv / git 历史）

→ r1321 已归档（11-27 r1321 Lite-500 live-eval R2 改造#23: BistOscRccReorder-001 finesim-mock GT-replay-by-signature Type A; 详见 designflow/contract_reform_B.md / live_eval_changes.tsv / git 历史）
→ r1320 已归档（11-27 r1320 Lite-500 live-eval R2 改造: StrongarmFomSweep-001 hspice-mock deck-driven GT-replay-by-signature Type A; 详见 designflow/contract_reform_B.md「R2 改造进度」节 / designflow/live_eval_changes.tsv / git 历史）
→ r1319 已归档（11-27 r1319 Lite-500 live-eval R2 改造: CmlPvtAcReport-001 hspice-mock deck-driven GT-replay-by-signature Type A; 详见 designflow/contract_reform_B.md「R2 改造进度」节 / designflow/live_eval_changes.tsv / git 历史）
→ r1318 已归档（11-27 r1318 Lite-500 live-eval R2 改造: PorCapSweep-001 hspice-mock deck-driven GT-replay-by-signature Type A; 详见 designflow/contract_reform_B.md「R2 改造进度」节 / designflow/live_eval_changes.tsv / git 历史）
→ r1317 已归档（11-27 r1317 Lite-500 live-eval R2 改造: DelaySigma-001 hspice-mock deck-driven GT-replay-by-signature Type A; 详见 designflow/contract_reform_B.md「R2 改造进度」节 / designflow/live_eval_changes.tsv / git 历史）
→ r1316 已归档（11-27 r1316 Lite-500 live-eval R2 改造: VwlpRefDeckSet-001 hspice-mock deck-driven GT-replay-by-signature Type A; 详见 designflow/contract_reform_B.md「R2 改造进度」节 / designflow/live_eval_changes.tsv / git 历史）
→ r1314 已归档（11-27 r1314 Lite-500 live-eval R2 改造: OpampACSpec-001 hspice-mock deck-driven GT-replay-by-signature Type A; 详见 designflow/contract_reform_B.md「R2 改造进度」节 / designflow/live_eval_changes.tsv / git 历史）
→ r1312 已归档（11-27 r1312 Lite-500 live-eval R2 改造: CtleAcChar-001 hspice-mock deck-driven GT-replay-by-signature Type A; 详见 designflow/contract_reform_B.md「R2 改造进度」节 / designflow/live_eval_changes.tsv / git 历史）
→ r1311 已归档（11-27 r1311 Lite-500 live-eval R2 改造: PFDdeadZone-001 hspice-mock deck-driven GT-replay-by-signature Type A; 详见 designflow/contract_reform_B.md「R2 改造进度」节 / designflow/live_eval_changes.tsv / git 历史）
→ r1310 已归档（11-27 r1310 Lite-500 live-eval R2 改造: InvPVTchar-001 hspice-mock deck-driven GT-replay-by-signature Type A; 详见 designflow/contract_reform_B.md「R2 改造进度」节 / designflow/live_eval_changes.tsv / git 历史）
CONTRACT: P1=0/12 · P2=29 L2.live (CdlBulkSanitize/InvTripDelay/AOI21ArcChar/AlterDeckSplit/SpiceSim/DffSetupHoldChar/GrDecPwrVerifTb/GmidLut/VcoKvcoChar/PVTalterChar/TaperBufOpt/SramSNM/InvPVTchar/PFDdeadZone/CtleAcChar/DelayChainEdgeMeas/OpampACSpec/VwlpRefDeckSet/DelaySigma/PorCapSweep/CmlPvtAcReport/StrongarmFomSweep/BistOscRccReorder/Vcc2scTranGen/FineSimWorkflowRunner/StdLibCharTmpl/SpiceTbGen/SlicerFbTimeOpt, r1294-r1300/r1304-r1308/r1310-r1314/r1316-r1321/r1323/r1324/r1328/r1329/r1330) · P3=600/600 judge_layers ✅ · P4=130/130 ✅
→ r1308 已归档（11-27 r1308 Lite-500 live-eval R2 改造: SramSNM-001 hspice-mock deck-driven GT-replay-by-signature Type A; 详见 designflow/contract_reform_B.md「R2 改造进度」节 / designflow/live_eval_changes.tsv / git 历史）
→ r1307 已归档（11-27 r1307 Lite-500 live-eval R2 第11条改造: TaperBufOpt-001 hspice-mock deck-driven GT-replay-by-signature Type A; 详见 contract_reform_B.md「R2 改造进度」节 / git 历史）
→ r1306 已归档（11-27 r1306 Lite-500 live-eval R2 第10条改造: PVTalterChar-001 hspice-mock deck-driven GT-replay-by-signature Type A; 详见 contract_reform_B.md「R2 改造进度」节 / git 历史）
→ r1305 已归档（11-27 r1305 Lite-500 live-eval R2 第9条改造: VcoKvcoChar-001 hspice-mock deck-driven GT-replay Type A; 详见 contract_reform_B.md「R2 改造进度」节 / git 历史）
→ r1303 已归档（11-27 r1303 Lite-500 live-eval R1 桩体检再复核#3 只读: 三分类清零, verdict REQ 36→33/OPT 12→15; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1300 已归档（11-26 r1300 Lite-500 live-eval R2 第7条改造: GrDecPwrVerifTb-001 hspice-mock deck-driven Type A; 详见 contract_reform_B.md「R2 改造进度」节 / git 历史）
→ r1292 已归档（11-26 r1292 Lite-500 live-eval R1 borderline empirical cheat 验证(只读): CdlBulkSanitize-001 REQ 确认(Type A) + MinpulseRewriteRun-001 降 REQ->OPT; verdict REQ 41->40, OPT 7->8; 详见 contract_reform_B.md / git 历史）
→ r1290 已归档（11-26 r1290 Lite-500 live-eval R1 桩体检实证轮(只读): 把 r1289 Q2=会判过 从 grep 推断升级为逐条实证. AOI21ArcChar-001(Type A) 实证: cheat harness(正确 .param 签名+stimulus, GARBAGE 网表) → 13/13 PASS 假阳 ⇒ REQ 稳固. CTLESpec-001(Type B) 过度分类→OPT: 候选跑给定 tb, 不造网表/不能 hardcode GT, 桩==真工具, judge 有牙(cond l cross-input). 关键区分 Type A(候选自建 deck, Q2 可骗) vs Type B(候选跑给定 deck, Q2 N/A). verdict: REQ 47→46, OPT 1→2. r1291 已完成全量 A/B 复核(见上 LIVE 行)）
→ r1288 已归档（11-26 r1288 Lite-500 live-eval R1 只读审视: 见上 LIVE 行 + designflow/live_eval_review_B.tsv + designflow/contract_reform_B.md「Live-eval 审视」节. R1 产出: 126/126 verdict 填满(REQ47/NA77/cross2) + REQ清单 + 与旧P4差异台账. 冻结窗口未解冻, 无落盘判分改动. 下一轮: 等解冻后 R2 改造 hspice-mock/finesim-mock 家族 ≤3条/轮）
→ r1287 已归档（11-26 r1287 第二轮回归抽检 4 mixed case re-verify; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1286 已归档（11-26 r1286 第二轮回归抽检 4 clean case re-verify; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1285 已归档（详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1277 已归档（详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1276 已归档（11-26 r1276 第二轮回归抽检 4 mixed case(DeckConsistencyCheck/DelayChainEdgeMeas/DelayCornerIdent/DelaySigma): 2 clean + 2 LATENT §4.9-b/c fix; 累计 2nd-pass 32/130; 详见 daily_B_2026-11-26_r1276.md / git 历史）
→ r1275 已归档（11-26 r1275 第二轮回归抽检 4 mixed case(CtleAcChar/DblTailSlicerDeckGen/DcaStimSweepGen/Ddr6RptCmdExtract): 3 clean + 1 LATENT §4.9-b fix; 累计 2nd-pass 28/130; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1274 已归档（11-26 r1274 第二轮回归抽检 4 mixed case(CmlSweepHeadroomDiag/Coord3DProj/CosimRunBlockOpt/CTLEAC) 4/4 NO regression; 累计 2nd-pass 24/130; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1273 已归档（11-26 r1273 第二轮回归抽检 4 clean case(ClampPwrStateExtract/CmlBwExtensionHandbook/CmlDivOscDiag/CmlPvtAcReport) 4/4 NO regression; 累计 2nd-pass 20/130; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1272 已归档（11-26 r1272 第二轮回归抽检 4 clean case(BridgeCfgDiag/ButterflyCurve/CabufPvtDatAudit/CdlBulkSanitize) 4/4 NO regression; 累计 2nd-pass 16/130; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1271 已归档（11-26 r1271 第二轮回归抽检 4 clean case(AOI21ArcChar/AlterDeckSplit/BisecMt0SmCalc/BistOscRccReorder) 4/4 NO regression; 累计 2nd-pass 12/130; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1270 已归档（11-26 r1270 第二轮回归抽检 4 LATENT-fixed case(CTLETranDeck/GaaFetDeckAugment/MR7PsdScopeAnalyze/SpfAutosimSetup) 4/4 NO regression; 累计 2nd-pass 8/130; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1269 已归档（11-26 r1269 第二轮回归抽检 4 LATENT-fixed case(CosimRunBlockOpt/PUvddSweep/OtaAcReport/SubcktExtract) 4/4 NO regression; 累计 2nd-pass 4/130; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1268 已归档（11-26 r1268 轮转抽检 3 条 fresh case(TrtfMeasDeckGen/WtmFileReview/XrunLogErrDiag): 1 clean + 2 LATENT §4.9 修复; 130/130 Lite-B 全覆盖; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1267 已归档（11-26 r1267 轮转抽检 5 条 re-verify: 4 clean + 1 LATENT §4.9-c SpfAutosimSetup 加 core_deleted neg; 累计抽检 69/130; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1266 已归档（11-26 r1266 轮转抽检 5 条 re-verify: 3 clean + 2 LATENT §4.9 修复(GaaFetDeckAugment §4.9-trio print_only 重写 / MR7PsdScopeAnalyze §4.9 missing-selftest 新建); 累计抽检 54/130; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1265 已归档（11-26 r1265 轮转抽检 5 条 re-verify: 4 clean + 1 LATENT §4.9-c CTLETranDeck 加 core_deleted neg; 累计抽检 64/130; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1264 已归档（11-26 r1264 P4 实跑适合性分析轮(只读): 全量 130 Lite-B 本质问复核 T1=0/T2=1(LisMeasExtract)/T3=129, 产出 designflow/contract_reform_B.md; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1263 已归档（11-26 r1263 轮转抽检 5 条 re-verify: 1 clean + 4 LATENT §4.9 fixes; 累计抽检 59/130; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1261 已归档（11-26 r1261 候选池二轮 triage: 3 high-mc parked 全 asset-dependent 不可移植, viable fresh trace 耗尽, 止损; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1258 已归档（11-26 r1258 契约改造 P3 轮: B 600 case 批量加 judge_layers=["L0","L1"], P3=600/600 ✅; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
LITE_FIX: B=130/130 · P0 余 0 · r1268 抽检最后 3 条 fresh(TrtfMeasDeckGen/WtmFileReview/XrunLogErrDiag): 1 clean + 2 LATENT §4.9 修复(TrtfMeasDeckGen §4.9-b print→f / WtmFileReview §4.9-a empty→c), check.py 两 case UNCHANGED 仅 negative/ 改 · 清单 md5=f7816ef4137353904e40a1a3b01fb3ae(500行,eval/cases_lite.txt) · id归一化:剥 EDA-Eval-DesignFlow- 前缀 · 本shard Lite=130 · green_verified=130/130 · 全500进度: green+gv=507/507 全绿(11-26 zhulong 3-run 验收中) · 累计抽检: 130/130 Lite-B case 均在 daily_B 出现过(r1268 后全覆盖; 含 r1253-r1268 各轮) · P3 DEBT cleared
→ r1257 已归档（11-26 r1257 轮转抽检 5 条 re-verify: 3 clean + 2 LATENT §4.9-trio 修复; 累计抽检 49/130; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1256 已归档（11-26 r1256 轮转抽检 5 条 re-verify: 4 clean + 1 LATENT(OtaAcReport §4.9-trio matplotlib-fallback+core_deleted neg 修复); 累计抽检 44/130; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1255 已归档（11-26 r1255 轮转抽检 5 条 01:50-batch fresh case 全 clean(StrongarmBaselineAnalyze/GrDecPwrVerifTb/TzqlatLocate/TrimMarginSpec/TbSpiceMeasureAudit)；详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1254 已归档（11-26 r1254 轮转抽检 re-verify 5 条 fresh case(1 clean+4 LATENT §4.9); 累计抽检 34/130; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1253 已归档（11-26 r1253 轮转抽检 re-verify 3 条 01:50-batch fresh case 全发现 LATENT 缺陷并修复: NetlistCmp-001 L5 test-field desync sync / SpiceMeasInjector-001 L3 5 negs distinct + sync / FinesimMatrixrunAgent-001 L3 5 negs + selftest path fix + sync; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1252 已归档（11-26 r1252 holding 轮转抽检 2 条 re-verify: CosimRunBlockOpt LATENT neg-distinct 修复 + LvLvioSweep clean; 累计 26/130; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1250 已归档（11-26 r1250 holding Lite spot re-verify BridgeCfgDiag+CmlSweepHeadroomDiag 全绿; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1249 已归档（11-26 r1249 holding Lite spot re-verify CmlDivOscDiag+CTLETranDeck 全绿; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1248 已归档（11-26 r1248 holding Lite spot re-verify CabufPvtDatAudit+LisMeasExtract 全绿; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1247 已归档（11-26 r1247 TSV-sync 轮: 修 lite_health_B.tsv 6 条 stale green_verified 行; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1245 已归档（11-26 r1245 holding Lite spot re-verify FineSimWorkflowRunner+MonteCarloDeckGen 全绿 + MonteCarloDeckGen L5 test-field sync; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1243 已归档（11-26 r1243 holding Lite spot re-verify CdlBulkSanitize+CtleAcChar 全绿; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1242 已归档（11-26 r1242 holding Lite spot re-verify AlterDeckSplit+OpampACSpec 全绿; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1240 已归档（11-26 r1240 holding Lite spot re-verify BistOscRccReorder+TxRonSize 全绿; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1239 已归档（11-26 r1239 holding Lite spot re-verify Mt0Reorg+InvTripDelay 全绿; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1238 已归档（11-26 r1238 Lite-fix 收口 AOI21ArcChar+ButterflyCurve green->green_verified -> B 130/130 全 green_verified; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1237 已归档（11-26 r1237 Lite-fix P3 Mt0Reorg-001 latent bare-except bug cleared -> B 130/130 全绿; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1236 已归档（11-26 r1236 Lite-fix 修 2 条 Sp2tVerilogaSwitch+InvTripDelay -> B 130/130 全绿; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1235 已归档（11-26 r1235 Lite-fix 修 4 条 NO_REF建refzip -> green_verified; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1234 已归档（11-26 r1234 Lite-fix 修 1 条 DelayCornerIdent-001 NO_REF建refzip→green_verified; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1233 已归档（11-26 r1233 Lite-fix 修 8 条 -> green_verified (2 P0 path-bug + 2 NO_REF + 4 runtime-verify); 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1232 已归档（11-26 r1232 Lite-fix P1 修 2 条 McVthSpVariantGen+Mt0Reorg -> green_verified; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1231 已归档（11-26 r1231 Lite-fix P0 修 1 条 BistOscRccReorder-001 finesim-mock+hidden-B+refzip-rebuild -> green_verified; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1230 已归档（11-26 r1230 Lite-fix P0 AOI21ArcChar-001 hspice-mock; 详见 git 历史）
→ r1229 已归档（11-26 r1229 Lite-fix P0 ButterflyCurve-001 hspice-mock→green_verified；详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1228 已归档（11-26 r1228 Lite-fix P0 PVTalterChar-001 hspice-mock→green_verified；详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1227 已归档（11-25 r1227 Lite-fix P0 PlatMosThinIdsatIoffSweep-001 hspice-mock→green_verified；详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1225 已归档（11-25 r1225 Lite-fix P0 修 2 条 DQSEHFlagNoEffectDiag+TxRonSize→green_verified；详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1224 已归档（11-25 r1224 Lite-fix P0 OpampACSpec-001 hspice-mock; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1223 已归档（11-25 r1223 Lite-fix P0 VwlpRefDeckSet-001 hspice-mock self-contained + neg redesign -> green_verified；详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1222 已归档（详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1221 已归档（11-25 r1221 Lite-fix P0 修 1 条 sim-dep+ref-bug -> green_verified: StimPWL-001 hspice-mock self-contained + portable ref + neg redesign; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1220 已归档（11-25 r1220 Lite-fix P0 修 1 条 sim-dep -> green_verified: SimExpl-001 finesim-mock self-contained; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1219 已归档（11-25 r1219 Lite-fix P0 修 1 条 sim-dep -> green_verified: SramSNM-001 hspice-mock; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1218 已归档（11-25 r1218 Lite-fix P0 修 1 条 sim-dep -> green_verified: DffSetupHoldChar-001 hspice-mock; 详见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md / git 历史）
→ r1217 已归档（r1217 Lite-fix 详见 git 历史 / ARCHIVE_OPERATOR_DESIGNFLOW_B.md）
→ r1216 已归档（r1216 Lite-fix 详见 git 历史 / ARCHIVE_OPERATOR_DESIGNFLOW_B.md）

