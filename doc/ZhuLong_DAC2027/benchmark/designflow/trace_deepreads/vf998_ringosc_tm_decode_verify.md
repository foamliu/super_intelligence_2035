# trace_deepread: vf998 daiweilu@hfeg0pgn145 — RingOsc testmode decode verify

- session: `1794903718405_vf998.messages.json` (1.3MB, 220 msgs)
- user/host: daiweilu / hfeg0pgn145 (10.129.35.244)
- match_count: 210 ; keywords: cmos:710;netlist:433;verilog:344;analog:190;transistor:27;schematic:14;pex:9;rtl:7;spectre:5;mixed-signal:4;lib.defs:4;waveview:3
- cwd: `/home/e0047434/work/std_cell/autocell/...` (e0047434 是另一用户; daiweilu 在 /proj/ddgoa/V0/simdir/verilog/daiweilu/verilog.lpddr5.ddgoa.1106/)
- domain: analog_context (process monitor / RingOsc testmode) + schematic_netlist (gate netlist decode)

## 用户真实意图（13 个 testmode 验证问答）
| U# | testmode | 用户原话 |
|----|----------|---------|
| U#0 | cm0_ts_RingOscCP90Sel<3:0> | 验证…ChanEdge Left Process Monitor Type Select + 4bit译码表 + netlist/pattern路径 |
| U#46 | (仿真后) | 我跑完仿真了，我该看哪个信号 |
| U#48 | cm0_ts_CrackMonEn | 置0开analog/置1开digital测试方案，如何验证 |
| U#81 | cm0_ts_VintReadSel | Vintcore/Vintbus trim code readout, 怎么验 |
| U#106 | TM_ChipID_FabID_CorePara | 给pattern，告诉该看哪几个信号 |
| U#117 | cm2_ts_BCCheckbit3NotBlown | 实现broadcast的自检功能 |
| U#137 | cm1_io_KillPPRDis | 默认0 disable除MRW外所有命令, 打开后enable KillPPR, 正确信号应该是什么样 |
| U#149 | cm1_id_SCmosDataWCKOSCFooter | 控制vsszftwckosc的scmos数量, 0=100%开启, 1=开50% |
| U#169 | (BCCheckbit3) | 加入broadcast过程, 看哪个信号判断broadcast成功 |
| U#193 | (broadcast) | broadcast链条在电路中的信号位置 |
| U#202 | (BCCheckDataBAForCPtest) | 为什么=0时FsBcTkIn/Out还是在传 |
| U#212 | (BCCheckbit3) | 这个testmode到底在验什么, 6个fuse位不是我在pattern里自己烧的吗 |
| U#218 | (BCCheckbit3) | 实际流程中6个位是每次广播后读回的吗 |

