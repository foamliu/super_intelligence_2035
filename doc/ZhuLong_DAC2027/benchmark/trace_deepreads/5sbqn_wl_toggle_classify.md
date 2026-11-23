# 5sbqn 深读 — WL 波形 toggle 判定

- session: 1794790671331_5sbqn / user: ypzheng / host: hfeg0plg103 (10.129.8.235)
- mc=122, wv=292/ana=91/net=219, 558KB/95 msgs
- 真实意图: 用户跑完 DDGOA DRAM finesim 仿真后要求「读取波形看看哪几根 WL toggle 了」
- 对话流:
  1. 问仿真 exit 原因 → agent 查 finesim.elog/bsub.log/si.out 确认 PrimeSim Successfully Completed（非异常退出，"error" 实为 chktiming violation 计数 + OOM 告警）
  2. 问 gvim 打不开 si.out/fsdb → FSDB 是二进制波形库 vim 读不了，si.out 太大超长行
  3. 「帮我读取波形，看看那几根 WL toggle 了」→ 三通道均被沙箱 license/网络卡住:
     - fscript 加载 576MB fsdb 超时被杀
     - wv -ace_no_gui: license server unreachable
     - SandBox tcl bridge: Connection refused
  4. 最终交付 wl_scan.tcl (sx_wdf_info -waveforms 列信号 + sx_export_data 导出)
     + wl_analyze.py (解析导出表判定 toggle) + wl_run.sh 一键脚本
- case 抽取: 纯 Python 内核 wl_analyze.py — 解析 WaveView 导出的 WL 波形 ASCII 表,
  逐信号计算 vmax/vmin/vswing/n_edges/n_pulses/dwell_high_ns, 分类 toggled/flat
- case_id: EDA-Eval-DesignFlow-WlToggleClassify-001 (waveform, L1, k_check=15)
- A: 16 WL top.ddgoa.* VPP=2.6 0-50ns/0.25ns 4 toggle
- B1: 24 WL tb.ddr.ch.* VPP=3.0 0-200ns/0.5ns 10 toggle (1-3 脉冲)
- B2: 20 WL chip.mem.ra.* VPP=2.4 0-120ns/0.4ns 7 toggle (含 0.4ns glitch)
- 自验: reference 15/15 PASS + 3 负样本全 FAIL + 确定性 + 列序随机化 3 种子一致
