# r1159 — 判分契约 var Pattern B 收口（11-24 运维令 · 续 r1158）

**轮次**：r1159 (2026-11-24, shard B)
**触发**：r1158 MEMORY 记「下轮 var Pattern B 15（`return results` 无 raise + __main__ all()，同 DelaySigma/SpGen wrap 模式）」+ 11-24 运维令判分契约修复
**结果**：15 var Pattern B case 全部 wrap；并发碰撞 central commit `51411495a`（shard D, 18:39:51）已对 15 reference check.py 施完全相同 wrap ⇒ 本轮 reference 编辑 no-op；**真实交付 = 5 negative_selftest.py 调用方修复 + 15 cases/B JSON test 字段 sync**

## 1. 选料与方法

fresh 池仍耗尽（r1125+ 连续 0-case），按 11-24 运维令续 r1158 转判分契约修复，治 var Pattern B 15（r1158 MEMORY 标注的下一类别）。

写 `/tmp/resolve_var_patternB.py`：AST 解析每个 case 的 `check()` 函数返回形状（不只看末行）。15/15 判 REAL VIOLATION（check() 末 `return results`/`return FAILS`，返回 list/dict 而非 bool）。

## 2. 15 case 的 results 结构与 reduction

| 结构类别 | case | reduction |
|---|---|---|
| list `(name, ok)` | CharRemovalAbort / InvTripDelay / NetlistStaticCheck / OpampChar | `all(ok for _, ok in res)` |
| list `(key, PASS/FAIL, detail)` | CTLESpec / PlatSweepGen | `all(s == PASS for _, s, _ in res)` |
| list `(name, passed, detail)` | ConlyPinDropDiagProduce / FinesimMt0ParserProduce | `all(p for _, p, _ in res)` |
| list `(letter, ok, msg)` | VcoBiasAcStbGen | `all(ok for _, ok, _ in res)` |
| dict key→bool | CabufPvtDatAudit / CtleAcChar / GmidLutRunSelect | `all(res.values())` |
| dict key→(bool, msg) | McVoltMarginSummary | `all(p for p, _ in res.values())` |
| dict key→(PASS/FAIL, why) | FineSimStimSweepFix | `all(st == 'PASS' for st, _ in res.values())` |
| list of failures (FAILS) | CTLEtranChar | `len(res) == 0` |

每个 reduction 与原 `_main`/`check_and_report` 的 exit-0 判据逐一对齐（如 CTLESpec `npass==len` ⟺ `all(s==PASS)`；McVoltMarginSummary 两条早退路径均填满全部 CONDITIONS 键 ⟺ `all(p for p,_ in res.values())` 安全）。

## 3. wrap 方法（同 r1158 DelaySigma/SpGen）

`/tmp/wrap_var_patternB.py` 对 15 reference check.py：
1. `def check(deliverable, workdir):` → `def _check_impl(deliverable, workdir):`
2. 内部调用方 `check(` → `_check_impl(`（main / check_and_report / __main__，正则 `(?<![A-Za-z0-9_])check\(` 不误伤 `_check_impl(` / `check_and_report(`）
3. 在 `def main` / `if __name__` 前插入新 `def check(deliverable, workdir): return <reduction>`
4. ast.parse 校验 + `def check`/`def _check_impl` 各恰 1 个

## 4. 并发碰撞与 central fix

本轮编辑 15 reference check.py 后 `git diff` 全部为空 ⇒ HEAD 已含相同修复。查 git log：commit `51411495a`（designflow shard D bench-shardD, 2026-11-24 18:39:51）已对同样 15 个 reference check.py 施加**完全相同**的 wrap（rename + 新 check() 返 all()/len()==0）。

⇒ 本轮 reference 编辑为 no-op（HEAD 已修）。**真实交付**：
- **5 negative_selftest.py 调用方修复**（central commit 未触）：central commit 把 check() 改成返 bool，但 negative_selftest.py 仍调用 `chk.check(...)` 并对结果做 list/dict 迭代（pretty-print），wrap 后 `chk.check()` 返 bool 导致 `'bool' object is not iterable` / `has no attribute 'values'`。修法：5 个 selftest 的 `chk.check(` / `CHK.check(` / `check.check(` → `chk._check_impl(` / `CHK._check_impl(` / `check._check_impl(`（CharRemovalAbort / GmidLutRunSelect / InvTripDelay / OpampChar / VcoBiasAcStbGen）。FineSimStimSweepFix selftest 依赖 `check()` raise（_check_impl 仍 raise），无需改。
- **15 cases/B JSON test 字段 sync**（central commit 未触）：15 JSON 的 `test` 从旧 check.py 更新为 wrap 后 check.py（test==ref_now True / test==HEAD-pre-central False）。

