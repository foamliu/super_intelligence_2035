# deepread: 1793171759141_p33gv (scarle @ hfhds206, mc=15, analog_context)

## trace 概况
- 21 msgs / 14 user / 7 assistant，207KB（snapshot daily-new.2026-11-08_2230，live .cline 已轮转）
- 3 个真实 user 文本轮（其余为 tool_result）：
  - msg[0] `<user_input mode="act">漏电功耗</user_input>` — 一句主题，无明确交付规格
  - (中间无更多 user 文本轮)
  - 全程 assistant 驱动：list_allowed_files → read_files(pvt.mt0.csv / bigblock.csv / find_spicesim_idd.py) → run_approved_command(find_spicesim_idd.py) → msg[20] 汇报文本报告
- **判为 borderline-analysis**：用户只给主题「漏电功耗」，assistant 产出文本汇报（非脚本/文件交付）。但机制真实 + 资产可达 → B-grade synthesized（把"汇报"重构成"产 CLI"）。

## 真实资产（均可达 /home/scarle/）
- `/home/scarle/pvt.mt0.csv` (758KB, 94 行)：FineSimPro .mt0
  - line1: `$DATA1 SOURCE='FineSimPro' VERSION='T-2022.06-SP1' PARAM_COUNT=0`
  - line2: `.TITLE '...hspice option...'`
  - line3: 列名表 `out000f..out127f, out000r..out127r, vrstrgresref_out000f..vrstrgresref_out127r, temper, alter#`（数百列，末两列 temper/alter#）
  - line4-94: 91 行 PVT corner 数据，末列 alter# 从 87 递增到 177，temper ≈ 130
- `/home/scarle/Desktop/bigblock.csv` (2.4KB)：`cellName,category`，Leakage 类 2 个（IO_ZqTop, DqRoC_V2），其余 BiasCurrent/CAIB/CSIB/CKIB/CmdDec/RowCtrl/... 共 ~95 行
- `/home/scarle/MY_desktop/bigblock.csv` (4.6KB)：另一版 cell-list，含 `***** NOT Sum *****` 分隔行 + bbus_new 等类，无 Leakage
- `/home/scarle/Desktop/PGM/find_spicesim_idd.py` (559B)：trivial os.walk 找 "spicesim_idd" 文件名（非金标准机制，仅辅助）

## 金标准机制（assistant msg[20] 汇报内容）
1. 从 bigblock.csv 筛 `category == "Leakage"` 的 cellName → IO_ZqTop, DqRoC_V2（漏电功耗监控单元）
2. 读 pvt.mt0.csv 识别 PVT 仿真数据（FineSimPro .mt0 格式，temper/alter# 列即 PVT corner 标识）
3. 汇报 Leakage cell 清单 + PVT 数据来源

## B-grade synthesized 设计 → EDA-Eval-DesignFlow-LeakageCellPvtAudit-001
- **SUT** `leakage_pwr_audit.py`：纯 stdlib(argparse/csv/json/os/re/sys) `<mt0> <cell_list> <outdir>`
  - parse .mt0: $DATA1→SOURCE/VERSION + header(含temper)→列名 + 定位 temper/alter# 索引 + 数据行→pvt_corners[{alter,temper}] + signal_columns(除temper/alter#)
  - parse cell-list: category 分组计数 + Leakage cell 收集
  - emit audit_report.json(10 键) + category_summary.csv(category,cell_count)
- **A**（SUT 见，assets/）：cell_list_A(_A 前缀, 12 cell/5 cat/Leakage 3) + pvt_A.mt0(6 corner, alter 200-205, temper 110/125) + example_report_A
- **B**（hidden, check.py 跑）：cell_list_B(_B 前缀, 17 cell/6 cat/Leakage 4, 多 Repeater) + pvt_B.mt0(8 corner, alter 300-307, temper 105/120/135, 5 signal 列) + hidden_manifest
- **C**（嵌入 check.py 字面量, 反硬编码）：_C 前缀, 7 cell/3 cat(Leakage 2, Driver 3)/ + pvt_C.mt0(5 corner, alter 400-404, temper 115)
- A/B/C：cell 前缀 + alter 范围 + temper 范围 + category 组合全不相交
- **check.py 13 条件 a-m**：a(zip+禁import+B/C字面量泄漏) b(py_compile) c(跑B退0+两产出) d(JSON必需键) e(tool_source=FineSimPro) f(total_corners=8+pvt_corners长8) g(每corner alter/temper对B) h(categories对B oracle) i(leakage_cells对B 4个) j(total_cells=17) k(category_summary表头+行) l(反硬编码C≠B+C Leakage=2+tool_source仍FineSimPro) m(3-seed sha256一致)
- 自验：ref PASS 13/13 + 4 neg(empty/print/hardcode_a/core_deleted)全FAIL(条件 c/c/f/h, n_distinct=4) + §4.9三假覆盖 + 3-seed 一致 + jsonl round-trip PASS
- **difficulty=L1**（诚实标：SUT 纯 stdlib CSV/.mt0 文本解析无 EDA 工具运行时，与 #520/#519/#518 一致；资产可达但金标准机制是文本汇报非真跑 FineSimPro）

## 维度正交（vs 既有 D 域 case）
- vs ClampLeakPwrAnalyze-001(#429)：彼=clamp 漏电功耗数值分析+L2；本=cell-list 分类审计+.mt0 PVT corner 提取+L1，机制不同
- vs CellLeakageIvPlot-001：彼=IV 曲线绘图；本=无 IV/无绘图，纯分类计数+corner 提取
- vs CioLeakageExtract-001：彼=CIO 漏电提取；本=DRAM block cell-list Leakage 类筛选，对象不同
- 非 dup ✓
