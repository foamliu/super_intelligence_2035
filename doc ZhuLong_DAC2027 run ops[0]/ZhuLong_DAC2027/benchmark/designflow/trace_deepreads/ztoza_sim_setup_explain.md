# Deepread — ztoza (1791875313313_ztoza, t0002965 @ hfhds201 = .75)

- **session**: `/home/t0002965/.cline/data/sessions/1791875313313_ztoza/1791875313313_ztoza.messages.json` (1.36 MB, 214 msgs, agent=lead, 2026-10-13)
- **user / host**: t0002965 @ hfhds201 (10.129.32.75 = .75 本机)
- **mc**: 142 (1115 scan); keywords: analog:182;pyaether:171;netlist:153;drc:98;cadence:73;verilog:69;hspice:55;lvs:43
- **shard / domain**: B / spice_sim (LPDDR6 SPICE 仿真环境配置 + finesim 选项讲解)
- **旧判定**: parked (r375 scout_1105: "false-positive/non-spice/explain-only")
- **重审**: r696 复活 (11-15 用户令·explain-only 不再是排除理由 + 实际意图=LPDDR6 SPICE sim_setup 讲解属 B 域 spice_sim)

## 多任务主线 (8 substantive user_input)

trace 是多任务 session，前半段 (U0-U126) 是发邮件功能探索 (非 EDA)；后半段 (U132-U213) 转入 DECQA/LPDDR6 仿真文件分析，是 B 域 spice_sim 真实意图。本轮取后半段 U190+U197 作 A-档 prompt seed。

