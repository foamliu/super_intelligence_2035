# 深读笔记 — r4p2e (MC RON mismatch extraction)

## Trace 元数据
- session: `1793178408819_r4p2e.messages.json`
- user: clarawu @ hfeg0pkn001 (mc=56, 277 msgs, 771KB)
- keywords (raw.tsv): hspice:96; netlist:...; spice_count=96
- 扫描时间 2026-10-28；本轮 scp 到 .75 workdir 验读

## 真实流（逐轮）
- **U0 (intent, A-档候选)**: `从 .../sim_MC/Ron_linMC#4.md0 中得到 RON_PU_mismatch，其定义为6倍 rpu_50 的标准差 std 除以 230，用百分数表示；还有 RON_PD_mismatch，其定义为6倍 rpd_50 的标准差 std 除以 230，用百分数表示`
  - 即：`mismatch = 6 × std(measure_col) / 230 × 100%`，230 = 标称 Ron（spec 常量，非样本均值）
- agent read .md0 → 列 `mc_index rpu_50 rpd_50 rpu_lin50 rpd_lin50 temper alter#`
- 写 compute_ron_mismatch.py：**第一版未检查 mc_index 是否为数字** → 把末尾 4 行系统汇总（avg/std/min/max）当数据行 → 504 样本，rpu_50 std=10.2883（错！），mismatch=26.84%
- **U16 (用户给根因 → A-档不可用)**: `不对，应该只有500个样本，最后四行中，avg是系统算出的均值，std是标准差，min和max是最大最小值`
  - → 违反 A-档选轮规则（用户指出根因），只能 B-档 synthesized
- agent 修：要求 `int(parts[0])` 数字 mc_index → 500 样本，std=1.23824，mismatch=3.2302%
- **U24 (用户给方法)**: `你直接用最后四行里面系统自己得到的std计算就可以了`
  - → 直接读 `std` 汇总行：rpu std=1.2397, rpd std=2.1902 → mismatch=3.234%/5.714%
  - 关键：两种正确法 (a) 读 std 汇总行  (b) 从 500 样本算 std（排除汇总行）——两者结果一致（系统 std=1.2397 vs 样本 std(n-1)=1.23824）
- **U26 (扩展)**: 读 5 个 .md0（Ron_linMC.md0/#1/#2/#3/#4）→ 每个 mismatch → 表格
- agent 写 extract_ron_mismatch_all.py → 5 行结果表
- **U32**: 把脚本放到 stimulus_file_global_corner/ 目录 → 策略拦截（writableRoots 只 /home/clarawu）→ 改 portable（os.path.dirname(__file__)+sim_MC）+ 符号链接验证
- **U46**: 输出表格需 .csv 格式

## 核心 skill（B-档 synthesized 保留）
**FineSim Monte Carlo .md0 → 6σ/std RON mismatch 提取器**
1. 跑 FineSim MC（.dc/.tran sweep monte=N）→ 产 .md0
2. 解析 .md0：列 `mc_index <measures...> temper alter#`，N 数据行 + 4 汇总行（avg/std/min/max，mc_index 列为字符串标签）
3. **核心陷阱**：naive parser 不检查 mc_index 是否数字 → 把 `std` 汇总行的 measure 列值（=std 本身，小数）当数据样本 → 巨大离群 → std 爆炸
4. 正确：排除汇总行（require numeric mc_index），mismatch = 6×std/divisor×100%，divisor 从 spec.json 读（=标称 Ron，非样本均值）
5. 输出 CSV（每文件一行：file, samples, std_pu, std_pd, mismatch_pu%, mismatch_pd%）

## .75 L2 可行性实测（本轮 .75 eda_flow 验证）
- **FineSim MC 跑通**：`finesim -spice deck.sp`，`.dc vin X X 1 sweep monte=N` 语法 OK，N=20 跑 ~3s
- **.md0 格式 = trace 原样**：
  ```
  $DATA1 SOURCE='FineSimPro' ...
         mc_index            rpu            rpd         temper         alter#
      1     1.9971e+05     1.9971e+05     2.5000e+01     1.0000e+00
      ...
      20    2.0623e+05     2.0623e+05     2.5000e+01     1.0000e+00
              avg     2.0033e+05     2.0033e+05     2.5000e+01     1.0000e+00
              std     2.9356e+03     2.9356e+03     2.5000e+01     1.0000e+00
              min     1.9526e+05     1.9526e+05     2.5000e+01     1.0000e+00
              max     2.0623e+05     2.0623e+05     2.5000e+01     1.0000e+00
  ```
- **陷阱bite实测**（fsmc3.sp, NMOS pass transistor W=40u L=180n, vg=vdd, il=1u, .measure rpu param='v(out)/i(il)'）：
  - rpu 数据 ~2e5，`std` 汇总行 rpu=2936（小 70×）
  - naive 含 std 行 → std 从 2936 爆到 ~41000（14× 膨胀），mismatch 从 8.8% 爆到 ~123%
  - 与 trace 一致（trace std 1.24→10.3, 8× 膨胀）✓
- **HSPICE 不可用**：HSPICE .mc 语法 `.mc` 被忽略（PrimeSim HSPICE V-2023.12-SP1-1）；`sweep monte=N` 跑通但 .ms0 **无汇总行**（stats 在 .ava.report）→ 陷阱不复现。**必须用 FineSim -spice**
- **DUT**：NMOS pass transistor Ron 表征（vgs=vdd on, il 小电流, .measure rpu=v(out)/i(il)）；标称 Ron~2e5Ω（divisor 在 spec.json，候选从 spec 读非硬编）
- **License**：FineSim OK（`Checked in primesim(2) successfully`，本轮 15:10）

