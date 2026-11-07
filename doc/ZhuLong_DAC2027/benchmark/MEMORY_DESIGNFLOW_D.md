WAITING: 0
SHARD: D (netlist_wave)
DOMAINS: analog_context, schematic_netlist, waveform
DEBT: 1（#346 选料/深读轮：194wf 已 claim+深读完成未合成；⚠️ L1/L2 比例债仍存，AnalogGroupRoleInfer 亦 L1，#347 合成后继续优先 L2/L3）

- **PHASE**: shard D 运行中。已交付 177 条 case（D.jsonl 177 行：analog_context:43/schematic_netlist:96/waveform:38）；台账 case-mark 175 + 1015 parked = 1190 已动过。**本轮 #346 = 选料/深读轮（DEBT:1，无 case 交付）**：194wf(ziyuny/mc128 AnaWeave VwlpRefAmpIP)已 claim+深读完成，留 #347 合成 EDA-Eval-DesignFlow-AnalogGroupRoleInfer-001。fresh 池 mc≥30 顶部 ~25 候选已全部 peek，clean L2 produce 稀缺；9 weak/dup 候选已 parked（t2hnp=dup NetHighlightProbe-001 / sr426=dup NetlistFightX-001 / iz828/7kyrv/vpj8o/5vmvu/vbxlf/kxqt7/mrlo9）。深读笔记 designflow/trace_deepreads/194wf_anaweave_grouprole.md（含完整真实电路提取：14 device+4 group+12 net + 合成 plan + 16 条件 a-p + k 断言）。**上轮 #345 = 交付 EDA-Eval-DesignFlow-FineSimDeckReport-001**（analog_context, lp4xw/clarawang mc77, B-grade synthesized **L1**, 16 条件 a-p；FineSim .inp deck 结构解析器→parsed.json+analysis.txt）。trace 逐字 U#1 "please help me analysis this file si.inp"(附 si.inp 7.8KB) + U#3 "please help me create a file analysis.txt for up detail answer"。A-faithful 不可移植(sim 输出 elog/compare.rep 在 /rundata 不可附加 + 中文乱码反复修正)，故 B 级合成：gen_finesim_deck_report.py --deck/--outdir 解析 FineSim deck(*注释/.title/.option/.lib/.temp/.volt/.param zq_pu/zq_pd/.option ignore/.include switch/.vec/* phaseN:/.meas/* signal compare)→ parsed.json(28 顶层键)+analysis.txt(12 章节)。A=si_A.inp(DRPCA DDR5 X8 SS 0.94V -40C 20fields 10params zq100111/101011 27ignored switch_NORMAL+switch_TSV 7phases 14/16 match[TDQ0,TDQ3] crc+accurate)；hidden B=si_B.inp(LPDDR4X X16 FF 1.3V -40C 20fields 10params zq011010/110101 20ignored switch_NORMAL 6phases 12/16 match[TDQ2,TDQ4])；hidden B2=si_B2.inp(GDDR6 X16 TT 0.92V 25C 15fields 6params zq101010/010101 6ignored switch_NORMAL 4phases 8/8 match[] 无crc/accurate)。反硬编码轴：A/B/B2 project/corner/volt/temp/zq/ignored/switch/phases/fields 全不同；B2 无 crc_alert+accurate；源码禁 A 字面量(Compress018/DRCPA/0.94/100111/switch_TSV/T_0.L.L0/B19BJ/NODLLK/10nm_G5 等)；A GT 出 B 范围；3x sha256 确定性。check 16 条件 a-p(zip 防泄漏/py_compile/B-run exit0+2文件/必需键/source_tool==FineSim/regression_name==B.title/n_fields==20/options mixed_mode+spicehd+prohd+crc_alert/corner FF+volt 1.3+temp -40/n_params==10+参数名集/zq pu=011010+pd=110101/n_ignored==20+集匹配/switch==[NORMAL]/n_phases==6/反硬编码源码无A字面量+A-run Compress018/跨输入B2 n_fields15+TT+crc False+n_phases4+3x确定性)。自验：ref PASS 16/16 + 6 negatives 全 FAIL(empty→c/hardcode_a→f/print→c/ref_deleted→d/naive→h/drop_b2→p, 5 distinct first_fail) + §4.9 三假全 FAIL。**断言闸门** k_rationale=k_check=16 ✓。⚠️ **L1/L2 比例债**：本条 L1(原希望 L2 还债，但 fresh 池 peek 14 候选 clean L2 produce 稀缺，rscalc RTEXT 适合 L2 但属 shard C physical_verify 域不强抢)；下轮继续优先 L2/L3。台账 case-mark 174→175 + parked 997→1006 = 1181；analog_context 42→43；D.jsonl 176→177。**#344 = 交付 IOBufParamTune-001**（已归档批次 2046）。**#343 = 选料轮**（已归档）。**#342 = 选料轮**（已归档）。**#341 = 交付 AnalogGroupCfgMergeDummy-001**（已归档）。
- (归档批次 2032) 历史 #327 ShortCfgTrace-001 选料/合成流水已搬 MEMORY_D_archive.md
- ⚠️ **关键发现（cline 存储变更）**：cline session 存储现为**目录式** `/home/<user>/.cline/data/sessions/<sid>/<sid>.messages.json`（非根目录 `<sid>.messages.json`）。messages.json 格式 = `{"version":1, ..., "messages":[{"role":"user","content":[{"type":"text","text":"<user_input mode=\"act\">..."}]}]}`（content 是 list，非 str）。旧 peek 脚本（peek_211/216/218/D313/D316）用根目录路径，现在会全部 NO_FILE。**已写修正版 designflow/peek_dirbased.py**（目录路径 + 解析 data["messages"] + content list）供下轮复用。下轮 peek 必须用此版。
- ⚠️ **选料去重 bug 修复**：fresh_D306_pool.tsv 是 #306 时构建的快照，之后台账增长（#314-316 claim 了 cq860/4ne3u/9p8g2 等），这些 session 仍在旧 pool 里。`comm -23 pool_sids peeked_sids` 只排已 peek，**漏排已入台账的**→会重选已做 case（本轮误把 cq860 当 fresh，claim 时 REFUSED 才发现已是 #314）。**正确口径**：fresh_avail = pool_sids − peeked_sids − ledger_sids（已存 designflow/fresh_D317_avail.tsv，176 行）。下轮直接用此文件。