- U0 (msg#0): "可以使用发邮件功能吗" — email 功能咨询 (非 EDA)
- U13: "发送一封邮件给jiacheng.shen@cxmt.com，内容为你好" — 发邮件
- U122: "直接根据相关内容，本地写一个脚本，发送邮件即可，不要去使用skill，sandbox，mcp等" — 写邮件脚本
- U132: "检查本地有没有DECQA/LPDDR6相关的文件" — 转折，开始查 DECQA/LPDDR6 文件
- U159: "寻找home目录下的" — find in home
- **U190 (msg#190) — A-档 seed ①**: "分析LPDDR6/DECQA/sim_setup下面的文件是干什么的？" — 分析 sim_setup 目录下文件功能
- **U197 (msg#197) — A-档 seed ②**: "能不能找到finesim仿真相关的文件目录" — 找 finesim 仿真相关文件目录

## agent 回答要点 (assistant#196 + #213)

### U190 回答 (msg#196): sim_setup 目录结构化分析
agent 用 list_allowed_files + read_files 读 `/home/coverage/LPDDR6/DECQA/sim_setup/`，给出：
```
sim_setup/
├── voltagefile/                     # 电压与工艺角定义
│   ├── common.env_LP6               # 电源域、时序阈值、信号参考电平
│   └── paramen.inc                  # 工艺偏差 & 温度相关 RC 参数
└── post_sim/                        # 后仿（寄生参数提取相关）
    └── SPF/
        └── no_vcap                  # 需要排除寄生电容的模块列表
```
逐文件讲解：
- **common.env_LP6**: LPDDR6 SPICE 仿真环境主配置，~70 电源域 (vdd1/vdd2h/vdd2l/vdd2c/vdd2d/vdd2sc/vdd2dp/vddq/vss/vcc/vwlp/vkb/vdleq/vblh/vwln/vad2o/vad2e/vap2/vcsl/vcslp/vpcsg/vtsc/vbn/vbp/vdiv/vdiv2/viso/vibcom/vmwln/vdbias/vncsgn/vintlp/vnoc/vdly/vpgvblh + vbn2c/vbn2sc/vbn2dp/vbndp/vbndq/vbnctrl/vbn2scSC0/vbn2scSC1/vbnDqSC0/vbnDqSC1/vbns + vpgdp/vpgsc/vbp2c/vbp2dp/vbp2sc/vbpdp/vbp2ctrl + 多个 SC0/SC1 子域)；AC 阈值 (VIL/VIH for CS/CA/DQ/CK/WCK/RST, VOL/VOH_DQ, Trf_CS=65/CA=90/DQ=50/CK=40/WCK=40/RST=500, pvinbase_ck=0.1/pvindiff_ck=0.15/pvinbase_wck=0.1/pvindiff_wck=0.15, TWCK2DQI=0/TWCKCKO=0, i_dlybias=7.93uA)
- **paramen.inc**: 工艺偏差 (delvto_Ns/Ps/Ysa=0mv, delvtoBL0-3_NsR/PsR/NsL/PsL=0mv) + RC by 10 temp (-40/-15/25/33/45/70/85/88/98/130, R_WL 89.8-102.3, R_BL 72.0-86.7, C_cell 4.71e-15-5.03e-15) + C_BL/C_WL/C_WL2WL/C_WL2ADJC/C_WL2CC/C_WL2BL/C_BL2ADJC/C_BL2CC/C_BL2BL + KCBGA-D/KCTA-H cell init + Cthin/Cthick/CapO/Cgatein
- **no_vcap**: 35 模块名列表 (CkRcvGutM6/CaIOM6/CaDlyAdj/CADlyAdjPre/Pst/CsIOM6/CsSetHld2/CsDlyAdjG/WCK2TVregGutV4/WckRcvGutV4/WCK2TVregBufV4/WCKIbDiffV5IP/DqIO/P2STopM6V2_new/DqOutTopM6IP/m512Meg_U/m512Meg_V_CCR/P2StopFbUnitV4/WCK2CKTrim/dlyrc*/dlynrc*/dlymosc*/dlynmosc*/dlybias*/Dlybias_gut/DlybiasGF_gut/DlybiasPF_gut/dlyg*/WckOsc/P2SDqTopM6IP/P2SRdqsTopM6IP/DqFinalDrvLegPuNAM6IP/DqFinalDrvLegPdNAM6IP/CsIbAmp_tsioIP)

### U197 回答 (msg#213): finesim 仿真文件目录
agent 用 search_codebase + list_allowed_files 找到：
- `/home/coverage/DDR6/DSCQA/sim_setup/finesim_option/`: 4 配置文件 (spf_block/spfba/vcap/vcap_block)
  - **spf_block**: SPF block 级 - finesim_chkdgt=8/finesim_vdd=6v/finesim_pwrloadmodel=2/finesim_output=fsdb/finesim_ignore_chkfunc_error=1/finesim_warn_limit=10000/finesim_spfprb=2/finesim_spfprb_finger=1/finesim_spfprb_sync=0/finesim_spfprb_mode=1/finesim_skip_flat_pl_node=0
  - **spfba**: SPF 反标 - PARHIER=LOCAL/SCALE=1.00/finesim_mode=promd/finesim_prbport=0/finesim_maxicout=0/finesim_vdd=3.5v/finesim_pwrloadmodel=1/finesim_output=fsdb/finesim_iprbtol=2e-9/finesim_vprbtol=2e-3/finesim_spfprb=1/finesim_spfprb_finger=0/finesim_spfprb_sync=1/finesim_spfprb_mode=1
  - **vcap**: 去耦电容 - PARHIER=LOCAL/SCALE=1.00/finesim_mode=promd/finesim_vdd=3.5v/finesim_pwrloadmodel=1/finesim_output=fsdb/finesim_iprbtol=2e-9/finesim_vprbtol=2e-3
  - **vcap_block**: vcap block - finesim_chkdgt=8/finesim_vdd=6v/finesim_pwrloadmodel=2/finesim_output=fsdb/finesim_warn_limit=10000
- `/home/coverage/sim/bin/`: Perl 仿真脚本 (runsimFC_LP6 全芯片仿真主脚本 ~1300 行)

## 合成方案 (A档 trace-faithful + cross-input guard)

- **任务**: 写 `sim_setup_explainer.py(workdir, out_dir)` 现场解析 `workdir/sim_setup/` 目录下任意 DRAM 项目的 sim_setup 文件 (voltagefile/common.env_*, voltagefile/paramen.inc, post_sim/SPF/no_vcap, finesim_option/spf_block|spfba|vcap|vcap_block) → 产 `sim_setup_report.json` (8 顶层键: project_info/voltage_domains/ac_parameters/process_params/cell_init/spf_exclusion_list/finesim_options/summary)
- **A assets** (LPDDR6/DECQA, verbatim from .75 `/home/coverage/`): common.env_LP6 (6233B) + paramen.inc (2380B) + no_vcap (402B, 35 modules) + 4 finesim_option files
- **hidden B** (LPDDR5/DEGNT, synthesized cross-input guard): ~25 电源域 (不同命名/数量) + 4 temp RC (非 10) + ~20 no_vcap modules (不同名) + finesim options 不同值 (chkdgt=4 非 8, vdd=4v/2.5v 非 6v/3.5v, mode=hpmd 非 promd) → 解析器必须泛化, 硬编 A 值在 B 全 FAIL
- **check.py** [23 断言]: a0-a2 前置 (zip/compile/hidden sanity) + a3/a4 跑+JSON + a5/a6 结构 (dict/8 键) + a7/a8 project_info (B: LP5/DEGNT, 非 A 的 LP6/DECQA) + a9/a10 voltage_domains (count B~25 非 A~70 + 含 vddq) + a11 ac_parameters (VIL_DQ 对 B) + a12/a13 process_params (num_temps B=4 非 A=10 + R_WL@25 B=82 非 A=94.7) + a14/a15 spf_exclusion (count B~20 非 A~35 + 含 B 模块 DqRcvV4) + a16-a18 finesim_options (spf_block chkdgt=4 非 8 + spfba mode=hpmd 非 promd + spfba vdd=2.5v 非 3.5v) + a19 A-leak guard (B 报告不含 LP6/DECQA/94.7/10000) + a20 B-grounding (含 LP5/DEGNT) + a21 确定性 3-seed + a22 finesim 4 files
- **自验**: ref 23/23 PASS + 4 negs (empty/print_only/hardcode_a/deleted_core) 全 FAIL
- k_rationale == k_check == 23 ✓

## 资产位置 (.75 /home/coverage/)
- A: `/home/coverage/LPDDR6/DECQA/sim_setup/` + `/home/coverage/DDR6/DSCQA/sim_setup/finesim_option/`
- hidden B: 合成 (LPDDR5/DEGNT/sim_setup, .75 上无 LPDDR5 sim_setup 故合成)
