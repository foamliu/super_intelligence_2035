# 80yiq 深读 — WaveMaxFind (waveform, A-faithful, B-grade synthesized)

- **session**: 1793776046349_80yiq · user shaoyou · host hfeg0pkn012 (10.129.2.12) · mc76
- **TOTAL_MSGS** 151 · **USER_TURNS** 2 (其余为工具结果)
- **U#0 (msg0) 逐字**: 「计算当前波形中信号v(vb)的最大值」 — 纯提需求，未给根因/修复 → A-faithful ✓
- **U#1 (msg "帮我算出结果")**: 用户令 agent 直接运行计算（directive，非新需求）
- **trace agent 行为**:
  - 大量 RAG search_apis/get_api_details 查 WaveView ACE Tcl API（sx_open_sim_file_read / sx_signal / sx_create_scan / sx_scan_data_points / sx_meas_max / sx_meas_min）
  - SandBox_MCP_Server__run_code 跑 Tcl：sx_current_sim_file 取当前波形 → sx_signal {v(vb)} 取信号句柄 → sx_meas_max $sig 直接得最大值
  - 验证 v(vg): max=1.1, min=0（确认 sx_meas_max/sx_meas_min 可用）
  - 写 proc compute_signal_max {sig_name} ：wdf=sx_current_sim_file → sig=sx_signal $sig_name → sx_meas_max $sig
  - 最终运行时 sandbox 超时（U72-U75 重试均 timeout）
- **关键事实**:
  - "当前波形" = WaveView ACE 沙箱中已加载的 FSDB（live，不可附加）→ B-grade synthesized
  - 波形含信号 v(vb), v(vg)（v(vg) max=1.1/min=0），至少还有其他信号
  - 核心操作 = 对指定信号取 max（sx_meas_max）；可泛化为 max + t@max + min + t@min + peak-to-peak
- **合成方案**: 真实 FSDB 不可附加 → 合成文本波形文件（time + 多信号列），金标 = 通用解析器读波形 + 计算 max/min/t@max/peak-to-peak/num_points/time-range，CLI `<waveform> [--signal <name>] [--out <report>]`
- **隐藏 B/B2**: 不同信号名 + 不同数值 + 不同点数，反硬编码 + 跨输入 guard
