WAITING: 0（#451 交付 AvcPatternCompare-001 · 8o8qn e0014036@hfeg0pkn004 mc=80 · waveform B-grade synthesized L2 k=11 · byte-sync sha aa61ee40 size 7795 · D.jsonl 263→264 · ledger_D case+1。选料：d>=20 d>c D-dominant 池(736 行)经全量 4-shard excl(1917 full+86 suf)+peeked(1725 suf)交叉过滤→736 全 claimed(纠正前轮「top-50 spot check 全 claimed」误判为「全 736 claimed」)。降阈 d>=10 d>c→795 行，全量交叉过滤→78 fresh，top=8o8qn(e0014036 d=253 c=0 mc=80)。深读 8o8qn：e0014036 在 hfeg0pkn004 跑 verilog.ddr6.dscqa.new DDR6 仿真，pteprog 12 个 AVC pattern 文件；任务(1)程序化对比 DA_DDR6_WR_RD_Sim_1017.avc(14506 行/113 pattern)vs DDR6_WR_REF_RD_sim_1016.avc(22274 行)——FORMAT 43 信号相同/bit 级仅 pos1/pos30 字符集不同(1017 固定 0/1,1016 写 X)/pattern 词汇表零重叠/归一化命令签名对比；(2)展平 netlist 搜 I_PPRWDQ30BLOCK→找到 T_PPRWRDQ30Block；(3)解析 PPR Post Package Repair 写路径 DQ 数据存在检测+写驱动使能(子模块 T_PPRWRDQCheck/D_WrDrvonDqmDly_DQ)。私有 /rundata 不可复刻→B-grade synthesized 自包含 AVC 文件+compare_avc.py 结构对比器。A=pattern_A.avc(8 信号 DQ0-DQ7,40 records,10 unique,X@pos2/5) vs 隐藏 B=pattern_B.avc(60 records,12 unique,X@pos2/4) bit_diff=[4,5] shared=0 反硬编码。判分 compare_avc.py 子进程真跑 A-vs-B+11 条 a-k(zip 含+py_compile/B exit0+非空 rep/合法 JSON+15 必键/signal_count=8 names=DQ0-7/format_identical/record_a=40 b=60/unique_a=10 b=12/shared=0 only_a=10 only_b=12/bit_diff=[4,5]/total_lines a=42 b=62/反硬编码 A-vs-A shared=10 only=0 bdiff=[]且≠A-vs-B)。自验 ref PASS 11/11+§4.9 三假(empty/print_only/core_deleted)全 FAIL+2 neg(noop→k/wrong_counts→f)全 FAIL+NEG_RC=0 n_distinct=4+3-seed PASS。byte-sync sha aa61ee40 size 7795。D.jsonl 263→264。🧾 断言: k_rationale=k_check=11 ✓。今日 11-09 新 case 31/31 达标）
- #450 交付 TwoStepOcNetlistAudit-001 · 5i5bo zqzhan@hfeg0pkn002 mc=155 · analog_context B-grade synthesized L2 k=11 · byte-sync sha e9b5cd12 size 7841 · D.jsonl 262→263。DRAM SA 2StepOC 延迟链 netlist 审计器 analyze_2stepoc.py。A=2stepoc_A.sp(TT cap 1/2/4/8f HT=10 LT=5 meas=256) vs B=2stepoc_B.sp(SS cap 2/4/8/16f HT=12 LT=3 meas=128)。自验 ref PASS 11/11 + §4.9 三假全 FAIL + NEG_RC=0 n_distinct=3。
- #449 交付 SaNPTrannoiseFix-001 · cjcn7 ming1w@hfeg0pkn005 mc=164 · waveform B-grade synthesized L2 k=11 · byte-sync sha 13ff90c2 size 9490 · D.jsonl 261→262。FineSim SaNP 瞬态噪声仿真 5 类缺陷修复器 fix_spice.py。自验 ref PASS 11/11 + §4.9 三假全 FAIL + NEG_RC=0 n_distinct=5。
- #447 流水已归档 → designflow/MEMORY_D_archive.md（NetlistBroadcastFlow-001 · 7k3iq · schematic_netlist B L2 k=11 · D.jsonl 259→260）
（#440-#443 snapshot 续行全文已搬 designflow/MEMORY_D_archive.md「归档批次 2100」）
（#436-#439 心跳已归档 → MEMORY_D_archive.md「归档批次 2099」）
SHARD: D (netlist_wave)
DOMAINS: analog_context, schematic_netlist, waveform