## distinct vs 已有 B characterization case
- GmidLut/NmosAgeChar/CTLEtranChar/VihTripTune/ButterflyCurve/DffSetupHoldChar/ThoxVthExtract/OtaAutoTune/TxRonSize/PVTvarSpecJudge/RcurrDirClassify/SizingSensDiag/Tr0JitterRemeas —— **无一为 Monte Carlo mismatch 提取**
- TxRonSize = Ron sizing（确定性，非 MC）；PVTvarSpecJudge = PVT variation spec 合规（.alter 非 MC，无 6σ/std）
- 本条 = **Monte Carlo .md0 parse + 6σ/std mismatch + 汇总行陷阱**，shard B 首个「MC mismatch 提取器」case，distinct ✓

## case 设计（下轮合成）EDA-Eval-DesignFlow-McRonMismatch-001
- domain: characterization, B档 synthesized, **L2 真跑 FineSim -spice**
- **A**（SUT 可见）：`ron_mc_A.sp`（NMOS pass transistor, sweep monte=N_A）+ `spec_A.json`（measure_cols=[rpu_A, rpd_A], divisor=D_A, sigma=6）
- **B**（隐藏，judge-only）：`ron_mc_B.sp`（PMOS pass transistor 或不同 sizing, sweep monte=N_B 不同）+ `spec_B.json`（measure_cols=[rpu_B, rpd_B], divisor=D_B 不同）
  - 跨输入：拓扑(NMOS/PMOS)、measure 名、N、divisor 全不同 → 防 hardcode
- 候选 mc_ron_mismatch_ref.py（CLI <deck.sp> <spec.json> <out_dir>：subprocess finesim -spice → 解析 .md0 [排除汇总行, require numeric mc_index] → std [读 std 行 或 样本 std] → mismatch=6×std/divisor×100% → CSV + report.json）
- **check.py 14 条 a-n 设计**：
  - (a) zip+mc_ron_mismatch.py (b) py_compile (c) subprocess 真跑 finesim（log 含 FineSim + Successfully Completed，反 fake_no_rerun）(d) .md0 解析（找到 .md0 文件）(e) **汇总行排除**：samples==N_B（非 N_B+4，反 naive 含汇总行）(f) mismatch_pu 正确 = 6×std_pu/D_B±5%（反 naive std 爆炸）(g) mismatch_pd 正确 (h) divisor 从 spec_B 读非硬编 A 的 (i) CSV 表头+数据行 (j) report.json schema (k) std 用 std 汇总行 或 样本 std（两者容差内）(l) 跨输入守卫 B-token 出现 + A-token 不泄 (m) 重跑 B 确定性（fixed seed）(n) A 重跑 mismatch 在 A 真值 ±10%
- 6 negatives: naive_empty, naive_print_expected, naive_no_rerun(不跑 finesim 伪造 .md0), naive_hardcode_a(硬编 A 值), naive_include_summary(含汇总行→std 爆炸), naive_wrong_divisor(用样本均值非 spec divisor)
- §4.9 三假 = naive_empty / naive_print_expected / naive_no_rerun
- **test_rationale**: `14 条断言：①zip 含 mc_ron_mismatch.py ②py_compile 通过 ③subprocess 真跑 FineSim 且 Successfully Completed ④解析产 .md0 文件 ⑤样本数==N_B（排除 avg/std/min/max 汇总行）⑥mismatch_pu==6×std_pu/D_B±5% ⑦mismatch_pd==6×std_pd/D_B±5% ⑧divisor 从 spec_B.json 读非硬编 ⑨CSV 表头+每文件一行 ⑩report.json schema 齐全 ⑪std 取值合法（汇总行或样本 std 容差内）⑫跨输入 B-token 出现且 A-token 不泄 ⑬fixed seed 重跑 B 一致 ⑭重跑 A mismatch 在真值±10%`

## DEBT 项（下轮第一件事）
1. 调 DUT：NMOS pass transistor Ron 标定（目标 clean 数值，std 适中，mismatch 落合理范围 5-15%）；A/B 两版（NMOS/PMOS 或不同 W/Vdd，N_A≠N_B，divisor 不同）
2. 合成 mc_ron_mismatch_ref.py + check.py 14 条 + 6 negatives + negative_selftest
3. .75 端到端验证（ref PASS 14/14 + 6 neg 全 FAIL + §4.9 三假 FAIL）
4. reference_submit.zip + 追加 EDA-Eval-DesignFlow_B.jsonl + mark --status case
5. 清 DEBT:1

## 教训
- (1) HSPICE .mc 在 PrimeSim HSPICE V-2023.12-SP1-1 被忽略；用 `sweep monte=N` 但 .ms0 无汇总行 → MC mismatch 陷阱必须 FineSim
- (2) FineSim `.dc X X 1 sweep monte=N` + `.measure ... param='expr'` 产 .md0 含 avg/std/min/max 汇总行（与 trace 原样）
- (3) 陷阱bite关键：measure 值大（Ron~2e5），`std` 汇总行 measure 列=std 本身（小数）→ naive 含入即离群爆炸
- (4) A-档不可用（U16 用户给根因「最后四行是汇总」+ U24 给方法「用系统 std」）
- (5) 候选 scouting 本轮 parked 17 条 reject（见 ledger_B）：4khqb/jesvi=dup 7ycbz, szdav=dup SAoptPwrDly, d1cg3=dup FineSimDcConvFix, gsmj2=explain, l36g5=AMS-ADE-GUI, 2y77m=dup NetlistTranDeck, opm9y=schematic-GUI, j8f3i=GUI-script, toak9=explain, f10db/vo4gm/vdeyi/i5slk/0b3ir/ioa1s/4oo3i/qw7ae/z72bi=旧轮 reject 补 park
