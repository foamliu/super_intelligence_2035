WAITING: 0
SHARD: D (netlist_wave)
DOMAINS: analog_context, schematic_netlist, waveform
DEBT: 0（#368 已合成 WaveCmpWrap-001（waveform B-grade synthesized L1，WaveCompare 波形对比 CLI 封装，边沿序列对比+EQUIVALENT/DIFFERENT/GRAY/NO_DATA 四判决）；⚠️ L1/L2 比例债 22→23 轮（#365 降到的 20 已被 #366/#367/#368 连续 L1 顶到 23；fresh mc>=30 D-domain 池用 candidates_mc30.tsv 重建得 245 fresh 候选；L2 需 live binary 不可移植 + 40min 预算风险高 → 继续 L1 produce）。下轮继续优先 L2/L3 produce，挑 hspice/spectre/calibre/wv 真跑类 trace；waveform(44)/analog_context(45) 仍为最低覆盖域，继续优先补）。

- **PHASE**: shard D 运行中。已交付 199 条 case（D.jsonl 199 行：analog_context:45/schematic_netlist:110/waveform:44）；台账 case-mark 197 + 1037 parked = 1234 已动过。**本轮 #368 = 交付 EDA-Eval-DesignFlow-WaveCmpWrap-001**（waveform B-grade synthesized **L1**，WaveCompare 波形对比 CLI 封装，边沿序列对比+四判决，16 条件 a-p）。**#367**(归档批次 2061)：d810y→WvDispCfg-001（waveform B-grade synthesized L1，WaveView 显示配置生成器 leaf名+总线分组，16 条件 a-p）。**#366**(归档批次 2060)：pspw5→WrCornerCmp-001（waveform B-grade synthesized L1，FineSim .mt0 corner 对比，16 条件 a-p）。**#365**(归档批次 2060)：p5x6n→CosWaveWdf-001（waveform **L2 真跑 WaveView ACE**，A-faithful，14 条件 a-n）。**#364**(归档批次 2060)：f86ll→DelayChainCmp-001（schematic_netlist L1）。**#363**(归档批次 2058)：dhgxy→NetlistSubstPlan-001（schematic_netlist L1）。**#368**：3qe6x/e0039602/hfeg0plg102/mc45, **B-grade synthesized** **L1**(离线 .tbl 文本解析无 EDA 依赖), 16 条件 a-p；WaveCompare 波形对比 CLI 封装 wave_cmp.py --pass-tbl --fail-tbl --signal --t0 --t1 --vdd-pass --vdd-fail --outdir → verdict.json+edges.json+report.md；_split_signal 归一化 v(a.b.c)/a.b.c/a.b<2>→(bare_net,vkey)；_read_tbl 读 .tbl(#signal/#vdd header + time_ns/v(...) 列, vkey 不在列→None=NO_DATA)；_extract_edges 在[t0,t1]窗内检测上升/下降沿(跨0.5*vdd)；_compare 边沿序列→EQUIVALENT/DIFFERENT/GRAY/NO_DATA。**A-faithful 不可行**：U#22/U#28 是干净 produce(封装 WaveCompare 顶层 CLI)，gold=tools/compare_signal.py(303行)依赖项目 src/divergence 模块不可移植 + 真实 fsdb 2GB 不可附加 + live FineSim/fscript L2 不可移植 → B 档 synthesized。A=DDR5 pumain<2> pass/fail .tbl(FF1.15v130c/SS0.88v-40c, 834-838ns, vdd1.15/0.88)；hidden B=LPDDR4 dq<7> .tbl(TT1.2v25c/FF1.1v-40c, 1200-1204ns, vdd1.2/1.1, pass 3脉冲6边沿 vs fail 2脉冲4边沿→DIFFERENT)；hidden B2=SERDES rx<0> 信号缺失守卫(.tbl 含 tx<0> 非 rx<0>→NO_DATA)。反硬编码五轴：design DDR5/LPDDR4/SERDES 全不同；信号名/层次前缀 xi_channel/phy_top/serdes_top 全不同；时间窗 834/1200/300 全不同；vdd 1.15-0.88/1.2-1.1/1.0 全不同；B2 信号缺失杀总假设信号存在硬编。自验 ref PASS 16/16(B DIFFERENT[6vs4边沿]+B2 NO_DATA[rx<0>缺失]) + 6 neg FAIL 5 distinct first_fail(b/d/g/m/o) + §4.9 三假 FAIL + 断言 k=16 + 确定性 3x sha256 一致。
- (归档批次 2032) 历史 #327 ShortCfgTrace-001 选料/合成流水已搬 MEMORY_D_archive.md
- ⚠️ **关键发现（cline 存储变更）**：cline session 存储现为**目录式** `/home/<user>/.cline/data/sessions/<sid>/<sid>.messages.json`（非根目录 `<sid>.messages.json`）。messages.json 格式 = `{"version":1, ..., "messages":[{"role":"user","content":[{"type":"text","text":"<user_input mode=\"act\">..."}]}]}`（content 是 list，非 str）。旧 peek 脚本（peek_211/216/218/D313/D316）用根目录路径，现在会全部 NO_FILE。**已写修正版 designflow/peek_dirbased.py**（目录路径 + 解析 data["messages"] + content list）供下轮复用。下轮 peek 必须用此版。
- ⚠️ **选料去重 bug 修复**：fresh_D306_pool.tsv 是 #306 时构建的快照，之后台账增长（#314-316 claim 了 cq860/4ne3u/9p8g2 等），这些 session 仍在旧 pool 里。`comm -23 pool_sids peeked_sids` 只排已 peek，**漏排已入台账的**→会重选已做 case（本轮误把 cq860 当 fresh，claim 时 REFUSED 才发现已是 #314）。**正确口径**：fresh_avail = pool_sids − peeked_sids − ledger_sids（已存 designflow/fresh_D317_avail.tsv，176 行）。下轮直接用此文件。

