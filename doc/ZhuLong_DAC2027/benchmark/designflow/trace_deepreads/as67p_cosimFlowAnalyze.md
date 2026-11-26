# 深读笔记：as67p (easont@hfeg0pkn004, mc166) — VCS+FineSimPro cosim 流程分析

**session**: `1793147699495_as67p.messages.json` (496 msgs, 268 user, 13 text-user)
**host**: hfeg0pkn004, **user**: easont
**domain**: eda_other (协仿真流程结构分析)

## 选轮（A档 faithful）
USER#goal (msg[392] 逐字原文):
> 分析文件夹：/proj/ddgoa/V0/workdir/easont/simulation/ddgoa_cmos_digital_TempHalfWL_schematic_ALPS_sim/cosim；说明整体仿真流程

纯目标轮（要求分析 cosim 目录 + 说明整体仿真流程，未指出根因/方案）→ A档任务说明。

## 金标准（msg[400]，用户接受）
assistant list_allowed_files(depth=3) 探 cosim 目录树 → read_files cosim.sv/cosim.svh/cosim.sp/makefile/run.bash/build.bash/pvt/*.sp/dummy.sp → 组织结构化分析：

### 目录全景
```
cosim/
├── build/      # VCS 编译产物 (build.bash/build.log/simv/simv.daidir/csrc)
├── cosim/      # 仿真运行目录 (dummy.sp/voltage.sed/setup.done)
├── pvt/        # PVT 配置 (tt0.94v45c.vdd2h.sp 当前 + backup/saved/rast_to_trasdly/vdd2h 子目录)
├── saved/      # 仿真结果存档 (finesim.fsdb/finsim_AI_glitch.fsdb)
├── measure/    # 测量脚本 (tRC_0p65v.sp/MeasureRuntRC_Vinit/output/)
├── netlist_AI  # 主网表(AETHER 导出)
├── netlist_pro→netlist_AI, netlist→netlist_pro, netlist_work/netlist_digital→netlist_AI (符号链接)
├── cosim.sp/cosim.sv/cosim.svh/makefile/run.bash/port_input.txt/port_output.txt (顶层)
```

### 三步仿真流程
1. `make setup`: 创建 cosim.svh/cosim.sv/cosim.sp/pvt/*.sp + build/cosim 目录
2. `make build`: VCS 编译 Verilog 侧 (`vcs -top top -full64 -sverilog -load finesim.so:finesim_startup`) → build/simv
3. `make run`: `bsub -q fqueue2h` LSF 集群执行 `build/simv -o finesim pvt/$pvt.sp` → FineSim 混合信号仿真 → finesim.fsdb/verilog.fsdb

### 关键文件
- cosim.sv: Verilog testbench (sys_clk 8ns, Temp 扫描 0→255, $finesim_config, $dumpfile)
- cosim.svh: 混合信号端口桥接 ($finesim_output D2A / $finesim_input A2D, 30 输出端口实际驱动 14)
- cosim.sp: SPICE 顶层 (.option finesim_mode=prohd, .inc netlist_pro, .tran 50p, .probe v(*) → 9131 探测)
- cosim.cfg: A2D-D2A 接口 (VL/VH/TX, 电阻阵列)
- pvt/tt0.94v45c.vdd2h.sp: PVT 配置 (ptemp=45, .lib tt, .inc cosim.sp)

### 仿真参数
TT/45°C/VDD2H=0.94V(芯片级)·1.25V(内部)/VINT=0.8V/30μs/50ps 步长/9131 探测/36158 SPICE 点/8 线程 27.9s

## 合成方案（A档 faithful · eda_other · L1-static+subprocess）
- **交付**: `analyze_cosim_flow.py` 遍历 cosim 目录树读取关键文件，输出结构化 JSON
- **A**: 真实 cosim_A 目录(从金标准重建: build/cosim/pvt/saved/measure/netlist_*+symlinks, pvt/current.sp→tt0.94v45c.vdd2h.sp) + prompt.txt(U#goal 逐字) + task_brief.md
- **隐藏 B**: cosim_B 合成(ss0.81v125c.vdd2l PVT + netlist_main + verilog.fsdb + measure/tWTR, 结构对立不同字面量)
- **隐藏 B'**: cosim_B_prime seed 随机化(ff1.08v0c.vdd2h active + tRFC measure)
- **判分**: check.py 独立临时目录 subprocess 真跑 B+B'，14 conds a-n (静态结构 a-m + B'一致性+反硬编码 n)
- **k=14** 闸门 PASS
