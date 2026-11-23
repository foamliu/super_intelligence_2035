# anti-hardcode 普查报告（D 线抽样首版 · 2026-11-24 r1233，r1234 复测修正）

## 范围
`benchmarks/EDA-Eval-DesignFlow/cases/D/` 抽样 4 条（覆盖 11-20~11-23，k=12~15）。

## 汇总
- 总数(抽样): 4
- GAP 数: 0
- PASS 数: 4
- 按 shard: 全 D
- 按年度: 11-20(1) 11-21(1) 11-23(2)

## r1234 复测修正（推翻 r1233 的 2 条 GAP 判定）
1. **NetlistSimSubmitProduce-001**：r1233 误判为 GAP·严重（声称 `reference/` 整体缺失）。
   - 根因：r1233 查了带 `EDA-Eval-DesignFlow-` 前缀的路径 `reference/EDA-Eval-DesignFlow-NetlistSimSubmitProduce-001/`，而实际 ref dir 在 `reference/NetlistSimSubmitProduce-001/`（无前缀，与 cases/D/ 的 JSON 文件名前缀不一致）。
   - 复测：`cd reference/NetlistSimSubmitProduce-001/negative && python3 negative_selftest.py` → GOLD PASS + 12/12 断言 PASS + 3 neg(empty_stub/print_only_stub/core_deleted_stub)全 FAIL。
   - 结论：**PASS**，case 健康，无需修改。
2. **SpfBlCouplingClassifyProduce-001**：r1233 判 GAP·轻微（`negative_selftest.py` 相对路径 bug）。r1234 修复 3 处 bug：
   - ① `NEG_DIR`/`ref` 双重拼接 CASE 名（REF_DIR 已解析到 case dir，却又 `+ "/" + CASE`）→ 改为 `REF_DIR + "/negative"` 与 `REF_DIR + "/solve.py"`。
   - ② `exec(check_code, {"__name__": "__negtest__"})` 传入临时 dict，命名空间未捕获，`__negtest__["check"]` NameError → 改为 `__negtest__ = {"__name__":"__negtest__"}; exec(check_code, __negtest__)`。
   - ③ check() 期望 `workdir/hidden/hidden.spf` 与 `workdir/A/sample.spf`（由 eval harness 暂存），selftest 未暂存 + 未捕 AssertionError → 补 `shutil.copyfile` 暂存 hidden/A + `try/except` 捕 check() 抛出的 AssertionError 视为 FAIL。
   - 复测：REF 15/15 PASS + N1_print_only/N2_hardcode_a/N3_core_deleted 全 FAIL。
   - 结论：**PASS**。

## PASS 案例（anti-hardcode 闸门有效）
- VmMhlAlterStats-001: 6 neg 全 FAIL(含 hardcode_A + core_deleted)，REF PASS。
- CrcAlertMeasFix-001: 5 neg 全 FAIL(含 print_only)。
- NetlistSimSubmitProduce-001: 3 neg 全 FAIL(empty/print_only/core_deleted)，REF 12/12 PASS。
- SpfBlCouplingClassifyProduce-001: 3 neg 全 FAIL(print_only/hardcode_a/core_deleted)，REF 15/15 PASS（r1234 修 selftest 后）。

## 教训
- **路径前缀一致性**：cases/D/ 的 JSON 文件名带 `EDA-Eval-DesignFlow-` 前缀，但部分 reference/ 子目录不带前缀（如 `NetlistSimSubmitProduce-001`）。普查脚本必须以 case JSON 内的实际引用为准，不能假设 ref dir 名 == case 文件名。后续普查脚本应用 `json.load(cases/D/<f>)` 解析出真实 ref 路径，而非字符串拼接前缀。
- **selftest 三类常见 bug 模板**：路径双重拼接 / exec 命名空间未捕获 / 未暂存 hidden 输入 + 未捕异常。后续造题 selftest 模板须含此四项。

## 方法
对每个 case 跑 `negative_selftest.py`（REF 须 PASS，全部 negative 须 FAIL）。任一假提交 PASS ⇒ GAP。
判据：§4.9 (a)空壳 (b)只 print 期望 (c)删核心逻辑 三假全 FAIL。

## 复现命令
```bash
cd benchmarks/EDA-Eval-DesignFlow/reference/<case_id>      # 或 .../negative/
python3 negative_selftest.py
# 注意：部分 ref dir 无 EDA-Eval-DesignFlow- 前缀，以实际目录为准
```

## 后续
- 本轮抽样 4 条全 PASS（mc≥5 池已竭，止损转 anti-hardcode，见 MEMORY r1233/r1234）。
- 下轮继续抽样 ≥20 条，优先 k<12 老题 + 11-17 初始批次。
- 普查脚本须改为从 case JSON 解析真实 ref 路径，避免前缀误判。
- GAP 案例按职责边界处置：D 自己的 case 直接修；A/B/C 的 case 写 discuss/board.md P0 条目。
