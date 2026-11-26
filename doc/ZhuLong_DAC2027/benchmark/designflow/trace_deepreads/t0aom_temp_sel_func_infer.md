# 深读笔记 — 1793078405436_t0aom（easont / hfhds211）

- **session**: `1793078405436_t0aom.messages.json`（easont, host hfhds211=10.129.32.85, mc=650）
- **文件位置**: `10.129.32.85:/home/easont/.cline/data/sessions/1793078405436_t0aom/1793078405436_t0aom.messages.json`（2.3MB, 415 msgs: 224 user / 191 assistant）
- **真实场景**: LPDDR5 DDGOA `ddgoa_cmos_digital_TempHalfWL_schematic_ALPS_sim` 温度传感器混合信号 cosim（FineSim SPICE + VCS Verilog），PVT = tt0.94v45c.vdd2h（TT 工艺 / 45°C / VDD=0.94V / VDD2H=1.25V）。仿真 30μs，9131 probes。

## 用户意图（逐字原文，关键轮）
1. **idx 0** (act): `can you read /proj/ddgoa/V0/workdir/easont/simulation/ddgoa_cmos_digital_TempHalfWL_schematic_ALPS_sim/cosim/cosim/tt0.94v45c.vdd2h/finesim.fsdb`
2. **idx 8** (act): `有fsdb相关的MCP server吗`
3. **idx 17** (act, **核心需求**): `使用上面的skill读取/proj/.../finesim.fsdb；根据波形说明signal的功能`
4. **idx 401** (act): `分析/proj/.../finesim.fsdb，将分析结果用markdown输出`
5. **idx 414** (act, 转新任务): `读取/rundata/.../finesim.NoBank_tRefpb.../raw/finesim.fsdb,分析RowControl模块的行为`

> 用户在第 3 轮明确提出「根据波形说明 signal 的功能」——这是**信号功能推断**任务（不是单纯读波形/统计）。A 档金标准可锚定到第 413 轮 assistant 产出的 markdown 报告（用户随后转新任务，隐含接受）。

## 工具链（assistant 真实调用）
- 自建 skill `waveview-fsdb-readerV2-2`（`/home/easont/.cline/skills/waveview-fsdb-readerV2-2/waveview-fsdb-readerV2-2.py`）：基于 Synopsys WaveView ACE Tcl 后端 `wv -ace_no_gui`（比 fscript 快 ~16x），从 finesim FSDB 按层次信号名逐个读波形，自动判 digital/analog，统计 边沿/脉冲/高 低电平持续/上升下降沿(25%↔75%)，总线 `v(path.bus<15:0>)` 自动展开。
- 通过 `run_approved_command` profile `python-runner` 执行；`shell-runner` 被策略禁用。
- 遇到 WaveView license checkout 失败（`-96,234`），改用 `bsub=True` 提交队列后成功。
- 信号名错配（`v(top.temp<0>)` not found）→ 改用 `v(temp<0>)`（去 `top.` 前缀）后成功。

## 真实波形结构（finesim.vcd，timescale 10ps，scope module top）
VCD `$var` 声明（idx 27 逐行捕获）：
```
temp<7>..temp<0>   8-bit
sel28to32 sel32to35 sel35to40 sel40to43 sel43to47 sel47to50
sel50to54 sel54to58 sel58to61 sel61to68 sel68to76 sel76to85   12 路 range selector
```
+ FSDB 内还有 `sel28 sel32 sel35 sel40 sel43 sel47 sel50 sel54 sel58 sel61 sel68 sel76 sel85 sel90`（单阈值点，14 路）与 `selN26`（主使能）。

## 分析结果（assistant 报告 idx 411/413，用户接受）
### 1. `Temp<7:0>` — 8-bit 二进制计数器（温度编码输入）
- 每 `posedge sys_clk`（8ns 周期）递增 1，遍历 0→255→0→255（两轮）。一轮 0→255 = 256×8ns = 2.048μs。
- `temp<0>` 62.5MHz（16ns 周期，8ns 高/8ns 低，50% 占空）；`temp<1>` 31.25MHz；每位周期 = 前一位 ×2（**半频率性质**）。
- 电压摆幅 LOW≈−490μV / HIGH≈1.250V；上升下降沿 ≈5.14ps。

