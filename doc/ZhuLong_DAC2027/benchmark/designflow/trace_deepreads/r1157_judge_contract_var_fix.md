# r1157 — 判分契约 var 类别收口轮 (11 case)

**日期**: 2026-11-24
**背景**: 11-24 运维令判分契约治理续。r1156 收口 dict_other(30 case) 后剩违规 var39>helper36>none_bare12>list6>ternary2>compare1。本轮治 var 类别。

## var 类别细分

audit `--shard B` 起始 VIOLATION=84。var 类(裸变量 return: `return msg`/`return results`/`return ok`/`return summary` 等)细分两 pattern:

- **Pattern A (11 case)**: check() 末尾 `return msg`/`return summary`/`return ok`，**失败路径 raise AssertionError**(或 `if nfail: raise`)，故 `return msg` 仅在全过时到达 → str return 新契约下误判 FAIL。修法: `return msg`→`return True` / `return summary`→`return True` / `return ok`→`return bool(ok)`(语义等价: raise=FAIL, return True=PASS)。
- **Pattern B (15 case)**: check() `return results`(list/dict)，无 raise，__main__ 用 `all(ok for ...)` 判。需 wrap 成 `{'pass':all_ok,...}` 并改 __main__ 提取 → 留 r1158+。

## 本轮修的 11 case (Pattern A)

| case | 旧 return | 新 return | fail path |
|---|---|---|---|
| BuildStepCacheClassifyProduce-001 | return msg | return True | if nfail: raise |
| Mt0CornerPivotAggregate-001 | return msg | return True | if nfail: raise |
| QuotedUnitValueNormalize-001 | return msg | return True | if nfail: raise |
| SenseMarginBlBatchSpecProduce-001 | return msg | return True | if nfail: raise |
| SramWmRmMeasGenProduce-001 | return msg | return True | if nfail: raise |
| Mt0MeasureStat-001 | return msg | return True | if passed<total: raise |
| SimCapLisParse-001 | return msg | return True | if passed<total: raise |
| LpfAnomalyDetect-001 | return msg | return True | if failed: raise |
| SlicerSweepFomOpt-001 | return msg | return True | if failed: raise |
| SpiceCfgDirMerge-001 | return summary | return True | if passed!=len: raise |
| Mt0MeasDiag-001 | return ok | return bool(ok) | ok=all(...) bool 已合规, 显式化消 audit var flag |

每 case 同步改 reference/check.py + cases/B/<case>.json test 字段(22 file)。

## 验证

- **audit**: VIOLATION 84→73(-11 精确), OK 507→518(+11), NO_RETURN 0, PARSE_ERROR 1(Tr0TrTfMeas pre-existing 非本类)。11/11 从 VIOLATION 列表消失。
- **AST**: 11/11 ast.parse OK; 11/11 check() 末 return 为 True/bool(ok); 11/11 cases/B test==reference 同步。
- **§4.9 ref+selftest** (4 case 抽验, 代表性覆盖两种 fail-path 形式 + 嵌套 try/finally):
  - Mt0CornerPivotAggregate-001: neg_selftest REF PASS(True) + 3 neg FAIL ✓
  - SimCapLisParse-001: neg_selftest NEG_RC=0(6 neg 全 FAIL, 6 distinct first-FAIL label) ✓
  - Mt0MeasDiag-001: neg/negative_selftest 5 neg 全 FAIL + ref check 直接跑 ALL PASS ✓
  - SpiceCfgDirMerge-001: neg_selftest NEG_RC=0(6 neg 全 FAIL, distinct labels a/c/f/h/j/l, n_PASS_BAD=0) ✓
- **断言逻辑/条数/严格度**: 0 改动(仅 return 形状: str/bool-var → True/bool())。
- **prompt/assets/hidden**: 0 改动。

## 剩违规 (r1158 起点)

```
helper: 36   # 辅助函数透传 _summarize/_finalize/_summary/_result/_cond/_check_impl 等
var: 15      # Pattern B: return results(list/dict) 需 wrap
none_bare: 12
list: 6
ternary: 2
compare: 1
other: 1   # PwlStimTransform-001 已合规({'pass':...}), audit heuristic 误报 COND 变量
```

下轮优先: helper(36, 最大类) — 按 §3.5 wrap 辅助函数返回值。Pattern B var(15) 需逐个看 negative_selftest 对 check() 返回值的依赖, 决定 wrap 策略。

## 并发安全

共享工作树 144 modified(他 shard B/C/D WIP)。显式路径 `git add` 仅 stage 本轮 22 file(11 ref check.py + 11 cases/B JSON), 零交叉。

## 提交

- EDA-Flow-Bench master: 22 file
- super_intelligence_2035 main: MEMORY_DESIGNFLOW_B.md + 本 deepread
