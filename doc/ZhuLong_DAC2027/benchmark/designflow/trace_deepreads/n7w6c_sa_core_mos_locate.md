# trace deepread — n7w6c SA Core MOS Locator (yuyingc @ hfeg0pkn001)

## trace source
- user: yuyingc · host: hfeg0pkn001 (10.129.2.13) · session: 1793623698314_n7w6c.messages.archive.json (1.5MB, 486 msgs, archived 2026-11-03)
- 11-05 重扫令：上轮(21:2x) peek .messages.json 判 "FineSim cmos_spf vs cmos_array_spf senb.sp diff debug 暂缓 archive 待查"；本轮 archive 深查 → CLEAN A-faithful
- tool freq: run_approved_command×90, editor×88, read_files×12 — 全程 SPICE deck 批量改+FineSim 仿真监控

## 用户意图轮（A-faithful prompt = U#38 msg#371 逐字）
「帮我查看 v(blasec28<562>) 这个信号线所在的SA中决定了上拉和下拉能力的4个mos管在Netlist网表里是哪四个」
- U#0/U#1/U#2/U#3 = 批量 sed 改 .inc 路径/加 .meas 行/删 RCC（mechanical L1，不入 prompt）
- U#4/U#7/U#25/U#31 = fqueueAry 仿真监控（run_approved_command bjobs，不入 prompt）
- U#38 = 提出「定位 SA 4 核心 MOS」需求，无根因/无修复方向 → 符合 A-档选轮 ✓
- U#39/U#42/U#43/U#44/U#45 = 用户后续追问「mismatch 是否加到这 4 管」+ 指出「senb/senw 收敛同 Vtarget 不正常」+ delvtoBL2_* 对应位 → 这些轮含根因/修复方向，不入 prompt

## 金标准（assistant msg#390）
层次追踪 sim_top → XI_msaq_fBCC_02 (msax320_fbcc) → CXSA1x4_die2_fbcc SA，每个 bit 的 4 核心管：
- 2 NMOS 下拉 XMMN0/XMMN1：drain=SaBla<k>/SaBlb<k>，gate=交叉 bitline(Blb_local/Bla_local)，NCS 使能，inh_vss body，delvto=delvtoBL<k>_NsL/NsR*0.5
- 2 PMOS 上拉交叉锁存 XMMP7/XMMP8：drain=SaBla<k>/SaBlb<k>，gate=交叉 Sa 节点(SaBlb/SaBla)，PCS 使能，inh_vblhbk body，delvto=delvtoBL<k>_PsL/PsR*0.5
- 关键 trap：(a) 顶层 Blasec28<562> 须经层次端口位置映射到 SA 的 Bla<k> bit (b) 反转端口序时不能假设 Bla<3> 总是 arg[0] (c) 4 管须由交叉耦合结构+delvto 参数辨识，非实例名 grep (d) 他 bit(0/1/3) MOS / 无 delvto precharge-iso-colsel / decoySA 实例 / parasitic RC 诱饵须排除

## 合成（本 case）
- case_id: EDA-Eval-DesignFlow-SaCoreMosLocate-001 · domain spice_sim · track faithful · layer L1
- A 网表(可见)：合成 SPICE PEX，sim_top→XI_sa562→CXSA1x4_die2_fbcc(4bit SA)，Blasec28<562>→arg[1]→Bla<2>→bit2→delvtoBL2_*；含 he-bit(0/1/3) MOS 诱饵、无 delvto precharge/iso/colsel 诱饵、parasitic R/C 诱饵、decoySA(连 BlaDummy) 实例诱饵
- hidden B：结构不同——反转 SA 端口序(Bla<0..3>)、重命名 SA subckt(CXSA1x4_die2_fbccB)+模型(ntnlvio_saB/ptnlvio_saB)+核心 MOS 实例名(XN0_b3/XN1_b3/XP0_b3/XP1_b3 vs A 的 XMMN0_2/..)、不同 bit(3)、2 个 decoySA(规模不同)、不同 w/l
- reference: sa_core_mos_locate_ref.py（解析 .SUBCKT+X-instance，定位含 top_signal 的 SA 实例→端口位置映射→bit→过滤 delvtoBL<bit>_* 的 4 核心 MOS→交叉耦合验证）
- check.py 15 断言(a-o)：zip含1.py/py_compile/B合法dict+键/4条/2N+2P/delvto全匹配delvtoBL<bit>_{NsL,NsR,PsL,PsR}/bit_index==3+sa_subckt+sa_instance(反转端口序)/NMOS交叉输入/PMOS交叉耦合锁存/共享SA节点/角色接线(NCS+vss/PCS+vblhbk)/实例集=={XN0_b3..}/A交叉输入(bit2+delvtoBL2)/A≠B/3x幂等sha256
- 自验：ref PASS 15/15 ✓ + 4 negative(empty→c/print_expected→m/hardcode_a→g/naive_all_delvto→d)全 FAIL distinct ✓ + §4.9 三假(empty/print_expected/hardcode_a)全 FAIL ✓ + 断言闸门 15==15≥8 ✓ + jsonl test==disk check.py roundtrip ✓
- jsonl B 188→189 · ledger mark case (covered 190→191, spice_sim 149→150)
