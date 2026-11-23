# anti-hardcode 普查报告（D 线抽样首版 · 2026-11-24 r1233）

## 范围
`benchmarks/EDA-Eval-DesignFlow/cases/D/` 抽样 4 条（覆盖 11-20~11-23，k=12~15）。

## 汇总
- 总数(抽样): 4
- GAP 数: 2
- PASS 数: 2
- 按 shard: 全 D
- 按年度: 11-20(1) 11-21(1) 11-23(2)

## Top 风险
1. **NetlistSimSubmitProduce-001 (GAP·严重)**: `reference/` 目录整体缺失 → case 无法评测。P0 补 reference 或下线。
2. **SpfBlCouplingClassifyProduce-001 (GAP·轻微)**: 三假文件齐全(符合§4.9)，但 `negative_selftest.py` 相对路径 bug → 自测跑不起来。P1 修 selftest。

## PASS 案例（anti-hardcode 闸门有效）
- VmMhlAlterStats-001: 6 neg 全 FAIL(含 hardcode_A + core_deleted)，REF PASS。
- CrcAlertMeasFix-001: 5 neg 全 FAIL(含 print_only)。

## 方法
对每个 case 跑 `negative_selftest.py`（REF 须 PASS，全部 negative 须 FAIL）。任一假提交 PASS ⇒ GAP。
判据：§4.9 (a)空壳 (b)只 print 期望 (c)删核心逻辑 三假全 FAIL。

## 复现命令
```bash
cd benchmarks/EDA-Eval-DesignFlow/reference/<case_id>      # 或 .../negative/
python3 negative_selftest.py
```

## 后续
- 本轮抽样 4 条（mc≥5 池已竭，止损转 anti-hardcode，见 MEMORY r1233）。
- 下轮继续抽样 ≥20 条，优先 k<12 老题 + 11-17 初始批次。
- GAP 案例按职责边界处置：D 自己的 case 直接修；A/B/C 的 case 写 discuss/board.md P0 条目。
