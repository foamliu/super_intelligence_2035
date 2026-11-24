# r1162 — 判分契约 5 收口（11-24 运维令 · 续 r1161）

## 背景
r1161 收口 list+compare 8 后，official audit (`audit_check_returns.py --shard B`) 仍报 VIOL 5。
本轮目标：清零剩余 5 VIOL。

## 5 case 修复（return-shape only，断言逻辑/条数/严格度 0 改）

| case | 违规形状 | 修法 |
|:--|:--|:--|
| DOERankBuild-001 | `ternary(number/number)` | `return 0 if npass==len else 1` → `if npass==len: return True else: return False`；`__main__` `sys.exit(check(...))` → `sys.exit(0 if check(...) else 1)`（保持 exit code 语义：0=成功） |
| SpBisecDeckGen-001 | `ternary(number/number)` | 同 DOERankBuild |
| PwlStimTransform-001 | `return COND`(variable, 2处) | `return COND` → `return all(ok for _, ok, _ in COND)`(bool_call)；JSON test sync，ref r1159 已是 `{'pass':bool(COND) and all(...)}`(dict-pass-ok) 仅 JSON 落后 |
| LvlShftSoaSizing-001 | `_finalize_l` `return result`(variable, helper 透传 5 处) | `return result` → `return True`（fail path raise 不变，到达 return 时 result 必为 True） |
| Vvdd2cStimRewriteProduce-001 | `_finalize` `return result`(variable, helper 透传 9 处) | `return result` → `return {"pass": result["pass"], "k": K, "passed": passed, "conditions": result["conditions"]}`(dict-pass-ok) |

## 同步
- JSON `test` 字段（judge 实际用）：5 case 全部修改
- reference/check.py：4 case 修改（PwlStimTransform ref r1159 已 compliant，无需改）

## 验证
- `ast.parse(test)` + `py_compile.compile(ref check.py)`：5/5 OK
- official audit B：VIOL 5→0 / OK 586→591 / NO_CHECK_FN 6 / PARSE_ERROR 1（预存在，非本轮 5 case）
- SpBisecDeckGen negative_selftest：6 negs 全 FAIL（naive_empty/hardcoded_a/sh_loop/only_measure/ref_core_deleted/bisection_for_opt）✓
- PwlStimTransform negative_selftest：5 negs 全 FAIL（empty/print_expected/hardcode_a/no_clip/wrong_rail）；ref 11/12（k=L2 hspice 本地无，预存在环境限制，非本轮引入）✓
- §4.9 三假：SpBisecDeckGen negselftest 含 ref_core_deleted FAIL ✓；PwlStimTransform 含 empty/print_expected FAIL ✓

## 不改
- 断言逻辑、断言条数、判分严格度：0 改
- prompt / assets / hidden：0 改

## 语义说明
PwlStimTransform 的 `return COND`(list) 在旧 truthy-judge 下 = 恒 PASS（list 非空），在新契约下 = 恒 FAIL（list 非 PASS 形状）。改为 `return all(ok...)` 后正确返回 verdict：全 pass→True，否则→False。这是必要修复（旧返回是 latent bug）。

## 指标
- 台账 B：不动（1769: case 597 / parked 1172）
- covered = 597/4529 = 13.2%
- 🎯 最近20条 20/20=100%（观察值，未 pi 实跑）
- DEBT: 0
- fresh 池仍耗尽
