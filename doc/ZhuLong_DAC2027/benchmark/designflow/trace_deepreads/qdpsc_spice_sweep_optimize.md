# deepread: 1794471129064_qdpsc — SpiceSweepOptimize (2nd case, distinct intent)

- **session**: `1794471129064_qdpsc` (jiangbaol @ 10.129.2.13, mc=146)
- **size**: 233 msgs / 1.06 MB messages.json (subdir path `1794471129064_qdpsc/`)
- **domain**: analog_context (SPICE 参数 sweep 优化，DqIb DDR4 DFE slicer)
- **本 case 覆盖的意图**: U#55 sizing-sweep-optimize（与既有 SpiceMeasInject-001 的 U#33 measure-inject 意图互斥）

## 用户真实意图流（10 个 user 轮）
- U#0: SPICE 报错 `duplicated subckt definition 'DqIb_2stg_DfeM6V2'` 该如何修改（Q&A）
- U#2: 如何设置 option 让 hspice 输出波形每层级包含所有 net 信号（Q&A）
- U#7: 检查 `.sp` 为何无法 probe slicer_out / slicer1st_out 并改正
- U#33: 在 `.sp` 中添加 measure 语句（测 XI7 功耗 / ldfedata 下降沿时刻 / outn_stg1 与 outp_stg1 电压）→ **既有 SpiceMeasInject-001 覆盖**
- **U#55: 调节 doubletail_nmoslatch 输入对管 M1,M2 与第一级尾电流管 MP1 尺寸，使 t_ldfe_first_fall 时刻 max(V_outn_stg1_at,V_outp_stg1_at)≤480mV，使该时刻 |ldfe_dm| 最大，仿真核验迭代出最佳方案 → 本 case 覆盖（A档 verbatim prompt）**
- U#148: 改目标为 |slicer1st_out| 最大，重新 sweep
- U#163: 输入对管类型 pulvt_ckt→prvt_ckt，约束放宽至 600mV，再 sweep
- U#207: 改目标为 t_ldfe_first_fall 时刻 |slicer_out| 最大，给最佳 M1/M2/MP1 尺寸+关键指标
- U#9: 上下文窗口不够，总结成 agent 可读说明文档（Q&A）
- U#10: LATCH05C symbol 与 latLV 不一致 为什么（Q&A）

## assistant 工具链
真跑 Finesim（`/apps/synopsys/SRB/finesim/V-2023.12-1/bin/finesim`）：编辑 `run_004.sp` 注入 `.param win/wtail` + `.meas` → 多批 `sweep_batch.sh` 迭代（win 0.3–28u × wtail 1–12u，10+ 批）→ 解析 `run_004.mt0.csv`（8 列测量）→ 按约束过滤 + 选 |目标| 最大点。涉及 LD_LIBRARY_PATH/license env 调试、netlist_par 参数化、best 点回写 netlist_best。

## 真实 sweep 输出（8 列，prvt era，U#207 阶段）
表头：`win,wtail,t_ldfe_first_fall,V_outn_stg1_at,V_outp_stg1_at,ldfe_dm,slicer1st_out,slicer_out`
真实样本（逐字自 tool_result）：
```
0.5,2.0,1.5979e-09,4.6902e-01,4.2909e-01,-2.0578e-01,-3.9925e-02,-2.0578e-01
0.5,1.5,1.6000e-09,4.5947e-01,4.1752e-01,-2.2077e-01,-4.1951e-02,-2.2077e-01
0.5,1.2,1.7599e-09,4.5224e-01,4.1006e-01,-2.5097e-01,-4.2187e-02,-2.5097e-01
0.4,1.5,1.6028e-09,4.4634e-01,4.0570e-01,-2.5838e-01,-4.0649e-02,-2.5838e-01
0.6,1.5,1.5978e-09,4.6761e-01,4.2431e-01,-2.5205e-01,-4.3307e-02,-2.5205e-01
...
```
（sweep_results_A.csv 的 10 行均取自上述真实数值；config_A 的 480mV 约束 + ldfe_dm 目标对齐 U#55 原话。注意：trace 中 prvt era 实际约束为 600mV、目标 |slicer_out|；本 case 为对齐 U#55 verbatim，采用 prvt 数据 + 480mV + ldfe_dm，因 prvt 行 Voutn 普遍 <0.50，480mV 下可行点充裕且最佳 |ldfe_dm|=0.25838 @ (0.4,1.5) 清晰。）

## case 设计
- **A档 trace-faithful verbatim prompt** = U#55 原话 + 一行交付桥接句
- **produce-parser reframe**: `sweep_optimize.py` 读 sweep CSV + config JSON → 按约束 `max(Voutn,Voutp)≤vmax` 过滤可行点 → 最大化 `|objective|` → 输出最佳 (win,wtail) + metrics JSON
- **隐藏 B**: 不同 win/wtail 网格 {1..5}×{2,3,4}=15 行，确定性公式生成，约束 0.50、目标 slicer_out，真值 best=(5.0,2.0) |slicer_out|=0.192，2 个不可行点
- **判分牙**: subprocess 在 B 上真跑 + 从 B 重算 ground truth（n_total/n_feasible/best|obj|/best_metrics 逐一比对）+ A 字面量反硬编码源码扫描 + 3 次确定性 md5 + 空 CSV degenerate + 无参 CLI guard = 16 断言
- **3 negatives 全 FAIL**: empty_shell(stdout 非 JSON) / print_expected(A 字面量命中反硬编码) / delcore(n_feasible 错)

## 同 session 第二条 case 的合规性
依 2026-11-15 任务初衷：同一 session 的不同真实用户意图可分别造 case。qdpsc 早段 U#33 measure-inject 已由 SpiceMeasInject-001 覆盖；其后 U#55 sizing-sweep-optimize 是另一独立意图（选最佳尺寸而非注入测量语句），本 case 覆盖之。两 case 意图互斥、判分对象不同、资产不同。ledger 一条 session 记录限制下，本 case 不重复 claim，仅 append jsonl + 在 trace_source.real_task_summary 注明关系。
