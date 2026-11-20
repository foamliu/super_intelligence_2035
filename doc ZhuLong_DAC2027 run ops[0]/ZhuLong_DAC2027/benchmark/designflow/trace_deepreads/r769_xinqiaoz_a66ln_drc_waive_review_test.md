# Deepread — r769 / xinqiaoz / a66ln — DrcValueCheck per-rule waive review+test

- **session**: `1788923302434_a66ln` (xinqiaoz / hfeg0pkn002 / 10.129.2.12, mc=71, 16 msgs / 183 KB)
- **domain**: physical_verify (DRC value check / calibre / pdk qa)
- **case**: `EDA-Eval-DesignFlow-DrcWaiveReviewTest-001` (track A-faithful, tier L1)

## 用户真实意图（U#0 原话，逐字）

> 我新增了一个 feature，代码修改可以通过 git status 查看。feature 文档在 /home/xinqiaoz/PDK_QA/pdkQaSystem/.tmp/0909_1102.md。你需要做下面的事情：
> 1. 看一下代码的修改是否与 feature 文档一致，review 代码，如果有不合理的地方，请指出
> 2. 构建真实的测试用例来测试 feature 是否真实生效。
> 3. 跑我们的 tests，确认这个 feature 不影响已有的代码，尤其是 drcValue。

三件交付：review 报告、真实测试用例、回归测试结果。这是真实 produce-task（不是 Q&A、不是 doc-search），有明确可判分的交付物。

## trace 摘要

- feature = DrcValueCheck 新增 per-rule waive：config.ini 加 `[DRC_VALUE_WAIVE]` section，`waive_<检查类型>={'ruleId1',...}`，用 `ast.literal_eval` 解析，ruleId 大小写不敏感（内部统一转大写），在 checkDerivedLayerIndirectVariable 之后、计数/报告之前 applyWaiveConfig 移除豁免项，记 `waivedItems`，报告末尾输出 waived 段。
- 真实 diff（92 行新增）：`loadWaiveConfig` / `isWaived` / `_filterWaived` / `applyWaiveConfig` + 在 check() 主流程调用 + 报告段。真实 diff 是**干净**实现（用 ast.literal_eval、ruleId upper、waiveConfig 在 __init__ 初始化）。
- assistant：读 feature doc → git diff → DrcValueCheck.py → rules/code-modification.md → testing-sop.md → tests/ 目录结构，逐条 review，写测试，跑 tests。

## 资产忠实度

- `feature_doc.md`：从 trace tool_result #2 抽取的 0909_1102.md **逐字原文**（80 行，含 config 格式 / 12 种检查类型表 / 行为 / 报告 / 测试要点）。
- `diff_A.patch`：基于真实 diff 结构，**植入 2 个 review 靶点**（让 review 有牙）：
  1. `ruleIdSet = eval(value)`（真实是 ast.literal_eval）→ 安全/spec 偏离（spec 第 17 行明确要求 ast.literal_eval）。
  2. `loadWaiveConfig` 方法体开头**缺 `self.waiveConfig = {}` 重置**（真实有）→ 幂等性/残留状态。
  - diff_A 顶层 `import ast` 仍在（保留真实结构），但解析用 eval，制造「import 了却没用」的 review 点。
- `drc_value_waiver.py`（A 模块）：自包含重构真实 waive 逻辑，外部依赖（common.Checker / IMCP.log / IniFileReader）用 stdlib stub 替换（configparser）。A 模块**与 diff_A 一致**（eval + 无重置），但大小写不敏感 + section 名正确 → **行为测试在 A 上 PASS**（eval 对合法 set 字面量能解析；单次调用无残留问题）。
- `config.ini`（A）：真实风格的 waive 配置（waive_unmatchedDrc={'bord_isc_s_02_b'} 等）。
- `regression/test_existing.py`：3 个既有行为 regression（init 属性 / 无 config isWaived=False / 无 config applyWaive 是 no-op），waive 特性不应破坏。

## 隐藏 B（杀硬编码 + 逮 bug 类）

- `drc_value_waiver_B.py`：植入 2 个**行为性 bug**（与 A 的 2 个 review 点完全不同）：
  - B1：`getSectionConfigV1("DRC_VALUE_WAIVE_S")`（多了一个 _S）→ config 永远加载不到 → waiveConfig={}。
  - B2：加载时 `set(r.strip() for r in ruleIdSet)` **缺 `.upper()`** → 大小写不敏感匹配对 mixed-case config 失效。
- `config_B.ini`：全异 ruleID（m3a_s_04_01_c / AA_Size_07 / X2_PCH_05 / OLD_RULE_99）+ 多一个 waive_skipList。
- `diff_B.patch`：B 的 diff（用 ast.literal_eval + 有重置，但 section 名错 + 缺 upper）。
- **判分逻辑**：SUT 的 test_waive.py 是 spec-faithful 测试 → 在 A 上 PASS（run_results.txt 证明）、在 B 上 ≥2 FAIL（逮住 B1+B2）。退化提交（空/print-only/删核心）→ (f)(g) 不满足 → FAIL。

## check.py 12 条独立断言 a-l

① 三件齐全 ② py_compile ③ ≥4 test 函数 ④ 导入 waiver ⑤ 含大小写不敏感测试 ⑥ B 上 ≥1 FAIL ⑦ B 上 ≥2 FAIL ⑧ regression 在 B 上 PASS ⑨ run_results.txt(A) ≥4 passed 0 failed ⑩ review 提 eval+ast.literal_eval ⑪ review 提 reset/stale ⑫ review 清单含大小写点（跨输入守卫）。

## 自验

- reference solution（solution/test_waive.py + review.md + run_results.txt）：check() **PASS 12/12** ✓
- 3 negatives（naive_empty / print_only / core_deleted）：check() **全 FAIL** ✓
- reference test_waive.py 在 .75 上真跑：A 上 9 passed / 0 failed；B 上 5 failed / 4 passed（regression 3 passed）→ 牙齿确认 ✓
- §4.9 退化提交（空壳 / 只 print / 删核心）全 FAIL ✓
