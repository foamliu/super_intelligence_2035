WAITING: 0
SHARD: D (netlist_wave)
DOMAINS: analog_context, schematic_netlist, waveform
DEBT: 0（#334 的 z5ett DEBT 无效——z5ett 已在 #328 做成 LdoTbGen-001，#334 重复 deepread 是去重 bug；#335 改用 7lp3l 交付 FineSimDataParse-001，已清重复 parked 行）

- **PHASE**: shard D 运行中。已交付 171 条 case（D.jsonl 171 行：analog_context:39/schematic_netlist:94/waveform:38）；台账 case-mark 170 + 920 parked = 1089 已动过。**本轮 #336 = 交付 LdoCircuitReport-001**（analog_context, B-grade synthesized, L1, 16 条件 a-p）：n1njg(jessegao mc137) LDO circuit_diagram_and_verification_report.md 生成器，distinct facet from #328 LdoTbGen-001(本 case 产单 markdown 报告，#328 产 SPICE deck+testbench 文件集)。7lp3l 深读 133msgs/10turns：U#2 给 finesim bench+clk3200MHz，U#3/U#4/U#6 粘贴 $DATA1 FineSimPro 测量块(8 指标 cur_slicer_avg/cur_slicer_latch_avg/ck2q_dfe_t_f/slicer1st_dly_f0 等 + temper 45/-40/130 + alter 1-6)，U#8/U#9 要求优化 pmos/nmos width/finger。合成 gen_finesim_meas_parse.py --data --outdir：解析 $DATA1 块→metrics.json(source/version/title/param_count/metrics/n_metrics/special_cols/corners[{temper,alter,values}]/n_corners/summary{min,max,mean})+report.md(corner 表+汇总表)。A=data_A.txt(strongarm 8 指标 6 corner，真实 trace block 0)；hidden B=data_B.txt(OTA AC 8 指标 5 corner，metric 名与 A 全不相交)；hidden B2=data_B2.txt(bandgap 4 指标 3 corner，全标量)。反硬编码轴：metric 名 A/B/B2 全不相交；corner 数 6/5/3 不同；B2 指标数 4≠8。check 16 条件 a-p(zip 无泄漏/py_compile/B-run exit0+2 文件/source==FineSimPro/metrics==B 8 名顺序/n_metrics==8/special_cols temper+alter/n_corners==5/corner 三键+8 指标/corner 数值与独立解析 B 比对/summary 三键/summary min/max 与独立计算比对/report 含 8 指标名/report 含 temper+alter 列/反硬编码源码无 A 字面量+A-run 产 A 8 指标/跨输入 B2 metrics 4+n_corners 3+确定性 3x sha256)。自验：ref PASS 16/16 + 6 negatives(empty_shell/hardcode_a/hardcode_b/print_expected/ref_core_deleted/drop_corners)全 FAIL + §4.9 三假全 FAIL。**断言闸门** k_rationale=k_check=16 ✓。台账 mark 7lp3l→case(FineSimDataParse-001)；删除 #334 重复 z5ett parked 行(z5ett 已是 #328 LdoTbGen-001 case)；25 条 weak 候选 parked(vbxlf/o5o6p/27c6f/5vmvu/kxqt7/o4frj/8zuqr/mrlo9/0j59o/j90k2/xxtqb/41sqh/vtl11/rw6z4/ibsuq/a9ta2/1488k/wqxag/w5knw/6sxh5/sr1fw/fxcqv/pax7g/be1i0/1giox)。深读笔记 designflow/trace_deepreads/7lp3l_finesim_meas.md。analog_context 37→38；D.jsonl 170→171。
- (归档批次 2032) 历史 #327 ShortCfgTrace-001 选料/合成流水已搬 MEMORY_D_archive.md
- ⚠️ **关键发现（cline 存储变更）**：cline session 存储现为**目录式** `/home/<user>/.cline/data/sessions/<sid>/<sid>.messages.json`（非根目录 `<sid>.messages.json`）。messages.json 格式 = `{"version":1, ..., "messages":[{"role":"user","content":[{"type":"text","text":"<user_input mode=\"act\">..."}]}]}`（content 是 list，非 str）。旧 peek 脚本（peek_211/216/218/D313/D316）用根目录路径，现在会全部 NO_FILE。**已写修正版 designflow/peek_dirbased.py**（目录路径 + 解析 data["messages"] + content list）供下轮复用。下轮 peek 必须用此版。
- ⚠️ **选料去重 bug 修复**：fresh_D306_pool.tsv 是 #306 时构建的快照，之后台账增长（#314-316 claim 了 cq860/4ne3u/9p8g2 等），这些 session 仍在旧 pool 里。`comm -23 pool_sids peeked_sids` 只排已 peek，**漏排已入台账的**→会重选已做 case（本轮误把 cq860 当 fresh，claim 时 REFUSED 才发现已是 #314）。**正确口径**：fresh_avail = pool_sids − peeked_sids − ledger_sids（已存 designflow/fresh_D317_avail.tsv，176 行）。下轮直接用此文件。

