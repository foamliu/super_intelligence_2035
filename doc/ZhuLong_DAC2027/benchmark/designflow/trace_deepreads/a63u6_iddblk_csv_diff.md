# Deepread: 1791955659176_a63u6 (jianwang @ hfhds201) — IddblkCsvDiff

**Session**: 1791955659176_a63u6 | **User**: jianwang | **Host**: hfhds201 (=.75 local) | **msgs**: 40 | **size**: 172KB
**Domain**: characterization | **Track**: A-faithful | **Level**: L1

## User turns (verbatim, A-档 任务说明)
- USER#1 (msg0): 在linux操作界面内，我有一些csv格式的文件，我希望你可以把这两个格式的csv文件做差，并将差异比较大的项高亮出来
- USER#2 (msg6): /proj/drgqa/V0/simdir/finesim/drgqaF/MatrixRun_Netlist_IDD_20260902pm_RevC_JEDEC_OC/idd0RevCx4-6400.x4.TT1.166v98c.current/iddblk.csv和.../idd2n-6400.x8.TT1.166v98c.current/iddblk.csv，我希望你按cellname匹配后计算插值。计算的数据通过表格中的ext_vdd+ext_vddq+ext_vpp*1.64得到
- USER#3 (msg28): 可以帮我把上面的数据中，绝对差值大于10的摘出来，做一张对比的柱状图吗

**A-档 判定**: CLEAN ✓ — 纯需求轮给目标(对比两 CSV 按 cellName 匹配 + 公式 calc + |diff|>10 高亮 + 柱状图), 未给根因/修复。

## Assistant tool chain
list_allowed_files(2) → read_files(7) → editor(5, compare_idd.py 分块写入) → run_approved_command(2) → run_commands(1, disabled)

## Key artifacts
1. **compare_idd.py**: 读两 iddblk.csv(csv.DictReader)→按 cellName 匹配→calc=ext_vdd!+ext_vddq!+ext_vpp!*1.64→diff=f2-f1→pct=diff/c1*100→|diff|>阈值高亮→写 CSV(idd_compare_highlight.csv)+HTML
2. **plot_idd_compare.py**: matplotlib Agg 双联柱状图(上图 x4 vs x8 分组, 下图 diff), 筛选 |diff|>10
3. **idd_compare_highlight.csv**: 88 common cells, 26 |diff|>10
4. **idd_compare_barchart.png**: 26 cells bar chart

## CSV format
列: cellName, category, ext_vdd!, ext_vddq!, ext_vpp!, vcc!, vdd1!, ... (多电源轨道电流值列; calc 只用 ext_vdd!+ext_vddq!+ext_vpp!*1.64)

## 真实输出 (compare_idd.py stdout, 88 cells)
common=88 only_file1=0 only_file2=0; highlighted(|diff|>10)=26
TOP diffs: d_banklogic(-658.817), c_cmddec(-569.258), ag_analogbankx2l(-356.087), d_wrlatencyctrl(-234.185), m392meg_u(-232.815)...

## Case 合成
- **Case ID**: EDA-Eval-DesignFlow-IddblkCsvDiff-001
- **交付**: compare_idd.py <file1> <file2> <output> [--threshold 10]
- **A (visible)**: iddblk_x4.csv (25 cells, 同构重建), iddblk_x8.csv (25 cells, 同 cellName 不同值)
- **B (hidden)**: iddblk_x4_B.csv (20 cells), iddblk_x8_B.csv (20 cells, 18 |diff|>10)
- **reference**: compare_idd_ref.py + check.py (k=12 断言 a-l)
- **negative**: empty/print_expected/core_deleted (全 FAIL)
- **自验**: REF PASS(B) + 3 neg 全 FAIL + §4.9 trio 全 FAIL + 断言闸门 k_rationale=k_check=12≥8 ✓

## trace_source
jianwang@hfhds201 1791955659176_a63u6 mc=40 hfhds201 local
