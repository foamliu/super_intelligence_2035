# r1156 — 判分契约 dict_other 收口轮（30 case）

**日期**：2026-11-24
**shard**：B
**触发**：2026-11-24 运维令（判分契约修复，commit 6c1a50ee9）；续 r1155 NO_RETURN 收口后的下一优先类别 dict_other。

## 背景
judge 通路统一为严格契约：`r.get('pass') is True` 才算 PASS（`eval/run_one.sh:464`）。dict_other 类 = check() 末尾 `return {...}` dict 缺 `pass`/`ok` 键（用了 `passed`/`PASS`/`status`/`verdict`/`all_pass`/`conditions_passed` 等非契约键），新契约下即使交付件正确也判 FAIL。

## 做了什么
**30 case**（dict_all_B.txt，audit `return dict keys=` 命中）test 字段补 `pass` 键：

### 修法（AST 定位 + 文本插入，纯加键不改逻辑/断言/条数）
- **28 单 dict 成功路径**（失败经 `_fail`/`assert`/`raise`，dict 仅在全过时到达）：dict 首键前插 `"pass": True`
  - 涵盖 `status:"PASS"` / `verdict:"PASS"` / `PASS:True` / `passed:len(CONDITIONS)` / `all_pass:all(...)` / `conditions_passed:N` 各种非契约键
- **2 多 dict 路径镜像 `passed` 键**：
  - `BatchBsubHspice`（4 dict）：L249 `pass: passed`（runtime bool 镜像）；L111/123/131 `pass: False`（早退 FAIL 路径）
  - `ZqPatternTimingAnalyze`（2 dict）：L165 `pass: True`；L167 `pass: False`（except 路径）

### 关键发现：test-vs-ref desync 债
30 case 的 `reference/<id>/check.py` 在前几轮（r1149–r1155）已修好（HEAD 即含 `pass` 键），但 `cases/B/*.json` 的 test 字段未同步。本轮纯做 test 字段 sync：30 个 cases/B JSON 改，0 个 ref check.py 改（已合规）。这与 r1154 的 test-field sync 债治理同源。

## 验证
- `audit_check_returns.py --shard B`：VIOLATION 114→**84**（−30，精确匹配）；OK 477→**507**；NO_RETURN 仍 0；PARSE_ERROR 仍 1（Tr0TrTfMeas，pre-existing，非本类）
- 30/30 test 字段 + 30/30 ref check.py 现在 AST 均含 `pass`/`ok` 键（compliant）
- 30/30 `ast.parse` 通过（无语法破坏）
- §4.9 三假完整性：
  - `AetherHierNavAnalyze` neg_selftest：ref PASS + 4 neg（always_empty/print_only/naive_hardcode_a/stub_partial）全 FAIL ✓
  - `BatchBsubHspice` neg_selftest：5 neg（empty/print_expected/hardcode_a/no_hspice_seg/wrong_defaults）全 FAIL（k_pass=1~9/11）✓
- RonDvqSlopeExtract：test-vs-ref 内容 pre-existing 分歧（ref 含 A's 注释，test 无），**非本轮引入**（HEAD 即不同 hash），仅 return 形状 sync，内容分歧超出契约修复范围未动

## 并发安全
共享工作树有 194 个 modified 文件（shard A/C/D 并发 worker WIP）。本轮用显式路径列表 `xargs git add` 仅 stage 30 个 cases/B JSON，staged-set 与他 shard 文件零交叉。ref check.py 0 改故未 add。

## 产出
- EDA-Flow-Bench master `a0a857c34`（30 files changed, 52 ins/52 del）
- 台账 B 不动（case 597/parked 1172，本轮无新 case）
- covered=597/4529=13.2%（不变）
- 🎯 最近20条 20/20=100%（观察值，未 pi 实跑）

## 剩余违规（下轮）
VIOL 84，按 MEMORY 优先级：var39 > helper36 > none_bare12 > list6 > ternary2 > compare1（dict_other 已清零）。下一轮收口 var（变量返回型）或 helper（辅助函数透传）。