## 选定造题轮: U#0（A-faithful）
理由: 最自包含 — 用户明确给出 4bit 译码表(9 codes) + netlist/pattern 路径，验证译码逻辑与表是否一致。
助手(A#1-A#45)静态追踪 netlist (V0_WOWTOP, 38万行):
- RingOscCtrl_ArrayCP (L348699-348833): cm0_ts_RingOscSel[3:0] 经 buf→cm_RO[i]=S[i], inv→cm_ROF[i]=~S[i]
- 9 个 RingOscDecDiffSite (L59762-59783): SelEn = SelA&SelB&SelC&SelD&SelE (nand3+nand2→nor2), SelE=SCmosOn 公共使能
- 逐位代入: 每个 decoder 的 SelA-D 接 cm_RO[i](=>S[i]=1) 或 cm_ROF[i](=>S[i]=0), 恢复激活 code
- A#45 验证结果: 9 codes 全部与用户表一致 ✓

## 金标准译码表 (trace A#45)
| S<3:0> | en_signal | 译码项(SelA..D) | monitor_type |
|--------|-----------|-----------------|--------------|
| 0001 | en_invx1       | ~S3,~S2,~S1, S0 | invx1 |
| 0010 | en_invx1_pgN   | ~S3,~S2, S1,~S0 | invx1 pgn |
| 0011 | en_invx1_pgP   | ~S3,~S2, S1, S0 | invx1 pgp |
| 0101 | en_invGFx1     | ~S3, S2,~S1, S0 | invgfx1 |
| 0110 | en_invGFx1_pgN | ~S3, S2, S1,~S0 | invgfx1 pgn |
| 0111 | en_invGFx1_pgP | ~S3, S2, S1, S0 | invgfx1 pgp |
| 1001 | en_invYx2      |  S3,~S2,~S1, S0 | invYx2 |
| 1010 | en_invYx2_pgN  |  S3,~S2, S1,~S0 | invYx2 pgn |
| 1011 | en_invYx2_pgP  |  S3,~S2, S1, S0 | invYx2 pgp |

## synthesized-reframe
真实 NFS 1.5GB+ V0_WOWTOP 网表不可沙盒 → 紧凑 Verilog fixture (ringosc_decode_A.v):
保留真实模块名 RingOscCtrl_ArrayCP_A / RingOscDecDiffSite_A + 真实 select cm0_ts_RingOscSel + buf/inv RO/ROF 结构 + 9 个 I_dec_<code> 译码器 + 真实 en 信号名 + SCmosOn + nand3/nand2/nor2 译码逻辑。
produce-script verify_testmode_decode.py: 解析 ArrayCP select 端口宽 + buf/inv RO/ROF map + 每个 DecDiffSite 的 SelA-D 连接 → 逐位恢复 code → 对照 spec.expected_decode → JSON 报告。
hidden B: testmode cm0_ts_OscNdXpSel / select cm0_ts_OscNdSel / osc_RO / osc_ROF / PwrGateOn, 6 译码器 codes{0001,0010,0100,0101,1000,1010}, flavors oscNdx1/oscNdx2/oscPdx1/oscPdx1_pgL/oscPdx2/oscPdx2_pgL。token 与 A 完全不相交。

## 自验
- ref 14/14 PASS on B + ref on A 产 A gold 9/9 matched 一致 + 3 neg(empty→FAIL b/print_only→FAIL h/core_deleted→FAIL g)全 FAIL NEG_RC=0 + §4.9 三假全 FAIL
- k_check=k_rationale=14>=8 GATE PASS ✓
- check_sha256 ae1acd30... check_size 9196
- case_id: EDA-Eval-DesignFlow-RingOscTmDecodeVerify-001 (analog_context, A-faithful)

## 后续 sister-turn 造题记录

### r1035 U#149 cm1_id_SCmosDataWCKOSCFooter (WckOsc footer 50/50 ratio)
- 机制类: 1-bit footer RATIO (A/B 两组 footer 管子, Footer=0->100% / Footer=1->50%)
- case_id: EDA-Eval-DesignFlow-WckOscFooterRatioVerify-001 (analog_context, A-faithful)

### r1043 U#81 cm0_ts_VintReadSel (Vintcore/Vintbus trim code readout)
- 机制类: 1-bit ENABLE GATE pass-through (CPSeli[i]=MdCPSel[i]&VintReadSel)
- case_id: EDA-Eval-DesignFlow-VintReadSelGateVerify-001 (analog_context, A-faithful)

### r1044 U#48 cm0_ts_CrackMonEn (analog/digital test scheme switch)
- 机制类: 1-bit COMPLEMENTARY DUAL-ENABLE (CrackMonEnF inv -> analog ref-cap; CrackMonEn + CrackMonEnF -> digital comparator)
- case_id: EDA-Eval-DesignFlow-CrackMonAnadigSwitchVerify-001 (analog_context, A-faithful)

### r1052 U#137 cm1_io_KillPPRDis (command-filter gate) ← 本轮
- 用户原话(会话 idx 137, 用户第 73 轮, A-faithful 逐字): 「验证cm1_io_KillPPRDis，默认为零，disable除MRW外所有命令（KillPPR信号），打开之后，可enable KillPPR信号，正确信号应该是什么样」
- 助手验证结论(idx 146): PPRKill 模块(L481438, 实例 I_PPRKill_15 在 CmdDec_PN1p76 I_CmdDec_PN1p76_646 L560749 内); 非 MRW 命令分两组 nor 活跃检测 net8={Act,Pre,MRR,RDC,RFF,WFF} net0={RdInit,WrInit,CasPre,Mpc,Rfsh,SelfRfsh}; KillPPR=aoi21(net8,net0,PprKillEnN)=PprKillEn&ACTIVE; AllCmd=nand3(net8,net0,cm1_io_KillPPRDis); 金标准: Dis=0->KillPPR 恒 0(masked)+AllCmd 强制 1, Dis=1+PprKillEn=1+任一非MRW命令->KillPPR 拉高脉冲, AllCmd=ACTIVE; MRW 是安全隔离例外命令
- 机制类: 1-bit testmode COMMAND-FILTER GATE (two nor2 command-detection groups + nand3 testmode mask + aoi21 trigger gate) — 与 4 个 sister 机制类 pairwise 正交 (DECODER/RATIO/ENABLE-GATE/DUAL-ENABLE)
- 三闸门全 PASS: (1) structure orthogonal (2) 17 不可复用断言 (a-q, 含 _gt_parse_module/_gt_parse_testmode/_gt_groups/_gt_simulate 独立重算 + anti-hardcode A-only 17 token 零漏 + B-only 17 token 全现 + 3-seed md5 + A-gold 交叉校验) (3) token 5-way disjoint (A-only vs B-only vs RingOsc-B vs WckOsc-B vs VintReadSel-B vs CrackMon-B 全 pairwise 不相交)
- synthesized-reframe: 紧凑 Verilog fixture ppr_kill_A.v 保留真实模块名 PPRKill_A + 真实 testmode cm1_io_KillPPRDis + 真实触发 PprKillEn + 真实两组命令 {Act,Pre,MRR,RDC,RFF,WFF}/{RdInit,WrInit,CasPre,Mpc,Rfsh,SelfRfsh} + 真实输出 KillPPR/AllCmd + 真实中间网络 net6/net5/net8/net4/net3/net0/ACTIVE + nor2/nand3/aoi21 等价门结构
- produce-script verify_killppr_gate.py CLI `<netlist.v> [-o report.json]`: 解析模块/testmode/trigger/两组命令/两输出/行为真值表(testmode,trigger,any_cmd_active)∈{0,1}^3/summary 三金标准性质
- hidden B ppr_kill_B.v (CmdGate_B/cm1_io_CmdMaskDis/GateEn/GatePulse/MaskAll/Init,Cfg,Scan,Bist,Acc,Load/Refresh,Sleep,Wake,Test,Mode,Calib) token 与 A 完全不相交
- check.py 17 断言 a-q, k_check=k_rationale=17>=8 GATE PASS ✓; ref 17/17 PASS + 3 neg(fake_empty->FAIL b/fake_print_only->FAIL n+q/fake_core_deleted->FAIL j)全 FAIL NEG_RC=ALL FAIL + §4.9 三假全 FAIL
- check_sha256 1fa486cc8bcc216df788eb8507d57cf3ba9446ad2bc7a5a908ddd2fa6ae02e2d check_size 17000
- case_id: EDA-Eval-DesignFlow-KillPPRDisGateVerify-001 (analog_context, A-faithful)

## vf998 sister-turn 覆盖盘点 (截至 r1052)
- 已造 5 个 testmode verify turn: U#0 RingOsc(r1023), U#149 WckOsc(r1035), U#81 VintReadSel(r1043), U#48 CrackMon(r1044), U#137 KillPPRDis(r1052)
- 剩余可造 turn (deepread 表): U#106 TM_ChipID_FabID_CorePara, U#117 cm2_ts_BCCheckbit3NotBlown, U#169/U#193/U#202/U#212/U#218 (broadcast 系列, 同一 BCCheckbit3 机制多角度 — 需判三闸门避免近 dup), U#46 (太薄, 仿真后问看哪个信号), U#137 已造
- 机制类已覆盖: DECODER / RATIO / ENABLE-GATE / DUAL-ENABLE / COMMAND-FILTER-GATE (5 类正交)
