# trace_deepread: 1zrj5 — bitline leakage sim deck assembly

- **session**: `1795670295949_1zrj5` (fxian@hfeg0plg74, mc=326)
- **domain**: schematic_netlist (netlist:874 + pyaether:425 + schematic:273 dominant)
- **claim**: D-ledger r1654, schematic_netlist
- **verdict**: FRESH → reframe → `BitlineLeakDeckAssembleProduce-001`

## 真实任务 (218 msgs)

用户 fxian 要求在 circuit `Blen_Ileakage_test_xian` (lib `drgqa_cmos_work`) 上分析
**位线漏电流 Ileakage**，目标节点 `Blb<3>` / `Bla<3>` / `Blb<2>`，要求使用与
full-chip top-level 仿真**相同的 model 与条件**。

agent 路径：
1. pyAether 沙盒 (10.129.8.112:41522) 打开 schematic，提取 nets/insts/pin→net 映射
   - nets: `vad2e! vss! vcc! net0 Sel_a Bla<3> Blb<3> Sel_b net1 vad2o! Iso NCS
     Bla_local<2> vad2! Csl Sel SaBlb<2> Blb_local<2> PreEq SaBla<2> Io<2> IoN<2>
     PCS OcEn Blb<2> vdleq! vblhbk!`
   - 关键 inst→master: MN10/MN11→`ntnlvio_blen`(位线 pass NMOS), MN12/MN13→
     `ntnlvio_preeq`, MN28/MN20/MN27/MN21→`ntnlvio_sa`(sense amp), I3/I2/I4→vcc
     (电流源/IO), I38→vcc, I24→vad2o, I26/I27/I28/I29→vss
   - 目标位线连接: `Bla<3>`={I3.noConn, MN11.S}, `Blb<3>`={I2.noConn, MN10.S},
     `Blb<2>`={I4.noConn, MN28.S}  → 漏电路径 = 位线→MN.S→MN.D→电源, 控制信号
     Sel_a/Sel_b/Sel/Csl/Iso/NCS/PCS/OcEn/PreEq 决定 pass 管开关态
   - 开关实例 I_switch_0..N: term1→vss!, term z→Sel_b/Sel_a/Sel/Csl/Iso/... 即
     把控制信号 force 到 vss(off 态) 以测漏电
2. pyAether 沙盒中途崩溃 (port 41522 worker down, 反复 30s 超时 U#59/61/63/105…)
3. 转 CLI `emy2netlist drgqa_cmos_work Blen_Ileakage_test_xian schematic
   -t spice -f hspice -flat -glo -delim '<'` → **成功**导出
   `/home/fxian/leak_sim/Blen_Ileakage_test_xian.sp`
   - header: `.GLOBAL vad2 vad2e vad2o vblhbk vcc vdleq`
4. 考察 full-chip model `V1_HK_Model_D5_v0d5_Rev04.sp` (Rev04, 8.8KB) +
   `incFile_V1_HKMG` (18.6MB symlink) → **5 个 PVT corner**:
   TT 1.1V/25C, FF 1.3V/110C, SS 0.94V/-40C, SS 0.98V/-40C, SS 0.98V/110C
5. 考察 full-chip netlist `MatrixRun_Netlist_SpfBA_20260114PM_Fullchip_DLL1/
   drgqa_top_WOWTOP_config_SpfBA_trans.netlist` (`.GLOBAL vad2e! vad2o! …`) 与
   `force_power.inc` 电源 force 源 (`vxxx net! 0 dc=pvcslp power=0`)
6. 用户 U#179 沮丧 ("half a day, no results")；session 结束于 msg 217 考察
   force_power.inc — **没有任何合成完成, 没有真正跑 finesim**

## 可合成核心 (synthesizable core)

漏电仿真 deck 的**装配**：从结构化输入拼出完整 hspice/finesim deck：
1. 电路拓扑 (inst + nets + pin→net, 即 pyAether 提取的那份) → subckt 实例
2. 5 个 PVT corner (name/vdd/temp) → `.lib`/`.endl` per-corner 块, vcc 按 corner.vdd 缩放
3. 电源 force (per-net → dc 电压) → Vsource 行
4. 控制信号 off 态 force (Sel_a/Sel_b/… → vss=0) → 控制电压源
5. per-target-node `.meas` 漏电流语句 (Blb<3>→i(MN10.S), Bla<3>→i(MN11.S), Blb<2>→i(MN28.S))
6. `.dc`/`.tran` 分析 + `.end`

## reframe

把"开 Aether 沙盒读 schematic + 拼真实 finesim deck"reframe 为 **spec-JSON 驱动纯
Python deck 装配器** `assemble_leak_deck.py(spec)->leak_deck.sp+manifest.json`：
spec 给 {globals, corners[name,vdd,temp], supplies[net,voltage], vdd_net,
control_signals, control_off_value, instances, target_bitlines[node,meas_inst,
meas_term], analysis}；装配器输出 deck 文本 + 结构化 manifest（corners /
supply_voltages_by_corner(vdd_net 按 corner.vdd 缩放, 其余固定) / control_forces /
meas_targets(meas_name=Ileak_<sanitized node>))。无 EDA 二进制依赖, LIVE-NA,
judge_layers=[L0,L1]。

与既有 D case 区别：
- r1653 NetNameConsistAudit = 网名一致性双向核 (partition+set diff)
- r1651 TrTfMeasGen = tr/tf edge .meas 生成 (per-lane per-edge 阈值)
- r1643 SpfPortMismatchPatch = SPF 端口对齐 patch
- **本 case = 漏电 deck 装配 (PVT corner × supply × control force × per-node meas)**，
  切面 = 多 corner 电源缩放 + 控制 off 态 force + 位线 meas 目标映射，独立

## hidden-B (token-structural-disjoint)

sense-amp 漏电测试 `Sao_Leak_test_y`：globals [vsan,vsap,vlat,vblh,vcc,vss]，
3 corner (TT/FF/SS, vs A 5 corner TT/FF/SS1/SS2/SS3)，control [LAT,CSL,PCH,
ISO_SA,SAEN] (vs A [Sel_a,Sel_b,Sel,Csl,Iso,NCS,PCS,OcEn,PreEq])，target
[San<2>/MNS0/S, Sap<2>/MNS1/S, San<3>/MNS2/S] (vs A [Blb<3>/MN10, Bla<3>/MN11,
Blb<2>/MN28])。A-hardcoder 喂 B → corners 5≠3 / meas 节点名全错 / control 9≠5。

## negatives (trio distinct first-fail)

- print_only → cond c (不写 leak_deck.sp/manifest.json)
- core_deleted → cond d (manifest.corners=[] ≠ gold 5)
- hardcode_a → cond n (B corners 5≠3)
