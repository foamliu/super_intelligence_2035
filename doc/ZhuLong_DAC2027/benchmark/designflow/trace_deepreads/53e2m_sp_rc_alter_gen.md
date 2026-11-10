# Deepread 53e2m — SpRcAlterGen-001

## Trace
- **anchor**: `1793608841437_53e2m`
- **user**: victorq · **host**: hfeg0plg96 · **match_count**: 315 · **mtime**: 2026-11-10
- **session_file**: `1793608841437_53e2m.messages.json` (365 msgs)
- **domain**: spice_sim (IGZO tWL word-line delay simulation, .alter RC-loading merge)

## Real Task (U#1, msg 77)
victorq 原话：
> /proj/drdqp/V0_20260227/workdir/victorq/simulation/tWL_IGZO/tWL_IGZO_1SC1LWL.sp，帮我改上述激励，其中主要的编辑项是：
> .param RpSC=17002.7 / .param CpSC=24.096f / .param TierNum=1 / .param RpC=63.74 / .param CpC=50.475a / .param CCpC=3.22a。
> 上面这些参数项，SC 的参数和 pC 的参数是联动的，我尽可能让大的 SC loading 去匹配小的 PC loading，小的 SC loading 匹配大的 PC loading，
> 保证在不同结构中他们的 tWL 的仿真均一性。所以除了上面这个 SC 和 PC，小的 SC loading 匹配大的 PC loading 参数如下：
> .param RpSC=8546.7 / .param CpSC=11.81f / .param TierNum=1 / .param RpC=79.76 / .param CpC=59.175a / .param CCpC=5.56a.
> 上面这个他们的 WL_len 都帮我 sweep 1024 1536 256 吧。帮我生成上述两种 RC 仿真条件的激励和sweep，保存在原目录下面

U#2 (msg 94): 「两个文件可以 merge 一起用 .alter 来跑吗？」

## Gold Standard (assistant msg 95 — editor tool_use)
生成 `/home/victorq/tWL_IGZO_1SC1LWL_both_alter.sp`（87 行）：

**结构**：
1. Header 注释（DSIM testbench header + MOD 合并说明）
2. `.include` finesim_option vcap_block
3. `.option finesim_mode=spicehd` / `.option PARHIER = LOCAL` / `.option scale = 1`
4. 5 条 `.lib`（T1_HK_Model_PF ss / bjt_ss / res_ss / nicap_ss / diode_ss）
5. `.temp -40`
6. **run0 .param 块**（主 body）：CapO=0.2f / Cgatein=0.4f / Cthick=0.4f / Cthin=0.2f / TierNum=1（common）+ RpSC=17002.7 / CpSC=24.096f / RpC=63.74 / CpC=50.475a / CCpC=3.22a（大 SC + 小 pC）
7. `.include` netlist（VictorQin_Study_LWL_study_SWDarray_schematic_ALPS）
8. `.include` stimulus（VictorQin_Study_LWL_SWDarray_1SWD2SC_V15C_schematic_ALPS/tWLsim/stimulus）
9. 9 条 `.meas tran`：near_rise10/90（v(WL7<3>) val=-650m/2.15）/ twl_near / far_rise10/90（v(wl1_r<192>) val=-650m/2.15）/ twl_far / near_rise50 / far_rise50 / delay
10. `.tran 10p 600n sweep WL_len 1024 1536 256`（=> 1024/1280/1536 三点，两个 run 共用）
11. `.probe v(*)`
12. **.alter 块**（run1）：`.alter` + 6 条 `.param`（RpSC=8546.7 / CpSC=11.81f / TierNum=1 / RpC=79.76 / CpC=59.175a / CCpC=5.56a）——小 SC + 大 pC
13. `.END`

**关键点**：
- 公共 deck（.lib/.temp/.include/.meas/.tran sweep）只写一份（run0）
- .alter 块只覆盖要改的 RC .param，FineSim 依次跑 run0→run1
- WL_len sweep 在每个 run 内部各自做 {1024,1280,1536} 三点
- TierNum=1 在 .alter 块中冗余重复（gold 的做法；本 case 设计为 common 不进 .alter）
- sweep 1024 1536 256 = start=1024 stop=1536 step=256（assistant 在 msg 85 ask_question 确认）

## Case Design
- **case_id**: EDA-Eval-DesignFlow-SpRcAlterGen-001
- **domain**: spice_sim · **layer**: L1（单文件 Python 脚本，纯文本处理，不真跑 FineSim）
- **deliverable**: sp_rc_alter_gen.py（CLI: `<base.sp> <rc_config.json> <out.sp> <out_report.json>`）
- **asset A**: sample_base.sp（单 RC 条件 deck，.temp -40, .meas WL7<3>/wl1_r<192>, WL_len 1024-2048, RC 12000.0/18.0f/70.0/55.0a/4.0a）+ rc_config.json（run0 17002.7/24.096f/63.74/50.475a/3.22a + run1 8546.7/11.81f/79.76/59.175a/5.56a, sweep 1024-1536-256）
- **hidden B1**: .temp 25, .meas WL3<5>/wl2_r<128> val=-600m/2.0, .tran 20p 800n, WL_len 2048-2560, RC 15678.9/22.5f/58.3/42.1a/2.8a + 7890.1/10.5f/88.2/61.3a/5.9a（不同 scale/structure）
- **hidden B2**: 同 B1 base，config RC 14200.3/20.8f/65.7/48.9a/3.3a + 9234.5/12.7f/82.1/55.8a/4.7a, WL_len 3072-4096（anti-hardcode）
- **check.py**: 15 断言（a-o），subprocess 真跑候选 B1+B2，_expected() 独立重算
  - a-b: zip 含 py + py_compile
  - c: B1 exit0 + 产出 out.sp/out_report.json
  - d: B1 .alter 存在
  - e: B1 run0 5 RC params 在 main body
  - f: B1 run1 5 RC params 在 .alter 块
  - g: B1 WL_len sweep 2048 2560 256
  - h: B1 .meas 行数保留
  - i: B1 .temp 保留
  - j: B1 report runs + points + sweep_replaced
  - k: B2 exit0 + run0 RpSC≠B1 + run0 全 5 参数匹配 B2 config
  - l: B2 WL_len sweep≠B1
  - m: cross-input A gold 17002.7/8546.7 不在 B1/B2
  - n: omission-type — B1 不含原 base sweep 行 1024 2048 256
  - o: determinism 3x sha1

## Self-Verify
- ref PASS 15/15 ✓
- 5 negatives（naive_empty/hardcoded_a/only_print/empty_shell/ref_core_deleted）全 FAIL ✓
- §4.9 三假（empty_shell/only_print/ref_core_deleted）= negatives 子集，全 FAIL ✓
- 确定性 3x（assertion o passed）✓
- 断言门 k_rationale=k_check=15≥8 ✓
- test 字段与盘上 check.py 字节同步（sha1 e8ec4c3c405f, 16366B）✓
- .75 Python 3.7.1 stdlib OK ✓

## Skipped
- msg 0-76: 前序 debug 任务（Iso0.sp BLSG/EQSG 脉冲问题）
- msg 100+: 后续任务（sch.oa 电路编辑、SiGe 电阻复制、full-factorial sweep、CBLx8 a/b 互换）
- msg 293-316: tWL_sweep 降额 sweep / full-factorial（不同任务，park）