### 2. `sel28..sel90` — 14 路温度阈值判定输出（range selector）
- 全部 digital（除 sel90 有 analog ringing）。每路在一个扫描轮次内有一次清晰翻转：temp 计数到达阈值时 sel 翻转。
- 阈值表（高→低时刻 / temp 编码）：sel28≥181(15°C) @1.45274μs, sel32≥186 @1.49272μs, sel35≥191 @1.53278μs, sel40≥196 @1.57274μs, …, sel90≥246(80°C) @1.97260μs。
- **相邻阈值间隔一致性**：Δt ≈ 40ns ± 0.2ns = 5 个温度步（5°C），✅ 全部一致。
- **one-hot 性质**：任一时刻至多一路 sel 有效；阈值窗连续铺满 0..256（**contiguous tiling**）。

### 3. 模拟监视信号
- sel90 出现 analog ringing（被分类为含模拟成分）；FSDB 中还有真实模拟 probe（vmon/iref/vsense 类）。

## 合成决策（B 档 synthesized）
- **不取 A 档**：用户核心需求轮（idx 17）虽是「提出需求」未给根因/方案，可用，但金标准（idx 413 markdown 报告）依赖真实 FSDB 路径（farm 节点权限隔离，本机读不到 /proj/ddgoa），且 WaveView license 在沙盒不可用 → 无法在 .75 复现金标准。故取 **B 档**：保留真实场景（easont / DDGOA TempHalfWL / temp<7:0> 计数器 / sel 范围选择器 / WaveView ACE），合成可离线解析的 **VCD**（timescale 10ps，与真机一致）作为资产。
- **任务核心**：用波形特征**推断信号功能**——temp<7:0> 是二进制计数器（验证半频率性质），selNNtoMM 是 one-hot 范围选择器（提取 [lo,hi) 窗，验证 one-hot + contiguous tiling），模拟信号分类为 analog。这是与 Waveform-001（仅统计 .tbl）/ WaveView-002（仅 WaveView Tcl 读 FSDB）的**关键差异点**：本 case 要求功能推断 + 跨信号一致性验证。
- **level=L1**：离线 Python 解析 VCD，不需要 EDA 工具（WaveView-002 已覆盖 L2 WaveView-Tcl）。
- **隐藏 B**：B1(step=12ns, ranges [0,48),[48,128),[128,208),[208,256), analog=iref) / B2(step=6ns, ranges [0,32),[32,96),[96,160),[160,256), analog=vsense)，与可见 A(step=8ns, ranges 64-均匀, analog=vmon) 的范围/步长/模拟信号均不同 → 击败硬编码 A。
- **真实要素保留**（红线 #1）：trace_source{user=easont, host=hfhds211, session_file=1793078405436_t0aom.messages.json, match_count=650, real_task_summary=...}；prompt 写真实用户名/路径/工具/指标；不脱敏。

## check.py 15 条独立断言 (a)-(o)
- (a) zip 存在+合法+含 temp_sel_infer.py  (b) ASCII-only  (c) py_compile  (d) B1 子进程 exit0+JSON  (e) temp<0..7> 全 digital  (f) counter.function=binary_counter + bits=[0..7]  (g) half_frequency_property=True  (h) selectors.function=range_selector  (i) B1 sel ranges 正确  (j) onehot_violations=0  (k) contiguous_tiling=True  (l) analog(iref) 分类 analog  (m) 跨输入 B2 ranges 正确+验证通过  (n) JSON 顶层结构  (o) B1 ranges ≠ A ranges（反硬编码）
- k_rationale = k_check = 15 ≥ 8 ✓
- negatives: fake_empty→(d), fake_print_expected→(i)/(o), fake_core_deleted→(i), naive_hardcode_A→(i)/(o)/(m), naive_always_digital→(i)/(l)；NEG_RC=0 全 FAIL ✓
