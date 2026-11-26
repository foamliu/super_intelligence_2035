# Deepread · 1793598171487_3gpkg · xinqiaoz · DRC QA merged-notice bloat root-cause

> shard C candidate (r391 selection round). SEED picked, deepread complete.
> 本轮（r391）基于本 deepread 合成 case：`EDA-Eval-DesignFlow-DrcQaMergeBloatDiagnose-001`（physical_verify, B档 synthesized）。

## trace_source

- session_file: `1793598171487_3gpkg.messages.json`
- user: xinqiaoz（PDK QA 工程师，r388 P-001 发言者；r389 的 rmlwy/xinqiaoz 是其同人 mc281 但 parked）
- host: hfeg0plg56 (10.129.32.75 也存)
- mc: 199 (mc≥10 口径, 11/11 snapshot)
- keywords: `drc:4486;calibre:162;pdk:837` — drc 关键词高来自 PDK-QA report 内容（true-positive，本次 trace 真在诊断 DRC QA 输出）
- match_count: 199
- 3 user turns, 89 messages total, 698KB trace file
- 日期：2026-11-02（Nov 2 周一，周末后的 PDK QA 周一例行核对窗口）

## real_task_summary

xinqiaoz 是 PDK QA 工程师，日常工作流：跑 DRC QA 工具链生成 run report + LDR CSV，对比前后两次 run 的 `ldrSameValueNeedMergeCount`（"Ldr with corresponding drc need to be merged" 检查项），定位计数为何在两次 run 间跳变。

本 trace 是一个 issue-handler / diagnosis 工作流（不是 build-tool）：agent 被给两份 DRC QA run report（t1 早 / t2 晚）+ 对应两份 LDR CSV，要求找出为什么 t2 的 `ldrSameValueNeedMergeCount` 比 t1 多了 30+ 条。

**关键对话节点**：
- USER#0 (plan/seed): 给出 t1/t2 report + ldr CSV 路径，要求对比诊断 "Ldr with corresponding drc need to be merged" 计数为何从 ~3 涨到 ~35
- USER#1 (act): 「你具体看了哪些字段？怎么定位到的？」追问诊断依据
- USER#2 (plan/confirm): 「那这个 _Auto 的 LDR 行是怎么被漏掉的？sheet 名字大小写吗？」← **用户自己提出 root-cause 假设**

## agent 实际诊断（trace msg flow）

agent 走了 8 步 reasoning chain（不是 build-tool，而是 issue 诊断）：

| step | 动作 | 输出 |
|---|---|---|
| 1 | `head`/`grep` 两份 report，提取 `ldrSameValueNeedMergeCount`（t1=3, t2=35）| 计数 delta=32 |
| 2 | 对比 t1/t2 其他 counter（ldrCount / ldrWithoutDrc / multiData / moreCheckDrc / skip），发现只有 ldrCount（t1=387→t2=380, -7）和 merged 计数变，其他不变 | "只有 merged + ldrCount 变" |
| 3 | 提取两份 report 的 merged ruleId 列表，做 set diff → 32 个 new rule（t2-only），都是 `*_Auto` 后缀（如 `V3_ENC_007_00_Auto`）的"父 ruleId"（去掉 _Auto）| new_rules=32 |
| 4 | `head`/`diff` 两份 ldr CSV，发现 t1 有 `LDR_AUTO` sheet，t2 改成了 `LDR_Auto`（首字母大写变小写）| sheet-name case change |
| 5 | grep 两份 CSV 的 sheet 名分布，t1 `LDR_AUTO`=7 行，t2 `LDR_Auto`=7 行（行数不变，仅 case 变）| case-only change |
| 6 | 读 PDK QA 工具源码（`findTargetDrc` / `buildDrcOwnerMap` / `LdrInfo`），确认 sheet filter 是 **case-sensitive exact match**（且在 match 前 `.strip()`）| filter mechanism |
| 7 | 验证：t2 的 `LDR_Auto` 7 行经 `.strip()` 仍是 `LDR_Auto`，不等于 t1 effective set 中的 `LDR_AUTO` → 被过滤掉 → 这些 `*_Auto` ruleId 的 deck rule 失去 owner，fallback 到 main ruleId → 一个 main ruleId 同时拥有 main + _Auto 两条 deck rule → `findTargetDrc` 返回 ≥2 → 触发 false "need to be merged" notice | root cause 链 |
| 8 | 同时发现 t2 还有 `LDR_Array ` / `LDR_CMOS_3DIC `（**尾部空格**），但 `.strip()` 后与 t1 一致 → 被 reconcile，**不是 bug**（red herring，需排除）| trailing-space 排除 |

**最终结论**：t1 sheet `LDR_AUTO` 在 t2 被改成 `LDR_Auto`，case-sensitive sheet filter 把 t2 的 7 行 `_Auto` LDR 静默过滤掉，导致 32 个 main ruleId 触发 false merge notice。trailing-space sheet 是 red herring（被 strip reconcile）。

## root-cause 机制（这是 case 的 hard part）