## 5. 验证

- **AST**：15/15 check() return shape = `all()->bool`（14）/ `Compare len()==0`（CTLEtranChar，bool）；_check_impl 仍返 list/dict（被 check() 包一层）。
- **missing-input 烟测**：15/15 `check("/nonexistent/submit.zip", tmp)` 全部返 False 或 raise（FAIL 合规），无任何返 list/dict/str。
- **empty-zip 烟测**（list/dict 类防 vacuous-pass）：8/8（CTLESpec/PlatSweepGen/ConlyPinDropDiagProduce/FinesimMt0ParserProduce/NetlistStaticCheck/InvTripDelay/McVoltMarginSummary/CTLEtranChar）`check(empty_zip, tmp)` 全部返 False ⇒ 无 `all([])==True` 空洞。
- **negative selftest**（本地可跑、无 hspice 依赖者）：
  - CharRemovalAbort: 4/4 negs FAIL（三假齐）✓
  - GmidLutRunSelect: 4/4 negs FAIL ✓
  - VcoBiasAcStbGen: **REF 13/13 PASS** + 4/4 negs FAIL ✓（完整 selftest 通过）
  - OpampChar: 6/6 negs FAIL ✓
  - FineSimStimSweepFix: 5/5 negs FAIL（NEG_RC=5/5，依赖 _check_impl raise）✓
  - CabufPvtDatAudit: 4/4 negs FAIL（NEG_RC=0）✓
  - InvTripDelay: 需 .75 hidden B assets + hspice，本地不可跑（环境限制，非本轮引入）；改法与 CharRemovalAbort/OpampChar 同（`(name,ok)` list + `all(ok for _,ok in res)`），等价性已由同类验证。
- **ref-PASS 本地验证**：CTLESpec/CtleAcChar/CabufPvtDatAudit/GmidLutRunSelect/OpampChar/PlatSweepGen/CTLEtranChar 的 ref-PASS 需 HSPICE + 特定 asset 布局（eval framework 在 .75 上 setup），本地不可跑；语义等价性由「reduction 与原 _main exit-0 判据逐一对齐」+ VcoBiasAcStbGen 完整 selftest（REF 13/13 PASS）保证。
- **test 字段 sync**：15/15 cases/B JSON `test ==` reference check.py（hash 一致）。
- **audit**：shard B VIOL 数静态不变（70）：15 case 的 `_check_impl` 仍 `return results`，audit 静态解析不了 wrap ⇒ 同 r1158 helper 28 audit 误报模式（实际合规，audit 工具局限）。OK 数不变。

## 6. 纪律遵守

- ✅ 只改返回值形状（list/dict→bool via wrap）+ 调用方接线，不改断言逻辑/条数/严格度
- ✅ 不改 case 的 prompt/assets/hidden
- ✅ wrap 保留 _main/__main__ pretty-print（改调 _check_impl），不断言逻辑变化
- ✅ 并发安全：显式路径 add 仅 stage 5 selftest + 15 cases/B JSON，零交叉他 shard WIP
- ✅ 不碰任何 *.jsonl（运维令 2026-11-23）
- ✅ 不碰别 shard 文件 / eval/run_one.sh / 其他 cases/B JSON（BisecMt0SmCalc 等他方修改）

## 7. 剩余违规与下轮

剩 VIOL 70（audit 静态口径）：var Pattern B 15（本轮 wrap，audit 误报残）+ helper 静态误报残 28+1 + r1158 5 wrap 误报残 + none_bare 12 + list 6（DbcVaractorSpTestGen/DutySkewAvg/Dvohdv2ZqRefFix/HcellNetlistXcross/SanadjRblDeckSweep/SpLibIncTokenRewrite）+ ternary 2（DOERankBuild/SpBisecDeckGen）+ compare 1（PwlFormatConvert）+ other 1（PwlStimTransform var:COND）+ NO_CHECK_FN 6 + PARSE_ERROR 1。

下轮建议优先级：① none_bare 12（无 return→补 `return True`，r1155 同法，需逐个看是否有早退 return None 需改 False）② list 6（`return list/errors`，同 r1158 helper wrap 模式 `all(...)`，但需查 list 元素是否为 bool 还是 tuple）。两类均为「修后从 FAIL 变 PASS」收益类（11-24 运维令优先级 3）。

台账 B 不动（1769: case 597/parked 1172）。covered=597/4529=13.2%。fresh 池仍耗尽。
