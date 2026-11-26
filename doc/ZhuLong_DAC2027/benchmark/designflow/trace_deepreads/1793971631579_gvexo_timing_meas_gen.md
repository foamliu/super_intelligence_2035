# Deep-read: 1793971631579_gvexo (kerwind@hfeg0pkn002, mc=135)

**Shard D · schematic_netlist · B-grade synthesized · A-grade task description eligible**

## Trace source
- session: 1793971631579_gvexo.messages.json
- user: kerwind · host: hfeg0pkn002 (10.129.2.11)
- mc=135 (markers: 85 netlist + 34 schematic + 16 hspice)
- 66 messages, 591KB messages.json
- path: /home/kerwind/.cline/data/sessions/1793971631579_gvexo/

## User intent (verbatim, A-grade eligible)
- U#0「当前工作路径」(housekeeping)
- U#2「切换工作路径到 /proj/ddgoa/V0/workdir/kerwind/simulation/sa_control_san_sap」(housekeeping)
- **U#2'(msg#13)「用finesim measure语法写一个timing_measure文件，测量 check_signal.sx 文件中其他信号第1个上升沿50%和第1个信号第1个上升沿50%的时间差，第1 个信号的电压用参数pvint 表示，san*开头的信号电压用pvnoc表示，sap开头的信号电压用pvpcsg表示」** ← 提需求 + 完整 spec（参数映射规则 + 50%阈值 + 上升沿），未指根因 → **A档任务说明可用原文**
- U#3(msg#44)「你能直接将文件输出到当前路径吗」(输出位置)
- **U#4(msg#54)「用finesim measure语法写一个timing_measure_out文件，测量match_signal_out.sx 文件中其他信号第1个上升沿50%和第1个信号第1个上升沿50%的时间差，第1 个信号的电压用参数pvint 表示，san*开头的信号电压用pvnoc表示，sap开头的信号电压用pvpcsg表示, 文件保存到/rundata/.../sa_control_san_sap/」** ← 同需求换输入(match_signal_out.sx)

## Agent tool chain (msg#13-53, U#2 闭环)
1. read_files: check_signal.sx (Custom WaveView session file, 信号列表) + measure_san_sap_timing.sp + template.sp + test.sp + dummy_sa_input.sp
2. read_files: check_signal.sx + sa_control_vwlp/hspice0.94v.voltage + match_signal.sig
3. search_codebase "pvnoc" (timeout)
4. ask_question: check_signal.sx 中 ocn*/ocp* 信号不匹配 san/sap 模式如何处理 → 用户答「只测量 san* 和 sap* 开头的信号，跳过 ocncsgsec0 和 ocpcsgsec0」
5. read_files: sim_sansap_tt_25.sp + sweep_pvt_sim.sh + batch_get_signal.tcl; search_codebase xi_sactrol_0
6. editor 写 /home/kerwind/timing_measure.sp (分多次：header + Section1-4)，因 policy writableRoot 限制落到 /home/kerwind/
7. run_approved_command python-runner: copy_timing_measure.py 把文件 copy 到 /rundata/.../sa_control_san_sap/timing_measure.sp
8. 用户 U#4 → 同流程用 match_signal_out.sig 写 timing_measure_out.sp (24 个测量项) → copy 到目标路径

## Gold standard (真实产物 timing_measure.sp, 50 条 .MEASURE)
格式：
```
.MEASURE tran t_<tarnode> TRIG v(<refnode>) VAL=pvint*0.5 RISE=1 TARG v(<tarnode>) VAL=<tarparam>*0.5 RISE=1
```
- 参考 signal (第1个): `xi_sactrol_0.xi_r_sactrol_fbcc_0.v(secd)` (.sig 原文) → measure 中 `v(xi_sactrol_0.xi_r_sactrol_fbcc_0.secd)` (层级化节点，v() 外移)
- san* 信号 → pvnoc*0.5；sap* 信号 → pvpcsg*0.5；ocn*/ocp* 跳过
- 全部 RISE=1，50% 阈值 = param*0.5
- measure 名 = `t_<tarnodename>` (节点名去掉 v() 包装)
- 分 Section 注释块 (gsec0 / sapena-sanena / _00v / _00u)

## .sig 信号列表格式 (msg#58 实读 match_signal_out.sig)
```
signal = xi_sactrol_0.xi_r_sactrol_fbcc_0.v(secd)
signal = v(sanena1s00)
signal = v(sapena1s00)
...
```
- 每行 `signal = <node>`；第1行=参考；其余=目标
- node 形态：层级化 `xi_...v(secd)` (需规范化为 `v(xi_...secd)`) 或 `v(name)` (保持) 或裸 `name` (包成 `v(name)`)

## A-faithful 不可复刻原因
- 依赖私有 /proj/ddgoa 工程沙盒 + Custom WaveView .sx/.sig 文件 + agent-policy 可写根限制 → SUT 沙盒无此环境
- → B-grade synthesized：抽成自包含「信号列表 .sig → FineSim .measure 文件生成」任务

## B-grade synthesized 设计
- 候选: `timing_measure_gen.py <signal_list.sig> <out.sp>`
- 解析 .sig (signal= 行, 跳 #/* 注释/空行) → 第1个=参考(TRIG), 其余=目标(TARG)
- 节点规范化: `(.+)\.v\(([^)]+)\)`→`v(\1.\2)`; `v(x)`→保持; 裸`name`→`v(name)`
- 前缀分类: san*→pvnoc, sap*→pvpcsg, 其余(ocn/ocp/其他)→跳过
- 输出 `.MEASURE tran t_<name> TRIG v(<ref>) VAL=pvint*0.5 RISE=1 TARG v(<tar>) VAL=<param>*0.5 RISE=1`
- A=match_signal_A.sig (ref=secd, ~14 信号含 2 跳过); 隐藏 B=match_signal_B.sig (ref=clkb, 不同信号名/数量/跳过) 反硬编码
- 判分 L1-L2 subprocess 真跑候选于隐藏 B + 16 条 a-p 结构化字段断言 (measure 数/参考节点/前缀参数映射/RISE=1/跳过信号/层级规范化/measure 名唯一/跨输入反硬编码/3-seed md5)

## 与已有 case 区别
- SpiceMeasInserter-001: 把 .measure 插入既有 .sp 网表 (输入=netlist, 输出=修改后 netlist)
- CapInsertStgOut-001: .sp 比较器参数化电容插入
- 本 case: 从信号列表 .sig 生成独立 timing_measure 文件 (输入=signal list, 输出=standalone .measure file) + 前缀→参数映射 + 层级节点规范化 + 跳过规则 — 操作维度不同，非重复
