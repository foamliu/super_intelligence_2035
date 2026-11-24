# r1152 — judge-contract str-return fix (13 cases, str category closeout)

**日期**: 2026-11-24
**轮次**: shard B #r1152
**类型**: 判分契约修复轮（2026-11-24 运维令，与造题并行；fresh 池仍耗尽）

## 背景

r1151 收口 tuple 类别（12→0）后，按运维令优先级 `tuple > str > None/无return > dict非法键 > 辅助函数透传`，本轮收口 **str 类别**（13 个 case）。

str 类别 = check() 的唯一 PASS-path return 是字符串字面量（`return "PASS"` / `return "PASS: <detail>"`）。新严格契约下 str 返回一律 FAIL，故正确交付件会被误判。

## 修复（13 case）

每个 case 的 check() 恰好 1 个 return（PASS path），FAIL path 经 `raise AssertionError(...)`，故修复极小且安全：

| 子类 | 数量 | 修法 |
|:--|:--|:--|
| plain `return "PASS"` | 8 | → `return True` |
| descriptive `return "PASS[: ]<detail>"` | 5 | → `return {'pass': True, 'detail': '<detail>'}` |
| MosToxeClassify ref dict 键 `passed`（非合规） | 1 | → 键名改 `pass` |

8 plain: FifoStimulusGen, FineSimDcConvGuide, MosToxeClassify, Mt0MetastabAudit, NetlistDiffBankLogic, ShmooCfgParser, SpSpecCovAudit, VamRecoCellReplace
5 descriptive: MBistTopAnalyze, MonteMt0Stats, PdkModelWlExtract, ResCornerPctCompareProduce, DspfFloatLayerDiag

**与 r1151 不同**：r1151 的 12 tuple case 在 HEAD 的 reference/check.py 已被 shard D (e0643a514) 修成 dict 形，本轮只需回填 cases/B test 字段。本轮 13 str case 的 reference/check.py **未被预修**（仍为 str 返回），故需同时修 cases/B test 字段 + reference/check.py 两处。MosToxeClassify ref 曾被半修成 `{"passed": True,...}`（键名错），cases/B test 仍为 `"PASS"`，本轮统一修合规。

## 仅改返回值形状

- ✅ 只改 return 的值形状（str → True / dict-with-pass）
- ✅ FAIL path（raise AssertionError）原样不动
- 🚫 不改断言逻辑 / 条数 / 严格度
- 🚫 不改 prompt / assets / hidden

## 验证

1. `scripts/audit_check_returns.py --shard B`:
   - VIOLATION 148 → 135（-13）
   - str 类别 13 → 0（清零）
   - OK 385 → 398（+13）
2. 13 个 reference/check.py `py_compile` 全 OK
3. 13 个 case JSON test 字段 ast.parse OK，check() return 现均为合规形（True / dict keys=['pass','detail']）
4. negative_selftest.py（有此件的 case）：
   - SpSpecCovAudit: 4 neg 全 FAIL ✅
   - NetlistDiffBankLogic: 5 neg 全 FAIL ✅（含 §4.9 trio: empty/print-expected/core-deleted）
   - FAIL path 经 raise 未受影响
5. JSON diff：仅 test 字段内 `return "PASS..."` → `return True`/`return {'pass':...}` 单点变化，余 9 键 SAME（indent=2 格式与原文件一致，无 reformat 噪声）

## 提交

- EDA-Flow-Bench master: `b27458486` (26 files: 13 cases/B/*.json + 13 reference/*/check.py)
- 体积：TASK≈22.9KB / MEMORY 待压（本轮追加 1 行流水）

## 剩余违规（下轮）

binop16 > none_bare12 > dict_other30 > helper36 > var39 > no_return52 > list6 > ternary2 > compare1
按运维令优先级，下轮：binop（str-valued BinOp，本质同 str）→ none_bare/no_return（None/无 return）。