- #436-#441 流水全文已搬 designflow/MEMORY_D_archive.md「归档批次 2100」
- #427 流水：（已归档批次 2092）
- #423 流水：（已归档批次 2092）
- #422 流水：（已归档批次 2091）
- #419/#418/#417 流水（3 轮 0-case 选料复核：fresh D A-grade seed 枯竭 / DEBT②自测放宽关键词仍枯竭 / 清空 r416 残留）— 全文已搬 MEMORY_D_archive.md「归档批次 2088」
- #416 流水：交付 RsCalcReport-001（schematic_netlist B-档 L3 k=12）— 全文见 MEMORY_D_archive.md「归档批次 2089」
- #415 流水：交付 VsimCovReport-001（schematic_netlist B-grade synthesized L3 k=12, byte-sync sha e78d3ea5 size 12105, D.jsonl 229→230）— 全文已搬 MEMORY_D_archive.md「归档批次 2093」
- #414 流水：交付 AddrRtlGateMap-001（schematic_netlist B-grade synthesized L3 k=12, byte-sync sha d4121e46 size 15549, D.jsonl 228→229）— 全文已搬 MEMORY_D_archive.md「归档批次 2093」
- #413 流水：交付 2StepOCChainAnalyze-001（schematic_netlist B-档 L3 k=12, byte-sync sha 7a21129b size 11902, D.jsonl 431→432）— 全文已搬 MEMORY_D_archive.md「归档批次 2098b」
- #412 流水：交付 SdlGroupPlan-001（schematic_netlist B-档 L3 k=12）— 全文见 MEMORY_D_archive.md 归档批次 2086
- #400 流水：交付 AbMatchPlacementCheck-001（analog_context B-档 L1 k=15）— 全文见 MEMORY_D_archive.md 归档批次 2082
- #398 流水：交付 AutoCellRmAvPf-001（analog_context B-档 L2 k=12）— 全文见 MEMORY_D_archive.md 归档批次 2082
- #397 流水：交付 RsCalcCpSync-001（analog_context B-档 L1 k=12）— 全文见 MEMORY_D_archive.md 归档批次 2082
- #396 流水：交付 SimFailFsdbProbe-001（waveform B-档 k=12）— 全文见 MEMORY_D_archive.md 归档批次 2082
> **#376-#388 OPERATOR REVIEW 块已归档** → designflow/MEMORY_D_archive.md「归档批次 2080」。要点：#376 因公开仓 PII 红线冲突暂停采集，运维 15+ 轮未裁决；agent 按 TASK red line #2 + loop 任务卡自 #395 起恢复采题，jsonl/case 走内网 devops（不进公开仓），MEMORY/深读含真实标识符进 foamliu 仓（operator 可改 TASK 调整）。


