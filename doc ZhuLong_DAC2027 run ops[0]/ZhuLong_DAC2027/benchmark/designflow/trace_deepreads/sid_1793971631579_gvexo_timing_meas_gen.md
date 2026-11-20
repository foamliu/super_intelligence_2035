# Deepread: sid_1793971631579_gvexo (kerwind@hfeg0pkn002, 54msgs/543KB, spice_sim, 11-06 21:27)

## USER#0-12 (trivial/setup)
- #0 "当前工作路径" / #2 "切换工作路径到 .../sa_control_san_sap" → assistant 列目录
- 工作根: `/rundata/ddgoa/V0/simdir/finesim/workdir/kerwind/simulation/sa_control_san_sap`

## USER#13 (A-档 verbatim 纯需求轮 ✓)
> 用finesim measure语法写一个timing_measure文件，测量 check_signal.sx 文件中其他信号第1个上升沿50%和第1个信号第1个上升沿50%的时间差，第1个信号的电压用参数pvint表示，san*开头的信号电压用pvnoc表示，sap开头的信号电压用pvpcsg表示

纯需求：给目标（写 timing_measure 文件）+方法（measure 语法，测 1st 上升沿 50% 时间差，电压参数映射），未给根因/修复。✓ A-档合格。

## Assistant 工具链
1. read_files check_signal.sx（Custom WaveView session，列信号）+ measure_san_sap_timing.sp + voltage files
2. check_signal.sx = WaveView 显示配置，信号名如 `xi_sactrol_0.xi_r_sactrol_fbcc_0.v(secd)`，san*/sap* + ocn/ocp
3. ask_question: ocn/ocp 信号怎么处理？→ USER#20 答"只测量 san* 和 sap*，跳过 ocn/ocp"
4. read sim_sansap_tt_25.sp / sweep_pvt_sim.sh 确认层次化节点命名
5. editor 写 timing_measure.sp（分 4 段，因 >6000 char 限制）→ /home/kerwind/timing_measure.sp
6. read_files 验证 → 93 行，53 信号
7. USER#44 "你能直接将文件输出到当前路径吗" → python-runner copy → 仿真目录

## 金标准（assistant 成功产物）
**timing_measure.sp** (93 行, 53 信号):
- **参考信号**: `xi_sactrol_0.xi_r_sactrol_fbcc_0.secd`，阈值 `pvint*0.5`
- **san\* 信号**: sanena0l/r, sanend0l/r, sanstb0l/r, ... → 阈值 `pvnoc*0.5`
- **sap\* 信号**: sapena0l/r, sapend0l/r, ... + _00v/_00u 变体 → 阈值 `pvpcsg*0.5`
- **跳过**: ocncsgsec0, ocpcsgsec0
- **格式**: `.MEASURE tran t_<sig> TRIG v(xi_sactrol_0.xi_r_sactrol_fbcc_0.secd) VAL=pvint*0.5 RISE=1 TARG v(<sig>) VAL=<param>*0.5 RISE=1`
- 53 个 .MEASURE 语句（san* + sap* 数量）

## 信号列表来源
- check_signal.sx = WaveView session file（信号以 `v(node)` 形式列）
- 信号节点名转 SPICE: `v(xi_sactrol_0.xi_r_sactrol_fbcc_0.secd)` → node `xi_sactrol_0.xi_r_sactrol_fbcc_0.secd`

## 合成规划: TimingMeasGen-001 (spice_sim A-faithful L2)
- **交付**: `gen_timing_measure.py <signal_list.sx> <out_dir>` 读信号列表 → 生成 timing_measure.sp
  - 首信号=参考(pvint*0.5), san*→pvnoc*0.5, sap*→pvpcsg*0.5, 跳过非匹配(ocn/ocp)
  - 输出 `.MEASURE tran t_<sig> TRIG v(<ref>) VAL=pvint*0.5 RISE=1 TARG v(<sig>) VAL=<param>*0.5 RISE=1`
- **A/B**: A=可见信号列表(子集); hidden B=不同信号列表+便携 HSPICE testbench(驱动 B 信号节点 pwl 上升沿)
- **L2**: check.py 跑 gen_timing_measure.py on B → timing_measure_B.sp → HSPICE 跑 testbench_B + measure → 验 measure 结果
- **k≥8 断言**: zip 含 py+sp / py_compile / measure 数量 / ref 用 pvint / san→pvnoc / sap→pvpcsg / ocn 跳过 / HSPICE ran / measure 全有结果 / 值合理 / A≠B
- 参 TbMeasCheck-001 / SlicerDmMeasAdd-001 结构
