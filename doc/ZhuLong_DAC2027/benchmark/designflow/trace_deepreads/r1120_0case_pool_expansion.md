# r1120 (shard B) — 0-case stop-loss + 1124 scan pool expansion

**日期**: 2026-11-24 04:1x
**轮次**: r1120 (loop shard B, 03:47:41 启动)
**结果**: 0-case stop-loss（produce 池真·趋紧，3 真 peek 全 reject + 1124 scan top hspice 全 ledgered）

## 1. 候选选取

从 `b_fresh_1123_Bonly_538.tsv`（11-23 fresh 池, 538 行）按 spice 关键词密度排序取高 mc 候选。
refresh 候选池口径: mc 5-60, hspice/finesim/siliconsmart/spectre/ngspice 合计 >=12, spice/total >=0.15。

## 2. 真 peek 3 候选（全 reject）

### 2.1 bqpjv (clarawu@hfhds201, mc39, netlist:144 hspice:144 schematic:144)
- **深读**: 67 msgs / 331KB。clarawu 写 Python 脚本从 HSPICE `.md0` 测量文件 (Ron.md0, Ron#1.md0) 提取 Ron (rpu_50/rpd_50) 随 zqdec 变化的线性度(一阶差分 max|d1|)、光滑度(二阶差分 max|d2|)、单调性(all d1<0))，并 merge 进 extract_all.py。
- 完整复刻了 assistant 的 ron_linearity_smoothness.py + ron_lin_smooth_stats() + 4 文件×2 信号的真实输出（从 msg 9 stdout 重建 64 点 rpu_50/rpd_50 数据，summary 与 trace 报告完全一致: Ron.md0 rpu_50 lin=8.56@1->2 sm=5.15@2 mono-dec 等）。
- **REJECT**: 台账已 parked (r913)，标注 near-dup of `RonCurveSmoothness-001` + `RonDvqSlopeExtract-001`。核对 cases/B/ 确认 `EDA-Eval-DesignFlow-RonCurveSmoothness-001` 已存在（clarawu, .md0 parser, rpu_50/rpd_50, zqdec, linearity/smoothness/monotonic）——核心 .md0 parse + d1/d2 + monotonic 完全重叠。bqpjv 仅增量(d1@zqdec/d2@zqdec location + 3-way direction)，不足以脱离 near-dup。parking 正确，不推翻。

### 2.2 gug8y (alan17z@hfhds201, mc28, netlist:265 hspice:66 .spi:60)
- **深读**: 26 msgs / 274KB。alan17z 合并 3 个 IBIS 抽取 skill (ibis-t2b-gen/ibis-zq-calib/ibis-zq-sim-gen) 为端到端 `ibis-extract` skill，用户令"完全利用 skill 从 0 验证"。
- 本 session 仅有 list_allowed_files/read_files 探索（10+4 次），**无 editor/write 动作** —— 实际 skill 脚本(gen_zq_decks/parse_zq/merge_zq/gen_t2b 等 7 个)在更早 session 创建。本 session 是 verification/orchestration，无独立 produce 交付物可 reframe。
- **REJECT**: verification-only session，无 in-session produce 代码；end-to-end 验证需 hspice bsub 跑（L2/L3 多脚本 skill），超本轮预算且 check 难以对 7-script skill 设齿。

### 2.3 lk95a (ryanren@hfeg0plg95, mc48, schematic:133 netlist:66 analog:53 hspice:25)
- **深读**: 26 msgs / 247KB。ryanren 检查 hspice stimulus 文件 `.meas` 语句 / Iwlp iprobe 电流问题，msg 4 "网表太大仿真太慢只想保留 Iwlp 电流"，msg 25 "meas 语句为什么没输出"。
- **REJECT**: debug-Q&A（"检查我写的有没有问题" / "为什么没输出"），无明确 produce 交付物，判分无齿。同 r1114 reject 的 debug-Q&A 模式。

## 3. 其他候选复核（未 peek，依据 keyword + ledger 状态判）

- **ze989** (clarawu@hfhds201, mc33, netlist:104 hspice:102 schematic:100): clarawu cluster，r913 note 明示"clarawu cluster all Ron/netlist-extract near-dup of 11 existing clarawu cases"。REJECT near-dup。
- **qsn6y** (joeyl@hfeg0plg74, mc23, spectre:34 hspice:18 netlist:196): r1088 已 peek reject（cross-shard D 占/near-dup）。
- **7xh6n** (e0018590, mc31, synopsys:54 hspice:35): r1113 已 peek reject（165msg 多为 ewave-license/LSF env-Q&A 混杂）。

## 4. 1124 scan pool expansion（重点产出）

执行 MEMORY r1119 next-step："扩 1124 scan 低 mc(<50) hspice/finesim/spectre 子域"。

- 拉 `.75:/home/t0002965/log/ssh_eda_search_20261124_023802/summary.tsv`（52378 行，较 1123 scan +6956 traces）。
- 过滤: mc 5-60, hspice/finesim/siliconsmart/spectre/ngspice 合计 >=10, spice/total >=0.15 → **876 候选行**（含跨 host 重复）。
- 去重得 top unique sids，核对台账状态:

| sid | user | mc | spice | top_kw | 台账状态 |
|---|---|---|---|---|---|
| cixxj | e0029308 | 21 | 20513 | hspice | **case** (已 ledger) |
| whc3n | zanezang | 5 | 2631 | hspice | parked (2 entries) |
| zns2p | shanmei | 43 | 2048 | hspice | **case** (已 ledger) |
| 2kj3r | e0029495 | 5 | 1977 | verilog | case (verilog-dominant, 非 B-spice) |
| sgk0l | vincentz | 56 | 1466 | hspice | **case** (已 ledger) |
| fhfno | vincentz | 54 | 1464 | hspice | **case** (已 ledger) |
| qetcj | kaixuanx | 58 | 1025 | hspice | **case** (已 ledger) |
| mv4xp | zlhou | 16 | 797 | hspice | **case** (已 ledger) |
| t1epq | e0030760 | 48 | 712 | hspice | **case** (已 ledger) |
| 4msey/5ue0u | chapinc | 5 | 679 | netlist | **case** (已 ledger, netlist-dominant) |

**结论**: 1124 scan 的 top hspice-dominant 候选（mc≥16 或 spice≥700）**全部已 ledgered（case/parked）**。印证 MEMORY r1118 "produce 池趋紧(top80 全 ledgered)"。1124 scan 未带来新的高质 B-spice produce 候选。

剩余 876 候选里 mc 5-15 / spice 10-100 的低 mc 段可能有未 ledger 项，但低 mc session 多为 Q&A/短交互（r1114 已验证 peek 10 全 reject），produce 命中率低。

## 5. 判定

**0-case stop-loss**。依据:
1. 真 peek 3 候选全 reject（near-dup / verification-only / debug-Q&A）
2. 复核 3 候选全 reject（clarawu cluster near-dup / 已 peek reject / 已 peek reject）
3. 1124 scan pool expansion 产出负结果：top hspice 候选全 ledgered，无新高质量 produce 候选

**不是 §4.9 selftest wrap**：r1119 已收口 B 域 selftest gap（仅 1 条已补完），无 selftest 欠债。

## 6. 下一步建议

- 1124 scan 低 mc 段（mc 5-15, spice 10-100）仍有 ~800 未 ledger 候选，但需大批 peek 才能命中 produce，ROI 低
- 等待下一次 scan（1125+）带来新 trace
- 或考虑跨 shard 协调：B-spice 高质 trace 可能已被 D shard（schematic_netlist/waveform）覆盖
- 维持 stop-loss 纪律：不凑 weak case，不降闸门

## 7. 产物

- `designflow/b_spice_1124_top50.tsv` — 1124 scan B-spice top 候选快照（含台账状态标注）
- `designflow/trace_deepreads/r1120_bqpjv_ron_lin_smooth.md` — bqpjv 深读（含重建的真实 .md0 数据 + summary 验证）
- 本文件 `designflow/trace_deepreads/r1120_0case_pool_expansion.md`
