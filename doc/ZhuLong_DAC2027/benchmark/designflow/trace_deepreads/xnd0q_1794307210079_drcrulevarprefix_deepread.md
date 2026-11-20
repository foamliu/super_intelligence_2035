# Deepread: 1794307210079_xnd0q (xinqiaoz @ 10.129.2.11, mc=249)

## 真实任务（physical_verify / DRC rule diagnosis，B-class revival）

用户 xinqiaoz 在 10.129.2.11（XinQiaoZ 工作站，DRC/QA 工程师）让 agent 排查一份
DRC QA 报告 `drcQa_G5_CIP_DECQA_v0d5_Rev12.report` 里出现的
"variable with unmatched value" 报错，怀疑是 LDR 规则名与 DRC deck 变量名前缀碰撞所致。

**用户原话（U#17，节选）**：
> drcQa_G5_CIP_DECQA_v0d5_Rev12.report...在 ldr 中，有 V1_ENC_007_00，V1_ENC_007_00_Auto
> 这两条 rule...drc deck 中 V1_ENC_007_00 这条 rule 没有定义 variable，
> V1_ENC_007_00_Auto 定义了 variable _V1_ENC_007_00_AUTO_。在最终的 report 中，有可能
> V1_ENC_007_00 这条 ldr 误匹配到了 _V1_ENC_007_00_AUTO_ 这个 variable，导致最终报错。

域关键词分布：drc:4180 / pdk:978 / calibre:583 / lvs:35 / cmos:29 / .gds:24 / techfile:8 →
强 physical_verify (Calibre DRC QA) 味，**正 C 域**。原 B-shard 在 candidates_mc10.tsv
判 spice_sim 是误判，B 把它 parked 为 "wrong-shard" 是对的（B 域不该收），但**整条 session
本身是 C 域 physical_verify**，r733 从 B 的 parked 池中复活回收至 C。

## Agent 实际行为（131 msgs，单意图诊断）

1. 读取 drcQa_G5_CIP_DECQA_v0d5_Rev12.report，定位报错块 "variable with unmatched value"，
   抽出报错变量名清单（`_V1_ENC_007_00_AUTO_` 等）。
2. 读取 LDR CSV，抽取规则名清单；识别 `V1_ENC_007_00` / `V1_ENC_007_00_Auto` 是同名族（前缀关系）。
3. 读取 DRC deck，定位每条规则的 VARIABLE 定义；确认 `V1_ENC_007_00` 在 deck 中无 VARIABLE，
   `V1_ENC_007_00_Auto` 在 deck 中定义 `_V1_ENC_007_00_AUTO_`。
4. 提出根因假设：LDR 规则名前缀匹配（calibre report 工具可能用前缀把报错变量
   `_V1_ENC_007_00_AUTO_` 错误归到 base 规则 `V1_ENC_007_00` 上，而 base 规则在 deck 里
   没有 VARIABLE → 报 "unmatched"）。
5. 用户接受诊断结论 = gold verdict。

诊断逻辑完全 path-dependent on 三文件交叉比对（report/LDR/deck），是 mock-behavioral
reframe 的理想原料：把「真实三文件交叉诊断」抽成「纯 stdlib 解析 report+ldr.csv+drc.deck」。

## Reframe：mock-behavioral `drc-rule-var-prefix-collision`（physical_verify）

纯 stdlib CLI：`python3 solve.py <report> <ldr.csv> <drc.deck>`
输出 7 顶层键 JSON：
- `unmatched_variables`：report 里 "variable with unmatched value" 抽出的变量名清单
- `undefined_drc_rules`：ldr 中出现、但 deck 中无 VARIABLE 定义的规则名清单
- `prefix_collisions`：每条含 `{base_rule, auto_rule, variable, ldr_base_value, ldr_auto_value}`，
  base 规则名是另一条 auto 规则名的前缀（去掉 `_Auto` 后缀），且 base 在 deck 中无 VARIABLE
- `genuine_unmatched`：unmatched_variables 减去 prefix_collisions 抓到的 _AUTO_ 变量，剩下真正未匹配的
- `root_cause`：`rule_name_prefix_collision`（当 prefix_collisions 非空且数量 == _AUTO_ 结尾报错变量数）
- `counts`：`{variableValueUnmatchedCount, variableUndefinedDrcCount, prefix_collision_count, genuine_unmatched_count}`
- `reproduction_confirmed`：bool，前缀碰撞数 == _AUTO_ 结尾报错变量数时为 true

