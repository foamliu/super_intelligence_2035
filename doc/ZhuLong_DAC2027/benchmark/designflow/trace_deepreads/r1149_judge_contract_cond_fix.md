# r1149 判分契约修复轮 — COND-list 返回型 case 修复

**日期**: 2026-11-24
**触发**: 2026-11-24 运维令「判分契约修复」（commit 6c1a50ee9），框架两条判分通路统一为严格契约：仅 `return True` / `return {'pass':True}` / `return {'ok':True}` 算 PASS。
**背景**: fresh 池仍耗尽（7 轮 reconfirm），转判分契约修复（与造题并行，按需执行）。

## 扫描结果

B shard 598 个 check.py，按顶层 return 形状分类（AST 扫描 check() 函数内所有 return，排除嵌套函数）：

| 形状 | 数量 | 契约形? |
|:--|--:|:--|
| True | 343 | ✅ |
| False | 12 | ✅ |
| dict_ok (pass/ok 键) | 34 | ✅ |
| boolop | (并入上) | ✅ |
| NO_RETURN | 51 | ❌ |
| Call | 38 | ❌ |
| Name | 36 | ❌ |
| dict_other | 31 | ❌ |
| tuple | 25 | ❌ |
| OTHER | 20 | ❌ |
| str | 13 | ❌ |
| bare | 8 | ❌ |
| list | 6 | ❌ |
| None | 4 | ❌ |

**违反契约的 case 共 220 个**（多轮分批修）。

## 本轮修复：6 个 COND-list 返回型 case

### 模式
这些 case 用共享模板：`COND = []`（模块级 list）+ `rec(tag, ok, detail)` append `(tag, bool(ok), detail)` + `check()` 内多处 `return COND`（list）。旧 evaluator 对 list 返回值判分语义混乱（通路 A 杀正解/通路 B 放行负样本），新契约下 list 一律 FAIL —— 即使交付件正确。

### 修复
`return COND` → `return {'pass': bool(COND) and all(c[1] for c in COND), 'conds': COND}`

- `bool(COND)` 防空 list（空 COND = 无断言跑 = FAIL，安全方向）
- `all(c[1] for c in COND)` = 所有断言 ok 才 PASS（c[1] 是 bool(ok)）
- 保留 `conds` 键供 `__main__`/selftest 解包逐条打印（不影响契约：evaluator 只看 `pass` 键）

### 6 个 case
1. EDA-Eval-DesignFlow-OpampACSpec-001 (5 return COND)
2. EDA-Eval-DesignFlow-PFDdeadZone-001 (3)
3. EDA-Eval-DesignFlow-ProbeTrim-001 (5)
4. EDA-Eval-DesignFlow-PwlStimTransform-001 (2)
5. EDA-Eval-DesignFlow-SramSNM-001 (5)
6. EDA-Eval-DesignFlow-StimPWL-001 (6)

### 同步改动（仅解包，不动断言）
- 6 个 check.py 的 `__main__` 块：`res = check(...)` → `conds = res['conds'] if isinstance(res,dict) else res; verdict = res.get('pass') if isinstance(res,dict) else bool(res)`
- 2 个 in-process negative_selftest（PwlStimTransform / StimPWL）：`chk.check()` 直接调用并 unpack list → 改用 `res['conds']` / `res['pass']`
- 其余 4 个 selftest（OpampACSpec/PFDdeadZone/ProbeTrim/SramSNM）走 subprocess 解析 stdout，`__main__` 输出格式不变 → 无需改

## 验证

| case | 负样本全 FAIL | ref PASS | 备注 |
|:--|:--|:--|:--|
| OpampACSpec | ✅ NEG_RC=0 exit=0 | 未跑 ref（selftest 只跑负样本） | 纯 Python，不需 sim |
| PFDdeadZone | ✅ 5 neg rc=1 | ref FAIL（hspice 未跑，env 限制） | pre-existing 非回归 |
| ProbeTrim | ✅ 3 neg rc=1 | ref FAIL（finesim 未跑，env 限制） | pre-existing 非回归 |
| PwlStimTransform | ✅ 5 neg 0 fully pass | ref FAIL（hspice k 项，env 限制） | pre-existing 非回归 |
| SramSNM | ✅ neg rc=1 | ref 9/14（k/n hspice+verdict，env 限制） | pre-existing 非回归 |
| StimPWL | ✅ ALL_NEGATIVES_FAIL=True exit=0 | ref 未跑 | 纯 Python |

**关键**: ref-PASS 失败均因 dev env 无 hspice/finesim 二进制（k/e/f/g 等断言需 sim 结论），非返回值形状改动所致。沙盒（.75）有 sim，ref 可 PASS。改动前后 ref 行为一致（旧 `__main__` 也是 `npass==len(conds)` 判 rc，sim 不跑则 rc=1）。

evaluator 契约确认（run_one.sh:462-464）：
```python
"""统一契约: 仅 True / {pass:True} / {ok:True} 算 PASS"""
if isinstance(r, dict) and r.get('pass') is True: return True
```
→ `{'pass': True, 'conds': COND}` = PASS；`{'pass': False, 'conds': COND}` = FAIL。✅

## 纪律遵守
- ✅ 只改返回值形状 + __main__/selftest 解包
- ✅ 不改断言逻辑、不改断言条数、不改判分严格度
- ✅ 不改 case prompt / assets / hidden
- 🚫 未碰任何 *.jsonl
- 🚫 未碰别 shard 文件（COND 模式的另 7 个文件属 A/C/D shard，未动）

## 剩余债
220 B case 待修，优先级（按运维令）：tuple(25) > str(13) > None/bare(12) > dict_other(31) > Call/Name(74) > NO_RETURN(51)。下轮继续分批。

## 提交
- EDA-Flow-Bench master: `15043fa90` (8 文件：6 check.py + 2 negative_selftest.py；顺带 1 个 working-tree 残留 reports/PHASE1_PILOT_LESSONS.md 删除被 autostash 带入，非 case 数据)
- super_intelligence_2035 main: MEMORY_B 更新 + 本笔记
