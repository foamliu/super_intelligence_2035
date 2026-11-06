WAITING: 0
SHARD: D (netlist_wave)
DOMAINS: analog_context, schematic_netlist, waveform

- **PHASE**: shard D 运行中。已交付 163 条 case（D.jsonl 163 行）；台账 case-mark 162 + 890 parked = 1052 已动过。**本轮 #326 交付 SpfTriggerMonitor-001（B 档 synthesized, analog_context, L1 真跑候选, 16 条件 a-p）**。选料：fresh_D319_avail.tsv(144) 经 pool−peeked−ledger 三集相减（suffix 匹配）得 135 真 fresh，按 mc 排序取 12 netlist/waveform/analog-heavy 候选 → peek_D320_gen.py(通用版) 在 .75 并跑。triage：n52mz=NO_FILE·zm1g8=UI how-to(smash/copy 快捷键 Q&A, nedit0)·nthdn=论文大纲撰写(非 EDA produce)·6sxh5=characterization deck line-by-line Q&A(25 turns)·1giox/qidc2/a9ta2=layout autovia/powerfill 识别+去GUI化(live virtuoso OA 依赖,非 D 域净产出)·1488k=Sentaurus TCAD MCP server 搭建(TCAD 非 EDA-Flow-Bench 域)·5vmvu=portText SKILL 扩展(layout port-text 非 D 域)·wiglh=run-regression skill 触发·ajcab=高亮 schematic line(live pyAether)·**u8kbk(devonma mc66 netlist/analog)★★=FineSim SpfBA 触发文件轮询监听脚本**(U#0 逐字「写个脚本，每隔5分钟检测 Channel 路径下是否存在 Channel.spf.TYP_98_RCC 文件，如果存在，执行 run_fullchip_SpfBA」+U#4「需要两个触发文件都存在，才执行目标脚本」+U#6「两个路径不一样」A-faithful 提需求未给根因；agent 产物 15 shell scripts monitor_and_run_SpfBA{,_fullchip}.sh/check_paths.sh/test_oneshot.sh/verify_syntax.sh：poll-then-fire AND 触发逻辑 5min 间隔 start/finish/exit 日志)。合成决策：真实 /rundata /proj live 路径不可附加 → **B 档 synthesized** 服务用户真实目标(config 驱动轮询监听器, AND over N triggers 不同目录, fire target once, 日志 start/finish/exit-code, exit 0; 未齐 WAITING+sleep 到 max_iter 非零退出)。A=config_A.json(2 触发/2 目录/300s); hidden B=2 触发/2 目录(psd0/psd1) 异名; hidden B2=跨输入 3 触发/3 嵌套目录(ca/dq/dqs) 反硬编码 A。金标 monitor_run_ref.py：json 读 config→all_present AND 检查→subprocess.call target(MARKER_FILE env)→日志 started/finished/exit code 真实 rc→未齐 WAITING+missing 列表+sleep→max_iter sys.exit(10)。check.py：解 zip→py_compile→8 场景(B 全齐/仅 1/仅 2/无/失败 exit7 + B2 全齐/2-3)独立断言 16 条 a-p。自验：ref PASS(16 a-p 全)+5 negatives(empty/print_expected/core_deleted/naive_always_fire/naive_first_only)全 FAIL+§4.9 三假(empty→[d]/print_expected→[d]/core_deleted→[h])全 FAIL+3 次确定性 md5 一致(d05191dc...)。**断言闸门** k_rationale=k_check=16 ✓。下轮 #327：fresh_D319_avail 剩 ~52 候选未 peek；或放宽 mc 15-30 / refresh 候选池。
- ⚠️ **关键发现（cline 存储变更）**：cline session 存储现为**目录式** `/home/<user>/.cline/data/sessions/<sid>/<sid>.messages.json`（非根目录 `<sid>.messages.json`）。messages.json 格式 = `{"version":1, ..., "messages":[{"role":"user","content":[{"type":"text","text":"<user_input mode=\"act\">..."}]}]}`（content 是 list，非 str）。旧 peek 脚本（peek_211/216/218/D313/D316）用根目录路径，现在会全部 NO_FILE。**已写修正版 designflow/peek_dirbased.py**（目录路径 + 解析 data["messages"] + content list）供下轮复用。下轮 peek 必须用此版。
- ⚠️ **选料去重 bug 修复**：fresh_D306_pool.tsv 是 #306 时构建的快照，之后台账增长（#314-316 claim 了 cq860/4ne3u/9p8g2 等），这些 session 仍在旧 pool 里。`comm -23 pool_sids peeked_sids` 只排已 peek，**漏排已入台账的**→会重选已做 case（本轮误把 cq860 当 fresh，claim 时 REFUSED 才发现已是 #314）。**正确口径**：fresh_avail = pool_sids − peeked_sids − ledger_sids（已存 designflow/fresh_D317_avail.tsv，176 行）。下轮直接用此文件。