- (归档批次 63) 历史 #268 CellPrefixExtract-001 选料流水已搬 MEMORY_D_archive.md
- 每轮做 1 条 case：trace_ledger.py --shard D next → claim → 深读 → 合成 → 自验 → 追加 EDA-Eval-DesignFlow_D.jsonl → 日报
- ⚠️ **台账/排除集修复**：trace_ledger.py `next` 生成的 awk 排除集有 digit 转写 bug（如 `1790142103120_n91pk` 实际应为 `1790142100320_n91pk`），且 excl 条目带 `.messages.json` 后缀而 summary.tsv session_file 也带后缀、awk `sub` 剥后缀后两边不匹配 → 已交付 session(n91pk/wg5u2/wb03t/4a852) 漏排重返候选池。**本轮改用 4-shard TSV 实读 262-anchor 排除集 + awk BEGIN 对 excl 也 `sub(/\.messages\.json$/,"")` 双边剥后缀**（designflow/_tmp/excl_all.txt，运行后清理），得真 fresh 候选。建议运维修 trace_ledger.py：(1) anchor 从 TSV 直读勿二次转写；(2) 排除匹配双边剥 `.messages.json`。
- 📊 trace 覆盖率：170 / 1511 = 11.3%（mc>=30 候选池；D.tsv 现 170 case-mark + 920 parked · 已动过 1089；快照 2026-11-07 02:23 sessions=5822 mc300=347 mc500=281 mc1000=8）。已覆盖 domain（D.jsonl 171 行）：analog_context:39 · schematic_netlist:94 · waveform:38。⚠️ **#336 选料（fresh_D319_avail 池 4 批 peek mc 56-138, 共 ~30 候选）**：~30 候选几乎全 weak（layout-placement/rscalc/autovia=shard C / SimDiag-skill-writing / Q&A / NO_FILE / regression-run / schematic-highlight-L2-live），唯 n1njg(jessegao mc137 LDO 电路图+验证报告)有可移植 D-domain produce facet→交付 LdoCircuitReport-001。印证 #335 结论「mc 56-262 池 produce 密度极低，Q&A/debug/skill/layout 占主导」。weak 候选未批量 parked（budget），下轮重建 fresh pool 时排除。
- 📦 体积：TASK_D≈25KB / MEMORY_D≈27.7KB（归档批次 2039 后；低于 32KB 红线）
- DEBT: 1（#334 选料/peek 轮，z5ett LDO A-faithful seed 深读完成待 #335 合成）。**下轮 #335 第一件事**：合成 z5ett LDO deck+report generator（B-grade synthesized, L1 离线, 12-16 条件），gen_ldo_design.py --spec --outdir → dut.sp+tb_ac+tb_loadreg+tb_linereg+tb_psrr+report.md，check 验结构不验 sim 结果。深读笔记 designflow/trace_deepreads/z5ett_ldo_design.md 含真实 spec+dut 拓扑。备用：(1) 继续跨 shard trace 共享；(2) 放宽 mc>=15 重建 fresh pool 并 peek。
- 🧾 断言: k_rationale=k_check=16 ✓（本轮 #336 LdoCircuitReport-001 16 条断言 ①-⑯ 对应 check a-p 全；#335 FineSimDataParse-001 16 条断言 ①-⑯ 对应 check a-p 全；#333 WvSigListGen-001 16 条断言 ①-⑯ 对应 check a-p 全；#332 MillerOpampTopoAudit-001 16 条断言 ①-⑯ 对应 check a-p 全；#331 DlyChainTrace-001 16 条断言 ①-⑯ 对应 check a-p 全；#330 CpumpDeckGen-001 16 条断言 ①-⑯ 对应 check a-p 全；#328 LdoTbGen-001 16 条；#327 ShortCfgTrace-001 16 条；#326 SpfTriggerMonitor-001 16 条；#325 PatternParamAudit-001 16 条；#324 NetlistFightX-001 16 条；#323 OtaSimReport-001 16 条；#322 VcdEdgeTraceZ-001 16 条；#321 CellRemapInvBase-001 16 条；#320 PatternVDepResolver-001 16 条；#319 SpfDiffCompare-001 16 条；#318 MeasStmtExtract-001 16 条；#315 FmInstFreq-001 16 条；#314 DlygResInsert-001 16 条；#313 NetlistSigRename-001 16 条；#312 NetlistHierFlowchart-001 16 条；#311 CdlXistorAudit-001 16 条；#310 NetlistCellReplace-001 16 条；#309 NetlistGate2Verilog-001 16 条；#308 CellRewriteSimlib-001 16 条；#307 OpCornerSummary-001 15 条；#306 FarthestCellPick-001 14 条；#305 SpStimLoopAudit-001 16 条；#304 SimReportPvtSummary-001 15 条；#303 WaveMaxFind-001 15 条；#302 SpTestbenchParamFix-001 14 条；#301 NetlistMMultAudit-001 16 条；#299 SineZeroCrossFreqPeak-001 16 条；#298 InvPulseStimTb-001 14 条；#297 SpiceldViewChg-001 14 条；#296 FinesimIgnoreGen-001 14 条；#295 CosimStimFolderGen-001 14 条；#294 CellExpandGen-001 14 条；#293 SchFixFloating-001 14 条）。shard D 存量 166 条 test_rationale 全部以 `k 条断言：①…` 开头已核验达标。今日 123/171 达标。rewrite_queue.tsv 全部 done（无待修）。

