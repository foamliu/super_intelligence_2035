# Deepread: 1795053953259_xwken (kaixuanx @ hfeg0pkn003)

## trace 元数据
- session: 1795053953259_xwken
- user: kaixuanx @ hfeg0pkn003 (10.129.2.12)
- match_count: 137 (hspice:711;netlist:302;pdk:109;schematic:105;synopsys:16;analog:11;transistor:4;drc:4)
- agent: lead, 256 messages, 1.45MB
- 日期: 2026-11-19
- domain: spice_sim (DFF characterization)

## 用户意图（逐轮）

1. **[0]** 搭了 DFF tb (dff_tb.sp)，只能仿真功耗和延时，要评估建立/保持时间等参数 → 重写 tb
2. **[38]** 新 netlist 有两种 DFF（static_tspc + stdcell_DFF），要跑 setup/hold/clk-to-q/平均电流并统计对比
3. **[89]** 用 hspiceD 仿真，不需要 tail
4. **[117]** 保持时间没显示（可能负值），功耗结果不对（tspc i(vvdd)=17.1uA, stdcell i(vvcc)=23.6uA）
5. **[125]** 功耗统计参考 `.meas tran ivdd_avg avg i(VVDD) from=0n to=endtime`
6. **[143-165]** 多轮调 hold time 负值 + 功耗对不上问题
7. **[192]** 统计脚本电流用 uA，百分比按增幅/减幅
8. **[198]** 形成表格
9. **[216]** 跑 PVT 变化下的仿真结果，写脚本实现
10. **[225]** 统计结果在终端显示不全，参考 corners_voltage_pre.sp 排序
11. **[244]** 形成两个对比表（tspc + stdcell）

## agent 交付物

### 核心脚本
- **compare_dff.py** (~11KB): 解析 .mt*.csv measure 文件，自动发现 setup/hold/power 文件（按列名），算 setup/hold/clkq/slew/avgI/maxI/perFF，输出合并对比表 + delta% + dff_compare.md
  - 关键算法：crossing() 线性插值求 qend 过 VDD/2 的 tsup/thold 交叉点
  - alter# 分组：setup=alter1, hold=alter2（支持负 hold）, power=alter3
  - clkq_nom = tsup 最大行的 clkq（最宽松 setup 下的标称延迟）
  - per-FF = chain total / 3
- **pvt_table.py** (~2.7KB): 按 PVT 顺序遍历 corner 目录，调 compare_dff.analyze() 算每个 corner 指标，输出两张分变体表（tspc + std）
  - PVT 顺序：voltage [0.85,0.82,0.88], temp [25,m40,125], process [tt,ff,ss,sf,fs]
  - 缺失 corner 打印 missing

### 测试台
- dff_compare_tb.sp: 两种 DFF 的 setup/hold/power 对比 testbench
- run_compare / run_pvt.sh / collect_pvt.sh: 运行脚本

### 合成测试 CSV
- _syn_mt0/mt1.csv, _syn_v2_mt0/mt1.csv, _t/mt0/mt1/mt2.csv: 手造 CSV 测试 compare_dff.py 解析逻辑

## reframe 决策

用户真实意图 = 解析 measure CSV → 算指标 → 对比/PVT 表。trace 的交付物（compare_dff.py + pvt_table.py）是 Python 脚本，不涉及真跑 HSPICE（HSPICE 在 trace 里是用户自己跑的，agent 只写解析脚本）。

**reframe**: pvt_compare_gen.py produce-generator（L1 offline-Python portability-reframe）
- SUT 写 pvt_compare_gen.py：解析 .mt*.csv → 算指标 → 对比表 + PVT 表
- 判分器在隐藏 B CSV 上跑（不同 vdd/corner/数值），与参考解对比
- 不要求 SUT 跑 HSPICE（需 PDK，不可移植）

## 与已有 case 的区分
- DffSetupHoldChar-001 (kaixuanx, 6tiy7): 单 DFF setup/hold char_gen.py（生成 HSPICE deck + 跑 sim）
- DffSetupHoldStimGen-001 (e0029308, g9bki): DFF setup/hold 激励 deck 生成器
- **本 case (xwken)**: 两 DFF 对比 + PVT 聚合表生成器（解析 CSV，非生成 deck）→ 不同交付物
