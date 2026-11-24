# Anti-Hardcode Audit — shard D 第 r1249 批（2026-11-24）

> 用户令 §4.9 全 bench anti-hardcode 普查 · D 自有 case 抽样续批。
> 本批聚焦 D 域 unaudited 中 k<12 的优先(老/弱)题，共 5 条。

## 本批结果（5 条）

| case_id | k_check | 判定 | 处置 |
|---|---|---|---|
| EDA-Eval-DesignFlow-FsdbWaveformParseAnalyzeProduce-001 | 10 | PASS | 手动审计 3 fake 全 FAIL；缺 negative_selftest.py(建议补) |
| EDA-Eval-DesignFlow-SpiceUndefParamScan-001 | 16 | **GAP→已修→PASS** | check() 返回 dict 不 raise→5 fake 全 PASS；r1249 加 `_fail()` helper + 3 处 raise，修复后 REF 16/16 PASS + 5 neg 全 FAIL |
| EDA-Eval-DesignFlow-SaNPTrannoiseFix-001 | 11 | PASS | selftest OK（neg 在 ref 顶层非 negative/ 子目录但齐全）|
| ParasiticsAnnotDiag-001 | 9 | **GAP** | cases/D 有 json 但 reference/ 无目录→dangling/incomplete，无法评测 |
| EDA-Eval-DesignFlow-CompressNetlistToggle-001 | 11 | **GAP** | 同上 dangling/incomplete |

## 关键发现：SpiceUndefParamScan-001 §4.9 GAP（已修复）

**问题**：`check(deliverable, workdir)` 契约要求 PASS 返回 None、FAIL raise AssertionError。原 check.py 在 3 处 `return results`（返回 dict）而不 raise，导致 5 类假提交（core_deleted/empty_shell/fake_hardcode_b/hardcode_a/print_only）**全部通过 check() 调用无异常**——即假提交判 PASS，违反 §4.9 (a)(b)(c) 与 §4.3（独立条件须可 FAIL）。

**根因**：check.py 用 `__main__` 块的 `sys.exit(0 if all(res.values()) else 1)` 做失败信号，但 evaluator 调的是 `check()` 函数本身（不看 sys.exit），所以函数层无失败信号。

**修复**：新增 `_fail(results)` helper（raise AssertionError 列出 failed keys），在 3 处 `return results` 前调用：
1. early return（no SUT，conds b-p=False）
2. early return（no A report，conds d-p=False）
3. final return（OVERALL FAIL）

**验证**：
- REF solution `find_undefined_params.py`：`OVERALL: PASS (16/16)`，check() 返回 None ✓
- 5 neg 全 FAIL：core_deleted(5/16) / empty_shell(2/16) / fake_hardcode_b(12/16) / hardcode_a(10/16) / print_only(5/16) ✓
- `negative_selftest.py`：`NEG_RC=0` ✓

## dangling/incomplete case（2 条）

`ParasiticsAnnotDiag-001` 与 `EDA-Eval-DesignFlow-CompressNetlistToggle-001`：cases/D/ 有 json（含 test_rationale 断言清单）但 reference/ 无对应目录，无法评测。属 §3 "未过闸门的 case"——不应计入通过率。建议：补 reference/check.py+negative，或标 incomplete 移出 cases/。

## 累计 D 审计进度

- D 审计 TSV 累计 25 行（本批 +5）
- GAP 修复：1（SpiceUndefParamScan-001，本批修复）
- GAP 待处置：2（dangling case，无 reference/）
- 其余 PASS

## 复现命令

```bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow
# SpiceUndefParamScan-001（已修）
cd reference/SpiceUndefParamScan-001 && python3 negative_selftest.py
# SaNPTrannoiseFix-001
cd reference/EDA-Eval-DesignFlow-SaNPTrannoiseFix-001 && python3 negative_selftest.py
# FsdbWaveform（手动）
REF=reference/EDA-Eval-DesignFlow-FsdbWaveformParseAnalyzeProduce-001
for f in $REF/negative/*.py; do z=$(mktemp -d); cp $f $z/solver.py; (cd $z && zip -q submit.zip solver.py); python3 -c "import sys;sys.path.insert(0,'$REF');from check import check
try: check('$z/submit.zip','.'); print('PASS(BAD)')
except: print('FAIL(ok)')"; rm -rf $z; done
```
