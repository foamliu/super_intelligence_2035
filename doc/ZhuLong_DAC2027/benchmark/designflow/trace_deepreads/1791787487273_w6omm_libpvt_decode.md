# 深读笔记：1791787487273_w6omm — CCS .lib 时序库 PVT 解码

- **trace_source**: user=e0045488 / host=hfeg0pkn002 / session=1791787487273_w6omm / match_count=59 / msgs=70 / 264KB
- **真实任务**：用户在签核级时序库发布目录 `/proj/lacaa/V0/workdir/leiwang/TOSOS/35H_STC_*/timing_power_noise/CCS/FS204/` 下，有 12 个子文件夹 `FSP51H204L6W{25,30,35,40}T6{LVT,SVT,ULVT}`（4 宽度 × 3 Vt 阈值），每个文件夹内含 3 个 CCS .lib/.db（ff/tt/ss 三工艺角）。要求：① 解释单个 .lib 文件名含义；② 列出 FS204 folder 包含哪些 PVT；③ 按 4 列(filename/Process/Voltage/Temperature)给表；④ 按文件夹名给表（每文件夹 3 行）；⑤ 按工艺角拆 3 张表；⑥ 按宽度 W{25,30,35,40} 拆 4 张表。
- **用户接受的金标准**（assistant #13/#15/#17/#19/#21，用户随后转问"5nm 判断依据"和"W 宽度含义"，未否定 PVT 表）：
  - 文件夹命名 `FSP51H204L6W{W}T6{VT}`：W∈{25,30,35,40}=标准单元宽度族，VT∈{LVT,SVT,ULVT}=阈值电压类。
  - .lib 文件名 `*_CCS_{corner}_v{V}p{dec}_{T}c.lib`：corner∈{ff,tt,ss}，V/T 联动：
    - **ff** = Fast-Fast = **0.825V / 0°C**（`v0p825_0c`）
    - **tt** = Typical-Typical = **0.75V / 85°C**（`v0p75_85c`）
    - **ss** = Slow-Slow = **0.675V / 125°C**（`v0p675_125c`）
  - 完整 PVT 覆盖 = 12 文件夹 × 3 角 = **36 个独立 .lib**（+ 36 .db = 72 文件）。
  - .lib header 内 `nom_process : 1 ; nom_temperature : <T> ; nom_voltage : <V>`（tt 文件 nom=0.75V/85°C）印证文件名。
- **A 档选轮**：#9 用户逐字原文『请帮我列出一个表格，逻辑出这个folder中包含哪些PVT』—— 纯"提出需求"，无根因/修复 → 合 A 档选轮规则。上下文（12 文件夹名）走 assets，不进 prompt 改写。
- **资产来源**：文件夹名（#3 逐字）、.lib 文件名模式（#11/#12 真实 listing）、.lib header nom 字段（#28 read_files 真实读取，trace 中 nom_temp 行被截断但值由文件名+STA 惯例确定 = 0.75/85）。
- **不适配部分（不取）**：#22-#70 后半段调查"工艺节点是不是 5nm"及"W 宽度物理含义"——开放式侦探任务，依赖 LEF/CDL/PDF 多文件 + 主观推断，非聚焦 design-flow 交付，不纳入本 case。
- **domain**：digital（时序库 PVT → 喂 STA/PT/Innovus，数字签核链路入口）。**层级**：L1-style（离线解析命名约定 + 读 .lib header，无 EDA 工具执行）。**档位**：A 档 trace-faithful。
