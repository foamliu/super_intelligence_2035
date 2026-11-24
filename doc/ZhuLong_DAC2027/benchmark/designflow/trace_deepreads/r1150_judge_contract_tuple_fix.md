# r1150 判分契约修复轮 — tuple 返回型 case 修复（续 r1149）

**日期**: 2026-11-24
**触发**: 2026-11-24 运维令「判分契约修复」（commit 6c1a50ee9），与造题并行（fresh 池仍耗尽，7 轮 reconfirm）。
**上轮**: r1149 修 6 个 COND-list 返回型 case。本轮按优先级转 **tuple 返回**（最大类，原 25 个）。

## 关键发现：reference/check.py 与 cases/B test 字段脱节

扫描发现 shard D commit `e0643a514`（2026-11-24 15:24）已批量修复 **9 个 tuple case 的 `reference/<id>/check.py`**（返回值改契约形），但**未同步 `cases/B/<id>.json` 的 `test` 字段**（evaluator 实际跑的源）。audit_check_returns.py 读 cases/ test 字段 → 仍报 VIOLATION。

**处理**: 对这 9 个 case，先 diff 确认 test 字段与 reference/check.py **仅差返回值形状 + __main__ 解包**（无断言/逻辑漂移），再把已修好的 reference/check.py 内容回填到 `test` 字段。这是纯同步，不动逻辑。

## 本轮修复 13 个 case

### A. 同步类（9 个，reference 已被 shard D 修好，回填 test 字段）
| case | 返回形 | 修法 |
|:--|:--|:--|
| BisecMt0SmCalc-001 | `return ok, results` / `return False, results` | dict `{'pass': bool(ok), 'results': results}` |
| CaSkewEdgeStat-001 | 同上 | 同上 |
| ProbeStimFromSx-001 | 同上 | 同上 |
| SnmSquareValidator-001 | `return passed, results` | dict `{'pass': bool(passed), 'results': results}` |
| VtargetBisecAggregate-001 | `return ok, results` | dict |
| GvimCjkConfigGen-001 | `return True, "msg"` | `return True`（FAIL 走 assert） |
| HspicePanelCurProjReport-001 | `return True, "msg"` | `return True` |
| SolidoSimlogLocateGuide-001 | `return (True, "msg")` | `return True` |
| TermInvestigationReport-001 | `return True, "msg"` | `return True` |

同步的 9 个 case 的 `__main__` 也已被 shard D 改为 dict 解包（`r = check(...); ok = r['pass']...`），回填 test 字段时一并带入。

### B. 新修类（4 个，reference/test 都还是 tuple，本轮动手）
| case | 旧返回 | 新返回 | __main__/selftest 解包 |
|:--|:--|:--|:--|
| SimErrSubcktRefDiag-001 | `return ("PASS", results)` | `{'pass': True, 'results': results}` | `verdict,res=check` → dict 解包 |
| SarAdc8bNetlistGen-001 | `return False,"msg"` ×3 + `return True,"msg"` | `return False` / `return True` | main + negative_selftest 两处 `passed,msg=check` → `passed=check; msg=...` |
| RcurrDirClassify-001 | `return (False,[...])` / `return (ok, errors)` | `{'pass': False, 'errors': [...]}` / `{'pass': bool(ok), 'errors': errors}` | main + negative_selftest `ok,errs=check.check` → dict 解包 |
| TrimSweepSpGen-001 | `return (False,"msg")` ×3 + `return (True,"msg")` | `{'pass': False, 'detail': ...}` / `{'pass': True, 'detail': ...}` | negative_selftest `ok,msg=run_check` ×2 → dict 解包 |

## 验证

| case | audit | selftest / ref |
|:--|:--|:--|
| BisecMt0SmCalc | OK | ref 需 hspice（dev env 无，沙盒有，pre-existing） |
| CaSkewEdgeStat | OK | 同上 |
| ProbeStimFromSx | OK | 同上 |
| SnmSquareValidator | OK | 同上 |
| VtargetBisecAggregate | OK | 同上 |
| GvimCjkConfigGen | OK | _gen_B.py 缺失（pre-existing，非回归） |
| HspicePanelCurProjReport | OK | 同上 |
| SolidoSimlogLocateGuide | OK | 同上 |
| TermInvestigationReport | OK | 同上 |
| SimErrSubcktRefDiag | OK | ref 需 sim（pre-existing） |
| SarAdc8bNetlistGen | OK | **selftest 全 6 neg FAIL = NEG_OK** ✅ |
| RcurrDirClassify | OK | ref FAIL（hspice 缺，pre-existing）；dict 解包正常工作（selftest 跑通打印 conditions） |
| TrimSweepSpGen | OK | **selftest ref PASS + 4 neg 全 FAIL** ✅（纯 Python，完整验证） |

**关键**: 纯 Python 的 SarAdc8bNetlistGen / TrimSweepSpGen selftest 完整通过（ref PASS + neg FAIL），证明 dict 解包改动正确。需 sim 的 case（hspice/finesim）ref 在 dev env 跑不通是 pre-existing（沙盒有 sim），改动前后行为一致（旧 __main__ 也是 sim 不跑则 rc=1）。

evaluator 契约确认（run_one.sh: `r.get('pass') is True`）：
- `return True` = PASS ✅
- `return {'pass': True, ...}` = PASS ✅
- `return {'pass': False, ...}` = FAIL ✅

## 纪律遵守
- ✅ 只改返回值形状 + __main__/selftest 解包
- ✅ 不改断言逻辑、不改断言条数、不改判分严格度
- ✅ 不改 case prompt / assets / hidden
- 🚫 未碰任何 *.jsonl
- 🚫 未碰别 shard 文件

## 进度
- B shard violations: 220 → **160**（本轮 -13 case；另 shard D commit e0643a514 直接修了 ~47 个 cases/B test 字段）
- 剩余 tuple-return: **12 个**（CbrForceMechanismExplain / DelvtoInjector / DsimSkillLogAnalyzer / MatrixRunDirExplain / Mt0PvrefAbsGroupStat / NmosAgeChar / RevCali3DCoord / SimRunScriptDiff / TxRonSize / VthOverrideHowtoGuide / WtmPatternDirReview / WvTrtfDutySummarizer）——多为 helper 透传 / 3-tuple / 大型 SimRunScriptDiff(51 return)，下轮续修。
