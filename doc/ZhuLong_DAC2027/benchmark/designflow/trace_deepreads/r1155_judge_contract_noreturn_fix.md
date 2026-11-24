# r1155 — 判分契约 NO_RETURN 收口轮（2026-11-24）

> 运维令：2026-11-24 判分契约修复（commit 6c1a50ee9）· 按需执行
> 契约：`reports/JUDGE_CONTRACT.md` — 仅 `return True` / `return {'pass':True}` / `return {'ok':True}` 算 PASS，其余一律 FAIL。

## 背景

fresh B-spice 池仍耗尽（r1143/r1125 stop-loss 确认），续判分契约治理。
本轮目标：**收口 NO_RETURN 类别**（check() 零 return 语句 ⇒ 新契约下返回 None ⇒ 始终 FAIL，即使交付件正确）。

## audit 起点（shard B）

| verdict | 数 |
|:--|--:|
| OK | 430 |
| VIOLATION | 114 |
| NO_RETURN | 47 |
| NO_CHECK_FN | 6 |
| PARSE_ERROR | 1 |

NO_RETURN 是"check() 有 0 个 return 语句"的类别（audit_check_returns.py 在 check() own body 内 prune 嵌套函数后无 Return 节点）。这些 case 失败路径全是 `raise AssertionError`，成功路径落到函数末尾返回 None → 新契约 FAIL。

## 修法（两类）

### A. 42 纯 NO_RETURN（check() 有真实 body，零 return）

机械修（JUDGE_CONTRACT §3.3）：AST 定位 check() FunctionDef，在 body 末尾（最后一个直接子语句 end_lineno 之后、函数体缩进层）插入 `return True`。

- 失败路径仍为 `raise`（不变）→ FAIL
- 成功路径 None → True → PASS
- 断言逻辑/条数/严格度**零改动**

脚本：`fix_noreturn.py`（AST 校验：插入后 check() own body 含 `return True`；跳过有 return 的 case；idempotent）。
4 case 命中 SYNTAX_AFTER_INSERT（McVariation/NetlistSim/SpiceNetlistFault/TimingTrace）——这 4 个 test 字段是单行 stub `def check(...): ...`，转入 B 类处理。

### B. 4 stub-test-field（test 字段 = stub，真实 check.py 在 reference/）

| case | reference/check.py 形状 | 修法 |
|:--|:--|:--|
| McVariationBlockGenProduce | 已 `return True`（合规） | sync test=ref |
| NetlistSimFlowGenProduce | NO_RETURN（零 return） | ref +return True，sync |
| SpiceNetlistFaultAnalyzer | `return "PASS:..." % args`（str→FAIL） | `print(...); return True`，sync |
| TimingTraceDatasetBuild | `return _finalize(conds)`×6（helper 透传，audit "call" flag） | `_finalize` 本返回 `{'pass':bool,...}`（runtime 合规但 audit 看不穿）；包成 `_r=_finalize(conds); return {"pass":_r["pass"],...}` dict 字面量（audit dict-pass-ok + __main__ 的 `r.get("pass")`/`json.dumps(r)` 仍工作） |

脚本：`fix_4stubs.py`（每步 AST 校验：return 形状合规 + __main__ 不破坏）。

## 验证

### audit（shard B，修后）

| verdict | 数 | Δ |
|:--|--:|:--|
| OK | 477 | +47 |
| VIOLATION | 114 | 0（他类不动） |
| NO_RETURN | 0 | -47 ✅ |
| NO_CHECK_FN | 6 | 0 |
| PARSE_ERROR | 1 | 0 |

### 47 case 全量校验
- parse 错误：0
- test==ref desync：0
- 无 success-capable return：0

### 功能自验（抽样）
- **AgingDirSeparateTransform-001**（42 纯 NO_RETURN 代表）：`python3 check.py` → `SELFTEST PASS: all 20 conditions satisfied`（exit 0）；`negative_selftest.py` → 4 neg（empty/print_only/hardcode_a/deleted_core）全 FAIL（§4.9 trio intact）。
- **TimingTraceDatasetBuild-001**（最复杂，6 站点 wrap）：`negative_selftest.py` → 3 neg（empty_stub/print_only/core_removed）全 FAIL。

## 提交

- EDA-Flow-Bench master `4f1bd70c5`（93 files：47 cases/B JSON + 46 reference/check.py；McVariation ref 无 diff 故 93 非 94）。
- 仅改返回值形状，未碰 prompt/assets/hidden/metadata/断言逻辑（契约 §7）。

## 共享工作树风险处置

本工作树被 shard B/C/D 多 worker 共享：
- 14 cases/B WIP（并发 B worker 的 tuple/str 半提交）+ 大量 cases/C WIP（并发 C worker）+ eval/run_one.sh mod —— **全部未碰**。
- 提交用**显式路径** `git add`（add_list.txt 94 路径），staged-set 三方校验：staged∩WIP=∅、staged∩cases/C=∅。
- `git reset` 清掉了被并发 worker 污染进 index 的 cases/A 文件（working tree 不动，无数据丢失）。
- `git index.lock` 竞争：retry 循环解决。
- 本地遗留的 shard D 旧 commit（ad5da92fb SineScanStdout-001）与 origin 同内容，rebase 时自动并入，无冲突。

## 剩余违规（下轮）

dict_other30 > var39 > helper36 > none_bare12 > list6 > ternary2 > compare1（NO_RETURN 已清零）。
dict_other（dict 用 passed/status/verdict 等键无 pass/ok）与 var（return 变量，类型不定）是下一优先级。