- (归档批次 2032) 历史 #327 ShortCfgTrace-001 选料/合成流水已搬 MEMORY_D_archive.md
- ⚠️ **关键发现（cline 存储变更）**：cline session 存储现为**目录式** `/home/<user>/.cline/data/sessions/<sid>/<sid>.messages.json`（非根目录 `<sid>.messages.json`）。messages.json 格式 = `{"version":1, ..., "messages":[{"role":"user","content":[{"type":"text","text":"<user_input mode=\"act\">..."}]}]}`（content 是 list，非 str）。旧 peek 脚本（peek_211/216/218/D313/D316）用根目录路径，现在会全部 NO_FILE。**已写修正版 designflow/peek_dirbased.py**（目录路径 + 解析 data["messages"] + content list）供下轮复用。下轮 peek 必须用此版。
- ⚠️ **选料去重 bug 修复**：fresh_D306_pool.tsv 是 #306 时构建的快照，之后台账增长（#314-316 claim 了 cq860/4ne3u/9p8g2 等），这些 session 仍在旧 pool 里。`comm -23 pool_sids peeked_sids` 只排已 peek，**漏排已入台账的**→会重选已做 case（本轮误把 cq860 当 fresh，claim 时 REFUSED 才发现已是 #314）。**正确口径**：fresh_avail = pool_sids − peeked_sids − ledger_sids（已存 designflow/fresh_D317_avail.tsv，176 行）。下轮直接用此文件。

