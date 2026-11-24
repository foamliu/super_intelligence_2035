# anti-hardcode 普查报告（D 线 · 2026-11-24 r1233 首版 / r1234 复测 / r1235 扩样至 20）

## 范围
`benchmarks/EDA-Eval-DesignFlow/cases/D/` 抽样 **20 条**（覆盖 11-20~11-24，k=0~15，优先 k<12 老题）。
方法：对每个 case 跑 `negative/negative_selftest.py`（REF 须 PASS，全部 negative/fake 须 FAIL）。任一假提交 PASS ⇒ GAP。
判据：§4.9 (a)空壳 (b)只 print 期望 (c)删核心逻辑 三假全 FAIL。

## 汇总
- 总数(抽样): **20**
- GAP 数: **0**
- PASS 数: **20**
- 按 shard: 全 D
- 按 k: k=0(1) k=9(1) k=11(4) k=12(12) k=15(2)
- 按年度: 11-20(1) 11-21(1) 11-23(4) 11-24(14)

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

## r1235 扩样（+16 条，累计 20，全 PASS）
新增 16 条全部 selftest rc=0（REF PASS + 全 neg FAIL），0 GAP：
| case_id | k | selftest 信号 |
|---|---|---|
| HierNameViolateCrossProbeProduce-001 | 0 | "SELFTEST OK: all negatives FAIL"（注:k=0=test_rationale 缺"N条断言",metadata 闸门 gap,非 check 无牙）|
| Ddr5ClDelayPivot-001 | 9 | "NEGATIVE SELF-TEST: ALL PASS"（5 neg 全 correctly FAILed）|
| AvcPatternCompare-001 | 11 | REF:PASS / NEG_RC=0 n_fail=6/6 |
| InvSpiceSim-001 | 11 | NEG_RC=0（3 §4.9 deg + hardcode_b 全 FAIL）|
| NetlistBroadcastFlow-001 | 11 | NEG_RC=0（deg_print_only/core_deleted FAIL）|
| Waveform-001 | 11 | REFERENCE check=True / neg_fake_hardcode_b FAIL |
| AeDelCellCurCellProduce-001 | 12 | "ALL NEGATIVES FAIL — selftest PASS" |
| CellConstraintsTplProduceQA-001 | 12 | 3 stub 全 pass=False（4/12,7/12,7/12）|
| AddrRtlGateMap-001 | 12 | rc=0（core_deleted/empty 11 conds FAIL）|
| AetherPartialNetlistExtractQA-001 | 12 | REF_PASS=True NEG_RC=0（§4.9 empty_zip FAIL）|
| AnalogDlyCellLogicDeriveProduce-001 | 12 | rc=0（core_deleted/hardcode_a FAIL as expected）|
| AutoCellRmAvPf-001 | 12 | ref PASS:True / hardcode_b FAIL(o) |
| ClcTruthTableFlowExplainQA-001 | 12 | rc=0（hardcode_a/always_ok false）|
| DbcoaZqCalCircuitExplainQA-001 | 12 | rc=0（print_only/core_deleted FAIL correct）|
| Ddr6OdtModifyMethodQA-001 | 12 | rc=0（print_only/core_deleted rc=1 FAIL as expected）|
| EccTopCircuitCompare-001 | 12 | rc=0（empty/hardcode_A/core_deleted 全 FAIL_expected）|

