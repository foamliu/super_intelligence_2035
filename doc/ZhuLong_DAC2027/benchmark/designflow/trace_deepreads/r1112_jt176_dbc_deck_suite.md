# r1112 deepread — jt176 (e0039786@hfhds201, mc87, spice_sim)

**session**: 1794816898157_jt176 (107 msgs, 523KB) — snapshot hourly-new.2026-11-22_2100
**user**: e0039786 (hfhds201) — DBC varactor characterization engineer
**scan keywords**: cellview:234 dbcreaterect:202 virtuoso:114 hspice:65 techfile:40 ...

## 真实意图（Phase 1, msg 0-19）— B 域 spice_sim, 选中

U#0 给参考 Hspice 激励文件 `nelvt_dbc_l6_1_removeV0GD.sp`（DBC nELVT varactor C-V characterization deck：
`.LIB` 35H_DBCFS_Model_PF_v0d1_Rev04.lib × 3 corners (tt_mos_varactor_dbc/tt_diode_bjt_dbc/tt_res_dbc)，
`.inc` nelvt_dbc_l6_1_removeV0GD.dspf 提取网表，12 个未用节点 vv1..vv12 端接到 0，
`.param` 14 个器件参数 (devtype/vdlin/vdd/ith/dv/lr/lrr/nfinr/wgaar/th/wr/Vssp/area1/area2)，
3 个源 VVD/VVS/VVG(NM2_D/NM2_S/NM2_G)，`.AC DEC 1 100K 100K SWEEP VVG -0.75 0.75 0.05`，
`.meas AC Cgg_/Cgs/Cgd/Cgc` 用 `II(Vx)/(2*pi*1e5*0.1*1e-15)` 公式），
要求「**参考这个激励文件帮我生成一系列测不同电性的 sp 文件**」。

assistant 生成 **9 个 .sp deck**（DBC_01..DBC_09），每个保留参考的 header（.options/.LIB/.inc/.param/vv 端接），
只换 analysis+.meas 部分：
- 01 cv_gate: C-V vs 栅压（同参考，100kHz AC sweep VVG）
- 02 qfactor_freq: Q vs 频率（固定 VG=0.3, AC 10k..10G, Q=|Im|/|Re|）
- 03 qfactor_vg: Q & Cgg vs 栅压（5GHz, sweep VVG）
- 04 cv_freq: 电容频率色散（固定偏置, AC 1k..10G）
- 05 rs_series: 串联电阻 Rs/Cs 提取（Rs=Re(1e-3/II(VVG)), Cs=-1/(2πf·Im(Zin))）
- 06 leakage: 栅/端漏电 I-V（DC sweep VVG -1.5..1.5）
- 07 temp_cv: 变温 C-V（.alter 切 .temp 25/125/-40）
- 08 tuning_range: 调谐范围（Cmax@-0.75, Cmin@+0.75, Cmax/Cmin）
- 09 id_vg: 转移 Id-VG（DC sweep, VDS=0.2V）

## Phase 2 (msg 20-106) — C 域 layout (SKILL pcell), 拒

U#20 转向 SKILL pcell 生成（DUT_Common.il + 6 Front_*.il 测试版图 DUT：CVDUT/RFDUT/BKDUT/TempDUT/DummyOpen/DummyShort），
后续讨论 GDS 导出。属 layout/Virtuoso（shard C），不计本 case。

## reframe（B 域, L1 纯 Python 复刻）

**DBC 变容管 Hspice 表征 deck 套件生成器** `dbc_deck_suite.py <spec.json> <out_dir>`：
读 spec（header: options/temp/model_lib_path/model_corners/inc_netlist_path/unused_nodes/params/terminals；
tests: 每条 {kind, filename, kind-specific params}），按 kind 渲染对应 .sp deck，
保留 header 不变，只换 sources/analysis/.meas。9 种 kind: cv_gate/qfactor_freq/qfactor_vg/cv_freq/rs_series/leakage/temp_cv/tuning_range/id_vg。

**case = EDA-Eval-DesignFlow-DBCDeckSuiteGen-001**（spec 驱动多 deck 套件生成，与 r1111 网表解析器方向相反；与 r1094 单 .meas 块生成器区别在本 case 是完整多 deck 套件 + 保留参考 header 不变）。

**A**: e0039786 真实参考 deck 结构（35H_DBCFS_Model_PF_v0d1_Rev04.lib, nelvt_dbc_l6_1_removeV0GD.dspf, NM2_D/S/G, 12 ncr_* 节点, vdd=0.75, 9 kinds 顺序 01..09）。
**hidden B**（五重 anti-hardcode）: ①model_lib_path 不同 ②model_corners 名不同 ③inc_netlist_path/dspf 不同 ④terminals 不同(ND/NS/NG) + unused_nodes 不同 ⑤params 值不同(vdd=0.9, nfinr=2...) + temp=27 + tests 子集重排(6 kinds, 不同顺序/文件名)。
