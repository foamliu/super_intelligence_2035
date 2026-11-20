# z5ett — LDO 设计（A-faithful produce 候选，深读完成待合成）

## trace_source
- session: `1792140744683_z5ett.messages.json`
- user: jessegao @ 10.129.2.14
- mc: 137 (aether:512;transistor:224;pdk:169;netlist:129;schematic:99;pyaether:91;calibre:37;dbopencv:25)
- domain: analog_context
- ledger: parked (#334, DEBT:1 — synthesis pending for #335)
- size: 1,048,265 bytes / 233 msgs / 9 user turns / 120 tool_uses

## user turns (verbatim)
- **U#0** [msg0]: 帮我生成一个LDO电路上电压域为1.1V，输出为0.9V，要求其静态功耗10uA以内，PSRR=-20dB @0~100kHz，DC gain大于40db，PHASE MARGIN 大于40度
- U#1 [msg99]: 声明一下，这里的psrr为负值
- U#2/U#3 [msg178/179]: 帮我输出一份电路图及验证报告
- U#4 [msg207]: 完整文档已生成在以下路径： /home/jessegao/Spice_Agent/design/ldo_v1/circuit_diagram_and_verification_report.md这个文件怎么打开
- U#5 [msg213]: 直接帮我把内容输出到终端
- U#6 [msg217]: 我如何看这个电路
- U#7 [msg219]: 2
- U#8 [msg232]: 我怎么操作去生成呢

**A-faithful 判定**：U#0 纯提需求（生成 LDO + 4 项指标），未给根因/未给修复 → 合规 A 档选轮。U#1 仅澄清 PSRR 符号（负值），非根因。U#4 确认产物已生成（user-accepted）。

## assistant tool_uses (120)
- editor: 51, run_approved_command: 29, read_files: 25, list_allowed_files: 10, search_codebase: 2, RAG_MCP_Server__search_apis: 2, get_agent_policy_status: 1

## produced files (17 unique paths in /home/jessegao/Spice_Agent/design/ldo_v1/ + aether/)
- state.json, pre-design.md, **spec.md**, dut_ldo_v1.sp, tb_ldo_v1_ac.sp, tb_ldo_v1_loadreg.sp, tb_ldo_v1_linereg.sp, tb_ldo_v1_psrr.sp, cleanup.sh, design-report.md, fix_psrr_sign.sh, fix_spec_psrr.sh, **verify_psrr.py**, clean_spec.py, **circuit_diagram_and_verification_report.md**, do_cleanup.sh, ../aether/gen_ldo_v1_scheme_aether.py

## real spec.md (extracted)
8 params: VIN(1.0-1.2 typ1.1), VOUT(0.85-0.95 typ0.9), ILOAD_MAX(5mA), IQ(<10uA), DC_GAIN(>40dB), PM(>40deg), LD_REG(<6mV/mA), VDROP(<30mV@5mA). + PSRR 声明: PSRR=20log10(Vout_ac/Vdd_ac), 越负越好, PSRR@100kHz 预计 -5~+10dB (不满足 -20dB). Operating: T 0-85C, corners tt/ff/ss, Cout=2nF ESR=3ohm.

## real dut_ldo_v1.sp (extracted, Rev.B)
```
.SUBCKT ldo_v1 vdd vout gnd vref en
.OPTION POST=2 POST_VERSION=9
* EA: nMOS diff pair (ntn, L=2um)
X1  ea_inp  vref  tail_n  gnd  ntn  w=5u  l=2u  nf=1
X2  ea_inn  vfb   tail_n  gnd  ntn  w=5u  l=2u  nf=1
* pMOS current mirror load (ptn, L=2um)
X3  ea_out  ea_out  vdd  vdd  ptn  w=5u  l=2u  nf=1
X4  ea_inp  ea_out  vdd  vdd  ptn  w=5u  l=2u  nf=1
* bias mirror (ntn_m, ratio 3:1)
X5  tail_n  vb_tail  gnd  gnd  ntn_m  w=6u  l=2u  nf=1
X6  vb_tail  vb_tail  gnd  gnd  ntn_m  w=2u  l=2u  nf=1
Rbias  vdd  vb_tail  290k
* PMOS pass (5mA, <30mV drop)
Xpass  vout  ea_out  vdd  vdd  ptn  w=5u  l=0.3u  nf=200
* Feedback divider
R1  vout  vfb  100k
R2  vfb   gnd  1.1M
* Output cap + ESR
Cout  vout  vout_esr  2n
Resr  vout_esr  gnd  3
.ENDS ldo_v1
```
拓扑: 5T EA (nMOS diff X1/X2 + pMOS mirror X3/X4 + bias X5/X6+Rbias) + PMOS pass Xpass(nf=200) + R1/R2 divider(100k/1.1M, vfb=vout*R2/(R1+R2)=0.825V → vref≈0.825) + Cout2nF/ESR3ohm. Pin order: vdd vout gnd vref en.

## synthesis plan (for #335, B-grade synthesized, portable L1)
**gen_ldo_design.py --spec <spec.json> --outdir <dir>** 读 spec JSON{vin,vout,iload_max,iq_max,dc_gain_min,pm_min,ld_reg_max,vdrop_max,cout,esr,psrr_target,ea_l} emit:
1. `dut.sp` — .SUBCKT ldo vdd vout gnd vref en: 5T EA (diff pair + mirror load + bias) + PMOS pass (W/nf 由 iload_max+vdrop_max 推) + R1/R2 divider (由 vout/vref 推 ratio) + Cout/ESR
2. `tb_ac.sp` — .ac dec + .measure dc_gain + .measure pm (loop gain broken at EA output)
3. `tb_loadreg.sp` — .dc Iload 0→iload_max + .measure ld_reg (vout@0 - vout@iload)/iload
4. `tb_linereg.sp` — .dc Vdd vin_min→vin_max + .measure ln_reg
5. `tb_psrr.sp` — .ac + vac on vdd (supply perturbation) + .measure psrr=20log10(vout_ac/vdd_ac)
6. `report.md` — spec table (8 params + .meas names) + PSRR 负值声明 + verdict 占位

**反硬编码轴**: A/B/B2 vin/vout 全不同 → pass W/nf + R1/R2 ratio + spec.md VOUT 全不同（硬编 A vout 者 B/B2 上结构断言 FAIL）。

**check 12-16 条件**: zip 无泄漏 / py_compile / B-run exit0+非空 / dut .SUBCKT ldo 5 pins / PMOS pass (Xpass ptn 大 nf) / EA diff pair (X1/X2 同型 gate=vref/vfb) / feedback divider R1/R2 + vfb / Cout+ESR / tb_ac .ac+.measure gain+pm / tb_psrr supply perturb(vac on vdd)+.measure psrr / tb_loadreg .dc Iload+.measure ld_reg / report spec table 8 params / report PSRR 负值声明 / 反硬编码 A 无 A 标记+A-run 产 vfb/vref / 跨输入 B2 diff vout→diff R1/R2 / 确定性 3x sha256.

## peer (same trace other intent)
- shard B 未取此 trace（ledger 无 cross-shard note）。z5ett 为 D 独占，无跨 shard 冲突。

## 教训
1. **z5ett 是干净 A-faithful produce + 离线可验好范式**：spec-driven LDO deck+report 生成器，纯文件 in/out，check 验结构不验 sim 结果（无需真跑 SPICE）。
2. **真实 LDO 拓扑可移植**：5T EA + PMOS pass + R1/R2 divider + Cout/ESR 是标准结构，spec→器件参数映射明确（pass W/nf 由 iload+vdrop 推，divider ratio 由 vout/vref 推）。
3. **PSRR 负值声明是强反硬编码轴**：spec.md 必须含 "PSRR 越负越好" 声明（U#1 用户澄清），naive 写正数者 FAIL。
4. **本轮 #334 因时间预算（40min）耗尽未能合成**，DEBT:1，#335 第一件事即合成此 case。
