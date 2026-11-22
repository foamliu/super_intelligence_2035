# 深读笔记 · l4hdo (1795067358138_l4hdo) · tianqizh @ hfeahpc501 · mc=148

> domain: **waveform**（D-pure，waveview:724 / drc:897 / schematic:141 / netlist:113 / mosfet:52 / analog:41 / synopsys:39 / pex:33）
> trace 源：`.75` → ssh hfeahpc501 → `/home/tianqizh/.cline/data/sessions/1795067358138_l4hdo/1795067358138_l4hdo.messages.json`（590 KB / 111 msgs）
> 选取：freshest scan `ssh_eda_search_20261122_172249/summary.tsv`，D-domain mc 50-150 段，ledger 交叉核对 = FRESH，claim 2026-11-22 19:19

## 一、真实用户意图（逐条 user text msg）

1. **USER[0]**：「我要看20—simulation里面02sim 的结果」—— 查看 `20_simulation/` 目录下 `02sim` 的仿真结果。
2. **USER[26]**（ask_question 回答）：选择查看 DQS 链路关键输入/输出节点的电压曲线（而非只看 log 摘要）。
3. **USER[58]/[68]**（ask_question 回答）：同意重启 WaveView 桥接以恢复 tr0 波形导出。

**意图定性**：真实 waveform 查看与导出任务——定位仿真结果 → 读取 sim log 确认状态 → 打开 tr0 波形 → 枚举 DQS 链路信号 → 限窗导出电压曲线 → 画图。**有明确交付物**（导出的 .tbl 波形数据 + 曲线图），**非 analysis-only Q&A**。

## 二、assistant 工具链（关键路径）

| 步 | 工具 | 作用 |
|---|---|---|
| 1 | `list_allowed_files` ×多 | 定位 `20_simulation/02_IO_DQS_jitter` 实际路径 `/rundata/drcpa_sim/V0/simdir/finesim/workdir/tianqizh/simulation/20_simulation/02_IO_DQS_jitter/` |
| 2 | `read_files` sim_results.lis.log/elog | 确认两路仿真（01_jitter_vdiv_npvt / 01_jitter_vdiv_sslh）FineSim V-2023.12-1 **全部成功完成** |
| 3 | `read_files` DQS.sp / DQIB.sp | 读激励确定 DQS 活动窗口：**DQS 在 150µs+12ns 才翻转，period≈208ps（DR=9.6Gbps），跑到 151µs** → 活动窗口 150.012µs→151µs |
| 4 | `SandBox_MCP_Server__run_code` (tcl) `sx_open_sim_file_read` | 打开 `01_jitter_vdiv_npvt/sim_results.lis.tr0`，句柄有效 |
| 5 | `sx_signal` + `sx_get_name` | 枚举 DQS 链路信号：`v(dqs_p)` `v(dqs_n)` `v(dqs_buf_f0)` `v(dqs_buf_f1)` `v(dqs_out<0>)` `v(dqs_out<1>)` `v(vdiv!)`（7 条） |
| 6 | `sx_export_data`（**未限窗**）→ 挂桥 | 50 万点 × 7 信号超过桥接 30s 限制，桥接卡死（已知陷阱） |
| 7 | `RAG get_api_details` sx_export_data/range | 发现 `sx_export_range <start> <stop> <step>` 可限窗 |
| 8 | `sx_export_range 150.01u 150.022u 0.5p` + `sx_export_precision 6` | 限窗 150.010→150.022µs，0.5ps 步进（≈2.4 万点），导出到 `dqs_chain_02sim.tbl` |
| 9 | `read_files` plot_wave_pure.py / read_fsdb.tcl / signal_list.txt | 复用用户已有波形读取/绘图流程（read_fsdb.tcl → sx 桥接导出 .tbl → plot_wave.py 画图） |
| 10 | 重启桥接（zl_start_bridge.sh，-96 license 抖动后 GUI 重启） | 桥接恢复后限窗导出 |
| 11 | 再次 `sx_open_sim_file_read` → 句柄类型错误（trace 在此附近，msg#73） | 待续 |

