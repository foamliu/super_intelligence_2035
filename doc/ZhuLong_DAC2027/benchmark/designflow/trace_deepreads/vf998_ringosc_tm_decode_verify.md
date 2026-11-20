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
