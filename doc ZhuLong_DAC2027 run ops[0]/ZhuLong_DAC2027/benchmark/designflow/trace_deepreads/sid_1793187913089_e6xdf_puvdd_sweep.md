# trace_deepread — sid 1793187913089_e6xdf · PU-VDD sweep testbench modification

- **trace**: `1793187913089_e6xdf.messages.json` · e0030760 @ hfeg0pkn004 (10.129.2.13) · match_count=185 · tools: 810 hspice / 468 schematic / 340 netlist · spice_ratio 0.501
- **首轮 user turn (verbatim, A-档 任务说明)**:
  > /home/e0030760/Documents/SRAM_6T_testbench/6Ttestbench.sp 根据这个6T的testbench.sp修改testbench仿真不同PU管的VDD电压对Iread、Iwrite、WSNM、RSNM、HSNM等参数的影响，该testbench内有电路netlist，直接读取并进行修改仿真
  - clean「提出需求」轮：给文件 + 目标（扫 PU 管 VDD 对 5 项参数影响）+ 「直接读取并修改仿真」。🚫 无根因、🚫 无修复方案 → 合格 A-档。
- **原始 testbench (6Ttestbench.sp, asset A verbatim)**：6T SRAM bitcell 特征化 deck。结构：
  - `.include` option_hspice.sp + pwr.sp + switch.sp + BitCell CH336 netlist
  - `.NODESET` 6 测试节点偏置；`V_power VDD 0 DC=VVDD`；`VIPRB_READ/WRITE/STANDBY` 电流探针；`V_input1/2 VIN_1/2 = VVDD-VIN`
  - `.tran 1p 10ns` + `.DC VIN 0.0 VVDD 10e-3`（VIN 扫参用于 SNM 蝴蝶曲线）
  - `.PROBE DC` 8 节点；`.Print DC V(S_RSNM)/V(SB_RSNM)/V(S_HSNM)/V(SB_HSNM)`（RSNM/HSNM 蝴蝶对，仅 print 待离线提取）
  - `.MEASURE DC Iread/Iwrite/Ileak FIND I(VIPRB_*) AT=VVDD/2`；`WNM_1/2 find v(VIN_*) when v(S*-v(SB*))=0 cross=1`（WSNM 交叉）
  - corner×temp×VVDD 巨大 alter 矩阵：tt/fs/ff/sf/ss × TEMP 25/-40/125 × VVDD 0.675/0.75/0.825（原 deck 扫的是 cell VVDD，不是 PU VDD）
- **trace 末态用户接受产物（金标准）**：assistant 产 `6Ttestbench_PUvdd.sp` + `run_puvdd_sweep.py` + `sram_metrics_vs_puvdd.csv/.png` + `butterfly_vs_puvdd/`。修改要点：
  1. 新增 `.PARAM VPUP=VVDD` + 独立 PU 电源轨 `V_pu VDD_PU 0 DC=VPUP`（隔离 PU 管 supply）
  2. cell VVDD 固定 0.75；**VPUP 扫 0.40→0.85V（10 点，.alter）**——观察 PU 强度对参数的影响
  3. 保留 Iread/Iwrite/Ileak `.MEASURE`、WNM_1/2（WSNM）；RSNM/HSNM 仍 `.Print DC` 蝴蝶对，由 `run_puvdd_sweep.py` 离线内接方计算
  4. netlist 改 include 本地 `bitcell_ch336_pu.sp`（暴露 VDD_PU 脚的 bitcell）
  - 接受结果表（VPU 0.85→0.40）：Iread 34.69→13.48µA、Iwrite 28.52→4.21µA（随 PU 减弱单调降）；RSNM 0.1462→0.0707（0.85→0.65 段单调降，<0.65 回升=读扰动失效边界）；HSNM 0.2802→0.0919；WSNM 0.5251→~0（<0.55V 趋 0）
- **case 抽取的子流**：通用「读 6T testbench → 解析探针节点/netlist/VVDD → 产出 PU-VDD 扫参 deck」生成器。要求 SUT 写 `modify_tb.py`，CLI `modify_tb.py <in.sp> <out.sp>`，对任意 6T testbench 产出结构正确的 PU 扫参 deck（VPUP 参数 + V_pu 轨 + ≥5 点 VPUP 扫 + 5 项测量保留 + VVDD 固定 + 节点名随输入适配）。
- **可判分性（不打散 netlist、不跑 sim）**：check.py 解析产出 deck 的结构（VPUP 参数/PU 轨/扫参点数/5 项测量/netlist include 保留/VVDD 固定），并在 hidden B（CH340 bitcell + _X 节点名 + VVDD 0.81/0.9/0.99）上验证节点名适配（防硬编码 A）。k=15 断言 a–o。
- **domain**: spice_sim（SRAM bitcell 特征化 testbench 修改）· **档**: A-faithful · **层**: L2（真 SRAM testbench 结构理解 + hspice deck 改写）· **难度要点**: 须懂 PU=上拉管、VDD_PU 隔离、SNM 蝴蝶法、.alter 扫参语义、节点名泛化（非硬编码）。
