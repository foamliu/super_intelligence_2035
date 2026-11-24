# r1158 — 判分契约 helper 类别收口（11-24 运维令 · 续 r1157）

**轮次**：r1158 (2026-11-24, shard B)
**触发**：r1157 MEMORY 记「下轮 helper(最大类) 按 §3.5 wrap」+ 11-24 运维令判分契约修复
**结果**：helper 类别 36 case 审计 → 5 真违规(已修) + 3 false-positive(已合规) + 28 audit 误报(已合规)；5 cases/B JSON test 字段同步

## 1. 选料与方法

fresh 池仍耗尽（r1125+ 连续 0-case），按 11-24 运维令转判分契约修复，治 helper 类别（r1157 MEMORY 标注 36 case，最大类）。

写 `/tmp/resolve_helpers.py`：AST 解析每个 helper 函数的 return 形状（不只是 check() 末行），区分真违规 vs audit 静态误报。判据：helper 实际 return `True`/`False`/`dict含pass|ok`/`boolop`/`ifexp` ⇒ 已合规（audit 误报）；return `list`/`str`/`tuple`/`None`/`var未解析` ⇒ 真违规。

## 2. 审计结果（36 helper case）

### 2.1 真违规 5 case（check() 实际返回 list/str）

| case | 违规形状 | 修法 |
|---|---|---|
| AOI21ArcChar-001 | `check()` 末 `return results`(list of 3-tuple) | `return all(s == PASS for _, s, _ in results)`（与 __main__ exit 判据等价） |
| PVTalterChar-001 | 同上（3 处 `return results`） | 同上 |
| DelaySigma-001 | `check()` 返回 list(2-tuple)；__main__ 迭代该 list | wrap: rename `check`→`_check_impl`(返 list) + 新 `check()` 返 `all(ok for _, ok in res)` + `_main` 改调 `_check_impl` |
| SpGen-001 | 同 DelaySigma | 同上 wrap |
| PvtDeckGen-001 | `_summarize` 返 str `"check PASSED..."` | `print(...); return True`（raise 路径不变=FAIL） |

### 2.2 false-positive 3 case（helper 返 bool + raise，已合规）

- LvlShftSoaSizing-001：`_finalize_l` 返 `result = all(...)`(bool) + 失败 raise AssertionError ⇒ check() 返 True/raise = 合规
- SaCoreMosLocate-001：`_check_inner` 返 True / 失败 raise ⇒ 合规
- Vvdd2cStimRewriteProduce-001：`_finalize` 返 `{"pass": bool, ...}` ⇒ 合规

### 2.3 audit 静态误报 28 case（helper 返 True / dict-pass）

`_summarize`/`_check_inner`/`_check_impl`/`_finalize`/`run_check` 等返 `True` 或 `{"pass":bool,...}`，audit 无法静态解析 ⇒ 标「需人工查」但实际合规。含 BiasOpAnalysis/ClampPwrStateExtract/CmdEdgeMeasGen/CpIcpChar/DelayedBmatrixSched/DffSetupHoldChar/LatchSubcktLocate/LvlshftBsubDiag/McRonMismatch/MeasExtractCornerTrace/MosComparaReportGen/Mt0ParseFix/NetlistChlMirrorDiff/OtaAcReport/PVTvarSpecJudge/SimConfigEditReport/SizingSensDiag/SlicerSizingOpt/SpiceFloatPortDetect/SramPortExplainQA/StimLoopComplianceFix/ThoxVthExtract/TimingMeasGen/Tr0JitterRemeas/UlvtGmCharAnalyzer/Vcc2scPVTvar/VerdiFsdbLoadDiagnose/WvFmFreqExtract。

## 3. 并发碰撞与 central fix

本轮编辑 5 reference check.py 后 `git diff` 无输出 ⇒ HEAD 已含相同修复。查 git log：commit `ff874a710`（paul.liu / zhulong, 2026-11-24 18:19:59, msg "designflow shard C bench-shardC"）已对同样 5 个 reference check.py 施加**完全相同**的修法（AOI21 `return all(...)` / DelaySigma+SpGen wrap / PvtDeckGen `print+return True`）。

⇒ 本轮 reference 编辑为 no-op（HEAD 已修）。**真实交付 = cases/B JSON test 字段同步**（central commit 未触 cases/B）：5 JSON 的 `test` 字段从旧 check.py 源码更新为修后 check.py 源码（test==ref_now=True, test==HEAD=False）。

## 4. 验证

- **AST**：5/5 check.py ast.parse OK；check() return shape = `all()->bool`（AOI21/PVTalter/DelaySigma/SpGen）/ `call:_summarize`→True（PvtDeckGen）。3 false-positive AST 确认 helper 返 True/dict-pass。
- **import 逻辑测**：5/5 `check("/nonexistent/submit.zip", tmp)` 全部 raise（FileNotFoundError/AssertionError）= FAIL（合规，missing 输入应 FAIL 而非返 list/str）。
- **PvtDeckGen 完整 selftest**（无 hspice 依赖）：ref `check()` 返 `True`（16/16 PASS）+ 5 negatives（empty_shell/print_expected/hardcoded_A/core_deleted/no_alter_sep）全 FAIL，NEG_RC=5/5。§4.9 三假（empty_shell/print_expected/core_deleted）全 FAIL ✓。
- **AOI21ArcChar selftest**：本地无 hspice ⇒ negatives FAIL-as-expected（exception=FAIL）；ref 因 hspice 缺失无法跑全。语义等价性由「`return all(s==PASS...)` 与原 __main__ `sys.exit(0 if all(s==PASS...) else 1)` 判据完全一致」保证。
- **audit**：shard B VIOL 73→70（−3 净；4 case VIOL→OK + PvtDeckGen 静态误报残留，同 r1157 PwlStimTransform 模式）；OK 518→522（+4）。

## 5. 纪律遵守

- ✅ 只改返回值形状（list→bool, str→True），不改断言逻辑/条数/严格度
- ✅ 不改 case 的 prompt/assets/hidden
- ✅ DelaySigma/SpGen wrap 保留 __main__ pretty-print（改调 _check_impl），不断言逻辑变化
- ✅ 并发安全：共享工作树他 shard WIP 不触；显式路径 add 仅 stage 5 cases/B JSON
- ✅ 不碰任何 *.jsonl（运维令 2026-11-23）
- ✅ 不碰别 shard 文件

## 6. 剩余违规与下轮

剩 VIOL 70：helper 静态误报残（PvtDeckGen + 28 audit 误报，实际合规，audit 工具局限）+ var Pattern B 15（r1157 留）+ none_bare 12 + list 6 + ternary 2 + compare 1 + other 1。下轮建议：var Pattern B 15（`return results` 无 raise + __main__ all()，同 DelaySigma/SpGen wrap 模式）。

台账 B 不动（1769: case 597/parked 1172）。covered=597/4529=13.2%。fresh 池仍耗尽。
