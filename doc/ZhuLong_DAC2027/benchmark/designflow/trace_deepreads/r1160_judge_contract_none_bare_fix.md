# r1160 — 判分契约 none_bare 12 收口（11-24 运维令 · 续 r1159）

**轮次**：r1160 (2026-11-24, shard B)
**触发**：r1159 MEMORY 记「下轮 none_bare 12（无 return→补 `return True`，r1155 同法，需逐个看是否有早退 return None 需改 False）」+ 11-24 运维令判分契约修复
**结果**：12 none_bare case 全部修复；audit OK 537→549 / VIOL 55→43（-12）；reference check.py + cases/B JSON test 字段双 sync

## 1. 选料与方法

fresh 池仍耗尽（r1125+ 连续 0-case），按 11-24 运维令续 r1159 转判分契约修复，治 none_bare 12。

`/tmp/audit_ref.py`（基于 `scripts/audit_check_returns.py` 的 `audit_check_source`）扫 B shard 598 case，VIOLATION 55 中 12 条 detail 含 "bare return / return None" 或 "return None"。

12 条分两类：

### Group 1: bare-return + _emit/_summarize 模式（8 条）
check() 末尾 `_emit(results); return`（早退，_emit raise 致 return 为 dead code）+ 成功路径 fallthrough 返 None。

| case | bare return 数 | 成功路径 |
|---|---|---|
| CmpLogReportMod-001 | 4（inline `_fail;_emit;return`） | try/finally 内末 `_emit` |
| FloatingNetChecker-001 | 5（`_summarize;return` 两行） | try/finally 内末 `_summarize` |
| GenXtopCliUpgrade-001 | 3（inline `_emit;return`） | try/finally 内末 `_emit` |
| Mt0Reorg-001 | 1（`_fail;return` 两行，_fail 直接 raise） | 函数末尾（无 try/finally） |
| SpfAutosimSetup-001 | 1 | try/finally 内末 `_summarize` |
| StcCrfGenerator-001 | 1 | try/finally 内末 `_summarize` |
| TtCdlVVerdictGen-001 | 3（`_summary;return` 两行） | try/finally 内末 `_summary` |
| VlshftParamOpt-001 | 4（`_summarize;return` 两行） | try/finally 内末 `_summarize` |

### Group 2: return None 模式（4 条）
check() 末尾 `return None`（成功路径），失败全靠 raise/assert。

| case | return None 位置 | 失败机制 |
|---|---|---|
| FineSimPostsimDiag-001 | L242（`# PASS` 注释后） | `_fail(msg)` raise |
| LibMismatchFix-001 | L222 | `_cond(cid,ok,msg)` raise |
| SramTailorPlanClassify-001 | L193 | `raise AssertionError(...)` |
| TwoStageLogExplainQA-001 | L217（try/finally 后） | `assert` raise |

## 2. 修法（/tmp/fix_none_bare_12.py）

AST 解析每个 check()，prune nested FunctionDef/Lambda，收集 direct returns：

1. **bare `return`（value=None）→ `return False`**：早退路径（dead code，_emit/_summarize/_fail 已 raise），改 False 为契约合规防御。
   - inline 模式 `_emit(...); return` → `_emit(...); return False`
   - 两行模式 `_summarize(...)` + `return` → `return` 改 `return False`
2. **`return None`（Constant None）→ `return True`**：成功路径，改 True 使契约 PASS。
3. **无 success-capable return → 末尾加 `return True`**：Group 1 改完 bare 后仍无 success path，在 check() body 最后一条语句（try/finally 块或末尾条件）之后插 `return True`。
   - try/finally 结构：`return True` 插在 finally 块之后（函数体层级）——try 内 _emit raise 则异常传播（FAIL），try 完成→finally 清理→`return True`（PASS）。
   - 无 try/finally（Mt0Reorg）：`return True` 插在函数体末尾。

r1155 脚本 `has_real_return` 把 `return False` 当 real return 致不补 `return True`——本脚本改用 `has_success_path`（只认 True/dict-pass-ok/all/any/bool/boolop/not/合规 ternary），避免此坑。

