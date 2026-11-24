# r1161 (11-24 19:1x–19:4x) — 判分契约 list+compare 8 收口

续 r1160 治 none_bare 12（11-24 运维令）。本轮治 **list 6 + Compare 2 = 8 case**。

## 发现：official audit ≠ audit_ref.py

- `audit_ref.py`（读 `reference/<id>/check.py`）报 37 VIOL，但很多 reference/check.py 是 **stale**（前轮修了 JSON `test` 字段但没同步 reference/check.py）。
- `scripts/audit_check_returns.py --shard B`（读 `cases/B/*.json` 的 `test` 字段 = judge 实际用的）才是权威。official B 真实违规远少于 37。
- **judge 用 JSON `test` 字段**，reference/check.py 仅供 selftest 本地跑。

## 关键发现：audit 不认 `ast.Compare`

`return len(errors) == 0` 是 `ast.Compare`，audit `_classify_return` 无 Compare 分支 → 落 "other" → 非 success-capable → VIOLATION。
- r1159 var Pattern B 用 `len()==0` 包的 case 全是此坑（CTLEtranChar/PwlFormatConvert 本轮修）。
- 正确写法：`return not <list>` → `ast.UnaryOp(Not)` → audit 认 "not"（success-capable）。`not []`=True / `not [x]`=False，语义等价 `len()==0`。

## 8 case 修法

### 5 uniform list-wrap（errors-list 模式）
- DbcVaractorSpTestGen / Dvohdv2ZqRefFix / HcellNetlistXcheck / SanadjRblDeckSweep / SpLibIncTokenRewrite
- 修法：`def check` → `def _check_impl`；插 wrapper `def check(d,w): return not _check_impl(d,w)`；`__main__` 里 `check(`→`_check_impl(`（保 3 个 selftest 解析 stdout "  - <msg>" 错误明细）
- selftest 5/5 全 PASS（ref PASS + negs FAIL）；§4.9 三假（empty/print_only/core_removed）抽 HcellNetlistXcheck 验全 FAIL ✓

### DutySkewAvg（str 返回）
- 末尾 `return report`（str，成功路径；失败路径 `raise AssertionError`）→ `return True`
- L92 `return [_cond(...)]`（fail 路径，list=FAIL 合规）不动（audit 只要有 1 个 success-capable 即 OK）
- selftest 有**预存在 path bug**（`HERE/reference/CASE` 双层嵌套），非本轮引入；直接跑 check.py on ref_submit → `True` exit0 ✓

### 2 Compare（r1159 var-B 遗留 len()==0 坑）
- CTLEtranChar L228 `return len(res) == 0` → `return not res`
- PwlFormatConvert L256 `return len(failures) == 0` → `return not failures`
- CTLEtranChar selftest 需 hspice 本地无（预存在，非本轮引入）；PwlFormatConvert 无 selftest，直跑 check on ref → exit0 PASS ✓

## 验证

- 8/8 cases/B JSON `test` == reference/check.py 字节级一致
- official audit B: OK 578→586 / VIOL 13→5（+NO_CHECK_FN 6 + PARSE_ERROR 1 不变）
- 断言逻辑/条数/严格度 0 改；prompt/assets/hidden 0 改

## 剩违规 5（official, JSON test）
1. DOERankBuild — `ternary(number/number)`
2. SpBisecDeckGen — `ternary(number/number)`
3. PwlStimTransform — `return COND`（变量）
4. LvlShftSoaSizing — `return _finalize_l(...)` helper 返 variable
5. Vvdd2cStimRewriteProduce — `return _finalize(...)` helper 返 variable

下轮：ternary 2（`return X if cond else Y` 两分支 number→改 bool）> variable/helper 3（需查 helper 返形状）。

## 另：reference/check.py stale 同步债
audit_ref.py 报 37 VIOL vs official 5 VIOL → ~32 case 的 reference/check.py 落后于 JSON test。下轮可批量 sync（reference ← JSON test）清此债。

## 指标
- 台账 B 不动（1769: case 597/parked 1172）
- 📊 covered=597/4529=13.2%（mc≥10，不变）
- 🎯 最近20条 20/20=100%（观察值，未 pi 实跑）
- 📦 MEMORY_B<32KB ✓
- DEBT:0
