# Deepread: lxy78 — AutoDebug V3 run 波形比对按时序分段解释

- **session**: `1791795684242_lxy78.messages.json`
- **user**: e0039602 (原始用户名, 不 hash)
- **host**: hfeg0pkn003 (10.129.2.12)
- **match_count**: 22 (netlist:64;waveview:38 — D-pure waveform)
- **domain**: waveform
- **case_id**: EDA-Eval-DesignFlow-WaveformStagePartitionQA-001
- **ledger status**: case (r769)
- **档位**: A档 trace-faithful "explain/partition produce" 型

## 真实任务 (verbatim U#21)

> 请你阅读run_20260929_152125_v3_b0dq0下所有的波形比对，然后简单按照对比的时间顺序把一系列波形比对划分为几个部分，给出每一部分在干什么

## Trace 概况

- 38 msgs, 2 user request turns
- 用户唯一实质性请求 = U#21 (上文)
- 助手读取 run 目录下 run.log / conclusion.json / waveforms/*.fscr, 按时间顺序把波形比对分段并解释每段在做什么
- 源 run 目录 `run_20260929_152125_v3_b0dq0` 在目标主机 hfeg0pkn003 上**已被删除** (10.129.2.12 上 ls 返回 not found)
- **恢复方式**: 从 trace 的 tool_results (read_files 结果在 `result` 字段) 中提取 40 个源文件, strip 行号前缀 (`  N | content`), 重建 A 资产

## 源 run 目录结构 (恢复后)

```
run_20260929_152125_v3_b0dq0/
├── run.log              # AutoDebug V3 stage 头 (S0-S5 + S2-Rk/S3-Rk/S4-Rk/S5-Rk + [P6 外扩重提])
├── conclusion.json      # 结构化结论 (fail_net/pvt/verdict_counts/rounds/drill_params/divergence_set)
├── conclusion.md        # 人类可读结论 (与 json 同源)
└── waveforms/
    ├── cone_r1_fail.fscr / cone_r1_pass.fscr   # R1 cone 提取 (双 corner)
    ├── cone_r2_fail.fscr / cone_r2_pass.fscr   # R2 cone
    ├── cone_r3_fail.fscr / cone_r3_pass.fscr   # R3 cone
    ├── nodata_r1_fail.fscr / nodata_r1_pass.fscr  # R1 NO_DATA 消歧
    ├── nodata_r2_fail.fscr / nodata_r2_pass.fscr  # R2 NO_DATA
    └── wcx_xi_channel_*_fail/pass.fscr (5 对)  # P6 外扩重提 (wcx)
```

## A (visible) 关键参数

| 字段 | A 值 |
|---|---|
| fail_net | `dq0<0>` |
| fail_pvt | `SS0.88v-40c` |
| pass_pvt | `FF1.15v130c` |
| total_nets | 311 |
| verdict_counts | {EQUIVALENT:141, DIFFERENT:159, GRAY:10, NO_DATA:1} |
| rounds | 3 (seeds: dq0<0> → 2 nets → 1 net) |
| drill_params | max_rounds=3, max_depth=16 |
| divergence_count | 159 |
| main window | 834.5n~838.5n step 10p |
| WCX (P6) window | 832.5n~840.5n step 50p |
| stages (6) | R1_cone, R1_nodata, R2_cone, R2_nodata, R3_cone, P6 |

注: A 的 nodata 只有 r1/r2 (无 r3), 故 6 stages = 3 cone + 2 nodata + 1 wcx(P6).

## B (hidden) 系统变换

| 字段 | A → B |
|---|---|
| fail_net | `dq0<0>` → `dq5<3>` |
| fail_pvt | `SS0.88v-40c` → `SS0.77v-25c` |
| pass_pvt | `FF1.15v130c` → `FF1.24v110c` |
| pattern | `PerBnk_ActWrPreActRd_4b4g_B0_tck0.313nsRL68WL32TS_12800_...` → `PerBnk_ActRdPreActWr_8b4g_B2_tck0.275nsRL72WL36TS_6400_...` |
| total_nets | 311 → 287 |
| verdict_counts | {141,159,10,1} → {138,132,14,3} |
| rounds | 3 → 2 |
| drill_params | max_rounds 3→2, max_depth 16→18 |
| main window | 834.5n~838.5n/10p → 712.3n~716.3n/20p |
| WCX window | 832.5n~840.5n/50p → 710.5n~718.5n/100p |
| batch 命名 | `cone_r*` → `drill_r*`, `nodata_r*` → `nadat_r*` |
| stages (5) | R1_cone, R1_nodata, P6, R2_cone, R2_nodata (R3 删除, 因 B 只 2 轮) |
| R1 cone 信号数 | (A 原值) → 122 (B) |
| R2 cone 信号数 | (A 原值) → 80 (B) |

## B2 (anti-hardcode cross-input)

全参异化, 强制 SUT 真解析 run_dir 而非 static print:

| 字段 | B2 值 |
|---|---|
| fail_net | `dq7<2>` |
| fail_pvt | `SS0.66v-15c` |
| pass_pvt | `FF1.35v140c` |
| total_nets | 296 |
| verdict_counts | {EQUIVALENT:151, DIFFERENT:118, GRAY:22, NO_DATA:5} |
| rounds | 3 |
| drill_params | max_rounds=3, max_depth=22 |
| main window | 611.1n~615.1n/20p |
| WCX window | 609.5n~617.5n/100p |
| stages (7) | R1_cone, R1_nodata, P6, R2_cone, R2_nodata, R3_cone, R3_nodata |

## 参考解 (waveform_stage_analyzer.py)

- 读 run.log (stage 头 S0-S5 + S2-Rk/S3-Rk/S4-Rk/S5-Rk + `[P6 ...]` 行) → pipeline 时序
- 读 conclusion.json → summary (fail_net/pvt/verdict_counts/rounds_count/drill_params/divergence_count)
- 读 waveforms/*.fscr → 每 batch: fsdb 路径 (corner PVT 经 generic regex `\.([A-Z]+[0-9.]+v-?[0-9]+c)\.` 提取), fset start/end/step 窗口, dsignal 信号列表
- batch 分类: `cone_rk`/`drill_rk` → cone(round=k), `nodata_rk`/`nadat_rk` → nodata(round=k), `wcx_*` → wcx(P6)
- stage 排序 order_key: wcx → (0,1,2) [P6 位于 R1_nodata 之后, R2_cone 之前]; cone/nodata → (0, round, seq) [cone seq=0, nodata seq=1]
- 输出 JSON: summary + main_window + pipeline_stages + waveform_stages(stage_id/kind/round/batch_name/window/corner_fail/corner_pass/signal_count_fail/purpose) + waveform_stage_count

## check.py (20 条断言, k_check=k_rationale=20)

- ① zip 含 waveform_stage_analyzer.py + 无 NUL + 无 A-only 字面量泄漏
- ② py_compile 通过
- ③ B 运行 exit 0 + 有效 JSON dict + 4 顶层键
- ④-⑱ B 的 15 项结构断言 (fail_net/fail_pvt/pass_pvt/total_nets/verdict_counts/rounds_count/drill_params/divergence_count/waveform_stage_count/stage_order/R1_window/R1_sigs/P6_window/main_window/corner_fail)
- ⑲ 反硬编码 B2: fail_net/total/rounds/stage_count/main_window/stage_order 全反映 B2 (证明 SUT 真解析, 非 static print)
- ⑳ 确定性: 3x md5 一致

## 自验

- 参考解 self-test: PASS (20/20)
- 5 负样本 (empty/print_only/hardcode_a/always_ok/wrong_counts): 全 FAIL (NEG_RC=0)
- 2 退化 (empty.zip 无 SUT / print_only.zip static print B 答案): 全 FAIL (反硬编码 B2 守住)

## 设计要点

- **generic corner regex** `\.([A-Z]+[0-9.]+v-?[0-9]+c)\.` — 不 hardcode A 的 `SS0.88v-40c`/`FF1.15v130c`, 自动适配 B/B2 的任意 PVT
- **stage order 基于 batch 分类** (非 run.log 行序) — 数据驱动, 适配任意 rounds 数
- **anti-hardcode B2** — 全参异化 (fail_net/total/rounds/window/stage_count 全不同), 强制 SUT 输出随输入变化, 堵死 static print
- **源文件恢复** — run 目录在主机上被删, 从 trace tool_results 重建, strip 行号前缀, 保持 A 档 trace-faithful