## 3. 验证

- **AST**：12/12 check() 现有 success-capable return（`return True`）。
- **audit**：12/12 从 VIOLATION → OK。B shard 总：OK 537→549 / VIOL 55→43 / missing 6 不变。
- **missing-input 烟测**：12/12 `check("/nonexistent/submit.zip", tmp)` 全部 raise（AssertionError/FileNotFoundError）→ FAIL 合规，无 vacuous pass。
- **empty-zip 烟测**：12/12 `check(empty.zip, tmp)` 全部 raise → FAIL 合规。
- **negative selftest**（11/12 有 selftest；TwoStageLogExplainQA 无）：
  - CmpLogReportMod-001: 5/5 negs FAIL ✓
  - FloatingNetChecker-001: 4/4 negs FAIL ✓
  - GenXtopCliUpgrade-001: 5/5 negs FAIL ✓
  - Mt0Reorg-001: 需 .75 hidden B assets（hidden_b1_config.json 等），本地不可跑（既有环境限制，非本轮引入）；改法与同类 case 等价（_fail raise + 末尾 return True）。
  - SpfAutosimSetup-001: 3/3 negs FAIL ✓
  - StcCrfGenerator-001: 5/5 negs FAIL ✓
  - TtCdlVVerdictGen-001: 4/4 negs FAIL ✓
  - VlshftParamOpt-001: 3/3 negs FAIL ✓
  - FineSimPostsimDiag-001: 3/3 negs FAIL（NEG_RC=5/5）✓
  - LibMismatchFix-001: 4/4 negs FAIL ✓
  - SramTailorPlanClassify-001: 3/3 negs FAIL ✓
- **test 字段 sync**：12/12 cases/B JSON `test` == reference check.py（sha256 一致）。

## 4. 纪律遵守

- ✅ 只改返回值形状（bare return→False / return None→True / 加 return True），不改断言逻辑/条数/严格度
- ✅ 不改 case 的 prompt/assets/hidden
- ✅ 不碰任何 *.jsonl（运维令 2026-11-23）
- ✅ 不碰别 shard 文件 / eval/run_one.sh / 其他 cases/B JSON（工作树有并发 shard D 修改 SineScanStdout-001 等，显式路径 add 零交叉）
- ✅ TwoStageLogExplainQA 无 negative_selftest.py——本轮只修返回值形状，不补 selftest（11-24 运维令范围外）

## 5. 剩余违规与下轮

剩 VIOL 43（audit 静态口径）：
- helper 透传（`return _summarize(...)` / `return _summary(...)` / `return _finalize(...)` 等）：~22 条（最大类，r1158/r1159 wrap 模式不适用——这些 helper 返回 tuple/dict/str 需逐个查 helper 返回形状再包 reduction）
- list 返回（`return list` / `return errors`）：6 条（DbcVaractorSpTestGen/DutySkewAvg/Dvohdv2ZqRefFix/HcellNetlistXcross/SanadjRblDeckSweep/SpLibIncTokenRewrite）
- ternary：2 条（DOERankBuild/SpBisecDeckGen）
- compare（`return Compare(len(...)==0)`）：2 条（CTLEtranChar/PwlFormatConvert）——CTLEtranChar 已 r1159 wrap，audit 误报残
- var（`return COND`）：1 条（PwlStimTransform）
- NO_CHECK_FN：6 条（缺 check 函数，需补）
- PARSE_ERROR：1 条（Tr0TrTfMeas-001 语法错误）
- 其他 helper 透传误报残

下轮建议优先级：① helper 透传 ~22（逐个查 helper 返回形状，包 reduction 或改 helper 返 bool）② list 6（`return errors`→`len(errors)==0` / `return list`→`all(...)`）③ NO_CHECK_FN 6（补 `def check`）。helper 透传为最大类但需逐个人工查，list 6 模式固定可批量。

台账 B 不动（1769: case 597/parked 1172）。covered=597/4529=13.2%。fresh 池仍耗尽。
