# Deepread — 1789610397098_48m5j (ericw @ hfhds206, mc=28)

**Selected for shard D #530** → case `EDA-Eval-DesignFlow-Ddr5ClDelayPivot-001`
- domain: analog_context
- track: synthesized
- difficulty: L2
- host: hfhds206 (10.129.32.80)
- user: ericw (fresh-USER — not previously used in D.jsonl)
- session_msgs: 87 (44 user / 43 assistant)
- tools used: editor×16, read_files×15, list_allowed_files×3, run_commands×2, skills×2

## Real task summary

DDR5 DRCPA analogsim engineer. The Verilog FSM `Task4FSM.v` declares, for every
supported DDR5 speed grade (`"TS_<data_rate_MT/s>":begin` block), the CAS
Latency (CL, in units of tCK) loaded into MR0 via `Load_Mode(.ma(MA_CL),
.op(CL_<n>tCK), ...)`. The CL value is selected by a PVT-corner macro chain:
`` `ifdef FF / `elsif TT / `elsif SS / `else `` (wrapped in an outer
`` `ifdef OVERCLOCK `` that the user wants ignored for the table).

User's evolving request (verbatim, condensed):
1. "分析这个sp文件，最好是逐行解析" (initial — sp file analysis)
2. **core task**: "从304行这个分支开始有 关于不同speed下 CL的值的定义 比如9600 SS corner下 CL的delay为 2除以9600×82 = 19.16 ns 帮我计算总结各个speed 各个corner下的CL delay 做一个excel表格"
3. refinement: "这个表格不够直观 改成下面这种形式 Speed\tSS\tTT\tFF / TS_10400\t17.69\t15.77\t13.85"  (pivot: rows=speed, cols=SS/TT/FF)
4. refinement: "再加一列 内容是对应speed 一个CK的大小" (add tCK column)
5. refinement: "CK的大小放在最后一列" (tCK column → last)

Final deliverable the agent produced: `/home/ericw/ddr5_cl_delay_pivot.csv`
with header `Speed Grade,SS (ns),TT (ns),FF (ns),tCK (ns)`, one row per speed
grade in file order, delays rounded to 2 dp, tCK rounded to 3 dp.

## Formula (as the user stated & the agent applied)
- `tCK_ns   = 2000 / data_rate_MT_s`   (user said "2除以9600" → 2/9600 ns? No:
  the user's "2除以9600×82" = (2/9600)×82 ×1000? Actually 2000/9600×82 = 17.08,
  user wrote 19.16 for SS=92 → 2000/9600×92 = 19.17. So formula is
  `CL_delay_ns = CL_tCK × (2000 / data_rate)`, `tCK_ns = 2000 / data_rate`.)
- `CL_delay_ns = CL_tCK × tCK_ns`

## Why this is a good design_flow case (analog_context)
- **Produce-task**: single concrete deliverable (a CSV), reproducible byte-for-byte.
- **Self-contained**: the only input is a Verilog file; no simulator/license/
  waveform files needed. Easily reduced to a synthetic A/B/C trio.
- **D-domain**: DDR5 timing characterization from Verilog mode defines — squarely
  analog_context (measurement / corner / timing-table synthesis), and D.jsonl's
  analog_context bucket (78) is the 2nd-least-covered after waveform (64).
- **Multi-step but well-defined** → L2: parse Verilog ifdef/elsif corner
  branches, extract `CL_<n>tCK` per corner, compute delay, build pivot with
  correct column order + rounding + row order.
- **Fresh-USER** (ericw never used in D.jsonl before).

## Synthesis plan (disjoint A/B/C)
- **A** (public, 10 grades): TS_10400/9600/8800/8000/7200/6400/5600/4800/4000/3200
- **B** (hidden, 13 grades): TS_9500/9200/8600/8400/8200/7600/6800/6720/6000/5200/4400/3600/1600
- **C** (embedded in check.py, 8 grades): TS_9800/8900/7800/7000/6200/5400/4600/3800

All three: disjoint grade-name sets, disjoint counts (10/13/8), disjoint CL
values. check.py runs SUT on hidden B (9 assertions) + embedded C (anti-hardcode:
C row-count ≠ B, C grade names disjoint from B, C values match C oracle).

## check.py assertion count: 9 (k_check = 9, k_rationale = 9 ≥ 8)
1. source hygiene (non-empty + no banned import/call + no B/C literal leak)
2. py_compile passes
3. SUT runs on hidden B, exits 0, produces pivot_B.csv
4. CSV header exact (5 cols in order)
5. row count == #grades in B
6. grade names in file order
7. tCK column matches oracle (3 dp) for all rows
8. SS/TT/FF delay columns match oracle (2 dp) for all rows
9. anti-hardcode C variant (different count, disjoint names, C values match C oracle)

## Verification (all PASS)
- ref_sut on A byte-matches example_report_A CSV ✓
- check.py self-test (ref_sut) → SELF-TEST: PASS ✓
- negative_selftest: empty_shell / print_only / hardcode_a / core_deleted all correctly FAIL ✓
- 3-seed sha256 of ref_sut-on-B stable: 542a49752c81... ✓
- ref_sut sha256(zip) prefix: 1de2cb8163cb

## trace_source (for metadata)
- host: hfhds206
- session_file: 1789610397098_48m5j
- session_msgs: 87
- user: ericw
- real_task_summary: "DDR5 Task4FSM.v 速度档×PVT corner CL(CAS Latency, tCK 单位)解析 → 计算 CL delay(ns)=CL_tCK×(2000/data_rate) → 生成 pivot CSV (Speed×SS/TT/FF + tCK), 列顺序 SS/TT/FF/tCK, delay 2dp tCK 3dp"
