# deepread: jp83r (1794379471399_jp83r) — CXSA DC-sweep deck generation

- user: t0002614 / host 10.129.2.13 / mc=105 / keywords netlist:508 hspice:477 aether:148 waveview:137 pex:133
- 79 msgs, 1.6MB, single-file (directory-format session: 1794379471399_jp83r/1794379471399_jp83r.messages.json)
- domain: spice_sim (hspice dominant); produce-task

## 用户意图（原话）
- msg0: 「根据网表netlist和参考的测试网表test.sp帮我写仿真测试。测试设置：TT工艺角，温度125摄氏度，直流仿真，vad2!=1.4V，Iso管关闭，sel管的栅压固定为1.77V，OC管和PreEq管的栅压扫描1.17-1.77V，看BL上的电压。」
- msg28: 网表换成只含一个SA的小模型，参考改为 sim.sp；静态仿真。
- **msg34 关键澄清**: 「明确一下，是OC管和PreEq管的栅压都为Vdleq，然后Vdleq扫描从1.17到1.77V」⇒ OC 与 PreEq 栅压绑定同一被扫参数 pvdleq。
- msg35: 「先写一个可以跑仿真的网表出来，即使有小问题…满足我上面的要求即可。」
- msg46: 「再写一个python脚本将结果文件sw0里的数据写到.csv文件中，浮点数保留6位小数」
- msg52: 「waveviewer在copy表格数据的时候怎样保证精度」(Q&A, 无产出脚本)

## 电路（CXSA1x4_1C2A 小模型 netlist，msg32）
顶层扁平 SA（drgqa_cmos_core/CXSA1x4_1C2A/schematic），关键管（1-bit, <0>）:
- Iso 管 ntnlvio_iso: SaBla<0>↔Bla_local<0>, SaBlb<0>↔Blb_local<0>, 栅=Iso
- Sel 管 ntnlvio_blen: Bla_local<0>↔Bla<0>, Blb_local<0>↔Blb<0>, 栅=Sel
- SA 核心 ntnlvio_sa: XMMN00 SaBla<0> Blb_local<0> NCS / XMMN01 SaBlb<0> Bla_local<0> NCS (交叉耦合)，栅 delvto 失配
- CSL 管 ntnlvio_csl: Bla/Blb_local→Csl→Io/IoN
- PMOS load ptnlvio_sa: XMMP00/01 SaBla↔SaBlb, 栅=PCS, body=vblhbk!
- **OC 管 ntnlvio_oc**: XMMN04 SaBla<0> OcEn Blb_local<0> / XMMN05 SaBlb<0> OcEn Bla_local<0>（交叉，栅=OcEn）
- **PreEq 管 ntnlvio_preeq**: XMMN0c SaBla<0> PreEq vad2! / XMMN0f SaBlb<0> PreEq vad2!（栅=PreEq, 漏到 vad2!=1.4V）
- 电容 c157-c160 (寄生)

直流通路（Iso 关断时）: Bla<0> —Sel(1.77V导通)→ Bla_local<0> —OC管(OcEn扫)→ SaBlb<0> —PreEq管(PreEq扫)→ vad2(1.4V). 扫 OC/PreEq 栅压 ⇒ 看 BL 被拉向 vad2 的程度。

## 交付物（agent msg38 写入 sim_dc.sp）
完整 HSPICE/FineSim DC-sweep deck:
- .lib TT 角 (主模型 t06.sp TT + incFile bjt_tt/res_tt/nicap_tt/diode_tt)
- .inc "./netlist"
- .inc '/rundata/.../finesim_option' + .option finesim_mode=spicead gmindc=1e-18 gmin=1e-18
- 失配 param delvtoBL*_NsR/...=0mv (理想)
- 电源: vss=0, vblhbk=0.93, vad2=1.4
- SA 控制: viso Iso=0(off), vsel Sel=1.77, vncs/vpcs/vcsl=0
- OC/PreEq: voc OcEn dc='pvdleq', vpreeq PreEq dc='pvdleq', vdelq vdleq! dc='pvdleq'
- .temp 125
- .dc sweep pvdleq 1.17 1.77 0.01 (61 点)
- .probe dc v(Bla<0>) v(Blb<0>) v(Bla_local<0>) v(Blb_local<0>) v(SaBla<0>) v(SaBlb<0>)
- .measure dc vbl_a MAX v(Bla<0>) / vbl_b MAX v(Blb<0>)
- .END

agent 还写了 check_lib.py (验证模型库 TT 段名 + finesim_option 路径存在, 全部 EXISTS)。CSV 导出脚本(msg46) 与 waveviewer 精度(msg52) 为 Q&A/未完成，不入 case。

## A 档可行性
❌ 不可行：真实模型库 /proj/shdc/models/G6/... 与 /rundata/sim_cloud/.../finesim_option 在 .75 对 e0031982 权限受限；真实 netlist 14万行 PEX 扁平。⇒ **B 档**：合成忠实小 SA netlist_A + manifest_A + 隐藏 netlist_B/manifest_B（不同 SA 变体 + 不同 corner/temp/sweep/bias/观察节点），reference = 参数化 DC-sweep deck 生成器。

## case 设计
- task_id: EDA-Eval-DesignFlow-CxsaDcSweepDeckGen-001
- deliverable: submit.zip{dc_sweep_deckgen.py}
- 输入 A: netlist_A (忠实小 CXSA) + manifest_A.json (TT/125C/pvdleq 1.17-1.77 step .01/vad2 1.4/Iso 0/Sel 1.77/OC+PreEq=pvdleq/probe Bla<0> Blb<0>) + task_context.md
- hidden B: netlist_B (不同 SA 变体: 节点 BL0/BLB0/SA0/SA1, 不同 sizing, 不同管型名) + manifest_B (SS 角/-40C/pvoc 0.8-1.6 step .02/vad2 1.2/Iso 0/Sel 1.5/OC+PreEq=pvoc/probe BL0 BLB0)
- check.py 13 断言: subprocess 真跑生成器于 B + 独立解析 deck 各字段复算 (corner/temp/sweep点数/bias值/swept gates 绑定/probe/measure/inc) + A≠B + 3 seed 一致 + 退化空 manifest
