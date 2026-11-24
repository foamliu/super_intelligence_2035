# r1164 — 判分契约 parse_error 收口：Tr0TrTfMeas-001

**日期**：2026-11-24
**轨道**：判分契约修复（11-24 运维令 · 续 r1162，与 r1163 造题轨并行）
**case**：EDA-Eval-DesignFlow-Tr0TrTfMeas-001（shard B / spice_sim）

## 背景

`audit_check_returns.py --shard B` 发现 1 个 PARSE_ERROR：
```
EDA-Eval-DesignFlow-Tr0TrTfMeas-001  PARSE_ERROR  SyntaxError: unmatched ')' (<unknown>, line 157)
```
该 case 的 check.py 完全无法解析 → check() 永远无法执行 → 任何交付件都被判 FAIL（包括参考解）。这是比 return-shape 违规更根本的缺陷。

## 根因

check.py 中 4 处 `_cond(...)` 调用的 msg 参数末尾多了一个 `)`：

| 行 | 条件 | 原结尾 | 修后 |
|:--:|:--|:--|:--|
| 157 | (f) v(sclk tr (B) | `GT_B["signals"]["v(sclk"]["tr"])))` | `["tr"]))` |
| 160 | (g) v(sclk tf (B) | `GT_B["signals"]["v(sclk"]["tf"])))` | `["tf"]))` |
| 179 | (k) cross-input A v(sclk tr | `GT_A["v(sclk"]["tr"])))` | `["tr"]))` |
| 184 | (l) interpolation A v(sfast tr | `GT_A["v(sfast"]["tr"])))` | `["tr"]))` |

结构应为 `_cond("f", _close(...), "msg" % (a, b))`：末尾 `))` = ① 闭 tuple `(a, b)` ② 闭 `_cond(`。实际写成 `)))`，多一个 `)`。

同时发现 return-shape 违规：line 202 `return "PASS"`（str），按契约 §3.2 应为 `return True`。

## 修复（只改返回值形状 + 语法 typo，不改断言逻辑）

1. 4 处 `])))` → `]))`（删多余 `)`，纯语法修复，断言条件 `_close(...)` 比较逻辑零改动）
2. `return "PASS"` → `return True`（str → 契约合规）
3. `__main__` 块未动：`print(check(d,w))` 现打印 `True`；AssertionError 仍 `sys.exit(1)`。negative_selftest.py 用 `rc==0` 判 PASS / `rc!=0` 判 FAIL，return True 保持 rc 行为不变。

同步修改两处（保持一致）：
- `benchmarks/EDA-Eval-DesignFlow/reference/EDA-Eval-DesignFlow-Tr0TrTfMeas-001/check.py`
- `benchmarks/EDA-Eval-DesignFlow/cases/B/EDA-Eval-DesignFlow-Tr0TrTfMeas-001.json` 的 `test` 字段

## 验证

- ✅ `ast.parse` OK（两文件）
- ✅ `py_compile` OK（reference check.py）
- ✅ `audit_check_returns.py --shard B`：`PARSE_ERROR 1→0`，`OK 591→592`，该 case shape=`['True']`
- ✅ JSON `test` 字段 == reference check.py（byte-identical after strip）
- ✅ `test_rationale` 14 条断言（a-n）未变；`_cond` 标签 16 处（a×3 + b-n）未变
- ✅ 断言逻辑 / 条数 / 严格度 0 改；prompt / assets / hidden 0 改
- ⏸ live selftest（negative_selftest.py）需 hspice + 完整 bench 结构在 .75，预算内不可行；static 验证已结论性（纯语法修复，rc 契约保持）

## 另发现（DEBT，未修）

6 个 NO_CHECK_FN case（audit 报 `no def check() found`）：
- HspiceMeasProbeGuide-001（fns: fail/condition/run_check）
- HspiceSparamSubmit-001（fns: cond/run/cand_run/ref_run/load_report/main）
- IddStimHowtoGuide-001（fns: fail/condition/run_check）
- LatchResetFomSweep-001（fns: record/fail/ok/main/finish/w_match）
- PsijCalc-001（fns: cond/run/ref_psij/cand_psij/main）
- SimlibMatchAnalyze-001（fns: _cell_part/.../oracle_match/fail/cond/run_check）

这些 case 的 test 字段用 `run_check` / `main` 而非 `def check(deliverable, workdir)`，属结构性问题（函数命名不符契约），非 return-shape 范围。按 JUDGE_CONTRACT.md §7「如果发现某个 case 的断言逻辑本身有 bug，单独记下来交回讨论」，本轮记 DEBT 待讨论，不顺手改。

## 台账

无新 claim/mark（判分契约修复轮，不造题）。台账 B 不动（1769：case 597/parked 1172）。covered=597/4529=13.2%。
