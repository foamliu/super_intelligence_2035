WAITING: 0
SHARD: D (netlist_wave)
DOMAINS: analog_context, schematic_netlist, waveform

- **PHASE**: shard D 运行中。已交付 165 条 case（D.jsonl 165 行）；台账 case-mark 164 + 890 parked = 1054 已动过。**本轮 #328 交付 LdoTbGen-001（B 档 synthesized, analog_context, L1 真跑候选, 16 条件 a-p）**。选料：fresh_D319_avail.tsv(144) 排除 ledger → 133 真 fresh；本机无法直 ssh 698 机，改在 .75 workdir 跑 peek_D328.py(目录式 cline 存储 `<sid>/<sid>.messages.json` + 解析 data["messages"] content list)。peek batch1(10 候选 mc 68-103): xyj1z=NO_FILE·sr426=verilog .trn 波形读+netlist fight 分析(live simvision)·phgjl=nturns0·y2xz6/u29lu=skill 搭建·9pcjd=autocell security rep(live /apps+/proj)·vhz0j=calibreDRC.rule 逐条 Q&A·htwv2=LVS rule 拆解 Q&A(0 edits)·50mu7=Spice_Agent skill 加载·hpd7c=Totem-SC 源码包更新(代码转录非 EDA)。peek batch2(10 候选 mc 115-184): 41sqh=simdiag-cli skill+RAG demo·wiglh=run-regression skill·n52mz=NO_FILE·j90k2="give me EDA image"+bsub test(玩耍)·1488k=Sentaurus TCAD MCP 开发(软件工程非 D 域)·o4frj=DRC log rule-time 解析(physical_verify 非 D 域,但 clean 转换)·o5o6p=VCLP UPF 低功耗 flow(digital 非 D)·5vmvu=SKILL .il 脚本改(live OA)·4ys8e=DFM SPEC FILL(live calibre)·**z5ett(jessegao mc137 aether:512 transistor:224 netlist:129)★★=LDO 设计+SPICE 测试台生成**(U#0 逐字「帮我生成一个LDO电路上电压域为1.1V，输出为0.9V，要求其静态功耗10uA以内，PSRR=-20dB @0~100kHz，DC gain大于40db，PHASE MARGIN 大于40度」+U#1 澄清「psrr为负值」+U#2/3「输出电路图及验证报告」；agent 51 editor 写入产 dut_ldo_v1.sp + tb_ac/tb_psrr/tb_linereg/tb_loadreg.sp + spec.md + reports，经 Spice_Agent/aether live 流)。**决策**：U#0 纯指标驱动 produce 未给根因(A 合规)，但 live pyaether+PDK 不可附加 → **B 档 synthesized**。合成：配置驱动 LDO 设计+测试台生成器 gen_ldo_design.py(--specs --outdir)，读 8 字段 emit dut.sp(.subckt ldo vdd vout gnd + PMOS pass + VCVS 误差放大 + **R1/R2 反馈分压 R1/R2=vout/vref-1** + Vref + Cc) + 4 测试台(tb_ac .AC+.measure gain/pm；tb_psrr Vdd AC 注入+.measure PSRR；tb_linereg .DC Vdd；tb_loadreg .DC Iload+.measure) + spec.md(7 label:value)。A=specs_A.json(真实 vin1.1/vout0.9/vref0.6/iload10mA/iq10uA/psrr-20/gain40/pm40)；hidden B=specs_B.json(vin1.2/vout0.8/vref0.5/iload20mA/iq5uA/psrr-30/gain50/pm55，全不相交)；hidden B2=specs_B2.json(跨输入 vin3.3/vout1.8/vref0.9/iload50mA)。A/B/B2 vout/vref 全不相交→R1/R2 比 0.5/0.6/1.0 全不同；spec.md 数值随输入变；Vdd 源值随 vin 变(反硬编码三轴)。金标 gen_ldo_design_ref.py：_scale(SPICE 后缀)+_fmt(%.6g 无后缀)+gen_dut/tb_ac/tb_psrr/tb_linereg/tb_loadreg/gen_spec_md。check.py：解 zip(防泄漏)→py_compile→B 真跑 subprocess→dut subckt 端口+R1/R2 比(2% 容差)→tb_ac .AC+.measure gain/pm→tb_psrr Vdd AC+.measure PSRR→tb_linereg .DC Vdd→tb_loadreg .DC Iload+.measure→spec.md 7 值数值匹配→B2 跨输入 spec.md Vout+R1/R2 比→B Vdd==vin→3 次确定性 sha256。自验：ref PASS(16 a-p 全)+4 negatives(empty/hardcode_a/no_divider/no_ac)全 FAIL+§4.9 三假(empty/print_expected/ref_core_deleted)全 FAIL+3 次确定性 sha256 一致(3a1d4d304f8150d5)。**断言闸门** k_rationale=k_check=16 ✓。**教训**：(1) cline editor 工具用 {path,new_text,old_text,insert_line} 增量编辑(非 write_to_file)，深读提产物内容需按序应用 edit 链或看 cat 输出；本轮取 user turns+产物名+U#0 specs 即足合成；(2) shard D 池 high-mc(>100) 仍 skill/live/Q&A/TCAD-MCP 主导，clean 离线可验 produce 密度低；LDO「指标→SPICE deck 生成」是 analog_context L1 可验好范式(结构+规格驱动分压比天然 16 条件)；(3) 生成类任务用「隐藏 B 换规格」反硬编码可行；(4) .subckt 端口名与 R1/R2 命名须在 prompt 固定，否则结构断言无法确定性比对。下轮 #329：fresh_D319_avail 剩 ~120 真 fresh 未 peek；或 refresh 候选池/放宽 mc 15-30。
- (归档批次 2032) 历史 #327 ShortCfgTrace-001 选料/合成流水已搬 MEMORY_D_archive.md
- ⚠️ **关键发现（cline 存储变更）**：cline session 存储现为**目录式** `/home/<user>/.cline/data/sessions/<sid>/<sid>.messages.json`（非根目录 `<sid>.messages.json`）。messages.json 格式 = `{"version":1, ..., "messages":[{"role":"user","content":[{"type":"text","text":"<user_input mode=\"act\">..."}]}]}`（content 是 list，非 str）。旧 peek 脚本（peek_211/216/218/D313/D316）用根目录路径，现在会全部 NO_FILE。**已写修正版 designflow/peek_dirbased.py**（目录路径 + 解析 data["messages"] + content list）供下轮复用。下轮 peek 必须用此版。
- ⚠️ **选料去重 bug 修复**：fresh_D306_pool.tsv 是 #306 时构建的快照，之后台账增长（#314-316 claim 了 cq860/4ne3u/9p8g2 等），这些 session 仍在旧 pool 里。`comm -23 pool_sids peeked_sids` 只排已 peek，**漏排已入台账的**→会重选已做 case（本轮误把 cq860 当 fresh，claim 时 REFUSED 才发现已是 #314）。**正确口径**：fresh_avail = pool_sids − peeked_sids − ledger_sids（已存 designflow/fresh_D317_avail.tsv，176 行）。下轮直接用此文件。

