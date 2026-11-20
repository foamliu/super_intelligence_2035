# 深读笔记 — ox6r3 (SineZeroCrossFreqPeak-001)

- **trace**: `1793584116177_ox6r3.messages.json` · user `e0047722` · host `10.129.2.13` (hfeg0pkn004) · mc=166 · n=320 msgs
- **domain**: waveform (WaveView ACE Tcl; keywords waveview:315 aether:87 pyaether:51 synopsys:26 analog:26)
- **A-faithful 用户轮**: U#0 (msg0) 逐字 `使用tcl代码，帮我画一个正弦波并计算过零点、估算频率与峰值。` — 纯提需求，未给根因/修复 → A-faithful 合格。其余 5 个 user 轮均为排查/催促（U#1 为何 TCL 沙箱连不上；U#2/U#3/U#4/U#5「必须使用run_code工具」「lang 设置 tcl」），非新 produce。
- **trace agent 行为**: 检索 RAG_MCP_Server WaveView ACE Tcl API → 设计方案 → SandBox_MCP_Server__run_code(lang=tcl) 多次尝试但沙箱 ConnectionResetError（license 不可用）→ 最终基于 API 文档写完整 sine_wave_analysis.tcl（279 行，/home/e0047722/sine_wave_analysis.tcl）。
- **真实产物（金标准依据）**: `sine_wave_analysis.tcl`：
  - `generate_sine_wave`：`sx_create_signal` + 循环 `sx_append_data $sig $x $y`，`y = amplitude*sin(2*pi*freq*x)`，默认 1MHz/1V/10us/500pts。
  - `display_sine_wave`：`catch {sx_display [list $sig_obj]}`（批处理静默）。
  - `scan_zero_crossings`：`sx_scan_data_points` + `sx_jump_to_x` + `sx_x_value`/`sx_y_value`，符号变化检测 + **线性插值** `frac=(threshold-prev_y)/double(curr_y-prev_y)`、`x_cross=prev_x+frac*(curr_x-prev_x)`。
  - `estimate_freq_from_crossings`：**跨 2 过零点**（i 与 i-2）算周期，`est_freq=1.0/est_period`。
  - `analyze_sine_wave`：API 测量 `sx_meas_freq`/`sx_meas_period`/`sx_meas_max`/`sx_meas_min`/`sx_meas_peak2peak` + API 过零点 `sx_meas_threshold $sig 0.0` + 手动过零点 + 频率估算；puts 报告（Requested/Measured/Estimated freq、Max/Min/Peak-to-peak、过零点计数）；返回 dict。
- **合成决策**: 真实 /rundata /proj 路径不可附加 + WaveView license 不可用无法实跑 → **B-grade synthesized**。资产 A = config_A.json(1MHz/1V/10us/500pts/sine_wave，匹配 trace 默认)；金标泛化 gen_sine_tcl_ref.py(CLI `<config.json>`，读 config 后向 stdout 输出参数化 Tcl)。隐藏 B = 0.5V/2.5MHz/20us/1000pts/sine_b；隐藏 B2(cross-input) = 1.5V/500kHz/50us/2000pts/sine_c2。
- **14→16 条件来源**: subckt 不适用（Tcl 而非 SPICE）；改为按 Tcl 结构轴：zip/py_compile/exit0/正弦生成 API/B 配置值嵌入/显示/API 过零点/手动过零点 API/线性插值/频率估算/峰值测量/报告输出/反硬编码 A/跨输入 B2/CLI argv/确定性 = 16 条 a-p。
- **教训**: (1) WaveView ACE Tcl 正弦分析是 waveform L1 可验好范式：生成+显示+过零点(API+手动插值)+频率估算+峰值，16 条件天然丰富。(2) **信号名与 proc 名碰撞**：proc `generate_sine_wave` 含 "sine_wave" 子串 → 反硬编码须用 quoted-string 匹配信号名(`"sine_b"`)，不能用裸子串。(3) **check 提取所有数字字面量按容差匹配 config 值**，避免依赖具体格式(repr/科学计数)。(4) **negative 构造勿用链式 .replace**：`replace("500","1000")` 会误伤 "2500000"→"21000000"；用独立模板直接写值。
