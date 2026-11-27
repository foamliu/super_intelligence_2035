# txjim — AMS mixed-signal wrapper debug → AmsWrapperProduce-001

## trace 溯源
- session: `1795403333217_txjim` (binwenh@hfeg0pkn003, mc=350)
- domain: analog_context (analog:836 schematic:694 netlist:603 verilog:354 .spi:81 hspice:38)
- 获取：`.75 ssh→hfeg0pkn003`，per-session subdir `/home/binwenh/.cline/data/sessions/1795403333217_txjim/`，archive 1.87MB(166 msgs checkpoint) + active 259KB(70 msgs resumed)

## 用户真实意图
AMS（VCS+FineSim）混合信号协同仿真：把 Slicer offset-calibration 模拟电路包成顶层
子电路 `sim_slicer_offset_calibration_ams`，让数字 FSM（`sim_Slicer_offset_calibration_FSM`）
通过 a2d/d2a 与模拟电路交换 clk / comparator 反馈 / trim 校准码，跑通 offset 校准闭环。

## 调试中踩过的真实坑（case 必须考察）
1. **vb 零电压桥 + .GLOBAL 跨名共享失效**：薄壳 wrapper 用 `vb_dqs dqs_ib DQS_IB 0`
   把引脚桥到真实网，cosim 扁平化后折叠到错误节点，`u_ana.dqs_ib` 读 0 而非真实跳动的
   `DQS_IB`。正确做法：把真实顶层实例搬进子电路，子电路端口=真实被驱动网，去 vb 桥，
   .GLOBAL 只留电源/地。
2. **端口名大小写敏感**：Verilog 小写 `dqs_ib` ≠ SPICE 大写 `DQS_IB`，须 `port_map` 显式映射。
3. **netlist 扁平顶层例化**（`**TopDesStart/End`）搬进子电路后顶层不得重复例化（冲突）；
   `.SUBCKT` 单元定义保留。
4. **hollow 模块端口方向**：a2d 口（模拟驱动数字）= output，d2a 口（数字驱动模拟）= input，
   反了 a2d/d2a 读不到真信号。

## case 合成（已落库 EDA-Eval-DesignFlow-AmsWrapperProduce-001）
- task_id: AmsWrapperProduce-001, LIVE-NA, judge_layers=[L0,L1]
- synthesized-reframe：通用「AMS wrapper 生成器 `gen_ams_wrapper.py(spec)->sim.sp+vcsAD.init+testbench_top.v` + hidden-B 反硬编码」
- A(visible) spec_A.json：Slicer offset-cal，6 fsm 口(2 a2d: dqs_ib/data_i_out_t + 4 d2a: trim_dq0_3..0)，2 top 实例(IO_DqRcv/IO_VrefDqGenV3_15)
- hidden B(token-structurally 不同) spec_B.json：PDM slicer trim，7 fsm 口(3 a2d + 4 d2a)，不同 design/cell/net 名，extra monitor a2d，不同 loth/hith
- reference `gen_ams_wrapper.py`：spec 驱动通用实现，subckt 端口=真实网，无 vb，.GLOBAL 只电源，port_map lowercase→uppercase，a2d/d2a，hollow 方向 a2d=output/d2a=input
- check.py 17 conds(a-q)：a zip 含 py ②b py_compile ③c A 运行 exit0 产 3 文件 ④d subckt 名+端口集合==spice_real_net ⑤e 无 vb 桥 ⑥f .GLOBAL 含 global_nets 不含信号网 ⑦g top 实例在 subckt 内 ⑧h 顶层无重复扁平例化 ⑨i use_spice -cell ⑩j port_map 全映射 ⑪k a2d 节点+loth/hith ⑫l d2a 节点 ⑬m hollow 方向 a2d=output/d2a=input ⑭n u_ana 连线 ⑮o u_fsm+trim 总线+rst ⑯p B 反硬编码(端口==B 网+port_map 完整+无 A token) ⑰q 源码无 A token
- 自验全绿：ref check.py → PASS 17/17 + negative_selftest 5 neg ALL-FAIL distinct first-fail{a,c,d,p,m}(§4.9 trio full: empty→a/print_only→c/core_deleted→d + extra: hardcode_a→p/wrong_direction→m) + SKIP_RUN=1 workdir leak 自检通过(无 check.py/reference/hidden 泄漏) + 3-way sha sync(disk==JSON test==metadata.check_sha256=61834b66... size 14094) + k_check=17=k_rationale=17 + 框架 auto-build jsonl D 596 case 含本条
- 台账 mark: 1795403333217_txjim → case(EDA-Eval-DesignFlow-AmsWrapperProduce-001)
