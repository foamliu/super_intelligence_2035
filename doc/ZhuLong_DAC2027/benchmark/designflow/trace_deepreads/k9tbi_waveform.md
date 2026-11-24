# deepread: 1795053942204_k9tbi (tianqizh @ hfeg0pjn120, mc=441)

## 用户意图
1. 接入其已打开的 Custom WaveView (wv) 进程（IPC bridge，.wv_cmd / zhulong_wv_server / wv_open_ipc.tcl）
2. 形成 skill（.cline/skills/eda-process-check/SKILL.md）让每次 agent 工作前先确认 wv 进程接入状况
3. 从 transient 仿真 .tr0（/rundata/drcoa/V0/.../sim_results.tr0）用 `sx_export_data` 导出信号到 wave_export.tbl
4. 纯 stdlib Python 画多面板模拟波形 PNG 供无 GUI 环境查看（plot_wave_pure.py）

## 关键真实产物
- `read_fsdb.tcl`: `sx_open_sim_file_read` .tr0 → `sx_signal` 取 v(dqs_p)/v(dqs_n)/v(cml2stage_p)/v(cml2stage_n)/v(vdiv!) → `sx_export_data` 导 wave_export.tbl
- `wave_export.tbl`（真实，3MB/42396 行）格式：
  ```
  #format table ## [Custom WaveView] saved 11:06:16 Thu Nov 19 2026
  TIME v(dqs_p) v(dqs_n) v(cml2stage_p) v(cml2stage_n) v(vdiv!) 
   0.0000E+00  7.8750E-01  8.6250E-01  3.1531E-01  8.9459E-01  1.1700E+00 
  ```
- `plot_wave_pure.py`: 解析 tbl（找 TIME 列头，跳非数值行），struct/zlib 拼 RGBA PNG，3 面板（DQS diff / CML2 stage / vdiv），网格+坐标轴+多色。

## 抽取的判分子任务（L1，可离线判分）
解析任意列数 wave_export.tbl → (1) 多面板 waveform.png（stdlib PNG）+ (2) summary.json（每信号 vmin/vmax/vpp/vmean/first_rising_cross_ns + 全局 signals/npts/time_span_ns）。
- A：真实格式重生成（DQS/CML2/vdiv 信号，800 行）
- hidden B：结构不同（clk_p/clk_n/data/vref 信号，380 行，含常数信号 vref 测 null 分支）
- check 18 断言：PNG magic/尺寸 + 信号集合==B(anti-hardcode) + npts/time_span + 每信号 vmin/vmax/vpp/vmean/first_rising_cross + 隔行抽样子集重跑一致性