- (归档批次 63) 历史 #268 CellPrefixExtract-001 选料流水已搬 MEMORY_D_archive.md
- 每轮做 1 条 case：trace_ledger.py --shard D next → claim → 深读 → 合成 → 自验 → 追加 EDA-Eval-DesignFlow_D.jsonl → 日报
- ⚠️ **台账/排除集修复**：trace_ledger.py `next` 生成的 awk 排除集有 digit 转写 bug（如 `1790142103120_n91pk` 实际应为 `1790142100320_n91pk`），且 excl 条目带 `.messages.json` 后缀而 summary.tsv session_file 也带后缀、awk `sub` 剥后缀后两边不匹配 → 已交付 session(n91pk/wg5u2/wb03t/4a852) 漏排重返候选池。**本轮改用 4-shard TSV 实读 262-anchor 排除集 + awk BEGIN 对 excl 也 `sub(/\.messages\.json$/,"")` 双边剥后缀**（designflow/_tmp/excl_all.txt，运行后清理），得真 fresh 候选。建议运维修 trace_ledger.py：(1) anchor 从 TSV 直读勿二次转写；(2) 排除匹配双边剥 `.messages.json`。
- 📊 trace 覆盖率：197 / 1511 = 13.0%（mc>=30 候选池；D.tsv 现 197 case-mark + 1037 parked · 已动过 1234；快照 2026-11-07 21:4x sessions=2912 mc300=252 mc500=281 mc1000=8）。已覆盖 domain（D.jsonl 199 行）：analog_context:45 · schematic_netlist:110 · waveform:44。**#368**：3qe6x→EDA-Eval-DesignFlow-WaveCmpWrap-001（已交付，waveform B-grade synthesized L1，WaveCompare 波形对比 CLI 封装，边沿序列+四判决，16 条件 a-p）。**#367**：d810y→EDA-Eval-DesignFlow-WvDispCfg-001（已归档，waveform B-grade synthesized L1，WaveView 显示配置生成器 leaf名+总线分组，16 条件 a-p）。**#366**：pspw5→EDA-Eval-DesignFlow-WrCornerCmp-001（已归档，waveform B-grade synthesized L1，FineSim .mt0 corner 对比报告生成器，16 条件 a-p）。**#365**：p5x6n→EDA-Eval-DesignFlow-CosWaveWdf-001（已归档，waveform L2 真跑 WaveView ACE，A-faithful，14 条件 a-n）。**#364**：f86ll→EDA-Eval-DesignFlow-DelayChainCmp-001（已归档，schematic_netlist L1）。**#363**：dhgxy→NetlistSubstPlan-001（已归档）。**#362**：l5r0u→IOBufTune-001（已归档）。**#361**：0oeb7→DelApiProbePlan-001（并行）。**#360**：oh3te→AutocellPlaceGen-001（已归档）。**#359**：4qpyk→ShiftIntervalReport-001（已归档）。**#358**：5hbdw→SaTransistorExtract-001（已归档）。**#357**：tx5s5→TestModeExtract-001（已归档）。**#356**：aw9d7→SpiceClosureExtract-001（已归档）。**#355**(并行)：8orer→SchHierCopyPlan-001（已归档）。
- 📦 体积：TASK_D≈25KB / MEMORY_D≈27KB（#368 顶替 #367 PHASE/coverage/debt/断言 行 + 新增 #368 流水；低于 32KB 红线）
- DEBT: 0（#367 已合成 WvDispCfg-001（waveform B-grade synthesized L1，WaveView 显示配置生成器 leaf名+总线分组）；⚠️ L1/L2 比例债 21→22 轮（#365 降到的 20 已被 #366/#367 连续 L1 顶到 22；fresh mc>=30 D-domain 池枯竭，#367 降 mc>=5 重建候选池取 d810y；L2 需 live binary 不可移植 + 40min 预算风险高 → 继续 L1 produce）。**下轮 #368 第一件事**：trace_ledger.py --shard D next 取新候选 → 优先 L2/L3 produce（挑 hspice/spectre/calibre/wv 真跑类 trace）；waveform(43)/analog_context(45) 仍为最低覆盖域，继续优先补；可降 mc 阈值到 ≥5 重建 fresh 池或跨 shard 共享 L2 trace。
- 🧾 断言: k_rationale=k_check=16 ✓（#368 WaveCmpWrap-001，16 条件 a-p 全对账；日报三列 k(断言)=16/k(check)=16/一致=✓ 自证）。存量 199 条 test_rationale 全部以 `k 条断言：①…` 开头已核验达标。rewrite_queue.tsv 全部 done（无待修）。今日 151/199 达标（#368 新增 1 条达标）。

