# 深读笔记: mdxo8 (kaixuanx / hfeg0pkn001 / mc149) — waveform 域

**session**: `1792561000352_mdxo8.messages.json` (1.3MB, ~500+ msgs)
**domain**: waveform (D shard) · **track**: A-faithful 提需求轮
**case**: EDA-Eval-DesignFlow-PwrCornerSweep-001

## 用户意图 (U#0 + U#1 原文)
- U#0: 「我现在有个波形文件需要做功耗处理，仿真是45corners的结果，corner文件在.../corners.sp，仿真波形文件在.../pvt.fsdb.grp，我需要对这里面的i(vvdpg)和i(vvdll)两个功耗做分析，二者分别是4PGen和DLL的电流（需要取绝对值），我想分别统计他们在200n~220n的电流（降低功耗前），和400n~500n（降低功耗的电流）...pvt#0和pvt#1是一个corner，因此只统计1～45即可」
- U#1: 「给出完整的所有corner下的结果，除了降低的比例，还有降低的值，列出表格，另外结果存在/home/kaixuanx/ai_project/DLL_TSAC_TOP路径下」

## agent 工具链
- python-runner 跑 power_extract.py：读 fsdb.grp (Synopsys fsdb API) + corners.sp (45 ALTER)，对 i(vvdpg)/i(vvdll) 取 |I|，在 200-220n (Idle_toggle) 与 400-500n (Idle_sleep) 窗口求均值，输出 CSV 表 (corner, before, after, delta, reduce_pct)。
- 后续多轮：make_chart.py 饼图/直方图美化（U#4-U#127 反复调整图例/配色/标注）；扩展到 6400/5200/9500 Mbps 多速率；最终总结为 skill `finesim-power-analysis` (pwr_extract.py / pwr_report.py / pwr_chart.py / pwr_idle_charts.py + SKILL.md)。

## gold 重建 (faithful)
- fsdb 不可移植到评测沙箱 → 资产改为**每个 corner 的波形文本转储** (corner_NN.csv: 列 t + 各信号电流 A)，config.json 描述接口。核心逻辑（|I| 窗口均值 + 45 corner 表 + delta/reduce_pct）保持 faithful。
- gold = `gen_pwr_analysis.py`：读 config.json + corners.sp(ALTER name 解析) + per-corner 波形 CSV，对每 corner×signal 在 before/after 窗口求 |I| 均值×1000→mA，输出 pwr_corners.csv (8 列)。

## 资产
- A (visible): config_A.json (45 corner, i(vvdpg)+i(vvdll), 200-220n/400-500n, tt_* names) + corners_A.sp + waveforms_A/ (45 文件，含负电流样本以验 |I|)
- B (hidden): config_B.json (30 corner, i(vvddq)+i(vvdll), 150-170n/350-450n, ff_* names, csv_name=pwr_corners_B.csv) + corners_B.sp + waveforms_B/ (30 文件) — 结构/规模/取值/命名族全异

## 判分
- check.py **15 条件 a-o**：zip+py_compile+跑B退0出CSV+8列+行数=pvt×sig+before_mA独立重算+after_mA+delta+reduce_pct+corner_name匹配ALTER+signal集合+单位mA+跨输入护栏+3次确定性+|I|abs验证
- ref PASS 15/15 · 4 negatives ALL-FAIL distinct{empty→c / print_fixed_A→e / core_deleted→h / naive_no_abs→f} · §4.9 三假(c/e/h) 3-distinct ✓ · k_rationale=k_check=15 ✓