- (归档批次 63) 历史 #268 CellPrefixExtract-001 选料流水已搬 MEMORY_D_archive.md
- 每轮做 1 条 case：trace_ledger.py --shard D next → claim → 深读 → 合成 → 自验 → 追加 EDA-Eval-DesignFlow_D.jsonl → 日报
- ⚠️ **台账/排除集修复**：trace_ledger.py `next` 生成的 awk 排除集有 digit 转写 bug（如 `1790142103120_n91pk` 实际应为 `1790142100320_n91pk`），且 excl 条目带 `.messages.json` 后缀而 summary.tsv session_file 也带后缀、awk `sub` 剥后缀后两边不匹配 → 已交付 session(n91pk/wg5u2/wb03t/4a852) 漏排重返候选池。**本轮改用 4-shard TSV 实读 262-anchor 排除集 + awk BEGIN 对 excl 也 `sub(/\.messages\.json$/,"")` 双边剥后缀**（designflow/_tmp/excl_all.txt，运行后清理），得真 fresh 候选。建议运维修 trace_ledger.py：(1) anchor 从 TSV 直读勿二次转写；(2) 排除匹配双边剥 `.messages.json`。
- 📊 trace 覆盖率：162 / 1511 = 10.7%（mc>=30 候选池；D.tsv 现 162 case-mark + 890 parked · 已动过 1052；快照 2026-11-06 08:40 sessions=3896）。已覆盖 domain（D.jsonl 163 行）：analog_context:34 · schematic_netlist:90 · waveform:32。⚠️ **#324 选料**：fresh_D319_avail.tsv(144 真 fresh = pool−peeked−ledger) 按域评分取 18 netlist/schematic/spice-heavy 候选，peek_D320_gen.py(通用版) 在 .75 并跑 13。triage：7hpf9=NO_FILE·lmg4r/znyhe=skill 触发(nedit0)·u29lu=Spice_Agent skill 加载·pmnfz=run-regression skill 搭建·be1i0=LVS DECK Q&A·6sxh5=characterization deck line-by-line Q&A·w7un3=续传 device_match 报告(live 依赖)·hpy3y/tadah/3lvd6(jackliu)=读 .trn 波形 debug inh_vblh x 态(106 tool_use, 全 simvision/xvfb, 无干净 netlist 分析产物)·2fb2m(ellawu)★=浮pin port-text SKILL 扩展(A-faithful 但 domain=layout port-text 非 D 域, 弃)。**决策**：选 tadah(jackliu mc87 netlist:118) 做 **B 档 synthesized**——服务用户真实目标(静态网表 fighting/x 态根因分析)，合成离线可验 Python netlist_fight.py。下轮 #325：fresh_D319_avail 剩 ~44 候选未 peek；或放宽 mc 15-30 / refresh 候选池。⚠️ **#322 选料**：fresh_D319_avail.tsv(144 真 fresh) 取未 peek 的 netlist/waveform/analog-heavy 候选，分两批 peek（batch1=18 mc41-162 含 vtl11/wqxag/n1njg/pax7g/se4uf/ckulq/xxtqb/t2hnp/kxqt7/zh4of/92ykp/hkyyj/ca92c/uorzd/1b60m/egm8i/vpj8o/z5ett；batch2=17 mc41-77 含 d3vay/rzitp/97g9m/9lbfz/oh3te/2igp1/wdnwl/h0gyt/c39j4/tjzn5/8o8qn/hojhc/a8164/1bc9r/zw6mx/7xqp9）。**triage**：batch1 多为 live-pyaether/virtuoso/cellview 依赖或 skill 搭建或 AutoCell TCL(live)/NO_FILE(vtl11/92ykp/uorzd)·kxqt7=DRC rule-time 统计(A-faithful 但 domain=physical_verify 非 D 域, 弃)·z5ett/n1njg=LDO 设计(A-faithful 但验 specs 需仿真, L1 静态难度低, 弃)·t2hnp/zh4of=skill 搭建。batch2：rzitp/wdnwl=NO_FILE·97g9m=fsdb 波形分析(A-faithful 但 fsdb 二进制合成难)·8o8qn=verilog 模块查找/avc 对比(依赖真实 /rundata)·**d3vay(pjli mc77 netlist:265)★★=VCD signal edge tracer**(U#3 逐字「只能trace 1或0的沿,如果我想trace z态...把新代码放 Vp1」+U#4「加输入参数从时间t开始检测x/z态」A-faithful 提需求未给根因；agent 产物 signal_edge_tracer.py/trace_signal_fixed.py：parse verilog netlist(named+positional ports)→driver chain 回溯→parse VCD→detect 0/1/z/x 沿 from start t；Python 离线 subprocess 可验)。**决策**：选 d3vay(B 档 synthesized，真实 netlist 119 modules + VCD 依赖真实 simvision.vcd 太大且 live，合成小型 netlist 5 modules + 小型 VCD 含 0/1/z/x 跳变)。**下轮 #323**：fresh_D319_avail 剩 ~60 候选未 peek；或放宽 mc 15-30 / refresh 候选池。
- 📦 体积：TASK_D≈26KB / MEMORY_D≈29KB（归档批次 2030 后；低于 32KB 红线）
- DEBT: 0（#326 已交付 SpfTriggerMonitor-001；#325/#324/#323/#322/#321/#320/#319/#318 已交付）
- 🧾 断言: k_rationale=k_check=16 ✓（本轮 #326 SpfTriggerMonitor-001 16 条断言 ①-⑯ 对应 check a-p 全；#325 PatternParamAudit-001 16 条；#324 NetlistFightX-001 16 条；#323 OtaSimReport-001 16 条；#322 VcdEdgeTraceZ-001 16 条；#321 CellRemapInvBase-001 16 条；#320 PatternVDepResolver-001 16 条；#319 SpfDiffCompare-001 16 条；#318 MeasStmtExtract-001 16 条；#315 FmInstFreq-001 16 条；#314 DlygResInsert-001 16 条；#313 NetlistSigRename-001 16 条；#312 NetlistHierFlowchart-001 16 条；#311 CdlXistorAudit-001 16 条；#310 NetlistCellReplace-001 16 条；#309 NetlistGate2Verilog-001 16 条；#308 CellRewriteSimlib-001 16 条；#307 OpCornerSummary-001 15 条；#306 FarthestCellPick-001 14 条；#305 SpStimLoopAudit-001 16 条；#304 SimReportPvtSummary-001 15 条；#303 WaveMaxFind-001 15 条；#302 SpTestbenchParamFix-001 14 条；#301 NetlistMMultAudit-001 16 条；#299 SineZeroCrossFreqPeak-001 16 条；#298 InvPulseStimTb-001 14 条；#297 SpiceldViewChg-001 14 条；#296 FinesimIgnoreGen-001 14 条；#295 CosimStimFolderGen-001 14 条；#294 CellExpandGen-001 14 条；#293 SchFixFloating-001 14 条）。shard D 存量 161 条 test_rationale 全部以 `k 条断言：①…` 开头已核验达标。今日 116/161 达标。rewrite_queue.tsv 全部 done（无待修）。

