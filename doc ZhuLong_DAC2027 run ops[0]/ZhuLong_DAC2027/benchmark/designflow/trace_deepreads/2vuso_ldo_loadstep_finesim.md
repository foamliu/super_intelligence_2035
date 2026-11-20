# 深读笔记 — 2vuso · LDO VwlpRef 负载阶跃 tran 仿真生成 + finesim 提交

## 元数据
- session: `1792724929127_2vuso` · user: tongni (E0017487 Tong Ni) · host: hfeg0pkn003 (10.129.2.12)
- match_count: 468 · keywords: netlist:1388 / hspice:874 / schematic:436 / analog:332 / cmos:30 / calibre:5 / aether:5
- 文件: 1.96MB / 510 msgs (284 user / 226 asst) / 239 tool_use: editor 99 + run_approved_command 35 + read_files 54 + ask_question 34 + search_codebase 8 + list_allowed_files 6 + run_commands 3
- model: deepseek-v4-flash · status: cancelled · cwd: /home/tongni/Desktop/1_Vcc2sc_stdby
- skill: `sim-sp-gen`（仿真文件生成，支持 Tran / AC / DC / Monte Carlo）

## 真实任务摘要
tongni 调用 `sim-sp-gen` skill，给定 DRAM 仿真 testbench 原理图网表，要求生成瞬态（tran）仿真 `.sp` 文件并丢仿真跑出 VwlpRef（LDO 参考输出）在负载阶跃下的瞬态响应。流程贯穿三个 DUT：
1. `tongni_Vcc2sc_DLDO_sim_..._netlist`（DLDO，最初 demo）
2. `tongni_DSCQA_2nd_sim_AG_Vcc2scALDOAct_..._netlist`（ACT 模块）
3. **`zmh_drvqa_sim_DRVQA_VwlpRef_sim_schematic.netlist`（VwlpRef LDO 参考，主线，本 case 抽取）**

主线（VwlpRef）agent 编辑 `zmh_drvqa_sim_DRVQA_VwlpRef_sim_tran.sp`，结构分节：`option / netlist(.inc) / power parameters / stimulus / measurement / pvt`。`_submit_tran.sh` 用 `bsub -q fqueue3 finesim -i <tran.sp> -o <outdir> -np 8` 提交。

## 关键用户 catch（判分 discriminator 来源）
1. **「你的信号给的不对，Vcc还没上电」** — 激励必须尊重 power-up ramp：vcc!/vdd1! 在 30us 才全上电，glbref 23.59us ramp 完，VwlpRef ~45us 才 settle。负载阶跃必须放在 settle 之后（65us）。
2. **「.param DC_load=10 不需要加上，对于 LDO 是 Ref Loading 要看从 0 到 40uA 的跳变」** — 用参数化 PWL 电流源做负载阶跃，而非固定 DC 负载。
3. **「iload VwlpRef 0 pwl(0 0 65u 0 65.001u 'DC_load' 85u 'DC_load' 85.001u 0 ) 改成这个」** — 精确 PWL：0→DC_load @65us，回 0 @85us，用 `'DC_load'` 参数引用。
4. **「vss_AnlgRef 已经和 vss 网表里面连在一起了，还需要加吗」** — `vss_AnlgRef` 在 DUT 网表内已 tie 到 vss，外部不得再驱动（双重驱动冲突）。后用户要求把「不加 vVssAnlgRef」写进 skill。
5. **「bmsub 是我自己配置的（.bashrc alias），你不能直接用，要学会丢仿真的方法和相关配置」** — 提交须用真实 `bsub -q fqueue3 finesim -i ... -np 8`，不能用个人 alias。
6. 终态 **「没有跑出来结果」** — 仿真未跑出结果（agent 提交/配置 struggle，session cancelled）。

