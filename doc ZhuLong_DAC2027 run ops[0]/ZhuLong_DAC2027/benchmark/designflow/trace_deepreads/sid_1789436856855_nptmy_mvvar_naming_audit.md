# trace_deepread: sid 1789436856855_nptmy (multi-value variable naming standard)

- **user**: xinqiaoz
- **host**: hfeg0pkn004 (10.129.2.13)
- **session_file**: 1789436856855_nptmy.messages.json (1.7MB, 336 msgs, 170 user turns)
- **match_count**: 358 (pdk:872; calibre:286; cmos:100; .gds:11; gdsii:1; aether:1)
- **domain**: physical_verify (calibre DRC deck)
- **claimed**: 2026-11-03 (shard C round 56)

## 真实任务（用户原话）

UI#0（逐字）：
> 阅读 /home/xinqiaoz/PDK_QA/pdkQaSystem/docs/proposals/02_multi_value_variable_naming_standard.md，了解需求，如果有任何没有弄清楚的问题，直接询问我，当你认为你全部弄清楚之后，向我复述你的理解.

UI#6（用户对 agent 澄清问题的回答，含设计决策/根因）：
> 1. _c/_p 的逻辑在当前的代码里面已经有了，是否大小写任然沿用当前的代码逻辑（代码中应该是把 ruleId upper，所以理论上大小写都可以）
> 2. seq 与 LDR 数值顺序要求做对应。
> 3. ldrValue.lower() == "check" 的行为暂时不变。
> 4. 目前没有，你可能需要自己构造假数据，可以参考我们的一些真实的文件：/home/xinqiaoz/issues/0811_bq
> 5. 被 skip 的 LDR rule（如 FAM_Size_004_01）的 coreValue/periValue 完全不参与值检查。

## A-档 disqualified 判定

- UI#0 是「读提案 + 复述理解」的元任务，不是纯需求陈述；真实需求落在私有提案文档 `02_multi_value_variable_naming_standard.md`（`/home/xinqiaoz/PDK_QA/...`，e0031982 身份 `Permission denied` 无法直接读取）。
- UI#6 用户已对 agent 的澄清问题给出根因/设计决策（_c/_p 沿用现有大小写逻辑、seq 与 LDR 顺序对应、"Check" 行为不变、被 skip 的 rule 不参与值检查）→ 违反 A-档选轮规则「🚫 用户已指出根因或给出修复方案」。
- gold = agent 改动 `DrcValueCheck.py`（`findTargetVariable` / `compareLdrValueWithVariable` / `compareLdrValueWithDrc0`）+ `DrcInfo.py`（`variableNameMatch`）+ `LdrInfo.py`，依赖整套 PDK_QA 私有代码 + calibre，沙盒不可复现。
- → **A-档 disqualified → B-档 synthesized L1-boundary**（离线 SVRF + CSV 文本解析，判分机无需 live calibre，§4.2 ✓）。

## 提案规范要点（从 agent 工具读结果提取）

- 新格式 `_{ruleId}__{seq}_`（双下划线 `__` 为 ruleId/seq 结构性锚点；ruleId 内部只用单 `_`，故 `__` 无歧义）。
- core ≠ peri 时：`_{ruleId}_c__{seq}_` / `_{ruleId}_p__{seq}_`，两侧各需 01..N 完整序列。
- core == peri 时：无 `_c`/`_p` 后缀，seq 01..N 连续无重复。
- 旧格式 `_{ruleId}_NN_`（无 `__`）有歧义（`_V2_Size_002_00_01_` 无法确定属于 `V2_Size_002_00` seq=01 还是 `V2_Size_002_00_01` 无 seq）→ 标 old_ambiguous。
- `//Skip <ruleId>`：该 rule 的变量不参与值检查（仅记录 skipped_not_checked）。
- DRC rule 块 `<ruleId> { ... }` 引用别的 ruleId 的变量 = 跨 ruleId 引用（正常写法，仅记录 cross_rule_ref，不报失败）。
- 适用所有 rule 类型的多值场景（Size / W / S / F / ENC / A / LS），不限 Size。
- 组合型（多条 LDR 各多值合并为 1 条 DRC）：值检查只查与当前 DRC ruleId 匹配的变量。
- LDR CSV 表头：`location,sheet,ruleType,ruleId,coreValue,periValue,shrinkCoreValue,shrinkPeriValue,coreRelation,periRelation,description`；真实样例 `V2_General_v0d5_Rev29_LDR_DDR.csv`，coreValue/periValue 可为单数值 / `Check`（不检查值）/ 空（值在 description）。

## 合成 case

- **task_id**: EDA-Eval-DesignFlow-MVVarNamingAudit-001
- **skill**: `mvvar_naming_audit.py`（Python3 标准库 re/csv/argparse/json/sys，确定性 JSON 输出）
- **核心难度**：`__` 双下划线锚点解析（区分新/旧格式）+ core/peri 双侧序列完整性（core≠peri 时 _c 与 _p 各自 01..N）+ seq 连续性（gap 检测）+ skip 规则隔离 + 跨 ruleId 引用识别 + 变量值保留 + 确定性输出。
- **A 输入**（可见，全合规）：deck_A.svrf（13 VARIABLE，含 2 old_ambiguous + 1 unknown_rule + 1 skipped rule 的 2 vars + 跨 ruleId 引用）+ ldr_A.csv（5 rule）。
- **hidden B**（主判分，植入 6 类违规）：core_peri_violation（BB missing _p）+ seq_gap（CC 01,03 missing 02）+ unknown_rule（ZZ_unk）+ skipped（GG //Skip + 2 vars）+ cross_rule_ref（HH block 引用 GG vars，4 次）+ old_ambiguous（_old_ambig_00_01_）。
- **hidden B2**（cross-input guard）：total_vars=4 ≠ B 的 14。
- **hidden B3**（cross-input guard 2）：rules_fail=1 ≠ B 的 2，old_ambiguous=0 ≠ B 的 1。
- **与既有区别**：DeckIncludeResolve=SVRF INCLUDE 闭包；DummyQaCliNoConfig=PDK QA CLI/config 合并；VlogPortAudit=Verilog 端口定义 vs 实例化；本案 = **DRC deck 多值变量命名规范审计**（新格式 `__` 锚点 + core/peri 双侧完整性 + seq 连续性 + skip/cross-ref 分类），主题/断言独立。

## 自验

- ref `mvvar_naming_audit.py` 在 A/B/B2/B3 上 check() 全 PASS（16 条件 a-p）。
- 5 negatives 全 FAIL_OK（NEG_RC=0）：fake_empty→(a), fake_print_expected→(m), fake_core_deleted→(g), naive_no_underscore→(g), naive_hardcode_B→(n)。
- §4.9 (a)空壳 (b)只 print 期望 (c)删核心 三假提交全 FAIL（= fake_empty / fake_print_expected / fake_core_deleted）。
- 确定性：B 跑 3 次 md5 一致（da0856c4739f880c7c05391d4aefb604）。
- k_rationale = k_check = 16 ≥ 8 GATE PASS ✓。
