# Deepread — a63u6 · jianwang@hfeg0pkn001 · mc=23 · analog_context

## Trace
- session: 1791955659176_a63u6 (40 msgs, dir-based .messages.json on .75 local /home/jianwang)
- user: jianwang, host: hfeg0pkn001 (10.129.32.75 = .75 itself, fast local peek)
- keywords: analog:44; drc:19; netlist:18; cmos:1 → d=82 c=19 a=0, clean D-dominant (analog_context)

## User turns (逐字, A-faithful)
- **Turn #0**: 「在linux操作界面内，我有一些csv格式的文件，我希望你可以把这两个格式的csv文件做差，并将差异比较大的项高亮出来」
- **Turn #1**: 「/proj/drgqa/V0/simdir/finesim/drgqaF/MatrixRun_Netlist_IDD_20260902pm_RevC_JEDEC_OC/idd0RevCx4-6400.x4.TT1.166v98c.current/iddblk.csv 和 /proj/drgqa/V0/simdir/finesim/drgqaF/MatrixRun_Netlist_IDD_20260902pm_RevC_JEDEC_OC/idd2n-6400.x8.TT1.166v98c.current/iddblk.csv，我希望你按cellname匹配后计算插值。计算的数据通过表格中的ext_vdd+ext_vddq+ext_vpp*1.64得到」
- **Turn #2**: 「可以帮我把上面的数据中，绝对差值大于10的摘出来，做一张对比的柱状图吗」

## Real task (agent 实测产物)
- agent (jianwang's cline) read 两个 iddblk.csv（/proj 权限对 jianwang 可读，对 e0031982/.75 不可读 → 资产不可达，须合成）
- 列结构：`cellName, category, ext_vdd!, ext_vddq!, ext_vpp!, vcc!, vdd1!, ...`（多列电源轨道，`!` 为 Cadence global-net 后缀）
- 公式（用户逐字指定）：`calc = ext_vdd! + ext_vddq! + ext_vpp! * 1.64`
- 匹配结果：88 common cellName, 0 only_file1, 0 only_file2
- agent 产出 compare_idd.py：按 cellName 匹配 → 计算 calc → diff(f2-f1) + pct → big_diff_flag → 输出 idd_compare_highlight.csv + .html
- 实测 top diff: d_banklogic(banklogic) 3773.223→3114.406 = -658.817(-17.5%); c_cmddec(cmdpath) 1262.344→693.086=-569.258(-45.1%); ag_analogbankx2l(dc) 359.187→3.100=-356.087(-99.1%); d_wrlatencyctrl(clkpath) 329.238→95.054=-234.185(-71.1%); m392meg_u(array) 591.110→358.296...
- Turn #2 follow-up: plot_idd_compare.py 过滤 |diff|>10 → 26 个 cell，matplotlib 双联柱状图 PNG（非自包含 EDA 产物，drop 为 non-core）
- 选 Turn #0+#1 作核心 produce-task（CSV diff + 公式 + 高亮）；Turn #2 柱状图 drop（matplotlib 不可独立 ≥8 断言且非核心）

## Domain & dup-check
- domain = analog_context（FineSim IDD 电流测量 .csv 后处理，power-rail 拆解）
- 现有 IDD/analog 类 case: IddLeakRank(iddtree tsv 排序) / IddMeasPostProcess(.meas 结果后处理) / MqaMd0PvtAggregate(.md0 PVT 聚合) / EccTopCircuitCompare(顶层电路对比) / WvFsdbBatchOpenCmd(FSDB 批开) / PvtPwrWinAvg(PVT 波形窗口平均功耗) — 本 case = iddblk.csv 双文件按 cellName 匹配 + 公式 calc=ext_vdd!+ext_vddq!+ext_vpp!*1.64 + diff/pct + big_diff_flag + 阈值过滤输出, 机制不同 ✓

## Case design (B-grade synthesized L1, pure stdlib)
- SUT: idd_blk_cmp.py — argparse(file1, file2, --threshold, --out), csv.DictReader by column name, select ext_vdd!/ext_vddq!/ext_vpp!, calc = ext_vdd!+ext_vddq!+ext_vpp!*1.64, match by cellName, diff=f2-f1, pct=diff/f1*100, flag |diff|>threshold, output CSV 7-col sorted by |diff| desc, only-in-one-file excluded
- A(可见): iddblk_A1.csv + iddblk_A2.csv (~12 common + 2 asymmetric, cell names: xa_top/xb_bank/xc_cmd/..., ext_vdd!/ext_vddq!/ext_vpp! + vcc!/vdd1! extra rails)
- B(hidden): iddblk_B1.csv + iddblk_B2.csv (~20 common + 3 only-B1 + 2 only-B2, disjoint cell names yd_*/ye_*)
- C(嵌入 check.py): iddblk_C1.csv + iddblk_C2.csv (~10 common, disjoint zf_*/zg_*, **列顺序打乱** + 额外列 → 反硬编码 by-name parse)
- 反硬编码: B/C cell 名 + 数值全不相交; C 列顺序与 A/B 不同; 阈值 --threshold CLI arg (SUT 不可硬编码阈值); 公式 1.64 系数固定(用户逐字指定，非反硬编码点) 但 B/C 数值不同 → SUT 若硬编码 A 的 calc 则 B/C 全错
- check.py 16 条件 a-p: 6 static + 7 dynamic(mock_B) + 2 anti-hardcode(mock_C) + 1 threshold-param + 1 negative
