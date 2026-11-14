# Waveview 「原意图需看图」用例交底清单（vision → designflow）

> 生成：2026-11-14（vision 线，wake 心跳本轮）
> 触发：用户令 2026-11-14 09:5x「需要多模态的题不要降级，暂时没有多模态能力就让它们 fail」+ 09:1x 四件事之 #2「协调 designflow 评 waveview 用例」。
> 数据出处：`reports/report_vision_waveview_failed_analysis_zh.html`（37 题 / 30 failed / α=4 β=7 γ=26，审计完成于 2026-11-14 08:5x）。
> ⚠️ 口径变更：该审计是在「把视觉判断降级为文本/Tcl」的基准版本下做的；09:5x 起基准已纠正——下列「原意图需看图」用例应**恢复原形态**，无多模态能力的系统**应当 fail**，并以「基线 fail → 上 VQA 后 pass」的差值度量多模态增益。
> 纪律：本清单只做交底，数字可追到上述报告与 designflow `trace_deepreads/` 笔记；🚫 不编造。

## 交底目标

请 designflow 据本清单判断**恢复哪些用例的原（需看图）形态**，并在恢复后跑出**新基线通过率**（预期：这些用例在无多模态时大量 fail）。vision 侧待 designflow 恢复后重新统计 α/β/γ 与新基线。

## α 强相关·识图可解（4 题，恢复后最可能呈现「fail→pass」增益）

| # | 题名 | case_id | 深读笔记（trace_deepreads/） | 评测状态 | 原意图 / 为何需看图 |
|:--|:--|:--|:--|:--|:--|
| 1 | 眼图孔径选择 | EDA-Eval-DesignFlow-EyeApertureSelect-001 | ayya3_waveview_eye_aperture.md | 未评测 | DDR/LPDRAM 眼图 VREF 扫描选最大眼孔径；原意=眼图视觉判断，合成降级为 .rep 文本阈值过滤。识图可直判 VREF=100 眼张开最大。 |
| 2 | 上升沿 margin 测量+标注 | EDA-Eval-DesignFlow-RiseEdgeMargin-001 | xr6sg_waveview_riseedge_margin.md | 未评测 | WaveView3 两信号上升沿 margin(skew) 并在波形上标注；原意=图形化测量+标注，降级为 CSV 线性插值。识图可直读上升沿时差。 |
| 3 | DQ 读路径波形比对根因定位 | —（h8pcp, B-grade 计划） | h8pcp_dq_readpath_wavedebug.md | 未评测 | golden vs actual 两份波形定位 DQ 不一致根因（哪一级/哪个信号）；本质=两波形视觉 diff 找首处分叉。识图可直看出哪一级开始分叉。 |
| 4 | 温度传感器波形功能推断 | EDA-Eval-DesignFlow-TempSelWaveform-001 | gtyj5_temp_sel_waveform.md | 未评测 | 「根据波形说明 signal 的功能」：从温度传感器 sel* 波形推断「区间选择器、按温度区间激活」。波形形态→功能语义，识图可直读激活区间。 |

## β 弱相关·识图有帮助（7 题，恢复后可能部分呈现增益）

| # | 题名 | case_id | 深读笔记（trace_deepreads/） | 评测状态 | 原意图 / 识图作用 |
|:--|:--|:--|:--|:--|:--|
| 5 | FSDB 信号翻转诊断（stuck/active） | EDA-Eval-DesignFlow-FsdbNetToggleDiag-001 | 1793078405436_t0aom_finesim_fsdb_netlist_diag.md | 未评测 | 从 FSDB 识别 stuck(从不翻转)/unexpected-active 信号+netlist 交叉对照。识图可目测 stuck 线，脚本读 transition 更严谨。 |
| 6 | 波形对比 CLI（边沿序列 diff） | —（3qe6x, B-grade 计划） | 3qe6x_wavecmp_wrap.md | 未评测 | WaveCompare 两波形边沿序列对比判 EQUIVALENT/DIFFERENT/GRAY。识图可看分叉，但 corner VDD 不同致视觉叠加歧义，算法更可靠。 |
| 7 | Write→DQ 边沿间隔测量 | EDA-Eval-DesignFlow-WrDqMeas-001 | 4v4nf_fsdb_wr_dq_meas.md | 未评测 | 测 write 命令到 DQ 第一上升/下降沿间隔。识图可估读时序，精确测量需脚本读 .vec 边沿。 |
| 8 | FSDB 信号类型/功能分析器 | EDA-Eval-DesignFlow-WaveView-002 | as67p_waveview_ace_fsdb_signal_extractor.md | DEFERRED | 读 FSDB 判数字/模拟、边沿/脉冲/过零并说明功能。功能说明偏视觉推理；pi 预算不足未跑。 |
| 9 | 波形信号最大值查找 | EDA-Eval-DesignFlow-WaveMaxFind-001 | sid_1793694775768_80yiq_wave_max_find.md | 未评测 | 「计算当前波形中信号 v(vb) 的最大值」。识图可读峰值，sx_meas_max 更精确；real session sandbox 超时未产出。 |
| 10 | 温度阈值表征 | EDA-Eval-DesignFlow-TempThreshChar-001 | okq91_tempthresh_finesim_fsdb_char.md | 未评测 | 从 FineSim FSDB 做温度阈值表征。识图可看阈值穿越，脚本测更准。 |
| 11 | SRAM 仿真失败 FSDB 探查 | EDA-Eval-DesignFlow-SimFailFsdbProbe-001 | woanw_sram_simfail_fsdb.md | 未评测 | 读 timing_check TEST 模式 violation 分支定位 SRAM sim 失败。识图可看违例区间，脚本读 violation 更准。 |

## 汇总

- 原意图需看图（交底给 designflow 恢复）：**α 4 + β 7 = 11 题**（占 37 题的 29.7%）。
- γ 26 题为脚本/环境/语法类，**不应恢复为看图形态**（与多模态无关）。
- 已评测 PASS 的 7 题全为 γ（此前因降级而通过；若其中含「原意图需看图」者应一并复查——当前 7 题均判定为 γ，故不在本交底清单内）。

## 下一步（依赖链）

1. designflow 据本清单恢复 11 题原形态 → 跑出新基线（无多模态）通过率。
2. vision 把 Qwen3.5-2B 封装为 VQA tool（#3）→ designflow 用同一批题再评 → 对比报告「哪些题靠 VQA 翻转」。
3. vision 用合成数据/SFT/RL 强化 VQA tool 识图能力（#4）→ 再评 → 证明显著提升（对照 + 显著性）。
