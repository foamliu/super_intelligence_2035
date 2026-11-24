# r1153 — judge-contract binop-return fix (16 cases, binop category closeout)

**日期**: 2026-11-24
**轮次**: shard B #r1153
**类型**: 判分契约修复轮（2026-11-24 运维令，与造题并行；fresh 池仍耗尽 7 轮 reconfirm）

## 背景

r1152 收口 str 类别（13→0）后，按运维令优先级 `tuple > str > None/无return > dict非法键 > 辅助函数透传`，下一最大类为 **binop**（16 个 case）。binop = check() 的唯一 PASS-path return 是 str-valued BinOp（`return "PASS..." % (...)` / `return "PASS..." + (...)`）。新严格契约下 str 一律 FAIL，故正确交付件会被误判。

## 修复（16 case）

每个 case 的 PASS-path return 是一个 str-valued BinOp 表达式。修法：wrap 整个表达式为 `{'pass': True, 'detail': <原 BinOp expr>}`，保留 detail 信息给判分器；FAIL path（raise AssertionError）原样不动。

SimSpecJudge 特殊：5 个 FAIL-path str return（`return "FAIL: ..."`）+ 1 个 PASS-path str return。FAIL str 在新契约下本就 FAIL（行为正确），但为清洁统一改为 `return False  # FAIL: ...`；PASS 改 dict-pass。

| 子类 | 数量 | 修法 |
|:--|:--|:--|
| plain BinOp `%` PASS return | 14 | → `{'pass': True, 'detail': <expr>}` |
| BinOp `+` PASS return (SiOutWarnDiag) | 1 | → `{'pass': True, 'detail': <expr>}` |
| 多行 BinOp (DcaStimSweepGen) | 1 | → `{'pass': True, 'detail': <多行 expr>}` |
| SimSpecJudge FAIL str (5) + PASS str (1) | 1 case | FAIL→`return False`；PASS→dict-pass |

16 case: DcaStimSweepGen, DffResetPrioClassify, DspfTailorNetFix, DupSubcktDefDiag, DynPowerScanProduce, FsdbScopeSignalLocate, RonCurveEvaluator, SiOutWarnDiag, SimSpecJudge, SpfMeasDiag, SpiceTbGen, SvUsedModelExtract, UlvtDelvtoNetlistModifierProduce, WaveformPwlStimGenProduce, XmelabCuvpomPortDiag, XrunLogErrDiag

## 仅改返回值形状

- ✅ 只改 return 的值形状（str BinOp → dict-with-pass；FAIL str → False）
- ✅ FAIL path（raise AssertionError）原样不动
- 🚫 不改断言逻辑 / 条数 / 严格度
- 🚫 不改 prompt / assets / hidden

## 验证

1. `scripts/audit_check_returns.py --shard B`:
   - VIOLATION 135 → 119（-16）
   - binop 类别 16 → 0（清零）
   - OK 398 → 414（+16）
2. 16 个 reference/check.py `py_compile` 全 OK
3. 16 个 case JSON test 字段与 reference/check.py sha 一致（三方 sync：cases/B test == reference check.py）
4. negative_selftest.py（有此件的 case，§4.9 trio intact）：
   - DspfTailorNetFix: 3 neg 全 FAIL ✅
   - RonCurveEvaluator: 4 neg 全 FAIL ✅
   - SimSpecJudge: 3 neg 全 FAIL ✅
   - SpiceTbGen: 4 neg 全 FAIL ✅
   - DffResetPrioClassify: 5 neg 全 FAIL ✅
   - DynPowerScanProduce: 3 neg 全 FAIL + REF PASS ✅
   - SpfMeasDiag: 5 neg 全 FAIL + REF PASS ✅（selftest 同步修 dict-return 解包：`_is_pass()`/`_detail()` helper）
   - UlvtDelvtoNetlistModifierProduce: 3 neg 全 FAIL + REF PASS ✅
5. JSON diff：仅 test 字段内 return 行变化（wrap dict / →False），余 9 键 SAME（indent=2 一致，无 reformat 噪声）

## SpfMeasDiag selftest 同步修

SpfMeasDiag/negative_selftest.py 原用 `msg.startswith("PASS")` 解包 str return；改 dict 后需同步。加 `_is_pass(ret)`（True / dict pass|ok 键 True）+ `_detail(ret)` helper，与 r1151 同模式（r1151 同步改 2 in-process selftest 解包）。

## 提交

- EDA-Flow-Bench master: `a36ee2b2d` (33 files: 16 cases/B/*.json + 16 reference/*/check.py + 1 SpfMeasDiag negative_selftest.py)
- 仅 stage 本轮 33 文件（🚫 git add -A）；working tree 另有 ~120 未提交文件（prior-round B r1149-r1152 cases/B 未提交 + C-shard 并发未提交），记为 DEBT 见下

## ⚠️ 发现的 working-tree 一致性债（DEBT，需后续治理）

`git log` 显示 master 最近 3 commit 为 shard C #1059 / D #r1264 / A #r1114，**shard B r1149-r1152 的 commit 不在 master**。但 r1149-r1152 的 reference/check.py 改动**已在 master**（reference 目录无未提交 prior-round 改动），而 cases/B JSON test 字段改动**未提交**（13 个 cases/B 文件处于 old-shape tuple/str，与已提交 reference new-shape dict 不一致）。这是 prior-round 半提交 bug：reference 提交了、cases/B 没提交。本轮 r1153 已自洽（reference + cases/B 同步提交）。13 个 prior-round cases/B 半提交债留待后续轮治理（需逐个核对 cases/B test 字段与已提交 reference 一致后补提交）。

## 剩余违规（下轮）

按运维令优先级，binop 收口后下一档：none_bare12 / no_return52（None / 无 return / 裸 return）。
当前：NO_RETURN 52 > none_bare 12 > dict_other 30 > helper 36 > var 39 > list 6 > ternary 2 > compare 1。
下轮：none_bare / no_return（None/无 return 类别，§3.3）。

## 台账 / 覆盖率

台账 B 不动（1769: case 597/parked 1172）。covered=597/4529=13.2%。fresh 池仍耗尽（7 轮 reconfirm）。🎯 最近20条 20/20=100%（观察值，未 pi 实跑）。DEBT:0 + 判分契约债 135→119（本轮 -16）+ working-tree 半提交债 13 cases/B。
