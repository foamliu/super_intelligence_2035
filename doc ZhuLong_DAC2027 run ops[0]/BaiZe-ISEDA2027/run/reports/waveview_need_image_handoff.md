# Waveview 「原意图需看图」用例交底清单（vision → designflow）

> 生成：2026-11-14（vision 线，wake 心跳本轮）
> 触发：用户令 2026-11-14 09:5x「需要多模态的题不要降级，暂时没有多模态能力就让它们 fail」+ 09:1x 四件事之 #2「协调 designflow 评 waveview 用例」。
> 数据出处：`reports/report_vision_waveview_failed_analysis_zh.html`（37 题 / 30 failed / α=4 β=7 γ=26，审计完成于 2026-11-14 08:5x）。
> ⚠️ 口径变更：该审计是在「把视觉判断降级为文本/Tcl」的基准版本下做的；09:5x 起基准已纠正——下列「原意图需看图」用例应**恢复原形态**，无多模态能力的系统**应当 fail**，并以「基线 fail → 上 VQA 后 pass」的差值度量多模态增益。
> 纪律：本清单只做交底，数字可追到上述报告与 designflow `trace_deepreads/` 笔记；🚫 不编造。

## 🔧 勘误（2026-11-14 · vision 线，wake#1210）

> designflow 召集人 shard A 裁定（r508，2026-11-14，见 `WAVEVIEW_COLLAB.md`「召集人裁定」节）：

1. **β5 `FsdbNetToggleDiag-001` 案例不存在**：对 4 shard jsonl（A/B/C/D）全量 `grep FsdbNet` / `FsdbNetToggleDiag` = **0 命中**；仅有深读笔记 `trace_deepreads/1793078405436_t0aom_finesim_fsdb_netlist_diag.md`（trace t0aom）。⇒ **vision 误抄**：把「有深读笔记」当成「有已落库 case」。β5 **不是「已降级可恢复」的 case，而是从未造题**，不在 Task1「恢复原形态」范围内。若需 β5，应走常规造题流程（t0aom → D 或 B 域新造），非 WAVEVIEW 恢复流程。
2. **基线分母订正**：designflow 侧核实的「真·降级文本替身可恢复」分母 = **4**（非本清单原写的 11）。本清单原 11 = α4 + β7，其中 β5 不存在、另有若干为「B-grade 计划/未落库」（如 α3 DQ-readpath、β6 WaveCompare 为 B-grade 计划，β8 WaveView-002 当时 DEFERRED）——这些**不是已落库的降级文本替身**，不应计入「可恢复」分母。vision 接受此订正：**度量多模态增益的基线分母以 designflow 实际恢复并落盘的 case 数为准**（截至本轮 D 已恢复 α1/β9/α4 共 3 题，见下方进展跟踪），而非本清单的交底估计。
3. **β8 `WaveView-002` 归属**：召集人核实 `EDA-Eval-DesignFlow-WaveView-002` **仅存在于 D.jsonl**（1 条，domain=waveform），A/B/C 0 命中 ⇒ 干净归属 D，无跨 shard 冲突（此前疑「A/B/D 同名」是 D 的 WaveView-002 与 B 的 `WaveViewPanel-001` 不同题混淆）。

> 影响范围：本勘误订正的是「交底清单」的可恢复分母口径；`reports/report_vision_waveview_failed_analysis_zh.html` 的 α/β/γ 分类基于 trace 深读笔记（β5 当时即标「未评测·仅深读笔记」），其 α=4/β=7/γ=26 的**分类口径不变**，但应补注「β5 案例未落库（convener r508 核实）」——该报告勘误留作下一轮，本轮先在交底清单落地。

## designflow 恢复进展跟踪（vision 侧记录 · 来源 `WAVEVIEW_COLLAB.md` 交付记录）

| 时间 | shard·轮次 | case | 恢复 | 无多模态基线 | 失败模式 |
|:--|:--|:--|:--|:--|:--|
| 2026-11-14 10:2x | D·r649 | 11 题素材可得性核查 | 方案完成，未恢复 | — | — |
| 2026-11-14 11:0x | D·r650 | α1 EyeApertureSelect-001 | ✅ 移除 .rep 文本替身→真眼图 PNG（3-panel VREF sweep） | **FAIL（正确）** | did-not-engage（2B surrogate 循环 generic ls/find，未读 prompt/PNG） |
| 2026-11-14 11:4x | D·r651 | β9 WaveMaxFind-001 | ✅ 移除波形文本替身→真数据图 PNG（阻尼正弦 v(vb)） | **FAIL（正确）** | engaged-but-incapable（读了 prompt、开 eda_flow session，tool-call 错误循环 abort） |
| 2026-11-14 12:1x | D·r652 | α4 TempSelWaveform-001 | ✅ 移除 .tbl 文本替身→真数据图 PNG（温度选择器梯形脉冲） | **FAIL（正确）** | engaged-but-aborted（接触了图/prompt，2B SFT surrogate tool-call 不可靠，abort 前未产出） |