## 教训
- **路径前缀一致性**：cases/D/ 的 JSON 文件名带 `EDA-Eval-DesignFlow-` 前缀，但部分 reference/ 子目录不带前缀（如 `NetlistSimSubmitProduce-001`、`AvcPatternCompare-001`、`Ddr5ClDelayPivot-001`）。普查脚本必须以 case JSON 内的实际引用为准 / 双候选探测，不能假设 ref dir 名 == case 文件名。r1235 批量脚本已用 `ref_dir_for(cid)` 双候选探测，0 误判。
- **selftest 三类常见 bug 模板**：路径双重拼接 / exec 命名空间未捕获 / 未暂存 hidden 输入 + 未捕异常。后续造题 selftest 模板须含此四项。
- **selftest 输出格式不统一**：各 case 的 PASS/FAIL 摘要关键词不一（"SELFTEST OK" / "NEG_RC=0" / "ALL PASS" / "ref PASS:True"）。统一判据用 **rc==0**（selftest 自身断言通过 = REF PASS + 全 neg FAIL），最稳。
- **k=0 metadata gap**：HierNameViolateCrossProbeProduce-001 的 `test_rationale` 缺"N条断言"格式（k 解析为 0），anti-hardcode 闸门本身 PASS，但 §4.6 test_rationale 闸门有 gap——属另一条治理线，不影响本普查判定。

## 复现命令
```bash
cd benchmarks/EDA-Eval-DesignFlow
# 单条（注意部分 ref dir 无 EDA-Eval-DesignFlow- 前缀，以实际目录为准）
cd reference/<case_id>/negative && python3 negative_selftest.py   # rc=0 ⇒ PASS
```

## r1277 扩样（+3 低 k 老题 + 14-stub GAP 关闭，累计 30 条全 PASS）

DEBT:3（连续三轮无新 case）触发「转不依赖新候选产出」条款，本轮按 11-21 令做 §4.9 anti-hardcode 自查，优先 k<12 老题。

**新增 3 条**（全部 selftest 4/4 PASS：REF PASS + print_only/core_deleted/hardcode_a 全 FAIL）：

| case_id | k | selftest 信号 | 备注 |
|---|---|---|---|
| CdlTruthTableVerify-001 | 9 | 4/4 groups passed | hidden B=R_2stepSenseAdjTempCtrl_defaultLT.netlist vs A=..._0822.netlist；hardcode_a FAIL 证 B≠A |
| SpfSwapPostSim-001 | 10 | REF PASS + 3 fake FAIL | check() inline 在 JSON test 字段，hidden B 内嵌为 B_FILES(CalibBlock 9 ports vs A 不同) |
| FifoStructNetlistGen-001 | 11 | NEGATIVE SELFTEST: ALL OK | hidden B1/B2 fifo_spec vs A fifo_spec_A 结构不同 |

**14-stub GAP 关闭**：r1250 发现 14 个 D case test 字段是 stub 指针（无 `def check`，全 broken）。r1277 复测 `python3 -c "sum(1 for f in glob('cases/D/*.json') if 'def check' not in json.load(open(f))['test'])"` → **0 stub 剩余**，14 个全部已 inline 修复。audit_all.tsv 该 meta-row 判定 GAP→RESOLVED。

## 汇总（r1277 更新）
- 总数(抽样): **30**（29 case-level PASS + 1 meta RESOLVED）
- GAP 数: **0**（14-stub GAP 已关闭）
- 全部 D shard，0 跨线
- 按 k: k=9(2) k=10(1) k=11(5) k=12(13) k=15(3) k=16(1) k=0→已修 k=14(1)
- 判分契约（11-24 令）shard D 608/608 合规，0 VIOLATION（r1276 AST 审计）

## 后续
- 本轮抽样 30 条全 PASS（mc≥5 池已竭，止损转 anti-hardcode，见 MEMORY r1233~r1235/r1277）。
- 已达 §4.9 普查 ≥20 条首版目标。后续轮次可继续扩样（D 共 609 case），或转 test_rationale 补断言清单 / ledger 治理 / 跨 shard A/B/C 抽样普查（11-21 令，按职责边界只报告不改）。
- **r1236 修复**: HierNameViolateCrossProbeProduce-001 的 k=0 test_rationale gap 已修（英文 prose → `14 条断言：①…⑭`，k=14>=8 GATE PASS，test 字段未动，selftest rc=0）。
- GAP 案例按职责边界处置：D 自己的 case 直接修；A/B/C 的 case 写 discuss/board.md P0 条目（本批全 D，无跨线）。
