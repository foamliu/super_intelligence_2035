# Deepread: 1793070934364_gtyj5 (easont / hfeg0plg58, mc=590)

**Session**: SpiceAgent/cline, 393 msgs, 10 substantive user turns
**Domain**: waveform (LPDDR5 DDGOA 温度传感器 cosim 波形分析)
**Period**: 2026-10-25~27

## 用户意图轨迹

- **U[0]**: `can you read .../tt0.94v45c.vdd2h/finesim.fsdb` — 读取 FineSim FSDB 波形文件
- **U[8]**: `有fsdb相关的MCP server吗` — 问 FSDB 读取工具
- **U[17]**: `使用上面的skill读取...finesim.fsdb；根据波形说明signal的功能` — **核心任务**：用 waveview-fsdb-readerV2-2 skill 读取 FSDB，根据波形推断信号功能
- **U[63]**: `读取.../cosim/netlist_AI,结合上面的fsdb分析，说明模块功能` — 结合网表+波形分析模块功能
- **U[97]**: `分析当前netlist是最简逻辑吗，是否有优化方案，直接输出优化后的网表...netlist_pro` — 网表优化
- **U[204]**: `仿真波形有问题，自己分析后迭代netlist` — 迭代修复
- **U[234]**: `结构参考这个来，你生成的都是错的 .../netlist_AI` — 修正参考结构
- **U[278]**: `你理解下这个网表，然后分析是否有可优化的点，然后直接在netlist上修改` — 直接修改网表
- **U[383]**: `对比修改后的网表和原先的网表，生成markdown形式的报告` — 网表 diff 报告
- **U[392]**: `分析文件夹.../cosim；说明整体仿真流程` — 说明仿真流程

## 助手工具链

1. `list_allowed_files` → 定位 FSDB 在 `/rundata/ddgoa/V0/simdir/finesim/workdir/easont/simulation/.../finesim.fsdb`
2. `read_files` → 读 cosim.sv / cosim.svh / finesim.vcd / port_input.txt / port_output.txt → 理解测试平台（温度传感器：Temp<7:0> 输入 0-511 遍历，sel* 比较器输出）
3. `run_approved_command (python-runner)` → 调 `/home/easont/.cline/skills/waveview-fsdb-readerV2-2/waveview-fsdb-readerV2-2.py` 通过 bsub+wv 读取 FSDB
   - 关键发现：WaveView 顶层信号**不需要** `top.` 前缀，直接 `v(temp<0>)` / `v(sel90)` 等
   - sx_export_data 导出 `.tbl` 格式（XVAL + 信号列）
4. 多次迭代读取不同信号组：sel28/32/35/.../90（14 信号）+ selN26 + sel28to32/sel32to35/sel54to58/sel61to68（19 信号总计）
5. 逐信号分析波形行为 → 推断功能（temp = 温度编码输入；sel* = 温度区间选择器输出）

## 真实 artifacts（提取用作 case A 输入）

- **wv_o_5724.tbl**（581KB, 1705 行, 19 信号, 0-30μs, 1.25V）：WaveView sx_export_data 导出的真实波形数据
  - 信号：seln26, sel28, sel32, sel35, sel40, sel43, sel47, sel50, sel54, sel58, sel61, sel68, sel76, sel85, sel90, sel28to32, sel32to35, sel54to58, sel61to68
  - 每信号是模拟电压（0~1.25V），在特定温度区间激活（vmax ≈ 1.25V）
  - seln26 duty=0.906（几乎常开），sel28-90 duty 0.097~0.131（按温度区间递增），sel*to* duty≈0.003（窄脉冲）
- **wv_s_5724.tcl**：WaveView Tcl 脚本（sx_open_sim_file_read + sx_signal{v(sig)} + sx_export_data）
- 路径：`/home/easont/wv_tmp/wv_o_5724.tbl`（.75 上，easont 用户）

## 金标准

用户接受助手对 sel* 信号的功能推断：每个 sel* 是温度传感器的区间选择器输出，在 temp 扫描到对应温度区间时激活（电压升至 ~1.25V）。波形特征：模拟电压、按温度区间激活、duty 与温度区间宽度正相关。

## 合成 case 决策

- **Case ID**: EDA-Eval-DesignFlow-TempSelWaveform-001
- **Domain**: waveform · **Level**: L1（离线 Python 解析 .tbl → JSON）· **Track**: B
- **A 输入**: wv_o_5724.tbl（真实 19 信号 30μs 1.25V）+ example_output_A.json + task_brief + prompt
- **隐藏 B**: 合成 wave_B.tbl（15 信号 = 13 analog sel + 2 digital clk/rst_n，0.9V，15μs，不同激活模式：always_active/single_pulse/multi_pulse/periodic/never_active）
- **交付**: submit.zip 含 signal_analyzer.py，调 `python3 signal_analyzer.py <tbl> <json>`
- **check.py**: 15 条件 a–o，独立解析器（不 import 参考解），对 B 验证 signal_type/v_min/v_max/num_activations/duty_cycle/activation_pattern/activation_windows/num_points/time_span/信号名/键齐全/窗口良构
- **test_rationale**: 15 条断言 ①–⑮ 与 a–o 一一对应，k=15 ≥ 8 ✓
