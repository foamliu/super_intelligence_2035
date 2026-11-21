# e692a — DBC nELVT varactor HSPICE 多电性测试 .sp deck 生成 (r1001 落库)

- **session**: 1794884424309_e692a.messages.json
- **user**: e0039786 @ hfeg0plg54 (10.129.35.73)
- **match_count**: 339 (summary_20261121_151844.tsv); keywords: hspice:309; dbcreaterect:611; cellview:419; techfile:233; netlist:104; ddgetobj:72; dbopencellviewbytype:72; drc:53; cadence:47; dbcreatepolygon:45; transistor:42; schematic:40; dbcreatepath:40; pex:38; pdk:36; cmos:29; .gds:28; gdsii:21; lvs:19; calibre:11; mosfet:5; synopsys:4; icfb:3; aether:3
- **domain**: spice_sim（msg 0-19 子任务；会话主体后续 drifted 到 layout/gds→il/pcell，属 shard C）
- **ledger status**: case (r1001, 2026-11-22) — EDA-Eval-DesignFlow-DbcVaractorSpTestGen-001
- **msgs**: 439 total / 36 real user_input / 194 assistant
- **fresh**: ✓（e692a 不在 4-shard used_slugs；同 e0039786 的 ilv08/8p2am 是 3 分钟内近-dup，仅取 e692a 一题）

## Trace intent (U[1] @msg0, the primary distinct spice_sim sub-task)

用户原话（msg 0，附参考激励文件 `nelvt_dbc_l6_1_removeV0GD.sp`）：
> 这是我进行Hspice仿真的激励文件，你参考这个激励文件帮我生成一系列测不同电性的sp文件

**背景**：e0039786 在做 DBC nELVT 变容器（MOS-cap，layout 提取后的 .dspf netlist）的 HSPICE 仿真。参考 deck 是一条 C-V 测试：固定 100 kHz AC 小信号（VVG AC 100mV），扫栅压 VVG -0.75~0.75 step 0.05，用 4 条 `.meas AC` 报 Cgg/Cgs/Cgd/Cgc（fF，表达式 `II(Vx)/(2*pi*f*Vac*1e-15)`）。

**deck 结构**（9 个测试文件共享）：
- 顶部 `$ ===` 注释块（测试名/型号/netlist/说明）
- `.options accurate runlvl=6 post=1 probe=1` + GMIN/measdgt/INGOLD/brief/PSF 等
- `.temp 25`
- 3 条 `.LIB`（35H_DBCFS_Model_PF_v0d1_Rev04 的 tt_mos_varactor_dbc / tt_diode_bjt_dbc / tt_res_dbc corner）
- 1 条 `.inc`（提取后 .dspf netlist：`/proj/lacaa/.../nelvt_dbc_l6_1_removeV0GD.dspf`）
- 12 条 `vv1..vv12` unused-node 终端（ncr_26/26:2/29/29:3/35/35:2/38/38:3/m3:g/m4:g/x1:t1/x2:t1 → 0）
- `.param` 器件参数块（devtype/vdlin/vdd/ith/dv/lr/lrr/nfinr/wgaar/th/wr/Vssp/area1/area2 共 14 个）
- **测试特定段**（随测试目标变化）：
  - 3 条终端源 VVD/VVS/VVG（DC + 可选 AC 幅度）
  - analysis 语句（`.AC`/`.AC SWEEP`/`.DC`）
  - `.PROBE` 行
  - `.meas` 行（2~6 条）
- `.end`

**agent 产出**（msgs 1-19）：9 个 .sp 文件（DBC_01~DBC_09），共享上述 boilerplate，只换测试特定段：

