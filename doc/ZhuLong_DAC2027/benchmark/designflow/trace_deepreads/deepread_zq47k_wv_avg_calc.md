# 深读笔记 · zq47k — WaveView ACE Tcl 信号平均值计算

- **session**: 1793775630003_zq47k
- **user**: shaoyou @ hfeg0pkn003
- **match_count**: 155 (tools col: 59 "lang":"tcl" + 2 schematic/pyAether/netlist/hspice — tcl-dominant)
- **size**: 291KB messages.json, 144 msgs, 4 real user turns
- **domain**: eda_other (Synopsys Custom WaveView ACE Tcl)
- **shard**: A

## 用户轮（逐字原文，仅 key/token 掩码——本 trace 无需掩码）

- U#0 (msg[0]): `<user_input mode="act">Plot信号v(vb)到当前Waveiew窗口中</user_input>`
- U#1 (msg[36]): `<user_input mode="act">Display信号v(vb)到当前Waveiew窗口中</user_input>`
- U#2 (msg[57]): `<user_input mode="act">计算信号v(vb)的平均值</user_input>`  ← **本轮 A档任务说明**
- U#3 (msg[68]): `<user_input mode="act">我已经打开来一个波形文件，请帮我打开电压信号v(vg)</user_input>`

## 选轮判定

U#2 "计算信号v(vb)的平均值" = 纯目标（提出需求，计算平均值），未给根因、未给修复方案 → 符合 A档选轮规则。
U#0/U#1 是 plot/display（GUI 操作，工具产物难机器化验真）；U#3 是打开信号（前置操作）。选 U#2。

## assistant 工具链（msg[58]–msg[143]，对 U#2 的响应延伸到 U#3）

- RAG_MCP_Server__get_api_details(["sx_open_sim_file_read","sx_current_sim_file","sx_signal","sx_export_data","sx_close_sim_file"]) → 拿到 sx_open_sim_file_read 文档
- RAG_MCP_Server__search_apis("plot signal wave window ace tcl ...") × 多次 → 全空（RAG 库缺 WaveView GUI API）
- read_files(skills/waveview-fsdb-readerV2-2/SKILL.md, sxcmd.log, wv_tmp/*.tcl) → 读 skill 参考脚本
- RAG_MCP_Server__get_api_details(["sx_display","sx_add_wave","sx_signal_add_mode",...]) → 拿到 sx_display / sx_add_wave 文档
- SandBox_MCP_Server__run_code(tcl) × 多次：
  - `info commands sx_*` → 列出全部 sx_* 命令（确认 sx_display/sx_add_wave/sx_signal/sx_get_active_wv/sx_current_wv 可用）
  - `sx_get_active_wv` → `_6109490_void_p`（环境已有活跃 WaveView 窗口）
  - `sx_current_sim_file` → `_60d30b0_void_p`（已有打开的波形文件）
  - `sx_signal {v(vb)}` → 成功拿到 wave 对象（信号存在）
  - `sx_display {v(vb)}` / `sx_add_wave $wave_obj` → **sandbox 超时 30s 不响应**（GUI 操作触发阻塞）
  - 后续 `puts "hello"` 也超时 → sandbox 连接中断（172.16.8.48:41517 refused）
- 末尾 assistant 仅给 API 分析表（sx_get_active_wv/sx_current_wv/sx_signal/sx_add_wave/sx_display），**未产出可运行的完整平均值计算脚本**（sandbox 挂了，未完成）

## 关键 API（assistant 探明，供合成的 gold 参考）

- `sx_open_sim_file_read <path>` → 读开波形文件
- `sx_find_wave_in_file <fobj> <name>` / `sx_signal {<pattern>}` → 取信号 wave 对象
- `sx_create_scan <sig> <type>` → 创建扫描（RISE/FALL/ALL/SAMPLE）
- `sx_scan_first <scan>` / `sx_scan_next <scan>` → 遍历数据点（next 返回 1=还有, 0=结束）
- `sx_fetch_x <scan>` / `sx_fetch_y <scan>` → 取当前点的 x(时间)/y(电压) 值
- `sx_create_signal <name> analog` → 建新模拟信号
- `sx_append_data <sig> <t> <v>` → 追加数据点
- `sx_free_scan <scan>` → 释放扫描
- `sx_write_open <path>` / `sx_write_add_signal <out> <sig>` / `sx_write_close <out>` → 写 WDF
- `sx_new_wv` / `sx_display_wave <wv> <sig>` / `sx_update_wv <wv>` → 新窗口显示

## gold 推断（assistant 未完成，按 API 能力合成 B档 gold）

"计算平均值" = 对信号所有采样点 y 值求算术平均 mean = Σy_i / N。
gold tcl: `calc_avg {sig}` 用 sx_create_scan + sx_scan_first/while{![sx_scan_next]} + sx_fetch_y 累加 + 除以 count → avg；
main 读 config.json → open_sim_file_read → find_wave → calc_avg → create_signal "avg_result" → append_data(0, avg) → write_open/add/close → display_wave/update_wv。

## 与近期 case 的区分

- r230 FmFreqVsTAnalyze：瞬时频率（RISE 扫描 + sx_fetch_x + 1/(t2-t1)）
- r227 ju0g4 / r220 WvSineWaveAnalyze：正弦波绘制/过零点/峰值
- **本轮 AvgValueCalc**：算术平均值（ALL/SAMPLE 扫描 + sx_fetch_y + Σy/N）—— 扫描类型、fetch 轴、计算公式均不同，不重复

## 备注

- trace 中 assistant 因 sandbox 超时未完成实际计算，故采用 config-driven stub judge（同 r230 模式）：stub 按 config.dc_value 生成 N 点 y=dc+A·sin(2πi/N)（整周期正弦均值为 dc），tclsh 独立临时目录真跑候选，验 API 序列 + 数值 avg≈dc。
