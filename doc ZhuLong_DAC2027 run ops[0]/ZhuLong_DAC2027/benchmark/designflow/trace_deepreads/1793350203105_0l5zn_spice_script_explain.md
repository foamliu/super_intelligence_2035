# Deepread Note: 1793350203105_0l5zn — Spice Script Pipeline Explain

## Trace Summary
- **Session**: `1793350203105_0l5zn.messages.json`
- **User**: chentong @ hfeg0plg76
- **Match count**: 37 (spice_sim domain, shard B)
- **Real task**: 用户上传 8 个组合逻辑真值表验证脚本，要求 agent 依次读取并讲解整套流程

## Pipeline Scripts (8 files)
| # | File | Lang | Role |
|---|------|------|------|
| 0 | `000_count_cells.il` | SKILL | 统计 Library 下 Cell 数量 (ddGetObj→length(cells)) |
| 1 | `00_PIN_Check.il` | SKILL | 导出 pin 信息 CSV，标注非 signal pin |
| 2 | `0_kt_cdlout_lib.il` | SKILL | 批量 CDL netlist 导出 (si -batch auCdl) |
| 3 | `1_Truth_table_cdl_Replace.py` | Python | CDL 预处理：MUX pin 重排 + 器件名加 X 前缀 |
| 4 | `2_CLC_Truth_table_classify_cells_cdl.py` | Python | Pin/Cell 分类：扫描 .cdl，按命名约定分 input/output |
| 5 | `3_CLC_Truth_table_hspice_alter.py` | Python | HSPICE 穷举激励生成：2^N 测量点 PULSE V 源 |
| 6 | `4_CLC_Truth_table_sim.sp` | HSPICE | 仿真 deck 模板：.TEMP/.LIB/VDD/subckt |
| 7 | `5_Truth_table_summary.py` | Python | 结果汇总：二值化 + FAMILY_RULES 家族归类 |

## User Follow-ups
1. "read and explain all scripts"
2. "walk through with an example"
3. "must truly read code not comments"
4. "explain family grouping logic"
5. "is grouping by name or content?"
6. "so same truth table → same group?"

## Case Construction
- **Form**: B档 synthesized (A档 infeasible: pure Q&A with no deliverable file)
- **A assets**: 8 real scripts scp'd from hfeg0plg76 (verbatim)
- **B assets**: 8 synthesized variant scripts with 12 parameter differences:
  - MUX regex: `^S\d*$` → `^SEL\d*$`
  - Output tuple: `('Z','CO','Q')` → `('Z','CO','Y')`
  - NEW_INPUT: `['CP','TE','E']` → `['CK','EN','TE']`
  - IGNORE: +`DCAP` (6→7 entries)
  - PULSE voltage: 0.75 → 0.9
  - TEMP: 25 → 27
  - VDD DC: 0.75 → 0.9
  - Lib process: 35H → 28H
  - Model name: tt_mos_varactor_dbc → tt_mos_varactor_28h
  - Binarize high threshold: 0.74 → 0.7
  - Binarize low threshold: 0.1 → 0.2
  - FAMILY_RULES count: 20 → 18 (buff/clkbuff→clkbuf merge, clk removed)

## Verification
- Reference solution: PASS (parses both A and B correctly)
- 4 negatives: all FAIL (empty_shell, print_only, hardcode_a, core_deleted)
- k_check = 45, k_rationale = 45
