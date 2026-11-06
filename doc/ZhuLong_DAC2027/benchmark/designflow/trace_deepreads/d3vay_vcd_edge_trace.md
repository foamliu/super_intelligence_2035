# trace_deepread — d3vay (pjli@172.16.8.13, mc=77, schematic_netlist)

**session**: 1789629900465_d3vay.messages.json (385 msgs, 1.14MB)
**user/host**: pjli / 172.16.8.13
**keywords**: netlist:265; cadence:26; cmos:9; schematic:1
**domain**: schematic_netlist (verilog netlist parse + VCD signal edge trace)

## 用户轮（逐字）

- **U#0** (continuation note, 4751 字)：续接修复 `signal_edge_tracer.py` / `trace_signal_fixed.py`，让 signal tracing 在实例使用 **positional (unnamed) port connections** 时也能正确找到 driver，并修正 one-level-at-a-time lifting 逻辑。已识别根因：实例 `I_RH_DLUT6_Stoarge_PRAC_13bit_5` 在 `RH_DLUT6_PRAC` 中通过 positional port 驱动 `RA_MATCH_INFO[5:0]`，但 parser 正则 `\.(\w+)\s*\(([^()]*)\)` 只抓 named 连接，导致该 driver 不可见。两文件修复计划已提交。
- **U#1** (bug 反馈)：`python3 test_positional_fix.py` 与 `RunTrace` 都报 `TypeError: 'NoneType' object is not iterable` at `trace_signal_fixed.py:104 _top_level_concat_elements(port_list_str)`。
- **U#2** (成功日志)：`RunTrace` 跑通，parsing netlist `rhr_netlist.sv`（119 modules, root `PRAC_Performance_TB_shell`, timescale 1ps），trace `top.Chip.I_PRAC_...I_SCHDULER_DEMUX.RA_MATCH_INFO[0]` edge#1 rising @ 18677997625 ps，driver chain = `I_RH_DLUT6_PRAC_new_5 → I_RH_DLUT6_Stoarge_PRAC_13bit_5 → I_LUT_COMP_1 → I33(bufx2) out_pin .Y`，input `.A` 回溯到 `net047` edge#3 rising @ 18677997465 ps。
- **U#3** (★ A-faithful 新需求，逐字)：「好了，代码可以了。不过我有个新的需求，现在的代码好像只能trace 1或0的沿，如果我想trace z态的话，代码能直接用吗。请你不要修改现在的代码，把新的代码都放在/home/pjli/Desktop/DFFLatchSRVp1」
- **U#4** (★ 细化，逐字)：「由于某些信号刚上电时它就是z态或x态，所以我希望还能再加一个输入参数，从时间t开始，才开始检测某个信号的x态或z态。」
- **U#5**：「这个脚本有trace某个1沿或者0沿的功能吗」
- **U#7** (新 bug)：trace `...I_DLUT_PRAC_RHR_LATCH_new_5.CLK_4_LatN_Mix` 报 `LookupError: signal not found in VCD header`（提示 bus bit 需 VCD 含整条 bus）。

## assistant 工具链
- editor 写 `trace_signal_fixed.py`（Vp0 修复 positional port 解析：module header ordered port list 提取 + 实例 positional 实参按端口顺序映射）、`signal_edge_tracer.py`（`_analyze`/`trace`/`render_text_log` 修复）。
- Vp1 版本（U#3 新需求）：`signal_edge_tracer.py` + `find_edge_time.py` + `TraceSignal/trace_signal_fixed.py` —— 增加 z/x 态沿检测 + `--start t` 时间参数。
- `diag_vcd_bit.py` 诊断 VCD bus bit；`test_positional_fix.py` / `test_zx_edges.py` 自测。

## 用户实际接受的金标准
Vp1 版本：parse verilog netlist（named + positional 端口）→ 沿层次结构回溯目标 signal 的 driver 实例链 → parse VCD → 检测 0/1/z/x 跳变沿，从 `--start t` 时刻起报告。输出 trace-back 文本日志（含 TARGET/DRIVER/lift trace + edge#n @ time ps）。

## 合成决策（B 档 synthesized）
真实 netlist 119 modules + VCD 依赖真实 simvision.vcd（live dep，且 bus bit 解析复杂）→ **B 档 synthesized**：保留「netlist named+positional 端口解析 + driver chain 回溯 + VCD 0/1/z/x 沿检测 + start 时间过滤」的核心语义，合成小型 verilog netlist（5 modules，named + positional 实例）+ 小型 VCD（含 0/1/z/x 跳变 + dumpvars 初值），提升可验条件数到 16，且纯 Python subprocess 可验（无需 EDA 工具）。A/B netlist 模块/实例/信号名全不相交，反硬编码靠 B 字面量扫描 + A-run==goldA 双保险。

## 与 check.py 条件对应
driver_chain 解析（named/positional/out_pin）→ 条件 d/e/f；VCD 沿检测（rising/falling/to_z/to_x）→ g/h/i/j；start 过滤 → k；from/to 值 → l；升序 → m；total_transitions → n；反硬编码 → o；确定性 → p。