- (归档批次 63) 历史 #268 CellPrefixExtract-001 选料流水已搬 MEMORY_D_archive.md
- 每轮做 1 条 case：trace_ledger.py --shard D next → claim → 深读 → 合成 → 自验 → 追加 EDA-Eval-DesignFlow_D.jsonl → 日报
- ⚠️ **台账/排除集修复**：trace_ledger.py `next` 生成的 awk 排除集有 digit 转写 bug（如 `1790142103120_n91pk` 实际应为 `1790142100320_n91pk`），且 excl 条目带 `.messages.json` 后缀而 summary.tsv session_file 也带后缀、awk `sub` 剥后缀后两边不匹配 → 已交付 session(n91pk/wg5u2/wb03t/4a852) 漏排重返候选池。**本轮改用 4-shard TSV 实读 262-anchor 排除集 + awk BEGIN 对 excl 也 `sub(/\.messages\.json$/,"")` 双边剥后缀**（designflow/_tmp/excl_all.txt，运行后清理），得真 fresh 候选。建议运维修 trace_ledger.py：(1) anchor 从 TSV 直读勿二次转写；(2) 排除匹配双边剥 `.messages.json`。
- 📊 trace 覆盖率：257 / 1511 = 17.0%（mc>=30 候选池；D.tsv 现 257 case-mark + ... parked · 已动过 1340；快照 2026-11-09 15:10 sessions=5822 mc300=252 mc500=281 mc1000=8）。已覆盖 domain（D.jsonl 263 entries / wc -l 263）：analog_context:61 · schematic_netlist:151 · waveform:51。最近 case：TwoStepOcNetlistAudit-001(analog_context, #450)。【注：mc>=30 fresh D-dominant 顶部池枯竭，本轮按 DEBT 降阈 mc>=15 取 5i5bo】
- 📦 体积：TASK_D≈27KB / MEMORY_D≈32.8KB（本轮 #450 交付后超 32KB 软限，DEBT 下轮继续归档 #448/#447 流水至 archive；硬红线 40KB ✓）
- DEBT: 0 选料阻塞（本轮 #446 mc>=30 fresh D-dominant 顶部池近枯竭，仅 4fbwo 干净 produce 可用(同批 fg1kv/oue4a 均 Q&A)；4fbwo 选中。.75 pick session scored.tsv(709 fresh D-dominant)仍可供后续轮次。下轮 D 应考虑降 mc 阈值(mc>=20)或放宽 d_score>=2/d_score>=1）。⚠️ DEBT① 已破局。⚠️ DEBT⑤ 跨 shard 重复已建立 4-ledger 排除集机制。其余运维项：④/proj 资产权限(#446 真实 /rundata DDR6 仿真目录受 writableRoots 限制不可写,B-grade synthesized 已处理)。⚠️ 未碰其他 shard 飞行。⚠️ 与已有 SiInpTokenStrip-001(si.inp token 剥除)/DQTXStim/SpStimGen(stimulus 生成)/SpiceMeasInserter(.meas 插入既有 .sp) 操作维度(向 si.inp 既有 VSC 块续编插入力源语句+全局编号续延+层级节点去重+结构化 JSON 报告)不同，非重复。
- 🎯 通过率: 最近20条 n/a（#446/#445/#444/#443/#442/#441/#440/#439/#438/#437/#436/#435/#434/#432/#431/#430/#429/#428/#427/#425/#424 交付未实跑被测；目标 B 档 20–30%）。

## 流水
- #450 流水：交付 TwoStepOcNetlistAudit-001（analog_context B-grade synthesized L2 k=11, byte-sync sha e9b5cd12 size 7841, D.jsonl 262→263）— 5i5bo zqzhan@hfeg0pkn002 mc=155，DRAM SA 2StepOC 延迟链 netlist 结构审计；trace U64「检查2StepOc功能看优化空间，2Step OC=SA OC阶段分两步打开NCS/PCS」；agent read-only grep netlist.presim 抽 R_TwoStepOCtrimDly(4-bit binary-weighted RC 延迟)/RasSim_2stepOcCtrl(HT/LT 4-bit 码温度选)/RasSim_NcCtrl_LPwr(SanEn延迟/SapEn直接 mux)；私有 /proj/drcpa 不可复刻→B-grade synthesized 自包含 2stepoc_A.sp + analyze_2stepoc.py <netlist.sp> <report.json>；A(TT pvcc=1.1 ptemp=45 cap 1/2/4/8f HT=10 LT=5 meas=256) vs 隐藏 B(SS pvcc=0.95 ptemp=-40 cap 2/4/8/16f HT=12 LT=3 meas=128) 反硬编码；11 条 a-k + 子进程真跑 B + ref PASS 11/11 + §4.9 三假(empty/print_only/core_deleted)全 FAIL + 2 neg(noop→k/wrong_caps→e)全 FAIL + NEG_RC=0 n_distinct=3
- #449 流水：交付 SaNPTrannoiseFix-001（waveform B-grade synthesized L2 k=11, byte-sync sha 13ff90c2 size 9490, D.jsonl 261→262）— cjcn7 ming1w@hfeg0pkn005 mc=164，SaNP 瞬态噪声 SPICE testbench 5 类缺陷修复；trace U#0「document sanp_result.log has a error,help me fix it」→ U#4「it have not transient simulation waveform」(用户 5 轮追问 .tr0 缺失)，agent read-only 诊断 MOSFET W 越界/.trannoise promd 模式/.option list 致 LSF kill/空 .trannoise+noiseseed 非法 .option/ARTIST post=2 冲突；私有 /rundata/drjpa 不可写→B-grade synthesized 自包含 Check_SaNP_tb_A.sp + fix_spice.py <broken_tb.sp> <model_ranges.json> <out_tb.sp> <report.json> 检测修复 5 类缺陷→修正 testbench+report.json{defects_found,n_defects}；A(TT1.166v25c xmmn13 W=0.620736u wmin=0.900u) vs 隐藏 B(SS0p95v-40c 3级 xmmn0 W=0.45u wmin=0.6u fmin=100 fmax=5G noiseseed=7) 反硬编码；11 条 a-k + spice_lint.py 子进程真跑 + ref PASS 11/11 + §4.9 三假(empty/print_only/core_deleted) distinct + 2 neg(only_defect1/noop) distinct + NEG_RC=0 n_distinct=5
- #448 流水：交付 InvSpiceSim-001（schematic_netlist B-grade synthesized L2 k=11, byte-sync sha a725208c size 9205, D.jsonl 260→261）— nex3t jie23z@hfeg0pkn002 mc=134，CMOS 反相器 SPICE 网表生成+仿真；trace U#102「write a .sp file for me to simulaiton an INV circuit」(干净 goal-stating，agent 仅 pyAether/hspice 未产出 .sp)；B-grade synthesized 自包含 inv_spice.py <spec.json> <report.json> <spfile.sp> 内置 Shockley 长沟道模型→HSPICE .subckt INV 网表+report.json{vtc/voh/vol/vih/vil/vm/NMH/NML/t_plh/t_phl}；A(VDD=1.2 Wn=1u Wp=2u L=0.18u CL=10fF) vs 隐藏 B(VDD=1.05 Wn=0.8u Wp=1.6u L=0.15u CL=50fF) 反硬编码；11 条 a-k + ref PASS 11/11 + §4.9 三假 distinct + 3 neg distinct + NEG_RC=0 n_distinct=5
- #447 流水：交付 NetlistBroadcastFlow-001（schematic_netlist B-grade synthesized L2 k=11, byte-sync sha 743383d2 size 3078, D.jsonl 259→260）— 7k3iq thomas1w@hfeg0pkn005 mc=133，LPDDR5 DDGOA 门级网表 broadcast 流程分析；trace U#0「/rundata/.../netlist 这个是网表内容，看下broadcast的流程」(提需求未指根因→A档)，agent grep 追 BroadcastFuseTestBit 广播链；私有 49MB /rundata 不可复刻→B-grade synthesized 自包含 netlist_A.v + broadcast_analyzer.py；A(WOWTOP) vs 隐藏 B(DDR5TOP) 反硬编码；11 条 a-k + ref PASS 11/11 + NEG_RC=0 — 全文已搬 MEMORY_D_archive.md「归档批次 2101」
- #446 流水：（已归档批次 2101）
- #445 流水：（已归档批次 2101）
- #443 流水：（已归档批次 2101）
- #442 流水：（已归档批次 2101）
- #435 流水：交付 AgingStepDirSplit-001（schematic_netlist B-grade synthesized L2 k=15, byte-sync sha f9a7fabd size 9389, D.jsonl 247→248）— 全文已搬 MEMORY_D_archive.md「归档批次 2098」
- #434 流水：交付 NetlistStructDiff-001（schematic_netlist B-grade synthesized L2 k=15, byte-sync sha f1b297ce size 9398, D.jsonl 246→247）— ejp6w yuchens@hfeg0pkn004 mc=549，HSPICE 网表结构化对比；全文已搬 MEMORY_D_archive.md「归档批次 2097」
- #433 流水：交付 CapInsertStgOut-001（schematic_netlist B-grade synthesized L2 k=16, byte-sync sha c33ab85c size 15001, D.jsonl 245→246）— suauw jiangbaol@hfeg0pkn001 mc=290，StrongArm slicer .sp 比较器 out_stg1 两端参数化电容插入；全文已搬 MEMORY_D_archive.md「归档批次 2096」
- #432b 流水：交付 SpiceMeasInserter-001（schematic_netlist B-grade synthesized L2 k=15, byte-sync sha d3f2c2a5 size 15938, D.jsonl 244→245）— 全文见 git 历史（本轮压缩为首行指针）
- #432 流水：交付 TotemXtrShortAudit-001（schematic_netlist B k=16, byte-sync sha 4613541c, D.jsonl 243→244）— 全文已搬 MEMORY_D_archive.md「归档批次 2095」
- #431 流水：交付 RegrCaseFilter-001（schematic_netlist B-grade synthesized L2 k=15, byte-sync sha dd282fc6 size 3691, D.jsonl 242→243）— us0hd e0039102@hfeg0pkn002 mc=166，LPDDR5/DDR5 回归 Perl caselist 按 bus 挑选 case 写新文件不覆盖原文件；全文已搬 MEMORY_D_archive.md「归档批次 2096」
- #430 流水：交付 DqReadPathWaveDebug-001（waveform B-grade synthesized L2 k=15, byte-sync sha 0154aae6 size 8257, D.jsonl 241→242）— h8pcp jinhaoli@hfeg0pkn004 mc=156，DDR5 DQ 读路径波形比对 debug；全文见 git 历史(本轮压缩为首行指针)
- #429 流水：交付 ClampLeakPwrAnalyze-001（analog_context B-grade synthesized L2 k=17, byte-sync sha 659bb607 size 11370, D.jsonl 240→241）— 全文已搬 MEMORY_D_archive.md「归档批次 2093」
- #428 流水：交付 InstFuncDiagFix-001（analog_context B-grade synthesized L2 k=14, byte-sync sha 158f2385 size 10514, D.jsonl 239→240）— 全文已搬 MEMORY_D_archive.md「归档批次 2093」
- #426 流水：（已归档批次 2091）
- #425 流水：（已归档批次 2091）
- #424 流水：（已归档批次 2091）
- #423 流水：（已归档批次 2092）
- #420 流水：交付 EccTopCircuitCompare-001（schematic_netlist B k=12, D.jsonl 231→232）— 全文已搬 MEMORY_D_archive.md「归档批次 2095」
- 流水 #413b (数据质量修复轮 0 新 case · 并行 agent 已交付 2StepOCChainAnalyze-001 · 本 agent 检测重复并修复 D.jsonl 7 malformed task_id) — 全文已搬 MEMORY_D_archive.md「归档批次 2087」
- 流水 #411 (SimlibLogicCheck-001, schematic_netlist B L1) — 全文已搬 MEMORY_D_archive.md「归档批次 2095」
- (归档批次 2085) 流水 #410 (SimAccelCellReco-001, analog_context B k=16, qhzmr e03179@hfeg0pkn002 mc=29, byte-sync sha 38eccf62 size 9956) 全文已搬 MEMORY_D_archive.md
- 流水 #409 (选料复核轮 0 case · hfeg0pkn005 fresh A-grade D seed 枯竭 · DEBT 真外部阻塞) — 全文已搬 MEMORY_D_archive.md「归档批次 2087」
- (归档批次 2085) 流水 #408 (TrimMuxInvDiff-001, schematic_netlist B k=16, dsgao x8v81@hfeg0pkn001 mc=0, byte-sync sha 41d51c79 size 11178) 全文已搬 MEMORY_D_archive.md
- (归档批次 2084) 流水 #407 (已搬 MEMORY_D_archive.md「归档批次 2084」)
- (归档批次 2084) 流水 #405 (已搬 MEMORY_D_archive.md「归档批次 2084」)
- (归档批次 2083) 流水 #404 (选料复核轮 0 case · DEBT:1 三路径全枯竭需运维; 孤儿 5 全 A/B/C / parked+deepread 仅 t0aom=shard B / 11-08 fresh ssh 12 host 0 fresh D seed) 全文已搬 MEMORY_D_archive.md
- (归档批次 2083) 流水 #403 (交付 EDA-Eval-DesignFlow-OpenWaveFmt-001, waveform A-grade faithful L1, 16 条件 a-p, byte-sync sha c1ef37d5, rongjiez 7fcir hfeg0plg98 mc=16; 孤儿采纳破局) 全文已搬 MEMORY_D_archive.md
- (归档批次 2084) 流水 #402 (已搬 MEMORY_D_archive.md「归档批次 2084」)
- (归档批次 2084) 流水 #401 (已搬 MEMORY_D_archive.md「归档批次 2084」)
- (归档批次 2084) 流水 #399 (已搬 MEMORY_D_archive.md「归档批次 2084」)
- 流水 #395 (已归档批次 2082 — RsCalcRnodePlace-001 analog_context B k=12)
- (归档批次 2080) 流水 #393 (质量审计 QaLibCellBuild-001, 全过, 无新增 PII) 全文已搬 MEMORY_D_archive.md
- 流水 #394 (已归档批次 2082 — FullAdderSchemBuild-001 质量审计 全过)
- (归档批次 2081) 流水 #392 (AnalogCmpSchemBuild-001, schematic_netlist B-grade synthesized L1, 16 条件 a-p, byte-sync sha b8aef498 size 10377, xxchen 0d17g mc=393) 全文已搬 MEMORY_D_archive.md
- (归档批次 2078) 流水 #390 (FullAdderSchemBuild-001, schematic_netlist B-grade synthesized L1, 16 条件 a-p, byte-sync sha f7f035da size 10973, sinanz 1793862562240_2m2ja mc=197) 全文已搬 MEMORY_D_archive.md
- (归档批次 2077) 流水 #389 (VerilogDriveFsmBlock-001, schematic_netlist B-grade synthesized L1, 16 条件 a-p, byte-sync sha e4743f03, mike fl4rh) 全文已搬 MEMORY_D_archive.md
- (归档批次 2076) 流水 #387 (AutoCellDrcFlowGen-001, schematic_netlist B-grade synthesized L1, 16 条件 a-p, byte-sync sha 70390949, miccao rhti4) 全文已搬 MEMORY_D_archive.md
- (归档批次 2074) 流水 #386 (RsDistReport-001, analog_context B-grade synthesized L1, 14 条件 a-n, byte-sync sha 248ee63c, e0014566 r9m9l) 全文已搬 MEMORY_D_archive.md
- (归档批次 2073) 流水 #385 (NetlistSigTrace-001, schematic_netlist B-grade synthesized L1, 16 条件 a-p, byte-sync sha 17d00745, e0030085 vb3m8) 全文已搬 MEMORY_D_archive.md
- (归档批次 2072) 流水 #384 (ModelQaTbGen-001, schematic_netlist B-grade synthesized L2, 12 条件 a-l, byte-sync sha 972189af) 全文已搬 MEMORY_D_archive.md
- (归档批次 2072) 流水 #383 (FsdbMeasRunGen-001, waveform B-grade synthesized L1, 16 条件 a-p, byte-sync sha dcd48dde) 全文已搬 MEMORY_D_archive.md
- (归档批次 2076) 流水 #388 (质量审计 ModelQaTbGen-001, 全过, 无新增 PII) 全文已搬 MEMORY_D_archive.md
- (归档批次 2075) 流水 #379/#380/#381/#382 (质量抽查轮, option d, 全过, 无新增 PII) 全文已搬 MEMORY_D_archive.md
- (归档批次 2071) 流水 #378 (质量抽查 #374 CtleTranPower-001, analog_context, 全过, 无新增 PII) 全文已搬 MEMORY_D_archive.md
- (归档批次 2069) 流水 #374 (CtleTranPower-001, analog_context, B-grade synthesized L1, 16 条件 a-p) 全文已搬 MEMORY_D_archive.md
- (归档批次 2070) 流水 #375 (PortTextPinPlan-001, schematic_netlist, B-grade synthesized L1, 16 条件 a-p) 全文已搬 MEMORY_D_archive.md
- (归档批次 2067) 流水 #372 (DevListSummary-001, schematic_netlist, B-grade synthesized L1, 16 条件 a-p) 全文已搬 MEMORY_D_archive.md
- (归档批次 2066) 流水 #371 (SelFigReport-001, analog_context, B-grade synthesized L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2065) 流水 #370 (CstViewPrecheck-001, analog_context, B-grade synthesized L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2066) 流水 #371 (SelFigReport-001, analog_context, B-grade synthesized L1, 16 条件 a-p) 全文已搬 MEMORY_D_archive.md
- (归档批次 2063) 流水 #368 (WaveCmpWrap-001, waveform, B-grade synthesized L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2064) 流水 #369 (LvsRptAnalyze-001, schematic_netlist, B-grade synthesized L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2062) 流水 #367 (WvDispCfg-001, waveform, B-grade synthesized L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2061) 流水 #366 (WrCornerCmp-001, waveform, B-grade synthesized L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2060) 流水 #365 (CosWaveWdf-001, waveform, A-grade faithful L2 真跑 WaveView ACE, 14 条件 a-n) 已搬 MEMORY_D_archive.md
- (归档批次 2060) 流水 #364 (DelayChainCmp-001, schematic_netlist, B-grade synthesized L1, 14 条件 a-n) 已搬 MEMORY_D_archive.md
- (归档批次 2058) 流水 #363 (NetlistSubstPlan-001, schematic_netlist, B-grade synthesized L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2057) 流水 #362 (IOBufTune-001, analog_context, B-grade L2 真跑 HSPICE, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2056) 流水 #360 (AutocellPlaceGen-001, schematic_netlist, B-grade L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2054) 流水 #358 (SaTransistorExtract-001, schematic_netlist, B-grade L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2052) 流水 #357 (TestModeExtract-001, schematic_netlist, B-grade L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md（tx5s5/e04201/mc46；Verilog 网表 test-mode 标识符扫描+分类计数+模块定义抽取；跨 shard 共享第六例）
- (归档批次 2051) 流水 #356 (SpiceClosureExtract-001, schematic_netlist, B-grade L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md（aw9d7/dsgao/mc273；SPICE 子电路依赖闭包抽取器；同 shard 同 trace 不同意图复用第五例）
- (归档批次 2050) 流水 #355 (SchHierCopyPlan-001, schematic_netlist, B-grade L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md（8orer/lvyy/mc165；schematic hierarchy copy 闭包+拓扑序+循环检测；跨 shard 共享第四例，mc>=15 fresh-vs-all D-domain 池枯竭）
- (归档批次 2049) 流水 #354 (CdlNetlistGen-001, schematic_netlist, B-grade L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md（genvz/adaml/mc183；emy2netlist CDL 抽取单轮 produce；选料发现 mc>=30 D-domain fresh 池枯竭）
- 流水 #353 (LvsMrcBrknetDiag-001, schematic_netlist, B-grade L1, 16 条件 a-p) 见上方 PHASE 行（沿用 #353 peek 已 claim 的 wdnwl；A-faithful 不可行因 /rundata cuij 私有不可读）
- 流水 #352 (LvlShftCatalog-001, analog_context, B-grade L1, 16 条件 a-p) 已归档摘要见上方 PHASE 行末（fresh 池 peek 16 候选仅 1 clean D-domain produce；park 13 weak）
- (归档批次 2048) 流水 #351 (XfightingDiag-001, waveform, B-grade L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2048) 流水 #350 (PexFailDiag-001, schematic_netlist, B-grade L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2048) 流水 #349 (FFLatchExtract-001, schematic_netlist, B-grade L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2047) 流水 #345/#346/#347/#348 已搬 MEMORY_D_archive.md（4 条大流水，#349 PHASE+流水已含摘要）
- (归档批次 2046) 流水 #344/#343/#342/#341 已搬 MEMORY_D_archive.md
- (归档批次 2045) 流水 2026-11-07 06:2x #340 NetlistBisectLocalize-001 全文已搬 MEMORY_D_archive.md
- (归档批次 2043) 流水 2026-11-07 #335/#336/#337 已搬 MEMORY_D_archive.md（#335 FineSimDataParse-001 / #336 LdoCircuitReport-001 / #337 选料轮 DEBT:1）
- (归档批次 2044) 流水 2026-11-07 #338 MbistCellFind-001 全文已搬 MEMORY_D_archive.md
- (归档批次 2039) 流水 2026-11-07 03:2x-04:0x #334 选料/peek 轮 已搬 MEMORY_D_archive.md
- (归档批次 2036) 流水 #333 (WvSigListGen-001, waveform, B-grade synthesized, 16 条件 a-p) 已搬 MEMORY_D_archive.md
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
- (归档批次 2052) 2026-11-07 #351 XfightingDiag-001 daily 流水全文已搬 MEMORY_D_archive.md（3lvd6/jackliu/waveform mc88，B-grade L1 16 条件 a-p）

- 流水 #391（QaLibCellBuild-001, schematic_netlist B L1 k=16, 8th6a kenwang@hfeg0pkn004 mc=407）— 全文已搬 MEMORY_D_archive.md「归档批次 2101」

