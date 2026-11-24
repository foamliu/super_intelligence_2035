# r1151 判分契约修复轮 — tuple 返回型 case 修复收口（续 r1150）

**日期**: 2026-11-24
**触发**: 2026-11-24 运维令「判分契约修复」（commit 6c1a50ee9），与造题并行（fresh 池仍耗尽，7 轮 reconfirm）。
**上轮**: r1150 修 13 个 tuple case（9 同步 + 4 新修），剩 12 个 tuple-return case。本轮**收口 tuple 类别**。

## 本轮修复 12 个 case（tuple-return → 契约 dict 形）

| case | 旧返回形 | 修法 |
|:--|:--|:--|
| DsimSkillLogAnalyzer | `return False, "\n".join(failures)` ×5 / `return True, "PASS..."` | `{'pass': False/True, 'detail': ...}` |
| MatrixRunDirExplain | `return False, "msg"` ×3 / `return True, "PASS..."` | dict |
| NmosAgeChar | `return False, "; ".join(...)"` ×3 / `return ok, (...)` | dict |
| SimRunScriptDiff | `return False, "msg"` ×50 / `return True, "PASS a-l..."` (51 returns) | dict（AST 段替换） |
| Mt0PvrefAbsGroupStat | `return (False, "msg")` ×4 / `return (passed, "msg")` | dict |
| VthOverrideHowtoGuide | `return results, False` ×6 / `return results, passed` | `{'pass': bool(passed), 'results': results}` |
| WtmPatternDirReview | `return cond, "msg"` ×5 | `{'pass': passed==total, 'conds': cond, 'detail': msg}` |
| WvTrtfDutySummarizer | `return 0, total, failures` ×3 / `return passed, total, failures` | `{'pass': passed==total, 'passed': N, 'total': N, 'failures': [...]}` |
| CbrForceMechanismExplain | `return results, msgs, "msg"` ×5（3-tuple） | `{'pass': True/False, 'results':.., 'msgs':.., 'detail':..}` |
| TxRonSize | `return False, "msg", conds` ×5 / `return ok, "msg", conds`（3-tuple） | `{'pass': bool(ok), 'detail':.., 'conds':..}` |
| RevCali3DCoord | `return False, "msg"` / `return _check_impl(...)`（helper 透传 tuple） | dict + lambda 包裹 helper 透传 |
| DelvtoInjector | `return results, "msg"` ×3 / `return _fill(results), _summarize(results)` | dict（pass 由 results 计算） |

**SimRunScriptDiff 用 AST 段替换**（51 个 return 跨多行括号续行，纯文本 replace 会破坏语法）：解析 test 字段 → 定位 check() 内所有 Return(Tuple) 节点 → 用 `ast.get_source_segment` 取原文本 → 替换为 `ast.unparse(Return(Dict(pass,detail)))` → 自底向上替换保持偏移。其余 11 case 用定向字符串 replace（每 case return 形状规整、唯一可定位）。

## 关键发现：reference/check.py 与 cases/B test 字段脱节（同 r1150）

12 case 的 `reference/<id>/check.py` 在 HEAD 已是 dict 形（shard D commit e0643a514 早修），但 `cases/B/<id>.json` 的 `test` 字段仍为旧 tuple 形（evaluator 实际跑的源）。audit_check_returns.py 读 cases/ test 字段 → 仍报 VIOLATION。

**处理**：对 12 case 把 test 字段改契约 dict 形。改完后 **test 字段 == HEAD reference/check.py == working reference/check.py（sha256 三方一致，全 MATCH）**——即本 round 的定向/AST 变换独立得出的结果与 shard D 早先的 reference 修法逐字节一致，强一致性验证。reference/check.py 与 negative_selftest.py 均已 CLEAN（HEAD 已修），本轮实际只动 cases/B JSON 的 test 字段。

## 验证

| case | audit | 端到端跑 |
|:--|:--|:--|
| CbrForceMechanismExplain | OK | **negative_selftest: ref 20/20 PASS + 4 neg 全 FAIL** ✅（直接 unpack 修复） |
| Mt0PvrefAbsGroupStat | OK | **negative_selftest: 4 neg 全 FAIL** ✅（直接 unpack 修复） |
| WvTrtfDutySummarizer | OK | **check.py __main__ 15/15 PASS exit0** ✅（纯 Python CSV） |
| TxRonSize | OK | __main__ dict unpack 正常（"hidden B not found"=env 非 regression） |
| SimRunScriptDiff | OK | __main__ dict unpack 正常（dummy zip FAIL gracefully） |
| 其余 7 | OK | 需 hspice/finesim（dev env 无，沙盒有，pre-existing 非回归）；unpack 模式与已验 5 case 同构 |

evaluator 契约确认（run_one.sh: `r.get('pass') is True`）：`return True`=PASS、`return {'pass':True}`=PASS、`return {'pass':False}`=FAIL，全部合规。

## 纪律遵守
- ✅ 只改 check() 返回值形状 + __main__/selftest 解包
- ✅ 不改断言逻辑、不改断言条数、不改判分严格度
- ✅ 不改 case prompt / assets / hidden（JSON diff 仅 test 字段变化，其余 9 键 SAME）
- ✅ test 字段 == reference/check.py（三方 sha256 一致）
- 🚫 未碰任何 *.jsonl
- 🚫 未碰别 shard 文件（工作树中 C shard 修改非本 round 所为，未 stage）

## 进度
- **B shard tuple 类别收口**：12 → **0**（tuple-return case 清零）
- audit summary: OK 373→**385**(+12) / VIOLATION 160→**148**(-12) / NO_RETURN 52 / NO_CHECK_FN 12 / PARSE_ERROR 1
- 剩余违规按优先级：str 13 > binop 16 > none_bare 12 > no_return 52 > dict_other 30 > helper 36 > var 39 > other 2（下轮按运维令优先级 str > None 续修）
- 判分契约债：220 → **148**（r1149 -6 + r1150 -13 + 本轮 -12 = -31；另 shard D/A/C 并行修各自 shard）
