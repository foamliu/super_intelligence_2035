# trace_deepreads/ltkg1_fifo_delay_opt.md — shard B 深读笔记

**trace**: 1793928990578_ltkg1.messages.json · curryxu @ hfeg0pkn001 (10.129.2.10) · mc=229 · 116 msgs / 633KB · mtime 2026-11-06 10:15
**扫描来源**: 11-10 cron diff (eda_trace_20261110.log) → 6 un-ledgered fresh 之一；前轮(00:1x) peek 标「留备选/偏 reject」(末轮 mid-debug FSDB)，本轮重 peek 发现金标准在 msg #30+#43。

## 用户轮（A-faithful 选轮）
- **U#0**（提需求，未给根因/修复 → A-faithful 合格 ✓）:
  > /proj/m2701/V0_DDR4/workdir/curryxu/simulation/FIFO_TOP_tb.sp
  > /proj/m2701/V0_DDR4/workdir/curryxu/simulation/FIFO_TOP/hspiceD/schematic/netlist/netlist
  > 这个电路我希望从nibble_sel0来之后，输出dnner端信号能在最快的时间翻转，也就是中间的delay尽可能地做小，有哪些地方管子的尺寸，或者结构可以调整的，请你帮忙检查一下
- **U#31**: 「我更新了，你帮我看一下现在延迟是多少」= 用户按 assistant #30 建议动手改了电路，再请测延迟 → 证明 #30 分析被接受。

## assistant 关键产物（金标准）
- **msg #30** 完整延迟优化分析：
  - 关键路径：`Nibble_Sel0 → XI_FIFOSel_14(FIFOSel, 3→6 译码+passgate 电平恢复) → Sel<5:0>/SelN<5:0> → XI_FIFOSelX6_15(FIFOSelX6, 6:1 三态 MUX) → DNNER/DNNOF/DNNEF/DNNOR`，约 7 级逻辑门。
  - 4 个瓶颈：① FIFOSel 译码器级数多、尺寸小(invFx1 130n/230n, nand2Tx1 130n/170n)；② invenTx4_sub 2NMOS+2PMOS 串联 → 等效 Ron 翻倍，net19 挂 6 个漏极寄生大；③ 输出级 invFx4_sub_Fifo(560n/680n) 驱动偏弱；④ passgtFx1_sub_Fifo(W=100n,L=40n) 全设计最弱。
  - 5 条优化建议（按 impact）：① FIFOSel 译码通路门加大 2~3×(-20~25%)；② FIFOSelX6 最后 2 级翻倍(-30~40%)；③ FIFOSelX6 内加局部 Sel 预缓冲(-10~15%)；④ 架构级 MUX 前移；⑤ 单 TG 替串联对。
- **msg #43** 用户实际应用的变更（被接受的产物）：
  | 改动位置 | 原尺寸 | 新尺寸 | 方向 |
  | passgtFx1_sub_Fifo NMOS | Wn=100n,L=40n | Wn=130n,L=30n | ↑30% |
  | passgtFx1_sub_Fifo PMOS | Wp=200n,L=40n | Wp=260n,L=30n | ↑30% |
  | FIFOSel NAND 译码器 | nand2Tx1(130n/170n) | nand2Tx2(260n/340n) | ↑2× |
  | FIFOSel Sel 缓冲(部分) | invFx1_sub_Fifo | invFx2_sub_Fifo | ↑2× |
  | FIFOSelX6 输出级 | invFx4_sub_Fifo(560n/680n) | invFx8_sub_Fifo(1.12μ/1.36μ) | ↑2× |
  > 注意：invenTx4_sub 串联电阻是瓶颈但用户未改（结构性，需拓扑变更），故 bottleneck 有它、recommendation 无它 → 本 case 关键区分点。

## 工具链
read_files×多 / search_codebase(超时) / run_approved_command(python-runner, shell-runner 拒绝) / editor(netlist_analyzer.py, measure_delay.sp, debug_fsdb.py) / list_allowed_files / skills(waveview-fsdb-readerV2-2)。末轮(mid-debug FSDB #1 suffix)与本 case 无关（金标准在前段已成立）。

## case 编码
- **case_id**: EDA-Eval-DesignFlow-FifoDelayOptDiag-001 (spice_sim A-faithful L1 k=17)
- **资产 A** fifo_sel_A.sp：忠实紧凑 HSPICE，保留真实信号名 Nibble_Sel0/Sel<5:0>/DNNER/DNNOF/DNNEF/DNNOR 与子电路名 FIFOSel/FIFOSelX6/invFx1/2/4/8_sub_Fifo/nand2Tx1_Fifo/nand2Tx2/invenTx4_sub/passgtFx1_sub_Fifo 及真实尺寸；4 路输出共享 Sel 总线。
- **隐藏 B** 结构全不同：B1=2 级 Dec3+Mux8(8 输出, nand3/invenTx8 族)；B2=3 级 Dec4+PreBuf+Mux4(4 输出, invFx1+nand2Tx1)；B3=1 级 mux_16(16 输出, 下划命名)。
- **check.py** 17 断言(a-q)：交付形态/编译/B1 运行/必需键/input_signal/output_signals 集合/path_subckts 有序/n_path/n_bottlenecks/series_resistance 存在/n_recommendations/invFx×2 推荐/ratio>=1.2/交叉输入守卫(A path!=B1)/泛化(B2 3级+B3 1级)/A-only 泄漏闸门/3 次幂等。inline 参考解析器(ref_parse)独立算 gold。
- 自验: ref PASS 17/17 + 4neg(stub/empty/coredeleted/printexpected)全 FAIL NEG_RC=0 + §4.9三假(空壳=empty/print-expected/core-deleted)全 FAIL + byte-sync(sha 1443db02…)。
- jsonl B 217→218 · ledger covered 218→219 (spice_sim 175→176)。

## reject/留备选（11-10 cron diff 6 fresh 余 5）
- vuj95(marryma@pkn002 mc=1126): file-search 咨询(SA/SWD 版图查找)，无 produce → parked
- v5icx/x1iee(yanxvwei@pkn002 mc=71): anasim_pro GUI 多轮演进，非单轮自包含 → 留 B-synthesized 候选
- fyfm9(yanxvwei@pkn002 mc=54): 245msgs 多主题，过大 → 留
- xgfh1(curryxu@pkn001 mc=51): finesim 报错 consulting → parked
- ltkg1: 本轮交付 ✓