## Fixtures（三 fixture 反硬编码）

- **A（visible，V1_ENC_007_00 族）**：3 条 _AUTO_ 碰撞 + 1 条真未匹配 _AT7_DRW_003_02_A_，
  undefined_drc_rules = V1_ENC_007_00 / V1_ENC_007_00_Auto；root_cause=prefix_collision；
  counts=(3,2,3,1)；reproduction_confirmed=true
- **B（hidden，反 A：V4/V5_SP_002_10 族）**：2 条 _AUTO_ 碰撞 + 1 条真未匹配 _AT7_DRW_003_02_A_，
  undefined_drc_rules = V4_SP_002_10 / V5_SP_002_10；PL/NL 控制组（无碰撞）；
  counts=(3,2,2,1)；reproduction_confirmed=true
  → prefix_collision_count 从 A 的 3 降到 2，反硬编码 A 答案（cond n 退化守卫）
- **B2（hidden cross-input guard，极简 L1_DRW_001_00 族）**：1 条 _AUTO_ 碰撞，0 真未匹配；
  counts=(1,1,1,0)；reproduction_confirmed=true
  → 跨输入泛化（不同规则族），反硬编码 A 或 B（cond k/l/m）

## 验证

- reference solve.py：纯 stdlib，A/B/B2 三 fixture 输出均与预期一致
- check.py：14 条件 a-n（每条独立可 FAIL；B 主 10 条 a-j + B2 cross-input guard 4 条 k-n）
- k_rationale == k_check == 14 ≥ 8 ✓
- 4 negatives FAIL distinct labels：
  solve_empty→(b) / solve_print_expected→(d) / solve_return_garbage→(f) /
  solve_wrong_key_structure→(c+JSON)
- §4.9 (a) 非 zip / 缺文件 deliverable → (a) FAIL；
  (b) 无输出 → (b) FAIL；(c) 硬编码 → 多条 FAIL
- round-trip PASS；determinism 3× md5 identical (ce3b81a1ff9d71cd99f7997f81432b5b)
- negative_selftest ALL GOOD；
  embedded test field == on-disk check.py byte-identical (md5=10f7f80a6a0c9720f02912fdd8b246cb)

## 落库

- 追加 EDA-Eval-DesignFlow_C.jsonl (455→456)
- assets/EDA-Eval-DesignFlow-DrcRuleVarPrefixCollision-001/：sample_input/, hidden/b/, hidden/b2/,
  prompt.txt, task_brief.md, hidden_manifest.json
- reference/EDA-Eval-DesignFlow-DrcRuleVarPrefixCollision-001/：solve.py, check.py,
  negative/ (4 个), negative_selftest.py
- ledger C 追加 xnd0q 一行（reclaimed from B parked → case）
- domain=physical_verify, track=mock-behavioral, tier=L1

## distinct vs 往轮

- vs r731 yavow LvsGuiLaunchJudge（env-config / launchability-judge）= 不同子型
- vs r730 LvsRunCompare（lvs-report-compare）= 不同子型
- vs r729 idkjn DummyDeckStructDiff（struct-diff）= 不同子型
- 本轮 = **drc-rule-var-prefix-collision** 子型（C 域首例 DRC QA 报告+LDR+deck 三文件交叉诊断）

## 复活判定（11-15 令§二）

旧规则会把这种「consultation / 诊断结论」判为 weak。11-15 令§二明确把
analysis-Q&A / debug-Q&A / diagnosis 类列为有效 case 类型。本 session：
- 单意图（DRC 规则名前缀碰撞根因诊断），非多轮发散；
- 有明确确定性结论（前缀碰撞根因清单 + 修复建议）= 用户接受的 gold verdict；
- 诊断逻辑完全 path-dependent on 三文件交叉比对，是 mock-behavioral reframe 理想原料。

→ **B-class revival 实证**，符合 r645-r733 mock-behavioral 单意图 analysis-Q&A/debug-Q&A family。