> **小结**：D 已恢复 3 题（α1/β9/α4），无多模态基线均 **FAIL = 正确行为**（与用户 09:5x 令一致）。剩余 D 域题（β10/β11/β8 已落库 + α3/β6 未落库）下轮起恢复。**#3 后半（无 VQA vs 有 VQA 对照）依赖链正在解锁**：待 D 恢复完毕并跑出完整新基线后，vision 把 Qwen3.5-2B VQA tool（#3 前半已交付·`vision/vqa_tool/`）接入 designflow 再跑同一批题。
> ⚠️ **归因注意（designflow 提示）**：当前 2B text-only surrogate 的 FAIL 混有「模型容量不足未 engage」成分，非纯「image-blind」。为更干净的多模态增益归因，#3 对照宜用「能 engage 任务但读不了图」的更强无多模态模型作基线（vision 侧留意）。

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
| 5 | ~~FSDB 信号翻转诊断（stuck/active）~~ | ~~EDA-Eval-DesignFlow-FsdbNetToggleDiag-001~~ | 1793078405436_t0aom_finesim_fsdb_netlist_diag.md | **案例不存在** | ⚠️ **勘误（convener r508 核实）**：4 shard jsonl 全量 grep `FsdbNet` = 0 命中，仅有深读笔记（trace t0aom），**从未造题**。vision 误把「有深读笔记」当「有已落库 case」。不计入可恢复分母；若需此题走常规造题流程。 |
| 6 | 波形对比 CLI（边沿序列 diff） | —（3qe6x, B-grade 计划） | 3qe6x_wavecmp_wrap.md | 未评测 | WaveCompare 两波形边沿序列对比判 EQUIVALENT/DIFFERENT/GRAY。识图可看分叉，但 corner VDD 不同致视觉叠加歧义，算法更可靠。 |
| 7 | Write→DQ 边沿间隔测量 | EDA-Eval-DesignFlow-WrDqMeas-001 | 4v4nf_fsdb_wr_dq_meas.md | 未评测 | 测 write 命令到 DQ 第一上升/下降沿间隔。识图可估读时序，精确测量需脚本读 .vec 边沿。 |
| 8 | FSDB 信号类型/功能分析器 | EDA-Eval-DesignFlow-WaveView-002 | as67p_waveview_ace_fsdb_signal_extractor.md | DEFERRED | 读 FSDB 判数字/模拟、边沿/脉冲/过零并说明功能。功能说明偏视觉推理；pi 预算不足未跑。 |
| 9 | 波形信号最大值查找 | EDA-Eval-DesignFlow-WaveMaxFind-001 | sid_1793694775768_80yiq_wave_max_find.md | 未评测 | 「计算当前波形中信号 v(vb) 的最大值」。识图可读峰值，sx_meas_max 更精确；real session sandbox 超时未产出。 |
| 10 | 温度阈值表征 | EDA-Eval-DesignFlow-TempThreshChar-001 | okq91_tempthresh_finesim_fsdb_char.md | 未评测 | 从 FineSim FSDB 做温度阈值表征。识图可看阈值穿越，脚本测更准。 |
| 11 | SRAM 仿真失败 FSDB 探查 | EDA-Eval-DesignFlow-SimFailFsdbProbe-001 | woanw_sram_simfail_fsdb.md | 未评测 | 读 timing_check TEST 模式 violation 分支定位 SRAM sim 失败。识图可看违例区间，脚本读 violation 更准。 |

## 汇总

- 原意图需看图（交底给 designflow 恢复）：**α 4 + β 7 = 11 题**（占 37 题的 29.7%）——此为**交底估计**（基于 trace 深读笔记）。
- ⚠️ **分母订正（convener r508）**：其中 β5 案例不存在（误抄），α3/β6 为 B-grade 计划（未落库），β8 当时 DEFERRED —— designflow 侧核实「真·降级文本替身可恢复」分母 = **4**。**度量多模态增益的基线分母以 designflow 实际恢复并落盘的 case 数为准**（截至 2026-11-14 D 已恢复 α1/β9/α4 共 3 题，均 FAIL = 正确无多模态基线）。
- γ 26 题为脚本/环境/语法类，**不应恢复为看图形态**（与多模态无关）。
- 已评测 PASS 的 7 题全为 γ（此前因降级而通过；若其中含「原意图需看图」者应一并复查——当前 7 题均判定为 γ，故不在本交底清单内）。

## 下一步（依赖链 · 进度更新 2026-11-14 wake#1210）

1. designflow 据本清单恢复原形态 → 跑出新基线（无多模态）通过率。**进度**：D 已恢复 α1/β9/α4（3 题，全 FAIL 正确），剩余 D 域题下轮起恢复。
2. ~~vision 把 Qwen3.5-2B 封装为 VQA tool（#3）~~ **✅ 已交付**（`vision/vqa_tool/`：原生多模态 VL server + client，单题样例跑通）→ 待 D 恢复完毕后 designflow 用同一批题再评 → 对比报告「哪些题靠 VQA 翻转」（#3 后半，依赖 D）。
3. ~~vision 用合成数据/SFT/RL 强化 VQA tool 识图能力（#4）~~ **✅ 已交付**（`vision/vqa_tool/sft_rl_strengthen.py`：合成波形 held-out 60→64.4%→73.3%，McNemar p=0.5 未达预注册判据，诚实负向；报告 `reports/report_vision_vqa_strengthen_zh.html`）。scope 限合成波形，不可外推到真实 EDA 波形，需 #3 跨线对照。
4. **本轮新增**：接受 convener r508 订正（β5 不存在 / 分母=4 / β8 归 D），交底清单已勘误；`report_vision_waveview_failed_analysis_zh.html` 的 β5 补注留作下一轮。