| 文件 | 测试内容 | analysis | .measure 数 | 关键手段 |
|------|---------|---------|------------|---------|
| DBC_01_cv_gate.sp | C-V (Cgg/Cgs/Cgd/Cgc vs VG) | .AC DEC 1 100K 100K SWEEP VVG -0.75 0.75 0.05 | 4 | 100kHz AC，扫栅压 |
| DBC_02_qfactor_freq.sp | Q vs frequency | .AC DEC 20 10K 10G | 2 | 固定 VG=0.3V，扫频，Q=\|Im/Re\| |
| DBC_03_qfactor_vg.sp | Q & Cgg vs VG @5G | .AC DEC 1 5G 5G SWEEP VVG | 2 | 固定 5GHz，扫栅压 |
| DBC_04_cv_freq.sp | C 色散 vs freq | .AC DEC 20 1K 10G | — | 固定偏置，看高频 C 滚降 |
| DBC_05_rs_series.sp | 串联电阻 Rs / Cs | .AC | — | Rs=Re(1/II), Cs=-1/(2πf·Im(Z)) |
| DBC_06_leakage.sp | 漏电 I-V | .DC VVG -1.5 1.5 0.01 | 5 | DC 扫栅压，报 Igate_p/0/n + Id_p/0，加 .option dcvol=1e-3 |
| DBC_07_temp_cv.sp | 变温 C-V | .AC + .alter .temp | — | 25/125/-40℃ |
| DBC_08_tuning_range.sp | 调谐范围 Cmax/Cmin | .AC SWEEP VVG | 5 | 报 Cmax/Cmid/Cmin/tun_ratio，.param +vmax=0.75 |
| DBC_09_id_vg.sp | Id-VG 转移 + 栅漏 | .DC VVG | — | VDS=0.2V |

## 造题方向（reframe → produce 工具）

**工具**：`dbc_sp_test_gen.py`（参数化 HSPICE 测试 deck 生成器）
- CLI：`--spec <spec.txt> --skeleton <skel.sp> --output <out.sp> --report <report.json>`
- spec key=value：test_name / extra_options(;分隔) / vvd_line / vvs_line / vvg_line / analysis_line / probe_lines(;分隔) / measure_lines(;分隔)
- skeleton：共享 boilerplate + `**TEST_BLOCK**` 标记 + `.end`
- 工具在标记处插入测试段：`* ---- <test_name> ----` + 可选 `.option` + vvd/vvs/vvg + analysis + probe + measure
- layer L1，纯 Python 文本模板，无 EDA 二进制

## A/B 防硬编码

- **A（可见）= test 01 C-V gate sweep**：AC @100K，SWEEP VVG -0.75~0.75 step 0.05，VVD/VVS AC 0mV + VVG AC 100mV，2 条 .PROBE AC（I(VVG)/I(VVS)/I(VVD) + V(NM2_G)），4 条 .meas AC Cgg_/Cgs/Cgd/Cgc（param='II(Vx)/(2*3.14159265*1e5*0.1*1e-15)'），无 extra_options
- **B（隐藏）= test 06 gate leakage DC I-V**：.DC VVG -1.5~1.5 step 0.01，VVD/VVS/VVG 纯 DC 0（无 AC），extra `.option dcvol=1e-3`，1 条 .PROBE DC I(VVG)/I(VVS)/I(VVD)，5 条 .meas DC Igate_p/Igate_0/Igate_n/Id_p/Id_0（find I(Vx) when VVG=..）
- A/B 全异：test_name / extra_options / vvg 源(AC vs 纯DC) / analysis 类型(AC vs DC) / sweep 范围(-0.75~0.75 vs -1.5~1.5) / .PROBE(AC vs DC) / .meas 名(Cgg_/Cgs/Cgd/Cgc vs Igate_*/Id_*) 与表达式(param=II(..)/π/f vs find I(..) when VVG=) — 11 个 A-specific 标记 word-boundary 检查

## check.py（12 条 a-l，k_check=12）