- (归档批次 63) 历史 #268 CellPrefixExtract-001 选料流水已搬 MEMORY_D_archive.md
- 每轮做 1 条 case：trace_ledger.py --shard D next → claim → 深读 → 合成 → 自验 → 追加 EDA-Eval-DesignFlow_D.jsonl → 日报
- ⚠️ **台账/排除集修复**：trace_ledger.py `next` 生成的 awk 排除集有 digit 转写 bug（如 `1790142103120_n91pk` 实际应为 `1790142100320_n91pk`），且 excl 条目带 `.messages.json` 后缀而 summary.tsv session_file 也带后缀、awk `sub` 剥后缀后两边不匹配 → 已交付 session(n91pk/wg5u2/wb03t/4a852) 漏排重返候选池。**本轮改用 4-shard TSV 实读 262-anchor 排除集 + awk BEGIN 对 excl 也 `sub(/\.messages\.json$/,"")` 双边剥后缀**（designflow/_tmp/excl_all.txt，运行后清理），得真 fresh 候选。建议运维修 trace_ledger.py：(1) anchor 从 TSV 直读勿二次转写；(2) 排除匹配双边剥 `.messages.json`。
- 📊 trace 覆盖率：164 / 1511 = 10.9%（mc>=30 候选池；D.tsv 现 164 case-mark + 890 parked · 已动过 1054；快照 2026-11-06 08:40 sessions=3896）。已覆盖 domain（D.jsonl 165 行）：analog_context:36 · schematic_netlist:92 · waveform:37。⚠️ **#328 选料**：fresh_D319_avail.tsv(144) 排除 ledger → 133 真 fresh；本机无法直 ssh 698 机(网络隔离)，改在 .75 workdir 跑 peek_D328.py(目录式 cline 存储)。peek 20 候选(batch1 mc68-103 + batch2 mc115-184)：多为 skill搭建/live pyaether/Q&A/TCAD-MCP开发/digital UPF/DRC-log(非D域)/玩耍。**决策**：选 z5ett(jessegao mc137 aether:512 transistor:224 netlist:129)★★=LDO 设计+SPICE 测试台生成做 **B 档 synthesized**(U#0 纯指标驱动 produce，live pyaether+PDK 不可附加)。下轮 #329：fresh_D319_avail 剩 ~120 真 fresh 未 peek；或 refresh 候选池/放宽 mc 15-30。
- 📦 体积：TASK_D≈26KB / MEMORY_D≈27KB（归档批次 2033 后；低于 32KB 红线）
- DEBT: 0（#328 已交付 LdoTbGen-001；#327/#326/#325/#324/#323/#322/#321/#320/#319/#318 已交付）
- 🧾 断言: k_rationale=k_check=16 ✓（本轮 #328 LdoTbGen-001 16 条断言 ①-⑯ 对应 check a-p 全；#327 ShortCfgTrace-001 16 条；#326 SpfTriggerMonitor-001 16 条；#325 PatternParamAudit-001 16 条；#324 NetlistFightX-001 16 条；#323 OtaSimReport-001 16 条；#322 VcdEdgeTraceZ-001 16 条；#321 CellRemapInvBase-001 16 条；#320 PatternVDepResolver-001 16 条；#319 SpfDiffCompare-001 16 条；#318 MeasStmtExtract-001 16 条；#315 FmInstFreq-001 16 条；#314 DlygResInsert-001 16 条；#313 NetlistSigRename-001 16 条；#312 NetlistHierFlowchart-001 16 条；#311 CdlXistorAudit-001 16 条；#310 NetlistCellReplace-001 16 条；#309 NetlistGate2Verilog-001 16 条；#308 CellRewriteSimlib-001 16 条；#307 OpCornerSummary-001 15 条；#306 FarthestCellPick-001 14 条；#305 SpStimLoopAudit-001 16 条；#304 SimReportPvtSummary-001 15 条；#303 WaveMaxFind-001 15 条；#302 SpTestbenchParamFix-001 14 条；#301 NetlistMMultAudit-001 16 条；#299 SineZeroCrossFreqPeak-001 16 条；#298 InvPulseStimTb-001 14 条；#297 SpiceldViewChg-001 14 条；#296 FinesimIgnoreGen-001 14 条；#295 CosimStimFolderGen-001 14 条；#294 CellExpandGen-001 14 条；#293 SchFixFloating-001 14 条）。shard D 存量 163 条 test_rationale 全部以 `k 条断言：①…` 开头已核验达标。今日 118/163 达标。rewrite_queue.tsv 全部 done（无待修）。