## 流水
- 流水 #368 (WaveCmpWrap-001, waveform, B-grade synthesized L1, 16 条件 a-p) — 3qe6x/e0039602/hfeg0plg102(10.129.8.136)/mc45；trace=AutoDebug V3 DRAM SPICE 仿真失败自动根因定位项目(157 msgs; U#22「如果我想单独调用一下compare代码对比两段波形...或者你写个代码，让我可以通过给信号的路径和名称，还有时间范围，直接对比两段代码」+U#28「请你尽可能调用这个项目当中的波形对比代码，然后封装一个顶层让我可以直接调用」; assistant 产 tools/compare_signal.py 303行, compare_waveforms 顶层函数 + _split_signal 信号归一化 + 四判决 EQUIVALENT/DIFFERENT/GRAY/NO_DATA; 真实信号 xi_channel.xi_chansc0.xi_dqsc0.xi_dqpadm6_0.xi_dqio.xi_dqouttop.pumain<2>, corners FF1.15v130c/SS0.88v-40c, 时间窗 834-838ns, vdd_pass1.15/vdd_fail0.88; WaveCompare 核心思路=比对边沿序列不逐点电压, 阈值0.5*vdd归一化)。**A-faithful 不可行**：U#22/U#28 是干净 produce(封装 WaveCompare 顶层 CLI)，gold=tools/compare_signal.py 依赖项目 src/divergence 模块不可移植 + 真实 fsdb 2GB 不可附加 + live FineSim/fscript L2 不可移植 → B 档 synthesized 重述为 produce(.tbl 波形快照→对比 CLI+报告)。**合成**：wave_cmp.py --pass-tbl --fail-tbl --signal --t0 --t1 --vdd-pass --vdd-fail --outdir → verdict.json+edges.json+report.md。_split_signal 归一化 v(a.b.c)/a.b.c/a.b<2>→(bare_net,vkey)；_read_tbl 读 .tbl(#signal/#vdd header + time_ns/v(...) 列, vkey 不在列→None=NO_DATA)；_extract_edges 在[t0,t1]窗内检测上升/下降沿(跨0.5*vdd)；_compare 边沿序列→EQUIVALENT(边沿数同+时刻差≤tol)/DIFFERENT(边沿数不同)/GRAY(灰区)/NO_DATA(信号缺失)。A=DDR5 pumain<2> pass/fail .tbl(FF1.15v130c/SS0.88v-40c, 834-838ns, vdd1.15/0.88, 4脉冲8边沿)；hidden B=LPDDR4 dq<7> .tbl(TT1.2v25c/FF1.1v-40c, 1200-1204ns, vdd1.2/1.1, pass 3脉冲6边沿 vs fail 2脉冲4边沿→DIFFERENT)；hidden B2=SERDES rx<0> 信号缺失守卫(.tbl 含 tx<0> 非 rx<0>→NO_DATA)。反硬编码五轴：design DDR5/LPDDR4/SERDES 全不同；信号名/层次前缀 xi_channel/phy_top/serdes_top 全不同；时间窗 834/1200/300 全不同；vdd 1.15-0.88/1.2-1.1/1.0 全不同；B2 信号缺失杀总假设信号存在硬编。check 16 条件 a-p：a(防泄漏+py_compile) b(B-run exit0+3文件) c(verdict.json 12键) d(_split_signal 归一化 v()剥离+bare/vkey+总线位) e(verdict∈四值) f(时间窗过滤) g(n_edges_pass==6) h(n_edges_fail==4) i(verdict==DIFFERENT) j(report含signal+verdict+边沿数) k(edges.json pass/fail列表+t_ns+direction) l(max_shift_ns非负) m(vdd_pass==1.2+vdd_fail==1.1) n(反硬编码无A标记+A-run≠B) o(B2守卫NO_DATA+0边沿) p(确定性3x sha256)。自验：ref PASS 16/16 + 6 neg FAIL 5 distinct first_fail(b/d/g/m/o: empty_shell→b.B-3files, print_expected→d.vkey, core_deleted→g.n-edges-pass, naive_hardcode_vdd→m.vdd-pass, naive_hardcode_a→d.bare-net, naive_no_nodata→o.B2-nodata) + §4.9 三假 FAIL + 断言闸门 k=16 + 确定性 3x sha256 一致。**教训**：(1) **candidates_mc30.tsv 本地过滤有效**：4-shard 台账 excl(1660 sids) + D-domain 关键词正则(waveview/cosmos/skill/netlist/spiros/spectrum/analog/schematic) → 245 fresh 候选，按 waveform/analog_context/schematic_netlist 优先级分桶选料，避免 .75 长 awk 超限(trace_ledger.py next 生成的 awk 排除集 1660 条单行超长报 syntax error，改本地 python 过滤 candidates_mc30.tsv)；(2) **边沿序列对比是 waveform L1 可验好范式**：比对边沿序列不逐点电压(真实 WaveCompare 核心思路)，0.5*vdd 阈值归一化 + 时刻匹配容差 → 16 条件天然丰富(归一化/边沿提取/时间窗/判决/跨输入/确定性)；(3) **B2 信号缺失是强反硬编码轴**：.tbl 含 tx<0> 但请求 rx<0> → 候选必须检测信号是否在 .tbl 列中，naive_no_nodata 把缺失当空边沿→EQUIVALENT 而非 NO_DATA → (o) FAIL；(4) **naive_hardcode_vdd 测 vdd 归一化**：hardcode A 的 vdd(1.15/0.88) 不读 B 的(1.2/1.1) → (m) FAIL（注意 fixed-threshold 0.5V 对满摆幅波形无效，须改 hardcode vdd 值才能命中 (m)）；(5) **真实 trace 的 produce 意图+user-accepted 产物 + 不可移植依赖 = B-grade synthesized 标准范式**：3qe6x gold=compare_signal.py 干净 produce 但依赖项目模块+fsdb，B 档重述为 .tbl→CLI 离线可验。台账 mark 3qe6x→case；case-mark 196→197；waveform 43→44；D.jsonl 198→199。
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
- (归档批次 2052) 2026-11-07 #351 XfightingDiag-001 daily 流水全文已搬 MEMORY_D_archive.md（3lvd6/jackliu/waveform mc88，B-grade L1 16 条件 a-p）
