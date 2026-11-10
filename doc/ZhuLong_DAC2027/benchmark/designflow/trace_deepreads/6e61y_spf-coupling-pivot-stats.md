# Deepread — 1789547704200_6e61y (spf-coupling-pivot-stats)

## Trace
- user: rongtaoy @ hfeg0plg99 | sid: 1789547704200_6e61y | 268 msgs | match_count 101
- domain claim: schematic_netlist (PEX/SPF 耦合 CSV 后处理 → 透视统计)
- gold produce: `/home/rongtaoy/Documents/python/for_coupling/spf_coupling_excel.py` (638 行, 60+ editor writes)
- final xlsx: `msaq_U_CCR_fBcc_int_0820BK_allM3shielding_0916BK.xlsx` (2.5 MB)

## 用户真实意图
PEX 跑 SPF 提耦合，每片/每个 lot 导出一批 CSV(每 CSV = 一个批次)，CSV 含两段：
- Section 1: BL 耦合数据(表头 `BL0..BLn` + 信号×BL 数值) ← 要保留
- Section 2: net-pair 耦合对明细 ← 要丢弃(遇空行截断)

需要：读同目录所有批次 CSV → 截断 → 校验各批次 BL 表头/信号对齐 → 透视成 信号×批次×BL 三维 → 输出 Excel 四 sheet(data / data_fig / data_fig_12BL / data_fig_func 含 20 统计量)。

## 关键机制(gold)
1. **parse_number**: 兼容 `1,234`(千分位) / `12%`(去%) / `3.5万`(→e4) / 非法→None；绝不抛异常。
2. **截断**: `read_batch_block` 遇完全空行即 `break`，尾部 Section 2 全丢弃。
3. **对齐校验** `_validate_alignment`: 所有批次 BL 表头列名 list 完全相等 + 信号名 list(按顺序)完全相等，否则 ValueError。
4. **parse_bl_range**: `"3,8"` 或 `"BL3,BL8"` → `range(3,9)`；start>end 自动交换。
5. **20 统计量** `_stats_over_bl` 返回 `[min, min_bl_name, mean, max, max_bl_name]`：
   - 全 BL 原值 / 全 BL 绝对值 / 区间内原值 / 区间内绝对值 → 4×5 = 20 个量。
   - None 跳过；全 None → 5 个 null。min/max 取第一个达到极值的 BL 名。
6. **CLI**: `<input_dir> -o out.xlsx -b 1200,1211 -s suffix -y batch1 batch2 --silent`，非交互 `-y` 直接选批次。
7. **输出四 sheet**: data(每批次一块原始布局) / data_fig(每信号一块,行=批次) / data_fig_12BL(BL 区间子集) / data_fig_func(20 统计量)。

## B-grade 合成决策
- **输出格式**: xlsx → JSON 报告(纯标准库, sandbox-portable; check.py 用 json 比对, 无需 openpyxl)。机制(截断/对齐/三维透视/20 统计量/parse_number)全部保留。
- **A 输入**(可见, `assets/CouplingPivotStats-001/inputs_A/`): 3 批次(wafer1-3) × 5 信号(WL0_en/SA_en/PCOL/ISO/VDD_RET) × 8 BL(BL0-7), bl_range `2,5`。
- **B 输入**(隐藏, `reference/.../hidden/inputs_B/`): 4 批次(lotA-D) × 6 信号(DWL/CSEL/PREG/VSSA/VDDA/VREF) × 10 BL(BL0-9), bl_range `3,8`。A/B 信号名+批次名+BL 数+区间全 disjoint → 反硬编码。
- **parse 边界**(隐藏 `inputs_parse/parse1.csv`): 单批次单信号 `PARSE_TEST`, 4 cell = `1,234`/`12%`/`3.5万`/`n/a` → 期望 `1234.0/12.0/35000.0/null`(注意 gold 的 `12%`→12.0 是朴素去符号, 非 0.12 — A-faithful)。
- **负样本**(隐藏 `negative_inputs/`): mismatch_dir(BL 表头不一致) / sig_mismatch_dir(信号集不一致) / empty_dir(空目录) → 全部应非零退出。
- **负桩**(reference/negative/): empty_shell / print_only / core_removed / static_b(硬编码 B 字面量) / wrong_cli → 全部应 FAIL check.py。
- **§4.9 三假提交**: 空 zip / 错名脚本 zip / 非 zip → 全部应被拒绝。
- **check.py 14 条件 a-n**: zip+禁 import / py_compile / B 4 节存在 / data 逐值 / data_fig / data_fig_12bl / data_fig_func(20 量) / 截断无 Section 2 / parse 边界 / 对齐拒绝 / 空目录拒绝 / 反硬码 A / 无 B 硬码字面量 / 3-seed 确定性。k_rationale==k_check==14≥8。

## 自验证结果
- ref(coupling_pivot_ref.py 独立实现) 在 A+B 上与 gen_case.py 期望逐值一致(两套独立实现互验)。
- check.py(ref_submit.zip): ALL PASS (14/14)。
- negative_selftest: ref PASS + 5 桩全 FAIL + 3 假提交全 REJECTED。
- 确定性: B 三重跑 sha256 一致。

## 案件
- task_id: EDA-Eval-DesignFlow-CouplingPivotStats-001
- shard D 第 #504 case, D.jsonl 313→314 行。
- 与已有 D case 机制不重复: 既有 FsdbPowerWindow/IVCurve/EyeAperture(waveform FSDB) / NetlistStructDiff/SpiceMeasInserter(netlist 文本) / SchemExplodeLabel(原理图打散打标)。本 case = SPF 耦合 CSV 批次聚合透视统计, 独立机制。
