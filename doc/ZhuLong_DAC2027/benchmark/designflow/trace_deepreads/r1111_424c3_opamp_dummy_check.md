# r1111 deepread — 424c3 (tongni@hfeg0plg65, mc67, spice_sim) → OpampDummyCheckProduce-001

## trace provenance
- session: `/home/tongni/.cline/data/sessions/1794798222398_424c3/1794798222398_424c3.messages.json` (336KB, 62 msgs, 31 user turns)
- reachable: .75 ssh e0031982@hfeg0plg65 OK (BatchMode); /proj/dscqa netlist Permission denied (owned by minghuiz) — 深读基于 assistant 全量读取后的最终报告 (msg 61)
- cross-shard 4-shard ledger dedup: 424c3 全 NONE ✓ (b_fresh_1123_4shard_218.tsv top-19)

## 用户真实意图
U#0: "解析这个电路运放的模块，对运放 dummy 要做检查" + 网表路径
`/proj/dscqa/V0/workdir/minghuiz/simulation/zmh_AI_VtscRef_standard_tb_sim_schematic_ALPS/zmh_AI_VtscRef_standard_tb_sim_schematic.netlist`

## assistant 轨迹
read_files 全量网表 → grep .SUBCKT AG_VtscRef → 多次 editor 写 analyze_amp_dummy.py (过程 corrupt 几次) → run_approved_command python-runner → 最终出报告 (msg 61)

## 关键产物（报告 msg 61 摘要）
层次: VtscRef_standard_tb_sim → AG_VtscRef → AG_VtscRefAnalog → {AG_VnocVdleqVtscRefAmpCore(运放核心), AG_VtscRefRES(电阻阵列), AG_VtscRefCom(补偿), AG_GlbBiasGenLoc(偏置)}

运放核心 AG_VnocVdleqVtscRefAmpCore (两级 Miller):
- 差分对 XMMN4<15:0>(Pos→n1) / XMMN5<15:0>(Neg→nCom), 共尾 ntail, w=6u l=3u ntn_m, 各 16 finger
- 尾电流 XMMN9<1:0>(HbiasV) / XMMN3<1:0>(EnVV)
- NMOS cascode XMMN8<3:0>/XMMN10<3:0>
- PMOS 电流镜 XMMP2<7:0>/XMM4<7:0>/XMM5<7:0>/XMMP1<7:0>(二极管)
- 使能 XMM6(pmirror→EnVV→VDD)
- ⚠ 运放核心内**无 G=S 的 MOS dummy**，所有 XMM 都是功能管

电阻 dummy (所有端子短接 inh_vss):
- AG_VtscRefRES: XI_AG_VtscRefRU_10<4:0> (5×RU) + XI_AG_VdlEqRefRESUX2_IPD_212<4:0> (5×RUX2) = 10
- AG_GlbBiasGenLoc: XI_AG_GlbBiasResUnitX0P5_2<7:0> = 8
- 合计 18 电阻 dummy

功能非 dummy: AG_NmirUnit_IPD_* 偏置复制 (net 不同), XMM6/XMMN3/XMMN9 使能/偏置 (gate 接信号非源)

## dummy 判据 (从报告提取)
- 电阻 X 例化: 所有端子(net)接同一 net → dummy
- MOS M 例化: G==S (报告称 "G=S 的 dummy 器件", "所有端子短接的 dummy") → dummy；功能管 gate 接真实信号排除
- 运放核心识别: 名字含 Amp + 有 MOS 例化

## reframe
spec 驱动 L1 纯 Python SPICE 网表解析器 opamp_dummy_check.py:
- parse .SUBCKT 块、X 例化、M 例化
- opamp_core = 名字含 'Amp' 且 m_inst>=1
- X dummy: nets 全相同; M dummy: d==g==s
- 输出 {subckts, opamp_cores, dummy_devices, summary}

## case 落库
- case_id: EDA-Eval-DesignFlow-OpampDummyCheckProduce-001
- A (visible): AG_VtscRef 结构, 10 subckts, 1 opamp core, 18 x-dummy / 0 m-dummy
- hidden B: VrefGen 结构 (异 IP/异 opamp 名/异 tied net avss), 9 subckts, 1 opamp core (TwoStageAmpCore), 12 x-dummy + **1 m-dummy (MXDUM0, D=G=S=avss, 核心齿 A 无)** = 13
- 五重 anti-hardcode: ①IP VrefGen vs AG_VtscRef ②opamp TwoStageAmpCore vs AG_VnocVdleqVtscRefAmpCore ③tied net avss vs inh_vss ④B 含 1 MOS dummy A 含 0 ⑤dummy 数 13 vs 18 + 子电路分布异
- check.py 16 条 (a-p), ref 16/16 PASS, NEG 3/3 FAIL (§4.9 三假齐), 3-seed sha256 确定性 ✓

## 自验
- REF on A: n_subckts=10, cores=[AG_VnocVdleqVtscRefAmpCore], 18 x/0 m, dummies_by_subckt={AG_VtscRefRES:10, AG_GlbBiasGenLoc:8} ✓
- REF on B: n_subckts=9, cores=[TwoStageAmpCore], 12 x/1 m, dummies_by_subckt={TwoStageAmpCore:1, VrefGenRES:7, VrefGenBiasGen:5} ✓
- check.py (B) PASS; negative_selftest 3/3 FAIL ✓