merged-notice 触发条件 = `(LDR main row valueSame=True) AND (findTargetDrc 找到 ≥2 deck rules for the main ruleId)`

`findTargetDrc` / `buildDrcOwnerMap` 给每条 deck rule 分配 owner = 最长 *sheet-filtered* LDR ruleId 前缀。

sheet filter (LdrInfo) 在 sheet 名上做 **case-sensitive exact match**，**match 之前先 `.strip()`**：
- 尾部空格 → strip 后一致 → reconcile → **不是 bug**
- 大小写变化（LDR_AUTO→LDR_Auto）→ strip 后仍不一致 → **被静默过滤** → **bug**

当 `_Auto` LDR row 被过滤掉，其 deck rule 的 owner fallback 到 main ruleId → main rule 同时匹配 main + _Auto 两条 deck rule → 触发 false "need to be merged" notice。

## case 合成决策（r391）

**B档 synthesized**（非 A档 faithful）：
- 原 trace 是 issue-handler 诊断流（agent 直接读真 report + 真 CSV 得出结论），A档 faithful 需要把 agent 的诊断过程 CLI-ize，但原报告 600+KB、CSV 4MB 且含真实产品 ruleId，无法直接附入 SUT 沙盒
- 故合成"小而精"的 reports + CSVs：保留 root-cause 机制（sheet-name case-only change + trailing-space red herring + _Auto correlation），但用合成的 ruleId 集和可控的计数规模
- visible A (3→8, delta=5) 与 hidden B (4→18, delta=14) 都遵循同一 root-cause 模型，但数值/规模/结构均不同 → cross-input guard 可行
- hidden B：4 baseline + 14 auto rules；sheet `LDR_XTO`→`LDR_Xto`；20 filtered rows；ldrCount 1542→1522
- visible A：3 baseline + 5 auto rules；sheet `LDR_AUTO`→`LDR_Auto`；7 filtered rows；ldrCount 387→380

## Gold reference

`diagnose_merge_bloat.py`（CLI-ized agent 诊断逻辑）：
- `parse_report` / `parse_ldr_csv` / `compute_sheet_diff` / `diagnose` / `main`
- `compute_sheet_diff` 按 `stripped().lower()` 分组：stripped 名不同 → `case_only` + `bug_causing=true`；仅 raw 不同（whitespace）→ `whitespace_only` + `bug_causing=false`
- `diagnose` 计算 count_t1/count_t2/delta/new_rules/baseline_rules，验证 other_counters_unchanged + input_files_changed，跑 sheet_diff，correlate new_rules 与 `_Auto` rows 在 bug-causing sheet 上的对应关系，最后判定 root_cause

## check.py 设计

18 conditions a-r（≥8 gate 远超）：
- a-d: zip 含脚本 / 语法 / 必需函数(parse_report/parse_ldr_csv/compute_sheet_diff/main) / argparse(--report1/--report2/--ldr1/--ldr2/--out)
- e: hidden B 上 exit 0 + 写 diagnosis.json
- f: 必需 top-level keys 齐全
- g/h/i: count_t1=4 / count_t2=18 / delta=14
- j/k: new_rules 14 个 auto / baseline_rules 4 个
- l: other_counters_unchanged=true
- m: input_files_changed=true
- n: sheet_name_diff 含 case_only LDR_XTO→LDR_Xto + bug_causing=true
- o: trailing-space sheets (LDR_Array/LDR_CMOS_3DIC) 标 whitespace_only + bug_causing=false（red herring 排除）
- p: root_cause=sheet_name_case_mismatch
- q: evidence changed_sheet 含 LDR_XTO 和 LDR_Xto / filtered_rows=20 / newly_merged_from_auto=14 / new_rules_with_auto_in_filtered_sheet=14 / new_rules_valuesame_verified=14
- r: cross-input guard — visible A 上 count_t1=3/count_t2=8/delta=5/root_cause=sheet_name_case_mismatch/changed_sheet=LDR_AUTO->LDR_Auto（与 B 不同，防硬编码）

2 subprocess real-run（cond e hidden B + cond r visible A）。

§4.9 三假全覆盖：
- empty shell → cond f fail（无 keys）
- print expected (hardcode B) → cond r fail（cross-input A 仍输出 B 值）
- hardcode A → cond g fail（B 上 count_t1=3≠4）
+ 4th neg omit_sheetdiff → cond n fail（跳过 sheet 分析，root_cause=unknown）

4 negatives + negative_selftest 全 FAIL ✓。
ref self-test 18/18 PASS ✓。

## 注意点

- 真实 trace 中 merged 计数 3→35（delta=32）；合成 B 用 4→18（delta=14）、A 用 3→8（delta=5）。规模缩小是为让 SUT 在合理 token 内读完，但 root-cause 拓扑（case-only sheet change + trailing-space red herring + _Auto correlation）100% 保留
- sheet 名 `LDR_XTO`/`LDR_Auto` 是合成名，但 case-sensitivity bug 的形态（全大写 → 混合大小写）与真实 trace 一致
- xinqiaoz 是 r388 P-001 议题的发言者；本 case 是其第二条 case（第一条 r388 发言本身未交付 case）