- (归档批次 63) 历史 #268 CellPrefixExtract-001 选料流水已搬 MEMORY_D_archive.md
- 每轮做 1 条 case：trace_ledger.py --shard D next → claim → 深读 → 合成 → 自验 → 追加 EDA-Eval-DesignFlow_D.jsonl → 日报
- ⚠️ **台账/排除集修复**：trace_ledger.py `next` 生成的 awk 排除集有 digit 转写 bug（如 `1790142103120_n91pk` 实际应为 `1790142100320_n91pk`），且 excl 条目带 `.messages.json` 后缀而 summary.tsv session_file 也带后缀、awk `sub` 剥后缀后两边不匹配 → 已交付 session(n91pk/wg5u2/wb03t/4a852) 漏排重返候选池。**本轮改用 4-shard TSV 实读 262-anchor 排除集 + awk BEGIN 对 excl 也 `sub(/\.messages\.json$/,"")` 双边剥后缀**（designflow/_tmp/excl_all.txt，运行后清理），得真 fresh 候选。建议运维修 trace_ledger.py：(1) anchor 从 TSV 直读勿二次转写；(2) 排除匹配双边剥 `.messages.json`。
- 📊 trace 覆盖率：175 / 1511 = 11.6%（mc>=30 候选池；D.tsv 现 175 case-mark + 1015 parked · 已动过 1190；快照 2026-11-07 04:52 sessions=3896 mc300=347 mc500=281 mc1000=8）。已覆盖 domain（D.jsonl 177 行）：analog_context:43 · schematic_netlist:96 · waveform:38。**#346**：194wf→(claimed, 待 #347 合成 AnalogGroupRoleInfer-001)（选料/深读轮 DEBT:1）。**#345**：lp4xw→EDA-Eval-DesignFlow-FineSimDeckReport-001（已归档）。**#344**：l5r0u→IOBufParamTune-001（已归档）。**#343/#342**：选料轮（已归档）。**#341**：ca92c→AnalogGroupCfgMergeDummy-001（已归档）。
- 📦 体积：TASK_D≈25KB / MEMORY_D≈34KB（#346 PHASE 更新 + #345 PHASE 改"上轮"；⚠️ 仍略超 32KB 红线，#347 须归档 #340 及更早流水到 MEMORY_D_archive.md）
- DEBT: 1（#346 选料/深读轮：194wf 深读完成未合成；⚠️ L1/L2 比例债仍存，AnalogGroupRoleInfer 亦 L1，#347 合成后继续优先 L2/L3）。**下轮 #347 第一件事**：复用 194wf_anaweave_grouprole.md 深读 → 合成 AnalogGroupRoleInfer-001（gen_group_role_infer.py + A=VwlpRefAmpIP网表/B=Miller opamp/B2=folded cascode + check 16 条件 a-p + 5 negatives）→ 自验 → 追加 D.jsonl → mark 194wf case → 还 DEBT。
- 🧾 断言: k_rationale=k_check=16 ✓（#345 FineSimDeckReport-001，16 条件 a-p 全对账；#346 已写 194wf 的 16 条断言清单于 deepread，待 #347 合成时对账）。存量 177 条 test_rationale 全部以 `k 条断言：①…` 开头已核验达标。rewrite_queue.tsv 全部 done（无待修）。今日 129/177 达标（#346 无新 case）。