## 流水
- 2026-11-07 04:1x-04:5x | shard D #336 | **交付 LdoCircuitReport-001**（analog_context, B-grade synthesized, L1, 16 条件 a-p）。open_session shardD_designflow_20261107_shardD-336_0。**选料**：fresh_D319_avail(mc>=30)池 4 批 peek 共 ~30 候选(mc 56-138)，写 peek_D336.py(目录式 cline 存储)在 .75 跑(max_workers=12 并发 ssh)。**peek 结果**：194wf=AnaWeave layout placement(shard C) / wiglh=run-regression(weak) / ajcab=schematic highlight L2-live(weak) / xs1lj=NO_FILE / n1njg=★LDO 设计 / 4ys8e=DFM implant fill(shard C) / pepxy=rscalc RTEXT(shard C) / 0oeb7=delete API(weak) / iz828=aether bindkey Q&A / n52mz=NO_FILE / zh4of=autovia(shard C) / 92ykp=rscalc(shard C) / hkyyj=OA API layout(shard C) / huntx=autovia(shard C) / ca92c=skill writing+layout / t2hnp=skill review / 7kyrv=logic_cosim debug / tcqqs=SimDiag skill / d1cg3=Finesim Q&A / 9pcjd=autocell PDK audit(borderline) / ku6wp=PDN_sim Q&A / hpd7c=Totem-SC EM tool update / acdfh=sandbox Q&A / 4qpyk=DDR5 config_pincheck shift(debug) / phgjl=SimDiag skill / tze5k=SimDiag CLI / xyj1z=NO_FILE / ckulq=RDC SpyGlass(shard A) / qhcja=Aether API Q&A → **唯 n1njg 可移植 D-domain produce**。**n1njg 深读**：ssh cat 拉 n1njg.messages.json(1.05MB/233msgs) → 提取 user turns + editor writes。U#0「帮我生成一个LDO电路上电压域为1.1V，输出为0.9V，要求其静态功耗10uA以内，PSRR=-20dB@0~100kHz，DC gain大于40db，PHASE MARGIN 大于40度」+ U#1「psrr为负值」+ U#2/U#3「帮我输出一份电路图及验证报告」+ U#4 用户接受产物 /home/jessegao/Spice_Agent/design/ldo_v1/circuit_diagram_and_verification_report.md。assistant editor writes: spec.md/dut_ldo_v1.sp/tb_ldo_v1_ac/loadreg/linereg/psrr.sp(dup #328 deck+TB)+circuit_diagram_and_verification_report.md(★distinct facet, 20KB, 7 sections: 拓扑ASCII/器件清单/DC解析/达标矩阵/PVT/PSRR负值声明/文件清单)+verify_psrr.py/clean_spec.py/fix_psrr_sign.sh。**A-faithful 判定**：U#0 纯 produce + U#4 用户接受 → 表面可行；但产物非便携+deck+TB 部分与 #328(z5ett, LdoTbGen-001)同 user 同 spec 重叠 → **B 档 synthesized**：取 distinct facet=circuit_diagram_and_verification_report.md 生成器(spec→单 markdown 报告)，check 验结构+spec驱动不验 sim，L1 离线可验。与 #328 区分：本 case 产**单 markdown 报告**，#328 产**SPICE deck+4 testbench 文件集**。**合成**：gen_ldo_circuit_report.py --spec --outdir 读 spec JSON{vdd,vout,iqs_max,psrr_db,psrr_freq,gain_db,pm_deg,vref,r2,iload_max,cout,resr} → derive(R1=R2×(vout/vref−1), Itail=Iq/5, wpass_um, nf_pass, ach_vout/iquiescent/psrr/gain/pm) → gen_report(7 sections: header/拓扑ASCII(VDD+Rbias+EA X1-X4+X5/X6+Xpass+R1/R2 divider+Cout/Resr)/器件表≥9/DC工作点表(VOUT公式+VFB+Vdrop+Itail)/达标矩阵5项/PSRR负值声明/PVT tt-ff-ss/文件清单)。A=spec_A.json(真实 trace spec: vdd1.1/vout0.9/iqs10uA/psrr-20dB@0~100kHz/gain40/pm40/vref0.825/r2 1.1M)；hidden B=spec_B.json(vdd1.2/vout1.0/iqs5uA/psrr-25dB@0~1MHz/gain50/pm55/r2 1.1M)；hidden B2=spec_B2.json(vdd1.8/vout1.5/iqs20uA/psrr-15dB@0~10kHz/gain35/pm45/r2 2.2M)。反硬编码轴：vout/vdd/iqs/psrr_freq/gain/pm 全不同；R1 由 spec 推导(硬编 A 的 100k → B 上 j FAIL)；PSRR freq 范围 0~100kHz/0~1MHz/0~10kHz 不同；r2 1.1M/1.1M/2.2M 不同；vref 共享 0.825 但 vout 不同→ratio 不同。金标 gen_ldo_circuit_report_ref.py。check.py 16 条件 a-p：解 zip(防 check/reference/negative/jsonl/tsv/spec_B 泄漏)→py_compile→B-run exit0+report>1000chars→拓扑段(VDD/Xpass/R1/R2/diff pair X1/X2)→器件表≥6→DC段 VOUT 公式+计算值==spec_B.vout(1.0,±2%)→达标矩阵5项+表格→PSRR负值声明(越负越好)→PSRR段含 B freq 0~1MHz→R1 由 spec 推导(233.3k,±10%)→PM achieved>55→gain achieved>50→反硬编码(源无 A freq 字面量 0~100kHz + A-run 产 A vout=0.9)→跨输入 B2 vout==1.5+B2 R1(1.8M)≠B R1→B2 5 spec 项+B2 freq 0~10kHz→确定性 3x sha256。自验：ref PASS 16/16 a-p + 7 negatives(empty_shell=3/16 / hardcode_a=10/16 / hardcode_b=13/16 / print_expected=11/16 / ref_core_deleted=14/16 / no_psrr_neg=15/16 / drop_corners=15/16)全 FAIL + §4.9 三假(empty/print_expected/ref_core_deleted)全 FAIL。**断言闸门** k_rationale=k_check=16 ✓。台账 mark n1njg→case(LdoCircuitReport-001)。analog_context 38→39；D.jsonl 170→171；台账 case-mark 169→170。**教训**：(1) **fresh_D319_avail 池 mc 56-138 区段 produce 密度极低**(~30 候选仅 1 可移植 D-domain produce)，印证 #317/#332/#335 结论「中低 mc 池 Q&A/debug/skill/layout(L2-live/physical_verify) 占主导」；e0014566 用户 4 连(92ykp/zh4of/huntx/acdfy)全 layout/rscalc/autovia(shard C)；sagequan 2 连(tcqqs/phgjl)全 SimDiag skill writing；(2) **n1njg 与 #328(z5ett)同 user 同 LDO spec 但 distinct facet**：#328 取 deck+TB 生成器，本 case 取 circuit_diagram_and_verification_report.md 生成器——不同 produce+check，trace_source 不同 session，可作 distinct case（继 #331/#332/#335 同 trace 多 facet 模式）；(3) **PSRR 负值声明是强反硬编码轴**(U#1 用户澄清「psrr为负值」)，report 必须含「越负越好」声明，naive 写正数者 h 上 FAIL；(4) **R1 spec 推导 R1=R2×(vout/vref−1) 是反硬编码核心**：硬编 A 的 100k 者 B 上 j FAIL(f=1.0≠0.9)，hardcode_a negative 即此；(5) **fix bug**: check.py VOUT 值提取正则 VOUT[^|]*\|\s*([0-9.]+)\s*V 因 DC 表行多 | 列失败，改用全局 re.findall(r"([0-9]+\.[0-9]+)\s*V") 扫所有 N.NN V 值匹配 spec.vout；(6) **fix bug**: check.py (o) b2_freq 在 lowercased 文本里搜 "0~10kHz"(camelCase) 不匹配，改搜 "0~10khz"。
- (归档批次 2040) 流水 #335 (FineSimDataParse-001, analog_context, B-grade synthesized, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2039) 流水 2026-11-07 03:2x-04:0x #334 选料/peek 轮 已搬 MEMORY_D_archive.md
- (归档批次 2036) 流水 #333 (WvSigListGen-001, waveform, B-grade synthesized, 16 条件 a-p) 已搬 MEMORY_D_archive.md/Vdd_ac), 越负越好, @100kHz 预计 -5~+10dB 不满足 -20dB」+ corners tt/ff/ss + Cout2nF ESR3ohm）+ dut_ldo_v1.sp（.SUBCKT ldo_v1 vdd vout gnd vref en：5T EA=nMOS diff X1/X2 ntn w5u l2u (gate=vref/vfb, src=tail_n) + pMOS mirror X3/X4 ptn w5u l2u (X3 diode-conn gate==drain=ea_out) + bias X5/X6 ntn_m w6u/w2u l2u + Rbias 290k vdd→vb_tail + PMOS pass Xpass ptn w5u l0.3u **nf200** (drain=vout gate=ea_out src=vdd) + R1 100k vout→vfb + R2 1.1M vfb→gnd (ratio → vfb=0.825 → vref≈0.825) + Cout 2n vout→vout_esr + Resr 3 vout_esr→gnd）。**A-faithful 判定**：U#0 纯 produce + user-accepted 产物存在 + 真实 spec/dut 可提取 → **A-faithful 可行**；但产物在 /home/jessegao（非便携）+ live SPICE 验证（PSRR/gain/PM）→ **B 档 synthesized**：spec-driven LDO deck+report 生成器（gen_ldo_design.py --spec --outdir → dut.sp+tb_ac+tb_loadreg+tb_linereg+tb_psrr+report.md），check 验**结构**不验 sim 结果（无需真跑 SPICE，L1 离线可验）。**本轮因 40min 预算耗尽未能合成** → parked z5ett 留 #335 合成（DEBT:1）。深读笔记 designflow/trace_deepreads/z5ett_ldo_design.md（含真实 spec+dut 拓扑+合成 plan+check 12-16 条件清单）。**7 weak 候选已全部 parked** 防止重选（jsb4j/npkmm/ld0p8/nibwl/ewjnc/wsi93/4vv1y）。台账 case-mark 168 + parked 895 = 1063 已动过；analog_context 33/schematic_netlist 81/waveform 33 不变；D.jsonl 169 行不变。**断言闸门**：本轮无 case 交付，k 断言不适用。**教训**：(1) **fresh_D317_avail 池顶部 mc 137-196 区段 produce 密度极低**（8 中 7 weak，仅 1 A-faithful），印证 #317/#332 结论「中等 mc 池 Q&A/debug/skill 占主导」；(2) **z5ett 是干净 A-faithful LDO produce 范式**：spec-driven deck 生成（5T EA+PMOS pass+divider+Cout/ESR）是 analog_context L1 可验好范式，spec→器件参数映射明确（pass W/nf 由 iload+vdrop 推，divider ratio 由 vout/vref 推），16 条件天然丰富（拓扑/测试台/报告/跨输入/确定性）；(3) **PSRR 负值声明是强反硬编码轴**（U#1 用户澄清「psrr 为负值」），report.md 必须含「越负越好」声明，naive 写正数者 FAIL；(4) **ssh cat 拉 messages.json 须用 ip 不带 user**（.75 e0031982 免密到 697/698，但 scp/jessegao@ 失败 Permission denied；peek 脚本用 `ssh ip cmd` 不带 user 才通）；(5) **选料/peek 轮需把 weak 候选全部 park** 防止下轮重选（本轮 7 条全 parked）。open_session default_designflow_shardD-333_0。**选料**：fresh_D319_avail(mc>=30)池 #329 已确认 clean produce 耗尽；本轮 peek 5 条 parked cross-shard dup 候选(ooyxi=sophiaw NO_FILE / 314mt=sophiaw 0turns / x2w2z=yueliu L2 FineSim fqueue batch / fkprl=e0014566 L2 layout RTEXT/RNODE / u78sz=hengbow ★waveform .sig 生成)→选 u78sz 跨 shard 共享(继 #331 6qt0a、#332 ahjnv 第三例)。u78sz(hengbow/hfeg0pgn045 mc407, ledger parked note「cross-shard dup = A CoreTimingSig-001 (verification)」)已被 shard A 取 verification L2 意图(coretiming 时序违例检查/分析)；本 case 取**同 trace 不同意图**=waveform L1 离线 .sig 信号列表生成器，无 FSDB/waveview/fscript 依赖。在 .75 deepread_u78sz.py + deepread_u78sz_sig.py 提取 511 msgs/25 user turns + assistant tool_use(.sig writes)：U#2「检查 ddr5 fullchip array coretiming+时序违例，找开启地址对应 wl 和 BL」+U#4「给出关键信号的路径 list，waveview 下直接 load」+U#5「把你找的信号也弄成 sig_demo.sig 格式」+U#8/U#13/U#24「wv 只认小写」+U#11「分五个文件我一次只能 load 一个」+U#16/U#17「根据 netlist 找真实层次不猜测」。**A-faithful 不可行**：真实 /home/hengbow fsdb(2GB)+netlist(公共目录)不可附加 + live waveview/fscript 不便携 → **B 档 synthesized**。**合成**：gen_wv_sig.py(--spec <spec.json> --outdir <dir>) 读 spec JSON{design,n_files,groups:[{name,file,signals:[...]}]}，_split_leaf(路径按 . 拆 parent+leaf)+_format_signal(顶层 signal=v(leaf)/层次 signal=parent.v(leaf) **全小写**，总线位 <n> 保留)+gen(每组一 .sig 文件+# group/# design 注释+单文件去重+manifest.json{design,n_files,total_signals,files:[{name,n_signals}]})。A=spec_A.json(DDR5_CORETIMING 5 groups 84 signals: 01_top_pad 23/02_read_pad 29/03_controller 6/04_array_addr 16/05_array_bl_wl 10，真实 trace 信号 ck_t/ca<0..13>/ldqpad<0..7>/cm1_fc_rdlatencyto56/ra10<0..3>/ra10gapin<0..3>/ble_b<0..3>/wlr<0>)；hidden B=spec_B.json(LPDDR4_PHY **4 groups** 46 signals, PHY_top 层次, ck_p/cmd<0..6>/dq<0..7>/phy_rdlat_sel<0..2>/rowa<0..3>/wlx<0..1>，与 A 信号名全不相交)；hidden B2=spec_B2.json(SERDES_ANALOG **3 groups** 19 signals, serdes_top 层次, **全标量无总线位** vddl!/vbg/ibias/pfd.up/cp_out/vco_ctrl/drv.outp/dfe_tap，测无总线处理)。反硬编码五轴：design DDR5/LPDDR4/SERDES 全不同；group 数 5/4/3→输出文件数不同(硬编 5 者 B 上 g FAIL)；信号名全不相交(硬编 A 信号者 B/B2 上 i/n FAIL)；层次前缀 xictop/PHY_top/SerDes_top 全不同；B2 无总线位(不处理标量者 o FAIL)。金标 gen_wv_sig_ref.py。check.py 16 条件 a-p：解 zip(防 check/reference/negative/jsonl 泄漏)→py_compile→B 真跑 subprocess(spec 路径 abspath 化)→全小写(WaveView 硬约束, 字母检查)→v(leaf)/path.v(leaf) 格式(正则, 总线 <n> 允许在 v 内)→无 [ 方括号(必须 <>)→.sig 文件数==spec_B group 数 4→manifest 文件名集==实际+各 n_signals==实际行数→每 .sig 文件含其 group 全部叶子(去重后)→. 层次分隔(无 / 或 ::)→单文件无重复 signal=→# 注释存在且不被计为 signal→反硬编码源码无 A 标记(ck_t/cm1_fc_rdlatencyto56/ra10gapin/ble_b<0>/xictop.xi_array8g_t)+A-run 产 v(ck_t)+v(ca<0>)→跨输入 B2-run 产 serdes_top+group 数 3≠4→B2 所有 signal= 行无 <(全标量)→3 次确定性 sha256。自验：ref PASS 16/16 a-p + 6 negatives(empty_shell→c / hardcode_a→g / no_lowercase→d / no_split→g / print_expected→c / ref_core_deleted→e)全 FAIL + §4.9 三假(empty/print_expected/ref_core_deleted)全 FAIL。**断言闸门** k_rationale=k_check=16 ✓。**教训**：(1) **跨 shard trace 共享第三例验证可行**：u78sz 已被 A 取 verification L2(coretiming 时序违例检查)，本 case 取同 trace waveform L1 离线 .sig 生成——不同意图+domain+L-level+check，parked note「D does not rebuild」可被 mark 覆盖（继 #331/#332 模式，parked 行保留 note + 新 case 行加 case_id）；(2) **WaveView 全小写是强反硬编码约束**：用户反复强调(U#8/13/24)「wv 只认小写」，生成器必须 lowercase 全部路径——naive 保留原 case 者 d 上立即 FAIL；(3) **.sig 格式 = signal = path.v(leaf)** 是 waveform L1 可验好范式：叶子 v() 包裹 + 点分层次 + 总线 <n>，16 条件天然丰富(格式/小写/分文件/去重/manifest/跨输入/确定性)；(4) **B2 全标量无总线位**是额外反硬编码轴：不处理标量(总输出 <n>)者 o 上 FAIL；(5) fix bug: check.py (e) 正则 v\([^()<>]+\) 会拒总线位 <n>，改 v\([^()]+\)（v 内允许 <> 仅拒括号）；(6) fix bug: _run_candidate subprocess cwd=tmp_out 需 spec 路径 abspath 化，否则相对 spec 路径解析失败。台账 mark u78sz→case；waveform 32→33；D.jsonl 168→169。
- (归档批次 2037) 流水 #332 (MillerOpampTopoAudit-001, schematic_netlist, B-grade, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2035) 流水 #331 (DlyChainTrace-001) 已搬 MEMORY_D_archive.md
- (归档批次 2037) 流水 #330 (CpumpDeckGen-001, analog_context, B-grade, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2034) 流水 #329 (选料/peek 轮, DEBT:1) 已搬 MEMORY_D_archive.md
- (归档批次 2034) 流水 #328 (LdoTbGen-001) 已搬 MEMORY_D_archive.md
- (归档批次 2033) 流水 #327 (ShortCfgTrace-001) 已搬 MEMORY_D_archive.md
- (归档批次 2032) 流水 #326 (SpfTriggerMonitor-001) 已搬 MEMORY_D_archive.md
- (归档批次 2030) 流水 #318 已搬 MEMORY_D_archive.md
- (归档批次 2030) 流水 #319 已搬 MEMORY_D_archive.md
- (归档批次 2030) 流水 #320 已搬 MEMORY_D_archive.md
- (归档批次 2030) 流水 #321 已搬 MEMORY_D_archive.md
- (归档批次 2030) 流水 #322 已搬 MEMORY_D_archive.md
- (归档批次 2033) 流水 #323 (OtaSimReport-001) 已搬 MEMORY_D_archive.md
- (归档批次 2037) 流水 #317 (选料/peek 轮, DEBT:1) 已搬 MEMORY_D_archive.md
- (归档批次 2037) 流水 #316 (ToggleCounterBindGen-001, schematic_netlist, A-grade, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2029) 流水 #315 (FmInstFreq-001) 已搬 MEMORY_D_archive.md
- (归档批次 2028) 流水 #314 (DlygResInsert-001) 已搬 MEMORY_D_archive.md
- (归档批次 2027) 流水 #313 已搬 MEMORY_D_archive.md
- (归档批次 2027) 流水 #312 已搬 MEMORY_D_archive.md
- (归档批次 2027) 流水 #312-prep 已搬 MEMORY_D_archive.md
- (归档批次 2027) 流水 #311 已搬 MEMORY_D_archive.md
- (归档批次 90) 流水 #309 (NetlistGate2Verilog-001) 已搬 MEMORY_D_archive.md
- (归档批次 91) 流水 2026-11-06 13:5x | shard D #310 | 交付 NetlistCellReplace-001（16 条件 a-p）已搬 MEMORY_D_archive.md
- (归档批次 89) 流水 #308 (CellRewriteSimlib-001) 已搬 MEMORY_D_archive.md
- (归档批次 85) 流水 #303 (WaveMaxFind-001, waveform, 15 条件 a-o) 已搬 MEMORY_D_archive.md
- (归档批次 88) 流水 #302 已搬 MEMORY_D_archive.md
- (归档批次 91) 流水 2026-11-06 08:0x | shard D #301 | 交付 NetlistMMultAudit-001（16 条件 a-p）已搬 MEMORY_D_archive.md
- (归档批次 83) 流水 #300 (选料/peek 轮) 已搬 MEMORY_D_archive.md
- (归档批次 84) 流水 #299 (SineZeroCrossFreqPeak-001) 已搬 MEMORY_D_archive.md
- (归档批次 75) 流水 #291 (LatDffRsHierExtract-001) 已搬 MEMORY_D_archive.md
- (归档批次 76) 流水 #292 (WvFsdbReaderV2Gen-001) 已搬 MEMORY_D_archive.md
- (归档批次 77) 流水 #293 (SchFixFloating-001) 已搬 MEMORY_D_archive.md
- (归档批次 78) 流水 #294 (CellExpandGen-001) 已搬 MEMORY_D_archive.md
- (归档批次 74) 流水 #290 (PorCapSweepGen-001) 已搬 MEMORY_D_archive.md
- (归档批次 72) 流水 #289 (WvAcReportGen-001) 已搬 MEMORY_D_archive.md
- (归档批次 73) 流水 #288 (ChPulseRespGen-001) 已搬 MEMORY_D_archive.md
- (归档批次 70) 流水 #287 (CtleTranGen-001) 已搬 MEMORY_D_archive.md
- (归档批次 69) 流水 #286 (Wr2dqEdgeMeas-001) 已搬 MEMORY_D_archive.md
- (归档批次 68) 流水 #285 (Wr4thCkMeas-001) 已搬 MEMORY_D_archive.md
- (归档批次 2027) 流水 #285 已搬 MEMORY_D_archive.md
- (归档批次 67) 流水 #284 (SiInpTokenStrip-001) 已搬 MEMORY_D_archive.md
- (归档批次 66) 流水 #283 (PsdDqMap-001) 已搬 MEMORY_D_archive.md
- (归档批次 65) 流水 #282 (MeasTrtfSkewGen-001) 已搬 MEMORY_D_archive.md
- (归档批次 65) 流水 #280 (VrefcsMrrSeq-001) 已搬 MEMORY_D_archive.md
- (归档批次 64) 流水 #279 (碰撞让步轮 MosParamStat-001, 无交付) 已搬 MEMORY_D_archive.md
- (归档批次 64) 流水 #278 (CircWfReport-001, analog_context, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2027) 流水 #277 已搬 MEMORY_D_archive.md
- (归档批次 63) 流水 #276 已搬 MEMORY_D_archive.md（含选料/peek/深读/合成/自验/教训全文）
- (归档批次 63) 流水 #275 已搬 MEMORY_D_archive.md（含选料/peek/深读/合成/自验/教训全文）
- (归档批次 63) 流水 #273 已搬 MEMORY_D_archive.md（含选料/peek/深读/合成/自验/教训全文）
- (归档批次 63) 流水 #272 已搬 MEMORY_D_archive.md（含选料/peek/深读/合成/自验/教训全文）
- (归档) 流水 #268 已搬 MEMORY_D_archive.md（归档批次 59）
- (归档) 流水 #267 已搬 MEMORY_D_archive.md（归档批次 59）
- (归档) 流水 #266 已搬 MEMORY_D_archive.md（归档批次 59）
- (归档) 流水 #265 已搬 MEMORY_D_archive.md（归档批次 59）
- (归档) 流水 #264 已搬 MEMORY_D_archive.md（归档批次 59）
- (归档) 流水 #263 已搬 MEMORY_D_archive.md（归档批次 58）
- (归档) 流水 #262 已搬 MEMORY_D_archive.md（归档批次 58）
- (归档) 流水 #261 已搬 MEMORY_D_archive.md（归档批次 58）
- (归档) 流水 #260 已搬 MEMORY_D_archive.md（归档批次 57）
- (归档) 流水 #258 已搬 MEMORY_D_archive.md（归档批次 57）
- (归档) 流水 #259 (MosSizeDoeGen-001) 已搬 MEMORY_D_archive.md（归档批次 56）
- (归档) 流水 #258 已搬 MEMORY_D_archive.md（归档批次 57）
- (归档) 流水 #257 已搬 MEMORY_D_archive.md（归档批次 57）
- (归档) 流水 #256 已搬 MEMORY_D_archive.md（归档批次 57）
- (归档) 流水 #255 已搬 MEMORY_D_archive.md（归档批次 57）
- (归档) 流水 #254 已搬 MEMORY_D_archive.md（归档批次 57）
- (归档) 流水 #253 (SweepCfgParse-001) 已搬 MEMORY_D_archive.md（归档批次 58）
- (归档) 流水 #252 (aq0vc/SpStimGen-001) + #251 (xkg53/FinesimAutoRun-001) 已搬 MEMORY_D_archive.md（归档批次 55）
- (归档) 流水 #250 (eypbp/PwlConvert-001) 已搬 MEMORY_D_archive.md（归档批次 55）
- (归档) 流水 #249 (s96je/HierSpiceMosCount-001) 已搬 MEMORY_D_archive.md（归档批次 55）
- (归档) 流水 #248 (7fcir/OpenWaveFmt-001) 已搬 MEMORY_D_archive.md（归档批次 55）
- (归档) 流水 #240-#247（含 #247 3jb3i/Tcs0PatAnalyze-001 全文）已搬 MEMORY_D_archive.md（归档批次 53/54/55）
- (归档) 流水 #240-#246 已搬 MEMORY_D_archive.md（归档批次 53）
- (归档) 流水 #241 已搬 MEMORY_D_archive.md（归档批次 52）
- (归档) 流水 239 已搬 MEMORY_D_archive.md（归档批次 51）
- (归档) 流水 238 已搬 MEMORY_D_archive.md（归档批次 51）
- (归档) 流水 237 已搬 MEMORY_D_archive.md（归档批次 51）
- (归档) 流水 235 已搬 MEMORY_D_archive.md（归档批次 51）
- (归档) 流水 234 已搬 MEMORY_D_archive.md（归档批次 51）
- (归档) 流水 233 已搬 MEMORY_D_archive.md（归档批次 51）
- (归档) 流水 #232 已搬 MEMORY_D_archive.md（归档批次 50）
- (归档) 流水 #231 已搬 MEMORY_D_archive.md（归档批次 50）
- (归档) 流水 #230 已搬 MEMORY_D_archive.md（归档批次 50）
- (归档) 流水 #229 已搬 MEMORY_D_archive.md（归档批次 50）
- (归档) 流水 #228 已搬 MEMORY_D_archive.md（归档批次 50）
- (归档) 流水 #227 已搬 MEMORY_D_archive.md（归档批次 50）
- (归档) 流水 #225 已搬 MEMORY_D_archive.md（归档批次 50）










- (归档) 流水 #193–#204 已原文搬 MEMORY_D_archive.md（归档批次 2026-11-03 #205）；更早 #164–#192 亦见 prior commits / ARCHIVE_OPERATOR_DESIGNFLOW.md