## 三、关键真实参数（造题可用，防硬编码）

- 仿真器：**FineSim V-2023.12-1**
- 仿真类型：DRCPA IO DQS jitter（post-layout 带寄生 RCC）
- 激励：`.tran 100p 151u`
- 结果目录：`20_simulation/02_IO_DQS_jitter/{01_jitter_vdiv_npvt,01_jitter_vdiv_sslh}`
- DQS 活动窗口：**150.012µs → 151µs**（翻转起点 150µs+12ns）
- DQS period：**≈208ps**（DR=9.6Gbps）
- 导出窗口（避挂桥）：**150.010µs → 150.022µs，0.5ps 步进**（≈2.4 万点 × 7 信号）
- DQS 链路 7 信号：`v(dqs_p)` `v(dqs_n)` `v(dqs_buf_f0)` `v(dqs_buf_f1)` `v(dqs_out<0>)` `v(dqs_out<1>)` `v(vdiv!)`
- 桥接端口：61771（10.129.33.24）
- 波形文件：`sim_results.lis.tr0`（二进制，Custom WaveView ADV tr0 格式）

## 四、造题方向（合成计划 · 下轮）

**case 形态**：design_flow，L2（真跑 WaveView TCL 桥接导出波形）。

**prompt（自然场景）**：用户 tianqizh 在 hfeahpc501 上跑了 DRCPA IO DQS jitter 仿真（FineSim，20_simulation/02_IO_DQS_jitter），想查看 02sim 的 DQS 链路关键节点电压曲线。要求：打开 tr0 波形 → 枚举 DQS 链路信号 → 用限窗导出（避免桥接挂死）→ 导出 .tbl → 画曲线图。交付 submit.zip 含 export_dqs.tcl + dqs_chain_02sim.tbl + plot_wave.py + signal_list.txt。

**check() 要点（≥8 断言，下轮细化）**：
1. zip 内 4 文件齐全
2. export_dqs.tcl 含 `sx_open_sim_file_read` 且路径指向 hidden B 的 tr0
3. 含 `sx_export_range` 且窗口落在 DQS 活动区（start≥150µs，stop≤151µs，step≤1ps）—— **防全量导出挂桥**
4. `sx_export_precision` 已设
5. signal_list.txt 含 7 条 DQS 链路信号（dqs_p/dqs_n/dqs_buf_f0/dqs_buf_f1/dqs_out<0>/dqs_out<1>/vdiv）
6. .tbl 结构正确（header + time + 7 列 voltage，行数与窗口/步进一致）
7. plot_wave.py 能解析 .tbl（真跑 subprocess，断言输出结构）
8. 退化提交（print_only / core_deleted / hardcode_a）全 FAIL
9. 随机化：3 seed 抽信号子集，导出结论一致

**hidden B**：另一路仿真 `01_jitter_vdiv_sslh` 的 tr0（与 A 的 npvt 在 corner/温度/节点不同，非换文件名）。A 给 SUT 看 npvt，B 放 hidden/。

**真实 trace 溯源**：`metadata.trace_source{user:tianqizh, host:hfeahpc501, session_file:1795067358138_l4hdo.messages.json, match_count:148, real_task_summary:"查看 20_simulation/02_IO_DQS_jitter 仿真结果 + 导出 DQS 链路 7 信号电压曲线（限窗避挂桥）"}`

## 五、DEBT

- **本轮未合成 case**：r1135 预算耗于 MCP 第 31 次复测（用户令最高优先）+ 候选选取 + 深读。合成（assets/reference/hidden/negative/check.py/self-verify）留下轮。
- 下轮 ETA：直接复用本深读笔记，按 §四 计划合成，预计 1 轮可交付。
- 台账状态：`claimed`（已 reserve，不会被他轮重选）。
