# Deepread: ju0g4 (e0047722@hfeg0pkn004, mc166, tcl 74, 674KB, 189 msgs)

**User goal (USER#0, 逐字原文)**: "使用tcl代码，帮我画一个正弦波并计算过零点、估算频率与峰值。"

## Trace flow
- USER#0: 上述目标。WaveView ACE Tcl 环境。
- assistant: search_apis/get_api_details 检索 sx_* API (sx_equation, sx_meas_freq, sx_meas_peak2peak, sx_create_scan, sx_set_threshold, sx_meas_threshold, sx_scan_data_points, sx_jump_to_x, sx_fetch_x, sx_get_x_from_y, sx_get_real_at_x, sx_gmeas_xatmax, sx_gmeas_xatmin, sx_meas_period, sx_save_signal, sx_release, sx_display)。
- 3 次 SandBox_MCP_Server__run_code (tcl) 全失败: "Connection refused by sandbox [tcl] at 10.129.33.34:41508. The sandbox service may not be started." → WaveView 沙箱全程未启动, 无真实工具产物。
- assistant 用 editor (14 次) 合成 /home/e0047722/sine_wave_analysis.tcl:
  - proc parse_time (工程单位→秒)
  - proc generate_sine_wave (sx_create_signal + sx_append_data 循环, y=amp*sin(omega*x), omega=2*pi*freq)
  - proc analyze_sine_wave (generate → sx_display → sx_meas_freq/period → sx_meas_max/min/peak2peak → sx_meas_threshold 0.0 过零 → dict → sx_release)
  - 主入口: analyze_sine_wave 默认参数 + puts 结果
- 同时写 run_sine_analysis.sh (wv -ace_no_gui 调用, 设 SNPSLMD_LICENSE_FILE) + check_wv.sh (诊断 wv/license/端口)。
- 末尾 assistant: "由于当前节点没有 WaveView license, 无法通过 wv -ace_no_gui 直接运行, 但代码已经基于 API 文档仔细设计完成。"

## 判定
- **B档 synthesized**: 沙箱全程 down, 无真实工具产物; gold = assistant 合成的 API-correct tcl (经我精炼为 reference/sine_wave_analysis.tcl)。
- **domain**: eda_other (WaveView 波形工具 tcl 脚本)。
- **layer**: L2-static — check 用 mock_sx.tcl 在 tclsh8.6 中模拟 sx_* API, subprocess 真跑候选 tcl (§4.2 真跑候选满足)。
- **USER#0 是纯目标陈述**(无根因/无修复方案) → 可作 A 档任务说明; 但因无真实产物, 整体判 B档 synthesized。

## 合成 (case EDA-Eval-DesignFlow-WvSineWaveAnalyze-001)
- A (SUT 可见): prompt.txt (用户原话 + sx_* API 参考) + task_brief.md (≤3 行交付接口)。
- 隐藏 B: amp=2.5 freq=5e5 dur=20us steps=2000 (check.py 内嵌, 不进沙箱)。
- 交付: outputs/submit.zip 含 sine_wave_analysis.tcl。
- check: 15 conds (a-o), static (a-h) + 真跑 (i-o)。mock_sx.tcl 模拟 sx_create_signal/append_data/meas_freq/period/max/min/peak2peak/threshold/create_scan/display/release。
- 自验: REF 15/15 PASS (/tmp/judge 独立目录) + 4 negs FAIL distinct{c,j,n,d} + §4.9 三假全 FAIL + negative_selftest PASS DISTINCT=4。