## 流水
- 2026-11-07 00:4x | shard D #328 | **交付 LdoTbGen-001（analog_context, track=synthesized B-grade, L1 真跑候选, 16 条件 a-p）**。open_session shardD_20261107_shardD-328_0。**选料**：fresh_D319_avail.tsv(144) 排除 ledger → 133 真 fresh；本机无法直 ssh 698 机(网络隔离)→ 在 .75 workdir 跑 peek_D328.py(目录式 cline 存储 `<sid>/<sid>.messages.json` + 解析 data["messages"] content list)。peek batch1(10 候选 mc 68-103: xyj1z/sr426/phgjl/y2xz6/u29lu/9pcjd/vhz0j/htwv2/50mu7/hpd7c) + batch2(10 候选 mc 115-184: 41sqh/wiglh/n52mz/j90k2/1488k/o4frj/o5o6p/z5ett/5vmvu/4ys8e)。**triage**：xyj1z/n52mz=NO_FILE·sr426=verilog .trn 波形读+netlist fight 分析(live simvision 不可离线)·phgjl=nturns0·y2xz6/u29lu/41sqh/wiglh=skill 搭建(run-regression/simdiag-cli/RAG demo)·9pcjd=autocell security rep(live /apps+/proj)·vhz0j=calibreDRC.rule 逐条 Q&A·htwv2=LVS rule 拆解 Q&A(0 edits)·50mu7=Spice_Agent skill 加载·hpd7c=Totem-SC 源码包更新(代码转录非 EDA)·j90k2="give me EDA image"+bsub test(玩耍)·1488k=Sentaurus TCAD MCP 开发(软件工程非 D 域)·o4frj=DRC log rule-time 解析(physical_verify 非 D 域,但 clean 转换)·o5o6p=VCLP UPF 低功耗 flow(digital 非 D)·5vmvu=SKILL .il 脚本改(live OA)·4ys8e=DFM SPEC FILL(live calibre)。**决策**：选 **z5ett(jessegao mc137 aether:512 transistor:224 netlist:129)★★=LDO 设计+SPICE 测试台生成**(U#0 逐字「帮我生成一个LDO电路上电压域为1.1V，输出为0.9V，要求其静态功耗10uA以内，PSRR=-20dB @0~100kHz，DC gain大于40db，PHASE MARGIN 大于40度」+U#1 澄清「psrr为负值」+U#2/3「输出电路图及验证报告」；agent 51 editor 写入产 dut_ldo_v1.sp + tb_ac/tb_psrr/tb_linereg/tb_loadreg.sp + spec.md + reports，经 Spice_Agent/aether live 流)。**深读**：scp z5ett.json(1MB,233 msgs,9 user turns) 经 .75 ssh 10.129.2.14(cat)→extract_z5ett.py 提全 user turns + assistant editor 产物文件名。**A-faithful 决策**：U#0 纯指标驱动 produce 未给根因(A 合规)，但 live pyaether+PDK 不可附加 → **B 档 synthesized**。**合成**：配置驱动 LDO 设计+测试台生成器 gen_ldo_design.py(--specs <specs.json> --outdir <dir>)：读 8 字段(vin/vout/vref/iload/iq_max/psrr_db/dc_gain_db/pm_deg)，emit dut.sp(.subckt ldo vdd vout gnd + PMOS pass + VCVS 误差放大 + **R1/R2 反馈分压 R1/R2=vout/vref-1** + Vref + Cc + Rq) + 4 测试台(tb_ac .AC+.measure gain/pm；tb_psrr Vdd AC 注入+.measure PSRR；tb_linereg .DC Vdd；tb_loadreg .DC Iload+.measure) + spec.md(7 label:value: Vin/Vout/Vref/Iload/Iq_max/PSRR/DC_gain/PM)。A=specs_A.json(真实 vin1.1/vout0.9/vref0.6/iload10mA/iq10uA/psrr-20/gain40/pm40)；hidden B=specs_B.json(vin1.2/vout0.8/vref0.5/iload20mA/iq5uA/psrr-30/gain50/pm55，全不相交)；hidden B2=specs_B2.json(跨输入 vin3.3/vout1.8/vref0.9/iload50mA，更大电压域)。A/B/B2 vout/vref 全不相交→R1/R2 比 0.5/0.6/1.0 全不同；spec.md 数值随输入变；Vdd 源值随 vin 变(反硬编码三轴)。金标 gen_ldo_design_ref.py：_scale(SPICE 后缀 k/m/u/n/p/f/meg/g)+_fmt(%.6g 无后缀)+gen_dut/tb_ac/tb_psrr/tb_linereg/tb_loadreg/gen_spec_md。check.py：解 zip(防 check/ref/negative/.jsonl 泄漏)→py_compile→B 真跑 subprocess→dut subckt 端口 vdd/vout/gnd+R1/R2 比(2% 容差)==vout/vref-1→tb_ac .AC+.measure gain/pm→tb_psrr Vdd AC+.measure PSRR→tb_linereg .DC Vdd→tb_loadreg .DC Iload+.measure→spec.md 7 值数值匹配(1% 容差)→B2 跨输入 spec.md Vout+R1/R2 比→B 某测试台 Vdd==vin→3 次确定性 sha256 16 条 a-p。自验：ref PASS(16 a-p 全)+4 negatives(empty/hardcode_a/no_divider/no_ac)全 FAIL+§4.9 三假(empty/print_expected/ref_core_deleted)全 FAIL+3 次确定性 sha256 一致(3a1d4d304f8150d5)。**断言闸门** k_rationale=k_check=16 ✓。**教训**：(1) cline editor 工具用 {path,new_text,old_text,insert_line} 增量编辑(非 write_to_file)，深读提产物内容需按序应用 edit 链或看 cat 输出；本轮取 user turns+产物名+U#0 specs 即足合成；(2) shard D 池 high-mc(>100) 仍 skill/live/Q&A/TCAD-MCP 主导，clean 离线可验 produce 密度低；LDO「指标→SPICE deck 生成」是 analog_context L1 可验好范式(结构+规格驱动分压比天然 16 条件)；(3) 生成类任务用「隐藏 B 换规格」反硬编码可行：判分跑候选生成器于 B/B2 specs，校验分压比与 spec.md 数值随输入变；(4) .subckt 端口名与 R1/R2 命名须在 prompt 固定，否则结构断言无法确定性比对。台账 mark z5ett→case；analog_context 35→36；D.jsonl 164→165。
- (归档批次 2033) 流水 #327 (ShortCfgTrace-001) 已搬 MEMORY_D_archive.md
- (归档批次 2032) 流水 #326 (SpfTriggerMonitor-001) 已搬 MEMORY_D_archive.md
- (归档批次 2030) 流水 #318 已搬 MEMORY_D_archive.md
- (归档批次 2030) 流水 #319 已搬 MEMORY_D_archive.md
- (归档批次 2030) 流水 #320 已搬 MEMORY_D_archive.md
- (归档批次 2030) 流水 #321 已搬 MEMORY_D_archive.md
- (归档批次 2030) 流水 #322 已搬 MEMORY_D_archive.md
- (归档批次 2033) 流水 #323 (OtaSimReport-001) 已搬 MEMORY_D_archive.md
- 2026-11-06 18:4x-19:0x | shard D #317 | **选料/peek 轮（无 case 交付，DEBT:1）**。open_session shardD_20261106_shardD-pick317。**选料**：fresh_D306_pool.tsv(262) 经 `comm pool−peeked−ledger` 得 fresh_D317_avail.tsv(176 真 fresh)。**关键发现**：cline 存储改目录式 `<sid>/<sid>.messages.json` + messages.json 格式 `{"messages":[{"role":"user","content":[{"type":"text","text":"<user_input mode=\"act\">..."}]}]}`（content 是 list）；旧 peek 脚本用根目录路径现在全 NO_FILE。写 peek_D317_v3.py/peek2.py（目录路径+解析 data["messages"]）在 .75 上跑。**peek 17 候选**（mc 30-80，shard D 域）：hi28t(alanji)=UI how-to 找选项·hojhc(aocao)=仿真提速 debug(U#1 给根因+修复)·ku6wp(kevin3d)=「文件怎么用」Q&A·tjzn5(tongfanl)=研究环境/检查文件 Q&A·5u4s2(e0025730)=业务场景 模拟电路生成 /lvlshft(skill 触发需 live pyaether)·ew6gi(rongjiez)=debug pyaether 报错·krjo2(lizwen)=打pin报错 debug·97g9m(e0039602)=分析 fsdb 信号·0h1pb(chengk)=读代码给流程图 analysis·cq860(thomasz)=★clean produce(写 test.py 插 R_mid/R_out 到 .ends 前)但**已是 #314 DlygResInsert**·4ne3u(e0023936)=★clean produce(Tcl ACE FM 瞬时频率)但**已是 #315 FmInstFreq**·ziv3j/ku6wp 等 nturns=0 经全文件重读仍 Q&A。**结论**：中等 mc(30-80)池 Q&A/debug/analysis 占主导，clean produce 已被 #314-316 取走。**下轮**：用 designflow/peek_dirbased.py 批量 peek fresh_D317_avail.tsv 剩余 ~159 候选（schematic_netlist/waveform/analog 域优先），找 clean A-faithful produce 交付。**教训**：(1) cline 存储目录化——peek 必须用 `<sid>/<sid>.messages.json` 路径 + 解析 `data["messages"]` 的 content list；(2) 选料去重必须 `pool−peeked−ledger` 三集相减，仅 `−peeked` 会重选已做 case；(3) 中等 mc 池 produce 密度低，下轮可放宽到 mc 15-30（shard A 已放宽先例）或 peek 更高 mc(80-150) 大 trace 的早期 produce 轮。脚本已存 designflow/peek_dirbased.py + designflow/fresh_D317_avail.tsv。
- 2026-11-06 18:3x | shard D #316 | **交付 ToggleCounterBindGen-001（schematic_netlist, track=faithful A-grade, L1 真跑候选, 16 条件 a-p）**。open_session shardD_20261106_shardD-pick316。**选料**：fresh_D306_pool.tsv(262 fresh) rank 206-262 共 57 候选未 peek → 写 peek_D316.py（57 targets，max_workers=20 并发 ssh 从 .75 到各机）→ 本机直 ssh 全超时(网络隔离)→改在 .75 上跑 peek_D316.py（.75 免密到 697/698）成功 329 行 peek_out。逐条审 57 候选 A-faithful produce-task：多数为诊断/Q&A/教学/analysis（pcb1x=skill 抓 Pin List 但需 live Virtuoso·k3qx4=高亮 net·9p8g2★=python 脚本生成 toggle_counter.sv·y9y0f=重跑 finesim 需真工具·bgrlw=读网表非 produce·a6f6r=说明 tcl 逻辑非 produce）。**clean A-faithful produce + 离线可验 = 9p8g2**★(clwang@10.129.2.14 mc31, schematic:110 pyaether:25)。**深读 9p8g2**：scp msgs.json(3.4MB) 到 .75 workdir → deepread.py 提取 user turns + assistant tools。**U#0 逐字**(唯一 A-faithful produce)「输入件目录是/home/clwang/test；编写一个python脚本，通过bind的方式，对文件cellname中的cell的输入输出信号添加信号翻转计数，具体的cell定义在cell_define.sv文件中，自己定义一个统计信号翻转的module，把定义的moudle和bind代码放在一个文件,文件名叫toggle_counter.sv」(纯提需求未给根因/修复→A-faithful)。U#91「修改了输入件，请重新执行」为细化非 produce。agent 受 policy-engine writableRoots 限制逐块 editor 写 add_toggle_counter.py + toggle_counter.sv，多次 search_codebase 30s 超时靠 read_file 分段读 cell_define.sv。**user-accepted 产物**(U#104)：`module toggle_counter_<cell>(input A, input Y,...); logic [31:0] cnt_A; always @(A) cnt_A<=cnt_A+32'd1; ... endmodule` + `bind <cell> toggle_counter_<cell> u_<cell> (.A(A),.Y(Y));`；input/output 端口都监测(输出作 counter 的 input)，inout/电源轨排除，32-bit 计数器。**真实输入**：cellname.sv(最终 invx1/nand2Lx1/oai21GFx3 3 cells) + cell_define.sv(真实 8711 行非 ANSI 库)。**合成**：trace 有 user-accepted 产物→A-faithful；真实 /home/clwang/test 不可附加→assets 用真实 cell_define 子集(extract_A.py 抽 7 真实 module 含 3 targets+4 distractors, 277 行)+真实 cellname，hidden B/B2 合成不同 cells。**hidden B**：bufx1/nand3Px1/oai22x/mux2busx(含总线 [3:0] D0/D1/Y + 电源 vdd/gnd)。**hidden B2**：invxZ/and2x/nor2Qx + cellname 含 notexistX(缺失 cell 测优雅跳过)。**反硬编码三轴**：A/B/B2 cell 名完全不相交 + B 含总线端口测范围处理 + B2 含缺失 cell 测鲁棒性。金标 add_toggle_counter_ref.py：argparse(--celldef cell_define.sv / --celllist cellname[→.sv] / --output toggle_counter.sv)；parse_design(非 ANSI：module 名 + body input/output/inout 行 + 端口名/范围/方向)；monitored 仅 input+output；gen_counter_module(input decl + logic[31:0] cnt_ + always@(p) cnt<=cnt+32'd1) + gen_bind(.p(p))；缺失 cell stderr 警告不崩。**16 条件 a-p**：a zip 含.py 无禁 import/路径 b py_compile c B-run exit0+非空 d B 每 cell 有 module toggle_counter_<cell> e B 每 cell 有 bind f B 计入所有 input(cnt+always@) g B 计入所有 output h B inout/电源不计数 i B bind 连每个信号(.p(p)) j B 总线范围保留(mux2busx [3:0]) k 反硬编码 A:源码无 A cell 名+A-run 产 invx1(A,Y)+bind l 跨输入 B2:产 invxZ/and2x/nor2Qx 正确端口 m 缺失 cell 优雅(B2 notexistX 跳过不崩) n 确定性 3 次重跑 sha256 一致 o 计数器递增(cnt<=cnt+) p 单文件含 module+bind。**自验**：ref PASS 16/16；10 negative 全 FAIL(empty_shell/syntax_err/print_expected_B/hardcode_a/no_inout_filter/output_not_counted/no_bind/no_increment/nondeterministic/ref_core_deleted)NEG_RC=0 NEG_SELFTEST PASS；§4.9 三假{empty_shell,print_expected_B,ref_core_deleted}全 FAIL；确定性 3 次 PASS；test==disk sha 1524d87aed36be42 GATE PASS k=16。台账 mark 9p8g2→case；schematic_netlist 83→84；D.jsonl 153→154。**教训**：(1) **本机不能直 ssh 698 机**（网络隔离全超时）→ peek/深读脚本必须经 .75 中转（.75 免密到 697/698）；(2) **9p8g2 是干净 A-faithful + 离线可验好范式**：python 生成器读 cell 库→emit SV，纯文件 in/out，真跑候选只需 python3 subprocess，无需 EDA 工具；(3) **非 ANSI cell 库解析**（module header 列端口名 + body input/output/inout 行带方向/范围）是核心难度，naive 正则易漏范围/方向；(4) **反硬编码靠 A/B/B2 cell 名不相交 + B 总线 + B2 缺失 cell**，硬编 A 输出者 B 上 d/e/j FAIL，不处理缺失 cell 者 m FAIL；(5) **bind-based toggle counter**（input/output 都监测、inout 排除）是 schematic_netlist L1 可验好范式，16 条件天然丰富。**下一步**：fresh_D306 pool rank 206-262 已 peek 完，下轮需 trace_ledger refresh 生成新 fresh 池再 peek。
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