## .tran.sp 最终结构（VwlpRef 主线）
```
*******option**********
.inc '/proj/dsjqa/V0/simdir/hspice/corner/hspiceconfig.sp'
********netlist**************
.inc '/proj/dscqa/.../zmh_drvqa_sim_DRVQA_VwlpRef_sim_schematic.netlist'
********power parameters*****
.inc '/proj/dsjqa/V0/simdir/hspice/corner/power_tran.sp'
.param res_sn=1 ...
********stimulus*************
.GLOBAL vcc! vss! vdd1!
vGlbRef085 GlbRef085 0 0.85 pwl( 0 0 17.92u 0 19.22u 0.533 23.59u 0.85 )
* vss_AnlgRef 已在 DUT 内 tie 到 vss -> 不加 vVssAnlgRef
vcm1_ag_AdjVwlpRef<2> cm1_ag_AdjVwlpRef<2> 0 pvss
...
.param DC_load=40u
iload VwlpRef 0 pwl(0 0 65u 0 65.001u 'DC_load' 85u 'DC_load' 85.001u 0 )
.tran 1n 120u
.probe v(*) i(*)
********measurement**********
.MEASURE TRAN VwlpRef_idle     AVG V(VwlpRef) FROM=55u TO=65u
.MEASURE TRAN VwlpRef_loaded   AVG V(VwlpRef) FROM=70u TO=80u
.MEASURE TRAN VwlpRef_droop    MIN V(VwlpRef) FROM=65u TO=70u
.MEASURE TRAN VwlpRef_dropVal  PARAM='VwlpRef_idle-VwlpRef_droop'
.MEASURE TRAN VwlpRef_LdRipple PP  V(VwlpRef) FROM=70u TO=80u
.MEASURE TRAN VwlpRef_unloaded AVG V(VwlpRef) FROM=95u TO=110u
.MEASURE TRAN VwlpRef_overshoot MAX V(VwlpRef) FROM=85u TO=90u
.MEASURE TRAN VwlpRef_overVal   PARAM='VwlpRef_overshoot-VwlpRef_idle'
.MEASURE TRAN VwlpRef_ULRipple  PP  V(VwlpRef) FROM=95u TO=110u
********pvt******************
.inc '/proj/dscqa/V0/simdir/hspice/corner/pvt_vcc2sc.sp'
.END
```

## .75 finesim 沙盒实测（L2 验证）
- 二进制：`/apps/synopsys/SRB/finesim/V-2023.12-1/bin/finesim`，headless `finesim -i <sp> -o <prefix>` 无需 X11。
- bsub：`/apps/lsf/10.1/tools/bin/bsub`（本 case 直接 finesim headless，不经 LSF queue，沙盒可跑）。
- 输出：`<prefix>.mt0`（tran measure，$DATA1 格式）+ `<prefix>.log` + `<prefix>.fsdb`。
- `.mt0` 解析：drop `$DATA1`/`.TITLE`/header token 行，剩余固定顺序 = measure 名 + temper + alter#；measure 值为 `error`/`failed`（diverged）→ null。
- 真跑 `bsub -q fqueue3 finesim -i ... -o ... -np 8` 命令在 trace 中出现（run_approved_command [201]），为真 L2。

## 合成 case（EDA-Eval-DesignFlow-LdoLoadStep-001）
- domain: spice_sim 扩量#4 · L2 真跑 finesim headless tran
- DUT：自包含 LDO 参考 buffer（Thevenin 闭环模型 = 理想受控源跟踪 vref + 有限 Rout + Cload），不依赖外部 hspiceconfig.sp / model 文件（/proj/dsjqa/dscqa 在 .75 上 permission denied）。
- 资产 A：dut_schematic_A.sp（VwlpRef_dut subckt，vss_AnlgRef 不内部 tie，需外部驱动）+ spec_A.json（pre_driven_nodes=[]）+ task_brief.md
- 隐藏 B：dut_schematic_B.sp（不同 vcc/vref/Rout/Cload，vss_AnlgRef 内部 tie 到 vss!）+ spec_B.json（pre_driven_nodes=["vss_AnlgRef"]）+ hidden_manifest.json
- deliverable: `gen_ldo_tran_sim.py` — 读 DUT 网表 + spec → 生成 tran.sp（分节 + .GLOBAL + 参数化 PWL 负载阶跃尊重 power-up + 跳过 pre_driven_nodes + .MEASURE）→ finesim headless 提交 → 解析 .mt0 $DATA1 + .log（error/failed→null）→ JSON report（measures + load_regulation + verdict）
- 核心 discriminator：
  1. pre_driven_nodes 由 spec 驱动（A 空→须加 vss_AnlgRef 源；B 含 vss_AnlgRef→须跳过；硬编任一方向在另一输入败）
  2. 负载阶跃必须放在 power-up settle 之后（step_up > vref ramp_end）
  3. 参数化 PWL `'DC_load'` 引用（非硬编 40uA）
  4. .mt0 measure 值 error/failed → null
  5. cross-input guard：A vs B 参数全不同（vcc/vref/Rout/Cload/DC_load/step 时间/tran stop），硬编 A 值在 B 败
  6. subprocess 真跑 finesim（不能只 print 期望串）