## 流水
- 2026-11-07 00:0x | shard D #326 | **交付 SpfTriggerMonitor-001（analog_context, track=synthesized B-grade, L1 真跑候选, 16 条件 a-p）**。open_session shardD_20261106_shardD-326-pick_0。**选料**：fresh_D319_avail.tsv(144) 经 pool−peeked−ledger 三集相减（suffix 匹配）得 135 真 fresh，按 mc 排序取 12 netlist/waveform/analog-heavy 候选(wiglh/1488k/5vmvu/n52mz/6sxh5/1giox/qidc2/nthdn/u8kbk/zm1g8/ajcab/a9ta2) → peek_D320_gen.py(通用版) 在 .75 并跑。**triage**：n52mz=NO_FILE·zm1g8=UI how-to(smash/copy 快捷键 Q&A,nedit0)·nthdn=论文大纲撰写(非 EDA produce)·6sxh5=characterization deck line-by-line Q&A(25 turns)·1giox/qidc2/a9ta2=layout autovia/powerfill 识别+去GUI化(live virtuoso OA 依赖,非 D 域净产出)·1488k=Sentaurus TCAD MCP server 搭建(TCAD 非 EDA-Flow-Bench 域,102 edits)·5vmvu=portText SKILL 扩展(layout port-text 非 D 域)·wiglh=run-regression skill 触发·ajcab=高亮 schematic line(live pyAether)·**u8kbk(devonma mc66)★★=FineSim SpfBA 触发文件轮询监听脚本**(U#0 逐字「写个脚本，每隔5分钟检测 Channel 路径下是否存在 Channel.spf.TYP_98_RCC 文件，如果存在，执行 run_fullchip_SpfBA」+U#4「需要两个触发文件都存在，才执行目标脚本」+U#6「两个路径不一样」A-faithful 提需求未给根因；agent 产物 15 shell scripts monitor_and_run_SpfBA{,_fullchip}.sh/check_paths.sh/test_oneshot.sh/verify_syntax.sh：poll-then-fire AND 触发逻辑 5min 间隔 start/finish/exit 日志)。**深读**：scp u8kbk.json(267KB,106 msgs,8 user turns)→deepread_u8kbk.py 提全 user turns + assistant write produces。**合成决策**：真实 /rundata /proj live 路径不可附加 → **B 档 synthesized** 服务用户真实目标(config 驱动轮询监听器, AND over N triggers 不同目录, fire target once, 日志 start/finish/exit-code, exit 0; 未齐 WAITING+sleep 到 max_iter 非零退出)。A=config_A.json(2 触发 Channel/Array16G_PSD0 /2 目录/300s); hidden B=2 触发(psd0_dir/DQ0 + psd1_dir/DQ1)异名; hidden B2=跨输入 3 触发(ca/nested + dq/nested + dqs/nested)反硬编码 A。金标 monitor_run_ref.py：json 读 config→all_present AND 检查→subprocess.call target(MARKER_FILE env)→日志 started/finished/exit code 真实 rc→未齐 WAITING+missing 列表+sleep→max_iter sys.exit(10)。check.py：解 zip→py_compile→8 场景(B 全齐/仅1/仅2/无/失败 exit7 + B2 全齐/2-3)独立断言 16 条 a-p。自验：ref PASS(16 a-p 全)+5 negatives(empty/print_expected/core_deleted/naive_always_fire/naive_first_only)全 FAIL+§4.9 三假(empty→[d]/print_expected→[d]/core_deleted→[h])全 FAIL+3 次确定性 md5 一致(d05191dc098027a6783332110696f987)。**断言闸门** k_rationale=k_check=16 ✓。**教训**：(1) write 工具路径会落 cwd 基础——务必给绝对全路径，否则可能落 EDA-Flow-Bench 根 reference 下同名目录(本轮误写一次，已 rm 修正)；(2) check.py 内避免对整文件 re.findall `\("([a-z])",` 计条件数(会匹配正文 Assertion 标签)，改用提取 CONDITIONS 块 + assert len 双校验。
- (归档批次 2031) 流水 #324 (NetlistFightX-001) 已搬 MEMORY_D_archive.md
- (归档批次 2030) 流水 #318 已搬 MEMORY_D_archive.md
- (归档批次 2030) 流水 #319 已搬 MEMORY_D_archive.md
- (归档批次 2030) 流水 #320 已搬 MEMORY_D_archive.md
- (归档批次 2030) 流水 #321 已搬 MEMORY_D_archive.md
- (归档批次 2030) 流水 #322 已搬 MEMORY_D_archive.md
- 2026-11-06 22:3x | shard D #323 | **交付 OtaSimReport-001（analog_context, track=faithful A-grade, L1 真跑候选, 16 条件 a-p）**。open_session shardD_20261106_shardD-323-pick_0。**选料**：fresh_D319_avail.tsv(144) 排除已 peek/ledger → 138 真 fresh，按 netlist/waveform/analog domain 评分取 18 候选 → peek_D320_gen.py(通用版) 在 .75 并跑 18 候选。**triage**：ld0p8/27c6f=skill 搭建(lvs-debuger/run-regression)·tze5k/tcqqs/w5knw=SimDiag 项目 live /rundata 依赖·vbxlf=nturns0·d1cg3=Finesim DC 不收敛 Q&A·7kyrv=logic_cosim debug 多轮 find 脚本·5u4s2/qe1va=skill 触发(模拟电路生成/仿真验证)·n1b1u=ERC Q&A·ku6wp="文件怎么用" Q&A·rw6z4/xs1lj=NO_FILE·mrlo9="继续晚餐"续接·7lp3l=strongarm 优化(live FineSim 仿真验 specs)·acdfh=skill 触发+Q&A·**j0t84(zhukaic mc87 aether/hspice/waveview)★★=OTA 仿真报告生成**(U#0 逐字「读取/home/zhukaic/aether_skill/ota_skill/ota_2stg_sim/目录下的数据结果，生成仿真报告到...workspace URL」A-faithful 提需求未给根因；agent 产物 ota_2stg_sim_report.html/md：解析 HSPICE 结果目录→结构化 markdown 报告；Python 离线 subprocess 可验)。**深读**：scp j0t84.json(403KB,1 user turn)+真实数据目录(6 文件 .lis/.ma0/.mt0/.ic0/.pa0/.st0)+golden report.md(4831B)。**U#0 逐字**(唯一 A-faithful produce-demand)。真实数据=两级 OTA PrimeSim HSPICE 前仿(gain 55.78dB/pm 80.72°/gbw 973kHz/22 MOSFET/temp 85C/vcc 1.025V/user zhukaic)。**合成决策**：真实数据文件全可离线文本解析(.lis 含 measures+counts+timing+LSTB, .ma0/.mt0 measure 表, .ic0 节点电压, .pa0 MOS 实例, .st0 license)→**A 档 faithful**：真实 6 数据文件作 asset A(逐字用户原话，不补全意图)；task_brief 只写交付接口(CLI python3 gen_ota_report.py <data_dir> <out_md> + submit.zip)。hidden B 合成全不同值(gain 62.42dB/pm 68.31°/gbw 2.48MHz/28 MOSFET/temp 27C/vcc 1.2V/设计名 ota_5stg_iref/不同节点名 na/nb/nc/nd/不同 counts/不同 user liuwen)。**反硬编码**：A/B 设计名+网名+值全不相交 + 交叉输入护栏(p)禁 A 专属串(55.776/973.293/zhukaic/ota_2stg_sim 等)。金标 gen_ota_report_ref.py：glob 按扩展名找文件(parse_num 带 HSPICE scale k/m/u/n/p/f/g/meg)+parse_ma0/mt0($DATA1 表)+parse_ic0(.nodeset 节点电压)+parse_lis(counts/LSTB/AC/tran measures/timing/memory/元数据)+parse_pa0(MOS 实例计数)+build_report(markdown 6 节)。check.py：解 zip→subprocess 跑候选脚本于 hidden B→num_in_range(兼容 MHz/kHz/Hz 单位)断言 16 条 a-p。**自验**：ref PASS(16 a-p 全)+3 negatives(empty/print_A/no_core)全 FAIL+naive_stub FAIL+NEG_RC=0+§4.9 三假(empty→b/print_A→c-o,p 泄 A 串/no_core→c-o 无值)全 FAIL+3 次判定 md5 一致(确定性)。**断言闸门** k_rationale=k_check=16 ✓。mark ledger case。下轮 #324：fresh_D319_avail 剩 ~120 候选未 peek；或放宽 mc 15-30 / refresh 候选池。
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
