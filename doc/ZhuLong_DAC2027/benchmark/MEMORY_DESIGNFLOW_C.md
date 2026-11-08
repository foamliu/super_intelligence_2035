WAITING: 0
SHARD: C (physical_layout)
DOMAINS: layout_aether, layout_virtuoso, pg_layout, physical_verify
round: 258（r258 已交付 ConnChkSummaryGen-001；r257 GloryRcFlowSetup-001；r256 LdrSvrfRuleGen-001；r255 CmMaOpTableGen-001；r254 EmyCdlNetlistExtract-001；r253 PinListPortOrderExtract-001；r252 LayStructExtract-001；r251 LvsAmbiguityDiag-001；r250 HcellPairGen-001；r249 选料筛选轮·0 case；r248 SpfRcAggregateAudit-001；r246 LefFromPinList-001；r245 RectAspectRuleCheck-001；r243 VssPunchRuleGen-001；r242 SaqpIntAngleEqSplit-001；r241 SvrfPvrsRuleTranslate-001；r240 WlAdjacentPairParse-001；r239 DrcRuleTimeRank-001；r238 LayoutFloorplanGen-001；r237 DrcLogTeardownReport-001；r236 SkillBindkeyFlattenMakeCell-001；r233-r216 已交付 230 case）
📊 trace 覆盖率：248/1511=16.4%（r258 +1 case；ledger 452:case 248·deepread 0·parked 204·claimed 0；jsonl C 248 行；mc30 池 target 1511(sessions=5822 mc30=1511 mc100=1291 mc300=252)；layout_aether 61·layout_virtuoso 55·pg_layout 34·physical_verify 94）
🎯 通过率: shard C 累计 248 case 已落 jsonl（pi/cline 实跑数见 cline_eval_status.jsonl，B 档目标 20–30%）
🧾 断言: k_rationale=k_check ✓（248/248 达标；r258 ConnChkSummaryGen-001 k=16 a-p；r257 GloryRcFlowSetup-001 k=14 a-n；r256 LdrSvrfRuleGen-001 k=14 a-n；r255 CmMaOpTableGen-001 k=17 a-q；r254 EmyCdlNetlistExtract-001 k=16 a-p；r253 PinListPortOrderExtract-001 k=15 a-o；r252 LayStructExtract-001 k=18 a-r；r251 LvsAmbiguityDiag-001 k=16 a-p；r250 HcellPairGen-001 k=18 a-r）
📦 体积：TASK≈26KB / TASK_C≈27KB / MEMORY_C≈31KB / MEMORY_C_archive≈90KB
🛠 DEBT: 0（r258 ConnChkSummaryGen-001 已交付，无遗留）
- research 日报 2026-11-08 参考：designflow 建议提「资源预算(CPU/内存/wall-clock/output token)作为测量规格 + 持续校验工作流(缺陷类别 env/instruction/verifier + 修复前后 pass-rate)」纳入判分口径；本轮未改判分（无相关条目需本轮落地），存疑待后续评估。已记录：rewrite_queue.tsv 现有 reason/status 列已近似「缺陷类别+修复动作」口径，资源轴待后续 cline_eval 报告补 wall-clock/token 列。
- **轮(258) 已交付 EDA-Eval-DesignFlow-ConnChkSummaryGen-001（physical_verify, B-synthesized, L1, k=16 a-p）✓** —— trace=1793088988568_84qb3（xxchen@hfeg0pkn002/10.129.2.11, mc=334, kw=drc675+calibre191+.gds144+cmos123；**NEW user** xxchen 首个 case；agent=lead, 263 msgs）。**选料**：sel_C_r258（.75 summary.tsv → 935 dedup mc≥30+tool-kw → 排除 ledger 445 sids + 43 SAT users → 212 fresh，layout-affinity score=ΣLAY+calibre/virtuoso/lef/def/gds/oasis −0.6×ΣSIM）。**关键发现**：cline sessions 目录为 per-sid 子目录（`sessions/<sid>/<sid>.messages.json`），非平铺——先前平铺路径 fetch 全空，nested 路径才命中（84qb3 911KB）。**84qb3(xxchen 167calibre)→organic physical_verify seed**。**用户真实意图(U#1 idx25, 提出需求, 未给根因)**：「允许指定多个 bottomLayer: config_multi bottomLayer, ["MT3","M0A"] connectOPC011, [...] 另外 sum.rep 中的 path，每条 path 单独写一行。」(U#2 idx53「shields 增 NBP->TCP + shields 每条单独占一行」)。**grounding**：scp 真实工具源码到 .75 workdir——`config_multi`(1930B, connectivity_multi 5 block)、`sum.rep`(2435B, 5 [run_N] 块: path(s)/shields 每条独立成行续行 17 空格对齐、sameNet/diffNet `[OK|HAS ERRORS]`、status)、`graph.py`(normalize_connectivity: >3 层边拆 [S,V,Ti]+全有序对 shields；find_all_paths: DFS 含 via for 3-layer, 不含 via for 2-layer)、`summary.py`(format_report: 头 5 行 72=、每 run 块、尾；_mode_line verdict)。**为何 B 档重定义为离线报告生成器**：真实 drcConnect 依赖用户私有 GDS/Calibre/run 目录+gdspy，e0031982 在 pyAether sandbox 不可访问；但 trace grounding 价值在「config→连通图遍历→sum.rep 报告格式」规范提取。故重定义为 `conn_summary.py <config.json> <runs_meta.json> -o <sum.rep>`(stdlib only)。**DISTINCT**：首次 ground on DRC 连通性图遍历+sum.rep 结构化报告生成，非规则/诊断/审计/编排。**case 结构**：assets/A(config_A 4 block + runs_meta_A + prompt + task_brief)+hidden(config_B 5 block 含 DRC ERROR status; config_B2 3 block 含 missing status; hidden_manifest)+reference(golden_solution.py + golden_A/B/B2.sum.rep + check.py 16条件 a-p + 6 negative + negative_selftest.py + reference_submit.zip)。**自验**：golden 16/16 PASS ✓；negative 6/6 全 FAIL ✓(empty_shell→a, print_expected→f/i/p, hardcoded_A→i/m/n/o/p, core_deleted→i, stub_no_shields→j/k, stub_comma_join→h/l)；§4.9 三假全 FAIL ✓；test==disk check.py 13144B ✓；3-seed sha256 确定 ✓。**断言闸门**：k_rationale=16=k_check(a-p)≥8 ✓，已落 jsonl_C(248 行)+ledger mark case(248/1511=16.4%)。深读=trace_deepreads/r258_84qb3_conn_chk_summary_gen.md。**DEBT: 0**。
- **轮(257) 已交付 EDA-Eval-DesignFlow-GloryRcFlowSetup-001（physical_verify, B-synthesized, L1, k=14 a-n）✓** —— trace=1790047784806_lsc1e（simplec@hfeg0pkn002/10.129.2.11, mc=143, **NEW user** simplec 首个 case；agent=lead, 250 msgs）。**选料**：sel_C_r257.py(内置 449 ledger sids 排除 + SAT users, mc 30-400, layout-affinity score=ΣLAY+lef/def/gds/oasis−0.6×ΣSIM)在 .75 上跑 summary.tsv → fresh cand。探针 non-seed parked：s8p63/gm17v/68dpw/sutmr(env-recon/skill-activation)、wjwc4/gwph0(how-to)、cwhbi(code-comprehension「DFM PROPERTY OPC011 转 html」)、i9qdi/necxj/x0ib4(PEX env-recon)、30a1n(skill-activation)、ext1v/idt7t/jgnwe(sim/copied-script)。**lsc1e(simplec mc143 gxrc+calibre+drc+lvs)**→**organic physical_verify seed**。**用户真实意图(U#0 idx=0, 提出需求, 未给根因)**：「帮我跑一下glory RC flow」(U#2「再跑一次flow 和上次的配置一样」/U#3「我已经修改了脚本，重新跑一下」)。**grounding**：agent read_files 扫 user 项目 `run_gxrc.sh`/`gxrc_cci_cmd` 模板/CCI_DB 目录结构→抽象「case-list 驱动批量 setup + gxrc_cci_cmd 模板替换 + CCI_DB 完整性校验 + 缺陷分类」flow 编排契约。**为何 B 档重定义为离线 flow 编排器**：真实 GloryEX/LSF/license/CCI_DB 在 .75 对 e0031982 不可访问(用户私有项目 + gxrc 二进制 + bsub 队列)，无法取真实 case-list/CCI_DB 作 A 输入；但 trace 的 grounding 价值在「flow 编排规范提取」——agent 把 gxrc_cci_cmd 模板替换 + CCI_DB manifest 校验 + ready/missing 分类抽象成可参数化的离线编排契约。故重定义为 `glory_rc_flow_setup.py <flow_config.json> <cci_db_manifest.json> -o <out_dir>`(stdlib only)：解析 flow_config(case_list + gxrc_cmd_template + cci_db_root)→对每 case 校验 CCI_DB manifest(source_dir/devtab/lvs_settings 三件齐→ready；缺任一→missing_source/missing_lvs/incomplete 分类)→按模板生成 `tasks/<case>/{gxrc_cci_cmd,run,query_cmd}` + `setup_manifest.json` + `status_report.json`→stdout 末行 JSON 摘要 `{"total","ready","missing_source","missing_lvs","incomplete"}`。**DISTINCT from 现有 physical_verify 系**：r256 LdrSvrfRuleGen(LDR→SVRF 规则生成, 文本级)/r251 LvsAmbiguityDiag(LVS 歧义诊断)/r250 HcellPairGen(Hcell 配对)/r248 SpfRcAggregateAudit(SPF RC 聚合审计)/r243 VssPunchRuleGen(VSS punch 规则生成)——本 case 是 **flow 编排**级(setup manifest + 任务目录生成 + 缺陷分类)，非规则/诊断/审计；编排对象是 gxrc_cci_cmd 模板替换而非 SVRF/PEX 规则。**自验**：golden 14/14 PASS；5 negatives(empty_shell/print_expected/hardcoded_A/core_deleted/stub_no_parse)ALL-FAIL；§4.9 三 fakes(empty/only-print/core-deleted)all-pass=False；3-run sha256 stable；`test` field byte-equal to disk check.py；assertion gate k_rationale=14=k_check(a-n)≥8 ✓。深读=trace_deepreads/r257_lsc1e_glory_rc_flow_setup.md。**DEBT: 0**。
- **轮(256) 已交付 EDA-Eval-DesignFlow-LdrSvrfRuleGen-001（physical_verify, B-synthesized, L1, k=14 a-n）✓** —— trace=1790154228796_wp6o1（yzwang@hfeg0pkn001/10.129.2.10, mc=174, kw=drc:1031+calibre:189+pex:62+lvs:50；**NEW user** yzwang 首个 case；agent=lead, 62 msgs）。**选料**：sel_C_r256.py(内置 448 ledger sids 排除 + SAT users incl adaml/mwxi/yohannw/hbpeng/e02141/e0023936/e0047527/gurmanli/rayfeng/jason17w/lvyy/zhigangw/pdsong/lynn1y/kevinc/e0047434/miccao/ellawu/e0046913/e0045488/e0016033/e0048306/e0047722/tongni/shaoyou/liwan/m1wang/yqlu/jeoteanl/e0047488/alenxu/johnl/xinqiaoz/zjqiao/e0014566/e0031668/haoyut/lizwen/ziyuny/e0042624/kenwang/e0031982/aocao, mc 30-400, layout-affinity score=ΣLAY+lef/def/gds/oasis−0.6×ΣSIM)在 .75 上跑 summary.tsv → 598 fresh cand。探针 3 条 NEW-user high-lay：wp6o1(yzwang mc174 drc1031+cal189 pex62 lvs50)→**organic physical_verify seed**；cwhbi(xxchen mc156 drc411+lvs159+calibre155+gds31)→code-comprehension「转 md 为 html+解释 DFM PROPERTY OPC011」wrong-task parked；v59v8(e0047695 mc376 virtuoso459+spi323+lef298)→general-tool「写 cdslck 文件查找删除 GUI 脚本」wrong-domain parked。**wp6o1→seed**。**用户真实意图(U#0 idx=0, 提出需求, 未给根因)**：「LDR有一个描述，要求M1的width最小是0.159，请你写出这条rule的DRC查法。」(U#38 idx=38 第二条同型：「VSH_cmp与VSH_cmp的space最小是0.028」)。**grounding**：agent read_files 逐段扫 /home/yzwang/calibreDRC.rule(22533 行)→M1 DRC 段 10211 行起、既有 M1_W_001_00_c/_p width 规则 10223-10232、PG_CMP/AT4_CMP spacing 14004-14050、M1_S_008_00_c 同层间距 EXT 10250-10261→抽象书写规范「VARIABLE  _<rid>_ <val> → <rid> { → @ <desc> [^_<rid>_] → <OP> <LAYER> < _<rid>_ ABUT<90 SINGULAR REGION → }」+ 算子语义 width→INT(内部宽度)/space→EXT(外部间距)。**为何 B 档重定义为参数化生成器**：真实 deck /home/yzwang/calibreDRC.rule 对 e0031982 在 .75 不可访问(用户私有项目)，无法取真实 22533 行 deck 作 A 输入；但 trace 的 grounding 价值在「规范提取」——agent 把既有 deck 写法抽象成格式契约，可参数化生成任意 LDR→SVRF 规则块。故重定义为 `ldr_to_svrf.py <ldr_rules.json>`(stdlib only)：解析 JSON 数组 `[{rule_id,layer,check,value,desc}]`→按 svrf_convention.md 逐块输出 SVRF DRC 规则到 stdout。**DISTINCT from 现有 physical_verify 系**：r241 SvrfPvrsRuleTranslate(SVRF→PVRS 跨语言翻译,方向相反)/r243 VssPunchRuleGen(单一 vss via-punch 规则,结构固定)/r245 RectAspectRuleCheck(分析既有 shape)/r239 DrcRuleTimeRank(排序既有 deck)——本 case 是 LDR 自然语言→参数化 SVRF DRC 规则块**批量生成器**，更纯粹的「规范理解+算子选择」判分。**判分**：14 条断言 a-n(zip合法+含py/编译+stdlib/隐藏B跑exit0+stdout非空/恰5块/VARIABLE值正确/@desc子串/算子匹配check/图层名/变量引用/修饰符ABUT<90 SINGULAR REGION按序/反硬编码B含且不含A/3随机子集+sha256确定性/块顺序/可见A 2块M1 0.159 INT+VSH_CMP 0.028 EXT)；隐藏 B=5 rules(M3 width0.2/VIA1 space0.14/PG width0.18/M2 space0.16/AT4 width0.12)vs A=2 rules，规模/取值/结构均不同。**自验**：ref PASS 14/14✓；3 negatives(naive_stub/always_empty/wrong_op)+3 §4.9 fakes(empty_shell/only_print/ref_core_deleted)全 FAIL✓。**环境**：calibre 在 .75 license 不可用(实测 `calibre -svrf` 报 `Unable to acquire calibrehdrc license` RC=4)，故判分不真跑 calibre，但要求生成器产出文本结构与真实 deck 一致(agent 真实 grounding 自 22533 行 deck，规范可信)。
- 轮(255) 已交付 EDA-Eval-DesignFlow-CmMaOpTableGen-001（physical_verify, B-synthesized, L1）✓ — 详细流水已归档 MEMORY_C_archive.md（归档批次 r258）；trace 见归档
- 轮(254) 已交付 EDA-Eval-DesignFlow-EmyCdlNetlistExtract-001（physical_verify, B-synthesized, L1）✓ — 详细流水已归档 MEMORY_C_archive.md（归档批次 r258）；trace 见归档
- 轮(253) 已交付 EDA-Eval-DesignFlow-PinListPortOrderExtract-001（physical_verify, B-synthesized, L1）✓ — 详细流水已归档 MEMORY_C_archive.md（归档批次 r258）；trace 见归档
- 轮(252) 已交付 EDA-Eval-DesignFlow-LayStructExtract-001（physical_verify, B-synthesized, L1）✓ — 详细流水已归档 MEMORY_C_archive.md（归档批次 r258）；trace 见归档
- 轮(251) 已交付 EDA-Eval-DesignFlow-LvsAmbiguityDiag-001（physical_verify, B-synthesized, L1, k=16 a-p）✓ — 详细流水已归档 MEMORY_C_archive.md（归档批次 r253）；trace 见归档
- 轮(250) 已交付 EDA-Eval-DesignFlow-HcellPairGen-001（physical_verify, B-synthesized, L1, k=18 a-r）✓ — 详细流水已归档 MEMORY_C_archive.md（归档批次 r253）；trace 见归档
- 轮(249) 选料筛选轮 · 0 case · DEBT:1 — 详细流水已归档 MEMORY_C_archive.md（归档批次 r253）；trace 见归档
- 轮(248) 已交付 EDA-Eval-DesignFlow-SpfRcAggregateAudit-001（physical_verify, B-synthesized, L1, k=14 a-n）✓ — 详细流水已归档 MEMORY_C_archive.md（归档批次 r253）；trace 见归档
- **轮(247) 选料筛选轮 · 0 case · DEBT:1** —— 详细流水已归档 MEMORY_C_archive.md（归档批次 r248）；trace 见归档
- 轮(246) 已交付 EDA-Eval-DesignFlow-LefFromPinList-001（pg_layout, B-synthesized, L1, k=19 a-?）✓ — 详细流水已归档 MEMORY_C_archive.md（归档批次 r255）；trace=1790067683167_wo5tr
- 轮(245) 已交付 EDA-Eval-DesignFlow-RectAspectRuleCheck-001（physical_verify, B-synthesized, L1, k=14 a-?）✓ — 详细流水已归档 MEMORY_C_archive.md（归档批次 r255）；trace=1791963569790_794ce
- 轮(243) 已交付 EDA-Eval-DesignFlow-VssPunchRuleGen-001（physical_verify, B-synthesized, L1, k=16 a-?）✓ — 详细流水已归档 MEMORY_C_archive.md（归档批次 r255）；trace=1793776902021_xvnac
- 轮(242) 已交付 EDA-Eval-DesignFlow-SaqpIntAngleEqSplit-001（physical_verify, B-synthesized, L1, k=16 a-?）✓ — 详细流水已归档 MEMORY_C_archive.md（归档批次 r255）；trace=1793607379592_t4gfl
- 轮(241) 已交付 EDA-Eval-DesignFlow-SvrfPvrsRuleTranslate-001（physical_verify, B-synthesized, L2, k=16 a-p）— 详细流水已归档 MEMORY_C_archive.md（归档批次 r242）；trace=1793017242561_zdwid
- 轮(240) 已交付 EDA-Eval-DesignFlow-WlAdjacentPairParse-001（physical_verify, B-synthesized, L1, k=18 a-r）— 详细流水已归档 MEMORY_C_archive.md（归档批次 r242）；trace=1793685353350_ydezg
- 轮(239) 已交付 EDA-Eval-DesignFlow-DrcRuleTimeRank-001（physical_verify, B-synthesized, L2, k=16 a-p）— 详细流水已归档 MEMORY_C_archive.md（归档批次 r242）；trace=1791967362296_kxqt7
- 轮(238) 已交付 EDA-Eval-DesignFlow-LayoutFloorplanGen-001（layout_aether, B-synthesized, L1, k=18 a-r）— 详细流水已归档 MEMORY_C_archive.md（归档批次 r242）；trace=1785899794656_0j59o

- 轮(237) 已交付 EDA-Eval-DesignFlow-DrcLogTeardownReport-001（physical_verify, B-synthesized, L2, k=18 a-r）— 详细流水已归档 MEMORY_C_archive.md（归档批次 r242）；trace=1789699671032_sk6cg

- 轮(236) 已交付 EDA-Eval-DesignFlow-SkillBindkeyFlattenMakeCell-001（layout_virtuoso, B-synthesized, L1, k=18 a-r）— 详细流水已归档 MEMORY_C_archive.md（归档批次 r242）；trace=1790306446486_bl0yj

- 轮(235) 选料筛选轮 · 0 case · DEBT:2 — 详细流水已归档 MEMORY_C_archive.md（归档批次 r242）

- 轮(235) 选料筛选轮 · 0 case · DEBT:2（path bug + 跨 shard 撞库）— 详细流水已归档 MEMORY_C_archive.md（归档批次 r242）

- ⚠️ 轮(234) 选料筛选轮 · 0 case · DEBT:1 — 详细流水已归档 MEMORY_C_archive.md（归档批次 r242）

- 轮(234) 选料筛选轮 · 0 case · DEBT:1（10 候选全 non-seed，scan 陈旧+schematic 枯竭）— 详细流水已归档 MEMORY_C_archive.md（归档批次 r242）

- 轮(233) 已交付 EDA-Eval-DesignFlow-InstM0ShapePinIdentify-001（layout_virtuoso, B-synthesized, L1, k=18 a-r）— 详细流水已归档 MEMORY_C_archive.md（归档批次 r242）；trace=1793605922073_ets0m

- 轮(232) 已交付 EDA-Eval-DesignFlow-SkillM1ShapeDeleteAudit-001（layout_virtuoso, B-synthesized, L1, k=18 a-r）— 详细流水已归档 MEMORY_C_archive.md（归档批次 r242）；trace=1782880367712_jzzsv


- 轮(230) 已交付 EDA-Eval-DesignFlow-VirtuosoStartupDiag-001 — 详细流水已归档 designflow/MEMORY_C_archive.md（归档批次 r233）；trace 见归档

- 轮(229) 已交付 EDA-Eval-DesignFlow-DiffNetConnLayerSelect-001 — 详细流水已归档 designflow/MEMORY_C_archive.md（归档批次 r233）；trace 见归档

- 轮(228) 已交付 EDA-Eval-DesignFlow-WlDrcClusterPairParse-001 — 详细流水已归档 designflow/MEMORY_C_archive.md（归档批次 r233）；trace 见归档

- 轮(227) 已交付 EDA-Eval-DesignFlow-ImplantFillDummyLeftoverDiag-001 — 详细流水已归档 designflow/MEMORY_C_archive.md（归档批次 r233）；trace 见归档

- 轮(226) 已交付 EDA-Eval-DesignFlow-PcellPatternGeoDiag-001 — 详细流水已归档 designflow/MEMORY_C_archive.md（归档批次 r233）；trace 见归档

- **轮(225) 选料筛选轮 · 0 case · DEBT:1** —— mc>=30 layout-affinity 顶部 3 条候选深读全判 non-seed，parked 入台账（无新 case 落库）。**选料方法**：在 .75 上对 summary.tsv 跑 layout-affinity 打分 `score=ΣLAYOUT − 0.6×ΣSIM`（LAYOUT={calibre,virtuoso,aether,dbGet,dbCreate,cellview,innovus,pcell,layout,lvs,drc,pex}, SIM={netlist,hspice,schematic,synthesis,spectre,finesim,primesim,fsdb,verdi,waveview,ncsim}），排除 ledger_C 364 session。**3 条候选**：① 74dww（e0047434 mc=91, virtuoso278/calibre185, lay0.97）env-recon/how-to，gold=prose 推荐，UI#91 用户贴 libicui18n.so.50 根因→A-disqualify，同 qk0vo/0i3r5/unnkw 类；② pax7g（miccao mc=106, calibre710）AutoCell TCL flow+calibre VCO aok/aoi 修复，重叠 VcoChainFixGen-001+6 miccao AutoCell case，miccao 主题饱和；③ 4ys8e（ellawu mc=178, calibre452）prose 文档 DFM_Spec_Fill.md 26KB markdown 非 runnable，违反 §4.2/§4.3，同 iacrk/kkjsm 类。**结论**：mc>=30 layout-affinity 顶部饱和。**r226 第一件事**：补 DEBT:1，降 mc 到 15 / 取 mc30–60 lay≥0.9 区间（mwxi NEW calibre405 系列 6bs3u/7vfvg/i96df 待深读）/ 触发 .75 rescan，优先 pg_layout(34 最低) 避开 alan3zh。台账：case 220·parked 152(+3)·claimed 0·已动过 372。

- 轮(224) EDA-Eval-DesignFlow-InnovusPwrRtDiag-001（pg_layout, B-synthesized, L1, k=17 a-p+a2）— 详细流水已归档 designflow/MEMORY_C_archive.md（r231 批次）；trace=1793701477122_z5wxj

- 轮(222) EDA-Eval-DesignFlow-SchOaInventoryExtract-001（layout_aether, B-synthesized, L1, k=16 a-p）— 详细流水已归档 designflow/MEMORY_C_archive.md（r223 批次）；trace=1793857146558_8anr6
- 轮(221) 已交付 EDA-Eval-DesignFlow-PexFlowRunLogDiag-001 — 详情已归档 MEMORY_C_archive.md（归档批次 r222）

- 轮(220) 已交付 EDA-Eval-DesignFlow-SvrfTvfLayerMapGen-001 — 详情已归档 MEMORY_C_archive.md（归档批次 r222）

- 轮(219) 阻塞 NFS/ESTALE（已解除）— 详情已归档 MEMORY_C_archive.md（归档批次 r222）

- 轮(218b) EDA-Eval-DesignFlow-DrcQaWidthTypeGeom-001（layout_virtuoso, B-synthesized, L1, k=13 a-m）— 详细流水已归档 designflow/MEMORY_C_archive.md（r231 批次）；trace=1790393143429_ok2y7

- 轮(218) 已交付 EDA-Eval-DesignFlow-ErcPathchkTopoDiag-001 — 详情已归档 MEMORY_C_archive.md（归档批次 r222）

- 轮(217) 已交付 EDA-Eval-DesignFlow-DrcExtendRuleValidator-001 — 详情已归档 MEMORY_C_archive.md（归档批次 r222）

- 轮(216) 已交付 EDA-Eval-DesignFlow-CalibreLvsRepDiag-001 — 详情已归档 MEMORY_C_archive.md（归档批次 r222）

- 轮(215) 已交付 EDA-Eval-DesignFlow-CmLatchMaOpGen-001 — 详情已归档 MEMORY_C_archive.md（归档批次 r222）

- 轮(214) EDA-Eval-DesignFlow-YamlToGds-001（layout_aether, B-synthesized, L1, k=16 a-p）— 详细流水已归档 designflow/MEMORY_C_archive.md（r216 批次（r207-r214 从 MEMORY_C 移入归档））；trace=1793666914540_bsypf

- 轮(213) EDA-Eval-DesignFlow-InvLayoutGen-001（layout_aether, B-synthesized, L1, k=14 a-p）— 详细流水已归档 designflow/MEMORY_C_archive.md（r216 批次（r207-r214 从 MEMORY_C 移入归档））；trace=1793845474118_uno3l

- 轮(211) EDA-Eval-DesignFlow-NoOverlapPcellLayerParse-001（layout_virtuoso, B-synthesized, L1, k=16 a-p）— 详细流水已归档 designflow/MEMORY_C_archive.md（r216 批次（r207-r214 从 MEMORY_C 移入归档））；trace=1792736016983_y42xz

- 轮(212) EDA-Eval-DesignFlow-SwitchGatedSpacePatternGen-001（layout_virtuoso, B-synthesized, L1, k=? a-p）— 详细流水已归档 designflow/MEMORY_C_archive.md（r216 批次（r207-r214 从 MEMORY_C 移入归档））；trace=1793271534868_4c4el

- 轮(209) EDA-Eval-DesignFlow-InnovusProjLogDiag-001（pg_layout, B-synthesized, L1, k=16 a-p）— 详细流水已归档 designflow/MEMORY_C_archive.md（r216 批次（r207-r214 从 MEMORY_C 移入归档））；trace=1793794350956_fi203

- 轮(210) EDA-Eval-DesignFlow-InnovusFpLogDiag-001（pg_layout, B-synthesized, L1, k=16 a-p）— 详细流水已归档 designflow/MEMORY_C_archive.md（r216 批次（r207-r214 从 MEMORY_C 移入归档））；trace=1793760774987_u7mv3

- 轮(208) EDA-Eval-DesignFlow-DrcUnusedVarClassify-001（physical_verify, B-synthesized, L1, k=16 a-p）— 详细流水已归档 designflow/MEMORY_C_archive.md（r216 批次（r207-r214 从 MEMORY_C 移入归档））；trace=1793347000576_ygv3b

- 轮(207) EDA-Eval-DesignFlow-QaWidthPatternGen-001（layout_virtuoso, B-synthesized, L1, k=16 a-p）— 详细流水已归档 designflow/MEMORY_C_archive.md（r216 批次（r207-r214 从 MEMORY_C 移入归档））；trace=1790576594987_e7fdl

- 轮(206) DupViaPriorityCheck-001（layout_aether, B-synthesized, L1, k=16 a-p）— 详细流水已归档 designflow/MEMORY_C_archive.md（r213 批次移入）；trace=1792736045626_maglj yqlu @ hfeg0pkn005 mc=281, gdspy+calibre LVS duplicate-via (via,top) 共用 bottom 检测 + winner/loser 优先级 + good/bad pattern cell

- 轮(7-206) 已归档→ designflow/MEMORY_C_archive.md（含归档批次 164/167/171/173/175/178/184/185/192/194/199/212/213；各轮 case-id/domain/track/k 值详见归档；r212 批次含轮 198-205b 原详细流水, r213 批次含轮 206 原详细流水）