1. (a) submit.zip 有效解压含 dbc_sp_test_gen.py 且 py_compile 通过
2. (b) 候选跑 hidden spec B + skeleton B exit 0 且产出 out_B.sp + report_B.json
3. (c) out_B 含 `.DC VVG -1.5 1.5 0.01`（B analysis）
4. (d) out_B 含 `.option dcvol=1e-3`（B extra option）
5. (e) out_B 含 B VVG 源 `VVG NM2_G 0 DC 0`（纯 DC 无 AC）
6. (f) out_B 含 `.PROBE DC I(VVG) I(VVS) I(VVD)`（B probe）
7. (g) out_B 含全部 5 个 B measure 名（Igate_p/Igate_0/Igate_n/Id_p/Id_0）
8. (h) out_B 含具体 B measure 行 `.meas DC Igate_p find I(VVG) when VVG=1.5` 逐字
9. (i) anti-hardcode-A：out_B 不含 11 个 A 标记（Cgg_/Cgs/Cgd/Cgc/100mV/0mV/100K/V(NM2_G)/3.14159265/II(VVG)/-0.75，word-boundary）
10. (j) report 字段反映 B（test_name 含 'leakage' / analysis_type=='DC' / n_measure==5 / has_extra_options==True / deterministic==True）
11. (k) 确定性：重跑 out_B.sp 字节一致
12. (l) `.end` + 共享 boilerplate（.inc netlist 行）被保留

## negatives（§4.9 三假 + hardcode-A，全 FAIL）

- neg_fake_empty：空 zip → FAIL b（no .py tool）
- neg_fake_print_only：只 print 不产出 → FAIL b（out_B.sp not produced）
- neg_fake_hardcode_a：硬编码 A（C-V）测试段 → FAIL 25 条（B analysis/option/probe/measure 全缺 + anti-hardcode-A 11 标记全中）

## 自验

- dbc_sp_test_gen_ref.py 打 reference_submit.zip → check.py **PASS 12/12** ✓
- negative_selftest：ref PASS + 3 negs ALL FAIL（28 distinct failure messages）✓
- A-faithful：ref 在 A 上产出与 e0039786 msg-1 真实 DBC_01_cv_gate.sp 测试段逐字一致（除空格归一化）✓

## 会话其余子任务（属 shard C layout/pcell，不在 B 造题）

- U[2] @msg20：参考 Front_DUT.il 写生成其他电性测试 DUT.il（pcell/layout 生成）
- U[3]-U[18] @msg65-221：Virtuoso SKILL 报错调试（fnboundp/dbDUTParams/car/gdsToIl）、layer 映射（93→88, 94→91）、gds→il 转换、INVD4_1_bottom 4-inverter 并联版图几何参数化
- U[27]-U[28] @msg292-296：gds→il SOP 文档 + python 脚本
- U[29]-U[34] @msg310-387：Inverter_Gates.il 删多余 VOG、97 级 RO 电路版图、DRC primary cell 错误
- U[35]-U[36] @msg389-401：SA-WD 专利版图方案（SRAM 宏 SA-WD 组合单元 pcell，SAWD_Cell.il，dbCreateLabel 报错）

以上全属 shard C physical_verify/layout/pcell 范畴，与 B spice_sim 仅 msg 0-19 .sp test-deck 生成这一突破口 distinct。

## 备注

- e692a 与 ilv08(1794882438855)/8p2am(1794878898936) 是 e0039786 在 2025-04-09 06:48-07:00 三分钟内连续三个 session，keyword profile 近-identical（hspice:281/309 + dbcreaterect:576/611），同任务三迭代，仅取 e692a（mc339 最高）造一题，ilv08/8p2am parked as near-dup。
- 本轮（r1001）由 r1000 之后接续；r1000 错误地选了 2vuso（已 in ledger_B 为 SpGen-001 case）造 LdoRefLoadStepStimGen-001 近-dup，本会话发现后 revert，重做 fresh 候选筛选（修正 used_slugs 过滤 bug：之前用 bare slug grep 但 used_slugs.txt 存 `<slug>.messages.json` 带后缀，导致 2vuso 误判 fresh），重新选 e692a 造 DbcVaractorSpTestGen-001 落库。
