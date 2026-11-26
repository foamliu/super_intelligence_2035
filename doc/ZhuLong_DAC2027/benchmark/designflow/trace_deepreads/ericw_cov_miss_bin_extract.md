# 深读笔记 · ericw 1793586676522_9kzwd · CovMissBinExtract-001 · spice_sim

## trace 元信息
- user: ericw · host: hfhds201(.75) · session: 1793586676522_9kzwd.messages.json
- size: 1,097,420 B (1.1MB) · msgs: 101 · match_count(spice_kw): 1017
- 时间: 2026-11-02 附近（analyze_cov.py mtime Nov 2 10:35）
- ledger: claimed + marked case (EDA-Eval-DesignFlow-CovMissBinExtract-001)

## 用户轮（任务意图）
- **U#0 (任务轮, 逐字原文)**:
  `/rundata/drcpa_sim/V0/simdir/finesim/workdir/ericw/verilog.ddr5.drcpa.aicov/cov_work/html_02-11-2026_10~05~53 分析这个结果，将没有命中meet_exactly的bin筛选出来`
  → 纯目标轮：给覆盖率目录 + 筛选目标（未给根因/未给修复方案）→ 合格 A-档任务说明
- **U#63 (提示轮, 不入任务说明)**:
  `你接着往下找来吗 下面还有table2 table3 ，table3里才有meet exactly的具体信息`
  → 提示轮（指出 meet_exactly 信息在 table3）→ 按 A-档规则不入 prompt，可作 hint

## assistant 工具链
list_allowed_files → read_files(覆盖率目录) → read_files(table1.json) → search_codebase →
read_files(table2/table3) → SandBox_MCP_Server__run_code → editor(写脚本) →
run_approved_command/run_commands(执行) → editor(多次迭代修脚本) →
最终产出 /home/ericw/analyze_cov.py (4683B)

## 金标准 (analyze_cov.py 解析逻辑)
覆盖率目录三级 JSON 层级：
- `table1.json` = [ {title, excluded, items_json -> table2 file}, ... ]（covergroup 列表，544 个）
- `table2/<cg>.json` = [ {title, items_json -> table3 file}, ... ]（coverpoint 列表）
  - 关键 coverpoint: `cp_delta_min_vs_constraint_min`、`cross_speed_min`
- `table3/<cg>_<kind>.json` = [ {title, "All Cov", Score}, ... ]（bin 列表）
  - 关键 bin: `meet_exactly`、`meet_exactly;SPEED_<grade>`
  - 未命中判据: "All Cov" 含 `0 / 1` 或 `(0%)`

输出：
- PART 1: cp_delta_min_vs_constraint_min -> meet_exactly 未命中 bin 列表
- PART 2: cross_speed_min -> meet_exactly;SPEED_* 未命中 bin 列表（按 covergroup 分组）
- SUMMARY: total_simple / total_cross / unique_covergroups / speed_breakdown

## case 合成
- **case_id**: EDA-Eval-DesignFlow-CovMissBinExtract-001
- **domain**: spice_sim · **track**: synthesized（真实覆盖率目录已清理，资产按真实结构合成）· **level**: L1
- **交付**: `gen_cov_miss_report.py <cov_dir> <outdir>` → miss_report.json + miss_report.md
- **A 资产**: 合成 DDR5 覆盖率目录（cov_A/，8 covergroup，SPEED_DDR5_3200/4800/6400）
- **hidden B**: 合成 LPDDR5 覆盖率目录（cov_B/，6 covergroup，SPEED_LPDDR5_5500/6400/8400，不同 hit/miss 模式）
- **check.py**: 12 条独立断言(a-l)
  - a zip+gen_cov_miss_report.py / b py_compile / c 无参非零 / d B exit0+2文件 /
    e JSON+3键 / f simple=3 / g cross=8 / h 100%bin不入miss(假阳性闸门) /
    i speed字段SPEED_LPDDR5_*拆分 / j summary 3/8/4 / k speed_breakdown{5500:2,6400:3,8400:3} / l 幂等
- **自验**: ref PASS(12/12) ✓ · 3 negatives(fake_empty/fake_print_expected/fake_core_deleted) 全 FAIL ✓ ·
  §4.9 (a)empty-shell (b)print-expected (c)core-deleted 三假全 FAIL ✓
- **断言闸门**: k_rationale=12 == k_check=12 ≥ 8 ✓

## 与现有 case 区别
- CovFMFlow-001（lorikx）= 建覆盖率 flow（lint+综合+仿真覆盖率流程）
- 本 case = 解析已有 finesim 覆盖率结果，抽取未命中 meet_exactly bin（结果分析/解析子流）