## 流水
- 2026-11-07 09:3x | shard D #346 | **选料/深读轮（DEBT:1，无 case 交付）**。open_session default_designflow_shardD_shardD-346-peek_0（peek 用，已 declare_done+close）。**选料**：fresh_D317_avail(mc≥30) 顶部 ~25 候选已全部 peek（#341 已 park 11 条 + 本轮新 peek 13 条）。本轮 .75 ssh 并发 scp 目录式 messages.json peek 13 候选：mrlo9(VAMAgent 1turn weak)/ajcab(=parked #341)/vbxlf(run-regression skill-opt weak)/kxqt7(shard C DRC)/5vmvu(skill-edit multi-turn)/iz828(hierarchy-jump Q&A 32 RAG weak)/t2hnp(★dup NetHighlightProbe-001)/n52m2(NO_FILE ssh fail)/194wf(★AnaWeave VwlpRefAmpIP 电路分析)/7kyrv(synopsys ddr6_model build wrong-domain)/sr426(★dup NetlistFightX-001)/vpj8o(AnaWeave GG exec dup cfg)/o5o6p/27c6f/8zuqr/j90k2(已 parked #341)。**dup 发现**：t2hnp = NetHighlightProbe-001(同任务 highlight nets starting 'net')；sr426 = NetlistFightX-001(同任务 vblh X-fighting debug) — 均已 parked 防 #347 重选。**选 194wf**(ziyuny/mc128 AnaWeave VwlpRefAmpIP layout placement)：真实 produce=版图 placement(live cellview 不可移植)，但 assistant [132]/[134]/[136] 产出的**电路结构分析**可移植(device-by-device role + symmetry group id)。claim→schematic_netlist。**真实电路完整提取**：VwlpRefAmpIP=带使能门控单端差分 OTA。CP0(尾电流:MN0/MN1/MNSW1/MNSW3, BiasN/RegEnVdd1/ntail)/DP0(输入对:MN2/MN3+MNPAIR1/MNPAIR2, Pos/Neg/ntail/net2/net3)/CM0(PMOS镜像:MPCUR3 diode+MPCUR4 mirror, pmirror/Out)/dummy(MPDUM=vdd1,MNDUM1=vss,MNDUM2=vss)/MPSW1(pmirror 复位开关)。14 device+4 group+12 net 全表已落 deepread。**A-faithful 不可行**(live cellview)→**B 档 synthesized**：facet=SPICE 网表→模拟单元对称群角色推断器(gen_group_role_infer.py --netlist/--outdir → group_roles.json+report.md)。**合成 plan 落 designflow/trace_deepreads/194wf_anaweave_grouprole.md**：A=VwlpRefAmpIP 网表(trace-faithful 真实名)/hidden B=2-stage Miller opamp(不同结构)/hidden B2=folded cascode(更简无 dummy)。check 16 条件 a-p(zip+py_compile/B-run exit0+2文件/8 顶层键/cell_name/n_groups/n_devices/group 7 字段/type 枚举/match≥2/dummy 全端子同网/mirror 共 gate/diff_pair 共 source/report 节/反硬编码无 A 字面量+A-run cell_name/跨输入 B2 n_groups3+n_dummy0/3x sha256)。k 条断言=16 与 a-p 一一对账。5 negatives。**#347 复用本深读直接合成**。**台账**：claim 194wf→schematic_netlist(in-progress); parked 9 weak/dup(t2hnp/sr426/iz828/7kyrv/vpj8o/5vmvu/vbxlf/kxqt7/mrlo9)。case-mark 175 不变 + parked 1006→1015 = 1190 已动过。D.jsonl 177 不变。**断言闸门**：本轮无 case 交付，k 断言不适用。**教训**：(1) fresh 池 mc≥30 顶部 clean L2 produce 稀疏印证 #317/#332/#345 结论，本轮 peek 13 候选仅 194wf 可用(且为 L1 facet); (2) **dup 检测必做**: t2hnp/sr426 与现有 NetHighlightProbe-001/NetlistFightX-001 任务字面相同，peek 后必 grep D.jsonl 同义 case 名; (3) **trace assistant 电路分析文本是可移植金矿**: 194wf [132]/[134]/[136] 完整给 14 device 连接+角色，可重建 SPICE 网表做 B 档 trace-faithful 输入(即使 read_files tool_result 未捕获); (4) 选料/深读轮 park weak 候选防重选(9 条全 parked); (5) ⚠️ MEMORY_D 仍 34KB 略超 32KB 红线，#347 须归档 #340 及更早流水。
- 2026-11-07 09:1x | shard D #345 | **交付 EDA-Eval-DesignFlow-FineSimDeckReport-001**（analog_context, lp4xw/clarawang/hfeg0pgn045 mc77, B-grade synthesized **L1**, 16 条件 a-p）。open_session default_designflow_shardD_345_shardD-345-peek_0（peek 用，已 declare_done + close）。**选料**：fresh_D317_avail.tsv(mc>=15) 115 fresh 未入台账，按 D-score(netlist/schematic/analog/hspice/waveview/fsdb/cdl/transistor/opamp/mosfet/spectre/spice)排序。.75 ssh 并发 peek 14 候选(peek_D345.py/b/c 经 .75 ssh 目录式 messages.json)：wiglh(run-regression 单轮 weak)/194wf(AnaWeave placement 续接笔记交互)/pepxy(rscalc RTEXT 单轮 produce 但属 shard C physical_verify 域)/xs1lj(NO_FILE)/0oeb7(API delete weak)/hkyyj(OA explore weak)/lp4xw(★FineSim si.inp 分析 produce ✓)/mx7xh(SPICE debug)/e0b5q(单行)/7uwtz(skill launcher)/rbvi8(finesim prof 重复请求 agent 失败)/vtz09(sacap perl 改+用户给根因)/lq00u(coupling debug)/nsf5a(waveview+C++ Qt)/1b60m(删 cell weak)/egm8i(placement)/huntx/uorzd/zh4of(autovia skill 调用)。**选 lp4xw** = 干净 A-faithful 多轮 produce(U#1 "please help me analysis this file si.inp" 附 si.inp 7.8KB + U#3 "please help me create a file analysis.txt for up detail answer") → claim→analog_context。**关键发现**：read_files tool_result 在 messages.json 中未被捕获(len=0)，仅 assistant derived 分析文本(MSG[14]/[16])可重建 si.inp 内容(DRPCA DDR5 X8 SS 0.94V -40C, Compress018 18字段, mixed spicehd/prohd, 10nm G5, 10 params, ZQ PU=100111/PD=101011, 28 ignored banks+B19 risk, switch_NORMAL+switch_TSV, 7 phases, 14/16 match TDQ0/TDQ3)。**A-faithful 不可行**(sim 输出 elog/compare.rep 在 /rundata 不可附加 + 中文乱码反复修正) → **B 级合成**：取 portable facet = FineSim .inp deck 结构解析器。**合成**：gen_finesim_deck_report.py --deck/--outdir 解析 FineSim deck(*注释 project/device/analysis/phaseN:/signal compare:/.title/.option mixed_mode spicehd prohd crc_alert accurate/.option ignore=/.lib corner/.temp/.volt/.param zq_pu/zq_pd/.include switch/.vec/.meas/.end)→ parsed.json(28 顶层键) + analysis.txt(12 章节 Overview/Regression Name Decoding/Sim Options/Process&Models/Key Params/ZQ Calibration/Ignored Subcircuits/Switch Model Design/Stimulus/Measurements/Signal Comparison/Conclusion)。A=si_A.inp(DRPCA DDR5 X8 SS 0.94V -40C 20fields 10params zq100111/101011 27ignored switch_NORMAL+switch_TSV 7phases 14/16 match[TDQ0,TDQ3] crc+accurate)；hidden B=si_B.inp(LPDDR4X X16 FF 1.3V -40C 20fields 10params zq011010/110101 20ignored switch_NORMAL 6phases 12/16 match[TDQ2,TDQ4])；hidden B2=si_B2.inp(GDDR6 X16 TT 0.92V 25C 15fields 6params zq101010/010101 6ignored switch_NORMAL 4phases 8/8 match[] 无 crc/accurate)。反硬编码轴：A/B/B2 project/corner/volt/temp/zq/ignored/switch/phases/fields 全不同；B2 无 crc_alert+accurate(少字段)；源码禁 A 字面量(Compress018/DRCPA/DDR5 X8/0.94/100111/101011/switch_TSV/T_0.L.L0/B19BJ/TDQ0/TDQ3/NODLLK/10nm_G5/Compress timing)；A GT 出 B 范围；3x sha256 确定性。check 16 条件 a-p(zip 防泄漏 leak_pat check.py/reference/negative/jsonl/_tmp_/__chk/py_compile/B-run exit0+2 文件(parsed.json+analysis.txt)/必需 28 顶层键/source_tool==FineSim/regression_name==B.title Refresh004/n_fields==20/options mixed_mode+spicehd+prohd+crc_alert/corner FF+volt 1.3+temp -40/n_params==10+参数名集{pvcc,tdqs2dq,pvwlp,pvtpd,pvtcmd,pvref,pvsstl,pvddq,pvtt,pvstb}/zq pu=011010+pd=110101/n_ignored==20+集匹配 B_IGNORED/switch==[switch_NORMAL.sp]/n_phases==6/反硬编码源码无 A_LITERALS+A-run regression_name Compress018 开头/跨输入 B2 n_fields15+corner TT+crc_alert False+n_phases4+3x sha256 一致)。**自验**：ref PASS 16/16 + 6 negatives 全 FAIL(empty_shell→c / hardcode_a→f / print_expected→c / ref_core_deleted→d / naive_stub→h / drop_b2→p, 5 distinct first_fail c/d/f/h/p) + §4.9 三假(empty/print_expected/ref_core_deleted)全 FAIL + k_rationale=k_check=16 ✓。**教训**：(1) **read_files tool_result 在 messages.json 中未被捕获**——只能从 assistant derived 分析文本重建附件内容，附件元数据只存 path/size 不存 content；(2) **FineSim deck 结构解析是 analog_context L1 可验好范式**：注释/.title/.option/.lib/.temp/.volt/.param/.include/.vec/.meas/signal compare 是 16 条件天然丰富来源(字段数/选项/工艺/参数/ZQ/忽略/开关/相位/测量/比对/反硬编码/跨输入/确定性)，与 FineSimDataParse-001($DATA1 输出块解析)facet 不同无重复；(3) **policy writableRoots + editor 6000 字符限制 + 中文 old_text 匹配失败** 是 cline 写大文件痛点(trace 中 assistant 反复失败)，合成 case 应避开(用 --outdir 一次性写文件)；(4) **rscalc RTEXT/RNODE 任务属 shard C physical_verify 域**——pepxy/92ykp 虽是 clean produce 但不强抢，跨 shard 域尊重；(5) **L1/L2 比例债未还**：fresh 池 peek 14 候选 clean L2 produce 稀缺，下轮继续优先 L2/L3。台账 mark lp4xw→case(FineSimDeckReport-001) + parked 9 weak peeked(pepxy/92ykp/lq00u/mx7xh/e0b5q/rbvi8/nsf5a/egm8i/1b60m)；case-mark 174→175 + parked 997→1006 = 1181；analog_context 42→43；D.jsonl 176→177。深读笔记 designflow/trace_deepreads/lp4xw_finesim_deck.md。**断言闸门** k_rationale=k_check=16 ✓ 通过。
- (归档批次 2046) 流水 #344/#343/#342/#341 已搬 MEMORY_D_archive.md
- (归档批次 2045) 流水 2026-11-07 06:2x #340 NetlistBisectLocalize-001 全文已搬 MEMORY_D_archive.md
- (归档批次 2043) 流水 2026-11-07 #335/#336/#337 已搬 MEMORY_D_archive.md（#335 FineSimDataParse-001 / #336 LdoCircuitReport-001 / #337 选料轮 DEBT:1）
- (归档批次 2044) 流水 2026-11-07 #338 MbistCellFind-001 全文已搬 MEMORY_D_archive.md
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
